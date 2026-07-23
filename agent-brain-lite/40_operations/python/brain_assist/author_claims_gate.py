"""Deterministic author-claims gate — brain (generic epistemic) + optional project packs.

Brain rules: methodology, writing hygiene, cross-population epistemic fences.
Project rules: domain-specific patterns under 10_projects/projects/<id>/author_claims/rules.json
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[3]
PROJECTS_ROOT = WORKSPACE / "10_projects" / "projects"


@dataclass(frozen=True)
class ClaimViolation:
    rule_id: str
    category: str
    severity: str
    pattern: str
    message: str
    fix_hint: str
    scope: str = "brain"


RuleTuple = tuple[str, str, str, re.Pattern[str], str, str]

# Generic epistemic fences — NOT domain-specific clinical doctrine
_BRAIN_RULES: list[RuleTuple] = [
    (
        "CLIN-ANIMAL-PK-HUMAN",
        "clinical",
        "medium",
        re.compile(
            r"(životinj\w*|animal|in\s+vitro).{0,120}(ljudi|human|odrasl\w*|patient)",
            re.IGNORECASE | re.DOTALL,
        ),
        "Animal/in vitro PK extrapolated to humans without caveat.",
        "State model species; no human doses/parameters without human cohort.",
    ),
    (
        "CLIN-POPULATION-EXTRAPOLATION",
        "clinical",
        "medium",
        re.compile(
            r"(neonatal\w*|pediatri\w*|paediatri\w*|newborn|children).{0,120}"
            r"(odrasl\w*|adult\w*|grown)",
            re.IGNORECASE | re.DOTALL,
        ),
        "Findings from one age population extrapolated to another without caveat.",
        "Label source population; use target-population literature or mark analogy as limited.",
    ),
    (
        "METH-PROTOCOL-RESULTS",
        "methodology",
        "medium",
        re.compile(
            r"(protokol|protocol\s+publication).{0,80}(ishod|outcome|effect\s+size|p\s*[<=>])",
            re.IGNORECASE | re.DOTALL,
        ),
        "Primary outcomes reported from protocol paper.",
        "Report design from protocol; results only from results publications.",
    ),
    (
        "METH-TITLE-ONLY-CLAIM",
        "methodology",
        "medium",
        re.compile(
            r"(prema naslovu|from the title alone|title suggests).{0,60}(pokazuje|demonstrates|proves)",
            re.IGNORECASE | re.DOTALL,
        ),
        "Substantive claim inferred from title when abstract/full text unavailable.",
        "Verify full text; title alone is not evidence for formulation.",
    ),
    (
        "WRIT-SCREENING-META",
        "writing",
        "low",
        re.compile(
            r"pregledni\s+skup|screened\s+corpus|screening\s+korpus",
            re.IGNORECASE,
        ),
        "Internal screening corpus language in journal-facing prose.",
        "Use neutral source wording; distinguish review article vs review corpus.",
    ),
    (
        "WRIT-EM-DASH",
        "writing",
        "low",
        re.compile(r"—"),
        "Em dash in manuscript prose.",
        "Use comma, colon, or two sentences.",
    ),
]


def project_rules_path(project_id: str) -> Path:
    return PROJECTS_ROOT / project_id / "author_claims" / "rules.json"


def load_project_rules(project_id: str) -> list[tuple[ClaimViolation, re.Pattern[str]]]:
    """Load compiled patterns from project pack."""
    path = project_rules_path(project_id)
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list[tuple[ClaimViolation, re.Pattern[str]]] = []
    for raw in data.get("rules") or []:
        rid = raw.get("rule_id", "PROJECT-UNKNOWN")
        cat = raw.get("category", "clinical")
        sev = raw.get("severity", "medium")
        pat = re.compile(raw["pattern"], re.IGNORECASE | re.DOTALL)
        meta = ClaimViolation(
            rule_id=rid,
            category=cat,
            severity=sev,
            pattern=raw["pattern"][:80],
            message=raw.get("message", ""),
            fix_hint=raw.get("fix_hint", ""),
            scope=f"project:{project_id}",
        )
        out.append((meta, pat))
    return out


def _active_brain_rules(categories: list[str] | None) -> list[tuple[ClaimViolation, re.Pattern[str]]]:
    allowed = set(categories) if categories else None
    out: list[tuple[ClaimViolation, re.Pattern[str]]] = []
    for rule_id, cat, sev, pattern, msg, fix in _BRAIN_RULES:
        if allowed is not None and cat not in allowed:
            continue
        meta = ClaimViolation(
            rule_id=rule_id,
            category=cat,
            severity=sev,
            pattern=pattern.pattern[:80],
            message=msg,
            fix_hint=fix,
            scope="brain",
        )
        out.append((meta, pattern))
    return out


def check_text(
    text: str,
    *,
    categories: list[str] | None = None,
    project_id: str | None = None,
) -> list[ClaimViolation]:
    """Return violations from brain rules and optional project pack."""
    if not text or not text.strip():
        return []
    hits: list[ClaimViolation] = []
    rulesets: list[tuple[ClaimViolation, re.Pattern[str]]] = list(_active_brain_rules(categories))
    if project_id:
        rulesets.extend(load_project_rules(project_id))
    for meta, pattern in rulesets:
        if categories is not None and meta.category not in categories:
            continue
        if pattern.search(text):
            hits.append(meta)
    return hits


def check_file(
    path: Path,
    *,
    categories: list[str] | None = None,
    project_id: str | None = None,
) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    violations = check_text(text, categories=categories, project_id=project_id)
    return {
        "path": str(path),
        "project_id": project_id,
        "pass": len(violations) == 0,
        "violation_count": len(violations),
        "violations": [v.__dict__ for v in violations],
    }


def gate_before_retry(
    text: str,
    *,
    block_severity: str = "high",
    project_id: str | None = None,
) -> dict:
    violations = check_text(text, project_id=project_id)
    blocking = [v for v in violations if v.severity == block_severity]
    return {
        "allow_retry": len(blocking) == 0,
        "blocking_count": len(blocking),
        "project_id": project_id,
        "violations": [v.__dict__ for v in violations],
    }


def list_project_packs() -> list[str]:
    if not PROJECTS_ROOT.is_dir():
        return []
    ids: list[str] = []
    for d in PROJECTS_ROOT.iterdir():
        if d.is_dir() and not d.name.startswith("_"):
            if (d / "author_claims" / "rules.json").is_file():
                ids.append(d.name)
    return sorted(ids)
