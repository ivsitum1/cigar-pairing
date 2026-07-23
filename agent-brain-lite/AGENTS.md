# Agent Brain Lite — writing-only (cigar_and_rum)

Profil za **pisanje** popularne literature (bonton, lifestyle). Znanstveni research stack je isključen.

## Setup

```powershell
# Parent path (already set in .env)
PARENT_BRAIN_PATH=C:\Users\Admin\Documents\agent rules
python scripts/link_parent.py --parent "$env:PARENT_BRAIN_PATH"
```

## Prvo pročitaj

1. `.agent/MEMORY.md` (korijen projekta)
2. `hot.md` / `index.md` (lite wiki)
3. `nodes/00_orchestrator.md` + `.cursor/rules/00_orchestrator.mdc`
4. Skills: `30_system/SKILLS/SKILL_nonacademic-writer.md`

## Čvorovi

| Čvor | Uloga u ovom projektu |
|------|------------------------|
| Orchestrator | Klasifikacija; default WRITER |
| Admin | organizacija, checklista |
| Writer | draftovi, stil, hrvatski pravopis |
| Automation | skripte / app |
| Research | samo brzi lookup — **ne** SR/meta-analiza |

## Hard stops

Nema: scholarly_workflow, reporting-* checklisti, statistics-test-selection, books-rag research pipeline, parent scientific orchestrator.
