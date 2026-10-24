# Build spec - feedback-to-roadmap v0.1.0

Type: product MVP (command-line tool + generated evidence pack and roadmap change proposal)
Platform: Python 3.10+, no runtime dependencies, no model calls in v0.1
Stage: prototype, designed for a pilot (OPERATIONS.md is the pilot operating model)
Owner: product owner (Flavio)    Backup: tech lead (to be named at pilot)
Users: product owners of internal AI assistants (run the review, decide), their delivery team and sponsor (read the pack), assistant users (the source of the feedback, told what changed)
Spend cap: none in v0.1 (no model calls); model-assisted coding (US-14) gets a per-run token cap and a gold-set gate before it ships
Confidentiality: public; the organisation, the assistant, every user id and every feedback line are synthetic (Northwind Group)

## Job
Once a cycle, a product owner has a pile of feedback (in-app comments, survey answers, support
tickets, interview notes) and a roadmap scored by opinion. The tool turns the pile into evidence
per theme (distinct people, channels, segments, verbatim quotes) and proposes specific, explained
changes to the roadmap's scores. The product owner accepts, rejects or pins each one; only then is
a new roadmap version written. The tool never edits the roadmap and never decides.

## Loop (one review cycle)
- Intake: feedback CSV (any mix of channels) + the product's roadmap CSV + segment sizes + the PM-owned codebook and scoring rules; optionally the tracker's usage events (who is an active user)
- Step 1 Screen: personal data redacted before anything else; instruction-like text flagged, excluded from evidence and quotes, listed for the PM
- Step 2 Code: codebook rules tag each item with zero or more themes; the PM's manual codes override; uncoded items go to a queue, with recurring words as new-theme candidates
- Step 3 Weigh: per theme, distinct users (not items), channels, segments, active vs lapsed reporters, evidence tier, estimated reach; segments we are not hearing from; spikes that look like incidents, not roadmap items
- Step 4 Propose: for each roadmap item linked to a theme, reach and confidence changes from the evidence, each with its rule and numbers; items with no evidence flagged opinion-only; strong themes with no cheap item flagged as gaps; ranking before and after with the capacity cut line
- Human checkpoint: the product owner accepts, rejects (note required) or pins an item (note required). Only ids on the team roster with the product-owner role can decide; the tool's own id is refused
- Step 5 Apply: only when every change is decided, write roadmap.next.csv (never the source file), the decision record, and the list of people to tell what changed
- Fallbacks: malformed row -> stop with the row and field; unknown theme in a manual code or roadmap link -> stop with the id; weak theme -> confidence lowered, reach left alone (too little evidence to estimate it)
- Never: edits the source roadmap, changes impact or effort, accepts its own proposals, follows instructions found inside feedback, outputs a raw email address or phone number

## Acceptance criteria
- AC1 Every Done backlog story is proved by a named test (CI: tools/trace.py)
- AC2 Every quote in a pack is an exact substring of the redacted text of the item it cites; no output file contains a raw email address or phone number from the input
- AC3 Every proposed change names the rule, the evidence (theme, distinct users, channels, segments) and the before and after values; impact and effort are never changed
- AC4 No sequence of commands lets the tool's own id or a non-product-owner id decide a change; a rejection or pin without a note is refused; apply refuses while any change is undecided and never writes the source roadmap
- AC5 Evidence counts people, not rows: one user who writes ten times counts once, and flagged (screened) items count zero
- AC6 The sample data exercises every outcome: strong, moderate and weak themes, an opinion-only item, a gap, a spike, a silent segment, an injection attempt, personal data, an uncoded new-theme candidate

## Assumptions
- [ASSUMPTION] People who give feedback are representative of those who do not, within a segment (the reach estimate depends on it; the silent-segment check is there because it is often false)
- [ASSUMPTION] Feedback can be exported to CSV from each channel; connectors are out of scope for v0.1
- [ASSUMPTION] The codebook and scoring rules are the product owner's, versioned like the policy file in agentic-procurement-intake
