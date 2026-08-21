#!/usr/bin/env python3
"""Unit tests for the RumRatings parsers and the catalogue matcher.

Fixtures are hand-written HTML in the three shapes the parser must survive:
schema.org JSON-LD, microdata, and plain markup. No network.

Run from app/:  python scripts/test_rumratings.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rumratings_shared import (  # noqa: E402
    USER_AGENT,
    best_match,
    catalog_target_urls,
    cache_url_from_path,
    detail_links,
    match_score,
    name_from_detail_url,
    next_page_url,
    parse_detail,
    parse_reviews,
    parse_robots,
    percentile_rank,
    sitemap_rum_urls,
    spearman,
)

JSON_LD_PAGE = """
<html><head><title>Hampden Estate 8 Year | RumRatings</title>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Product",
 "name":"Hampden Estate 8 Year",
 "brand":{"@type":"Brand","name":"Hampden Estate"},
 "aggregateRating":{"@type":"AggregateRating","ratingValue":"8.4","ratingCount":"612"}}
</script></head>
<body><h1>Hampden Estate 8 Year</h1>
<div class="review-item">9 Founded in 1753, the estate still ferments with dunder and muck.
 Huge esters, best neat in a copita after dinner.</div>
<div class="comment-body">8 Paired it with a maduro robusto and the smoke went sweet.
 Let it breathe ten minutes before the first sip.</div>
</body></html>
"""

MICRODATA_PAGE = """
<html><head><title>Diplomatico Reserva Exclusiva - RumRatings</title></head>
<body><h1>Diplomatico Reserva Exclusiva</h1>
<span itemprop="ratingValue" content="7.9"></span>
<span itemprop="ratingCount" content="4211"></span>
</body></html>
"""

PLAIN_PAGE = """
<html><head><title>Foursquare Detente | RumRatings</title></head>
<body><h1>Foursquare Detente</h1>
<p>Average rating 8.7 / 10 from 143 ratings</p></body></html>
"""

LISTING_PAGE = """
<html><body>
<a href="/brands/12-hampden-estate-8-year">Hampden</a>
<a href="/brands/12-hampden-estate-8-year">dupe</a>
<a href="https://rumratings.com/brands/44-foursquare-detente">Foursquare</a>
<a href="/brands">index, not a bottle</a>
<a href="https://example.com/brands/9-offsite">other host</a>
<a href="/?page=3">3</a><a href="/?page=2">2</a>
</body></html>
"""

# Live 2026-08-21 shape: /rum/<id>-<slug>, hero <big>score</big>/10, no JSON-LD.
LIVE_PAGE = """
<html><head><title>Admiral Rodney Extra Old 12-Year | Rum Ratings</title></head>
<body>
<h1>Admiral Rodney Extra Old 12-Year</h1>
<turbo-frame id="reviews">
<big style="font-size: 52px; font-weight: 900">7.8</big><span>/10</span>
<span class="whitespace-nowrap">185 ratings</span>
</turbo-frame>
<a href="/companies/7-admiral-rodney-rum">Admiral Rodney</a>
<p class="review-text">Founded in 1753, the estate still ferments with dunder and muck pit.</p>
</body></html>
"""

ROBOTS_FIXTURE = """
User-Agent: *
Disallow: /rum?
Disallow: /like/
Disallow: /prices/
crawl-delay: 30
User-agent: 008
Disallow: /
"""

SITEMAP_FIXTURE = """
<urlset>
 <url><loc>https://rumratings.com</loc></url>
 <url><loc>https://rumratings.com/companies/7-admiral-rodney-rum</loc></url>
 <url><loc>https://rumratings.com/rum/12-admiral-rodney-extra-old-12-year</loc></url>
 <url><loc>https://rumratings.com/rum/44-foursquare-detente</loc></url>
