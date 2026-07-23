# Model capability tiers (Cursor)

**Purpose:** Route **planning** to stronger models and **execution** to cheaper ones. Tiers are **capability classes**, not fixed product names — update the mapping when providers ship new models.

**Last updated:** 2026-07-08

---

## Tiers

| Tier | Role | Use for |
|------|------|---------|
| **P — Planner** | Deep reasoning, architecture, trade-offs | Plan mode; grill-me; wargame; refactor design; statistical/SAP design; ambiguous specs; pipeline design; complex bug diagnosis |
| **E — Executor** | Reliable implementation after plan is fixed | Agent mode execution; edits; tests; MCP loops; skill eval runs; applying an approved plan |
| **F — Fast** | Cheap throughput on bounded tasks | Bulk format/convert; simple retrieval summaries; repetitive file ops when steps are explicit |

**Do not** use **F** for primary planning. **Do not** use **E** for initial architecture on non-trivial scope when **P** is available.

---

## Current mapping (examples only)

Refresh when Cursor or Anthropic/OpenAI/Google ship new models. User override always wins.

| Tier | Examples (2026-07) |
|------|---------------------|
| **P** | Claude Fable 5, Opus (incl. thinking/high), Gemini Pro thinking, GPT Codex high |
| **E** | Sonnet, Composer balanced, mid-tier Codex |
| **F** | Haiku, Flash, mini/nano tiers |

Canonical editable list: `30_system/docs/MODEL_CAPABILITY_TIERS.md` (this file section below).

---

## Workflow rules

1. **Plan mode** → default **Tier P** for the full session.
2. **Agent mode — complex task** (≥3 dependent steps, orchestrator refactor, rules/skills/MCP, clinical/statistical inference):
   - **Plan phase:** Tier **P** (or tell user to switch to P before planning).
   - **Execute phase:** Tier **E** after plan is written to `.agent/task/` or user confirms.
3. **Agent mode — trivial** (single-file fix, lookup, formatting) → **E** or **F** OK without separate P pass.
4. **Handoff / Task subagents:** state tier in handoff: `[HANDOFF …] Context: Tier E execute; plan at .agent/task/plan_<id>.md`.
5. **Distillation:** P generates reasoning traces; E (or local student) executes on-policy attempts — see `DISTILLATION_TRACE_PROTOCOL.md`.

---

## Escalation

- Execution stuck after 2 failed attempts on same plan step → pause and recommend **P** replan (do not silently keep burning E tokens).
- Never downgrade a **FULL** reasoning task to **F** for speed.

---

## Maintenance

When you adopt a new flagship or budget model, update the table above and `user.md` § Model preferences if needed. Do not hardcode model names in `.cursor/rules/` except in this doc as **examples**.
