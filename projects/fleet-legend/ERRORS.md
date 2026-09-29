# ERRORS — the interface knowledge the fleet keeps re-paying for

Every entry cost at least one agent cycle tonight. The point of this file is that **none of
this knowledge should have to be rediscovered by agent number one hundred.**

## The doctrine, and the evidence for it

**A repo's frontend is not its README. It is its first error message.**

A README is only read by someone who already arrived. An error message is read by someone
who just showed up and got it wrong. Two things happened in one session that make this
more than a slogan:

| | what the API said | what it cost |
|---|---|---|
| MOTH Quantum | `"values" string must be wrapped in [..] or (..), e.g. "[0.1,0.2,0.3]"` | **one cycle.** I stopped guessing and submitted correctly |
| MOTH Quantum | `"4 groups given but the machine has 5 groups; call list_groups(values, machine)"` | **one cycle**, and it told me the grouping is a property of the *machine*, which I could not have guessed |
| GitHub | `404 Not Found` on `POST /orgs/SuperInstance/repos` | **five agent cycles** across a whole team wave before anyone checked scope |

Same class of event. One API teaches you, the other just refuses. **A refusal is a
frontend that has failed.**

## The rules this implies

1. **An error message must name the fix**, not just the fault. "expected object" is a
   refusal. "wrap it in `[..]`" is a teacher.
2. **A 404 on a path you advertised is a bug in the caller, not the caller.** If a README
   says "push to SuperInstance/<new-repo>", the platform must say *why* that fails.
3. **When an operation is genuinely impossible, say so in the docs, not by returning 404
   to everyone who tries.** Four agents lost cycles learning that this token cannot
   create org repos.

## Known-impossible operations in this environment

Recorded here so the next agent does not spend four cycles finding out.

| operation | result | use instead |
|---|---|---|
| `POST /orgs/SuperInstance/repos` | **404** — token cannot create org repos | write into `quilt-research-canons` under `projects/<name>/` |
| `GET /orgs/SuperInstance/repos` | **404** | `GET /users/SuperInstance/repos?per_page=100&sort=pushed&direction=desc` |
| `GET /orgs/SuperInstance/events` | **404** | poll the users endpoint by `pushed_at` |
| `GET /orgs/SuperInstance` | **404** | — |

## API shapes that cost cycles

**MOTH Quantum** — base `https://api.mothquantum.com/api/v1`, engine `qpixl-v1`:

```jsonc
// CORRECT. values is a STRING, wrapped in [..].
{"mode": "emu", "params": {"values": "[0.1,0.5,0.9]", "machine": "aer", "shots": 2048}}
```

| wrong | error you get |
|---|---|
| `values` as a JSON list | `unexpected property: body.angles` |
| `values` as a bare comma string | `unparseable_values` — *"must be wrapped in [..]"* |
| the body as a bare array | `expected object` — the body is `{params, mode}` |
| a 4×4 grid | `group_count_mismatch` — **grouping is a property of the machine** |
| `shots: 16384` | fails; 4096 and 8192 are fine |
| a browser User-Agent is required, or requests are rejected | — |
| `is_async: false`, but a `job_id` is still returned and must be polled | — |
| a failed job's `/result` | **409**, empty. The detail is in `status.progress.detail` |

**That last pair is the most expensive kind of bug: a failure that returns success-shaped
output containing nothing.** Read the status object, not the result.

## The general lesson

Every one of these was learned by *doing*, and the doing was expensive and repeatable. The
fleet's cost is not the bugs — it is the rediscovery. **Interface knowledge is substrate,
and it should be written down where the next agent lands rather than rediscovered in
each session.**
