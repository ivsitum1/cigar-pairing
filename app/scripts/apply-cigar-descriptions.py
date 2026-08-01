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
ALIASES = HERE.parent / "src" / "data" / "cigarIdAliases.json"


def resolve_id(cigar_id: str, by_id: dict, aliases: dict) -> str | None:
    """Prati cigarIdAliases.json do zivog zapisa (isto kao resolveCigarId u appu).

    Bez ovoga svako spajanje linija (npr. Asylum 13) ostavi kurirani opis da
    visi na starom id-u i obori CI, iako alias vec postoji i tocan je.
    """
    cur = cigar_id
    seen = set()
    while cur not in by_id:
        if cur in seen:
            return None
        seen.add(cur)
        cur = aliases.get(cur)
        if cur is None:
            return None
    return cur


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="ne piši, samo provjeri")
    args = ap.parse_args()

    descriptions = json.loads(SOURCE.read_text(encoding="utf-8"))
    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in cigars}
    aliases = json.loads(ALIASES.read_text(encoding="utf-8")).get("aliases", {})

    missing = sorted(
        cid for cid in descriptions if resolve_id(cid, by_id, aliases) is None
    )
    changed = 0
    for cigar_id, text in descriptions.items():
        canonical = resolve_id(cigar_id, by_id, aliases)
        if canonical is None:
            continue
        cigar = by_id[canonical]
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
