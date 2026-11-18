import json,sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
root=Path(__file__).resolve().parent.parent
c=Credentials.from_authorized_user_file(str(root/'.youtube-auth/token.json'))
if c.expired:c.refresh(Request())
y=build('youtube','v3',credentials=c,cache_discovery=False)
rows=[]
for folder in ('series/videos','agile-masterclass/episodes'):
 for p in sorted((root/folder).glob('*/youtube-upload-receipt.json')):
  r=json.loads(p.read_text())
  if not r.get('videoId'):continue
  items=y.videos().list(part='snippet,status',id=r['videoId']).execute().get('items',[])
  for v in items:rows.append(dict(title=v['snippet']['title'],videoId=v['id'],visibility=v['status']['privacyStatus'],publishAt=v['status'].get('publishAt'),uploadStatus=v['status'].get('uploadStatus')))
result=dict(checkedAt=datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),videos=rows)
(root/'series/live-status.json').write_text(json.dumps(result,indent=2)+'\n')
for r in rows:
 if r['visibility']!='public':print(json.dumps(r))
