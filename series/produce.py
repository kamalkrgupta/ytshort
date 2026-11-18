#!/usr/bin/env python3
import argparse,asyncio,csv,hashlib,json,math,os,re,shutil,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
import edge_tts
ROOT=Path(__file__).resolve().parent.parent
SERIES=ROOT/'series'; PROJECT=SERIES/'renderer'
IDS=['hook','idea','code','result','tip','caution','try','close']
COMPONENTS=['Hook','Idea','Code','Result','Tip','Caution','Try','Close']
SOURCES={'html':'https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content','css':'https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics','js':'https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting','pages':'https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site'}
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n');t.replace(p)
def run(args,cwd=PROJECT):
 p=subprocess.Popen(list(map(str,args)),cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
 output=[]
 for line in p.stdout:
  output.append(line);print(line,end='',flush=True)
 if p.wait(): raise RuntimeError('Command failed: '+str(args[0])+' (see production log)')
 return ''.join(output)
def timeline(ds):
 (PROJECT/'src/scenes/index.js').write_text("import {"+','.join(COMPONENTS)+"} from './Lesson.jsx';\nexport const scenes = [\n"+'\n'.join(f"{{id:'{id}',duration:{d},transition:'fade',component:{c}}}," for id,d,c in zip(IDS,ds,COMPONENTS))+"\n];\n")
def speak(s):
 for a,b in [('HTML','H T M L'),('CSS','C S S'),('DOM','D O M'),('IDs','identifiers'),('ID','identifier')]: s=s.replace(a,b)
 return s
async def tts(lines,dest):
 sem=asyncio.Semaphore(3)
 async def one(id,text):
  h=hashlib.sha256(('en-IN-NeerjaNeural|+8%|'+text).encode()).hexdigest()
  stamp=dest/(id+'.sha256');wav=dest/(id+'.wav')
  if wav.exists() and stamp.exists() and stamp.read_text()==h:return
  async with sem:
   for attempt in range(3):
    try:
     await edge_tts.Communicate(text,'en-IN-NeerjaNeural',rate='+8%').save(str(dest/(id+'.mp3')))
     raw=dest/(id+'.mp3')
     trim='silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.03'
     p=await asyncio.create_subprocess_exec('ffmpeg','-y','-loglevel','error','-i',str(raw),'-af',f'{trim},areverse,{trim},areverse','-ar','48000','-ac','1',str(wav))
     if await p.wait(): raise RuntimeError('Voice conversion failed')
     stamp.write_text(h);raw.unlink();return
    except Exception:
     if attempt==2: raise
     await asyncio.sleep(2*(attempt+1))
 await asyncio.gather(*(one(k,v) for k,v in lines.items()))
def prepare(entry,dest):
 lines=dict(zip(IDS,map(speak,[entry['topic']+'. Let’s make it simple.',entry['definition']+' Start by understanding the role it plays in a page.',entry['rule']+' Read the example from top to bottom.','Here’s an illustration of the result. Compare it with the example you just saw. Small changes in code can change the output.',entry['tip']+' Keep this detail in mind when writing your own example.',entry['caution']+' Understanding this helps you avoid a common beginner mistake.',entry['exercise']+' Change one part, then compare your result.','Like, share, and subscribe for more web development basics.'])))
 write(PROJECT/'lesson.json',entry);write(dest/'lesson.json',entry)
 narration=dict(voice='en-IN-NeerjaNeural',rate='+8%',pitch='+0Hz',leadIn=.35,scenes=lines)
 write(dest/'narration.json',narration);write(PROJECT/'narration.json',narration)
 ds=[5,8,8,9,8,9,8,5]
 def storyboard(ds):
  text='# '+entry['topic']+'\n\n9:16 | 1080 × 1920 | 60s | 30 fps\nDirection: beginner-friendly; midnight, orange and mint; bundled Inter font; code becomes output.\n\n'
  for i,(id,d) in enumerate(zip(IDS,ds)):
   visual=[entry['topic'],entry['definition'],entry['code'],entry['preview'],entry['tip'],entry['caution'],entry['exercise'],'Like, share & subscribe.'][i]
   text+=f'## {i+1}. {id} ({d}s)\nNarration: {lines[id]}\nText / visuals: {visual}\nMotion: 0.25s heading rises (Framer Motion); 0.5s rule draws (GSAP); 0.8s card enters; supporting details reveal at 3.5s and 5.3s. CSS grid pulses. Closing settles before last second.\n\n'
  text+='Source: '+SOURCES['html' if entry['videoNumber']<21 else 'css' if entry['videoNumber']<37 else 'pages' if entry['videoNumber']==51 else 'js']+'\n'
  (dest/'storyboard.md').write_text(text)
 storyboard(ds)
 voice=dest/'voice';voice.mkdir(exist_ok=True)
 asyncio.run(tts(lines,voice))
 lengths=[]
 for id in IDS:
  r=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(voice/(id+'.wav'))],capture_output=True,text=True,check=True)
  lengths.append(float(r.stdout))
 minima=[5,6.5,6,6,6,7,6,5]
 ds=[max(m,math.ceil((d+.75)*2)/2) for m,d in zip(minima,lengths)]
 if sum(ds)>60:
  lines['result']='Here’s an illustration of the result. Compare it with the example you just saw.'
  lines['caution']=speak(entry['caution'])
  lines['code']=speak(entry['rule'])
  narration['scenes']=lines
  write(dest/'narration.json',narration);write(PROJECT/'narration.json',narration)
  asyncio.run(tts(lines,voice))
  lengths=[float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(voice/(id+'.wav'))])) for id in IDS]
  ds=[max(m,math.ceil((d+.75)*2)/2) for m,d in zip(minima,lengths)]
 if sum(ds)>60: raise RuntimeError('Narration exceeds 60 seconds; shorten the script. No silent export.')
 priorities=[3,2,5,6,1,4,0]
 i=0
 while sum(ds)<60:
  ds[priorities[i%len(priorities)]]+=.5;i+=1
 timeline(ds);storyboard(ds)
 write(dest/'timeline.json',dict(zip(IDS,ds)))
 if (PROJECT/'voice').exists(): shutil.rmtree(PROJECT/'voice')
 shutil.copytree(voice,PROJECT/'voice')
 run(['node','tools/voiceover.mjs','--measure'])
 source=SOURCES['html' if entry['videoNumber']<21 else 'css' if entry['videoNumber']<37 else 'pages' if entry['videoNumber']==51 else 'js']
 title=entry['topic']+' | Web Development in 60 Seconds'
 description=(entry['definition']+' Learn '+entry['topic'].lower()+' with a quick example for beginners.\n\n'+entry['rule']+'\n'+entry['tip']+'\n\nTry it: '+entry['exercise']+'\n\nWhat would you build with this? Tell us in the comments.\nLike, share, and subscribe to @Techat60 for more web development basics.\n\nWeb Development in 60 Seconds • Lesson '+str(entry['videoNumber'])+'\nLearn more: '+source+'\n\n#WebDevelopment #LearnToCode #Shorts')
 metadata=dict(title=title[:100],description=description,tags=[entry['topic'].lower(),'web development for beginners','learn to code','coding shorts','html tutorial' if entry['videoNumber']<21 else 'css tutorial' if entry['videoNumber']<37 else 'javascript tutorial' if entry['videoNumber']<51 else 'github pages'],video='video.mp4',publishAt=entry['publishAt'])
 metadata['tags']=list(dict.fromkeys(metadata['tags']+json.loads((ROOT/'youtube-publishing.json').read_text()).get('additionalTags',[])))
 write(dest/'youtube-metadata.json',metadata)
 (dest/'youtube-upload-details.txt').write_text(title+'\n\n'+description+'\n\nTags: '+', '.join(metadata['tags']))
 run(['npm','run','build'])
 output=run(['node','tools/record.mjs','--stills'])
 if 'Page errors:' in output or 'WARNING:' in output:raise RuntimeError('Stills reported errors; inspect before publishing.')
 if (dest/'stills').exists():shutil.rmtree(dest/'stills')
 shutil.copytree(PROJECT/'out/stills',dest/'stills')
 shutil.copytree(PROJECT/'dist',dest/'dist',dirs_exist_ok=True)
 shutil.copy(PROJECT/'voice/manifest.json',voice/'manifest.json')
 return ds

