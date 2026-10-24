"""The evidence pack (Markdown, HTML; the JSON is the pack itself) and the decision record."""
from __future__ import annotations

import html
from pathlib import Path

CH = {"in_app": "in-app", "survey": "survey", "ticket": "ticket", "interview": "interview"}


def pct(x: float) -> str:
    return f"{int(x * 100 + 0.5)}%"


def _fmt(x) -> str:
    return f"{x:g}" if isinstance(x, (int, float)) else str(x)


def _moves(pack: dict) -> tuple[list[str], list[str]]:
    p = pack["proposal"]
    after_key = "ranking_after" if p["status"] == "applied" else "ranking_if_all_accepted"
    before = {r["id"]: r["above_cut"] for r in p["ranking_before"]}
    after = {r["id"]: r["above_cut"] for r in p[after_key]}
    up = [i for i in after if after[i] and not before.get(i)]
    down = [i for i in after if before.get(i) and not after[i]]
    return up, down


def headline(pack: dict) -> list[str]:
    s, p = pack["summary"], pack["proposal"]
    problems = sorted((t for t in pack["themes"] if t["kind"] == "problem" and t["users"] and not t["spike_week"]),
                      key=lambda t: (-t["users"], t["id"]))
    lines = [f"{s['items']} items from {s['voices']} people, of {s['target_users']} target users "
             f"(voice rate {s['voice_rate']})"
             + (f"; {s['active_users']} active users in the window, thumbs {s['usage'].get('feedback_positive', 0)} up "
                f"and {s['usage'].get('feedback_negative', 0)} down" if s["active_users"] is not None else "") + "."]
    if problems:
        t = problems[0]
        na = f", {t['not_active']} of them not active users" if t["not_active"] is not None else ""
        lines.append(f"Most reported problem: **{t['id']} {t['name']}**, {t['users']} people in "
                     f"{len(t['channels'])} channels{na}.")
    up, down = _moves(pack)
    verb = "moved" if p["status"] == "applied" else "would move"
    if up or down:
        lead = f"The decisions {verb} " if p["status"] == "applied" else f"If every change is accepted, the evidence {verb} "
        lines.append(lead + (f"{', '.join(up)} above the cut line" if up else "")
                     + (" and " if up and down else "") + (f"{', '.join(down)} below it" if down else "") + ".")
    else:
        lines.append("The proposed changes do not move anything across the cut line.")
    silent = [x for x in pack["silent_segments"] if x["silent"]]
    if silent:
        lines.append("Not hearing from: " + "; ".join(
            f"**{x['segment']}** ({x['voices']} of {s['voices']} voices, {pct(x['share_of_users'])} of target users)"
            for x in silent) + ".")
    for sp in pack["spikes"]:
        lines.append(f"Spike: **{sp['theme']} {sp['name']}**, {sp['in_week']} of {sp['items']} items in the week of "
                     f"{sp['week']}. Looks like an incident: route to support, not to the roadmap.")
    lines.append(f"Screening: {s['flagged']} item(s) flagged and excluded from the evidence; "
                 f"{s['redactions']} personal detail(s) redacted. Uncoded: {s['uncoded']} item(s) for the product owner.")
    return lines


def next_step(pack: dict) -> str:
    p = pack["proposal"]
    if p["status"] == "applied":
        return f"Applied by {p['applied_by']} on {p['applied_on']}: roadmap.next.csv written; the source roadmap is unchanged."
    pending = [c["id"] for c in p["changes"] if c["status"] == "pending"]
    if pending:
        return (f"The product owner decides each of the {len(pending)} pending change(s): accept, or reject with a note; "
                f"pin any item that must stay above the cut line, with a note. Then `f2r apply`.")
    return "Every change is decided. The product owner runs `f2r apply` to write the next roadmap version."


