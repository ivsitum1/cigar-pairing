#!/usr/bin/env python3
"""Reset harness v2 grill slots for live re-grill (keep first 3 live pass1 answers)."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
OUT = WORKSPACE / "outputs" / "notebooklm"
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
bak = OUT / "_archive" / f"pre_regrill_{ts}"
bak.mkdir(parents=True, exist_ok=True)

for name in ("harness_v2_query_batch.json", "harness_v2_query_batch_pass2.json"):
    src = OUT / name
    if src.exists():
        shutil.copy2(src, bak / name)

p1 = json.loads((OUT / "harness_v2_query_batch.json").read_text(encoding="utf-8"))
cleared = 0
for i, row in enumerate(p1.get("results", [])):
    prov = row.get("provenance", "")
    if i >= 3 or prov != "live_notebooklm":
        p1["results"][i] = {"question": row["question"], "result": None}
        cleared += 1
p1.pop("merge_stats", None)
p1["regrill_started"] = ts
(OUT / "harness_v2_query_batch.json").write_text(
    json.dumps(p1, ensure_ascii=False, indent=2), encoding="utf-8"
)

cfg = json.loads(
    (WORKSPACE / "30_system/docs/reference/notebooklm_harness_v2_questions.json").read_text(
        encoding="utf-8"
    )
)
p2 = {
    "notebook_url": cfg["notebook_url"],
    "notebook_id": cfg["notebook_id"],
    "regrill_started": ts,
    "results": [{"question": q, "result": None} for q in cfg["pass2"]],
}
(OUT / "harness_v2_query_batch_pass2.json").write_text(
    json.dumps(p2, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"Backup: {bak}")
print(f"Pass1 cleared slots: {cleared}")
print(f"Pass2 reset: {len(p2['results'])} questions")
