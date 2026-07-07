# Poboljšani OCR (predobrada + eng/spa + fuzzy matching) — plan implementacije

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Podići uspješnost OCR prepoznavanja cigara/ruma bez backenda: predobrada slike u canvasu, OCR na eng+spa sa sparse-text modom, i fuzzy dvofazni (brend→linija) matching.

**Architecture:** Sve klijentski. Matching logika se izdvaja iz `OcrScan.tsx` u `app/src/lib/ocrMatch.ts` (čisti, testabilni modul). Predobrada slike ide u `app/src/lib/ocrPreprocess.ts`. `OcrScan.tsx` ostaje UI komponenta koja veže: fotka → predobrada (2 varijante) → tesseract (eng+spa, sparse) → matching.

**Tech Stack:** React 19 + Vite + TypeScript, tesseract.js v7 (postojeći), vitest. **Bez novih npm ovisnosti.**

## Global Constraints

- Nema novih npm ovisnosti; tesseract.js ostaje i lijeno se učitava na prvu upotrebu.
- Komentari u kodu na hrvatskom, kratki, u stilu postojećeg koda.
- Postojeći pozivatelj (`PairingPage.tsx`) smije se mijenjati samo minimalno (dodavanje `brand` polja kandidatima).
- Svi testovi se pokreću iz `app/`: `npm test` (vitest run); build: `npm run build`.
- Commit poruke na engleskom, sa Co-Authored-By trailerom kao u postojećoj povijesti.

---

### Task 1: Fuzzy dvofazni matching — `app/src/lib/ocrMatch.ts`

**Files:**
- Create: `app/src/lib/ocrMatch.ts`
- Create: `app/src/lib/ocrMatch.test.ts`
- Modify: `app/src/components/OcrScan.tsx` (ukloniti preseljenu logiku, importati iz lib)
- Delete: `app/src/components/OcrScan.test.ts` (testovi sele u lib)

**Interfaces:**
- Consumes: ništa novo (podaci iz `../data/cigars.json`, `../data/rums.json` samo u testu).
- Produces (Task 3 se oslanja na ovo):
  - `interface OcrCandidate { id: string; label: string; brand?: string }`
  - `function matchOcrText(text: string, candidates: OcrCandidate[]): { candidate: OcrCandidate; score: number } | null`
  - `function tokenize(s: string): string[]`
  - `const STOP: Set<string>`

- [ ] **Step 1: Napiši padajuće testove** — `app/src/lib/ocrMatch.test.ts`:

```ts
import { describe, it, expect } from "vitest";
import { matchOcrText, tokenize } from "./ocrMatch";
import cigarsData from "../data/cigars.json";
import rumsData from "../data/rums.json";

const cigarCandidates = (cigarsData as { id: string; brand: string; line: string }[]).map(
  (c) => ({ id: c.id, label: `${c.brand} ${c.line}`, brand: c.brand }),
);
const rumCandidates = (rumsData as { id: string; name: string }[]).map((r) => ({
  id: r.id,
  label: r.name,
}));

describe("OCR matcher", () => {
  // postojeci slucajevi (preseljeni iz OcrScan.test.ts)
  it("prepoznaje bocu iz OCR teksta s bukom", () => {
    const ocr = "HAMPDEN\nESTATE\n8 YEARS\nPure Single Jamaican Rum 46% vol";
    const m = matchOcrText(ocr, rumCandidates);
    expect(m?.candidate.id).toBe("rum-hampden-estate-8");
  });

  it("prepoznaje cigaru iz teksta bande", () => {
    const ocr = "PARTAGAS\nSERIE D No.4\nHABANA CUBA";
    const m = matchOcrText(ocr, cigarCandidates);
    expect(m?.candidate.label.toLowerCase()).toContain("partag");
  });

  it("vraca null za nepovezan tekst", () => {
    expect(matchOcrText("xyzabc qwerty", rumCandidates)).toBeNull();
    expect(matchOcrText("", rumCandidates)).toBeNull();
  });

  // novi: fuzzy tolerancija na OCR greske
  it("tolerira jednu krivu OCR zamjenu u brendu", () => {
    const ocr = "PARTAQAS\nSERIE D No.4"; // g -> q
    const m = matchOcrText(ocr, cigarCandidates);
    expect(m?.candidate.label.toLowerCase()).toContain("partag");
  });

  it("tolerira 0 umjesto O", () => {
    const ocr = "M0NTECRIST0\nOPEN EAGLE";
    const m = matchOcrText(ocr, cigarCandidates);
    expect(m?.candidate.label.toLowerCase()).toContain("montecristo");
  });

  it("kratki tokeni se ne matchaju fuzzy (nema laznih pogodaka)", () => {
    // 3-znakovni tokeni moraju biti egzaktni; smece ne smije proci prag
    expect(matchOcrText("ron dom abc", rumCandidates)).toBeNull();
  });

  // novi: dvofazni brend -> linija
  it("prepoznati brend suzuje kandidate", () => {
    const synth = [
      { id: "right", label: "Cohiba Panetela", brand: "Cohiba" },
      { id: "wrong", label: "Panetela Larga Panetela Fina", brand: "Fonseca" },
    ];
    // bez brend-faze "wrong" bi skupio vise bodova preko linije;
    // s brend-fazom pool se suzi na Cohibu
    const m = matchOcrText("COHIBA PANETELA LARGA FINA", synth);
    expect(m?.candidate.id).toBe("right");
  });
});

describe("tokenize", () => {
  it("normalizira dijakritike i baca kratke tokene", () => {
    expect(tokenize("Partagás No.4")).toEqual(["partagas"]);
  });
});
```

