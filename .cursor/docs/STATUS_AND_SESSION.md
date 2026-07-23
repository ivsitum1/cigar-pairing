# Status and Session Management

**Purpose:** Guidance on when to clear context or start a new session to maintain output quality. Cursor does not expose token usage to the workspace; this doc is guidance only unless you add a script that estimates from rule/skill file sizes.

---

## When to /clear or start a new session

- **After long runs:** Many tool calls or multiple pipeline stages in one session.
- **When output quality drops:** Repetition, loops, or off-topic answers.
- **When many rules and skills are loaded:** e.g. more than 8 rules active (see OVERLOAD in context-optimization.mdc).
- **After isolated task completion:** Consider session reset before starting a large new task.

---

## Lightweight heuristic

- If **Tier 0 + Tier 1 + Tier 2 + 2 or more skills** are loaded, consider a session reset after the current task.
- **Overload rule (context-optimization.mdc):** More than 5 rules → WARN; more than 8 → STOP and deactivate Tier 2/3 or ask user which to keep.

---

## No real-time status bar

There is no built-in token or context-usage widget. If you implement a small script that estimates context from rule/skill file sizes, you can run it periodically and use the result to decide when to /clear.

## Related Hubs

- [Folder index hub](../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
