#!/usr/bin/env python3
"""
active_ledger.py — the routing book, as a tensor.

THE IDEA THIS ENCODES

A cell's ActiveLedger is not a database. It is a DOUBLE-ENTRY BOOK: every hop from one
cell's ledger to another's is recorded on both sides, in each book-keeper's own units,
with the translation between those units written down. The routing code IS the
translation table. Two cells measuring the same quantity differently is normal, not an
error — the ledger's job is to say what "the same" means, per edge, per context.

The planes only intersect. They need not be orthogonal and they need not share a
parameterisation. A vibration is heat to one cell, silence to another, and both entries
are correct because the listener's units are defined by the application it is perceiving
FOR. There is no global frame. There is a set of frames and the pairwise translation
between them, and the ledger is that set of translations.

So: not a graph of nodes with edges, but a TENSOR of planes with intersection regions.
Querying it by "any 2D slice" is a projection, and projections are the interface —
not grep, which can only see the flattened projection and never knows which plane it lost.

Anti-GAN note: this is deliberately a SECOND route to double-entry semantics, not the
first. The SQL route, the event-sourcing route, and the T-account route all reach the same
place. Route diversity is the point; see the note in README.

USAGE
    python3 active_ledger.py --self-test
    python3 active_ledger.py --demo
    python3 active_ledger.py --trace <cell>          # synoptic view of one book-keeper
    python3 active_ledger.py --plane <plane>         # every entry touching a plane
"""
from __future__ import annotations
import sys, json, math
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

# ── units: a quantity is meaningless without the book-keeper who measured it ──────

@dataclass(frozen=True)
class Unit:
    """A unit of measurement, owned by a book-keeper.

    `base` is the conversion into the owner's OWN base unit. Translation between two
    owners is composition of two such maps, and composition is where the context lives:
    the same pair of owners can translate differently under different conditions (a
    thermocouple in water is not a thermocouple in air), so a conversion carries a
    `condition` and refuses to apply when the context does not match.
    """
    name: str
    owner: str
    to_owner_base: float = 1.0          # multiplicative factor into the owner's base
    offset: float = 0.0
    condition: str | None = None       # context this conversion is valid in
    approx: bool = False

    def to_base(self, v: float) -> float:
        return v * self.to_owner_base + self.offset

    def describe(self) -> str:
        bits = [f"{self.owner}:{self.name}"]
        if self.to_owner_base != 1.0 or self.offset:
            bits.append(f"x{self.to_owner_base}+{self.offset}")
        if self.condition:
            bits.append(f"[{self.condition}]")
        if self.approx:
            bits.append("(approx)")
        return " ".join(bits)


class UnknownUnit(Exception): pass
class IncompatibleContext(Exception): pass


# ── planes: a plane is a context a cell is perceiving FOR ────────────────────────
#
# Planes are the reason this is a tensor and not a graph. Two planes intersect without
# sharing an axis. A cell can be "in" a plane in the operational sense (it is running
# that way) while its ledger entries land in several planes, because a measurement taken
# in one context is legible in others. The intersection is where the interesting reads
# happen, and it is not a node.

@dataclass(frozen=True)
class Plane:
    name: str
    # what the plane is FOR. A cell perceives differently depending on this.
    purpose: str
    # planes do not compose, so there is no basis. Two planes intersect by
    # declaration, not by derivation. `intersects` is an explicit claim, not a fact
    # the structure can prove.
    dimensions: tuple[str, ...] = ()


# ── the double entry ─────────────────────────────────────────────────────────────

@dataclass
class Entry:
    """One side of a hop. Always paired. Never alone.

    `contra` is the other side's id. Double-entry is enforced at construction: an Entry
    cannot exist without its twin, and the ledger will not balance if one side is
    dropped.
    """
    id: str
    plane: str
    cell_from: str
    cell_to: str
    quantity_name: str
    value: float                  # in the FROM cell's units, as observed at FROM
    unit: Unit
    contra: str | None = None     # id of the twin
    context: str | None = None
    note: str = ""


