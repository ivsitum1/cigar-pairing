"""
Domain rubrics for self-assessment (ported from former R rubrics).
Output is always coerced to a single string for keyword / regex checks.
"""

from __future__ import annotations

import re
from typing import Any, Callable, Dict, List

Criterion = Dict[str, Any]


def _text(output: Any) -> str:
    if output is None:
        return ""
    if isinstance(output, dict):
        if "_raw" in output:
            return _text(output["_raw"])
        payload = {k: v for k, v in output.items() if not str(k).startswith("_")}
        if payload:
            if len(payload) == 1:
                only = next(iter(payload.values()))
                if isinstance(only, (str, list, tuple, dict)):
                    return _text(only)
            return " ".join(str(x) for x in payload.values())
        return ""
    if isinstance(output, str):
        return output
    if isinstance(output, (list, tuple)):
        return " ".join(str(x) for x in output)
    return str(output)


def _statistics_rubric() -> Dict[str, Criterion]:
    def assumptions_checked(txt: str) -> float:
        keywords = (
            "shapiro",
            "levene",
            "assumption",
            "normality",
            "homoscedasticity",
            "independence",
            "residual",
        )
        score = sum(1 for k in keywords if re.search(k, txt, re.I))
        return min(score / 3, 1) * 10

    def effect_size_reported(txt: str) -> float:
        has_es = bool(
            re.search(
                r"cohen|hedges|odds ratio|risk ratio|hazard ratio|eta.?squared|partial eta|r.?squared|effect size",
                txt,
                re.I,
            )
        )
        has_ci = bool(re.search(r"95%|confidence interval|CI\s*[\[\(]|\bCI\b", txt))
        return (float(has_es) + float(has_ci)) / 2 * 10

    def multiple_testing(txt: str) -> float:
        n_tests = len(
            re.findall(r"p\s*[=<]|p-value|pvalue", txt, re.I)
        )
        if n_tests <= 1:
            return 10.0
        has_correction = bool(
            re.search(r"bonferroni|holm|FDR|BH|adjusted|correction", txt, re.I)
        )
        return 10.0 if has_correction else 3.0

    def reproducibility(txt: str) -> float:
        checks = (
            bool(re.search(r"set\.seed", txt)),
            bool(re.search(r"sessionInfo|session_info", txt)),
            bool(re.search(r"library\(|require\(|::", txt)),
            bool(re.search(r"here::here|relative|getwd", txt, re.I)),
        )
        return sum(checks) / 4 * 10

    return {
        "assumptions_checked": {
            "weight": 2,
            "check": assumptions_checked,
            "feedback_low": "Missing assumption checks. Add Shapiro-Wilk/residual plots.",
            "feedback_high": "Assumptions thoroughly verified.",
        },
        "effect_size_reported": {
            "weight": 2,
            "check": effect_size_reported,
            "feedback_low": "Report effect sizes with 95% CI.",
            "feedback_high": "Effect sizes and CIs properly reported.",
        },
        "multiple_testing": {
            "weight": 1,
            "check": multiple_testing,
            "feedback_low": "Multiple comparisons detected without correction.",
            "feedback_high": "Multiple testing properly addressed.",
        },
        "reproducibility": {
            "weight": 2,
            "check": reproducibility,
            "feedback_low": "Add set.seed(), sessionInfo(), use here::here().",
            "feedback_high": "Reproducibility elements present.",
        },
    }


