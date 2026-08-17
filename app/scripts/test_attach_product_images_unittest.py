# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent / "attach-product-images.py"
_SPEC = importlib.util.spec_from_file_location("attach_product_images", _SCRIPT)
assert _SPEC and _SPEC.loader
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)
is_http_image = _MOD.is_http_image
parse_allez_listing = _MOD.parse_allez_listing
pick_offer_image = _MOD.pick_offer_image


class AllezListingParseTests(unittest.TestCase):
    def test_extracts_product_url_and_image(self) -> None:
        html = """
        <div class="product-image"><a href="/shop/svi-proizvodi/aberfeldy-21-yo">
        <img loading="lazy" src="https://allez.hr/imager/300x400/upload/thumbs/aberfeldy.jpeg" alt="Aberfeldy">
        </a></div>
        """
        rows = parse_allez_listing(html)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "https://allez.hr/shop/svi-proizvodi/aberfeldy-21-yo")
        self.assertIn("aberfeldy.jpeg", rows[0][1])

    def test_rejects_placeholder(self) -> None:
        self.assertFalse(is_http_image("https://shop.example/placeholder.png"))
        self.assertTrue(is_http_image("https://havana-cigar-shop.com/wp-content/uploads/x.png"))

    def test_prefers_hr_shop_image(self) -> None:
        img = pick_offer_image(
            [
                {"sourceShopId": "cigarsdaily_us", "image": "https://cigarsdaily.com/a.jpg"},
                {"sourceShopId": "havana_hr", "image": "https://havana-cigar-shop.com/b.png"},
            ]
        )
        self.assertEqual(img, "https://havana-cigar-shop.com/b.png")


if __name__ == "__main__":
    unittest.main()
