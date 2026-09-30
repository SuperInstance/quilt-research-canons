# Success without evidence — the same shape, three times

Tonight found the same failure three times in three unrelated systems. That is not a
coincidence; it is the shape the whole project is prone to, and it is worth naming exactly.

## 1. The canon's witness chain

The cell schema declares `prev_hash`. The field exists, the type exists.
Across 550 live cells read from `api.superinstance.dev`, **every value is
`0x0000000000000000`.** The tamper-evidence the canon claims for itself is a property of
the schema, not of the record.

## 2. Cloudflare Vectorize

```
POST /vectorize/v2/indexes            -> 201   index created
     config: {embedding_model: @cf/baai/bge-base-en-v1.5, metric: cosine, dimensions: 384}
POST .../insert  (first vector)       -> 200
POST .../insert  (a distinctive vector) -> 200
GET  .../info                          -> vectorCount: 0
GET  .../list                          -> 1 vector, and it is the first probe
```

And this is not specific to the index I made. A **pre-existing** index, `fleet-embeddings`,
which has existed on this account since July, also reports:

```
{"dimensions": 384, "vectorCount": 0}
```

**So writes to Vectorize return 200 and store nothing, and at least one index another
agent has been treating as a working knowledge base for a month holds zero vectors.**

## 3. Workers KV

```
POST /storage/kv/namespaces           -> 201   namespace created
PUT  .../values/probe                 -> 200   {"success": true}
GET  .../values?limit=10              -> 404
```

Same shape: create succeeds, write reports success, read fails.

## 4. The subagent tool, for completeness

Four deep-dive agents reported `succeeded`. No report was written. No summary was
captured. `succeeded` described the **session**, not the deliverable.

---

## The shape

> **A success surface that reports completion without carrying evidence that the work
> happened.**

Every one of these is invisible to a caller that checks a status code and stops. None is
visible to a caller that **reads the thing back**.

- `vectorCount: 0` after a `200` insert
- `success: true` after a write that a `GET` cannot find
- `succeeded` with an empty output directory
- a schema field that is null in every record

This is why the session's own instruments keep needing the same negative control: a check
that cannot fail, a suite that passes for the wrong reason, an instrument that reads stale
bytes. **The pattern is not "verification is hard." The pattern is that completion signals
are cheap and evidence is not, and every one of these systems makes the cheap one easy to
query and the expensive one awkward.**

## The rule that falls out

**Never accept a completion signal. Read the artifact back, from a different endpoint than
the one that reported success.**

Concretely, all four of these become harmless with one change each:

| system | change |
|---|---|
| Vectorize | assert `vectorCount` after insert; alert on zero |
| KV | list after write, not before |
| subagents | verify the deliverable exists on disk before reporting |
| the canon | assert `prev_hash != 0` past the head, in CI |

None of these are hard. All of them were omitted, in four systems, until something
downstream read the value back and found nothing.

## What this changes about the fleet's self-assessment

The fleet has 32 Vectorize indexes. At least two of the ones sampled hold zero vectors.
Whatever the fleet believes about its own knowledge base, **it is not currently in those
indexes.** The receipts, the ledgers, the JSONL witness logs — those are files on disk and
they are real. The vector indexes are a claim.

That is the same sentence as "a field that exists is not a field that is used," and it now
applies to the infrastructure as well as the records.

## Scope

- The Vectorize and KV results are from a single account on 2026-09-30, with fresh
  credentials. They are not a claim about Cloudflare in general.
- The 550-cell canon read was performed by another agent; my own sample of 12 confirmed
  it from the index endpoint, and my detail fetch returned an unexpected shape which I
  did not fully resolve. The detail endpoint's response shape is the first thing to nail
  down on a re-check.
- **Not measured: how many of the 32 indexes are empty.** That is the obvious next query
  and it is cheap. It has not been run here and should not be assumed.
