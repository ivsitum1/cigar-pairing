# -*- coding: utf-8 -*-
"""Shared helpers for gin catalog scrape, Excel build, and JSON export."""
from __future__ import annotations

import re
import unicodedata
from typing import Any

from whisky_shared import (
    catalog_entry_tokens,
    format_price_eur,
    is_bare_category_url,
    numeric_age_tokens,
    parse_price_eur,
    slugify,
)

__all__ = [
    "ALLEZ_LISTS",
    "ECUGA_CATEGORIES",
    "catalog_index",
    "cigar_hint_en_for_style",
    "cigar_hint_for_style",
    "cigar_hint_pair",
    "detect_botanical",
    "detect_style_region",
    "estimate_quality",
    "extract_abv",
    "find_best_catalog_match",
    "format_price_eur",
    "is_gift_sku",
    "is_pairable",
    "is_templated_hint",
    "match_tokens",
    "parse_price_eur",
    "serving_for_style",
    "slugify",
    "token_overlap",
]

GIN_STOP = {
    "the", "of", "and", "vol", "gin", "dry", "london", "giftbox", "gift", "box",
    "poklon", "kutiji", "u", "in", "gb", "limited", "edition", "l", "de", "la",
    "le", "du", "des", "with", "glass", "casa", "bottle",
}

ALLEZ_LISTS = [
    ("https://allez.hr/shop/gin1", "gin"),
]

# ecuga spirits tree — gin usually under spirits-and-liqueurs/gin
ECUGA_CATEGORIES: list[tuple[str, str, str]] = [
    ("gin", "", "Gin"),
]

