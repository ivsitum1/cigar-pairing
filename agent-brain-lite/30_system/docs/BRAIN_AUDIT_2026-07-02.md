# Brain audit + upgrade — 2026-07-02

Analiza "synthetic brain" repoa (`agent-rules`): novosti s interneta, rupe, gdje
je proces pao, i implementirane nadogradnje. Prati plan
`~/.claude/plans/pretra-i-intrenet-za-novosti-recursive-manatee.md`.

## 1. Gdje je proces pao

Sve tjedne automatizacije su **zdrave**: weekly-learning 2026-W27 = ispravan
no-op (svi W29 prijedlozi već implementirani), pytest zelen, git u syncu s
originom, W28 ai_news generiran (30 stavki), `memory.db` aktivan.

**Jedini stvarni kvar:** sesije se pokreću iz **stare OneDrive kopije**
(`C:\Users\Admin\OneDrive\Dokumenti\agent rules`) unatoč ADR-u i markeru
`_STARA_KOPIJA_NE_KORISTITI.md`. `workspace_bootstrap.py` validirao je *symlink
targete* (`stale_onedrive: 0`), ali **ne i gdje je sesija fizički pokrenuta** —
pa je curenje prolazilo nezapaženo. To je korijenski uzrok drifta iz 2026-07.

Ispravljeno u Traci A (vidi §3).

## 2. Novosti (web, srpanj 2026) → mapiranje na repo

| Trend | Izvor | Stanje u repou |
|-------|-------|----------------|
| **"Dreaming"** — idle-time review sesija → plain-text playbooks (Harvey 6× task completion) | [VentureBeat](https://venturebeat.com/technology/anthropic-introduces-dreaming-a-system-that-lets-ai-agents-learn-from-their-own-mistakes), [Anthropic](https://www.anthropic.com/institute/recursive-self-improvement) | weekly-learning postoji; dodani **playbookovi** (Traka C) |
| **Harness engineering** — Agent = Model + Harness; feedback gate hvata korekcije kao pravila | [Faros](https://www.faros.ai/blog/harness-engineering), [awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering) | verifier_bridge / self_harness_proposals ✓ |
| **Brain-inspired memorija** — tipizirane neuro-domene (explicit/implicit/associative) | [Synthius-Mem arXiv](https://arxiv.org/pdf/2604.11563), [mem0 state-of-memory](https://mem0.ai/blog/state-of-ai-agent-memory-2026) | dodan **mem_type** + **staleness pruning** (Traka B) |
| **Agent-Native Immune System / memory poisoning** | arXiv 2606.28270 (u našem W28 ai_news) | dodan **poisoning guard** na ingestu (Traka B) |

## 3. Implementirane nadogradnje

### Traka A — popravak curenja procesa
- `scripts/check_sync.py`: CWD guard — detektira staru kopiju preko markera i
  glasno preusmjerava na živi repo (čita živu putanju iz markera).
- `40_operations/scripts/workspace_bootstrap.py`: novi `check_session_cwd()` →
  polje `session_cwd_onedrive`; audit sad pada ako je sesija u OneDrive kopiji.
- Doc gapovi: `.mdc` count 58 → **60** (`README.md`, `index.md`); README link
  `CLAUDE.md` → `claude.md` (git prati samo `claude.md`; `CLAUDE.md` je artefakt
  case-insensitive Windows FS-a — **nije** stvaran duplikat, brisanje bi obrisalo
  jedini `claude.md`).

### Traka B — memory-engine upgrade (kanonski `memory_engine/`, po ADR-u)
- **Tipizirana memorija:** `models.MEM_TYPES` + `Observation.mem_type`; kolona u
  `store.py` (+ backfill migracija); klasifikator `compression.infer_mem_type`.
- **Staleness pruning:** `config` (`observation_ttl_days`, `prune_min_confidence`),
  `store.prune_stale()` (briše staro **i** nisko-pouzdano; visoka pouzdanost
  preživljava), CLI `40_operations/scripts/memory_prune.py --dry-run`.
- **Poisoning guard:** `compression.is_poisoned()` + karantena na `ingest.py`
  (raw event ostaje za audit; observation se NE kreira → ne može se retrievati
  ni re-injektirati).
- Testovi: `40_operations/tests/memory_engine/test_memory_upgrades.py`.

### Traka C — Dreaming-style playbooks
- `machine_digest_learning.py`: `--emit-playbooks` piše
  `.agent/task/playbooks/<week>_<pid>.md` (trigger → action → verification) po
  **prihvaćenom** prijedlogu; weekly SKILL.md ažuriran.
- Skill-reference validacija: **već postoji** i zelena je
  (`skill_registry.py validate` = PASS; `validate_rules_links.py` = 0 missing) —
  robusniji registry-based pristup od krhkog `@token` skeniranja, pa novi
  validator nije dodavan.
- Test: `40_operations/tests/scripts/test_digest_playbooks.py`.

## 4. Preostale (ne-blokirajuće) rupe
- 13 root-level compatibility bridge mapa — namjerne, ali dodaju šum; kandidat za
  cleanup politiku.
- Migracijski status `behavior_rules/` 15–28, 57–59 nejasan (reference vs aktivno).
- `.cursorrules` vs `.cursor/rules/` preklapanje — dokumentirati presedan.

## 5. Verifikacija
- `python -m pytest 40_operations/tests -q` → **274 testa, 0 failova, 5 skip**.
- Guard: `check_sync.py`/`workspace_bootstrap.py --check-only` iz OneDrive → FAIL;
  iz živog repoa → PASS.
- `memory_prune.py --dry-run`, `skill_registry.py validate` (PASS),
  `validate_rules_links.py` (0 missing).
