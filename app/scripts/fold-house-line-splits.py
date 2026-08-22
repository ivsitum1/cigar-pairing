#!/usr/bin/env python3
"""Fold shop-split house lines back under the parent brand.

Goes through audit section 6 in order. Skips cases that are two real marques
sharing a name (Cuban Fonseca / H. Upmann / Montecristo vs AJ Fernandez or
My Father collabs). Merges Neptune shape stubs into an existing parent-line
record; rehomes named wrapper/edition rows as `Parent / Marque Subline`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from taxonomy_lib import shape_words  # noqa: E402

DATA = HERE.parent / "src" / "data"
TAX = HERE / "data" / "taxonomy"
CIGARS = DATA / "cigars.json"
BRANDS = DATA / "brands.json"
ALIASES = DATA / "cigarIdAliases.json"
IMAGES = DATA / "productImages.json"

SHAPE = {s.lower() for s in shape_words()}
TODAY = "2026-08-18"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _vitola_key(name: str) -> str:
    return " ".join((name or "").lower().split())


def _merge_link(dst: dict, src: dict) -> None:
    for key in ("shop", "url", "priceEUR", "priceApprox", "fetchedAt", "inStock", "stockFetchedAt"):
        if src.get(key) is None:
            continue
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


def _prefer_hr_url(dst: dict, src: dict) -> None:
    src_url = src.get("priceUrl") or ""
    dst_url = dst.get("priceUrl") or ""
    if "humidor.hr" in src_url and "humidor.hr" not in dst_url:
        dst["priceUrl"] = src_url
        if src.get("priceEUR") is not None:
            dst["priceEUR"] = src["priceEUR"]
            dst["priceApprox"] = src.get("priceApprox", False)


def _merge_vitolas(dst: dict, src: dict) -> None:
    dst_vs = list(dst.get("vitolas") or [])
    have = {_vitola_key(v.get("name") or "") for v in dst_vs}
    for v in src.get("vitolas") or []:
        if not isinstance(v, dict):
            continue
        key = _vitola_key(v.get("name") or "")
        if not key:
            continue
        if key in have:
            for existing in dst_vs:
                if _vitola_key(existing.get("name") or "") == key:
                    if not existing.get("url") and v.get("url"):
                        existing["url"] = v["url"]
                    _merge_region_maps(existing, v)
                    _merge_link(existing, v)
                    break
            continue
        dst_vs.append(dict(v))
        have.add(key)
    dst["vitolas"] = dst_vs


def merge_into(survivor: dict, donor: dict) -> None:
    _stamp_availability(survivor, donor)
    _merge_region_maps(survivor, donor)
    _merge_vitolas(survivor, donor)
    _prefer_hr_url(survivor, donor)
    if donor.get("priceEUR") is not None and survivor.get("priceEUR") is None:
        survivor["priceEUR"] = donor["priceEUR"]
        survivor["priceApprox"] = donor.get("priceApprox", False)
    if donor.get("inStock") is not None and survivor.get("inStock") is None:
        survivor["inStock"] = donor["inStock"]
        survivor["stockFetchedAt"] = donor.get("stockFetchedAt")
    for leaf in ("wrapper", "binder", "filler", "wrapperOrigin", "binderOrigin", "fillerOrigin"):
        if donor.get(leaf) and not survivor.get(leaf):
            survivor[leaf] = donor[leaf]


def rehome(row: dict, *, brand: str, line: str) -> None:
    row["brand"] = brand
    row["line"] = line


def set_rename(tax_name: str, parent: str, line_map: dict[str, str]) -> None:
    path = TAX / tax_name
    data = _load(path)
    data["renameBrand"] = parent
    data["reviewedAt"] = TODAY
    lines = {src: {"line": dst} for src, dst in line_map.items()}
    data["lines"] = lines
    sources = list(data.get("sources") or [])
    note = f"house-line fold under {parent} {TODAY}"
    if note not in sources:
        sources.append(note)
    data["sources"] = sources
    _save(path, data)


def copy_image(images: dict, donor_id: str, survivor_id: str) -> None:
    cig = images.setdefault("cigars", {})
    donor = cig.get(donor_id)
    if not isinstance(donor, str):
        return
    existing = cig.get(survivor_id)
    if existing is None:
        cig[survivor_id] = donor
        return
    if "humidor.hr" in donor and "humidor.hr" not in existing:
        cig[survivor_id] = donor


def main() -> int:
    cigars = _load(CIGARS)
    by_id = {c["id"]: c for c in cigars}
    aliases = _load(ALIASES)
    amap = aliases.setdefault("aliases", {})
    images = _load(IMAGES)
    drop: set[str] = set()

    def absorb(survivor_id: str, donor_id: str) -> None:
        survivor = by_id[survivor_id]
        donor = by_id[donor_id]
        merge_into(survivor, donor)
        copy_image(images, donor_id, survivor_id)
        amap[donor_id] = survivor_id
        drop.add(donor_id)
        print(f"  merge {donor_id} -> {survivor_id}")

    print("1 Benchmade -> Ashton")
    for cid, line in (
        ("cig-benchmade-maduro", "Benchmade Maduro"),
        ("cig-benchmade-natural", "Benchmade Natural"),
        ("cig-benchmade-sun-grown", "Benchmade Sun Grown"),
    ):
        rehome(by_id[cid], brand="Ashton", line=line)
        print(f"  rehome {cid} -> Ashton / {line}")
    set_rename(
        "benchmade.json",
        "Ashton",
        {"Maduro": "Benchmade Maduro", "Natural": "Benchmade Natural", "Sun Grown": "Benchmade Sun Grown"},
    )

    print("2 Dominus MMXX -> Padilla (keep separate from regular Dominus)")
    for c in list(by_id.values()):
        if c.get("brand") != "Dominus":
            continue
        line = c.get("line") or "Dominus"
        new_line = line if line.lower().startswith("dominus") else f"Dominus {line}"
        rehome(c, brand="Padilla", line=new_line)
        print(f"  rehome {c['id']} -> Padilla / {new_line}")
    set_rename(
        "dominus.json",
        "Padilla",
        {spec: f"Dominus {spec}" for spec in (
            "MMXX Astkreuz",
            "MMXX Jerusalemkreuz",
            "MMXX Patoncerkreuz",
            "MMXX Santiagokreuz",
            "MMXX Tatzenkreuz",
            "MMXX Templerkreuz",
            "MMXX Wiederkreuz",
        )},
    )

    print("3 El Centurion -> My Father")
    absorb("cig-my-father-el-centurion", "cig-el-centurion-el-centurion")
    absorb("cig-my-father-el-centurion", "cig-el-centurion-h2kct")
    absorb("cig-my-father-el-centurion", "cig-el-centurion-h-2k-ct")
    set_rename(
        "el-centurion.json",
        "My Father",
        {"El Centurion": "El Centurion", "H-2K-CT": "El Centurion", "H2kct": "El Centurion"},
    )

    print("4 Fausto Avion 12 -> Tatuaje Fausto")
    absorb("cig-tatuaje-fausto", "cig-fausto-avion-12")
    set_rename("fausto.json", "Tatuaje", {"Avion 12": "Fausto"})

    print("5 Flor de las Antillas -> My Father")
    parent_fda = "cig-my-father-flor-de-las-antillas"
    for c in list(by_id.values()):
        if c.get("brand") != "Flor de las Antillas" or c["id"] in drop:
            continue
        line = (c.get("line") or "").strip()
        if line.lower() in SHAPE or line.lower() in {"de las antillas", "flor de las antillas"}:
            absorb(parent_fda, c["id"])
        else:
            new_line = line if line.lower().startswith("flor de las antillas") else f"Flor de las Antillas {line}"
            rehome(c, brand="My Father", line=new_line)
            print(f"  rehome {c['id']} -> My Father / {new_line}")
    set_rename(
        "flor-de-las-antillas.json",
        "My Father",
        {
            "10th Anniversary": "Flor de las Antillas 10th Anniversary",
            "Maduro": "Flor de las Antillas Maduro",
            "San Andres TAA": "Flor de las Antillas San Andres TAA",
            "de las Antillas": "Flor de las Antillas",
            "Robusto": "Flor de las Antillas",
            "Toro": "Flor de las Antillas",
            "Belicoso": "Flor de las Antillas",
        },
    )

    print("6 Fonseca — skip (Cuban Habanos vs My Father collab)")
    print("7 H. Upmann — skip (Cuban Habanos vs AJ Fernandez license)")

    print("8 La Antiguedad -> My Father")
    parent_ant = "cig-my-father-la-antiguedad"
    for c in list(by_id.values()):
        if c.get("brand") != "La Antiguedad" or c["id"] in drop:
            continue
        line = (c.get("line") or "").strip()
        if line.lower() in SHAPE or line.lower() in {"la antiguedad", "grande", "super"}:
            absorb(parent_ant, c["id"])
        else:
            new_line = line if line.lower().startswith("la antiguedad") else f"La Antiguedad {line}"
            rehome(c, brand="My Father", line=new_line)
            print(f"  rehome {c['id']} -> My Father / {new_line}")
    set_rename(
        "la-antiguedad.json",
        "My Father",
        {
            "La Antiguedad": "La Antiguedad",
            "Grande": "La Antiguedad",
            "Super": "La Antiguedad",
            "Robusto": "La Antiguedad",
            "Toro": "La Antiguedad",
        },
    )

    print("9 La Capitana -> Villiger")
    absorb("cig-villiger-la-capitana", "cig-la-capitana-la-capitana")
    set_rename("la-capitana.json", "Villiger", {"La Capitana": "La Capitana"})

    print("10 La Duena -> My Father")
    parent_duena = "cig-my-father-la-duena"
    absorb(parent_duena, "cig-la-duena-la-duena")
    absorb(parent_duena, "cig-la-duena-petit-no")
    absorb(parent_duena, "cig-la-duena-toro-no13")
    set_rename(
        "la-duena.json",
        "My Father",
        {"La Duena": "La Duena", "Petit No.": "La Duena", "Toro No13": "La Duena"},
    )

    print("11 La Instructora -> La Galera")
    for c in list(by_id.values()):
        if c.get("brand") != "La Instructora" or c["id"] in drop:
            continue
        line = (c.get("line") or "").strip()
        if line.lower() in SHAPE or line.lower() in {"la instructora"}:
            absorb("cig-la-galera-la-instructora", c["id"])
        else:
            new_line = (
                line
                if line.lower().startswith("la instructora")
                else f"La Instructora {line}"
            )
            rehome(c, brand="La Galera", line=new_line)
            print(f"  rehome {c['id']} -> La Galera / {new_line}")
    set_rename(
        "la-instructora.json",
        "La Galera",
        {
            "Delicado": "La Instructora Delicado",
            "Perfection": "La Instructora Perfection",
            "Perfection Extra": "La Instructora Perfection Extra",
            "Pressed": "La Instructora Pressed",
        },
    )

    print("12 La Ley -> Nicarao")
    absorb("cig-nicarao-la-ley", "cig-la-ley-la-ley")
    absorb("cig-nicarao-la-ley", "cig-la-ley-nicarao")
    set_rename("la-ley.json", "Nicarao", {"La Ley": "La Ley", "Nicarao": "La Ley"})

    print("13 La Libertad -> Villiger")
    absorb("cig-villiger-la-libertad", "cig-la-libertad-la-libertad")
    set_rename("la-libertad.json", "Villiger", {"La Libertad": "La Libertad"})

    print("14 Montecristo — skip (Cuban Habanos vs AJ Fernandez license)")
    print("15 Nicarao — skip (parent of La Ley)")

    cigars = [c for c in cigars if c["id"] not in drop]
    _save(CIGARS, cigars)
    _save(ALIASES, aliases)
    _save(IMAGES, images)

    brands = _load(BRANDS)
    used = {c["brand"] for c in cigars}
    orphans = (
        "Benchmade",
        "Dominus",
        "El Centurion",
        "Fausto",
        "Flor de las Antillas",
        "La Antiguedad",
        "La Capitana",
        "La Duena",
        "La Instructora",
        "La Ley",
        "La Libertad",
    )
    for orphan in orphans:
        if orphan not in used and orphan in brands:
            del brands[orphan]
            print(f"removed brands.json key {orphan!r}")
    _save(BRANDS, brands)

    print(f"done; catalog now {len(cigars)} cigars; dropped {len(drop)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
