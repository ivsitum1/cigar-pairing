#!/usr/bin/env python3
"""Unit tests for stock_parse (HTML → in-stock / out / unknown).

Run from app/:  python scripts/test_stock_parse.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stock_parse import parse_stock  # noqa: E402


JSONLD_IN = """
<html><head>
<script type="application/ld+json">
{"@type":"Product","offers":{"@type":"Offer","availability":"https://schema.org/InStock"}}
</script>
</head><body></body></html>
"""

JSONLD_OUT = """
<html><head>
<script type="application/ld+json">
{"@type":"Product","offers":[{"@type":"Offer","availability":"http://schema.org/OutOfStock"}]}
</script>
</head><body><button>Add to cart</button></body></html>
"""

WC_IN = """
<html><body>
<p class="stock in-stock">Na zalihi</p>
</body></html>
"""

WC_OUT = """
<html><body>
<p class="stock out-of-stock">Nema na zalihi</p>
<button disabled>Dodaj u košaricu</button>
</body></html>
"""

MICRODATA_IN = """
<html><body>
<link itemprop="availability" href="https://schema.org/InStock" />
</body></html>
"""

SOFT_404 = """
<html><head><title>PAGE NOT FOUND</title></head>
<body><p class="stock in-stock">Na zalihi</p></body></html>
"""

PREORDER = """
<html><head>
<script type="application/ld+json">
{"@type":"Offer","availability":"https://schema.org/PreOrder"}
</script>
</head></html>
"""

EMPTY = "<html><body><h1>Some cigar</h1><p>Nice smoke.</p></body></html>"

BOTH = """
<html><head>
<script type="application/ld+json">
{"@type":"Offer","availability":"https://schema.org/InStock"}
</script>
</head>
<body><p class="stock out-of-stock">Out of stock</p></body></html>
"""

FAMOUS_OUT = """
<html><body>
<div class="availability">Out of Stock</div>
</body></html>
"""

ALLEZ_IN = """
<html><body>
<form id="add-to-cart-form" method="POST">
<div class="single-product-actions-item"><button class="btn">Dodaj u košaricu</button></div>
</form>
</body></html>
"""

ALLEZ_OUT = """
<html><body>
<form id="add-to-cart-form" method="POST">
<p>Rasprodano</p>
<button class="btn" disabled>Dodaj u košaricu</button>
</form>
</body></html>
"""

ECUGA_IN = """
<html><head>
<script id="__NEXT_DATA__" type="application/json">
{"props":{"pageProps":{"product":{"isAvailableForPurchase":true,"variants":[{"quantityAvailable":3}]}}}}
</script>
</head><body></body></html>
"""

ECUGA_OUT = """
<html><head>
<script id="__NEXT_DATA__" type="application/json">
{"props":{"pageProps":{"product":{"isAvailableForPurchase":true,"variants":[{"quantityAvailable":0}]}}}}
</script>
</head><body></body></html>
"""


class TestParseStock(unittest.TestCase):
    def test_jsonld_in_stock(self):
        self.assertIs(parse_stock(JSONLD_IN), True)

    def test_jsonld_out_of_stock(self):
        self.assertIs(parse_stock(JSONLD_OUT), False)

    def test_woocommerce_croatian_in(self):
        self.assertIs(parse_stock(WC_IN), True)

    def test_woocommerce_croatian_out(self):
        self.assertIs(parse_stock(WC_OUT), False)

    def test_microdata_in_stock(self):
        self.assertIs(parse_stock(MICRODATA_IN), True)

    def test_soft_404_is_unknown(self):
        self.assertIsNone(parse_stock(SOFT_404))

    def test_preorder_is_unknown(self):
        self.assertIsNone(parse_stock(PREORDER))

    def test_no_signal_is_unknown(self):
        self.assertIsNone(parse_stock(EMPTY))

    def test_out_wins_when_signals_conflict(self):
        self.assertIs(parse_stock(BOTH), False)

    def test_famous_out_of_stock_phrase(self):
        self.assertIs(parse_stock(FAMOUS_OUT), False)

    def test_allez_add_to_cart_is_in(self):
        self.assertIs(parse_stock(ALLEZ_IN), True)

    def test_allez_disabled_or_phrase_is_out(self):
        self.assertIs(parse_stock(ALLEZ_OUT), False)

    def test_ecuga_saleor_quantity_in(self):
        self.assertIs(parse_stock(ECUGA_IN), True)

    def test_ecuga_saleor_zero_quantity_out(self):
        self.assertIs(parse_stock(ECUGA_OUT), False)

    def test_empty_html_is_unknown(self):
        self.assertIsNone(parse_stock(""))
        self.assertIsNone(parse_stock(None))


if __name__ == "__main__":
    unittest.main()
