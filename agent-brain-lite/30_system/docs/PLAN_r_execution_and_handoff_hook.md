# Plan: R Execution MCP + Handoff Hook

**Datum:** 2025-03-01  
**Cilj:** (1) Privremeno ukloniti ili označiti R execution MCP kao experimental; (2) Kreirati handoff hook da agent automatski logira prelazak između subagenata.

---

## 1. R Execution MCP – Plan

### 1.1 Problem

- `.cursor/mcp.json` koristi `npx -y mcp-r` – **paket `mcp-r` ne postoji na npm**
- R MCP implementacije su R paketi: `mcpr` (opifex), `mcptools` (Posit)
- mcptools se pokreće: `Rscript -e "mcptools::mcp_server()"` – zahtijeva R + instalirani mcptools

### 1.2 Opcije

| Opcija | Akcija | Prednost | Nedostatak |
|--------|--------|----------|------------|
| A | Ukloniti `r-execution` iz mcp.json | Jednostavno, bez grešaka pri startu | Nema R izvršavanja |
| B | Označiti kao experimental, prebaciti na mcptools | R dostupan ako korisnik konfigurira | Kompleksnija postava |
| C | Kreirati wrapper skriptu koja pokreće mcptools | Jednostavniji command u mcp.json | Zahtijeva R i mcptools |

### 1.3 Preporuka: Opcija A + dokumentacija za B

**Faza 1 (sada):**
- Ukloniti `r-execution` iz [.cursor/mcp.json](.cursor/mcp.json)
- U [30_system/docs/MCP_INSTALL.md](30_system/docs/MCP_INSTALL.md) dodati sekciju **"R Execution (experimental)"** s uputama za mcptools:

```markdown
## R Execution (experimental)

Za izvršavanje R koda preko MCP-a, nema npx paketa. Koristi R paket `mcptools`:

1. Instaliraj u R: `install.packages("mcptools")` ili `pak::pkg_install("posit-dev/mcptools")`
2. Dodaj u mcp.json:
   "r-execution": {
     "command": "Rscript",
     "args": ["-e", "mcptools::mcp_server()"],
     "description": "Execute R code (requires mcptools)"
   }
3. Restart Cursor. R session mora biti dostupan.
```

**Faza 2 (opcionalno, kasnije):**
- Kreirati [40_operations/scripts/mcp_r_wrapper.ps1](40_operations/scripts/mcp_r_wrapper.ps1) koji provjerava ima li R i mcptools, pa pokreće `Rscript -e "mcptools::mcp_server()"` – olakšava postavu za Windows korisnike

### 1.4 Datoteke za izmjenu

- [.cursor/mcp.json](.cursor/mcp.json) – ukloniti `r-execution` objekt
- [30_system/docs/MCP_INSTALL.md](30_system/docs/MCP_INSTALL.md) – dodati sekciju R Execution (experimental)

---

## 2. Handoff Hook – Plan

### 2.1 Ograničenje

Cursor nema ugradene hookove za "na AI odgovor" ili "na handoff". Jedini mehanizam je **pravilo koje agent mora slijediti** – ponašajni hook.

### 2.2 Strategija: Pravilo + skripta kao "hook"

Hook = kombinacija:
1. **handoff_log.py** – skripta koja append-a u JSONL; agent je poziva
2. **Obavezno pravilo u orchestratoru** – "Nakon svakog HANDOFF bloka MORATE pokrenuti handoff_log.py"
3. Pravilo "huka" agentovo ponašanje – agent mora izvršiti akciju u istoj poruci kad ispiše HANDOFF

### 2.3 Implementacija

**2.3.1 Kreirati [.cursor/40_operations/scripts/handoff_log.py](.cursor/40_operations/scripts/handoff_log.py)**

```python
#!/usr/bin/env python3
"""Append handoff to .agent/handoff_log.jsonl. Called by agent after each HANDOFF."""
# CLI: handoff_log.py append --from STATISTICS --to WRITING --done "..." --next "..." --context "..."
# Ili: handoff_log.py append --from X --to Y (minimalno)
```

- `append` subcommand s argumentima: `--from`, `--to`, `--done`, `--next`, `--context`
- Validacija: from, to obavezni; done, next, context opcionalni (default "")
- Append u `.agent/handoff_log.jsonl` format: `{"ts":"ISO8601","from":"...","to":"...","done":"...","next":"...","30_system/context":"..."}`
- Workspace root: iz Path(__file__) ili env

**2.3.2 Ažurirati [.cursor/rules/00_orchestrator_agent.mdc](.cursor/rules/00_orchestrator_agent.mdc)**

U sekciji **Handoff (When Chaining)** dodati **HOOK** blok:

```markdown
## Handoff (When Chaining)

[HANDOFF Subagent1 → Subagent2]
Completed: [1 sentence]
Next: [1 sentence]
Context: [≤30 tok]

**HOOK – MANDATORY:** Nakon svakog HANDOFF bloka, u ISTOJ poruci pokreni:
`python .cursor/40_operations/scripts/handoff_log.py append --from Subagent1 --to Subagent2 --done "Completed sentence" --next "Next sentence" --context "Context"`
Zamijeni Subagent1/Subagent2 s pravim imenima (STATISTICS, WRITING, ...). Ne preskači ovaj korak.
```

