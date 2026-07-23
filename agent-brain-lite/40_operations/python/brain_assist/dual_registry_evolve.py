"""SkillLens dual-registry evolution: verifier updates + skill REWRITE proposals."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .verifier_registry import load_verifier_registry, save_verifier_registry

WORKSPACE = Path(__file__).resolve().parents[3]
SKILLS_DIR = WORKSPACE / "30_system" / "SKILLS"
PROPOSALS_DIR = WORKSPACE / "outputs" / "skill_rewrites" / "proposals"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ts_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def propose_skill_rewrite(
    skill_id: str,
    *,
    failure_text: str,
    correction_text: str,
    gap_source: str = "trajectory",
    relation_tag: str | None = None,
) -> dict[str, Any]:
    skill_path = SKILLS_DIR / f"SKILL_{skill_id}.md"
    if not skill_path.is_file():
        raise FileNotFoundError(f"Skill file not found: {skill_path}")

    proposal_id = f"{skill_id}_{_ts_slug()}"
    amendment = (
        f"\n\n<!-- gap-amendment:{proposal_id} -->\n"
        f"## Gap-driven amendment ({_utc_now()})\n\n"
        f"**Source:** {gap_source}\n\n"
        f"**Failure context:**\n\n{failure_text.strip()[:1500]}\n\n"
        f"**Correction / target behaviour:**\n\n{correction_text.strip()[:1500]}\n\n"
    )
    if relation_tag:
        amendment += f"**Relation tag:** `{relation_tag}`\n\n"

    proposal = {
        "proposal_id": proposal_id,
        "skill_id": skill_id,
        "skill_file": str(skill_path.relative_to(WORKSPACE)).replace("\\", "/"),
        "created_at": _utc_now(),
        "status": "pending",
        "gap_source": gap_source,
        "relation_tag": relation_tag,
        "failure_text": failure_text.strip()[:2000],
        "correction_text": correction_text.strip()[:2000],
        "amendment_markdown": amendment,
    }

    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    out = PROPOSALS_DIR / f"{proposal_id}.json"
    out.write_text(json.dumps(proposal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        proposal["proposal_path"] = str(out.relative_to(WORKSPACE)).replace("\\", "/")
    except ValueError:
        proposal["proposal_path"] = str(out)
    return proposal


def apply_rewrite_proposal(proposal_path: Path, *, dry_run: bool = False) -> dict[str, Any]:
    data = json.loads(proposal_path.read_text(encoding="utf-8"))
    if data.get("status") == "applied":
        return {"ok": False, "reason": "already_applied", "proposal_id": data.get("proposal_id")}

    skill_file = WORKSPACE / data["skill_file"]
    amendment = data.get("amendment_markdown", "")
    if not skill_file.is_file():
        raise FileNotFoundError(skill_file)

    marker = f"gap-amendment:{data.get('proposal_id')}"
    existing = skill_file.read_text(encoding="utf-8")
    if marker in existing:
        return {"ok": False, "reason": "amendment_already_in_skill", "proposal_id": data.get("proposal_id")}

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "proposal_id": data.get("proposal_id"),
            "would_append_chars": len(amendment),
        }

    skill_file.write_text(existing.rstrip() + amendment, encoding="utf-8")
    data["status"] = "applied"
    data["applied_at"] = _utc_now()
    proposal_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "proposal_id": data.get("proposal_id"), "skill_file": data["skill_file"]}


def _relation_override_exists(registry: dict[str, Any], relation_tag: str, skill_id: str) -> bool:
    for row in registry.get("relation_overrides") or []:
        if row.get("relation_tag") == relation_tag and skill_id in (row.get("boost_skill_ids") or []):
            return True
    return False


def evolve_verifier_from_gap(
    registry: dict[str, Any],
    *,
    skill_id: str,
    gap_type: str,
    relation_tag: str | None = None,
    usage_ledger_path: Path | None = None,
    skip_gate: bool = False,
) -> dict[str, Any]:
    """Tighten verifier thresholds after a gap; log evolution."""
    try:
        from .verifier_usage_ledger import count_gap_occurrences, count_relation_tag, ledger_path

        ledger = usage_ledger_path or ledger_path()
        repeat_gap = count_gap_occurrences(skill_id=skill_id, gap_type=gap_type, path=ledger) >= 2
        repeat_rel = bool(relation_tag and count_relation_tag(relation_tag, path=ledger) >= 2)
    except Exception:
        repeat_gap = False
        repeat_rel = False

    auto_signal = repeat_gap or repeat_rel or os.environ.get("VERIFIER_ML_BLEND", "").strip() in {
        "1",
        "true",
        "TRUE",
    }
    if auto_signal and gap_type != "user_correction" and not skip_gate:
        try:
            from .verifier_ml import evolution_gate_passes

            passes, blockers = evolution_gate_passes(skill_id=skill_id)
            if not passes:
                log = list(registry.get("evolution_log") or [])
                log.append(
                    {
                        "ts": _utc_now(),
                        "skill_id": skill_id,
                        "gap_type": gap_type,
                        "relation_tag": relation_tag,
                        "source": "usage_ledger_blocked",
                        "gate_blockers": blockers,
                    }
                )
                registry["evolution_log"] = log[-100:]
                return registry
        except Exception:
            pass

    policies = {p["skill_id"]: p for p in registry.get("skill_policies") or [] if p.get("skill_id")}
    policy = policies.get(skill_id, {"skill_id": skill_id})
    accept = float(policy.get("accept_score", registry.get("defaults", {}).get("accept_score", 0.12)))
    delta = 0.02 if repeat_gap else 0.01
    policy["accept_score"] = round(max(0.06, accept - delta), 4)
    policy["rewrite_on_gap"] = True
    if repeat_gap and gap_type in {"user_correction", "tool_failure"}:
        policy["force_action"] = "ACCEPT"
    policies[skill_id] = policy
    registry["skill_policies"] = list(policies.values())

    if repeat_rel and relation_tag and not _relation_override_exists(registry, relation_tag, skill_id):
        overrides = list(registry.get("relation_overrides") or [])
        found = False
        for row in overrides:
            if row.get("relation_tag") == relation_tag:
                boosts = list(row.get("boost_skill_ids") or [])
                if skill_id not in boosts:
                    boosts.append(skill_id)
                row["boost_skill_ids"] = boosts
                row["score_bonus"] = float(row.get("score_bonus", 0.03)) + 0.01
                found = True
                break
        if not found:
            overrides.append(
                {
                    "relation_tag": relation_tag,
                    "boost_skill_ids": [skill_id],
                    "score_bonus": 0.04,
                    "source": "usage_ledger",
                }
            )
        registry["relation_overrides"] = overrides

    pending = list(registry.get("pending_rewrites") or [])
    pending.append(
        {
            "skill_id": skill_id,
            "status": "pending",
            "created_at": _utc_now(),
            "gap_type": gap_type,
            "relation_tag": relation_tag,
        }
    )
    registry["pending_rewrites"] = pending[-50:]

    log = list(registry.get("evolution_log") or [])
    log.append(
        {
            "ts": _utc_now(),
            "skill_id": skill_id,
            "gap_type": gap_type,
            "relation_tag": relation_tag,
            "accept_score_after": policy["accept_score"],
            "source": "usage_ledger" if (repeat_gap or repeat_rel) else "gap_report",
            "repeat_gap": repeat_gap,
            "repeat_relation": repeat_rel,
        }
    )
    registry["evolution_log"] = log[-100:]
    return registry


def process_gap_report(
    report: dict[str, Any],
    *,
    propose_rewrite: bool = True,
    evolve_verifier: bool = True,
    verifier_path: Path | None = None,
) -> dict[str, Any]:
    suggested = report.get("suggested_case") or {}
    skill_id = report.get("skill_id") or suggested.get("skill_id")
    if not skill_id:
        gaps = report.get("gaps") or []
        skill_id = "notebooklm-research-gate" if gaps else None
    if not skill_id:
        return {"ok": False, "error": "no_skill_id"}

    failure = suggested.get("failure_text") or json.dumps(report.get("gaps") or [])[:2000]
    correction = suggested.get("correction_text") or "Apply corrected procedure per user feedback."
    gap_type = (report.get("gaps") or [{}])[-1].get("gap_type", "tool_failure") if report.get("gaps") else "unknown"
    relation_tag = report.get("relation_tag")

    result: dict[str, Any] = {"ok": True, "skill_id": skill_id}

    if evolve_verifier:
        reg = load_verifier_registry(verifier_path)
        reg = evolve_verifier_from_gap(reg, skill_id=skill_id, gap_type=gap_type, relation_tag=relation_tag)
        save_verifier_registry(reg, verifier_path)
        result["verifier_updated"] = True

    if propose_rewrite:
        proposal = propose_skill_rewrite(
            skill_id,
            failure_text=failure,
            correction_text=correction,
            gap_source=report.get("trace_path", "gap_report"),
            relation_tag=relation_tag,
        )
        result["rewrite_proposal"] = proposal

    return result
