# -*- coding: utf-8 -*-
"""Part B: enrich remaining Allez families + apply all enrichment to rums.json."""
from __future__ import annotations

import importlib.util
import json
import shutil
from copy import deepcopy
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "src" / "data" / "rums.json"
OUT = Path(__file__).resolve().parent / "output"
HERE = Path(__file__).resolve().parent


def _load_part_a():
    spec = importlib.util.spec_from_file_location("enrich_a", HERE / "enrich-allez-rums.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod.get_enrich()


def pack(status, hr, en, src, sweetness):
    return {
        "additiveStatus": status,
        "additiveDetail": {"hr": hr, "en": en},
        "additiveSource": src,
        "sweetness": sweetness,
    }


FDC = pack(
    "clean",
    "Proizvođač: 0 dodanog šećera, bez umjetne boje",
    "Producer: 0 added sugar, no artificial colour",
    "Dekl. proizvođača (Flor de Caña — zero sugar / no artificial colour)",
    1,
)
FSQ = pack(
    "clean",
    "Foursquare/Doorly's — bez doziranog šećera; boja od bačve",
    "Foursquare/Doorly's — no dosed sugar; colour from cask",
    "Dekl. (Foursquare)",
    1,
)
MG = pack(
    "clean",
    "Mount Gay — tipično čist Barbados; boja od bačve (nije lab)",
    "Mount Gay — typically clean Barbados; colour from cask (not lab)",
    "Stilska procjena (Mount Gay / Barbados) — nije lab mjerenje",
    1,
)
JAM = pack(
    "clean",
    "Jamajčanski estate/pure single — bez doziranog šećera; boja od bačve",
    "Jamaican estate/pure single — no dosed sugar; colour from cask",
    "Pravilo regije / stil destilerije — nije hidrometar mjerenje",
    1,
)
BOTTLER = pack(
    "clean",
    "Nezavisni bottler — tipično bez šećera; boja od bačve",
    "Independent bottler — typically unsweetened; colour from cask",
    "Dekl./praksa bottlera — nije lab mjerenje",
    1,
)
RIISE = pack(
    "sweetened",
    "Spirit drink — dodani šećer; karamel čest (EU oznaka zbog šećera)",
    "Spirit drink — added sugar; caramel colour common (EU label due to sugar)",
    "EU oznaka spirit drink + stilska procjena — nije hidrometar",
    4,
)
SPICED = pack(
    "flavored",
    "Aromatizirano/spiced — šećer i arome; boja često podešena",
    "Flavoured/spiced — sugar and flavourings; colour often adjusted",
    "Stilska procjena (aromatizirano/spiced) — nije lab mjerenje",
    5,
)
SOLERA_MOD = pack(
    "moderate",
    "Solera stil — tipično umjeren šećer + karamel E150 (nije lab)",
    "Solera style — typically moderate sugar + E150 caramel (not lab-verified)",
    "Stilska procjena (solera/hispan) — nije lab/hidrometar",
    3,
)
SOLERA_SWEET = pack(
    "sweetened",
    "Doslađen solera profil; karamel E150 uobičajen (nije lab g/L)",
    "Sweetened solera profile; E150 caramel usual (no lab g/L)",
    "Stilska procjena (doslađen solera) — nije lab/hidrometar",
    4,
)
ST_LUCIA = pack(
    "clean",
    "St Lucia Distillers — tipično čist/vrlo nizak šećer; boja od bačve",
    "St Lucia Distillers — typically clean/very low sugar; colour from cask",
    "Stilska procjena (St Lucia Distillers) — nije lab mjerenje",
    1,
)
MAU_LIGHT = pack(
    "light",
    "Mauricijski stil — blagi dodatak moguć; boja od bačve (nije lab)",
    "Mauritian style — light addition possible; colour from cask (not lab)",
    "Stilska procjena — nije lab/hidrometar",
    2,
)
NAVY = pack(
    "clean",
    "Navy blend — tipično bez jakog doziranja; boja od blenda (nije lab)",
    "Navy blend — typically without heavy dosing; colour from blend (not lab)",
    "Stilska procjena (navy blend) — nije lab mjerenje",
    1,
)


def prose(name: str, style_hr: str, style_en: str, add_hr: str) -> dict:
    return {
        "hr": f"{name} — {style_hr} {add_hr}",
        "en": f"{name} — {style_en} {add_hr.replace('Boja', 'Colour').replace('boja', 'colour').replace('šećera', 'sugar').replace('Šećer', 'Sugar')}",
    }


# Explicit per-id enrichment (additive packs + quality + notes)
B: dict[str, dict] = {}


def put(rid: str, add: dict, q: float, notes_hr: str, notes_en: str, body: int | None = None, tags: list | None = None):
    d = {**deepcopy(add), "qualityScore": q, "notes": {"hr": notes_hr, "en": notes_en}}
    if body is not None:
        d["body"] = body
    if tags is not None:
        d["flavorTags"] = tags
    B[rid] = d


# Flor de Caña
put("rum-flor-de-cana-extra-seco-4", FDC, 6.5,
    "Flor de Caña Extra Seco 4 (40%, 1 l) — suh bijeli nikaragvanski rum za koktele. Proizvođač deklarira 0 šećera i bez umjetne boje.",
    "Flor de Caña Extra Seco 4 (40%, 1 l) — dry white Nicaraguan rum for cocktails. Producer declares 0 sugar and no artificial colour.", 1, ["trska", "citrus"])
put("rum-flor-de-cana-4-oro", FDC, 6.8,
    "Flor de Caña 4 YO Oro (40%, 1 l) — kratko odležani nikaragvanski rum, blaga vanilija. Dekl. 0 šećera, bez umjetne boje; zlatna boja od bačve.",
    "Flor de Caña 4 YO Oro (40%, 1 l) — briefly aged Nicaraguan rum, light vanilla. Declared 0 sugar, no artificial colour; gold from cask.", 2)
put("rum-flor-de-cana-5-clasico", FDC, 6.5,
    "Flor de Caña 5 YO Clásico (37,5%) — kratko odležani nikaragvanski rum. Proizvođač: bez dodanog šećera i bez umjetne boje.",
    "Flor de Caña 5 YO Clásico (37.5%) — briefly aged Nicaraguan rum. Producer: no added sugar and no artificial colour.", 2)
put("rum-flor-de-cana-7-blanco-reserva", FDC, 7.0,
    "Flor de Caña 7 YO Blanco Reserva (40%) — filtrirani/bjeli stil nakon odležavanja. Dekl. 0 šećera; boja uklonjena filtracijom, ne karamelom.",
    "Flor de Caña 7 YO Blanco Reserva (40%) — filtered/white style after ageing. Declared 0 sugar; colour removed by filtration, not caramel.", 1, ["trska", "citrus", "hrast"])
put("rum-flor-de-cana-7-gran-reserva", FDC, 7.5,
    "Flor de Caña 7 YO Gran Reserva (40%, 1 l) — single estate, suh nikaragvanski profil. Dekl. 0 šećera i bez umjetne boje.",
    "Flor de Caña 7 YO Gran Reserva (40%, 1 l) — single estate, dry Nicaraguan profile. Declared 0 sugar and no artificial colour.", 3)
put("rum-flor-de-cana-12", FDC, 8.0,
    "Flor de Caña Centenario 12 (40%) — suhi, whiskey-nalik nikaragvanski rum; uredan hrast i suho voće. Proizvođač deklarira nula šećera i bez umjetne boje — boja je od hrasta.",
    "Flor de Caña Centenario 12 (40%) — dry, whisky-like Nicaraguan rum; tidy oak and dried fruit. Producer declares zero sugar and no artificial colour — colour is from oak.", 3, ["hrast", "suho-voce", "vanilija"])
put("rum-flor-de-cana-14", FDC, 8.2,
    "Flor de Caña 14 YO (43%) — korak iznad 12-ice; malo puniji hrast uz isti suhi stil. Dekl. 0 šećera, bez E150.",
    "Flor de Caña 14 YO (43%) — a step above the 12; slightly fuller oak in the same dry style. Declared 0 sugar, no E150.", 3)
put("rum-flor-de-cana-18", FDC, 8.5,
    "Flor de Caña Centenario 18 (40%) — starija ekspresija; dublji hrast i suho voće, i dalje suh. Dekl. 0 šećera i bez umjetne boje.",
    "Flor de Caña Centenario 18 (40%) — older expression; deeper oak and dried fruit, still dry. Declared 0 sugar and no artificial colour.", 4)
put("rum-flor-de-cana-25", FDC, 9.0,
    "Flor de Caña 25 YO Slow Aged (40%) — duga odležavanja, kompleksan suh profil. Dekl. 0 šećera; tamna boja isključivo od bačve.",
    "Flor de Caña 25 YO Slow Aged (40%) — long ageing, complex dry profile. Declared 0 sugar; dark colour solely from cask.", 4)
put("rum-flor-de-cana-130th", FDC, 8.6,
    "Flor de Caña 130th Anniversary (45%) — jubilarna boca, puniji ABV uz klasični suhi stil. Dekl. 0 šećera, bez umjetne boje.",
    "Flor de Caña 130th Anniversary (45%) — anniversary bottle, higher ABV in the classic dry style. Declared 0 sugar, no artificial colour.", 3)
put("rum-flor-de-cana-30-v-generaciones", FDC, 9.4,
    "Flor de Caña 30 YO V Generaciones 1988 (45%) — raritetni single barrel. Dekl. 0 šećera; boja od trideset godina hrasta.",
    "Flor de Caña 30 YO V Generaciones 1988 (45%) — rare single barrel. Declared 0 sugar; colour from thirty years of oak.", 4)
put("rum-flor-de-cana-eco", FDC, 7.8,
    "Flor de Caña ECO (40%) — eco linija, suh nikaragvanski profil. Ista deklaracija: bez dodanog šećera i bez umjetne boje.",
    "Flor de Caña ECO (40%) — eco line, dry Nicaraguan profile. Same declaration: no added sugar and no artificial colour.", 3)
put("rum-flor-de-cana-cognac-cask-1997", FDC, 9.2,
    "Flor de Caña Cognac Cask Finish 1997 (47%) — raritetni cognac finish. Dekl. 0 šećera; boja od bačve i cognac finisha.",
    "Flor de Caña Cognac Cask Finish 1997 (47%) — rare cognac finish. Declared 0 sugar; colour from cask and cognac finish.", 4)
put("rum-zapatera-reserva-1996", FDC, 8.0,
    "Zapatera Reserva 1996 (40%) — nikaragvanski vintage. Stil suh, blizak Flor de Caña tradiciji; boja od bačve (nije lab hidrometrija).",
    "Zapatera Reserva 1996 (40%) — Nicaraguan vintage. Dry style close to Flor de Caña tradition; colour from cask (no lab hydrometry).", 3)
put("rum-zapatera-reserva-especial-1992", FDC, 8.3,
    "Zapatera Reserva Especial 1992 (40%) — starija bačva, puniji nikaragvanski profil. Stilski bez doziranja; boja od bačve.",
    "Zapatera Reserva Especial 1992 (40%) — older cask, fuller Nicaraguan profile. Style-wise undosed; colour from cask.", 4)
put("rum-zapatera-gran-reserva-1989", FDC, 8.7,
    "Zapatera Gran Reserva 1989 (42%) — najstarija Zapatera s Alleza; dubok hrast. Stilski čist; tamna boja od bačve.",
    "Zapatera Gran Reserva 1989 (42%) — oldest Zapatera on Allez; deep oak. Style-wise clean; dark colour from cask.", 4)

# Barbados
put("rum-doorly-s-5", FSQ, 7.2,
    "Doorly's 5 YO (40%) — mlađi Foursquare Barbados; suh, pristupačan. Deklarirano bez doziranog šećera; zlatna boja od bačve.",
    "Doorly's 5 YO (40%) — younger Foursquare Barbados; dry, approachable. Declared without dosed sugar; gold from cask.", 2)
put("rum-doorly-s-8", FSQ, 7.8,
    "Doorly's 8 YO (40%) — srednja dob Foursquarea; suhi hrast i vanilija bez šećera. Boja od bačve, ne E150.",
    "Doorly's 8 YO (40%) — mid-age Foursquare; dry oak and vanilla with no sugar. Colour from cask, not E150.", 2)
put("rum-doorly-s-12-foursquare", FSQ, 8.5,
    "Doorly's 12 iz Foursquarea (Barbados) je suh, čist single-blended stil: hrast, suho voće i vanilija bez doziranog šećera. U čaši srednje tijelo i uredan završetak uz kap vode.",
    "Doorly's 12 from Foursquare (Barbados) is a dry, clean single-blended style: oak, dried fruit and vanilla with no dosed sugar. Medium body and a tidy finish with a drop of water.", 3)
put("rum-doorly-s-14-foursquare", FSQ, 8.6,
    "Doorly's 14 ide korak dalje u zrelosti: više orašastog hrasta i suhog voća, i dalje bez aditiva. Malo bogatiji od 12-ice; boja dublja od bačve.",
    "Doorly's 14 steps further in maturity: more nutty oak and dried fruit, still additive-free. A touch richer than the 12; deeper cask colour.", 3)
put("rum-doorly-s-xo-foursquare", FSQ, 8.3,
    "Doorly's XO (43%) — Foursquare blend, suh i jasan Barbados profil. Bez doziranog šećera; boja od bačve.",
    "Doorly's XO (43%) — Foursquare blend, dry clear Barbados profile. No dosed sugar; colour from cask.", 3)
put("rum-foursquare-spiced", SPICED, 5.5,
    "Foursquare Spiced (37,5%) — spiced linija: arome i šećer su dio stila; boja često podešena. Za highball.",
    "Foursquare Spiced (37.5%) — spiced line: flavourings and sugar are part of the style; colour often adjusted. For highballs.", 2)
put("rum-mount-gay-eclipse", MG, 6.8,
    "Mount Gay Eclipse (40%, 1 l) — pristupačni Barbados blend. Tipično čist profil; zlatna boja od bačve (nije lab g/L).",
    "Mount Gay Eclipse (40%, 1 l) — approachable Barbados blend. Typically clean profile; gold from cask (no lab g/L).", 2)
put("rum-mount-gay-black-barrel", MG, 7.8,
    "Mount Gay Black Barrel (43%, 1 l) — tostirani hrast, suho voće i vanilija. Tipično bez jakog doziranja; bakrena boja od tostiranih bačava.",
    "Mount Gay Black Barrel (43%, 1 l) — toasted oak, dried fruit and vanilla. Typically without heavy dosing; copper colour from toasted casks.", 3)
put("rum-mount-gay-xo", MG, 8.5,
    "Mount Gay XO Triple Cask (43%) — suho voće, vanilija i hrast. Tipično čist Barbados; boja od bačve.",
    "Mount Gay XO Triple Cask (43%) — dried fruit, vanilla and oak. Typically clean Barbados; colour from cask.", 3)
put("rum-mount-gay-andean-oak", MG, 9.0,
    "Mount Gay Master Blender Andean Oak (48%) — limited, južnoamerički hrast finish. Premium čist sipper; boja od bačve.",
    "Mount Gay Master Blender Andean Oak (48%) — limited, South American oak finish. Premium clean sipper; colour from cask.", 4)
put("rum-veritas-foursquare-white", FSQ, 7.5,
    "Veritas Foursquare White (47%) — bijeli blend Foursquarea za koktele. Čist; prozirna/blijeda boja.",
    "Veritas Foursquare White (47%) — Foursquare white blend for cocktails. Clean; clear/pale colour.", 2)

# Jamaica core (abbreviated but complete for Allez batch ids)
JAMAICA = {
    "rum-appleton-estate-8-reserve": (7.2, 2, "Appleton Estate Reserve 8 (43%) — pristupačni jamajčanski stil: blagi esteri, tropično voće. Tipično bez doziranog šećera; zlatna boja od bačve.",
        "Appleton Estate Reserve 8 (43%) — approachable Jamaican style: mild esters, tropical fruit. Typically no dosed sugar; gold from cask."),
    "rum-appleton-estate-12": (8.0, 3, "Appleton Estate 12 YO Rare Casks (43%) — naranča, hrast, prženi ton. Estate stil bez tipičnog doziranja; boja od bačve.",
        "Appleton Estate 12 YO Rare Casks (43%) — orange, oak, toasted tone. Estate style without typical dosing; colour from cask."),
    "rum-appleton-estate-15-black-river": (8.5, 4, "Appleton Estate 15 Black River (43%) — puniji esteri i hrast. Tipično čist jamajčanski estate; boja od bačve.",
        "Appleton Estate 15 Black River (43%) — fuller esters and oak. Typically clean Jamaican estate; colour from cask."),
    "rum-appleton-estate-21": (8.8, 4, "Appleton Estate 21 YO Rare Limited (43%) — starija limited ekspresija. Tipično bez šećera; tamnija boja od dugog odležavanja.",
        "Appleton Estate 21 YO Rare Limited (43%) — older limited expression. Typically unsweetened; darker colour from long ageing."),
    "rum-hampden-estate-8": (9.0, 4, "Hampden Estate 8 (46%) — jaki esteri, tropično voće i suhi hrast bez teške slatkoće. Čist jamajčanski pure single; boja od bačve.",
        "Hampden Estate 8 (46%) — high esters, tropical fruit and dry oak without heavy sweetness. Clean Jamaican pure single; colour from cask."),
    "rum-hampden-hlcf-classic-60": (9.0, 4, "Hampden HLCF Classic (60%) — mark HLCF, cask strength. Bez doziranog šećera; intenzivna aroma, boja od bačve.",
        "Hampden HLCF Classic (60%) — HLCF marque, cask strength. No dosed sugar; intense aroma, colour from cask."),
    "rum-hampden-rum-fire": (8.0, 2, "Hampden Rum Fire White Overproof (63%) — ekstremni esteri, bijeli overproof. Prozirna boja; bez šećera.",
        "Hampden Rum Fire White Overproof (63%) — extreme esters, white overproof. Clear colour; no sugar."),
    "rum-wray-nephew-overproof-63": (7.5, 2, "Wray & Nephew Overproof (63%) — klasični jamajčanski overproof za koktele. Bijeli; bez doziranog šećera.",
        "Wray & Nephew Overproof (63%) — classic Jamaican overproof for cocktails. White; no dosed sugar."),
    "rum-smith-cross": (8.2, 4, "Smith & Cross Traditional (57%) — navy-ish jamajčanski stil, jaki esteri. Tipično čist; boja od bačve/blenda.",
        "Smith & Cross Traditional (57%) — navy-ish Jamaican style, high esters. Typically clean; colour from cask/blend."),
    "rum-worthy-park-select": (7.2, 2, "Worthy Park Select (40%) — ulazni single estate. Tipično čist; zlatna boja od bačve.",
        "Worthy Park Select (40%) — entry single estate. Typically clean; gold from cask."),
    "rum-worthy-park-109": (7.8, 3, "Worthy Park 109 (54,5%, 1 l) — jači single estate. Čist jamajčanski stil; boja od bačve.",
        "Worthy Park 109 (54.5%, 1 l) — stronger single estate. Clean Jamaican style; colour from cask."),
    "rum-worthy-park-single-estate": (8.0, 3, "Worthy Park Single Estate Reserve (45%) — glađi od Hampdena, i dalje esterski. Tipično bez šećera; boja od bačve.",
        "Worthy Park Single Estate Reserve (45%) — smoother than Hampden, still estery. Typically unsweetened; colour from cask."),
    "rum-worthy-park-10-madeira-2010": (8.4, 3, "Worthy Park 10 YO Madeira 2010 (45%) — madeira finish. Čist WP distillate; boja od madeira bačve, ne od E150 doziranja.",
        "Worthy Park 10 YO Madeira 2010 (45%) — Madeira finish. Clean WP distillate; colour from Madeira cask, not E150 dosing."),
    "rum-worthy-park-10-port-2010": (8.4, 3, "Worthy Park 10 YO Port 2010 (45%) — port finish. Čist distillate; boja od porta.",
        "Worthy Park 10 YO Port 2010 (45%) — port finish. Clean distillate; colour from port."),
    "rum-worthy-park-12-2006": (8.8, 4, "Worthy Park 12 YO 2006 (56%) — starija WP ekspresija. Čist; tamnija boja od bačve.",
        "Worthy Park 12 YO 2006 (56%) — older WP expression. Clean; darker colour from cask."),
    "rum-worthy-park-oloroso-2013": (8.3, 3, "Worthy Park Oloroso 2013 (55%) — oloroso finish. Čist distillate; boja od sherry bačve.",
        "Worthy Park Oloroso 2013 (55%) — oloroso finish. Clean distillate; colour from sherry cask."),
    "rum-exchange-hampden-5-2013": (8.6, 4, "Rum Exchange Hampden 5 YO #001 2013 (61,5%) — pure single bottling. Bez šećera; boja od bačve.",
        "Rum Exchange Hampden 5 YO #001 2013 (61.5%) — pure single bottling. No sugar; colour from cask."),
    "rum-exchange-worthy-park-5-2013": (8.5, 4, "Rum Exchange Worthy Park 5 YO #002 2013 (59%) — pure single. Čist; boja od bačve.",
        "Rum Exchange Worthy Park 5 YO #002 2013 (59%) — pure single. Clean; colour from cask."),
    "rum-kill-devil-hampden-35-1983": (9.5, 4, "Kill Devil Hampden 35 YO 1983 (58,1%) — raritetni cask strength. Bottler praksa: bez šećera; boja od 35 godina hrasta.",
        "Kill Devil Hampden 35 YO 1983 (58.1%) — rare cask strength. Bottler practice: no sugar; colour from 35 years of oak."),
    "rum-habitation-velier-svm-plummer-14": (9.0, 4, "HV SVM EMB Plummer 14 YO (69,7%) — vatted single, high-proof. Velier praksa: bez šećera; boja od tropskog odležavanja.",
        "HV SVM EMB Plummer 14 YO (69.7%) — vatted single, high-proof. Velier practice: no sugar; colour from tropical ageing."),
    "rum-habitation-velier-forsyths-151": (8.2, 2, "HV Forsyths 151 Proof White (75,5%) — ekstremni bijeli jamajčanski pure single. Prozirna boja; bez šećera.",
        "HV Forsyths 151 Proof White (75.5%) — extreme white Jamaican pure single. Clear colour; no sugar."),
    "rum-papalin-5": (8.1, 3, "Papalin 5 YO High Ester (47%) — high ester pot still. Velier/Papalin: bez šećera; boja od bačve.",
        "Papalin 5 YO High Ester (47%) — high-ester pot still. Velier/Papalin: no sugar; colour from cask."),
    "rum-papalin-5-overproof": (8.3, 4, "Papalin 5 YO Overproof (57%) — visoki esteri. Bez šećera; boja od bačve.",
        "Papalin 5 YO Overproof (57%) — high esters. No sugar; colour from cask."),
    "rum-papalin-7": (8.3, 3, "Papalin 7 YO Pot Still (47%) — duže odležani Papalin. Čist; boja od bačve.",
        "Papalin 7 YO Pot Still (47%) — longer-aged Papalin. Clean; colour from cask."),
    "rum-papalin-reunion-10": (8.6, 4, "Papalin Réunion 10 YO (50%) — Papalin linija (etiketa na Allezu). Stilski čist pure single; boja od bačve.",
        "Papalin Réunion 10 YO (50%) — Papalin line (label on Allez). Style-wise clean pure single; colour from cask."),
    "rum-velier-tiger-shark-2019": (8.8, 4, "Velier Royal Navy Tiger Shark 2019 (57,2%) — pure vatted navy. Velier: bez šećera; boja od blenda/bačve.",
        "Velier Royal Navy Tiger Shark 2019 (57.2%) — pure vatted navy. Velier: no sugar; colour from blend/cask."),
    "rum-cdi-jamaica-5": (7.8, 3, "CDI Jamaica 5 ans (43%) — nezavisni bottling. Tipično bez šećera; boja od bačve.",
        "CDI Jamaica 5 ans (43%) — independent bottling. Typically unsweetened; colour from cask."),
    "rum-cdi-jamaica-navy-5": (8.0, 4, "CDI Jamaica Navy Strength 5 YO (57%) — jači jamajčanski bottling. Čist; boja od bačve.",
        "CDI Jamaica Navy Strength 5 YO (57%) — stronger Jamaican bottling. Clean; colour from cask."),
    "rum-black-tot-rum": (7.5, 4, "Black Tot Rum (46,2%) — navy blend. Tipično čist-ish; boja od blenda (nije lab g/L šećera).",
        "Black Tot Rum (46.2%) — navy blend. Typically clean-ish; colour from blend (no lab sugar g/L)."),
    "rum-black-tot-mbr-2021": (8.8, 4, "Black Tot MBR 2021 (54,5%) — limited navy blend, gušći od osnovnog. Tipično bez jakog doziranja; tamna boja od blenda.",
        "Black Tot MBR 2021 (54.5%) — limited navy blend, denser than core. Typically without heavy dosing; dark colour from blend."),
}
for rid, (q, body, hr, en) in JAMAICA.items():
    add = NAVY if "black-tot" in rid or "tiger" in rid else (BOTTLER if "cdi" in rid or "exchange" in rid or "kill" in rid or "habitation" in rid or "papalin" in rid or "velier" in rid else JAM)
    put(rid, add, q, hr, en, body)

# Riise — apply pack + short honest notes for all a-h / ah-riise ids via prefix in apply()
# Zacapa / Botran / Dominican / Mauritius / CDI / St Lucia — compact
OTHER = {
    "rum-zacapa-centenario-23": (SOLERA_SWEET, 7.0, 3, "Zacapa 23 Solera Gran Reserva (40%) — gvatemalski solera, mekan i slađkast. Tipično doslađen s karamelom za boju (nije lab g/L).",
        "Zacapa 23 Solera Gran Reserva (40%) — Guatemalan solera, soft and sweetish. Typically sweetened with caramel for colour (no lab g/L)."),
    "rum-zacapa-ambar": (SOLERA_MOD, 6.8, 3, "Zacapa Ámbar 12 (40%, 1 l) — mlađi Zacapa solera. Umjeren šećer + boja tipični za liniju (stilska procjena).",
        "Zacapa Ámbar 12 (40%, 1 l) — younger Zacapa solera. Moderate sugar + colour typical of the line (style estimate)."),
    "rum-zacapa-edicion-negra": (SOLERA_SWEET, 7.2, 4, "Zacapa Edición Negra (43%) — tamnija, punija ekspresija. Doslađen stil; tamna boja uz E150 uobičajena.",
        "Zacapa Edición Negra (43%) — darker, fuller expression. Sweetened style; dark colour with E150 usual."),
    "rum-zacapa-xo": (SOLERA_SWEET, 7.5, 4, "Zacapa XO (40%) — XO solera, bogatiji od 23. Doslađen; boja podešena karamelom (stilska procjena).",
        "Zacapa XO (40%) — XO solera, richer than 23. Sweetened; colour adjusted with caramel (style estimate)."),
    "rum-zacapa-royal": (SOLERA_SWEET, 7.8, 4, "Zacapa Royal (45%) — premium solera. Snažno desertni/slađeni stil; tamna boja.",
        "Zacapa Royal (45%) — premium solera. Strongly dessert/sweetened style; dark colour."),
    "rum-zacapa-la-doma": (SOLERA_SWEET, 8.2, 4, "Zacapa La Doma Heavenly Cask (40%) — posebna cask kolekcija nad 23 bazom. Isti doslađeni solera pristup.",
        "Zacapa La Doma Heavenly Cask (40%) — special cask collection over the 23 base. Same sweetened solera approach."),
    "rum-zacapa-30-aniversario": (SOLERA_SWEET, 9.0, 4, "Zacapa 30 Aniversario (40%) — raritetna jubilarna boca. Solera stil s šećerom i bojom; ocjena zbog starosti, ne 'čistoće'.",
        "Zacapa 30 Aniversario (40%) — rare anniversary bottle. Solera style with sugar and colour; score for age, not 'cleanness'."),
    "rum-zacapa-etiqueta-negra-23": (SOLERA_SWEET, 8.5, 4, "Zacapa Etiqueta Negra 23 (43%) — raritetnija crna etiketa. Doslađen solera; tamna boja.",
        "Zacapa Etiqueta Negra 23 (43%) — rarer black label. Sweetened solera; dark colour."),
    "rum-zacapa-reserva-limitada-2015": (SOLERA_SWEET, 8.7, 4, "Zacapa RL 2015 (45%) — limited release, gušći i slađi. Šećer + boja (stilska procjena).",
        "Zacapa RL 2015 (45%) — limited release, denser and sweeter. Sugar + colour (style estimate)."),
    "rum-zacapa-reserva-limitada-2019": (SOLERA_SWEET, 8.3, 4, "Zacapa RL 2019 (45%) — novija limited solera. Doslađen stil; boja podešena.",
        "Zacapa RL 2019 (45%) — newer limited solera. Sweetened style; colour adjusted."),
    "rum-zacapa-el-alma": (SOLERA_SWEET, 7.8, 3, "Zacapa El Alma 23 Limited (40%) — limited nad 23 bazom. Isti solera/šećer/boja obrazac.",
        "Zacapa El Alma 23 Limited (40%) — limited over the 23 base. Same solera/sugar/colour pattern."),
    "rum-botran-oro": (SOLERA_MOD, 5.5, 2, "Botran Añejo Oro (40%) — ulazni gvatemalski solera. Umjeren šećer + boja tipični (nije lab).",
        "Botran Añejo Oro (40%) — entry Guatemalan solera. Moderate sugar + colour typical (not lab)."),
    "rum-botran-12": (SOLERA_MOD, 7.0, 3, "Botran 12 Solera (40%) — solidan dnevni solera. Tipično umjeren šećer i E150.",
        "Botran 12 Solera (40%) — solid daily solera. Typically moderate sugar and E150."),
    "rum-botran-18-solera": (SOLERA_MOD, 7.2, 3, "Botran 18 Solera 1893 (40%, 1 l) — starija Botran solera. Umjeren šećer + karamel za boju (stilska procjena).",
        "Botran 18 Solera 1893 (40%, 1 l) — older Botran solera. Moderate sugar + caramel for colour (style estimate)."),
    "rum-botran-1893-decanter": (SOLERA_MOD, 7.2, 3, "Botran 1893 Decanter (40%) — klasični 1893. Isti solera obrazac: šećer + boja.",
        "Botran 1893 Decanter (40%) — classic 1893. Same solera pattern: sugar + colour."),
    "rum-botran-primera-edicion": (SOLERA_MOD, 8.2, 4, "Botran Primera Edición (40%, 0,75 l) — premium gold. Solera s umjerenim šećerom; boja podešena.",
        "Botran Primera Edición (40%, 0.75 l) — premium gold. Solera with moderate sugar; colour adjusted."),
    "rum-ron-centenario-25": (SOLERA_MOD, 7.5, 3, "Ron Centenario 25 (40%) — kostarikanski solera. Tipično umjeren šećer + E150 (nije lab).",
        "Ron Centenario 25 (40%) — Costa Rican solera. Typically moderate sugar + E150 (not lab)."),
    "rum-kirk-sweeney-gran-reserva": (SOLERA_MOD, 7.0, 3, "Kirk and Sweeney Gran Reserva (40%) — dominikanski rum, mekani karamel. Tipično umjeren šećer + boja.",
        "Kirk and Sweeney Gran Reserva (40%) — Dominican rum, soft caramel. Typically moderate sugar + colour."),
    "rum-kirk-sweeney-18": (SOLERA_MOD, 7.0, 3, "Kirk and Sweeney 18 Reserva (40%) — dominikanski rum. Solera/hispan stil: šećer i boja uobičajeni (nije lab).",
        "Kirk and Sweeney 18 Reserva (40%) — Dominican rum. Solera/Hispanic style: sugar and colour usual (not lab)."),
    "rum-kirk-sweeney-23": (SOLERA_MOD, 7.3, 4, "Kirk and Sweeney 23 Reserva (40%) — starija reserva, puniji slatki profil. Umjeren šećer + boja.",
        "Kirk and Sweeney 23 Reserva (40%) — older reserva, fuller sweet profile. Moderate sugar + colour."),
    "rum-kirk-sweeney-gran-reserva-superior": (SOLERA_MOD, 7.2, 3, "Kirk and Sweeney Gran Reserva Superior (40%) — korak iznad Gran Reservé. Isti doslađeni obrazac.",
        "Kirk and Sweeney Gran Reserva Superior (40%) — a step above Gran Reserva. Same sweetened pattern."),
    "rum-kirk-sweeney-xo-no5-bio": (SOLERA_MOD, 8.2, 4, "Kirk and Sweeney XO No.5 BIO (65,5%) — cask strength limited. BIO ne znači nužno 0 šećera; stil hispan/solera (nije lab).",
        "Kirk and Sweeney XO No.5 BIO (65.5%) — cask-strength limited. BIO does not necessarily mean 0 sugar; Hispanic/solera style (not lab)."),
    "rum-matusalem-platino": (SOLERA_MOD, 5.5, 1, "Matusalem Platino (40%) — bijeli/solera-blender za koktele. Moguć blagi šećer; boja filtrirana.",
        "Matusalem Platino (40%) — white/solera-blender for cocktails. Light sugar possible; colour filtered."),
    "rum-matusalem-7": (SOLERA_MOD, 6.0, 2, "Matusalem 7 Anos (40%) — ulazni solera, mekani karamel. Umjeren šećer + boja (stilska procjena).",
        "Matusalem 7 Anos (40%) — entry solera, soft caramel. Moderate sugar + colour (style estimate)."),
    "rum-matusalem-10-clasico": (SOLERA_MOD, 6.5, 3, "Matusalem 10 Solera Clásico (40%) — klasični solera. Tipično umjeren šećer i E150.",
        "Matusalem 10 Solera Clásico (40%) — classic solera. Typically moderate sugar and E150."),
    "rum-ron-matusalem-15": (SOLERA_MOD, 7.0, 3, "Matusalem 15 Solera Gran Reserva (40%) — starija gran reserva. Umjeren šećer + boja.",
        "Matusalem 15 Solera Gran Reserva (40%) — older gran reserva. Moderate sugar + colour."),
    "rum-matusalem-23": (SOLERA_MOD, 7.5, 4, "Matusalem 23 Solera Gran Reserva (40%) — bogatiji slatki profil. Solera s šećerom i karamelom (nije lab).",
        "Matusalem 23 Solera Gran Reserva (40%) — richer sweet profile. Solera with sugar and caramel (not lab)."),
    "rum-opthimus-15-res-laude": (SOLERA_MOD, 6.8, 3, "Opthimus 15 Res Laude (38%) — dominikanski solera, mekan i slatkast. Tipično šećer + boja.",
        "Opthimus 15 Res Laude (38%) — Dominican solera, soft and sweetish. Typically sugar + colour."),
    "rum-opthimus-15-oporto": (SOLERA_MOD, 7.2, 3, "Opthimus 15 Solera Oporto (43%) — port finish. Šećer + boja od porta/karamela.",
        "Opthimus 15 Solera Oporto (43%) — port finish. Sugar + colour from port/caramel."),
    "rum-opthimus-18-cum-laude": (SOLERA_MOD, 7.0, 3, "Opthimus 18 Cum Laude (38%) — slatki dominikanski stil. Umjeren šećer + E150.",
        "Opthimus 18 Cum Laude (38%) — sweet Dominican style. Moderate sugar + E150."),
    "rum-opthimus-21-magna-cum-laude": (SOLERA_MOD, 7.3, 4, "Opthimus 21 Magna Cum Laude (38%) — punija solera. Doslađen stil; boja podešena.",
        "Opthimus 21 Magna Cum Laude (38%) — fuller solera. Sweetened style; colour adjusted."),
    "rum-opthimus-25-malt-whisky": (SOLERA_MOD, 7.8, 4, "Opthimus 25 Malt Whisky Finish (43%) — whisky finish nad solera bazom. Šećer vjerojatan; boja od bačve + mogući karamel.",
        "Opthimus 25 Malt Whisky Finish (43%) — whisky finish over a solera base. Sugar likely; colour from cask + possible caramel."),
    "rum-opthimus-25-oporto": (SOLERA_MOD, 7.7, 4, "Opthimus 25 Solera Oporto (43%) — starija port-finish ekspresija. Solera + šećer + boja.",
        "Opthimus 25 Solera Oporto (43%) — older port-finish expression. Solera + sugar + colour."),
    "rum-opthimus-25-summa-cum-laude": (SOLERA_MOD, 7.6, 4, "Opthimus 25 Summa Cum Laude (38%) — vrhunac Cum Laude linije. Doslađen solera stil.",
        "Opthimus 25 Summa Cum Laude (38%) — top of the Cum Laude line. Sweetened solera style."),
    "rum-opthimus-xo-summa-cum-laude": (SOLERA_MOD, 8.0, 4, "Opthimus XO Summa Cum Laude (38%) — XO ekspresija. Šećer + boja (stilska procjena).",
        "Opthimus XO Summa Cum Laude (38%) — XO expression. Sugar + colour (style estimate)."),
    "rum-blue-mauritius-gold": (SOLERA_MOD, 6.2, 3, "Blue Mauritius Gold (40%) — mauricijski rum, mekani karamel. Tipično umjeren šećer + boja (nije lab).",
        "Blue Mauritius Gold (40%) — Mauritian rum, soft caramel. Typically moderate sugar + colour (not lab)."),
    "rum-new-grove-10": (MAU_LIGHT, 7.5, 3, "New Grove Old Tradition 10 YO (40%) — mauricijski island rum. Blagi dodatak moguć; boja od bačve (nije lab).",
        "New Grove Old Tradition 10 YO (40%) — Mauritian island rum. Light addition possible; colour from cask (not lab)."),
    "rum-new-grove-beau-plan-2007": (MAU_LIGHT, 8.0, 3, "New Grove Beau Plan 2007 (45%) — Savoir Faire vintage. Čistiji od gold linija; boja od bačve.",
        "New Grove Beau Plan 2007 (45%) — Savoir Faire vintage. Cleaner than gold lines; colour from cask."),
    "rum-new-grove-ville-bague-2004": (MAU_LIGHT, 8.3, 4, "New Grove Ville Bague 2004 (45%) — starija Savoir Faire. Boja od bačve; šećer nizak/nejasan bez lab podatka.",
        "New Grove Ville Bague 2004 (45%) — older Savoir Faire. Colour from cask; sugar low/unclear without lab data."),
    "rum-new-grove-emotion-1969": (MAU_LIGHT, 8.8, 4, "New Grove Emotion 1969 (47%) — premium mauricijski rum. Bogatiji profil; boja od bačve (nije lab šećer).",
        "New Grove Emotion 1969 (47%) — premium Mauritian rum. Richer profile; colour from cask (no lab sugar)."),
    "rum-cdi-caraibes": (BOTTLER, 7.5, 3, "CDI Caraïbes (40%) — blended Caribbean. Bottler praksa: tipično bez šećera; boja od bačve.",
        "CDI Caraïbes (40%) — blended Caribbean. Bottler practice: typically unsweetened; colour from cask."),
    "rum-cdi-latino-5": (BOTTLER, 7.2, 3, "CDI Latino 5 ans (40%) — latino blend. Tipično čist; boja od bačve.",
        "CDI Latino 5 ans (40%) — Latino blend. Typically clean; colour from cask."),
    "rum-cdi-tricorne-white": (BOTTLER, 7.0, 2, "CDI Tricorne White (43%) — bijeli blend. Prozirna boja; tipično bez šećera.",
        "CDI Tricorne White (43%) — white blend. Clear colour; typically unsweetened."),
    "rum-cdi-west-indies-8": (BOTTLER, 7.8, 3, "CDI West Indies 8 YO (40%) — blended West Indies. Čist bottler stil; boja od bačve.",
        "CDI West Indies 8 YO (40%) — blended West Indies. Clean bottler style; colour from cask."),
    "rum-cdi-guyana-30": (BOTTLER, 9.3, 4, "CDI Guyana 30 ans (48%) — raritetni Demerara single cask. Bottler: bez šećera; boja od 30 godina hrasta.",
        "CDI Guyana 30 ans (48%) — rare Demerara single cask. Bottler: no sugar; colour from 30 years of oak."),
    "rum-cdi-mauritius-13-armagnac": (BOTTLER, 8.5, 4, "CDI Mauritius 13 Armagnac Finish (53,1%) — cask strength. Čist bottler; boja od bačve/armagnaca.",
        "CDI Mauritius 13 Armagnac Finish (53.1%) — cask strength. Clean bottler; colour from cask/Armagnac."),
    "rum-cdi-spiced": (SPICED, 5.5, 2, "CDI Spiced (40%) — spiced bottling. Šećer i arome; boja često podešena.",
        "CDI Spiced (40%) — spiced bottling. Sugar and flavourings; colour often adjusted."),
    "rum-admiral-rodney-hms-formidable": (ST_LUCIA, 8.5, 3, "Admiral Rodney HMS Formidable (40%) — vanilija, hrast, tihi duhan. Tipično čist; boja od bačve.",
        "Admiral Rodney HMS Formidable (40%) — vanilla, oak, quiet tobacco. Typically clean; colour from cask."),
    "rum-admiral-rodney-hms-monarch": (ST_LUCIA, 8.0, 3, "Admiral Rodney HMS Monarch (40%) — pristupačniji Rodney. Tipično čist; zlatna boja od bačve.",
        "Admiral Rodney HMS Monarch (40%) — more approachable Rodney. Typically clean; gold from cask."),
    "rum-admiral-rodney-officers-2-irish": (ST_LUCIA, 8.4, 3, "Admiral Rodney Officer's N°2 Irish Cask 2009 (45%) — Irish finish. Tipično čist distillate; boja od finisha.",
        "Admiral Rodney Officer's N°2 Irish Cask 2009 (45%) — Irish finish. Typically clean distillate; colour from finish."),
    "rum-chairmans-masters-selection-coffey": (ST_LUCIA, 8.5, 4, "Chairman's Master's Selection Coffey Still (46,2%) — column-still Svete Lucije. Tipično čist; boja od bačve.",
        "Chairman's Master's Selection Coffey Still (46.2%) — Saint Lucia column still. Typically clean; colour from cask."),
    "rum-chairmans-legacy": (ST_LUCIA, 7.5, 3, "Chairman's Reserve Legacy (43%) — klasični Saint Lucia stil. Tipično čist; boja od bačve.",
        "Chairman's Reserve Legacy (43%) — classic Saint Lucia style. Typically clean; colour from cask."),
    "rum-chairmans-vintage-2009": (ST_LUCIA, 8.2, 3, "Chairman's Reserve Vintage 2009 (46%) — berba 2009. Tipično čist; boja od bačve.",
        "Chairman's Reserve Vintage 2009 (46%) — 2009 vintage. Typically clean; colour from cask."),
    "rum-chairmans-forgotten-casks": (ST_LUCIA, 7.8, 3, "Chairman's Forgotten Casks (40%) — starije bačve, mekši profil. Tipično čist; boja od bačve.",
        "Chairman's Forgotten Casks (40%) — older casks, softer profile. Typically clean; colour from cask."),
    "rum-chairmans-spiced": (SPICED, 5.5, 2, "Chairman's Spiced Original (40%) — spiced; šećer i arome; boja podešena. Za highball.",
        "Chairman's Spiced Original (40%) — spiced; sugar and flavourings; colour adjusted. For highballs."),
    "rum-banks-7-golden-age": (BOTTLER, 7.5, 3, "Banks 7 Golden Age (43%) — multi-island blend. Tipično čist; boja od blenda.",
        "Banks 7 Golden Age (43%) — multi-island blend. Typically clean; colour from blend."),
    "rum-banks-5": (BOTTLER, 7.2, 2, "Banks 5 (43%) — multi-island blend. Tipično čist; boja od blenda.",
        "Banks 5 (43%) — multi-island blend. Typically clean; colour from blend."),
}
for rid, (add, q, body, hr, en) in OTHER.items():
    put(rid, add, q, hr, en, body)


def riise_notes(name: str) -> dict:
    return {
        "hr": f"{name} — slađeni spirit drink (EU oznaka zbog šećera). Karamel za boju je uobičajen; nema javnog lab g/L u našem izvoru.",
        "en": f"{name} — sweetened spirit drink (EU label due to sugar). Caramel colouring is common; no public lab g/L in our source.",
    }


def main() -> None:
    enrich = _load_part_a()
    enrich.update(B)

    rums = json.loads(P.read_text(encoding="utf-8"))
    by = {r["id"]: r for r in rums}

    # Auto-cover any remaining A.H. Riise ids
    for r in rums:
        if r["id"] in enrich:
            continue
        if r["id"].startswith("rum-ah-riise") or r["id"].startswith("rum-a-h-riise"):
            add = SPICED if "spiced" in r["id"] else RIISE
            enrich[r["id"]] = {
                **deepcopy(add),
                "qualityScore": r.get("qualityScore") or 5.5,
                "notes": riise_notes(r["name"]),
            }

    updated = 0
    missing = []
    for rid, fields in enrich.items():
        r = by.get(rid)
        if not r:
            missing.append(rid)
            continue
        for k, v in fields.items():
            r[k] = v
        # ensure notes en exists
        if isinstance(r.get("notes"), dict) and not r["notes"].get("en"):
            r["notes"]["en"] = r["notes"].get("hr", "")
        updated += 1

    P.write_text(json.dumps(rums, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(P, OUT / f"rums-allez-backup-{stamp}.json")
    shutil.copy2(P, OUT / "rums-allez-latest.json")

    # honesty report: how many still style-estimate
    stil = sum(1 for r in rums if "stilska" in (r.get("additiveSource") or "").lower() or "Stilska" in (r.get("additiveSource") or ""))
    clean = sum(1 for r in rums if r.get("additiveStatus") == "clean")
    print(f"enriched={updated} missing={len(missing)} total={len(rums)} map={len(enrich)}")
    print(f"catalog clean={clean} style_estimate_sources={stil}")
    if missing:
        print("missing:", ", ".join(missing[:25]))


if __name__ == "__main__":
    main()
