#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge flavor enrichment into thin cigars (notes/tags).

Sources (priority):
  1. Existing notes text → flavorTags (no invention)
  2. Optional CigarWorld raw JSON if present (scrape-cigarworld-flavors.py)
  3. Wrapper / line-name heuristics → tags + structured notes; stays profileEstimated

  python scripts/merge-flavor-enrichment.py
  python scripts/merge-flavor-enrichment.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
RAW = HERE / "output" / "cigarworld_flavor_raw.json"
WORKLIST = HERE / "output" / "flavor_enrich_worklist.json"
CIGARS = DATA / "cigars.json"

WORD_TO_TAG = [
    (r"cocoa|kakao|schokolade|chocolate|čokolad|cokolad", "kakao"),
    (r"coffee|kaffee|espresso|mocha|\bkava\b", "kava"),
    (r"pepper|pfeffer|\bpapar\b|peppery", "papar"),
    (r"cream|creamy|creme|sahne|kremast", "kremasto"),
    (r"cedar|zeder|cedr|cedrovin", "cedar"),
    (r"earth|earthy|erde|erdige|zemljan|soil", "zemljano"),
    (r"nut|nuss|hazelnut|haselnuss|almond|orašast|orasast", "orasasti"),
    (r"leather|leder|\bkoža\b|\bkoza\b", "koza"),
    (r"spice|spicy|w[uü]rze|gew[uü]rz|začin|zacin", "zacini"),
    (r"sweet spice|slatki začin|slatki zacin", "zacini-slatki"),
    (r"honey|honig|\bmed\b", "med"),
    (r"caramel|karamell|karamel", "karamela"),
    (r"vanilla|vanille|vanilij", "vanilija"),
    (r"citrus|zitrus|lemon|orange|naranc", "citrus"),
    (r"floral|blumig|cvjetn", "cvjetno"),
    (r"dried fruit|trockenobst|suho.?vo", "suho-voce"),
    (r"dark fruit|dunkle.?frucht|tamno.?vo", "tamno-voce"),
    (r"fruit|frucht|\bvoce\b", "suho-voce"),
    (r"wood|holz|\bdrvo\b|woody|drvenast|toast|roast", "drvo"),
    (r"molasses|melasse|melasa", "melasa"),
    (r"grass|gras|heu|trava", "trava-slatka"),
    (r"tobacco|tabak|duhan", "duhan"),
    (r"smoke|rauch|\bdim\b", "dim"),
    (r"sweet|s[uü]ss|slatk", "slatko"),
]

WRAPPER_FROM_TEXT = [
    (r"maduro|oscuro|broadleaf|san andr", "Maduro"),
    (r"corojo", "Corojo"),
    (r"sumatra", "Sumatra"),
    (r"cameroon", "Cameroon"),
    (r"connecticut|shade|\bclaro\b|\bwhite\b", "Connecticut"),
    (r"criollo", "Criollo"),
    (r"habano|sun.?grown|sungrown|colorado|sapphire|blue", "Habano"),
]

WRAPPER_TAGS = {
    "Maduro": ["kakao", "kava", "karamela", "zemljano"],
    "Corojo": ["papar", "zacini", "koza", "cedar"],
    "Sumatra": ["kakao", "zacini", "drvo"],
    "Cameroon": ["zacini-slatki", "cedar", "orasasti"],
    "Connecticut": ["kremasto", "cedar", "orasasti", "med"],
    "Criollo": ["zemljano", "cedar", "orasasti", "zacini"],
    "Habano": ["cedar", "zacini", "koza", "kava"],
}

TAG_HR = {
    "kakao": "kakao", "kava": "kava", "zemljano": "zemljani tonovi", "koza": "koža",
    "papar": "papar", "zacini": "začini", "zacini-slatki": "slatki začini",
    "cedar": "cedrovina", "drvo": "drvo", "med": "med", "citrus": "citrus",
    "kremasto": "kremasto", "orasasti": "orašasti tonovi", "karamela": "karamela",
    "vanilija": "vanilija", "slatko": "slatkoća", "suho-voce": "suho voće",
    "tamno-voce": "tamno voće", "cvjetno": "cvjetno", "trava-slatka": "slatka trava",
    "duhan": "duhan", "dim": "dim", "melasa": "melasa",
}
TAG_EN = {
    "kakao": "cocoa", "kava": "coffee", "zemljano": "earth", "koza": "leather",
    "papar": "pepper", "zacini": "spice", "zacini-slatki": "sweet spice",
    "cedar": "cedar", "drvo": "wood", "med": "honey", "citrus": "citrus",
    "kremasto": "cream", "orasasti": "nuts", "karamela": "caramel",
    "vanilija": "vanilla", "slatko": "sweetness", "suho-voce": "dried fruit",
    "tamno-voce": "dark fruit", "cvjetno": "florals", "trava-slatka": "sweet grass",
    "duhan": "tobacco", "dim": "smoke", "melasa": "molasses",
}
EN_S = {1: "very mild", 2: "mild", 3: "medium", 4: "medium-full", 5: "full"}
EN_B = {1: "very light", 2: "light", 3: "medium", 4: "medium-full", 5: "full"}
HR_S = {1: "vrlo lagane", 2: "lagane", 3: "srednje", 4: "jače", 5: "pune"}
HR_B = {1: "vrlo laganog", 2: "laganog", 3: "srednjeg", 4: "punijeg", 5: "punog"}


