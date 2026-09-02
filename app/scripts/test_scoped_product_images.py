#!/usr/bin/env python3
"""Sloj fotografija po vitoli (cig-x@robusto) mora proci cijeli lanac.

`productImages.json` nosi 3547 adresa po vitoli, a obradjenih je bilo 0 — pa je
odabir vitole vracao neobradjenu ducansku sliku umjesto izrezane. Lanac to
podrzava, ali nista nije cuvalo da ga znak "@" u imenu ne razbije: on prolazi
kroz ime datoteke, `Path.stem`, kljuc manifesta i `encodeURIComponent` u
aplikaciji. Ovi testovi drze taj put otvorenim, bez mreze i bez binarnih
datoteka u repou.

Pokreni iz app/:  python3 scripts/test_scoped_product_images.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

try:
    from PIL import Image, ImageDraw

    IMA_PILLOW = True
except ImportError:  # pragma: no cover
    IMA_PILLOW = False


def _ucitaj(ime: str):
    """Skripte imaju crticu u imenu, pa se ucitavaju putem, ne importom."""
    spec = importlib.util.spec_from_file_location(ime.replace("-", "_"), HERE / f"{ime}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


SCOPED = "cig-1502-black-gold@robusto"
LINIJA = "cig-1502-black-gold"


def nacrtaj_cigaru(put: Path) -> None:
    """Proizvod na jednolicnoj podlozi — dovoljno da obrada napravi izrez."""
    img = Image.new("RGB", (400, 300), (245, 245, 245))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 130, 340, 170), radius=18, fill=(92, 62, 38))
    d.rectangle((120, 130, 175, 170), fill=(198, 160, 74))
    img.save(put)


@unittest.skipUnless(IMA_PILLOW, "treba Pillow")
class ObradaScopedKljuca(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.raw = self.root / "raw" / "cigars"
        self.raw.mkdir(parents=True)
        self.izlaz = self.root / "out"
        self.manifest = self.root / "productImagesLocal.json"

        self.norm = _ucitaj("normalize-product-images")
        self.norm.RAW_DIR = self.root / "raw"
        self.norm.IZLAZ_DIR = self.izlaz
        self.norm.MANIFEST = self.manifest
        self.norm.RAW_INDEX = self.root / "raw_index.json"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_znak_at_prezivi_ime_datoteke_i_kljuc_manifesta(self) -> None:
        nacrtaj_cigaru(self.raw / f"{SCOPED}.png")
        nacrtaj_cigaru(self.raw / f"{LINIJA}.png")

        popis, redci = self.norm.obradi_vrstu("cigars", limit=0, sirina=400, provjera=False)

        self.assertIn(SCOPED, popis, "scoped kljuc mora zavrsiti u manifestu")
        self.assertIn(LINIJA, popis)
        self.assertTrue(
            (self.izlaz / "cigars" / f"{SCOPED}.webp").exists(),
            "scoped slika mora zavrsiti kao <id>@<vitola>.webp",
        )
        self.assertEqual([r for r in redci if r.get("greska")], [])

    def test_popis_nosi_dimenzije_i_postupak(self) -> None:
        nacrtaj_cigaru(self.raw / f"{SCOPED}.png")
        popis, _ = self.norm.obradi_vrstu("cigars", limit=0, sirina=400, provjera=False)
        unos = popis[SCOPED]
        self.assertGreater(unos["w"], 0)
        self.assertGreater(unos["h"], 0)
        self.assertIn(unos["t"], ("cutout", "framed"))

    def test_ponovni_prolaz_ne_mijenja_izlaz(self) -> None:
        """Resume: vec obradjena scoped slika se preskace, popis ostaje isti."""
        nacrtaj_cigaru(self.raw / f"{SCOPED}.png")
        prvi, _ = self.norm.obradi_vrstu("cigars", limit=0, sirina=400, provjera=False)
        self.manifest.write_text(json.dumps({"cigars": prvi}), encoding="utf-8")
        drugi, redci = self.norm.obradi_vrstu("cigars", limit=0, sirina=400, provjera=False)
        self.assertEqual(prvi, drugi)
        self.assertTrue(any(r.get("preskoceno") for r in redci))


class FiltarPoVitoli(unittest.TestCase):
    """`--scoped only|skip` mora tocno razdvojiti sloj po vitoli od linija."""

    def setUp(self) -> None:
        self.fetch = _ucitaj("fetch-product-images")

    def test_separator_je_isti_kao_u_aplikaciji(self) -> None:
        # cigarItemId u src/lib/cigarItemId.ts koristi "@"
        self.assertEqual(self.fetch.VITOLA_SEP, "@")

    def test_manifest_stvarno_nosi_oba_sloja(self) -> None:
        popis = json.loads(
            (HERE.parent / "src" / "data" / "productImages.json").read_text(encoding="utf-8")
        )["cigars"]
        scoped = [k for k in popis if self.fetch.VITOLA_SEP in k]
        linije = [k for k in popis if self.fetch.VITOLA_SEP not in k]
        self.assertTrue(scoped, "nema nijednog kljuca po vitoli — filtar bi bio besmislen")
        self.assertTrue(linije)
        self.assertEqual(len(scoped) + len(linije), len(popis))


if __name__ == "__main__":
    unittest.main(verbosity=2)
