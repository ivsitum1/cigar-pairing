# -*- coding: utf-8 -*-
"""Ingest Allez rum SKUs missing from rums.json (Martinique + Caribbean paste).

Idempotent: skips ids already present; updates priceEUR for known matches when listed.
Skips packaging-only variants (sa 2 čaše, duplicate gift boxes) and advent calendars.
"""
from __future__ import annotations

import json
import re
import unicodedata
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUMS = ROOT / "src" / "data" / "rums.json"

# --- templates by family ---------------------------------------------------

AGRI = {
    "style": "agricole",
    "region": "Agricole (Martinique)",
    "body": 2,
    "sweetness": 1,
    "flavorTags": ["travnato", "citrus", "vanilija"],
    "additiveStatus": "clean",
    "additiveDetail": {"hr": "Bez aditiva (AOC)", "en": "No additives (AOC)"},
    "additiveSource": "AOC zakon (zabranjeni aditivi)",
    "qualityScore": 8.0,
    "serving": {
        "neat": 3,
        "water": 3,
        "rocks": 1,
        "highball": 2,
        "cola": 0,
        "best": "Čisto / Ti' Punch",
    },
}

AGRI_AGED = {
    **AGRI,
    "body": 3,
    "flavorTags": ["travnato", "hrast", "suho-voce"],
    "qualityScore": 8.5,
    "serving": {
        "neat": 3,
        "water": 2,
        "rocks": 0,
        "highball": 0,
        "cola": 0,
        "best": "Čisto",
    },
}

AGRI_BLANC = {
    **AGRI,
    "body": 1,
    "flavorTags": ["travnato", "vegetalno", "citrus"],
    "qualityScore": 7.5,
    "serving": {
        "neat": 2,
        "water": 2,
        "rocks": 0,
        "highball": 3,
        "cola": 0,
        "best": "Ti' Punch",
    },
}

RIISE = {
    "style": "other",
    "region": "Danska (spirit drink)",
    "body": 3,
    "sweetness": 4,
    "flavorTags": ["karamela", "vanilija"],
    "additiveStatus": "sweetened",
    "additiveDetail": {
        "hr": "Dodani šećer (spirit drink)",
        "en": "Added sugar (spirit drink)",
    },
    "additiveSource": "Stilska procjena (doslađen profil) — nije lab/hidrometar",
    "qualityScore": 5.5,
    "serving": {
        "neat": 2,
        "water": 2,
        "rocks": 3,
        "highball": 2,
        "cola": 1,
        "best": "Velika kocka leda",
    },
}

RIISE_SPICED = {
    **RIISE,
    "style": "spiced",
    "region": "Spiced / spirit drink (Danska)",
    "body": 2,
    "sweetness": 5,
    "flavorTags": ["vanilija", "zacini"],
    "qualityScore": 5.0,
    "serving": {
        "neat": 1,
        "water": 0,
        "rocks": 2,
        "highball": 3,
        "cola": 3,
        "best": "Koktel / highball",
    },
}

ST_LUCIA = {
    "style": "st-lucia",
    "region": "Sv. Lucija",
    "body": 3,
    "sweetness": 1,
    "flavorTags": ["vanilija", "duhan", "hrast"],
    "additiveStatus": "clean",
    "additiveDetail": {"hr": "Čist/vrlo nizak", "en": "Clean / very low"},
    "additiveSource": "Stilska procjena (St Lucia Distillers) — nije lab mjerenje",
    "qualityScore": 8.0,
    "serving": {
        "neat": 3,
        "water": 3,
        "rocks": 2,
        "highball": 1,
        "cola": 0,
        "best": "Čisto / kap vode",
    },
}

BLEND = {
    "style": "blend",
    "region": "Blend (vise regija)",
    "body": 3,
    "sweetness": 2,
    "flavorTags": ["suho-voce", "hrast"],
    "additiveStatus": "clean",
    "additiveDetail": {"hr": "Čist (bottler)", "en": "Clean (bottler)"},
    "additiveSource": "Dekl. (bottler)",
    "qualityScore": 8.0,
    "serving": {
        "neat": 3,
        "water": 3,
        "rocks": 1,
        "highball": 0,
        "cola": 0,
        "best": "Čisto / kap vode",
    },
}

