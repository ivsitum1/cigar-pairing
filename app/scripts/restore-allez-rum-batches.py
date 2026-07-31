# -*- coding: utf-8 -*-
"""Restore all Allez rum batches after Martinique/Caribbean ingest (idempotent)."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "src" / "data" / "rums.json"

AGRI = {
    "style": "agricole",
    "region": "Agricole (Martinique)",
    "body": 2,
    "sweetness": 1,
    "flavorTags": ["travnato", "citrus", "vanilija"],
    "additiveStatus": "clean",
    "additiveDetail": {"hr": "Bez aditiva (AOC)", "en": "No additives (AOC)"},
    "additiveSource": "AOC zakon (zabranjeni aditivi)",
    "qualityScore": 7.8,
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
NAVY = {
    "style": "navy",
    "region": "Blend (Navy)",
    "body": 4,
    "sweetness": 2,
    "flavorTags": ["melasa", "dim", "zacini"],
    "additiveStatus": "clean",
    "additiveDetail": {"hr": "Čist-ish", "en": "Essentially clean"},
    "additiveSource": "Stilska procjena (navy blend) — nije lab mjerenje",
    "qualityScore": 8.5,
    "serving": {
        "neat": 2,
        "water": 2,
        "rocks": 3,
        "highball": 1,
        "cola": 0,
        "best": "On the rocks (velika kocka)",
    },
}
SPICED = {
    "style": "spiced",
    "region": "Spiced / aromatizirano",
    "body": 2,
    "sweetness": 5,
    "flavorTags": ["vanilija", "zacini"],
    "additiveStatus": "flavored",
    "additiveDetail": {"hr": "Dodane arome i šećer", "en": "Added flavourings and sugar"},
    "additiveSource": "Stilska procjena (aromatizirano/spiced) — nije lab mjerenje",
    "qualityScore": 5.5,
    "serving": {
        "neat": 1,
        "water": 0,
        "rocks": 2,
        "highball": 3,
        "cola": 3,
        "best": "Koktel / highball",
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
    "additiveSource": "Dekl. (Flor de Caña / proizvođač)",
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
NIC_AGED = {
    **NIC,
    "body": 3,
    "flavorTags": ["hrast", "suho-voce", "vanilija"],
    "qualityScore": 8.0,
    "serving": {
        "neat": 3,
        "water": 3,
        "rocks": 2,
        "highball": 0,
        "cola": 0,
        "best": "Čisto / kap vode",
    },
}
NIC_OLD = {**NIC_AGED, "body": 4, "qualityScore": 8.8}
GUAT = {
    "style": "solera",
    "region": "Gvatemala",
    "body": 3,
    "sweetness": 4,
    "flavorTags": ["karamela", "suho-voce", "hrast"],
    "additiveStatus": "sweetened",
    "additiveDetail": {
        "hr": "Doslađen solera profil (stilska procjena)",
        "en": "Sweetened solera profile (style estimate)",
    },
    "additiveSource": "Stilska procjena (solera) — nije lab/hidrometar",
    "qualityScore": 7.0,
    "serving": {
        "neat": 2,
        "water": 2,
        "rocks": 3,
        "highball": 0,
        "cola": 0,
        "best": "Rocks / čisto",
    },
}
GUAT_PREMIUM = {
    **GUAT,
    "body": 4,
    "qualityScore": 8.0,
    "serving": {
        "neat": 3,
        "water": 2,
        "rocks": 2,
        "highball": 0,
        "cola": 0,
        "best": "Čisto",
    },
}
BOTRAN = {
    "style": "solera",
    "region": "Gvatemala",
    "body": 3,
    "sweetness": 3,
    "flavorTags": ["karamela", "vanilija", "hrast"],
    "additiveStatus": "moderate",
    "additiveDetail": {
        "hr": "Solera; umjereni dodatak (stilska procjena)",
        "en": "Solera; moderate addition (style estimate)",
    },
    "additiveSource": "Stilska procjena (solera) — nije lab/hidrometar",
    "qualityScore": 7.0,
    "serving": {
        "neat": 2,
        "water": 2,
        "rocks": 3,
        "highball": 1,
        "cola": 0,
        "best": "Rocks / čisto",
    },
}
MAU = {
    "style": "other",
    "region": "Mauricijus",
    "body": 3,
    "sweetness": 3,
    "flavorTags": ["karamela", "vanilija", "tropsko-voce"],
    "additiveStatus": "moderate",
    "additiveDetail": {
        "hr": "Umjereni dodatak (stilska procjena)",
        "en": "Moderate addition (style estimate)",
    },
    "additiveSource": "Stilska procjena — nije lab/hidrometar",
    "qualityScore": 6.5,
    "serving": {
        "neat": 2,
        "water": 2,
        "rocks": 3,
        "highball": 1,
        "cola": 0,
        "best": "Rocks / čisto",
    },
}
MAU_AGED = {
    **MAU,
    "body": 3,
    "sweetness": 2,
    "flavorTags": ["hrast", "suho-voce", "vanilija"],
    "additiveStatus": "light",
    "additiveDetail": {
        "hr": "Blagi dodatak / čistiji profil (stilska procjena)",
        "en": "Light addition / cleaner profile (style estimate)",
    },
    "qualityScore": 7.8,
    "serving": {
        "neat": 3,
        "water": 3,
        "rocks": 2,
        "highball": 0,
        "cola": 0,
        "best": "Čisto / kap vode",
    },
}
DOM = {
    "style": "dominican",
    "region": "Dominikanska Republika",
    "body": 3,
    "sweetness": 3,
    "flavorTags": ["karamela", "vanilija", "suho-voce"],
    "additiveStatus": "moderate",
    "additiveDetail": {
        "hr": "Umjereni dodatak (stilska procjena)",
        "en": "Moderate addition (style estimate)",
    },
    "additiveSource": "Stilska procjena (solera/hispan) — nije lab/hidrometar",
    "qualityScore": 6.5,
    "serving": {
        "neat": 2,
        "water": 2,
        "rocks": 3,
        "highball": 1,
        "cola": 0,
        "best": "Rocks / čisto",
    },
}
DOM_AGED = {
    **DOM,
    "qualityScore": 7.2,
    "serving": {
        "neat": 3,
        "water": 2,
        "rocks": 2,
        "highball": 0,
        "cola": 0,
        "best": "Čisto / rocks",
    },
}
BB = {
    "style": "barbados",
    "region": "Barbados",
    "body": 3,
    "sweetness": 1,
    "flavorTags": ["suho-voce", "hrast", "vanilija"],
    "additiveStatus": "clean",
    "additiveDetail": {"hr": "Čist", "en": "Clean"},
    "additiveSource": "Dekl. (Foursquare / Mount Gay)",
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


NEW: list[dict] = []


def add(id_: str, name: str, price: float, tpl: dict, hr: str, en: str, **extra) -> None:
    NEW.append(make(id_, name, price, tpl, hr, en, **extra))


# --- batch2 ---
add("rum-saint-james-vsop", "Saint James VSOP", 39.68, AGRI,
    "Saint James VSOP Très Vieux (43%) — klasični martinique agricole VSOP: travnata trska, citrus i blagi hrast.",
    "Saint James VSOP Très Vieux (43%) — classic Martinique agricole VSOP: grassy cane, citrus and light oak.")
add("rum-black-tot-mbr-2021", "Black Tot Master Blender's Reserve 2021", 215.0, NAVY,
    "Black Tot Master Blender's Reserve 2021 (54,5%) — limited navy blend, gušći i kompleksniji od osnovnog Black Tota.",
    "Black Tot Master Blender's Reserve 2021 (54.5%) — limited navy blend, denser and more complex than core Black Tot.",
    qualityScore=8.8)
add("rum-cdi-spiced", "Compagnie des Indes Spiced Rum", 39.38, SPICED,
    "Compagnie des Indes Spiced (40%) — spiced bottling; vanilija i začin za highball.",
    "Compagnie des Indes Spiced (40%) — spiced bottling; vanilla and spice for highballs.")

# --- flor / zapatera / centenario ---
add("rum-flor-de-cana-5-clasico", "Flor de Caña 5 YO Añejo Clásico", 25.90, NIC,
    "Flor de Caña 5 YO Clásico (37,5%) — kratko odležani nikaragvanski rum, blaga vanilija i hrast.",
    "Flor de Caña 5 YO Clásico (37.5%) — briefly aged Nicaraguan rum, light vanilla and oak.", qualityScore=6.5)
add("rum-flor-de-cana-7-blanco-reserva", "Flor de Caña 7 YO Blanco Reserva", 32.80,
    {**NIC, "body": 1, "flavorTags": ["trska", "citrus", "hrast"],
     "serving": {"neat": 2, "water": 1, "rocks": 1, "highball": 3, "cola": 2, "best": "Koktel / highball"}},
    "Flor de Caña 7 YO Blanco Reserva (40%) — filtrirani/bjeli stil nakon odležavanja; čistiji koktel rum.",
    "Flor de Caña 7 YO Blanco Reserva (40%) — filtered/white style after ageing; cleaner cocktail rum.", qualityScore=7.0)
add("rum-flor-de-cana-7-gran-reserva", "Flor de Caña 7 YO Gran Reserva", 26.81, NIC_AGED,
    "Flor de Caña 7 YO Gran Reserva (40%, 1 l) — single estate, suh nikaragvanski profil s hrastom i vanilijom.",
    "Flor de Caña 7 YO Gran Reserva (40%, 1 l) — single estate, dry Nicaraguan profile with oak and vanilla.", qualityScore=7.5)
add("rum-flor-de-cana-12", "Flor de Caña Centenario 12 YO", 42.50, NIC_AGED,
    "Flor de Caña Centenario 12 (40%) — suhi, whiskey-nalik nikaragvanski rum; uredan hrast i suho voće.",
    "Flor de Caña Centenario 12 (40%) — dry, whisky-like Nicaraguan rum; tidy oak and dried fruit.", qualityScore=8.0)
add("rum-flor-de-cana-14", "Flor de Caña 14 YO", 49.99, NIC_AGED,
    "Flor de Caña 14 YO (43%) — korak iznad 12-ice; malo puniji hrast uz isti suhi stil.",
    "Flor de Caña 14 YO (43%) — a step above the 12; slightly fuller oak in the same dry style.", qualityScore=8.2)
add("rum-flor-de-cana-18", "Flor de Caña Centenario 18 YO", 60.81, NIC_OLD,
    "Flor de Caña Centenario 18 (40%) — starija ekspresija; dublji hrast i suho voće, i dalje suh.",
    "Flor de Caña Centenario 18 (40%) — older expression; deeper oak and dried fruit, still dry.", qualityScore=8.5)
add("rum-flor-de-cana-25", "Flor de Caña 25 YO", 162.50, NIC_OLD,
    "Flor de Caña 25 YO Slow Aged Single Estate (40%) — duga odležavanja, kompleksan suh profil.",
    "Flor de Caña 25 YO Slow Aged Single Estate (40%) — long ageing, complex dry profile.", qualityScore=9.0)
add("rum-flor-de-cana-130th", "Flor de Caña 130th Anniversary", 96.25, NIC_AGED,
    "Flor de Caña 130th Anniversary (45%) — jubilarna boca, puniji ABV uz klasični suhi stil.",
    "Flor de Caña 130th Anniversary (45%) — anniversary bottle, higher ABV in the classic dry style.", qualityScore=8.6)
add("rum-flor-de-cana-30-v-generaciones", "Flor de Caña 30 YO V Generaciones 1988", 2219.00, NIC_OLD,
    "Flor de Caña 30 YO V Generaciones Single Barrel 1988 (45%) — raritetni single barrel, berba 1988.",
    "Flor de Caña 30 YO V Generaciones Single Barrel 1988 (45%) — rare single barrel, 1988 vintage.", qualityScore=9.4)
add("rum-flor-de-cana-eco", "Flor de Caña ECO", 41.34, NIC_AGED,
    "Flor de Caña ECO (40%) — eco linija, suh nikaragvanski profil sličan srednjoj dobi.",
    "Flor de Caña ECO (40%) — eco line, dry Nicaraguan profile akin to mid-age expressions.", qualityScore=7.8)
add("rum-flor-de-cana-cognac-cask-1997", "Flor de Caña Cognac Cask Finish 1997", 499.00, NIC_OLD,
    "Flor de Caña Cognac Cask Finish Vintage 1997 (47%) — raritetni cognac finish nad starom bazom.",
    "Flor de Caña Cognac Cask Finish Vintage 1997 (47%) — rare cognac finish over an old base.",
    flavorTags=["hrast", "suho-voce", "vanilija"], qualityScore=9.2)
add("rum-zapatera-reserva-1996", "Zapatera Reserva Cask 62 Vintage 1996", 63.40, NIC_AGED,
    "Zapatera Reserva Cask No. 62 Vintage 1996 (40%) — nikaragvanski vintage, uredan hrast i suho voće.",
    "Zapatera Reserva Cask No. 62 Vintage 1996 (40%) — Nicaraguan vintage, tidy oak and dried fruit.", qualityScore=8.0)
add("rum-zapatera-reserva-especial-1992", "Zapatera Reserva Especial Cask 50 Vintage 1992", 82.40, NIC_AGED,
    "Zapatera Reserva Especial Cask No. 50 Vintage 1992 (40%) — starija bačva, puniji nikaragvanski profil.",
    "Zapatera Reserva Especial Cask No. 50 Vintage 1992 (40%) — older cask, fuller Nicaraguan profile.",
    body=4, qualityScore=8.3)
add("rum-zapatera-gran-reserva-1989", "Zapatera Gran Reserva Cask 78 Vintage 1989", 148.75, NIC_OLD,
    "Zapatera Gran Reserva Cask No. 78 Vintage 1989 (42%) — najstarija Zapatera s Alleza; dubok hrast.",
    "Zapatera Gran Reserva Cask No. 78 Vintage 1989 (42%) — oldest Zapatera on Allez; deep oak.", qualityScore=8.7)

# --- botran / zacapa ---
add("rum-botran-oro", "Botran Añejo Oro", 15.75, {**BOTRAN, "body": 2, "qualityScore": 5.5},
    "Botran Añejo Oro Solera (40%) — ulazni gvatemalski solera; mekani karamel za rocks ili highball.",
    "Botran Añejo Oro Solera (40%) — entry Guatemalan solera; soft caramel for rocks or highball.",
    serving={"neat": 1, "water": 1, "rocks": 3, "highball": 2, "cola": 1, "best": "Rocks / highball"})
add("rum-botran-1893-decanter", "Botran Solera 1893 Decanter", 47.78, BOTRAN,
    "Botran Solera 1893 Anejo Decanter (40%) — klasični Botran 1893 u decanter pakiranju; karamel i vanilija.",
    "Botran Solera 1893 Anejo Decanter (40%) — classic Botran 1893 in decanter packaging; caramel and vanilla.",
    qualityScore=7.2)
add("rum-botran-primera-edicion", "Botran Solera 1893 Primera Edición", 197.58, {**BOTRAN, "body": 4, "qualityScore": 8.2},
    "Botran Solera 1893 Primera Edicion Premium Gold (40%, 0,75 l) — premium gold linija, bogatiji solera profil.",
    "Botran Solera 1893 Primera Edicion Premium Gold (40%, 0.75 l) — premium gold line, richer solera profile.")
add("rum-zacapa-la-doma", "Zacapa Centenario 23 La Doma Heavenly Cask", 168.00, GUAT_PREMIUM,
    "Zacapa 23 La Doma Heavenly Cask Collection (40%) — posebna cask kolekcija nad 23 solera bazom.",
    "Zacapa 23 La Doma Heavenly Cask Collection (40%) — special cask collection over the 23 solera base.", qualityScore=8.2)
add("rum-zacapa-30-aniversario", "Zacapa Centenario 30 Aniversario", 1114.00, GUAT_PREMIUM,
    "Zacapa Centenario 30 Aniversario Edicion Especial (40%) — raritetna jubilarna boca.",
    "Zacapa Centenario 30 Aniversario Edicion Especial (40%) — rare anniversary bottle.", qualityScore=9.0)
add("rum-zacapa-etiqueta-negra-23", "Zacapa Centenario Etiqueta Negra 23", 326.00, GUAT_PREMIUM,
    "Zacapa Etiqueta Negra 23 (43%) — raritetnija crna etiketa, puniji ABV uz slatki solera stil.",
    "Zacapa Etiqueta Negra 23 (43%) — rarer black label, higher ABV in the sweet solera style.", qualityScore=8.5)
add("rum-zacapa-reserva-limitada-2015", "Zacapa Reserva Limitada 2015", 414.00, GUAT_PREMIUM,
    "Zacapa Reserva Limitada Solera Gran Reserva 2015 (45%) — limited release, gušći i slađi profil.",
    "Zacapa Reserva Limitada Solera Gran Reserva 2015 (45%) — limited release, denser and sweeter profile.", qualityScore=8.7)
add("rum-zacapa-reserva-limitada-2019", "Zacapa Reserva Limitada 2019", 141.00, GUAT_PREMIUM,
    "Zacapa Reserva Limitada Solera Gran Reserva 2019 (45%) — novija limited solera ekspresija.",
    "Zacapa Reserva Limitada Solera Gran Reserva 2019 (45%) — newer limited solera expression.", qualityScore=8.3)
add("rum-zacapa-el-alma", "Zacapa Centenario El Alma 23", 109.00, GUAT,
    "Zacapa El Alma Sistema Solera 23 Limited (40%) — limited edition nad 23 bazom.",
    "Zacapa El Alma Sistema Solera 23 Limited (40%) — limited edition over the 23 base.", qualityScore=7.8)

# --- mauritius ---
add("rum-blue-mauritius-gold", "Blue Mauritius Gold", 59.59, MAU,
    "Blue Mauritius Gold (40%) — mauricijski rum, mekani karamel i tropično voće.",
    "Blue Mauritius Gold (40%) — Mauritian rum, soft caramel and tropical fruit.", qualityScore=6.2)
add("rum-cdi-mauritius-13-armagnac", "Compagnie des Indes Mauritius 13 Ans Armagnac Finish", 103.70,
    {**MAU_AGED, "style": "blend", "body": 4, "sweetness": 1, "flavorTags": ["hrast", "suho-voce", "zacini"],
     "additiveStatus": "clean", "additiveDetail": {"hr": "Čist (bottler)", "en": "Clean (bottler)"},
     "additiveSource": "Dekl. (bottler)", "qualityScore": 8.5},
    "CDI Mauritius Single Cask 13 ans Armagnac Finish (53,1%) — cask strength, armagnac finish.",
    "CDI Mauritius Single Cask 13 ans Armagnac Finish (53.1%) — cask strength, Armagnac finish.")
add("rum-new-grove-10", "New Grove Old Tradition 10 YO", 49.90, MAU_AGED,
    "New Grove Old Tradition 10 YO (40%) — mauricijski island rum, uredan hrast i vanilija.",
    "New Grove Old Tradition 10 YO (40%) — Mauritian island rum, tidy oak and vanilla.", qualityScore=7.5)
add("rum-new-grove-beau-plan-2007", "New Grove Savoir Faire Beau Plan 2007", 70.50, MAU_AGED,
    "New Grove Beau Plan Vintage 13 YO 2007 (45%) — Savoir Faire linija, vintage mauricijski rum.",
    "New Grove Beau Plan Vintage 13 YO 2007 (45%) — Savoir Faire line, vintage Mauritian rum.", qualityScore=8.0)
add("rum-new-grove-ville-bague-2004", "New Grove Savoir Faire Ville Bague 2004", 89.00, MAU_AGED,
    "New Grove Ville Bague Vintage 16 YO 2004 (45%) — starija Savoir Faire ekspresija.",
    "New Grove Ville Bague Vintage 16 YO 2004 (45%) — older Savoir Faire expression.", body=4, qualityScore=8.3)
add("rum-new-grove-emotion-1969", "New Grove Emotion 1969", 198.00, {**MAU_AGED, "body": 4, "qualityScore": 8.8},
    "New Grove Emotion 1969 (47%) — premium mauricijski rum, bogatiji i zreliji profil.",
    "New Grove Emotion 1969 (47%) — premium Mauritian rum, richer and more mature profile.")

# --- dominican ---
add("rum-kirk-sweeney-18", "Kirk and Sweeney 18 Reserva", 50.62, DOM_AGED,
    "Kirk and Sweeney 18 Reserva (40%) — dominikanski rum, mekani karamel i suho voće.",
    "Kirk and Sweeney 18 Reserva (40%) — Dominican rum, soft caramel and dried fruit.", qualityScore=7.0)
add("rum-kirk-sweeney-23", "Kirk and Sweeney 23 Reserva", 61.46, DOM_AGED,
    "Kirk and Sweeney 23 Reserva (40%) — starija reserva, puniji slatki profil.",
    "Kirk and Sweeney 23 Reserva (40%) — older reserva, fuller sweet profile.", body=4, qualityScore=7.3)
add("rum-kirk-sweeney-gran-reserva-superior", "Kirk and Sweeney Gran Reserva Superior", 55.43, DOM_AGED,
    "Kirk and Sweeney Gran Reserva Superior (40%) — korak iznad Gran Reservé.",
    "Kirk and Sweeney Gran Reserva Superior (40%) — a step above Gran Reserva.", qualityScore=7.2)
add("rum-kirk-sweeney-xo-no5-bio", "Kirk and Sweeney XO Edición Limitada No. 5 BIO", 289.00,
    {**DOM_AGED, "body": 4, "sweetness": 2, "qualityScore": 8.2},
    "Kirk and Sweeney XO Edicion Limitada No. 5 BIO (65,5%) — cask strength limited BIO izdanje.",
    "Kirk and Sweeney XO Edicion Limitada No. 5 BIO (65.5%) — cask-strength limited BIO release.")
add("rum-matusalem-platino", "Ron Matusalem Platino", 25.75,
    {**DOM, "body": 1, "sweetness": 2, "flavorTags": ["trska", "vanilija"], "qualityScore": 5.5,
     "serving": {"neat": 1, "water": 1, "rocks": 1, "highball": 3, "cola": 2, "best": "Koktel / highball"}},
    "Matusalem Platino (40%) — bijeli/solera-blender stil za koktele.",
    "Matusalem Platino (40%) — white/solera-blender style for cocktails.")
add("rum-matusalem-7", "Ron Matusalem 7 Anos Solera", 25.20, DOM,
    "Matusalem 7 Anos Solera Blender (40%) — ulazni solera, mekani karamel.",
    "Matusalem 7 Anos Solera Blender (40%) — entry solera, soft caramel.", qualityScore=6.0)
add("rum-matusalem-10-clasico", "Ron Matusalem 10 Solera Clásico", 32.00, DOM,
    "Matusalem 10 Solera Clasico (40%) — klasični solera, vanilija i karamel.",
    "Matusalem 10 Solera Clasico (40%) — classic solera, vanilla and caramel.", qualityScore=6.5)
add("rum-matusalem-23", "Ron Matusalem 23 Solera Gran Reserva", 68.50, DOM_AGED,
    "Matusalem 23 Solera Gran Reserva (40%) — starija gran reserva, bogatiji slatki profil.",
    "Matusalem 23 Solera Gran Reserva (40%) — older gran reserva, richer sweet profile.", body=4, qualityScore=7.5)
add("rum-opthimus-15-res-laude", "Opthimus 15 Res Laude", 58.61, DOM_AGED,
    "Opthimus 15 Anos Res Laude (38%) — dominikanski solera, mekan i slatkast.",
    "Opthimus 15 Anos Res Laude (38%) — Dominican solera, soft and sweetish.", qualityScore=6.8)
add("rum-opthimus-15-oporto", "Opthimus 15 Solera Oporto", 61.25, DOM_AGED,
    "Opthimus 15 Solera Oporto (43%) — port finish nad solera bazom.",
    "Opthimus 15 Solera Oporto (43%) — port finish over a solera base.",
    flavorTags=["karamela", "crveno-voce", "suho-voce"], qualityScore=7.2)
add("rum-opthimus-18-cum-laude", "Opthimus 18 Cum Laude", 56.60, DOM_AGED,
    "Opthimus 18 Anos Cum Laude (38%) — srednja dob, slatki dominikanski stil.",
    "Opthimus 18 Anos Cum Laude (38%) — mid-age, sweet Dominican style.", qualityScore=7.0)
add("rum-opthimus-21-magna-cum-laude", "Opthimus 21 Magna Cum Laude", 73.71, DOM_AGED,
    "Opthimus 21 Anos Magna Cum Laude (38%) — punija solera ekspresija.",
    "Opthimus 21 Anos Magna Cum Laude (38%) — fuller solera expression.", body=4, qualityScore=7.3)
add("rum-opthimus-25-malt-whisky", "Opthimus 25 Malt Whisky Finish", 100.45, DOM_AGED,
    "Opthimus 25 Anos Malt Whisky Finish (43%) — whisky finish nad starom solera bazom.",
    "Opthimus 25 Anos Malt Whisky Finish (43%) — whisky finish over an old solera base.",
    body=4, flavorTags=["karamela", "hrast", "zacini"], qualityScore=7.8)
add("rum-opthimus-25-oporto", "Opthimus 25 Solera Oporto", 89.38, DOM_AGED,
    "Opthimus 25 Solera Oporto (43%) — starija port-finish ekspresija.",
    "Opthimus 25 Solera Oporto (43%) — older port-finish expression.",
    body=4, flavorTags=["karamela", "crveno-voce", "suho-voce"], qualityScore=7.7)
add("rum-opthimus-25-summa-cum-laude", "Opthimus 25 Summa Cum Laude", 85.79, DOM_AGED,
    "Opthimus 25 Anos Summa Cum Laude (38%) — vrhunac Cum Laude linije.",
    "Opthimus 25 Anos Summa Cum Laude (38%) — top of the Cum Laude line.", body=4, qualityScore=7.6)
add("rum-opthimus-xo-summa-cum-laude", "Opthimus XO Summa Cum Laude", 149.18, DOM_AGED,
    "Opthimus XO Summa Cum Laude (38%) — XO ekspresija, najbogatiji Opthimus s Alleza.",
    "Opthimus XO Summa Cum Laude (38%) — XO expression, the richest Opthimus on Allez.", body=4, qualityScore=8.0)

# --- barbados ---
add("rum-doorly-s-5", "Doorly's 5 YO", 32.00,
    {**BB, "body": 2, "qualityScore": 7.2,
     "serving": {"neat": 2, "water": 2, "rocks": 2, "highball": 2, "cola": 0, "best": "Čisto / rocks"}},
    "Doorly's 5 YO (40%) — mlađi Foursquare Barbados; suh, pristupačan ulaz u Doorly's liniju.",
    "Doorly's 5 YO (40%) — younger Foursquare Barbados; dry, approachable entry to the Doorly's line.")
add("rum-doorly-s-8", "Doorly's 8 YO", 43.40, {**BB, "body": 2, "qualityScore": 7.8},
    "Doorly's 8 YO (40%) — srednja dob Foursquarea; suhi hrast i vanilija bez šećera.",
    "Doorly's 8 YO (40%) — mid-age Foursquare; dry oak and vanilla with no sugar.")
add("rum-mount-gay-black-barrel", "Mount Gay Black Barrel", 59.99, BB,
    "Mount Gay 1703 Black Barrel (43%, 1 l) — tostirani hrast, suho voće i vanilija; kućni Barbados klasik.",
    "Mount Gay 1703 Black Barrel (43%, 1 l) — toasted oak, dried fruit and vanilla; a Barbados house classic.",
    qualityScore=7.8)
add("rum-mount-gay-eclipse", "Mount Gay Eclipse", 29.00,
    {**BB, "body": 2, "qualityScore": 6.8,
     "serving": {"neat": 2, "water": 2, "rocks": 2, "highball": 3, "cola": 1, "best": "Highball / rocks"}},
    "Mount Gay Eclipse (40%, 1 l) — pristupačni Barbados blend za highball i čistu čašu.",
    "Mount Gay Eclipse (40%, 1 l) — approachable Barbados blend for highball and neat pours.")
add("rum-mount-gay-andean-oak", "Mount Gay Master Blender Andean Oak Cask", 222.79,
    {**BB, "body": 4, "qualityScore": 9.0, "flavorTags": ["hrast", "suho-voce", "orasasti"]},
    "Mount Gay Master Blender Collection Andean Oak Cask (48%) — limited, južnoamerički hrast finish.",
    "Mount Gay Master Blender Collection Andean Oak Cask (48%) — limited, South American oak finish.")

# also from earlier batches that may need re-add if missing from first ingest rename path
add("rum-chairmans-masters-selection-coffey", "Chairman's Reserve Master's Selection Coffey Still", 77.0, ST_LUCIA,
    "Chairman's Reserve Master's Selection Coffey Still (46,2%) — column-still ekspresija Svete Lucije: čistiji hrast i vanilija, punije tijelo.",
    "Chairman's Reserve Master's Selection Coffey Still (46.2%) — Saint Lucia column-still expression: cleaner oak and vanilla, fuller body.",
    body=4, qualityScore=8.5)

# --- Karukera (Guadeloupe) ---
GUAD = {
    "style": "agricole",
    "region": "Agricole (Guadeloupe)",
    "body": 2,
    "sweetness": 1,
    "flavorTags": ["travnato", "vegetalno", "citrus"],
    "additiveStatus": "clean",
    "additiveDetail": {"hr": "Bez aditiva", "en": "No additives"},
    "additiveSource": "Pravilo regije / stilska procjena — nije lab mjerenje",
    "qualityScore": 7.8,
    "serving": {
        "neat": 3,
        "water": 3,
        "rocks": 1,
        "highball": 2,
        "cola": 0,
        "best": "Čisto / Ti' Punch",
    },
}
GUAD_AGED = {
    **GUAD,
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
GUAD_BLANC = {
    **GUAD,
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
add("rum-karukera-black-edition-alligator", "Karukera Black Edition Alligator", 82.35, GUAD_AGED,
    "Karukera Black Edition Alligator (45%, 1 l) — vieux agricole Guadeloupe, puniji hrast uz travnatu bazu.",
    "Karukera Black Edition Alligator (45%, 1 l) — vieux agricole Guadeloupe, fuller oak over a grassy base.",
    qualityScore=8.2,
    priceUrl="https://allez.hr/shop/svi-proizvodi/karukera-black-edition-alligator-rhum-vieux-agricole-45-vol-1l")
add("rum-karukera-christophe-colomb-1493", "Karukera Cuvée Christophe Colomb 1493", 228.00,
    {**GUAD_AGED, "body": 4, "qualityScore": 9.0},
    "Karukera Christophe Colomb 1493 Hors d'Age (45%) — tres vieux premium linija.",
    "Karukera Christophe Colomb 1493 Hors d'Age (45%) — tres vieux premium line.")
add("rum-karukera-expression-2008", "Karukera L'Expression Millésime 2008", 173.98,
    {**GUAD_AGED, "body": 4, "qualityScore": 8.8},
    "Karukera L'Expression Millésime 2008 (48,1%) — berba 2008, intenzivniji agricole.",
    "Karukera L'Expression Millésime 2008 (48.1%) — 2008 vintage, more intense agricole.")
add("rum-karukera-reserve-speciale", "Karukera Réserve Spéciale", 68.10, GUAD_AGED,
    "Karukera Réserve Spéciale Vieux (42%) — rezervna linija, uredan hrast uz Guadeloupe agricole.",
    "Karukera Réserve Spéciale Vieux (42%) — reserve line, tidy oak over Guadeloupe agricole.", qualityScore=8.0)
add("rum-karukera-blanc", "Karukera Blanc Agricole", 32.40, GUAD_BLANC,
    "Karukera Blanc Agricole (50%) — bijeli Guadeloupe agricole; klasika za Ti' Punch.",
    "Karukera Blanc Agricole (50%) — white Guadeloupe agricole; a Ti' Punch classic.")
add("rum-karukera-intense-blanc", "Karukera L'Intense Blanc", 69.02, {**GUAD_BLANC, "qualityScore": 8.0},
    "Karukera L'Intense Blanc Agricole (63,8%) — high-proof bijeli agricole.",
    "Karukera L'Intense Blanc Agricole (63.8%) — high-proof white agricole.")
add("rum-karukera-gold-premium", "Karukera Gold Premium", 31.28,
    {**GUAD, "body": 2, "sweetness": 2, "qualityScore": 6.5,
     "serving": {"neat": 2, "water": 2, "rocks": 2, "highball": 2, "cola": 0, "best": "Rocks / Ti' Punch"}},
    "Karukera Gold Premium (40%) — pristupačniji gold/ambre stil Guadeloupea.",
    "Karukera Gold Premium (40%) — more approachable gold/ambre Guadeloupe style.")

PRICE_UPDATES = {
    "rum-saint-james-xo-agricole": 50.17,
    "rum-ron-centenario-25": 79.90,
    "rum-botran-18-solera": 44.98,
    "rum-botran-12": 31.78,
    "rum-zacapa-centenario-23": 85.40,
    "rum-zacapa-ambar": 77.00,
    "rum-zacapa-edicion-negra": 102.50,
    "rum-zacapa-xo": 149.00,
    "rum-zacapa-royal": 377.00,
    "rum-kirk-sweeney-gran-reserva": 51.40,
    "rum-ron-matusalem-15": 45.95,
    "rum-doorly-s-12-foursquare": 62.00,
    "rum-doorly-s-14-foursquare": 93.40,
    "rum-doorly-s-xo-foursquare": 48.00,
    "rum-mount-gay-xo": 59.50,
    "rum-foursquare-spiced": 31.85,
    "rum-karukera-vieux-agricole-guadeloupe": 58.40,
}

NAME_UPDATES = {
    "rum-ron-centenario-25": "Ron Centenario Gran Reserva 25",
    "rum-zacapa-ambar": "Zacapa Centenario Ámbar 12",
    "rum-zacapa-edicion-negra": "Zacapa Centenario Edición Negra",
    "rum-zacapa-xo": "Zacapa Centenario XO",
    "rum-zacapa-royal": "Zacapa Centenario Royal",
    "rum-botran-18-solera": "Botran Añejo 18 Solera 1893",
    "rum-botran-12": "Botran Añejo 12 Solera",
    "rum-kirk-sweeney-gran-reserva": "Kirk and Sweeney Gran Reserva",
    "rum-ron-matusalem-15": "Ron Matusalem 15 Solera Gran Reserva",
}


def main() -> None:
    rums = json.loads(P.read_text(encoding="utf-8"))
    by = {r["id"]: r for r in rums}

    # rename orphans if still present
    if "rum-master-s" in by and "rum-chairmans-masters-selection-coffey" not in by:
        m = by["rum-master-s"]
        m["id"] = "rum-chairmans-masters-selection-coffey"
        m["name"] = "Chairman's Reserve Master's Selection Coffey Still"
        m["priceEUR"] = {"min": 77.0, "max": 77.0}
        m["status"] = None
        by["rum-chairmans-masters-selection-coffey"] = m
        print("renamed rum-master-s")

    if "rum-mount-gay-1703-master-blender" in by and "rum-mount-gay-andean-oak" not in by:
        m = by["rum-mount-gay-1703-master-blender"]
        m["id"] = "rum-mount-gay-andean-oak"
        m["name"] = "Mount Gay Master Blender Andean Oak Cask"
        m["priceEUR"] = {"min": 222.79, "max": 222.79}
        m["status"] = None
        by["rum-mount-gay-andean-oak"] = m
        print("renamed master-blender -> andean-oak")

    for rid, price in PRICE_UPDATES.items():
        r = by.get(rid)
        if not r:
            continue
        r["priceEUR"] = {"min": price, "max": price}
        r["shopHR"] = "allez.hr"
        if rid in NAME_UPDATES:
            r["name"] = NAME_UPDATES[rid]

    # Combined 12/18 / 15/18/21 META entries are removed by cleanup-combined-rums.py
    m = by.get("rum-mount-gay-1703")
    if m:
        m["status"] = "META"

    added = 0
    for item in NEW:
        if item["id"] in by:
            by[item["id"]]["priceEUR"] = item["priceEUR"]
            continue
        rums.append(item)
        by[item["id"]] = item
        added += 1

    seen = set()
    out = []
    for r in rums:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        out.append(r)

    P.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"added={added} total={len(out)}")


if __name__ == "__main__":
    main()
