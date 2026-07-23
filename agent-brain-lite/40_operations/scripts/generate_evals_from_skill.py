"""
Phase 0: Generate initial evals.json from a skill file.

The LLM is prompted to produce a valid evals.json with 5-15 cases and binary-only
assertions derived from the skill's verification checklist and never/always rules.

Usage:
    python 40_operations/scripts/generate_evals_from_skill.py --skill-id avoid-ai-formulations
    SKILL_ID=manuscript-structure python 40_operations/scripts/generate_evals_from_skill.py

Requires: OPENAI_API_KEY or ANTHROPIC_API_KEY.
Output: 30_system/SKILLS/evals/<skill_id>.json (overwrites if present).
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
    """Load full content of SKILL_<id>.md."""
    safe_id = skill_id.strip().lower().replace(" ", "-")
    if re.search(r"[^a-z0-9\-]", safe_id):
        raise ValueError(f"Invalid skill_id: {skill_id}")
    path = SKILLS_DIR / f"SKILL_{safe_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"Skill file not found: {path}")
    return path.read_text(encoding="utf-8")


def call_llm(skill_content: str, skill_id: str, provider: str) -> str:
    """Ask LLM to generate evals.json; return raw response."""
    prompt = f"""You are generating an evals.json file for the autonomous skill optimization loop.

Skill id: {skill_id}

--- Skill file content ---
{skill_content}
--- End skill file ---

Generate a valid evals.json with:
- "skill_id": "{skill_id}"
- "version": "1.0"
- "cases": array of 5 to 15 test cases

Each case must have:
- "id": unique string (e.g. case_1, case_2)
- "input": object with "text" (string) for writing skills, or other fields as needed
- "assertions": array of binary assertions

Allowed assertion types (value as needed):
- contains (string): output must contain
- not_contains (string): output must not contain
- regex_match (string): output matches regex
- regex_not_match (string): output must not match
- word_count_below (number): word count < N
- word_count_above (number): word count > N
- word_count_between ([min, max]): min <= word count <= max
- last_sentence_not_question: no value needed

Derive assertions from the skill's Verification checklist, "Never/Always" rules, and step-by-step procedure. Use only deterministic, binary checks (no subjective criteria like "sounds natural").

Output ONLY a single JSON object, no markdown fences or commentary. Valid JSON only."""

    if provider == "openai":
        return _call_openai(prompt)
    if provider == "anthropic":
        return _call_anthropic(prompt)
    raise ValueError(f"Unknown provider: {provider}")


def _call_openai(prompt: str) -> str:
    try:
        import openai
    except ImportError:
        raise ImportError("openai package required. pip install openai")
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not set")
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
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
    return (msg.content[0].text if msg.content else "").strip()


def extract_json(text: str) -> str:
    """Extract JSON from response, optionally inside ```json ... ```."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text


def validate_evals(data: dict, skill_id: str) -> list[str]:
    """Basic schema validation. Returns list of error messages."""
    errors = []
    if data.get("skill_id") != skill_id:
        errors.append(f"skill_id must be '{skill_id}'")
    if "version" not in data:
        errors.append("Missing 'version'")
    if "cases" not in data or not isinstance(data["cases"], list):
        errors.append("'cases' must be a non-empty array")
    else:
        for i, case in enumerate(data["cases"]):
            if not isinstance(case, dict):
                errors.append(f"cases[{i}] must be an object")
                continue
            if "id" not in case:
                errors.append(f"cases[{i}] missing 'id'")
            if "input" not in case:
                errors.append(f"cases[{i}] missing 'input'")
            if "assertions" not in case or not isinstance(case["assertions"], list):
                errors.append(f"cases[{i}] must have 'assertions' array")
            else:
                for j, a in enumerate(case["assertions"]):
                    if not isinstance(a, dict) or "type" not in a:
                        errors.append(f"cases[{i}].assertions[{j}] must have 'type'")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate evals.json from a skill file (Phase 0).")
    parser.add_argument("--skill-id", default=os.environ.get("SKILL_ID"), help="Skill id (or set SKILL_ID)")
    parser.add_argument("--provider", choices=["openai", "anthropic"], default=None,
                        help="LLM provider (default: openai if OPENAI_API_KEY else anthropic)")
    parser.add_argument("--dry-run", action="store_true", help="Print JSON to stdout, do not write file")
    args = parser.parse_args()

    skill_id = args.skill_id
    if not skill_id:
        print("Error: --skill-id or SKILL_ID required.", file=sys.stderr)
        return 1

    provider = args.provider
    if not provider:
        provider = "openai" if os.environ.get("OPENAI_API_KEY") else "anthropic"
    if provider == "openai" and not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set.", file=sys.stderr)
        return 1
    if provider == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set.", file=sys.stderr)
        return 1

    try:
        skill_content = load_skill_content(skill_id)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        raw = call_llm(skill_content, skill_id, provider)
    except (ImportError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    json_str = extract_json(raw)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error: LLM output is not valid JSON: {e}", file=sys.stderr)
        print("Raw output (first 500 chars):", file=sys.stderr)
        print(raw[:500], file=sys.stderr)
        return 1

    data["skill_id"] = skill_id
    data["version"] = data.get("version", "1.0")

    errs = validate_evals(data, skill_id)
    if errs:
        print("Validation errors:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1

    out_json = json.dumps(data, ensure_ascii=False, indent=2)

    if args.dry_run:
        print(out_json)
        return 0

    EVALS_DIR.mkdir(parents=True, exist_ok=True)
    safe_id = skill_id.strip().lower().replace(" ", "-")
    out_path = EVALS_DIR / f"{safe_id}.json"
    out_path.write_text(out_json + "\n", encoding="utf-8")
    print(f"Written: {out_path} ({len(data['cases'])} cases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