NIC = {
    "style": "nicaragua-dry",
    "region": "Nikaragva",
    "body": 2,
    "sweetness": 1,
    "flavorTags": ["hrast", "vanilija"],
    "additiveStatus": "clean",
    "additiveDetail": {"hr": "Čist (deklaracija)", "en": "Clean (declared)"},
    "additiveSource": "Dekl. (Flor de Caña)",
    "qualityScore": 7.0,
    "serving": {
        "neat": 2,
        "water": 2,
        "rocks": 2,
        "highball": 2,
        "cola": 1,
        "best": "Čisto / rocks",
    },
}

LIQUEUR = {
    "style": "liqueur",
    "region": "Liker (rum baza)",
    "body": 1,
    "sweetness": 5,
    "flavorTags": ["slatko", "citrus"],
    "additiveStatus": "flavored",
    "additiveDetail": {
        "hr": "Rum liker / aromatizirano",
        "en": "Rum liqueur / flavoured",
    },
    "additiveSource": "Stilska procjena (aromatizirano) — nije lab mjerenje",
    "qualityScore": 5.0,
    "serving": {
        "neat": 1,
        "water": 0,
        "rocks": 2,
        "highball": 2,
        "cola": 1,
        "best": "Rocks / koktel",
    },
}


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def entry(id_: str, name: str, price: float, tpl: dict, notes_hr: str, notes_en: str, **extra) -> dict:
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
        "notes": {"hr": notes_hr, "en": notes_en},
    }
    d.update(extra)
    return d


# Products to add (id, display name, price EUR, template, notes hr/en)
NEW: list[dict] = []


def add(id_: str, name: str, price: float, tpl: dict, hr: str, en: str, **extra) -> None:
    NEW.append(entry(id_, name, price, tpl, hr, en, **extra))