# pattern, style, region, body, sweetness, botanicalProfile, tags
STYLE_RULES: list[tuple[str, str, str, int, int, str, list[str]]] = [
    # ── Brand-specific rules (most specific first) ──────────────────────────────
    # Monkey 47: 47 botanicals incl. blackberries, lingonberries, spruce (producer)
    (r"monkey\s*47", "contemporary", "Schwarzwald, Njema\u010dka", 3, 1, "botanical", ["borovica", "tamno-voce", "zacini"]),
    # Hendrick's: rose, cucumber, chamomile, elderflower (producer)
    (r"hendrick", "contemporary", "\u0160kotska", 3, 3, "botanical", ["cvjetno", "kamilica", "biljno"]),
    # The Botanist: 22 Islay botanicals (producer)
    (r"botanist", "contemporary", "Islay, \u0160kotska", 3, 2, "botanical", ["biljno", "cvjetno", "citrus"]),
    # Ki No Bi: yuzu, sansho pepper, ginger, green tea (Kyoto Distillery)
    (r"ki\s*no\s*bi|kinobi", "contemporary", "Kyoto, Japan", 3, 2, "botanical", ["citrus", "papar", "biljno"]),
    # Roku: sakura, yuzu, sansho pepper (Suntory)
    (r"\broku\b", "contemporary", "Japan", 3, 2, "botanical", ["cvjetno", "citrus", "papar"]),
    # Nikka Coffey Gin: grain-forward, Japanese citrus (Nikka)
    (r"nikka.*coffey.*gin|nikka.*gin", "contemporary", "Japan", 3, 2, "botanical", ["citrus", "travnato", "kamilica"]),
    # Silent Pool editions
    (r"silent pool.*rose", "contemporary", "World", 3, 3, "botanical", ["cvjetno", "kamilica", "slatko"]),
    (r"silent pool.*rare citrus|silent pool.*citrus", "contemporary", "World", 2, 2, "botanical", ["citrus", "cvjetno", "kamilica"]),
    (r"silent pool", "contemporary", "World", 3, 3, "botanical", ["cvjetno", "kamilica", "med"]),
    # Copperhead editions
    (r"copperhead.*barrel", "contemporary", "World", 4, 2, "botanical", ["zacini", "hrast", "citrus"]),
    (r"copperhead.*black batch", "contemporary", "World", 3, 2, "botanical", ["zacini", "citrus", "biljno"]),
    (r"copperhead.*alchemist", "contemporary", "World", 3, 2, "botanical", ["citrus", "zacini", "biljno"]),
    (r"copperhead", "contemporary", "World", 3, 2, "botanical", ["zacini", "citrus", "korijen"]),
    # Citadelle Reserve: aged (producer)
    (r"citadelle.*reserve", "contemporary", "Francuska", 4, 2, "botanical", ["anis", "hrast", "citrus"]),
    (r"citadelle", "contemporary", "Francuska", 3, 2, "botanical", ["anis", "biljno", "citrus"]),
    # Aviation: lavender, sarsaparilla, rose petal (producer)
    (r"aviation", "contemporary", "SAD", 3, 2, "botanical", ["cvjetno", "biljno", "korijen"]),
    # Elephant Gin editions
    (r"elephant.*orange", "contemporary", "World", 3, 3, "botanical", ["citrus", "kakao", "zacini"]),
    (r"elephant", "contemporary", "World", 3, 2, "botanical", ["biljno", "suho-voce", "zacini"]),
    # Amuerte Coca Leaf editions
    (r"amuerte.*red", "contemporary", "World", 3, 3, "botanical", ["tamno-voce", "biljno", "zacini"]),
    (r"amuerte.*black", "contemporary", "World", 4, 2, "botanical", ["biljno", "zacini", "citrus"]),
    (r"amuerte.*orange", "contemporary", "World", 3, 2, "botanical", ["citrus", "biljno", "cvjetno"]),
    (r"amuerte.*yellow", "contemporary", "World", 2, 2, "botanical", ["citrus", "cvjetno", "biljno"]),
    (r"amuerte.*blue", "contemporary", "World", 3, 2, "botanical", ["biljno", "anis", "citrus"]),
    (r"amuerte.*green", "contemporary", "World", 3, 1, "botanical", ["biljno", "travnato", "citrus"]),
    (r"amuerte.*white", "contemporary", "World", 3, 2, "botanical", ["borovica", "citrus", "biljno"]),
    (r"amuerte", "contemporary", "World", 3, 2, "botanical", ["biljno", "citrus", "zacini"]),
    # Sipsmith editions
    (r"sipsmith.*v\.?j\.?o\.?p|sipsmith.*vjop", "premium-dry", "London, UK", 4, 1, "classic-juniper", ["borovica", "citrus", "zacini"]),
    (r"sipsmith.*zesty|sipsmith.*orange", "london-dry", "Engleska", 3, 2, "classic-juniper", ["citrus", "biljno", "travnato"]),
    (r"sipsmith", "london-dry", "London, UK", 3, 2, "classic-juniper", ["borovica", "citrus", "travnato"]),
    # Gin Mare: olive, rosemary, thyme, basil (producer)
    (r"gin mare", "contemporary", "Mediteran", 3, 2, "mediterranean", ["biljno", "travnato", "zacini"]),
    # Malfy editions
    (r"malfy.*arancia|malfy.*orange", "contemporary", "Mediteran", 2, 2, "mediterranean", ["citrus", "voce", "biljno"]),
    (r"malfy.*limone|malfy.*lemon", "contemporary", "Mediteran", 2, 2, "mediterranean", ["citrus", "biljno", "cvjetno"]),
    (r"malfy", "contemporary", "Mediteran", 3, 2, "mediterranean", ["citrus", "biljno", "travnato"]),
    # Four Pillars: Australian botanicals, Tassie pepperberry (producer)
    (r"four pillars", "contemporary", "Australija", 3, 2, "botanical", ["biljno", "papar", "citrus"]),
    # ── Plymouth (root spice recipe) ──────────────────────────────────────────
    (r"plymouth.*navy", "plymouth", "Plymouth, UK", 4, 1, "classic-juniper", ["borovica", "korijen", "zacini"]),
    (r"plymouth|black friars", "plymouth", "Plymouth, UK", 3, 2, "classic-juniper", ["borovica", "korijen", "biljno"]),
    # ── London Dry & variants ─────────────────────────────────────────────────
    # Beefeater 24: green tea + standard botanicals (producer)
    (r"beefeater.*24", "london-dry", "London, UK", 3, 2, "classic-juniper", ["travnato", "citrus", "cvjetno"]),
    # Beefeater standard: traditional recipe incl. coriander, licorice, angelica
    (r"beefeater", "london-dry", "London, UK", 3, 2, "classic-juniper", ["borovica", "citrus", "zacini"]),
    # Tanqueray No. Ten: grapefruit, lime blossom, chamomile (producer)
    (r"tanqueray\s+no\.?\s*ten|tanqueray\s+n\.?\s*ten|tanqueray.*10", "premium-dry", "London, UK", 3, 2, "classic-juniper", ["citrus", "cvjetno", "travnato"]),
    # Tanqueray standard: classic London dry
    (r"tanqueray", "london-dry", "Engleska", 3, 2, "classic-juniper", ["borovica", "citrus", "travnato"]),
    # No. 3: angelica root, cardamom, coriander (producer)
    (r"no\.?\s*3\b|number\s*three", "london-dry", "Engleska", 3, 2, "classic-juniper", ["borovica", "korijen", "citrus"]),
    # Windspiel editions
    (r"windspiel.*pfeffer|windspiel.*kampot", "premium-dry", "Njema\u010dka", 3, 2, "botanical", ["papar", "biljno", "citrus"]),
    (r"windspiel.*kaffee|windspiel.*caxambu", "premium-dry", "Njema\u010dka", 3, 2, "botanical", ["kava", "zacini", "biljno"]),
    (r"windspiel", "premium-dry", "Njema\u010dka", 3, 2, "classic-juniper", ["borovica", "citrus", "biljno"]),
    # Scapegrace Gold: navy-strength premium NZ dry
    (r"scapegrace.*gold", "premium-dry", "Engleska", 4, 1, "classic-juniper", ["borovica", "citrus", "zacini"]),
    # Akori, Roby Marton: Italian premium dry
    (r"akori", "premium-dry", "Engleska", 3, 2, "classic-juniper", ["biljno", "borovica", "travnato"]),
    (r"roby\s*marton", "premium-dry", "Italija", 3, 2, "classic-juniper", ["biljno", "borovica", "citrus"]),
    # Generic premium-dry fallback
    (r"premium.*dry|dry.*premium", "premium-dry", "Engleska", 3, 2, "classic-juniper", ["borovica", "citrus", "biljno"]),
    # ── Mediterranean ────────────────────────────────────────────────────────
    (r"nordes", "contemporary", "Galicija, \u0160panjolska", 3, 2, "mediterranean", ["biljno", "citrus", "travnato"]),
    (r"nordes|nordés|portofino|mediterranean", "contemporary", "Mediteran", 3, 2, "mediterranean", ["biljno", "citrus", "travnato"]),
    # ── Japanese ──────────────────────────────────────────────────────────────
    (r"roku|ki no bi|kinobi|nikka|etsu|japanese", "contemporary", "Japan", 3, 2, "botanical", ["cvjetno", "citrus", "papar"]),
    # ── Croatian ──────────────────────────────────────────────────────────────
    # Aura Karbun: navy strength, charcoal (producer)
    (r"aura.*karbun", "croatian", "Istra, Hrvatska", 4, 1, "botanical", ["biljno", "borovica", "citrus"]),
    # Old Pilot's Dalmatian: Dalmatian lavender, rosemary (producer)
    (r"old pilot|dalmatian.*gin", "croatian", "Hrvatska", 3, 2, "mediterranean", ["biljno", "cvjetno", "travnato"]),
    (r"aura|maraska|badel|croati|istra|dalma|hrvatsk|dugave|dalmatian|dalmatinski", "croatian", "Hrvatska", 3, 2, "botanical", ["biljno", "citrus", "zacini"]),
    # ── Generic London dry fallback ───────────────────────────────────────────
    (r"london\s*dry|dry gin|bombay|broker|fords|hayman|city of london|gordons|gordon's", "london-dry", "Engleska", 3, 2, "classic-juniper", ["borovica", "citrus", "travnato"]),
    # ── Generic contemporary fallback ─────────────────────────────────────────
    (r"contemporary|g'?vine|the illusionist|bathtub|bobby", "contemporary", "World", 3, 2, "botanical", ["cvjetno", "citrus", "zacini"]),
]

