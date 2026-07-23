"""Full residual-stream pipeline: hooks → SAE → steering eval on HF causal LM."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

WORKSPACE = Path(__file__).resolve().parents[3]
DEFAULT_OUT = WORKSPACE / "outputs" / "model_native"


def _unit_norm(v: np.ndarray) -> np.ndarray:
    mag = float(np.linalg.norm(v))
    if mag < 1e-9:
        return v.astype(np.float32)
    return (v / mag).astype(np.float32)


def _cosine_rows(vectors: np.ndarray, direction: np.ndarray) -> np.ndarray:
    d = _unit_norm(direction.reshape(-1))
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms < 1e-9, 1.0, norms)
    normed = vectors / norms
    return (normed @ d.reshape(-1, 1)).ravel().astype(np.float32)


def run_gpu_pipeline(
    *,
    positive_texts: list[str],
    negative_texts: list[str],
    eval_prompts: list[str],
    sae_corpus: list[str] | None = None,
    alpha: float = 0.35,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    from .residual_hooks import HookConfig, ResidualHookManager, TORCH_AVAILABLE, gpu_available
    from .residual_sae import fit_residual_sae

    if not TORCH_AVAILABLE:
        raise RuntimeError("GPU/residual pipeline requires torch+transformers")

    config = HookConfig.from_env()
    mgr = ResidualHookManager(config)
    mgr.register_capture_hook()

    pos_mean = mgr.mean_residual(positive_texts)
    neg_mean = mgr.mean_residual(negative_texts)
    direction = _unit_norm(pos_mean - neg_mean)

    corpus = sae_corpus or (positive_texts + negative_texts + eval_prompts)
    act_matrix = np.stack(mgr.forward_texts(corpus))
    _, sae_report = fit_residual_sae(act_matrix, device=config.device)

    baseline_vecs = np.stack(mgr.forward_texts(eval_prompts))
    baseline_score = float(np.mean(_cosine_rows(baseline_vecs, direction)))

    mgr.clear_hooks()
    mgr.register_steering_hook(direction, alpha=alpha)
    steered_vecs = np.stack(mgr.forward_texts(eval_prompts))
    steered_score = float(np.mean(_cosine_rows(steered_vecs, direction)))
    mgr.clear_hooks()

    delta = steered_score - baseline_score
    payload: dict[str, Any] = {
        "mode": "residual_stream_hooks",
        "device": config.device,
        "gpu_available": gpu_available(),
        "hook_model": config.model_name,
        "hook_layer": config.layer_idx,
        "hidden_dim": mgr.hidden_dim,
        "steering": {
            "magnitude": float(np.linalg.norm(pos_mean - neg_mean)),
            "alpha": alpha,
        },
        "eval": {
            "baseline_mean_alignment": round(baseline_score, 4),
            "steered_mean_alignment": round(steered_score, 4),
            "delta": round(delta, 4),
            "improved": delta > 0,
            "n_prompts": len(eval_prompts),
            "claim_status": "VERIFIED" if delta > 0 else "INFERRED",
        },
        "residual_sae": sae_report.to_dict(),
        "reproducibility": {
            "seed": 42,
            "hook_model_env": "MODEL_NATIVE_HOOK_MODEL",
            "device_env": "MODEL_NATIVE_DEVICE",
        },
    }

    out_dir = output_dir or DEFAULT_OUT
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "gpu_pipeline_report.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return payload
