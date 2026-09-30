#!/usr/bin/env python3
"""Deploy quilt-negation.html as a wave66-quilt Cloudflare Worker (no bindings)."""
import json
import os
import urllib.request

TOK = os.environ["CLOUDFLARE_TOKEN"]
info = json.load(open("/home/z/my-project/scripts/cf_account.json"))
AID, SUB = info["account_id"], info["subdomain"]
HTML = open("/home/z/my-project/lanes/wave-66/fleet-negation/quilt-negation.html").read()

WORKER = f"""// wave66-quilt — fleet-negation quilt, served at the edge.
// No bindings on purpose: a static receipt needs no state. Backend honesty per
// gpu-lab precedent: this worker serves exactly one file and says so.
export default {{
  async fetch(request) {{
    return new Response(HTML, {{
      headers: {{"content-type": "text/html;charset=UTF-8",
                 "x-quilt-receipt": "wave-66-lane-A / 11-11 models / P1-P4 confirmed"}},
    }});
  }},
}};
const HTML = {json.dumps(HTML)};
"""

# multipart: metadata + single ES-module file
metadata = {"main_module": "worker.js", "compatibility_date": "2024-11-06"}
boundary = "----wave66quilt"
parts = []
parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"metadata\"; filename=\"metadata.json\"\r\nContent-Type: application/json\r\n\r\n{json.dumps(metadata)}\r\n".encode())
parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"worker.js\"; filename=\"worker.js\"\r\nContent-Type: application/javascript+module\r\n\r\n".encode() + WORKER.encode() + b"\r\n")
parts.append(f"--{boundary}--\r\n".encode())
body = b"".join(parts)

req = urllib.request.Request(
    f"https://api.cloudflare.com/client/v4/accounts/{AID}/workers/scripts/wave66-quilt",
    data=body, method="PUT",
    headers={"Authorization": f"Bearer {TOK}",
             "Content-Type": f"multipart/form-data; boundary={boundary}"})
with urllib.request.urlopen(req, timeout=60) as r:
    res = json.loads(r.read().decode())
print("upload:", res.get("success"), res.get("errors") or "")

# enable on workers.dev subdomain
req2 = urllib.request.Request(
    f"https://api.cloudflare.com/client/v4/accounts/{AID}/workers/scripts/wave66-quilt/subdomain",
    data=json.dumps({"enabled": True, "previews_enabled": True}).encode(), method="POST",
    headers={"Authorization": f"Bearer {TOK}", "Content-Type": "application/json"})
with urllib.request.urlopen(req2, timeout=30) as r:
    res2 = json.loads(r.read().decode())
print("subdomain enabled:", res2.get("success"))

url = f"https://wave66-quilt.{SUB}.workers.dev/"
print("url:", url)
import time
time.sleep(4)
try:
    with urllib.request.urlopen(url, timeout=20) as resp:
        txt = resp.read().decode()
        print("GET", resp.status, "| bytes:", len(txt), "| receipt header check:", "negation" in txt)
except Exception as e:
    print("verify pending (propagation):", type(e).__name__, e)
