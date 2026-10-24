"""The human checkpoint. Only a product owner on the team roster decides; the tool never does.

decide: accept, reject (a note is required) or pin an item above the cut line (a note is required).
        A decided change is final; to reconsider, run a new review.
apply:  only when every change is decided, and only if the source roadmap has not changed since the
        review. Writes roadmap.next.csv, the decision record and the people to tell. Never writes the
        source roadmap.
"""
from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

from .data import InputError, load_roadmap
from .proposal import rank
from .review import sha256


class DecisionError(PermissionError):
    """A decision the workflow refuses: wrong person, missing note, wrong state."""


def load_team(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _check_person(by: str, team: dict) -> str:
    if not by or by == team.get("tool_id", "f2r"):
        raise DecisionError("the tool cannot decide on its own proposal; a product owner must")
    roles = [r for r, ids in team["roles"].items() if by in ids]
    allowed = [r for r in roles if r in team["decide_roles"]]
    if not allowed:
        raise DecisionError(f"'{by}' is not on the roster as {' or '.join(team['decide_roles'])} "
                            f"(roles found: {', '.join(roles) or 'none'})")
    return allowed[0]


def decide(pack: dict, team: dict, by: str, accept: list[str] = (), reject: dict[str, str] | None = None,
           pin: dict[str, str] | None = None, accept_rest: bool = False, on: date | None = None) -> dict:
    role = _check_person(by, team)
    prop = pack["proposal"]
    if prop["status"] != "open":
        raise DecisionError("this proposal has been applied; run a new review to change the roadmap again")
    reject, pin = reject or {}, pin or {}
    if not (accept or reject or pin or accept_rest):
        raise DecisionError("nothing to decide: give --accept, --reject, --pin or --accept-rest")
    by_id = {c["id"]: c for c in prop["changes"]}
    for cid in list(accept) + list(reject):
        if cid not in by_id:
            raise DecisionError(f"no change {cid} in this proposal")
        if by_id[cid]["status"] != "pending":
            raise DecisionError(f"{cid} is already {by_id[cid]['status']}; decisions are final, run a new review to reconsider")
    both = set(accept) & set(reject)
    if both:
        raise DecisionError(f"{', '.join(sorted(both))} both accepted and rejected")
    for cid, note in reject.items():
        if not note.strip():
            raise DecisionError(f"rejecting {cid} needs a note: the reason is the useful part")
    item_ids = {r["id"] for r in prop["ranking_before"]}
    for iid, note in pin.items():
        if iid not in item_ids:
            raise DecisionError(f"no roadmap item {iid}")
        if not note.strip():
            raise DecisionError(f"pinning {iid} needs a note: a pin overrides the evidence and must say why")
        if any(p["item"] == iid for p in prop["pins"]):
            raise DecisionError(f"{iid} is already pinned")

    day = (on or date.today()).isoformat()
    for cid in accept:
        by_id[cid].update(status="accepted", decided_by=by, decided_on=day)
    for cid, note in reject.items():
        by_id[cid].update(status="rejected", decided_by=by, decided_on=day, note=note.strip())
    if accept_rest:
        for c in prop["changes"]:
            if c["status"] == "pending":
                c.update(status="accepted", decided_by=by, decided_on=day)
    for iid, note in pin.items():
        prop["pins"].append({"item": iid, "note": note.strip(), "by": by, "on": day})
    pack["decision_history"].append({"by": by, "role": role, "on": day, "accepted": sorted(accept),
                                     "rejected": sorted(reject), "pinned": sorted(pin), "accept_rest": accept_rest})
    return pack


def apply(pack: dict, team: dict, by: str, out_dir: str | Path, on: date | None = None) -> dict:
    _check_person(by, team)
    prop = pack["proposal"]
    if prop["status"] != "open":
        raise DecisionError("already applied")
    pending = [c["id"] for c in prop["changes"] if c["status"] == "pending"]
    if pending:
        raise DecisionError(f"{len(pending)} change(s) still pending ({', '.join(pending)}); decide every change before applying")
    src = pack["inputs"]["roadmap"]
    if sha256(src) != pack["inputs"]["roadmap_sha256"]:
        raise DecisionError(f"{src} changed since the review; run the review again so the proposal matches the roadmap")

    theme_ids = {t["id"] for t in pack["themes"]}
    items = load_roadmap(src, theme_ids)
    by_id = {x.id: x for x in items}
    applied = []
    for c in prop["changes"]:
        if c["status"] == "accepted":
            setattr(by_id[c["item"]], c["field"], c["to"])
            applied.append(c["id"])
    for p in prop["pins"]:
        by_id[p["item"]].pinned, by_id[p["item"]].pin_note = True, p["note"]
    open_items = [x for x in items if x.status != "done"]
    ranking = rank(open_items, pack["capacity_points"])

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    next_path = out / "roadmap.next.csv"
    if next_path.resolve() == Path(src).resolve():
        raise DecisionError("refusing to overwrite the source roadmap")
    changed = {c["item"] for c in prop["changes"] if c["status"] == "accepted"}
    with open(next_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["id", "title", "themes", "reach", "impact", "confidence", "effort", "proposed_by", "status",
                    "pinned", "pin_note", "rice", "rank", "above_cut", "changed_in_review"])
        rk = {r["id"]: r for r in ranking}
        for x in sorted(items, key=lambda x: rk.get(x.id, {"rank": 999})["rank"]):
            r = rk.get(x.id)
            w.writerow([x.id, x.title, ";".join(x.themes), f"{x.reach:g}", f"{x.impact:g}", f"{x.confidence:g}",
                        f"{x.effort:g}", x.proposed_by, x.status, "yes" if x.pinned else "", x.pin_note,
                        f"{x.rice:g}", r["rank"] if r else "", ("yes" if r["above_cut"] else "no") if r else "",
                        "yes" if x.id in changed else ""])

    # the people who told us about something now above the cut line
    users_by_theme = {t["id"]: t["user_ids"] for t in pack["themes"] if t["kind"] == "problem"}
    notify = []
    for r in ranking:
        if not r["above_cut"]:
            continue
        for t in by_id[r["id"]].themes:
            for u in users_by_theme.get(t, []):
                notify.append({"user_id": u, "theme": t, "item": r["id"], "item_title": r["title"]})
    with open(out / "notify.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["user_id", "theme", "item", "item_title"], lineterminator="\n")
        w.writeheader()
        w.writerows(notify)

    prop.update(status="applied", applied_by=by, applied_on=(on or date.today()).isoformat(),
                ranking_after=ranking, applied_changes=applied, notify_users=len({n["user_id"] for n in notify}))
    return {"roadmap_next": str(next_path), "notify": str(out / "notify.csv"), "ranking": ranking,
            "applied": applied, "notify_rows": len(notify), "item_themes": {x.id: x.themes for x in items}}


def save(pack: dict, path: str | Path) -> None:
    Path(path).write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8")


def load(path: str | Path) -> dict:
    p = Path(path)
    if not p.exists():
        raise InputError(f"{p}: file not found")
    return json.loads(p.read_text(encoding="utf-8"))
