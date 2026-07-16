# HANDOFF — nastavak Parallel deep research

**Za novi Cloud Agent / razgovor.** Čitaj ovo prvo.

## Stanje (2026-07-16)

- Branch: `cursor/bonton-book-research-9b19` (**NE mergati u `master`**)
- Korpus: `docs/bonton/research/` (~2.6 MB) — vidi `CATALOG.md`
- Rukopis: `docs/bonton/mala-knjiga-pusackog-bontona.md`
- App bonton: `app/src/data/bonton.json` (na masteru, već deployano)
- Korisnik je dodao Cursor Secret: `PARALLEL_API_KEY` (Runtime Secret)
- Prethodna sesija **nije** imala ključ (agent pokrenut prije secreta) — zato deep research nije krenuo

## Što napraviti odmah

1. `git checkout cursor/bonton-book-research-9b19`
2. Provjeri auth **bez ispisivanja ključa**:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   [ -n "$PARALLEL_API_KEY" ] && echo "key present" || echo "key MISSING"
   parallel-cli auth
   ```
3. Ako ključ postoji, pokreni **opsežno** deep research (korisnik tražio: polako, u pozadini, sva građa, notirati izvore, preuzimati tekst):
   ```bash
   cd /workspace/docs/bonton/research
   parallel-cli research run "Exhaustive source corpus for a book on cigar and smoking etiquette (pušački bonton): British and Victorian/Edwardian gentleman manners and smoking-room customs; classic etiquette manuals (Hartley, Young, Wells, Emily Post, Beeton); Zino Davidoff cigar etiquette; contemporary cigar lounge hospitality norms; scholarly literature on tobacco, gender, and social space; cultural history of gentlemen's clubs and smoking jackets; hospitality rules for offering cigars and pairing drinks; public-domain texts and repository holdings (Internet Archive, Gutenberg, libraries). Prefer citable primary and secondary sources; list URLs/DOIs; extract usable excerpts for manuscript writing." \
     --processor ultra --no-wait --json
   ```
4. Poll u pozadini (`--timeout 540`), spremi output u:
   - `notes/parallel-ultra-bonton.md`
   - `notes/parallel-ultra-bonton.json`
5. Iz rezultata izvuci URL-ove → `parallel-cli extract` u `extracts/`
6. Ažuriraj `CATALOG.md` + commit + push **samo** na research branch

## Dodatni research krugovi (ako ultra uspije)

- Europeana / Library of Congress tobacco etiquette prints
- HR / regional hospitality norms (ako postoje kvalitetni izvori)
- Emily Post smoking sections (full)
- Davidoff essay text if licence-clean

## Ne raditi

- Ne mergati u `master`
- Ne printati / commitati `PARALLEL_API_KEY`
- Ne wholesale-kopirati Bridges *How to Be a Gentleman* (copyright) — samo forma kratkih precepta
