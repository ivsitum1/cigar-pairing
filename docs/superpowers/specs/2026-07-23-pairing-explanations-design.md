# Pairing explanations (blurb + narrative)

**Date:** 2026-07-23  
**Status:** approved — implemented 2026-07-23  
**Scope:** UI + local engine text; no Gemini / API

## Goal

Every scored cigar–drink pair shows a short explanation by default. Expanding reveals a fuller paragraph plus the existing rule-by-rule ＋/− list. Easy to revert if the prose feels wrong.

## Non-goals

- No LLM / Gemini / agents-cli
- No change to `scorePairing` scoring weights
- No precomputation for all catalog pairs (compute on render from existing `reasons`)

## UX

### Pairing result card (`PairingPage` result rows)

| Layer | When | Content |
|-------|------|---------|
| **Blurb** | Always | One sentence (~max ~180 chars), bilingual via `lx` |
| ★ / ⚠ curated | As today | Unchanged; only praise / warning zones |
| **Expand (▾)** | On toggle | (1) Narrative paragraph 2–3 sentences; (2) existing ＋/− reason list |

### Custom pairing (`CustomPairing`)

Same blurb always under the score. Narrative above the reason list (list is already always open there; no new toggle required unless we add one for consistency — prefer: always show blurb + narrative + list when both items selected).

## Engine API (new)

File: `app/src/engine/pairingExplain.ts` (or adjacent to `curatedOpinion.ts`)

```ts
pairingBlurb(cigar, drink, reasons, score): { hr: string; en: string }
pairingNarrative(cigar, drink, reasons, score): { hr: string; en: string }
```

### Blurb rules

1. Prefer top positive reason’s meaning (reuse / compress synergy-style lines; do not dump raw multi-clause rule text if a short template fits).
2. If no positive reasons, use strongest negative as cautionary one-liner.
3. Fall back: body levels + drink category + score %.
4. Deterministic; HR and EN both required.

### Narrative rules

1. Start from blurb idea, then add up to two more contributing reasons (pos then neg if useful).
2. Mention up to 3 shared flavor tags when present (normalized tags, same as engine).
3. Do not invent tasting notes not in data / reasons.
4. Avoid repeating the curated ★/⚠ string verbatim; narrative is independent.

## UI wiring

- `PairingPage` result card: render `lx(blurb)` below title row (or under curated chip); inside `{open && …}`: narrative `<p>` then existing `<ul>` of reasons.
- `CustomPairing`: blurb + narrative + reasons when `result` exists.

## Tests

- Unit: blurb/narrative non-empty for sample pairs; HR/EN keys; no throw on empty reasons.
- Sanity: spot-check that narrative length is longer than blurb for a strong match.
- Existing pairing / curatedOpinion tests unchanged.

## Rollback

Remove blurb/narrative render calls and delete `pairingExplain.ts` (+ tests). Scoring and curated opinion stay.

## Acceptance

- [ ] Every pair card shows a one-line explanation without expand
- [ ] Expand shows paragraph then ＋/− list
- [ ] Custom pairing shows blurb + paragraph + list
- [ ] Offline, no network calls
- [ ] `npm test` (or project equivalent) green for new units
