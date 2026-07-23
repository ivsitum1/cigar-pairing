"""Shared TF-IDF cosine index (sklearn). Used for skill rerank and error similarity."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TfidfIndex:
    def __init__(self, ids: Sequence[str], texts: Sequence[str]) -> None:
        if len(ids) != len(texts):
            raise ValueError("ids and texts length mismatch")
        self.ids = list(ids)
        self.vectorizer = TfidfVectorizer(
            max_features=40_000,
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=1,
            strip_accents="unicode",
        )
        self.matrix = self.vectorizer.fit_transform(texts)

    def rank(self, query: str, *, top_k: int = 5, min_score: float = 0.04) -> list[tuple[str, float]]:
        if not self.ids or not query.strip():
            return []
        q = self.vectorizer.transform([query])
        sims = cosine_similarity(q, self.matrix).ravel()
        order = np.argsort(-sims)
        out: list[tuple[str, float]] = []
        for idx in order:
            score = float(sims[idx])
            if score < min_score:
                break
            out.append((self.ids[idx], score))
            if len(out) >= top_k:
                break
        return out
