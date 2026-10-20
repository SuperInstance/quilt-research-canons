import json, os, threading, urllib.request, urllib.error, time
from concurrent.futures import ThreadPoolExecutor
TOKEN=os.environ['GITHUB_TOKEN']
H={'Authorization':'Bearer '+TOKEN,'Accept':'application/vnd.github+json','User-Agent':'scout'}
recs=[json.loads(l) for l in open('trees.jsonl')]
lau=[r for r in recs if r['name'].startswith('lau-')]
def get(url,tries=3):
    for t in range(tries):
        try:
            req=urllib.request.Request(url,headers=H)
            with urllib.request.urlopen(req,timeout=30) as r: return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (403,429): time.sleep(4); continue
            if e.code==404: return None
            return {'__err':e.code}
        except Exception: time.sleep(2)
    return None
lock=threading.Lock(); out=open('lau_ci.jsonl','a')
def scan(r):
    d=get("https://api.github.com/repos/SuperInstance/%s/actions/runs?per_page=100"%r['name'])
    rec={'name':r['name'],'code_kb':r['code_bytes']//1024}
    if d is None or 'workflow_runs' not in d:
        rec['ci']='no_api'
    else:
        runs=d['workflow_runs']
        rec['runs']=len(runs)
        if not runs: rec['ci']='no_runs'
        else:
            cons=[x['conclusion'] for x in runs]
            rec['ci']=('green' if all(c=='success' for c in cons) else
                       'red' if any(c=='failure' in (c or '') for c in cons) else
                       'mixed:'+','.join(sorted(set(str(c) for c in cons))))
            rec['last']=max(x['created_at'] for x in runs)
            rec['wfs']=len(set(x['name'] for x in runs))
    with lock: out.write(json.dumps(rec)+'\n'); out.flush()
with ThreadPoolExecutor(max_workers=8) as ex: list(ex.map(scan,lau))
print("DONE")
