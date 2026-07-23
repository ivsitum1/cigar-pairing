---
source: everything-claude-code (mle-workflow skill, manifest-only import)
note: Snippets for CODE_IMPL / Tier 2 ML work; not a registry skill.
---

# MLE workflow snippets (ECC)

Use when building or reviewing production ML pipelines:

1. **Data contract:** schema version, null policy, train/val/test split rules documented before training.
2. **Reproducibility:** fixed seeds, logged package versions, artifact hash for training data snapshot.
3. **Evaluation:** holdout metrics pre-registered; no test-set peeking for model selection.
4. **Serving:** monitor drift, latency, and error rate; define rollback trigger.
5. **Documentation:** model card with intended use, limitations, and demographic caveats when applicable.

Cross-link: `90_archive/imports/ecc-index/SKILL_MAP.yaml` → `statsmodels-python` / future Tier 2 ML rules.

## Semantic graph (auto)

- [[Skill registry]]
- [[Statistics skill stack]]
- [SKILLS INDEX](../../docs/indexes/SKILLS_INDEX.md)
- [REFERENCE INDEX](REFERENCE_INDEX.md)
- [FOLDER INDEX](../../docs/FOLDER_INDEX.md)
