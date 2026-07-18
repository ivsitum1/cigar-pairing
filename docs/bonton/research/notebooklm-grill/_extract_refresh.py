"""Extract a single NotebookLM MCP dump into dated refresh markdown."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: _extract_refresh.py <agent-tools-file> <slug>")
        return 2
    fp = Path(sys.argv[1])
    slug = sys.argv[2]
    data = json.loads(fp.read_text(encoding="utf-8"))
    d = data.get("data", data)
    answer = d.get("answer") or d.get("error") or ""
    dest = OUT / f"{slug}-refresh-2026-07-18.md"
    dest.write_text(
        f"# Refresh grill: {slug}\n\n"
        f"URL: {d.get('notebook_url')}\n"
        f"Session: {d.get('session_id')}\n"
        f"Success: {data.get('success')}\n\n"
        f"## Answer\n\n{answer}\n",
        encoding="utf-8",
    )
    count = None
    m = re.search(r"TOTAL COUNT[:\s]*(\d+)|Total Count[:\s]*(\d+)|Ukupno[^:]*:\s*(\d+)", answer, re.I)
    if m:
        count = next(g for g in m.groups() if g)
    print(f"{slug}: ok={data.get('success')} len={len(answer)} count~={count} -> {dest.name}")
    # print first thesis-ish lines
    for line in answer.splitlines()[:25]:
        if re.search(r"title|Total|Count|Thesis|NEW|izvora", line, re.I):
            print(" ", line[:140])
    return 0 if data.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
