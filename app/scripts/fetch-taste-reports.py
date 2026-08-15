#!/usr/bin/env python3
"""Pokupi dojmove s GitHuba — sve prijave s oznakom, bez rucnog kopiranja.

App salje dojmove kao predpopunjenu prijavu (vidi src/lib/tasteReport.ts). Ova
skripta ih dohvati, iz svake izvuce ```json blok i spoji u
src/data/tasteReports.json — istim putem kao rucni import-taste-report.py, samo
bez posrednika.

Prijava koja nema uredan blok se preskace i prijavi; komentar ispod prijave se
ne cita (dojmovi idu u tijelo, ne u raspravu).

Prijava ostaje otvorena — zatvara je covjek kad provjeri diff. Skripta nista ne
pise na GitHub; treba joj samo pravo citanja.

Prijava:
  * `gh` ako je instaliran (radi i za privatni repo, koristi tvoju prijavu)
  * inace GITHUB_TOKEN / GH_TOKEN iz okoline
  * inace bez prijave (javni repo; GitHub tada dopusta 60 zahtjeva na sat)

Pokreni iz app/:
    python3 scripts/fetch-taste-reports.py
    python3 scripts/fetch-taste-reports.py --dry-run
    python3 scripts/fetch-taste-reports.py --repo netko/drugi --label feedback
"""
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent

_spec = importlib.util.spec_from_file_location("imp", HERE / "import-taste-report.py")
_imp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_imp)

DEFAULT_REPO = "ivsitum1/cigar-pairing"
DEFAULT_LABEL = "dojmovi"
API = "https://api.github.com"


def _via_gh(path: str) -> list | None:
    """`gh api` kad postoji — nasljeduje prijavu korisnika, radi i za privatno."""
    if not shutil.which("gh"):
        return None
    try:
        out = subprocess.run(
            ["gh", "api", "--paginate", path],
            capture_output=True, text=True, check=True, timeout=60,
        ).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"gh nije uspio ({exc}); pokušavam izravno", file=sys.stderr)
        return None
    # --paginate zna nizati vise JSON nizova jedan za drugim
    rows: list = []
    decoder = json.JSONDecoder()
    idx = 0
    while idx < len(out):
        while idx < len(out) and out[idx].isspace():
            idx += 1
        if idx >= len(out):
            break
        chunk, end = decoder.raw_decode(out, idx)
        rows.extend(chunk if isinstance(chunk, list) else [chunk])
        idx = end
    return rows


def _via_http(path: str) -> list:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "cigar-pairing"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    rows: list = []
    url = f"{API}{path}&per_page=100" if "?" in path else f"{API}{path}?per_page=100"
    while url:
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                rows.extend(json.loads(resp.read().decode("utf-8")))
                link = resp.headers.get("Link") or ""
        except urllib.error.HTTPError as exc:
            hint = " (bez tokena GitHub dopušta 60 zahtjeva na sat)" if not token else ""
            raise SystemExit(f"GitHub je odbio zahtjev: {exc.code} {exc.reason}{hint}")
        except urllib.error.URLError as exc:
            raise SystemExit(f"GitHub nije dostupan: {exc.reason}")
        url = None
        for part in link.split(","):
            if 'rel="next"' in part:
                url = part.split(";")[0].strip().strip("<>")
    return rows


def fetch_issues(repo: str, label: str, state: str) -> list[dict]:
    path = f"/repos/{repo}/issues?state={state}&labels={label}"
    rows = _via_gh(path)
    if rows is None:
        rows = _via_http(path)
    # GitHub pod "issues" vraca i pull requestove — oni ovdje nisu dojmovi
    return [r for r in rows if isinstance(r, dict) and "pull_request" not in r]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=DEFAULT_REPO)
    ap.add_argument("--label", default=DEFAULT_LABEL)
    ap.add_argument("--state", default="all", choices=("open", "closed", "all"))
    ap.add_argument("--dry-run", action="store_true", help="ne piši, samo pokaži")
    args = ap.parse_args()

    issues = fetch_issues(args.repo, args.label, args.state)
    print(f"prijava s oznakom „{args.label}”: {len(issues)}")
    if not issues:
        print("nema što pokupiti — provjeri da oznaka postoji i da je prijava označena")
        return 0

    resolve = _imp.resolver()
    kept = _imp.load_store()
    total_new = total_upd = total_skip = 0
    ignored = []

    # od najstarije prema najnovijoj, da novija ocjena iste osobe pobijedi
    for issue in sorted(issues, key=lambda i: i.get("number", 0)):
        number = issue.get("number")
        body = issue.get("body") or ""
        try:
            payload = _imp.extract_payload(body)
        except SystemExit:
            ignored.append((number, "nema uredan blok s podacima"))
            continue
        try:
            by, added, updated, skipped = _imp.merge_payload(
                kept, payload, resolve, source=f"{args.repo}#{number}"
            )
        except ValueError:
            ignored.append((number, "izvještaj nije potpisan"))
            continue
        total_new += added
        total_upd += updated
        total_skip += skipped
        print(f"  #{number} {by}: novih {added}, izmijenjenih {updated}, preskočenih {skipped}")

    for number, why in ignored:
        print(f"  #{number} preskočena: {why}", file=sys.stderr)

    print(f"ukupno: novih {total_new}, izmijenjenih {total_upd}, preskočenih {total_skip}")
    if args.dry_run:
        print("(dry-run — ništa nije zapisano)")
        return 0
    count = _imp.save_store(kept)
    print(f"-> {_imp.STORE} ({count} dojmova)")
    print("Sada: python3 scripts/apply-taste-reports.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
