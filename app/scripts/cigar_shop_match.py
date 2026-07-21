# -*- coding: utf-8 -*-
"""Shared cigar shop matching / dedupe helpers.

Extracted from sync-hr-shops.py and dedupe-data.py so market-catalog export,
HR sync, and pipeline dedupe share one matching process for:
- brand aliases (same cigar under two names)
- line rules + fuzzy line match
- pack / dimension stripping
- vitola upsert / unique-by-name
- URL normalization
- line merge (brand|line groups)
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

FRACTIONS = {"½": 0.5, "¼": 0.25, "¾": 0.75, "⅛": 0.125, "⅜": 0.375, "⅝": 0.625, "⅞": 0.875}
FRACTION_CHARS = "".join(FRACTIONS)

# brand alias -> canonical brand name in cigars.json
BRAND_ALIASES = {
    "bundle selection by cusano": "Cusano",
    "cusano": "Cusano",
    "arturo fuente": "Arturo Fuente",
    "joya de nicaragua": "Joya de Nicaragua",
    "joya silver": "Joya de Nicaragua",
    "joya red": "Joya de Nicaragua",
    "joya black": "Joya de Nicaragua",
    # Humidor often omits "AJ Fernandez" from product titles
    "blend 15": "AJ Fernandez",
    "last call": "AJ Fernandez",
    "enclave": "AJ Fernandez",
    "bellas artes": "AJ Fernandez",
    "san lotano": "AJ Fernandez",
    "dias de gloria": "AJ Fernandez",
    "new world": "AJ Fernandez",
    "ajf 20th": "AJ Fernandez",
    "ajf new world": "AJ Fernandez",
    "liga privada": "Drew Estate",
    "undercrown": "Drew Estate",
    "herrera esteli": "Drew Estate",
    "padron": "Padrón",
    "oscar valladares": "Oscar Valladares",
    "2012 by oscar": "Oscar Valladares",
}

# (brand_norm, line keywords in product name) -> existing id or None
LINE_RULES: list[tuple[str, tuple[str, ...], str | None]] = [
    ("arturo fuente", ("hemingway",), "cig-arturo-fuente-hemingway"),
    ("arturo fuente", ("opus", "opusx"), "cig-fuente-opus-x"),
    ("arturo fuente", ("don carlos",), None),
    ("arturo fuente", ("anejo", "añejo"), None),
    ("arturo fuente", ("brevas",), None),
    ("arturo fuente", ("curly head",), None),
    ("arturo fuente", ("chateau",), None),
    (
        "arturo fuente",
        ("gran reserva", "exquisitos", "petit corona", "cuban corona", "cubanitos"),
        "cig-arturo-fuente-gran-reserva",
    ),
    ("joya de nicaragua", ("antano 1970", "antano gran reserva", "antano ct"), "cig-joya-de-nicaragua-antano"),
    ("joya de nicaragua", ("joya red", "red robusto"), "cig-joya-red"),
    ("joya de nicaragua", ("joya silver",), None),
    ("joya de nicaragua", ("joya black",), None),
    ("joya de nicaragua", ("numero uno", "número uno"), None),
    ("joya de nicaragua", ("cuatro cinco",), None),
    ("joya de nicaragua", ("cinco decadas", "cinco décadas"), None),
    ("joya de nicaragua", ("clasico medio siglo", "clásico medio siglo"), None),
    ("joya de nicaragua", ("rosalones",), None),
    ("cusano", (), "cig-cusano"),
    ("aj fernandez", ("blend 15",), "cig-aj-fernandez-blend-15"),
    ("aj fernandez", ("last call",), "cig-aj-fernandez-last-call"),
    ("aj fernandez", ("enclave",), "cig-aj-fernandez-aj-enclave"),
    ("aj fernandez", ("bellas artes",), "cig-aj-fernandez-bellas-artes"),
    ("aj fernandez", ("dias de gloria",), "cig-aj-fernandez-dias-de-gloria"),
    ("aj fernandez", ("san lotano",), "cig-aj-fernandez-aj-san-lotano"),
    ("aj fernandez", ("20th anniversary",), "cig-aj-fernandez-20th-anniversary"),
    ("aj fernandez", ("dorado sampler",), "cig-aj-fernandez-new-world-dorado-sampler"),
    ("aj fernandez", ("new world sampler",), "cig-aj-fernandez-new-world-sampler"),
    ("aj fernandez", ("premium sampler",), "cig-aj-fernandez-premium-sampler"),
    ("aj fernandez", ("toro sampler",), "cig-aj-fernandez-toro-sampler"),
    ("aj fernandez", ("new world",), "cig-aj-fernandez-new-world"),
    ("drew estate", ("liga privada",), "cig-drew-estate-de-liga-privada"),
    ("drew estate", ("undercrown",), "cig-drew-estate-de-undercrown"),
    ("drew estate", ("herrera",), "cig-drew-estate-de-herrera"),
    ("drew estate", ("acid",), "cig-drew-estate-de-acid"),
    ("padrón", ("1926",), "cig-padron-1926"),
    ("padron", ("1926",), "cig-padron-1926"),
    ("padrón", ("1964",), "cig-padron-padron-1964"),
    ("padron", ("1964",), "cig-padron-padron-1964"),
    ("padrón", ("damaso",), "cig-padron-padron-damaso"),
    ("padron", ("damaso",), "cig-padron-padron-damaso"),
    ("padrón", ("family reserve",), "cig-padron-padron-family-reserve"),
    ("padron", ("family reserve",), "cig-padron-padron-family-reserve"),
]

# zadrzi ove ID-jeve kad se spoje duplikati iste linije (dedupe-data.py)
CANONICAL_CIGAR_ID = {
    "aj-fernandez|dias-de-gloria": "cig-aj-fernandez-dias-de-gloria",
    "macanudo|cafe": "cig-macanudo-cafe",
    "joya-de-nicaragua|antano-1970": "cig-joya-de-nicaragua-antano",
    "partagas|serie-d": "cig-partagas-serie-d4",
    "padron|1926-serie": "cig-padron-1926",
    "montecristo|no-4": "cig-montecristo-no4",
}

LINE_BY_ID = {
    "cig-montecristo-no4": "No. 4",
    "cig-montecristo-no2": "No. 2",
    "cig-juan-lopez-seleccion-no2": "Selección No. 2",
}

VITOLA_NAME_TOKENS = (
    "Robusto Grande",
    "Double Robusto",
    "Short Robusto",
    "Petit Corona",
    "Gran Consul",
    "Gran Cónsul",
    "Robusto",
    "Toro",
    "Churchill",
    "Corona",
    "Figurado",
    "Lonsdale",
    "Panatela",
    "Torpedo",
    "Gordo",
    "Diadema",
    "Machito",
    "Signature",
    "Classic",
    "Short Story",
    "Best Seller",
    "Exquisitos",
    "Cuban Corona",
    "Cubanitos",
    "PerfecXion X",
)


def parse_length_inches(raw: str) -> float:
    s = raw.strip()
    total = 0.0
    for part in s.split():
        if part in FRACTIONS:
            total += FRACTIONS[part]
            continue
        m = re.match(rf"^(\d+(?:\.\d+)?)([{FRACTION_CHARS}])?$", part)
        if not m:
            raise ValueError(f"cannot parse length: {raw!r}")
        total += float(m.group(1))
        if m.group(2):
            total += FRACTIONS[m.group(2)]
    return total


def parse_humidor_dims(name: str) -> tuple[str, int | None, int | None]:
    """'Arturo Fuente Hemingway Signature 6 x 46' -> (base, 152mm, 46)"""
    dim_re = re.compile(rf"^(.*?)\s+([\d\s{FRACTION_CHARS}.]+)\s*[xX]\s*(\d+)\s*$")
    m = dim_re.match(name.strip())
    if not m:
        return name.strip(), None, None
    base = m.group(1).strip()
    try:
        length_in = parse_length_inches(m.group(2))
    except ValueError:
        return name.strip(), None, None
    ring = int(m.group(3))
    return base, int(round(length_in * 25.4)), ring


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s.lower().strip())


def slugify(s: str) -> str:
    s = norm(s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def slug(text: str) -> str:
    """ASCII slug used by dedupe-data merge keys."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def parse_pack_suffix(name: str) -> tuple[str, int | None]:
    """'Montecristo No.2/25' -> ('Montecristo No.2', 25)"""
    m = re.search(r"^(.+?)/(\d+)\*?\s*$", name.strip())
    if m:
        return m.group(1).strip(), int(m.group(2))
    return name.strip(), None


