# MCP (Model Context Protocol) – Enabling

The repository contains `.cursor/mcp.json` with server definitions. For Cursor to actually use them, the configuration must be enabled in Cursor's MCP setup.

---

## Option A: Project MCP (Cursor 0.43+)

If Cursor automatically loads MCP from the project:

1. Open the project (root where `.cursor/mcp.json` is) in Cursor.
2. In **Settings → Features → MCP** (or **Cursor Settings → MCP**) check that "Use project MCP config" or similar is enabled.
3. If there is **MCP** in the status bar or in settings, you should see the servers from `.cursor/mcp.json`.

---

## Option B: Global MCP config (user-level)

Cursor often reads the global MCP config from the user directory:

- **Windows:** `%APPDATA%\Cursor\mcp.json` or `~/.cursor/mcp.json`
- **macOS/Linux:** `~/.cursor/mcp.json`

**Enabling project mcp.json:**

1. Open `.cursor/mcp.json` in this repo.
2. Open your global MCP config (e.g. `%APPDATA%\Cursor\mcp.json` on Windows). If it does not exist, create it.
3. Copy the entire content from `.cursor/mcp.json` into `mcpServers` in the global config (or merge manually if you already have other servers).

**Example (only relevant section in global mcp.json):**

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-filesystem", "--root", "C:\\path\\to\\your\\project"],
      "description": "Access project files"
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-git"],
      "description": "Git operations"
    },
    "pubmed": {
      "command": "python",
      "args": [".cursor/mcp_servers/pubmed_server.py"],
      "env": {
        "NCBI_API_KEY": "your_api_key",
        "NCBI_EMAIL": "your@email.com"
      },
      "description": "PubMed search (local FastMCP server)"
    }
  }
}
```

For **filesystem** replace `--root` with the absolute path to your project if using global config. For **pubmed** set `NCBI_API_KEY` (free at NCBI) and `NCBI_EMAIL` (recommended by NCBI). Requires `pip install -r .cursor/mcp_servers/requirements.txt` for `fastmcp`.

4. Restart Cursor. In **Tools / MCP** the servers should be visible.

---

## Servers in this repo

| Server    | Purpose                     | Note                          |
|-----------|-----------------------------|-------------------------------|
| filesystem| File access                 | `--root` = project path       |
| git       | Git commands                | npx package                   |
| pubmed    | Literature search           | Local Python server; `pip install -r .cursor/mcp_servers/requirements.txt`; optional `NCBI_API_KEY` + `NCBI_EMAIL` |
| handoff   | Handoff log; detect_agent for classification | `pip install fastmcp`; workspace root must contain .cursor/ |
| memory    | Persistent memory retrieval (`search`, `timeline`, `get_observations`) + injection | `pip install fastmcp`; uses `.agent/memory/memory.db` |
| pdf       | Text extraction from PDFs   | npx @sylphx/pdf-reader-mcp    |
| latex     | Create/edit/validate/compile LaTeX locally | Python; MiKTeX or TeX Live; `pip install -r .cursor/mcp_servers/requirements.txt` |
| overleaf  | Overleaf pull/push, lint, compile (optional) | `uvx overleaf-mcp`; set `OVERLEAF_PROJECT_ROOT`; one-time `ols login` via [overleaf-sync](https://pypi.org/project/overleaf-sync/) |

### LaTeX MCP setup (Windows)

1. Install **MiKTeX** or **TeX Live** (for `pdflatex` / `latexmk`).
2. From repo root: `pip install -r .cursor/mcp_servers/requirements.txt`
3. Enable MCP in Cursor; confirm **latex** server appears under Tools.
4. **Optional Overleaf:** `pipx install overleaf-sync` (or `uv tool install overleaf-sync`), then in your LaTeX project folder run `ols login`. Set `OVERLEAF_PROJECT_ROOT` in `.cursor/mcp.json` to that folder.

**Optional npm compiler** (alternative to local `latex` MCP): `npm install -g latexpdf-mcp` — see import at `90_archive/imports/latex_mcp_skills_2026-05/LateXPDF-MCP-main/`.

Skills: `latex-document`, `latex-compile`, `journal-production`, `journal-cover-design` in `30_system/SKILLS/`.

---

## R Execution (experimental)

For executing R code via MCP there is no npx package. Use R package `mcptools`:

1. Install in R: `install.packages("mcptools")` or `pak::pkg_install("posit-dev/mcptools")`
2. Add to mcp.json:
```json
"r-execution": {
  "command": "Rscript",
  "args": ["-e", "mcptools::mcp_server()"],
  "description": "Execute R code (requires mcptools)"
}
```
3. Restart Cursor.

---

## Handoff MCP

Logs handoffs between subagents to `.agent/handoff_log.jsonl`. Also exposes `detect_agent` tool for low-confidence task classification. Prerequisite:

```bash
pip install fastmcp
```

**Workspace path:** Handoff server expects workspace root to contain `.cursor/`. If agent-rules is a subfolder of your project, ensure Cursor is opened at the folder that contains `.cursor/mcp_servers/` (or set `WORKSPACE_ROOT` env).

If handoff MCP is not active, agent uses fallback: `python .cursor/40_operations/scripts/handoff_log.py append --from X --to Y --done "..." --next "..." --context "..."`

---

## PDF Extraction (optional)

For systematic review – text extraction from PDFs. Options:

- **@sylphx/pdf-reader-mcp** (recommended): `npx -y @sylphx/pdf-reader-mcp` – parallel processing, layout preservation
- **@iflow-mcp/pdftotext-mcp**: requires poppler-utils (pdftotext)

Add to mcp.json:
```json
"pdf": {
  "command": "npx",
  "args": ["-y", "@sylphx/pdf-reader-mcp"],
  "description": "Extract text from PDFs"
}
```

---

## Setup script (Windows)

`.\40_operations/scripts\setup_mcp.ps1` – copies project MCP config to global Cursor config, sets filesystem --root to absolute path.

---

## Verification

In Cursor chat: if MCP is enabled, tools description should show e.g. "filesystem" or "git" (depending on Cursor version). If you do not see MCP tools, check Cursor documentation for your version: [Cursor MCP](https://docs.cursor.com/context/model-context-protocol).

## Related Hubs

- [Folder index hub](FOLDER_INDEX.md)
- [All notes index](ALL_NOTES_INDEX.md)
- [Graph connectivity map](GRAPH_CONNECTIVITY_MAP.md)
