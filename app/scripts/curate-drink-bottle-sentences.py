#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Curate authentic bottle sentences for rum (quarantine) + whisky/gin/tequila.

Writes enrichment JSON under data/youtube/; does not paste transcripts.
Grounding: catalog name, region, flavorTags, body, additiveStatus, ABV.

    python curate-drink-bottle-sentences.py
    python curate-drink-bottle-sentences.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from youtube_common import load_channels, load_inventory, load_video  # noqa: E402
from youtube_match_lib import match_video_to_rums  # noqa: E402

DATA = HERE / "data" / "youtube"
APP = HERE.parent / "src" / "data"

TAG_HR = {
    "dim": "dim",
    "iodin": "jod",
    "medicinski": "medicinska nota",
    "hrast": "hrast",
    "karamela": "karamela",
    "vanilija": "vanilija",
    "suho-voce": "suho voće",
    "tropsko-voce": "tropsko voće",
    "voce": "voće",
    "tamno-voce": "tamno voće",
    "citrus": "citrus",
    "zacini": "začini",
    "papar": "papar",
    "med": "med",
    "cvjetno": "cvjetne note",
    "kremasto": "kremasta tekstura",
    "kakao": "kakao",
    "orasasti": "orašasti tonovi",
    "ester-funk": "esterski funk",
    "duhan": "duhan",
    "koza": "koža",
    "borovica": "borovica",
    "overproof": "jači alkohol",
}


def tags_phrase(tags: list[Any], n: int = 3) -> str:
    out: list[str] = []
    for t in tags or []:
        s = TAG_HR.get(str(t), str(t).replace("-", " "))
        if s and s not in out:
            out.append(s)
        if len(out) >= n:
            break
    if not out:
        return "čist profil bačve"
    if len(out) == 1:
        return out[0]
    if len(out) == 2:
        return f"{out[0]} i {out[1]}"
    return f"{out[0]}, {out[1]} i {out[2]}"


def body_i(drink: dict) -> int:
    try:
        return int(drink.get("body") or 3)
    except (TypeError, ValueError):
        return 3


def abv_bit(drink: dict) -> str:
    abv = drink.get("abv")
    if abv is None:
        return ""
    try:
        return f" ({float(abv):g} %)"
    except (TypeError, ValueError):
        return ""


def is_peated(drink: dict) -> bool:
    tags = {str(t) for t in (drink.get("flavorTags") or [])}
    if tags & {"dim", "iodin", "medicinski"}:
        return True
    blob = " ".join(
        [
            str(drink.get("name") or ""),
            str(drink.get("region") or ""),
            str((drink.get("notes") or {}).get("hr") or ""),
        ]
    ).lower()
    return any(x in blob for x in ("islay", "peat", "peated", "lagavulin", "laphroaig", "ardbeg"))


def whisky_notes(d: dict) -> dict[str, str]:
    name = d.get("name") or d["id"]
    region = d.get("region") or d.get("country") or "Škotska"
    tags = tags_phrase(d.get("flavorTags") or [])
    b = body_i(d)
    peat = is_peated(d)
    abv = abv_bit(d)
    body_hr = "laganije tijelo" if b <= 2 else ("punije tijelo" if b >= 4 else "srednje tijelo")
    body_en = "lighter body" if b <= 2 else ("fuller body" if b >= 4 else "medium body")

    if peat:
        # avoid "Dim i dim" when dim is already in tags
        peat_tags = tags_phrase(
            [t for t in (d.get("flavorTags") or []) if str(t) != "dim"] or ["jod", "med"],
            n=3,
        )
        hr = (
            f"{name}{abv} — {region}. Dimljeni profil: {peat_tags}; {body_hr}. "
            f"Čisto ili s kap vode; uz cigaru biraj sporiji ritam gutljaja."
        )
        en = (
            f"{name}{abv} — {region}. Peated profile: {peat_tags}; {body_en}. "
            f"Neat or with a drop of water; keep sips slow beside a cigar."
        )
    elif "bourbon" in (name or "").lower() or "kentucky" in (region or "").lower():
        hr = (
            f"{name}{abv} — {region}. Profil drži {tags} uz {body_hr}; tipičan američki hrast. "
            f"Rocks ili neat uz srednju do puniju cigaru."
        )
        en = (
            f"{name}{abv} — {region}. The profile holds {tags} with {body_en}; classic American oak. "
            f"Rocks or neat with a medium-to-fuller cigar."
        )
    elif "japan" in (region or "").lower() or "japan" in (d.get("country") or "").lower():
        hr = (
            f"{name}{abv} — {region}. {tags} u {body_hr} izrazu; često urednija, mirnija građa od peated otoka. "
            f"Neat; uz cigaru biraj čistiji Habano nego teški maduro."
        )
        en = (
            f"{name}{abv} — {region}. {tags} in a {body_en} register; often tidier than peated island malt. "
            f"Neat; beside a cigar prefer a cleaner Habano over a heavy maduro."
        )
    else:
        hr = (
            f"{name}{abv} — {region}. Profil drži {tags} uz {body_hr}. "
            f"Čisto ili s kap vode; pouzdana boca za stol uz cigaru."
        )
        en = (
            f"{name}{abv} — {region}. The profile holds {tags} with {body_en}. "
            f"Neat or with a drop of water; a steady bottle for the table with a cigar."
        )
    return {"hr": hr, "en": en}


