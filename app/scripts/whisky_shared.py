# -*- coding: utf-8 -*-
"""Shared helpers for whisky catalog scrape, Excel build, and JSON export."""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Callable
from urllib.parse import urlparse

WHISKY_STOP = {
    "the", "of", "and", "yo", "vol", "old", "years", "year", "single", "malt",
    "scotch", "whisky", "whiskey", "giftbox", "gift", "box", "poklon", "kutiji",
    "u", "in", "gb", "limited", "edition", "batch", "bottle", "l",
}

ECUGA_CATEGORIES: list[tuple[str, str, str]] = [
    ("skotski-maltgrain-whisky", "Q2F0ZWdvcnk6MTM=", "Skotski malt/grain"),
    ("skotski-blended-whisky", "Q2F0ZWdvcnk6MTI=", "Skotski blended"),
    ("irski-whiskey", "Q2F0ZWdvcnk6OQ==", "Irska"),
    ("americki-bourbon-whiskey", "Q2F0ZWdvcnk6OA==", "Bourbon/Tennessee"),
    ("azijski-whisky", "Q2F0ZWdvcnk6MTA=", "Azija/Japan"),
    ("kanadski-whisky", "Q2F0ZWdvcnk6MTE=", "Kanada"),
    ("ostalo", "Q2F0ZWdvcnk6MzE=", "Europski/world"),
]

STYLE_RULES: list[tuple[str, str, str, int, int, list[str]]] = [
    (r"islay|ardbeg|laphroaig|lagavulin|bowmore|caol ila|kilchoman|octomore|bruichladdich", "islay-peated", "Islay, Škotska", 4, 1, ["dim", "iodin", "medicinski"]),
    (r"campbeltown|springbank|glengyle|kilkerran|longrow", "campbeltown", "Campbeltown, Škotska", 4, 2, ["dim", "sol", "slane"]),
    (r"peated|peat|torf|peated malt", "islay-peated", "Peated, Škotska", 4, 1, ["dim", "slane"]),
    (r"highland park|talisker|jura|highland(?! park)", "highland", "Highlands, Škotska", 3, 2, ["med", "hrast", "suho-voce"]),
    (r"speyside|glenlivet|glenfiddich|macallan|balvenie|glenfarclas|aberlour|glenrothes|cardhu|cragganmore", "speyside-fruity", "Speyside, Škotska", 3, 2, ["suho-voce", "med", "cvjetno"]),
    (r"sherry|pedro ximenez|oloroso|m PX|double cask|sherry cask|sherry finish", "speyside-sherry", "Sherry cask, Škotska", 4, 3, ["suho-voce", "kakao", "karamela"]),
    (r"blended scotch|johnnie walker|chivas|dewar|famous grouse|ballantine|teacher", "blended-scotch", "Blended, Škotska", 3, 2, ["karamela", "med", "vanilija"]),
    (r"bourbon|jim beam|maker'?s mark|buffalo trace|wild turkey|four roses|woodford|knob creek|booker", "bourbon", "Kentucky, SAD", 4, 3, ["karamela", "vanilija", "kokos"]),
    (r"tennessee|jack daniel", "tennessee", "Tennessee, SAD", 4, 3, ["karamela", "vanilija", "maple"]),
    (r"\brye\b|rye whiskey|bulleit rye|rittenhouse|pikesville", "rye", "Rye, SAD", 4, 2, ["papar", "karamela", "hrast"]),
    (r"irish|jameson|redbreast|green spot|yellow spot|bushmills|teeling|powers|writer", "irish-pot-still", "Irska", 3, 3, ["med", "vanilija", "kremasto"]),
    (r"single pot still|pot still", "irish-pot-still", "Irska pot still", 4, 3, ["med", "zacini", "kremasto"]),
    (r"japanese|japan|yamazaki|hakushu|nikka|yoichi|miyagikyo|chichibu|matsui|kavalan", "japanese", "Japan", 3, 2, ["cvjetno", "citrus", "hrast"]),
    (r"canadian|crown royal|canadian club", "canadian", "Kanada", 3, 2, ["karamela", "vanilija"]),
    (r"indian|amrut|paul john|-rampur", "world", "Indija", 3, 2, ["tropsko-voce", "zacini"]),
    (r"taiwan|kavalan", "world", "Tajvan", 3, 2, ["tropsko-voce", "suho-voce"]),
    (r"australian|starward", "world", "Australija", 3, 2, ["tropsko-voce", "karamela"]),
]

NON_PAIRABLE_EXPR = {"flavored", "rtd", "liqueur", "mixing"}
NON_PAIRABLE_STYLES: set[str] = set()

PREMIUM_BRANDS = {
    "macallan", "springbank", "lagavulin", "laphroaig", "highland park", "redbreast",
    "hibiki", "yamazaki", "pappy", "george t stagg", "booker's", "whistlepig",
    "glendronach", "glengoyne", "benriach", "kilchoman", "octomore", "ardbeg",
}

