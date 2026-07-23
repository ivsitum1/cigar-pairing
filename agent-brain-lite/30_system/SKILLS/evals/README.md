# Skill Evals – Binary Assertions for Autonomous Optimization

Evals in this folder are used by the **Autonomous Skill Optimization Loop**: the agent runs a skill against test cases, evaluates binary (True/False) assertions on the output, and iteratively improves the skill until pass rate reaches 100% or the process is interrupted.

**Location:** One JSON file per skill: `30_system/SKILLS/evals/<skill_id>.json`  
**Example:** `30_system/SKILLS/evals/avoid-ai-formulations.json`

---

## Schema: `evals.json`

```json
{
  "skill_id": "<id from registry>",
  "version": "1.0",
  "cases": [
    {
      "id": "case_1",
      "input": { "text": "..." },
      "assertions": [
        { "type": "<assertion_type>", "value": "<type_specific>", "description": "Human-readable" }
      ]
    }
  ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `skill_id` | Yes | Must match the skill id in `30_system/SKILLS/registry.json` (e.g. `avoid-ai-formulations`). |
| `version` | Yes | Schema version; use `"1.0"`. |
| `cases` | Yes | Array of test cases. |
| `cases[].id` | Yes | Unique identifier for the case (e.g. `case_1`). |
| `cases[].input` | Yes | Input for the skill. Use `{ "text": "..." }` for writing skills; other shapes allowed for future use. |
| `cases[].assertions` | Yes | Array of binary assertions evaluated on the skill output. |

---

## Assertion types (all binary: Pass / Fail)

Assertions are evaluated **on the model output** produced when the skill is applied to `input`. Every assertion must resolve to True (pass) or False (fail). No subjective scoring.

| Type | Meaning | `value` format | Pass when |
|------|---------|----------------|-----------|
| `contains` | Output must contain the string | String | `value in output` |
| `not_contains` | Output must not contain the string | String | `value not in output` |
| `regex_match` | Output (or a line) matches pattern | Regex string | `re.search(value, output)` |
| `regex_not_match` | Output must not match pattern | Regex string | `not re.search(value, output)` |
| `word_count_below` | Word count strictly below N | Number | `word_count(output) < value` |
| `word_count_above` | Word count strictly above N | Number | `word_count(output) > value` |
| `word_count_between` | Word count in [min, max] inclusive | `[min, max]` | `min <= word_count(output) <= max` |
| `last_sentence_not_question` | Last sentence does not end with `?` | Omitted or `true` | Last non-empty sentence does not end with `?` |

**Word count:** Split on whitespace; empty segments ignored. No stipulation on how the runner strips leading/trailing or normalizes spaces.

**Optional field:** `description` is for logs and debugging; it is not used for evaluation.

---

## Example

```json
{
  "skill_id": "avoid-ai-formulations",
  "version": "1.0",
  "cases": [
    {
      "id": "case_1",
      "input": { "text": "It is important to note that in order to achieve better outcomes, we must consider several factors." },
      "assertions": [
        { "type": "not_contains", "value": "It is important to note that", "description": "No 'It is important to note that'" },
        { "type": "not_contains", "value": "in order to", "description": "No 'in order to'" },
        { "type": "word_count_below", "value": 300, "description": "Under 300 words" }
      ]
    }
  ]
}
```

---

## Pass rate

- **Per run:** `pass_rate = (total assertions passed) / (total assertions)`.
- The optimization loop compares this value across iterations and keeps only edits that **strictly improve** the pass rate (or reaches 100% and stops).

---

## What to avoid

- **Subjective assertions** (e.g. “sounds natural”, “appropriate tone”) cannot be evaluated deterministically; keep those for human review.
- **Fragile regex** that depends on exact punctuation or spacing may flake; prefer simple strings for `contains` / `not_contains` when possible.

---

## Related files

- **Runner:** `40_operations/scripts/skill_eval_runner.py` – loads skill + evals, runs LLM per case, evaluates assertions, outputs pass rate.
- **Agent loop:** `30_system/docs/SKILL_OPTIMIZATION_AGENT.md` – when to run, `SKILL_ID`, autonomy rules, log location, commit convention.
- **Optional generator:** `40_operations/scripts/generate_evals_from_skill.py` – generate initial `evals.json` from a skill file (Phase 0).

## Related Hubs

- [Folder index hub](../../docs/FOLDER_INDEX.md)
- [All notes index](../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../docs/GRAPH_CONNECTIVITY_MAP.md)
