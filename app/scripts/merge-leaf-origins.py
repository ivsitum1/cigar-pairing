#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge wrapper/binder/filler origins into cigars.json and derive isPuro.

Sources (priority):
  1. CigarWorld raw (cigarworld_flavor_raw.json, cw_famous_flavor_raw.json)
  2. Unified shop catalog (cigar_unified_catalog.json) — brand+line match
  3. Cuban manufacture default (country=Kuba → all origins Kuba if no conflict)

Never invents binder/filler. Writes coverage report alongside merge.

  python scripts/merge-leaf-origins.py
  python scripts/merge-leaf-origins.py --dry-run
  python scripts/merge-leaf-origins.py --skip-unified
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from lib.leaf_origins import (  # noqa: E402
    apply_cuban_default,
    apply_leaf_fields,
    leaf_from_facts,
    normalize_origin_single,
    refresh_is_puro,
)

DATA = HERE.parent / "src" / "data"
CIGARS = DATA / "cigars.json"
OUT = HERE / "output"
CW_RAW = OUT / "cigarworld_flavor_raw.json"
CW_FAMOUS = OUT / "cw_famous_flavor_raw.json"
# Local non-OneDrive backup from scrape-leaf-origins.py
import os

_BAK = Path(os.environ.get("LOCALAPPDATA", str(OUT))) / "cigar_leaf_scrape"
CW_RAW_BAK = _BAK / "cigarworld_flavor_raw.json"
CW_FAMOUS_BAK = _BAK / "cw_famous_flavor_raw.json"
UNIFIED = OUT / "cigar_unified_catalog.json"
REPORT = OUT / "leaf_origins_coverage.json"


