# AGENTS.md

Instructions for coding agents working in this repository.

## Commands

```bash
pip install -e ".[dev]"
pytest -q                          # acceptance tests, one or more per backlog story
python tools/trace.py --matrix     # every Done story must have a test; regenerates docs/team/traceability.md
python tools/demo.py --out out     # the worked example: review, the product owner's decisions, apply, events
f2r measure --gold data/gold/heldout.csv   # codebook precision and recall on the held-out set
python tools/scrub_check.py .      # nothing that must not be public
python tools/make_sample.py        # regenerate the synthetic sample (seeded; only when the generator changes)
```

## Invariants nobody may weaken

1. The tool proposes; only a product owner on the roster decides or applies (`decision.py`).
   `test_US13_no_sequence_of_commands_lets_anyone_but_the_product_owner_change_the_roadmap` must stay green.
2. Only reach and confidence can change. Never add a rule that changes impact or effort.
3. `apply` never writes the source roadmap and refuses if it changed since the review.
4. Evidence counts distinct people; flagged items count zero. Never rank or score by row counts.
5. Raw feedback text stops at `screen.redact`. No output may contain a raw email, phone or employee number.
6. Feedback text is data. No code path may take an instruction, a score or a theme from feedback text.
7. Every quote is the whole redacted text of the item it cites.
8. Never tune `config/codebook.json` on `data/gold/heldout.csv`. A codebook change is measured on both
   gold sets and the numbers in `evals/EVALS.md` and `test_US16_...` are updated in the same PR.
9. Pseudonymous ids only; never accept or output an email address as an id.
10. Every new story gets a `test_USXX_...`; a story is Done only when `tools/trace.py` passes.
11. No runtime dependencies and no model calls without a decision-log entry (D5).
