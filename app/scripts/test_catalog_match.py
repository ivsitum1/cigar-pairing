# -*- coding: utf-8 -*-
"""Regression tests for drink catalog URL matching (pipeline)."""
from __future__ import annotations

from whisky_shared import find_best_catalog_match, match_tokens


def test_rejects_category_and_wrong_sku() -> None:
    catalog = [
        {
            "name": "Havana Club Añejo 15",
            "url": "https://allez.hr/shop/svi-proizvodi/havana-club-gran-reserva-anejo-15-anos-40-vol-07l-u-poklon-kutiji",
            "tokens": match_tokens("Havana Club Anejo 15"),
        },
        {
            "name": "Rum category",
            "url": "https://ecuga.com/katalog/rum",
            "tokens": match_tokens("rum"),
        },
    ]
    assert find_best_catalog_match("Havana Club Tributo", catalog) is None
    assert find_best_catalog_match("Appleton Estate 15", catalog) is None