def tags_from_text(text: str) -> list[str]:
    if not text:
        return []
    low = text.lower()
    found: list[str] = []
    for pat, tag in WORD_TO_TAG:
        if re.search(pat, low, re.I) and tag not in found:
            found.append(tag)
    return found[:6]


def wrapper_label(text: str | None) -> str | None:
    if not text:
        return None
    low = text.lower()
    for pat, label in WRAPPER_FROM_TEXT:
        if re.search(pat, low, re.I):
            return label
    return None


def build_notes(country: str, wrapper: str | None, strength: int, body: int, tags: list[str]) -> dict:
    w = wrapper or "natural"
    tag_hr = ", ".join(TAG_HR.get(t, t) for t in tags[:4]) or "duhanski tonovi"
    tag_en = ", ".join(TAG_EN.get(t, t) for t in tags[:4]) or "tobacco tones"
    hr = (
        f"{country or 'Mješavina'}, {w} pokrov — {HR_S.get(strength, 'srednje')} snage, "
        f"{HR_B.get(body, 'srednjeg')} tijela. Okusi: {tag_hr}."
    )
    en = (
        f"{country or 'Blend'}, {w} wrapper — {EN_S.get(strength, 'medium')} strength, "
        f"{EN_B.get(body, 'medium')} body. Notes: {tag_en}."
    )
    return {"hr": hr, "en": en}


GENERIC_TAGS = frozenset({"cedar", "zacini", "duhan", "drvo"})


def needs_tags(c: dict) -> bool:
    return len(c.get("flavorTags") or []) < 2


def needs_notes(c: dict) -> bool:
    return len(((c.get("notes") or {}).get("hr") or "").strip()) < 40


def tags_are_generic(tags: list[str]) -> bool:
    if not tags:
        return True
    return set(tags) <= GENERIC_TAGS


def merge_tags(existing: list[str], incoming: list[str]) -> list[str]:
    out: list[str] = []
    for t in incoming + existing:
        if t and t not in out:
            out.append(t)
    return out[:6]


