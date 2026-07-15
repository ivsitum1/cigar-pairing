# -*- coding: utf-8 -*-
"""Regression tests for brandy style detection (XO mislabeling fix)."""
from __future__ import annotations

import unittest

from brandy_shared import detect_style_region


class DetectStyleRegionTests(unittest.TestCase):
    def test_non_cognac_xo_labels_stay_in_category(self) -> None:
        cases = {
            "Stock 84 XO": "brandy-italian",
            "Badel Vinjak XO / Prima": "vinjak",
            "Christian Drouin XO Calvados": "calvados",
            "Janneau XO Grand Armagnac": "armagnac",
            "Boulard Calvados Pays d Auge XO": "calvados",
            "Asbach Selection Extra Old 21 Jears": "brandy-german",
        }
        for name, expected_style in cases.items():
            style, *_ = detect_style_region(name)
            self.assertEqual(style, expected_style, msg=name)

    def test_cognac_xo_still_detected(self) -> None:
        cases = [
            "Hennessy XO Cognac",
            "Martell XO Extra Old Cognac",
            "Camus XO Intensely Aromatic Cognac",
            "Hine Antique XO",
            "Hennessy PARADIS Rare Cognac",
        ]
        for name in cases:
            style, *_ = detect_style_region(name)
            self.assertEqual(style, "cognac-xo", msg=name)

    def test_jerez_brandy_unchanged(self) -> None:
        style, *_ = detect_style_region("Carlos I Solera Gran Reserva")
        self.assertEqual(style, "brandy-de-jerez")


if __name__ == "__main__":
    unittest.main()
