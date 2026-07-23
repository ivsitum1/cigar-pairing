# Monthly arXiv skill scout

Scheduled scan of stat / CS / math preprints to propose agent skills. **Not** clinical evidence.

## Scripts and config

| Item | Path |
|------|------|
| CLI | `40_operations/scripts/arxiv_monthly_scan.py` |
| Config | `30_system/config/arxiv_monthly_scan.json` |
| Skill | `30_system/SKILLS/SKILL_arxiv-skill-scout.md` |
| JSON output | `.agent/task/arxiv_scan_YYYY-MM.json` |
| Digest | `.agent/task/arxiv_digest_YYYY-MM.md` |
| Template | `.agent/task/_templates/arxiv_digest_template.md` |

## Manual run

From repo root:

```powershell
py -3 -m pip install arxiv>=2.1.0
py -3 40_operations/scripts/arxiv_monthly_scan.py
py -3 40_operations/scripts/arxiv_monthly_scan.py --month 2026-05
py -3 40_operations/scripts/arxiv_monthly_scan.py --dry-run
py -3 40_operations/scripts/arxiv_self_evolving_scan.py --period monthly
py -3 40_operations/scripts/arxiv_self_evolving_scan.py --period weekly
```

Default month: **previous calendar month**. Respects arXiv rate limit (~3.5 s between requests in config).

**Self-evolving sensor** (same schedule): `arxiv_self_evolving_scan.py` writes
`.agent/task/self_evolving_arxiv_scan_YYYY-MM.json` (monthly) or `_YYYY-WW.json`
(weekly via Machine digest). Flags papers not yet in
`30_system/docs/reference/self_evolving_arxiv_registry.json`.

## Windows Task Scheduler

**Quick install (repo root):**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File 40_operations/scripts/install_arxiv_scheduled_task.ps1
```

Default: task `AgentRules-ArXivSkillScout`, monthly on day **1** at **09:00**, first run **2026-07-01**.

Manual GUI steps:

1. Open **Task Scheduler** → Create Task.
2. **General:** name `AgentRules-ArXivSkillScout`, run whether user is logged on or not (or only when logged on if you prefer OAuth-free CLI).
3. **Triggers:** Monthly, day **1**, time e.g. **09:00**.
4. **Actions:** Start a program (recommended wrapper):  
   - Program: `powershell.exe`  
   - Arguments: `-NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\Documents\agent rules\40_operations\scripts\run_arxiv_monthly_scan.ps1"`  
   - Or one-shot install:  
     `schtasks /Create /TN "AgentRules-ArXivSkillScout" /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"<REPO>\40_operations\scripts\run_arxiv_monthly_scan.ps1\"" /SC MONTHLY /D 1 /ST 09:00 /SD 07/01/2026 /F`
5. **Conditions:** disable “Start only on AC power” if on laptop.
6. After first run, open `.agent/task/arxiv_digest_YYYY-MM.md` in Cursor and review proposals.

Optional: set environment `PYTHONPATH` only if needed; the script resolves repo root from its own path.

## Human gate

Do **not** auto-register skills. User approves proposals in chat; then `create-skill` + eval seed.

## Related

- [[Skill gap pipeline]]
- [[Consensus MCP]] (clinical writing; separate track)
- `30_system/docs/AUTOMATION_INDEX.md`
