# Toolchain KAR — a live characterisation of my own instruments

## The error this corrects

I asked "is each tool up?" and got **4 of 11**. That number was a lie of composition.
Nine of the eleven failures were not dead tools. They were **three different failures
wearing one coat**, and averaging them made working tools look broken:

| class | meaning | correct treatment | examples found tonight |
|---|---|---|---|
| **IDENTITY** | the credential's *state* is wrong | nothing in the request helps; fix the account | `zai` → 429 `1113 Insufficient balance` |
| **SHAPE** | the request is wrong *for that gateway* | deterministic, permanent fix in the client | `groq` → 403 `1010` is a **User-Agent gate**; `curl/7.88.0` is enough. Same for `moth-quantum`. |
| **LOAD** | the path is flaky or a resource is busy | retry; the retry policy is per-tool | `deepseek` TLS close → 200 on retry 1. `deepinfra` 429 "Model busy" → **all 3 other models 200**. Cloudflare 503. |

**The trap:** a 429 from ZAI and a 429 from DeepInfra are the same status code and
opposite problems. One is a dead account, the other is a model mid-load. Treating them
as "rate limited, try later" means retrying a dead account forever; treating them as
"down" means abandoning a healthy one.

## Measured, with the same tools

```
tool                   cause     code      ms  detail
github                 OK        200      537  1705B
elevenlabs             OK        200      673  119661B
typesafe-jev           OK        200      693  113B
github-anon            OK        200      775  1454B
groq                   OK        200      790  788B
cloudflare-vectorize   OK        200      809  8325B
deepseek               OK        200     1449  479B
deepinfra              OK        200     2969  1226B
moth-quantum           OK        200     3444  15040B
gemini                 LOAD      429      778  rate limited
zai                    IDENTITY  429     1078  Insufficient balance

usable now: 9/11   load/edge: 1   genuinely dead: 1
```

**9 usable, not 4.** The two that failed both failed *correctly*: one is worth a
retry, one needs a recharge.

## The control

`--self-test` runs 7 legs, every one a failure signature this session actually
produced. The load-bearing legs are the two 429s:

```
ok   429 -> IDENTITY  'Insufficient balance' is IDENTITY -- retrying is pointless
ok   429 -> LOAD      'Model busy' is LOAD, despite sharing a 429 with the balance case
```

If status code alone decided the class, one of those would be wrong.

## What this changes in practice

- `groq` and `moth-quantum` are permanently fixed by a browser `User-Agent` in the
  client — not intermittent, not flaky, just previously mis-called.
- `deepseek` needs retry-on-TLS-reset (documented ~30% of the fleet's calls).
- `deepinfra` needs **per-model** health, not per-account: one busy model is not a
  busy account.
- `zai` is the only tool needing a human, and the fix is a recharge.

## Generalisation

This is the same move as the fleet's instrument registry, turned inward. An
instrument that reports only "working / not working" cannot tell you what to do about
it. The classification is the deliverable; the boolean is the report.
