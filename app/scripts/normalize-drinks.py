# -*- coding: utf-8 -*-
"""Cisti nazive pica i spaja pakiranja-duplikate (idempotentno).

Scrape iz shopova ostavi u nazivu sum: "40% Vol. 0,7l u poklon kutiji",
"+ 2 CASE", HTML entitete (&#039;), pa se ista boca pojavi u vise izdanja.
Ovo:
  1. dekodira HTML entitete
  2. skida ABV / volumen / "u poklon kutiji" / "+ N casa" / gift box i sl.
  3. spaja stavke koje se svedu na isti cist naziv -> zadrzi jednu
     (najjeftiniju pravu bocu; izbjegava gift/mini pakiranja)

Pokreni nakon regeneracije kataloga pica:
  python scripts/normalize-drinks.py
"""
import html
import json
import re
import unicodedata
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "src" / "data"
FILES = ["rums.json", "whiskies.json", "brandies.json", "gins.json"]

# uzorci suma na kraju/unutar naziva (redom se skidaju)
NOISE = [
    r"\s*\d{1,2}(?:[.,]\d)?\s*%\s*vol\.?",              # 40% Vol.
    r"\s*\d+\s*[x×]\s*\d+(?:[.,]\d+)?\s*l\b",            # 5x0,05 l
    r"\s*\d+(?:[.,]\d+)?\s*(?:cl|ml)\b",                 # 70cl / 700ml
    r"\s*\d+(?:[.,]\d+)?\s*l\b",                          # 0,7l / 1l
    r"\s*u\s+(?:drvenoj\s+)?poklon\s+kutij\w*",         # u (drvenoj) poklon kutiji
    r"\s*u\s+poklon\s+set\w*",
    r"\s*\bgift\s*box\b",
    r"\s*\bin\s+giftbox\b",
    r"\s*\bGB\b",
    r"\s*(?:sa?|with|\+)\s*\d*\s*(?:čaš\w*|case\b|glass\w*|glencairn)\w*",  # + 2 case / with glass
    r"\s*\bu\s+tubi\b|\s*\btuba\b|\s*\btin\b",
    r"\s*\bnew\s+edition\b|\s*\bold\s+edition\b",
]
NOISE_RE = [re.compile(p, re.I) for p in NOISE]

# genericke kategorije (ne razlikuju proizvod unutar marke) — skinu se s kraja/sredine
CATEGORY = [
    r"islay single malt scotch whisky", r"single malt scotch whisky",
    r"blended malt scotch whisky", r"blended grain scotch whisky",
    r"blended scotch whisky", r"single grain scotch whisky", r"scotch whisky",
    r"single pot still irish whiskey", r"blended irish whiskey", r"irish whiskey",
    r"tennessee whiskey", r"kentucky straight bourbon whiskey",
    r"straight bourbon whiskey", r"bourbon whiskey", r"straight rye whiskey",
    r"rye whiskey", r"japanese whisky", r"world whisky", r"single malt whisky",
    r"pure single jamaican rum", r"single blended rum", r"jamaican rum",
    r"superior spirit drink", r"spirit drink",
    r"london dry gin", r"dry gin",
]
CATEGORY_RE = [re.compile(rf"\b{p}\b", re.I) for p in CATEGORY]


# mojibake (UTF-8 pogresno dekodiran kao OEM codepage) -> ispravni znak
MOJIBAKE = {
    "├í": "á", "├ę": "é", "├ş": "í", "├│": "ó", "├║": "ú", "├▒": "ñ",
    "├╝": "ü", "├ó": "â", "├¿": "è", "├ę": "é", "┼ż": "ž", "┼í": "š",
    "─ç": "ć", "─Ź": "č", "├ë": "É", "N°": "No.",
}


def fix_mojibake(s: str) -> str:
    for k, v in MOJIBAKE.items():
        s = s.replace(k, v)
    return s


def clean_name(name: str) -> str:
    s = fix_mojibake(html.unescape(name))
    s = s.replace("&#039;", "'").replace("&amp;", "&")
    for rx in NOISE_RE:
        s = rx.sub("", s)
    for rx in CATEGORY_RE:
        s = rx.sub("", s)
    s = re.sub(r"\s{2,}", " ", s).strip(" -–,")
    # popravi ALLCAPS u Title Case (cuva kratice XO/VSOP/VS/No./rimske)
    if s.isupper():
        s = smart_title(s)
    return s


ACRONYMS = {"XO", "VS", "VSOP", "VSOP.", "VO", "NAS", "PX", "ABV", "USA", "HLCF",
            "ECS", "OFTD", "AOC", "No.", "N.", "JM", "HSE", "II", "III", "IV",
            "VI", "VII", "VIII", "IX", "XII", "XV", "XXI", "SE", "DR"}


def smart_title(s: str) -> str:
    out = []
    for w in s.split(" "):
        up = w.upper().strip(".")
        if w.upper() in ACRONYMS or up in ACRONYMS or re.fullmatch(r"[IVXLC]+", w.upper()):
            out.append(w.upper())
        elif "'" in w:  # Jack Daniel'S -> Jack Daniel's
            out.append(w.capitalize().replace("'S", "'s"))
        else:
            out.append(w.capitalize())
    return " ".join(out)


def dedup_key(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def price_min(e):
    p = e.get("priceEUR")
    if isinstance(p, dict):
        return p.get("min") or 1e9
    if isinstance(p, (int, float)):
        return p
    return 1e9


def normalize_file(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    for e in data:
        e["name"] = clean_name(e["name"])

    # spoji po cistom nazivu — zadrzi najjeftiniju pravu bocu (cijena >= 8€),
    # inace najjeftiniju uopce
    groups: dict[str, list] = {}
    for e in data:
        groups.setdefault(dedup_key(e["name"]), []).append(e)

    kept, removed = [], 0
    for _, items in groups.items():
        if len(items) == 1:
            kept.append(items[0])
            continue
        real = [e for e in items if price_min(e) >= 8] or items
        best = min(real, key=price_min)
        # prenesi priceUrl ako ga best nema a netko ima
        if not best.get("priceUrl"):
            for e in items:
                if e.get("priceUrl"):
                    best["priceUrl"] = e["priceUrl"]
                    break
        kept.append(best)
        removed += len(items) - 1

    # zadrzi originalni redoslijed po prvom pojavljivanju
    order = {id(e): i for i, e in enumerate(data)}
    kept.sort(key=lambda e: order[id(e)])
    path.write_text(json.dumps(kept, ensure_ascii=False, indent=1), encoding="utf-8")
    return len(data), len(kept), removed


def main():
    for f in FILES:
        p = DATA / f
        if not p.exists():
            continue
        before, after, removed = normalize_file(p)
        print(f"{f}: {before} -> {after}  (spojeno {removed} pakiranja-duplikata)")


if __name__ == "__main__":
    main()
