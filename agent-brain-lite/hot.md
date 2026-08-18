---
title: Session Hot Cache
category: meta
tags: [session, cache]
updated: 2026-08-18
---

> **2026-08-18:** Gift finder: uz pet jezgrenih pitanja, uvjetna polica (BUCKETS) i način odabira boce (rupa / vrh / omjer). Budžet `over100`. Ne čita tuđu kolekciju. Naslov: „Poklon u nekoliko pitanja”.

> **2026-08-18:** Katalog house-line: shop-split linije vraćene pod Ashton/Padilla/My Father/Tatuaje/La Galera/Nicarao/Villiger. Cuban Fonseca, H. Upmann, Montecristo ostaju zasebno. `productPhoto` prati `cigarIdAliases`. Humidorova slika za Tailgate i La Ley.

> **2026-08-17:** Gift chooser `#/shopping/gift`: pet pitanja (osoba + budžet do 20 / 20–40 / 40–60 / 60–100 €) → cigara, boca ili kombinacija s cijenom u blizini. Zbroj kombinacije ostaje u pojasu.

# Session Hot Cache

~500 riječi snapshot nedavne aktivnosti. Agent ažurira nakon svake značajnije operacije pisanja u wiki.

> **2026-08-13:** Cusano HR duhovi (linije *Cusano* / *Petit*): `sync-hr-shops` iz Havana naziva radio je lažne linije; `LINE_RULES` je ciljao nestali `cig-cusano`. Katalog u gitu već ima 4 prave linije. Popravak: LINE_RULES + alias follow, *petit panatela* kao vitola, aliasi + absorb odluke. Ne vrtiti `normalize-vitolas.py` bez `--check` (presloži cijeli katalog).

> **2026-08-12:** Coffee audit: `coffees.json` +3 (americano, Burundi, Panama Geisha); Sumatra duhan/drvo; `coffeePairing` wired u `pairing.ts` + WEIGHTS; `coffees.catalog.test.ts`.

> **2026-08-12:** Club 101 Pića: `d-wine-table`, `d-coffee`, `d-tequila` u `club101.json`.

> **2026-08-12:** NotebookLM grill kava: Hoffmann *World Atlas* (`e2f2af38` = `e2f4c754` alt URL). Dump `docs/bonton/research/notebooklm-grill/e2f2af38-*`; MCP id `coffee-hoffmann-atlas`.

> **2026-08-12:** Kalendar dnevnika: korekcija datuma — `updateJournalEntry`, `applyLocalDayToIso`, date input na JournalCard + Collection journal; HR/EN `hum.editDate`.

> **2026-08-12:** Logo refine: snifter unutar tijela (bez cijepanja), −15°, taper head, oxblood band + zlato-2 rubovi. PWA + `LOGO_PHILOSOPHY.md` ažurirani.

> **2026-08-11:** Logo mark **Negativni band** (cigara + snifter prorez, zlato/humidor/oxblood). Skice `docs/brand/logo-sketches/`; philosophy `docs/brand/LOGO_PHILOSOPHY.md`; PWA `app/public/icon.svg` + 192/512. Regenerator `generate_logo_assets.py`.

> **2026-08-11:** Full vitola catalogs (pagefetch): Neptune sitemap **6489** (100% project URL overlap 2196/2196), Cigarworld sitemap_en **6488** (3124/3160), Cigarsdaily WP sitemap **1619** (31/31), Cigarpassion Luigi **2269**, Humidor/Havana prior. Famous/C.Gars CF-limited (partial). Holt's sitemap = brand pages only. Report `sideprojects/pagefetch/output/vitola_compare/report.json`.

> **2026-08-11:** pagefetch vitola katalog: Humidor 312/312, Havana WC API 426, Cigarpassion Luigi Box API → **2252** unique SKU (site/API `total_hits` 2293 = 41 dup id). Skripte `crawl_cigarpassion_luigi.py`, `rebuild_vitola_report.py`; report `sideprojects/pagefetch/output/vitola_compare/report.json`. Usporedba na product URL, ne line.