def mermaid_tree(pack: dict) -> str:
    themes = {t["id"]: t for t in pack["themes"]}
    rows = pack["proposal"].get("ranking_after") or pack["proposal"]["ranking_if_all_accepted"]
    items = {r["id"]: r for r in rows}
    links = {c["item"]: c["evidence"]["themes"] for c in pack["proposal"]["changes"]}
    for o in pack["proposal"]["opinion_only"]:
        links.setdefault(o["item"], [])
    out = ["flowchart LR", f'    O(["Outcome: more of the {pack["summary"]["target_users"]} target users get answers they can act on"])']
    used = set()
    for t in sorted(themes.values(), key=lambda t: (-t["users"], t["id"])):
        if t["kind"] != "problem" or not t["users"]:
            continue
        label = f'{t["id"]} {t["name"]}<br/>{t["users"]} people, {t["tier"]}' + (" - spike" if t["spike_week"] else "")
        out.append(f'    O --> {t["id"]}["{label}"]')
        used.add(t["id"])
    item_themes = {}
    for r in rows:
        item_themes[r["id"]] = links.get(r["id"])
    for iid, r in items.items():
        ts = [t for t in (item_themes.get(iid) or []) if t in used]
        shape = f'{iid}{{{{"{iid} {r["title"]}<br/>{"above" if r["above_cut"] else "below"} the cut"}}}}'
        if ts:
            for i, t in enumerate(ts):
                out.append(f"    {t} --> {shape if i == 0 else iid}")
        else:
            out.append(f'    O -. no evidence .-> {shape}')
    return "\n".join(out)


