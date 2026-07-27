#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print leaf-origin coverage from cigars.json (and optional report file).

  python scripts/report-leaf-coverage.py
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CIGARS = HERE.parent / "src" / "data" / "cigars.json"
REPORT = HERE / "output" / "leaf_origins_coverage.json"


def main() -> None:
    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    n = len(cigars)
    wo = sum(1 for c in cigars if c.get("wrapperOrigin"))
    bo = sum(1 for c in cigars if c.get("binderOrigin"))
    fo = sum(1 for c in cigars if c.get("fillerOrigin"))
    all3 = sum(
        1
        for c in cigars
        if c.get("wrapperOrigin") and c.get("binderOrigin") and c.get("fillerOrigin")
    )
    puro_t = sum(1 for c in cigars if c.get("isPuro") is True)
    puro_f = sum(1 for c in cigars if c.get("isPuro") is False)
    report = {
        "total": n,
        "wrapperOrigin": wo,
        "binderOrigin": bo,
        "fillerOrigin": fo,
        "all_three_origins": all3,
        "pct_all_three": round(100.0 * all3 / n, 1) if n else 0,
        "isPuro_true": puro_t,
        "isPuro_false": puro_f,
        "isPuro_unknown": n - puro_t - puro_f,
        "top_wrapper_origins": Counter(
            c["wrapperOrigin"] for c in cigars if c.get("wrapperOrigin")
        ).most_common(15),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
