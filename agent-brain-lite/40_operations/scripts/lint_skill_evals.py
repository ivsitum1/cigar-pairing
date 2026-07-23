"""Lint evals/<skill_id>.json against registry and assertion schema."""
import json
import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = WORKSPACE / "30_system/SKILLS/registry.json"
EVALS_DIR = WORKSPACE / "30_system/SKILLS/evals"

VALID_TYPES = {
    "contains",
    "not_contains",
    "regex_match",
    "regex_not_match",
    "word_count_below",
    "word_count_above",
    "word_count_between",
    "last_sentence_not_question",
}


def validate_evals(data: dict, skill_id: str) -> list[str]:
    errors: list[str] = []
    if data.get("skill_id") != skill_id:
        errors.append(f"skill_id mismatch: {data.get('skill_id')!r} != {skill_id!r}")
    if "version" not in data:
        errors.append("missing version")
    cases = data.get("cases")
    if not cases or not isinstance(cases, list):
        errors.append("cases must be a non-empty array")
        return errors
    ids: set[str] = set()
    for i, case in enumerate(cases):
        cid = case.get("id")
        label = cid or f"cases[{i}]"
        if not cid:
            errors.append(f"cases[{i}] missing id")
        elif cid in ids:
            errors.append(f"duplicate case id: {cid}")
        else:
            ids.add(cid)
        if "input" not in case:
            errors.append(f"{label}: missing input")
        elif not isinstance(case.get("input"), dict):
            errors.append(f"{label}: input must be object")
        elif "text" not in case["input"]:
            errors.append(f"{label}: input.text missing (required for runner)")
        assertions = case.get("assertions")
        if not assertions:
            errors.append(f"{label}: no assertions")
        elif not isinstance(assertions, list):
            errors.append(f"{label}: assertions must be array")
        else:
            for j, a in enumerate(assertions):
                if not isinstance(a, dict):
                    errors.append(f"{label} assertions[{j}]: not an object")
                    continue
                atype = a.get("type")
                if atype not in VALID_TYPES:
                    errors.append(f"{label} assertions[{j}]: unknown type {atype!r}")
                if atype in ("contains", "not_contains", "regex_match", "regex_not_match"):
                    if a.get("value") is None:
                        errors.append(f"{label} assertions[{j}]: missing value for {atype}")
                if atype and atype.startswith("regex"):
                    try:
                        re.compile(str(a.get("value", "")))
                    except re.error as exc:
                        errors.append(f"{label} assertions[{j}]: bad regex: {exc}")
                if atype == "word_count_between":
                    v = a.get("value")
                    if not isinstance(v, list) or len(v) != 2:
                        errors.append(f"{label} assertions[{j}]: word_count_between needs [min,max]")
    return errors


def main() -> int:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    registry_ids = [s["id"] for s in registry["skills"]]
    missing: list[str] = []
    lint_ok: list[str] = []
    lint_fail: dict[str, list[str]] = {}

    for sid in registry_ids:
        path = EVALS_DIR / f"{sid}.json"
        if not path.exists():
            missing.append(sid)
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            lint_fail[sid] = [f"invalid JSON: {exc}"]
            continue
        errs = validate_evals(data, sid)
        if errs:
            lint_fail[sid] = errs
        else:
            lint_ok.append(sid)

    print(f"registry_skills={len(registry_ids)}")
    print(f"eval_present_lint_ok={len(lint_ok)}")
    print(f"eval_missing={len(missing)}")
    print(f"eval_lint_fail={len(lint_fail)}")
    if missing:
        print("MISSING:")
        for sid in missing:
            print(f"  - {sid}")
    if lint_fail:
        print("LINT_FAIL:")
        for sid, errs in sorted(lint_fail.items()):
            print(f"  {sid}:")
            for e in errs:
                print(f"    - {e}")
    return 1 if missing or lint_fail else 0


if __name__ == "__main__":
    sys.exit(main())
