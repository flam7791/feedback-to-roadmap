"""Measure the codebook against a human-coded gold set: precision and recall per theme.

Precision matters most: a wrong tag puts a person's voice behind the wrong roadmap item. A missed
tag only sends the item to the uncoded queue, where the product owner codes it by hand.
"""
from __future__ import annotations

import csv
from pathlib import Path

from .coding import Codebook
from .data import InputError, Theme
from .screen import redact


def load_gold(gold: str | Path, feedback: str | Path | None = None) -> list[tuple[str, str, set[str]]]:
    with open(gold, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    texts = {}
    if feedback:
        with open(feedback, newline="", encoding="utf-8") as f:
            texts = {r["id"]: r["text"] for r in csv.DictReader(f)}
    out = []
    for r in rows:
        text = r.get("text") or texts.get(r["id"])
        if text is None:
            raise InputError(f"{gold}: no text for {r['id']} (give --feedback for a labels-only file)")
        out.append((r["id"], redact(text)[0], {t for t in (r["themes"] or "").split(";") if t}))
    return out


def measure(gold: list[tuple[str, str, set[str]]], themes: list[Theme]) -> dict:
    cb = Codebook(themes)
    per = {t.id: {"tp": 0, "fp": 0, "fn": 0} for t in themes}
    exact = missed_all = wrong = 0
    errors = []
    for iid, text, truth in gold:
        pred = set(cb.match(text))
        exact += pred == truth
        missed_all += bool(truth) and not pred
        wrong += bool(pred - truth)
        for t in per:
            per[t]["tp"] += t in pred and t in truth
            per[t]["fp"] += t in pred and t not in truth
            per[t]["fn"] += t not in pred and t in truth
        if pred != truth:
            errors.append({"id": iid, "text": text, "gold": sorted(truth), "codebook": sorted(pred)})

    def pr(d):
        p = d["tp"] / (d["tp"] + d["fp"]) if d["tp"] + d["fp"] else None
        r = d["tp"] / (d["tp"] + d["fn"]) if d["tp"] + d["fn"] else None
        return p, r

    rows = []
    for t in themes:
        p, r = pr(per[t.id])
        rows.append({"theme": t.id, "name": t.name, **per[t.id], "precision": p, "recall": r})
    tot = {k: sum(per[t][k] for t in per) for k in ("tp", "fp", "fn")}
    p, r = pr(tot)
    n = len(gold)
    return {"items": n, "per_theme": rows, "micro": {**tot, "precision": p, "recall": r},
            "exact_match": round(exact / n, 3) if n else None,
            "items_with_a_wrong_tag": wrong, "items_sent_to_uncoded_queue_wrongly": missed_all,
            "errors": errors}


def to_markdown(res: dict, title: str) -> str:
    f = lambda x: "-" if x is None else f"{x:.2f}"  # noqa: E731
    L = [f"### {title}", "", f"{res['items']} items. Micro precision **{f(res['micro']['precision'])}**, recall "
         f"**{f(res['micro']['recall'])}**; exact match {res['exact_match']}; items with a wrong tag: "
         f"{res['items_with_a_wrong_tag']}; items that went to the uncoded queue but had a theme: "
         f"{res['items_sent_to_uncoded_queue_wrongly']}.", "",
         "| Theme | TP | FP | FN | Precision | Recall |", "|---|---|---|---|---|---|"]
    for r in res["per_theme"]:
        if r["tp"] + r["fp"] + r["fn"]:
            L.append(f"| {r['theme']} {r['name']} | {r['tp']} | {r['fp']} | {r['fn']} | {f(r['precision'])} | {f(r['recall'])} |")
    if res["errors"]:
        L += ["", "Disagreements:", ""]
        L += [f"- {e['id']}: gold {', '.join(e['gold']) or 'none'}; codebook {', '.join(e['codebook']) or 'none'}: {e['text']}"
              for e in res["errors"]]
    return "\n".join(L) + "\n"
