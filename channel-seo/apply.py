import copy,json,sys,time
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
W=Path(__file__).resolve().parent.parent;B=W/'channel-seo'
sys.path.insert(0,str(W/'tools'));from youtube_upload import save
plan=json.loads((B/'changes.json').read_text());before=json.loads((B/'before.json').read_text());channel_id=before['channel']['id']
c=Credentials.from_authorized_user_file(str(W/'.youtube-auth/token.json'))
if c.expired:c.refresh(Request());save(W/'.youtube-auth/token.json',json.loads(c.to_json()),True)
y=build('youtube','v3',credentials=c,cache_discovery=False)
channel=y.channels().list(part='brandingSettings',mine=True).execute()['items'];channel=next(ch for ch in channel if ch['id']==channel_id)
branding=copy.deepcopy(channel['brandingSettings']);branding['channel']['description']=plan['channelDescription'];branding['channel']['keywords']=plan['channelKeywords'];branding['channel']['defaultLanguage']='en'
y.channels().update(part='brandingSettings',body=dict(id=channel_id,brandingSettings=branding)).execute()
print('Channel description and keywords updated.',flush=True)
playlist_ids={kind:json.loads((W/path).read_text())['playlistId'] for kind,path in [('AI','ai-beginners/youtube-publishing.json'),('Agile','agile-masterclass/youtube-publishing.json'),('Web','youtube-publishing.json')]}
mapping={};local=[]
for kind,folder in [('AI','ai-beginners/episodes'),('Agile','agile-masterclass/episodes'),('Web','series/videos')]:
 for p in (W/folder).glob('*/youtube-metadata.json'):
  local.append((kind,p));rp=p.with_name('youtube-upload-receipt.json')
  if rp.exists():
   r=json.loads(rp.read_text())
   if r.get('videoId'):mapping[r['videoId']]=kind
p=W/'html-introduction/out/youtube-metadata.json';local.append(('Web',p));rp=p.with_name('youtube-upload-receipt.json')
if rp.exists():mapping[json.loads(rp.read_text())['videoId']]='Web'
changes=[];remove={t.lower() for t in plan['removeTags']}
def optimize(snippet,kind):
 out={k:v for k,v in snippet.items() if k in ('title','description','tags','categoryId','defaultLanguage','defaultAudioLanguage')}
 out['tags']=[t for t in out.get('tags',[]) if t.lower() not in remove]
 if 'TECH AT 60' not in out['tags'] and 'Techat60' not in out['tags']:out['tags'].append('TECH AT 60')
 if kind:
  url='https://www.youtube.com/playlist?list='+playlist_ids[kind]
  if url not in out['description']:out['description']+='\n\nWatch the course in order: '+url
 assert len(out['description'])<=5000
 return out
for video in before['videos']:
 vid=video['id'];kind=mapping.get(vid)
 # Read fresh mutable metadata before updating, preserving concurrent edits.
 current=y.videos().list(part='snippet',id=vid).execute().get('items',[])
 if not current:continue
 snippet=current[0]['snippet'];assert snippet['channelId']==channel_id
 new=optimize(snippet,kind)
 old={k:v for k,v in snippet.items() if k in new}
 if new!=old:
  response=y.videos().update(part='snippet',body=dict(id=vid,snippet=new)).execute()
  changes.append(dict(videoId=vid,title=new['title'],tagsRemoved=[t for t in snippet.get('tags',[]) if t.lower() in remove],playlistLinked=kind))
  print('Updated video:',new['title'],flush=True)
for kind,p in local:
 if not p.exists():continue
 m=json.loads(p.read_text());new=optimize(m,kind);m.update(new);save(p,m)
sections=y.channelSections().list(part='snippet,contentDetails',mine=True).execute().get('items',[])
represented={pid for s in sections for pid in s.get('contentDetails',{}).get('playlists',[])}
for kind,pid in playlist_ids.items():
 if pid not in represented:
  section=y.channelSections().insert(part='snippet,contentDetails',body=dict(snippet=dict(type='singlePlaylist',position=len(sections)),contentDetails=dict(playlists=[pid]))).execute();sections.append(section)
report=dict(channelId=channel_id,channelDescription=plan['channelDescription'],channelKeywords=plan['channelKeywords'],updatedVideos=changes,localMetadataUpdated=len(local),playlistIds=playlist_ids,sections=sections)
save(B/'applied.json',report)
print('SEO changes applied:',len(changes),'videos;',len(local),'local metadata files;',len(sections),'homepage sections.',flush=True)
