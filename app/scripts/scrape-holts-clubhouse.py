#!/usr/bin/env python3
"""Scrape Holt's Clubhouse editorial (pairings + cigar-101) into a local corpus.

Does NOT scrape Magento product listings (/all-cigar-brands/).
Output: ../../01_work/output/holts-clubhouse/ — **git-ignored, stays local.**

The scraped text is Holt's copyrighted editorial, not ours: it is a reading
corpus for research only. Never commit the output, never redistribute it, and
never copy its wording into app content — cite the source instead
(app/src/data/clubSources.json). See NOTICE.md.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "01_work" / "output" / "holts-clubhouse"
SEED_URLS = [
    # Pairings
    "https://www.holts.com/clubhouse/pairings/cognac-and-cigars",
    "https://www.holts.com/clubhouse/pairings/bourbon-and-cigars",
    "https://www.holts.com/clubhouse/pairings/scotch-and-cigar-pairings",
    "https://www.holts.com/clubhouse/pairings/whiskey-and-cigars",
    "https://www.holts.com/clubhouse/pairings/rum-cigar-pairing",
    "https://www.holts.com/clubhouse/pairings/port-wine-and-cigars",
    "https://www.holts.com/clubhouse/pairings/cigars-and-after-dinner-drinks",
    "https://www.holts.com/clubhouse/pairings/arturo-fuente-drink-pairings",
    "https://www.holts.com/clubhouse/pairings/laphroaig-and-cigars",
    # Cigar 101
    "https://www.holts.com/clubhouse/cigar-101/relative-humidity",
    "https://www.holts.com/clubhouse/cigar-101/cigar-tunneling",
    "https://www.holts.com/clubhouse/cigar-101/cigar-burns-unevenly",
    "https://www.holts.com/clubhouse/cigar-101/how-to-get-an-even-burn-on-a-cigar",
    "https://www.holts.com/clubhouse/cigar-101/fixing-common-cigar-problems",
    "https://www.holts.com/clubhouse/cigar-101/how-to-fix-hard-draw-cigar",
    "https://www.holts.com/clubhouse/cigar-101/cigar-will-not-stay-lit",
    "https://www.holts.com/clubhouse/cigar-101/cigar-gets-soft-while-smoking",
]

INDEX_URLS = [
    "https://www.holts.com/clubhouse/pairings",
    "https://www.holts.com/clubhouse/cigar-101",
]

UA = "cigar-pairing-research/1.0 (+local corpus; educational)"


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip = 0
        self._parts: list[str] = []
        self.title = ""
        self._in_title = False
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg", "nav", "footer", "header"}:
            self._skip += 1
        if tag == "title":
            self._in_title = True
        if tag == "a":
            href = dict(attrs).get("href") or ""
            if "/clubhouse/" in href:
                self.links.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg", "nav", "footer", "header"}:
            self._skip = max(0, self._skip - 1)
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        t = data.strip()
        if not t:
            return
        if self._in_title and not self.title:
            self.title = t
        self._parts.append(t)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8", errors="replace")


def abs_url(href: str) -> str | None:
    if href.startswith("//"):
        href = "https:" + href
    if href.startswith("/"):
        href = "https://www.holts.com" + href
    if not href.startswith("https://www.holts.com/clubhouse/"):
        return None
    if "/all-cigar-brands/" in href or "/catalog/" in href:
        return None
    href = href.split("?")[0].split("#")[0]
    # keep pairings + cigar-101 + how-to style paths
    if not re.search(r"/clubhouse/(pairings|cigar-101|how-to|humidor)/", href):
        if href.rstrip("/").endswith("/clubhouse/pairings") or href.rstrip("/").endswith(
            "/clubhouse/cigar-101"
        ):
            return href
        if "/clubhouse/pairings/" in href or "/clubhouse/cigar-101/" in href:
            return href
        return None
    return href


def parse_page(url: str, html: str) -> dict:
    p = _TextExtractor()
    p.feed(html)
    text = re.sub(r"\s+", " ", " ".join(p._parts)).strip()
    # Trim Magento chrome noise if present
    for marker in ("Shop Cigars", "Customer Service", "Subscribe"):
        if marker in text and len(text) > 800:
            # keep body; soft trim of repeated chrome at ends only
            break
    links = []
    for h in p.links:
        a = abs_url(h)
        if a and a not in links:
            links.append(a)
    section = "pairings" if "/pairings/" in url else "cigar-101" if "/cigar-101/" in url else "other"
    return {
        "url": url,
        "title": p.title or url.rsplit("/", 1)[-1],
        "section": section,
        "text": text[:50000],
        "charCount": len(text),
        "outboundClubhouse": links[:80],
    }


def discover_from_indexes() -> list[str]:
    found: list[str] = []
    for idx in INDEX_URLS:
        try:
            html = fetch(idx)
            page = parse_page(idx, html)
            for u in page["outboundClubhouse"]:
                if u not in found and u not in INDEX_URLS:
                    found.append(u)
            time.sleep(0.6)
        except Exception as e:  # noqa: BLE001
            print(f"index fail {idx}: {e}")
    return found


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    urls = list(dict.fromkeys(SEED_URLS + discover_from_indexes()))
    articles: list[dict] = []
    errors: list[dict] = []
    for i, url in enumerate(urls):
        try:
            html = fetch(url)
            art = parse_page(url, html)
            articles.append(art)
            slug = re.sub(r"[^a-z0-9-]+", "-", url.rstrip("/").rsplit("/", 1)[-1])[:80]
            (OUT / f"{art['section']}_{slug}.json").write_text(
                json.dumps(art, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"[{i+1}/{len(urls)}] OK {url} ({art['charCount']} chars)")
        except (urllib.error.URLError, TimeoutError, Exception) as e:  # noqa: BLE001
            errors.append({"url": url, "error": str(e)})
            print(f"[{i+1}/{len(urls)}] FAIL {url}: {e}")
        time.sleep(0.7)

    index = {
        "source": "holts.com/clubhouse",
        "scrapedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "articleCount": len(articles),
        "errorCount": len(errors),
        "articles": [
            {"url": a["url"], "title": a["title"], "section": a["section"], "charCount": a["charCount"]}
            for a in articles
        ],
        "errors": errors,
    }
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    # Compact corpus for gap analysis
    (OUT / "corpus.json").write_text(
        json.dumps(articles, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote {len(articles)} articles to {OUT}")


if __name__ == "__main__":
    main()
