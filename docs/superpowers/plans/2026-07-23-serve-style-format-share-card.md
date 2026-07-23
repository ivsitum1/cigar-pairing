# Plan: Serve Style · Format & Trajanje · Share-kartica

**Datum:** 2026-07-23
**Autor:** koncept iz nezavisne recenzije (3 prijedloga) + analiza koda
**Za izvođača:** Cursor može preuzeti direktno — svaki korak ima točne datoteke, potpise i testove.
**Grana:** raditi na `claude/app-flyer-pr-campaign-dvvciz` ili otvoriti feature grane po fazi (vidi §7).

---

## 0. TL;DR — što stvarno treba napraviti

Recenzija predlaže tri stvari. **Bitno: dvije su već djelomično u podacima, samo ih engine/UI ne koristi.** Nemoj graditi ispočetka — spoji postojeće.

| # | Prijedlog | Status u kodu **danas** | Što stварно fali |
|---|-----------|--------------------------|------------------|
| A | **Serve style** (neat / kap vode / rocks / highball / cola) | `Drink.serving {neat,water,rocks,highball,cola,best}` **već postoji u svim JSON-ovima** (0–3 + `best`). Engine ga **ne čita**. | Selektor u UI-u + prilagodba bodovanja + objašnjenje. |
| B | **Format & trajanje cigare** | `Cigar.smokeTimeMin`, `Cigar.format`, `Vitola.{format,smokeTimeMin,ring,lengthMM,shape}` **već postoje**; `applyVitola()` ih već primjenjuje; picker ih prikazuje. Engine ih **ne koristi za pairing/ritam**. | „Ritam/trajanje” hint na rezultatu (B1) + opcionalni blagi nudge (B2). |
| C | **Backup + share** | Export/Import JSON **već postoji** (`store/collection.ts` `exportData`/`importData`, UI u `CollectionPage`). | **Slikovna „pairing kartica”** za dijeljenje (canvas → PNG / `navigator.share`). Backup NE dirati. |

Prioritet isporuke: **A → C → B** (A ima najveću vrijednost i najčišći dodir; C je vidljiv i sam za sebe; B (geometrija vitole) je sada pravi ulaz formule jer su podaci popunjeni — vidi §0.5).

---

## 0.5 Provjera domenskih tvrdnji (recenzija runda 2)

Dvije tvrdnje provjerene izvorima — **obje točne**, i mijenjaju model iz prve verzije plana.

**Tvrdnja 1 — geometrija vitole (dužina × debljina) mijenja gorenje i okus. ✅ TOČNO.**
Tanji ring gauge sužava dovod zraka → veća brzina zraka → **žar gori znatno toplije i brže**; veći omjer wrapper:filler čini **wrapper dominantnijim, okus koncentriranijim i intenzivnijim** (najizraženije na ringu ~36–44). Deblji ring gori **hladnije, glađe, filler-naprijed, manje koncentrirano**. Dužina: dim se hladi na putu do usta → duže cigare glađe kreću i intenzitet grade prema kraju.
Izvori: Holt's „What is Cigar Ring Gauge”, JR Cigars „Large Ring Gauge”, Cigars.com „Ring Gauge Explained”.

**Tvrdnja 2 — kap vode otvara aromu (ne smanjuje bitno tijelo); led zatvara. ✅ TOČNO.**
Nature 2017 (Karlsson & Friedman, „Dilution of whisky — the molecular perspective”): razrjeđivanjem amfipatski aromatski spojevi (npr. **gvajakol**) migriraju na granicu tekućina–zrak i lakše isparavaju → **pojačana aroma**; efekt slabi tek iznad ~59 vol-% etanola. Dakle kap (mlake) vode **otvara aromu i umiruje žestinu etanola**, a **tijelo/viskoznost jedva mijenja**. Hlađenje (led) snižava tlak para hlapljivih spojeva → **zatvara/prigušuje aromu** i smanjuje percepciju slatkoće; s vremenom topljenjem razrjeđuje.
Izvori: Nature Sci. Reports 2017 (s41598-017-06423-5); ScienceDaily 2017-08-18; PMC10048241 (senzorna analiza dilucije).

