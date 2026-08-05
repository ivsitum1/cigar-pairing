#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Expand thin rum notes/flavorTags without inventing sugar g/L.

- notes.hr shorter than 80 chars → replace with curated bilingual notes when mapped,
  else a style-based template that stays factual.
- flavorTags fewer than 3 → pad from style defaults (canonical slugs only).

Usage:
  python scripts/enrich-rum-taste-notes.py
  python scripts/enrich-rum-taste-notes.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RUMS = ROOT / "src" / "data" / "rums.json"
OUT = HERE / "output"

CANON = {
    "citrus", "dim", "duhan", "ester-funk", "hrast", "kakao",
    "karamela", "kava", "melasa", "orasasti", "overproof", "slatko",
    "suho-voce", "tamno-voce", "travnato", "tropsko-voce", "voce",
    "vanilija", "vegetalno", "zacini",
}

STYLE_TAGS = {
    "solera": ["karamela", "vanilija", "hrast"],
    "guatemala": ["karamela", "vanilija", "hrast"],
    "nicaragua-dry": ["vanilija", "hrast", "orasasti"],
    "jamaica": ["ester-funk", "tropsko-voce", "hrast"],
    "agricole": ["travnato", "citrus", "vegetalno"],
    "barbados": ["suho-voce", "vanilija", "hrast"],
    "cuba": ["duhan", "suho-voce", "hrast"],
    "dominican": ["karamela", "vanilija", "hrast"],
    "panama": ["karamela", "vanilija", "suho-voce"],
    "venezuela": ["karamela", "vanilija", "suho-voce"],
    "colombia": ["karamela", "suho-voce", "hrast"],
    "trinidad": ["vanilija", "hrast", "orasasti"],
    "puerto-rico": ["vanilija", "hrast", "orasasti"],
    "demerara": ["melasa", "hrast", "zacini"],
    "st-lucia": ["vanilija", "duhan", "hrast"],
    "spiced": ["zacini", "vanilija", "karamela"],
    "mixing": ["citrus", "travnato", "tropsko-voce"],
    "liqueur": ["slatko", "vanilija", "tropsko-voce"],
    "blend": ["vanilija", "hrast", "suho-voce"],
    "other": ["vanilija", "hrast", "karamela"],
}

