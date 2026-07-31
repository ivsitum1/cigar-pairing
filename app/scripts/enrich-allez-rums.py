# -*- coding: utf-8 -*-
"""Enrich Allez-added rums: notes, sugar/colour additives, editorial qualityScore.

Honesty rules:
- No invented g/L hydrometer numbers.
- Colour = caramel E150 (or none), declared in additiveDetail with sugar.
- qualityScore = editorial /10 (same scale as rest of catalog), calibrated to peers.
- Sources stated honestly (AOC / producer claim / style estimate).
"""
from __future__ import annotations

import json
import shutil
from copy import deepcopy
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "src" / "data" / "rums.json"
OUT = Path(__file__).resolve().parent / "output"

# --- additive packs --------------------------------------------------------

AOC = {
    "additiveStatus": "clean",
    "additiveDetail": {
        "hr": "Bez dodanog šećera i bez karamela (AOC Martinique)",
        "en": "No added sugar and no caramel colouring (Martinique AOC)",
    },
    "additiveSource": "AOC zakon (zabranjeni aditivi)",
    "sweetness": 1,
}

GUAD_CLEAN = {
    "additiveStatus": "clean",
    "additiveDetail": {
        "hr": "Agricole Guadeloupe — tipično bez šećera; boja od bačve (nije lab)",
        "en": "Guadeloupe agricole — typically unsweetened; colour from cask (not lab-verified)",
    },
    "additiveSource": "Stilska procjena (agricole Guadeloupe) — nije lab/hidrometar",
    "sweetness": 1,
}

FDC = {
    "additiveStatus": "clean",
    "additiveDetail": {
        "hr": "Proizvođač: 0 dodanog šećera, bez umjetne boje",
        "en": "Producer: 0 added sugar, no artificial colour",
    },
    "additiveSource": "Dekl. proizvođača (Flor de Caña — zero sugar / no artificial colour)",
    "sweetness": 1,
}

FSQ = {
    "additiveStatus": "clean",
    "additiveDetail": {
        "hr": "Foursquare/Doorly's — bez doziranog šećera; boja od bačve",
        "en": "Foursquare/Doorly's — no dosed sugar; colour from cask",
    },
    "additiveSource": "Dekl. (Foursquare)",
    "sweetness": 1,
}

MG = {
    "additiveStatus": "clean",
    "additiveDetail": {
        "hr": "Mount Gay — tipično čist Barbados profil; boja od bačve (nije lab)",
        "en": "Mount Gay — typically clean Barbados profile; colour from cask (not lab)",
    },
    "additiveSource": "Stilska procjena (Mount Gay / Barbados) — nije lab mjerenje",
    "sweetness": 1,
}

JAM = {
    "additiveStatus": "clean",
    "additiveDetail": {
        "hr": "Jamajčanski pure single / estate — bez doziranog šećera; boja od bačve",
        "en": "Jamaican pure single / estate — no dosed sugar; colour from cask",
    },
    "additiveSource": "Pravilo regije / stil destilerije — nije hidrometar mjerenje",
    "sweetness": 1,
}

BOTTLER = {
    "additiveStatus": "clean",
    "additiveDetail": {
        "hr": "Nezavisni bottler — tipično bez šećera; boja od bačve",
        "en": "Independent bottler — typically unsweetened; colour from cask",
    },
    "additiveSource": "Dekl./praksa bottlera — nije lab mjerenje",
    "sweetness": 1,
}

RIISE = {
    "additiveStatus": "sweetened",
    "additiveDetail": {
        "hr": "Spirit drink — dodani šećer; karamel čest (EU oznaka zbog šećera)",
        "en": "Spirit drink — added sugar; caramel colour common (EU label due to sugar)",
    },
    "additiveSource": "EU oznaka spirit drink + stilska procjena — nije hidrometar",
    "sweetness": 4,
}

SPICED = {
    "additiveStatus": "flavored",
    "additiveDetail": {
        "hr": "Aromatizirano/spiced — šećer i arome; boja često podešena",
        "en": "Flavoured/spiced — sugar and flavourings; colour often adjusted",
    },
    "additiveSource": "Stilska procjena (aromatizirano/spiced) — nije lab mjerenje",
    "sweetness": 5,
}