**Popravci u odnosu na prvu verziju plana:**
1. Serve model više **nije tijelo-centričan**. Uvodi se `aromaFactor` (množi aroma-sinergiju: voda ↑, led ↓) i `tameFactor` (množi kazne žestine: voda umiruje). Voda ima `bodyDelta ≈ 0` (bila je −0.5 — pogrešno).
2. **Podaci to podržavaju:** `vitola.ring`, `vitola.lengthMM`, `format` = "RING x LENGTHmm" popunjeni na **99%**, `smokeTimeMin` **100%** (5516 vitola). Zato geometrija (§4) postaje **pravilo u formuli**, uz siguran neutralni fallback za 1% bez dimenzija.

---

## 1. Zajednički pojmovi i tipovi

Dodati u `app/src/types.ts`:

```ts
export type ServeStyle = "neat" | "water" | "rocks" | "highball" | "cola";
```

Podsjetnik na postojeće (NE mijenjati sheme, samo čitati):

```ts
// types.ts (postojeće)
export interface Serving {
  neat?: number; water?: number; rocks?: number; highball?: number; cola?: number;
  best: string;         // slobodni tekst, npr. "Cisto / kap vode"
}
export interface Drink { body: number; sweetness: number; flavorTags: string[]; serving: Serving; /* … */ }
export interface Cigar { body: number; strength: number; smokeTimeMin: number; format: string; /* … */ }
export interface Vitola { format: string|null; smokeTimeMin: number|null; ring?: number; lengthMM?: number; shape?: string; /* … */ }
```

Engine reasons **ne koriste i18n ključeve** — nose vlastiti `{hr,en}` tekst (vidi `PairingReason`). Nova objašnjenja iz enginea slijede taj obrazac. **Samo UI chipovi/gumbi** dobivaju i18n ključeve.

---

## 2. Feature A — Serve Style

### 2.1 Namjera
Kako se piće servira mijenja ravnotežu spoja: kap vode spušta žestinu i otvara aromu; led priguši arome i sladak dojam; highball/cola razrijede tijelo i (cola) naglo dignu slatkoću. To mijenja koja cigara pristaje.

### 2.2 Opseg (važno — drži usko)
- Serve selektor se prikazuje **samo u `drinkToCigar` modu i u `custom` modu** (tamo postoji **jedno** odabrano piće → mijenjamo rang cigara).
- U `cigarToDrink` modu (jedan cigar → 7 različitih pića) **ne** stavljamo selektor; umjesto toga na svakoj kartici pića prikažemo **read-only** `serving.best` kao hint („Najbolje: čisto / kap vode”).

### 2.3 Deterministički model (novi modul `app/src/engine/serve.ts`)

**Ispravljeno prema §0.5.** Serve ne mijenja samo body/sweetness — glavni efekt je na **aromu** (tag-sinergija) i **žestinu** (kazne). Zato uz delte body/sweet uvodimo dva množitelja: `aromaFactor` (voda ↑ otvara, led ↓ zatvara) i `tameFactor` (<1 = umiruje alkohol → smanjuje kazne overwhelm/power-mismatch).

