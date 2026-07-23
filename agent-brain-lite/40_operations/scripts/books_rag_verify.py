#!/usr/bin/env python3
"""Verify books RAG index integrity and live retrieval."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE))
sys.path.insert(0, str(WORKSPACE / "40_operations" / "python"))

from books_rag.config import load_config
from books_rag.retrieval import BooksRetriever
from common.gpu import resolve_device


def _check_count(retriever: BooksRetriever, *, tolerance: float) -> dict:
    status = retriever.status()
    live = int(status.get("chunk_count") or 0)
    manifest = int(status.get("chunks_indexed") or 0)
    if manifest <= 0:
        return {"ok": live > 0, "live": live, "manifest": manifest, "reason": "manifest empty"}
    ratio = live / manifest if manifest else 0.0
    ok = (1.0 - tolerance) <= ratio <= (1.0 + tolerance)
    return {
        "ok": ok,
        "live": live,
        "manifest": manifest,
        "ratio": round(ratio, 4),
        "tolerance": tolerance,
    }


def _check_domain_medicine(retriever: BooksRetriever) -> dict:
    query = "regionalna anestezija komplikacije"
    domain_candidates: list[str | None] = [
        None,
        "medicine_anesthesiology",
        "medicine_intensive_care",
        "medicine_emergency",
        "inbox_raw",
    ]
    last: dict = {"ok": False, "query": query, "n_items": 0}
    for domain in domain_candidates:
        try:
            result = retriever.search(
                query,
                k=3,
                domain=domain,
                use_rerank=False,
                use_hybrid=False,
            )
        except Exception as exc:
            return {"ok": False, "query": query, "error": str(exc)}
        items = result.get("items") or []
        last = {
            "ok": bool(result.get("ready")) and len(items) > 0,
            "query": query,
            "domain": domain,
            "n_items": len(items),
        }
        if last["ok"]:
            return last
    return last


def _check_eval(root: Path, *, limit: int) -> dict:
    import os

    eval_script = root / "40_operations" / "scripts" / "books_rag_eval.py"
    proc = subprocess.run(
        [
            sys.executable,
            str(eval_script),
            "--limit",
            str(limit),
            "--json",
        ],
        capture_output=True,
        text=True,
        cwd=str(root),
        env=os.environ.copy(),
    )
    if proc.returncode != 0:
        return {"ok": False, "reason": "eval exit non-zero", "stderr": proc.stderr[-500:]}
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "reason": "eval output not json", "stdout": proc.stdout[-500:]}
    summary = report.get("summary") or {}
    errors = int(summary.get("variant_errors") or 0)
    ready = bool(summary.get("ready"))
    dense_avg = (summary.get("avg_top_score") or {}).get("dense")
    return {
        "ok": ready and errors == 0 and dense_avg is not None,
        "ready": ready,
        "variant_errors": errors,
        "avg_top_score_dense": dense_avg,
        "queries": summary.get("queries"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify books RAG index and retrieval.")
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.add_argument("--count-tolerance", type=float, default=0.02)
    parser.add_argument("--eval-limit", type=int, default=5)
    parser.add_argument(
        "--cpu-ok",
        action="store_true",
        help="Do not fail verify when GPU/CUDA is unavailable (CPU-only machines)",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    import os

    root = Path(args.root).resolve()
    cfg = load_config(root)
    retriever = BooksRetriever(cfg)

    prefer = os.environ.get("BOOKS_RAG_DEVICE", "auto")
    device_check = resolve_device(prefer)

    report = {
        "ok": True,
        "data_dir": str(cfg.data_dir),
        "chroma_path": str(cfg.chroma_path),
        "compute_device": cfg.compute_device,
        "resolved_device": device_check,
        "gpu_ok": device_check == "cuda",
        "checks": {},
    }

    report["checks"]["gpu"] = {
        "ok": device_check == "cuda",
        "device": device_check,
    }

    if not retriever.is_ready():
        report["ok"] = False
        report["checks"]["ready"] = {"ok": False, "status": retriever.status()}
    else:
        report["checks"]["ready"] = {"ok": True}
        report["checks"]["count"] = _check_count(retriever, tolerance=args.count_tolerance)
        report["checks"]["domain_medicine"] = _check_domain_medicine(retriever)
        report["checks"]["eval"] = _check_eval(root, limit=args.eval_limit)

    for name, check in report["checks"].items():
        if name == "gpu" and args.cpu_ok:
            continue
        if not check.get("ok", False):
            report["ok"] = False

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.json:
        print(text)
    else:
        print("=== BOOKS RAG VERIFY ===")
        print(text)
        print()
        print("Result:", "PASS" if report["ok"] else "FAIL")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
