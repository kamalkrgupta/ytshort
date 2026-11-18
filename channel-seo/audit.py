import json,sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
W=Path(__file__).resolve().parent.parent;B=W/'channel-seo'
sys.path.insert(0,str(W/'tools'));from youtube_upload import save
c=Credentials.from_authorized_user_file(str(W/'.youtube-auth/token.json'))
if c.expired:c.refresh(Request());save(W/'.youtube-auth/token.json',json.loads(c.to_json()),True)
y=build('youtube','v3',credentials=c,cache_discovery=False)
channel=y.channels().list(part='snippet,brandingSettings,statistics,contentDetails',mine=True).execute()['items']
channel=next(v for v in channel if v['id']=='UC7F3e0NsVP37sqroVmYxiFw')
u=channel['contentDetails']['relatedPlaylists']['uploads'];ids=[];token=None
while True:
 r=y.playlistItems().list(part='snippet',playlistId=u,maxResults=50,pageToken=token).execute();ids += [v['snippet']['resourceId']['videoId'] for v in r.get('items',[])];token=r.get('nextPageToken')
 if not token:break
videos=[]
for i in range(0,len(ids),50):videos+=y.videos().list(part='snippet,status,statistics,contentDetails',id=','.join(ids[i:i+50])).execute().get('items',[])
playlists=y.playlists().list(part='snippet,status,contentDetails',mine=True,maxResults=50).execute().get('items',[])
sections=y.channelSections().list(part='snippet,contentDetails',mine=True).execute().get('items',[])
result=dict(channel=channel,videos=videos,playlists=playlists,sections=sections)
save(B/'before.json',result)
print(json.dumps(dict(channel=channel['snippet'],branding=channel.get('brandingSettings'),statistics=channel.get('statistics'),videos=[dict(id=v['id'],title=v['snippet']['title'],tags=v['snippet'].get('tags',[]),description=v['snippet']['description'][:220],visibility=v['status']['privacyStatus'],views=v.get('statistics',{}).get('viewCount')) for v in videos],playlists=[dict(id=p['id'],title=p['snippet']['title'],description=p['snippet']['description'],count=p['contentDetails']['itemCount']) for p in playlists],sections=sections),indent=2))
