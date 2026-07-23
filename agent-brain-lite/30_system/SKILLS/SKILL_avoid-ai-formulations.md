---
name: avoid-ai-formulations
description: Use for writing strategy and phrase-level revision; for automated AI score checking use ai-detection instead. Both can be used sequentially. Triggers include: avoid AI phrasing, natural writing, AI formulations, reduce AI score.
version: 1.4
last_updated: 2026-06-28
domain: writing
tokens: ~1000
triggers:
  - avoid AI phrasing
  - natural writing
  - AI formulations
  - reduce AI score
requires_packages: []
reference_files:
  - reference/ai_phrase_replacements.md
  - reference/ai_detection_patterns.md
  - reference/medical_research/medical-english-precision-editor/hard-rules.md
pipeline_position: [1, 4]
---

# Skill: Avoid AI Formulations in Writing

## When to use

Use this skill when:
- Writing or revising academic text
- Polishing a **non-academic** draft after `nonacademic-writer` (allowed Tier 3 pair)
- AI detection score is high (> 20%)
- Need to make writing sound more natural
- Before finalizing any manuscript or publish-ready blog post

## Prerequisites

- Text to revise
- AI detection tool (optional but recommended)

## Step-by-step procedure

0. **Phase 0 — Phantom denial and verbosity trim (before phrase swaps):**
   - Remove negations of claims nobody made ("this is not…", "we do not claim…").
   - Cut prefix disclaimers before the substantive answer.
   - For manuscript: enforce one job per sentence; trim sentences >35 words outside Methods.
   - Run `ai_pattern_scan.py` for `phantom_denials`, `syntactic_inflation`, `pseudo_commitment`.

1. **Identify AI formulations:**
   - Load `reference/ai_detection_patterns.md` for full category checklist (critical/high/medium signals).
   - Search for: "It is important to note that...", "In order to...", "It should be noted that..."
   - Look for excessive passive voice
   - Check for formulaic transitions
   - For medical prose: apply `reference/medical_research/medical-english-precision-editor/hard-rules.md` (fluency must not strengthen claims).

2. **Apply replacements:**
   - "It is important to note that..." → Remove or "Note that..."
   - "In order to..." → "To..."
   - "It should be noted that..." → Remove or "We note that..."
   - "It can be observed that..." → "We observed..." or directly state
   - Significance puffery ("stands as a testament", "pivotal moment") → concrete fact or delete
   - Copula avoidance ("serves as", "boasts") → is/are/has

3. **Phased revision (NotebookLM gate GO, 2026-06):**
   - Phase 0: phantom denials, defensive bloat, sentence-length trim (see above)
   - Phase 1: citation bugs, markdown, UTM URLs, cutoff phrases
   - Phase 2: AI vocabulary, puffery, transitions, copulas
   - Phase 3: rule-of-three, burstiness, inline-header lists
   - Phase 4: verified detail only (do not invent facts)

4. **Re-check:** `ai_pattern_scan.py` or `check_ai_score_only()` — target < 0.20
   - "It is evident that..." → "Evidently..." or directly state

3. **Vary sentence structure:**
   - Mix short (10-15 words) and longer (25-35 words) sentences
   - Vary declarative, complex, compound structures
   - Not every sentence needs to be perfectly balanced

4. **Add specific details:**
   - Use concrete examples and specific numbers
   - "10 studies with 831 participants" not "multiple studies"
   - "Egger's test (p=0.0003)" not just "publication bias was assessed"

5. **Natural transitions:**
   - Connect ideas through meaning, not just transition words
   - Occasionally omit transitions when connection is clear
   - Mix transition words: "Furthermore", "Moreover", "Also", "In addition"

6. **Check with AI detector:**
   - Run text through AI detector
   - Target: Score < 20%
   - If still high, repeat steps 2-5

## Honesty and grounding checkpoints

- Tag outputs internally; in manuscript deliverables keep prose clean (see `55_conversational_cognition.mdc`).
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Ova rečenica zvuči kao ChatGPT; zamijeni je akademski, bez šablonskih fraza."  
**Output:** "Zamjene predložim uz provjeru liste zabranjenih fraza `[EXTRACTED]`; ton discipline `[ASSUMPTION]` ako nema uzorka iz časopisa."

## Verification

- [ ] Phase 0: no phantom denials; manuscript sentences trimmed
- [ ] Removed all "It is important to note that..." constructions
- [ ] Replaced "In order to" with "To"
- [ ] Removed vague "It can be observed that..." phrases
- [ ] Varied sentence structure and length
- [ ] Added specific details and examples
- [ ] Mixed transition words
- [ ] Checked with AI detector (score < 20%)
- [ ] Maintained academic rigor and accuracy

## Related rules

- `.cursor/rules/55_conversational_cognition.mdc`
- `.cursor/rules/writing-avoid-ai.mdc`
- `30_system/behavior_rules/10_ai_writing_plagiarism.md`

## Learning integration

- **task_type:** writing
- **log_fields:** ai_score_before, ai_score_after, strategies_used
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)

## Skill reference graph (auto)

- [[ai_detection_patterns]]
- [[ai_phrase_replacements]]
- [[hard-rules]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
