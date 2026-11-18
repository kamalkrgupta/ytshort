"""Verify every course upload, release timestamp and exact playlist ordering."""
import json,subprocess,sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
B=Path(__file__).resolve().parent;W=B.parent
sys.path.insert(0,str(W/'tools'))
from youtube_upload import save

def main():
 subprocess.run([sys.executable,B/'audit_schedule.py','--all','--repair'],check=True,stdout=subprocess.DEVNULL)
 report=json.loads((B/'schedule-audit-2026-11-04.json').read_text());checks=report['checks']
 if report['needsAttention']:
  print(json.dumps({'status':'pending','episodes':report['needsAttention'],'states':{r['episode']:r['liveState'] for r in checks if r['episode'] in report['needsAttention']}}));return 2
 assert report['localScheduleCorrect'] and report['liveVerified'] and len(checks)==50
 ids=[r['videoId'] for r in checks];assert len(set(ids))==50 and all(ids)
 assert all(r['liveState']=='ready' and r['uploadStatus']=='processed' for r in checks)
 from google.oauth2.credentials import Credentials
 from googleapiclient.discovery import build
 cfg=json.loads((B/'youtube-publishing.json').read_text());y=build('youtube','v3',credentials=Credentials.from_authorized_user_file(str(W/'.youtube-auth/token.json')),cache_discovery=False)
 members=[];token=None
 while True:
  result=y.playlistItems().list(part='snippet',playlistId=cfg['playlistId'],maxResults=50,pageToken=token).execute();members.extend(v['snippet']['resourceId']['videoId'] for v in result['items']);token=result.get('nextPageToken')
  if not token:break
 assert members==ids,'Playlist must contain exactly these fifty episodes in order'
 summary=dict(verifiedAt=datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),status='complete',channelId=cfg['channelId'],uploaded=50,public=sum(r['visibility']=='public' for r in checks),scheduled=sum(r['visibility']=='private' for r in checks),allProcessed=True,uniqueVideoIds=50,playlistOrdered=True,playlistUrl='https://www.youtube.com/playlist?list='+cfg['playlistId'],dailyRelease='Two episodes at 14:00 Asia/Kolkata',finalRelease=checks[-1]['expectedAt'],videos=[dict(episode=r['episode'],videoId=r['videoId'],visibility=r['visibility'],expectedAt=r['expectedAt'],actualPublishAt=r.get('actualPublishAt')) for r in checks])
 save(B/'upload-all-verification.json',summary)
 print(json.dumps({k:v for k,v in summary.items() if k!='videos'},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
