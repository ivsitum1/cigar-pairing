# -*- coding: utf-8 -*-
"""One-shot cleanup for Task 3 review findings."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "data" / "tequilas.json"

CLASE_AZUL_IDS = {
    "tq-clase-azul-reposado",
    "tq-clase-azul-anejo",
    "tq-clase-azul-tequila-reposado-40-0-7-l-u-poklon-kutiji",
    "tq-clase-azul-tequila-plata-40-0-7-l-u-poklon-kutiji",
}

KERAMIKA_RE = re.compile(r"keramik", re.I)

HINT_EN: dict[str, str] = {
    "Gusto, desertno i polirano tijelo traži sporu punu cigaru; držite format dulji, a nikako agresivan nikotinski udar.": (
        "Dense, dessert-leaning, polished body wants a slow full cigar; keep the format longer, never an aggressive nicotine hit."
    ),
    "Habano / maduro — vanilija i hrast. Hrast i kakao traže srednje punu cigaru koja ostaje suha u finišu.": (
        "Habano / maduro — vanilla and oak. Oak and cocoa want a medium-full cigar that stays dry in the finish."
    ),
    "Agava još ostaje živa, ali hrast i vanilija već nose srednju cigaru; pustite da drugi dim dođe nakon prvog gutljaja.": (
        "Agave is still lively, but oak and vanilla already carry a medium cigar; let the second draw come after the first sip."
    ),
    "Mekši reposado s medom i vanilijom traži srednju cigaru; hrast se lijepo veže kad omot ne guri previše kakaa.": (
        "A softer reposado with honey and vanilla wants a medium cigar; oak pairs well when the wrapper does not push too much cocoa."
    ),
    "Connecticut / blagi Habano — čista agava. Agava i citrus drže lakšu do srednju cigaru bez teškog završetka.": (
        "Connecticut / mild Habano — clean agave. Agave and citrus hold a light to medium cigar without a heavy finish."
    ),
    "Connecticut / blagi Habano — čista agava. Svježiji profil drži lakšu cigaru i življi, kraći format večeri.": (
        "Connecticut / mild Habano — clean agave. A fresher profile suits a lighter cigar and a livelier, shorter evening format."
    ),
    "Habano srednje snage — agava + hrast. Vanilija i blagi hrast nose srednju cigaru bez da uguše agavu.": (
        "Medium-strength Habano — agave + oak. Vanilla and gentle oak carry a medium cigar without smothering the agave."
    ),
    "Slađi reposado i meka vanilija traže srednju cigaru koja ostaje elegantna; cijena boce je visoka, ali pairing ne mora biti težak.": (
        "A sweeter reposado and soft vanilla want a medium cigar that stays elegant; the bottle is pricey, but the pairing need not feel heavy."
    ),
    "Maduro / oscuro — gusta večer. Gusto tijelo voli sporu punu cigaru, ali ne i slatki višak.": (
        "Maduro / oscuro — a dense evening. Full body likes a slow full cigar, not a sugary excess."
    ),
    "Corojo / oscura — dim uz dim. Dim i zemljanost traže začinsku cigaru koja ne ide u sirup.": (
        "Corojo / oscuro — smoke with smoke. Smoke and earthiness want a spicy cigar that does not turn syrupy."
    ),
    "Mekši, desertniji añejo nosi maduro bez svađe, ali bolji je kada cigara zadrži papar i suhi kakao umjesto šećera.": (
        "A softer, dessert-leaning añejo carries maduro without conflict, but works best when the cigar keeps pepper and dry cocoa instead of sugar."
    ),
    "Habano / maduro — vanilija i hrast. Klasični añejo traži srednje punu cigaru koja drži hrast bez prevelike slatkoće.": (
        "Habano / maduro — vanilla and oak. A classic añejo wants a medium-full cigar that holds oak without too much sweetness."
    ),
    "Corojo / oscura — dim uz dim. Gladak mezcal drži srednju cigaru; dim neka bude slojevit, ne sirupast.": (
        "Corojo / oscuro — smoke with smoke. A smooth mezcal holds a medium cigar; keep the smoke layered, not syrupy."
    ),
}

STYLE_NOTES: dict[str, tuple[str, str]] = {
    "blanco": (
        "Blanco s čistom agavom — uz lakšu do srednju cigaru.",
        "A blanco with clean agave — with a light to medium cigar.",
    ),
    "reposado": (
        "Reposado s hrastom i vanilijom — uz srednju cigaru.",
        "A reposado with oak and vanilla — with a medium cigar.",
    ),
    "anejo": (
        "Añejo s hrastom — uz srednje punu cigaru.",
        "An añejo with oak — with a medium-full cigar.",
    ),
    "extra-anejo": (
        "Extra añejo za sporu večer — uz puniju cigaru.",
        "An extra añejo for a slow evening — with a fuller cigar.",
    ),
    "mezcal": (
        "Mezcal s dimom — uz srednju, začinsku cigaru.",
        "A smoky mezcal — with a medium, spicy cigar.",
    ),
}

MOJIBAKE = {
    "A?EJO": "AÑEJO",
    "a?ejo": "añejo",
    "Sla?i": "Slađi",
    "sla?i": "slađi",
    "Klasi?ni": "Klasični",
    "klasi?ni": "klasični",
    "tra?e": "traže",
    "te?ak": "težak",
    "fini?u": "finišu",
    " ? ": " — ",
}


def fix_mojibake(text: str) -> str:
    if not text:
        return text
    for bad, good in MOJIBAKE.items():
        if bad == "?":
            continue
        text = text.replace(bad, good)
    # Fix remaining lone ? used as em-dash in clase azul mojibake lines
    text = re.sub(r" profil \? ", " profil — ", text)
    text = re.sub(r"profil \? dio", "profil — dio", text)
    return text


def translate_hint(hr: str) -> str:
    hr = fix_mojibake(hr)
    if hr in HINT_EN:
        return HINT_EN[hr]
    style_guess = "reposado"
    low = hr.lower()
    if "connecticut" in low or "blagi habano" in low or "čista agava" in low:
        style_guess = "blanco"
    elif "maduro / oscuro" in low or "gusta večer" in low:
        style_guess = "extra-anejo"
    elif "dim" in low and "mezcal" in low or "corojo" in low:
        style_guess = "mezcal"
    elif "añejo" in low or "anejo" in low or "kakao" in low:
        style_guess = "anejo"
    fallback = {
        "blanco": "Connecticut / mild Habano — clean agave suits a light to medium cigar.",
        "reposado": "Medium-strength Habano — agave and oak carry a medium cigar.",
        "anejo": "Habano / maduro — vanilla and oak suit a medium-full cigar.",
        "extra-anejo": "Maduro / oscuro — a dense evening wants a slow full cigar.",
        "mezcal": "Corojo / oscuro — smoke with smoke; keep the cigar spicy, not syrupy.",
    }
    return fallback[style_guess]


def style_notes(style: str) -> tuple[str, str]:
    return STYLE_NOTES.get(style, STYLE_NOTES["reposado"])


def patron_silver_entry(gift: dict) -> dict:
    return {
        "id": "tq-patron-silver",
        "category": "tequila",
        "name": "Patrón Silver",
        "style": "blanco",
        "region": "Jalisco, Meksiko",
        "country": "Meksiko",
        "abv": 40.0,
        "body": 2,
        "sweetness": 2,
        "flavorTags": ["agava", "citrus", "papar", "biljno"],
        "qualityScore": 8.0,
        "priceEUR": {"min": 49.0, "max": 49.0},
        "priceApprox": False,
        "shopHR": "ecuga.com",
        "priceUrl": "https://ecuga.com/proizvod/patron-silver",
        "pairable": True,
        "serving": gift.get("serving") or {"neat": 3, "rocks": 2, "best": "Cisto / lagano ohlađeno"},
        "cigarHint": {
            "hr": "Connecticut / blagi Habano — čista agava. Svježiji profil drži lakšu cigaru i življi, kraći format večeri.",
            "en": translate_hint(
                "Connecticut / blagi Habano — čista agava. Svježiji profil drži lakšu cigaru i življi, kraći format večeri."
            ),
        },
        "notes": {
            "hr": "Glatki premium blanco — dobra ulazna točka za pairing s Connecticutom ili blagim Habano.",
            "en": "A smooth premium blanco — a good entry for pairing with Connecticut or a mild Habano.",
        },
    }


def patron_anejo_entry(gift: dict) -> dict:
    return {
        "id": "tq-patron-anejo",
        "category": "tequila",
        "name": "Patrón Añejo",
        "style": "anejo",
        "region": "Jalisco, Meksiko",
        "country": "Meksiko",
        "abv": 40.0,
        "body": 4,
        "sweetness": 3,
        "flavorTags": ["hrast", "vanilija", "karamela", "agava"],
        "qualityScore": 8.2,
        "priceEUR": {"min": 59.0, "max": 59.0},
        "priceApprox": False,
        "shopHR": "ecuga.com",
        "priceUrl": "https://ecuga.com/proizvod/patron-anejo",
        "pairable": True,
        "serving": gift.get("serving") or {"neat": 3, "rocks": 2, "best": "Cisto (snifter)"},
        "cigarHint": {
            "hr": "Habano / maduro — vanilija i hrast. Hrast i kakao traže srednje punu cigaru koja ostaje suha u finišu.",
            "en": translate_hint(
                "Habano / maduro — vanilija i hrast. Hrast i kakao traže srednje punu cigaru koja ostaje suha u finišu."
            ),
        },
        "notes": {
            "hr": "Glatki añejo s orasastim tonom — uz srednje–punu večernju cigaru.",
            "en": "A smooth añejo with a nutty tone — with a medium–full evening cigar.",
        },
    }


def gift_from(item: dict, new_id: str, name: str | None = None) -> dict:
    out = dict(item)
    out["id"] = new_id
    if name:
        out["name"] = fix_mojibake(name)
    out["meta"] = True
    out["pairable"] = False
    out.pop("status", None)
    out["status"] = "META"
    if out.get("notes"):
        hr, en = style_notes(out.get("style", "reposado"))
        if not KERAMIKA_RE.search(out["notes"].get("hr", "")) or out["id"] in CLASE_AZUL_IDS:
            pass
        else:
            out["notes"] = {"hr": hr, "en": en}
    return out


def main() -> int:
    data: list[dict] = json.loads(OUT.read_text(encoding="utf-8"))
    by_id = {d["id"]: d for d in data}
    new_rows: list[dict] = []

    # Patron gift SKUs -> new ids; restore referent ids
    if "tq-patron-silver" in by_id:
        gift_silver = by_id["tq-patron-silver"]
        new_rows.append(
            gift_from(
                gift_silver,
                "tq-gran-patron-tequila-platinum-silver-100-de-agave-40-vol-0-7l-u-poklon-kutiji",
                gift_silver["name"],
            )
        )
        by_id["tq-patron-silver"] = patron_silver_entry(gift_silver)

    if "tq-patron-anejo" in by_id:
        gift_anejo = by_id["tq-patron-anejo"]
        new_rows.append(
            gift_from(
                gift_anejo,
                "tq-gran-patron-tequila-burdeos-anejo-100-de-agave-40-vol-0-7l-u-drvenoj-poklon-kutiji",
                gift_anejo["name"],
            )
        )
        by_id["tq-patron-anejo"] = patron_anejo_entry(gift_anejo)

    # Padre Azul: SKU variant meta
    padre_sku = "tq-padre-azul-super-premium-tequila-reposado-100-agave-40-vol-0-7l"
    if padre_sku in by_id:
        row = by_id[padre_sku]
        row["meta"] = True
        row["pairable"] = False
        row["status"] = "META"
        hr, en = style_notes("reposado")
        row["notes"] = {"hr": hr, "en": en}

    padre_ref = "tq-padre-azul-reposado"
    if padre_ref in by_id:
        row = by_id[padre_ref]
        row.pop("meta", None)
        row.pop("status", None)
        row["pairable"] = True
        hr, en = style_notes("reposado")
        if KERAMIKA_RE.search(row.get("notes", {}).get("hr", "")):
            row["notes"] = {"hr": hr, "en": en}

    # Rebuild list preserving order, inserting patron gifts after originals
    out: list[dict] = []
    inserted_gifts = set()
    for d in data:
        cid = d["id"]
        if cid in by_id and cid not in inserted_gifts:
            out.append(by_id[cid])
            for g in new_rows:
                if g["id"].startswith("tq-gran-patron") and cid in ("tq-patron-silver", "tq-patron-anejo"):
                    if g["id"] not in inserted_gifts:
                        out.append(g)
                        inserted_gifts.add(g["id"])
        elif cid not in by_id:
            out.append(d)

    for g in new_rows:
        if g["id"] not in {x["id"] for x in out}:
            out.append(g)

    # Global passes
    for item in out:
        item["name"] = fix_mojibake(item.get("name", ""))
        notes = item.get("notes") or {}
        if notes.get("hr"):
            notes["hr"] = fix_mojibake(notes["hr"])
        if notes.get("en"):
            notes["en"] = fix_mojibake(notes["en"])
        item["notes"] = notes

        cid = item["id"]
        style = item.get("style", "reposado")
        nhr = notes.get("hr", "")
        if KERAMIKA_RE.search(nhr) and cid not in CLASE_AZUL_IDS:
            hr, en = style_notes(style)
            item["notes"] = {"hr": hr, "en": en}

        if item.get("meta"):
            item["pairable"] = False

        hint = item.get("cigarHint")
        if hint and hint.get("hr"):
            hint["hr"] = fix_mojibake(hint["hr"])
            hint["en"] = translate_hint(hint["hr"])
            item["cigarHint"] = hint

        if cid == "tq-herradura-anejo" and not item.get("cigarHint"):
            item["cigarHint"] = {
                "hr": "Habano / maduro — vanilija i hrast. Klasični añejo traži srednje punu cigaru koja drži hrast bez prevelike slatkoće.",
                "en": translate_hint(
                    "Habano / maduro — vanilija i hrast. Klasični añejo traži srednje punu cigaru koja drži hrast bez prevelike slatkoće."
                ),
            }

        if cid == "tq-casamigos-mezcal" and not item.get("cigarHint"):
            item["cigarHint"] = {
                "hr": "Corojo / oscura — dim uz dim. Gladak mezcal drži srednju cigaru; dim neka bude slojevit, ne sirupast.",
                "en": translate_hint(
                    "Corojo / oscura — dim uz dim. Gladak mezcal drži srednju cigaru; dim neka bude slojevit, ne sirupast."
                ),
            }

    out.sort(key=lambda d: (-(d.get("qualityScore") or 0), d.get("name", "")))
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Fixed {len(out)} tequilas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
