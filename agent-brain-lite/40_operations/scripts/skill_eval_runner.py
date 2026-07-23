"""
Skill eval runner: run a skill against evals.json, call LLM per case, evaluate binary assertions, output pass rate.

Usage:
    python 40_operations/scripts/skill_eval_runner.py --skill-id avoid-ai-formulations
    SKILL_ID=avoid-ai-formulations python 40_operations/scripts/skill_eval_runner.py

Requires: OPENAI_API_KEY or ANTHROPIC_API_KEY (unless --outputs is used).
With --outputs <path>: evaluate pre-produced outputs only (no API). JSON at path: {"case_1": "text", ...}.
Output: Human-readable summary + machine-readable JSON (--json or --output <path>).
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = WORKSPACE / "30_system/SKILLS"
EVALS_DIR = SKILLS_DIR / "evals"


def load_skill_content(skill_id: str) -> str:
    """Load full content of SKILL_<id>.md (no path traversal)."""
    safe_id = skill_id.strip().lower().replace(" ", "-")
    if re.search(r"[^a-z0-9\-]", safe_id):
        raise ValueError(f"Invalid skill_id: {skill_id}")
    path = SKILLS_DIR / f"SKILL_{safe_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"Skill file not found: {path}")
    return path.read_text(encoding="utf-8")


def load_evals(skill_id: str) -> dict:
    """Load 30_system/SKILLS/evals/<skill_id>.json."""
    safe_id = skill_id.strip().lower().replace(" ", "-")
    if re.search(r"[^a-z0-9\-]", safe_id):
        raise ValueError(f"Invalid skill_id: {skill_id}")
    path = EVALS_DIR / f"{safe_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Evals file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def word_count(text: str) -> int:
    """Count words: split on whitespace, drop empty."""
    return len([w for w in text.split() if w])


def last_sentence_not_question(text: str) -> bool:
    """True if the last non-empty sentence does not end with ?."""
    text = text.strip()
    if not text:
        return True
    last_char = text[-1]
    if last_char == "?":
        return False
    return True


def evaluate_assertion(output: str, assertion: dict) -> bool:
    """Evaluate a single assertion on output. Returns True if pass."""
    atype = assertion.get("type")
    value = assertion.get("value")

    if atype == "contains":
        return value is not None and str(value) in output

    if atype == "not_contains":
        return value is not None and str(value) not in output

    if atype == "regex_match":
        if value is None:
            return False
        try:
            return bool(re.search(value, output))
        except re.error:
            return False

    if atype == "regex_not_match":
        if value is None:
            return True
        try:
            return not re.search(value, output)
        except re.error:
            return True

    if atype == "word_count_below":
        n = word_count(output)
        return value is not None and n < int(value)

    if atype == "word_count_above":
        n = word_count(output)
        return value is not None and n > int(value)

    if atype == "word_count_between":
        if not isinstance(value, list) or len(value) != 2:
            return False
        n = word_count(output)
        lo, hi = int(value[0]), int(value[1])
        return lo <= n <= hi

    if atype == "last_sentence_not_question":
        return last_sentence_not_question(output)

    return False


def call_llm(skill_content: str, case_input: dict, provider: str) -> str:
    """Build prompt, call OpenAI or Anthropic, return model output only."""
    text = case_input.get("text", "")
    if isinstance(case_input.get("text"), str):
        input_str = text
    else:
        input_str = json.dumps(case_input, ensure_ascii=False)

    prompt = (
        "You are applying the following skill. Produce only the output (no commentary, no preamble).\n\n"
        "--- Skill instructions ---\n"
        f"{skill_content}\n\n"
        "--- Input ---\n"
        f"{input_str}\n\n"
        "--- Output (skill applied) ---\n"
    )

    if provider == "openai":
        return _call_openai(prompt)
    if provider == "anthropic":
        return _call_anthropic(prompt)
    raise ValueError(f"Unknown provider: {provider}")


def _call_openai(prompt: str) -> str:
    try:
        import openai
    except ImportError:
        raise ImportError("openai package required for OpenAI. pip install openai")
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not set")
    resp = client.chat.completions.create(
        model=os.environ.get("SKILL_EVAL_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return (resp.choices[0].message.content or "").strip()


def _call_anthropic(prompt: str) -> str:
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package required. pip install anthropic")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise ValueError("ANTHROPIC_API_KEY not set")
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=os.environ.get("SKILL_EVAL_MODEL", "claude-3-5-haiku-20241022"),
        max_tokens=4096,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    text = msg.content[0].text if msg.content else ""
    return text.strip()


def run_evals(
    skill_id: str,
    provider: str,
    json_output: bool = False,
    out_path: str | None = None,
    outputs_path: str | None = None,
    save_outputs_path: str | None = None,
) -> dict:
    """Load skill + evals, run each case (LLM or pre-provided outputs), evaluate assertions. Return result dict."""
    evals_data = load_evals(skill_id)
    if evals_data.get("skill_id") != skill_id:
        evals_data["skill_id"] = skill_id

    if outputs_path:
        with open(outputs_path, "r", encoding="utf-8") as f:
            outputs_by_case = json.load(f)
        skill_content = None
        collected_outputs = None
    else:
        skill_content = load_skill_content(skill_id)
        outputs_by_case = None
        collected_outputs = {} if save_outputs_path else None

    results = []
    total_assertions = 0
    passed_assertions = 0
    failed_list = []

    for case in evals_data.get("cases", []):
        case_id = case.get("id", "?")
        case_input = case.get("input", {})
        assertions = case.get("assertions", [])

        if outputs_by_case is not None:
            output = (outputs_by_case.get(case_id) or "").strip()
        else:
            try:
                output = call_llm(skill_content, case_input, provider)
                if collected_outputs is not None:
                    collected_outputs[case_id] = output
            except Exception as e:
                output = ""
                results.append({
                    "case_id": case_id,
                    "error": str(e),
                    "passed": 0,
                    "total": len(assertions),
                })
                total_assertions += len(assertions)
                for a in assertions:
                    failed_list.append({"case_id": case_id, "assertion": a, "reason": str(e)})
                continue

        case_passed = 0
        for a in assertions:
            total_assertions += 1
            pass_ = evaluate_assertion(output, a)
            if pass_:
                passed_assertions += 1
                case_passed += 1
            else:
                failed_list.append({
                    "case_id": case_id,
                    "assertion": a,
                    "output_snippet": output[:200] + ("..." if len(output) > 200 else ""),
                })

        results.append({
            "case_id": case_id,
            "passed": case_passed,
            "total": len(assertions),
        })

    if collected_outputs is not None and save_outputs_path:
        Path(save_outputs_path).write_text(json.dumps(collected_outputs, ensure_ascii=False, indent=2), encoding="utf-8")

    pass_rate = (passed_assertions / total_assertions * 100) if total_assertions else 0.0
    out = {
        "skill_id": skill_id,
        "pass_rate_pct": round(pass_rate, 2),
        "passed_assertions": passed_assertions,
        "total_assertions": total_assertions,
        "cases": results,
        "failed_assertions": failed_list,
    }
    if json_output or out_path:
        payload = json.dumps(out, ensure_ascii=False, indent=2)
        if out_path:
            Path(out_path).write_text(payload, encoding="utf-8")
        if json_output:
            print(payload)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Run skill evals and report pass rate.")
    parser.add_argument("--skill-id", default=os.environ.get("SKILL_ID"), help="Skill id (or set SKILL_ID)")
    parser.add_argument("--provider", choices=["openai", "anthropic"], default=None,
                        help="LLM provider (default: openai if OPENAI_API_KEY else anthropic)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON to stdout")
    parser.add_argument("--output", metavar="PATH", help="Write JSON result to file")
    parser.add_argument("--outputs", metavar="PATH", help="Evaluate only: JSON file with case_id -> output text (no API)")
    parser.add_argument("--save-outputs", metavar="PATH", help="When using API: save LLM outputs to this JSON file (case_id -> text)")
    args = parser.parse_args()

    skill_id = args.skill_id
    if not skill_id:
        print("Error: --skill-id or SKILL_ID required.", file=sys.stderr)
        return 1

    provider = "openai"
    if not args.outputs:
        if args.provider:
            provider = args.provider
        else:
            provider = "openai" if os.environ.get("OPENAI_API_KEY") else "anthropic"
        if provider == "openai" and not os.environ.get("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY not set (required for --provider openai).", file=sys.stderr)
            return 1
        if provider == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
            print("Error: ANTHROPIC_API_KEY not set (required for --provider anthropic).", file=sys.stderr)
            return 1

    try:
        out = run_evals(
            skill_id, provider,
            json_output=args.json, out_path=args.output,
            outputs_path=args.outputs,
            save_outputs_path=getattr(args, "save_outputs", None),
        )
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if not args.json:
        print(f"Skill: {out['skill_id']}")
        print(f"Pass rate: {out['pass_rate_pct']}% ({out['passed_assertions']}/{out['total_assertions']} assertions)")
        if out["failed_assertions"]:
            print("Failed assertions:")
            for fa in out["failed_assertions"][:20]:
                desc = fa.get("assertion", {}).get("description", fa.get("assertion", {}).get("type"))
                print(f"  - {fa['case_id']}: {desc}")
            if len(out["failed_assertions"]) > 20:
                print(f"  ... and {len(out['failed_assertions']) - 20} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
