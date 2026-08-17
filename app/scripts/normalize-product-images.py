#!/usr/bin/env python3
"""Preuzete fotografije -> ujednacene slike koje aplikacija prikazuje.

Ulaz:  output/product-images/raw/<vrsta>/<id>.<ext>  (scrape-product-images.py)
Izlaz: public/img/products/<vrsta>/<id>.webp         (WebP s prozirnom podlogom)
       src/data/productImages.json                  (popis za aplikaciju)

Sav posao oko podloge radi `product_image_lib`; ovdje je samo prolaz kroz
datoteke, izvjestaj i popis. Idempotentno je — slika koja se nije promijenila
daje isti izlaz, pa ponovno pokretanje ne mijenja repo.

Popis nosi po stavci sirinu, visinu, postupak ("cutout" ili "framed") i domenu
s koje je slika preuzeta. Sirina i visina su tu da kartica rezervira prostor
prije nego se slika ucita (bez poskakivanja sadrzaja), a domena da se zna
odakle je sto doslo.

Pokreni iz app/:
    python3 scripts/normalize-product-images.py
    python3 scripts/normalize-product-images.py --kind drinks --limit 20
    python3 scripts/normalize-product-images.py --check     # samo provjera, ne pise
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

HERE = Path(__file__).resolve().parent
APP = HERE.parent
RAW_DIR = HERE / "output" / "product-images" / "raw"
RAW_INDEX = HERE / "output" / "product_images_raw.json"
IZLAZ_DIR = APP / "public" / "img" / "products"
MANIFEST = APP / "src" / "data" / "productImages.json"
IZVJESTAJ = HERE / "output" / "product_images_report.json"

VRSTE = ("cigars", "drinks")


def _lib():
    try:
        import product_image_lib  # noqa: PLC0415

        return product_image_lib
    except ImportError:
        print("Nedostaje Pillow. Instaliraj:  pip install Pillow", file=sys.stderr)
        raise SystemExit(2) from None


def _domena(url: str | None) -> str:
    if not url:
        return ""
    return urllib.parse.urlparse(url).netloc.removeprefix("www.")


def obradi_vrstu(vrsta: str, limit: int, sirina: int, provjera: bool) -> tuple[dict, list[dict]]:
    lib = _lib()
    from PIL import Image, UnidentifiedImageError  # noqa: PLC0415

    izvori = json.loads(RAW_INDEX.read_text(encoding="utf-8")) if RAW_INDEX.exists() else {}
    izvori_vrste = izvori.get(vrsta, {})

    ulaz_dir = RAW_DIR / vrsta
    datoteke = sorted(p for p in ulaz_dir.glob("*.*") if p.suffix.lower() != ".json")
    if limit:
        datoteke = datoteke[:limit]

    popis: dict[str, dict] = {}
    redci: list[dict] = []
    izlaz_vrste = IZLAZ_DIR / vrsta

    for n, put in enumerate(datoteke, 1):
        pid = put.stem
        try:
            with Image.open(put) as img:
                img.load()
                obradjena, izvjestaj = lib.obradi(img, stranica=sirina)
        except (UnidentifiedImageError, OSError) as e:
            redci.append({"id": pid, "greska": f"{type(e).__name__}: {e}"})
            continue

        cilj = izlaz_vrste / f"{pid}.webp"
        bajtova = 0 if provjera else lib.spremi_webp(obradjena, cilj)

        popis[pid] = {
            "w": izvjestaj.sirina,
            "h": izvjestaj.visina,
            "t": izvjestaj.postupak,
            "s": _domena((izvori_vrste.get(pid) or {}).get("page")),
        }
        redci.append(
            {
                "id": pid,
                "postupak": izvjestaj.postupak,
                "podloga": izvjestaj.podloga,
                "udio_ruba": izvjestaj.udio_ruba,
                "udio_proizvoda": izvjestaj.udio_proizvoda,
                "svjetlina": izvjestaj.svjetlina_faktor,
                "px": f"{izvjestaj.sirina}x{izvjestaj.visina}",
                "kb": round(bajtova / 1024, 1) if bajtova else None,
            }
        )
        if n % 50 == 0:
            print(f"  {vrsta}: {n}/{len(datoteke)}")

    return popis, redci


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--kind", choices=VRSTE, action="append", help="zadano: obje vrste")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--width", type=int, default=800, help="najveca stranica izlazne slike")
    p.add_argument("--check", action="store_true", help="ne pisi nista (za CI)")
    args = p.parse_args()

    vrste = args.kind or list(VRSTE)
    if not RAW_DIR.exists():
        print(f"Nema preuzetih slika u {RAW_DIR.relative_to(APP)} — prvo pokreni")
        print("  python3 scripts/scrape-product-images.py")
        # Prazan ulaz nije greska: repo se klonira bez slika i CI mora proci.
        return 0

    manifest = {"generatedAt": date.today().isoformat()}
    svi_redci: list[dict] = []
    for vrsta in vrste:
        if not (RAW_DIR / vrsta).exists():
            manifest[vrsta] = {}
            continue
        popis, redci = obradi_vrstu(vrsta, args.limit, args.width, args.check)
        manifest[vrsta] = popis
        svi_redci.extend({"vrsta": vrsta, **r} for r in redci)
        cutout = sum(1 for r in redci if r.get("postupak") == "cutout")
        framed = sum(1 for r in redci if r.get("postupak") == "framed")
        greske = sum(1 for r in redci if r.get("greska"))
        print(f"{vrsta}: {len(popis)} slika — {cutout} izrezano, {framed} u okviru, {greske} greska")

    if args.check:
        print("--check: nista nije zapisano")
        return 0

    # Vrste koje se ovaj put nisu obradjivale zadrzavaju ono sto vec imaju.
    if MANIFEST.exists():
        staro = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for vrsta in VRSTE:
            if vrsta not in manifest and vrsta in staro:
                manifest[vrsta] = staro[vrsta]
    for vrsta in VRSTE:
        manifest.setdefault(vrsta, {})

    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    IZVJESTAJ.write_text(
        json.dumps(svi_redci, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\npopis: {MANIFEST.relative_to(APP)}")
    print(f"izvjestaj: {IZVJESTAJ.relative_to(APP)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
