# Evaluacija workspace-a „agent rules”

**Datum:** 2026-03-16  
**Ocjena:** **84/100**

---

## Sažetak

Workspace je dobro strukturiran sustav pravila i alata za AI agente u znanstvenom/medicinskom pisanju. Jaka je strana: tier sustav pravila, orchestrator, registry vještina, Swiss Cheese verifikacija, learning loop i skripte za „brain” operacije. Glavni nedostaci: zastarjele putanje u dijelu dokumentacije (.ai vs. 30_system/behavior_rules/tools), dvojnost .ai vs. .agent bez jasnog objašnjenja u jednom mjestu, te potreba da se eksplicitno dokumentira pokretanje skripti kada je agent-rules u drugom projektu kao podfolder.

---

## Ocjena po kriterijima (1–100)

| Kriterij | Ocjena | Napomena |
|----------|--------|----------|
| **Arhitektura i konzistentnost** | 82 | Tier sustav, INDEX, .agent – odlično; zastarjele putanje u behavior_rules |
| **Potpunost** | 90 | Pravila, skills, skripte, dokumentacija, testovi, MCP – vrlo potpuno |
| **Dokumentacija** | 85 | INDEX, README, BRAIN_AND_PROJECT; neke unakrsne reference zastarjele |
| **Održivost** | 84 | Error memory, learning loop, registry; ponegdje duplikati putanja (backslash) |
| **Uporabljivost** | 86 | Jasna delegacija, pipelinei, brain naredbe; treba pojasniti putanje skripti |

**Ukupno:** (82+90+85+84+86)/5 ≈ **85**; zbog utjecaja konzistentnosti na svakodnevnu uporabu konačna ocjena **84/100**.

---

## Što radi dobro

1. **Tier sustav i kontekst**  
   Tier 0–3, token budžet, progresivno učitavanje vještina (scan YAML → load skill → reference files po potrebi) – smisleno i dobro opisano u `context-optimization.mdc` i INDEX.md.

2. **Orchestrator i subagenti**  
   Klasifikacija zadatka, odabir subagenta, pipelinei i handoff format jasno su u `00_orchestrator_agent.mdc`; classification hints u `30_system/behavior_rules/reference/classification_hints.md`.

3. **Skills registry**  
   `30_system/SKILLS/registry.json` kao jedan izvor istine, disambiguation i conflicts_with; sve SKILL datoteke iz registra postoje. Mapiranje zadatak → skill u skills-auto-detect.mdc i skill_task_mapping.md.

4. **Sigurnost i kvaliteta**  
   Core principles (no hallucination, no fabrication, self-assessment ≥9/10), Swiss Cheese obavezan za kritične analize, verification.mdc i 30_system/behavior_rules/05_verification.md.

5. **Learning loop i error memory**  
   `14_learning_loop.md`, `99_error_memory.mdc`, error_log.jsonl i promocija u pravila; ERROR LEARNING PROTOCOL u orchestratoru.

6. **Skripte i „brain” naredbe**  
   brain_status, brain_audit, brain_health, context_sync, project_init, skill_registry, run_pipeline – na jednom mjestu u 40_operations/scripts/ s README.

7. **MCP**  
   handoff (log_handoff, detect_agent), filesystem, git, pubmed, pdf – konfiguracija u .cursor/mcp.json.

8. **Reporting i writing**  
   reporting-*.mdc (STROBE, CONSORT, PRISMA, TRIPOD+AI, STARD, CARE, SPIRIT, SQUIRE, CHEERS), writing-avoid-ai, writing-manuscript-structure.

9. **.agent kao kontekst**  
   .agent/README.md kao obvezno „read-first“ s tablicom task/, system/, SOPs/, MEMORY.md, handoff_log, dreaming, 30_system/04_documentation/context.

10. **Testovi**  
    testovi za brain_health, context_sync, skill_registry, handoff_log – korisno za regresiju.

---

## Prijedlozi poboljšanja

### Visoki prioritet

