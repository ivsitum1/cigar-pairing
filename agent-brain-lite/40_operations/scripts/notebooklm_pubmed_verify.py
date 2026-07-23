#!/usr/bin/env python3
"""PubMed E-utilities cross-check for NotebookLM external benchmark claims."""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
OUT = WORKSPACE / "30_system" / "docs" / "notebooklm_pubmed_verification.json"
LIT = WORKSPACE / "30_system" / "docs" / "notebooklm_external_verification.json"

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

QUERIES = [
    {
        "registry_id": "LH-54PCT",
        "query": '"Language Models are Few-Shot Butlers"[Title] OR (AlfWorld[Title/Abstract] AND imitation learning[Title/Abstract])',
        "expect": "Micheli et al. EMNLP 2021 AlfWorld +51% absolute improvement",
    },
    {
        "registry_id": "TGS-80PCT",
        "query": "(retrieval augmented generation[Title/Abstract]) AND (knowledge graph[Title/Abstract] OR multi-hop[Title/Abstract])",
        "expect": "Graph-RAG / neuro-symbolic RAG efficiency papers",
    },
    {
        "registry_id": "SKILLS-4700",
        "query": "agent skills software repository daily",
        "expect": "Non-biomedical; PubMed not appropriate primary source",
        "pubmed_appropriate": False,
    },
]


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pubmed_search(term: str, retmax: int = 5) -> list[dict[str, str]]:
    params = {
        "db": "pubmed",
        "term": term,
        "retmax": str(retmax),
        "retmode": "json",
    }
    url = f"{ESEARCH}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    ids = data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []
    summary_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
        + urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids), "retmode": "xml"})
    )
    with urllib.request.urlopen(summary_url, timeout=30) as resp:
        root = ET.fromstring(resp.read())
    hits: list[dict[str, str]] = []
    for doc in root.findall(".//DocSum"):
        id_elem = doc.find("Id")
        pmid = (id_elem.text or "").strip() if id_elem is not None else ""
        title = ""
        for item in doc.findall("Item"):
            if item.get("Name") == "Title":
                title = (item.text or "").strip()
        if pmid:
            hits.append({"pmid": pmid, "title": title})
    return hits


def main() -> int:
    results = []
    for q in QUERIES:
        try:
            hits = pubmed_search(q["query"])
        except Exception as e:
            hits = []
            err = str(e)
        else:
            err = ""
        row = {
            "registry_id": q["registry_id"],
            "pubmed_query": q["query"],
            "search_utc": _utc(),
            "hits": hits,
            "hit_count": len(hits),
            "error": err or None,
            "note": q["expect"],
            "pubmed_appropriate": q.get("pubmed_appropriate", True),
        }
        if q.get("pubmed_appropriate") is False:
            row["pubmed_verdict"] = "NOT_APPLICABLE"
        elif hits:
            row["pubmed_verdict"] = "HITS_REQUIRE_MANUAL_REVIEW"
        else:
            row["pubmed_verdict"] = "NO_PUBMED_MATCH"
        results.append(row)

    payload = {
        "verified_utc": _utc(),
        "method": "NCBI E-utilities esearch+esummary (PubMed MCP unavailable)",
        "claims": results,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    if LIT.is_file():
        lit = json.loads(LIT.read_text(encoding="utf-8"))
        by_id = {c["registry_id"]: c for c in lit.get("claims", [])}
        for r in results:
            entry = by_id.get(r["registry_id"])
            if entry:
                entry["pubmed_verification"] = {
                    "path": str(OUT.relative_to(WORKSPACE)).replace("\\", "/"),
                    "hit_count": r["hit_count"],
                    "top_pmids": [h["pmid"] for h in r["hits"][:3]],
                }
        lit["pubmed_pass_utc"] = _utc()
        LIT.write_text(json.dumps(lit, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({"written": str(OUT), "claims": len(results)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
