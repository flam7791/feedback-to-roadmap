"""f2r: feedback in, evidence and a roadmap change proposal out; the product owner decides.

    f2r review data/sample/feedback.csv --roadmap data/sample/roadmap.csv --segments data/sample/segments.csv --out out
    f2r decide out/pack.json --by po-01 --accept CH-01 CH-02 --reject "CH-05=reason" --pin "R1=reason"
    f2r apply  out/pack.json --by po-01 --out out
    f2r measure --gold data/gold/heldout.csv
    f2r events out/pack.json
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from .data import InputError, load_codebook
from .decision import DecisionError, apply, decide, load, load_team, save
from .events import collect, to_csv
from .measure import load_gold, measure, to_markdown
from .render import decision_record, to_html, to_markdown as pack_md, write_pack
from .review import run_review


def _kv(values: list[str], what: str) -> dict[str, str]:
    out = {}
    for v in values or []:
        if "=" not in v:
            raise DecisionError(f"{what} '{v}' needs a note: use ID=\"reason\"")
        k, note = v.split("=", 1)
        out[k.strip()] = note
    return out


def _date(s: str | None) -> date | None:
    return date.fromisoformat(s) if s else None


def _rerender(pack: dict, path: Path) -> None:
    save(pack, path)
    path.with_suffix(".md").write_text(pack_md(pack), encoding="utf-8")
    path.with_suffix(".html").write_text(to_html(pack), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="f2r", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("review", help="screen, code and weigh feedback; propose roadmap changes")
    r.add_argument("feedback")
    r.add_argument("--roadmap", required=True)
    r.add_argument("--segments", required=True)
    r.add_argument("--codebook", default="config/codebook.json")
    r.add_argument("--scoring", default="config/scoring.json")
    r.add_argument("--codes", help="the product owner's manual codes (CSV)")
    r.add_argument("--events", help="ai-adoption-tracker usage events, to tell active users from lapsed ones")
    r.add_argument("--use-case", help="use case id in the events file (e.g. UC03)")
    r.add_argument("--product", default="the assistant")
    r.add_argument("--start")
    r.add_argument("--end")
    r.add_argument("--as-of")
    r.add_argument("--out", default="out")

    d = sub.add_parser("decide", help="the product owner accepts, rejects or pins")
    d.add_argument("pack")
    d.add_argument("--by", required=True)
    d.add_argument("--accept", nargs="*", default=[])
    d.add_argument("--reject", action="append", default=[], metavar="CH-XX=NOTE")
    d.add_argument("--pin", action="append", default=[], metavar="RX=NOTE")
    d.add_argument("--accept-rest", action="store_true", help="accept every change still pending")
    d.add_argument("--team", default="config/team.json")
    d.add_argument("--date")

    a = sub.add_parser("apply", help="write the next roadmap version once every change is decided")
    a.add_argument("pack")
    a.add_argument("--by", required=True)
    a.add_argument("--out", default="out")
    a.add_argument("--team", default="config/team.json")
    a.add_argument("--date")

    m = sub.add_parser("measure", help="codebook precision and recall against a human-coded gold set")
    m.add_argument("--gold", required=True)
    m.add_argument("--feedback", help="texts, when the gold file has labels only")
    m.add_argument("--codebook", default="config/codebook.json")
    m.add_argument("--title")
    m.add_argument("--out")

    e = sub.add_parser("events", help="usage events in the ai-adoption-tracker format")
    e.add_argument("packs", nargs="+")
    e.add_argument("--use-case", default="UC10")

    args = ap.parse_args(argv)
    try:
        if args.cmd == "review":
            pack = run_review(args.feedback, args.roadmap, args.segments, args.codebook, args.scoring, args.codes,
                              args.events, args.use_case, args.product, _date(args.start), _date(args.end), _date(args.as_of))
            paths = write_pack(pack, args.out)
            p = pack["proposal"]
            print(f"{pack['summary']['items']} items, {pack['summary']['voices']} people, "
                  f"{sum(1 for t in pack['themes'] if t['users'])} themes; {len(p['changes'])} proposed change(s), "
                  f"{len(p['opinion_only'])} opinion-only item(s), {len(p['gaps'])} gap(s); "
                  f"{pack['summary']['flagged']} flagged -> {paths[1]}")
        elif args.cmd == "decide":
            path = Path(args.pack)
            pack = decide(load(path), load_team(args.team), args.by, args.accept, _kv(args.reject, "reject"),
                          _kv(args.pin, "pin"), args.accept_rest, _date(args.date))
            _rerender(pack, path)
            pending = sum(1 for c in pack["proposal"]["changes"] if c["status"] == "pending")
            print(f"recorded; {pending} change(s) still pending")
        elif args.cmd == "apply":
            path = Path(args.pack)
            pack = load(path)
            res = apply(pack, load_team(args.team), args.by, args.out, _date(args.date))
            _rerender(pack, path)
            Path(args.out, "decision-record.md").write_text(decision_record(pack, res), encoding="utf-8")
            above = [r["id"] for r in res["ranking"] if r["above_cut"]]
            print(f"applied {len(res['applied'])} change(s); above the cut: {', '.join(above)}; "
                  f"{pack['proposal']['notify_users']} people to tell -> {res['roadmap_next']}")
        elif args.cmd == "measure":
            themes, _, version = load_codebook(args.codebook)
            res = measure(load_gold(args.gold, args.feedback), themes)
            text = to_markdown(res, args.title or f"Codebook {version} on {Path(args.gold).name}")
            if args.out:
                Path(args.out).write_text(text, encoding="utf-8")
            print(text)
        elif args.cmd == "events":
            sys.stdout.write(to_csv(collect(args.packs, args.use_case)))
    except (InputError, DecisionError) as exc:
        print(f"f2r: {exc}", file=sys.stderr)
        return 2
    return 0
