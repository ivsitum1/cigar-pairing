#!/usr/bin/env python3
"""Build offer inventories for Famous + Neptune (HTTP) from catalog brands.

Writes:
  output/famous_smoke_catalog_raw.json
  output/neptune_catalog_raw.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from shop_common import slug

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
CIGARS = HERE.parent / "src" / "data" / "cigars.json"
OUT = HERE / "output"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

VITOLAS = (
    "robusto", "toro", "churchill", "corona", "gordo", "belicoso", "torpedo",
    "lancero", "perfecto", "lonsdale", "panetela", "presidente", "figurado",
    "piramide", "double corona", "petit corona", "grande", "gigante", "half corona",
)

SKIP_PATH = (
    "/samplers/", "/sampler", "/humidors/", "/accessories/", "/sale/",
    "/type/", "/country/", "/package/", "/gifts/", "/best-cigars/",
    "/brands/", "/brand/", "/brandgroup/", "/cigars?", "/search",
)


def _ssl_context():
    try:
        import certifi
        import ssl

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return None


def fetch(url: str) -> str | None:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60, context=_ssl_context()) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"  FAIL {url}: {e}")
        return None


def brand_slugs(brand: str) -> list[str]:
    s = slug(brand)
    alts = [s]
    # Padron special
    if "padron" in s or "padr" in s:
        alts += ["padron", "padron-cigars"]
    if s.endswith("-cigars"):
        alts.append(s[: -len("-cigars")])
    return list(dict.fromkeys(alts))


def parse_size(text: str) -> tuple[int | None, int | None]:
    m = re.search(
        r'(\d+)\s+(\d+)/(\d+)\s*["″]?\s*[x×*]\s*(\d{2,3})\b',
        text,
    )
    if m:
        inches = int(m.group(1)) + int(m.group(2)) / int(m.group(3))
        return int(m.group(4)), int(round(inches * 25.4))
    m = re.search(r'(\d+(?:\.\d+)?)\s*["″]?\s*[x×*]\s*(\d{2,3})\b', text)
    if m:
        return int(m.group(2)), int(round(float(m.group(1)) * 25.4))
    return None, None


def guess_country(text: str) -> str | None:
    low = (text or "").lower()
    if "nicaragua" in low:
        return "Nicaragua"
    if "dominican" in low:
        return "Dominican Republic"
    if "honduras" in low:
        return "Honduras"
    return None


def guess_vitola(text: str) -> str | None:
    low = f" {text.lower()} "
    for v in sorted(VITOLAS, key=len, reverse=True):
        if f" {v} " in low or low.strip().endswith(v):
            return v.title() if v != "double corona" else "Double Corona"
    return None


def line_from_product(brand: str, product_name: str, vitola: str | None) -> str:
    name = product_name
    name = re.sub(re.escape(brand), " ", name, flags=re.I)
    name = re.sub(r"\b cigars?\b", " ", name, flags=re.I)
    if vitola:
        name = re.sub(rf"\b{re.escape(vitola)}\b", " ", name, flags=re.I)
    name = re.sub(r"\d+\s*(?:/\d+)?\s*[\"″]?\s*[x×*]\s*\d+", " ", name)
    name = re.sub(r"\b(box|pack|bundle|sampler|single|tubo|tubos|5[- ]pack|10[- ]pack)\b", " ", name, flags=re.I)
    name = re.sub(r"\s+", " ", name).strip(" -–—/")
    return name or (vitola or "Classic")


def parse_neptune_brand(html: str, brand: str) -> list[dict]:
    offers = []
    # absolute + relative /cigars/ links
    hrefs = set(re.findall(r'href="(https://www\.neptunecigar\.com/cigars/[^"#?]+)"', html, re.I))
    hrefs |= {
        "https://www.neptunecigar.com" + p
        for p in re.findall(r'href="(/cigars/[^"#?]+)"', html, re.I)
    }
    # strip samplers
    hrefs = {u for u in hrefs if "sampler" not in u.lower()}
    # try to find title near each slug in page text (plain)
    plain = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    plain = re.sub(r"<style[\s\S]*?</style>", " ", plain, flags=re.I)
    plain = re.sub(r"<[^>]+>", "\n", plain)
    plain = re.sub(r"[ \t]+", " ", plain)
    for url in sorted(hrefs):
        slug_part = url.rstrip("/").split("/")[-1]
        # find a line mentioning slug tokens
        tokens = [t for t in slug_part.split("-") if t not in ("cigar", "cigars")]
        # build display guess from slug
        title = " ".join(t.title() for t in tokens)
        # search nearby size in plain text
        ring = length_mm = None
        vitola = guess_vitola(title.replace("-", " "))
        # look for size after title words
        for m in re.finditer(re.escape(tokens[-1] if tokens else ""), plain, re.I):
            window = plain[m.start() : m.start() + 120]
            ring, length_mm = parse_size(window)
            if ring:
                break
        if not vitola:
            vitola = guess_vitola(slug_part.replace("-", " "))
        line = line_from_product(brand, title, vitola)
        # country hint from text near this product, not the whole brand page
        country = guess_country(slug_part.replace("-", " "))
        if not country and tokens:
            search_key = tokens[-1]
            for m in re.finditer(re.escape(search_key), plain, re.I):
                country = guess_country(plain[m.start() : m.start() + 400])
                if country:
                    break
        offers.append(
            {
                "sourceShopId": "neptune_us",
                "brand": brand,
                "line": line,
                "vitola": vitola,
                "ring": ring,
                "lengthMM": length_mm,
                "amount": None,
                "currency": "USD",
                "url": url,
                "country": country,
                "wrapper": None,
                "inStock": True,
            }
        )
    return offers


def parse_famous_brand(html: str, brand: str) -> list[dict]:
    offers = []
    hrefs = set(re.findall(r'href="(https://www\.famous-smoke\.com/[^"#?]+)"', html, re.I))
    hrefs |= {
        "https://www.famous-smoke.com" + p
        for p in re.findall(r'href="(/[a-z0-9][a-z0-9\-]{6,})"', html, re.I)
    }
    prods = []
    for u in hrefs:
        low = u.lower()
        if any(s in low for s in SKIP_PATH):
            continue
        path = urllib.parse.urlparse(u).path.strip("/")
        if not path or "/" in path:
            continue
        if "cigar" not in path:
            continue
        # product-ish: many hyphens
        if path.count("-") < 3:
            continue
        prods.append(u)
    for url in sorted(set(prods)):
        path = urllib.parse.urlparse(url).path.strip("/")
        title = path.replace("-", " ")
        title = re.sub(r"\bcigars?\b", " ", title, flags=re.I)
        title = re.sub(r"\s+", " ", title).strip()
        vitola = guess_vitola(title)
        line = line_from_product(brand, title, vitola)
        ring, length_mm = parse_size(title)
        offers.append(
            {
                "sourceShopId": "famous_smoke_us",
                "brand": brand,
                "line": line,
                "vitola": vitola,
                "ring": ring,
                "lengthMM": length_mm,
                "amount": None,
                "currency": "USD",
                "url": url,
                "country": None,
                "wrapper": None,
                "inStock": True,
            }
        )
    return offers


def neptune_urls(brand: str) -> list[str]:
    out = []
    for s in brand_slugs(brand):
        out.append(f"https://www.neptunecigar.com/{s}-cigar")
        out.append(f"https://www.neptunecigar.com/{s}-cigars")
        out.append(f"https://www.neptunecigar.com/{s}")
    return list(dict.fromkeys(out))


def famous_urls(brand: str) -> list[str]:
    out = []
    for s in brand_slugs(brand):
        out.append(f"https://www.famous-smoke.com/brands/{s}-cigars")
        out.append(f"https://www.famous-smoke.com/brands/{s}")
        out.append(f"https://www.famous-smoke.com/brand-{s}")
    return list(dict.fromkeys(out))


def load_brands(limit: int | None) -> list[str]:
    data = json.loads(CIGARS.read_text(encoding="utf-8"))
    brands = sorted({c["brand"] for c in data}, key=lambda b: b.casefold())
    # skip obvious Cuban-only embargos for US shops later in merge
    if limit:
        brands = brands[:limit]
    return brands


def _checkpoint(shop: str, offers: list[dict]) -> None:
    """Write partial inventory so a mid-run crash does not lose progress."""
    name = (
        "famous_smoke_catalog_raw.json"
        if shop == "famous"
        else "neptune_catalog_raw.json"
    )
    shop_id = "famous_smoke_us" if shop == "famous" else "neptune_us"
    path = OUT / name
    path.write_text(
        json.dumps({"shop": shop_id, "offers": offers}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )


def scrape_shop(shop: str, brands: list[str], sleep: float) -> list[dict]:
    all_offers: list[dict] = []
    seen_url: set[str] = set()
    for i, brand in enumerate(brands, 1):
        urls = neptune_urls(brand) if shop == "neptune" else famous_urls(brand)
        got = False
        for url in urls:
            html = fetch(url)
            time.sleep(sleep)
            if not html or len(html) < 2000:
                continue
            # soft 404 detection
            if "page not found" in html.lower() or "404" in html[:500].lower() and "oliva" not in brand.lower():
                # still parse — some 200 soft pages
                pass
            offers = (
                parse_neptune_brand(html, brand)
                if shop == "neptune"
                else parse_famous_brand(html, brand)
            )
            if offers:
                for o in offers:
                    if o["url"] in seen_url:
                        continue
                    seen_url.add(o["url"])
                    all_offers.append(o)
                print(
                    f"[{shop}] {i}/{len(brands)} {brand}: +{len(offers)} "
                    f"(total {len(all_offers)}) via {url}",
                    flush=True,
                )
                got = True
                break
        if not got:
            print(f"[{shop}] {i}/{len(brands)} {brand}: no page", flush=True)
        if i % 25 == 0:
            _checkpoint(shop, all_offers)
    return all_offers


def enrich_from_sitemap_neptune(offers: list[dict]) -> list[dict]:
    """Add sitemap product URLs not already present; brand inferred from catalog brands."""
    xml = fetch("https://www.neptunecigar.com/sitemap.xml")
    if not xml:
        return offers
    locs = re.findall(r"<loc>(https://www\.neptunecigar\.com/cigars/[^<]+)</loc>", xml)
    brands = load_brands(None)
    brand_by_slug = {slug(b): b for b in brands}
    # also multi-word prefixes
    seen = {o["url"] for o in offers}
    added = 0
    for url in locs:
        if url in seen or "sampler" in url.lower():
            continue
        path = url.rstrip("/").split("/")[-1]
        # find longest matching brand slug prefix
        matched = None
        for bs, bname in sorted(brand_by_slug.items(), key=lambda x: -len(x[0])):
            if path.startswith(bs + "-") or path == bs:
                matched = bname
                break
        if not matched:
            continue
        title = path.replace("-", " ")
        vitola = guess_vitola(title)
        line = line_from_product(matched, title, vitola)
        offers.append(
            {
                "sourceShopId": "neptune_us",
                "brand": matched,
                "line": line,
                "vitola": vitola,
                "ring": None,
                "lengthMM": None,
                "amount": None,
                "currency": "USD",
                "url": url,
                "country": None,
                "wrapper": None,
                "inStock": True,
            }
        )
        seen.add(url)
        added += 1
    print(f"[neptune sitemap] +{added} matched to catalog brands")
    return offers


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shop", choices=["neptune", "famous", "both"], default="both")
    ap.add_argument("--limit", type=int, default=0, help="limit brands (0=all)")
    ap.add_argument("--sleep", type=float, default=0.35)
    ap.add_argument("--skip-sitemap", action="store_true")
    args = ap.parse_args()
    lim = args.limit or None
    brands = load_brands(lim)
    OUT.mkdir(parents=True, exist_ok=True)

    if args.shop in ("neptune", "both"):
        nep = scrape_shop("neptune", brands, args.sleep)
        if not args.skip_sitemap:
            nep = enrich_from_sitemap_neptune(nep)
        path = OUT / "neptune_catalog_raw.json"
        path.write_text(
            json.dumps({"shop": "neptune_us", "offers": nep}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {path} ({len(nep)} offers)")

    if args.shop in ("famous", "both"):
        fam = scrape_shop("famous", brands, args.sleep)
        path = OUT / "famous_smoke_catalog_raw.json"
        path.write_text(
            json.dumps({"shop": "famous_smoke_us", "offers": fam}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {path} ({len(fam)} offers)")


if __name__ == "__main__":
    main()