# Curated notes for thin placeholders (no invented g/L).
NOTES: dict[str, tuple[str, str, list[str] | None]] = {
    "rum-barcelo-gran-anejo": (
        "Barceló Gran Añejo (37,5%) — dnevni dominikanski anejo: karamela, vanilija i blagi hrast. U čaši mekan; često i u highballu.",
        "Barceló Gran Añejo (37.5%) — everyday Dominican añejo: caramel, vanilla and soft oak. Soft in the glass; fine in a highball too.",
        ["karamela", "vanilija", "hrast"],
    ),
    "rum-barcelo-imperial-onyx": (
        "Barceló Imperial Onyx (38%) — tamniji Imperial: karamela, suho voće i blaga slatkoća. Najbolje čisto uz maduro ili jaču cigaru.",
        "Barceló Imperial Onyx (38%) — darker Imperial: caramel, dried fruit and gentle sweetness. Best neat with maduro or a stronger cigar.",
        ["karamela", "suho-voce", "vanilija"],
    ),
    "rum-planteray-3-stars-bijeli": (
        "Planteray 3 Stars (bijeli) — blending rum: tropsko voće, blagi arrak i svježe bilje. Primarno za koktele; uz laganu cigaru samo ako treba čist kontrast.",
        "Planteray 3 Stars (white) — blending rum: tropical fruit, light arrack and fresh herbs. Mainly for cocktails; with a light cigar only for clean contrast.",
        ["tropsko-voce", "citrus", "travnato"],
    ),
    "rum-planteray-original-dark": (
        "Planteray Original Dark — tamni blending stil: melasa, začini i karamela. Više koktel/rocks nego čisti sipper uz punu cigaru.",
        "Planteray Original Dark — dark blending style: molasses, spice and caramel. More cocktail/rocks than a neat sipper with a full cigar.",
        ["melasa", "zacini", "karamela"],
    ),
    "rum-ron-abuelo-anejo": (
        "Ron Abuelo Añejo — ulazni panamski anejo: karamela, vanilija i mekana slatkoća. Dobar za miješanje ili lagani sip uz blagu cigaru.",
        "Ron Abuelo Añejo — entry Panama añejo: caramel, vanilla and soft sweetness. Fine for mixing or an easy sip with a mild cigar.",
        ["karamela", "vanilija", "suho-voce"],
    ),
    "rum-botran-12": (
        "Botran Añejo 12 Solera (40%) — dnevni gvatemalski solera: karamela, vanilija i hrast. Mekan u čaši; čisto ili s kockom leda.",
        "Botran Añejo 12 Solera (40%) — everyday Guatemalan solera: caramel, vanilla and oak. Soft in the glass; neat or with one cube.",
        ["karamela", "vanilija", "hrast"],
    ),
    "rum-botran-8": (
        "Botran No.8 — lakša solera ulaznica: karamela i vanilija, manje hrasta od 12/18. Često highball ili lagani sipper.",
        "Botran No.8 — lighter solera entry: caramel and vanilla, less oak than 12/18. Often highball or an easy sipper.",
        ["karamela", "vanilija", "hrast"],
    ),
    "rum-botran-roaju": (
        "Botran Roaju — premium Botran ekspresija: gušća karamela, suho voće i zaobljeni hrast. Čisto, sporije gutljaje.",
        "Botran Roaju — premium Botran expression: denser caramel, dried fruit and rounded oak. Neat, slower sips.",
        ["karamela", "suho-voce", "hrast"],
    ),
    "rum-botran-15": (
        "Botran 15 Solera — srednja solera linija: karamela, vanilija i tihi hrast. Uredan dnevni sipper uz srednju cigaru.",
        "Botran 15 Solera — mid solera line: caramel, vanilla and quiet oak. Tidy everyday sipper with a medium cigar.",
        ["karamela", "vanilija", "hrast"],
    ),
    "rum-botran-1893-decanter": (
        "Botran Solera 1893 Decanter — klasični 1893 u decanteru: karamela, suho voće i meki hrast. Čisto, desertniji ton.",
        "Botran Solera 1893 Decanter — classic 1893 in a decanter: caramel, dried fruit and soft oak. Neat, dessert-leaning.",
        ["karamela", "suho-voce", "hrast"],
    ),
    "rum-zafra-21": (
        "Zafra Master Reserve 21 — panamski solera: karamela, vanilija i zaobljeni hrast. Mekan sipper uz maduro ili Connecticut.",
        "Zafra Master Reserve 21 — Panama solera: caramel, vanilla and rounded oak. Soft sipper with maduro or Connecticut.",
        ["karamela", "vanilija", "hrast"],
    ),
    "rum-zafra-30": (
        "Zafra Master Series 30 — starija panamska solera: dublji hrast, suho voće i slatka karamela. Sporiji gutljaj, čisto.",
        "Zafra Master Series 30 — older Panama solera: deeper oak, dried fruit and sweet caramel. Slower sips, neat.",
        ["karamela", "suho-voce", "hrast"],
    ),
    "rum-zacapa-royal": (
        "Zacapa Centenario Royal (45%) — premium solera: karamela, suho voće i baršunasta slatkoća. Čisto uz punu maduro cigaru.",
        "Zacapa Centenario Royal (45%) — premium solera: caramel, dried fruit and velvet sweetness. Neat with a full maduro.",
        ["karamela", "suho-voce", "vanilija"],
    ),
    "rum-zacapa-reserva-limitada-2019": (
        "Zacapa Reserva Limitada 2019 (45%) — limited solera: tamno voće, karamela i hrast. Desertniji ton; čisto.",
        "Zacapa Reserva Limitada 2019 (45%) — limited solera: dark fruit, caramel and oak. Dessert-leaning; neat.",
        ["tamno-voce", "karamela", "hrast"],
    ),
    "rum-opthimus-15-oporto": (
        "Opthimus 15 Solera Oporto (43%) — port finish: crveno voće, karamela i meki hrast. Čisto ili kap vode.",
        "Opthimus 15 Solera Oporto (43%) — port finish: red fruit, caramel and soft oak. Neat or a drop of water.",
        ["voce", "karamela", "hrast"],
    ),
    "rum-opthimus-18-cum-laude": (
        "Opthimus 18 Cum Laude (38%) — slatki dominikanski solera: vanilija, karamela i blagi hrast. Lagani sipper.",
        "Opthimus 18 Cum Laude (38%) — sweet Dominican solera: vanilla, caramel and soft oak. Easy sipper.",
        ["vanilija", "karamela", "hrast"],
    ),
    "rum-chairmans-spiced": (
        "Chairman's Reserve Spiced Original (40%) — spiced Sv. Lucija: vanilija, klinčić i karamela. Rocks ili cola; uz cigaru samo ako želite začinski kontrast.",
        "Chairman's Reserve Spiced Original (40%) — St Lucia spiced: vanilla, clove and caramel. Rocks or cola; with a cigar only for spice contrast.",
        ["zacini", "vanilija", "karamela"],
    ),
    "rum-companero-elixir-orange-jamajka": (
        "Compañero Elixir Orange — jamajčanska baza s narančom i jakim šećerom (lab). Liker-profil; desert uz blagu cigaru ili solo.",
        "Compañero Elixir Orange — Jamaican base with orange and heavy sugar (lab). Liqueur profile; dessert with a mild cigar or alone.",
        ["tropsko-voce", "slatko", "zacini"],
    ),
    "rum-havana-club-15yo": (
        "Havana Club 15 YO — zreli kubanski stil: duhan, suho voće i hrast. Čisto uz srednju do jaku cigaru.",
        "Havana Club 15 YO — mature Cuban style: tobacco, dried fruit and oak. Neat with a medium to full cigar.",
        ["duhan", "suho-voce", "hrast"],
    ),
    "rum-havana-club-7-anos": (
        "Havana Club 7 años — referentni kubanski anejo: duhan, koža i suho voće. Odličan value sipper uz cigaru.",
        "Havana Club 7 años — benchmark Cuban añejo: tobacco, leather and dried fruit. Excellent value sipper with a cigar.",
        ["duhan", "suho-voce", "hrast"],
    ),
    "rum-the-real-mccoy-12-foursquare": (
        "The Real McCoy 12 — Foursquare destilat: suho voće, hrast i čista vanilija. Suh sipper; čisto ili kap vode.",
        "The Real McCoy 12 — Foursquare distillate: dried fruit, oak and clean vanilla. Dry sipper; neat or a drop of water.",
        ["suho-voce", "hrast", "vanilija"],
    ),
    "rum-brugal-1888": (
        "Brugal 1888 — double-aged DR s sherry utjecajem: suho voće, hrast i blaga slatkoća. Čisto uz cigaru.",
        "Brugal 1888 — double-aged DR with sherry influence: dried fruit, oak and mild sweetness. Neat with a cigar.",
        ["suho-voce", "hrast", "vanilija"],
    ),
    "rum-coruba-12-cigar-jamajka": (
        "Coruba 12 Cigar — jamajčanski stil namijenjen sparivanju: melasa, ester i hrast. Čisto uz puniju cigaru.",
        "Coruba 12 Cigar — Jamaican style aimed at pairing: molasses, ester and oak. Neat with a fuller cigar.",
        ["melasa", "ester-funk", "hrast"],
    ),
    "rum-coruba-18-jamajka": (
        "Coruba 18 — stariji jamajčanac: dublji ester, suho voće i hrast. Sporiji gutljaj, čisto.",
        "Coruba 18 — older Jamaican: deeper ester, dried fruit and oak. Slower sips, neat.",
        ["ester-funk", "suho-voce", "hrast"],
    ),
    "rum-don-q-gran-anejo": (
        "Don Q Gran Añejo — portorikanski gran anejo: vanilija, hrast i orašasti ton. Suhiji sipper; čisto.",
        "Don Q Gran Añejo — Puerto Rican gran añejo: vanilla, oak and nutty tone. Drier sipper; neat.",
        ["vanilija", "hrast", "orasasti"],
    ),
    "rum-savanna-traditionnel-reunion": (
        "Savanna Traditionnel (Réunion) — traditionnel stil: trska, blagi začini i suho voće. Poseban otok; čisto ili kap vode.",
        "Savanna Traditionnel (Réunion) — traditionnel style: cane, light spice and dried fruit. Distinct island; neat or a drop of water.",
        ["travnato", "zacini", "suho-voce"],
    ),
    "rum-rum-nation-barbados-panama-demerara": (
        "Rum Nation (Barbados/Panama/Demerara) — bottler serija: ovisno o destilatu suho voće, hrast ili melasa. Birajte bocu, ne marku.",
        "Rum Nation (Barbados/Panama/Demerara) — bottler series: dried fruit, oak or molasses depending on distillate. Choose the bottle, not the brand.",
        ["suho-voce", "hrast", "vanilija"],
    ),
    "rum-bocatheva-15-yo-venezuela": (
        "Bocatheva 15 YO Venezuela — venezuelanski anejo: karamela, suho voće i meki hrast. Čisto, sporije.",
        "Bocatheva 15 YO Venezuela — Venezuelan añejo: caramel, dried fruit and soft oak. Neat, slower sips.",
        ["karamela", "suho-voce", "hrast"],
    ),
    "rum-dictador-20-yo": (
        "Dictador 20 YO — kolumbijski solera: karamela, suho voće i zaobljeni hrast. Mekan uz maduro.",
        "Dictador 20 YO — Colombian solera: caramel, dried fruit and rounded oak. Soft with maduro.",
        ["karamela", "suho-voce", "hrast"],
    ),
    "rum-dictador-12-yo": (
        "Dictador 12 YO — mlađi Dictador: karamela i vanilija, manje dubine od 20. Dnevni sipper.",
        "Dictador 12 YO — younger Dictador: caramel and vanilla, less depth than the 20. Everyday sipper.",
        ["karamela", "vanilija", "hrast"],
    ),
    "rum-pampero-aniversario": (
        "Pampero Aniversario — venezuelanski classics: karamela, vanilija i blagi hrast. Value sipper ili rocks.",
        "Pampero Aniversario — Venezuelan classic: caramel, vanilla and soft oak. Value sipper or rocks.",
        ["karamela", "vanilija", "hrast"],
    ),
    "rum-plantation-planteray-xo-20th": (
        "Planteray / Plantation XO 20th — Barbados XO: suho voće, hrast i slatka vanilija. Čisto uz srednju do jaku cigaru.",
        "Planteray / Plantation XO 20th — Barbados XO: dried fruit, oak and sweet vanilla. Neat with a medium to full cigar.",
        ["suho-voce", "hrast", "vanilija"],
    ),
    "rum-ron-cartavio-xo-18-peru": (
        "Ron Cartavio XO 18 (Peru) — peruanski XO: karamela, suho voće i hrast. Mekan solera ton; čisto.",
        "Ron Cartavio XO 18 (Peru) — Peruvian XO: caramel, dried fruit and oak. Soft solera tone; neat.",
        ["karamela", "suho-voce", "hrast"],
    ),
    "rum-vizcaya-vxop-cuban-formula": (
        "Vizcaya VXOP — DR u kubanskom ključu: duhan, karamela i suho voće. Bogat sipper uz maduro.",
        "Vizcaya VXOP — DR in a Cuban key: tobacco, caramel and dried fruit. Rich sipper with maduro.",
        ["duhan", "karamela", "suho-voce"],
    ),
    "rum-angostura-5-yo": (
        "Angostura 5 YO — trinidadski dnevni anejo: vanilija, hrast i orašasti ton. Suhiji sipper; čisto ili rocks.",
        "Angostura 5 YO — Trinidad everyday añejo: vanilla, oak and nutty tone. Drier sipper; neat or rocks.",
        ["vanilija", "hrast", "orasasti"],
    ),
    "rum-cihuatan-12-solera": (
        "Cihuatán 12 Solera — salvadorski solera: karamela, vanilija i hrast. Često suši od tipičnog hispano stila.",
        "Cihuatán 12 Solera — Salvadoran solera: caramel, vanilla and oak. Often drier than typical Hispanic style.",
        ["karamela", "vanilija", "hrast"],
    ),
    "rum-fortin-epopeya-paragvaj": (
        "Fortín Epopeya (Paragvaj) — rijetko podrijetlo: trska, karamela i blagi hrast. Kuriozitet; čisto.",
        "Fortín Epopeya (Paraguay) — rare origin: cane, caramel and soft oak. Curiosity; neat.",
        ["travnato", "karamela", "hrast"],
    ),
    "rum-goslings-black-seal": (
        "Gosling's Black Seal — bermudski dark: melasa, začini i tamni ton. Klasik za Dark'n'Stormy; i kao sipper.",
        "Gosling's Black Seal — Bermuda dark: molasses, spice and a dark tone. Dark'n'Stormy classic; also a sipper.",
        ["melasa", "zacini", "karamela"],
    ),
    "rum-lazy-dodo-mauricijus": (
        "Lazy Dodo (Mauricijus) — single estate: suho voće, hrast i blaga trska. Suhiji otok; čisto.",
        "Lazy Dodo (Mauritius) — single estate: dried fruit, oak and light cane. Drier island; neat.",
        ["suho-voce", "hrast", "travnato"],
    ),
    "rum-matusalem-gran-reserva": (
        "Matusalem Gran Reserva — klasika cigar-zajednice: karamela, vanilija i meki hrast. Čisto uz maduro.",
        "Matusalem Gran Reserva — cigar-community classic: caramel, vanilla and soft oak. Neat with maduro.",
        ["karamela", "vanilija", "hrast"],
    ),
    "rum-ron-dos-maderas-5-3-5-5": (
        "Ron Dos Maderas (5+3 / 5+5) — Barbados/Gvajana s sherry finishom: suho voće, karamela i hrast. Čisto.",
        "Ron Dos Maderas (5+3 / 5+5) — Barbados/Guyana with sherry finish: dried fruit, caramel and oak. Neat.",
        ["suho-voce", "karamela", "hrast"],
    ),
    "rum-ron-millonario-xo": (
        "Ron Millonario XO — peruanski XO: gust, sladak, karamela i tamno voće. Kontrast punoj maduro cigari.",
        "Ron Millonario XO — Peruvian XO: dense, sweet, caramel and dark fruit. Contrast with a full maduro.",
        ["karamela", "tamno-voce", "vanilija"],
    ),
    "rum-serum-ron-de-panama-10": (
        "Serum Ron de Panama 10 — panamski 10: vanilija, karamela i blagi hrast. Uredan sipper.",
        "Serum Ron de Panama 10 — Panama 10: vanilla, caramel and soft oak. Tidy sipper.",
        ["vanilija", "karamela", "hrast"],
    ),
    "rum-barcelo-imperial-standard": (
        "Barceló Imperial — dominikanski value Imperial: karamela, vanilija i meki hrast. Često rocks ili čisto.",
        "Barceló Imperial — Dominican value Imperial: caramel, vanilla and soft oak. Often rocks or neat.",
        ["karamela", "vanilija", "hrast"],
    ),
    "rum-diplomatico-mantuano": (
        "Diplomático Mantuano — suši od Reserva Exclusiva: vanilija, hrast i blaga karamela. Dnevni sipper.",
        "Diplomático Mantuano — drier than Reserva Exclusiva: vanilla, oak and light caramel. Everyday sipper.",
        ["vanilija", "hrast", "karamela"],
    ),
    "rum-gold-of-mauritius-dark-heritage-solera": (
        "Gold of Mauritius (Dark/Heritage/Solera) — mauricijski solera: karamela, začini i meki hrast. Pristojan sipper.",
        "Gold of Mauritius (Dark/Heritage/Solera) — Mauritius solera: caramel, spice and soft oak. Decent sipper.",
        ["karamela", "zacini", "hrast"],
    ),
    "rum-presidente-marti-15-dr": (
        "Presidente Martí 15 (DR) — Oliver & Oliver solera: karamela, vanilija i slatki hrast. Mekan uz maduro.",
        "Presidente Martí 15 (DR) — Oliver & Oliver solera: caramel, vanilla and sweet oak. Soft with maduro.",
        ["karamela", "vanilija", "hrast"],
    ),
    "rum-relicario-dr": (
        "Relicario (DR) — mekan ron dominicano: vanilija, karamela i blago suho voće. OK uz maduro.",
        "Relicario (DR) — soft Dominican ron: vanilla, caramel and light dried fruit. Fine with maduro.",
        ["vanilija", "karamela", "suho-voce"],
    ),
    "rum-ryoma-japan": (
        "Ryoma (Japan) — japanski rum od trske: čist, lagan, travnato-citrusni rub. Poseban sipper; čisto.",
        "Ryoma (Japan) — Japanese cane rum: clean, light, grassy-citrus edge. Distinct sipper; neat.",
        ["travnato", "citrus", "travnato"],
    ),
    "rum-sol-tarasco-4-yo-charanda": (
        "Sol Tarasco 4 YO (charanda) — meksička charanda: trska, blagi začini i suh ton. Kuriozitet; čisto.",
        "Sol Tarasco 4 YO (charanda) — Mexican charanda: cane, light spice and a dry tone. Curiosity; neat.",
        ["travnato", "zacini", "citrus"],
    ),
    "rum-bacardi-anejo-cuatro-4yo": (
        "Bacardi Añejo Cuatro — mlad 4 YO: vanilija, hrast i čist alkohol. Više koktel/highball nego teški sipper.",
        "Bacardi Añejo Cuatro — young 4 YO: vanilla, oak and clean spirit. More cocktail/highball than a heavy sipper.",
        ["vanilija", "hrast", "orasasti"],
    ),
    "rum-barcelo-imperial-maple-cask": (
        "Barceló Imperial Maple Cask — maple finish: javorov sirup, karamela i slatki hrast. Desertniji Imperial.",
        "Barceló Imperial Maple Cask — maple finish: maple syrup, caramel and sweet oak. Dessert-leaning Imperial.",
        ["karamela", "slatko", "hrast"],
    ),
    "rum-barcelo-imperial-misunara-cask": (
        "Barceló Imperial Mizunara Cask — japanski hrast finish: začini, vanilija i slatka karamela. Čisto, sporije.",
        "Barceló Imperial Mizunara Cask — Japanese oak finish: spice, vanilla and sweet caramel. Neat, slower sips.",
        ["zacini", "vanilija", "karamela"],
    ),
    "rum-havana-club-especial": (
        "Havana Club Especial — mlad kubanski rum: trska, blagi duhan i citrus. Najčešće highball ili lagani sip.",
        "Havana Club Especial — young Cuban rum: cane, light tobacco and citrus. Mostly highball or an easy sip.",
        ["travnato", "duhan", "citrus"],
    ),
    "rum-ratu-dark-5yo-fiji": (
        "Ratu Dark 5yo (Fiji) — fijijski dark: tropsko voće, melasa i blaga slatkoća. Egzotičan sipper.",
        "Ratu Dark 5yo (Fiji) — Fijian dark: tropical fruit, molasses and mild sweetness. Exotic sipper.",
        ["tropsko-voce", "melasa", "karamela"],
    ),
    "rum-ron-centenario-12-gran-legado": (
        "Ron Centenario 12 Gran Legado — kostarikanski solera: karamela, vanilija i meki hrast. Gladak dnevni sipper.",
        "Ron Centenario 12 Gran Legado — Costa Rican solera: caramel, vanilla and soft oak. Smooth everyday sipper.",
        ["karamela", "vanilija", "hrast"],
    ),
    "rum-rom-club-white": (
        "Rom Club White (Mauricijus) — bijeli blending rum: citrus, trska i tropsko voće. Koktel baza.",
        "Rom Club White (Mauritius) — white blending rum: citrus, cane and tropical fruit. Cocktail base.",
        ["citrus", "travnato", "tropsko-voce"],
    ),
    "rum-ron-centenario-20": (
        "Ron Centenario 20 — kostarikanska solera: karamela, suho voće i gladak hrast. Jednostavan, sladak sipper.",
        "Ron Centenario 20 — Costa Rican solera: caramel, dried fruit and smooth oak. Simple, sweet sipper.",
        ["karamela", "suho-voce", "hrast"],
    ),
    "rum-ron-centenario-1985": (
        "Ron Centenario 1985 — starija solera linija: mekana karamela, vanilija i blagi hrast. Desertniji ton.",
        "Ron Centenario 1985 — older solera line: soft caramel, vanilla and mild oak. Dessert-leaning.",
        ["karamela", "vanilija", "hrast"],
    ),
    "rum-maraboo-brown": (
        "Maraboo Brown — pristupačni smeđi rum: karamela i blagi začini. Primarno za miješanje.",
        "Maraboo Brown — approachable brown rum: caramel and light spice. Mainly for mixing.",
        ["karamela", "zacini", "vanilija"],
    ),
    "rum-professore-rum-carib-elixir": (
        "Professore Rum (Caribbean Elixir) — slađeni elixir profil: vanilija i karamela. Diskontni desertni stil.",
        "Professore Rum (Caribbean Elixir) — sweetened elixir profile: vanilla and caramel. Discount dessert style.",
        ["vanilija", "karamela", "slatko"],
    ),
    "rum-bacardi-carta-blanca-oro-negra": (
        "Bacardi Carta Blanca / Oro / Negra — globalni mixing standard: čist alkohol, citrus i blaga vanilija. Kokteli prije sippera.",
        "Bacardi Carta Blanca / Oro / Negra — global mixing standard: clean spirit, citrus and light vanilla. Cocktails before sipping.",
        ["citrus", "vanilija", "travnato"],
    ),
    "rum-barcelo-blanco": (
        "Barceló Blanco — dominikanski bijeli: citrus, trska i čist alkohol. Mojito, cuba libre, highball.",
        "Barceló Blanco — Dominican white: citrus, cane and clean spirit. Mojito, cuba libre, highball.",
        ["citrus", "travnato", "tropsko-voce"],
    ),
    "rum-pampero-blanco": (
        "Pampero Blanco — venezuelanski bijeli: citrus i trska. Koktel baza, ne teški sipper.",
        "Pampero Blanco — Venezuelan white: citrus and cane. Cocktail base, not a heavy sipper.",
        ["citrus", "travnato", "tropsko-voce"],
    ),
    "rum-remedy-spiced": (
        "Remedy Spiced — njemački spiced stil: vanilija, začini i karamela. Rocks ili cola; uz cigaru samo za začinski kontrast.",
        "Remedy Spiced — German spiced style: vanilla, spice and caramel. Rocks or cola; with a cigar only for spice contrast.",
        ["zacini", "vanilija", "karamela"],
    ),
    "rum-rom-club-classic-sherry-spiced": (
        "Rom Club Classic / Sherry Spiced — pristupačni spiced: vanilija i začini; sherry verzija donosi suho voće.",
        "Rom Club Classic / Sherry Spiced — approachable spiced: vanilla and spice; sherry version adds dried fruit.",
        ["zacini", "vanilija", "suho-voce"],
    ),
    "rum-bacardi-spiced": (
        "Bacardi Spiced — pristupačni spiced: vanilija, klinčić i karamela. Cola i highball.",
        "Bacardi Spiced — approachable spiced: vanilla, clove and caramel. Cola and highball.",
        ["zacini", "vanilija", "karamela"],
    ),
    "rum-captain-morgan-spiced-white-black": (
        "Captain Morgan Spiced / White / Black — masovni spiced: vanilija i začini. Cola prije čiste čaše.",
        "Captain Morgan Spiced / White / Black — mass-market spiced: vanilla and spice. Cola before a neat glass.",
        ["zacini", "vanilija", "karamela"],
    ),
    "rum-ron-cana-del-caribe-white": (
        "Ron Caña del Caribe White — osnovni bijeli rum: citrus, trska i čist alkohol. Koktel baza (mojito, cuba libre), ne teški sipper.",
        "Ron Caña del Caribe White — basic white rum: citrus, cane and clean spirit. Cocktail base (mojito, cuba libre), not a heavy sipper.",
        ["citrus", "travnato", "tropsko-voce"],
    ),
    "rum-sailor-jerry": (
        "Sailor Jerry (46%) — karipski spiced: vanilija, cimet i jači alkohol. Rocks ili cola.",
        "Sailor Jerry (46%) — Caribbean spiced: vanilla, cinnamon and higher proof. Rocks or cola.",
        ["zacini", "vanilija", "karamela"],
    ),
    "rum-the-bush-rum-pass-fr-spiced": (
        "The Bush Rum (Passionfruit / Spiced) — voćno aromatizirano: tropsko voće i slatki začini. Liker-ish koktel stil.",
        "The Bush Rum (Passionfruit / Spiced) — fruit-flavoured: tropical fruit and sweet spice. Liqueur-ish cocktail style.",
        ["tropsko-voce", "zacini", "slatko"],
    ),
    "rum-malibu": (
        "Malibu — kokosov liker na rum bazi (21%): kokos, slatkoća i lagani alkohol. Piña colada standard.",
        "Malibu — coconut rum liqueur (21%): coconut, sweetness and light alcohol. Piña colada standard.",
        ["tropsko-voce", "slatko", "vanilija"],
    ),
    "rum-bumbu-cream-liker": (
        "Bumbu Cream — krem liker na rum bazi (15%): vanilija, karamela i mliječna slatkoća. Desert solo.",
        "Bumbu Cream — cream liqueur on a rum base (15%): vanilla, caramel and dairy sweetness. Dessert alone.",
        ["vanilija", "karamela", "slatko"],
    ),
    "rum-cdi-spiced": (
        "Compagnie des Indes Spiced — bottler spiced: začini, vanilija i karamela. Rocks; uz cigaru samo za začinski kontrast.",
        "Compagnie des Indes Spiced — bottler spiced: spice, vanilla and caramel. Rocks; with a cigar only for spice contrast.",
        ["zacini", "vanilija", "karamela"],
    ),
    "rum-banks-5": (
        "Banks 5 Island (43%) — multi-island blend: vanilija, citrus i čist alkohol. Lagani sipper ili highball.",
        "Banks 5 Island (43%) — multi-island blend: vanilla, citrus and clean spirit. Easy sipper or highball.",
        ["vanilija", "citrus", "hrast"],
    ),
    "rum-banks-7-golden-age": (
        "Banks 7 Golden Age (43%) — širi blend: suho voće, vanilija i hrast. Čisto ili rocks.",
        "Banks 7 Golden Age (43%) — broader blend: dried fruit, vanilla and oak. Neat or rocks.",
        ["suho-voce", "vanilija", "hrast"],
    ),
    "rum-cdi-latino-5": (
        "CDI Latino 5 ans — latino blend: vanilija, hrast i blaga karamela. Tipično čist bottler profil.",
        "CDI Latino 5 ans — Latino blend: vanilla, oak and light caramel. Typically clean bottler profile.",
        ["vanilija", "hrast", "karamela"],
    ),
    "rum-cdi-tricorne-white": (
        "CDI Tricorne White (43%) — bijeli blend: citrus, trska i čist alkohol. Koktel ili lagani kontrast uz cigaru.",
        "CDI Tricorne White (43%) — white blend: citrus, cane and clean spirit. Cocktail or light contrast with a cigar.",
        ["citrus", "travnato", "tropsko-voce"],
    ),
    "rum-papalin-5-overproof": (
        "Papalin 5 YO Overproof (57%) — jamajčanski overproof: esteri, tropsko voće i hrast. Kap vode obavezna.",
        "Papalin 5 YO Overproof (57%) — Jamaican overproof: esters, tropical fruit and oak. A drop of water is essential.",
        ["ester-funk", "tropsko-voce", "overproof"],
    ),
    "rum-papalin-7": (
        "Papalin 7 YO Pot Still (47%) — duže odležani Papalin: esteri, suho voće i hrast. Čisto ili kap vode.",
        "Papalin 7 YO Pot Still (47%) — longer-aged Papalin: esters, dried fruit and oak. Neat or a drop of water.",
        ["ester-funk", "suho-voce", "hrast"],
    ),
    "rum-la-hechicera-extra-anejo-solera-21": (
        "La Hechicera Extra Añejo Solera 21 — kolumbijski solera: suho voće, hrast i orašasti ton. Suhiji hispano stil.",
        "La Hechicera Extra Añejo Solera 21 — Colombian solera: dried fruit, oak and nutty tone. Drier Hispanic style.",
        ["suho-voce", "hrast", "orasasti"],
    ),
    "rum-a-h-riise-xo": (
        "A.H. Riise XO — danski spirit drink: karamela, vanilija i jaka slatkoća. Desertni sipper; EU oznaka zbog šećera.",
        "A.H. Riise XO — Danish spirit drink: caramel, vanilla and strong sweetness. Dessert sipper; EU spirit-drink label.",
        ["karamela", "vanilija", "slatko"],
    ),
    "rum-ah-riise-family-reserve-1838": (
        "A.H. Riise Family Reserve Solera 1838 — bogat spirit drink: karamela, suho voće i slatki hrast. Sporiji gutljaj.",
        "A.H. Riise Family Reserve Solera 1838 — rich spirit drink: caramel, dried fruit and sweet oak. Slower sips.",
        ["karamela", "suho-voce", "slatko"],
    ),
    "rum-stroh-80-austrija": (
        "Stroh 80 (Austrija) — Inländer rum 80%: jak alkohol, začini i pečeni ton. Tradicionalno za kuhanje; oprezno u čaši.",
        "Stroh 80 (Austria) — Inländer rum 80%: high proof, spice and roasted tone. Traditionally for cooking; careful in the glass.",
        ["zacini", "melasa", "overproof"],
    ),
    "rum-soccaron-white": (
        "Soccaron White — jednostavan kolonski bijeli rum: citrus, trska i tropsko voće. Koktel baza prije čiste čaše.",
        "Soccaron White — simple column white rum: citrus, cane and tropical fruit. Cocktail base before a neat glass.",
        ["citrus", "travnato", "tropsko-voce"],
    ),
    "rum-capitan-bucanero-blanco": (
        "Capitan Bucanero Blanco — dominikanski bijeli mikser: citrus, trska i čist alkohol.",
        "Capitan Bucanero Blanco — Dominican white mixer: citrus, cane and clean spirit.",
        ["citrus", "travnato", "tropsko-voce"],
    ),
    "rum-four-monkeys-svijetli-tamni": (
        "Four Monkey's (svijetli/tamni) — pristupačni rum za miješanje: karamela ili citrus ovisno o boji. Kokteli prije sippera.",
        "Four Monkey's (light/dark) — approachable mixing rum: caramel or citrus depending on colour. Cocktails before sipping.",
        ["karamela", "citrus", "vanilija"],
    ),
    "rum-ratu-spiced-fiji": (
        "Ratu Spiced (Fiji) — začinjena fijijska linija: zacini, tropsko voće i karamela. Rocks ili cola.",
        "Ratu Spiced (Fiji) — spiced Fijian line: spice, tropical fruit and caramel. Rocks or cola.",
        ["zacini", "tropsko-voce", "karamela"],
    ),
    "rum-ron-centenario-25": (
        "Ron Centenario Gran Reserva 25 — kostarikanski solera: karamela, vanilija i meki hrast. Gladak, sladak sipper.",
        "Ron Centenario Gran Reserva 25 — Costa Rican solera: caramel, vanilla and soft oak. Smooth, sweet sipper.",
        ["karamela", "vanilija", "hrast"],
    ),
    "rum-ron-centenario-5": (
        "Ron Centenario 5 — mlađi kostarikanski anejo: vanilija, karamela i lagani hrast. Highball ili lagani sip.",
        "Ron Centenario 5 — younger Costa Rican añejo: vanilla, caramel and light oak. Highball or an easy sip.",
        ["vanilija", "karamela", "hrast"],
    ),
    "rum-matusalem-platino": (
        "Matusalem Platino — bijeli/solera blender: citrus, vanilija i čist alkohol. Koktel ili lagani kontrast.",
        "Matusalem Platino — white/solera blender: citrus, vanilla and clean spirit. Cocktail or light contrast.",
        ["citrus", "vanilija", "travnato"],
    ),
    "rum-flor-de-cana-5-clasico": (
        "Flor de Caña 5 YO Clásico — kratko odležani nikaragvanski: vanilija, hrast i orašasti ton. Čist dekl. stil.",
        "Flor de Caña 5 YO Clásico — briefly aged Nicaraguan: vanilla, oak and nutty tone. Declared clean style.",
        ["vanilija", "hrast", "orasasti"],
    ),
    "rum-flor-de-cana-extra-seco-4": (
        "Flor de Caña Extra Seco 4 — suh bijeli nikaragvanski: citrus, trska i čist alkohol. Koktel standard.",
        "Flor de Caña Extra Seco 4 — dry Nicaraguan white: citrus, cane and clean spirit. Cocktail standard.",
        ["citrus", "travnato", "vanilija"],
    ),
    "rum-flor-de-cana-4-oro": (
        "Flor de Caña 4 YO Oro — zlatni kratki anejo: vanilija, hrast i blago suho voće. Highball ili lagani sip.",
        "Flor de Caña 4 YO Oro — gold short añejo: vanilla, oak and light dried fruit. Highball or an easy sip.",
        ["vanilija", "hrast", "suho-voce"],
    ),
    "rum-karukera-gold-premium": (
        "Karukera Gold Premium — guadeloupski gold/ambre: trska, citrus i blagi hrast. Agricole pristupačniji ton.",
        "Karukera Gold Premium — Guadeloupe gold/ambre: cane, citrus and soft oak. More approachable agricole tone.",
        ["travnato", "citrus", "hrast"],
    ),
    "rum-pyrat-xo-anguilla-blend": (
        "Pyrat XO — blend s narančom i slatkoćom: tropsko voće, vanilija i desertni ton. Liker-ish sipper.",
        "Pyrat XO — blend with orange and sweetness: tropical fruit, vanilla and dessert tone. Liqueur-ish sipper.",
        ["tropsko-voce", "vanilija", "slatko"],
    ),
    "rum-takamaka-dark-spiced": (
        "Takamaka Dark Spiced (38%) — sejšelski spiced: zacini, vanilija i karamela. Rocks ili cola.",
        "Takamaka Dark Spiced (38%) — Seychelles spiced: spice, vanilla and caramel. Rocks or cola.",
        ["zacini", "vanilija", "karamela"],
    ),
    "rum-canerock-jamajka": (
        "Canerock — jamajčanska baza s vanilijom i kokosom: tropsko voće, zacini i slatkoća. Spiced/liker profil.",
        "Canerock — Jamaican base with vanilla and coconut: tropical fruit, spice and sweetness. Spiced/liqueur profile.",
        ["tropsko-voce", "zacini", "vanilija"],
    ),
    "rum-the-kraken-black-spiced": (
        "The Kraken Black Spiced — tamni spiced: zacini, karamela i melasa. Popularan rocks/cola stil.",
        "The Kraken Black Spiced — dark spiced: spice, caramel and molasses. Popular rocks/cola style.",
        ["zacini", "karamela", "melasa"],
    ),
    "rum-clement-creole-shrubb": (
        "Clément Créole Shrubb — narančasti rum-liker s Martiniquea: citrus, trska i gorka kora. Aperitiv ili desert.",
        "Clément Créole Shrubb — orange rum liqueur from Martinique: citrus, cane and bitter peel. Aperitif or dessert.",
        ["citrus", "travnato", "slatko"],
    ),
    "rum-jm-shrubb": (
        "J.M Shrubb — narančasti rum-liker Habitation Bellevue: citrus, trska i blaga slatkoća. Aperitiv.",
        "J.M Shrubb — Habitation Bellevue orange rum liqueur: citrus, cane and mild sweetness. Aperitif.",
        ["citrus", "travnato", "slatko"],
    ),
}


