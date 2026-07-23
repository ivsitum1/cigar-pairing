# Research Gap Finder

## Purpose

Systematic identification of research gaps in reviewed literature. Used for:
- Defining research questions
- Justifying new studies
- Positioning scientific contribution
- Identifying future research directions

## Types of Research Gaps (Taxonomy)

| # | Gap Type | Definition | Key Indicators | Example |
|---|----------|------------|----------------|---------|
| 1 | **Theoretical Gap** | Lack of theoretical frameworks to explain phenomenon | "No existing theory explains...", "Theoretical framework lacking" | No theory explaining why TIVA improves recovery vs. inhalational anesthesia |
| 2 | **Knowledge Gap** | Lack of understanding or information on a topic | "Little is known about...", "Poorly understood", "Underexplored" | Optimal timing for therapeutic suggestions during anesthesia is unknown |
| 3 | **Evidence Gap** | Insufficient or conflicting evidence for conclusion | "Conflicting results...", "Inconsistent findings", "Limited evidence" | Studies show conflicting results on effect of music on anxiety |
| 4 | **Practical Knowledge Gap** | Inability to apply theoretical knowledge to real problems | "Translation gap", "Implementation barriers", "Real-world applicability unclear" | We know suggestions help but not how to implement them in clinical practice |
| 5 | **Population Gap** | Underrepresentation or exclusion of certain groups | "Elderly excluded...", "Pediatric data lacking", "Specific populations underrepresented" | Most studies exclude patients >75 years |
| 6 | **Implementation Gap** | Gap between research findings and practical application | "Not adopted in practice...", "Barriers to implementation", "Low uptake" | ERAS protocols proven effective but rarely fully implemented |
| 7 | **Contextual Gap** | Inability to generalize findings due to different contexts | "Limited to [setting]...", "Cultural differences", "Healthcare system variations" | US results may not apply in other countries |
| 8 | **Empirical Gap** | Lack of data or research studies | "No studies have examined...", "Lack of empirical data", "Unexplored" | No RCTs on effect of suggestions on QoR-40 |
| 9 | **Data Gap** | Insufficient data to answer research question | "Data unavailable...", "Missing variables", "Insufficient sample size" | Registries do not collect data on use of suggestions |
| 10 | **Methodological Gap** | Inadequacy or absence of appropriate research methods | "No validated instrument...", "Methodological limitations", "Bias in existing studies" | No validated questionnaire for measuring effect of suggestions in target language |

## Gap Analysis Workflow

### Step 1: Literature Extraction Template

When reviewing literature, extract the following information:

```markdown
## Literature Gap Analysis Form

### Study Information
- **Citation:** [Authors, Year, Journal]
- **Study Design:** [RCT/Cohort/Meta-analysis/etc.]
- **Population:** [N, demographics, inclusion/exclusion]
- **Intervention/Exposure:** [What was studied]
- **Outcome:** [Primary and secondary outcomes]
- **Key Findings:** [Main results with effect sizes]

### Gap Identification
- **Explicitly Stated Gaps:** [What authors identify as limitations/future directions]
- **Implicit Gaps:** [What is missing but not stated]
- **Methodological Limitations:** [Design flaws, bias risks]
- **Generalizability Issues:** [External validity concerns]

### Gap Classification
- [ ] Theoretical Gap
- [ ] Knowledge Gap
- [ ] Evidence Gap
- [ ] Practical Knowledge Gap
- [ ] Population Gap
- [ ] Implementation Gap
- [ ] Contextual Gap
- [ ] Empirical Gap
- [ ] Data Gap
- [ ] Methodological Gap
```

### Step 2: Systematic Gap Identification Questions

For each gap type, ask the following questions:

