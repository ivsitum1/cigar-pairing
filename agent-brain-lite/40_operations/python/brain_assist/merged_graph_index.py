"""Load Graphify merged.json for wiki-code bridging and TGS augmentation."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[3]
DEFAULT_MERGED = WORKSPACE / "graphify-out" / "merged.json"

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_GENERIC_TOKENS = frozenset(
    {
        "system",
        "scripts",
        "operations",
        "rules",
        "skill",
        "skills",
        "wiki",
        "python",
        "agent",
        "agents",
        "docs",
        "tools",
        "test",
        "tests",
        "utils",
        "helper",
        "helpers",
        "config",
        "index",
        "main",
        "readme",
        "md",
        "json",
        "py",
        "cursor",
        "knowledge",
        "brain",
        "assist",
        "vendor",
        "reference",
        "guide",
        "model",
        "data",
        "file",
        "files",
        "path",
        "code",
        "map",
        "graph",
    }
)


def _meaningful_tokens(text: str) -> set[str]:
    return {t for t in normalize_tokens(text) if t not in _GENERIC_TOKENS}


def _norm_stem(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def wiki_node_id(page_id: str) -> str:
    safe = page_id.replace("/", "_").replace("-", "_").replace(" ", "_").lower()
    return f"wiki_{safe}"


def normalize_tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall(text.lower()) if len(t) > 2}


@dataclass
class MergedGraphIndex:
    path: Path
    nodes: dict[str, dict]
    outbound: dict[str, set[str]]
    inbound: dict[str, set[str]]
    wiki_page_by_gid: dict[str, str]
    page_by_wiki_gid: dict[str, str]
    code_nodes: list[dict] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path | None = None) -> MergedGraphIndex | None:
        merged_path = path or DEFAULT_MERGED
        if not merged_path.is_file():
            return None
        data = json.loads(merged_path.read_text(encoding="utf-8"))
        nodes_list = data.get("nodes") or []
        links = data.get("links") or []

        nodes: dict[str, dict] = {}
        wiki_page_by_gid: dict[str, str] = {}
        code_nodes: list[dict] = []
        for node in nodes_list:
            nid = node.get("id")
            if not nid:
                continue
            nodes[nid] = node
            if node.get("file_type") == "wiki" or str(nid).startswith("wiki_"):
                sf = str(node.get("source_file") or "")
                prefix = "20_knowledge/wiki/"
                if prefix in sf.replace("\\", "/"):
                    rel = sf.replace("\\", "/").split(prefix, 1)[-1]
                    page_id = rel[:-3] if rel.endswith(".md") else rel
                    wiki_page_by_gid[nid] = page_id
            elif node.get("file_type") == "code":
                code_nodes.append(node)

        page_by_wiki_gid = {v: k for k, v in wiki_page_by_gid.items()}
        outbound: dict[str, set[str]] = {nid: set() for nid in nodes}
        inbound: dict[str, set[str]] = {nid: set() for nid in nodes}
        for link in links:
            s, t = link.get("source"), link.get("target")
            if not s or not t or s not in nodes or t not in nodes:
                continue
            outbound[s].add(t)
            inbound[t].add(s)

        return cls(
            path=merged_path,
            nodes=nodes,
            outbound=outbound,
            inbound=inbound,
            wiki_page_by_gid=wiki_page_by_gid,
            page_by_wiki_gid=page_by_wiki_gid,
            code_nodes=code_nodes,
        )

    def wiki_neighbors_via_merged(
        self,
        page_id: str,
        *,
        max_hops: int = 2,
    ) -> dict[str, float]:
        """Wiki page ids reachable through merged graph (including via code nodes)."""
        start = self.page_by_wiki_gid.get(page_id)
        if not start:
            return {}
        scores: dict[str, float] = {}
        frontier: list[tuple[str, int, float]] = [(start, 0, 1.0)]
        seen: set[str] = {start}
        while frontier:
            node, depth, weight = frontier.pop(0)
            if depth >= max_hops:
                continue
            for nbr in self.outbound.get(node, ()):
                if nbr in seen:
                    continue
                seen.add(nbr)
                decay = 0.65 ** (depth + 1)
                nbr_weight = weight * decay
                if nbr in self.wiki_page_by_gid:
                    pid = self.wiki_page_by_gid[nbr]
                    if pid != page_id:
                        scores[pid] = max(scores.get(pid, 0.0), nbr_weight)
                frontier.append((nbr, depth + 1, nbr_weight))
            for nbr in self.inbound.get(node, ()):
                if nbr in seen:
                    continue
                seen.add(nbr)
                decay = 0.55 ** (depth + 1)
                nbr_weight = weight * decay
                if nbr in self.wiki_page_by_gid:
                    pid = self.wiki_page_by_gid[nbr]
                    if pid != page_id:
                        scores[pid] = max(scores.get(pid, 0.0), nbr_weight)
                frontier.append((nbr, depth + 1, nbr_weight))
        return scores

    def propose_bridge_links(self, *, min_token_overlap: int = 2, max_per_wiki: int = 8) -> list[dict]:
        """Suggest wiki_* -> code node edges by basename/token overlap."""
        links: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for page_id, wiki_gid in self.page_by_wiki_gid.items():
            wiki_title = page_id.split("/")[-1]
            wiki_stem = _norm_stem(wiki_title)
            wiki_tokens = _meaningful_tokens(page_id.replace("/", " "))
            if not wiki_tokens and len(wiki_stem) < 4:
                continue
            candidates: list[tuple[float, dict]] = []
            for code in self.code_nodes:
                cid = code.get("id")
                if not cid:
                    continue
                sf = str(code.get("source_file") or "").replace("\\", "/")
                stem = Path(sf).stem.lower() if sf else ""
                code_stem = _norm_stem(stem)
                label = str(code.get("label") or "")
                code_tokens = _meaningful_tokens(f"{stem} {label}")
                overlap = wiki_tokens & code_tokens
                exact_stem = bool(wiki_stem and code_stem and wiki_stem == code_stem)
                prefix_stem = bool(
                    wiki_stem
                    and code_stem
                    and len(wiki_stem) >= 5
                    and (wiki_stem in code_stem or code_stem in wiki_stem)
                )
                if exact_stem:
                    score = 1.0
                elif prefix_stem:
                    score = 0.75
                elif len(overlap) >= min_token_overlap:
                    score = 0.45 + 0.1 * len(overlap)
                else:
                    continue
                key = (wiki_gid, cid)
                if key in seen:
                    continue
                candidates.append(
                    (
                        score,
                        {
                            "source": wiki_gid,
                            "target": cid,
                            "relation": "bridges_to",
                            "context": "wiki_code_bridge",
                            "confidence": "INFERRED",
                            "source_file": f"20_knowledge/wiki/{page_id}.md",
                            "source_location": "L1",
                            "weight": round(min(1.0, score), 3),
                            "bridge_tokens": sorted(overlap)[:8],
                        },
                    )
                )
            candidates.sort(key=lambda x: x[0], reverse=True)
            for _, link in candidates[:max_per_wiki]:
                key = (link["source"], link["target"])
                if key in seen:
                    continue
                seen.add(key)
                links.append(link)
        return links
