# Plan: lokalizacija okusa i serviranja + wishlist dedup

**Datum:** 2026-07-23
**Izvor:** korisnički report na live buildu (screenshotovi) nakon merge-a serve/geometrija/share/ritual.
**Za izvođača:** Cursor može preuzeti direktno — svaki bug ima točne datoteke, uzrok i popravak.
**Grana:** `claude/app-flyer-pr-campaign-dvvciz` (ili feature grana po bugu).

---

## 0. Kontekst — što je stvarno u problemu

Live **jest** deployan (na screenshotu se vidi novi ritam-hint „⏱ Medium length (~45′)” i ⤴ share gumb). Percepcija „nema razlike” dolazi iz dva razloga koja rješavamo:
1. **Serve selektor se po dizajnu prikazuje samo u `DRINK→CIGAR` i `COMBINE` modu**, a korisnik je bio u `CIGAR→DRINK`. → §4 (vidljivost, opcionalno).
2. **Okusi i serviranje nisu prevedeni** pa objašnjenja izgledaju „nedovršeno/isto”. → §1, §2 (glavni popravci).

Tri stvarna buga, po prioritetu: **A (okusi) → B (serving) → C (wishlist).**

---

## 1. Bug A — Flavor tagovi nisu prevedeni (glavni)

### Simptom
- `DetailSheet` chipovi prikazuju sirove kanonske tagove: `zacini`, `hrast`, `suho-voce`.
- Pairing „zašto” reasoni: „Shared notes: **zacini**”, „Complementary notes: **cedar ↔ hrast, zacini ↔ hrast, zacini ↔ suho-voce**”.
- Isti tekst u HR i EN — nema prijevoda ni čišćenja (`-` → razmak, dijakritika).

### Uzrok
Ne postoji rječnik oznaka okusa. `pairing.ts` gradi `reason.text.hr` i `.en` s **istim** sirovim tagovima (`shared.join(", ")`), a `DetailSheet` renderira `<Chip>{tag}</Chip>` bez prijevoda.

### Popravak

**1a. Novi rječnik + helper u `app/src/engine/rules.ts`** (uz `KNOWN_TAGS`):

```ts
// Prikazne oznake okusa (HR/EN). Ključ = kanonski tag (nakon normalizeTag).
// MORA pokrivati cijeli KNOWN_TAGS (integrity test to provjerava).
export const TAG_LABELS: Record<string, { hr: string; en: string }> = {
  kakao: { hr: "kakao", en: "cocoa" },
  kava: { hr: "kava", en: "coffee" },
  kremasto: { hr: "kremasto", en: "creamy" },
  zemljano: { hr: "zemljano", en: "earthy" },
  papar: { hr: "papar", en: "pepper" },
  zacini: { hr: "začini", en: "spice" },
  "zacini-slatki": { hr: "slatki začini", en: "sweet spice" },
  cedar: { hr: "cedar", en: "cedar" },
  drvo: { hr: "drvo", en: "wood" },
  hrast: { hr: "hrast", en: "oak" },
  med: { hr: "med", en: "honey" },
  citrus: { hr: "citrus", en: "citrus" },
  "trava-slatka": { hr: "slatka trava", en: "sweet grass" },
  travnato: { hr: "travnato", en: "grassy" },
  cvjetno: { hr: "cvjetno", en: "floral" },
  koza: { hr: "koža", en: "leather" },
  duhan: { hr: "duhan", en: "tobacco" },
  "tamno-voce": { hr: "tamno voće", en: "dark fruit" },
  "suho-voce": { hr: "suho voće", en: "dried fruit" },
  "tropsko-voce": { hr: "tropsko voće", en: "tropical fruit" },
  voce: { hr: "voće", en: "fruit" },
  jabuka: { hr: "jabuka", en: "apple" },
  orasasti: { hr: "orašasti", en: "nutty" },
  slatko: { hr: "slatko", en: "sweet" },
  gorko: { hr: "gorko", en: "bitter" },
  dim: { hr: "dim", en: "smoke" },
  karamela: { hr: "karamela", en: "caramel" },
  melasa: { hr: "melasa", en: "molasses" },
  vanilija: { hr: "vanilija", en: "vanilla" },
  mineralno: { hr: "mineralno", en: "mineral" },
  agava: { hr: "agava", en: "agave" },
  biljno: { hr: "biljno", en: "herbal" },
  vegetalno: { hr: "vegetalno", en: "vegetal" },
  mlijeko: { hr: "mlijeko", en: "milk" },
  milk: { hr: "mlijeko", en: "milk" },
  kokos: { hr: "kokos", en: "coconut" },
  psenica: { hr: "pšenica", en: "wheat" },
  caj: { hr: "čaj", en: "tea" },
  overproof: { hr: "overproof", en: "overproof" },
  "ester-funk": { hr: "esteri/funk", en: "ester/funk" },
  vino: { hr: "vino", en: "wine" },
};

/** Prikazna oznaka okusa. Fallback: prettify (‘-’→razmak) ako tag nije u rječniku. */
export function flavorLabel(tag: string, lang: "hr" | "en"): string {
  const canon = normalizeTag(tag);            // podnosi sirove/alias varijante
  const hit = TAG_LABELS[canon];
  if (hit) return hit[lang];
  return canon.replace(/-/g, " ");
}
```