NON_PAIRABLE_RE = re.compile(
    r"sloe|pink|flavou?r|liker|liqueur|rtd|cocktail|premix|watermelon|peach|"
    r"june\b|candy|strawberry|raspberry|passion|mango|coconut|cream",
    re.I,
)

PREMIUM_BRANDS = {
    "monkey 47", "hendrick", "botanist", "gin mare", "sipsmith", "tanqueray",
    "roku", "ki no bi", "citadelle", "copperhead", "silent pool", "no. 3",
    "plymouth", "malfy", "elephant",
}


def match_tokens(name: str) -> set[str]:
    toks = set(
        re.findall(
            r"[a-z0-9]+",
            unicodedata.normalize("NFKD", name.lower()).encode("ascii", "ignore").decode(),
        )
    )
    return {t for t in toks if t not in GIN_STOP and not (t.isdigit() and len(t) <= 2)}


def token_overlap(a: str, b: str) -> int:
    return len(match_tokens(a) & match_tokens(b))


def extract_abv(name: str) -> float | None:
    m = re.search(r"(\d{2}(?:[.,]\d+)?)\s*%\s*(?:Vol|vol)?", name)
    if m:
        return float(m.group(1).replace(",", "."))
    return None


def detect_style_region(name: str, ecuga_category: str = "") -> tuple[str, str, int, int, str, list[str]]:
    text = f"{name} {ecuga_category}"
    for pattern, style, region, body, sweet, botanical, tags in STYLE_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return style, region, body, sweet, botanical, list(tags)
    if re.search(r"london\s*dry|dry gin", text, re.I):
        return "london-dry", "Engleska", 3, 2, "classic-juniper", ["travnato", "citrus", "biljno"]
    return "contemporary", "World", 3, 2, "botanical", ["cvjetno", "citrus", "zacini"]


def detect_botanical(name: str, style: str = "", botanical: str = "") -> str:
    if botanical:
        return botanical
    _, _, _, _, bot, _ = detect_style_region(name)
    return bot


def estimate_quality(
    name: str,
    price: float | None,
    style: str,
    botanical: str,
    abv: float | None,
    seed_score: float | None = None,
) -> float:
    if seed_score is not None:
        return float(seed_score)
    if NON_PAIRABLE_RE.search(name):
        return 3.5
    score = 6.2
    low = name.lower()
    for brand in PREMIUM_BRANDS:
        if brand in low:
            score += 0.9
            break
    if style in ("premium-dry", "plymouth"):
        score += 0.4
    if style == "croatian":
        score += 0.2
    if botanical == "mediterranean":
        score += 0.2
    if price:
        if price >= 55:
            score += 0.8
        elif price >= 40:
            score += 0.5
        elif price >= 28:
            score += 0.3
        elif price < 18:
            score -= 0.5
    if abv and abv >= 45:
        score += 0.2
    return round(min(10.0, max(3.0, score)), 1)


def is_pairable(name: str, style: str, quality: float) -> bool:
    if NON_PAIRABLE_RE.search(name):
        return False
    if quality < 5.5:
        return False
    return True


def serving_for_style(style: str, botanical: str = "") -> dict[str, Any]:
    if style in ("london-dry", "premium-dry", "plymouth"):
        return {
            "neat": 2,
            "tonic": 3,
            "martini": 3,
            "highball": 2,
            "best": "Martini ili G&T",
        }
    if botanical == "mediterranean" or style == "croatian":
        return {
            "neat": 2,
            "tonic": 3,
            "martini": 2,
            "highball": 2,
            "best": "G&T s mediteranskim tonikom",
        }
    return {
        "neat": 3,
        "tonic": 2,
        "martini": 3,
        "highball": 2,
        "best": "Cisti ili martini",
    }


GIFT_RE = re.compile(
    r"poklon|gift\s*box|giftbox|\bkutiji\b|miniset|mini\s*set|tasting\s*set|"
    r"baubles|kiosk\s*set|sa čašom|s čašom|s 2 čaš|with glass|with 2|"
    r"wooden case|drvenoj",
    re.I,
)


def is_gift_sku(name: str) -> bool:
    return bool(GIFT_RE.search(name or ""))


