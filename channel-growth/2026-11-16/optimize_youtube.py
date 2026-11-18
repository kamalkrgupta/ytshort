"""Targeted YouTube improvements with immutable baseline, resume and live verification."""
import argparse,copy,csv,json,re,sys,time
from datetime import datetime,timezone
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
B=Path(__file__).resolve().parent;W=B.parents[1]
sys.path.insert(0,str(W/'tools'))
from youtube_upload import save
CHANNEL='UC7F3e0NsVP37sqroVmYxiFw'
FIELDS=('title','description','tags','categoryId','defaultLanguage','defaultAudioLanguage')
COPY={
'n8KtvhK8ScQ':('JavaScript Functions: Parameters, Return and Your First Function','Write a reusable JavaScript function, pass in two numbers and return their sum. Learn how parameters, arguments and return work together.','What should add(2, 3) return?'),
'vgVn3gu5lhI':('JavaScript If Else: Choose a Message Based on a Score','Use JavaScript if and else to display a different message depending on a practice score. See how a condition chooses which branch runs.','What message would you show when a score is below your target?'),
'_3T2NZM_2Ac':('JavaScript For Loops: Print 1 to 5 with One Loop','Repeat an instruction with a JavaScript for loop. Learn the counter, condition and update by printing the numbers from one through five.','Which part of a for loop changes the counter?'),
'B8q7YYhyiWs':('JavaScript Arrays: Index 0, Push and Length Explained','Store three skills in a JavaScript array, read the first item with index 0 and learn what push and length do.','Which index gives you the first item in an array?'),
'Ka2cK0AVxJA':('Responsive Web Design: Make a Layout Fit Phone and Desktop','Learn how flexible layouts, responsive images and a viewport declaration help a page adapt to phones and desktops. Try a responsive card layout.','What should happen to side-by-side cards on a narrow phone screen?'),
'ubZHLFw_rP4':('CSS Media Queries: Change Your Layout at a Breakpoint','Start with a narrow-screen layout, then use a min-width media query to adjust the layout on wider screens. Try stacking cards on mobile.','Would you start with the narrow layout or the desktop layout?'),
}

def read_playlist(y,pid):
 for attempt in range(5):
  try:return y.playlistItems().list(part='snippet',playlistId=pid,maxResults=50).execute().get('items',[])
  except HttpError as e:
   if e.resp.status!=404 or attempt==4:raise
   time.sleep(2**attempt)

def sn(v):return {k:copy.deepcopy(v['snippet'][k]) for k in FIELDS if k in v['snippet']}
def matches(actual,expected):
 # YouTube may populate an omitted audio-language default after a snippet update.
 return all(actual.get(k)==v for k,v in expected.items()) and set(actual)-set(expected)<={'defaultAudioLanguage'}

def local_metadata():
 out={}
 for pat in ('series/videos/*/youtube-upload-receipt.json','ai-beginners/episodes/*/youtube-upload-receipt.json'):
  for p in W.glob(pat):
   v=json.loads(p.read_text()).get('videoId')
   if v and p.with_name('youtube-metadata.json').exists():out[v]=p.with_name('youtube-metadata.json')
 return out

