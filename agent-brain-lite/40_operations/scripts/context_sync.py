#!/usr/bin/env python3
"""Sync context: append log/commit, trim MEMORY.md and log.md. Run from project root."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

AGENT_RULES = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = AGENT_RULES.parent if (AGENT_RULES.parent / "01_input").exists() else AGENT_RULES
AGENT = PROJECT_ROOT / ".agent"
_HARNESS_PY = AGENT_RULES / "40_operations" / "python"
if str(_HARNESS_PY) not in sys.path:
    sys.path.insert(0, str(_HARNESS_PY))
CONTEXT = PROJECT_ROOT / "30_system/04_documentation" / "context"
MEMORY = AGENT / "MEMORY.md"
SOLVED_LEMMAS = AGENT / "solved_lemmas.jsonl"
LOG = CONTEXT / "log.md"
COMMIT = CONTEXT / "commit.md"
HANDOFF_LOG = AGENT / "handoff_log.jsonl"
ERROR_LOG = PROJECT_ROOT / ".cursor" / "errors" / "error_log.jsonl"

MEMORY_MAX = 200
LOG_MAX = 100


def read_tail(path: Path, n: int) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").strip().split("\n")
    return [l for l in lines if l.strip() and not l.startswith("#")][-n:]


def append_log(msg: str, prefix: str = "A") -> None:
    CONTEXT.mkdir(parents=True, exist_ok=True)
    if prefix.upper() not in ("O", "T", "A"):
        prefix = "A"
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] [{prefix.upper()}] {msg}\n"
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line)


def update_commit(phase: str = "", completed: str = "", next_items: str = "") -> None:
    CONTEXT.mkdir(parents=True, exist_ok=True)
    content = "# commit.md – Milestones (per branch/phase)\n\n"
    content += "**Purpose:** What is \"done\" in this phase. Updated at milestone boundaries.\n\n---\n\n"
    content += f"- **Phase:** {phase or '(not set)'}\n"
    content += f"- **Completed:** {completed or '(none)'}\n"
    content += f"- **Next:** {next_items or '(none)'}\n\n---\n"
    COMMIT.write_text(content, encoding="utf-8")


def trim_memory() -> None:
    if not MEMORY.exists():
        return
    lines = MEMORY.read_text(encoding="utf-8").split("\n")
    header = []
    body = []
    in_header = True
    for line in lines:
        if in_header and (line.startswith("---") or line.startswith("#") or not line.strip()):
            header.append(line)
            if line.strip() == "---" and len(header) > 1:
                in_header = False
        elif in_header:
            header.append(line)
        else:
            body.append(line)
    # Keep header + last MEMORY_MAX body lines
    if len(body) > MEMORY_MAX:
        body = body[-MEMORY_MAX:]
    MEMORY.write_text("\n".join(header + body) + "\n", encoding="utf-8")


def trim_log() -> None:
    if not LOG.exists():
        return
    lines = LOG.read_text(encoding="utf-8").split("\n")
    header = []
    body = []
    in_header = True
    for line in lines:
        if in_header and (line.startswith("---") or line.startswith("#") or line.startswith("##")):
            header.append(line)
            if line.strip() == "---" and len(header) > 1:
                in_header = False
        elif in_header:
            header.append(line)
        else:
            if line.strip():
                body.append(line)
    if len(body) > LOG_MAX:
        body = body[-LOG_MAX:]
    LOG.write_text("\n".join(header + body) + "\n" if body else "\n".join(header) + "\n", encoding="utf-8")


def fold_lemma(subgoal: str, summary: str, *, provenance: str = "") -> None:
    """HIP-If information folding: store compact solved lemma; trim verbose log tail."""
    AGENT.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "subgoal": subgoal[:500],
        "summary": summary[:2000],
        "provenance": provenance[:300],
    }
    with open(SOLVED_LEMMAS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    line_no = sum(
        1
        for ln in SOLVED_LEMMAS.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    )
    try:
        from harness.memory_hierarchy import add_lemma_node

        add_lemma_node(
            subgoal=subgoal,
            summary=summary,
            provenance=provenance,
            solved_lemmas_line=line_no,
        )
    except ImportError:
        pass
    append_log(f"Folded lemma: {subgoal[:80]}", "A")
    trim_log()


def sync_memory_hierarchy() -> int:
    """Sync .agent/solved_lemmas.jsonl into memory_hierarchy/index.json."""
    try:
        from harness.memory_hierarchy import sync_from_solved_lemmas

        return sync_from_solved_lemmas(SOLVED_LEMMAS)
    except ImportError:
        return 0


def summary() -> dict:
    out = {
        "memory_lines": len(read_tail(MEMORY, 9999)) if MEMORY.exists() else 0,
        "log_lines": len(read_tail(LOG, 9999)) if LOG.exists() else 0,
        "handoff_count": 0,
        "error_count": 0,
        "solved_lemmas": 0,
        "has_main": (CONTEXT / "main.md").exists(),
        "has_commit": COMMIT.exists(),
    }
    if HANDOFF_LOG.exists():
        out["handoff_count"] = sum(
            1
            for _ in HANDOFF_LOG.read_text(encoding="utf-8", errors="replace").strip().split("\n")
            if _.strip()
        )
    if ERROR_LOG.exists():
        out["error_count"] = sum(
            1
            for _ in ERROR_LOG.read_text(encoding="utf-8", errors="replace").strip().split("\n")
            if _.strip()
        )
    if SOLVED_LEMMAS.exists():
        out["solved_lemmas"] = sum(
            1
            for _ in SOLVED_LEMMAS.read_text(encoding="utf-8", errors="replace").strip().split("\n")
            if _.strip()
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Context sync and trim")
    parser.add_argument("--append-log", "-l", metavar="MSG", help="Append to log.md [O|T|A] MSG")
    parser.add_argument("--log-prefix", choices=["O", "T", "A"], default="A", help="O=Observation T=Thought A=Action")
    parser.add_argument("--update-commit", action="store_true", help="Update commit.md from --phase, --completed, --next")
    parser.add_argument("--phase", default="", help="Phase name for commit.md")
    parser.add_argument("--completed", default="", help="Completed items for commit.md")
    parser.add_argument("--next", dest="next_items", default="", help="Next items for commit.md")
    parser.add_argument("--trim", "-t", action="store_true", help="Trim MEMORY.md and log.md")
    parser.add_argument("--fold-lemma", metavar="SUBGOAL", help="Store solved lemma (HIP-If fold) and trim log")
    parser.add_argument("--lemma-summary", default="", help="Summary text for --fold-lemma")
    parser.add_argument("--lemma-provenance", default="", help="Optional path/ref for lemma provenance")
    parser.add_argument(
        "--sync-memory-hierarchy",
        action="store_true",
        help="Bootstrap .agent/memory_hierarchy/ from solved_lemmas.jsonl",
    )
    parser.add_argument("--summary", "-s", action="store_true", help="Print summary only")
    args = parser.parse_args()

    if args.append_log:
        append_log(args.append_log, args.log_prefix)
        print(f"Appended to {LOG}")

    if args.update_commit:
        update_commit(args.phase, args.completed, args.next_items)
        print(f"Updated {COMMIT}")

    if args.trim:
        trim_memory()
        trim_log()
        print("Trimmed MEMORY.md and log.md")

    if args.fold_lemma:
        if not args.lemma_summary:
            print("--lemma-summary required with --fold-lemma", file=sys.stderr)
            sys.exit(1)
        fold_lemma(args.fold_lemma, args.lemma_summary, provenance=args.lemma_provenance)
        print(f"Appended solved lemma to {SOLVED_LEMMAS}")

    if args.sync_memory_hierarchy:
        n = sync_memory_hierarchy()
        print(f"Synced {n} lemma(s) to .agent/memory_hierarchy/")

    if args.summary or (
        not args.append_log
        and not args.update_commit
        and not args.trim
        and not args.fold_lemma
        and not args.sync_memory_hierarchy
    ):
        s = summary()
        print(
            f"MEMORY: {s['memory_lines']} entries | log: {s['log_lines']} | "
            f"handoff: {s['handoff_count']} | errors: {s['error_count']} | lemmas: {s['solved_lemmas']}"
        )
        print(f"main.md: {s['has_main']} | commit.md: {s['has_commit']}")


if __name__ == "__main__":
    main()