def cigar_hint_for_style(style: str, botanical: str = "") -> str:
    if botanical == "mediterranean":
        return (
            "Biljno-citrusni gin traži Connecticut ili blagu Habano. "
            "Maslina i mediteransko bilje prate kremasti dim, a G&T drži sparivanje svježim."
        )
    if style in ("london-dry", "premium-dry", "plymouth"):
        return (
            "Klasična borovica sjeda uz Connecticut ili blagu Habano. "
            "Martini drži profil koncentriran, a svježina reže kremasti dim bez da cigaru preglasi."
        )
    if style == "croatian":
        return (
            "Lokalni gin traži Connecticut do blage Habano. "
            "Mediteransko bilje i citrus prate zemljasti dim, a G&T ostavlja sparivanje pitkim."
        )
    return (
        "Gusta botanika traži Connecticut ili blagu Habano. "
        "Čist ili martini drži profil, a citrus i začin režu kremasti dim."
    )


def cigar_hint_en_for_style(style: str, botanical: str = "") -> str:
    if botanical == "mediterranean":
        return (
            "A herbal-citrus gin wants a Connecticut or a mild Habano. "
            "Olive and Mediterranean herbs track creamy smoke, and a G&T keeps the match fresh."
        )
    if style in ("london-dry", "premium-dry", "plymouth"):
        return (
            "Classic juniper sits beside a Connecticut or a mild Habano. "
            "A martini keeps the profile concentrated, and the lift cuts creamy smoke without flattening the cigar."
        )
    if style == "croatian":
        return (
            "A local gin wants a Connecticut through to a mild Habano. "
            "Mediterranean herbs and citrus track earthy smoke, and a G&T keeps the match drinkable."
        )
    return (
        "Dense botanicals want a Connecticut or a mild Habano. "
        "Neat or a martini holds the profile, and citrus and spice cut creamy smoke."
    )


def is_templated_hint(hr: str | None) -> bool:
    text = (hr or "").strip()
    if len(text) < 80:
        return True
    return text.startswith((
        "Connecticut / blagi Habano —",
        "Connecticut — klasična borovica",
        "Connecticut do blage Habano —",
    ))


