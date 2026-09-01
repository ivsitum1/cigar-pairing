#!/usr/bin/env python3
"""Koliko katalog ima fotografija, gdje ih nema i odakle bi se dohvatile.

Racuna po istoj logici kao `src/lib/productImage.ts`: alias -> kanonski id,
obradjena slika ispred ducanske. Tri sloja se broje odvojeno jer su tri
razlicita posla:

  cigare (linija)   — sto vidi kartica linije
  cigare (vitola)   — `cig-x@vitola`; ducan ima zaseban SKU po velicini
  pica              — sve kategorije zajedno

Izvjestaj nabraja i ODAKLE se slika moze dohvatiti, jer to odlucuje redoslijed
posla: `priceUrl` je izravno preuzimanje, samo `shopHR` znaci da stranicu
proizvoda tek treba pronaci.

Pokreni iz app/:
    python3 scripts/report-image-gaps.py              # sazetak na ekran
    python3 scripts/report-image-gaps.py --json       # + output/image_gaps.json
    python3 scripts/report-image-gaps.py --check      # CI: pokrivenost ne smije pasti
    python3 scripts/report-image-gaps.py --update-baseline
"""
from __future__ import annotations

import argparse
import json
import sys
import unicodedata
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
OUT = HERE / "output"
BASELINE = HERE / "data" / "image_coverage_baseline.json"

DRINK_FILES = [
    "rums", "whiskies", "brandies", "gins",
    "wines", "tequilas", "digestifs", "coffees",
]
VITOLA_SEP = "@"


def ucitaj(ime: str):
    return json.loads((DATA / f"{ime}.json").read_text(encoding="utf-8"))


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r"['’`]", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


class Slike:
    """Isti izbor kao productImage.ts: obradjena ako postoji, inace ducanska."""

    def __init__(self) -> None:
        self.remote = ucitaj("productImages")
        self.local = ucitaj("productImagesLocal")
        self.alias = {
            "cigar": ucitaj("cigarIdAliases").get("aliases", {}),
            "drink": ucitaj("drinkIdAliases").get("aliases", {}),
        }

    def _kanon(self, vrsta: str, i: str) -> str:
        m = self.alias[vrsta]
        cur, seen = i, set()
        while m.get(cur) and cur not in seen:
            seen.add(cur)
            cur = m[cur]
        return cur

    def sloj(self, vrsta: str, i: str) -> str | None:
        """'local' | 'remote' | None — sto bi aplikacija stvarno prikazala."""
        kljuc = "cigars" if vrsta == "cigar" else "drinks"
        canon = self._kanon(vrsta, i)
        adrese = self.remote.get(kljuc, {})
        look = canon if adrese.get(canon) else (i if adrese.get(i) else canon)
        for k in (look, i):
            if self.local.get(kljuc, {}).get(k):
                return "local"
        u = adrese.get(look)
        return "remote" if isinstance(u, str) and u.startswith("http") else None


def izvor_pica(d: dict) -> str:
    url = d.get("priceUrl")
    if isinstance(url, str) and url.startswith("http"):
        return "priceUrl"
    return "shopHR" if d.get("shopHR") else "nema traga"


def prikupi() -> dict:
    s = Slike()
    cigars = ucitaj("cigars")
    cigars = cigars if isinstance(cigars, list) else cigars.get("cigars", [])

    slojevi: dict[str, Counter] = defaultdict(Counter)
    rupe: dict[str, list] = defaultdict(list)

    for c in cigars:
        sl = s.sloj("cigar", c["id"])
        slojevi["cigare-linija"][sl or "nema"] += 1
        if not sl:
            rupe["cigare-linija"].append(
                {"id": c["id"], "naziv": f"{c.get('brand','')} {c.get('line','')}".strip()}
            )
        for v in c.get("vitolas") or []:
            k = f"{c['id']}{VITOLA_SEP}{slug(v.get('name', ''))}"
            if k not in s.remote.get("cigars", {}):
                continue  # ducan nema zaseban SKU za tu velicinu — nije rupa
            sl = "local" if s.local.get("cigars", {}).get(k) else "remote"
            slojevi["cigare-vitola"][sl] += 1
            if sl == "remote":
                rupe["cigare-vitola"].append({"id": k, "naziv": v.get("name", "")})

    po_katalogu: dict[str, Counter] = defaultdict(Counter)
    for f in DRINK_FILES:
        d = ucitaj(f)
        for x in d if isinstance(d, list) else d.get("items", []):
            sl = s.sloj("drink", x["id"])
            slojevi["pica"][sl or "nema"] += 1
            po_katalogu[f][sl or "nema"] += 1
            if not sl:
                rupe["pica"].append(
                    {"id": x["id"], "naziv": x.get("name", ""), "katalog": f,
                     "izvor": izvor_pica(x), "ducan": x.get("shopHR") or ""}
                )
    return {"slojevi": slojevi, "rupe": rupe, "po_katalogu": po_katalogu}


