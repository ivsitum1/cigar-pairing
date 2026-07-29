#!/usr/bin/env python3
"""Upisuje kurirane opise iz cigar_descriptions.json u src/data/cigars.json.

Idempotentno. Pokreni nakon svake regeneracije kataloga (pipeline prepisuje
`notes` generiranim sazetkom atributa):

    python3 scripts/cigar_descriptions.py        # uredi .py pa regeneriraj JSON
    python3 scripts/apply-cigar-descriptions.py  # upisi u katalog

`--check` ne mijenja nista, samo javlja bi li se sto promijenilo (za CI).
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CIGARS = HERE.parent / "src" / "data" / "cigars.json"
SOURCE = HERE / "cigar_descriptions.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="ne piši, samo provjeri")
    args = ap.parse_args()

    descriptions = json.loads(SOURCE.read_text(encoding="utf-8"))
    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in cigars}

    missing = sorted(set(descriptions) - set(by_id))
    changed = 0
    for cigar_id, text in descriptions.items():
        cigar = by_id.get(cigar_id)
        if cigar is None:
            continue
        if cigar.get("notes") != text:
            cigar["notes"] = {"hr": text["hr"], "en": text["en"]}
            changed += 1

    if missing:
        print(f"UPOZORENJE: {len(missing)} id-ova nema u katalogu:", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)

    if args.check:
        if changed:
            print(f"--check: {changed} opisa nije primijenjeno", file=sys.stderr)
            return 1
        print(f"--check: svih {len(descriptions)} opisa je na mjestu")
        return 0

    if changed:
        CIGARS.write_text(
            json.dumps(cigars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(f"Primijenjeno {changed} opisa ({len(descriptions)} u izvoru)")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
