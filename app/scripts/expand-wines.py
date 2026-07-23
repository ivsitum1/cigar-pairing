# -*- coding: utf-8 -*-
"""Proširi wines.json: split kompozita + flagship dodaci (pairing-first).

Pokretanje (iz app/):
  python scripts/expand-wines.py
  python scripts/expand-wines.py --dry-run
"""
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WINES_PATH = ROOT / "src" / "data" / "wines.json"

CLEAN = {
    "hr": "Standardno vinarstvo (sulfiti)",
    "en": "Standard winemaking (sulphites)",
}
FORTIFIED = {
    "hr": "Fortificirano vinskim destilatom; slatkoca iz zaustavljene fermentacije",
    "en": "Fortified with grape spirit; sweetness from arrested fermentation",
}
SPARKLING_BRUT = {
    "hr": "Standardno vinarstvo (sulfiti); dozaza secera u brut razini (<12 g/L)",
    "en": "Standard winemaking (sulphites); sugar dosage at brut level (<12 g/L)",
}
DESSERT = {
    "hr": "Standardno vinarstvo (sulfiti); prirodni zaostali secer (botritis / kasna berba)",
    "en": "Standard winemaking (sulphites); natural residual sugar (botrytis / late harvest)",
}

# Kompoziti koje skripta uklanja (zamjenjuju se konkretnim bocama).
REMOVE_IDS = {
    "wine-vintage-port",
    "wine-blandys-madeira-10",
    "wine-prosek-hvar",
    "wine-dingac",
    "wine-plavac-mali",
    "wine-postup",
    "wine-babic",
    "wine-amarone",
    "wine-ripasso",
    "wine-barolo",
    "wine-brunello",
    "wine-rioja-gran-reserva",
    "wine-crljenak",
    "wine-cabernet-sauvignon",
    "wine-malbec-mendoza",
    "wine-syrah-shiraz",
    "wine-zinfandel",
    "wine-chateauneuf",
    "wine-chianti-classico",
    "wine-pinot-noir",
    "wine-merlot-istra",
    "wine-frankovka",
    "wine-grasevina",
    "wine-posip",
    "wine-malvazija",
    "wine-chardonnay-barrique",
    "wine-riesling-mosel",
    "wine-champagne-brut",
    "wine-prosecco-docg",
    "wine-cartizze",
    "wine-cava-juve-y-camps",
    "wine-tomac-pjenusac",
    "wine-misal-persuric",
    "wine-sauternes",
}

# Keep ID-jevi: ostaju iz starog JSON-a (uz eventualni rename u RENAMES).
KEEP_IDS = {
    "wine-grahams-tawny-10",
    "wine-grahams-tawny-20",
    "wine-sandeman-tawny-20",
    "wine-taylors-lbv",
    "wine-fonseca-bin-27",
    "wine-grahams-six-grapes",
    "wine-lustau-amontillado",
    "wine-lustau-oloroso",
    "wine-lustau-px",
    "wine-tio-pepe-fino",
    "wine-teran",
    "wine-primitivo-sessantanni",
    "wine-franciacorta-ca-del-bosco",
    "wine-muskat-momjanski",
    "wine-mionetto-prosecco-doc",
    "wine-nino-franco-rustico",
    "wine-bottega-gold",
    "wine-tokaji-aszu-5",
    "wine-tokaji-aszu-6",
    "wine-tokaji-aszu-3",
    "wine-tokaji-essencia",
    "wine-tokaji-szamorodni-edes",
    "wine-tokaji-furmint-dry",
}

RENAMES = {
    "wine-tio-pepe-fino": "Tio Pepe Fino (Gonzalez Byass)",
    "wine-tokaji-aszu-5": "Royal Tokaji Aszú 5 Puttonyos",
    "wine-tokaji-aszu-6": "Oremus Tokaji Aszú 6 Puttonyos",
    "wine-tokaji-aszu-3": "Disznókő Tokaji Aszú 3 Puttonyos",
    "wine-tokaji-essencia": "Royal Tokaji Essencia",
    "wine-tokaji-szamorodni-edes": "Oremus Tokaji Szamorodni Édes",
    "wine-tokaji-furmint-dry": "Disznókő Tokaji Furmint (suhi)",
    "wine-teran": "Coronica Gran Teran",
}


def W(
    id: str,
    name: str,
    style: str,
    region: str,
    abv: float,
    body: int,
    sweetness: int,
    tags: list[str],
    qs: float,
    price: tuple[float, float],
    shop: str,
    serve: str,
    notes_hr: str,
    notes_en: str,
    *,
    additive: str = "clean",
    detail: dict | None = None,
    source: str = "Standard kategorije vino",
    price_url: str | None = None,
    approx: bool = True,
) -> dict:
    if detail is None:
        if additive == "fortified":
            detail = FORTIFIED
            source = "Standard kategorije porto/sherry/madeira"
        elif style == "sparkling":
            detail = SPARKLING_BRUT
            source = "Standard kategorije pjenusac"
        elif style == "dessert-wine" or sweetness >= 4 and style in ("prosek", "dessert-wine"):
            detail = DESSERT
        else:
            detail = CLEAN
    out: dict = {
        "id": id,
        "category": "wine",
        "name": name,
        "style": style,
        "region": region,
        "abv": abv,
        "body": body,
        "sweetness": sweetness,
        "flavorTags": tags,
        "additiveStatus": additive,
        "additiveDetail": detail,
        "additiveSource": source,
        "qualityScore": qs,
        "priceEUR": {"min": price[0], "max": price[1]},
        "shopHR": shop,
        "status": None,
        "pairable": True,
        "serving": {"best": serve},
        "cigarHint": None,
        "priceUrl": price_url,
        "notes": {"hr": notes_hr, "en": notes_en},
    }
    if approx:
        out["priceApprox"] = True
    return out


