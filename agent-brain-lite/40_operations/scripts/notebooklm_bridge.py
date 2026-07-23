#!/usr/bin/env python3
"""
NotebookLM export normalize, research gate report, and wiki ingest bridge.

Usage:
  python 40_operations/scripts/notebooklm_bridge.py export-normalize --input outputs/notebooklm/geometry_query_latest.json
  python 40_operations/scripts/notebooklm_bridge.py gate-report --input outputs/notebooklm/geometry_query_latest.json
  python 40_operations/scripts/notebooklm_bridge.py wiki-ingest --input outputs/notebooklm/geometry_query_latest.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
WIKI_SOURCES = WORKSPACE / "20_knowledge" / "wiki" / "sources" / "notebooklm"
WIKI_LOG = WORKSPACE / "20_knowledge" / "wiki" / "log.md"

CLAIM_PATTERNS = [
    (re.compile(r"\+\d+%|\d+%\s+(boost|improvement|reduction)", re.I), "UNVERIFIED"),
    (re.compile(r"\b(SAE|steering vector|eigenvector|LifeHarness|SkillRAE|MUSE)\b", re.I), "INFERRED"),
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_input(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_turns(data: dict) -> list[dict]:
    if "chat_turns" in data:
        return data["chat_turns"]
    if "data" in data and isinstance(data["data"], dict):
        inner = data["data"]
        if inner.get("question") or inner.get("answer"):
            return [{"question": inner.get("question", ""), "answer": inner.get("answer", "")}]
    turns: list[dict] = []
    if "answer" in data:
        turns.append(
            {
                "question": data.get("question", ""),
                "answer": data.get("answer", ""),
            }
        )
    if "results" in data:
        for item in data["results"]:
            q = item.get("question", "")
            r = item.get("result") or {}
            ans = r.get("answer") or r.get("content") or str(r)
            turns.append({"question": q, "answer": ans})
    return turns


def export_normalize(data: dict, notebook_id: str | None = None) -> dict:
    turns = _extract_turns(data)
    return {
        "notebook_id": notebook_id or data.get("notebook_id", "unknown"),
        "notebook_title": data.get("notebook_title", data.get("notebook_url", "")),
        "exported_at": _utc_now(),
        "chat_turns": [
            {
                "turn_index": i,
                "question": t.get("question", ""),
                "answer": t.get("answer", ""),
                "citations": t.get("citations"),
                "source_refs": t.get("source_refs"),
                "timestamp": t.get("timestamp"),
            }
            for i, t in enumerate(turns)
        ],
    }


def _tag_claims(text: str) -> list[dict]:
    claims: list[dict] = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        s = sentence.strip()
        if len(s) < 20:
            continue
        status = "INFERRED"
        for pattern, tag in CLAIM_PATTERNS:
            if pattern.search(s):
                status = tag
                break
        if any(kw in s.lower() for kw in ("unverified", "not verified", "speculative")):
            status = "UNVERIFIED"
        claims.append({"text": s[:500], "status": status})
    return claims[:50]


def gate_report(normalized: dict) -> dict:
    all_claims: list[dict] = []
    blockers: list[str] = []
    for turn in normalized.get("chat_turns", []):
        ans = turn.get("answer") or ""
        claims = _tag_claims(ans)
        all_claims.extend(claims)
    unverified = [c for c in all_claims if c["status"] == "UNVERIFIED"]
    if len(unverified) > 5:
        blockers.append("high_unverified_claim_count")
    go = len(blockers) == 0 or len(unverified) <= 10
    return {
        "exported_at": _utc_now(),
        "verdict": "GO" if go else "NO-GO",
        "claim_count": len(all_claims),
        "unverified_count": len(unverified),
        "blockers": blockers,
        "claims": all_claims,
        "notes": [
            "Cross-check critical UNVERIFIED claims via research-lookup before rules/skill changes.",
            "NotebookLM output is untrusted input per AI Semantic Gate.",
        ],
    }


def wiki_ingest(normalized: dict, gate: dict, slug: str) -> Path:
    WIKI_SOURCES.mkdir(parents=True, exist_ok=True)
    out = WIKI_SOURCES / f"{slug}.md"
    lines = [
        "---",
        "tags:",
        "  - source",
        "  - notebooklm",
        f"verdict: {gate['verdict']}",
        f"exported_at: {normalized.get('exported_at', '')}",
        "---",
        "",
        f"# NotebookLM export: {slug}",
        "",
        f"**Gate verdict:** {gate['verdict']} | UNVERIFIED claims: {gate['unverified_count']}",
        "",
        "## Related",
        "",
        "- [[NotebookLM research gate]]",
        "- [[LifeHarness four-layer model]]",
        "",
        "## Summary",
        "",
    ]
    for turn in normalized.get("chat_turns", [])[:3]:
        q = turn.get("question", "")[:200]
        a = (turn.get("answer") or "")[:1500]
        lines.append(f"### Q: {q}")
        lines.append("")
        lines.append(a)
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    log_entry = f"\n[{_utc_now()}] [A] NotebookLM wiki-ingest: {slug} verdict={gate['verdict']}\n"
    if WIKI_LOG.is_file():
        WIKI_LOG.write_text(WIKI_LOG.read_text(encoding="utf-8") + log_entry, encoding="utf-8")
    else:
        WIKI_LOG.parent.mkdir(parents=True, exist_ok=True)
        WIKI_LOG.write_text(log_entry, encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="NotebookLM bridge")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_norm = sub.add_parser("export-normalize")
    p_norm.add_argument("--input", required=True)
    p_norm.add_argument("--output", default="")
    p_norm.add_argument("--notebook-id", default="")

    p_gate = sub.add_parser("gate-report")
    p_gate.add_argument("--input", required=True)
    p_gate.add_argument("--output", default="")

    p_wiki = sub.add_parser("wiki-ingest")
    p_wiki.add_argument("--input", required=True)
    p_wiki.add_argument("--slug", default="geometry_export")

    p_emp = sub.add_parser("empirical-validate")
    p_emp.add_argument("--registry", default="30_system/docs/notebooklm_benchmark_registry.json")
    p_emp.add_argument("--gate-input", default="outputs/notebooklm/geometry_query_latest.json")
    p_emp.add_argument("--output", default="")
    p_emp.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.cmd == "empirical-validate":
        sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))
        from notebooklm.empirical_validate import merge_into_gate_report, run_empirical_validation

        reg = Path(args.registry)
        if not reg.is_file():
            reg = WORKSPACE / args.registry
        empirical = run_empirical_validation(reg)
        gate_in = Path(args.gate_input)
        if not gate_in.is_file():
            gate_in = WORKSPACE / args.gate_input
        if gate_in.is_file():
            norm = export_normalize(_load_input(gate_in))
            procedural = gate_report(norm)
            merged = merge_into_gate_report(procedural, empirical)
        else:
            merged = empirical
        out_path = Path(args.output) if args.output else WORKSPACE / "outputs" / "notebooklm" / "empirical_gate_report.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
        if args.json:
            print(json.dumps(merged, ensure_ascii=False, indent=2))
        else:
            print(str(out_path))
            s = empirical["summary"]
            print(f"verified={s['verified']} inferred={s['inferred']} unverified={s['unverified']}")
        return 0

    inp = Path(args.input)
    if not inp.is_file():
        inp = WORKSPACE / args.input
    data = _load_input(inp)

    if args.cmd == "export-normalize":
        norm = export_normalize(data, args.notebook_id or None)
        out_path = Path(args.output) if args.output else inp.parent / "normalized_export.json"
        out_path.write_text(json.dumps(norm, ensure_ascii=False, indent=2), encoding="utf-8")
        print(str(out_path))
        return 0

    norm = export_normalize(data)
    report = gate_report(norm)

    if args.cmd == "gate-report":
        out_path = Path(args.output) if args.output else inp.parent / "gate_report.json"
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(str(out_path))
        return 0

    if args.cmd == "wiki-ingest":
        path = wiki_ingest(norm, report, args.slug)
        print(str(path))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
