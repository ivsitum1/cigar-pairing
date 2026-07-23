---
name: meeting-insights
description: Analyze meeting transcripts for decisions, action items, communication patterns, and follow-ups. Use for meeting insights, transcript summary, standup analysis.
version: 1.0
last_updated: 2026-05-18
domain: tools
tokens: ~550
triggers:
  - meeting insights
  - analyze transcript
  - meeting summary
  - action items from meeting
requires_packages: []
reference_files: []
conflicts_with: []
disambiguation: Use for meeting/transcript ops; not clinical CDSS.
pipeline_position: []
---

# Skill: Meeting insights

## When to use

- User provides meeting transcript or recording notes

## Procedure

1. **Participants and purpose** (from text only).
2. **Decisions** — explicit agreements.
3. **Action items** — owner, deadline if stated; else `[TO_CONFIRM]`.
4. **Open questions** — unresolved threads.
5. **Patterns (optional)** — only if user asked; avoid psychologizing.

## Verification

- [ ] No invented commitments
- [ ] Sensitive content flagged, not repeated unnecessarily

## Related

- `SKILL_create-sop.md` for recurring workflows

## Related Hubs

- [[Meeting insights skill]]
- [[Skills audit 2026-05]]
