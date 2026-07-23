#!/usr/bin/env python3
"""Semantic graph linking: path buckets + token/TF-IDF embedding neighbors → hub backlinks.

Orphans have zero inbound AND zero outbound. Folder indexes give inbound only; this script
adds outbound sections. Use --embeddings for TF-IDF neighbor wikilinks (sklearn).

Usage:
  py -3 40_operations/scripts/wiki_semantic_link.py --root . --dry-run
  py -3 40_operations/scripts/wiki_semantic_link.py --root . --apply
  py -3 40_operations/scripts/wiki_semantic_link.py --root . --apply --embeddings
  py -3 40_operations/scripts/wiki_semantic_link.py --root . --apply --embeddings --regenerate-reference-index
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from obsidian_connectivity_check import build_graph, collect_markdown_files
from wiki_embedding_index import TfidfEmbeddingIndex, build_embedding_corpus, _doc_text

SECTION_MARK = "## Semantic graph (auto)"
EMBED_MARK = "## Semantic neighbors (embedding)"
TOKEN_RE = re.compile(r"[a-z0-9]{3,}", re.I)

_BUCKET_RULES: list[tuple[str, list[str], list[str]]] = [
    (
        "30_system/SKILLS/reference/legal/",
        ["Legal contract review skill", "Skill registry"],
        ["30_system/docs/indexes/SKILLS_INDEX.md", "30_system/SKILLS/reference/REFERENCE_INDEX.md"],
    ),
    (
        "30_system/SKILLS/reference/kdense/",
        ["Statistics skill stack", "Skill registry"],
        ["30_system/docs/indexes/SKILLS_INDEX.md", "30_system/SKILLS/reference/REFERENCE_INDEX.md"],
    ),
    (
        "30_system/SKILLS/reference/scientific_thinking/",
        ["Scholarly skill loop", "Skill registry"],
        ["30_system/docs/indexes/SKILLS_INDEX.md", "30_system/SKILLS/reference/REFERENCE_INDEX.md"],
    ),
    (
        "30_system/SKILLS/reference/",
        ["Skill registry", "Statistics skill stack"],
        ["30_system/docs/indexes/SKILLS_INDEX.md", "30_system/SKILLS/reference/REFERENCE_INDEX.md"],
    ),
    (
        "30_system/SKILLS/",
        ["Skill registry", "skills-auto-detect"],
        ["30_system/docs/indexes/SKILLS_INDEX.md", "30_system/docs/FOLDER_INDEX.md"],
    ),
    (
        ".agent/task/",
        ["Skill gap pipeline", "Skill discovery skill"],
        ["30_system/docs/indexes/_agent_INDEX.md", "20_knowledge/wiki/log.md"],
    ),
    (
        ".agent/",
        ["Orchestrator - agent roles"],
        ["30_system/docs/indexes/_agent_INDEX.md", "30_system/docs/FOLDER_INDEX.md"],
    ),
    (
        "20_knowledge/wiki/concepts/",
        ["Skill registry", "20_knowledge/wiki/index"],
        ["20_knowledge/wiki/index.md", "30_system/docs/FOLDER_INDEX.md"],
    ),
    (
        "20_knowledge/wiki/sources/",
        ["20_knowledge/wiki/index"],
        ["20_knowledge/wiki/sources/pdf/INDEX.md", "30_system/docs/indexes/20_knowledge_INDEX.md"],
    ),
    (
        "20_knowledge/",
        ["20_knowledge/wiki/index"],
        ["30_system/docs/indexes/20_knowledge_INDEX.md", "30_system/docs/FOLDER_INDEX.md"],
    ),
    (
        "40_operations/",
        ["Graph connectivity map"],
        ["30_system/docs/indexes/40_operations_INDEX.md", "30_system/docs/AUTOMATION_INDEX.md"],
    ),
    (
        "30_system/behavior_rules/",
        ["Behavior rules hub", "Orchestrator - agent roles"],
        ["30_system/docs/indexes/behavior_rules_INDEX.md", "30_system/docs/FOLDER_INDEX.md"],
    ),
    (
        "30_system/",
        ["Behavior rules hub"],
        ["30_system/docs/indexes/30_system_INDEX.md", "30_system/docs/FOLDER_INDEX.md"],
    ),
]

_DEFAULT_WIKI = ["20_knowledge/wiki/index", "Graph connectivity map"]
_DEFAULT_MD = ["30_system/docs/FOLDER_INDEX.md", "30_system/docs/GRAPH_CONNECTIVITY_MAP.md"]


def _tokens(text: str) -> Counter[str]:
    return Counter(t.lower() for t in TOKEN_RE.findall(text))


def _bucket_for(rel_posix: str) -> tuple[list[str], list[str]]:
    for prefix, wikis, mds in _BUCKET_RULES:
        if rel_posix.startswith(prefix):
            return list(wikis), list(mds)
    return list(_DEFAULT_WIKI), list(_DEFAULT_MD)


def _load_concept_corpus(concepts_dir: Path) -> list[tuple[str, Counter[str]]]:
    corpus: list[tuple[str, Counter[str]]] = []
    if not concepts_dir.is_dir():
        return corpus
    for p in concepts_dir.glob("*.md"):
        try:
            body = p.read_text(encoding="utf-8", errors="ignore")[:4000]
        except OSError:
            continue
        title = p.stem.replace("_", " ")
        corpus.append((title, _tokens(f"{title} {body}")))
    return corpus


def _suggest_wikilinks(
    rel_posix: str,
    body: str,
    corpus: list[tuple[str, Counter[str]]],
    top_k: int = 2,
    min_score: float = 0.12,
) -> list[str]:
    path = Path(rel_posix)
    query = _tokens(f"{path.stem} {' '.join(path.parts)} {body[:2500]}")
    if not query or not corpus:
        return []
    scored: list[tuple[float, str]] = []
    q_total = sum(query.values())
    for title, ct in corpus:
        overlap = sum((query & ct).values())
        if overlap == 0:
            continue
        denom = q_total + sum(ct.values()) - overlap
        score = overlap / denom if denom else 0.0
        if score >= min_score:
            scored.append((score, title))
    scored.sort(reverse=True)
    return [t for _, t in scored[:top_k]]


def _rel_link(from_file: Path, root: Path, target_rel: str) -> str:
    target = (root / target_rel).resolve()
    rel = os.path.relpath(target, from_file.parent).replace("\\", "/")
    label = Path(target_rel).stem.replace("_", " ")
    return f"- [{label}]({rel})"


def _wiki_line(title: str) -> str:
    return f"- [[{title}]]"


def _build_graph_section(
    from_file: Path,
    root: Path,
    rel_posix: str,
    body: str,
    corpus: list[tuple[str, Counter[str]]],
) -> str:
    wikis, mds = _bucket_for(rel_posix)
    suggested = _suggest_wikilinks(rel_posix, body, corpus)
    seen: set[str] = set()
    lines: list[str] = [SECTION_MARK, ""]
    for t in suggested:
        if t not in seen:
            seen.add(t)
            lines.append(_wiki_line(t))
    for t in wikis:
        if t not in seen:
            seen.add(t)
            lines.append(_wiki_line(t))
    linked_md: set[str] = set()
    for md in mds:
        if (root / md).is_file() and md not in linked_md:
            linked_md.add(md)
            lines.append(_rel_link(from_file, root, md))
    folder_hub = "30_system/docs/FOLDER_INDEX.md"
    if folder_hub not in linked_md and (root / folder_hub).is_file():
        lines.append(_rel_link(from_file, root, folder_hub))
    return "\n".join(lines) + "\n"


def _build_embed_section(
    neighbors: list[tuple[str, float]],
) -> str:
    if not neighbors:
        return ""
    lines: list[str] = [EMBED_MARK, ""]
    for title, _score in neighbors:
        lines.append(_wiki_line(title))
    return "\n".join(lines) + "\n"


def _strip_section(text: str, mark: str) -> str:
    idx = text.find(mark)
    if idx < 0:
        return text
    rest = text[idx + len(mark) :]
    m = re.search(r"\n## [^\n]+\n", rest)
    if m:
        end = idx + len(mark) + m.start()
    else:
        end = len(text)
    return (text[:idx].rstrip() + "\n\n").replace("\n\n\n", "\n\n")


def ensure_reference_index(root: Path, md_files: list[Path]) -> Path:
    out = root / "30_system/SKILLS/reference/REFERENCE_INDEX.md"
    refs = sorted(
        p.relative_to(root).as_posix()
        for p in md_files
        if p.relative_to(root).as_posix().startswith("30_system/SKILLS/reference/")
        and p.name != "REFERENCE_INDEX.md"
    )
    lines = [
        "# SKILLS reference index",
        "",
        "Auto hub for skill reference playbooks (path-semantic cluster).",
        "",
        "## Related Hubs",
        "",
        "- [[Skill registry]]",
        "- [[Statistics skill stack]]",
        "- [[Scholarly skill loop]]",
        "- [[Legal contract review skill]]",
        "- [[Wiki semantic graph linking]]",
        "- [SKILLS index](../../docs/indexes/SKILLS_INDEX.md)",
        "- [Folder index hub](../../docs/FOLDER_INDEX.md)",
        "",
        "## Reference files",
        "",
    ]
    for rel in refs:
        name = Path(rel).stem.replace("_", " ")
        target = root / rel
        rel_from_out = os.path.relpath(target, out.parent).replace("\\", "/")
        stem = Path(rel).stem
        lines.append(f"- [[{stem}]] · [{name}]({rel_from_out})")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def _compose_sections(
    from_file: Path,
    root: Path,
    rel_posix: str,
    body: str,
    token_corpus: list[tuple[str, Counter[str]]],
    embed_index: TfidfEmbeddingIndex | None,
    embed_top_k: int,
) -> str:
    parts: list[str] = []
    parts.append(_build_graph_section(from_file, root, rel_posix, body, token_corpus).rstrip())
    if embed_index is not None:
        query_text = f"{rel_posix} {_doc_text(from_file)}"
        neighbors = embed_index.neighbors(
            query_text,
            top_k=embed_top_k,
            exclude_rel=rel_posix,
        )
        embed = _build_embed_section(neighbors)
        if embed:
            parts.append(embed.rstrip())
    return "\n\n".join(parts) + "\n"


def apply_to_file(
    path: Path,
    root: Path,
    token_corpus: list[tuple[str, Counter[str]]],
    embed_index: TfidfEmbeddingIndex | None,
    embed_top_k: int,
    dry_run: bool,
    *,
    force_graph: bool,
) -> bool:
    rel = path.relative_to(root).as_posix()
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except OSError:
        return False

    need_graph = force_graph or SECTION_MARK not in text
    need_embed = embed_index is not None

    if not need_graph and not need_embed:
        return False

    body = text
    body = _strip_section(body, EMBED_MARK)
    if need_graph or SECTION_MARK in text:
        body = _strip_section(body, SECTION_MARK)

    new_tail = _compose_sections(path, root, rel, text, token_corpus, embed_index if need_embed else None, embed_top_k)
    new_text = body.rstrip() + "\n\n" + new_tail

    if new_text == text:
        return False
    if not dry_run:
        path.write_text(new_text, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Semantic Obsidian linking for orphans and weak nodes.")
    ap.add_argument("--root", default=".", help="Workspace root")
    ap.add_argument("--dry-run", action="store_true", help="Report only, do not write")
    ap.add_argument("--apply", action="store_true", help="Write sections")
    ap.add_argument("--include-weak", action="store_true", help="Also process weak nodes (degree <= 1)")
    ap.add_argument(
        "--embeddings",
        action="store_true",
        help="Add TF-IDF semantic neighbor wikilinks (sklearn)",
    )
    ap.add_argument(
        "--embed-top-k",
        type=int,
        default=5,
        help="Max embedding neighbors per file (default 5)",
    )
    ap.add_argument(
        "--fix-zero-outbound",
        action="store_true",
        help="Process all markdown files with zero outbound links (default with --embeddings)",
    )
    ap.add_argument(
        "--regenerate-reference-index",
        action="store_true",
        help="Rewrite 30_system/SKILLS/reference/REFERENCE_INDEX.md",
    )
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if not args.apply and not args.dry_run:
        args.dry_run = True

    if args.embeddings and not args.fix_zero_outbound:
        args.fix_zero_outbound = True
    if args.embeddings and not args.include_weak:
        args.include_weak = True

    md_files = collect_markdown_files(root)
    inbound, outbound = build_graph(root, md_files)
    orphans = {rel for rel in inbound if inbound[rel] == 0 and outbound[rel] == 0}
    weak = {rel for rel in inbound if inbound[rel] + outbound[rel] <= 1}
    zero_out = {rel for rel in outbound if outbound[rel] == 0}

    targets: set[str] = set(orphans)
    if args.include_weak:
        targets |= weak
    if args.fix_zero_outbound:
        targets |= zero_out

    if args.regenerate_reference_index or args.apply:
        ensure_reference_index(root, md_files)
        print("Wrote: 30_system/SKILLS/reference/REFERENCE_INDEX.md")

    concepts_dir = root / "20_knowledge/wiki/concepts"
    token_corpus = _load_concept_corpus(concepts_dir)

    embed_index: TfidfEmbeddingIndex | None = None
    if args.embeddings:
        corpus = build_embedding_corpus(root)
        print(f"Embedding corpus: {len(corpus)} documents")
        embed_index = TfidfEmbeddingIndex(corpus)

    changed = 0
    for path in md_files:
        rel = path.relative_to(root).as_posix()
        if rel not in targets:
            continue
        if apply_to_file(
            path,
            root,
            token_corpus,
            embed_index,
            args.embed_top_k,
            dry_run=not args.apply,
            force_graph=args.fix_zero_outbound or rel in orphans,
        ):
            changed += 1

    print(f"targets: {len(targets)} (orphans={len(orphans)}, weak={len(weak)}, zero_outbound={len(zero_out)})")
    print(f"updated_files: {changed}" + (" (dry-run)" if not args.apply else ""))
    if args.embeddings:
        print("embeddings: tfidf (sklearn)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
