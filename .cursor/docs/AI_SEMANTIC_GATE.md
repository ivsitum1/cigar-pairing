# AI Semantic Gate (Source Classification and Data Void)

**Purpose:** Classify every source used for synthesis or discovery as **CORE**, **BACKGROUND**, or **REJECTED**. If no CORE (or insufficient) evidence exists for a claim, report **"Data Void"** and do not invent a plausible bridge. Hallucination is strictly forbidden.

---

## Source classification

| Class | Meaning | Use in synthesis |
|-------|---------|------------------|
| **CORE** | Directly supports or contradicts the hypothesis or claim. Required for a conclusion. | Count toward Evidence Consistency Check; use for support ratio. |
| **BACKGROUND** | Provides context, methods, or tangential support. Useful but not sufficient alone for the claim. | May inform narrative; do not count as primary support for the 25% threshold. |
| **REJECTED** | Off-topic, unreliable, or fails quality check. | Do not use for synthesis. |

Apply this classification when processing papers, DB hits, or MCP-fetched content before running the Evidence Consistency Check or writing synthesis.

---

## Data Void

- **When:** No CORE evidence exists for a specific claim, or the Evidence Consistency Check is below the threshold and a pivot does not yield sufficient CORE evidence.
- **Action:** Report **"Data Void"** for that claim. Optionally suggest where evidence might be sought (e.g. other databases, study designs, or outcomes). Do **not** generate a plausible-sounding bridge or filler.
- **Wording:** e.g. "No sufficient evidence was found to support or refute [claim]. Data void; consider [suggested search or study type]."

---

## Integration

- Use with **Evidence Consistency Protocol** (`.cursor/docs/EVIDENCE_CONSISTENCY_PROTOCOL.md`): only CORE sources count toward the support ratio; REJECTED sources are excluded; BACKGROUND can inform but does not substitute for CORE.
- In **literature-synthesis** or **evidence-pivot** skill: add an optional checklist step: "Classify each source as CORE / BACKGROUND / REJECTED; if no CORE for claim X, output Data Void."

## Related Hubs

- [Folder index hub](../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