def new_entries() -> list[dict]:
    """Svi splitovi + novi flagshipi (bez KEEP zapisa)."""
    v = "Vinoteke"
    viv = "Vivat fina vina / vinoteke"
    hr = "Konzum / vinoteke"
    return [
        # --- Porto (split + add) ---
        W("wine-taylors-vintage", "Taylor's Vintage Port", "port-ruby", "Douro, Portugal", 20, 5, 4,
          ["tamno-voce", "kakao", "zacini", "hrast"], 9.0, (90, 160), viv, "Casa za porto, 14-16 C",
          "Deklarirano godište Taylor's: crna trešnja, kakao, začini, dug život. Vrh piramide uz punu cigaru.",
          "Declared Taylor's vintage: black cherry, cocoa, spice, long life. Peak of the pyramid with a full cigar.",
          additive="fortified"),
        W("wine-grahams-vintage", "Graham's Vintage Port", "port-ruby", "Douro, Portugal", 20, 5, 4,
          ["tamno-voce", "kakao", "suho-voce", "zacini"], 9.0, (90, 160), viv, "Casa za porto, 14-16 C",
          "Graham's vintage: bogato tamno voće i čokolada, malo slađi stil od Taylor's. Klasičan pairing uz maduro.",
          "Graham's vintage: rich dark fruit and chocolate, a touch sweeter than Taylor's. Classic pairing with maduro.",
          additive="fortified"),
        W("wine-dows-vintage", "Dow's Vintage Port", "port-ruby", "Douro, Portugal", 20, 5, 4,
          ["tamno-voce", "zacini", "kakao", "hrast"], 9.0, (85, 150), viv, "Casa za porto, 14-16 C",
          "Dow's: suši, strukturiraniji vintage; crno voće i papar. Odličan uz Habano punoće.",
          "Dow's: drier, more structured vintage; black fruit and pepper. Excellent with full Habano.",
          additive="fortified"),
        W("wine-taylors-tawny-10", "Taylor's Tawny Port 10 Y.O.", "port-tawny", "Douro, Portugal", 20, 3, 4,
          ["orasasti", "karamela", "suho-voce"], 8.0, (32, 42), viv, "Casa za porto, 14-16 C",
          "Taylor's 10 YO tawny: orasi, karamela, suhe smokve. Pouzdan partner srednjoj cigari.",
          "Taylor's 10 YO tawny: nuts, caramel, dried figs. A reliable partner for a medium cigar.",
          additive="fortified"),
        W("wine-taylors-tawny-20", "Taylor's Tawny Port 20 Y.O.", "port-tawny", "Douro, Portugal", 20, 4, 4,
          ["orasasti", "karamela", "suho-voce", "hrast"], 8.5, (55, 75), viv, "Casa za porto, 14-16 C",
          "Dublji Taylor's 20 YO: pečeni orasi, datulje, fina oksidacija. Univerzalan uz maduro.",
          "Deeper Taylor's 20 YO: roasted nuts, dates, fine oxidation. Universal with maduro.",
          additive="fortified"),
        W("wine-dows-lbv", "Dow's Late Bottled Vintage", "port-ruby", "Douro, Portugal", 20, 4, 4,
          ["tamno-voce", "zacini", "kakao"], 7.5, (18, 28), viv, "Casa za porto, 14-16 C",
          "Dow's LBV: zrelo crno voće i začini bez vintage cijene. Dobar svakodnevni ruby uz cigaru.",
          "Dow's LBV: ripe black fruit and spice without vintage pricing. A solid everyday ruby with a cigar.",
          additive="fortified"),
        W("wine-warres-otima-10", "Warre's Otima 10 Y.O. Tawny", "port-tawny", "Douro, Portugal", 20, 3, 4,
          ["orasasti", "karamela", "med"], 7.5, (25, 35), v, "Casa za porto, 14-16 C",
          "Warre's Otima: mekani tawny u elegantnoj boci; orasi i med. Lagan ulaz u porto uz cigaru.",
          "Warre's Otima: soft tawny in an elegant bottle; nuts and honey. An easy entry to port with a cigar.",
          additive="fortified"),
        # --- Sherry / madeira / prošek ---
        W("wine-la-gitana-manzanilla", "Hidalgo La Gitana Manzanilla", "sherry-dry", "Sanlucar, Španjolska", 15, 2, 1,
          ["mineralno", "orasasti", "citrus"], 8.0, (12, 18), viv, "Dobro ohladjeno, 6-8 C",
          "Najpoznatija manzanilla: morska svježina, badem, limuna kora. Uz najblažu Connecticut cigaru ili aperitiv.",
          "The best-known manzanilla: sea breeze, almond, lemon peel. With the mildest Connecticut or as an aperitif.",
          additive="fortified", source="Standard kategorije sherry"),
        W("wine-valdespino-tio-diego", "Valdespino Tio Diego Amontillado", "sherry-dry", "Jerez, Španjolska", 18, 3, 1,
          ["orasasti", "suho-voce", "mineralno"], 8.5, (22, 32), v, "Casa za sherry, 12-14 C",
          "Valdespino amontillado: orasi, jod, suha jabuka. Most između fino i olorosa uz srednju cigaru.",
          "Valdespino amontillado: nuts, iodine, dried apple. A bridge from fino to oloroso with a medium cigar.",
          additive="fortified", source="Standard kategorije sherry"),
        W("wine-blandys-bual-10", "Blandy's Bual 10 Y.O.", "madeira", "Madeira, Portugal", 19, 4, 4,
          ["orasasti", "suho-voce", "karamela", "med"], 8.0, (35, 48), viv, "Casa za madeira, 14-16 C",
          "Bual 10 YO: karamela, suhe marelice, dimna nota. Odličan uz maduro srednje snage.",
          "Bual 10 YO: caramel, dried apricot, a smoky note. Excellent with a medium-strength maduro.",
          additive="fortified", source="Standard kategorije madeira"),
        W("wine-blandys-malmsey-10", "Blandy's Malmsey 10 Y.O.", "madeira", "Madeira, Portugal", 19, 4, 5,
          ["med", "suho-voce", "karamela", "orasasti"], 8.0, (35, 48), viv, "Casa za madeira, 14-16 C",
          "Malmsey 10 YO: najslađi stil madeire; med, smokve, orasi. Desert uz blagi do srednji maduro.",
          "Malmsey 10 YO: Madeira's sweetest style; honey, figs, nuts. Dessert with a mild-to-medium maduro.",
          additive="fortified", source="Standard kategorije madeira"),
        W("wine-hh-madeira-10", "Henriques & Henriques 10 Y.O. Medium Rich", "madeira", "Madeira, Portugal", 19, 4, 4,
          ["orasasti", "karamela", "suho-voce"], 7.5, (28, 40), v, "Casa za madeira, 14-16 C",
          "H&H medium rich: uravnotežen madeira profil; orasi i karamela. Dobra alternativa Blandy's.",
          "H&H medium rich: balanced Madeira profile; nuts and caramel. A solid alternative to Blandy's.",
          additive="fortified", source="Standard kategorije madeira"),
        W("wine-tomic-prosek", "Tomić Prošek", "prosek", "Hvar, Hrvatska", 16, 4, 5,
          ["suho-voce", "med", "orasasti"], 8.0, (25, 40), hr, "Mala casa, 12-14 C",
          "Tomić s Hvara: tradicionalni prošek od plavca; suhe smokve i med. Lokalni desert uz cigaru.",
          "Tomić from Hvar: traditional Plavac prošek; dried figs and honey. A local dessert with a cigar.",
          additive="fortified", source="Standard kategorije prosek", detail={
              "hr": "Fortificirano / zaustavljena fermentacija; tradicionalni dalmatinski desert",
              "en": "Fortified / arrested fermentation; traditional Dalmatian dessert",
          }),
        W("wine-plancic-prosek", "Plančić Prošek", "prosek", "Hvar, Hrvatska", 15.5, 4, 5,
          ["med", "suho-voce", "karamela"], 7.5, (22, 35), hr, "Mala casa, 12-14 C",
          "Plančić: bogat hvarski prošek; med i suho voće. HR alternativa uz blagi maduro.",
          "Plančić: rich Hvar prošek; honey and dried fruit. A Croatian alternative with a mild maduro.",
          additive="fortified", source="Standard kategorije prosek", detail={
              "hr": "Fortificirano / zaustavljena fermentacija; tradicionalni dalmatinski desert",
              "en": "Fortified / arrested fermentation; traditional Dalmatian dessert",
          }),
        # --- Desert ---
        W("wine-rieussec-sauternes", "Château Rieussec Sauternes", "dessert-wine", "Bordeaux, Francuska", 13.5, 4, 5,
          ["med", "suho-voce", "citrus", "karamela"], 8.5, (45, 80), viv, "Ohladjeno, 8-10 C",
          "Rieussec (Rothschild): botritis med, marelica, limun. Klasika uz blagi maduro ili desert.",
          "Rieussec (Rothschild): botrytis honey, apricot, lemon. Classic with a mild maduro or dessert."),
        W("wine-suduiraut-sauternes", "Château Suduiraut Sauternes", "dessert-wine", "Bordeaux, Francuska", 13.5, 4, 5,
          ["med", "suho-voce", "karamela", "citrus"], 8.5, (50, 90), v, "Ohladjeno, 8-10 C",
          "Suduiraut: gust, kremast Sauternes; ananas, med, vanilija. Ozbiljan desertni pairing.",
          "Suduiraut: dense, creamy Sauternes; pineapple, honey, vanilla. A serious dessert pairing."),
        W("wine-disznoko-aszu-5", "Disznókő Tokaji Aszú 5 Puttonyos", "dessert-wine", "Tokaj, Mađarska", 11.5, 4, 5,
          ["med", "suho-voce", "citrus", "karamela"], 8.5, (40, 65), viv, "Ohladjeno, 8-10 C",
          "Disznókő 5 putt: med, marelica, limunova kora. Pouzdan Tokaj uz cigaru.",
          "Disznókő 5 putt: honey, apricot, lemon zest. Reliable Tokaji with a cigar."),
        # --- HR crveno ---
        W("wine-skaramuca-dingac", "Skaramuča Dingač", "red-full", "Pelješac, Hrvatska", 14.5, 5, 2,
          ["tamno-voce", "suho-voce", "zacini", "zemljano"], 8.5, (28, 45), "Madirazza / vinoteke", "Velika casa, 16-18 C",
          "Skaramuča s položaja Dingač: zreli plavac, suha trešnja, začini. Vrh HR crvenog uz Habano.",
          "Skaramuča from the Dingač site: ripe Plavac, dried cherry, spice. Peak Croatian red with Habano."),
        W("wine-madirazza-dingac", "Madirazza Dingač", "red-full", "Pelješac, Hrvatska", 14.5, 5, 2,
          ["tamno-voce", "zacini", "suho-voce", "hrast"], 8.5, (29, 52), "Madirazza webshop / vinoteke", "Velika casa, 16-18 C",
          "Madirazza Dingač: koncentrirani plavac s južne padine. Klasičan HR pairing uz punu cigaru.",
          "Madirazza Dingač: concentrated Plavac from the southern slope. Classic HR pairing with a full cigar."),
        W("wine-saints-hills-dingac", "Saints Hills Dingač", "red-full", "Pelješac, Hrvatska", 14.5, 5, 2,
          ["tamno-voce", "zacini", "hrast", "suho-voce"], 8.5, (35, 55), viv, "Velika casa, 16-18 C",
          "Saints Hills: moderniji, bačveni Dingač; crno voće i vanilija. Snaga uz maduro.",
          "Saints Hills: a more modern, barrel-aged Dingač; black fruit and vanilla. Power with maduro."),
        W("wine-zlatan-plavac", "Zlatan Otok Plavac Mali", "red-full", "Hvar, Hrvatska", 14, 4, 2,
          ["tamno-voce", "zacini", "zemljano"], 7.5, (12, 22), hr, "Velika casa, 16-18 C",
          "Zlatan: tipičan hvarski plavac; trešnja, papar, mediteran. Solidan HR crveni uz srednju cigaru.",
          "Zlatan: typical Hvar Plavac; cherry, pepper, Mediterranean notes. Solid HR red with a medium cigar."),
        W("wine-korta-katarina-plavac", "Korta Katarina Plavac Mali", "red-full", "Pelješac, Hrvatska", 14.5, 4, 2,
          ["tamno-voce", "hrast", "zacini"], 8.0, (25, 40), viv, "Velika casa, 16-18 C",
          "Korta Katarina: uređen, međunarodni stil plavca. Dobar most prema Novom svijetu uz cigaru.",
          "Korta Katarina: polished, international Plavac style. A good bridge to New World with a cigar."),
        W("wine-matusko-postup", "Matuško Postup", "red-full", "Pelješac, Hrvatska", 14.5, 5, 2,
          ["tamno-voce", "suho-voce", "zacini"], 8.0, (25, 42), hr, "Velika casa, 16-18 C",
          "Matuško Postup: susjed Dingača; zrelo voće i struktura. Ozbiljan plavac uz Habano.",
          "Matuško Postup: Dingač's neighbour; ripe fruit and structure. Serious Plavac with Habano."),
        W("wine-madirazza-postup", "Madirazza Postup", "red-full", "Pelješac, Hrvatska", 14.5, 5, 2,
          ["tamno-voce", "zacini", "zemljano"], 8.0, (24, 40), "Madirazza webshop", "Velika casa, 16-18 C",
          "Madirazza Postup: tamno voće i mediteranski začini. Pairing blizak Dingaču.",
          "Madirazza Postup: dark fruit and Mediterranean spice. Pairing close to Dingač."),
        W("wine-testament-babic", "Testament Babić", "red-full", "Primošten, Hrvatska", 14, 4, 2,
          ["tamno-voce", "mineralno", "zacini"], 8.0, (18, 30), viv, "Velika casa, 16-18 C",
          "Testament: moderno primoštensko babić; mineralnost i crvena trešnja. Karakter uz srednje-punu cigaru.",
          "Testament: modern Primošten Babić; minerality and red cherry. Character with a medium-full cigar."),
        W("wine-grabovac-babic", "Grabovac Babić", "red-full", "Primošten, Hrvatska", 13.5, 4, 1,
          ["tamno-voce", "zemljano", "zacini"], 7.5, (14, 24), hr, "Velika casa, 16-18 C",
          "Grabovac: klasični babić s kamenjara. Zemljano i začinsko uz Habano srednje snage.",
          "Grabovac: classic Babić from rocky soils. Earthy and spicy with a medium Habano."),
        W("wine-zlatan-crljenak", "Zlatan Otok Crljenak", "red-full", "Hvar, Hrvatska", 14, 4, 2,
          ["tamno-voce", "zacini", "voce"], 7.5, (18, 32), hr, "Velika casa, 16-18 C",
          "Crljenak (zinfandelov predak): crveno voće i papar. Zanimljiv HR most prema CA zinu.",
          "Crljenak (Zinfandel ancestor): red fruit and pepper. An interesting HR bridge to CA Zin."),
        W("wine-rizman-tribidrag", "Rizman Tribidrag", "red-full", "Dalmacija, Hrvatska", 14, 4, 2,
          ["tamno-voce", "zacini", "hrast"], 7.5, (20, 35), viv, "Velika casa, 16-18 C",
          "Rizman Tribidrag: isto sortno ime, bačveniji stil. Punije tijelo uz maduro.",
          "Rizman Tribidrag: same variety, more barrel-led style. Fuller body with maduro."),
        # --- IT / ES / FR crveno ---
        W("wine-masi-costasera", "Masi Costasera Amarone", "red-full", "Veneto, Italija", 15, 5, 2,
          ["suho-voce", "tamno-voce", "kakao", "zacini"], 8.5, (40, 60), viv, "Velika casa, 16-18 C",
          "Masi Costasera: suha trešnja, čokolada, začini. Jedan od najpouzdanijih Amaronea uz cigaru.",
          "Masi Costasera: dried cherry, chocolate, spice. One of the most reliable Amarones with a cigar."),
        W("wine-allegrini-amarone", "Allegrini Amarone della Valpolicella", "red-full", "Veneto, Italija", 15.5, 5, 2,
          ["suho-voce", "tamno-voce", "kakao", "hrast"], 8.5, (55, 80), viv, "Velika casa, 16-18 C",
          "Allegrini: elegantniji, koncentrirani Amarone. Suho voće i kakao uz punu cigaru.",
          "Allegrini: a more elegant, concentrated Amarone. Dried fruit and cocoa with a full cigar."),
        W("wine-masi-campofiorin", "Masi Campofiorin", "red-medium", "Veneto, Italija", 13.5, 3, 2,
          ["tamno-voce", "zacini", "voce"], 7.5, (12, 20), viv, "Casa, 15-17 C",
          "Campofiorin: ripasso-stil Masi; trešnja i začini. Lakši ulaz u Valpolicellu uz blagu cigaru.",
          "Campofiorin: Masi's ripasso style; cherry and spice. An easier Valpolicella entry with a mild cigar."),
        W("wine-cesari-ripasso", "Cesari Mara Valpolicella Ripasso", "red-medium", "Veneto, Italija", 13.5, 3, 2,
          ["tamno-voce", "suho-voce", "zacini"], 7.5, (14, 22), v, "Casa, 15-17 C",
          "Cesari Mara: popularni ripasso; suha trešnja i blaga slatkoća. Svakodnevni pairing.",
          "Cesari Mara: popular ripasso; dried cherry and gentle sweetness. An everyday pairing."),
        W("wine-fontanafredda-barolo", "Fontanafredda Barolo", "red-full", "Piemont, Italija", 14, 4, 1,
          ["cvjetno", "tamno-voce", "koza", "zemljano"], 8.5, (35, 55), viv, "Velika casa, 16-18 C",
          "Fontanafredda: klasični Barolo; ruža, katran, višnja. Tannini uz strukturiranu cigaru.",
          "Fontanafredda: classic Barolo; rose, tar, cherry. Tannins with a structured cigar."),
        W("wine-pio-cesare-barolo", "Pio Cesare Barolo", "red-full", "Piemont, Italija", 14, 4, 1,
          ["cvjetno", "tamno-voce", "koza", "hrast"], 8.5, (45, 70), viv, "Velika casa, 16-18 C",
          "Pio Cesare: tradicionalni, snažni Barolo. Koža i crveno voće uz Habano.",
          "Pio Cesare: traditional, powerful Barolo. Leather and red fruit with Habano."),
        W("wine-banfi-brunello", "Castello Banfi Brunello di Montalcino", "red-full", "Toskana, Italija", 14, 4, 1,
          ["tamno-voce", "koza", "zemljano", "hrast"], 8.0, (40, 65), viv, "Velika casa, 16-18 C",
          "Banfi Brunello: široko dostupan, zreo sangiovese. Višnja i hrast uz srednje-punu cigaru.",
          "Banfi Brunello: widely available, ripe Sangiovese. Cherry and oak with a medium-full cigar."),
        W("wine-casanova-di-neri-brunello", "Casanova di Neri Brunello di Montalcino", "red-full", "Toskana, Italija", 14.5, 4, 1,
          ["tamno-voce", "hrast", "koza", "zacini"], 8.5, (55, 90), v, "Velika casa, 16-18 C",
          "Casanova di Neri: moderniji, koncentrirani Brunello. Snaga i elegancija uz maduro.",
          "Casanova di Neri: a more modern, concentrated Brunello. Power and elegance with maduro."),
        W("wine-faustino-i-gr", "Faustino I Gran Reserva", "red-full", "Rioja, Španjolska", 13.5, 4, 1,
          ["orasasti", "suho-voce", "vanilija", "tamno-voce"], 8.0, (22, 35), viv, "Velika casa, 16-18 C",
          "Faustino I GR: klasik Rioje; vanilija, suha trešnja, orasi. Prijateljski uz Connecticut do Habano.",
          "Faustino I GR: Rioja classic; vanilla, dried cherry, nuts. Friendly from Connecticut to Habano."),
        W("wine-muga-gran-reserva", "Muga Gran Reserva", "red-full", "Rioja, Španjolska", 14, 4, 1,
          ["tamno-voce", "hrast", "orasasti", "zacini"], 8.5, (40, 60), viv, "Velika casa, 16-18 C",
          "Muga GR: ozbiljnija Rioja; hrast, crno voće, začini. Bolje uz puniju cigaru.",
          "Muga GR: a more serious Rioja; oak, black fruit, spice. Better with a fuller cigar."),
        W("wine-pesquera-ribera", "Tinto Pesquera Crianza", "red-full", "Ribera del Duero, Španjolska", 14, 4, 1,
          ["tamno-voce", "hrast", "zacini"], 8.0, (25, 40), viv, "Velika casa, 16-18 C",
          "Pesquera: Tempranillo s Ribere; crna trešnja i hrast. Pouzdan uz Habano.",
          "Pesquera: Ribera Tempranillo; black cherry and oak. Reliable with Habano."),
        W("wine-alvaro-palacios-terrasses", "Álvaro Palacios Les Terrasses", "red-full", "Priorat, Španjolska", 14.5, 5, 1,
          ["tamno-voce", "mineralno", "zacini", "hrast"], 8.5, (30, 45), v, "Velika casa, 16-18 C",
          "Les Terrasses: pristupačni Priorat; škriljevac, crno voće, alkoholna snaga. Uz maduro.",
          "Les Terrasses: approachable Priorat; slate, black fruit, alcoholic power. With maduro."),
        W("wine-emilio-moro", "Emilio Moro Ribera del Duero", "red-full", "Ribera del Duero, Španjolska", 14.5, 4, 1,
          ["tamno-voce", "hrast", "zacini"], 8.0, (22, 35), viv, "Velika casa, 16-18 C",
          "Emilio Moro: zreo Ribera stil; voće i bačva. Svakodnevni španjolski pairing.",
          "Emilio Moro: ripe Ribera style; fruit and barrel. An everyday Spanish pairing."),
        W("wine-beaucastel-cdp", "Château de Beaucastel Châteauneuf-du-Pape", "red-full", "Rhone, Francuska", 14.5, 4, 1,
          ["tamno-voce", "zacini", "zemljano", "koza"], 8.5, (55, 90), viv, "Velika casa, 16-18 C",
          "Beaucastel: garrigue, crno voće, 13 sorti. Referentni CdP uz Habano.",
          "Beaucastel: garrigue, black fruit, 13 varieties. Benchmark CdP with Habano."),
        W("wine-vieux-telegraphe-cdp", "Vieux Télégraphe Châteauneuf-du-Pape", "red-full", "Rhone, Francuska", 14.5, 4, 1,
          ["tamno-voce", "zacini", "zemljano", "mineralno"], 8.5, (50, 85), v, "Velika casa, 16-18 C",
          "Vieux Télégraphe: kamenito, začinsko CdP s La Crau. Elegancija uz punu cigaru.",
          "Vieux Télégraphe: stony, spicy CdP from La Crau. Elegance with a full cigar."),
        W("wine-guigal-cotes-du-rhone", "E. Guigal Côtes du Rhône", "red-full", "Rhone, Francuska", 14, 3, 1,
          ["tamno-voce", "zacini", "papar"], 7.5, (10, 16), hr, "Casa, 15-17 C",
          "Guigal CdR: Syrah/Grenache pristupačnost; papar i crveno voće. Ulaz u Rhône uz cigaru.",
          "Guigal CdR: approachable Syrah/Grenache; pepper and red fruit. A Rhône entry with a cigar."),
        W("wine-guigal-gigondas", "E. Guigal Gigondas", "red-full", "Rhone, Francuska", 14.5, 4, 1,
          ["tamno-voce", "zacini", "zemljano"], 8.0, (20, 32), viv, "Velika casa, 16-18 C",
          "Guigal Gigondas: puniji južni Rhône; garrigue i crno voće. Blizu CdP-a uz manju cijenu.",
          "Guigal Gigondas: fuller southern Rhône; garrigue and black fruit. Near CdP at a lower price."),
        W("wine-gaja-barbaresco", "Gaja Barbaresco", "red-full", "Piemont, Italija", 14, 4, 1,
          ["cvjetno", "tamno-voce", "koza", "mineralno"], 9.0, (120, 220), v, "Velika casa, 16-18 C",
          "Gaja Barbaresco: ikona Piemonta; elegancija i snaga. Posebna prilika uz fine Habano.",
          "Gaja Barbaresco: a Piedmont icon; elegance and power. A special occasion with fine Habano."),
        W("wine-ornellaia", "Ornellaia Bolgheri Superiore", "red-full", "Toskana, Italija", 14.5, 5, 1,
          ["tamno-voce", "hrast", "zacini", "kakao"], 9.0, (150, 250), v, "Velika casa, 16-18 C",
          "Ornellaia: Bordeaux blend s toskanske obale. Koncentracija uz vrhunski maduro.",
          "Ornellaia: Bordeaux blend from the Tuscan coast. Concentration with a top maduro."),
        # --- Novi svijet ---
        W("wine-catena-malbec", "Catena Malbec", "red-full", "Mendoza, Argentina", 14, 4, 2,
          ["tamno-voce", "zacini", "vanilija"], 7.5, (12, 20), hr, "Velika casa, 16-18 C",
          "Catena: referentni Mendoza Malbec; šljiva i začini. Prijateljski uz srednju cigaru.",
          "Catena: benchmark Mendoza Malbec; plum and spice. Friendly with a medium cigar."),
        W("wine-norton-reserva-malbec", "Norton Reserva Malbec", "red-full", "Mendoza, Argentina", 14, 4, 2,
          ["tamno-voce", "hrast", "vanilija"], 7.5, (10, 18), hr, "Velika casa, 16-18 C",
          "Norton Reserva: bačveniji Malbec; vanilija i crno voće. Value pairing.",
          "Norton Reserva: more barrel-led Malbec; vanilla and black fruit. Value pairing."),
        W("wine-penfolds-bin-28", "Penfolds Bin 28 Kalimna Shiraz", "red-full", "Barossa, Australija", 14.5, 5, 2,
          ["tamno-voce", "zacini", "hrast", "kakao"], 8.0, (25, 40), viv, "Velika casa, 16-18 C",
          "Bin 28: klasični Barossa Shiraz; džem, papar, hrast. Snaga uz maduro.",
          "Bin 28: classic Barossa Shiraz; jam, pepper, oak. Power with maduro."),
        W("wine-penfolds-bin-389", "Penfolds Bin 389 Cabernet Shiraz", "red-full", "Južna Australija", 14.5, 5, 1,
          ["tamno-voce", "hrast", "zacini", "kakao"], 8.5, (45, 70), viv, "Velika casa, 16-18 C",
          "Bin 389 (Baby Grange): Cabernet struktura + Shiraz meso. Ozbiljan NS pairing.",
          "Bin 389 (Baby Grange): Cabernet structure plus Shiraz flesh. A serious New World pairing."),
        W("wine-ridge-lytton-springs", "Ridge Lytton Springs", "red-full", "California, SAD", 14.5, 4, 2,
          ["tamno-voce", "zacini", "orasasti"], 8.5, (45, 70), v, "Velika casa, 16-18 C",
          "Ridge Lytton: Zinfandel field blend; bobičasto voće i začini. Referenca uz maduro.",
          "Ridge Lytton: Zinfandel field blend; berry fruit and spice. A benchmark with maduro."),
        W("wine-seghesio-zin", "Seghesio Sonoma Zinfandel", "red-full", "California, SAD", 15, 4, 2,
          ["tamno-voce", "zacini", "papar"], 7.5, (18, 28), viv, "Velika casa, 16-18 C",
          "Seghesio: pristupačni Sonoma Zin; papar i džem. Lakši CA stil uz cigaru.",
          "Seghesio: approachable Sonoma Zin; pepper and jam. An easier CA style with a cigar."),
        W("wine-don-melchor", "Concha y Toro Don Melchor", "red-full", "Maipo, Čile", 14.5, 5, 1,
          ["tamno-voce", "hrast", "zacini", "cedar"], 8.5, (70, 110), v, "Velika casa, 16-18 C",
          "Don Melchor: vodeći čileanski Cabernet; cedar i crno voće. Icon uz punu cigaru.",
          "Don Melchor: leading Chilean Cabernet; cedar and black fruit. An icon with a full cigar."),
        W("wine-korak-cabernet", "Korak Cabernet Sauvignon", "red-full", "Plešivica, Hrvatska", 13.5, 4, 1,
          ["tamno-voce", "hrast", "zacini"], 7.5, (18, 30), viv, "Velika casa, 16-18 C",
          "Korak: kontinentalni HR Cabernet; struktura i crveno voće. Domaci flagship.",
          "Korak: continental Croatian Cabernet; structure and red fruit. A domestic flagship."),
        W("wine-lynch-bages", "Château Lynch-Bages", "red-full", "Bordeaux, Francuska", 13.5, 4, 1,
          ["tamno-voce", "cedar", "hrast", "zacini"], 8.5, (90, 160), v, "Velika casa, 16-18 C",
          "Lynch-Bages (Pauillac): cedar, crni ribiz, grafit. Klasični Bordeaux uz Habano.",
          "Lynch-Bages (Pauillac): cedar, blackcurrant, graphite. Classic Bordeaux with Habano."),
        W("wine-caymus-cabernet", "Caymus Cabernet Sauvignon", "red-full", "Napa Valley, SAD", 14.5, 5, 2,
          ["tamno-voce", "vanilija", "kakao", "hrast"], 8.0, (60, 95), v, "Velika casa, 16-18 C",
          "Caymus: bogati Napa Cab; vanilija i crno voće. Američki stil uz maduro.",
          "Caymus: rich Napa Cab; vanilla and black fruit. American style with maduro."),
        # --- Srednje / bijelo (tanko) ---
        W("wine-antinori-pepploi", "Antinori Peppoli Chianti Classico", "red-medium", "Toskana, Italija", 13.5, 3, 1,
          ["tamno-voce", "voce", "zacini"], 7.5, (14, 22), viv, "Casa, 15-17 C",
          "Peppoli: pristupačni Chianti Classico; trešnja i začini. Uz blagu do srednju cigaru.",
          "Peppoli: approachable Chianti Classico; cherry and spice. With a mild-to-medium cigar."),
        W("wine-castello-di-ama-chianti", "Castello di Ama Chianti Classico", "red-medium", "Toskana, Italija", 13.5, 3, 1,
          ["tamno-voce", "cvjetno", "mineralno"], 8.0, (28, 45), v, "Casa, 15-17 C",
          "Castello di Ama: finiji Chianti; cvijet i mineralnost. Elegantniji pairing.",
          "Castello di Ama: finer Chianti; flower and minerality. A more elegant pairing."),
        W("wine-louis-jadot-pinot", "Louis Jadot Bourgogne Pinot Noir", "red-medium", "Burgundija, Francuska", 13, 2, 1,
          ["voce", "zemljano", "cvjetno"], 7.5, (18, 28), viv, "Casa, 14-16 C",
          "Jadot regionalni Pinot: crvena trešnja i zemlja. Samo uz blagu Connecticut cigaru.",
          "Jadot regional Pinot: red cherry and earth. Only with a mild Connecticut cigar."),
        W("wine-benvenuti-pinot", "Benvenuti Pinot Noir", "red-medium", "Istra, Hrvatska", 13, 2, 1,
          ["voce", "cvjetno", "mineralno"], 7.5, (16, 26), viv, "Casa, 14-16 C",
          "Benvenuti: istarski Pinot; svježe voće i mineralnost. Lagani HR pairing.",
          "Benvenuti: Istrian Pinot; fresh fruit and minerality. A light HR pairing."),
        W("wine-kozlovic-merlot", "Kozlović Merlot", "red-medium", "Istra, Hrvatska", 13.5, 3, 1,
          ["voce", "tamno-voce", "hrast"], 7.0, (12, 20), hr, "Casa, 15-17 C",
          "Kozlović Merlot: meko voće i blagi hrast. Svakodnevni istarski crveni.",
          "Kozlović Merlot: soft fruit and gentle oak. An everyday Istrian red."),
        W("wine-roxanich-merlot", "Roxanich Merlot", "red-medium", "Istra, Hrvatska", 13.5, 3, 1,
          ["tamno-voce", "zemljano", "orasasti"], 7.5, (25, 40), viv, "Casa, 15-17 C",
          "Roxanich: duži maceration stil; kompleksniji Merlot. Uz srednju cigaru.",
          "Roxanich: longer-maceration style; a more complex Merlot. With a medium cigar."),
        W("wine-krauthaker-frankovka", "Krauthaker Frankovka", "red-medium", "Slavonija, Hrvatska", 13, 3, 1,
          ["voce", "zacini", "papar"], 7.0, (8, 14), hr, "Casa, 15-17 C",
          "Krauthaker Frankovka: papar i crveno voće. Lagani kontinentalni pairing.",
          "Krauthaker Frankovka: pepper and red fruit. A light continental pairing."),
        W("wine-belje-frankovka", "Belje Frankovka", "red-medium", "Baranja, Hrvatska", 12.5, 3, 1,
          ["voce", "zacini"], 6.5, (6, 12), hr, "Casa, 15-17 C",
          "Belje: široko dostupna frankovka; svježe voće. Ulazni HR crveni.",
          "Belje: widely available Frankovka; fresh fruit. An entry-level HR red."),
        W("wine-krauthaker-grasevina", "Krauthaker Graševina", "white-fresh", "Slavonija, Hrvatska", 12.5, 2, 1,
          ["jabuka", "citrus", "mineralno"], 7.5, (8, 14), hr, "Dobro ohladjeno, 6-8 C",
          "Krauthaker: standard HR bijelog; jabuka i citrus. Samo uz najblažu cigaru.",
          "Krauthaker: HR white standard; apple and citrus. Only with the mildest cigar."),
        W("wine-enjingi-grasevina", "Enjingi Graševina", "white-fresh", "Slavonija, Hrvatska", 12.5, 2, 1,
          ["jabuka", "citrus", "med"], 7.5, (9, 16), hr, "Dobro ohladjeno, 6-8 C",
          "Enjingi: malo bogatija graševina; med i jabuka. Kontrast uz Connecticut.",
          "Enjingi: a slightly richer Graševina; honey and apple. Contrast with Connecticut."),
        W("wine-stina-posip", "Stina Pošip", "white-rich", "Brač, Hrvatska", 13, 3, 1,
          ["citrus", "mineralno", "orasasti"], 8.0, (14, 24), viv, "Ohladjeno, 8-10 C",
          "Stina Pošip: mineralan, mediteranski bijeli. Uz blagu cigaru ili aperitiv.",
          "Stina Pošip: mineral Mediterranean white. With a mild cigar or as an aperitif."),
        W("wine-krajancic-posip", "Krajančić Pošip", "white-rich", "Korčula, Hrvatska", 13.5, 3, 1,
          ["citrus", "orasasti", "mineralno"], 8.0, (16, 28), viv, "Ohladjeno, 8-10 C",
          "Krajančić: referentni korčulanski pošip; orasi i citrus. Ozbiljniji bijeli pairing.",
          "Krajančić: benchmark Korčula Pošip; nuts and citrus. A more serious white pairing."),
        W("wine-kozlovic-malvazija", "Kozlović Malvazija", "white-fresh", "Istra, Hrvatska", 13, 2, 1,
          ["voce", "citrus", "cvjetno"], 7.5, (10, 18), hr, "Dobro ohladjeno, 6-8 C",
          "Kozlović: istarska klasika; breskva i bagrem. Svježina uz blagu cigaru.",
          "Kozlović: Istrian classic; peach and acacia. Freshness with a mild cigar."),
        W("wine-matosevic-malvazija", "Matošević Malvazija", "white-fresh", "Istra, Hrvatska", 13, 2, 1,
          ["voce", "mineralno", "citrus"], 7.5, (12, 20), viv, "Dobro ohladjeno, 6-8 C",
          "Matošević: mineralnija malvazija; citrus i kamen. Elegantan HR bijeli.",
          "Matošević: a more mineral Malvasia; citrus and stone. An elegant HR white."),
        W("wine-korak-chardonnay", "Korak Chardonnay", "white-rich", "Plešivica, Hrvatska", 13.5, 3, 1,
          ["orasasti", "vanilija", "citrus"], 7.5, (16, 28), viv, "Ohladjeno, 10-12 C",
          "Korak barrique Chardonnay: maslac i citrus. Bogatiji bijeli uz Connecticut.",
          "Korak barrel Chardonnay: butter and citrus. A richer white with Connecticut."),
        W("wine-louis-latour-chardonnay", "Louis Latour Pouilly-Fuissé", "white-rich", "Burgundija, Francuska", 13.5, 3, 1,
          ["orasasti", "citrus", "mineralno"], 8.0, (25, 40), viv, "Ohladjeno, 10-12 C",
          "Latour Pouilly-Fuissé: klasični bijeli Burgundac; orasi i mineralnost.",
          "Latour Pouilly-Fuissé: classic white Burgundy; nuts and minerality."),
        W("wine-dr-loosen-kabinett", "Dr. Loosen Riesling Kabinett", "white-fresh", "Mosel, Njemačka", 8.5, 2, 3,
          ["citrus", "jabuka", "mineralno", "med"], 8.0, (12, 20), viv, "Dobro ohladjeno, 6-8 C",
          "Dr. Loosen Kabinett: limeta, jabuka, škriljevac, nježna slatkoća. Uz najblažu cigaru.",
          "Dr. Loosen Kabinett: lime, apple, slate, gentle sweetness. With the mildest cigar."),
        W("wine-jj-prum-kabinett", "J.J. Prüm Riesling Kabinett", "white-fresh", "Mosel, Njemačka", 9, 2, 3,
          ["citrus", "mineralno", "cvjetno", "med"], 8.5, (22, 35), v, "Dobro ohladjeno, 6-8 C",
          "J.J. Prüm: ikona Mosela; precizan, cvjetan, mineralan. Rijedak bijeli uz cigaru.",
          "J.J. Prüm: a Mosel icon; precise, floral, mineral. A rare white with a cigar."),
        # --- Pjenušavo ---
        W("wine-moet-brut-imperial", "Moët & Chandon Brut Impérial", "sparkling", "Champagne, Francuska", 12, 2, 1,
          ["citrus", "kremasto", "orasasti"], 7.5, (40, 55), "Siroka dostupnost", "Dobro ohladjeno, 6-8 C",
          "Moët Brut Impérial: brioche i citrus; široko dostupan. Tradicija uz blagu dnevnu cigaru.",
          "Moët Brut Impérial: brioche and citrus; widely available. Tradition with a mild daytime cigar."),
        W("wine-veuve-clicquot-yellow", "Veuve Clicquot Yellow Label Brut", "sparkling", "Champagne, Francuska", 12, 2, 1,
          ["citrus", "kremasto", "voce"], 8.0, (45, 60), "Siroka dostupnost", "Dobro ohladjeno, 6-8 C",
          "Veuve Yellow Label: malo puniji brut; voće i tost. Kontrast uz Connecticut.",
          "Veuve Yellow Label: a slightly fuller brut; fruit and toast. Contrast with Connecticut."),
        W("wine-bollinger-special-cuvee", "Bollinger Special Cuvée", "sparkling", "Champagne, Francuska", 12, 3, 1,
          ["orasasti", "kremasto", "citrus", "hrast"], 8.5, (55, 75), viv, "Dobro ohladjeno, 6-8 C",
          "Bollinger: pinot-teži, orašasti Champagne. Ozbiljniji pjenušac uz blagu do srednju cigaru.",
          "Bollinger: Pinot-led, nutty Champagne. A more serious sparkler with a mild-to-medium cigar."),
        W("wine-pol-roger-brut", "Pol Roger Brut Réserve", "sparkling", "Champagne, Francuska", 12, 2, 1,
          ["citrus", "kremasto", "mineralno"], 8.5, (50, 70), viv, "Dobro ohladjeno, 6-8 C",
          "Pol Roger: elegantan, fin mousse; citrus i biskvit. Churchillova kuća uz blagu cigaru.",
          "Pol Roger: elegant, fine mousse; citrus and biscuit. Churchill's house with a mild cigar."),
        W("wine-valdo-prosecco-docg", "Valdo Valdobbiadene Prosecco Superiore DOCG", "sparkling", "Veneto, Italija", 11, 1, 2,
          ["voce", "cvjetno", "citrus"], 7.0, (10, 16), hr, "Dobro ohladjeno, 6-8 C",
          "Valdo DOCG: jabuka i cvijet; lagani prosecco. Samo uz najblažu cigaru.",
          "Valdo DOCG: apple and flower; light Prosecco. Only with the mildest cigar."),
        W("wine-villa-sandi-prosecco", "Villa Sandi Valdobbiadene Prosecco Superiore", "sparkling", "Veneto, Italija", 11, 1, 2,
          ["voce", "citrus", "cvjetno"], 7.5, (12, 18), viv, "Dobro ohladjeno, 6-8 C",
          "Villa Sandi: čist DOCG stil; kruška i citrus. Aperitiv uz Connecticut.",
          "Villa Sandi: clean DOCG style; pear and citrus. Aperitif with Connecticut."),
        W("wine-villa-sandi-cartizze", "Villa Sandi Cartizze", "sparkling", "Veneto, Italija", 11.5, 2, 2,
          ["voce", "kremasto", "cvjetno"], 8.5, (28, 40), viv, "Dobro ohladjeno, 6-8 C",
          "Villa Sandi Cartizze: vrh prosecco piramide; kremast, cvjetan. Ozbiljniji mousse uz blagu cigaru.",
          "Villa Sandi Cartizze: top of the Prosecco pyramid; creamy, floral. A more serious mousse with a mild cigar."),
        W("wine-bisol-cartizze", "Bisol Cartizze", "sparkling", "Veneto, Italija", 11.5, 2, 2,
          ["voce", "med", "cvjetno"], 8.5, (30, 45), v, "Dobro ohladjeno, 6-8 C",
          "Bisol Cartizze: referentni Cartizze; med i bijelo cvijeće. Premium prosecco pairing.",
          "Bisol Cartizze: benchmark Cartizze; honey and white flowers. A premium Prosecco pairing."),
        W("wine-bisol-crede", "Bisol Crede Valdobbiadene DOCG", "sparkling", "Veneto, Italija", 11.5, 1, 2,
          ["voce", "citrus", "mineralno"], 8.0, (14, 22), viv, "Dobro ohladjeno, 6-8 C",
          "Bisol Crede: suši, mineralniji prosecco. Bolji omjer cijene i ozbiljnosti.",
          "Bisol Crede: a drier, more mineral Prosecco. Better value-to-seriousness ratio."),
        W("wine-juve-y-camps-reserva", "Juvé y Camps Reserva de la Familia Brut Nature", "sparkling", "Penedes, Španjolska", 12, 2, 1,
          ["orasasti", "citrus", "kremasto"], 7.5, (12, 20), viv, "Dobro ohladjeno, 6-8 C",
          "Juvé y Camps Brut Nature: bez dozaže; orasi i citrus. Cava vrijednost uz blagu cigaru.",
          "Juvé y Camps Brut Nature: no dosage; nuts and citrus. Cava value with a mild cigar."),
        W("wine-gramona-imperial", "Gramona Imperial Brut", "sparkling", "Penedes, Španjolska", 12, 2, 1,
          ["orasasti", "kremasto", "mineralno"], 8.5, (25, 40), v, "Dobro ohladjeno, 6-8 C",
          "Gramona Imperial: dugo odležavanje; brioche i orasi. Najbolja Cava kuća uz cigaru.",
          "Gramona Imperial: long ageing; brioche and nuts. The best Cava house with a cigar."),
        W("wine-tomac-klasik", "Tomac Klasik", "sparkling", "Plešivica, Hrvatska", 12, 2, 1,
          ["citrus", "mineralno", "kremasto"], 8.0, (18, 28), viv, "Dobro ohladjeno, 6-8 C",
          "Tomac Klasik: plešivička klasična metoda; citrus i kvasac. HR referentni pjenušac.",
          "Tomac Klasik: Plešivica classic method; citrus and yeast. Benchmark Croatian sparkling."),
        W("wine-tomac-amfora", "Tomac Amfora", "sparkling", "Plešivica, Hrvatska", 12, 2, 1,
          ["orasasti", "mineralno", "citrus"], 8.5, (28, 42), viv, "Dobro ohladjeno, 6-8 C",
          "Tomac Amfora: fermentacija u amforama; kompleksniji, orašasti. Svjetska razina uz blagu cigaru.",
          "Tomac Amfora: amphora fermentation; more complex, nutty. World-class with a mild cigar."),
        W("wine-misal-brut", "Misal Peršurić Brut", "sparkling", "Istra, Hrvatska", 12, 2, 1,
          ["citrus", "voce", "mineralno"], 7.5, (15, 24), viv, "Dobro ohladjeno, 6-8 C",
          "Misal Brut: prvi HR klasični metoda (Višnjan); svjež citrus. Ulaz u HR pjenušce.",
          "Misal Brut: first Croatian classic method (Višnjan); fresh citrus. Entry to HR sparkling."),
        W("wine-misal-prestige", "Misal Peršurić Prestige", "sparkling", "Istra, Hrvatska", 12, 2, 1,
          ["kremasto", "orasasti", "citrus"], 8.0, (25, 38), viv, "Dobro ohladjeno, 6-8 C",
          "Misal Prestige: duže na kvascima; kremastiji. Bolji HR pairing uz Connecticut.",
          "Misal Prestige: longer on lees; creamier. A better HR pairing with Connecticut."),
        W("wine-sember-brut", "Šember Brut", "sparkling", "Plešivica, Hrvatska", 12, 2, 1,
          ["citrus", "mineralno", "cvjetno"], 8.0, (16, 26), viv, "Dobro ohladjeno, 6-8 C",
          "Šember: još jedan plešivički klasik; precizan i mineralan. Alternativa Tomacu.",
          "Šember: another Plešivica classic; precise and mineral. An alternative to Tomac."),
        # --- Extra pairing-first fills (do ~120+) ---
        W("wine-fonseca-tawny-20", "Fonseca 20 Y.O. Tawny Port", "port-tawny", "Douro, Portugal", 20, 4, 4,
          ["orasasti", "karamela", "suho-voce", "med"], 8.5, (55, 75), viv, "Casa za porto, 14-16 C",
          "Fonseca 20 YO: bogat tawny; orasi, karamela, suhe smokve. Rival Graham's uz maduro.",
          "Fonseca 20 YO: rich tawny; nuts, caramel, dried figs. A rival to Graham's with maduro.",
          additive="fortified"),
        W("wine-grahams-lbv", "Graham's Late Bottled Vintage", "port-ruby", "Douro, Portugal", 20, 4, 4,
          ["tamno-voce", "kakao", "zacini"], 7.5, (18, 28), viv, "Casa za porto, 14-16 C",
          "Graham's LBV: voćniji, slađi LBV stil. Lakši ulaz u ruby porto uz cigaru.",
          "Graham's LBV: fruitier, sweeter LBV style. An easier entry to ruby port with a cigar.",
          additive="fortified"),
        W("wine-niepoort-ruby", "Niepoort Ruby Dum", "port-ruby", "Douro, Portugal", 19.5, 4, 4,
          ["tamno-voce", "voce", "zacini"], 7.5, (14, 22), v, "Casa za porto, 14-16 C",
          "Niepoort Ruby Dum: moderniji, voćni ruby. Svježiji porto profil uz srednju cigaru.",
          "Niepoort Ruby Dum: a more modern, fruity ruby. Fresher port profile with a medium cigar.",
          additive="fortified"),
        W("wine-lustau-east-india", "Lustau East India Solera", "sherry-sweet", "Jerez, Španjolska", 20, 4, 4,
          ["orasasti", "suho-voce", "karamela", "med"], 8.0, (18, 28), viv, "Casa za sherry, 14-16 C",
          "East India Solera: cream/oloroso stil; orasi i suho voće. Odličan uz Connecticut do maduro.",
          "East India Solera: cream/oloroso style; nuts and dried fruit. Excellent from Connecticut to maduro.",
          additive="fortified", source="Standard kategorije sherry"),
        W("wine-capcanes-priorat", "Celler de Capçanes Mas Donis Priorat", "red-full", "Priorat, Španjolska", 14.5, 4, 1,
          ["tamno-voce", "mineralno", "zacini"], 7.5, (14, 22), viv, "Velika casa, 16-18 C",
          "Mas Donis: pristupačni Priorat; škriljevac i crno voće. Value uz Habano.",
          "Mas Donis: approachable Priorat; slate and black fruit. Value with Habano."),
        W("wine-masi-brolo", "Masi Brolo di Campofiorin", "red-full", "Veneto, Italija", 14, 4, 2,
          ["suho-voce", "tamno-voce", "zacini"], 8.0, (22, 35), viv, "Velika casa, 16-18 C",
          "Brolo: premium Campofiorin linija; suha trešnja i začini. Most prema Amaroneu.",
          "Brolo: premium Campofiorin line; dried cherry and spice. A bridge toward Amarone."),
        W("wine-antinori-tignanello", "Antinori Tignanello", "red-full", "Toskana, Italija", 14, 4, 1,
          ["tamno-voce", "hrast", "zacini", "koza"], 8.5, (80, 130), v, "Velika casa, 16-18 C",
          "Tignanello: ikona Super Toscane; Sangiovese + Cabernet. Elegancija uz punu cigaru.",
          "Tignanello: Super Tuscan icon; Sangiovese plus Cabernet. Elegance with a full cigar."),
        W("wine-berlucchi-61", "Berlucchi '61 Franciacorta Brut", "sparkling", "Lombardija, Italija", 12.5, 2, 1,
          ["citrus", "kremasto", "orasasti"], 8.0, (22, 32), viv, "Dobro ohladjeno, 6-8 C",
          "Berlucchi '61: pionir Franciacorte; citrus i brioche. Alternativa Ca' del Boscu.",
          "Berlucchi '61: Franciacorta pioneer; citrus and brioche. An alternative to Ca' del Bosco."),
        W("wine-taittinger-brut", "Taittinger Brut Réserve", "sparkling", "Champagne, Francuska", 12, 2, 1,
          ["cvjetno", "citrus", "kremasto"], 8.0, (45, 60), viv, "Dobro ohladjeno, 6-8 C",
          "Taittinger: chardonnay-teži, cvjetni Champagne. Elegantan uz blagu cigaru.",
          "Taittinger: Chardonnay-led, floral Champagne. Elegant with a mild cigar."),
        W("wine-plenkovic-zlatan", "Zlatan Plenković Grand Cru Plavac", "red-full", "Hvar, Hrvatska", 14.5, 5, 2,
          ["tamno-voce", "suho-voce", "zacini", "hrast"], 8.0, (30, 50), viv, "Velika casa, 16-18 C",
          "Zlatan Grand Cru: vrhunski hvarski plavac; koncentracija i začini. Uz Habano/maduro.",
          "Zlatan Grand Cru: top Hvar Plavac; concentration and spice. With Habano/maduro."),
    ]


