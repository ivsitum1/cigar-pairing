# -*- coding: utf-8 -*-
"""Offline tests for ecuga_listings (GraphQL parsing + cursor replay)."""
from __future__ import annotations

import json
import unittest

import ecuga_listings as el


def _products(slugs, *, has_next=False, cursor=None):
    return {
        "edges": [
            {
                "node": {
                    "slug": s,
                    "name": f"Rum {s}",
                    "pricing": {"priceRange": {"start": {"gross": {"amount": 42.5}}}},
                }
            }
            for s in slugs
        ],
        "pageInfo": {"hasNextPage": has_next, "endCursor": cursor},
    }


class EcugaParsing(unittest.TestCase):
    def test_products_from_body(self) -> None:
        body = {"data": {"products": _products(["a"])}}
        self.assertEqual(el.products_from_body(body)["edges"][0]["node"]["slug"], "a")
        self.assertIsNone(el.products_from_body({"data": {"products": {"edges": []}}}))
        self.assertIsNone(el.products_from_body({"data": {"menu": {}}}))
        self.assertIsNone(el.products_from_body(None))

    def test_items_use_product_url_and_dedupe(self) -> None:
        seen: set[str] = {"old"}
        items = el.items_from_products(_products(["old", "new", "new"]), "rum", seen)
        self.assertEqual(len(items), 1)
        it = items[0]
        # catalog stores /proizvod/<slug>; a /katalog/ URL would never reach tier A
        self.assertEqual(it["url"], "https://ecuga.com/proizvod/new")
        self.assertEqual(it["shop"], "ecuga")
        self.assertEqual(it["shopLabel"], "ecuga.com")
        self.assertEqual(it["category"], "rum")
        self.assertEqual(it["price_eur"], 42.5)
        self.assertIn("new", seen)

    def test_pending_seen_defers_commit(self) -> None:
        global_seen: set[str] = set()
        pending: set[str] = set()
        items = el.items_from_products(_products(["a"]), "rum", global_seen, pending)
        self.assertEqual(len(items), 1)
        self.assertEqual(pending, {"a"})
        self.assertEqual(global_seen, set())
        global_seen.update(pending)
        self.assertEqual(global_seen, {"a"})

    def test_missing_price_is_none(self) -> None:
        prods = {"edges": [{"node": {"slug": "x", "name": "X", "pricing": None}}]}
        self.assertIsNone(el.items_from_products(prods, "rum", set())[0]["price_eur"])

    def test_next_page_payload_sets_after(self) -> None:
        req = json.dumps(
            {"query": "query P($first: Int, $after: String) { products }", "variables": {"first": 20}}
        )
        body = el.next_page_payload(req, _products(["a"], has_next=True, cursor="CUR"))
        self.assertEqual(json.loads(body)["variables"], {"first": 20, "after": "CUR"})

    def test_next_page_payload_stops(self) -> None:
        req = json.dumps({"query": "query P($after: String) { products }", "variables": {}})
        self.assertIsNone(el.next_page_payload(req, _products(["a"], has_next=False, cursor="C")))
        self.assertIsNone(el.next_page_payload(None, _products(["a"], has_next=True, cursor="C")))
        # query without an $after variable cannot be cursor-paged
        no_after = json.dumps({"query": "query P { products }", "variables": {}})
        self.assertIsNone(el.next_page_payload(no_after, _products(["a"], has_next=True, cursor="C")))

    def test_rum_is_scanned(self) -> None:
        self.assertIn("rum", [cat for _paths, cat in el.ECUGA_SPIRIT_LISTS])
        self.assertEqual(el.ECUGA_SPIRIT_LISTS[0][0][0], "rum")


if __name__ == "__main__":
    unittest.main()
