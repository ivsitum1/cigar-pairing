#!/usr/bin/env python3
"""Preuzmi fotografije proizvoda koje aplikacija vec prikazuje.

Drugi korak od tri:

    attach-product-images.py   nadje ADRESU slike kod duckana -> productImages.json
    fetch-product-images.py    preuzme te slike               -> output/product-images/raw/
    normalize-product-images.py obradi podloge                -> public/img/products/

Aplikacija te slike danas prikazuje izravno s tudjeg posluzitelja, svaku na
podlozi koju je taj duckan koristio — bijela kod Humidora i CigarWorlda, crna
kod Neptunea, drvo kod Alleza. Da bi se podloge dale ujednaciti, slika mora
prvo doci k nama; to radi ova skripta.

ODAKLE ADRESA. Prvenstveno iz `productImages.json` — tamo je vec razrijeseno
koja je fotografija ciji proizvod, pa se stranice ne otvaraju ponovno. Za
stavke kojih u tom popisu nema, otvara se stranica proizvoda koju katalog zna
(`vitolas[].url`, `regionLinks`, `priceUrl`) i s nje se cita `og:image`, pa
JSON-LD `Product.image`, pa `<link rel="image_src">`. Prvi `<img>` sa stranice
se NE uzima: to je redovito logo duckana ili ikona kosarice.

Izlaz:
  output/product-images/raw/<vrsta>/<id>.<ext>   originali, netaknuti
  output/product_images_raw.json                 popis: id -> izvor, datoteka

Skripta je pristojna prema duckanima: pauza izmedju zahtjeva, resume po
zadanom (vec preuzeto se preskace) i staje na prvi znak blokade.

Pokreni iz app/:
    python3 scripts/fetch-product-images.py --kind cigars --limit 50
    python3 scripts/fetch-product-images.py --kind drinks
    python3 scripts/fetch-product-images.py --force        # ponovno sve
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
OUT = HERE / "output"
RAW_DIR = OUT / "product-images" / "raw"
INDEX = OUT / "product_images_raw.json"

MANIFEST = DATA / "productImages.json"

DRINK_FILES = (
    "rums.json",
    "whiskies.json",
    "gins.json",
    "tequilas.json",
    "brandies.json",
    "wines.json",
    "digestifs.json",
    "coffees.json",
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "hr-HR,hr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/*;q=0.8,*/*;q=0.7",
}

PAUZA_S = 1.8
NAJVECA_SLIKA_MB = 8
VRSTE_SLIKA = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}

# Slike manje od ovoga su ikone, ne proizvodi.
NAJMANJE_BAJTOVA = 4000


# ── citanje HTML-a ────────────────────────────────────────────────────────────


def _meta(page: str, kljuc: str, vrijednost: str) -> str | None:
    """Sadrzaj <meta> taga, bez obzira na redoslijed atributa."""
    uzorci = (
        rf'<meta[^>]+{kljuc}=["\']{re.escape(vrijednost)}["\'][^>]*content=["\']([^"\']+)["\']',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]*{kljuc}=["\']{re.escape(vrijednost)}["\']',
    )
    for u in uzorci:
        m = re.search(u, page, re.I)
        if m:
            return m.group(1).strip()
    return None


def _iz_json_ld(page: str) -> str | None:
    """Product.image iz JSON-LD bloka; podnosi i niz i objekt i puko polje."""
    for blok in re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        page,
        re.I | re.S,
    ):
        try:
            podatak = json.loads(blok.strip())
        except json.JSONDecodeError:
            continue
        for cvor in podatak if isinstance(podatak, list) else [podatak]:
            if not isinstance(cvor, dict):
                continue
            if "@graph" in cvor and isinstance(cvor["@graph"], list):
                for g in cvor["@graph"]:
                    if isinstance(g, dict) and g.get("@type") == "Product" and g.get("image"):
                        cvor = g
                        break
            slika = cvor.get("image")
            if isinstance(slika, str):
                return slika
            if isinstance(slika, list) and slika:
                prva = slika[0]
                if isinstance(prva, str):
                    return prva
                if isinstance(prva, dict) and prva.get("url"):
                    return prva["url"]
            if isinstance(slika, dict) and slika.get("url"):
                return slika["url"]
    return None


def slika_sa_stranice(page: str, osnovni_url: str) -> str | None:
    """Apsolutni URL glavne fotografije proizvoda, ili None.

    Ovo je jedini dio skripte koji ovisi o obliku stranice, pa je izdvojen i
    pokriven testom — mreza za njega nije potrebna.
    """
    kandidat = (
        _meta(page, "property", "og:image")
        or _meta(page, "name", "og:image")
        or _meta(page, "name", "twitter:image")
        or _iz_json_ld(page)
    )
    if not kandidat:
        m = re.search(r'<link[^>]+rel=["\']image_src["\'][^>]*href=["\']([^"\']+)["\']', page, re.I)
        kandidat = m.group(1) if m else None
    if not kandidat:
        return None
    kandidat = kandidat.replace("&amp;", "&").strip()
    if kandidat.startswith("data:"):
        return None
    return urllib.parse.urljoin(osnovni_url, kandidat)


# ── odakle uzeti stranicu proizvoda ───────────────────────────────────────────


def stranice_cigare(cigar: dict) -> list[str]:
    """URL-ovi proizvoda za jednu cigaru, HR pa EU pa USA."""
    hr: list[str] = []
    eu: list[str] = []
    usa: list[str] = []
    for v in cigar.get("vitolas") or []:
        if v.get("url"):
            hr.append(v["url"])
        for regija, veza in (v.get("regionLinks") or {}).items():
            if isinstance(veza, dict) and veza.get("url"):
                (eu if regija == "EU" else usa).append(veza["url"])
    for regija, veza in (cigar.get("regionLinks") or {}).items():
        if isinstance(veza, dict) and veza.get("url"):
            (eu if regija == "EU" else usa).append(veza["url"])
    if cigar.get("priceUrl"):
        hr.append(cigar["priceUrl"])
    ostalo = [u for u in (cigar.get("sourceUrls") or []) if isinstance(u, str)]

    poredano: list[str] = []
    for u in hr + eu + usa + ostalo:
        if u not in poredano:
            poredano.append(u)
    return poredano


def stranice_pica(drink: dict) -> list[str]:
    poredano: list[str] = []
    for u in (drink.get("priceUrl"), *(drink.get("sourceUrls") or [])):
        if isinstance(u, str) and u.startswith("http") and u not in poredano:
            poredano.append(u)
    return poredano


def poznate_slike(vrsta: str) -> dict[str, str]:
    """id -> izravna adresa slike, iz popisa koji aplikacija vec koristi."""
    if not MANIFEST.exists():
        return {}
    popis = json.loads(MANIFEST.read_text(encoding="utf-8"))
    mapa = popis.get(vrsta) or {}
    return {i: u for i, u in mapa.items() if isinstance(u, str) and u.startswith("http")}


def worklist(vrsta: str) -> list[tuple[str, list[str]]]:
    """(id, stranice) po stavci — stranice se citaju samo ako slike nema u popisu."""
    if vrsta == "cigars":
        stavke = [
            (c["id"], stranice_cigare(c))
            for c in json.loads((DATA / "cigars.json").read_text(encoding="utf-8"))
        ]
    else:
        stavke = []
        for ime in DRINK_FILES:
            put = DATA / ime
            if not put.exists():
                continue
            for d in json.loads(put.read_text(encoding="utf-8")):
                stavke.append((d["id"], stranice_pica(d)))
    return stavke


# ── mreza ─────────────────────────────────────────────────────────────────────


def dohvati(url: str, timeout: int = 20) -> tuple[bytes, str] | None:
    try:
        zahtjev = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(zahtjev, timeout=timeout) as odgovor:
            duljina = odgovor.headers.get("Content-Length")
            if duljina and int(duljina) > NAJVECA_SLIKA_MB * 1024 * 1024:
                return None
            return odgovor.read(), (odgovor.headers.get_content_type() or "")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, TimeoutError) as e:
        print(f"    preskacem ({type(e).__name__}): {url}")
        return None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--kind", choices=("cigars", "drinks"), default="cigars")
    p.add_argument("--limit", type=int, default=0, help="0 = bez ogranicenja")
    p.add_argument("--force", action="store_true", help="ponovno preuzmi i vec spremljeno")
    p.add_argument("--pause", type=float, default=PAUZA_S)
    args = p.parse_args()

    indeks = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else {}
    indeks.setdefault(args.kind, {})
    vec = indeks[args.kind]

    izravne = poznate_slike(args.kind)
    stavke = worklist(args.kind)
    posao = [
        (i, u) for i, u in stavke if (u or i in izravne) and (args.force or i not in vec)
    ]
    if args.limit:
        posao = posao[: args.limit]

    print(
        f"{args.kind}: {len(stavke)} u katalogu, {len(izravne)} s poznatom adresom, "
        f"{len(posao)} za preuzeti"
    )
    odredisce = RAW_DIR / args.kind
    odredisce.mkdir(parents=True, exist_ok=True)

    def spremi(pid: str, url_slike: str, izvor_stranice: str) -> bool:
        """Preuzmi jednu sliku i upisi je u indeks. False = nije upotrebljiva."""
        slika = dohvati(url_slike)
        time.sleep(args.pause)
        if not slika or len(slika[0]) < NAJMANJE_BAJTOVA:
            return False
        nastavak = VRSTE_SLIKA.get(slika[1], Path(urllib.parse.urlparse(url_slike).path).suffix)
        if nastavak.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            return False
        datoteka = odredisce / f"{pid}{nastavak}"
        datoteka.write_bytes(slika[0])
        vec[pid] = {
            "page": izvor_stranice,
            "image": url_slike,
            "file": f"{args.kind}/{datoteka.name}",
            "bytes": len(slika[0]),
            "fetchedAt": date.today().isoformat(),
        }
        print(f"    ✓ {datoteka.name} ({len(slika[0]) // 1024} kB)")
        return True

    uspjeh = 0
    for n, (pid, stranice) in enumerate(posao, 1):
        print(f"[{n}/{len(posao)}] {pid}")

        # 1) adresa je vec poznata — stranica se ne otvara
        izravna = izravne.get(pid)
        if izravna and spremi(pid, izravna, izravna):
            uspjeh += 1
            if n % 25 == 0:
                INDEX.write_text(
                    json.dumps(indeks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
            continue

        # 2) inace: otvori stranicu proizvoda i procitaj og:image
        for stranica in stranice[:3]:
            html_bytes = dohvati(stranica)
            time.sleep(args.pause)
            if not html_bytes:
                continue
            page = html_bytes[0].decode("utf-8", errors="replace")
            url_slike = slika_sa_stranice(page, stranica)
            if not url_slike:
                continue
            if spremi(pid, url_slike, stranica):
                uspjeh += 1
                break
        else:
            print("    — nema upotrebljive slike")

        if n % 25 == 0:
            INDEX.write_text(
                json.dumps(indeks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )

    INDEX.write_text(json.dumps(indeks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\ngotovo: {uspjeh} novih slika, ukupno {len(vec)} za {args.kind}")
    print(f"indeks: {INDEX.relative_to(HERE.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
