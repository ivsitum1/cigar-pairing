# Shop raw catalogs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Python CLI that exports standardized “raw” cigar shop catalogs for HR/EU/USA shops into `app/scripts/output/` without modifying `app/src/data/cigars.json`.

**Architecture:** Prefer stable machine-readable sources (WooCommerce Store API where available, sitemap + JSON-LD where not). Use a shared HTTP layer with rate limiting, caching, and retry/backoff to avoid bans and to keep runs reproducible.

**Tech Stack:** Python 3.12 stdlib (`argparse`, `json`, `urllib`, `xml.etree.ElementTree`, `hashlib`, `datetime`), plus whatever is already present in the runtime image (do not introduce mandatory third-party deps).

## Global Constraints

- No browser automation to bypass anti-bot challenges (e.g. Cloudflare JS challenge).
- Prefer API/sitemap/JSON-LD over brittle HTML selectors.
- Output must follow the standardized raw schema described in `docs/superpowers/specs/2026-07-21-shop-scrape-raw-design.md`.
- Keep imports at top of file; avoid inline imports.

---

## File structure (new + modified)

- Create: `app/scripts/shop_scrape/http.py` — shared fetch/cache/retry/rate-limit.
- Create: `app/scripts/shop_scrape/woocommerce.py` — WooCommerce Store API pagination + normalization.
- Create: `app/scripts/shop_scrape/sitemap.py` — streaming sitemap reader (iterparse).
- Create: `app/scripts/shop_scrape/jsonld.py` — JSON-LD Product extraction from HTML.
- Create: `app/scripts/shop_scrape/shops.py` — shop definitions + per-shop scrape functions.
- Create: `app/scripts/scrape-cigar-shops.py` — CLI entrypoint; writes output JSON files.
- Create: `app/scripts/test_shop_scrape_unittest.py` — stdlib `unittest` unit tests for parsers/normalizers.
- (Optional) Modify: `.gitignore` only if `app/scripts/output/` is not already ignored for raw artifacts.

## Task 1: Shared HTTP layer (cache + rate limit + retry)

**Files:**
- Create: `app/scripts/shop_scrape/http.py`
- Create: `app/scripts/shop_scrape/__init__.py`

**Interfaces:**
- Produces:
  - `class HttpClient:`
    - `def get_text(self, url: str, *, headers: dict[str, str] | None = None) -> str`
    - `def get_json(self, url: str, *, headers: dict[str, str] | None = None) -> object`
  - `def iso_utc_now() -> str`

- [ ] **Step 1: Write failing tests (cache key + basic fetch wrappers)**

```python
import json
import unittest

from shop_scrape.http import _cache_key, iso_utc_now


class TestHttpHelpers(unittest.TestCase):
    def test_cache_key_is_stable(self):
        self.assertEqual(_cache_key("https://x.test/a?b=1"), _cache_key("https://x.test/a?b=1"))

    def test_iso_utc_now_is_isoish(self):
        s = iso_utc_now()
        self.assertTrue(s.endswith("Z"))
        self.assertIn("T", s)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest app/scripts/test_shop_scrape_unittest.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'shop_scrape'` (or missing `_cache_key`).

- [ ] **Step 3: Implement `shop_scrape/http.py`**

