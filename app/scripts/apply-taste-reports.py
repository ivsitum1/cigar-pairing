#!/usr/bin/env python3
"""Zabiljezeni dojmovi -> snaga i tijelo u cigars.json.

Ono sto je netko stvarno popusio nadjacava svaku procjenu — opis trgovine,
heuristiku pokrova, sve. Zato ovaj korak ide POSLIJE svih spajanja iz trgovina
i zapis oznacava kao `strengthFromTasting`, cime ga merge-neptune-profiles.py
vise ne dira (on radi samo nad `profileEstimated`).

Kad istu cigaru ocijeni vise ljudi, uzima se prosjek — zaokruzen na najblizi
cijeli broj, uz remi prema gore (dvoje ljudi, 3 i 4, daje 4: tko je osjetio
vise, osjetio je nesto sto drugi nije).

Idempotentno. `--check` ne mijenja nista, samo javlja (za CI).

Pokreni iz app/:
    python3 scripts/apply-taste-reports.py
    python3 scripts/apply-taste-reports.py --check
"""
import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
STORE = DATA / "tasteReports.json"
CIGARS = DATA / "cigars.json"


def average(values: list[int]) -> int:
    """Prosjek, remi prema gore. 3 i 4 -> 4, ne 3."""
    total = sum(values)
    n = len(values)
    return (2 * total + n) // (2 * n)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="ne piši, samo provjeri")
    args = ap.parse_args()

    reports = json.loads(STORE.read_text(encoding="utf-8")).get("reports", [])
    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in cigars}

    grouped: dict[str, dict[str, list[int]]] = collections.defaultdict(
        lambda: {"strength": [], "body": [], "by": []}
    )
    for r in reports:
        g = grouped[r["cigarId"]]
        g["strength"].append(int(r["strength"]))
        g["body"].append(int(r["body"]))
        g["by"].append(r["by"])

    changed = []
    missing = []
    for cid, g in sorted(grouped.items()):
        cigar = by_id.get(cid)
        if cigar is None:
            missing.append(cid)
            continue
        s, b = average(g["strength"]), average(g["body"])
        tasters = len(set(g["by"]))
        want = {
            "strength": s,
            "body": b,
            "profileEstimated": False,
            "strengthFromTasting": tasters,
        }
        if any(cigar.get(k) != v for k, v in want.items()):
            changed.append((cid, cigar.get("strength"), cigar.get("body"), s, b, tasters))
            if not args.check:
                cigar.update(want)
                # procjena je bila procjena; sada je iza broja netko tko je pusio
                cigar.pop("strengthFromShop", None)

    if missing:
        print(f"upozorenje: {len(missing)} dojmova nema cigaru u katalogu: {missing[:5]}", file=sys.stderr)

    if args.check:
        if changed:
            for cid, os_, ob, s, b, n in changed[:20]:
                print(f"  {cid}: S{os_}->{s} B{ob}->{b} ({n} ocjenjivača)", file=sys.stderr)
            print(f"--check: {len(changed)} zapisa ne prati zabilježene dojmove", file=sys.stderr)
            return 1
        print(f"--check: svih {len(grouped)} ocijenjenih cigara je na mjestu")
        return 0

    if changed:
        CIGARS.write_text(
            json.dumps(cigars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        for cid, os_, ob, s, b, n in changed:
            print(f"  {cid}: S{os_}->{s} B{ob}->{b} ({n} ocjenjivača)")
    print(f"Primijenjeno {len(changed)} zapisa iz {len(reports)} dojmova")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
