#!/usr/bin/env python3
"""Apply app/scripts/data/taxonomy/*.json onto cigars.json.

Pass order (plan §4.2 + §5):
  0 auto-pass P1–P5 (deterministic floor)
  1 brand rename → 2 line remap → 3 record merge → 4 vitola rename/shape
  → 5 dimension parse → 6 derive ids/sort → 7 aliases → 8 normalize-vitolas

Hand-written taxonomy files always win over auto-pass (keyed via _raw_line).

Usage:
  python scripts/apply-taxonomy.py
  python scripts/apply-taxonomy.py --check
  python scripts/apply-taxonomy.py --skip-normalize
"""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

from taxonomy_lib import (
    ALIASES_PATH,
    CIGARS_PATH,
    OUT_DIR,
    brand_slug,
    cigar_id,
    format_missing,
    line_ends_with_shape,
    load_json,
    load_taxonomy_files,
    normalize_format_string,
    normalize_line_key,
    parse_format,
    shape_words,
    split_trailing_dimensions,
    toks,
    write_json,
)

APP = Path(__file__).resolve().parent.parent


def locale_url(u: str | None) -> str | None:
    if not u:
        return None
    import re

    u = u.split("?")[0].split("#")[0]
    u = re.sub(
        r"(humidor\.hr|havana-cigar-shop\.com)/(?:hr|en)/proizvod/",
        r"\1/proizvod/",
        u,
    )
    return u.rstrip("/")


def vitola_key(v: dict) -> str:
    name = (v.get("name") or "").strip().lower()
    url = locale_url(v.get("url")) or locale_url(
        ((v.get("regionLinks") or {}).get("HR") or {}).get("url")
    )
    return f"{name}||{url or ''}"


def merge_vitolas(a: list, b: list) -> list:
    by = {}
    order = []
    for src in (a or []) + (b or []):
        k = vitola_key(src)
        if k not in by:
            by[k] = copy.deepcopy(src)
            order.append(k)
        else:
            cur = by[k]
            for field in ("format", "smokeTimeMin", "priceEUR", "url"):
                if cur.get(field) in (None, "", "—") and src.get(field) not in (None, "", "—"):
                    cur[field] = src[field]
            rl = dict(cur.get("regionLinks") or {})
            for reg, link in (src.get("regionLinks") or {}).items():
                if reg not in rl:
                    rl[reg] = link
                elif reg == "HR" and link.get("url") and "humidor" in (link.get("url") or ""):
                    rl[reg] = link
            if rl:
                cur["regionLinks"] = rl
    return [by[k] for k in order]


def merge_notes(a: dict | None, b: dict | None) -> dict:
    a = a or {}
    b = b or {}
    out = {}
    for lang in ("hr", "en"):
        av = (a.get(lang) or "").strip()
        bv = (b.get(lang) or "").strip()
        out[lang] = av if len(av) >= len(bv) else bv
    return out


def merge_records(canonical: dict, other: dict, report: dict) -> dict:
    out = copy.deepcopy(canonical)
    out["vitolas"] = merge_vitolas(out.get("vitolas") or [], other.get("vitolas") or [])
    markets = sorted(set((out.get("markets") or []) + (other.get("markets") or [])))
    out["markets"] = markets
    rl = dict(out.get("regionLinks") or {})
    for reg, link in (other.get("regionLinks") or {}).items():
        if reg not in rl:
            rl[reg] = link
    if rl:
        out["regionLinks"] = rl
    out["notes"] = merge_notes(out.get("notes"), other.get("notes"))
    prices = [p for p in (out.get("priceEUR"), other.get("priceEUR")) if isinstance(p, (int, float))]
    if prices:
        out["priceEUR"] = min(prices)
    for flag in ("flavoured", "strengthFromShop", "formatEstimated", "profileEstimated"):
        out[flag] = bool(out.get(flag)) or bool(other.get(flag))
    for metric in ("strength", "body"):
        a, b = out.get(metric), other.get(metric)
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if abs(a - b) <= 1:
                out[metric] = round((a + b) / 2)
            else:
                report.setdefault("metric_conflicts", []).append(
                    {"id": out.get("id"), "metric": metric, "a": a, "b": b}
                )
    lineup = list(out.get("lineup") or [])
    for x in other.get("lineup") or []:
        if x not in lineup:
            lineup.append(x)
    if lineup:
        out["lineup"] = lineup
    return out


