#!/usr/bin/env python3
"""features.py — shared by the trainer and the browser. ONE implementation, two runtimes.

Deliberately generic: nothing here keys on a specific claim, a specific word from the
corpus, or a band label. The model has to work on a claim it has never seen, which is
the only test that separates a model from a lookup table.
"""
import re, math

# (name, compiled pattern, weight-of-evidence sign is learned, not hard-coded)
PATTERNS = [
    ("specific_number", r"\b\d[\d,.]*\s*(?:%|ms|s|GB|MB|KB|Hz|nm|px|bits?|x)\b|\b0x[0-9a-f]{4,}|\b\d+\.\d+\b"),
    ("named_artifact",  r"`[^`]+`|\b[\w-]+\.(py|js|ts|rs|c|md|json|toml|yaml|erl|pl)\b|\b[A-Z][a-z]+[A-Z]\w+"),
    ("falsifiable",     r"\bunless\b|\bexcept\b|\bonly if\b|\bstrictly\b|\bif and only if\b|\biff\b|\bcounter-?example\b|\bprovided that\b"),
    ("universal_quant", r"\ball\b|\bevery\b|\balways\b|\bnever\b|\bany\b|\bnone\b|\beverything\b|\bno one\b"),
    ("hedge",           r"\b(probably|perhaps|might|may|could|possibly|likely|seems?|appears?|suggest(?:s|ive)?|i think\b)"),
    ("vague_praise",    r"\b(very|really|quite|extremely|highly|powerful|robust|seamless|elegant|novel|significant|substantial|excellent|great|major|effective|promising|state.of.the.art|well.known)\b"),
    ("vague_quant",     r"\b(many|most|several|various|numerous|often|generally|typically|usually|lots of|a variety)\b"),
    ("absolutist",      r"\b(guarantee(?:s|d)?|ensures?|always|never|proven|impossible|cannot (?: )?(?:be|ever))\b"),
    ("self_reference",  r"\b(our|we|this (?:paper|work|approach|method|system|repo))\b"),
    ("measured_past",   r"\b(measured|measured\b|reports?|returned|observed|computed|logged|recorded)\b|\d"),
    ("negation",        r"\b(not|no|never|cannot|without|neither|nor|fails?|un)\b"),
    ("concrete_noun",   r"\b(hash|entropy|index|gate|test|token|vector|commit|log|receipt|distribution|threshold|node|cell)\b"),
]
# re.A is REQUIRED for parity with JavaScript. Python's \b and \w are Unicode-aware on
# str patterns; JavaScript's are strictly ASCII. On a corpus containing "cafe Δ 日本語"
# the two implementations therefore counted features differently -- a 0.0165 logit gap,
# found by the two-implementation check and not by reading. re.A makes Python ASCII-only,
# which is what JS already was. The model is retrained under the corrected features.
_COMPILED = [(n, re.compile(p, re.I | re.A)) for n, p in PATTERNS]
FEATURES = [n for n, _ in _COMPILED]

def extract(text: str):
    """Return the feature vector. Pure, deterministic, dependency-free."""
    t = (text or "").strip()
    words = max(1, len(t.split()))
    x = [1.0]                                  # bias
    for _, rx in _COMPILED:
        x.append(len(rx.findall(t)) / math.sqrt(max(words, 8)))
    x.append(min(len(t), 400) / 200.0)          # length, saturating
    x.append(len(t.split()) / 20.0)             # length in words
    return x

N_FEATURES = len(_COMPILED) + 3
