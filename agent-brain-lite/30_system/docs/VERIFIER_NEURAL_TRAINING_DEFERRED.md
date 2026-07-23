# Verifier neural training (Phase 4 — deferred)

**Status:** DOCUMENTATION ONLY — do not implement in agent-rules runtime until review on **2026-07-08**.

## Motivation

Sklearn blend (Phase 3) caps at TF-IDF + numeric features. Relation-conditioned encoder heads (Rcml, arXiv:2508.17497) may improve verifier routing when live ledger exceeds ~500 labeled rows.

## Inputs

| Source | Path |
|--------|------|
| Live contrastive | `outputs/rcml_training/live_contrastive.jsonl` |
| Live instruction | `outputs/rcml_training/live_instruction.jsonl` |
| Usage ledger | `.agent/memory/verifier_usage_ledger.jsonl` |
| Seed relations | `30_system/docs/rcml_relation_registry.json` |
| MemFail pairs | MemFail harness contrastive storage/retrieval tasks |

## Model (out of repo)

- Small sentence encoder (e.g. `sentence-transformers/all-MiniLM-L6-v2`)
- Relation-conditioned classification head (Rcml-style)
- Training project: `02_analysis/verifier_training/` or external study repo

## Runtime integration (future)

- Optional local MCP or HTTP service
- Hook replaces sklearn blend in `skill_verifier.verify_bundle`
- Env: `VERIFIER_NEURAL_ENDPOINT`, `VERIFIER_ML_BLEND=0` during rollout

## Metrics

- MemFail storage / retrieval diagnostic pass rate
- Internal `skill-verifier-gate` eval pass rate
- No regression on `test_relation_conditioned*` / `test_verifier_*`

## Rollback

1. `VERIFIER_ML_BLEND=0`
2. Remove `40_operations/models/verifier_sklearn.joblib`
3. Disable neural endpoint
4. Revert `verifier_registry.json` `accept_score` from `evolution_log` snapshot

## Policy alignment

[DEEP_LEARNING_POLICY.md](DEEP_LEARNING_POLICY.md): no LLM fine-tuning on rules in agent-rules. Neural verifier training stays **outside** the brain repo; only inference adapter may be linked later.
