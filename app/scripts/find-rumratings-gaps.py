# -*- coding: utf-8 -*-
"""Shortlist RumRatings bottles we lack, from already-discovered listing links."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rumratings_shared import BASE, OUT_DIR, best_match, name_from_detail_url  # noqa: E402

RUMS = Path(__file__).resolve().parent.parent / "src" / "data" / "rums.json"
PROBE = OUT_DIR / "_probe_rr"
RAW = OUT_DIR / "rumratings_raw.json"
OUT = OUT_DIR / "rumratings_gap_candidates.json"


def main() -> None:
    catalog = json.loads(RUMS.read_text("utf-8"))
    have_urls = {r["url"].rstrip("/") for r in json.loads(RAW.read_text("utf-8"))} if RAW.exists() else set()

    urls: set[str] = set()
    for f in PROBE.glob("list-*.html"):
        html = f.read_text("utf-8")
        for href in re.findall(r'href=["\']([^"\']*/rum/\d+-[^"\']+)["\']', html):
            if href.startswith("http"):
                urls.add(href.rstrip("/"))
            else:
                urls.add(f"{BASE}{href}".rstrip("/"))

    # Featured ultra-high from homepage (allowed path).
    urls.update(
        [
            f"{BASE}/rum/17880-planteray-2004-barbados-collection-foundations-20-year",
            f"{BASE}/rum/18027-planteray-1999-trinidad-prestige-cellar-25-year",
            f"{BASE}/rum/18886-planteray-2001-mlc-foundation-23-year",
            f"{BASE}/rum/20944-pere-labat-revelation",
            f"{BASE}/rum/21083-plantation-jamaica-selection-bar-1802-1998-23-year",
            f"{BASE}/rum/21084-s-b-s-hampden-jamaica-dok-px-cask-matured-rombo-edition-dok-2018-2-year",
        ]
    )

    gaps = []
    for url in sorted(urls):
        if url in have_urls:
            continue
        name = name_from_detail_url(url)
        hit, score = best_match(name, catalog, floor=0.70)
        if hit:
            continue
        gaps.append({"url": url, "nameGuess": name, "bestCatalogScore": round(score, 3)})

    OUT.write_text(json.dumps(gaps, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"{len(gaps)} gap candidates (not in catalogue at floor 0.70)")
    for g in gaps:
        print(f"  {g['bestCatalogScore']:.2f}  {g['nameGuess']}  {g['url']}")


if __name__ == "__main__":
    main()
