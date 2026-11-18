"""Resumable original tech Shorts; each verified artifact is uploaded at most once."""
import argparse,asyncio,concurrent.futures,csv,hashlib,json,math,random,shutil,subprocess,sys,threading,time
from datetime import datetime,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import edge_tts
from content import TOPICS
B=Path(__file__).resolve().parent;W=B.parent;ZONE=ZoneInfo('Asia/Kolkata');CHANNEL='UC7F3e0NsVP37sqroVmYxiFw'
sys.path.insert(0,str(W/'tools'));from youtube_upload import save
VOICE='en-US-GuyNeural';RATE='-15%';IDS=['hook','idea','demo','compare','takeaway','close'];COMP=['Hook','Idea','Demo','Compare','Takeaway','Close'];LOCK=threading.RLock()
def load(p):return json.loads(p.read_text())
def d(n):return B/'videos'/f'{n:02d}'
def project(n):return d(n)/'project'
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
def duration(p):return float(probe(p)['format']['duration'])
def update(n,**values):
 with LOCK:
  q=load(B/'queue.json')
  for r in q:
   if r['number']==n:r.update(values,updatedAt=datetime.now(ZONE).isoformat());r.pop('error',None)
  save(B/'queue.json',q)
  with (B/'posting-calendar.csv').open('w') as f:
   writer=csv.DictWriter(f,fieldnames=['number','title','publishLocal','publishAt','status','url']);writer.writeheader();writer.writerows({k:r.get(k,'') for k in writer.fieldnames} for r in q)
def init():
 p=B/'queue.json'
 if p.exists():return load(p)
 before=load(B/'channel-before.json');existing={v['snippet']['title'].lower() for v in before['videos']};times={datetime.fromisoformat(v['status']['publishAt'].replace('Z','+00:00')) for v in before['videos'] if v['status'].get('publishAt')}
 now=datetime.now(ZONE);first=now.replace(hour=20,minute=0,second=0,microsecond=0)
 if first<now+timedelta(hours=2):first+=timedelta(days=1)
 topics=TOPICS.copy();random.Random(20261116).shuffle(topics);q=[]
 for i,t in enumerate(topics):
  at=first+timedelta(days=i)
  assert at.astimezone(timezone.utc) not in times and t['title'].lower() not in existing
  q.append(dict(number=i+1,**t,publishLocal=at.isoformat(),publishAt=at.astimezone(timezone.utc).isoformat(),status='planned',accent=['#ffab73','#8ee4c8','#b7b4ff','#8fc9ff'][i%4]))
 save(p,q);cfg=load(W/'youtube-publishing.json');cfg.pop('playlistId',None);cfg.update(queueFile=str(p),scheduleStatus='batch_in_progress',descriptionSuffix='Subscribe to TECH AT 60 for clear tech explainers.',dailySchedule=dict(times=['20:00'],timezone='Asia/Kolkata',videosPerDay=1,startDate=first.date().isoformat()))
 save(B/'youtube-publishing.json',cfg);save(B/'voice-preferences.json',dict(engine='Microsoft Edge TTS',voice=VOICE,rate=RATE,leadIn=.25,language='en',source='Same narrator as the approved project Shorts and newer English cartoon videos'))
 sources='# Topic research — November 16, 2026\n\nA shuffled editorial selection of 20 timely topics, not a measured popularity ranking. Primary sources checked before scripts were written. Videos explain the underlying idea rather than announce availability of future products. Original diagram illustrations do not represent real product interfaces or benchmark results.\n\n'
 for t in q:sources+=f'- **{t["title"]}** — {t["source"]}\n'
 (B/'Sources.md').write_text(sources);return q

def run(cmd,p,log):
 subprocess.run(list(map(str,cmd)),cwd=p,stdout=log,stderr=subprocess.STDOUT,check=True)
def storyboard(t,ds):
 text=f'# {t["title"]}\n\n9:16; 1080×1920; 30 fps; 60 seconds. Edge TTS {VOICE}, rate {RATE}.\nAudience: curious tech beginners. Original midnight/mint/orange SVG and UI diagrams; meaningful motion, large type and phone safe areas. No filmed or generated product footage.\n\n'
 visuals=[t['headline'],t['meaning'],t['example'],t['comparison'],t['caution'],t['question']]
 for ident,secs,line,visual in zip(IDS,ds,t['lines'],visuals):text+=f'## {ident} ({secs}s)\nNarration: {line}\nOn-screen key idea: {visual}\nVisual: topic-specific diagram or comparison; flow labels: {" → ".join(t["flow"])}.\nMotion: Framer Motion reveals cards and labels; packet markers or illustration elements move on the virtual clock. GSAP draws the section rule. Title visible within 0.1s, main visual begins within 0.3s. Transition: fade.\n\n'
 text+='Primary source: '+t['source']+'\n';return text