```r
# RESEARCH GAP IDENTIFICATION QUESTIONS

gap_questions <- list(
  
  theoretical = c(
    "Is there a theoretical framework that explains this phenomenon?",
    "Have existing theories been tested in this context?",
    "Which mechanisms remain unexplained?"
  ),
  
  knowledge = c(
    "What do we still not know about this topic?",
    "Which aspects are insufficiently researched?",
    "What information is missing for full understanding?"
  ),
  
  evidence = c(
    "Are findings consistent across studies?",
    "Are there conflicting results?",
    "What is the quality of evidence (GRADE)?"
  ),
  
  practical_knowledge = c(
    "Can the knowledge be applied in practice?",
    "What are the barriers to implementation?",
    "Is there a gap between theory and practice?"
  ),
  
  population = c(
    "Which populations are excluded from research?",
    "Are results applicable to all age groups?",
    "Are there subgroups requiring special attention?"
  ),
  
  implementation = c(
    "Are findings used in clinical practice?",
    "What are the barriers to adoption?",
    "Is there an implementation strategy?"
  ),
  
  contextual = c(
    "Can findings be generalized to other contexts?",
    "Do cultural differences affect results?",
    "Are results applicable in the target healthcare system?"
  ),
  
  empirical = c(
    "Are there empirical studies on this topic?",
    "Which research designs have been used?",
    "What is missing in the empirical literature?"
  ),
  
  data = c(
    "Are the necessary data available?",
    "Are there registries or databases?",
    "Is the sample size sufficient?"
  ),
  
  methodological = c(
    "Are the methods used appropriate?",
    "Are there validated instruments?",
    "What are the methodological weaknesses of existing studies?"
  )
)
```

### Step 3: Gap Synthesis Matrix

```r
# CREATE GAP SYNTHESIS MATRIX

create_gap_matrix <- function(studies) {
  
  # Define gap types
  gap_types <- c(
    "Theoretical", "Knowledge", "Evidence", "Practical Knowledge",
    "Population", "Implementation", "Contextual", "Empirical",
    "Data", "Methodological"
  )
  
  # Create empty matrix
  gap_matrix <- matrix(
    nrow = length(studies),
    ncol = length(gap_types),
    dimnames = list(studies, gap_types)
  )
  
  # Fill with: 0 = No gap, 1 = Minor gap, 2 = Major gap
  # [To be filled during analysis]
  
  return(gap_matrix)
}

# EXAMPLE USAGE
studies <- c(
  "Smith et al. 2020",
  "Jones et al. 2021",
  "Brown et al. 2022",
  "Garcia et al. 2023"
)

gap_matrix <- create_gap_matrix(studies)
```

### Step 4: Gap Prioritization Framework

```markdown
## Gap Prioritization Criteria

### Impact Score (1-5)
- **5:** Addressing gap would significantly advance field
- **4:** High potential for clinical impact
- **3:** Moderate contribution to knowledge
- **2:** Incremental advancement
- **1:** Limited impact

### Feasibility Score (1-5)
- **5:** Can be addressed with available resources
- **4:** Requires moderate additional resources
- **3:** Significant but achievable investment
- **2:** Major challenges to overcome
- **1:** Not feasible with current capabilities

### Urgency Score (1-5)
- **5:** Critical need for patient safety/outcomes
- **4:** High clinical relevance
- **3:** Important but not urgent
- **2:** Low priority
- **1:** Can wait indefinitely

### Priority = Impact × Feasibility × Urgency
- **Score 100-125:** Immediate priority
- **Score 50-99:** High priority
- **Score 25-49:** Medium priority
- **Score 1-24:** Low priority
```

## Gap Analysis Report Template

```markdown
# Research Gap Analysis Report

## 1. Executive Summary
- **Total Studies Reviewed:** [N]
- **Date Range:** [Start - End]
- **Primary Research Question:** [RQ]
- **Key Gaps Identified:** [Brief list of top 3-5 gaps]

## 2. Literature Overview
### 2.1 Search Strategy
- Databases: [PubMed, Scopus, Web of Science, etc.]
- Keywords: [Search terms]
- Inclusion/Exclusion Criteria: [List]

### 2.2 Study Characteristics
- Study designs: [N RCTs, N cohorts, N reviews]
- Total participants: [N]
- Geographic distribution: [Countries]
- Publication years: [Range]

## 3. Gap Identification

### 3.1 Theoretical Gaps
| Gap Description | Supporting Evidence | Impact | Feasibility | Priority |
|-----------------|---------------------|--------|-------------|----------|
| [Gap 1] | [Studies that identify this gap] | [1-5] | [1-5] | [Score] |

### 3.2 Knowledge Gaps
[Same format as above]

### 3.3 Evidence Gaps
[Same format as above]

### 3.4 Practical Knowledge Gaps
[Same format as above]

### 3.5 Population Gaps
[Same format as above]

### 3.6 Implementation Gaps
[Same format as above]

### 3.7 Contextual Gaps
[Same format as above]

### 3.8 Empirical Gaps
[Same format as above]

### 3.9 Data Gaps
[Same format as above]

### 3.10 Methodological Gaps
[Same format as above]

## 4. Gap Synthesis Matrix
[Visual matrix showing all gaps across studies]

## 5. Priority Ranking
| Rank | Gap Type | Description | Impact | Feasibility | Urgency | Total Score |
|------|----------|-------------|--------|-------------|---------|-------------|
| 1 | [Type] | [Description] | [X] | [X] | [X] | [Score] |
| 2 | ... | ... | ... | ... | ... | ... |

## 6. Recommendations for Future Research

### 6.1 High-Priority Research Questions
1. [RQ1 that addresses top gap]
2. [RQ2]
3. [RQ3]

### 6.2 Suggested Study Designs
- [Gap 1]: [Recommended design, e.g., RCT, cohort]
- [Gap 2]: [Design]

### 6.3 Methodological Recommendations
- [Specific methods to address gaps]

## 7. Implications

### 7.1 For Research
- [How these gaps inform future studies]

### 7.2 For Clinical Practice
- [What clinicians should know]

### 7.3 For Policy
- [Policy implications]

## 8. Limitations of This Analysis
- [Acknowledge limitations of gap analysis itself]

## 9. References
[Full reference list]
```

