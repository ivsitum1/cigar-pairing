---
name: agentic-react-os
description: Use for Agentic OS and full Re-Act operating mode — roadmap first, checkpoint TAOR, CoT vs ToT, iteration caps, memory and strategies hooks, parallel fan-out. Triggers include Agentic OS, Re-Act OS, Think Act Observe Reflect, TAOR, Tree of Thought debugging, verbose agent loop, @agentic-os.
version: 1.0
last_updated: 2026-05-10
domain: engineering
tokens: ~650
triggers:
  - Agentic OS
  - Re-Act OS
  - TAOR
  - Think Act Observe Reflect
  - Tree of Thought
  - verbose agent loop
  - checkpoint planning
  - @agentic-os
requires_packages: []
reference_files:
  - .cursor/docs/AGENTIC_REACT_OS.md
  - .cursor/docs/CLI_VS_MCP_AGENT_NATIVE.md
pipeline_position: []
---

# Skill: Agentic Re-Act OS

## When to use

- User asks for **Agentic OS**, **Re-Act** execution discipline, **TAOR**, or explicit **Tree of Thought** debugging.
- Multi-step codebase work where planning, stop conditions, and memory hooks must be explicit.
- User wants **verbose** step narration (override default checkpoint-only TAOR until context pressure requires compaction).

## Procedure

1. **Load reference:** Read `.cursor/docs/AGENTIC_REACT_OS.md` (full patterns). Load `.cursor/docs/CLI_VS_MCP_AGENT_NATIVE.md` only if the task involves API integration, MCP bloat, or CLI design.
2. **Roadmap:** Emit Investigation → Implementation → Verification → Summary before heavy tool use; replan on contradiction.
3. **TAOR:** Default **checkpoint-style** narration per AGENTIC_REACT_OS; switch to verbose if user requested.
4. **Reasoning:** Use **CoT** internally for logic-heavy steps; use **ToT** for ambiguous production defects (branch hypotheses, prune with evidence).
5. **Stop conditions:** Same bug-fix loop **max 5** iterations; same subtask failure **max 3** (see AGENTIC_REACT_OS table); escalate with evidence.
6. **Persistence:** Append verified facts to `30_system/context/memory.md`; session notes to `.agent/MEMORY.md`; reusable post-fix playbooks to `.agent/SOPs/strategies.md`.
7. **Parallelism:** Use parallel tools or Task fan-out only for independent workstreams (see `AGENT_AUTONOMY_AND_PARALLEL.md`).

## Zoom-out (skills-main)

When the user is unfamiliar with a code area, go up one abstraction level: map relevant modules, callers, and data flow using `UBIQUITOUS_LANGUAGE.md` vocabulary. Do not edit until the map is confirmed or evidence from the repo supports the next step.

## Introspection after failure (ECC pattern)

After a failed fix iteration, emit a short introspection block: what was tried, what evidence contradicted it, what remains unknown. Cap fix loops at 5 per AGENTIC_REACT_OS; escalate with options instead of repeating the same edit.

## Conflicts

- Does not replace domain skills (statistics, writing). Load **one** Tier 3 skill at a time; unload before loading e.g. `ralph-loop` or scholarly loop unless user sequences them.

## Honesty and grounding

- Tag claims per `.cursorrules`. Do not record guesses in `memory.md` or `strategies.md`.

## Verification

- [ ] Roadmap updated when observations contradict plan
- [ ] Iteration caps respected or user explicitly approved override
- [ ] Memory/strategy files updated only with verified or user-confirmed content

## Related

- [Cursor workspace router](../../.cursor/docs/INDEX.md) (Tier 0 rules and orchestrator entry)
- [Agentic Re-Act OS (full guide)](../../.cursor/docs/AGENTIC_REACT_OS.md)
- [CLI vs MCP (agent-native tooling)](../../.cursor/docs/CLI_VS_MCP_AGENT_NATIVE.md)
- [Strategy playbooks (informal SOPs)](../../.agent/SOPs/strategies.md)
- [Compact state share](../claude.md)

## Skill reference graph (auto)

- [[AGENTIC_REACT_OS]]
- [[CLI_VS_MCP_AGENT_NATIVE]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
