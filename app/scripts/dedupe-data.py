# -*- coding: utf-8 -*-
"""Uklanja duplikate ID-jeva u generiranim JSON indeksima (idempotentno).

Pipeline-i (excel-to-brandy-json.py, enrich-cigars.py) povremeno stvore koliziju
ID-jeva. Pokreni ovo NA KRAJU regeneracije da app ostane ispravan:

  python scripts/dedupe-data.py

- brandies/whiskies/rums/gins: prava duplikata (isti proizvod) -> zadrzi jedan,
  preferiraj naziv koji NIJE cijeli velikim slovima (kurirani), pa vecu cijenu.
- cigars: kolizije su cesto RAZLICITI proizvodi (razlicita linija) -> ID se
  uniuje dodavanjem slug-a linije.
"""
import json
import re
import unicodedata
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "src" / "data"


def slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def price_max(entry) -> float:
    p = entry.get("priceEUR")
    if isinstance(p, dict):
        return p.get("max") or 0
    if isinstance(p, (int, float)):
        return p
    return 0


def dedupe_drinks(path: Path):
    """Zadrzi jednu stavku po ID-u (isti proizvod iz dvije pipeline)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    best: dict[str, dict] = {}
    for e in data:
        eid = e["id"]
        if eid not in best:
            best[eid] = e
            continue
        cur = best[eid]
        name = e.get("name", "")
        cur_name = cur.get("name", "")
        e_curated = not name.isupper()
        cur_curated = not cur_name.isupper()
        # preferiraj kurirani naziv; ako oba ista, vecu (svjeziju) cijenu
        if (e_curated, price_max(e)) > (cur_curated, price_max(cur)):
            best[eid] = e
    out = [e for e in data if e is best[e["id"]]]
    removed = len(data) - len(out)
    if removed:
        path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return removed


def dedupe_cigars(path: Path):
    """Kolizije su razliciti proizvodi -> uniuj ID slug-om linije/vitole."""
    data = json.loads(path.read_text(encoding="utf-8"))
    seen: set[str] = set()
    changed = 0
    for c in data:
        cid = c["id"]
        if cid not in seen:
            seen.add(cid)
            continue
        suffix = slug(c.get("line", "")) or slug(c.get("vitola", "")) or "v"
        new_id = f"{cid}-{suffix}"
        n = 2
        while new_id in seen:
            new_id = f"{cid}-{suffix}-{n}"
            n += 1
        c["id"] = new_id
        seen.add(new_id)
        changed += 1
    if changed:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return changed


# isti proizvod pogresno podijeljen zbog ID kolizije ili encodinga (Dias/Días de Gloria)
LINE_BY_ID = {
    "cig-montecristo-no4": "No. 4",
    "cig-montecristo-no2": "No. 2",
    "cig-juan-lopez-seleccion-no2": "Selección No. 2",
}


# zadrzi ove ID-jeve kad se spoje duplikati iste linije
CANONICAL_CIGAR_ID = {
    "aj-fernandez|dias-de-gloria": "cig-aj-fernandez-dias-de-gloria",
    "macanudo|cafe": "cig-macanudo-cafe",
    "joya-de-nicaragua|antano-1970": "cig-joya-de-nicaragua-antano",
    "partagas|serie-d": "cig-partagas-serie-d4",
    "padron|1926-serie": "cig-padron-1926",
    "montecristo|no-4": "cig-montecristo-no4",
}


def norm_product_url(url: str) -> str:
    if not url:
        return ""
    u = url.split("?")[0].rstrip("/").lower()
    return u.replace("/hr/", "/").replace("/en/", "/")


def vitola_urls(c: dict) -> set[str]:
    return {norm_product_url(v["url"]) for v in c.get("vitolas", []) if v.get("url")}


def entry_score(c: dict) -> tuple:
    line = c.get("line", "")
    ascii_line = unicodedata.normalize("NFKD", line).encode("ascii", "ignore").decode()
    has_diacritics = line != ascii_line
    notes = (c.get("notes") or {}).get("hr", "")
    curated = "dani slave" in notes or "enklavi" in notes or len(notes) > 80
    brand = slug(c["brand"])
    collision = c["id"].count(brand) > 1 or "-aj-" in c["id"] or "-jl-" in c["id"]
    return (len(c.get("vitolas", [])), has_diacritics, curated, not collision, -len(c["id"]))


def merge_vitolas(target: dict, source: dict):
    seen_urls = vitola_urls(target)
    seen_names = {v["name"].lower() for v in target.get("vitolas", [])}
    for v in source.get("vitolas", []):
        url = v.get("url")
        name = v["name"].lower()
        if url and url in seen_urls:
            continue
        if name in seen_names and not url:
            continue
        target.setdefault("vitolas", []).append(v)
        if url:
            seen_urls.add(url)
        seen_names.add(name)
    prices = [v["priceEUR"] for v in target.get("vitolas", []) if v.get("priceEUR")]
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


def merge_cigar_lines(path: Path) -> int:
    """Spoji iste linije (brend + normalizirano ime) u jedan zapis."""
    data = json.loads(path.read_text(encoding="utf-8"))
    for c in data:
        fix = LINE_BY_ID.get(c["id"])
        if fix:
            c["line"] = fix

    groups: dict[str, list[dict]] = {}
    for c in data:
        key = slug(c["brand"]) + "|" + slug(c.get("line", ""))
        groups.setdefault(key, []).append(c)

    remove_ids: set[str] = set()
    merged = 0
    for key, group in groups.items():
        if len(group) < 2 or not should_merge_group(group):
            continue
        group.sort(key=entry_score, reverse=True)
        keeper, *rest = group
        canonical = CANONICAL_CIGAR_ID.get(key)
        if canonical:
            keeper["id"] = canonical
        for dup in rest:
            merge_vitolas(keeper, dup)
            hr = (keeper.get("notes") or {}).get("hr", "")
            dup_hr = (dup.get("notes") or {}).get("hr", "")
            if len(dup_hr) > len(hr) and "Dostupno u HR" not in dup_hr:
                keeper["notes"] = dup["notes"]
            remove_ids.add(dup["id"])
            merged += 1

    if not merged:
        merged = 0
    out = [c for c in data if c["id"] not in remove_ids]
    for c in out:
        key = slug(c["brand"]) + "|" + slug(c.get("line", ""))
        cid = CANONICAL_CIGAR_ID.get(key)
        if cid:
            c["id"] = cid
    if merged or remove_ids:
        path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return merged


# UTF-8 interpunkcija/dijakritici pogresno dekodirani kao OEM codepage
MOJIBAKE = {
    "ÔÇö": "—", "ÔÇô": "–", "ÔÇť": "“", "ÔÇŁ": "”", "ÔÇÖ": "’",
    "ÔÇś": "‘", "ÔÇŽ": "…", "┬á": " ", "┬░": "°",
    "├í": "á", "├ę": "é", "├ş": "í", "├│": "ó", "├║": "ú", "├▒": "ñ",
    "├╝": "ü", "├ó": "â", "┼ż": "ž", "┼í": "š", "─ç": "ć", "─Ź": "č", "─Ĺ": "đ",
}


def fix_encoding_pass():
    """Globalni popravak mojibake sekvenci u svim data JSON-ovima."""
    total = 0
    roots = [DATA, DATA.parent.parent / "scripts" / "seed"]
    for root in roots:
        if not root.exists():
            continue
        for p in root.glob("*.json"):
            s = p.read_text(encoding="utf-8")
            orig = s
            for k, v in MOJIBAKE.items():
                s = s.replace(k, v)
            if s != orig:
                p.write_text(s, encoding="utf-8")
                total += sum(orig.count(k) for k in MOJIBAKE)
    if total:
        print(f"encoding: popravljeno {total} mojibake sekvenci")


def main():
    fix_encoding_pass()
    for name in ["rums", "whiskies", "brandies", "gins", "coffees"]:
        p = DATA / f"{name}.json"
        if p.exists():
            r = dedupe_drinks(p)
            if r:
                print(f"{name}: uklonjeno {r} duplikata")
    cp = DATA / "cigars.json"
    c = dedupe_cigars(cp)
    if c:
        print(f"cigars: uniiran {c} kolidirajucih ID-jeva")
    m = merge_cigar_lines(cp)
    if m:
        print(f"cigars: spojeno {m} duplikatnih linija")
    print("dedupe gotovo.")


if __name__ == "__main__":
    main()
