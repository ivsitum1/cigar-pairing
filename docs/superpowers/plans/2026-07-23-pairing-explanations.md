# Pairing Explanations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show a one-line local blurb on every pairing card, and on expand a short narrative paragraph above the existing ＋/− reason list.

**Architecture:** New pure functions `pairingBlurb` / `pairingNarrative` build bilingual text from `scorePairing` reasons + shared flavor tags. UI wires them into `PairingPage` result cards and `CustomPairing`. No scoring or API changes.

**Tech Stack:** TypeScript, Vitest, React (existing Vite app under `app/`).

## Global Constraints

- No Gemini / network calls for explanations
- Do not change `scorePairing` weights or rule scores
- HR + EN via `LocalizedText` / `lx()`
- Rollback: delete explain module + UI calls
- Do not commit unless the user explicitly asks

## File map

| File | Role |
|------|------|
| Create `app/src/engine/pairingExplain.ts` | `pairingBlurb`, `pairingNarrative` |
| Create `app/src/engine/pairingExplain.test.ts` | Unit tests |
| Modify `app/src/pages/PairingPage.tsx` | Blurb always; narrative inside expand |
| Modify `app/src/pages/CustomPairing.tsx` | Blurb + narrative above reason list |

---

### Task 1: `pairingBlurb` + `pairingNarrative`

**Files:**
- Create: `app/src/engine/pairingExplain.ts`
- Test: `app/src/engine/pairingExplain.test.ts`

**Interfaces:**
- Consumes: `Cigar`, `Drink`, `PairingReason[]`, `score: number`; `normalizeTags` from `./rules`
- Produces:
  - `pairingBlurb(cigar, drink, reasons, score): LocalizedText`
  - `pairingNarrative(cigar, drink, reasons, score): LocalizedText`

- [ ] **Step 1: Write failing tests**

```ts
import { describe, it, expect } from "vitest";
import { scorePairing } from "./pairing";
import { pairingBlurb, pairingNarrative } from "./pairingExplain";
import type { Cigar, Drink } from "../types";
import cigarsData from "../data/cigars.json";
import rumsData from "../data/rums.json";

const cigars = cigarsData as Cigar[];
const rums = rumsData as unknown as Drink[];
const byId = <T extends { id: string }>(arr: T[], id: string): T => {
  const found = arr.find((x) => x.id === id);
  if (!found) throw new Error(`missing ${id}`);
  return found;
};

describe("pairingBlurb / pairingNarrative", () => {
  it("blurb is non-empty HR+EN for a real pair", () => {
    const cigar = byId(cigars, "cig-macanudo-cafe");
    const drink = byId(rums, "rum-doorly-s-xo-foursquare");
    const { score, reasons } = scorePairing(cigar, drink);
    const b = pairingBlurb(cigar, drink, reasons, score);
    expect(b.hr.length).toBeGreaterThan(20);
    expect(b.en.length).toBeGreaterThan(20);
  });

  it("narrative is longer than blurb for a strong-ish match", () => {
    const cigar = byId(cigars, "cig-macanudo-cafe");
    const drink = byId(rums, "rum-doorly-s-xo-foursquare");
    const { score, reasons } = scorePairing(cigar, drink);
    const b = pairingBlurb(cigar, drink, reasons, score);
    const n = pairingNarrative(cigar, drink, reasons, score);
    expect(n.hr.length).toBeGreaterThan(b.hr.length);
    expect(n.en.length).toBeGreaterThan(b.en.length);
  });

  it("handles empty reasons without throwing", () => {
    const cigar = byId(cigars, "cig-macanudo-cafe");
    const drink = byId(rums, "rum-doorly-s-xo-foursquare");
    const b = pairingBlurb(cigar, drink, [], 50);
    const n = pairingNarrative(cigar, drink, [], 50);
    expect(b.hr.length).toBeGreaterThan(10);
    expect(n.hr.length).toBeGreaterThan(10);
  });
});
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
cd app && npm test -- src/engine/pairingExplain.test.ts
```

Expected: FAIL — module not found / export missing.

- [ ] **Step 3: Implement `pairingExplain.ts`**

