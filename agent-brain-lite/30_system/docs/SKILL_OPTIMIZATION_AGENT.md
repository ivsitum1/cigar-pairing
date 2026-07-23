# Autonomous Skill Optimization Agent

**Obsidian hub:** `20_knowledge/wiki/concepts/Autonomous Skill Optimization Agent.md` (backlinks to eval schema and safety gates).  
**Regression ingest from real failures:** `40_operations/scripts/skill_gap_ingest.py` and `30_system/docs/SKILL_GAP_PIPELINE.md`.  
**Loop arming:** `40_operations/scripts/skill_gap_optimize_gate.py` (`run_optimization_loop`, default cutoff 72).

This document describes how to run the **autonomous skill optimization loop**: the agent iteratively improves a Cursor skill (`SKILL_*.md`) by running it against binary evals, modifying the skill when assertions fail, and committing only when the pass rate improves. The loop does not pause for permission until pass rate reaches 100% or the user interrupts.

---

## When to run

- You want to improve a specific skill’s behaviour on **deterministic** criteria (forbidden phrases, word count, required strings, structure).
- You have prepared **evals** for that skill in `30_system/SKILLS/evals/<skill_id>.json` (see [30_system/SKILLS/evals/README.md](../30_system/SKILLS/evals/index.md)).

**Evaluation method:** Optimization uses **agent-only evaluation** (no external API). The agent applies the skill to each test case, writes outputs to a JSON file, then runs the eval runner with `--outputs` to compute pass rate. No tokens are spent on external API calls.

**Not suitable for:** Subjective quality (tone, “naturalness”). Those remain human-reviewed.

**Process vs outcome (SkillCoach, arXiv:2607.01874):** Outcome-only evals can miss bad skill selection or composition that still passes by trial-and-error. Run `skill_process_rubric.py` on trajectory JSONL before trusting pass rate:

```bash
python 40_operations/scripts/skill_process_rubric.py --trace 90_archive/artifacts/<run_id>/trajectory.jsonl --json
```

Flag `process_outcome_gap: true` when task succeeded but process_score < 60.

---

## Setting the skill

- **Environment:** Set `SKILL_ID` to the skill id (e.g. `avoid-ai-formulations`). Must match the id in `30_system/SKILLS/registry.json`.
- **CLI:** The eval runner accepts `--skill-id <id>`. The agent should pass the same id when calling the script.

Example: optimize the avoid-ai-formulations skill:

```bash
export SKILL_ID=avoid-ai-formulations
```

---

## Autonomy rules (agent behaviour)

Once the loop has started:

1. **Do not stop to ask** “should I continue?” or “proceed?”. Keep iterating.
2. **Terminate only when:**
   - Pass rate is **100%**, or
   - The user **manually interrupts** (e.g. stops the agent or cancels the run).
3. **One change per iteration:** Make a single, specific edit to the skill file aimed at the current failed assertions (e.g. add a “Never output X” rule or a step that addresses one failure). This keeps cause–effect clear and makes reverts meaningful.
4. **Commit only on improvement:** If the new score is **strictly greater** than the previous best, run `git add 30_system/SKILLS/SKILL_<id>.md` and `git commit` with the message convention below. If the score did not improve, revert the file (`git checkout -- 30_system/SKILLS/SKILL_<id>.md`) and try a **different** modification in the next iteration.

---

## Loop steps (agent flow)

1. **Initialize**
   - Read `30_system/SKILLS/SKILL_<id>.md` and `30_system/SKILLS/evals/<id>.json`.
   - **Produce outputs:** For each case in evals, apply the skill to the case input and write the revised text. Save to `30_system/SKILLS/evals/<id>_outputs.json` as `{"case_1": "text", "case_2": "text", ...}`.
   - **Run baseline:**  
     `python 40_operations/scripts/skill_eval_runner.py --skill-id <id> --outputs 30_system/SKILLS/evals/<id>_outputs.json --json`  
     (no API; evaluation only).
   - Parse pass rate and list of failed assertions. Set **best_score** = baseline pass rate.

