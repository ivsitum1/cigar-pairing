#!/usr/bin/env python3
"""Orchestrate NotebookLM batch grill for 2026-06 four-notebook sprint."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
QUESTIONS = WORKSPACE / "30_system/docs/reference/notebooklm_batch_2026-06_questions.json"
GRILL_PLAYWRIGHT = WORKSPACE / "40_operations/scripts/notebooklm_grill_playwright.py"
GRILL_CLI = WORKSPACE / "40_operations/scripts/notebooklm_batch_grill_cli.py"
OUT_DIR = WORKSPACE / "outputs" / "notebooklm"


def _load_config() -> dict:
    return json.loads(QUESTIONS.read_text(encoding="utf-8"))


def grill_slug(slug: str, pass_num: int, start: int, backend: str, dry_run: bool, force: bool = False) -> int:
    if backend == "cli":
        cmd = [
            sys.executable,
            str(GRILL_CLI),
            "--slug",
            slug,
            "--pass",
            str(pass_num),
            "--start",
            str(start),
        ]
        if force:
            cmd.append("--force")
    else:
        cfg = _load_config()
        nb_id = cfg["notebooks"][slug]["id"]
        url = f"https://notebooklm.google.com/notebook/{nb_id}"
        suffix = "_pass2" if pass_num == 2 else ""
        out = OUT_DIR / f"{slug}_query_batch{suffix}.json"
        questions = (
            list(cfg.get("pass2", []))
            if pass_num == 2
            else list(cfg.get("common", [])) + list(cfg.get("topic", {}).get(slug, []))
        )
        qfile = OUT_DIR / f"{slug}_questions_temp.json"
        qfile.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8")
        cmd = [
            sys.executable,
            str(GRILL_PLAYWRIGHT),
            "--notebook-url",
            url,
            "--output",
            str(out),
            "--questions-file",
            str(qfile),
            "--start",
            str(start),
        ]
    print(f"Grill {slug} pass{pass_num} backend={backend}", file=sys.stderr)
    if dry_run:
        print(" ".join(cmd))
        return 0
    return subprocess.call(cmd, cwd=WORKSPACE)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Single slug; default all notebooks")
    parser.add_argument("--pass", dest="pass_num", type=int, default=1, choices=[1, 2])
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--backend", choices=["cli", "playwright"], default="cli")
    parser.add_argument("--force", action="store_true", help="Re-grill all turns (use after new sources)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    cfg = _load_config()
    slugs = [args.slug] if args.slug else list(cfg.get("notebooks", {}).keys())
    # Stable order: okf first (most new brain artifacts)
    order = ["okf-knowledge", "last-mile-glm", "humanize-predictability", "loop-of-loops"]
    if not args.slug:
        slugs = [s for s in order if s in slugs]
    rc = 0
    for slug in slugs:
        if grill_slug(slug, args.pass_num, args.start, args.backend, args.dry_run, force=args.force) != 0:
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