```ts
import type { Drink, PairingReason, ServeStyle } from "../types";

export interface ServeEffect {
  bodyDelta: number;      // pomak EFEKTIVNOG tijela (dilucija) — voda ≈ 0
  sweetnessDelta: number; // pomak EFEKTIVNE slatkoće — cola +, led −
  aromaFactor: number;    // množi aroma-sinergiju (rules 2 + 2b): >1 otvara, <1 zatvara
  tameFactor: number;     // množi kazne žestine (rules 1b + 5neg): <1 umiruje alkohol
}

// Kalibracija namjerno konzervativna — serve nikad presudan. Jedno mjesto za ugađanje.
export const SERVE_EFFECT: Record<ServeStyle, ServeEffect> = {
  neat:     { bodyDelta:  0.0, sweetnessDelta:  0.0, aromaFactor: 1.00, tameFactor: 1.00 }, // baseline
  // kap (mlake) vode: OTVARA aromu (gvajakol na površinu), UMIRUJE žestinu; tijelo ~netaknuto
  water:    { bodyDelta:  0.0, sweetnessDelta:  0.0, aromaFactor: 1.15, tameFactor: 0.65 },
  // led: hladno ZATVARA aromu i prigušuje slatkoću; blaga dilucija tijela
  rocks:    { bodyDelta: -0.2, sweetnessDelta: -0.3, aromaFactor: 0.80, tameFactor: 0.85 },
  // highball: jaka dilucija tijela + svježina; aroma blago prigušena
  highball: { bodyDelta: -1.3, sweetnessDelta:  0.3, aromaFactor: 0.95, tameFactor: 0.50 },
  // cola: šećer naglo diže slatkoću (mijenja contrast-sweet-maduro), razrjeđuje tijelo
  cola:     { bodyDelta: -0.8, sweetnessDelta:  1.3, aromaFactor: 0.90, tameFactor: 0.60 },
};

const clamp15 = (v: number) => Math.max(1, Math.min(5, v));

/** EFEKTIVNO piće + množitelji + objašnjenje serve stila. */
export function applyServe(
  drink: Drink,
  serve: ServeStyle | undefined,
): { drink: Drink; effect: ServeEffect; reason?: PairingReason } {
  const effect = SERVE_EFFECT[serve ?? "neat"];
  if (!serve || serve === "neat") return { drink, effect };
  const adjusted: Drink = {
    ...drink,
    body: clamp15(drink.body + effect.bodyDelta),
    sweetness: clamp15(drink.sweetness + effect.sweetnessDelta),
  };
  return { drink: adjusted, effect, reason: SERVE_REASON[serve] };
}

const SERVE_REASON: Record<Exclude<ServeStyle, "neat">, PairingReason> = {
  water: { rule: "serve-water", score: 0, text: {
    hr: "Kap vode otvara aromu i umiruje žestinu — spoj podnosi i blažu cigaru (tijelo ostaje slično).",
    en: "A drop of water opens the aroma and tames the heat — it tolerates a milder cigar (body stays similar)." } },
  rocks: { rule: "serve-rocks", score: 0, text: {
    hr: "Led zatvara aromu i prigušuje slatkoću — manje aromatskog preklapanja s cigarom.",
    en: "Ice closes the aroma and dampens sweetness — less aromatic overlap with the cigar." } },
  highball: { rule: "serve-highball", score: 0, text: {
    hr: "Highball razrjeđuje tijelo i dodaje svježinu — traži lakšu cigaru.",
    en: "A highball dilutes the body and adds lift — it calls for a lighter cigar." } },
  cola: { rule: "serve-cola", score: 0, text: {
    hr: "Cola naglo diže slatkoću — pojačava kontrast prema tamnijoj, punijoj cigari.",
    en: "Cola spikes the sweetness — it strengthens the contrast toward a darker, fuller cigar." } },
};
```

> `score: 0`: reason se **prikaže** u „zašto”, ali bodove ne dodaje izravno. Efekt dolazi kroz (a) prilagođeni body/sweetness u pravilima body-match/overwhelm/contrast i (b) množitelje `aromaFactor`/`tameFactor` u §2.4. Time nema dvostrukog bodovanja, a mehanizam odgovara §0.5 (voda = aroma↑/žestina↓, ne tijelo↓).

### 2.4 Izmjena `app/src/engine/pairing.ts`

Dodati opcionalni 4. argument, primijeniti serve na početku i **množiti aroma/žestina bodove**:

```ts
export function scorePairing(
  cigar: Cigar,
  drink: Drink,
  prefs?: PersonalPrefs,
  serve?: ServeStyle,          // NOVO
): { score: number; reasons: PairingReason[] } {
  const { drink: effDrink, effect, reason: serveReason } = applyServe(drink, serve);
  // …ostatak koristi effDrink umjesto drink…
  // na kraju, prije return, ako serveReason: reasons.push(serveReason)
}
```

Konkretne izmjene po pravilu (množitelji zaokružiti tek pri dodavanju u `score`):
- **Pravilo 1 / 1b (body/overwhelm):** `bodyDiff = Math.abs(effCigar.body - effDrink.body)` (float; `BODY_LABEL_*` indeksirati `Math.round`). Overwhelm kazna (1b) **× `effect.tameFactor`** — voda umiruje pa jaka cigara manje „guši” razrijeđeno piće.
- **Pravilo 2 (flavor-shared)** i **2b (flavor-complement):** bodovi **× `effect.aromaFactor`** — voda (1.15) otvara aromu → jače aromatsko preklapanje; led (0.80) zatvara → slabije. Npr. `pts = Math.round(Math.min(shared.length,3) * WEIGHTS.tagOverlap * effect.aromaFactor)`.
- **Pravilo 3 (contrast-sweet-maduro):** čita `effDrink.sweetness` → cola (+1.3) automatski pali/pojačava kontrast; led (−0.3) ga slabi.
- **Pravilo 5 (power):** negativna grana (`power-mismatch`) **× `effect.tameFactor`** (voda umiruje overproof); pozitivna grana bez množitelja.
- Proslijediti `serve` kroz `pairCigarsForDrink(drink, cigars, prefs, serve?)`. `pairDrinksForCigar` **ostaje bez serve** (opseg §2.2).

