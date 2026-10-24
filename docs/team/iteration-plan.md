# Iteration plan

Planning assumption: two engineers (one at 60%), a part-time researcher, two-week iterations,
about 12 points per iteration (a guess until three iterations of real velocity exist). Iterations 1
to 4 are the MVP in this repository: planned as iterations so scope and estimates can be inspected,
but **built by one person for this portfolio**, so the velocity is not evidence about a team.

## PI 1 (MVP)

### Iteration 1 - "all the feedback, safely, coded" (Done)

| Story | Points | Result |
|---|---|---|
| US-01 Read every channel; stop on malformed rows | 3 | Done |
| US-02 Redact personal data at intake | 2 | Done |
| US-03 Feedback is data, never instructions | 2 | Done |
| US-04 Codebook and manual codes | 3 | Done |
| US-05 Uncoded queue and new-theme candidates | 2 | Done |
| **Total** | **12** | |

Demo: an export with an email address and an injection attempt comes out redacted, flagged and coded.

### Iteration 2 - "people, not rows" (Done)

| Story | Points | Result |
|---|---|---|
| US-06 Evidence per theme and tier | 3 | Done |
| US-07 Verbatim quotes | 2 | Done |
| US-08 Who we are not hearing from | 2 | Done |
| US-09 Spikes go to support | 1 | Done |
| **Total** | **8** | |

Demo: the sponsor sees 15 rows about outdated content become 11 people, and Poland's silence.

### Iteration 3 - "a proposal the product owner can check in seconds" (Done)

| Story | Points | Result |
|---|---|---|
| US-10 Proposed changes with rules | 5 | Done |
| US-11 Opinion-only items and gaps | 2 | Done |
| US-12 Ranking and cut line | 2 | Done |
| US-13 Only the product owner decides | 3 | Done |
| **Total** | **12** | |

Demo: the product owner rejects one change with a note and pins one item; nobody else can.

### Iteration 4 - "the next roadmap, and who to tell" (Done)

| Story | Points | Result |
|---|---|---|
| US-14 Apply writes a new version | 3 | Done |
| US-15 Pack, decision record, people to tell | 3 | Done |
| US-16 Measure the codebook on gold sets | 2 | Done |
| US-17 Usage events for the tracker | 1 | Done |
| **Total** | **9** | |

Demo: the worked example end to end; the held-out measure (0.69 / 0.24) and what it changes.

Retrospective note: the held-out measure came last and changed the plan (US-18 added, first in PI 2).
Next time, the gold set is written in iteration 1, before the codebook.

## PI 2 (pilot increment)

| Iteration | Goal | Stories | Points |
|---|---|---|---|
| 5 | "catch wrong tags, shrink the queue" | US-18 spot-check (3), US-19 model coding behind a gate (8) | 11 |
| 6 | "hear the silent, close the loop" | US-20 pulse survey and segment-weighted reach (5), US-22 tell people when it ships (3) | 8 |
| Pilot | three product owners, three cycles each | measurement only; every problem becomes a story with a failing test | - |
| 7 (Later) | "less copy and paste, more experiments" | US-21 connectors (8), US-23 assumption tests (5) | 13 |