# === Martinique / agricole ================================================
add(
    "rum-clement-blanc-canne-bleue",
    "Clément Blanc Canne Bleue",
    31.52,
    AGRI_BLANC,
    "Clément Canne Bleue je bijeli agricole (50%) s Habitation Clément — svježa trska, citrus i biljni ton. Klasik za Ti' Punch.",
    "Clément Canne Bleue is a white agricole (50%) from Habitation Clément — fresh cane, citrus and herbal tone. A Ti' Punch classic.",
    qualityScore=7.8,
)
add(
    "rum-clement-ambre",
    "Clément Agricole Ambré",
    26.25,
    AGRI,
    "Clément Ambré je kratko odležani agricole: još travnat, s blagim hrastom i vanilijom. Lagani sipper ili Ti' Punch.",
    "Clément Ambré is a briefly aged agricole: still grassy, with light oak and vanilla. Light sipper or Ti' Punch.",
    qualityScore=7.2,
)
add(
    "rum-clement-select-barrel",
    "Clément Select Barrel",
    36.30,
    AGRI,
    "Clément Select Barrel (40%) spaja agricole travnatost s kraćim hrastom — pristupačni martinique stil.",
    "Clément Select Barrel (40%) joins agricole grassiness with shorter oak — an approachable Martinique style.",
    qualityScore=7.4,
)
add(
    "rum-clement-10-ans",
    "Clément 10 Ans",
    95.50,
    AGRI_AGED,
    "Clément 10 Ans: deset godina u hrastu — mokka, suho voće i začin nad agricole bazom. Namijenjen čistom servisu.",
    "Clément 10 Ans: ten years in oak — mocha, dried fruit and spice over an agricole base. Meant for neat service.",
    qualityScore=8.8,
)
add(
    "rum-clement-15-ans",
    "Clément 15 Ans",
    159.39,
    AGRI_AGED,
    "Clément 15 Ans je starija Habitation ekspresija: dublji hrast, suho voće i mirnija travnata kičma.",
    "Clément 15 Ans is an older Habitation expression: deeper oak, dried fruit and a quieter grassy spine.",
    body=4,
    qualityScore=9.0,
)
add(
    "rum-clement-xo",
    "Clément XO",
    69.90,
    AGRI_AGED,
    "Clément XO (42%) dulje odležava od VSOP-a: više hrasta, kakaa i kandiranog voća uz AOC agricole bazu.",
    "Clément XO (42%) ages longer than VSOP: more oak, cocoa and candied fruit on an AOC agricole base.",
    qualityScore=8.6,
)
add(
    "rum-clement-single-batch-canne-bleue",
    "Clément Single Batch Canne Bleue",
    66.90,
    AGRI_AGED,
    "Clément Très Rhum Single Batch 100% Canne Bleue (46,1%, 0,5 l) — uža serija, intenzivnija trska i začin.",
    "Clément Très Rhum Single Batch 100% Canne Bleue (46.1%, 0.5 l) — a tighter batch, more intense cane and spice.",
    qualityScore=8.4,
)
add(
    "rum-clement-moka-torrefie",
    "Clément Single Cask Moka Torréfié",
    60.52,
    AGRI_AGED,
    "Clément Single Cask Moka Torréfié 05 (41,8%, 0,5 l) — finish s pečenom kavom nad agricole kičmom.",
    "Clément Single Cask Moka Torréfié 05 (41.8%, 0.5 l) — roasted-coffee finish over an agricole spine.",
    flavorTags=["travnato", "kava", "hrast"],
    qualityScore=8.3,
)
add(
    "rum-clement-chauffe-extreme",
    "Clément Chauffe Extrême Single Batch",
    59.99,
    AGRI_AGED,
    "Clément Chauffe Extrême Single Batch (46,9%, 0,5 l) — limited, intenzivniji pečeni/hrastov profil.",
    "Clément Chauffe Extrême Single Batch (46.9%, 0.5 l) — limited, more intense roasted/oak profile.",
    qualityScore=8.3,
)
add(
    "rum-depaz-vsop",
    "Depaz VSOP",
    61.58,
    AGRI,
    "Depaz VSOP (45%) s Saint-Pierrea: vulkansko tlo, travnata trska i blagi hrast. Puniji od Plantationa.",
    "Depaz VSOP (45%) from Saint-Pierre: volcanic soil, grassy cane and light oak. Fuller than Plantation.",
    qualityScore=8.0,
)
add(
    "rum-hse-vo",
    "HSE VO",
    64.50,
    AGRI,
    "HSE VO (42%) je mlađi vieux Habitation Saint-Étienne — citrus, trska i lagani hrast.",
    "HSE VO (42%) is a younger vieux from Habitation Saint-Étienne — citrus, cane and light oak.",
    qualityScore=7.8,
)
add(
    "rum-hse-black-sheriff",
    "HSE Black Sheriff",
    45.80,
    AGRI,
    "HSE Black Sheriff American Barrel (40%) — agricole u američkom hrastu: vanilija i blagi begin uz travnatu bazu.",
    "HSE Black Sheriff American Barrel (40%) — agricole in American oak: vanilla and light toast over a grassy base.",
    flavorTags=["travnato", "vanilija", "hrast"],
    qualityScore=7.8,
)
add(
    "rum-hse-port-cask-finish",
    "HSE VSOP Port Cask Finish",
    75.39,
    AGRI_AGED,
    "HSE VSOP Port Cask Finish (45%) — agricole VSOP s port finishom: crveno voće nad travnatom kičmom.",
    "HSE VSOP Port Cask Finish (45%) — agricole VSOP with port finish: red fruit over a grassy spine.",
    flavorTags=["travnato", "crveno-voce", "hrast"],
    qualityScore=8.2,
)
add(
    "rum-hse-kilchoman-cask-finish",
    "HSE Kilchoman Cask Finish 2014",
    99.53,
    AGRI_AGED,
    "HSE Extra Vieux Kilchoman Cask Finish 2014 (44%, 0,5 l) — peaty Islay finish nad martinique agricole.",
    "HSE Extra Vieux Kilchoman Cask Finish 2014 (44%, 0.5 l) — peaty Islay finish over Martinique agricole.",
    flavorTags=["travnato", "dim", "hrast"],
    qualityScore=8.5,
)
add(
    "rum-jm-epices-creoles",
    "Rhum J.M Épices Créoles",
    49.90,
    AGRI,
    "J.M Épices Créoles (46%) — agricole s kreolskim začinom; jači začinski ton uz travnatu bazu.",
    "J.M Épices Créoles (46%) — agricole with Creole spice; stronger spice over a grassy base.",
    flavorTags=["travnato", "zacini", "citrus"],
    qualityScore=7.8,
)
add(
    "rum-jm-fumee-volcanique",
    "Rhum J.M Fumée Volcanique",
    39.90,
    AGRI,
    "J.M Fumée Volcanique (49%) — dimljeni/vulkanski karakter uz agricole trsku; intenzivniji sipper.",
    "J.M Fumée Volcanique (49%) — smoked/volcanic character with agricole cane; a more intense sipper.",
    flavorTags=["travnato", "dim", "zacini"],
    qualityScore=8.0,
)
add(
    "rum-jm-canopee",
    "Rhum J.M Canopée Hors d'Âge",
    173.20,
    AGRI_AGED,
    "J.M Canopée Hors d'Âge (46%) — novija premium linija; dubok hrast i zrela trska.",
    "J.M Canopée Hors d'Âge (46%) — newer premium line; deep oak and ripe cane.",
    body=4,
    qualityScore=9.0,
)
add(
    "rum-jm-millesime-2004",
    "Rhum J.M Millésimé 2004",
    188.47,
    AGRI_AGED,
    "J.M Vieux Agricole Millésimé 2004 (42,9%) — berba 2004, duga odležavanja, kompleksan hors d'âge.",
    "J.M Vieux Agricole Millésimé 2004 (42.9%) — 2004 vintage, long ageing, complex hors d'âge.",
    body=4,
    qualityScore=9.1,
)
add(
    "rum-jm-millesime-2011",
    "Rhum J.M Millésimé 2011",
    95.69,
    AGRI_AGED,
    "J.M Vieux Agricole Millésimé 2011 (41,9%) — berba 2011; zreli hrast uz agricole bazu.",
    "J.M Vieux Agricole Millésimé 2011 (41.9%) — 2011 vintage; ripe oak over an agricole base.",
    qualityScore=8.7,
)
add(
    "rum-jm-single-barrel-1999",
    "Rhum J.M Single Barrel 1999",
    274.53,
    AGRI_AGED,
    "J.M Single Barrel Hors d'Âge 1999 (43,6%, 0,5 l) — limited single barrel, raritetna berba.",
    "J.M Single Barrel Hors d'Âge 1999 (43.6%, 0.5 l) — limited single barrel, rare vintage.",
    body=4,
    qualityScore=9.2,
)
add(
    "rum-jm-single-barrel-2015",
    "Rhum J.M Single Barrel 2015",
    102.59,
    AGRI_AGED,
    "J.M Single Barrel Vieux 2015 (55,1%) — cask strength single barrel, intenzivniji agricole.",
    "J.M Single Barrel Vieux 2015 (55.1%) — cask-strength single barrel, more intense agricole.",
    qualityScore=8.8,
)
add(
    "rum-trois-rivieres-cannes-brulees",
    "Trois Rivières Cannes Brûlées",
    45.61,
    AGRI,
    "Trois Rivières Cannes Brûlées (43%) — pečena trska/karamelizirani ton uz agricole kičmu.",
    "Trois Rivières Cannes Brûlées (43%) — roasted cane/caramelised tone over an agricole spine.",
    flavorTags=["travnato", "karamela", "hrast"],
    qualityScore=7.8,
)
add(
    "rum-trois-rivieres-cuvee-ocean",
    "Trois Rivières Cuvée de l'Océan",
    34.63,
    AGRI_BLANC,
    "Trois Rivières Cuvée de l'Océan (42%) — svježi, mineralniji agricole; dobar za Ti' Punch.",
    "Trois Rivières Cuvée de l'Océan (42%) — fresher, more mineral agricole; good for Ti' Punch.",
    qualityScore=7.5,
)
add(
    "rum-trois-rivieres-cuvee-moulin",
    "Trois Rivières Cuvée du Moulin",
    46.39,
    AGRI,
    "Trois Rivières Cuvée du Moulin (40%) — klasični vieux/ambre stil s blagim hrastom.",
    "Trois Rivières Cuvée du Moulin (40%) — classic vieux/ambre style with light oak.",
    qualityScore=7.6,
)
add(
    "rum-clement-creole-shrubb",
    "Clément Créole Shrubb",
    30.26,
    LIQUEUR,
    "Clément Créole Shrubb (40%) — narančasti rum-liker s Martiniquea; za Ti' Punch varijante i rocks.",
    "Clément Créole Shrubb (40%) — orange rum liqueur from Martinique; for Ti' Punch variants and rocks.",
)
add(
    "rum-jm-shrubb",
    "J.M Shrubb Liqueur d'Orange",
    29.68,
    LIQUEUR,
    "J.M Shrubb (35%) — narančasti rum-liker Habitation Bellevue; desertniji od čistog agricole.",
    "J.M Shrubb (35%) — orange rum liqueur from Habitation Bellevue; sweeter than neat agricole.",
)

