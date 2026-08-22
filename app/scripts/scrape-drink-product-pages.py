# -*- coding: utf-8 -*-
"""Fetch product-page text for drinks that already have priceUrl.

Writes scripts/output/drink_pdp_raw.json for merge-drink-profile-enrichment.py.
Also merges substantial extracts into drink_notes_raw.json (merge-drink-profiles scraped path).

  python scripts/scrape-drink-product-pages.py
  python scripts/scrape-drink-product-pages.py --limit 40 --resume
  python scripts/scrape-drink-product-pages.py --resume --files tequilas.json
"""
from __future__ import annotations

import argparse
import html as html_mod
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
OUT = HERE / "output" / "drink_pdp_raw.json"
NOTES_RAW = HERE / "output" / "drink_notes_raw.json"
LISTINGS = HERE / "output" / "drink_shop_listings_raw.json"
UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "hr-HR,hr;q=0.9,en;q=0.8",
}

ALLOW_HOSTS = (
    "allez.hr",
    "ecuga.com",
    "tipsy.hr",
    "cugaklik.hr",
    "miva.com.hr",
    "rotodinamic.hr",
    "vrutak.hr",
)

FILES = [
    "rums.json",
    "whiskies.json",
    "brandies.json",
    "gins.json",
    "tequilas.json",
    "wines.json",
    "digestifs.json",
]

JUNK = (
    "ova stranica namijenjena",
    "ecuga stranica",
    "sadržaj ne smije se dijeliti",
    "najčešćih grešaka",
    "sommeliera",
    "web trgovina s velikim asortimanom",
)

MIN_KEEP = 80


def host_ok(url: str) -> bool:
    try:
        h = urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")
    except Exception:
        return False
    return any(h.endswith(a) for a in ALLOW_HOSTS)


def is_katalog_url(url: str) -> bool:
    """Ecuga category shelves — HTML has no product tasting copy."""
    path = urllib.parse.urlparse(url).path.lower()
    return "/katalog/" in path and "/proizvod/" not in path


def is_product_url(url: str) -> bool:
    return bool(url) and host_ok(url) and not is_katalog_url(url)


def _name_tokens(name: str) -> set[str]:
    raw = re.findall(r"[a-z0-9]+", (name or "").lower())
    stop = {
        "the", "of", "and", "yo", "vol", "old", "years", "year", "single", "malt",
        "scotch", "whisky", "whiskey", "giftbox", "gift", "box", "poklon", "kutiji",
        "u", "in", "gb", "l", "cl", "ml", "rum", "gin", "tequila", "de", "la",
    }
    out: set[str] = set()
    for t in raw:
        if t in stop or len(t) < 2:
            continue
        if t.isdigit():
            # Keep ages (12, 15, 18…) — drop volumes / ABV-ish noise.
            n = int(t)
            if 3 <= n <= 60:
                out.add(t)
            continue
        out.add(t)
    return out


