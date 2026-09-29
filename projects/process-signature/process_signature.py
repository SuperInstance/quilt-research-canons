#!/usr/bin/env python3
"""
process_signature.py — read a repo's SHAPE and report what PROCESS it is running.

WHY THIS EXISTS

Casey's question: study the *processes* of different agents and find novel thought
patterns in the DIFFERENCES. The fleet already contains several process archetypes and
they are not written down anywhere — they are only visible in the artifacts each one
leaves behind. A repo that pre-registers leaves a registration file. A repo that chains
witnesses leaves a JSONL with a parent field. A repo that can restore itself ships a
snapshot tool AND a bootstrap tool, which is the difference between "we survive wipes"
and "we can rebuild from each other".

So the archetype is READABLE OFF DISK. That is the claim this instrument tests.

AND THE HARD PART, WHICH IS WHY IT MATTERS

Tonight's legibility census found 55 repos that never say what they do NOT do, and 59
that never say what to do when they fail — while the receipts were the BEST-kept
obligation. That implies a class of repo that is heavily documented and barely verified,
and it implies that class is DETECTABLE without reading a word of prose. If that holds,
then "rigorous" and "well documented" can be told apart mechanically, and the whole
question of which repos deserve attention stops being a judgement call.

Eight archetypes, each keyed on an artifact that the archetype cannot exist without.
The negative control is the ninth: a synthetic repo that is all prose and no receipts
must land on NARRATIVE_FIRST and must NOT accidentally satisfy any of the eight.
"""
from __future__ import annotations
import json, re, os, sys
from dataclasses import dataclass, field

# A PATH archetype can be read off the file tree alone.
PATH_ARCHETYPES = {
    "self-hosting":        dict(what="the tool can capture or restore the whole fleet, incl. itself",
                                sig=(r"snapshot", r"bootstrap", r"restore[_-]?fleet", r"brewer", r"walk(er)?[_-]?s?")),
    "recipe-grown":        dict(what="code is emitted from a spec rather than hand-written",
                                sig=(r"recipe", r"generator", r"scaffold", r"template")),
    "contract-enforcing":  dict(what="a machine-checked schema/contract exists",
                                sig=(r"schema", r"contract")),
    "falsification-first": dict(what="the suite contains a test asserting a claim is FALSE",
                                sig=(r"falsif", r"negative[_-]?control", r"must[_-]?fail", r"inject", r"fault")),
    "externally-checkable":dict(what="a release/tag is mapped to a verifiable receipt",
                                sig=(r"release[_-]?verify", r"verify[_-]?receipt", r"provenance")),
    "single-command":      dict(what="one entry point produces an observable result",
                                sig=(r"^makefile$", r"^justfile$", r"pyproject\.toml$", r"^cli", r"bin/")),
    "pre-registered":      dict(what="predictions recorded with a number BEFORE the run",
                                sig=(r"registration", r"prereg", r"pre-?reg", r"/seal")),
    "witness-chained":     dict(what="events carry a parent, so the log cannot be edited unnoticed",
                                sig=(r"ledger\.jsonl$", r"history\.jsonl$", r"witness(es)?\.jsonl$")),
}
# A TEXT archetype can only be read from CONTENT, and guessing it from a filename is how
# a dead check acquires a name. These are reported as UNKNOWN unless text is supplied.
TEXT_ARCHETYPES = {
    "chained-fields":   dict(what="a parent/prev hash field appears in the data",
                             sig=(r'"prev_?witness', r'"prev_?hash', r'"parent_?receipt')),
    "sealed-registration": dict(what="a seal/registration record with a timestamp and a hash",
                                sig=(r'"pred_?sha256"', r'"sealed', r'"registered_?at"')),
    "negative-space":   dict(what="the docs state what the thing does NOT do",
                             sig=(r"out of scope", r"limitations", r"caveats", r"not implemented", r"does not")),
    "error-surface":    dict(what="the docs say what to do when it fails",
                             sig=(r"troubleshoot", r"common mistakes", r"gotcha", r"error", r"exception")),
    "receipt-named":    dict(what="a receipt identifier appears in the text or code",
                             sig=(r"receipt@", r"receipt_id", r"VERIFY_RECEIPT")),
}
PROSE = re.compile(r"\b(receipt|verif\w+|pre-?regist\w+|canon|witness|schema)\b", re.I)
CODE  = re.compile(r"\.(py|js|ts|c|h|rs|go|sh|mjs|cjs|erl|ex|hs)$", re.I)


@dataclass
class Signature:
    repo: str
    files: list = field(default_factory=list)
    n_files: int = 0
    n_code: int = 0
    n_docs: int = 0
    n_tests: int = 0
    n_ci: int = 0
    n_license: int = 0
    n_jsonl: int = 0
    path_hits: dict = field(default_factory=dict)
    text_hits: dict = field(default_factory=dict)
    text_supplied: bool = False

    def path_archetypes(self):
        return sorted(self.path_hits)

    def text_archetypes(self):
        return sorted(self.text_hits) if self.text_supplied else []

    def unknown(self):
        """Archetypes that CANNOT be judged from a tree. Reported as unknown rather than
        assumed absent -- an unmeasured thing is not a missing thing."""
        return sorted(set(TEXT_ARCHETYPES) - set(self.text_hits)) if self.text_supplied else sorted(TEXT_ARCHETYPES)

    def grade(self):
        """A PROCESS grade. It answers 'what process is this repo running' and refuses to
        answer 'is it good'. Graded on PATH evidence only, so it is reproducible from a
        tree listing with no content fetch."""
        a = set(self.path_archetypes())
        if {"falsification-first", "witness-chained"} <= a: return "SELF-AUDITING"
        if {"pre-registered", "witness-chained"} <= a:   return "PRE-REGISTERED+CHAINED"
        if {"externally-checkable", "self-hosting"} & a:  return "PUBLISHABLE"
        if {"witness-chained", "contract-enforcing"} & a: return "RECEIPTED"
        if a: return "PROCESS-PRESENT-UNCLASSIFIED"
        if self.n_code > 0 or self.n_docs > 0: return "NARRATIVE-FIRST"
        return "EMPTY"

    def gap(self):
        miss = []
        if not self.n_ci:      miss.append("no CI")
        if not self.n_license: miss.append("no LICENSE")
        if not self.n_tests:   miss.append("no tests")
        if not self.n_jsonl:   miss.append("no append-only ledger (.jsonl)")
        return miss


