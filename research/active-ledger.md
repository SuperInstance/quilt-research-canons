---
title: The ActiveLedger — a routing book that is a tensor, and a filter that is a cell
date: 2026-09-29
code: research/active-ledger/active_ledger.py
selftest: 12/12, including four negative controls
---

A proof of concept for the routing idea, in about 350 lines of dependency-free Python.

## The claim

A cell's ActiveLedger is not a database. It is a **double-entry book**: every hop from one
cell's ledger to another's is recorded on both sides, in each book-keeper's own units, with
the translation between those units written down. **The routing code IS the translation
table.**

Two cells measuring the same quantity differently is not an error. It is the normal case.
The ledger's job is to say what "the same" means, per edge, per context.

## Why a tensor and not a graph

Planes only intersect. They need not be orthogonal and they need not share a
parameterisation. A cell is "in" a plane in the operational sense — it is running that
way — while its ledger entries land in several planes, because a measurement taken in one
context is legible in others.

A vibration is heat to one cell, silence to another, and **both entries are correct**,
because the listener's units are defined by the application it is perceiving *for*.

```
A hull is vibrating at 47 Hz. Three cells perceive it.

  plane structural   (load-bearing reading, for the engineer)
    reading -> FAULT: 47 Hz resonance inside the 45-55 Hz band
    ledger  -> 47 hull-sensor:hz [in-contact]

  plane acoustic     (speech-band reading, for the STT route)
    reading -> nothing — below the 300 Hz speech floor
    ledger  -> 0 hull-sensor:hz [in-contact]

  plane comfort      (passenger-experience reading)
    reading -> low-frequency vibration, below the reporting threshold
    ledger  -> 47 hull-sensor:hz [in-contact]
```

A grep for "47" finds the number. It does **not** find that two of the three cells
consider the event absent. The ActiveLedger does, because the entry carries the plane, and
the plane carries the purpose, and the purpose is what makes a reading a reading.

## The filter is a cell, not a step

The route from a hull microphone to an LLM goes: `mic -> pre-stt-filter -> stt ->
grammar-cleanup -> pincher -> llm-cell`.

The pre-STT filter is a real cell. Its job is to recognise what is obviously not speech and
suppress it, which lowers the STT's load and therefore its model requirements, because it
has had a first pass. Being a cell means:

- its decision is **posted to the same ledger** as everything it gates, so a filter
  failure is a visible entry rather than a quality drop you can only taste;
- a **blocked signal sends nothing across the gate at all** — not a zero. "The STT was
  never called" and "the STT was called and returned nothing" are completely different
  failures and the ledger has to be able to tell them apart;
- its verdict is a **reading in words with a confidence**, not an embedding distance:
  `noise, 0.94, below 300 Hz, no speech-band energy`.

## What a human reads

```
ActiveLedger — pre-stt-filter
entries: 12   balanced: True
  plane              to               quantity            value     unit
  pre-stt-gate       stt              gate-decision       1.0000    pre-stt-filter:passed
  pre-stt-gate       pre-stt-filter   gate-confidence     0.9400    pre-stt-filter:fraction

  pre-STT gate — what the filter decided, in words:
    pre-stt-filter  noise   conf=0.94  through=False  below 300 Hz, no speech-band energy
```

The arithmetic that produced the 0.94 is not shown, and should not be. Internally the cell
may be doing a matrix multiply; what is valuable to the observer is the words. You zoom in
for maintenance and you get the workings; you do not have to, and by default you do not.

## The anti-GAN note

This is deliberately a **second route** to double-entry semantics, not the first. SQL
transactions, event sourcing, and T-accounts all reach the same place. Route diversity is
the point: a system that can only get somewhere one way is brittle in a way that does not
announce itself. The preferred route is a function of the state, and the state is the
tensor.

## Four bugs this found in itself

Every one was found by a **negative control** — a test that has to fail when the law is
broken:

1. **A unit meant nothing without its context.** `translate()` short-circuited on
   `frm.owner == to_owner` *before* checking the condition, so a conversion declared valid
   only in water applied in air without complaint. The same class of error as a wrong
   number: it looks right.
2. **A gate that posted to a hardcoded cell name.** `filter_verdict` posted to the literal
   `"stt-cell"`, so in any pipeline whose STT node was named something else the gate
   posted into a cell that did not exist.
3. **The route was always empty.** `Route.add()` guarded with
   `if self.hops and self.hops[-1] != cell`, which is false on an empty list — so the
   first hop was never appended and every later one compared against an empty tail.
   Silent, total, and it made the positive self-test legs pass **for the wrong reason**:
   nothing was ever posted, so "the block worked" and "the post never happened" looked
   identical.
4. **A book that recorded only what it posted.** The receiving cell's ledger stayed empty
   until the receiver posted something itself, so the synoptic view of a downstream cell
   said nothing about the signal that made it run. Fixed: every post lands in **both**
   books. That is what double-entry actually means — the same fact in two books, not once
   in the sender's and never in the receiver's.

Bug 3 is the one worth naming. It passed eleven tests. It was caught only because a
negative control was written that the thing would have to survive.

## Fail-closed receipts

| injected fault | caught by |
|---|---|
| gate always passes (blocked signal leaks to the STT) | `a filter that blocks sends NOTHING across the gate` |
| planes merged (the tensor collapses to a graph) | `entries are separated by plane, not merged` |
| route drops the first hop again | two legs, both failing loudly |

## The projection is the interface

A grep sees one flattened projection and cannot know which plane it lost. The ledger is
queryable by any 2D slice, and the slice is a *choice* — structural, acoustic, comfort —
not an accident of the storage format. That is the difference between an interface and a
convenience.

```sh
python3 active_ledger.py --self-test
python3 active_ledger.py --demo
```

No dependencies. 350 lines. Every law has a negative control.
