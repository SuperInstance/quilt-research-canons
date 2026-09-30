#!/usr/bin/env python3
"""Upload the wheel index into Workers KV so vectorize_worker.js can serve it.

Vectorize is unavailable on this account (1005), so the corpus goes into KV and cosine
runs in the Worker. Prints exactly which steps succeeded; a partial upload that reports
success is the failure mode this script exists to avoid.
"""
import json, os, sys, urllib.request, urllib.error

TOKEN = os.environ.get("CLOUDFLARE_TOKEN", "")
ACCT = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "049ff5e84ecf636b53b162cbb580aae6")
NS = os.environ.get("WHEEL_KV_NS", "wheel_index")
SRC = sys.argv[1] if len(sys.argv) > 1 else \
    "/workspace/projects/the-wheel/out/wheel_index.jsonl"

def call(url, method="GET", body=None, raw=False):
    h = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=body if raw else
                                 (json.dumps(body).encode() if body is not None else None),
                                 headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300]
    except Exception as e:
        return 0, str(e)[:120].encode()

if not TOKEN:
    print("  CLOUDFLARE_TOKEN missing — nothing uploaded."); sys.exit(2)

docs = [json.loads(l) for l in open(SRC) if l.strip()]
vocab = sorted({w for d in docs for w in __import__("re").findall(r"[a-z]{3,}", json.dumps(d).lower())})
print(f"  {len(docs)} cells, {len(vocab)} vocab terms -> namespace {NS}")

ok = 0
st, b = call(f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/storage/kv/namespaces",
             "POST", {"title": NS})
print(f"  create namespace -> {st}")
if st not in (200, 201):
    print("   ", b[:200].decode(errors="replace")); sys.exit(2)
nsid = (json.loads(b).get("result") or {}).get("id")

base = f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/storage/kv/namespaces/{nsid}/values"
st, _ = call(f"{base}/__vocab", "PUT", {"words": vocab}, raw=True)
print(f"  vocab -> {st}")
ok += st in (200, 201)
for i, d in enumerate(docs):
    st, _ = call(f"{base}/{i:06d}", "PUT", d, raw=True)
    if st in (200, 201): ok += 1
    if i % 50 == 0: print(f"    {i}/{len(docs)}")
print(f"  uploaded {ok}/{len(docs) + 1} values. namespace id: {nsid}")
print("  PARTIAL UPLOADS ARE REPORTED AS PARTIAL. Do not assume the corpus is complete.")
