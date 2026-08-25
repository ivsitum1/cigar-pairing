#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-shot: add YouTube-gap drink SKUs (tequila / rum / bourbon).

Profiles are estimated (no HR shop scrape yet). Re-run is idempotent by id.
"""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "src" / "data"
OVERRIDES = Path(__file__).resolve().parent / "data" / "drink_brand_overrides.json"

TEQUILAS = [
    {
        "id": "tq-siete-leguas-blanco",
        "category": "tequila",
        "name": "Siete Leguas Blanco",
        "style": "blanco",
        "region": "Jalisco, Meksiko",
        "country": "Meksiko",
        "abv": 40.0,
        "body": 2,
        "sweetness": 1,
        "flavorTags": ["biljno", "citrus", "vegetalno"],
        "qualityScore": 8.4,
        "priceEUR": {"min": 40.0, "max": 50.0},
        "priceApprox": True,
        "shopHR": None,
        "priceUrl": None,
        "pairable": True,
        "serving": {"neat": 3, "rocks": 2, "best": "Cisto / lagano ohlađeno"},
        "cigarHint": {
            "hr": "Blanco profil Siete Leguas Blanco ne voli slatki maduro. Uz cigaru: Connecticut ili kratki Habano — agava ostaje čista.",
            "en": "With Siete Leguas Blanco Connecticut or a short Habano — agave stays clean. Keep the glass near the ashtray; slower loop.",
        },
        "notes": {
            "hr": "Siete Leguas Blanco (blanco) na 40 %: bilje, citrus i vegetalno uz laganije tijelo. Tradicionalna tahona linija; profil procijenjen dok nema HR cijene.",
            "en": "Siete Leguas Blanco (blanco) at 40%: herbal, citrus, vegetal with lighter body. Traditional tahona house; profile estimated until a HR price lands.",
        },
        "profileEstimated": True,
    },
    {
        "id": "tq-fortaleza-reposado",
        "category": "tequila",
        "name": "Fortaleza Reposado",
        "style": "reposado",
        "region": "Jalisco, Meksiko",
        "country": "Meksiko",
        "abv": 40.0,
        "body": 3,
        "sweetness": 2,
        "flavorTags": ["agava", "vanilija", "hrast"],
        "qualityScore": 8.8,
        "priceEUR": {"min": 65.0, "max": 80.0},
        "priceApprox": True,
        "shopHR": None,
        "priceUrl": None,
        "pairable": True,
        "serving": {"neat": 3, "rocks": 2, "best": "Cisto (snifter)"},
        "cigarHint": {
            "hr": "Reposado kao Fortaleza Reposado sjeda uz blagi maduro ili zreliji Habano. Gutljaj neka prati prvi dim; ne žuri trećinu.",
            "en": "Reposado like Fortaleza Reposado sits with a gentle maduro or warmer Habano. One sip, one draw; do not rush the middle third.",
        },
        "notes": {
            "hr": "Fortaleza Reposado (reposado) na 40 %: agava, vanilija i hrast. Tahona / bakreni kotlovi; profil procijenjen dok nema HR cijene.",
            "en": "Fortaleza Reposado (reposado) at 40%: agave, vanilla, oak. Tahona / copper stills; profile estimated until a HR price lands.",
        },
        "profileEstimated": True,
    },
    {
        "id": "tq-g4-blanco",
        "category": "tequila",
        "name": "G4 Blanco",
        "style": "blanco",
        "region": "Los Altos, Jalisco, Meksiko",
        "country": "Meksiko",
        "abv": 40.0,
        "body": 2,
        "sweetness": 1,
        "flavorTags": ["biljno", "citrus", "papar"],
        "qualityScore": 8.6,
        "priceEUR": {"min": 50.0, "max": 60.0},
        "priceApprox": True,
        "shopHR": None,
        "priceUrl": None,
        "pairable": True,
        "serving": {"neat": 3, "rocks": 2, "best": "Cisto / lagano ohlađeno"},
        "cigarHint": {
            "hr": "Uz G4 Blanco Connecticut ili kratki Habano — mineralna agava ostaje čista. Drži čašu bliže pepeljari.",
            "en": "With G4 Blanco Connecticut or a short Habano — mineral agave stays clean. Keep the glass near the ashtray.",
        },
        "notes": {
            "hr": "G4 Blanco (blanco) na 40 %: bilje, citrus i papar. Highlands / Camarena; profil procijenjen dok nema HR cijene.",
            "en": "G4 Blanco (blanco) at 40%: herbal, citrus, pepper. Highlands / Camarena; profile estimated until a HR price lands.",
        },
        "profileEstimated": True,
    },
    {
        "id": "tq-tequila-ocho-plata",
        "category": "tequila",
        "name": "Ocho Plata",
        "style": "blanco",
        "region": "Jalisco, Meksiko",
        "country": "Meksiko",
        "abv": 40.0,
        "body": 2,
        "sweetness": 1,
        "flavorTags": ["agava", "citrus", "biljno"],
        "qualityScore": 8.5,
        "priceEUR": {"min": 50.0, "max": 60.0},
        "priceApprox": True,
        "shopHR": None,
        "priceUrl": None,
        "pairable": True,
        "serving": {"neat": 3, "rocks": 2, "best": "Cisto / lagano ohlađeno"},
        "cigarHint": {
            "hr": "Blanco profil Tequila Ocho Plata ne voli slatki maduro. Jedan gutljaj, jedan dim; single-estate linija traži mirniji tempo.",
            "en": "The blanco profile of Tequila Ocho Plata does not love a sweet maduro. One sip, one draw; single-estate line wants a quieter tempo.",
        },
        "notes": {
            "hr": "Tequila Ocho Plata (blanco) na 40 %: agava, citrus i bilje. Single estate / vintage etiketa; profil procijenjen dok nema HR cijene.",
            "en": "Tequila Ocho Plata (blanco) at 40%: agave, citrus, herbal. Single-estate / vintage label; profile estimated until a HR price lands.",
        },
        "profileEstimated": True,
    },
    {
        "id": "tq-avion-reserva-44",
        "category": "tequila",
        "name": "Avión Reserva 44",
        "style": "extra-anejo",
        "region": "Jalisco, Meksiko",
        "country": "Meksiko",
        "abv": 40.0,
        "body": 4,
        "sweetness": 3,
        "flavorTags": ["hrast", "vanilija", "karamela"],
        "qualityScore": 7.2,
        "priceEUR": {"min": 140.0, "max": 160.0},
        "priceApprox": True,
        "shopHR": None,
        "priceUrl": None,
        "pairable": True,
        "serving": {"neat": 3, "rocks": 2, "best": "Cisto (snifter)"},
        "cigarHint": {
            "hr": "Extra añejo kao Avión Reserva 44 traži puniji maduro ili zreliji Habano. Status boca — pitaj što osjećaš u čaši, ne što košta.",
            "en": "Extra añejo like Avión Reserva 44 wants a fuller maduro or warmer Habano. Status bottle — ask what you feel in the glass, not the price.",
        },
        "notes": {
            "hr": "Avión Reserva 44 (extra-anejo) na 40 %: hrast, vanilija i karamela. Profil i ocjena procijenjeni; community često spominje aditive — bez propovijedi za stolom.",
            "en": "Avión Reserva 44 (extra-anejo) at 40%: oak, vanilla, caramel. Profile estimated; additive talk stays off the table unless asked.",
        },
        "profileEstimated": True,
    },
    {
        "id": "tq-818-anejo",
        "category": "tequila",
        "name": "818 Tequila Añejo",
        "style": "anejo",
        "region": "Jalisco, Meksiko",
        "country": "Meksiko",
        "abv": 40.0,
        "body": 3,
        "sweetness": 3,
        "flavorTags": ["vanilija", "karamela", "hrast"],
        "qualityScore": 6.5,
        "priceEUR": {"min": 55.0, "max": 70.0},
        "priceApprox": True,
        "shopHR": None,
        "priceUrl": None,
        "pairable": True,
        "serving": {"neat": 3, "rocks": 2, "best": "Cisto (snifter)"},
        "cigarHint": {
            "hr": "Uz 818 Tequila Añejo blagi maduro može proći; celebrity boca nije argument za sparivanje. Pitaj za miris, ne za Instagram.",
            "en": "With 818 Tequila Añejo a gentle maduro can work; celebrity label is not a pairing argument. Ask for aroma, not Instagram.",
        },
        "notes": {
            "hr": "818 Tequila Añejo (anejo) na 40 %: vanilija, karamela i hrast. Lifestyle pozicioniranje; profil procijenjen dok nema HR cijene.",
            "en": "818 Tequila Añejo (anejo) at 40%: vanilla, caramel, oak. Lifestyle positioning; profile estimated until a HR price lands.",
        },
        "profileEstimated": True,
    },
]

RUMS = [
    {
        "id": "rum-don-q-reserva-7",
        "category": "rum",
        "name": "Don Q Reserva 7",
        "style": "puerto-rico",
        "region": "Puerto Rico",
        "country": "Puerto Rico",
        "abv": 40.0,
        "body": 2,
        "sweetness": 1,
        "flavorTags": ["vanilija", "karamela", "suho-voce"],
        "additiveStatus": "clean",
        "additiveDetail": {
            "hr": "Suha, charcoal filtrirana linija — bez teškog sirupa (stilska procjena)",
            "en": "Dry, charcoal-filtered line — no heavy syrup (style estimate)",
        },
        "additiveSource": "Stilska procjena (nije lab/hidrometar)",
        "qualityScore": 7.6,
        "priceEUR": {"min": 28.0, "max": 35.0},
        "priceApprox": True,
        "shopHR": None,
        "priceUrl": None,
        "pairable": True,
        "serving": {
            "neat": 3,
            "water": 2,
            "rocks": 2,
            "highball": 1,
            "cola": 0,
            "best": "Čisto ili kap vode",
        },
        "cigarHint": {
            "hr": "S Don Q Reserva 7 uz dim biraj Connecticut ili blagi Habano — suha linija ne voli slatki maduro.",
            "en": "With Don Q Reserva 7 beside smoke pick Connecticut or a mild Habano — the dry line dislikes a sweet maduro.",
        },
        "notes": {
            "hr": "Don Q Reserva 7 (Puerto Rico) na 40 %: vanilija, karamela i suho voće uz suše tijelo. Lokalni sipper stil; profil procijenjen.",
            "en": "Don Q Reserva 7 (Puerto Rico) at 40%: vanilla, caramel, dried fruit with a drier body. Local sipper style; profile estimated.",
        },
        "profileEstimated": True,
    },
    {
        "id": "rum-ron-del-barrilito-3-star",
        "category": "rum",
        "name": "Ron del Barrilito 3 Star",
        "style": "puerto-rico",
        "region": "Puerto Rico",
        "country": "Puerto Rico",
        "abv": 43.0,
        "body": 3,
        "sweetness": 1,
        "flavorTags": ["hrast", "suho-voce", "orasasti"],
        "additiveStatus": "clean",
        "additiveDetail": {
            "hr": "Suha linija; Oloroso bačve — bez doslađivanja (stilska procjena)",
            "en": "Dry line; Oloroso casks — no dosing (style estimate)",
        },
        "additiveSource": "Stilska procjena (nije lab/hidrometar)",
        "qualityScore": 8.0,
        "priceEUR": {"min": 40.0, "max": 50.0},
        "priceApprox": True,
        "shopHR": None,
        "priceUrl": None,
        "pairable": True,
        "serving": {
            "neat": 3,
            "water": 2,
            "rocks": 1,
            "highball": 0,
            "cola": 0,
            "best": "Čisto",
        },
        "cigarHint": {
            "hr": "Srednje tijelo Ron del Barrilito 3 Star sjeda uz zreliji Habano ili blagi maduro. Suhi hrast ne voli šećerni rum istih večeri.",
            "en": "Medium body of Ron del Barrilito 3 Star sits with a riper Habano or gentle maduro. Dry oak dislikes a sugar-bomb rum the same evening.",
        },
        "notes": {
            "hr": "Ron del Barrilito 3 Star (Puerto Rico) na ~43 %: hrast, suho voće i orašasti ton. Hacienda Santa Ana; profil procijenjen dok nema HR cijene.",
            "en": "Ron del Barrilito 3 Star (Puerto Rico) at ~43%: oak, dried fruit, nutty. Hacienda Santa Ana; profile estimated until a HR price lands.",
        },
        "profileEstimated": True,
    },
]

WHISKIES = [
    {
        "id": "wh-green-river-full-proof",
        "category": "whisky",
        "name": "Green River Full Proof",
        "style": "bourbon",
        "region": "Kentucky, SAD",
        "country": "SAD",
        "abv": 58.5,
        "body": 4,
        "sweetness": 3,
        "flavorTags": ["karamela", "hrast", "zacini"],
        "additiveStatus": "clean",
        "additiveDetail": {
            "hr": "Prirodna boja; ostalo nepoznato",
            "en": "Natural colour; otherwise unknown",
        },
        "additiveSource": "Stilska procjena",
        "qualityScore": 8.2,
        "priceEUR": {"min": 38.0, "max": 45.0},
        "priceApprox": True,
        "shopHR": None,
        "priceUrl": None,
        "pairable": True,
        "serving": {
            "neat": 2,
            "water": 3,
            "rocks": 2,
            "highball": 0,
            "cola": 0,
            "best": "Kap vode (full proof)",
        },
        "cigarHint": {
            "hr": "Američki hrast u Green River Full Proof ne voli preblagi Connecticut; robusto ili maduro drži ritam.",
            "en": "With Green River Full Proof go Habano or a gentle maduro — caramel and oak want warmer smoke.",
        },
        "notes": {
            "hr": "Green River Full Proof (Kentucky, SAD) na ~58.5 %: karamela, hrast i začin u punije tijelo. Owensboro; profil procijenjen.",
            "en": "Green River Full Proof (Kentucky, USA) at ~58.5%: caramel, oak, spice in fuller body. Owensboro; profile estimated.",
        },
        "profileEstimated": True,
    },
    {
        "id": "wh-frey-ranch-straight-bourbon",
        "category": "whisky",
        "name": "Frey Ranch Straight Bourbon",
        "style": "bourbon",
        "region": "Nevada, SAD",
        "country": "SAD",
        "abv": 45.0,
        "body": 3,
        "sweetness": 3,
        "flavorTags": ["karamela", "vanilija", "papar"],
        "additiveStatus": "clean",
        "additiveDetail": {
            "hr": "Prirodna boja; ostalo nepoznato",
            "en": "Natural colour; otherwise unknown",
        },
        "additiveSource": "Stilska procjena",
        "qualityScore": 8.0,
        "priceEUR": {"min": 50.0, "max": 60.0},
        "priceApprox": True,
        "shopHR": None,
        "priceUrl": None,
        "pairable": True,
        "serving": {
            "neat": 3,
            "water": 2,
            "rocks": 2,
            "highball": 0,
            "cola": 0,
            "best": "Čisto ili kap vode",
        },
        "cigarHint": {
            "hr": "Uz Frey Ranch Straight Bourbon Habano srednjeg tijela — karamela i papar traže topliji dim.",
            "en": "With Frey Ranch Straight Bourbon a medium Habano — caramel and pepper want warmer smoke.",
        },
        "notes": {
            "hr": "Frey Ranch Straight Bourbon (Nevada, SAD) na ~45 %: karamela, vanilija i papar. Farm-to-glass; profil procijenjen.",
            "en": "Frey Ranch Straight Bourbon (Nevada, USA) at ~45%: caramel, vanilla, pepper. Farm-to-glass; profile estimated.",
        },
        "profileEstimated": True,
    },
    {
        "id": "wh-starlight-distillery-bourbon",
        "category": "whisky",
        "name": "Starlight Distillery Bourbon",
        "style": "bourbon",
        "region": "Indiana, SAD",
        "country": "SAD",
        "abv": 46.0,
        "body": 3,
        "sweetness": 3,
        "flavorTags": ["karamela", "voce", "zacini"],
        "additiveStatus": "clean",
        "additiveDetail": {
            "hr": "Prirodna boja; ostalo nepoznato",
            "en": "Natural colour; otherwise unknown",
        },
        "additiveSource": "Stilska procjena",
        "qualityScore": 8.1,
        "priceEUR": {"min": 45.0, "max": 55.0},
        "priceApprox": True,
        "shopHR": None,
        "priceUrl": None,
        "pairable": True,
        "serving": {
            "neat": 3,
            "water": 2,
            "rocks": 2,
            "highball": 0,
            "cola": 0,
            "best": "Čisto ili kap vode",
        },
        "cigarHint": {
            "hr": "Uz Starlight Distillery Bourbon Habano ili blagi maduro — karamela i začini traže topliji dim.",
            "en": "With Starlight Distillery Bourbon Habano or a gentle maduro — caramel and spice want warmer smoke.",
        },
        "notes": {
            "hr": "Starlight Distillery Bourbon (Indiana, SAD / Huber) na ~46 %: karamela, voće i začini. Farm whisky; profil procijenjen.",
            "en": "Starlight Distillery Bourbon (Indiana, USA / Huber) at ~46%: caramel, fruit, spice. Farm whiskey; profile estimated.",
        },
        "profileEstimated": True,
    },
    {
        "id": "wh-woodinville-straight-bourbon",
        "category": "whisky",
        "name": "Woodinville Straight Bourbon",
        "style": "bourbon",
        "region": "Washington, SAD",
        "country": "SAD",
        "abv": 45.0,
        "body": 3,
        "sweetness": 3,
        "flavorTags": ["karamela", "kakao", "hrast"],
        "additiveStatus": "clean",
        "additiveDetail": {
            "hr": "Prirodna boja; ostalo nepoznato",
            "en": "Natural colour; otherwise unknown",
        },
        "additiveSource": "Stilska procjena",
        "qualityScore": 8.3,
        "priceEUR": {"min": 55.0, "max": 65.0},
        "priceApprox": True,
        "shopHR": None,
        "priceUrl": None,
        "pairable": True,
        "serving": {
            "neat": 3,
            "water": 2,
            "rocks": 2,
            "highball": 0,
            "cola": 0,
            "best": "Čisto ili kap vode",
        },
        "cigarHint": {
            "hr": "Uz Woodinville Straight Bourbon zreliji Habano — karamela i hrast žele topliji dim.",
            "en": "With Woodinville Straight Bourbon a riper Habano — caramel and oak want warmer smoke.",
        },
        "notes": {
            "hr": "Woodinville Straight Bourbon (Washington, SAD) na ~45 %: karamela, kakao i hrast. Pot still / PNW; profil procijenjen.",
            "en": "Woodinville Straight Bourbon (Washington, USA) at ~45%: caramel, cocoa, oak. Pot still / PNW; profile estimated.",
        },
        "profileEstimated": True,
    },
    {
        "id": "wh-cedar-ridge-straight-bourbon",
        "category": "whisky",
        "name": "Cedar Ridge Straight Bourbon",
        "style": "bourbon",
        "region": "Iowa, SAD",
        "country": "SAD",
        "abv": 40.0,
        "body": 2,
        "sweetness": 3,
        "flavorTags": ["karamela", "vanilija", "med"],
        "additiveStatus": "clean",
        "additiveDetail": {
            "hr": "Prirodna boja; ostalo nepoznato",
            "en": "Natural colour; otherwise unknown",
        },
        "additiveSource": "Stilska procjena",
        "qualityScore": 7.5,
        "priceEUR": {"min": 40.0, "max": 50.0},
        "priceApprox": True,
        "shopHR": None,
        "priceUrl": None,
        "pairable": True,
        "serving": {
            "neat": 3,
            "water": 2,
            "rocks": 2,
            "highball": 1,
            "cola": 0,
            "best": "Čisto ili kocka leda",
        },
        "cigarHint": {
            "hr": "Uz Cedar Ridge Straight Bourbon blagi Habano ili Connecticut — pristupačna karamela ne voli preteški maduro.",
            "en": "With Cedar Ridge Straight Bourbon a mild Habano or Connecticut — approachable caramel dislikes a heavy maduro.",
        },
        "notes": {
            "hr": "Cedar Ridge Straight Bourbon (Iowa, SAD) na ~40 %: karamela, vanilija i med. Gateway Midwestern stil; profil procijenjen.",
            "en": "Cedar Ridge Straight Bourbon (Iowa, USA) at ~40%: caramel, vanilla, honey. Gateway Midwestern style; profile estimated.",
        },
        "profileEstimated": True,
    },
]

BRAND_OVERRIDES = {
    "tq-siete-leguas-blanco": "Siete Leguas",
    "tq-fortaleza-reposado": "Fortaleza",
    "tq-g4-blanco": "G4",
    "tq-tequila-ocho-plata": "Ocho",
    "tq-avion-reserva-44": "Avión",
    "tq-818-anejo": "818 Tequila",
    "rum-don-q-reserva-7": "Don Q",
    "rum-ron-del-barrilito-3-star": "Ron del Barrilito",
    "wh-green-river-full-proof": "Green River",
    "wh-frey-ranch-straight-bourbon": "Frey Ranch",
    "wh-starlight-distillery-bourbon": "Starlight Distillery",
    "wh-woodinville-straight-bourbon": "Woodinville",
    "wh-cedar-ridge-straight-bourbon": "Cedar Ridge",
}


def _load(path: Path) -> list:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump(path: Path, data: list) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def merge(path: Path, new_rows: list[dict]) -> list[str]:
    data = _load(path)
    by_id = {d["id"]: i for i, d in enumerate(data)}
    added: list[str] = []
    for row in new_rows:
        rid = row["id"]
        if rid in by_id:
            continue
        data.append(row)
        added.append(rid)
    if added:
        data.sort(key=lambda d: d["id"].lower())
        _dump(path, data)
    return added


def main() -> None:
    added: list[str] = []
    added += merge(DATA / "tequilas.json", TEQUILAS)
    added += merge(DATA / "rums.json", RUMS)
    added += merge(DATA / "whiskies.json", WHISKIES)

    reg_path = DATA / "drinkIdRegistry.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    ids = set(reg["ids"])
    new_ids = [r["id"] for r in TEQUILAS + RUMS + WHISKIES]
    for rid in new_ids:
        ids.add(rid)
    reg["ids"] = sorted(ids)
    reg_path.write_text(
        json.dumps(reg, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    ov = json.loads(OVERRIDES.read_text(encoding="utf-8"))
    brands = ov.setdefault("brands", {})
    for kid, brand in BRAND_OVERRIDES.items():
        brands[kid] = brand
    OVERRIDES.write_text(
        json.dumps(ov, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(f"added: {len(added)}")
    for rid in added:
        print(" ", rid)
    if not added:
        print("(all ids already present)")


if __name__ == "__main__":
    main()
