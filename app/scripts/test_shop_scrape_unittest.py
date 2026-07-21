import sys
import unittest
from pathlib import Path

# Ensure `app/scripts` is on sys.path so tests can import `shop_scrape.*`.
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from shop_scrape.http import _cache_key, iso_utc_now  # noqa: E402
from shop_scrape.woocommerce import wc_price_to_amount  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()

