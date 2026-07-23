# Machine Primary vs Secondary relevance

**Version:** 2.0  
**PRD:** [prd_machine.json](prd_machine.json) US-12, [prd_machine_v1.1.json](prd_machine_v1.1.json)  
**Grill-me log:** `.agent/task/machine_grillme_v1.1_2026-06-29.md`  
**Metaphor:** Person of Interest — Primary threats need immediate routing; Secondary items wait (digest count only).

## Primary (never defer)

Execute in the current turn. Do not batch for weekly digest.

| ID | Category | Rule |
|----|----------|------|
| P1 | User correction / error memory | Explicit correction → fix now + `error_log.jsonl` + promotion check |
| P2 | Primary analysis | Pre-specified primary outcome, MA pooled estimate, survival primary, MS-bound inference. Exploratory EDA without MS intent → Secondary unless user elevates |
| P3 | Verification gates | Swiss Cheese before Results text, before publication, after primary-outcome analysis |
| P4 | PHI / clinical safety | Names, DOB/admission dates, MRN/IDs, free-text identifiers, unsourced dosing → stop. Aggregated N OK |
| P5 | Integrity | N mismatch across abstract/tables/flow → stop. Unverified MS citation → stop. Chat-only typos → warn |
| P6 | Blocking unknowns | Execution blocked → hard stop + one question. Advice-only → `[TO_CONFIRM]` |
| P7 | Destructive / irreversible | rm -rf, force push, overwrite canonical MS, mass delete, publish without confirm. User-requested commit OK |

## Secondary (deferrable)

Surface as **proposal count only** at brain session start when `.agent/task/machine_digest_YYYY-WW.md` exists. Sensor breakdown stays in digest only.

| ID | Category | Examples |
|----|----------|----------|
| S1 | Skill scout proposals | arXiv / GitHub / digest upgrade ideas |
| S2 | Wiki lint / graph hygiene | Broken wikilinks, tag drift |
| S3 | arXiv / AI news summaries | Unless user explicitly asks in this session |
| S4 | Dreaming frameworks | Hypothesis files until user invokes dreaming |
| S5 | Memory maintenance proposals | `learning_run_*.json` suggest-only items |
| S6 | Non-blocking tooling | Formatting, index updates, doc typos |

## Session start (brain repo only)

If latest `machine_digest_*.md` exists and user did not ask for digest content:

> Secondary queue: **N** upgrade proposals in `machine_digest_YYYY-WW.md` (pending review). Say "open machine digest" for detail.

Do not inject Secondary bodies into prompt automatically.

## Escalation Secondary → Primary

| Trigger | Action |
|---------|--------|
| User keyword | `primary`, `urgent`, `blocking`, `@machine primary` |
| User digest command | `open machine digest`, `@machine digest` → summarize on request (not silent inject) |
| Same Secondary item failed twice | Promote to Primary on third occurrence |
| User approves digest proposal | Primary implementation task for that item |
| Deadline in user message | Relevant Secondary items become Primary for that session |

## Orchestrator routing

1. Classify request against tables above before subagent selection.
2. Primary always wins over Secondary when both match.
3. MIXED pipelines: Primary domain leads (see orchestrator MIXED resolution).

## Changelog

- **v2.0 (2026-06-29):** Grill-me v1.1 — narrowed P2, extended P7, stop-the-line P5, proposal-only session count, digest command escalation.

## Related

- [THE_MACHINE.md](THE_MACHINE.md)
- `.cursor/rules/machine-relevance.mdc`
