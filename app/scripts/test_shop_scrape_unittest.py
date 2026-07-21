import sys
import unittest
from pathlib import Path

# Ensure `app/scripts` is on sys.path so tests can import `shop_scrape.*`.
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from shop_scrape.http import _cache_key, iso_utc_now  # noqa: E402
from shop_scrape.woocommerce import wc_price_to_amount  # noqa: E402
from shop_scrape.jsonld import extract_jsonld_products  # noqa: E402
from shop_scrape.sitemap import iter_sitemap_locs  # noqa: E402


class TestHttpHelpers(unittest.TestCase):
    def test_cache_key_is_stable(self):
        self.assertEqual(_cache_key("https://x.test/a?b=1"), _cache_key("https://x.test/a?b=1"))

    def test_iso_utc_now_is_isoish(self):
        s = iso_utc_now()
        self.assertTrue(s.endswith("Z"))
        self.assertIn("T", s)


class TestWooCommerce(unittest.TestCase):
    def test_wc_price_to_amount(self):
        prices = {"price": "1200", "currency_minor_unit": 2}
        self.assertEqual(wc_price_to_amount(prices), 12.0)


class TestSitemapAndJsonLd(unittest.TestCase):
    def test_iter_sitemap_locs(self):
        xml = """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/a</loc></url>
  <url><loc>https://example.com/b</loc></url>
</urlset>"""
        self.assertEqual(iter_sitemap_locs(xml), ["https://example.com/a", "https://example.com/b"])

    def test_extract_jsonld_products(self):
        html = """<html><head>
<script type="application/ld+json">{\"@type\":\"Product\",\"name\":\"X\",\"offers\":{\"price\":\"12.00\",\"priceCurrency\":\"EUR\",\"availability\":\"http://schema.org/InStock\"}}</script>
</head></html>"""
        ps = extract_jsonld_products(html)
        self.assertEqual(ps[0]["name"], "X")


if __name__ == "__main__":
    unittest.main()

