# Distillation trace protocol

Phase 0 of the **Fable → md-file-system** distillation plan. Defines how full
reasoning traces are captured (notebook step 1) and cleaned (step 2) so they can
be authored into `behavior_rules/` and `SKILLS/` (step 3 = Phase 1) and used to
grade a student model on-policy (Phase 2).

> Source recipe: NotebookLM "The AI Frontier news" — *6-step plan to capture
> Fable 5's intelligence*. Here the "student" is this markdown file system plus
> whatever model reads it, not a trained weights model.

## How this differs from `trajectory_rl`

| | `trajectory_rl` (TRAJECTORY_EMIT_PROTOCOL.md) | distillation traces (this doc) |
|---|---|---|
| Purpose | RL reward / eval — *did the tool succeed* | rule authoring — *how the task was solved* |
| Content | metadata only, **no PHI, no prompts** | full Context→Reasoning→Action→Outcome |
| Storage | `90_archive/artifacts/<run_id>/trajectory.jsonl` | `.agent/distillation/raw/` (gitignored) |
| Commit? | yes (metadata is safe) | only after PHI review → corpus |

They are complementary layers, not competitors: RL tells you *which* traces are
worth distilling; this layer holds the *substance* to distill from.

## Record schema (one JSON object per trace)

```json
{
  "schema_version": 1,
  "trace_id": "dtr_20260706_062058_add79a90",
  "ts": "2026-07-06T06:20:58+00:00",
  "source_model": "claude-fable-5",
  "task_domain": "biostatistics",
  "tags": ["glm", "robust-se"],
  "context":   "the situation / prompt the task started from",
  "reasoning": "why, not just what — the reasoning trace",
  "actions": [
    {"tool": "Bash", "intent": "run statsmodels fit", "result_summary": "converged, OR=1.8", "success": true}
  ],
  "outcome":   {"success": true, "verification": "pytest green; OR matches hand calc"},
  "clean": true,
  "phi_hits": [],
  "phi_reviewed": false,
  "promotable": true
}
```

`context → reasoning → actions → outcome` is the ChatML analogue from the
notebook (**Context → Reasoning → Action**), plus `outcome` so Phase 2 can grade
a student attempt against the recorded target.

## Cleaning (notebook step 2)

`distillation/clean.py::clean_text` strips, before a trace is written:

- UTF-8 BOM (the same bug the memory capture hook was patched for),
- ANSI / OSC escape sequences and spinner glyphs,
- rate-limit / quota / retry warning lines (harness noise, not model output),
- box-drawing menu chrome lines,
- runs of 3+ blank lines.

> If you don't clean, the student learns the noise as signal.

## PHI / PII safety (clinical workspace)

`distillation/clean.py::scrub_phi` redacts emails, phone-like runs, 7+ digit IDs
(MRN/OIB), and dotted dates, and returns the categories it hit. Any trace with
`phi_hits` is written with `promotable: false` and `phi_reviewed: false`.

**Gate:** a trace may be promoted to the committed corpus only after a human sets
`phi_reviewed: true` and confirms `promotable`. Raw traces never leave the
gitignored `.agent/distillation/raw/` on their own.

## Capture

Python:

```python
from distillation.emit import Action, CaptureRecord, capture
capture(CaptureRecord(
    context="...", reasoning="...",
    actions=[Action(tool="Bash", intent="run tests", result_summary="12 passed")],
    outcome={"success": True, "verification": "pytest green"},
    task_domain="python", tags=["tdd"],
))
```

CLI (also accepts the record on stdin):

```bash
python 40_operations/scripts/distillation_capture.py --json --record '{"context":"...","outcome":{"success":true}}'
```

Disable capture: `DISTILLATION_CAPTURE_DISABLED=1`.

## Hybrid capture (hook + agent enrichment)

**Automatic skeleton:** `.cursor/hooks/distillation_lifecycle.py` registers on
`sessionStart`, `postToolUse`, `sessionEnd`, and `stop` (see `.cursor/hooks.json`).
It accumulates tool metadata and on session end writes a skeleton trace:

- `context` — placeholder (agent must enrich)
- `reasoning` — empty
- `actions` + `outcome` — from hook payload
- `skeleton: true`, `enrichment_status: "pending"`, `promotable: false`

**Agent enrichment:** Tier-0 rule `distillation-hybrid.mdc` instructs the agent to
enrich promising skeletons with reasoning and re-capture (or promote after PHI
review). Full traces remain manual via CLI when you want immediate richness.

| Layer | Who writes reasoning | When |
|-------|---------------------|------|
| Hook skeleton | nobody (empty) | every session end |
| Agent enrich | agent in normal loop | after substantive tasks |
| Manual CLI | you or agent | on demand |

## Storage layout

```
.agent/distillation/raw/traces.jsonl     # append log (gitignored, content-bearing)
.agent/distillation/raw/<trace_id>.json  # one file per trace (gitignored)
20_knowledge/distillation/corpus/*.md    # curated, PHI-reviewed cards (committed) — Phase 1 input
```

## Phase 1 — Promote to corpus

After enrichment and PHI review, promote a trace to a committed corpus card:

```bash
# List raw traces and readiness
python 40_operations/scripts/distillation_promote.py --list

# Enrich a hook skeleton (agent or manual)
python 40_operations/scripts/distillation_enrich.py \
  --trace-id dtr_YYYYMMDD_HHMMSS_xxxxxxxx \
  --context "what the task was" \
  --reasoning "why this approach"

# Promote (human PHI gate required)
python 40_operations/scripts/distillation_promote.py \
  --trace-id dtr_YYYYMMDD_HHMMSS_xxxxxxxx \
  --phi-reviewed
```

Output: `20_knowledge/distillation/corpus/card_<domain>_<slug>.md` with Context →
Reasoning → Action → Outcome sections and a **Distills to** line for authoring
`behavior_rules/` or `SKILLS/` (Phase 2 grades student attempts against `outcome`).

Promotion updates the raw `.json` with `promoted_to` and `phi_reviewed: true`.
Skeleton traces with `enrichment_status: pending` are rejected until enriched.

## Next phases

- **Phase 2 — On-policy:** a cheaper/local model attempts a task under the rules;
  Fable grades the attempt against `outcome` and rewrites the rule. Reuses
  `SKILLS/evals/` + the self-eval learning loop.
- **Phase 3 — Quantize & run:** compact rules to the Tier-0 context budget so any
  local model runs them offline.

## Related

- [TRAJECTORY_EMIT_PROTOCOL.md](TRAJECTORY_EMIT_PROTOCOL.md) — the PHI-free RL layer
- [14_learning_loop.md](../behavior_rules/14_learning_loop.md) — task-outcome learning
- `40_operations/python/distillation/` — implementation
- `40_operations/scripts/distillation_capture.py` — manual capture CLI
- `40_operations/scripts/distillation_enrich.py` — skeleton enrichment
- `40_operations/scripts/distillation_promote.py` — corpus promotion
- `40_operations/tests/distillation/test_capture.py` — contract tests
