# -*- coding: utf-8 -*-
"""Add Jamaica Allez SKUs; update prices; backup catalog."""
from __future__ import annotations

import json
import shutil
from copy import deepcopy
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "src" / "data" / "rums.json"
OUT = Path(__file__).resolve().parent / "output"

JAM = {
    "style": "jamaica",
    "region": "Jamajka",
    "body": 3,
    "sweetness": 1,
    "flavorTags": ["ester-funk", "tropsko-voce", "hrast"],
    "additiveStatus": "clean",
    "additiveDetail": {"hr": "Čist", "en": "Clean"},
    "additiveSource": "Pravilo regije / dekl. — tipično bez doziranja",
    "qualityScore": 8.0,
    "serving": {
        "neat": 3,
        "water": 3,
        "rocks": 1,
        "highball": 1,
        "cola": 0,
        "best": "Čisto / kap vode",
    },
}
JAM_FUNK = {
    **JAM,
    "body": 4,
    "flavorTags": ["ester-funk", "tropsko-voce", "zacini"],
    "qualityScore": 8.5,
}
JAM_WHITE = {
    **JAM,
    "body": 2,
    "flavorTags": ["ester-funk", "trska", "tropsko-voce"],
    "qualityScore": 7.5,
    "serving": {
        "neat": 1,
        "water": 2,
        "rocks": 0,
        "highball": 3,
        "cola": 1,
        "best": "Koktel / Ti' Punch stil",
    },
}
NAVY = {
    "style": "navy",
    "region": "Blend (Navy)",
    "body": 4,
    "sweetness": 1,
    "flavorTags": ["ester-funk", "melasa", "zacini"],
    "additiveStatus": "clean",
    "additiveDetail": {"hr": "Čist-ish", "en": "Essentially clean"},
    "additiveSource": "Stilska procjena (navy/vatted) — nije lab mjerenje",
    "qualityScore": 8.5,
    "serving": {
        "neat": 2,
        "water": 3,
        "rocks": 2,
        "highball": 1,
        "cola": 0,
        "best": "Čisto / kap vode",
    },
}
BB_WHITE = {
    "style": "barbados",
    "region": "Barbados",
    "body": 2,
    "sweetness": 1,
    "flavorTags": ["trska", "citrus", "hrast"],
    "additiveStatus": "clean",
    "additiveDetail": {"hr": "Čist", "en": "Clean"},
    "additiveSource": "Dekl. (Foursquare)",
    "qualityScore": 7.5,
    "serving": {
        "neat": 2,
        "water": 2,
        "rocks": 1,
        "highball": 3,
        "cola": 1,
        "best": "Koktel / rocks",
    },
}


def make(id_: str, name: str, price: float, tpl: dict, hr: str, en: str, **extra) -> dict:
    d = {
        "id": id_,
        "category": "rum",
        "name": name,
        **deepcopy(tpl),
        "priceEUR": {"min": price, "max": price},
        "shopHR": "allez.hr",
        "status": None,
        "pairable": True,
        "cigarHint": None,
        "priceUrl": None,
        "notes": {"hr": hr, "en": en},
    }
    d.update(extra)
    return d


