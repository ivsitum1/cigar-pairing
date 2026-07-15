# -*- coding: utf-8 -*-
"""Popravi priceEUR/priceUrl na zadanoj vitoli (ne najjeftinijoj).

Pokretanje:
  python scripts/fix-cigar-prices-links.py
  python scripts/fix-cigar-prices-links.py --report
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CIGARS_JSON = ROOT / "src" / "data" / "cigars.json"


def norm(s: str) -> str:
    return s.strip().lower()


def pick_default_vitola(cigar: dict) -> dict | None:
    vitolas = cigar.get("vitolas") or []
    if not vitolas:
        return None
    if len(vitolas) == 1:
        return vitolas[0]

    line = norm(cigar.get("line", ""))
    for v in vitolas:
        if norm(v.get("name", "")) == line:
            return v

    target = norm(cigar.get("vitola", ""))
    for v in vitolas:
        if norm(v.get("name", "")) == target:
            return v

    for v in vitolas:
        name = norm(v.get("name", ""))
        if line in name or name in line:
            return v

    product = [v for v in vitolas if v.get("url") and "?s=" not in v["url"]]
    priced = [v for v in product if v.get("priceEUR") is not None]
    if priced:
        humidor = [v for v in priced if "humidor.hr" in (v.get("url") or "")]
        return humidor[0] if humidor else priced[0]
    if product:
        humidor = [v for v in product if "humidor.hr" in (v.get("url") or "")]
        return humidor[0] if humidor else product[0]
    return vitolas[0]


def finalize_cigar(cigar: dict) -> dict:
    """Vrati promjene: {id, before_price, after_price, before_url, after_url} ili {}."""
    vitolas = cigar.get("vitolas") or []
    if not vitolas:
        return {}

    default = pick_default_vitola(cigar)
    if not default:
        return {}

    before_price = cigar.get("priceEUR")
    before_url = cigar.get("priceUrl")
    changed = False

    if default.get("priceEUR") is not None and cigar.get("priceEUR") != default["priceEUR"]:
        cigar["priceEUR"] = default["priceEUR"]
        cigar["priceApprox"] = False
        changed = True

    if default.get("url") and cigar.get("priceUrl") != default["url"]:
        cigar["priceUrl"] = default["url"]
        changed = True

    if norm(cigar.get("vitola", "")) != norm(default.get("name", "")):
        cigar["vitola"] = default["name"]
        changed = True

    if default.get("format") and default["format"] != "—":
        cigar["format"] = default["format"]
    if default.get("smokeTimeMin"):
        cigar["smokeTimeMin"] = default["smokeTimeMin"]

    if not changed:
        return {}

    return {
        "id": cigar["id"],
        "vitola": default.get("name"),
        "before_price": before_price,
        "after_price": cigar.get("priceEUR"),
        "before_url": (before_url or "")[:80],
        "after_url": (cigar.get("priceUrl") or "")[:80],
    }


def main() -> None:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="store_true", help="Samo ispiši probleme, ne piši JSON")
    args = parser.parse_args()

    cigars = json.loads(CIGARS_JSON.read_text(encoding="utf-8"))
    changes: list[dict] = []
    search_defaults: list[str] = []

    for cigar in cigars:
        ch = finalize_cigar(cigar)
        if ch:
            changes.append(ch)
        default = pick_default_vitola(cigar)
        if default and (default.get("url") or "").find("?s=") >= 0:
            search_defaults.append(f"{cigar['id']} ({default.get('name')}): {default['url'][:90]}")

    print(f"Ažurirano {len(changes)} linija cigare.")
    for ch in changes[:30]:
        print(
            f"  {ch['id']}: {ch['before_price']} -> {ch['after_price']} € | "
            f"{ch['vitola']}"
        )
    if len(changes) > 30:
        print(f"  ... i još {len(changes) - 30}")

    if search_defaults:
        print(f"\nZadana vitola još uvijek na search URL-u ({len(search_defaults)}):")
        for row in search_defaults[:20]:
            print(f"  {row}")
        if len(search_defaults) > 20:
            print(f"  ... i još {len(search_defaults) - 20}")

    if not args.report:
        CIGARS_JSON.write_text(
            json.dumps(cigars, ensure_ascii=False, indent=1),
            encoding="utf-8",
        )
        print(f"\nZapisano: {CIGARS_JSON}")


if __name__ == "__main__":
    main()