> **2026-08-05:** CONTINUATION OF Claude Code � handoff `.agent/task/handoff_2026-08-05-claude-continuation.md`. Cursor dovr�ava W4 + nomenklatura/~72 vitola curate.

> **2026-08-01:** Rum lab/hidrometar Val 1: **17** boca dobile stvarni g/L (Systembolaget/FRP/Drejer) umjesto stilske procjene — mapa `scripts/data/rum-lab-sugar.json`. Okusne note + tagovi: tanki unosi popunjeni (notes ispod 80 → 0; tags ispod 3 → 0). Ostalih ~135 stilskih bez mjerenja nije dirano. Skripte `apply-rum-lab-sugar.py`, `enrich-rum-taste-notes.py`.

> **2026-07-31:** Rum cleanup kombiniranih unosa: ako postoje obje polovice (npr. Flor 12+18) → briši `12/18`; ako samo jedna → preimenuj stari u drugu. Ne uvoziti „sa 2 čaše”. Obrisano 9 supersedanih/META; katalog **321**. Formidable dobio `cigarHint` (curatedNotes). Skripta `cleanup-combined-rums.py`.

> **2026-07-31:** Allez rum enrichment: **181** boca — opisi HR+EN, šećer+boja (E150) u `additiveDetail`, urednički `qualityScore`. Izvori: AOC / dekl. proizvođača / stilska procjena (bez izmišljenih g/L). Skripte `enrich-allez-rums.py` + `enrich-allez-rums-b.py`. Katalog bio **330**, sad **321** nakon cleanup.

> **2026-07-31:** Allez rum ingest (više batchova) → `rums.json` **305** boca. Skripte: `ingest-allez-rum-gaps.py` + `restore-allez-rum-batches.py` + `_run_allez_rum_full.py`; backup `scripts/output/rums-allez-latest.json` (OneDrive je jednom vratio stariju verziju).

> **2026-08-01:** Orthography/parallel keys: Don Pepin→**Don Pépin García**; Aliados→**Cuba Aliados**; The Oscar→**Oscar Valladares** (linija The Oscar * na kartici). Katalog 3711→3701. Skripta `unify_orthography_brands.py`.

> **2026-08-01:** House lines pod kuću + jasno označene: Four Kicks/La Imperiosa/Juarez/Mil Dias/Luminosa→**Crowned Heads**; Charter Oak/Tabernacle/Olmec/Menelik/El Güegüense/Wise Man→**Foundation**; Sobremesa/Mi Querida→**Dunbarton T&T**. Blurbs kažu da su imenovane linije kuće. Skripta `unify_house_lines.py`. Katalog 3738→3711.

> **2026-08-01:** Brand≠line splits spojeni: Argyle Fumas, Bahia Blu, Cain*, Don Lino Fumas, Nat Sherman Host/Metropolitan/Timeless, Lunatic→JFR. Testovi integrity/data OK.

> **2026-07-31:** Four shops → cigars.json (additive): baseline `baseline_four_shops_20260731`; Neptune sitemap (~4417) + Exa curated Famous/C.Gars/La Couronne; merge `merge_four_shops_additive.py` (nikad overwrite regionLinks; kubanke samo EU). Katalog 2400→3756; integrity/cigars.data/shops + tsc OK.

> **2026-07-31:** Allez rum gap: +60 boca u `rums.json` (Martinique Clément/Depaz/HSE/J.M/Trois Rivières + A.H. Riise linija + Rodney/Banks/Chairman/CDI/Flor de Caña/Saint James 15). Cijene s Alleza; `priceUrl` kasnije (shop timeout). Skripta `ingest-allez-rum-gaps.py`. Katalog 193→253. Pairing testovi OK.

> **2026-07-31:** Coffee↔cigar overlay (`engine/coffeePairing.ts`): izvor znanja o kavi = Hoffmann *The World Atlas of Coffee*; cigar-pairing pravila izvedena (balance/intensity/harmony), ne doslovno iz knjige. Soft rules + `data/coffeePairingModel.json`. Body-first. Testovi OK.

