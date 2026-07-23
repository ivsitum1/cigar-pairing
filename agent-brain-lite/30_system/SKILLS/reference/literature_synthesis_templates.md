# Literature Synthesis Templates

Reference file for `SKILL_literature-synthesis.md`. Load only when executing a step that needs these templates.

---

## 1. Analysis Grid Template

Use this table to extract structured data from each included study. One row per study.

| Study (Author, Year) | Aim / Objective | Design / Method | Sample (n, population) | Key Findings | Limitations | Gap Identified |
|-|-|-|-|-|-|-|
| Smith et al., 2023 | [State the study's primary aim] | [RCT / cohort / cross-sectional / etc.] | [n=120, ICU patients] | [Main result with effect size if available] | [Small sample, single-centre, etc.] | [What this study did not address] |
| ... | ... | ... | ... | ... | ... | ... |

**Usage notes:**
- Maintain consistent terminology across rows (same outcome names, same population descriptors)
- Record effect sizes and confidence intervals where reported
- In the "Gap Identified" column, note what remains unanswered that is relevant to your RQ

---

## 2. Consensus Meter Template

For each research question or sub-question, tally the direction of evidence across studies.

| Research Question / Sub-question | Studies Supporting | Studies Contradicting | Inconclusive / Mixed | Consensus Level |
|-|-|-|-|-|
| [Does X improve outcome Y?] | Author1, Author3, Author5 (n=3) | Author2 (n=1) | Author4 (n=1) | **60% — Moderate** |
| [Is Z associated with W?] | Author1, Author2, Author3, Author4 (n=4) | — (n=0) | Author5 (n=1) | **80% — High** |

**Consensus thresholds:**
- **High (>80%):** Strong agreement across studies. State this directly; gap may lie in populations, settings, or methods not yet tested.
- **Moderate (50-80%):** Partial agreement with notable exceptions. Explore why disagreement exists (methods, populations, measurement). Signals opportunity for replication or methodological improvement.
- **Low / Divided (<50%):** No clear consensus. Strong justification for further investigation. Discuss possible reasons for divergence.

---

## 3. Boolean Search String Examples

### Structure
```
(Population terms) AND (Intervention/Exposure terms) AND (Outcome terms)
```

### Example 1: Clinical intervention
```
("critically ill" OR "intensive care" OR "ICU") 
AND ("early mobilization" OR "physical therapy" OR "rehabilitation") 
AND ("length of stay" OR "functional outcome*" OR "mortality")
```

### Example 2: Observational association
```
("type 2 diabetes" OR "T2DM" OR "diabetes mellitus") 
AND ("sleep quality" OR "sleep disorder*" OR "insomnia") 
AND ("glycemic control" OR "HbA1c" OR "glucose")
```

### Example 3: Methodological focus
```
("machine learning" OR "artificial intelligence" OR "deep learning") 
AND ("diagnosis" OR "prediction" OR "classification") 
AND ("clinical validation" OR "external validation" OR "prospective")
```

**Documentation checklist:**
- [ ] Database searched (PubMed, Scopus, Web of Science, CINAHL, Embase, etc.)
- [ ] Date of search
- [ ] Filters applied (language, date range, study type)
- [ ] Number of results per database
- [ ] Deduplication method

---

## 4. Critical Appraisal Sentence Patterns

Use these patterns to write evaluative (not descriptive) prose. Replace bracketed content with study-specific details.

### Evaluating methodology
- "While [Author] employed [method], the reliance on [limitation] restricts the generalizability of these findings to [broader population]."
- "[Author]'s [design] strengthens the evidence for [claim], though the absence of [missing element] warrants cautious interpretation."
- "The cross-sectional nature of [Author]'s analysis precludes causal inference regarding [relationship]."

### Comparing across studies
- "In contrast to [Author1], who reported [finding], [Author2] observed [different finding], a discrepancy likely attributable to [methodological/population difference]."
- "These findings align with [Author1] and [Author2] but diverge from [Author3], whose [specific methodological choice] may account for the difference."
- "Collectively, these studies suggest [pattern], although heterogeneity in [variable] across designs complicates direct comparison."

### Identifying gaps
- "Despite growing interest in [topic], no study to date has examined [specific gap] in [specific context]."
- "The existing evidence base is limited by [common limitation across studies], indicating a need for [type of study needed]."
- "While [number] studies have addressed [broad topic], the specific relationship between [X] and [Y] in [Z population] remains unexplored."

### Transitioning to the current study
- "Given the [inconsistent/limited/preliminary] evidence regarding [topic], the present study aims to [objective]."
- "Building on the work of [key authors], this study extends the evidence by [what is new: population, method, outcome]."
- "To address this gap, we [designed/conducted] a [study type] examining [specific focus]."

---

## 5. Thematic Organization Patterns

When grouping studies into themes, consider these organizing structures:

- **By outcome:** Group studies that measured the same or similar outcomes, then compare methods and findings across them.
- **By population:** Group studies by patient/participant characteristics to reveal whether findings vary across subgroups.
- **By methodology:** Group studies by design type (RCT vs. observational vs. qualitative) to evaluate how method choice influences findings.
- **By temporal sequence:** When a field has evolved substantially, organize chronologically to show how understanding has developed.

Select the structure that best serves your research question. Thematic organization is almost always preferable to a study-by-study summary.

## Related Hubs

- [Folder index hub](../../docs/FOLDER_INDEX.md)
- [All notes index](../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../docs/GRAPH_CONNECTIVITY_MAP.md)

## Parent skills (auto)

- [[SKILL_literature-synthesis]]

## Related playbooks (auto)

- [[ai_detection_patterns]]
- [[ai_phrase_replacements]]
- [[bayesian_code_templates]]
- [[consort_checklist_items]]
- [[meta_analysis_code_templates]]
- [[OBSIDIAN_AGENT_PLAYBOOK]]
- [[r_statistics_coding]]
- [[r_statistics_packages]]
