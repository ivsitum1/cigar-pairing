# Memory hierarchy spec (HORMA + AutoMem)

**Version:** 1.1 | **Last updated:** 2026-07-04  
**Sources:** Agent Harness SkillTree notebook (arXiv:2606.11680); AutoMem ([arXiv:2607.01224](https://arxiv.org/abs/2607.01224)).

---

## AutoMem file-op vocabulary

Memory-as-filesystem ops map to harness actions (see `30_system/SKILLS/clusters/memory-ops/intent.md`). Use these verbs consistently in skills, handoffs, and wiki frontmatter.

| Op | AutoMem intent | Harness path | When to use |
|----|----------------|--------------|-------------|
| **log** | Record step/event | `context_sync --append-log`, trajectory hook | After observation or tool failure; before retry |
| **read** | Retrieve prior state | `memory_hierarchy/index.json`, `solved_lemmas.jsonl`, `MEMORY.md` | Before planning or after context trim |
| **write** | Persist folded knowledge | `context_sync --fold-lemma`, `summaries/*.md` | Sub-goal complete; Swiss gate if global |
| **plan** | Declare sub-goal / phase | `commit.md`, HANDOFF brief, lemma `subgoal` field | Start of long autonomous segment |

### Schema fields (summary nodes)

Optional YAML frontmatter on `summaries/*.md`:

```yaml
memory_op: write          # log | read | write | plan
schema_version: "1.0"
subgoal: "verify PH assumption before Cox model"
provenance: [".agent/solved_lemmas.jsonl#L3"]
token_estimate: 120
```

### Structure-revision loop (outer, harness-only)

AutoMem loop 1 revises **memory scaffolding** (prompts, schemas, vocabulary). In agent-rules this is **proposal-only**:

1. Review `trajectory.jsonl` or `failure_patterns.json`
2. Draft diff to `memory_hierarchy/` layout or cluster `intent.md`
3. Human gate every 3rd `self_harness_propose` iteration — no auto-apply to `.cursorrules`

---

## Layout (`.agent/memory_hierarchy/`)

```
.agent/memory_hierarchy/
  index.json           # summary nodes + provenance pointers
  summaries/           # compact narrative nodes (YAML frontmatter + body)
  raw/                 # optional symlink or path refs to trajectories (not full copy)
```

### `index.json` schema

```json
{
  "nodes": [
    {
      "id": "lemma-001",
      "title": "Folded sub-goal summary",
      "summary_path": "summaries/lemma-001.md",
      "provenance": [".agent/solved_lemmas.jsonl#L12", "20_knowledge/wiki/log.md"],
      "token_estimate": 120,
      "updated_at": "2026-06-24T00:00:00Z"
    }
  ]
}
```

---

## Provenance pointers

- Every summary node MUST list at least one `provenance` path.
- `context_sync.py --fold-lemma --lemma-provenance` writes to `solved_lemmas.jsonl`.
- `context_sync.py --sync-memory-hierarchy` bootstraps index from existing lemmas.
- `fold_lemma` auto-updates `memory_hierarchy/index.json` via `harness/memory_hierarchy.py`.
- Wiki pages may use frontmatter `provenance:` list (see `wiki_chunk_ingest`).

---

## Policy

- Do not replace episodic-first policy ([`MEMORY_MIXTURE_ROUTING.md`](MEMORY_MIXTURE_ROUTING.md)).
- Flat `MEMORY.md` trim remains; hierarchy is additive.
- No auto-promote summary → global brain without Swiss gate.

---

## Related

- [`LIFEHARNESS_4_LAYER.md`](LIFEHARNESS_4_LAYER.md) L4
- [[Agent harness memory and skill tree]]
- [[AutoMem metamemory skill]]
- `30_system/SKILLS/clusters/memory-ops/intent.md`