def style_key(rum: dict) -> str:
    s = (rum.get("style") or "").lower()
    if s in STYLE_TAGS:
        return s
    if "solera" in s:
        return "solera"
    if "agricole" in s:
        return "agricole"
    if "spiced" in s or "elixir" in s:
        return "spiced"
    if "mix" in s or "bijeli" in s or "white" in s:
        return "mixing"
    if "liqueur" in s or "liker" in s:
        return "liqueur"
    return "other"


def pad_tags(existing: list[str], rum: dict, forced: list[str] | None) -> list[str]:
    out = [t for t in existing if t in CANON]
    extras = forced or STYLE_TAGS.get(style_key(rum), STYLE_TAGS["other"])
    for t in extras:
        if t in CANON and t not in out:
            out.append(t)
        if len(out) >= 3:
            break
    return out[:5]


def template_notes(rum: dict) -> tuple[str, str]:
    name = rum.get("name") or rum["id"]
    region = rum.get("region") or ""
    tags = ", ".join((rum.get("flavorTags") or [])[:3]) or "vanilija, hrast"
    hr = (
        f"{name} ({region}) — profil: {tags}. U čaši srednje tijelo; čisto ili uz kocku leda, "
        f"ovisno o snazi alkohola."
    )
    en = (
        f"{name} ({region}) — profile: {tags}. Medium body in the glass; neat or with a cube, "
        f"depending on strength."
    )
    if len(hr) < 80:
        hr += " Sparivanje birajte prema tijelu cigare, ne prema marketinškom broju."
        en += " Match by cigar body, not by the marketing number on the bottle."
    return hr, en


