"""Usage events in the ai-adoption-tracker format (date, use_case_id, user_id, action).

So this tool's own pilot can be reviewed for scale, iterate or stop on evidence: one
`task_completed` per review applied by a product owner. Ids are the roster's pseudonymous ids.
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path

FIELDS = ["date", "use_case_id", "user_id", "action"]


def collect(packs: list[str | Path], use_case_id: str) -> list[dict]:
    rows = []
    for p in packs:
        pack = json.loads(Path(p).read_text(encoding="utf-8"))
        prop = pack["proposal"]
        if prop["status"] == "applied":
            rows.append({"date": prop["applied_on"], "use_case_id": use_case_id, "user_id": prop["applied_by"],
                         "action": "task_completed"})
    return sorted(rows, key=lambda r: (r["date"], r["user_id"]))


def to_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()
