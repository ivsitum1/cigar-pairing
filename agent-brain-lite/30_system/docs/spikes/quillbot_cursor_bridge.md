# Spike: QuillBot ↔ Cursor bridge (AI Detector)

**Scope:** AI Detector only — not paraphraser automation.  
**Account:** User-paid session (local Playwright profile). **Do not commit credentials.**  
**Policy:** [HUM-3](../../.agent/task/HUM-3_human_gate.md) — advisory QA, not acceptance gate.

## Why Playwright

QuillBot has [no official public API](https://help.quillbot.com/). Paid features (e.g. [bulk file upload on AI Detector](https://help.quillbot.com/hc/en-us/articles/35295733817111)) require an authenticated browser session.

## One-time auth (pick one)

### A — `import-chrome` (recommended if login window fails)

QuillBot often blocks Playwright's isolated profile (Google OAuth / bot detection). Use cookies from your normal Chrome:

```powershell
# 1. Close ALL Chrome windows
pip install browser_cookie3
python 40_operations/scripts/quillbot_bridge.py import-chrome
python 40_operations/scripts/quillbot_bridge.py check-auth
```

### B — `sync-cdp` (recommended on Windows)

On Windows, `--remote-debugging-port` is **ignored** if Chrome is already running. Use the helper:

```powershell
python 40_operations/scripts/quillbot_bridge.py start-chrome-debug
# Chrome opens on quillbot.com — sign in with your paid account
python 40_operations/scripts/quillbot_bridge.py sync-cdp
python 40_operations/scripts/quillbot_bridge.py check-auth
```

Manual equivalent (must have **zero** `chrome.exe` processes first):

```powershell
taskkill /F /IM chrome.exe /T
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --user-data-dir="$env:LOCALAPPDATA\Google\Chrome\User Data" `
  https://quillbot.com/ai-content-detector
python 40_operations/scripts/quillbot_bridge.py sync-cdp
```

If `sync-cdp` says `authenticated=false`, you are not signed in on **that** Chrome window — log in there, then re-run `sync-cdp`.

### C — `login` (isolated profile; often blocked)

Headed Playwright window with stealth flags — fallback only.

## Scripts

| Command | Purpose |
|---------|---------|
| `python 40_operations/scripts/quillbot_bridge.py start-chrome-debug` | Kill Chrome + restart with CDP port 9222 (Windows) |
| `python 40_operations/scripts/quillbot_bridge.py sync-cdp` | Copy session from debug Chrome → `~/.quillbot/` |
| `python 40_operations/scripts/quillbot_bridge.py check-auth` | Session OK? |
| `python 40_operations/scripts/quillbot_bridge.py detect --file path.md --json` | Scan ≥80 words |

**URL:** [AI Content Detector](https://quillbot.com/ai-content-detector)

## Env (optional)

| Variable | Default |
|----------|---------|
| `QUILLBOT_HOME` | `~/.quillbot` |
| `QUILLBOT_PROFILE_DIR` | `~/.quillbot/profiles/default/browser_profile` |
| `QUILLBOT_DETECTOR_URL` | `https://quillbot.com/ai-content-detector` |

## Cursor workflow

1. `ai_pattern_scan.py` (local structural)
2. `quillbot_bridge.py detect` (external advisory %)
3. Agent suggests paragraph-level edits per `writing-avoid-ai.mdc` — **no** auto-paraphrase loop

## Phase 2 (optional)

- Premium batch upload (20 files) via Playwright `set_input_files`
- Hook in `check_ai_plagiarism.py --tools quillbot`
- MCP wrapper (human approval per MCP governance)

## Risks

- UI selector drift → use `--headed` to debug; update `_parse_results` in bridge
- False positives on human text (known detector limitation)
