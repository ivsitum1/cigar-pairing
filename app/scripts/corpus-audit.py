# -*- coding: utf-8 -*-
"""P4 corpus audit — sweep cigars.json + brands.json for P1–P3 problem classes.

Outputs (app/scripts/output/):
  brand_dupe_candidates.json
  markets_audit_report.json
  blurb_translation_review.json
  corpus_audit_findings.md

Auto-fixes (idempotent):
  - HTML entities in line/vitola/notes (&amp; &quot; …)
  - country label normalization (Dominikana→Dominikanska Republika, etc.)
  - HR/EN note leaks via describe-lines.py (if available) for wrapper/Note:

Pokretanje (iz app/):
  python scripts/corpus-audit.py [--fix]
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT.parent
DATA = APP / "src" / "data"
OUT = ROOT / "output"
CIGARS = DATA / "cigars.json"
BRANDS = DATA / "brands.json"

COUNTRY_CANON = {
    "Dominikana": "Dominikanska Republika",
    "Dominican Republic": "Dominikanska Republika",
    "Nicaragua": "Nikaragva",
    "Honduras": "Honduras",
    "Cuba": "Kuba",
    "Mexico": "Meksiko",
    "USA": "SAD",
    "United States": "SAD",
}

HR_EN_LEAK = re.compile(
    r"\bwrapper\b|Note:|Notes of|\bmild\b|\bmedium\b|full-bodied|\bspice\b|\bleather\b|\bsmooth\b",
    re.I,
)
EN_HR_LEAK = re.compile(
    r"pokrov|snage|tijela|Okusi|zacini|koza|orasasti|cedrovina|kremasto|začini|koža|"
    r"Nikaragva|Meksiko|\bKuba\b",
)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def decode_entities(s: str) -> str:
    if not s or "&" not in s:
        return s
    prev = None
    cur = s
    while prev != cur:
        prev = cur
        cur = html.unescape(cur)
    return re.sub(r" {2,}", " ", cur)


def brand_dupe_candidates(brands: dict, cigars: list) -> list[dict]:
    by_norm: dict[str, list[str]] = defaultdict(list)
    for name in brands:
        by_norm[norm(name)].append(name)
    # also group near-duplicates by shared significant tokens
    habanos_hint = re.compile(r"\b(habanos|cuban|kuba|cuba|non.?cuban|\(nw\))\b", re.I)
    cands = []
    for key, names in sorted(by_norm.items()):
        if len(names) > 1:
            cands.append({"type": "exact-norm", "key": key, "brands": names})
    # similar roots: strip leading La/El/The
    roots: dict[str, list[str]] = defaultdict(list)
    for name in brands:
        r = re.sub(r"^(la|el|the|los|las)\s+", "", norm(name))
        roots[r].append(name)
    for key, names in sorted(roots.items()):
        uniq = sorted(set(names))
        if len(uniq) > 1 and not any(c["brands"] == uniq for c in cands):
            cands.append({"type": "shared-root", "key": key, "brands": uniq})
    # non-cuban namesakes mentioned in blurbs
    for name, meta in brands.items():
        blurb = " ".join(
            [
                (meta.get("blurb") or {}).get("hr") or "",
                (meta.get("blurb") or {}).get("en") or "",
            ]
        )
        if habanos_hint.search(blurb) and meta.get("country") not in ("Kuba", "Cuba"):
            cands.append({
                "type": "non-cuban-habanos-hint",
                "brand": name,
                "country": meta.get("country"),
                "blurb_snip": blurb[:160],
            })
    return cands


def markets_audit(cigars: list) -> dict:
    hosts = {
        "HR": ("humidor.hr", "havana-cigar-shop.com"),
        "EU": ("cigarworld.de", "cigarworld.com"),
        "USA": ("holts.com", "famous-smoke.com", "cigarsdaily.com", "neptunecigar.com"),
    }

    def has_url_proof(c: dict, region: str) -> bool:
        rl = (c.get("regionLinks") or {}).get(region)
        if isinstance(rl, dict) and rl.get("url"):
            return True
        urls = [c.get("priceUrl")] + [v.get("url") for v in (c.get("vitolas") or [])]
        hs = hosts.get(region, ())
        for u in urls:
            if u and any(h in u.lower() for h in hs):
                return True
        if region == "HR" and c.get("availabilityHR"):
            return True
        return False

    without: dict[str, list] = {r: [] for r in ("HR", "EU", "USA")}
    missing_market: dict[str, list] = {r: [] for r in ("HR", "EU", "USA")}
    for c in cigars:
        markets = c.get("markets") or []
        for region in ("HR", "EU", "USA"):
            if region in markets and not has_url_proof(c, region):
                if c.get("catalogSource") == "market" and region != "HR":
                    # market EU/USA usually from scrapes; still report if no link
                    without[region].append({
                        "id": c["id"], "brand": c["brand"], "line": c["line"],
                        "catalogSource": c.get("catalogSource"),
                    })
                else:
                    without[region].append({
                        "id": c["id"], "brand": c["brand"], "line": c["line"],
                        "catalogSource": c.get("catalogSource"),
                    })
            rl = (c.get("regionLinks") or {}).get(region)
            if isinstance(rl, dict) and rl.get("url") and region not in markets:
                missing_market[region].append({
                    "id": c["id"], "brand": c["brand"], "line": c["line"],
                    "url": rl.get("url"),
                })
    return {
        "without_source": {k: {"count": len(v), "items": v} for k, v in without.items()},
        "has_link_missing_market": {
            k: {"count": len(v), "items": v} for k, v in missing_market.items()
        },
    }


def blurb_review(brands: dict) -> list[dict]:
    out = []
    for name, meta in brands.items():
        bl = meta.get("blurb") or {}
        hr = (bl.get("hr") or "").strip()
        en = (bl.get("en") or "").strip()
        if not hr or not en:
            continue
        flags = []
        if re.search(r"\bwrapper\b|Note:|great basic|veliki osnovni|machine-made", hr, re.I):
            flags.append("en-leak-or-kalk")
        # token overlap heuristic
        en_toks = set(re.findall(r"[A-Za-z]{4,}", en.lower()))
        hr_latin = set(re.findall(r"[A-Za-z]{4,}", hr.lower()))
        shared = en_toks & hr_latin
        if len(shared) >= 8 and len(en_toks) > 0 and len(shared) / max(len(en_toks), 1) > 0.55:
            flags.append("high-en-token-overlap")
        if hr == en:
            flags.append("hr-eq-en")
        if flags:
            out.append({"brand": name, "flags": flags, "hr": hr, "en": en})
    return out


def note_leak_counts(cigars: list) -> dict:
    hr_leak = []
    en_leak = []
    empty = []
    identical = []
    filler = []
    for c in cigars:
        notes = c.get("notes") or {}
        hr = (notes.get("hr") or "").strip()
        en = (notes.get("en") or "").strip()
        if not hr:
            empty.append({"id": c["id"], "field": "hr"})
        if not en:
            empty.append({"id": c["id"], "field": "en"})
        if hr and HR_EN_LEAK.search(hr):
            hr_leak.append({"id": c["id"], "hr": hr[:120]})
        if en and EN_HR_LEAK.search(en):
            en_leak.append({"id": c["id"], "en": en[:120]})
        if hr and en and hr == en:
            identical.append(c["id"])
        if re.match(r"^(Sinkronizirano iz HR trgovina|Dostupno u HR)", hr):
            filler.append(c["id"])
    return {
        "hr_en_leak": {"count": len(hr_leak), "items": hr_leak[:200]},
        "en_hr_leak": {"count": len(en_leak), "items": en_leak[:200]},
        "empty": {"count": len(empty), "items": empty[:100]},
        "hr_eq_en": {"count": len(identical), "sample": identical[:50]},
        "filler_hr": {"count": len(filler), "sample": filler[:50]},
    }


def fix_entities_and_countries(cigars: list) -> dict:
    stats = {"entities": 0, "countries": 0, "fields": []}
    fields = ("line", "vitola", "wrapper", "format", "brand")
    for c in cigars:
        for f in fields:
            v = c.get(f)
            if isinstance(v, str):
                nv = decode_entities(v)
                if nv != v:
                    c[f] = nv
                    stats["entities"] += 1
                    stats["fields"].append(f"{c['id']}.{f}")
        notes = c.get("notes")
        if isinstance(notes, dict):
            for lang in ("hr", "en"):
                v = notes.get(lang)
                if isinstance(v, str):
                    nv = decode_entities(v)
                    if nv != v:
                        notes[lang] = nv
                        stats["entities"] += 1
        country = c.get("country")
        if isinstance(country, str) and country in COUNTRY_CANON:
            c["country"] = COUNTRY_CANON[country]
            stats["countries"] += 1
        for v in c.get("vitolas") or []:
            for f in ("name", "format"):
                val = v.get(f)
                if isinstance(val, str):
                    nv = decode_entities(val)
                    if nv != val:
                        v[f] = nv
                        stats["entities"] += 1
    return stats


def outliers(cigars: list) -> list[dict]:
    out = []
    for c in cigars:
        st = c.get("smokeTimeMin")
        if isinstance(st, (int, float)) and (st <= 0 or st > 180):
            out.append({"id": c["id"], "issue": "smokeTimeMin", "value": st})
        for v in c.get("vitolas") or []:
            fmt = v.get("format") or ""
            m = re.search(r"(\d+)\s*x", fmt)
            if m:
                ring = int(m.group(1))
                if ring and (ring < 30 or ring > 80):
                    out.append({
                        "id": c["id"], "vitola": v.get("name"),
                        "issue": "ring-outlier", "value": ring, "format": fmt,
                    })
        if (c.get("wrapper") or "") == "—" and c.get("catalogSource") != "market":
            # only flag if any vitola note elsewhere — keep light
            pass
    return out


def write_findings(path: Path, sections: dict) -> None:
    lines = [
        "# Corpus audit findings",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Auto-fixed",
        "",
    ]
    for k, v in (sections.get("auto_fixed") or {}).items():
        lines.append(f"- **{k}**: {v}")
    lines += ["", "## Review required", ""]
    for item in sections.get("review") or []:
        lines.append(f"- {item}")
    lines += ["", "## Counts", ""]
    for k, v in (sections.get("counts") or {}).items():
        lines.append(f"- **{k}**: {v}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="Apply auto-fixes")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    brands = json.loads(BRANDS.read_text(encoding="utf-8"))

    auto = {}
    if args.fix:
        ent = fix_entities_and_countries(cigars)
        auto["html_entities_fields"] = ent["entities"]
        auto["country_normalized"] = ent["countries"]
        # describe-lines for HR leaks if present
        dl = ROOT / "describe-lines.py"
        if dl.exists():
            # write cigars first so describe-lines sees entity fixes
            CIGARS.write_text(json.dumps(cigars, ensure_ascii=False, indent=1), encoding="utf-8")
            subprocess.check_call(["python", str(dl)], cwd=str(APP))
            cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
            auto["describe_lines_ran"] = True
        else:
            auto["describe_lines_ran"] = False
        CIGARS.write_text(json.dumps(cigars, ensure_ascii=False, indent=1), encoding="utf-8")

    dupes = brand_dupe_candidates(brands, cigars)
    markets = markets_audit(cigars)
    blurbs = blurb_review(brands)
    leaks = note_leak_counts(cigars)
    outs = outliers(cigars)

    (OUT / "brand_dupe_candidates.json").write_text(
        json.dumps({"count": len(dupes), "candidates": dupes}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT / "markets_audit_report.json").write_text(
        json.dumps(markets, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    (OUT / "blurb_translation_review.json").write_text(
        json.dumps({"count": len(blurbs), "items": blurbs}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    review = [
        f"Brand dupe candidates: {len(dupes)} (see brand_dupe_candidates.json) — editorial",
        f"Markets without source HR={markets['without_source']['HR']['count']} "
        f"EU={markets['without_source']['EU']['count']} "
        f"USA={markets['without_source']['USA']['count']} — do not auto-remove EU/USA without live catalog",
        f"Blurbs for translation review: {len(blurbs)}",
        f"Outliers (smokeTime/ring): {len(outs)}",
    ]
    if leaks["hr_en_leak"]["count"]:
        review.append(
            f"HR notes still have EN leak patterns: {leaks['hr_en_leak']['count']} "
            "(merge P3 describe-lines fix or re-run with --fix after cherry-pick)"
        )
    if leaks["en_hr_leak"]["count"]:
        review.append(f"EN notes still have HR leak patterns: {leaks['en_hr_leak']['count']}")

    write_findings(OUT / "corpus_audit_findings.md", {
        "auto_fixed": auto,
        "review": review,
        "counts": {
            "cigars": len(cigars),
            "brands": len(brands),
            "hr_en_leak": leaks["hr_en_leak"]["count"],
            "en_hr_leak": leaks["en_hr_leak"]["count"],
            "empty_notes": leaks["empty"]["count"],
            "hr_eq_en": leaks["hr_eq_en"]["count"],
            "filler_hr": leaks["filler_hr"]["count"],
            "brand_dupe_candidates": len(dupes),
            "blurb_review": len(blurbs),
            "outliers": len(outs),
            **{f"markets_without_{r}": markets["without_source"][r]["count"] for r in ("HR", "EU", "USA")},
            **{f"link_missing_market_{r}": markets["has_link_missing_market"][r]["count"] for r in ("HR", "EU", "USA")},
        },
    })
    # also dump leaks + outliers for review
    (OUT / "note_leak_report.json").write_text(
        json.dumps(leaks, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    (OUT / "outliers_report.json").write_text(
        json.dumps({"count": len(outs), "items": outs}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({"auto": auto, "leaks_hr": leaks["hr_en_leak"]["count"],
                      "leaks_en": leaks["en_hr_leak"]["count"],
                      "dupes": len(dupes), "blurbs": len(blurbs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
