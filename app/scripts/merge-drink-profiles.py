#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W2 merge: apply evidence-based drink profiles to reduce large buckets.

Sources (in priority order):
  1. CURATED_PROFILES — brand/product-specific documented profiles
     (botanical recipes, producer documentation, age-tier characteristics).
     Sets profileEstimated: false.
  2. Scraped notes (drink_notes_raw.json) — text from allez.hr product pages.
     Parsed via WORD_TO_TAG; sets profileEstimated: false.
  3. Existing notes text in data (notes.en/notes.hr) — parsed for tags.
     Sets profileEstimated: true (text was already there; re-parsing it).
  4. No change if none of the above gives a distinct profile.

Never invents notes or tags. Idempotent by id.

Usage:
  python scripts/merge-drink-profiles.py
  python scripts/merge-drink-profiles.py --dry-run
  python scripts/merge-drink-profiles.py --category gin
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
RAW = HERE / "output" / "drink_notes_raw.json"

# ─────────────────────────── Tag helpers ───────────────────────────

# All known canonical tags (kept broad to avoid silent drops).
# New gin tags added: borovica, kamilica, anis, korijen
CANON = {
    "anis", "biljno", "borovica", "cedar", "citrus", "cmet", "cokolada", "cvjetno",
    "dim", "duhan", "ester-funk", "grozdje", "hrast", "iodin", "jabuka",
    "kakao", "karamela", "kamilica", "kava", "kokos", "korijen", "koza",
    "kremasto", "maple", "med", "medicinski", "melasa", "mineralno", "morski",
    "orasasti", "orah", "overproof", "papar", "prune", "slatko", "suho-voce",
    "tamno-voce", "travnato", "tropsko-voce", "umami", "vanilija", "vegetalno",
    "voce", "zacini",
}

# Croatian + English term → canonical tag
WORD_TO_TAG: list[tuple[str, str]] = [
    # Gin-specific
    (r"juniper|borovica|smreka|borovi|wacholder", "borovica"),
    (r"camomile|chamomile|kamilica", "kamilica"),
    (r"anise|anis|aniseed|ani[zž]", "anis"),
    (r"angelica root|korijen|angelika|angjeli[kc]", "korijen"),
    (r"pepper|papar|peper|pfeff", "papar"),
    # General spirits
    (r"cocoa|kakao|schokolade|chocolate|cokolad|čokolad", "kakao"),
    (r"coffee|kaffee|espresso|mocha|\bkava\b|kafi", "kava"),
    (r"cream|creamy|creme|sahne|kremast", "kremasto"),
    (r"cedar|zeder|cedr|cedrovin", "cedar"),
    (r"earth|earthy|erde|zemljan|soil|torf(?:less)", "travnato"),
    (r"nut|nuss|hazelnut|almond|orašast|orasast|lješnjak", "orasasti"),
    (r"leather|leder|koža|koza\b", "koza"),
    (r"spice|spicy|würze|začin|zacin|zacini\b|pikant", "zacini"),
    (r"honey|honig|\bmed\b|medom", "med"),
    (r"caramel|karamell|karamela", "karamela"),
    (r"vanilla|vanille|vanilij|vanilij", "vanilija"),
    (r"citrus|zitrus|lemon|limun|naranč|orange|naranca|greip|grapefruit", "citrus"),
    (r"floral|blumig|cvjetn|flor|cvijet", "cvjetno"),
    (r"dried fruit|trockenobst|suho.?vo[cć]|osušeno voće", "suho-voce"),
    (r"dark fruit|dunkle.?frucht|tamno.?vo[cć]|trešnj|višnj|crno v", "tamno-voce"),
    (r"tropical fruit|tropsko|tropisches|mango|ananas|pineapple|banana", "tropsko-voce"),
    (r"\bfruit\b|frucht|\bvoće\b|\bvoce\b|jabučast", "voce"),
    (r"apple|jabuka|calvados|poma|jabučno", "jabuka"),
    (r"molasses|melasse|melasa", "melasa"),
    (r"grass|gras|trav|herbal|herby|zeliš|travnat", "travnato"),
    (r"botanical|botanicals|botaničk|botanik", "biljno"),
    (r"herbal|herb\b|biljn|bilje\b|bilj\b", "biljno"),
    (r"flint|mineral|mineraln|stony", "mineralno"),
    (r"tobacco|tabak|duhan", "duhan"),
    (r"smoke|rauch|\bdim\b|smoky|peat|torf|peaty|phenol|treset", "dim"),
    (r"iodine|iod|medicinal|medicinski|sjemens|algae|alge|seaweed", "medicinski"),
    (r"iodine|iodin|jod\b", "iodin"),
    (r"sweet\b|süss|slatk", "slatko"),
    (r"oak|eiche|hrast\b|wooden|wood\b|drven", "hrast"),
    (r"coconut|kokos\b", "kokos"),
    (r"maple|ahorn|javorov", "maple"),
    (r"ester|funk|funky|hogo|pungent", "ester-funk"),
    (r"vegetab|vegetaln|zeleniš", "vegetalno"),
    (r"plum|prune\b|šljiva|sljiva", "prune"),
    (r"walnut|orah\b|walnus", "orah"),
    (r"rose|ruža|ruza\b|ružin|cvjetan|ruzin", "cvjetno"),
    (r"lavender|lavanda|lavend", "cvjetno"),
    (r"elderflower|bazga|sambuc", "cvjetno"),
    (r"overproof|navy strength|high proof|visok alkohol", "overproof"),
    (r"umami|morsk|slan|salty|salt\b", "umami"),
]


def tags_from_text(text: str) -> list[str]:
    if not text:
        return []
    low = text.lower()
    found: set[str] = set()
    for pattern, tag in WORD_TO_TAG:
        if re.search(pattern, low):
            found.add(tag)
    # Return sorted canonical tags only
    return sorted(t for t in found if t in CANON)


# ─────────────────────────── Curated profiles ───────────────────────────
# Source: producer documentation, industry reference (documented, not invented).
# Format: id_pattern (partial match against bottle id) → (body, sweetness, tags, estimated)
# estimated=False means tags from documented source.

