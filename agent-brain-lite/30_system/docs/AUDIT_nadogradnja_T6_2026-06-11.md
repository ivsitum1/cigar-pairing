# Audit — Beyond memory_engine / books_rag (T6, 2026-06-11)

Scope: `40_operations/scripts/`, `40_operations/python/brain_assist/`, `.cursor/hooks/`, `.cursor/scripts/`.

Pattern: uncaught external input, silent `except: pass`, unbounded logs, `sys.path` depth, non-atomic writes.

## Findings

| Sev | File:line | Issue | Status |
|-----|-----------|-------|--------|
| **P1** | `40_operations/scripts/memory_worker.py:7` | `sys.path` used 4× `.parent` (resolves above workspace); `memory_engine` import fails outside monorepo layout | **Fixed** → 3× `.parent` (same as `memory_admin.py`) |
| **P2** | `40_operations/python/brain_assist/*.py` | Multiple `write_text` state files without atomic rename (crash mid-write corrupts JSON) | Open — low frequency hooks; consider `os.replace` temp pattern |
| **P2** | `.cursor/hooks/memory_lifecycle.py:65` | `hook_session.json` written non-atomically | Open — small file; acceptable for session state |
| **P3** | `40_operations/scripts/arxiv_monthly_scan.py:31` | `REPO_ROOT = SCRIPT_DIR.parent.parent` (2 levels) — correct for `40_operations/scripts` layout | OK |
| **P3** | `.cursor/hooks/*_lifecycle.py` | `json.loads` on stdin wrapped in `JSONDecodeError` handlers | OK |
| **P3** | `40_operations/scripts/` (~134 files) | No bare `except: pass` found in scripts tree | OK |
| **P3** | `.cursor/hooks/` | Live hook paths: memory, books_rag, relation_conditioned, verifier_learning, trajectory | Reviewed; books_rag gated by `cfg.enabled` |

## Hook-path priority (live)

1. `memory_lifecycle.py` — ingest + retrieval/injection eval (wired 2026-06-11)
2. `relation_conditioned_lifecycle.py` — SkillLens verifier pack
3. `books_rag_lifecycle.py` — optional book injection
4. `verifier_learning_lifecycle.py` — sessionEnd/stop learning
5. `trajectory_lifecycle.py` — benchmark trajectory emit

## Recommended follow-ups

- Atomic JSON writes for `verifier_learning_cycle` state under `.agent/`
- Cap `.agent/memory/verifier_usage_ledger.jsonl` (same pattern as `memory_admin cap_self_eval`)
- Re-run full audit after major hook additions

## Verification

```powershell
python -m pytest 40_operations/tests/memory_engine 40_operations/tests/books_rag -q
```

## Semantic graph (auto)

- [[Behavior rules hub]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