# === A.H. Riise ============================================================
add(
    "rum-ah-riise-1888-copenhagen-gold",
    "A.H. Riise 1888 Copenhagen Gold Medal",
    57.44,
    RIISE,
    "A.H. Riise 1888 Copenhagen Gold Medal (40%) — slađeni spirit drink, mekani karamelni profil.",
    "A.H. Riise 1888 Copenhagen Gold Medal (40%) — sweetened spirit drink, soft caramel profile.",
)
add(
    "rum-ah-riise-black-barrel-navy-spiced",
    "A.H. Riise Black Barrel Navy Spiced",
    40.50,
    RIISE_SPICED,
    "A.H. Riise Black Barrel Navy Spiced (40%) — spiced spirit drink; vanilija i začin za highball.",
    "A.H. Riise Black Barrel Navy Spiced (40%) — spiced spirit drink; vanilla and spice for highballs.",
)
add(
    "rum-ah-riise-frigate-jylland",
    "A.H. Riise Royal Danish Navy Frigate Jylland",
    63.40,
    RIISE,
    "A.H. Riise Frigate Jylland (45%) — navy linija, slađeni superior spirit drink.",
    "A.H. Riise Frigate Jylland (45%) — navy line, sweetened superior spirit drink.",
)
add(
    "rum-ah-riise-family-reserve-1838",
    "A.H. Riise Family Reserve Solera 1838",
    81.45,
    RIISE,
    "A.H. Riise Family Reserve Solera 1838 (42%) — starija solera, mekana i slatkasta.",
    "A.H. Riise Family Reserve Solera 1838 (42%) — older solera, soft and sweetish.",
    qualityScore=6.0,
)
add(
    "rum-ah-riise-npu-ambre-dor",
    "A.H. Riise Non Plus Ultra Ambre d'Or",
    94.99,
    RIISE,
    "A.H. Riise Non Plus Ultra Ambre d'Or (42%) — premium slađeni profil, desertniji od XO Reserve.",
    "A.H. Riise Non Plus Ultra Ambre d'Or (42%) — premium sweetened profile, dessertier than XO Reserve.",
    qualityScore=6.0,
)
add(
    "rum-ah-riise-npu-black-edition",
    "A.H. Riise Non Plus Ultra Black Edition",
    167.10,
    RIISE,
    "A.H. Riise Non Plus Ultra Black Edition (42%) — vrhunac NPU linije, bogat karamel/vanilija.",
    "A.H. Riise Non Plus Ultra Black Edition (42%) — top of the NPU line, rich caramel/vanilla.",
    body=4,
    qualityScore=6.2,
)
add(
    "rum-ah-riise-npu-very-rare",
    "A.H. Riise Non Plus Ultra Very Rare",
    149.76,
    RIISE,
    "A.H. Riise Non Plus Ultra Very Rare (42%) — rijetka NPU ekspresija, gusti desertni profil.",
    "A.H. Riise Non Plus Ultra Very Rare (42%) — rare NPU expression, dense dessert profile.",
    body=4,
    qualityScore=6.2,
)
add(
    "rum-ah-riise-frogman",
    "A.H. Riise Royal Danish Navy Frogman",
    126.35,
    RIISE,
    "A.H. Riise Frogman (58%) — navy strength ekspresija; slađeni profil na višem ABV-u.",
    "A.H. Riise Frogman (58%) — navy-strength expression; sweetened profile at higher ABV.",
    body=4,
    qualityScore=5.8,
)
add(
    "rum-ah-riise-naval-cadet",
    "A.H. Riise Royal Danish Navy Naval Cadet",
    61.50,
    RIISE,
    "A.H. Riise Naval Cadet (42%) — pristupačniji navy spirit drink.",
    "A.H. Riise Naval Cadet (42%) — more approachable navy spirit drink.",
)
add(
    "rum-ah-riise-royal-danish-navy",
    "A.H. Riise Royal Danish Navy",
    52.80,
    RIISE,
    "A.H. Riise Royal Danish Navy Superior (40%) — osnovna navy boca, mekani karamel.",
    "A.H. Riise Royal Danish Navy Superior (40%) — core navy bottle, soft caramel.",
)
add(
    "rum-ah-riise-navy-strength",
    "A.H. Riise Royal Danish Navy Strength",
    66.23,
    RIISE,
    "A.H. Riise Navy Strength (55%) — jača navy linija; i dalje slađeni spirit drink.",
    "A.H. Riise Navy Strength (55%) — stronger navy line; still a sweetened spirit drink.",
    qualityScore=5.8,
)
add(
    "rum-ah-riise-signature-master-blender",
    "A.H. Riise Signature Master Blender",
    229.86,
    RIISE,
    "A.H. Riise Signature Master Blender Collection (43,9%) — limited master blender, premium desertni stil.",
    "A.H. Riise Signature Master Blender Collection (43.9%) — limited master blender, premium dessert style.",
    body=4,
    qualityScore=6.5,
)
add(
    "rum-ah-riise-xo-founders-reserve",
    "A.H. Riise XO Founders Reserve",
    69.90,
    RIISE,
    "A.H. Riise XO Founders Reserve (45,1%) — slađeni XO spirit drink, bogatiji od osnovnog XO.",
    "A.H. Riise XO Founders Reserve (45.1%) — sweetened XO spirit drink, richer than core XO.",
)
add(
    "rum-ah-riise-xo-175-years",
    "A.H. Riise XO Reserve 175 Years Anniversary",
    70.30,
    RIISE,
    "A.H. Riise XO Reserve 175 Years (42%) — anniversary XO Reserve, mekani karamelni profil.",
    "A.H. Riise XO Reserve 175 Years (42%) — anniversary XO Reserve, soft caramel profile.",
)
add(
    "rum-ah-riise-xo-ambre-dor-reserve",
    "A.H. Riise XO Reserve Ambre d'Or",
    62.20,
    RIISE,
    "A.H. Riise XO Reserve Ambre d'Or (42%) — XO Reserve linija s jantarno-slatkim profilom.",
    "A.H. Riise XO Reserve Ambre d'Or (42%) — XO Reserve line with amber-sweet profile.",
)
add(
    "rum-ah-riise-xo-christmas",
    "A.H. Riise XO Reserve Christmas Limited",
    70.61,
    RIISE,
    "A.H. Riise XO Reserve Christmas Limited (40%) — sezonska limited boca, desertni stil.",
    "A.H. Riise XO Reserve Christmas Limited (40%) — seasonal limited bottle, dessert style.",
)
add(
    "rum-ah-riise-xo-port-cask",
    "A.H. Riise XO Reserve Port Cask",
    60.92,
    RIISE,
    "A.H. Riise XO Reserve Port Cask (45%) — port cask utjecaj nad slađenom bazom.",
    "A.H. Riise XO Reserve Port Cask (45%) — port-cask influence over a sweetened base.",
    flavorTags=["karamela", "crveno-voce"],
)
add(
    "rum-ah-riise-xo-superior-cask",
    "A.H. Riise XO Reserve Superior Cask",
    57.50,
    RIISE,
    "A.H. Riise XO Reserve Superior Cask (40%) — osnovniji XO Reserve spirit drink.",
    "A.H. Riise XO Reserve Superior Cask (40%) — more entry-level XO Reserve spirit drink.",
)
add(
    "rum-ah-riise-xo-kong-haakon",
    "A.H. Riise XO Royal Reserve Kong Haakon",
    63.20,
    RIISE,
    "A.H. Riise Kong Haakon Limited (42%) — royal reserve limited edition, slađeni profil.",
    "A.H. Riise Kong Haakon Limited (42%) — royal reserve limited edition, sweetened profile.",
)