> Napomena: `effCigar` u pravilima 1/1b/5 dolazi iz §4 (geometrija vitole). Ako se §4 ne isporučuje u istom PR-u, `effCigar === cigar`.

### 2.5 UI — `app/src/pages/PairingPage.tsx`

1. Novi state: `const [serve, setServe] = useState<ServeStyle | undefined>(undefined);`
2. Reset u `reset()` i pri promjeni pića: `setServe(undefined)`.
3. Kad je odabrano piće (`mode === "drinkToCigar" && selectedDrink`), iznad liste cigara render **ServeChips** (nova mala komponenta, može inline):
   - Prikaži samo stilove gdje `selectedDrink.serving[style] > 0`, poredane po vrijednosti (najviše prvo); uvijek uključi `neat` ako je >0.
   - Default odabir: stil s najvišom vrijednošću (ili `undefined` = neat baseline). Sub-label: `serving.best`.
4. `cigarSuggestions` useMemo: dodati `serve` u ovisnosti i proslijediti u `pairCigarsForDrink(selectedDrink, cigars, prefs, serve)`.
5. `custom` mod (`CustomPairing.tsx`): isto — dodati serve selektor za piće i proslijediti u `scorePairing(..., serve)`.
6. `cigarToDrink` kartice: dodati read-only redak „Najbolje: {lokaliziran best}” iz `result.item.serving.best` (bez selektora).

**ServeChips skica** (Tailwind klase kao postojeći `Chip`):
```tsx
{(["neat","water","rocks","highball","cola"] as ServeStyle[])
  .filter((s) => (selectedDrink.serving[s] ?? 0) > 0)
  .map((s) => (
    <Chip key={s} active={(serve ?? defaultServe) === s} onClick={() => setServe(s)}>
      {t(`serve.${s}` as StringKey)}
    </Chip>
  ))}
```

### 2.6 i18n (`app/src/i18n/index.tsx`, dodati u `STRINGS`)
```ts
"serve.title":    { hr: "Kako serviraš?",            en: "How do you serve it?" },
"serve.neat":     { hr: "Čisto",                     en: "Neat" },
"serve.water":    { hr: "Kap vode",                  en: "Splash of water" },
"serve.rocks":    { hr: "Na ledu",                   en: "On the rocks" },
"serve.highball": { hr: "Highball",                  en: "Highball" },
"serve.cola":     { hr: "S colom",                   en: "With cola" },
"serve.best":     { hr: "Najbolje",                  en: "Best" },
```

### 2.7 Testovi (`app/src/engine/serve.test.ts` — novi)
- `applyServe(drink,"neat")` vraća isti body/sweetness, `aromaFactor===1`, `tameFactor===1`, bez reasona.
- `water`: `bodyDelta === 0` (tijelo se **ne** mijenja — regresija na §0.5), `aromaFactor > 1`, `tameFactor < 1`, dodan `serve-water` reason.
- `rocks`: `aromaFactor < 1` (zatvara aromu), `sweetnessDelta < 0`.
- `cola`: efektivni sweetness ≥ +1 i klema na 5 kad je već visoko.
- Klemanje: `highball` na piću body=1 ostaje ≥1.
- Regresija u `pairing.test.ts`: `scorePairing(c,d,undefined,undefined)` === stara vrijednost (serve opcionalan ne mijenja default).
- Integracijski A — žestina: jako piće (body 5, overproof tag) + blaga cigara → `water` **smanjuje** kaznu (score ≥ neat) preko `tameFactor`.
- Integracijski B — aroma: cigara i piće s 2+ zajedničkih tagova → `water` **diže** score vs `neat`, a `rocks` ga **spušta** (aromaFactor).

---

## 3. Feature C — Share-kartica (slika spoja)

> Backup/Export/Import **već postoji** i NE dira se. Ovdje dodajemo samo **vizualnu karticu za dijeljenje**.

### 3.1 Pristup (bez novih dependencija)
Canvas 2D → PNG. `navigator.share({files})` na mobitelu (Web Share API level 2), fallback download `<a download>`. Marcellus/Manrope su već bundlani (fontsource) pa ih canvas može koristiti nakon `document.fonts.load`.

### 3.2 Novi modul `app/src/lib/shareCard.ts`

Razdvojiti **model** (čisto, testabilno) od **crtanja** (canvas):

