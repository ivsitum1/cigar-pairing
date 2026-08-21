# -*- coding: utf-8 -*-
"""Shared fetch/parse/match helpers for the RumRatings cross-check.

Split out of the CLI scripts so the parsers can be unit-tested from saved
HTML with no network (`test_rumratings.py`). Stdlib only, like the other
scrape helpers in this folder.

Two rules the callers rely on:
- Every fetch goes through the on-disk cache, so a re-parse after tweaking a
  selector costs no requests (`--parse-only`).
- Extraction never guesses: each record records which strategy produced it
  (`parseStrategy`), and a page nothing matched is reported, not dropped
  silently.
"""
from __future__ import annotations

import hashlib
import html as html_mod
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from dataclasses import dataclass, field
from pathlib import Path

BASE = "https://rumratings.com"
SITEMAP_URL = "http://s3.amazonaws.com/images.rumratings.com/sitemaps/sitemap.xml.gz"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "output"
CACHE_DIR = OUT_DIR / "rumratings_cache"

# Live site uses /rum/<id>-<slug>; older bookmarks and fixtures used /brands/.
DETAIL_RE = re.compile(r"^/(?:brands|rum)/(\d+)(?:-([a-z0-9-]+))?/?$", re.I)
HERO_RATING_RE = re.compile(
    r"(?is)<big\b[^>]*>\s*(\d{1,2}(?:[.,]\d)?)\s*</big>\s*<span\b[^>]*>\s*/\s*10"
)
HERO_VOTES_RE = re.compile(
    r"(?is)<span\b[^>]*>\s*([\d,.]+)\s*ratings?\s*</span>"
)
COMPANY_RE = re.compile(
    r'(?is)<a\b[^>]+href=["\'][^"\']*/companies/\d+-[^"\']+["\'][^>]*>(.*?)</a>'
)


# ---------------------------------------------------------------- fetching


def parse_robots(text: str) -> urllib.robotparser.RobotFileParser:
    """Parse a robots.txt body. Callers fetch the file with our User-Agent.

    `RobotFileParser.read()` uses Python's default urllib UA. rumratings.com
    answers that with 403, which the stdlib treats as 'disallow everything'.
    """
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(text.splitlines())
    return rp


def cache_url_from_path(filename: str) -> str:
    """Invert Fetcher.cache_path naming: rum-12-x.hash.html -> /rum/12-x."""
    slug = Path(filename).name.rsplit(".", 2)[0]
    kind, _, rest = slug.partition("-")
    if kind in ("rum", "brands") and rest:
        return f"{BASE}/{kind}/{rest}"
    return f"{BASE}/{slug.replace('-', '/', 1)}"


def name_from_detail_url(url: str) -> str:
    """Slug after the numeric id, spaces for matching against rums.json names."""
    leaf = urllib.parse.urlparse(url).path.rstrip("/").rsplit("/", 1)[-1]
    leaf = re.sub(r"^\d+-", "", leaf)
    return leaf.replace("-", " ")


def sitemap_rum_urls(xml_text: str) -> list[str]:
    """Bottle detail URLs from a sitemap document (companies/home dropped)."""
    urls: list[str] = []
    seen: set[str] = set()
    for loc in re.findall(r"<loc>\s*(.*?)\s*</loc>", xml_text):
        loc = html_mod.unescape(loc).strip().rstrip("/")
        path = urllib.parse.urlparse(loc).path
        if not DETAIL_RE.match(path):
            continue
        if loc not in seen:
            seen.add(loc)
            urls.append(loc)
    return urls