def slug_bits(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def load_cw_facts_by_id() -> dict[str, dict]:
    """id → facts dict from both CW raw formats (repo + local backup)."""
    by_id: dict[str, dict] = {}

    def ingest_flat(rows: list) -> None:
        for r in rows:
            cid = r.get("id")
            if not cid or not r.get("ok"):
                continue
            facts = r.get("facts") or {}
            if facts:
                _prefer(by_id, cid, facts)

    def ingest_famous(rows: list) -> None:
        for r in rows:
            cid = r.get("id")
            if not cid:
                continue
            cw = r.get("cigarworld") or {}
            if not cw.get("ok"):
                continue
            facts = cw.get("facts") or {}
            if facts:
                _prefer(by_id, cid, facts)
            fam = r.get("famous") or {}
            if fam.get("ok") and fam.get("facts"):
                ff = fam["facts"]
                merged = dict(by_id.get(cid) or {})
                for k, v in ff.items():
                    key = str(k).lower()
                    if key in ("wrapper", "binder", "filler") and v and key not in merged:
                        merged[key] = v
                by_id[cid] = merged

    def _prefer(store: dict, cid: str, facts: dict) -> None:
        prev = store.get(cid) or {}
        score = sum(
            1
            for k in ("wrapper origin", "binder origin", "filler origin")
            if facts.get(k)
        )
        prev_score = sum(
            1
            for k in ("wrapper origin", "binder origin", "filler origin")
            if prev.get(k)
        )
        if score >= prev_score:
            store[cid] = facts

    for path in (CW_RAW, CW_RAW_BAK):
        if path.exists():
            ingest_flat(json.loads(path.read_text(encoding="utf-8-sig")))
    for path in (CW_FAMOUS, CW_FAMOUS_BAK):
        if path.exists():
            ingest_famous(json.loads(path.read_text(encoding="utf-8-sig")))

    return by_id


def build_unified_index(records: list[dict]) -> dict[tuple[str, str], dict]:
    """(brand_slug, line_slug) → best leaf facts from shop details."""
    index: dict[tuple[str, str], dict] = {}
    for rec in records:
        brand = rec.get("brand") or ""
        line = rec.get("line") or rec.get("name") or ""
        if not brand or not line:
            continue
        key = (slug_bits(brand), slug_bits(line))
        if not key[0] or not key[1]:
            continue
        det = dict(rec.get("details") or {})
        for o in rec.get("offers") or []:
            od = o.get("details") or {}
            for k, v in od.items():
                if k not in det and v:
                    det[k] = v
        if not any(det.get(k) for k in ("wrapper", "binder", "filler")):
            continue
        facts = {
            "wrapper": det.get("wrapper"),
            "binder": det.get("binder"),
            "filler": det.get("filler"),
            "wrapper origin": det.get("wrapper") if normalize_origin_single(det.get("wrapper")) else None,
            "binder origin": det.get("binder") if normalize_origin_single(det.get("binder")) else None,
            "filler origin": det.get("filler") if normalize_origin_single(det.get("filler")) else None,
        }
        # Also try dedicated origin keys if present
        for ok in ("wrapper_origin", "binder_origin", "filler_origin"):
            if det.get(ok):
                facts[ok.replace("_", " ")] = det[ok]

        prev = index.get(key)
        if not prev:
            index[key] = facts
            continue
        prev_n = sum(1 for x in (prev.get("binder"), prev.get("filler")) if x)
        new_n = sum(1 for x in (facts.get("binder"), facts.get("filler")) if x)
        if new_n >= prev_n:
            index[key] = facts
    return index


def coverage_stats(cigars: list[dict]) -> dict:
    n = len(cigars)
    wo = sum(1 for c in cigars if c.get("wrapperOrigin"))
    bo = sum(1 for c in cigars if c.get("binderOrigin"))
    fo = sum(1 for c in cigars if c.get("fillerOrigin"))
    all3 = sum(
        1
        for c in cigars
        if c.get("wrapperOrigin") and c.get("binderOrigin") and c.get("fillerOrigin")
    )
    puro_t = sum(1 for c in cigars if c.get("isPuro") is True)
    puro_f = sum(1 for c in cigars if c.get("isPuro") is False)
    puro_u = n - puro_t - puro_f
    origins_w = Counter(c["wrapperOrigin"] for c in cigars if c.get("wrapperOrigin"))
    return {
        "total": n,
        "wrapperOrigin": wo,
        "binderOrigin": bo,
        "fillerOrigin": fo,
        "all_three_origins": all3,
        "isPuro_true": puro_t,
        "isPuro_false": puro_f,
        "isPuro_unknown": puro_u,
        "pct_all_three": round(100.0 * all3 / n, 1) if n else 0,
        "top_wrapper_origins": origins_w.most_common(15),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-unified", action="store_true")
    ap.add_argument("--skip-cuban", action="store_true")
    args = ap.parse_args()

    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in cigars}

    cw_facts = load_cw_facts_by_id()
    stats = Counter()

    for cid, facts in cw_facts.items():
        c = by_id.get(cid)
        if not c:
            stats["cw_orphan"] += 1
            continue
        leaf = leaf_from_facts(facts)
        # CW wins over empty; fill display binder/filler always when empty
        if apply_leaf_fields(c, leaf, prefer_existing=True, fill_wrapper_display=True):
            stats["cw_updated"] += 1
        else:
            stats["cw_noop"] += 1
        # Force-set origins from CW even when prefer_existing would skip empty-only
        for ok in ("wrapperOrigin", "binderOrigin", "fillerOrigin"):
            if leaf.get(ok) and not c.get(ok):
                c[ok] = leaf[ok]
                stats["cw_origin_fill"] += 1
        for dk in ("binder", "filler"):
            if leaf.get(dk) and not c.get(dk):
                c[dk] = leaf[dk]
                stats["cw_display_fill"] += 1
        # Prefer CW variety for wrapper when current is weak country-only
        if leaf.get("wrapper"):
            cur = (c.get("wrapper") or "").strip()
            if cur in ("—", "-", "Natural", "?", "") or normalize_origin_single(cur):
                # country-as-wrapper → replace with variety if different
                if leaf["wrapper"] != cur:
                    c["wrapper"] = leaf["wrapper"]
                    stats["cw_wrapper_upgrade"] += 1

    unified_matched = 0
    if not args.skip_unified and UNIFIED.exists():
        raw_u = json.loads(UNIFIED.read_text(encoding="utf-8-sig"))
        if isinstance(raw_u, list):
            records = raw_u
        else:
            records = raw_u.get("cigars") or raw_u.get("records") or []
        # Direct catalogId match first
        by_catalog_id: dict[str, dict] = {}
        for rec in records:
            cid = rec.get("catalogId") or rec.get("id")
            if not cid or not str(cid).startswith("cig-"):
                continue
            det = dict(rec.get("details") or {})
            for o in rec.get("offers") or []:
                od = o.get("details") or {}
                for k, v in od.items():
                    if k not in det and v:
                        det[k] = v
            if not any(det.get(k) for k in ("wrapper", "binder", "filler")):
                continue
            facts = {
                "wrapper": det.get("wrapper"),
                "binder": det.get("binder"),
                "filler": det.get("filler"),
            }
            prev = by_catalog_id.get(cid)
            if not prev or sum(1 for x in (facts.get("binder"), facts.get("filler")) if x) >= sum(
                1 for x in (prev.get("binder"), prev.get("filler")) if x
            ):
                by_catalog_id[cid] = facts

        index = build_unified_index(records)
        stats["unified_index"] = len(index)
        stats["unified_by_id"] = len(by_catalog_id)
        for c in cigars:
            if c.get("wrapperOrigin") and c.get("binderOrigin") and c.get("fillerOrigin"):
                continue
            facts = by_catalog_id.get(c["id"])
            if not facts:
                key = (slug_bits(c.get("brand") or ""), slug_bits(c.get("line") or ""))
                facts = index.get(key)
            if not facts:
                continue
            leaf = leaf_from_facts(facts)
            before = (
                c.get("wrapperOrigin"),
                c.get("binderOrigin"),
                c.get("fillerOrigin"),
                c.get("binder"),
                c.get("filler"),
            )
            apply_leaf_fields(c, leaf, prefer_existing=True)
            for ok in ("wrapperOrigin", "binderOrigin", "fillerOrigin"):
                if leaf.get(ok) and not c.get(ok):
                    c[ok] = leaf[ok]
            for dk in ("binder", "filler"):
                if leaf.get(dk) and not c.get(dk):
                    c[dk] = leaf[dk]
            after = (
                c.get("wrapperOrigin"),
                c.get("binderOrigin"),
                c.get("fillerOrigin"),
                c.get("binder"),
                c.get("filler"),
            )
            if after != before:
                unified_matched += 1
        stats["unified_matched"] = unified_matched
    elif not args.skip_unified:
        stats["unified_missing"] = 1

    cuban_n = 0
    if not args.skip_cuban:
        for c in cigars:
            if apply_cuban_default(c):
                cuban_n += 1
        stats["cuban_default"] = cuban_n

    for c in cigars:
        refresh_is_puro(c)

    report = coverage_stats(cigars)
    report["merge_stats"] = dict(stats)

    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not args.dry_run:
        CIGARS.write_text(json.dumps(cigars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"wrote_report={REPORT} dry_run={args.dry_run}")


if __name__ == "__main__":
    main()
