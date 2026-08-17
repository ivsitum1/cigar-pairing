#!/usr/bin/env python3
"""Ujednacavanje podloga na fotografijama proizvoda (cigare i boce).

PROBLEM. Slike dolaze iz cetiri duckana i svaki snima na svojoj podlozi:
Humidor i CigarWorld na bijeloj, Neptune cesto na crnoj, Allez na smedjem
drvu. Poredane u istoj kartici izgledaju kao da su iz tri razlicite aplikacije
— bijeli pravokutnik svijetli na tamnoj kartici, crni se s njom stopi u mrlju,
smedji nosi svoju teksturu.

RJESENJE. Podloga se ne prebojava u jednu boju, nego se MICE: sto je bilo
pozadina postaje prozirno, pa svaka slika sjedne na pozadinu koju crta sama
aplikacija. Time je ujednacenost posljedica, a ne pogadjanje nijanse — kad se
tema kartice promijeni, slike idu za njom bez ponovne obrade.

KAKO SE PREPOZNAJE PODLOGA. Rub slike, ne sredina: proizvod je uvijek u
sredini, pa vijenac piksela uz rub govori na cemu je snimljen. Ako je taj
vijenac ujednacen (mala rasprsenost), boja mu je podloga. Ako nije — ruka, stol
s teksturom, ambijentalna fotografija — slika se NE rezuckava, nego dobiva
oznaku "framed" i aplikacija ju prikaze u okviru. Bolje postena fotografija u
okviru nego proizvod izgrizen po rubovima.

ZASTO SAMO BOJA NIJE DOVOLJNA. Bijela etiketa na cigari jednako je bijela kao
bijela podloga iza nje. Kad bi se micalo "sve sto je boje podloge", etiketa bi
nestala i ostala bi rupa. Zato se micu samo pikseli koji su boje podloge I
povezani s rubom slike — do etikete zatvorene tamnim obodom cigare popuna s
ruba ne dolazi, pa ona ostaje.

Povezanost se racuna na umanjenoj kopiji (do POVEZANOST_STRANICA px). Popuna
je jedina operacija koja ide piksel po piksel; na punoj velicini trajala bi
sekundama po slici, na umanjenoj traje milisekunde, a granica podloge je
gruba struktura koju umanjivanje ne gubi. Rezultat se vraca na punu velicinu i
presijece s maskom pune rezolucije, pa je rub proizvoda ostar koliko i original.

Ovisnosti: Pillow. Nista drugo.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable

from PIL import Image, ImageChops, ImageFilter, ImageStat

# Vijenac uz rub iz kojeg se cita podloga — 3% kratke stranice, najmanje 2px.
VIJENAC_UDIO = 0.03
VIJENAC_MIN = 2

# Koliko rubnih piksela mora biti uz medijalnu boju da bi se podloga zvala
# jednolicnom. Mjeri se UDIO, ne rasprsenost: proizvod cesto dodiruje rub
# kadra, i tada rasprsenost vijenca skoci iako je podloga besprijekorno
# bijela. Udio to razdvaja — cigara koja ulazi u vijenac pokvari petinu
# piksela, drvena ploca pokvari vecinu.
JEDNOLICNA_MIN_UDIO = 0.72

# Do koje udaljenosti od medijalne boje se rubni piksel jos broji "uz podlogu".
VIJENAC_BLIZINA = 24

# Koliko piksel smije odstupati od boje podloge a da se jos broji kao podloga.
# Prag prati rasprsenost vijenca: cistija podloga, stroza granica.
TOLERANCIJA_MIN = 16
TOLERANCIJA_MAX = 48

# Velicina kopije na kojoj se racuna povezanost s rubom.
POVEZANOST_STRANICA = 256

# Meksanje ruba — bez njega izrez ima stepenice piksela.
RUB_MEKOCA_PX = 0.8

# Uvlacenje ruba za jedan piksel PRIJE meksanja. Piksel na samoj granici je
# mjesavina proizvoda i podloge (JPEG to jos i razmaze), pa bez uvlacenja oko
# izreza s bijele podloge ostane svijetli obrub, a s crne tamni — tocno ono
# sto se htjelo maknuti, samo tanje.
RUB_UVLAKA = True

# Najveca stranica izlazne slike. Kartica ju prikazuje na ~320px sirine, pa je
# 800 dovoljno i za retinu, a datoteka ostaje mala.
IZLAZ_STRANICA = 800

# Prazan prostor oko proizvoda nakon rezanja, u udjelu duze stranice.
OBRUB_UDIO = 0.04

# Ciljna medijana svjetline proizvoda. Podsvijetlo snimljena cigara i
# presvijetlo snimljena boca inace i dalje izgledaju razlicito iako im je
# podloga ista. Ispravak je namjerno blag i ogranicen — slika se poravnava,
# ne prebojava.
CILJNA_SVJETLINA = 118.0
SVJETLINA_MIN_FAKTOR = 0.85
SVJETLINA_MAX_FAKTOR = 1.30


@dataclass(frozen=True)
class Podloga:
    """Sto je procitano s ruba slike."""

    boja: tuple[int, int, int]
    #: rasprsenost SAMO medju pikselima koji su uz medijalnu boju — sum
    #: podloge, bez proizvoda koji je usao u vijenac
    sd: float
    #: koliki dio vijenca lezi uz medijalnu boju
    udio: float
    jednolicna: bool

    @property
    def vrsta(self) -> str:
        """Ime podloge za izvjestaj — bijela, crna, smedja ili mijesana."""
        if not self.jednolicna:
            return "mijesana"
        r, g, b = self.boja
        if min(r, g, b) >= 210:
            return "bijela"
        if max(r, g, b) <= 60:
            return "crna"
        # Smedje/drvo: crvena vodi, plava zaostaje.
        if r >= b + 18 and r >= g:
            return "smedja"
        return "siva"


@dataclass(frozen=True)
class Obrada:
    """Izvjestaj o jednoj obradjenoj slici."""

    postupak: str  # "cutout" (podloga maknuta) ili "framed" (ostavljena)
    podloga: str
    sd: float
    udio_ruba: float  # koliki dio vijenca je bio uz boju podloge
    tolerancija: int
    udio_proizvoda: float  # koliki dio slike je ostao neproziran
    svjetlina_faktor: float
    sirina: int
    visina: int


def _vijenac_piksela(img: Image.Image) -> list[tuple[int, int, int]]:
    """Pikseli uz sam rub slike, u jednom popisu."""
    w, h = img.size
    d = max(VIJENAC_MIN, int(round(min(w, h) * VIJENAC_UDIO)))
    px = img.load()
    uzorci: list[tuple[int, int, int]] = []
    for y in range(min(d, h)):
        for x in range(w):
            uzorci.append(px[x, y])
            uzorci.append(px[x, h - 1 - y])
    for x in range(min(d, w)):
        for y in range(d, max(d, h - d)):
            uzorci.append(px[x, y])
            uzorci.append(px[w - 1 - x, y])
    return uzorci


def _medijan(vrijednosti: list[int]) -> int:
    s = sorted(vrijednosti)
    return s[len(s) // 2]


def detektiraj_podlogu(img: Image.Image) -> Podloga:
    """Procitaj boju podloge s ruba i reci je li jednolicna.

    Medijan, ne prosjek: ako proizvod dodiruje rub slike, prosjek bi povukao
    boju prema proizvodu, a medijan ostaje na podlozi dok ona drzi vecinu ruba.

    Jednolicnost se mjeri udjelom vijenca uz tu boju, a rasprsenost se racuna
    samo na tom dijelu. Inace bi cigara koja izlazi iz kadra podigla
    rasprsenost i studijska bijela bi prosla kao "ambijentalna".
    """
    rgb = img.convert("RGB")
    uzorci = _vijenac_piksela(rgb)
    kanali = ([p[0] for p in uzorci], [p[1] for p in uzorci], [p[2] for p in uzorci])
    boja = tuple(_medijan(k) for k in kanali)

    udaljenosti = [max(abs(p[i] - boja[i]) for i in range(3)) for p in uzorci]
    uz_podlogu = [d for d in udaljenosti if d <= VIJENAC_BLIZINA]
    udio = len(uz_podlogu) / len(udaljenosti)

    if uz_podlogu:
        sredina = sum(uz_podlogu) / len(uz_podlogu)
        sd = (sum((d - sredina) ** 2 for d in uz_podlogu) / len(uz_podlogu)) ** 0.5
    else:
        sd = float(VIJENAC_BLIZINA)

    return Podloga(
        boja=boja,  # type: ignore[arg-type]
        sd=sd,
        udio=udio,
        jednolicna=udio >= JEDNOLICNA_MIN_UDIO,
    )


def tolerancija_za(podloga: Podloga) -> int:
    """Koliko piksel smije odstupati od podloge a da se jos broji kao podloga."""
    prag = int(round(TOLERANCIJA_MIN + podloga.sd * 2.0))
    return max(TOLERANCIJA_MIN, min(TOLERANCIJA_MAX, prag))


def maska_odstupanja(img: Image.Image, boja: tuple[int, int, int], tolerancija: int) -> Image.Image:
    """Bijelo = piksel se dovoljno razlikuje od podloge (kandidat za proizvod).

    Udaljenost je najveci odmak po kanalu, ne prosjek: crvena vrpca na bijelom
    odstupa jako u dva kanala i nimalo u trecem, pa bi ju prosjek stanjio.
    """
    rgb = img.convert("RGB")
    plocica = Image.new("RGB", rgb.size, boja)
    razlika = ImageChops.difference(rgb, plocica)
    r, g, b = razlika.split()
    najveci = ImageChops.lighter(ImageChops.lighter(r, g), b)
    return najveci.point(lambda v: 255 if v > tolerancija else 0, mode="L")


def _povezano_s_rubom(maska_podloge: Image.Image) -> Image.Image:
    """Od piksela podloge zadrzi samo one do kojih se dodje s ruba slike.

    Ulaz: bijelo = piksel je boje podloge. Izlaz: bijelo = piksel je podloga
    KOJA DODIRUJE rub. Zatvorena bijela polja unutar proizvoda (etiketa, odsjaj
    na staklu boce) ostaju crna i time dio proizvoda.
    """
    w, h = maska_podloge.size
    px = maska_podloge.load()
    dosegnuto = bytearray(w * h)
    red: deque[tuple[int, int]] = deque()

    def zasij(x: int, y: int) -> None:
        if px[x, y] and not dosegnuto[y * w + x]:
            dosegnuto[y * w + x] = 1
            red.append((x, y))

    for x in range(w):
        zasij(x, 0)
        zasij(x, h - 1)
    for y in range(h):
        zasij(0, y)
        zasij(w - 1, y)

    while red:
        x, y = red.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and px[nx, ny] and not dosegnuto[ny * w + nx]:
                dosegnuto[ny * w + nx] = 1
                red.append((nx, ny))

    izlaz = Image.new("L", (w, h))
    izlaz.putdata([255 if bit else 0 for bit in dosegnuto])
    return izlaz


def alfa_maska(img: Image.Image, podloga: Podloga, tolerancija: int) -> Image.Image:
    """Alfa kanal: 255 proizvod, 0 podloga.

    Povezanost se racuna na umanjenoj kopiji (brzo), a rez se izvodi na punoj
    rezoluciji (ostro): puna maska boje presijeca se s uvecanom maskom "ovo je
    podloga s ruba".
    """
    puna_proizvod = maska_odstupanja(img, podloga.boja, tolerancija)
    puna_podloga = ImageChops.invert(puna_proizvod)

    mala = puna_podloga.copy()
    mala.thumbnail((POVEZANOST_STRANICA, POVEZANOST_STRANICA), Image.Resampling.NEAREST)
    rubna = _povezano_s_rubom(mala)
    # Bilinearno natrag: granica podloge dobiva prijelaz umjesto stepenica.
    rubna_puna = rubna.resize(img.size, Image.Resampling.BILINEAR)

    # Podloga je ono sto je i boje podloge i doseznuto s ruba.
    podloga_puna = ImageChops.multiply(puna_podloga, rubna_puna)
    alfa = ImageChops.invert(podloga_puna)
    if RUB_UVLAKA:
        alfa = alfa.filter(ImageFilter.MinFilter(3))
    return alfa.filter(ImageFilter.GaussianBlur(RUB_MEKOCA_PX))


def udio_neprozirnog(alfa: Image.Image) -> float:
    """Koliki dio slike je proizvod. Sluzi kao provjera razumnosti izreza."""
    stat = ImageStat.Stat(alfa)
    return stat.mean[0] / 255.0


def izrezi_na_proizvod(img: Image.Image) -> Image.Image:
    """Odrezi prozirni rub i vrati blagi jednolicni obrub.

    Bez ovoga proizvod u kartici "pluta" razlicito od slike do slike — jedan
    duckan snima izbliza, drugi ostavlja pola kadra prazno.
    """
    bbox = img.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if not bbox:
        return img
    izrezano = img.crop(bbox)
    w, h = izrezano.size
    obrub = max(1, int(round(max(w, h) * OBRUB_UDIO)))
    platno = Image.new("RGBA", (w + 2 * obrub, h + 2 * obrub), (0, 0, 0, 0))
    platno.paste(izrezano, (obrub, obrub))
    return platno


def poravnaj_svjetlinu(img: Image.Image) -> tuple[Image.Image, float]:
    """Priblizi svjetlinu proizvoda zajednickoj razini; vrati (slika, faktor).

    Mjeri se SAMO proizvod (kroz alfa masku) — da prozirni dio ne povuce
    medijanu i ne pretvori korekciju u pojacavanje praznine.
    """
    alfa = img.getchannel("A")
    binarna = alfa.point(lambda v: 255 if v > 128 else 0, mode="L")
    if not binarna.getbbox():
        return img, 1.0
    siva = img.convert("RGB").convert("L")
    sredina = ImageStat.Stat(siva, mask=binarna).mean[0]
    if sredina <= 1.0:
        return img, 1.0
    faktor = CILJNA_SVJETLINA / sredina
    faktor = max(SVJETLINA_MIN_FAKTOR, min(SVJETLINA_MAX_FAKTOR, faktor))
    if abs(faktor - 1.0) < 0.02:
        return img, 1.0
    r, g, b, a = img.split()
    skala = [min(255, int(round(v * faktor))) for v in range(256)]
    return Image.merge("RGBA", (r.point(skala), g.point(skala), b.point(skala), a)), faktor


def smanji(img: Image.Image, stranica: int = IZLAZ_STRANICA) -> Image.Image:
    if max(img.size) <= stranica:
        return img
    kopija = img.copy()
    kopija.thumbnail((stranica, stranica), Image.Resampling.LANCZOS)
    return kopija


def obradi(img: Image.Image, stranica: int = IZLAZ_STRANICA) -> tuple[Image.Image, Obrada]:
    """Jedna slika -> (RGBA slika, izvjestaj).

    Dva ishoda:
      * "cutout" — podloga je bila jednolicna i maknuta je u prozirno.
      * "framed" — podloga nije jednolicna ILI bi izrez pojeo (gotovo) cijelu
        sliku; original ostaje citav, aplikacija ga stavlja u okvir.

    Drugi uvjet je zastita od tihe stete: kad kadar ispuni proizvod do ruba,
    popuna s ruba prodire u njega i vrati se maska koja je "sve podloga".
    Takav izrez radije se odbaci nego isporuci praznu sliku.
    """
    izvor = smanji(img.convert("RGBA"), stranica)
    podloga = detektiraj_podlogu(izvor)
    tolerancija = tolerancija_za(podloga)

    if not podloga.jednolicna:
        return izvor, Obrada(
            postupak="framed",
            podloga=podloga.vrsta,
            sd=round(podloga.sd, 2),
            udio_ruba=round(podloga.udio, 3),
            tolerancija=tolerancija,
            udio_proizvoda=1.0,
            svjetlina_faktor=1.0,
            sirina=izvor.size[0],
            visina=izvor.size[1],
        )

    alfa = alfa_maska(izvor, podloga, tolerancija)
    udio = udio_neprozirnog(alfa)
    if udio < 0.02 or udio > 0.985:
        return izvor, Obrada(
            postupak="framed",
            podloga=podloga.vrsta,
            sd=round(podloga.sd, 2),
            udio_ruba=round(podloga.udio, 3),
            tolerancija=tolerancija,
            udio_proizvoda=round(udio, 4),
            svjetlina_faktor=1.0,
            sirina=izvor.size[0],
            visina=izvor.size[1],
        )

    izrez = izvor.copy()
    izrez.putalpha(alfa)
    izrez = izrezi_na_proizvod(izrez)
    izrez, faktor = poravnaj_svjetlinu(izrez)
    return izrez, Obrada(
        postupak="cutout",
        podloga=podloga.vrsta,
        sd=round(podloga.sd, 2),
        udio_ruba=round(podloga.udio, 3),
        tolerancija=tolerancija,
        udio_proizvoda=round(udio, 4),
        svjetlina_faktor=round(faktor, 3),
        sirina=izrez.size[0],
        visina=izrez.size[1],
    )


def spremi_webp(img: Image.Image, put, kvaliteta: int = 82) -> int:
    """Spremi RGBA u WebP s alfom; vrati velicinu datoteke u bajtovima."""
    put.parent.mkdir(parents=True, exist_ok=True)
    img.save(put, "WEBP", quality=kvaliteta, method=6)
    return put.stat().st_size


def prvi_postojeci(putovi: Iterable) -> object | None:
    for p in putovi:
        if p and p.exists():
            return p
    return None
