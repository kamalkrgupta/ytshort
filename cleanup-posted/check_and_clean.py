import sys,json,hashlib,os,tempfile
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.append('/Users/impulsiveweb/Techat60-Instagram/.venv/lib/python3.15/site-packages')
sys.path[:0]=[str(ROOT/'tools'),'/Users/impulsiveweb/Techat60-Instagram']
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from github_deploy import auth,read_key
from github_store import GitHub,StateStore
from database import Database
from meta_client import MetaClient
from config import Config
receipts=[]
for p in ROOT.rglob('*receipt*.json'):
 try:r=json.loads(p.read_text())
 except (ValueError,OSError):continue
 if isinstance(r,dict) and r.get('videoId') and r.get('sha256'):receipts.append((p,r))
creds=Credentials.from_authorized_user_file(str(ROOT/'.youtube-auth/token.json'))
if creds.expired:
 creds.refresh(Request());(ROOT/'.youtube-auth/token.json').write_text(creds.to_json());os.chmod(ROOT/'.youtube-auth/token.json',0o600)
y=build('youtube','v3',credentials=creds,cache_discovery=False)
ids=sorted({r['videoId'] for _,r in receipts});live={}
for i in range(0,len(ids),50):
 for item in y.videos().list(part='snippet,status,processingDetails',id=','.join(ids[i:i+50])).execute().get('items',[]):live[item['id']]=item
published={};protected=set()
for p,r in receipts:
 item=live.get(r['videoId'])
 if item and item['snippet']['channelId']=='UC7F3e0NsVP37sqroVmYxiFw' and item['status']['privacyStatus']=='public' and item['status'].get('uploadStatus')=='processed':published.setdefault(r['sha256'],[]).append({'platform':'youtube','id':item['id']})
 elif item:protected.add(r['sha256'])
api=GitHub('kamalkrgupta/techat60-instagram-publisher',auth())
with tempfile.TemporaryDirectory() as tmp:
 db=Database(StateStore(api,read_key()).load(Path(tmp)/'state.sqlite3'))
 meta=MetaClient(Config.load())
 for row in db.history():
  if not row.get('sha256'):continue
  media=meta.media(row['media_id'])
  if str(media.get('id'))==str(row['media_id']) and media.get('permalink'):published.setdefault(row['sha256'],[]).append({'platform':'instagram','id':row['media_id']})
 ig_published=db.published_hashes();protected.update(j['sha256'] for j in db.pending());db.conn.close()
import base64
manifest=json.loads(base64.b64decode(api.contents('cloud/videos.json','main')['content']))
# Preserve local inputs for all future Instagram posts; sync exports this folder.
protected.update(v['sha256'] for v in manifest['videos'] if v['sha256'] not in ig_published)
eligible=[];kept=[]
for p in ROOT.rglob('*'):
 if not p.is_file() or p.suffix.lower() not in ('.mp4','.mov','.m4v','.webm') or p.is_symlink():continue
 with p.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 if digest in published and digest not in protected:eligible.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':digest,'publications':published[digest]})
 else:kept.append(str(p.relative_to(ROOT)))
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'files':eligible,'count':len(eligible),'bytes':sum(r['bytes'] for r in eligible),'keptCount':len(kept),'status':'verified-plan'}
(ROOT/'cleanup-posted/verified-plan.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))
if '--delete' in sys.argv:
 import fcntl
 archive_lock=(ROOT/'Published Shorts/.archive.lock').open('a')
 fcntl.flock(archive_lock,fcntl.LOCK_EX)
 report['status']='deleting'
 (ROOT/'cleanup-posted/deleted.json').write_text(json.dumps(report,indent=2)+'\n')
 for row in eligible:
  p=ROOT/row['path']
  with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256']
  p.unlink()
 report['status']='deleted';(ROOT/'cleanup-posted/deleted.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Deleted verified posted files:',len(eligible))