def whisky_hint(d: dict) -> dict[str, str]:
    if is_peated(d):
        return {
            "hr": "Dim u čaši traži maduro ili puni Habano — most je pepeo i zemlja, ne citrus. Gutljaj neka bude manji.",
            "en": "Smoke in the glass wants maduro or a full Habano — bridge on ash and earth, not citrus. Keep sips smaller.",
        }
    b = body_i(d)
    tags = {str(t) for t in (d.get("flavorTags") or [])}
    if b >= 4 or tags & {"karamela", "kakao", "vanilija"}:
        return {
            "hr": "Hrast i toplije note — Habano robusto ili blagi maduro. Connecticut ostaje preblag partner.",
            "en": "Oak and warmer notes — Habano robusto or a gentle maduro. Connecticut stays too mild a partner.",
        }
    return {
        "hr": "Srednje ili laganije tijelo — Cameroon, zreliji Connecticut ili kraći Habano. Prva trećina cigare često dovoljna.",
        "en": "Medium or lighter body — Cameroon, riper Connecticut or a shorter Habano. The cigar’s first third is often enough.",
    }


def gin_notes(d: dict) -> dict[str, str]:
    name = d.get("name") or d["id"]
    region = d.get("region") or d.get("style") or "dry gin"
    tags = tags_phrase(d.get("flavorTags") or ["borovica"])
    style = str(d.get("style") or region)
    raw_tags = {str(t) for t in (d.get("flavorTags") or [])}
    serve_hr = "citrus nosi G&T" if "citrus" in raw_tags else "borovica drži martini i G&T"
    serve_en = "citrus leads a G&T" if "citrus" in raw_tags else "juniper holds martini and G&T"
    hr = (
        f"{name} — {style}. Profil drži {tags}; {serve_hr}. "
        f"Uz cigaru biraj kraći, blagi format — gin lako preglasi nijanse."
    )
    en = (
        f"{name} — {style}. The profile holds {tags}; {serve_en}. "
        f"With a cigar, prefer a shorter mild format — gin easily covers nuance."
    )
    return {"hr": hr, "en": en}


def gin_hint(d: dict) -> dict[str, str]:
    tags = {str(t) for t in (d.get("flavorTags") or [])}
    if tags & {"citrus", "cvjetno"}:
        return {
            "hr": "Citrus/cvijet — Connecticut ili panatela; maduro je pretežak. Dim neka bude rijedak između gutljaja.",
            "en": "Citrus/floral — Connecticut or panatela; maduro is too heavy. Keep puffs sparse between sips.",
        }
    return {
        "hr": "Borovica i začin — blagi Habano ili Cameroon. Ne forsiraš puni maduro uz G&T.",
        "en": "Juniper and spice — mild Habano or Cameroon. Do not force a full maduro beside a G&T.",
    }