def _writing_rubric() -> Dict[str, Criterion]:
    def no_ai_phrases(txt: str) -> float:
        bad = (
            "delve",
            "crucial",
            "it is important to",
            "landscape",
            "realm",
            "testament",
            "leverage",
            "pivotal",
            "comprehensive study",
            "further research is needed",
            "in conclusion, this study",
        )
        hits = sum(1 for p in bad if re.search(re.escape(p), txt, re.I))
        if hits == 0:
            return 10.0
        return max(0.0, 10 - hits * 2)

    def numbers_consistent(txt: str) -> float:
        has_flow = bool(
            re.search(r"flow|diagram|CONSORT|STROBE|enrolled|analyzed", txt, re.I)
        )
        has_nums = bool(
            re.search(r"\d+\s*(participants|patients|enrolled|completed)", txt, re.I)
        )
        return (float(has_flow) + float(has_nums)) / 2 * 10

    def reporting_guideline(txt: str) -> float:
        has_guideline = bool(
            re.search(
                r"CONSORT|STROBE|PRISMA|STARD|TRIPOD|CARE|SPIRIT|checklist",
                txt,
                re.I,
            )
        )
        return 10.0 if has_guideline else 5.0

    def readability(txt: str) -> float:
        words = re.split(r"\s+", txt.strip())
        nwords = len([w for w in words if w])
        if nwords < 50:
            return 5.0
        sentences = re.split(r"[.!?]+", txt)
        nsent = max(1, len([s for s in sentences if s.strip()]))
        avg_len = nwords / nsent
        if avg_len > 25:
            return 6.0
        if avg_len < 10:
            return 8.0
        return 10.0

    return {
        "no_ai_phrases": {
            "weight": 2,
            "check": no_ai_phrases,
            "feedback_low": "Reduce AI-flagged phrases (see writing-avoid-ai.mdc).",
            "feedback_high": "Natural, non-AI phrasing.",
        },
        "numbers_consistent": {
            "weight": 2,
            "check": numbers_consistent,
            "feedback_low": "Reconcile numbers in flow diagram and text.",
            "feedback_high": "Numbers consistent with flow.",
        },
        "reporting_guideline": {
            "weight": 2,
            "check": reporting_guideline,
            "feedback_low": "Mention reporting guideline and checklist.",
            "feedback_high": "Reporting guideline acknowledged.",
        },
        "readability": {
            "weight": 1,
            "check": readability,
            "feedback_low": "Vary sentence length; avoid very long sentences.",
            "feedback_high": "Readable sentence structure.",
        },
    }


def _code_rubric() -> Dict[str, Criterion]:
    def no_subset_setwd(txt: str) -> float:
        bad_subset = bool(re.search(r"subset\(|df\[df\$", txt)) and not bool(
            re.search(r"#.*subset", txt)
        )
        bad_setwd = bool(re.search(r"setwd\(", txt)) and not bool(
            re.search(r"#.*setwd", txt)
        )
        score = 10.0
        if bad_subset:
            score -= 4
        if bad_setwd:
            score -= 4
        return max(0.0, score)

    def true_false(txt: str) -> float:
        has_tf = bool(re.search(r"\b[T]\b|\b[F]\b", txt))
        has_true_false = bool(re.search(r"TRUE|FALSE", txt))
        if not has_tf:
            return 10.0
        if has_true_false:
            return 7.0
        return 3.0

    def seed_and_namespace(txt: str) -> float:
        has_seed = bool(re.search(r"set\.seed", txt))
        has_namespace = bool(re.search(r"::", txt))
        return (float(has_seed) + float(has_namespace)) / 2 * 10

    def reproducibility(txt: str) -> float:
        checks = (
            bool(re.search(r"set\.seed", txt)),
            bool(re.search(r"here::here|library\(here\)", txt)),
            bool(re.search(r"sessionInfo|session_info", txt)),
        )
        return sum(checks) / 3 * 10

    return {
        "no_subset_setwd": {
            "weight": 2,
            "check": no_subset_setwd,
            "feedback_low": "Use dplyr::filter() not subset(); use here::here() not setwd().",
            "feedback_high": "No subset()/setwd(); filter/here used.",
        },
        "true_false": {
            "weight": 1,
            "check": true_false,
            "feedback_low": "Use TRUE/FALSE, not T/F.",
            "feedback_high": "TRUE/FALSE used.",
        },
        "seed_and_namespace": {
            "weight": 2,
            "check": seed_and_namespace,
            "feedback_low": "Add set.seed(); use pkg::fun() in functions.",
            "feedback_high": "Seed set; namespaced calls.",
        },
        "reproducibility": {
            "weight": 2,
            "check": reproducibility,
            "feedback_low": "Add set.seed(), here::here(), sessionInfo().",
            "feedback_high": "Reproducibility elements present.",
        },
    }


