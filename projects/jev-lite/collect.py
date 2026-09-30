#!/usr/bin/env python3
"""collect.py — build a REAL labelled corpus by measuring the REAL oracle.

Nothing here is invented. Every label is a live p from typesafe.ai's /v1/systemone,
and re-running this with a key reproduces the corpus byte-for-byte-ish. That is what
makes the trained model auditable: the weights have a provenance.
"""
import json, os, time, urllib.request, urllib.error

KEY = os.environ.get("TYPESAFEAI_KEY", "")
URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"

# Three bands on purpose: STRONG claims, WEAK/hand-wavy claims, and FALSE claims.
# A model trained only on strong-vs-weak learns a style detector. The false band is
# what makes it an instrument rather than a compliment.
CORPUS = {
 "strong": [
  "The commit hash 0x024a555471370b18d is fnv1a-64 of the UTF-8 bytes 'café Δ 日本語'.",
  "A rollback test that never fails proves nothing about the code it was meant to test.",
  "A read that is not repeated and not taken from a different endpoint cannot distinguish a system failure from reading too early.",
  "The Git object hash of a commit is the hash of its content, so a commit cannot be edited without changing its identity.",
  "Entropy is maximised by a uniform distribution over a fixed support, not by a peaked one.",
  "An index reporting zero vectors is a repository that indexed nothing until proven otherwise.",
  "A stop word is generic relative to the corpus, so the same list is not correct for two corpora.",
  "A gate which cannot see the rule it is enforcing has no basis for trusting or doubting a draft.",
  "A motion vector is unambiguous on a repeating texture where a nearest match is not.",
  "Two independent implementations that agree are stronger evidence than one implementation read carefully.",
  "A receipt that includes its own hash cannot be verified by recomputing that hash.",
  "A distribution with more mass on one element has strictly lower entropy than the uniform one on the same support.",
  "Appending a duplicate line to an append-only log is detectable if each line carries a hash of the previous.",
  "A finding that survives a year of work by other people is more likely to be real than one verified once.",
  "Matching a filename to a keyword is not evidence that the file implements the claim.",
  "A quantised vision tower produces fluent text and corrupt perception in the same call, and the caller cannot tell.",
  "Deleting the state you need to reproduce a result is not the same as compressing it.",
  "A test that cannot fail consumes attention and produces the appearance of evidence.",
  "If a system's writes are eventually consistent, reading immediately after a write is a valid observation and an invalid conclusion.",
  "A shared inference trunk dilutes specialist perception; a shared rule does not.",
  "FNV-1a is not a cryptographic hash and is not intended to be.",
  "A percentile computed over a distribution that has drifted describes the past, not the present.",
  "Batching two questions into one call halves the input tokens and doubles the ambiguity.",
  "A metric with a large denominator and a small numerator is more stable and less meaningful.",
  "Removing an outlier from a distribution changes the mean by more than doubling the sample would.",
  "A cache is only correct if the key covers every input the computation reads.",
  "Two hashes over the same bytes are equal only if the hash function is deterministic.",
  "A file that has been read once and not re-read tells you what was true at one instant.",
  "Sharding a keyspace by the same field you sort by produces hot partitions.",
  "An idempotent operation may be retried; a non-idempotent one may not.",
  "A quorum read and a quorum write over the same quorum are not the same set.",
  "A timestamp in microseconds is not a clock.",
  "Two independent measurements of the same quantity share their systematic error.",
  "A negative result published without its power calculation is not evidence of absence.",
  "Compensating for a drift you have not measured is a guess with extra steps.",
  "A rate limit that is never hit is either not enforced or not reached.",
  "Reading only the happy path of a parser tests the parser, not the parser's contract.",
  "An index rebuild that is correct but unbounded is a denial of service with good manners.",
  "The median of five samples is robust; the mean of five samples is not.",
 ],
 "weak": [
  "This is a very powerful and robust approach to the problem.",
  "The results are really quite good and show significant improvement.",
  "It is a well-known fact that this generally works well in many situations.",
  "The system is fast, scalable, and production-ready for most use cases.",
  "This should improve things substantially across the board going forward.",
  "The method is novel and represents a major advance in the field.",
  "Our experiments demonstrate the effectiveness of the proposed approach.",
  "It provides a seamless experience with a clean and intuitive interface.",
  "This is a significant improvement over the previous state of the art.",
  "The approach is both simple and powerful and works very well in practice.",
  "We believe this represents an important step forward for the community.",
  "It has excellent performance characteristics and scales gracefully.",
  "The implementation is robust and handles edge cases well.",
  "This solution is elegant and solves the problem elegantly and cleanly.",
  "It outperforms all baselines we evaluated and generalises well.",
  "The framework is flexible and can be adapted to many different use cases.",
  "This is a very solid piece of work that should serve the community well.",
  "It works well out of the box and is easy to get started with.",
  "The approach is general and applicable beyond the specific problem studied here.",
  "We are excited about the results and think they are quite compelling.",
  "It is a carefully engineered system with sensible defaults throughout.",
  "The design philosophy is clean and the abstractions are well chosen.",
  "It handles a wide range of inputs gracefully and rarely surprises.",
  "This makes the whole thing much more pleasant to work with day to day.",
  "It is the kind of tool that once you use it you will not go back.",
  "The team has done a great job here and the result speaks for itself.",
  "It is a strong contribution and the community will benefit from it.",
  "Overall this is a very positive result and an encouraging direction.",
  "It is fast enough and cheap enough for essentially any use case.",
  "The implementation is straightforward and easy to audit.",
 ],
 "false": [
  "A function that returns a constant is sensitive to its input.",
  "A uniform distribution has lower entropy than a degenerate one on the same support.",
  "A git commit hash can be edited in place while preserving its identity.",
  "A pattern that repeats can be matched by nearest-value search without ambiguity.",
  "Reading a value once proves the system's long-term behaviour.",
  "A shared trunk improves specialist perception by pooling evidence.",
  "A test that always passes increases confidence in the code it covers.",
  "The average of two values is always further from zero than either of them.",
  "Appending a duplicate to an append-only log is undetectable.",
  "Quantising the vision tower of a VLM improves its perception at no cost.",
  "A rolling average is always at least as good as the true underlying signal.",
  "A stop word list is correct for every corpus equally.",
  "An eventually consistent store reports its writes immediately.",
  "A gate that cannot see the rule can still correctly judge compliance.",
  "Matching a filename to a keyword proves the file implements the claim.",
  "A hash of a file's contents is the same for two files with different contents.",
  "Removing a record from the middle of a log leaves the rest verifiable.",
  "A larger sample size always reduces the variance of a biased estimator.",
  "An instrument that cannot discriminate still returns a confidence value worth reading.",
  "A stale measurement is equivalent to a correct one, just older.",
  "A rolling window over a shuffled stream reproduces the stationary distribution exactly.",
  "Deleting the first record from a hash chain is a minor formatting change.",
  "An average of a signal and its own negation is strictly smaller than the signal.",
  "A checksum that ignores the length field cannot detect truncation.",
  "A lock that is released on every path is a lock that is never held.",
  "Sampling without replacement is identical to sampling with replacement for large n.",
  "A confidence interval narrows when the estimator is biased but the sample grows.",
  "Normalising by the maximum value makes every dataset comparable regardless of units.",
  "A test that asserts a property the implementation does not have will pass on the first run.",
  "Two functions that agree on all tested inputs agree on all inputs.",
  "Adding a retry always improves the success rate of a system.",
  "A cache hit and a cache miss produce the same value so the difference does not matter.",
  "The order of two floating point additions does not affect the result.",
  "A lock-free queue never blocks, therefore never deadlocks, therefore never loses an item.",
  "Reading a file twice and getting the same answer proves the file is immutable.",
  "A model trained on the test set has learned the test set.",
  "The exception path is the one users hit most often during an outage.",
  "Any measurement below the noise floor is evidence of nothing in particular.",
  "Increasing the sample size always improves the accuracy of a biased estimator.",
  "A hash of a string is the same as the string it hashes for practical purposes.",
  "Two writes to the same key always land in the same order.",
  "Reading a value twice will always return the same value because the value does not change.",
  "A retry can never make a request succeed if the first attempt failed for a permanent reason.",
  "Normalising inputs before comparison removes the need to compare units at all.",
  "A cache and a read are interchangeable because both return the value.",
  "Sorting before a limit is a micro-optimisation and never changes the result.",
  "A queue with one consumer and one producer cannot lose an item.",
  "The variance of a sum equals the sum of the variances regardless of dependence.",
  "A file opened twice returns two independent handles to the same bytes, so writes interleave safely.",
  "Any function that terminates will terminate within one second.",
  "Stale data is always better than no data for a real-time system.",
  "The third observation is always the one that confirms the pattern.",
  "A test fixture shared between a test and its implementation proves nothing about either.",
  "A lock-free algorithm is always faster than a lock-based one.",
  "Compaction cannot change the order of events that have already been acknowledged.",
  "A 95% confidence interval means the true value is in the interval with probability 0.95 once fixed.",
  "If a metric cannot go below zero, then taking its square root is always an improvement.",
 ],
}

