# Grill-me injection heuristic (memory hook)

## What this is

This is **only** the rule set for **when the Cursor hook prefetches memory** into `additional_context` on `beforeSubmitPrompt`. It answers: “Should we retrieve and attach memory snippets before this user message is processed?”

It is **not**:

- **Not** the conversational **SKILL_grill-me** workflow (design-tree interview in chat). That skill governs *how the assistant talks to you*, not this hook.
- **Not** `.cursor/rules` or orchestrator routing rules.
- **Not** a guarantee that the model will “grill” you; it only brings **retrieved memory** into context when cues match.

Naming in code and docs uses **injection cues** or **prompt cues**, not “grill rules”, to avoid confusion.

## Canonical trigger source

**Primary:** `30_system/SKILLS/registry.json`, skill ids:

- `grill-me` — engineering / PRD alignment triggers
- `research-grill-me` — scholarly / research-spec alignment triggers

All `triggers[]` strings from those two entries are normalized to lowercase and used as **substring** matches against the user prompt (same idea as skill auto-detect, but implemented in `memory_engine/grill_me_inject.py` for the hook).

**Supplement (explicit, small):** phrases that appear in **SKILL_grill-me.md** narrative but are **not** always duplicated in the registry, for example informal “interview me”, “clarify the plan”, and the typo form `grillme`. Listed in code as `SUPPLEMENTAL_INJECTION_CUES` with a comment pointing here.

If `registry.json` is missing or unreadable, the hook falls back to a minimal built-in list so behavior degrades safely.

## Behaviour summary

| Piece | Role |
| ----- | ---- |
| `AGENT_MEMORY_INJECT_ON_GRILL_ME` | Master switch for cue-based inject (default on). |
| Conversation id | When present in hook payload, at most **one** inject per id. |
| No conversation id | At most **one** inject until `.agent/memory/hook_session.json` is cleared or logic reset. |
| Query sent to retrieval | User prompt (truncated) plus stable anchors; see `build_injection_query()` |

## Maintenance

- **Add or change product triggers for users** → edit **registry** `triggers` for `grill-me` / `research-grill-me`, then run `python 40_operations/scripts/skill_registry.py validate` if you use that workflow.
- **Add informal cue only for injection** → extend `SUPPLEMENTAL_INJECTION_CUES` in `memory_engine/grill_me_inject.py` and note one line in this doc under Supplement.

## Hook log tag

When a prefetch runs, the hook may append `memory_prefetch=alignment-cues` to `agent_message` (not “grill-me” wording, to avoid equating this mechanism with the conversational skill).

## Related

- Skill behaviour (conversation): `30_system/SKILLS/SKILL_grill-me.md`, `30_system/SKILLS/SKILL_research-grill-me.md`
- Hook implementation: `.cursor/hooks/memory_lifecycle.py`
- Cue loading and matching: `memory_engine/grill_me_inject.py`
- Env vars table: `30_system/docs/MEMORY_SYSTEM.md`

**Note:** The environment variable `AGENT_MEMORY_INJECT_ON_GRILL_ME` keeps its name for backward compatibility; it controls this **registry-based alignment prefetch**, not the chat interview skill.

## Semantic graph (auto)

- [[Skill gap pipeline]]
- [[Behavior rules hub]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[SKILL_research-grill-me]]
- [[SKILL_grill-me]]
- [[SKILL_write-research-spec]]
- [[Scholarly skill loop]]
- [[SKILL_scholarly-iteration-loop]]
