---
aliases: [OBSIDIAN_AGENT_PLAYBOOK]
tags: [meta/obsidian]
---

# Obsidian agent playbook

Reference for Cursor agents editing markdown and related files so they remain valid in **Obsidian**. Use when the user asks for syntax, “Obsidian tricks”, Canvas, Bases, URIs, or vault-native formatting.

**Scope:** Core Obsidian behavior and widely used patterns. Features that require a **specific community plugin** are marked *plugin*; do not assume they are installed unless the user says so.

## Wiki integration (agent-rules)

This file ships inside the shared brain repo; keep it aligned with the markdown graph under `20_knowledge/wiki/`.

- Vault index: [[20_knowledge/wiki/index]]
- Routing hub: [[Obsidian-centered agent routing]]
- Agent workflow (ingest + syntax + graph checks): [[Claude agent Obsidian wiki workflow]]
- Registry skill (YAML triggers, workflows A–D): [[SKILL_obsidian-wiki-agent]]

---

## 1. Wikilinks (internal links)

| Pattern | Meaning |
|--------|---------|
| `[[Note title]]` | Link to note by **exact title** (filename without `.md`, or display title depending on settings). |
| `[[folder/Note title]]` | Path-qualified when titles collide. Prefer vault-relative paths consistent with user convention. |
| `[[Note title\|shown text]]` | Link with **custom display text** (pipe alias). |
| `[[Note title#Heading]]` | Link to a **heading block** in the target note. Heading text must match (Obsidian updates links when headings rename if settings allow). |
| `[[Note title#Heading\|shown]]` | Heading link with display text. |
| `[[Note title^block-id]]` | Link to a **block** (see block IDs below). |
| `[[#Heading]]` | Link to heading **in the same file**. |

**Agent habits**

- Prefer titles that match existing notes to avoid orphans; grep or list dir before inventing new titles.
- After renaming a file, search for `[[Old Title]]` and update (Obsidian may auto-update wikilinks depending on settings; do not rely on it in batch edits).

---

## 2. Embeds (transclusion)

| Pattern | Meaning |
|--------|---------|
| `![[Note]]` | Embed **entire note** content in preview. |
| `![[Note#Heading]]` | Embed from heading downward (behavior follows Obsidian version). |
| `![[image.png]]` | Embed image (path relative to vault or attachment folder). |
| `![[doc.pdf]]` | PDF embed when supported (page navigation is UI-side). |

Embeds differ from links: leading `!`.

---

## 3. Block identifiers

- Paragraph or list item can end with `^my-id` (unique per file) to create a **block reference**.
- Link: `[[Note^my-id]]` or `[[Note#^my-id]]` depending on Obsidian version and link format.
- Embed block: `![[Note^my-id]]`.

Use **stable, readable** ids (`^definition`, `^eq-1`), not random strings, when the user wants maintainable notes.

---

## 4. Markdown Obsidian extends (common)

| Feature | Syntax |
|--------|--------|
| Highlight | `==highlighted==` |
| Inline comment (non-export in many setups) | `%% hidden comment %%` |
| Task | `- [ ]` todo, `- [x]` done |
| Footnote | `[^1]` with `[^1]: text` below |
| Math | `$inline$` and `$$block$$` |

---

## 5. Callouts

Foldable / styled blocks:

```markdown
> [!note] Title optional
> Body line one
> Body line two

> [!tip] Shortcuts
> Single paragraph.

> [!warning]
> No title; still works.
```

Common types Obsidian recognizes include `note`, `abstract`, `info`, `todo`, `tip`, `success`, `question`, `warning`, `failure`, `danger`, `bug`, `example`, `quote` (exact set can vary by version).

**Foldable:** `[!note]-` collapsed by default; `[!note]+` expanded (syntax availability follows Obsidian release notes).

---

## 6. Frontmatter (YAML)

Standard at **top of file**:

```yaml
---
title: Optional override
aliases: [Alt Name, Another]
tags: [topic/sub]
date: 2026-05-10
cssclasses: [wide]
---
```

**Properties / typed metadata:** Newer Obsidian versions expose frontmatter as Properties UI. Stick to valid YAML; avoid tabs in YAML; quote strings with `:` or special chars.

**Agent rule:** When adding tags, align with existing tag vocabulary in the vault; avoid dozens of one-off tags.

---

## 7. Tags vs wikilinks

