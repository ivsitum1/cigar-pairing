# -*- coding: utf-8 -*-
"""Obogacuje cigars.json vitolama, cijenama i linkovima.

Izvori:
  - humidor_catalog.txt (scrape humidor.hr, format: "Naziv L x RG | cijena | url")
  - VITOLA_SETS: standardne vitole za linije koje nisu na humidor.hr (Habanos itd.)
  - BRAND_SLUGS: havana-cigar-shop.com brand stranice kao priceUrl fallback

Pokretanje: python scripts/enrich-cigars.py <put-do-humidor_catalog.txt>
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"

FRACTIONS = {"½": 0.5, "¼": 0.25, "¾": 0.75, "⅛": 0.125, "⅜": 0.375,
             "⅝": 0.625, "⅞": 0.875, "⅔": 0.667, "⅓": 0.333}

# prefiks naziva proizvoda (case-insensitive) -> id linije u cigars.json
MAP = [
    ("aj fernandez new world", "cig-aj-fernandez-new-world"),
    ("new world", "cig-aj-fernandez-new-world"),
    ("dias de gloria", "cig-aj-fernandez-dias-de-gloria"),
    ("eiroa classic", "cig-eiroa-classic"),
    ("eiroa", "cig-eiroa-cbt-maduro"),
    ("la galera 85th", "cig-la-galera-85th"),
    ("la galera habano", "cig-la-galera-85th"),
    ("la galera connecticut", "cig-la-galera-connecticut"),
    ("eladio diaz", "cig-eladio-diaz"),
    ("viva la vida connecticut", "cig-viva-la-vida-connecticut"),
    ("viva la vida", "cig-viva-la-vida"),
    ("el pulpo", "cig-el-pulpo"),
    ("liga privada no.9", "cig-liga-privada-no9"),
    ("mi querida", "cig-mi-querida"),
    ("sobremesa brulee", "cig-sobremesa-brulee"),
    ("sobremesa", "cig-sobremesa"),
    ("oliva connecticut reserve", "cig-oliva-connecticut-reserve"),
    ("oliva serie g", "cig-oliva-serie-g"),
    ("oliva serie o", "cig-oliva-serie-o"),
    ("oliva serie v", "cig-oliva-serie-v"),
    ("nub connecticut", "cig-nub-connecticut"),
    ("macanudo cafe", "cig-macanudo-cafe"),
    ("camacho connecticut", "cig-camacho-connecticut"),
    ("camacho corojo", "cig-camacho-corojo"),
    ("ashton classic", "cig-ashton-classic"),
    ("davidoff signature", "cig-davidoff-signature"),
    ("davidoff nicaragua", "cig-davidoff-nicaragua"),
    ("davidoff wsc the late hour", "cig-davidoff-winston-churchill"),
    ("perdomo 10th anniversary connecticut", "cig-perdomo-champagne"),
    ("perdomo 20th anniversary", "cig-perdomo-20th-maduro"),
    ("plasencia alma fuerte", "cig-plasencia-alma-fuerte"),
    ("plasencia alma del campo", "cig-plasencia-alma-del-campo"),
    ("aganorsa leaf la validacion", "cig-aganorsa-la-validacion"),
    ("aganorsa leaf aniversario", "cig-aganorsa-aniversario"),
    ("arturo fuente gran reserva", "cig-arturo-fuente-gran-reserva"),
    ("arturo fuente hemingway", "cig-arturo-fuente-hemingway"),
    ("arturo fuente opusx", "cig-fuente-opus-x"),
    ("montecristo no.4", "cig-montecristo-no4"),
    ("montecristo no.2", "cig-montecristo-no2"),
    ("partagas serie d", "cig-partagas-serie-d4"),
    ("partagas short", "cig-partagas-shorts"),
    ("romeo y julieta no.2", "cig-romeo-y-julieta-no2"),
    ("h. upmann half corona", "cig-hupmann-half-corona"),
    ("la aurora 107", "cig-la-aurora-107"),
]

# standardne vitole za linije bez humidor podataka: id -> [(vitola, ring, duljina_mm)]
VITOLA_SETS = {
    "cig-cohiba-siglo-i-ii": [("Siglo I", 40, 102), ("Siglo II", 42, 129), ("Siglo III", 42, 155)],
    "cig-cohiba-siglo-iv-vi": [("Siglo IV", 46, 143), ("Siglo V", 43, 170), ("Siglo VI", 52, 150)],
    "cig-cohiba-robustos": [("Robusto", 50, 124)],
    "cig-montecristo-no4": [("No.4 (mareva)", 42, 129), ("No.5", 40, 102), ("No.3 (corona)", 42, 155)],
    "cig-montecristo-no2": [("No.2 (pirámide)", 52, 156), ("Petit No.2", 52, 120)],
    "cig-montecristo-edmundo": [("Petit Edmundo", 52, 110), ("Edmundo", 52, 135), ("Open Eagle", 54, 150)],
    "cig-partagas-serie-d4": [("Serie D No.6", 50, 90), ("Serie D No.5", 50, 110), ("Serie D No.4", 50, 124), ("Serie E No.2", 54, 140)],
    "cig-partagas-shorts": [("Short", 42, 110), ("Mille Fleurs", 42, 129)],
    "cig-romeo-y-julieta-no2": [("No.3", 40, 117), ("No.2", 42, 129), ("No.1", 40, 140)],
    "cig-romeo-y-julieta-short-churchills": [("Petit Churchill", 50, 102), ("Short Churchill", 50, 124), ("Wide Churchill", 55, 130), ("Churchill", 47, 178)],
    "cig-hoyo-epicure-no2": [("Epicure Especial", 50, 141), ("Epicure No.2", 50, 124), ("Epicure No.1", 46, 143)],
    "cig-hoyo-petit-robusto": [("Petit Robusto", 50, 102)],
    "cig-hupmann-half-corona": [("Half Corona", 44, 90)],
    "cig-hupmann-magnum": [("Magnum 46", 46, 143), ("Magnum 50", 50, 160), ("Magnum 54", 54, 120)],
    "cig-trinidad-reyes": [("Reyes", 40, 110), ("Coloniales", 44, 132)],
    "cig-trinidad-vigia": [("Vigía", 54, 110), ("Esmeralda", 53, 145)],
    "cig-quai-dorsay-50-54": [("No.50", 50, 110), ("No.54", 54, 135)],
    "cig-ramon-allones-specially-selected": [("Small Club Coronas", 42, 110), ("Specially Selected", 50, 124)],
    "cig-juan-lopez-seleccion-no2": [("Selección No.2", 50, 124), ("Selección No.1", 46, 143)],
    "cig-fonseca-delicias": [("KDT Cadetes", 36, 115), ("Delicias", 40, 123)],
    "cig-quintero-favoritos": [("Petit Quintero", 33, 110), ("Favoritos", 50, 110)],
    "cig-jose-l-piedra-petit-caballeros": [("Petit Caballeros", 44, 105), ("Cazadores", 43, 152)],
    "cig-cuaba-divinos": [("Divinos", 43, 101), ("Tradicionales", 42, 120)],
    "cig-padron-2000": [("2000 (robusto)", 50, 127), ("3000", 52, 140), ("4000", 54, 165)],
    "cig-padron-1964": [("Principe", 46, 114), ("Exclusivo", 50, 140), ("Imperial", 54, 152)],
    "cig-padron-1926": [("No.6", 52, 121), ("No.9", 56, 133), ("No.2 (belicoso)", 52, 140)],
    "cig-davidoff-aniversario": [("Entreacto", 43, 89), ("Special R", 50, 124), ("No.3", 50, 152)],
    "cig-davidoff-grand-cru": [("No.3", 42, 127), ("No.2", 43, 143)],
    "cig-my-father-le-bijou": [("Petit Robusto", 50, 114), ("Toro", 54, 152), ("Torpedo Box Press", 52, 156)],
    "cig-my-father-flor-antillas": [("Robusto", 50, 127), ("Toro", 52, 152), ("Belicoso", 52, 140)],
    "cig-undercrown-maduro": [("Robusto", 52, 127), ("Corona Doble", 54, 178), ("Gran Toro", 52, 152)],
    "cig-undercrown-shade": [("Robusto", 52, 127), ("Gran Toro", 52, 152)],
    "cig-joya-de-nicaragua-antano": [("Machito", 50, 121), ("Robusto Grande", 52, 121), ("Gran Cónsul", 60, 121)],
    "cig-joya-red": [("Robusto", 50, 127), ("Toro", 52, 152)],
    "cig-foundation-tabernacle": [("Corona", 46, 133), ("Robusto", 50, 127), ("Toro", 52, 152)],
    "cig-foundation-charter-oak": [("Rothschild", 50, 114), ("Toro", 52, 152)],
    "cig-vegafina-classic": [("Corona", 42, 142), ("Robusto", 50, 127), ("Fortaleza 2 Toro", 52, 152)],
}

# havana-cigar-shop brand stranice (fallback priceUrl)
HAVANA = "https://havana-cigar-shop.com/en/product-brand/{}/"
BRAND_SLUGS = {
    "Cohiba": "cohiba", "Montecristo": "montecristo", "Partagás": "partagas",
    "Romeo y Julieta": "romeo-y-julieta", "Hoyo de Monterrey": "hoyo-de-monterrey",
    "H. Upmann": "h-upmann", "Trinidad": "trinidad", "Quai d'Orsay": "quai-dorsai",
    "Ramón Allones": "ramon-allones", "Juan López": "juan-lopez", "Fonseca": "fonseca",
    "Quintero": "quintero", "José L. Piedra": "jose-piedra", "Cuaba": "cuaba",
    "Davidoff": "davidoff", "Zino": "zino", "Arturo Fuente": "arturo-fuente",
    "Oliva": "oliva", "Joya de Nicaragua": "joya-de-nicaragua", "Camacho": "camacho",
    "Plasencia": "plasencia", "E.P. Carrillo": "e-p-carrillo", "Nub": "nub",
    "Oscar Valladares": "oscar-valladares", "Flor de Selva": "flor-de-selva",
    "Villa Zamorano": "villa-zamorano", "Cumpay": "cumpay", "Cusano": "cusano",
    "Casa 1910": "casa-1910",
}

# nove linije pronadjene na humidor.hr (user: nedostaju serije)
NEW_LINES = [
    {"id": "cig-oliva-connecticut-reserve", "brand": "Oliva", "line": "Connecticut Reserve",
     "vitola": "Robusto", "format": "50 x 127mm", "country": "Nikaragva",
     "wrapper": "Ecuador Connecticut", "strength": 2, "body": 3,
     "flavorTags": ["kremasto", "orasasti", "med", "cedar"], "smokeTimeMin": 50,
     "priceEUR": None, "priceApprox": False, "markets": ["HR", "EU", "USA", "WW"],
     "availabilityHR": ["The Humidor"],
     "notes": {"hr": "Blaga Oliva — kremasti Connecticut na nikaragvanskoj bazi.",
               "en": "Mild Oliva — creamy Connecticut on a Nicaraguan base."}},
    {"id": "cig-la-galera-connecticut", "brand": "La Galera", "line": "Connecticut",
     "vitola": "Robusto", "format": "50 x 130mm", "country": "Dominikana",
     "wrapper": "Ecuador Connecticut", "strength": 2, "body": 2,
     "flavorTags": ["kremasto", "med", "cedar", "trava-slatka"], "smokeTimeMin": 50,
     "priceEUR": None, "priceApprox": False, "markets": ["HR", "EU", "USA", "WW"],
     "availabilityHR": ["The Humidor"],
     "notes": {"hr": "Blaga dominikanska linija — value Connecticut u puno formata.",
               "en": "Mild Dominican line — value Connecticut in many formats."}},
    {"id": "cig-la-aurora-107", "brand": "La Aurora", "line": "107 / 107 Nicaragua",
     "vitola": "Robusto", "format": "50 x 127mm", "country": "Dominikana",
     "wrapper": "Ecuador Sun Grown / Nicaragua", "strength": 3, "body": 3,
     "flavorTags": ["cedar", "zacini", "kakao", "zemljano"], "smokeTimeMin": 50,
     "priceEUR": None, "priceApprox": False, "markets": ["HR", "EU", "USA", "WW"],
     "availabilityHR": ["The Humidor"],
     "notes": {"hr": "Najstarija dominikanska fabrika (1903) — uravnotežena moderna linija.",
               "en": "The oldest Dominican factory (1903) — a balanced modern line."}},
    {"id": "cig-aganorsa-aniversario", "brand": "Aganorsa Leaf", "line": "Aniversario",
     "vitola": "Robusto", "format": "54 x 127mm", "country": "Nikaragva",
     "wrapper": "Corojo / Connecticut / Maduro", "strength": 3, "body": 4,
     "flavorTags": ["kremasto", "zacini-slatki", "kakao", "cedar"], "smokeTimeMin": 55,
     "priceEUR": None, "priceApprox": False, "markets": ["HR", "EU", "USA", "WW"],
     "availabilityHR": ["The Humidor"],
     "notes": {"hr": "Jubilarna Aganorsa linija u tri wrappera — svilenkast dim.",
               "en": "Aganorsa's anniversary line in three wrappers — silky smoke."}},
    {"id": "cig-sobremesa-brulee", "brand": "Dunbarton T&T", "line": "Sobremesa Brulée",
     "vitola": "Robusto", "format": "52 x 133mm", "country": "Nikaragva",
     "wrapper": "Ecuador Connecticut", "strength": 2, "body": 3,
     "flavorTags": ["kremasto", "med", "vanilija", "slatko"], "smokeTimeMin": 55,
     "priceEUR": None, "priceApprox": False, "markets": ["HR", "EU", "USA", "WW"],
     "availabilityHR": ["The Humidor"],
     "notes": {"hr": "'Crème brûlée' cigara — slatka blaga strana Steve Sake.",
               "en": "The 'crème brûlée' cigar — Steve Saka's sweet mild side."}},
]


def parse_len(tok: str) -> float:
    """'5 ½' -> 5.5 ; '6' -> 6.0"""
    total = 0.0
    for part in tok.split():
        if part in FRACTIONS:
            total += FRACTIONS[part]
        else:
            total += float(part)
    return total


def smoke_minutes(length_in: float, ring: int) -> int:
    est = length_in * 10 * (0.60 + ring / 140)
    return int(round(est / 5) * 5)


def parse_catalog(path: Path):
    """Vraca [{name, vitola_dims, price, url}] iz humidor_catalog.txt."""
    rows = []
    dim_re = re.compile(r"^(.*?)\s+((?:\d+(?:\s+[½¼¾⅛⅜⅝⅞⅔⅓])?))\s*[xX]\s*(\d+)(?:\s*[xX]\s*\d+)?\s*$")
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        name_part, price, url = [t.strip() for t in line.split("|")]
        m = dim_re.match(name_part)
        if not m:
            rows.append({"name": name_part, "len": None, "ring": None,
                         "price": float(price), "url": url})
            continue
        rows.append({"name": m.group(1).strip(), "len": parse_len(m.group(2)),
                     "ring": int(m.group(3)), "price": float(price), "url": url})
    return rows


def match_id(product_name: str):
    low = product_name.lower()
    for prefix, cid in MAP:
        if low.startswith(prefix):
            return cid, product_name[len(prefix):].strip(" -–") or "Standard"
    return None, None


def main():
    catalog = parse_catalog(Path(sys.argv[1]))
    cigars = json.loads((DATA / "cigars.json").read_text(encoding="utf-8"))
    ids = {c["id"] for c in cigars}
    for nl in NEW_LINES:
        if nl["id"] not in ids:
            cigars.append(nl)

    by_id = {c["id"]: c for c in cigars}
    humidor_vitolas: dict[str, list] = {}
    unmatched = []

    for row in catalog:
        cid, vitola_name = match_id(row["name"])
        if not cid or cid not in by_id:
            unmatched.append(row["name"])
            continue
        if row["len"] is None:
            continue  # neparsiran format (sampler/culebra) — preskoci
        ring, mm = row["ring"], round(row["len"] * 25.4)
        if vitola_name == "Standard":
            vitola_name = f"{ring} RG"  # ime iz dimenzija kad ga proizvod nema
        humidor_vitolas.setdefault(cid, []).append({
            "name": vitola_name, "format": f"{ring} x {mm}mm",
            "smokeTimeMin": smoke_minutes(row["len"], ring),
            "priceEUR": row["price"], "url": row["url"],
            "_ring": ring, "_mm": mm,
        })

    for c in cigars:
        hv = humidor_vitolas.get(c["id"], [])
        base = [{
            "name": name, "format": f"{ring} x {mm}mm",
            "smokeTimeMin": smoke_minutes(mm / 25.4, ring),
            "priceEUR": None, "url": None, "_ring": ring, "_mm": mm,
        } for name, ring, mm in VITOLA_SETS.get(c["id"], [])]

        if base and hv:
            # spoji humidor cijene/linkove na standardne vitole (isti ring, ±8mm)
            extra = []
            for v in hv:
                hit = next((b for b in base if b["_ring"] == v["_ring"]
                            and abs(b["_mm"] - v["_mm"]) <= 8), None)
                if hit:
                    hit["priceEUR"], hit["url"] = v["priceEUR"], v["url"]
                else:
                    extra.append(v)
            vitolas = base + extra
        elif hv:
            # dedupe po imenu
            seen, vitolas = set(), []
            for v in hv:
                if v["name"].lower() in seen:
                    continue
                seen.add(v["name"].lower())
                vitolas.append(v)
        elif base:
            vitolas = base
        else:
            vitolas = [{"name": c["vitola"], "format": c["format"],
                        "smokeTimeMin": c["smokeTimeMin"], "priceEUR": None, "url": None}]

        vitolas.sort(key=lambda v: v["smokeTimeMin"] or 999)
        for v in vitolas:
            v.pop("_ring", None)
            v.pop("_mm", None)
        c["vitolas"] = vitolas

        priced = [v for v in vitolas if v["priceEUR"]]
        if priced:
            cheapest = min(priced, key=lambda v: v["priceEUR"])
            c["priceEUR"] = cheapest["priceEUR"]
            c["priceApprox"] = False
            c["priceUrl"] = cheapest["url"]
            if "The Humidor" not in c["availabilityHR"]:
                c["availabilityHR"].append("The Humidor")
        # default polja = srednja vitola
        mid = vitolas[len(vitolas) // 2]
        c["vitola"], c["format"] = mid["name"], mid["format"] or c["format"]
        c["smokeTimeMin"] = mid["smokeTimeMin"] or c["smokeTimeMin"]

        if not c.get("priceUrl"):
            slug = BRAND_SLUGS.get(c["brand"])
            c["priceUrl"] = HAVANA.format(slug) if slug and "Havana Shop" in c["availabilityHR"] else None

    (DATA / "cigars.json").write_text(
        json.dumps(cigars, ensure_ascii=False, indent=1), encoding="utf-8")

    n_humidor = len(humidor_vitolas)
    n_multi = sum(1 for c in cigars if len(c["vitolas"]) > 1)
    print(f"cigara: {len(cigars)} | s humidor podacima: {n_humidor} | s 2+ vitola: {n_multi}")
    if unmatched:
        uniq = sorted({u.split(' ')[0] + ' ' + u.split(' ')[1] if len(u.split(' ')) > 1 else u for u in unmatched})
        print(f"nepovezano ({len(unmatched)} proizvoda): " + "; ".join(uniq[:25]))


if __name__ == "__main__":
    main()