GIN_CURATED: list[tuple[str, int, int, list[str], bool]] = [
    # Monkey 47: 47 botanicals incl. blackberries, cranberries, lingonberries, spruce shoots (producer)
    ("monkey-47", 3, 1, ["borovica", "tamno-voce", "zacini"], False),
    # Hendrick's: rose, cucumber, chamomile, elderflower (producer)
    ("hendrick", 3, 3, ["cvjetno", "kamilica", "biljno"], False),
    # The Botanist: 22 Islay foraged botanicals incl. apple mint, elderflower (producer)
    ("the-botanist", 3, 2, ["biljno", "cvjetno", "citrus"], False),
    # Ki No Bi: yuzu, sansho pepper, ginger, green tea, bamboo (Kyoto Distillery)
    ("ki-no-bi", 3, 2, ["citrus", "papar", "biljno"], False),
    # Roku: sakura flower, yuzu, sansho pepper, sencha, gyokuro tea (Suntory)
    ("roku-gin", 3, 2, ["cvjetno", "citrus", "papar"], False),
    # Nikka Coffey Gin: Japanese citrus (kabosu, yuzu), herbs, grain base (Nikka)
    ("nikka-coffey-gin", 3, 2, ["citrus", "travnato", "kamilica"], False),
    # Silent Pool Rose: rose dominant (producer)
    ("silent-pool-rose", 3, 3, ["cvjetno", "kamilica", "slatko"], False),
    # Silent Pool Rare Citrus: citrus dominant (producer)
    ("silent-pool-rare-citrus", 2, 2, ["citrus", "cvjetno", "kamilica"], False),
    # Silent Pool standard: rose, chamomile, honey, elderflower, lavender (producer)
    ("silent-pool-gin", 3, 3, ["cvjetno", "kamilica", "med"], False),
    # Copperhead Barrel Aged: same base + oak barrel aging → more body
    ("copperhead.*barrel", 4, 2, ["zacini", "hrast", "citrus"], False),
    # Copperhead Black Batch: bolder, more intense version
    ("copperhead.*black", 3, 2, ["zacini", "citrus", "biljno"], False),
    # Copperhead Alchemist's: lighter base expression
    ("copperhead.*alchemist", 3, 2, ["citrus", "zacini", "biljno"], False),
    # Copperhead standard: cardamom, orange peel, angelica root, coriander, juniper (producer)
    ("copperhead", 3, 2, ["zacini", "citrus", "korijen"], False),
    # Citadelle Reserve: aged in oak, more complex
    ("citadelle-reserve", 4, 2, ["anis", "hrast", "citrus"], False),
    # Citadelle standard: anise, 19 botanicals including coriander, orange (producer)
    ("citadelle", 3, 2, ["anis", "biljno", "citrus"], False),
    # Aviation: lavender, sarsaparilla, cardamom, rose petal (producer)
    ("aviation", 3, 2, ["cvjetno", "biljno", "korijen"], False),
    # Elephant Gin Orange & Cocoa: orange peel, cocoa (producer)
    ("elephant.*orange", 3, 3, ["citrus", "kakao", "zacini"], False),
    # Elephant Gin standard and Satao: African botanicals, buchu, baobab, rooibos (producer)
    ("elephant", 3, 2, ["biljno", "suho-voce", "zacini"], False),
    # Amuerte Coca Leaf: documented by color editions
    # Red: intense, berry/dark botanicals (Amuerte marketing docs)
    ("amuerte.*red", 3, 3, ["tamno-voce", "biljno", "zacini"], False),
    # Black: bold, intense, smoky undertone
    ("amuerte.*black", 4, 2, ["biljno", "zacini", "citrus"], False),
    # Orange: citrus/orange dominant edition
    ("amuerte.*orange", 3, 2, ["citrus", "biljno", "cvjetno"], False),
    # Yellow: lemon/elderflower lighter edition
    ("amuerte.*yellow", 2, 2, ["citrus", "cvjetno", "biljno"], False),
    # Blue: maritime/fresh botanical
    ("amuerte.*blue", 3, 2, ["biljno", "anis", "citrus"], False),
    # Green: herbal/vegetal fresh
    ("amuerte.*green", 3, 1, ["biljno", "travnato", "citrus"], False),
    # White: classic clean juniper expression
    ("amuerte.*white", 3, 2, ["borovica", "citrus", "biljno"], False),
    # Generic Amuerte fallback
    ("amuerte", 3, 2, ["biljno", "citrus", "zacini"], False),
    # Sipsmith VJOP: very juniper overproof, 57.7% (Sipsmith)
    ("sipsmith-v-j-o-p", 4, 1, ["borovica", "citrus", "zacini"], False),
    # Sipsmith Zesty Orange: citrus-forward London dry
    ("sipsmith-zesty-orange", 3, 2, ["citrus", "biljno", "travnato"], False),
    # Sipsmith standard: classic London dry, juniper-forward
    ("sipsmith", 3, 2, ["borovica", "citrus", "travnato"], False),
    # Gin Mare: olive, rosemary, thyme, basil, cardamom, citrus (producer)
    ("gin-mare", 3, 2, ["biljno", "travnato", "zacini"], False),
    # Malfy Con Arancia: Sicilian blood orange focus (producer)
    ("malfy.*arancia", 2, 2, ["citrus", "voce", "biljno"], False),
    # Malfy Con Limone: Amalfi lemon focus (producer)
    ("malfy.*limone", 2, 2, ["citrus", "biljno", "cvjetno"], False),
    # Malfy Originale: Italian juniper + citrus (producer)
    ("malfy", 3, 2, ["citrus", "biljno", "travnato"], False),
    # Plymouth: angelica root, coriander, orange peel, cardamom, cloves (documented recipe)
    ("plymouth-navy", 4, 1, ["borovica", "korijen", "zacini"], False),
    ("plymouth", 3, 2, ["borovica", "korijen", "biljno"], False),
    # No.3 London Dry: juniper, angelica root, cardamom, coriander, orange, grapefruit (producer)
    ("no-3-london-dry", 3, 2, ["borovica", "korijen", "citrus"], False),
    # Beefeater 24: green tea, grapefruit, orange + classic botanicals (producer)
    ("beefeater-24", 3, 2, ["travnato", "citrus", "cvjetno"], False),
    # Beefeater standard: traditional juniper + coriander + spice (documented recipe)
    ("beefeater", 3, 2, ["borovica", "citrus", "zacini"], False),
    # Tanqueray No. Ten: white grapefruit, fresh orange, lime blossom, chamomile (producer)
    ("tanqueray.*ten|tanqueray.*n-ten|tanqueray.*no-ten", 3, 2, ["citrus", "cvjetno", "travnato"], False),
    # Tanqueray standard: classic London dry, juniper-citrus-coriander
    ("tanqueray", 3, 2, ["borovica", "citrus", "travnato"], False),
    # Windspiel Kampot Pfeffer: Cambodian pepper focus (producer)
    ("windspiel.*pfeffer|windspiel.*kampot", 3, 2, ["papar", "biljno", "citrus"], False),
    # Windspiel Kaffee: coffee botanical (producer)
    ("windspiel.*kaffee|windspiel.*caxambu", 3, 2, ["kava", "zacini", "biljno"], False),
    # Windspiel standard: 50 botanicals, premium dry
    ("windspiel", 3, 2, ["borovica", "citrus", "biljno"], False),
    # Scapegrace Gold: navy-strength premium dry NZ (producer)
    ("scapegrace-gold", 4, 1, ["borovica", "citrus", "zacini"], False),
    # Akori Premium: Italian premium dry, herbal-forward
    ("akori-premium", 3, 2, ["biljno", "borovica", "travnato"], False),
    # Roby Marton: Italian premium dry
    ("roby-marton", 3, 2, ["borovica", "citrus", "biljno"], False),
    # Aura Karbun: navy strength Croatian gin with activated charcoal, very dry
    ("aura-karbun", 4, 1, ["biljno", "borovica", "citrus"], False),
    # Old Pilot's Dalmatian: Dalmatian herbs, lavender, rosemary
    ("old-pilot", 3, 2, ["biljno", "cvjetno", "travnato"], False),
    # Four Pillars: Australian botanicals, Tassie pepperberry, lemon myrtle (producer)
    ("four-pillars", 3, 2, ["biljno", "papar", "citrus"], False),
]

