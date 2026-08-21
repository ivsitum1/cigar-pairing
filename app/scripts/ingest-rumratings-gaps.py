# -*- coding: utf-8 -*-
"""Append RumRatings gap bottles into rums.json + drinkIdRegistry.

Idempotent. Does not invent lab sugar figures — additive notes stay estimated
where we lack a measurement.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUMS = ROOT / "src" / "data" / "rums.json"
REGISTRY = ROOT / "src" / "data" / "drinkIdRegistry.json"

NEW = [
    {
        "id": "rum-santa-teresa-1796",
        "category": "rum",
        "name": "Santa Teresa 1796",
        "style": "venezuela",
        "region": "Venezuela (solera)",
        "abv": 40,
        "body": 3,
        "sweetness": 2,
        "flavorTags": ["hrast", "karamela", "vanilija", "suho-voce"],
        "additiveStatus": "moderate",
        "additiveDetail": {
            "hr": "Solera; umjereno doslađen profil (stilska procjena)",
            "en": "Solera; moderately sweetened profile (stylistic estimate)",
        },
        "additiveSource": "Stilska procjena — nije lab/hidrometar",
        "qualityScore": 7.5,
        "priceEUR": {"min": 45, "max": 55},
        "shopHR": "razno",
        "status": None,
        "pairable": True,
        "serving": {
            "neat": 3,
            "water": 2,
            "rocks": 3,
            "highball": 1,
            "cola": 0,
            "best": "Čisto / velika kocka leda",
        },
        "cigarHint": {
            "hr": "Most su suhi hrast i blaga karamela; radi uz srednju connecticut ili blagu maduro.",
            "en": "The bridge is dry oak and soft caramel; works with a medium Connecticut or a mild maduro.",
        },
        "priceUrl": None,
        "notes": {
            "hr": "Santa Teresa 1796 (40%) — venezuelanski solera s Hacienda Santa Teresa (Aragua). Suši je od tipičnih slatkih solera; hrast, karamela i suho voće. RumRatings ~7,5 uz stotine glasova.",
            "en": "Santa Teresa 1796 (40%) — Venezuelan solera from Hacienda Santa Teresa (Aragua). Drier than typical sweet soleras: oak, caramel and dried fruit. RumRatings ~7.5 across hundreds of votes.",
        },
        "profileEstimated": True,
        "lineup": "Santa Teresa",
    },
    {
        "id": "rum-zaya-gran-reserva-12",
        "category": "rum",
        "name": "Zaya Gran Reserva 12",
        "style": "trinidad",
        "region": "Trinidad i Tobago",
        "abv": 40,
        "body": 3,
        "sweetness": 5,
        "flavorTags": ["karamela", "vanilija", "kakao"],
        "additiveStatus": "sweetened",
        "additiveDetail": {
            "hr": "Jako doslađen dessert stil (stilska procjena / spirit drink)",
            "en": "Heavily sweetened dessert style (stylistic estimate / spirit drink)",
        },
        "additiveSource": "Stilska procjena — nije lab/hidrometar",
        "qualityScore": 5.5,
        "priceEUR": {"min": 35, "max": 50},
        "shopHR": "razno",
        "status": None,
        "pairable": True,
        "serving": {
            "neat": 2,
            "water": 1,
            "rocks": 3,
            "highball": 1,
            "cola": 1,
            "best": "Velika kocka leda",
        },
        "cigarHint": {
            "hr": "Desertni most: karamela i čokolada; biraj blagu do srednju maduro ili connecticut s kremom.",
            "en": "Dessert bridge: caramel and chocolate; pick a mild–medium maduro or a creamy Connecticut.",
        },
        "priceUrl": None,
        "notes": {
            "hr": "Zaya Gran Reserva 12 (40%) — trinidadski blend poznat po jakoj slatkoći (vanilija, karamela, kakao). U EU često kao spirit drink. Ocjena unutar doslađenog stila, ne prema ocjeni zajednice koja voli slatko.",
            "en": "Zaya Gran Reserva 12 (40%) — Trinidad blend known for heavy sweetness (vanilla, caramel, cocoa). Often labelled a spirit drink in the EU. Scored within the sweetened style, not to the community's sweet tooth.",
        },
        "profileEstimated": True,
        "lineup": "Zaya",
    },
    {
        "id": "rum-planteray-barbados-5",
        "category": "rum",
        "name": "Plantation Barbados 5 YO",
        "style": "barbados",
        "region": "Barbados",
        "abv": 40,
        "body": 2,
        "sweetness": 2,
        "flavorTags": ["tropsko-voce", "vanilija", "hrast"],
        "additiveStatus": "moderate",
        "additiveDetail": {
            "hr": "Maison Ferrand linija; blago doziranje tipično za Grand Reserve (stilska procjena)",
            "en": "Maison Ferrand line; light dosing typical of Grand Reserve (stylistic estimate)",
        },
        "additiveSource": "Stilska procjena — nije lab/hidrometar",
        "qualityScore": 7.5,
        "priceEUR": {"min": 28, "max": 38},
        "shopHR": "razno",
        "status": None,
        "pairable": True,
        "serving": {
            "neat": 2,
            "water": 2,
            "rocks": 2,
            "highball": 2,
            "cola": 1,
            "best": "Čisto ili rocks",
        },
        "cigarHint": {
            "hr": "Ulazni Barbados: tropsko voće i meki hrast; uz laganu do srednju connecticut ili mild maduro.",
            "en": "Entry Barbados: tropical fruit and soft oak; with a light–medium Connecticut or mild maduro.",
        },
        "priceUrl": None,
        "notes": {
            "hr": "Plantation/Planteray Barbados 5 YO (Grand Reserve, 40%) — ulazni odležani Barbados Maison Ferranda (West Indies Rum Distillery). Tropsko voće, vanilija, blagi hrast. Ime na etiketi može biti Plantation ili Planteray.",
            "en": "Plantation/Planteray Barbados 5 YO (Grand Reserve, 40%) — Maison Ferrand's entry aged Barbados (West Indies Rum Distillery). Tropical fruit, vanilla, soft oak. Labels may still say Plantation or Planteray.",
        },
        "profileEstimated": True,
        "lineup": "Planteray",
    },
]


def main() -> None:
    rums = json.loads(RUMS.read_text("utf-8"))
    by_id = {r["id"]: i for i, r in enumerate(rums)}
    added = 0
    for bottle in NEW:
        if bottle["id"] in by_id:
            print(f"skip existing {bottle['id']}")
            continue
        rums.append(deepcopy(bottle))
        added += 1
        print(f"+ {bottle['id']}  {bottle['name']}")

    RUMS.write_text(json.dumps(rums, ensure_ascii=False, indent=2) + "\n", "utf-8")

    reg = json.loads(REGISTRY.read_text("utf-8"))
    ids = reg.get("ids") or []
    id_set = set(ids)
    for bottle in NEW:
        if bottle["id"] not in id_set:
            ids.append(bottle["id"])
            id_set.add(bottle["id"])
    ids.sort()
    reg["ids"] = ids
    REGISTRY.write_text(json.dumps(reg, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"rums.json now {len(rums)} (+{added}); registry {len(ids)} ids")


if __name__ == "__main__":
    main()