# === St Lucia / Banks / Chairman / Rodney =================================
add(
    "rum-admiral-rodney-hms-formidable",
    "Admiral Rodney HMS Formidable",
    79.50,
    ST_LUCIA,
    "Admiral Rodney HMS Formidable (40%) — starija Saint Lucia ekspresija: vanilija, hrast, tihi duhan.",
    "Admiral Rodney HMS Formidable (40%) — older Saint Lucia expression: vanilla, oak, quiet tobacco.",
    qualityScore=8.5,
)
add(
    "rum-admiral-rodney-hms-monarch",
    "Admiral Rodney HMS Monarch",
    59.96,
    ST_LUCIA,
    "Admiral Rodney HMS Monarch (40%) — pristupačniji Rodney; vanilija i hrast Svete Lucije.",
    "Admiral Rodney HMS Monarch (40%) — more approachable Rodney; Saint Lucia vanilla and oak.",
    qualityScore=8.0,
)
add(
    "rum-admiral-rodney-officers-2-irish",
    "Admiral Rodney Officer's N°2 Irish Whiskey Cask 2009",
    88.13,
    ST_LUCIA,
    "Admiral Rodney Officer's N°2 (2009, 45%) — Irish whiskey cask finish nad Saint Lucia bazom.",
    "Admiral Rodney Officer's N°2 (2009, 45%) — Irish whiskey cask finish over a Saint Lucia base.",
    flavorTags=["vanilija", "hrast", "zacini"],
    qualityScore=8.4,
)
add(
    "rum-banks-7-golden-age",
    "Banks 7 Golden Age",
    49.99,
    BLEND,
    "Banks 7 Golden Age (43%) — multi-island blend, malo puniji od Banks 5.",
    "Banks 7 Golden Age (43%) — multi-island blend, a touch fuller than Banks 5.",
    qualityScore=7.5,
)
add(
    "rum-chairmans-legacy",
    "Chairman's Reserve Legacy Edition",
    46.50,
    ST_LUCIA,
    "Chairman's Reserve Legacy Edition (43%) — klasični Saint Lucia stil: hrast, vanilija, blagi začin.",
    "Chairman's Reserve Legacy Edition (43%) — classic Saint Lucia style: oak, vanilla, light spice.",
    qualityScore=7.5,
)
add(
    "rum-chairmans-vintage-2009",
    "Chairman's Reserve Vintage 2009",
    64.00,
    ST_LUCIA,
    "Chairman's Reserve Vintage 2009 (46%) — berba 2009, puniji hrast i začin.",
    "Chairman's Reserve Vintage 2009 (46%) — 2009 vintage, fuller oak and spice.",
    qualityScore=8.2,
)
add(
    "rum-chairmans-forgotten-casks",
    "Chairman's Reserve The Forgotten Casks",
    49.39,
    ST_LUCIA,
    "Chairman's Reserve The Forgotten Casks (40%) — starije bačve, mekši Saint Lucia profil.",
    "Chairman's Reserve The Forgotten Casks (40%) — older casks, softer Saint Lucia profile.",
    qualityScore=7.8,
)
add(
    "rum-chairmans-spiced",
    "Chairman's Reserve Spiced Original",
    27.81,
    RIISE_SPICED,
    "Chairman's Reserve Spiced Original (40%) — spiced Saint Lucia; za highball i colu.",
    "Chairman's Reserve Spiced Original (40%) — spiced Saint Lucia; for highball and cola.",
    region="Spiced (Sv. Lucija)",
    qualityScore=5.5,
)

