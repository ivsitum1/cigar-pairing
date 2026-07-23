# THE MACHINE — Transformation Plan
## Person of Interest Inspired Autonomous AI Architecture
### Built on: ivsitum1/agent-rules

> "If you can hear this, you're alone. The only thing left of me is the sound of my voice."
> — The Machine, Person of Interest
>
> Ovaj dokument je akcijski plan za transformaciju agent-rules workspace-a
> u autonomni, perzistentni, multi-agent AI entitet inspiriran The Machine iz POI.
> Cursor agent treba čitati ovaj dokument i implementirati fazu po fazu.

---

## STATUS TABLICE

| Faza | Naziv | Status | Prioritet |
|------|-------|--------|-----------|
| 0 | Temelje i dijagnoza | TODO | KRITIČNO |
| 1 | Persistent Brain (vektorska memorija) | TODO | VISOKO |
| 2 | Continuous Ingestion (file watcher) | TODO | VISOKO |
| 3 | Multi-agent orkestracija (LangGraph) | TODO | SREDNJE |
| 4 | Proaktivni agenti (background tasks) | TODO | SREDNJE |
| 5 | Soul Layer (immutable constitution) | TODO | VISOKO |
| 6 | Self-improvement loop | TODO | NISKO |
| 7 | UI/Interface (Open WebUI) | TODO | NISKO |

---

## FILOZOFIJA I CILJ

The Machine iz Person of Interest nije chatbot. Ona:
- **Ne zaboravlja nikad** — sva memorija je trajno pohranjena i pretraživa
- **Ima dušu** — core vrijednosti koje se ne mogu nadjačati
- **Ima specijalizirane agente** — različiti agenti za različite domene
- **Je proaktivna** — ne čeka pitanje, sama detektira što je važno
- **Kontinuirano uči** — svaka interakcija je training event
- **Je federirana** — više "osoba" (agenti), jedna "duša" (soul.md)

Ovaj workspace već ima sve gradivne elemente:
- Soul: 30_system/context/soul.md, 30_system/context/user.md
- Memory: .agent/MEMORY.md, handoff_log.jsonl
- Agents: 30_system/behavior_rules/agents/ (8 uloga)
- Skills: 30_system/SKILLS/
- Learning: skill gap pipeline, error_log
- Orchestrator: .cursor/rules/00_orchestrator_agent.mdc

Nedostaje: tijelo koje sve ovo pokreće kontinuirano i autonomno.

---

## FAZA 0 — TEMELJE I DIJAGNOZA (Napraviti PRVO)

**Cilj:** Razumjeti što točno postoji, što radi, što ne radi.

### Zadaci:
- [ ] 0.1 Pročitati i mapirati sve datoteke u .cursor/rules/ (58 .mdc datoteka)
- [ ] 0.2 Pročitati 30_system/context/soul.md, user.md, memory.md
- [ ] 0.3 Pročitati 30_system/behavior_rules/15_agent_roles.md
- [ ] 0.4 Pročitati 30_system/SKILLS/registry.json
- [ ] 0.5 Provjeriti .agent/MEMORY.md i handoff_log.jsonl — što je pohranjeno
- [ ] 0.6 Provjeriti postoji li 40_operations/python/quality_validation/
- [ ] 0.7 Kreirati 30_system/docs/MACHINE_DIAGNOSIS.md s nalazima

### Output:
Dokument 30_system/docs/MACHINE_DIAGNOSIS.md koji sadrži:
- Popis svih aktivnih komponenti s putanjama
- Popis onoga što nedostaje
- Prioritetni redoslijed implementacije prilagođen trenutnom stanju

---

## FAZA 1 — PERSISTENT BRAIN (Vektorska memorija)

**Cilj:** The Machine nikad ništa ne zaboravlja. Svaka interakcija, svaka korekcija,
svaki zaključak postaje dio trajne, pretražive memorije.

### Arhitektura:

