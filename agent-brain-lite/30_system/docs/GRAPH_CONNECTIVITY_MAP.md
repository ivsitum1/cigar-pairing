# Graph Connectivity Map

This document tracks Obsidian graph connectivity and the remediation workflow for this workspace.

## Related Hubs

- [README.md](../index.md)
- [AUTOMATION_INDEX.md](AUTOMATION_INDEX.md)
- [bridges/non_markdown_bridges.md](bridges/non_markdown_bridges.md)
- [../20_knowledge/wiki/index.md](../20_knowledge/wiki/index.md)
- [Folder index hub](FOLDER_INDEX.md)
- [All notes index](ALL_NOTES_INDEX.md)
## Baseline Snapshot

- Scan date: 2026-05-05
- Markdown files scanned: 256
- Strict orphan nodes (0 inbound and 0 outbound): 215
- Weak nodes (total degree <= 1): 222

## Post-Implementation Snapshot

- Scan date: 2026-05-05
- Markdown files scanned: 259
- Connected nodes (inbound >=1 and outbound >=1): 15
- Strict orphan nodes (0 inbound and 0 outbound): 198
- Weak nodes (total degree <= 1): 211
- Connectivity check command: `python 40_operations/scripts/obsidian_connectivity_check.py --root .`

Current pass criteria status:

- `0 orphan markdown files`: not yet met
- `100% files represented directly or through bridge notes`: implemented for priority operational clusters
- `No isolated automation-critical nodes`: met for targeted loop entrypoints in `30_system/docs/AUTOMATION_INDEX.md`

## Second-Pass Snapshot (Zero-Orphan Pass)

- Scan date: 2026-05-05
- Markdown files scanned: 260
- Connected nodes (inbound >=1 and outbound >=1): 24
- Weak nodes (total degree <= 1): 196
- Strict orphan nodes (0 inbound and 0 outbound): 0
- Connectivity check command: `python 40_operations/scripts/obsidian_connectivity_check.py --root .`

Second-pass actions:

- Added canonical global hub: `30_system/docs/ALL_NOTES_INDEX.md`
- Linked global hub from root/30_system/docs/router indexes
- Preserved bridge-note approach for non-markdown assets

## Connectivity Status Model

- `connected`: at least one inbound and one outbound link
- `weak`: only one direction or only one total edge
- `orphan`: no inbound and no outbound links
- `bridged`: non-markdown file represented through a bridge note

## Primary Hubs

- `README.md`
- `30_system/docs/README.md`
- `.cursor/docs/INDEX.md`
- `20_knowledge/wiki/index.md`
- `30_system/docs/AUTOMATION_INDEX.md`
- `30_system/docs/bridges/non_markdown_bridges.md`

## Priority Gap Clusters

### Context Cluster

- `30_system/context/user.md`
- `30_system/context/memory.md`
- `30_system/context/soul.md`

### Wiki Cluster

- `20_knowledge/wiki/index.md`
- `20_knowledge/wiki/log.md`

### Root Singleton Cluster

- `claude.md`
- `UBIQUITOUS_LANGUAGE.md`
- `WORKSPACE_RECONSTRUCTION_GUIDE.md`

### Automation Cluster

- `.cursor/hooks.json`
- `.cursor/hooks/memory_lifecycle.py`
- `40_operations/scripts/context_sync.py`
- `40_operations/scripts/changelog_auto.py`
- `40_operations/scripts/run_all_checks.sh`
- `40_operations/scripts/self_eval_learning_loop.py`

## Bridging Rule For Non-Markdown Files

Non-markdown files are linked through documentation bridge notes to keep the graph navigable and avoid modifying generated artifacts.

- Bridge index: `30_system/docs/bridges/non_markdown_bridges.md`
- Automation index: `30_system/docs/AUTOMATION_INDEX.md`

## Recheck Workflow

1. Regenerate folder indexes: `py -3 40_operations/scripts/generate_folder_md_indexes.py --root .`
2. Semantic orphan pass: `py -3 40_operations/scripts/wiki_semantic_link.py --root . --apply --regenerate-reference-index` (see [[Wiki semantic graph linking]]).
3. Run a connectivity scan: `py -3 40_operations/scripts/obsidian_connectivity_check.py --root .`
4. Optional: normalize `## Related Hubs` blocks: `py -3 40_operations/scripts/normalize_related_hubs.py --root .`
5. Update this file with latest counts.
6. Ensure each markdown file is in at least one hub path (inbound) and links out to a hub (outbound).
7. Ensure each non-markdown operational file is represented in bridge notes.
8. Python/XML graph: `py -3 40_operations/scripts/generate_code_bridge_clusters.py --root .` then `validate_code_bridge_clusters.py` (wikilinks via [[code_graph_hub]]).

## Latest connectivity snapshot (maintainer)

- Scan tool: `40_operations/scripts/obsidian_connectivity_check.py`
- Last run (2026-05-16): Markdown files **4209**, Connected **3285**, Weak **0**, Orphan **0**.
- Embedding pass: `wiki_semantic_link.py --apply --embeddings` (104 targets; TF-IDF corpus 928 docs → `## Semantic neighbors (embedding)` + graph section for zero-outbound). Module: `wiki_embedding_index.py`.
- Prior pass: path buckets (516 orphans → 0). Concept hub: `20_knowledge/wiki/concepts/Wiki semantic graph linking.md`.
- Prior run (2026-05-10): manual wikilinks for Obsidian playbook + obsidian-wiki-agent. Re-run folder indexes + semantic pass after large doc moves.
