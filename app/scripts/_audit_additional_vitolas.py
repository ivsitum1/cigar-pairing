# -*- coding: utf-8 -*-
"""Audit Additional Vitolas buckets: propose remaps without mutating cigars.json."""
from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"
CIGARS = json.loads((DATA / "cigars.json").read_text(encoding="utf-8"))
OUT = ROOT.parent / "docs" / "superpowers" / "specs" / "2026-07-20-cigar-additional-vitolas-audit.md"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower().strip())


def brand_lines(brand: str) -> dict[str, str]:
    """norm(line) -> id for named lines (excl Additional Vitolas)."""
    out = {}
    for c in CIGARS:
        if c["brand"] != brand:
            continue
        if c["line"] == "Additional Vitolas":
            continue
        out[norm(c["line"])] = c["id"]
    return out


def guess_target(brand: str, vitola_name: str, lines: dict[str, str]) -> str | None:
    n = norm(vitola_name)
    # longest line name that appears as prefix/token in vitola
    best = None
    best_len = 0
    for line_n, cid in lines.items():
        if len(line_n) < 4:
            continue
        if n.startswith(line_n) or f" {line_n} " in f" {n} " or line_n in n:
            if len(line_n) > best_len:
                best = cid
                best_len = len(line_n)
    return best


def flag_issues(url: str | None, price, brand: str, vitola_name: str) -> list[str]:
    out = []
    if not url:
        out.append("missing_url")
    elif "?s=" in url or "post_type=product" in url:
        out.append("search_only_url")
    elif "/proizvod/" in url or "/product/" in url:
        slug = url.split("/proizvod/")[-1].split("/product/")[-1]
        slug_n = norm(slug.replace("-", " ").replace("%c2%bd", " "))
        tokens = set(re.findall(r"[a-z0-9]{4,}", norm(f"{brand} {vitola_name}")))
        slug_toks = set(re.findall(r"[a-z0-9]{4,}", slug_n))
        if tokens and slug_toks and not tokens & slug_toks:
            out.append("url_token_mismatch")
        # sampler pasted as single stick
        if "sampler" in slug_n and "sampler" not in norm(vitola_name):
            out.append("sampler_url_on_stick")
    if price is None:
        out.append("null_price")
    return out


def main() -> None:
    extras = [c for c in CIGARS if c.get("line") == "Additional Vitolas"]
    rows = []
    for extra in sorted(extras, key=lambda c: c["brand"]):
        brand = extra["brand"]
        lines = brand_lines(brand)
        for v in extra.get("vitolas") or []:
            target = guess_target(brand, v["name"], lines)
            fl = flag_issues(v.get("url"), v.get("priceEUR"), brand, v["name"])
            if target:
                fl.insert(0, f"remap_to:{target}")
            elif any(
                k in norm(v["name"])
                for k in (
                    "sampler",
                    "limited",
                    "anniversary",
                    "reserva",
                    "serie",
                    "series",
                )
            ):
                fl.append("possible_own_line")
            rows.append(
                {
                    "brand": brand,
                    "extra_id": extra["id"],
                    "vitola": v["name"],
                    "price": v.get("priceEUR"),
                    "url": v.get("url"),
                    "flags": fl,
                }
            )

    by_brand: dict[str, list] = defaultdict(list)
    for r in rows:
        by_brand[r["brand"]].append(r)

    lines_out = [
        "# Additional Vitolas audit (2026-07-20)",
        "",
        "Read-only audit of all `line: \"Additional Vitolas\"` buckets in `app/src/data/cigars.json`.",
        "AJ Fernandez Additional Vitolas entry was **removed** in the same pass (lines remapped to named entries).",
        "",
        "## Summary",
        "",
        f"- Brands with Additional Vitolas: **{len(by_brand)}**",
        f"- Vitola rows audited: **{len(rows)}**",
        f"- Rows with suggested remap to existing line: **{sum(1 for r in rows if any(f.startswith('remap_to:') for f in r['flags']))}**",
        f"- Search-only URLs: **{sum(1 for r in rows if 'search_only_url' in r['flags'])}**",
        f"- Sampler URL on single stick: **{sum(1 for r in rows if 'sampler_url_on_stick' in r['flags'])}**",
        f"- URL token mismatch: **{sum(1 for r in rows if 'url_token_mismatch' in r['flags'])}**",
        "",
        "## Priority brands (most remap / URL issues)",
        "",
    ]

    scored = []
    for brand, items in by_brand.items():
        score = sum(
            1
            for r in items
            for f in r["flags"]
            if f.startswith("remap_to:")
            or f in ("search_only_url", "sampler_url_on_stick", "url_token_mismatch")
        )
        scored.append((score, brand, items))
    scored.sort(reverse=True)

    for score, brand, items in scored[:15]:
        lines_out.append(f"### {brand} (issue score {score})")
        lines_out.append("")
        lines_out.append("| Vitola | Flags | Price |")
        lines_out.append("|--------|-------|-------|")
        for r in items:
            flag_s = ", ".join(r["flags"]) if r["flags"] else "ok"
            price = r["price"] if r["price"] is not None else "—"
            lines_out.append(f"| {r['vitola']} | {flag_s} | {price} |")
        lines_out.append("")

    lines_out.extend(
        [
            "## Full flag legend",
            "",
            "- `remap_to:<id>`: vitola name matches an existing named line under the same brand",
            "- `search_only_url`: Humidor search URL, not a product page",
            "- `sampler_url_on_stick`: product URL is a sampler while vitola is a single format",
            "- `url_token_mismatch`: product slug shares no 4+ char token with brand/vitola",
            "- `null_price`: no EUR price",
            "- `possible_own_line`: name hints at a distinct line not yet in catalog",
            "",
            "## Next passes (suggested order)",
            "",
        ]
    )
    for score, brand, _ in scored:
        if score <= 0:
            continue
        lines_out.append(f"1. **{brand}** (score {score})")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"brands={len(by_brand)} rows={len(rows)}")
    for score, brand, _ in scored[:10]:
        print(f"  {score:3d}  {brand}")


if __name__ == "__main__":
    main()