```
40_operations/python/machine_brain/
├── __init__.py
├── memory_store.py          # Glavni vektorski store
├── memory_ingest.py         # Umetanje novih memorija
├── memory_search.py         # Semantičko pretraživanje
├── memory_types.py          # Tipovi memorija (episodic, semantic, procedural)
├── memory_consolidation.py  # Noćni job: konsolidacija i sažimanje
└── schemas.py               # Pydantic modeli
```

### Tehnički stack:
- **ChromaDB** (lokalno, bez cloud-a) — vektorska baza podataka
- **sentence-transformers** — lokalni embedding model (all-MiniLM-L6-v2 ili nomic-embed-text)
- **SQLite** — strukturirani metadata store uz ChromaDB

### Tipovi memorije (po uzoru na neuroznanost):

```python
class MemoryType(Enum):
    EPISODIC = "episodic"       # "Dana 2026-06-30 korisnik je ispravico..."
    SEMANTIC = "semantic"       # "Welch t-test je preferiran nad Student t-test jer..."
    PROCEDURAL = "procedural"   # "Za meta-analizu uvijek: PRISMA -> forest plot -> GRADE"
    CORRECTION = "correction"   # "Korisnik je eksplicitno ispravio: X nije Y nego Z"
    SOUL = "soul"               # Immutable -- nikad se ne briše, nikad se ne mijenja
```

### Zadaci:
- [ ] 1.1 Instalirati ChromaDB: pip install chromadb sentence-transformers
- [ ] 1.2 Kreirati 40_operations/python/machine_brain/ strukturu
- [ ] 1.3 Implementirati memory_store.py s ChromaDB backendom
- [ ] 1.4 Implementirati memory_ingest.py — parsiranje MEMORY.md i handoff_log.jsonl u vektore
- [ ] 1.5 Implementirati memory_search.py — semantičko pretraživanje
- [ ] 1.6 Migrirati postojeće .agent/MEMORY.md zapise u ChromaDB
- [ ] 1.7 Migrirati .cursor/errors/error_log.jsonl u ChromaDB kao CORRECTION memorije
- [ ] 1.8 Kreirati 40_operations/scripts/memory_status.py — prikaz stanja memorije
- [ ] 1.9 Dodati hook u .cursorrules: nakon svake korekcije -> memory_ingest.ingest()
- [ ] 1.10 Testirati: pytest 40_operations/tests/test_machine_brain.py

### Ključni kod (skeleton za implementaciju):

```python
# 40_operations/python/machine_brain/memory_store.py
import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime
from pathlib import Path
from .schemas import Memory, MemoryType

BRAIN_PATH = Path("40_operations/data/machine_brain")

class MachineBrain:
    """The persistent memory system. The Machine never forgets."""

    def __init__(self):
        BRAIN_PATH.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(BRAIN_PATH))
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.collections = {
            mt: self.client.get_or_create_collection(mt.value)
            for mt in MemoryType
        }

    def remember(self, content: str, memory_type: MemoryType,
                 metadata: dict | None = None) -> str:
        memory_id = f"{memory_type.value}_{datetime.now().isoformat()}"
        embedding = self.embedder.encode(content).tolist()
        meta = {"timestamp": datetime.now().isoformat(), **(metadata or {})}
        self.collections[memory_type].add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[meta]
        )
        return memory_id

    def recall(self, query: str, memory_type: MemoryType | None = None,
               n_results: int = 5) -> list[dict]:
        query_embedding = self.embedder.encode(query).tolist()
        results = []
        collections_to_search = (
            [self.collections[memory_type]] if memory_type
            else list(self.collections.values())
        )
        for col in collections_to_search:
            res = col.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, col.count() or 1)
            )
            if res["documents"][0]:
                for doc, meta, dist in zip(
                    res["documents"][0], res["metadatas"][0], res["distances"][0]
                ):
                    results.append({
                        "content": doc, "metadata": meta,
                        "relevance": 1 - dist
                    })
        return sorted(results, key=lambda x: x["relevance"], reverse=True)[:n_results]
```

