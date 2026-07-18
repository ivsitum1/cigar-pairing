# App backlog — NotebookLM grill 2026-07-18

**Grana:** `master` (PWA)  
**Puni dumpovi / knjižna sinteza:** grana `cursor/bonton-book-research-9b19` → `docs/bonton/research/notebooklm-grill/`  
**Most:** [`CROSSWALK.md`](./CROSSWALK.md)

> AI-sinteza iz NotebookLM (Gemini). Prije ugradnje u JSON/engine: `VERIFIED` | `INFERRED` | vanjska provjera. Ton appa: originalan HR/EN, ne YouTube idiom.

Stanje korpusa nakon refresha (3 ključne bilježnice): Cigar 101 **100**, Drink 101 **100**, Family Story **99** izvora. Ostale (Rum 101, Black Gold, Holt's, Oliva, value) grillane u prvom valu — dumpovi na book grani.

---

## 1. `bonton.json` — novi chapter *Lounge i klub*

**Prioritet:** visok · **Datoteka:** `app/src/data/bonton.json` (+ sync rukopisa `mala-knjiga-pusackog-bontona.md`)

Predloženi `id`: `b-lounge`

### HR body (skica precepta — preradi u app stil)

Naslov: *X. Lounge i klub* / EN: *X. Lounge and club*

Uvod: Javna pušionica nije tvoja terasa — ali ista pažnja prema tuđem zraku.

Bulleti (katalog `•`):

- Prije sjedanja pitaj je li mjesto slobodno; pozdravi prostor, ne samo šank.
- Rezač je zajednički samo ako je čist — ne vlaži cap slinom prije kućnog ili lounge rezača.
- Podrži kuću: u trgovini/klubu kupi barem jednu stavku ili poštuj njihov cut fee; na **privatnoj terasi** to pravilo ne vrijedi — tamo vrijedi gostoprimstvo.
- Dim gore ili od lica; na vjetru biraj smjer.
- Telefon: kratko ili vani; bez zvučnika i video poziva nad stolom.
- Pepeo u pepeljaru; na kraju ostavi cigar da se ugasi — ne stubaj ga poput cigarete.
- Ne traži „jedan dim” tuđe cigare; ne ispravljaj tuđe paljenje dok te ne pitaju.
- BYOB: dijeli što doneseš, ili ostavi bocu u autu.
- Parfem i cologne u mjeri — nepce drugih također degustira.
- Cigarete i vape nisu dio cigar salona; poštuj kućna pravila.

US footnote (opcionalno, kratko u EN ili samo u knjizi): tip 15–20% za uslugu cut/light — u HR rijetko standardizirano.

### Pojačanja postojećih chaptera

| Chapter | Dodati |
|---------|--------|
| V Pepeo | „Ne stubaj”; pepeo ~1" kao toplinska zaštita (ne trofej) |
| VI Stol | Ritual: miris → gutljaj → dim; ne umakati cigar u piće; Glencairn/copita + voda |
| VII Domaćin | Gostima početnicima blaža / „golf” vitola; ne forsiranje premium sticka |
| III Nuditi | BYOB dijeljenje; uzvratiti poklonjenu cigaru kad možeš |

---

## 2. Club 101 — nove / proširene lekcije

**Datoteke:** `app/src/data/club101.json`

| Predloženi naslov | Sadržaj | Izvor |
|-------------------|---------|--------|
| Higijena alata | Zajednički rezač, vlastiti pribor, spit cups, „stick licker” | Cigar 101 |
| Čaša i voda uz dim | Tulip/Glencairn; voda kao alat; led svjesno; pinch vode za high-proof | Drink / Rum 101 |
| Nic-sick i tempo | 60–90 s između dimova; šećer/čokolada ako zaboli; jaka kava + jaka cigar = oprez | Cigar 101 |
| Degustacijski redoslijed | Blago→jako; voda/čokolada između; ne swirl rum kao vino (kontradikcija — navedi nijansu) | Black Gold |
| Smoke your smoke | Ne snobizam; savjet samo na upit; Davidoff krutost vs suvremeni lounge | Cigar 101 + Family |

Holt's / Oliva dumpovi: koristiti za **tehničke / povijesne** 101 lekcije, ne za bonton tone.

---

## 3. Leksikon (`lexicon.json`)

Predloženi unosi:

| Term | Definicija (kratko) |
|------|---------------------|
| Cut fee | Naknada kad pušiš vanjsku cigaru u tuđem salonu |
| Mushrooms | Freeloaderi: Wi‑Fi, vlastito piće, bez kupnje (US slang — u HR: „besplatni gost”) |
| Smoke your smoke | Ne ocjenjuj tuđi izbor naglas |
| Smooth (piće) | Često marketing; može signalizirati additiv — usklađeno s uređivačkom politikom |
| Band etiquette | UK: skidanje prstena nakon paljenja; US: često ostavljen — nije moralni sud |
| Nic-sick | Nikotinska mučnina; uspori, voda, slatko |

---

## 4. Arhetipovi večeri (`eveningArchetypes.json`)

Iz Family Story — **originalan** eseistički ton, brandovi samo kao primjer ili zamijeni katalog ID-jevima iz appa:

1. **Cigar Box Vortex** — večer u kojoj nestaje vrijeme; srednje–puna cigar + bourbon slatkoće.  
2. **Highland Morning** — vani / jutro; delicatan format + crna kava.  
3. **Sweet & Savory** — peated scotch uz sweet/creamy sun-grown ili Maduro (ili soft-warn o phenolu).  
4. **Armenian Ritual** — formalnija večer; brandy/XO + elegantna vitola.

Dodatno: *Mentorski stol* vs *Tihi solo* (slušalice = ne ulaziti).

---

## 5. Quiz (`club.json`)

3–5 pitanja:

1. Što radiš s cigarom na kraju? (ostavi da se ugasi / stubaj)  
2. Zajednički rezač — vlažiti cap? (ne)  
3. Telefon na zvučniku u salonu? (ne)  
4. Tražiti puff tuđe cigare? (ne)  
5. Na privatnoj terasi moraš kupiti cigaru od domaćina? (ne — gostoprimstvo)

---

## 6. Pairing engine — kandidati (`app/src/engine/`)

Uskladiti s politikom: ocjena unutar stila; deklaracija dodataka; sve pairable.

| ID | Pravilo | Prioritet | Napomena |
|----|---------|-----------|----------|
| P1 | `cigar.body` ↔ `drink.intensity` / ABV tier | **visok** | mild↔lager/bijelo/kava; full↔CS/peat/espresso |
| P2 | ABV ≥ ~46% bolje drži puni dim | **visok** | 40% soft-downscore uz full body |
| P3 | Maduro ↔ residual sugar / sherry / aged sweet rum | srednji | UI: deklaracija šećera |
| P4 | CT ↔ kiselost / light coffee / white wine; CT ≠ heavy doslađeni rum | srednji | |
| P5 | Peated × cigar: ili max body match ili soft-warn „phenol clash” | srednji | Drink 101 kontradikcija |
| P6 | Tequila (reposado/añejo) kao dozvoljena white-spirit grana | nizak | proširiti kategoriju ako postoji |
| P7 | High-ester Jamaica ↔ robustna cigar | nizak | eksperiment |
| P8 | Nic-sick hint: jaka cigar + predloži slatko/ne espresso double | UI | ne score |
| P9 | Glassware hint Glencairn/copita | UI copy | ne score |

**Ne raditi:** hard-ban pića; „cigar uvijek protagonist”; shop blacklist obitelji vs conglomerate.

Testovi: proširiti postojeće engine testove za P1–P2 prije UI copyja.

---

## 7. Shopping / buy-link ton (opcionalno)

Family Story: preferirati obiteljske / pouzdane izvore — već djelomično pokriveno s „Kupi vs Traži online”. Ne hardcodati STG/JR ban.

---

## 8. Redoslijed implementacije (app)

1. `bonton.json` chapter Lounge (+ test snapshot ako postoji)  
2. Club 101: Higijena alata + Čaša/voda  
3. Quiz 3 pitanja  
4. Engine P1–P2 + testovi  
5. Leksikon 4 termina  
6. Arhetipovi (kad ima vremena za eseje)

---

## 9. Vanjski linkovi (referenca, ne scrape u app)

- https://www.cigarlounges.co/blog/cigar-lounge-etiquette  
- https://vdg-cigars.com/cigar-lounge-etiquette-the-complete-rules-guide/  
- https://www.themanual.com/culture/cigar-etiquette-101/  

---

*Zadnji sync s NotebookLM grillom: 2026-07-18. Book dumpovi: `cursor/bonton-book-research-9b19`.*