```python
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class HttpConfig:
    user_agent: str
    cache_dir: Path
    cache_ttl_s: int
    per_host_delay_s: float
    timeout_s: int
    max_retries: int


class HttpClient:
    def __init__(self, config: HttpConfig):
        self._cfg = config
        self._last_by_host: dict[str, float] = {}
        self._cfg.cache_dir.mkdir(parents=True, exist_ok=True)

    def _throttle(self, url: str) -> None:
        host = urllib.parse.urlparse(url).netloc
        last = self._last_by_host.get(host)
        if last is None:
            self._last_by_host[host] = time.time()
            return
        wait = self._cfg.per_host_delay_s - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
        self._last_by_host[host] = time.time()

    def _cache_path(self, url: str) -> Path:
        return self._cfg.cache_dir / f"{_cache_key(url)}.json"

    def _read_cache(self, url: str) -> bytes | None:
        p = self._cache_path(url)
        if not p.exists():
            return None
        try:
            st = p.stat()
        except OSError:
            return None
        if self._cfg.cache_ttl_s > 0 and (time.time() - st.st_mtime) > self._cfg.cache_ttl_s:
            return None
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
            return (obj.get("body") or "").encode("utf-8")
        except Exception:
            return None

    def _write_cache(self, url: str, body_text: str) -> None:
        p = self._cache_path(url)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps({"url": url, "body": body_text}, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, p)

    def get_text(self, url: str, *, headers: dict[str, str] | None = None) -> str:
        cached = self._read_cache(url)
        if cached is not None:
            return cached.decode("utf-8", "replace")

        merged_headers = {"User-Agent": self._cfg.user_agent, "Accept": "*/*"}
        if headers:
            merged_headers.update(headers)

        last_err: Exception | None = None
        for attempt in range(self._cfg.max_retries + 1):
            try:
                self._throttle(url)
                req = urllib.request.Request(url, headers=merged_headers)
                with urllib.request.urlopen(req, timeout=self._cfg.timeout_s) as resp:
                    raw = resp.read()
                text = raw.decode("utf-8", "replace")
                self._write_cache(url, text)
                return text
            except urllib.error.HTTPError as e:
                last_err = e
                if e.code in (429, 500, 502, 503, 504) and attempt < self._cfg.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise
            except Exception as e:
                last_err = e
                if attempt < self._cfg.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise
        raise RuntimeError(f"unreachable: {last_err!r}")

    def get_json(self, url: str, *, headers: dict[str, str] | None = None) -> object:
        text = self.get_text(url, headers=headers)
        return json.loads(text)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest app/scripts/test_shop_scrape_unittest.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/scripts/shop_scrape/__init__.py app/scripts/shop_scrape/http.py app/scripts/test_shop_scrape_unittest.py
git commit -m "feat: shared http client with cache and retries"
```

## Task 2: WooCommerce Store API scrapers (HR + cigarsdaily)

**Files:**
- Create: `app/scripts/shop_scrape/woocommerce.py`
- Create: `app/scripts/shop_scrape/shops.py` (partial)
- Modify: `app/scripts/test_shop_scrape_unittest.py` (add parser tests)

**Interfaces:**
- Consumes: `HttpClient`
- Produces:
  - `def wc_iter_products(client: HttpClient, base_url: str, *, per_page: int = 100, max_pages: int = 200) -> list[dict]`
  - `def scrape_humidor_hr(client: HttpClient, *, limit: int | None) -> dict`
  - `def scrape_havana_hr(client: HttpClient, *, limit: int | None) -> dict`
  - `def scrape_cigarsdaily_us(client: HttpClient, *, limit: int | None) -> dict`

- [ ] **Step 1: Add failing test for WC normalization**

```python
from shop_scrape.woocommerce import wc_price_to_amount


class TestWooCommerce(unittest.TestCase):
    def test_wc_price_to_amount(self):
        prices = {"price": "1200", "currency_minor_unit": 2}
        self.assertEqual(wc_price_to_amount(prices), 12.0)
```

- [ ] **Step 2: Implement `woocommerce.py`**

```python
from __future__ import annotations

from typing import Any

from shop_scrape.http import HttpClient


def wc_price_to_amount(prices: dict[str, Any]) -> float | None:
    raw = prices.get("price")
    if raw is None:
        return None
    minor = int(prices.get("currency_minor_unit", 2))
    try:
        return int(raw) / (10 ** minor)
    except Exception:
        return None


def wc_iter_products(
    client: HttpClient, base_url: str, *, per_page: int = 100, max_pages: int = 200
) -> list[dict]:
    out: list[dict] = []
    for page in range(1, max_pages + 1):
        url = f"{base_url}/wp-json/wc/store/products?per_page={per_page}&page={page}"
        batch = client.get_json(url)
        if not isinstance(batch, list) or not batch:
            break
        out.extend(batch)
    return out
```

- [ ] **Step 3: Implement per-shop functions in `shops.py` (WC-based)**

Include logic:
  - set shop metadata, `scrapedAt`, `currency` from API response,
  - map each product into the standardized `items[]` shape,
  - apply `--limit` by slicing after full normalization.

- [ ] **Step 4: Run unit tests**

Run: `python3 -m unittest app/scripts/test_shop_scrape_unittest.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/scripts/shop_scrape/woocommerce.py app/scripts/shop_scrape/shops.py app/scripts/test_shop_scrape_unittest.py
git commit -m "feat: wooCommerce store API scrapers for HR and cigarsdaily"
```

## Task 3: Sitemap reader + JSON-LD extraction (holts + cigarworld)

**Files:**
- Create: `app/scripts/shop_scrape/sitemap.py`
- Create: `app/scripts/shop_scrape/jsonld.py`
- Modify: `app/scripts/shop_scrape/shops.py` (add holts/cigarworld)
- Modify: `app/scripts/test_shop_scrape_unittest.py`

