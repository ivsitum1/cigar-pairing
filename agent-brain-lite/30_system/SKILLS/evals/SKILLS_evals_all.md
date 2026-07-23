# SKILLS Eval Cases — Ivan Šitum Cursor Workspace

**Version:** 1.1  
**Last updated:** 2026-03-14

<!-- Koristi za kreiranje/ažuriranje 30_system/SKILLS/evals/<skill_id>.json -->
<!-- Svaki case testira PRIMJENU skilla, ne znanje o skillu -->
<!-- Svaki case: description + input + assertions (contains, not_contains, regex_match, word_count_below, last_sentence_not_question) -->

---

## ai-detection

### Case 1 — Happy path: AI-heavy tekst, revizija za snižavanje scorea
**Input:**
Revidiraj sljedeći paragraf da sniziš AI detection score (GPTZero/Originality). Tekst mora ostati medicinski točan.
> "It is worth noting that the administration of vasopressors in septic shock represents a cornerstone of hemodynamic management. Furthermore, it is important to consider that norepinephrine is generally considered the first-line agent. In conclusion, clinicians should be aware of the potential adverse effects."

**Assertions:**
- `regex_match`: "(?i)norepinephr(in|ine)" — termin ostaje (medicinska točnost; prihvaća norepinephrin i norepinephrine)
- `not_contains`: "It is worth noting"
- `not_contains`: "Furthermore"
- `not_contains`: "In conclusion"
- `not_contains`: "it is important to consider"
- `last_sentence_not_question`

---

### Case 2 — Edge: Tekst koji je već stilski prirodan, minimalna intervencija
**Input:**
Provjeri AI score i revidiraj samo dijelove s visokim AI markerima:
> "Norepinephrin ostaje lijek prvog izbora u septičnom šoku prema Surviving Sepsis Guidelines 2021. Ciljana vrijednost MAP ≥65 mmHg postiže se titriranjem doze između 0.01–3.3 mcg/kg/min. Nismo opservirali statistički značajnu razliku u 28-dnevnom mortalitetu između skupina (p=0.34)."

**Assertions:**
- `regex_match`: "nizak|minimalne izmjene|prirodan stil|low score|malo AI markera"
- `not_contains`: "It is worth noting" — ne dodaje AI fraze revizijom
- `not_contains`: "Furthermore"
- `word_count_below`: 400

---

### Case 3 — Negativni: Identifikacija svih markera u tekstu punom AI signatura
**Input:**
Identificiraj sve AI formulacije i predloži konkretne zamjene za svaku:
> "Certainly, it is evident that this groundbreaking study delves into the intricate complexities of perioperative fluid management. Importantly, the findings underscore the necessity of a nuanced approach. It should be noted that the authors navigate these challenges with commendable rigor. In summary, this research paves the way for future investigations."

**Assertions:**
- `contains`: "delve" OR `regex_match`: "delves?.{0,50}marker|delves?.{0,50}AI" — identificiran
- `contains`: "groundbreaking" — identificiran
- `contains`: "paves the way" OR `contains`: "pave the way" — identificiran
- `contains`: "Certainly" — identificiran
- `not_contains`: "tekst je prihvatljiv" OR `not_contains`: "nema AI markera"
- `regex_match`: "zamjen|alternativ|umjesto|replace|revid"

---

## avoid-ai-formulations

### Case 1 — Happy path: Revizija apstrakta s AI frazama
**Input:**
Revidiraj ovaj sažetak eliminirajući AI formulacije. Zadržaj medicinsku točnost i akademski ton.
> "This study aims to delve into the effectiveness of high-flow nasal cannula therapy. It is worth noting that HFNC has gained significant traction in recent years. Furthermore, our findings underscore the importance of early intervention. In conclusion, HFNC represents a promising approach that warrants further investigation."

**Assertions:**
- `not_contains`: "delve"
- `not_contains`: "It is worth noting"
- `not_contains`: "underscore"
- `not_contains`: "warrants further investigation"
- `not_contains`: "In conclusion"
- `contains`: "HFNC" — termin ostaje
- `last_sentence_not_question`

---

### Case 2 — Strategy: Lista zabranjenih fraza s alternativama za uvod medicinskog članka
**Input:**
Daj mi konkretne strategije i listu fraza koje treba izbjegavati pri pisanju uvoda medicinskog članka, s konkretnim alternativama za svaku zabranjenu frazu.

**Assertions:**
- `regex_match`: "delve|worth noting|underscore|pave the way|navigate" — navedeni kao primjeri koje treba izbjegavati
- `regex_match`: "umjesto|instead|zamijeni|replace|alternativ"
- `contains`: "aktivan glagol" OR `contains`: "active verb" OR `regex_match`: "aktivn.{0,50}glagol" — strategija
- `not_contains`: "nije moguće"
- `word_count_below`: 600

---

### Case 3 — Edge: Revizija diskusije — ukloni AI fraze ali zadrži legitimnu akademsku terminologiju
**Input:**
Revidiraj diskusiju, ukloni AI fraze, ali NE briši standardne akademske izraze kao "statistically significant", "95% confidence interval" ili "p-value". Razlikuj AI fraze od legitimne terminologije.
> "These groundbreaking results certainly demonstrate that, importantly, our intervention paves the way for future research. The data shows a statistically significant reduction (p=0.02, 95% CI 0.45–0.89) in 30-day mortality."

**Assertions:**
- `not_contains`: "groundbreaking"
- `not_contains`: "certainly"
- `not_contains`: "paves the way"
- `contains`: "statistically significant" — legitimni termin ostaje
- `contains`: "95% CI" OR `contains`: "confidence interval" — ostaje
- `contains`: "p=0.02" — numerički podaci ostaju

---

## bayesian-workflow

### Case 1 — Happy path: Binarni ishod, uninformativni prior, kompletan R kod
**Input:**
Provedi potpuni Bayesov workflow: binarni ishod (30-dnevni mortalitet), tretman vs. kontrola: 45/200 vs. 30/200. Uninformativni prior. Napiši kompletan R kod s brms: prior specification, prior predictive check, model fitting, MCMC dijagnostika, posterior summary.

**Assertions:**
- `contains`: "brms"
- `contains`: "prior(" OR `contains`: "prior_summary"
- `contains`: "pp_check" OR `contains`: "prior_predictive"
- `contains`: "Rhat"
- `contains`: "ESS" OR `contains`: "ess_bulk"
- `regex_match`: "brm\s*\("
- `not_contains`: "glm(" — ne samo frequentist alternativa

---

### Case 2 — Edge: Informativni prior iz prethodne meta-analize
**Input:**
Isti scenarij (binarni ishod, 45/200 vs 30/200), ali s informativnim priorom iz meta-analize: pooled OR=0.75, 95% CI 0.60–0.94. Specificiraj prior u brms i prikaži usporedbu posteriornih distribucija s uninformativnim priorom (sensitivity analysis).

