> **⚠️ PARTIALLY MIGRATED:** AI formulation avoidance rules have been migrated to `.cursor/rules/writing-avoid-ai.mdc`.
> See `.cursor/rules/writing-avoid-ai.mdc` for specific formulations to avoid.
> This file is retained for comprehensive AI detection strategies and tools.

# AI Writing Detection and Plagiarism - Rules and Tools

## Purpose

This document establishes rules and guidelines for addressing AI writing detection and plagiarism issues in scientific writing. It ensures transparency, integrity and ethical use of AI tools.

---

## Problem: AI Writing Detection and Plagiarism

### Challenges

1. **AI Writing Detection**:
   - Journals and reviewers check if text is AI-written
   - Excessive AI use may be considered unethical
   - Transparency about AI tool usage is needed

2. **Plagiarism**:
   - Accidental copying of text without citation
   - Excessive reliance on sources without own contribution
   - Self-plagiarism (reusing own work)

3. **Similarity Check**:
   - Checking similarity with existing works
   - Checking similarity within own work
   - Checking similarity with AI-generated content

---

## Rules for Using AI Tools

### Transparency

**MANDATORY:**

- [ ] **Declare AI tool usage**: In manuscript or cover letter
- [ ] **List tools used**: Which AI tools were used
- [ ] **Describe usage method**: How tools were used (drafting, editing, etc.)
- [ ] **Emphasize human control**: All outputs reviewed and approved by authors

**Declaration Format:**

```markdown
## AI Tool Usage Declaration

The authors acknowledge the use of AI tools (specifically [tool names]) 
in the preparation of this manuscript. These tools were used for:
- [Purpose 1, e.g., "drafting initial versions of the methods section"]
- [Purpose 2, e.g., "language editing and grammar checking"]
- [Purpose 3, e.g., "reference formatting"]

All AI-generated content was reviewed, edited, and approved by the authors. 
The authors take full responsibility for the content of this manuscript.
```

### Limitations

**DO NOT use AI for:**

- ❌ Generating facts or data
- ❌ Fabricating references
- ❌ Generating statistical results
- ❌ Replacing critical thinking
- ❌ Generating entire paper without human control

**ALLOWED to use AI for:**

- ✅ Drafting assistance (with human review)
- ✅ Language editing and grammar checking
- ✅ Reference formatting
- ✅ Text structuring
- ✅ Generating outline (with human review)

---

## AI Writing Detection - Tools and Methods

### Recommended Tools

#### 1. GPTZero
- **URL**: https://gptzero.me/
- **Purpose**: Detection of AI-generated text
- **How to use**: Upload text or paste directly
- **Result**: Score (0-1) and highlighted sections
- **Free**: Yes (with limitations)
- **Precision**: High for GPT-3.5/4 text

#### 2. OpenAI AI Text Classifier
- **URL**: https://platform.openai.com/ai-text-classifier
- **Purpose**: Detection of AI-generated text
- **How to use**: Paste text (min 1000 characters)
- **Result**: Probability that text is AI-generated
- **Free**: Yes
- **Precision**: Moderate (may be false positive)

#### 3. Writer.com AI Content Detector
- **URL**: https://writer.com/ai-content-detector/
- **Purpose**: Detection of AI-generated text
- **How to use**: Paste text
- **Result**: Percentage of AI-generated content
- **Free**: Yes
- **Precision**: Moderate

#### 4. Copyleaks AI Content Detector
- **URL**: https://copyleaks.com/ai-content-detector
- **Purpose**: Detection of AI-generated text
- **How to use**: Upload or paste
- **Result**: Detailed analysis with highlighted sections
- **Free**: Limited (free version)
- **Precision**: High

#### 5. Turnitin AI Writing Detection
- **URL**: https://www.turnitin.com/solutions/ai-writing
- **Purpose**: Detection of AI-generated text (integrated with plagiarism checker)
- **How to use**: Through Turnitin platform
- **Result**: AI writing score
- **Free**: No (requires subscription)
- **Precision**: High (industry standard)

### Workflow for AI Writing Detection

