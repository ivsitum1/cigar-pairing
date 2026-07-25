#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Famous Smoke flavor scrape via Playwright.

NOTE (2026-07): Search/brand listing pages usually show a Client Challenge
CAPTCHA. Prefer Exa search dumps → ingest-famous-exa.py when possible.
Direct product URLs sometimes work over plain HTTP; Playwright may still
hit CAPTCHA in headless mode — try --headed and solve once (storage state).

Merges into existing cw_famous_flavor_raw.json (famous field), then:
  python scripts/convert-cw-famous-raw.py
  python scripts/merge-flavor-enrichment.py --batch 2

  python scripts/scrape-famous-playwright.py --limit 5 --headed
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE / "output" / "flavor_enrich_worklist.json"
RAW = HERE / "output" / "cw_famous_flavor_raw.json"
STATE = HERE / "output" / "famous_storage.json"
DATA = HERE.parent / "src" / "data"


def dismiss_walls(page) -> None:
    for sel in (
        'button:has-text("Yes, I am")',
        'button:has-text("I am of legal age")',
        'button:has-text("Enter")',
        'button:has-text("I Agree")',
        'button:has-text("Accept")',
        'button:has-text("Accept All")',
        "#onetrust-accept-btn-handler",
        '[aria-label="Close"]',
    ):
        try:
            page.locator(sel).first.click(timeout=2000)
            page.wait_for_timeout(300)
        except Exception:
            pass


def is_blocked(page) -> bool:
    try:
        t = page.content()[:4000].lower()
    except Exception:
        return False
    return any(
        x in t
        for x in (
            "client challenge",
            "cf-browser-verification",
            "attention required",
            "just a moment",
            "checking your browser",
        )
    )


def extract_product(page) -> dict:
    facts: dict[str, str] = {}
    try:
        rows = page.evaluate(
            """() => {
              const out = [];
              document.querySelectorAll('tr').forEach(tr => {
                const cells = [...tr.querySelectorAll('th,td')].map(c => c.innerText.trim());
                if (cells.length >= 2) out.push([cells[0], cells.slice(1).join(' ')]);
              });
              document.querySelectorAll('li,div,span,p').forEach(el => {
                const t = (el.innerText || '').trim();
                if (!t || t.length > 120) return;
                const m = t.match(/^(Wrapper|Binder|Filler|Strength|Shape|Origin|Country|Size)\\s*[:|]\\s*(.+)$/i);
                if (m) out.push([m[1], m[2]]);
              });
              return out;
            }"""
        )
        for k, v in rows or []:
            key = re.sub(r"\s+", " ", (k or "")).strip().lower()
            val = re.sub(r"\s+", " ", (v or "")).strip()
            if key and val and len(val) < 160:
                facts[key] = val
    except Exception:
        pass

    desc = ""
    try:
        desc = page.evaluate(
            """() => {
              const sels = [
                '[itemprop="description"]',
                '.product-description',
                '#product-description',
                '.description',
                '#Description',
                '.tab-content',
              ];
              for (const s of sels) {
                const el = document.querySelector(s);
                if (el && el.innerText && el.innerText.trim().length > 60)
                  return el.innerText.trim().slice(0, 2000);
              }
              const body = document.body.innerText || '';
              for (const label of ['Product Description', 'About This Cigar', 'Tasting Notes']) {
                const i = body.indexOf(label);
                if (i >= 0) return body.slice(i, i + 900).trim();
              }
              return '';
            }"""
        ) or ""
    except Exception:
        pass

    title = ""
    try:
        title = page.locator("h1").first.inner_text(timeout=3000).strip()
    except Exception:
        pass

    return {
        "title": title,
        "facts": facts,
        "description": re.sub(r"\s+", " ", desc).strip()[:2000],
        "ok": bool(facts or (desc and len(desc) > 60)),
    }


def pick_product_url(page, brand: str, line: str) -> str | None:
    hrefs = page.evaluate(
        """() => [...document.querySelectorAll('a[href]')]
            .map(a => a.href)
            .filter(Boolean)"""
    ) or []
    brand_l = (brand or "").lower()
    line_l = (line or "").lower()
    products: list[str] = []
    for h in hrefs:
        low = h.lower()
        if "famous-smoke.com" not in low:
            continue
        if any(x in low for x in ("/cigars?", "/search", "/customer", "/cart", "/account", "/login")):
            continue
        # product-ish paths
        if not (re.search(r"/\d{4,}", low) or low.endswith(".html") or "/cigar/" in low or "-cigar" in low):
            continue
        products.append(h)
    if not products:
        return None
    # prefer brand/line in URL
    scored = []
    for h in products:
        low = h.lower()
        score = 0
        if brand_l and brand_l.replace(" ", "-") in low.replace(" ", "-"):
            score += 2
        if line_l and any(tok in low for tok in line_l.replace("/", " ").split() if len(tok) > 3):
            score += 1
        scored.append((score, h))
    scored.sort(key=lambda x: -x[0])
    return scored[0][1]


