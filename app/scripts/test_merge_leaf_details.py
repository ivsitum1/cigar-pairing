#!/usr/bin/env python3
"""Testovi za citanje veznog lista i punjenja iz duckanskih redaka.

Sve tvrdnje ovdje su stvarne niske iz `neptune_raw.json` i
`cigarworld_flavor_raw.json` — ne izmisljeni primjeri.

Pokreni iz app/:  python3 scripts/test_merge_leaf_details.py
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def _ucitaj():
    spec = importlib.util.spec_from_file_location("merge_leaf_details", HERE / "merge-leaf-details.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


m = _ucitaj()


class TestSjeme(unittest.TestCase):
    """Kubansko sjeme nije kubanski duhan — najskuplja zamjena u ovom mergeu."""

    def test_cuban_seed_ne_daje_kubansko_podrijetlo(self):
        self.assertIsNone(m.jedno_podrijetlo("Cuban Seed"))
        self.assertEqual(m.sorta_iz_teksta("Cuban Seed"), "Cuban Seed")

    def test_zemlja_uzgoja_stoji_iza_sjemena(self):
        self.assertEqual(m.jedno_podrijetlo("Cuban Seed Nicaraguan"), "Nikaragva")
        self.assertEqual(m.sorta_iz_teksta("Cuban Seed Nicaraguan"), "Cuban Seed")
        self.assertEqual(m.jedno_podrijetlo("Cuban Seed Dominican"), "Dominikanska Republika")

    def test_sorta_sa_sufiksom_seed_nije_isto(self):
        # "Ecuadorian Sumatra-Seed": vodeca rijec je mjesto, sorta je Sumatra
        self.assertEqual(m.sorta_iz_teksta("Ecuadorian Sumatra-Seed"), "Sumatra-Seed")


class TestZemljaISorta(unittest.TestCase):
    def test_sam_naziv_zemlje_ne_daje_sortu(self):
        for tekst in ("Nicaragua", "Dominican Republic", "Honduras"):
            self.assertIsNone(m.sorta_iz_teksta(tekst), tekst)
            self.assertIsNotNone(m.jedno_podrijetlo(tekst), tekst)

    def test_zemlja_pa_sorta_se_razdvajaju(self):
        self.assertEqual(m.sorta_iz_teksta("Ecuador Sumatra"), "Sumatra")
        self.assertEqual(m.sorta_iz_teksta("Dominican Republic Piloto Cubano"), "Piloto Cubano")
        self.assertEqual(m.jedno_podrijetlo("Dominican Republic Piloto Cubano"), "Dominikanska Republika")

    def test_sumatra_i_connecticut_ostaju_sorte(self):
        # Rjecnik ih zna kao mjesta (Indonezija, SAD), ali u polju lista su sorte
        self.assertEqual(m.sorta_smije("Sumatra", "Ekvador"), "Sumatra")
        self.assertEqual(m.sorta_smije("Connecticut", "Ekvador"), "Connecticut")

    def test_vodeca_zemlja_razrjesava_dvoznacan_redak(self):
        # "Ecuadorian Connecticut Shade" — connecticutska sorta iz Ekvadora
        self.assertEqual(m.jedno_podrijetlo("Ecuadorian Connecticut Shade"), "Ekvador")


class TestSumIzDuckana(unittest.TestCase):
    def test_nepoznato_se_ne_upisuje_kao_sorta(self):
        for tekst in ("Undisclosed", "Mixed", "Various", "unbekannt / geheim"):
            self.assertIsNone(m.sorta_smije(m.sorta_iz_teksta(tekst), None), tekst)

    def test_njemacko_nepoznato_nije_dvije_zemlje(self):
        # kosa crta u "unbekannt / geheim" nije popis zemalja
        self.assertIsNone(m.jedno_podrijetlo("unbekannt / geheim"))

    def test_zemlja_koju_rjecnik_ne_zna_ne_postaje_sorta(self):
        # Toscano: punjenje pise "Italy" — zemlja bez prijevoda, ne sorta
        self.assertIsNone(m.sorta_smije("Italy", None))
        self.assertIsNone(m.sorta_smije("Central America", None))

    def test_njemacki_i_pogresno_napisani_nazivi_mjesta_padaju(self):
        # CigarWorld pise njemacki, a zna i pogrijesiti ("Columbia")
        for tekst in ("Kolumbien", "Mexiko", "Brasilien", "Germany", "Columbia", "Zimbabwe"):
            self.assertIsNone(m.sorta_smije(tekst, None), tekst)

    def test_popis_nije_sorta_bez_obzira_na_jezik(self):
        # Oblik odlucuje, ne rjecnik — zato pada i njemacki popis
        for tekst in (
            "Ecuador, Nicaragua",
            "Kolumbien, Nicaragua",
            "Condega, Criollo, Esteli",
            "Secret - Proprietary, Nicaragua, USA",
            "unknown / confidential",
            "Nicaragua and Peru",
        ):
            self.assertIsNone(m.sorta_smije(tekst, None), tekst)

    def test_prave_sorte_prezive(self):
        for tekst in ("Criollo 98", "Piloto Cubano", "Mata Fina", "Connecticut Broadleaf"):
            self.assertEqual(m.sorta_smije(tekst, "Nikaragva"), tekst)

    def test_sorta_ne_ponavlja_svoje_podrijetlo(self):
        self.assertIsNone(m.sorta_smije("Indonesia", "Indonezija"))
        self.assertIsNone(m.sorta_smije("Nikaragva", "Nikaragva"))


class TestVisestrukoPodrijetlo(unittest.TestCase):
    def test_mjesavina_zemalja_ostaje_neupisana(self):
        for tekst in ("Dominican Republic, Nicaragua", "Honduras and Nicaragua", "Brazil / Peru"):
            self.assertIsNone(m.jedno_podrijetlo(tekst), tekst)

    def test_izvori_koji_se_ne_slazu_ne_daju_upis(self):
        # CigarWorld: mjesavina; Neptune: jedna zemlja -> nista se ne upisuje
        self.assertTrue(m.izvori_se_ne_slazu("Honduras, Nicaragua", "Dominican Republic Piloto Cubano"))

    def test_slaganje_ili_samo_jedan_izvor_prolazi(self):
        self.assertFalse(m.izvori_se_ne_slazu("Nicaragua", "Nicaragua"))
        self.assertFalse(m.izvori_se_ne_slazu(None, "Nicaragua"))
        self.assertFalse(m.izvori_se_ne_slazu("Honduras, Nicaragua", None))
        # obje strane mjesavina — nema jedne zemlje koju bi se moglo upisati
        self.assertFalse(m.izvori_se_ne_slazu("Honduras, Nicaragua", "Brazil, Peru"))


class TestUpisUZapis(unittest.TestCase):
    def test_upisano_se_ne_prepisuje(self):
        cigar = {"binder": "Kurirani list", "binderOrigin": "Kuba"}
        nep = {"binder": "Ecuador Sumatra"}
        self.assertEqual(m.prijedlozi(cigar, nep, None), {})

    def test_prazno_se_popunjava_iz_neptunea(self):
        cigar = {}
        nep = {"binder": "Ecuador Sumatra"}
        self.assertEqual(m.prijedlozi(cigar, nep, None), {"binderOrigin": "Ekvador", "binder": "Sumatra"})

    def test_cigarworldova_sorta_ima_prednost_pred_neptuneovom(self):
        cigar = {}
        nep = {"binder": "Ecuador Sumatra"}
        cw = {"facts": {"binder origin": "Mexico", "binder variety": "San Andrés"}}
        self.assertEqual(
            m.prijedlozi(cigar, nep, cw), {"binderOrigin": "Meksiko", "binder": "San Andrés"}
        )

    def test_sorta_upisana_u_polje_podrijetla_se_ne_baca(self):
        # duckan je u "filler origin" stavio sortu; Corojo nije zemlja
        cigar = {}
        cw = {"facts": {"filler origin": "Corojo"}}
        self.assertEqual(m.prijedlozi(cigar, None, cw), {"filler": "Corojo"})

    def test_pokrovu_se_dira_samo_podrijetlo(self):
        # `wrapper` je popunjen u cijelom katalogu i kuriran je
        cigar = {"wrapper": "H-2000"}
        cw = {"facts": {"wrapper origin": "Ecuador", "wrapper variety": "Habano"}}
        self.assertEqual(m.prijedlozi(cigar, None, cw), {"wrapperOrigin": "Ekvador"})

    def test_bez_izvora_nema_izmjena(self):
        self.assertEqual(m.prijedlozi({}, None, None), {})
        self.assertEqual(m.prijedlozi({}, {}, {"facts": {}}), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
