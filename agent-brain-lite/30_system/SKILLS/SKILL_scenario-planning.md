---
name: scenario-planning
description: Structured what-if and multi-horizon scenario analysis for strategies and investments. Use for what if, scenario analysis, threat model horizon, strategic scenarios.
version: 1.0
last_updated: 2026-05-18
domain: engineering
tokens: ~650
triggers:
  - what if
  - scenario analysis
  - scenario planning
  - threat model horizon
  - strategic scenarios
requires_packages: []
reference_files: []
conflicts_with:
  - grill-me
disambiguation: Use for exploratory scenarios; for software requirements interview use grill-me.
pipeline_position: []
---

# Skill: Scenario planning

## When to use

- User wants structured branches (best/base/worst) or multi-horizon stress test of a plan

## Procedure

1. Define decision and time horizons.
2. List drivers and uncertainties (max 5–7).
3. Build 3–4 scenarios with named triggers.
4. For each: implications, early signals, mitigations.
5. Tag assumptions `[ASSUMPTION]`; no false precision.

## Verification

- [ ] Scenarios mutually exclusive where required
- [ ] No fabricated probabilities without user data

## Related

- `54_strategic_engineering.mdc`, `SKILL_write-prd.md`

## Related Hubs

- [[Scenario planning skill]]
- [[Skills audit 2026-05]]
