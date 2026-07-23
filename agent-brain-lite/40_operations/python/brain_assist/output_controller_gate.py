"""Zero-tolerance output gate — composes author_claims + rubric + hygiene checks."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from brain_assist.author_claims_gate import check_text

WORKSPACE = Path(__file__).resolve().parents[3]

_PLACEHOLDER_RE = re.compile(
    r"(\[TODO\]|\[BLANK\]|\[TO_CONFIRM\]|INSERT HERE|{{[^}]+}}|<TODO>)",
    re.IGNORECASE,
)

_P_ONLY_RE = re.compile(
    r"p\s*[=<>]\s*0?\.\d+|p-value|p\s+value",
    re.IGNORECASE,
)
_CI_ES_RE = re.compile(
    r"95\s*%|confidence interval|CI\s*[\[\(]|effect size|cohen|hedges|odds ratio|mean diff",
    re.IGNORECASE,
)


@dataclass
class GateCheck:
    id: str
    layer: str
    name: str
    passed: bool
    severity: str
    message: str
    evidence: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "layer": self.layer,
            "name": self.name,
            "pass": self.passed,
            "severity": self.severity,
            "message": self.message,
            "evidence": self.evidence,
        }


@dataclass
class GateReport:
    path: str | None
    domain: str
    project_id: str | None
    tolerance: str = "zero"
    checks: list[GateCheck] = field(default_factory=list)

    @property
    def pass_all(self) -> bool:
        return all(c.passed for c in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "domain": self.domain,
            "project_id": self.project_id,
            "tolerance": self.tolerance,
            "pass": self.pass_all,
            "check_count": len(self.checks),
            "failed_count": sum(1 for c in self.checks if not c.passed),
            "checks": [c.to_dict() for c in self.checks],
        }


def _read_text(path: Path | None, text: str | None) -> str:
    if text is not None:
        return text
    if path is None:
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _check_nonempty(text: str) -> GateCheck:
    ok = bool(text and text.strip())
    return GateCheck(
        id="L1-NONEMPTY",
        layer="1",
        name="non_empty_deliverable",
        passed=ok,
        severity="high",
        message="Deliverable is empty." if not ok else "Deliverable has content.",
    )


def _check_placeholders(text: str) -> GateCheck:
    hits = _PLACEHOLDER_RE.findall(text)
    ok = len(hits) == 0
    return GateCheck(
        id="L1-PLACEHOLDER",
        layer="1",
        name="no_placeholders",
        passed=ok,
        severity="high",
        message="Placeholder or unresolved marker found." if not ok else "No placeholders.",
        evidence=", ".join(sorted(set(hits))[:5]) if hits else "",
    )


def _check_author_claims(text: str, project_id: str | None) -> list[GateCheck]:
    violations = check_text(text, project_id=project_id)
    checks: list[GateCheck] = []
    if not violations:
        checks.append(
            GateCheck(
                id="L1-AUTHOR-CLAIMS",
                layer="1",
                name="author_claims",
                passed=True,
                severity="high",
                message="No author-claims violations.",
            )
        )
        return checks
    for v in violations:
        checks.append(
            GateCheck(
                id=f"L1-CLAIM-{v.rule_id}",
                layer="1",
                name="author_claims",
                passed=False,
                severity=v.severity,
                message=v.message,
                evidence=f"{v.scope}:{v.rule_id}",
            )
        )
    return checks


def _check_domain_rubric(text: str, domain: str) -> GateCheck:
    from quality_validation.rubrics import PASS_THRESHOLD, evaluate_rubric_domain

    ev = evaluate_rubric_domain(text, domain)
    overall = float(ev.get("overall", 0))
    passed = bool(ev.get("pass")) and overall >= PASS_THRESHOLD
    details = ev.get("details", [])
    failed_dims: list[str] = []
    if isinstance(details, dict):
        failed_dims = [
            k
            for k, v in details.items()
            if isinstance(v, dict) and float(v.get("score", 0)) < PASS_THRESHOLD
        ]
    elif isinstance(details, list):
        failed_dims = [
            str(i)
            for i, v in enumerate(details)
            if isinstance(v, dict) and float(v.get("score", 0)) < PASS_THRESHOLD
        ]
    return GateCheck(
        id="L1-RUBRIC",
        layer="1",
        name=f"domain_rubric_{domain}",
        passed=passed,
        severity="high",
        message=(
            f"Rubric overall {overall:.1f} < {PASS_THRESHOLD}."
            if not passed
            else f"Rubric overall {overall:.1f} (zero-tolerance pass)."
        ),
        evidence=", ".join(failed_dims) if failed_dims else "",
    )


def _check_statistics_hygiene(text: str, domain: str) -> GateCheck | None:
    if domain != "statistics":
        return None
    has_p = bool(_P_ONLY_RE.search(text))
    has_ci_es = bool(_CI_ES_RE.search(text))
    if not has_p:
        return GateCheck(
            id="L1-STATS-P-CI",
            layer="1",
            name="p_value_with_ci_effect",
            passed=True,
            severity="high",
            message="No p-value pattern detected; CI/effect rule N/A.",
        )
    passed = has_ci_es
    return GateCheck(
        id="L1-STATS-P-CI",
        layer="1",
        name="p_value_with_ci_effect",
        passed=passed,
        severity="high",
        message=(
            "p-value reported without 95% CI or effect size pattern."
            if not passed
            else "p-value accompanied by CI/effect size pattern."
        ),
    )


def run_output_gate(
    *,
    path: Path | None = None,
    text: str | None = None,
    domain: str = "writing",
    project_id: str | None = None,
) -> GateReport:
    """Run deterministic zero-tolerance checks. Semantic layers 2–5 remain agent-side."""
    content = _read_text(path, text)
    report = GateReport(
        path=str(path) if path else None,
        domain=domain,
        project_id=project_id,
    )

    report.checks.append(_check_nonempty(content))
    if not report.checks[-1].passed:
        return report

    report.checks.append(_check_placeholders(content))
    report.checks.extend(_check_author_claims(content, project_id))
    report.checks.append(_check_domain_rubric(content, domain))

    stats_check = _check_statistics_hygiene(content, domain)
    if stats_check is not None:
        report.checks.append(stats_check)

    return report
