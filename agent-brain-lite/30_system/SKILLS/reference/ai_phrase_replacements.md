# AI Phrase Replacements – Reference Data

**Used by:** `SKILL_avoid-ai-formulations.md`
**Source:** Extracted from skill process logic to reduce context load during execution.

---

## Phrase Replacement Table

| AI-flagged phrase | Replacement options |
|---|---|
| "It is important to note that..." | Remove entirely, or "Note that..." |
| "In order to..." | "To..." |
| "It should be noted that..." | Remove entirely, or "We note that..." |
| "It can be observed that..." | "We observed..." or state directly |
| "It is evident that..." | "Evidently..." or state directly |
| "Furthermore" (overused) | "Also", "In addition", "Moreover" (vary) |
| "In conclusion" (formulaic) | "Taken together", "Overall", or omit |
| "plays a crucial role" | "contributes to", "is central to", specific verb |
| "a comprehensive analysis" | "an analysis", "a detailed analysis" (if warranted) |
| "sheds light on" | "clarifies", "reveals", "demonstrates" |
| "it is worth mentioning" | Remove, or state the point directly |
| "the findings suggest" | "these results indicate", "the data show" |
| "a growing body of literature" | "recent studies", "several investigations" |
| "remains a significant challenge" | "is still difficult", specific challenge statement |
| "has garnered significant attention" | "has been widely studied", "is increasingly investigated" |

## Sentence Structure Guidelines

- Mix short (10-15 words) and longer (25-35 words) sentences
- Vary declarative, complex, and compound structures
- Not every sentence needs to be perfectly balanced
- Connect ideas through meaning, not just transition words
- Occasionally omit transitions when the connection is clear

## Specificity Rules

- Use concrete numbers: "10 studies with 831 participants" not "multiple studies"
- Include test statistics: "Egger's test (p=0.0003)" not "publication bias was assessed"
- Name methods: "random-effects meta-analysis using REML" not "statistical analysis"

## Related Hubs

- [Folder index hub](../../docs/FOLDER_INDEX.md)
- [All notes index](../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../docs/GRAPH_CONNECTIVITY_MAP.md)

## Parent skills (auto)

- [[SKILL_avoid-ai-formulations]]

## Related playbooks (auto)

- [[ai_detection_patterns]]
- [[bayesian_code_templates]]
- [[consort_checklist_items]]
- [[literature_synthesis_templates]]
- [[meta_analysis_code_templates]]
- [[OBSIDIAN_AGENT_PLAYBOOK]]
- [[r_statistics_coding]]
- [[r_statistics_packages]]
