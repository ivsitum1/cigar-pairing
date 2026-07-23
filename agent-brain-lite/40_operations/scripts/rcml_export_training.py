#!/usr/bin/env python3
"""Export Rcml relation registry to training-ready JSONL."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.rcml_registry import (  # noqa: E402
    export_contrastive_jsonl,
    export_instruction_jsonl,
    load_rcml_registry,
)

WORKSPACE = Path(__file__).resolve().parents[2]
DEFAULT_OUT = WORKSPACE / "outputs" / "rcml_training"


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Rcml relation registry for future training")
    parser.add_argument(
        "--format",
        choices=["contrastive", "instruction", "both"],
        default="both",
    )
    parser.add_argument("--registry", default="", help="Path to rcml_relation_registry.json")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--json", action="store_true", help="Print to stdout instead of files")
    args = parser.parse_args()

    reg_path = Path(args.registry).expanduser() if args.registry else None
    registry = load_rcml_registry(reg_path)

    outputs: dict[str, list] = {}
    if args.format in {"contrastive", "both"}:
        outputs["contrastive"] = export_contrastive_jsonl(registry)
    if args.format in {"instruction", "both"}:
        outputs["instruction"] = export_instruction_jsonl(registry)

    if args.json:
        print(json.dumps(outputs, ensure_ascii=False, indent=2))
        return 0

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in outputs.items():
        path = out_dir / f"rcml_{name}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(str(path))
    meta = {
        "source": "30_system/docs/rcml_relation_registry.json",
        "relation_count": len(registry.get("relations") or []),
        "formats": list(outputs.keys()),
    }
    (out_dir / "manifest.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
