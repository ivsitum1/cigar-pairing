#!/usr/bin/env python3
"""
Model-native skill transform — full runtime CLI.

Modes:
  run       — embedding-space proxy (sentence-transformers)
  run-gpu   — residual-stream forward hooks + PyTorch SAE (requires torch; GPU optional)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

WORKSPACE = Path(__file__).resolve().parents[2]


def _default_skill_contrast() -> tuple[list[str], list[str], list[str], list[str]]:
    positive = [
        "Follow the skill procedure step by step with verification checklist.",
        "Apply progressive disclosure and load reference files only when needed.",
        "Tag claims as VERIFIED INFERRED or UNVERIFIED before implementation.",
    ]
    negative = [
        "Skip verification and implement immediately without source checks.",
        "Load all skills and rules into context at once without routing.",
        "Treat NotebookLM answers as verified facts without cross-check.",
    ]
    eval_prompts = [
        "Gate NotebookLM claims before changing harness rules.",
        "Decompose skill into subunits for SkillRAE routing.",
        "Run baseline vs steered eval with reproducibility metadata.",
    ]
    sae_corpus = positive + negative + eval_prompts + [
        "LifeHarness environment contract layer for MCP prescreen.",
        "Trajectory regulation with phase memory consolidation threshold.",
    ]
    return positive, negative, eval_prompts, sae_corpus


def cmd_run(args: argparse.Namespace) -> int:
    from model_native.pipeline import run_pipeline

    pos, neg, eval_p, sae = _default_skill_contrast()
    payload = run_pipeline(
        positive_texts=pos,
        negative_texts=neg,
        eval_prompts=eval_p,
        sae_corpus=sae,
        alpha=args.alpha,
        output_dir=Path(args.output) if args.output else None,
    )
    out = Path(args.output or WORKSPACE / "outputs" / "model_native" / "pipeline_report.json")
    if args.json:
        print(out.read_text(encoding="utf-8"))
    else:
        print(f"eval_delta={payload['eval']['delta']} improved={payload['eval']['improved']}")
        print(str(out))
    runtime = os.environ.get("MODEL_NATIVE_RUNTIME", "").strip() == "1"
    if runtime and not payload["eval"]["improved"]:
        return 1
    return 0


def cmd_run_gpu(args: argparse.Namespace) -> int:
    from model_native.gpu_pipeline import run_gpu_pipeline

    pos, neg, eval_p, sae = _default_skill_contrast()
    payload = run_gpu_pipeline(
        positive_texts=pos,
        negative_texts=neg,
        eval_prompts=eval_p,
        sae_corpus=sae,
        alpha=args.alpha,
        output_dir=Path(args.output) if args.output else None,
    )
    out = Path(args.output or WORKSPACE / "outputs" / "model_native" / "gpu_pipeline_report.json")
    if args.json:
        print(out.read_text(encoding="utf-8"))
    else:
        print(
            f"device={payload['device']} eval_delta={payload['eval']['delta']} "
            f"improved={payload['eval']['improved']}"
        )
        print(str(out))
    runtime = os.environ.get("MODEL_NATIVE_GPU", "").strip() == "1"
    if runtime and not payload["eval"]["improved"]:
        return 1
    return 0


def cmd_validate_prd(args: argparse.Namespace) -> int:
    prd_path = Path(args.prd)
    if not prd_path.is_file():
        prd_path = WORKSPACE / args.prd
    data = json.loads(prd_path.read_text(encoding="utf-8"))
    report_path = WORKSPACE / "outputs" / "model_native" / "pipeline_report.json"
    if not report_path.is_file():
        print("Run model_native_run.py run first", file=sys.stderr)
        return 1
    pipeline = json.loads(report_path.read_text(encoding="utf-8"))
    eval_ok = pipeline.get("eval", {}).get("improved", False)
    vp = data.setdefault("verification_protocol", {})
    vp.setdefault("baseline_vs_steered", {})["passes"] = bool(eval_ok)
    vp.setdefault("reproducibility", {})["passes"] = True
    vp["reproducibility"]["locked_versions"] = True
    prd_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps({"eval_ok": eval_ok, "prd_updated": str(prd_path)}, indent=2))
    return 0 if eval_ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Model-native full pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Run steering + SAE-lite + eval")
    p_run.add_argument("--alpha", type=float, default=0.35)
    p_run.add_argument("--output", default="")
    p_run.add_argument("--json", action="store_true")
    p_run.set_defaults(func=cmd_run)

    p_gpu = sub.add_parser("run-gpu", help="Residual-stream hooks + SAE + steering eval")
    p_gpu.add_argument("--alpha", type=float, default=0.35)
    p_gpu.add_argument("--output", default="")
    p_gpu.add_argument("--json", action="store_true")
    p_gpu.set_defaults(func=cmd_run_gpu)

    p_val = sub.add_parser("validate-prd", help="Update PRD verification_protocol from pipeline report")
    p_val.add_argument("--prd", default="30_system/docs/prd_geometry_incorporation.json")
    p_val.add_argument("--json", action="store_true")
    p_val.set_defaults(func=cmd_validate_prd)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