```
1. BEFORE SUBMISSION
   ├── Check entire manuscript with AI detector
   ├── Identify sections with high AI score (> 20%)
   ├── Note specific AI indicators (mechanical precision, formulaic organization, etc.)
   └── Revise those sections using natural academic writing strategies

2. SECTION REVISION
   ├── Rewrite sections with high AI score
   ├── Apply natural writing strategies (see below)
   ├── Maintain academic standards (third-person, passive, formal)
   ├── Add own style and voice (within academic bounds)
   └── Check again with AI detector

3. FINAL CHECK
   ├── Check with multiple AI detectors (cross-validation)
   ├── Ensure AI score is acceptable (< 20% for all sections)
   ├── Verify academic quality maintained
   └── Document check results
```

### Identifying AI Writing Patterns

**Common AI Indicators (from independent checkers):**

1. **Mechanical Precision**: Overly precise and technical word choice that sounds robotic
2. **Formulaic Organization**: Overly structured text with predictable headings and sections
3. **Robotic Formality**: Overly formal and polished writing that lacks variation
4. **Impersonal Tone**: Overly formal tone (note: impersonal is correct for academic writing, but can be robotic)
5. **Technical Jargon**: Overuse of technical terms and complex sentence structures
6. **Overly Formal**: Grammatically perfect but overly formal structures
7. **Mechanical Transitions**: Formulaic transitional phrases in predictable patterns
8. **Sophisticated Clarity**: Overly precise word choice prioritizing sophistication
9. **Lacks Creativity**: Writing lacks subtle creative variations
10. **Lacks Creative Grammar**: Grammatically correct but predictable structures
11. **Predictable Syntax**: Limited syntax patterns with repetitive structures

**Our checker limitations:**
- Our `check_ai_plagiarism.py` may not detect all these patterns
- Use independent checkers (GPTZero, Copyleaks, etc.) for validation
- Cross-validate with multiple tools
- Focus on patterns identified by independent checkers

### Strategies for Reducing AI Score

**CRITICAL:** These strategies maintain academic rigor, third-person/passive voice, and formal tone while making writing sound more natural and human.

#### 1. Add Own Style (Natural Academic Voice)
   - Use own formulations, not AI-generated templates
   - Add personal insights and interpretations (within academic bounds)
   - Use specific terminology from the field with natural variation
   - Allow subtle voice: Not every statement needs to be perfectly balanced

#### 2. Variation in Structure (Reduce Formulaic Patterns)
   - **Sentence length**: Mix short (10-15 words) and longer (25-35 words) sentences
   - **Sentence structures**: Vary declarative, complex, compound structures
   - **Paragraph structure**: Break perfect paragraph symmetry (allow some asymmetry)
   - **Paragraph lengths**: Vary from 3-4 sentences to 6-8 sentences
   - **Section introductions**: Not every section needs "This section describes..."

#### 3. Add Specific Details (Reduce Abstract Formulations)
   - Concrete examples from own experience or data
   - Specific numbers and data: "10 studies with 831 participants" not just "multiple studies"
   - References to specific studies with context
   - Methodological specifics: "Egger's test (p=0.0003)" not just "publication bias was assessed"

#### 4. Human Editing (Critical Step)
   - Thorough human review of all AI-generated content
   - Rewriting AI-generated parts with natural academic voice
   - Adding own voice while maintaining academic standards
   - Checking with multiple AI detectors after revision

#### 5. Agency-Based Humanization (CRITICAL - Agency, NOT emotion)
   - **Visible agency**: Replace "The study found" with "We found" or "Our analysis showed" (if journal allows)
   - **Methodological transparency**: "We performed sensitivity analyses across all outcome definitions" not "Sensitivity analyses confirmed"
   - **Ownership of uncertainties**: "Our data don't allow us to determine" not "It is unclear"
   - **Accountability**: "We chose X because..." not just "X was chosen"
   - **Ownership of limitations**: "Our sample size limits our ability to..." not "Sample size was small"

#### 6. AVOID (Anti-Human Signals)
   - ❌ Performative emotions: "I'm frustrated", "This is frustrating", "I'm surprised"
   - ❌ Subjective hedges: "I think", "I believe", "I'm not entirely sure", "unclear to me"
   - ❌ Personal sentiments: These are WORSE than AI - they signal unprofessional writing

#### 7. Natural Transitions (Reduce Mechanical Patterns)
   - **Mix transition words**: "Furthermore", "Moreover", "Additionally" → also use "Also", "In addition", "Similarly"
   - **Content-based transitions**: Connect ideas through meaning, not just transition words
   - **Occasionally omit transitions**: Not every paragraph needs a transition word when connection is clear
   - **Varied transition patterns**: Some paragraphs start with data, others with interpretation
   - **Avoid formulaic patterns**: Not always "X. Furthermore, Y. Additionally, Z."

