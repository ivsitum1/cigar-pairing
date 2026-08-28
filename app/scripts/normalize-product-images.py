#!/usr/bin/env python3
"""Preuzete fotografije -> ujednacene slike koje aplikacija prikazuje.

Ulaz:  output/product-images/raw/<vrsta>/<id>.<ext>  (fetch-product-images.py)
Izlaz: public/img/products/<vrsta>/<id>.webp         (WebP s prozirnom podlogom)
       src/data/productImagesLocal.json             (popis obradjenih)

PISE U ODVOJEN POPIS. `productImages.json` je popis adresa kod duckana i njime
aplikacija radi i bez ijedne obradjene slike; ovdje mu se NE dira sadrzaj.
Obradjene idu u `productImagesLocal.json`, a `lib/productImage.ts` bira:
obradjena ako postoji, inace duckanska. Tako obrada moze stati na pola i
aplikacija i dalje pokazuje sve slike.

Sav posao oko podloge radi `product_image_lib`; ovdje je samo prolaz kroz
datoteke, izvjestaj i popis. Idempotentno je — slika koja se nije promijenila
daje isti izlaz, pa ponovno pokretanje ne mijenja repo.

Popis nosi po stavci sirinu, visinu i postupak ("cutout" ili "framed").
Sirina i visina su tu da kartica rezervira prostor prije nego se slika ucita,
a postupak da zna crta li plohu iza slike ili ne.

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
MANIFEST = APP / "src" / "data" / "productImagesLocal.json"
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


def _obradi_jednu(
    put_str: str,
    pid: str,
    izvor_url: str | None,
    sirina: int,
    cilj_str: str,
    provjera: bool,
) -> tuple[str, dict | None, dict]:
    """Worker: jedna slika. Vraća (pid, popis_entry|None, redak)."""
    from PIL import Image, UnidentifiedImageError  # noqa: PLC0415

    lib = _lib()
    put = Path(put_str)
    cilj = Path(cilj_str)
    try:
        with Image.open(put) as img:
            img.load()
            obradjena, izvjestaj = lib.obradi(img, stranica=sirina)
    except (UnidentifiedImageError, OSError) as e:
        return pid, None, {"id": pid, "greska": f"{type(e).__name__}: {e}"}

    bajtova = 0 if provjera else lib.spremi_webp(obradjena, cilj)
    popis = {
        "w": izvjestaj.sirina,
        "h": izvjestaj.visina,
        "t": izvjestaj.postupak,
    }
    redak = {
        "id": pid,
        "izvor": _domena(izvor_url),
        "postupak": izvjestaj.postupak,
        "podloga": izvjestaj.podloga,
        "udio_ruba": izvjestaj.udio_ruba,
        "udio_proizvoda": izvjestaj.udio_proizvoda,
        "svjetlina": izvjestaj.svjetlina_faktor,
        "px": f"{izvjestaj.sirina}x{izvjestaj.visina}",
        "kb": round(bajtova / 1024, 1) if bajtova else None,
    }
    return pid, popis, redak


def obradi_vrstu(
    vrsta: str, limit: int, sirina: int, provjera: bool, jobs: int = 1
) -> tuple[dict, list[dict]]:
    izvori = json.loads(RAW_INDEX.read_text(encoding="utf-8")) if RAW_INDEX.exists() else {}
    izvori_vrste = izvori.get(vrsta, {})

    ulaz_dir = RAW_DIR / vrsta
    datoteke = sorted(p for p in ulaz_dir.glob("*.*") if p.suffix.lower() != ".json")
    if limit:
        datoteke = datoteke[:limit]

    popis: dict[str, dict] = {}
    redci: list[dict] = []
    izlaz_vrste = IZLAZ_DIR / vrsta
    izlaz_vrste.mkdir(parents=True, exist_ok=True)

    staro_popis: dict = {}
    if MANIFEST.exists():
        try:
            staro_popis = (json.loads(MANIFEST.read_text(encoding="utf-8")) or {}).get(
                vrsta, {}
            ) or {}
        except json.JSONDecodeError:
            staro_popis = {}

    # Resume: već gotov WebP ne dira se.
    posao: list[tuple[str, str, str | None, int, str, bool]] = []
    for put in datoteke:
        pid = put.stem
        cilj = izlaz_vrste / f"{pid}.webp"
        if cilj.exists() and not provjera:
            if pid in staro_popis and isinstance(staro_popis[pid], dict):
                popis[pid] = staro_popis[pid]
            else:
                try:
                    from PIL import Image  # noqa: PLC0415

                    with Image.open(cilj) as gotova:
                        gotova.load()
                        popis[pid] = {
                            "w": gotova.width,
                            "h": gotova.height,
                            "t": "framed",
                        }
                except OSError:
                    pass
                else:
                    redci.append({"id": pid, "preskoceno": "vec postoji"})
                    continue
            redci.append({"id": pid, "preskoceno": "vec postoji"})
            continue
        izvor = (izvori_vrste.get(pid) or {}).get("image")
        posao.append((str(put), pid, izvor, sirina, str(cilj), provjera))

    if not posao:
        return popis, redci

    workers = max(1, jobs)
    if workers == 1:
        for i, args in enumerate(posao, 1):
            pid, entry, redak = _obradi_jednu(*args)
            if entry:
                popis[pid] = entry
            redci.append(redak)
            if i % 50 == 0:
                print(f"  {vrsta}: {i}/{len(posao)} (ukupno {len(popis)})")
    else:
        from concurrent.futures import ProcessPoolExecutor, as_completed  # noqa: PLC0415

        print(f"  {vrsta}: {len(posao)} za obradu, jobs={workers}")
        done = 0
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_obradi_jednu, *a) for a in posao]
            for fut in as_completed(futures):
                pid, entry, redak = fut.result()
                if entry:
                    popis[pid] = entry
                redci.append(redak)
                done += 1
                if done % 50 == 0:
                    print(f"  {vrsta}: {done}/{len(posao)} (ukupno {len(popis)})")

    return popis, redci


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--kind", choices=VRSTE, action="append", help="zadano: obje vrste")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--width", type=int, default=800, help="najveca stranica izlazne slike")
    p.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="broj procesa za obradu (1 = sekvencijalno)",
    )
    p.add_argument("--check", action="store_true", help="ne pisi nista (za CI)")
    args = p.parse_args()

    vrste = args.kind or list(VRSTE)
    if not RAW_DIR.exists():
        print(f"Nema preuzetih slika u {RAW_DIR.relative_to(APP)} — prvo pokreni")
        print("  python3 scripts/fetch-product-images.py")
        # Prazan ulaz nije greska: repo se klonira bez slika i CI mora proci.
        return 0

    manifest = {
        "note": (
            "Obradjene slike u public/img/products/ — puni "
            "scripts/normalize-product-images.py. Prazno = jos nijedna nije obradjena, "
            "pa app koristi dućanske URL-ove iz productImages.json."
        ),
        "generatedAt": date.today().isoformat(),
    }
    svi_redci: list[dict] = []
    for vrsta in vrste:
        if not (RAW_DIR / vrsta).exists():
            manifest[vrsta] = {}
            continue
        popis, redci = obradi_vrstu(
            vrsta, args.limit, args.width, args.check, jobs=args.jobs
        )
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