VALUE_BRANDS = {"glenlivet", "glenfiddich", "jameson", "famous grouse", "ballantine"}

FLAVORED_RE = re.compile(
    r"flavou?r|honey|fireball|apple|chocolate|liqueur|cocktail|rtd|old fashioned|"
    r"ginger beer|cola|spiced|sherry cask finish liqueur|sour mash liqueur",
    re.I,
)
RTD_RE = re.compile(r"cocktail|rtd|old fashioned|manhattan|highball|premix|#1|#2", re.I)


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text


def match_tokens(name: str) -> set[str]:
    toks = set(
        re.findall(
            r"[a-z0-9]+",
            unicodedata.normalize("NFKD", name.lower()).encode("ascii", "ignore").decode(),
        )
    )
    return {t for t in toks if t not in WHISKY_STOP and not (t.isdigit() and len(t) <= 2)}


def parse_price_eur(raw: Any) -> float | None:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    s = str(raw).replace("€", "").strip()
    nums = re.findall(r"\d+(?:[.,]\d+)?", s)
    if not nums:
        return None
    return float(nums[0].replace(",", "."))


def format_price_eur(value: float | None) -> str:
    if value is None:
        return "provjeriti"
    return f"{value:.2f} €".replace(".", ",")


def extract_abv(name: str) -> float | None:
    m = re.search(r"(\d{2}(?:[.,]\d+)?)\s*%\s*(?:Vol|vol)?", name)
    if m:
        return float(m.group(1).replace(",", "."))
    m = re.search(r"(\d{2}(?:[.,]\d+)?)\s*°", name)
    if m:
        return float(m.group(1).replace(",", "."))
    return None


def extract_age(name: str) -> int | None:
    m = re.search(r"\b(\d{1,2})\s*YO\b", name, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"\b(\d{1,2})\s*Years?\s*Old\b", name, re.I)
    if m:
        return int(m.group(1))
    return None


def detect_expression_type(name: str) -> str:
    low = name.lower()
    if RTD_RE.search(low):
        return "rtd"
    if FLAVORED_RE.search(low):
        return "flavored"
    if re.search(r"\brye\b", low):
        return "rye"
    if re.search(r"bourbon|tennessee", low):
        return "bourbon"
    if re.search(r"blended|blend", low):
        return "blend"
    if re.search(r"single malt|single pot still|pot still", low, re.I):
        return "single-malt"
    if re.search(r"grain whisky|grain whiskey", low, re.I):
        return "grain"
    return "whisky"


def normalize_region(region: str, style: str | None = None) -> str:
    """Strip legacy 'style / geo' prefix from region text."""
    r = (region or "").strip()
    if " / " not in r:
        return r
    left, right = r.split(" / ", 1)
    left, right = left.strip(), right.strip()
    if style and left == style:
        return right
    if "-" in left and " " not in left:
        return right
    geo_markers = (
        "škotska", "irska", "sad", "japan", "kanada", "orkney", "islay",
        "speyside", "highland", "kentucky", "tennessee", "tajvan", "taiwan",
        "india", "australija", "francuska", "njemačka",
    )
    if "," in right or any(m in right.lower() for m in geo_markers):
        return right
    return r


def detect_style_region(name: str, ecuga_category: str = "") -> tuple[str, str, int, int, list[str]]:
    text = f"{name} {ecuga_category}"
    for pattern, style, region, body, sweet, tags in STYLE_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return style, region, body, sweet, list(tags)
    if ecuga_category:
        for slug, _cid, label in ECUGA_CATEGORIES:
            if slug in ecuga_category.lower():
                style_map = {
                    "skotski-maltgrain": ("speyside-fruity", "Škotska"),
                    "skotski-blended": ("blended-scotch", "Škotska"),
                    "irski": ("irish-pot-still", "Irska"),
                    "bourbon": ("bourbon", "SAD"),
                    "azijski": ("japanese", "Japan"),
                    "kanadski": ("canadian", "Kanada"),
                }
                for key, (st, reg) in style_map.items():
                    if key in slug:
                        return st, reg, 3, 2, ["hrast", "karamela"]
    return "world", "World", 3, 2, ["hrast"]


def detect_coloring(name: str, style: str, expr: str) -> str:
    if expr in ("bourbon", "rye", "tennessee", "irish-pot-still", "single-malt", "japanese"):
        return "natural"
    if style == "blended-scotch":
        return "e150"
    if re.search(r"single malt|single pot", name, re.I):
        return "natural"
    return "unknown"


def detect_filter(name: str) -> str:
    if re.search(r"non.?chill|ncf|natural colour|unfiltrated|unfiltered", name, re.I):
        return "ncf"
    return "unknown"


def additive_status(coloring: str, expr: str) -> str:
    if expr in ("flavored", "rtd", "liqueur"):
        return "flavored"
    if coloring == "natural":
        return "clean"
    if coloring == "e150":
        return "moderate"
    return "unknown"


