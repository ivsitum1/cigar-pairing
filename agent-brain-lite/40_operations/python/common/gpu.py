"""Unified GPU/CPU device resolution for compute-heavy workloads."""
from __future__ import annotations

import os
import sys


def _torch_cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except ImportError:
        return False


def resolve_device(prefer: str | None = None) -> str:
    """Return ``cuda`` or ``cpu`` based on preference and availability.

    Env ``AGENT_COMPUTE_DEVICE`` (or *prefer*): ``auto`` | ``cuda`` | ``cpu``.
    ``auto`` picks CUDA when available; explicit ``cuda`` falls back to CPU with
    a stderr warning when CUDA is unavailable.
    """
    mode = (prefer or os.environ.get("AGENT_COMPUTE_DEVICE", "auto")).strip().lower()
    if mode == "cpu":
        return "cpu"
    if mode == "cuda":
        if _torch_cuda_available():
            return "cuda"
        print(
            "[gpu] cuda requested but unavailable; falling back to cpu",
            file=sys.stderr,
            flush=True,
        )
        return "cpu"
    return "cuda" if _torch_cuda_available() else "cpu"


def is_gpu() -> bool:
    return resolve_device() == "cuda"


def log_device(context: str, *, stream=None) -> str:
    dev = resolve_device()
    line = f"[gpu] {context}: device={dev}"
    print(line, file=stream or sys.stderr, flush=True)
    return dev