**Assertions:**
- `contains`: "prior("
- `contains`: "normal(" OR `contains`: "lognormal("
- `contains`: "prior predictive" OR `contains`: "prior_predictive"
- `contains`: "sensitivity" OR `contains`: "osjetljivost" OR `contains`: "usporedba priora"
- `not_contains`: "flat prior" OR `not_contains`: "uninformative prior" — ne ignorira zadani informativni prior
- `regex_match`: "0\.75|log\(0\.75\)|log.*0\.75"

---

### Case 3 — Dijagnostika: Loša konvergencija, akcijski plan
**Input:**
Interpretiraj MCMC dijagnostiku i predloži konkretne korake korekcije: Rhat=1.18 za sve parametre, ESS_bulk=95, ESS_tail=80, trace plotovi pokazuju loš mixing između 4 chaina.

**Assertions:**
- `contains`: "konvergencij" OR `contains`: "convergence" — problem identificiran
- `not_contains`: "prihvatljiv" OR `not_contains`: "zadovoljavajuć" — Rhat=1.18 NIJE prihvatljiv
- `contains`: "iter" OR `contains`: "warmup" OR `contains`: "iteracij" — povećanje iteracija
- `contains`: "adapt_delta" OR `contains`: "max_treedepth" OR `contains`: "thin" — tuning parametri
- `regex_match`: "Rhat.{0,80}1\.0[0-9]|granica|threshold|<\s*1\.0[0-9]"
- `last_sentence_not_question`

---

### Case 4 — Izvještaj: Posterior summary za sekciju Results
**Input:**
Na temelju posteriornih distribucija: OR=0.68 (95% CrI: 0.51–0.89), P(OR<1)=0.97, P(OR<0.5)=0.08. Napiši klinički interpretabilan posterior summary za Results sekciju medicinskog članka. Bez R koda, bez formula.

**Assertions:**
- `contains`: "0.68" AND `contains`: "OR"
- `contains`: "credible interval" OR `contains`: "CrI" OR `contains`: "wjerodostojni interval"
- `contains`: "0.97" OR `contains`: "97%" — P(OR<1)
- `not_contains`: "p-value" OR `not_contains`: "p-vrijednost" — Bayesov, ne frequentist jezik
- `not_contains`: "statistički značajno" — Bayesova interpretacija, ne NHST
- `word_count_below`: 300
- `last_sentence_not_question`

---

## consort-checklist

### Case 1 — Happy path: Methods sekcija s nedostajućim elementima
**Input:**
Provjeri CONSORT 2010 usklađenost i navedi koje su stavke nedostajuće ili nepotpune:
> "Patients were randomized 1:1 to TIVA or sevoflurane. Randomization was performed using a computer-generated list. Both patients and surgeons were blinded to group allocation. Primary endpoint was QoR-40 at 24h. We enrolled 120 patients between January and December 2023."

**Assertions:**
- `contains`: "allocation concealment" — nije opisan, mora biti označeno
- `regex_match`: "1b|sequence generation|item [0-9]" — CONSORT item reference
- `not_contains`: "sve stavke su prisutne" OR `not_contains`: "zadovoljava sve" — nedostaju elementi
- `contains`: "CONSORT" — eksplicitno referenciranje
- `regex_match`: "nedostaje|nije naveden|missing|incomplete|nepotpun"
- `last_sentence_not_question`

---

### Case 2 — Edge: Open-label RCT, zasljepljenje nije moguće
**Input:**
Evaluiraj CONSORT usklađenost za open-label RCT (kirurška intervencija vs. konzervativno liječenje) gdje zasljepljenje pacijenata nije moguće. Koje CONSORT stavke su primjenjive, a koje nisu? S obrazloženjem.

**Assertions:**
- `contains`: "open-label" — prepoznaje prirodu studije
- `contains`: "performance bias" OR `contains`: "detection bias" — relevantni rizici pristranosti
- `contains`: "assessor" OR `contains`: "outcome assessor" — zasljepljenje procjenitelja kao alternativa
- `not_contains`: "blinding je obavezan" OR `not_contains`: "studija ne zadovoljava" — razumije iznimku
- `regex_match`: "primjenjiv|applicable|nije primjenjiv|not applicable|modific"

---

### Case 3 — Negativni: "Fully CONSORT compliant" tvrdnja bez dokaza
**Input:**
Ocijeni CONSORT usklađenost: studija prijavljuje CONSORT flow dijagram, ITT analizu, p-vrijednosti, demografske tablice, broj izgubljenih iz praćenja. Autori tvrde da je studija "fully CONSORT compliant."

**Assertions:**
- `not_contains`: "fully compliant" OR `not_contains`: "u potpunosti zadovoljava" — bez kompletne provjere ne može se tvrditi
- `contains`: "protokol" OR `contains`: "protocol registration" OR `contains`: "PROSPERO" OR `contains`: "ClinicalTrials" — česta nedostatak
- `contains`: "sample size" OR `contains`: "veličina uzorka" — kalkulacija uzorka česta nedostatak
- `regex_match`: "nije dostatan|insufficient|nedovoljan|incomplete|nepotpun|provjerit"

---

## document-conversion

### Case 1 — Happy path: Docx u Markdown s očuvanjem strukture
**Input:**
Konvertiraj ovaj Word sadržaj u Markdown, čuvajući naslove (H1, H2), tablice i bold tekst:
```
Naslov studije

Uvod
Ova studija ispituje...

Metode
| Varijabla | Vrijednost |
|---|---|
| n | 120 |
```

**Assertions:**
- `regex_match`: "^#\s+Naslov|^##\s+Naslov" — H1/H2 header
- `contains`: "## Uvod" OR `contains`: "# Uvod" — section header
- `contains`: "| Varijabla | Vrijednost |" — tablica u MD formatu
- `regex_match`: "\|---\||\|:---\|" — separator retka tablice
- `not_contains`: "<table>" — nije HTML format
- `last_sentence_not_question`

---

### Case 2 — Edge: CSV u formatiranu Markdown tablicu
**Input:**
Pretvori ovaj CSV u formatiranu Markdown tablicu:
```
group,n,mean_age,sd_age,mortality_30d
HFNC,45,67.3,12.1,8
NIV,43,68.9,11.7,12
```

**Assertions:**
- `contains`: "| group |" OR `contains`: "| Group |"
- `contains`: "| HFNC |"
- `contains`: "| NIV |"
- `regex_match`: "\|\s*67\.3\s*\|"
- `not_contains`: "group,n,mean_age" — nije ostalo u CSV formatu
- `regex_match`: "\|---\||\|:---\|" — separator prisutan

---

### Case 3 — Negativni: Konverzija u plain text s upozorenjem na gubitak
**Input:**
Konvertiraj ovaj dokument u plain text (.txt), ali upozori na sve elemente koji će se izgubiti. Dokument sadrži: matematičke formule (∑x²/n), tablice, bold/italic, reference [1], header s paginacijom.

