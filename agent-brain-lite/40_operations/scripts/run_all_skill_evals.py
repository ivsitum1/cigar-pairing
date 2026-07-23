"""
Run eval for every registry skill that has evals/<skill_id>.json.

Phases:
  1. Lint eval JSON (schema + regex validity) via lint_skill_evals.py
  2. Evaluate assertions using <skill_id>_outputs.json when present (no API)
  3. Optional --live: call LLM per skill missing outputs (needs OPENAI_API_KEY or ANTHROPIC_API_KEY)

Usage:
    py -3 40_operations/scripts/run_all_skill_evals.py
    py -3 40_operations/scripts/run_all_skill_evals.py --live
    py -3 40_operations/scripts/run_all_skill_evals.py --json-out .agent/task/skill_eval_run_all.json
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
EVALS_DIR = WORKSPACE / "30_system/SKILLS/evals"
REGISTRY_PATH = WORKSPACE / "30_system/SKILLS/registry.json"
RUNNER = WORKSPACE / "40_operations/scripts/skill_eval_runner.py"
LINTER = WORKSPACE / "40_operations/scripts/lint_skill_evals.py"


def registry_skill_ids() -> list[str]:
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return [s["id"] for s in data["skills"]]


def run_lint() -> int:
    r = subprocess.run(
        [sys.executable, str(LINTER)],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    print(r.stdout, end="")
    if r.stderr:
        print(r.stderr, file=sys.stderr, end="")
    return r.returncode


def eval_one(skill_id: str, outputs_path: Path | None, live: bool) -> dict:
    import subprocess

    tmp_result = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
    tmp_path = tmp_result.name
    tmp_result.close()

    cmd = [sys.executable, str(RUNNER), "--skill-id", skill_id, "--json", "--output", tmp_path]
    if outputs_path and outputs_path.exists():
        cmd.extend(["--outputs", str(outputs_path)])
    elif live:
        save_out = EVALS_DIR / f"{skill_id}_outputs.json"
        cmd.extend(["--save-outputs", str(save_out)])
    else:
        return {
            "skill_id": skill_id,
            "status": "skipped",
            "reason": "no _outputs.json; use --live or generate outputs first",
        }

    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")

    try:
        r = subprocess.run(
            cmd,
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600 if live else 120,
            env=env,
        )
        if r.returncode != 0:
            return {
                "skill_id": skill_id,
                "status": "error",
                "stderr": (r.stderr or "")[:500],
            }
        out = json.loads(Path(tmp_path).read_text(encoding="utf-8"))
        out["status"] = "ok"
        out["mode"] = "outputs_file" if outputs_path and outputs_path.exists() else "live"
        return out
    except Exception as exc:
        return {"skill_id": skill_id, "status": "error", "error": str(exc)[:300]}
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def main() -> int:
    live = "--live" in sys.argv
    json_out = None
    for i, arg in enumerate(sys.argv):
        if arg == "--json-out" and i + 1 < len(sys.argv):
            json_out = Path(sys.argv[i + 1])

    print("=== Phase 1: lint eval JSON ===")
    lint_rc = run_lint()
    if lint_rc != 0:
        print("Lint failed; fix eval files before running.", file=sys.stderr)
        return 1

    print("\n=== Phase 2: run assertions ===")
    if live:
        if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")):
            print("Error: --live requires OPENAI_API_KEY or ANTHROPIC_API_KEY", file=sys.stderr)
            return 1

    results: list[dict] = []
    for skill_id in registry_skill_ids():
        eval_path = EVALS_DIR / f"{skill_id}.json"
        if not eval_path.exists():
            results.append({"skill_id": skill_id, "status": "no_eval_file"})
            continue
        outputs_path = EVALS_DIR / f"{skill_id}_outputs.json"
        if not outputs_path.exists() and not live:
            results.append(eval_one(skill_id, None, live=False))
            continue
        results.append(eval_one(skill_id, outputs_path if outputs_path.exists() else None, live=live))

    summary = {
        "lint_passed": True,
        "live_mode": live,
        "skills": results,
    }
    if json_out:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nWrote {json_out}")

    print("\nSkill\tPass %\tStatus")
    print("-" * 60)
    for row in results:
        sid = row.get("skill_id", "?")
        if row.get("status") == "ok":
            print(f"{sid}\t{row.get('pass_rate_pct', 0)}%\tok ({row.get('mode')})")
        else:
            print(f"{sid}\t—\t{row.get('status')}: {row.get('reason') or row.get('stderr') or row.get('error', '')[:80]}")

    failed = [r for r in results if r.get("status") == "ok" and (r.get("pass_rate_pct") or 0) < 100]
    skipped = [r for r in results if r.get("status") in ("skipped", "no_eval_file")]
    errors = [r for r in results if r.get("status") == "error"]
    print(f"\nSummary: ok={sum(1 for r in results if r.get('status')=='ok')}, "
          f"below_100%={len(failed)}, skipped={len(skipped)}, errors={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
