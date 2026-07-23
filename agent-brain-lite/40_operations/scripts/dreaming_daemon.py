#!/usr/bin/env python3
"""Dreaming Daemon — grounded framework generation from run logs."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
RUN_LOGS = REPO_ROOT / ".agent" / "dreaming" / "run_logs"
FRAMEWORKS = REPO_ROOT / ".agent" / "dreaming" / "frameworks"
SCORES = REPO_ROOT / ".agent" / "dreaming" / "success_scores.json"


def slugify(text: str, max_len: int = 48) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len].strip("-") or "framework"


def load_run_events() -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if not RUN_LOGS.is_dir():
        return events
    for path in sorted(RUN_LOGS.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def extract_patterns(events: list[dict[str, Any]], *, similarity_threshold: float = 0.7) -> list[dict[str, Any]]:
    """Find repeated or TF-IDF-similar tool/outcome motifs with source references."""
    entries: list[dict[str, Any]] = []
    for idx, ev in enumerate(events):
        tool = str(ev.get("tool") or ev.get("action") or "unknown")
        outcome = str(ev.get("outcome") or ev.get("result") or "")
        if not outcome:
            continue
        entries.append(
            {
                "tool": tool,
                "outcome": outcome,
                "text": f"{tool} {outcome}",
                "ref": f".agent/dreaming/run_logs event#{idx + 1}",
            }
        )
    if not entries:
        return []

    # Exact duplicates first
    exact: Counter[str] = Counter()
    exact_refs: dict[str, list[str]] = {}
    for e in entries:
        key = f"{e['tool']}:{e['outcome'][:80]}"
        exact[key] += 1
        exact_refs.setdefault(key, []).append(e["ref"])

    patterns: list[dict[str, Any]] = []
    used_indices: set[int] = set()

    for key, count in exact.most_common(8):
        if count < 2:
            continue
        tool, outcome = key.split(":", 1)
        patterns.append(
            {
                "title": f"Repeated {tool} outcome",
                "premise": f"Tool `{tool}` produced identical outcome {count} times in run logs.",
                "inference": "Consider codifying a checklist or SKILL step before this tool runs.",
                "source_refs": exact_refs.get(key, [])[:5],
                "count": count,
            }
        )

    # TF-IDF clustering for similar (non-identical) outcomes
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        return patterns

    texts = [e["text"] for e in entries]
    if len(texts) < 2:
        return patterns

    matrix = TfidfVectorizer(min_df=1, ngram_range=(1, 2)).fit_transform(texts)
    sim = cosine_similarity(matrix)

    for i in range(len(entries)):
        if i in used_indices:
            continue
        cluster = [i]
        for j in range(i + 1, len(entries)):
            if j in used_indices:
                continue
            if sim[i, j] >= similarity_threshold:
                cluster.append(j)
        if len(cluster) < 2:
            continue
        for j in cluster:
            used_indices.add(j)
        tool = entries[cluster[0]]["tool"]
        refs = [entries[k]["ref"] for k in cluster]
        patterns.append(
            {
                "title": f"Similar {tool} outcomes (TF-IDF cluster)",
                "premise": f"Tool `{tool}` produced {len(cluster)} similar outcomes (cosine >= {similarity_threshold}).",
                "inference": "Review whether a shared precondition or SKILL gap explains the cluster.",
                "source_refs": refs[:5],
                "count": len(cluster),
            }
        )
    return patterns[:12]


def render_framework(pattern: dict[str, Any], today: str) -> str:
    title = pattern["title"]
    slug = slugify(title)
    lines = [
        f"# {title}",
        "",
        f"**Status:** hypothesis",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Date slug:** {today}",
        "",
        "## Premise (evidence-backed)",
        "",
        f"- {pattern['premise']}",
        "",
        "**Sources:**",
    ]
    for ref in pattern.get("source_refs", []):
        lines.append(f"- `{ref}`")
    lines.extend(
        [
            "",
            "## Inference (creative, not fact)",
            "",
            f"- {pattern['inference']}",
            "",
            "## Verification before use",
            "",
            "- Run Swiss Cheese or human review before applying to manuscripts or protocols.",
            "",
        ]
    )
    return "\n".join(lines), slug


def update_scores(framework_id: str, score: float) -> None:
    data: dict[str, Any] = {}
    if SCORES.is_file():
        try:
            data = json.loads(SCORES.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    data[framework_id] = {"score": score, "updated": datetime.now(timezone.utc).isoformat()}
    SCORES.parent.mkdir(parents=True, exist_ok=True)
    SCORES.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Dreaming Daemon — grounded framework builder")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--min-count", type=int, default=2)
    args = parser.parse_args()

    events = load_run_events()
    if not events:
        print("No run logs in .agent/dreaming/run_logs/ — nothing to dream.")
        return 0

    patterns = [p for p in extract_patterns(events) if p["count"] >= args.min_count]
    if not patterns:
        print("No repeated patterns found (min_count=%d)." % args.min_count)
        return 0

    today = date.today().isoformat()
    written: list[Path] = []
    for pattern in patterns:
        md, slug = render_framework(pattern, today)
        fname = f"{slug}_{today}.md"
        out = FRAMEWORKS / fname
        if args.dry_run:
            print(md[:400])
            print("---")
            continue
        FRAMEWORKS.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        written.append(out)
        update_scores(slug, float(pattern["count"]))

    if not args.dry_run:
        for path in written:
            print(f"Wrote {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
