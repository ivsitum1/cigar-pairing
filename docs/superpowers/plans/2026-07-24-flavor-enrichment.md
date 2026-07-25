# Flavor enrichment (existing cigars) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline) or subagent-driven-development. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pull shop-published flavour cues (CigarWorld first) into thin existing cigar profiles; do not touch founded years.

**Architecture:** Worklist JSON → Playwright scrape of CW product pages → raw JSON → merge into `cigars.json` (`flavorTags`, `notes`, optional `wrapper`/`strength`/`body`). Heuristic fallback for thin rows without CW URL via existing `describe-lines.py` / tag rules.

**Tech Stack:** Python 3, Playwright, existing `describe-lines.py` TAG maps, Vitest for data integrity.

## Global Constraints

- Flavors first; leave `founded` alone
- No fabricated tasting notes without shop/heuristic basis
- Never overwrite HR prices/URLs
- `profileEstimated: false` only when notes/tags come from shop prose
- Rate-limit 1–2 s; consent wall once
- Spec: `docs/superpowers/specs/2026-07-24-flavor-enrichment-design.md`

## File map

| File | Role |
|------|------|
| `app/scripts/build-flavor-worklist.py` | Emit thin-set worklist |
| `app/scripts/scrape-cigarworld-flavors.py` | Playwright product scrape |
| `app/scripts/merge-flavor-enrichment.py` | Apply raw → cigars.json |
| `app/scripts/output/flavor_enrich_worklist.json` | Worklist |
| `app/scripts/output/cigarworld_flavor_raw.json` | Raw scrape |
| `app/src/data/cigars.json` | Target data |

---

### Task 1: Worklist

- [ ] Script: thin if `notes.hr` &lt; 40 OR `len(flavorTags) &lt; 2`
- [ ] Attach best CigarWorld EU URL from cigar or vitola `regionLinks`
- [ ] Write `flavor_enrich_worklist.json` + print counts (thin / with_cw)

### Task 2: Scrape CigarWorld flavors

- [ ] Playwright chromium; click cookie/age if present; reuse context
- [ ] Per URL extract: title, wrapper, strength text, description paragraphs, any flavour keywords
- [ ] Sleep 1.5s between pages; write `cigarworld_flavor_raw.json`

### Task 3: Merge

- [ ] Map DE/EN shop words → existing `flavorTags` vocabulary (`describe-lines.TAG_EN` inverse)
- [ ] Build bilingual notes from shop description or wrapper+tags template
- [ ] Set `profileEstimated: false` when shop description used; else keep true
- [ ] Idempotent by cigar id

### Task 4: Heuristic fallback (no CW)

- [ ] For remaining thin without scrape hit: run tag fill from wrapper via `profile-cigars` logic or call `describe-lines` for notes only where still thin
- [ ] Keep `profileEstimated: true`

### Task 5: Verify

- [ ] Re-count thin set (expect drop)
- [ ] `cd app && npx vitest run src/data/cigars.data.test.ts`
- [ ] Update design status to implemented