- [ ] **Step 2: Pokreni testove — moraju pasti**

Run: `cd app; npm test`
Expected: FAIL — `Cannot find module './ocrMatch'` (odnosno datoteka ne postoji).

- [ ] **Step 3: Implementiraj `app/src/lib/ocrMatch.ts`**

```ts
// Fuzzy matching OCR teksta na katalog. Dvofazno: prvo brend, pa linija
// unutar brenda; tolerira tipicne OCR zamjene znakova (0/O, q/g...).

export interface OcrCandidate {
  id: string;
  label: string;
  brand?: string; // omogucuje dvofazni matching (prvo brend, pa linija)
}

const normalize = (s: string) =>
  s
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase();

export const tokenize = (s: string) =>
  normalize(s)
    .split(/[^a-z0-9]+/)
    .filter((t) => t.length >= 3);

export const STOP = new Set(["rum", "ron", "rhum", "whisky", "whiskey", "cigar", "cigars",
  "anos", "years", "old", "aged", "vol", "70cl", "700ml", "product", "the"]);

/** Levenshteinova udaljenost s ranim izlazom kad prijedje max. */
function levenshtein(a: string, b: string, max: number): number {
  if (Math.abs(a.length - b.length) > max) return max + 1;
  let prev = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    let rowMin = i;
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost);
      rowMin = Math.min(rowMin, cur[j]);
    }
    if (rowMin > max) return max + 1;
    prev = cur;
  }
  return prev[b.length];
}

// kratki tokeni samo egzaktno; do 6 znakova 1 greska, dulji 2
const fuzzyEquals = (a: string, b: string): boolean => {
  if (a === b) return true;
  if (a.length < 4 || b.length < 4) return false;
  const max = Math.min(a.length, b.length) <= 6 ? 1 : 2;
  return levenshtein(a, b, max) <= max;
};

// egzaktan pogodak 2/1 boda (kao dosad), fuzzy pola vrijednosti
function scoreTokens(candTokens: string[], textTokens: string[]): number {
  const textSet = new Set(textTokens);
  let score = 0;
  for (const t of candTokens) {
    if (textSet.has(t)) {
      score += t.length >= 5 ? 2 : 1;
    } else if (textTokens.some((x) => fuzzyEquals(t, x))) {
      score += t.length >= 5 ? 1 : 0.5;
    }
  }
  return score;
}

/** Nadji kandidata s najboljim (fuzzy) poklapanjem; prvo suzi po brendu. */
export function matchOcrText(
  text: string,
  candidates: OcrCandidate[],
): { candidate: OcrCandidate; score: number } | null {
  const textTokens = tokenize(text).filter((t) => !STOP.has(t));
  if (textTokens.length === 0) return null;

  // faza 1: ako kandidati nose brend, suzi pool na najbolje pogodjeni brend
  let pool = candidates;
  const brands = [...new Set(candidates.map((c) => c.brand).filter((b): b is string => !!b))];
  if (brands.length > 1) {
    let bestBrand: string | null = null;
    let bestBrandScore = 0;
    for (const b of brands) {
      const s = scoreTokens(tokenize(b).filter((t) => !STOP.has(t)), textTokens);
      if (s > bestBrandScore) {
        bestBrand = b;
        bestBrandScore = s;
      }
    }
    if (bestBrand && bestBrandScore >= 2) {
      pool = candidates.filter((c) => c.brand === bestBrand);
    }
  }

  // faza 2: najbolja linija unutar poola
  let best: OcrCandidate | null = null;
  let bestScore = 0;
  for (const c of pool) {
    const candTokens = tokenize(c.label).filter((t) => !STOP.has(t));
    if (candTokens.length === 0) continue;
    const score = scoreTokens(candTokens, textTokens);
    if (score > bestScore) {
      best = c;
      bestScore = score;
    }
  }
  return best && bestScore >= 2 ? { candidate: best, score: bestScore } : null;
}
```