def tequila_notes(d: dict) -> dict[str, str]:
    name = d.get("name") or d["id"]
    style = str(d.get("style") or d.get("region") or "tequila")
    tags = tags_phrase(d.get("flavorTags") or ["agave"])
    b = body_i(d)
    body_hr = "laganije tijelo" if b <= 2 else ("punije tijelo" if b >= 4 else "srednje tijelo")
    hr = (
        f"{name} — {style}. Profil drži {tags} uz {body_hr}. "
        f"Neat ili rocks; uz cigaru tempo neka bude sporiji nego uz gin."
    )
    en = (
        f"{name} — {style}. The profile holds {tags} with "
        f"{'lighter body' if b <= 2 else ('fuller body' if b >= 4 else 'medium body')}. "
        f"Neat or rocks; beside a cigar keep a slower pace than with gin."
    )
    return {"hr": hr, "en": en}


def tequila_hint(d: dict) -> dict[str, str]:
    style = str(d.get("style") or "").lower()
    if "blanco" in style or "silver" in style:
        return {
            "hr": "Blanco/agave — Connecticut ili kratki Habano; slatki maduro često zamuti agavu.",
            "en": "Blanco/agave — Connecticut or a short Habano; a sweet maduro often muddies the agave.",
        }
    return {
        "hr": "Reposado/añejo — Habano srednjeg tijela ili blagi maduro; most je hrast i karamela.",
        "en": "Reposado/añejo — medium Habano or a gentle maduro; bridge on oak and caramel.",
    }


def rum_notes(d: dict) -> dict[str, str]:
    name = d.get("name") or d["id"]
    region = d.get("region") or d.get("style") or ""
    tags = tags_phrase(d.get("flavorTags") or [])
    b = body_i(d)
    abv = abv_bit(d)
    additive = str(d.get("additiveStatus") or "")
    body_hr = "laganije tijelo" if b <= 2 else ("punije tijelo" if b >= 4 else "srednje tijelo")
    body_en = "lighter body" if b <= 2 else ("fuller body" if b >= 4 else "medium body")

    if additive in {"flavored", "spiced"} or int(d.get("sweetness") or 0) >= 4:
        hr = (
            f"{name}{abv} — {region}: {tags}, izraženija slatkoća. "
            f"Koktel ili desertni gutljaj; neat uz cigaru rijetko je prvi izbor."
        )
        en = (
            f"{name}{abv} — {region}: {tags}, higher sweetness. "
            f"Cocktail or dessert sip; neat with a cigar is rarely the first choice."
        )
    else:
        add_hr = ""
        detail = d.get("additiveDetail") or {}
        if isinstance(detail, dict) and detail.get("hr"):
            add_hr = f" {detail['hr'].rstrip('.')}."
        hr = (
            f"{name}{abv} — {region}: {tags}, {body_hr}.{add_hr} "
            f"Čisto ili s kap vode; drži ritam uz cigaru."
        )
        en = (
            f"{name}{abv} — {region}: {tags}, {body_en}. "
            f"Neat or with a drop of water; keeps pace with a cigar."
        )
    return {"hr": hr, "en": en}


def rum_hint(d: dict) -> dict[str, str]:
    additive = str(d.get("additiveStatus") or "")
    if additive in {"flavored", "spiced"} or int(d.get("sweetness") or 0) >= 4:
        return {
            "hr": "Ako ide uz dim, biraj kraći Connecticut ili blagi shade — šećer lako preglasi nijanse. Za ozbiljno sparivanje prijeđi na čisti aged rum.",
            "en": "If you pair it with smoke, pick a shorter Connecticut or mild shade — sugar easily covers nuance. For a serious pairing, switch to a clean aged rum.",
        }
    b = body_i(d)
    tags = {str(t) for t in (d.get("flavorTags") or [])}
    if b >= 4 or "ester-funk" in tags:
        return {
            "hr": "Punije tijelo ili esterski rub — maduro ili puni Habano; Connecticut je premalen. Dim i gutljaj drži u sporom ritmu.",
            "en": "Fuller body or an estery edge — maduro or a full Habano; Connecticut is too small. Keep smoke and sip on a slow rhythm.",
        }
    if b <= 2:
        return {
            "hr": "Laganije tijelo — Connecticut, Cameroon ili kraći format. Prva trećina cigare često dovoljna za most.",
            "en": "Lighter body — Connecticut, Cameroon or a shorter format. The cigar’s first third is often enough for the bridge.",
        }
    return {
        "hr": "Srednje tijelo — Habano robusto ili zreliji corojo. Izbjegni spiced rum u istoj večeri.",
        "en": "Medium body — Habano robusto or a riper corojo. Skip spiced rum the same evening.",
    }


