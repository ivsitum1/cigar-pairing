#!/usr/bin/env python3
"""Health check for brain and project. Exit 0 if all ok, 1 if issues."""
import argparse
import json
import subprocess
import sys
import warnings
from pathlib import Path

# Avoid noisy urllib3/charset mismatch warning when requests is pulled in transitively
warnings.filterwarnings("ignore", message=r".*urllib3.*doesn't match a supported version.*")

AGENT_RULES = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = AGENT_RULES.parent if (AGENT_RULES.parent / "01_input").exists() else AGENT_RULES
CURSOR_SCRIPTS = PROJECT_ROOT / ".cursor" / "scripts"
SCRIPTS = AGENT_RULES / "40_operations/scripts"

MEMORY_MAX_LINES = 250


def run(cmd: list[str], cwd=None) -> tuple:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(cwd or PROJECT_ROOT),
    )
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    return result.returncode, stdout + (stderr if result.returncode != 0 else "")


def check_structure(report: dict) -> None:
    ok = True
    paths = {
        ".agent": PROJECT_ROOT / ".agent",
        "30_system/context": AGENT_RULES / "30_system" / "context",
        "40_operations/scripts": AGENT_RULES / "40_operations/scripts",
    }
    for name, p in paths.items():
        exists = p.exists()
        report["structure"][name] = "ok" if exists else "missing"
        if not exists:
            ok = False
    report["ok"] = report["ok"] and ok


def check_context(report: dict) -> None:
    # Identity context — always present in agent rules repo
    ctx = AGENT_RULES / "30_system" / "context"
    for name in ["user.md", "soul.md", "memory.md"]:
        p = ctx / name
        try:
            readable = p.exists() and len(p.read_text(encoding="utf-8")) > 0
        except Exception:
            readable = False
        report["30_system/context"][name] = "ok" if readable else "missing"
        if not readable:
            report["ok"] = False

    # Project documentation context — present when a project is active (warn-only)
    doc_ctx = PROJECT_ROOT / "30_system" / "04_documentation" / "context"
    doc_status = {}
    for name in ["main.md", "commit.md", "log.md"]:
        p = doc_ctx / name
        try:
            readable = p.exists() and len(p.read_text(encoding="utf-8")) > 0
        except Exception:
            readable = False
        doc_status[name] = "ok" if readable else "absent"
    report["04_documentation/context (project, warn-only)"] = doc_status


def check_memory(report: dict) -> None:
    mem = PROJECT_ROOT / ".agent" / "MEMORY.md"
    if not mem.exists():
        report["memory"] = "missing"
        report["ok"] = False
        return
    lines = len([l for l in mem.read_text(encoding="utf-8").split("\n") if l.strip()])
    if lines > MEMORY_MAX_LINES:
        report["memory"] = f"warn ({lines} lines, trim recommended)"
    else:
        report["memory"] = f"ok ({lines} lines)"


def check_handoff(report: dict) -> None:
    handoff = PROJECT_ROOT / ".agent" / "handoff_log.jsonl"
    if not handoff.exists():
        report["handoff"] = "ok (none)"
        return
    invalid = 0
    for line in handoff.read_text(encoding="utf-8").strip().split("\n"):
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError:
            invalid += 1
    if invalid:
        report["handoff"] = f"warn ({invalid} invalid lines)"
        report["ok"] = False
    else:
        report["handoff"] = "ok"


def check_errors(report: dict, *, strict: bool = False) -> None:
    """Fail on unpromoted critical/high entries. Promoted entries are learning memory."""
    err_log = PROJECT_ROOT / ".cursor" / "errors" / "error_log.jsonl"
    if not err_log.exists():
        report["errors"] = "ok (none)"
        return
    total = 0
    promoted_learning = 0
    unpromoted_critical_high = 0
    any_critical_high = 0
    for line in err_log.read_text(encoding="utf-8").strip().split("\n"):
        if not line.strip():
            continue
        total += 1
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        if j.get("sev") not in ("critical", "high"):
            continue
        any_critical_high += 1
        if j.get("promoted") is True:
            promoted_learning += 1
        else:
            unpromoted_critical_high += 1
    if strict and any_critical_high:
        report["errors"] = (
            f"fail ({total} total, {any_critical_high} critical/high, strict mode)"
        )
        report["ok"] = False
    elif unpromoted_critical_high:
        report["errors"] = (
            f"fail ({total} total, {unpromoted_critical_high} unpromoted critical/high)"
        )
        report["ok"] = False
    elif promoted_learning:
        report["errors"] = (
            f"ok ({total} entries, {promoted_learning} promoted learning events)"
        )
    else:
        report["errors"] = f"ok ({total} entries)"


def check_scripts(report: dict) -> None:
    results = {}
    scripts_to_test = [
        ("context_sync", [sys.executable, str(SCRIPTS / "context_sync.py"), "--summary"]),
        ("brain_status", [sys.executable, str(SCRIPTS / "brain_status.py")]),
        ("memory_trim", [sys.executable, str(SCRIPTS / "memory_trim.py")]),
    ]
    for name, cmd in scripts_to_test:
        code, _ = run(cmd, PROJECT_ROOT)
        results[name] = "ok" if code == 0 else "fail"
        if code != 0:
            report["ok"] = False
    report["40_operations/scripts"] = results