> Napomena: `normalizeTag` je već u `rules.ts`. Popis gore je početni — **integrity test (1d) mora prisiliti potpunu pokrivenost `KNOWN_TAGS`**; Cursor dopuni što fali (npr. `demerara`/stilovi NISU u `KNOWN_TAGS` pa ne trebaju oznaku — u `KNOWN_TAGS` su samo okusni tagovi iz `COMPLEMENTS` + `WRAPPER_AFFINITY.tags` + `POWER_TAGS`).

**1b. `app/src/engine/pairing.ts` — prevedi tagove u reasonima.** Umjesto sirovog `join`, mapiraj po jeziku:

```ts
import { /* … */ flavorLabel } from "./rules";

// pravilo 2 (flavor-shared):
const top = shared.slice(0, 3);
reasons.push({
  rule: "flavor-shared",
  score: pts,
  text: {
    hr: `Dijele note: ${top.map((t) => flavorLabel(t, "hr")).join(", ")}.`,
    en: `Shared notes: ${top.map((t) => flavorLabel(t, "en")).join(", ")}.`,
  },
});

// pravilo 2b (flavor-complement): parove drži kao [ct, dt], ne string
const pairs = complemented.slice(0, 3); // complemented: Array<[string,string]>
reasons.push({
  rule: "flavor-complement",
  score: pts,
  text: {
    hr: `Note se nadopunjuju: ${pairs.map(([c, d]) => `${flavorLabel(c, "hr")} ↔ ${flavorLabel(d, "hr")}`).join(", ")}.`,
    en: `Complementary notes: ${pairs.map(([c, d]) => `${flavorLabel(c, "en")} ↔ ${flavorLabel(d, "en")}`).join(", ")}.`,
  },
});
```
Za ovo `complemented` promijeni s `string[]` (`"ct↔dt"`) na `Array<[string, string]>` (push `[ct, dt]`).

**1c. `app/src/components/DetailSheet.tsx` — prevedi chipove.** Dohvati `lang` iz `useI18n()` i:
```tsx
{cigar.flavorTags.map((tag) => (
  <Chip key={tag}>{flavorLabel(tag, lang)}</Chip>
))}
/* isto za drink.flavorTags */
```
(import `flavorLabel` iz `../engine/rules`.) Provjeri i `components/cards.tsx` te sve ostalo — `grep -rn "flavorTags" src` i primijeni `flavorLabel` gdje se tagovi prikazuju.

**1d. Integrity test** (`app/src/data/integrity.test.ts`, novi `it`): za svaki `tag` u `KNOWN_TAGS` očekuj da `TAG_LABELS[tag]` postoji i ima ne-prazan `hr` i `en`. Time nijedan tag ne ostane nepreveden.

---

## 2. Bug B — `serving.best` nije prevedeno u EN

### Simptom
Na EN, DetailSheet „Serving: **Čisto**” (ostaje hrvatski).

### Uzrok
`i18n/index.tsx:587`: `sv = (serving) => lang === "en" ? (SERVING_LABELS[serving] ?? serving) : serving`. Ključevi u `SERVING_LABELS` su bez dijakritike (`"Cisto"`), a podatak je `"Čisto"` (s Č) → promašaj → vraća original. (Provjereno: Germana `serving.best === "Čisto"`.)

### Popravak (`app/src/i18n/index.tsx`)
Napravi pretragu **neosjetljivu na dijakritiku i velika/mala slova**, uz token-fallback za kombinacije („A / B”):

```ts
const stripDia = (s: string) =>
  s.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();

// mapu indeksiraj po normaliziranom ključu (jednom, izvan render funkcije)
const SERVING_LABELS_NORM: Record<string, string> = Object.fromEntries(
  Object.entries(SERVING_LABELS).map(([k, v]) => [stripDia(k), v]),
);

// token rječnik za nepokrivene kombinacije
const SERVE_TOKENS: Record<string, string> = {
  cisto: "neat", "kap vode": "drop of water", "na ledu": "on the rocks",
  "on the rocks": "on the rocks", highball: "highball", "uz colu": "with cola",
  snifter: "snifter", "velika kocka leda": "large ice cube",
};

export function localizeServing(best: string, lang: "hr" | "en"): string {
  if (lang === "hr") return best;                      // podatak je već HR
  const direct = SERVING_LABELS_NORM[stripDia(best)];
  if (direct) return direct;
  // fallback: prevedi dio-po-dio oko "/"
  return best
    .split("/")
    .map((part) => SERVE_TOKENS[stripDia(part)] ?? part.trim())
    .join(" / ");
}
```
Zamijeni staru `sv` implementaciju s pozivom na `localizeServing`. Dopuni `SERVING_LABELS` za sve stvarne vrijednosti (`grep -oh '"best": *"[^"]*"' src/data/*.json | sort -u` → dodaj nedostajuće). Zadrži postojeće ključeve.

