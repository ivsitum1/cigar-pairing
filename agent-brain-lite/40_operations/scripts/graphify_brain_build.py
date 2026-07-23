#!/usr/bin/env python3
"""Build or refresh Graphify structural index for agent-rules brain."""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GRAPH_OUT = REPO_ROOT / "graphify-out"
GRAPH_JSON = GRAPH_OUT / "graph.json"
DEFAULT_IGNORE = REPO_ROOT / ".graphifyignore"
FULL_IGNORE = REPO_ROOT / ".graphifyignore.full"
DEFAULT_OLLAMA_URL = "http://localhost:11434/v1"
DEFAULT_OLLAMA_MODEL = "gemma4:latest"
PREFERRED_OLLAMA_MODELS = (
    "gemma4:latest",
    "gemma4",
    "gemma3:4b",
    "gemma3:12b",
    "gemma3:latest",
    "gemma2:2b",
)
DEFAULT_TOKEN_BUDGET = 8000
REFILL_DOC_PREFIXES = (
    "30_system/",
    "30_system\\",
    ".cursor/rules/",
    ".cursor\\rules\\",
    ".cursor/skills/",
    ".cursor\\skills\\",
    ".agents/skills/",
    ".agents\\skills\\",
)


def _invalidate_doc_cache(prefixes: tuple[str, ...] = REFILL_DOC_PREFIXES) -> int:
    """Drop stat-index entries for rules/skills/docs so --update re-extracts them."""
    stat_path = GRAPH_OUT / "cache" / "stat-index.json"
    if not stat_path.is_file():
        return 0
    index = json.loads(stat_path.read_text(encoding="utf-8"))
    removed = 0
    kept: dict = {}
    for key, meta in index.items():
        norm = key.replace("\\", "/")
        if any(p.replace("\\", "/") in norm for p in prefixes):
            removed += 1
            continue
        kept[key] = meta
    if removed:
        stat_path.write_text(json.dumps(kept, ensure_ascii=False), encoding="utf-8")
    return removed


def _resolve_graphify_cmd() -> list[str]:
    if shutil.which("graphify"):
        return ["graphify"]
    return [sys.executable, "-m", "graphify"]


def _ollama_tags(base_url: str) -> list[str]:
    # Graphify uses OpenAI-compatible /v1; tags API lives on host root.
    root = base_url.rstrip("/")
    if root.endswith("/v1"):
        root = root[:-3]
    url = f"{root}/api/tags"
    with urllib.request.urlopen(url, timeout=5) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [m.get("name", "") for m in data.get("models", []) if m.get("name")]


def _pick_ollama_model(base_url: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    if os.environ.get("OLLAMA_MODEL"):
        return os.environ["OLLAMA_MODEL"]
    installed = _ollama_tags(base_url)
    if not installed:
        raise RuntimeError(
            f"No Ollama models at {base_url}. Run: ollama pull gemma4:latest"
        )
    for pref in PREFERRED_OLLAMA_MODELS:
        if pref in installed:
            return pref
    if DEFAULT_OLLAMA_MODEL in installed:
        return DEFAULT_OLLAMA_MODEL
    return installed[0]


def _check_ollama(base_url: str, model: str | None) -> str:
    try:
        return _pick_ollama_model(base_url, model)
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Ollama not reachable at {base_url}. Start Ollama, then retry.\n  {exc}"
        ) from exc


def _run(args: list[str], *, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    cmd = _resolve_graphify_cmd() + args
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=False,
        check=check,
        env=env,
    )