NEW = [
    make(
        "rum-cdi-jamaica-5",
        "Compagnie des Indes Jamaica 5 Ans",
        44.10,
        JAM,
        "CDI Jamaica 5 ans (43%) — nezavisni bottling, čist jamajčanski ester profil.",
        "CDI Jamaica 5 ans (43%) — independent bottling, clean Jamaican ester profile.",
        qualityScore=7.8,
    ),
    make(
        "rum-cdi-jamaica-navy-5",
        "Compagnie des Indes Jamaica Navy Strength 5 YO",
        49.46,
        {**JAM_FUNK, "qualityScore": 8.0},
        "CDI Jamaica Navy Strength 5 YO (57%) — jači jamajčanski blend/bottling.",
        "CDI Jamaica Navy Strength 5 YO (57%) — stronger Jamaican blend/bottling.",
    ),
    make(
        "rum-habitation-velier-svm-plummer-14",
        "Habitation Velier SVM EMB Plummer 14 YO",
        179.71,
        {**JAM_FUNK, "qualityScore": 9.0},
        "HV SVM EMB Plummer 14 YO Tropical Aging (69,7%) — vatted single, high-proof Hampden-stil.",
        "HV SVM EMB Plummer 14 YO Tropical Aging (69.7%) — vatted single, high-proof Hampden style.",
    ),
    make(
        "rum-velier-tiger-shark-2019",
        "Velier Royal Navy Tiger Shark 2019",
        177.72,
        NAVY,
        "Velier Royal Navy Tiger Shark Release 2019 (57,2%) — pure vatted navy rum.",
        "Velier Royal Navy Tiger Shark Release 2019 (57.2%) — pure vatted navy rum.",
        qualityScore=8.8,
    ),
    make(
        "rum-hampden-rum-fire",
        "Hampden Estate Rum Fire",
        39.39,
        {**JAM_WHITE, "qualityScore": 8.0},
        "Hampden Rum Fire White Overproof (63%) — ekstremni esteri, bijeli overproof.",
        "Hampden Rum Fire White Overproof (63%) — extreme esters, white overproof.",
    ),
    make(
        "rum-exchange-hampden-5-2013",
        "Rum Exchange Hampden 5 YO #001 2013",
        100.89,
        {**JAM_FUNK, "qualityScore": 8.6},
        "Rum Exchange Jamaica Hampden 5 YO #001 2013 (61,5%) — pure single cask-ish bottling.",
        "Rum Exchange Jamaica Hampden 5 YO #001 2013 (61.5%) — pure single cask-ish bottling.",
    ),
    make(
        "rum-kill-devil-hampden-35-1983",
        "Hunter Laing Kill Devil Hampden 35 YO 1983",
        956.50,
        {**JAM_FUNK, "body": 4, "qualityScore": 9.5},
        "Kill Devil Hampden 35 YO 1983 (58,1%) — raritetni cask strength single cask.",
        "Kill Devil Hampden 35 YO 1983 (58.1%) — rare cask-strength single cask.",
    ),
    make(
        "rum-worthy-park-10-madeira-2010",
        "Worthy Park 10 YO Madeira 2010",
        102.80,
        {**JAM, "flavorTags": ["ester-funk", "suho-voce", "hrast"], "qualityScore": 8.4},
        "Worthy Park 10 YO Madeira Special Cask 2010 (45%) — madeira finish.",
        "Worthy Park 10 YO Madeira Special Cask 2010 (45%) — Madeira finish.",
    ),
    make(
        "rum-worthy-park-10-port-2010",
        "Worthy Park 10 YO Port 2010",
        99.99,
        {**JAM, "flavorTags": ["ester-funk", "crveno-voce", "hrast"], "qualityScore": 8.4},
        "Worthy Park 10 YO Port Special Cask 2010 (45%) — port finish.",
        "Worthy Park 10 YO Port Special Cask 2010 (45%) — port finish.",
    ),
    make(
        "rum-worthy-park-12-2006",
        "Worthy Park 12 YO 2006",
        140.11,
        {**JAM_FUNK, "qualityScore": 8.8},
        "Worthy Park 12 YO Single Estate 2006 (56%) — starija WP ekspresija, cask strength-ish.",
        "Worthy Park 12 YO Single Estate 2006 (56%) — older WP expression, cask-strength-ish.",
    ),
    make(
        "rum-worthy-park-oloroso-2013",
        "Worthy Park Oloroso 2013",
        85.35,
        {**JAM, "flavorTags": ["ester-funk", "suho-voce", "hrast"], "qualityScore": 8.3},
        "Worthy Park Oloroso Special Cask 2013 (55%) — oloroso sherry finish.",
        "Worthy Park Oloroso Special Cask 2013 (55%) — oloroso sherry finish.",
    ),
    make(
        "rum-worthy-park-select",
        "Worthy Park Select",
        36.80,
        {**JAM, "body": 2, "qualityScore": 7.2},
        "Worthy Park Select (40%) — ulazni single estate jamajčanski rum.",
        "Worthy Park Select (40%) — entry single-estate Jamaican rum.",
    ),
    make(
        "rum-exchange-worthy-park-5-2013",
        "Rum Exchange Worthy Park 5 YO #002 2013",
        101.10,
        {**JAM_FUNK, "qualityScore": 8.5},
        "Rum Exchange Jamaica Worthy Park 5 YO #002 2013 (59%) — pure single bottling.",
        "Rum Exchange Jamaica Worthy Park 5 YO #002 2013 (59%) — pure single bottling.",
    ),
    make(
        "rum-habitation-velier-forsyths-151",
        "Habitation Velier Forsyths 151 Proof White",
        67.00,
        {**JAM_WHITE, "qualityScore": 8.2},
        "HV Forsyths 151 Proof White (75,5%) — ekstremni bijeli jamajčanski pure single.",
        "HV Forsyths 151 Proof White (75.5%) — extreme white Jamaican pure single.",
    ),
    make(
        "rum-papalin-5-overproof",
        "Habitation Velier Papalin 5 YO Overproof",
        77.90,
        {**JAM_FUNK, "qualityScore": 8.3},
        "Papalin 5 YO Jamaica High Ester Overproof (57%) — visoki esteri, overproof.",
        "Papalin 5 YO Jamaica High Ester Overproof (57%) — high esters, overproof.",
    ),
    make(
        "rum-papalin-5",
        "Habitation Velier Papalin 5 YO",
        65.90,
        {**JAM_FUNK, "qualityScore": 8.1},
        "Papalin 5 YO Jamaica High Ester (47%) — high ester pot still stil.",
        "Papalin 5 YO Jamaica High Ester (47%) — high-ester pot-still style.",
    ),
    make(
        "rum-papalin-7",
        "Habitation Velier Papalin 7 YO",
        72.00,
        {**JAM_FUNK, "qualityScore": 8.3},
        "Papalin 7 YO Jamaica Pot Still (47%) — duže odležani Papalin.",
        "Papalin 7 YO Jamaica Pot Still (47%) — longer-aged Papalin.",
    ),
    make(
        "rum-papalin-reunion-10",
        "Habitation Velier Papalin Réunion 10 YO",
        117.80,
        {
            **JAM,
            "region": "Réunion / Jamajka (Papalin)",
            "body": 4,
            "qualityScore": 8.6,
            "flavorTags": ["ester-funk", "hrast", "suho-voce"],
        },
        "Papalin Réunion 10 YO (50%) — Papalin linija s Réunion oznakom; kompleksan pure single stil.",
        "Papalin Réunion 10 YO (50%) — Papalin line with Réunion label; complex pure-single style.",
    ),
]

