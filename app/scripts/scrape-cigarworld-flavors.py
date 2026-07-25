#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scrape CigarWorld product pages for wrapper / strength / description / flavours.

Reads app/scripts/output/flavor_enrich_worklist.json (entries with cw_url).
Writes app/scripts/output/cigarworld_flavor_raw.json.

  python scripts/scrape-cigarworld-flavors.py
  python scripts/scrape-cigarworld-flavors.py --limit 3   # probe
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKLIST = HERE / "output" / "flavor_enrich_worklist.json"
OUT = HERE / "output" / "cigarworld_flavor_raw.json"
STATE = HERE / "output" / "cigarworld_storage.json"

FACT_KEYS = (
    "wrapper",
    "binder",
    "filler",
    "length",
    "ring",
    "strength",
    "flavour",
    "flavor",
    "aroma",
    "origin",
    "wrapper origin",
    "binder origin",
    "filler origin",
    "fabrication",
    "deckblatt",
    "umblatt",
    "einlage",
    "stärke",
    "geschmack",
)


def dismiss_walls(page) -> None:
    for sel in (
        'button:has-text("Accept all")',
        'button:has-text("Alle akzeptieren")',
        'button:has-text("Agree")',
        'button:has-text("Zustimmen")',
        'button:has-text("I am of legal age")',
        'button:has-text("Ich bin volljährig")',
        '[data-testid="uc-accept-all-button"]',
        "#onetrust-accept-btn-handler",
    ):
        try:
            page.locator(sel).first.click(timeout=2500)
            page.wait_for_timeout(400)
        except Exception:
            pass


def extract_facts(page) -> dict:
    facts: dict[str, str] = {}
    # definition lists / tables
    try:
        rows = page.evaluate(
            """() => {
              const out = [];
              document.querySelectorAll('dt').forEach(dt => {
                const dd = dt.nextElementSibling;
                if (dd && dd.tagName === 'DD') {
                  out.push([dt.innerText.trim(), dd.innerText.trim()]);
                }
              });
              document.querySelectorAll('tr').forEach(tr => {
                const cells = [...tr.querySelectorAll('th,td')].map(c => c.innerText.trim());
                if (cells.length >= 2) out.push([cells[0], cells.slice(1).join(' ')]);
              });
              return out;
            }"""
        )
        for k, v in rows or []:
            key = re.sub(r"\s+", " ", (k or "")).strip().lower()
            val = re.sub(r"\s+", " ", (v or "")).strip()
            if not key or not val or len(val) > 400:
                continue
            if any(fk in key for fk in FACT_KEYS) or key in FACT_KEYS:
                facts[key] = val
    except Exception:
        pass

    # meta / body description
    desc = ""
    try:
        desc = page.evaluate(
            """() => {
              const sels = [
                '[itemprop="description"]',
                '.product-description',
                '.product--description',
                '#description',
                'article .cms-element-text',
              ];
              for (const s of sels) {
                const el = document.querySelector(s);
                if (el && el.innerText && el.innerText.trim().length > 40)
                  return el.innerText.trim().slice(0, 2000);
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

    return {"title": title, "facts": facts, "description": desc}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    work = json.loads(WORKLIST.read_text(encoding="utf-8"))
    targets = [w for w in work if w.get("cw_url")]
    if args.limit:
        targets = targets[: args.limit]

    results: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            locale="en-GB",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
        )
        if STATE.exists():
            try:
                context = browser.new_context(
                    storage_state=str(STATE),
                    locale="en-GB",
                )
            except Exception:
                pass
        page = context.new_page()
        # warm-up + consent
        page.goto("https://www.cigarworld.de/en", wait_until="domcontentloaded", timeout=60000)
        dismiss_walls(page)
        try:
            context.storage_state(path=str(STATE))
        except Exception:
            pass

        for i, row in enumerate(targets, 1):
            url = row["cw_url"]
            print(f"[{i}/{len(targets)}] {row['id']}")
            entry = {
                "id": row["id"],
                "url": url,
                "ok": False,
                "error": None,
                "title": "",
                "facts": {},
                "description": "",
            }
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                dismiss_walls(page)
                page.wait_for_timeout(800)
                extracted = extract_facts(page)
                entry.update(extracted)
                entry["ok"] = bool(extracted.get("facts") or extracted.get("description"))
            except Exception as e:
                entry["error"] = str(e)[:300]
            results.append(entry)
            time.sleep(1.5)

        browser.close()

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ok = sum(1 for r in results if r["ok"])
    print(f"scraped={len(results)} ok={ok} -> {OUT}")


if __name__ == "__main__":
    main()
