#!/usr/bin/env python3
"""
Deterministic, idempotent vitola dedup pass (Stream A of the 2026-07-23 plan).

Runs over the WHOLE cigars.json (base + market). Collapses:
  1. locale-twin vitolas — same shop product ingested from /en/ and /hr/ pages,
     parsed under different names (No.4 vs Connecticut No.4, Half Corona vs
     Corona, ...). Grouped by locale-normalized product URL.
  2. sampler/gift self-vitolas — a "Robusto Sampler" line that also carries a
     redundant "Robusto Sampler" vitola row next to the concrete "Robusto".

Optional inputs (produced by parallel streams; used when present):
  - scripts/data/vitola_lexicon.json      (Stream B: slug -> canonical name)
  - scripts/data/vitola_dedup_decisions.json (Stream C: per-cigar merge/keep)
  - scripts/data/dimension_fixes.json     (Stream D: cigarId::name -> ring/lmm)

Emits scripts/output/vitola_dedup_audit.json (merges + prefix_suspects for C).
Re-running on already-normalized data is a no-op (byte-identical).

Usage:  python3 scripts/normalize-vitolas.py [--check]
        --check exits non-zero if the file would change (CI guard).
"""
import json
import re
import sys
import collections
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
CIGARS = APP / "src/data/cigars.json"
OUTDIR = APP / "scripts/output"
AUDIT = OUTDIR / "vitola_dedup_audit.json"
LEXICON = APP / "scripts/data/vitola_lexicon.json"
DECISIONS = APP / "scripts/data/vitola_dedup_decisions.json"
DIMFIX = APP / "scripts/data/dimension_fixes.json"


def load(p, default=None):
    if Path(p).exists():
        return json.loads(Path(p).read_text(encoding="utf-8"))
    return default


def write_cigars(obj):
    CIGARS.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def norm_url(u):
    """Locale-normalized product URL — /en/ and /hr/ variants collapse to one."""
    if not u:
        return None
    u = u.split("?")[0].split("#")[0]
    u = re.sub(r"(humidor\.hr|havana-cigar-shop\.com)/(?:hr|en)/proizvod/", r"\1/proizvod/", u)
    u = re.sub(r"cigarworld\.de/(?:en|de)/", "cigarworld.de/", u)
    return u.rstrip("/")


def slug_tail(url):
    """Last path segment of a normalized product URL (the vitola-bearing slug)."""
    if not url:
        return ""
    return url.rstrip("/").split("/")[-1]


def toks(s):
    return [
        t
        for t in re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).split()
        if t and not (len(t) == 1 and t.isalpha())
    ]


def toks_all(s):
    """Like toks() but KEEPS single-char tokens — roman numerals / letters
    distinguish vitolas (Siglo I vs Siglo V), so they must survive here."""
    return [t for t in re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).split() if t]


def product_key(v):
    """Locale-normalized key for a vitola, ONLY from a real product page.

    Restricted to '/proizvod/' (humidor.hr / havana-cigar-shop.com) product
    URLs — the shops whose /en/ and /hr/ pages create the twins. Listing /
    search URLs (and shared cross-vitola regionLinks) are deliberately ignored
    so unrelated vitolas never collapse together.
    """
    u = norm_url(v.get("url"))
    if u and "/proizvod/" in u:
        return u
    return None


def parse_dims(fmt):
    m = re.search(r"(\d+)\s*[x×]\s*(\d+)\s*mm", fmt or "")
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def has_dims(fmt):
    return parse_dims(fmt)[0] is not None