def scrape_one(page, brand: str, line: str) -> dict:
    q = f"{brand} {line}".strip()
    furl = f"https://www.famous-smoke.com/cigars?search={urllib.parse.quote_plus(q)}"
    out: dict = {
        "search_url": furl,
        "product_url": None,
        "facts": {},
        "description": "",
        "title": "",
        "ok": False,
        "blocked": False,
    }
    page.goto(furl, wait_until="domcontentloaded", timeout=60000)
    dismiss_walls(page)
    page.wait_for_timeout(1200)
    if is_blocked(page):
        out["blocked"] = True
        out["error"] = "bot challenge"
        return out
    product_url = pick_product_url(page, brand, line)
    out["product_url"] = product_url
    if not product_url:
        out["error"] = "no product link"
        return out
    page.goto(product_url, wait_until="domcontentloaded", timeout=60000)
    dismiss_walls(page)
    page.wait_for_timeout(900)
    if is_blocked(page):
        out["blocked"] = True
        out["error"] = "bot challenge on product"
        return out
    extracted = extract_product(page)
    out.update(extracted)
    return out


def load_work(limit: int) -> list[dict]:
    if WORK.exists():
        work = json.loads(WORK.read_text(encoding="utf-8"))
    else:
        cigars = json.loads((DATA / "cigars.json").read_text(encoding="utf-8"))
        work = [
            {"id": c["id"], "brand": c.get("brand"), "line": c.get("line")}
            for c in cigars
            if c.get("profileEstimated") is True
        ]
    # Prefer rows already in CW raw (merge targets), else worklist
    if RAW.exists():
        ids = {r["id"] for r in json.loads(RAW.read_text(encoding="utf-8"))}
        work = [w for w in work if w["id"] in ids] or work
    return work[:limit]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--sleep", type=float, default=1.8)
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--channel", default="chrome", help="chrome|msedge|'' for bundled chromium")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    targets = load_work(args.limit)
    prior: dict[str, dict] = {}
    if RAW.exists():
        for r in json.loads(RAW.read_text(encoding="utf-8")):
            prior[r["id"]] = r

    with sync_playwright() as p:
        launch_kwargs: dict = {"headless": not args.headed}
        if args.channel:
            launch_kwargs["channel"] = args.channel
        try:
            browser = p.chromium.launch(**launch_kwargs)
        except Exception:
            # fallback bundled chromium
            launch_kwargs.pop("channel", None)
            browser = p.chromium.launch(headless=not args.headed)

        ctx_kwargs = {
            "locale": "en-US",
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "viewport": {"width": 1280, "height": 900},
        }
        if STATE.exists():
            ctx_kwargs["storage_state"] = str(STATE)
        context = browser.new_context(**ctx_kwargs)
        page = context.new_page()

        page.goto("https://www.famous-smoke.com/", wait_until="domcontentloaded", timeout=60000)
        dismiss_walls(page)
        if is_blocked(page):
            print("WARN: homepage still shows challenge — try --headed")
        try:
            context.storage_state(path=str(STATE))
        except Exception:
            pass

        fam_ok = 0
        blocked_n = 0
        for i, row in enumerate(targets, 1):
            entry = prior.get(row["id"]) or {
                "id": row["id"],
                "brand": row.get("brand"),
                "line": row.get("line"),
                "cw_url": row.get("cw_url"),
                "cigarworld": {"ok": False},
                "famous": {"ok": False},
            }
            if (entry.get("famous") or {}).get("ok"):
                print(f"[{i}/{len(targets)}] skip OK {row['id']}")
                prior[row["id"]] = entry
                fam_ok += 1
                continue

            print(f"[{i}/{len(targets)}] Famous {row['id']} ({row.get('brand')} {row.get('line')})")
            try:
                fam = scrape_one(page, row.get("brand") or "", row.get("line") or "")
            except Exception as e:
                fam = {"ok": False, "error": str(e)[:240]}
            entry["famous"] = fam
            entry["brand"] = entry.get("brand") or row.get("brand")
            entry["line"] = entry.get("line") or row.get("line")
            prior[row["id"]] = entry
            if fam.get("ok"):
                fam_ok += 1
                print(f"  ok facts={list((fam.get('facts') or {}))[:4]} title={(fam.get('title') or '')[:50]}")
            elif fam.get("blocked"):
                blocked_n += 1
                print("  blocked")
                if blocked_n >= 3:
                    print("too many blocks — stopping")
                    break
            else:
                print(f"  miss {fam.get('error')}")

            if i % 5 == 0:
                try:
                    context.storage_state(path=str(STATE))
                except Exception:
                    pass
                RAW.write_text(
                    json.dumps(list(prior.values()), ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            time.sleep(args.sleep)

        browser.close()

    # Keep prior order: write all prior rows (CW scrape) with updated famous
    out_rows = list(prior.values())
    RAW.write_text(json.dumps(out_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"done targets={len(targets)} famous_ok={fam_ok} blocked={blocked_n} -> {RAW}")


if __name__ == "__main__":
    main()
