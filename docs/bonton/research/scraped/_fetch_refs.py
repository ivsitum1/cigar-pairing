"""Fetch public etiquette articles via pagefetch. Run from repo root."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "sideprojects" / "pagefetch" / "src"))

from pagefetch import fetch_page  # noqa: E402

OUT = Path(__file__).resolve().parent

URLS = [
    ("cigarlounges-etiquette", "https://www.cigarlounges.co/blog/cigar-lounge-etiquette"),
    ("vdg-lounge-etiquette", "https://vdg-cigars.com/cigar-lounge-etiquette-the-complete-rules-guide/"),
    ("the-manual-etiquette-101", "https://www.themanual.com/culture/cigar-etiquette-101/"),
    ("wikipedia-cigar-etiquette", "https://en.wikipedia.org/wiki/Cigar_etiquette"),
    ("gentlemans-gazette-cigar-101", "https://www.gentlemansgazette.com/cigar-etiquette-101/"),
    ("holts-clubhouse", "https://www.holts.com/clubhouse"),
    ("stogiehub-lounge", "https://stogiehub.com/cigar-lounge-etiquette/"),
    ("late-smoke-lounge", "https://www.thelatesmoke.com/articles/cigar-lounge-amp-bar-etiquette-how-not-to-be-that-guy"),
    ("cigars-international-etiquette", "https://www.cigarsinternational.com/blog/cigar-101/cigar-etiquette/"),
]


def slug_md(slug: str) -> Path:
    return OUT / f"{slug}.md"


def main() -> int:
    lines = ["# Fetch log", ""]
    for slug, url in URLS:
        dest = slug_md(slug)
        try:
            r = fetch_page(url, prefer="auto")
        except Exception as e:
            lines.append(f"- {slug}: ERROR {type(e).__name__}: {e}")
            dest.write_text(f"# {slug}\n\nURL: {url}\n\nFetch failed: {e}\n", encoding="utf-8")
            continue
        body = r.markdown or ""
        header = (
            f"# {r.title or slug}\n\n"
            f"- URL: {url}\n"
            f"- fetched: 2026-08-18\n"
            f"- method: {r.method}\n"
            f"- blocked: {r.blocked}\n"
            f"- error: {r.error or ''}\n\n"
            "---\n\n"
        )
        dest.write_text(header + body, encoding="utf-8")
        status = "blocked" if r.blocked else "ok"
        lines.append(
            f"- {slug}: {status} method={r.method} chars={len(body)} err={r.error or '-'}"
        )
    (OUT / "_fetch_log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