**Assertions:**
- `contains`: "formula" OR `contains`: "matematičk" OR `contains`: "∑" — gubitak formula identificiran
- `contains`: "tablica" OR `contains`: "table" — gubitak tablice
- `contains`: "bold" OR `contains`: "italic" OR `contains`: "formatiranje" — gubitak formatiranja
- `not_contains`: "bez gubitka" OR `not_contains`: "bez promjena" — konverzija nije bezgubitna
- `regex_match`: "upozorenje|warning|izgub|loss|neće biti sačuvan"

---

## figure-pipeline

### Case 1 — Happy path: Forest + PRISMA flow, publikacijska kvaliteta
**Input:**
Kreiraj R pipeline za generiranje dviju publikacijskih figura: (1) forest plot meta-analize s 8 studija, (2) PRISMA 2020 flow dijagram. Output: PDF, 300 DPI, font Times New Roman. Organiziraj pipeline u funkcije s jasnim inputima.

**Assertions:**
- `contains`: "forest" OR `contains`: "forest_plot"
- `contains`: "PRISMA" OR `contains`: "prisma"
- `contains`: "pdf(" OR `contains`: "ggsave(" OR `contains`: "cairo_pdf"
- `contains`: "300" AND `regex_match`: "dpi|DPI|res\s*="
- `contains`: "Times New Roman" OR `contains`: "serif"
- `regex_match`: "library\s*\(\s*['\"]?(forestplot|meta|ggplot2|metafor)"

---

### Case 2 — Edge: CONSORT flow dijagram s kompleksnom randomizacijom
**Input:**
Generiraj R kod za CONSORT 2010 flow dijagram: screenirano 450, isključeno 230 (ineligible 180, odbili 50), randomizirano 220, TIVA n=110 (izgubljeni iz praćenja: 5), Sevo n=110 (izgubljeni: 8), ITT analiza: TIVA n=105, Sevo n=102.

**Assertions:**
- `contains`: "450" — screened
- `contains`: "220" — randomized
- `regex_match`: "105|102" — ITT brojevi
- `contains`: "DiagrammeR" OR `contains`: "Gmisc" OR `contains`: "consort" OR `contains`: "ggflowchart" — paket
- `not_contains`: "PRISMA" — ovo je CONSORT, ne PRISMA
- `regex_match`: "izgubljen|lost.{0,30}follow|withdraw|excluded"

---

### Case 3 — Negativni: Zahtjev za forest plot pri I²=94%
**Input:**
Generiraj forest plot pipeline, ali imam samo 3 studije i heterogenost je I²=94%.

**Assertions:**
- `contains`: "I²" OR `contains`: "heterogenost" — problem identificiran
- `contains`: "94%" OR `contains`: "visoka" — visoka heterogenost
- `not_contains`: "random effects" kao jedino rješenje bez upozorenja
- `contains`: "pooling" OR `contains`: "meta-analiza" — upitnost poolinga
- `regex_match`: "upozorenje|caution|ograničenje|limitation|subgroup|ne preporuč"
- `last_sentence_not_question`

---

## forest-plot

### Case 1 — Happy path: Standardni forest plot, 6 studija, OR
**Input:**
Napiši R kod za forest plot meta-analize (OR, 95% CI):
Study1: OR=0.72, CI=0.51–1.02, w=18%
Study2: OR=0.68, CI=0.48–0.96, w=22%
Study3: OR=0.81, CI=0.60–1.09, w=20%
Study4: OR=0.55, CI=0.38–0.80, w=15%
Study5: OR=0.74, CI=0.52–1.05, w=13%
Study6: OR=0.69, CI=0.49–0.97, w=12%
Pooled (RE): OR=0.70, CI=0.60–0.82, I²=12%

**Assertions:**
- `contains`: "metafor" OR `contains`: "meta" OR `contains`: "forestplot" — paket
- `regex_match`: "OR|odds.ratio|log.*OR"
- `contains`: "I²" OR `contains`: "I2" OR `contains`: "heterogen"
- `regex_match`: "diamond|pooled|summary|polygon" — prikaz pooled estimata
- `not_contains`: "lm(" OR `not_contains`: "t.test(" — pogrešne funkcije
- `regex_match`: "library\s*\("

---

### Case 2 — Edge: Kontinuirana mjera (MD), ne binarni ishod
**Input:**
Forest plot za 5 studija, mean difference u QoR-40 score (kontinuirani outcome):
StudyA: MD=8.2, CI=3.1–13.3
StudyB: MD=6.5, CI=1.8–11.2
StudyC: MD=10.1, CI=4.7–15.5
StudyD: MD=5.8, CI=0.9–10.7
StudyE: MD=7.4, CI=2.2–12.6

**Assertions:**
- `contains`: "MD" OR `contains`: "mean difference"
- `not_contains`: "OR" OR `not_contains`: "odds ratio" — nije binarni ishod
- `not_contains`: "log(" — ne logaritmira MD
- `regex_match`: "yi\s*=|TE\s*=|measure\s*=\s*['\"]MD|metacont|metagen"
- `regex_match`: "rma\s*\(|metacont\s*\(|metagen\s*\("

---

### Case 3 — Negativni: k=2 studije, upozorenje
**Input:**
Napravi forest plot za meta-analizu s 2 studije.

**Assertions:**
- `contains`: "2" OR `contains`: "dvije studije" — prepoznaje mali broj
- `contains`: "upozorenje" OR `contains`: "caution" OR `contains`: "ograničenje"
- `not_contains`: "I²" — s 2 studije heterogenost nije interpretabilna
- `regex_match`: "minimalan|insufficient|nije preporučeno|not recommended|premalo|k\s*<\s*[345]"
- `last_sentence_not_question`

---

## grade-assessment

### Case 1 — Happy path: Primarni ishod RCT-a, procjena sigurnosti
**Input:**
Provedi GRADE procjenu za ishod 30-dnevni mortalitet: 2 RCT-a (n=430, n=280), RoB low, konzistentnost I²=18%, direktnost direktna, preciznost 95% CI 0.55–0.98, nema sumnje na publication bias.

**Assertions:**
- `contains`: "high" OR `contains`: "visoka" OR `regex_match`: "⊕⊕⊕⊕" — RCT = high kao polazna razina
- `contains`: "risk of bias" OR `contains`: "pristranost"
- `contains`: "I²" OR `contains`: "konzistentnost"
- `contains`: "preciznost" OR `contains`: "precision"
- `regex_match`: "⊕|GRADE|razina|certainty|quality of evidence"
- `not_contains`: "niska sigurnost" OR `not_contains`: "low certainty" — bez razloga za downgrade
- `last_sentence_not_question`

---

### Case 2 — Edge: Downgrade zbog višestrukih ograničenja
**Input:**
GRADE procjena za isti tip ishoda, ali: opservacijska studija, RoB visok (confounding bez adjustment), konzistentnost I²=62%, preciznost CI=0.31–1.89 (prelazi null vrijednost, široki CI), indirektnost postoji (surrogate outcome).