- `#tag` and `#nested/tag` for tag pane navigation.
- `[[Concept]]` for graph edges between notes. Use **both** deliberately: tags for loose grouping, links for explicit conceptual ties.

---

## 8. Mermaid

````markdown
```mermaid
flowchart LR
  A --> B
```
````

Valid Mermaid inside fenced block; Obsidian renders in preview. Validate syntax mentally or with a quick render check when complex.

---

## 9. Attachments

- Default attachment folder is often `attachments/` or per-vault setting.
- Wikilink to attachment: `[[folder/file.pdf]]` or embed `![[file.png]]`.
- When the agent adds binary assets, respect user policy (many academic vaults avoid committing large binaries to git).

---

## 10. JSON Canvas (`.canvas`)

Obsidian Canvas uses JSON files the graph opens visually. Agents can **edit JSON directly** for automation.

Conceptual structure:

- **Nodes:** text, file, link, group, etc., each with `id`, `type`, `x`, `y`, `width`, `height`, and type-specific fields (e.g. `file` path for file nodes).
- **Edges:** connections between node ids with optional labels.

**Practices**

- Preserve existing `id` strings when editing; duplicate ids break the canvas.
- Small incremental edits safer than rewriting entire file without backup.
- File nodes reference vault paths using forward slashes.

When unsure of schema details, open an existing `.canvas` from the user vault as template.

---

## 11. Bases (Obsidian Bases)

**Bases** are a native way to define table/card views over notes using filters (depends on Obsidian version). Files often use extension `.base` with structured content.

**Agent practices**

- Treat `.base` files as **data definitions**: edit carefully; validate against an existing working `.base` in the vault.
- Do not invent filter DSL without copying working patterns from the user’s vault.

---

## 12. Obsidian URI scheme

External apps and scripts open vault notes via URIs, e.g.:

- `obsidian://open?vault=VAULT_NAME&file=RELATIVE_PATH.md`
- Vault name usually matches the vault folder name (spaces encoded).

Use URIs when integrating automation the user requests; paths must match their OS encoding (`%20` for spaces).

---

## 13. Core vs community plugins

| Area | Core / stock | *plugin* (confirm installed) |
|------|----------------|------------------------------|
| Graph, backlinks, outline | Core | |
| Daily notes, templates | Core (templates) | Templater (*plugin*) for advanced scripting |
| Query tables over metadata | Limited core | Dataview (*plugin*) |
| Calendar, spaced repetition | | Community |
| Excalidraw | | Excalidraw (*plugin*) |

**Rule:** If the user did not name a plugin, prefer **core markdown + wikilinks + callouts + frontmatter**. Suggest Dataview/Templater snippets only when they confirm use.

---

## 14. Vault hygiene for agents

1. **Atomic notes:** one main idea per file when building PKM; long manuals split by heading still okay for specs.
2. **Hub notes:** index pages list children; avoid orphan-only structures.
3. **Link direction:** when creating `[[B]]` from `A`, consider whether `B` should backlink context in body (Obsidian shows backlinks automatically).
4. **Rename strategy:** rename file → fix incoming links if batch-needed.
5. **Git:** `.obsidian/workspace.json` may churn; many teams gitignore workspace or use workspace sync intentionally.

---

## 15. Quality checklist (before finishing an edit)

- [ ] Wikilink targets exist or are intentionally stubs the user asked for.
- [ ] YAML frontmatter parses (no stray `---` inside body).
- [ ] Callout fence lines use `>` consistently.
- [ ] Code fences closed; Mermaid valid.
- [ ] Block ids unique within file.

---

## 16. Inspiration map (external repos, not copied here)

Community collections such as **kepano/obsidian-skills**, **anthropics/skills**, and **jykim/claude-obsidian-skills** illustrate packaging of Obsidian-specific agent instructions; this playbook distills portable syntax and habits for **any** vault, including `20_knowledge/wiki/` in agent-rules.

## Parent skills (auto)

- [[SKILL_obsidian-wiki-agent]]

## Related playbooks (auto)

- [[ai_detection_patterns]]
- [[ai_phrase_replacements]]
- [[bayesian_code_templates]]
- [[consort_checklist_items]]
- [[literature_synthesis_templates]]
- [[meta_analysis_code_templates]]
- [[r_statistics_coding]]
- [[r_statistics_packages]]
