"""Maintain episode order in the course playlist; never duplicate members."""
import fcntl,json,sys,time
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
W=Path(__file__).resolve().parent.parent;B=W/'series'
sys.path.insert(0,str(W/'tools'))
from youtube_upload import save
TITLE='Web Development for Beginners | HTML, CSS & JavaScript | TECH AT 60'
DESCRIPTION='Learn web development with TECH AT 60. Start with HTML tags, headings, links, images, lists, forms and semantic markup, then progress through CSS and JavaScript. Short English tutorials with code examples and beginner exercises. Watch in lesson order and practice one idea at a time.'
def pages(request):
 while request:
  response=request.execute()
  yield from response.get('items',[])
  token=response.get('nextPageToken')
  if not token:return
  # HttpRequest URI already includes all existing filters; append the next page safely.
  from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
  u=urlsplit(request.uri);q=dict(parse_qsl(u.query));q['pageToken']=token;request.uri=urlunsplit((u.scheme,u.netloc,u.path,urlencode(q),u.fragment))
def sync():
 cfg=json.loads((W/'youtube-publishing.json').read_text())
 creds=Credentials.from_authorized_user_file(str(W/'.youtube-auth/token.json'))
 if creds.expired:creds.refresh(Request());save(W/'.youtube-auth/token.json',json.loads(creds.to_json()),True)
 y=build('youtube','v3',credentials=creds,cache_discovery=False)
 assert cfg['channelId'] in {c['id'] for c in y.channels().list(part='id',mine=True).execute().get('items',[])},'Wrong channel'
 pid=cfg.get('playlistId')
 if not pid:
  existing=[p for p in pages(y.playlists().list(part='snippet,status',mine=True,maxResults=50)) if p['snippet']['title']==TITLE]
  if len(existing)>1:raise RuntimeError('Multiple matching playlists; inspect before selecting')
  pl=existing[0] if existing else y.playlists().insert(part='snippet,status',body={'snippet':{'title':TITLE,'description':DESCRIPTION,'defaultLanguage':'en'},'status':{'privacyStatus':'public'}}).execute()
  pid=pl['id'];cfg['playlistId']=pid;save(W/'youtube-publishing.json',cfg)
 for attempt in range(12):
  found=y.playlists().list(part='snippet,status',id=pid).execute().get('items',[])
  if found:break
  time.sleep(2)
 if not found:raise RuntimeError('Playlist created but not yet readable; retry with saved playlistId')
 pl=found[0]
 assert pl['snippet']['channelId']==cfg['channelId']
 members=list(pages(y.playlistItems().list(part='snippet',playlistId=pid,maxResults=50)))
 order=[p['snippet']['resourceId']['videoId'] for p in members]
 items={p['snippet']['resourceId']['videoId']:p for p in members}
 added=[];ordered=[]
 rows=[(1,W/'html-introduction/out/youtube-upload-receipt.json')]+[(row['videoNumber'],B/'videos'/f'{row["videoNumber"]:02d}'/'youtube-upload-receipt.json') for row in json.loads((B/'queue.json').read_text())]
 for number,rp in rows:
  if not rp.exists():continue
  r=json.loads(rp.read_text());vid=r.get('videoId')
  if not vid and (B/'verified-playlist-videos.json').exists():
   known=json.loads((B/'verified-playlist-videos.json').read_text()).get(str(number))
   if known:
    check=y.videos().list(part='snippet',id=known['videoId']).execute().get('items',[])
    if check and check[0]['snippet']['channelId']==cfg['channelId'] and check[0]['snippet']['title']==known['title']:vid=known['videoId']
  if not vid or r.get('state') in ('failed','rejected'):continue
  position=len(ordered);ordered.append(vid)
  snippet=dict(playlistId=pid,resourceId=dict(kind='youtube#video',videoId=vid),position=position)
  if vid not in items:
   item=y.playlistItems().insert(part='snippet',body=dict(snippet=snippet)).execute();items[vid]=item;order.insert(position,vid);added.append(number)
  elif order.index(vid)!=position:
   y.playlistItems().update(part='snippet',body=dict(id=items[vid]['id'],snippet=snippet)).execute();order.remove(vid);order.insert(position,vid)
 actual=list(pages(y.playlistItems().list(part='snippet',playlistId=pid,maxResults=50)))
 assert [p['snippet']['resourceId']['videoId'] for p in actual][:len(ordered)]==ordered,'Playlist order mismatch'
 result=dict(playlistId=pid,url='https://www.youtube.com/playlist?list='+pid,title=pl['snippet']['title'],privacyStatus=pl['status']['privacyStatus'],episodesAdded=added,orderedVideoIds=ordered)
 save(B/'playlist-status.json',result);print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':
 with (B/'.playlist.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);sync()
