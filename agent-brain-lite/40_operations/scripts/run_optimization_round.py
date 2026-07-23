"""
One round of optimization: for each skill, generate outputs via API (--save-outputs)
then run eval. Use when OPENAI_API_KEY or ANTHROPIC_API_KEY is set.
Skips skills that already have 100% (keeps existing outputs).

Usage:
    python 40_operations/scripts/run_optimization_round.py
    python 40_operations/scripts/run_optimization_round.py --force  # regenerate outputs for all skills
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
EVALS_DIR = WORKSPACE / "30_system/SKILLS" / "evals"
RUNNER = WORKSPACE / "40_operations/scripts" / "skill_eval_runner.py"


def run_eval(skill_id: str, out_path: Path) -> tuple[float | None, list]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        tmp_path = tmp.name
    try:
        with open(tmp_path, "w", encoding="utf-8") as outfile:
            r = subprocess.run(
                [sys.executable, str(RUNNER), "--skill-id", skill_id, "--outputs", str(out_path), "--json"],
                stdout=outfile,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(WORKSPACE),
                timeout=90,
            )
        if r.returncode != 0:
            return None, []
        data = json.loads(Path(tmp_path).read_text(encoding="utf-8"))
        return data.get("pass_rate_pct"), data.get("failed_assertions", [])
    except Exception:
        return None, []
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def main() -> int:
    force = "--force" in sys.argv
    skill_ids = sorted({p.stem for p in EVALS_DIR.glob("*.json") if not p.name.endswith("_outputs.json")})
    results = []
    for skill_id in skill_ids:
        out_path = EVALS_DIR / f"{skill_id}_outputs.json"
        if not out_path.exists():
            results.append((skill_id, None, "no outputs"))
            continue
        pct_before, _ = run_eval(skill_id, out_path)
        if pct_before is None:
            results.append((skill_id, None, "eval error"))
            continue
        if pct_before >= 100.0 and not force:
            results.append((skill_id, pct_before, "already 100%"))
            continue
        # Generate new outputs via API
        r = subprocess.run(
            [sys.executable, str(RUNNER), "--skill-id", skill_id, "--save-outputs", str(out_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(WORKSPACE),
            timeout=120,
        )
        if r.returncode != 0 and "API_KEY" in (r.stderr or ""):
            results.append((skill_id, pct_before, "no API key"))
            continue
        pct_after, failed = run_eval(skill_id, out_path)
        if pct_after is not None:
            results.append((skill_id, pct_after, f"{len(failed)} failed" if failed else "100%"))
        else:
            results.append((skill_id, pct_before, "eval error after gen"))
    print("Skill\tPass %\tNote")
    print("-" * 55)
    for skill_id, pct, note in results:
        pct_s = f"{pct}%" if pct is not None else "—"
        print(f"{skill_id}\t{pct_s}\t{note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
