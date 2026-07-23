"""Forward-hook infrastructure for residual-stream capture and steering injection."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import numpy as np

TORCH_AVAILABLE = False
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    TORCH_AVAILABLE = True
except ImportError:
    torch = None  # type: ignore[assignment,misc]


def gpu_available() -> bool:
    import sys
    from pathlib import Path

    ops = Path(__file__).resolve().parents[1] / "common"
    parent = ops.parent
    if str(parent) not in sys.path:
        sys.path.insert(0, str(parent))
    from common.gpu import is_gpu

    return is_gpu()


def default_device() -> str:
    import sys
    from pathlib import Path

    ops = Path(__file__).resolve().parents[1] / "common"
    parent = ops.parent
    if str(parent) not in sys.path:
        sys.path.insert(0, str(parent))
    from common.gpu import resolve_device

    return resolve_device(os.environ.get("MODEL_NATIVE_DEVICE", "auto"))


@dataclass
class HookConfig:
    model_name: str = "gpt2"
    layer_idx: int = -2
    max_length: int = 128
    device: str = field(default_factory=default_device)

    @classmethod
    def from_env(cls) -> HookConfig:
        return cls(
            model_name=os.environ.get("MODEL_NATIVE_HOOK_MODEL", "gpt2"),
            layer_idx=int(os.environ.get("MODEL_NATIVE_HOOK_LAYER", "-2")),
            max_length=int(os.environ.get("MODEL_NATIVE_HOOK_MAXLEN", "128")),
            device=os.environ.get("MODEL_NATIVE_DEVICE", default_device()),
        )


class ResidualHookManager:
    """Register forward hooks on a HF causal LM residual block."""

    def __init__(self, config: HookConfig | None = None) -> None:
        if not TORCH_AVAILABLE:
            raise RuntimeError(
                "torch and transformers required for residual hooks. "
                "Install: pip install torch transformers"
            )
        self.config = config or HookConfig.from_env()
        self._model: Any = None
        self._tokenizer: Any = None
        self._handles: list[Any] = []
        self._last_hidden: torch.Tensor | None = None

    @property
    def hidden_dim(self) -> int:
        self._ensure_loaded()
        return int(self._model.config.n_embd)

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        self._tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token
        self._model = AutoModelForCausalLM.from_pretrained(self.config.model_name)
        self._model.to(self.config.device)
        self._model.eval()

    def _layer_module(self) -> Any:
        self._ensure_loaded()
        blocks = self._model.transformer.h
        idx = self.config.layer_idx
        if idx < 0:
            idx = len(blocks) + idx
        return blocks[idx]

    def register_capture_hook(self) -> None:
        def hook(_module: Any, _inputs: Any, output: Any) -> None:
            hs = output[0] if isinstance(output, tuple) else output
            self._last_hidden = hs.detach()

        self._handles.append(self._layer_module().register_forward_hook(hook))

    def register_steering_hook(self, direction: np.ndarray, *, alpha: float = 0.35) -> None:
        self._ensure_loaded()
        steer = torch.tensor(direction, dtype=torch.float32, device=self.config.device)
        steer = steer / (steer.norm() + 1e-9)

        def hook(_module: Any, _inputs: Any, output: Any) -> Any:
            hs = output[0] if isinstance(output, tuple) else output
            delta = alpha * steer.view(1, 1, -1)
            modified = hs + delta
            self._last_hidden = modified.detach()
            if isinstance(output, tuple):
                return (modified,) + output[1:]
            return modified

        self._handles.append(self._layer_module().register_forward_hook(hook))

    def clear_hooks(self) -> None:
        for handle in self._handles:
            handle.remove()
        self._handles.clear()
        self._last_hidden = None

    def forward_texts(self, texts: list[str]) -> list[np.ndarray]:
        """Run forward passes; returns mean-pooled residual vector per text."""
        self._ensure_loaded()
        if not self._handles:
            self.register_capture_hook()
        vectors: list[np.ndarray] = []
        with torch.no_grad():
            for text in texts:
                inputs = self._tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=self.config.max_length,
                    padding=True,
                )
                inputs = {k: v.to(self.config.device) for k, v in inputs.items()}
                self._model(**inputs)
                if self._last_hidden is None:
                    continue
                mean_vec = self._last_hidden.mean(dim=1).cpu().numpy()[0]
                vectors.append(mean_vec.astype(np.float32))
        return vectors

    def mean_residual(self, texts: list[str]) -> np.ndarray:
        vecs = self.forward_texts(texts)
        if not vecs:
            return np.zeros(self.hidden_dim, dtype=np.float32)
        return np.mean(np.stack(vecs), axis=0).astype(np.float32)
