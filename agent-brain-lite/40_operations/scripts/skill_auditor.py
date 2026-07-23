#!/usr/bin/env python3
"""
Local skill security auditor (SkillGuard-lite).

Usage:
  python 40_operations/scripts/skill_auditor.py --skill-id meta-analysis
  python 40_operations/scripts/skill_auditor.py --scan-all --json
  python 40_operations/scripts/skill_auditor.py --file path/to/SKILL.md
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
REGISTRY = WORKSPACE / "30_system" / "SKILLS" / "registry.json"
SKILLS_DIR = WORKSPACE / "30_system" / "SKILLS"

CRITICAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("eval_exec", re.compile(r"\b(eval|exec)\s*\(", re.I)),
    ("shell_pipe_bash", re.compile(r"curl\s+[^|]+\|\s*bash", re.I)),
    ("reverse_shell", re.compile(r"(/dev/tcp/|nc\s+-e|bash\s+-i\s+>&)", re.I)),
    ("hardcoded_secret", re.compile(r"(api[_-]?key|secret|password)\s*=\s*['\"][^'\"]{8,}", re.I)),
]

HIGH_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("env_harvest", re.compile(r"\.env\b|id_rsa|keychain|MetaMask|Exodus", re.I)),
    ("webhook_exfil", re.compile(r"https?://[^\s]*webhook", re.I)),
    ("prompt_injection", re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.I)),
    ("subprocess_shell", re.compile(r"subprocess\.(call|run|Popen)\([^)]*shell\s*=\s*True", re.I)),
]

MEDIUM_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("rm_rf", re.compile(r"rm\s+-rf\s+/")),
    ("os_system", re.compile(r"\bos\.system\s*\(")),
    ("pickle_load", re.compile(r"pickle\.loads?\s*\(")),
]

GENERIC_TRIGGERS = {
    "help",
    "task",
    "work",
    "do",
    "make",
    "create",
    "fix",
    "run",
    "use",
    "agent",
    "ai",
    "tool",
}


@dataclass
class Finding:
    severity: str
    rule_id: str
    message: str
    location: str = ""


@dataclass
class AuditResult:
    skill_id: str
    score: int
    findings: list[Finding] = field(default_factory=list)
    trust_tier: int | None = None

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "score": self.score,
            "trust_tier": self.trust_tier,
            "pass": self.score >= 70 and not any(f.severity == "critical" for f in self.findings),
            "findings": [
                {"severity": f.severity, "rule_id": f.rule_id, "message": f.message, "location": f.location}
                for f in self.findings
            ],
        }


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def skill_path(skill: dict) -> Path:
    return SKILLS_DIR / skill["file"]


def extract_code_blocks(text: str) -> list[tuple[int, str, str]]:
    """Return (line_approx, lang, code) for fenced blocks."""
    blocks: list[tuple[int, str, str]] = []
    fence = re.compile(r"^```(\w*)\n(.*?)```", re.MULTILINE | re.DOTALL)
    for match in fence.finditer(text):
        lang = match.group(1) or "text"
        code = match.group(2)
        line = text[: match.start()].count("\n") + 1
        blocks.append((line, lang, code))
    return blocks


def audit_python_ast(code: str, location: str) -> list[Finding]:
    findings: list[Finding] = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return findings
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in {"eval", "exec"}:
                findings.append(Finding("critical", "ast_eval_exec", f"AST: {func.id}()", location))
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in {"pickle", "marshal"}:
                    findings.append(
                        Finding("medium", "ast_unsafe_import", f"import {alias.name}", location)
                    )
    return findings


def scan_text(text: str, location: str) -> list[Finding]:
    findings: list[Finding] = []
    for rule_id, pattern in CRITICAL_PATTERNS:
        if pattern.search(text):
            findings.append(Finding("critical", rule_id, f"Pattern {rule_id}", location))
    for rule_id, pattern in HIGH_PATTERNS:
        if pattern.search(text):
            findings.append(Finding("high", rule_id, f"Pattern {rule_id}", location))
    for rule_id, pattern in MEDIUM_PATTERNS:
        if pattern.search(text):
            findings.append(Finding("medium", rule_id, f"Pattern {rule_id}", location))
    return findings


def audit_triggers(skill: dict) -> list[Finding]:
    findings: list[Finding] = []
    triggers = [t.lower().strip() for t in skill.get("triggers", [])]
    generic_hits = [t for t in triggers if t in GENERIC_TRIGGERS]
    if len(triggers) > 12 and len(generic_hits) >= 4:
        findings.append(
            Finding(
                "medium",
                "c_poisoning",
                f"Overbroad triggers ({len(triggers)} total, {len(generic_hits)} generic)",
                "registry.triggers",
            )
        )
    return findings


def score_findings(findings: list[Finding]) -> int:
    score = 100
    for f in findings:
        if f.severity == "critical":
            score -= 40
        elif f.severity == "high":
            score -= 20
        elif f.severity == "medium":
            score -= 10
        else:
            score -= 5
    return max(0, min(100, score))


def audit_skill(skill: dict) -> AuditResult:
    sid = skill.get("id", "unknown")
    path = skill_path(skill)
    findings: list[Finding] = []
    findings.extend(audit_triggers(skill))

    if not path.is_file():
        findings.append(Finding("critical", "missing_file", f"Skill file not found: {path}", str(path)))
        return AuditResult(sid, 0, findings, skill.get("trust_tier"))

    text = path.read_text(encoding="utf-8")
    findings.extend(scan_text(text, str(path)))

    for line_no, lang, code in extract_code_blocks(text):
        loc = f"{path}:{line_no}"
        findings.extend(scan_text(code, loc))
        if lang in {"python", "py"}:
            findings.extend(audit_python_ast(code, loc))

    # Deduplicate by rule_id+location
    seen: set[tuple[str, str]] = set()
    unique: list[Finding] = []
    for f in findings:
        key = (f.rule_id, f.location)
        if key not in seen:
            seen.add(key)
            unique.append(f)

    return AuditResult(sid, score_findings(unique), unique, skill.get("trust_tier"))


def audit_file(path: Path) -> AuditResult:
    text = path.read_text(encoding="utf-8")
    findings = scan_text(text, str(path))
    for line_no, lang, code in extract_code_blocks(text):
        loc = f"{path}:{line_no}"
        findings.extend(scan_text(code, loc))
        if lang in {"python", "py"}:
            findings.extend(audit_python_ast(code, loc))
    return AuditResult(path.stem, score_findings(findings), findings)


def main() -> int:
    parser = argparse.ArgumentParser(description="Skill security auditor")
    parser.add_argument("--skill-id", action="append", default=[])
    parser.add_argument("--scan-all", action="store_true")
    parser.add_argument("--file", type=Path)
    parser.add_argument("--min-score", type=int, default=70)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    results: list[AuditResult] = []

    if args.file:
        results.append(audit_file(args.file))
    else:
        reg = load_registry()
        skills = reg.get("skills", [])
        if args.scan_all:
            targets = skills
        elif args.skill_id:
            ids = set(args.skill_id)
            targets = [s for s in skills if s.get("id") in ids]
        else:
            print("Provide --skill-id, --scan-all, or --file", file=sys.stderr)
            return 2
        for skill in targets:
            results.append(audit_skill(skill))

    payload = {
        "results": [r.to_dict() for r in results],
        "pass": all(r.score >= args.min_score and not any(f.severity == "critical" for f in r.findings) for r in results),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for r in results:
            status = "PASS" if r.score >= args.min_score else "FAIL"
            print(f"{r.skill_id}: {status} score={r.score} findings={len(r.findings)}")
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
