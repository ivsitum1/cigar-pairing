#!/usr/bin/env python3
"""Stream D: fetch ring × length for vitolas with format '—'.

Reads scripts/output/stream-d-worklist.json (or rebuilds from cigars.json).
Writes scripts/data/dimension_fixes.json and scripts/output/stream-d-fetch-report.json.

Never invents dims: only product-page fields or explicit size tokens in /proizvod/ slug.
"""
from __future__ import annotations

import json
import re
import ssl
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
WORKLIST = APP / "scripts/output/stream-d-worklist.json"
CIGARS = APP / "src/data/cigars.json"
OUT = APP / "scripts/data/dimension_fixes.json"
REPORT = APP / "scripts/output/stream-d-fetch-report.json"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
CTX = ssl.create_default_context()

RING_DULJINA = re.compile(
    r"Ring\s*:\s*(\d{2,3})\s*Duljina\s*:\s*(\d+(?:[.,]\d+)?)\s*cm",
    re.I,
)
RING_ONLY = re.compile(r"\bRing\s*:\s*(\d{2,3})\b", re.I)
DULJINA_ONLY = re.compile(r"\bDuljina\s*:\s*(\d+(?:[.,]\d+)?)\s*cm\b", re.I)
LENGTH_IN = re.compile(
    r"Length\s*(?:</[^>]+>\s*)*(\d+(?:[./]\d+)?(?:\s*\d+/\d+)?)\s*inch",
    re.I,
)
RING_LABEL = re.compile(
    r"Ring(?:\s*Gauge)?\s*(?:</[^>]+>\s*)*(\d{2,3})\b",
    re.I,
)
# slug tails: ...-5-x-54 / ...-6-1-2-x-52 / ...-5-1-2-x-50
SLUG_DIM = re.compile(
    r"(?:^|-)(\d+)(?:-(\d+))?(?:-(\d+))?-[x×]-(\d{2,3})(?:-|$)",
    re.I,
)


def is_dash(fmt: str | None) -> bool:
    return not fmt or fmt.strip() in {"—", "-", "–", "?", "n/a", "N/A"}


def brand_range(b: str) -> str:
    ch = (b or "")[:1].upper()
    if "A" <= ch <= "F":
        return "AF"
    if "G" <= ch <= "M":
        return "GM"
    if "N" <= ch <= "Z":
        return "NZ"
    return "other"


def rebuild_worklist() -> list[dict]:
    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    rows = []
    for c in cigars:
        for v in c.get("vitolas") or []:
            if not is_dash(v.get("format")):
                continue
            url = v.get("url") or ""
            if not url:
                for rk in ("HR", "EU", "USA"):
                    rv = (v.get("regionLinks") or {}).get(rk)
                    if isinstance(rv, dict) and rv.get("url"):
                        url = rv["url"]
                        break
                    if isinstance(rv, str) and rv:
                        url = rv
                        break
            rows.append(
                {
                    "id": c["id"],
                    "brand": c["brand"],
                    "line": c["line"],
                    "name": v["name"],
                    "url": url,
                    "range": brand_range(c["brand"]),
                }
            )
    WORKLIST.parent.mkdir(parents=True, exist_ok=True)
    WORKLIST.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rows


def strip_noise(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html)


def parse_inches(token: str) -> float | None:
    token = token.strip().replace(",", ".")
    # 6 1/2 or 6.5 or 6
    m = re.match(r"^(\d+)\s+(\d+)/(\d+)$", token)
    if m:
        return int(m.group(1)) + int(m.group(2)) / int(m.group(3))
    m = re.match(r"^(\d+)/(\d+)$", token)
    if m:
        return int(m.group(1)) / int(m.group(2))
    m = re.match(r"^(\d+(?:\.\d+)?)$", token)
    if m:
        return float(m.group(1))
    return None


def dims_from_slug(url: str) -> tuple[int, int] | None:
    if not url or "/proizvod/" not in url:
        return None
    slug = url.rstrip("/").split("/")[-1]
    m = SLUG_DIM.search(slug)
    if not m:
        return None
    whole, num, den, ring_s = m.group(1), m.group(2), m.group(3), m.group(4)
    ring = int(ring_s)
    if not (30 <= ring <= 80):
        return None
    inches = float(whole)
    if num and den:
        inches += int(num) / int(den)
    elif num and not den:
        # ambiguous -5-2-x-54 style without clear fraction; skip
        return None
    lmm = round(inches * 25.4)
    if not (70 <= lmm <= 250):
        return None
    return ring, lmm