# --- union-find over a cigar's vitolas by shared normalized URL --------------
def url_groups(vitolas):
    parent = list(range(len(vitolas)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a, b):
        parent[find(a)] = find(b)

    by_url = collections.defaultdict(list)
    for i, v in enumerate(vitolas):
        u = product_key(v)
        if u:
            by_url[u].append(i)
    for idxs in by_url.values():
        for j in idxs[1:]:
            union(idxs[0], j)

    groups = collections.defaultdict(list)
    for i in range(len(vitolas)):
        groups[find(i)].append(i)
    # keep original order of first appearance
    ordered = []
    seen = set()
    for i in range(len(vitolas)):
        r = find(i)
        if r not in seen:
            seen.add(r)
            ordered.append(groups[r])
    return ordered


def canonical_name(members, rep_url, brand, line, lexicon):
    slug = slug_tail(rep_url)
    if slug and slug in lexicon:
        return lexicon[slug]
    strip = set(toks(brand)) | set(toks(line))
    tail = [t for t in toks(slug) if t not in strip]
    tailset = set(tail)
    best, best_score = None, None
    for m in members:
        name = m["name"]
        nt = [t for t in toks(name) if t not in strip]
        hits = sum(1 for t in nt if t in tailset)
        # more slug-token hits wins; tiebreak = shorter name (fewer tokens)
        score = (hits, -len(nt), -len(name))
        if best is None or score > best_score:
            best, best_score = name, score
    return best


def merge_group(members, canonical):
    """Merge locale twins into one vitola; primary = member with canonical name."""
    primary = next((m for m in members if m["name"] == canonical), members[0])
    out = dict(primary)
    out["name"] = canonical
    # real dimensions win over "—"
    if not has_dims(out.get("format")):
        for m in members:
            if has_dims(m.get("format")):
                out["format"] = m["format"]
                break
    # fill missing scalar fields from other members
    for key in ("smokeTimeMin", "priceEUR", "url"):
        if out.get(key) in (None, "", "—"):
            for m in members:
                if m.get(key) not in (None, "", "—"):
                    out[key] = m[key]
                    break
    # union regionLinks: primary first, then fill absent regions
    links = {}
    for m in [primary] + [x for x in members if x is not primary]:
        for region, rl in (m.get("regionLinks") or {}).items():
            links.setdefault(region, rl)
    if links:
        out["regionLinks"] = {r: links[r] for r in ("HR", "EU", "USA") if r in links}
    elif "regionLinks" in out:
        del out["regionLinks"]
    return out


def is_sampler(cig):
    hay = f"{cig.get('line','')} {cig.get('vitola','')}".lower()
    return "sampler" in hay or "gift" in hay


def semantic_key(name, prefix):
    """Tokens of a vitola name after dropping a LEADING run of brand/line
    tokens. 'Serie V Belicoso' (line Serie V) -> ('belicoso',); 'V No.4' ->
    ('no','4'). Only leading tokens are stripped, so distinct middles never
    collide (Serie V Melanio Robusto stays separate from Serie V Robusto).
    Single-char tokens are kept so Siglo I and Siglo V don't collapse."""
    tt = toks_all(name)
    i = 0
    while i < len(tt) and tt[i] in prefix:
        i += 1
    return tuple(tt[i:]) or tuple(tt)


def normalize(cigars, lexicon, decisions, dimfix):
    audit = {
        "locale_twin_merges": [],
        "semantic_merges": [],
        "sampler_collapses": [],
        "prefix_suspects": [],
        "shared_region_urls": [],
        "duplicate_line_suspects": [],
    }
    for cig in cigars:
        vitolas = cig.get("vitolas") or []
        if not vitolas:
            continue
        cid = cig["id"]
        original_default = cig.get("vitola")
        changed = False

        # 1) locale-twin collapse ------------------------------------------------
        groups = url_groups(vitolas)
        if any(len(g) > 1 for g in groups):
            new_vitolas = []
            used_names = set()
            for g in groups:
                members = [vitolas[i] for i in g]
                if len(members) == 1:
                    new_vitolas.append(members[0])
                    used_names.add(members[0]["name"])
                    continue
                urls = collections.Counter()
                for m in members:
                    u = product_key(m)
                    if u:
                        urls[u] += 1
                rep_url = urls.most_common(1)[0][0] if urls else ""
                canon = canonical_name(members, rep_url, cig["brand"], cig["line"], lexicon)
                # avoid colliding with a distinct existing vitola name
                if canon in used_names:
                    canon = max((m["name"] for m in members), key=len)
                merged = merge_group(members, canon)
                new_vitolas.append(merged)
                used_names.add(canon)
                audit["locale_twin_merges"].append(
                    {"id": cid, "kept": canon, "dropped": [m["name"] for m in members if m["name"] != canon]}
                )
                changed = True
            vitolas = new_vitolas

        # 1b) semantic within-line dedup: same vitola named with/without the
        #     redundant brand/line/series prefix (Belicoso == Serie V Belicoso).
        #     Guard: never merge when the members carry CONFLICTING real
        #     dimensions — that means genuinely different sizes (kept + flagged).
        prefix = set(toks_all(cig["brand"])) | set(toks_all(cig["line"]))
        groups2 = collections.OrderedDict()
        for v in vitolas:
            groups2.setdefault(semantic_key(v["name"], prefix), []).append(v)
        if any(len(g) > 1 for g in groups2.values()):
            new_vitolas = []
            for members in groups2.values():
                if len(members) == 1:
                    new_vitolas.append(members[0])
                    continue
                dims = {parse_dims(v.get("format")) for v in members if has_dims(v.get("format"))}
                if len(dims) > 1:  # conflicting sizes → not the same vitola
                    new_vitolas.extend(members)
                    audit["prefix_suspects"].append(
                        {"id": cid, "brand": cig["brand"], "line": cig["line"],
                         "conflict": [{"name": m["name"], "format": m.get("format")} for m in members]}
                    )
                    continue
                rep = min(members, key=lambda m: (len(toks_all(m["name"])), len(m["name"])))
                new_vitolas.append(merge_group(members, rep["name"]))
                audit["semantic_merges"].append(
                    {"id": cid, "kept": rep["name"], "dropped": [m["name"] for m in members if m is not rep]}
                )
                changed = True
            vitolas = new_vitolas

        # 2) Stream C decisions (explicit merges) -------------------------------
        dec = (decisions or {}).get(cid)
        if dec and dec.get("merge"):
            for pair in dec["merge"]:
                names = set(pair)
                grp = [v for v in vitolas if v["name"] in names]
                if len(grp) < 2:
                    continue
                canon = canonical_name(grp, slug_tail(norm_url(grp[0].get("url"))), cig["brand"], cig["line"], lexicon)
                if canon not in names:
                    canon = min(pair, key=len)
                merged = merge_group(grp, canon)
                vitolas = [v for v in vitolas if v["name"] not in names] + [merged]
                changed = True

        # 3) sampler self-vitola collapse ---------------------------------------
        if is_sampler(cig) and len(vitolas) > 1:
            concrete = [v for v in vitolas if not re.search(r"\b(sampler|gift)\b", v["name"].lower())]
            if concrete and len(concrete) < len(vitolas):
                dropped = [v["name"] for v in vitolas if v not in concrete]
                vitolas = concrete
                audit["sampler_collapses"].append({"id": cid, "kept": [v["name"] for v in vitolas], "dropped": dropped})
                changed = True

        # 4) Stream D dimension fixes -------------------------------------------
        if dimfix:
            for v in vitolas:
                fx = dimfix.get(f"{cid}::{v['name']}")
                if fx and fx.get("ring") and fx.get("lmm"):
                    newfmt = f"{fx['ring']} x {fx['lmm']}mm"
                    if v.get("format") != newfmt:
                        v["format"] = newfmt
                        changed = True

        if changed:
            # keep default vitola / derived top-level fields consistent
            names = [v["name"] for v in vitolas]
            if original_default not in names:
                def sortkey(v):
                    r, l = parse_dims(v.get("format"))
                    return (r if r is not None else 9999, l if l is not None else 9999, v["name"])
                dv = sorted(vitolas, key=sortkey)[0]
                cig["vitola"] = dv["name"]
                if has_dims(dv.get("format")):
                    cig["format"] = dv["format"]
                if dv.get("smokeTimeMin") is not None:
                    cig["smokeTimeMin"] = dv["smokeTimeMin"]
            cig["vitolas"] = vitolas

        # prefix-dup suspects (for Stream C) — not auto-merged
        for i in range(len(vitolas)):
            for j in range(i + 1, len(vitolas)):
                a, b = vitolas[i], vitolas[j]
                if (
                    has_dims(a.get("format"))
                    and a.get("format") == b.get("format")
                    and a.get("priceEUR") is not None
                    and a.get("priceEUR") == b.get("priceEUR")
                ):
                    na, nb = a["name"].lower(), b["name"].lower()
                    if na != nb and (na in nb or nb in na):
                        audit["prefix_suspects"].append(
                            {"id": cid, "brand": cig["brand"], "line": cig["line"],
                             "a": a["name"], "b": b["name"], "format": a["format"], "price": a["priceEUR"]}
                        )

    # --- link worklist for the network streams (H/I) -----------------------
    # Region URL reused by >1 cigar => a listing/category page, not a per-product
    # link (e.g. holts oliva-monticello.html on Monticello AND Monticello Double).
    url_owners = collections.defaultdict(set)
    for cig in cigars:
        for v in cig.get("vitolas") or []:
            for rl in (v.get("regionLinks") or {}).values():
                u = (rl or {}).get("url") if isinstance(rl, dict) else None
                if u:
                    url_owners[u].add(cig["id"])
    for u, ids in sorted(url_owners.items()):
        if len(ids) > 1:
            audit["shared_region_urls"].append({"url": u, "cigars": sorted(ids)})

    # Lines within a brand where one name is a strict prefix of another
    # (Serie V ⊂ Serie V / Melanio, Monticello ⊂ Monticello Double) — suspects
    # for human/agent adjudication (some, like Flor de *, are genuinely distinct).
    by_brand = collections.defaultdict(list)
    for cig in cigars:
        by_brand[cig["brand"]].append(cig)
    for brand, cs in by_brand.items():
        for a in cs:
            for b in cs:
                if a is b:
                    continue
                la, lb = a["line"].strip(), b["line"].strip()
                if la and lb != la and lb.lower().startswith(la.lower() + " "):
                    audit["duplicate_line_suspects"].append(
                        {"brand": brand, "line_a": la, "id_a": a["id"], "line_b": lb, "id_b": b["id"]}
                    )
    return audit


def main():
    check = "--check" in sys.argv
    cigars = load(CIGARS)
    before = json.dumps(cigars, ensure_ascii=False, indent=2) + "\n"
    lexicon = load(LEXICON, {}) or {}
    if isinstance(lexicon, dict) and "slugs" in lexicon:
        lexicon = lexicon["slugs"]
    decisions = load(DECISIONS, {}) or {}
    dimfix = load(DIMFIX, {}) or {}

    audit = normalize(cigars, lexicon, decisions, dimfix)
    after = json.dumps(cigars, ensure_ascii=False, indent=2) + "\n"

    OUTDIR.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    stats = {
        "locale_twin_merges": len(audit["locale_twin_merges"]),
        "semantic_merges": len(audit["semantic_merges"]),
        "sampler_collapses": len(audit["sampler_collapses"]),
        "prefix_suspects": len(audit["prefix_suspects"]),
        "shared_region_urls": len(audit["shared_region_urls"]),
        "duplicate_line_suspects": len(audit["duplicate_line_suspects"]),
        "changed": before != after,
    }
    print(json.dumps(stats, ensure_ascii=False, indent=2))

    if check:
        sys.exit(1 if before != after else 0)
    write_cigars(cigars)


if __name__ == "__main__":
    main()