def strip_leading_brand_line_tokens(name: str, brand: str, line: str) -> str:
    """Stream-G style: strip leading brand/line token runs; keep single-char tokens."""
    vt = toks(name)
    prefix = toks(f"{brand} {line}")
    if not vt or not prefix:
        return name
    i = 0
    while i < len(prefix) and i < len(vt) and prefix[i] == vt[i]:
        # never strip a lone roman/letter token that distinguishes (Siglo I vs V)
        if len(vt[i]) == 1 and vt[i].isalpha():
            break
        i += 1
    if i == 0:
        return name
    rest = vt[i:]
    if not rest:
        return name
    # rebuild with original casing best-effort: join remaining original words
    parts = name.split()
    # fall back to title-case rest
    return " ".join(parts[i:]) if len(parts) >= len(vt) else " ".join(w.title() for w in rest)


def sort_vitolas(vitolas: list) -> list:
    def key(v):
        ring = v.get("ring")
        lmm = v.get("lengthMM")
        return (
            ring is None,
            ring if ring is not None else 999,
            lmm is None,
            lmm if lmm is not None else 9999,
            (v.get("name") or "").lower(),
        )

    return sorted(vitolas, key=key)


def _dims_conflict(a: dict, b: dict) -> bool:
    """True when both have parseable dims that disagree."""
    ar, al = parse_format(a.get("format"))
    br, bl = parse_format(b.get("format"))
    if ar is None or br is None:
        return False
    return ar != br or (al is not None and bl is not None and al != bl)