```ts
import type { Cigar, Drink, ServeStyle, Lang, PairingReason } from "../types";

export interface ShareCardModel {
  title: string;        // "PAIRING"
  cigarLine: string;    // "Padrón 1964 · Robusto"
  drinkLine: string;    // "Diplomático Reserva · Kap vode"
  score: number;        // 0..100
  reasons: string[];    // do 2 pozitivna razloga, lokalizirano
  footer: string;       // "ivsitum1.github.io/cigar-pairing"
}

export function buildShareCardModel(
  cigar: Cigar, drink: Drink, serve: ServeStyle | undefined,
  score: number, reasons: PairingReason[], lang: Lang,
): ShareCardModel { /* … čista funkcija … */ }

export async function renderShareCardPng(model: ShareCardModel): Promise<Blob> {
  // 1080×1350 canvas, humidor paleta (#201812 pozadina, #c9a35c zlato,
  // #ede0c8 papir), zlatna band-linija, Marcellus naslovi (await document.fonts.load).
  // return await new Promise(res => canvas.toBlob(b => res(b!), "image/png"));
}

export async function sharePairing(model: ShareCardModel): Promise<"shared"|"downloaded"> {
  const blob = await renderShareCardPng(model);
  const file = new File([blob], "pairing.png", { type: "image/png" });
  if (navigator.canShare?.({ files: [file] })) {
    await navigator.share({ files: [file], title: "Cigar & Drink Pairing" });
    return "shared";
  }
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a"); a.href = url; a.download = "pairing.png"; a.click();
  URL.revokeObjectURL(url);
  return "downloaded";
}
```

**Paleta kartice** = ista „humidor” iz `index.css` (pozadina `#201812`, cedar kartica `#2c211a`, zlato `#c9a35c`/`#e3c68b`, papir `#ede0c8`, dim `#a98f72`). Layout: eyebrow „DOSJE · SPOJ”, velika Marcellus imena cigare i pića, ScoreBand krug sa scoreom, 1–2 razloga, zlatna band-linija, footer URL. Reduced-motion nije relevantan (statična slika).

### 3.3 UI dodaci
- `ResultCard` (`PairingPage.tsx`): mali gumb „⤴ {t('share.pairing')}” pored „zašto ▾”. `onClick`: `const m = buildShareCardModel(cigar, drink, serve, result.score, result.reasons, lang); const how = await sharePairing(m); flash(how==="shared"?…:…)`.
- (Opcionalno) i u `EveningSessionSheet` nakon spremanja: „Podijeli ovaj spoj”.

### 3.4 i18n
```ts
"share.pairing":    { hr: "Podijeli spoj",                      en: "Share pairing" },
"share.shared":     { hr: "Kartica spremna za dijeljenje.",     en: "Card ready to share." },
"share.downloaded": { hr: "Kartica preuzeta (PNG).",            en: "Card downloaded (PNG)." },
"share.failed":     { hr: "Dijeljenje nije uspjelo.",           en: "Sharing failed." },
```

### 3.5 Testovi (`app/src/lib/shareCard.test.ts`)
- `buildShareCardModel` slaže `drinkLine` s lokaliziranim serve sufiksom (npr. „· Kap vode” / „· Splash of water”).
- Uzima **najviše 2** pozitivna razloga, redom po `score` (desc).
- HR/EN varijante teksta.
- Crtanje (`renderShareCardPng`) NE testirati u jsdom-u (nema canvasa) — izdvojiti iza `if (typeof HTMLCanvasElement…)` ili preskočiti u vitestu; testira se samo model.

---

## 4. Feature B — Geometrija vitole (dužina × ring) u formuli + ritam

> Prema §0.5 (potvrđeno izvorima) i popunjenosti podataka (ring/lengthMM/format 99%, smokeTime 100%): geometrija **ulazi u formulu** kao `effCigar` prilagodba (B0), uz informativni ritam-hint (B1). Opcionalni kompleksnost-nudge (B2) ostaje iza zastavice.

### 4.0 B0 — Geometrija u bodovanju (novi `app/src/engine/vitolaGeometry.ts`)

Model iz §0.5: **tanji ring → gori toplije/brže, wrapper-dominantno, intenzivnije** (djeluje kao „jača i wrapper-glasnija” cigara); **deblji ring → hladnije, glađe, filler-naprijed** (blaže); **duže → dim se hladi, glađi start**.