def estimate_quality(
    name: str,
    price: float | None,
    style: str,
    expr: str,
    abv: float | None,
    seed_score: float | None = None,
) -> float:
    if seed_score is not None:
        return seed_score
    if expr in NON_PAIRABLE_EXPR:
        return 3.5
    score = 5.5
    age = extract_age(name)
    if age:
        if age >= 18:
            score += 2.0
        elif age >= 15:
            score += 1.5
        elif age >= 12:
            score += 1.0
        elif age >= 10:
            score += 0.5
    low = name.lower()
    for brand in PREMIUM_BRANDS:
        if brand in low:
            score += 0.8
            break
    if abv and abv >= 55:
        score += 0.4
    if price:
        if price >= 150:
            score += 0.8
        elif price >= 90:
            score += 0.5
        elif price >= 55:
            score += 0.2
        elif price < 25:
            score -= 0.5
    if style in ("islay-peated", "speyside-sherry", "campbeltown", "irish-pot-still"):
        score += 0.3
    if expr == "single-malt" and age and age >= 12:
        score += 0.3
    return round(min(10.0, max(3.0, score)), 1)


def is_pairable(expr: str, style: str, quality: float) -> bool:
    if expr in NON_PAIRABLE_EXPR:
        return False
    if style in NON_PAIRABLE_STYLES:
        return False
    return quality >= 4.0


def serving_for_style(style: str, abv: float | None, expr: str) -> dict[str, Any]:
    if expr in NON_PAIRABLE_EXPR:
        return {"neat": 1, "water": 0, "rocks": 2, "highball": 3, "cola": 0, "best": "Koktel / RTD"}
    if style == "islay-peated":
        best = "Cisto / kap vode (otvara dim)"
        neat, water, rocks = 3, 3, 1
    elif style == "speyside-sherry":
        best = "Cisto" if not abv or abv < 50 else "Kap vode (cask strength)"
        neat, water, rocks = 3, 3 if abv and abv >= 50 else 2, 2
    elif style in ("bourbon", "tennessee", "rye"):
        best = "Cisto ili velika kocka leda"
        neat, water, rocks = 3, 2, 3
    elif style == "irish-pot-still":
        best = "Cisto"
        neat, water, rocks = 3, 2, 2
    elif style == "japanese":
        best = "Cisto / mala kocka leda"
        neat, water, rocks = 3, 2, 2
    else:
        best = "Cisto"
        neat, water, rocks = 3, 2, 2
    return {"neat": neat, "water": water, "rocks": rocks, "highball": 0, "cola": 0, "best": best}


def cigar_hint_for_style(style: str) -> str:
    hints = {
        "islay-peated": "Jaka Habano/corojo — dim nosi dim",
        "speyside-sherry": "Maduro/oscuro — sherry + kakao",
        "speyside-fruity": "Connecticut do Habano srednje snage",
        "bourbon": "Maduro/broadleaf — karamela i vanilija",
        "rye": "Corojo/Habano srednje-jake",
        "irish-pot-still": "Connecticut do Habano blage-srednje",
        "japanese": "Connecticut/claro — elegantno",
        "blended-scotch": "Sve wrapper tipovi srednje snage",
        "highland": "Habano srednje snage",
        "campbeltown": "Jaca Habano ili maduro",
    }
    return hints.get(style, "Srednja cigara, balans snage")


def token_overlap(a: str, b: str) -> int:
    return len(match_tokens(a) & match_tokens(b))


def numeric_age_tokens(name: str) -> set[str]:
    norm = unicodedata.normalize("NFKD", name.lower()).encode("ascii", "ignore").decode()
    return {t for t in re.findall(r"[a-z0-9]+", norm) if t.isdigit() and 1 <= len(t) <= 4}


def is_bare_category_url(url: str) -> bool:
    try:
        path = urlparse(url).path.lower().rstrip("/")
    except Exception:
        return True
    if "/svi-proizvodi/" in path or "/proizvod/" in path:
        return False
    if "/vrsta/" in path:
        after = path.split("/vrsta/", 1)[-1]
        return len([s for s in after.split("/") if s]) <= 1
    if "/katalog/" in path:
        after = path.split("/katalog/", 1)[-1]
        return len([s for s in after.split("/") if s]) <= 1
    return False


def catalog_entry_tokens(entry: dict, tokenize: Callable[[str], set[str]]) -> set[str]:
    tokens = set(entry.get("tokens") or ())
    url = entry.get("url", "")
    if not url:
        return tokens
    slug = urlparse(url).path.rstrip("/").split("/")[-1]
    tokens |= tokenize(slug)
    tokens |= {t for t in re.findall(r"[a-z0-9]+", slug.lower()) if t.isdigit()}
    return tokens


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
    out = []
    for e in entries:
        out.append({**e, "tokens": match_tokens(e["name"])})
    return out