# === Compagnie des Indes ==================================================
add(
    "rum-cdi-caraibes",
    "Compagnie des Indes Caraïbes",
    39.33,
    BLEND,
    "CDI Caraïbes (40%) — blended Caribbean bottling, čist profil bez teškog šećera.",
    "CDI Caraïbes (40%) — blended Caribbean bottling, clean profile without heavy sugar.",
    qualityScore=7.5,
)
add(
    "rum-cdi-guyana-30",
    "Compagnie des Indes Guyana 30 Ans",
    552.00,
    {**BLEND, "style": "demerara", "region": "Gvajana (Demerara)", "body": 4, "sweetness": 1,
     "flavorTags": ["hrast", "suho-voce", "dim"]},
    "CDI Guyana Single Cask 30 ans (48%) — raritetni Demerara single cask, duga odležavanja.",
    "CDI Guyana Single Cask 30 ans (48%) — rare Demerara single cask, long ageing.",
    qualityScore=9.3,
)
add(
    "rum-cdi-latino-5",
    "Compagnie des Indes Latino 5 Ans",
    43.86,
    BLEND,
    "CDI Latino 5 ans (40%) — latino blend, pristupačan i uredan.",
    "CDI Latino 5 ans (40%) — Latino blend, approachable and tidy.",
    qualityScore=7.2,
)
add(
    "rum-cdi-tricorne-white",
    "Compagnie des Indes Tricorne",
    35.00,
    {**BLEND, "body": 2, "sweetness": 1, "flavorTags": ["trska", "citrus"]},
    "CDI Tricorne Blended White (43%) — bijeli blend za koktele i čistu čašu s ledom.",
    "CDI Tricorne Blended White (43%) — white blend for cocktails and a neat pour over ice.",
    serving={
        "neat": 2,
        "water": 2,
        "rocks": 2,
        "highball": 3,
        "cola": 1,
        "best": "Koktel / rocks",
    },
    qualityScore=7.0,
)
add(
    "rum-cdi-west-indies-8",
    "Compagnie des Indes West Indies 8 YO",
    53.41,
    BLEND,
    "CDI West Indies 8 YO (40%) — blended West Indies, srednje tijelo i suhi hrast.",
    "CDI West Indies 8 YO (40%) — blended West Indies, medium body and dry oak.",
    qualityScore=7.8,
)

