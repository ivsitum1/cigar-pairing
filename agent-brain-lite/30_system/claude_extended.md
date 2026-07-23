# Claude Master State Share — Workflow Extensions

This section defines stable operating behavior for autonomous work in this repository.
Load on demand from `30_system/claude.md` for long-running agentic sessions.

## Related Nodes

- [[README]]
- [[.cursor/docs/INDEX]]
- [[30_system/docs/GRAPH_CONNECTIVITY_MAP]]
- [[30_system/docs/AUTOMATION_INDEX]]
- [[20_knowledge/wiki/index]]
- [[30_system/context/user]]
- [[30_system/context/memory]]
- [[30_system/context/soul]]

## Workspace Contract

- Root contexts:
  - `30_system/context/user.md`
  - `30_system/context/soul.md`
  - `30_system/context/memory.md`
- Modular procedures live in `30_system/SKILLS/` and `skills/`.
- Session and execution traces live in `40_operations/logs/`.

## Agentic Search (Codebase Investigation)

Do active terminal-style exploration before changing code.

### Search Order

1. Map structure with `glob` patterns.
2. Trace behavior and symbols with ripgrep (`rg`).
3. Read only relevant files; avoid broad file dumps.
4. Confirm current branch state before risky edits.

### Investigation Output

For non-trivial tasks, produce a short investigation note:

- probable root files
- observed patterns/conventions
- constraints and unknowns

## Plan-Execute-Verify (TDD-first default)

For implementation and bugfix tasks:

1. Plan:
   - define acceptance criteria
   - identify target files and test files
2. Execute:
   - write or update tests first when feasible
   - implement minimal change to satisfy tests
3. Verify:
   - run focused tests first, then broader checks if needed
   - summarize what passed, what remains, and residual risk

If tests are impossible or unavailable, state why and provide a manual verification checklist.

## Re-Act Loop

Use Think -> Act -> Observe -> Reflect per step.
For complex defects, cap fix attempts at 5 iterations, then escalate with options.

## Context Management and Compacting

When session context becomes crowded:

1. Write a compact handoff note to `40_operations/logs/compact-[YYYY-MM-DD-HHMM].md`:
   - completed actions
   - key decisions
   - pending tasks
   - blockers
2. Continue from that compact summary rather than replaying full history.

## Terminal-First Operations

Prefer CLI workflows for reproducibility:

- git for source control
- pytest for tests
- Rscript for R validation scripts
- gh for GitHub operations when needed

Never run destructive commands without explicit user confirmation.

## Memory Discipline

### Episodic

- Keep current session steps and outcomes in concise updates.

### Long-term

- If a stable architectural fact is verified, append it to `30_system/context/memory.md` with evidence.
- Never store guesses as long-term memory.

### Strategy playbooks

- After non-trivial fixes or strategy-level user feedback, append reusable steps to `.agent/SOPs/strategies.md` (see `.cursor/docs/AGENTIC_REACT_OS.md`).

## Conversational Re-Act

If the request is ambiguous, ask one precise clarification question before expensive tool usage.

## Three Project-Specific Improvements (Applied)

1. Dual-stack execution guardrail (R and Python):
   - Always identify whether a task belongs to `40_operations/R/` statistical scripts or Python tooling before edits.
   - Verification command must match stack (`Rscript ...` vs `pytest ...`).

2. Test runner optimization policy (pytest plugin-heavy environment):
   - Use targeted test selection first (single file/test), then broaden.
   - Avoid full-suite runs for small changes unless requested.

3. Rule layering discipline (high rule density repo):
   - Prefer minimal active context per task.
   - Load only directly relevant rule/skill files to reduce context rot and conflicting guidance.

## LLM Wiki Mode (Karpathy-style Knowledge Management)

When user requests wiki ingestion or knowledge-base updates, switch to this mode.

### Wiki Architecture

- Input folder: `00_inbox/raw/`
- Knowledge base root: `20_knowledge/wiki/`
- Required wiki subfolders:
  - `20_knowledge/wiki/entities/`
  - `20_knowledge/wiki/concepts/`
  - `20_knowledge/wiki/sources/`
  - `20_knowledge/wiki/analysis/`
- Required operational files:
  - `20_knowledge/wiki/index.md`
  - `20_knowledge/wiki/log.md`

### Ingestion Protocol

When processing files from `00_inbox/raw/`:

1. Do not produce only a flat summary.
2. Decompose material into linked notes across `entities`, `concepts`, `sources`, and `analysis`.
3. Use Obsidian-style backlinks `[[Node Name]]` to build a navigable graph.
4. Update `20_knowledge/wiki/index.md` with new or changed key nodes.
5. Append an entry to `20_knowledge/wiki/log.md` with inputs, outputs, and decisions.

### Backlink and Canonicalization Rules

- Reuse existing canonical nodes when possible; avoid duplicate concept pages.
- If aliases exist, keep one canonical note and link aliases to it.
- Prefer short atomic notes with high link density over long monolithic notes.

### Wiki Health Check (Linting)

On request to run "wiki lint" or "health check", verify:

- broken or missing internal links
- orphan notes (no inbound and no outbound links)
- duplicate or near-duplicate concept/entity pages
- empty stubs without source grounding
- missing updates in `20_knowledge/wiki/index.md` or `20_knowledge/wiki/log.md` after ingestion

Then return:

- issues list (severity + file path)
- proposed fixes
- priority order for remediation
