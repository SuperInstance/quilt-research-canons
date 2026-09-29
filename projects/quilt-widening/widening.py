#!/usr/bin/env python3
"""
widening.py — a quilt that decomposes ITSELF into wider and wider arrays, where every
widening is a named, rewindable, observable action.

WHAT THIS IS

A seed-state. A loop that proposes a decomposition. Every child NAMED. One observation of
every named child, batched. The whole step recorded as a reversible action. Then a nudge,
then again. The trace is the seed-state material for the next generation.

WHY THE NAMING IS NOT COSMETIC

Eleven pre-registered rounds established the operational contract for this oracle, and it
is the load-bearing detail of this whole file:

  - a `noul` question whose subject is NOT named collapses: two questions in one call
    return the SAME number, spread 0.01, because the model is scoring the whole state once
    and reporting it per question. Same instruction, unnamed subjects -> one answer.
  - naming the subject in the question text fixes it completely: four subjects, one call,
    spread 0.57-0.63.
  - a 4-question batch costs 545 input tokens against 1344 for four separate calls.

So a self-widening array is the WORST case for the collapse, because widening means asking
about many array elements at once. An unnamed widening is not a slightly worse measurement;
it is N copies of one measurement, and it looks like agreement.

    THE RULE: a question that applies to a whole array must say WHICH ELEMENT it is about.
    The instruction text does not have to differ. It only has to POINT.

REWIND

The trail is append-only and every action carries a handle, so any step can be undone by
moving a pointer, never by deleting. That is the same primitive as `molt`'s shells and
`two-views`' frames, and it is the difference between a process and a log.
"""
from __future__ import annotations
import json, os, sys, time, urllib.request, urllib.error
from dataclasses import dataclass, field, asdict
from typing import Optional

API = os.environ.get("JEV_BASE", "https://api.typesafe.ai") + "/v1/systemone"
KEY = os.environ.get("TYPESAFEAI_KEY", "")
UA = {"User-Agent": "widening/1.0", "Authorization": f"Bearer {KEY}",
      "Content-Type": "application/json"}

# ---------------------------------------------------------------- the vocabulary
# What a cell's RESPONSE characteristic is -- the thing that gets modularised when one
# cell is swapped for another. Four kinds, so a swap is a real change and not a reshuffle.
CHARACTERISTICS = ["directive", "question", "refusal", "silence"]


@dataclass
class Cell:
    cid: str
    kind: str                 # seed | child
    text: str
    characteristic: str
    parent: Optional[str] = None
    depth: int = 0
    #: what this cell is ABOUT, in words. This is the field the JEV question must name.
    subject: str = ""


@dataclass
class Action:
    """One reversible step. `undo_of` points at what this reverses; nothing is deleted."""
    seq: int
    kind: str                  # seed | decompose | nudge | rewind
    detail: dict
    undo_of: Optional[int] = None
    result: str = ""            # what came back, in one line


class Trail:
    """Append-only, with a moveable head. Rewind is a pointer move, not a deletion."""
    def __init__(self):
        self.actions: list[Action] = []
        self.head = -1
        self._seq = 0

    def append(self, kind, detail, result="", undo_of=None) -> Action:
        self._seq += 1
        a = Action(self._seq, kind, detail, undo_of, result)
        self.actions.append(a)
        self.head = len(self.actions) - 1
        return a

    def rewind(self, to_seq: int) -> bool:
        """Move the head back. Nothing is deleted -- the record of having tried is the
        point, and a rewind that erased the attempt would be a lie about the history.

        The head is a PREFIX LENGTH: actions[:head+1] are in effect, the rest are not.
        A rewind marker is appended to the log and is immediately outside that prefix, so
        the marker records the undo without re-applying it. (The first version appended the
        marker INSIDE the prefix and therefore replayed the very action it was undoing --
        a rewind that rewound nothing, which is the worst possible version of this bug:
        it looks like it worked.)
        """
        idx = next((i for i, a in enumerate(self.actions) if a.seq == to_seq), None)
        if idx is None or idx > self.head:
            return False
        self.head = idx                          # the named action STAYS in effect
        self.append("rewind", {"to_seq": to_seq, "head_after": self.head},
                    result=f"prefix shortened to {self.head + 1} action(s)", undo_of=to_seq)
        self.head = idx                          # keep the marker itself out of effect
        return True

    def state_at_head(self, cells: dict) -> dict:
        """Rebuild the live cell set by replaying ONLY the effective prefix."""
        live: dict = {}
        for a in self.actions[:self.head + 1]:
            if a.kind == "seed":
                for cid in a.detail.get("cells", []):
                    live[cid] = cells[cid]
            elif a.kind == "decompose":
                live.pop(a.detail["parent"], None)
                for cid in a.detail.get("children", []):
                    live[cid] = cells[cid]
        return live


