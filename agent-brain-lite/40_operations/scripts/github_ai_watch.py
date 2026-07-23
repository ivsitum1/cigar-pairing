#!/usr/bin/env python3
"""Watch GitHub for trending AI/agent repositories (brain maintenance sensor)."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_CONFIG = REPO_ROOT / "30_system" / "config" / "github_ai_watch.json"
TASK_DIR = REPO_ROOT / ".agent" / "task"
API_URL = "https://api.github.com/search/repositories"


@dataclass
class RepoRecord:
    full_name: str
    html_url: str
    description: str
    stars: int
    pushed_at: str
    topics: list[str] = field(default_factory=list)
    score: float = 0.0
    keyword_hits: list[str] = field(default_factory=list)


@dataclass
class UpgradeProposal:
    proposal_id: str
    repo: str
    html_url: str
    rationale: str
    suggested_action: str
    risk: str


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def iso_week_label(when: date | None = None) -> str:
    when = when or date.today()
    iso = when.isocalendar()
    return f"{iso.year:04d}-W{iso.week:02d}"


def github_request(url: str, token: str | None) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "agent-rules-machine-watch",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def score_repo(repo: RepoRecord, cfg: dict[str, Any]) -> tuple[float, list[str]]:
    keywords = [k.lower() for k in cfg.get("rank_keywords", [])]
    text = f"{repo.full_name} {repo.description} {' '.join(repo.topics)}".lower()
    hits = [kw for kw in keywords if kw in text]
    score = float(repo.stars) / 100.0
    score += len(hits) * 2.0
    return score, hits


def fetch_repos(query: str, token: str | None, per_page: int) -> list[RepoRecord]:
    params = urllib.parse.urlencode(
        {"q": query, "sort": "stars", "order": "desc", "per_page": per_page}
    )
    data = github_request(f"{API_URL}?{params}", token)
    out: list[RepoRecord] = []
    for item in data.get("items", []):
        out.append(
            RepoRecord(
                full_name=item.get("full_name", ""),
                html_url=item.get("html_url", ""),
                description=(item.get("description") or "").strip(),
                stars=int(item.get("stargazers_count") or 0),
                pushed_at=(item.get("pushed_at") or "")[:10],
                topics=list(item.get("topics") or []),
            )
        )
    return out


def within_lookback(pushed_at: str, lookback_days: int) -> bool:
    if not pushed_at:
        return True
    try:
        pushed = datetime.strptime(pushed_at[:10], "%Y-%m-%d").date()
    except ValueError:
        return True
    cutoff = date.today() - timedelta(days=lookback_days)
    return pushed >= cutoff


def slugify(text: str, max_len: int = 48) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len].strip("-") or "repo"


def build_proposals(ranked: list[RepoRecord], cfg: dict[str, Any]) -> list[UpgradeProposal]:
    top_n = int(cfg.get("proposal_top_n", 5))
    proposals: list[UpgradeProposal] = []
    for repo in ranked:
        if len(proposals) >= top_n:
            break
        if not repo.keyword_hits:
            continue
        pid = slugify(repo.full_name)
        proposals.append(
            UpgradeProposal(
                proposal_id=pid,
                repo=repo.full_name,
                html_url=repo.html_url,
                rationale=(
                    f"Stars {repo.stars}; keywords {repo.keyword_hits[:4]}; "
                    f"last push {repo.pushed_at}. Review for MCP/skill/orchestrator patterns."
                ),
                suggested_action="Review README; if pattern fits, draft SKILL or doc note in weekly digest.",
                risk="low" if repo.stars < 500 else "med",
            )
        )
    return proposals


def run_watch(config_path: Path, dry_run: bool, week_label: str | None) -> dict[str, Any]:
    cfg = load_config(config_path)
    label = week_label or iso_week_label()
    if dry_run:
        return {
            "week": label,
            "dry_run": True,
            "queries": cfg.get("search_queries", []),
            "repos": [],
            "proposals": [],
        }

    token = os.environ.get("GITHUB_TOKEN", "").strip() or None
    min_stars = int(cfg.get("min_stars", 20))
    lookback = int(cfg.get("lookback_days", 7))
    per_query = int(cfg.get("max_results_per_query", 15))
    seen: dict[str, RepoRecord] = {}

    for query in cfg.get("search_queries", []):
        try:
            repos = fetch_repos(query, token, per_query)
        except urllib.error.HTTPError as exc:
            print(f"WARN: GitHub query failed ({exc.code}): {query}", file=sys.stderr)
            continue
        for repo in repos:
            if repo.stars < min_stars:
                continue
            if not within_lookback(repo.pushed_at, lookback):
                continue
            sc, hits = score_repo(repo, cfg)
            repo.score = sc
            repo.keyword_hits = hits
            prev = seen.get(repo.full_name)
            if prev is None or repo.score > prev.score:
                seen[repo.full_name] = repo

    ranked = sorted(seen.values(), key=lambda r: r.score, reverse=True)
    digest_n = int(cfg.get("digest_top_n", 20))
    ranked = ranked[:digest_n]
    proposals = build_proposals(ranked, cfg)

    return {
        "week": label,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "config_path": str(config_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "repo_count": len(ranked),
        "repos": [asdict(r) for r in ranked],
        "proposals": [asdict(p) for p in proposals],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="GitHub AI/agent repo watch for Machine digest")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--week", help="ISO week label YYYY-WW")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()

    if not args.config.is_file():
        print(f"ERROR: config not found: {args.config}", file=sys.stderr)
        return 1

    payload = run_watch(args.config.resolve(), args.dry_run, args.week)
    if args.dry_run:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if not args.no_write:
        TASK_DIR.mkdir(parents=True, exist_ok=True)
        out = TASK_DIR / f"github_ai_watch_{payload['week']}.json"
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {out.relative_to(REPO_ROOT)}")

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