def pokrivenost(c: Counter) -> int:
    """Udio zapisa koji uopce imaju sliku (obradjenu ili ducansku)."""
    n = sum(c.values())
    return 100 * (n - c["nema"]) // n if n else 100


def obradjenost(c: Counter) -> int:
    """Udio zapisa s OBRADJENOM slikom — ono sto kartica prikazuje ujednaceno."""
    n = sum(c.values())
    return 100 * c["local"] // n if n else 100


def ispisi(r: dict) -> None:
    print(f"{'sloj':18}{'zapisa':>8}{'obradjeno':>11}{'ducansko':>10}{'bez slike':>11}"
          f"{'pokriveno':>11}{'obradjeno':>11}")
    for ime, c in r["slojevi"].items():
        n = sum(c.values())
        print(f"{ime:18}{n:8}{c['local']:11}{c['remote']:10}{c['nema']:11}"
              f"{pokrivenost(c):10}%{obradjenost(c):10}%")
    print()
    print(f"{'katalog pica':13}{'zapisa':>8}{'sa slikom':>11}{'nedostaje':>11}")
    for f, c in sorted(r["po_katalogu"].items(), key=lambda kv: -kv[1]["nema"]):
        n = sum(c.values())
        print(f"{f:13}{n:8}{n - c['nema']:11}{c['nema']:11}")
    izvori = Counter(x["izvor"] for x in r["rupe"]["pica"])
    if izvori:
        print("\nodakle se rupa u picima moze dohvatiti:")
        for k, v in izvori.most_common():
            print(f"  {v:5}  {k}")
        ducani = Counter(x["ducan"] for x in r["rupe"]["pica"] if x["izvor"] == "shopHR")
        if ducani:
            print("  najcesci ducani:",
                  ", ".join(f"{d} {n}" for d, n in ducani.most_common(6)))


def mjere(r: dict) -> dict:
    return {
        ime: {"zapisa": sum(c.values()), "obradjeno": c["local"],
              "sa_slikom": sum(c.values()) - c["nema"]}
        for ime, c in r["slojevi"].items()
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true", help="zapisi output/image_gaps.json")
    p.add_argument("--check", action="store_true", help="CI: pokrivenost ne smije pasti")
    p.add_argument("--update-baseline", action="store_true")
    args = p.parse_args()

    r = prikupi()
    ispisi(r)
    sada = mjere(r)

    if args.json:
        OUT.mkdir(parents=True, exist_ok=True)
        put = OUT / "image_gaps.json"
        put.write_text(json.dumps(r["rupe"], ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nrupe zapisane: {put.relative_to(HERE.parent)}")

    if args.update_baseline:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(json.dumps(sada, ensure_ascii=False, indent=1) + "\n",
                            encoding="utf-8")
        print(f"\nbaseline osvjezen: {BASELINE.relative_to(HERE.parent)}")
        return 0

    if args.check:
        if not BASELINE.exists():
            print("\nbaseline ne postoji — pokreni --update-baseline", file=sys.stderr)
            return 2
        prije = json.loads(BASELINE.read_text(encoding="utf-8"))
        pao = []
        for ime, m in sada.items():
            staro = prije.get(ime)
            if not staro:
                continue
            for polje in ("sa_slikom", "obradjeno"):
                if m[polje] < staro[polje]:
                    pao.append(f"{ime}.{polje}: {staro[polje]} -> {m[polje]}")
        if pao:
            print("\nPOKRIVENOST JE PALA:", file=sys.stderr)
            for x in pao:
                print(f"  {x}", file=sys.stderr)
            print("Slike se smiju samo dodavati. Ako je uklanjanje namjerno, "
                  "osvjezi baseline s --update-baseline.", file=sys.stderr)
            return 1
        print("\ncheck: pokrivenost nije pala")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