```ts
import type { Cigar, PairingReason } from "../types";

// Kalibracija na jednom mjestu (kao WEIGHTS/SERVE_EFFECT). Male magnitude — geometrija
// dotjeruje, ne preokreće body-match. Pragovi: klasične granice ring gaugea.
export const GEOMETRY = {
  thinRingMax: 42,    // ≤42: panetela/corona/lonsdale/lancero — wrapper-forward, vruće
  thickRingMin: 54,   // ≥54: toro gordo/60 — hladno, glatko, filler-forward
  longLenMin: 160,    // ≥160mm: churchill/double corona — dim se hladi na putu
  thin:  { strengthDelta: +0.4, bodyDelta: +0.2, wrapperForwardBonus: 5 },
  thick: { strengthDelta: -0.3, bodyDelta: -0.1, wrapperForwardBonus: 0 },
  longSmoothStrengthDelta: -0.1, // duljina blago glača početnu oštrinu
} as const;

/** Ring/length iz odabrane vitole ili iz "RING x LENGTHmm" stringa; null ako nepoznato. */
export function parseGeometry(cigar: Cigar): { ring: number | null; len: number | null } {
  const v = cigar.vitolas?.[0];
  let ring = v?.ring ?? null;
  let len = v?.lengthMM ?? null;
  const m = /(\d{2})\s*[x×]\s*(\d{2,3})\s*mm/i.exec(cigar.format ?? "");
  if (ring == null && m) ring = Number(m[1]);
  if (len == null && m) len = Number(m[2]);
  return { ring, len };
}

/** EFEKTIVNA cigara (strength/body dotjerani geometrijom) + wrapper-forward bonus + reason.
 *  Ako geometrija nepoznata (1% unosa) → neutralno (cigar netaknut). */
export function applyGeometry(cigar: Cigar): {
  cigar: Cigar; wrapperForwardBonus: number; reason?: PairingReason;
} {
  const { ring, len } = parseGeometry(cigar);
  if (ring == null) return { cigar, wrapperForwardBonus: 0 };
  const clamp15 = (x: number) => Math.max(1, Math.min(5, x));
  let dS = 0, dB = 0, wrapperForwardBonus = 0, reason: PairingReason | undefined;

  if (ring <= GEOMETRY.thinRingMax) {
    dS += GEOMETRY.thin.strengthDelta; dB += GEOMETRY.thin.bodyDelta;
    wrapperForwardBonus = GEOMETRY.thin.wrapperForwardBonus;
    reason = { rule: "vitola-thin", score: 0, text: {
      hr: `Tanak ring (${ring}): gori toplije i brže, wrapper vodi — intenzivnije i začinjenije.`,
      en: `Thin ring (${ring}): burns hotter and faster, wrapper-led — more intense and spicy.` } };
  } else if (ring >= GEOMETRY.thickRingMin) {
    dS += GEOMETRY.thick.strengthDelta; dB += GEOMETRY.thick.bodyDelta;
    reason = { rule: "vitola-thick", score: 0, text: {
      hr: `Debeo ring (${ring}): gori hladnije i glađe, punija/mekša strana duhana.`,
      en: `Thick ring (${ring}): burns cooler and smoother, fuller/mellower tobacco.` } };
  }
  if (len != null && len >= GEOMETRY.longLenMin) dS += GEOMETRY.longSmoothStrengthDelta;

  const eff: Cigar = { ...cigar, strength: clamp15(cigar.strength + dS), body: clamp15(cigar.body + dB) };
  return { cigar: eff, wrapperForwardBonus, reason };
}
```

**Izmjena `pairing.ts`:** na početku izračunaj `const { cigar: effCigar, wrapperForwardBonus, reason: geoReason } = applyGeometry(cigar);` i koristi `effCigar` u:
- Pravilo 1/1b (body, overwhelm) — `effCigar.body`, `effCigar.strength`.
- Pravilo 4 (wrapper-affinity) — kad wrapper pogodi, dodaj `WEIGHTS.wrapperMatch + wrapperForwardBonus` (tanka cigara → wrapper glasniji, pa afinitet wrappera nosi više).
- Pravilo 5 (power) — `effCigar.strength`.
- Ako `geoReason`, `reasons.push(geoReason)`.
Redoslijed: `applyGeometry(cigar)` **i** `applyServe(drink, serve)` na vrhu; ostatak funkcije radi s `effCigar` + `effDrink`.

**Zašto ovo poštuje §0.5:** tanka cigara sad lakše „pregazi” delikatno piće (viši effStrength u 1b/5) i jače naginje wrapper-afinitetu (bonus u pravilu 4) — točno mehanizam „vruće + wrapper-forward”. Debela cigara djeluje blaže i glađe. Magnitude (≤0.4 koraka) drže body-match kao dominantno pravilo.