```ts
import type { Cigar, Drink, LocalizedText, PairingReason } from "../types";
import { normalizeTags } from "./rules";

const BODY_HR = ["", "vrlo lagano", "lagano", "srednje", "puno", "vrlo puno"];
const BODY_EN = ["", "very light", "light", "medium", "full", "very full"];

function stripDot(s: string): string {
  return s.replace(/\.+$/, "").trim();
}

function sharedTags(cigar: Cigar, drink: Drink): string[] {
  const drinkTags = normalizeTags(drink.flavorTags);
  return normalizeTags(cigar.flavorTags).filter((t) => drinkTags.includes(t));
}

function sortedPos(reasons: PairingReason[]): PairingReason[] {
  return reasons.filter((r) => r.score > 0).sort((a, b) => b.score - a.score);
}

function sortedNeg(reasons: PairingReason[]): PairingReason[] {
  return reasons.filter((r) => r.score < 0).sort((a, b) => a.score - b.score);
}

function fallback(cigar: Cigar, drink: Drink, score: number): LocalizedText {
  return {
    hr: `${BODY_HR[cigar.body] || "srednje"} tijelo cigare uz ${drink.category} (${drink.style}) — ${score}% slaganja.`,
    en: `${BODY_EN[cigar.body] || "medium"} cigar body with ${drink.category} (${drink.style}) — ${score}% match.`,
  };
}

/** One-line explanation for every scored pair. */
export function pairingBlurb(
  cigar: Cigar,
  drink: Drink,
  reasons: PairingReason[],
  score: number,
): LocalizedText {
  const topPos = sortedPos(reasons)[0];
  if (topPos) {
    return { hr: `${stripDot(topPos.text.hr)}.`, en: `${stripDot(topPos.text.en)}.` };
  }
  const topNeg = sortedNeg(reasons)[0];
  if (topNeg) {
    return { hr: `${stripDot(topNeg.text.hr)}.`, en: `${stripDot(topNeg.text.en)}.` };
  }
  return fallback(cigar, drink, score);
}

/** 2–3 sentence paragraph for expand / detail view. */
export function pairingNarrative(
  cigar: Cigar,
  drink: Drink,
  reasons: PairingReason[],
  score: number,
): LocalizedText {
  const blurb = pairingBlurb(cigar, drink, reasons, score);
  const pos = sortedPos(reasons);
  const neg = sortedNeg(reasons);
  const shared = sharedTags(cigar, drink).slice(0, 3);

  const extraHr: string[] = [];
  const extraEn: string[] = [];

  const second = pos[1];
  if (second) {
    extraHr.push(stripDot(second.text.hr));
    extraEn.push(stripDot(second.text.en));
  } else if (neg[0]) {
    extraHr.push(stripDot(neg[0].text.hr));
    extraEn.push(stripDot(neg[0].text.en));
  }

  if (shared.length > 0) {
    const tags = shared.join(", ");
    extraHr.push(`Zajedničke note: ${tags}`);
    extraEn.push(`Shared notes: ${tags}`);
  }

  if (extraHr.length === 0) {
    return {
      hr: `${stripDot(blurb.hr)}. Match ${score}%.`,
      en: `${stripDot(blurb.en)}. Match ${score}%.`,
    };
  }

  return {
    hr: `${stripDot(blurb.hr)}. ${extraHr.join(". ")}.`,
    en: `${stripDot(blurb.en)}. ${extraEn.join(". ")}.`,
  };
}
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
cd app && npm test -- src/engine/pairingExplain.test.ts
```

Expected: PASS (all three tests).

---

### Task 2: Wire `PairingPage` result card

**Files:**
- Modify: `app/src/pages/PairingPage.tsx` (result card component ~lines 670–770)

**Interfaces:**
- Consumes: `pairingBlurb`, `pairingNarrative` from `../engine/pairingExplain`

- [ ] **Step 1: Import and compute**

Inside the result card component (same place as `pairingOpinion`):

```ts
import { pairingBlurb, pairingNarrative } from "../engine/pairingExplain";
// ...
const blurb = pairingBlurb(cigar, drink, result.reasons, result.score);
const narrative = pairingNarrative(cigar, drink, result.reasons, result.score);
```

Ensure `cigar` and `drink` are both in scope for that card (today the card receives one item + the selected counterpart — pass both into the helper that already has them).

- [ ] **Step 2: Always-visible blurb**

After the title/price row (and before or after curated chip), add:

```tsx
<p className="mt-2 text-xs leading-relaxed text-papir/80">{lx(blurb)}</p>
```

- [ ] **Step 3: Narrative inside expand**

Inside `{open && (…)}`, before the `<ul>` of reasons:

```tsx
<p className="mb-2 text-xs leading-relaxed text-papir/85">{lx(narrative)}</p>
```

Keep existing ＋/− `<ul>` unchanged below.

- [ ] **Step 4: Smoke-check**

```bash
cd app && npm test
```

Expected: existing suite still green.

---

### Task 3: Wire `CustomPairing`

**Files:**
- Modify: `app/src/pages/CustomPairing.tsx`

**Interfaces:**
- Consumes: same `pairingBlurb` / `pairingNarrative`

- [ ] **Step 1: Import + compute when `result` exists**

```ts
import { pairingBlurb, pairingNarrative } from "../engine/pairingExplain";

const blurb =
  result && cigar && drink
    ? pairingBlurb(cigar, drink, result.reasons, result.score)
    : null;
const narrative =
  result && cigar && drink
    ? pairingNarrative(cigar, drink, result.reasons, result.score)
    : null;
```

- [ ] **Step 2: Render**

After score / curated block, before the reasons `<ul>`:

```tsx
{blurb && (
  <p className="mt-3 text-xs leading-relaxed text-papir/80">{lx(blurb)}</p>
)}
{narrative && (
  <p className="mt-2 text-xs leading-relaxed text-papir/85">{lx(narrative)}</p>
)}
```

Then existing reasons list.

- [ ] **Step 3: Full test run**

```bash
cd app && npm test
```

Expected: all green.

---

## Spec coverage (self-review)

| Spec requirement | Task |
|------------------|------|
| Always-visible one sentence | Task 1 + 2 + 3 |
| Expand: paragraph then ＋/− list | Task 2 |
| CustomPairing blurb + paragraph + list | Task 3 |
| Offline / no API | Global + Task 1 |
| Unit tests | Task 1 |
| Rollback path | Delete files listed in File map |

No placeholders left. Commit steps omitted (user must request commits).