def signature(repo: str, files: list, text: str = "") -> Signature:
    s = Signature(repo=repo, files=list(files), n_files=len(files))
    low = [f.lower() for f in files]
    for name, spec in PATH_ARCHETYPES.items():
        hits = [f for f in low for p in spec["sig"] if re.search(p, f)]
        if hits:
            s.path_hits[name] = hits[:3]
    s.n_docs = sum(1 for f in low if f.endswith((".md", ".rst", ".txt")))
    s.n_code = sum(1 for f in low if CODE.search(f))
    s.n_tests = sum(1 for f in low if re.search(r"(^|/)(test|tests|spec)/|_test\.|\.test\.|_spec\.", f))
    s.n_ci = sum(1 for f in low if f.startswith(".github/workflows/") or f in ("jenkinsfile", ".gitlab-ci"))
    s.n_license = sum(1 for f in low if re.match(r"^(license|copying)", f))
    s.n_jsonl = sum(1 for f in low if f.endswith(".jsonl"))
    s.text_supplied = bool(text)
    if text:
        for name, spec in TEXT_ARCHETYPES.items():
            if any(re.search(p, text, re.I) for p in spec["sig"]):
                s.text_hits[name] = True
    return s


def all_prose_nor_receipts():
    """THE NEGATIVE CONTROL. Real code, real prose, plenty of it -- and none of the
    process artifacts. It must grade NARRATIVE-FIRST.

    This is the hypothesis under test from the legibility census: a repo can be well
    documented and barely verified, and that class should be MECHANICALLY separable
    rather than a judgement call.
    """
    prose = (
        "# A Design\n\n"
        "We have a receipt for every cell. The canon is verified. Each witness is sealed.\n"
        "Our schema is enforced. See also our pre-registration.\n"
        "Limitations: this is a proposal, not implemented.\n"
        "Troubleshooting: if you see an error, read the docs.\n"
    )
    return signature(
        repo="synthetic-heavy-prose-no-process",
        files=["README.md", "DESIGN.md", "ARCHITECTURE.md", "NOTES.md", "ROADMAP.md",
               "doc/one.md", "doc/two.md", "doc/three.md",
               "src/engine.py", "src/codec.py", "src/view.py"],
        text=prose)


def fully_processed():
    """THE POSITIVE CONTROL. The same prose, PLUS the artifacts each archetype needs."""
    prose = (
        "# A Design\n\n"
        "`make verify` prints a receipt.\n"
        "## Limitations\nNot implemented on Windows.\n"
        "## Troubleshooting\nIf you see a 4xx the schema is wrong.\n"
        + json.dumps({"pred_sha256": "ab", "sealed": "2026-01-01"}) + "\n"
        + json.dumps({"prev_witness": "00", "receipt_id": "r-1", "VERIFY_RECEIPT": True}) + "\n"
    )
    return signature(
        repo="synthetic-fully-processed",
        files=["README.md", "Makefile", "LICENSE", "tests/test_injection.py",
               ".github/workflows/ci.yml", "lode/registration.jsonl",
               "fleet/witnesses.jsonl", "tools/release_verify.mjs", "schema/cell.schema.json",
               "src/engine.py"],
        text=prose)


if __name__ == "__main__":
    print()
    print("  PROCESS SIGNATURE — what process is this repo RUNNING, read off its shape?")
    print("  " + "=" * 60)
    a = all_prose_nor_receipts()
    b = fully_processed()
    print(f"\n  NEGATIVE CONTROL (all prose, no process artifacts):")
    print(f"    grade      : {a.grade()}")
    print(f"    path ev.   : {a.path_archetypes() or 'none'}")
    print(f"    text ev.   : {a.text_archetypes() or 'none'}")
    print(f"    gap        : {a.gap()}")
    ok_neg = a.grade() == "NARRATIVE-FIRST"
    print(f"    -> must be NARRATIVE-FIRST with no path evidence: {ok_neg}")
    print(f"\n  POSITIVE CONTROL (same prose PLUS the artifacts):")
    print(f"    grade      : {b.grade()}")
    print(f"    path ev.   : {b.path_archetypes()}")
    print(f"    text ev.   : {b.text_archetypes()}")
    print(f"    gap        : {b.gap() or 'none'}")
    ok_pos = b.grade() in ("SELF-AUDITING", "PRE-REGISTERED+CHAINED", "PUBLISHABLE", "RECEIPTED")
    print(f"    -> must clear the archetypes: {ok_pos}")
    print()
    print(f"  BOTH CONTROLS BEHAVED CORRECTLY: {ok_neg and ok_pos}")
    print()
    print("  The gap between those two grades is the whole instrument: a repo can")
    print("  describe a rigorous process in prose and still leave no trace of running one.")
    print()
    sys.exit(0 if (ok_neg and ok_pos) else 2)
