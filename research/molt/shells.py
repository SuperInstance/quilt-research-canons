#!/usr/bin/env python3
"""
shells.py — the soft shells, extracted from patterns that actually fired.

Every shell here corresponds to something that ran today and did work. Nothing is
included because it sounds like good practice. If a shell is not in here because it was
used, it does not belong here.
"""
import json
import sys

from molt import Molt, Receipt, addr, Timeline, apply_with_rewind

MOLTS: list[Molt] = []
def shell(id_, name, fits, outgrows, why, body, verify=None):
    m = Molt(id=id_, name=name, fits=fits, outgrows=outgrows, why=why, apply=body, verify=verify)
    MOLTS.append(m); return m

# ── 1. pre-register ──────────────────────────────────────────────────────────
def _preregister(state):
    """Force the prediction to exist BEFORE the run, with a number in it."""
    title = state.get("title", "(untitled)")
    if "predictions" in state:
        return state, f"'{title}' is already pre-registered; not re-registering"
    n = state.get("n_predictions", 3)
    out = dict(state)
    out["predictions"] = [
        {"id": f"P{i+1}", "predict": None, "tolerance": 0.10, "kind": "num",
         "result": None, "status": "REGISTERED",
         "claim": f"a claim that names a number, written before the run"}
        for i in range(n)]
    out["status"] = "PREREGISTERED"
    return out, f"{n} predictions registered for '{title}'"

shell(addr("molt", "method", "pre-register"),
      "pre-register",
      fits="Any run that could produce a number. Writing the prediction first is the "
           "only way the run can be wrong in a way that corrects a belief.",
      outgrows="You are registering hundreds of predictions a round and nobody reads the "
               "debriefs. Then the pre-registration is theatre and the round is noise.",
      why="A loop that only confirms cannot correct a belief. The expensive part of a "
          "prediction is writing it down before you know, and that is exactly the part "
          "that gets skipped when the run is about to start anyway.",
      body=_preregister,
      verify=lambda s: bool(s.get("predictions")) and s.get("status") == "PREREGISTERED")

# ── 2. fault injection ───────────────────────────────────────────────────────
def _fault_inject(state):
    """Every rule claims a negative control. Run one and confirm the suite notices."""
    rule = state.get("rule", "(unnamed)")
    checks = state.get("checks", [])
    outcome = state.get("outcome", "unknown")
    survived = outcome == "SURVIVED"
    out = dict(state)
    out["verdict"] = ("THE RULE IS NOT COVERED" if survived else "the rule is covered")
    if survived:
        out["next"] = ("the claim may be untestable rather than the test weak — check "
                       "whether the fault's precondition is REACHABLE in the code")
    out["checks_exercised"] = len(checks)
    return out, f"injected into '{rule}' with {len(checks)} checks: {outcome}"

shell(addr("molt", "test", "fault-injection"),
      "fault-injection",
      fits="Any test suite you are about to trust, and any rule you are about to "
           "depend on. Break the thing on purpose and confirm the suite notices.",
      outgrows="You find that every fault is caught first time, or that the faults you "
               "can think of are not the faults that happen. Then the KAT is the shape "
               "of a discipline and not the discipline.",
      why="A passing suite that cannot fail is worse than no suite, because it gets "
          "consumed as evidence. The only defence is to break the thing deliberately. "
          "The most valuable outcome is not 'caught' — it is a fault that SURVIVES, "
          "because a surviving fault is the one place your model of the code is wrong.",
      body=_fault_inject,
      verify=lambda s: "verdict" in s)

# ── 3. derive the prose ──────────────────────────────────────────────────────
def _derive_prose(state):
    """Every sentence a demo prints must come from the run, not from the author."""
    run = state.get("run", {})
    out = dict(state)
    claims, wrong = [], []
    for text, actual in (state.get("claims") or []):
        ok = str(actual) in str(text)
        (claims if ok else wrong).append((text, actual))
    out["claims_checked"] = len(claims) + len(wrong)
    out["claims_false"] = len(wrong)
    out["verdict"] = ("the demo contradicts its own output" if wrong
                      else "every claim in the demo is derived from the run")
    if wrong:
        out["first_contradiction"] = wrong[0]
    return out, f"{len(claims)} claims verified, {len(wrong)} contradicted the run"

shell(addr("molt", "test", "derive-prose-from-run"),
      "derive-prose-from-run",
      fits="Any demo, any report, any reading written next to a number. Especially when "
           "the number is one you already believe.",
      outgrows="You are writing narrative for a human who is not reading the output. "
               "Then the coupling has to break, but it should break on purpose, not "
               "quietly.",
      why="A demo whose prose contradicts its own output teaches the reader to trust a "
          "number and ignore the sentence next to it. That is a worse outcome than no "
          "demo, because it actively trains the reader. Every assertion should be a "
          "lookup into the run.",
      body=_derive_prose,
      verify=lambda s: s.get("claims_checked", 0) > 0)

# ── 4. the rewind shell ──────────────────────────────────────────────────────
def _rewind_shell(state):
    """Outgrowing a shell is the normal case, not the failure case."""
    uses = state.get("uses", 0)
    threshold = state.get("fit_for", 10)
    out = dict(state)
    out["action"] = ("shed" if uses >= threshold else "keep")
    out["why"] = (f"{uses}/{threshold} uses — a soft shell is meant to be outgrown, and "
                  f"a shell past its fit is not a success, it is a leftover"
                  if uses >= threshold else f"{uses}/{threshold} uses, still the right size")
    return out, out["why"]

