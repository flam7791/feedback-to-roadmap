"""Weigh the evidence: people, not rows.

For each theme: distinct users, channels, segments, how many reporters are not active users of the
assistant, the share of items with a severity marker, an evidence tier and an estimated reach.
Across themes: segments we are not hearing from, and spikes that look like incidents rather than
roadmap items. Every quote is an exact substring of the redacted text of the item it cites.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import timedelta

from .coding import severity
from .data import Item, Theme


@dataclass
class ThemeEvidence:
    id: str
    name: str
    kind: str
    items: int
    users: set[str]
    channels: Counter
    segments: Counter                # distinct users per segment
    weeks: Counter                   # items per ISO week (Monday)
    severe_share: float
    not_active: int | None           # reporters who are not active users (None without usage events)
    tier: str
    reach_estimate: int | None
    quotes: list[dict] = field(default_factory=list)
    spike_week: str | None = None


def tier_for(users: int, channels: int, segments: int, tiers: list[dict]) -> tuple[str, float]:
    for t in tiers:
        if users >= t["min_users"] and channels >= t["min_channels"] and segments >= t["min_segments"]:
            return t["name"], t["confidence"]
    return "none", 0.0


def week_of(d) -> str:
    return (d - timedelta(days=d.weekday())).isoformat()


def pick_quotes(items: list[Item], n: int) -> list[dict]:
    """Up to n quotes: items about this theme alone first, then the most recent, spread over channels,
    then segments, one per person. Deterministic, and always the item's whole (redacted) text."""
    pool = sorted(items, key=lambda x: (len(x.themes), -x.date.toordinal(), x.id))   # single-theme, recent first
    chosen: list[Item] = []
    seen_users: set[str] = set()
    for key in (lambda x: x.channel, lambda x: x.segment, lambda x: x.user_id):
        used = {key(c) for c in chosen}
        for it in pool:
            if len(chosen) >= n:
                break
            if it in chosen or it.user_id in seen_users or key(it) in used:
                continue
            chosen.append(it)
            seen_users.add(it.user_id)
            used.add(key(it))
    return [{"item_id": it.id, "text": it.text, "channel": it.channel, "segment": it.segment,
             "date": it.date.isoformat()} for it in chosen]


def weigh(items: list[Item], themes: list[Theme], markers: list[str], scoring: dict,
          total_users: int, active: set[str] | None) -> tuple[dict[str, ThemeEvidence], dict]:
    evidence_items = [it for it in items if not it.flags]
    voices = {it.user_id for it in evidence_items}
    voice_rate = len(voices) / total_users if total_users else 0.0
    by_theme: dict[str, list[Item]] = defaultdict(list)
    for it in evidence_items:
        for t in it.themes:
            by_theme[t].append(it)

    out: dict[str, ThemeEvidence] = {}
    for th in themes:
        its = by_theme.get(th.id, [])
        users = {it.user_id for it in its}
        seg_users: dict[str, set] = defaultdict(set)
        for it in its:
            seg_users[it.segment].add(it.user_id)
        channels = Counter(it.channel for it in its)
        tier, _ = tier_for(len(users), len(channels), len(seg_users), scoring["tiers"]) if users else ("none", 0)
        reach = (round(len(users) / voice_rate) if th.kind == "problem" and users and voice_rate
                 and tier in scoring["reach_from_tiers"] else None)
        ev = ThemeEvidence(
            id=th.id, name=th.name, kind=th.kind, items=len(its), users=users, channels=channels,
            segments=Counter({s: len(u) for s, u in seg_users.items()}),
            weeks=Counter(week_of(it.date) for it in its),
            severe_share=round(sum(severity(it.text, markers) for it in its) / len(its), 2) if its else 0.0,
            not_active=(len(users - active) if active is not None else None),
            tier=tier, reach_estimate=reach, quotes=pick_quotes(its, scoring["quotes_per_theme"]))
        sp = scoring["spike"]
        if ev.items >= sp["min_items"]:
            wk, n = max(ev.weeks.items(), key=lambda x: (x[1], x[0]))
            if n / ev.items >= sp["share_in_one_week"]:
                ev.spike_week = wk
        out[th.id] = ev

    return out, {"voice_rate": round(voice_rate, 3), "voices": len(voices), "evidence_items": len(evidence_items)}


def silent_segments(items: list[Item], segments: dict[str, int], ratio: float) -> list[dict]:
    """Segments whose share of the people giving feedback is well below their share of target users."""
    voices: dict[str, set] = defaultdict(set)
    for it in items:
        if not it.flags:
            voices[it.segment].add(it.user_id)
    total_v = sum(len(v) for v in voices.values())
    total_u = sum(segments.values())
    rows = []
    for seg, n in segments.items():
        share_u = n / total_u
        share_v = len(voices.get(seg, ())) / total_v if total_v else 0.0
        rows.append({"segment": seg, "target_users": n, "voices": len(voices.get(seg, ())),
                     "share_of_users": round(share_u, 3), "share_of_voices": round(share_v, 3),
                     "ratio": round(share_v / share_u, 2), "silent": share_v / share_u < ratio})
    return rows
