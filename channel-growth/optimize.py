"""Apply a bounded metadata experiment; preserve release settings and backups."""
import argparse, copy, json, sys, time
from datetime import datetime, timezone
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'channel-growth'
sys.path.insert(0, str(ROOT / 'tools'))
from youtube_upload import save
CHANNEL = 'UC7F3e0NsVP37sqroVmYxiFw'
PLAYLIST = 'https://www.youtube.com/playlist?list=PLEJDqf_3IqMU'
EXPERIMENTS = {
 'iJj3UEqr3mM': ('HTML Headings: h1 to h6 Explained in 60 Seconds', 'Use h1 to h6 to organize a page into meaningful sections. See the heading hierarchy with a beginner HTML example.', 'Which heading would you use for a section inside your page: h1 or h2?', 'NwK_T8Qxams'),
 'PZeEmk-S7_w': ('HTML Forms for Beginners: Build Your First Form', 'Learn how an HTML form groups input controls, and try a simple beginner form example.', 'What would your first form collect: feedback or a sign-up?', 'MEEDwR24JOw'),
 'rk479ZjGpvo': ('CSS Box Model: Content, Padding, Border and Margin', 'Understand the CSS box model with a visual example of content, padding, border and margin.', 'Which adds space inside the border: padding or margin?', '_k9pL5fcolg'),
 '_k9pL5fcolg': ('CSS Backgrounds: Make a Two-Color Gradient Card', 'Learn CSS backgrounds with a beginner example, then give a card a two-color gradient. Keep text readable over the background.', 'Which two colors would you use for your gradient card?', 'A9SjSOECb8s'),
 'A9SjSOECb8s': ('CSS Class vs ID: Which Should You Use?', 'Compare CSS classes and IDs with a beginner code example. Reuse a class across elements and keep each ID unique.', 'To style three matching cards, would you choose a class or an ID?', 'tozXzYirna4'),
 'tozXzYirna4': ('CSS Display: Block vs Inline vs Inline-Block', 'See how block, inline and inline-block affect a CSS layout. Compare a block container with inline-block labels.', 'Which display value lets a label flow inline and accept width and height?', 'c_JdeG3Iq3o'),
}
BAD = {'bjp','cjp','congree','neha bora','elon mask','trump','usa','modi','latent','delhi','mock'}
FIELDS = ('title','description','tags','categoryId','defaultLanguage','defaultAudioLanguage')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');args=ap.parse_args()
 creds=Credentials.from_authorized_user_file(str(ROOT/'.youtube-auth/token.json'))
 if creds.expired:
  creds.refresh(Request());save(ROOT/'.youtube-auth/token.json',json.loads(creds.to_json()),True)
 y=build('youtube','v3',credentials=creds,cache_discovery=False)
 mine=y.channels().list(part='id',mine=True).execute()['items']
 assert CHANNEL in {v['id'] for v in mine}, 'Wrong channel'
 ids=list(EXPERIMENTS)+['J-erLjRrEvM']
 videos=y.videos().list(part='snippet,status,statistics',id=','.join(ids)).execute()['items']
 assert len(videos)==len(ids)
 sections=y.channelSections().list(part='snippet,contentDetails',mine=True).execute()['items']
 originals = {}
 if (OUT/'experiment-backup.json').exists():
  originals = {c['videoId']:c['before'] for c in json.loads((OUT/'experiment-backup.json').read_text())['changes']}
 changes=[]
 for v in videos:
  assert v['snippet']['channelId']==CHANNEL
  snippet={k:copy.deepcopy(v['snippet'][k]) for k in FIELDS if k in v['snippet']}
  if v['id'] in EXPERIMENTS:
   assert v['status']['privacyStatus']=='public'
   title,intro,question,next_id=EXPERIMENTS[v['id']]
   original=originals.get(v['id'],v)['snippet']['description']
   # Keep exercises, source links and series context after the original first paragraph.
   body=original.split('\n\n',1)[1] if '\n\n' in original else ''
   body='\n'.join(line for line in body.splitlines() if not line.startswith(('What would you build','Like, share','Watch the course in order:'))).strip()
   snippet.update(title=title, description=f'{intro}\n\n{question}\n\nNext lesson: https://www.youtube.com/watch?v={next_id}\nFull beginner course: {PLAYLIST}\n\n{body}')
  snippet['tags']=[t for t in snippet.get('tags',[]) if t.lower() not in BAD]
  assert len(snippet['title'])<=100 and len(snippet['description'])<=5000
  old={k:v['snippet'][k] for k in snippet}
  if snippet!=old:changes.append(dict(videoId=v['id'],before=v,after=snippet))
 plan=dict(createdAt=datetime.now(timezone.utc).isoformat(),channelId=CHANNEL,changes=changes,sections=sections)
 save(OUT/'experiment-plan.json',plan)
 print('Prepared',len(changes),'video updates; six title/description experiments and unrelated-tag cleanup.')
 if not args.apply:return
 # Durable original backup: never overwrite it on a retry.
 backup=OUT/'experiment-backup.json'
 if not backup.exists():save(backup,plan)
 results=[]
 for change in changes:
  vid=change['videoId'];fresh=y.videos().list(part='snippet,status',id=vid).execute()['items'][0]
  assert {k:fresh['snippet'].get(k) for k in FIELDS}=={k:change['before']['snippet'].get(k) for k in FIELDS}, 'Concurrent metadata change'
  y.videos().update(part='snippet',body=dict(id=vid,snippet=change['after'])).execute()
  results.append(dict(videoId=vid,title=change['after']['title'],submitted=True))
  save(OUT/'applied.json',dict(videos=results,complete=False))
  # Sync active metadata only; keep publication receipts and archive history intact.
  for pattern in ('series/videos/*/youtube-upload-receipt.json','special-shorts/*/youtube-upload-receipt.json'):
   for receipt in ROOT.glob(pattern):
    if json.loads(receipt.read_text()).get('videoId')!=vid:continue
    p=receipt.with_name('youtube-metadata.json')
    if p.exists():
     m=json.loads(p.read_text());save(OUT/'local-backups'/str(p.relative_to(ROOT)),m)
     m.update({k:change['after'][k] for k in ('title','description','tags')});save(p,m)
 web=next(s for s in sections if 'PLEJDqf_3IqMU' in s.get('contentDetails',{}).get('playlists',[]))
 if web['snippet']['position']!=0:
  sn={k:v for k,v in web['snippet'].items() if k in ('type','title','position')};sn['position']=0
  y.channelSections().update(part='snippet,contentDetails',body=dict(id=web['id'],snippet=sn,contentDetails=web['contentDetails'])).execute()
 current=y.channelSections().list(part='snippet,contentDetails',mine=True).execute()['items']
 assert next(s for s in current if s['id']==web['id'])['snippet']['position']==0
 save(OUT/'applied.json',dict(videos=results,complete=False,sections=current,verifiedAt=datetime.now(timezone.utc).isoformat()))
 print('Submitted',len(results),'remaining updates; run verify.py after metadata propagation.')
if __name__=='__main__':main()
