# Statistical Rules by Study Type

## Purpose

This document establishes specific statistical rules and best practices for different types of clinical research. Each study type has its specific requirements and reporting standards.

---

## Prospective Clinical Studies

### Definition

Prospective studies collect data forward in time, starting from the moment of participant enrollment. They include randomized controlled trials (RCT), non-randomized controlled trials, and prospective cohort studies.

### Statistical Requirements

#### Study Planning

- [ ] **Sample size calculation**: Before study start
  - Power analysis (usually 80% or 90%)
  - Effect size based on clinically relevant difference
  - Alpha level (usually 0.05)
  - Dropout rate accounted for
  - Document all assumptions

- [ ] **Pre-specification of analysis**: Statistical Analysis Plan (SAP)
  - Primary and secondary outcomes
  - Analysis methods for each outcome
  - Plan for handling missing data
  - Plan for subgroup analyses
  - Plan for interim analyses (if applicable)

#### Randomization (for RCT)

- [ ] **Randomization method**: Clearly described
  - Simple randomization
  - Block randomization
  - Stratified randomization
  - Minimization (if used)

- [ ] **Allocation concealment**: Ensure randomization is not predictable

- [ ] **Blinding**: Describe level of blinding
  - Single-blind
  - Double-blind
  - Triple-blind
  - Open-label (justify)

#### Data Analysis

**Primary Outcome:**

- [ ] **Intention-to-treat (ITT) analysis**: Primary analysis
  - Analyze all randomized participants in their assigned groups
  - Regardless of compliance or dropout

- [ ] **Per-protocol (PP) analysis**: Secondary analysis
  - Only participants who completed protocol
  - Clearly label as sensitivity analysis

**Statistical Methods:**

- [ ] **Continuous outcomes**:
  - Primary: Welch's t-test or robust parametric tests
  - Secondary: Mann-Whitney as sensitivity (if needed)
  - Paired data: Paired t-test or permutation tests

- [ ] **Binary outcomes**:
  - Chi-square test or Fisher's exact test (if expected frequencies < 5)
  - Logistic regression for adjustment of confounders
  - Report risk ratio (RR) or odds ratio (OR) with 95% CI

- [ ] **Time-to-event outcomes**:
  - Kaplan-Meier survival curves
  - Log-rank test for comparison
  - Cox proportional hazards model for multivariate analysis
  - Check proportional hazards assumption

**Handling Missing Data:**

- [ ] **Document missing pattern**:
  - MCAR (Missing Completely At Random)
  - MAR (Missing At Random)
  - MNAR (Missing Not At Random)

- [ ] **Methods**:
  - Primary: Complete case analysis (if < 5% missing)
  - Alternative: Multiple imputation or sensitivity analysis
  - Document all methods

#### Reporting

- [ ] **CONSORT checklist**: Follow CONSORT guidelines
- [ ] **Flow diagram**: Mandatory
- [ ] **Baseline characteristics**: Table with group comparison
- [ ] **Results**: For all pre-specified outcomes
- [ ] **Adverse events**: Fully reported

---

## Retrospective Observational Studies

### Definition

Retrospective studies analyze data that has already been collected, usually from medical records or databases. They include case-control studies, retrospective cohort studies, and cross-sectional studies.

### Statistical Requirements

#### Study Planning

- [ ] **Sample size calculation**: Although retrospective, plan before analysis
  - Power analysis for expected effect sizes
  - Consider data availability

- [ ] **Pre-specification**: Although retrospective, define:
  - Primary and secondary outcomes
  - Analysis methods
  - Confounders for adjustment
  - Plan for handling missing data

#### Participant Selection

- [ ] **Inclusion/exclusion criteria**: Clearly defined
- [ ] **Matching (for case-control)**: Describe method
  - Frequency matching
  - Individual matching
  - Reason for matching variables

#### Data Analysis

**Case-Control Studies:**

- [ ] **Odds ratio (OR)**: Primary effect measure
  - Unadjusted OR
  - Adjusted OR (logistic regression)
  - 95% CI for both

- [ ] **Matching**: If matching was used
  - Conditional logistic regression
  - Consider stratified analysis

**Retrospective Cohort Studies:**

- [ ] **Risk ratio (RR) or hazard ratio (HR)**: Primary effect measure
  - Unadjusted and adjusted
  - 95% CI

- [ ] **Time-to-event analysis**: If relevant
  - Kaplan-Meier curves
  - Cox regression

