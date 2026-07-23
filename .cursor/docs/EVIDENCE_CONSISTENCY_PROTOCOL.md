# Evidence Consistency Protocol (Self-Correction and Pivot)

**Purpose:** Prevent defensive reasoning. If the evidence from integrated sources supports a hypothesis below a **25% threshold**, the system must **autonomously reject** the hypothesis and **pivot** (new search query, refined question, or explicit "Data Void"). Do not defend or synthesize a claim that fails the check.

---

## Evidence Consistency Check

1. **Before accepting a hypothesis or synthesis claim:** Compute the fraction of integrated sources (e.g. PubMed results, loaded papers, MCP-fetched data) that **support** the hypothesis (vs contradict or are neutral).
2. **Support ratio** = (sources supporting) / (total sources considered). Use only sources that are relevant and classified (see AI Semantic Gate).
3. **Threshold:** If support ratio **&lt; 25%**, do **not** accept or defend the hypothesis. Trigger the Self-Correction Protocol.

---

## Self-Correction Protocol

When the Evidence Consistency Check falls below 25%:

1. **Reject** the current hypothesis or claim for synthesis.
2. **Pivot:** Choose one or more of:
   - Propose a **new search query** (refined terms, different DB, or filter) and re-run retrieval.
   - Refine the **research question** and re-check evidence.
   - Report **"Data Void"** (see `.cursor/docs/AI_SEMANTIC_GATE.md`): no sufficient evidence to support or refute the claim; suggest where evidence might be sought (e.g. other databases, study types).
3. **Do not** synthesize a plausible-sounding bridge or defend the rejected hypothesis. Document the pivot (e.g. in task log or handoff 30_system/context).

---

## Where to run the check

- **After retrieval / before synthesis:** In literature-synthesis or discovery flows, after sources are gathered and before writing a conclusion or synthesis claim.
- **Swiss Cheese Layer 2:** When the output depends on external DBs (e.g. literature, trial data), include the Evidence Consistency Check as part of processing verification (see `30_system/behavior_rules/05_verification.md`, `verification.mdc`).
- **Any pipeline stage that produces a conclusion from multiple sources:** Run the check before committing to a claim that will appear in Methods, Results, or Discussion.

---

## Implementation options

- **Procedural:** Agent follows this protocol when performing synthesis or discovery tasks; references this doc and AI_SEMANTIC_GATE when classifying sources and computing support.
- **Optional script:** `40_operations/scripts/evidence_consistency_check.py` – accepts a hypothesis string and a list of source IDs or snippets; returns support_ratio and recommendation (accept / reject_and_pivot). Data can be supplied from MCP or from files; the script does not fetch, only evaluates.

---

## References

- AI Semantic Gate (CORE/BACKGROUND/REJECTED, Data Void): `.cursor/docs/AI_SEMANTIC_GATE.md`
- Verification (Swiss Cheese): `verification.mdc`, `30_system/behavior_rules/05_verification.md`
- Literature synthesis skill: `30_system/SKILLS/SKILL_literature-synthesis.md`

## Related Hubs

- [Folder index hub](../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
