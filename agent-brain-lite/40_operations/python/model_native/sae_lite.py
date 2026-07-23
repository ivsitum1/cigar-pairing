"""SAE-lite: NMF sparse components over embedding matrix (proxy, not residual-stream SAE)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from sklearn.decomposition import NMF

from .embedder import embed_texts


@dataclass
class SaeLiteResult:
    components: np.ndarray
    activations: np.ndarray
    n_components: int

    def to_dict(self) -> dict:
        return {
            "n_components": self.n_components,
            "components_shape": list(self.components.shape),
            "activations_shape": list(self.activations.shape),
            "note": "embedding-space NMF proxy; not trained sparse autoencoder on residual stream",
        }


def fit_sae_lite(
    texts: Sequence[str],
    *,
    n_components: int = 8,
    random_state: int = 42,
) -> SaeLiteResult:
    mat = embed_texts(texts)
    if mat.shape[0] < 2:
        raise ValueError("need at least 2 texts for SAE-lite")
    k = min(n_components, mat.shape[0], mat.shape[1])
    # NMF requires non-negative; shift embeddings to positive orthant
    shifted = mat - mat.min()
    model = NMF(n_components=k, init="nndsvda", random_state=random_state, max_iter=400)
    activations = model.fit_transform(shifted)
    return SaeLiteResult(
        components=model.components_.astype(np.float32),
        activations=activations.astype(np.float32),
        n_components=k,
    )