def to_markdown(pack: dict) -> str:
    p, s = pack["proposal"], pack["summary"]
    L = [f"# Feedback review: {pack['product']}" + (f" ({pack['use_case']})" if pack["use_case"] else ""), "",
         f"Window {pack['window']['start']} to {pack['window']['end']} · as of {pack['as_of']} · {pack['tool']} · "
         f"codebook {pack['inputs']['codebook_version']} · scoring {pack['inputs']['scoring_version']}", "",
         f"**Next human step:** {next_step(pack)}", "", "## In one minute", ""]
    L += [f"- {x}" for x in headline(pack)]
    L += ["", "## Themes: people, not rows", "",
          "| Theme | People | Items | Channels | Segments | Not active | Severe | Tier | Est. reach |",
          "|---|---|---|---|---|---|---|---|---|"]
    for t in sorted(pack["themes"], key=lambda t: (t["kind"] != "problem", -t["users"], t["id"])):
        if not t["users"]:
            continue
        L.append(f"| {t['id']} {t['name']}{' (spike)' if t['spike_week'] else ''} | {t['users']} | {t['items']} | "
                 f"{', '.join(f'{CH[c]} {n}' for c, n in sorted(t['channels'].items()))} | "
                 f"{', '.join(f'{k} {v}' for k, v in sorted(t['segments'].items(), key=lambda x: (-x[1], x[0])))} | "
                 f"{'-' if t['not_active'] is None else t['not_active']} | {pct(t['severe_share'])} | "
                 f"{t['tier'] if t['kind'] == 'problem' else 'praise'} | {t['reach_estimate'] or '-'} |")
    L += ["", "People: distinct users. Not active: reporters with no use of the assistant in the window. "
          "Severe: items that say the person gave up, escalated or got a wrong answer. Est. reach: people / voice rate, "
          "only for strong and moderate themes.", "", "## What people said (verbatim, after redaction)", ""]
    for t in sorted(pack["themes"], key=lambda t: (t["kind"] != "problem", -t["users"], t["id"])):
        if not t["quotes"]:
            continue
        L.append(f"**{t['id']} {t['name']}** ({t['users']} people)")
        L.append("")
        for q in t["quotes"]:
            L.append(f"> {q['text']}  \n> <sub>{q['item_id']} · {CH[q['channel']]} · {q['segment']} · {q['date']}</sub>")
            L.append("")
    L += ["## Proposed changes", "",
          "Nothing changes until the product owner decides. Impact and effort are never changed by the tool.", "",
          "| Change | Item | Field | From | To | Status | Why |", "|---|---|---|---|---|---|---|"]
    for c in p["changes"]:
        st = c["status"] + (f" by {c['decided_by']}" if c["decided_by"] else "") + (f": {c['note']}" if c["note"] else "")
        L.append(f"| {c['id']} | {c['item']} | {c['field']} | {_fmt(c['from'])} | {_fmt(c['to'])} | {st} | {c['rule']} |")
    if p["pins"]:
        L += ["", "Pinned above the cut line: " + "; ".join(f"**{x['item']}** by {x['by']}: {x['note']}" for x in p["pins"])]
    after_key = "ranking_after" if p["status"] == "applied" else "ranking_if_all_accepted"
    after_label = "after the decisions" if p["status"] == "applied" else "if every change is accepted"
    L += ["", f"## Ranking before and {after_label} (capacity {pack['capacity_points']:g} points)", "",
          "| Item | RICE before | Before | RICE after | After |", "|---|---|---|---|---|"]
    before = {r["id"]: r for r in p["ranking_before"]}
    for r in p[after_key]:
        b = before[r["id"]]
        L.append(f"| {r['id']} {r['title']}{' (pinned)' if r['pinned'] else ''} | {b['rice']:g} | "
                 f"{'above' if b['above_cut'] else 'below'} | {r['rice']:g} | {'**above**' if r['above_cut'] else 'below'} |")
    L += ["", "RICE = reach x impact x confidence / effort. Pinned items take capacity first; then highest RICE "
          "first, skipping any item that no longer fits.", "", "## Flags for the product owner", ""]
    for o in p["opinion_only"]:
        L.append(f"- **Opinion-only:** {o['item']} {o['title']} (proposed by {o['proposed_by']}): {o['why']}.")
    for g in p["gaps"]:
        L.append(f"- **Gap:** {g['theme']} {g['name']} ({g['users']} people, {g['tier']}): {g['kind']}.")
    for sp in pack["spikes"]:
        L.append(f"- **Spike:** {sp['theme']} {sp['name']}: {sp['in_week']} of {sp['items']} items in the week of {sp['week']}.")
    L += ["", "| Segment | Target users | Voices | Share of users | Share of voices | Ratio |", "|---|---|---|---|---|---|"]
    for x in pack["silent_segments"]:
        L.append(f"| {x['segment']}{' **(silent)**' if x['silent'] else ''} | {x['target_users']} | {x['voices']} | "
                 f"{pct(x['share_of_users'])} | {pct(x['share_of_voices'])} | {x['ratio']} |")
    L += ["", "## Opportunity solution tree", "", "```mermaid", mermaid_tree(pack), "```", "",
          "## Screening and coding", ""]
    for f in pack["flagged"]:
        L.append(f"- **Flagged, excluded from the evidence:** {f['item_id']} ({', '.join(f['rules'])}): {f['text']}")
    for m in pack["manual_codes"]:
        L.append(f"- Manual code applied: {m['item_id']} -> {', '.join(m['themes']) or 'no theme'} by {m['coded_by']}")
    for c in pack["new_theme_candidates"]:
        L.append(f"- New-theme candidate: \"{c['word']}\" in {c['items']} uncoded items ({', '.join(c['item_ids'])})")
    L += ["", f"Uncoded queue ({len(pack['uncoded'])}):", ""]
    L += [f"- {u['item_id']} ({CH[u['channel']]}, {u['segment']}): {u['text']}" for u in pack["uncoded"]]
    if pack["decision_history"]:
        L += ["", "## Decision history", ""]
        L += [f"- {d['on']} {d['by']} ({d['role']}): accepted {', '.join(d['accepted']) or '-'}"
              f"{' and the rest' if d['accept_rest'] else ''}; rejected {', '.join(d['rejected']) or '-'}; "
              f"pinned {', '.join(d['pinned']) or '-'}" for d in pack["decision_history"]]
    return "\n".join(L) + "\n"


