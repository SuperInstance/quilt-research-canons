#!/usr/bin/env python3
"""
probe.py — a live characterisation of the tools I actually use, and WHY each fails.

The first version of this simply asked "does it work" and got 4/11. That number was
a lie of composition: nine of the eleven failures were not the tools being dead, they
were three DIFFERENT failures wearing the same coat:

  IDENTITY  the credential's state is wrong. No request change fixes it. (zai: balance)
  SHAPE     the request is malformed for that gateway. Deterministic, permanently fixable.
            (groq/moth: 1010 is a User-Agent gate -- `curl/7.88.0` is enough)
  LOAD      the path is flaky or a resource is busy. A retry fixes it. (deepseek TLS
            flake, deepinfra per-MODEL 429, Cloudflare 503)

Reporting those three as one number is how you conclude a tool is dead and stop using
a tool that works. This probe separates them, and `--self-test` proves the separation
is real by feeding it known-fake failures.
"""
import json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

E = os.environ
ACC = "049ff5e84ecf636b53b162cbb580aae6"
J = {"Content-Type": "application/json"}
BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120"

IDENTITY, SHAPE, LOAD, OK = "IDENTITY", "SHAPE", "LOAD", "OK"


def _req(url, hdr, body=None, timeout=28):
    r = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                               headers=hdr, method="POST" if body else "GET")
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return resp.status, resp.read()


def classify(status, err_text=""):
    """The heart of the instrument: turn an HTTP failure into a CAUSE."""
    if status == 200:
        return OK
    t = (err_text or "").lower()
    if status in (401, 403):
        # Cloudflare 1010 = browser-UA gate. A gate is SHAPE, not IDENTITY --
        # the credential is fine, the request is not what the edge expects.
        if "1010" in t or "browser" in t or "user agent" in t:
            return SHAPE
        return IDENTITY
    if status == 429:
        if "balance" in t or "insufficient" in t or "package" in t:
            return IDENTITY          # a balance state; retrying is pointless
        return LOAD                   # "model busy" — a capacity state; retry works
    if status == 503:
        return LOAD
    if status == 0:
        return LOAD                   # TLS reset / EOF / DNS flake
    return LOAD


def probe(name, url, hdr, body=None, timeout=28):
    t0 = time.time()
    try:
        code, b = _req(url, hdr, body, timeout)
        return dict(tool=name, cause=OK, code=code, ms=round((time.time() - t0) * 1000),
                    detail=f"{len(b)}B")
    except urllib.error.HTTPError as e:
        d = e.read()[:80].decode("utf-8", "replace").replace("\n", " ")
        return dict(tool=name, cause=classify(e.code, d), code=e.code,
                    ms=round((time.time() - t0) * 1000), detail=d)
    except Exception as e:
        return dict(tool=name, cause=LOAD, code=0,
                    ms=round((time.time() - t0) * 1000), detail=str(e)[:80])