def load_listing_candidates() -> list[dict]:
    if not LISTINGS.exists():
        return []
    try:
        blob = json.loads(LISTINGS.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    items = blob.get("items") if isinstance(blob, dict) else blob
    out: list[dict] = []
    for row in items or []:
        url = (row.get("url") or "").strip()
        if not is_product_url(url):
            continue
        name = row.get("name") or ""
        out.append({"url": url, "name": name, "tokens": _name_tokens(name)})
    return out


def prefer_product_url(drink: dict, current: str, listings: list[dict]) -> str:
    """Replace Ecuga /katalog/ (and other non-PDP) links with a listing product URL."""
    if is_product_url(current):
        return current
    drink_toks = _name_tokens(drink.get("name") or "")
    if len(drink_toks) < 2 or not listings:
        return current
    drink_ages = {t for t in drink_toks if t.isdigit()}
    best_url = current
    best_score = 0.0
    for row in listings:
        inter = drink_toks & row["tokens"]
        if len(inter) < 2:
            continue
        row_ages = {t for t in row["tokens"] if t.isdigit()}
        # Never cross ages (Redbreast 15 ↛ Redbreast 12).
        if drink_ages and row_ages and drink_ages.isdisjoint(row_ages):
            continue
        if drink_ages and not (drink_ages & row_ages):
            # Listing has no age while drink does — allow, but do not prefer.
            age_bonus = 0.0
        elif drink_ages and drink_ages & row_ages:
            age_bonus = 0.35
        else:
            age_bonus = 0.0
        score = len(inter) / max(len(drink_toks), 1) + age_bonus
        try:
            cur_host = urllib.parse.urlparse(current).netloc.lower().removeprefix("www.")
            row_host = urllib.parse.urlparse(row["url"]).netloc.lower().removeprefix("www.")
        except Exception:
            cur_host = row_host = ""
        if cur_host and row_host and (
            row_host == cur_host or row_host.endswith(cur_host) or cur_host.endswith(row_host)
        ):
            score += 0.25
        if "/proizvod/" in row["url"]:
            score += 0.1
        if score > best_score:
            best_score = score
            best_url = row["url"]
    if best_score >= 0.5 and is_product_url(best_url):
        return best_url
    return current


def is_junk(text: str) -> bool:
    low = text.lower().strip()
    if len(low) < 20:
        return True
    return any(j in low for j in JUNK)


def is_chrome(text: str) -> bool:
    """Shop chrome (price, SKU, add-to-cart) without a tasting paragraph."""
    low = text.lower()
    if "dodaj u košaricu" not in low and "cijena za j.m" not in low:
        return False
    tasting = ("nota", "okus", "bačv", "destil", "agave", "agava", "hrast", "vanilij", "aroma")
    return not any(t in low for t in tasting)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as resp:
        return resp.read().decode("utf-8", "replace")


def _clean(text: str) -> str:
    text = html_mod.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _usable(text: str) -> bool:
    return bool(text) and len(text) > 40 and not is_junk(text) and not is_chrome(text)


def _editorjs_texts(html: str) -> list[str]:
    found: list[str] = []
    for m in re.finditer(r'"text"\s*:\s*"((?:\\.|[^"\\]){40,})"', html):
        raw = '"' + m.group(1) + '"'
        try:
            t = json.loads(raw)
        except json.JSONDecodeError:
            continue
        t = _clean(t)
        if _usable(t):
            found.append(t)
    for m in re.finditer(r'"description"\s*:\s*"((?:\\.|[^"\\]){20,})"', html):
        blob = '"' + m.group(1) + '"'
        try:
            inner = json.loads(blob)
        except json.JSONDecodeError:
            continue
        if isinstance(inner, str) and inner.lstrip().startswith("{"):
            try:
                parsed = json.loads(inner)
            except json.JSONDecodeError:
                t = _clean(inner)
                if _usable(t):
                    found.append(t)
                continue
            if isinstance(parsed, dict):
                for b in parsed.get("blocks") or []:
                    t = _clean(str((b.get("data") or {}).get("text") or ""))
                    if _usable(t):
                        found.append(t)
        elif isinstance(inner, str):
            t = _clean(inner)
            if _usable(t):
                found.append(t)
    return found


def _ldjson_texts(html: str) -> list[str]:
    found: list[str] = []
    for m in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.I | re.S,
    ):
        raw = m.group(1).strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else [data]
        stack = list(items)
        while stack:
            item = stack.pop()
            if isinstance(item, list):
                stack.extend(item)
                continue
            if not isinstance(item, dict):
                continue
            if "@graph" in item and isinstance(item["@graph"], list):
                stack.extend(item["@graph"])
            typ = item.get("@type")
            types = {typ} if isinstance(typ, str) else set(typ or [])
            if types & {"Product", "ProductGroup", "Offer"} or item.get("description"):
                t = _clean(str(item.get("description") or ""))
                if _usable(t):
                    found.append(t)
    return found


def extract_text(html: str) -> dict:
    # Pull structured blobs before stripping <script> tags.
    structured = _editorjs_texts(html) + _ldjson_texts(html)
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()
    chunks: list[str] = list(structured)
    for sel in [
        ".single-product-text",
        ".product__description",
        ".product-single__description",
        ".rte",
        ".woocommerce-product-details__short-description",
        "#tab-description",
        ".woocommerce-Tabs-panel--description",
        ".product-description",
        ".product-short-description",
        "[itemprop=description]",
        ".ee-product-description",
    ]:
        for el in soup.select(sel):
            t = _clean(el.get_text(" ", strip=True))
            if _usable(t):
                chunks.append(t)
    og = soup.find("meta", attrs={"property": "og:description"})
    if og and og.get("content"):
        t = _clean(og["content"])
        if _usable(t):
            chunks.append(t)
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        t = _clean(meta["content"])
        if _usable(t):
            chunks.append(t)
    uniq: list[str] = []
    seen: set[str] = set()
    for t in sorted(chunks, key=len, reverse=True):
        key = t[:60].lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(t)
    title = soup.find("h1")
    text = "\n".join(uniq)[:8000]
    return {
        "title": title.get_text(strip=True) if title else None,
        "text": text,
    }


