# -*- coding: utf-8 -*-
"""Obogacuje cigare kojima nedostaje profil (prazan flavorTags -> generic 3/3).

Pipeline za sirenje kataloga ostavi ~370 cigara na snaga=3/tijelo=3, wrapper
"Natural" i bez flavorTags. Ovdje izvodimo stvaran profil iz:
  1. wrapper polja (+ naziv linije/vitole kad wrapper = "Natural")
  2. marka-baseline karaktera (jake vs blage kuce)
  3. kljucnih rijeci u engleskim biljeskama (chocolate/pepper/cream...)
  4. tablice poznatih ikonskih linija (KNOWN)

Dira ISKLJUCIVO stavke s praznim flavorTags — kurirane ostaju netaknute.
Idempotentno; pokreni nakon regeneracije cigars.json:

  python scripts/profile-cigars.py
"""
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "src" / "data"
CIGARS = DATA / "cigars.json"


def clamp(v, lo=1, hi=5):
    return max(lo, min(hi, v))


# wrapper kategorija -> (snaga, tijelo, [tagovi], normalizirani prikaz wrappera)
WRAPPER_BASE = {
    "dark_maduro": (4, 5, ["kakao", "kava", "zemljano", "koza", "papar"], "Maduro / Oscuro"),
    "maduro":      (3, 4, ["kakao", "kava", "karamela", "slatko", "zemljano"], "Maduro"),
    "corojo":      (4, 4, ["papar", "zacini", "koza", "cedar"], "Corojo"),
    "sumatra":     (3, 4, ["kakao", "zacini", "drvo", "karamela"], "Sumatra"),
    "cameroon":    (2, 3, ["zacini-slatki", "cedar", "orasasti", "koza"], "Cameroon"),
    "connecticut": (2, 2, ["kremasto", "cedar", "orasasti", "med", "trava-slatka"], "Connecticut"),
    "criollo":     (3, 3, ["zemljano", "cedar", "orasasti", "zacini"], "Criollo"),
    "habano":      (3, 3, ["cedar", "zacini", "koza", "kava"], "Habano"),
    "cuban":       (3, 3, ["cedar", "duhan", "zemljano", "zacini", "med"], "Cuban Habano"),
}

# redoslijed detekcije (prvi pogodak pobjeduje)
WRAPPER_PATTERNS = [
    ("dark_maduro", r"oscuro|double maduro|nicaraguan maduro|dark"),
    ("maduro", r"maduro|broadleaf|san andr|brazil|arapiraca|mexican"),
    ("corojo", r"corojo"),
    ("sumatra", r"sumatra"),
    ("cameroon", r"cameroon"),
    ("connecticut", r"connecticut|shade|\bclaro\b|champagne|ecuador connecticut"),
    ("criollo", r"criollo"),
    ("habano", r"habano|sun.?grown|sungrown|colorado|rosado|medio tiempo|cuban seed"),
]

# marka -> (delta_snaga, delta_tijelo) — karakter kuce
BRAND_BIAS = {
    "Joya de Nicaragua": (1, 1), "La Flor Dominicana": (1, 1), "Foundation Cigar Company": (1, 1),
    "Padrón": (1, 0), "AJ Fernandez": (1, 0), "Camacho": (1, 0), "Tatuaje": (0, 1),
    "Partagás": (1, 1), "Bolívar": (1, 1), "Ramón Allones": (1, 1), "Punch": (0, 1),
    "Plasencia": (0, 1), "Oscar Valladares": (0, 1), "Casa 1910": (0, 1), "Warped Cigars": (0, 0),
    "Macanudo": (-1, -1), "Ashton": (-1, -1), "Flor de Selva": (-1, -1), "Zino": (-1, -1),
    "Cusano": (-1, -1), "Villiger": (-1, -1), "Villa Zamorano": (-1, -1), "Fonseca": (-1, -1),
    "Hoyo de Monterrey": (-1, 0), "Romeo y Julieta": (-1, 0), "H. Upmann": (0, 0),
    "Cohiba": (0, 0), "Montecristo": (0, 0), "Trinidad": (0, 0), "Quintero": (0, 0),
    "Cuaba": (0, 0), "San Cristóbal de la Habana": (0, 0), "Vegas Robaina": (0, 1),
    "Juan López": (0, 0),
}

