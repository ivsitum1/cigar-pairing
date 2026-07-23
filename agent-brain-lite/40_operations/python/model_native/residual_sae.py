"""Sparse autoencoder on residual-stream activations (PyTorch)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .residual_hooks import TORCH_AVAILABLE

if TORCH_AVAILABLE:
    import torch
    import torch.nn as nn


@dataclass
class ResidualSaeResult:
    n_samples: int
    hidden_dim: int
    n_latents: int
    sparsity_mean: float
    recon_mse: float
    device: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "n_samples": self.n_samples,
            "hidden_dim": self.hidden_dim,
            "n_latents": self.n_latents,
            "sparsity_mean": round(self.sparsity_mean, 4),
            "recon_mse": round(self.recon_mse, 6),
            "device": self.device,
            "note": "trained SAE on residual stream (not NMF embedding proxy)",
        }


if TORCH_AVAILABLE:

    class SparseAutoencoder(nn.Module):
        def __init__(self, hidden_dim: int, n_latents: int) -> None:
            super().__init__()
            self.encoder = nn.Linear(hidden_dim, n_latents, bias=True)
            self.decoder = nn.Linear(n_latents, hidden_dim, bias=True)

        def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
            z = torch.relu(self.encoder(x))
            recon = self.decoder(z)
            return z, recon

    def fit_residual_sae(
        activations: np.ndarray,
        *,
        n_latents: int | None = None,
        epochs: int = 80,
        lr: float = 1e-3,
        l1_coef: float = 1e-4,
        device: str | None = None,
    ) -> tuple[SparseAutoencoder, ResidualSaeResult]:
        if activations.ndim != 2 or activations.shape[0] < 2:
            raise ValueError("activations must be (n_samples, hidden_dim) with n>=2")
        dev = device or ("cuda" if torch.cuda.is_available() else "cpu")
        hidden_dim = activations.shape[1]
        latents = n_latents or max(8, hidden_dim // 8)
        model = SparseAutoencoder(hidden_dim, latents).to(dev)
        opt = torch.optim.Adam(model.parameters(), lr=lr)
        x = torch.tensor(activations, dtype=torch.float32, device=dev)

        model.train()
        for _ in range(epochs):
            opt.zero_grad()
            z, recon = model(x)
            mse = torch.mean((recon - x) ** 2)
            l1 = torch.mean(torch.abs(z))
            loss = mse + l1_coef * l1
            loss.backward()
            opt.step()
        model.eval()

        with torch.no_grad():
            z, recon = model(x)
            sparsity = float((z > 0).float().mean().cpu())
            mse = float(torch.mean((recon - x) ** 2).cpu())

        result = ResidualSaeResult(
            n_samples=int(activations.shape[0]),
            hidden_dim=hidden_dim,
            n_latents=latents,
            sparsity_mean=sparsity,
            recon_mse=mse,
            device=dev,
        )
        return model, result

else:

    def fit_residual_sae(*_args: Any, **_kwargs: Any) -> tuple[Any, ResidualSaeResult]:
        raise RuntimeError("torch required for residual SAE")
