"""Load and validate the inputs. Malformed input stops with the file, row and field; nothing is guessed."""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

CHANNELS = ("in_app", "survey", "ticket", "interview")
USER_RE = re.compile(r"^[A-Za-z0-9_-]{3,40}$")


class InputError(ValueError):
    """Raised for any input the tool refuses to interpret."""


@dataclass
class Item:
    id: str
    date: date
    channel: str
    user_id: str
    segment: str
    text: str                       # redacted text: the only text any output may contain
    redactions: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)   # screening flags; a flagged item is not evidence
    themes: list[str] = field(default_factory=list)
    coded_by: str = "codebook"      # "codebook" or the id of the person whose manual code applies


@dataclass
class Theme:
    id: str
    name: str
    kind: str                       # "problem" or "praise"
    keywords: list[str]


@dataclass
class RoadmapItem:
    id: str
    title: str
    themes: list[str]
    reach: float
    impact: float
    confidence: float
    effort: float
    proposed_by: str
    status: str
    pinned: bool = False
    pin_note: str = ""

    @property
    def rice(self) -> float:
        return round(self.reach * self.impact * self.confidence / self.effort, 2)


def _read_csv(path: str | Path, required: list[str]) -> list[dict]:
    p = Path(path)
    if not p.exists():
        raise InputError(f"{p}: file not found")
    with open(p, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        cols = reader.fieldnames or []
    missing = [c for c in required if c not in cols]
    if missing:
        raise InputError(f"{p}: missing column(s) {', '.join(missing)}")
    return rows


def _date(value: str, where: str) -> date:
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        raise InputError(f"{where}: date '{value}' is not YYYY-MM-DD") from None


def _num(value: str, where: str, positive: bool = False) -> float:
    try:
        x = float(value)
    except ValueError:
        raise InputError(f"{where}: '{value}' is not a number") from None
    if x < 0 or (positive and x == 0):
        raise InputError(f"{where}: {value} must be {'greater than' if positive else 'at least'} 0")
    return x


def load_feedback(path: str | Path, segments: dict[str, int]) -> list[dict]:
    rows = _read_csv(path, ["id", "date", "channel", "user_id", "segment", "text"])
    seen = set()
    out = []
    for i, r in enumerate(rows, 2):
        where = f"{path}: row {i}"
        if not r["id"] or r["id"] in seen:
            raise InputError(f"{where}: id '{r['id']}' is empty or repeated")
        seen.add(r["id"])
        if r["channel"] not in CHANNELS:
            raise InputError(f"{where}: channel '{r['channel']}' is not one of {', '.join(CHANNELS)}")
        if not USER_RE.match(r["user_id"] or ""):
            raise InputError(f"{where}: user_id must be a pseudonymous id (letters, digits, _ or -), not '{r['user_id'][:20]}'")
        if r["segment"] not in segments:
            raise InputError(f"{where}: segment '{r['segment']}' is not in the segments file")
        out.append({**r, "date": _date(r["date"], where)})
    return out


def load_segments(path: str | Path) -> dict[str, int]:
    rows = _read_csv(path, ["segment", "target_users"])
    return {r["segment"]: int(_num(r["target_users"], f"{path}: segment {r['segment']}", positive=True)) for r in rows}


def load_codebook(path: str | Path) -> tuple[list[Theme], list[str], str]:
    cb = json.loads(Path(path).read_text(encoding="utf-8"))
    themes = [Theme(t["id"], t["name"], t.get("kind", "problem"), [k.lower() for k in t["keywords"]]) for t in cb["themes"]]
    ids = [t.id for t in themes]
    if len(set(ids)) != len(ids):
        raise InputError(f"{path}: repeated theme id")
    return themes, [m.lower() for m in cb.get("severity_markers", [])], cb.get("version", "?")


def load_manual_codes(path: str | Path | None, theme_ids: set[str], item_ids: set[str]) -> dict[str, tuple[list[str], str]]:
    if not path:
        return {}
    out = {}
    for i, r in enumerate(_read_csv(path, ["item_id", "themes", "coded_by"]), 2):
        where = f"{path}: row {i}"
        if r["item_id"] not in item_ids:
            raise InputError(f"{where}: item '{r['item_id']}' is not in the feedback file")
        themes = [t.strip() for t in (r["themes"] or "").split(";") if t.strip()]
        for t in themes:
            if t not in theme_ids:
                raise InputError(f"{where}: theme '{t}' is not in the codebook")
        if not r["coded_by"]:
            raise InputError(f"{where}: coded_by is required (who made the call)")
        out[r["item_id"]] = (themes, r["coded_by"])
    return out


def load_roadmap(path: str | Path, theme_ids: set[str]) -> list[RoadmapItem]:
    rows = _read_csv(path, ["id", "title", "themes", "reach", "impact", "confidence", "effort"])
    items = []
    for i, r in enumerate(rows, 2):
        where = f"{path}: row {i} ({r['id']})"
        themes = [t.strip() for t in (r["themes"] or "").split(";") if t.strip()]
        for t in themes:
            if t not in theme_ids:
                raise InputError(f"{where}: theme '{t}' is not in the codebook")
        conf = _num(r["confidence"], where)
        if conf > 1:
            raise InputError(f"{where}: confidence {conf} must be a share between 0 and 1")
        items.append(RoadmapItem(r["id"], r["title"], themes, _num(r["reach"], where), _num(r["impact"], where),
                                 conf, _num(r["effort"], where, positive=True), r.get("proposed_by", ""),
                                 r.get("status", "planned"), r.get("pinned", "").lower() == "yes", r.get("pin_note", "")))
    if len({x.id for x in items}) != len(items):
        raise InputError(f"{path}: repeated roadmap id")
    return items


def load_active_users(path: str | Path | None, use_case: str | None, start: date, end: date) -> tuple[set[str] | None, dict]:
    """Active users of the assistant in the window, from ai-adoption-tracker's events (optional)."""
    if not path:
        return None, {}
    rows = _read_csv(path, ["date", "use_case_id", "user_id", "action"])
    rows = [r for r in rows if (not use_case or r["use_case_id"] == use_case) and start <= _date(r["date"], str(path)) <= end]
    counts = {a: sum(1 for r in rows if r["action"] == a) for a in ("task_completed", "feedback_positive", "feedback_negative")}
    return {r["user_id"] for r in rows}, counts
