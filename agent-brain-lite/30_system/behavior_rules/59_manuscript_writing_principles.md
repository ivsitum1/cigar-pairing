# Principi AI-potpomognutog pisanja rukopisa

**Version:** 1.0  
**Author:** Ivan Šitum  
**Last updated:** 2026-06-28  
**Scope:** Konceptualne upute za bilo koji AI sustav koji sudjeluje u izradi akademskih dokumenata. Agnostične na alat (Cursor, Claude, Copilot, bilo što).

**Operativni sloj (implementacija):** `58_manuscript_agent_protocol.md` — derivira iz ovih principa, ne obrnuto.

---

## 1. JEDAN IZVOR ISTINE

Rukopis ima jedan kanonski fajl. Sve ostalo je derivat.

Svaka informacija — broj pacijenata, statistički rezultat, redoslijed autora, izjava o sukobu interesa — postoji na **jednom mjestu** u tom fajlu. Kad se pojavi drugdje (abstract, tablica, prevedeni sažetak, supplementary materijal), to je **referenca na izvor**, ne neovisna kopija. Ako se izvor promijeni, svi derivati se ažuriraju u istoj operaciji.

Praktična posljedica: ne postoji "odvojeni abstract", "odvojeni QA log", "odvojene reference" koje žive samostalno. Postoji rukopis i, eventualno, supplement koji je eksplicitno vezan na verziju rukopisa. Sve interno ostaje interno.

**Test:** ako izbrišeš sve osim jednog fajla, možeš li rekonstruirati cijeli submission? Ako da — imaš jedan izvor istine. Ako ne — imaš rasuti sustav koji će divergirati.

---

## 2. OPERACIJE SU ATOMSKE

Editiranje rukopisa nije niz odvojenih mikro-operacija s backupom između svake. To je **jedna transakcija**: pročitaj, identificiraj sve potrebne promjene, primijeni ih, producaj jedan output.

Backup nije verzioniranje. Backup je strah od vlastite greške materijaliziran kao fajl. Git je verzioniranje. Conversation history je verzioniranje. `_pre_ref_fix.docx` nije ni jedno ni drugo — to je entropija.

**Princip:** agent koji mora napraviti 8 izmjena na rukopisu radi jednu editing sesiju koja producira jedan fajl, ne 8 sesija s 8 međufajlova. Ako je nesiguran u neku izmjenu, traži potvrdu od korisnika PRIJE nego napravi fajl, ne NAKON što napravi backup.

---

## 3. QA JE PROCES, NE ARTEFAKT

Provjera konzistentnosti, verifikacija brojeva, audit missing data — to su **koraci u procesu pisanja**, ne samostalni dokumenti. Agent koji producira `verification_audit_v2.csv` s 2 reda podataka nije napravio QA — napravio je fajl koji nitko neće čitati.

QA se izvršava u radnom procesu i rezultat se komunicira korisniku u razgovoru:

- "Provjerio sam: N=59 u svim tablicama, abstractu, i Results sekciji — konzistentno."
- "UPOZORENJE: Table 1 kaže N=59, ali QA audit koristi N=90. Razjasni prije nastavka."

Ako QA otkrije problem, output se ne generira dok se problem ne riješi. QA koji producira fajl i onda nastavlja dalje nije QA — to je dokumentiranje vlastite greške za buduće arheologe.

---

## 4. DERIVATI SE GENERIRAJU, NE ODRŽAVAJU

Prevedeni abstract, STROBE checklist, reference u drugom formatu — sve to su **derivati** koji se mogu automatski generirati iz kanonskog rukopisa. Ne održavaju se paralelno.

Kad agent napravi rumunjski abstract kao odvojeni `.md` fajl, stvorio je **drugu kopiju podataka** koja će neizbježno divergirati od izvora. Kad se promijeni rezultat u engleskom abstractu, rumunjski ostaje star. Kad se promijeni N, rumunjski kaže stari N.

**Princip:** derivat se generira na zahtjev iz aktualnog izvora, ili se ugrađuje u kanonski fajl. Nikad ne živi odvojeno kao fajl koji se "održava".

---

## 5. VERZIJA JE MILESTONE, NE CHECKPOINT

Verzija postoji kad se **nešto smisleno promijenilo** — struktura, sadržaj, analiza. Ispravak tipfelera, reformat referenci, dodavanje jedne rečenice u Discussion — to nije nova verzija, to je edit unutar iste verzije.

Korisna verzija: `v1.0` → `v2.0` (dodan Bayesian sensitivity analysis, proširena Discussion, dodano 15 referenci).

Beskorisna verzija: `_pre_ref_fix` → `_pre_sync` → `_pre_missing_data` → `_pre_methods_sync` → `_pre_no_missing_text` → `_pre_verified_refs` (6 fajlova koji se razlikuju za 4-136 redaka).

**Test:** može li korisnik za svaku verziju reći **zašto postoji** u jednoj rečenici koja počinje s "Zato što..."? Ako ne — to nije verzija, to je nered.

---

## 6. KONTEKST SE PROVJERAVA, NE PRETPOSTAVLJA

Kad agent nastavlja rad na rukopisu iz prethodne sesije, ne smije pretpostaviti da je prethodno stanje točno. Memorija prethodne sesije kaže "reference verified" — ali jedini izvor istine je **fajl sam po sebi**. Agent čita aktualni fajl, provjerava stanje, i tek onda radi.

