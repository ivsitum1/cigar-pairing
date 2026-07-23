#!/usr/bin/env python3
"""Post-process NotebookLM batch exports: normalize, gate, executive, delta."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
OUT_DIR = WORKSPACE / "outputs" / "notebooklm"
BRIDGE = WORKSPACE / "40_operations/scripts/notebooklm_bridge.py"
QUESTIONS_CFG = WORKSPACE / "30_system/docs/reference/notebooklm_batch_2026-06_questions.json"

MAP_PATHS = {
    "okf-knowledge": WORKSPACE / "30_system/docs/OKF_KNOWLEDGE_MAP.md",
    "last-mile-glm": WORKSPACE / "30_system/docs/LAST_MILE_GLM_MAP.md",
    "humanize-predictability": WORKSPACE / "30_system/docs/HUMANIZE_PREDICTABILITY_MAP.md",
    "loop-of-loops": WORKSPACE / "30_system/docs/LOOP_OF_LOOPS_MAP.md",
}

DEDUP_NOTES = {
    "okf-knowledge": "Cross-check RAG Anatomy, RAG Chunking, wiki manifest, books_rag.",
    "last-mile-glm": "Cross-check Geometry model-native, strategic engineering, project_init.",
    "humanize-predictability": "Delta-only vs outputs/notebooklm/humanize_ai_vs_agent_rules_delta.md.",
    "loop-of-loops": "Cross-check Harness SkillTree, Ralph, AGENT_AUTONOMY_AND_PARALLEL, wiki skills.",
}


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_slugs() -> list[str]:
    cfg = json.loads(QUESTIONS_CFG.read_text(encoding="utf-8"))
    return list(cfg.get("notebooks", {}).keys())


def _batch_path(slug: str, pass2: bool) -> Path:
    return OUT_DIR / (f"{slug}_query_batch_pass2.json" if pass2 else f"{slug}_query_batch.json")


def _merge_batches(slug: str) -> Path:
    """Merge pass1 + pass2 into single query batch for gate."""
    p1 = _batch_path(slug, False)
    p2 = _batch_path(slug, True)
    if not p1.is_file():
        raise FileNotFoundError(p1)
    data = json.loads(p1.read_text(encoding="utf-8"))
    if p2.is_file():
        p2data = json.loads(p2.read_text(encoding="utf-8"))
        r1 = data.get("results") or []
        r2 = p2data.get("results") or []
        data["results"] = r1 + r2
        data["pass2_merged_at"] = _utc()
    merged = OUT_DIR / f"{slug}_query_batch_merged.json"
    merged.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return merged


def _run_bridge(cmd: str, inp: Path, out: Path) -> None:
    subprocess.run(
        [sys.executable, str(BRIDGE), cmd, "--input", str(inp), "--output", str(out)],
        cwd=WORKSPACE,
        check=True,
    )


def _extract_inventory(data: dict) -> dict:
    results = data.get("results") or []
    first_answer = ""
    if results and results[0]:
        first_answer = (results[0].get("result") or {}).get("answer") or ""
    return {
        "notebook_id": data.get("notebook_id"),
        "notebook_title": data.get("notebook_title"),
        "exported_at": _utc(),
        "source_list_answer": first_answer[:12000],
        "line_count": len(first_answer.splitlines()),
    }


def _success_count(data: dict) -> tuple[int, int]:
    results = data.get("results") or []
    ok = sum(1 for r in results if r and (r.get("result") or {}).get("success"))
    return ok, len(results)


def _write_executive(slug: str, data: dict, gate: dict, pass2: bool) -> Path:
    ok, total = _success_count(data)
    nb_id = data.get("notebook_id", "?")
    url = data.get("notebook_url", "")
    title = data.get("notebook_title", slug)
    path = OUT_DIR / f"{slug}_executive.md"
    thesis = ""
    for r in data.get("results") or []:
        if not r:
            continue
        q = (r.get("question") or "").lower()
        if "central thesis" in q or "3 sentences" in q:
            thesis = ((r.get("result") or {}).get("answer") or "")[:2000]
            break
    lines = [
        f"# {title} — executive summary",
        "",
        f"**Slug:** `{slug}`  ",
        f"**Notebook:** {url}  ",
        f"**ID:** `{nb_id}`  ",
        f"**Grill turns:** {ok}/{total}" + (" (pass1+pass2 merged)" if pass2 else ""),
        f"**Gate:** {gate.get('verdict', '?')} — UNVERIFIED: {gate.get('unverified_count', '?')}",
        f"**Dedup:** {DEDUP_NOTES.get(slug, '')}",
        "",
        "## Thesis (from grill)",
        "",
        thesis or "_See query batch._",
        "",
        "## Artifacts",
        "",
        f"- `outputs/notebooklm/{slug}_query_batch.json`",
        f"- `outputs/notebooklm/{slug}_gate_report.json`",
        f"- `outputs/notebooklm/{slug}_vs_agent_rules_delta.md`",
        f"- Map: `{MAP_PATHS.get(slug, '').relative_to(WORKSPACE).as_posix() if slug in MAP_PATHS else 'TBD'}`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _write_delta(slug: str, data: dict, gate: dict) -> Path:
    path = OUT_DIR / f"{slug}_vs_agent_rules_delta.md"
    p0_block = ""
    for r in data.get("results") or []:
        if not r:
            continue
        q = (r.get("question") or "").lower()
        if "p0/p1/p2" in q or "p0" in q and "agent-rules" in q:
            p0_block = ((r.get("result") or {}).get("answer") or "")[:6000]
            break
    reject_block = ""
    for r in data.get("results") or []:
        if not r:
            continue
        q = (r.get("question") or "").lower()
        if "reject" in q:
            reject_block = ((r.get("result") or {}).get("answer") or "")[:3000]
            break
    lines = [
        f"# Delta: {slug} vs agent-rules",
        "",
        f"**Gate:** {gate.get('verdict', '?')}  ",
        f"**Generated:** {_utc()}",
        "",
        "## Proposed changes (from grill)",
        "",
        p0_block or "_Run grill P0 question._",
        "",
        "## Rejected / caution",
        "",
        reject_block or "_See grill reject question._",
        "",
        "## Dedup note",
        "",
        DEDUP_NOTES.get(slug, ""),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _write_skill_fit(slug: str, gate: dict) -> Path:
    path = OUT_DIR / f"{slug}_skill_fit_assessment.md"
    lines = [
        f"# Skill fit: {slug}",
        "",
        f"**Verdict:** {gate.get('verdict', '?')}",
        f"**Claims:** {gate.get('claim_count', 0)} | UNVERIFIED: {gate.get('unverified_count', 0)}",
        "",
        "## Registry mapping (manual refine after grill)",
        "",
        "| Cluster | Likely skill | Action |",
        "|---------|--------------|--------|",
    ]
    skill_hints = {
        "okf-knowledge": ("notebooklm-research-gate, wiki-ingest, meta-analysis", "extend reference"),
        "last-mile-glm": ("grill-me, setup-project, agentic-react-os", "docs + project_init"),
        "humanize-predictability": ("avoid-ai-formulations, manuscript-writing", "delta vs humanize_ai"),
        "loop-of-loops": ("wiki-synthesize, daily-update, research-grill-me", "L4 trajectory map"),
    }
    hint = skill_hints.get(slug, ("TBD", "TBD"))
    lines.append(f"| Primary | {hint[0]} | {hint[1]} |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _write_map(slug: str, data: dict, gate: dict) -> Path | None:
    map_path = MAP_PATHS.get(slug)
    if not map_path:
        return None
    map_path.parent.mkdir(parents=True, exist_ok=True)
    nb_id = (json.loads(QUESTIONS_CFG.read_text(encoding="utf-8"))["notebooks"][slug]["id"])
    lines = [
        f"# {slug.replace('-', ' ').title()} — agent-rules map",
        "",
        f"**Notebook ID:** `{nb_id}`  ",
        f"**Gate:** {gate.get('verdict', '?')}  ",
        f"**Last updated:** {_utc()}",
        "",
        "## Executive pointer",
        "",
        f"- [`outputs/notebooklm/{slug}_executive.md`](../../outputs/notebooklm/{slug}_executive.md)",
        f"- [`outputs/notebooklm/{slug}_vs_agent_rules_delta.md`](../../outputs/notebooklm/{slug}_vs_agent_rules_delta.md)",
        "",
        "## Repo anchors",
        "",
        DEDUP_NOTES.get(slug, ""),
        "",
        "## Implementation backlog",
        "",
        "See `.agent/task/notebooklm_batch_2026-06_backlog.md` for OKF-*, MILE-*, HUM-*, LOOP-* issues.",
        "",
    ]
    map_path.write_text("\n".join(lines), encoding="utf-8")
    return map_path


def process_slug(slug: str, pass2: bool) -> None:
    merged = _merge_batches(slug) if pass2 else _batch_path(slug, False)
    if pass2 and not _batch_path(slug, True).is_file():
        merged = _batch_path(slug, False)
    data = json.loads(merged.read_text(encoding="utf-8"))
    norm_out = OUT_DIR / f"{slug}_normalized.json"
    gate_out = OUT_DIR / f"{slug}_gate_report.json"
    _run_bridge("export-normalize", merged, norm_out)
    _run_bridge("gate-report", merged, gate_out)
    gate = json.loads(gate_out.read_text(encoding="utf-8"))
    inv = _extract_inventory(data)
    (OUT_DIR / f"{slug}_source_inventory.json").write_text(
        json.dumps(inv, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _write_executive(slug, data, gate, pass2)
    _write_delta(slug, data, gate)
    _write_skill_fit(slug, gate)
    _write_map(slug, data, gate)
    print(f"Processed {slug} -> {gate.get('verdict')}")


def write_merged_delta(slugs: list[str]) -> Path:
    out = OUT_DIR / "batch_2026-06_merged_delta.md"
    lines = [
        "# Merged delta: NotebookLM batch 2026-06",
        "",
        f"**Generated:** {_utc()}",
        "",
        "## Per-notebook summary",
        "",
    ]
    for slug in slugs:
        delta = OUT_DIR / f"{slug}_vs_agent_rules_delta.md"
        gate_path = OUT_DIR / f"{slug}_gate_report.json"
        verdict = "?"
        if gate_path.is_file():
            verdict = json.loads(gate_path.read_text(encoding="utf-8")).get("verdict", "?")
        lines.append(f"### `{slug}` — gate **{verdict}**")
        lines.append("")
        if delta.is_file():
            body = delta.read_text(encoding="utf-8")
            # first 80 lines
            lines.extend(body.splitlines()[:40])
        lines.append("")
    lines.extend(
        [
            "## Cross-notebook dedup",
            "",
            "- humanize-predictability: do not duplicate humanize_ai (`ac8b47a1`)",
            "- loop-of-loops: align with Harness SkillTree + Ralph, do not replace orchestrator",
            "- okf-knowledge: OKF spike only; keep Obsidian wikilinks",
            "- last-mile-glm: JEPA/world models = research wiki only",
            "",
        ]
    )
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--pass2", action="store_true", help="Merge pass2 batches before gate")
    parser.add_argument("--merged-delta", action="store_true")
    args = parser.parse_args()
    slugs = _load_slugs()
    if args.merged_delta:
        write_merged_delta(slugs)
        return 0
    targets = slugs if args.all else ([args.slug] if args.slug else [])
    if not targets:
        parser.error("Specify --slug or --all")
    for slug in targets:
        if not _batch_path(slug, False).is_file():
            print(f"SKIP {slug}: no query batch", file=sys.stderr)
            continue
        process_slug(slug, args.pass2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