def _methodology_rubric() -> Dict[str, Criterion]:
    def primary_outcome_prespec(txt: str) -> float:
        has_primary = bool(
            re.search(r"primary outcome|primary endpoint|primary objective", txt, re.I)
        )
        has_prespec = bool(
            re.search(r"pre-specif|prespecif|a priori|protocol", txt, re.I)
        )
        return (float(has_primary) + float(has_prespec)) / 2 * 10

    def sample_size(txt: str) -> float:
        has_justification = bool(
            re.search(r"sample size|power|n\s*=|80%|90%|alpha|beta", txt, re.I)
        )
        return 10.0 if has_justification else 4.0

    def subgroup_prespec(txt: str) -> float:
        has_subgroup = bool(re.search(r"subgroup|stratified", txt, re.I))
        if not has_subgroup:
            return 10.0
        has_prespec = bool(
            re.search(r"pre-specif|prespecif|a priori|protocol|planned", txt, re.I)
        )
        return 10.0 if has_prespec else 4.0

    def bias_assessment(txt: str) -> float:
        has_bias = bool(
            re.search(
                r"bias|confounding|selection|information bias|internal validity",
                txt,
                re.I,
            )
        )
        return 10.0 if has_bias else 5.0

    return {
        "primary_outcome_prespec": {
            "weight": 2,
            "check": primary_outcome_prespec,
            "feedback_low": "Define primary outcome and pre-specify in protocol.",
            "feedback_high": "Primary outcome pre-specified.",
        },
        "sample_size": {
            "weight": 2,
            "check": sample_size,
            "feedback_low": "Justify sample size (power, precision).",
            "feedback_high": "Sample size justified.",
        },
        "subgroup_prespec": {
            "weight": 1,
            "check": subgroup_prespec,
            "feedback_low": "Pre-specify subgroup analyses in protocol.",
            "feedback_high": "Subgroup analyses pre-specified.",
        },
        "bias_assessment": {
            "weight": 2,
            "check": bias_assessment,
            "feedback_low": "Address bias and confounding.",
            "feedback_high": "Bias assessment present.",
        },
    }


DOMAIN_RUBRICS: Dict[str, Dict[str, Criterion]] = {
    "statistics": _statistics_rubric(),
    "writing": _writing_rubric(),
    "code": _code_rubric(),
    "methodology": _methodology_rubric(),
}

DOMAIN_CHOICES = tuple(DOMAIN_RUBRICS.keys())

# Pass only at perfect score; 9.x must iterate or flag for human review.
PASS_THRESHOLD = 10.0


def evaluate_rubric_domain(output: Any, domain: str) -> dict:
    """Return overall (0–10), details, pass (overall >= PASS_THRESHOLD), domain."""
    if domain not in DOMAIN_RUBRICS:
        raise ValueError(f"Unknown domain: {domain}. Expected one of {DOMAIN_CHOICES}.")
    txt = _text(output)
    rubric = DOMAIN_RUBRICS[domain]
    details: List[dict] = []
    weighted_sum = 0.0
    wsum = 0
    check_fn: Callable[[str], float]
    for _name, spec in rubric.items():
        check_fn = spec["check"]
        score = min(10, max(0, float(check_fn(txt))))
        w = int(spec["weight"])
        details.append(
            {
                "score": score,
                "weight": w,
                "feedback": spec["feedback_high"]
                if score >= 7
                else spec["feedback_low"],
            }
        )
        weighted_sum += score * w
        wsum += w
    overall = round(weighted_sum / wsum, 1) if wsum else 0.0
    return {
        "overall": overall,
        "details": details,
        "pass": overall >= PASS_THRESHOLD,
        "domain": domain,
    }