**Cross-Sectional Studies:**

- [ ] **Prevalence or prevalence ratio**: Primary effect measure
  - Appropriate statistical methods (chi-square, log-binomial regression)

**Confounding:**

- [ ] **Identify potential confounders**: A priori
- [ ] **Adjustment**: Multivariate models
  - Logistic regression (binary outcome)
  - Cox regression (time-to-event)
  - Linear regression (continuous outcome)

- [ ] **Propensity score method**: If appropriate
  - Propensity score matching
  - Propensity score weighting
  - Propensity score stratification

**Handling Missing Data:**

- [ ] **Document**: Pattern and proportion of missingness
- [ ] **Methods**: 
  - Complete case (if appropriate)
  - Multiple imputation (preferred if > 5% missing)
  - Sensitivity analysis

#### Reporting

- [ ] **STROBE checklist**: Follow STROBE guidelines
- [ ] **Flow diagram**: Recommended
- [ ] **Baseline characteristics**: Table with group comparison
- [ ] **Confounders**: Clearly identify and document
- [ ] **Limitations**: Explicitly discuss
  - Selection bias
  - Information bias
  - Confounding
  - Generalizability

---

## Case Series

### Definition

Case series describes a series of patients with the same condition or intervention, without a control group.

### Statistical Requirements

#### Data Analysis

- [ ] **Descriptive statistics**: Primary method
  - Continuous: Mean ± SD or Median [IQR]
  - Categorical: n (%)

- [ ] **No inferential statistics**: 
  - No p-values
  - No comparison with control group
  - Can compare with literature (narrative)

- [ ] **Time trends**: If relevant
  - Describe changes over time
  - Visualize (line plot, etc.)

#### Reporting

- [ ] **CARE checklist**: Follow CARE guidelines (if appropriate)
- [ ] **Characteristics table**: For all cases
- [ ] **Narrative description**: Detailed description of each case or summary
- [ ] **Limitations**: Explicitly state
  - No control group
  - No randomization
  - Selection bias
  - Generalizability limited

---

## Case Reports

### Definition

Case report describes one or a small number of cases with unusual or new characteristics.

### Statistical Requirements

#### Data Analysis

- [ ] **Descriptive statistics only**: 
  - No statistical tests
  - No inferential statistics
  - Descriptive presentation of data

- [ ] **Narrative description**: 
  - Detailed case description
  - Clinical course
  - Results

#### Reporting

- [ ] **CARE checklist**: Follow CARE guidelines
- [ ] **Structured format**:
  - Introduction
  - Case description
  - Discussion
  - Conclusion

- [ ] **Limitations**: 
  - N = 1 (or small number)
  - No generalization
  - No statistical inference

---

## Prospective Pseudo-Randomized Studies

### Definition

Studies that use alternative allocation methods (e.g., alternation, date of birth, medical record number) instead of true randomization.

### Types

1. **Alternation**: Alternative allocation (e.g., first patient to group A, second to group B)
2. **Quasi-randomization**: Based on date of birth, medical number, etc.
3. **Cluster randomization**: Randomization at cluster level (e.g., hospital, department)

### Statistical Requirements

#### Study Planning

- [ ] **Sample size calculation**: 
  - For cluster randomization: account for intracluster correlation coefficient (ICC)
  - Design effect = 1 + (m-1) × ICC, where m is average cluster size
  - Adjusted sample size = n × design effect

#### Data Analysis

- [ ] **Apply same methods as for RCT**: 
  - ITT approach
  - Same statistical tests

- [ ] **Cluster randomization**: 
  - If used: Mixed-effects models
  - Account for clustering in analysis
  - Do not treat as independent observations

- [ ] **Sensitivity analysis**: 
  - Consider impact of allocation method
  - Compare with literature

#### Reporting

- [ ] **Clearly label**: Not true randomization
- [ ] **Describe allocation method**: In detail
- [ ] **Discuss limitations**:
  - Selection bias possible
  - Allocation concealment difficult to ensure
  - Potential confounders

- [ ] **CONSORT**: Can be used with modifications
- [ ] **Label in title/abstract**: "Quasi-randomized" or "Non-randomized"

---

## Cross-Sectional Studies

### Definition

Cross-sectional studies measure outcomes and exposures simultaneously at one point in time.

### Statistical Requirements

#### Data Analysis

- [ ] **Prevalence**: Primary effect measure
  - Prevalence ratio or prevalence odds ratio
  - 95% CI

