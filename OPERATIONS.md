# Operations: sample operating model for the pilot

Designed for a pilot with three product owners; operated so far as a prototype on synthetic data.
Thresholds below are the plan, not measurements.

## 1. Release gate (ticked before each release to the pilot)

- [ ] CI green: tests on Python 3.10 and 3.12, `tools/trace.py` (every Done story has a test), the worked example, scrub check
- [ ] Regression set passes: every must-pass case in [evals/EVALS.md](evals/EVALS.md), including the 4,096-sequence decision test
- [ ] Any change to `config/codebook.json` measured on both gold sets, numbers updated in EVALS.md
- [ ] Any change to `config/scoring.json` or `config/team.json` recorded in the CHANGELOG and, if it changes a rule, the decision log
- [ ] DPO consulted if redaction, identifiers or the export format changed
- [ ] Before the first pilot release only: the coding spot-check (US-18) is live; roles come from single sign-on groups, not the sample roster; packs live where only the product owner can edit them
- [ ] Previous release tag kept; pilot product owners told what changed, in two lines

A release that fails any line does not go out.

## 2. Rollout

Three product owners, three review cycles each (about three months). Success metrics and decision
rules are fixed in [05-metrics-and-pilot.md](docs/product/05-metrics-and-pilot.md) before launch:
go when H2 and H3 hold with coding under 30 minutes per 100 items; iterate between 30 and 60; stop if
the pack shows nothing new in two of three cycles, or on any guardrail breach.

## 3. Monitoring

| Signal | Source | Frequency | Alert when |
|---|---|---|---|
| Cycles completed | pack.json (applied), usage events | per cycle | a product owner skips a cycle |
| Time to decision | product owner's log | per cycle | over 2 hours for about 150 items |
| Hand-coding cost | product owner's log | per cycle | over 30 minutes per 100 items |
| Acceptance | pack.json | per cycle | under 70% accepted, or a rejection with no reason the evidence could not see |
| Spot-check corrections (from US-18) | pack.json | per cycle | more than 1 in 5 sampled tags corrected |
| Screening flags | flagged list, reviewed by the product owner | per cycle | any flag judged a real attempt (incident); false positives over 20% of flags |
| Unauthorised changes | roadmap versions vs applied packs | per cycle and in CI | any (cannot happen; if seen, kill switch) |
| Personal data in outputs | CI test; DPO spot check of one pack per month | every push, monthly | any |

There is no telemetry beyond the packs and usage events (the tool is a local command in v0.1).
Format of the per-cycle log: [ops/sample-monitoring-log.csv](ops/sample-monitoring-log.csv) (invented values).

## 4. Feedback into tests

Every confirmed problem (a wrong tag that moved a score, a quote that misrepresented a person, a flag
that should not have fired, a change nobody could understand) becomes a test named after its story,
failing, before the fix is merged. Misread phrasings join the next held-out gold set, never the codebook directly.

## 5. Change and drift

Re-run the regression set and the worked example when: the codebook, scoring file or roster changes;
the export format of any channel changes; a new channel is added. Re-measure the codebook on a fresh
held-out set every quarter: phrasing drifts with the assistant. Roll back to the previous tag if a
must-pass case regresses and the fix is not ready the same day.

## 6. Incident runbook

| Incident | Detected by | Contain | Tell | Follow-up |
|---|---|---|---|---|
| A wrong tag or estimate moved an item and the decision was relied on | spot-check, team or sponsor challenge | re-run the review with the correction as a manual code; the product owner re-decides; the next roadmap version supersedes | sponsor, delivery team | failing test; gold-set item; CHANGELOG line |
| Roadmap changed without a product owner's apply | per-cycle check (should be impossible) | **kill switch**: stop using the tool; restore the last applied version | sponsor, head of the AI centre | root cause before restart; new sequence test |
| Personal data in a pack, record or notify list | CI, DPO spot check | delete the outputs; re-run after the redaction fix | DPO the same day | pattern added to the redaction tests |
| Real attempt to rig the ranking through feedback | flag reviewed by the product owner | item stays excluded | sponsor | pattern added to the eval set |

## 7. Ownership and retirement

Owner: product owner. Backup: tech lead. Review every three months with the head of the AI centre of
excellence. Retire if the pilot hits a kill criterion, if no product owner runs a cycle for two
consecutive months, or if the organisation's feedback platform does the same job with the same
controls: tell the product owners, archive the repository with its last test run.
