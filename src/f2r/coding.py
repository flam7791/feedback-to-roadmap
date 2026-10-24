"""Code each item with zero or more themes, from the product owner's codebook.

Rules first, on purpose: every tag can be traced to the keyword that set it, and the product
owner can predict the result. A manual code (the product owner's call on one item) overrides the
codebook for that item, in both directions. Items no rule matches go to the uncoded queue; words
that recur there are offered as candidates for a new theme, never added by the tool.
"""
from __future__ import annotations

import re
from collections import Counter

from .data import Item, Theme

STOP = set("""a an and are as at be but by can do does for from had has have i if in is it its it's
just me my no not of on or our please so that the their them there this to too use used using
very was we were what when where which who will with would you your should could than then
answer answers assistant policy it'd i'm i've don't doesn't can't won't isn't more less need needs
interview note she he they said""".split())
WORD = re.compile(r"[a-z][a-z'-]+")


def _rx(phrase: str) -> re.Pattern:
    return re.compile(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])")


def _norm(text: str) -> str:
    return text.lower().replace("’", "'")


class Codebook:
    def __init__(self, themes: list[Theme]):
        self.themes = themes
        self._rules = [(t.id, k, _rx(k)) for t in themes for k in t.keywords]

    def match(self, text: str) -> dict[str, list[str]]:
        """theme id -> the keywords that matched (empty dict when nothing matches)."""
        low = _norm(text)
        hits: dict[str, list[str]] = {}
        for tid, kw, rx in self._rules:
            if rx.search(low):
                hits.setdefault(tid, []).append(kw)
        return hits


def code_items(items: list[Item], codebook: Codebook, manual: dict[str, tuple[list[str], str]]) -> None:
    order = {t.id: i for i, t in enumerate(codebook.themes)}
    for it in items:
        if it.id in manual:
            it.themes, it.coded_by = sorted(manual[it.id][0], key=order.get), manual[it.id][1]
        else:
            it.themes = sorted(codebook.match(it.text), key=order.get)
            it.coded_by = "codebook"


def new_theme_candidates(uncoded: list[Item], min_items: int) -> list[dict]:
    """Words that recur across uncoded items: a hint for the product owner, never a theme."""
    seen: Counter = Counter()
    where: dict[str, list[str]] = {}
    for it in uncoded:
        for w in sorted(set(WORD.findall(_norm(it.text))) - STOP):
            if len(w) < 4:
                continue
            seen[w] += 1
            where.setdefault(w, []).append(it.id)
    return [{"word": w, "items": n, "item_ids": where[w]}
            for w, n in sorted(seen.items(), key=lambda x: (-x[1], x[0])) if n >= min_items]


def severity(text: str, markers: list[str]) -> bool:
    low = _norm(text)
    return any(_rx(m).search(low) for m in markers)
