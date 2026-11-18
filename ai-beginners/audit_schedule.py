"""Audit AI course dates and live release readiness; repair only this course."""
import argparse, csv, fcntl, json, sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
B=Path(__file__).resolve().parent;W=B.parent
sys.path.insert(0,str(W/'tools'))
from youtube_upload import save
from schedule_healthcheck import action,corrected_status
ZONE=ZoneInfo('Asia/Kolkata');CHANNEL='UC7F3e0NsVP37sqroVmYxiFw'
def main():
 p=argparse.ArgumentParser();p.add_argument('--local-only',action='store_true');p.add_argument('--repair',action='store_true');p.add_argument('--all',action='store_true');args=p.parse_args()
 if args.repair:
  lock=(B/'.worker.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 now=datetime.now(ZONE);q=json.loads((B/'queue.json').read_text());cfg=json.loads((B/'youtube-publishing.json').read_text());schedule=cfg['dailySchedule'];start=datetime.fromisoformat(schedule['startDate']).replace(hour=14,tzinfo=ZONE)
 assert len(q)==50 and {r['episode'] for r in q}==set(range(1,51))
 rows=[];receipts={}
 for row in q:
  n=row['episode'];dest=B/'episodes'/f'{n:02d}';m=json.loads((dest/'youtube-metadata.json').read_text());expected=start+timedelta(days=(n-1)//2)
  rp=dest/'youtube-upload-receipt.json';receipt=json.loads(rp.read_text()) if rp.exists() else {};receipts[n]=(rp,receipt)
  matches=all(datetime.fromisoformat(v.replace('Z','+00:00'))==expected for v in [row['publishAt'],m['publishAt']])
  rows.append(dict(episode=n,expectedAt=expected.isoformat(),localDatesCorrect=matches,videoId=receipt.get('videoId'),rendered=(dest/'video.mp4').exists(),localState=row['status'],liveState='not_checked',withinBuffer=args.all or expected<=now+timedelta(days=3)))
 report=dict(checkedAt=now.isoformat(),timezone='Asia/Kolkata',episodes=50,videosPerDay=2,publishTime='14:00',lastRelease=rows[-1]['expectedAt'],localScheduleCorrect=all(r['localDatesCorrect'] for r in rows),liveVerified=False,checks=rows)
 if not args.local_only:
  from google.oauth2.credentials import Credentials
  from google.auth.transport.requests import Request
  from googleapiclient.discovery import build
  c=Credentials.from_authorized_user_file(str(W/'.youtube-auth/token.json'))
  if c.expired:c.refresh(Request());save(W/'.youtube-auth/token.json',json.loads(c.to_json()),True)
  y=build('youtube','v3',credentials=c,cache_discovery=False)
  assert CHANNEL in {v['id'] for v in y.channels().list(part='id',mine=True).execute()['items']}
  ids=[r['videoId'] for r in rows if r['videoId']];assert len(ids)==len(set(ids)), 'Duplicate upload IDs'
  found={}
  for i in range(0,len(ids),50):found.update({v['id']:v for v in y.videos().list(part='snippet,status,processingDetails,contentDetails',id=','.join(ids[i:i+50])).execute()['items']})
  for row in rows:
   item=found.get(row['videoId']);expected=datetime.fromisoformat(row['expectedAt']);n=row['episode']
   if not item:row['liveState']='video_missing' if row['videoId'] else 'not_uploaded';continue
   assert item['snippet']['channelId']==CHANNEL
   state=action(item,expected,now)
   if args.repair and state in ('correct_schedule','publish_overdue'):
    y.videos().update(part='status',body=corrected_status(item,expected,now)).execute()
    item=y.videos().list(part='snippet,status,processingDetails,contentDetails',id=row['videoId']).execute()['items'][0];state=action(item,expected,now)
   row.update(liveState=state,visibility=item['status']['privacyStatus'],uploadStatus=item['status'].get('uploadStatus'),actualPublishAt=item['status'].get('publishAt'),duration=item.get('contentDetails',{}).get('duration'))
   if args.repair and state=='ready':
    status='published' if row['visibility']=='public' else 'scheduled';rp,receipt=receipts[n];receipt.update(state=status,actualVisibility=row['visibility'],verifiedPublishAt=row['actualPublishAt']);save(rp,receipt);q[n-1]['status']=status;row['localState']=status
  report['liveVerified']=True
  if args.repair:
   save(B/'queue.json',q)
   with (B/'posting-calendar.csv').open('w') as f:
    fields=['episode','topic','title','publishAt','plannedDate','status','videoId','url'];writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows({k:r.get(k,'') for k in fields} for r in q)
 report['needsAttention']=[r['episode'] for r in rows if not r['localDatesCorrect'] or (report['liveVerified'] and r['withinBuffer'] and r['liveState']!='ready')]
 save(B/'schedule-audit-2026-11-04.json',report)
 print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
 for row in rows:
  if row['videoId'] or row['withinBuffer']:print(json.dumps(row))
if __name__=='__main__':main()
