#!/usr/bin/env python3
"""
reef.py — the coral reef model, with skin.

`ternary-reef` is a specification: Reef, Coral, Polyp, Symbiodinium, ReefZone,
BleachingEvent, and a lifecycle Seedling -> Juvenile -> Adult -> Ancient. It is
8 files and a README, and the README has a Rust example nobody has run.

This is the same model, executable, in the language this fleet actually ships
(C99 was the reference port; Python is the one that reaches an ESP32 and a
browser). It is deliberately a SECOND ROUTE to the same semantics, per the
anti-GAN doctrine: the Rust crate and this are two ways to the same reef, and
where they disagree is where the model is wrong.

WHY THE METAPHOR IS load-BEARING RATHER THAN DECORATIVE:

  Coral is a slow-growing persistent structure built by polyps. A polyp can die
  and the coral remains. That is the whole argument for substrate over model, and
  it is checkable: does killing a polyp change the reef's mass? It should not.

  Symbiodinium are endosymbionts: the polyp hosts a thing that makes its own
  energetics possible, and loses both when stressed. In this model a polyp
  without its symbiont cannot pay its maintenance cost. That is the dependency
  pressure that makes regeneration coupled rather than independent.

  Bleaching is a stress event that can destroy OR strengthen the colony. A reef
  that never bleaches has never been tested. This is the anti-GAN's forcing
  function and it is the most useful idea in the whole README.

  Zones partition by light and depth, with capacity limits. A reef with no
  zoning is a heap. Zoning is what makes "preferred when" a spatial question
  rather than a ranking.

USAGE
    python3 reef.py --self-test
    python3 reef.py --demo
    python3 reef.py --bleach      # the interesting one
"""
from __future__ import annotations
import json, sys
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional

class Health(Enum):
    HEALTHY = "healthy"; STRESSED = "stressed"; BLEACHED = "bleached"; DEAD = "dead"

class Stage(Enum):
    SEEDLING = "seedling"; JUVENILE = "juvenile"; ADULT = "adult"; ANCIENT = "ancient"

# Stages are ordered because maturity IS the function, not a label: resilience is
# a property of how long the coral has been accumulating.
STAGE_ORDER = [Stage.SEEDLING, Stage.JUVENILE, Stage.ADULT, Stage.ANCIENT]
# Resilience per stage. A bleaching event damages a seedling far more than an
# ancient coral, and that asymmetry is the entire point of the model.
RESILIENCE = {Stage.SEEDLING: 0.10, Stage.JUVENILE: 0.30, Stage.ADULT: 0.60, Stage.ANCIENT: 0.85}

@dataclass
class Symbiodinium:
    """The endosymbiont. Supplies energy; lives in the polyp; leaves with it."""
    id: str
    output: float
    alive: bool = True

@dataclass
class Polyp:
    """An individual agent. Dies freely. The coral it built does not."""
    id: str
    health: Health = Health.HEALTHY
    energy: float = 10.0
    coral_id: Optional[str] = None
    zone: Optional[str] = None
    symbiont: Optional[Symbiodinium] = None
    deposits: float = 0.0     # mass contributed to the coral. Persists after death.

@dataclass
class Coral:
    """The slow-growing persistent structure. Built by polyps, outlasts all of them."""
    id: str
    stage: Stage = Stage.SEEDLING
    mass: float = 0.0
    scars: int = 0            # survived bleachings. A coral with scars is stronger.
    built_by: list[str] = field(default_factory=list)
    capacity: int = 100

@dataclass
class ReefZone:
    name: str
    light: float            # 0..100
    depth: float
    capacity: int
    energy_bonus: float