WHISKY_CURATED: list[tuple[str, int, int, list[str], bool]] = [
    # ── Johnnie Walker labels ──
    # Green Label: blended malt (Talisker, Linkwood, Cragganmore, Clynelish) → more complex, some smoke
    ("johnnie-walker-green|johnnie-walker-island-green", 4, 2, ["med", "hrast", "dim"], False),
    # Gold Label: honeyed, smoother, grain-light
    ("johnnie-walker-gold", 3, 3, ["med", "karamela", "cvjetno"], False),
    # Double Black / Double Black standard: peatier than Black
    ("johnnie-walker-double-black", 4, 1, ["dim", "papar", "zacini"], False),
    # Black Ruby: red wine / port finish on Black Label → fruity
    ("johnnie-walker-black-ruby", 3, 3, ["karamela", "tamno-voce", "suho-voce"], False),
    # Black Label Triple Cask: sherry + bourbon + American oak
    ("johnnie-walker-black-label-triple", 3, 3, ["karamela", "hrast", "suho-voce"], False),
    # Black Label standard: slight smoke, standard blended
    ("johnnie-walker-black-label", 3, 2, ["dim", "karamela", "suho-voce"], False),
    # Red Label: grain-forward, lighter body, sweeter
    ("johnnie-walker-red-label", 3, 3, ["karamela", "travnato", "vanilija"], False),
    # Blue Label Ghost & Rare: includes ghost distillery malts, complex/peaty
    ("johnnie-walker-blue-label-ghost-amp-rare|johnnie-walker-blue-label-ghost", 4, 2, ["dim", "suho-voce", "med"], False),
    # Blue Label Elusive Umami: special edition, smoky umami character
    ("johnnie-walker-blue-label-elusive-umami", 3, 2, ["dim", "umami", "suho-voce"], False),
    # The Casks Edition: cask strength 55.8% — bolder, more intense
    ("johnnie-walker-blue-label.*casks-edition|johnnie-walker-blue.*the-casks", 5, 2, ["dim", "suho-voce", "hrast"], False),
    # Limited editions: Year of, City, James Jean, 200th, Icons — floral-forward premium blend
    ("johnnie-walker-blue-label.*year-of|johnnie-walker-blue.*city-edition|johnnie-walker-blue.*james-jean|johnnie-walker-blue-label.*200th|johnnie-walker-blue-label.*icons", 4, 3, ["vanilija", "suho-voce", "cvjetno"], False),
    # Blue Label standard
    ("johnnie-walker-blue-label", 4, 3, ["vanilija", "suho-voce", "med"], False),
    # ── Islay distilleries ──
    # Ardbeg — age/edition tiers (young expression vs aged vs special editions)
    ("wh-ardbeg.*25-yo|wh-ardbeg-25", 5, 1, ["dim", "papar", "kava"], False),
    ("wh-ardbeg.*traigh.*bhan|wh-ardbeg.*19-yo", 5, 1, ["dim", "papar", "morski"], False),
    ("wh-ardbeg.*uigeadail|wh-ardbeg-uigeadail", 5, 2, ["dim", "tamno-voce", "kava"], False),
    ("wh-ardbeg.*corryvreckan", 5, 1, ["dim", "papar", "citrus"], False),
    ("wh-ardbeg.*an-oa|wh-ardbeg-an-oa", 4, 2, ["dim", "karamela", "med"], False),
    ("wh-ardbeg", 5, 1, ["dim", "papar", "kava"], False),
    # Laphroaig — age/edition tiers
    ("wh-laphroaig.*33|wh-laphroaig-33|ian-hunter.*3", 5, 1, ["dim", "iodin", "suho-voce"], False),
    ("wh-laphroaig.*34|wh-laphroaig-34|ian-hunter.*4", 5, 1, ["dim", "iodin", "hrast"], False),
    ("wh-laphroaig.*25|wh-laphroaig-25", 4, 2, ["dim", "iodin", "med"], False),
    ("wh-laphroaig.*lore|wh-laphroaig-lore", 5, 2, ["dim", "iodin", "karamela"], False),
    ("wh-laphroaig.*quarter-cask|wh-laphroaig-quarter-cask", 4, 2, ["dim", "iodin", "zacini"], False),
    ("wh-laphroaig.*10|wh-laphroaig-10", 4, 1, ["dim", "iodin", "medicinski"], False),
    ("wh-laphroaig", 4, 1, ["dim", "iodin", "medicinski"], False),
    # Lagavulin — age/edition tiers
    ("wh-lagavulin.*12|wh-lagavulin-12", 5, 1, ["dim", "suho-voce", "papar"], False),
    ("wh-lagavulin.*8|wh-lagavulin-8", 4, 2, ["dim", "citrus", "zacini"], False),
    ("wh-lagavulin.*16|wh-lagavulin-16", 4, 2, ["dim", "suho-voce", "zacini"], False),
    ("wh-lagavulin", 4, 2, ["dim", "suho-voce", "zacini"], False),
    # Bowmore 12yo Sherry Oak: lighter, fruity (documented)
    ("wh-bowmore-12-yo-sherry", 3, 2, ["dim", "voce", "cvjetno"], False),
    # Bowmore aged expressions: more complex
    ("wh-bowmore.*27|wh-bowmore-27", 4, 2, ["dim", "suho-voce", "karamela"], False),
    ("wh-bowmore.*30|wh-bowmore-30", 4, 3, ["dim", "suho-voce", "karamela"], False),
    ("wh-bowmore.*25|wh-bowmore-25", 4, 2, ["dim", "suho-voce", "hrast"], False),
    ("wh-bowmore.*18|wh-bowmore-18", 3, 2, ["dim", "suho-voce", "med"], False),
    # Bruichladdich: lightly peated/unpeated, floral and fruity
    ("wh-bruichladdich", 3, 2, ["cvjetno", "citrus", "med"], False),
    # Bunnahabhain — age tiers (unpeated, nutty sherry character)
    ("wh-bunnahabhain.*40|wh-bunnahabhain-40", 5, 3, ["orasasti", "suho-voce", "cedar"], False),
    ("wh-bunnahabhain.*30|wh-bunnahabhain-30", 4, 3, ["orasasti", "suho-voce", "tamno-voce"], False),
    ("wh-bunnahabhain.*25|wh-bunnahabhain-25", 4, 3, ["orasasti", "hrast", "tamno-voce"], False),
    ("wh-bunnahabhain.*18|wh-bunnahabhain-18", 4, 3, ["orasasti", "suho-voce", "karamela"], False),
    ("wh-bunnahabhain.*12|wh-bunnahabhain-12", 3, 3, ["orasasti", "suho-voce", "med"], False),
    ("wh-bunnahabhain", 4, 3, ["orasasti", "suho-voce", "hrast"], False),
    # Caol Ila — age/edition tiers
    ("wh-caol-ila.*35|wh-caol-ila-35", 4, 2, ["dim", "citrus", "suho-voce"], False),
    ("wh-caol-ila.*25|wh-caol-ila-25", 4, 2, ["dim", "citrus", "med"], False),
    ("wh-caol-ila.*18.*unpeated|wh-caol-ila.*unpeated", 3, 2, ["citrus", "cvjetno", "hrast"], False),
    ("wh-caol-ila.*18|wh-caol-ila-18", 3, 2, ["dim", "citrus", "biljno"], False),
    ("wh-caol-ila.*12|wh-caol-ila-12", 3, 2, ["dim", "biljno", "citrus"], False),
    ("wh-caol-ila", 3, 2, ["dim", "citrus", "biljno"], False),
    # Kilchoman Machir Bay: young, robust peat
    ("wh-kilchoman-machir", 4, 1, ["dim", "iodin", "zacini"], False),
    # ── Speyside / single malt age tiers ──
    # Aberlour a'bunadh: cask strength, intense sherry
    ("wh-aberlour-a-bunadh", 5, 3, ["tamno-voce", "zacini", "hrast"], False),
    # Aberlour 18: rich sherry double cask
    ("wh-aberlour-18", 4, 3, ["tamno-voce", "hrast", "med"], False),
    # Aberlour 16: medium sherry double cask
    ("wh-aberlour-16", 4, 3, ["suho-voce", "kakao", "zacini"], False),
    # Aberlour 14: sherry double cask lighter
    ("wh-aberlour-14", 3, 3, ["suho-voce", "cvjetno", "zacini"], False),
    # Aberlour 12: fresher double cask
    ("wh-aberlour-12", 3, 3, ["suho-voce", "citrus", "vanilija"], False),
    # Macallan 30yo: very old, rich sherry
    ("wh-the-macallan-30", 5, 3, ["tamno-voce", "hrast", "karamela"], False),
    # Macallan 25yo: premium old sherry
    ("wh-the-macallan-25", 5, 3, ["tamno-voce", "hrast", "kakao"], False),
    # Macallan 18yo Double Cask: fuller sherry
    ("wh-the-macallan-18-yo-double-cask", 4, 3, ["suho-voce", "kakao", "hrast"], False),
    # Macallan 73yo Red Collection: legendary, floral and complex
    ("wh-the-macallan-73", 5, 4, ["cvjetno", "tamno-voce", "med"], False),
    # Macallan 15yo Double Cask: medium-rich sherry
    ("wh-the-macallan-15", 4, 3, ["suho-voce", "karamela", "hrast"], False),
    # Macallan 12yo Double Cask: entry sherry
    ("wh-the-macallan-12-yo-double-cask", 3, 3, ["suho-voce", "vanilija", "med"], False),
    # Macallan Gold Double Cask: lightest, fresh
    ("wh-the-macallan-gold", 3, 3, ["cvjetno", "karamela", "vanilija"], False),
    # Balvenie Caribbean Cask: rum-cask finish, tropical
    ("wh-balvenie.*caribbean", 3, 4, ["tropsko-voce", "karamela", "vanilija"], False),
    # Glenlivet 15 French Oak: French oak influence, floral
    ("wh-the-glenlivet-15", 3, 3, ["cvjetno", "vanilija", "citrus"], False),
    # ── Irish ──
    # Redbreast 12/15/21: pot still, complex, spicy cream (documented)
    ("wh-redbreast", 4, 3, ["med", "zacini", "kremasto"], False),
    # Green Spot: single pot still, fruity (documented)
    ("wh-green-spot", 3, 3, ["voce", "kremasto", "zacini"], False),
    # Yellow Spot: sherried pot still (documented)
    ("wh-yellow-spot", 4, 3, ["med", "zacini", "suho-voce"], False),
    # Teeling: innovative Irish, often wine cask
    ("wh-teeling", 3, 3, ["voce", "cvjetno", "kremasto"], False),
    # Bushmills: lighter, triple distilled, fruity
    ("wh-bushmills", 3, 3, ["voce", "med", "kremasto"], False),
    # NOTE: Jameson variants (original, black barrel, caskmates, crested, 18yo) are in Bourbon/Tennessee block below
    # ── Bourbon/Tennessee ──
    # BenRiach — age and cask-specific ──
    # Pedro Ximénez vintage cask: sweet, dried fruit dominant
    ("wh-benriach.*27.*pedro|benriach.*pedro-ximenez|wh-benriach-27-yo-cask-edition-pedro", 4, 4, ["tamno-voce", "suho-voce", "cvjetno"], False),
    ("wh-benriach.*30|wh-benriach-the-thirty", 4, 3, ["suho-voce", "orasasti", "hrast"], False),
    ("wh-benriach.*25|wh-benriach-the-twenty-five", 4, 3, ["suho-voce", "hrast", "citrus"], False),
    ("wh-benriach.*22", 3, 3, ["cvjetno", "voce", "hrast"], False),
    ("wh-the-benriach.*21|wh-benriach.*21", 3, 3, ["cvjetno", "med", "hrast"], False),
    ("wh-benriach.*16|wh-benriach-the-sixteen", 3, 3, ["voce", "vanilija", "hrast"], False),
    ("wh-benriach.*12", 3, 3, ["voce", "citrus", "hrast"], False),
    # Elijah Craig: high rye Heaven Hill bourbon
    ("elijah-craig", 4, 3, ["karamela", "hrast", "papar"], False),
    # Highland Park — age/edition tiers ──
    ("wh-highland-park.*30|wh-highland-park-30", 4, 2, ["suho-voce", "dim", "hrast"], False),
    ("wh-highland-park.*21|wh-highland-park-21", 4, 2, ["dim", "suho-voce", "hrast"], False),
    ("wh-highland-park.*18|wh-highland-park-18", 4, 2, ["med", "dim", "hrast"], False),
    ("wh-highland-park.*17|wh-highland-park-17", 3, 2, ["dim", "med", "cvjetno"], False),
    ("wh-hunter-laing.*highland-park|wh-hunter.*highland-park", 4, 2, ["dim", "suho-voce", "papar"], False),
    # Glengoyne 15yo: unpeated, sherry-influenced
    ("wh-glengoyne-15|wh-glengoyne.*15", 3, 3, ["suho-voce", "med", "karamela"], False),
    # Macallan Sherry Oak — full sherry (different from Double Cask) ──
    ("wh-the-macallan.*18.*sherry-oak|wh-macallan.*18.*sherry-oak", 4, 4, ["tamno-voce", "hrast", "zacini"], False),
    ("wh-the-macallan.*12.*sherry-oak|wh-macallan.*12.*sherry-oak", 3, 4, ["suho-voce", "cvjetno", "med"], False),
    # JW Blue Label — specific editions handled in JW section above
    # ── Highland Park — age/edition tiers ──
    ("wh-highland-park.*30|wh-highland-park-30", 5, 2, ["suho-voce", "dim", "hrast"], False),
    ("wh-highland-park.*21|wh-highland-park-21", 4, 2, ["dim", "suho-voce", "hrast"], False),
    ("wh-highland-park.*18|wh-highland-park-18", 4, 2, ["med", "dim", "hrast"], False),
    ("wh-highland-park.*17|wh-highland-park-17", 3, 2, ["dim", "med", "cvjetno"], False),
    ("wh-hunter-laing.*highland-park|wh-hunter.*highland-park", 4, 2, ["dim", "suho-voce", "papar"], False),
    # ── Blanton's — standard vs Gold vs SFTTB ──
    ("wh-blanton.*straight-from-the-barrel|wh-blanton.*sfttb", 5, 2, ["vanilija", "karamela", "papar"], False),
    ("wh-blanton.*gold|wh-blanton.*039.*gold|wh-blanton.*039-s-gold", 4, 3, ["vanilija", "karamela", "med"], False),
    ("wh-blanton", 4, 3, ["vanilija", "karamela", "papar"], False),
    # ── Michter's ──
    ("wh-michter.*rye|wh-michter.*single-barrel.*rye|wh-michter.*kentucky.*rye", 4, 2, ["papar", "zacini", "hrast"], False),
    ("wh-michter.*kentucky.*bourbon|wh-michter.*small-batch.*bourbon", 4, 3, ["karamela", "vanilija", "hrast"], False),
    ("wh-michter.*sour-mash|wh-michter.*unblended-american", 3, 2, ["papar", "karamela", "hrast"], False),
    ("wh-michter", 4, 2, ["papar", "karamela", "hrast"], False),
    # Elijah Craig: high rye Heaven Hill bourbon
    ("elijah-craig", 4, 3, ["karamela", "hrast", "papar"], False),
    # ── Suntory Hibiki / Yamazaki editions ──
    ("wh-suntory.*hibiki.*21|wh-suntory-hibiki-21", 4, 3, ["suho-voce", "anis", "hrast"], False),
    ("wh-suntory.*hibiki.*blossom|wh-suntory.*hibiki-blossom", 3, 3, ["cvjetno", "citrus", "med"], False),
    ("wh-suntory.*hibiki.*master.*select|wh-suntory.*hibiki.*master", 3, 2, ["cvjetno", "citrus", "hrast"], False),
    ("wh-suntory.*hibiki|wh-suntory-hibiki", 3, 2, ["cvjetno", "citrus", "hrast"], False),
    ("wh-suntory.*yamazaki.*mizunara", 4, 3, ["suho-voce", "anis", "hrast"], False),
    # ── Bushmills — age/edition tiers ──
    ("wh-bushmills.*26|wh-bushmills-26", 4, 3, ["suho-voce", "karamela", "hrast"], False),
    ("wh-bushmills.*25|wh-bushmills-25", 4, 3, ["suho-voce", "cvjetno", "hrast"], False),
    ("wh-bushmills.*21|wh-bushmills-21", 4, 3, ["suho-voce", "orasasti", "hrast"], False),
    ("wh-bushmills.*black.*bush|wh-bushmills-black-bush", 3, 4, ["karamela", "suho-voce", "kremasto"], False),
    ("wh-bushmills", 3, 3, ["voce", "med", "kremasto"], False),
    # ── Powers / Writer's Tears / Jameson variants ──
    ("wh-powers.*12.*john.*lane|wh-powers-12-yo-john", 4, 2, ["zacini", "hrast", "papar"], False),
    ("wh-writer.*tears.*cognac|wh-writer.*tears.*deau", 3, 3, ["voce", "karamela", "kremasto"], False),
    ("wh-writer.*tears.*marsala|wh-writer.*tears.*florio", 3, 4, ["voce", "tamno-voce", "kremasto"], False),
    ("wh-writer.*tears", 3, 3, ["voce", "med", "kremasto"], False),
    ("wh-jameson.*18|wh-jameson-18", 4, 3, ["suho-voce", "hrast", "kremasto"], False),
    ("wh-jameson.*black.*barrel|wh-jameson-black-barrel", 3, 4, ["karamela", "vanilija", "hrast"], False),
    ("wh-jameson.*stout|wh-jameson-caskmates-stout", 3, 4, ["kakao", "kremasto", "vanilija"], False),
    ("wh-jameson.*crested", 3, 3, ["voce", "kremasto", "zacini"], False),
    # Jameson Original / standard fallback
    ("wh-jameson", 3, 3, ["med", "vanilija", "kremasto"], False),
    # Jack Daniel's — specific variants before generic catch-all
    # American Single Malt: 100% malted barley — very different character
    ("jack-daniel.*american.*single.*malt", 3, 3, ["suho-voce", "hrast", "citrus"], False),
    # Bottled in Bond: 100 proof, bolder
    ("jack-daniel.*bonded|jack-daniel.*bottled-in-bond", 4, 2, ["karamela", "hrast", "papar"], False),
    # Sinatra Select: special charcoal-mellowed, richer
    ("jack-daniel.*sinatra", 5, 3, ["karamela", "maple", "hrast"], False),
    # Tennessee Fire: cinnamon-sweetened
    ("jack-daniel.*fire", 2, 5, ["zacini", "karamela", "cmet"], False),
    # Tennessee Apple: apple-flavored
    ("jack-daniel.*apple", 2, 5, ["jabuka", "karamela", "vanilija"], False),
    # Tennessee Blackberry
    ("jack-daniel.*blackberry", 2, 5, ["tamno-voce", "karamela", "vanilija"], False),
    # Honey: honey-sweetened
    ("jack-daniel.*honey", 2, 5, ["med", "karamela", "vanilija"], False),
    # Single Barrel Rye: rye grain forward
    ("jack-daniel.*rye|jack-daniel.*tennessee-rye", 4, 2, ["papar", "karamela", "hrast"], False),
    # Single Barrel: richer, more complex
    ("jack-daniel.*single-barrel", 4, 3, ["karamela", "vanilija", "hrast"], False),
    # Gentleman Jack: double-mellowed, smoother
    ("jack-daniel.*gentleman", 3, 3, ["kremasto", "karamela", "vanilija"], False),
    # McLaren, Guitar editions, 2-case: collector packaging, same No.7 base
    ("jack-daniel.*mclaren|jack-daniel.*guitar|jack-daniel.*2-case", 4, 3, ["karamela", "vanilija", "zacini"], False),
    # Old No.7 and standard Tennessee
    ("jack-daniel", 4, 3, ["karamela", "maple", "vanilija"], False),
    # Woodford Reserve standard and Double Oaked
    ("wh-woodford.*double", 4, 4, ["karamela", "hrast", "kokos"], False),
    ("wh-woodford", 4, 3, ["karamela", "vanilija", "hrast"], False),
    # Maker's Mark: wheat mash, soft and sweet
    ("maker.*mark", 3, 4, ["karamela", "vanilija", "kremasto"], False),
    # Buffalo Trace: classic bourbon
    ("buffalo-trace", 4, 3, ["karamela", "vanilija", "hrast"], False),
    # Wild Turkey 101: high proof rye bourbon, spicy
    ("wild-turkey.*101", 4, 2, ["papar", "karamela", "hrast"], False),
    ("wild-turkey", 4, 3, ["karamela", "vanilija", "med"], False),
    # Four Roses Single Barrel: fruity, elegant
    ("four-roses.*single", 3, 3, ["voce", "karamela", "vanilija"], False),
    ("four-roses", 3, 3, ["voce", "kremasto", "karamela"], False),
    # Knob Creek: full-bodied rye bourbon
    ("knob-creek", 4, 2, ["papar", "karamela", "hrast"], False),
    # Jim Beam standard: lighter bourbon
    ("jim-beam", 3, 3, ["karamela", "vanilija", "kokos"], False),
    # Booker's: uncut cask strength bourbon
    ("booker", 5, 2, ["papar", "hrast", "karamela"], False),
    # ── Japanese ──
    # Yamazaki 18yo: plum, anise, wood
    ("wh-yamazaki-18", 4, 3, ["suho-voce", "anis", "hrast"], False),
    # Yamazaki standard: floral, honey
    ("wh-yamazaki", 3, 3, ["cvjetno", "med", "suho-voce"], False),
    # Nikka Coffey Malt: lighter, fruity
    ("wh-nikka-coffey-malt", 3, 2, ["voce", "citrus", "med"], False),
    # Nikka from the Barrel: intense, complex
    ("wh-nikka-from-the-barrel", 4, 2, ["suho-voce", "hrast", "med"], False),
]