SOLERA_MOD = {
    "additiveStatus": "moderate",
    "additiveDetail": {
        "hr": "Solera stil — tipično umjeren šećer + karamel E150 (nije lab)",
        "en": "Solera style — typically moderate sugar + E150 caramel (not lab-verified)",
    },
    "additiveSource": "Stilska procjena (solera/hispan) — nije lab/hidrometar",
    "sweetness": 3,
}

SOLERA_SWEET = {
    "additiveStatus": "sweetened",
    "additiveDetail": {
        "hr": "Doslađen solera profil; karamel E150 uobičajen (nije lab g/L)",
        "en": "Sweetened solera profile; E150 caramel usual (no lab g/L)",
    },
    "additiveSource": "Stilska procjena (doslađen solera) — nije lab/hidrometar",
    "sweetness": 4,
}

LIQ = {
    "additiveStatus": "flavored",
    "additiveDetail": {
        "hr": "Rum-liker — šećer i arome (naranča); boja od sastojaka",
        "en": "Rum liqueur — sugar and flavourings (orange); colour from ingredients",
    },
    "additiveSource": "Kategorija likera — deklarativno aromatizirano",
    "sweetness": 5,
}

ST_LUCIA = {
    "additiveStatus": "clean",
    "additiveDetail": {
        "hr": "St Lucia Distillers — tipično čist/vrlo nizak šećer; boja od bačve",
        "en": "St Lucia Distillers — typically clean/very low sugar; colour from cask",
    },
    "additiveSource": "Stilska procjena (St Lucia Distillers) — nije lab mjerenje",
    "sweetness": 1,
}


def note(hr: str, en: str) -> dict:
    return {"hr": hr, "en": en}


def hint(hr: str, en: str) -> dict:
    return {"hr": hr, "en": en}


# id -> partial override
ENRICH: dict[str, dict] = {}


def e(id_: str, *, add: dict, q: float, body: int | None = None, tags: list[str] | None = None,
      notes: dict | None = None, cigar: dict | None = None, serving: dict | None = None) -> None:
    d: dict = {"qualityScore": q, **deepcopy(add)}
    if body is not None:
        d["body"] = body
    if tags is not None:
        d["flavorTags"] = tags
    if notes is not None:
        d["notes"] = notes
    if cigar is not None:
        d["cigarHint"] = cigar
    if serving is not None:
        d["serving"] = serving
    ENRICH[id_] = d


# ========== Martinique AOC / agricole =====================================
e("rum-clement-blanc-canne-bleue", add=AOC, q=7.8, body=1,
  tags=["travnato", "vegetalno", "citrus"],
  notes=note(
      "Clément Blanc Canne Bleue (50%) je bijeli AOC agricole s Habitation Clément: svježa trska, citrusna kora i biljni ton. Boja je prozirna — nema karamela. Klasik za Ti' Punch; u čaši je suh i oštar dok se ne razrijedi.",
      "Clément Blanc Canne Bleue (50%) is a white AOC agricole from Habitation Clément: fresh cane, citrus peel and herbal tone. The colour is clear — no caramel. A Ti' Punch classic; neat it is dry and sharp until diluted.",
  ),
  cigar=hint("Uz blanc biraj laganu Connecticut ili natural — travnati citrus treba prostor.",
             "With blanc choose a light Connecticut or natural — grassy citrus needs room."),
  serving={"neat": 2, "water": 2, "rocks": 0, "highball": 3, "cola": 0, "best": "Ti' Punch"})

e("rum-clement-ambre", add=AOC, q=7.4, body=2,
  tags=["travnato", "vanilija", "hrast"],
  notes=note(
      "Clément Ambré (40%) kratko odležava u hrastu: još travnat, s blagom vanilijom i zlatnom bojom isključivo od bačve. Lagani sipper ili Ti' Punch s malo zrelosti.",
      "Clément Ambré (40%) ages briefly in oak: still grassy, with light vanilla and a golden colour only from cask. A light sipper or Ti' Punch with a touch of maturity.",
  ))

e("rum-clement-select-barrel", add=AOC, q=7.5, body=2,
  tags=["travnato", "citrus", "vanilija"],
  notes=note(
      "Clément Select Barrel (40%) spaja agricole travnatost s kraćim hrastom — pristupačni martinique stil, suh, bez šećera i bez umjetne boje.",
      "Clément Select Barrel (40%) joins agricole grassiness with shorter oak — an approachable Martinique style, dry, without sugar or artificial colour.",
  ))