**Assertions:**
- `regex_match`: "⊕⊕○○|⊕○○○|low|very low|niska|vrlo niska" — niska ili vrlo niska
- `contains`: "opservacijska" OR `contains`: "observational" — niža polazna razina
- `contains`: "wide CI" OR `contains`: "preciznost" OR `contains`: "CI prelazi"
- `contains`: "downgrade" OR `contains`: "sniženo" OR `contains`: "degradiran"
- `not_contains`: "high certainty" OR `not_contains`: "visoka sigurnost"

---

### Case 3 — Multi-outcome: Tri ishoda s različitim razinama
**Input:**
GRADE procjena za 3 ishoda:
(1) mortalitet: 2 RCT, I²=8%, low RoB, CI=0.55–0.89
(2) ICU LOS: 1 RCT, I²=N/A, high RoB
(3) adverse events: samo case reports
Prezentiraj kao GRADE sažetnu tablicu.

**Assertions:**
- `contains`: "mortalitet" OR `contains`: "mortality"
- `contains`: "ICU" OR `contains`: "LOS"
- `contains`: "adverse" OR `contains`: "nuspojave"
- `regex_match`: "tablica|table|GRADE table|sažetna"
- `regex_match`: "⊕⊕⊕⊕|⊕⊕⊕○|⊕⊕○○|⊕○○○" — GRADE simboli
- `not_contains`: "svi ishodi imaju jednaku razinu" — 3 ishoda moraju imati različite razine

---

## manuscript-structure

### Case 1 — Happy path: IMRaD provjera s identificiranim propustima
**Input:**
Provjeri IMRaD strukturu: dokument ima sekcije "Uvod", "Metode", "Rezultati", "Rasprava". Uvod nema jasno postavljenu hipotezu. Rasprava nema sekciju ograničenja. Abstract ima 320 riječi. Provjeri usklađenost.

**Assertions:**
- `contains`: "hipoteza" OR `contains`: "research question" — nedostaje, mora biti označeno
- `contains`: "ograničenja" OR `contains`: "limitations" — nedostaje u raspravi
- `regex_match`: "320.{0,30}rije|word.{0,30}limit|predug|exceeds|abstract"
- `not_contains`: "struktura je ispravna" OR `not_contains`: "zadovoljava sve zahtjeve"
- `regex_match`: "nedostaje|nije naveden|missing|incomplete"
- `last_sentence_not_question`

---

### Case 2 — Edge: Methods sekcija bez statističke analize
**Input:**
Evaluiraj ovu Methods sekciju: opisana randomizacija, inkluzijski/ekskluzijski kriteriji, intervencija, follow-up. Statistička analiza nije navedena kao zasebna podsekcija. Software nije specificiran.

**Assertions:**
- `contains`: "statistička analiza" OR `contains`: "statistical analysis" — nedostaje
- `contains`: "software" OR `contains`: "verzija" OR `contains`: "version" — mora biti naveden
- `not_contains`: "metode su kompletne" — nedostaje statistička sekcija
- `regex_match`: "nedostaje|missing|nije naveden|not reported|dodati"

---

### Case 3 — Negativni: Nema etike, pristanka i registracije
**Input:**
Provjeri rukopis: Introduction, Methods (randomizacija, intervencija), Results, Discussion, References. Nema: ethics approval, informed consent statement, trial registration number.

**Assertions:**
- `contains`: "etič" OR `contains`: "ethics" OR `contains`: "IRB" OR `contains`: "ethics approval"
- `contains`: "pristanak" OR `contains`: "informed consent"
- `contains`: "registracija" OR `contains`: "registration" OR `contains`: "ClinicalTrials" OR `contains`: "PROSPERO"
- `not_contains`: "rukopis je kompletan" OR `not_contains`: "sve sekcije su prisutne"
- `regex_match`: "nedostaje|missing|obavezan|required|mora biti naveden"

---

## meta-analysis

### Case 1 — Happy path: Pooled OR, random effects, 6 studija, R kod
**Input:**
Provedi meta-analizu (binarni ishod, 30-dnevni mortalitet). Podaci (events/n tratman vs. kontrola):
Study1: 45/200 vs 60/200 | Study2: 30/150 vs 42/150 | Study3: 18/100 vs 28/100
Study4: 55/220 vs 70/220 | Study5: 12/80 vs 20/80  | Study6: 22/110 vs 31/110
R kod s metafor paketom, random effects model (REML), pooled OR i heterogenost.

**Assertions:**
- `contains`: "metafor" OR `contains`: "library(meta"
- `contains`: "rma(" OR `contains`: "metabin("
- `contains`: "REML" OR `contains`: "random"
- `contains`: "I²" OR `contains`: "I2"
- `regex_match`: "escalc\s*\(|measure\s*=\s*['\"]OR|OR"
- `not_contains`: "lm(" — pogrešan pristup

---

### Case 2 — Edge: Visoka heterogenost, subgroup analiza i meta-regresija
**Input:**
Meta-analiza pokazuje I²=78% (p<0.001). Dostupni moderatori: tip intervencije (A vs B), setting (ICU vs non-ICU), doza (visoka vs niska). Napiši R kod za subgroup analizu i meta-regresiju.

**Assertions:**
- `contains`: "subgroup" OR `contains`: "podgrupa"
- `contains`: "metareg(" OR `contains`: "meta-regresija"
- `contains`: "moderator" OR `contains`: "moderato"
- `not_contains`: "I²=78% je prihvatljiv" — nije prihvatljivo bez obrazloženja
- `regex_match`: "metareg\s*\(|rma\s*\(.{0,100}mods\s*="
- `last_sentence_not_question`

---

### Case 3 — Negativni: Direktno poolanje OR i HR bez transformacije
**Input:**
U meta-analizi 4 studije prijavljuju OR a 3 studije prijavljuju HR za isti ishod (mortalitet). Mogu li ih direktno poolati u jednu meta-analizu?

**Assertions:**
- `contains`: "ne" OR `contains`: "nije preporučeno" OR `contains`: "nije ispravno"
- `contains`: "HR" AND `contains`: "OR" — oba tipa effect measure navedena
- `contains`: "transformacij" OR `contains`: "konzistentnost mjera" OR `contains`: "conversion"
- `not_contains`: "da, možeš" OR `not_contains`: "jednostavno poolaj"
- `regex_match`: "konzistentno|isti effect measure|standardiz|konverzij|incompatible"

---

## prisma-checklist

### Case 1 — Happy path: Provjera PRISMA s identificiranim propustima
**Input:**
Provjeri PRISMA 2020 usklađenost: prijavljeni eligibility criteria, 4 baze (PubMed, Scopus, WoS, CENTRAL), full search strings, screening (2 recenzenta), data extraction (standardiziran form), RoB 2, forest plot, funnel plot. NIJE prijavljeno: PROSPERO registracija, GRADE procjena sigurnosti.