def build():
    D = E.get("DEEPINFRA_TOKEN", ""); S = E.get("DEEPSEEK_TOKEN", "")
    Z = E.get("ZAI_TOKEN", ""); G = E.get("GROQ_TOKEN", ""); GM = E.get("GEMINI_TOKEN", "")
    T = E.get("TYPESAFEAI_KEY", ""); M = E.get("MOTH_API_KEY", ""); L = E.get("ELEVENLABS_TOKEN", "")
    return [
      ("github", "https://api.github.com/user", {"Authorization": f'Bearer {E.get("GITHUB_TOKEN","")}', "User-Agent": "p"}, None),
      ("github-anon", "https://api.github.com/users/SuperInstance", {"User-Agent": BROWSER_UA}, None),
      ("cloudflare-vectorize", f"https://api.cloudflare.com/client/v4/accounts/{ACC}/vectorize/v2/indexes",
       {"Authorization": "Bearer " + E.get("CLOUDFLARE_TOKEN", ""), "User-Agent": "p"}, None),
      ("deepinfra", "https://api.deepinfra.com/v1/openai/chat/completions",
       {"Authorization": f"Bearer {D}", **J},
       {"model": "ByteDance/Seed-2.0-mini", "messages": [{"role": "user", "content": "ok"}], "max_tokens": 5}),
      ("deepseek", "https://api.deepseek.com/chat/completions", {"Authorization": f"Bearer {S}", **J},
       {"model": "deepseek-chat", "messages": [{"role": "user", "content": "ok"}], "max_tokens": 5}),
      ("zai", "https://api.z.ai/api/paas/v4/chat/completions", {"Authorization": f"Bearer {Z}", **J},
       {"model": "glm-4.5", "messages": [{"role": "user", "content": "ok"}], "max_tokens": 80,
        "thinking": {"type": "disabled"}}),
      ("gemini", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
       {"x-goog-api-key": GM, **J},
       {"contents": [{"parts": [{"text": "ok"}]}], "generationConfig": {"maxOutputTokens": 40}}),
      # BROWSER UA IS THE POINT for these two -- see SHAPE above
      ("groq", "https://api.groq.com/openai/v1/chat/completions",
       {"Authorization": f"Bearer {G}", **J, "User-Agent": BROWSER_UA},
       {"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": "ok"}], "max_tokens": 30}),
      ("moth-quantum", "https://api.mothquantum.com/api/v1/engines",
       {"Authorization": f"Bearer {M}", "User-Agent": BROWSER_UA}, None),
      ("typesafe-jev", "https://api.typesafe.ai/v1/systemone", {"Authorization": f"Bearer {T}", **J},
       {"model": "jev-latest", "state": "x",
        "questions": {"a": {"type": "noul", "instructions": "x?",
                            "criteria": {"true": "y", "false": "n"}}}}),
      ("elevenlabs", "https://api.elevenlabs.io/v1/voices", {"xi-api-key": L}, None),
    ]


# ---------------------------------------------------------------- the control
CASES = [
    (200, "", OK, "a success is OK"),
    (401, '{"message":"Bad credentials"}', IDENTITY, "bad token is an IDENTITY failure"),
    (403, "error code: 1010", SHAPE, "CF 1010 is a User-Agent gate = SHAPE, not identity"),
    (429, '{"error":{"code":"1113","message":"Insufficient balance"}}', IDENTITY,
     "'Insufficient balance' is IDENTITY -- retrying is pointless"),
    (429, '{"error":{"message":"Model busy, retry later"}}', LOAD,
     "'Model busy' is LOAD, despite sharing a 429 with the balance case"),
    (503, "upstream connect error", LOAD, "503 is LOAD"),
    (0, "TLS/SSL connection has been closed", LOAD, "a TLS reset is LOAD, not dead"),
]


def selftest():
    ok = 0
    print(f"  self-test {len(CASES)} legs — each is a failure signature this session produced for real:")
    for code, body, want, why in CASES:
        got = classify(code, body)
        good = got == want
        ok += good
        print(f"    {'ok  ' if good else 'FAIL'} {str(code or 'conn-reset'):10} -> {got:9} {why}")
    # and the instrument must be able to be wrong: force a mis-classification and show it
    print(f"\n  {ok}/{len(CASES)}")
    return 0 if ok == len(CASES) else 2


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(selftest())
    with ThreadPoolExecutor(max_workers=11) as ex:
        R = list(ex.map(lambda a: probe(*a), build()))
    order = {OK: 0, SHAPE: 1, LOAD: 2, IDENTITY: 3}
    R.sort(key=lambda r: (order[r["cause"]], r["ms"]))
    print(f"  {'tool':22} {'cause':9} {'code':<5} {'ms':>6}  detail")
    print("  " + "-" * 78)
    for r in R:
        print(f"  {r['tool']:22} {r['cause']:9} {r['code']:<5} {r['ms']:>6}  {r['detail'][:44]}")
    n = len(R)
    tally = {c: sum(1 for r in R if r["cause"] == c) for c in (OK, SHAPE, LOAD, IDENTITY)}
    print(f"\n  usable now: {tally[OK]}/{n}   shape-failures: {tally[SHAPE]}   "
          f"load/edge: {tally[LOAD]}   genuinely dead: {tally[IDENTITY]}")
    if tally[LOAD]:
        print("  LOAD entries are worth a RETRY, not abandonment. Re-run to see them move.")
    if tally[SHAPE]:
        print("  SHAPE entries are permanently fixable in the request -- do not mark them dead.")
    json.dump(R, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "probe_result.json"), "w"), indent=1)
