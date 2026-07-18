# NotebookLM grill — sinteza za knjigu, Club i pairing

**Datum:** 2026-07-18  
**Metoda:** MCP `ask_question` discovery (1 upit / bilježnica) + vanjski Exa pregled lounge etikeete  
**Napomena o pouzdanosti:** NotebookLM odgovori su AI-sinteza YouTube/web korpusa — tvrdnje označavati `VERIFIED` (u izvoru) / `INFERRED` / `UNVERIFIED` prije ugradnje u kanonski rukopis. Deep follow-up na Cigar 101 nije prošao (UI overlay/timeout); discovery je dovoljno bogat za backlog.

---

## Mapiranje bilježnica

| UUID | Naziv | Izvora | Primarna vrijednost za projekt |
|------|--------|--------|--------------------------------|
| `2707d3fe-…` | **Cigar 101** | 56 | Lounge bonton, pepeo, tempo, snobizam, pairing intenziteta |
| `7d62a4d2-…` | **The cigar family Story** | 22 | Ton gostoprimstva, mentorski duh, ritual kao „moderni logorski plamen” |
| `c4044fbd-…` | (brand/value YouTube) | 28 | Tempo, vrijednost vs. snobizam, „stara škola” zajednice |
| `5b8ae55e-…` | **Holt's** | 61 | Retail/lounge praksa (tehnički 101 više nego bonton) |
| `e4921359-…` | **Drink 101** | 51 | Čaša, voda, led, bar etiketa, darovi, tempo gutljaja |
| `18ea7df7-…` | **Rum 101** | ~40+ | Additivi/„smooth”, ABV vs. dim, Maduro–slatkoća, agricole |
| `30d6a797-…` | **Black Gold / rum tasting** | 47 | Hosting degustacije, redoslijed, čišćenje nepca, swirl kontroverza |
| `5d9870a0-…` | **Oliva / heritage** | 99 | Povijest, zanati, klubovi/fabrike — Club 101 / arhetipovi, manje bonton |

Sirovi dumpovi (razbijeni): `docs/bonton/research/notebooklm-grill/<slug>/answer.md` + `sources-NN.md`.

---

## A. Knjiga (`mala-knjiga-pusackog-bontona.md`) — što dodati

Već pokriveno u rukopisu: prostor/suglasnost, nuditi/dijeliti, tempo, pepeo, stol, domaćin/gost, vani, poklon.  
**Nove građe iz grilla (prijedlog poglavlja / vignette — ne copy-paste YouTube tona):**

### A1. Novi/prošireni odjeljak: *Lounge / javna pušionica* (HR adaptacija)