def prepare():
 d=json.loads((B/'youtube-live-before.json').read_text());vs={v['id']:v for v in d['videos']};changes=[]
 for vid,(title,intro,q) in COPY.items():
  v=vs[vid];assert v['status']['privacyStatus']=='public'
  s=sn(v);body=s['description'].split('\n\n',1)[1]
  body='\n'.join(line for line in body.splitlines() if not line.startswith(('What would you build','Like, share, and subscribe','Watch the course in order:'))).strip()
  course='CSS for Beginners' if vid in ('Ka2cK0AVxJA','ubZHLFw_rP4') else 'JavaScript for Beginners'
  s.update(title=title,description=f'{intro}\n\nTry answering: {q}\n\nContinue learning: open the {course} playlist on @Techat60.\nSubscribe to TECH AT 60 for practical beginner coding lessons.\n\n{body}')
  changes.append(dict(id=vid,kind='coding-title-and-description',before=v,after=s))
 ai={}
 for v in vs.values():
  m=re.search(r'AI for Beginners [—–-] Episode (\d+) of 50',v['snippet']['description'])
  if m and v['status']['privacyStatus']=='public':ai[int(m[1])]=v
 for n,v in sorted(ai.items()):
  s=sn(v);lines=s['description'].splitlines();has_next=any(line.startswith('Next lesson:') for line in lines)
  if has_next or n+1 not in ai:continue
  body='\n'.join(line for line in lines if not line.startswith(('Watch the course in order:','Continue the course:','Next lesson:'))).strip()
  intro,rest=body.split('\n\n',1)
  nav=f'Next lesson: https://www.youtube.com/watch?v={ai[n+1]["id"]}\nFull AI beginner course: https://www.youtube.com/playlist?list=PLHH8ZgwKrWFk'
  s['description']=intro+'\n\n'+nav+'\n\n'+rest
  changes.append(dict(id=v['id'],kind='AI-course-navigation',before=v,after=s))
 queue=json.loads((W/'series/queue.json').read_text());playlists=[]
 for name,low,high,desc in [
  ('HTML for Beginners | Build Your First Web Page',2,20,'Start with HTML structure, then learn links, images, forms and semantic elements. Follow these beginner lessons in order and try each small exercise.'),
  ('CSS for Beginners | Style a Responsive Website',21,36,'Learn CSS step by step: selectors, colors, the box model, Flexbox, Grid, responsive layouts and animations. Watch in order and practise one concept at a time.'),
  ('JavaScript for Beginners | Variables to DOM Manipulation',37,46,'Start JavaScript with variables and data types, then learn functions, conditions, loops, arrays, objects and DOM manipulation. Follow the lessons in order and try each exercise.')]:
  ids=[r['videoId'] for r in queue if low<=r['videoNumber']<=high and r.get('videoId') in vs and vs[r['videoId']]['status']['privacyStatus']=='public']
  if low==2:ids.insert(0,'Vi_gc4jOFAw')
  playlists.append(dict(title=name,description=desc,ids=ids))
 for c in changes:assert len(c['after']['title'])<=100 and len(c['after']['description'])<=5000
 save(B/'youtube-change-plan.json',dict(createdAt=datetime.now(timezone.utc).isoformat(),channelId=CHANNEL,changes=changes,playlists=playlists))
 with (B/'youtube-measurement-baseline.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['id','change','title','published_at','duration','views','likes','comments'])
  for c in changes:
   v=c['before'];st=v.get('statistics',{});w.writerow([v['id'],c['kind'],v['snippet']['title'],v['snippet']['publishedAt'],v['contentDetails']['duration'],st.get('viewCount',''),st.get('likeCount',''),st.get('commentCount','')])
 print('Prepared',len(changes),'video changes and',len(playlists),'topic playlists.')

def apply():
 plan=json.loads((B/'youtube-change-plan.json').read_text());c=Credentials.from_authorized_user_file(str(W/'.youtube-auth/token.json'))
 if c.expired:c.refresh(Request());save(W/'.youtube-auth/token.json',json.loads(c.to_json()),True)
 y=build('youtube','v3',credentials=c,cache_discovery=False)
 assert CHANNEL in {v['id'] for v in y.channels().list(part='id',mine=True).execute()['items']}
 path=B/'youtube-application-state.json';state=json.loads(path.read_text()) if path.exists() else dict(videos=[],playlists=[],complete=False)
 locals=local_metadata()
 for change in plan['changes']:
  vid=change['id'];v=y.videos().list(part='snippet,status',id=vid).execute()['items'][0]
  assert v['snippet']['channelId']==CHANNEL and v['status']==change['before']['status'],'Visibility/schedule changed; stop'
  current=sn(v);assert matches(current,sn(change['before'])) or matches(current,change['after']),'Concurrent editorial change; stop'
  if not matches(current,change['after']):
   merged=copy.deepcopy(current);merged.update(change['after']);y.videos().update(part='snippet',body=dict(id=vid,snippet=merged)).execute()
  if vid not in state['videos']:state['videos'].append(vid)
  save(path,state)
  if vid in locals:
   p=locals[vid];backup=B/'optimization-local-backups'/p.relative_to(W)
   if not backup.exists():save(backup,json.loads(p.read_text()))
   metadata=json.loads(p.read_text());metadata.update({k:change['after'][k] for k in ('title','description')});save(p,metadata)
 allps=y.playlists().list(part='snippet,status',mine=True,maxResults=50).execute().get('items',[])
 sections=y.channelSections().list(part='snippet,contentDetails',mine=True).execute().get('items',[])
 position=max((s['snippet']['position'] for s in sections),default=-1)+1
 for p in plan['playlists']:
  playlist_matches=[v for v in allps if v['snippet']['title']==p['title']];assert len(playlist_matches)<=1
  if playlist_matches:pid=playlist_matches[0]['id']
  else:
   result=y.playlists().insert(part='snippet,status',body=dict(snippet=dict(title=p['title'],description=p['description'],defaultLanguage='en'),status=dict(privacyStatus='public'))).execute();pid=result['id'];allps.append(result)
  if not any(v['id']==pid for v in state['playlists']):state['playlists'].append(dict(id=pid,title=p['title']))
  save(path,state)
  rows=read_playlist(y,pid);present=[v['snippet']['resourceId']['videoId'] for v in rows]
  assert present==p['ids'][:len(present)],'Unexpected playlist membership; stop'
  for n,vid in enumerate(p['ids']):
   if vid not in present:y.playlistItems().insert(part='snippet',body=dict(snippet=dict(playlistId=pid,position=n,resourceId=dict(kind='youtube#video',videoId=vid)))).execute()
  if not any(pid in s.get('contentDetails',{}).get('playlists',[]) for s in sections):
   section=y.channelSections().insert(part='snippet,contentDetails',body=dict(snippet=dict(type='singlePlaylist',position=position),contentDetails=dict(playlists=[pid]))).execute();sections.append(section);position+=1
  print('Verified submission:',p['title'],len(p['ids']),'lessons',flush=True)
 # Verify every edited snippet, release status and playlist order from fresh reads.
 for change in plan['changes']:
  v=y.videos().list(part='snippet,status',id=change['id']).execute()['items'][0]
  assert matches(sn(v),change['after']) and v['status']==change['before']['status'],'Live video verification failed'
 for p,actual in zip(plan['playlists'],state['playlists']):
  assert p['title']==actual['title']
  rows=read_playlist(y,actual['id'])
  assert [r['snippet']['resourceId']['videoId'] for r in rows]==p['ids']
 sections=y.channelSections().list(part='snippet,contentDetails',mine=True).execute()['items']
 for p in state['playlists']:assert any(p['id'] in s.get('contentDetails',{}).get('playlists',[]) for s in sections)
 # Check status across all baseline videos, including future releases.
 baseline=json.loads((B/'youtube-live-before.json').read_text());ids=[v['id'] for v in baseline['videos']];fresh={}
 for i in range(0,len(ids),50):fresh.update({v['id']:v for v in y.videos().list(part='status',id=','.join(ids[i:i+50])).execute()['items']})
 for v in baseline['videos']:assert fresh[v['id']]['status']==v['status'],'A release setting changed during execution'
 state.update(complete=True,verifiedAt=datetime.now(timezone.utc).isoformat(),allReleaseSettingsVerified=len(ids),sections=sections);save(path,state)
 print('All changes verified.',json.dumps({k:v for k,v in state.items() if k!='sections'}))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');args=ap.parse_args()
 if args.apply:apply()
 else:prepare()
