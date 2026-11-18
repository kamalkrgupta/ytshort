"""Live schedule readiness audit and bounded repair for all TECH AT 60 series."""
import argparse,copy,fcntl,hashlib,json,os,subprocess,sys,time
from datetime import datetime,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from daily_schedule import production_environment
from youtube_upload import save
ROOT=Path(__file__).resolve().parent.parent
ZONE=ZoneInfo('Asia/Kolkata');CHANNEL='UC7F3e0NsVP37sqroVmYxiFw'
OUT=ROOT/'schedule-health';OUT.mkdir(exist_ok=True)
COURSES=[('Shorts','series','videos','videoNumber',ROOT/'youtube-publishing.json','series/.production.lock'),('AI','ai-beginners','episodes','episode',ROOT/'ai-beginners/youtube-publishing.json','ai-beginners/.worker.lock'),('Agile','agile-masterclass','episodes','episode',ROOT/'agile-masterclass/youtube-publishing.json','agile-masterclass/.render.lock')]
def date(value):return datetime.fromisoformat(value.replace('Z','+00:00'))
def expected_at(kind,row,cfg):
 n=row['videoNumber'] if kind=='Shorts' else row['episode']
 if kind=='Agile' and n<3:return date(row['publishAt']) if row.get('publishAt') else None
 first=2 if kind=='Shorts' else 3 if kind=='Agile' else 1
 schedule=cfg['dailySchedule'];per_day=schedule['videosPerDay'];index=n-first
 day=datetime.fromisoformat(schedule['startDate']).date()+timedelta(days=index//per_day)
 times=schedule['times'];hour,minute=map(int,times[index%per_day if len(times)>1 else 0].split(':'))
 return datetime(day.year,day.month,day.day,hour,minute,tzinfo=ZONE)
def action(item,at,now):
 status=item['status'];p=item.get('processingDetails',{}).get('processingStatus')
 if p in ('failed','terminated') or status.get('uploadStatus') in ('failed','rejected','deleted'):return 'replace_failed'
 if p!='succeeded' and status.get('uploadStatus')!='processed':return 'processing'
 if at<=now:return 'ready' if status['privacyStatus']=='public' else 'publish_overdue'
 if status['privacyStatus']=='public':return 'already_public'
 actual=status.get('publishAt')
 return 'ready' if actual and date(actual)==at and status['privacyStatus']=='private' else 'correct_schedule'
def run(args):
 return subprocess.run(list(map(str,args)),cwd=ROOT,env=production_environment(),check=True)
def verify_asset(dest,kind):
 video=dest/'video.mp4'
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
 v=next(s for s in info['streams'] if s['codec_type']=='video');expected=(1080,1920,60) if kind=='Shorts' else (1920,1080,300 if kind=='AI' else 600)
 assert (v['width'],v['height'])==expected[:2] and abs(float(info['format']['duration'])-expected[2])<.15
 assert any(s['codec_type']=='audio' for s in info['streams'])
 return hashlib.file_digest(video.open('rb'),'sha256').hexdigest()
def corrected_status(item,at,now):
 status={k:v for k,v in item['status'].items() if k in ('license','embeddable','publicStatsViewable','selfDeclaredMadeForKids','containsSyntheticMedia')}
 status.setdefault('selfDeclaredMadeForKids',False)
 status['privacyStatus']='public' if at<=now else 'private'
 if at>now:status['publishAt']=at.isoformat()
 return dict(id=item['id'],status=status)
def upload(dest,config,at,now):
 args=[sys.executable,ROOT/'tools/youtube_upload.py','--noninteractive','--credentials',next(ROOT.glob('client_secret*.json')),'--config',config,'--metadata',dest/'youtube-metadata.json']
 if at<=now:args+=['--publish-now']
 run(args)
def latest_uploads(y):
 c=y.channels().list(part='contentDetails',id=CHANNEL).execute()['items'][0]
 pid=c['contentDetails']['relatedPlaylists']['uploads'];ids=[];token=None
 for _ in range(3):
  r=y.playlistItems().list(part='snippet',playlistId=pid,maxResults=50,pageToken=token).execute();ids.extend(i['snippet']['resourceId']['videoId'] for i in r.get('items',[]));token=r.get('nextPageToken')
  if not token:break
 result=[]
 for i in range(0,len(ids),50):result+=y.videos().list(part='snippet,status,processingDetails,contentDetails',id=','.join(ids[i:i+50])).execute().get('items',[])
 return result

def audit(y,repair=False):
 now=datetime.now(ZONE);until=now+timedelta(days=3);results=[];repairs=[];workers=set();candidates=None
 for kind,folder,episodes,key,config,lockfile in COURSES:
  base=ROOT/folder
  # Producers own their queue and render assets; avoid racing an active producer.
  with (ROOT/lockfile).open('a') as course_lock:
   course_repair=repair
   try:fcntl.flock(course_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:
    course_repair=False
    results.append(dict(course=kind,state='producer_running',needsFollowup=True))
   queue=json.loads((base/'queue.json').read_text());cfg=json.loads(config.read_text());changed=False
   rows=[r for r in queue if expected_at(kind,r,cfg) and expected_at(kind,r,cfg)<=until and (expected_at(kind,r,cfg).date()>=now.date() or r.get('status') not in ('published','scheduled'))]
   for row in rows:
    n=row[key];at=expected_at(kind,row,cfg);dest=base/episodes/f'{n:02d}';rp=dest/'youtube-upload-receipt.json';receipt=json.loads(rp.read_text()) if rp.exists() else {};vid=receipt.get('videoId')
    check=dict(course=kind,episode=n,publishAt=at.isoformat())
    try:
     if course_repair and (not row.get('publishAt') or date(row['publishAt'])!=at):
      row['publishAt']=at.isoformat();changed=True
      mp=dest/'youtube-metadata.json'
      if mp.exists():
       m=json.loads(mp.read_text());m['publishAt']=at.isoformat();save(mp,m)
      repairs.append(dict(course=kind,episode=n,action='corrected_local_schedule'))
     if not vid and receipt and not receipt.get('rejectedBeforeUpload'):
      if candidates is None:candidates=latest_uploads(y)
      started=date(receipt['startedAt']) if receipt.get('startedAt') else None
      matches=[v for v in candidates if v['snippet']['channelId']==CHANNEL and v['snippet']['title']==receipt.get('title') and started and abs((date(v['snippet']['publishedAt'])-started).total_seconds())<600]
      if len(matches)==1 and course_repair:
       vid=matches[0]['id'];receipt.update(videoId=vid,url='https://www.youtube.com/watch?v='+vid,recoveredBy='exact channel, title and upload timestamp match');save(rp,receipt);repairs.append(dict(course=kind,episode=n,action='recovered_upload_receipt',videoId=vid))
      elif len(matches)!=1:
       check.update(state='uncertain_upload',needsFollowup=True);results.append(check);continue
     if not vid:
      check.update(state='missing_upload',needsFollowup=True);workers.add(kind);results.append(check);continue
     found=y.videos().list(part='snippet,status,processingDetails,contentDetails',id=vid).execute().get('items',[])
     if not found:check.update(state='video_missing',needsFollowup=True);results.append(check);continue
     item=found[0];assert item['snippet']['channelId']==CHANNEL
     state=action(item,at,now)
     if state=='processing' and item.get('contentDetails',{}).get('duration')=='P0D':
      started=receipt.get('startedAt',item['snippet']['publishedAt'])
      if now-date(started)>timedelta(hours=2):state='replace_stuck'
     if course_repair and state in ('correct_schedule','publish_overdue'):
      y.videos().update(part='status',body=corrected_status(item,at,now)).execute();repairs.append(dict(course=kind,episode=n,action=state,videoId=vid))
      item=y.videos().list(part='snippet,status,processingDetails,contentDetails',id=vid).execute()['items'][0];state=action(item,at,now)
     if course_repair and state in ('replace_stuck','replace_failed'):
      digest=verify_asset(dest,kind)
      if receipt.get('sha256') and receipt['sha256']!=digest:raise RuntimeError('Asset revision differs from original upload')
      attempts=list(dest.glob('health-replaced-'+now.strftime('%Y%m%d')+'*.json'))
      if len(attempts)>=1:raise RuntimeError('Replacement already attempted today; stopped to avoid repeated uploads')
      meta=json.loads((dest/'youtube-metadata.json').read_text());meta['publishAt']=at.isoformat();save(dest/'youtube-metadata.json',meta)
      archive=dest/('health-replaced-'+now.strftime('%Y%m%d%H%M%S')+'.json');save(archive,dict(receipt=receipt,live=item))
      hidden=corrected_status(item,at,now);hidden['status'].pop('publishAt',None);hidden['status']['privacyStatus']='private';y.videos().update(part='status',body=hidden).execute()
      rp.unlink();upload(dest,config,at,now);receipt=json.loads(rp.read_text());replacement=receipt['videoId'];receipt['replacesVideoId']=vid;save(rp,receipt)
      pid=json.loads(config.read_text()).get('playlistId')
      if pid:
       for member in y.playlistItems().list(part='snippet',playlistId=pid,videoId=vid,maxResults=50).execute().get('items',[]):y.playlistItems().delete(id=member['id']).execute()
      vid=replacement;repairs.append(dict(course=kind,episode=n,action=state,videoId=vid));item=y.videos().list(part='snippet,status,processingDetails,contentDetails',id=vid).execute()['items'][0];state=action(item,at,now)
     if state=='ready':
      confirmed='published' if item['status']['privacyStatus']=='public' else 'scheduled'
      if course_repair:
       receipt.update(state=confirmed,videoId=vid,url='https://www.youtube.com/watch?v='+vid,actualVisibility=item['status']['privacyStatus'],processingStatus=item.get('processingDetails',{}).get('processingStatus'),verifiedPublishAt=item['status'].get('publishAt'));save(rp,receipt)
       row.update(status=confirmed,videoId=vid,url=receipt['url']);row.pop('error',None);changed=True
     check.update(state=state,videoId=vid,needsFollowup=state!='ready')
    except Exception as e:check.update(state='needs_attention',error=type(e).__name__,message=str(e)[:220] if not hasattr(e,'resp') else 'YouTube API error; check authorization, permissions or quota.',needsFollowup=True)
    results.append(check)
   if changed:save(base/'queue.json',queue)
 return results,repairs,workers

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--repair',action='store_true');parser.add_argument('--force',action='store_true');args=parser.parse_args()
 now=datetime.now(ZONE);status=OUT/'latest.json'
 if not args.force and now.hour!=8 and status.exists():
  prior=json.loads(status.read_text())
  if prior.get('date')==now.date().isoformat() and prior.get('state')=='ready':return
 report=dict(date=now.date().isoformat(),checkedAt=now.isoformat(),state='checking',timezone='Asia/Kolkata',lookaheadDays=3)
 save(status,report)
 try:
  c=Credentials.from_authorized_user_file(str(ROOT/'.youtube-auth/token.json'))
  if c.expired:c.refresh(Request());save(ROOT/'.youtube-auth/token.json',json.loads(c.to_json()),True)
  y=build('youtube','v3',credentials=c,cache_discovery=False)
  assert CHANNEL in {v['id'] for v in y.channels().list(part='id',mine=True).execute().get('items',[])}
  results,repairs,workers=audit(y,args.repair)
  report.update(checks=results,repairs=repairs)
  if args.repair:
   try:
    from archive_published_shorts import sync as archive_shorts
    archive_shorts(y)
   except Exception as e:report['archiveError']=type(e).__name__
  if args.repair:
   # Use existing supervised workers, with their receipt and locking safeguards.
   for kind,label in [('Shorts','com.techat60.daily-publishing'),('AI','com.techat60.ai-beginners')]:
    if kind in workers:subprocess.run(['launchctl','kickstart',f'gui/{os.getuid()}/{label}'],check=False)
   if 'Agile' in workers:
    for r in results:
     if r['course']=='Agile' and r['state']=='missing_upload':
      dest=ROOT/'agile-masterclass/episodes'/f'{r["episode"]:02d}'
      try:
       if (dest/'reviewed.json').exists():
        verify_asset(dest,'Agile');upload(dest,ROOT/'agile-masterclass/youtube-publishing.json',date(r['publishAt']),now)
      except Exception:r.update(state='needs_attention',error='Agile upload requires attention')
   for script in ['channel-seo/web_playlist.py','ai-beginners/playlist.py','agile-masterclass/playlist.py']:
    try:run([sys.executable,ROOT/script])
    except Exception:report.setdefault('playlistErrors',[]).append(script)
  report['state']='ready' if not any(r.get('needsFollowup') for r in results) and not report.get('playlistErrors') and not report.get('archiveError') else 'repairing_or_needs_attention'
 except Exception as e:report.update(state='needs_attention',error=type(e).__name__,message='Authorization or connection check failed; manual sign-in may be required.')
 report['finishedAt']=datetime.now(ZONE).isoformat();save(status,report);save(OUT/(now.strftime('%Y-%m-%d-%H%M%S')+'.json'),report)
 lines=['# Daily publishing readiness',f'Checked: {report["checkedAt"]}',f'Status: {report["state"]}','']
 for r in report.get('checks',[]):lines.append(f'- {r["course"]} '+(f'episode {r["episode"]}: ' if 'episode' in r else '')+r['state'])
 (OUT/'latest.md').write_text('\n'.join(lines)+'\n');print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':
 with (OUT/'.lock').open('a') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:sys.exit(0)
  main()
