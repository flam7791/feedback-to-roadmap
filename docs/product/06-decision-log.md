# 6. Product decision log

One entry per decision that someone could reasonably question later. Newest last.

### D1 - Count people, not rows (Oct 2026)
**Context.** Feedback exports are rows; the obvious count is rows per theme.
**Decision.** Every measure of evidence counts distinct users. Flagged (screened) items count zero.
**Why.** In the sample, one user wrote about outdated content six times: 15 rows, 11 people. Rows reward
persistence and channels with repeat contact (tickets). The roadmap is about how many people a fix helps.

### D2 - The tool proposes; the product owner decides; only reach and confidence move (Oct 2026)
**Context.** The tool could re-rank the roadmap directly.
**Decision.** It writes a proposal. Each change is accepted or rejected (with a note) by a product owner
on the roster. Impact and effort are never touched: impact is a judgement about value, effort is the
team's estimate, and feedback says nothing reliable about either.
**Why.** A roadmap is a set of commitments to people. A tool that edits it is a tool someone will learn
to game, and a sponsor will learn to resent. The proposal format also makes every disagreement visible.

### D3 - Confidence comes from evidence tiers, as a house rule (Oct 2026)
**Context.** In RICE, confidence is usually a gut percentage.
**Decision.** Confidence is set from the evidence tier of the item's themes: strong 0.8, moderate 0.5,
weak 0.3, no evidence 0.2, thresholds in `config/scoring.json`.
**Trade-off.** Confidence in RICE also covers confidence in impact and effort, which feedback cannot see.
The product owner can reject the change; the note then records what the evidence missed.
**Revisit when.** Pilot rejections show a pattern (e.g. technical risk dominating confidence).

### D4 - Reach = people / voice rate, and say what it assumes (Oct 2026)
**Context.** Feedback gives a floor on how many people a problem affects, not an estimate.
**Decision.** Estimated reach = people who reported the theme / (people who gave any feedback / target
users). Changes are proposed only for strong and moderate themes, and only above a 25% difference.
**Assumption, written down.** People who give feedback represent those who do not. Often false; the
silent-segment flag is there to catch where it is most false. Segment-weighted reach (US-20) is the fix.
**In the worked example.** The product owner rejected the reach cut for "answer in the user's language"
for exactly this reason: the survey was English-only and Poland was almost silent.

### D5 - Rules-first coding in v0.1; a model must pass a gold gate (Oct 2026)
**Context.** Theme coding is the textbook use of a language model.
**Decision.** v0.1 codes with keyword rules the product owner owns, manual codes override, and misses go
to a queue. A model may later propose themes from the closed list, each with an exact supporting span,
switched on only at held-out precision 0.90 and recall 0.70 (US-19).
**Measured.** On 48 held-out items written after the codebook was frozen: precision 0.69, recall 0.24.
**Not patched.** Tuning the codebook on the held-out set would make the number meaningless. The result
is recorded, pinned by a test, and changed the plan: the coding spot-check (US-18) is first in Next.
**Why rules first anyway.** Reproducible results, a tag that can always be traced to its keyword, and a
baseline any model has to beat. The portfolio's earlier lesson: closed answer sets and checks in code
did the work, not a model's confidence.

### D6 - Pins exist, cost a note, and are shown (Oct 2026)
**Context.** Some work is not a feedback question: a policy that takes legal effect on a fixed date.
**Decision.** A product owner can pin an item above the cut line, with a note. Pins take capacity first,
appear in the ranking and the decision record, and cannot be added without a reason.
**Why.** Without pins, obligations get smuggled in by inflating scores, which corrupts every other
comparison. With pins, the override is explicit and its cost (what fell below the line) is visible.

### D7 - A new roadmap version, never an overwrite (Oct 2026)
**Decision.** `apply` writes `roadmap.next.csv`; the source is never written. If the source changed
since the review (hash check), apply refuses: the proposal no longer matches the roadmap.
**Why.** The roadmap's history is the record of what was promised when. Two people editing a roadmap
while a proposal is pending is the normal case, not an edge case.

### D8 - Spikes go to support (Oct 2026)
**Decision.** A theme with most of its items in one week is flagged as a likely incident, and is not
reported as a roadmap gap.
**Why.** Eight sign-in tickets in one week are an outage. Putting them on the roadmap delays the fix.

### D9 - The same assistant as ai-adoption-tracker, the same event format (Oct 2026)
**Decision.** The sample is Northwind's HR policy assistant (UC03): the 40 active users are the
tracker's user ids, the committee's "iterate" decision is the starting point, and the tool emits its own
usage in the tracker's event format.
**Why.** The portfolio's products form one loop: the tracker decides scale, iterate or stop; this tool
plans the iterate cycle; its own use is measured by the tracker.

### D10 - Draft the message, never send it (Oct 2026)
**Decision.** `apply` writes the list of people who reported what is now above the cut, and a draft
message that promises only what is planned. Sending is a person's job.
**Why.** Telling people their feedback mattered is what keeps it coming, and a message about plans is a
commitment that only the product owner can make.