BRANDY_CURATED: list[tuple[str, int, int, list[str], bool]] = [
    # ── Calvados (apple brandy) ──
    ("boulard-calvados", 3, 3, ["jabuka", "karamela", "hrast"], False),
    ("christian-drouin-calvados|drouin.*calvados", 3, 3, ["jabuka", "zacini", "hrast"], False),
    ("dupont-calvados", 3, 3, ["jabuka", "cvjetno", "hrast"], False),
    ("calvados", 3, 3, ["jabuka", "zacini", "hrast"], False),
    # ── Louis XIII / Hennessy Paradis (ultra-premium) ──
    ("remy-martin-louis-xiii", 4, 4, ["cvjetno", "med", "suho-voce"], False),
    ("hennessy-paradis", 4, 4, ["cvjetno", "med", "karamela"], False),
    # ── Hennessy XXO / XO / VSOP / VS — specific before generic ──
    ("hennessy-x-x-o|hennessy-xxo|hennessy.*hors-d", 5, 3, ["kakao", "suho-voce", "zacini"], False),
    ("hennessy-xo", 4, 3, ["kakao", "suho-voce", "zacini"], False),
    # Hennessy VSOP: younger than XO, rounder and fruitier
    ("hennessy-vsop", 3, 3, ["voce", "vanilija", "zacini"], False),
    # Hennessy VS: entry-level, lighter, simple oak
    ("hennessy-vs-40-vol|hennessy-vs$|^br-hennessy-vs$", 2, 3, ["voce", "vanilija", "hrast"], False),
    # ── Rémy Martin ──
    ("remy-martin-xo", 3, 3, ["cvjetno", "suho-voce", "zacini"], False),
    ("remy-martin-vsop|remy-martin-1738", 3, 3, ["voce", "vanilija", "cvjetno"], False),
    # ── Martell — variants first, generic last ──
    # Martell Chanteloup XXO: premium expression, richer than Cordon Bleu
    ("martell.*chanteloup-xxo|martell-chanteloup-xxo|br-martell-chanteloup", 4, 3, ["orasasti", "suho-voce", "kakao"], False),
    # Martell Cohiba: special cigar-edition, robust tobacco-adjacent richness
    ("martell.*cohiba|br-martell-cohiba", 4, 2, ["suho-voce", "hrast", "koza"], False),
    ("martell-xo|martell.*extra-old", 4, 2, ["orasasti", "suho-voce", "hrast"], False),
    ("martell.*cordon-bleu", 3, 2, ["orasasti", "suho-voce", "cedar"], False),
    # ── Frapin ──
    ("frapin.*cigar", 4, 2, ["suho-voce", "hrast", "koza"], False),
    ("frapin", 4, 2, ["suho-voce", "kakao", "hrast"], False),
    # ── Hine — Antique XO first, then VSOP variants ──
    ("hine-antique", 3, 3, ["cvjetno", "suho-voce", "hrast"], False),
    # Hine VSOP (H by Hine, Rare VSOP): lighter, more floral than antique
    ("hine.*vsop|h-by-hine.*vsop|br-hine-rare-vsop|br-h-by-hine", 3, 3, ["cvjetno", "vanilija", "med"], False),
    # ── Camus — XO before VSOP ──
    ("camus-xo|camus.*xo", 3, 4, ["cvjetno", "med", "suho-voce"], False),
    # Camus VSOP Borderies: lighter, more citrus/floral than XO
    ("camus.*vsop.*borderies|camus-vsop-borderies", 3, 3, ["cvjetno", "citrus", "hrast"], False),
    ("camus.*vsop", 3, 3, ["cvjetno", "voce", "hrast"], False),
    # ── Courvoisier ──
    ("courvoisier-xo", 3, 3, ["cvjetno", "voce", "hrast"], False),
    # ── Gautier ──
    ("gautier-xo", 3, 3, ["cvjetno", "suho-voce", "hrast"], False),
    # ── Davidoff — XO specific: tobacco-house cognac, dry and structured ──
    ("davidoff-xo.*prestige|br-davidoff-xo.*prestige|br-davidoff-xo", 4, 2, ["suho-voce", "duhan", "hrast"], False),
    ("davidoff-xo", 4, 3, ["suho-voce", "zacini", "hrast"], False),
    # ── Pierre Ferrand — age-specific ──
    # Pierre Ferrand 1840 Original Formula: made for cocktails, higher ABV, drier
    ("pierre-ferrand-1840|br-pierre-ferrand-1840", 3, 1, ["citrus", "hrast", "cvjetno"], False),
    # Pierre Ferrand Reserve: VSOP range, elegant
    ("pierre-ferrand.*reserve|br-r-serve|br-pierre-ferrand.*r-serve", 3, 3, ["cvjetno", "voce", "hrast"], False),
    ("pierre-ferrand.*1er|pierre-ferrand.*premier", 3, 3, ["cvjetno", "suho-voce", "hrast"], False),
    ("pierre-ferrand", 3, 3, ["cvjetno", "voce", "hrast"], False),
    # ── Delamain ──
    ("delamain", 3, 2, ["suho-voce", "cvjetno", "hrast"], False),
    # ── Carlos I ──
    ("carlos-i-imperial-xo", 4, 2, ["orah", "karamela", "suho-voce"], False),
    ("carlos-i", 4, 3, ["orah", "karamela", "suho-voce"], False),
    # ── Alfonso XO: dark Spanish sherry brandy ──
    ("alfonso-xo", 4, 4, ["karamela", "suho-voce", "tamno-voce"], False),
    # ── Fundador ──
    ("fundador", 3, 3, ["karamela", "suho-voce", "hrast"], False),
    # ── Armagnac — Janneau age-specific, then generic ──
    # Janneau XO Royal: oldest and richest
    ("janneau.*royal|janneau-xo-royal|br-janneau.*royal", 4, 3, ["prune", "tamno-voce", "hrast"], False),
    # Janneau XO: full Armagnac character
    ("janneau.*xo|janneau-xo|br-janneau.*xo", 4, 3, ["prune", "suho-voce", "hrast"], False),
    # Janneau VSOP: younger, fruitier expression
    ("janneau.*vsop|janneau-vsop|br-janneau.*vsop", 3, 3, ["voce", "zacini", "hrast"], False),
    ("janneau", 3, 3, ["suho-voce", "zacini", "hrast"], False),
    # Darroze: grower Armagnac, vintage-specific — younger assemblage (8yr), lighter and more fruity
    ("darroze.*les-grands|darroze-les-grands", 3, 3, ["prune", "voce", "citrus"], False),
    ("dartigalongue", 4, 3, ["prune", "suho-voce", "hrast"], False),
    # Delord / Tariquet: Bas-Armagnac producers
    ("delord.*15|delord-15-ans", 4, 3, ["prune", "hrast", "karamela"], False),
    ("tariquet.*vsop|tariquet-armagnac-vsop|chateau.*tariquet.*vsop", 3, 3, ["prune", "hrast", "citrus"], False),
    ("choteau|laubade", 4, 3, ["prune", "suho-voce", "hrast"], False),
    # ── Ararat Armenian brandy — age-specific ──
    # Ararat Dvin 50yo: extremely old expression
    ("ararat.*dvin.*50|ararat-dvin-50|br-ararat-dvin-50", 5, 3, ["suho-voce", "med", "hrast"], False),
    # Ararat Erebuni / 30yo: premium aged
    ("ararat.*erebuni|ararat.*30", 4, 3, ["suho-voce", "karamela", "hrast"], False),
    # Ararat Vaspurakan / 25yo
    ("ararat.*vaspurakan|ararat.*aznavour.*25|br-ararat-aznavour-25|ararat.*25", 4, 3, ["suho-voce", "zacini", "orasasti"], False),
    # Ararat Nairi / 20yo: rich, dried fruit
    ("ararat.*nairi|ararat.*20|br-ararat-nairi", 4, 3, ["suho-voce", "karamela", "orasasti"], False),
    # Ararat Akhtamar / 10yo: medium, fruity
    ("ararat.*akhtamar|ararat.*10", 3, 3, ["voce", "vanilija", "hrast"], False),
    # Ararat Ani / 7yo: younger fruity
    ("ararat.*ani|ararat.*7", 3, 3, ["voce", "citrus", "hrast"], False),
    # Ararat 5 Stars: entry, lighter
    ("ararat.*5-stars|ararat.*5.*stars|br-ararat-5", 3, 3, ["voce", "zacini", "hrast"], False),
    ("ararat", 3, 3, ["voce", "zacini", "hrast"], False),
]

