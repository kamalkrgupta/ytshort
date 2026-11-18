"""Cloud-only YouTube readiness checks; credentials supplied as a secret env var."""
import json,os
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
ZONE=ZoneInfo('Asia/Kolkata')
def main():
 creds=Credentials.from_authorized_user_info(json.loads(os.environ['YOUTUBE_OAUTH_JSON']))
 if not creds.valid:creds.refresh(Request())
 y=build('youtube','v3',credentials=creds,cache_discovery=False)
 m=json.loads(os.environ['YOUTUBE_SCHEDULE_JSON']) if os.environ.get('YOUTUBE_SCHEDULE_JSON') else json.loads(Path(__file__).with_name('schedule.json').read_text());channel=m['channelId']
 mine=y.channels().list(part='id,contentDetails',mine=True).execute()['items'];c=next(c for c in mine if c['id']==channel)
 ids=[];token=None
 for _ in range(4):
  r=y.playlistItems().list(part='snippet',playlistId=c['contentDetails']['relatedPlaylists']['uploads'],maxResults=50,pageToken=token).execute();ids.extend(v['snippet']['resourceId']['videoId'] for v in r.get('items',[]));token=r.get('nextPageToken')
  if not token:break
 videos=[]
 for n in range(0,len(ids),50):videos+=y.videos().list(part='snippet,status,processingDetails,contentDetails',id=','.join(ids[n:n+50])).execute().get('items',[])
 now=datetime.now(ZONE);report=[]
 for row in m['releases']:
  at=datetime.fromisoformat(row['publishAt'].replace('Z','+00:00'))
  if at.date()<now.date() or at>now+timedelta(days=3):continue
  found=[v for v in videos if v['id']==row.get('videoId')]
  if not found:found=[v for v in videos if v['snippet']['title']==row['title'] and v['snippet']['channelId']==channel]
  if len(found)!=1:report.append(dict(**row,state='missing_or_ambiguous_upload',repair='Cloud video assets/production required'));continue
  v=found[0];s=v['status'];processed=s.get('uploadStatus')=='processed' or v.get('processingDetails',{}).get('processingStatus')=='succeeded'
  if not processed:report.append(dict(**row,state='processing_not_ready',video=v['id']));continue
  correct=s['privacyStatus']=='public' if at<=now else s['privacyStatus']=='private' and s.get('publishAt') and datetime.fromisoformat(s['publishAt'].replace('Z','+00:00'))==at
  state='ready'
  if not correct:
   if at>now and s['privacyStatus']=='public':state='already_public_before_slot'
   else:
    status={k:value for k,value in s.items() if k in ('license','embeddable','publicStatsViewable','selfDeclaredMadeForKids','containsSyntheticMedia')}
    status['privacyStatus']='public' if at<=now else 'private'
    if at>now:status['publishAt']=at.isoformat()
    y.videos().update(part='status',body=dict(id=v['id'],status=status)).execute()
    checked=y.videos().list(part='status',id=v['id']).execute()['items'][0]['status']
    assert checked['privacyStatus']==status['privacyStatus']
    if at>now:assert datetime.fromisoformat(checked['publishAt'].replace('Z','+00:00'))==at
    state='repaired'
  report.append(dict(**row,state=state,video=v['id']))
 print(json.dumps(dict(checkedAt=now.isoformat(),checks=report),indent=2))
 if any(r['state'] not in ('ready','repaired') for r in report):raise SystemExit(1)
if __name__=='__main__':main()