PRICE_UPDATES = {
    "rum-appleton-estate-12": (55.60, "Appleton Estate 12 YO Rare Casks"),
    "rum-appleton-estate-15-black-river": (83.50, "Appleton Estate 15 YO Black River Casks"),
    "rum-appleton-estate-21": (203.00, "Appleton Estate 21 YO Rare Limited Edition"),
    "rum-appleton-estate-8-reserve": (41.80, "Appleton Estate Reserve 8"),
    "rum-hampden-estate-8": (75.55, "Hampden Estate 8 YO"),
    "rum-hampden-hlcf-classic-60": (113.59, "Hampden HLCF Classic"),
    "rum-wray-nephew-overproof-63": (31.33, "Wray & Nephew Overproof"),
    "rum-worthy-park-109": (44.98, "Worthy Park 109"),
    "rum-worthy-park-single-estate": (67.60, "Worthy Park Single Estate Reserve"),
    "rum-smith-cross": (34.00, "Smith & Cross Traditional Jamaica Rum"),
    "rum-veritas-foursquare-white": (36.80, "Veritas Foursquare White"),
}


def main() -> None:
    rums = json.loads(P.read_text(encoding="utf-8"))
    by = {r["id"]: r for r in rums}

    for rid, (price, name) in PRICE_UPDATES.items():
        r = by.get(rid)
        if not r:
            print("missing for update", rid)
            continue
        r["priceEUR"] = {"min": price, "max": price}
        r["name"] = name
        r["shopHR"] = "allez.hr"
        print("updated", rid)

    added = 0
    for item in NEW:
        if item["id"] in by:
            by[item["id"]]["priceEUR"] = item["priceEUR"]
            print("price refresh", item["id"])
            continue
        rums.append(item)
        by[item["id"]] = item
        added += 1
        print("added", item["id"])

    P.write_text(json.dumps(rums, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(P, OUT / f"rums-allez-backup-{stamp}.json")
    shutil.copy2(P, OUT / "rums-allez-latest.json")
    print(f"added={added} total={len(rums)}")


if __name__ == "__main__":
    main()
