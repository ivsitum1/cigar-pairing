#!/usr/bin/env python3
"""Train sklearn verifier assist model from usage ledger + eval cases."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from brain_assist.verifier_ml import (  # noqa: E402
    MIN_LABELED_ROWS,
    collect_training_rows,
    maybe_incremental_train,
    train_model,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Train verifier sklearn model")
    parser.add_argument("--min-rows", type=int, default=MIN_LABELED_ROWS)
    parser.add_argument("--output", default="", help="Model output path (.joblib)")
    parser.add_argument("--incremental", action="store_true", help="Use maybe_incremental_train (default)")
    parser.add_argument("--force", action="store_true", help="Force train when enough rows")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.incremental or (not args.force and not args.output):
        result = maybe_incremental_train(force=args.force)
    else:
        rows = collect_training_rows()
        out = Path(args.output).expanduser() if args.output else None
        result = train_model(rows, out_path=out, min_rows=args.min_rows)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
