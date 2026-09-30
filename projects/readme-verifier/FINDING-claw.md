# `claw` — the README's three SuperInstance mechanisms, verified

*Checked 2026-09-30. Scope is stated below and is narrower than the claim it tests.*

## What the README says

```
 37  ### Ternary Routing (SuperInstance Extension)
 44  The ratios of these classifications feed directly into the γ + η = C conservation
     framework. When γ_drift is detected (too many avoids), the rout...
 53  | Ternary classification | $O(1)$ per message (threshold comparison) |
137  conservation:  # SuperInstance extension
145  claw is the **cellular logic engine** of the SuperInstance fleet ...
```

So there IS a named section, a named config key, and a named formula. This is not a
misreading of a README.

## Filename search — exhaustive over 7,445 files

| term | files matching |
|---|---|
| `ternary` | **0** |
| `conservation` | **0** |
| `gamma` | **0** |
| `quilt` | **0** |
| `superinstance` | **0** |
| `drift` | 2 — `src/cli/daemon-cli/gateway-token-drift{,.test}.ts` |
| `cocapn` | 3 — `skills/cocapn-fleet/{SKILL.md, scripts/claw_fleet_bridge.py, scripts/test_claw_fleet_bridge.py}` |

Two of those need naming rather than counting.

**`drift` is a name collision, not the mechanism.** The file is
`gateway-token-drift.ts` — *gateway token* drift, a credential-mismatch detector.
`γ_drift` in the README is a proportion of avoided classifications, used to steer
routing. The word matches; the thing does not. Worse, that path **404s on the default
branch**, so even the colliding file is not where the README would find it.

**`cocapn` is real, and its direction is the reverse of the README's framing.** Three
files, and the bridge is named `claw_fleet_bridge.py` — a SuperInstance surface
*exposed to* Claw. The README presents claw as extending into the fleet; the code has
the fleet served to claw.

## Content search — bounded, and this is the honest limit

Filename absence is suggestive; a real implementation could be inside a generically
named file. So I also read the most plausible homes — `src/gateway/**`, `src/agents/**`,
`src/infra/**`, and anything matching `*router*.ts` — **26 files**:

```
scanned 26 candidate files
zero content hits for ternary / conservation / gamma in the routing cores
```

## Verdict, and what is NOT established

**SUPPORTED:** no file in the tree is *named* for any of the three claimed mechanisms,
and no file in the routing cores *mentions* them.

**NOT ESTABLISHED:** I did not content-search the remaining ~7,400 files. A prior scout
reported doing so; I have not verified that, and I am not going to repeat a number I
cannot re-derive. **The strongest honest statement is: no filename and no routing-core
file supports the claims, and a full content sweep is the check that would settle it.**

The cheap, high-value next step is not another search — it is **one line in the README
pointing at the file that implements each mechanism, or removing the section.** A
mechanism claimed in prose and absent from the tree costs the next reader an hour and
costs this repo the ability to be believed about the things it *does* implement.

## The unrelated thing worth keeping

`claw` is a 7,445-file fork of [openclaw/openclaw] and it is a real, substantial
multi-channel gateway. Nothing here says the fork is bad. It says three sentences of
its README are not backed by the tree — and that is a much smaller problem than the one
it creates, which is a reader's trust in everything else the README asserts.