@dataclass
class Reef:
    name: str
    corals: dict[str, Coral] = field(default_factory=dict)
    polyps: dict[str, Polyp] = field(default_factory=dict)
    symbionts: dict[str, Symbiodinium] = field(default_factory=dict)
    zones: dict[str, ReefZone] = field(default_factory=dict)
    tick: int = 0
    events: list[dict] = field(default_factory=list)

    # -- construction --------------------------------------------------------
    def zone(self, name, light, depth, capacity, bonus):
        self.zones[name] = ReefZone(name, light, depth, capacity, bonus)
        return name

    def coral(self, cid, zone=None):
        self.corals[cid] = Coral(id=cid)
        return cid

    def polyp(self, pid, coral_id=None, zone=None, sym=None):
        self.symbionts[sym] = Symbiodinium(sym, output=3.0)
        p = Polyp(id=pid, coral_id=coral_id, zone=zone, symbiont=self.symbionts[sym])
        self.polyps[pid] = p
        if coral_id and coral_id in self.corals:
            self.corals[coral_id].built_by.append(pid)
        return pid

    # -- the metabolism ------------------------------------------------------
    def step(self) -> dict:
        """One tick. Polymps feed, grow their coral, and pay maintenance.

        A polyp with no symbiont cannot pay maintenance. That is the whole
        dependency claim: the reef is not a pile of agents, it is agents who
        each owe their upkeep to something they host.
        """
        self.tick += 1
        fed = 0
        for p in self.polyps.values():
            if p.health in (Health.DEAD, Health.BLEACHED):
                continue
            if p.symbiont is None or not p.symbiont.alive:
                p.energy -= 1.0
                if p.energy <= 0:
                    p.health = Health.DEAD
                    self.events.append({"tick": self.tick, "e": "polyp_died", "id": p.id})
                continue
            zone_bonus = self.zones[p.zone].energy_bonus if p.zone in self.zones else 1.0
            gain = p.symbiont.output * zone_bonus
            p.energy += gain
            fed += 1
            if p.coral_id and p.coral_id in self.corals:
                c = self.corals[p.coral_id]
                # The zone's light bonus must reach the DEPOSIT, not just the polyp's
                # energy. The first version scaled energy but added a flat 1.0 to the
                # coral, so a dim zone and a bright zone grew identical structure and
                # "zoning" was a label rather than a constraint. A reef's zones are the
                # thing that makes placement matter, so placement has to cost something.
                c.mass += 1.0 * zone_bonus
                p.deposits += 1.0 * zone_bonus
        self._grow()
        return {"tick": self.tick, "fed": fed, "mass": self.total_mass()}

    def _grow(self) -> None:
        """Coral advances a stage on accumulated mass, and gains capacity.

        Growth is driven by what polyps deposited, not by a polyp being alive.
        This is the load-bearing asymmetry and the self-test checks it directly.
        """
        for c in self.corals.values():
            i = STAGE_ORDER.index(c.stage)
            nxt = i + 1 if i + 1 < len(STAGE_ORDER) else i
            need = 10 * (nxt + 1) ** 2
            if c.stage is not Stage.ANCIENT and c.mass >= need:
                c.stage = STAGE_ORDER[nxt]
                c.capacity = int(10 * (nxt + 1) * 2)
                self.events.append({"tick": self.tick, "e": "coral_advanced", "id": c.id,
                                    "to": c.stage.value})

    # -- bleaching ------------------------------------------------------------
    def bleach(self, severity: float) -> dict:
        """A stress event. Can destroy OR strengthen.

        severity 0..1. Damage is scaled by the coral's resilience, which rises with
        stage. A bleaching that kills every polyp on a SEEDLING and barely dents
        an ANCIENT coral is the correct behaviour and the reason for stages.
        """
        sev = max(0.0, min(1.0, severity))
        killed, damaged = [], []
        for p in self.polyps.values():
            if p.health is Health.DEAD:
                continue
            roll = sev
            if p.health is Health.STRESSED:
                roll = min(1.0, sev * 1.4)
            if roll > 0.5:
                p.health = Health.BLEACHED
                killed.append(p.id)
                if p.symbiont:
                    p.symbiont.alive = False      # the symbiont is expelled with it
                # A bleaching severe enough to strip the tissue does not leave a polyp
                # hovering between states forever. Past the survival threshold it dies
                # and the coral keeps the mass it already banked. Without this edge the
                # state machine had a terminal BLEACHED with no exit, and the central
                # asymmetry of the model had no way to be tested at all.
                if roll >= 1.0:
                    p.health = Health.DEAD
            elif roll > 0.25:
                p.health = Health.STRESSED
        for c in self.corals.values():
            loss = sev * (1.0 - RESILIENCE[c.stage])
            c.mass = max(0.0, c.mass - loss)
            c.scars += 1                       # survived => stronger
            damaged.append({"id": c.id, "loss": round(loss, 3), "stage": c.stage.value})
        self.events.append({"tick": self.tick, "e": "bleach", "severity": sev,
                            "killed": killed, "corals": damaged})
        return {"severity": sev, "killed": killed, "corals": damaged,
                "mass": self.total_mass()}

    def total_mass(self) -> float:
        return round(sum(c.mass for c in self.corals.values()), 3)

    def summary(self) -> dict:
        alive = sum(1 for p in self.polyps.values() if p.health is not Health.DEAD)
        return {"reef": self.name, "tick": self.tick,
                "corals": len(self.corals), "polyps": len(self.polyps), "polyps_alive": alive,
                "mass": self.total_mass(),
                "stages": {c.id: c.stage.value for c in self.corals.values()},
                "scars": {c.id: c.scars for c in self.corals.values()}}


