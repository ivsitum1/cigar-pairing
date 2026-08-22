#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Summarize cigar match proposals into a human review queue.

Filters: confidence >= min, matchedKey in title, min key length, global dedupe by cigarId.

Usage:
  python scripts/summarize-youtube-cigar-proposals.py
  python scripts/summarize-youtube-cigar-proposals.py --min-confidence 0.9 --prefer-stubs --limit 50
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

from summarize_youtube_cigar_lib import build_queue, collect_proposals
from youtube_common import CIGARS_PATH, OUTPUT_ROOT, load_json, save_json, today_iso

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

QUEUE_PATH = OUTPUT_ROOT / "cigar_review_queue.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build cigar YouTube review queue")
    parser.add_argument("--min-confidence", type=float, default=0.85)
    parser.add_argument("--min-key-len", type=int, default=8)
    parser.add_argument("--stub-en-max", type=int, default=80, help="EN note length treated as stub")
    parser.add_argument("--require-in-title", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--prefer-stubs", action="store_true", help="Only lines with empty/short notes")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--out", type=Path, default=QUEUE_PATH)
    args = parser.parse_args()

    proposals = collect_proposals(
        min_confidence=args.min_confidence,
        min_key_len=args.min_key_len,
        require_in_title=args.require_in_title,
    )
    cigars = load_json(CIGARS_PATH, [])
    cigars_by_id = {c["id"]: c for c in cigars if c.get("id")}
    queue = build_queue(
        proposals,
        cigars_by_id,
        stub_en_max=args.stub_en_max,
        prefer_stubs=args.prefer_stubs,
    )
    if args.limit is not None:
        queue = queue[: args.limit]

    out = {
        "generatedAt": today_iso(),
        "filters": {
            "minConfidence": args.min_confidence,
            "minKeyLen": args.min_key_len,
            "requireInTitle": args.require_in_title,
            "stubEnMax": args.stub_en_max,
            "preferStubs": args.prefer_stubs,
        },
        "proposalCount": len(proposals),
        "queueCount": len(queue),
        "queue": queue,
        "note": "Review queue only — add approved copy to scripts/data/youtube/cigar_enrichments.json",
    }
    save_json(args.out, out)
    print(
        json.dumps(
            {
                "out": str(args.out),
                "proposalCount": len(proposals),
                "queueCount": len(queue),
                "stubInQueue": sum(1 for r in queue if r["isStubNote"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