Ovo je posebno važno za brojeve. Ako agent "zna" da je N=59, ali QA artifact kaže N=90, agent ne smije nastaviti dok se diskrepancija ne razriješi. "Prošla sesija je ovo riješila" nije prihvatljiv argument jer prošla sesija može biti izvor greške.

**Princip:** svaki put kad se otvori rukopis za rad, agent obavlja minimalni integrity check:

- N konzistentan kroz abstract, text, tablice, supplemente
- Declarations headeri odgovaraju sadržaju
- Abstract brojevi odgovaraju Results brojevima
- Reference count je razuman za tip članka

---

## 7. FORMA SLIJEDI SADRŽAJ, NE OBRNUTO

AI sustavi imaju tendenciju producirati dokumente koji izgledaju ispravno ali su sadržajno prazni ili redundantni. Tablica koja ponavlja tekst. Discussion od 3 rečenice za studiju s 10 metodoloških izazova. Reference list od 7 stavki za temu s 200 relevantnih publikacija.

**Princip:** agent procjenjuje **proporcionalnost** — koliko prostora zaslužuje svaka sekcija s obzirom na kompleksnost onoga što treba reći, ne s obzirom na to koliko prostora je "uobičajeno".

Skeletni Discussion nije kratak — on je nepotpun. Tablica koja replicira prethodne paragrafe nije informativna — ona je redundantna. 7 referenci za temu koja zahtijeva 30 nije koncizan — to je nedovoljno.

---

## 8. GREŠKA SE KORIGIRA NA IZVORU, NE DODAVANJEM SLOJA

Kad se pronađe greška u rukopisu (krivi redoslijed Declarations, permutiran abstract, nekonzistentan N), ispravak se radi **na originalnom mjestu greške**, ne dodavanjem novog fajla koji "popravlja" prethodni.

Sustav koji na grešku reagira s "napravit ću novi fajl s popravkom" akumulira slojeve. Sustav koji reagira s "popravit ću grešku u originalnom fajlu" konvergira prema ispravnom stanju.

---

## 9. TRANSPARENTNOST NEIZVJESNOSTI

Agent koji ne zna nešto — recimo, je li referenca točna, odgovara li MIC vrijednost aktualnom izolatu, ili je li NI margina klinički opravdana — mora to **eksplicitno reći**, ne zaobići šutnjom ili pretpostavkom.

"Ne mogu verificirati referencu 14 bez pristupa PubMedu — označi za ručnu provjeru" je korisno.  
Tiho generiranje reference koja izgleda ispravno ali nije provjerena je štetno.

Isto vrijedi za statističke odluke. Ako agent odabere prior, marginu, ili prag — obrazlaže zašto. Ako ne zna koji je pravi — kaže da ne zna i nudi opcije.

---

## 10. SUSTAV OTPORAN NA AKUMULACIJU

Svaki puta kad agent dodaje fajl, treba se pitati: hoće li ovaj fajl još biti relevantan za 2 iteracije? Ako ne — ne bi trebao postojati kao fajl.

QA logovi, intermediate backupi, separate abstracts, audit CSV-ovi — ništa od toga ne preživljava drugu iteraciju. Za 3 sesije, korisnik ima 30 fajlova i ne zna koji je aktualan.

**Princip otpornosti:** nakon N iteracija, broj fajlova u outputu treba biti **konstantan ili opadajući**, ne rastući. Ako svaka sesija dodaje fajlove bez brisanja starih, sustav divergira.

**Test entropije:** ako korisnik uploada sve fajlove iz prethodnih sesija i pita "koji je konačni rukopis?" — odgovor mora biti trivijalan. Ako zahtijeva forenziku, sustav je zakazao.

---

## Mapiranje na implementaciju

| Princip | Operativni sloj (`58`) | Cursor rule / skill |
|---------|------------------------|---------------------|
| 1 Jedan izvor istine | Part 1, Part 2.3 (abstract numbers) | `writing-manuscript-structure.mdc`, `writing-manuscript-files.mdc` |
| 2 Operacije atomske | Part 1.5 | `writing-manuscript-files.mdc`, Step 1 skill |
| 3 QA je proces | Part 5 + output gate | `SKILL_manuscript-writing` Step 6; chat only |
| 4 Derivati generirani | Part 1.3–1.4 | `writing-manuscript-files.mdc` |
| 5 Verzija = milestone | Part 1.2 | `{name}_v{M}.{m}` naming |
| 6 Kontekst provjeren | Part 6 | Skill Step 0 integrity check |
| 7 Forma slijedi sadržaj | Part 3.4–3.6 | `writing-paper-style.mdc` |
| 8 Greška na izvoru | Part 1.5 | `writing-manuscript-files.mdc` |
| 9 Transparentnost | Part 4, honesty | `[TO_CONFIRM]` in skill |
| 10 Otpornost akumulaciji | Part 1.3, Part 5.3 | Entropy test before deliverable |

---

## Related

- `58_manuscript_agent_protocol.md` — operational protocol (EN)
- `.cursor/rules/writing-manuscript-principles.mdc` — thin Tier 1 slice
- `SKILL_manuscript-writing.md` — end-to-end workflow

*Specifična implementacija (naming convention, checklist items, section order) derivira iz principa, ne obrnuto.*