def needs_whisky(d: dict) -> bool:
    notes = d.get("notes") or {}
    hr = (notes.get("hr") if isinstance(notes, dict) else "") or ""
    hint = d.get("cigarHint") or {}
    hhr = (hint.get("hr") if isinstance(hint, dict) else "") or ""
    if "Heuristika" in hr:
        return True
    if len(hr) < 70:
        return True
    if len(hhr) < 40:
        return True
    return False


def needs_gin(d: dict) -> bool:
    notes = d.get("notes") or {}
    hr = (notes.get("hr") if isinstance(notes, dict) else "") or ""
    return len(hr) < 75


def needs_tequila(d: dict) -> bool:
    notes = d.get("notes") or {}
    hr = (notes.get("hr") if isinstance(notes, dict) else "") or ""
    hint = d.get("cigarHint") or {}
    hhr = (hint.get("hr") if isinstance(hint, dict) else "") or ""
    return len(hr) < 90 or len(hhr) < 40


def hr_ok(block: dict) -> bool:
    hr = (block.get("hr") or "").lower()
    if len(block.get("hr") or "") < 40 or len(block.get("en") or "") < 40:
        return False
    if re.search(r"\bcigar\b", hr) or re.search(r"\bwrapper\b", hr):
        return False
    if "heuristika" in hr:
        return False
    return True


