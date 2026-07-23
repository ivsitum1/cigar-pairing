from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INV = ROOT / "30_system" / "docs" / "local_source_inventory.csv"
OUT = ROOT / "30_system" / "docs" / "local_source_classified.csv"

PATTERNS = {
    "anesthesiology": r"anesth|anestez|regional|nerve|periop|sevo|propofol|airway",
    "emergency": r"emergency|hitn|trauma|atls|urgent",
    "intensive_care": r"icu|intensive|critical\s?care|ventilat|ards|respirat",
    "statistics": r"statist|bayes|meta[ -]?anal|cochrane|regression|trial|consort|prisma|strobe|stard|tripod|r[ -]?program",
    "scientific_writing": r"writing|manuscript|paper|thesis|dissertation|editorial|review|guideline|reporting",
}


def main() -> None:
    compiled = {k: re.compile(v, re.IGNORECASE) for k, v in PATTERNS.items()}
    rows: list[dict[str, str]] = []
    with INV.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = f"{row.get('path', '')} {row.get('name', '')}"
            domains = [d for d, pattern in compiled.items() if pattern.search(text)]
            if domains:
                row["domains"] = ";".join(domains)
                rows.append(row)

    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "ext", "name", "dir", "domains"])
        writer.writeheader()
        writer.writerows(rows)

    counts = {k: 0 for k in PATTERNS}
    for row in rows:
        for d in row["domains"].split(";"):
            counts[d] += 1
    print(json.dumps({"matched_rows": len(rows), "domain_hits": counts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
