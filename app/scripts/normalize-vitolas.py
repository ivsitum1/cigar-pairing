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
  - scripts/data/line_merge_decisions.json (Stream J: absorb / keep / relocate)
  - scripts/data/vitola_link_fixes.json  (Stream I/D: per-vitola/cigar URL+format)

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
LINE_MERGES = APP / "scripts/data/line_merge_decisions.json"
LINK_FIXES = APP / "scripts/data/vitola_link_fixes.json"


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


def _union_region_links(dst, src):
    links = dict(dst.get("regionLinks") or {})
    for region, rl in (src.get("regionLinks") or {}).items():
        links.setdefault(region, rl)
    if links:
        dst["regionLinks"] = {r: links[r] for r in ("HR", "EU", "USA") if r in links}


def _append_or_merge_vitola(canon, vitola, brand=None, line=None):
    """Add vitola to canon; merge on exact name or semantic key when dims agree."""
    existing_list = canon.get("vitolas") or []
    existing = {v["name"]: v for v in existing_list}
    name = vitola["name"]
    target_name = None
    if name in existing:
        target_name = name
    elif brand is not None:
        prefix = set(toks_all(brand)) | set(toks_all(line or ""))
        sk = semantic_key(name, prefix)
        if sk:
            for v in existing_list:
                if semantic_key(v["name"], prefix) == sk:
                    target_name = v["name"]
                    break
    if target_name is None:
        canon.setdefault("vitolas", []).append(vitola)
        return "added"
    cur = existing[target_name]
    dims_a = parse_dims(cur.get("format"))
    dims_b = parse_dims(vitola.get("format"))
    real_a = dims_a[0] is not None
    real_b = dims_b[0] is not None
    if real_a and real_b and dims_a != dims_b:
        if name not in existing:
            canon.setdefault("vitolas", []).append(vitola)
            return "added-conflict"
        return "conflict"
    # prefer shorter / less-prefixed display name
    canon_name = min([cur["name"], vitola["name"]], key=lambda n: (len(toks_all(n)), len(n)))
    merged = merge_group([cur, vitola], canon_name)
    canon["vitolas"] = [merged if v["name"] == target_name else v for v in canon["vitolas"]]
    return "merged"


