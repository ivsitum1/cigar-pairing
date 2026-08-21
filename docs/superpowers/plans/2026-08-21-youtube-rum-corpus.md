# YouTube Rum Corpus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a local yt-dlp pipeline that inventories `@StevetheBarmanUK`, fetches EN captions, classifies videos, and emits rum↔catalog match proposals — without writing transcripts into the PWA or auto-merging `rums.json`.

**Architecture:** Channel registry → inventory → captions → classify → match proposals. Shared helpers in `youtube_common.py`; pure classify/match logic unit-tested offline.

**Tech Stack:** Python 3, yt-dlp, stdlib unittest, existing `app/scripts/` layout.

**Spec:** `docs/superpowers/specs/2026-08-21-youtube-rum-corpus-design.md`

## Global Constraints

- Captions stay under `app/scripts/output/youtube/` (gitignored); never under `app/src/`.
- Scripts never write `rums.json` or Club JSON — proposals only.
- No YouTube network calls in CI/unit tests.
- Pilot channel id: `stevethebarmanuk`.
- Prefer manual EN subs, else auto `en`.

---

### Task 1: Registry, gitignore, shared helpers

- [x] gitignore + `channels.json` + `youtube_common.py` + `docs/sources/youtube/README.md`

### Task 2: Classify + match (TDD)

- [x] `youtube_classify_lib.py` / `youtube_match_lib.py` + unit tests (10 OK)

### Task 3: CLI scripts

- [x] inventory / fetch-captions / classify / match-rums + `yt-dlp` in requirements-scrape.txt

### Task 4: Smoke + full inventory

- [x] Smoke `--limit 5` (4 captions ok, 1 members-only; 5 rum tags; 30 proposals)
- [x] Full inventory (~927 public videos as of run)
- [ ] Full captions pass (local ops; resume-safe — not required to merge pipeline code)
- [ ] Re-classify + match after captions; report counts (local ops after caption pass)

### Task 5: Spec status

- [x] Spec marked implemented
