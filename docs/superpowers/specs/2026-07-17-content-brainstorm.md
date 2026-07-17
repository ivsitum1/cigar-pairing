# Content brainstorm — Cigar & Drink Pairing

**Datum:** 2026-07-17  
**Vrsta:** urednički memo (sadržaj / kultura / učenje), ne tehnička specifikacija  
**Jezik:** hrvatski (kanonski ton za pisanje)  
**Opseg:** što pisati i kurirati za čitatelja — znanje, bonton, pairing kultura, kupnja, degustacijski jezik, HR tržište. Bez APIja, shema, UI komponenti ili implementacije značajki.

---

## Napomena o bontonu (važno)

Autor će **kasnije sam** graditi *grill notebook* (radnu bilježnicu) za *Malu knjigu pušačkog bontona*, dok paralelno skuplja materijal. Ovaj memo **ne predlaže** prepisivanje ili proširenje cijelog rukopisa sada. Za bonton se predlažu samo **kutovi istraživanja i sakupljanja** (citati, situacije, lokalni običaji, pitanja za stolom) — sirovina za budući grill, ne nova verzija knjige.

---

## 1. Inventar postojećeg sadržaja

Što već postoji kao *čitanje / učenje / uređivanje*, ne kao kod.

### 1.1 Club — rotacija i provjera znanja (`club.json`)