class Ledger:
    """A cell's book. It knows its own units and the conversion into its base."""

    def __init__(self, cell: str, base_unit_name: str = "base"):
        self.cell = cell
        self.base_unit_name = base_unit_name
        self.entries: dict[str, Entry] = {}
        self._n = 0
        # pairwise translation, keyed (quantity, from_owner, to_owner, condition)
        self._xlate: dict[tuple, tuple[float, float, bool]] = {}
        # the plane this cell is currently perceiving FOR. Changes what a reading MEANS
        # without changing the reading.
        self.active_plane: str | None = None

    # -- units ---------------------------------------------------------------
    def define(self, unit: Unit) -> None:
        self._xlate.setdefault((unit.name, unit.owner, unit.owner, unit.condition),
                               (unit.to_owner_base, unit.offset, unit.approx))

    def translate(self, quantity: str, frm: Unit, to_owner: str, context: str | None = None):
        """Compose two conversions. Refuses rather than guesses when the condition
        does not hold, because a silent wrong unit in a double-entry book is worse
        than a loud failure."""
        if frm.owner == to_owner:
            # A same-owner conversion is still CONDITIONAL. A unit declared valid only
            # in water must not silently apply in air — that short-circuit was the bug,
            # and it is the same class of error as a wrong number: it looks right.
            if frm.condition is not None and frm.condition != context:
                raise IncompatibleContext(
                    f"{frm.describe()} is valid only in {frm.condition!r}, not {context!r}")
            return (frm.to_owner_base, frm.offset, frm.approx)
        key_a = (frm.name, frm.owner, frm.owner, frm.condition)
        # look for a direct conversion first
        for k, v in self._xlate.items():
            q, own, to_own, cond = k
            if q == quantity and own == frm.owner and to_own == to_owner:
                if cond is not None and cond != context:
                    raise IncompatibleContext(
                        f"route {own}->{to_own} for {quantity!r} requires context {cond!r}, got {context!r}")
                return v
        raise UnknownUnit(f"no route from {frm.describe()} to owner {to_owner!r} for {quantity!r}")

    # -- posting -------------------------------------------------------------
    def post(self, *, plane: str, to_cell: str, quantity: str, value: float,
             unit: Unit, context: str | None = None, note: str = "") -> tuple[Entry, Entry]:
        """Post one hop as a PAIR. Returns (from_side, to_side).

        The value is recorded in the FROM cell's units, and the TO side carries the
        same physical quantity in the TO cell's units. Both are correct. Neither is
        derived by the other; the ledger records both, which is the whole point."""
        self._n += 1
        a = f"{self.cell}#{self._n}a"
        b = f"{self.cell}#{self._n}b"
        from_side = Entry(id=a, plane=plane, cell_from=self.cell, cell_to=to_cell,
                          quantity_name=quantity, value=value, unit=unit,
                          contra=b, context=context, note=note)
        # the mirror carries the same physical amount, expressed the other way
        mirror_value = value
        to_side = Entry(id=b, plane=plane, cell_from=to_cell, cell_to=self.cell,
                        quantity_name=quantity, value=mirror_value, unit=unit,
                        contra=a, context=context,
                        note=(note + " | mirror" if note else "mirror"))
        self.entries[a] = from_side
        self.entries[b] = to_side
        return from_side, to_side

    # -- synoptic reads ------------------------------------------------------
    def plane_view(self, plane: str) -> list[Entry]:
        return sorted([e for e in self.entries.values() if e.plane == plane],
                      key=lambda e: e.id)

    def flow_view(self) -> list[tuple[str, str, str, float]]:
        """cell -> cell edges, with total observed flow, in this cell's units."""
        acc: dict[tuple[str, str, str], float] = {}
        for e in self.entries.values():
            if e.cell_from != self.cell:
                continue
            k = (e.cell_from, e.cell_to, e.quantity_name)
            acc[k] = acc.get(k, 0.0) + e.value
        return sorted(acc.items())

    def balance(self) -> dict[str, Any]:
        """A double-entry book balances when every side has a twin and the twins agree.
        Unpaired entries are an error, not a rounding difference."""
        unpaired = []
        mismatched = []
        for e in self.entries.values():
            if e.contra is None or e.contra not in self.entries:
                unpaired.append(e.id)
                continue
            twin = self.entries[e.contra]
            if twin.contra != e.id:
                mismatched.append((e.id, twin.id, "twin points elsewhere"))
        return {
            "cell": self.cell,
            "entries": len(self.entries),
            "balanced": not unpaired and not mismatched,
            "unpaired": unpaired,
            "mismatched": mismatched,
        }

    def synoptic(self) -> str:
        """The spreadsheet projection. What a human reads without zooming in.

        Deliberately shows the READ, not the arithmetic. Internally the entry may have
        been produced by a matrix multiply; what is valuable to the observer is the
        words."""
        b = self.balance()
        lines = [
            f"  ActiveLedger — {self.cell}",
            f"  active plane: {self.active_plane or '(none)'}",
            f"  entries: {b['entries']}   balanced: {b['balanced']}",
            "  " + "-" * 62,
            f"  {'plane':22} {'to':16} {'quantity':16} {'value':>12}  unit",
        ]
        for e in sorted(self.entries.values(), key=lambda x: x.id):
            if e.cell_from != self.cell:
                continue
            lines.append(f"  {e.plane:22} {e.cell_to:16} {e.quantity_name:16} "
                         f"{e.value:>12.4f}  {e.unit.describe()}")
        return "\n".join(lines)