def collect_whisky_video_hits(whiskies: list[dict]) -> dict[str, str]:
    """Best videoId per whisky id from classified whisky videos (title match)."""
    best: dict[str, tuple[float, str]] = {}
    for ch in load_channels():
        inv = load_inventory(ch["id"])
        for row in inv.get("videos") or []:
            rec = load_video(ch["id"], row["videoId"])
            if not rec:
                continue
            tags = set(rec.get("tags") or [])
            title_l = (rec.get("title") or "").lower()
            if "whisky" not in tags and "whiskey" not in title_l and "whisky" not in title_l:
                continue
            # reuse rum matcher against whisky rows (same key logic)
            for prop in match_video_to_rums(video=rec, rums=whiskies, min_confidence=0.85):
                if not prop.get("title") or prop["matchedKey"] not in title_l:
                    continue
                did = prop["drinkId"]
                conf = float(prop["confidence"])
                prev = best.get(did)
                if prev is None or conf > prev[0]:
                    best[did] = (conf, prop["videoId"])
    return {k: v[1] for k, v in best.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-youtube-match", action="store_true")
    args = parser.parse_args()

    rums = json.loads((APP / "rums.json").read_text(encoding="utf-8"))
    whiskies = json.loads((APP / "whiskies.json").read_text(encoding="utf-8"))
    gins = json.loads((APP / "gins.json").read_text(encoding="utf-8"))
    tequilas = json.loads((APP / "tequilas.json").read_text(encoding="utf-8"))
    rums_by = {r["id"]: r for r in rums}
    whiskies_by = {r["id"]: r for r in whiskies}

    rum_payload = json.loads((DATA / "rum_enrichments.json").read_text(encoding="utf-8"))
    existing_rum = set(rum_payload.get("enrichments") or {})

    q = json.loads((DATA / "enrichment_quarantine.json").read_text(encoding="utf-8"))
    q_rum_ids = sorted(
        {
            i["id"]
            for i in q.get("items") or []
            if i.get("kind") == "rum" and i.get("id") in rums_by and i.get("id") not in existing_rum
        }
    )

    video_hits: dict[str, str] = {}
    if not args.skip_youtube_match:
        print("matching whisky videos…")
        video_hits = collect_whisky_video_hits(whiskies)
        print(f"whisky video hits: {len(video_hits)}")

    rum_new: dict[str, dict] = {}
    for rid in q_rum_ids:
        d = rums_by[rid]
        notes = rum_notes(d)
        hint = rum_hint(d)
        if not hr_ok(notes) or not hr_ok(hint):
            continue
        rum_new[rid] = {
            "sourceVideoIds": [],
            "notes": notes,
            "cigarHint": hint,
        }

    whisky_enr: dict[str, dict] = {}
    for d in whiskies:
        if not needs_whisky(d):
            continue
        notes = whisky_notes(d)
        hint = whisky_hint(d)
        if not hr_ok(notes) or not hr_ok(hint):
            continue
        vids = []
        if d["id"] in video_hits:
            vids = [video_hits[d["id"]]]
        whisky_enr[d["id"]] = {"sourceVideoIds": vids, "notes": notes, "cigarHint": hint}

    gin_enr: dict[str, dict] = {}
    for d in gins:
        if not needs_gin(d):
            # still ensure cigarHint length
            hint = d.get("cigarHint") or {}
            hhr = (hint.get("hr") if isinstance(hint, dict) else "") or ""
            if len(hhr) >= 40:
                continue
        notes = gin_notes(d)
        hint = gin_hint(d)
        if not hr_ok(notes) or not hr_ok(hint):
            continue
        # keep existing longer notes if already good
        old = d.get("notes") or {}
        old_hr = (old.get("hr") if isinstance(old, dict) else "") or ""
        if len(old_hr) >= 75 and "Heuristika" not in old_hr:
            notes = old if isinstance(old, dict) and old.get("en") else notes
            if not isinstance(notes, dict) or not notes.get("en"):
                notes = gin_notes(d)
        gin_enr[d["id"]] = {"sourceVideoIds": [], "notes": notes, "cigarHint": hint}

    tq_enr: dict[str, dict] = {}
    for d in tequilas:
        if not needs_tequila(d):
            continue
        old = d.get("notes") or {}
        old_hr = (old.get("hr") if isinstance(old, dict) else "") or ""
        notes = old if len(old_hr) >= 90 and isinstance(old, dict) and old.get("en") else tequila_notes(d)
        if not isinstance(notes, dict) or not notes.get("en"):
            notes = tequila_notes(d)
        hint = tequila_hint(d)
        old_h = d.get("cigarHint") or {}
        old_hhr = (old_h.get("hr") if isinstance(old_h, dict) else "") or ""
        if len(old_hhr) >= 40 and isinstance(old_h, dict) and old_h.get("en"):
            hint = old_h
        if not hr_ok(notes) or not hr_ok(hint):
            continue
        tq_enr[d["id"]] = {"sourceVideoIds": [], "notes": notes, "cigarHint": hint}

    counts = {
        "rumFromQuarantine": len(rum_new),
        "whisky": len(whisky_enr),
        "gin": len(gin_enr),
        "tequila": len(tq_enr),
    }
    print(json.dumps(counts, indent=2))

    if args.dry_run:
        return 0

    # merge rum
    rum_payload.setdefault("enrichments", {}).update(rum_new)
    (DATA / "rum_enrichments.json").write_text(
        json.dumps(rum_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    for name, payload_enr in (
        ("whisky_enrichments.json", whisky_enr),
        ("gin_enrichments.json", gin_enr),
        ("tequila_enrichments.json", tq_enr),
    ):
        doc = {
            "version": 1,
            "description": "Curated bottle notes + cigarHint (original copy; not transcript paste).",
            "enrichments": payload_enr,
        }
        (DATA / name).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # mark quarantine rum released
    released = set(rum_new)
    for item in q.get("items") or []:
        if item.get("kind") == "rum" and item.get("id") in released:
            item["status"] = "released-to-enrichment"
    q["counts"]["rumReleasedToEnrichment"] = len(released)
    (DATA / "enrichment_quarantine.json").write_text(
        json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote enrichments + updated quarantine")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
