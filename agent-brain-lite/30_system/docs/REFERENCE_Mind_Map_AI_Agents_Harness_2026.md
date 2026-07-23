# AI Agents i Harness Engineering (2026) – Referentni dokument

Preuzeto iz mind map vizualizacije i prevedeno u čitljiv markdown format za integraciju u plan nadogradnje.

---

## 1. Koncept Harness Engineeringa

| Element | Opis |
|---------|------|
| **Definicija** | Infrastruktura oko modela: alati, memorija, mehanizmi oporavka |
| **Trend** | Harness je važniji od samog LLM modela |
| **Gorko poučenje** | Jednostavniji harness skalira bolje s pametnijim modelima |
| **Optimizacija konteksta** | Smanjenje šuma kroz "context engineering" |

---

## 2. Dokumentacijski sustavi (.agent folder)

### Struktura mapa

| Mapa | Sadržaj |
|------|---------|
| **task/** | PRD-ovi i planovi implementacije |
| **system/** | Arhitektura, sheme baze, API-ji |
| **SOPs/** | Standardni postupci i ispravci grešaka |
| **readme.md** | Indeks svih dokumenata |

### Datoteke

| Datoteka | Namjena |
|----------|---------|
| **CLAUDE.md** | Upute (korisničke instrukcije, stil, biblioteke) |
| **MEMORY.md** | Auto-memorija (agent piše progress, ograničeno ~200 linija) |

### Ključni princip

**File system kao eksterna memorija za LLM** – zaobilazak ograničenja tokena; informacije se čuvaju u datotekama i čitaju samo kad treba.

---

## 3. Izolacija i paralelizacija

| Tehnika | Opis |
|---------|------|
| **Git Worktrees** | Izolirani direktoriji po granama; izbjegavanje merge konflikata |
| **Tmux** | Više terminalskih okana za "swarm" agenata; orchestacija |
| **Sub-agenti** | Delegiranje istraživanja radi uštede tokena – research u izolaciji, sažetak u glavni thread |

---

## 4. Cursor Cloud Agents

| Element | Opis |
|---------|------|
| **Isolated VMs** | Agent ima vlastito računalo u oblaku |
| **Computer Use** | Agent koristi preglednik i terminal kao čovjek |
| **Provjera** | Snimke zaslona i video zapisi rada ("Demos, not diffs") |
| **Testiranje** | Integracija s alatima poput Test Sprite |

---

## 5. Napredne tehnike i alati

| Element | Opis |
|---------|------|
| **Skills.md** | Strukturirano: Title, Description, Instructions |
| **MCP (Model Context Protocol)** | Standardizirano povezivanje s alatima |
| **NotebookLM MCP** | Povezivanje dokumentacije iz više izvora |
| **Vibe Coding** | Razvoj aplikacija bez dubokog pregleda koda – rizično |

---

## 6. Izazovi i etika

| Izazov | Opis |
|--------|------|
| **Rizik** | Sigurnost koda koji čovjek nije pregledao |
| **Brzina vs kontrola** | Balansiranje brzine agenta i ljudskog review-a |
| **Halucinacije** | Zabrana izmišljanja URL-ova; oslanjanje na dokumentaciju |

---

## Mapiranje na postojeći sustav

| Mind map element | Ekvivalent u agent rules |
|------------------|--------------------------|
| .agent/task/ | 30_system/04_documentation/context/, plan taskova |
| .agent/system/ | 30_system/docs/EXISTING_ARCHITECTURE.md, 30_system/behavior_rules/ |
| .agent/SOPs/ | 30_system/SKILLS/*.md, 99_error_memory.mdc |
| CLAUDE.md | .cursor/rules (core-principles, orchestrator) |
| MEMORY.md | Novo – auto-progress tracking |
| Skills.md | 30_system/SKILLS/SKILL_*.md |
| Halucinacije | core-principles: "Never hallucinate", "Never fabricate citations" |

## Related Hubs

- [Folder index hub](FOLDER_INDEX.md)
- [All notes index](ALL_NOTES_INDEX.md)
- [Graph connectivity map](GRAPH_CONNECTIVITY_MAP.md)