- [ ] **Step 4: Prespoji `OcrScan.tsx` na novi modul**

U `app/src/components/OcrScan.tsx`:
1. Obriši lokalne definicije `OcrCandidate`, `normalize`, `tokenize`, `STOP` i `matchOcrText` (redci 6–47).
2. Na vrh dodaj import i re-export tipa:

```ts
import { matchOcrText, tokenize, STOP, type OcrCandidate } from "../lib/ocrMatch";

export type { OcrCandidate };
```

Ostatak komponente (fallback s najduljom riječi koristi `tokenize` i `STOP`) ostaje isti.

3. Obriši `app/src/components/OcrScan.test.ts`.

- [ ] **Step 5: Pokreni sve testove — moraju proći**

Run: `cd app; npm test`
Expected: PASS (svi, uključujući postojeće integrity/pairing testove).

- [ ] **Step 6: Commit**

```bash
git add app/src/lib/ocrMatch.ts app/src/lib/ocrMatch.test.ts app/src/components/OcrScan.tsx
git rm app/src/components/OcrScan.test.ts
git commit -m "Extract OCR matching to lib with fuzzy + brand-first two-phase logic"
```

---

### Task 2: Predobrada slike — `app/src/lib/ocrPreprocess.ts`

**Files:**
- Create: `app/src/lib/ocrPreprocess.ts`

**Interfaces:**
- Consumes: ništa.
- Produces (Task 3 se oslanja na ovo): `async function preprocessImage(file: File): Promise<Blob[]>` — vraća točno 2 JPEG varijante: [normalna, invertirana], obje grayscale s rastegnutim kontrastom, dulja stranica ~1600 px.

Napomena: po specu se za predobradu **ne pišu** unit testovi (canvas u jsdom-u nije reprezentativan); provjera je tipovima/buildom u ovom tasku i ručno na kraju.

- [ ] **Step 1: Implementiraj `app/src/lib/ocrPreprocess.ts`**

```ts
// Predobrada fotke za OCR: skaliranje na ~1600px, grayscale s rastegnutim
// kontrastom, te normalna + invertirana varijanta (svijetli tekst na tamnom).

const TARGET_DIM = 1600;
const MAX_UPSCALE = 3;

export async function preprocessImage(file: File): Promise<Blob[]> {
  const bmp = await createImageBitmap(file);
  const factor = Math.min(MAX_UPSCALE, TARGET_DIM / Math.max(bmp.width, bmp.height));
  const w = Math.max(1, Math.round(bmp.width * factor));
  const h = Math.max(1, Math.round(bmp.height * factor));

  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("canvas 2d context unavailable");
  ctx.imageSmoothingQuality = "high";
  ctx.drawImage(bmp, 0, 0, w, h);
  bmp.close();

  const img = ctx.getImageData(0, 0, w, h);
  const d = img.data;

  // luminancija + histogram za rastezanje kontrasta (5./95. percentil)
  const lum = new Uint8ClampedArray(w * h);
  const hist = new Array<number>(256).fill(0);
  for (let i = 0, p = 0; i < d.length; i += 4, p++) {
    const y = Math.round(0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2]);
    lum[p] = y;
    hist[y]++;
  }
  const total = w * h;
  let lo = 0;
  let hi = 255;
  for (let v = 0, acc = 0; v < 256; v++) {
    acc += hist[v];
    if (acc >= total * 0.05) {
      lo = v;
      break;
    }
  }
  for (let v = 255, acc = 0; v >= 0; v--) {
    acc += hist[v];
    if (acc >= total * 0.05) {
      hi = v;
      break;
    }
  }
  const range = Math.max(1, hi - lo);

  const variants: Blob[] = [];
  for (const invert of [false, true]) {
    for (let p = 0; p < lum.length; p++) {
      let y = Math.round(((lum[p] - lo) / range) * 255);
      y = Math.max(0, Math.min(255, y));
      if (invert) y = 255 - y;
      const i = p * 4;
      d[i] = d[i + 1] = d[i + 2] = y;
      d[i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
    const blob = await new Promise<Blob>((resolve, reject) =>
      canvas.toBlob(
        (b) => (b ? resolve(b) : reject(new Error("toBlob failed"))),
        "image/jpeg",
        0.9,
      ),
    );
    variants.push(blob);
  }
  return variants;
}
```

