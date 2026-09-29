#!/usr/bin/env python3
"""
molt.py — soft shells.

A soft shell is a starting state, not a product. It fits exactly one size. It is
supposed to be outgrown, and when you outgrow it the correct action is to shed it and
find a larger one, not to patch it into something that fits nothing.

Three properties, and all three are load-bearing:

  1. APPLIABLE.   A shell is an application ON the quilt: it has a cell address, it
                  BINDs to the state you hand it, and it leaves a receipt. You do not
                  read a shell to understand it; you run it against a state and read
                  what it did.

  2. REWINDABLE.  Every apply() can snapshot the state first and return a handle. Calling
                  rewind(handle) puts the state back exactly. A shell that cannot be
                  left is a commitment, and commitments are what molt exists to avoid.

  3. FITS ONE SIZE. Each shell declares what it is for AND what it stops being good
                  for. A shell with no `outgrows` clause is a framework, and frameworks
                  are the thing this replaces.

The shells below are not invented for this file. They are the patterns that actually
carried today's work, extracted in the form they were used. If a shell is not in here
because it was used, it does not belong here.

USAGE
    python3 molt.py --self-test
    python3 molt.py --list
    python3 molt.py --show <name>
    python3 molt.py --apply <name> --state '{"k": 1}'
"""
from __future__ import annotations
import copy, json, sys
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Optional

# ── the cell address ──────────────────────────────────────────────────────────
# Everything in the quilt is addressable. A shell is a cell, so a shell has an addr.

def addr(*parts: str) -> str:
    """A cell address. Dotted, stable, greppable — and deliberately NOT a repo name,
    because a repo name is a distribution boundary and a shell is not."""
    return ".".join(p for p in parts if p)


@dataclass
class Receipt:
    """What a shell did. A shell that leaves no receipt is a shell you cannot audit,
    and an unauditable shell is where a fleet goes to accumulate cargo cult."""
    cell: str
    shell: str
    changed: list = field(default_factory=list)
    added: dict = field(default_factory=dict)
    removed: list = field(default_factory=list)
    note: str = ""
    rewind: Optional[str] = None

    def digest(self) -> str:
        import hashlib
        body = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(body.encode()).hexdigest()[:16]


@dataclass
class Molt:
    """A soft shell."""
    id: str                       # cell address
    name: str
    fits: str                     # what this shell is FOR
    outgrows: str                 # when it stops being the right size
    why: str                      # the reasoning it encodes, in one paragraph
    apply: Callable[[dict], dict] # the body: state -> (new_state, change_record)
    verify: Optional[Callable[[dict], bool]] = None   # did the shell actually work

    def __call__(self, state: dict) -> tuple[dict, Receipt]:
        before = copy.deepcopy(state)
        new_state, note = self.apply(copy.deepcopy(state))
        changed = [k for k in set(before) | set(new_state) if before.get(k) != new_state.get(k)]
        removed = [k for k in before if k not in new_state]
        added = {k: new_state[k] for k in new_state if k not in before}
        return new_state, Receipt(cell=self.id, shell=self.name, changed=changed,
                                  added=added, removed=removed, note=note)


# ── rewind ───────────────────────────────────────────────────────────────────

class Timeline:
    """Snapshot stack. rewind(handle) restores a state exactly.

    This is the whole reason a shell is soft. Without it, applying a shell is a
    decision; with it, applying a shell is an experiment."""

    def __init__(self):
        self._states: dict[str, dict] = {}
        self._order: list[str] = []

    def snapshot(self, label: str, state: dict) -> str:
        h = f"{label}#{len(self._order)}"
        self._states[h] = copy.deepcopy(state)
        self._order.append(h)
        return h

    def rewind(self, handle: str) -> dict:
        if handle not in self._states:
            raise KeyError(f"no such handle: {handle}")
        return copy.deepcopy(self._states[handle])

    def handles(self) -> list[str]:
        return list(self._order)

    def discard(self, handle: str) -> None:
        self._states.pop(handle, None)
        if handle in self._order:
            self._order.remove(handle)


def apply_with_rewind(molt: Molt, state: dict, timeline: Timeline) -> tuple[dict, Receipt, str]:
    handle = timeline.snapshot(molt.name, state)
    new_state, receipt = molt(state)
    receipt.rewind = handle
    return new_state, receipt, handle