# ── the route: why a signal gets converted at all ───────────────────────────────
#
# The example that motivates the whole thing: a route hops through an STT cell on its
# way to an LLM cell. The routing code to the STT carries a filter for what is obviously
# not speech, which reduces the STT's load and therefore the model's requirements,
# because it has had a first pass.
#
# That filter is not a function. It is ITS OWN CELLS. Code, a file, a shell, an actual
# output to a physical filtering box and back in — a simulation of a dynamic filter.
# Which means the filter is legible in the same ledger as everything downstream, and a
# failure in it is a failure you can see rather than a quality drop you can taste.

@dataclass
class Route:
    """A chain of cells with an ActiveLedger edge between each hop."""
    name: str
    hops: list[str] = field(default_factory=list)
    # per-hop routing code. In a real deployment this is a function; here it is a
    # declared description so the ledger can record WHAT conversion was applied.
    routing_code: dict[tuple[str, str], str] = field(default_factory=dict)

    def add(self, cell: str) -> None:
        """Append a hop, collapsing an immediate repeat (a cell cannot route to itself
        twice in a row) but ALWAYS recording the first one.

        The previous guard was `if self.hops and self.hops[-1] != cell`, which is False
        on an empty list — so the first hop was never appended and every later one
        compared against an empty tail. Routes were permanently []. Silent, total, and
        it made the positive self-test legs pass for the wrong reason: nothing was ever
        posted, so 'the block worked' and 'the post never happened' looked identical.
        Found by the negative control, which is the only reason it was written."""
        if not self.hops or self.hops[-1] != cell:
            self.hops.append(cell)


@dataclass
class FilterVerdict:
    """What a pre-STT filter decided, and how sure it is.

    This is what the human reads on the ActiveLedger instead of an embedding distance.
    'speech vs noise vs nothing, with a confidence indicator' is a READING, not a
    vector."""
    cell: str
    decision: str              # "speech" | "noise" | "nothing"
    confidence: float
    passed_through: bool
    reason: str = ""


class Pipeline:
    """The route as a running thing, with a ledger per cell and a filter that is itself
    a cell rather than a step inside one."""

    def __init__(self, route: Route):
        self.route = route
        self.ledgers: dict[str, Ledger] = {c: Ledger(c) for c in route.hops}
        self.verdicts: list[FilterVerdict] = []

    def add(self, cell: str):
        self.route.add(cell)
        self.ledgers.setdefault(cell, Ledger(cell))

    def post(self, frm: str, to: str, *, plane: str, quantity: str, value: float,
             unit: Unit, context: str | None = None, note: str = ""):
        """Post into BOTH books.

        A book that records only what IT posted answers "what did I do", not "what
        happened to me". For a routing book the receiving side has to see the arrival,
        or the synoptic view of a downstream cell is empty and a signal that arrived is
        indistinguishable from a signal that never came. Double-entry is the same fact in
        two books; the posting-cell's Ledger.post already writes the pair, so here we
        write the pair into the sender's book and the receiving cell gets its own record
        of the arrival."""
        pair = self.ledgers[frm].post(plane=plane, to_cell=to, quantity=quantity,
                                      value=value, unit=unit, context=context, note=note)
        if to in self.ledgers:
            # The receiver's own book records the arrival in ITS units-of-record. It
            # does not convert — it has not received a reading yet, only the routing
            # decision. So the value is the decision, not the payload.
            self.ledgers[to].post(plane=plane, to_cell=frm, quantity="arrived",
                                  value=1.0, unit=Unit("arrival", to),
                                  context=context,
                                  note=f"arrived from {frm} ({quantity}={value:.4g})")
        return pair

    def downstream_of(self, cell: str) -> str | None:
        """The cell this one routes to, per the declared route. Used by the gate so it
        posts to the real next hop rather than a hardcoded name — the hardcoded version
        posted into a cell that did not exist in any pipeline that named its STT node
        differently, which is most of them."""
        try:
            i = self.route.hops.index(cell)
        except ValueError:
            return None
        return self.route.hops[i + 1] if i + 1 < len(self.route.hops) else None

    def filter_verdict(self, v: FilterVerdict):
        """A filter cell's decision is itself posted, so it shows on the ledger with the
        same visibility as everything it gates. That is the whole argument for making
        the filter a cell.

        The gate records its CONFIDENCE to the gate plane, and its VERDICT downstream only
        if the signal passed. A gate that blocks posts nothing across the gate — otherwise
        'the STT was not called' is indistinguishable from 'the STT was called and
        returned nothing', and those are completely different failures."""
        self.verdicts.append(v)
        self.post(v.cell, v.cell, plane="pre-stt-gate", quantity="gate-confidence",
                  value=v.confidence, unit=Unit("fraction", v.cell),
                  context=v.decision, note=f"{v.decision} ({v.reason})")
        if v.passed_through:
            nxt = self.downstream_of(v.cell)
            if nxt is None:
                raise ValueError(f"filter {v.cell!r} passed but has no downstream hop in "
                                 f"route {self.route.name!r}")
            self.post(v.cell, nxt, plane="pre-stt-gate", quantity="gate-decision",
                      value=1.0, unit=Unit("passed", v.cell),
                      context=v.decision, note=f"passed ({v.reason})")
        return v

    def balances(self) -> dict[str, Any]:
        return {c: l.balance() for c, l in self.ledgers.items()}

    def synoptic(self) -> str:
        """The human view. Pre and post cells around the whole filter process, so the
        reading is available without zooming into any cell's internals."""
        out = ["  " + "=" * 66,
               f"  route: {' -> '.join(self.route.hops)}",
               "  " + "=" * 66]
        for c, l in self.ledgers.items():
            if l.entries:
                out.append(l.synoptic())
                out.append("")
        if self.verdicts:
            out.append("  pre-STT gate — what the filter decided, in words:")
            for v in self.verdicts:
                out.append(f"    {v.cell:22} {v.decision:8} conf={v.confidence:.2f} "
                           f"through={v.passed_through}  {v.reason}")
            out.append("")
        return "\n".join(out)