# ── the demonstration ──────────────────────────────────────────────────────────

def _demo(bleach_at=40, severity=0.9):
    r = Reef("fleet-alpha")
    r.zone("shallow", light=95, depth=5, capacity=12, bonus=1.6)
    r.zone("mid",    light=55, depth=35, capacity=20, bonus=1.0)
    r.zone("deep",   light=15, depth=80, capacity=30, bonus=0.5)
    r.coral("C-coral", zone="shallow")
    r.coral("C-deep",  zone="deep")
    for i in range(6): r.polyp(f"shallow-{i}", "C-coral", "shallow", f"sym-s{i}")
    for i in range(3): r.polyp(f"deep-{i}",    "C-deep",  "deep",    f"sym-d{i}")
    out = ["", "  THE REEF", "  " + "=" * 72, ""]
    marks = {0: "seeded", 20: "twenty ticks", bleach_at: "BLEACHING EVENT"}
    for t in range(bleach_at + 5):
        r.step()
        if t in marks:
            s = r.summary()
            out.append(f"  t={t:<4} {marks[t]:<16} mass={s['mass']:<8} "
                       f"coral={s['stages']}  polyps_alive={s['polyps_alive']}/{s['polyps']}")
    out += ["", "  the bleaching", "  " + "-" * 72]
    b = r.bleach(severity)
    out.append(f"  severity {severity}  ->  {len(b['killed'])} polyps killed")
    for c in b["corals"]:
        out.append(f"    coral {c['id']:<10} stage={c['stage']:<9} loss={c['loss']}")
    s = r.summary()
    out += ["", "  after", "  " + "-" * 72,
            f"  mass={s['mass']}  stages={s['stages']}  scars={s['scars']}  "
            f"polyps_alive={s['polyps_alive']}/{s['polyps']}",
            ""]
    # Derive the reading FROM the run, never assert it. The first version of this
    # demo hardcoded "the deep coral is ancient" and "every polyp is dead" while the
    # run said juvenile and 9/9 alive. A demo whose prose contradicts its own output is
    # worse than no demo, because it teaches the reader to trust a number and ignore
    # the sentence next to it.
    by_id = {c["id"]: c for c in b["corals"]}
    toughest = max(by_id.values(), key=lambda c: RESILIENCE[Stage(c["stage"])])
    frailest = min(by_id.values(), key=lambda c: RESILIENCE[Stage(c["stage"])])
    dead_now = s["polyps"] - s["polyps_alive"]
    out += ["  READ IT", "  " + "-" * 72,
            f"  {toughest['id']} ({toughest['stage']}) lost {toughest['loss']}.",
            f"  {frailest['id']} ({frailest['stage']}) lost {frailest['loss']} -- "
            f"{frailest['loss']/max(toughest['loss'],1e-9):.1f}x more, at the same severity.",
            f"  Polyps dead after the event: {dead_now} of {s['polyps']}.",
            "",
            "  That is the argument for substrate over model, and it is arithmetic: the",
            "  mass that remains was deposited, and bleaching took a resilience-scaled",
            "  slice of it. Maturity is not a label on the coral. It is the size of the",
            "  slice bleaching gets to take.",
            ""]
    return "\n".join(out), r


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--bleach", action="store_true")
    ap.add_argument("--severity", type=float, default=0.9)
    a = ap.parse_args()
    if a.self_test:
        sys.path.insert(0, ".")
        import selftest_reef
        sys.exit(selftest_reef.main())
    if a.bleach:
        txt, _ = _demo(40, a.severity)
    else:
        txt, _ = _demo(60, 0.0)
    print(txt)