**Interfaces:**
- Consumes: `HttpClient`
- Produces:
  - `def iter_sitemap_locs(xml_text: str) -> list[str]` (small) and/or
  - `def iter_sitemap_locs_stream(path: str) -> list[str]` (for large local file) OR `def iter_sitemap_locs_url(client, sitemap_url) -> iterator[str]`
  - `def extract_jsonld_products(html: str) -> list[dict]`

- [ ] **Step 1: Add failing tests (sitemap + jsonld)**

```python
from shop_scrape.jsonld import extract_jsonld_products
from shop_scrape.sitemap import iter_sitemap_locs


class TestSitemapAndJsonLd(unittest.TestCase):
    def test_iter_sitemap_locs(self):
        xml = \"\"\"<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/a</loc></url>
  <url><loc>https://example.com/b</loc></url>
</urlset>\"\"\"
        self.assertEqual(iter_sitemap_locs(xml), ["https://example.com/a", "https://example.com/b"])

    def test_extract_jsonld_products(self):
        html = \"\"\"<html><head>
<script type="application/ld+json">{\"@type\":\"Product\",\"name\":\"X\",\"offers\":{\"price\":\"12.00\",\"priceCurrency\":\"EUR\",\"availability\":\"http://schema.org/InStock\"}}</script>
</head></html>\"\"\"
        ps = extract_jsonld_products(html)
        self.assertEqual(ps[0]["name"], "X")
```

- [ ] **Step 2: Implement `sitemap.py` using `xml.etree.ElementTree`**

Use namespace-aware parsing; for big sitemap files prefer `iterparse` over `fromstring` when reading from disk/URL.

- [ ] **Step 3: Implement `jsonld.py` (robust extraction)**

Implement:
  - find all `<script type="application/ld+json">...</script>` blocks,
  - parse JSON that may be object/array,
  - return Product objects (including nested `@graph`).

- [ ] **Step 4: Implement `holts_us` and `cigarworld_eu` shop scrapers in `shops.py`**

Approach:
  - fetch sitemap index → filter relevant URLs,
  - for each candidate product URL (bounded by `--limit`), fetch HTML and extract JSON-LD Product,
  - normalize into raw `items[]`.

- [ ] **Step 5: Run unit tests**

Run: `python3 -m unittest app/scripts/test_shop_scrape_unittest.py -v`  
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add app/scripts/shop_scrape/sitemap.py app/scripts/shop_scrape/jsonld.py app/scripts/shop_scrape/shops.py app/scripts/test_shop_scrape_unittest.py
git commit -m "feat: sitemap and json-ld scrapers for holts and cigarworld"
```

## Task 4: CLI entrypoint and end-to-end verification

**Files:**
- Create: `app/scripts/scrape-cigar-shops.py`
- Modify: `README.md` (optional: add a short “Raw cigar shop export” snippet)

**Interfaces:**
- Consumes: `HttpClient`, `shops.py` functions
- Produces:
  - `python app/scripts/scrape-cigar-shops.py --shop all --limit 25`
  - JSON outputs in `app/scripts/output/`

- [ ] **Step 1: Implement CLI**

CLI flags:
  - `--shop {all,humidor_hr,havana_hr,cigarsdaily_us,holts_us,cigarworld_eu}`
  - `--limit N`
  - `--cache-ttl-s N`
  - `--no-cache`
  - `--per-host-delay-s FLOAT`
  - `--out-dir PATH` (default `app/scripts/output`)

- [ ] **Step 2: Manual verification run (small limits)**

Run:
  - `python3 app/scripts/scrape-cigar-shops.py --shop humidor_hr --limit 10`
  - `python3 app/scripts/scrape-cigar-shops.py --shop havana_hr --limit 10`
  - `python3 app/scripts/scrape-cigar-shops.py --shop cigarsdaily_us --limit 10`
  - `python3 app/scripts/scrape-cigar-shops.py --shop holts_us --limit 5`
  - `python3 app/scripts/scrape-cigar-shops.py --shop cigarworld_eu --limit 5`

Expected:
  - each produces a JSON with top-level keys `shop`, `scrapedAt`, `currency`, `items`,
  - `items` length equals `limit` (or less if shop has fewer items under chosen filters),
  - no uncaught exceptions.

- [ ] **Step 3: Commit**

```bash
git add app/scripts/scrape-cigar-shops.py app/scripts/shop_scrape/shops.py README.md
git commit -m "feat: export raw cigar shop catalogs CLI"
```

## Task 5: PR hygiene

- [ ] Ensure outputs under `app/scripts/output/` are not committed.
- [ ] Run `git status` clean.
- [ ] Update the PR description with brief run instructions and sample commands.

