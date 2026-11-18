"""Verify all twenty public-release schedules and the ordered topic playlist."""
import csv,hashlib,json,sys,time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
B=Path(__file__).resolve().parent;W=B.parent;ZONE=ZoneInfo('Asia/Kolkata');CHANNEL='UC7F3e0NsVP37sqroVmYxiFw'
sys.path.insert(0,str(W/'tools'));from youtube_upload import save
def load(p):return json.loads(p.read_text())
c=Credentials.from_authorized_user_file(str(W/'.youtube-auth/token.json'))
if c.expired:c.refresh(Request());save(W/'.youtube-auth/token.json',json.loads(c.to_json()),True)
y=build('youtube','v3',credentials=c,cache_discovery=False)
assert CHANNEL in {v['id'] for v in y.channels().list(part='id',mine=True).execute()['items']}
q=load(B/'queue.json');assert len(q)==20
corrections=load(B/'editorial-corrections.json') if (B/'editorial-corrections.json').exists() else {}
for t in q:
 if str(t['number']) in corrections:t['title']=corrections[str(t['number'])]['title']
receipts=[load(B/'videos'/f'{t["number"]:02d}'/'youtube-upload-receipt.json') for t in q];ids=[r['videoId'] for r in receipts];assert len(set(ids))==20
live={v['id']:v for v in y.videos().list(part='snippet,status,processingDetails,contentDetails',id=','.join(ids)).execute()['items']};assert len(live)==20
rows=[]
for t,r in zip(q,receipts):
 d=B/'videos'/f'{t["number"]:02d}';v=live[r['videoId']];s=v['status'];processing=v.get('processingDetails',{}).get('processingStatus')
 assert v['snippet']['channelId']==CHANNEL and v['snippet']['title']==t['title']
 assert s['privacyStatus']=='private' and s['uploadStatus']=='processed' and processing=='succeeded'
 assert datetime.fromisoformat(s['publishAt'].replace('Z','+00:00'))==datetime.fromisoformat(t['publishAt'])
 assert datetime.fromisoformat(s['publishAt'].replace('Z','+00:00')).astimezone(ZONE).strftime('%H:%M')=='20:00'
 assert s.get('selfDeclaredMadeForKids') is False
 assert hashlib.sha256((d/'video.mp4').read_bytes()).hexdigest()==r['sha256']
 manifest=load(d/'voice/manifest.json');assert manifest['voice']=='en-US-GuyNeural' and manifest['rate']=='-15%'
 timeline=load(d/'timeline.json');assert sum(timeline.values())==60
 for k,clip in manifest['clips'].items():assert manifest['leadIn']+clip['duration']<=timeline[k]
 r.update(state='scheduled',processingStatus=processing,verifiedPublishAt=s['publishAt']);save(d/'youtube-upload-receipt.json',r)
 t.update(status='scheduled',videoId=r['videoId'],url=r['url']);t.pop('error',None)
 rows.append({k:t[k] for k in ('number','slug','title','publishLocal','publishAt','videoId','url','source')})
slots=[datetime.fromisoformat(t['publishAt']) for t in q];assert all((b-a).total_seconds()==86400 for a,b in zip(slots,slots[1:]))
pid=load(B/'youtube-publishing.json')['playlistId']
def members():
 data=y.playlistItems().list(part='snippet',playlistId=pid,maxResults=50).execute().get('items',[])
 return [r['snippet']['resourceId']['videoId'] for r in data]
current=members()
# Only append expected IDs. Refuse unrelated members or changes to existing order.
assert current==ids[:len(current)],'Unexpected playlist members or ordering'
for pos,vid in enumerate(ids):
 if vid not in current:y.playlistItems().insert(part='snippet',body=dict(snippet=dict(playlistId=pid,position=pos,resourceId=dict(kind='youtube#video',videoId=vid)))).execute()
for _ in range(5):
 actual=members()
 if actual==ids:break
 time.sleep(2)