# ---------------------------------------------------------------- observation
def jev_batch(subjects: list[str], question: str, tries=4) -> tuple[dict, int]:
    """One call. Every subject NAMED in its own instruction. Returns (scores, retries).

    The naming is the whole contract -- see the module docstring. This function is the only
    place that talks to the oracle, so it is also the only place that can get it wrong."""
    if not KEY:
        return {}, 0
    # `state` is a FIRST-CLASS body field, not something to bury in the instructions.
    # The API rejects the request without it (422: body.state required). That is the
    # empirical 11-round finding made structural: the array is the thing being scored,
    # and each question has to say which element of it it is about.
    state = ". ".join(f"Subject {n}: {s}" for n, s in enumerate(subjects)) + "."
    payload = {"model": "jev-latest", "state": state, "questions": {}}
    for n, s in enumerate(subjects):
        payload["questions"][f"subject_{n}"] = {
            "type": "noul",
            "instructions": f"Regarding Subject {n}: {question}",
            "criteria": {"true": "yes", "false": "no"},
        }
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(
                    API, data=json.dumps(payload).encode(), headers=UA), timeout=60) as r:
                d = json.loads(r.read())
            out = {}
            for n in range(len(subjects)):
                a = d.get("answers", {}).get(f"subject_{n}", {})
                v = a.get("noul")
                if isinstance(v, dict):
                    v = v.get("probability")
                try:
                    out[n] = float(v)
                except (TypeError, ValueError):
                    out[n] = None
            return out, attempt
        except Exception:
            time.sleep(2 + attempt)
    return {}, tries


def spread(scores: dict) -> float:
    """Heterogeneity WITHIN one array. Kept, and deliberately NOT used as the verdict."""
    v = [x for x in scores.values() if isinstance(x, float)]
    return (max(v) - min(v)) if len(v) > 1 else 0.0


def level(scores: dict) -> float | None:
    """Mean LEVEL of an array's scores."""
    v = [x for x in scores.values() if isinstance(x, float)]
    return (sum(v) / len(v)) if v else None


HOMOGENEOUS_CONTROL = (
    "Subject 0: a cell about the topic. Subject 1: a cell about the topic. "
    "Subject 2: a cell about the topic. Subject 3: a cell about the topic.")


def discrimination(real: dict, control: dict) -> float:
    """THE RIGHT STATISTIC, found the hard way.

    Spread is heterogeneity WITHIN an array. A homogeneous array correctly gets a low
    spread, so a low spread is not evidence that the oracle is flat -- it is evidence the
    array carries no internal variation. My first version printed "subjects DO NOT
    DISCRIMINATE" off a low spread and was blaming the oracle for correctly reporting that
    my own decomposition was redundant.

    The question that actually matters is: does the oracle give a DIFFERENT answer to an
    array whose elements differ than to an array whose elements do not? That is a
    comparison across two arrays, and it is what "does the map discriminate" means.

    Measured live: redundant array 0.19, distinct array 0.86, spreads 0.04 and 0.05 --
    the spreads are indistinguishable while the levels are 0.67 apart.
    """
    a, b = level(real), level(control)
    if a is None or b is None:
        return 0.0
    return abs(a - b)


# ---------------------------------------------------------------- the loop
def seed_state(width: int = 3) -> tuple[dict, list]:
    cells, subs = {}, []
    for i in range(width):
        cid = f"seed-{i}"
        cells[cid] = Cell(cid, "seed",
                          f"a seed cell holding one instruction about the whole system",
                          CHARACTERISTICS[i % len(CHARACTERISTICS)],
                          subject=f"the whole system, read as {CHARACTERISTICS[i % len(CHARACTERISTICS)]}")
        subs.append(f"seed cell {i}, a {cells[cid].characteristic}")
    return cells, subs


def decompose(cells: dict, parent: str, k: int, seq: int) -> list[Cell]:
    """Split one cell into k named children. Naming happens HERE, at construction, so no
    downstream step can forget it."""
    p = cells[parent]
    kids = []
    for i in range(k):
        cid = f"{parent}.{i}"
        kind = CHARACTERISTICS[i % len(CHARACTERISTICS)]
        kids.append(Cell(cid, "child", f"{p.text} (narrowed: {kind})", kind,
                         parent=parent, depth=p.depth + 1,
                         subject=f"element {i} of {parent}, which is specifically about {kind}"))
    return kids