# kljucna rijec u biljesci/liniji -> tag (i eventualni nudge snage)
KEYWORD_TAGS = [
    (r"chocolate|cocoa|kakao", "kakao"),
    (r"coffee|espresso|mocha|kava", "kava"),
    (r"pepper|papar|peppery", "papar"),
    (r"cream|creamy|kremast", "kremasto"),
    (r"cedar|cedr", "cedar"),
    (r"earth|earthy|zemljan", "zemljano"),
    (r"\bnut|nutty|almond|hazelnut|orasast", "orasasti"),
    (r"sweet|slatk", "slatko"),
    (r"leather|koza|koža", "koza"),
    (r"spice|spicy|zacin|začin", "zacini"),
    (r"floral|cvjetn|flower", "cvjetno"),
    (r"citrus|lemon|orange|lime|naranc", "citrus"),
    (r"wood|woody|oak|hrast|drvo", "drvo"),
    (r"caramel|toffee|karamel|toast", "karamela"),
    (r"honey|med\b", "med"),
    (r"grass|hay|travnat", "trava-slatka"),
    (r"fruit|voce|voće|cherry|raisin|plum|dried fruit", "suho-voce"),
    (r"nutmeg|cinnamon|clove|cimet", "zacini"),
    (r"tobacco|duhan|barnyard|hay", "duhan"),
]

STRONG_WORDS = re.compile(r"\bfull\b|full-bodied|full bodied|bold|strong|powerful|robust|potent|puno tijelo|jak")
MILD_WORDS = re.compile(r"\bmild\b|mellow|smooth|creamy|elegant|delicate|light-bodied|blag|nizak|lagan")
MEDIUM_WORDS = re.compile(r"medium|balanced|srednj")

