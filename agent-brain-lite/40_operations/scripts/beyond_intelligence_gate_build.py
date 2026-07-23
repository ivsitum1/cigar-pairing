#!/usr/bin/env python3
"""Build Beyond Intelligence gate report from Playwright query batch + external ledger."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE / "40_operations" / "scripts"))

from notebooklm_bridge import export_normalize, gate_report  # noqa: E402

NOTEBOOK_ID = "b8896972-fd70-40ca-9456-15c8ff41e72a"
QUERY_BATCH = WORKSPACE / "outputs" / "notebooklm" / "beyond_intelligence_query_batch.json"
GATE_OUT = WORKSPACE / "outputs" / "notebooklm" / "beyond_intelligence_gate_report.json"
EXTERNAL = WORKSPACE / "30_system" / "docs" / "notebooklm_beyond_intelligence_external_verification.json"


def _load_query_batch(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Query batch missing: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    turns = []
    for i, item in enumerate(data.get("results") or []):
        result = item.get("result") or {}
        turns.append(
            {
                "turn_index": i,
                "question": item.get("question", ""),
                "answer": result.get("answer", ""),
                "citations": None,
                "success": result.get("success", False),
            }
        )
    return {
        "notebook_id": data.get("notebook_id") or NOTEBOOK_ID,
        "notebook_title": data.get("notebook_title") or "Beyond Intelligence",
        "notebook_url": data.get("notebook_url")
        or f"https://notebooklm.google.com/notebook/{NOTEBOOK_ID}",
        "exported_at": data.get("exported_at", ""),
        "chat_turns": turns,
    }


def build_gate(query_path: Path | None = None) -> dict:
    batch_path = query_path or QUERY_BATCH
    normalized = export_normalize(_load_query_batch(batch_path), NOTEBOOK_ID)
    procedural = gate_report(normalized)
    external = {}
    if EXTERNAL.is_file():
        external = json.loads(EXTERNAL.read_text(encoding="utf-8"))

    merged = {
        **procedural,
        "notebook_id": NOTEBOOK_ID,
        "notebook_title": normalized.get("notebook_title") or "Beyond Intelligence",
        "notebook_url": normalized.get("notebook_url"),
        "external_ledger": str(EXTERNAL.relative_to(WORKSPACE)).replace("\\", "/"),
        "prd": "30_system/docs/prd_beyond_intelligence_incorporation.json",
        "method": "Playwright grill + notebooklm_bridge gate_report + external verification merge",
        "scope_in": [
            "failure_mode tags",
            "episodic-first MEMORY.md policy",
            "memory mixture routing",
            "verifier usage ledger",
        ],
        "scope_out": ["Mem0/StructMem replacement", "neural memory runtime"],
        "implementation_priorities": {
            "P0": ["TRAJECTORY_RL_POLICY episodic-first", "VERIFIER_LEARNING_LOOP.md"],
            "P1": ["MEMORY_MIXTURE_ROUTING.md", "failure_mode ingest", "memfail_adapter.py"],
            "P2": ["memfail_brain_smoke.py", "semantic forgetting docs"],
        },
        "external_claims_verified": len(external.get("claims") or []),
        "playwright_turns": len(normalized.get("chat_turns") or []),
        "playwright_success_count": sum(
            1 for t in (batch_path and json.loads(batch_path.read_text()).get("results") or [])
            if (t.get("result") or {}).get("success")
        ),
    }
    if procedural.get("verdict") == "NO-GO" and external.get("gate_verdict") == "GO":
        merged["verdict"] = "GO_WITH_NOTES"
        merged["notes"] = list(procedural.get("notes") or []) + [
            "Procedural gate NO-GO overridden partially by external arXiv verification.",
        ]
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Beyond Intelligence gate report")
    parser.add_argument("--input", default=str(QUERY_BATCH))
    parser.add_argument("--output", default=str(GATE_OUT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = build_gate(Path(args.input))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
