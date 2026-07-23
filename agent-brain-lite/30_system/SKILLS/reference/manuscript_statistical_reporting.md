# Manuscript Statistical Reporting Reference

**Source:** `30_system/behavior_rules/58_manuscript_agent_protocol.md` Part 4  
**Use when:** Drafting or QC of Methods, Results, Table 1 for clinical manuscripts.

---

## 4.1 Bayesian Analysis Reporting

Include all of:

- Prior specification and justification (why this prior? sensitivity to alternatives?)
- Posterior summary: median/mean, 95% credible interval
- Decision criterion: prespecified threshold AND justification
- Sensitivity analysis: at minimum different priors; ideally different decision thresholds
- Visual: posterior density plot with decision boundary marked

**Workflow:** `SKILL_bayesian-workflow.md`

---

## 4.2 Non-inferiority Specific

- State NI margin AND justify (clinical reasoning, regulatory precedent)
- State decision threshold AND justify (P>0.70 needs explicit argument; P>0.90 is conventional)
- Acknowledge NI from observational data: assay sensitivity, confounding
- If not randomised: consider "Bayesian comparative effectiveness estimation" framing

---

## 4.3 Table 1 — ICU Cohort Minimum

| Domain | Variables |
|--------|-----------|
| Demographics | age, sex, BMI |
| Severity | APACHE II or III, SOFA (admission + peak) |
| Comorbidities | Charlson or individual: DM, CKD, liver disease, transplant, malignancy, immunosuppression |
| ICU context | reason for admission, MV at enrolment, vasopressor use, days in ICU before infection |
| Infection | site, MIC values, prior antibiotics, polymicrobial |
| Treatment | drug doses, duration, concomitant antibiotics |
| Renal | baseline GFR/creatinine, RRT during treatment |

**Flag if missing:** severity scores or renal function in antibiotic/ICU cohort Table 1.

---

## Honesty gate

Direct causal language only when design supports it. Observational/cross-sectional: retain design-appropriate limits.