# poznate ikonske linije: (snaga, tijelo, [tagovi]) — override heuristike
KNOWN = {
    ("Cohiba", "Behike"): (4, 4, ["kremasto", "med", "cedar", "zacini", "kakao"]),
    ("Cohiba", "Maduro"): (3, 4, ["kakao", "kava", "cedar", "zemljano"]),
    ("Montecristo", "Edmundo"): (3, 4, ["kakao", "kremasto", "cedar", "orasasti"]),
    ("Partagás", "Serie D"): (4, 5, ["zemljano", "papar", "koza", "kava"]),
    ("Partagás", "Lusitanias"): (4, 5, ["zemljano", "papar", "koza", "kava"]),
    ("Romeo y Julieta", "Wide Churchill"): (3, 3, ["cedar", "med", "kremasto", "orasasti"]),
    ("Hoyo de Monterrey", "Epicure"): (2, 3, ["kremasto", "trava-slatka", "orasasti", "cedar"]),
    ("Bolívar", "Belicosos"): (4, 5, ["zemljano", "papar", "koza", "kakao"]),
    ("Punch", "Punch"): (3, 4, ["zemljano", "kava", "koza", "cedar"]),
    ("Trinidad", "Fundadores"): (3, 3, ["kremasto", "med", "cedar", "citrus"]),
    ("H. Upmann", "Magnum"): (3, 3, ["kremasto", "cedar", "kava", "med"]),
    ("Ramón Allones", "Specially Selected"): (4, 5, ["tamno-voce", "kakao", "zemljano", "zacini"]),
    ("Davidoff", "Nicaragua"): (3, 4, ["kakao", "papar", "citrus", "zemljano"]),
    ("Davidoff", "Winston Churchill"): (3, 4, ["kava", "tamno-voce", "zacini", "dim"]),
    ("Davidoff", "Escurio"): (3, 4, ["kakao", "karamela", "zacini", "citrus"]),
    ("Davidoff", "Yamasa"): (3, 4, ["zemljano", "kakao", "koza", "zacini"]),
    ("Davidoff", "Signature"): (1, 2, ["kremasto", "orasasti", "cedar", "citrus"]),
    ("Davidoff", "Grand Cru"): (2, 2, ["kremasto", "orasasti", "med", "drvo"]),
    ("Davidoff", "Aniversario"): (2, 3, ["kremasto", "med", "orasasti", "cedar"]),
    ("Plasencia", "Alma Fuerte"): (4, 5, ["kakao", "tamno-voce", "zacini", "zemljano"]),
    ("Plasencia", "Cosecha"): (3, 4, ["zemljano", "citrus", "drvo", "kremasto"]),
    ("Oliva", "Serie V"): (4, 4, ["kakao", "karamela", "zacini", "koza"]),
    ("Oliva", "Serie O"): (3, 3, ["zemljano", "zacini", "kakao", "drvo"]),
    ("Oliva", "Serie G"): (2, 3, ["kava", "orasasti", "karamela", "cedar"]),
    ("Arturo Fuente", "Hemingway"): (2, 3, ["cedar", "zacini-slatki", "karamela", "kava"]),
    ("Arturo Fuente", "Don Carlos"): (3, 4, ["zacini", "cedar", "kakao", "koza"]),
    ("Arturo Fuente", "Anejo"): (4, 5, ["kakao", "kava", "tamno-voce", "zacini"]),
    ("Ashton", "VSG"): (4, 5, ["zemljano", "zacini", "koza", "tamno-voce"]),
    ("Ashton", "Paragon"): (2, 2, ["kremasto", "orasasti", "med", "cedar"]),
    ("Bolívar", "Core Line"): (4, 5, ["zemljano", "papar", "koza", "kakao"]),
    ("My Father", "Le Bijou"): (4, 5, ["kakao", "papar", "zemljano", "karamela"]),
    ("La Aurora", "1903"): (2, 3, ["cedar", "kremasto", "orasasti", "zacini"]),
    ("La Aurora", "107"): (3, 3, ["cedar", "zacini", "kakao", "zemljano"]),
    ("La Aurora", "Preferidos"): (3, 4, ["kakao", "cedar", "zacini", "koza"]),
    ("E.P. Carrillo", "Pledge"): (4, 4, ["kakao", "zacini-slatki", "zemljano", "kava"]),
    ("E.P. Carrillo", "Encore"): (4, 4, ["kakao", "zemljano", "kava", "koza"]),
    ("Foundation Cigar Company", "Tabernacle"): (5, 5, ["zemljano", "kakao", "papar", "koza", "dim"]),
    ("Foundation Cigar Company", "Charter Oak"): (2, 2, ["kremasto", "trava-slatka", "med", "orasasti"]),
    ("Tatuaje", "Havana"): (4, 4, ["cedar", "zacini", "koza", "zemljano"]),
    ("Rocky Patel", "Decade"): (4, 4, ["zemljano", "kakao", "zacini", "koza"]),
    ("Aganorsa Leaf", "Supreme Leaf"): (4, 4, ["kakao", "papar", "koza", "zemljano"]),
    ("Aganorsa Leaf", "Aniversario"): (3, 4, ["kremasto", "zacini-slatki", "cedar", "kakao"]),
    # web-verificirano (halfwheel / cigar-coop / developingpalates / neptunecigar)
    ("Joya de Nicaragua", "Joya Black"): (3, 4, ["kakao", "zemljano", "papar", "kava"]),
    ("Joya de Nicaragua", "Joya Silver"): (3, 4, ["kakao", "karamela", "zacini", "kremasto"]),
    ("Joya de Nicaragua", "Cinco Décadas"): (4, 5, ["kakao", "koza", "zemljano", "karamela"]),
    ("Joya de Nicaragua", "Numero Uno"): (2, 3, ["kremasto", "cedar", "citrus", "med"]),
    ("Rocky Patel", "A.L.B."): (4, 4, ["papar", "kakao", "orasasti", "zemljano"]),
    ("Rocky Patel", "Alr"): (4, 4, ["papar", "kakao", "orasasti", "zemljano"]),
    ("La Galera", "Anemoi"): (4, 4, ["kakao", "zemljano", "papar", "slatko"]),
    ("La Galera", "Imperial Jade"): (3, 3, ["zacini-slatki", "cedar", "orasasti", "kakao"]),
    ("La Galera", "Habano"): (3, 3, ["cedar", "zacini", "med", "orasasti"]),
    ("La Galera", "Maduro"): (3, 4, ["kakao", "kava", "slatko", "zemljano"]),
    ("La Galera", "1936"): (3, 4, ["cedar", "zacini", "orasasti", "koza"]),
    ("Casa 1910", "Jilguero"): (3, 4, ["kakao", "zemljano", "papar", "slatko"]),
    ("Casa 1910", "As De Oro"): (3, 4, ["cedar", "zacini", "zemljano", "kakao"]),
    ("Casa 1910", "Lucero"): (3, 4, ["cedar", "zacini", "zemljano", "kakao"]),
    ("CAO", "Vision"): (4, 4, ["cedar", "zacini", "zemljano", "papar"]),
    ("Camacho", "Diploma"): (5, 4, ["papar", "zemljano", "koza", "kakao"]),
    ("Camacho", "Nicaragua"): (4, 4, ["papar", "zemljano", "kakao", "cedar"]),
    ("Cohiba", "Esplendidos"): (3, 4, ["kremasto", "med", "cedar", "trava-slatka"]),
    ("Montecristo", "Open"): (2, 3, ["trava-slatka", "cedar", "med", "citrus"]),
    ("Partagás", "Serie E"): (4, 5, ["zemljano", "papar", "koza", "kava"]),
    ("Trinidad", "La Trova"): (4, 4, ["kremasto", "med", "cedar", "zacini"]),
    ("Arturo Fuente", "Chateau Fuente"): (2, 3, ["kremasto", "cedar", "orasasti", "med"]),
}