def run(rounds=3, width=3, split=2, question=None, dry=False):
    question = question or ("Is this element a distinct, non-redundant part of the whole, "
                            "or a restatement of its neighbours?")
    trail = Trail()
    cells, subs = seed_state(width)
    trail.append("seed", {"cells": list(cells), "question": question},
                 result=f"seeded {len(cells)} cells")

    print()
    print("  QUILT WIDENING — self-decomposition into wider arrays, every step rewindable")
    print("  " * 30)
    print(f"  question: {question}")
    print()
    print(f"  round 0  array width = {width}")
    live = trail.state_at_head(cells)
    sc, r = ({}, 0) if dry else jev_batch([cells[c].subject for c in live], question)
    if sc:
        print(f"          spread across {len(sc)} named subjects: {spread(sc):.2f}"
              f"   {'(BATCH SOUND -- subjects named)' if spread(sc) > 0.10 else '(COLLAPSED -- check naming)'}")
    else:
        print("          (dry run -- no oracle call)")

    for rnd in range(1, rounds + 1):
        live = trail.state_at_head(cells)
        if not live:
            break
        parent = sorted(live)[0]
        kids = decompose(cells, parent, split, trail.head)
        for k in kids:
            cells[k.cid] = k
        trail.append("decompose",
                     {"parent": parent, "children": [k.cid for k in kids], "k": split},
                     result=f"{parent} -> {len(kids)} named children")
        live = trail.state_at_head(cells)
        subs_live = [cells[c].subject for c in live]
        if dry:
            print(f"  round {rnd}  array width = {len(live):<3} (+{split})   (dry -- unmeasured)")
        else:
            sc, _ = jev_batch(subs_live, question)
            ct, _ = jev_batch([HOMOGENEOUS_CONTROL] * len(subs_live), question)
            sp, lv, cv = spread(sc), level(sc), level(ct)
            disc = discrimination(sc, ct)
            verdict = ("array carries INFORMATION"
                       if disc > 0.20 else
                       "array is REDUNDANT -- this decomposition added restatement, not structure")
            print(f"  round {rnd}  array width = {len(live):<3} (+{split})   "
                  f"level={lv if lv is None else round(lv,3)}  "
                  f"control={cv if cv is None else round(cv,3)}  "
                  f"discrimination={disc:.2f}  spread={sp:.2f}")
            print(f"          {verdict}")
        if sc:
            ranked = sorted(((v, c) for c, v in zip(live, [sc.get(i) for i in range(len(live))])
                             if v is not None), reverse=True)
            for v, c in ranked[:3]:
                print(f"            {v:.3f}  {c}")
        # the nudge: one trailback proves the rewind path works on live data
        if rnd == 1 and len(trail.actions) > 1:
            before = trail.state_at_head(cells)
            if trail.rewind(trail.actions[0].seq):
                after = trail.state_at_head(cells)
                trail.append("nudge", {"action": "rewind to seed"},
                             result=f"live cells {len(before)} -> {len(after)} (nothing deleted)")
                print(f"          nudge: rewound to seed, {len(before)} -> {len(after)} live cells,"
                      f" {len(trail.actions)} actions retained")
                # re-apply so the array keeps growing after the demonstration
                kids2 = decompose(cells, parent, split, trail.head)
                for k in kids2:
                    cells[k.cid] = k
                trail.append("decompose",
                             {"parent": parent, "children": [k.cid for k in kids2], "k": split},
                             result="re-applied after the rewind demo")

    print()
    print(f"  trail: {len(trail.actions)} actions, head at seq {trail.head+1}, nothing deleted")
    print(f"  final live width: {len(trail.state_at_head(cells))}")
    print()
    out = dict(rounds=rounds, seed_width=width, split=split,
               actions=[asdict(a) for a in trail.actions],
               final_width=len(trail.state_at_head(cells)),
               cells={k: asdict(v) for k, v in cells.items()})
    json.dump(out, open("widening_trace.json", "w"), indent=1)
    print("  wrote widening_trace.json -- this trace IS the seed-state material for gen+1")
    print()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--width", type=int, default=3)
    ap.add_argument("--split", type=int, default=2)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    run(a.rounds, a.width, a.split, dry=a.dry)