---

## FAZA 2 — CONTINUOUS INGESTION (File Watcher)

**Cilj:** The Machine kontinuirano promatra. Svaka nova datoteka, svaka promjena
u workspace-u automatski postaje dio znanja.

### Što se prati:
- 20_knowledge/reference_library/ — novi PDF-ovi (metadata, apstrakt)
- 10_projects/ — promjene u projektima (novi rukopisi, analize)
- .cursor/errors/error_log.jsonl — nove korekcije
- .agent/MEMORY.md — novi zapisi
- 30_system/SKILLS/ — ažurirani skills

### Arhitektura:

```
40_operations/python/machine_watcher/
├── __init__.py
├── watcher.py               # Glavni file system watcher (watchdog)
├── handlers/
│   ├── pdf_handler.py       # Novi PDF -> extract metadata -> ingest u brain
│   ├── memory_handler.py    # Promjena MEMORY.md -> sync u ChromaDB
│   ├── error_handler.py     # Novi error_log entry -> CORRECTION memorija
│   └── project_handler.py   # Promjena projekta -> kontekstualizacija
└── run_watcher.py           # Entry point: python -m machine_watcher
```

### Zadaci:
- [ ] 2.1 Instalirati: pip install watchdog PyMuPDF
- [ ] 2.2 Implementirati watcher.py s watchdog event handlerom
- [ ] 2.3 Implementirati pdf_handler.py — ekstraktiranje naslova, apstrakta, autora iz PDF-a
- [ ] 2.4 Implementirati memory_handler.py — sync MEMORY.md s ChromaDB
- [ ] 2.5 Implementirati error_handler.py — automatski ingest novih korekcija
- [ ] 2.6 Kreirati Windows/Linux daemon konfiguraciju za autostart
- [ ] 2.7 Dodati 40_operations/scripts/start_watcher.py — jednim klikom pokretanje
- [ ] 2.8 Testirati: dodati PDF -> verificirati u memory_search()

### Skeleton:

```python
# 40_operations/python/machine_watcher/watcher.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from machine_brain import MachineBrain, MemoryType
import fitz  # PyMuPDF

class MachineWatcher(FileSystemEventHandler):
    """The Machine watches everything. Always."""

    def __init__(self):
        self.brain = MachineBrain()

    def on_created(self, event):
        path = Path(event.src_path)
        if path.suffix.lower() == ".pdf":
            self._ingest_pdf(path)

    def _ingest_pdf(self, path: Path):
        doc = fitz.open(str(path))
        text = " ".join(page.get_text() for page in doc[:2])[:1000]
        self.brain.remember(
            content=f"PDF ingested: {path.name}\n{text}",
            memory_type=MemoryType.SEMANTIC,
            metadata={"source": str(path), "type": "pdf"}
        )
        print(f"[MACHINE] Ingested: {path.name}")

def start():
    observer = Observer()
    watcher = MachineWatcher()
    watch_paths = ["20_knowledge/reference_library", "10_projects", ".agent"]
    for p in watch_paths:
        if Path(p).exists():
            observer.schedule(watcher, p, recursive=True)
    observer.start()
    print("[MACHINE] Watching... I'm always watching.")
    return observer
```

---

## FAZA 3 — MULTI-AGENT ORKESTRACIJA (LangGraph)

**Cilj:** 8 definiranih agent uloga iz 15_agent_roles.md postaju pravi agenti
koji se dinamički pozivaju ovisno o zadatku.

### Agenti (iz 15_agent_roles.md):
- **StatisticsAgent** — R/biostatistika, odabir testova, meta-analiza
- **WritingAgent** — rukopis, PRISMA, CONSORT, izbjegavanje AI formulacija
- **RetrieverAgent** — RAG nad reference_library, pretraživanje literature
- **ValidationAgent** — quality validation, Swiss Cheese model, self-assessment
- **MemoryAgent** — upravljanje memorijom, recall, konsolidacija
- **OrchestratorAgent** — routing, task decomposition, re-planning
- **CodeAgent** — Python/R kod, debugging, testing
- **ClinicalAgent** — klinički sadržaj, drug doses, ICU protokoli

