# NotebookLM MCP — setup za pristup notebookovima

_Generirana referenca: 2026-07-17_

## Zašto MCP

Agent ne može čitati NotebookLM share-linkove bez Google autentifikacije.
S MCP serverom agent dobiva programatički pristup: lista notebookove,
dodaje izvore, postavlja pitanja (s citatima), i generira studio artefakte
(audio, quiz, study guide).

## Dvije opcije

### Opcija A: `notebooklm-mcp-cli` (jacob-bd) — preporučeno

**Repo:** <https://github.com/jacob-bd/notebooklm-mcp>
**PyPI:** `notebooklm-mcp-cli` (v0.8.7, 2026-07-15)
**Zvjezdice:** 5 464 | **Licencija:** MIT

Instalacija:

```bash
uv tool install notebooklm-mcp-cli
# ili: pip install notebooklm-mcp-cli
# ili: pipx install notebooklm-mcp-cli
```

Autentifikacija (jednokratno, treba Chrome):

```bash
nlm login
```

Setup za Cursor:

```bash
nlm setup add cursor
```

Ovo generira JSON blok za `~/.cursor/mcp.json` ili `.cursor/mcp.json`.
Alternativno, ručno dodaj:

```json
{
  "mcpServers": {
    "notebooklm-mcp": {
      "command": "notebooklm-mcp",
      "args": []
    }
  }
}
```

Provjera:

```bash
nlm notebook list
```

#### Dostupni MCP alati

| MCP tool | Opis |
|---|---|
| `notebook_list` | Lista svih notebookova |
| `notebook_create` | Kreiraj novi notebook |
| `source_add` | Dodaj izvor (URL, tekst, Drive, file) |
| `notebook_query` | Postavi pitanje notebooku (odgovor s citatima) |
| `studio_create` | Generiraj audio/video/quiz/flashcards/study guide |
| `download_artifact` | Preuzmi generirani artefakt |
| `research_start` | Web/Drive research i auto-import izvora |
| `notebook_share_*` | Dijeli notebook |
| `source_sync_drive` | Sinkroniziraj Drive izvore |
| `cross_notebook_query` | Pitanje kroz više notebookova |
| `batch` | Batch operacije |
| `pipeline` | Multi-step workflow |
| `tag` | Tagiranje i smart select |

### Opcija B: `notebooklm-mcp` (PleasePrompto/mulyg)

**Repo:** <https://github.com/mulyg/notebooklm-mcp>
**npm:** `notebooklm-mcp`

```bash
npx notebooklm-mcp@latest
```

Za Cursor, dodaj u `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "npx",
      "args": ["notebooklm-mcp@latest"]
    }
  }
}
```

24 alata uključujući `notebooklm_ask`, `notebooklm_list_notebooks`,
`notebooklm_add_url_source`, `notebooklm_generate_audio`, itd.

## Važne napomene

- Google nema službeni NotebookLM API. Oba MCP servera koriste browser
  automatizaciju (reverse-engineering web sučelja).
- Potreban je Chrome za prvi login.
- Nakon autentifikacije, server radi headless iz spremljenog profila.
- Ovo je za osobnu upotrebu, ne za produkciju.
- **Cloud agenti** (poput ovog) ne mogu pokrenuti Chrome za login — MCP
  se mora konfigurirati lokalno na Cursor Desktop-u.

## Naši notebookovi

1. <https://notebooklm.google.com/notebook/5b8ae55e-d6bf-4cde-afb2-33492c1b241b>
2. <https://notebooklm.google.com/notebook/2707d3fe-73d1-4879-8e8d-b7538d1cb3f2>

## Workflow s MCP-om

1. Instaliraj `notebooklm-mcp-cli` lokalno.
2. `nlm login` — autentificiraj se u Chrome prozoru.
3. `nlm setup add cursor` — konfigurira Cursor MCP.
4. Pokreni Cursor, otvori chat, koristi NotebookLM alate direktno.
5. `notebook_query` za pitanja s citatima iz naših izvora.
6. `studio_create` za study guide, quiz, audio overview.
7. Exportaj rezultate u `docs/bonton/research/extracts/notebooklm-*.md`.
