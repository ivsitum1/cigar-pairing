#!/usr/bin/env python3
"""Testovi za ujednacavanje podloga (product_image_lib).

Slike se ne preuzimaju — svaka se crta u testu, pa test radi bez mreze i bez
ijedne binarne datoteke u repou. Crtaju se tri varijante istog proizvoda na tri
podloge koje stvarno stizu iz duckana (bijela, crna, smedje drvo) i provjerava
se ono zbog cega je biblioteka i napisana: da nakon obrade izgledaju jednako.

Pokreni iz app/:  python3 scripts/test_product_image_lib.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from PIL import Image, ImageDraw  # noqa: E402

    IMA_PILLOW = True
except ImportError:  # pragma: no cover - CI bez Pillowa preskace
    IMA_PILLOW = False

if IMA_PILLOW:
    import product_image_lib as lib  # noqa: E402

BIJELA = (245, 245, 245)
CRNA = (18, 18, 18)
SMEDJA = (109, 74, 46)

CIGARA = (92, 62, 38)  # tijelo cigare — tamno smedje
PRSTEN = (198, 160, 74)  # zlatni prsten
ETIKETA = (248, 248, 248)  # bijeli natpis na prstenu


def slika_cigare(
    podloga: tuple[int, int, int],
    velicina: tuple[int, int] = (400, 300),
    pomak: tuple[int, int] = (0, 0),
    sum: int = 0,
) -> "Image.Image":
    """Nacrtaj cigaru na zadanoj podlozi.

    `pomak` mice proizvod iz sredista (razliciti duckani razlicito kadriraju),
    `sum` razbija podlogu u teksturu (ambijentalna fotografija).
    """
    img = Image.new("RGB", velicina, podloga)
    if sum:
        px = img.load()
        for y in range(velicina[1]):
            for x in range(velicina[0]):
                r, g, b = px[x, y]
                d = ((x * 7 + y * 13) % (2 * sum)) - sum
                px[x, y] = (
                    max(0, min(255, r + d)),
                    max(0, min(255, g + d)),
                    max(0, min(255, b + d)),
                )
    crtac = ImageDraw.Draw(img)
    dx, dy = pomak
    x0, y0, x1, y1 = 60 + dx, 130 + dy, 340 + dx, 170 + dy
    crtac.rectangle([x0, y0, x1, y1], fill=CIGARA)
    # prsten sa svijetlim natpisom — natpis je bijel kao bijela podloga, i
    # upravo on pokazuje mice li se boja ili se mice pozadina
    crtac.rectangle([x0 + 30, y0, x0 + 80, y1], fill=PRSTEN)
    crtac.rectangle([x0 + 45, y0 + 14, x0 + 65, y1 - 14], fill=ETIKETA)
    return img


class TestPrepoznavanjePodloge(unittest.TestCase):
    def test_imenuje_tri_podloge_iz_duckana(self):
        for boja, ime in ((BIJELA, "bijela"), (CRNA, "crna"), (SMEDJA, "smedja")):
            podloga = lib.detektiraj_podlogu(slika_cigare(boja))
            self.assertTrue(podloga.jednolicna, ime)
            self.assertEqual(podloga.vrsta, ime)

    def test_teksturirana_podloga_nije_jednolicna(self):
        podloga = lib.detektiraj_podlogu(slika_cigare(SMEDJA, sum=40))
        self.assertFalse(podloga.jednolicna)
        self.assertEqual(podloga.vrsta, "mijesana")

    def test_boja_se_cita_i_kad_proizvod_dodiruje_rub(self):
        # medijan drzi podlogu dok ona ima vecinu ruba; prosjek bi odlutao
        img = slika_cigare(BIJELA, pomak=(0, -130))
        self.assertEqual(lib.detektiraj_podlogu(img).vrsta, "bijela")


class TestIzrez(unittest.TestCase):
    def test_podloga_postaje_prozirna_a_proizvod_ostaje(self):
        for boja in (BIJELA, CRNA, SMEDJA):
            izlaz, izvjestaj = lib.obradi(slika_cigare(boja))
            self.assertEqual(izvjestaj.postupak, "cutout", izvjestaj.podloga)
            alfa = izlaz.getchannel("A")
            w, h = izlaz.size
            self.assertLess(alfa.getpixel((1, 1)), 20, f"kut mora biti prozirovan ({boja})")
            self.assertGreater(
                alfa.getpixel((w // 2, h // 2)), 200, f"sredina mora ostati ({boja})"
            )

    def test_bijeli_natpis_na_cigari_prezivi_bijelu_podlogu(self):
        # Natpis je iste boje kao podloga. Ostaje jer do njega nema puta s ruba
        # — da se micalo po boji, na njegovom bi mjestu ostala rupa.
        izlaz, _ = lib.obradi(slika_cigare(BIJELA))
        alfa = izlaz.getchannel("A")
        rgb = izlaz.convert("RGB")
        w, h = izlaz.size
        svijetli = [
            (x, y)
            for y in range(h)
            for x in range(w)
            if alfa.getpixel((x, y)) > 200 and min(rgb.getpixel((x, y))) > 230
        ]
        self.assertGreater(len(svijetli), 50, "bijeli natpis je pojeden zajedno s podlogom")

    def test_izrez_ne_ostavlja_obrub_stare_podloge(self):
        # Piksel na granici je mjesavina cigare i podloge. Bez uvlacenja ruba
        # oko tamne cigare izrezane s bijelog ostane svijetli vijenac i on se
        # na tamnoj kartici vidi kao bijeli obris.
        img = Image.new("RGB", (400, 300), BIJELA)
        ImageDraw.Draw(img).rectangle([60, 130, 340, 170], fill=(60, 40, 26))
        izlaz, izvjestaj = lib.obradi(img)
        self.assertEqual(izvjestaj.postupak, "cutout")

        alfa = izlaz.getchannel("A")
        rgb = izlaz.convert("RGB")
        w, h = izlaz.size
        svijetli_na_rubu = [
            (x, y)
            for y in range(h)
            for x in range(w)
            if alfa.getpixel((x, y)) > 60 and min(rgb.getpixel((x, y))) > 200
        ]
        self.assertEqual(svijetli_na_rubu, [], "ostao je svijetli obrub stare podloge")

    def test_ambijentalna_fotografija_se_ne_rezucka(self):
        izlaz, izvjestaj = lib.obradi(slika_cigare(SMEDJA, sum=40))
        self.assertEqual(izvjestaj.postupak, "framed")
        # framed znaci: slika je ostala citava, bez prozirnih rupa
        self.assertEqual(izlaz.getchannel("A").getextrema(), (255, 255))

    def test_kadar_ispunjen_proizvodom_ne_daje_praznu_sliku(self):
        # Nema podloge za citanje — rub je sam proizvod. Radije framed nego
        # slika u kojoj je sve prozirno.
        puna = Image.new("RGB", (200, 200), CIGARA)
        izlaz, izvjestaj = lib.obradi(puna)
        self.assertEqual(izvjestaj.postupak, "framed")
        self.assertEqual(izlaz.getchannel("A").getextrema(), (255, 255))


class TestUjednacenost(unittest.TestCase):
    """Ono zbog cega sve ovo postoji: tri duckana, jedan izgled."""

    def test_tri_podloge_daju_jednake_izreze(self):
        izlazi = [lib.obradi(slika_cigare(boja))[0] for boja in (BIJELA, CRNA, SMEDJA)]
        sirine = {i.size[0] for i in izlazi}
        visine = {i.size[1] for i in izlazi}
        self.assertLessEqual(max(sirine) - min(sirine), 4, f"razlicite sirine: {sirine}")
        self.assertLessEqual(max(visine) - min(visine), 4, f"razlicite visine: {visine}")

    def test_razlicito_kadriranje_zavrsi_na_istoj_velicini(self):
        # isti proizvod, jedan duckan snima izbliza, drugi ostavlja zraka
        blizu, daleko = lib.obradi(slika_cigare(BIJELA))[0], lib.obradi(
            slika_cigare(BIJELA, velicina=(600, 500), pomak=(120, 90))
        )[0]
        omjer_a = blizu.size[0] / blizu.size[1]
        omjer_b = daleko.size[0] / daleko.size[1]
        self.assertAlmostEqual(omjer_a, omjer_b, delta=0.25)

    def test_tamno_i_svijetlo_snimljena_slika_se_priblizavaju(self):
        def prosjek(img):
            from PIL import ImageStat

            binarna = img.getchannel("A").point(lambda v: 255 if v > 128 else 0, mode="L")
            return ImageStat.Stat(img.convert("RGB").convert("L"), mask=binarna).mean[0]

        tamna = Image.new("RGB", (400, 300), BIJELA)
        svijetla = Image.new("RGB", (400, 300), BIJELA)
        from PIL import ImageDraw as D

        D.Draw(tamna).rectangle([60, 130, 340, 170], fill=(40, 28, 18))
        D.Draw(svijetla).rectangle([60, 130, 340, 170], fill=(190, 150, 110))

        prije = abs(40 - 190)
        a, b = lib.obradi(tamna)[0], lib.obradi(svijetla)[0]
        poslije = abs(prosjek(a) - prosjek(b))
        self.assertLess(poslije, prije, "poravnanje svjetline nije nista promijenilo")


class TestTolerancija(unittest.TestCase):
    def test_cistija_podloga_dobiva_strozi_prag(self):
        cista = lib.detektiraj_podlogu(slika_cigare(BIJELA))
        mrljava = lib.detektiraj_podlogu(slika_cigare(BIJELA, sum=8))
        self.assertLessEqual(lib.tolerancija_za(cista), lib.tolerancija_za(mrljava))

    def test_prag_ostaje_u_granicama(self):
        for s in (0.0, 5.0, 50.0, 500.0):
            prag = lib.tolerancija_za(lib.Podloga(boja=(1, 1, 1), sd=s, udio=1.0, jednolicna=True))
            self.assertGreaterEqual(prag, lib.TOLERANCIJA_MIN)
            self.assertLessEqual(prag, lib.TOLERANCIJA_MAX)


def _scraper():
    """scrape-product-images.py ima crticu u imenu, pa ide preko importliba."""
    import importlib.util

    put = Path(__file__).resolve().parent / "scrape-product-images.py"
    spec = importlib.util.spec_from_file_location("scrape_product_images", put)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


class TestIzborSlikeSaStranice(unittest.TestCase):
    """Koju sliku uzeti sa stranice proizvoda — bez mreze, na uzorku HTML-a."""

    def setUp(self):
        self.s = _scraper()

    def test_uzima_og_image(self):
        page = '<html><head><meta property="og:image" content="/media/cigara.jpg"></head></html>'
        self.assertEqual(
            self.s.slika_sa_stranice(page, "https://humidor.hr/hr/proizvod/x/"),
            "https://humidor.hr/media/cigara.jpg",
        )

    def test_podnosi_obrnut_redoslijed_atributa(self):
        page = '<meta content="https://cdn.shop/a.png" property="og:image">'
        self.assertEqual(self.s.slika_sa_stranice(page, "https://shop.de/p"), "https://cdn.shop/a.png")

    def test_pada_na_json_ld_kad_nema_og(self):
        page = """<script type="application/ld+json">
        {"@type":"Product","name":"X","image":["https://cdn.shop/1.jpg","https://cdn.shop/2.jpg"]}
        </script>"""
        self.assertEqual(self.s.slika_sa_stranice(page, "https://shop.de/p"), "https://cdn.shop/1.jpg")

    def test_ne_uzima_prvi_img_sa_stranice(self):
        # logo duckana nije fotografija proizvoda
        page = '<html><body><img src="/static/logo.svg"><img src="/media/cigara.jpg"></body></html>'
        self.assertIsNone(self.s.slika_sa_stranice(page, "https://humidor.hr/p"))

    def test_preskace_ugradjenu_data_sliku(self):
        page = '<meta property="og:image" content="data:image/png;base64,iVBOR">'
        self.assertIsNone(self.s.slika_sa_stranice(page, "https://shop.de/p"))


class TestRedoslijedDuckana(unittest.TestCase):
    def test_hrvatski_duckan_ide_prvi(self):
        s = _scraper()
        cigara = {
            "id": "cig-x",
            "vitolas": [
                {
                    "name": "Toro",
                    "url": "https://humidor.hr/hr/proizvod/x/",
                    "regionLinks": {
                        "EU": {"url": "https://cigarworld.de/x"},
                        "USA": {"url": "https://neptunecigar.com/x"},
                    },
                }
            ],
            "sourceUrls": ["https://famous-smoke.com/x"],
        }
        self.assertEqual(
            s.stranice_cigare(cigara),
            [
                "https://humidor.hr/hr/proizvod/x/",
                "https://cigarworld.de/x",
                "https://neptunecigar.com/x",
                "https://famous-smoke.com/x",
            ],
        )

    def test_isti_url_se_ne_ponavlja(self):
        s = _scraper()
        cigara = {
            "vitolas": [{"url": "https://humidor.hr/x"}, {"url": "https://humidor.hr/x"}],
            "priceUrl": "https://humidor.hr/x",
        }
        self.assertEqual(s.stranice_cigare(cigara), ["https://humidor.hr/x"])

    def test_boca_ide_preko_priceUrl(self):
        s = _scraper()
        self.assertEqual(
            s.stranice_pica({"priceUrl": "https://allez.hr/shop/x", "sourceUrls": ["ne-url"]}),
            ["https://allez.hr/shop/x"],
        )


if __name__ == "__main__":
    if not IMA_PILLOW:
        print("Pillow nije instaliran — preskacem (pip install Pillow)")
        sys.exit(0)
    unittest.main(verbosity=2)
