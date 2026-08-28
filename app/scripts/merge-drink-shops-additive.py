# -*- coding: utf-8 -*-
"""Apply Tier A/B (and answered Tier C) shop matches onto drink JSON.

Hard rules:
- never delete drink ids
- never replace allez.hr / ecuga.com priceUrl with another shop
- humidor fills gaps only (weak/empty URL)
- idempotent: same URL on same id → skip
- ledger: scripts/output/shop_drinks_ledger.jsonl
- hold: scripts/output/shop_drinks_hold.json

  python scripts/merge-drink-shops-additive.py --dry-run
  python scripts/merge-drink-shops-additive.py --apply --tiers a,b
  python scripts/merge-drink-shops-additive.py --apply --tiers a,b,c
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
OUT = HERE / "output"
REPORT = OUT / "shop_gaps_report.json"
LEDGER = OUT / "shop_drinks_ledger.jsonl"
HOLD = OUT / "shop_drinks_hold.json"
ASK_PATH = OUT / "catalog_ask_queue.json"

FILES = [
    "rums.json",
    "whiskies.json",
    "brandies.json",
    "gins.json",
    "tequilas.json",
    "wines.json",
    "digestifs.json",
]


def _load_mdl():
    name = "match_drink_listings_lib"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE / "match-drink-listings.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_drinks() -> dict[str, tuple[str, dict]]:
    by_id: dict[str, tuple[str, dict]] = {}
    for fname in FILES:
        path = DATA / fname
        if not path.exists():
            continue
        for d in json.loads(path.read_text(encoding="utf-8")):
            by_id[d["id"]] = (fname, d)
    return by_id


def append_ledger(rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def save_hold(items: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    HOLD.write_text(
        json.dumps(
            {
                "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "items": items,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def candidates_from_report(tiers: set[str]) -> list[dict]:
    if not REPORT.exists():
        raise SystemExit(f"missing {REPORT}; run scan-drink-shop-gaps.py first")
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    rows: list[dict] = []
    if "a" in tiers:
        for it in report.get("itemsA") or []:
            rows.append({**it, "tier": "A", "source": "report"})
    if "b" in tiers:
        for it in report.get("itemsB") or []:
            rows.append({**it, "tier": "B", "source": "report"})
    return rows


def candidates_from_answered_ask() -> list[dict]:
    """Tier C answers: answered drink-ambiguous with answer.id set."""
    if not ASK_PATH.exists():
        return []
    payload = json.loads(ASK_PATH.read_text(encoding="utf-8"))
    out: list[dict] = []
    for it in payload.get("items") or []:
        if not it.get("answered"):
            continue
        if it.get("kind") != "drink-ambiguous":
            continue
        answer = it.get("answer") or {}
        drink_id = answer.get("id") if isinstance(answer, dict) else None
        if not drink_id or drink_id in ("new", "skip"):
            continue
        out.append(
            {
                "name": it.get("name"),
                "url": it.get("url"),
                "price_eur": (it.get("extra") or {}).get("price_eur")
                if isinstance(it.get("extra"), dict)
                else it.get("price_eur"),
                "shop": it.get("shop"),
                "shopLabel": it.get("shop"),
                "matchId": drink_id,
                "tier": "C",
                "bestScore": it.get("bestScore") or 1.0,
                "source": "ask-answered",
                "askKey": it.get("key"),
            }
        )
    return out


def build_updates(
    candidates: list[dict],
    by_id: dict[str, tuple[str, dict]],
) -> tuple[list[dict], list[dict]]:
    mdl = _load_mdl()
    updates: list[dict] = []
    held: list[dict] = []
    used: set[str] = set()

    def norm_url(u: str | None) -> str:
        return (u or "").split("?")[0].rstrip("/").lower()

    for cand in candidates:
        drink_id = cand.get("matchId")
        url = cand.get("url") or ""
        tier = (cand.get("tier") or "").upper()
        if not drink_id or not url:
            held.append({**cand, "holdReason": "missing matchId or url"})
            continue
        if drink_id in used:
            held.append({**cand, "holdReason": "drink already claimed this run"})
            continue
        hit = by_id.get(drink_id)
        if not hit:
            held.append({**cand, "holdReason": f"unknown drink id {drink_id}"})
            continue
        fname, drink = hit

        # Tier A = URL already known on this drink. Only refresh price/shop when
        # priceUrl already equals the listing (never promote a sourceUrl sibling
        # into priceUrl automatically).
        if tier == "A":
            if norm_url(drink.get("priceUrl")) != norm_url(url):
                held.append(
                    {
                        **cand,
                        "holdReason": "tier A url only on sourceUrls / sibling — not auto-promoted",
                    }
                )
                continue

        after = mdl.propose_update(
            drink,
            {
                "url": url,
                "price_eur": cand.get("price_eur"),
                "shop": cand.get("shop"),
                "shopLabel": cand.get("shopLabel") or cand.get("shop"),
            },
            score=float(cand.get("bestScore") or 1.0),
        )
        if not after:
            held.append({**cand, "holdReason": "no change / overwrite blocked"})
            continue
        used.add(drink_id)
        updates.append(
            {
                "id": drink_id,
                "file": fname,
                "tier": cand.get("tier"),
                "score": cand.get("bestScore"),
                "listing": cand.get("name"),
                "url": url,
                "source": cand.get("source"),
                "before": {
                    "priceUrl": drink.get("priceUrl"),
                    "priceEUR": drink.get("priceEUR"),
                    "shopHR": drink.get("shopHR"),
                },
                "after": after,
            }
        )
    return updates, held


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="Plan only (default if no --apply)")
    ap.add_argument("--apply", action="store_true", help="Write drink JSON")
    ap.add_argument(
        "--tiers",
        default="a,b",
        help="Comma list of tiers: a,b,c (c = answered ask-queue)",
    )
    args = ap.parse_args()
    if not args.apply:
        args.dry_run = True

    tiers = {t.strip().lower() for t in args.tiers.split(",") if t.strip()}
    candidates = candidates_from_report(tiers)
    if "c" in tiers:
        candidates.extend(candidates_from_answered_ask())

    by_id = load_drinks()
    updates, held = build_updates(candidates, by_id)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"candidates={len(candidates)} updates={len(updates)} held={len(held)}")
    save_hold(held)

    if args.dry_run:
        print("dry-run: not writing drink JSON")
        for u in updates[:15]:
            print(f"  would {u['tier']} {u['id']} <- {u['url'][:80]}")
        if len(updates) > 15:
            print(f"  ... +{len(updates) - 15} more")
        return

    mdl = _load_mdl()
    mdl.write_updates(updates)
    append_ledger(
        [
            {
                "at": stamp,
                "id": u["id"],
                "file": u["file"],
                "tier": u["tier"],
                "url": u["url"],
                "before": u["before"],
                "after": u["after"],
                "source": u.get("source"),
            }
            for u in updates
        ]
    )
    print(f"applied {len(updates)} updates; ledger={LEDGER}")


if __name__ == "__main__":
    main()