# === Flor de Caña + Saint James 15 ========================================
add(
    "rum-flor-de-cana-extra-seco-4",
    "Flor de Caña Extra Seco Reserva N°4",
    22.28,
    {**NIC, "body": 1, "flavorTags": ["trska", "citrus"]},
    "Flor de Caña Extra Seco 4 (40%, 1 l) — suh bijeli nikaragvanski rum za koktele.",
    "Flor de Caña Extra Seco 4 (40%, 1 l) — dry white Nicaraguan rum for cocktails.",
    serving={
        "neat": 1,
        "water": 1,
        "rocks": 1,
        "highball": 3,
        "cola": 2,
        "best": "Koktel / highball",
    },
    qualityScore=6.5,
)
add(
    "rum-flor-de-cana-4-oro",
    "Flor de Caña 4 YO Añejo Oro",
    27.83,
    NIC,
    "Flor de Caña 4 YO Oro (40%, 1 l) — kratko odležani nikaragvanski rum, blaga vanilija.",
    "Flor de Caña 4 YO Oro (40%, 1 l) — briefly aged Nicaraguan rum, light vanilla.",
    qualityScore=6.8,
)
add(
    "rum-saint-james-15",
    "Saint James 15 Ans Réserve Privée",
    102.59,
    AGRI_AGED,
    "Saint James 15 Ans Réserve Privée (43%) — petnaest godina; dublji hrast uz martinique agricole.",
    "Saint James 15 Ans Réserve Privée (43%) — fifteen years; deeper oak over Martinique agricole.",
    body=4,
    qualityScore=8.9,
)

