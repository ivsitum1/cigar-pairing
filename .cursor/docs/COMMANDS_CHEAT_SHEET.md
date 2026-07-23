# Cheat sheet: komande, skillovi, načini rada

Kratki pregled eksplicitnih okidača iz `00_orchestrator_agent.mdc`, `skills-auto-detect.mdc`, `30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md`, `30_system/docs/SCHOLARLY_WORKFLOW.md` i srodnih pravila.

---

## Autonomija (orchestrator)

| Uključi | Isključi |
|---------|----------|
| `@autonomous`, `AUTONOMOUS ON`, „unattended pipeline” | `AUTONOMOUS OFF` |

Detalji: `.cursor/docs/AGENT_AUTONOMY_AND_PARALLEL.md` (§5 token economics). Kanonski brojevi: `context-optimization.mdc`.

---

## Skillovi

| Što | Kako |
|-----|------|
| **Nametni skill** | `@skill-name` (npr. `@meta-analysis`, `@swiss-cheese`, `@obsidian-wiki-agent`) — vidi `30_system/SKILLS/registry.json` |
| **Automatski** | Opis zadatka koji odgovara triggerima u `skills-auto-detect.mdc` |
| **Isključi** | Nema `@skill-off`. Jedan skill aktivan odjednom; sljedeći skill zamijeni prethodni u pipelineu. Ili jasno reci da ne želiš proceduralni skill. |

---

## Software / PRD / Ralph

| Uključi | Isključi (default) |
|---------|-------------------|
| `Ralph ON`, „Run Ralph loop [N iterations]” | `Ralph OFF` |
| Exploration Mode (spike; i dalje `progress.txt`) | — |

Vodič: `30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md`.

---

## Scholarly (research spec)

| Uključi | Isključi (default) |
|---------|-------------------|
| `LOOP ON`, „run loop” | `LOOP OFF` |

Vodič: `30_system/docs/SCHOLARLY_WORKFLOW.md`.

---

## Pipeline-i

`@pipeline 1` … `@pipeline 7`, `@pipeline 7B` + sinonimi („meta-analysis”, „full lifecycle”, …).  
Uz autonomiju: `@autonomous` + odabrani pipeline.

---

## Brain i greške

| Komanda |
|---------|
| `@brain status` \| `@brain audit` \| `@brain health` |
| `@sync context` |
| `remember this` / `learn this` \| `forget E[ID]` \| `@audit errors` |

---

## Agenti (eksplicitno)

`@STATS_AGENT`, `@WRITER_AGENT`, `@CLINICAL_AGENT`, `@METHODOLOGY_AGENT`, `@CODER_AGENT`, `@QA_AGENT`, `@PROMPT_AGENT`, `@MAINTAINER_AGENT`

(vidi `30_system/behavior_rules/15_agent_roles.md`)

---

## Napomena

Tier 1/2 `.mdc` pravila u Cursoru uključuješ **kontekstom datoteka** ili postavkama projekta, ne ovim chat naredbama.

**Verzija:** 1.0 | **Datum:** 2026-04-10

## Related Hubs

- [Folder index hub](../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
