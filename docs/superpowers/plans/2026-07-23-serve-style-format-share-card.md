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

Prioritet isporuke: **A → C → B** (A ima najveću vrijednost i najčišći dodir; C je vidljiv i sam za sebe; B je fino ugađanje).

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

```ts
import type { Drink, PairingReason, ServeStyle } from "../types";

// Delte na EFEKTIVNI profil pića (float dopušten; klemanje 1..5 na kraju).
// Kalibracija namjerno konzervativna — serve nikad ne smije biti presudan.
export const SERVE_ADJUST: Record<ServeStyle, { body: number; sweetness: number }> = {
  neat:     { body:  0.0, sweetness:  0.0 }, // baseline
  water:    { body: -0.5, sweetness:  0.0 }, // kap vode: otvara aromu, spušta žestinu
  rocks:    { body: -0.7, sweetness: -0.5 }, // led: priguši arome i slatkoću
  highball: { body: -1.5, sweetness:  0.5 }, // soda: razrijedi tijelo, doda svježinu
  cola:     { body: -1.0, sweetness:  1.5 }, // cola: razrijedi + naglo digne slatkoću
};

const clamp15 = (v: number) => Math.max(1, Math.min(5, v));

/** Vrati piće s prilagođenim (float) body/sweetness + objašnjenje serve stila. */
export function applyServe(
  drink: Drink,
  serve: ServeStyle | undefined,
): { drink: Drink; reason?: PairingReason } {
  if (!serve || serve === "neat") return { drink };
  const d = SERVE_ADJUST[serve];
  const adjusted: Drink = {
    ...drink,
    body: clamp15(drink.body + d.body),
    sweetness: clamp15(drink.sweetness + d.sweetness),
  };
  return { drink: adjusted, reason: SERVE_REASON[serve] };
}

const SERVE_REASON: Record<Exclude<ServeStyle, "neat">, PairingReason> = {
  water: { rule: "serve-water", score: 0, text: {
    hr: "Kap vode otvara aromu i spušta žestinu — spoj bolje podnosi i blažu cigaru.",
    en: "A drop of water opens the aroma and tames the heat — the match tolerates a milder cigar." } },
  rocks: { rule: "serve-rocks", score: 0, text: {
    hr: "Led priguši arome i slatkoću — tijelo pića djeluje lakše.",
    en: "Ice mutes aroma and sweetness — the drink reads lighter." } },
  highball: { rule: "serve-highball", score: 0, text: {
    hr: "Highball razrjeđuje tijelo i dodaje svježinu — traži lakšu cigaru.",
    en: "A highball dilutes the body and adds lift — it calls for a lighter cigar." } },
  cola: { rule: "serve-cola", score: 0, text: {
    hr: "Cola naglo diže slatkoću — mijenja kontrast prema tamnijoj, punijoj cigari.",
    en: "Cola spikes the sweetness — it shifts the contrast toward a darker, fuller cigar." } },
};
```

> `score: 0` znači: reason se **prikaže** u „zašto”, ali sam po sebi ne dodaje bodove. Efekt na rezultat dolazi kroz **prilagođeni body/sweetness** koji ulaze u postojeća pravila (body-match, overwhelm, contrast-sweet-maduro). Time izbjegavamo dvostruko bodovanje i držimo engine čitljivim.

### 2.4 Izmjena `app/src/engine/pairing.ts`

Dodati opcionalni 4. argument i primijeniti serve na početku:

```ts
export function scorePairing(
  cigar: Cigar,
  drink: Drink,
  prefs?: PersonalPrefs,
  serve?: ServeStyle,          // NOVO
): { score: number; reasons: PairingReason[] } {
  const { drink: effDrink, reason: serveReason } = applyServe(drink, serve);
  // …ostatak koristi effDrink umjesto drink…
  // na kraju, prije return, ako serveReason: reasons.push(serveReason)
}
```

- `bodyDiff = Math.abs(cigar.body - effDrink.body)` — sad radi s floatom; `BODY_LABEL_HR[…]` indeksirati s `Math.round(effDrink.body)`.
- Pravilo 3 (contrast-sweet-maduro) čita `effDrink.sweetness` → cola automatski pojačava kontrast.
- Proslijediti `serve` kroz `pairCigarsForDrink(drink, cigars, prefs, serve?)`. `pairDrinksForCigar` **ostaje bez serve** (opseg §2.2).

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
- `applyServe(drink,"neat")` vraća isti body/sweetness (bez reasona).
- `water` spušta body i dodaje `serve-water` reason.
- `cola` diže sweetness ≥ +1 i klema na 5 kad je već visoko.
- Klemanje: `highball` na piću body=1 ostaje ≥1.
- Regresija u `pairing.test.ts`: `scorePairing(c,d,undefined,undefined)` === stara vrijednost (serve opcionalan ne mijenja default).
- Integracijski: jako piće (body 5, overproof tag) + blaga cigara → `water` **smanjuje** kaznu (viši ili jednak score).

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

