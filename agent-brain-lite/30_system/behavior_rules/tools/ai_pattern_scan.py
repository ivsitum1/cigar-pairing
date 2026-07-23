#!/usr/bin/env python3
"""Local lexical/structural AI writing pattern scanner.

Sources: Wikipedia Signs of AI Writing, humanize-ai-text patterns.json,
NotebookLM grill exports (humanize_ai, humanize-predictability batch 2026-06).
Purpose: natural academic prose review — not detector evasion.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

PATTERNS_PATH = Path(__file__).with_name("ai_detection_patterns.json")

INLINE_HEADER_RE = re.compile(
    r"(?m)^\s*[-*]\s+\*\*[^*]+\*\*\s*:\s*.+$"
)
RULE_OF_THREE_RE = re.compile(
    r"\b\w+,\s+\w+,\s+and\s+\w+\b",
    re.IGNORECASE,
)


@dataclass
class CategoryHits:
    name: str
    matches: list[dict[str, Any]] = field(default_factory=list)
    weight: float = 1.0

    @property
    def count(self) -> int:
        return sum(m.get("count", 0) for m in self.matches)


SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass
class PatternScanResult:
    word_count: int
    total_hits: int
    score: float
    probability_label: str
    categories: list[CategoryHits]
    recommendations: list[str]
    structural_signals: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "word_count": self.word_count,
            "total_hits": self.total_hits,
            "score": self.score,
            "probability_label": self.probability_label,
            "structural_signals": self.structural_signals,
            "categories": [
                {
                    "name": c.name,
                    "count": c.count,
                    "matches": c.matches,
                    "weight": c.weight,
                }
                for c in self.categories
            ],
            "recommendations": self.recommendations,
        }


def _load_patterns() -> dict[str, Any]:
    return json.loads(PATTERNS_PATH.read_text(encoding="utf-8"))


def _find_phrase_matches(text: str, patterns: list[str]) -> list[dict[str, Any]]:
    lower = text.lower()
    hits: list[dict[str, Any]] = []
    for phrase in patterns:
        count = lower.count(phrase.lower())
        if count:
            hits.append({"phrase": phrase, "count": count})
    return sorted(hits, key=lambda x: -x["count"])


def _score_from_hits(
    word_count: int,
    categories: list[CategoryHits],
    critical_any: bool,
) -> tuple[float, str]:
    weighted = sum(c.count * c.weight for c in categories)
    density = weighted / max(word_count, 1) * 100
    if critical_any:
        return min(0.98, 0.75 + density * 0.02), "very_high"
    if density > 5 or weighted > 30:
        return min(0.92, 0.55 + density * 0.04), "high"
    if density > 2 or weighted > 15:
        return min(0.65, 0.35 + density * 0.05), "medium"
    if weighted > 5:
        return min(0.35, 0.15 + density * 0.03), "low"
    return max(0.05, density * 0.02), "low"


def _structural_signals(text: str) -> dict[str, Any]:
    """Heuristic predictability proxies (not true perplexity)."""
    sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]
    if len(sentences) < 2:
        return {
            "sentence_count": len(sentences),
            "length_cv": None,
            "burstiness_proxy": None,
            "passive_voice_ratio": None,
        }
    lengths = [len(s.split()) for s in sentences]
    mean_len = sum(lengths) / len(lengths)
    variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
    std_len = variance ** 0.5
    length_cv = round(std_len / mean_len, 4) if mean_len else 0.0
    alternations = 0
    for a, b in zip(lengths, lengths[1:]):
        if (a <= 12 and b >= 20) or (a >= 20 and b <= 12):
            alternations += 1
    burstiness_proxy = round(alternations / max(len(lengths) - 1, 1), 4)
    passive_hits = len(
        re.findall(
            r"\b(is|are|was|were|been|being)\s+\w+ed\b",
            text,
            flags=re.IGNORECASE,
        )
    )
    passive_ratio = round(passive_hits / len(sentences), 4)
    return {
        "sentence_count": len(sentences),
        "mean_sentence_words": round(mean_len, 2),
        "length_cv": length_cv,
        "burstiness_proxy": burstiness_proxy,
        "passive_voice_ratio": passive_ratio,
        "low_variance_flag": length_cv < 0.35,
    }


def _recommendations(
    categories: list[CategoryHits],
    score: float,
    structural: dict[str, Any],
) -> list[str]:
    recs: list[str] = []
    by_name = {c.name: c for c in categories}
    if by_name.get("citation_bugs", CategoryHits("")).count:
        recs.append("Remove chatbot citation placeholders and broken reference codes.")
    if by_name.get("knowledge_cutoff", CategoryHits("")).count:
        recs.append("Delete knowledge-cutoff disclaimers; verify facts or omit.")
    if by_name.get("chatbot_artifacts", CategoryHits("")).count:
        recs.append("Remove chatbot conversational artifacts.")
    if by_name.get("significance_inflation", CategoryHits("")).count:
        recs.append("Replace significance puffery with concrete facts and numbers.")
    if by_name.get("ai_vocabulary", CategoryHits("")).count:
        recs.append("Swap AI-flagged vocabulary (delve, tapestry, pivotal) for plain terms.")
    if by_name.get("copula_avoidance", CategoryHits("")).count:
        recs.append("Prefer simple is/are/has over serves as or boasts.")
    if by_name.get("filler_phrases", CategoryHits("")).count:
        recs.append("Shorten filler phrases (in order to → to).")
    if by_name.get("phantom_denials", CategoryHits("")).count:
        recs.append("Remove phantom denials: do not negate claims nobody made.")
    if by_name.get("syntactic_inflation", CategoryHits("")).count:
        recs.append("Trim syntactic inflation; prefer shorter direct sentences.")
    if by_name.get("pseudo_commitment", CategoryHits("")).count:
        recs.append("Replace pseudo-commitment words (central, crucial) with concrete facts.")
    if structural.get("low_variance_flag"):
        recs.append(
            "Sentence lengths are uniform (low CV); vary length — one short sentence after a long one."
        )
    elif score >= 0.5:
        recs.append("Vary sentence length (burstiness); add one short sentence after a long one.")
    if score >= 0.2:
        recs.append("Target institutional review threshold: keep pattern score under 0.20 where possible.")
    if not recs:
        recs.append("Few lexical AI patterns detected; verify structure and facts separately.")
    return recs


def scan_text(text: str, patterns: dict[str, Any] | None = None) -> PatternScanResult:
    """Scan text for AI-writing pattern categories; return structured result."""
    patterns = patterns or _load_patterns()
    word_count = len(text.split())
    categories: list[CategoryHits] = []

    def add(name: str, hits: list[dict[str, Any]], weight: float = 1.0) -> None:
        if hits:
            categories.append(CategoryHits(name=name, matches=hits, weight=weight))

    add("significance_inflation", _find_phrase_matches(text, patterns["significance_inflation"]))
    add("notability_emphasis", _find_phrase_matches(text, patterns["notability_emphasis"]))
    add("superficial_analysis", _find_phrase_matches(text, patterns["superficial_analysis"]), 0.8)
    add("promotional_language", _find_phrase_matches(text, patterns["promotional_language"]))
    add("vague_attributions", _find_phrase_matches(text, patterns["vague_attributions"]))
    add("challenges_formula", _find_phrase_matches(text, patterns["challenges_formula"]))
    add("ai_vocabulary", _find_phrase_matches(text, patterns["ai_vocabulary"]))
    add(
        "copula_avoidance",
        _find_phrase_matches(text, list(patterns["copula_avoidance"].keys())),
    )
    add(
        "filler_phrases",
        _find_phrase_matches(text, list(patterns["filler_replacements"].keys())),
    )
    add("chatbot_artifacts", _find_phrase_matches(text, patterns["chatbot_artifacts"]), 3.0)
    add("hedging_phrases", _find_phrase_matches(text, patterns["hedging_phrases"]), 0.5)
    add("negative_parallelisms", _find_phrase_matches(text, patterns["negative_parallelisms"]))
    add("phantom_denials", _find_phrase_matches(text, patterns["phantom_denials"]), 1.8)
    add("syntactic_inflation", _find_phrase_matches(text, patterns["syntactic_inflation"]), 1.2)
    add("pseudo_commitment", _find_phrase_matches(text, patterns["pseudo_commitment"]), 1.3)
    add("rule_of_three", _find_phrase_matches(text, patterns["rule_of_three_patterns"]))
    add("markdown_artifacts", _find_phrase_matches(text, patterns["markdown_artifacts"]), 2.0)
    add("citation_bugs", _find_phrase_matches(text, patterns["citation_bugs"]), 5.0)
    add("knowledge_cutoff", _find_phrase_matches(text, patterns["knowledge_cutoff"]), 3.0)

    inline_headers = INLINE_HEADER_RE.findall(text)
    if inline_headers:
        add(
            "inline_header_lists",
            [{"phrase": h[:80], "count": 1} for h in inline_headers[:10]],
            1.5,
        )

    rot_matches = RULE_OF_THREE_RE.findall(text)
    if rot_matches:
        add(
            "rule_of_three_regex",
            [{"phrase": m, "count": 1} for m in rot_matches[:10]],
            1.2,
        )

    em_count = text.count("\u2014") + text.count(" -- ")
    if em_count > 3:
        add("em_dash_overuse", [{"phrase": "em dash", "count": em_count}], 0.5)

    critical = any(
        c.name in {"citation_bugs", "knowledge_cutoff", "chatbot_artifacts"}
        for c in categories
    )
    total_hits = sum(c.count for c in categories)
    score, label = _score_from_hits(word_count, categories, critical)
    structural = _structural_signals(text)
    recs = _recommendations(categories, score, structural)

    return PatternScanResult(
        word_count=word_count,
        total_hits=total_hits,
        score=round(score, 4),
        probability_label=label,
        categories=categories,
        recommendations=recs,
        structural_signals=structural,
    )


def pattern_score(text: str) -> float:
    """Return 0-1 AI pattern probability for integration with check_ai_score_only."""
    if len(text) < 50:
        return 0.0
    return scan_text(text).score


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Scan text for AI writing patterns")
    parser.add_argument("file", nargs="?", help="Text file path (or stdin)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()
    content = (
        Path(args.file).read_text(encoding="utf-8")
        if args.file
        else sys.stdin.read()
    )
    result = scan_text(content)
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"Score: {result.score:.2%} ({result.probability_label})")
        print(f"Hits: {result.total_hits} in {result.word_count} words")
        for line in result.recommendations:
            print(f"  - {line}")