e("rum-clement-vsop-agricole", add=AOC, q=8.5, body=2,
  tags=["travnato", "citrus", "vanilija"],
  notes=note(
      "Clément VSOP s Habitation Clément (Martinique AOC) odležava najmanje 4 godine: mješavina novih i bourbon bačava daje mokku, kakao, kandiranu naranču i vaniliju uz travnatu agricole bazu. U čaši je suh, srednje lagan i jasan kad se pije čisto.",
      "Clément VSOP from Habitation Clément (Martinique AOC) ages at least four years: new and bourbon casks bring mocha, cocoa, candied orange and vanilla over a grassy agricole base. In the glass it is dry, light-medium and clearest neat.",
  ))

e("rum-clement-xo", add=AOC, q=8.6, body=3,
  tags=["travnato", "hrast", "suho-voce"],
  notes=note(
      "Clément XO (42%) dulje odležava od VSOP-a: više hrasta, kakaa i kandiranog voća uz AOC agricole bazu. Amber do bakrene boje dolazi od bačve, ne od karamela. Namijenjen čistom servisu.",
      "Clément XO (42%) ages longer than VSOP: more oak, cocoa and candied fruit on an AOC agricole base. Amber-to-copper colour comes from cask, not caramel. Meant for neat service.",
  ),
  cigar=hint("XO podnosi srednji Habano ili blagi maduro s cedrom.",
             "XO handles a medium Habano or mild maduro with cedar."))

e("rum-clement-10-ans", add=AOC, q=8.8, body=3,
  tags=["travnato", "hrast", "suho-voce"],
  notes=note(
      "Clément 10 Ans: deset godina u hrastu — mokka, suho voće i začin nad agricole bazom. Tamnija bakrena boja je od dugog odležavanja; šećer i E150 zabranjeni su AOC-om.",
      "Clément 10 Ans: ten years in oak — mocha, dried fruit and spice over an agricole base. Darker copper colour is from long ageing; sugar and E150 are banned by the AOC.",
  ))

e("rum-clement-15-ans", add=AOC, q=9.0, body=4,
  tags=["travnato", "hrast", "suho-voce"],
  notes=note(
      "Clément 15 Ans je starija Habitation ekspresija: dublji hrast, suho voće i mirnija travnata kičma. U čaši punije tijelo; pije se čisto.",
      "Clément 15 Ans is an older Habitation expression: deeper oak, dried fruit and a quieter grassy spine. Fuller body in the glass; drink neat.",
  ))

e("rum-clement-single-batch-canne-bleue", add=AOC, q=8.4, body=3,
  tags=["travnato", "zacini", "hrast"],
  notes=note(
      "Clément Très Rhum Single Batch 100% Canne Bleue (46,1%, 0,5 l) — uža serija, intenzivnija trska i začin. AOC čist; boja od bačve.",
      "Clément Très Rhum Single Batch 100% Canne Bleue (46.1%, 0.5 l) — a tighter batch, more intense cane and spice. AOC-clean; colour from cask.",
  ))

e("rum-clement-moka-torrefie", add=AOC, q=8.3, body=3,
  tags=["travnato", "kava", "hrast"],
  notes=note(
      "Clément Single Cask Moka Torréfié 05 (41,8%, 0,5 l) — finish s pečenom kavom nad agricole kičmom. AOC: bez šećera i karamela.",
      "Clément Single Cask Moka Torréfié 05 (41.8%, 0.5 l) — roasted-coffee finish over an agricole spine. AOC: no sugar or caramel.",
  ))

e("rum-clement-chauffe-extreme", add=AOC, q=8.3, body=3,
  tags=["travnato", "hrast", "zacini"],
  notes=note(
      "Clément Chauffe Extrême Single Batch (46,9%, 0,5 l) — limited, intenzivniji pečeni/hrastov profil. Čist AOC agricole.",
      "Clément Chauffe Extrême Single Batch (46.9%, 0.5 l) — limited, more intense roasted/oak profile. Clean AOC agricole.",
  ))

e("rum-clement-creole-shrubb", add=LIQ, q=5.5, body=1,
  tags=["slatko", "citrus"],
  notes=note(
      "Clément Créole Shrubb (40%) — narančasti rum-liker s Martiniquea. Slatkoća i boja dolaze od likerskih sastojaka, ne od čistog AOC ruma. Za Ti' Punch varijante i rocks.",
      "Clément Créole Shrubb (40%) — orange rum liqueur from Martinique. Sweetness and colour come from liqueur ingredients, not neat AOC rum. For Ti' Punch variants and rocks.",
  ))

