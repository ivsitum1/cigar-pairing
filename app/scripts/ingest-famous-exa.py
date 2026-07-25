#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ingest Exa search/fetch dumps into cw_famous_flavor_raw.json.

Expects scripts/output/famous_exa_results.json:
  [
    {
      "id": "cig-...",
      "brand": "...",
      "line": "...",
      "results": [
        {"url": "...", "title": "...", "text": "...highlights/markdown..."}
      ]
    }
  ]

  python scripts/ingest-famous-exa.py
  python scripts/convert-cw-famous-raw.py
  python scripts/merge-flavor-enrichment.py --batch 2
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "output" / "famous_exa_results.json"
RAW = HERE / "output" / "cw_famous_flavor_raw.json"

FACT_LABELS = (
    "wrapper leaf",
    "wrapper color",
    "wrapper origin",
    "wrapper",
    "binder",
    "filler",
    "strength",
    "country of origin",
    "country",
    "cigar shape",
    "ring gauge",
)


def pick_best(results: list[dict], brand: str, line: str) -> dict | None:
    scored: list[tuple[int, dict]] = []
    b = (brand or "").lower()
    l = (line or "").lower()
    for r in results:
        url = (r.get("url") or "").lower()
        title = (r.get("title") or "").lower()
        text = (r.get("text") or "")
        if "famous-smoke.com" not in url:
            continue
        if "/cigaradvisor/" in url:
            continue
        score = 0
        if "-cigars" in url:
            score += 5
        if url.rstrip("/").endswith(tuple(["-natural", "-maduro", "-dark-natural"])):
            score += 2
        if "/brand" in url or "/brands/" in url:
            score += 3  # line-level specs often good enough
        if any(tok in url or tok in title for tok in l.replace("/", " ").split() if len(tok) > 3):
            score += 2
        if b and b.split()[0] in url:
            score += 1
        if "wrapper" in text.lower() or "strength" in text.lower():
            score += 2
        if "box-of" in url:
            score -= 1
        scored.append((score, r))
    if not scored:
        return None
    scored.sort(key=lambda x: -x[0])
    return scored[0][1]


def parse_text(text: str) -> dict:
    facts: dict[str, str] = {}

    def maybe_set(k: str, v: str) -> None:
        k = re.sub(r"\s+", " ", k).strip().lower()
        v = re.sub(r"\s+", " ", v).strip()
        if not k or not v or v.lower() == "---" or k == "---":
            return
        if k == "specifications":
            return
        if any(lab in k for lab in FACT_LABELS) or k in FACT_LABELS:
            facts[k] = v[:120]

    # Prefer line-oriented 2-column markdown rows (avoids 3-col header shift)
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 2:
            maybe_set(cells[0], cells[1])
        elif len(cells) >= 3 and cells[0].lower() == "specifications":
            # "| Specifications | Strength | Medium |" style
            maybe_set(cells[1], cells[2])

    # bullet lines: - Wrapper: ...
    for m in re.finditer(
        r"(?im)^(?:[-*]\s*)?(Wrapper(?:\s+Leaf|\s+Color|\s+Origin)?|Binder|Filler|Strength|Country(?:\s+of\s+Origin)?)\s*[:|-]\s*(.+)$",
        text,
    ):
        maybe_set(m.group(1), m.group(2))

    if facts.get("wrapper leaf") and not facts.get("wrapper"):
        facts["wrapper"] = facts["wrapper leaf"]
    if facts.get("country of origin") and not facts.get("country"):
        facts["country"] = facts["country of origin"]

    # description: longest prose paragraph with flavor words
    desc = ""
    paras = re.split(r"\n\s*\n", text)
    flavorish = re.compile(
        r"\b(notes?|flavor|flavour|wrapper|cedar|cocoa|pepper|cream|leather|spice|sweet|earthy|coffee)\b",
        re.I,
    )
    for p in paras:
        p = re.sub(r"\s+", " ", p).strip()
        if len(p) < 80 or not flavorish.search(p):
            continue
        if p.startswith("|") or p.startswith("#"):
            continue
        if len(p) > len(desc):
            desc = p[:2000]

    return {
        "facts": facts,
        "description": desc,
        "ok": bool(facts or (desc and len(desc) > 80)),
    }


def main() -> None:
    if not SRC.exists():
        print(f"missing {SRC}")
        return
    batches = json.loads(SRC.read_text(encoding="utf-8"))
    prior = {r["id"]: r for r in json.loads(RAW.read_text(encoding="utf-8"))} if RAW.exists() else {}

    ok_n = 0
    for row in batches:
        best = pick_best(row.get("results") or [], row.get("brand") or "", row.get("line") or "")
        entry = prior.get(row["id"]) or {
            "id": row["id"],
            "brand": row.get("brand"),
            "line": row.get("line"),
            "cigarworld": {"ok": False},
            "famous": {"ok": False},
        }
        if not best:
            entry["famous"] = {
                "ok": False,
                "error": "no famous-smoke result",
                "search_url": f"exa:{row.get('brand')} {row.get('line')}",
            }
            prior[row["id"]] = entry
            continue
        parsed = parse_text(best.get("text") or "")
        parsed["title"] = best.get("title") or ""
        parsed["product_url"] = best.get("url")
        parsed["search_url"] = f"exa:{row.get('brand')} {row.get('line')}"
        entry["famous"] = parsed
        prior[row["id"]] = entry
        if parsed["ok"]:
            ok_n += 1
            print(
                f"ok {row['id']} wrap={parsed['facts'].get('wrapper')} "
                f"str={parsed['facts'].get('strength')} url={parsed['product_url'][-50:]}"
            )
        else:
            print(f"miss {row['id']}")

    RAW.write_text(json.dumps(list(prior.values()), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ingested={len(batches)} famous_ok={ok_n} -> {RAW}")


if __name__ == "__main__":
    main()
