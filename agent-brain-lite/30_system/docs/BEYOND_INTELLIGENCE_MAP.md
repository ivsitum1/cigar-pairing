# Beyond Intelligence — incorporation map

Notebook: `b8896972-fd70-40ca-9456-15c8ff41e72a`  
URL: https://notebooklm.google.com/notebook/b8896972-fd70-40ca-9456-15c8ff41e72a  
Gate report: `outputs/notebooklm/beyond_intelligence_gate_report.json`  
External verification: `30_system/docs/notebooklm_beyond_intelligence_external_verification.json`  
PRD: `30_system/docs/prd_beyond_intelligence_incorporation.json`

## Central thesis (harness interpretation)

LLM agent memory fails in three separable operations — **summarization**, **storage**, **retrieval** — not as a single "bad memory" score. Diagnostic benchmarks (MemFail) and episodic-first harness design reduce silent consolidation errors.

## Priority matrix

| ID | Concept | Repo / paper | Agent-rules artifact | Priority |
|----|---------|--------------|----------------------|----------|
| BI-1 | Three memory operations + failure attribution | [MemFail](https://github.com/ishirgarg/MemFail) arXiv:2605.26667 | `failure_mode` tags, `memfail_adapter.py` | P1 |
| BI-2 | Episodic-first — avoid aggressive abstraction | Faulty Memory / AutoMem themes | `TRAJECTORY_RL_POLICY.md` episodic-first | P0 |
| BI-3 | Mixture-of-memories routing | MemFail recommendation | `MEMORY_MIXTURE_ROUTING.md` | P1 |
| BI-4 | Semantic forgetting limits | no-escape literature | `SEMANTIC_FORGETTING_LIMITS.md` | P2 |
| BI-5 | Verifier learning from usage | SkillLens + trajectory RL | `VERIFIER_LEARNING_LOOP.md` | P0 |
| BI-6 | MemFail harness API | `store/retrieve/get_all` | `memfail_brain_smoke.py` | P2 |

## Out of scope

- Replacing `memory_engine` with Mem0/StructMem stack
- Neural memory models in runtime
- Reporting MemFail benchmark % without local reproduction

## Grill script

```bash
python outputs/notebooklm/_query_beyond_intelligence_notebook.py
```

Uses Playwright profile `~/.notebooklm/profiles/default/browser_profile`.

## Wiki

`20_knowledge/wiki/concepts/Beyond Intelligence memory failures.md`

## Semantic graph (auto)

- [[Beyond Intelligence memory failures]]
- [[SkillDAG]]
- [[Behavior rules hub]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
