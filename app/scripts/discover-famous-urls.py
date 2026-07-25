#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Discover Famous Smoke product URLs via DuckDuckGo (site search).

Search pages on famous-smoke.com are CAPTCHA-gated; direct product URLs
often work via Exa/HTTP. This script only discovers candidates.

  python scripts/discover-famous-urls.py --limit 40
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "output" / "cw_famous_flavor_raw.json"
OUT = HERE / "output" / "famous_url_candidates.json"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

SKIP = (
    "/cigars?",
    "/search",
    "/brands/",
    "/brand-",
    "/cigaradvisor",
    "/cart",
    "/customer",
    "/account",
    "/sale/",
    "/type/",
    "/country/",
    "/package/",
    "/strength/",
    "/wrapper-leaf/",
    "/best-cigars/",
)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def ddg(brand: str, line: str) -> list[str]:
    q = f'site:famous-smoke.com "{brand}" "{line}" cigars'
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q)
    try:
        html = fetch(url)
    except Exception:
        q2 = f"site:famous-smoke.com {brand} {line}"
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q2)
        html = fetch(url)
    hrefs = re.findall(r"uddg=([^&\"]+)", html)
    hrefs += re.findall(r'href="(https://www\.famous-smoke\.com/[^"]+)"', html)
    out: list[str] = []
    for h in hrefs:
        h = urllib.parse.unquote(h).split("&")[0]
        if "famous-smoke.com" not in h:
            continue
        low = h.lower()
        if any(x in low for x in SKIP):
            continue
        # product-ish: slug with cigars or long hyphenated path
        path = urllib.parse.urlparse(h).path.strip("/")
        if not path or "/" in path:
            # allow /foo/bar only if looks like product box url
            if not re.search(r"cigars?", path, re.I):
                continue
        if path.count("-") < 2 and "cigar" not in path.lower():
            continue
        if h not in out:
            out.append(h)
    return out[:8]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--sleep", type=float, default=1.2)
    args = ap.parse_args()

    rows = json.loads(RAW.read_text(encoding="utf-8"))
    # Prefer mainstream brands more likely stocked at Famous
    prefer = (
        "ashton",
        "arturo fuente",
        "padron",
        "oliva",
        "alec bradley",
        "aj fernandez",
        "my father",
        "drew estate",
        "rocky patel",
        "perdomo",
        "davidoff",
        "macanudo",
        "cao",
        "punch",
        "romeo",
        "montecristo",
        "cohiba",
        "hoyo",
        "partagas",
    )
    ranked = []
    for r in rows:
        b = (r.get("brand") or "").lower()
        score = 0
        for i, p in enumerate(prefer):
            if p in b:
                score = 100 - i
                break
        ranked.append((score, r))
    ranked.sort(key=lambda x: -x[0])
    targets = [r for s, r in ranked if s > 0][: args.limit]
    if len(targets) < args.limit:
        # fill with others
        have = {t["id"] for t in targets}
        for r in rows:
            if r["id"] in have:
                continue
            targets.append(r)
            if len(targets) >= args.limit:
                break

    results = []
    for i, r in enumerate(targets, 1):
        brand, line = r.get("brand") or "", r.get("line") or ""
        print(f"[{i}/{len(targets)}] {brand} {line}")
        try:
            urls = ddg(brand, line)
        except Exception as e:
            urls = []
            print("  err", e)
        print(f"  urls={len(urls)}" + (f" top={urls[0][:70]}" if urls else ""))
        results.append(
            {
                "id": r["id"],
                "brand": brand,
                "line": line,
                "urls": urls,
            }
        )
        time.sleep(args.sleep)

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with_urls = sum(1 for x in results if x["urls"])
    print(f"done {len(results)} with_urls={with_urls} -> {OUT}")


if __name__ == "__main__":
    main()
