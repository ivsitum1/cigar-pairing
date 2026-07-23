#!/usr/bin/env python3
"""Batch SkillsMP keyword search; writes JSON report."""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

QUERIES = {
    "legal_contract": "contract review",
    "legal_gdpr": "GDPR privacy compliance",
    "legal_research": "legal research memo",
    "clinical_cdss": "clinical decision support",
    "clinical_anesthesia": "anesthesiology perioperative",
    "clinical_ecmo": "ECMO critical care",
    "stats_meta": "systematic review meta-analysis PRISMA",
    "stats_bayes": "Bayesian clinical trial biostatistics",
    "stats_r": "biostatistics R survival analysis",
    "science_pubmed": "PubMed literature search",
    "science_lit": "literature review biomedical",
    "marketing_content": "content marketing strategy B2B",
    "marketing_seo": "SEO content strategy",
    "business_grant": "grant proposal NIH specific aims",
    "ethics_irb": "IRB research ethics human subjects",
    "health_econ": "health economics cost effectiveness",
}

BASE = "https://skillsmp.com/api/v1/skills/search"


def search(q: str, limit: int = 15) -> dict:
    url = f"{BASE}?q={urllib.parse.quote(q)}&limit={limit}&sortBy=stars"
    with urllib.request.urlopen(url, timeout=40) as resp:
        return json.loads(resp.read().decode())


def main() -> None:
    out: dict = {}
    for tag, q in QUERIES.items():
        try:
            data = search(q)
            skills = data.get("data", {}).get("skills", [])
            out[tag] = {
                "query": q,
                "count": len(skills),
                "top": [
                    {
                        "name": s.get("name"),
                        "author": s.get("author"),
                        "stars": s.get("stars"),
                        "description": (s.get("description") or "")[:280],
                        "githubUrl": s.get("githubUrl"),
                        "skillUrl": s.get("skillUrl"),
                    }
                    for s in skills[:12]
                ],
            }
        except Exception as exc:  # noqa: BLE001
            out[tag] = {"query": q, "error": str(exc)}
        time.sleep(0.35)

    root = Path(__file__).resolve().parents[2]
    dest = root / ".agent" / "task" / "skillsmp_search_results.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {dest}")
    for tag, v in out.items():
        if "error" in v:
            print(f"  {tag}: ERR {v['error']}")
        elif v.get("top"):
            t0 = v["top"][0]
            print(
                f"  {tag}: {v['count']} | {t0.get('author')}/{t0.get('name')} "
                f"stars={t0.get('stars')}"
            )


if __name__ == "__main__":
    main()
