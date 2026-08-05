#!/usr/bin/env python3
"""Fold broken market vitola lines into multi-vitola records.

Many catalogSource=="market" cigars from Neptune Cigar shop imports encode the
vitola shape name inside the line name (e.g. "Quattro F55 Concerto" for a line
that should be "Quattro F55" with a "Concerto" vitola). This creates separate
cigar records for what are really just different sizes of one line.

Fold criterion — ALL of the following must hold for every member of a group:
  - catalogSource == "market"
  - wrapper == "—"           (Neptune template import: no wrapper data)
  - Neptune note in notes    (the template note from build-market-cigars.py)
  - exactly 1 vitola
  - formatEstimated == True  (shop only guessed the size; no stated dimension)
  - line has at least 2 words

Grouping key: (brand, line_without_last_word). A group of 2+ qualifying records
is folded: the last word of each member's line becomes its vitola name, and all
vitolas are gathered onto a single survivor record.

When cigar_id(brand, base) matches an existing non-member record, the new
vitolas are merged into that record rather than creating a new one.

Every absorbed ID — including the new survivor's own re-derived ID — is written
as an alias in cigarIdAliases.json (append-only; existing aliases are never
overwritten).

Usage (run from app/):
  python scripts/fold-market-vitolas.py            # apply fold + write files
  python scripts/fold-market-vitolas.py --check    # CI gate: exit 1 if stale
  python scripts/fold-market-vitolas.py --dry-run  # print report, no writes
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from taxonomy_lib import (  # noqa: E402
    ALIASES_PATH,
    CIGARS_PATH,
    cigar_id,
    load_json,
    write_json,
)

NEPTUNE_MARKER = "Neptune"
DASH = "\u2014"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_neptune_template(c: dict) -> bool:
    notes = c.get("notes") or {}
    return any(NEPTUNE_MARKER in str(v) for v in notes.values())


def _is_fold_candidate(c: dict) -> bool:
    return (
        c.get("catalogSource") == "market"
        and c.get("wrapper") == DASH
        and _is_neptune_template(c)
        and len(c.get("vitolas") or []) == 1
        and bool(c.get("formatEstimated"))
    )


# ---------------------------------------------------------------------------
# Core algorithm
# ---------------------------------------------------------------------------

def build_groups(cigars: list) -> dict[tuple[str, str], list]:
    """Return {(brand, base): [(cigar, last_word), ...]} for groups of 2+."""
    raw: dict = defaultdict(list)
    for c in cigars:
        if not _is_fold_candidate(c):
            continue
        line = c.get("line") or ""
        parts = line.rsplit(None, 1)
        if len(parts) != 2:
            continue
        base, last = parts
        raw[(c.get("brand") or "", base)].append((c, last))
    return {k: v for k, v in raw.items() if len(v) >= 2}


def _sort_key(pair):
    c, _ = pair
    # Prefer records with more fields set (non-None, non-empty)
    score = sum(1 for v in c.values() if v not in (None, "", [], {}))
    return (-score, c.get("id") or "")


def _merge_vitola_fields(dst: dict, src: dict) -> None:
    """Fill missing shop fields on dst from src (same rules as apply-taxonomy.merge_vitolas)."""
    for field in ("format", "smokeTimeMin", "priceEUR", "url", "shape"):
        if dst.get(field) in (None, "", DASH) and src.get(field) not in (None, "", DASH):
            dst[field] = src[field]
    rl = dict(dst.get("regionLinks") or {})
    for reg, link in (src.get("regionLinks") or {}).items():
        if reg not in rl:
            rl[reg] = link
        elif reg == "HR" and link.get("url") and "humidor" in (link.get("url") or ""):
            rl[reg] = link
    if rl:
        dst["regionLinks"] = rl


def apply_fold(
    cigars: list,
    groups: dict[tuple[str, str], list],
    aliases: dict[str, str],
) -> tuple[list, list]:
    """Fold groups into cigars list; return (new_cigars, alias_pairs_added).

    Mutates ``aliases`` in place (append-only — existing entries are kept).
    """
    by_id: dict[str, dict] = {c["id"]: c for c in cigars}
    absorbed_ids: set[str] = set()
    new_records: list[dict] = []
    alias_pairs: list[tuple[str, str]] = []

    for (brand, base), members in sorted(groups.items()):
        survivor_id = cigar_id(brand, base)
        member_ids = {c["id"] for c, _ in members}

        # Determine survivor: prefer an existing non-member record with survivor_id,
        # then build a new record from the member with the richest data.
        if survivor_id in by_id and survivor_id not in member_ids:
            survivor = by_id[survivor_id]
            is_new_record = False
        else:
            sorted_members = sorted(members, key=_sort_key)
            survivor = copy.deepcopy(sorted_members[0][0])
            survivor["line"] = base
            old_id = survivor["id"]
            survivor["id"] = survivor_id
            # Clear the vitolas list; we'll rebuild it from all members.
            survivor["vitolas"] = []
            survivor.pop("vitola", None)
            is_new_record = True
            # The first member's original id also needs an alias
            if old_id != survivor_id:
                alias_pairs.append((old_id, survivor_id))
            by_id[survivor_id] = survivor

        vitolas_by_name_lower = {
            (v.get("name") or "").lower(): v
            for v in (survivor.get("vitolas") or [])
        }

        for c, last_word in sorted(members, key=lambda x: x[0]["id"]):
            old_vit = copy.deepcopy((c.get("vitolas") or [{}])[0])
            new_vit_name = last_word
            key = new_vit_name.lower()

            if key not in vitolas_by_name_lower:
                # Promote generic shape name (e.g. "Robusto") to vitola.shape
                generic = old_vit.get("name") or ""
                if generic and generic.lower() != key:
                    old_vit["shape"] = generic
                old_vit["name"] = new_vit_name
                if not survivor.get("vitolas"):
                    survivor["vitolas"] = []
                survivor["vitolas"].append(old_vit)
                vitolas_by_name_lower[key] = old_vit
            else:
                existing = vitolas_by_name_lower[key]
                generic = old_vit.get("name") or ""
                if generic and generic.lower() != key:
                    if existing.get("shape") in (None, "", DASH):
                        existing["shape"] = generic
                _merge_vitola_fields(existing, old_vit)

            # All member IDs (including the one we used as the base) get aliased
            if c["id"] != survivor_id:
                alias_pairs.append((c["id"], survivor_id))
                absorbed_ids.add(c["id"])
            elif not is_new_record:
                # Existing survivor absorbs itself: just mark it absorbed
                absorbed_ids.add(c["id"])

        # Set default vitola after all are gathered
        vitolas = survivor.get("vitolas") or []
        if vitolas and not survivor.get("vitola"):
            survivor["vitola"] = vitolas[0].get("name")

        if is_new_record:
            new_records.append(survivor)

    # Write aliases (append-only)
    for frm, to in alias_pairs:
        if frm != to and frm not in aliases:
            aliases[frm] = to

    # Build output: drop absorbed members from original list; add new survivors
    out_cigars = [c for c in cigars if c["id"] not in absorbed_ids]
    out_cigars.extend(new_records)
    out_cigars.sort(
        key=lambda c: ((c.get("brand") or "").lower(), (c.get("line") or "").lower())
    )
    return out_cigars, alias_pairs


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="CI gate: exit 1 if fold is not yet applied")
    ap.add_argument("--dry-run", action="store_true", help="Print report without writing files")
    args = ap.parse_args()

    cigars_before = CIGARS_PATH.read_text(encoding="utf-8")
    cigars = json.loads(cigars_before)

    groups = build_groups(cigars)
    group_count = len(groups)
    record_count = sum(len(v) for v in groups.values())
    absorbed_count = sum(len(v) - 1 for v in groups.values())

    if not groups:
        print(json.dumps({"groups": 0, "records": 0, "absorbed": 0, "changed": False}))
        return 0

    aliases_data = load_json(ALIASES_PATH, {"aliases": {}})
    if not isinstance(aliases_data, dict):
        aliases_data = {"aliases": {}}
    aliases_data.setdefault("aliases", {})
    aliases = aliases_data["aliases"]

    new_cigars, alias_pairs = apply_fold(cigars, groups, aliases)

    after = json.dumps(new_cigars, ensure_ascii=False, indent=2) + "\n"
    changed = after != cigars_before

    report = {
        "groups": group_count,
        "records_in_groups": record_count,
        "absorbed": absorbed_count,
        "new_aliases": len(alias_pairs),
        "changed": changed,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.check:
        if changed:
            print(
                "fold-market-vitolas: stale — run without --check to apply the fold.",
                file=sys.stderr,
            )
            sys.exit(1)
        return 0

    if args.dry_run:
        print("(dry-run — no files written)")
        return 0

    if changed:
        CIGARS_PATH.write_text(after, encoding="utf-8")
        aliases_data["aliases"] = dict(sorted(aliases.items()))
        write_json(ALIASES_PATH, aliases_data)
        print(f"Wrote {CIGARS_PATH.name} ({len(new_cigars)} records) and {ALIASES_PATH.name} (+{len(alias_pairs)} aliases)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
