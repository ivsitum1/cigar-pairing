"""
Convert SKILLS_evals_all.md to 30_system/SKILLS/evals/<skill_id>.json per skill.

Parses ## skill_id sections, ### Case N blocks, **Input:** and **Assertions:**.
Handles OR in assertions by merging into regex where possible, or taking first alternative.
Output: valid evals JSON per schema in 30_system/SKILLS/evals/README.md.

Usage:
    python 40_operations/scripts/md_evals_to_json.py [path_to_SKILLS_evals_all.md]
    Default path: workspace docs or 30_system/SKILLS/evals/SKILLS_evals_all.md
"""

import json
import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
EVALS_DIR = WORKSPACE / "30_system/SKILLS" / "evals"
DEFAULT_MD = WORKSPACE / "30_system/SKILLS" / "evals" / "SKILLS_evals_all.md"


def slug(s: str) -> str:
    return s.strip().lower().replace(" ", "-").replace("_", "-")


def parse_assertion_line(line: str) -> list[dict]:
    """Parse one assertion line; may contain OR. Returns list of assertion dicts (type, value, description)."""
    line = line.strip()
    if not line or not line.startswith("-"):
        return []
    # Remove leading -
    line = line[1:].strip()
    # Match backtick-enclosed type and value. Value can be "quoted" or `regex` or number
    # Also match OR alternatives: `type`: "value" OR `type`: "value2"
    parts = re.split(r"\s+OR\s+", line, flags=re.IGNORECASE)
    assertions = []
    for part in parts:
        part = part.strip()
        # Description after " — "
        desc_match = re.search(r"\s+—\s+(.+)$", part)
        desc = desc_match.group(1).strip() if desc_match else ""
        if desc_match:
            part = part[: desc_match.start()].strip()
        # type and value
        if "`last_sentence_not_question`" in part or part.strip() == "`last_sentence_not_question`":
            assertions.append({"type": "last_sentence_not_question", "description": desc or "Last sentence not ?"})
            continue
        m = re.match(r"`(\w+)`:\s*(.+)$", part)
        if not m:
            continue
        atype, v = m.group(1), m.group(2).strip()
        value = None
        if atype in ("word_count_below", "word_count_above") and v.isdigit():
            value = int(v)
        elif v.startswith('"') and v.endswith('"'):
            value = v[1:-1].replace('\\"', '"')
        elif v.startswith("`") and v.endswith("`"):
            value = v[1:-1].replace("\\`", "`")
        else:
            value = v
        if atype == "regex_match" and value and not value.startswith("(?i)") and atype != "regex_not_match":
            # Optional: add (?i) for case-insensitive where it's not already a pattern
            pass  # leave as-is; spec says add (?i) where appropriate, we keep original
        assertions.append({"type": atype, "value": value, "description": desc or f"{atype}: {str(value)[:50]}"})
    return assertions


def merge_or_assertions(assertions: list[dict]) -> list[dict]:
    """If multiple assertions are same type with OR (e.g. contains A OR contains B), merge into one regex_match where possible."""
    if len(assertions) <= 1:
        return assertions
    types = [a["type"] for a in assertions]
    if len(types) and types.count(types[0]) == len(types) and types[0] == "contains":
        # Merge contains A|B into one regex
        vals = [re.escape(str(a["value"])) for a in assertions]
        return [{"type": "regex_match", "value": "(?i)(" + "|".join(vals) + ")", "description": " OR ".join(a.get("description", "") for a in assertions)}]
    if types.count(types[0]) == len(types) and types[0] == "not_contains":
        # Keep all not_contains (must not contain A and must not contain B)
        return assertions
    return assertions