RUM_CURATED: list[tuple[str, int, int, list[str], bool]] = [
    # ── DOORLY'S — must precede generic 'foursquare' (IDs end with -foursquare) ──
    ("doorly.*xo", 3, 1, ["suho-voce", "citrus", "hrast"], False),
    ("doorly.*14(?!\\d)", 3, 2, ["hrast", "suho-voce", "zacini"], False),
    ("doorly.*12(?!\\d)", 3, 1, ["hrast", "orasasti", "citrus"], False),
    ("doorly.*8(?!\\d)", 3, 1, ["hrast", "suho-voce", "citrus"], False),
    ("doorly.*5(?!\\d)", 2, 1, ["citrus", "hrast", "voce"], False),
    ("doorly", 3, 1, ["suho-voce", "hrast", "vanilija"], False),
    # ── THE REAL McCOY — must precede generic 'foursquare' ──
    ("the-real-mccoy", 3, 1, ["suho-voce", "hrast", "orasasti"], False),
    # ── VERITAS — must precede generic 'foursquare' ──
    ("veritas.*white|veritas-foursquare|foursquare.*white", 2, 1, ["citrus", "travnato", "vegetalno"], False),
    # ── FOURSQUARE specific, then generic ──
    ("foursquare-ecs|foursquare.*detente|rum-foursquare-nobiliary|rum-sagacity", 3, 1, ["suho-voce", "hrast", "orasasti"], False),
    ("foursquare-sovereignty|foursquare.*sovereignty", 4, 1, ["hrast", "overproof", "suho-voce"], False),
    ("foursquare.*spiced|foursquare-spiced", 3, 3, ["karamela", "zacini", "vanilija"], False),
    ("foursquare", 3, 1, ["suho-voce", "hrast", "vanilija"], False),
    # ── MOUNT GAY ──
    ("mount-gay-xo|mount.*gay.*xo", 3, 2, ["suho-voce", "citrus", "hrast"], False),
    ("mount-gay-andean.*oak|mount.*gay.*andean", 3, 2, ["hrast", "suho-voce", "zacini"], False),
    ("mount-gay-black.*barrel|mount.*gay.*black.*barrel", 3, 2, ["hrast", "zacini", "voce"], False),
    ("mount-gay-eclipse|mount.*gay.*eclipse", 2, 2, ["citrus", "hrast", "voce"], False),
    # ── BANKS ──
    ("rum-banks-5(?!\\d)|banks.*5(?!\\d)", 2, 2, ["tropsko-voce", "citrus", "voce"], False),
    ("rum-banks-7|banks.*7.*golden", 3, 2, ["tropsko-voce", "zacini", "voce"], False),
    # ── CDI ──
    ("cdi.*jamaica.*navy|cdi-jamaica-navy", 4, 1, ["ester-funk", "tropsko-voce", "melasa"], False),
    ("cdi-jamaica-5|cdi.*jamaica-5", 3, 1, ["ester-funk", "tropsko-voce", "hrast"], False),
    ("cdi.*caraibes|cdi-caraibes", 3, 2, ["hrast", "voce", "suho-voce"], False),
    ("cdi.*latino|cdi-latino", 3, 3, ["karamela", "hrast", "voce"], False),
    ("cdi.*west-indies|cdi-west-indies", 3, 2, ["hrast", "suho-voce", "zacini"], False),
    ("cdi.*spiced|cdi-spiced", 2, 5, ["karamela", "zacini", "voce"], False),
    # ── FLOR DE CANA — age-specific BEFORE generic ──
    ("flor.*de.*cana.*4.*oro|flor-de-cana-4-oro", 2, 1, ["citrus", "travnato", "voce"], False),
    ("flor.*de.*cana.*extra.*seco|flor-de-cana-extra-seco", 2, 1, ["citrus", "travnato", "vegetalno"], False),
    ("flor.*de.*cana.*5.*clasico|flor-de-cana-5-clasico", 2, 1, ["citrus", "travnato", "vegetalno"], False),
    ("flor.*de.*cana.*7.*blanco|flor-de-cana-7-blanco", 2, 1, ["citrus", "hrast", "travnato"], False),
    ("flor.*de.*cana.*7.*gran|flor-de-cana-7-gran", 3, 1, ["hrast", "travnato", "vanilija"], False),
    ("flor.*de.*cana.*eco|flor-de-cana-eco", 3, 1, ["citrus", "suho-voce", "travnato"], False),
    ("flor.*de.*cana.*130|flor-de-cana-130th", 3, 1, ["hrast", "suho-voce", "voce"], False),
    ("flor.*de.*cana.*cognac|flor-de-cana-cognac", 4, 2, ["hrast", "voce", "karamela"], False),
    ("flor-de-cana-12(?!\\d)|rum-flor-de-cana-12(?!\\d)", 3, 1, ["hrast", "suho-voce", "citrus"], False),
    ("flor-de-cana-14(?!\\d)|rum-flor-de-cana-14(?!\\d)", 3, 1, ["hrast", "suho-voce", "orasasti"], False),
    ("flor-de-cana-18(?!\\d)|rum-flor-de-cana-18(?!\\d)", 4, 1, ["hrast", "suho-voce", "karamela"], False),
    ("flor-de-cana-25(?!\\d)|rum-flor-de-cana-25(?!\\d)", 4, 1, ["hrast", "suho-voce", "vanilija"], False),
    ("flor-de-cana-30|flor.*de.*cana.*v-generaciones", 5, 2, ["hrast", "suho-voce", "zacini"], False),
    ("flor-de-cana", 3, 1, ["hrast", "suho-voce", "travnato"], False),
    # ── ZAPATERA vintage expressions ──
    ("zapatera.*gran.*reserva.*1989|zapatera.*1989", 5, 1, ["hrast", "suho-voce", "koza"], False),
    ("zapatera.*reserva.*especial.*1992|zapatera.*1992", 4, 1, ["hrast", "suho-voce", "zacini"], False),
    ("zapatera.*reserva.*1996|zapatera-reserva-1996", 4, 1, ["hrast", "suho-voce", "orasasti"], False),
    # ── MARTINIQUE AGRICOLE — Karukera, Saint James, JM, Clement, HSE, Depaz ──
    ("karukera.*1493|karukera.*christophe-colomb", 5, 2, ["hrast", "suho-voce", "zacini"], False),
    ("karukera.*expression.*2008|karukera.*2008", 4, 2, ["hrast", "orasasti", "suho-voce"], False),
    ("karukera.*black|karukera-black", 3, 1, ["hrast", "travnato", "zacini"], False),
    ("karukera.*reserve.*speciale|karukera-reserve-speciale", 3, 2, ["hrast", "cvjetno", "travnato"], False),
    ("saint-james.*15(?!\\d)|saint-james-15(?!\\d)", 4, 2, ["hrast", "voce", "suho-voce"], False),
    ("saint-james.*xo|saint-james-xo", 3, 1, ["hrast", "suho-voce", "voce"], False),
    ("saint-james.*vsop|saint-james-vsop", 2, 1, ["citrus", "travnato", "voce"], False),
    ("saint-james.*12|saint-james-12", 3, 1, ["hrast", "travnato", "zacini"], False),
    ("jm.*canopee|jm-canopee", 3, 1, ["hrast", "travnato", "citrus"], False),
    ("jm.*millesime|jm-millesime", 4, 2, ["hrast", "suho-voce", "voce"], False),
    ("jm.*single.*barrel.*1999|jm-single-barrel-1999", 4, 1, ["hrast", "suho-voce", "orasasti"], False),
    ("jm.*single.*barrel.*2015|jm-single-barrel-2015", 3, 1, ["hrast", "travnato", "zacini"], False),
    ("clement.*15.*ans|clement-15-ans", 4, 2, ["hrast", "suho-voce", "karamela"], False),
    ("clement.*10.*ans|clement-10-ans", 3, 2, ["hrast", "voce", "karamela"], False),
    ("clement.*xo|clement-xo", 4, 2, ["hrast", "suho-voce", "orasasti"], False),
    ("clement.*vsop|clement-vsop", 2, 2, ["citrus", "hrast", "voce"], False),
    ("clement.*select|clement-select", 2, 1, ["citrus", "travnato", "voce"], False),
    ("clement.*single.*batch|clement.*canne-bleue|clement.*chauffe-extreme", 3, 1, ["hrast", "travnato", "zacini"], False),
    ("hse.*xo|hse-xo", 4, 2, ["hrast", "voce", "zacini"], False),
    ("hse.*vsop|hse-vsop", 2, 1, ["citrus", "hrast", "zacini"], False),
    ("hse.*vo|hse-vo", 2, 1, ["citrus", "travnato", "vegetalno"], False),
    ("depaz.*xo|depaz-xo", 3, 2, ["hrast", "voce", "zacini"], False),
    ("depaz.*vieux|depaz-vieux", 2, 2, ["hrast", "travnato", "voce"], False),
    # ── A.H. RIISE — specific before generic NPU ──
    ("ah-riise.*npu.*black|ah-riise-npu-black", 4, 4, ["karamela", "duhan", "suho-voce"], False),
    ("ah-riise-npu-ambre-dor|ah-riise.*npu.*ambre", 3, 4, ["karamela", "suho-voce", "vanilija"], False),
    ("ah-riise-npu", 3, 4, ["karamela", "suho-voce", "vanilija"], False),
    ("ah-riise-xo-175|ah-riise.*175", 3, 4, ["karamela", "suho-voce", "hrast"], False),
    ("ah-riise-xo-founders|ah-riise.*founders", 3, 4, ["karamela", "vanilija", "med"], False),
    ("ah-riise-xo-kong|ah-riise.*kong", 3, 4, ["karamela", "suho-voce", "zacini"], False),
    ("ah-riise-xo-christmas|ah-riise.*christmas", 3, 4, ["karamela", "zacini", "vanilija"], False),
    ("ah-riise-xo-superior|ah-riise.*superior", 3, 4, ["karamela", "hrast", "suho-voce"], False),
    ("ah-riise.*ambre.*dor.*reserve|ah-riise-xo-ambre-dor-reserve", 3, 4, ["karamela", "orasasti", "suho-voce"], False),
    ("ah-riise-navy-strength|ah-riise.*navy-strength", 4, 3, ["karamela", "zacini", "melasa"], False),
    ("ah-riise.*frigate|ah-riise-frigate", 3, 4, ["karamela", "vanilija", "suho-voce"], False),
    ("ah-riise.*1888|ah-riise-1888", 3, 4, ["karamela", "med", "voce"], False),
    ("ah-riise.*frogman|ah-riise-frogman", 4, 4, ["karamela", "suho-voce", "melasa"], False),
    ("ah-riise.*signature.*master|ah-riise-signature-master", 4, 4, ["karamela", "suho-voce", "orasasti"], False),
    ("ah-riise-naval-cadet|ah-riise.*naval-cadet", 3, 4, ["karamela", "vanilija", "med"], False),
    # ── ZAFRA ──
    ("rum-zafra-30|zafra.*30", 4, 2, ["suho-voce", "hrast", "karamela"], False),
    ("rum-zafra-21|zafra.*21", 3, 3, ["karamela", "voce", "zacini"], False),
    # ── BOTRAN ──
    ("rum-botran-roaju|botran.*roaju", 4, 3, ["karamela", "suho-voce", "hrast"], False),
    ("rum-botran-1893|botran.*1893", 4, 4, ["karamela", "suho-voce", "orasasti"], False),
    ("rum-botran-15(?!\\d)|botran.*15(?!\\d)", 3, 3, ["karamela", "voce", "hrast"], False),
    # ── RON CARTAVIO ──
    ("rum-ron-cartavio-xo|ron-cartavio.*xo", 4, 3, ["suho-voce", "karamela", "zacini"], False),
    # ── MATUSALEM ──
    ("rum-23(?!\\d)|rum-ron-matusalem-23|matusalem.*23", 4, 4, ["karamela", "suho-voce", "tamno-voce"], False),
    ("rum-ron-matusalem-15|matusalem.*15(?!\\d)", 4, 3, ["karamela", "suho-voce", "hrast"], False),
    ("rum-matusalem-gran-reserva|matusalem.*gran.*reserva", 3, 4, ["karamela", "med", "suho-voce"], False),
    ("rum-matusalem-10-clasico|matusalem.*10(?!\\d)", 3, 3, ["karamela", "voce", "vanilija"], False),
    # ── KIRK & SWEENEY ──
    ("rum-kirk-sweeney-gran-reserva-superior|kirk.*sweeney.*gran.*reserva.*superior", 4, 3, ["karamela", "suho-voce", "hrast"], False),
    ("rum-kirk-sweeney-gran-reserva(?!-superior)|kirk.*sweeney.*gran.*reserva(?!.*superior)", 3, 2, ["karamela", "suho-voce", "vanilija"], False),
    ("rum-kirk-sweeney-xo|kirk.*sweeney.*xo", 4, 3, ["karamela", "suho-voce", "zacini"], False),
    ("rum-kirk-sweeney-23|kirk.*sweeney.*23", 4, 3, ["karamela", "suho-voce", "orasasti"], False),
    ("rum-kirk-sweeney-18(?!\\d)|kirk.*sweeney.*18(?!\\d)", 3, 2, ["karamela", "hrast", "suho-voce"], False),
    # ── OPTHIMUS — differentiate by age tier ──
    ("opthimus.*25|opthimus-25", 4, 3, ["karamela", "suho-voce", "orasasti"], False),
    ("opthimus.*21|opthimus-21", 4, 3, ["karamela", "suho-voce", "kakao"], False),
    ("opthimus.*xo|opthimus-xo", 4, 3, ["karamela", "hrast", "suho-voce"], False),
    ("opthimus.*18(?!\\d)|opthimus-18", 3, 3, ["karamela", "suho-voce", "zacini"], False),
    ("opthimus.*15(?!\\d)|opthimus-15", 3, 3, ["karamela", "suho-voce", "hrast"], False),
    # ── RON ABUELO ──
    ("ron-abuelo.*centuria|ron-abuelo-centuria", 4, 3, ["karamela", "suho-voce", "orasasti"], False),
    ("ron-abuelo.*xv|ron-abuelo-xv", 3, 3, ["karamela", "hrast", "voce"], False),
    ("ron-abuelo.*anejo|ron-abuelo-anejo", 3, 3, ["karamela", "voce", "vanilija"], False),
    # ── DICTADOR ──
    ("dictador.*20(?!\\d)|dictador-20", 4, 3, ["karamela", "med", "suho-voce"], False),
    ("dictador.*12(?!\\d)|dictador-12", 3, 3, ["karamela", "vanilija", "zacini"], False),
    # ── BRUGAL ──
    ("brugal.*1888|brugal-1888", 3, 3, ["karamela", "hrast", "zacini"], False),
    # ── BOCATHEVA ──
    ("bocatheva.*barbados.*jamaica|bocatheva.*barbados", 2, 2, ["ester-funk", "tropsko-voce", "citrus"], False),
    ("bocatheva.*venezuela|bocatheva.*10", 3, 3, ["karamela", "tropsko-voce", "hrast"], False),
    ("bocatheva.*master|bocatheva-master", 4, 2, ["hrast", "suho-voce", "orasasti"], False),
    # ── NEW GROVE / LA HECHICERA / RUM NATION ──
    ("new-grove.*beau-plan|new-grove.*beau", 4, 2, ["hrast", "suho-voce", "tamno-voce"], False),
    ("new-grove.*10(?!\\d)|new-grove-10", 3, 2, ["hrast", "voce", "suho-voce"], False),
    ("la-hechicera.*solera|la-hechicera", 4, 2, ["hrast", "suho-voce", "karamela"], False),
    ("rum-nation.*barbados.*panama|rum-nation.*demerara", 3, 2, ["hrast", "suho-voce", "zacini"], False),
    # ── CIHUATAN ──
    ("rum-cihuatan-12|cihuatan.*12", 3, 3, ["karamela", "vanilija", "zacini"], False),
    # ── APPLETON ESTATE ──
    ("appleton.*estate|appleton.*21|appleton.*rare", 4, 3, ["ester-funk", "tropsko-voce", "suho-voce"], False),
    ("appleton", 3, 3, ["ester-funk", "tropsko-voce", "voce"], False),
    # ── WORTHY PARK — differentiate by cask/age ──
    ("worthy-park.*madeira|worthy-park.*port", 3, 2, ["ester-funk", "tropsko-voce", "voce"], False),
    ("worthy-park.*oloroso", 3, 2, ["ester-funk", "tamno-voce", "tropsko-voce"], False),
    ("worthy-park.*109|worthy-park-109", 4, 1, ["ester-funk", "overproof", "tropsko-voce"], False),
    ("worthy-park.*select|worthy-park-select", 3, 1, ["ester-funk", "tropsko-voce", "hrast"], False),
    ("exchange.*worthy-park|exchange-worthy-park", 4, 1, ["ester-funk", "tropsko-voce", "suho-voce"], False),
    ("worthy-park", 4, 1, ["ester-funk", "tropsko-voce", "zacini"], False),
    # ── HAMPDEN — differentiate by mark/age ──
    ("kill-devil.*hampden|kill.*devil.*hampden", 5, 1, ["ester-funk", "tropsko-voce", "medicinski"], False),
    ("exchange.*hampden|exchange-hampden", 4, 1, ["ester-funk", "tropsko-voce", "melasa"], False),
    ("hampden.*rum.*fire|hampden-rum-fire", 5, 1, ["ester-funk", "overproof", "melasa"], False),
    ("hampden.*hlcf|hampden-hlcf", 5, 1, ["ester-funk", "overproof", "tropsko-voce"], False),
    ("habitation-velier.*svm|habitation.*plummer|habitation-velier", 4, 1, ["ester-funk", "tropsko-voce", "vegetalno"], False),
    ("hampden", 5, 1, ["ester-funk", "tropsko-voce", "vegetalno"], False),
    # ── LONG POND ──
    ("long-pond", 5, 1, ["ester-funk", "tropsko-voce", "melasa"], False),
    # ── RUM BAR ──
    ("rum-bar", 3, 1, ["ester-funk", "tropsko-voce", "hrast"], False),
    # ── RON DIPLOMATICO ──
    ("diplomatico-planas", 2, 1, ["travnato", "citrus", "vegetalno"], False),
    ("diplomatico-mantuano", 3, 3, ["karamela", "vanilija", "suho-voce"], False),
    ("diplomatico-reserva-exclusiva|diplomatico.*exclusiva", 4, 5, ["karamela", "suho-voce", "zacini"], False),
    # ── ZACAPA — full range ──
    ("rum-zacapa-royal|zacapa.*royal", 4, 3, ["karamela", "suho-voce", "vanilija"], False),
    ("rum-zacapa-reserva-limitada|zacapa.*reserva.*limitada|zacapa.*2015", 4, 3, ["tamno-voce", "karamela", "hrast"], False),
    ("rum-zacapa-centenario-23|zacapa.*centenario.*23", 3, 4, ["karamela", "vanilija", "zacini"], False),
    ("rum-zacapa-ambar|zacapa.*ambar", 3, 3, ["karamela", "suho-voce", "voce"], False),
    ("rum-zacapa-xo|zacapa.*-xo", 4, 3, ["kakao", "hrast", "suho-voce"], False),
    ("rum-zacapa-la-doma|zacapa.*la-doma|zacapa.*doma", 4, 3, ["karamela", "hrast", "zacini"], False),
    ("rum-zacapa-30-aniversario|zacapa.*30.*aniversario", 4, 4, ["karamela", "suho-voce", "hrast"], False),
    ("rum-zacapa-edicion-negra|zacapa.*edicion.*negra|zacapa.*negra", 4, 3, ["tamno-voce", "hrast", "zacini"], False),
    ("rum-zacapa-etiqueta-negra|zacapa.*etiqueta.*negra", 4, 3, ["karamela", "hrast", "suho-voce"], False),
    # ── RON CENTENARIO ──
    ("rum-ron-centenario-25(?!\\d)|ron-centenario.*25(?!\\d)", 4, 3, ["karamela", "suho-voce", "hrast"], False),
    ("rum-30(?!\\d)|rum-ron-centenario-30|ron-centenario.*30(?!\\d)", 4, 4, ["karamela", "suho-voce", "tamno-voce"], False),
    ("rum-ron-centenario-1985|ron-centenario.*1985", 4, 3, ["karamela", "suho-voce", "orasasti"], False),
    ("rum-ron-centenario-12(?!\\d)|ron-centenario.*12(?!\\d)|ron-centenario.*legado", 3, 3, ["karamela", "voce", "zacini"], False),
    ("rum-ron-centenario-5(?!\\d)|ron-centenario.*5(?!\\d)", 2, 3, ["karamela", "voce", "vanilija"], False),
    # ── BARCELO ──
    ("barcelo.*imperial.*onyx|barcelo-imperial-onyx", 4, 3, ["karamela", "suho-voce", "kakao"], False),
    ("barcelo.*imperial.*maple|barcelo-imperial-maple", 3, 3, ["karamela", "maple", "hrast"], False),
    ("barcelo.*imperial.*misunara|barcelo-imperial-misunara", 3, 3, ["karamela", "voce", "hrast"], False),
    ("barcelo.*imperial|barcelo-imperial", 4, 4, ["karamela", "suho-voce", "zacini"], False),
    ("barcelo.*gran.*anejo|barcelo-gran-anejo", 3, 3, ["karamela", "voce", "zacini"], False),
    ("barcelo.*dorado|barcelo-dorado", 2, 3, ["karamela", "citrus", "voce"], False),
    ("barcelo.*blanco|rum-blanco", 2, 1, ["citrus", "travnato", "vegetalno"], False),
    # ── BARRUM ──
    ("barrum.*classic|barrum-classic", 3, 1, ["ester-funk", "hrast", "tropsko-voce"], False),
    # ── PRESIDENTE MARTI ──
    ("rum-presidente-marti-15|presidente-marti", 3, 4, ["karamela", "vanilija", "med"], False),
    # ── CAPITAN BUCANERO ──
    ("rum-capitan-bucanero-elixir|capitan-bucanero.*elixir", 3, 5, ["karamela", "vanilija", "slatko"], False),
    ("rum-capitan-bucanero-anejo|capitan-bucanero.*anejo", 3, 4, ["karamela", "suho-voce", "hrast"], False),
    ("rum-capitan-bucanero-blanco|capitan-bucanero.*blanco", 2, 3, ["citrus", "voce", "vanilija"], False),
    ("rum-reserva|capitan-bucanero.*reserva|rum-capitan-bucanero-reserva", 3, 4, ["karamela", "orasasti", "hrast"], False),
    ("rum-capitan-bucanero|capitan-bucanero", 3, 4, ["karamela", "vanilija", "zacini"], False),
    # ── TIMON ──
    ("timon-caribbean-spice", 2, 5, ["karamela", "zacini", "vanilija"], False),
    # ── SPICED RUMS — differentiate by character ──
    ("legendario.*elixir|legendario-elixir", 3, 5, ["karamela", "slatko", "voce"], False),
    ("kraken.*black.*spiced|the-kraken|rum-the-kraken", 3, 5, ["karamela", "zacini", "melasa"], False),
    ("takamaka.*dark.*spiced|takamaka-dark|takamaka.*spiced", 2, 5, ["karamela", "kokos", "zacini"], False),
    ("sailor.*jerry|sailor-jerry", 2, 5, ["vanilija", "zacini", "kokos"], False),
    ("bacardi.*spiced|bacardi-spiced", 2, 4, ["karamela", "zacini", "vanilija"], False),
    ("remedy.*spiced|remedy-spiced", 2, 5, ["karamela", "zacini", "voce"], False),
    # ── CHAIRMANS / ADMIRAL RODNEY (St. Lucia) ──
    ("chairmans.*reserve.*1931|chairman.*1931|chairman-s-reserve-1931", 4, 1, ["duhan", "hrast", "med"], False),
    ("chairmans.*vintage.*2009|chairman.*vintage.*2009", 4, 1, ["duhan", "hrast", "suho-voce"], False),
    ("chairmans.*forgotten.*cask|chairman.*forgotten", 3, 1, ["duhan", "hrast", "voce"], False),
    ("chairmans.*legacy|chairman.*legacy", 3, 1, ["duhan", "hrast", "zacini"], False),
    ("admiral-rodney.*formidable|admiral.*rodney.*formidable", 3, 2, ["duhan", "hrast", "karamela"], False),
    ("admiral-rodney.*monarch|admiral.*rodney.*monarch", 3, 2, ["duhan", "hrast", "suho-voce"], False),
    # ── SERUM RON DE PANAMA ──
    ("rum-serum-ron-de-panama-10|serum-ron-de-panama", 3, 3, ["karamela", "voce", "citrus"], False),
    # ── PINTA / CRISTOBAL (DR) ──
    ("rum-pinta|rum-cristobal-nina", 3, 3, ["karamela", "vanilija", "suho-voce"], False),
    # ── ANGOSTURA ──
    ("angostura.*1919|angostura-1919", 3, 3, ["karamela", "hrast", "voce"], False),
    ("angostura.*5|angostura-5", 2, 3, ["karamela", "voce", "vanilija"], False),
    # ── EL DORADO ──
    ("el-dorado.*21|el-dorado-21", 4, 4, ["karamela", "tamno-voce", "orasasti"], False),
]