- [ ] **Step 2: Provjeri tipove i build**

Run: `cd app; npm run build`
Expected: build prolazi bez TS grešaka (datoteka još nije nigdje importana — to je OK, Task 3 je veže).

- [ ] **Step 3: Commit**

```bash
git add app/src/lib/ocrPreprocess.ts
git commit -m "Add canvas image preprocessing for OCR (contrast stretch + inverted pass)"
```

---

### Task 3: Integracija u `OcrScan.tsx` + brend u kandidatima

**Files:**
- Modify: `app/src/components/OcrScan.tsx` (funkcija `handleFile`)
- Modify: `app/src/pages/PairingPage.tsx` (~redak 293: kandidati cigara dobivaju `brand`)

**Interfaces:**
- Consumes: `preprocessImage(file): Promise<Blob[]>` (Task 2); `matchOcrText`, `tokenize`, `STOP` (Task 1).
- Produces: ništa novo prema van; ponašanje komponente (props `candidates/onMatch/onText`) nepromijenjeno.

- [ ] **Step 1: Zamijeni `handleFile` u `OcrScan.tsx`**

Dodaj import na vrh:

```ts
import { preprocessImage } from "../lib/ocrPreprocess";
```

Zamijeni postojeći `handleFile` (Tesseract.recognize s "eng") ovim:

```ts
const handleFile = async (file: File) => {
  setBusy(true);
  setStatus(t("ocr.working"));
  try {
    // paralelno: ucitaj tesseract i predobradi sliku (2 varijante)
    const [{ createWorker, PSM }, variants] = await Promise.all([
      import("tesseract.js"),
      preprocessImage(file),
    ]);
    const worker = await createWorker(["eng", "spa"], undefined, {
      logger: (m) => {
        if (m.status === "recognizing text") {
          setStatus(`${t("ocr.working")} ${Math.round(m.progress * 100)}%`);
        }
      },
    });
    let text = "";
    try {
      // tekst na prstenu/etiketi je rasprsen, ne uredan odlomak
      await worker.setParameters({ tessedit_pageseg_mode: PSM.SPARSE_TEXT });
      for (const v of variants) {
        const r = await worker.recognize(v);
        text += (r.data.text ?? "") + "\n";
      }
    } finally {
      await worker.terminate();
    }
    const match = matchOcrText(text, candidates);
    if (match) {
      setStatus(`✓ ${match.candidate.label}`);
      onMatch(match.candidate.id);
    } else {
      // nema pouzdanog pogotka — ponudi najdulju prepoznatu rijec u pretrazi
      const words = tokenize(text).filter((w) => !STOP.has(w));
      if (words.length > 0) {
        const longest = words.sort((a, b) => b.length - a.length)[0];
        onText(longest);
        setStatus(t("ocr.partial"));
      } else {
        setStatus(t("ocr.noMatch"));
      }
    }
  } catch {
    setStatus(t("ocr.error"));
  } finally {
    setBusy(false);
    setTimeout(() => setStatus(null), 4000);
  }
};
```

- [ ] **Step 2: Dodaj `brand` kandidatima cigara u `PairingPage.tsx`**

Na ~retku 293, u `<OcrScan candidates={...}>`:

```ts
marketCigars.map((c) => ({
  id: c.id,
  label: `${c.brand} ${c.line}`,
  brand: c.brand,
}))
```

(pića ostaju bez `brand` — jednofazni matching kao dosad).

- [ ] **Step 3: Testovi + build**

Run: `cd app; npm test; npm run build`
Expected: svi testovi PASS, build prolazi.

- [ ] **Step 4: Commit**

```bash
git add app/src/components/OcrScan.tsx app/src/pages/PairingPage.tsx
git commit -m "OCR: preprocess image, eng+spa sparse-text recognition, brand-aware matching"
```

---

### Task 4: Push i provjera deploya

**Files:** ništa novo.

- [ ] **Step 1: Push na master**

```bash
git push origin master
```

- [ ] **Step 2: Provjeri GitHub Actions run**

Provjeri zadnji run na `https://api.github.com/repos/ivsitum1/cigar-pairing/actions/runs?per_page=1` — `conclusion` mora biti `success` (build + test + deploy na Pages).

- [ ] **Step 3: Ručna provjera (korisnik)**

Na mobitelu otvoriti aplikaciju, skenirati 2–3 prstena cigara i etiketu ruma; očekivano osjetno bolje prepoznavanje. Ovo je zadnja točka speca („predobrada se provjerava ručno na stvarnim fotkama").
