# -*- coding: utf-8 -*-
"""Render the shop gap scan as a Markdown list of bottles we do not carry.

Input:  scripts/output/shop_gaps_report.json   (scan-drink-shop-gaps.py)
Output: scripts/output/shop_new_bottles.md     (tracked: the monthly PR diff)

Tier D = no catalog drink scores >= 0.5 → a bottle the app does not have.
Tier C = a weak match → maybe a new edition of something we have; listed
separately so it is not mistaken for either "new" or "known".
The same bottle offered by several shops is shown once, with every shop.

Read-only on drink JSON. Used by .github/workflows/drink-shop-scan.yml.

  python scripts/report-new-shop-bottles.py
  python scripts/report-new-shop-bottles.py --stdout      # also print (step summary)
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
REPORT_JSON = OUT / "shop_gaps_report.json"
REPORT_MD = OUT / "shop_new_bottles.md"

CATEGORY_ORDER = ("rum", "whisky", "brandy", "gin", "tequila", "digestif", "liqueur", "wine")
CATEGORY_LABEL = {
    "rum": "Rum",
    "whisky": "Whisky",
    "brandy": "Brandy / cognac",
    "gin": "Gin",
    "tequila": "Tequila / mezcal",
    "digestif": "Digestivi",
    "liqueur": "Likeri",
    "wine": "Vino",
    None: "Nerazvrstano",
}

_VOLUME_RE = re.compile(r"\b\d+(?:[.,]\d+)?\s*(?:l|cl|ml)\b|\b0[.,]\d+\b")


def bottle_key(name: str) -> str:
    """Shop-independent key: accents, case, volume and punctuation removed."""
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = _VOLUME_RE.sub(" ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def group_bottles(rows: list[dict]) -> list[dict]:
    """Collapse the same bottle across shops; keep the lowest price."""
    by_key: dict[tuple[str | None, str], dict] = {}
    for r in rows:
        key = (r.get("suggestedCategory"), bottle_key(r.get("name") or ""))
        if not key[1]:
            continue
        g = by_key.get(key)
        offer = {
            "shop": r.get("shopLabel") or r.get("shop") or "?",
            "url": r.get("url"),
            "price": r.get("price_eur"),
        }
        if g is None:
            by_key[key] = {
                "name": (r.get("name") or "").strip(),
                "category": r.get("suggestedCategory"),
                "new": bool(r.get("newSinceLastRun")),
                "closest": r.get("matchName"),
                "score": r.get("bestScore"),
                "offers": [offer],
            }
            continue
        g["new"] = g["new"] or bool(r.get("newSinceLastRun"))
        if all(o["url"] != offer["url"] for o in g["offers"]):
            g["offers"].append(offer)
    out = list(by_key.values())
    for g in out:
        g["offers"].sort(key=lambda o: (o["price"] is None, o["price"] or 0, o["shop"]))
    return out


def _cat_rank(cat: str | None) -> int:
    return CATEGORY_ORDER.index(cat) if cat in CATEGORY_ORDER else len(CATEGORY_ORDER)


def _fmt_price(p: float | None) -> str:
    return "—" if p is None else f"{p:.2f} €".replace(".", ",")


def _offers_md(g: dict) -> str:
    parts = []
    for o in g["offers"]:
        label = f"[{o['shop']}]({o['url']})" if o.get("url") else o["shop"]
        parts.append(f"{label} {_fmt_price(o['price'])}")
    return " · ".join(parts)


def _cell(s: str) -> str:
    return (s or "").replace("|", "\\|")


def render(report: dict) -> str:
    items = report.get("items") or []
    if not report.get("hadPreviousSnapshot", True):
        items = [{**r, "newSinceLastRun": False} for r in items]
    tier_d = group_bottles([r for r in items if r.get("tier") == "D"])
    tier_c = group_bottles([r for r in items if r.get("tier") == "C"])
    failed = report.get("failedShops") or {}

    lines = [
        "# Nove boce u trgovinama",
        "",
        f"Scan: `{report.get('generatedAt')}` · trgovine: "
        + ", ".join(f"`{s}`" for s in report.get("shops") or []),
        "",
        f"- listinga: **{report.get('listingsScraped', 0)}** "
        f"(preskočeno {report.get('skippedListings', 0)} — minijature, setovi)",
        f"- **{len(tier_d)}** boca kojih nemamo (tier D)",
        f"- **{len(tier_c)}** mogućih novih izdanja postojećih (tier C, slabo poklapanje)",
        f"- tier A/B (već imamo; link/cijena se osvježava): "
        f"{report.get('tierA', 0)} / {report.get('tierB', 0)}",
    ]
    if failed:
        lines += ["", "> **Trgovine koje ovaj put nisu uspjele** (njihove boce nisu provjerene):", ">"]
        lines += [f"> - `{s}`: {why}" for s, why in sorted(failed.items())]

    lines += ["", "## Boce kojih nemamo", ""]
    if not tier_d:
        lines.append("_Nema — katalog pokriva sve što trgovine nude._")
    by_cat: dict[str | None, list[dict]] = {}
    for g in tier_d:
        by_cat.setdefault(g["category"], []).append(g)
    for cat in sorted(by_cat, key=_cat_rank):
        rows = sorted(by_cat[cat], key=lambda g: (not g["new"], g["name"].lower()))
        n_new = sum(1 for g in rows if g["new"])
        head = f"### {CATEGORY_LABEL.get(cat, cat)} ({len(rows)}"
        head += f", od toga {n_new} novo od prošlog scana)" if n_new else ")"
        lines += [head, "", "| Boca | Trgovina · cijena |", "|---|---|"]
        for g in rows:
            mark = "🆕 " if g["new"] else ""
            lines.append(f"| {mark}{_cell(g['name'])} | {_offers_md(g)} |")
        lines.append("")

    if tier_c:
        lines += [
            "## Možda novo izdanje nečega što imamo",
            "",
            "Odgovor ide u `catalog_ask_queue.json` (ista boca → tier A/B; nova → ingest).",
            "",
            "| Boca u trgovini | Najbliže u katalogu | Skor | Trgovina · cijena |",
            "|---|---|---|---|",
        ]
        for g in sorted(tier_c, key=lambda g: (_cat_rank(g["category"]), g["name"].lower())):
            lines.append(
                f"| {_cell(g['name'])} | {_cell(g.get('closest') or '')} | "
                f"{g.get('score') or ''} | {_offers_md(g)} |"
            )
        lines.append("")

    lines += [
        "## Kako dodati",
        "",
        "Lokalno, u `app/`: `python scripts/ingest-staged-drink-shops.py --apply` "
        "(tier D → stubovi, obogaćuje `enrich-shop-ingest-stubs.py`), pa "
        "`python scripts/audit_drink_shops_preship.py --check`. "
        "Nijedan drink id se ne briše bez aliasa.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", type=Path, default=REPORT_JSON)
    ap.add_argument("--out", type=Path, default=REPORT_MD)
    ap.add_argument("--stdout", action="store_true", help="Also print the Markdown")
    args = ap.parse_args()
    if not args.report.exists():
        raise SystemExit(f"missing {args.report}; run scan-drink-shop-gaps.py first")
    md = render(json.loads(args.report.read_text(encoding="utf-8")))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(md, encoding="utf-8")
    if args.stdout:
        print(md)
    else:
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