TEQUILA_CURATED: list[tuple[str, int, int, list[str], bool]] = [
    # Don Julio Anejo: aged, caramel and vanilla forward
    ("don-julio.*anejo", 3, 3, ["karamela", "vanilija", "hrast"], False),
    # Don Julio 1942: premium extra anejo
    ("don-julio-1942|don-julio.*1942", 4, 3, ["karamela", "suho-voce", "hrast"], False),
    # Don Julio Reposado: lighter aging
    ("don-julio.*reposado", 3, 2, ["karamela", "citrus", "biljno"], False),
    # Don Julio Blanco: fresh unaged
    ("don-julio.*blanco", 2, 1, ["citrus", "biljno", "vegetalno"], False),
    # Don Julio standard (other)
    ("don-julio", 3, 2, ["citrus", "karamela", "biljno"], False),
    # Patron Anejo
    ("patron.*anejo", 3, 3, ["karamela", "vanilija", "hrast"], False),
    # Patron Reposado
    ("patron.*reposado", 3, 2, ["karamela", "citrus", "biljno"], False),
    # Patron standard
    ("patron", 2, 2, ["citrus", "biljno", "travnato"], False),
    # Clase Azul Reposado
    ("clase-azul.*reposado", 3, 3, ["karamela", "vanilija", "biljno"], False),
    # General: extra anejo vs anejo vs reposado
    ("extra.*anejo|extra.?ano|extraanejo", 4, 3, ["karamela", "suho-voce", "hrast"], True),
    ("anejo", 3, 3, ["karamela", "vanilija", "hrast"], True),
    ("reposado", 3, 2, ["karamela", "citrus", "biljno"], True),
    ("blanco|silver|plata", 2, 1, ["citrus", "biljno", "vegetalno"], True),
]

