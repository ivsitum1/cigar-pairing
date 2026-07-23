---
name: model-native-skill-transform
description: Model-native skill transformation via steering vectors, SAE-lite, and baseline vs steered eval. Geometry notebook slice; requires MODEL_NATIVE_RUNTIME=1.
version: 0.1.0
last_updated: 2026-06-24
domain: engineering
tokens: ~380
triggers:
  - model-native skill
  - steering vector workflow
  - representation engineering pipeline
  - SAE skill transform
requires_packages: []
reference_files:
  - 30_system/docs/LIFEHARNESS_4_LAYER.md
  - 40_operations/python/model_native/residual_hooks.py
pipeline_position: []
---

# Model-native skill transform (P2 / gated)

**Status:** Experimental. Run only when `MODEL_NATIVE_RUNTIME=1` and Geometry PRD artifacts present.

## When to use

- User requests steering-vector or activation-space skill adaptation
- After grill-me + write-prd; not for default Cursor rules edits

## Workflow

1. Decompose target `SKILL_*.md` into atomic steps
2. Run `model_native_run.py` baseline vs steered on eval prompts
3. Record VERIFIED/INFERRED/UNVERIFIED per claim
4. Do not auto-merge into production skills without eval pass ≥ 80%

## Reject

- Citing YouTube +54% harness metrics without local repro
- Replacing SkillDAG or notebooklm-research-gate

## Eval

`30_system/SKILLS/evals/model-native-skill-transform.json` (seed when armed)
