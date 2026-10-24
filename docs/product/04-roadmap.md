# 4. Roadmap: Now, Next, Later

Status: v0.1, October 2026. Owner: product owner. Ordering: [03-prioritisation.md](03-prioritisation.md).

## Now: v0.1 (done, this repository)

The loop end to end on synthetic data: feedback in, evidence per theme, proposed changes with
rules, the product owner's decisions, the next roadmap version, the people to tell. 17 stories,
each proved by a test in CI.

**Exit condition:** a product owner of a real internal assistant agrees to run a pilot cycle with it.

## Next: PI 2, the pilot increment (three iterations)

| Order | Story | Why now |
|---|---|---|
| 1 | US-18 Coding spot-check before deciding | Held-out precision 0.69: wrong tags must be caught before they move a score |
| 2 | US-20 Translated pulse survey, segment-weighted reach | The worked example's one rejection; the reach estimate's main assumption |
| 3 | US-19 Model-assisted coding behind a gold gate | Held-out recall 0.24: the uncoded queue is the cost H4 measures |
| 4 | US-22 Tell people when it ships | Closing the loop is what keeps feedback coming |

PI 2 objectives:

- **Committed:** three product owners each run three review cycles; every cycle's pack, decisions and
  hand-coding time are logged; the go / iterate / stop call is taken on the rules in
  [05-metrics-and-pilot.md](05-metrics-and-pilot.md).
- **Committed:** the spot-check is live before the first pilot cycle.
- **Uncommitted:** model-assisted coding passes its gate on a gold set of at least 150 items coded by
  two people, with their agreement measured first.

## Later

- **US-21 Connectors** to the in-app comments, ticketing and survey exports, once H2 and H4 hold.
- **US-23 Assumption tests** in the opportunity tree: the cheapest experiment that would raise or
  kill a weak opportunity, feeding confidence.
- **Portfolio view**: every assistant's themes and decisions beside its ai-adoption-tracker gates,
  so an "iterate" decision arrives at the committee with the plan the evidence supports.

## Kill criteria (any one stops the product)

- H2 fails: in two of three cycles, product owners record that the pack showed nothing new.
- H4 fails and model coding does not pass its gate: the coding cost is higher than the value.
- Any roadmap change is found that was not decided by a product owner (should be impossible; tested
  on every push), or any personal data is found in an output: stop, investigate, restart only with
  the cause fixed and a test added.