CSS = """
:root{--bg:#fafaf8;--fg:#1f2328;--mut:#5b636d;--line:#d8dce0;--card:#fff;--acc:#1f5fbf;--warn:#9a5b00;--warnbg:#fff4e0;--ok:#17703b;--okbg:#e8f5ec;--bad:#a1262b;--badbg:#fbe9ea}
@media (prefers-color-scheme:dark){:root{--bg:#16181b;--fg:#e6e8ea;--mut:#9aa3ad;--line:#33383e;--card:#1e2125;--acc:#7fb0ff;--warn:#f0b35a;--warnbg:#3a2c12;--ok:#7bd69b;--okbg:#15301f;--bad:#f08a8f;--badbg:#3a1a1c}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:24px;margin:0 0 4px}h2{font-size:18px;margin:28px 0 10px}
.meta{color:var(--mut);font-size:13px}
.step{background:var(--warnbg);color:var(--fg);border-left:4px solid var(--warn);padding:10px 14px;border-radius:6px;margin:16px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px 16px}
table{border-collapse:collapse;width:100%;font-size:13.5px;background:var(--card)}
th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{background:color-mix(in srgb,var(--line) 35%,var(--card))}
.num{text-align:right;font-variant-numeric:tabular-nums}
.tier{display:inline-block;padding:1px 8px;border-radius:10px;font-size:12px}
.strong{background:var(--okbg);color:var(--ok)}.moderate{background:var(--warnbg);color:var(--warn)}.weak,.none{background:var(--badbg);color:var(--bad)}
.praise{background:var(--okbg);color:var(--ok)}
blockquote{margin:6px 0;padding:6px 12px;border-left:3px solid var(--acc);background:var(--card)}
blockquote small{display:block;color:var(--mut);font-size:12px}
.above{font-weight:600;color:var(--ok)}.below{color:var(--mut)}
.flag{background:var(--badbg);color:var(--fg);border-radius:6px;padding:8px 12px;margin:6px 0}
.wrap{overflow-x:auto}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
"""


def _e(x) -> str:
    return html.escape(str(x))


def _bold(s: str) -> str:
    parts = s.split("**")
    return "".join(_e(p) if i % 2 == 0 else f"<b>{_e(p)}</b>" for i, p in enumerate(parts))


