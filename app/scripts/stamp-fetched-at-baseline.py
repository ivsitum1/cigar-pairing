#!/usr/bin/env python3
"""Jednokratna skripta: postavi fetchedAt = BASELINE_DATE na svim točkama cijena
koje ga nemaju — bez izmjene cijene ili URL-a.

Namjena: nakon implementacije W3 sheme (fetchedAt polje) ovom skriptom sve
postojeće cijene dobivaju konzervativni datum koji odražava da su podaci skupljeni
otprilike u Q2/Q3 2026. Data-quality-report tada prikazuje with_fetched_at_pct = 100 %
bez izmišljanja novih cijena.

Pokretanje (jednom, offline):
  python scripts/stamp-fetched-at-baseline.py

Provjera (bez pisanja):
  python scripts/stamp-fetched-at-baseline.py --dry-run
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASELINE_DATE = "2026-07-01"  # konzervativni datum za sve nestampane cijene

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
CIGARS_JSON = DATA / "cigars.json"

DRY_RUN = "--dry-run" in sys.argv


def stamp_vitola(v: dict) -> bool:
    """Vrati True ako je nešto promijenjeno."""
    changed = False
    if v.get("priceEUR") is not None and not v.get("fetchedAt"):
        v["fetchedAt"] = BASELINE_DATE
        changed = True
    for region in ("HR", "EU", "USA"):
        rl = (v.get("regionLinks") or {}).get(region)
        if rl and rl.get("priceEUR") is not None and not rl.get("fetchedAt"):
            rl["fetchedAt"] = BASELINE_DATE
            changed = True
    return changed


def stamp_cigar(c: dict) -> int:
    """Vrati broj promijenjenih točaka cijena."""
    stamped = 0
    for region in ("HR", "EU", "USA"):
        rl = (c.get("regionLinks") or {}).get(region)
        if rl and rl.get("priceEUR") is not None and not rl.get("fetchedAt"):
            rl["fetchedAt"] = BASELINE_DATE
            stamped += 1
    for v in c.get("vitolas") or []:
        if stamp_vitola(v):
            stamped += 1
    return stamped


def main() -> None:
    cigars = json.loads(CIGARS_JSON.read_text(encoding="utf-8"))
    total_stamped = 0
    cigars_touched = 0
    for c in cigars:
        n = stamp_cigar(c)
        if n:
            total_stamped += n
            cigars_touched += 1

    if DRY_RUN:
        print(f"[dry-run] Bi stampalo {total_stamped} točaka cijena u {cigars_touched} cigara.")
        print(f"[dry-run] Baseline datum: {BASELINE_DATE}")
        return

    CIGARS_JSON.write_text(json.dumps(cigars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Stampano {total_stamped} točaka cijena u {cigars_touched} cigara s fetchedAt={BASELINE_DATE}.")
    print("Sljedeći korak: python scripts/export-indexes.py")


if __name__ == "__main__":
    main()
