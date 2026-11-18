import json,sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
W=Path(__file__).resolve().parent.parent;B=W/'channel-seo'
sys.path.insert(0,str(W/'tools'));from youtube_upload import save
before=json.loads((B/'before.json').read_text());plan=json.loads((B/'changes.json').read_text());applied=json.loads((B/'applied.json').read_text())
y=build('youtube','v3',credentials=Credentials.from_authorized_user_file(str(W/'.youtube-auth/token.json')),cache_discovery=False)
c=y.channels().list(part='snippet,brandingSettings,statistics',id=before['channel']['id']).execute()['items'][0]
assert c['brandingSettings']['channel']['description']==plan['channelDescription'];assert c['brandingSettings']['channel']['keywords']==plan['channelKeywords']
ids=[v['id'] for v in before['videos']];videos=y.videos().list(part='snippet,status',id=','.join(ids)).execute()['items'];removed={t.lower() for t in plan['removeTags']}
fixed=[]
for v in videos:
 s=v['snippet'];kind='AI' if 'Ep ' in s['title'] else 'Agile' if 'Episode ' in s['title'] else 'Web'
 assert not any(t.lower() in removed for t in s.get('tags',[]))
 url='https://www.youtube.com/playlist?list='+applied['playlistIds'][kind]
 if url not in s['description']:
  snippet={k:x for k,x in s.items() if k in ('title','description','tags','categoryId','defaultLanguage','defaultAudioLanguage')};snippet['description']+='\n\nWatch the course in order: '+url
  y.videos().update(part='snippet',body=dict(id=v['id'],snippet=snippet)).execute();fixed.append(v['id'])
 # Status was never included in any SEO update; verify that scheduled times stayed intact.
 old=next(o for o in before['videos'] if o['id']==v['id'])
 assert v['status'].get('publishAt')==old['status'].get('publishAt')
sections=y.channelSections().list(part='snippet,contentDetails',channelId=c['id']).execute().get('items',[])
assert set(applied['playlistIds'].values()) <= {p for s in sections for p in s.get('contentDetails',{}).get('playlists',[])}
checked=y.videos().list(part='snippet',id=','.join(ids)).execute()['items']
assert all('https://www.youtube.com/playlist?list=' in v['snippet']['description'] for v in checked)
save(B/'verified.json',dict(channelId=c['id'],channelSettingsVerified=True,videosVerified=len(videos),homepageSectionsVerified=len(sections),additionalPlaylistLinks=fixed,scheduledTimesPreserved=True,statistics=c['statistics']))
print('Verified channel metadata,',len(videos),'video descriptions/tags,',len(sections),'homepage sections and unchanged release times.')
