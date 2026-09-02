# -*- coding: utf-8 -*-
"""Uskladi availabilityHR / markets.HR s živim HR katalogom (idempotentno).

Ulaz: scripts/output/hr_catalog_snapshot.json (havana + humidor proizvodi).
Matcher: sync-hr-shops.detect_brand / line_name_from_product / norm.

Pravila:
  - market i curated: otkrij HR kad snapshot poklopi (brand+line ili brand+vitola)
  - tvrdi dokaz (regionLinks.HR ili URL na humidor/havana) → zadrži HR
  - walkIn shopovi iz shops.ts se prenose kroz svaki prolaz
  - bez poklapanja i bez dokaza → availabilityHR=[] i makni "HR" iz markets

Pokretanje (iz app/):
  python scripts/reconcile-hr-availability.py [--fetch]
  --fetch  ponovno dohvati kataloge i prepiši snapshot
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT.parent
DATA = APP / "src" / "data"
OUT = ROOT / "output"
SNAPSHOT = OUT / "hr_catalog_snapshot.json"
REPORT = OUT / "hr_reconcile_report.json"
CIGARS_BACKUP = OUT / "hr_cigars_pre_reconcile.json"
CIGARS = DATA / "cigars.json"

HR_HOSTS = ("humidor.hr", "havana-cigar-shop.com")
SHOP_FROM_SOURCE = {
    "humidor": "The Humidor",
    "havana": "Havana Cigar Shop",
}
SHOPS_TS = APP / "src" / "data" / "shops.ts"


def walk_in_shops() -> set[str]:
    """Nazivi trgovina bez web kataloga (`walkIn: true` u shops.ts).

    Takva se dostupnost unosi ručno i online snapshot je NIKAD ne može
    potvrditi, pa je reconcile ne smije brisati — inače bi svaki tjedni
    prolaz pobrisao fizičke dućane.
    """
    if not SHOPS_TS.exists():
        return set()
    src = SHOPS_TS.read_text(encoding="utf-8")
    out: set[str] = set()
    for block in re.split(r"\n  \{", src):
        if "walkIn: true" not in block:
            continue
        m = re.search(r'name:\s*"((?:[^"\\]|\\.)*)"', block)
        if m:
            out.add(m.group(1))
    return out


def _load_sync():
    spec = importlib.util.spec_from_file_location("sync_hr_shops", ROOT / "sync-hr-shops.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


# Ispod ovog udjela prethodnog snapshota dohvat se smatra neuspjelim, ne
# praznjenjem police. Trgovina koja padne ili promijeni API vratila bi kratku
# listu, a reconcile bi tada pomeo HR s pola kataloga — tiho i nepovratno.
MIN_FETCH_RATIO = 0.7

# Ako bi reconcile maknuo više od ovog udjela postojećih HR tržišta odjednom,
# vjerojatnije je da je matcher ili snapshot kriv — vratimo cigars.json iz
# sigurnosne kopije i ne pišemo promjenu.
MAX_REMOVAL_RATIO = 0.15


def fetch_snapshot(sync) -> dict:
    havana = sync.fetch_havana_catalog()
    humidor = sync.fetch_humidor_catalog()

    if SNAPSHOT.exists():
        prev = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        for key, fresh in (("havana", havana), ("humidor", humidor)):
            before = len(prev.get(key) or [])
            now = len(fresh)
            if before and now < before * MIN_FETCH_RATIO:
                raise SystemExit(
                    f"Dohvat '{key}' vratio {now} proizvoda, a prošli snapshot ih je "
                    f"imao {before} (< {MIN_FETCH_RATIO:.0%}). Vjerojatnije je da je "
                    f"dohvat pao nego da je police ostala prazna — snapshot NIJE "
                    f"prepisan i cigars.json nije diran."
                )

    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "havana": havana,
        "humidor": humidor,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def load_snapshot() -> dict:
    if not SNAPSHOT.exists():
        raise SystemExit(f"Nedostaje snapshot: {SNAPSHOT}. Pokreni s --fetch.")
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def is_hr_url(url: str | None) -> bool:
    if not url:
        return False
    u = url.lower()
    return any(h in u for h in HR_HOSTS)


def has_hard_hr_proof(c: dict) -> bool:
    rl = (c.get("regionLinks") or {}).get("HR")
    if isinstance(rl, dict) and is_hr_url(rl.get("url")):
        return True
    if is_hr_url(c.get("priceUrl")):
        return True
    for v in c.get("vitolas") or []:
        if is_hr_url(v.get("url")):
            return True
    return False


def build_present(
    sync, snapshot: dict, cigars: list[dict]
) -> tuple[dict[tuple[str, str], set[str]], dict[tuple[str, str], set[str]]]:
    """Vrati (by_line, by_vitola): (brand_norm, line|vitola_norm) -> shopovi.

    by_vitola pokriva brojčane linije (npr. Cain Daytona 646) gdje shop
    piše samo 'Cain Daytona Corona' — line_name_from_product ne pogodi '646'.
    """
    detectors = sync.build_brand_detectors(cigars)
    by_line: dict[tuple[str, str], set[str]] = {}
    by_vitola: dict[tuple[str, str], set[str]] = {}
    for src_key in ("havana", "humidor"):
        shop = SHOP_FROM_SOURCE[src_key]
        for row in snapshot.get(src_key) or []:
            name = row.get("name") or ""
            brand = sync.detect_brand(name, detectors)
            if not brand:
                continue
            bn = sync.norm(brand)
            line = sync.line_name_from_product(brand, name)
            by_line.setdefault((bn, sync.norm(line)), set()).add(shop)
            vit = sync.vitola_from_product(name, brand)
            # Samo kad shop naslov nema imenovane linije (Cain Daytona Corona → 646).
            # Inače bi OpusX Robusto lažno pogodio brojčanu liniju 858.
            if vit and sync._numeric_looking_rest(line, brand):
                by_vitola.setdefault((bn, sync.norm(vit)), set()).add(shop)
    return by_line, by_vitola


def match_shops(
    c: dict,
    present: dict[tuple[str, str], set[str]],
    sync,
    present_vitola: dict[tuple[str, str], set[str]] | None = None,
) -> set[str]:
    key = (sync.norm(c.get("brand", "")), sync.norm(c.get("line", "")))
    shops = set(present.get(key) or ())
    # fuzzy: line containment within same brand (isto kao find_or_create_cigar)
    if not shops:
        bn = key[0]
        ln = key[1]
        for (pb, pl), sh in present.items():
            if pb != bn:
                continue
            if ln and pl and (ln in pl or pl in ln):
                shops |= sh
    # fallback samo za brojčane linije (Cain Daytona 646) — inače bi
    # "Robusto" na brandu s više linija lažno označio sve linije kao HR
    if not shops and present_vitola and _numeric_line(c.get("line")):
        bn = key[0]
        names: list[str] = []
        if c.get("vitola"):
            names.append(str(c["vitola"]))
        for v in c.get("vitolas") or []:
            n = v.get("name") if isinstance(v, dict) else None
            if n:
                names.append(str(n))
        for n in names:
            shops |= set(present_vitola.get((bn, sync.norm(n))) or ())
    return shops


def _numeric_line(line: str | None) -> bool:
    """True za linije tipa '646', '550', 'Double 660'."""
    s = re.sub(r"\s+", " ", (line or "").strip().lower())
    return bool(re.fullmatch(r"(double )?\d{2,4}", s))


def _ensure_hr_market(c: dict, prev_markets: list) -> None:
    if "HR" not in c.get("markets", []):
        c["markets"] = list(prev_markets) + ["HR"]


def reconcile(
    cigars: list[dict],
    present: dict,
    sync,
    present_vitola: dict[tuple[str, str], set[str]] | None = None,
) -> tuple[list[dict], list[dict]]:
    removed: list[dict] = []
    added: list[dict] = []
    walk_in = walk_in_shops()
    for c in cigars:
        prev_av = list(c.get("availabilityHR") or [])
        # fizicki ducani se ne mogu potvrditi online — nose se kroz svaki prolaz
        kept_walk_in = [s for s in prev_av if s in walk_in]
        prev_markets = list(c.get("markets") or [])
        is_market = c.get("catalogSource") == "market"
        shops = match_shops(c, present, sync, present_vitola)

        if is_market:
            # Market: otkrij novu online / walk-in ponudu. Tvrdi URL dokaz drži HR.
            # Ne briši ručno postavljen availabilityHR samo zato što zastarjeli
            # snapshot još nema red (npr. Cain/Perla prije --fetch) — samo makni
            # prazan markets.HR bez ikakvog dokaza (integritet).
            if shops or kept_walk_in:
                had_hr = "HR" in prev_markets or bool(prev_av)
                if shops:
                    c["availabilityHR"] = sorted(set(shops) | set(kept_walk_in))
                else:
                    # samo walk-in poklapanje — zadrži i postojeće online unose
                    c["availabilityHR"] = sorted(set(prev_av) | set(kept_walk_in))
                _ensure_hr_market(c, prev_markets)
                if shops and not had_hr:
                    added.append({
                        "id": c.get("id"),
                        "brand": c.get("brand"),
                        "line": c.get("line"),
                        "shops": sorted(shops),
                    })
                continue

            if has_hard_hr_proof(c):
                if not c.get("availabilityHR"):
                    c["availabilityHR"] = sorted(
                        {"The Humidor", "Havana Cigar Shop"} | set(kept_walk_in)
                    )
                _ensure_hr_market(c, prev_markets)
                continue

            if "HR" in prev_markets and not prev_av:
                removed.append({
                    "id": c.get("id"),
                    "brand": c.get("brand"),
                    "line": c.get("line"),
                    "previous_availabilityHR": prev_av,
                    "previous_markets": prev_markets,
                    "reason": "market-HR-without-source",
                })
                c["markets"] = [m for m in prev_markets if m != "HR"]
            continue

        if "HR" not in prev_markets and not prev_av:
            # Nova ponuda: linija koju dosad nismo vodili kao HR, a trgovina je
            # sada drži. Bez ove grane reconcile samo briše zastarjelo i nikad
            # ne otkriva novo, pa cigara koja je stigla nakon zadnjeg scrapea
            # zauvijek ostaje "nema u HR".
            if shops:
                c["availabilityHR"] = sorted(set(shops) | set(kept_walk_in))
                c["markets"] = prev_markets + ["HR"]
                added.append({
                    "id": c.get("id"),
                    "brand": c.get("brand"),
                    "line": c.get("line"),
                    "shops": sorted(shops),
                })
            continue

        if has_hard_hr_proof(c):
            # zadrži HR; normaliziraj availability ako prazan a ima dokaz
            if not c.get("availabilityHR"):
                filled = shops or {"The Humidor", "Havana Cigar Shop"}
                c["availabilityHR"] = sorted(set(filled) | set(kept_walk_in))
            _ensure_hr_market(c, prev_markets)
            continue

        if shops or kept_walk_in:
            c["availabilityHR"] = sorted(set(shops) | set(kept_walk_in))
            _ensure_hr_market(c, prev_markets)
        else:
            if prev_av or "HR" in prev_markets:
                removed.append({
                    "id": c.get("id"),
                    "brand": c.get("brand"),
                    "line": c.get("line"),
                    "previous_availabilityHR": prev_av,
                    "previous_markets": prev_markets,
                    "reason": "no-snapshot-match",
                })
            c["availabilityHR"] = []
            c["markets"] = [m for m in (c.get("markets") or []) if m != "HR"]
    return removed, added


def integrity_count(cigars: list[dict]) -> int:
    bad = [
        c for c in cigars
        if "HR" in (c.get("markets") or [])
        and not (c.get("regionLinks") or {}).get("HR")
        and not c.get("availabilityHR")
    ]
    return len(bad)


def hr_market_count(cigars: list[dict]) -> int:
    return sum(1 for c in cigars if "HR" in (c.get("markets") or []))


def backup_cigars() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CIGARS, CIGARS_BACKUP)


def rollback_cigars() -> bool:
    if not CIGARS_BACKUP.exists():
        return False
    shutil.copy2(CIGARS_BACKUP, CIGARS)
    return True


def validate_reconcile(
    cigars: list[dict],
    removed: list[dict],
    hr_before: int,
) -> None:
    bad = integrity_count(cigars)
    if bad:
        raise SystemExit(
            f"Integritet: {bad} cigara ima markets.HR bez availabilityHR ili "
            f"regionLinks.HR — cigars.json NIJE prepisan."
        )
    if hr_before and len(removed) > hr_before * MAX_REMOVAL_RATIO:
        raise SystemExit(
            f"Reconcile bi maknuo {len(removed)} HR tržišta od {hr_before} "
            f"(>{MAX_REMOVAL_RATIO:.0%}) — sumnjivo mnogo; cigars.json NIJE prepisan."
        )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="Ponovno dohvati HR kataloge")
    args = ap.parse_args()

    sync = _load_sync()
    if args.fetch:
        print("Dohvat HR kataloga...", flush=True)
        snap = fetch_snapshot(sync)
    else:
        snap = load_snapshot()
    print(
        f"Snapshot: havana={len(snap.get('havana') or [])} "
        f"humidor={len(snap.get('humidor') or [])} "
        f"at={snap.get('fetched_at')}",
        flush=True,
    )

    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    hr_before = hr_market_count(cigars)
    backup_cigars()
    present, present_vitola = build_present(sync, snap, cigars)
    print(
        f"Prisutni (brand,line)={len(present)} (brand,vitola)={len(present_vitola)}",
        flush=True,
    )

    removed, added = reconcile(cigars, present, sync, present_vitola)
    try:
        validate_reconcile(cigars, removed, hr_before)
    except SystemExit:
        if rollback_cigars():
            print(f"Povrat: {CIGARS} vraćen iz {CIGARS_BACKUP}", flush=True)
        raise

    # indent=2 + zavrsni novi red = format ostatka repozitorija; indent=1 bi
    # reformatirao cijelu datoteku i utopio stvarnu promjenu u 2400 redaka suma
    CIGARS.write_text(
        json.dumps(cigars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "snapshot_at": snap.get("fetched_at"),
        "present_keys": len(present),
        "removed_count": len(removed),
        "added_count": len(added),
        "hr_without_source": integrity_count(cigars),
        "hr_markets_remaining": hr_market_count(cigars),
        "hr_markets_before": hr_before,
        "removed": removed,
        "added": added,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"Dodano HR: {report['added_count']} | "
        f"Maknuto HR: {report['removed_count']} | "
        f"HR bez izvora: {report['hr_without_source']} | "
        f"HR markets preostalo: {report['hr_markets_remaining']}",
        flush=True,
    )
    print(f"Sigurnosna kopija: {CIGARS_BACKUP}", flush=True)
    print(f"Report: {REPORT}", flush=True)


if __name__ == "__main__":
    main()
