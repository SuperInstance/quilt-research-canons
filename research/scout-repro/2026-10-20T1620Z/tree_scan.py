import json, os, sys, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

TOKEN = os.environ['GITHUB_TOKEN']
cands = json.load(open('candidates.json'))
OUT = open('trees.jsonl','a')
lock = threading.Lock()
done = [0]
H = {'Authorization':'Bearer '+TOKEN,'Accept':'application/vnd.github+json','User-Agent':'scout'}

CODE_EXT = {'.py','.js','.mjs','.cjs','.ts','.tsx','.jsx','.rs','.go','.c','.h','.cc','.cpp','.hpp',
 '.sh','.bash','.rb','.php','.java','.swift','.m','.mm','.jl','.scala','.kt','.cs','.lua','.zig',
 '.ex','.exs','.hs','.ml','.r','.dart','.vue','.svelte','.sql','.pl','.nim','.v','.clj','.f90','.rs.in'}
DOC_EXT = {'.md','.txt','.rst','.adoc','.pdf','.org'}
VENDOR_PAT = ('/node_modules/','/vendor/','/third_party/','/thirdparty/','/target/','/.git/','/dist/',
              '/build/','/__pycache__/','/.venv/','/venv/','/site-packages/','/deps/','/external/','/Pods/')
TEST_PAT = ('test','spec','_test.','tests/','/tests/','/spec/','/test_','_spec.')

def get(url, tries=3):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers=H)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (403,429):
                time.sleep(5*(t+1)); continue
            if e.code == 404: return None
            if e.code == 409: return {'__conflict__':True}
            time.sleep(2)
        except Exception:
            time.sleep(2)
    return None

def scan(r):
    name = r['full_name'].split('/',1)[1]
    br = r['default_branch'] or 'main'
    d = get("https://api.github.com/repos/%s/git/trees/%s?recursive=1" % (r['full_name'], urllib.parse.quote(br,safe='')))
    rec = {'name':name,'api_size':r['size'],'pushed':r['pushed_at'],'archived':r['archived'],
           'desc':r.get('description'),'default_branch':br}
    if d is None:
        rec['error']='tree_fetch_failed'
    elif d.get('__conflict__'):
        rec['error']='conflict_empty_repo'
    else:
        rec['truncated'] = d.get('truncated', False)
        tr = d.get('tree',[])
        code=0; doc=0; vend=0; other=0; blobs=0; files=0
        tests=0; workflows=0; symlinks=0; gitlinks=0; exts={}
        has_readme=False; has_license=False; has_pkg=False; has_ci=False
        for e in tr:
            if e['type']=='commit':
                gitlinks+=1; continue
            if e['type']!='blob': continue
            p=e['path']; sz=e.get('size',0)
            if e.get('mode')=='120000': symlinks+=1
            blobs+=1
            low=p.lower()
            base=os.path.basename(low)
            if base.startswith('readme'): has_readme=True
            if base.startswith('license') or base.startswith('copying'): has_license=True
            if base in ('package.json','cargo.toml','pyproject.toml','go.mod','requirements.txt','setup.py','build.gradle','pom.xml','makefile','cmakelists.txt'): has_pkg=True
            if low.startswith('.github/workflows/') and (base.endswith('.yml') or base.endswith('.yaml')): workflows+=1
            ext=os.path.splitext(low)[1]
            isvend = any(v in '/'+low for v in VENDOR_PAT)
            if isvend:
                vend+=sz; continue
            if any(t in low for t in TEST_PAT): tests+=1
            if ext in CODE_EXT:
                code+=sz; exts[ext]=exts.get(ext,0)+sz
            elif ext in DOC_EXT:
                doc+=sz
            else:
                other+=sz
            files+=1
        rec.update({'blobs':blobs,'files':files,'code_bytes':code,'doc_bytes':doc,'vendored_bytes':vend,
                    'other_bytes':other,'total_bytes':code+doc+vend+other,'test_files':tests,
                    'workflows':workflows,'symlinks':symlinks,'gitlinks':gitlinks,
                    'has_readme':has_readme,'has_license':has_license,'has_manifest':has_pkg,
                    'exts':dict(sorted(exts.items(),key=lambda kv:-kv[1])[:8])})
    with lock:
        OUT.write(json.dumps(rec)+'\n'); OUT.flush()
        done[0]+=1
        if done[0]%50==0:
            print("done",done[0],"/",len(cands),flush=True)
    return rec

import urllib.parse
with ThreadPoolExecutor(max_workers=8) as ex:
    list(ex.map(scan, cands))
print("FINISHED", done[0], flush=True)