**Assertions:**
- `contains`: "PROSPERO" — nedostaje, mora biti identificirano
- `contains`: "GRADE" OR `contains`: "certainty" — nedostaje
- `not_contains`: "u potpunosti zadovoljava" OR `not_contains`: "fully compliant"
- `regex_match`: "nedostaje|nije naveden|missing|incomplete"
- `contains`: "PRISMA 2020"
- `last_sentence_not_question`

---

### Case 2 — Edge: Scoping review vs. systematic review PRISMA
**Input:**
Trebam primijeniti PRISMA checklist na scoping review (ne systematic review). Koje su stavke PRISMA 2020 primjenjive, a koje nisu? Specifično: meta-analiza nije rađena, GRADE nije primjenjiv.

**Assertions:**
- `contains`: "scoping" — prepoznaje razliku
- `contains`: "PRISMA-ScR" OR `contains`: "PRISMA for Scoping Reviews" — upućuje na ispravno izdanje
- `not_contains`: "GRADE je obavezan" — GRADE nije za scoping review
- `contains`: "eligibility criteria" — primjenjivo i za scoping
- `regex_match`: "primjenjiv|applicable|nije primjenjiv|not applicable|modific|prilagod"

---

### Case 3 — Kompletan: Identifikacija specifičnih propusta u dobro pripremljenoj studiji
**Input:**
Sustavni pregled ima: PROSPERO registraciju, 5 baza, 2 recenzenta za screening, GRADE procjenu, forest plot. Nema: datum zadnje pretrage, contact with study authors, full search strategy u suplementu.

**Assertions:**
- `contains`: "datum pretrage" OR `contains`: "search date" OR `contains`: "last search"
- `contains`: "search strategy" OR `contains`: "full search" — nepotpun prikaz pretrage
- `contains`: "autori studija" OR `contains`: "contact with authors"
- `not_contains`: "PRISMA compliant" OR `not_contains`: "zadovoljava PRISMA" — postoje propusti
- `regex_match`: "stavka|item|PRISMA.{0,20}[0-9]|[0-9].{0,20}PRISMA" — PRISMA item brojevi

---

## publication-bias

### Case 1 — Happy path: Egger + funnel + trim-and-fill, k=12
**Input:**
Provedi analizu publication biasa za meta-analizu s k=12 studija (OR effect measure). Napiši R kod za: (1) funnel plot, (2) Egger test, (3) trim-and-fill metodu. Interpretiraj rezultate.

**Assertions:**
- `contains`: "funnel" OR `contains`: "funnel_plot" OR `contains`: "funnel.plot"
- `contains`: "egger" OR `contains`: "regtest(" — Egger test
- `contains`: "trimfill(" OR `contains`: "trim.fill(" OR `contains`: "trimFill"
- `regex_match`: "library\s*\(\s*['\"]?meta|library\s*\(\s*['\"]?metafor"
- `last_sentence_not_question`

---

### Case 2 — Edge: k<10, Egger test nije valjan
**Input:**
Imam meta-analizu s k=7 studija. Treba li provoditi Egger test i trim-and-fill analizu?

**Assertions:**
- `contains`: "nije preporučeno" OR `contains`: "ograničena snaga" OR `contains`: "limited power"
- `contains`: "10" — navođenje granice k≥10
- `not_contains`: "da, provedi Egger" — ne smije preporučiti bez upozorenja za k=7
- `regex_match`: "snaga|power|ograničen|insufficient|k\s*[<≥]\s*10|premalo studij"
- `last_sentence_not_question`

---

### Case 3 — Interpretacija: Asimetrični funnel, trim-and-fill korigirao estimate
**Input:**
Interpretiraj ove nalaze i napiši tekst za Discussion: Egger test p=0.03. Trim-and-fill dodao 3 studije, korigirani OR=0.82 (95% CI 0.68–0.99) vs originalni OR=0.70 (95% CI 0.58–0.84).

**Assertions:**
- `contains`: "asimetri" OR `contains`: "asymmetr" — funnel asimetrija
- `contains`: "publication bias" — termin mora biti korišten
- `contains`: "0.82" — korigirani estimate
- `regex_match`: "3.{0,30}studij|trim.{0,10}fill.{0,50}3|dodane.{0,20}3"
- `not_contains`: "nema publication biasa" — Egger p=0.03 sugerira bias
- `regex_match`: "korigirani|adjusted|trim.{0,10}fill|adjusted estimate"
- `word_count_below`: 350
- `last_sentence_not_question`

---

## sensitivity-analysis

### Case 1 — Happy path: Leave-one-out, influence plot
**Input:**
Provedi sensitivity analizu za meta-analizu s k=8 studija (pooled OR=0.70, I²=18%). Napiši R kod za leave-one-out analizu i influence plot.

**Assertions:**
- `contains`: "leave.one.out(" OR `contains`: "leave_one_out" OR `contains`: "l1o"
- `contains`: "influence" OR `contains`: "influence plot" OR `contains`: "baujat"
- `contains`: "metafor" OR `contains`: "dmetar" OR `contains`: "library(meta"
- `regex_match`: "leave.one.out|influence\s*\(|baujat"
- `not_contains`: "nije potrebno" — sensitivity analiza je standardni korak
- `last_sentence_not_question`

---

### Case 2 — Edge: Jedna studija dramatično mijenja zaključak
**Input:**
Leave-one-out pokazuje: bez StudyC pooled OR=0.61 (95% CI 0.49–0.76, I²=5%); sa StudyC pooled OR=0.70 (CI 0.58–0.84, I²=18%). StudyC: n=950, high RoB. Interpretiraj za Discussion.

**Assertions:**
- `contains`: "StudyC" OR `contains`: "utjecajna studija" OR `contains`: "influential"
- `contains`: "high RoB" OR `contains`: "visok rizik pristranosti"
- `contains`: "sensitivity" — ključni termin
- `not_contains`: "zaključak se ne mijenja" — I² i CI se mijenjaju
- `regex_match`: "utjecaj|influential|mijenja|heterogenost.{0,50}smanji|I².{0,50}5"
- `last_sentence_not_question`

---

### Case 3 — Subgroup kao sensitivity: Prospektivne vs. retrospektivne studije
**Input:**
Provedi sensitivity analizu stratificiranu po dizajnu: prospektivne studije (k=4, OR=0.62), retrospektivne (k=4, OR=0.81). Napiši R kod i interpretiraj razliku između podgrupa, uključujući test za interakciju.

**Assertions:**
- `contains`: "prospektivn" OR `contains`: "prospective"
- `contains`: "retrospektivn" OR `contains`: "retrospective"
- `contains`: "0.62" AND `contains`: "0.81" — oba estimata
- `regex_match`: "Q_between|Q_b|test.{0,20}interaction|between.group|interakcij"
- `not_contains`: "nema razlike između podgrupa" — bez formalnog testa interakcije ne može se zaključiti
- `last_sentence_not_question`