def verify_video(path):
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
 v=next((s for s in info['streams'] if s['codec_type']=='video'),{})
 if not (v.get('width')==1080 and v.get('height')==1920 and v.get('nb_frames')=='1800' and v.get('r_frame_rate')=='30/1' and abs(float(info['format']['duration'])-60)<.1 and any(s['codec_type']=='audio' for s in info['streams'])):raise RuntimeError('MP4 verification failed; no upload attempted.')
 return info

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=50);ap.add_argument('--prepare-only',action='store_true');ap.add_argument('--upload',action='store_true');ap.add_argument('--start',type=int,default=2);ap.add_argument('--publish-overdue',action='store_true');ap.add_argument('--ahead-days',type=int);args=ap.parse_args()
 catalog=json.loads((SERIES/'catalog.json').read_text());queue=json.loads((SERIES/'queue.json').read_text())
 def update(n,**changes):
  for r in queue:
   if r['videoNumber']==n:
    r.update(changes)
    if changes.get('status') in ('scheduled','published'):r.pop('error',None)
  write(SERIES/'queue.json',queue)
  with (SERIES/'posting-calendar.csv').open('w') as f:
   writer=csv.DictWriter(f,fieldnames=['videoNumber','topic','publishLocal','publishAt','status','url']);writer.writeheader();writer.writerows({k:r.get(k,'') for k in writer.fieldnames} for r in queue)
  configured=json.loads((ROOT/'youtube-publishing.json').read_text())
  configured['scheduleStatus']='scheduled' if all(r['status'] in ('scheduled','published') for r in queue) else 'needs_attention' if any(r['status']=='needs_attention' for r in queue) else 'batch_in_progress'
  write(ROOT/'youtube-publishing.json',configured)
 for entry in [e for e in catalog if e['videoNumber']>=args.start][:args.limit]:
  if args.ahead_days is not None and (datetime.fromisoformat(entry['publishAt'].replace('Z','+00:00'))-datetime.now(timezone.utc)).total_seconds()>args.ahead_days*86400:continue
  n=entry['videoNumber'];dest=SERIES/'videos'/f'{n:02d}';dest.mkdir(parents=True,exist_ok=True)
  receipt=dest/'youtube-upload-receipt.json'
  if receipt.exists() and json.loads(receipt.read_text()).get('state') in ('scheduled','published'):
   saved=json.loads(receipt.read_text())
   update(n,**{k:v for k,v in saved.items() if k in ('url','videoId')},status=saved['state']);continue
  try:
   print('\n=== LESSON',n,entry['topic'],'===',flush=True)
   if (dest/'video.mp4').exists():
    try:verify_video(dest/'video.mp4')
    except (RuntimeError,subprocess.CalledProcessError,ValueError,KeyError):
     if receipt.exists():raise RuntimeError('Invalid media has an existing upload receipt; reconcile before replacing.')
     archived=dest/('video.incomplete-'+datetime.now().strftime('%Y%m%d%H%M%S')+'.mp4')
     (dest/'video.mp4').rename(archived)
     print('Preserved incomplete export:',archived.name,flush=True)
   if not (dest/'video.mp4').exists() or args.prepare_only:
    update(n,status='producing');prepare(entry,dest)
    update(n,status='prepared')
    if args.prepare_only:continue
    partial=dest/'video.partial.mp4'
    run(['node','tools/record.mjs','--out',str(partial)])
    verify_video(partial);partial.replace(dest/'video.mp4')
    update(n,status='rendered')
   if not args.prepare_only:verify_video(dest/'video.mp4')
   if args.upload:
    overdue=datetime.fromisoformat(entry['publishAt'].replace('Z','+00:00'))<=datetime.now(timezone.utc)
    if overdue and not args.publish_overdue:raise RuntimeError('Release slot is past; refusing immediate publication.')
    credentials=list(ROOT.glob('client_secret*.json'))
    if len(credentials)!=1:raise RuntimeError('Configure exactly one local OAuth credentials file.')
    run([sys.executable,ROOT/'tools/youtube_upload.py','--credentials',credentials[0],'--metadata',dest/'youtube-metadata.json','--noninteractive']+(['--publish-now'] if overdue else []),cwd=ROOT)
    result=json.loads(receipt.read_text());update(n,status=result['state'],url=result['url'],videoId=result['videoId'])
    if result['state'] not in ('scheduled','published'):raise RuntimeError('Upload schedule not confirmed. Production stopped for review.')
  except Exception as e:
   update(n,status='needs_attention',error=str(e));print('STOPPED:',str(e),flush=True);raise
 print('Selected production batch complete.',flush=True)
if __name__=='__main__':
 import fcntl
 with (SERIES/'.production.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  main()
