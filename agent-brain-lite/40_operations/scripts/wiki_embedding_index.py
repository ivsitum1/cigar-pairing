#!/usr/bin/env python3
"""TF-IDF embedding index for wiki semantic neighbor linking (no API, sklearn only)."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

YAML_DESC = re.compile(r"^description:\s*>?-\s*\n((?:\s+.+\n)+)|^description:\s*(.+)$", re.M)
TOKEN_RE = re.compile(r"[a-z0-9]{3,}", re.I)


def _extract_yaml_description(text: str) -> str:
    m = YAML_DESC.search(text)
    if not m:
        return ""
    if m.group(1):
        return " ".join(line.strip() for line in m.group(1).splitlines())
    return (m.group(2) or "").strip()


def _doc_text(path: Path, max_chars: int = 6000) -> str:
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end > 0:
            front = raw[3:end]
            body = raw[end + 4 :]
            return f"{front}\n{body[:max_chars]}"
    return raw[:max_chars]


def _wikilink_title(path: Path) -> str:
    return path.stem


def build_embedding_corpus(
    root: Path,
    *,
    max_entities: int = 900,
    max_analysis: int = 400,
) -> list[tuple[str, str, str]]:
    """Return list of (rel_posix, wikilink_title, document_text)."""
    docs: list[tuple[str, str, str]] = []

    def add_file(path: Path) -> None:
        rel = path.relative_to(root).as_posix()
        text = _doc_text(path)
        if len(text.strip()) < 40:
            return
        title = _wikilink_title(path)
        docs.append((rel, title, f"{title} {rel} {text}"))

    concepts = root / "20_knowledge/wiki/concepts"
    if concepts.is_dir():
        for p in sorted(concepts.glob("*.md")):
            add_file(p)

    entities = root / "20_knowledge/wiki/entities"
    if entities.is_dir():
        for p in sorted(entities.glob("*.md"))[:max_entities]:
            add_file(p)

    analysis = root / "20_knowledge/wiki/analysis"
    if analysis.is_dir():
        for p in sorted(analysis.glob("*.md"))[:max_analysis]:
            add_file(p)

    skills = root / "30_system/SKILLS"
    if skills.is_dir():
        for p in sorted(skills.glob("SKILL_*.md")):
            add_file(p)
        ref_root = skills / "reference"
        if ref_root.is_dir():
            for p in sorted(ref_root.rglob("*.md")):
                add_file(p)

    for rel in (
        "20_knowledge/wiki/index.md",
        "30_system/docs/indexes/SKILLS_INDEX.md",
        "30_system/docs/FOLDER_INDEX.md",
        "30_system/docs/GRAPH_CONNECTIVITY_MAP.md",
        "30_system/SKILLS/reference/REFERENCE_INDEX.md",
    ):
        p = root / rel
        if p.is_file():
            add_file(p)

    beh = root / "30_system/behavior_rules"
    if beh.is_dir():
        for p in sorted(beh.glob("*.md")):
            if p.name.startswith("CHANGELOG"):
                continue
            add_file(p)

    # Deduplicate by rel
    seen: set[str] = set()
    out: list[tuple[str, str, str]] = []
    for rel, title, text in docs:
        if rel in seen:
            continue
        seen.add(rel)
        out.append((rel, title, text))
    return out


class TfidfEmbeddingIndex:
    def __init__(self, corpus: list[tuple[str, str, str]]) -> None:
        self.rel_paths = [c[0] for c in corpus]
        self.titles = [c[1] for c in corpus]
        self._title_to_rel = {t: r for r, t, _ in corpus}
        texts = [c[2] for c in corpus]
        self.vectorizer = TfidfVectorizer(
            max_features=80_000,
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=1,
            strip_accents="unicode",
        )
        self.matrix = self.vectorizer.fit_transform(texts)

    def neighbors(
        self,
        text: str,
        *,
        top_k: int = 5,
        exclude_rel: str | None = None,
        min_score: float = 0.06,
    ) -> list[tuple[str, float]]:
        if self.matrix.shape[0] == 0:
            return []
        q = self.vectorizer.transform([text])
        sims = cosine_similarity(q, self.matrix).ravel()
        order = np.argsort(-sims)
        results: list[tuple[str, float]] = []
        for idx in order:
            score = float(sims[idx])
            if score < min_score:
                break
            rel = self.rel_paths[idx]
            if exclude_rel and rel == exclude_rel:
                continue
            results.append((self.titles[idx], score))
            if len(results) >= top_k:
                break
        return results
