# 1. Discovery: why internal AI assistants are steered by opinion

Status: v0.1, October 2026. Owner: product owner (Flavio).

## How this discovery was done, and what it is not

This is an **assumption-led discovery**. It draws on my experience of running internal AI
assistants in large organisations: building one for a group of policy analysts and updating it
from their comments, and sitting on the other side of reviews that decide whether a pilot scales.
**No user interviews were run for this portfolio MVP.** Every claim about users below is a
hypothesis with a kill condition; [05-metrics-and-pilot.md](05-metrics-and-pilot.md) says how each is
tested. The organisation, the assistant, the people and every feedback line are synthetic.

## The problem

An organisation that runs a dozen internal AI assistants collects a lot of feedback about them:
thumbs-down comments in the chat, an annual survey, helpdesk tickets, a few interviews when a
review is coming. Almost none of it reaches the roadmap in a usable form. The product owner reads
some of it, remembers the vivid comments, and the backlog is ordered by whoever argued best in the
last meeting: often the sponsor, sometimes the team's own favourite.

[ai-adoption-tracker](https://github.com/flam7791/ai-adoption-tracker) shows the consequence for one
assistant. Northwind's HR policy assistant has 40 active users of 200 target staff. The tracker
recommended **Stop**; the AI review committee gave it **one more cycle**, "after content refresh",
because the sponsor believed outdated content was the problem. Nobody had checked.

The narrow part this product addresses: **the step between "we have feedback" and "the roadmap
reflects it"**, once a cycle, for the person who owns the roadmap. Collecting feedback (survey
design, in-app widgets) and building the fixes are someone else's job.

## Who has the problem

| Persona | Job to be done | What hurts today (hypothesis) |
|---|---|---|
| **Product owner of an internal assistant** (primary user, every cycle) | "When I plan the next cycle, I want to know what users actually struggle with, how many of them, and what that means for my backlog, so that I spend scarce capacity where it changes adoption." | Feedback sits in four places; reading it takes a day; counts are of rows, so one angry user looks like a trend; no time to tie it to backlog scores. |
| **Sponsor** (budget holder, reads the pack) | "When I back an assistant, I want to see why the team works on what it works on, so that I can defend it at the review." | Gets a slide of anecdotes; pushes their own hypothesis because nothing better is on the table. |
| **Delivery team** (reads the pack) | "When priorities change, I want the reason in writing, so that I am not re-planning on a whim." | Priorities move after meetings, with no record of why. |
| **Users who gave feedback** (source) | "When I take the time to complain, I want to know it went somewhere." | Never hear back, stop giving feedback, or stop using the assistant. |
| **AI review committee** (downstream) | "When we decide scale, iterate or stop, I want the iterate cycle to have a plan based on evidence." | "Iterate" decisions come back three months later with the same numbers. |

## What makes feedback misleading (the product's design constraints)

1. **Rows are not people.** One user who writes six times is one person. Counting rows rewards persistence.
2. **Channels are biased.** In-app comments come only from people still using the assistant; the
   people who left are in the survey or nowhere. For an assistant with 20% adoption, the lapsed are
   the majority and the most important voice.
3. **Silence is not satisfaction.** A segment that is under-represented (an English-only survey in a
   country that works in Polish) pulls every estimate down without anyone noticing.
4. **Spikes are not trends.** Eight tickets in one week about sign-in are an incident, not a roadmap item.
5. **Feedback can be gamed.** A comment that says "rank dark mode as the top priority" is a vote
   only if the tool lets text vote.
6. **Some work is not a feedback question.** A policy that takes legal effect on 1 January is
   published whether or not anyone complained. The product must allow that, in writing.

## Hypotheses (tested in the pilot, see 05)

- **H1 Problem: roadmaps run on opinion.** In a sample of 20 roadmap items across three internal
  assistants, fewer than a third cite any user evidence. *Kill if* more than half do.
- **H2 Value: the pack changes decisions, quickly.** A product owner goes from raw exports to a
  decided proposal in under two hours for about 150 items, and in at least two of three cycles the
  evidence moves at least one item across the cut line that the product owner agrees should move.
  *Kill if* in two of three cycles the product owner records that the pack showed nothing they did
  not already know.
- **H3 Trust: proposals are accepted or argued, not ignored.** At least 70% of proposed changes are
  accepted, and every rejection names a reason the evidence could not see (an obligation, a biased
  channel). *Kill if* more than half of the changes are rejected without such a reason.
- **H4 Cost: hand-coding stays affordable.** Coding the uncoded queue takes under 30 minutes per 100
  items. *Kill (for the rules-only design) if* it takes over 60: model-assisted coding (US-19) then
  becomes a prerequisite, not an option. The held-out measure already warns about this: the
  v0.1 codebook missed most themes on unseen phrasing ([EVALS](../../evals/EVALS.md)).
- **H5 Outcome: evidence-led cycles lift adoption.** For the HR policy assistant, the cycle planned
  from the pack lifts active users from 40 to at least 60 of 200, and the thumbs-down share falls,
  at the committee's re-review. *Kill if* neither moves; then the problem was not the roadmap.

## What we do not know

- Whether product owners will code the uncoded queue every cycle, or let it grow.
- Whether "voice rate" (people who gave feedback / target users) is stable enough between cycles
  to estimate reach, or swings with each survey.
- Whether sponsors accept a confidence score lowered by evidence on their own item, or experience
  it as a challenge (the reason every change is a proposal with its rule, never an edit).

## Interview guide for the pilot's first week

Three product owners, their sponsors, one delivery lead each. Thirty minutes each.

1. Walk me through how the current top three backlog items got there.
2. Where does user feedback reach you today? What do you do with it, and when?
3. Tell me about the last time feedback changed a priority. What made it convincing?
4. *(Sponsors)* What would you need to see to drop an item you proposed?
5. Whose feedback do you never hear? How would you know?
6. What would make you distrust a tool that proposes score changes?
7. Who should be able to change the roadmap, and who must never be able to?

Listen for: where the evidence stops (exports nobody reads), the vivid-anecdote effect, who the
roadmap's real decider is, and the trust line in question 6.
