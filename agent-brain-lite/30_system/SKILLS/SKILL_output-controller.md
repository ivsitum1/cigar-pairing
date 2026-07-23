---
name: output-controller
description: >
  Zero-tolerance terminal output gate before deliverable release. Use when user says output gate,
  output check, kontrola outputa, provjeri output, final gate, zero tolerance, @OUTPUT_CTRL,
  @output-gate, or before deliver/submit/isporuči on manuscript, analysis, or code bundle.
  Validates system rules + project author_claims. WARN equals FAIL. NOT code review with majors
  (CODE_QA) and NOT skill routing (SkillLens verifier).
version: 1.0
last_updated: 2026-07-08
---

# Output Controller

## When to use

Terminal validation **after** a deliverable exists. Producer subagent (STATISTICS, WRITING, CODE_IMPL) has finished; Output Controller runs before user sees final files.

## Honesty and grounding

- High-risk: fabricated citations, untraceable numbers, figure-code drift, project rule bypass.
- Mandatory checkpoints: CLI exit 0, every layer PASS, no `[BLANK]` in deliverable prose.
- `[EXTRACTED]` from CLI JSON and file reads; `[INFERRED]` only for semantic citation support (flag `[NEEDS VERIFICATION]` if unsure → FAIL).

## Workflow

### Step 1 — Bind scope

1. Identify deliverable path(s) and type (manuscript / analysis / code / figure).
2. Load project id from context or ask once if manuscript under `10_projects/projects/<id>/`.
3. Select `--domain`: `statistics` | `writing` | `code` | `methodology`.

### Step 2 — Run deterministic gate

```bash
python 40_operations/scripts/output_controller_gate.py <path> \
  --domain <domain> \
  [--project <id>] \
  --gate --json
```

If exit code ≠ 0 → **STOP**. Parse JSON `checks[]` for failing items.

### Step 3 — Semantic layers (2–5)

Run per `09_output_controller.md`:

- Citations: real + supportive; project pack via `author_claims_check.py <path> --project <id> --gate`
- Numbers: trace each; reconcile N
- Figures: compare to source script output

Any ambiguity → FAIL (zero tolerance).

### Step 4 — Domain checklist

Apply layer 5 table from role file. Cross-check `99_error_memory.mdc` relevant category.

### Step 5 — Verdict

Emit role-file report format. Status `RELEASE` only if all layers PASS.

If FAIL: hand back to producer with numbered blockers; do not soften language.

### Step 6 — Critical analyses

If deliverable is primary outcome, meta-analysis pooled estimate, or pre-publication manuscript: confirm Swiss Cheese was run when mandatory (`verification.mdc`). Missing mandatory Swiss Cheese → FAIL.

### Step 7 — Session hook (automatic)

On session end, `.cursor/hooks/output_gate_lifecycle.py` auto-gates flagged deliverables. Check `.agent/output_gate/last_report.json` if the hook reported BLOCKED. Opt-out: `OUTPUT_GATE_HOOK_DISABLED=1`.

## Edge cases

| Case | Action |
|------|--------|
| Chat-only output (no file) | Pipe text to `output_controller_gate.py` via stdin `--domain` |
| Multiple files | Gate each; all must pass |
| User override "ship anyway" | Document override in chat; do not mark RELEASE |
| Empty deliverable | FAIL at Layer 1 |

## Examples

**Input:** "Provjeri output prije isporuke — `03_output/manuscript_v2.md`, projekt sedacija-ecmo"  
**Output:** Run CLI with `--project sedacija-ecmo --domain writing --gate`; full layer report; BLOCKED or RELEASE.

**Input:** "@output-gate Welch t-test rezultati u chatu"  
**Output:** stdin gate `--domain statistics`; FAIL if p without CI/effect size.

## Related

- `agents/09_output_controller.md`
- `.cursor/rules/output-controller-agent.mdc`
- `reviewer-agent.mdc` (semantic subset)
- `SKILL_swiss-cheese.md`