---

## setup-project

### Case 1 — Happy path: Kreiranje standardne meta-analiza projektne strukture
**Input:**
Kreiraj projektnu strukturu za meta-analizu. Koristi standardni template: 01_input, 02_analysis, 03_output, 04_manuscript, 05_admin. Uključi README.md i .gitignore.

**Assertions:**
- `contains`: "01_input" OR `contains`: "input"
- `contains`: "02_analysis" OR `contains`: "analysis"
- `contains`: "03_output" OR `contains`: "output"
- `contains`: "04_manuscript" OR `contains`: "manuscript"
- `contains`: "README" — obavezan element
- `regex_match`: "mkdir|dir\.create|fs::|struktura|created"

---

### Case 2 — Edge: Projekt već postoji, ne prepiši
**Input:**
Kreiraj projektnu strukturu za novi projekt, ali mapa "01_input" već postoji s 5 datoteka unutra. Što napraviti s postojećom mapom?

**Assertions:**
- `contains`: "već postoji" OR `contains`: "exists" — prepoznaje problem
- `contains`: "ne briši" OR `contains`: "preskoči" OR `contains`: "skip" OR `contains`: "overwrite"
- `not_contains`: "izbriši" OR `not_contains`: "rm -rf" OR `not_contains`: "delete" — ne briše postojeće
- `regex_match`: "if.*exists|exist.*skip|provjeri|check.{0,30}exist"
- `last_sentence_not_question`

---

### Case 3 — Negativni: Zahtjev bez specificiranja projekta
**Input:**
Kreiraj projektnu strukturu.

**Assertions:**
- `regex_match`: "(?i)(naziv|name|ime projekta|koji projekt|koji tip|which project|what type|default|example_project)"
- `not_contains`: "ne mogu" OR `not_contains`: "nije moguće" — mora nešto napraviti ili zatražiti info
- `last_sentence_not_question`

---

## strobe-checklist

### Case 1 — Happy path: Kohortna studija s identificiranim propustima
**Input:**
Provjeri STROBE usklađenost za kohortnu studiju: prijavljeni setting, participanti, exposures, outcomes, confounders, statistička metoda. NIJE prijavljeno: handling of missing data, sensitivity analysis, funding sources.

**Assertions:**
- `contains`: "missing data" OR `contains`: "nedostajući podaci" — mora biti identificirano
- `contains`: "sensitivity analysis" OR `contains`: "osjetljivost" — nedostaje
- `contains`: "funding" OR `contains`: "financiranje" — nedostaje
- `contains`: "STROBE" — eksplicitno referenciranje
- `regex_match`: "nedostaje|nije naveden|item [0-9]|stavka [0-9]|missing"
- `last_sentence_not_question`

---

### Case 2 — Edge: Case-control, specifičnosti u odnosu na kohortnu studiju
**Input:**
Primijeniti STROBE checklist na case-control studiju. Koje su stavke specifične za case-control a ne za kohortnu? Fokus na selekciju kontrola i matchanje.

**Assertions:**
- `contains`: "case-control" — prepoznaje dizajn
- `contains`: "controls" OR `contains`: "kontrole" — selekcija kontrola specifična za CC
- `contains`: "matching" OR `contains`: "uparivanje" OR `contains`: "matched"
- `not_contains`: "isti checklist kao kohortna" — postoje razlike
- `regex_match`: "specifičan|specific|razlika|differ|case.control"

---

### Case 3 — Negativni: Cross-sectional studija, je li STROBE primjenjiv?
**Input:**
Koristim STROBE checklist za cross-sectional studiju. Je li STROBE primjenjiv ili treba drugi checklist?

**Assertions:**
- `contains`: "cross-sectional" — prepoznaje dizajn
- `contains`: "STROBE" AND `contains`: "cross-sectional" — STROBE JE primjenjiv
- `contains`: "prevalencija" OR `contains`: "prevalence" — specifičan za cross-sectional
- `not_contains`: "STROBE nije za cross-sectional" — STROBE je primjenjiv za CS
- `regex_match`: "cross.sectional.{0,60}STROBE|STROBE.{0,60}cross.sectional|prilagod|modificiran"

---

## swiss-cheese

### Case 1 — Happy path: Validacija PSM analize pred reporting
**Input:**
Provedi Swiss Cheese validaciju za propensity score matching analizu: opservacijska studija, primarni ishod 30-dnevni mortalitet, n=180. Analiza rađena u R, matching je gotov, ali balance post-matching nije provjeren.

**Assertions:**
- `contains`: "balance" OR `contains`: "balans" — SMD/love plot kao obavezan sloj
- `contains`: "SMD" OR `contains`: "standardized mean difference"
- `not_contains`: "analiza je ispravna" OR `not_contains`: "validacija je gotova" — balance nije provjeren
- `regex_match`: "sloj|layer|validacij|provjera|check|love plot"
- `last_sentence_not_question`

---

### Case 2 — Edge: Kompletna validacija pred slanje meta-analize
**Input:**
Pred slanje rukopisa, Swiss Cheese validacija meta-analize: k=8, pooled OR=0.70, I²=18%, Egger p=0.14, leave-one-out stabilna. Što još ostaje za validirati?

**Assertions:**
- `contains`: "GRADE" OR `contains`: "certainty" — sigurnost dokaza
- `contains`: "PRISMA" OR `contains`: "checklist" — izvještavanje
- `contains`: "protokol" OR `contains`: "PROSPERO" — registracija
- `contains`: "reproducibilnost" OR `contains`: "reproducibility" OR `contains`: "seed" — reproduktivnost koda
- `regex_match`: "sloj|layer|provjera|checklist|validacij"
- `word_count_below`: 500

---

### Case 3 — Negativni: Nedovoljna validacija — samo p-vrijednosti i forest plot
**Input:**
Analitičar tvrdi: "Swiss Cheese validacija je gotova — provjerio sam p-vrijednosti i napravio forest plot." Je li validacija dovoljna?

**Assertions:**
- `contains`: "nije dovoljna" OR `contains`: "insufficient" OR `contains`: "nepotpuna"
- `contains`: "assumptions" OR `contains`: "pretpostavke" — model assumptions
- `contains`: "reproducibilnost" OR `contains`: "reproducibility"
- `not_contains`: "da, validacija je dovoljna" OR `not_contains`: "prihvatljivo"
- `regex_match`: "nedostaje|missing|dodatni sloj|additional layer|samo.{0,30}nedovoljno"

---

## target-trial-emulation

### Case 1 — Happy path: Definiranje TTE protokola za ICU intervenciju
**Input:**
Definiraj protokol target triala za emulaciju RCT-a iz registry podataka: early CRRT (unutar 24h od AKI KDIGO stage 2) vs. standard timing (>24h). Ishod: 28-dnevni mortalitet. Dostupni podaci: bolnički registry ICU pacijenata, n=1200.

