"""Finish the five project Shorts using the approved cartoon narrator."""
import argparse,asyncio,csv,fcntl,hashlib,json,math,os,shutil,subprocess,sys,time
from datetime import datetime,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import edge_tts
from content import DATA
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1];SERIES=ROOT/'series';ZONE=ZoneInfo('Asia/Kolkata')
IDS=['hook','idea','code','result','tip','caution','try','close'];COMP=['Hook','Idea','Code','Result','Tip','Caution','Try','Close']
VOICE='en-US-GuyNeural';RATE='-15%'
sys.path.insert(0,str(ROOT/'tools'));from youtube_upload import save

def run(cmd,cwd=None):
 subprocess.run(list(map(str,cmd)),cwd=cwd or ROOT,check=True)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def duration(p):return float(probe(p)['format']['duration'])
def dest(n):return SERIES/'videos'/f'{n:02d}'
def project(n):return dest(n)/'project'
def load(p):return json.loads(p.read_text())
def state(**values):
 p=BASE/'batch-state.json';d=load(p) if p.exists() else {};d.update(values,updatedAt=datetime.now(ZONE).isoformat());save(p,d)
def plan():
 backup=BASE/'before-batch.json'
 if not backup.exists():save(backup,{name:load(SERIES/name) for name in ('catalog.json','queue.json')})
 planpath=BASE/'schedule-plan.json'
 if planpath.exists():return load(planpath)
 start=datetime(2026,11,17,11,tzinfo=ZONE);rows=[]
 for i,n in enumerate(DATA):
  at=start+timedelta(days=i//2,hours=5*(i%2));rows.append(dict(videoNumber=n,title=DATA[n]['title'],publishLocal=at.isoformat(),publishAt=at.astimezone(timezone.utc).isoformat()))
 save(planpath,rows)
 for name in ('catalog.json','queue.json'):
  d=load(SERIES/name)
  for r in d:
   if r['videoNumber'] in DATA:
    match=next(v for v in rows if v['videoNumber']==r['videoNumber']);r.update({k:match[k] for k in ('publishLocal','publishAt')});r['status']='planned'
  save(SERIES/name,d)
 save(BASE/'voice-preferences.json',dict(engine='Microsoft Edge TTS',voice=VOICE,rate=RATE,language='en',reference='/Users/impulsiveweb/Documents/Cartoon Movies/youtube-daily/series/learning-10/build.py',scope='Remaining project Shorts 47–51',authorizedBy='go ahead and schedule all shorts. use new voice over which was used in cartoon videos'))
 state(active=True,status='preparing')
 return rows

def update(n,**values):
 q=load(SERIES/'queue.json')
 for r in q:
  if r['videoNumber']==n:r.update(values);r.pop('error',None)
 save(SERIES/'queue.json',q)
 with (SERIES/'posting-calendar.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=['videoNumber','topic','publishLocal','publishAt','status','url']);w.writeheader();w.writerows({k:r.get(k,'') for k in w.fieldnames} for r in q)

async def voice(n):
 d=dest(n);v=d/'voice';v.mkdir(parents=True,exist_ok=True);sem=asyncio.Semaphore(2)
 async def one(ident,line):
  wav=v/(ident+'.wav');stamp=v/(ident+'.sha256');key=hashlib.sha256(json.dumps([VOICE,RATE,line,edge_tts.__version__]).encode()).hexdigest()
  if wav.exists() and stamp.exists() and stamp.read_text()==key:return
  async with sem:
   for attempt in range(3):
    try:
     raw=v/(ident+'.mp3');await edge_tts.Communicate(line,VOICE,rate=RATE).save(str(raw))
     trim='silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.03'
     run(['ffmpeg','-y','-v','error','-i',raw,'-af',f'{trim},areverse,{trim},areverse','-ar','48000','-ac','1',wav]);stamp.write_text(key);raw.unlink();print('Voice',n,ident,round(duration(wav),2),flush=True);return
    except Exception:
     if attempt==2:raise
     await asyncio.sleep(2**attempt)
 await asyncio.gather(*(one(ident,line) for ident,line in zip(IDS,DATA[n]['lines'])))

def prepare(n,slot):
 d=dest(n);d.mkdir(exist_ok=True,parents=True);p=project(n)
 if (d/'youtube-upload-receipt.json').exists():raise RuntimeError('Existing receipt: reconcile before preparing')
 for name in ('lesson.json','narration.json','storyboard.md'):
  original=d/name;bak=BASE/'originals'/str(n)/name
  if original.exists() and not bak.exists():bak.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,bak)
 p.mkdir(exist_ok=True)
 for source in BASE.iterdir():
  if source.name not in ('src','tools','public','package.json','package-lock.json','vite.config.js','index.html','video.config.json'):continue
  if source.is_dir():shutil.copytree(source,p/source.name,dirs_exist_ok=True)
  else:shutil.copy2(source,p/source.name)
 if not (p/'node_modules').exists():(p/'node_modules').symlink_to((BASE/'node_modules').resolve(),target_is_directory=True)
 entry=next(v for v in load(SERIES/'catalog.json') if v['videoNumber']==n);entry.update({k:v for k,v in DATA[n].items() if k!='lines'})
 for path in (d/'lesson.json',p/'lesson.json'):save(path,entry)
 narration=dict(voice=VOICE,rate=RATE,pitch='+0Hz',leadIn=.25,scenes=dict(zip(IDS,DATA[n]['lines'])))
 for path in (d/'narration.json',p/'narration.json'):save(path,narration)
 asyncio.run(voice(n));ds=[math.ceil((duration(d/'voice'/(i+'.wav'))+.7)*2)/2 for i in IDS]
 if sum(ds)>60:raise RuntimeError(f'Lesson {n}: speech needs {sum(ds)} seconds; shorten narration')
 # Distribute only modest gaps, favoring the visible demonstration and code.
 for i in range(round((60-sum(ds))*2)):ds[[3,4,2,1,6,0,5,7][i%8]]+=.5
 timeline="import {"+','.join(COMP)+"} from './Lesson.jsx';\nexport const scenes = [\n"+'\n'.join(f"{{id:'{i}',duration:{t},transition:'fade',component:{c}}}," for i,t,c in zip(IDS,ds,COMP))+"\n];\n"
 (p/'src/scenes/index.js').write_text(timeline);save(d/'timeline.json',dict(zip(IDS,ds)))
 if (p/'voice').exists():shutil.rmtree(p/'voice')
 shutil.copytree(d/'voice',p/'voice');run(['node','tools/voiceover.mjs','--measure'],p);shutil.copy2(p/'voice/manifest.json',d/'voice/manifest.json')
 story=f'# {DATA[n]["title"]}\n\n9:16; 1080 × 1920; 30 fps; 60 seconds. Voice: {VOICE}, {RATE}.\nCreative direction: midnight, mint and orange; large readable code; result first; working counter/list handlers; simple before/after transitions. No stock imagery.\n\n'
 visuals=[entry['hook'],entry['idea'],entry['code'],entry['code2'],entry['tip'],entry['caution'],entry['exercise'],'Subscribe for practical beginner coding projects.']
 for i,t,line,visual in zip(IDS,ds,DATA[n]['lines'],visuals):story+=f'## {i} — {t}s\nNarration: {line}\nVisuals/text: {visual}\nMotion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.\n\n'
 (d/'storyboard.md').write_text(story);(p/'storyboard.md').write_text(story)
 if n==51:description='Publish a static website with GitHub Pages using the free public-repository option. Learn where to put index.html and how to choose a branch and source folder. The deployment flow and URL shown are illustrative.'
 else:description=DATA[n]['lines'][0]+' '+entry['idea']+' '+entry['rule']
 description+='\n\nTry it: '+entry['exercise']+'\n\n'+entry['caution']+'\n\nFind the complete Web Development for Beginners playlist on @Techat60. Subscribe for practical HTML, CSS and JavaScript projects.\n\nWeb Development in 60 Seconds • Lesson '+str(n)+'\n\n'+('Source: https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site\n\n' if n==51 else 'Reference: https://developer.mozilla.org/en-US/docs/Learn_web_development\n\n')+'#WebDevelopment #LearnToCode #Shorts'
 metadata=dict(title=DATA[n]['title'],description=description,tags=[DATA[n]['title'].lower(),'web development for beginners','beginner coding projects','Tech at 60'],video='video.mp4',publishAt=slot['publishAt'])
 save(d/'youtube-metadata.json',metadata);(d/'youtube-upload-details.txt').write_text(metadata['title']+'\n\n'+description)
 run(['npm','run','build'],p);run(['node','tools/record.mjs','--stills'],p)
 if (d/'stills').exists():shutil.rmtree(d/'stills')
 shutil.copytree(p/'out/stills',d/'stills')
 update(n,status='prepared');print('PREPARED',n,'speech',round(sum(duration(d/'voice'/(i+'.wav')) for i in IDS),2),flush=True)

def render(n):
 d=dest(n);p=project(n)
 if (d/'youtube-upload-receipt.json').exists():raise RuntimeError('Existing upload receipt; do not replace media')
 target=d/'video.partial.mp4';run(['node','tools/record.mjs','--out',target],p)
 info=probe(target);v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
 assert (v['width'],v['height'],v['r_frame_rate'],v['nb_frames'])==(1080,1920,'30/1','1800') and abs(float(info['format']['duration'])-60)<.1 and a['codec_name']=='aac'
 target.replace(d/'video.mp4');save(d/'verification.json',dict(verifiedAt=datetime.now(ZONE).isoformat(),voice=VOICE,rate=RATE,probe=info,narrationTiming='Measured clip lengths; every clip fits its scene. Not checked by ear.'))
 update(n,status='rendered');print('RENDERED',n,flush=True)

def upload(n):
 d=dest(n);review=d/'reviewed.json'
 assert review.exists() and load(review).get('approved'), 'Visual review required before upload'
 assert (d/'verification.json').exists()
 credentials=list(ROOT.glob('client_secret*.json'));assert len(credentials)==1
 metadata=load(d/'youtube-metadata.json');assert datetime.fromisoformat(metadata['publishAt'])>datetime.now(timezone.utc),'Past slot: reschedule; do not publish immediately'
 run([sys.executable,ROOT/'tools/youtube_upload.py','--credentials',credentials[0],'--metadata',d/'youtube-metadata.json','--noninteractive'])
 receipt=load(d/'youtube-upload-receipt.json');assert receipt['state']=='scheduled'
 update(n,status='scheduled',videoId=receipt['videoId'],url=receipt['url']);print('SCHEDULED',n,receipt['url'],flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prepare','render','upload']);ap.add_argument('--numbers',nargs='+',type=int,default=list(DATA));args=ap.parse_args()
 with (SERIES/'.production.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  slots=plan()
  for n in args.numbers:
   assert n in DATA
   if args.stage=='prepare':prepare(n,next(r for r in slots if r['videoNumber']==n))
   elif args.stage=='render':render(n)
   else:upload(n)
  state(active=True,status=args.stage+'-complete')
