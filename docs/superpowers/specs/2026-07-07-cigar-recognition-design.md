# AI prepoznavanje cigara i ruma sa slike — dizajn

Datum: 2026-07-07
Status: prijedlog (čeka odobrenje)

## Kontekst i problem

Aplikacija (React PWA, statički hostana na GitHub Pages) ima OCR skeniranje preko
tesseract.js (`app/src/components/OcrScan.tsx`): fotografija → tekst → token-matching
na katalog. U praksi Tesseract s prstenova cigara ne izvuče upotrebljiv tekst
(ukrasni fontovi, zakrivljen tekst, zlatotisak, španjolski nazivi), pa matching nema
s čime raditi.

Aplikaciju koristi više ljudi, pa mora raditi bez da itko unosi API ključ.

## Cilj

Fotografiraš cigaru (prsten) ili bocu ruma → aplikacija pouzdano prepozna brend i
liniju → otvori odgovarajući artikl iz kataloga, ili ubaci prepoznati naziv u
tražilicu ako artikla nema.

## Arhitektura

```
Browser (GitHub Pages)                Cloudflare Worker              Anthropic API
┌─────────────────────┐   POST       ┌──────────────────┐           ┌────────────┐
│ ScanButton           │ /recognize   │ - CORS provjera   │  vision   │ Claude     │
│ - fotka → canvas     │ ───────────► │ - rate limit      │ ────────► │ Haiku 4.5  │
│   downscale ~1024px  │              │ - veličina/tip    │           │ structured │
│ - base64 JPEG        │ ◄─────────── │ - API ključ (tajna)│ ◄──────── │ output     │
│ - fuzzy match na     │   JSON       └──────────────────┘           └────────────┘
│   katalog            │
└─────────────────────┘
```

- API ključ živi isključivo kao Worker secret; nikad ne dolazi u browser.
- Tesseract.js se **uklanja** (manji bundle, jednostavniji kod). Nema offline
  fallbacka — ako Worker nije dostupan, prikazuje se poruka o grešci.

## Worker (`worker/`)

Novi TypeScript Cloudflare Worker u folderu `worker/` unutar repoa, deploy preko
`npx wrangler deploy`. Besplatni tier (100.000 zahtjeva/dan) je višestruko dovoljan.

### API ugovor

`POST /recognize`

Zahtjev:
```json
{ "image": "<base64 JPEG/PNG/WebP>", "media_type": "image/jpeg" }
```

Odgovor (200):
```json
{
  "type": "cigar" | "rum" | "unknown",
  "brand": "Partagás",
  "line": "Serie D No. 4",
  "confidence": "high" | "medium" | "low"
}
```

Greške: 400 (neispravan zahtjev / prevelika slika), 403 (nedopušten origin),
429 (rate limit), 502 (greška prema Anthropic API-ju).

### Poziv modela

- Model: **`claude-haiku-4-5`** (~0,2 centa po skenu), konfigurabilan kroz
  env varijablu Workera da se lako promijeni.
- Službeni `@anthropic-ai/sdk` (podržava Cloudflare Workers).
- Vision: slika kao base64 content block + kratki prompt („prepoznaj brend i
  liniju cigare s prstena / ruma s etikete").
- Strukturirani izlaz preko `output_config.format` (json_schema) — zajamčen
  parsabilan JSON, bez parsiranja slobodnog teksta.
- `max_tokens` malen (~500); odgovor je sitan JSON.

### Zaštita

- **CORS**: dopušten samo GitHub Pages origin (npr. `https://ivsitum1.github.io`)
  + `http://localhost:5173` za razvoj.
- **Rate limit**: ~10 zahtjeva/min po IP-u (Cloudflare rate-limiting binding ili
  jednostavan KV brojač — odluka u planu implementacije).
- **Validacija**: max ~2 MB base64, samo `image/jpeg|png|webp` media type.

## Klijentske izmjene (`app/`)

1. `OcrScan.tsx` → preimenovati u `ScanButton.tsx`:
   - ista UX površina (gumb 📷, `capture="environment"`, statusni toast),
   - fotka se u canvasu smanji na max 1024 px duže stranice, JPEG kvaliteta ~0.8,
   - POST na Worker URL (konstanta iz `import.meta.env.VITE_RECOGNIZE_URL` s
     defaultom na produkcijski Worker),
   - i18n poruke prilagoditi (postojeći `ocr.*` ključevi se prenamjenjuju).
2. **Matching na katalog**: strukturirani `brand` + `line` matchaju se na kandidate
   postojećom normalize/tokenize logikom, uz prioritet poklapanja brenda; prag
   pogotka može biti stroži jer je ulaz čist tekst. `type` sužava kandidate
   (cigare vs. rum).
3. Ako nema pogotka: `"{brand} {line}"` ide u tražilicu (postojeće ponašanje).
4. `tesseract.js` se briše iz `package.json`.

## Testiranje

- Vitest unit testovi za novu matching funkciju (strukturirani odgovor → artikl
  iz kataloga): točan pogodak, pogodak samo brenda, unknown, rum vs. cigara.
- Worker: ručna provjera kroz `wrangler dev` + curl prije deploya.
- Postojeći CI (test + build na push) pokriva klijentski dio.

## Deploy koraci (jednokratno, ručno)

1. Otvoriti besplatni Cloudflare račun.
2. Otvoriti Anthropic Console račun i kupiti početni kredit (~$5 ≈ više tisuća
   skenova s Haiku 4.5).
3. `npx wrangler secret put ANTHROPIC_API_KEY` + `npx wrangler deploy` iz `worker/`.
4. Upisati produkcijski Worker URL u konfiguraciju aplikacije.

## Izvan opsega

- Offline prepoznavanje / lokalni model.
- Korisnički uneseni API ključevi.
- Povijest skenova, spremanje slika (slike se ne pohranjuju nigdje).
- Prepoznavanje vitole/formata sa slike (samo brend + linija).