def check_error_ops(report: dict) -> None:
    err_ops = CURSOR_SCRIPTS / "error_ops.py"
    bridge = CURSOR_SCRIPTS / "error_to_learning_bridge.py"
    if not err_ops.exists():
        report["error_ops"] = "missing"
        report["ok"] = False
        return
    code1, _ = run([sys.executable, str(err_ops), "audit"], PROJECT_ROOT)
    code2, _ = run([sys.executable, str(bridge)], PROJECT_ROOT) if bridge.exists() else (0, "")
    report["error_ops"] = "ok" if code1 == 0 else "fail"
    if code1 != 0:
        report["ok"] = False


def check_git(report: dict) -> None:
    code, _ = run(["git", "status"], PROJECT_ROOT)
    report["git"] = "ok" if code == 0 else "fail"
    if code != 0:
        report["ok"] = False


def check_python(report: dict) -> None:
    v = sys.version_info
    ok = v.major >= 3 and v.minor >= 8
    report["python"] = f"ok ({v.major}.{v.minor})" if ok else f"fail (need 3.8+)"
    if not ok:
        report["ok"] = False


SURPRISES_LOG = PROJECT_ROOT / ".cursor" / "surprises.log"


def log_surprise(context: str, description: str, solution: str = "") -> None:
    """Append an unexpected finding to .cursor/surprises.log."""
    SURPRISES_LOG.parent.mkdir(parents=True, exist_ok=True)
    ts = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"[{ts}] [{context}] What is confusing: {description}."
    if solution:
        line += f" Proposed solution: {solution}."
    with open(SURPRISES_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def check_cursor_skills(report: dict) -> None:
    """Fail if Obsidian wiki skill junctions are missing or point at OneDrive."""
    bootstrap = SCRIPTS / "workspace_bootstrap.py"
    if not bootstrap.is_file():
        report["cursor_skills"] = "warn (workspace_bootstrap.py missing)"
        return

    def _parse_junctions(out: str) -> tuple[int, dict | None]:
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            return 0, None
        junctions = data.get("steps", {}).get("junctions", {})
        return junctions.get("total", 0), junctions

    code, out = run(
        [sys.executable, str(bootstrap), "--check-only", "--json"],
        AGENT_RULES,
    )
    if code != 0:
        run(
            [sys.executable, str(bootstrap), "--json"],
            AGENT_RULES,
        )
        code, out = run(
            [sys.executable, str(bootstrap), "--check-only", "--json"],
            AGENT_RULES,
        )

    if code != 0:
        total, junctions = _parse_junctions(out)
        if junctions:
            broken = len(junctions.get("broken", []))
            stale = junctions.get("stale_onedrive", 0)
            missing = junctions.get("missing_upstream", 0)
            if missing:
                report["cursor_skills"] = "fail (obsidian-wiki upstream .skills missing after bootstrap)"
            else:
                report["cursor_skills"] = f"fail ({broken} broken junctions, {stale} stale OneDrive)"
        else:
            report["cursor_skills"] = "fail (junction check)"
        report["ok"] = False
        return

    total, _ = _parse_junctions(out)
    report["cursor_skills"] = f"ok ({total} junctions)"


def check_mcp_deps(report: dict) -> None:
    """Check that MCP server dependencies are importable (warn-only)."""
    try:
        import importlib
        importlib.import_module("fastmcp")
        report["mcp_deps"] = "ok (fastmcp available)"
    except ImportError:
        report["mcp_deps"] = (
            "warn (fastmcp not installed; optional: "
            "pip install -r 40_operations/requirements-optional-mcp.txt; "
            "CLI handoff fallback still works)"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any critical/high error_log entry (ignore promoted flag)",
    )
    args = parser.parse_args()

    report = {
        "ok": True,
        "structure": {},
        "30_system/context": {},
        "04_documentation/context (project, warn-only)": {},
        "memory": "",
        "handoff": "",
        "errors": "",
        "40_operations/scripts": {},
        "error_ops": "",
        "git": "",
        "python": "",
        "cursor_skills": "",
        "mcp_deps": "",
    }

    check_structure(report)
    check_context(report)
    check_memory(report)
    check_handoff(report)
    check_errors(report, strict=args.strict)
    check_scripts(report)
    check_error_ops(report)
    check_git(report)
    check_python(report)
    check_cursor_skills(report)
    check_mcp_deps(report)

    if args.json:
        # Remove empty dicts for cleaner output
        out = {k: v for k, v in report.items() if v}
        print(json.dumps(out, indent=2))
    else:
        print("=== BRAIN HEALTH CHECK ===")
        print(f"Project root: {PROJECT_ROOT}")
        print()
        for k, v in report.items():
            if k == "ok":
                continue
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    print(f"  {k}/{k2}: {v2}")
            else:
                print(f"  {k}: {v}")
        print()
        print("Result:", "PASS" if report["ok"] else "FAIL")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
