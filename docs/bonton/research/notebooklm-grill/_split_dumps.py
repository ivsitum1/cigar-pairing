"""Split NotebookLM grill monoliths into answer + chunked sources."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAX_SOURCES_CHARS = 18_000
SKIP = {
    "README.md",
    "SYNTHESIS-2026-07-18.md",
    "REFRESH-DELTA-2026-07-18.md",
}


def split_sources(sources_body: str) -> list[str]:
    """Split Sources block into chunks under MAX_SOURCES_CHARS."""
    # Keep leading "Sources:" line out; chunks are self-contained lists
    body = sources_body
    if body.startswith("Sources:"):
        body = body[len("Sources:") :].lstrip("\n")

    parts = re.split(r"(?=^\[\d+\])", body, flags=re.M)
    parts = [p for p in parts if p.strip()]

    chunks: list[str] = []
    buf: list[str] = []
    size = 0
    for p in parts:
        if buf and size + len(p) > MAX_SOURCES_CHARS:
            chunks.append("".join(buf).rstrip() + "\n")
            buf, size = [], 0
        buf.append(p)
        size += len(p)
    if buf:
        chunks.append("".join(buf).rstrip() + "\n")
    return chunks or [body]


def process(path: Path) -> Path | None:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"\nSources:\s*\n", text)
    if not m:
        print(f"skip (no Sources): {path.name}")
        return None

    head_and_answer = text[: m.start()].rstrip() + "\n"
    sources_raw = text[m.start() + 1 :]  # starts with Sources:

    dest_dir = ROOT / path.stem
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True)

    answer_path = dest_dir / "answer.md"
    answer_path.write_text(head_and_answer, encoding="utf-8")

    chunks = split_sources(sources_raw)
    for i, chunk in enumerate(chunks, 1):
        (dest_dir / f"sources-{i:02d}.md").write_text(
            f"# Sources (part {i}/{len(chunks)})\n\n"
            f"Parent: `{path.stem}/answer.md`\n\n"
            f"Sources:\n\n{chunk}",
            encoding="utf-8",
        )

    index = [
        f"# {path.stem}\n",
        "",
        f"Split from monolith `{path.name}`.",
        "",
        "- [answer.md](./answer.md) — grill response (no footnote dump)",
    ]
    for i in range(1, len(chunks) + 1):
        index.append(f"- [sources-{i:02d}.md](./sources-{i:02d}.md)")
    index.append("")
    (dest_dir / "README.md").write_text("\n".join(index), encoding="utf-8")

    path.unlink()
    print(
        f"{path.name} -> {dest_dir.name}/ "
        f"(answer {answer_path.stat().st_size} B, {len(chunks)} source parts)"
    )
    return dest_dir


def main() -> int:
    # Drop exact duplicate holts twin if present
    a = ROOT / "5b8ae55e-discovery.md"
    b = ROOT / "5b8ae55e-holts-discovery.md"
    if a.exists() and b.exists():
        ta = a.read_text(encoding="utf-8")
        tb = b.read_text(encoding="utf-8")
        # Normalize slug line difference
        if ta.replace("5b8ae55e", "X") == tb.replace("5b8ae55e-holts", "X").replace(
            "5b8ae55e", "X"
        ) or abs(len(ta) - len(tb)) < 20:
            a.unlink()
            print("removed duplicate 5b8ae55e-discovery.md (kept holts)")

    monoliths = sorted(
        p
        for p in ROOT.glob("*.md")
        if p.name not in SKIP and (p.name.endswith("-discovery.md") or "refresh" in p.name)
    )
    for p in monoliths:
        process(p)

    # Rewrite root README index
    dirs = sorted(d for d in ROOT.iterdir() if d.is_dir())
    lines = [
        "# NotebookLM grill dumps (book research)",
        "",
        "**Grana:** `cursor/bonton-book-research-9b19`",
        "**Format:** svaki grill = mapa s `answer.md` + `sources-NN.md` (cijepano radi veličine).",
        "",
        "Sinteze (ne cijepati):",
        "- [SYNTHESIS-2026-07-18.md](./SYNTHESIS-2026-07-18.md)",
        "- [REFRESH-DELTA-2026-07-18.md](./REFRESH-DELTA-2026-07-18.md)",
        "",
        "Knjiga: `docs/bonton/BOOK-FROM-NOTEBOOKLM.md` · App: `docs/bonton/APP-FROM-NOTEBOOKLM.md`",
        "",
        "## Grillovi",
        "",
    ]
    for d in dirs:
        readme = d / "README.md"
        n_src = len(list(d.glob("sources-*.md")))
        lines.append(f"- [{d.name}/](./{d.name}/) — answer + {n_src} source part(s)")
    lines.append("")
    (ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print("updated README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
