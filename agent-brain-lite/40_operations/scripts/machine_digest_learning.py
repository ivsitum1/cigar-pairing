#!/usr/bin/env python3
"""Ingest machine digest proposal decisions into learning ledger."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
TASK_DIR = WORKSPACE / ".agent" / "task"
LEDGER = WORKSPACE / ".agent" / "memory" / "digest_proposal_ledger.jsonl"
PLAYBOOK_DIR = TASK_DIR / "playbooks"

ACCEPT_VERDICTS = {"accept", "accepted", "approve", "approved", "implement", "implemented"}


def _slug(text: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in str(text).lower()).strip("-") or "proposal"


def emit_playbooks(data: dict, *, implemented: bool) -> list[str]:
    """Write a Dreaming-style plain-text playbook per accepted proposal.

    Mirrors Anthropic's 2026 "Dreaming" pattern: turn what was learned into a
    reusable trigger -> action -> verification note, not just a ledger row.
    Only accepted proposals become playbooks; rejected/deferred stay in the
    ledger only.
    """
    week = data.get("week", "unknown")
    written: list[str] = []
    for item in data.get("decisions", []):
        verdict = str(item.get("verdict", "")).lower()
        if verdict not in ACCEPT_VERDICTS:
            continue
        pid = item.get("proposal_id", "proposal")
        note = (item.get("note") or "").strip() or "(no note recorded)"
        PLAYBOOK_DIR.mkdir(parents=True, exist_ok=True)
        path = PLAYBOOK_DIR / f"{week}_{_slug(pid)}.md"
        path.write_text(
            f"# Playbook: {pid}\n\n"
            f"Source: machine digest {week} · verdict: {verdict} · "
            f"implemented: {str(implemented).lower()}\n"
            f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n"
            f"## Trigger\n"
            f"When a situation matching this proposal recurs "
            f"(repo: {item.get('repo', 'agent-rules')}).\n\n"
            f"## Action\n{note}\n\n"
            f"## Verification\n"
            f"- `python -m pytest 40_operations/tests -q` stays green\n"
            f"- Change is minimal and scoped to the accepted proposal\n",
            encoding="utf-8",
        )
        try:
            written.append(str(path.relative_to(WORKSPACE)))
        except ValueError:
            written.append(str(path))
    return written


def ingest_decisions(path: Path, *, implemented: bool = False, outcome_score: float | None = None) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with LEDGER.open("a", encoding="utf-8") as fh:
        for item in data.get("decisions", []):
            record = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "week": data.get("week"),
                "proposal_id": item.get("proposal_id"),
                "repo": item.get("repo"),
                "verdict": item.get("verdict"),
                "note": item.get("note"),
                "implemented": implemented,
                "outcome_score": outcome_score,
            }
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest machine digest decisions to learning ledger")
    parser.add_argument("--file", type=Path, help="machine_digest_decisions_YYYY-WW.json")
    parser.add_argument("--week", help="ISO week label e.g. 2026-W27")
    parser.add_argument("--implemented", action="store_true")
    parser.add_argument("--outcome-score", type=float, default=None)
    parser.add_argument(
        "--emit-playbooks",
        action="store_true",
        help="Write a Dreaming-style playbook per accepted proposal to .agent/task/playbooks/",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    path = args.file
    if path is None:
        if not args.week:
            print("ERROR: provide --file or --week", file=sys.stderr)
            return 1
        path = TASK_DIR / f"machine_digest_decisions_{args.week}.json"
    if not path.is_file():
        print(f"ERROR: not found: {path}", file=sys.stderr)
        return 1

    n = ingest_decisions(path, implemented=args.implemented, outcome_score=args.outcome_score)
    payload = {"ingested": n, "ledger": str(LEDGER.relative_to(WORKSPACE))}
    if args.emit_playbooks or args.implemented:
        data = json.loads(path.read_text(encoding="utf-8"))
        playbooks = emit_playbooks(data, implemented=args.implemented)
        payload["playbooks"] = playbooks
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Ingested {n} decisions -> {LEDGER}")
        if payload.get("playbooks"):
            print(f"Wrote {len(payload['playbooks'])} playbook(s) -> {PLAYBOOK_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