async def synth(t):
 n=t['number'];v=d(n)/'voice';v.mkdir(parents=True,exist_ok=True);sem=asyncio.Semaphore(3)
 async def one(ident,line):
  key=hashlib.sha256(json.dumps([VOICE,RATE,line,edge_tts.__version__]).encode()).hexdigest();stamp=v/(ident+'.sha256');wav=v/(ident+'.wav')
  if wav.exists() and stamp.exists() and stamp.read_text()==key:return
  async with sem:
   for attempt in range(3):
    try:
     raw=v/(ident+'.mp3');await edge_tts.Communicate(line,VOICE,rate=RATE).save(str(raw));trim='silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.03'
     subprocess.run(['ffmpeg','-y','-v','error','-i',str(raw),'-af',f'{trim},areverse,{trim},areverse','-ar','48000','-ac','1',str(wav)],check=True);stamp.write_text(key);raw.unlink();return
    except Exception:
     if attempt==2:raise
     await asyncio.sleep(2**attempt)
 await asyncio.gather(*(one(i,line) for i,line in zip(IDS,t['lines'])))

def prepare(t):
 n=t['number'];folder=d(n);folder.mkdir(parents=True,exist_ok=True)
 if (folder/'youtube-upload-receipt.json').exists():raise RuntimeError('Existing upload receipt; do not prepare a revision')
 update(n,status='producing');(folder/'storyboard.md').write_text(storyboard(t,[8,10,12,12,10,8]));asyncio.run(synth(t))
 ds=[math.ceil((duration(folder/'voice'/(ident+'.wav'))+.7)*2)/2 for ident in IDS]
 if sum(ds)>60:raise RuntimeError(f'Voice {n} needs {sum(ds)} seconds; shorten script')
 for i in range(round((60-sum(ds))*2)):ds[[2,3,1,4,0,5][i%6]]+=.5
 p=project(n);p.mkdir(exist_ok=True)
 for src in (B/'template').iterdir():
  if src.name in ('node_modules','dist','out','voice','lesson.json','narration.json'):continue
  if src.is_dir():shutil.copytree(src,p/src.name,dirs_exist_ok=True)
  else:shutil.copy2(src,p/src.name)
 if not (p/'node_modules').exists():(p/'node_modules').symlink_to((B/'template/node_modules').resolve(),target_is_directory=True)
 narration=dict(voice=VOICE,rate=RATE,pitch='+0Hz',leadIn=.25,scenes=dict(zip(IDS,t['lines'])))
 for target in (folder,p):save(target/'lesson.json',t);save(target/'narration.json',narration);(target/'storyboard.md').write_text(storyboard(t,ds))
 save(folder/'timeline.json',dict(zip(IDS,ds)))
 (p/'src/scenes/index.js').write_text("import {"+','.join(COMP)+"} from './Lesson.jsx';\nexport const scenes = [\n"+'\n'.join(f"{{id:'{ident}',duration:{secs},transition:'fade',component:{comp}}}," for ident,secs,comp in zip(IDS,ds,COMP))+"\n];\n")
 if (p/'voice').exists():shutil.rmtree(p/'voice')
 shutil.copytree(folder/'voice',p/'voice')
 with (folder/'prepare.log').open('w') as log:
  run(['node','tools/voiceover.mjs','--measure'],p,log);shutil.copy2(p/'voice/manifest.json',folder/'voice/manifest.json')
  run(['npm','run','build'],p,log);run(['node','tools/record.mjs','--stills'],p,log)
 text=(folder/'prepare.log').read_text();assert 'WARNING:' not in text and 'Page errors:' not in text
 if (folder/'stills').exists():shutil.rmtree(folder/'stills')
 shutil.copytree(p/'out/stills',folder/'stills')
 # One additional early sample catches animations that are absent from settled stills.
 with (folder/'motion.log').open('w') as log:run(['node','tools/record.mjs','--at','0.8,2.5'],p,log)
 if (folder/'motion-stills').exists():shutil.rmtree(folder/'motion-stills')
 shutil.copytree(p/'out/stills',folder/'motion-stills')
 description=t['meaning']+' '+t['example']+'\n\n'+t['caution']+'\n\n'+t['question']+'\nSubscribe to @Techat60 for clear, beginner-friendly tech explainers.\n\nSource checked November 16, 2026:\n'+t['source']+'\n\nOriginal illustrative diagrams; not a product demonstration or benchmark.\n\n#Technology #TechExplained #Shorts'
 save(folder/'youtube-metadata.json',dict(title=t['title'],description=description,tags=[t['slug'].replace('-',' '),'technology explained','tech for beginners','TECH AT 60'],video='video.mp4',publishAt=t['publishAt']))
 (folder/'youtube-upload-details.txt').write_text(t['title']+'\n\n'+description)
 update(n,status='prepared');print('PREPARED',n,t['slug'],'speech',round(sum(duration(folder/'voice'/(ident+'.wav')) for ident in IDS),1),flush=True)