**Testovi (`app/src/engine/vitolaGeometry.test.ts`):**
- `parseGeometry` čita `vitola.ring`/`lengthMM`; fallback na regex iz `format`; `null` kad nema ni jedno.
- Tanak ring (npr. 38) → `effStrength > cigar.strength`, `wrapperForwardBonus === 5`, `vitola-thin` reason.
- Debeo ring (60) → `effStrength < cigar.strength`, bonus 0.
- Nepoznata geometrija → cigar netaknut, bonus 0, bez reasona.
- Integracijski: ista linija, tanka vs debela vitola, uz delikatno piće (body 2) → tanka ima **veću** overwhelm kaznu (niži score); uz jako začinjeno piće tanka ima **veći** wrapper-afinitet.
- Klemanje strength/body u [1,5].
- **Regresija:** cigara bez `vitolas`/`format` → `scorePairing` identičan staroj vrijednosti.

### 4.1 B1 — Ritam/trajanje hint (novi `app/src/lib/cigarRitual.ts`)

```ts
import type { Lang } from "../types";

export interface RitualHint { icon: string; text: string; }

/** Hint o ritmu pijenja prema trajanju pušenja (min). Bez bodovanja. */
export function ritualHint(smokeTimeMin: number | null | undefined, lang: Lang): RitualHint | null {
  if (!smokeTimeMin || smokeTimeMin <= 0) return null;
  if (smokeTimeMin >= 75) return { icon: "⏳", text: lang === "hr"
    ? `Duga cigara (~${smokeTimeMin}′): odaberi piće za sporo pijuckanje ili planiraj drugu turu.`
    : `Long cigar (~${smokeTimeMin}′): pick a drink to sip slowly, or plan a second pour.` };
  if (smokeTimeMin <= 30) return { icon: "⚡", text: lang === "hr"
    ? `Kratka cigara (~${smokeTimeMin}′): brz ritam, jedno dobro nalijevanje je dovoljno.`
    : `Short cigar (~${smokeTimeMin}′): a quick pace — one good pour is enough.` };
  return { icon: "⏱", text: lang === "hr"
    ? `Srednje trajanje (~${smokeTimeMin}′): ugodan tempo za jednu čašu.`
    : `Medium length (~${smokeTimeMin}′): an easy pace for a single glass.` };
}
```

**UI:** u odabranom panelu cigare (`selected` blok u `PairingPage`, `mode==="cigarToDrink"`) prikazati `ritualHint(selectedCigar.smokeTimeMin, lang)` kao tanki redak ispod metara. Isto može ići i na `ResultCard` za cigare (drinkToCigar) koristeći `r.item.smokeTimeMin`.

**Test** (`app/src/lib/cigarRitual.test.ts`): granice 30/75, `null`→`null`, HR/EN, umetnut broj minuta.

### 4.2 B2 — (opcionalno) blagi nudge u bodovanju
Iza kalibracijske zastavice u `rules.ts`:
```ts
// WEIGHTS
formatComplexityBonus: 0, // 0 = isključeno (default). Postavi npr. 3 za eksperiment.
```
Pravilo (u `pairing.ts`, iza `if (WEIGHTS.formatComplexityBonus > 0)`): duga cigara (`cigar.smokeTimeMin >= 75`) + kompleksno piće (`drink.qualityScore != null && drink.qualityScore >= 8`) → `+formatComplexityBonus` uz reason „Duga cigara traži piće koje se razvija u čaši”. Default 0 = **nema promjene u rangu** dok se ne kalibrira. Ne isporučivati uključeno bez A/B osjećaja; drži izvan prvog PR-a.

> Napomena: ring gauge (`Vitola.ring`) i `lengthMM` popunjeni su na **99%** (provjereno 2026-07-23, 5488/5516 vitola), pa **B0 (§4.0) koristi ring/length izravno** kao jezgru geometrije, dok `smokeTimeMin` (100%) nosi ritam (B1) i ovaj opcionalni B2 nudge. Za 1% bez dimenzija `applyGeometry` je neutralan.

---

## 5. Popis datoteka (za Cursor)

**Novi:**
- `app/src/engine/serve.ts` — `SERVE_EFFECT`, `applyServe` (vraća `{drink, effect, reason}`), serve reasons.
- `app/src/engine/serve.test.ts`
- `app/src/engine/vitolaGeometry.ts` — `GEOMETRY`, `parseGeometry`, `applyGeometry` (B0).
- `app/src/engine/vitolaGeometry.test.ts`
- `app/src/lib/shareCard.ts` — model + canvas render + share.
- `app/src/lib/shareCard.test.ts`
- `app/src/lib/cigarRitual.ts` — `ritualHint`.
- `app/src/lib/cigarRitual.test.ts`

