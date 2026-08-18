#!/usr/bin/env python3
"""Copy shop photos from folded (alias) ids onto live canonical ids.

productImages.json keys must be live catalog ids (productImage.test.ts).
Alias sources that still hold a photo lose it unless we copy first.
Does not overwrite a photo the canonical id already has.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"

IMAGES = DATA / "productImages.json"
LOCAL = DATA / "productImagesLocal.json"
ALIASES = DATA / "cigarIdAliases.json"
DRINK_ALIASES = DATA / "drinkIdAliases.json"
CIGARS = DATA / "cigars.json"
DRINK_FILES = [
    DATA / "whiskies.json",
    DATA / "rums.json",
    DATA / "gins.json",
    DATA / "tequilas.json",
    DATA / "brandies.json",
    DATA / "wines.json",
    DATA / "coffees.json",
    DATA / "digestifs.json",
]


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _follow(aliases: dict[str, str], start: str) -> str:
    cur = start
    seen: set[str] = set()
    while cur in aliases and cur not in seen:
        seen.add(cur)
        cur = aliases[cur]
    return cur


def _copy_map(
    photos: dict[str, object],
    aliases: dict[str, str],
    live: set[str],
    kind: str,
) -> tuple[int, int, int]:
    copied = 0
    skipped_has = 0
    dropped = 0
    for src, dst in aliases.items():
        canon = _follow(aliases, dst)
        if src not in photos:
            continue
        if canon not in live:
            continue
        if canon not in photos:
            photos[canon] = photos[src]
            copied += 1
            print(f"  copy {kind} {src} -> {canon}")
        else:
            skipped_has += 1
    for key in list(photos):
        if key not in live:
            photos.pop(key)
            dropped += 1
            print(f"  drop orphan {kind} {key}")
    return copied, skipped_has, dropped


def main() -> int:
    images = _load(IMAGES)
    local = _load(LOCAL)
    cigar_aliases = (_load(ALIASES).get("aliases") or {})
    drink_aliases = (_load(DRINK_ALIASES).get("aliases") or {})
    live_cigars = {c["id"] for c in _load(CIGARS)}
    live_drinks: set[str] = set()
    for p in DRINK_FILES:
        if p.exists():
            live_drinks.update(d["id"] for d in _load(p) if isinstance(d, dict) and d.get("id"))

    print("=== productImages.json cigars ===")
    c_copy, c_skip, c_drop = _copy_map(images["cigars"], cigar_aliases, live_cigars, "cigar")
    print("=== productImages.json drinks ===")
    d_copy, d_skip, d_drop = _copy_map(images["drinks"], drink_aliases, live_drinks, "drink")

    print("=== productImagesLocal.json cigars ===")
    local.setdefault("cigars", {})
    lc_copy, lc_skip, lc_drop = _copy_map(local["cigars"], cigar_aliases, live_cigars, "local-cigar")
    print("=== productImagesLocal.json drinks ===")
    local.setdefault("drinks", {})
    ld_copy, ld_skip, ld_drop = _copy_map(local["drinks"], drink_aliases, live_drinks, "local-drink")

    missing = sorted(i for i in live_cigars if i not in images["cigars"])
    print(f"\nlive cigars without shop photo: {len(missing)}")
    for i in missing[:40]:
        print(f"  {i}")
    if len(missing) > 40:
        print(f"  ... +{len(missing) - 40}")

    _save(IMAGES, images)
    _save(LOCAL, local)
    print(
        f"\ncopied cigars={c_copy} drinks={d_copy} local_c={lc_copy} local_d={ld_copy}; "
        f"already-had cigar={c_skip} drink={d_skip}; dropped cigar={c_drop} drink={d_drop} "
        f"local_c={lc_drop} local_d={ld_drop}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
