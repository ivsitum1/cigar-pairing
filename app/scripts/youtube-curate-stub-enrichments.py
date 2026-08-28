#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Autonomous stub → enrichment / quarantine for YouTube corpus (Phase 3).

Does not paste transcripts. Drafts original notes from catalog fields only.

    python youtube-curate-stub-enrichments.py          # write enrichments + quarantine
    python youtube-curate-stub-enrichments.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from youtube_common import channel_dir, load_channels  # noqa: E402

OUT = HERE / "output" / "youtube"
DATA = HERE / "data" / "youtube"
APP_DATA = HERE.parent / "src" / "data"

CIGAR_ENRICH = DATA / "cigar_enrichments.json"
RUM_ENRICH = DATA / "rum_enrichments.json"
QUARANTINE = DATA / "enrichment_quarantine.json"
QUEUE = OUT / "cigar_review_queue.json"

REJECT_TITLE = re.compile(
    r"\b(sampler|sample pack|gift set|gift pack|variety pack|unboxing|"
    r"top\s*\d+|ranked|brands?\s+to\s+(avoid|never)|levels?\s+of\s+rum|"
    r"vs\.?|versus|comparison)\b",
    re.I,
)


def norm(s: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def strength_band(n: int | None) -> str:
    if n is None:
        return "medium"
    if n <= 2:
        return "mild"
    if n >= 5:
        return "full"
    if n == 4:
        return "medium-full"
    return "medium"


def wrapper_family(w: str | None) -> str:
    s = (w or "").lower()
    if "connecticut" in s or "shade" in s or "ecuador" in s and "habano" not in s:
        if "maduro" in s:
            return "maduro"
        return "connecticut"
    if "maduro" in s or "brazil" in s or "san andres" in s or "oscuro" in s:
        return "maduro"
    if "corojo" in s:
        return "corojo"
    if "cameroon" in s:
        return "cameroon"
    if "habano" in s or "h-2000" in s or "cuba" in s:
        return "habano"
    if not s or s in {"—", "-", "n/a"}:
        return "natural"
    return "natural"


# Catalog countries are stored in HR; EN notes must never leak the HR form.
COUNTRY_EN: dict[str, str] = {
    "Nikaragva": "Nicaragua",
    "Honduras": "Honduras",
    "Brazil": "Brazil",
    "Dominikanska Republika": "Dominican Republic",
    "Dominikana": "Dominican Republic",
    "Kuba": "Cuba",
    "Kostarika": "Costa Rica",
    "Meksiko": "Mexico",
    "Njemačka": "Germany",
    "Španjolska": "Spain",
    "SAD": "USA",
    "Italija": "Italy",
    "Indonezija": "Indonesia",
    "Ekvador": "Ecuador",
    "Panama": "Panama",
    "Kolumbija": "Colombia",
    "Peru": "Peru",
    "Jamajka": "Jamaica",
    "Kamerun": "Cameroon",
    "Filipini": "Philippines",
    "Haiti": "Haiti",
    "Nikaragva / Honduras": "Nicaragua / Honduras",
    "Honduras / Nikaragva": "Honduras / Nicaragua",
}


def country_en(hr: str) -> str | None:
    """Map HR country label to English. Unknown → None (omit origin in EN)."""
    if not hr:
        return None
    if hr in COUNTRY_EN:
        return COUNTRY_EN[hr]
    if " / " in hr:
        parts = [country_en(p.strip()) for p in hr.split("/")]
        if all(parts):
            return " / ".join(p for p in parts if p)
        return None
    return COUNTRY_EN.get(hr)


def draft_cigar_notes(cigar: dict, brand: str, line: str) -> dict[str, str]:
    strength = cigar.get("strength")
    try:
        strength_i = int(strength) if strength is not None else None
    except (TypeError, ValueError):
        strength_i = None
    band = strength_band(strength_i)
    wrap = wrapper_family(str(cigar.get("wrapper") or ""))
    origin = cigar.get("origin") or cigar.get("country") or ""
    origin = str(origin) if origin else ""
    origin_en = country_en(origin) if origin else None

    wrap_hr = {
        "connecticut": "Connecticut shade pokrovom",
        "maduro": "tamnijim maduro pokrovom",
        "corojo": "corojo pokrovom",
        "cameroon": "Cameroon pokrovom",
        "habano": "habano pokrovom",
        "natural": "prirodnim pokrovom",
    }[wrap]
    wrap_en = {
        "connecticut": "Connecticut shade wrapper",
        "maduro": "darker maduro wrapper",
        "corojo": "corojo wrapper",
        "cameroon": "Cameroon wrapper",
        "habano": "habano wrapper",
        "natural": "natural wrapper",
    }[wrap]

    body_hr = {
        "mild": "lagano tijelo i predvidiv draw",
        "medium": "srednje tijelo i uredan ritam dimova",
        "medium-full": "srednje-puno tijelo koje traži sporiji dim",
        "full": "punije tijelo i gustoća koja traži miran ritam",
    }[band]
    body_en = {
        "mild": "light body and a predictable draw",
        "medium": "medium body and a steady puff rhythm",
        "medium-full": "medium-full body that wants a slower pace",
        "full": "fuller body and density that wants a calm rhythm",
    }[band]

    bridge_hr = {
        "connecticut": "kremasti duhan i blagi cedar umjesto oštrog začina",
        "maduro": "tamnija slatkoća, kava i toplina umjesto oštre snage",
        "corojo": "zemlja i začinski rub bez grube grubosti",
        "cameroon": "orašasti tonovi i blagi začin uz urednu konstrukciju",
        "habano": "cedar, zemlja i blagi papar u ravnoteži",
        "natural": "čist duhan i blagi začin bez dramatičnih skokova",
    }[wrap]
    bridge_en = {
        "connecticut": "creamy tobacco and soft cedar rather than sharp spice",
        "maduro": "darker sweetness, coffee and warmth rather than sharp strength",
        "corojo": "earth and a spicy edge without rough edges",
        "cameroon": "nutty tones and soft spice with tidy construction",
        "habano": "cedar, earth and soft pepper in balance",
        "natural": "clean tobacco and soft spice without dramatic jumps",
    }[wrap]

    use_hr = {
        "mild": "Dobra za gosta ili prvu cigaru za stolom; ne forsiraš je uz overproof rum.",
        "medium": "Dobra kad želiš sat vremena i profil koji drži srednju trećinu.",
        "medium-full": "Biraj je kad imaš vremena i piće koje podnese više tijela.",
        "full": "Najbolje uz piće koje podnese snagu, ne uz lagani highball.",
    }[band]
    use_en = {
        "mild": "A good guest or first-at-the-table pick; do not force it against an overproof rum.",
        "medium": "A solid pick when you want an hour and a profile that holds the middle third.",
        "medium-full": "Choose it when you have time and a drink that can carry more body.",
        "full": "Best with a drink that can carry the strength, not a light highball.",
    }[band]

    origin_bit_hr = f"iz {origin}" if origin else "s karipskom / srednjoameričkom osnovom"
    if origin_en:
        origin_bit_en = f"from {origin_en}"
    elif origin:
        # Unknown HR country: omit rather than leak into notes.en
        origin_bit_en = "on a Caribbean / Central American base"
    else:
        origin_bit_en = "on a Caribbean / Central American base"

    hr = (
        f"{line} ({brand}) ide s {wrap_hr} {origin_bit_hr} — {body_hr}. "
        f"Profil tipično drži {bridge_hr}. {use_hr}"
    )
    en = (
        f"{line} ({brand}) takes a {wrap_en} {origin_bit_en} — {body_en}. "
        f"The profile typically holds {bridge_en}. {use_en}"
    )
    return {"hr": hr, "en": en}


def draft_rum_notes(drink: dict) -> tuple[dict[str, str], dict[str, str]]:
    name = drink.get("name") or drink.get("id")
    region = drink.get("region") or drink.get("style") or ""
    body = drink.get("body")
    try:
        body_i = int(body) if body is not None else 3
    except (TypeError, ValueError):
        body_i = 3
    tags = drink.get("flavorTags") or []
    tag_hr = ", ".join(str(t).replace("-", " ") for t in tags[:3]) if tags else "hrast i suho voće"
    tag_en = ", ".join(str(t).replace("-", " ") for t in tags[:3]) if tags else "oak and dried fruit"
    sweet = drink.get("sweetness")
    try:
        sweet_i = int(sweet) if sweet is not None else 2
    except (TypeError, ValueError):
        sweet_i = 2
    additive = drink.get("additiveStatus") or ""

    if additive in {"flavored", "spiced"} or sweet_i >= 4:
        notes = {
            "hr": (
                f"{name} — {region}: {tag_hr}, izraženija slatkoća. "
                f"Često koktel ili desertni gutljaj; neat uz cigaru rijetko je prvi izbor."
            ),
            "en": (
                f"{name} — {region}: {tag_en}, higher sweetness. "
                f"Often a cocktail or dessert sip; neat with a cigar is rarely the first choice."
            ),
        }
        hint = {
            "hr": (
                "Ako ide uz dim, biraj kraći Connecticut ili blagi shade — šećer lako preglasi nijanse. "
                "Za ozbiljno sparivanje prijeđi na čisti aged rum."
            ),
            "en": (
                "If you pair it with smoke, pick a shorter Connecticut or mild shade — sugar easily covers nuance. "
                "For a serious pairing, switch to a clean aged rum."
            ),
        }
        return notes, hint

    body_phrase_hr = "laganije tijelo" if body_i <= 2 else ("punije tijelo" if body_i >= 4 else "srednje tijelo")
    body_phrase_en = "lighter body" if body_i <= 2 else ("fuller body" if body_i >= 4 else "medium body")
    notes = {
        "hr": (
            f"{name} — {region}: {tag_hr}, {body_phrase_hr}. "
            f"Čisto ili s kap vode; drži ritam uz cigaru bez pretjerane teške slatkoće."
        ),
        "en": (
            f"{name} — {region}: {tag_en}, {body_phrase_en}. "
            f"Neat or with a drop of water; keeps pace with a cigar without heavy sweetness."
        ),
    }
    if body_i >= 4:
        hint = {
            "hr": "Punije tijelo — maduro ili puni Habano; Connecticut je premalen partner. Dim i gutljaj drži u sporom ritmu.",
            "en": "Fuller body — maduro or a full Habano; Connecticut is too small a partner. Keep smoke and sip on a slow rhythm.",
        }
    elif body_i <= 2:
        hint = {
            "hr": "Laganije tijelo — Connecticut, Cameroon ili kraći format prije madura. Prva trećina cigare često dovoljna.",
            "en": "Lighter body — Connecticut, Cameroon or a shorter format before maduro. The cigar’s first third is often enough.",
        }
    else:
        hint = {
            "hr": "Srednje tijelo — Habano robusto ili zreliji corojo kao most. Izbjegni spiced rum u istoj večeri.",
            "en": "Medium body — Habano robusto or a riper corojo as the bridge. Skip spiced rum the same evening.",
        }
    return notes, hint


def classify_cigar_queue(
    queue: list[dict],
    cigars: dict[str, dict],
    existing: set[str],
) -> tuple[dict[str, dict], list[dict]]:
    by_video: dict[str, list[dict]] = {}
    for item in queue:
        if item.get("inTitle"):
            by_video.setdefault(item["videoId"], []).append(item)

    approve: dict[str, dict] = {}
    quarantine: list[dict] = []
    seen_q: set[str] = set()

    for item in queue:
        cid = item.get("cigarId") or ""
        reason = None
        if not cid:
            reason = "missing-cigarId"
        elif cid not in cigars:
            reason = "not-in-catalog"
        elif cid in existing:
            reason = "already-enriched"
        elif not item.get("inTitle"):
            reason = "not-in-title"
        elif float(item.get("confidence") or 0) < 0.9:
            reason = "low-confidence"
        elif REJECT_TITLE.search(item.get("videoTitle") or ""):
            reason = "reject-title-pattern"
        else:
            title = norm(item.get("videoTitle"))
            line = norm(item.get("line"))
            brand = norm(item.get("brand"))
            if not line or line not in title:
                reason = "line-not-in-title"
            elif brand and brand not in title:
                reason = "brand-not-in-title"
            else:
                same = by_video.get(item["videoId"], [])
                if len(same) > 3:
                    lengths = sorted(
                        (
                            (len(norm(x.get("line") or "")), x["cigarId"])
                            for x in same
                            if norm(x.get("line") or "") in title
                        ),
                        reverse=True,
                    )
                    if not lengths or lengths[0][1] != cid:
                        reason = "ambiguous-sibling-match"

        if reason:
            key = f"{cid}:{item.get('videoId')}"
            if key not in seen_q:
                seen_q.add(key)
                quarantine.append(
                    {
                        "kind": "cigar",
                        "id": cid,
                        "videoId": item.get("videoId"),
                        "title": item.get("videoTitle"),
                        "channelId": item.get("channelId"),
                        "reason": reason,
                        "matchedName": item.get("matchedName"),
                    }
                )
            continue

        # Prefer longest notes overwrite only if missing
        notes = cigars[cid].get("notes") or {}
        en = (notes.get("en") or "") if isinstance(notes, dict) else ""
        if len(en) > 140 and cid not in existing:
            quarantine.append(
                {
                    "kind": "cigar",
                    "id": cid,
                    "videoId": item.get("videoId"),
                    "title": item.get("videoTitle"),
                    "channelId": item.get("channelId"),
                    "reason": "catalog-notes-already-long",
                    "matchedName": item.get("matchedName"),
                }
            )
            continue

        if cid in approve:
            # keep higher confidence / keep video if title clearer
            prev = approve[cid]
            if float(item.get("confidence") or 0) <= float(prev.get("_confidence") or 0):
                continue

        draft = draft_cigar_notes(cigars[cid], item.get("brand") or "", item.get("line") or "")
        approve[cid] = {
            "sourceVideoIds": [item["videoId"]] if item.get("videoId") else [],
            "notes": draft,
            "_confidence": float(item.get("confidence") or 0),
            "_title": item.get("videoTitle"),
        }

    # strip private keys
    clean = {
        k: {"sourceVideoIds": v["sourceVideoIds"], "notes": v["notes"]} for k, v in approve.items()
    }
    return clean, quarantine


def classify_rum(
    drinks: dict[str, dict],
    existing: set[str],
) -> tuple[dict[str, dict], list[dict]]:
    approve: dict[str, dict] = {}
    quarantine: list[dict] = []
    seen: set[str] = set()

    for ch in load_channels():
        cid = ch["id"] if isinstance(ch, dict) else ch
        fp = channel_dir(cid) / "rum_match_proposals.json"
        if not fp.is_file():
            continue
        props = json.loads(fp.read_text(encoding="utf-8"))
        for it in props.get("proposals") or []:
            rid = it.get("drinkId") or ""
            title = it.get("title") or ""
            title_n = norm(title)
            name = norm(it.get("matchedName") or (drinks.get(rid) or {}).get("name"))
            reason = None
            if not rid:
                reason = "missing-drinkId"
            elif rid not in drinks:
                reason = "not-in-catalog"
            elif rid in existing or rid in approve:
                reason = "already-enriched"
            elif float(it.get("confidence") or 0) < 0.9:
                reason = "low-confidence"
            elif REJECT_TITLE.search(title):
                reason = "reject-title-pattern"
            elif not name or name not in title_n:
                reason = "name-not-in-title"
            elif "review" not in title_n:
                reason = "not-dedicated-review"

            if reason:
                key = f"{rid}:{it.get('videoId')}"
                if key not in seen:
                    seen.add(key)
                    quarantine.append(
                        {
                            "kind": "rum",
                            "id": rid,
                            "videoId": it.get("videoId"),
                            "title": title,
                            "channelId": cid,
                            "reason": reason,
                            "matchedName": it.get("matchedName"),
                        }
                    )
                continue

            notes, hint = draft_rum_notes(drinks[rid])
            approve[rid] = {
                "sourceVideoIds": [it["videoId"]] if it.get("videoId") else [],
                "notes": notes,
                "cigarHint": hint,
            }

    return approve, quarantine


def hr_canon_ok(notes: dict) -> str | None:
    hr = (notes.get("hr") or "").lower()
    if re.search(r"\bcigar\b", hr):
        return "hr-contains-cigar"
    if re.search(r"\bwrapper\b", hr):
        return "hr-contains-wrapper"
    if " short filler" in hr:
        return "hr-short-filler"
    if len(notes.get("hr") or "") < 40 or len(notes.get("en") or "") < 40:
        return "notes-too-short"
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    queue = json.loads(QUEUE.read_text(encoding="utf-8"))["queue"]
    cigars = {c["id"]: c for c in json.loads((APP_DATA / "cigars.json").read_text(encoding="utf-8"))}
    drinks = {d["id"]: d for d in json.loads((APP_DATA / "rums.json").read_text(encoding="utf-8"))}

    cigar_payload = json.loads(CIGAR_ENRICH.read_text(encoding="utf-8"))
    rum_payload = json.loads(RUM_ENRICH.read_text(encoding="utf-8"))
    existing_c = set(cigar_payload.get("enrichments") or {})
    existing_r = set(rum_payload.get("enrichments") or {})

    cigar_new, q_cigar = classify_cigar_queue(queue, cigars, existing_c)
    rum_new, q_rum = classify_rum(drinks, existing_r)

    # verify drafts → quarantine failures
    for cid, entry in list(cigar_new.items()):
        bad = hr_canon_ok(entry["notes"])
        if bad:
            q_cigar.append({"kind": "cigar", "id": cid, "reason": f"draft-fail:{bad}", "videoId": (entry.get("sourceVideoIds") or [None])[0]})
            del cigar_new[cid]

    for rid, entry in list(rum_new.items()):
        bad = hr_canon_ok(entry["notes"])
        if not bad and entry.get("cigarHint"):
            bad = hr_canon_ok(entry["cigarHint"])
        if bad:
            q_rum.append(
                {
                    "kind": "rum",
                    "id": rid,
                    "reason": f"draft-fail:{bad}",
                    "videoId": (entry.get("sourceVideoIds") or [None])[0],
                }
            )
            del rum_new[rid]

    # merge (keep prior curated copy; do not overwrite existing keys)
    for cid, entry in cigar_new.items():
        if cid not in cigar_payload.get("enrichments", {}):
            cigar_payload.setdefault("enrichments", {})[cid] = entry
    for rid, entry in rum_new.items():
        if rid not in rum_payload.get("enrichments", {}):
            rum_payload.setdefault("enrichments", {})[rid] = entry

    quarantine = {
        "generatedAt": "2026-08-23",
        "note": "Human decision later — do not auto-apply. Reasons explain exclusion from ship batch.",
        "counts": {
            "cigarQuarantine": len(q_cigar),
            "rumQuarantine": len(q_rum),
            "cigarApprovedNew": len(cigar_new),
            "rumApprovedNew": len(rum_new),
            "cigarEnrichmentsTotal": len(cigar_payload["enrichments"]),
            "rumEnrichmentsTotal": len(rum_payload["enrichments"]),
        },
        "items": q_cigar + q_rum,
    }

    print(json.dumps(quarantine["counts"], indent=2))

    if args.dry_run:
        return 0

    DATA.mkdir(parents=True, exist_ok=True)
    CIGAR_ENRICH.write_text(json.dumps(cigar_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    RUM_ENRICH.write_text(json.dumps(rum_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    QUARANTINE.write_text(json.dumps(quarantine, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {CIGAR_ENRICH}")
    print(f"wrote {RUM_ENRICH}")
    print(f"wrote {QUARANTINE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
