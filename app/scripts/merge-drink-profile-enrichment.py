# -*- coding: utf-8 -*-
"""Map drink PDP / Wine-Searcher text → flavorTags / notes / body / sweetness (fill-thin).

  python scripts/merge-drink-profile-enrichment.py --dry-run
  python scripts/merge-drink-profile-enrichment.py
  python scripts/merge-drink-profile-enrichment.py --file tequilas.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
PDP = HERE / "output" / "drink_pdp_raw.json"
WS = HERE / "output" / "wine_searcher_raw.json"
REPORT = HERE / "output" / "drink_profile_enrich_report.json"

# Canonical tags used by pairing engine / enrich-rum-taste-notes
CANON_SYNONYMS: list[tuple[str, list[str]]] = [
    ("vanilija", ["vanilla", "vanilija", "vanille"]),
    ("karamela", ["caramel", "karamela", "toffee", "butterscotch"]),
    ("hrast", ["oak", "hrast", "woody", "wood", "barrel", "bačv"]),
    ("suho-voce", ["dried fruit", "suho voce", "raisin", "fig", "prune", "date", "sultana"]),
    ("tropsko-voce", ["tropical", "mango", "pineapple", "banana", "papaya", "tropsko"]),
    ("citrus", ["citrus", "orange", "lemon", "lime", "grapefruit", "bergamot", "naranca"]),
    ("zacini", ["spice", "spicy", "pepper", "cinnamon", "clove", "nutmeg", "zacin", "papar", "cimet"]),
    ("dim", ["smoke", "smoky", "peat", "peated", "dim", "torf"]),
    ("med", ["honey", "med", "miel"]),
    ("cvjetno", ["floral", "flower", "blossom", "cvjet", "rose", "heather"]),
    ("orasasti", ["nut", "almond", "hazelnut", "walnut", "orasast", "nougat"]),
    ("kakao", ["cocoa", "chocolate", "kakao", "cacao", "mocha"]),
    ("kava", ["coffee", "espresso", "kava"]),
    ("melasa", ["molasses", "melasa", "treacle"]),
    ("travnato", ["grassy", "grass", "herbaceous", "travnat", "fresh cut"]),
    ("vegetalno", ["vegetal", "olive", "vegetalno", "green"]),
    ("ester-funk", ["funk", "ester", "overripe", "banana ester"]),
    ("voce", ["fruit", "fruity", "voce", "berry", "apple", "pear"]),
    ("tamno-voce", ["dark fruit", "blackcurrant", "cherry", "plum", "blackberry"]),
    ("duhan", ["tobacco", "duhan", "cigar"]),
    ("slatko", ["sweet", "sweetness", "dosladen", "syrupy"]),
    ("sol", ["salt", "saline", "maritime", "sea", "sol"]),
    ("medicinski", ["medicinal", "iodine", "phenol", "medicinski"]),
    ("kremasto", ["creamy", "cream", "butter", "kremasto", "velvety"]),
    ("kokos", ["coconut", "kokos"]),
    ("papar", ["black pepper", "peppercorn", "papar"]),
    ("agava", ["agave", "agava"]),
    ("zemljano", ["earthy", "earth", "zemljan"]),
]

BODY_HINTS = [
    (5, [r"full[\s-]?bodied", r"punog? tijela", r"very full", r"rich and full", r"teško tijelo"]),
    (4, [r"full body", r"medium[\s-]full", r"puno tijelo", r"robust", r"powerful"]),
    (2, [r"light[\s-]?bodied", r"lagan", r"delicate", r"fine and light", r"easy drinking"]),
    (1, [r"very light", r"vrlo lagan", r"wispy"]),
    (3, [r"medium[\s-]?bodied", r"medium body", r"srednje", r"balanced body"]),
]

SWEET_HINTS = [
    (5, [r"very sweet", r"dessert[\s-]?like", r"syrupy", r"doslađen", r"liqueur[\s-]?like"]),
    (4, [r"(?<!dried )(?<!dry-)(?<!semi[\s-])\bsweet\b", r"sweetness", r"slatk", r"honeyed"]),
    (1, [r"bone dry", r"\bsuho\b", r"not sweet", r"unsweetened", r"(?<!dried )(?<!semi[\s-])\bdry\b(?![\s-]fruit|ed)"]),
    (2, [r"off[\s-]?dry", r"slightly sweet", r"semi[\s-]?dry", r"polusuho"]),
]


def map_tags(text: str) -> list[str]:
    low = text.lower()
    found: list[str] = []
    for canon, syns in CANON_SYNONYMS:
        if any(s in low for s in syns):
            found.append(canon)
    # stable unique, max 6
    out: list[str] = []
    for t in found:
        if t not in out:
            out.append(t)
    return out[:6]


def map_body(text: str) -> int | None:
    low = text.lower()
    for val, pats in BODY_HINTS:
        for p in pats:
            if re.search(p, low):
                return val
    return None


def map_sweet(text: str) -> int | None:
    low = text.lower()
    for val, pats in SWEET_HINTS:
        for p in pats:
            if re.search(p, low):
                return val
    return None


def thin_notes(notes) -> bool:
    if not notes:
        return True
    if isinstance(notes, dict):
        hr = notes.get("hr") or ""
        return len(hr) < 80
    return len(str(notes)) < 80


def thin_tags(tags: list | None) -> bool:
    return not tags or len(tags) < 3


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--file",
        action="append",
        dest="files",
        help="Limit to catalog file(s), e.g. tequilas.json (repeatable)",
    )
    args = ap.parse_args()
    allow_files = set(args.files) if args.files else None

    pages = []
    if PDP.exists():
        pages.extend(json.loads(PDP.read_text(encoding="utf-8")).get("pages") or [])
    if WS.exists():
        pages.extend(json.loads(WS.read_text(encoding="utf-8")).get("pages") or [])

    by_id: dict[str, dict] = {}
    for p in pages:
        if not p.get("id") or not p.get("text"):
            continue
        if allow_files and p.get("file") not in allow_files:
            continue
        # skip empty / junk-thin copy — never fabricate notes
        if len((p.get("text") or "").strip()) < 80:
            continue
        prev = by_id.get(p["id"])
        if not prev or len(p.get("text") or "") > len(prev.get("text") or ""):
            by_id[p["id"]] = p

    report = []
    file_cache: dict[str, list] = {}

    for drink_id, page in by_id.items():
        fname = page.get("file")
        if not fname:
            continue
        if allow_files and fname not in allow_files:
            continue
        if fname not in file_cache:
            path = DATA / fname
            if not path.exists():
                continue
            file_cache[fname] = json.loads(path.read_text(encoding="utf-8"))
        rows = file_cache[fname]
        drink = next((d for d in rows if d.get("id") == drink_id), None)
        if not drink:
            continue

        text = page.get("text") or ""
        tags = map_tags(text)
        body = map_body(text)
        sweet = map_sweet(text)
        changes = {}

        if tags:
            old = list(drink.get("flavorTags") or [])
            if thin_tags(old):
                drink["flavorTags"] = tags
                changes["flavorTags"] = {"from": old, "to": tags}
            else:
                merged = list(old)
                for t in tags:
                    if t not in merged:
                        merged.append(t)
                merged = merged[:6]
                if merged != old:
                    drink["flavorTags"] = merged
                    changes["flavorTags"] = {"from": old, "to": merged}

        if body is not None and (thin_tags(drink.get("flavorTags")) or True):
            # only change body when explicit shop signal and current is default-ish mid
            old_b = drink.get("body")
            if old_b in (None, 3) or (body != old_b and abs((old_b or 3) - body) >= 1 and thin_notes(drink.get("notes"))):
                if old_b != body and (old_b in (None, 2, 3) or thin_notes(drink.get("notes"))):
                    drink["body"] = body
                    changes["body"] = {"from": old_b, "to": body}

        if sweet is not None:
            old_s = drink.get("sweetness")
            if old_s in (None, 2, 3) and sweet != old_s:
                drink["sweetness"] = sweet
                changes["sweetness"] = {"from": old_s, "to": sweet}

        if thin_notes(drink.get("notes")) and len(text) > 80:
            snippet = re.sub(r"\s+", " ", text).strip()[:280]
            drink["notes"] = {
                "hr": snippet,
                "en": snippet,
            }
            changes["notes"] = "filled_from_pdp"

        if changes and len(text) >= 200:
            drink["profileEstimated"] = False
            changes["profileEstimated"] = False

        if changes:
            report.append({"id": drink_id, "file": fname, "url": page.get("url"), "changes": changes})

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({"count": len(report), "items": report}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"enrich candidates={len(report)} -> {REPORT}")
    if args.dry_run:
        print("dry-run: not writing")
        return
    if not report:
        print("no changes")
        return
    for fname, rows in file_cache.items():
        (DATA / fname).write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  wrote {fname}")


if __name__ == "__main__":
    main()
