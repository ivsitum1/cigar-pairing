---
name: legal-contract-review
description: >-
  Reviews commercial and research agreements against an HR/EU-oriented playbook:
  flags deviations (GREEN/YELLOW/RED), suggests redlines, summarizes business impact.
  Not legal advice. Use for contract review, NDA, MSA, DPA, collaboration agreement,
  ugovor, red flags, clause-by-clause. NOT for clinical treatment or statistics.
version: 1.0
last_updated: 2026-05-16
domain: legal
tokens: ~1100
triggers:
  - contract review
  - review contract
  - pregled ugovora
  - NDA
  - MSA
  - DPA
  - data processing agreement
  - ugovor o suradnji
  - redline
  - red flags ugovor
  - limitation of liability
  - indemnification
  - governing law
requires_packages: []
reference_files:
  - reference/legal/contract_review_playbook_hr_eu.md
pipeline_position: []
---

# Skill: Legal contract review (HR/EU playbook)

**Disclaimer (always state upfront):** This workflow supports preparation for negotiation. It does **not** provide legal advice. Qualified counsel must review before signing.

## When to use

- User uploads or pastes a contract (PDF/DOCX/text) or links a document path in the workspace.
- User asks to flag risks, compare to standard positions, or draft negotiation redlines.
- Research collaboration, vendor SaaS, consulting, MTA-like agreements, confidentiality.

## When NOT to use

- Clinical treatment, dosing, bedside decisions → Clinical Decision Support subagent (no dosing from contracts skill).
- PRISMA/CONSORT/STROBE reporting → methodology skills.
- Drafting full statutes or court filings.

## Prerequisites

- Contract text available (file path or pasted excerpt).
- Optional: user states **side** (customer/vendor/licensor), **deadline**, **jurisdiction** (default: ask if missing).

## Step-by-step procedure

### 1) Intake

Ask or infer (do not guess jurisdiction):

1. Which **side** are you on? (customer, vendor, licensor, licensee, research institution, PI)
2. **Contract type** (NDA, MSA, SaaS, SOW, research collaboration, DPA)
3. **Governing law** preference (HR/EU member state) if known
4. **Focus areas** (data, IP, liability, termination, publication)

If only a fragment is provided, state limits of partial review.

### 2) Load playbook

Read `reference/legal/contract_review_playbook_hr_eu.md` (Stage 3 reference).

If the user has an institution-specific playbook file, prefer that over the generic baseline.

### 3) Read holistically

Read the full agreement (or offered sections) before flagging. Note cross-clause interactions (e.g. indemnity vs liability cap).

Minimum clause categories to cover when present:

| Category | Review focus |
|----------|----------------|
| Limitation of liability | Cap, mutuality, consequential damages, carveouts |
| Indemnification | Scope, mutuality, cap, procedure |
| IP | Pre-existing IP, deliverables, license scope, feedback clauses |
| Data protection | DPA, subprocessors, breach notice, transfers, deletion |
| Confidentiality | Term, carveouts, return/destruction |
| Term / termination | Duration, renewal, convenience, cause, wind-down |
| Governing law / disputes | EU/EEA preference; arbitration vs courts |

For **research/clinical data**, apply research-specific rows in the playbook (purpose limitation, retention, publication).

### 4) Classify deviations

Use **GREEN / YELLOW / RED** (definitions in playbook):

- **GREEN:** Acceptable; note only if useful.
- **YELLOW:** Negotiate; provide **current quote**, **proposed redline**, **rationale** (shareable with counterparty), **fallback**, **priority** (must-have / should-have / nice-to-have).
- **RED:** Escalate to counsel; explain risk and market-standard direction.

Never label RED items as GREEN to avoid conflict.

### 5) Output format

```markdown
## Contract review summary

**Document:** [name/path]
**Your side:** [role]
**Basis:** HR/EU generic playbook [or institution playbook if supplied]
**Not legal advice:** Counsel review required before execution.

## Top issues (max 5)

1. [RED/YELLOW] ...

## Clause analysis

### [Category] — GREEN|YELLOW|RED
**Contract says:** ...
**Playbook position:** ...
**Deviation:** ...
**Business impact:** ...
**Redline (if YELLOW/RED):** ...

## Negotiation strategy

Tier 1 must-haves / Tier 2 should-haves / Tier 3 concessions

## Next steps
```

Write in the user's language (Croatian or English) unless they request otherwise.

### 6) Honesty and grounding

- Tag: `[EXTRACTED]` from contract text, `[INFERRED]` for risk interpretation, `[BLANK]` if clause missing.
- **Never fabricate** clause text; quote exactly or mark paraphrase.
- Do not invent governing law or party names.
- If uncertain on HR-specific statute, say so and recommend local counsel.

## Verification

- [ ] Disclaimer included
- [ ] Each YELLOW/RED has concrete redline or escalation path
- [ ] Research/data clauses addressed when health data mentioned
- [ ] No clinical dosing or treatment recommendations

## Related (wiki)

- [[Legal contract review skill]]
- [[Skill discovery skill]]
- [[Skill registry]]

## Related (repo)

- External skill search: `SKILL_skill-discovery.md`
- New repeatable legal workflows: `SKILL_create-skill.md`
- Document conversion for DOCX: `SKILL_document-conversion.md`

## Skill reference graph (auto)

- [[contract_review_playbook_hr_eu]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