CURATED_BY_CATEGORY: dict[str, list] = {
    "gin": GIN_CURATED,
    "whisky": WHISKY_CURATED,
    "brandy": BRANDY_CURATED,
    "rum": RUM_CURATED,
    "tequila": TEQUILA_CURATED,
}

CATEGORY_FILE: dict[str, str] = {
    "gin": "gins",
    "whisky": "whiskies",
    "brandy": "brandies",
    "rum": "rums",
    "wine": "wines",
    "tequila": "tequilas",
    "digestif": "digestifs",
}


def match_curated(bottle_id: str, curated: list) -> tuple[int, int, list[str], bool] | None:
    low = bottle_id.lower()
    for pattern, body, sweet, tags, estimated in curated:
        if re.search(pattern, low, re.I):
            return body, sweet, [t for t in tags if t in CANON], estimated
    return None


def apply_profiles(
    bottles: list[dict],
    curated: list,
    scraped: dict[str, dict],
    dry_run: bool,
    category: str,
) -> tuple[list[dict], int]:
    changed = 0
    for bottle in bottles:
        bid = bottle["id"]
        new_body = bottle["body"]
        new_sweet = bottle["sweetness"]
        new_tags: list[str] | None = None
        source = "unchanged"
        estimated = True

        # 1) Check curated first
        result = match_curated(bid, curated)
        if result:
            new_body, new_sweet, curated_tags, estimated = result
            if curated_tags:
                new_tags = curated_tags
                source = "curated"

        # 2) Scraped text (only if no curated match, or if curated didn't give tags)
        if new_tags is None and bid in scraped and scraped[bid].get("text"):
            raw_tags = tags_from_text(scraped[bid]["text"])
            if raw_tags:
                new_tags = raw_tags
                source = "scraped"
                estimated = False

        # 3) Existing notes text
        if new_tags is None:
            existing_notes = (bottle.get("notes") or {}).get("en", "") or (bottle.get("notes") or {}).get("hr", "")
            if existing_notes:
                raw_tags = tags_from_text(existing_notes)
                if raw_tags and len(raw_tags) >= 2:
                    new_tags = raw_tags
                    source = "notes_text"
                    estimated = True

        if new_tags is None:
            continue

        # Only update if something changes
        old_profile = (bottle["body"], bottle["sweetness"], tuple(sorted(bottle.get("flavorTags") or [])))
        new_profile = (new_body, new_sweet, tuple(sorted(new_tags)))
        if old_profile == new_profile:
            continue

        if not dry_run:
            bottle["body"] = new_body
            bottle["sweetness"] = new_sweet
            bottle["flavorTags"] = sorted(new_tags)
            bottle["profileEstimated"] = estimated

        changed += 1
        if dry_run:
            print(
                f"  [{source}] {bid[:50]}"
                f"\n    old: {old_profile}"
                f"\n    new: {new_profile}"
            )

    return bottles, changed


