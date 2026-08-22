#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print captionStatus tally per channel (local ops).

Usage: python scripts/youtube-caption-status.py
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from youtube_common import load_channels, OUTPUT_ROOT


def main() -> None:
    tot = Counter()
    for ch in sorted(load_channels(), key=lambda c: (c.get("priority", 99), c["id"])):
        cid = ch["id"]
        invp = OUTPUT_ROOT / cid / "inventory.json"
        if not invp.is_file():
            print(f"{cid}\tNO_INVENTORY")
            continue
        inv = json.loads(invp.read_text(encoding="utf-8"))
        c = Counter((v.get("captionStatus") or "unset") for v in inv.get("videos") or [])
        tot.update(c)
        n = sum(c.values())
        pending = c.get("missing", 0) + c.get("error", 0)
        print(
            f"{cid}\tn={n}\tok={c.get('ok', 0)}\terr={c.get('error', 0)}"
            f"\tmiss={c.get('missing', 0)}\tunavail={c.get('unavailable', 0)}\tpending={pending}"
        )
    print("---")
    print("TOTAL", sum(tot.values()), dict(tot))
    print("PENDING(missing+error)", tot.get("missing", 0) + tot.get("error", 0))


if __name__ == "__main__":
    main()
