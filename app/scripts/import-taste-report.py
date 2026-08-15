#!/usr/bin/env python3
"""Dojmovi iz prijave -> src/data/tasteReports.json.

App ne moze sama pisati u repo (staticna stranica, nema gdje cuvati kljuc), pa
dojmove salje kao predpopunjenu GitHub prijavu ili obican tekst. Ova skripta
prima jedno i drugo: proguta cijelo tijelo prijave i izvuce ```json blok iz
njega, ili primi cisti JSON.

Zapis je po osobi i cigari: nova ocjena iste osobe za istu cigaru zamjenjuje
staru, ocjena druge osobe stoji uz nju. Tko je ocijenio ostaje zapisano — bez
potpisa prosjek dvoje ljudi nije prosjek nego zbrka.

Pokreni iz app/:
    python3 scripts/import-taste-report.py < prijava.txt
    python3 scripts/import-taste-report.py prijava.txt
    python3 scripts/import-taste-report.py --dry-run < prijava.txt
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
STORE = DATA / "tasteReports.json"
CIGARS = DATA / "cigars.json"
ALIASES = DATA / "cigarIdAliases.json"

KIND = "cigar-pairing-taste-report"

FENCE = re.compile(r"```json\s*(\{.*?\})\s*```", re.S)


def extract_payload(text: str) -> dict:
    """Tijelo prijave ili cisti JSON -> objekt izvjestaja."""
    text = text.strip()
    if not text:
        raise SystemExit("prazan ulaz")
    for candidate in ([m.group(1) for m in FENCE.finditer(text)] + [text]):
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("kind") == KIND:
            return obj
    raise SystemExit(f"u ulazu nema izvjestaja (trazi se kind={KIND!r})")


def resolver():
    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    by_id = {c["id"] for c in cigars}
    aliases = json.loads(ALIASES.read_text(encoding="utf-8"))["aliases"]

    def resolve(cid: str):
        seen = set()
        while cid not in by_id:
            if cid in seen or cid not in aliases:
                return None
            seen.add(cid)
            cid = aliases[cid]
        return cid

    return resolve


def clamp(n) -> int | None:
    try:
        v = int(round(float(n)))
    except (TypeError, ValueError):
        return None
    return max(1, min(5, v))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", help="datoteka s prijavom; bez nje se čita stdin")
    ap.add_argument("--dry-run", action="store_true", help="ne piši, samo pokaži")
    args = ap.parse_args()

    text = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    payload = extract_payload(text)
    by = str(payload.get("by") or "").strip()
    if not by:
        raise SystemExit("izvjestaj nije potpisan — bez imena se ocjene ne mogu razlikovati")

    resolve = resolver()
    store = json.loads(STORE.read_text(encoding="utf-8"))
    kept = {(r["by"], r["cigarId"]): r for r in store.get("reports", [])}

    added = updated = skipped = 0
    for entry in payload.get("reports") or []:
        cid = resolve(str(entry.get("cigarId") or ""))
        s, b = clamp(entry.get("strength")), clamp(entry.get("body"))
        if cid is None or s is None or b is None:
            skipped += 1
            continue
        key = (by, cid)
        row = {"by": by, "cigarId": cid, "strength": s, "body": b,
               "at": str(entry.get("at") or payload.get("at") or "")}
        if key in kept:
            if kept[key] != row:
                updated += 1
            kept[key] = row
        else:
            kept[key] = row
            added += 1

    reports = sorted(kept.values(), key=lambda r: (r["cigarId"], r["by"]))
    print(f"{by}: novih {added}, izmijenjenih {updated}, preskocenih {skipped}; ukupno {len(reports)}")
    if args.dry_run:
        return 0
    STORE.write_text(
        json.dumps({"reports": reports}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"-> {STORE}")
    print("Sada: python3 scripts/apply-taste-reports.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
