#!/usr/bin/env python3
"""Fold shop-title splits of Karen Berger back under the parent brand.

K. Fire, Tailgate, and the AJ Fernandez 25th Anniversary collab were ingested
as separate brands/lines from Humidor titles ('K-Fire by Karen Berger',
'Tailgate by Karen Berger', 'K by Karen Berger 25th Anniversary by AJ Fernandez').
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
TAX = HERE / "data" / "taxonomy"

CIGARS = DATA / "cigars.json"
BRANDS = DATA / "brands.json"
ALIASES = DATA / "cigarIdAliases.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _index(cigars: list) -> dict[str, dict]:
    return {c["id"]: c for c in cigars}


def _merge_link(dst: dict, src: dict) -> None:
    """Copy shop/url/price/stock from src onto dst without dropping dst extras."""
    for key in ("shop", "url", "priceEUR", "priceApprox", "fetchedAt", "inStock", "stockFetchedAt"):
        if src.get(key) is not None and dst.get(key) is None:
            dst[key] = src[key]
        elif key in ("url", "shop") and src.get(key) and not dst.get(key):
            dst[key] = src[key]
        elif key in ("priceEUR", "inStock", "stockFetchedAt", "fetchedAt") and src.get(key) is not None:
            if dst.get(key) is None:
                dst[key] = src[key]


def _merge_region_maps(dst_obj: dict, src_obj: dict) -> None:
    dst_links = dict(dst_obj.get("regionLinks") or {})
    for region, link in (src_obj.get("regionLinks") or {}).items():
        if not isinstance(link, dict):
            continue
        if region not in dst_links:
            dst_links[region] = dict(link)
        else:
            _merge_link(dst_links[region], link)
    if dst_links:
        dst_obj["regionLinks"] = dst_links


def _stamp_availability(dst: dict, src: dict) -> None:
    shops = list(dst.get("availabilityHR") or [])
    for s in src.get("availabilityHR") or []:
        if s not in shops:
            shops.append(s)
    dst["availabilityHR"] = shops
    markets = list(dst.get("markets") or [])
    for m in src.get("markets") or []:
        if m not in markets:
            markets.append(m)
    order = ["HR", "EU", "USA", "WW"]
    dst["markets"] = [m for m in order if m in markets] + [m for m in markets if m not in order]


def _merge_vitola_links(dst: dict, src: dict) -> None:
    dst_v = (dst.get("vitolas") or [None])[0]
    src_v = (src.get("vitolas") or [None])[0]
    if not isinstance(dst_v, dict) or not isinstance(src_v, dict):
        return
    if not dst_v.get("url") and src_v.get("url"):
        dst_v["url"] = src_v["url"]
    if dst_v.get("priceEUR") is None and src_v.get("priceEUR") is not None:
        dst_v["priceEUR"] = src_v["priceEUR"]
        dst_v["fetchedAt"] = src_v.get("fetchedAt") or dst_v.get("fetchedAt")
    if src_v.get("inStock") is not None and dst_v.get("inStock") is None:
        dst_v["inStock"] = src_v["inStock"]
        dst_v["stockFetchedAt"] = src_v.get("stockFetchedAt")
    _merge_region_maps(dst_v, src_v)
    if src_v.get("smokeTimeMin") and (
        not dst_v.get("smokeTimeMin") or dst.get("formatEstimated")
    ):
        dst_v["smokeTimeMin"] = src_v["smokeTimeMin"]


def fold_into(survivor: dict, donor: dict, *, line: str, notes: dict, extra: dict) -> None:
    survivor["brand"] = "Karen Berger"
    survivor["line"] = line
    survivor["notes"] = notes
    for k, v in extra.items():
        survivor[k] = v
    if donor.get("priceEUR") is not None and (
        survivor.get("priceEUR") is None or survivor.get("priceApprox")
    ):
        survivor["priceEUR"] = donor["priceEUR"]
        survivor["priceApprox"] = donor.get("priceApprox", False)
        survivor["priceUrl"] = donor.get("priceUrl") or survivor.get("priceUrl")
    elif donor.get("priceUrl") and not survivor.get("priceUrl"):
        survivor["priceUrl"] = donor["priceUrl"]
    if donor.get("inStock") is not None and survivor.get("inStock") is None:
        survivor["inStock"] = donor["inStock"]
        survivor["stockFetchedAt"] = donor.get("stockFetchedAt")
    _stamp_availability(survivor, donor)
    _merge_region_maps(survivor, donor)
    _merge_vitola_links(survivor, donor)
    if extra.get("smokeTimeMin"):
        survivor["smokeTimeMin"] = extra["smokeTimeMin"]
        if survivor.get("vitolas"):
            survivor["vitolas"][0]["smokeTimeMin"] = extra["smokeTimeMin"]
    survivor.pop("formatEstimated", None)


def patch_taxonomy() -> None:
    kb = _load(TAX / "karen-berger.json")
    lines = dict(kb.get("lines") or {})
    lines.update(
        {
            "K-Fire": {"line": "K-Fire"},
            "K-Fire by Karen Berger": {"line": "K-Fire"},
            "Tailgate": {"line": "Tailgate"},
            "Berger Tailgate": {"line": "Tailgate"},
            "by Karen Berger": {"line": "Tailgate"},
            "25th Anniversary": {"line": "25th Anniversary"},
            "Berger 25th Anniversary": {"line": "25th Anniversary"},
            "K by Karen Berger": {"line": "25th Anniversary"},
        }
    )
    kb["lines"] = lines
    kb["reviewedAt"] = "2026-08-18"
    sources = list(kb.get("sources") or [])
    note = "fold shop-title splits (K. Fire / Tailgate / 25th) 2026-08-18"
    if note not in sources:
        sources.append(note)
    kb["sources"] = sources
    _save(TAX / "karen-berger.json", kb)

    fire = _load(TAX / "k-fire.json")
    fire["renameBrand"] = "Karen Berger"
    fire["lines"] = {"K-Fire by Karen Berger": {"line": "K-Fire"}}
    fire["reviewedAt"] = "2026-08-18"
    _save(TAX / "k-fire.json", fire)

    tg = _load(TAX / "tailgate.json")
    tg["renameBrand"] = "Karen Berger"
    tg["lines"] = {"by Karen Berger": {"line": "Tailgate"}}
    tg["reviewedAt"] = "2026-08-18"
    _save(TAX / "tailgate.json", tg)


def main() -> int:
    cigars = _load(CIGARS)
    by_id = _index(cigars)

    kfire = by_id["cig-k-fire-k-fire-by-karen-berger"]
    kfire["brand"] = "Karen Berger"
    kfire["line"] = "K-Fire"
    kfire["binder"] = "Ecuador Havana"
    kfire["filler"] = "Nikaragva"
    kfire["wrapperOrigin"] = "Meksiko"
    kfire["binderOrigin"] = "Ekvador"
    kfire["fillerOrigin"] = "Nikaragva"
    kfire["notes"] = {
        "hr": "K-Fire je punija linija Karen Berger: tamni meksički San Andrés maduro pokriva ekvadorski havanski binder i nikaragvansko punjenje. Začinjeno-slatka, s notama začina, zemlje i kave.",
        "en": "K-Fire is Karen Berger's fuller line: a dark Mexican San Andrés maduro wrapper over an Ecuadorian Havana binder and Nicaraguan filler. Spicy-sweet, with spice, earth, and coffee.",
    }

    tail_surv = by_id["cig-karen-berger-tailgate"]
    tail_donor = by_id["cig-tailgate-by-karen-berger"]
    fold_into(
        tail_surv,
        tail_donor,
        line="Tailgate",
        notes={
            "hr": "Tailgate je srednjeg tijela, blend indonezijskih i nikaragvanskih duhana. Kremast dim sa svijetlim notama crnog papra, zobi, orašastih plodova i slatkoće.",
            "en": "Tailgate is a medium-bodied blend of Indonesian and Nicaraguan tobaccos. Creamy smoke with bright notes of black pepper, oat, nuts, and sweetness.",
        },
        extra={
            "wrapper": "Indonesia, Sumatra",
            "binder": "Nikaragva",
            "filler": "Nikaragva",
            "wrapperOrigin": "Indonezija",
            "binderOrigin": "Nikaragva",
            "fillerOrigin": "Nikaragva",
            "smokeTimeMin": 75,
            "strength": 3,
            "body": 4,
        },
    )

    ann_surv = by_id["cig-karen-berger-25th-anniversary"]
    ann_donor = by_id["cig-aj-fernandez-k-by-karen-berger"]
    fold_into(
        ann_surv,
        ann_donor,
        line="25th Anniversary",
        notes={
            "hr": "Za 25 godina u industriji Karen Berger se udružila s AJ Fernandezom. Connecticut Habano Broadleaf pokrov, meksički San Andrés binder i nikaragvansko punjenje — srednje do pune snage, kremasto s pikantnošću, kavom i slatkoćom.",
            "en": "For 25 years in the trade Karen Berger joined AJ Fernandez. Connecticut Habano Broadleaf wrapper, Mexican San Andrés binder and Nicaraguan filler — medium to full, creamy with spice, coffee, and sweetness.",
        },
        extra={
            "wrapper": "Connecticut Habano Broadleaf",
            "binder": "Mexican San Andres",
            "filler": "Nikaragva",
            "wrapperOrigin": "SAD",
            "binderOrigin": "Meksiko",
            "fillerOrigin": "Nikaragva",
            "smokeTimeMin": 75,
            "strength": 4,
            "body": 4,
        },
    )

    drop = {"cig-tailgate-by-karen-berger", "cig-aj-fernandez-k-by-karen-berger"}
    cigars = [c for c in cigars if c["id"] not in drop]
    _save(CIGARS, cigars)

    aliases = _load(ALIASES)
    amap = aliases.setdefault("aliases", {})
    amap["cig-tailgate-by-karen-berger"] = "cig-karen-berger-tailgate"
    amap["cig-aj-fernandez-k-by-karen-berger"] = "cig-karen-berger-25th-anniversary"
    amap["cig-aj-fernandez-k-by-karen-berger-25th-anniversary"] = "cig-karen-berger-25th-anniversary"
    amap["cig-aj-fernandez-k-by-karen-berger-25th-anniversary-by-aj-fernandez-toro-6-x-52"] = (
        "cig-karen-berger-25th-anniversary"
    )
    _save(ALIASES, aliases)

    brands = _load(BRANDS)
    used = {c["brand"] for c in cigars}
    for orphan in ("K. Fire", "Tailgate"):
        if orphan not in used and orphan in brands:
            del brands[orphan]
            print(f"removed brands.json key {orphan!r}")
    _save(BRANDS, brands)

    patch_taxonomy()
    print(
        "folded K-Fire / Tailgate / 25th Anniversary under Karen Berger; "
        f"catalog now {len(cigars)} cigars"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