**Izmjene:**
- `app/src/types.ts` — dodati `ServeStyle`.
- `app/src/engine/pairing.ts` — `serve?` param; na vrhu `applyGeometry(cigar)` + `applyServe(drink,serve)`; pravila koriste `effCigar`/`effDrink`, `aromaFactor`/`tameFactor` množitelje i `wrapperForwardBonus`.
- `app/src/engine/rules.ts` — (B2 opcionalno) `formatComplexityBonus: 0`.
- `app/src/pages/PairingPage.tsx` — serve state + ServeChips (drinkToCigar/custom), ritual hint (cigarToDrink), share gumb na `ResultCard`, read-only `serving.best` na drink karticama.
- `app/src/pages/CustomPairing.tsx` — serve selektor + proslijediti u `scorePairing`.
- `app/src/i18n/index.tsx` — novi ključevi (`serve.*`, `share.*`).
- (Opcionalno) `app/src/components/EveningSessionSheet.tsx` — share nakon spremanja.

---

## 6. Kriteriji prihvaćanja
- [ ] `npm test` prolazi; postojeći pairing/personal/integrity testovi **nepromijenjeni** (serve i format su opcionalni, default ne mijenja rezultate).
- [ ] `npm run build` (tsc) bez grešaka; nema novih dependencija u `package.json`.
- [ ] drinkToCigar: promjena serve stila **vidljivo** mijenja rang/score; `water` diže aromatsko preklapanje i smanjuje kaznu žestine, `rocks` ga spušta; objašnjenje u „zašto”.
- [ ] Geometrija (B0): ista linija u tankoj vs debeloj vitoli daje **različit** rang (tanka = jača/wrapper-glasnija); cigara bez dimenzija ne mijenja stari rezultat.
- [ ] cigarToDrink: prikazan `serving.best` (read-only) i ritual-hint za odabranu cigaru.
- [ ] Share gumb na mobitelu otvara share-sheet sa PNG-om; na desktopu preuzme PNG; kartica je u humidor paleti i čitljiva.
- [ ] Sve nove UI oznake dvojezične (HR/EN) preko `STRINGS`.
- [ ] Nema regresije u deep-linkovima/back tipki (serve je lokalni UI state, ne ide u hash — dokumentirati; ako se poželi dijeljivost serve stila, to je zaseban zahvat).

## 7. Redoslijed / PR razbijanje
1. **PR 1 — Serve Style (A):** `serve.ts` + engine (`serve?`, aroma/tame množitelji) + PairingPage/CustomPairing selektor + i18n + testovi. *(Najveća vrijednost.)*
2. **PR 2 — Geometrija vitole (B0):** `vitolaGeometry.ts` + `effCigar` u pravilima 1/1b/4/5 + testovi. *(Sada pravi ulaz formule; podaci 99% popunjeni.)* Može ići i prije PR 1 — modeli su nezavisni (serve množi aroma/žestinu, geometrija dotjeruje effCigar), a `pairing.ts` ih kombinira `effCigar × effDrink`.
3. **PR 3 — Share-kartica (C):** `shareCard.ts` + gumb + i18n + model test. *(Vidljivo, samostalno.)*
4. **PR 4 — Ritam/trajanje (B1) + B2:** `cigarRitual.ts` + hint u UI + test. **B2 ostaviti isključeno** (`formatComplexityBonus: 0`) dok se ne kalibrira.

> Ako PR 1 i PR 2 idu odvojeno: onaj koji stigne drugi samo doda svoj `eff*` u već postojeći izračun; `scorePairing` potpis je isti (`serve?` opcionalan, geometrija interna).

## 8. Izvan opsega / rizici
- **Ne** dirati Export/Import backup (već radi) niti localStorage shemu.
- **Ne** uvoditi cloud/nalog (to je „faza 2” iz README-a).
- Web Share API level 2 (`navigator.canShare({files})`) nije na svim desktop preglednicima → fallback download je obavezan.
- Serve delte su namjerno male; kalibraciju držati u `SERVE_ADJUST` (jedno mjesto), po uzoru na `WEIGHTS`.
- B2 nudge lako „preštima” rang — zato default 0 i izvan prvog izdanja.
