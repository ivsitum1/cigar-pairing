#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Second-pass: quarantine weak auto matches; rewrite auto notes with fixed grammar."""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "youtube"
APP = HERE.parent / "src" / "data"

HAND = {
    "cig-ashton-cabinet-selection",
    "cig-punch-gran-puro",
    "cig-rocky-patel-decade",
    "cig-1502-aniversario-10",
    "cig-aging-room-quattro-nicaragua",
    "cig-ashton-classic",
    "cig-ashton-symmetry",
    "cig-balmoral-serie-signaturas-paso-doble",
    "cig-camacho-connecticut",
    "cig-camacho-corojo",
    "cig-cao-brazilia",
    "cig-davidoff-aniversario",
    "cig-davidoff-nicaragua",
    "cig-davidoff-signature",
    "cig-blackbird-cactus-wren",
}

GENERIC = re.compile(
    r"^(maduro|black|connecticut|natural|corojo|habano|serie [a-z]|no\.?|"
    r"petit|churchill|robusto|toro|lb1|107|year of the)$",
    re.I,
)


def load_draft():
    path = HERE / "youtube-curate-stub-enrichments.py"
    spec = importlib.util.spec_from_file_location("curate", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod.draft_cigar_notes


def main() -> None:
    draft = load_draft()
    enrich_path = DATA / "cigar_enrichments.json"
    q_path = DATA / "enrichment_quarantine.json"
    cigars_path = APP / "cigars.json"

    payload = json.loads(enrich_path.read_text(encoding="utf-8"))
    enrich = payload["enrichments"]
    cigars_list = json.loads(cigars_path.read_text(encoding="utf-8"))
    cigars = {c["id"]: c for c in cigars_list}
    quarantine = json.loads(q_path.read_text(encoding="utf-8"))

    to_drop: list[tuple[str, str]] = []
    for cid, entry in list(enrich.items()):
        if cid in HAND:
            continue
        row = cigars.get(cid) or {}
        line = (row.get("line") or "").strip()
        brand = (row.get("brand") or "").strip()
        reason = None
        if GENERIC.match(line) or len(line) < 4:
            reason = "postcheck-generic-or-short-line"
        elif brand.lower() == line.lower():
            reason = "postcheck-brand-eq-line"
        elif "coffin" in line.lower() or "family series" in line.lower():
            reason = "postcheck-ultra-specific-variant"
        elif re.search(r"\b(year of the|no\.?)\b", line, re.I) and len(line) < 20:
            reason = "postcheck-truncated-line"
        if reason:
            to_drop.append((cid, reason))
            quarantine["items"].append(
                {
                    "kind": "cigar",
                    "id": cid,
                    "videoId": (entry.get("sourceVideoIds") or [None])[0],
                    "reason": reason,
                    "matchedName": f"{brand} {line}".strip(),
                    "title": None,
                    "channelId": None,
                }
            )
            del enrich[cid]

    # Restore notes for dropped ids from last committed cigars.json when possible
    try:
        raw = subprocess.check_output(
            ["git", "show", "HEAD:app/src/data/cigars.json"],
            cwd=str(HERE.parent.parent),
        )
        head_cigars = {c["id"]: c for c in json.loads(raw.decode("utf-8"))}
    except Exception:
        head_cigars = {}

    for cid, _reason in to_drop:
        row = cigars.get(cid)
        if not row:
            continue
        if cid in head_cigars and "notes" in head_cigars[cid]:
            row["notes"] = head_cigars[cid]["notes"]
        elif "notes" in row:
            # leave stub-like placeholder rather than wrong template
            del row["notes"]

    # Rewrite remaining auto drafts with fixed grammar
    for cid, entry in enrich.items():
        if cid in HAND:
            continue
        row = cigars[cid]
        entry["notes"] = draft(row, row.get("brand") or "", row.get("line") or "")

    quarantine["counts"]["cigarEnrichmentsTotal"] = len(enrich)
    quarantine["counts"]["cigarPostcheckDropped"] = len(to_drop)
    quarantine["counts"]["cigarApprovedShipped"] = len(enrich)

    enrich_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    q_path.write_text(json.dumps(quarantine, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cigars_path.write_text(json.dumps(cigars_list, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("dropped", len(to_drop), [x[0] for x in to_drop])
    print("remaining_enrichments", len(enrich))


if __name__ == "__main__":
    main()
