"""Replace the demonstrably incomplete Short while preserving the old upload."""
import fcntl,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
ROOT=Path(__file__).resolve().parent.parent;D=ROOT/'series/videos/18'
sys.path.insert(0,str(ROOT/'tools'));from youtube_upload import save
from daily_schedule import production_environment
with (ROOT/'series/.production.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 y=build('youtube','v3',credentials=Credentials.from_authorized_user_file(str(ROOT/'.youtube-auth/token.json')),cache_discovery=False)
 old_id='9enXNnWJxG0';old=y.videos().list(part='snippet,status,processingDetails,contentDetails',id=old_id).execute()['items'][0]
 assert old['snippet']['channelId']=='UC7F3e0NsVP37sqroVmYxiFw'
 assert old['processingDetails']['processingStatus']=='processing' and old['contentDetails']['duration']=='P0D'
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(D/'video.mp4')]))
 v=next(s for s in info['streams'] if s['codec_type']=='video');assert v['width']==1080 and v['height']==1920 and v['nb_frames']=='1800' and abs(float(info['format']['duration'])-60)<.1
 assert any(s['codec_type']=='audio' for s in info['streams'])
 rp=D/'youtube-upload-receipt.json';receipt=json.loads(rp.read_text())
 assert not receipt.get('videoId') and receipt['sha256']==hashlib.file_digest((D/'video.mp4').open('rb'),'sha256').hexdigest()
 save(D/'stuck-upload-evidence.json',old)
 y.videos().update(part='status',body=dict(id=old_id,status=dict(privacyStatus='private',selfDeclaredMadeForKids=False))).execute()
 rp.rename(D/'youtube-incomplete-upload-receipt.json')
 print('Hidden stuck upload; uploading verified replacement.',flush=True)
 subprocess.run([sys.executable,str(ROOT/'tools/youtube_upload.py'),'--noninteractive','--credentials',str(next(ROOT.glob('client_secret*.json'))),'--metadata',str(D/'youtube-metadata.json'),'--publish-now'],cwd=ROOT,env=production_environment(),check=True)
 new=json.loads(rp.read_text());assert new['state']=='published'
 new['replacesVideoId']=old_id;save(rp,new)
 known=json.loads((ROOT/'series/verified-playlist-videos.json').read_text());known['18']=dict(videoId=new['videoId'],channelId=new['channelId'],title=new['title'],source='Verified replacement for zero-duration stuck upload');save(ROOT/'series/verified-playlist-videos.json',known)
 q=json.loads((ROOT/'series/queue.json').read_text())
 for row in q:
  if row['videoNumber']==18:row.update(status='published',videoId=new['videoId'],url=new['url']);row.pop('error',None)
 save(ROOT/'series/queue.json',q)
 pid=json.loads((ROOT/'youtube-publishing.json').read_text())['playlistId']
 items=y.playlistItems().list(part='snippet',playlistId=pid,maxResults=50).execute().get('items',[])
 for item in items:
  if item['snippet']['resourceId']['videoId']==old_id:y.playlistItems().delete(id=item['id']).execute()
 subprocess.run([sys.executable,str(ROOT/'channel-seo/web_playlist.py')],cwd=ROOT,check=True)
 print('REPAIRED',new['url'],flush=True)
