import json
from datetime import datetime,timezone
from optimize import ROOT,OUT,CHANNEL,EXPERIMENTS,BAD,PLAYLIST,save
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
backup=json.loads((OUT/'experiment-backup.json').read_text())
y=build('youtube','v3',credentials=Credentials.from_authorized_user_file(str(ROOT/'.youtube-auth/token.json')),cache_discovery=False)
ids=[c['videoId'] for c in backup['changes']]
current=y.videos().list(part='snippet,status,statistics',id=','.join(ids)).execute()['items']
assert len(current)==len(ids)
originals={c['videoId']:c['before'] for c in backup['changes']}
for v in current:
 vid=v['id'];s=v['snippet'];assert s['channelId']==CHANNEL
 assert v['status']==originals[vid]['status']
 assert not BAD.intersection(t.lower() for t in s.get('tags',[]))
 if vid in EXPERIMENTS:
  title,intro,question,next_id=EXPERIMENTS[vid]
  assert s['title']==title and s['description'].startswith(intro)
  assert question in s['description'] and PLAYLIST in s['description'] and next_id in s['description']
 for pattern in ('series/videos/*/youtube-upload-receipt.json','special-shorts/*/youtube-upload-receipt.json'):
  for receipt in ROOT.glob(pattern):
   if json.loads(receipt.read_text()).get('videoId')!=vid:continue
   p=receipt.with_name('youtube-metadata.json')
   if p.exists():
    m=json.loads(p.read_text());b=OUT/'local-backups'/str(p.relative_to(ROOT))
    if not b.exists():save(b,m)
    m.update({k:s[k] for k in ('title','description','tags')});save(p,m)
sections=y.channelSections().list(part='snippet,contentDetails',mine=True).execute()['items']
assert any(s['snippet']['position']==0 and 'PLEJDqf_3IqMU' in s.get('contentDetails',{}).get('playlists',[]) for s in sections)
save(OUT/'verified.json',dict(verifiedAt=datetime.now(timezone.utc).isoformat(),videos=current,sections=sections,releaseSettingsPreserved=True))
save(OUT/'applied.json',dict(complete=True,verifiedVideos=len(current),titleDescriptionExperiments=6,tagCleanupVideos=1,webPlaylistPosition=0,releaseSettingsPreserved=True))
print('Verified all seven videos, six title/description experiments, homepage order, unchanged release settings and active local metadata.')
