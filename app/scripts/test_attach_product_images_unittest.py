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
extract_product_image = _MOD.extract_product_image


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

    def test_extracts_og_image(self) -> None:
        html = '<meta property="og:image" content="https://www.cigarworld.de/bilder/detail/big/13801.jpg">'
        img = extract_product_image(html, "https://www.cigarworld.de/en/zigarren/x")
        self.assertEqual(img, "https://www.cigarworld.de/bilder/detail/big/13801.jpg")

    def test_skips_share_logo(self) -> None:
        html = '<meta property="og:image" content="https://images.famous-smoke.com/image/upload/v1/main/site/fss_share.jpg">'
        img = extract_product_image(html, "https://www.famous-smoke.com/x")
        self.assertIsNone(img)

    def test_extracts_ecuga_product_thumbnail(self) -> None:
        html = (
            '{"props":{"pageProps":{"product":{"media":['
            '{"url":"https://ecuga.com/media/thumbnails/products/aberlour_12_thumbnail_4096.jpg"}'
            "]}}}"
        )
        img = extract_product_image(html, "https://ecuga.com/proizvod/aberlour-12-double-cask")
        self.assertEqual(
            img,
            "https://ecuga.com/media/thumbnails/products/aberlour_12_thumbnail_4096.jpg",
        )

    def test_rewrites_ecuga_katalog_to_product_page(self) -> None:
        url = (
            "https://ecuga.com/katalog/whisky/skotski-maltgrain-whisky/"
            "aberlour-12-double-cask"
        )
        self.assertEqual(
            _MOD.shop_fetch_url(url),
            "https://ecuga.com/proizvod/aberlour-12-double-cask",
        )
        self.assertEqual(
            _MOD.shop_fetch_url("https://www.cigarworld.de/en/zigarren/x"),
            "https://www.cigarworld.de/en/zigarren/x",
        )

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