# Price updates for existing ids (name match not required)
PRICE_UPDATES: dict[str, float] = {
    "rum-clement-vsop-agricole": 41.34,
    "rum-depaz-vieux": 49.46,
    "rum-depaz-xo": 113.35,
    "rum-hse-vsop-agricole": 63.50,
    "rum-hse-xo-agricole": 91.00,
    "rum-rhum-j-m-vsop-agricole": 50.50,
    "rum-rhum-j-m-xo-agricole": 70.48,
    "rum-trois-rivieres-agricole": 34.63,
    "rum-banks-5": 44.20,
    "rum-black-tot-rum": 54.80,
    "rum-bumbu-original": 44.35,
    "rum-bumbu-xo": 49.89,
    "rum-bumbu-cream-liker": 41.44,
    "rum-chairman-s-reserve-1931": 86.20,
    "rum-a-h-riise-xo-thin-blue-line": 62.00,
    "rum-saint-james-12-agricole": 73.86,
}


def main() -> None:
    rums: list[dict] = json.loads(RUMS.read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in rums}

    updated = 0
    for rid, price in PRICE_UPDATES.items():
        r = by_id.get(rid)
        if not r:
            continue
        pe = r.get("priceEUR") or {}
        if pe.get("min") != price or pe.get("max") != price:
            r["priceEUR"] = {"min": price, "max": price}
            updated += 1

    # Rename orphan "Family Reserve" if still present and new id not yet there
    orphan = by_id.get("rum-family-reserve")
    if orphan and "rum-ah-riise-family-reserve-1838" not in by_id:
        orphan["id"] = "rum-ah-riise-family-reserve-1838"
        orphan["name"] = "A.H. Riise Family Reserve Solera 1838"
        orphan["priceEUR"] = {"min": 81.45, "max": 81.45}
        by_id["rum-ah-riise-family-reserve-1838"] = orphan
        del by_id["rum-family-reserve"]
        updated += 1

    added = 0
    skipped = 0
    for item in NEW:
        if item["id"] in by_id:
            # refresh price if we have a newer figure
            existing = by_id[item["id"]]
            pe = existing.get("priceEUR") or {}
            new_p = item["priceEUR"]["min"]
            if pe.get("min") != new_p:
                existing["priceEUR"] = {"min": new_p, "max": new_p}
                updated += 1
            skipped += 1
            continue
        rums.append(item)
        by_id[item["id"]] = item
        added += 1

    RUMS.write_text(json.dumps(rums, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"added={added} skipped_existing={skipped} price_updates={updated} total={len(rums)}")


if __name__ == "__main__":
    main()
