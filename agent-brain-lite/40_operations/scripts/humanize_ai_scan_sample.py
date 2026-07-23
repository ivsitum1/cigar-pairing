#!/usr/bin/env python3
"""Before/after pattern scan verification sample."""
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[2] / "30_system" / "behavior_rules" / "tools"
sys.path.insert(0, str(TOOLS))

from ai_pattern_scan import scan_text  # noqa: E402

BEFORE = (
    "It is important to note that this groundbreaking study delves into the "
    "intricate tapestry of perioperative fluid management. Furthermore, the "
    "findings underscore the necessity of a nuanced approach and serve as a "
    "testament to vibrant clinical innovation. In conclusion, outcomes were "
    "lightweight, flexible, and low-cost."
)

AFTER = (
    "We analyzed perioperative fluid management in 84 adults after major abdominal "
    "surgery. Balanced crystalloid use was associated with fewer electrolyte "
    "disturbances (p=0.02). The protocol is feasible in our ICU. One limitation "
    "was single-center design."
)

OUT = Path(__file__).resolve().parents[2] / "outputs" / "notebooklm" / "humanize_ai_scan_sample.json"


def main() -> None:
    before = scan_text(BEFORE)
    after = scan_text(AFTER)
    payload = {
        "before": before.to_dict(),
        "after": after.to_dict(),
        "delta_score": round(before.score - after.score, 4),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} (delta_score={payload['delta_score']})")


if __name__ == "__main__":
    main()