#### 8. Terminology Variation (Subtle Natural Variation)
   - Use slight variations in technical terms (within reason): "heterogeneity" → occasionally "variability"
   - Avoid excessive semantic consistency that feels unnatural
   - Allow natural human variation in expression
   - Mix sophisticated and accessible language: "demonstrate" → occasionally "show"

#### 9. Reduce Mechanical Precision (While Maintaining Accuracy)
   - **Mix precision levels**: "approximately 10 studies" occasionally instead of always "exactly 10 studies"
   - **Natural phrasing**: "Analysis showed" occasionally instead of always "The statistical analysis demonstrated"
   - **Slightly less formal synonyms**: "utilize" → "use", "facilitate" → "help" (occasionally)
   - **Never sacrifice accuracy**: Statistical claims and methods must remain precise

#### 10. Reduce Robotic Formality (Natural Academic Tone)
   - **Vary formality levels**: Mix "It was observed that" with "Observations showed"
   - **Direct statements**: "The effect was significant" instead of always "It was observed that the effect demonstrated statistical significance"
   - **Natural academic phrasing**: "Several studies reported" instead of always "A number of studies in the literature have reported"
   - **Reduce hedging when appropriate**: "The results indicate" instead of always "The results appear to indicate"
   - **Maintain academic tone**: Never become casual or subjective

#### 11. Creative Grammar (Within Academic Standards)
   - **Vary clause structures**: Some sentences with multiple clauses, some simpler
   - **Mix active and passive**: Not always passive voice (when journal allows active)
   - **Vary sentence length**: Short (10-15 words) to longer (25-35 words)
   - **Varied punctuation**: Occasional semicolons, dashes for emphasis
   - **Natural flow**: Not every sentence needs to be perfectly structured
   - **Never incorrect grammar**: Maintain grammatical correctness

#### 12. Reduce Predictable Syntax
   - **Vary sentence types**: Mostly declarative, but occasional complex structures
   - **Mix sentence patterns**: Subject-verb-object, but also varied structures
   - **Varied clause orders**: Main clause first, subordinate first, embedded clauses
   - **Break patterns**: Not every sentence follows the same structure
   - **Maintain clarity**: Never sacrifice understanding

#### 13. Reduce Over-Sophisticated Clarity
   - **Mix sophisticated and accessible**: "demonstrate" → occasionally "show"
   - **Natural academic phrasing**: "The findings indicate" instead of always "The findings demonstrate with clarity"
   - **Occasional simpler phrasing**: When meaning is clear, simpler is better
   - **Vary vocabulary**: Not always the most sophisticated word
   - **Never sacrifice clarity**: Always maintain understanding

#### 14. Add Subtle Creativity (Within Academic Bounds)
   - **Vary sentence rhythm**: Mix short and long sentences
   - **Varied paragraph structures**: Some analytical, some descriptive, some interpretive
   - **Occasional rhetorical questions**: "What might explain this discrepancy?" (in discussion)
   - **Vary emphasis**: Some statements more direct, others more nuanced
   - **Natural academic voice**: Not every statement needs to be perfectly balanced
   - **Never sacrifice standards**: Maintain academic objectivity

**Core Principle:** Human writing in academic work = Visible agency through methodology and transparency, NOT through emotions. Natural variation within academic standards distinguishes human writing from AI-generated text.

**Balance is Key:**
- Use these strategies OCCASIONALLY, not always
- Maintain academic standards: Never sacrifice accuracy, clarity, or objectivity
- Keep third-person and passive voice (academic standard, unless journal prefers active)
- Vary patterns naturally: Not every sentence needs variation
- Check with AI detectors: Verify that changes reduce AI score while maintaining quality

**See:** `tools/learning_ai_writing_detection.md` and `AI_AGENTS_UPDATE_GUIDE.md` for detailed agency-based approach.

---

## Plagiarism Detection - Tools and Methods

### Recommended Tools

#### 1. Turnitin
- **URL**: https://www.turnitin.com/
- **Purpose**: Plagiarism detection and similarity checking
- **How to use**: Upload document
- **Result**: Similarity report with sources
- **Free**: No (requires subscription, often available through institutions)
- **Precision**: High (gold standard)

