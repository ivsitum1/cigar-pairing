#!/usr/bin/env python3
"""Moze li CigarWorldova ocjena zamijeniti snagu i tijelo? Mjerenje, ne dojam.

`cw_famous_flavor_raw.json` uz svaku cigaru nosi CigarWorldove ocjene zajednice
(1–10): `props.strength`, `props["smoke volume"]`, `props["aroma strength"]`, i
aroma-radar od dvanaest dimenzija. Prirodno je pomisliti da se iz njih mogu
popuniti cigare za koje Neptuneov opis o jacini ne kaze nista.

Ovaj audit to provjerava umjesto da pretpostavi: gdje za istu cigaru imamo i
CigarWorldovu ocjenu i Neptuneovo izreceno citanje, koliko se poredak slaze
(Kendall tau nad usporedivim parovima).

Zakljucak zapisan 2026-08: NE. Snaga tau ~0.17 (n=26), najbolji izvedeni
pokazatelj za tijelo tau ~0.39 (n=57) — preslabo da bi se broj upisao u
katalog kao da je mjeren. Aroma-radar se koristi ondje gdje mjeri ono sto
tvrdi da mjeri: okusne oznake (merge-cigarworld-aroma.py).

Pokreni iz app/:  python3 scripts/audit-cigarworld-axes.py
"""
import json
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"

HEAVY = ("pepper", "leather", "soil", "wood", "chocolate", "coffee")
LIGHT = ("cream", "grass", "fruit", "sweet", "nut", "toast")


def resolver():
    cigars = json.loads((DATA / "cigars.json").read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in cigars}
    aliases = json.loads((DATA / "cigarIdAliases.json").read_text(encoding="utf-8"))["aliases"]

    def resolve(cid: str):
        seen = set()
        while cid not in by_id:
            if cid in seen or cid not in aliases:
                return None
            seen.add(cid)
            cid = aliases[cid]
        return cid

    return resolve


def kendall(xs, ys) -> tuple[float, int]:
    """Tau-b: udio parova koji se slazu u poretku, minus onih koji se ne slazu."""
    con = dis = 0
    for (x1, y1), (x2, y2) in combinations(zip(xs, ys), 2):
        a, b = x1 - x2, y1 - y2
        if a == 0 or b == 0:
            continue
        con += a * b > 0
        dis += a * b < 0
    total = con + dis
    return ((con - dis) / total if total else float("nan"), total)


def main() -> int:
    resolve = resolver()
    cw = json.loads((HERE / "output" / "cw_famous_flavor_raw.json").read_text(encoding="utf-8"))
    nep = json.loads((HERE / "output" / "neptune_raw.json").read_text(encoding="utf-8"))

    shop: dict[str, dict] = {}
    for row in cw:
        block = row.get("cigarworld") or {}
        if block.get("props") or block.get("aroma"):
            cid = resolve(row["id"])
            if cid:
                shop[cid] = block
    stated: dict[str, dict] = {}
    for row in nep:
        cid = resolve(row["id"])
        if cid and (row.get("strength") or row.get("body")):
            stated[cid] = row

    print(f"CigarWorldovih ocjena spojenih na katalog: {len(shop)}")
    print(f"Neptuneovih izrecenih citanja: {len(stated)}\n")

    def probe(label, value_of, axis):
        xs, ys = [], []
        for cid, block in shop.items():
            v = value_of(block)
            target = stated.get(cid, {}).get(axis)
            if v and target:
                xs.append(v)
                ys.append(target)
        tau, pairs = kendall(xs, ys) if len(xs) > 2 else (float("nan"), 0)
        print(f"  {label:<34} vs {axis:<8} n={len(xs):3d}  tau={tau:+.3f}  ({pairs} parova)")

    def aroma_gap(block):
        a = block.get("aroma") or {}
        if not a:
            return None
        return sum(a.get(k, 0) for k in HEAVY) - sum(a.get(k, 0) for k in LIGHT)

    print("snaga:")
    probe("props.strength", lambda b: (b.get("props") or {}).get("strength"), "strength")
    probe("aroma tezak-lagan", aroma_gap, "strength")
    print("tijelo:")
    probe("props.smoke volume", lambda b: (b.get("props") or {}).get("smoke volume"), "body")
    probe("props.aroma strength", lambda b: (b.get("props") or {}).get("aroma strength"), "body")
    probe("aroma tezak-lagan", aroma_gap, "body")
    print("\nTau blizu 0 znaci da ocjena ne poznaje poredak koji opis tvrdi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