# Most-specific first. HR copy: cigara, finite verbs, sparivanje.
HINT_PAIRS: list[tuple[str, str, str]] = [
    (
        r"monkey\s*47.*kiosk",
        "Mini kiosk set nosi isti Schwarzwald profil u malim bocama; traži blagu Connecticut cigaru. G&T drži botaniku uz laki dim kad martini nije praktičan.",
        "The mini kiosk set carries the same Schwarzwald profile in small bottles; it wants a mild Connecticut cigar. A G&T holds the botanicals beside light smoke when a martini is impractical.",
    ),
    (
        r"monkey\s*47.*barrel",
        "Bačveno zaokruženje daje malo više tijela od standardnog Monkeyja; čist ili martini nosi srednju Habano, a začinska botanika pravi most prema Habano pokrovu.",
        "The barrel rounding gives a touch more body than the standard Monkey; neat or as a martini it carries a medium Habano, and the spiced botanicals bridge to a Habano wrapper.",
    ),
    (
        r"monkey\s*47",
        "Most prema cigari je gusta botanika i borovica; kao martini koncentracija drži blažu do srednju cigaru — Connecticut ili mlađu Habano, gdje svježina reže kremasti dim.",
        "The bridge to a cigar is dense botanicals and juniper; as a martini the concentration holds a mild-to-medium cigar — Connecticut or a younger Habano, where freshness cuts creamy smoke.",
    ),
    (
        r"hendrick",
        "Cvjetni profil (ruža, krastavac) je nježan — most je svježina, ne tijelo; traži blagu Connecticut cigaru, gdje G&T ili martini radi kao osvježenje uz laki dim.",
        "The floral profile (rose, cucumber) is delicate — the bridge is freshness, not body; it wants a mild Connecticut cigar, where a G&T or martini works as a refresher beside light smoke.",
    ),
    (
        r"four pillars",
        "Most prema cigari je citrus i začin; kao martini drži srednju cigaru, a citrusna svježina reže blaži, kremasti dim bez da ga preglasi.",
        "The bridge to a cigar is citrus and spice; as a martini it holds a medium cigar, the citrus lift cutting milder, creamy smoke without overpowering it.",
    ),
    (
        r"botanist",
        "Most prema cigari je zelena, travnata botanika Islaya; traži laganu do srednju cigaru — čist ili martini, gdje biljna svježina osvježava kremasti Connecticut dim.",
        "The bridge to a cigar is Islay's green, herbal botanicals; it wants a mild-to-medium cigar — neat or a martini, where the herbal lift refreshes creamy Connecticut smoke.",
    ),
    (
        r"gin mare.*capri",
        "Capri izdanje nosi maslinu i citrus uz Connecticut ili blagu Habano. G&T s mediteranskim tonikom drži sparivanje svježim, a bilje prati kremasti dim.",
        "The Capri edition carries olive and citrus beside a Connecticut or mild Habano. A G&T with Mediterranean tonic keeps the match fresh, and the herbs track creamy smoke.",
    ),
    (
        r"gin mare.*lantern",
        "Lantern drži isti mediteranski kostur u užoj boci; traži blagu Habano. G&T ostavlja maslinu i ružmarin u prvom planu uz laki, kremasti dim.",
        "Lantern keeps the same Mediterranean frame in a tighter bottle; it wants a mild Habano. A G&T leaves olive and rosemary forward beside light, creamy smoke.",
    ),
    (
        r"gin mare",
        "Maslina, ružmarin i timijan traže Connecticut ili blagu Habano. G&T s mediteranskim tonikom drži sparivanje pitkim, a bilje prati zemljasti dim.",
        "Olive, rosemary and thyme want a Connecticut or a mild Habano. A G&T with Mediterranean tonic keeps the match drinkable, and the herbs track earthy smoke.",
    ),
    (
        r"nikka",
        "Japanski citrus (yuzu, jabuka) je elegantan i lagan; most je citrusna svježina uz blagu Connecticut ili Cameroon cigaru — čist ili martini da profil ostane koncentriran.",
        "The Japanese citrus (yuzu, apple) is elegant and light; the bridge is citrus freshness with a mild Connecticut or Cameroon cigar — neat or a martini to keep the profile concentrated.",
    ),
    (
        r"tanqueray\s+no\.?\s*ten|tanqueray\s+n\.?\s*ten|tanqueray.*10",
        "Citrus-forward London dry — most prema cigari je koriander i citrus; martini klasik drži srednju Habano, gdje začinska botanika sjeda uz Habano pokrov.",
        "A citrus-forward London dry — the bridge to a cigar is coriander and citrus; the classic martini holds a medium Habano, the spiced botanicals settling against a Habano wrapper.",
    ),
    (
        r"tanqueray.*blackcurrant|tanqueray.*royale",
        "Crni ribizl sladi London dry bazu; traži blagu Connecticut cigaru, ne maduro. G&T drži voće pod kontrolom, a borovica i dalje reže kremasti dim.",
        "Blackcurrant sweetens the London dry base; it wants a mild Connecticut cigar, not a maduro. A G&T keeps the fruit in check, and juniper still cuts creamy smoke.",
    ),
    (
        r"tanqueray",
        "Klasični London dry sjeda uz Connecticut; borovica i citrus režu kremasti dim. Martini drži profil suh, a G&T radi kao aperitiv uz kraću cigaru.",
        "A classic London dry sits beside Connecticut; juniper and citrus cut creamy smoke. A martini keeps the profile dry, and a G&T works as an aperitif with a shorter cigar.",
    ),
    (
        r"ki\s*no\s*bi.*sei|kinobi.*sei",
        "Pojačana Kyoto verzija na 54.5% — više tijela od standardnog KI NO BI; nosi srednju cigaru čist ili s kapi vode, papreni sansho pravi most prema Habano pokrovu.",
        "The reinforced Kyoto version at 54.5% — more body than the standard KI NO BI; it carries a medium cigar neat or with a drop of water, the peppery sansho bridging to a Habano wrapper.",
    ),
    (
        r"ki\s*no\s*bi|kinobi",
        "Kyoto botanika (yuzu, hinoki, sansho papar) je precizna i cvjetna; most je citrusna svježina i papreni začin uz laganu do srednju cigaru — čist ili martini.",
        "Kyoto botanicals (yuzu, hinoki, sansho pepper) are precise and floral; the bridge is citrus lift and peppery spice beside a mild-to-medium cigar — neat or a martini.",
    ),
    (
        r"sipsmith.*v\.?j\.?o\.?p|sipsmith.*vjop",
        "Very Junipery Over Proof, 57.7% — dovoljno tijela i borovice da ponese srednju do punu cigaru; čist ili s kapi vode, borovica i začin nose maduro karamel kao 'treći akt'.",
        "Very Junipery Over Proof, 57.7% — enough body and juniper to carry a medium-to-full cigar; neat or with a drop of water, the juniper and spice carry maduro caramel as a 'third act'.",
    ),
    (
        r"sipsmith.*zesty|sipsmith.*orange",
        "Narančasta kora sladi London dry; traži blagu Connecticut cigaru, ne puni maduro. G&T drži citrus u prvom planu, a borovica i dalje reže laki dim.",
        "Orange peel sweetens the London dry; it wants a mild Connecticut cigar, not a full maduro. A G&T keeps citrus forward, and juniper still cuts light smoke.",
    ),
    (
        r"sipsmith.*london",
        "Hammersmith London dry traži Connecticut ili blagu Habano. Martini drži borovicu čistom, a citrus reže kremasti dim bez da cigaru preglasi.",
        "Hammersmith London dry wants a Connecticut or a mild Habano. A martini keeps the juniper clean, and citrus cuts creamy smoke without flattening the cigar.",
    ),
    (
        r"sipsmith",
        "Čist London dry profil — most prema cigari je klasična borovica i citrus; pouzdan martini uz srednju cigaru, svježina protiv kremastog dima.",
        "A clean London dry profile — the bridge to a cigar is classic juniper and citrus; a dependable martini beside a medium cigar, freshness against creamy smoke.",
    ),
    (
        r"plymouth.*navy",
        "Navy strength 57% — koncentrirana borovica i žestina drže i maduro; čist ili s kapi vode uz punu cigaru, klasičan 'treći akt' s espressom (tamna čokolada + borovica nose karamel maduro pokrova).",
        "Navy strength 57% — concentrated juniper and heat hold even a maduro; neat or with a drop of water beside a full cigar, a classic 'third act' with espresso (dark chocolate + juniper carrying maduro wrapper caramel).",
    ),
    (
        r"plymouth.*original",
        "Original Strength ostaje mekši od navyja; traži Connecticut ili blagu Habano. G&T ili martini drži zaobljenu borovicu uz kremasti dim, bez guranja tijela.",
        "Original Strength stays softer than the navy; it wants a Connecticut or a mild Habano. A G&T or martini holds the rounded juniper beside creamy smoke, without pushing body.",
    ),
    (
        r"plymouth|black friars",
        "Mekši od klasičnog London dry — most je zaobljena borovica; dobar G&T uz srednju cigaru ili martini, gdje blaža žestina ne gazi kremasti dim.",
        "Softer than a classic London dry — the bridge is rounded juniper; a good G&T beside a medium cigar or a martini, where the gentler heat doesn't trample creamy smoke.",
    ),
    (
        r"silent pool.*rose",
        "Ružino izdanje je slađe i cvjetnije; traži vrlo blagu Connecticut cigaru. G&T drži ružu pod kontrolom, a kamilica ne smije pasti u sapunasti dim.",
        "The rose edition is sweeter and more floral; it wants a very mild Connecticut cigar. A G&T keeps the rose in check, and chamomile must not slide into soapy smoke.",
    ),
    (
        r"silent pool.*citrus|silent pool.*rare",
        "Rare Citrus diže koru i kamilicu; traži blagu Connecticut cigaru. Martini drži citrus koncentriran, a G&T radi kao aperitiv uz laki dim.",
        "Rare Citrus lifts peel and chamomile; it wants a mild Connecticut cigar. A martini keeps the citrus concentrated, and a G&T works as an aperitif beside light smoke.",
    ),
    (
        r"silent pool",
        "Cvjetna kamilica i med traže Connecticut, ne maduro. Čist ili martini drži profil mekanim, a svježina reže kremasti dim bez dodatnog tijela.",
        "Floral chamomile and honey want Connecticut, not maduro. Neat or a martini keeps the profile soft, and the lift cuts creamy smoke without adding body.",
    ),
    (
        r"copperhead.*barrel",
        "Bačva dodaje hrast i tijelo; nosi srednju Habano čist ili s kapi vode. Začin i citrus i dalje režu dim, a slatki maduro lako preuzme večer.",
        "The cask adds oak and body; it carries a medium Habano neat or with a drop of water. Spice and citrus still cut the smoke, and a sugary maduro easily takes over.",
    ),
    (
        r"copperhead.*black",
        "Black Batch zgušnjava začin na London dry bazi; traži srednju Habano. Martini drži profil suh, a citrus sprečava da začin zgazi cigaru.",
        "Black Batch densifies spice on a London dry base; it wants a medium Habano. A martini keeps the profile dry, and citrus stops the spice from flattening the cigar.",
    ),
    (
        r"copperhead",
        "Alchemistov začinski dry traži Connecticut ili blagu Habano. Martini drži koriander i citrus uz laki dim, bez guranja punog madura.",
        "The Alchemist's spiced dry wants a Connecticut or a mild Habano. A martini holds coriander and citrus beside light smoke, without pushing a full maduro.",
    ),
    (
        r"dugave",
        "Lokalni craft s mediteranskim biljem — most je začinska svježina uz blažu Habano; G&T ili martini da botanika ostane u prvom planu, bez guranja tijela.",
        "A local craft with Mediterranean herbs — the bridge is a herbal lift beside a milder Habano; a G&T or martini to keep the botanicals forward, without pushing body.",
    ),
    (
        r"beefeater.*24",
        "Čaj i citrus na London dry bazi — most je taninska gorčina čaja koja odgovara duhanskom začinu; lagana do srednja cigara, martini ili G&T kao aperitiv.",
        "Tea and citrus on a London dry base — the bridge is the tea's tannic edge meeting tobacco spice; a mild-to-medium cigar, martini or G&T as an aperitif.",
    ),
    (
        r"beefeater",
        "Radnički London dry sjeda uz Connecticut; borovica i koriander režu kremasti dim. G&T je prirodan aperitiv, a martini drži profil suh uz kraću cigaru.",
        "A workhorse London dry sits beside Connecticut; juniper and coriander cut creamy smoke. A G&T is the natural aperitif, and a martini keeps the profile dry with a shorter cigar.",
    ),
    (
        r"malfy.*limone",
        "Sicilijanski limun traži blagu Connecticut cigaru, ne maduro. G&T drži koru u prvom planu, a bilje prati laki dim bez dodatnog tijela.",
        "Sicilian lemon wants a mild Connecticut cigar, not a maduro. A G&T keeps the peel forward, and the herbs track light smoke without adding body.",
    ),
    (
        r"malfy.*arancia",
        "Krvava naranča sladi mediteranski dry; traži Connecticut ili vrlo blagu Habano. G&T drži voće svježim, a gorčina kore reže kremasti dim.",
        "Blood orange sweetens the Mediterranean dry; it wants a Connecticut or a very mild Habano. A G&T keeps the fruit fresh, and the peel bitterness cuts creamy smoke.",
    ),
    (
        r"malfy.*mini",
        "Mini set nudi isti mediteranski citrus u malim bocama; traži blagu Connecticut cigaru. G&T je jedini razuman format uz laki dim.",
        "The mini set offers the same Mediterranean citrus in small bottles; it wants a mild Connecticut cigar. A G&T is the only sensible format beside light smoke.",
    ),
    (
        r"malfy",
        "Originale nosi smokvu i mediteransko bilje uz Connecticut ili blagu Habano. G&T drži sparivanje pitkim, a citrus reže kremasti dim.",
        "Originale carries fig and Mediterranean herbs beside a Connecticut or mild Habano. A G&T keeps the match drinkable, and citrus cuts creamy smoke.",
    ),
    (
        r"citadelle.*reserve",
        "Réserve dodaje hrast na anisnu bazu; nosi srednju Habano čist. Vanilija i citrus drže sparivanje suhim, a slatki maduro lako preglasi čašu.",
        "Réserve adds oak to the anise base; it carries a medium Habano neat. Vanilla and citrus keep the match dry, and a sugary maduro easily outshouts the glass.",
    ),
    (
        r"citadelle",
        "Francuski dry s anisom traži Connecticut ili blagu Habano. Martini drži profil suh, a citrus i koromač režu kremasti dim bez sapunastog finiša.",
        "A French dry with anise wants a Connecticut or a mild Habano. A martini keeps the profile dry, and citrus and fennel cut creamy smoke without a soapy finish.",
    ),
    (
        r"aviation",
        "American dry s cvjetno-anisnim tonom — nježan profil traži laganu Connecticut cigaru; most je svježina anisa i cvijeća uz laki, kremasti dim.",
        "An American dry with a floral-anise tone — the delicate profile wants a mild Connecticut cigar; the bridge is anise and floral lift beside light, creamy smoke.",
    ),
    (
        r"elephant.*orange|elephant.*cocoa",
        "Naranča i kakao slade afrički dry; traže srednju Habano, ne puni maduro. Čist drži kakao uz duhan, a citrus sprečava da slatko zgazi cigaru.",
        "Orange and cocoa sweeten the African dry; they want a medium Habano, not a full maduro. Neat holds cocoa against the tobacco, and citrus stops the sweetness flattening the cigar.",
    ),
    (
        r"elephant.*satao",
        "Satao zgušnjava začin i suho voće; nosi srednju Habano čist ili martini. Borovica i dalje reže dim, a tijelo ne traži oscuro.",
        "Satao densifies spice and dried fruit; it carries a medium Habano neat or as a martini. Juniper still cuts the smoke, and the body does not ask for an oscuro.",
    ),
    (
        r"elephant.*miniature|elephant.*tasting",
        "Tasting set nudi isti afrički dry u minijaturama; traži blagu Connecticut cigaru. G&T je jedini razuman format uz laki dim.",
        "The tasting set offers the same African dry in miniatures; it wants a mild Connecticut cigar. A G&T is the only sensible format beside light smoke.",
    ),
    (
        r"elephant",
        "Afrički London dry s bokvica i suhim voćem traži Connecticut ili blagu Habano. Martini drži profil suh, a bilje prati kremasti dim.",
        "An African London dry with buchú and dried fruit wants a Connecticut or a mild Habano. A martini keeps the profile dry, and the herbs track creamy smoke.",
    ),
    (
        r"aura.*karbun",
        "Navy strength s istrijskim ugljenom nosi srednju do punu Habano. Čist ili s kapi vode drži borovicu uz zemljasti dim; G&T razvodni je za ovu žestinu.",
        "Navy strength with Istrian charcoal carries a medium to full Habano. Neat or with a drop of water holds juniper against earthy smoke; a G&T is too dilute for this heat.",
    ),
    (
        r"old pilot|dalmatian.*gin",
        "Mediteranska botanika (ružmarin, kadulja, borovica) pravi most uz Habano pokrov; najbolje G&T ili martini uz srednju cigaru — začinska svježina prati zemljasti dim.",
        "Mediterranean botanicals (rosemary, sage, juniper) bridge to a Habano wrapper; best as a G&T or martini beside a medium cigar — the herbal lift tracking earthy smoke.",
    ),
    (
        r"no\.?\s*3\b|number\s*three",
        "Angelika i kardamom na London dry bazi sjeda uz Connecticut ili blagu Habano. Martini drži borovicu koncentriranom, a korijenasta nota prati duhanski začin.",
        "Angelica and cardamom on a London dry base sit beside a Connecticut or a mild Habano. A martini keeps the juniper concentrated, and the root note tracks tobacco spice.",
    ),
    (
        r"amuerte.*black",
        "Black edition zgušnjava kokin list i začin; nosi srednju Habano čist. Gorka botanika reže kremasti dim, a slatki maduro lako preuzme večer.",
        "The black edition densifies coca leaf and spice; it carries a medium Habano neat. Bitter botanicals cut creamy smoke, and a sugary maduro easily takes over.",
    ),
    (
        r"amuerte.*red",
        "Red edition sladi tamnim voćem; traži blagu do srednju Habano, ne oscuro. G&T drži voće svježim, a bilje prati laki dim.",
        "The red edition sweetens with dark fruit; it wants a mild to medium Habano, not an oscuro. A G&T keeps the fruit fresh, and the herbs track light smoke.",
    ),
    (
        r"amuerte.*white",
        "White edition ostaje bliža borovici; traži Connecticut ili blagu Habano. Martini drži profil suh, a citrus reže kremasti dim.",
        "The white edition stays closer to juniper; it wants a Connecticut or a mild Habano. A martini keeps the profile dry, and citrus cuts creamy smoke.",
    ),
    (
        r"amuerte.*blue",
        "Blue edition diže anis i citrus; traži blagu Connecticut cigaru. Martini drži koromač pod kontrolom, da sapunasti finiš ne sjedne na dim.",
        "The blue edition lifts anise and citrus; it wants a mild Connecticut cigar. A martini keeps fennel in check, so a soapy finish does not land on the smoke.",
    ),
    (
        r"amuerte.*green",
        "Green edition je travnatija i suša; traži Connecticut. G&T drži zeleni ton uz laki dim, a tijelo ne nosi maduro.",
        "The green edition is grassier and drier; it wants Connecticut. A G&T holds the green tone beside light smoke, and the body does not carry a maduro.",
    ),
    (
        r"amuerte.*orange",
        "Orange edition diže koru i cvijet; traži blagu Connecticut cigaru. G&T ostavlja citrus u prvom planu uz kremasti dim.",
        "The orange edition lifts peel and flower; it wants a mild Connecticut cigar. A G&T leaves citrus forward beside creamy smoke.",
    ),
    (
        r"amuerte.*yellow",
        "Yellow edition ostaje svijetla i cvjetna; traži Connecticut, ne Habano. G&T drži sparivanje pitkim, a gorčina kore reže laki dim.",
        "The yellow edition stays bright and floral; it wants Connecticut, not Habano. A G&T keeps the match drinkable, and the peel bitterness cuts light smoke.",
    ),
    (
        r"amuerte",
        "Kokin list zgušnjava botaniku; traži Connecticut ili blagu Habano. Čist ili martini drži gorki list uz kremasti dim, bez punog madura.",
        "Coca leaf densifies the botanicals; it wants a Connecticut or a mild Habano. Neat or a martini holds the bitter leaf beside creamy smoke, without a full maduro.",
    ),
    (
        r"\broku\b",
        "Japanski craft (sakura, sencha, sansho) — most je zeleni čaj i cvjetni začin uz laganu do srednju cigaru; martini drži profil, G&T radi kao aperitiv.",
        "A Japanese craft (sakura, sencha, sansho) — the bridge is green tea and floral spice beside a mild-to-medium cigar; a martini holds the profile, a G&T works as an aperitif.",
    ),
    (
        r"akori",
        "Španjolski premium dry sjeda uz Connecticut; borovica i travnati ton režu kremasti dim. Martini drži profil suh uz kraću cigaru.",
        "A Spanish premium dry sits beside Connecticut; juniper and a grassy tone cut creamy smoke. A martini keeps the profile dry with a shorter cigar.",
    ),
    (
        r"roby\s*marton",
        "Talijanski premium dry na 47% nosi srednju Habano čist. Citrus i borovica režu dim, a žestina ne traži oscuro.",
        "An Italian premium dry at 47% carries a medium Habano neat. Citrus and juniper cut the smoke, and the heat does not ask for an oscuro.",
    ),
    (
        r"scapegrace.*gold",
        "Gold na 57% drži i puniju Habano; čist ili s kapi vode. Borovica i začin nose treći akt, a G&T razvodni je za ovu žestinu.",
        "Gold at 57% holds even a fuller Habano; neat or with a drop of water. Juniper and spice carry a third act, and a G&T is too dilute for this heat.",
    ),
    (
        r"scapegrace",
        "Novozelandski premium dry sjeda uz Connecticut ili blagu Habano. Martini drži borovicu čistom, a citrus reže kremasti dim bez guranja tijela.",
        "A New Zealand premium dry sits beside a Connecticut or a mild Habano. A martini keeps the juniper clean, and citrus cuts creamy smoke without pushing body.",
    ),
    (
        r"windspiel.*kaffee|windspiel.*caxambu",
        "Caxambu kava sladi njemački dry; nosi srednju Habano čist. Espresso nota sjeda uz duhan, a borovica sprečava da kava zgazi cigaru.",
        "Caxambu coffee sweetens the German dry; it carries a medium Habano neat. The espresso note sits against the tobacco, and juniper stops the coffee flattening the cigar.",
    ),
    (
        r"windspiel.*pfeffer|windspiel.*kampot",
        "Kampot papar diže začin; traži srednju Habano, ne Connecticut. Martini drži papar uz duhanski začin, a citrus reže kremasti dim.",
        "Kampot pepper lifts the spice; it wants a medium Habano, not Connecticut. A martini holds the pepper against tobacco spice, and citrus cuts creamy smoke.",
    ),
    (
        r"windspiel.*reserve",
        "Reserve u drvenoj kutiji zgušnjava tijelo; nosi srednju Habano čist. Hrast i borovica drže sparivanje suhim, a slatki maduro lako preuzme večer.",
        "Reserve in a wooden case densifies the body; it carries a medium Habano neat. Oak and juniper keep the match dry, and a sugary maduro easily takes over.",
    ),
    (
        r"windspiel",
        "Njemački premium dry sjeda uz Connecticut ili blagu Habano. Martini drži borovicu čistom, a citrus reže kremasti dim bez guranja tijela.",
        "A German premium dry sits beside a Connecticut or a mild Habano. A martini keeps the juniper clean, and citrus cuts creamy smoke without pushing body.",
    ),
]


def cigar_hint_pair(name: str, style: str = "", botanical: str = "") -> dict[str, str]:
    for pattern, hr, en in HINT_PAIRS:
        if re.search(pattern, name, re.IGNORECASE):
            return {"hr": hr, "en": en}
    return {
        "hr": cigar_hint_for_style(style, botanical),
        "en": cigar_hint_en_for_style(style, botanical),
    }


def find_best_catalog_match(name: str, catalog: list[dict]) -> dict | None:
    tokens = match_tokens(name)
    age_nums = numeric_age_tokens(name)
    best, best_score = None, 0
    for entry in catalog:
        url = entry.get("url", "")
        if is_bare_category_url(url):
            continue
        score = len(tokens & entry["tokens"])
        if score <= best_score:
            continue
        if age_nums and not age_nums.issubset(catalog_entry_tokens(entry, match_tokens)):
            continue
        best, best_score = entry, score
    return best if best and best_score >= 3 else None


def catalog_index(entries: list[dict]) -> list[dict]:
    return [{**e, "tokens": match_tokens(e["name"])} for e in entries]
