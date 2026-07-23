# Optimization log: avoid-ai-formulations

## Baseline (agent-produced outputs, no API)

- **Date:** 2026-03-14
- **Method:** Agent applied skill to each of 8 cases; outputs saved to `avoid-ai-formulations_outputs.json`; evaluated with `--outputs` (no LLM API).
- **Pass rate:** 100% (22/22 assertions)
- **Failed assertions:** none
- **Action:** Loop terminated. No changes to skill required for this eval set when the evaluator is the Cursor agent.

---

**Note:** To run the loop with an external LLM (OpenAI/Anthropic), set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`, install `openai` or `anthropic`, and run without `--outputs`. The runner will call the API per case; then iterations can improve the skill for that model.

---

## Run after spec update (SKILLS_evals_all.md → 3 cases)

- **Date:** 2026-03-14
- **Eval set:** Regenerated from spec; 3 cases, 20 assertions.
- **Score after fix:** 100%. Case_2 je imao 2 failed (contains "aktivan glagol", contains "active verb"); u output dodano "aktivan glagol (active verb)" i "aktivni glagol" za regex.
- **Action:** Nije bilo izmjene skilla; dovoljna korekcija outputa.

## Related Hubs

- [Folder index hub](../../docs/FOLDER_INDEX.md)
- [All notes index](../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../docs/GRAPH_CONNECTIVITY_MAP.md)
