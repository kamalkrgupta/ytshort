"""Keep independent local copies and a register of verified published Shorts."""
import argparse,csv,fcntl,hashlib,json,os,re,shutil,tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from youtube_upload import ROOT,save
ARCHIVE=ROOT/'Published Shorts';ZONE=ZoneInfo('Asia/Kolkata')
CHANNEL='UC7F3e0NsVP37sqroVmYxiFw'
FIELDS=['lesson','title','videoId','url','youtubePublishedAt','publishedIST','plannedPublishAt','verifiedAt','currentVisibility','processingStatus','file','sha256']
def checksum(path):
 with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def eligible(item):
 s=item['status'];return s['privacyStatus']=='public' and (s.get('uploadStatus')=='processed' or item.get('processingDetails',{}).get('processingStatus')=='succeeded')
def source_entries():
 paths=[ROOT/'html-introduction/out/youtube-upload-receipt.json']+sorted((ROOT/'series/videos').glob('*/youtube-upload-receipt.json'))
 result=[]
 for rp in paths:
  if not rp.exists():continue
  receipt=json.loads(rp.read_text())
  if receipt.get('videoId'):
   number=1 if rp.parent==ROOT/'html-introduction/out' else int(rp.parent.name)
   result.append((number,rp,receipt))
 return result
def read_register():
 p=ARCHIVE/'published.json';return json.loads(p.read_text()).get('videos',[]) if p.exists() else []
def write_register(rows):
 rows.sort(key=lambda r:(int(r['lesson']),r.get('youtubePublishedAt',''),r['videoId']))
 save(ARCHIVE/'published.json',dict(checkedAt=datetime.now(ZONE).isoformat(),videos=rows))
 tmp=ARCHIVE/'published.csv.tmp'
 with tmp.open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=FIELDS,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
 tmp.replace(ARCHIVE/'published.csv')
 text='# Published Shorts\n\nUpdated: '+datetime.now(ZONE).isoformat()+'\n\n| Lesson | Short | Published (IST, YouTube timestamp) | Current visibility | Local file |\n|---|---|---|---|---|\n'
 for r in rows:text+=f'| {r["lesson"]} | [{r["title"].replace("|"," / ")}]({r["url"]}) | {r["publishedIST"]} | {r["currentVisibility"]} | {r["file"]} |\n'
 (ARCHIVE/'published.md').write_text(text)
def archive_one(number,rp,receipt,item,rows):
 assert item['snippet']['channelId']==CHANNEL
 if not eligible(item):return False
 dest=rp.parent;mp=dest/'youtube-metadata.json';meta=json.loads(mp.read_text())
 source=(dest/meta['video']).resolve();assert source.is_relative_to(ROOT)
 digest=checksum(source)
 if receipt.get('sha256') and digest!=receipt['sha256']:raise RuntimeError('Local video no longer matches published receipt; refusing incorrect archive copy')
 vid=item['id'];previous=next((r for r in rows if r['videoId']==vid),None)
 title=item['snippet']['title'];safe=re.sub(r'[^\w .-]+',' ',title);safe=re.sub(r'\s+',' ',safe).strip()[:95]
 name=previous['file'] if previous else f'{number:03d} - {safe} - {vid}.mp4'
 target=ARCHIVE/name
 if not target.exists():
  fd,temporary=tempfile.mkstemp(prefix='.copy-',suffix='.mp4',dir=ARCHIVE);os.close(fd)
  try:
   shutil.copy2(source,temporary)
   assert checksum(temporary)==digest
   os.replace(temporary,target)
  finally:Path(temporary).unlink(missing_ok=True)
 else:
  if checksum(target)!=digest:raise RuntimeError('Existing archived copy differs; preserve it for inspection')
 published=item['snippet']['publishedAt'];local=datetime.fromisoformat(published.replace('Z','+00:00')).astimezone(ZONE).isoformat()
 record=dict(lesson=number,title=title,videoId=vid,url='https://www.youtube.com/shorts/'+vid,youtubePublishedAt=published,publishedIST=local,plannedPublishAt=meta.get('publishAt'),verifiedAt=datetime.now(ZONE).isoformat(),currentVisibility='public',processingStatus=item.get('processingDetails',{}).get('processingStatus',item['status'].get('uploadStatus')),file=name,sha256=digest)
 detail=ARCHIVE/'records'/vid;detail.mkdir(parents=True,exist_ok=True)
 save(detail/'publication.json',record);shutil.copy2(rp,detail/'upload-receipt.json');shutil.copy2(mp,detail/'youtube-metadata.json')
 if previous:previous.update(record)
 else:rows.append(record)
 return previous is None
def sync(youtube=None):
 ARCHIVE.mkdir(exist_ok=True)
 with (ARCHIVE/'.archive.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  if youtube is None:
   creds=Credentials.from_authorized_user_file(str(ROOT/'.youtube-auth/token.json'))
   if creds.expired:creds.refresh(Request());save(ROOT/'.youtube-auth/token.json',json.loads(creds.to_json()),True)
   youtube=build('youtube','v3',credentials=creds,cache_discovery=False)
  entries=source_entries();rows=read_register();ids=list(dict.fromkeys([r['videoId'] for _,_,r in entries]+[r['videoId'] for r in rows]));live={}
  for n in range(0,len(ids),50):
   for item in youtube.videos().list(part='snippet,status,processingDetails',id=','.join(ids[n:n+50])).execute().get('items',[]):live[item['id']]=item
  added=0;errors=[]
  for row in rows:
   item=live.get(row['videoId']);row['currentVisibility']=item['status']['privacyStatus'] if item else 'unavailable';row['verifiedAt']=datetime.now(ZONE).isoformat()
  for number,rp,receipt in entries:
   item=live.get(receipt['videoId'])
   if not item:continue
   try:added+=archive_one(number,rp,receipt,item,rows)
   except Exception as e:errors.append(dict(lesson=number,videoId=receipt['videoId'],error=type(e).__name__,message=str(e)[:160]))
  write_register(rows)
  save(ARCHIVE/'archive-status.json',dict(checkedAt=datetime.now(ZONE).isoformat(),archived=len(rows),added=added,errors=errors))
  print(f'Published Shorts archive: {len(rows)} videos, {added} new, {len(errors)} errors.',flush=True)
  if errors:raise RuntimeError('Some published Shorts need archive inspection; see archive-status.json')
if __name__=='__main__':sync()
