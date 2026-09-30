#!/usr/bin/env python3
"""
the-wheel — a harness for working a corpus the way a quilt is built: SEQUENTIALLY along
a spine, PARALLELLY across angles, with the negative space mapped as a first-class output.

THE SHAPE

    spine (one item at a time, ordered by READINESS not by position)
      └── for each item, N parallel ANGLES on the same goal
            └── each angle emits CELLS
                  └── cells carry what the angle could NOT determine
                        └── the gaps become the next spine item

That last arrow is the wheel. The negative space is not a report section, it is the work
queue. An angle that cannot determine something has produced the next thing to look at.

THE ENCODING IS THE FLEET'S OWN

Every cell carries the canonical envelope (witness_id, prev_witness_id, cell_id, substrate,
polarity, timestamp, payload) so the output of this wheel is the same shape as the rest of
the substrate. A knowledge graph that is not in the substrate's own format is another
island.

VECTORISATION, HONESTLY

Cloudflare Vectorize is UNAVAILABLE on this account — it returns
`vectorize.unknown_content_type` (code 1005) for this token, and the known working
alternative is Workers KV plus in-Worker cosine for corpora under ~25MB. This module
therefore builds a local index with a swappable backend, and ships the Worker source
separately. It does not pretend to have vectorised anything it has not.

    python3 wheel.py --scan            # rank the corpus by readiness
    python3 wheel.py --cell <paper>    # emit cells for one item, all angles
    python3 wheel.py --index           # build the local index + report the negative space
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, re, time, urllib.request, urllib.error
from collections import defaultdict
from dataclasses import dataclass, field, asdict

PAPERS_REPO = "SuperInstance/SuperInstance-papers"
GH = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
H = {"Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN','')}",
     "Accept": "application/vnd.github+analytics.github+json", "User-Agent": "the-wheel/1.0"}


# ------------------------------------------------------------------ the cell
@dataclass
class Cell:
    cell_id: str
    substrate: str          # what produced this cell
    polarity: str          # SUPPORTED | CONTRADICTED | UNKNOWN | GAP
    claim: str
    evidence: str = ""     # path / line / api fact
    unmapped: str = ""     # <-- THE NEGATIVE SPACE, per cell, not per report
    edges: list = field(default_factory=list)   # cites | contradicts | corroborates | depends-on
    timestamp: str = ""
    prev_witness_id: str = ""

    def to_wire(self) -> dict:
        """The canonical envelope. Same shape as the rest of the substrate."""
        body = {k: v for k, v in asdict(self).items()
                if k not in ("cell_id", "timestamp", "prev_witness_id")}
        h = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        wid = f"wheel-{h[:16]}"
        return dict(witness_id=wid, prev_witness_id=self.prev_witness_id,
                    cell_id=self.cell_id, substrate=self.substrate,
                    polarity=self.polarity, timestamp=self.timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    payload=body)


# ------------------------------------------------------------------ the angles
ANGLES = {
  "claims":    "What does the text CLAIM, concretely and checkably?",
  "code":      "Does an artifact exist, and does the artifact do what the claim says?",
  "runnable":  "Can it be run right now, and do stored results reproduce?",
  "calibrate": "Is any number in it calibrated against realised outcomes?",
  "adversary": "What is the strongest reason this is wrong, overclaiming, or vacuous?",
  "negative":  "What CANNOT be determined from the artifact, and what would it take?",
}

# A stop word is GENERIC RELATIVE TO THE CORPUS. The original list mixed function
# words with this corpus's own vocabulary -- 'quilt', 'cell', 'architecture', 'model',
# 'system' -- and those are not generic here: they are how the fleet NAMES things.
# Filtering them made 6 of 40 papers unable to see any code that referenced them,
# which is the same class of bug as a search-mutate pool hard-wired to one wire:
# the matcher was configured so the answer could not be expressed.
STOP = {'the','of','and','a','an','for','to','in','is','are','as','on','with','by','from'}


def gh_json(path):
    try:
        with urllib.request.urlopen(urllib.request.Request(GH + path, headers=H), timeout=30) as r:
            return json.loads(r.read())
    except Exception:
        return None


def raw(path, ref="main"):
    try:
        with urllib.request.urlopen(urllib.request.Request(f"{RAW}/{PAPERS_REPO}/{ref}/{path}",
                                                           headers=H), timeout=25) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return ""


# MEASURED (2026-09-30): with the domain words in STOP, 33/40 papers had zero code
# matches; with this list, 27/40. The remaining 27 are NOT a stop-word problem --
# the filename-stem matcher is structurally unable to see an artifact filed under a
# different name, which `unmapped` already says out loud. Fixing that means reading
# the paper body for distinctive terms, not the filename. Not fixed here.
def keywords(name: str) -> list:
    stem = re.sub(r'^\d{2}-|\.md$', '', os.path.basename(name))
    ws = re.findall(r'[A-Za-z][A-Za-z0-9]{2,}', stem.replace('-', ' ').replace('_', ' '))
    return [w.lower() for w in ws if w.lower() not in STOP and len(w) > 3]


# ------------------------------------------------------------------ spine
def scan():
    t = gh_json(f"/repos/{PAPERS_REPO}/git/trees/main?recursive=1")
    if not t:
        raise SystemExit("cannot reach GitHub tree API")
    paths = [e['path'] for e in t.get('tree', []) if e['type'] == 'blob']
    code = [p for p in paths if re.search(r'\.(py|ts|js|rs|c|ex|mjs)$', p)]
    eco = [p for p in paths if 'Equipment-' in p]
    res = [p for p in paths if re.search(r'(result|output|summary).*\.(json|md)$', p, re.I)]
    papers = [p for p in paths if p.startswith('white-papers/') and p.endswith('.md')
              and re.search(r'/\d{2}-', p) and 'README' not in p
              and 'appendix' not in p.lower() and 'section' not in p.lower()]
    out = []
    for p in sorted(papers):
        kws = keywords(p)
        hit = lambda pool, n: [q for q in pool if sum(1 for k in kws if k in q.lower()) >= n]
        e, c, r = hit(eco, 1), hit(code, 2), hit(res, 1)
        a = [q for q in paths if 'appendix' in q.lower() and any(k in q.lower() for k in kws)]
        out.append(dict(path=p, name=os.path.basename(p), ecosystem=e[:3], code=c[:3],
                        results=r[:2], appendix=len(a),
                        score=5*len(e)+3*len(c)+6*len(r)+2*len(a)))
    out.sort(key=lambda d: -d['score'])
    return out


# ------------------------------------------------------------------ angles -> cells
def cells_for(item):
    """Six angles on one item. Each may produce SUPPORTED, CONTRADICTED or GAP.
    A GAP is a first-class output, not a failure: it seeds the next spine item."""
    name, path = item['name'], item['path']
    body = raw(path)
    cid = re.sub(r'[^a-z0-9]+', '-', name.lower().replace('.md', ''))[:48]
    cs, prev = [], ""

    def add(sub, pol, claim, ev="", unmapped="", edges=None):
        nonlocal prev
        c = Cell(cid, sub, pol, claim, ev, unmapped, edges or [], prev_witness_id=prev)
        cs.append(c); prev = c.to_wire()["witness_id"]; return c

    add("claims", "SUPPORTED" if body else "UNKNOWN",
        f"paper body retrieved: {len(body)} bytes" if body else "paper body NOT retrievable",
        path)

    for label, pool, n in (("attached repo", item['ecosystem'], 1),
                           ("code", item['code'], 2),
                           ("stored results", item['results'], 1)):
        if pool:
            add("code", "SUPPORTED", f"{label} exists ({len(pool)} match)",
                pool[0], edges=["depends-on"])
        else:
            add("code", "GAP", f"no {label} matched this paper's distinctive keywords",
                unmapped=f"cannot tell whether a {label} exists under a different name; "
                         f"needs a human or a full-tree read to settle")

    has_any = bool(item['ecosystem'] or item['code'] or item['results'] or item['appendix'])
    if not has_any:
        add("negative", "GAP",
            "this paper has NO attached artifact of any kind",
            unmapped="nothing to run, nothing to diff, no stored result to reproduce. "
                     "This item is a WRITE task, not a PRESS task, and no tooling can change that")

    if not body:
        add("runnable", "UNKNOWN", "body unavailable, so nothing could be run",
            unmapped="the raw.githubusercontent fetch failed — may be size, ref, or rate limit")

    if item['results']:
        add("adversary", "UNKNOWN",
            f"stored results exist ({len(item['results'])}) but were not re-run here",
            item['results'][0],
            unmapped="reproducing stored results is the highest-information check and it was "
                     "NOT performed by this pass")
    return cs


# ------------------------------------------------------------------ index + negative space
def build_index(cells):
    """Local index. A swappable backend standing in for a vector store we do not have."""
    docs = [c.to_wire() for c in cells]
    # bag-of-words vectors, unit-normalised, cosine by dot product
    vocab = sorted({w for d in docs for w in re.findall(r'[a-z]{3,}', json.dumps(d).lower())})
    idx = {w: i for i, w in enumerate(vocab)}
    vecs = []
    for d in docs:
        v = [0.0] * len(vocab)
        for w in re.findall(r'[a-z]{3,}', json.dumps(d).lower()):
            v[idx[w]] += 1.0
        n = math.sqrt(sum(x*x for x in v)) or 1.0
        vecs.append([x/n for x in v])
    return docs, vocab, vecs


def search(docs, vocab, vecs, query, k=5):
    v = [0.0]*len(vocab)
    for w in re.findall(r'[a-z]{3,}', query.lower()):
        if w in vocab: v[vocab.index(w)] += 1.0
    n = math.sqrt(sum(x*x for x in v)) or 1.0
    v = [x/n for x in v]
    scored = sorted(((sum(a*b for a, b in zip(vec, v)), d) for vec, d in zip(vecs, docs)),
                    key=lambda t: -t[0])[:k]
    return scored


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--cell", type=str)
    ap.add_argument("--index", action="store_true")
    ap.add_argument("--query", type=str)
    ap.add_argument("--limit", type=int, default=8)
    a = ap.parse_args()
    items = scan()

    if a.scan or (not a.cell and not a.index and not a.query):
        print(f"\n  THE WHEEL — spine, {len(items)} papers, ordered by READINESS not position")
        print("  " + "="*84)
        for i, it in enumerate(items[:a.limit], 1):
            tag = ("press" if it['score'] >= 20 else
                   "thin" if it['score'] > 0 else "WRITE — no artifact at all")
            print(f"  {i:>2}. [{tag:22}] {it['name'][:44]:44} score={it['score']}")
        n0 = sum(1 for it in items if it['score'] == 0)
        print(f"\n  {n0} of {len(items)} papers have no attached artifact of any kind.")
        print("  For those the wheel cannot help. They are write-tasks, and that is the")
        print("  single most useful thing the negative-space map just said.")
        return 0

    if a.cell:
        item = next((i for i in items if a.cell.lower() in i['name'].lower()), None)
        if not item:
            print("  no such paper:", a.cell); return 2
        cs = cells_for(item)
        print(f"\n  {item['name']} — {len(cs)} cells across {len(ANGLES)} angles")
        print("  " + "="*84)
        for c in cs:
            w = c.to_wire()
            print(f"  [{w['polarity']:12}] {w['substrate']:10} {c.claim[:52]}")
            if c.unmapped: print(f"       UNMAPPED: {c.unmapped[:96]}")
        os.makedirs("out", exist_ok=True)
        json.dump([c.to_wire() for c in cs], open("out/cells.json", "w"), indent=1)
        gaps = [c for c in cs if c.unmapped]
        print(f"\n  {len(gaps)} of {len(cs)} cells carry an explicit unknown -> next spine work")
        return 0

    allcells = []
    for it in items:
        allcells += cells_for(it)
    docs, vocab, vecs = build_index(allcells)
    os.makedirs("out", exist_ok=True)
    json.dump(docs, open("out/wheel_index.json", "w"), indent=1)
    with open("out/wheel_index.jsonl", "w") as f:
        for d in docs: f.write(json.dumps(d) + "\n")
    pol = defaultdict(int)
    for d in docs: pol[d['polarity']] += 1
    print(f"\n  WHEEL INDEX — {len(docs)} cells, {len(vocab)} terms, bag-of-words cosine")
    print(f"  local embedding, NOT a vector database. Cloudflare Vectorize is")
    print(f"  unavailable on this account (1005 unknown_content_type).")
    print("  " + "="*84)
    for p, n in sorted(pol.items(), key=lambda x: -x[1]): print(f"    {p:14} {n}")
    if a.query:
        print(f"\n  QUERY: {a.query!r}")
        for s, d in search(docs, vocab, vecs, a.query):
            print(f"    {s:.3f}  [{d['polarity']:12}] {d['payload']['claim'][:60]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
