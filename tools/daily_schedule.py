"""Reconcile the authorized daily schedule and keep a Shorts buffer uploaded."""
import csv, fcntl, json, os, shutil, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
ROOT=Path(__file__).resolve().parent.parent
ZONE=ZoneInfo('Asia/Kolkata')
def production_environment():
 # launchd does not load the shell's nvm setup. Include Node's bin directory
 # for the producer and its npm/Node subprocesses on every scheduled run.
 env=os.environ.copy()
 if not shutil.which('node',path=env.get('PATH','')):
  candidates=sorted((Path.home()/'.nvm/versions/node').glob('*/bin/node'),key=lambda p:tuple(int(n) for n in p.parents[1].name.lstrip('v').split('.')),reverse=True)
  if not candidates:raise RuntimeError('Node.js is unavailable; install Node before producing Shorts.')
  env['PATH']=str(candidates[0].parent)+os.pathsep+env.get('PATH','/usr/bin:/bin')
 return env
def save(p,v):
 t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(v,indent=2)+'\n');t.replace(p)
def long_schedule(youtube):
 base=ROOT/'agile-masterclass';queue=json.loads((base/'queue.json').read_text()); results=[]
 for row in queue:
  n=row['episode']
  if n<3:continue
  at=datetime(2026,10,24,18,tzinfo=ZONE)+timedelta(days=(n-3)//2)
  value=at.isoformat();dest=base/'episodes'/f'{n:02d}';rp=dest/'youtube-upload-receipt.json'
  receipt=json.loads(rp.read_text()) if rp.exists() else {}
  if receipt.get('videoId'):
   item=youtube.videos().list(part='snippet,status',id=receipt['videoId']).execute()['items'][0]
   assert item['snippet']['channelId']=='UC7F3e0NsVP37sqroVmYxiFw'
   status=item['status']
   if status['privacyStatus']=='public':
    results.append(dict(episode=n,state='published',videoId=item['id']));continue
   if datetime.fromisoformat(status.get('publishAt','2000-01-01T00:00:00Z').replace('Z','+00:00'))!=at:
    youtube.videos().update(part='status',body=dict(id=item['id'],status=dict(privacyStatus='private',publishAt=value,selfDeclaredMadeForKids=False))).execute()
   check=youtube.videos().list(part='status',id=item['id']).execute()['items'][0]['status']
   assert datetime.fromisoformat(check['publishAt'].replace('Z','+00:00'))==at
   receipt.update(publishAt=value,verifiedPublishAt=check['publishAt']);save(rp,receipt)
  meta=json.loads((dest/'youtube-metadata.json').read_text());meta['publishAt']=value;save(dest/'youtube-metadata.json',meta)
  row.update(publishAt=value,plannedDate=at.date().isoformat())
  results.append(dict(episode=n,publishAt=value,videoId=receipt.get('videoId'),state='scheduled' if receipt.get('videoId') else 'pending_upload'))
 save(base/'queue.json',queue)
 cfg=json.loads((base/'youtube-publishing.json').read_text());cfg['dailySchedule']=dict(times=['18:00'],timezone='Asia/Kolkata',videosPerDay=2,startDate='2026-10-24');save(base/'youtube-publishing.json',cfg)
 retry=base/'retry-state.json';state=json.loads(retry.read_text());state['intendedPublishAt']='2026-10-28T18:00:00+05:30';save(retry,state)
 save(base/'daily-schedule-audit.json',dict(checkedAt=datetime.now(ZONE).isoformat(),episodes=results))
 (ROOT/'series/long-schedule-error.json').unlink(missing_ok=True)
def main():
 creds=Credentials.from_authorized_user_file(str(ROOT/'.youtube-auth/token.json'))
 if creds.expired:creds.refresh(Request())
 from youtube_upload import save as save_token
 save_token(ROOT/'.youtube-auth/token.json',json.loads(creds.to_json()),True)
 youtube=build('youtube','v3',credentials=creds,cache_discovery=False)
 try:long_schedule(youtube)
 except Exception as e:
  reason=''
  if hasattr(e,'content'):
   try:reason=json.loads(e.content)['error']['message']
   except Exception:pass
  save(ROOT/'series/long-schedule-error.json',dict(at=datetime.now(ZONE).isoformat(),error=type(e).__name__,message=reason))
  print('Long schedule reconciliation:',type(e).__name__,reason,flush=True)
 if '--long-only' in sys.argv:return
 from archive_published_shorts import sync as archive_shorts
 try:archive_shorts(youtube)
 except Exception as e:print('Published Shorts archive needs attention:',type(e).__name__,flush=True)
 for rp in (ROOT/'series/videos').glob('*/youtube-upload-receipt.json'):
  r=json.loads(rp.read_text())
  if r.get('state')=='rejected' and r.get('rejectedBeforeUpload') and r.get('errorReason')=='uploadLimitExceeded' and not r.get('videoId'):
   rp.rename(rp.with_name('youtube-rejected-'+datetime.now().strftime('%Y%m%d%H%M%S')+'.json'))
 save(ROOT/'series/daily-worker-state.json',dict(checkedAt=datetime.now(ZONE).isoformat(),status='building_upload_buffer',retryIntervalSeconds=3600,shortsTimes=['11:00','16:00'],timezone='Asia/Kolkata'))
 result=subprocess.run([sys.executable,'-u',str(ROOT/'series/produce.py'),'--start','10','--upload','--publish-overdue','--ahead-days','3'],cwd=ROOT,env=production_environment())
 subprocess.run([sys.executable,'-u',str(ROOT/'channel-seo/web_playlist.py')],cwd=ROOT,env=production_environment())
 try:archive_shorts(youtube)
 except Exception as e:print('Published Shorts archive needs attention:',type(e).__name__,flush=True)
 receipts=[json.loads(p.read_text()) for p in (ROOT/'series/videos').glob('*/youtube-upload-receipt.json')]
 limited=any(r.get('state')=='rejected' and r.get('errorReason')=='uploadLimitExceeded' for r in receipts)
 state='buffer_scheduled' if result.returncode==0 else 'waiting_for_upload_limit' if limited else 'needs_attention'
 save(ROOT/'series/daily-worker-state.json',dict(checkedAt=datetime.now(ZONE).isoformat(),status=state,retryIntervalSeconds=3600,shortsTimes=['11:00','16:00'],episodesPerDay=2,episodeTime='18:00',timezone='Asia/Kolkata'))
 print('Daily publishing: '+state,flush=True)
 if result.returncode and not limited:raise RuntimeError('Production requires attention; inspect daily-publishing.log')
if __name__=='__main__':
 with (ROOT/'series/.daily.lock').open('w') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:sys.exit(0)
  main()