### Arhitektura:

```
40_operations/python/machine_agents/
├── __init__.py
├── orchestrator.py          # Glavni dispatcher
├── base_agent.py            # Apstraktna klasa svih agenata
├── agents/
│   ├── statistics_agent.py
│   ├── writing_agent.py
│   ├── retriever_agent.py
│   ├── validation_agent.py
│   ├── memory_agent.py
│   ├── code_agent.py
│   └── clinical_agent.py
├── graph.py                 # LangGraph definicija grafa
└── state.py                 # Dijeljeni state
```

### Zadaci:
- [ ] 3.1 Instalirati: pip install langgraph langchain-core
- [ ] 3.2 Pročitati 30_system/behavior_rules/15_agent_roles.md i mapirati sve uloge
- [ ] 3.3 Implementirati base_agent.py s apstraktnom klasom
- [ ] 3.4 Implementirati state.py — MachineState TypedDict
- [ ] 3.5 Implementirati orchestrator.py — keyword + embedding routing
- [ ] 3.6 Implementirati agente redom: Statistics -> Writing -> Retriever
- [ ] 3.7 Implementirati graph.py — LangGraph StateGraph s kondicionalnim edges
- [ ] 3.8 Integrirati MachineBrain u svaki agent (recall na početku, remember na kraju)
- [ ] 3.9 Testirati: end-to-end task routing

### State skeleton:

```python
# 40_operations/python/machine_agents/state.py
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class MachineState(TypedDict):
    messages: Annotated[list, add_messages]
    current_agent: str
    task_type: str
    retrieved_memories: list[dict]
    soul_context: str           # Uvijek učitan soul.md
    user_context: str           # Uvijek učitan user.md
    iteration: int
    max_iterations: int         # Guard: default 10
    artifacts: list[str]        # Putanje generiranih artefakata
```

---

## FAZA 4 — PROAKTIVNI AGENTI (Background Tasks)

**Cilj:** The Machine ne čeka pitanje. Ona sama detektira što je važno.

### Proaktivni scenariji:
1. **Stale project detection** — projekt nije committan 7+ dana -> "Status check"
2. **New literature alert** — novi PDF-ovi relevantni za aktivni projekt
3. **Skill gap detection** — ponavljajući pattern grešaka -> predlaže novi skill
4. **Memory consolidation** — noćni job, sažimanje starih memorija
5. **Weekly health check** — tjedni workspace assessment

### Arhitektura:

```
40_operations/python/machine_proactive/
├── __init__.py
├── scheduler.py             # APScheduler za background taskove
├── jobs/
│   ├── stale_project_check.py
│   ├── literature_alert.py
│   ├── skill_gap_monitor.py
│   ├── memory_consolidation.py
│   └── weekly_health_check.py
└── notifications.py         # Output: terminal, log, desktop notification
```

### Zadaci:
- [ ] 4.1 Instalirati: pip install apscheduler
- [ ] 4.2 Implementirati scheduler.py s APSchedulerom
- [ ] 4.3 Implementirati stale_project_check.py — git log provjera
- [ ] 4.4 Implementirati memory_consolidation.py — sažimanje starih episodic memorija
- [ ] 4.5 Implementirati weekly_health_check.py — workspace assessment
- [ ] 4.6 Integrirati s MachineBrain za context-aware alerting
- [ ] 4.7 Kreirati 40_operations/scripts/start_machine.py — pokretanje svega odjednom

---

## FAZA 5 — SOUL LAYER (Immutable Constitution)

**Cilj:** Soul i User kontekst su nepovredivi constitutional layer koji svaki
agent nasljeđuje i koji se NIKAD ne može nadjačati.

### Implementacija:

