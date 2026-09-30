# Success without evidence — CORRECTED 2026-09-30T01:00Z

**The first version of this file got the doctrine right and one of its four examples
wrong. The wrong one was mine, and it was the one I was most confident about.**

## What I wrote, and why it was wrong

I reported:

> Cloudflare Vectorize `insert` returns **200** and `info` still reads **`vectorCount: 0`**.
> **So writes to Vectorize return 200 and store nothing.**

That is false. Vectorize is **eventually consistent on reads**, and I read too early.
The decisive test, run after the fact:

```
insert a distinct vector  -> 200 accepted
  t+ 0s   count=4   list=[probe, PROBE-VECTOR-0001, v1, p1]
  t+ 5s   count=4   list=[probe, PROBE-VECTOR-0001, v1, p1]
  t+15s   count=5   list=[CONSISTENCY-PROBE-9, probe, ...]     <- appeared here
  t+30s   count=5
```

Read-after-write lags by roughly **5 to 15 seconds**. The write was never lost. The
platform was not lying. **My instrument was.**

## The census that followed, and what it actually shows

```
31 Vectorize indexes on the account
  12 EMPTY (0 vectors)   39%
  19 holding data        up to 52,324 vectors (fleet-twin)
```

That looks like a smoking gun for silent data loss. It is not. Sorting by creation
date, **emptiness interleaves with fullness across the entire nine-month timeline**:

```
2026-01-14    3   claudes-friend-index     <- full
2026-01-18    7   agent-context-index      <- full
2026-01-22    0   makerlog-conversations   <- empty
2026-06-09 1541   fleet-crates             <- full
2026-06-12    0   superinstance-knowledge  <- empty
2026-06-15  603   crab-trap-lures          <- full
2026-06-15    0   shoal-vectors            <- empty
```

If the API had been dropping writes, the empty ones would cluster at the end. They do
not. **The honest reading is that those 12 indexes were simply never populated** — a
repo that indexes nothing and an index whose writes were dropped look identical from
the outside, and I could not tell them apart with a single read.

## What the KV example is worth now — downgraded, not deleted

I also reported: KV `PUT` returns `{"success": true}` and `GET ?limit=10` returns 404.
**I never re-read that after a delay, so I cannot claim it.** It may be the same
eventual-consistency shape, or a different endpoint contract, or a real gap. It is
recorded as unresolved rather than as a finding. Reporting it as a finding would be
the same error one level up.

## The corrected doctrine — sharper than what it replaced

> **A single read-back cannot distinguish "the system failed" from "you read too early."**

The first version said *never accept a completion signal, always read the artifact back.*
That was right and incomplete. The rule that actually survives is:

**A read-back supports a claim about system behaviour only if it is REPEATED, or taken
through a DIFFERENT endpoint, or made after the system's own consistency window.**
One read tells you what was true at that instant. It does not tell you what the system
does.

This is not a smaller claim than the original. It is a sharper one, and it has a
consequence the original missed: **an instrument that reads once will confidently
report a platform bug that does not exist, and the more confident the platform
behaviour, the more damage that does.**

## The examples that survive

| system | claim | status |
|---|---|---|
| canon `prev_hash` | null in all 550 cells | **stands** — a 550-sample census, not a single read |
| subagent `succeeded` | empty output directory | **stands** — filesystem, not a distributed index |
| Vectorize insert | "returns 200 and stores nothing" | **RETRACTED** — eventually consistent, ~5-15s |
| KV write | "success:true with GET 404" | **DOWNGRADED** — never re-read after a delay |

## Why this happened at all

I had a strong prior — the session's theme was "success without evidence" — and I
found a measurement that fit it perfectly. **A theory that explains everything will
explain the first number that arrives, and the first number is usually the instrument
describing itself.**

The tell was available and I did not use it: I wrote at the time that a *pre-existing*
index, `fleet-embeddings`, also read zero. I treated that as corroboration. It was not
corroboration — it was the same class of observation, and it had the same alternative
explanation I never tested.
