# -*- coding: utf-8 -*-
"""Remove superseded combined rum entries after Allez splits.

Rules:
- Combined age like 12/18: if BOTH halves exist as separate SKUs → delete combined.
- If only ONE half exists → rename combined to the missing half.
- Brand META superseded by specific Allez SKUs → delete META.
- Never keep packaging-only 'sa 2 čaše' SKUs (none should be present).
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "src" / "data" / "rums.json"
OUT = Path(__file__).resolve().parent / "output"

# combined_id → list of specific ids that replace it (delete if all present)
DELETE_IF_ALL = {
    "rum-flor-de-cana-12-18": ["rum-flor-de-cana-12", "rum-flor-de-cana-18"],
    "rum-opthimus-15-18-21-solera": [
        "rum-opthimus-15-res-laude",
        "rum-opthimus-18-cum-laude",
        "rum-opthimus-21-magna-cum-laude",
    ],
    # brand META fully covered by Allez specifics
    "rum-trois-rivieres-agricole": [
        "rum-trois-rivieres-cannes-brulees",
        "rum-trois-rivieres-cuvee-ocean",
        "rum-trois-rivieres-cuvee-moulin",
    ],
    "rum-admiral-rodney-st-lucia": [
        "rum-admiral-rodney-hms-formidable",
        "rum-admiral-rodney-hms-monarch",
    ],
    "rum-compagnie-des-indes-razne": [
        "rum-cdi-caraibes",
        "rum-cdi-latino-5",
        "rum-cdi-west-indies-8",
    ],
    "rum-chairman-s-reserve-sv-lucija": [
        "rum-chairmans-legacy",
        "rum-chairmans-forgotten-casks",
    ],
    "rum-goslings-black-tot-navy": [
        "rum-goslings-black-seal",
        "rum-black-tot-rum",
    ],
}

# Orphan halves / duplicate META to delete if sibling exists
DELETE_IF_SIBLING = {
    "rum-7": "rum-banks-7-golden-age",  # leftover from Banks 5/7 slash split
    "rum-single-estate-reserve": "rum-worthy-park-single-estate",
}

# Rename combined → missing half when only one specific exists
# (combined_id, [(specific_id, rename_fields), ...])
RENAME_IF_ONLY_ONE: dict[str, list[tuple[str, dict]]] = {
    # Template for future: if flor-12 existed but not flor-18, rename 12-18 → 18.
    # Currently both exist so DELETE_IF_ALL handles flor/opthimus.
}


def main() -> None:
    rums = json.loads(P.read_text(encoding="utf-8"))
    by = {r["id"]: r for r in rums}
    remove: set[str] = set()
    actions: list[str] = []

    for combined, specifics in DELETE_IF_ALL.items():
        if combined not in by:
            continue
        present = [s for s in specifics if s in by]
        missing = [s for s in specifics if s not in by]
        if not missing:
            remove.add(combined)
            actions.append(f"DELETE {combined} (all of {specifics} exist)")
        elif len(present) >= 1 and len(missing) == 1 and combined in (
            "rum-flor-de-cana-12-18",
            "rum-opthimus-15-18-21-solera",
        ):
            # Age-slash: rename combined to the single missing age
            miss = missing[0]
            if miss in by:
                remove.add(combined)
                actions.append(f"DELETE {combined} (missing half already exists as {miss})")
            else:
                old = by[combined]
                old["id"] = miss
                # minimal rename from id pattern
                if "flor" in miss and "18" in miss:
                    old["name"] = "Flor de Caña Centenario 18 YO"
                    old["status"] = None
                elif "flor" in miss and "12" in miss:
                    old["name"] = "Flor de Caña Centenario 12 YO"
                    old["status"] = None
                actions.append(f"RENAME {combined} → {miss}")
                by[miss] = old
                del by[combined]
        else:
            actions.append(
                f"KEEP {combined} (missing specifics: {missing})"
            )

    for orphan, sibling in DELETE_IF_SIBLING.items():
        if orphan in by and sibling in by:
            remove.add(orphan)
            actions.append(f"DELETE {orphan} (sibling {sibling} exists)")

    # Drop any accidental 2-glass packaging SKUs
    for r in rums:
        name = (r.get("name") or "").lower()
        if "sa 2 čaš" in name or "s 2 čaš" in name or "with 2 glass" in name:
            remove.add(r["id"])
            actions.append(f"DELETE {r['id']} (packaging 2 glasses)")

    out = []
    seen = set()
    for r in rums:
        rid = r["id"]
        if rid in remove:
            continue
        if rid in seen:
            continue
        seen.add(rid)
        # Clear META on bottles that are now concrete Allez SKUs with own price
        if r.get("status") == "META" and r.get("priceEUR") and rid.startswith(
            (
                "rum-doorly-s-",
                "rum-appleton-",
                "rum-hampden-",
                "rum-worthy-park-",
                "rum-smith-cross",
                "rum-veritas-",
                "rum-banks-",
                "rum-mount-gay-",
                "rum-flor-de-cana-",
                "rum-clement-",
                "rum-hse-",
                "rum-rhum-j-m-",
                "rum-saint-james-",
            )
        ):
            if rid not in (
                "rum-mount-gay-1703",  # still a line META note
            ):
                # only clear if notes don't say Meta-unos
                notes = (r.get("notes") or {}).get("hr") or ""
                if "Meta-unos" not in notes and "meta-unos" not in notes.lower():
                    r["status"] = None
                    actions.append(f"CLEAR META {rid}")
        out.append(r)

    P.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(P, OUT / f"rums-allez-backup-{stamp}.json")
    shutil.copy2(P, OUT / "rums-allez-latest.json")

    for a in actions:
        print(a)
    print(f"removed={len(remove)} total={len(out)}")


if __name__ == "__main__":
    main()
