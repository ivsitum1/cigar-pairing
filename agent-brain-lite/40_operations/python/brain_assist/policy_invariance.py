"""Policy invariance checks for verifier rubrics (Beyond Intelligence arXiv:2605.06161)."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class InvarianceResult:
    stable: bool
    flip_rate: float
    details: list[str]


def paraphrase_rubric(text: str) -> list[str]:
    """Generate meaning-preserving rubric variants for invariance test."""
    variants = [text.strip()]
    v2 = re.sub(r"\bmust\b", "shall", text, flags=re.I)
    v3 = re.sub(r"\bnever\b", "must not", text, flags=re.I)
    v4 = text.replace("Do not", "Avoid").replace("do not", "avoid")
    for v in (v2, v3, v4):
        if v.strip() and v.strip() not in variants:
            variants.append(v.strip())
    return variants


def evaluate_invariance(
    verdicts: list[bool],
    *,
    max_flip_rate: float = 0.25,
) -> InvarianceResult:
    """Given boolean verdicts across paraphrased rubrics, compute flip rate."""
    if len(verdicts) < 2:
        return InvarianceResult(stable=True, flip_rate=0.0, details=["insufficient variants"])
    base = verdicts[0]
    flips = sum(1 for v in verdicts[1:] if v != base)
    rate = flips / (len(verdicts) - 1)
    return InvarianceResult(
        stable=rate <= max_flip_rate,
        flip_rate=round(rate, 4),
        details=[f"flips={flips}/{len(verdicts)-1}"],
    )