def apply_line_decisions(cigars, line_decisions, audit):
    """Stream J: absorb duplicate lines, relocate misfiled vitolas, filter suspects.

    Decision file shape:
      { "<canonicalId>": { "absorb": ["<otherId>"], "rename_absorbed_vitolas": {...} },
        "_keep_distinct": [ {"ids": [...], "reason": "..."} ],
        "_relocate_vitolas": [ {"from": "...", "to": "...", "names": [...]} ] }
    Keys starting with '_' are metadata / non-merge directives.
    """
    if not line_decisions:
        return cigars

    audit.setdefault("line_merges", [])
    audit.setdefault("vitola_relocations", [])
    audit.setdefault("keep_distinct", [])

    by_id = {c["id"]: c for c in cigars}
    remove_ids = set()

    # --- absorb duplicate lines into a canonical id ---------------------------
    for canon_id, spec in line_decisions.items():
        if canon_id.startswith("_") or not isinstance(spec, dict):
            continue
        absorb = spec.get("absorb") or []
        if not absorb:
            continue
        canon = by_id.get(canon_id)
        if not canon:
            continue
        renames = spec.get("rename_absorbed_vitolas") or {}
        absorbed_now = []
        already_gone = []
        for abs_id in absorb:
            other = by_id.get(abs_id)
            if not other:
                if abs_id not in by_id:
                    already_gone.append(abs_id)
                continue
            if abs_id in remove_ids:
                continue
            for v in other.get("vitolas") or []:
                vv = dict(v)
                if vv["name"] in renames:
                    vv["name"] = renames[vv["name"]]
                _append_or_merge_vitola(canon, vv, canon.get("brand"), canon.get("line"))
            _union_region_links(canon, other)
            mk = list(dict.fromkeys((canon.get("markets") or []) + (other.get("markets") or [])))
            if mk:
                canon["markets"] = mk
            remove_ids.add(abs_id)
            absorbed_now.append(abs_id)
        if absorbed_now:
            audit["line_merges"].append(
                {
                    "canonical": canon_id,
                    "absorbed": absorbed_now,
                    "line": canon.get("line"),
                    "reason": spec.get("reason"),
                    "status": "applied",
                }
            )
        elif already_gone:
            audit["line_merges"].append(
                {
                    "canonical": canon_id,
                    "absorbed": already_gone,
                    "line": canon.get("line"),
                    "reason": spec.get("reason"),
                    "status": "already_applied",
                }
            )

    if remove_ids:
        cigars = [c for c in cigars if c["id"] not in remove_ids]
        by_id = {c["id"]: c for c in cigars}

    # --- relocate misfiled vitolas between kept-distinct lines ----------------
    for move in line_decisions.get("_relocate_vitolas") or []:
        src = by_id.get(move.get("from"))
        dst = by_id.get(move.get("to"))
        names = set(move.get("names") or [])
        if not src or not dst or not names:
            continue
        keep, moved, already = [], [], []
        src_names = {v["name"] for v in (src.get("vitolas") or [])}
        for want in names:
            if want not in src_names:
                already.append(want)
        for v in src.get("vitolas") or []:
            if v["name"] in names:
                _append_or_merge_vitola(dst, dict(v), dst.get("brand"), dst.get("line"))
                moved.append(v["name"])
            else:
                keep.append(v)
        if moved:
            src["vitolas"] = keep
            if src.get("vitola") in moved:
                non_samp = [
                    v
                    for v in keep
                    if not re.search(r"\b(sampler|gift)\b", v["name"].lower())
                ]
                pick = non_samp or keep
                src["vitola"] = pick[0]["name"] if pick else src.get("vitola")
            audit["vitola_relocations"].append(
                {
                    "from": src["id"],
                    "to": dst["id"],
                    "moved": moved,
                    "reason": move.get("reason"),
                    "status": "applied",
                }
            )
        elif already:
            audit["vitola_relocations"].append(
                {
                    "from": src["id"],
                    "to": dst["id"],
                    "moved": already,
                    "reason": move.get("reason"),
                    "status": "already_applied",
                }
            )

    # record keep_distinct adjudications
    for kd in line_decisions.get("_keep_distinct") or []:
        audit["keep_distinct"].append(kd)

    # drop adjudicated pairs from duplicate_line_suspects
    decided_pairs = set()
    for m in audit.get("line_merges") or []:
        for abs_id in m.get("absorbed") or []:
            decided_pairs.add(frozenset((m["canonical"], abs_id)))
    for kd in line_decisions.get("_keep_distinct") or []:
        ids = kd.get("ids") or []
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                decided_pairs.add(frozenset((ids[i], ids[j])))

    if decided_pairs and audit.get("duplicate_line_suspects"):
        audit["duplicate_line_suspects"] = [
            s
            for s in audit["duplicate_line_suspects"]
            if frozenset((s.get("id_a"), s.get("id_b"))) not in decided_pairs
        ]

    # drop absorbed cigar ids from shared_region_urls worklist
    if remove_ids and audit.get("shared_region_urls"):
        cleaned = []
        for row in audit["shared_region_urls"]:
            left = [i for i in row.get("cigars") or [] if i not in remove_ids]
            if len(left) > 1:
                cleaned.append({"url": row["url"], "cigars": sorted(left)})
        audit["shared_region_urls"] = cleaned

    return cigars


