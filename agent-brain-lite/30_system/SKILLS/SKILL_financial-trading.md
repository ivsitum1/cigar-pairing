---
name: financial-trading
description: Market analysis, risk framing, and position discipline for trading workflows. Use for trading skill, risk manager, portfolio risk, R-multiple. NOT clinical or research statistics.
version: 1.0
last_updated: 2026-05-18
domain: finance
tokens: ~600
triggers:
  - trading analysis
  - risk manager
  - portfolio risk
  - R-multiple
  - position sizing
requires_packages: []
reference_files: []
conflicts_with:
  - test-selection
  - r-statistics
disambiguation: Use for trading/risk ops; for biostatistics use test-selection or r-statistics.
pipeline_position: []
---

# Skill: Financial trading (light)

## When to use

- User explicitly requests trading or portfolio risk analysis

## Procedure

1. Restate strategy rules and constraints from user (no invented edge).
2. Risk: position size, stop, R-multiple, max drawdown limits.
3. Separate **facts** (prices, fills) from **hypotheses**.
4. Refuse autonomous live trading without explicit user authorization and API guardrails.

## Verification

- [ ] No guaranteed return claims
- [ ] Past performance caveat when relevant

## Related

- `SKILL_scenario-planning.md`

## Related Hubs

- [[Financial trading skill]]
- [[Skills audit 2026-05]]
