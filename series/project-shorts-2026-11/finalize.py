"""Read back every new schedule and synchronize the existing course playlist."""
import csv,hashlib,json,sys,time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
sys.path.insert(0,str(ROOT/'tools'));from youtube_upload import save
ZONE=ZoneInfo('Asia/Kolkata');CHANNEL='UC7F3e0NsVP37sqroVmYxiFw'
def load(p):return json.loads(p.read_text())
c=Credentials.from_authorized_user_file(str(ROOT/'.youtube-auth/token.json'))
if c.expired:c.refresh(Request());save(ROOT/'.youtube-auth/token.json',json.loads(c.to_json()),True)
y=build('youtube','v3',credentials=c,cache_discovery=False)
assert CHANNEL in {v['id'] for v in y.channels().list(part='id',mine=True).execute()['items']}
plan=load(BASE/'schedule-plan.json');receipts={p['videoNumber']:load(ROOT/'series/videos'/str(p['videoNumber'])/'youtube-upload-receipt.json') for p in plan};ids=[r['videoId'] for r in receipts.values()];assert len(set(ids))==5
live={v['id']:v for v in y.videos().list(part='snippet,status,contentDetails,processingDetails',id=','.join(ids)).execute()['items']};assert len(live)==5
rows=[]
for p in plan:
 n=p['videoNumber'];r=receipts[n];v=live[r['videoId']];d=ROOT/'series/videos'/str(n);status=v['status'];processing=v.get('processingDetails',{}).get('processingStatus')
 assert v['snippet']['channelId']==CHANNEL and v['snippet']['title']==p['title']
 assert status['privacyStatus']=='private' and status['uploadStatus']=='processed' and processing=='succeeded'
 assert datetime.fromisoformat(status['publishAt'].replace('Z','+00:00'))==datetime.fromisoformat(p['publishAt'])
 assert status.get('selfDeclaredMadeForKids') is False
 assert hashlib.sha256((d/'video.mp4').read_bytes()).hexdigest()==r['sha256']
 manifest=load(d/'voice/manifest.json');assert manifest['voice']=='en-US-GuyNeural' and manifest['rate']=='-15%'
 r.update(state='scheduled',processingStatus=processing,actualVisibility='private',verifiedPublishAt=status['publishAt']);save(d/'youtube-upload-receipt.json',r)
 rows.append(dict(videoNumber=n,title=p['title'],videoId=r['videoId'],url=r['url'],publishLocal=p['publishLocal'],publishAt=status['publishAt'],processingStatus=processing,voice=manifest['voice']))
# Add only missing entries to the established full course. Scheduled videos stay private until release.
pid='PLEJDqf_3IqMU';members=[];token=None
while True:
 data=y.playlistItems().list(part='snippet',playlistId=pid,maxResults=50,pageToken=token).execute();members+=data.get('items',[]);token=data.get('nextPageToken')
 if not token:break
present=[v['snippet']['resourceId']['videoId'] for v in members]
for r in rows:
 if r['videoId'] not in present:
  y.playlistItems().insert(part='snippet',body=dict(snippet=dict(playlistId=pid,position=len(present),resourceId=dict(kind='youtube#video',videoId=r['videoId'])))).execute();present.append(r['videoId'])
for attempt in range(4):
 confirmed=[];token=None
 while True:
  data=y.playlistItems().list(part='snippet',playlistId=pid,maxResults=50,pageToken=token).execute();confirmed.extend(v['snippet']['resourceId']['videoId'] for v in data.get('items',[]));token=data.get('nextPageToken')
  if not token:break
 if confirmed[-5:]==ids:break
 time.sleep(2)
assert confirmed[-5:]==ids and all(confirmed.count(vid)==1 for vid in ids),'Course ending order or duplicate mismatch'
q=load(ROOT/'series/queue.json')
for entry in q:
 if entry['videoNumber'] in receipts:
  r=receipts[entry['videoNumber']];entry.update(status='scheduled',url=r['url'],videoId=r['videoId']);entry.pop('error',None)
save(ROOT/'series/queue.json',q)
with (ROOT/'series/posting-calendar.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=['videoNumber','topic','publishLocal','publishAt','status','url']);writer.writeheader();writer.writerows({k:r.get(k,'') for k in writer.fieldnames} for r in q)
cfg=load(ROOT/'youtube-publishing.json');cfg['scheduleStatus']='scheduled';save(ROOT/'youtube-publishing.json',cfg)
now=datetime.now(ZONE).isoformat();result=dict(verifiedAt=now,channelId=CHANNEL,complete=True,scheduled=rows,coursePlaylist='https://www.youtube.com/playlist?list='+pid,courseMembers=len(confirmed),voice='en-US-GuyNeural',rate='-15%',allProcessingSucceeded=True)
save(BASE/'verified-schedules.json',result)
state=load(BASE/'batch-state.json');state.update(active=False,status='complete',updatedAt=now);save(BASE/'batch-state.json',state)
save(ROOT/'series/daily-worker-state.json',dict(checkedAt=now,status='buffer_scheduled',shortsTimes=['11:00','16:00'],timezone='Asia/Kolkata',scheduledThrough='2026-11-19T11:00:00+05:30',remainingCourseShortsScheduled=5))
report='# Remaining Shorts scheduled — November 16, 2026\n\nAll five videos are uploaded, fully processed and remotely scheduled on @Techat60. YouTube handles their releases even when this Mac is off. Existing public Shorts were not replaced.\n\nVoice: Microsoft Edge en-US-GuyNeural at -15%, matching the adult English narrator in the newer cartoon learning series. Voice timing was checked by measured clip lengths, not by ear.\n\n| Lesson | Video | Release (IST) |\n|---|---|---|\n'
for r in rows:
 when=datetime.fromisoformat(r['publishLocal']).strftime('%d %b %Y, %I:%M %p');report+=f'| {r["videoNumber"]} | [{r["title"]}]({r["url"]}) | {when} |\n'
report+='\nEvery final MP4 passed 1080×1920, 30 fps, 1,800-frame, 60-second and AAC-audio checks. Stills were visually reviewed; counter and to-do actions were checked mid-animation. All five videos were verified on the intended channel with the exact release time and the existing not-made-for-kids setting. The five lessons were added to the full web-development playlist in order.\n\nThis completes the existing course queue through lesson 51. No additional Shorts are planned after November 19 at 11 AM IST. New topics would need a new production batch.\n\nBackups: before-batch.json and originals/. Schedule plan: schedule-plan.json. Confirmed results: verified-schedules.json. Each lesson folder retains its final MP4, script, voice clips, stills, checks and upload receipt. The isolated renderer keeps its own project files so older lessons remain unchanged.\n'
(BASE/'Scheduled-Shorts.md').write_text(report)
(ROOT/'series/daily-publishing-status.md').write_text(report)
# Remove the temporary guard now that every requested upload is confirmed.
p=ROOT/'tools/daily_schedule.py';s=p.read_text();guard=" migration=ROOT/'series/project-shorts-2026-11/batch-state.json'\n if migration.exists() and json.loads(migration.read_text()).get('active'):\n  print('Project Shorts voice/render batch active; preserving its queue and media.',flush=True);return\n";assert guard in s;s=s.replace(guard,'');p.write_text(s)
print(json.dumps(result,indent=2))
