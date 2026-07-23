"""Orchestrate model-native skill transform pipeline."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .eval_protocol import run_baseline_vs_steered
from .sae_lite import fit_sae_lite

WORKSPACE = Path(__file__).resolve().parents[3]
DEFAULT_OUT = WORKSPACE / "outputs" / "model_native"


def run_pipeline(
    *,
    positive_texts: list[str],
    negative_texts: list[str],
    eval_prompts: list[str],
    sae_corpus: list[str] | None = None,
    alpha: float = 0.35,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    out_dir = output_dir or DEFAULT_OUT
    out_dir.mkdir(parents=True, exist_ok=True)

    steering, report = run_baseline_vs_steered(
        eval_prompts,
        positive_texts,
        negative_texts,
        alpha=alpha,
    )

    sae_result = None
    if sae_corpus and len(sae_corpus) >= 2:
        sae = fit_sae_lite(sae_corpus)
        sae_result = sae.to_dict()
        (out_dir / "sae_lite.json").write_text(
            json.dumps(sae_result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    payload = {
        "steering": steering.to_dict(),
        "eval": report.to_dict(),
        "sae_lite": sae_result,
        "reproducibility": {
            "seed": 42,
            "alpha": alpha,
            "embed_model_env": "MODEL_NATIVE_EMBED_MODEL",
        },
    }
    (out_dir / "pipeline_report.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return payload