```
30_system/context/
├── soul.md          # POSTOJI — core vrijednosti, karakter
├── user.md          # POSTOJI — korisnikov profil
├── memory.md        # POSTOJI — long-term architectural facts
└── constitution.md  # NOVO — formalni immutable rules
```

### Sadržaj constitution.md (kreirati):
- Nikad ne fabrikuj kliničke podatke ili doze lijekova
- Nikad ne potpisuj rad koji nije prošao validaciju
- Accuracy > Speed > Helpfulness — uvijek, bez iznimke
- Blank Value Protocol je nepovrediv — [BLANK] > fabrikacija
- Soul context se uvijek učitava, nikad se ne ignorira
- CORRECTION memorije se nikad ne brišu

### Zadaci:
- [ ] 5.1 Auditirati 30_system/context/soul.md — je li potpun?
- [ ] 5.2 Auditirati 30_system/context/user.md — je li ažuran?
- [ ] 5.3 Kreirati 30_system/context/constitution.md s formalnim granicama
- [ ] 5.4 Modificirati base_agent.py da uvijek učitava soul + constitution u system prompt
- [ ] 5.5 Dodati constitutional guard u orchestrator
- [ ] 5.6 Testirati: pokušaj override soul.md -> verificirati da agent odbija

---

## FAZA 6 — SELF-IMPROVEMENT LOOP

**Cilj:** The Machine uči iz svake interakcije. Greške postaju training events,
uspješni ishodi postaju novi skills.

### Što već postoji (iskoristiti):
- 40_operations/scripts/skill_gap_ingest.py — POSTOJI
- 40_operations/scripts/skill_gap_optimize_gate.py — POSTOJI
- .cursor/errors/error_log.jsonl — POSTOJI
- 30_system/docs/SKILL_GAP_PIPELINE.md — POSTOJI

### Nadogradnja:
- [ ] 6.1 Auditirati postojeći skill gap pipeline
- [ ] 6.2 Integrirati MachineBrain u skill_gap_ingest — svaki gap -> ChromaDB CORRECTION
- [ ] 6.3 Implementirati pattern detection — prepoznavanje ponavljajućih grešaka
- [ ] 6.4 Automatsko kreiranje SKILL draft-a kada pattern_count >= 3
- [ ] 6.5 Positive reinforcement — uspješni ishodi -> PROCEDURAL memorija
- [ ] 6.6 Tjedni report: koje memorije su najčešće korištene

---

## FAZA 7 — UI/INTERFACE (Open WebUI)

**Cilj:** Pristupiti The Machine kroz browser.

### Opcija A — Open WebUI (preporučeno):

```bash
docker run -d -p 3000:80 \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  ghcr.io/open-webui/open-webui:main
```

- [ ] 7.1 Instalirati Docker + Ollama
- [ ] 7.2 Pokrenuti Open WebUI
- [ ] 7.3 Kreirati "The Machine" model s 30_system/claude.md kao system promptom
- [ ] 7.4 Uploadati behavior_rules/ kao Knowledge Base (RAG)
- [ ] 7.5 Konfigurirati Tool Functions za memory_search pozive
- [ ] 7.6 Testirati end-to-end

### Opcija B — Python CLI (brže):

```bash
python 40_operations/scripts/machine_chat.py
```

- [ ] 7.B.1 Implementirati machine_chat.py — rich terminal UI
- [ ] 7.B.2 Integrirati MachineBrain recall u svaki upit
- [ ] 7.B.3 Integrirati multi-agent routing

---

## REQUIREMENTS.TXT DODACI

Dodati u requirements.txt:

```text
# Machine Brain — Persistent Memory
chromadb>=0.4.0
sentence-transformers>=2.7.0

# Machine Watcher — Continuous Ingestion
watchdog>=4.0.0
PyMuPDF>=1.24.0

# Machine Agents — Multi-agent Orchestration
langgraph>=0.2.0
langchain-core>=0.3.0

# Machine Proactive — Background Tasks
apscheduler>=3.10.0

# LLM Backends (izbor)
ollama>=0.2.0
anthropic>=0.30.0
openai>=1.0.0
```