def auto_pass(cigars: list, report: dict) -> list:
    """Phase 1 deterministic floor (plan §5). Taxonomy remaps override afterward."""
    shapes = shape_words()
    auto = report.setdefault(
        "auto_pass",
        {"P1": [], "P2": [], "P3": [], "P4": [], "P5": []},
    )

    # Snapshot raw lines so taxonomy files can still key on pre-auto strings.
    for c in cigars:
        c["_raw_line"] = c.get("line") or ""

    # P1 — strip trailing dimensions from line into vitola.format when missing
    for c in cigars:
        line = c.get("line") or ""
        split = split_trailing_dimensions(line)
        if not split:
            continue
        new_line, fmt_hint = split
        c["line"] = new_line
        vitolas = c.get("vitolas") or []
        if len(vitolas) == 1 and format_missing(vitolas[0].get("format")):
            vitolas[0]["format"] = fmt_hint
        elif not vitolas:
            c["vitolas"] = [
                {
                    "name": c.get("vitola") or "Unknown",
                    "format": fmt_hint,
                    "smokeTimeMin": None,
                    "priceEUR": None,
                    "url": None,
                }
            ]
        auto["P1"].append({"id": c.get("id"), "from": line, "to": new_line, "format": fmt_hint})

    # P2 — line ends with shape AND sole vitola has that same shape name → strip from line
    for c in cigars:
        line = c.get("line") or ""
        sh = line_ends_with_shape(line, shapes)
        if not sh:
            continue
        vitolas = c.get("vitolas") or []
        if len(vitolas) != 1:
            continue
        vname = (vitolas[0].get("name") or "").strip().lower()
        if vname != sh and vname != sh.replace(" ", ""):
            # also accept exact last-token equality for multi-word shapes
            if vname != sh.split()[-1]:
                continue
        low = line.strip().lower()
        if low == sh:
            continue  # would empty the line
        cut = len(line) - len(sh) if low.endswith(sh) else None
        if cut is None:
            continue
        new_line = line[:cut].rstrip(" -–—/")
        if not new_line or new_line == line:
            continue
        c["line"] = new_line
        if not vitolas[0].get("shape"):
            vitolas[0]["shape"] = sh.title() if sh.islower() else sh
        auto["P2"].append({"id": c.get("id"), "from": line, "to": new_line, "shape": sh})

    # P3 — collapse lines equal after normalization within each brand
    by_brand: dict[str, list] = {}
    for c in cigars:
        by_brand.setdefault(c.get("brand") or "", []).append(c)
    for brand, rows in by_brand.items():
        buckets: dict[str, list] = {}
        for c in rows:
            key = normalize_line_key(c.get("line") or "")
            if not key:
                continue
            buckets.setdefault(key, []).append(c)
        for key, group in buckets.items():
            spellings = [c.get("line") or "" for c in group]
            uniq = sorted(set(spellings), key=lambda s: (len(s), s.lower()))
            if len(uniq) < 2:
                continue
            # Prefer the shortest spelling (usually without punctuation noise);
            # tie-break: most common, then lexicographic.
            counts: dict[str, int] = {}
            for s in spellings:
                counts[s] = counts.get(s, 0) + 1
            canon = sorted(uniq, key=lambda s: (-counts[s], len(s), s.lower()))[0]
            for c in group:
                if c.get("line") != canon:
                    auto["P3"].append(
                        {"id": c.get("id"), "from": c.get("line"), "to": canon, "brand": brand}
                    )
                    c["line"] = canon

    # P4 — strip leading brand/line tokens from vitola names (guard dim conflicts)
    for c in cigars:
        brand = c.get("brand") or ""
        line = c.get("line") or ""
        vitolas = c.get("vitolas") or []
        proposed = []
        for v in vitolas:
            old = v.get("name") or ""
            new = strip_leading_brand_line_tokens(old, brand, line)
            proposed.append((v, old, new))
        # conflict: two proposed names collide with conflicting dims → skip those strips
        by_new: dict[str, list] = {}
        for v, old, new in proposed:
            by_new.setdefault(new.lower(), []).append((v, old, new))
        skip = set()
        for _nk, items in by_new.items():
            if len(items) < 2:
                continue
            for i, (va, _oa, _na) in enumerate(items):
                for vb, _ob, _nb in items[i + 1 :]:
                    if _dims_conflict(va, vb):
                        skip.add(id(va))
                        skip.add(id(vb))
        for v, old, new in proposed:
            if old == new or id(v) in skip:
                continue
            v["name"] = new
            if c.get("vitola") == old:
                c["vitola"] = new
            auto["P4"].append({"id": c.get("id"), "from": old, "to": new})

    # P5 — normalize fraction glyphs and X→x in every format string
    for c in cigars:
        if c.get("format"):
            nf = normalize_format_string(c.get("format"))
            if nf != c.get("format"):
                auto["P5"].append({"id": c.get("id"), "field": "format", "from": c.get("format"), "to": nf})
                c["format"] = nf
        for v in c.get("vitolas") or []:
            if v.get("format"):
                nf = normalize_format_string(v.get("format"))
                if nf != v.get("format"):
                    auto["P5"].append(
                        {
                            "id": c.get("id"),
                            "vitola": v.get("name"),
                            "from": v.get("format"),
                            "to": nf,
                        }
                    )
                    v["format"] = nf

    report["auto_pass_counts"] = {k: len(v) for k, v in auto.items()}
    return cigars