def to_html(pack: dict) -> str:
    p, s = pack["proposal"], pack["summary"]
    H = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
         f"<title>Feedback review: {_e(pack['product'])}</title><style>{CSS}</style></head><body><main>",
         f"<h1>Feedback review: {_e(pack['product'])}{' (' + _e(pack['use_case']) + ')' if pack['use_case'] else ''}</h1>",
         f"<div class='meta'>Window {_e(pack['window']['start'])} to {_e(pack['window']['end'])} · as of {_e(pack['as_of'])} · "
         f"{_e(pack['tool'])} · codebook {_e(pack['inputs']['codebook_version'])} · scoring {_e(pack['inputs']['scoring_version'])}</div>",
         f"<div class='step'><b>Next human step:</b> {_bold(next_step(pack).replace('`', ''))}</div>",
         "<h2>In one minute</h2><div class='card'><ul>" + "".join(f"<li>{_bold(x)}</li>" for x in headline(pack)) + "</ul></div>",
         "<h2>Themes: people, not rows</h2><div class='wrap'><table><tr><th>Theme</th><th>People</th><th>Items</th><th>Channels</th>"
         "<th>Segments</th><th>Not active</th><th>Severe</th><th>Tier</th><th>Est. reach</th></tr>"]
    for t in sorted(pack["themes"], key=lambda t: (t["kind"] != "problem", -t["users"], t["id"])):
        if not t["users"]:
            continue
        tier = t["tier"] if t["kind"] == "problem" else "praise"
        spike = " <span class='tier weak'>spike</span>" if t["spike_week"] else ""
        H.append(f"<tr><td><b>{_e(t['id'])}</b> {_e(t['name'])}{spike}</td>"
                 f"<td class='num'><b>{t['users']}</b></td><td class='num'>{t['items']}</td>"
                 f"<td>{_e(', '.join(f'{CH[c]} {n}' for c, n in sorted(t['channels'].items())))}</td>"
                 f"<td>{_e(', '.join(f'{k} {v}' for k, v in sorted(t['segments'].items(), key=lambda x: (-x[1], x[0]))))}</td>"
                 f"<td class='num'>{'-' if t['not_active'] is None else t['not_active']}</td>"
                 f"<td class='num'>{pct(t['severe_share'])}</td><td><span class='tier {tier}'>{tier}</span></td>"
                 f"<td class='num'>{t['reach_estimate'] or '-'}</td></tr>")
    H.append("</table></div>")
    H.append("<h2>Proposed changes</h2><div class='wrap'><table><tr><th>Change</th><th>Item</th><th>Field</th><th>From</th><th>To</th><th>Status</th><th>Why</th></tr>")
    for c in p["changes"]:
        st = c["status"] + (f" by {c['decided_by']}" if c["decided_by"] else "")
        H.append(f"<tr><td>{_e(c['id'])}</td><td><b>{_e(c['item'])}</b></td><td>{_e(c['field'])}</td><td class='num'>{_e(_fmt(c['from']))}</td>"
                 f"<td class='num'><b>{_e(_fmt(c['to']))}</b></td><td>{_e(st)}{'<br><i>' + _e(c['note']) + '</i>' if c['note'] else ''}</td><td>{_e(c['rule'])}</td></tr>")
    H.append("</table></div>")
    after_key = "ranking_after" if p["status"] == "applied" else "ranking_if_all_accepted"
    before = {r["id"]: r for r in p["ranking_before"]}
    H.append(f"<h2>Ranking before and {'after the decisions' if p['status'] == 'applied' else 'if every change is accepted'} "
             f"(capacity {pack['capacity_points']:g} points)</h2><div class='wrap'><table><tr><th>Item</th><th>Effort</th><th>RICE before</th><th>Before</th><th>RICE after</th><th>After</th></tr>")
    for r in p[after_key]:
        b = before[r["id"]]
        pin = " <span class='tier moderate'>pinned</span>" if r["pinned"] else ""
        H.append(f"<tr><td><b>{_e(r['id'])}</b> {_e(r['title'])}{pin}</td>"
                 f"<td class='num'>{r['effort']:g}</td><td class='num'>{b['rice']:g}</td>"
                 f"<td class='{'above' if b['above_cut'] else 'below'}'>{'above' if b['above_cut'] else 'below'}</td>"
                 f"<td class='num'>{r['rice']:g}</td><td class='{'above' if r['above_cut'] else 'below'}'>{'above' if r['above_cut'] else 'below'}</td></tr>")
    H.append("</table></div><h2>Flags for the product owner</h2>")
    for o in p["opinion_only"]:
        H.append(f"<div class='flag'><b>Opinion-only:</b> {_e(o['item'])} {_e(o['title'])} (proposed by {_e(o['proposed_by'])}): {_e(o['why'])}.</div>")
    for g in p["gaps"]:
        H.append(f"<div class='flag'><b>Gap:</b> {_e(g['theme'])} {_e(g['name'])} ({g['users']} people, {_e(g['tier'])}): {_e(g['kind'])}.</div>")
    for sp in pack["spikes"]:
        H.append(f"<div class='flag'><b>Spike:</b> {_e(sp['theme'])} {_e(sp['name'])}: {sp['in_week']} of {sp['items']} items in the week of {_e(sp['week'])}. Route to support.</div>")
    for x in pack["silent_segments"]:
        if x["silent"]:
            H.append(f"<div class='flag'><b>Silent segment:</b> {_e(x['segment'])}: {x['voices']} of {s['voices']} voices "
                     f"({pct(x['share_of_voices'])}) for {pct(x['share_of_users'])} of target users.</div>")
    H.append("<h2>What people said (verbatim, after redaction)</h2><div class='grid'>")
    for t in sorted(pack["themes"], key=lambda t: (t["kind"] != "problem", -t["users"], t["id"])):
        if not t["quotes"]:
            continue
        H.append(f"<div class='card'><b>{_e(t['id'])} {_e(t['name'])}</b> <span class='meta'>{t['users']} people</span>")
        for q in t["quotes"]:
            H.append(f"<blockquote>{_e(q['text'])}<small>{_e(q['item_id'])} · {CH[q['channel']]} · {_e(q['segment'])} · {_e(q['date'])}</small></blockquote>")
        H.append("</div>")
    H.append("</div><h2>Screening and coding</h2>")
    for f in pack["flagged"]:
        H.append(f"<div class='flag'><b>Flagged, excluded from the evidence:</b> {_e(f['item_id'])} ({_e(', '.join(f['rules']))}): {_e(f['text'])}</div>")
    for c in pack["new_theme_candidates"]:
        H.append(f"<p>New-theme candidate: <b>{_e(c['word'])}</b> in {c['items']} uncoded items ({_e(', '.join(c['item_ids']))}).</p>")
    H.append(f"<p class='meta'>{s['uncoded']} uncoded item(s) and {len(pack['manual_codes'])} manual code(s): see the Markdown or JSON pack.</p>")
    H.append("</main></body></html>")
    return "\n".join(H)