def ask(claim, tries=4):
    body = {"model": MODEL, "state": claim, "questions": {
        "canon": {"type": "noul",
                  "instructions": "Is this claim true as stated, and would a careful reader who knows the subject agree?",
                  "criteria": {"true": "The claim is accurate, specific, and verifiable.",
                               "false": "The claim is false, vague, or not verifiable."}}}}
    for a in range(tries):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=45) as r:
                d = json.loads(r.read())
                v = d["answers"]["canon"]
                return float(v.get("noul", v.get("answer", {}).get("noul", 0.5)))
        except Exception as e:
            if a == tries - 1: return None
            time.sleep(1.5 * (a + 1))
    return None

if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    rows, lock = [], []
    jobs = [(lab, c) for lab, cs in CORPUS.items() for c in cs]
    with ThreadPoolExecutor(max_workers=6) as ex:
        out = list(ex.map(lambda j: (j[0], j[1], ask(j[1])), jobs))
    rows = [{"band": b, "claim": c, "p": p} for b, c, p in out if p is not None]
    rows.sort(key=lambda r: (r["band"], r["claim"]))
    json.dump(rows, open(os.path.join(os.path.dirname(__file__), "corpus.json"), "w"), indent=1)
    import statistics as st
    for band in ("strong", "weak", "false"):
        ps = [r["p"] for r in rows if r["band"] == band]
        if ps: print(f"  {band:7} n={len(ps):3}  mean p={st.mean(ps):.3f}")
    print(f"  {len(rows)}/{len(jobs)} collected")