Iz Cigar 101 + vanjskih vodiča ([CigarLounges etiquette](https://www.cigarlounges.co/blog/cigar-lounge-etiquette), [VDG](https://vdg-cigars.com/cigar-lounge-etiquette-the-complete-rules-guide/), [The Manual](https://www.themanual.com/culture/cigar-etiquette-101/)):

| Precept (kratko) | Status | HR napomena |
|------------------|--------|-------------|
| Ne vlaži cap prije zajedničkog rezača | VERIFIED (lounge corpus) | Ista higijena kod kuće ako dijeliš rezač |
| Kupi barem jednu stavku / poštuj cut fee | VERIFIED | U HR: specijalizirana trgovina / klub — podržati kuću |
| Dim gore ili od lica | VERIFIED | Terasa + vjetar već u gl. VIII |
| Telefon: kratko ili vani; bez zvučnika | VERIFIED | Dodati vignette „WhatsApp na speakeru” |
| Ne stubati cigar poput cigarete | VERIFIED | Već blisko gl. V — pojačati |
| Savjet samo kad traže | VERIFIED | Zlatno pravilo gl. I — potvrda |
| Ne traži „puff” tuđe cigare | VERIFIED | Gl. III — potvrda |
| BYOB: dijeli što doneseš | VERIFIED | Gl. III boca — proširiti na lounge |

**US-only (ne prenositi doslovno u HR knjigu):** tip $2–5 cut, dress-code „swanky”, cut fee kao standard — zamijeniti lokalnim običajima (klub/trgovina/terasa).

### A2. Vinjete za inbox → knjigu

1. **Stick licker** — gost navlaži cap, uzme kućni rezač → domaćin tiho nudi vlastiti rezač.  
2. **Speakerphone** — poziv usred stola → „izlazim 30 sekundi”.  
3. **Snob savjet** — netko ispravlja paljenje bez pitanja → treći mijenja temu.  
4. **Zadnja četvrtina boce** — Drink 101: podijeli dok je živa, ne čuvaj do „fotokopije”.  
5. **„Smooth” kompliment** — Rum 101: u stručnom društvu bolje opisati okus nego „glatko”.  
6. **Fotografija stola** — The Manual: pitaj prije lica u kadru (već u grill-inboxu).

### A3. Epigraf / duh

Family Story: cigar kao „modern campfire” / egalitarno utočište — uskladiti s „bonton nije policija ukusa”, bez američkog „Brotherhood” jargona.

---

## B. Club app — proširenja

| Sloj | Prijedlog | Izvor |
|------|-----------|--------|
| **Bonton** | Novi chapter: *Lounge i klub* (HR/EN) — 8–12 bulleta iz A1 | Cigar 101 + Exa |
| **Bonton** | Vinjete kao kratke „situacije” kartice (opcionalno UI kasnije) | discovery precepts |
| **Club 101** | Lekcija: *Higijena alata* (rezač, zajednički stol) | Cigar 101 |
| **Club 101** | Lekcija: *Čaša i voda uz dim* (Glencairn/copita, voda kao alat) | Drink 101, Rum 101 |
| **Club 101** | Lekcija: *Degustacijski redoslijed* (blago→jako; voda/čokolada između) | Black Gold |
| **Leksikon** | „Smooth” / additivi; plume vs. plijesan; cut fee | Cigar/Rum 101 |
| **Arhetipovi** | Večer „mentorski stol” vs. „tihi solo” (headphones signal) | Family + lounge vodiči |
| **Quiz** | 3–5 pitanja: stubanje? zajednički rezač? telefon? | Cigar 101 |

Holt's / Oliva: bogati za **101/povijest**, slabi za nove bonton precepts — ne forsirati u knjigu.

---

## C. Pairing engine — kandidati pravila

Uskladiti s postojećom uređivačkom politikom (ocjena unutar stila; deklaracija dodataka; sve pairable).

| Pravilo | Logika | Bilježnica | Prioritet |
|---------|--------|------------|-----------|
| **Body match** | mild↔lager/bijelo/kava; medium↔bourbon/aged rum; full↔peat/CS/espresso | Cigar 101, Rum 101 | visok |
| **Proof vs smoke** | visoki ABV (≈46%+) bolje drži puni dim; 40% često „nestane” | Rum 101 | visok |
| **Sweetness bridge** | doslađeni/aged sweet rum ↔ Maduro; oprez s Connecticut | Rum 101 | sred (deklaracija! ) |
| **Sugar vs nicotine** | slatko piće može ublažiti nikotinski udar; jaka kava + jaka cigar = dvostruki udar | Cigar 101 | sred (označiti INFERRED) |
| **Wrapper heuristics** | CT↔svjetliji rum/kava; Maduro↔tamna čokolada/espresso/dark rum | Black Gold, Rum 101 | već djelomično |
| **Ester/hogo** | high-ester Jamaica ↔ robustna cigar | Rum 101, Black Gold | nizak/eksperiment |
| **Agricole** | biljni/travnati profil ↔ CT / herbal cigar | Rum 101 | nizak |
| **Glassware soft rule** | tulip/Glencairn u dimu (nije score, UI hint) | Drink/Rum 101 | UI copy |
| **Progression** | blago→jako u večeri (već u bonton VI) | Black Gold | UI/Club |

**Ne implementirati slijepo:** „cigar je uvijek protagonist” (Black Gold) — u vašem app modelu večer je dijalog, ne hijerarhija.

---

## D. Vanjska literatura (Exa, 2026)

- [Cigar lounge etiquette — CigarLounges](https://www.cigarlounges.co/blog/cigar-lounge-etiquette)  
- [VDG — complete rules](https://vdg-cigars.com/cigar-lounge-etiquette-the-complete-rules-guide/)  
- [Casa de Montecristo — beginners](https://www.casademontecristo.com/broadleaf-social/cigar-lounge-etiquette-for-beginners/)  
- [The Manual — cigar etiquette 101](https://www.themanual.com/culture/cigar-etiquette-101/)  
- Debrett/Post i dalje na listi u `grill-inbox.md` (struktura precepta, ne sadržaj o cigar)

---

## E. Sljedeći koraci (predloženi redoslijed)

1. Unijeti A1 bullets u `grill-inbox.md` + odabrati 3 vinjete za rukopis.  
2. Draft chapter *Lounge i klub* u `bonton.json` (HR/EN) — **tekst originalan**, ne YouTube idiom.  
3. Club 101: 2 lekcije (čaša/voda; higijena alata).  
4. Pairing: kalibracija `body`/`abv`/`sweetness` u `rules.ts` s testovima — samo VISOK prioritet.  
5. Po želji: ponoviti deep grill na Cigar 101 + Drink 101 (svježi session, zatvoriti Chrome overlay).

---

*Zadnje ažuriranje: 2026-07-18. Quota NotebookLM: ~9 discovery upita potrošeno; deep retry fail.*
