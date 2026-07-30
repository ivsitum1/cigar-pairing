# -*- coding: utf-8 -*-
"""Dohvat CigarWorld (sitemap proizvoda) i Holt's (sitemap brandova) za EU/USA reconcile.

Pokretanje (iz app/):
  python scripts/fetch-eu-usa-catalogs.py

Izlaz: scripts/output/eu_usa_catalog_snapshot.json
"""
from __future__ import annotations

import json
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
SNAPSHOT = OUT / "eu_usa_catalog_snapshot.json"

UA = "Mozilla/5.0 (compatible; CigarRumEuUsaSync/1.0)"
CW_SITEMAP_INDEX = "https://www.cigarworld.de/sitemap.xml"
HOLTS_SITEMAP = "https://www.holts.com/sitemap.xml"


def _http_get(url: str, timeout: float = 60.0, retries: int = 3) -> str:
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": UA, "Accept": "application/xml,text/xml,*/*"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            last = e
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
    raise last or RuntimeError(f"GET failed: {url}")


def _locs(xml: str) -> list[str]:
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml, flags=re.I)


def slug_to_name(slug: str) -> str:
    """arturo-fuente-don-carlos-robusto-90000961_180 → Arturo Fuente Don Carlos Robusto."""
    s = slug.strip().lower()
    s = re.sub(r"-\d+_\d+$", "", s)
    s = re.sub(r"-\d+$", "", s)
    s = re.sub(r"_\d+$", "", s)
    return " ".join(p for p in s.split("-") if p).title()


def parse_cw_product_url(url: str) -> dict | None:
    """https://www.cigarworld.de/en/zigarren/<country>/<slug> → {name, url, slug}."""
    m = re.search(
        r"cigarworld\.de/en/zigarren/[^/]+/([^/?#]+)/?$",
        url,
        flags=re.I,
    )
    if not m:
        return None
    slug = m.group(1)
    if not slug or slug in ("index", "filter"):
        return None
    return {"source": "cigarworld", "name": slug_to_name(slug), "url": url, "slug": slug}


def fetch_cigarworld_catalog() -> list[dict]:
    """Puni EN zigarren URL-ove iz sitemap_en.xml (~10k+)."""
    idx = _http_get(CW_SITEMAP_INDEX)
    en_map = next((u for u in _locs(idx) if u.rstrip("/").endswith("sitemap_en.xml")), None)
    if not en_map:
        raise RuntimeError("CigarWorld sitemap index nema sitemap_en.xml")
    time.sleep(0.4)
    xml = _http_get(en_map, timeout=120.0)
    items: list[dict] = []
    seen: set[str] = set()
    for loc in _locs(xml):
        row = parse_cw_product_url(loc)
        if not row or row["url"] in seen:
            continue
        seen.add(row["url"])
        items.append(row)
    return items


def parse_holts_brand_url(url: str) -> dict | None:
    """Brand listing / brand hub → {brand, url}."""
    u = url.strip()
    m = re.search(r"holts\.com/cigars/all-cigar-brands/brand/([^/?#]+)/?$", u, re.I)
    if m:
        slug = m.group(1)
        return {
            "source": "holts",
            "brand": slug_to_name(slug),
            "url": u,
            "slug": slug,
            "level": "brand",
        }
    m = re.search(r"holts\.com/cigars/all-cigar-brands/([^/?#]+)\.html$", u, re.I)
    if m:
        slug = m.group(1)
        if slug in ("brand", "index"):
            return None
        return {
            "source": "holts",
            "brand": slug_to_name(slug),
            "url": u,
            "slug": slug,
            "level": "line_or_brand",
        }
    m = re.search(r"holts\.com/cigars/([^/?#]+)/?$", u, re.I)
    if m:
        slug = m.group(1)
        if slug.endswith(".html"):
            slug = slug[:-5]
        if slug in (
            "all-cigar-brands",
            "new-arrivals",
            "bundle-heaven",
            "flavored-cigars",
            "machine-made-cigars",
            "html",
        ):
            return None
        return {
            "source": "holts",
            "brand": slug_to_name(slug),
            "url": u,
            "slug": slug,
            "level": "brand_hub",
        }
    return None


def fetch_holts_brands() -> list[dict]:
    """Holt's sitemap nema SKU — samo brand/line listing stranice."""
    xml = _http_get(HOLTS_SITEMAP, timeout=90.0)
    items: list[dict] = []
    seen: set[str] = set()
    for loc in _locs(xml):
        row = parse_holts_brand_url(loc)
        if not row or row["url"] in seen:
            continue
        seen.add(row["url"])
        items.append(row)
    return items


def write_snapshot(cigarworld: list[dict], holts: list[dict]) -> dict:
    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "cigarworld": cigarworld,
        "holts": holts,
        "counts": {"cigarworld": len(cigarworld), "holts": len(holts)},
        "note": (
            "CigarWorld = product URLs from sitemap_en. "
            "Holt's = brand/line listing URLs only (no SKU sitemap)."
        ),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    print("Dohvat CigarWorld sitemap_en…", flush=True)
    cw = fetch_cigarworld_catalog()
    print(f"  CigarWorld proizvoda: {len(cw)}", flush=True)
    print("Dohvat Holt's sitemap (brandovi)…", flush=True)
    holts = fetch_holts_brands()
    print(f"  Holt's brand/line URL-ova: {len(holts)}", flush=True)
    snap = write_snapshot(cw, holts)
    print(f"Snapshot: {SNAPSHOT} at {snap['fetched_at']}", flush=True)


if __name__ == "__main__":
    main()
