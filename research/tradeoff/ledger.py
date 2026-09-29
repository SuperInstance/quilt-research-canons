#!/usr/bin/env python3
"""
ledger.py — the trade-off ledger, and the gate that makes an entry incomplete without it.

Every entry is a REAL thing in this fleet, with the paradigm it optimises and the paradigm
it taxes. Nothing here is hypothetical. The point is that all of them are ALSO the obvious
choice inside their own paradigm, which is what makes them plugins rather than mistakes.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from paradigms import PARADIGMS

@dataclass
class Plugin:
    id: str
    what: str
    optimises: str                    # paradigm id
    taxes: list = field(default_factory=list)   # paradigm ids
    how: str = ""                     # the mechanism, stated so it can be argued with
    unmitigated: str = ""             # what gets worse and nothing currently pays for it
    reversible: bool = True

    def complete(self) -> bool:
        """A plugin that names no cost is not finished. This is the whole gate."""
        return bool(self.taxes) and bool(self.unmitigated)

    def who_pays(self) -> list:
        """The paradigms that bear the cost. Named, so it can be argued about rather than
        discovered later by whoever happens to be standing there."""
        return [PARADIGMS[t].name for t in self.taxes if t in PARADIGMS]


PLUGINS = [
  Plugin(id="qpixl-residual",
    what="cancel constant rows, uniform intensity, absent colour channels, unchanged cells",
    optimises="bandwidth",
    taxes=["fidelity", "calibration"],
    how="QPIXL's decomposition run on glyphs: delete identity terms and report what is left.",
    unmitigated="a cancelled cell and a correctly-PREDICTED cell cost the same, so a "
                "matcher that finds the wrong correspondence looks 67 points cheaper than "
                "the truth and nothing in the pipeline notices"),

  Plugin(id="glyphcast-pyramid",
    what="coarse-to-fine heads 12x9 -> 48x36 -> 96x72",
    optimises="bandwidth",
    taxes=["fidelity"],
    how="resolution flows to wherever the bandwidth moment needs it.",
    unmitigated="a pyramid says HOW MUCH to spend. It cannot say WHICH WAY to describe a "
                "cell, so a cell that is cheap to describe wrongly is described wrongly "
                "at full cost. A menu would let it choose SKIP"),

  Plugin(id="reef-coral",
    what="structure that outlasts the polyp that built it",
    optimises="persistence",
    taxes=["locality", "sheddability"],
    how="mass accumulates from deposits; a polyp can die and the mass stays.",
    unmitigated="a dead agent's work persists and keeps costing attention. Persistence "
                "without reachability is a liability, and nothing here distinguishes them"),

  Plugin(id="active-ledger",
    what="double-entry routing book; every hop recorded on both sides in both units",
    optimises="audit",
    taxes=["locality", "bandwidth"],
    how="translation tables between book-keepers; planes that only intersect.",
    unmitigated="recording every hop is precisely wrong on a hot path. This is a design "
                "probe, not a service, and the cost has not been paid because nothing "
                "runs on it yet"),

  Plugin(id="jev-gate",
    what="promote a claim to canon at p > 0.7",
    optimises="calibration",
    taxes=["legibility"],
    how="a calibrated oracle, 0.7 threshold, FAIL-first receipts.",
    unmitigated="the `score` question type returns a near-constant at confident-looking "
                "confidence, so any score-based gate is decorative. The gate itself is a "
                "STEP function: it fires on mechanism-plus-guarantee and is inert after"),

  Plugin(id="two-views",
    what="one substrate, a human projection and an agent projection",
    optimises="legibility",
    taxes=["persistence"],
    how="one walk over one dict, rendered twice; rewind by frame index.",
    unmitigated="the human view is rich and the agent view is a contract, and they are "
                "generated together — so improving one degrades the other unless both are "
                "regenerated, and there is no such step to forget"),

  Plugin(id="molt-shells",
    what="soft shells with an explicit outgrows clause and a rewind handle",
    optimises="sheddability",
    taxes=["persistence"],
    how="every shell declares what it fits and what it stops fitting.",
    unmitigated="a system where everything is sheddable has nothing to rely on. The rule "
                "is right per-component and wrong as an architecture"),

  Plugin(id="chiaroscuro-ramp",
    what="fixed ramp, characters as shapes, colour discarded",
    optimises="fidelity",
    taxes=["bandwidth", "legibility"],
    how="real-time webcam-to-text; the glyph IS the quantisation.",
    unmitigated="intensity carries nothing below the ramp step while colour does, so a "
                "matcher keyed on the coarser channel under-charges. Fixing it is a "
                "colour-ramped lattice, which is an engine change"),

  Plugin(id="two-readers",
    what="a second reader on a different substrate verifies the first",
    optimises="audit",
    taxes=["bandwidth"],
    how="second language, second model, or second role; all three used this session.",
    unmitigated="three of the checks this session found their own bugs by agreeing, which "
                "means the disagreements are rarer than the agreement rate suggests and "
                "the true error rate is higher than measured"),
]

def audit() -> dict:
    incomplete = [p.id for p in PLUGINS if not p.complete()]
    by_paradigm = {}
    for p in PLUGINS:
        by_paradigm.setdefault(p.optimises, []).append(p.id)
    taxed = {}
    for p in PLUGINS:
        for t in p.taxes:
            taxed.setdefault(t, []).append(p.id)
    return {
        "n": len(PLUGINS),
        "incomplete": incomplete,
        "optimises": by_paradigm,
        "taxed": taxed,
        "unpaid": [p.id for p in PLUGINS if p.unmitigated],
    }

if __name__ == "__main__":
    a = audit()
    print()
    print("  THE TRADE-OFF LEDGER")
    print("  " + "=" * 78)
    print(f"  {a['n']} plugins, each optimal inside its paradigm and expensive outside it.")
    print(f"  entries missing a declared cost: {a['incomplete'] or 'none'}")
    print()
    for p in PLUGINS:
        par = PARADIGMS[p.optimises]
        print(f"  {p.id}")
        print(f"    optimises  {par.name}  ({par.measures[:52]})")
        print(f"    taxes      {', '.join(p.who_pays()) or 'NOTHING DECLARED'}")
        print(f"    unpaid     {p.unmitigated[:96]}")
        print()
    print("  WHO PAYS, IN TOTAL")
    print("  " + "-" * 78)
    for t, ids in sorted(a["taxed"].items(), key=lambda x: -len(x[1])):
        print(f"    {PARADIGMS[t].name:14} taxed by {len(ids)}: {', '.join(ids)}")