for rid, name_bit, price_q, body, tags, hr, en in [
    ("rum-depaz-vsop", "VSOP", 8.0, 2, ["travnato", "vegetalno", "citrus"],
     "Depaz VSOP (45%) s Saint-Pierrea: vulkansko tlo, travnata trska i blagi hrast. AOC čist — bez šećera i bez E150; zlatna boja od bačve. Puniji od Plantationa.",
     "Depaz VSOP (45%) from Saint-Pierre: volcanic soil, grassy cane and light oak. AOC-clean — no sugar and no E150; gold colour from cask. Fuller than Plantation."),
    ("rum-depaz-vieux", "Plantation", 7.8, 2, ["travnato", "vegetalno", "citrus"],
     "Depaz Vieux Plantation (45%) — martinique agricole s vulkanskog tla, vegetalan i začinski. AOC: bez aditiva; boja od kraćeg odležavanja.",
     "Depaz Vieux Plantation (45%) — Martinique agricole from volcanic soil, vegetal and spicy. AOC: no additives; colour from shorter ageing."),
    ("rum-depaz-xo", "XO", 8.7, 3, ["travnato", "hrast", "suho-voce"],
     "Depaz XO Grande Réserve (45%) — odležani vrh Depaza: dubok, kompleksan agricole. Tamnija bakrena boja od bačve; šećer zabranjen AOC-om.",
     "Depaz XO Grande Réserve (45%) — Depaz's aged flagship: a deep, complex agricole. Darker copper from cask; sugar banned by the AOC."),
]:
    e(rid, add=AOC, q=price_q, body=body, tags=tags, notes=note(hr, en))

e("rum-hse-vo", add=AOC, q=7.8, body=2, tags=["travnato", "citrus", "vanilija"],
  notes=note(
      "HSE VO (42%) je mlađi vieux Habitation Saint-Étienne — citrus, trska i lagani hrast. AOC čist; svijetlo zlatna boja od bačve.",
      "HSE VO (42%) is a younger vieux from Habitation Saint-Étienne — citrus, cane and light oak. AOC-clean; light gold from cask.",
  ))
e("rum-hse-vsop-agricole", add=AOC, q=8.2, body=2, tags=["travnato", "citrus", "vanilija"],
  notes=note(
      "Habitation Saint-Étienne VSOP je martinique agricole s citrusom, vanilijom i svježom trskom nakon nekoliko godina u hrastu. Lagani do srednje lagani sipper; AOC bez šećera i karamela.",
      "Habitation Saint-Étienne VSOP is Martinique agricole with citrus, vanilla and fresh cane after several years in oak. A light to light-medium sipper; AOC with no sugar or caramel.",
  ))
e("rum-hse-xo-agricole", add=AOC, q=8.6, body=3, tags=["travnato", "hrast", "suho-voce"],
  notes=note(
      "HSE XO dulje odležava: više hrasta, suhog voća i začina uz agricole kičmu. Puniji od VSOP-a; boja dublja od bačve, bez E150.",
      "HSE XO ages longer: more oak, dried fruit and spice on an agricole spine. Fuller than VSOP; deeper cask colour, no E150.",
  ))
e("rum-hse-black-sheriff", add=AOC, q=7.9, body=2, tags=["travnato", "vanilija", "hrast"],
  notes=note(
      "HSE Black Sheriff American Barrel (40%) — agricole u američkom hrastu: vanilija i blagi begin uz travnatu bazu. AOC čist.",
      "HSE Black Sheriff American Barrel (40%) — agricole in American oak: vanilla and light toast over a grassy base. AOC-clean.",
  ))
e("rum-hse-port-cask-finish", add=AOC, q=8.2, body=3, tags=["travnato", "crveno-voce", "hrast"],
  notes=note(
      "HSE VSOP Port Cask Finish (45%) — agricole VSOP s port finishom: crveno voće nad travnatom kičmom. AOC i dalje zabranjuje šećer; boja može biti malo tamnija od porta.",
      "HSE VSOP Port Cask Finish (45%) — agricole VSOP with port finish: red fruit over a grassy spine. AOC still bans sugar; colour may run a touch darker from port.",
  ))
