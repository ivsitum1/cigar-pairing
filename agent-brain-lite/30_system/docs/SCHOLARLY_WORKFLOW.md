# Scholarly workflow (research spec + iteration loop)

**Purpose:** The same *discipline* as software PRD + Ralph—external memory, `passes` flags, append-only progress—but for **statistics, manuscripts, and book chapters**. Use this path when you are not building application features.

**Not the same as:** `30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md` (code, TDD, `30_system/docs/prd.json`).

---

## Artifacts

| Artifact | Typical path | Role |
|----------|----------------|------|
| Research spec | `30_system/docs/research-spec.json` (or `.md`) | Source of truth: question, design, analysis summary, outline, `passes` |
| Progress | `30_system/docs/scholarly-progress.txt` | Append-only log between sessions |
| Templates | `30_system/docs/templates/research-spec.schema.json`, `research-spec.example.json`, `scholarly-progress.template.txt` | Bootstrap |

Optional: mirror key entries in `30_system/04_documentation/context/log.md` if your project already uses that convention.

---

## Skills (order)

1. **SKILL_research-grill-me** — Align on PICO, design, outlet, reporting standard.
2. **SKILL_write-research-spec** — Lock `research-spec.json` / `.md` with `passes` fields.
3. **SKILL_research-spec-to-milestones** — Order milestones, `blocked_by`, tracer bullets.
4. **SKILL_scholarly-iteration-loop** — **LOOP ON**: one milestone per iteration; validate (Swiss Cheese when required); append progress; commit.

Invoke by name or trigger phrase; registry: `30_system/SKILLS/registry.json` (domain `scholarly`).

---

## Modes

| Mode | Trigger |
|------|---------|
| LOOP OFF | Default |
| LOOP ON | User says "LOOP ON" or "run loop" |

When you **start describing a task**, the agent should help you **create or fill `30_system/docs/research-spec.json` early** (from templates), not only after a long planning phase. See **SKILL_write-research-spec** — “First steps when the user starts describing a task.”
| Exploration | Extra analyses or drafts; still log to progress file |

---

## Validation (instead of TDD)

- **SKILL_swiss-cheese** for critical analyses and before major writing transitions when rules require it (`verification.mdc`, orchestrator).
- Reproducible scripts, effect sizes + CI, no fabricated citations.

---

## Brain vs project

If **agent rules** is attached read-only to another repo, create `30_system/docs/research-spec.json` in the **research project**, not inside the brain folder.

---

## Cross-reference

- Pipelines: `30_system/behavior_rules/22_pipeline_and_refinement.md`
- MCP vs skills: `.cursor/docs/MCP_AND_SKILLS_LAYERS.md`
- Engineering agentic flow: `30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md`

## Related Hubs

- [Folder index hub](FOLDER_INDEX.md)
- [All notes index](ALL_NOTES_INDEX.md)
- [Graph connectivity map](GRAPH_CONNECTIVITY_MAP.md)