## 4. Feature B — Format & Trajanje (ritam)

> Podaci već postoje. **B1 (informativni ritam-hint) isporučiti; B2 (nudge u bodovanju) ostaje opcionalno/experimentalno iza zastavice.**

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

> Napomena: ring gauge (`Vitola.ring`) i `lengthMM` postoje, ali nisu popunjeni za sve unose — zato B temeljimo na `smokeTimeMin` (najpotpuniji signal). Ako kasnije poželiš ring-based intenzitet, prvo provjeri popunjenost polja skriptom.

---

## 5. Popis datoteka (za Cursor)

**Novi:**
- `app/src/engine/serve.ts` — `SERVE_ADJUST`, `applyServe`, serve reasons.
- `app/src/engine/serve.test.ts`
- `app/src/lib/shareCard.ts` — model + canvas render + share.
- `app/src/lib/shareCard.test.ts`
- `app/src/lib/cigarRitual.ts` — `ritualHint`.
- `app/src/lib/cigarRitual.test.ts`

**Izmjene:**
- `app/src/types.ts` — dodati `ServeStyle`.
- `app/src/engine/pairing.ts` — `serve?` param u `scorePairing` i `pairCigarsForDrink`; koristi `effDrink`.
- `app/src/engine/rules.ts` — (B2 opcionalno) `formatComplexityBonus: 0`.
- `app/src/pages/PairingPage.tsx` — serve state + ServeChips (drinkToCigar/custom), ritual hint (cigarToDrink), share gumb na `ResultCard`, read-only `serving.best` na drink karticama.
- `app/src/pages/CustomPairing.tsx` — serve selektor + proslijediti u `scorePairing`.
- `app/src/i18n/index.tsx` — novi ključevi (`serve.*`, `share.*`).
- (Opcionalno) `app/src/components/EveningSessionSheet.tsx` — share nakon spremanja.

---

## 6. Kriteriji prihvaćanja
- [ ] `npm test` prolazi; postojeći pairing/personal/integrity testovi **nepromijenjeni** (serve i format su opcionalni, default ne mijenja rezultate).
- [ ] `npm run build` (tsc) bez grešaka; nema novih dependencija u `package.json`.
- [ ] drinkToCigar: promjena serve stila **vidljivo** mijenja rang/score i dodaje serve-objašnjenje u „zašto”.
- [ ] cigarToDrink: prikazan `serving.best` (read-only) i ritual-hint za odabranu cigaru.
- [ ] Share gumb na mobitelu otvara share-sheet sa PNG-om; na desktopu preuzme PNG; kartica je u humidor paleti i čitljiva.
- [ ] Sve nove UI oznake dvojezične (HR/EN) preko `STRINGS`.
- [ ] Nema regresije u deep-linkovima/back tipki (serve je lokalni UI state, ne ide u hash — dokumentirati; ako se poželi dijeljivost serve stila, to je zaseban zahvat).

## 7. Redoslijed / PR razbijanje
1. **PR 1 — Serve Style (A):** `serve.ts` + engine param + PairingPage/CustomPairing selektor + i18n + testovi. *(Najveća vrijednost.)*
2. **PR 2 — Share-kartica (C):** `shareCard.ts` + gumb + i18n + model test. *(Vidljivo, samostalno.)*
3. **PR 3 — Ritam/trajanje (B1):** `cigarRitual.ts` + hint u UI + test. **B2 ostaviti isključeno** (`formatComplexityBonus: 0`) dok se ne kalibrira.

## 8. Izvan opsega / rizici
- **Ne** dirati Export/Import backup (već radi) niti localStorage shemu.
- **Ne** uvoditi cloud/nalog (to je „faza 2” iz README-a).
- Web Share API level 2 (`navigator.canShare({files})`) nije na svim desktop preglednicima → fallback download je obavezan.
- Serve delte su namjerno male; kalibraciju držati u `SERVE_ADJUST` (jedno mjesto), po uzoru na `WEIGHTS`.
- B2 nudge lako „preštima” rang — zato default 0 i izvan prvog izdanja.