### Test
`app/src/data/hrGuide.test.ts` stil ili novi `serving.test.ts`: `localizeServing("Čisto","en") === "Neat"`, `localizeServing("Čisto / kap vode","en") === "Neat / drop of water"`, HR vraća original.

---

## 3. Bug C — Wishlist dupliciran (ukloni iz Collection)

### Simptom
Lista želja se vidi i na **Kolekcija** i na **Kupovina**.

### Odluka
Zadrži **samo u Kupovina** (`ShoppingPage`). Ukloni prikaz iz **Kolekcija**. Zadrži: (a) store polje `wishlist` (`store/collection.ts`) i (b) ☆ Wishlist **toggle** u `DetailSheet` (to je kontrola kojom se stavka dodaje na listu za Kupovinu).

### Popravak (`app/src/pages/CollectionPage.tsx`)
- Ukloni izračune `wishlistIds` (linije ~36–37), `wishlistCigars`/`wishlistDrinks` (~44–45).
- Ukloni render sekciju „☆ Wishlist” (~116–125, blok `{(wishlistCigars.length > 0 || wishlistDrinks.length > 0) && (…)}`).
- U uvjetu praznog stanja (~84) makni `wishlistIds.length === 0` član (ostaje `ownedIds`/`historyIds`).
- `ShoppingPage.tsx` ostaje netaknut. i18n ključ `coll.wishlistTitle` može ostati (nekorišten) ili se ukloni — po želji.

### Test
Nije nužan; smoke: `npm run build` + ručna provjera da Kolekcija nema wishlist sekciju, a Kupovina je ima.

---

## 4. (Opcionalno) Vidljivost serve stila i objašnjenja

Korisnik je očekivao promjene i u `CIGAR→DRINK` modu i „natuknice za sve”. Neobavezno, ali korisno:

- **4a. `serving.best` (lokalizirano) na svakoj kartici pića** u `CIGAR→DRINK` prijedlozima — read-only redak „Najbolje: {localizeServing(best, lang)}”. Malo, a odmah pokaže serve-kontekst tamo gdje selektora nema.
- **4b. (razmisliti)** serve selektor i u `CIGAR→DRINK` po kartici pića — veći zahvat (svaka kartica drugo piće); ostaviti za zasebni prijedlog.
- **4c. PWA cache:** ako korisnik i dalje vidi staro, treba osvježenje service workera (hard reload / „Ažuriraj” banner). Provjeri `vite-plugin-pwa` `registerType` u `app/vite.config.ts` — ako je `prompt`, dodati UI za update; ako `autoUpdate`, dovoljno je zatvoriti/otvoriti app. Dokumentirati u README.

---

## 5. Popis datoteka

**Izmjene:**
- `app/src/engine/rules.ts` — `TAG_LABELS`, `flavorLabel` (§1a).
- `app/src/engine/pairing.ts` — prijevod tagova u reasonima; `complemented` → `Array<[string,string]>` (§1b).
- `app/src/components/DetailSheet.tsx` — `flavorLabel(tag, lang)` za cigar+drink chipove; `localizeServing` za serving (§1c, §2).
- `app/src/components/cards.tsx` i drugi prikazi tagova — `flavorLabel` (grep!).
- `app/src/i18n/index.tsx` — `localizeServing` + normalizirana `SERVING_LABELS` + dopune (§2).
- `app/src/pages/CollectionPage.tsx` — ukloni wishlist sekciju (§3).
- (opc.) `app/src/pages/PairingPage.tsx` — `serving.best` na drink karticama (§4a).

**Testovi:**
- `app/src/data/integrity.test.ts` — `TAG_LABELS` pokriva `KNOWN_TAGS` (§1d).
- serving test (§2).

## 6. Kriteriji prihvaćanja
- [ ] EN mod: chipovi i „zašto” pokazuju „spice, oak, dried fruit…”, n=nema `zacini`/`hrast`/`suho-voce`.
- [ ] HR mod: „začini, hrast, suho voće…” (s dijakritikom, bez `-`).
- [ ] EN mod: „Serving: Neat” (ne „Čisto”); kombinacije prevedene.
- [ ] Kolekcija nema wishlist sekciju; Kupovina je ima; ☆ toggle u DetailSheetu radi.
- [ ] `npm test` zeleno (uklj. novi integrity test za oznake), `tsc` i `vite build` čisti.
- [ ] Bez regresije u pairing scoreovima (mijenja se samo **tekst** reasona, ne bodovi).

## 7. Redoslijed
1. **PR A** — flavor oznake (rules + pairing + DetailSheet + cards + integrity test). Najveći vizualni učinak.
2. **PR B** — serving lokalizacija.
3. **PR C** — wishlist dedup (Collection).
4. (opc.) **PR D** — serving.best na karticama + PWA update note.