def normalize(cigars, lexicon, decisions, dimfix):
    audit = {
        "locale_twin_merges": [],
        "semantic_merges": [],
        "sampler_collapses": [],
        "prefix_suspects": [],
        "shared_region_urls": [],
        "duplicate_line_suspects": [],
        "line_merges": [],
        "vitola_relocations": [],
        "keep_distinct": [],
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


def is_holts_listing(url):
    """Holt's /all-cigar-brands/*.html pages are line listings, never a single SKU."""
    if not url:
        return False
    return bool(
        re.search(
            r"holts\.com/cigars/all-cigar-brands/[^/?#]+\.html",
            url,
            re.I,
        )
    )


def demote_holts_listings(cigars, audit):
    """Stream H (deterministic): move Holts listing URLs off vitolas onto the cigar.

    A listing page shared across every size (or across sibling lines) must not
    claim to be the product URL of a specific vitola. Keep it on
    cigar.regionLinks so USA still has a useful line-level Holts link.
    """
    audit.setdefault("listing_demotions", [])
    for cig in cigars:
        lifted = {}
        touched = False
        for v in cig.get("vitolas") or []:
            rl = v.get("regionLinks") or {}
            keep = {}
            for region, link in rl.items():
                u = (link or {}).get("url") if isinstance(link, dict) else None
                if u and is_holts_listing(u):
                    lifted.setdefault(region, link)
                    touched = True
                else:
                    keep[region] = link
            if keep:
                v["regionLinks"] = keep
            elif "regionLinks" in v:
                del v["regionLinks"]
            if v.get("url") and is_holts_listing(v["url"]):
                v["url"] = None
                touched = True
        if not touched:
            continue
        links = dict(cig.get("regionLinks") or {})
        for region, link in lifted.items():
            links.setdefault(region, link)
        if links:
            cig["regionLinks"] = {r: links[r] for r in ("HR", "EU", "USA") if r in links}
        audit["listing_demotions"].append(
            {
                "id": cig["id"],
                "regions": sorted(lifted.keys()),
                "url": next(
                    ((lifted[r] or {}).get("url") for r in ("USA", "EU", "HR") if r in lifted),
                    None,
                ),
            }
        )


def serie_token(text):
    m = re.search(r"\bserie[\s\-]+([a-z0-9]+)\b", (text or "").lower())
    return m.group(1) if m else None


def pick_product_url(cig):
    """Best /proizvod/ URL on this cigar — prefer non-sampler SKUs."""
    urls = []
    for v in cig.get("vitolas") or []:
        vu = v.get("url")
        if vu and "/proizvod/" in vu and not is_holts_listing(vu):
            urls.append(vu)
    non_samp = [u for u in urls if not re.search(r"\b(sampler|gift)\b", u, re.I)]
    return (non_samp or urls or [None])[0]


def scrub_mismatched_price_urls(cigars, audit):
    """Stream I (deterministic): drop priceUrl when its serie letter ≠ line serie.

    Classic mis-hit: Serie V / Melanio priceUrl → oliva-serie-o-robusto.
    Prefer a real /proizvod/ URL from the cigar's own vitolas when available.
    Also upgrade a sampler/gift priceUrl when a non-sampler product URL exists.
    """
    audit.setdefault("price_url_scrubs", [])
    for cig in cigars:
        url = cig.get("priceUrl")
        line_s = serie_token(cig.get("line"))
        url_s = serie_token(slug_tail(url or "").replace("-", " "))
        mismatch = bool(url and line_s and url_s and line_s != url_s)
        samplerish = bool(url and re.search(r"\b(sampler|gift)\b", url, re.I))
        if not mismatch and not samplerish:
            continue
        replacement = pick_product_url(cig)
        if not mismatch and samplerish:
            if not replacement or replacement == url:
                continue
            if re.search(r"\b(sampler|gift)\b", replacement, re.I):
                continue
        if mismatch:
            cig["priceUrl"] = replacement
            audit["price_url_scrubs"].append(
                {
                    "id": cig["id"],
                    "line": cig.get("line"),
                    "was": url,
                    "now": replacement,
                    "reason": f"URL serie {url_s} ≠ line serie {line_s}",
                }
            )
        else:
            cig["priceUrl"] = replacement
            audit["price_url_scrubs"].append(
                {
                    "id": cig["id"],
                    "line": cig.get("line"),
                    "was": url,
                    "now": replacement,
                    "reason": "upgraded sampler/gift priceUrl to product SKU",
                }
            )


def shared_region_urls(cigars):
    url_owners = collections.defaultdict(set)
    for cig in cigars:
        for v in cig.get("vitolas") or []:
            for rl in (v.get("regionLinks") or {}).values():
                u = (rl or {}).get("url") if isinstance(rl, dict) else None
                if u:
                    url_owners[u].add(cig["id"])
    return [
        {"url": u, "cigars": sorted(ids)}
        for u, ids in sorted(url_owners.items())
        if len(ids) > 1
    ]


def apply_vitola_link_fixes(cigars, fixes, audit):
    """Stream I/D: apply curated per-vitola / per-cigar URL and format fixes."""
    if not fixes:
        return
    audit.setdefault("link_fixes", [])
    by_id = {c["id"]: c for c in cigars}
    for key, spec in fixes.items():
        if key.startswith("_") or not isinstance(spec, dict):
            continue
        if "::" in key:
            cid, vname = key.split("::", 1)
            cig = by_id.get(cid)
            if not cig:
                continue
            aliases = {vname}
            if spec.get("name"):
                aliases.add(spec["name"])
            for v in cig.get("vitolas") or []:
                if v.get("name") not in aliases:
                    continue
                changed = []
                if spec.get("name") and spec["name"] != v["name"]:
                    old = v["name"]
                    v["name"] = spec["name"]
                    if cig.get("vitola") == old:
                        cig["vitola"] = spec["name"]
                    changed.append("name")
                if spec.get("format") and spec["format"] != v.get("format"):
                    v["format"] = spec["format"]
                    changed.append("format")
                if spec.get("clearPriceEUR") and v.get("priceEUR") is not None:
                    v["priceEUR"] = None
                    changed.append("clearPriceEUR")
                if "url" in spec and spec.get("url") != v.get("url"):
                    v["url"] = spec["url"]
                    changed.append("url")
                if spec.get("regionLinks"):
                    links = dict(v.get("regionLinks") or {})
                    for region, rl in spec["regionLinks"].items():
                        if links.get(region) != rl:
                            links[region] = rl
                            changed.append(f"regionLinks.{region}")
                    v["regionLinks"] = {
                        r: links[r] for r in ("HR", "EU", "USA") if r in links
                    }
                if changed:
                    audit["link_fixes"].append(
                        {"id": cid, "vitola": vname, "fields": changed, "status": "applied"}
                    )
                else:
                    audit["link_fixes"].append(
                        {"id": cid, "vitola": vname, "fields": [], "status": "already_applied"}
                    )
                break
        else:
            cig = by_id.get(key)
            if not cig:
                continue
            if spec.get("regionLinks"):
                links = dict(cig.get("regionLinks") or {})
                changed = []
                for region, rl in spec["regionLinks"].items():
                    if links.get(region) != rl:
                        links[region] = rl
                        changed.append(f"regionLinks.{region}")
                if changed:
                    cig["regionLinks"] = {
                        r: links[r] for r in ("HR", "EU", "USA") if r in links
                    }
                    audit["link_fixes"].append(
                        {"id": key, "vitola": None, "fields": changed, "status": "applied"}
                    )
                else:
                    audit["link_fixes"].append(
                        {"id": key, "vitola": None, "fields": [], "status": "already_applied"}
                    )


def main():
    check = "--check" in sys.argv
    cigars = load(CIGARS)
    before = json.dumps(cigars, ensure_ascii=False, indent=2) + "\n"
    lexicon = load(LEXICON, {}) or {}
    if isinstance(lexicon, dict) and "slugs" in lexicon:
        lexicon = lexicon["slugs"]
    decisions = load(DECISIONS, {}) or {}
    dimfix = load(DIMFIX, {}) or {}
    line_decisions = load(LINE_MERGES, {}) or {}
    link_fixes = load(LINK_FIXES, {}) or {}

    audit = normalize(cigars, lexicon, decisions, dimfix)
    cigars = apply_line_decisions(cigars, line_decisions, audit)
    demote_holts_listings(cigars, audit)
    scrub_mismatched_price_urls(cigars, audit)
    apply_vitola_link_fixes(cigars, link_fixes, audit)
    # rebuild after demotion — listing URLs no longer sit on vitolas
    audit["shared_region_urls"] = shared_region_urls(cigars)
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
        "line_merges": len(audit.get("line_merges") or []),
        "vitola_relocations": len(audit.get("vitola_relocations") or []),
        "keep_distinct": len(audit.get("keep_distinct") or []),
        "listing_demotions": len(audit.get("listing_demotions") or []),
        "price_url_scrubs": len(audit.get("price_url_scrubs") or []),
        "link_fixes": len(audit.get("link_fixes") or []),
        "changed": before != after,
    }
    print(json.dumps(stats, ensure_ascii=False, indent=2))

    if check:
        sys.exit(1 if before != after else 0)
    write_cigars(cigars)


if __name__ == "__main__":
    main()
