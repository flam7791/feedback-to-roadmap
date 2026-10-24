"""Turn the backlog into GitHub issues the team can pick up.

Dry run by default: prints the `gh` commands. With --run it executes them (needs the GitHub CLI,
signed in, and labels are created if missing). Stories already Done are skipped unless --all.

    python tools/seed_issues.py --repo OWNER/REPO            # print commands
    python tools/seed_issues.py --repo OWNER/REPO --run      # create the issues
"""
from __future__ import annotations

import argparse
import csv
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def body(s: dict) -> str:
    ac = "\n".join(f"- [ ] {x.strip()}" for x in s["acceptance"].split(";") if x.strip())
    return (f"**Story**\n\n{s['story']}\n\n**Acceptance criteria**\n\n{ac}\n\n"
            f"**Feature:** {s['feature']} | **Priority:** {s['priority']} | **Estimate:** {s['estimate']} pts | "
            f"**Target:** {s['iteration']}\n\n"
            "Definition of Done: see docs/team/working-agreement.md. The PR adds a test named "
            f"`test_{s['id'].replace('-', '')}_...` so tools/trace.py can prove this story.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--all", action="store_true", help="include stories already Done")
    a = ap.parse_args()
    with open(ROOT / "docs" / "team" / "backlog.csv", newline="", encoding="utf-8") as f:
        stories = [s for s in csv.DictReader(f) if a.all or s["status"] != "Done"]

    labels = sorted({"story"} | {s["priority"].lower() for s in stories} | {f"feature:{s['feature'].split(' ')[0].lower()}" for s in stories})
    cmds = [["gh", "label", "create", lb, "--repo", a.repo, "--force"] for lb in labels]
    for s in stories:
        cmds.append(["gh", "issue", "create", "--repo", a.repo, "--title", f"{s['id']} {s['title']}",
                     "--body", body(s), "--label", f"story,{s['priority'].lower()},feature:{s['feature'].split(' ')[0].lower()}"])
    for c in cmds:
        if a.run:
            subprocess.run(c, check=True)
        else:
            print(" ".join(shlex.quote(x) for x in c))
    print(f"{'created' if a.run else 'would create'} {len(stories)} issues and {len(labels)} labels", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