e("rum-hse-kilchoman-cask-finish", add=AOC, q=8.5, body=3, tags=["travnato", "dim", "hrast"],
  notes=note(
      "HSE Extra Vieux Kilchoman Cask Finish 2014 (44%, 0,5 l) — peaty Islay finish nad martinique agricole. Rijetka kombinacija; AOC čist.",
      "HSE Extra Vieux Kilchoman Cask Finish 2014 (44%, 0.5 l) — peaty Islay finish over Martinique agricole. A rare pairing; AOC-clean.",
  ))

e("rum-rhum-j-m-vsop-agricole", add=AOC, q=8.3, body=2, tags=["travnato", "vegetalno", "citrus"],
  notes=note(
      "J.M VSOP (Habitation Bellevue, Macouba) tipično nosi 4+ godine u hrastu: svježa trska, citrusna kora i blagi začin, još uvijek laganog tijela. AOC čist; klasika za Ti' Punch ili čistu čašu.",
      "J.M VSOP (Habitation Bellevue, Macouba) typically carries 4+ years in oak: fresh cane, citrus peel and light spice, still light-bodied. AOC-clean; a classic for Ti' Punch or a neat pour.",
  ))
e("rum-rhum-j-m-xo-agricole", add=AOC, q=8.7, body=3, tags=["travnato", "hrast", "suho-voce"],
  notes=note(
      "J.M XO dulje odležava (često 6+ godina): hrast, suho voće i začin nadograđuju agricole bazu. Pije se čisto; AOC bez šećera i karamela.",
      "J.M XO ages longer (often 6+ years): oak, dried fruit and spice build on the agricole base. Drink neat; AOC with no sugar or caramel.",
  ))
e("rum-jm-epices-creoles", add=AOC, q=7.9, body=2, tags=["travnato", "zacini", "citrus"],
  notes=note(
      "J.M Épices Créoles (46%) — agricole s kreolskim začinom; jači začinski ton uz travnatu bazu. AOC čist.",
      "J.M Épices Créoles (46%) — agricole with Creole spice; stronger spice over a grassy base. AOC-clean.",
  ))
e("rum-jm-fumee-volcanique", add=AOC, q=8.0, body=2, tags=["travnato", "dim", "zacini"],
  notes=note(
      "J.M Fumée Volcanique (49%) — dimljeni/vulkanski karakter uz agricole trsku; intenzivniji sipper. Bez šećera (AOC).",
      "J.M Fumée Volcanique (49%) — smoked/volcanic character with agricole cane; a more intense sipper. No sugar (AOC).",
  ))
e("rum-jm-canopee", add=AOC, q=9.0, body=4, tags=["travnato", "hrast", "suho-voce"],
  notes=note(
      "J.M Canopée Hors d'Âge (46%) — novija premium linija; dubok hrast i zrela trska. AOC čist; tamnija boja od dugog odležavanja.",
      "J.M Canopée Hors d'Âge (46%) — newer premium line; deep oak and ripe cane. AOC-clean; darker colour from long ageing.",
  ))
e("rum-jm-millesime-2004", add=AOC, q=9.1, body=4, tags=["travnato", "hrast", "suho-voce"],
  notes=note(
      "J.M Vieux Agricole Millésimé 2004 (42,9%) — berba 2004, duga odležavanja, kompleksan hors d'âge. AOC; boja isključivo od bačve.",
      "J.M Vieux Agricole Millésimé 2004 (42.9%) — 2004 vintage, long ageing, complex hors d'âge. AOC; colour solely from cask.",
  ))
e("rum-jm-millesime-2011", add=AOC, q=8.7, body=3, tags=["travnato", "hrast", "citrus"],
  notes=note(
      "J.M Vieux Agricole Millésimé 2011 (41,9%) — berba 2011; zreli hrast uz agricole bazu. AOC čist.",
      "J.M Vieux Agricole Millésimé 2011 (41.9%) — 2011 vintage; ripe oak over an agricole base. AOC-clean.",
  ))
e("rum-jm-single-barrel-1999", add=AOC, q=9.2, body=4, tags=["travnato", "hrast", "suho-voce"],
  notes=note(
      "J.M Single Barrel Hors d'Âge 1999 (43,6%, 0,5 l) — limited single barrel, raritetna berba. AOC; bez šećera i E150.",
      "J.M Single Barrel Hors d'Âge 1999 (43.6%, 0.5 l) — limited single barrel, rare vintage. AOC; no sugar or E150.",
  ))