@dataclass
class Fetcher:
    """Polite cached GET. Obeys robots.txt; never re-requests a cached URL."""

    delay: float = 1.5
    timeout: int = 45
    cache_dir: Path = CACHE_DIR
    offline: bool = False
    _robots: urllib.robotparser.RobotFileParser | None = field(default=None, init=False)
    _crawl_delay: float = field(default=0.0, init=False)
    _last: float = field(default=0.0, init=False)
    stats: dict[str, int] = field(default_factory=lambda: {"cache": 0, "net": 0, "error": 0})

    def cache_path(self, url: str) -> Path:
        digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
        slug = re.sub(r"[^a-z0-9]+", "-", urllib.parse.urlparse(url).path.lower()).strip("-")
        return self.cache_dir / f"{slug[:60] or 'root'}.{digest}.html"

    def _load_robots(self) -> None:
        if self._robots is not None or self.offline:
            return
        robots_url = urllib.parse.urljoin(BASE, "/robots.txt")
        req = urllib.request.Request(
            robots_url, headers={"User-Agent": USER_AGENT, "Accept-Language": "en;q=0.9"}
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                text = resp.read().decode(resp.headers.get_content_charset() or "utf-8", "replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
            rp = urllib.robotparser.RobotFileParser()
            rp.disallow_all = True
            self._robots = rp
            self._crawl_delay = 0.0
            print("  robots.txt unreadable — refusing to crawl")
            return
        self._robots = parse_robots(text)
        delay = self._robots.crawl_delay(USER_AGENT)
        if delay is None:
            delay = self._robots.crawl_delay("*")
        self._crawl_delay = float(delay or 0)
        if self._crawl_delay:
            print(f"  robots.txt crawl-delay {self._crawl_delay:.0f}s")

    def allowed(self, url: str) -> bool:
        self._load_robots()
        if self._robots is None:
            return True
        return self._robots.can_fetch(USER_AGENT, url)

    def get(self, url: str) -> str | None:
        path = self.cache_path(url)
        if path.exists():
            self.stats["cache"] += 1
            return path.read_text("utf-8", "replace")
        if self.offline:
            return None
        if not self.allowed(url):
            self.stats["error"] += 1
            print(f"  robots.txt disallows {url} — skipped")
            return None
        wait = max(self.delay, self._crawl_delay) - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(
            url, headers={"User-Agent": USER_AGENT, "Accept-Language": "en;q=0.9"}
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
                charset = resp.headers.get_content_charset() or "utf-8"
                text = raw.decode(charset, "replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
            self.stats["error"] += 1
            print(f"  fetch failed {url}: {exc}")
            return None
        finally:
            self._last = time.time()
        self.stats["net"] += 1
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, "utf-8")
        return text


# ----------------------------------------------------------------- parsing


def strip_tags(fragment: str) -> str:
    fragment = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", fragment)
    fragment = re.sub(r"(?i)<br\s*/?>", "\n", fragment)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    text = html_mod.unescape(fragment)
    text = text.replace("\xa0", " ")
    return re.sub(r"[ \t]+", " ", text).strip()


def json_ld_blocks(page: str) -> list[dict]:
    blocks: list[dict] = []
    for m in re.finditer(
        r'(?is)<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', page
    ):
        try:
            data = json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
            elif isinstance(node, dict):
                blocks.append(node)
                stack.extend(v for v in node.values() if isinstance(v, (dict, list)))
    return blocks


def _num(value) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).replace(",", ".").strip())
    except ValueError:
        return None


def detail_links(page: str) -> list[str]:
    """Absolute URLs of rum detail pages linked from a listing page."""
    seen: dict[str, None] = {}
    for m in re.finditer(r'href=["\']([^"\']+)["\']', page):
        href = html_mod.unescape(m.group(1))
        path = urllib.parse.urlparse(urllib.parse.urljoin(BASE, href))
        if path.netloc and path.netloc.replace("www.", "") != "rumratings.com":
            continue
        if DETAIL_RE.match(path.path):
            seen.setdefault(f"{BASE}{path.path.rstrip('/')}", None)
    return list(seen)


def next_page_url(page: str, current: str) -> str | None:
    """rel=next when present, else the highest ?page= link above the current one."""
    m = re.search(r'(?is)<link[^>]+rel=["\']next["\'][^>]+href=["\']([^"\']+)["\']', page)
    if not m:
        m = re.search(r'(?is)<a[^>]+rel=["\']next["\'][^>]+href=["\']([^"\']+)["\']', page)
    if m:
        return urllib.parse.urljoin(current, html_mod.unescape(m.group(1)))
    cur_no = int((urllib.parse.parse_qs(urllib.parse.urlparse(current).query).get("page") or ["1"])[0])
    best: tuple[int, str] | None = None
    for hit in re.finditer(r'href=["\']([^"\']*[?&]page=(\d+)[^"\']*)["\']', page):
        no = int(hit.group(2))
        if no <= cur_no:
            continue
        if best is None or no < best[0]:
            best = (no, urllib.parse.urljoin(current, html_mod.unescape(hit.group(1))))
    return best[1] if best else None


def parse_detail(page: str, url: str) -> dict | None:
    """One rum: name, brand, community average (1-10), vote count, reviews.

    Strategies in order — schema.org JSON-LD, microdata, then the visible
    text. The first that yields a name *and* a rating wins.
    """
    name = brand = None
    rating = votes = None
    strategy = None

    for node in json_ld_blocks(page):
        agg = node.get("aggregateRating")
        if not isinstance(agg, dict):
            continue
        rating = _num(agg.get("ratingValue"))
        votes = _num(agg.get("ratingCount") or agg.get("reviewCount"))
        name = (node.get("name") or "").strip() or None
        maker = node.get("brand") or node.get("manufacturer")
        if isinstance(maker, dict):
            brand = (maker.get("name") or "").strip() or None
        elif isinstance(maker, str):
            brand = maker.strip() or None
        if name and rating is not None:
            strategy = "json-ld"
            break
        rating = votes = None

    if strategy is None:
        hero = HERO_RATING_RE.search(page)
        if hero:
            rating = _num(hero.group(1))
            votes_hit = HERO_VOTES_RE.search(page)
            votes = _num(votes_hit.group(1).replace(",", "")) if votes_hit else None
            strategy = "hero"

    if strategy is None:
        micro_rating = re.search(r'itemprop=["\']ratingValue["\'][^>]*content=["\']([\d.,]+)', page)
        micro_votes = re.search(r'itemprop=["\'](?:ratingCount|reviewCount)["\'][^>]*content=["\'](\d+)', page)
        if micro_rating:
            rating = _num(micro_rating.group(1))
            votes = _num(micro_votes.group(1)) if micro_votes else None
            strategy = "microdata"

    if not name:
        h1 = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", page)
        if h1:
            name = strip_tags(h1.group(1)) or None
        if not name:
            title = re.search(r"(?is)<title[^>]*>(.*?)</title>", page)
            if title:
                name = re.split(r"\s*[|–-]\s*Rum ?Ratings", strip_tags(title.group(1)))[0].strip() or None

    if not brand:
        company = COMPANY_RE.search(page)
        if company:
            brand = strip_tags(company.group(1)) or None

    text = strip_tags(page)
    if rating is None:
        # "8.2 / 10", "Average rating 8.2", "8.2 out of 10"
        hit = re.search(
            r"(?i)(?:average(?:\s+rating)?[:\s]+)?\b(\d{1,2}(?:[.,]\d)?)\s*(?:/|out of)\s*10\b", text
        )
        if hit:
            rating = _num(hit.group(1))
            strategy = strategy or "text"
    if votes is None:
        hit = re.search(r"(?i)\b([\d,.]+)\s*(?:ratings?|votes?|reviews?)\b", text)
        if hit:
            votes = _num(hit.group(1).replace(",", "").replace(".", ""))

    if not name or rating is None:
        return None

    m = DETAIL_RE.match(urllib.parse.urlparse(url).path)
    return {
        "sourceId": m.group(1) if m else None,
        "slug": m.group(2) if m else None,
        "url": url,
        "name": name,
        "brand": brand,
        "rating": round(rating, 2),
        "votes": int(votes) if votes is not None else None,
        "reviews": parse_reviews(page),
        "parseStrategy": strategy or "heuristic",
    }


REVIEW_BLOCK_RE = re.compile(
    r'(?is)<(?:div|li|article)[^>]*class=["\'][^"\']*(?:review|comment)[^"\']*["\'][^>]*>(.*?)</(?:div|li|article)>'
)
REVIEW_TEXT_RE = re.compile(
    r'(?is)<p[^>]*class=["\'][^"\']*review-text[^"\']*["\'][^>]*>(.*?)</p>'
)


def parse_reviews(page: str, limit: int = 40) -> list[dict]:
    """User review texts, for the story/etiquette worklists.

    Kept verbatim only as *source quotes* — the report marks them for
    editorial rewrite, never for pasting into club.json as-is.
    """
    out: list[dict] = []
    seen: set[str] = set()

    def add(body: str) -> bool:
        body = re.sub(r"\s+", " ", body).strip()
        if len(body) < 40:
            return False
        key = body[:120].lower()
        if key in seen:
            return False
        seen.add(key)
        score = re.match(r"^(\d{1,2}(?:[.,]\d)?)\s", body)
        out.append({"text": body[:1200], "score": _num(score.group(1)) if score else None})
        return True

    for block in REVIEW_TEXT_RE.finditer(page):
        if add(strip_tags(block.group(1))) and len(out) >= limit:
            return out
    for block in REVIEW_BLOCK_RE.finditer(page):
        if add(strip_tags(block.group(1))) and len(out) >= limit:
            return out
    return out


# ---------------------------------------------------------------- matching

STOP = {
    "rum", "rhum", "ron", "the", "of", "and", "a", "de", "la", "le", "el",
    "year", "years", "yo", "yr", "aged", "old", "edition", "limited", "cl",
    "ml", "l", "vol", "abv", "bottle", "bottling", "agricole", "vieux",
}
# Words the catalogue drops but shops/community add (and vice versa).
SOFT = {
    "reserva", "reserve", "gran", "grand", "extra", "special", "selection",
    "select", "seleccion", "solera", "estate", "distillery", "original",
    "classic", "black", "white", "gold", "dark", "spiced", "blend", "blended",
    "single", "cask", "barrel", "casks", "finish", "anniversary", "anos",
    "años", "premium", "superior",
}
VOLUME_NUMS = {"70", "75", "50", "05", "07", "100", "1000"}


def fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower()


def tokens(name: str) -> tuple[frozenset[str], frozenset[str]]:
    """(word tokens, age/number tokens) — numbers must agree to call it a match."""
    words: set[str] = set()
    nums: set[str] = set()
    for raw in re.split(r"[^a-z0-9]+", fold(name)):
        if not raw:
            continue
        if raw.isdigit():
            if raw not in VOLUME_NUMS:
                nums.add(raw.lstrip("0") or raw)
            continue
        if raw in STOP or len(raw) == 1:
            continue
        words.add(raw)
    return frozenset(words), frozenset(nums)


def match_score(left: str, right: str) -> float:
    """0..1 similarity. A number clash (12 vs 15 YO) hard-fails to 0."""
    lw, ln = tokens(left)
    rw, rn = tokens(right)
    return score_from_tokens(lw, ln, rw, rn)


def score_from_tokens(
    lw: frozenset[str], ln: frozenset[str], rw: frozenset[str], rn: frozenset[str]
) -> float:
    if not lw or not rw:
        return 0.0
    if ln and rn and not (ln & rn):
        return 0.0
    if bool(ln) != bool(rn) and (ln | rn):
        penalty = 0.15
    else:
        penalty = 0.0
    shared = lw & rw
    strong_shared = {t for t in shared if t not in SOFT}
    if not strong_shared:
        return 0.0
    weight = lambda ts: sum(0.5 if t in SOFT else 1.0 for t in ts)  # noqa: E731
    denom = weight(lw | rw)
    if denom <= 0:
        return 0.0
    return max(0.0, weight(shared) / denom - penalty)


def catalog_target_urls(
    detail_urls: list[str], catalog: list[dict], floor: float = 0.7
) -> list[str]:
    """One RumRatings URL per catalogue bottle, greedy by match score.

    Sitemap is ~13k URLs; an inverted index on strong tokens keeps this
    linear in catalogue size instead of a 13k × 320 scan.
    """
    named: list[tuple[str, frozenset[str], frozenset[str]]] = []
    index: dict[str, list[int]] = {}
    for i, url in enumerate(detail_urls):
        words, nums = tokens(name_from_detail_url(url))
        named.append((url, words, nums))
        for tok in words:
            if tok not in SOFT:
                index.setdefault(tok, []).append(i)

    claimed: set[str] = set()
    chosen: list[str] = []
    for bottle in catalog:
        ours = bottle.get("name") or ""
        ow, on = tokens(ours)
        candidates: set[int] = set()
        for tok in ow:
            if tok not in SOFT:
                candidates.update(index.get(tok, ()))
        best_url, best_s = None, 0.0
        for i in candidates:
            url, rw, rn = named[i]
            if url in claimed:
                continue
            score = score_from_tokens(ow, on, rw, rn)
            if score > best_s:
                best_url, best_s = url, score
        if best_url and best_s >= floor:
            claimed.add(best_url)
            chosen.append(best_url)
    return chosen


def best_match(name: str, candidates: list[dict], key: str = "name", floor: float = 0.55):
    """Highest-scoring candidate above `floor`, or (None, 0.0)."""
    best = (None, 0.0)
    for cand in candidates:
        score = match_score(name, cand.get(key) or "")
        if score > best[1]:
            best = (cand, score)
    return best if best[1] >= floor else (None, best[1])


# ------------------------------------------------------------- statistics


def spearman(pairs: list[tuple[float, float]]) -> float | None:
    """Rank correlation without scipy. Ties get average ranks."""
    if len(pairs) < 3:
        return None

    def ranks(values: list[float]) -> list[float]:
        order = sorted(range(len(values)), key=lambda i: values[i])
        out = [0.0] * len(values)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                out[order[k]] = avg
            i = j + 1
        return out

    xs = ranks([p[0] for p in pairs])
    ys = ranks([p[1] for p in pairs])
    n = len(pairs)
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    return round(num / den, 3) if den else None


def percentile_rank(value: float, population: list[float]) -> float:
    """Share of the population at or below `value`, 0..1."""
    if not population:
        return 0.0
    below = sum(1 for v in population if v < value)
    equal = sum(1 for v in population if v == value)
    return round((below + equal / 2) / len(population), 4)
