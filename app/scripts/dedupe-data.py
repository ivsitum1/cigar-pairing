# -*- coding: utf-8 -*-
"""Uklanja duplikate ID-jeva u generiranim JSON indeksima (idempotentno).

Pipeline-i (excel-to-brandy-json.py, enrich-cigars.py) povremeno stvore koliziju
ID-jeva. Pokreni ovo NA KRAJU regeneracije da app ostane ispravan:

  python scripts/dedupe-data.py

- brandies/whiskies/rums/gins: prava duplikata (isti proizvod) -> zadrzi jedan,
  preferiraj naziv koji NIJE cijeli velikim slovima (kurirani), pa vecu cijenu.
- cigars: kolizije su cesto RAZLICITI proizvodi (razlicita linija) -> ID se
  uniuje dodavanjem slug-a linije; iste linije (dva naziva) spajaju se preko
  cigar_shop_match.merge_duplicate_cigar_lines.
"""
import json
from pathlib import Path

from cigar_shop_match import merge_duplicate_cigar_lines, slug

DATA = Path(__file__).resolve().parent.parent / "src" / "data"


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
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def merge_cigar_lines(path: Path) -> int:
    """Spoji iste linije (brend + normalizirano ime) u jedan zapis."""
    data = json.loads(path.read_text(encoding="utf-8"))
    out, merged = merge_duplicate_cigar_lines(data)
    if merged or len(out) != len(data):
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