e("rum-jm-single-barrel-2015", add=AOC, q=8.8, body=3, tags=["travnato", "hrast", "zacini"],
  notes=note(
      "J.M Single Barrel Vieux 2015 (55,1%) — cask strength single barrel, intenzivniji agricole. AOC čist.",
      "J.M Single Barrel Vieux 2015 (55.1%) — cask-strength single barrel, more intense agricole. AOC-clean.",
  ))
e("rum-jm-shrubb", add=LIQ, q=5.5, body=1, tags=["slatko", "citrus"],
  notes=note(
      "J.M Shrubb (35%) — narančasti rum-liker Habitation Bellevue; desertniji od čistog agricole. Šećer i arome su dio likera.",
      "J.M Shrubb (35%) — orange rum liqueur from Habitation Bellevue; sweeter than neat agricole. Sugar and flavourings are part of the liqueur.",
  ))

e("rum-saint-james-vsop", add=AOC, q=7.9, body=2, tags=["travnato", "citrus", "vanilija"],
  notes=note(
      "Saint James VSOP Très Vieux (43%) — klasični martinique agricole VSOP: travnata trska, citrus i blagi hrast. AOC čist; zlatna boja od bačve.",
      "Saint James VSOP Très Vieux (43%) — classic Martinique agricole VSOP: grassy cane, citrus and light oak. AOC-clean; gold from cask.",
  ))
e("rum-saint-james-12-agricole", add=AOC, q=8.5, body=3, tags=["travnato", "hrast", "zacini"],
  notes=note(
      "Saint James 12 Year (Martinique) spaja agricole travnatost s dubljim hrastom i začinom nakon dvanaest godina. Srednje tijelo, suši završetak; AOC bez šećera.",
      "Saint James 12 Year (Martinique) joins agricole grassiness with deeper oak and spice after twelve years. Medium body, dry finish; AOC without sugar.",
  ))
e("rum-saint-james-xo-agricole", add=AOC, q=8.4, body=3, tags=["travnato", "hrast", "suho-voce"],
  notes=note(
      "Saint James XO — stariji Habitation stil: više hrasta i suhog voća uz agricole kičmu. AOC čist.",
      "Saint James XO — older Habitation style: more oak and dried fruit on an agricole spine. AOC-clean.",
  ))
e("rum-saint-james-15", add=AOC, q=8.9, body=4, tags=["travnato", "hrast", "suho-voce"],
  notes=note(
      "Saint James 15 Ans Réserve Privée (43%) — petnaest godina; dublji hrast uz martinique agricole. AOC; tamnija boja od bačve.",
      "Saint James 15 Ans Réserve Privée (43%) — fifteen years; deeper oak over Martinique agricole. AOC; darker colour from cask.",
  ))

e("rum-trois-rivieres-cannes-brulees", add=AOC, q=7.9, body=2, tags=["travnato", "karamela", "hrast"],
  notes=note(
      "Trois Rivières Cannes Brûlées (43%) — pečena trska/karamelizirani ton uz agricole kičmu. Nota karamele dolazi od pečenja trske i bačve, ne od dodanog šećera (AOC).",
      "Trois Rivières Cannes Brûlées (43%) — roasted cane/caramelised tone over an agricole spine. Caramel notes come from roasted cane and cask, not dosed sugar (AOC).",
  ))
e("rum-trois-rivieres-cuvee-ocean", add=AOC, q=7.5, body=1, tags=["travnato", "vegetalno", "citrus"],
  notes=note(
      "Trois Rivières Cuvée de l'Océan (42%) — svježi, mineralniji agricole; dobar za Ti' Punch. AOC čist; svijetla boja.",
      "Trois Rivières Cuvée de l'Océan (42%) — fresher, more mineral agricole; good for Ti' Punch. AOC-clean; pale colour.",
  ))
e("rum-trois-rivieres-cuvee-moulin", add=AOC, q=7.6, body=2, tags=["travnato", "vanilija", "hrast"],
  notes=note(
      "Trois Rivières Cuvée du Moulin (40%) — klasični vieux/ambre stil s blagim hrastom. AOC bez šećera i E150.",
      "Trois Rivières Cuvée du Moulin (40%) — classic vieux/ambre style with light oak. AOC without sugar or E150.",
  ))
e("rum-trois-rivieres-agricole", add=AOC, q=7.5, body=2, tags=["travnato", "citrus", "vegetalno"],
  notes=note(
      "Trois Rivières (meta/linija) — martinique agricole s travnatom bazom. Pojedinačne bocé (Océan, Moulin, Cannes Brûlées) imaju zasebne unose.",
      "Trois Rivières (meta/line) — Martinique agricole with a grassy base. Individual bottles (Océan, Moulin, Cannes Brûlées) have separate entries.",
  ))

