#!/usr/bin/env python3
"""Monthly arXiv scan for agent/stat/CS skill scouting.

Writes JSON + markdown digest under .agent/task/.
Respects arXiv rate limit (default 3.5s between API calls).

Usage:
  py -3 40_operations/scripts/arxiv_monthly_scan.py
  py -3 40_operations/scripts/arxiv_monthly_scan.py --month 2026-05
  py -3 40_operations/scripts/arxiv_monthly_scan.py --dry-run --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from calendar import monthrange
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    import arxiv
except ImportError:
    arxiv = None  # type: ignore[assignment,misc]

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_CONFIG = REPO_ROOT / "30_system" / "config" / "arxiv_monthly_scan.json"
TASK_DIR = REPO_ROOT / ".agent" / "task"


@dataclass
class PaperRecord:
    arxiv_id: str
    title: str
    authors: list[str]
    published: str
    primary_category: str
    categories: list[str]
    abstract: str
    pdf_url: str
    abs_url: str
    score: float = 0.0
    keyword_hits: list[str] = field(default_factory=list)


@dataclass
class SkillProposal:
    proposed_skill_id: str
    title: str
    arxiv_id: str
    abs_url: str
    rationale: str
    suggested_triggers: list[str]
    risk: str


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def parse_week(week_str: str | None) -> tuple[str, date, date]:
    """Return (label YYYY-WW, start Monday, end Sunday) for ISO week window."""
    if week_str:
        year_s, week_s = week_str.split("-W", 1)
        year, week = int(year_s), int(week_s)
    else:
        today = date.today()
        iso = today.isocalendar()
        year, week = iso.year, iso.week
        # Default: previous ISO week
        monday = date.fromisocalendar(year, week, 1) - timedelta(days=7)
        iso = monday.isocalendar()
        year, week = iso.year, iso.week
    start = date.fromisocalendar(year, week, 1)
    end = start + timedelta(days=6)
    return f"{year:04d}-W{week:02d}", start, end


def parse_month(month_str: str | None) -> tuple[str, date, date]:
    """Return (label YYYY-MM, first_day, last_day) for the scan window."""
    if month_str:
        year_s, mon_s = month_str.split("-", 1)
        year, mon = int(year_s), int(mon_s)
    else:
        today = date.today()
        if today.month == 1:
            year, mon = today.year - 1, 12
        else:
            year, mon = today.year, today.month - 1
    last_day = monthrange(year, mon)[1]
    start = date(year, mon, 1)
    end = date(year, mon, last_day)
    return f"{year:04d}-{mon:02d}", start, end


def arxiv_date_range(start: date, end: date) -> str:
    """arXiv submittedDate query segment."""
    return (
        f"submittedDate:[{start.strftime('%Y%m%d')}0000 "
        f"TO {end.strftime('%Y%m%d')}2359]"
    )


def build_category_query(categories: list[str]) -> str:
    parts = [f"cat:{c}" for c in categories]
    return "(" + " OR ".join(parts) + ")"


def normalize_arxiv_id(entry_id: str) -> str:
    """Extract bare arXiv id from entry id URL."""
    m = re.search(r"arxiv\.org/abs/([^/]+)", entry_id)
    if m:
        return m.group(1).split("v")[0]
    return entry_id.rsplit("/", 1)[-1].split("v")[0]


def entry_from_result(r: Any) -> PaperRecord:
    cats = [c for c in (getattr(r, "categories", None) or [])]
    primary = cats[0] if cats else ""
    aid = normalize_arxiv_id(r.entry_id)
    return PaperRecord(
        arxiv_id=aid,
        title=(r.title or "").strip().replace("\n", " "),
        authors=[a.name for a in (r.authors or [])],
        published=r.published.date().isoformat() if r.published else "",
        primary_category=primary,
        categories=cats,
        abstract=(r.summary or "").strip().replace("\n", " "),
        pdf_url=r.pdf_url or f"https://arxiv.org/pdf/{aid}.pdf",
        abs_url=r.entry_id or f"https://arxiv.org/abs/{aid}",
    )


def is_excluded(paper: PaperRecord, exclude_prefixes: list[str]) -> bool:
    for cat in paper.categories:
        for prefix in exclude_prefixes:
            if cat.startswith(prefix):
                return True
    return False


def score_paper(
    paper: PaperRecord,
    cfg: dict[str, Any],
) -> tuple[float, list[str]]:
    weights: dict[str, int] = cfg.get("category_weights", {})
    keywords: list[str] = cfg.get("rank_keywords", [])
    text = f"{paper.title} {paper.abstract}".lower()
    hits: list[str] = []
    score = float(weights.get(paper.primary_category, 1))
    for kw in keywords:
        if kw.lower() in text:
            hits.append(kw)
            bonus = 3.0 if kw.lower() in paper.title.lower() else 1.5
            score += bonus
    return score, hits


def fetch_papers(
    query: str,
    max_results: int,
    delay: float,
) -> list[PaperRecord]:
    if arxiv is None:
        raise RuntimeError(
            "Missing package 'arxiv'. Install: pip install arxiv>=2.1.0"
        )
    client = arxiv.Client(delay_seconds=delay, num_retries=3)
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    return [entry_from_result(r) for r in client.results(search)]


def dedupe_papers(papers: list[PaperRecord]) -> list[PaperRecord]:
    seen: dict[str, PaperRecord] = {}
    for p in papers:
        if p.arxiv_id not in seen or p.score > seen[p.arxiv_id].score:
            seen[p.arxiv_id] = p
    return list(seen.values())


def slugify(text: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len].strip("-") or "arxiv-method"


def build_proposals(
    ranked: list[PaperRecord],
    cfg: dict[str, Any],
) -> list[SkillProposal]:
    proposal_kw = [k.lower() for k in cfg.get("proposal_keywords", [])]
    top_n = int(cfg.get("proposal_top_n", 3))
    proposals: list[SkillProposal] = []
    for paper in ranked:
        if len(proposals) >= top_n:
            break
        text = f"{paper.title} {paper.abstract}".lower()
        if not any(kw in text for kw in proposal_kw):
            continue
        skill_id = slugify(paper.title)
        triggers = [
            skill_id.replace("-", " "),
            "arxiv workflow",
        ]
        if "agent" in text:
            triggers.append("agent workflow")
        risk = "low" if paper.score < 15 else "med"
        proposals.append(
            SkillProposal(
                proposed_skill_id=skill_id,
                title=paper.title,
                arxiv_id=paper.arxiv_id,
                abs_url=paper.abs_url,
                rationale=(
                    f"Preprint ({paper.primary_category}) scores {paper.score:.1f} "
                    f"on scout keywords {paper.keyword_hits[:5]}. "
                    "Extract a repeatable agent procedure if methods generalize; "
                    "not for clinical claims."
                ),
                suggested_triggers=triggers[:4],
                risk=risk,
            )
        )
    return proposals


def render_digest_md(
    month_label: str,
    start: date,
    end: date,
    ranked: list[PaperRecord],
    proposals: list[SkillProposal],
    query: str,
) -> str:
    lines = [
        f"# arXiv skill scout digest — {month_label}",
        "",
        f"**Window:** {start.isoformat()} to {end.isoformat()} (UTC dates)",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "**Status:** Non-peer-reviewed preprints. Not clinical evidence.",
        "",
        f"**Query:** `{query}`",
        "",
        "## Top papers (ranked)",
        "",
    ]
    for i, p in enumerate(ranked, 1):
        authors = ", ".join(p.authors[:3])
        if len(p.authors) > 3:
            authors += " et al."
        lines.extend(
            [
                f"### {i}. {p.title}",
                "",
                f"- **arXiv:** [{p.arxiv_id}]({p.abs_url}) | **Score:** {p.score:.1f}",
                f"- **Category:** `{p.primary_category}` | **Published:** {p.published}",
                f"- **Authors:** {authors}",
                f"- **Keywords hit:** {', '.join(p.keyword_hits) or '—'}",
                "",
                f"> {p.abstract[:400]}{'…' if len(p.abstract) > 400 else ''}",
                "",
            ]
        )
    lines.extend(
        [
            "## Proposed skills (human approval required)",
            "",
            "Reply with **approve** / **reject** per `proposed_skill_id`. "
            "No registry change until approved. Then run `create-skill` flow.",
            "",
        ]
    )
    if not proposals:
        lines.append("_No proposals met keyword thresholds this month._\n")
    for j, pr in enumerate(proposals, 1):
        lines.extend(
            [
                f"### Proposal {j}: `{pr.proposed_skill_id}`",
                "",
                f"- **Source:** [{pr.arxiv_id}]({pr.abs_url}) — {pr.title}",
                f"- **Risk:** {pr.risk}",
                f"- **Suggested triggers:** {', '.join(pr.suggested_triggers)}",
                f"- **Rationale:** {pr.rationale}",
                "",
            ]
        )
    lines.extend(
        [
            "## Next steps",
            "",
            "1. Review proposals; approve at most 1–3 per month.",
            "2. On approve: `@create-skill` or SKILL_create-skill with paper-derived procedure.",
            "3. Optional: `python 40_operations/scripts/skill_gap_ingest.py wiki-log --detail \"arxiv scout {month_label}\"`",
            "",
        ]
    )
    return "\n".join(lines)


def run_scan(
    month_str: str | None,
    config_path: Path,
    dry_run: bool,
    *,
    period: str = "monthly",
    week_str: str | None = None,
) -> dict[str, Any]:
    cfg = load_config(config_path)
    if period == "weekly":
        period_label, start, end = parse_week(week_str)
    else:
        period_label, start, end = parse_month(month_str)
    cat_query = build_category_query(cfg["categories"])
    date_query = arxiv_date_range(start, end)
    query = f"{cat_query} AND {date_query}"

    if dry_run:
        return {
            "period": period,
            "month": period_label,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "query": query,
            "dry_run": True,
            "papers": [],
            "proposals": [],
        }

    raw = fetch_papers(
        query,
        max_results=int(cfg.get("max_results_per_query", 80)),
        delay=float(cfg.get("request_delay_seconds", 3.5)),
    )
    exclude = cfg.get("exclude_category_prefixes", [])
    papers = [p for p in raw if not is_excluded(p, exclude)]

    for p in papers:
        sc, hits = score_paper(p, cfg)
        p.score = sc
        p.keyword_hits = hits

    papers = dedupe_papers(papers)
    papers.sort(key=lambda x: x.score, reverse=True)
    digest_n = int(cfg.get("digest_top_n", 15))
    ranked = papers[:digest_n]
    proposals = build_proposals(papers, cfg)

    payload: dict[str, Any] = {
        "period": period,
        "month": period_label,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "query": query,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "config_path": str(config_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "paper_count_raw": len(raw),
        "paper_count_ranked": len(ranked),
        "papers": [asdict(p) for p in ranked],
        "proposals": [asdict(p) for p in proposals],
    }
    return payload


def write_outputs(payload: dict[str, Any], digest_md: str, *, period: str = "monthly") -> tuple[Path, Path]:
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    label = payload["month"]
    if period == "weekly":
        json_path = TASK_DIR / f"arxiv_scan_{label}.json"
        md_path = TASK_DIR / f"arxiv_digest_{label}.md"
    else:
        json_path = TASK_DIR / f"arxiv_scan_{label}.json"
        md_path = TASK_DIR / f"arxiv_digest_{label}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(digest_md, encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Monthly arXiv scan for skill scouting")
    parser.add_argument(
        "--period",
        choices=("monthly", "weekly"),
        default="monthly",
        help="Scan window: calendar month (default) or ISO week",
    )
    parser.add_argument(
        "--week",
        help="Target ISO week YYYY-WW (default: previous week when --period weekly)",
    )
    parser.add_argument(
        "--month",
        help="Target month YYYY-MM (default: previous calendar month)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to JSON config",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show query only; no API calls",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Do not write .agent/task files",
    )
    args = parser.parse_args()

    if not args.config.is_file():
        print(f"ERROR: config not found: {args.config}", file=sys.stderr)
        return 1

    try:
        payload = run_scan(
            args.month,
            args.config.resolve(),
            args.dry_run,
            period=args.period,
            week_str=args.week,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"Period: {payload.get('period', 'monthly')}")
            print(f"Window: {payload['month']} ({payload['start']} .. {payload['end']})")
            print(f"Query: {payload['query']}")
        return 0

    if args.period == "weekly":
        period_label, start, end = parse_week(args.week)
    else:
        period_label, start, end = parse_month(args.month)
    ranked = [PaperRecord(**p) for p in payload.get("papers", [])]
    proposals = [SkillProposal(**p) for p in payload.get("proposals", [])]
    digest_md = render_digest_md(
        period_label,
        start,
        end,
        ranked,
        proposals,
        payload["query"],
    )

    if not args.no_write:
        json_path, md_path = write_outputs(payload, digest_md, period=args.period)
        print(f"Wrote {json_path.relative_to(REPO_ROOT)}")
        print(f"Wrote {md_path.relative_to(REPO_ROOT)}")

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif not args.no_write:
        print(f"Papers in digest: {len(ranked)} | Proposals: {len(proposals)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