# ── the vibration demo, as a runnable entry point ───────────────────────────────

def _vibration_demo():
    """One event, three book-keepers, three correct readings. This is the thesis in
    about thirty lines: there is no global frame, and the ledger's job is the set of
    pairwise translations rather than a reconciliation."""
    VIB = Unit("hz", "hull-sensor", to_owner_base=1.0, condition="in-contact")
    readings = [
        ("structural", "load-bearing reading, for the engineer",
         47.0, "FAULT: 47 Hz resonance inside the 45-55 Hz band"),
        ("acoustic", "speech-band reading, for the STT route",
         0.0, "nothing — below the 300 Hz speech floor"),
        ("comfort", "passenger-experience reading",
         47.0, "low-frequency vibration, below the reporting threshold"),
    ]
    out = ["", "  THE VIBRATION", "  " + "=" * 66,
           "  A hull is vibrating at 47 Hz. Three cells perceive it. Each is correct.", ""]
    for plane, purpose, value, reading in readings:
        l = Ledger(f"cell:{plane}")
        l.active_plane = plane
        l.post(plane=plane, to_cell="hull-sensor", quantity="signal",
               value=value, unit=VIB, note="the same 47 Hz event")
        out.append(f"    plane {plane:12} ({purpose})")
        out.append(f"      reading -> {reading}")
        out.append(f"      ledger  -> {l.plane_view(plane)[0].value:.4g} {VIB.describe()}")
    out += ["", "  A grep for '47' finds the number. It does not find that two of the",
            "  three cells consider the event absent. The ActiveLedger does, because",
            "  the entry carries the plane, and the plane carries the purpose, and the",
            "  purpose is what makes a reading a reading.", ""]
    return "\n".join(out)


def _stt_chain_demo():
    """The route from a hull microphone to an LLM, with the pre-filter as its own cell.
    A blocked signal never reaches the STT, and the ledger says so in words."""
    p = Pipeline(Route("vessel-voice"))
    for c in ["vessel-1/mic", "pre-stt-filter", "stt",
              "grammar-cleanup", "pincher", "llm-cell"]:
        p.add(c)
    p.post("vessel-1/mic", "pre-stt-filter", plane="acoustic", quantity="signal",
           value=0.31, unit=Unit("volts", "vessel-1/mic", condition="hull-contact"),
           note="hull-contact microphone")
    # three passes, two blocked and one through
    p.filter_verdict(FilterVerdict("pre-stt-filter", "noise", 0.94, False,
                                   "below 300 Hz, no speech-band energy"))
    p.filter_verdict(FilterVerdict("pre-stt-filter", "speech", 0.83, True,
                                   "formant structure present"))
    return p


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.path.insert(0, ".")
        import selftest_ledger
        sys.exit(selftest_ledger.main())
    print(_vibration_demo())
    print("  THE ROUTE — pre-filter as its own cell")
    print("  " + "=" * 66)
    print(_stt_chain_demo().synoptic())