2. **Iterate**
   - **Modify:** Edit `30_system/SKILLS/SKILL_<id>.md` in one specific way to address one or more failed assertions.
   - **Produce outputs again:** Re-apply the (modified) skill to each case; overwrite `30_system/SKILLS/evals/<id>_outputs.json`.
   - **Evaluate:** Run the eval runner with `--outputs 30_system/SKILLS/evals/<id>_outputs.json --json`; parse the new pass rate and failed_assertions list.
   - **Decision:**
     - If new pass rate **> best_score:**  
       `git add 30_system/SKILLS/SKILL_<id>.md` and  
       `git commit -m "skill-optim: <brief description> pass <X>%"`.  
       Set **best_score** = new pass rate. Append to the iteration log.
     - If new pass rate ≤ best_score:  
       `git checkout -- 30_system/SKILLS/SKILL_<id>.md` (revert). Try a different modification in the next iteration (e.g. different phrase or different section).
   - **Termination:** If pass rate is 100%, stop. Otherwise continue until the user interrupts.

3. **Logging**  
   After each iteration, append to the iteration log (see below): iteration number, short description of the change, score before/after, and whether the change was committed or reverted.

---

## Log location

- **Path:** `30_system/SKILLS/evals/<skill_id>_optimization_log.md`  
  Example: `30_system/SKILLS/evals/avoid-ai-formulations_optimization_log.md`
- **Content (append each iteration):**
  - Iteration number
  - One-line description of the change
  - Score before / score after
  - Commit (with message) or Revert

Example entry:

```markdown
## Iteration 3
- **Change:** Added explicit "Never output 'It is important to note that'." to step 2.
- **Score:** 72% → 78%
- **Action:** Committed as `skill-optim: add never-output rule pass 78%`
```

---

## Commit message convention

Use a short, consistent format so history is scannable:

```
skill-optim: <brief description> pass <X>%
```

Examples:

- `skill-optim: add never 'in order to' rule pass 85%`
- `skill-optim: require specific numbers in step 4 pass 92%`

---

## Eval runner usage (optimization loop only – no API)

- **Always use pre-produced outputs.** The agent applies the skill to each case, saves outputs to `30_system/SKILLS/evals/<id>_outputs.json`, then runs:
  `python 40_operations/scripts/skill_eval_runner.py --skill-id <id> --outputs 30_system/SKILLS/evals/<id>_outputs.json --json`
- **No API calls.** The runner only evaluates assertions on the provided outputs; no `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is used in the optimization loop.
- **Machine-readable output:** With `--json`, the script prints pass rate, passed/total assertions, and `failed_assertions` list to stdout.

---

## File reference

| Item | Path |
|------|------|
| Skill instructions (edited by loop) | `30_system/SKILLS/SKILL_<id>.md` |
| Test cases and assertions | `30_system/SKILLS/evals/<id>.json` |
| Agent-produced outputs (per iteration) | `30_system/SKILLS/evals/<id>_outputs.json` |
| Eval schema and assertion types | [30_system/SKILLS/evals/README.md](../30_system/SKILLS/evals/index.md) |
| Iteration log | `30_system/SKILLS/evals/<id>_optimization_log.md` |
| Eval runner script | `40_operations/scripts/skill_eval_runner.py` |
| Optional: generate evals from skill | `40_operations/scripts/generate_evals_from_skill.py` (Phase 0) |

---

## Limitations

- **Binary assertions only:** Best for formatting, word limits, forbidden/required phrases. Subjective quality still needs human review.
- **Possible local optima:** If the score stops improving, the agent should try alternative edits (different section or phrasing); after many failed attempts, document and stop or escalate to the user.
- **Agent as evaluator:** Optimization uses only the Cursor agent’s outputs (no external LLM API). For evaluation with an external API, run the runner without `--outputs` and with the relevant API key set; that mode is outside the optimization loop.

## Related Hubs

- [Folder index hub](FOLDER_INDEX.md)
- [All notes index](ALL_NOTES_INDEX.md)
- [Graph connectivity map](GRAPH_CONNECTIVITY_MAP.md)
