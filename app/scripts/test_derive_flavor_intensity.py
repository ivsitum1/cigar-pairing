"""derive-flavor-intensity: mapiranje CW + raspon kataloga."""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"


def _load():
    spec = importlib.util.spec_from_file_location(
        "derive_flavor_intensity", HERE / "derive-flavor-intensity.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class DeriveFlavorIntensity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load()
        cls.cigars = json.loads((DATA / "cigars.json").read_text(encoding="utf-8"))

    def test_cw_ten_to_five(self):
        m = self.mod.cw_ten_to_five
        self.assertEqual(m(1), 1)
        self.assertEqual(m(2), 1)
        self.assertEqual(m(3), 2)
        self.assertEqual(m(5), 3)
        self.assertEqual(m(6), 3)
        self.assertEqual(m(7), 4)
        self.assertEqual(m(8), 4)
        self.assertEqual(m(10), 5)

    def test_every_line_has_axis(self):
        for c in self.cigars:
            v = c.get("flavorIntensity")
            self.assertIsInstance(v, int, c["id"])
            self.assertGreaterEqual(v, 1, c["id"])
            self.assertLessEqual(v, 5, c["id"])

    def test_shop_coverage(self):
        shop = sum(1 for c in self.cigars if c.get("flavorIntensityFromShop"))
        self.assertGreater(shop, 400)

    def test_not_collapsed_to_one_value(self):
        from collections import Counter

        dist = Counter(c["flavorIntensity"] for c in self.cigars)
        self.assertGreaterEqual(len([v for v in dist.values() if v > 0]), 4)
        self.assertLess(max(dist.values()) / len(self.cigars), 0.55)


if __name__ == "__main__":
    unittest.main()
