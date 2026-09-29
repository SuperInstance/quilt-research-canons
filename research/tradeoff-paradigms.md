---
title: Everything is a plugin, and every plugin taxes another paradigm
date: 2026-09-29
subject: why the specs have to name their cost, and who is actually paying
---

## The observation

Every thing in this fleet is optimal inside one value system and expensive outside it. That
is not a flaw in any of them. **It is what a plugin IS: a local optimum that becomes a
global cost somewhere you were not looking.**

The failure is not having trade-offs. It is having them **unstated**. A spec that names only
what it maximises reads as though it has no cost — and the cost then lands somewhere nobody
was measuring, usually in a different agent's paradigm, weeks later, attributed to
something else.

So the rule is narrow and checkable:

> **A spec that does not name the paradigm it TAXES is not finished.**

That is a completeness gate, not a quality gate. It does not tell you which plugin to use.
It tells you that a spec claiming no cost is a spec whose cost is *unlocated*.

---

## The eight paradigms, and what each is structurally blind to

`blind_to` matters more than `measures`. A paradigm that measured everything would not be
a paradigm.

| paradigm | measures | structurally cannot see |
|---|---|---|
| **Transport** | bits per frame, cells per wire | that a cancelled cell and a correctly-predicted cell cost the SAME, so cancellation buys nothing the predictor has not already bought |
| **Fidelity** | reconstruction error vs source | that the source may not be the thing worth reconstructing |
| **Durability** | what survives the next wipe | that a survivor nobody can reach is a liability, not an asset |
| **Auditability** | claims with a traceable receipt | that recording every hop is exactly wrong on a hot path |
| **Calibration** | predicted prob vs realised freq | that an instrument which cannot discriminate still returns a confident number, and the confidence is not a property of the answer |
| **Legibility** | can a stranger use this unaided | that legibility by removing substance is indistinguishable from legibility by adding it |
| **Locality** | latency to a local answer | that a subgraph optimised alone can be net-negative for the whole |
| **Sheddability** | how cheaply a component is abandoned | that a system where everything is sheddable has nothing to rely on |

## The ledger: nine real plugins, none hypothetical

Each is the obvious choice inside its own paradigm. That is what makes them plugins rather
than mistakes.

| plugin | optimises | taxes | the unpaid cost |
|---|---|---|---|
| `qpixl-residual` | Transport | Fidelity, Calibration | a cancelled cell and a correctly-*predicted* cell cost the same, so a matcher that finds the wrong correspondence looks 67 points cheaper than the truth and nothing notices |
| `glyphcast-pyramid` | Transport | Fidelity | a pyramid says **how much** to spend; it cannot say **which way** to describe a cell, so a cell cheap to describe wrongly is described wrongly at full cost |
| `reef-coral` | Durability | Locality, Sheddability | a dead agent's work persists and keeps costing attention — persistence without reachability is a liability |
| `active-ledger` | Auditability | Locality, Transport | recording every hop is precisely wrong on a hot path; a design probe, not a service, and the cost is unpaid because nothing runs on it yet |
| `jev-gate` | Calibration | Legibility | `score` returns a near-constant at confident-looking confidence, so any score-based gate is decorative |
| `two-views` | Legibility | Durability | the two views are generated together, so improving one degrades the other unless both regenerate — and there is no such step to forget |
| `molt-shells` | Sheddability | Durability | correct per-component, wrong as an architecture |
| `chiaroscuro-ramp` | Fidelity | Transport, Legibility | intensity carries nothing below the ramp step while colour does, so a matcher keyed on the coarser channel under-charges |
| `two-readers` | Auditability | Transport | three checks this session found their own bugs *by agreeing*, so disagreements are rarer than the agreement rate suggests and the true error rate is higher than measured |

---

## THE FINDING: the load is not circular

```
paradigm         optimises  taxed   net
Transport                2      3    -2  ##
Locality                 0      2    -2  ##
Durability               1      2    -1  #
Legibility               1      2    -1  #
Fidelity                 1      2    -1  #
Calibration              1      1    +0
Sheddability             1      1    +0
Auditability             2      0    +1  #
```

Two lines carry this whole thing:

**Locality is optimised by ZERO plugins and taxed by two.** Nothing in this fleet is built
to be local, fast, and dependent on nothing — and two things actively charge for it. The
reef persists so things outlive their process; the ledger records so things can be
audited. Both are right. Both bill locality. And the paradigm that would push back is the
one with nobody standing in it.

**Auditability is the only net winner (+1).** The fleet has systematically decided that
receipts cost nothing. They do — until someone asks what it costs to hold a receipt.

The ledger only says something *because the load is asymmetric*. A ledger where every
paradigm both optimised and paid equally would be a diagram of good manners and would
predict nothing. **The observation is worth making only because Transport and Locality are
net losers, and because nobody noticed until the costs were written down.**

## The gate

`ledger.py` is a completeness check with a negative control: a `Plugin` with no declared
tax **fails** `complete()`, so the gate can be shown to fail. Leg 3 proves it.

`self_test.py` — **10/10**, including two negative controls that the positive legs are not
vacuous:

- a tax on a paradigm that does not exist is caught
- a self-taxing plugin is rejected (a plugin may not charge its own paradigm)
- **a self-consistent circular ledger produces no net payers and the asymmetry check
  FAILS** — this is the one that matters, because it proves the finding is a measurement
  rather than an artefact of the bookkeeping

## What this changes about the specs

Every roadmap, README, and design doc in this fleet is currently a *paradigm declaration
wearing a plan's clothes*. Adding three lines — `optimises:`, `taxes:`, `unmitigated:` —
turns a recommendation into something a later reader can argue with, which is the only
form of a recommendation that survives the author being wrong.

**The next spec to be written should fail its own gate until it names what it costs.**
