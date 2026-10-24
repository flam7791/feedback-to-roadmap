# 3. Prioritisation: what went into v0.1, and what waits

Status: v0.1, October 2026. Owner: product owner. Method: RICE, the same scoring the tool applies to
the roadmaps it reviews, so the product is held to its own rule.

## Scoring scale

- **Reach**: product owners of internal assistants who would use it per quarter. Northwind's
  portfolio in ai-adoption-tracker has 12 assistants at any time; 12 is "all of them".
- **Impact**: 3 = changes what gets built; 2 = changes how confidently; 1 = saves time; 0.5 = nice to have.
- **Confidence**: 1.0 measured, 0.8 strong reasoned case, 0.5 plausible, 0.3 a hunch. Assumption-led
  discovery caps most items at 0.8 (no interviews yet).
- **Effort**: story points (one point is roughly half a day for one person).

## Ranking

| Feature (stories) | Reach | Impact | Confidence | Effort | RICE | v0.1? |
|---|---|---|---|---|---|---|
| F6 Usage events for the tracker (US-17) | 12 | 0.5 | 1.0 | 1 | 6.0 | **yes** |
| F3 People, not rows: evidence, quotes, silent segments, spikes (US-06 to 09) | 12 | 3 | 0.8 | 8 | 3.6 | **yes** |
| F2 Codebook, uncoded queue, gold-set measure (US-04, 05, 16) | 12 | 2 | 0.8 | 7 | 2.74 | **yes** |
| F5 Decide, apply, decision record, people to tell (US-13 to 15) | 12 | 2 | 0.8 | 9 | 2.13 | **yes** |
| F4 Proposed changes with rules, ranking and cut line (US-10 to 12) | 12 | 3 | 0.5 | 9 | 2.0 | **yes** |
| F1 Intake, redaction, screening (US-01 to 03) | 12 | 1 | 1.0 | 7 | 1.71 | **yes** |
| *cut line: 41 points, four iterations* | | | | | | |
| Coding spot-check before deciding (US-18) | 12 | 1 | 0.8 | 3 | 3.2 | Next, first |
| Model-assisted coding behind a gold gate (US-19) | 12 | 2 | 0.5 | 8 | 1.5 | Next |
| Connectors to the channel exports (US-21) | 12 | 1 | 0.8 | 8 | 1.2 | Later |
| Tell people when it ships (US-22) | 12 | 0.5 | 0.5 | 3 | 1.0 | Next |
| Assumption tests in the opportunity tree (US-23) | 12 | 1 | 0.3 | 5 | 0.72 | Later |
| Translated pulse survey, segment-weighted reach (US-20) | 6 | 1 | 0.5 | 5 | 0.6 | Next (pulled up, see below) |
| Portfolio view across assistants | 1 | 2 | 0.5 | 8 | 0.13 | Later |

## The calls worth explaining

**The MVP is a slice through the whole loop, not the top of the RICE list.** F1 and F4 score lower
than the spot-check, but without intake there is no input and without proposals there is nothing to
decide. RICE orders the work inside the slice and everything after it; it does not choose the slice.

**The spot-check was not in the original plan.** It was added after the held-out measure
(precision 0.69: about one tag in three wrong on phrasing the codebook had not seen). It scores
highest of the remaining work and is the first story of the next increment. The measure changed the
plan, which is what a measure is for.

**Model-assisted coding is the obvious "AI feature" and is deliberately not in v0.1.** Confidence
0.5: the portfolio's earlier measurements found that a model's stated confidence carried no
information and that closed answer sets plus checks in code did the work. It gets built, behind a
gate: closed theme list, an exact supporting span, and held-out precision of at least 0.90 before
it is switched on (D5).

**Segment-weighted reach is pulled up despite RICE 0.6.** Its reach is half the portfolio (the
assistants with multilingual users), but it is the fix for the one rejection in the worked example
and for the assumption every reach estimate rests on (D4). A low score on a correctness fix is a
reason to keep it small, not to drop it.

**Connectors wait.** Every channel already exports CSV. Connectors bring identity mapping and a data
protection review per channel; they are worth it once H2 and H4 hold, not before.
