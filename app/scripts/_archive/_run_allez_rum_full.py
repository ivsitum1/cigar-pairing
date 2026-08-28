# -*- coding: utf-8 -*-
"""Run ingest + restore in one process; write backup outside sync races."""
from __future__ import annotations

import json
import runpy
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "data" / "rums.json"
OUT = Path(__file__).resolve().parent / "output"


def main() -> None:
    before = len(json.loads(SRC.read_text(encoding="utf-8")))
    print("before", before)
    runpy.run_path(str(Path(__file__).parent / "ingest-allez-rum-gaps.py"), run_name="__main__")
    mid = len(json.loads(SRC.read_text(encoding="utf-8")))
    print("after ingest", mid)
    runpy.run_path(str(Path(__file__).parent / "restore-allez-rum-batches.py"), run_name="__main__")
    runpy.run_path(str(Path(__file__).parent / "_add_jamaica.py"), run_name="__main__")
    data = json.loads(SRC.read_text(encoding="utf-8"))
    print("after jamaica", len(data))
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = OUT / f"rums-allez-backup-{stamp}.json"
    shutil.copy2(SRC, bak)
    # also keep a stable name for recovery
    stable = OUT / "rums-allez-latest.json"
    shutil.copy2(SRC, stable)
    print("backup", bak)
    print("stable", stable)


if __name__ == "__main__":
    main()
