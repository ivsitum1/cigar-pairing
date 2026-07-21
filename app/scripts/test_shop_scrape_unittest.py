import sys
import unittest
from pathlib import Path

# Ensure `app/scripts` is on sys.path so tests can import `shop_scrape.*`.
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from shop_scrape.details import (  # noqa: E402
    parse_cigarworld_variant_info,
    parse_holts_line_details,
    parse_holts_vitola_rows,
    parse_humidor_product_details,
    parse_wc_store_attributes,
    prefer_holts_pack,
)
from shop_scrape.http import _cache_key, iso_utc_now  # noqa: E402
from shop_scrape.jsonld import extract_jsonld_products  # noqa: E402
from shop_scrape.sitemap import iter_sitemap_locs  # noqa: E402
from shop_scrape.woocommerce import wc_normalize_product, wc_price_to_amount  # noqa: E402


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


class TestDetailParsers(unittest.TestCase):
    def test_parse_humidor_product_details(self):
        html = """
<span class="product-brand-label">1502</span>
<div class="product-specs-grid">
  <div class="product-spec-card"><div class="product-spec-card__label">Length</div><div class="product-spec-card__value">6 inch <span>/ 15.2 cm</span></div></div>
  <div class="product-spec-card"><div class="product-spec-card__label">Diameter</div><div class="product-spec-card__value">Ring 50 <span>/ 2 cm</span></div></div>
  <div class="product-spec-card"><div class="product-spec-card__label">Wrapper <span>Type</span></div><div class="product-spec-card__value">Ecuadorian Habano</div></div>
  <div class="product-spec-card"><div class="product-spec-card__label">Binder</div><div class="product-spec-card__value">Mexican San Andres</div></div>
  <div class="product-spec-card"><div class="product-spec-card__label">Filler</div><div class="product-spec-card__value">Nicaragua</div></div>
  <div class="product-spec-card"><div class="product-spec-card__label">Origin</div><div class="product-spec-card__value">Nicaragua</div></div>
  <div class="product-spec-card"><div class="product-spec-card__label">Strength</div><div class="product-spec-card__value"><ul class="strength-bars s3" aria-label="3/5"></ul></div></div>
  <div class="product-spec-card"><div class="product-spec-card__label">Burning Time</div><div class="product-spec-card__value">75 min</div></div>
</div>
<section></section>
"""
        d = parse_humidor_product_details(html)
        self.assertEqual(d["wrapper"], "Ecuadorian Habano")
        self.assertEqual(d["binder"], "Mexican San Andres")
        self.assertEqual(d["filler"], "Nicaragua")
        self.assertEqual(d["origin"], "Nicaragua")
        self.assertEqual(d["strength"], 3)
        self.assertEqual(d["burnTimeMin"], 75)
        self.assertEqual(d["ringGauge"], 50)
        self.assertEqual(d["lengthIn"], 6.0)
        self.assertEqual(d["brandLabel"], "1502")

    def test_parse_cigarworld_variant_info(self):
        html = """
<div class="ws-u-1 VariantInfo-itemName">Size</div>
<div class="ws-u-1 VariantInfo-itemValue">Robusto</div>
<div class="ws-u-1 VariantInfo-itemName">Ring / Diameter</div>
<div class="ws-u-1 VariantInfo-itemValue"><u>48</u> / <u>1.91 cm</u></div>
<div class="ws-u-1 VariantInfo-itemName">Wrapper origin</div>
<div class="ws-u-1 VariantInfo-itemValue"><u>Cameroon</u></div>
<div class="ws-u-1 VariantInfo-itemName">Binder origin</div>
<div class="ws-u-1 VariantInfo-itemValue"><u>Dominican Republic</u></div>
<div class="ws-u-1 VariantInfo-itemName">Filler origin</div>
<div class="ws-u-1 VariantInfo-itemValue"><u>Dominican Republic</u></div>
<div class="ws-u-1 VariantInfo-itemName">Boxpressed</div>
<div class="ws-u-1 VariantInfo-itemValue"><u>No</u></div>
<div class="ws-u-1 VariantInfo-itemName">Tabacalera</div>
<div class="ws-u-1 VariantInfo-itemValue">A. Fuente y Cia.</div>
"""
        d = parse_cigarworld_variant_info(html)
        self.assertEqual(d["size"], "Robusto")
        self.assertEqual(d["wrapper"], "Cameroon")
        self.assertEqual(d["binder"], "Dominican Republic")
        self.assertEqual(d["filler"], "Dominican Republic")
        self.assertEqual(d["ringGauge"], 48)
        self.assertEqual(d["diameterCm"], 1.91)
        self.assertEqual(d["boxPressed"], False)
        self.assertEqual(d["tabacalera"], "A. Fuente y Cia.")


if __name__ == "__main__":
    unittest.main()

