#!/usr/bin/env python3
"""render.py — the registry in prose, so a person can read it without a JSON parser."""
import json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
reg = json.load(open(os.path.join(HERE, "instruments.json")))

out = ["# The instrument registry", "",
       "*Every failure this project has found was a failure of an instrument nobody had",
       "characterised. This file exists so the next one is a known quantity.*", "",
       "> An instrument is not an instrument because it returns a number. It is an",
       "> instrument because it has been shown to return the **right** number on a case",
       "> where the right number is already known.", "",
       "Generated from `instruments.json` by `render.py`. Validate with `validate.py`.", "",
       "## The three failure classes", ""]
for k, v in reg["failure_classes"].items():
    out += [f"**`{k}`** — {v}", ""]
out += ["The first two are opposites, and you cannot tell them apart without a known-answer",
        "control. That is the whole reason the control is not optional.", ""]

insts = reg["instruments"]
out += ["## What is actually working", ""]
for i in insts:
    if i["class"] == "characterised":
        out += [f"### `{i['id']}`", "",
                f"- **used for:** {i['uses']}",
                f"- **known good:** {i['known_good']}",
                f"- **known failure:** {i.get('known_failure') or 'none measured'}",
                f"- **KAT:** `{i.get('kat')}` → **{i.get('kat_result')}**"]
        if i.get("caveat"): out += [f"- **caveat:** {i['caveat']}"]
        out += [""]
out += ["## What is quietly broken", "",
        "These all return a number. That is the problem.", ""]
for i in insts:
    if i["class"] == "BROKEN":
        out += [f"### `{i['id']}` — *{i['failure_class']}*", "",
                f"- **used for:** {i['uses']}",
                f"- **failure:** {i['known_failure']}"]
        if i.get("known_good") and i["known_good"] != "nothing found":
            out += [f"- **still good at:** {i['known_good']}"]
        if i.get("fix"): out += [f"- **fix:** {i['fix']}"]
        if i.get("residual"): out += [f"- **residual (not fixed):** {i['residual']}"]
        if i.get("caveat"): out += [f"- **caveat:** {i['caveat']}"]
        if i.get("evidence"): out += [f"- **evidence:** {i['evidence']}"]
        out += ["", f"- **KAT:** {i.get('kat_result')}"
                + ("" if not i.get("kat") else f" (`{i['kat']}`)"), ""]

c = Counter(i["class"] for i in insts)
unk = [i["id"] for i in insts if i.get("kat_result") in (None, "NONE")]
out += ["## The number that matters", "",
        f"**{len(unk)} of {len(insts)} instruments in this registry have no known-answer control.**", "",
        "That is the honest state of the fleet's measurement apparatus. It is also the whole",
        "remaining work: not more instruments, and not more findings, but **the small test",
        "that proves each existing one is telling the truth.**", "",
        "Five of the six broken entries above were found by accident, by something downstream",
        "noticing. A control turns an accident into a gate.", "",
        "## Adding an instrument", "",
        "```jsonc",
        '{ "id": "...", "class": "characterised | BROKEN | characterised-partial | proposed",',
        '  "failure_class": "context_starved | context_saturated | uncharacterised | null",',
        '  "uses": "what depends on it",',
        '  "known_good": "...", "known_failure": "...",',
        '  "kat": "path or null", "kat_result": "PASS | FAIL_* | NONE | INHERENT",',
        '  "evidence": "where the numbers are" }',
        "```", "",
        "`validate.py` fails (exit 2) if a `characterised` instrument names no KAT, if a",
        "`BROKEN` one claims a passing KAT, if a failure class is outside the three, or if a",
        "`known_failure` key is missing entirely. `validate.py --self-test` runs 6 legs",
        "including one negative control per rule.", ""]
text = "\n".join(out) + "\n"
open(os.path.join(HERE, "README.md"), "w").write(text)
print("  README.md written (%d bytes, %d instruments)" % (len(text), len(insts)))
