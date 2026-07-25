# -*- coding: utf-8 -*-
"""Uskladi markets.EU / markets.USA s dokazom (regionLinks / host URL) + soft keep iz unified kataloga.

Idempotentno. Ne izmišlja dostupnost.

Pravila (curated, catalogSource != "market"):
  - tvrdi dokaz: regionLinks[region] s URL-om ILI product URL na regionalnim hostovima → zadrži
  - soft keep: (brand, line) prisutan u unified katalogu za tu regiju (offers) → zadrži
  - inače: makni regiju iz markets
  - reverse: regionLinks[region] ima URL, a regija nije u markets → DODAJ

Market (catalogSource == "market"):
  - ne diraj osim integriteta: regija u markets bez hard i bez soft dokaza → makni

Pokretanje (iz app/):
  python scripts/reconcile-eu-usa-availability.py [--fetch]
  --fetch  HTTP probe shop homepagea (nije puni scrape). Soft keep koristi
           app/scripts/output/cigar_unified_catalog.json ako postoji
           (restore: git show origin/cursor/shop-raw-catalogs-d678:app/scripts/output/cigar_unified_catalog.json).
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT.parent
DATA = APP / "src" / "data"
OUT = ROOT / "output"
UNIFIED = OUT / "cigar_unified_catalog.json"
FETCH_PROBE = OUT / "eu_usa_fetch_probe.json"
REPORT = OUT / "eu_usa_reconcile_report.json"
CIGARS = DATA / "cigars.json"

REGIONS = ("EU", "USA")
HOSTS = {
    "EU": ("cigarworld.de", "cigarworld.com"),
    "USA": ("holts.com", "famous-smoke.com", "cigarsdaily.com", "neptunecigar.com"),
}
PROBE_URLS = {
    "cigarworld.de": "https://www.cigarworld.de/",
    "holts.com": "https://www.holts.com/",
    "cigarsdaily.com": "https://cigarsdaily.com/",
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower().strip())


def is_region_host_url(url: str | None, region: str) -> bool:
    if not url:
        return False
    u = url.lower()
    return any(h in u for h in HOSTS[region])


def has_hard_proof(c: dict, region: str) -> bool:
    rl = (c.get("regionLinks") or {}).get(region)
    if isinstance(rl, dict) and rl.get("url"):
        return True
    if is_region_host_url(c.get("priceUrl"), region):
        return True
    for v in c.get("vitolas") or []:
        if is_region_host_url(v.get("url"), region):
            return True
    return False


def region_link_url(c: dict, region: str) -> str | None:
    rl = (c.get("regionLinks") or {}).get(region)
    if isinstance(rl, dict):
        url = rl.get("url")
        if url:
            return str(url)
    return None


def build_present(unified: dict | None) -> dict[str, set[tuple[str, str]]]:
    """region -> set of (brand_norm, line_norm) with shop offers in that region.

    Only offer.region counts — never row.markets/regions (those can mirror the
    curated markets we are validating and would circularly soft-keep).
    """
    present: dict[str, set[tuple[str, str]]] = {r: set() for r in REGIONS}
    if not unified:
        return present
    for row in unified.get("cigars") or []:
        brand = row.get("brand")
        line = row.get("line")
        if not brand or not line:
            continue
        key = (norm(brand), norm(line))
        for o in row.get("offers") or []:
            r = o.get("region")
            if r in REGIONS:
                present[r].add(key)
    return present


def soft_match(c: dict, present: set[tuple[str, str]]) -> bool:
    key = (norm(c.get("brand", "")), norm(c.get("line", "")))
    if key in present:
        return True
    bn, ln = key
    if not bn or not ln:
        return False
    for pb, pl in present:
        if pb != bn:
            continue
        if ln in pl or pl in ln:
            return True
    return False


def probe_live(timeout_s: float = 20.0) -> dict:
    """Lightweight HTTP probe — not a full catalog scrape."""
    results: dict[str, dict] = {}
    ua = "Mozilla/5.0 (compatible; cigar-pairing-reconcile/1.0)"
    for host, url in PROBE_URLS.items():
        entry: dict = {"url": url, "ok": False}
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua})
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                entry["status"] = getattr(resp, "status", None) or resp.getcode()
                body = resp.read(2048)
                entry["bytes"] = len(body)
                entry["ok"] = 200 <= int(entry["status"]) < 400
        except urllib.error.HTTPError as e:
            entry["status"] = e.code
            entry["error"] = str(e.reason)[:200]
            entry["ok"] = 200 <= e.code < 400
        except Exception as e:  # noqa: BLE001 — probe must never crash reconcile
            entry["error"] = f"{type(e).__name__}: {e}"[:240]
        results[host] = entry
    any_ok = any(v.get("ok") for v in results.values())
    return {
        "probed_at": datetime.now(timezone.utc).isoformat(),
        "full_catalog_fetch": False,
        "note": (
            "Probe only (homepage reachability). Full EU/USA catalog scrape is not "
            "performed by this script; use cigar_unified_catalog.json snapshot."
        ),
        "any_ok": any_ok,
        "hosts": results,
    }


def load_unified() -> tuple[dict | None, str]:
    if not UNIFIED.exists():
        return None, "missing"
    try:
        data = json.loads(UNIFIED.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as e:
        return None, f"unreadable: {e}"
    return data, "loaded"


def reconcile(
    cigars: list[dict],
    present: dict[str, set[tuple[str, str]]],
) -> tuple[list[dict], list[dict]]:
    removed: list[dict] = []
    added: list[dict] = []

    for c in cigars:
        is_market = c.get("catalogSource") == "market"
        markets = list(c.get("markets") or [])
        changed_markets = list(markets)

        for region in REGIONS:
            hard = has_hard_proof(c, region)
            soft = soft_match(c, present.get(region) or set())
            in_markets = region in changed_markets
            link = region_link_url(c, region)

            if is_market:
                # Integrity only (HR spirit): neither hard nor soft → remove
                if in_markets and not hard and not soft:
                    removed.append({
                        "id": c.get("id"),
                        "brand": c.get("brand"),
                        "line": c.get("line"),
                        "region": region,
                        "catalogSource": "market",
                        "previous_markets": markets,
                        "reason": f"market-{region}-without-source",
                    })
                    changed_markets = [m for m in changed_markets if m != region]
                continue

            # curated: reverse add when regionLinks has URL but market missing
            if link and not in_markets:
                changed_markets.append(region)
                added.append({
                    "id": c.get("id"),
                    "brand": c.get("brand"),
                    "line": c.get("line"),
                    "region": region,
                    "url": link,
                    "reason": "has_link_missing_market",
                })
                in_markets = True

            if not in_markets:
                continue

            if hard or soft:
                continue

            removed.append({
                "id": c.get("id"),
                "brand": c.get("brand"),
                "line": c.get("line"),
                "region": region,
                "catalogSource": c.get("catalogSource"),
                "previous_markets": markets,
                "reason": "no-proof-no-snapshot-match",
            })
            changed_markets = [m for m in changed_markets if m != region]

        order = {"HR": 0, "EU": 1, "USA": 2}
        changed_markets = sorted(set(changed_markets), key=lambda m: (order.get(m, 9), m))
        if changed_markets != markets:
            c["markets"] = changed_markets

    return removed, added


def integrity_bad(
    cigars: list[dict],
    present: dict[str, set[tuple[str, str]]],
) -> dict[str, list[dict]]:
    """Curated with region in markets but neither hard proof nor soft catalog match."""
    bad: dict[str, list[dict]] = {r: [] for r in REGIONS}
    for c in cigars:
        if c.get("catalogSource") == "market":
            continue
        markets = c.get("markets") or []
        for region in REGIONS:
            if region not in markets:
                continue
            if has_hard_proof(c, region):
                continue
            if soft_match(c, present.get(region) or set()):
                continue
            bad[region].append({
                "id": c.get("id"),
                "brand": c.get("brand"),
                "line": c.get("line"),
            })
    return bad


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--fetch",
        action="store_true",
        help="Probe live shop HTTP; does not replace unified catalog scrape",
    )
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)

    if args.fetch:
        print("Live HTTP probe (CigarWorld / Holt's / Cigars Daily)...", flush=True)
        fetch_status = probe_live()
        FETCH_PROBE.write_text(json.dumps(fetch_status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        ok_hosts = [h for h, v in fetch_status["hosts"].items() if v.get("ok")]
        print(f"Probe ok={fetch_status['any_ok']} hosts={ok_hosts or 'none'}", flush=True)
        if not fetch_status["any_ok"]:
            print(
                "WARNING: live shop probe failed — not inventing availability; "
                "continuing with regionLinks/URL proof (+ unified snapshot soft keep if present).",
                flush=True,
            )
    else:
        fetch_status = {
            "probed_at": None,
            "full_catalog_fetch": False,
            "skipped": True,
            "note": "Ran without --fetch; no live probe.",
            "any_ok": False,
            "hosts": {},
        }

    unified, unified_status = load_unified()
    present = build_present(unified)
    print(
        f"Unified catalog: {unified_status} | "
        f"present EU={len(present['EU'])} USA={len(present['USA'])} | "
        f"generatedAt={(unified or {}).get('generatedAt')}",
        flush=True,
    )
    if unified is None:
        print(
            "No unified snapshot — soft keep disabled; hard URL/regionLinks proof only.",
            flush=True,
        )

    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    removed, added = reconcile(cigars, present)
    CIGARS.write_text(json.dumps(cigars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    bad = integrity_bad(cigars, present)
    removed_eu = sum(1 for r in removed if r["region"] == "EU")
    removed_usa = sum(1 for r in removed if r["region"] == "USA")
    added_eu = sum(1 for a in added if a["region"] == "EU")
    added_usa = sum(1 for a in added if a["region"] == "USA")

    soft_kept: dict[str, list[dict]] = {r: [] for r in REGIONS}
    for c in cigars:
        if c.get("catalogSource") == "market":
            continue
        for region in REGIONS:
            if region not in (c.get("markets") or []):
                continue
            if has_hard_proof(c, region):
                continue
            if soft_match(c, present.get(region) or set()):
                soft_kept[region].append({
                    "id": c.get("id"),
                    "brand": c.get("brand"),
                    "line": c.get("line"),
                })

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "fetch": fetch_status,
        "unified_catalog": {
            "path": str(UNIFIED.relative_to(APP)).replace("\\", "/") if UNIFIED.exists() else None,
            "status": unified_status,
            "generatedAt": (unified or {}).get("generatedAt"),
            "present_keys": {r: len(present[r]) for r in REGIONS},
        },
        "removed_count": len(removed),
        "removed_eu": removed_eu,
        "removed_usa": removed_usa,
        "added_count": len(added),
        "added_eu": added_eu,
        "added_usa": added_usa,
        "soft_kept_curated_catalog_match": {r: len(soft_kept[r]) for r in REGIONS},
        "soft_kept": soft_kept,
        "integrity_curated_without_proof": {r: len(bad[r]) for r in REGIONS},
        "markets_remaining": {
            r: sum(1 for c in cigars if r in (c.get("markets") or []))
            for r in REGIONS
        },
        "removed": removed,
        "added": added,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Removed EU={removed_eu} USA={removed_usa} | "
        f"Added EU={added_eu} USA={added_usa} | "
        f"soft-kept curated EU={len(soft_kept['EU'])} USA={len(soft_kept['USA'])} | "
        f"integrity bad EU={len(bad['EU'])} USA={len(bad['USA'])}",
        flush=True,
    )
    print(f"Report: {REPORT}", flush=True)


if __name__ == "__main__":
    main()