# ========== Karukera Guadeloupe ============================================
e("rum-karukera-blanc", add=GUAD_CLEAN, q=7.5, body=1, tags=["travnato", "vegetalno", "citrus"],
  notes=note(
      "Karukera Blanc Agricole (50%) — bijeli Guadeloupe agricole; klasika za Ti' Punch. Prozirna boja; tipično bez šećera.",
      "Karukera Blanc Agricole (50%) — white Guadeloupe agricole; a Ti' Punch classic. Clear colour; typically unsweetened.",
  ))
e("rum-karukera-intense-blanc", add=GUAD_CLEAN, q=8.0, body=2, tags=["travnato", "vegetalno", "zacini"],
  notes=note(
      "Karukera L'Intense Blanc (63,8%) — high-proof bijeli agricole. Za koktele i razrijeđenu čistu čašu; bez doziranog šećera (stilska procjena).",
      "Karukera L'Intense Blanc (63.8%) — high-proof white agricole. For cocktails and a diluted neat pour; no dosed sugar (style estimate).",
  ))
e("rum-karukera-gold-premium", add=GUAD_CLEAN, q=6.5, body=2, tags=["travnato", "vanilija"],
  notes=note(
      "Karukera Gold Premium (40%) — pristupačniji gold/ambre stil Guadeloupea. Zlatna boja od kraćeg odležavanja; šećer nije deklariran kao dio stila.",
      "Karukera Gold Premium (40%) — more approachable gold/ambre Guadeloupe style. Gold from shorter ageing; sugar is not part of the declared style.",
  ))
e("rum-karukera-vieux-agricole-guadeloupe", add=GUAD_CLEAN, q=8.0, body=2, tags=["travnato", "vegetalno", "citrus"],
  notes=note(
      "Karukera Vieux Agricole (42%) — Guadeloupe agricole, travnata baza i blagi hrast. Tipično čist; boja od bačve (nije lab potvrda).",
      "Karukera Vieux Agricole (42%) — Guadeloupe agricole, grassy base and light oak. Typically clean; colour from cask (not lab-confirmed).",
  ))
e("rum-karukera-reserve-speciale", add=GUAD_CLEAN, q=8.0, body=3, tags=["travnato", "hrast", "suho-voce"],
  notes=note(
      "Karukera Réserve Spéciale Vieux (42%) — rezervna linija, uredan hrast uz Guadeloupe agricole. Bez tipičnog doziranja; boja od bačve.",
      "Karukera Réserve Spéciale Vieux (42%) — reserve line, tidy oak over Guadeloupe agricole. No typical dosing; colour from cask.",
  ))
e("rum-karukera-black-edition-alligator", add=GUAD_CLEAN, q=8.2, body=3, tags=["travnato", "hrast", "zacini"],
  notes=note(
      "Karukera Black Edition Alligator (45%, 1 l) — vieux agricole Guadeloupe, puniji hrast uz travnatu bazu. Tamnija boja od bačve; stilski bez šećera.",
      "Karukera Black Edition Alligator (45%, 1 l) — vieux agricole Guadeloupe, fuller oak over a grassy base. Darker cask colour; style-wise unsweetened.",
  ))
e("rum-karukera-expression-2008", add=GUAD_CLEAN, q=8.8, body=4, tags=["travnato", "hrast", "suho-voce"],
  notes=note(
      "Karukera L'Expression Millésime 2008 (48,1%) — berba 2008, intenzivniji agricole. Boja od dugog odležavanja; bez deklariranog šećera.",
      "Karukera L'Expression Millésime 2008 (48.1%) — 2008 vintage, more intense agricole. Colour from long ageing; no declared sugar.",
  ))
e("rum-karukera-christophe-colomb-1493", add=GUAD_CLEAN, q=9.0, body=4, tags=["travnato", "hrast", "suho-voce"],
  notes=note(
      "Karukera Christophe Colomb 1493 Hors d'Age (45%) — tres vieux premium linija. Duboka boja od bačve; stilski čist agricole.",
      "Karukera Christophe Colomb 1493 Hors d'Age (45%) — tres vieux premium line. Deep cask colour; style-wise clean agricole.",
  ))

def get_enrich() -> dict:
    return ENRICH