- [ ] **Statistical methods**:
  - Chi-square test for categorical variables
  - T-test or Mann-Whitney for continuous variables
  - Log-binomial or Poisson regression for adjusted analysis

- [ ] **Confounding**: 
  - Multivariate models for adjustment
  - Clearly identify confounders

#### Reporting

- [ ] **STROBE checklist**: Follow STROBE guidelines
- [ ] **Clearly label**: Cross-sectional design
- [ ] **Limitations**: 
  - No temporal relationship (cannot prove causality)
  - Selection bias
  - Survivorship bias

---

## Longitudinal Studies

### Definition

Longitudinal studies follow participants over time with multiple measurements.

### Statistical Requirements

#### Data Analysis

- [ ] **Mixed-effects models**: Preferred approach
  - Account for within-subject correlation
  - Random intercept and/or random slope

- [ ] **Repeated measures ANOVA**: Alternative
  - Check assumptions (sphericity)
  - Greenhouse-Geisser correction if needed

- [ ] **Generalized Estimating Equations (GEE)**: For binary outcome
  - Select working correlation structure
  - Robust standard errors

- [ ] **Time-varying covariates**: If relevant
  - Include in model

#### Reporting

- [ ] **Clearly describe**: Design and time points
- [ ] **Dropout analysis**: 
  - Document dropout rate
  - Analyze differences between completers and non-completers
  - Handling missing data

---

## Checklist by Study Type

### Prospective Clinical Studies (RCT)

- [ ] Sample size calculation before study
- [ ] Pre-specified SAP
- [ ] Randomization clearly described
- [ ] Allocation concealment ensured
- [ ] Blinding described
- [ ] ITT analysis as primary
- [ ] CONSORT checklist followed
- [ ] Flow diagram included
- [ ] Baseline characteristics reported
- [ ] All pre-specified outcomes reported

### Retrospective Observational Studies

- [ ] Sample size calculation (if possible)
- [ ] Pre-specification of analysis
- [ ] Confounders identified a priori
- [ ] Multivariate adjustment
- [ ] STROBE checklist followed
- [ ] Flow diagram (recommended)
- [ ] Baseline characteristics reported
- [ ] Limitations explicitly discussed

### Case Series

- [ ] Descriptive statistics
- [ ] No inferential statistics
- [ ] CARE checklist (if appropriate)
- [ ] Characteristics table
- [ ] Limitations clearly stated

### Case Reports

- [ ] CARE checklist followed
- [ ] Structured format
- [ ] Descriptive statistics only
- [ ] No statistical tests
- [ ] Limitations explicitly stated

### Pseudo-Randomized Studies

- [ ] Clearly labeled as not true randomization
- [ ] Allocation method described in detail
- [ ] Cluster analysis (if applicable)
- [ ] Limitations discussed
- [ ] Labeled in title/abstract

---

## Hybrid Study Designs

### Nested Case-Control (within a cohort)

- Report as: "nested case-control within [cohort name]"
- Apply STROBE checklist + additional case-control items
- OR from nested case-control approximates RR only when outcome prevalence < 10%
- Matching variables must not be on the causal pathway

### Case-Cohort Design

- Subcohort sampled at baseline; cases identified during follow-up
- More efficient than nested case-control when multiple outcomes studied
- Use Barlow-Prentice or Lin-Wei weighted Cox regression
- Report subcohort sampling fraction

---

## References

- **CONSORT**: Consolidated Standards of Reporting Trials
- **STROBE**: Strengthening the Reporting of Observational Studies in Epidemiology
- **CARE**: Case Report Guidelines
- **TREND**: Transparent Reporting of Evaluations with Nonrandomized Designs
- **STARD**: Standards for Reporting Diagnostic Accuracy Studies

---

## Key Principles

### For All Study Types

1. **Pre-specification**: Define analysis before looking at data
2. **Transparency**: Clearly describe all methods
3. **Limitations**: Explicitly acknowledge design limitations
4. **Reproducibility**: Document all steps
5. **Appropriate methods**: Use methods appropriate for study design

### Specifically for Observational Studies

1. **Confounding**: Always consider and adjust
2. **Bias**: Identify and discuss potential biases
3. **Causal inference**: Do not claim causality without caution
4. **Generalizability**: Discuss generalization limitations

---

**Version:** 1.0  
**Last updated:** 2024-12-31

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
