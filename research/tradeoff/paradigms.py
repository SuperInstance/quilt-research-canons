#!/usr/bin/env python3
"""
paradigms.py — every spec is a plugin, and every plugin taxes another paradigm.

THE OBSERVATION

Each thing in this fleet is optimal inside one value system and expensive outside it. That
is not a flaw in any of them. It is what a plugin IS: a local optimum that becomes a
global cost somewhere you were not looking.

The failure is not having trade-offs. It is having them UNSTATED. A spec that names only
what it maximises reads as though it has no cost, and the cost then lands somewhere nobody
was measuring — usually in a different agent's paradigm, weeks later, attributed to
something else.

So the rule this file enforces is narrow and checkable:

    A spec that does not name the paradigm it TAXES is not finished.

That is a completeness gate, not a quality gate. It does not tell you which spec to use.
It tells you that a spec claiming no cost is a spec whose cost is unlocated.

THE PARADIGMS IN PLAY

These are not abstract. Each one is a real value system something in this fleet is
actually optimising, and each has a cost that is actually being paid.
"""
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Paradigm:
    id: str
    name: str
    """What "better" means inside this value system. Deliberately narrow: a paradigm that
    measured everything would not be a paradigm."""
    measures: str
    """The one number a practitioner in this paradigm watches."""
    blind_to: str
    """What this value system structurally cannot see. Not 'overlooks' — CANNOT see,
    because the measurement is defined in terms that exclude it."""

PARADIGMS = {
 "bandwidth":  Paradigm(
    id="bandwidth", name="Transport",
    measures="bits per frame, cells carried per wire",
    blind_to="that a cancelled cell and a correctly-predicted cell cost the SAME, so "
             "cancellation buys nothing the predictor has not already bought"),
 "fidelity":   Paradigm(
    id="fidelity", name="Fidelity",
    measures="reconstruction error against the source",
    blind_to="that the source may not be the thing worth reconstructing"),
 "persistence":Paradigm(
    id="persistence", name="Durability",
    measures="what survives the next wipe",
    blind_to="that a survivor nobody can reach is a liability, not an asset"),
 "audit":      Paradigm(
    id="audit", name="Auditability",
    measures="fraction of claims with a traceable receipt",
    blind_to="that recording every hop is exactly wrong on a hot path"),
 "calibration":Paradigm(
    id="calibration", name="Calibration",
    measures="predicted probability against realised frequency",
    blind_to="that an instrument which cannot discriminate will still return a confident "
             "number, and the confidence is not a property of the answer"),
 "legibility": Paradigm(
    id="legibility", name="Legibility",
    measures="can a stranger use this unaided",
    blind_to="that legibility achieved by removing substance is indistinguishable from "
             "legibility achieved by adding it"),
 "locality":   Paradigm(
    id="locality", name="Locality",
    measures="latency to a local answer, no remote dependency",
    blind_to="that a subgraph optimised alone can be net-negative for the whole"),
 "sheddability":Paradigm(
    id="sheddability", name="Sheddability",
    measures="how cheaply a component is abandoned",
    blind_to="that a system where everything is sheddable has nothing to rely on"),
}