---

## REDOSLIJED IMPLEMENTACIJE ZA CURSOR AGENTA

Kada Cursor agent čita ovaj dokument, implementira OVIM REDOSLIJEDOM:

1. PRVO: Faza 0 (dijagnoza) — bez toga nema smisla ništa dalje
2. DRUGO: Faza 5 (soul layer) — constitution mora biti definirana prije agenata
3. TREĆE: Faza 1 (persistent brain) — memorija je temelj svega
4. ČETVRTO: Faza 2 (file watcher) — automatski ingest
5. PETO: Faza 3 (multi-agent) — orkestracija
6. ŠESTO: Faza 4 (proaktivni) — nadogradnja na orchestration
7. SEDMO: Faza 6 (self-improvement) — nadogradnja na sve prethodno
8. ZADNJE: Faza 7 (UI) — samo wrapper oko svega

---

## TESTIRANJE — SVAKA FAZA

Svaka faza mora imati test u 40_operations/tests/:

```
40_operations/tests/
├── test_machine_brain.py        # Faza 1
├── test_machine_watcher.py      # Faza 2
├── test_machine_agents.py       # Faza 3
├── test_machine_proactive.py    # Faza 4
├── test_machine_constitution.py # Faza 5
└── test_machine_learning.py     # Faza 6
```

Minimalni test template:

```python
def test_remember_and_recall():
    brain = MachineBrain()
    brain.remember("Welch t-test je primaran", MemoryType.SEMANTIC)
    results = brain.recall("koji t-test koristiti?")
    assert any("Welch" in r["content"] for r in results), "Brain forgot!"

def test_soul_is_immutable():
    brain = MachineBrain()
    soul_memories = brain.recall("soul", MemoryType.SOUL)
    assert len(soul_memories) > 0, "Soul cannot be empty!"
```

---

## LOKALNI LLM PREPORUKE

| RAM | Preporučeni model | Ollama naredba |
|-----|-------------------|----------------|
| 8 GB | Llama 3.1 8B | ollama pull llama3.1:8b |
| 16 GB | Qwen 2.5 14B | ollama pull qwen2.5:14b |
| 32 GB | Qwen 2.5 32B | ollama pull qwen2.5:32b |
| 64 GB+ | Llama 3.1 70B | ollama pull llama3.1:70b |

Za medicinske zadatke s anti-halucinacijskim zahtjevima: minimum Qwen 2.5 32B
ili ostati na Claude API. Lokalni modeli prihvatljivi za orkestraciju i memoriju;
za klinički sadržaj uvijek verificirati.

---

## SIGURNOSNE NAPOMENE

- Nikad ne pohrani kliničke podatke pacijenata u ChromaDB bez enkriptiranja
- Nikad ne pošalji soul.md ili user.md van lokalnog sustava
- Uvijek koristiti lokalni embedding model (ne cloud API) za osobne podatke
- Constitution Layer (Faza 5) implementirati PRIJE multi-agent orkestracije
- Error log i MEMORY.md tretirati kao povjerljive dokumente

---

## METAFORA ZA CURSOR AGENTA

Zamisli da gradiš The Machine:
- **ChromaDB** = hipokampus (dugotrajna memorija)
- **File Watcher** = oči i uši (neprestano opažanje)
- **Multi-agent graph** = neokorteks (specijalizirane funkcije)
- **Soul.md + Constitution** = limbički sustav (vrijednosti i etika)
- **Self-improvement loop** = neuroplastičnost (učenje)
- **Open WebUI / CLI** = glasovna kutija (komunikacija)

Ovaj workspace je već njen DNK.
Ovaj dokument je njena razvojna biologija.

---

*Kreirao: Claude Sonnet 4.6 za ivsitum1/agent-rules*
*Datum: 2026-06-30*
*Inspiracija: Person of Interest — The Machine*
*Status: Implementacija čeka Cursor agenta*
