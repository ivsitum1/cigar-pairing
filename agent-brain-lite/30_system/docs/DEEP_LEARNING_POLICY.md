# Deep learning policy (agent-rules brain)

Where deep learning (DL) and classical ML belong in this workspace, and how the brain may evolve without fine-tuning LLMs on rules.

**Related:** [PADDLEPADDLE.md](PADDLEPADDLE.md), [SELF_EVAL_RULES_SKILLS_LEARNING_SPEC.md](SELF_EVAL_RULES_SKILLS_LEARNING_SPEC.md), [RAG_VS_STUDY_DATA.md](RAG_VS_STUDY_DATA.md)

---

## Three layers

| Layer | DL role | Mechanism | Auto-change rules? |
|-------|---------|-----------|-------------------|
| **Task tools** | Primary | Pretrained models (OCR, embeddings, project ML) | No |
| **Brain assist** | Ranking only | TF-IDF skill rerank, similar error retrieval | No |
| **Rules/skills learning** | None (no fine-tuning) | error_log, evals, self_eval loop, autoresearch gates, **trajectory RL** ([TRAJECTORY_RL_POLICY.md](TRAJECTORY_RL_POLICY.md)) | Skills yes (gated); core rules proposal-only |

---

## Task layer (use DL here)

| Use case | Stack | Location |
|----------|-------|----------|
| Scanned PDF OCR | PaddlePaddle + PaddleOCR | `.venv-ocr`, `extract_pdf_ocr.ps1` |
| Library semantic search | sentence-transformers + Chroma | `BOOKS_RAG_DATA_DIR` (`C:\books_rag`), MCP `books_rag` |
| Wiki / note neighbors | TF-IDF (sklearn) | `wiki_embedding_index.py` |
| **Study / project ML & DL** | PyTorch, sklearn, tidymodels, etc. | **Study project** `02_analysis/`, not brain root |
| Drug discovery (optional) | Pipeline 7B skills | `SKILL_drug-discovery-workbench` |

**Principle:** Brain holds skills, rules, and install docs. **Trained model artifacts** live in study projects or gitignored `data/`.

---

## Brain assist layer (lightweight ML)

Optional **signals** before routing or answering (orchestrator may call CLI):

```bash
python 40_operations/scripts/skill_rerank.py --prompt "..." --auto-pipeline --dag --json
python 40_operations/scripts/similar_errors.py --prompt "..." --json
```

- **Does not** replace keyword routing or `detect_agent`.
- **Does not** write or patch rules.
- Requires `scikit-learn` (see `requirements-dev.txt` / `30_system/behavior_rules/tools/requirements.txt`).

Module: `40_operations/python/brain_assist/`.

---

## Rules and workspace evolution (no DL training)

Allowed:

- `error_log.jsonl` → `99_error_memory.mdc` (promote after pattern)
- Skill eval regression (`skill_gap_ingest.py`)
- `self_eval_learning_loop.py` / autoresearch with metric gates and rollback

**Non-goals** (see learning spec):

- Fine-tuning LLMs on chat or rules
- Auto-apply patches to `core-principles.mdc` or `00_orchestrator_agent.mdc`

DL may **surface** candidates (similar errors); humans or eval gates **decide**.

---

## Statistical methodology vs DL

For **inferential clinical research** (hypothesis tests, meta-analysis, regression on tabular data), default to classical/Bayesian workflow in `.cursor/rules/statistics-test-selection.mdc`.

Use **DL models** when the project protocol pre-specifies them and the outcome is prediction/perception, not primary confirmatory inference on a simple tabular RCT. Full decision tree: same file, section **Deep learning vs inferential statistics**, and `30_system/behavior_rules/02_statistics.md`.

When DL is chosen:

- Load `.cursor/rules/50_ml_mlops_standards.mdc` (globs: `**/ml/**`, `**/models/**`, …)
- Models and weights in study repo; report per SPIRIT-AI/CONSORT-AI when applicable

---

## Virtual environments (this machine)

| Venv | Python | Purpose |
|------|--------|---------|
| System / default | Often 3.14 | Brain scripts, pytest (not Paddle) |
| `.venv-ocr` | 3.12 | PaddleOCR only |
| Study project venv | 3.11–3.12 typical | Project ML/DL |

Recreate `.venv-ocr` locally after sync from another PC (venv paths are machine-specific).

---

## @brain commands (assist)

| Command | Script |
|---------|--------|
| `@brain similar-errors <text>` | `similar_errors.py --prompt "..."` |
| `@brain skill-rerank <text>` | `skill_rerank.py --prompt "..." --auto-pipeline --dag` |

---

## References

- [PaddlePaddle/Paddle](https://github.com/PaddlePaddle/Paddle) — framework wheels only
- [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) — vendored OCR app
- `30_system/docs/autoresearch_hybrid_spec.md` — bounded rule/skill iteration