## Automated Gap Detection Keywords

```r
# KEYWORDS FOR AUTOMATED GAP DETECTION IN LITERATURE

gap_detection_keywords <- list(
  
  # Explicit gap indicators
  explicit_gap_phrases = c(
    "further research is needed",
    "future studies should",
    "remains unclear",
    "little is known",
    "poorly understood",
    "underexplored",
    "gap in the literature",
    "lack of evidence",
    "insufficient data",
    "conflicting results",
    "inconsistent findings",
    "limited to",
    "not generalizable",
    "methodological limitations",
    "small sample size",
    "selection bias",
    "no randomized controlled trials",
    "observational only",
    "heterogeneity across studies"
  ),
  
  # Limitation section keywords
  limitation_phrases = c(
    "limitations of this study",
    "study limitations",
    "weaknesses include",
    "potential biases",
    "could not assess",
    "unable to determine",
    "beyond the scope"
  ),
  
  # Future direction keywords
  future_direction_phrases = c(
    "future research",
    "future studies",
    "warrants further investigation",
    "should be explored",
    "remains to be determined",
    "needs to be established",
    "requires validation"
  )
)

# FUNCTION TO SCAN TEXT FOR GAPS
detect_gaps_in_text <- function(text, keywords = gap_detection_keywords) {
  
  text_lower <- tolower(text)
  
  gaps_found <- list()
  
  for (category in names(keywords)) {
    matches <- sapply(keywords[[category]], function(phrase) {
      grepl(phrase, text_lower, fixed = TRUE)
    })
    gaps_found[[category]] <- keywords[[category]][matches]
  }
  
  return(gaps_found)
}
```

## Integration with Literature Review Workflow

When conducting literature review:

1. **During Reading:**
   - Use gap extraction template for each study
   - Mark explicit and implicit gaps
   - Note methodological limitations

2. **After Reading:**
   - Compile gap synthesis matrix
   - Apply prioritization framework
   - Generate gap analysis report

3. **For Research Proposal:**
   - Select highest-priority gap
   - Justify with evidence from analysis
   - Design study to address specific gap

## Example Gap Analysis Output

```markdown
## Gap Analysis: Therapeutic Suggestions in Anesthesia

### Top 3 Identified Gaps:

**1. Empirical Gap (Priority Score: 100)**
- No RCTs examining therapeutic suggestions + QoR-40 outcome
- Existing studies use non-validated outcome measures
- **Recommendation:** Conduct RCT with validated QoR-40 as primary outcome

**2. Methodological Gap (Priority Score: 80)**
- No standardized protocol for delivering suggestions
- Timing, content, and delivery vary across studies
- **Recommendation:** Develop and validate standardized suggestion protocol

**3. Population Gap (Priority Score: 64)**
- Elderly (>75 years) excluded from all studies
- No data on patients with cognitive impairment
- **Recommendation:** Include elderly population in future trials with appropriate modifications
```

## Related Hubs

- [Folder index hub](../../../docs/FOLDER_INDEX.md)
- [All notes index](../../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../../docs/GRAPH_CONNECTIVITY_MAP.md)