def norm_product_url(url: str | None) -> str:
    if not url or not isinstance(url, str):
        return ""
    u = url.split("?")[0].split("#")[0].rstrip("/").lower()
    return u.replace("/hr/", "/").replace("/en/", "/")


def build_brand_detectors(cigars: list[dict]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for brand in {c["brand"] for c in cigars if isinstance(c.get("brand"), str)}:
        pairs.append((norm(brand), brand))
    for alias, brand in BRAND_ALIASES.items():
        pairs.append((norm(alias), brand))
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for alias, brand in sorted(pairs, key=lambda x: -len(x[0])):
        if alias in seen:
            continue
        seen.add(alias)
        out.append((alias, brand))
    return out


def detect_brand(product_name: str, detectors: list[tuple[str, str]]) -> str | None:
    low = norm(product_name)
    for alias, brand in detectors:
        if low.startswith(alias) or f" {alias} " in f" {low} ":
            return brand
    return None


def detect_line_id(brand: str, product_name: str) -> str | None:
    bnorm = norm(brand)
    low = norm(product_name)
    for brand_key, keywords, cid in LINE_RULES:
        if brand_key != bnorm:
            continue
        if not keywords or any(kw in low for kw in keywords if kw):
            return cid
    return None


def line_name_from_product(brand: str, product_name: str) -> str:
    low = norm(product_name)
    b = norm(brand)
    rest = low
    for prefix in [b, "bundle selection by cusano", "joya de nicaragua", "2012 by oscar", "oscar valladares"]:
        if rest.startswith(prefix):
            rest = rest[len(prefix) :].strip(" -/")
    rest = re.sub(r"/\d+\*?$", "", rest).strip()
    rest = re.sub(r"\([^)]*\d+\s*[x×]\s*\d+[^)]*\)", " ", rest)
    rest = re.sub(r"\b\d+\s*[x×]\s*\d+(\.\d+)?\b", " ", rest)
    rest = re.sub(r"\bbox\s*pressed\b", " ", rest)
    rest = re.sub(r"^\d{4}\b", " ", rest)
    rest = re.sub(r"\s+", " ", rest).strip()
    for vit in (
        "robusto grande",
        "double robusto",
        "short robusto",
        "petit corona",
        "robusto",
        "toro",
        "churchill",
        "corona",
        "figurado",
        "lonsdale",
        "panatela",
        "torpedo",
        "gordo",
        "diadema",
        "consul",
        "machito",
    ):
        if rest.endswith(" " + vit):
            rest = rest[: -len(vit)].strip()
            break
    return rest.title() if rest else brand


def vitola_name_key(name: str, brand: str | None = None) -> str:
    """Collapse 'Montecristo No.4', 'No.4', 'No.4/' into one key."""
    n = norm(name).rstrip(" /")
    if brand:
        b = norm(brand)
        if n.startswith(b + " "):
            n = n[len(b) :].strip()
    n = re.sub(r"\s+", " ", n).strip(" /-")
    return n


def unique_vitolas(cigar: dict) -> list[dict]:
    """Mirror of app/src/lib/cigarVitola.ts uniqueVitolas(), plus brand-prefix collapse."""
    seen: set[str] = set()
    out: list[dict] = []
    brand = str(cigar.get("brand") or "")
    for v in cigar.get("vitolas") or []:
        if not isinstance(v, dict):
            continue
        key = vitola_name_key(str(v.get("name") or ""), brand)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(v)
    return out


def vitola_from_product(product_name: str, brand: str) -> str:
    base, _pack = parse_pack_suffix(product_name)
    base, _mm, _ring = parse_humidor_dims(base)
    low = norm(base)
    b = norm(brand)
    if low.startswith(b):
        low = low[len(b) :].strip(" -/")
    low = re.sub(r"/\d+\*?$", "", low).strip()
    low = re.sub(r"\([^)]*\d+\s*[x×]\s*\d+[^)]*\)", " ", low)
    low = re.sub(r"\s+", " ", low).strip()
    for vit in VITOLA_NAME_TOKENS:
        if norm(vit) in low or low.endswith(norm(vit)):
            return vit
    parts = base.split()
    if len(parts) >= 2:
        return " ".join(parts[-2:]).title()
    return base.title() if base else "Standard"


def find_existing_cigar(cigars: list[dict], brand: str, product_name: str) -> dict | None:
    """Same resolution order as sync-hr-shops find_or_create (without creating)."""
    cid = detect_line_id(brand, product_name)
    if cid:
        for c in cigars:
            if c.get("id") == cid:
                return c
    line = line_name_from_product(brand, product_name)
    for c in cigars:
        if c.get("brand") == brand and norm(str(c.get("line") or "")) == norm(line):
            return c
    for c in cigars:
        if c.get("brand") != brand:
            continue
        cline = norm(str(c.get("line") or ""))
        if not cline or not line:
            continue
        if norm(line) in cline or cline in norm(line):
            return c
    return None


def parse_format_size(fmt: str | None) -> tuple[int | None, int | None]:
    if not fmt or not isinstance(fmt, str) or fmt.strip() in ("", "—", "-"):
        return None, None
    m = re.search(r"(\d+)\s*[x×]\s*(\d+)\s*mm", fmt, re.IGNORECASE)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def product_dims(product_name: str, details: dict | None = None) -> tuple[int | None, int | None]:
    details = details or {}
    ring = details.get("ringGauge") if isinstance(details.get("ringGauge"), int) else None
    length_mm = None
    if isinstance(details.get("lengthCm"), (int, float)):
        length_mm = int(round(float(details["lengthCm"]) * 10))
    elif isinstance(details.get("lengthMm"), int):
        length_mm = details["lengthMm"]
    if ring is not None and length_mm is not None:
        return ring, length_mm
    _base, mm, r = parse_humidor_dims(parse_pack_suffix(product_name)[0])
    return r if ring is None else ring, mm if length_mm is None else length_mm


def match_vitola_in_cigar(
    cigar: dict,
    product_name: str,
    *,
    brand: str,
    details: dict | None = None,
) -> dict | None:
    """Match shop product to a vitola: name, then ring ±8mm (enrich-cigars)."""
    vitolas = unique_vitolas(cigar)
    if not vitolas:
        return None
    want = vitola_name_key(vitola_from_product(product_name, brand), brand)
    product_low = norm(product_name)
    for v in vitolas:
        if vitola_name_key(str(v.get("name") or ""), brand) == want:
            return v
    # Substring match only when exactly one vitola qualifies (avoid Habano/Brazil collisions).
    contains_hits = [
        v
        for v in vitolas
        if want
        and (
            want in vitola_name_key(str(v.get("name") or ""), brand)
            or vitola_name_key(str(v.get("name") or ""), brand) in want
            or vitola_name_key(str(v.get("name") or ""), brand) in product_low
        )
    ]
    if len(contains_hits) == 1:
        return contains_hits[0]
    ring, mm = product_dims(product_name, details)
    if ring is not None and mm is not None:
        size_hits = []
        for v in vitolas:
            vr, vm = parse_format_size(v.get("format") if isinstance(v.get("format"), str) else None)
            if vr == ring and vm is not None and abs(vm - mm) <= 8:
                size_hits.append(v)
        if len(size_hits) == 1:
            return size_hits[0]
        if len(size_hits) > 1 and contains_hits:
            overlap = [v for v in size_hits if v in contains_hits]
            if len(overlap) == 1:
                return overlap[0]
    if len(vitolas) == 1:
        return vitolas[0]
    return None


def shop_dedupe_key(brand: str, product_name: str) -> str:
    """merge_shop_rows key: brand|vitola|line."""
    return (
        f"{norm(brand)}|"
        f"{norm(vitola_from_product(product_name, brand))}|"
        f"{norm(line_name_from_product(brand, product_name))}"
    )


def vitola_urls(c: dict) -> set[str]:
    return {norm_product_url(v.get("url")) for v in c.get("vitolas") or [] if v.get("url")}


def entry_score(c: dict) -> tuple:
    line = c.get("line", "") or ""
    ascii_line = unicodedata.normalize("NFKD", line).encode("ascii", "ignore").decode()
    has_diacritics = line != ascii_line
    notes = (c.get("notes") or {}).get("hr", "") if isinstance(c.get("notes"), dict) else ""
    curated = "dani slave" in notes or "enklavi" in notes or len(notes) > 80
    brand = slug(str(c.get("brand") or ""))
    cid = str(c.get("id") or "")
    collision = cid.count(brand) > 1 or "-aj-" in cid or "-jl-" in cid
    return (len(c.get("vitolas") or []), has_diacritics, curated, not collision, -len(cid))


def merge_vitolas(target: dict, source: dict) -> None:
    brand = str(target.get("brand") or source.get("brand") or "")
    seen_urls = vitola_urls(target)
    seen_names = {vitola_name_key(str(v.get("name") or ""), brand) for v in target.get("vitolas") or []}
    for v in source.get("vitolas") or []:
        if not isinstance(v, dict):
            continue
        url = norm_product_url(v.get("url")) if v.get("url") else ""
        name = vitola_name_key(str(v.get("name") or ""), brand)
        if url and url in seen_urls:
            # Prefer filling missing fields on existing entry with same URL.
            continue
        if name and name in seen_names:
            # Same vitola under two names — merge URL/price onto keeper.
            for existing in target.get("vitolas") or []:
                if vitola_name_key(str(existing.get("name") or ""), brand) != name:
                    continue
                if url and not existing.get("url"):
                    existing["url"] = v.get("url")
                if v.get("priceEUR") is not None and existing.get("priceEUR") is None:
                    existing["priceEUR"] = v.get("priceEUR")
                if v.get("format") and (not existing.get("format") or existing.get("format") == "—"):
                    existing["format"] = v.get("format")
                break
            continue
        target.setdefault("vitolas", []).append(v)
        if url:
            seen_urls.add(url)
        if name:
            seen_names.add(name)
    # Final pass: unique by collapsed name, prefer URL'd entries.
    collapsed: dict[str, dict] = {}
    for v in target.get("vitolas") or []:
        key = vitola_name_key(str(v.get("name") or ""), brand)
        if not key:
            continue
        prev = collapsed.get(key)
        if not prev:
            collapsed[key] = v
            continue
        # Prefer product URL / priced.
        score = (1 if v.get("url") else 0, 1 if v.get("priceEUR") is not None else 0)
        prev_score = (1 if prev.get("url") else 0, 1 if prev.get("priceEUR") is not None else 0)
        if score > prev_score:
            collapsed[key] = v
    target["vitolas"] = list(collapsed.values())
    prices = [v["priceEUR"] for v in target.get("vitolas") or [] if v.get("priceEUR")]
    if prices:
        target["priceEUR"] = min(prices)


def should_merge_group(group: list[dict]) -> bool:
    if len(group) < 2:
        return False
    urls = [vitola_urls(c) for c in group]
    for i in range(len(urls)):
        for j in range(i + 1, len(urls)):
            a, b = urls[i], urls[j]
            if not a or not b:
                return True
            if a & b or a <= b or b <= a:
                return True
    return False


def merge_duplicate_cigar_lines(cigars: list[dict]) -> tuple[list[dict], int]:
    """In-memory merge_cigar_lines from dedupe-data.py (does not write disk)."""
    data = [dict(c) for c in cigars]
    for c in data:
        fix = LINE_BY_ID.get(c.get("id"))
        if fix:
            c["line"] = fix

    groups: dict[str, list[dict]] = {}
    for c in data:
        key = slug(str(c.get("brand") or "")) + "|" + slug(str(c.get("line") or ""))
        groups.setdefault(key, []).append(c)

    remove_ids: set[str] = set()
    merged = 0
    keepers: dict[str, dict] = {c["id"]: c for c in data}
    for key, group in groups.items():
        if len(group) < 2 or not should_merge_group(group):
            continue
        group.sort(key=entry_score, reverse=True)
        keeper, *rest = group
        canonical = CANONICAL_CIGAR_ID.get(key)
        if canonical:
            old_id = keeper["id"]
            keeper["id"] = canonical
            if old_id != canonical and old_id in keepers:
                keepers.pop(old_id, None)
            keepers[canonical] = keeper
        for dup in rest:
            merge_vitolas(keeper, dup)
            notes = keeper.get("notes") if isinstance(keeper.get("notes"), dict) else {}
            dup_notes = dup.get("notes") if isinstance(dup.get("notes"), dict) else {}
            hr = notes.get("hr", "") if notes else ""
            dup_hr = dup_notes.get("hr", "") if dup_notes else ""
            if len(dup_hr) > len(hr) and "Dostupno u HR" not in dup_hr:
                keeper["notes"] = dup["notes"]
            remove_ids.add(dup["id"])
            merged += 1

    out = [c for c in data if c["id"] not in remove_ids]
    for c in out:
        key = slug(str(c.get("brand") or "")) + "|" + slug(str(c.get("line") or ""))
        cid = CANONICAL_CIGAR_ID.get(key)
        if cid:
            c["id"] = cid
        # Collapse same vitola under two names (No.4 / Montecristo No.4).
        merge_vitolas(c, {"brand": c.get("brand"), "vitolas": []})
    # collapse any remaining id collisions after canonical rewrite
    by_id: dict[str, dict] = {}
    for c in out:
        cid = c["id"]
        if cid not in by_id:
            by_id[cid] = c
            continue
        merge_vitolas(by_id[cid], c)
        merged += 1
    return list(by_id.values()), merged


def resolve_shop_product(
    cigars: list[dict],
    product_name: str,
    *,
    detectors: list[tuple[str, str]],
    details: dict | None = None,
    url: str | None = None,
) -> tuple[dict | None, dict | None, str | None]:
    """Map a shop product to (cigar, vitola, brand). Any None means unmapped."""
    brand = detect_brand(product_name, detectors)
    nurl = norm_product_url(url)
    if nurl:
        for c in cigars:
            for v in unique_vitolas(c):
                if norm_product_url(v.get("url")) == nurl:
                    return c, v, str(c.get("brand") or brand or "")
            if norm_product_url(c.get("priceUrl")) == nurl:
                vit = match_vitola_in_cigar(c, product_name, brand=str(c.get("brand") or brand or ""), details=details)
                return c, vit, str(c.get("brand") or brand or "")

    if not brand:
        return None, None, None
    cigar = find_existing_cigar(cigars, brand, product_name)
    if not cigar:
        return None, None, brand
    vitola = match_vitola_in_cigar(cigar, product_name, brand=brand, details=details)
    return cigar, vitola, brand
