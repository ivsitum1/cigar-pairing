# Agentic Re-Act OS (extended guide)

**Purpose:** Consolidate the Reason–Act–Observe–Reflect (TAOR) operating model, advanced reasoning modes, persistence hooks, and iteration limits for this workspace.  
**Relationship:** `.cursorrules` already embeds a concise Re-Act operational loop; this document expands patterns without duplicating Tier 0 safety rules. Canonical compact behavior also lives in `30_system/claude.md`.

---

## 1. Roadmap first (planning and exploration)

Before multi-step work:

1. **Investigation** — Map structure (glob), locate symbols (search), read only what is needed.
2. **Implementation** — Smallest verifiable change per step.
3. **Verification** — Tests, scripts, or explicit manual checks.
4. **Summary** — Outcomes, residual risk, open `[TO_CONFIRM]` items.

**Replanning:** If tool output or file contents contradict the plan, pause, revise the roadmap, then continue. Do not accumulate stale assumptions.

---

## 2. TAOR narration policy (token-aware)

**Default (checkpoint-style):** Emit explicit Think → Act → Observe → (brief) Reflect **at checkpoints**:

- Initial roadmap and whenever the plan changes
- After a **batch** of related reads or searches (not after every single line read)
- After tool failures, test failures, or unexpected outputs
- Before and after handoffs (`00_orchestrator_agent.mdc`)
- When escalating after hitting iteration caps

**Verbose mode:** If the user asks for full transparency (e.g. “narrate every step”), expand TAOR accordingly while monitoring context budget (`context-optimization.mdc`).

**Describe:** After substantive actions, one short sentence on what changed and why is enough unless verbose mode is on.

---

## 3. Advanced reasoning modes

### Chain of Thought (CoT)

Use **internally** for: multi-step arithmetic, intricate logic, protocol interpretation, or aligning several constraints before touching tools. Prefer to expose only conclusions and key assumptions to the user unless they asked for derivation.

### Tree of Thought (ToT)

Use for **production-style debugging** and ambiguous failures:

1. List several plausible causes (branches).
2. Rank by likelihood using evidence from logs, stack traces, recent edits.
3. Prune branches contradicted by observations.
4. Test the strongest remaining branch first; avoid fixing multiple hypotheses at once.

Pair ToT with **single-variable changes** where possible so observations remain attributable.

---

## 4. Parallel execution

When subtasks are **independent** (e.g. searching three unrelated paths, unrelated file reads), prefer parallel tool use or Cursor Task fan-out per `.cursor/docs/AGENT_AUTONOMY_AND_PARALLEL.md` and `context-optimization.mdc`. Do not parallelize steps that share mutable state or ordering constraints.

---

## 5. Iteration and stop conditions (canonical)

Two limits coexist; do not conflate them:

| Limit | Source | Meaning |
|-------|--------|---------|
| **5 fix iterations** | `30_system/claude.md`, `.cursorrules` | Same defect line of attack: after five unsuccessful fix cycles, stop and escalate with options and current evidence. |
| **3× same subtask failure** | `agentic-workflow-guardrails.mdc` | Same subtask fails three times → stop retries, summarize root cause, switch approach or ask user. |

If both could apply, **whichever triggers first** wins. Escalation should include: last error text, what was tried, and the smallest next experiment or question.

**Debugging cap note:** External prompts sometimes cite “5–10” iterations; **this repo standardizes on 5** for the same bug-fix loop unless the user explicitly raises the cap for one task.

---

## 6. Persistence and learning

| Kind | Where | Content |
|------|--------|---------|
| Long-term verified facts | `30_system/context/memory.md` | Architecture, verified stack facts, evidence pointers |
| Session / episodic | `.agent/MEMORY.md`, optional `30_system/04_documentation/context/log.md` | Progress, handoffs, OTA-style notes when project uses that tree |
| Corrected playbooks | `.agent/SOPs/strategies.md` | **How** a class of problems was solved after feedback (procedural), not one-line anti-patterns |
| Corrections / anti-patterns | `99_error_memory.mdc`, `.cursor/errors/error_log.jsonl` | Promoted mistakes and fixes |

After a successful non-trivial fix or explicit user feedback on approach, append a short strategy entry when it will **reuse** (template in `.agent/SOPs/strategies.md`).

---

## 7. Quality and safety

- **Reflection:** Before marking done: Does this satisfy requirements? What is unverified? What would falsify the conclusion?
- **Sandbox:** Risky refactors → branch or isolate; run targeted tests before merge.
- **Honesty:** `.cursorrules` claim classification and `[BLANK]` protocol override narrative polish.

---

## 8. Related docs

- Autonomy and parallelism: `.cursor/docs/AGENT_AUTONOMY_AND_PARALLEL.md`
- MCP vs CLI tradeoffs: `.cursor/docs/CLI_VS_MCP_AGENT_NATIVE.md`
- MCP vs Skills layering: `.cursor/docs/MCP_AND_SKILLS_LAYERS.md`
- Orchestrator and pipelines: `.cursor/rules/00_orchestrator_agent.mdc`
- Skill entry point (optional load): `30_system/SKILLS/SKILL_agentic-react-os.md`

### Navigable links (Obsidian)

- [Agent autonomy and parallel work](AGENT_AUTONOMY_AND_PARALLEL.md)
- [CLI vs MCP for agent-native workflows](CLI_VS_MCP_AGENT_NATIVE.md)
- [MCP and Skills layers](MCP_AND_SKILLS_LAYERS.md)
- [Skill: Agentic Re-Act OS](../../30_system/SKILLS/SKILL_agentic-react-os.md)
- [Strategy playbooks (SOPs)](../../.agent/SOPs/strategies.md)
