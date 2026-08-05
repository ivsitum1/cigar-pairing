#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build W2 drink profile worklist: bottles in profile buckets >= 5.

Reads all drink JSON files, groups bottles by (body, sweetness, flavorTags)
profile key, and emits a worklist sorted by bucket size (largest first).

Priority order: gin → brandy → whisky → rum (as specified in W2 plan)

Usage:
  python scripts/build-drink-profile-worklist.py
  python scripts/build-drink-profile-worklist.py --min-bucket 3   # include >=3
  python scripts/build-drink-profile-worklist.py --json            # JSON output only
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
OUT = HERE / "output"

# W2 priority order: gin first, then brandy, whisky, rum
DRINK_FILES_ORDERED = [
    ("gins", "gin"),
    ("brandies", "brandy"),
    ("whiskies", "whisky"),
    ("rums", "rum"),
    ("wines", "wine"),
    ("tequilas", "tequila"),
    ("digestifs", "digestif"),
]


def profile_key(d: dict) -> tuple:
    return (d["body"], d["sweetness"], tuple(sorted(d.get("flavorTags") or [])))


def build_worklist(min_bucket: int = 5) -> dict:
    buckets_per_category: dict[str, dict] = {}
    worklist: list[dict] = []

    for fname, category in DRINK_FILES_ORDERED:
        path = DATA / f"{fname}.json"
        if not path.exists():
            continue
        bottles = json.loads(path.read_text(encoding="utf-8"))

        # Build bucket → [bottle_ids] mapping
        bucket_to_ids: dict[tuple, list[str]] = defaultdict(list)
        id_to_bottle: dict[str, dict] = {}
        for d in bottles:
            key = profile_key(d)
            bucket_to_ids[key].append(d["id"])
            id_to_bottle[d["id"]] = d

        # Count per bucket
        bucket_counts = Counter({k: len(v) for k, v in bucket_to_ids.items()})
        total_in_big = sum(v for v in bucket_counts.values() if v >= min_bucket)

        buckets_per_category[category] = {
            "total": len(bottles),
            "distinct_profiles": len(bucket_counts),
            "largest_bucket": max(bucket_counts.values()),
            "in_buckets_ge_5": sum(v for v in bucket_counts.values() if v >= 5),
            "in_target_buckets": total_in_big,
        }

        # Emit entries for buckets >= min_bucket, largest first
        for bucket_key, count in bucket_counts.most_common():
            if count < min_bucket:
                break
            body, sweetness, flavor_tags = bucket_key
            bucket_id = f"({body},{sweetness},{','.join(flavor_tags)})"
            for bid in bucket_to_ids[bucket_key]:
                bottle = id_to_bottle[bid]
                worklist.append({
                    "id": bid,
                    "name": bottle.get("name", ""),
                    "category": category,
                    "file": fname,
                    "bucket_id": bucket_id,
                    "bucket_size": count,
                    "body": body,
                    "sweetness": sweetness,
                    "flavor_tags": list(flavor_tags),
                    "priceUrl": bottle.get("priceUrl"),
                    "style": bottle.get("style"),
                    "region": bottle.get("region"),
                    "has_notes": bool(
                        (bottle.get("notes") or {}).get("en")
                        or (bottle.get("notes") or {}).get("hr")
                    ),
                    "notes_snippet": (
                        (bottle.get("notes") or {}).get("en", "")[:120]
                        or (bottle.get("notes") or {}).get("hr", "")[:120]
                    ),
                })

    return {
        "meta": {
            "min_bucket": min_bucket,
            "total_worklist_entries": len(worklist),
        },
        "per_category": buckets_per_category,
        "worklist": worklist,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-bucket", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    result = build_worklist(min_bucket=args.min_bucket)
    worklist = result["worklist"]

    OUT.mkdir(exist_ok=True)
    out_path = OUT / "drink_profile_worklist.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"W2 drink profile worklist — buckets >= {args.min_bucket}")
    print(f"{'Category':<12} {'Bottles':>7} {'Profiles':>9} {'Largest':>8} {'In>=5':>6}")
    print("-" * 46)
    for cat, stats in result["per_category"].items():
        print(
            f"{cat:<12} {stats['total']:>7} {stats['distinct_profiles']:>9} "
            f"{stats['largest_bucket']:>8} {stats['in_buckets_ge_5']:>6}"
        )
    print("-" * 46)
    total_bottles = sum(s["total"] for s in result["per_category"].values())
    total_in_big = sum(s["in_buckets_ge_5"] for s in result["per_category"].values())
    print(
        f"{'TOTAL':<12} {total_bottles:>7} {'':>9} {'':>8} {total_in_big:>6} "
        f"({100*total_in_big/total_bottles:.1f}%)"
    )
    print()
    print(f"Worklist: {len(worklist)} entries -> {out_path}")

    # Print top buckets to fix
    print("\nTop 20 buckets to fix (priority: gin->brandy->whisky->rum):")
    from itertools import groupby
    seen = set()
    shown = 0
    for entry in worklist:
        key = (entry["category"], entry["bucket_id"])
        if key in seen:
            continue
        seen.add(key)
        print(
            f"  [{entry['category']:<8}] size={entry['bucket_size']:>2}  "
            f"{entry['bucket_id'][:55]}"
        )
        shown += 1
        if shown >= 20:
            break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
