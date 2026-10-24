"""The worked example end to end: one review cycle of the HR policy assistant.

    python tools/demo.py [--out out]

Runs the review on the synthetic sample, then the product owner's decisions as recorded in
docs/product/07-worked-example.md: reject the reach cut for R5 (the survey was English-only),
pin R1 (a compliance obligation), accept the rest, apply. Then the usage events.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from f2r.cli import main  # noqa: E402

S = ROOT / "data" / "sample"
REJECT_R5 = ("CH-07=The survey went out in English only and Poland is almost silent (1 of 85 voices): the people "
             "who need answers in their language are the least able to tell us. Keep 60 until the translated pulse survey runs.")
PIN_R1 = ("R1=The 2026 policies take effect on 1 January; publishing them is a compliance obligation, not a bet "
          "on feedback. Kept above the cut regardless of its score.")


def run(*args: str) -> None:
    if main(list(args)) != 0:
        raise SystemExit(f"failed: f2r {' '.join(args)}")


def review(out: str) -> Path:
    run("review", str(S / "feedback.csv"), "--roadmap", str(S / "roadmap.csv"), "--segments", str(S / "segments.csv"),
        "--codebook", str(ROOT / "config" / "codebook.json"), "--scoring", str(ROOT / "config" / "scoring.json"),
        "--codes", str(S / "manual_codes.csv"), "--events", str(S / "tracker_events_uc03.csv"), "--use-case", "UC03",
        "--product", "HR policy assistant", "--start", "2026-08-03", "--end", "2026-09-27", "--as-of", "2026-10-01",
        "--out", out)
    return Path(out) / "pack.json"


def demo(out: str) -> None:
    pack = str(review(out))
    team = str(ROOT / "config" / "team.json")
    run("decide", pack, "--by", "po-01", "--reject", REJECT_R5, "--pin", PIN_R1, "--team", team, "--date", "2026-10-02")
    run("decide", pack, "--by", "po-01", "--accept-rest", "--team", team, "--date", "2026-10-02")
    run("apply", pack, "--by", "po-01", "--out", out, "--team", team, "--date", "2026-10-02")
    print()
    run("events", pack)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out")
    demo(ap.parse_args().out)