1. **Uskladiti putanje agent auto-detection u behavior_rules**  
   U `30_system/behavior_rules/15_agent_roles.md` (linije 57–58) stoji:
   - `.ai/agent_auto_detection.R` i `.ai/agent_auto_detection.py`  
   Stvarna lokacija: `30_system/behavior_rules/tools/agents/agent_auto_detection.R` i `.py`.  
   **Akcija:** Zamijeniti u 15_agent_roles.md s `30_system/behavior_rules/tools/agents/agent_auto_detection.R` i `30_system/behavior_rules/tools/agents/agent_auto_detection.py`.

2. **Jedno mjesto za .ai vs. .agent**  
   README naglašava `.ai/` za setup; INDEX i .agent/ za kontekst. Nema jedne kratke definicije: što je .ai (setup, init, detect_study_type), što je .agent (kontekst, task, MEMORY, handoff).  
   **Akcija:** U README u odjeljku „Project structure“ ili na početku dodati 2–3 rečenice: npr. „.agent/ je indeks konteksta agenta (task, MEMORY, handoff). .ai/ sadrži skripte za inicijalizaciju projekta i detekciju tipa studije.“

3. **Putanje brain skripti kada je brain u drugom projektu**  
   Orchestrator i Brain Commands navode `python 40_operations/scripts/brain_status.py` itd. Kada je agent-rules kopiran kao podfolder u drugi projekt, skripte su u `agent-rules/40_operations/scripts/`.  
   **Akcija:** U `00_orchestrator_agent.mdc` u tablici Brain Commands dodati napomenu: „Ako je agent-rules podfolder u projektu, pokrenuti npr. `python agent-rules/40_operations/scripts/brain_status.py` (ili iz direktorija agent-rules: `python 40_operations/scripts/brain_status.py`).“ Isto eventualno u 40_operations/scripts/README.md.

### Srednji prioritet

4. **VERSION.md i CHANGELOG.md u behavior_rules**  
   Brojni unosi i dalje referenciraju `.ai/` za writing/agent alate (npr. agent_auto_detection, writing_workflow).  
   **Akcija:** U VERSION.md i CHANGELOG.md zamijeniti stare putanje s `30_system/behavior_rules/tools/` (ili dodati napomenu „tools moved to 30_system/behavior_rules/tools“ na vrhu).

5. **Quality validation (Python)**  
   Swiss Cheese i self-assessment u `40_operations/python/quality_validation/`; R samo za statistiku. Vidi `CANONICAL_PATHS.md`.

6. **Jedinstvenost putanja u .cursor**  
   Pojavljuju se i `.cursor/rules/` i `.cursor\rules\` (npr. u glob rezultatima).  
   **Akcija:** U dokumentima i pravilima dosljedno koristiti forward slash; za skripte koje grade putanje koristiti `pathlib` ili `os.path.join` da bude neovisno o OS-u.

### Niski prioritet

7. **README – requirements.txt**  
   README kaže „pip install -r requirements.txt“ bez naznake direktorija.  
   **Akcija:** Dodati: „(s korijena projekta, gdje se nalazi requirements.txt).“

8. **Broj unosa u 99_error_memory**  
   Pravilo kaže „Max entries per category: 10“.  
   **Akcija:** Povremeno pregledati broj unosa po kategoriji i trimati ako prelazi 10.

9. **Skill evals**  
   30_system/SKILLS/evals/ sadrži JSON outpute i README.  
   **Akcija:** U 30_system/SKILLS/evals/README.md kratko opisati kako se pokreće evaluacija (npr. koja skripta, iz kojeg direktorija) da novi suradnici mogu reproducirati.

---

## Zaključak

Workspace je **spremnan za produkcijsku uporabu** s ocjenom **84/100**. Najveći doprinos daju: tier sustav, orchestrator, registry vještina, verification i learning loop. Implementacijom visokoprioritetnih izmjena (stvarne putanje agent_auto_detection, jasno .ai vs. .agent, putanje brain skripti u ugniježdenom projektu) konzistentnost i korisnička iskustvo će porasti bez promjene arhitekture.

## Semantic graph (auto)

- [[Behavior rules hub]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[README]]
- [[Skill registry]]
- [[skills-auto-detect]]
- [[Error learning protocol]]
- [[Behavior rules hub]]