#### 2. iThenticate
- **URL**: https://www.ithenticate.com/
- **Purpose**: Plagiarism detection for scientific papers
- **How to use**: Upload document
- **Result**: Detailed similarity report
- **Free**: No (requires subscription)
- **Precision**: High (industry standard for science)

#### 3. Grammarly Plagiarism Checker
- **URL**: https://www.grammarly.com/plagiarism-checker
- **Purpose**: Plagiarism detection
- **How to use**: Paste text or upload
- **Result**: Similarity report
- **Free**: Limited (free version)
- **Precision**: Moderate to high

#### 4. Copyleaks
- **URL**: https://copyleaks.com/
- **Purpose**: Plagiarism detection and AI content detection
- **How to use**: Upload or paste
- **Result**: Detailed report with sources
- **Free**: Limited (free version)
- **Precision**: High

#### 5. PlagScan
- **URL**: https://www.plagscan.com/
- **Purpose**: Plagiarism detection
- **How to use**: Upload document
- **Result**: Similarity report
- **Free**: Limited (free version)
- **Precision**: Moderate to high

#### 6. Quetext
- **URL**: https://www.quetext.com/
- **Purpose**: Plagiarism detection
- **How to use**: Paste text
- **Result**: Similarity report with sources
- **Free**: Limited (free version)
- **Precision**: Moderate

### Workflow for Plagiarism Detection

```
1. BEFORE STARTING WRITING
   ├── Check own previous works (self-plagiarism)
   ├── Identify key references
   └── Plan own formulations

2. DURING WRITING
   ├── Cite all sources immediately
   ├── Use own formulations
   └── Check sections based on other works

3. BEFORE SUBMISSION
   ├── Check entire manuscript with plagiarism checker
   ├── Identify sections with high similarity
   ├── Revise problematic sections
   └── Check again

4. FINAL CHECK
   ├── Check with multiple plagiarism checkers
   ├── Ensure similarity score is acceptable (< 15-20%)
   └── Document check
```

### Acceptable Similarity Scores

| Content Type | Acceptable Score | Action Needed |
|--------------|------------------|---------------|
| **Original text** | < 10% | No action |
| **With citations** | 10-20% | Check citations |
| **With methods** | 15-25% | Verify methods are standard |
| **High score** | > 25% | **MANDATORY REVISION** |

**Note**: 
- Methods sections may have higher score due to standard formulations
- Reference lists are not counted in similarity
- Citations are not counted in similarity (if properly formatted)

---

## Combined Approach: AI + Plagiarism Detection

### Recommended Workflow

```
1. DRAFTING PHASE
   ├── Use AI for drafting assistance (with transparency)
   ├── Check AI score of sections
   └── Revise to sound more natural

2. REVISION PHASE
   ├── Check plagiarism (similarity check)
   ├── Check AI writing detection
   ├── Revise problematic sections
   └── Check again

3. FINAL PHASE
   ├── Final check with multiple tools
   ├── Document all checks
   └── Declare AI tool usage (if applicable)
```

### Integrated Tools

#### Turnitin (Recommended for Institutions)
- **AI Writing Detection**: ✅
- **Plagiarism Detection**: ✅
- **Similarity Check**: ✅
- **Integration**: With learning management systems
- **Price**: Subscription (often available through institutions)

#### Copyleaks (Recommended for Individual Users)
- **AI Writing Detection**: ✅
- **Plagiarism Detection**: ✅
- **Similarity Check**: ✅
- **Integration**: API available
- **Price**: Freemium model

---

## Best Practices

### 1. Transparency

- **Always declare** AI tool usage
- **Be specific** about how tools were used
- **Emphasize human control** and responsibility

### 2. Regular Checking

- **Check during writing**, not just at the end
- **Use multiple tools** for cross-validation
- **Document checks** in changelog

### 3. Revision of Problematic Sections

- **Do not ignore high scores**
- **Rewrite sections** with high AI score
- **Add own style** and voice

### 4. Citation

- **Cite all sources** immediately
- **Use own formulations** even when citing ideas
- **Verify citations are accurate**

### 5. Self-Plagiarism

- **Check own previous works**
- **Do not copy from own works** without citation
- **Consider permission** for reuse

---

## Pre-Submission Checklist

### AI Writing Detection

