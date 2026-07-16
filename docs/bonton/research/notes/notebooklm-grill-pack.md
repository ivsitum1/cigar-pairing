# NotebookLM grill pack — pušački bonton

_Generated: 2026-07-16_

Agent **ne može** čitati NotebookLM share linkove bez Google auth-a (redirect na Sign in).
Korisnik grill-a notebooke lokalno ovim promptima, pa exporta odgovore u repo.

## Notebookovi

1. https://notebooklm.google.com/notebook/5b8ae55e-d6bf-4cde-afb2-33492c1b241b
2. https://notebooklm.google.com/notebook/2707d3fe-73d1-4879-8e8d-b7538d1cb3f2

## Kako vratiti rezultate agentu

Za svaki notebook:

1. Pokrenite prompti ispod (jedan po jedan, ili batch).
2. Koristite NotebookLM **Save to note** / copy odgovora.
3. Exportajte kao markdown/tekst u:
   - `docs/bonton/research/extracts/notebooklm-01-<short-title>.md`
   - `docs/bonton/research/extracts/notebooklm-02-<short-title>.md`
4. Ili zalijepite odgovore u chat.

U svakom exportu navedite: notebook URL, datum, popis source videa/dokumenata.

---

## Prompti (zalijepi u NotebookLM chat)

### A. Inventar izvora
```
List every source in this notebook (title, creator/channel, type: YouTube/PDF/web, and one-sentence relevance to cigar or smoking etiquette). Flag weak or off-topic sources.
```

### B. Pravila lounge bontona
```
Extract a structured list of cigar lounge etiquette rules from the sources. For each rule give: (1) the rule in one sentence, (2) why it matters, (3) which source(s) support it, (4) whether sources agree or conflict. Separate hard rules from soft preferences.
```

### C. Gentleman / Davidoff ritual
```
Summarize gentleman cigar manners and Davidoff-related guidance: cutting, lighting, band removal, ash, pacing, relighting, walking while smoking, offering/sharing light. Quote short phrases only when clearly attributed; otherwise paraphrase. Note copyrighted vs paraphrase-safe material.
```

### D. Povijesni kontekst
```
What do the sources say about historical smoking rooms, Victorian/Edwardian manners, clubs, gender/space, or Turkish smoking rooms? Separate verified historical claims from modern lifestyle commentary.
```

### E. Gostoprimstvo (ponuda cigare)
```
Extract hospitality norms: offering a cigar to a guest, asking permission to smoke, host/guest duties, tipping, BYOC, supporting the house, phone use, perfume/cologne, table manners around smoke.
```

### F. Kontrast s knjižnim korpusom
```
Compare these video-derived rules with classic etiquette manuals (Emily Post smoking rules; no smoking with a lady on the street; after-dinner cigars; club smoking rooms). Where do modern lounge norms continue or break from 19th/early-20th-century codes?
```

### G. Rukopis-ready precepti
```
Produce 25 short precepts suitable for a Croatian book of smoking manners (pušački bonton), in this format:
- EN precept (1 sentence)
- HR draft precept (1 sentence)
- Source tags
Do not invent rules not grounded in the notebook sources. Mark low-confidence items.
```

### H. Rupe i proturječja
```
What important etiquette questions are unanswered or contradicted across sources in this notebook? List gaps we should fill with books, LOC/Europeana items, or more YouTube.
```

### I. Study Guide / FAQ (ako NotebookLM nudi gumb)
Generiraj **Study Guide** i **FAQ**, pa ih spremi u notes. Posebno traži:
- lounge dos/don'ts
- lighting & cutting mistakes
- band etiquette
- historical smoking-room notes

---

## Agent follow-up (nakon exporta)

1. Deduplikacija vs postojeći `extracts/web-*` lounge izvori
2. Unos u `CATALOG.md` pod `notebooklm-*`
3. Selekcija precepta za `mala-knjiga-pusackog-bontona.md`
