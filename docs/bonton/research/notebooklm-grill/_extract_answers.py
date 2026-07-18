"""Extract NotebookLM MCP answer payloads into markdown files."""
from __future__ import annotations

import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent
AGENT_TOOLS = Path(
    r"C:\Users\Admin\.cursor\projects\c-Users-Admin-OneDrive-Dokumenti-09-OSOBNO-cigar-and-rum\agent-tools"
)

PAIRS: list[tuple[str, str]] = [
    ("76c61cfc-6ea8-43f1-b8ec-c44339828910.txt", "2707d3fe-cigar-101"),
    ("20e91912-37a6-411c-acd5-a9d367237d43.txt", "7d62a4d2-cigar-family"),
    ("83a36f00-022e-4d58-996a-cec0be4024d5.txt", "c4044fbd"),
    ("17096be4-96bf-45cf-8ac6-ef46a1334912.txt", "5b8ae55e-holts"),
    ("b8f64e40-33c2-4dce-b18d-abb4ee93aa88.txt", "e4921359"),
    ("5b1a0468-ee2d-41ef-a2f9-c64a4d7a4696.txt", "18ea7df7-rum-101"),
    ("5da0d3ee-a7dc-4a70-96ec-fb4e265f7733.txt", "5d9870a0"),
]


def extract(fp: Path, slug: str) -> None:
    data = json.loads(fp.read_text(encoding="utf-8"))
    d = data.get("data", data)
    answer = d.get("answer") or d.get("error") or ""
    url = d.get("notebook_url", "")
    text = (
        f"# Grill: {slug}\n\n"
        f"URL: {url}\n"
        f"Session: {d.get('session_id')}\n"
        f"Success: {data.get('success')}\n\n"
        f"## Answer\n\n{answer}\n"
    )
    dest = OUT / f"{slug}-discovery.md"
    dest.write_text(text, encoding="utf-8")
    title = ""
    for line in answer.splitlines()[:40]:
        if re.search(r"Notebook [Tt]itle|Source Inventory|\"[^\"]+\" notebook", line):
            title = line.strip()[:140]
            break
    print(f"{slug}: ok={data.get('success')} len={len(answer)}")
    if title:
        print(f"  {title}")


def main() -> int:
    for name, slug in PAIRS:
        fp = AGENT_TOOLS / name
        if not fp.exists():
            print(f"missing {name}")
            continue
        extract(fp, slug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