def build(old: list[dict]) -> list[dict]:
    by_id = {w["id"]: w for w in old}
    out: list[dict] = []

    for wid in sorted(KEEP_IDS):
        if wid not in by_id:
            raise SystemExit(f"Missing keep id: {wid}")
        w = deepcopy(by_id[wid])
        if wid in RENAMES:
            w["name"] = RENAMES[wid]
        # Ukloni em dash iz notes ako postoji (stil projekta)
        for lang in ("hr", "en"):
            if isinstance(w.get("notes"), dict) and lang in w["notes"]:
                w["notes"][lang] = w["notes"][lang].replace("\u2014", ",").replace("—", ",")
        out.append(w)

    out.extend(new_entries())

    ids = [w["id"] for w in out]
    if len(ids) != len(set(ids)):
        from collections import Counter
        dup = [i for i, c in Counter(ids).items() if c > 1]
        raise SystemExit(f"Duplicate ids: {dup}")

    style_order = [
        "port-tawny", "port-ruby", "sherry-dry", "sherry-sweet", "madeira", "prosek",
        "dessert-wine", "red-full", "red-medium", "white-rich", "white-fresh", "sparkling",
    ]
    rank = {s: i for i, s in enumerate(style_order)}
    out.sort(key=lambda w: (rank.get(w["style"], 99), w["name"].lower()))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    old = json.loads(WINES_PATH.read_text(encoding="utf-8"))
    new = build(old)

    removed = sorted(REMOVE_IDS & {w["id"] for w in old})
    kept = sorted(KEEP_IDS)
    print(f"old={len(old)} new={len(new)} kept={len(kept)} removed={len(removed)} added={len(new)-len(kept)}")

    from collections import Counter
    styles = Counter(w["style"] for w in new)
    for s, c in styles.most_common():
        print(f"  {c:3d}  {s}")

    if args.dry_run:
        return

    WINES_PATH.write_text(
        json.dumps(new, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {WINES_PATH}")


if __name__ == "__main__":
    main()