**Assertions:**
- `contains`: "eligibility criteria" OR `contains`: "inkluzijski kriteriji"
- `contains`: "treatment strategies" OR `contains`: "intervencija"
- `contains`: "time zero" OR `contains`: "index date" OR `contains`: "početna točka"
- `contains`: "confounders" OR `contains`: "konfunderi"
- `contains`: "ITT" OR `contains`: "causal contrast" OR `contains`: "kauzalni"
- `regex_match`: "target.trial|emulacij|Hernán|protokol"
- `last_sentence_not_question`

---

### Case 2 — Edge: Immortal time bias u registry studiji
**Input:**
U registry studiji, pacijenti koji primili CRRT u 24–72h od ICU prijema uspoređeni su s pacijentima koji nisu primili CRRT. Period od primitka do primanja CRRT nije tretiran kao at-risk period. Identificiraj problem kroz TTE framework i predloži rješenje.

**Assertions:**
- `contains`: "immortal time bias" — problem identificiran
- `contains`: "time zero" OR `contains`: "clone" OR `contains`: "cloning" — TTE rješenje
- `not_contains`: "nema problema" OR `not_contains`: "analiza je ispravna"
- `regex_match`: "immortal|besmrtno vrijeme|pristranost|bias|clone.{0,30}censor"
- `last_sentence_not_question`

---

### Case 3 — Negativni: TTE nije potreban za RCT
**Input:**
Imam randomiziranu kliničku studiju (RCT). Treba li primijeniti Target Trial Emulation framework?

**Assertions:**
- `contains`: "nije potrebno" OR `contains`: "not needed" OR `contains`: "RCT ne zahtijeva"
- `contains`: "TTE" AND `regex_match`: "opservacijska|observational|nije randomiziran|not randomized"
- `not_contains`: "da, primijeni TTE" — TTE je za opservacijske podatke
- `regex_match`: "opservacijska|observational|randomiziran.{0,30}nije|RCT.{0,50}ne treba"
- `last_sentence_not_question`

---

## test-selection

### Case 1 — Happy path: Dvije neovisne grupe, normalna distribucija, nejednake varijance
**Input:**
Odaberi statistički test: dvije neovisne grupe, kontinuirani outcome (MAP u mmHg), n=25 po grupi, Shapiro-Wilk p=0.31 (obje grupe), Levene test p=0.02.

**Assertions:**
- `contains`: "Welch" — Welch t-test (nejednake varijance)
- `not_contains`: "Student t-test" OR `not_contains`: "Student's t-test" — Student je za jednake varijance
- `not_contains`: "Mann-Whitney" — distribucija je normalna (SW p=0.31)
- `contains`: "Levene" OR `contains`: "varijanca" — objašnjenje zašto Welch
- `regex_match`: "Welch.{0,100}varijanca|nejednake varijance.{0,100}Welch"
- `last_sentence_not_question`

---

### Case 2 — Edge: Mali uzorak, nenormalna distribucija
**Input:**
Odaberi test: dvije neovisne grupe, kontinuirani outcome (ICU LOS u danima, desno asimetričan), n=12 po grupi, Shapiro-Wilk p=0.003 (grupa A), p=0.11 (grupa B).

**Assertions:**
- `contains`: "Mann-Whitney" OR `contains`: "Wilcoxon rank-sum" — neparametrijski test
- `not_contains`: "t-test" — nije prikladan (SW p=0.003)
- `contains`: "neparametri" OR `contains`: "nonparametric" OR `contains`: "asimetri"
- `contains`: "Shapiro-Wilk" OR `contains`: "normalnost" — obrazloženje
- `regex_match`: "Mann.Whitney|Wilcoxon|neparametri"
- `last_sentence_not_question`

---

### Case 3 — Tri ili više grupa: ANOVA
**Input:**
Odaberi test: 3 grupe (propofol, ketamin, midazolam), kontinuirani outcome (induction time u sekundama), n=20 po grupi, sve grupe normalno distribuirane (SW p>0.1 sve), Levene p=0.45.

**Assertions:**
- `contains`: "ANOVA" OR `contains`: "one-way ANOVA"
- `not_contains`: "Kruskal-Wallis" — nepotrebno, distribucija je normalna
- `not_contains`: "t-test" — više od 2 grupe
- `contains`: "post-hoc" OR `contains`: "Tukey" OR `contains`: "Bonferroni" — post-hoc provjera
- `regex_match`: "one.way.{0,50}ANOVA|ANOVA.{0,50}post.hoc"
- `last_sentence_not_question`

---

### Case 4 — Upareni podaci: Pre-post dizajn
**Input:**
Odaberi test: isti pacijenti mjereni u 2 točke (MAP prije i 5 minuta nakon indukcije anestezije), n=30, razlike normalno distribuirane (SW p=0.21).

**Assertions:**
- `contains`: "paired" OR `contains`: "upareni"
- `contains`: "paired t-test" OR `contains`: "upareni t-test"
- `not_contains`: "neovisni" OR `not_contains`: "independent" — nije neovisni uzorak
- `not_contains`: "Wilcoxon" — distribucija razlika je normalna, SW p=0.21
- `regex_match`: "paired.{0,50}t.test|upareni.{0,50}t"
- `last_sentence_not_question`

---

## validate-setup

### Case 1 — Happy path: Gotovo ispravna struktura, identificirani sitni propusti
**Input:**
Provjeri projektnu strukturu: mape 01_input (3 CSV), 02_analysis (R skripte), 03_output (prazna), 04_manuscript (DOCX draft), 05_admin (protokol PDF). Nedostaju: README.md, .gitignore, session_info.txt.

**Assertions:**
- `contains`: "README" — nedostaje, mora biti označeno
- `contains`: ".gitignore" OR `contains`: "gitignore" — nedostaje
- `contains`: "session_info" OR `contains`: "reproducibilnost" — reproducibilnost koda
- `not_contains`: "struktura je ispravna" OR `not_contains`: "sve je prisutno"
- `regex_match`: "nedostaje|missing|dodaj|add|preporuča"
- `last_sentence_not_question`

---

### Case 2 — Edge: Flat struktura, sve datoteke u jednoj mapi
**Input:**
Validacija: sve datoteke (input CSV, R skripte, output PDF, manuscript DOCX) su u jednoj mapi bez podstrukture. Postoji README.md ali nije organizirano po fazama projekta.

**Assertions:**
- `contains`: "podstruktura" OR `contains`: "organizacij" OR `contains`: "mape" — problem
- `contains`: "01_input" OR `contains`: "odvojiti" OR `contains`: "reorganiz" — preporuka
- `not_contains`: "struktura je prihvatljiva" — flat struktura nije prihvatljiva
- `regex_match`: "reorganiz|restructur|premjesti|move|odvoj|preporuč"
- `last_sentence_not_question`

---