> **2026-07-31:** Cusano katalog: Bundle Selection (HR+EU) + **Honduras Bundle** (EU) + **18 Double Connecticut** / **18 Maduro** (USA). Maknut krivi Holts Connecticut s Bundlea. Taxonomy `cusano.json` done. Testovi integrity/cigars OK.

> **2026-07-30:** Triple NotebookLM grill — `7b267552` Cigars daily · `6ccc327c` Omaha value · `30d6a797` Black Gold. Dumpovi `research/notebooklm-grill/{uuid}-*`. Wiki: value-vs-price-stol, rum-tasting-host, limited-edition-culture. App: Club `d-tasting-order`, 3 lexicon termina, mala-knjiga/`bonton.json` precepti. Gentleman EN/HR freeze netaknut.

> **2026-07-30:** App sync: `mala-knjiga-pusackog-bontona.md` + `bonton.json` — kanon iz HR freeze (*dim* vs *draw*, BYOB, Jadran, finite glagoli, *sparivanje*). Testovi bonton.

> **2026-07-30:** Faza 2 gotova — HR *Gospodin za stolom* zamrznut kao književni prijevod s EN freeze. `KAKO-BITI-GOSPODIN-ZA-STOLOM-DRAFT.md` (~13.5k riječi, Dodatak A/B usklađen s EN rezom). Kanon-prolaz: *dim* vs *draw*, *cigara*, finite glagoli. EN ostaje source of truth; app sync (`mala-knjiga` / `bonton.json`) kasnije.

> **2026-07-30:** EN *Gentleman at the Table* **frozen** for HR translation. File: `docs/bonton/HOW-TO-BE-A-GENTLEMAN-AT-THE-TABLE-DRAFT.md` (~18k words after appendix cut). TOC synced to H2s; ch.11 retitled; ch.18 Adriatic sensory beat; Appendix A/B slimmed (cut layout-filler / Appendix D / mechanical essays); back matter honesty + editor note. HR draft header = read-only until Phase 2. Plan: `docs/superpowers/plans/2026-07-30-gentleman-en-finalize.md`. CROSSWALK + craft grill `5017a44b` remain reference.

> **2026-07-30:** NotebookLM craft grill `5017a44b` (*Art and Craft of Showing Not Telling*, 44 izvora) → nonfiction priručnik. Dump: `docs/bonton/research/notebooklm-grill/5017a44b-*`. EN/HR draft: How-to-read (promise + desk use + Uber Reader=gost/domaćin), gl.1 miniature beat, vinjeta senzor, editor anti-overwrite. MCP id `writing-craft-publishing`. CROSSWALK ažuriran.

> **2026-07-30:** Dnevnik večeri: ulaz C (DetailSheet + kartice sparivanja), pretraga kataloga pića + solo cigara, wishlist upit kad zaliha → 0, Kupovina restock. Don Tomas Clásico HR @ Tobacco Petica. Testovi 381/381.

> **2026-07-30:** Club facts/kviz: *vlak* → **draw** (loan; otpor/protok). Kanon: *dim* = brojivi gutljaj; *vlak* zabranjen kao calque. Rez: „tri **uobičajena**” + fact „Jeste li znali?” (škare, casino, Cuban cut, pinch).

> **2026-07-27:** Live: kategorija **digestif** (Biljni digestivi / Herbal digestifs) + Club101 `d-digestif` + 12 boca. PR #102 merged; Pages deploy OK. CI fix: taxonomy linije La Aroma (No. 3 / Habano Reserve / Small Batch) + re-apply.

> **2026-07-27:** HR kanon (projekt): `.cursor/rules/hr-copy-canon.mdc` — *cigara* (padeži), *pepeo*, *domaćin*≠kuća-agens, bez infinitivnih lanaca, Rječnik≠Leksikon≠Bonton. Rječnik očišćen (maknut table/bonton; Leksikon više nije „rječnik”).

