# -*- coding: utf-8 -*-
"""Enrich shopIngest drink stubs: category profile + name-specific notes/hints.

Offline (name + price). Uses *_shared detectors and rewrite-unique-drink-notes
pair functions so copy names the bottle instead of generic auto-ingest text.
When a dedicated YouTube review match exists in corpus_knowledge_by_topic.json
(+ full caption in output/youtube/), notes/cigarHint prefer corpus-extracted
flavor signals; otherwise heuristics.

  python scripts/enrich-shop-ingest-stubs.py --dry-run
  python scripts/enrich-shop-ingest-stubs.py --apply
  python scripts/enrich-shop-ingest-stubs.py --apply --no-corpus   # heuristics only
  python scripts/enrich-drinks-from-corpus.py --apply --category rum
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"

FILES = {
    "rum": "rums.json",
    "whisky": "whiskies.json",
    "brandy": "brandies.json",
    "gin": "gins.json",
    "tequila": "tequilas.json",
    "digestif": "digestifs.json",
}

STUB_NOTE_RE = re.compile(
    r"Automatski unos|Auto-ingested|Profil i pairable treba potvrditi",
    re.I,
)


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _rewrite():
    return _load("rewrite_unique_drink_notes", HERE / "rewrite-unique-drink-notes.py")


def _price_min(drink: dict) -> float | None:
    pe = drink.get("priceEUR")
    if isinstance(pe, dict) and pe.get("min") is not None:
        try:
            return float(pe["min"])
        except (TypeError, ValueError):
            return None
    return None


def brandy_pair(d: dict) -> tuple[dict[str, str], dict[str, str]]:
    rw = _rewrite()
    name = rw.short_name(d.get("name") or d["id"])
    region = d.get("region") or d.get("style") or "brandy"
    tags = rw.tags_list(d) or ["suho voće", "hrast"]
    tag_s = rw.tags_join(tags)
    body_hr, body_en = rw.body_word(d)
    abv = rw.abv_s(d)
    did = d["id"]
    abv_c = f" ({abv})" if abv else ""
    frames_hr = [
        f"{name}{abv_c} — {region}: {tag_s} u {body_hr}. Čisto ili nakon večere, bez žurbe.",
        f"U {name} vodi {tag_s}. Stil {region}{abv_c}; tijelo {body_hr.replace(' tijelo', '')}.",
        f"{name} drži {tag_s} bez peated buke — {region}{abv_c}, {body_hr}.",
        f"Profil {name}: {tag_s}. To je {body_hr} iz kruga {region}{abv_c}.",
    ]
    frames_en = [
        f"{name}{abv_c} — {region}: {tag_s} in {body_en}. Neat or after dinner, without haste.",
        f"In {name}, {tag_s} leads. Style {region}{abv_c}; body {body_en}.",
        f"{name} holds {tag_s} without peated noise — {region}{abv_c}, {body_en}.",
        f"Profile of {name}: {tag_s}. That is {body_en} from the {region} circle{abv_c}.",
    ]
    hints_hr = [
        f"Uz {name} srednji Habano — {tag_s} traži topliji dim, ne shade.",
        f"Tijelo {name} sjeda uz robusto; maduro samo ako boca nije suha.",
        f"Uz {name} prvi gutljaj + prva trećina cigare otkrivaju most.",
        f"Ne sparuj {name} sa spiced rumom iste večeri.",
    ]
    hints_en = [
        f"With {name} a medium Habano — {tag_s} wants warmer smoke, not shade.",
        f"The body of {name} sits with a robusto; maduro only if the bottle is not dry.",
        f"With {name} first sip + the cigar’s first third reveal the bridge.",
        f"Do not pair {name} with spiced rum the same evening.",
    ]
    return (
        {"hr": rw.hpick(did, frames_hr).strip(), "en": rw.hpick(did + ":en", frames_en).strip()},
        {"hr": rw.hpick(did + ":h", hints_hr).strip(), "en": rw.hpick(did + ":he", hints_en).strip()},
    )


def digestif_pair(d: dict) -> tuple[dict[str, str], dict[str, str]]:
    rw = _rewrite()
    name = rw.short_name(d.get("name") or d["id"])
    style = d.get("style") or "digestif"
    region = d.get("region") or ""
    tags = rw.tags_list(d) or ["biljno", "začini"]
    tag_s = rw.tags_join(tags)
    did = d["id"]
    frames_hr = [
        f"{name} ({style}) — {tag_s}. Nakon večere ili uz kratki dim; ne forsiraš tasting maraton.",
        f"U {name} biljni/gorkasti krug: {tag_s}. Regija {region or 'Europa'}.",
        f"{name} drži {tag_s}; gutljaj mali, dim rijedak.",
        f"Profil {name}: {tag_s}. Stil {style} — digestiv prije desertne slatkoće.",
    ]
    frames_en = [
        f"{name} ({style}) — {tag_s}. After dinner or with a short puff; no tasting marathon.",
        f"In {name}, herbal/bitter circle: {tag_s}. Region {region or 'Europe'}.",
        f"{name} holds {tag_s}; small sip, sparse smoke.",
        f"Profile of {name}: {tag_s}. Style {style} — digestif before dessert sweetness.",
    ]
    hints_hr = [
        f"Uz {name} kratki Habano ili panatela — gorčina traži miran format.",
        f"Ne guraj maduro uz {name}; bilje se izgubi.",
        f"Uz {name} jedan dim pa pauza — digestiv nije sipping rum.",
        f"Ako ide {name} uz cigaru, neka bude zadnji gutljaj večeri.",
    ]
    hints_en = [
        f"With {name} a short Habano or panatela — bitterness wants a calm format.",
        f"Do not push maduro with {name}; herbs get lost.",
        f"With {name} one puff then pause — digestif is not sipping rum.",
        f"If {name} meets a cigar, keep it the last sip of the evening.",
    ]
    return (
        {"hr": rw.hpick(did, frames_hr).strip(), "en": rw.hpick(did + ":en", frames_en).strip()},
        {"hr": rw.hpick(did + ":h", hints_hr).strip(), "en": rw.hpick(did + ":he", hints_en).strip()},
    )


def enrich_rum(drink: dict) -> dict[str, Any]:
    import rum_shared as rs

    name = drink.get("name") or ""
    price = _price_min(drink)
    style, region, body, sweet, tags = rs.detect_style_region(name)
    quality = rs.estimate_quality(name, price, style)
    additive, detail = rs.additive_for_style(style, name)
    abv = rs.extract_abv(name)
    serving = rs.serving_for_style(style, additive)
    pairable = rs.is_pairable(style, quality)
    patch: dict[str, Any] = {
        "style": style,
        "region": region,
        "body": body,
        "sweetness": sweet,
        "flavorTags": tags,
        "additiveStatus": additive,
        "qualityScore": quality,
        "serving": serving,
        "pairable": pairable,
        "profileEstimated": True,
    }
    if detail:
        patch["additiveDetail"] = detail
    if abv is not None:
        patch["abv"] = abv
    return patch


def enrich_whisky(drink: dict) -> dict[str, Any]:
    import whisky_shared as ws

    name = drink.get("name") or ""
    price = _price_min(drink)
    style, region, body, sweet, tags = ws.detect_style_region(name)
    expr = ws.detect_expression_type(name)
    abv = ws.extract_abv(name)
    quality = ws.estimate_quality(name, price, style, expr, abv)
    coloring = ws.detect_coloring(name, style, expr)
    filt = ws.detect_filter(name)
    additive = ws.additive_status(coloring, expr)
    serving = ws.serving_for_style(style, abv, expr)
    pairable = ws.is_pairable(expr, style, quality)
    patch: dict[str, Any] = {
        "style": style,
        "region": region,
        "body": body,
        "sweetness": sweet,
        "flavorTags": tags,
        "additiveStatus": additive,
        "qualityScore": quality,
        "serving": serving,
        "pairable": pairable,
        "profileEstimated": True,
    }
    if abv is not None:
        patch["abv"] = abv
    if filt and filt != "unknown":
        patch["filtration"] = filt
    return patch


def enrich_gin(drink: dict) -> dict[str, Any]:
    import gin_shared as gs

    name = drink.get("name") or ""
    price = _price_min(drink)
    style, region, body, sweet, botan, tags = gs.detect_style_region(name)
    abv = gs.extract_abv(name)
    quality = gs.estimate_quality(name, price, style, botan, abv)
    serving = gs.serving_for_style(style, botan)
    pairable = gs.is_pairable(name, style, quality)
    patch: dict[str, Any] = {
        "style": style,
        "region": region,
        "body": body,
        "sweetness": sweet,
        "flavorTags": tags,
        "botanicalProfile": botan,
        "additiveStatus": "unknown",
        "qualityScore": quality,
        "serving": serving,
        "pairable": pairable,
        "profileEstimated": True,
    }
    if abv is not None:
        patch["abv"] = abv
    return patch


def enrich_brandy(drink: dict) -> dict[str, Any]:
    import brandy_shared as bs

    name = drink.get("name") or ""
    price = _price_min(drink)
    style, region, body, sweet, tags = bs.detect_style_region(name)
    cat = bs.detect_category_type(name)
    age_tier = bs.detect_age_tier(name)
    abv = bs.extract_abv(name)
    quality = bs.estimate_quality(name, price, style, cat, age_tier, abv)
    serving = bs.serving_for_style(style, abv, cat)
    pairable = bs.is_pairable(cat, style, quality)
    patch: dict[str, Any] = {
        "style": style,
        "region": region,
        "body": body,
        "sweetness": sweet,
        "flavorTags": tags,
        "additiveStatus": "unknown",
        "qualityScore": quality,
        "serving": serving,
        "pairable": pairable,
        "profileEstimated": True,
    }
    if abv is not None:
        patch["abv"] = abv
    return patch


def enrich_tequila(drink: dict) -> dict[str, Any]:
    import tequila_shared as ts

    name = drink.get("name") or ""
    price = _price_min(drink)
    style, region, body, sweet, tags = ts.detect_style_region(name)
    cat = ts.detect_category_type(name)
    age_tier = ts.detect_age_tier(name)
    abv = ts.extract_abv(name)
    quality = ts.estimate_quality(name, price, style, cat, age_tier, abv)
    serving = ts.serving_for_style(style)
    pairable = ts.is_pairable(name, style, cat, quality)
    patch: dict[str, Any] = {
        "style": style,
        "region": region,
        "body": body,
        "sweetness": sweet,
        "flavorTags": tags,
        "additiveStatus": "unknown",
        "qualityScore": quality,
        "serving": serving,
        "pairable": pairable,
        "profileEstimated": True,
    }
    if abv is not None:
        patch["abv"] = abv
    return patch


def enrich_digestif(drink: dict) -> dict[str, Any]:
    import digestif_shared as ds

    name = drink.get("name") or ""
    price = _price_min(drink)
    style, region, country, body, sweet, tags = ds.detect_style_region(name)
    abv = ds.extract_abv(name)
    quality = ds.estimate_quality(name, price, style)
    serving = {"best": ds.serving_for_style(style)}
    pairable = ds.is_pairable_digestif(name)
    patch: dict[str, Any] = {
        "style": style,
        "region": region,
        "country": country,
        "body": body,
        "sweetness": sweet,
        "flavorTags": tags,
        "additiveStatus": "flavored",
        "qualityScore": quality,
        "serving": serving,
        "pairable": pairable,
        "profileEstimated": True,
    }
    if abv is not None:
        patch["abv"] = abv
    return patch


PROFILE_FN: dict[str, Callable[[dict], dict[str, Any]]] = {
    "rum": enrich_rum,
    "whisky": enrich_whisky,
    "brandy": enrich_brandy,
    "gin": enrich_gin,
    "tequila": enrich_tequila,
    "digestif": enrich_digestif,
}


def notes_for(category: str, drink: dict) -> tuple[dict[str, str], dict[str, str]]:
    rw = _rewrite()
    if category == "rum":
        return rw.rum_pair(drink)
    if category == "whisky":
        return rw.whisky_pair(drink)
    if category == "gin":
        notes, hint = rw.gin_pair(drink)
        # Prefer brand-specific gin hints when available
        try:
            import gin_shared as gs

            pair = gs.cigar_hint_pair(
                drink.get("name") or "",
                str(drink.get("style") or ""),
                str(drink.get("botanicalProfile") or ""),
            )
            if pair and pair.get("hr") and pair.get("en"):
                hint = pair
        except Exception:
            pass
        return notes, hint
    if category == "tequila":
        return rw.tequila_pair(drink)
    if category == "brandy":
        return brandy_pair(drink)
    return digestif_pair(drink)


def needs_enrich(drink: dict) -> bool:
    if drink.get("shopIngest"):
        return True
    notes = drink.get("notes") or {}
    hr = notes.get("hr") if isinstance(notes, dict) else ""
    if hr and STUB_NOTE_RE.search(hr):
        return True
    if (drink.get("region") or "") == "Nepoznato" and drink.get("profileEstimated"):
        return True
    return False


def enrich_drink(category: str, drink: dict, *, prefer_corpus: bool = True) -> bool:
    """Mutate drink in place. Return True if changed."""
    before = json.dumps(drink, sort_keys=True, ensure_ascii=False)
    patch = PROFILE_FN[category](drink)
    drink.update(patch)

    corpus_used = False
    if prefer_corpus:
        try:
            import youtube_corpus_enrich_lib as yce

            match = yce.try_corpus_enrich(drink, category)
            if match:
                yce.apply_corpus_patch(drink, match)
                corpus_used = True
        except Exception:
            pass

    if not corpus_used:
        notes, hint = notes_for(category, drink)
        drink["notes"] = notes
        drink["cigarHint"] = hint

    drink["shopIngestEnriched"] = True
    after = json.dumps(drink, sort_keys=True, ensure_ascii=False)
    return before != after


def enrich_stub_fields(category: str, stub: dict) -> dict:
    """Return a new dict with profile+notes applied (for ingest pipeline)."""
    d = dict(stub)
    enrich_drink(category, d)
    return d


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--category", default="", help="rum|whisky|brandy|gin|tequila|digestif")
    ap.add_argument("--no-corpus", action="store_true", help="Skip YouTube corpus notes; heuristics only")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    if not args.apply:
        args.dry_run = True

    cats = [args.category] if args.category else list(FILES)
    total = 0
    changed = 0
    newly_pairable = 0
    for cat in cats:
        if cat not in FILES:
            raise SystemExit(f"unknown category: {cat}")
        path = DATA / FILES[cat]
        rows = json.loads(path.read_text(encoding="utf-8"))
        file_changed = 0
        for d in rows:
            if not (d.get("shopIngest") or needs_enrich(d)):
                continue
            total += 1
            was_pairable = bool(d.get("pairable"))
            if enrich_drink(cat, d, prefer_corpus=not args.no_corpus):
                file_changed += 1
                changed += 1
            if d.get("pairable") and not was_pairable:
                newly_pairable += 1
            if args.limit and changed >= args.limit:
                break
        print(f"{FILES[cat]}: updated {file_changed}")
        if args.apply and file_changed:
            path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"  wrote {path}")
        if args.limit and changed >= args.limit:
            break

    print(f"total scanned={total} changed={changed} newly_pairable={newly_pairable}")
    if args.dry_run:
        print("dry-run: not writing")


if __name__ == "__main__":
    main()