def decision_record(pack: dict, result: dict) -> str:
    p = pack["proposal"]
    acc = [c for c in p["changes"] if c["status"] == "accepted"]
    rej = [c for c in p["changes"] if c["status"] == "rejected"]
    up, down = _moves(pack)
    L = [f"# Roadmap decision record: {pack['product']}" + (f" ({pack['use_case']})" if pack["use_case"] else ""), "",
         f"Review of feedback from {pack['window']['start']} to {pack['window']['end']}; applied by {p['applied_by']} on {p['applied_on']}.",
         f"Source roadmap unchanged ({pack['inputs']['roadmap']}); next version written to roadmap.next.csv.", "",
         f"- Changes accepted: {len(acc)} of {len(p['changes'])}; rejected: {len(rej)}; items pinned: {len(p['pins'])}",
         f"- Moved above the cut line: {', '.join(up) or 'none'}; moved below: {', '.join(down) or 'none'}",
         f"- People to tell what changed: {p['notify_users']} (notify.csv, pseudonymous ids)", ""]
    if rej:
        L += ["## Rejected, and why", ""] + [f"- {c['id']} {c['item']} {c['field']} {_fmt(c['from'])} -> {_fmt(c['to'])}: {c['note']}" for c in rej] + [""]
    if p["pins"]:
        L += ["## Pinned against the evidence, and why", ""] + [f"- {x['item']}: {x['note']} ({x['by']}, {x['on']})" for x in p["pins"]] + [""]
    L += ["## Message to the people who told us (draft for the product owner)", "",
          "> You told us about " + "; ".join(sorted({f"{t['name'].lower()}" for t in pack["themes"]
                                                  if any(t["id"] in r_themes for r_themes in _above_themes(pack, result))})) + ".",
          "> In the next cycle the team plans to work on: " + "; ".join(
              f"{r['title']}" for r in result["ranking"] if r["above_cut"]) + ".",
          "> Plans can change; we will tell you when it ships.", "",
          "## Next roadmap", "", "| Rank | Item | RICE | Effort | Above the cut |", "|---|---|---|---|---|"]
    L += [f"| {r['rank']} | {r['id']} {r['title']}{' (pinned)' if r['pinned'] else ''} | {r['rice']:g} | {r['effort']:g} | {'yes' if r['above_cut'] else 'no'} |"
          for r in result["ranking"]]
    return "\n".join(L) + "\n"


def _above_themes(pack: dict, result: dict) -> list[list[str]]:
    return [result["item_themes"].get(r["id"], []) for r in result["ranking"] if r["above_cut"]]


def write_pack(pack: dict, out_dir: str | Path, stem: str = "pack") -> list[Path]:
    from .decision import save
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = [out / f"{stem}.json", out / f"{stem}.md", out / f"{stem}.html"]
    save(pack, paths[0])
    paths[1].write_text(to_markdown(pack), encoding="utf-8")
    paths[2].write_text(to_html(pack), encoding="utf-8")
    return paths
