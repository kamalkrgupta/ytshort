import json,subprocess,sys
from pathlib import Path
base=Path(__file__).resolve().parent;repo=base/'source';local=Path('/Users/impulsiveweb/Techat60-Instagram');gh=local/'.tools/gh'
sys.path.insert(0,str(local));from config import Config
c=Config.load(local);secrets=[c.token,c.app_secret,c.app_access_token,c.openai_key,(local/'.github-state-key').read_text().strip()]
def run(args,**kwargs):return subprocess.run(list(map(str,args)),check=True,text=True,**kwargs)
tracked=subprocess.check_output(['git','ls-files'],cwd=repo,text=True).splitlines()
for name in tracked:
 p=repo/name
 if p.is_file():
  data=p.read_bytes()
  if any(value and len(value)>=8 and value.encode() in data for value in secrets):raise RuntimeError('Protected value found in source export; deployment blocked')
print('Public source export secret scan passed.',flush=True)
r=run([gh,'run','list','--repo','kamalkrgupta/techat60-instagram-publisher','--limit','30','--json','databaseId,status,createdAt'],capture_output=True)
from datetime import datetime,timezone,timedelta
active=[]
for v in json.loads(r.stdout):
 if v['status']=='completed':continue
 age=datetime.now(timezone.utc)-datetime.fromisoformat(v['createdAt'].replace('Z','+00:00'))
 if v['status']=='queued' and age>timedelta(days=1):
  detail=run([gh,'run','view',str(v['databaseId']),'--repo','kamalkrgupta/techat60-instagram-publisher','--json','jobs,status'],capture_output=True)
  if not json.loads(detail.stdout).get('jobs'):
   print('Ignoring stale unstarted list entry:',v['databaseId'],flush=True);continue
 active.append(v)
if active:raise RuntimeError('An existing workflow is active; reconcile before deployment: '+str([v['databaseId'] for v in active]))
run([gh,'secret','set','INSTAGRAM_CLOUD_ENABLED','--repo','kamalkrgupta/techat60-instagram-publisher'],input='false',capture_output=True)
print('Cloud public publishing held for deployment validation.',flush=True)
run(['git','add','README.md','.github/workflows/instagram-daily.yml','cloud_runner.py','cloud_watchdog.py','scheduled_reel.py','tests/test_scheduled_reel.py','tests/test_watchdog.py'],cwd=repo)
run(['git','-c','user.name=Codex','-c','user.email=codex@users.noreply.github.com','commit','-m','Start guarded Instagram workers before the evening publishing window'],cwd=repo)
helper='!'+str(gh)+' auth git-credential'
run(['git','-c','credential.helper=','-c','credential.helper='+helper,'fetch','origin','main'],cwd=repo)
run(['git','rebase','origin/main'],cwd=repo)
run(['git','-c','credential.helper=','-c','credential.helper='+helper,'push','origin','HEAD:main'],cwd=repo)
sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip();(base/'deployed-commit.txt').write_text(sha+'\n');print('DEPLOYED',sha,flush=True)
run([gh,'workflow','run','instagram-daily.yml','--repo','kamalkrgupta/techat60-instagram-publisher','--ref','main','-f','mode=check'],capture_output=True)
print('Read-only cloud validation dispatched.',flush=True)