# Explicit "8 x 48" / "6 1/2 x 52" / "6 ½ x 52" in vitola display name.
NAME_DIM = re.compile(
    r"(?<!\d)(\d{1,2})\s*(?:([½¼¾])|(\d)\s*/\s*(\d))?\s*[x×]\s*(\d{2,3})(?!\d)",
    re.I,
)
FRAC_CHAR = {"½": 0.5, "¼": 0.25, "¾": 0.75}


def dims_from_name(name: str) -> tuple[int, int] | None:
    if not name:
        return None
    m = NAME_DIM.search(name.replace(",", "."))
    if not m:
        return None
    whole = int(m.group(1))
    ring = int(m.group(5))
    if not (30 <= ring <= 80):
        return None
    inches = float(whole)
    if m.group(2):
        inches += FRAC_CHAR.get(m.group(2), 0.0)
    elif m.group(3) and m.group(4):
        inches += int(m.group(3)) / int(m.group(4))
    # Heuristic: first number is length inches when < 12, else it may be ring-first (rare)
    if inches > 12:
        return None
    lmm = round(inches * 25.4)
    if not (70 <= lmm <= 250):
        return None
    return ring, lmm


def is_age_gate(html: str) -> bool:
    title_m = re.search(r"<title>([^<]+)", html, re.I)
    title = title_m.group(1) if title_m else ""
    if re.search(r"potvrdi\s+godine|confirm\s+age|age\s*gate|potvrda\s+dobi", title, re.I):
        return True
    if "agegate-btn" in html and "Ring:" not in html:
        return True
    return False


def dims_from_html(html: str, url: str) -> tuple[int, int, str] | None:
    text = strip_noise(html)
    m = RING_DULJINA.search(text)
    if m:
        ring = int(m.group(1))
        cm = float(m.group(2).replace(",", "."))
        lmm = round(cm * 10)
        if 30 <= ring <= 80 and 70 <= lmm <= 250:
            return ring, lmm, "page:ring+duljina_cm"
    # humidor-style English specs
    rm = RING_LABEL.search(html) or RING_ONLY.search(text)
    # Length N inch / N.N inch near specs
    lm = re.search(
        r"Length\s*</[^>]+>\s*</[^>]+>\s*(\d+(?:\s*\d+/\d+)?(?:\.\d+)?)\s*inch",
        html,
        re.I,
    )
    if not lm:
        lm = re.search(
            r"Length\s+(\d+(?:\s*\d+/\d+)?(?:\.\d+)?)\s*inch",
            text,
            re.I,
        )
    if rm and lm:
        ring = int(rm.group(1))
        inches = parse_inches(lm.group(1).replace(",", "."))
        if inches is None:
            return None
        lmm = round(inches * 25.4)
        if 30 <= ring <= 80 and 70 <= lmm <= 250:
            return ring, lmm, "page:ring+length_in"
    # duljina alone + ring alone
    r2 = RING_ONLY.search(text)
    d2 = DULJINA_ONLY.search(text)
    if r2 and d2:
        ring = int(r2.group(1))
        cm = float(d2.group(1).replace(",", "."))
        lmm = round(cm * 10)
        if 30 <= ring <= 80 and 70 <= lmm <= 250:
            return ring, lmm, "page:ring+duljina_cm"
    return None


def fetch(url: str) -> tuple[str | None, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "hr,en;q=0.8"})
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=25) as resp:
            return resp.read().decode("utf-8", errors="replace"), None
    except Exception as e:  # noqa: BLE001 — collect per-URL errors in report
        return None, f"{type(e).__name__}: {e}"


def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=25) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace")), None
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