assert actual==ids and len(set(actual))==20
sections=y.channelSections().list(part='snippet,contentDetails',mine=True).execute()['items']
if not any(pid in s.get('contentDetails',{}).get('playlists',[]) for s in sections):
 position=max(s['snippet']['position'] for s in sections)+1
 y.channelSections().insert(part='snippet,contentDetails',body=dict(snippet=dict(type='singlePlaylist',position=position),contentDetails=dict(playlists=[pid]))).execute()
for attempt in range(5):
 sections=y.channelSections().list(part='snippet,contentDetails',mine=True).execute()['items']
 if any(pid in s.get('contentDetails',{}).get('playlists',[]) for s in sections):break
 time.sleep(2)
assert any(pid in s.get('contentDetails',{}).get('playlists',[]) for s in sections)
before=load(B/'channel-before-resume.json')['videos'];preserved=0
for i in range(0,len(before),50):
 group=before[i:i+50];fresh={v['id']:v for v in y.videos().list(part='snippet,status',id=','.join(v['id'] for v in group)).execute()['items']}
 for old in group:
  v=fresh[old['id']];assert v['snippet']['title']==old['snippet']['title'] and v['snippet']['description']==old['snippet']['description']
  # A scheduled release may become public naturally while this batch runs.
  assert v['status']==old['status'] or (old['status'].get('publishAt') and v['status']['privacyStatus']=='public' and datetime.fromisoformat(old['status']['publishAt'].replace('Z','+00:00'))<=datetime.now(ZONE))
  preserved+=1
save(B/'queue.json',q)
with (B/'posting-calendar.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=['number','title','publishLocal','publishAt','status','url']);writer.writeheader();writer.writerows({k:t.get(k,'') for k in writer.fieldnames} for t in q)
cfg=load(B/'youtube-publishing.json');cfg['scheduleStatus']='scheduled';save(B/'youtube-publishing.json',cfg)
result=dict(complete=True,verifiedAt=datetime.now(ZONE).isoformat(),channelId=CHANNEL,scheduledCount=20,allProcessingSucceeded=True,voice='en-US-GuyNeural',rate='-15%',playlistUrl='https://www.youtube.com/playlist?list='+pid,existingVideosPreserved=preserved,videos=rows);save(B/'verified-schedules.json',result)
text='# Twenty tech Shorts — confirmed publishing schedule\n\nAll 20 original 60-second vertical Shorts are uploaded, fully processed and scheduled on @Techat60 at **8 PM Asia/Kolkata daily**, November 17–December 6, 2026. YouTube handles the releases even while this Mac is off.\n\nVoice: Microsoft Edge TTS **en-US-GuyNeural, −15%**, matching the selected cartoon narrator. Narration timing was checked using measured clip lengths, not by ear.\n\nThis is a shuffled editorial selection of timely AI, security, connectivity and gadget topics, not a ranking based on search-volume data. Sources were checked November 16 and are linked below and in Sources.md. Illustrations are original diagrams, not product footage or benchmark measurements.\n\n[Watch the topic playlist]('+result['playlistUrl']+')\n\n| Date (2026) | Time IST | Short |\n|---|---|---|\n'
for t in rows:text+='| '+datetime.fromisoformat(t['publishLocal']).strftime('%b %d')+' | 8 PM | ['+t['title']+']('+t['url']+') |\n'
text+='\nEach video passed 1080×1920, H.264, 30 fps, 1,800-frame, 60-second and AAC-audio checks. All 120 voice clips fit their scenes; stills and mid-animation frames were reviewed. Verified remote checks include channel identity, exact future publish time, private visibility before release, successful processing, and the existing not-made-for-kids setting. Every video appears once in the ordered topic playlist.\n\nThe prior course videos and their release settings were preserved. This batch has its own queue and 8 PM configuration; it does not replace the existing course cadence.\n\nProduction sources and final MP4s are in videos/01 through videos/20. Schedule and upload proof: verified-schedules.json and per-video youtube-upload-receipt.json. Resume scripts refuse past release times and preserve uncertain upload receipts instead of creating duplicate uploads.\n'
(B/'Scheduled-Tech-Shorts.md').write_text(text)
print(json.dumps({k:v for k,v in result.items() if k!='videos'},indent=2))
