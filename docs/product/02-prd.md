# 2. Product requirements: feedback-to-roadmap v0.1

Status: v0.1, October 2026. Owner: product owner. Discovery: [01-discovery.md](01-discovery.md).

## Goal

Once a cycle, a product owner turns all the feedback on their internal AI assistant into evidence
per theme and a short list of explained changes to the roadmap's scores, decides on each, and gets
the next roadmap version and the list of people to tell. In under two hours, with every number
traceable to the feedback behind it and every override written down.

## Non-goals (v0.1)

- **Deciding.** The tool proposes; the product owner decides. No automatic re-prioritisation, ever (D2).
- **Changing impact or effort.** Those are the team's judgement. Only reach and confidence move, by written rules.
- **Collecting feedback.** No survey tool, no widget, no connectors (US-21 is Later). Input is a CSV export.
- **Writing solutions.** A gap says "strong problem, no affordable item"; it never invents the item.
- **Sending messages.** The tool drafts the message and lists who to tell; a person sends it.
- **Model calls.** v0.1 is rules-only and reproducible. Model-assisted coding must pass a gate first (US-19, D5).

## Users and the moment of use

The product owner, at the end of a cycle, before planning the next. The sponsor and the delivery
team read the pack and the decision record. Users never see the tool; they receive a message.

## Requirements

| # | Requirement | Story | Priority |
|---|---|---|---|
| R1 | Read in-app, survey, ticket and interview feedback from one CSV; stop on malformed rows with the row and field | US-01 | Must |
| R2 | Redact email addresses, phone numbers and employee numbers before anything reads the text | US-02 | Must |
| R3 | Flag instruction-like text; flagged items count zero and are never quoted | US-03 | Must |
| R4 | Code items from a codebook the product owner owns; manual codes override; uncoded items queued with recurring words as candidates | US-04, US-05 | Must |
| R5 | Per theme: distinct people, channels, segments, severity share, reporters who are not active users, evidence tier, estimated reach | US-06, US-08 | Must |
| R6 | Up to three verbatim quotes per theme, exact, one per person, spread over channels | US-07 | Must |
| R7 | Flag silent segments, spikes, opinion-only items and gaps | US-08, US-09, US-11 | Must |
| R8 | Propose reach and confidence changes, each with its rule and numbers; ranking before and if all accepted, cut at capacity | US-10, US-12 | Must |
| R9 | Only a product owner on the roster decides; notes required for rejections and pins; decisions final | US-13 | Must |
| R10 | Apply only when every change is decided and the source roadmap is unchanged; write a new version, never the source | US-14 | Must |
| R11 | Pack in Markdown, HTML and JSON; decision record; notify list of pseudonymous ids | US-15 | Must |
| R12 | Codebook precision and recall on gold sets | US-16 | Must |
| R13 | Usage events in the ai-adoption-tracker format | US-17 | Should |

## Rules the product owner owns (config files, versioned)

| File | Holds | Default in v0.1 |
|---|---|---|
| `config/codebook.json` | Themes, keywords, severity markers | 9 themes for the HR assistant |
| `config/scoring.json` | Evidence tiers, reach threshold, capacity, silent-segment ratio, spike rule | strong 15+ people, 2+ channels, 2+ segments -> 0.8; moderate 6+ -> 0.5; weak 1+ -> 0.3; no evidence -> 0.2; reach changes above 25%; capacity 10 points |
| `config/team.json` | Who may decide | product owner role only |

Changing any of them is a product decision recorded in the CHANGELOG and followed by the
regression set, like a policy change.

## Success metrics (targets fixed before the pilot; detail in 05)

| Metric | Target |
|---|---|
| Time from exports to applied proposal | under 2 hours for about 150 items |
| Proposals accepted, or rejected with a reason the evidence could not see | at least 70% accepted; every rejection reasoned |
| Cycles where the pack moved an item the product owner agreed should move | at least 2 of 3 |
| Hand-coding time | under 30 minutes per 100 items |
| Guardrail: roadmap changes not made by a product owner | 0 (enforced in code, tested on every push) |
| Guardrail: personal data in any output | 0 (tested on every push) |

## Risks

| Risk | Mitigation |
|---|---|
| Wrong tags put people behind the wrong item (held-out precision 0.69) | Quotes shown for every theme; coding spot-check before deciding is first in Next (US-18) |
| Codebook misses most new phrasing (held-out recall 0.24) | Uncoded queue is part of the job; model coding behind a gold gate (US-19); H4 measures the cost |
| Reach estimate assumes respondents represent non-respondents | Silent-segment flag; segment-weighted reach (US-20); rejection with a note is expected and recorded |
| Evidence used to overrule obligations | Pins: allowed, visible, with a note (D6) |
| Sponsor experiences lowered scores as a challenge | Every change is a proposal with its rule; the product owner decides; the record says why |
| Gaming through feedback text | Text cannot change anything; screening is a tripwire, counting people is the control |
