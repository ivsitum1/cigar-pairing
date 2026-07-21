# -*- coding: utf-8 -*-
"""Tests for shared cigar shop match / dedupe helpers."""
from __future__ import annotations

import unittest

from cigar_shop_match import (
    build_brand_detectors,
    detect_brand,
    find_existing_cigar,
    match_vitola_in_cigar,
    merge_duplicate_cigar_lines,
    norm_product_url,
    parse_pack_suffix,
    resolve_shop_product,
    shop_dedupe_key,
    unique_vitolas,
    vitola_from_product,
)


class TestNormAndPack(unittest.TestCase):
    def test_pack_suffix(self) -> None:
        base, pack = parse_pack_suffix("Montecristo No.2/25")
        self.assertEqual(base, "Montecristo No.2")
        self.assertEqual(pack, 25)
        base2, pack2 = parse_pack_suffix("Cohiba Panetelas/25*")
        self.assertEqual(base2, "Cohiba Panetelas")
        self.assertEqual(pack2, 25)

    def test_norm_product_url(self) -> None:
        self.assertEqual(
            norm_product_url("https://humidor.hr/hr/proizvod/foo/?x=1"),
            "https://humidor.hr/proizvod/foo",
        )


class TestAliasesAndMatch(unittest.TestCase):
    def setUp(self) -> None:
        self.cigars = [
            {
                "id": "cig-aj-fernandez-dias-de-gloria",
                "brand": "AJ Fernandez",
                "line": "Días de Gloria",
                "vitolas": [
                    {"name": "Robusto", "format": "50 x 127mm", "url": "https://humidor.hr/hr/proizvod/dias-robusto/"},
                    {"name": "Toro", "format": "54 x 152mm", "url": None},
                ],
            },
            {
                "id": "cig-montecristo-no4",
                "brand": "Montecristo",
                "line": "No. 4",
                "vitolas": [{"name": "No.4", "format": "42 x 129mm", "url": "https://example.com/no4"}],
            },
            {
                "id": "cig-montecristo-no-4",
                "brand": "Montecristo",
                "line": "No.4",
                "vitolas": [{"name": "Montecristo No.4", "format": "42 x 129mm", "url": None}],
            },
        ]
        self.detectors = build_brand_detectors(self.cigars)

    def test_brand_alias_without_maker_prefix(self) -> None:
        self.assertEqual(detect_brand("Dias de Gloria Robusto", self.detectors), "AJ Fernandez")

    def test_find_existing_via_line_rule(self) -> None:
        c = find_existing_cigar(self.cigars, "AJ Fernandez", "Dias de Gloria Robusto")
        self.assertIsNotNone(c)
        assert c is not None
        self.assertEqual(c["id"], "cig-aj-fernandez-dias-de-gloria")

    def test_vitola_match_by_size(self) -> None:
        cigar = self.cigars[0]
        v = match_vitola_in_cigar(
            cigar,
            "AJ Fernandez Dias de Gloria Something 5 x 50",
            brand="AJ Fernandez",
            details={"ringGauge": 50, "lengthCm": 12.7},
        )
        self.assertIsNotNone(v)
        assert v is not None
        self.assertEqual(v["name"], "Robusto")

    def test_wrapper_hint_blocks_brazil_vs_habano(self) -> None:
        cigar = {
            "id": "cig-aj-fernandez-dias-de-gloria",
            "brand": "AJ Fernandez",
            "line": "Días de Gloria",
            "vitolas": [
                {"name": "Robusto", "format": "52 x 140mm"},
                {"name": "Brazil Toro", "format": "54 x 165mm"},
            ],
        }
        habano = match_vitola_in_cigar(
            cigar,
            "AJ Fernandez Dias De Gloria Habano Toro (6×56)",
            brand="AJ Fernandez",
        )
        self.assertIsNone(habano)
        brazil = match_vitola_in_cigar(
            cigar,
            "AJ Fernandez Dias De Gloria Brazil Toro (6.5×54)",
            brand="AJ Fernandez",
        )
        self.assertIsNotNone(brazil)
        assert brazil is not None
        self.assertEqual(brazil["name"], "Brazil Toro")

    def test_unique_vitolas(self) -> None:
        cigar = {
            "vitolas": [
                {"name": "Robusto"},
                {"name": "robusto"},
                {"name": "Toro"},
            ]
        }
        self.assertEqual([v["name"] for v in unique_vitolas(cigar)], ["Robusto", "Toro"])

    def test_merge_montecristo_duplicate_lines(self) -> None:
        merged, n = merge_duplicate_cigar_lines(self.cigars)
        self.assertGreaterEqual(n, 1)
        ids = [c["id"] for c in merged]
        self.assertIn("cig-montecristo-no4", ids)
        self.assertNotIn("cig-montecristo-no-4", ids)
        mc = next(c for c in merged if c["id"] == "cig-montecristo-no4")
        names = {v["name"] for v in mc["vitolas"]}
        self.assertTrue("No.4" in names or "Montecristo No.4" in names)

    def test_resolve_url_match(self) -> None:
        c, v, brand = resolve_shop_product(
            self.cigars,
            "Whatever",
            detectors=self.detectors,
            url="https://humidor.hr/hr/proizvod/dias-robusto/",
        )
        self.assertEqual(c["id"], "cig-aj-fernandez-dias-de-gloria")
        self.assertEqual(v["name"], "Robusto")
        self.assertEqual(brand, "AJ Fernandez")

    def test_shop_dedupe_key_collapses_pack_noise(self) -> None:
        a = shop_dedupe_key("Montecristo", "Montecristo No.4/25")
        b = shop_dedupe_key("Montecristo", "Montecristo No.4/10")
        # same vitola/line base — pack size stripped from line/vitola extraction
        self.assertEqual(a.split("|")[0], b.split("|")[0])
        self.assertEqual(vitola_from_product("Montecristo No.4/25", "Montecristo"),
                         vitola_from_product("Montecristo No.4/10", "Montecristo"))


if __name__ == "__main__":
    unittest.main()
