#!/usr/bin/env python3
"""CigarWorldov aroma-radar -> okusne oznake u cigars.json.

`cw_famous_flavor_raw.json` uz 567 cigara nosi CigarWorldov radar: dvanaest
imenovanih dimenzija okusa, svaka ocijenjena 1–10. To je jedini izvor u repou
koji o okusu govori mjereno umjesto da ga izvodi iz pokrova, i dosad je stajao
neiskoristen — `convert-cw-famous-raw.py` nikad nije ponovno pokrenut nakon sto
je radar dohvacen, pa je `cigarworld_flavor_raw.json` ostao bez njega.

Namjerno se NE ide preko tog starog puta: on radar pretvara u tekst
("wood 8 pepper 7 grass 1") i onda ga cita regexom, cime se gubi ocjena — grass
ocijenjen jedinicom (dakle: nema ga) dao bi jednaku oznaku kao wood ocijenjen
osmicom. Ovdje ocjena odlucuje: uzimaju se dimenzije >= AROMA_MIN.

Dvije od dvanaest dimenzija namjerno nemaju oznaku: `toast` (najblize sto
katalog ima je "pšenica", a to nije prepecen kruh) i nista drugo se ne
izmislja. Bolje deset tocnih nego dvanaest nategnutih.

Dira samo zapise s `profileEstimated: true` — kurirani profili se ne prepisuju.
Idempotentno; `--check` ne mijenja nista (za CI).

Pokreni iz app/:
    python3 scripts/merge-cigarworld-aroma.py
    python3 scripts/merge-cigarworld-aroma.py --check
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
CIGARS = DATA / "cigars.json"
RAW = HERE / "output" / "cw_famous_flavor_raw.json"

# Ocjena od 5 na ljestvici 1–10 znaci "osjeti se"; ispod toga je sum. Prag daje
# oko cetiri oznake po cigari, sto je otprilike koliko ih kartica i prikazuje.
AROMA_MIN = 5
MAX_TAGS = 6

AROMA_TO_TAG = {
    "wood": "drvo",
    "pepper": "papar",
    "grass": "trava-slatka",
    "fruit": "voce",
    "cream": "kremasto",
    "sweet": "slatko",
    "nut": "orasasti",
    "chocolate": "kakao",
    "coffee": "kava",
    "leather": "koza",
    "soil": "zemljano",
}


def _load(filename: str):
    spec = importlib.util.spec_from_file_location(
        filename.replace("-", "_").removesuffix(".py"), HERE / filename
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


_profile = _load("profile-cigars.py")


def tags_from_aroma(aroma: dict) -> list[str]:
    """Radar -> oznake, jace prvo. Ocjena odlucuje, ne puko spominjanje."""
    hits = [
        (int(v), AROMA_TO_TAG[k])
        for k, v in aroma.items()
        if k in AROMA_TO_TAG and isinstance(v, (int, float)) and v >= AROMA_MIN
    ]
    hits.sort(key=lambda kv: -kv[0])
    return list(dict.fromkeys(tag for _, tag in hits))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="ne piši, samo provjeri")
    args = ap.parse_args()

    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in cigars}
    aliases = json.loads((DATA / "cigarIdAliases.json").read_text(encoding="utf-8"))["aliases"]

    def resolve(cid: str):
        seen = set()
        while cid not in by_id:
            if cid in seen or cid not in aliases:
                return None
            seen.add(cid)
            cid = aliases[cid]
        return cid

    changed = []
    for row in json.loads(RAW.read_text(encoding="utf-8")):
        aroma = (row.get("cigarworld") or {}).get("aroma") or {}
        if not aroma:
            continue
        cid = resolve(row["id"])
        if cid is None:
            continue
        cigar = by_id[cid]
        if not cigar.get("profileEstimated"):
            continue  # kurirani profil se ne dira
        measured = tags_from_aroma(aroma)
        if not measured:
            continue
        existing = list(cigar.get("flavorTags") or [])
        # Stub je popunjivac, ne podatak — mjereno tada vodi. Inace se dopunjuje.
        if _profile.is_pure_stub(cigar):
            merged = list(dict.fromkeys([*measured, *existing]))[:MAX_TAGS]
        else:
            merged = list(dict.fromkeys([*existing, *measured]))[:MAX_TAGS]
        if merged != existing:
            changed.append((cid, existing, merged))
            if not args.check:
                cigar["flavorTags"] = merged

    if args.check:
        if changed:
            for cid, old, new in changed[:20]:
                print(f"  {cid}: {old} -> {new}", file=sys.stderr)
            print(f"--check: {len(changed)} zapisa nije usklađeno s radarom", file=sys.stderr)
            return 1
        print("--check: sve okusne oznake iz radara su na mjestu")
        return 0

    if changed:
        CIGARS.write_text(
            json.dumps(cigars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(f"Osvježeno {len(changed)} zapisa iz aroma-radara")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
