#!/usr/bin/env python3
"""Cluster error_log.jsonl into failure_patterns for self-harness weakness mining."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
ERROR_LOG = WORKSPACE / ".cursor" / "errors" / "error_log.jsonl"
WIKI_CONCEPT = WORKSPACE / "20_knowledge" / "wiki" / "concepts" / "Failure patterns registry.md"
OUT_JSON = WORKSPACE / "outputs" / "harness" / "failure_patterns.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cluster_errors(path: Path) -> dict:
    by_cat: Counter[str] = Counter()
    by_cluster: Counter[str] = Counter()
    samples: dict[str, list[dict]] = defaultdict(list)

    if not path.is_file():
        return {"clusters": [], "total": 0, "exported_at": _utc_now()}

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        cat = rec.get("cat", "unknown")
        ctx = (rec.get("ctx") or "general")[:80]
        by_cat[cat] += 1
        cluster_key = f"{cat}::{ctx}"
        by_cluster[cluster_key] += 1
        if len(samples[cluster_key]) < 3:
            samples[cluster_key].append(
                {
                    "id": rec.get("id"),
                    "err": (rec.get("err") or "")[:300],
                    "fix": (rec.get("fix") or "")[:300],
                    "sev": rec.get("sev"),
                }
            )

    clusters = []
    for key, count in sorted(by_cluster.items(), key=lambda x: -x[1])[:20]:
        cat = key.split("::", 1)[0] if "::" in key else "unknown"
        ctx = key.split("::", 1)[1] if "::" in key else key
        clusters.append(
            {
                "cluster_key": ctx,
                "category": cat,
                "size": count,
                "actionability": "high" if count >= 2 else "medium",
                "samples": samples.get(key, []),
            }
        )

    try:
        source = str(path.relative_to(WORKSPACE)).replace("\\", "/")
    except ValueError:
        source = str(path)

    return {
        "exported_at": _utc_now(),
        "source": source,
        "total": sum(by_cat.values()),
        "by_category": dict(by_cat),
        "clusters": clusters,
    }


def write_wiki_snippet(report: dict) -> None:
    if not WIKI_CONCEPT.is_file():
        return
    text = WIKI_CONCEPT.read_text(encoding="utf-8")
    marker = "## Latest cluster export"
    block = (
        f"{marker}\n\n"
        f"- Exported: {report['exported_at']}\n"
        f"- Total errors: {report['total']}\n"
        f"- Top clusters: {len(report['clusters'])}\n"
    )
    if marker in text:
        head, _, _tail = text.partition(marker)
        WIKI_CONCEPT.write_text(head.rstrip() + "\n\n" + block, encoding="utf-8")
    else:
        WIKI_CONCEPT.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Failure patterns bridge")
    parser.add_argument("--input", default=str(ERROR_LOG), help="error_log.jsonl path")
    parser.add_argument("--output", default=str(OUT_JSON), help="JSON output")
    parser.add_argument("--update-wiki", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print to stdout")
    args = parser.parse_args()

    report = cluster_errors(Path(args.input))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.update_wiki:
        write_wiki_snippet(report)

    if args.json:
        payload = json.dumps(report, ensure_ascii=False, indent=2)
        try:
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass
        print(payload)
    else:
        print(f"Wrote {out_path} ({report['total']} errors, {len(report['clusters'])} clusters)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