</urlset>
"""


class TestDetailParsing(unittest.TestCase):
    def test_reads_json_ld_first(self):
        rec = parse_detail(JSON_LD_PAGE, "https://rumratings.com/brands/12-hampden-estate-8-year")
        self.assertEqual(rec["parseStrategy"], "json-ld")
        self.assertEqual(rec["name"], "Hampden Estate 8 Year")
        self.assertEqual(rec["brand"], "Hampden Estate")
        self.assertEqual(rec["rating"], 8.4)
        self.assertEqual(rec["votes"], 612)
        self.assertEqual(rec["sourceId"], "12")
        self.assertEqual(rec["slug"], "hampden-estate-8-year")

    def test_falls_back_to_microdata(self):
        rec = parse_detail(MICRODATA_PAGE, "https://rumratings.com/brands/7-diplomatico")
        self.assertEqual(rec["parseStrategy"], "microdata")
        self.assertEqual(rec["rating"], 7.9)
        self.assertEqual(rec["votes"], 4211)
        self.assertEqual(rec["name"], "Diplomatico Reserva Exclusiva")

    def test_falls_back_to_visible_text(self):
        rec = parse_detail(PLAIN_PAGE, "https://rumratings.com/brands/44-foursquare-detente")
        self.assertEqual(rec["parseStrategy"], "text")
        self.assertEqual(rec["rating"], 8.7)
        self.assertEqual(rec["votes"], 143)

    def test_page_without_a_rating_is_a_miss_not_a_zero(self):
        # A miss must be reported, never invented as 0 — it would poison the join.
        self.assertIsNone(parse_detail("<html><h1>Some rum</h1></html>", "https://rumratings.com/brands/1-x"))

    def test_live_rum_path_hero_score_and_company_link(self):
        rec = parse_detail(LIVE_PAGE, "https://rumratings.com/rum/12-admiral-rodney-extra-old-12-year")
        self.assertEqual(rec["parseStrategy"], "hero")
        self.assertEqual(rec["name"], "Admiral Rodney Extra Old 12-Year")
        self.assertEqual(rec["brand"], "Admiral Rodney")
        self.assertEqual(rec["rating"], 7.8)
        self.assertEqual(rec["votes"], 185)
        self.assertEqual(rec["sourceId"], "12")
        self.assertEqual(rec["slug"], "admiral-rodney-extra-old-12-year")
        self.assertTrue(any("dunder and muck" in r["text"] for r in rec["reviews"]))


class TestReviews(unittest.TestCase):
    def test_collects_review_bodies_with_leading_score(self):
        reviews = parse_reviews(JSON_LD_PAGE)
        self.assertEqual(len(reviews), 2)
        self.assertEqual(reviews[0]["score"], 9.0)
        self.assertIn("dunder and muck", reviews[0]["text"])

    def test_skips_scraps(self):
        self.assertEqual(parse_reviews('<div class="review">ok</div>'), [])


class TestListing(unittest.TestCase):
    def test_collects_detail_links_once_and_on_host(self):
        links = detail_links(LISTING_PAGE)
        self.assertEqual(
            links,
            [
                "https://rumratings.com/brands/12-hampden-estate-8-year",
                "https://rumratings.com/brands/44-foursquare-detente",
            ],
        )

    def test_collects_live_rum_paths(self):
        page = '<a href="/rum/12-hampden-estate-8-year">x</a><a href="/rum/12-hampden-estate-8-year">dupe</a>'
        self.assertEqual(
            detail_links(page),
            ["https://rumratings.com/rum/12-hampden-estate-8-year"],
        )

    def test_next_page_takes_the_lowest_page_above_current(self):
        self.assertEqual(
            next_page_url(LISTING_PAGE, "https://rumratings.com/?page=1"),
            "https://rumratings.com/?page=2",
        )

    def test_rel_next_wins(self):
        page = '<link rel="next" href="/?page=9">' + LISTING_PAGE
        self.assertEqual(
            next_page_url(page, "https://rumratings.com/?page=1"),
            "https://rumratings.com/?page=9",
        )

    def test_no_next_on_last_page(self):
        self.assertIsNone(next_page_url(LISTING_PAGE, "https://rumratings.com/?page=3"))


class TestMatching(unittest.TestCase):
    def test_same_bottle_across_naming_styles(self):
        self.assertGreater(match_score("Hampden Estate 8 YO", "Hampden Estate 8 Year"), 0.7)
        self.assertGreater(match_score("Appleton Estate 15 YO Black River Casks",
                                       "Appleton Estate 15 Year Black River Casks"), 0.7)

    def test_age_clash_never_matches(self):
        # The whole point: a 12 must not silently inherit a 15's community score.
        self.assertEqual(match_score("Appleton Estate 12 YO", "Appleton Estate 15 YO"), 0.0)

    def test_shared_filler_words_alone_are_not_a_match(self):
        self.assertEqual(match_score("Gran Reserva Especial", "Gran Reserva Solera"), 0.0)

    def test_best_match_respects_the_floor(self):
        pool = [{"name": "Plantation Xaymaca Special Dry"}, {"name": "Doorly's XO"}]
        hit, score = best_match("Doorly's XO", pool, floor=0.55)
        self.assertEqual(hit["name"], "Doorly's XO")
        self.assertGreaterEqual(score, 0.55)
        self.assertIsNone(best_match("Zacapa 23", pool, floor=0.55)[0])


class TestRobotsAndSitemap(unittest.TestCase):
    def test_robots_allows_detail_and_home_sort_but_not_rum_query(self):
        rp = parse_robots(ROBOTS_FIXTURE)
        self.assertTrue(rp.can_fetch(USER_AGENT, "https://rumratings.com/rum/12-x"))
        self.assertTrue(rp.can_fetch(USER_AGENT, "https://rumratings.com/?sort=rating"))
        self.assertFalse(rp.can_fetch(USER_AGENT, "https://rumratings.com/rum?sort=rating"))
        self.assertEqual(rp.crawl_delay("*"), 30.0)

    def test_sitemap_keeps_only_bottle_urls(self):
        urls = sitemap_rum_urls(SITEMAP_FIXTURE)
        self.assertEqual(
            urls,
            [
                "https://rumratings.com/rum/12-admiral-rodney-extra-old-12-year",
                "https://rumratings.com/rum/44-foursquare-detente",
            ],
        )

    def test_catalog_picks_one_url_and_respects_age(self):
        catalog = [
            {"name": "Admiral Rodney Extra Old 12 Year"},
            {"name": "Foursquare Detente"},
        ]
        urls = [
            "https://rumratings.com/rum/12-admiral-rodney-extra-old-12-year",
            "https://rumratings.com/rum/99-admiral-rodney-extra-old-15-year",
            "https://rumratings.com/rum/44-foursquare-detente",
        ]
        got = catalog_target_urls(urls, catalog, floor=0.7)
        self.assertEqual(
            got,
            [
                "https://rumratings.com/rum/12-admiral-rodney-extra-old-12-year",
                "https://rumratings.com/rum/44-foursquare-detente",
            ],
        )

    def test_name_from_detail_url_drops_numeric_id(self):
        self.assertEqual(
            name_from_detail_url("https://rumratings.com/rum/12-admiral-rodney-extra-old-12-year"),
            "admiral rodney extra old 12 year",
        )

    def test_cache_path_roundtrip_for_rum_and_brands(self):
        self.assertEqual(
            cache_url_from_path("rum-12-admiral-rodney.abc123def456.html"),
            "https://rumratings.com/rum/12-admiral-rodney",
        )
        self.assertEqual(
            cache_url_from_path("brands-44-foursquare-detente.abc123def456.html"),
            "https://rumratings.com/brands/44-foursquare-detente",
        )


class TestStats(unittest.TestCase):
    def test_spearman_on_identical_order_is_one(self):
        self.assertEqual(spearman([(1, 2), (2, 4), (3, 6), (4, 9)]), 1.0)

    def test_spearman_on_reversed_order_is_minus_one(self):
        self.assertEqual(spearman([(1, 9), (2, 6), (3, 4), (4, 2)]), -1.0)

    def test_spearman_needs_three_points(self):
        self.assertIsNone(spearman([(1, 2), (2, 3)]))

    def test_percentile_rank_is_midpoint_on_ties(self):
        self.assertEqual(percentile_rank(5, [1, 5, 5, 9]), 0.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
