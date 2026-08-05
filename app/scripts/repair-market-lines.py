#!/usr/bin/env python3
"""Vraca linije iz market scrapea u brend/linija/vitola strukturu kataloga.

Neptune/Famous scrape je za svaku VITOLU napravio zapis i cijelo ime proizvoda
spustio u `line`, malim slovima i s mjerom u imenu:

    1502   | "xo 7 40", "xo salomon 7 58"        -> linija XO, vitole Lancero/Salomon
    Diesel | "fool s errand simple fool"         -> linija Fool's Errand, vitola Simple Fool
    Aging  | "quattro f55m concerto/espressivo"  -> linija Quattro F55M, vitole Concerto/...

Skripta radi tri stvari, sve tri iz samog imena (nema vanjskog izvora):

1. MJERA IZ IMENA -> vitola. "5 52" = 5 x 52, "61 2 52" = 6 1/2 x 52. Scrape je
   svima upisao istu izmisljenu mjeru (50 x 124mm), pa je ovo jedini pravi
   podatak o dimenziji koji postoji. Godine (2023) i goli brojevi se NE diraju.
2. SPAJANJE. Zapisi iste marke koji dijele pocetak imena, a razlikuju se u
   zadnjih 1-2 tokena, jedna su linija s vise vitola. Rijeci pokrova/izdanja
   (maduro, connecticut, limited...) nisu vitole, pa takve zapise ne spaja —
   Cachito Original i Cachito White Connecticut ostaju odvojeni.
3. VELIKO SLOVO. "fool s errand" -> "Fool's Errand" (apostrof je scrape pojeo).
   "serie s" je izuzetak: to je Serie S, ne Serie's.

Stari ID-jevi idu u cigarIdAliases.json da korisnikov Imam/Probao, ocjena i
dnevnik ostanu vezani. Idempotentno: nakon prolaza linije pocinju velikim
slovom pa ih drugi prolaz vise ne dira.

Usage:
  python3 scripts/repair-market-lines.py --dry-run   # izvjestaj, bez pisanja
  python3 scripts/repair-market-lines.py
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
DATA = APP / "src" / "data"
CIGARS = DATA / "cigars.json"
ALIASES = DATA / "cigarIdAliases.json"
REPORT = APP / "scripts" / "output" / "market_line_repair.md"

# Rijeci koje opisuju pokrov, izdanje ili jakost — nikad ime vitole. Zapis s
# takvim repom je druga MJESAVINA, ne drugi format iste linije.
BLEND_WORDS = {
    "maduro", "natural", "connecticut", "habano", "corojo", "sumatra", "cameroon",
    "criollo", "claro", "colorado", "oscuro", "rosado", "broadleaf", "candela",
    "ecuador", "ecuadorian", "nicaragua", "nicaraguan", "mexican", "brazilian",
    "andres", "shade", "barber", "pole", "edition", "limited", "limitada",
    "especial", "special", "anniversary", "aniversario", "vintage", "selection",
    "original", "white", "black", "blue", "red", "green", "gold", "silver",
    "platinum", "reserva", "reserve", "collection", "series", "serie", "cask",
    "barrel", "infused", "sampler", "gift", "pack", "box", "tin", "glastube",
    "no", "lot", "batch", "serie", "vol",
}

# "No." bez broja je ostatak nakon sto je broj otisao u vitolu ("Mi Querida
# Triqui Traca No." + vitole 448/552). Samo taj rep se skida — "Small Batch" i
# "1926 Serie" su prava imena linija.
DANGLING_NO = re.compile(r"(?i)^no\.?$")

# RUCNA IZNIMKA. Kod vecine marki je "No. 3" dio imena linije (La Aroma de Cuba
# "Edición Especial No. 3"), pa se rep s brojem ne dira. Kod ovih marki je
# obrnuto — broj je oznaka formata, a linija je ono ispred (Laura Chavin Classic
# No. 33/44/55/66/88, Virginy No. 1/2/3). Iz podataka se to ne moze razluciti.
NUMBERED_VITOLA_BRANDS = {"Laura Chavin"}
NUMBERED_TAIL = re.compile(r"(?i)\bno\.?\s*\d+$")

# Prava imena/oblici vitola — rep koji je jedno od njih je format, ne mjesavina.
SHAPE_WORDS = {
    "robusto", "robustos", "toro", "toros", "churchill", "churchills", "lancero",
    "lanceros", "corona", "coronas", "gordo", "gorda", "gordito", "torpedo",
    "belicoso", "belicosos", "perfecto", "salomon", "salomones", "diadema",
    "petit", "petite", "magnum", "double", "figurado", "piramide", "pyramid",
    "sublime", "sublimes", "grande", "gran", "rothschild", "sixty", "lonsdale",
    "panetela", "panatela", "culebra", "cigarillos", "chico", "gigante",
    "presidente", "immenso", "mini", "short", "corona", "boolit", "nub",
}

# Mjera na kraju imena: "5 52", "61 2 52" (6 1/2 x 52, polovica zaljepljena za
# duljinu), "6 1 4 52" (6 1/4). Duljina 3-9 cola, prsten 30-90 (Asylum ide do
# 9 x 90), razlomak mora biti pravi (1/2, 1/4, 3/4, 5/8...). Godine i goli
# brojevi tako ne prolaze.
SIZE_RE = re.compile(r"\s+(\d)\s*(?:(\d)\s+(\d)\s+)?(\d{2})$")
FRACTIONS = {2, 4, 8, 16}

# Kod vitole u kojem su duljina i prsten zaljepljeni: Nub 460 = 4 x 60,
# Asylum 770 = 7 x 70. Ime vitole ostaje kod, mjera se cita iz njega.
SKU_RE = re.compile(r"^([3-9])(\d{2})$")


def sku_size(token: str) -> tuple[int, int] | None:
    m = SKU_RE.fullmatch(token)
    if not m:
        return None
    ring = int(m.group(2))
    return (ring, round(int(m.group(1)) * 25.4)) if 26 <= ring <= 90 else None

LOWER_PARTICLES = {"de", "del", "y", "di", "da", "du", "des", "of", "the", "and",
                   "von", "van", "el", "las", "los"}
KEEP_UPPER = {"xo", "xxo", "adv", "epc", "taa", "lfd", "osa", "sp", "ii", "iii",
              "iv", "vi", "vii", "viii", "ix", "xi", "xii", "bhk", "ese", "pca",
              "bbq", "obs", "lbv", "hba", "anb", "fyt", "usa", "ec", "gr"}


def strip_brand_tail(brand: str, line: str) -> str:
    """Splitter je kod marki s veznikom ostavio rep marke u liniji.

    "Cuervo y Sobrinos" + "y sobrinos historiador" -> "historiador".
    Skida najdulji poklapajuci rep marke, ali samo ako sto ostane nije prazno.
    """
    bt = slug(brand).split("-")
    lt = line.split()
    for start in range(len(bt)):
        tail = bt[start:]
        if len(lt) > len(tail) and [slug(t) for t in lt[: len(tail)]] == tail:
            return " ".join(lt[len(tail):])
    return line


def parse_size(line: str) -> tuple[str, tuple[int, int] | None]:
    """-> (ime bez mjere, (prsten, mm)). "blackfin s parlay 5 52" -> 52 x 127mm."""
    m = SIZE_RE.search(line)
    if not m:
        return line, None
    inch = int(m.group(1))
    if m.group(2):
        num, den = int(m.group(2)), int(m.group(3))
        if den not in FRACTIONS or num >= den:
            m = re.search(r"\s+(\d)\s+(\d{2})$", line)   # bez razlomka
            if not m:
                return line, None
            inch, ring = int(m.group(1)), int(m.group(2))
        else:
            inch += num / den
            ring = int(m.group(4))
    else:
        ring = int(m.group(4))
    if not (3 <= inch <= 9 and 30 <= ring <= 90):
        return line, None
    rest = line[: m.start()].strip()
    toks = rest.split()
    last = toks[-1] if toks else ""
    prev = toks[-2].lower().rstrip(".") if len(toks) > 1 else ""
    if (re.fullmatch(r"\d+", last) and not re.fullmatch(r"(19|20)\d\d", last)
            and prev not in {"no", "lot", "batch", "serie", "series", "vol"}):
        return line, None   # rep je slozena oznaka ("Miami 8 9 8 63"), ne cista mjera
    if last.lower().rstrip(".") in {"no", "lot", "batch", "serie", "series", "vol"}:
        return line, None   # "no 660" = vitola No. 660, ne 6 x 60
    return rest, (ring, round(inch * 25.4))


def titlecase(line: str) -> str:
    """"fool s errand" -> "Fool's Errand"; "serie s" -> "Serie S"; "f55m" -> "F55M"."""
    words = line.split()
    out: list[str] = []
    for i, w in enumerate(words):
        prev = words[i - 1].lower() if i else ""
        if w == "s" and prev in {"serie", "series"}:
            out.append("S")
            continue
        if w == "s" and out:  # apostrof koji je scrape pojeo
            out[-1] += "'s"
            continue
        if re.fullmatch(r"\d+(st|nd|rd|th)", w.lower()):
            out.append(w.lower())
        elif w.lower() == "le" and i + 1 < len(words) and re.fullmatch(r"(19|20)\d\d", words[i + 1]):
            out.append("LE")  # Limited Edition, ne francuski clan
        elif (w.lower() in KEEP_UPPER or re.fullmatch(r"\d*x{1,3}l", w.lower())
                or re.fullmatch(r"[a-z]*\d+[a-z]*", w.lower())):
            out.append(w.upper())
        elif w.lower() == "no" and i + 1 < len(words) and words[i + 1].isdigit():
            out.append("No.")
        elif i and w.lower() in LOWER_PARTICLES:
            out.append(w.lower())
        else:
            out.append(w[:1].upper() + w[1:])
    return " ".join(out)


def slug(text: str) -> str:
    t = unicodedata.normalize("NFKD", text)
    t = "".join(ch for ch in t if not unicodedata.combining(ch)).lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def smoke(mm: int) -> int:
    return max(20, min(120, round(mm / 2.6)))  # ista formula kao build-market-cigars.py


# Kljuc linije ne smije stati na vezniku: "year of the snake 2025 by" + "oscar
# valladares" nije linija s vitolom, nego suradnja s drugom kucom.
DANGLING = {"by", "de", "del", "of", "the", "and", "con", "with", "x", "y", "in",
            "from", "for", "la", "el", "las", "los", "du", "di", "da", "no"}


def vitola_tail(tokens: list[str], numbered: bool = False) -> bool:
    """Je li rep (1-2 tokena) ime vitole, a ne druga mjesavina?"""
    if not tokens or len(tokens) > 2:
        return False
    low = [t.lower().rstrip(".") for t in tokens]
    if numbered and len(low) == 2 and low[0] == "no" and re.fullmatch(r"\d+", low[1]):
        return True                      # samo za NUMBERED_VITOLA_BRANDS
    if len(low) == 1 and sku_size(low[0]):
        return True
    if any(t in BLEND_WORDS or re.fullmatch(r"\d+", t) for t in low):
        return False
    return any(t in SHAPE_WORDS for t in low) or len(tokens) <= 2


def group_key(records: list[dict], bases: dict[str, str]) -> dict[str, str]:
    """ID zapisa -> kljuc linije. Najdulji pocetak koji dijele >=2 zapisa pobjeduje."""
    by_brand: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_brand[r["brand"]].append(r)

    keys: dict[str, str] = {}
    for brand, recs in by_brand.items():
        # kandidati: ime bez zadnjeg 1 ili 2 tokena, kad je taj rep ime vitole
        support: dict[str, list[tuple[dict, list[str]]]] = defaultdict(list)
        for r in recs:
            toks = bases[r["id"]].split()
            support[" ".join(toks)].append((r, []))  # isti base = razlika samo u mjeri
            for cut in (1, 2):
                if len(toks) > cut and vitola_tail(
                        toks[-cut:], brand in NUMBERED_VITOLA_BRANDS):
                    support[" ".join(toks[:-cut])].append((r, toks[-cut:]))
        taken: set[str] = set()
        for key in sorted(support, key=lambda k: (-len(k.split()), k)):
            if not key or key.split()[-1].lower() in DANGLING:
                continue
            members = [(r, tail) for r, tail in support[key] if r["id"] not in taken]
            if len({r["id"] for r, _ in members}) < 2:
                continue
            wraps = {r["wrapper"] for r, _ in members if r["wrapper"] != "—"}
            if len(wraps) > 1:   # razlicit pokrov = razlicita mjesavina, ne vitola
                continue
            for r, tail in members:
                keys[r["id"]] = key
                taken.add(r["id"])
        for r in recs:
            keys.setdefault(r["id"], bases[r["id"]])
    return keys


def one_pass(cigars: list[dict], merged_log: list[str], renamed_log: list[str],
             alias_add: dict[str, str]) -> list[dict]:
    """Jedan prolaz; vraca preostale zapise. Prazan alias_add prirast = fiksna tocka."""
    targets = [c for c in cigars if c.get("catalogSource") == "market"
               and (re.match(r"^[a-z0-9]", c["line"]) or parse_size(c["line"])[1]
                    or re.search(r"(?i)\bno\.?$", c["line"])
                    or (c["brand"] in NUMBERED_VITOLA_BRANDS
                        and NUMBERED_TAIL.search(c["line"])))]
    bases: dict[str, str] = {}
    sizes: dict[str, tuple[int, int] | None] = {}
    skus: dict[str, str] = {}
    for c in targets:
        stripped = strip_brand_tail(c["brand"], c["line"])
        base, size = parse_size(stripped)
        bases[c["id"]], sizes[c["id"]] = base.strip(), size
        # kod u kojem su duljina i prsten zaljepljeni JE ime vitole (Nub 460)
        m = re.search(r"\s([3-9]\d{2})$", stripped)
        if m and sku_size(m.group(1)):
            skus[c["id"]] = m.group(1)

    keys = group_key(targets, bases)
    for cid, key in keys.items():
        toks = key.split()
        while len(toks) > 1 and DANGLING_NO.match(toks[-1]):
            toks.pop()
        keys[cid] = " ".join(toks)
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    display: dict[tuple[str, str], str] = {}
    for c in targets:
        key = keys[c["id"]]
        gk = (c["brand"], key.lower())
        groups[gk].append(c)
        # ime linije: titlecase kad je kljuc sav mali, inace zadrzi postojece pisanje
        display.setdefault(gk, titlecase(key) if key == key.lower() else key)

    # market zapis koji vec ima to ime linije je ista linija iz drugog scrapea
    # (Crowned Heads "La Imperiosa" + "la imperiosa dukes") — ide u istu grupu
    target_ids = {c["id"] for c in targets}
    by_line = defaultdict(list)
    for c in cigars:
        if c.get("catalogSource") == "market" and c["id"] not in target_ids:
            by_line[(c["brand"], c["line"])].append(c)

    used_ids = {c["id"] for c in cigars}
    drop: set[str] = set()

    for (brand, key), members in sorted(groups.items()):
        line = display[(brand, key)]
        toks = line.split()
        while len(toks) > 1 and DANGLING_NO.match(toks[-1]):
            toks.pop()                   # goli "No." na kraju imena nije podatak
        if len(toks) == 1 and DANGLING_NO.match(toks[0]):
            codes = [v["name"] for m in members for v in m["vitolas"]
                     if sku_size(v["name"])]
            toks = [f"No. {codes[0]}"] if len(codes) == 1 else toks
        line = " ".join(toks)
        members = members + by_line.get((brand, line), [])
        orig = [(m["id"], m["line"]) for m in members]   # prije mutacije, za izvjestaj
        # vitola po clanu: rep imena kad postoji, inace vitola koju zapis nosi
        vitolas: list[dict] = []
        for m in members:
            if m["id"] not in bases:      # zapis iz drugog scrapea — vitole kakve su
                vitolas.extend(dict(v) for v in m["vitolas"])
                continue
            tail = bases[m["id"]].split()[len(key.split()):]
            name = titlecase(" ".join(tail)) if tail else m["vitola"]
            size = sizes[m["id"]]
            if size is None and len(tail) == 1 and sku_size(tail[0]):
                size, name = sku_size(tail[0]), tail[0]
            elif not tail and m["id"] in skus:
                name = skus[m["id"]]    # Nub 460 / Asylum 770: kod je ime vitole
            for v in m["vitolas"]:
                v = dict(v)
                if len(m["vitolas"]) == 1:
                    v["name"] = name
                    if size:
                        v["format"] = f"{size[0]} x {size[1]}mm"
                        v["ring"], v["lengthMM"] = size
                        v["smokeTimeMin"] = smoke(size[1])
                vitolas.append(v)
        seen: set[tuple[str, str | None]] = set()
        uniq = []
        for v in vitolas:
            sig = (v["name"], v.get("format"))
            if sig not in seen:
                seen.add(sig)
                uniq.append(v)
        uniq.sort(key=lambda v: (v.get("ring") or 999, v.get("lengthMM") or 9999, v["name"]))

        # prezivljava zapis s najvise podataka (HR link > cijena > prvi)
        base_id = "cig-" + slug(f"{brand} {line}")
        survivor = max(members, key=lambda m: (
            bool((m.get("regionLinks") or {}).get("HR")), m["wrapper"] != "—",
            m["id"] == base_id, m["priceEUR"] or 0, -len(m["id"])))
        new_id = survivor["id"]

        # Link na razini linije: prvi koji NOSI CIJENU (kartica prikazuje "od X €"),
        # inace link primarne vitole, inace bilo koji. Kandidat prve ruke je
        # primarna vitola — da linija ne nudi No. 3 a vodi na No. 1.
        prim_links = (uniq[0].get("regionLinks") or {}) if uniq else {}
        links: dict = {}
        for region in ("HR", "EU", "USA"):
            cands = [rl for rl in [prim_links.get(region)] if rl]
            cands += [rl for m in [survivor] + members
                      if (rl := (m.get("regionLinks") or {}).get(region))]
            if cands:
                links[region] = next((c for c in cands if c.get("priceEUR")), cands[0])
        markets = [mk for mk in ("HR", "EU", "USA", "WW")
                   if mk in {x for m in members for x in m["markets"]}]
        wrappers = [m["wrapper"] for m in members if m["wrapper"] != "—"]
        srcs = sorted({u for m in members for u in (m.get("sourceUrls") or [])})
        shops = sorted({s for m in members for s in m["availabilityHR"]})

        primary = uniq[0]
        old_id = survivor["id"]
        survivor.update({
            "id": new_id, "line": line, "vitola": primary["name"],
            "format": primary["format"] or survivor["format"],
            "smokeTimeMin": primary["smokeTimeMin"] or survivor["smokeTimeMin"],
            "vitolas": uniq, "markets": markets, "availabilityHR": shops,
        })
        if wrappers:
            survivor["wrapper"] = max(set(wrappers), key=wrappers.count)
        # link na razini linije mora voditi na PRIMARNU vitolu (inace kartica
        # nudi No. 3 a link vodi na No. 1), ali po regiji: gdje primarna vitola
        # nema link, ostaje spojeni iz clanova da linija ne izgubi HR pokrivenost
        if links:
            survivor["regionLinks"] = links
        if srcs:
            survivor["sourceUrls"] = srcs
        hr = survivor.get("regionLinks", {}).get("HR")
        if hr and hr.get("priceEUR"):
            survivor["priceEUR"] = hr["priceEUR"]

        for m in members:
            if m is survivor:
                continue
            drop.add(m["id"])
            alias_add[m["id"]] = new_id
        if old_id != new_id:
            alias_add[old_id] = new_id
            used_ids.add(new_id)
        if len(members) > 1:
            merged_log.append(
                f"- **{brand} — {line}** ({len(uniq)} vitola: "
                + ", ".join(f"{v['name']} {v.get('format') or '—'}" for v in uniq)
                + f")\n    - ostaje `{new_id}`\n"
                + "".join(f"    - `{ln}` ({i})\n" for i, ln in orig))
        elif orig[0][1] != line:
            renamed_log.append(f"- {brand}: `{orig[0][1]}` -> **{line}**"
                               + (f" (id `{old_id}` -> `{new_id}`)" if old_id != new_id else ""))

    return [c for c in cigars if c["id"] not in drop]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    before = len(cigars)
    merged_log: list[str] = []
    renamed_log: list[str] = []
    alias_add: dict[str, str] = {}
    for _ in range(5):
        seen = len(alias_add), len(renamed_log)
        cigars = one_pass(cigars, merged_log, renamed_log, alias_add)
        if (len(alias_add), len(renamed_log)) == seen:
            break
    kept = cigars

    print(f"{before} -> {len(kept)} cigara "
          f"({len(alias_add)} spojeno/preimenovano, {len(renamed_log)} imena linija)")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "# Popravak linija iz market scrapea\n\n"
        f"`repair-market-lines.py`: {before} -> {len(kept)} zapisa, "
        f"{len(alias_add)} ID-jeva dobilo alias.\n\n## Spojene linije\n\n"
        + "".join(merged_log)
        + "\n## Preimenovane linije (bez spajanja)\n\n"
        + "\n".join(renamed_log) + "\n", encoding="utf-8")
    print(f"izvjestaj: {REPORT.relative_to(APP)}")

    if args.dry_run:
        return 0

    CIGARS.write_text(json.dumps(kept, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    doc = json.loads(ALIASES.read_text(encoding="utf-8"))
    al = doc["aliases"]
    al.update(alias_add)
    live = {c["id"] for c in kept}
    for src in list(al):
        dst, hops = al[src], 0
        while dst not in live and dst in al and hops < 10:
            dst, hops = al[dst], hops + 1
        al[src] = dst
    doc["aliases"] = al  # poredak u datoteci je poredak dodavanja, ne abecedni
    ALIASES.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