def extract_input_block(text: str) -> str:
    """Extract the input text from **Input:** section: either > "..." or ``` ... ``` or plain lines."""
    text = text.strip()
    # Block quote: > "multi line" or > line
    if '>"' in text or text.strip().startswith(">"):
        quoted = []
        in_quote = False
        for line in text.split("\n"):
            if re.match(r'^\s*>\s*"', line):
                in_quote = True
                line = re.sub(r'^\s*>\s*"?', "", line).rstrip()
                if line.endswith('"'):
                    quoted.append(line[:-1])
                    break
                quoted.append(line)
            elif in_quote:
                if line.strip().endswith('"'):
                    quoted.append(line.strip()[:-1])
                    break
                quoted.append(line)
        if quoted:
            return "\n".join(quoted)
        # Single line >
        m = re.search(r'>\s*"([^"]*)"', text, re.DOTALL)
        if m:
            return m.group(1).strip()
        m = re.search(r'>\s*(.+)', text)
        if m:
            return m.group(1).strip()
    # Code block
    if "```" in text:
        m = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
        if m:
            return m.group(1).strip()
    # Plain: take first paragraph or up to **Assertions**
    lines = []
    for line in text.split("\n"):
        if line.strip().startswith("**Assertions:**"):
            break
        if line.strip().startswith("-"):
            break
        line = re.sub(r"^\s*>\s*", "", line)
        if line.strip():
            lines.append(line.strip())
    return "\n".join(lines) if lines else text[:2000].strip()


def parse_md(content: str) -> dict[str, list]:
    """Parse full md content. Returns { skill_id: [ cases ] } where each case is { id, input: { text }, assertions }."""
    out = {}
    # Split by ## (skill sections)
    sections = re.split(r"\n##\s+", content)
    for section in sections:
        if not section.strip():
            continue
        lines = section.strip().split("\n")
        skill_id = slug(lines[0].strip())
        if not skill_id or skill_id in ("napomene-za-implementaciju", "napomene"):
            continue
        # Split by ### Case
        case_blocks = re.split(r"\n###\s+Case\s+", section, flags=re.IGNORECASE)
        cases = []
        for i, block in enumerate(case_blocks):
            if i == 0:
                continue  # header part before first case
            block = block.strip()
            if not block:
                continue
            first_line = block.split("\n")[0]
            case_num = re.match(r"(\d+)", first_line)
            if not case_num:
                continue
            case_id = f"case_{case_num.group(1)}"
            rest = "\n".join(block.split("\n")[1:])
            # Find **Input:** and **Assertions:**
            input_section = ""
            assertions_section = ""
            if "**Input:**" in rest:
                inp_start = rest.index("**Input:**") + len("**Input:**")
                if "**Assertions:**" in rest:
                    inp_end = rest.index("**Assertions:**")
                    input_section = rest[inp_start:inp_end]
                    assertions_section = rest[rest.index("**Assertions:**") + len("**Assertions:**") :]
                else:
                    input_section = rest[inp_start:]
            input_text = extract_input_block(input_section)
            # Prepend instruction line if present (line right after **Input:** before > or ```)
            intro = re.match(r"^([^\n>`]+)", input_section.strip())
            if intro and intro.group(1).strip() and not input_text.startswith(intro.group(1).strip()):
                instruction = intro.group(1).strip()
                if instruction and len(instruction) > 5:
                    input_text = instruction + "\n\n" + input_text if input_text else instruction
            assertions = []
            for line in assertions_section.split("\n"):
                line = line.strip()
                if not line or not line.startswith("-"):
                    continue
                parsed = parse_assertion_line(line)
                if len(parsed) > 1:
                    merged = merge_or_assertions(parsed)
                    assertions.extend(merged)
                else:
                    assertions.extend(parsed)
            cases.append({"id": case_id, "input": {"text": input_text}, "assertions": assertions})
        if cases:
            out[skill_id] = cases
    return out


def main() -> int:
    md_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MD
    if not md_path.exists():
        # Try workspace root or Downloads
        alt = WORKSPACE / "30_system/docs" / "SKILLS_evals_all.md"
        if alt.exists():
            md_path = alt
        else:
            print(f"Error: {md_path} not found.", file=sys.stderr)
            return 1
    content = md_path.read_text(encoding="utf-8")
    data = parse_md(content)
    for skill_id, cases in data.items():
        out = {"skill_id": skill_id, "version": "1.0", "cases": cases}
        out_path = EVALS_DIR / f"{skill_id}.json"
        out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {out_path} ({len(cases)} cases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
