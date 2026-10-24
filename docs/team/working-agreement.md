# Working agreement

## Definition of Ready (a story can enter an iteration when)

- It has a user, a need and a reason ("As a ... I want ... so that ...").
- Its acceptance criteria are observable: a reviewer can check each one without asking the author.
- It names the hypothesis or finding it serves (H1 to H5, a pilot finding, an incident).
- Dependencies outside the team are resolved or named with an owner and a date (for example, the
  DPO's sign-off on a change to identifiers).
- It is estimated, and it fits in one iteration (8 points or fewer; split otherwise).

## Definition of Done (a story is Done when)

- Every acceptance criterion is met and the product owner has accepted it at the demo.
- At least one test named `test_<STORY>_...` proves it; `python tools/trace.py` passes. CI enforces this.
- CI is green: tests on Python 3.10 and 3.12, traceability, the worked example, the scrub check.
- Any changed rule, tier or threshold is updated in the PRD or the decision log in the same PR.
- Any codebook change re-runs `f2r measure` on both gold sets and updates the numbers in `evals/EVALS.md`.
- The CHANGELOG has a line for anything a user would notice.

## Rituals

| Ritual | When | Who | Output |
|---|---|---|---|
| Iteration planning | Monday, week 1, 60 min | Team | Iteration goal (one sentence) and committed stories |
| Stand-up | Daily, 15 min | Team | Blockers named with an owner |
| Backlog refinement | Wednesday, week 2, 45 min | Product owner, tech lead, researcher | Next iteration's stories Ready, RICE refreshed |
| Demo | Friday, week 2, 30 min | Team plus a pilot product owner | Accepted / not accepted per story; feedback as new backlog items (run through the tool itself) |
| Retrospective | Friday, week 2, 30 min | Team | One change to try next iteration |

The team's own feedback from demos goes through `f2r review` like any assistant's: the product is
held to its own rule.

## Pull requests

- Small: one story or less per PR. The title starts with the story id (`US-18: ...`).
- One reviewer from the team; the DPO as well if redaction, identifiers or the export format change.
- The PR template's checklist is the Definition of Done.

## Disagreements

Decisions about *what* and *in which order* are the product owner's; about *how* the tech lead's. If
either is challenged, write the disagreement as a decision-log entry with both options; the
accountable person decides within two working days and the entry records why.