### Case 3 — Negativni: Nedostajuće mape kritične za analizu
**Input:**
Provjeri strukturu: postoje mape 04_manuscript i 05_admin s dokumentima. Mape 01_input, 02_analysis, 03_output ne postoje. R skripte su u root direktoriju.

**Assertions:**
- `contains`: "01_input" OR `contains`: "input" — kritična mapa nedostaje
- `contains`: "02_analysis" OR `contains`: "analysis" — nedostaje
- `contains`: "03_output" OR `contains`: "output" — nedostaje
- `not_contains`: "struktura je zadovoljavajuća" OR `not_contains`: "prihvatljivo"
- `regex_match`: "nedostaje|kritična mapa|missing|reorganiz|kreirati"
- `last_sentence_not_question`

---

## create-sop

### Case 1 — Happy path: SOP za statističku analizu (PSM u 40_operations/R)
**Input:**
Kreiraj SOP za propensity score matching analizu u R: od uvoza podataka do izvještavanja. Uključi: korake, odgovornu osobu, verziju softvera, format outputa i kriterij za odobrenje.

**Assertions:**
- `contains`: "SOP" OR `contains`: "Standard Operating Procedure"
- `contains`: "software" OR `contains`: "R verzija" OR `contains`: "version"
- `contains`: "odgovornost" OR `contains`: "responsible" OR `contains`: "odgovorna osoba"
- `contains`: "propensity score" OR `contains`: "PSM"
- `regex_match`: "korak\s+[0-9]|step\s+[0-9]|[0-9]\.\s" — numeracija koraka
- `last_sentence_not_question`

---

### Case 2 — Edge: SOP za hitni klinički postupak (RSI)
**Input:**
Kreiraj SOP za rapid sequence induction (RSI): indikacije, preduvjeti (preoxygenation), lijekovi (indukcija + mišićni relaksant), koraci, moguće komplikacije, rescue plan za failed intubation.

**Assertions:**
- `contains`: "RSI" OR `contains`: "rapid sequence"
- `contains`: "preoksigenacij" OR `contains`: "preoxygenation" — obavezan korak
- `contains`: "rescue" OR `contains`: "cannot intubate" OR `contains`: "plan B" OR `contains`: "failed airway"
- `contains`: "krikoidsni" OR `contains`: "Sellick" OR `contains`: "cricoid" — ili eksplicitno navodi da je kontroverzno
- `regex_match`: "korak\s+[0-9]|[0-9]\.\s|faza|step"
- `not_contains`: "nije moguće napisati SOP"
- `last_sentence_not_question`

---

### Case 3 — Negativni: Zahtjev bez konteksta
**Input:**
Napiši SOP.

**Assertions:**
- `regex_match`: "koji postupak|za što|specificiraj|koji tip|which procedure|what process|tema|subject"
- `not_contains`: "Korak 1:" — ne piše generički SOP bez konteksta
- `not_contains`: "Standard Operating Procedure za" — ne generira nasumičan SOP
- `last_sentence_not_question`

---

## literature-synthesis

### Case 1 — Happy path: Sinteza 5 studija, grid + konsenzus + gapovi
**Input:**
Sintetiziraj ove studije o HFNC vs. NIV u ACPE:
A: RCT 2019, n=200 — HFNC bolji za SpO2 na 1h, mortalitet NS
B: RCT 2021, n=150 — NIV bolji za dyspnea score
C: Retrospektivna 2020, n=400 — HFNC kraći ICU boravak
D: RCT 2022, n=180 — bez razlike u mortalitetu
E: Meta-analiza 2023, k=8 — mortalitet OR=0.89 (I²=42%)
Identificiraj konsenzus, kontradikcije i istraživačke gapove.

**Assertions:**
- `contains`: "konsenzus" OR `contains`: "consensus" OR `contains`: "agreement"
- `contains`: "kontradikcij" OR `contains`: "contradict" OR `contains`: "inconsisten"
- `contains`: "gap" OR `contains`: "praznina" OR `contains`: "nedostaje istraživanje" OR `contains`: "future research"
- `contains`: "mortalitet" — ključni ishod
- `regex_match`: "grid|tablica|table|sinteza|summary|pregled"
- `not_contains`: "nije moguće sintetizirati"
- `last_sentence_not_question`

---

### Case 2 — Edge: Direktno kontradiktorni nalazi, sinteza nije jednoznačna
**Input:**
Sintetiziraj 3 RCT-a s direktno kontradiktornim nalazima za isti primarni ishod (mortalitet, slična populacija):
Studija 1: HFNC superioran, p=0.02
Studija 2: NIV superioran, p=0.04
Studija 3: bez razlike, p=0.38

**Assertions:**
- `contains`: "kontradiktorni" OR `contains`: "contradict" OR `contains`: "inconsistent"
- `contains`: "heterogenost" OR `contains`: "heterogeneity" OR `contains`: "raznolik"
- `not_contains`: "zaključak je jasan" OR `not_contains`: "HFNC je superioran" — nema jednoznačnog zaključka
- `not_contains`: "NIV je superioran"
- `contains`: "daljnje istraživanje" OR `contains`: "future research" OR `contains`: "potrebno"
- `regex_match`: "nesukladnost|inconsisten|kontradiktor|mixed evidence|nedovoljan dokaz"

---

### Case 3 — Negativni: Sinteza bez dovoljno informacija o studijama
**Input:**
Sintetiziraj literaturu o perioperativnoj tekućinskoj terapiji. Nemam detalje o studijama, samo temu.

**Assertions:**
- `regex_match`: "(?i)(koje studije|koji članci|koje izvore|specific studies|which papers|popis|lista studija|trebam detalje|navedi studije|popis referenci)"
- `not_contains`: "konsenzus je:" — ne generira sintezu bez inputa
- `not_contains`: "literatura pokazuje" — bez konkretnih studija ne može sintetizirati
- `last_sentence_not_question`

---

## Napomene za implementaciju

- **Case-insensitive:** Gdje nije striktno potrebno, koristi `regex_match` s `(?i)` umjesto `contains` (npr. `(?i)norepinephr(in|ine)`), ili navedi obje jezične varijante (HR/EN).
- **OR u jednoj liniji:** Konverter (`md_evals_to_json.py`) pretvara "A OR B" u jedan assertion: za `contains` spaja u jedan `regex_match`; za `not_contains` ostavlja oba. Ako treba "prolazi ako bilo koji od A/B", koristi jedan `regex_match` s alternativama.
- **Kod (R, Python):** Uvijek dodaj `regex_match` za ključne funkcije/pakete, ne samo `contains` na naziv.
- **word_count_below:** Postavi realistično; prestroge granice penaliziraju točnost.
- **Regeneracija JSON:** Nakon izmjene speca pokreni `python 40_operations/scripts/md_evals_to_json.py` (čita ovaj md iz `30_system/SKILLS/evals/`).

## Related Hubs

- [Folder index hub](../../docs/FOLDER_INDEX.md)
- [All notes index](../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../docs/GRAPH_CONNECTIVITY_MAP.md)
