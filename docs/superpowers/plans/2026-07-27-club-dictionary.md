# Club Dictionary (Rječnik) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a Club A–Ž dictionary (`#/club/dictionary`) with expansive bilingual articles (cigar + drink + pairing + table), separate from the pairing lexicon.

**Architecture:** Static `dictionary.json` catalog + `DictionaryPage` (search, category filter, A–Ž, detail). Route extends existing Club hash routing. Content is house-voice prose; Holts/bonton are inventory only.

**Tech Stack:** Vite + React + TypeScript, Vitest, existing `useI18n` / `LocalizedText`, Club page patterns from `LexiconPage`.

## Global Constraints

- Full bilingualism on `term`, `def`, `body` (and `doNotConfuse.note`) from day one.
- Categories only: `cigar` | `drink` | `pairing` | `table`.
- Do not paste Holts Clubhouse glossary prose.
- Do not merge or delete pairing `lexicon.json`.
- Do not invent numeric RH / vitola facts that contradict Club101 / club facts.
- Expansive first (≥250 honest entries preferred; fewer OK if honesty requires — no fluff stubs).
- Body rendering: plain paragraphs (`\n\n`); not required to match Lexicon `LessonBody` catalog sections.

---

## File map

| File | Responsibility |
|------|----------------|
| `app/src/data/dictionary.json` | Catalog: title, intro, entries[] |
| `app/src/data/dictionary.test.ts` | Schema / link integrity / count floor |
| `app/src/pages/DictionaryPage.tsx` | List + detail UI |
| `app/src/pages/ClubPage.tsx` | Teaser card + `clubView === "dictionary"` branch |
| `app/src/store/route.ts` | Add `dictionary` to `ClubView` / `CLUB_VIEWS` |
| `app/src/store/route.test.ts` | Hash round-trip |
| `app/src/i18n/index.tsx` | `club.dictionary*` strings |

---

### Task 1: Route + dictionary tests + stub JSON

**Files:**
- Modify: `app/src/store/route.ts`
- Modify: `app/src/store/route.test.ts`
- Create: `app/src/data/dictionary.test.ts`
- Create: `app/src/data/dictionary.json`

### Task 2: DictionaryPage + Club teaser + i18n

**Files:**
- Create: `app/src/pages/DictionaryPage.tsx`
- Modify: `app/src/pages/ClubPage.tsx`
- Modify: `app/src/i18n/index.tsx`

### Task 3: Expansive bilingual content (≥250 entries)

**Files:**
- Modify: `app/src/data/dictionary.json`

### Task 4: Verify

- `cd app && npm test`
- `cd app && npx tsc -b --noEmit`

## Spec coverage

| Spec requirement | Task |
|------------------|------|
| Separate from lexicon | Task 2 |
| Bilingual articles | Task 3 |
| Search / category / A–Ž | Task 2 |
| Schema fields | Tasks 1–3 |
| Holts inventory only | Task 3 |
| Expansive then prune | Task 3 |
| Tests | Tasks 1, 4 |
