#!/usr/bin/env python3
"""Find truncated/split brands and likely duplicate catalog rows.

Heuristics:
  1. Live brand still listed under renameBrand in taxonomy (should be folded)
  2. Line starts with 'by ' (shop title remnant)
  3. ' by ' in line pointing at another live brand
  4. Shape word used as line name (= vitola duplicate)
  5. Short brand whose lines mention another brand
  6. Brand name that is also a line of another brand (house-line split)
  7. Same shop URL on more than one cigar id (unmerged duplicate)

Prints a compact report. Does not write catalog.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from taxonomy_lib import CIGARS_PATH, TAXONOMY_DIR, shape_words  # noqa: E402

BY_RE = re.compile(r"\bby\s+(.+)$", re.I)
SHAPE = {s.lower() for s in shape_words()}


def load() -> list[dict]:
    return json.loads(CIGARS_PATH.read_text(encoding="utf-8"))


def tax_renames() -> dict[str, str]:
    out: dict[str, str] = {}
    for p in TAXONOMY_DIR.glob("*.json"):
        if p.parent.name == "_worklist":
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        brand = data.get("brand")
        rb = data.get("renameBrand")
        if brand and rb and brand != rb:
            out[brand] = rb
    return out


def norm_url(url: str | None) -> str | None:
    if not url or not isinstance(url, str):
        return None
    u = url.strip().rstrip("/")
    if not u.startswith("http"):
        return None
    p = urlparse(u)
    host = (p.netloc or "").lower().removeprefix("www.")
    path = (p.path or "").rstrip("/").lower()
    return f"{host}{path}"


def collect_urls(c: dict) -> set[str]:
    out: set[str] = set()
    for key in ("priceUrl", "url"):
        n = norm_url(c.get(key))
        if n:
            out.add(n)
    for link in (c.get("regionLinks") or {}).values():
        if isinstance(link, dict):
            n = norm_url(link.get("url"))
            if n:
                out.add(n)
    for v in c.get("vitolas") or []:
        if not isinstance(v, dict):
            continue
        n = norm_url(v.get("url"))
        if n:
            out.add(n)
        for link in (v.get("regionLinks") or {}).values():
            if isinstance(link, dict):
                n = norm_url(link.get("url"))
                if n:
                    out.add(n)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for machine-readable summary (counts + section 6/7 rows)",
    )
    ap.add_argument(
        "--skip-shapes",
        action="store_true",
        help="Omit section 4 (100+ Neptune shape stubs)",
    )
    args = ap.parse_args()

    cigars = load()
    brands = sorted({c.get("brand") or "" for c in cigars if c.get("brand")})
    brand_set = set(brands)
    by_brand: dict[str, list] = defaultdict(list)
    for c in cigars:
        by_brand[c.get("brand") or ""].append(c)

    summary: dict[str, object] = {"cigarCount": len(cigars), "sections": {}}

    print("=== 1. Live brand still has renameBrand in taxonomy ===")
    renames = tax_renames()
    leftover = [(src, dst) for src, dst in sorted(renames.items()) if src in brand_set]
    for src, dst in leftover:
        n = len(by_brand[src])
        print(f"  {src!r} -> {dst!r}  ({n} live rows)")
    if not leftover:
        print("  (none)")
    summary["sections"]["renameBrandPending"] = [
        {"from": src, "to": dst, "rows": len(by_brand[src])} for src, dst in leftover
    ]

    print("\n=== 2. Line starts with 'by ' (shop title remnant) ===")
    by_lines = []
    for c in cigars:
        line = c.get("line") or ""
        if line.lower().startswith("by "):
            by_lines.append(c)
            print(f"  {c.get('id')}  brand={c.get('brand')!r}  line={line!r}  vitola={c.get('vitola')!r}")
    if not by_lines:
        print("  (none)")
    summary["sections"]["lineStartsWithBy"] = [c["id"] for c in by_lines]

    print("\n=== 3. Line contains ' by ' -> another live brand ===")
    by_parent: list[dict] = []
    for c in cigars:
        brand = c.get("brand") or ""
        line = c.get("line") or ""
        m = BY_RE.search(line)
        if not m:
            continue
        parent = m.group(1).strip()
        hit_parent = parent if parent in brand_set else None
        if hit_parent and hit_parent != brand:
            by_parent.append(c)
            print(f"  {c.get('id')}  {brand!r} / {line!r}  -> parent brand {hit_parent!r}")
    if not by_parent:
        print("  (none)")
    summary["sections"]["byAnotherBrand"] = [
        {"id": c["id"], "brand": c.get("brand"), "line": c.get("line")} for c in by_parent
    ]

    print("\n=== 4. Line equals vitola AND line is a shape word ===")
    shape_as_line: list[dict] = []
    if args.skip_shapes:
        print("  (skipped — use default run for full list)")
    else:
        for c in cigars:
            line = (c.get("line") or "").strip()
            vitola = (c.get("vitola") or "").strip()
            if not line or line.lower() not in SHAPE:
                continue
            if line.lower() == vitola.lower() or any(
                (v.get("name") or "").lower() == line.lower() for v in (c.get("vitolas") or [])
            ):
                shape_as_line.append(c)
                print(
                    f"  {c.get('id')}  brand={c.get('brand')!r}  line=vitola={line!r}  "
                    f"url={(c.get('priceUrl') or '')[:80]}"
                )
        print(f"  total={len(shape_as_line)}")
    summary["sections"]["shapeAsLineCount"] = len(shape_as_line)

    print("\n=== 5. Short brand whose lines mention another brand ===")
    short_mentions: list[dict] = []
    for brand, rows in sorted(by_brand.items()):
        tokens = brand.replace(".", " ").split()
        if len(tokens) > 2:
            continue
        if len(brand) > 18 and len(tokens) > 1:
            continue
        mentioned: dict[str, int] = defaultdict(int)
        for c in rows:
            line = c.get("line") or ""
            for other in brand_set:
                if other == brand:
                    continue
                if other.lower() in line.lower():
                    mentioned[other] += 1
        if mentioned:
            top = sorted(mentioned.items(), key=lambda x: -x[1])[:3]
            short_mentions.append({"brand": brand, "rows": len(rows), "mentions": top})
            print(f"  brand={brand!r} n={len(rows)} mentions={top}")
    summary["sections"]["shortBrandMentionsCount"] = len(short_mentions)

    print("\n=== 6. Brand equals another brand's line name ===")
    lines_of: dict[str, set[str]] = defaultdict(set)
    for c in cigars:
        if c.get("line"):
            lines_of[c["line"]].add(c.get("brand") or "")
    brand_line_dupes: list[dict] = []
    for brand in brands:
        owners = lines_of.get(brand) or set()
        owners.discard(brand)
        if owners:
            n = len(by_brand[brand])
            brand_line_dupes.append({"brand": brand, "rows": n, "alsoLineOf": sorted(owners)})
            print(f"  live brand {brand!r} ({n} rows) is also a line of {sorted(owners)[:6]}")
    summary["sections"]["brandEqualsLine"] = brand_line_dupes

    print("\n=== 7. Same shop URL on multiple cigar ids ===")
    url_to_ids: dict[str, list[str]] = defaultdict(list)
    for c in cigars:
        cid = c.get("id") or ""
        for u in collect_urls(c):
            url_to_ids[u].append(cid)
    dup_urls: list[dict] = []
    for u, ids in sorted(url_to_ids.items(), key=lambda x: (-len(x[1]), x[0])):
        uniq = sorted(set(ids))
        if len(uniq) < 2:
            continue
        dup_urls.append({"url": u, "ids": uniq})
        brands_involved = sorted({next(x["brand"] for x in cigars if x["id"] == i) for i in uniq})
        print(f"  {u}")
        print(f"    ids={uniq}")
        print(f"    brands={brands_involved}")
    if not dup_urls:
        print("  (none)")
    summary["sections"]["duplicateUrls"] = dup_urls
    print(f"  total duplicate-url groups={len(dup_urls)}")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nWrote summary -> {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
