"""Focused Agile packaging and public-course navigation; no release changes."""
import argparse,copy,json,sys,time
from pathlib import Path
from datetime import datetime,timezone
B=Path(__file__).resolve().parent;W=B.parents[1]
sys.path.insert(0,str(W/'tools'))
from youtube_upload import save
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
CHANNEL='UC7F3e0NsVP37sqroVmYxiFw'
FIELDS=('title','description','tags','categoryId','defaultLanguage','defaultAudioLanguage')
COPY={
 1:('Agile Testing for Beginners: How Testing Fits a Sprint','See how testing fits into Agile development, from story refinement to a sprint example. Learn the core principles with fictional software-testing scenarios.','Which risk would you test first in a new checkout feature?'),
 3:('What Does an Agile Tester Do? Roles and Skills Explained','Understand the role of an Agile tester in refinement, developer collaboration, test execution and team communication. Follow a fictional payment example.','If a payment times out, what would you check before retrying it?'),
 4:('Agile Testing Metrics: Track Tests, Bugs and Release Risk','Learn how to track test execution, defects and release risk in Agile. Compare useful reporting signals through a worked testing example.','Which unresolved failure would stop you from recommending a release?'),
 7:('Testing in Scrum: A QA Workflow from Planning to Done','Follow testing through Scrum refinement, sprint planning, development and the Definition of Done. Work through a fictional sprint example.','What evidence would you need before calling a story Done?'),
 8:('TDD vs BDD vs ATDD: What Is the Difference?','Compare TDD, BDD and ATDD, then see how exploratory testing and test-design techniques complement them. Learn with beginner-friendly worked examples.','Would you clarify a business rule with a unit test or a shared acceptance example first?'),
 9:('Agile Test Documentation: Test Cases, Bug Reports and Traceability','Learn which testing documents help an Agile team: acceptance criteria, test cases, bug reports, exploratory charters and traceability. Follow a practical document example.','What information would another tester need to reproduce your bug report?'),
}
START_TITLE='Start Here | Learn AI, Web Development & Software Testing'
START_IDS=['Vi_gc4jOFAw','z3Z_RcpRZrw','reA35oDRHj8']
START_DESC='New to TECH AT 60? Choose your learning path with these introductory English lessons.\n\nBuild websites: https://www.youtube.com/playlist?list=PLEJDqf_3IqMU\nLearn AI: https://www.youtube.com/playlist?list=PLHH8ZgwKrWFk\nLearn software testing: https://www.youtube.com/playlist?list=PLXqX5lBoONpI\n\nStart with one path, try a small exercise, then continue through its course playlist.'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--verify',action='store_true');args=ap.parse_args()
 c=Credentials.from_authorized_user_file(str(W/'.youtube-auth/token.json'))
 if c.expired:c.refresh(Request());save(W/'.youtube-auth/token.json',json.loads(c.to_json()),True)
 y=build('youtube','v3',credentials=c,cache_discovery=False)
 assert CHANNEL in {v['id'] for v in y.channels().list(part='id',mine=True).execute()['items']}
 if args.verify:
  plan=json.loads((B/'plan.json').read_text());expected=plan['videos'];found={}
  for i in range(0,len(expected),50):found.update({v['id']:v for v in y.videos().list(part='snippet,status',id=','.join(r['id'] for r in expected[i:i+50])).execute()['items']})
  for item in expected:
   v=found[item['id']];assert v['snippet']['title']==item['after']['title'] and v['snippet']['description']==item['after']['description'],item['id']
   assert v['status']==item['before']['status'],'Release settings changed'
  nav=json.loads((B/'navigation.json').read_text());pid=nav['playlistId']
  members=y.playlistItems().list(part='snippet',playlistId=pid,maxResults=50).execute()['items'];assert [v['snippet']['resourceId']['videoId'] for v in members]==START_IDS
  sections=y.channelSections().list(part='snippet,contentDetails',mine=True).execute()['items'];assert any(s['snippet']['position']==0 and pid in s.get('contentDetails',{}).get('playlists',[]) for s in sections)
  branding=y.channels().list(part='brandingSettings',mine=True).execute()['items'];ch=next(c for c in branding if c['id']==CHANNEL);assert 'https://www.youtube.com/playlist?list='+pid in ch['brandingSettings']['channel']['description']
  result=dict(verifiedAt=datetime.now(timezone.utc).isoformat(),updatedVideos=len(expected),agileTitleExperiments=6,publicCourseNavigation=True,startHerePlaylist='https://www.youtube.com/playlist?list='+pid,homepagePosition=0,releaseSettingsPreserved=True)
  save(B/'verified.json',result);print(json.dumps(result,indent=2));return
 baseline=json.loads((B/'before.json').read_text());live={v['id']:v for v in baseline['videos']};courses={};locals={}
 for kind,folder in [('Agile','agile-masterclass'),('AI','ai-beginners')]:
  rows=json.loads((W/folder/'queue.json').read_text());items=[]
  for row in rows:
   d=W/folder/'episodes'/f'{row["episode"]:02d}';rp=d/'youtube-upload-receipt.json'
   if not rp.exists():continue
   vid=json.loads(rp.read_text()).get('videoId')
   if vid and vid in live and live[vid]['status']['privacyStatus']=='public':items.append((row['episode'],vid));locals[vid]=d/'youtube-metadata.json'
  courses[kind]=sorted(items)
 changes=[]
 for kind,items in courses.items():
  pid='PLXqX5lBoONpI' if kind=='Agile' else 'PLHH8ZgwKrWFk';url='https://www.youtube.com/playlist?list='+pid
  for pos,(n,vid) in enumerate(items):
   v=live[vid];snippet={k:copy.deepcopy(v['snippet'][k]) for k in FIELDS if k in v['snippet']};original=snippet['description']
   intro,body=(original.split('\n\n',1)+[''])[:2]
   body='\n'.join(line for line in body.splitlines() if not line.startswith(('Watch the course in order:','Next lesson:','Continue the course:'))).strip()
   question=''
   if kind=='Agile' and n in COPY:
    title,intro,question=COPY[n];snippet['title']=title
    body='\n'.join(line for line in body.splitlines() if not line.startswith('Practice:')).strip()
    body=f'Agile Testing Masterclass — Episode {n} of 12 | English | 10-minute lesson.\n\n'+body
   nav=[]
   if pos+1<len(items):nav.append('Next lesson: https://www.youtube.com/watch?v='+items[pos+1][1])
   nav.append('Continue the course: '+url)
   snippet['description']=intro+'\n\n'+(('Try answering: '+question+'\n\n') if question else '')+'\n'.join(nav)+'\n\n'+body
   assert len(snippet['title'])<=100 and len(snippet['description'])<=5000
   changes.append(dict(id=vid,course=kind,episode=n,before=v,after=snippet,localPath=str(locals[vid].relative_to(W))))
 plan=dict(createdAt=datetime.now(timezone.utc).isoformat(),videos=changes)
 if not (B/'plan.json').exists():save(B/'plan.json',plan)
 else:plan=json.loads((B/'plan.json').read_text());changes=plan['videos']
 print('Prepared',len(changes),'public video updates; six Agile title experiments.')
 if not args.apply:return
 applied=[]
 for change in changes:
  vid=change['id'];current=y.videos().list(part='snippet,status',id=vid).execute()['items'][0]
  old={k:current['snippet'][k] for k in FIELDS if k in current['snippet']}
  before={k:change['before']['snippet'][k] for k in FIELDS if k in change['before']['snippet']}
  allowed_desc={before['description'],change['after']['description']}
  if change.get('previousAfter'):allowed_desc.add(change['previousAfter']['description'])
  allowed_desc.update(change.get('previousDescriptions',[]))
  assert old['title'] in (before['title'],change['after']['title']) and old['description'] in allowed_desc,'Concurrent editorial change'
  merged=copy.deepcopy(old);merged.update({k:change['after'][k] for k in ('title','description')});change['after']=merged
  save(B/'plan.json',plan)
  if old!=merged:y.videos().update(part='snippet',body=dict(id=vid,snippet=merged)).execute()
  p=W/change['localPath'];m=json.loads(p.read_text());backup=B/'local-backups'/change['localPath']
  if not backup.exists():save(backup,m)
  m.update({k:change['after'][k] for k in ('title','description')});save(p,m)
  applied.append(vid);save(B/'applied.json',dict(videos=applied,complete=False))
 # Idempotent playlist creation; exact title and saved ID protect retries.
 playlists=y.playlists().list(part='snippet,status',mine=True,maxResults=50).execute()['items'];matches=[p for p in playlists if p['snippet']['title']==START_TITLE];assert len(matches)<=1
 if (B/'navigation.json').exists():playlist={'id':json.loads((B/'navigation.json').read_text())['playlistId']}
 elif matches:playlist=matches[0]
 else:playlist=y.playlists().insert(part='snippet,status',body=dict(snippet=dict(title=START_TITLE,description=START_DESC,defaultLanguage='en'),status=dict(privacyStatus='public'))).execute()
 pid=playlist['id'];save(B/'navigation.json',dict(playlistId=pid))
 for attempt in range(12):
  try:members=y.playlistItems().list(part='snippet',playlistId=pid,maxResults=50).execute().get('items',[]);break
  except HttpError as e:
   if e.resp.status!=404 or attempt==11:raise
   time.sleep(2)
 known={v['snippet']['resourceId']['videoId'] for v in members}
 for pos,vid in enumerate(START_IDS):
  assert live[vid]['status']['privacyStatus']=='public'
  if vid not in known:y.playlistItems().insert(part='snippet',body=dict(snippet=dict(playlistId=pid,position=pos,resourceId=dict(kind='youtube#video',videoId=vid)))).execute()
 sections=y.channelSections().list(part='snippet,contentDetails',mine=True).execute()['items'];section=next((s for s in sections if pid in s.get('contentDetails',{}).get('playlists',[])),None)
 if not section:y.channelSections().insert(part='snippet,contentDetails',body=dict(snippet=dict(type='singlePlaylist',position=0),contentDetails=dict(playlists=[pid]))).execute()
 elif section['snippet']['position']!=0:
  sn={k:v for k,v in section['snippet'].items() if k in ('type','position','title')};sn['position']=0;y.channelSections().update(part='snippet,contentDetails',body=dict(id=section['id'],snippet=sn,contentDetails=section['contentDetails'])).execute()
 channels=y.channels().list(part='brandingSettings',mine=True).execute()['items'];channel=next(v for v in channels if v['id']==CHANNEL);branding=copy.deepcopy(channel['brandingSettings']);url='https://www.youtube.com/playlist?list='+pid
 if url not in branding['channel']['description']:
  branding['channel']['description']+='\n\nNew here? Choose a learning path: '+url
  assert len(branding['channel']['description'])<=1000
  y.channels().update(part='brandingSettings',body=dict(id=CHANNEL,brandingSettings=branding)).execute()
 save(B/'applied.json',dict(videos=applied,complete=True,startHerePlaylist=pid));print('Submitted all changes. Run --verify after propagation.')
if __name__=='__main__':main()