| Sloj | Opseg | Karakter |
|------|-------|----------|
| Citati | ~24 | Twain, Churchill, Kipling, Hemingway i dr.; dvojezično; napomene o atribuciji |
| Činjenice („Jeste li znali?”) | ~72 | Kratke deklarativne činjenice (angel's share, stilovi, pravila) |
| Kviz | ~71 | Pitanje + 4 odgovora + „zašto”; jaka pokrivenost aditiva/EU pravila, osnovne kategorije |

**Urednički dojam:** solidan „dnevni dozir” znanja; ton informativan, ne moralizatorski. Još nije sustavni kurikulum — to je 101.

### 1.2 Club 101 — kurikulum (`club101.json`)

Četiri trake, već zrele kao katalog lekcija:

1. **Cigare** (8) — vitole, snaga/tijelo, wrapperi, humidor, rez, paljenje, vučenje/trećine, pairing ulaz.
2. **Pića** (8) — etiketa, VS/VSOP/XO, destilacija, bačva/solera, rum↔whisky karte, vino/sherry/porto (+ prošek), serviranje, aditivi/transparentnost.
3. **Pribor** (7) — čaše, humidori, rezači, pepeljare, dekanteri, upaljači, minimalni kit (+ shop linkovi gdje ima smisla).
4. **Savjeti** (8) — ritam, voda/kava, hrana, odmor, bilješke, vrijeme, budžet, gosti.

**Urednički dojam:** najbogatiji prozni sloj u proizvodu. Format je katalog (odlomak + točke) — pogodan za brzo čitanje, manje za dugi „esej večeri”.

### 1.3 Bonton (`bonton.json` + kanonski MD)

- **10 poglavlja** od duha bontona do zadnje riječi; HR + EN.
- Radni rukopis: `docs/bonton/mala-knjiga-pusackog-bontona.md` (~480 redaka, uključujući engleski referent).
- Ton: gostoprimstvo, mjera, suglasnost; „bonton nije policija ukusa”.
- Spec već postoji (`2026-07-16-club-bonton-design.md`) — oblik knjige bontona, ne tehnika.

**Urednički dojam:** jezgra je napisana i konzistentna. Sljedeći korak nije rewritе, nego sakupljanje materijala za grill notebook (vidi §6 i inicijativu F).

### 1.4 Katalozi — bilješke i pairing tragovi

| Katalog | Broj (orijentir) | Bilješke (kvaliteta) | Pairing tragovi |
|---------|------------------|----------------------|-----------------|
| Cigare | ~480–525 | ~230 bogatijih; mnogo kratkih; velik udio *procijenjenih profila* | `flavorTags`, snaga/tijelo; nema zasebnog „eseja spoja” |
| Rum | ~147 | većinom kratke; manji dio bogatih | `serving`, polje za `cigarHint` uglavnom prazno |
| Whisky | ~278 | mnogo kratkih + heurističkih profila; malo bogatih | isto |
| Brandy/grappa | ~80+ | većinom kratke | isto |
| Vino | ~50+ | relativno bogatije (porto/sherry/prošek) | isto |
| Gin / kava | ~20 / ~23 | tanko | kategorije postoje, kultura pairinga tek naznačena |

Uređivačka politika (README) već određuje ton kataloga: **deklaracija umjesto osude**, ocjena unutar stila, sve je pairable, različita pravila po kategoriji.

### 1.5 Shopping / HR dostupnost

- Cijene i shop linkovi (allez, ecuga, humidor, vinoteke…) kao *podatak*, ne kao vodič u prozi.
- README jasno: online prodaja duhana u HR nije dozvoljena — linkovi na cigare su referentni.
- `shopping.json` više liči na osobni plan kupnje nego na čitateljski vodič.

**Urednički dojam:** infrastruktura za kupnju postoji; **editorial shopping guidance** (kako birati u HR, što očekivati u trgovini, kako čitati cijenu/link) još nije napisan kao sadržaj.

### 1.6 Teme već pokrivene u `docs/superpowers/specs/`

Postojeći specovi uglavnom su *proizvod/tehnika* (Club 101 + pribor, bonton kao view, OCR, linkovi/karta). Ovaj memo namjerno nadopunjuje ono što ti dokumenti **ne** pokrivaju: što čitatelj još treba pročitati, naučiti i osjetiti.

---

## 2. Praznine i prilike (gdje proizvod djeluje „tanak” kao iskustvo čitanja)

1. **Jezik degustacije nije učen, nego pretpostavljen.** Tagovi (`cedar`, `peat`, `suho-voce`) rade u motoru, ali korisnik rijetko dobije rječnik mostova: što znači „most”, kako opisati trećinu, kako razlikovati snagu od tijela riječima (101 to dotiče, ali nema leksikona).
2. **Pairing kultura živi u motoru, ne u narativu.** Nema kratkih „večernjih arhetipova” (npr. *nedjeljni amontillado + Connecticut*, *zimski maduro + tawny*) koje bi učile *zašto* spoj radi — samo rang lista.
3. **HR kut nije proza.** Dostupnost, referentni linkovi, zabranjena online prodaja duhana, razlika allez/ecuga/vinoteka/humidor — sve je u napomenama i podacima, ne u vodiču za čitatelja.
4. **Nejednaka gustoća bilješki.** Whisky (i dijelom rum/brandy) često zvuči heuristički; vino i dio cigara nose više „glasa”. Čitatelj osjeti katalog kao bazu podataka, ne kao kurirani glas.
5. **`cigarHint` / serving tekstovi gotovo ne postoje kao urednički sloj** — polja su spremna, proza nije.
6. **Gin i kava** u 101 i katalogu stoje na margini; uz cigaru imaju smisla (aperitiv, jutro, espresso most), ali nemaju vlastiti jezik u proizvodu.
7. **Bonton je zatvoren kao knjiga, otvoren kao istraživanje.** Rukopis je dovoljan za app; grill notebook treba *sirovinu* (situacije, lokalni običaji, pitanja), ne novi draft svih 10 poglavlja.
8. **Činjenice/kviz** dobro pokrivaju aditive i osnove; slabije pokrivaju degustacijski vokabular, HR kontekst i „meke” situacije stola (gdje se 101 savjeti i bonton susreću).

---

## 3. Inicijative (rangirane: vrijednost vs urednički trud)

Trud = pisanje, kuracija, istraživanje izvora — **ne** inženjering.

| Rang | Inicijativa | Vrijednost | Trud | Zašto sada |
|------|-------------|------------|------|------------|
| **A** | Leksikon pairing jezika (mostovi, trećine, tijelo, „što osjećam”) | Visoka | Srednji | Pretvara motor i tagove u čitljivo učenje; jedinstven glas proizvoda |
| **B** | HR vodič kupnje i dostupnosti (piće + referentno duhan) | Visoka | Srednji–nizak | Lokalna prednost; smanjuje zbunjenost oko cijena/linkova/zakona |
| **C** | Kurirane bilješke + `cigarHint` za top N po kategoriji | Visoka (svakodnevna) | Visok, ali inkrementalan | Katalog prestaje biti „prazan” kad korisnik otvori detalj |
| **D** | Večernji arhetipovi (6–8 kratkih pairing eseja) | Visoka (angažman) | Srednji–nizak | Uči kulturu spoja bez ovisnosti o UI-ju |
| **E** | Popuna kviza/činjenica: degustacija + HR + gin/kava | Srednja | Nizak | Brz win uz postojeći Club ritam |
| **F** | Sakupljanje materijala za bonton grill notebook | Srednja (dugoročno) | Nizak sada | Poštuje autorov plan; ne dira kanonski rukopis |
| **G** | Gin & kava — mini 101 / pairing kutovi | Srednja | Srednji–nizak | Popunjava najtanje kategorije |
| **H** | Predložak degustacijske bilješke (prozni „kako bilježiti”) | Srednja | Nizak | Nadograđuje postojeći tip `t-notebook` bez novog sustava |

**Preporučeni redoslijed rada:** A → B → D (brzi narativ) paralelno s C u malim serijama; E/F/H kao „uvijek uključeno” sakupljanje; G kad A/B sjednu.

---

## 4. Top 3 — obrisi

### A. Leksikon pairing jezika

**Cilj.** Jedan čitljiv rječnik (HR, uz EN paralel kasnije) koji uči korisnika govoriti o spoju cigare i pića — ne o bodovima.

**Predložena poglavlja / odjeljci**

1. **Što je most** — zajednička nota vs. kontrast; „ne pobjeda okusa”.
2. **Tijelo ↔ tijelo** — gustoća dima i punoća gutljaja (veza na 101, ali rječnikom).
3. **Snaga vs. tijelo** — riječi za nikotin i za „težinu” dima; što nije isto.
4. **Trećine** — rječnik prve / srednje / zadnje; kada skratiti.
5. **Obitelji nota** — cedar, kakao, orah, citrus, dim, sol, koža… s *pairable* primjerima (piće × wrapper), bez hijerarhije „bolje/gore”.
6. **Riječi za ritam** — vruće, prebrzo, crni pepeo, „zatvoreno nepce”.
7. **Riječi za stol** — kako pohvaliti, kako pitati, kako reći „ne paše mi” (most prema bontonu, bez prepisivanja bontona).
8. **Mini vježbe** — 3–5 rečenica koje korisnik može napisati u Kolekciji nakon večeri.

**Ton.** Deklarativan, učiteljski-blag, kategorijski precizan; bez snobizma i bez „must-try” marketinga.

**Izvori za crtanje (ne za copy-paste)**

- Postojeći Club 101 (`c-pair-start`, `c-strength-body`, `d-additives`, tipovi).
- Vlastite bilješke iz Kolekcije / degustacija autora.
- Javni stilski okviri: BNIC (konjak), SWA/etikete scotcha, EU 2019/787 (rum/šećer), Jerez/porto terminologija — **kao činjenice**, ne kao tuđi prose.
- Neutrale lab napomene (Systembolaget/Alko) gdje potkrjepljuju deklaraciju aditiva.

**Što ne kopirati**

- Tuđe tasting note banke (Whiskybase recenzije, Cigar Aficionado prose, blogovi) — parafrazirati nije dovoljno ako struktura i fraze ostaju tuđe.
- Marketinške „flavour wheels” brendova kao vlastiti kanon.
- Moraliziranje o aditivima; držati se politike deklaracije.

---

### B. HR vodič kupnje i dostupnosti

**Cilj.** Kratki, pošteni vodič: gdje i kako u Hrvatskoj (i online za piće) nabaviti što treba za pairing večer — bez lažne preciznosti cijena i bez poticanja ilegalne kupnje duhana.

**Predložena poglavlja / odjeljci**

1. **Što zakon i praksa znače za čitatelja** — online duhan nije u ponudi kao kupnja; što su referentni linkovi; piće se kupuje drugačije.
2. **Karta trgovina (piće)** — allez, ecuga, vinoteke (Vivat/Miva/Vrutak…), diskonti: što očekivati (širina, cijena, etiketa), ne rang „najbolji shop”.
3. **Karta duhana (referentno)** — humidor / specijalizirane trgovine: što gledati uživo (RH, vitola, stanje), zašto cijena na webu nije košarica.
4. **Kako čitati cijenu u appu** — `priceApprox`, shop hint, „traži online” vs. točan link; očekivati odstupanja.
5. **Prvi kit u HR budžetu** — veza na `a-kit` / `t-budget`: jedna čaša, rezač, putni humidor ili tegla, 2–3 boce različitog stila.
6. **Sezona i zaliha** — što se brzo troši, što odležava; kad ima smisla VSOP vs. lov na rare.
7. **Poklon u HR kontekstu** — most prema bontonu IX, lokalno dostupne boce/kutije.

**Ton.** Praktičan, gostoljubiv, bez affiliate glasa; transparentan o neizvjesnosti cijena.

**Izvori**

- README napomene o HR prodaji duhana i shopovima.
- Vlastito iskustvo autora s allez/ecuga/humidor/vinotekama.
- Javne informacije trgovina (katalog kategorija), ne scraped „tajni” cjenici kao urednička istina.
- Club 101 pribor + savjeti o budžetu.

**Što ne kopirati**

- Tuđe „top 10 shopova” članke i price-comparison blogove.
- Tvrdnje o stalno točnim cijenama ili zalihama.
- Upute koje zaobilaze zabranu online prodaje duhana.

---

### C. Kurirane bilješke + `cigarHint` (top N po kategoriji)

**Cilj.** U uredničkim serijama (npr. 15–25 stavki po valu) podići glas kataloga: kratka bilješka koja *uči*, plus 1–2 rečenice `cigarHint` gdje motor ne govori dovoljno.

**Predloženi redoslijed valova**

1. **Rum MASTER favoriti + transparentni „čisti” stilovi** (već imaju političku težinu u appu).
2. **Whisky klasici** (seed / često heuristic → prava bilješka).
3. **Fortificirana vina i sherry** (već bogatija baza — uskladiti glas).
4. **Brandy/XO i HR vinjak** (lokalni kut).
5. **Cigare s `profileEstimated`** — prioritet markama koje korisnik stvarno susreće u HR.

**Struktura jedne bilješke (predložak, ne shema)**

- 1 rečenica: što je stilski (deklarativno).
- 1 rečenica: što očekivati u čaši / dimu.
- `cigarHint`: most (wrapper/tijelo/trećina) ili svjestan kontrast; bez „must”.
- Po potrebi: aditiv u jednoj neutralnoj rečenici (već postoji `additiveDetail`).

**Ton.** Isti kao politika kataloga: unutar stila, bez kazne, bez hypea.

**Izvori**

- Vlastita degustacija i Excel MASTER kalibracija.
- Javne deklaracije destilerija / lab vrijednosti gdje postoje.
- Postojeće bogate bilješke (vino, dio ruma/cigara) kao *unutarnji* stilski uzor.

**Što ne kopirati**

- Whiskybase / Distiller / Living Cask / CA bodove i tekstove.
- Shop opise proizvoda (često marketinški i netočni za aditive).
- Automatsko generiranje istih fraza za cijeli katalog odjednom — bolje manje, bolje.

---

## 5. Urednička načela (usklađena s postojećom politikom)

1. **Deklaracija umjesto osude.** Aditiv, šećer, E150a, fortifikacija — imenovati i, gdje postoji izvor, izmjeriti. Ne „loš rum”.
2. **Ocjena i hvala unutar kategorije.** Spirit drink nije „lažni rum” u prozi; to je druga etiketa s vlastitim očekivanjem.
3. **Sve je pairable.** Tekst uči *kako birati*, ne *što zabraniti*. Kontrast je alat, ne greška.
4. **Pravila po kategoriji, jasno odvojena.** Rum ≠ whisky ≠ konjak ≠ vino — ne miješati norme u jednoj rečenici-pouci.
5. **Bonton = gostoprimstvo.** Uključiv jezik (domaćin/gost); mjera; suglasnost; bez spolnog ispita ukusa.
6. **101 = tehnika i pojmovi; bonton = odnosi; leksikon = jezik nepca.** Ne stapati u jedan „sveznajući” esej.
7. **HR iskrenost.** Referentni link ≠ košarica; `priceApprox` ostaje približno; ne obećavati zalihu.
8. **Atribucija i skromnost izvora.** Citati s napomenom „pripisano” gdje treba; ne izmišljati anegdote.
9. **Kratkoća s gustoćom.** Katalog stil 101 (odlomak + točke) ostaje default; dulji eseji samo za arhetipove večeri.
10. **Ne dirati kanonski bonton rukopis dok traje sakupljanje za grill.** Novi uvidi idu u bilješke autora, ne u tihi rewrite `bonton.json`.

---

## 6. Bonton — kutovi istraživanja (za grill notebook, ne za rewrite)

Dok autor gradi grill notebook, vrijedi skupljati *sirovinu* u slobodnoj formi (kartice, bulleti, citati s izvorom):

| Kut sakupljanja | Primjeri pitanja / bilješki |
|-----------------|-----------------------------|
| **Lokalni prostor** | Terase u HR, balkoni, kafići s dozvolom, „gdje dim smeta a nije zabranjen” |
| **Nuditi u praksi** | Što ljudi stvarno kažu kad nude; kako objasniti duljinu dima bez pedanterije |
| **Piće i pritisak** | Kada „još jedna” postaje neugodna; kako domaćin spusti ljestvicu |
| **Spol / inkluzija** | Fraze koje zastarijevaju; kako držati ton gospodstva bez isključivanja |
| **Greške za stolom** | Canoeing, krivi rez, preljev — što se smije šaliti, što ne |
| **Poklon** | Što je u HR lako nabaviti kao dar bez snobizma |
| **Paralelni žanrovi** | Struktura klasičnih knjiga bontona (poglavlja, precepti) — **oblika**, ne teksta |
| **Suprotni glasovi** | Situacije gdje „pravila” smetaju gostoljubivosti — za kasniju napetost u knjizi |

**Namjerno izvan opsega sada:** nova poglavlja, EN sync rewrite, dulji esejistički bonton u appu.

---

## 7. Otvorena urednička pitanja (za ljudskog autora)

1. Je li **leksikon** zaseban Club sloj (poput 101/bontona) ili proširenje trake „Savjeti” / nova traka „Jezik”?
2. Koliki je **kanonski jezik** za nove tekstove — samo HR pa EN kasnije, ili odmah dvojezično kao 101?
3. Za **HR vodič**: imenovati konkretne trgovine u prozi (kao sad u podacima) ili govoriti tipovima („specijalizirana žestoka”, „vinoteka”) da se izbjegne brzo zastarijevanje?
4. Prioritet **vala C**: prvo rum (politika aditiva) ili whisky (najviše heuristike)?
5. Smiju li **večernji arhetipovi** imenovati konkretne boce/cigare iz kataloga ili ostati na stilovima (maduro × tawny) radi dugovječnosti?
6. Za grill notebook bontona: skuplja li se i **usmeno** (prijatelji, večeri) ili samo literatura / vlastita praksa?
7. Treba li kviz ostati „tvrd” (norme, brojke) ili smije ući i „meki” bonton (jedan točan odgovor o ljubaznosti)?
8. Gin/kava: ciljaju li **jutarnji / aperitivni** pairing kao ravnopravan stup, ili ostaju rubni uz brandy/vino?

---

## 8. Što ovaj memo namjerno ne radi

- Ne predlaže implementaciju ekrana, shema ili pipelinea.
- Ne prepisuje *Malu knjigu pušačkog bontona*.
- Ne nalaže brisanje heurističkih profila — samo urednički prioritet bogatijih bilješki.
- Ne uvodi affiliate strategiju; shop linkovi ostaju korisni i transparentni kad već postoje.

---

*Kraj mema. Sljedeći korak nakon autorova odabira inicijativa: tanki content-spec po odabranoj inicijativi (A/B/C), zatim pisanje — i dalje bez miješanja s inženjerskim planom osim ako autor eksplicitno zatraži.*
