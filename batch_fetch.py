import sys, json, time, requests, re
from pathlib import Path

sys.path.append('/home/xiaowu/TCP_LLM_TEST/datasets/LRTS/artifact')
from token_pool import TokenPool

OUT_DIR = Path('/home/xiaowu/codex_survey')
BASE_JSON = OUT_DIR / 'checkpoint_base.json'
CKPT_DETAIL = OUT_DIR / 'checkpoint_detail.json'
BATCH_SIZE = 1000

BASE = 'https://api.github.com/repos/openai/codex'
pool = TokenPool()

def gh_get(url, params=None, retries=6):
    for i in range(retries):
        try:
            headers = pool.get_next_token()
        except:
            headers = pool._default_headers()
        try:
            r = requests.get(url, headers=headers, params=params, timeout=40)
        except:
            time.sleep(min(2**i, 8)); continue
        if r.status_code in (200, 201): return r
        if r.status_code in (403, 429):
            time.sleep(min(2**(i+1), 15)); continue
        if r.status_code >= 500:
            time.sleep(min(2**i, 10)); continue
        return r
    return None

def clean(text):
    if not text: return ''
    t = re.sub(r'<img[^>]*>', ' ', text, flags=re.I)
    t = re.sub(r'!\[[^\]]*\]\([^\)]*\)', ' ', t)
    t = t.replace('\r', ' ').replace('\n', ' ')
    return re.sub(r'\s+', ' ', t).strip()

def section(body, heading):
    if not body or f'### {heading}' not in body: return ''
    s = body.split(f'### {heading}', 1)[1]
    return s.split('\n### ', 1)[0].strip()

def repro_clarity(body):
    s = clean(section(body, 'Steps to reproduce'))
    d = clean(section(body, 'Description'))
    if s and s.lower() not in {'_no response_','n/a','none'} and len(s)>30: return 'high'
    if len(d)>120 or any(k in d.lower() for k in ['step','after','when i','reproduce','1.','2.']): return 'medium'
    return 'low'

def infer_issue(title, body, comments_text, label_names):
    txt = (title+' '+body+' '+comments_text).lower()
    labels = {x.lower() for x in label_names}
    if 'docs' in labels or '/docs' in txt or 'documentation' in txt or 'translation' in txt:
        return ('docs/site', 'Docs out of sync with implementation or i18n/site routing issues.', 'high')
    if 'opentui' in labels or 'tui' in txt or 'terminal' in txt:
        return ('tui/rendering', 'Terminal rendering/state handling fails on specific sequences or capabilities.', 'medium')
    if 'web' in labels or any(k in txt for k in ['desktop app','web ui','browser','android','firefox']):
        return ('web/desktop-ui', 'Frontend event/layout sync has race or viewport handling issues.', 'medium')
    if 'perf' in labels or any(k in txt for k in ['memory leak','leak','slow','freeze','unresponsive','oom','high cpu','lag','stuck']):
        return ('performance/resource', 'Resource lifecycle or heavy reload/re-render causes memory/CPU growth.', 'medium')
    if 'windows' in labels or 'windows' in txt or 'wsl' in txt:
        return ('platform/windows', 'Platform-specific code path diverges on Windows.', 'medium')
    if any(k in txt for k in ['api key','invalid','expired','quota','spending limit','oauth','provider','bedrock','copilot','kimi','mcp']):
        return ('integration/auth/billing', 'Provider adapter/auth validation mismatches upstream API requirements.', 'medium')
    return ('other', 'Edge-case workflow regression (insufficient repro details).', 'low')

base_issues = json.loads(BASE_JSON.read_text(encoding='utf-8'))
detailed = json.loads(CKPT_DETAIL.read_text(encoding='utf-8')) if CKPT_DETAIL.exists() else []
seen = {d['number'] for d in detailed}

todo = [it for it in base_issues if it['number'] not in seen]
batch = todo[:BATCH_SIZE]
print(f'Batch: {len(batch)} to process (done: {len(seen)}, remaining after: {len(todo)-len(batch)})')

for idx, it in enumerate(batch, 1):
    n = it['number']
    try:
        ir = gh_get(f'{BASE}/issues/{n}')
        if not ir or ir.status_code != 200: continue
        issue = ir.json()
        cr = gh_get(issue['comments_url'])
        comments = cr.json() if cr and cr.status_code == 200 else []
        body = issue.get('body','') or ''
        comments_text = ' '.join(c.get('body','') for c in comments)
        label_names = [lb.get('name','') for lb in issue.get('labels',[])]
        bug_type, cause, conf = infer_issue(issue.get('title',''), body, comments_text, label_names)
        detailed.append({
            'number': n,
            'title': issue.get('title',''),
            'state': issue.get('state',''),
            'created_at': issue.get('created_at',''),
            'updated_at': issue.get('updated_at',''),
            'labels': label_names,
            'version': clean(section(body,'OpenCode version')),
            'os': clean(section(body,'Operating System')),
            'plugins': clean(section(body,'Plugins')),
            'repro_clarity': repro_clarity(body),
            'bug_type': bug_type,
            'likely_root_cause': cause,
            'confidence': conf,
            'html_url': it.get('html_url','')
        })
        seen.add(n)
        if len(detailed) % 100 == 0:
            CKPT_DETAIL.write_text(json.dumps(detailed, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f'  checkpoint {len(detailed)}')
    except Exception as e:
        print(f'  error issue {n}: {e}')

CKPT_DETAIL.write_text(json.dumps(detailed, ensure_ascii=False, indent=2), encoding='utf-8')
remaining = len(base_issues) - len(seen)
print(f'BATCH DONE. Total: {len(detailed)}, remaining: {remaining}')
