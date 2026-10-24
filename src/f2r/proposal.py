"""Turn evidence into a roadmap change proposal. Proposes; never applies.

Two fields can change, each by a written rule from the product owner's scoring file:
- reach: set to the evidence estimate (distinct users who reported a linked theme, divided by the
  share of target users who gave any feedback) when the theme is strong or moderate and the current
  value differs from it by more than the threshold;
- confidence: set to the evidence tier's value (strong, moderate, weak; or "no evidence").
Impact and effort are the team's judgement and are never touched. Every change carries its rule,
its numbers and the themes behind it, so the product owner can check it in seconds.
"""
from __future__ import annotations

from .data import RoadmapItem
from .evidence import ThemeEvidence, tier_for


def rank(items: list[RoadmapItem], capacity: float) -> list[dict]:
    """Pinned items take capacity first; then RICE, highest first. Items that do not fit are
    skipped and the next one that fits is taken (the cut line is about capacity, not position)."""
    order = sorted(items, key=lambda x: (not x.pinned, -x.rice if not x.pinned else 0, x.id))
    used, rows = 0.0, []
    for i, it in enumerate(order, 1):
        fits = used + it.effort <= capacity
        if fits:
            used += it.effort
        rows.append({"rank": i, "id": it.id, "title": it.title, "rice": it.rice, "reach": it.reach,
                     "impact": it.impact, "confidence": it.confidence, "effort": it.effort,
                     "pinned": it.pinned, "above_cut": fits, "capacity_used": used if fits else None})
    return rows


def combined(item: RoadmapItem, ev: dict[str, ThemeEvidence], scoring: dict, voice_rate: float) -> dict:
    """The evidence behind one roadmap item: the union of its themes' reporters."""
    users, channels, segments = set(), set(), set()
    for t in item.themes:
        users |= ev[t].users
        channels |= set(ev[t].channels)
        segments |= set(ev[t].segments)
    tier, conf = tier_for(len(users), len(channels), len(segments), scoring["tiers"]) if users else ("none", 0.0)
    if tier == "none":
        conf = scoring["no_evidence_confidence"]
    reach = round(len(users) / voice_rate) if users and voice_rate and tier in scoring["reach_from_tiers"] else None
    return {"themes": item.themes, "users": len(users), "channels": sorted(channels), "segments": sorted(segments),
            "tier": tier, "tier_confidence": conf, "reach_estimate": reach}


def _next_tier(tier: str, scoring: dict) -> str:
    names = [t["name"] for t in scoring["tiers"]]
    if tier not in names or names.index(tier) == 0:
        return ""
    up = scoring["tiers"][names.index(tier) - 1]
    return (f" ('{up['name']}' needs {up['min_users']}+ people, {up['min_channels']}+ channels, "
            f"{up['min_segments']}+ segments)")


def build(roadmap: list[RoadmapItem], ev: dict[str, ThemeEvidence], scoring: dict, voice: dict,
          total_users: int) -> dict:
    vr = voice["voice_rate"]
    changes, opinion_only = [], []
    for it in roadmap:
        if it.status == "done":
            continue
        e = combined(it, ev, scoring, vr)
        if e["tier"] == "none":
            opinion_only.append({"item": it.id, "title": it.title, "proposed_by": it.proposed_by,
                                 "why": "no linked theme" if not it.themes else "no feedback in the window for its themes"})
        th = "+".join(it.themes) or "no theme"
        if e["reach_estimate"] is not None and it.reach and abs(e["reach_estimate"] - it.reach) / it.reach > scoring["reach_change_threshold"]:
            changes.append({"item": it.id, "field": "reach", "from": it.reach, "to": float(e["reach_estimate"]), "evidence": e,
                            "rule": (f"{e['users']} distinct users reported {th}; {voice['voices']} of {total_users} target users "
                                     f"gave any feedback (voice rate {vr}); {e['users']} / {vr} = {e['reach_estimate']}. "
                                     f"The current {it.reach:g} differs by more than {int(scoring['reach_change_threshold'] * 100)}%.")})
        if abs(e["tier_confidence"] - it.confidence) > 1e-9:
            if e["tier"] == "none":
                rule = (f"No feedback in the window supports this item ({e['users']} users): confidence set to "
                        f"{scoring['no_evidence_confidence']} (no evidence). The reason to build it has to come from "
                        f"somewhere other than users, and should be written down.")
            else:
                rule = (f"{th}: {e['users']} distinct users, {len(e['channels'])} channel(s), {len(e['segments'])} "
                        f"segment(s), so tier '{e['tier']}' -> confidence {e['tier_confidence']}{_next_tier(e['tier'], scoring)}.")
            changes.append({"item": it.id, "field": "confidence", "from": it.confidence, "to": e["tier_confidence"],
                            "evidence": e, "rule": rule})
    for i, c in enumerate(changes, 1):
        c.update({"id": f"CH-{i:02d}", "status": "pending", "decided_by": None, "decided_on": None, "note": ""})
        c = {k: c[k] for k in ("id", "item", "field", "from", "to", "rule", "evidence", "status", "decided_by", "decided_on", "note")}
        changes[i - 1] = c

    cap = scoring["capacity_points"]
    expensive = scoring["expensive_effort_share"] * cap
    gaps = []
    for t in ev.values():
        if t.kind != "problem" or t.tier not in ("strong", "moderate") or t.spike_week:
            continue
        linked = [it for it in roadmap if t.id in it.themes and it.status != "done"]
        if not linked:
            gaps.append({"theme": t.id, "name": t.name, "users": len(t.users), "tier": t.tier, "kind": "no roadmap item"})
        elif all(it.effort > expensive for it in linked):
            gaps.append({"theme": t.id, "name": t.name, "users": len(t.users), "tier": t.tier,
                         "kind": f"only expensive items ({', '.join(f'{it.id} effort {it.effort:g}' for it in linked)}; "
                                 f"more than {expensive:g} of {cap:g} points)"})

    after = [RoadmapItem(**{**it.__dict__}) for it in roadmap]
    for c in changes:
        x = next(a for a in after if a.id == c["item"])
        setattr(x, c["field"], c["to"])
    open_items = [x for x in roadmap if x.status != "done"]
    return {
        "changes": changes,
        "opinion_only": opinion_only,
        "gaps": gaps,
        "ranking_before": rank(open_items, cap),
        "ranking_if_all_accepted": rank([x for x in after if x.status != "done"], cap),
    }