- [ ] Entire manuscript checked with AI detector
- [ ] AI score < 20% for all sections
- [ ] Problematic sections revised
- [ ] Checked with multiple tools (cross-validation)
- [ ] AI usage declaration prepared (if applicable)

### Plagiarism Detection

- [ ] Entire manuscript checked with plagiarism checker
- [ ] Similarity score < 20% (or acceptable for paper type)
- [ ] All sources properly cited
- [ ] Self-plagiarism checked
- [ ] Problematic sections revised
- [ ] Checked with multiple tools (cross-validation)

### Documentation

- [ ] All check results recorded
- [ ] Actions taken for problematic sections documented
- [ ] AI usage declaration prepared (if applicable)
- [ ] Changelog current

---

## Ethical Aspects

### When is AI Use Acceptable?

✅ **ACCEPTABLE:**
- Drafting assistance (with human review)
- Language editing
- Formatting
- Structuring
- Generating outline (with human review)

❌ **UNACCEPTABLE:**
- Generating entire paper without human control
- Generating facts or data
- Fabricating references
- Replacing critical thinking
- Hiding AI tool usage

### Author Responsibility

**Author is always responsible for:**
- Content accuracy
- Work integrity
- Ethical use of tools
- Transparency about AI tool usage

---

## Practical Implementation

### Python Script for Automation

**Available script**: `tools/check_ai_plagiarism.py`

Complete Python script for checking AI writing and plagiarism. See `tools/README_tools.md` for detailed instructions.

#### Basic Usage

```bash
# Check manuscript
python tools/check_ai_plagiarism.py manuscript.txt

# With custom output directory
python tools/check_ai_plagiarism.py manuscript.txt --output-dir results/

# With selected tools
python tools/check_ai_plagiarism.py manuscript.txt --tools gptzero,local_similarity
```

#### Installation

```bash
# Install requirements (optional, for advanced features)
pip install -r tools/requirements.txt
```

#### API Keys (Optional)

```bash
# Windows PowerShell
$env:GPTZERO_API_KEY="your_key"
$env:OPENAI_API_KEY="your_key"
$env:COPYLEAKS_API_KEY="your_key"

# Linux/Mac
export GPTZERO_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
export COPYLEAKS_API_KEY="your_key"
```

#### Output

Script generates:
- `ai_plagiarism_report.json`: JSON format with detailed results
- `ai_plagiarism_report.txt`: Human-readable text report

#### Available Tools

**AI Writing Detection:**
- `gptzero`: GPTZero check (fallback method)
- `openai`: OpenAI AI Text Classifier (requires API key)

**Plagiarism Detection:**
- `copyleaks`: Copyleaks check (requires API key)
- `local_similarity`: Local similarity check with reference texts

#### Workflow Integration Example

```r
# R script calling Python script
system("python tools/check_ai_plagiarism.py manuscript.txt --output-dir results/")
```

See `tools/README_tools.md` for detailed instructions and examples.

---

## Recommendations for Different Scenarios

### Scenario 1: Writing from Scratch

1. **Drafting**: Use AI for assistance (with transparency)
2. **Revision**: Check AI score and revise
3. **Finalization**: Check plagiarism and AI writing
4. **Submission**: Declare AI tool usage

### Scenario 2: Revision of Existing Paper

1. **Check**: Check existing paper with AI and plagiarism checker
2. **Identification**: Identify problematic sections
3. **Revision**: Rewrite problematic sections
4. **Finalization**: Check again

### Scenario 3: Before Submission

1. **Final check**: Check with multiple tools
2. **Documentation**: Record all results
3. **Declaration**: Prepare AI usage declaration (if needed)
4. **Changelog**: Update changelog with checks

---

## References and Resources

### Articles on AI Writing Detection

- "AI Writing Detection: Current State and Future Directions" (2024)
- "Ethical Use of AI in Academic Writing" (2024)
- "Plagiarism Detection in the Age of AI" (2024)

### Journal Guidelines

- Check specific journal guidelines on AI usage
- Some journals have specific declaration requirements
- Some journals prohibit AI tool usage

### Tools and Services

- See recommended tools above
- Check availability through institution (Turnitin, iThenticate)
- Consider combination of free and paid tools

---

**Version:** 3.0  
**Last updated:** 2026-04-10  
**Status:** Rules and recommendations for AI writing detection and plagiarism

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
