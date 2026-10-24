# Team brief: feedback-to-roadmap

One page for the people who take this from v0.1 to a pilot with three product owners. Read this
first; everything else is linked.

## Mission

Every internal AI assistant's next cycle is planned from what its users actually struggle with,
counted in people, with every override written down, and the people who told us hear back.

## Where we are

v0.1 works end to end on synthetic data: feedback in, evidence and an explained proposal out, the
product owner's decisions applied to a new roadmap version
([worked example](../product/07-worked-example.md)). Seventeen stories are Done and proved by tests in
CI. What we do **not** know: whether real product owners trust the proposals (H3), and what
hand-coding costs on real phrasing (H4). The held-out measure says the codebook alone will not be
enough: precision 0.69, recall 0.24.

## What done looks like for PI 2 (three iterations of two weeks, then the pilot cycles)

1. The coding spot-check (US-18) is live before the first pilot cycle.
2. Segment-weighted reach and the translated pulse survey template (US-20).
3. Model-assisted coding (US-19) evaluated against its gate; switched on only if it passes.
4. Three product owners run their first cycle; every pack, decision and coding time is logged.

## Constraints that are not up for debate in this phase

- **The tool proposes; a product owner decides** (D2). No feature changes a roadmap without `apply` by
  a product owner. The sequence test stays green.
- **Impact and effort are never changed by the tool** (D2).
- **People, not rows; flagged items count zero** (D1).
- **Personal data is redacted at intake.** Anything touching identifiers or the export format goes past the DPO.
- **No model call ships without its gold gate and a recording CI replays** (D5).
- **No new runtime dependencies** without a decision-log entry.

## Team and decision rights

| Role | Who (planned) | Owns |
|---|---|---|
| Product owner | Flavio | Problem, priorities (RICE), backlog order, pilot design, story acceptance |
| Tech lead / engineer | to be named | Architecture, code quality, estimates, release |
| Engineer (60%) | to be named | Stories, tests, gold-set tooling |
| User researcher (30%) | to be named | Codebook, gold-set coding with a second coder, pulse survey, interviews |
| Pilot product owners | three, from the tracker's portfolio | Run cycles, log time, say what they did not trust |
| Head of the AI centre of excellence | sponsor | Pilot selection, go / no-go with the product owner |
| DPO | reviewer | Redaction, identifiers, exports |

### RACI for the decisions that come up most

| Decision | Product owner | Tech lead | Engineers | Researcher | Sponsor | DPO |
|---|---|---|---|---|---|---|
| Backlog order and RICE scores | A/R | C | C | C | C | I |
| Change to a scoring threshold or tier | A/R | C | I | C | I | - |
| Change to the codebook | A | I | I | R | - | - |
| Switch on model-assisted coding | A | R | R | C (gold set) | I | C |
| Change to redaction or identifiers | R | C | R | I | I | A |
| Release to the pilot | A | R | R | C | C | I |
| Go / iterate / stop after the pilot | R | C | I | C | A | C |

## Where things are

Product case: [docs/product](../product/). Backlog: [backlog.csv](backlog.csv). Plan:
[iteration-plan.md](iteration-plan.md). Ways of working: [working-agreement.md](working-agreement.md).
Proof of Done: [traceability.md](traceability.md). Operating model: [OPERATIONS.md](../../OPERATIONS.md).
