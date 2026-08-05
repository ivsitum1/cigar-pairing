#!/usr/bin/env python3
"""Izvodi prikazna imena pića → src/data/drinkDisplayNames.json.

Sirovi `name` ostaje netaknut (buy-link slugovi, pretraga). Čisti se samo
prikaz: scrape repovi (% Vol, volumen, poklon pakiranje, HTML entiteti).

Ručne ispravke: scripts/data/drink_display_name_overrides.json — uvijek
nadjačavaju heuristiku.

Sudari:
  - ista očišćena imena = stvarne varijante → dodaj diskriminator (0,5 l / Magnum /
    poklon kutija)
  - čišćenje koje se poklopi s već postojećim čistim imenom (katalog duplikat)
    → isto prikazno ime je u redu; evidentira se u stderr sažetku

Usage:
  python3 scripts/derive-drink-display-names.py
  python3 scripts/derive-drink-display-names.py --check
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
DATA = APP / "src" / "data"
OUT = DATA / "drinkDisplayNames.json"
OVERRIDES = APP / "scripts" / "data" / "drink_display_name_overrides.json"
FILES = ["rums", "whiskies", "brandies", "gins", "wines", "tequilas", "digestifs"]

# Isti repovi kao derive-drink-brands.py + bare % (bez "Vol") / giftbox / čaša.
TAIL = re.compile(
    r"\s*(?:\d+[.,]?\d*\s*%(?:\s*Vol\.?)?.*|u poklon kutij.*|"
    r"\d+[.,]?\d*\s*l\b.*|MAGNUM.*|in Giftbox.*|"
    r"sa\s+[cčć]a[sš]om.*|in wooden case.*|&#0\d\d;.*)$",
    re.I,
)

VOL_RE = re.compile(r"(\d+[.,]?\d*)\s*l\b", re.I)
HAS_GIFT = re.compile(
    r"u poklon kutij|in Giftbox|gift ?box|sa\s+[cčć]a[sš]om|in wooden case",
    re.I,
)
HAS_MAGNUM = re.compile(r"\bMAGNUM\b", re.I)


def clean(name: str) -> str:
    n = html.unescape(name or "").replace("&#039;", "'")
    n = TAIL.sub("", n)
    return re.sub(r"\s+", " ", n).strip(" -–—,")


def discriminator(raw: str) -> str | None:
    """Kratki dodatak kad bi dvije boce dobile isto očišćeno ime."""
    parts: list[str] = []
    if HAS_MAGNUM.search(raw):
        parts.append("Magnum")
    m = VOL_RE.search(raw)
    if m:
        parts.append(f"{m.group(1).replace('.', ',')} l")
    if HAS_GIFT.search(raw):
        parts.append("poklon kutija")
    if not parts:
        return None
    # Magnum već nosi volumen; gift+volumen zadrži oba kad treba (0,5 vs 0,7).
    if "Magnum" in parts and any(p.endswith(" l") for p in parts):
        parts = [p for p in parts if p == "Magnum" or p.endswith(" l")]
        # Magnum + volumen dovoljno; bez "poklon kutija" ako je magnum gift
        if "Magnum" in parts:
            parts = [p for p in parts if p == "Magnum" or p.endswith(" l")]
    return " · ".join(dict.fromkeys(parts))  # stable unique


def disambiguate(groups: dict[str, list[tuple[str, str]]]) -> dict[str, str]:
    """id → display.

    Stvarne varijante (različit volumen / Magnum / poklon) dobiju diskriminator.
    Katalog-duplikati (isto očišćeno ime, isti ili nikakav disc) dijele bazu —
    prikaz smije biti isti; spajanje zapisa je drugi posao.
    """
    out: dict[str, str] = {}
    for base, items in groups.items():
        if len(items) == 1:
            did, _raw = items[0]
            out[did] = base
            continue

        annotated = [(did, raw, discriminator(raw)) for did, raw in items]
        discs = {d for _, _, d in annotated}
        meaningful = {d for d in discs if d}

        if len(meaningful) > 1 or (len(items) > 1 and len(discs) == len(items) and None not in discs):
            for did, _raw, disc in annotated:
                out[did] = f"{base} ({disc})" if disc else base
        else:
            for did, _raw, _disc in annotated:
                out[did] = base
    return out


def load_all() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for f in FILES:
        for d in json.loads((DATA / f"{f}.json").read_text(encoding="utf-8")):
            rows.append((d["id"], d.get("name", "")))
    return rows


def derive(rows: list[tuple[str, str]]) -> tuple[dict[str, str], list[str]]:
    """Vrati display mapu samo za boce kojima se prikaz razlikuje od sirovog imena."""
    cleaned_all: dict[str, str] = {}
    groups: dict[str, list[tuple[str, str]]] = defaultdict(list)
    notes: list[str] = []

    for did, raw in rows:
        base = clean(raw)
        cleaned_all[did] = base
        groups[base].append((did, raw))

    resolved = disambiguate(groups)

    # Evidentiraj katalog-duplikate: čišćenje spoji scrape s već čistim imenom.
    for base, items in groups.items():
        if len(items) < 2:
            continue
        raws = {r for _, r in items}
        if len(raws) == 1:
            continue
        if any(clean(r) == r for _, r in items) and any(clean(r) != r for _, r in items):
            notes.append(
                f"katalog-duplikat → {base!r}: "
                + ", ".join(i for i, _ in items)
            )

    display = {
        did: label
        for did, label in resolved.items()
        if label != next(r for i, r in rows if i == did)
    }
    return display, notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    overrides: dict[str, str] = {}
    if OVERRIDES.exists():
        overrides = json.loads(OVERRIDES.read_text(encoding="utf-8")).get("names", {})

    rows = load_all()
    display, notes = derive(rows)
    display.update({k: v for k, v in overrides.items() if any(i == k for i, _ in rows)})

    payload = {
        "_comment": (
            "Prikazna imena pića bez scrape repova. Generira "
            "scripts/derive-drink-display-names.py. Sirovi `name` ostaje za "
            "buy-link i pretragu. Ručne ispravke: "
            "scripts/data/drink_display_name_overrides.json."
        ),
        "names": dict(sorted(display.items())),
    }
    text = json.dumps(payload, ensure_ascii=False, indent=1) + "\n"

    for n in notes:
        print(f"napomena: {n}", file=sys.stderr)

    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("--check: drinkDisplayNames.json nije u skladu s podacima", file=sys.stderr)
            return 1
        print(f"--check: {len(display)} prikaznih imena na mjestu")
        return 0

    OUT.write_text(text, encoding="utf-8")
    print(f"{len(display)} prikaznih imena ({len(overrides)} ručnih ispravki)")
    if notes:
        print(f"{len(notes)} napomena o katalog-duplikatima (stderr)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