def dims_from_wc_product(product: dict) -> tuple[int, int, str] | None:
    ring = None
    lmm = None
    for attr in product.get("attributes") or []:
        name = (attr.get("name") or "").strip().lower()
        terms = attr.get("terms") or []
        if not terms:
            continue
        val = (terms[0].get("name") or "").strip()
        if name == "ring":
            m = re.search(r"(\d{2,3})", val)
            if m:
                ring = int(m.group(1))
        elif name == "duljina":
            m = re.search(r"(\d+(?:[.,]\d+)?)\s*cm", val, re.I)
            if m:
                lmm = round(float(m.group(1).replace(",", ".")) * 10)
            else:
                m = re.search(r"(\d+(?:[.,]\d+)?)\s*mm", val, re.I)
                if m:
                    lmm = round(float(m.group(1).replace(",", ".")))
    if ring is None or lmm is None:
        blob = f"{product.get('short_description') or ''} {product.get('description') or ''}"
        blob = re.sub(r"<[^>]+>", " ", blob)
        m = RING_DULJINA.search(blob)
        if m:
            ring = int(m.group(1))
            lmm = round(float(m.group(2).replace(",", ".")) * 10)
    if ring is not None and lmm is not None and 30 <= ring <= 80 and 70 <= lmm <= 250:
        return ring, lmm, "wc-store-api:attributes"
    return None


def dims_from_havana_api(url: str) -> tuple[int, int, str] | None:
    if "havana-cigar-shop.com" not in url or "/proizvod/" not in url:
        return None
    slug = url.rstrip("/").split("/")[-1].split("?")[0]
    if not slug:
        return None
    api = f"https://havana-cigar-shop.com/wp-json/wc/store/v1/products?slug={slug}"
    data, err = fetch_json(api)
    if err or not data or not isinstance(data, list) or not data:
        return None
    return dims_from_wc_product(data[0])


def resolve_row(row: dict) -> dict:
    key = f"{row['id']}::{row['name']}"
    url = (row.get("url") or "").strip()
    out = {"key": key, **row, "status": "skip", "fix": None, "error": None}

    named = dims_from_name(row.get("name") or "")
    if named:
        ring, lmm = named
        out["status"] = "ok_name"
        out["fix"] = {
            "ring": ring,
            "lmm": lmm,
            "source": url or f"name:{row.get('name')}",
            "via": "name:explicit-dims",
        }
        return out

    if not url:
        out["status"] = "no_url"
        return out

    api_dims = dims_from_havana_api(url)
    if api_dims:
        ring, lmm, how = api_dims
        out["status"] = "ok_api"
        out["fix"] = {"ring": ring, "lmm": lmm, "source": url, "via": how}
        return out

    html, err = fetch(url)
    if html:
        if is_age_gate(html):
            out["error"] = "age_gate"
        else:
            parsed = dims_from_html(html, url)
            if parsed:
                ring, lmm, how = parsed
                out["status"] = "ok"
                out["fix"] = {"ring": ring, "lmm": lmm, "source": url, "via": how}
                return out

    slug = dims_from_slug(url)
    if slug:
        ring, lmm = slug
        out["status"] = "ok_slug"
        out["fix"] = {"ring": ring, "lmm": lmm, "source": url, "via": "slug:proizvod"}
        if err:
            out["error"] = err
        return out

    out["status"] = "unverified"
    if not out.get("error"):
        out["error"] = err or "no dims on api/page/slug/name"
    return out


def main() -> None:
    rows = rebuild_worklist()
    by_key: dict[str, dict] = {}
    for r in rows:
        by_key[f"{r['id']}::{r['name']}"] = r
    uniq = list(by_key.values())
    print(f"worklist {len(rows)} rows, {len(uniq)} unique keys, with_url={sum(1 for r in uniq if r.get('url'))}")

    results = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = {pool.submit(resolve_row, r): r for r in uniq}
        done = 0
        for fut in as_completed(futs):
            results.append(fut.result())
            done += 1
            if done % 25 == 0:
                ok = sum(
                    1
                    for x in results
                    if x["status"] in {"ok", "ok_slug", "ok_name", "ok_api"}
                )
                print(f"  … {done}/{len(uniq)} (ok-ish {ok})")
            time.sleep(0.05)

    fixes = {}
    for r in results:
        if r["status"] in {"ok", "ok_slug", "ok_name", "ok_api"} and r["fix"]:
            fx = r["fix"]
            fixes[r["key"]] = {
                "ring": fx["ring"],
                "lmm": fx["lmm"],
                "source": fx["source"],
                "via": fx["via"],
            }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(fixes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    counts = Counter(r["status"] for r in results)
    report = {
        "counts": dict(counts),
        "fixes": len(fixes),
        "unverified": [
            {"key": r["key"], "url": r.get("url"), "error": r.get("error")}
            for r in results
            if r["status"] in {"unverified", "no_url"}
        ],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"counts": dict(counts), "fixes": len(fixes)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
