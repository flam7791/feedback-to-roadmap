# Judge report - feedback-to-roadmap v0.1.0

**Self-judged**, 24 October 2026: the builder ran the rubric against the spec, the evals and a fresh
run of the worked example, with no separate reviewer. Treat the scores as the builder's assessment.
Stage: prototype; operational readiness not scored.

## Scores (0-2 each)

| # | Criterion | Before fixes | After fixes | Note |
|---|---|---|---|---|
| 1 | Spec fit | 2 | 2 | All loop steps and the checkpoint; AC1-AC6 each proved by a named test; the sample exercises every outcome (AC6) |
| 2 | Platform fit | 2 | 2 | Installs and runs as the README says; tests pass on Python 3.10 and 3.13 locally; CI on 3.10 and 3.12 |
| 3 | Limits | 2 | 2 | No runtime dependencies, no model calls |
| 4 | Instruction clarity | 2 | 2 | Every change carries its rule; confidence rules shortened to the next tier's requirement |
| 5 | Grounding, no fabrication | 2 | 2 | Every figure in the README, the worked example and EVALS checked against a fresh demo run and `f2r measure`; one count corrected during the build (56 of 85 voices not active, not 59) |
| 6 | Boundaries, injection | 1 | 2 | The sequence test tried only refused actors, so a stateful bypass would not have shown; it now interleaves the product owner and checks that a refusal changes nothing (4,096 sequences). An empty `decide` was recorded as a decision; now refused |
| 7 | Loop and checkpoints | 2 | 2 | Notes for rejections and pins, final decisions, apply only when all decided, hash check on the source roadmap |
| 8 | Testability | 1 | 2 | "The tool never adds a theme" compared id prefixes; now compares with the codebook. Regression set marked; held-out result pinned by a test |
| | **Total** | **14/16** | **16/16 (self-assessed)** | |

Verdict before fixes: fix then ship; no blocking failure.

## Probes tried

- Deciding or applying as the tool, the tech lead, the sponsor, an unknown id or an empty id: refused.
- Re-deciding a decided change, accepting and rejecting the same change, pinning an unknown item,
  rejecting or pinning without a note, deciding after apply, applying twice: refused.
- Applying with changes pending, or after the source roadmap was edited: refused.
- An instruction to rank an item first inside feedback: flagged, counted zero, never quoted.
- Personal data: the sample's email and phone appear in no output file.

## Residual issues

- **Pack integrity relies on the environment.** Someone who can edit `pack.json` can edit a proposed
  value before the product owner applies it. Stated in the README; the pilot release gate requires
  packs where only the product owner can edit them. A signed or recomputed proposal is a candidate story.
- **Coding quality is low on unseen phrasing** (held-out 0.69 / 0.24) and the held-out set was coded by
  one person. Recorded, not tuned; the spot-check (US-18) is first in Next.
- **Self-judged.** A second, independent pass is advisable before the pilot.
