from __future__ import annotations

import re
import unicodedata

from whisky_shared import slugify

__all__ = [
    "canonical_name",
    "detect_style_region",
    "digestif_id",
    "estimate_quality",
    "extract_abv",
    "is_pairable_digestif",
    "parse_price_text",
    "serving_for_style",
]


NON_PAIRABLE_RE = re.compile(
    r"cream|coco|pina colada|shrubb|orange|lychee|maraschino|limoncello|sambuca|"
    r"amaretto|aperol|campari|bitter bianco|caffe liquore|coffee liqueur|honey liqueur|"
    r"negroamaro|amarone|vanilla|espresso|summer|aperitivo|gift box|ukrasnoj kutiji|"
    r"grappa|fragolino|prosecco|malvasia|amarone oro|cleopatra",
    re.I,
)

PAIRABLE_HINT_RE = re.compile(
    r"amaro|fernet|pelinkovac|benedictine|chartreuse|drambuie|becherovka|jäger|jager|unicum|strega|averna|nonino|montenegro|del capo|galliano|herbs",
    re.I,
)


def _fold(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()


def parse_price_text(text: str | None) -> float | None:
    if not text:
        return None
    matches = re.findall(r"(\d+(?:[.,]\d{1,2})?)\s*€", text)
    if not matches:
        matches = re.findall(r"(\d+(?:[.,]\d{1,2})?)", text)
    if not matches:
        return None
    return float(matches[-1].replace(",", "."))


def extract_abv(name: str) -> float | None:
    m = re.search(r"(\d{1,2}(?:[.,]\d+)?)\s*%\s*(?:vol\.?)?", name, re.I)
    if not m:
        return None
    return float(m.group(1).replace(",", "."))


def canonical_name(name: str) -> str:
    text = re.sub(r"\s+", " ", name).strip()
    text = re.sub(r"\s+\((?:0,\d+L|0\.\d+L)\)$", "", text, flags=re.I)
    text = re.sub(r"\b[Ll]iker\b", "", text)
    text = re.sub(r"\s{2,}", " ", text).strip(" -")
    replacements = {
        "Jagermeister": "Jägermeister",
        "Dom Benedictine": "DOM Benedictine",
        "Vecchio Amaro Del Capo": "Vecchio Amaro del Capo",
        "Aura Premium Pelinkovac Victoris": "Aura Pelinkovac Victoris",
    }
    return replacements.get(text, text)


def is_pairable_digestif(name: str) -> bool:
    low = _fold(name)
    if NON_PAIRABLE_RE.search(low):
        return False
    return bool(PAIRABLE_HINT_RE.search(low))


def detect_style_region(name: str) -> tuple[str, str, str, int, int, list[str]]:
    low = _fold(name)
    if "fernet" in low:
        return ("fernet", "Italija", "Italija", 4, 2, ["biljno", "gorcina", "menta"])
    if "chartreuse" in low:
        return ("chartreuse", "Francuska", "Francuska", 4, 3, ["bilje", "zacini", "med"])
    if "pelinkovac" in low:
        return ("pelinkovac", "Hrvatska", "Hrvatska", 3, 3, ["pelin", "bilje", "gorcina"])
    if "drambuie" in low:
        return ("spiced-honey", "Škotska", "Škotska", 3, 4, ["med", "zacini", "bilje"])
    if "benedictine" in low:
        return ("herbal-liqueur", "Francuska", "Francuska", 3, 3, ["bilje", "med", "zacini"])
    if "becherovka" in low:
        return ("herbal-bitter-central", "Češka", "Češka", 3, 3, ["cimet", "klinčić", "bilje"])
    if "jager" in low or "jäger" in low:
        return ("herbal-bitter-central", "Njemačka", "Njemačka", 3, 4, ["anis", "biljno", "zacini"])
    if "unicum" in low:
        return ("herbal-bitter-central", "Mađarska", "Mađarska", 4, 2, ["bilje", "gorcina", "zacini"])
    if "nonino" in low or "averna" in low or "montenegro" in low or "amaro" in low:
        return ("herbal-bitter-italian", "Italija", "Italija", 3, 3, ["bilje", "gorcina", "karamela"])
    if "galliano" in low or "strega" in low:
        return ("herbal-spice", "Italija", "Italija", 3, 3, ["bilje", "vanilija", "zacini"])
    return ("herbal-liqueur", "World", "World", 3, 3, ["bilje", "gorcina"])


def estimate_quality(name: str, price: float | None, style: str) -> float:
    score = 7.0
    low = _fold(name)
    if style in {"chartreuse", "fernet"}:
        score += 1.0
    elif style in {"herbal-bitter-italian", "pelinkovac"}:
        score += 0.4
    if any(k in low for k in ("chartreuse", "nonino", "benedictine", "drambuie")):
        score += 0.6
    if price is not None:
        if price <= 14:
            score += 0.2
        elif price <= 20:
            score += 0.4
        elif price <= 35:
            score += 0.6
        else:
            score += 0.8
    return round(min(score, 9.0), 1)


def serving_for_style(style: str) -> str:
    if style == "fernet":
        return "Čisto, hladno"
    if style in {"chartreuse", "herbal-bitter-italian"}:
        return "Čisto ili s ledom"
    if style == "spiced-honey":
        return "Čisto"
    return "Čisto, lagano rashlađeno"


def digestif_id(name: str) -> str:
    return f"dg-{slugify(canonical_name(name))}"
