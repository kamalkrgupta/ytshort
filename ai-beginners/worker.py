"""Resumable AI series production; YouTube owns release timing after upload."""
import asyncio,csv,fcntl,json,subprocess,sys,os
from datetime import datetime,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
B=Path(__file__).resolve().parent;W=B.parent
sys.path.insert(0,str(W/'tools'))
from daily_schedule import production_environment
from voice import synthesize,finish
from render import render,setup
Z=ZoneInfo('Asia/Kolkata')
def save(p,v):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(v,indent=2)+'\n');t.replace(p)
 if p.name=='queue.json':
  fields=['episode','topic','title','publishAt','plannedDate','status','videoId','url']
  with (B/'posting-calendar.csv').open('w') as f:
   writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows({k:r.get(k) for k in fields} for r in v)
def run(args,**kw):subprocess.run(list(map(str,args)),check=True,env=production_environment(),**kw)
def main():
 if (B/'human-narration-required.json').exists():raise RuntimeError('Human narration requested; replace synthetic voice before production or uploads.')
 if not (B/'tts-approval.json').exists():raise RuntimeError('External narration transfer approval is required before running production.')
 os.environ.update(production_environment())
 run([sys.executable,B/'playlist.py'],cwd=W)
 cfg=json.loads((B/'youtube-publishing.json').read_text())
 if '--all' in sys.argv:
  cfg['uploadAllRemaining']=True;save(B/'youtube-publishing.json',cfg)
 queue=json.loads((B/'queue.json').read_text());now=datetime.now(Z)
 for row in queue:
  n=row['episode'];d=B/'episodes'/f'{n:02d}';r=d/'youtube-upload-receipt.json'
  if not cfg.get('uploadAllRemaining') and datetime.fromisoformat(row['publishAt'])>now+timedelta(days=3):break
  if r.exists():
   receipt=json.loads(r.read_text())
   if receipt.get('state') in ('published','scheduled'):
    row.update(status=receipt['state'],videoId=receipt['videoId'],url=receipt['url']);save(B/'queue.json',queue);continue
   if receipt.get('rejectedBeforeUpload') and not receipt.get('videoId'):
    r.rename(d/('rejected-'+datetime.now().strftime('%Y%m%d%H%M%S')+'.json'))
  save(B/'worker-state.json',dict(checkedAt=datetime.now(Z).isoformat(),state='producing',episode=n))
  print('Producing AI episode',n,flush=True)
  if not (d/'lesson.json').exists():
   ep=json.loads((d/'script.json').read_text());asyncio.run(synthesize([ep]));finish(ep)
   meta=json.loads((d/'youtube-metadata.json').read_text())
   meta['description']+='\n\nCHAPTERS\n'+'\n'.join(f'{int(c["start"])//60:02d}:{int(c["start"])%60:02d} {c["title"]}' for c in ep['chapters'])
   save(d/'youtube-metadata.json',meta)
  if not (d/'contact.png').exists():
   project=setup(n);run(['node','tools/capture-longform.mjs','--stills'],cwd=project,)
  if '--prepare-only' in sys.argv:return
  render(n)
  if '--no-upload' in sys.argv:return
  cmd=[sys.executable,W/'tools/youtube_upload.py','--noninteractive','--credentials',next(W.glob('client_secret*.json')),'--config',B/'youtube-publishing.json','--metadata',d/'youtube-metadata.json']
  if datetime.fromisoformat(row['publishAt'])<=datetime.now(Z):cmd+=['--publish-now']
  run(cmd,cwd=W)
  receipt=json.loads(r.read_text());row.update(status=receipt['state'],videoId=receipt.get('videoId'),url=receipt.get('url'));save(B/'queue.json',queue)
  run([sys.executable,B/'playlist.py'],cwd=W)
 complete=all(r['status'] in ('published','scheduled') for r in queue)
 cfg=json.loads((B/'youtube-publishing.json').read_text());cfg['scheduleStatus']='complete' if complete else 'active';save(B/'youtube-publishing.json',cfg)
 save(B/'worker-state.json',dict(checkedAt=datetime.now(Z).isoformat(),state='complete' if complete else 'buffer_scheduled'))
if __name__=='__main__':
 with (B/'.worker.lock').open('w') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:sys.exit(0)
  try:main()
  except Exception as e:
   save(B/'worker-state.json',dict(checkedAt=datetime.now(Z).isoformat(),state='needs_attention',error=type(e).__name__))
   raise
