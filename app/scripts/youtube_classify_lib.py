# -*- coding: utf-8 -*-
"""Heuristic tags for YouTube rum/bar videos (offline)."""
from __future__ import annotations

import re
from typing import Iterable

TAG_RUM = "rum"
TAG_COCKTAIL = "cocktail"
TAG_WHISKY = "whisky"
TAG_OTHER_SPIRIT = "other-spirit"
TAG_BAR_TECHNIQUE = "bar-technique"
TAG_SKIP = "skip"

ALL_TAGS = (
    TAG_RUM,
    TAG_COCKTAIL,
    TAG_WHISKY,
    TAG_OTHER_SPIRIT,
    TAG_BAR_TECHNIQUE,
    TAG_SKIP,
)

_RUM = re.compile(
    r"\b(rum|rums|rhum|ron|agricole|pot.?still|column.?still|"
    r"foursquare|appleton|havana.?club|doorly|mount.?gay|"
    r"diplomatico|zacapa|plantation|el.?dorado|clairin|"
    r"jamaican|barbados|martinique|guyanese)\b",
    re.I,
)
_COCKTAIL = re.compile(
    r"\b(cocktail|cocktails|daiquiri|mojito|mai.?tai|tiki|"
    r"old.?fashioned|negroni|martini|highball|punch|"
    r"how to make|recipe)\b",
    re.I,
)
_WHISKY = re.compile(
    r"\b(whisk(?:e)?y|scotch|bourbon|rye|peated|islay|speyside)\b",
    re.I,
)
_OTHER = re.compile(
    r"\b(gin|vodka|tequila|mezcal|brandy|cognac|armagnac|"
    r"liqueur|absinthe|pisco)\b",
    re.I,
)
_TECH = re.compile(
    r"\b(glassware|glencairn|garnish|shake|stir|strain|"
    r"ice|bar.?spoon|jigger|technique|beginner|"
    r"how to drink|tasting|nose|palate)\b",
    re.I,
)
_SKIP = re.compile(
    r"\b(vlog|travel.?vlog|unboxing.?haul|shorts.?meme|"
    r"subscribe|giveaway.?only)\b",
    re.I,
)


def _blob(title: str, text: str, text_chars: int = 800) -> str:
    body = (text or "")[:text_chars]
    return f"{title or ''}\n{body}"


def classify_video(title: str, text: str = "") -> list[str]:
    """Return zero or more tags. Empty → [skip] only when nothing else matches."""
    blob = _blob(title, text)
    tags: list[str] = []
    if _RUM.search(blob):
        tags.append(TAG_RUM)
    if _COCKTAIL.search(blob):
        tags.append(TAG_COCKTAIL)
    if _WHISKY.search(blob):
        tags.append(TAG_WHISKY)
    if _OTHER.search(blob):
        tags.append(TAG_OTHER_SPIRIT)
    if _TECH.search(blob):
        tags.append(TAG_BAR_TECHNIQUE)
    if not tags:
        if _SKIP.search(blob):
            tags.append(TAG_SKIP)
        else:
            tags.append(TAG_SKIP)
    return tags


def summarize_tags(tag_lists: Iterable[list[str]]) -> dict[str, int]:
    counts: dict[str, int] = {t: 0 for t in ALL_TAGS}
    for tags in tag_lists:
        for t in tags:
            counts[t] = counts.get(t, 0) + 1
    return counts