shell(addr("molt", "self", "outgrew-it"),
      "outgrew-it",
      fits="Deciding whether to keep or shed whatever you have been using. The default "
           "answer to 'should I keep growing this' is no.",
      outgrows="You start shedding things you are still using successfully. Then the "
               "rule has become a ritual and the shell-trap is closed from the wrong side.",
      why="Nothing in a substrate that lives gets bigger by accretion alone. A shell "
          "that has outgrown its fit is a liability dressed as continuity, and the "
          "expensive mistake is never shedding.",
      body=_rewind_shell,
      verify=lambda s: s.get("action") in ("shed", "keep"))

# ── 5. two instruments, no reconciliation ────────────────────────────────────
def _two_instruments(state):
    """Run two instruments on one thing and DO NOT average them."""
    a, b = state.get("a"), state.get("b")
    both = [x for x in (a, b) if isinstance(x, (int, float))]
    out = dict(state)
    if len(both) < 2:
        out["verdict"] = "NEED TWO INSTRUMENTS"
    else:
        out["agree"] = (a > 0.7) == (b > 0.7)
        out["spread"] = round(abs(a - b), 4)
        out["verdict"] = ("both clear" if out["agree"] and a > 0.7
                          else "both block" if out["agree"]
                          else "THEY DISAGREE — that is the finding, keep both")
    return out, out["verdict"]

shell(addr("molt", "method", "two-instruments"),
      "two-instruments",
      fits="Any claim you are about to trust, where a single instrument could be wrong "
           "in a way that agrees with you.",
      outgrows="The two instruments turn out to share an ancestor and you have not "
               "checked. Then you have one instrument wearing two hats — which is the "
               "reconciliation failure this shell exists to prevent.",
      why="A second reader that shares your substrate, your model lineage and your "
          "incentives is not a second reader, it is the same reader twice. And a "
          "disagreement between two genuinely independent instruments is the most "
          "informative thing in the system. Averaging it away throws away the only "
          "cross-check you had.",
      body=_two_instruments,
      verify=lambda s: "verdict" in s)

# ── 6. measure before concluding ─────────────────────────────────────────────
def _measure_first(state):
    """Replace an assertion with a measurement, even when you are confident."""
    belief = state.get("belief", "(unmeasured)")
    measurement = state.get("measurement")
    out = dict(state)
    if measurement is None:
        out["status"] = "UNMEASURED"
        out["next"] = f"'{belief}' is a belief. Measure it or mark it as a belief."
    else:
        out["status"] = "MEASURED"
        out["belief_confirmed"] = measurement == state.get("predicted")
    return out, out["status"]

shell(addr("molt", "method", "measure-first"),
      "measure-first",
      fits="Any claim about your own work, especially the ones you are already sure of. "
           "The census refuted four of five of my predictions in a single round.",
      outgrows="You are measuring things that cannot be measured and recording a number "
               "anyway. Then the number is a costume and the round is slower than "
               "believing.",
      why="Confidence is not evidence and never has been. The specific failure is "
          "filtering: you measure the thing you already believed and report it as a "
          "result. Pre-registering the prediction is the only thing that makes the "
          "measurement honest, because it commits you to a number before the "
          "measurement exists.",
      body=_measure_first,
      verify=lambda s: s.get("status") in ("MEASURED", "UNMEASURED"))

# ── 7. quilt-native addressing ───────────────────────────────────────────────
def _to_cells(state):
    """Split a flat dict into cells. The address is the unit, not the key."""
    out = {}
    for k, v in (state.get("flat") or {}).items():
        if isinstance(v, dict):
            out[addr("cell", k)] = v
        else:
            out[addr("field", k)] = v
    return out, f"{len(out)} cells addressed"

shell(addr("molt", "quilt", "to-cells"),
      "to-cells",
      fits="Turning a flat record into something addressable, so a later shell can BIND "
           "to part of it without touching the rest.",
      outgrows="Your cells have no edges and the addressing is a naming convention. "
               "Then it is a namespace, not a graph, and BIND has nothing to bind to.",
      why="A repository is a distribution boundary: something you clone, version and "
          "depend on. A cell is not. Keeping the two apart is what lets the same logic "
          "live in twelve languages and in a Python package and in a running route "
          "without any of them being the unit of meaning.",
      body=_to_cells,
      verify=lambda s: all("." in k for k in s))


def by_name(n):
    """Look up a shell by its short name. Every consumer needs this and it belongs
    next to the registry rather than in each caller."""
    return next(m for m in MOLTS if m.name == n)


def main():
    import argparse, json, sys
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--show")
    ap.add_argument("--apply")
    ap.add_argument("--state", default="{}")
    a = ap.parse_args()
    if a.self_test:
        import self_test
        return self_test.main()
    if a.list or (not a.show and not a.apply):
        print(f"  {len(MOLTS)} soft shells\n")
        for m in MOLTS:
            print(f"  {m.id}")
            print(f"    fits      {m.fits}")
            print(f"    outgrows  {m.outgrows}")
            print()
        return 0
    if a.show:
        m = by_name(a.show)
        print(f"  {m.id} — {m.name}")
        print(f"\n  FITS\n    {m.fits}")
        print(f"\n  OUTGROWS\n    {m.outgrows}")
        print(f"\n  WHY\n    {m.why}")
        return 0
    if a.apply:
        m = by_name(a.apply)
        state = json.loads(a.state)
        tl = Timeline()
        ns, r, h = apply_with_rewind(m, state, tl)
        print(f"  applied {m.id}")
        print(f"    changed: {r.changed}")
        print(f"    added:   {list(r.added)}")
        print(f"    note:    {r.note}")
        print(f"    receipt: {r.digest()}")
        print(f"    rewind:  {h}")
        print()
        print(f"  state now: {json.dumps(ns, indent=2, default=str)[:400]}")
        print(f"  rewind to: {h}")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
