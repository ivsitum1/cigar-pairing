# AI writing pattern checklist (detection + revision)

**Purpose:** Natural academic prose and accuracy. Not for circumventing plagiarism or AI-detection policies.

**Sources:** `ai-check`, `humanize-ai-text` (Wikipedia Signs of AI Writing), NotebookLM grill export `humanize_ai_query_batch.json` (2026-06-16, gate GO).

**Scanner:** `30_system/behavior_rules/tools/ai_pattern_scan.py` + `ai_detection_patterns.json`

---

## Critical patterns (fix first)

| Category | Examples / signals |
|----------|-------------------|
| Citation bugs | `oaicite`, `turn0search`, `contentReference`, `oai_citation`, `attached_file` |
| Unicode chatbot placeholders | `cite turn0search`, DeepSeek `【†L…】`, `:::writing{variant=…}` |
| UTM tracking URLs | `utm_source=chatgpt.com`, `utm_source=openai` |
| Knowledge cutoff | "as of my last training", "based on available information", "not widely documented" |
| Chatbot artifacts | "I hope this helps", "Great question!", "As an AI" |
| Markdown in manuscript | `**bold**`, `## headers`, fenced code in journal-bound prose |

---

## High-signal vocabulary

**AI clusters:** delve, tapestry, landscape, pivotal, vibrant, underscore, meticulous, bolster, foster, showcase  
**Copula avoidance:** "serves as", "stands as", "boasts", "features" instead of is/are/has  
**Significance inflation:** "marking a pivotal moment", "stands as a testament", "reflects a broader movement", "indelible mark"  
**Phantom denials:** "this is not to say", "we do not claim", "does not mean that", "nije riječ o", "ne znači da" (negating claims nobody made)  
**Syntactic inflation:** "in the context of", "plays a critical role in", "a comprehensive", "it is worth emphasizing"  
**Pseudo-commitment:** "central to", "crucial to", "intricate interplay", "underscores the importance" (without data)  
**Promotional:** groundbreaking, nestled, breathtaking, game-changing, vibrant heritage  
**Transitions (overuse):** furthermore, moreover, additionally, consequently, subsequently, nevertheless  
**Phrases:** "it is important to note that", "in order to", "with respect to", "due to the fact that"

---

## Structural signals

| Signal | Description |
|--------|-------------|
| Low burstiness | Sentences cluster at 15–25 words with low variance |
| Rule of three | Forced triplets: "lightweight, flexible, and low-cost" |
| Inline-header lists | `**Topic:** description` bullet format rare in human drafts |
| Negative parallelisms | "Not only X, but also Y" chains |
| Topic-sentence formula | Every paragraph: topic + support + mini-conclusion |
| Challenges formula | "Despite these challenges… future outlook" closings |

---

## Statistical signals (detector theory)

- **Perplexity:** low randomness / high predictability → higher AI score (GPTZero)
- **Burstiness:** uniform rhythm → machine-like; humans mix short and long sentences
- **False positives:** ESL writers, formulaic human text (e.g. legal/constitutional), technical manuals

**Institutional thresholds:** often 20–25% triggers review; treat scores as probability, not proof.

---

## Academic Methods exception

- Passive voice and standard hedging (**may**, **likely**, **suggest**) are acceptable in Methods when journal style requires them.
- Do **not** replace field-specific terms or verified statistics to sound "more human."
- Deepen Methods with protocol-specific detail, not marketing vocabulary.

---

## Revision order (15 steps, meaning-preserving first)

### Phase 0 — Phantom denial and verbosity trim
0. Remove negations of claims nobody made; cut prefix disclaimers; trim non-Methods sentences >35 words

### Phase 1 — Technical cleanup
1. Remove citation/Unicode chatbot artifacts  
2. Strip markdown not required by journal  
3. Fix or delete broken reference codes  
4. Clean UTM parameters from URLs  

### Phase 2 — Lexical / stylistic
5. Replace AI vocabulary clusters with plain field terms  
6. Delete significance puffery  
7. Trim sentence-initial Furthermore/Moreover/In conclusion  
8. Restore simple copulas (is/are/has)  

### Phase 3 — Structural
9. Break rule-of-three triplets  
10. Vary sentence length (add short punchy lines)  
11. Convert inline-header lists to prose  

### Phase 4 — Semantic (higher fact risk)
12. Add verified technical detail only  
13. Add qualified edge cases where literature supports them  
14. Insert original analysis / scaffolding (HAT method)  
15. Rewrite paragraphs from meaning, not surface swap  

---

## Mixed authorship boundary

Detectors struggle when human and AI passages alternate in one document. Flag **section-level** scores separately; do not treat a low-AI Methods block as proof the whole manuscript is human-written. Use `check_ai_plagiarism.py` batch mode per section when word count exceeds 1500.

---

1. Run `python ai_pattern_scan.py manuscript.txt --json`  
2. Run `check_ai_score_only(text)` from `check_ai_plagiarism.py`  
3. Target combined pattern score **< 0.20** before submission  
4. Re-check clinical/statistical facts unchanged (`99_error_memory`)

---

## Parent skills

- [[SKILL_ai-detection]]
- [[SKILL_avoid-ai-formulations]]