def merge_notes_raw(pages: list[dict]) -> None:
    """Feed substantial PDP text into drink_notes_raw.json (dict keyed by id)."""
    existing: dict[str, dict] = {}
    if NOTES_RAW.exists():
        try:
            prev = json.loads(NOTES_RAW.read_text(encoding="utf-8"))
            if isinstance(prev, dict):
                existing = prev
        except json.JSONDecodeError:
            existing = {}
    n = 0
    for row in pages:
        did = row.get("id")
        if not did:
            continue
        text = (row.get("text") or "").strip()
        if len(text) < MIN_KEEP or is_chrome(text):
            existing.pop(did, None)
            continue
        existing[did] = {
            "id": did,
            "url": row.get("url"),
            "status": "ok",
            "text": text[:800],
            "raw_desc": text[:1200],
        }
        n += 1
    NOTES_RAW.parent.mkdir(parents=True, exist_ok=True)
    NOTES_RAW.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"drink_notes_raw: merged {n} PDP extracts -> {NOTES_RAW}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=0, help="Max pages (0 = all)")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--sleep", type=float, default=0.45)
    ap.add_argument(
        "--files",
        nargs="*",
        default=None,
        help="Limit to these catalog files (e.g. tequilas.json)",
    )
    ap.add_argument(
        "--min-text",
        type=int,
        default=200,
        help="Resume keeps a row only when text is at least this long",
    )
    args = ap.parse_args()

    file_list = args.files or FILES
    listings = load_listing_candidates()
    existing: dict[str, dict] = {}
    if args.resume and OUT.exists():
        prev = json.loads(OUT.read_text(encoding="utf-8"))
        for row in prev.get("pages") or []:
            if row.get("id"):
                existing[row["id"]] = row

    jobs = []
    skipped_katalog = 0
    for fname in file_list:
        path = DATA / fname
        if not path.exists():
            continue
        for d in json.loads(path.read_text(encoding="utf-8")):
            url = prefer_product_url(d, d.get("priceUrl") or "", listings)
            if not url or not host_ok(url):
                continue
            if is_katalog_url(url):
                skipped_katalog += 1
                continue
            prev_row = existing.get(d["id"]) if args.resume else None
            if prev_row and len(prev_row.get("text") or "") >= args.min_text:
                continue
            jobs.append({"id": d["id"], "name": d.get("name"), "url": url, "file": fname})

    if args.limit:
        jobs = jobs[: args.limit]

    # When scraping a subset, do not keep unrelated resume rows in the output.
    if args.files:
        keep_ids = {j["id"] for j in jobs}
        keep_ids |= {
            rid
            for rid, row in existing.items()
            if row.get("file") in file_list and len(row.get("text") or "") >= args.min_text
        }
        existing = {k: v for k, v in existing.items() if k in keep_ids}

    print(
        f"PDP jobs: {len(jobs)} (resume keep {len(existing)}; "
        f"listings={len(listings)}; skipped_katalog={skipped_katalog})"
    )
    by_id = dict(existing)
    ok = fail = 0
    for i, job in enumerate(jobs, 1):
        try:
            html = fetch(job["url"])
            extracted = extract_text(html)
            row = {**job, **extracted, "ok": True}
            ok += 1
        except Exception as e:
            row = {**job, "text": "", "title": None, "ok": False, "error": f"{type(e).__name__}: {e}"}
            fail += 1
        by_id[job["id"]] = row
        if i % 25 == 0 or i == len(jobs):
            OUT.parent.mkdir(parents=True, exist_ok=True)
            OUT.write_text(
                json.dumps({"pages": list(by_id.values()), "ok": ok, "fail": fail}, ensure_ascii=False, indent=2)
                + "\n",
                encoding="utf-8",
            )
            print(f"  {i}/{len(jobs)} ok={ok} fail={fail}", flush=True)
        time.sleep(args.sleep)

    pages = list(by_id.values())
    OUT.write_text(
        json.dumps({"pages": pages, "ok": ok, "fail": fail}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT}")
    merge_notes_raw(pages)


if __name__ == "__main__":
    main()
