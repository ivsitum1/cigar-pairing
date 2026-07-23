# Cigar & Drink Pairing — PR kampanja

**Kodno ime:** *Dosje № 007*
**Proizvod:** Cigar & Drink Pairing (PWA)
**Live:** https://ivsitum1.github.io/cigar-pairing/
**Ton:** James Bond — smiren, precizan, samouvjeren. Nikad glasan, nikad snobovski. Elegancija je u tome što se ništa ne prepušta slučaju.

---

## 1. Pozicioniranje u jednoj rečenici

> Sommelier za cigaru i čašu — u džepu, offline, bez računa: bira spoj, objasni zašto radi i kaže gdje kupiti.

**Elevator (10 s):** „Imaš cigaru i policu s bocama. Jedino pitanje je koja čaša — i to smo riješili. Aplikacija boduje spoj po tijelu, slatkoći i okusima, napiše ti zašto radi, i pokaže gdje kupiti u HR/EU/USA. Radi offline, ne traži račun.”

---

## 2. Dijagnoza: zašto ju ljudi (isprva) nisu željeli

Poštena procjena prepreka je temelj kampanje. Ne skrivamo prigovore — okrećemo ih u poruke. Ovo je srce cijele kampanje: **svaki prigovor ima ugrađen odgovor u samom proizvodu.**

| # | Prigovor (što smo čuli) | Korijen | Odgovor kampanje | Dokaz u proizvodu |
|---|--------------------------|---------|------------------|-------------------|
| 1 | „Još jedna aplikacija — pa registracija, pa dopuštenja…” | Umor od aplikacija; strah od podataka | **„Otvoriš link i radi.”** Nema računa, nema slanja podataka, instalacija je opcija. | Bez logina; sve u localStorage; PWA se otvara iz browsera |
| 2 | „Ne razumijem se dovoljno u cigare/pića.” | Osjećaj da je to za znalce | **„Nauči usput.”** Klub 101 vodi korak po korak; engine objasni svaki spoj. | Klub: 33 lekcije, leksikon, kviz; svaki pairing ima obrazloženje |
| 3 | „Gdje bih to uopće kupio?” | Jaz između preporuke i police | **„Kaže ti gdje.”** Trgovine i cijene po regiji, izravan link kad postoji. | HR/EU/USA filter; HR cijene scrapane; „Traži online” fallback |
| 4 | „Zvuči snobovski — sudit će moj ukus.” | Strah od elitizma | **„Sve je pairable, ništa se ne osuđuje.”** Dodaci se deklariraju, ne kažnjavaju. | Uređivačka politika: neutralno i informativno |
| 5 | „Naučeno je na engleskom, a ja pijem lokalno.” | Strani katalozi, strane cijene | **„Domaći teren.”** HR trgovine, HR cijene, hrvatski jezik. | Hrvatsko sučelje; HR vodič (7 poglavlja); shops.ts |
| 6 | „Nemam signala u lounge-u/na terasi.” | Loš wi-fi tamo gdje se puši | **„Radi bez signala.”** Offline-first PWA. | Service worker; data chunkovi cachirani |

**Sažetak strategije:** ne uvjeravamo ljude da su u krivu — pokazujemo da je svaki njihov prigovor već riješen. Kampanja je *demonstracija*, ne obećanje.

---

## 3. Publika

- **Primarna:** HR ljubitelji cigara i kvalitetnih pića (25–55), koji već imaju policu i cigaru, ali nagađaju kod spoja.
- **Sekundarna:** darivatelji (rođendan, umirovljenje, blagdani), lounge/cigar klubovi, vinoteke i specijalizirane trgovine.
- **Tercijarna:** znatiželjni početnici koje je dosad odbijao „snobovski” ton hobija.

---

## 4. Poruke (message house)

**Krovna poruka:** *Ništa se ne prepušta slučaju.*

Tri stupa:
1. **Precizno** — engine s objašnjenjem, ocjene unutar stila, izmjereni podaci gdje postoje.
2. **Privatno** — bez računa, bez slanja, radi offline; podaci ostaju kod tebe.
3. **Pristupačno** — hrvatski, s cijenama i trgovinama, uči te usput, ne osuđuje.

**Slogan banka (Bond ton):**
- „Odležano, ne prepušteno slučaju.”
- „Za večeri koje se pamte.”
- „Znaš cigaru. Sad znaš i čašu.”
- „Sommelier u džepu. Bez računa.”
- „Otvori, zapali, nazdravi.”

---

## 5. Kanali i taktike