def apply_taxonomy(cigars: list, tax_files: list[dict], report: dict) -> list:
    # Index taxonomy by current brand key
    by_brand: dict[str, dict] = {}
    rename_map: dict[str, str] = {}
    for tf in tax_files:
        brand = tf.get("brand")
        if not brand:
            continue
        by_brand[brand] = tf
        rb = tf.get("renameBrand")
        if rb:
            rename_map[brand] = rb

    # 1. Brand canonicalization
    for c in cigars:
        b = c.get("brand")
        if b in rename_map:
            report.setdefault("brand_renames", []).append({"from": b, "to": rename_map[b], "id": c.get("id")})
            c["brand"] = rename_map[b]

    # 2. Line remap
    for c in cigars:
        tf = by_brand.get(c.get("brand")) or by_brand.get(
            next((src for src, dst in rename_map.items() if dst == c.get("brand")), None)
        )
        # taxonomy file is keyed by *current* brand before rename; also try original via file brand
        if not tf:
            for cand in tax_files:
                if cand.get("renameBrand") == c.get("brand") or cand.get("brand") == c.get("brand"):
                    tf = cand
                    break
        if not tf:
            continue
        lines_map = tf.get("lines") or {}
        raw_line = c.get("_raw_line") or c.get("line") or ""
        cur_line = c.get("line") or ""
        spec = lines_map.get(raw_line) or lines_map.get(cur_line)
        if not spec:
            continue
        if spec.get("drop"):
            report.setdefault("dropped", []).append(c.get("id"))
            c["_drop"] = True
            continue
        new_line = spec.get("line", raw_line)
        c["line"] = new_line
        if spec.get("sampler"):
            c.setdefault("lineup", c.get("lineup") or [])
        if "vitola" in spec:
            vname = spec["vitola"]
            vitolas = c.get("vitolas") or []
            if len(vitolas) > 1 and not spec.get("vitolas"):
                report.setdefault("errors", []).append(
                    {
                        "id": c.get("id"),
                        "error": "vitola remap on multi-vitola record without per-vitola map",
                    }
                )
            elif len(vitolas) == 1:
                vitolas[0]["name"] = vname
                if spec.get("shape"):
                    vitolas[0]["shape"] = spec["shape"]
                c["vitola"] = vname
            elif not vitolas:
                c["vitolas"] = [{"name": vname, "format": None, "smokeTimeMin": None, "priceEUR": None, "url": None}]
                if spec.get("shape"):
                    c["vitolas"][0]["shape"] = spec["shape"]
                c["vitola"] = vname
            c["vitolas"] = vitolas
        elif spec.get("shape") and (c.get("vitolas") or []):
            if len(c["vitolas"]) == 1:
                c["vitolas"][0]["shape"] = spec["shape"]

    cigars = [c for c in cigars if not c.get("_drop")]

    # 3. Record merge by (brand, line)
    groups: dict[tuple[str, str], list] = {}
    for c in cigars:
        key = (c.get("brand") or "", c.get("line") or "")
        groups.setdefault(key, []).append(c)

    merged = []
    aliases_new = []
    for (brand, line), rows in groups.items():
        # prefer non-market / longer notes as canonical base
        rows_sorted = sorted(
            rows,
            key=lambda r: (
                1 if r.get("catalogSource") == "market" else 0,
                -len(((r.get("notes") or {}).get("hr") or "")),
                r.get("id") or "",
            ),
        )
        base = copy.deepcopy(rows_sorted[0])
        for other in rows_sorted[1:]:
            base = merge_records(base, other, report)
            if other.get("id") and other.get("id") != base.get("id"):
                aliases_new.append({"from": other["id"], "to": None})  # filled after id derive
                report.setdefault("merges", []).append({"into": base.get("id"), "from": other.get("id")})
        # stash old ids + pre-auto lines for stable-id derive
        base["_old_ids"] = [r.get("id") for r in rows_sorted if r.get("id")]
        base["_raw_lines"] = [
            r.get("_raw_line") if r.get("_raw_line") is not None else (r.get("line") or "")
            for r in rows_sorted
        ]
        base.pop("_raw_line", None)
        merged.append(base)

    # 4. Vitola rename + shape + strip tokens
    for c in merged:
        tf = None
        for cand in tax_files:
            if cand.get("renameBrand") == c.get("brand") or cand.get("brand") == c.get("brand"):
                tf = cand
                break
        renames = (tf or {}).get("vitolaRenames") or {}
        shapes = (tf or {}).get("shapes") or {}
        line = c.get("line") or ""
        brand = c.get("brand") or ""
        for v in c.get("vitolas") or []:
            key = f"{line}::{v.get('name')}"
            if key in renames:
                v["name"] = renames[key]
            if key in shapes:
                v["shape"] = shapes[key]
            stripped = strip_leading_brand_line_tokens(v.get("name") or "", brand, line)
            if stripped != v.get("name"):
                report.setdefault("vitola_strips", []).append(
                    {"id": c.get("id"), "from": v.get("name"), "to": stripped}
                )
                v["name"] = stripped

    # 5. Dimension parse
    for c in merged:
        for v in c.get("vitolas") or []:
            fmt = normalize_format_string(v.get("format"))
            if fmt != v.get("format"):
                v["format"] = fmt
            ring, lmm = parse_format(v.get("format"))
            if ring is not None:
                v["ring"] = ring
            if lmm is not None:
                v["lengthMM"] = lmm
        # record-level format from default vitola
        c["vitolas"] = sort_vitolas(c.get("vitolas") or [])

    # 6. Derive id, default vitola, format.
    # Keep stable ids when a single record's line identity did not change.
    # Only mint cigar_id(...) on merges or when auto-pass/taxonomy changed the line.
    used_ids: set[str] = set()
    alias_pairs = []
    for c in merged:
        brand = c.get("brand") or ""
        line = c.get("line") or ""
        old_ids = [i for i in (c.pop("_old_ids", []) or []) if i]
        raw_lines = c.pop("_raw_lines", None) or []
        line_changed = bool(raw_lines) and not (len(raw_lines) == 1 and raw_lines[0] == line)
        merged_many = len(old_ids) > 1

        if not merged_many and not line_changed and len(old_ids) == 1 and old_ids[0] not in used_ids:
            new_id = old_ids[0]
        else:
            new_id = cigar_id(brand, line)
            base_id = new_id
            n = 2
            while new_id in used_ids:
                new_id = f"{base_id}-{n}"
                n += 1

        if new_id in used_ids:
            new_id = cigar_id(brand, line)
            base_id = new_id
            n = 2
            while new_id in used_ids:
                new_id = f"{base_id}-{n}"
                n += 1

        used_ids.add(new_id)
        for oid in old_ids:
            if oid and oid != new_id:
                alias_pairs.append((oid, new_id))
        c["id"] = new_id
        vitolas = c.get("vitolas") or []
        if vitolas:
            names = {v.get("name") for v in vitolas}
            if c.get("vitola") not in names:
                c["vitola"] = vitolas[0].get("name") or c.get("vitola")
            default = next((v for v in vitolas if v.get("name") == c.get("vitola")), vitolas[0])
            if default.get("format") and not format_missing(default.get("format")):
                c["format"] = default["format"]
            if default.get("priceEUR") is not None:
                c["priceEUR"] = default["priceEUR"]
            if default.get("url"):
                c["priceUrl"] = default["url"]
            if default.get("smokeTimeMin") is not None:
                c["smokeTimeMin"] = default["smokeTimeMin"]

    merged.sort(key=lambda c: ((c.get("brand") or "").lower(), (c.get("line") or "").lower()))

    # 7. Aliases append-only — never alias away a live id
    report["aliases_added"] = []
    live_ids = {c.get("id") for c in merged if c.get("id")}
    existing = load_json(ALIASES_PATH, {}) or {}
    if not isinstance(existing, dict):
        existing = {"aliases": existing}
    aliases = existing.setdefault(
        "aliases", existing if "aliases" not in existing else existing["aliases"]
    )
    if not isinstance(aliases, dict):
        aliases = {}
        existing = {"aliases": aliases}

    removed = []
    for frm in list(aliases.keys()):
        if frm in live_ids:
            del aliases[frm]
            removed.append(frm)
    if removed:
        report["aliases_removed_live_collision"] = removed

    for frm, to in alias_pairs:
        if frm in live_ids:
            report.setdefault("aliases_skipped_live_collision", []).append(
                {"from": frm, "to": to}
            )
            continue
        if frm not in aliases:
            aliases[frm] = to
            report["aliases_added"].append({"from": frm, "to": to})
        elif aliases[frm] != to:
            report.setdefault("alias_conflicts", []).append(
                {"from": frm, "existing": aliases[frm], "new": to}
            )

    # Retarget aliases whose destination was an intermediate id that later merged away.
    retargeted = []
    for frm, to in list(aliases.items()):
        if to in live_ids:
            continue
        # follow alias chain (e.g. long-id → alr-2nd → aged-limited-…)
        seen = {frm, to}
        cur = to
        while cur in aliases and aliases[cur] not in seen:
            cur = aliases[cur]
            seen.add(cur)
            if cur in live_ids:
                break
        if cur in live_ids:
            aliases[frm] = cur
            retargeted.append({"from": frm, "was": to, "to": cur})
            continue
        cands = sorted(
            (lid for lid in live_ids if to == lid or to.startswith(f"{lid}-")),
            key=len,
            reverse=True,
        )
        if not cands and to.endswith("-limited-edition-quinquagenario"):
            alt = "cig-roma-craft-tobac-quinquagenario"
            if alt in live_ids:
                cands = [alt]
        if cands:
            aliases[frm] = cands[0]
            retargeted.append({"from": frm, "was": to, "to": cands[0]})
        else:
            report.setdefault("aliases_broken", []).append({"from": frm, "to": to})
    if retargeted:
        report["aliases_retargeted"] = retargeted

    write_json(ALIASES_PATH, {"aliases": aliases})

    return merged


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--skip-normalize", action="store_true")
    args = ap.parse_args()

    before = CIGARS_PATH.read_text(encoding="utf-8")
    cigars = json.loads(before)
    tax = load_taxonomy_files(applyable_only=True)
    report: dict = {
        "taxonomy_files": len(tax),
        "taxonomy_files_total": len(load_taxonomy_files(applyable_only=False)),
        "input_records": len(cigars),
    }

    # Phase 1 floor (always), then taxonomy overrides + merge/derive.
    cigars = auto_pass(cigars, report)
    cigars = apply_taxonomy(cigars, tax, report)
    if not tax:
        report["note"] = "no applyable taxonomy/*.json (status done|brand-only); auto-pass only"

    report["output_records"] = len(cigars)
    after = json.dumps(cigars, ensure_ascii=False, indent=2) + "\n"
    changed = after != before

    # Keep auto_pass detail bounded in the report file
    auto = report.get("auto_pass") or {}
    report["auto_pass"] = {k: (v if len(v) <= 200 else v[:200] + [{"_truncated": len(v) - 200}]) for k, v in auto.items()}

    write_json(OUT_DIR / "taxonomy_apply_report.json", report)

    if args.check:
        summary = {
            "changed": changed,
            "taxonomy_files": report["taxonomy_files"],
            "input_records": report["input_records"],
            "output_records": report["output_records"],
            "auto_pass_counts": report.get("auto_pass_counts"),
        }
        print(json.dumps(summary, indent=2))
        if changed:
            sys.exit(1)
        return

    if changed:
        CIGARS_PATH.write_text(after, encoding="utf-8")

    if not args.skip_normalize:
        subprocess.run([sys.executable, str(Path(__file__).with_name("normalize-vitolas.py"))], check=True)

    payload = {
        "changed": changed,
        "taxonomy_files": report.get("taxonomy_files"),
        "taxonomy_files_total": report.get("taxonomy_files_total"),
        "input_records": report.get("input_records"),
        "output_records": report.get("output_records"),
        "auto_pass_counts": report.get("auto_pass_counts"),
        "aliases_added": len(report.get("aliases_added") or []),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