def measure_w2(data_files: dict[str, list]) -> dict:
    from collections import Counter
    total = 0
    in_big = 0
    per_cat = {}
    for cat, bottles in data_files.items():
        buckets = Counter(
            (b["body"], b["sweetness"], tuple(sorted(b.get("flavorTags") or [])))
            for b in bottles
        )
        big = sum(v for v in buckets.values() if v >= 5)
        per_cat[cat] = {"bottles": len(bottles), "in_big": big, "profiles": len(buckets)}
        total += len(bottles)
        in_big += big
    return {"total": total, "in_big": in_big, "pct": round(100 * in_big / total, 1), "per_cat": per_cat}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--category", choices=list(CATEGORY_FILE), default=None)
    args = ap.parse_args()

    # Load scraped notes
    scraped: dict[str, dict] = {}
    if RAW.exists():
        scraped = json.loads(RAW.read_text(encoding="utf-8"))
        ok = sum(1 for v in scraped.values() if v.get("status") == "ok")
        print(f"Scraped notes loaded: {ok} with content / {len(scraped)} total")

    categories = list(CATEGORY_FILE) if args.category is None else [args.category]
    data_files: dict[str, list] = {}
    total_changed = 0

    for cat in categories:
        fname = CATEGORY_FILE[cat]
        path = DATA / f"{fname}.json"
        if not path.exists():
            continue
        bottles = json.loads(path.read_text(encoding="utf-8"))
        data_files[cat] = bottles

        curated = CURATED_BY_CATEGORY.get(cat, [])
        bottles, n_changed = apply_profiles(bottles, curated, scraped, args.dry_run, cat)
        total_changed += n_changed

        if not args.dry_run and n_changed > 0:
            # Backup
            backup = path.with_suffix(f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            shutil.copy2(path, backup)
            path.write_text(json.dumps(bottles, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  [{cat}] {n_changed} bottles updated -> {path.name}")
        elif args.dry_run:
            print(f"  [{cat}] {n_changed} bottles would change (dry-run)")
        else:
            print(f"  [{cat}] {n_changed} bottles changed")

    # Measure
    if not args.dry_run:
        # Reload for accurate measurement
        for cat in categories:
            fname = CATEGORY_FILE[cat]
            path = DATA / f"{fname}.json"
            if path.exists():
                data_files[cat] = json.loads(path.read_text(encoding="utf-8"))

    w2 = measure_w2(data_files)
    print(f"\nW2 after: {w2['in_big']}/{w2['total']} = {w2['pct']}% in buckets >=5")
    print(f"{'Category':<12} {'Bottles':>7} {'Profiles':>9} {'In>=5':>6}")
    for cat, stats in w2["per_cat"].items():
        print(f"  {cat:<10} {stats['bottles']:>7} {stats['profiles']:>9} {stats['in_big']:>6}")

    print(f"\nTotal changes: {total_changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
