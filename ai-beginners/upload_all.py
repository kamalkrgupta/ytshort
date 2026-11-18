"""Render in isolated pairs; upload sequentially using existing receipt guards."""
import argparse,asyncio,concurrent.futures,fcntl,json,os,subprocess,sys
from datetime import datetime
from pathlib import Path
B=Path(__file__).resolve().parent;W=B.parent
sys.path.insert(0,str(W/'tools'))
from daily_schedule import production_environment
from worker import save,Z

def prepare(n):
 from voice import synthesize,finish
 from render import setup,render,verify
 os.environ.update(production_environment());d=B/'episodes'/f'{n:02d}'
 if (d/'video.mp4').exists():verify(d);return
 if not (d/'lesson.json').exists():
  ep=json.loads((d/'script.json').read_text());asyncio.run(synthesize([ep]));finish(ep)
  m=json.loads((d/'youtube-metadata.json').read_text())
  if '\n\nCHAPTERS\n' not in m['description']:
   m['description']+='\n\nCHAPTERS\n'+'\n'.join(f'{int(c["start"])//60:02d}:{int(c["start"])%60:02d} {c["title"]}' for c in ep['chapters']);save(d/'youtube-metadata.json',m)
 if not (d/'contact.png').exists():
  project=setup(n,isolated=True)
  subprocess.run(['node','tools/capture-longform.mjs','--stills'],cwd=project,env=dict(production_environment(),AGILE_EPISODE_DIR=str(d)),check=True)
 render(n,isolated=True)

def render_job(n):
 log=B/'episodes'/f'{n:02d}'/'batch-production.log'
 with log.open('a') as f:
  r=subprocess.run([sys.executable,'-u',str(Path(__file__).resolve()),'--prepare',str(n)],cwd=W,env=production_environment(),stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(f'Episode {n} production failed; see {log}')
 return n

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--prepare',type=int);args=ap.parse_args()
 if args.prepare:prepare(args.prepare);return
 with (B/'.worker.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  approval=json.loads((B/'tts-approval.json').read_text());assert approval.get('approved') is True
  assert not (B/'human-narration-required.json').exists()
  env=production_environment();subprocess.run([sys.executable,B/'playlist.py'],cwd=W,env=env,check=True)
  cfg=json.loads((B/'youtube-publishing.json').read_text());cfg['uploadAllRemaining']=True;save(B/'youtube-publishing.json',cfg)
  queue=json.loads((B/'queue.json').read_text());pending=[];errors=[];upload_blocked=False
  for row in queue:
   rp=B/'episodes'/f'{row["episode"]:02d}'/'youtube-upload-receipt.json';r=json.loads(rp.read_text()) if rp.exists() else {}
   if r.get('state') not in ('published','scheduled'):pending.append(row['episode'])
  print('Remaining episodes:',pending,flush=True)
  save(B/'worker-state.json',dict(checkedAt=datetime.now(Z).isoformat(),state='uploading_all',remaining=len(pending)))
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
   futures={pool.submit(render_job,n):n for n in pending}
   for future in concurrent.futures.as_completed(futures):
    n=futures[future];d=B/'episodes'/f'{n:02d}';rp=d/'youtube-upload-receipt.json'
    try:future.result()
    except Exception as e:
     errors.append(dict(episode=n,error=str(e)));print(str(e),flush=True);continue
    print('Rendered and verified episode',n,flush=True)
    if upload_blocked:continue
    if rp.exists():
     r=json.loads(rp.read_text())
     if r.get('rejectedBeforeUpload') and not r.get('videoId'):rp.rename(d/('rejected-'+datetime.now().strftime('%Y%m%d%H%M%S')+'.json'))
    args=[sys.executable,W/'tools/youtube_upload.py','--noninteractive','--credentials',next(W.glob('client_secret*.json')),'--config',B/'youtube-publishing.json','--metadata',d/'youtube-metadata.json']
    if datetime.fromisoformat(queue[n-1]['publishAt'])<=datetime.now(Z):args+=['--publish-now']
    log=d/'batch-upload.log'
    with log.open('a') as f:r=subprocess.run(list(map(str,args)),cwd=W,env=env,stdout=f,stderr=subprocess.STDOUT)
    receipt=json.loads(rp.read_text()) if rp.exists() else {}
    if r.returncode or receipt.get('state') not in ('scheduled','published'):
     errors.append(dict(episode=n,error='Upload not confirmed; inspect batch-upload.log',reason=receipt.get('errorReason')));upload_blocked=True
     print('Uploads held after episode',n,'to avoid retries or duplicates; finishing remaining renders.',flush=True)
    else:
     queue[n-1].update(status=receipt['state'],videoId=receipt['videoId'],url=receipt['url']);save(B/'queue.json',queue)
     print('Scheduled episode',n,receipt['url'],receipt.get('verifiedPublishAt'),flush=True)
    save(B/'worker-state.json',dict(checkedAt=datetime.now(Z).isoformat(),state='uploading_all' if not upload_blocked else 'uploads_held_rendering',lastEpisode=n,errors=errors))
  subprocess.run([sys.executable,B/'playlist.py'],cwd=W,env=env,check=True)
  complete=all(r['status'] in ('published','scheduled') for r in queue)
  cfg=json.loads((B/'youtube-publishing.json').read_text());cfg['scheduleStatus']='complete' if complete else 'needs_attention';save(B/'youtube-publishing.json',cfg)
  save(B/'worker-state.json',dict(checkedAt=datetime.now(Z).isoformat(),state='complete' if complete else 'needs_attention',errors=errors))
  if not complete:raise RuntimeError('Some episodes remain unconfirmed; originals, renders and receipts retained for safe recovery.')
if __name__=='__main__':main()
