#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick HTTP scrape: CigarWorld product pages + Famous Smoke search→first product.

  python scripts/scrape-cw-famous-quick.py --limit 40
  python scripts/scrape-cw-famous-quick.py --limit 200
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
WORK = HERE / "output" / "flavor_enrich_worklist.json"
OUT = HERE / "output" / "cw_famous_flavor_raw.json"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


def fetch(url: str, timeout: int = 25, retries: int = 4) -> str:
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": UA,
                    "Accept-Language": "en",
                    "Accept": "text/html,application/xhtml+xml",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 503) and attempt < retries - 1:
                time.sleep(8 * (attempt + 1))
                continue
            raise
        except Exception as e:
            last = e
            if attempt < retries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            raise
    raise last or RuntimeError("fetch failed")


def strip_tags(s: str) -> str:
    s = re.sub(r"<script[^>]*>.*?</script>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<style[^>]*>.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def parse_cw(html: str) -> dict:
    facts: dict[str, str] = {}
    # Structured product facts
    for name, val in re.findall(
        r'VariantInfo-itemName">\s*([^<]+?)\s*</div>\s*'
        r'<div class="[^"]*VariantInfo-itemValue[^"]*">\s*(.*?)\s*</div>',
        html,
        re.S | re.I,
    ):
        key = strip_tags(name).lower()
        value = strip_tags(val)
        if key and value and len(value) < 120:
            facts[key] = value

    aroma_names = [
        "Wood", "Pepper", "Grass", "Fruit", "Cream", "Sweet", "Nut",
        "Chocolate", "Coffee", "Toast", "Leather", "Soil",
    ]
    props_names = [
        "Price/Value", "Production Quality", "Strength", "Smoke Volume",
        "draw resistance", "Combustion behavior", "Aroma Diversity", "Aroma Strength",
    ]
    aromas: dict[str, int] = {}
    props: dict[str, int] = {}
    # First product canvas (page hero), not review canvases further down if possible —
    # take the first aromaimg with both attributes.
    m = re.search(
        r'<canvas[^>]*class="[^"]*aromaimg[^"]*"[^>]*data-content="(\d+)"[^>]*data-props="(\d+)"',
        html,
        re.I,
    )
    if not m:
        m = re.search(
            r'<canvas[^>]*data-content="(\d+)"[^>]*data-props="(\d+)"[^>]*class="[^"]*aromaimg',
            html,
            re.I,
        )
    if m:
        content, prop = m.group(1), m.group(2)
        for i, name in enumerate(aroma_names):
            if i < len(content) and content[i].isdigit():
                aromas[name.lower()] = int(content[i])
        for i, name in enumerate(props_names):
            if i < len(prop) and prop[i].isdigit():
                props[name.lower()] = int(prop[i])

    # Top aromas (>=5) as flavour phrase for tag extraction
    top = sorted(aromas.items(), key=lambda kv: -kv[1])
    flavour_bits = [f"{n} {v}" for n, v in top if v >= 5][:8]

    title = ""
    hm = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    if hm:
        title = strip_tags(hm.group(1))

    ok = bool(facts.get("wrapper variety") or facts.get("wrapper origin") or aromas)
    return {
        "title": title,
        "facts": facts,
        "aroma": aromas,
        "props": props,
        "description": "",
        "flavour_bits": flavour_bits,
        "ok": ok,
    }


def parse_famous_search(html: str, brand: str, line: str) -> dict:
    # Famous Smoke often serves a bot challenge to non-browser clients.
    if re.search(r"client challenge|cf-browser-verification|attention required", html, re.I):
        return {
            "search_hits": 0,
            "product_url": None,
            "facts": {},
            "description": "",
            "ok": False,
            "blocked": True,
        }
    hrefs = re.findall(r'href="(https://www\.famous-smoke\.com/[^"#?]+)"', html, re.I)
    hrefs += re.findall(r'href="(/[^"#?]+\.html)"', html, re.I)
    products: list[str] = []
    for h in hrefs:
        if h.startswith("/"):
            h = "https://www.famous-smoke.com" + h
        low = h.lower()
        if any(x in low for x in ("/cigars?", "/search", "/customer", "/cart", "/account")):
            continue
        if "/cigar" in low or re.search(r"/\d{5,}", low) or low.endswith(".html"):
            if h not in products:
                products.append(h)
    product_url = products[0] if products else None
    out: dict = {
        "search_hits": len(products),
        "product_url": product_url,
        "facts": {},
        "description": "",
        "ok": False,
        "blocked": False,
    }
    if not product_url:
        return out
    try:
        ph = fetch(product_url)
    except Exception as e:
        out["error"] = str(e)[:200]
        return out
    if re.search(r"client challenge|cf-browser-verification", ph, re.I):
        out["blocked"] = True
        return out
    text = strip_tags(ph)
    facts: dict[str, str] = {}
    for label in ("Wrapper", "Binder", "Filler", "Strength", "Shape", "Origin", "Country"):
        mm = re.search(label + r"\s*[:|]?\s*([A-Za-z0-9 /,\-]{2,60})", text, re.I)
        if mm:
            facts[label.lower()] = mm.group(1).strip()
    desc = ""
    for pat in (
        r"Product Description(.{80,900})",
        r"About This Cigar(.{80,900})",
        r"Tasting Notes(.{40,500})",
    ):
        mm = re.search(pat, text, re.I)
        if mm:
            desc = mm.group(1).strip()[:1500]
            break
    out["facts"] = facts
    out["description"] = desc
    out["title"] = ""
    tm = re.search(r"<h1[^>]*>(.*?)</h1>", ph, re.S | re.I)
    if tm:
        out["title"] = strip_tags(tm.group(1))
    out["ok"] = bool(facts or desc)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--sleep", type=float, default=1.5)
    ap.add_argument("--famous-every", type=int, default=3, help="also hit Famous Smoke every Nth row (0=skip)")
    ap.add_argument("--resume", action="store_true", help="keep prior OK rows; retry failures")
    args = ap.parse_args()

    if WORK.exists():
        work = json.loads(WORK.read_text(encoding="utf-8"))
    else:
        # fallback: estimated with CW from cigars.json
        cigars = json.loads((DATA / "cigars.json").read_text(encoding="utf-8"))
        work = []
        for c in cigars:
            if c.get("profileEstimated") is not True:
                continue
            eu = ((c.get("regionLinks") or {}).get("EU") or {}).get("url") or ""
            if "cigarworld.de" not in eu:
                continue
            work.append({"id": c["id"], "brand": c.get("brand"), "line": c.get("line"), "cw_url": eu})
    work = [w for w in work if w.get("cw_url")][: args.limit]

    prior: dict[str, dict] = {}
    if args.resume and OUT.exists():
        for r in json.loads(OUT.read_text(encoding="utf-8")):
            prior[r["id"]] = r

    results: list[dict] = []
    for i, row in enumerate(work, 1):
        old = prior.get(row["id"])
        if old and (old.get("cigarworld") or {}).get("ok"):
            results.append(old)
            print(f"[{i}/{len(work)}] skip OK {row['id']}")
            continue

        entry = {
            "id": row["id"],
            "brand": row.get("brand"),
            "line": row.get("line"),
            "cw_url": row["cw_url"],
            "cigarworld": {"ok": False},
            "famous": (old or {}).get("famous") or {"ok": False},
        }
        print(f"[{i}/{len(work)}] CW {row['id']}")
        try:
            html = fetch(row["cw_url"])
            entry["cigarworld"] = parse_cw(html)
            entry["cigarworld"]["url"] = row["cw_url"]
        except Exception as e:
            entry["cigarworld"] = {"ok": False, "error": str(e)[:240], "url": row["cw_url"]}
            if "429" in str(e):
                print("  rate-limited — pausing 20s")
                time.sleep(20)

        if args.famous_every and i % args.famous_every == 0 and not (entry["famous"] or {}).get("ok"):
            q = urllib.parse.quote_plus(f"{row.get('brand') or ''} {row.get('line') or ''}".strip())
            furl = f"https://www.famous-smoke.com/cigars?search={q}"
            print(f"  Famous {q}")
            try:
                fhtml = fetch(furl)
                entry["famous"] = parse_famous_search(fhtml, row.get("brand") or "", row.get("line") or "")
                entry["famous"]["search_url"] = furl
            except Exception as e:
                entry["famous"] = {"ok": False, "error": str(e)[:240], "search_url": furl}
            time.sleep(args.sleep)

        results.append(entry)
        time.sleep(args.sleep)
        if i % 25 == 0:
            OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cw_ok = sum(1 for r in results if r["cigarworld"].get("ok"))
    fam_ok = sum(1 for r in results if r["famous"].get("ok"))
    print(f"done rows={len(results)} cw_ok={cw_ok} famous_ok={fam_ok} -> {OUT}")


if __name__ == "__main__":
    main()
