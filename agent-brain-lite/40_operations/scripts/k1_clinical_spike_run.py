#!/usr/bin/env python3
"""Execute K1 clinical spike checklist (paper-gated; no cloud PHI)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
SPIKE = WORKSPACE / "30_system" / "docs" / "K1_CLINICAL_RESEARCH_SPIKE.md"
BOOKS = WORKSPACE / "20_knowledge" / "wiki" / "sources" / "books_md"
OUT = WORKSPACE / "outputs" / "k1" / "spike_status.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="K1 clinical spike status report")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    sample_pdfs = list(BOOKS.rglob("*.md"))[:3]
    status = {
        "spike_doc": str(SPIKE.relative_to(WORKSPACE)),
        "primary_paper_verified": False,
        "sample_corpus_count": len(sample_pdfs),
        "sample_paths": [str(p.relative_to(WORKSPACE)) for p in sample_pdfs],
        "go_implementation": False,
        "blockers": [
            "Primary K1 paper URL not VERIFIED in notebooklm_harness_skilltree_external_verification.json",
            "Privacy review required before cloud upload",
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(status, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(f"K1 spike: GO={status['go_implementation']} samples={status['sample_corpus_count']}")
    return 1 if not status["go_implementation"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