@contextlib.contextmanager
def _full_ignore_profile():
    """Swap to .graphifyignore.full for semantic doc extract, then restore."""
    if not FULL_IGNORE.is_file():
        raise FileNotFoundError(f"Missing {FULL_IGNORE}")
    backup = REPO_ROOT / ".graphifyignore.bak"
    had_default = DEFAULT_IGNORE.is_file()
    if had_default:
        shutil.copy2(DEFAULT_IGNORE, backup)
    shutil.copy2(FULL_IGNORE, DEFAULT_IGNORE)
    try:
        yield
    finally:
        if had_default and backup.is_file():
            shutil.move(str(backup), str(DEFAULT_IGNORE))
        elif backup.is_file():
            backup.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Graphify brain structural graph")
    parser.add_argument("--update", action="store_true", help="Incremental extract only")
    parser.add_argument("--force", action="store_true", help="Overwrite even if fewer nodes")
    parser.add_argument("--no-cluster", action="store_true", help="Skip Leiden clustering")
    parser.add_argument("--no-viz", action="store_true", help="Skip graph.html generation")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Semantic extract + clustering via local Ollama (default backend)",
    )
    parser.add_argument(
        "--backend",
        default="ollama",
        help="LLM backend for --full (default: ollama = local, no cloud API)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=f"Ollama model (default: {DEFAULT_OLLAMA_MODEL})",
    )
    parser.add_argument(
        "--ollama-url",
        default=os.environ.get("OLLAMA_BASE_URL", DEFAULT_OLLAMA_URL),
        help=f"Ollama base URL (default: {DEFAULT_OLLAMA_URL})",
    )
    parser.add_argument(
        "--token-budget",
        type=int,
        default=DEFAULT_TOKEN_BUDGET,
        help=f"Semantic chunk token budget (default: {DEFAULT_TOKEN_BUDGET}; use 4000 for refill pass)",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=2,
        help="Parallel Ollama extract workers (default: 2; use 1 for refill pass)",
    )
    parser.add_argument(
        "--refill-docs",
        action="store_true",
        help="Invalidate cache for rules/skills/docs paths before extract (--update recommended)",
    )
    args = parser.parse_args()

    try:
        _run(["--version"], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            "Graphify CLI not found. Install with:\n"
            '  pip install "graphifyy[mcp,ollama]"',
            file=sys.stderr,
        )
        return 1

    run_env: dict[str, str] | None = None
    if args.full and args.backend == "ollama":
        try:
            model = _check_ollama(args.ollama_url, args.model)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        run_env = os.environ.copy()
        run_env["OLLAMA_BASE_URL"] = args.ollama_url
        run_env["OLLAMA_API_KEY"] = run_env.get("OLLAMA_API_KEY", "local")
        run_env["OLLAMA_MODEL"] = model
        run_env.setdefault("GRAPHIFY_OLLAMA_NUM_CTX", "16384")
        print(f"Using local Ollama: {args.ollama_url} model={model}", flush=True)

    force = args.force or not args.update

    if args.refill_docs:
        n = _invalidate_doc_cache()
        print(f"Refill-docs: invalidated {n} stat-index entries for rules/skills/docs", flush=True)

    if args.full:
        extract_args = [
            "extract",
            ".",
            "--backend",
            args.backend,
            "--max-concurrency",
            str(args.max_concurrency),
            "--token-budget",
            str(args.token_budget),
        ]
        if args.backend == "ollama" and run_env:
            extract_args.extend(["--model", run_env["OLLAMA_MODEL"]])
        if args.update:
            extract_args.append("--update")
        if force:
            extract_args.append("--force")
        if args.no_cluster:
            extract_args.append("--no-cluster")
        if args.no_viz:
            extract_args.append("--no-viz")
        ctx = _full_ignore_profile()
    else:
        extract_args = ["update", ".", "--no-cluster"]
        if force:
            extract_args.append("--force")
        ctx = contextlib.nullcontext()

    try:
        with ctx:
            _run(extract_args, check=True, env=run_env)
    except subprocess.CalledProcessError as exc:
        return exc.returncode or 1
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if GRAPH_JSON.is_file():
        print(f"\nOK: {GRAPH_JSON} ({GRAPH_JSON.stat().st_size:,} bytes)")
        report = GRAPH_OUT / "GRAPH_REPORT.md"
        if report.is_file():
            print(f"Report: {report}")
        elif args.full and not args.no_cluster:
            print("Note: GRAPH_REPORT.md not found — check graphify extract output.")
        elif not args.full:
            print("Note: use --full for GRAPH_REPORT.md and semantic doc nodes (local Ollama).")
    else:
        print("WARN: graph.json not created — check graphify output.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