| Kanal | Taktika | Format | KPI |
|-------|---------|--------|-----|
| Instagram / Facebook | „Spoj tjedna” — jedna cigara + jedna čaša + zašto radi | Carousel + reel (10–15 s) | Save/share rate |
| Cigar & whisky lounge-i (HR) | QR letak na stolovima („Skeniraj → tvoj spoj večeras”) | Tiskani letak (ovaj `flyer.html`) | Skenovi po lokaciji |
| Vinoteke / specijalizirane trgovine | Co-marketing: „Uz ovu bocu ide ova cigara” | Kartica na polici + link | Referral instali |
| Reddit r/cigars, r/whisky, HR forumi | Autentičan post kreatora: „Napravio sam alat jer sam bio umoran od nagađanja” | Tekst + screenshot | Klikovi na live |
| Blogeri / YouTuberi (cigare, whisky) | Rani pristup + „isprobaj i reci iskreno” | Recenzija/hands-on | Coverage komada |
| E-mail / newsletter | „Dosje” serija — jedan spoj + jedna lekcija tjedno | Plain-text, potpisan | Open/CTR |

**Zašto QR letak radi ovdje:** publika je fizički na mjestu (lounge, terasa) gdje im spoj treba *sada*. QR → live app u sekundi, offline nakon prvog otvaranja. Nula trenja.

---

## 6. Vremenski plan (6 tjedana)

- **Tjedan 0 — Priprema.** Letak u tisak i QR; press kit (ovaj dokument + screenshotovi + link). Rani pristup 5–10 kreatorima.
- **Tjedan 1 — Tihi start.** Objava kreatora („napravio sam alat…”). Prvi „Spoj tjedna”. Letci u 2–3 lounge-a.
- **Tjedan 2 — Dokaz.** Objaviti dijagnozu prigovora javno kao karusel: „6 razloga zašto ljudi nisu htjeli app — i zašto sada hoće.” Ovo je najviralniji komad jer je iskren.
- **Tjedan 3 — Partnerstva.** Vinoteke/trgovine: kartice na polici. Blogerske recenzije izlaze.
- **Tjedan 4 — Klub.** Gurati Klub 101 / kviz kao „razlog da se vratiš”, ne samo alat za jednom.
- **Tjedan 5 — Retrospektiva.** „Spoj mjeseca” od zajednice; UGC (korisnici dijele svoj dnevnik večeri).
- **Tjedan 6 — Zaključak.** Sažetak brojki, prikupiti svjedočanstva, planirati fazu 2 (cloud sync).

---

## 7. Press blurb (spreman za slanje)

**Kratki (za newsletter / caption):**
> Novi hrvatski alat *Cigar & Drink Pairing* rješava vječno pitanje uz cigaru: koja čaša? Bira spoj iz 525 cigara i stotina rumova, viskija, konjaka i vina — objasni zašto radi i pokaže gdje kupiti. Radi offline, ne traži račun. https://ivsitum1.github.io/cigar-pairing/

**Dulji (za blog/portal):**
> Većina preporuka za sparivanje cigara i pića završi na „probaj i vidi”. *Cigar & Drink Pairing* ide korak dalje: rule-based engine boduje svaki spoj po tijelu, slatkoći i okusima i napiše obrazloženje na hrvatskom. Katalog pokriva rum, whisky, konjak i brandy, gin, vino i kavu, svaki rangiran za sipping uz cigaru, s cijenama i trgovinama za HR, EU i USA. Uređivačka politika je namjerno neutralna — dodaci u pićima se transparentno deklariraju, a ne kažnjavaju. Aplikacija je PWA: instalira se na mobitel, radi offline i ne traži nikakav račun; sve ocjene i dnevnik ostaju na uređaju korisnika.

---

## 8. Social copy (primjeri)

**Objava „dijagnoza” (najvažnija):**
> Bili ste u pravu što ste bili skeptični.
> „Još jedna aplikacija.” → Nema računa. Otvoriš i radi.
> „Ne razumijem se.” → Uči te usput.
> „Gdje kupiti?” → Kaže ti, po regiji.
> „Snobovski je.” → Sve je pairable. Ništa se ne sudi.
> Cigara je vaša. Čašu prepustite nama. 🥃 [link]

**„Spoj tjedna”:**
> DOSJE № 12 — Padron 1964 × Diplomático Reserva.
> Puno tijelo traži rum koji ne popušta: karamela i suho voće drže korak s espresso-kakao dimom. Zašto? U appu, jedan tap. [link]

---

## 9. Mjere uspjeha

- **Aktivacija:** % posjeta koji naprave barem jedan pairing.
- **Povrat:** 7-dnevni povratni posjeti (Klub/kviz kao kuka).
- **Instalacije PWA-a** (add to home screen).
- **Referral po kanalu** (QR po lounge-u, UTM po partneru).
- **Coverage:** broj objava kreatora/portala.
- **Kvalitativno:** svjedočanstva „napokon znam koju čašu”.

---

## 10. Rizici i granice tona

- **Regulativa:** online prodaja duhana u HR nije dozvoljena — kampanja **nikad ne prodaje** cigare; linkovi su referentni. Uvijek „18+, uživajte odgovorno”.
- **Ton:** Bond, ne bahatost. Elegancija = suzdržanost. Bez „najboljeg”, bez osude tuđeg ukusa.
- **Privatnost je značajka, ne fusnota:** „bez računa, radi offline” je glavna poruka jer izravno gasi prigovor br. 1.

---

*Materijali: `marketing/flyer.html` (tiskani/QR letak, ista vizualna paleta kao app).*