**2.3.3 Kreirati .agent/handoff_log.jsonl**

- Prazna datoteka ili s jednim komentarom u prvom retku (JSONL ne podržava komentare – ostaviti prazno ili .gitkeep)
- Dodati u .gitignore? Ne – handoff log je koristan za praćenje; commitati ga ili dodati u .gitignore ovisno o preferenciji. Preporuka: ne ignorirati – može biti dio projekta za audit.

**2.3.4 Ažurirati [.agent/README.md](.agent/index.md)**

U tablicu dodati:
| handoff_log.jsonl | Handoff history (from→to, done, next, 30_system/context) | Kad pratimo pipeline tokove |

### 2.4 MCP tool umjesto skripte – Detaljni plan

Za integraciju kroz Cursor MCP (agent poziva tool umjesto terminal naredbe).

---

#### 2.4.1 Arhitektura

```mermaid
flowchart LR
    Agent[Orchestrator Agent]
    MCP[MCP Server: handoff]
    Log[.agent/handoff_log.jsonl]
    Agent -->|"log_handoff tool call"| MCP
    MCP -->|append| Log
```

- Agent ispisuje HANDOFF blok → u istoj poruci poziva MCP tool `log_handoff`
- MCP server prima poziv, append-a u `.agent/handoff_log.jsonl`, vraća potvrdu
- Nema `run_terminal_cmd` – sve ide preko MCP toola

---

#### 2.4.2 Tehnologija

- **FastMCP** (Python): `pip install fastmcp` ili `uv run --with fastmcp`
- STDIO transport (standardno za Cursor)
- Jedan tool: `log_handoff`

---

#### 2.4.3 Struktura datoteka

```
.cursor/
├── mcp.json                          # Dodati "handoff" server
└── mcp_servers/
    ├── handoff_server.py             # MCP server s log_handoff toolom
    └── requirements.txt              # fastmcp
```

---

#### 2.4.4 handoff_server.py – Specifikacija

```python
# .cursor/mcp_servers/handoff_server.py
import os
import json
from datetime import datetime, timezone
from pathlib import Path

# FastMCP: pip install fastmcp
from fastmcp import FastMCP

mcp = FastMCP("Agent Rules Handoff")

@mcp.tool()
def log_handoff(
    from_agent: str,
    to_agent: str,
    done: str = "",
    next_step: str = "",
    context: str = ""
) -> str:
    """
    Log a handoff between subagents. Call this after every [HANDOFF A → B] block.
    from_agent: Source subagent (e.g. STATISTICS, WRITING)
    to_agent: Target subagent
    done: What was completed (1 sentence)
    next_step: What comes next (1 sentence)
    context: Brief context (≤30 tokens)
    """
    # Workspace root: env WORKSPACE_ROOT, else derived from script path
    if os.environ.get("WORKSPACE_ROOT"):
        workspace = Path(os.environ["WORKSPACE_ROOT"]).resolve()
    else:
        workspace = Path(__file__).resolve().parent.parent.parent
    log_path = workspace / ".agent" / "handoff_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "from": from_agent,
        "to": to_agent,
        "done": done[:500] if done else "",
        "next": next_step[:500] if next_step else "",
        "30_system/context": context[:200] if context else ""
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return f"Logged handoff {from_agent} → {to_agent}"

if __name__ == "__main__":
    mcp.run()  # STDIO transport (default za Cursor)
```

- Workspace: `WORKSPACE_ROOT` env (Cursor može postaviti), inače `Path(__file__).resolve().parent.parent.parent` (repo root)
- Validacija: `from_agent`, `to_agent` obavezni; ostalo opcionalno

---

#### 2.4.5 mcp.json konfiguracija

**Opcija A – uv (preporučeno ako je uv instaliran):**

```json
"handoff": {
  "command": "uv",
  "args": [
    "run",
    "--with", "fastmcp",
    "--project", "C:\\path\\to\\agent rules\\.cursor\\mcp_servers",
    "fastmcp", "run", "handoff_server.py"
  ],
  "env": {
    "WORKSPACE_ROOT": "C:\\path\\to\\agent rules"
  },
  "description": "Log handoffs between subagents"
}
```

**Opcija B – python (ako nema uv):**

```json
"handoff": {
  "command": "python",
  "args": [
    ".cursor/mcp_servers/handoff_server.py"
  ],
  "cwd": "C:\\path\\to\\agent rules",
  "env": {
    "WORKSPACE_ROOT": "C:\\path\\to\\agent rules"
  },
  "description": "Log handoffs between subagents"
}
```

Napomena: `cwd` nije standardno polje u mcp.json; Cursor ga možda ne podržava. Alternativa: u serveru koristiti relativnu putanju od skripte – `Path(__file__).parent.parent.parent` = workspace root.

**Opcija C – relativna putanja u serveru:**

