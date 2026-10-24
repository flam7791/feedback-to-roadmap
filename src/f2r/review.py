"""One review cycle: screen -> code -> weigh -> propose. Produces the evidence pack and the proposal."""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

from . import __version__
from .coding import Codebook, code_items, new_theme_candidates
from .data import (InputError, Item, load_active_users, load_codebook, load_feedback, load_manual_codes,
                   load_roadmap, load_segments)
from .evidence import silent_segments, weigh
from .proposal import build
from .screen import flag, redact


def sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_review(feedback: str, roadmap: str, segments: str, codebook: str, scoring: str,
               codes: str | None = None, events: str | None = None, use_case: str | None = None,
               product: str = "the assistant", start: date | None = None, end: date | None = None,
               as_of: date | None = None) -> dict:
    seg = load_segments(segments)
    themes, markers, cb_version = load_codebook(codebook)
    sc = json.loads(Path(scoring).read_text(encoding="utf-8"))
    theme_ids = {t.id for t in themes}
    rows = load_feedback(feedback, seg)
    if not rows:
        raise InputError(f"{feedback}: no feedback rows")
    start = start or min(r["date"] for r in rows)
    end = end or max(r["date"] for r in rows)
    if end < start:
        raise InputError(f"window end {end} is before start {start}")
    rows = [r for r in rows if start <= r["date"] <= end]

    items = []
    for r in rows:
        text, red = redact(r["text"])       # raw text stops here
        items.append(Item(r["id"], r["date"], r["channel"], r["user_id"], r["segment"], text, red, flag(text)))
    manual = load_manual_codes(codes, theme_ids, {it.id for it in items})
    cb = Codebook(themes)
    code_items(items, cb, manual)

    active, usage = load_active_users(events, use_case, start, end)
    ev, voice = weigh(items, themes, markers, sc, sum(seg.values()), active)
    rm = load_roadmap(roadmap, theme_ids)
    prop = build(rm, ev, sc, voice, sum(seg.values()))
    uncoded = [it for it in items if not it.flags and not it.themes]

    return {
        "tool": f"feedback-to-roadmap {__version__}",
        "product": product,
        "use_case": use_case,
        "as_of": (as_of or date.today()).isoformat(),
        "window": {"start": start.isoformat(), "end": end.isoformat()},
        "inputs": {"feedback": str(feedback), "feedback_sha256": sha256(feedback),
                   "roadmap": str(roadmap), "roadmap_sha256": sha256(roadmap),
                   "codebook_version": cb_version, "scoring_version": sc.get("version", "?"),
                   "manual_codes": len(manual)},
        "summary": {"items": len(items), "evidence_items": voice["evidence_items"], "voices": voice["voices"],
                    "target_users": sum(seg.values()), "voice_rate": voice["voice_rate"],
                    "flagged": sum(1 for it in items if it.flags),
                    "redactions": sum(len(it.redactions) for it in items),
                    "uncoded": len(uncoded),
                    "channels": {c: sum(1 for it in items if it.channel == c) for c in sorted({it.channel for it in items})},
                    "active_users": len(active) if active is not None else None,
                    "usage": usage},
        "themes": [{
            "id": t.id, "name": t.name, "kind": t.kind, "items": t.items, "users": len(t.users),
            "channels": dict(t.channels), "segments": dict(t.segments), "weeks": dict(sorted(t.weeks.items())),
            "severe_share": t.severe_share, "not_active": t.not_active, "tier": t.tier,
            "reach_estimate": t.reach_estimate, "spike_week": t.spike_week, "quotes": t.quotes,
            "user_ids": sorted(t.users)} for t in ev.values()],
        "silent_segments": silent_segments(items, seg, sc["silent_segment_ratio"]),
        "spikes": [{"theme": t.id, "name": t.name, "week": t.spike_week, "items": t.items,
                    "in_week": t.weeks[t.spike_week]} for t in ev.values() if t.spike_week],
        "flagged": [{"item_id": it.id, "rules": it.flags, "text": it.text, "channel": it.channel} for it in items if it.flags],
        "uncoded": [{"item_id": it.id, "text": it.text, "channel": it.channel, "segment": it.segment} for it in uncoded],
        "new_theme_candidates": new_theme_candidates(uncoded, sc["new_theme_min_items"]),
        "manual_codes": [{"item_id": it.id, "themes": it.themes, "coded_by": it.coded_by}
                         for it in items if it.coded_by != "codebook"],
        "capacity_points": sc["capacity_points"],
        "proposal": {**prop, "pins": [], "status": "open"},
        "decision_history": [],
    }
