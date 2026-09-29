# Five users, run at this frontend

The problem this solves: every second reader in this fleet has been me reading my own work
twice. The sow loop added a second MODEL, which is better and is still the same substrate.
A different ROLE is a different substrate in the way that matters — a stranger does not
share my priors about what is obvious, and that is exactly where my work is weakest.

## The five

| user | wants | will not forgive |
|---|---|---|
| **stranger** | to know in 90s whether any of this is real, and check it themselves | a claim I cannot verify in the time they have |
| **skipper** | to know whether the edge cases in the demo are the ones that matter at 4am in a swell | a synthetic scene standing in for a real one |
| **skeptic** | to find the thing that is overclaimed | a number from one run, or a claim that moves when the gate moves |
| **maintainer** | to know what breaks, what is safe to delete, what the next person inherits | an undocumented invariant |
| **agent** | a machine-checkable surface, a licence, an error mode | a human-only interface, an unauthenticated mutation endpoint |

## What each one actually said

**stranger** — *the first 90 seconds are spent on a table, not on a claim.* The page opens
on nine cells of boat state. Nothing says what the thing IS or that it can be checked.
There is no one-sentence claim, no "here is what to run", no answer to "how do I check the
check". **The landing page I shipped earlier answers this; this page does not.** That is a
real gap between two artifacts I built today and I did not notice until asked.

**skipper** — *the failure is missing and the demo is too clean.* The ice reads "moderate,
rising" and the temp reads "7.1 C" and neither has a threshold, a trend, or a consequence.
At 4am "is the ice getting worse" is the only question that matters and the cell answers
with a string. There is no "this cell is about to gate something" anywhere. **The
relationships are edges, and no edge is marked as load-bearing.**

**skeptic** — *which number came from one run?* The frames are a hand-authored sequence.
Every receipt is real (sha256 over addr+value) but the *history* is a story I wrote, not a
measurement. The receipt proves a value was set; it does not prove the boat did that.
**The page invites a reading it cannot support**, and the header should say so.

**maintainer** — *what breaks silently.* Nothing: there is no server, no auth, no network,
no dependency. That is a virtue for a design probe and a hazard for a deployment, and the
page does not say which it is. There is no schema version a caller can depend on, no
migration note, no statement of what is load-bearing in the model.

**agent** — *no licence, no rate limit, no retry contract in the file.* The agent payload
declares an error shape and three codes, which is more than most, but it is a
static artefact with no way to call it. There is no `version`, and a consumer has no way to
tell a schema change from a data change.

## The two things I am changing because of this

1. **The `note` field stops being a caption and becomes a claim.** Every cell states what it
   would take for the value to be wrong. A string like "0.3 m, rising" becomes
   "0.3 m, rising — crossing 0.5 m closes the north berth". That is the difference between
   a display and a cell, and it is the difference the skipper and the skeptic both asked
   for in different words.
2. **The header states what kind of thing this is.** A probe, with a hand-authored history,
   no auth, no server. The skeptic's objection is not fixed by better numbers; it is fixed
   by saying out loud that the numbers are a story with real receipts attached.

## What I am not changing

The two-view structure survives all five. It is the thing none of them attacked, and the
agent explicitly asked for exactly the surface it provides. The rewind survives, because the
maintainer needs to know what changes when and the skeptic needs to see the same cell
across time. And the receipts survive, because that is what the stranger uses instead of
trusting me.
