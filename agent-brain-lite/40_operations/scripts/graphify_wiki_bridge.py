#!/usr/bin/env python3
"""Add inferred wiki↔code bridge edges to graphify-out/merged.json."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PY_ROOT = REPO_ROOT / "40_operations" / "python"
if str(PY_ROOT) not in sys.path:
    sys.path.insert(0, str(PY_ROOT))

from brain_assist.merged_graph_index import MergedGraphIndex  # noqa: E402

DEFAULT_MERGED = REPO_ROOT / "graphify-out" / "merged.json"


def apply_bridges(merged_path: Path, *, dry_run: bool = False) -> dict:
    index = MergedGraphIndex.load(merged_path)
    if index is None:
        raise FileNotFoundError(f"Missing merged graph: {merged_path}")

    data = json.loads(merged_path.read_text(encoding="utf-8"))
    links = list(data.get("links") or [])
    existing = {(l.get("source"), l.get("target"), l.get("relation")) for l in links}

    proposed = index.propose_bridge_links()
    added: list[dict] = []
    for link in proposed:
        key = (link["source"], link["target"], link["relation"])
        if key in existing:
            continue
        added.append(link)
        existing.add(key)

    if added and not dry_run:
        links.extend(added)
        meta = data.get("graph_meta") or {}
        meta["bridge_edges"] = meta.get("bridge_edges", 0) + len(added)
        meta["total_links"] = len(links)
        meta["bridged"] = True
        data["links"] = links
        data["graph_meta"] = meta
        merged_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    return {
        "merged": str(merged_path),
        "proposed": len(proposed),
        "added": len(added),
        "total_links": len(links) if not dry_run else len(links) + len(added),
        "dry_run": dry_run,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Add wiki↔code bridge edges to merged.json")
    parser.add_argument("--merged", type=Path, default=DEFAULT_MERGED)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        report = apply_bridges(args.merged, dry_run=args.dry_run)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        mode = "dry-run" if report["dry_run"] else "applied"
        print(
            f"bridge {mode}: proposed={report['proposed']} added={report['added']} "
            f"total_links={report['total_links']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
