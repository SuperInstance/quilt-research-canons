"""
Gate 2 — the internal-consistency linter.

Gate 1 (grounding) asks: did the artifact exist before the claim? That catches ORDER.
It does not catch a well-grounded claim that the artifact REFUTES.

The real case from the fleet, verbatim:

    headline:  "NO. None of the three implements or plans a per-cell mode menu."
    body, two clauses later:
               "That is genuinely a transmitted per-cell mode, and it is the only one
                in any of the three repos."

The receipt for that headline PREDATES the headline. Gate 1 passes it. It is still wrong,
and it is wrong in the most expensive way: a reader who stops at the lead draws the
opposite conclusion from the one the report supports.

So this gate reads a report AGAINST ITSELF. It is not a truth-checker and does not try to
be. It looks for a small number of high-signal, high-frequency shapes, and it is honest
about the fact that those shapes are a sample of the ways a report can contradict itself.

THE FOUR SHAPES, each chosen because it actually occurred

  C1  UNIVERSAL vs EXCEPTION
      A summary asserts a universal negative ("none of the three", "no repo has"),
      and the body contains a unique-existence phrase ("the only one in any of the
      three", "the only X in the fleet").

  C2  SUMMARY NUMBER NOT IN BODY
      A number appears in the summary and never anywhere in the body. A summary
      statistic that exists only in the summary is an invented statistic.

  C3  POLARITY FLIP
      The summary negates a term and the body affirms the same term in the same
      subject context ("not lossless" ... "round-trips exactly").

  C4  HEADLINE/BODY COUNT DISAGREEMENT
      The summary says "N of M" and the body says a different "N of M" for the same
      subject token.

Every check is REPORT-ONLY. None of them can prove a report is consistent; a pass means
"these four shapes were not found", which is a much smaller claim than "consistent".
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# Deliberately narrow vocabularies. A broad word list produces confident false positives,
# and a linter that cries wolf gets switched off, which is worse than no linter.
UNIVERSAL_NEG = re.compile(
    r"\b(none of|no repo|not one|neither of|no implementation of|nothing in)\b", re.I)
UNIQUE_EXIST = re.compile(
    r"\b(the only|only one|only transmitted|only repo|unique)\b", re.I)
COUNT_PAIR = re.compile(r"\b(\d+)\s+(?:of|/)\s+(\d+)\b")
NEG_TERMS = {
    "lossless": "lossless", "exact": "exactly", "monotone": "monotone",
    "preserved": "preserved", "works": "works", "valid": "valid",
}


@dataclass
class Finding:
    check: str
    line: int
    detail: str
    excerpt: str = ""

    def __str__(self) -> str:
        loc = f"L{self.line}" if self.line else "-"
        ex = f"  <- {self.excerpt[:64]!r}" if self.excerpt else ""
        return f"[{self.check}] {loc} {self.detail}{ex}"


def _lines(text: str) -> list[str]:
    return text.splitlines()


def _regions(lines: list[str]) -> tuple[list[str], list[str]]:
    """Split a report into (summary, body) STRUCTURALLY, not by counting lines.

    Calibrated against the real fleet report, whose shape is:
        # title
        metadata
        ## <first section>
        > the question
        ### Verdict: <THE HEADLINE>      <-- the headline lives UNDER the first ##
        prose
        ## <second section>              <-- body proper starts here

    So the split is the SECOND `##` when there are two or more. With exactly one, the
    first `##` is the only available boundary. With none, the document has no structure
    to read: the first 12 non-empty lines are treated as summary and the remainder as
    body. In that last case a contradiction spanning the whole document is not
    detectable, and that limitation is tested rather than hidden.
    """
    h2 = [i for i, l in enumerate(lines) if l.startswith("## ")]
    if len(h2) >= 2:
        cut = h2[1]
    elif len(h2) == 1:
        cut = h2[0]
    else:
        seen, cut = 0, len(lines)
        for i, l in enumerate(lines):
            if l.strip():
                seen += 1
                if seen > 12:
                    cut = i
                    break
    return lines[:cut], lines[cut:]


def check_universal_vs_exception(text: str) -> list[Finding]:
    summary, body = _regions(_lines(text))
    body_txt = "\n".join(body)
    out = []
    for i, l in enumerate(summary):
        if UNIVERSAL_NEG.search(l) and UNIQUE_EXIST.search(body_txt):
            m = UNIQUE_EXIST.search(body_txt)
            out.append(Finding("C1", i,
                "summary asserts a universal negative but the body claims a unique instance",
                (body_txt[max(0, m.start() - 40):m.end() + 60]).replace("\n", " ").strip()))
    return out


def check_summary_numbers_in_body(text: str) -> list[Finding]:
    summary, body = _regions(_lines(text))
    body_nums = set(COUNT_PAIR.findall("\n".join(body)))
    body_all = set(re.findall(r"\d+(?:\.\d+)?", "\n".join(body)))
    out = []
    for i, l in enumerate(summary):
        for a, b in COUNT_PAIR.findall(l):
            if (a, b) not in body_nums and a not in body_all and b not in body_all:
                out.append(Finding("C2", i,
                    f"summary statistic {a} of {b} does not appear in the body", l.strip()))
    return out


def check_polarity_flip(text: str) -> list[Finding]:
    summary, body = _regions(_lines(text))
    body_txt = "\n".join(body).lower()
    out = []
    for i, l in enumerate(summary):
        low = l.lower()
        for term in NEG_TERMS:
            if f"not {term}" in low or f"isn't {term}" in low or f"not {term}s" in low:
                if re.search(rf"\b(are|is|were|was)?\s*{term}\b", body_txt) and \
                   f"not {term}" not in body_txt:
                    out.append(Finding("C3", i,
                        f"summary negates '{term}' and the body affirms it", l.strip()))
    return out


def check_count_disagreement(text: str) -> list[Finding]:
    summary, body = _regions(_lines(text))
    summary_pairs, body_pairs = [], []
    for i, l in enumerate(summary):
        summary_pairs += [(i, m, l) for m in COUNT_PAIR.findall(l)]
    for _i, l in enumerate(body):
        body_pairs += [(_i, m) for m in COUNT_PAIR.findall(l)]
    out = []
    for i, (a, b), src in summary_pairs:
        for _, (c, d) in body_pairs:
            if a != c and b == d:
                out.append(Finding("C4", i,
                    f"summary says {a} of {b}, body says {c} of {b} for the same denominator",
                    src.strip()))
                break
    return out


CHECKS = (
    ("C1", check_universal_vs_exception),
    ("C2", check_summary_numbers_in_body),
    ("C3", check_polarity_flip),
    ("C4", check_count_disagreement),
)


class LinterCrashed(RuntimeError):
    """A check raised. This is NOT a finding -- it is the instrument failing.

    It gets its own exception type on purpose. An earlier version caught every check
    exception and appended it to the findings list, which meant a NameError in a check
    looked exactly like "this check found nothing". The linter had a silent blind spot
    and reported clean. A crash must be louder than a pass, never quieter."""


def lint(text: str, strict: bool = True) -> list[Finding]:
    findings: list[Finding] = []
    crashed = []
    for name, fn in CHECKS:
        try:
            findings.extend(fn(text))
        except Exception as e:
            crashed.append(f"{name}/{fn.__name__}: {type(e).__name__}: {e}")
    if crashed and strict:
        raise LinterCrashed(
            "consistency linter is BROKEN, its output cannot be trusted:\n  " +
            "\n  ".join(crashed))
    if crashed:
        findings.append(Finding("ERR", 0, "checks crashed: " + "; ".join(crashed)))
    return findings