def enrich_one(c: dict, raw: dict | None, *, batch: int = 1) -> str | None:
    """Returns source label if changed: notes|shop|heuristic|upgrade."""
    changed = False
    source = None

    note_blob = " ".join(
        [
            ((c.get("notes") or {}).get("hr") or ""),
            ((c.get("notes") or {}).get("en") or ""),
            c.get("line") or "",
            c.get("wrapper") or "",
        ]
    )
    from_notes = tags_from_text(note_blob)

    # Batch 2: upgrade tags from notes/wrapper without rewriting good notes
    if batch == 2:
        existing = list(c.get("flavorTags") or [])
        w = wrapper_label(c.get("wrapper") or "") or wrapper_label(c.get("line") or "")
        incoming = list(from_notes)
        if w and w in WRAPPER_TAGS:
            for t in WRAPPER_TAGS[w]:
                if t not in incoming:
                    incoming.append(t)
        if len(incoming) >= 2 and (
            needs_tags(c)
            or tags_are_generic(existing)
            or len(incoming) > len(existing)
            or not set(incoming).issubset(set(existing))
        ):
            merged = merge_tags(existing, incoming) if existing and not tags_are_generic(existing) else incoming[:6]
            if merged != existing:
                c["flavorTags"] = merged[:6]
                changed = True
                source = "upgrade"
        if w and (not c.get("wrapper") or c.get("wrapper") in ("—", "-", "Natural", "?")):
            c["wrapper"] = w
            changed = True
            source = source or "upgrade"
        # shop raw still wins when present
        if raw and raw.get("ok"):
            facts = raw.get("facts") or {}
            desc = (raw.get("description") or "").strip()
            blob = " ".join([*(f"{k} {v}" for k, v in facts.items()), desc, raw.get("title") or ""])
            shop_tags = tags_from_text(blob)
            if shop_tags:
                c["flavorTags"] = merge_tags(c.get("flavorTags") or [], shop_tags)[:6]
                changed = True
                source = "shop"
            for key in ("wrapper", "wrapper leaf", "deckblatt"):
                if facts.get(key):
                    raw_w = facts[key].strip()
                    if re.search(r"not available|undisclosed", raw_w, re.I):
                        continue
                    # Prefer shop's concrete leaf name; only use family label as fallback
                    labeled = wrapper_label(raw_w)
                    ww = raw_w[:40] if len(raw_w) <= 40 else (labeled or raw_w[:40])
                    cur = (c.get("wrapper") or "").strip()
                    weak = (not cur) or cur in ("—", "-", "Natural", "?", "Nicaragua", "Honduras", "Dominican Republic", "Maduro")
                    if ww:
                        c["wrapper"] = ww
                        changed = True
                        source = "shop"
                    break
            if desc and len(desc) > 80 and re.search(r"\b(the|and|with|cigar|wrapper|flavour|flavor|notes?)\b", desc, re.I):
                # only enrich EN note appendix if HR notes already exist; do not wipe
                notes = dict(c.get("notes") or {})
                en = (notes.get("en") or "").strip()
                # Replace radar-digit noise / short stubs with shop prose
                radarish = bool(re.search(r"\b(wood|pepper|cream|leather|soil)\s+\d\b", en, re.I))
                if (not en) or len(en) < 40 or radarish:
                    notes["en"] = re.sub(r"\s+", " ", desc)[:420]
                    if notes.get("hr"):
                        c["notes"] = notes
                        c["profileEstimated"] = False
                        changed = True
                        source = "shop"
        return source if changed else None

    # --- batch 1 (thin) ---
    if needs_tags(c):
        if len(from_notes) >= 2:
            c["flavorTags"] = from_notes
            changed = True
            source = "notes"

    if raw and raw.get("ok"):
        facts = raw.get("facts") or {}
        desc = (raw.get("description") or "").strip()
        blob = " ".join([*(f"{k} {v}" for k, v in facts.items()), desc, raw.get("title") or ""])
        shop_tags = tags_from_text(blob)
        w = None
        for key in ("wrapper", "deckblatt", "wrapper origin"):
            if facts.get(key):
                w = wrapper_label(facts[key]) or facts[key].strip()[:40]
                break
        if not w:
            w = wrapper_label(blob)
        if w and (not c.get("wrapper") or c.get("wrapper") in ("—", "-", "Natural", "?")):
            c["wrapper"] = w
            changed = True
        if needs_tags(c) and shop_tags:
            c["flavorTags"] = shop_tags[:6]
            changed = True
            source = "shop"
        if w and w in WRAPPER_TAGS and needs_tags(c):
            c["flavorTags"] = list(WRAPPER_TAGS[w][:4])
            changed = True
            source = source or "shop"
        if desc and len(desc) > 60 and needs_notes(c):
            base = build_notes(
                c.get("country") or "",
                c.get("wrapper"),
                int(c.get("strength") or 3),
                int(c.get("body") or 3),
                c.get("flavorTags") or shop_tags,
            )
            if re.search(r"\b(the|and|with|cigar|wrapper)\b", desc, re.I):
                base["en"] = re.sub(r"\s+", " ", desc)[:320]
            c["notes"] = base
            c["profileEstimated"] = False
            changed = True
            source = "shop"

    if needs_tags(c) or needs_notes(c):
        w = wrapper_label(c.get("wrapper") or "") or wrapper_label(c.get("line") or "")
        tags = list(c.get("flavorTags") or [])
        if len(tags) < 2:
            if w and w in WRAPPER_TAGS:
                tags = list(WRAPPER_TAGS[w][:4])
            else:
                tags = tags_from_text(note_blob) or ["cedar", "zacini", "duhan"]
            c["flavorTags"] = tags[:6]
            changed = True
            source = source or "heuristic"
        if needs_notes(c):
            c["notes"] = build_notes(
                c.get("country") or "",
                c.get("wrapper") or w,
                int(c.get("strength") or 3),
                int(c.get("body") or 3),
                c.get("flavorTags") or tags,
            )
            if c.get("profileEstimated") is not False:
                c["profileEstimated"] = True
            changed = True
            source = source or "heuristic"

    return source if changed else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--batch", type=int, choices=(1, 2), default=1)
    args = ap.parse_args()

    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in cigars}
    raw_rows = json.loads(RAW.read_text(encoding="utf-8")) if RAW.exists() else []
    raw_by_id = {r["id"]: r for r in raw_rows if r.get("id")}
    work = json.loads(WORKLIST.read_text(encoding="utf-8"))

    counts: dict[str, int] = {}
    for row in work:
        c = by_id.get(row["id"])
        if not c:
            continue
        src = enrich_one(c, raw_by_id.get(row["id"]), batch=args.batch)
        if src:
            counts[src] = counts.get(src, 0) + 1

    if not args.dry_run:
        CIGARS.write_text(json.dumps(cigars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    thin = 0
    generic = 0
    for c in cigars:
        hr = ((c.get("notes") or {}).get("hr") or "").strip()
        tags = c.get("flavorTags") or []
        if len(hr) < 40 or len(tags) < 2:
            thin += 1
        if c.get("profileEstimated") is True and tags_are_generic(tags):
            generic += 1
    print(
        f"batch={args.batch} enriched={counts} remaining_thin={thin} "
        f"estimated_generic_tags={generic} dry_run={args.dry_run}"
    )


if __name__ == "__main__":
    main()
