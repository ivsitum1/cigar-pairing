#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scrape CigarWorld wrapper/binder/filler origins for catalog cigars.

Writes primarily to a local (non-OneDrive) backup dir to avoid sync overwrites,
and mirrors into app/scripts/output/.

  python scripts/scrape-leaf-origins.py --resume --sleep 0.8
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
LEAF_WORK = HERE / "output" / "leaf_origin_worklist.json"
OUT_REPO = HERE / "output" / "cw_famous_flavor_raw.json"
FLAT_REPO = HERE / "output" / "cigarworld_flavor_raw.json"

# Prefer local non-synced backup (Windows AppData)
BACKUP_DIR = Path(os.environ.get("LOCALAPPDATA", str(HERE / "output"))) / "cigar_leaf_scrape"
OUT_BAK = BACKUP_DIR / "cw_famous_flavor_raw.json"
FLAT_BAK = BACKUP_DIR / "cigarworld_flavor_raw.json"

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

    title = ""
    hm = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    if hm:
        title = strip_tags(hm.group(1))

    ok = bool(
        facts.get("wrapper variety")
        or facts.get("wrapper origin")
        or facts.get("binder origin")
        or facts.get("filler origin")
        or aromas
    )
    return {
        "title": title,
        "facts": facts,
        "aroma": aromas,
        "props": props,
        "description": "",
        "flavour_bits": [],
        "ok": ok,
    }


def load_json_list(path: Path) -> list:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def write_outputs(merged: dict[str, dict]) -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    rows = list(merged.values())
    payload = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    OUT_BAK.write_text(payload, encoding="utf-8")
    try:
        OUT_REPO.parent.mkdir(parents=True, exist_ok=True)
        OUT_REPO.write_text(payload, encoding="utf-8")
    except Exception as e:
        print(f"warn: could not write repo OUT: {e}")

    flat: dict[str, dict] = {}
    for path in (FLAT_BAK, FLAT_REPO):
        for row in load_json_list(path):
            if row.get("id") and row.get("ok"):
                flat[row["id"]] = row
    for r in rows:
        cw = r.get("cigarworld") or {}
        if not cw.get("ok"):
            continue
        flat[r["id"]] = {
            "id": r["id"],
            "url": cw.get("url") or r.get("cw_url"),
            "ok": True,
            "title": cw.get("title") or "",
            "facts": cw.get("facts") or {},
            "description": cw.get("description") or "",
            "sources": {"cigarworld": True, "famous": False},
        }
    flat_payload = json.dumps(list(flat.values()), ensure_ascii=False, indent=2) + "\n"
    FLAT_BAK.write_text(flat_payload, encoding="utf-8")
    try:
        FLAT_REPO.write_text(flat_payload, encoding="utf-8")
    except Exception as e:
        print(f"warn: could not write repo FLAT: {e}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="0 = all")
    ap.add_argument("--sleep", type=float, default=0.8)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--gaps-only", action="store_true")
    args = ap.parse_args()

    if LEAF_WORK.exists():
        work = json.loads(LEAF_WORK.read_text(encoding="utf-8"))
    else:
        cigars = json.loads((DATA / "cigars.json").read_text(encoding="utf-8"))
        work = []
        for c in cigars:
            eu = ((c.get("regionLinks") or {}).get("EU") or {}).get("url") or ""
            if "cigarworld.de" not in eu:
                continue
            work.append({"id": c["id"], "brand": c.get("brand"), "line": c.get("line"), "cw_url": eu})

    work = [w for w in work if w.get("cw_url")]
    if args.gaps_only:
        work = [
            w
            for w in work
            if not (
                w.get("has_wrapper_origin")
                and w.get("has_binder_origin")
                and w.get("has_filler_origin")
            )
        ]
    if args.limit and args.limit > 0:
        work = work[: args.limit]

    prior: dict[str, dict] = {}
    if args.resume:
        for path in (OUT_BAK, OUT_REPO, FLAT_BAK, FLAT_REPO):
            rows = load_json_list(path)
            for r in rows:
                cid = r.get("id")
                if not cid:
                    continue
                if "cigarworld" in r:
                    if (r.get("cigarworld") or {}).get("ok"):
                        prior[cid] = r
                elif r.get("ok") and r.get("facts"):
                    prior.setdefault(
                        cid,
                        {
                            "id": cid,
                            "brand": None,
                            "line": None,
                            "cw_url": r.get("url"),
                            "cigarworld": {
                                "ok": True,
                                "facts": r.get("facts") or {},
                                "url": r.get("url"),
                                "title": r.get("title") or "",
                            },
                            "famous": {"ok": False},
                        },
                    )

    merged = dict(prior)
    print(f"work={len(work)} prior_ok={sum(1 for v in prior.values() if (v.get('cigarworld') or {}).get('ok'))} bak={BACKUP_DIR}")

    for i, row in enumerate(work, 1):
        old = merged.get(row["id"])
        if old and (old.get("cigarworld") or {}).get("ok"):
            print(f"[{i}/{len(work)}] skip OK {row['id']}")
            continue

        entry = {
            "id": row["id"],
            "brand": row.get("brand"),
            "line": row.get("line"),
            "cw_url": row["cw_url"],
            "cigarworld": {"ok": False},
            "famous": {"ok": False},
        }
        print(f"[{i}/{len(work)}] CW {row['id']}", flush=True)
        try:
            html = fetch(row["cw_url"])
            entry["cigarworld"] = parse_cw(html)
            entry["cigarworld"]["url"] = row["cw_url"]
        except Exception as e:
            entry["cigarworld"] = {"ok": False, "error": str(e)[:240], "url": row["cw_url"]}
            if "429" in str(e):
                print("  rate-limited — pausing 20s", flush=True)
                time.sleep(20)

        merged[row["id"]] = entry
        time.sleep(args.sleep)
        if i % 25 == 0:
            write_outputs(merged)
            ok = sum(1 for v in merged.values() if (v.get("cigarworld") or {}).get("ok"))
            print(f"  checkpoint ok={ok}", flush=True)

    write_outputs(merged)
    ok = sum(1 for v in merged.values() if (v.get("cigarworld") or {}).get("ok"))
    print(f"done total={len(merged)} cw_ok={ok} bak={OUT_BAK}")


if __name__ == "__main__":
    main()