> **2026-07-26:** Pairing/copy prolaz: agricole light-band + bidirekcionalni tag komplem.; 34 slash-boca razdvojene; Holts Clubhouse scrape (34 čl.) + gap map; Club facts (tanini, pepeo, Boveda RH, vino/žestice); 16 brand blurba; krivi URL-ovi (ADN, Perdomo, Camacho, Cohiba); filter tipa pića u Pairing. Testovi 279/279.

> **2026-07-26:** Soft-band drink→cigara: `softBandRank` (max−5 + day seed + cycle); UI samo taj smjer. Audit 779×2394: mean band 35.6, bandSize==1 1.9% (gate OK, formula netaknuta). Izvještaj `01_work/output/SOFT-BAND-RANK-AUDIT.md`.

> **2026-07-26:** Klub facts/kviz krugovi 6–8 (nastavak Claude sesije): 148→190 facts, 148→196 quiz u `club.json`; bez em dasha / dimka.

> **2026-07-26:** HR rječnik (puff): **dim** (brojivo: prvi dim, jedan dim). Ne: dimka, povlačenje, potez, usis. Tvar/atmosfera i dalje *dim*.

> **2026-07-26:** HR spirits: gin/tequila pipeline (scrape→Excel→calibrate-master→JSON); brandy refresh + orphan merge. Katalog: gin 70, tequila 26, brandy 98. Branch `catalog-hr-gin-tequila-cognac`.

> **2026-07-26:** Bonton salon: „kuća” (agens) → „domaćin”; „kućna pravila” / „kućni rezač” ostaju. Prije: „javna pušionica” → „cigar lounge”; XI 3. pravilo.

> **2026-07-25:** Flavor scrape: CW HTTP (VariantInfo + aroma canvas; 429→resume/backoff). Famous: urllib/CAPTCHA; Cursor browser `fetch` radi — 22 linije u korpusu. Learning: `knowledge/learnings/shop-flavor-scrape.md`.

> **2026-07-24:** Cigare na popisu: „od X €” samo kad je X stvarno najniža stick cijena; LE/krivi brend URL i sampler/pack isključeni iz zadane cijene. HR bilješke: pokrov→wrapper (runtime + generatori); filler/binder u brands.

> **2026-07-24:** Katalog: filter oblika (Robusto/Toro/…) opet vidljiv uz indeks brendova; odabir oblika prebacuje na filtrirani ravni popis (+ BrandSheet poštuje filter).

> **2026-07-23:** Round 3 C/D/J/B: katalog **2729 / 5528**; residual J 0; lexicon `slugs` 36; dims 239 + 28 dash leftover; H/I exact-URL fill out of scope (no invent).

> **2026-07-22:** App dijakritike: cijeli `hrGuide.json` + pića/notes (`doslađivanje`, `Čist`, `klasična`, `kuća`, `više regija`/`miješanje`); shops + regions.uskladjeno.

> **2026-07-22:** Prolaz dijakritika u draftu bontona (gl. pića/čaša i cijeli rukopis): skener visoke pouzdanosti; ispravak `nepceu` → `nepcu` u gl. 13; ostalo čisto (filename `pusackog` namjerno ASCII).

> **2026-07-22:** Exhaustivni audit pairing scorea: 3104 cigare × 633 pića = 1 964 832 parova; μ≈48.9, σ≈21.2; JB/χ² odbacuju Gaus; invarijante OK. Izvještaj `01_work/output/PAIRING-SCORE-AUDIT.md`, skripta `app/scripts/audit-pairing-distribution.mts`.

> **2026-07-20:** App: Brand Index (Catalog chip Brendovi + Excel sheet); Batch A remap Padrón + Drew Estate Additional Vitolas. Audit sad 26 brendova.

> **2026-07-20:** App katalog: AJ Fernandez usklađen s humidor.hr (Blend 15, Last Call, Enclave, New World, Bellas Artes…); Additional Vitolas audit → `docs/superpowers/specs/2026-07-20-cigar-additional-vitolas-audit.md`.

> **2026-07-20:** Jedini kanonski draft: `docs/bonton/KAKO-BITI-GOSPODIN-ZA-STOLOM-DRAFT.md`. Backup + PDF → `docs/bonton/archive/`. README u bonton/.