def apply(dry_run: bool) -> None:
    rums = json.loads(RUMS.read_text(encoding="utf-8"))
    notes_n = 0
    tags_n = 0

    for rum in rums:
        rid = rum["id"]
        tags = list(rum.get("flavorTags") or [])
        note_hr = (rum.get("notes") or {}).get("hr") or ""

        forced_tags = None
        if rid in NOTES:
            hr, en, forced_tags = NOTES[rid]
            if len(note_hr) < 100 or note_hr != hr:
                rum["notes"] = {"hr": hr, "en": en}
                notes_n += 1
        elif len(note_hr) < 80:
            # Pad tags first so template can use them
            rum["flavorTags"] = pad_tags(tags, rum, None)
            tags = rum["flavorTags"]
            hr, en = template_notes(rum)
            rum["notes"] = {"hr": hr, "en": en}
            notes_n += 1

        new_tags = pad_tags(list(rum.get("flavorTags") or []), rum, forced_tags)
        if new_tags != list(rum.get("flavorTags") or []):
            rum["flavorTags"] = new_tags
            tags_n += 1

    print(f"notes_updated={notes_n} tags_updated={tags_n}")
    if dry_run:
        print("dry-run: no write")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = OUT / f"rums-before-taste-notes-{stamp}.json"
    shutil.copy2(RUMS, backup)
    RUMS.write_text(json.dumps(rums, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    shutil.copy2(RUMS, OUT / "rums-allez-latest.json")
    print(f"wrote {RUMS} (backup {backup.name})")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    apply(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