```python
# U handoff_server.py – workspace = parent of .cursor
_script_dir = Path(__file__).resolve().parent
workspace_root = _script_dir.parent.parent  # .cursor/mcp_servers -> .cursor -> repo root
```

Tada mcp.json može biti:

```json
"handoff": {
  "command": "uv",
  "args": ["run", "--with", "fastmcp", "-C", "C:\\path\\to\\agent rules", "fastmcp", "run", ".cursor/mcp_servers/handoff_server.py"],
  "description": "Log handoffs between subagents"
}
```

Ili s `python`:

```json
"handoff": {
  "command": "python",
  "args": [".cursor/mcp_servers/handoff_server.py"],
  "description": "Log handoffs between subagents"
}
```

Za `python` mora biti cwd = workspace root. Cursor obično pokreće MCP servere s workspace root kao cwd – treba provjeriti.

---

#### 2.4.6 requirements.txt za MCP server

```
# .cursor/mcp_servers/requirements.txt
fastmcp>=2.0.0
```

Ili koristiti `uv run --with fastmcp` bez zasebnog requirements.

---

#### 2.4.7 Orchestrator pravilo (MCP varijanta)

U [.cursor/rules/00_orchestrator_agent.mdc](.cursor/rules/00_orchestrator_agent.mdc):

```markdown
## Handoff (When Chaining)

[HANDOFF Subagent1 → Subagent2]
Completed: [1 sentence]
Next: [1 sentence]
Context: [≤30 tok]

**HOOK – MANDATORY:** Nakon svakog HANDOFF bloka pozovi MCP tool **log_handoff** s parametrima:
- from_agent: ime subagenta koji predaje (npr. STATISTICS)
- to_agent: ime subagenta koji preuzima (npr. WRITING)
- done: sentence from "Completed"
- next_step: sentence from "Next"
- context: tekst iz "Context"

Ako MCP tool handoff nije dostupan, pokreni: `python .cursor/40_operations/scripts/handoff_log.py append --from X --to Y --done "..." --next "..." --context "..."`
```

---

#### 2.4.8 Fallback: handoff_log.py

Zadržati [.cursor/40_operations/scripts/handoff_log.py](.cursor/40_operations/scripts/handoff_log.py) kao fallback kad MCP handoff server nije aktivan (npr. prvi put prije postave).

---

#### 2.4.9 Datoteke za kreiranje/izmjenu (MCP varijanta)

| Akcija | Datoteka |
|--------|----------|
| Create | .cursor/mcp_servers/handoff_server.py |
| Create | .cursor/mcp_servers/requirements.txt (opcionalno) |
| Edit | .cursor/mcp.json – dodati "handoff" server |
| Edit | .cursor/rules/00_orchestrator_agent.mdc |
| Create | .agent/handoff_log.jsonl (prazan) |
| Edit | .agent/README.md |
| Create | .cursor/40_operations/scripts/handoff_log.py (fallback) |
| Edit | 30_system/docs/MCP_INSTALL.md – dodati Handoff MCP |

---

#### 2.4.10 Redoslijed implementacije (MCP)

1. Kreirati `.cursor/mcp_servers/` i `handoff_server.py`
2. Kreirati `handoff_log.py` (fallback)
3. Dodati "handoff" u `.cursor/mcp.json`
4. Ažurirati orchestrator pravilo (MCP + fallback)
5. Kreirati `.agent/handoff_log.jsonl`, ažurirati `.agent/README.md`
6. Dokumentirati u `30_system/docs/MCP_INSTALL.md`

**Procijenjeno vrijeme:** ~1h

### 2.5 Datoteke za kreiranje/izmjenu

| Akcija | Datoteka |
|--------|----------|
| Create | .cursor/40_operations/scripts/handoff_log.py |
| Edit | .cursor/rules/00_orchestrator_agent.mdc |
| Create | .agent/handoff_log.jsonl (prazan) |
| Edit | .agent/README.md |

---

## 3. Redoslijed izvršavanja

### Varijanta A: Handoff skripta (brže)
1. R execution MCP: ukloniti iz mcp.json, ažurirati MCP_INSTALL.md
2. Handoff: kreirati handoff_log.py, ažurirati orchestrator, kreirati handoff_log.jsonl, ažurirati .agent/README.md  
**Vrijeme:** ~30–45 min

### Varijanta B: Handoff MCP tool (preporučeno)
1. R execution MCP: ukloniti iz mcp.json, ažurirati MCP_INSTALL.md
2. Handoff MCP: kreirati handoff_server.py, requirements, dodati u mcp.json
3. Fallback: kreirati handoff_log.py
4. Orchestrator: ažurirati pravilo (MCP tool + fallback)
5. Kreirati handoff_log.jsonl, ažurirati .agent/README.md, MCP_INSTALL.md  
**Vrijeme:** ~1h

### Preduvjeti za MCP
- Python 3.10+ i `pip install fastmcp` (ili `uv`)
- Cursor MCP uključen (Settings → MCP)

## Related Hubs

- [Folder index hub](FOLDER_INDEX.md)
- [All notes index](ALL_NOTES_INDEX.md)
- [Graph connectivity map](GRAPH_CONNECTIVITY_MAP.md)