def wrapper_category(text: str, country: str) -> str:
    for cat, pat in WRAPPER_PATTERNS:
        if re.search(pat, text, re.I):
            return cat
    if country == "Kuba":
        return "cuban"
    return "habano"  # "Natural" bez signala -> medium habano-ish


def known_lookup(brand: str, line: str):
    for (b, key), val in KNOWN.items():
        if b == brand and key.lower() in line.lower():
            return val
    return None


def enrich(c: dict) -> None:
    brand, line = c["brand"], c.get("line", "")
    text = f"{c.get('wrapper','')} {line} {c.get('vitola','')}"
    notes = (c.get("notes", {}).get("en", "") + " " +
             c.get("notes", {}).get("hr", "") + " " + line).lower()

    known = known_lookup(brand, line)
    if known:
        s, b, tags = known
        tags = list(tags)
    else:
        cat = wrapper_category(text, c.get("country", ""))
        s, b, base_tags, wrap_disp = WRAPPER_BASE[cat]
        tags = list(base_tags)
        # normaliziraj prikaz wrappera kad je bio "Natural"/"Cuban seed"
        if (c.get("wrapper") or "").lower() in ("natural", "cuban seed wrapper", ""):
            c["wrapper"] = wrap_disp
        # marka-karakter
        ds, db = BRAND_BIAS.get(brand, (0, 0))
        s, b = s + ds, b + db
        # tekstualni nudge
        if STRONG_WORDS.search(notes):
            s, b = s + 1, b + 1
        elif MILD_WORDS.search(notes):
            s, b = s - 1, b - 1

    # kljucne rijeci -> dodatni tagovi
    for pat, tag in KEYWORD_TAGS:
        if re.search(pat, notes) and tag not in tags:
            tags.append(tag)

    c["strength"] = clamp(s)
    c["body"] = clamp(b)
    c["flavorTags"] = tags[:6]
    # KNOWN tablica je istrazena rucno; sve ostalo je heuristika koju app
    # oznacava kao "procijenjeni profil"
    if not known:
        c["profileEstimated"] = True


def main():
    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    n = 0
    for c in cigars:
        if not c.get("flavorTags"):  # samo generirane stubove
            enrich(c)
            n += 1
    CIGARS.write_text(json.dumps(cigars, ensure_ascii=False, indent=1), encoding="utf-8")

    from collections import Counter
    sb = Counter((c["strength"], c["body"]) for c in cigars)
    print(f"obogaceno: {n} cigara")
    print("distribucija (snaga,tijelo) nakon:")
    for k, v in sorted(sb.items()):
        print(f"   {k}: {v}")


if __name__ == "__main__":
    main()
