#!/usr/bin/env python3
"""Drzi snagu i tijelo razdvojenima, ali ne dalje nego sto ima smisla.

Snaga i tijelo su dvije osi i SMIJU se razlikovati — Connecticut zna biti pun a
blag, corojo jak a suh. Ali razmak od tri stepenice nije cigara, nego dva
izvora koja se ne poznaju: `build-market-cigars.py` snagu uzima iz shopa
(CigarWorld 1–5), a tijelo iz heuristike pokrova, pa "La Flor Dominicana Suave"
zavrsi kao snaga 2 / tijelo 5.

Gdje se osi raziđu za vise od dvije stepenice, tijelo se vraca na ono sto za
takav pokrov znaci mjerena snaga: body = snaga + razmak koji WRAPPER_BASE drzi
izmedu tijela i snage za tu vrstu pokrova. Snaga se ne dira — ona je mjerena.

Idempotentno. `--check` ne mijenja nista, samo javlja (za CI).

Pokreni iz app/:
    python3 scripts/normalize-profile-axes.py
    python3 scripts/normalize-profile-axes.py --check
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CIGARS = HERE.parent / "src" / "data" / "cigars.json"
MAX_GAP = 2


def _load(filename: str):
    spec = importlib.util.spec_from_file_location(
        filename.replace("-", "_").removesuffix(".py"), HERE / filename
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


_profile = _load("profile-cigars.py")


def house_gap(cigar: dict) -> int:
    """Koliko je tijelo punije od snage za ovakav pokrov, po katalogovoj heuristici."""
    probe = {
        "brand": cigar.get("brand", ""),
        "line": cigar.get("line", ""),
        "vitola": cigar.get("vitola", ""),
        "wrapper": cigar.get("wrapper", ""),
        "country": cigar.get("country", ""),
        "notes": cigar.get("notes", {}),
    }
    try:
        _profile.enrich(probe)
    except Exception:  # noqa: BLE001
        return 0
    return int(probe.get("body", 3)) - int(probe.get("strength", 3))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="ne piši, samo provjeri")
    args = ap.parse_args()

    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    fixed = []
    for c in cigars:
        s, b = c.get("strength"), c.get("body")
        if not isinstance(s, int) or not isinstance(b, int):
            continue
        if abs(s - b) <= MAX_GAP:
            continue
        new_body = _profile.clamp(s + house_gap(c))
        fixed.append((c["id"], s, b, new_body))
        if not args.check:
            c["body"] = new_body

    if args.check:
        if fixed:
            for cid, s, b, nb in fixed:
                print(f"  {cid}: snaga {s}, tijelo {b} -> {nb}", file=sys.stderr)
            print(f"--check: {len(fixed)} zapisa ima razmak veći od {MAX_GAP}", file=sys.stderr)
            return 1
        print(f"--check: nijedan zapis ne razdvaja osi više od {MAX_GAP}")
        return 0

    if fixed:
        CIGARS.write_text(
            json.dumps(cigars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        for cid, s, b, nb in fixed:
            print(f"  {cid}: snaga {s}, tijelo {b} -> {nb}")
    print(f"Ispravljeno {len(fixed)} zapisa")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