def render(t):
 n=t['number'];folder=d(n);p=project(n)
 if (folder/'youtube-upload-receipt.json').exists():raise RuntimeError('Do not replace an uploaded artifact')
 assert (folder/'reviewed.json').exists() and load(folder/'reviewed.json').get('approved')
 update(n,status='rendering');partial=folder/'video.partial.mp4'
 with (folder/'render.log').open('w') as log:run(['node','tools/record.mjs','--out',partial],p,log)
 info=probe(partial);v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
 assert (v['width'],v['height'],v['r_frame_rate'],v['nb_frames'])==(1080,1920,'30/1','1800') and abs(float(info['format']['duration'])-60)<.1 and a['codec_name']=='aac'
 partial.replace(folder/'video.mp4');save(folder/'verification.json',dict(verifiedAt=datetime.now(ZONE).isoformat(),voice=VOICE,rate=RATE,sha256=hashlib.sha256((folder/'video.mp4').read_bytes()).hexdigest(),probe=info,narrationTiming='Measured, not auditioned'))
 update(n,status='rendered');print('RENDERED',n,t['slug'],flush=True)

def upload(t):
 n=t['number'];folder=d(n);assert (folder/'verification.json').exists() and load(folder/'reviewed.json')['approved']
 assert datetime.fromisoformat(t['publishAt'])>datetime.now(timezone.utc),'Expired slot: stop instead of publishing immediately'
 credential=next(W.glob('client_secret*.json'))
 with (folder/'upload.log').open('w') as log:run([sys.executable,W/'tools/youtube_upload.py','--credentials',credential,'--metadata',folder/'youtube-metadata.json','--config',B/'youtube-publishing.json','--noninteractive'],W,log)
 receipt=load(folder/'youtube-upload-receipt.json');assert receipt['state']=='scheduled'
 update(n,status='scheduled',videoId=receipt['videoId'],url=receipt['url']);print('SCHEDULED',n,t['slug'],receipt['verifiedPublishAt'],flush=True)

def setup_playlist():
 from google.oauth2.credentials import Credentials
 from google.auth.transport.requests import Request
 from googleapiclient.discovery import build
 cfg=load(B/'youtube-publishing.json');c=Credentials.from_authorized_user_file(str(W/'.youtube-auth/token.json'))
 if c.expired:c.refresh(Request());save(W/'.youtube-auth/token.json',json.loads(c.to_json()),True)
 y=build('youtube','v3',credentials=c,cache_discovery=False);assert CHANNEL in {v['id'] for v in y.channels().list(part='id',mine=True).execute()['items']}
 title='Tech Explained in 60 Seconds | AI, Gadgets & Digital Life'
 if not cfg.get('playlistId'):
  ps=y.playlists().list(part='snippet,status',mine=True,maxResults=50).execute().get('items',[]);matches=[p for p in ps if p['snippet']['title']==title];assert len(matches)<=1
  p=matches[0] if matches else y.playlists().insert(part='snippet,status',body=dict(snippet=dict(title=title,description='Short, beginner-friendly explanations of AI, security, gadgets, smart homes and connectivity. One clear idea and one practical takeaway per video. TECH AT 60.',defaultLanguage='en'),status=dict(privacyStatus='public'))).execute();cfg['playlistId']=p['id'];save(B/'youtube-publishing.json',cfg)
 print('Playlist configured:',cfg['playlistId'],flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['init','prepare','render','upload','setup']);ap.add_argument('--numbers',nargs='+',type=int);ap.add_argument('--workers',type=int,default=2);args=ap.parse_args();q=init();selected=[t for t in q if not args.numbers or t['number'] in args.numbers]
 if args.stage=='init':print([(t['number'],t['slug'],t['publishLocal']) for t in q])
 elif args.stage=='setup':setup_playlist()
 elif args.stage=='upload':
  for t in selected:upload(t)
 else:
  failures=[]
  with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
   futures={ex.submit(prepare if args.stage=='prepare' else render,t):t for t in selected}
   for f in concurrent.futures.as_completed(futures):
    t=futures[f]
    try:f.result()
    except Exception as e:
     with LOCK:
      q=load(B/'queue.json');next(r for r in q if r['number']==t['number']).update(status='needs_attention',error=type(e).__name__+': '+str(e));save(B/'queue.json',q)
     failures.append((t['number'],str(e)));print('FAILED',t['number'],str(e),flush=True)
  if failures:raise RuntimeError(str(failures))
