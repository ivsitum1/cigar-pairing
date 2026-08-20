# -*- coding: utf-8 -*-
"""Cross-check rums.json against the RumRatings community scores.

Reads:  app/scripts/output/rumratings_raw.json (scrape-rumratings.py)
        app/src/data/rums.json
Writes: app/scripts/output/rumratings_compare.json   (machine-readable join)
        app/scripts/output/rumratings_report.md      (HR report to read)

  python scripts/compare-rumratings.py
  python scripts/compare-rumratings.py --min-votes 50 --gap 1.5

Read-only: it never touches src/data. Ratings are opinions of a different
crowd on a different scale, so the report compares two ways — the raw
delta on the shared 1-10 axis, and the *rank* delta inside each list, which
is the fair question ("do we order the shelf the same way?").

Review text is collected as SOURCE QUOTES for the Club/Bonton worklists.
It is other people's writing: rewrite it editorially, never paste it in.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path

from rumratings_shared import OUT_DIR, best_match, percentile_rank, spearman

RAW = OUT_DIR / "rumratings_raw.json"
RUMS = Path(__file__).resolve().parent.parent / "src" / "data" / "rums.json"
JOIN = OUT_DIR / "rumratings_compare.json"
REPORT = OUT_DIR / "rumratings_report.md"

# Sentences worth an editor's eye for Club facts: history, process, place.
STORY_MARKERS = re.compile(
    r"(?i)\b(founded|since 1[6-9]\d\d|in 1[6-9]\d\d|in 20[0-2]\d|distiller[yi]|estate|"
    r"pot still|column still|coffey|dunder|muck|marque|continental|ester|"
    r"named after|legend|history|historic|tradition|family|generation|"
    r"solera|dunnage|warehouse|hurricane|closed|reopened|revived|"
    r"molasses|cane juice|agricole|terroir|volcanic|blender|master blender)\b"
)
# Sentences about how it is served / shared at a table: Bonton material.
BONTON_MARKERS = re.compile(
    r"(?i)\b(neat|on the rocks|with ice|glassware|glencairn|snifter|copita|"
    r"pour|sipping|sipper|after dinner|digestif|nightcap|share|shared|"
    r"guest|host|offer|toast|cigar|pairing|paired|first sip|let it breathe|"
    r"open up|water|dilut)\w*\b"
)
NOISE = re.compile(r"(?i)\b(shipping|amazon|buy it|price|bought|store|link|http)\b")


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if 30 <= len(p.strip()) <= 300]


def mine(reviews: list[dict], pattern: re.Pattern, cap: int = 4) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for rev in reviews:
        for sent in sentences(rev.get("text") or ""):
            if not pattern.search(sent) or NOISE.search(sent):
                continue
            key = re.sub(r"\W+", "", sent.lower())[:60]
            if key in seen:
                continue
            seen.add(key)
            out.append(sent)
            if len(out) >= cap:
                return out
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-votes", type=int, default=25,
                    help="ignore community scores thinner than this")
    ap.add_argument("--gap", type=float, default=1.2,
                    help="raw-score delta that counts as a disagreement")
    ap.add_argument("--rank-gap", type=float, default=0.25,
                    help="percentile delta that counts as a rank disagreement")
    ap.add_argument("--floor", type=float, default=0.55, help="name-match threshold")
    args = ap.parse_args()

    if not RAW.exists():
        raise SystemExit(
            f"missing {RAW}\nRun: python scripts/scrape-rumratings.py  (needs network access "
            "to rumratings.com)"
        )
    community = json.loads(RAW.read_text("utf-8"))
    catalog = json.loads(RUMS.read_text("utf-8"))

    solid = [c for c in community if (c.get("votes") or 0) >= args.min_votes and c.get("rating")]
    ours_pop = [r["qualityScore"] for r in catalog if r.get("qualityScore") is not None]
    theirs_pop = [c["rating"] for c in solid]

    matched: list[dict] = []
    used: set[str] = set()
    for rum in catalog:
        hit, score = best_match(rum["name"], solid, floor=args.floor)
        if not hit or hit["url"] in used:
            continue
        used.add(hit["url"])
        ours, theirs = rum.get("qualityScore"), hit["rating"]
        if ours is None:
            continue
        matched.append(
            {
                "id": rum["id"],
                "name": rum["name"],
                "style": rum.get("style"),
                "region": rum.get("region"),
                "ourScore": ours,
                "communityScore": theirs,
                "votes": hit.get("votes"),
                "delta": round(ours - theirs, 2),
                "ourPercentile": percentile_rank(ours, ours_pop),
                "communityPercentile": percentile_rank(theirs, theirs_pop),
                "matchScore": round(score, 3),
                "communityName": hit["name"],
                "url": hit["url"],
                "storyQuotes": mine(hit.get("reviews") or [], STORY_MARKERS),
                "bontonQuotes": mine(hit.get("reviews") or [], BONTON_MARKERS, cap=3),
            }
        )
    for row in matched:
        row["rankDelta"] = round(row["ourPercentile"] - row["communityPercentile"], 3)

    unmatched_theirs = [
        c for c in solid
        if c["url"] not in used and best_match(c["name"], catalog, floor=args.floor)[0] is None
    ]
    unmatched_theirs.sort(key=lambda c: (-(c["rating"]), -(c.get("votes") or 0)))

    pairs = [(m["ourScore"], m["communityScore"]) for m in matched]
    summary = {
        "communityBottles": len(community),
        "communityBottlesSolid": len(solid),
        "catalogBottles": len(catalog),
        "matched": len(matched),
        "spearman": spearman(pairs),
        "meanAbsDelta": round(statistics.mean(abs(m["delta"]) for m in matched), 2) if matched else None,
        "meanBias": round(statistics.mean(m["delta"] for m in matched), 2) if matched else None,
        "withinHalfPoint": sum(1 for m in matched if abs(m["delta"]) <= 0.5),
        "rankAgreeWithin20pct": sum(1 for m in matched if abs(m["rankDelta"]) <= 0.2),
        "minVotes": args.min_votes,
    }

    JOIN.write_text(
        json.dumps(
            {
                "summary": summary,
                "matched": matched,
                "candidates": unmatched_theirs[:120],
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        "utf-8",
    )
    REPORT.write_text(render(summary, matched, unmatched_theirs, args), "utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print(f"\n{JOIN.name} + {REPORT.name} written to scripts/output/")


def render(summary: dict, matched: list[dict], candidates: list[dict], args) -> str:
    L: list[str] = []
    add = L.append
    add("# RumRatings × naš indeks\n")
    add("Automatski izvještaj (`scripts/compare-rumratings.py`). Ocjene zajednice su\n"
        "mišljenje druge publike na drugoj skali — zato se gleda i sirova razlika i\n"
        "razlika u *rangu* unutar svake liste.\n")

    add("\n## 1. Koliko se poklapamo\n")
    add(f"- Boca u našem indeksu: **{summary['catalogBottles']}**")
    add(f"- Boca s RumRatingsa (≥ {summary['minVotes']} glasova): **{summary['communityBottlesSolid']}** "
        f"od {summary['communityBottles']} skinutih")
    add(f"- Spojeno po imenu: **{summary['matched']}**")
    add(f"- Spearman (poklapanje redoslijeda): **{summary['spearman']}**")
    add(f"- Prosječna apsolutna razlika: **{summary['meanAbsDelta']}** boda; "
        f"sustavni pomak (mi − oni): **{summary['meanBias']}**")
    add(f"- Unutar ±0,5 boda: **{summary['withinHalfPoint']}** / {summary['matched']}")
    add(f"- Isti rang (±20 percentila): **{summary['rankAgreeWithin20pct']}** / {summary['matched']}")

    over = sorted([m for m in matched if m["delta"] >= args.gap], key=lambda m: -m["delta"])
    under = sorted([m for m in matched if m["delta"] <= -args.gap], key=lambda m: m["delta"])

    add("\n## 2. Gdje se ne slažemo\n")
    add(f"\n### Mi hvalimo više nego zajednica (Δ ≥ {args.gap})\n")
    add(_table(over))
    add(f"\n### Zajednica hvali više nego mi (Δ ≤ −{args.gap})\n")
    add(_table(under))
    add("\n> Razlika sama po sebi nije greška: naša ocjena je *unutar stila* i ne kažnjava\n"
        "> aditive, a zajednica voli slađe profile. Provjeri redom one gdje se **i rang**\n"
        "> razilazi — to su kandidati za rekalibraciju, ne pojedinačni bodovi.\n")

    rank_off = sorted(
        [m for m in matched if abs(m["rankDelta"]) >= args.rank_gap],
        key=lambda m: -abs(m["rankDelta"]),
    )[:25]
    add(f"\n### Razilaženje u rangu (|Δ percentila| ≥ {args.rank_gap})\n")
    add("| Boca | naš percentil | njihov | Δ |")
    add("| --- | ---: | ---: | ---: |")
    for m in rank_off:
        add(f"| {m['name']} | {m['ourPercentile']:.2f} | {m['communityPercentile']:.2f} | {m['rankDelta']:+.2f} |")

    add("\n## 3. Boce koje nemamo, a zajednica ih drži visoko\n")
    add("| Boca | ocjena | glasova | link |")
    add("| --- | ---: | ---: | --- |")
    for c in candidates[:40]:
        add(f"| {c['name']} | {c['rating']} | {c.get('votes') or '—'} | {c['url']} |")
    add("\nKandidati za `rums.json` — provjeri dostupnost u HR prije unosa (`shopHR`).\n")

    story = [m for m in matched if m["storyQuotes"]]
    add(f"\n## 4. Materijal za Club — priče i zanimljivosti ({len(story)} boca)\n")
    add("**Izvorni citati, za uredničku preradu — ne kopirati doslovno u `club.json`.**\n")
    for m in story[:60]:
        add(f"\n### {m['name']} ({m['communityScore']} / {m['votes']} gl.) — {m['url']}")
        for q in m["storyQuotes"]:
            add(f"- {q}")

    bonton = [m for m in matched if m["bontonQuotes"]]
    add(f"\n## 5. Materijal za knjigu o bontonu ({len(bonton)} boca)\n")
    add("Zapažanja o serviranju, čaši, ritmu i dijeljenju za stolom. Isto pravilo:\n"
        "polazište za pisanje, ne citat.\n")
    for m in bonton[:40]:
        add(f"\n### {m['name']} — {m['url']}")
        for q in m["bontonQuotes"]:
            add(f"- {q}")

    weak = sorted([m for m in matched if m["matchScore"] < 0.7], key=lambda m: m["matchScore"])
    add(f"\n## 6. Spojevi imena za provjeru ({len(weak)})\n")
    add("Slabije poklapanje imena — potvrdi da je riječ o istoj boci prije nego što\n"
        "ijedan broj iz gornjih tablica uzmeš zdravo za gotovo.\n")
    add("| Naše ime | Njihovo ime | poklapanje |")
    add("| --- | --- | ---: |")
    for m in weak[:40]:
        add(f"| {m['name']} | {m['communityName']} | {m['matchScore']:.2f} |")

    return "\n".join(L) + "\n"


def _table(rows: list[dict]) -> str:
    if not rows:
        return "_nema_\n"
    out = ["| Boca | naša | zajednica | Δ | glasova |", "| --- | ---: | ---: | ---: | ---: |"]
    for m in rows[:30]:
        out.append(
            f"| {m['name']} | {m['ourScore']} | {m['communityScore']} | {m['delta']:+.2f} | {m['votes'] or '—'} |"
        )
    return "\n".join(out)


if __name__ == "__main__":
    main()
