import edge_tts
import asyncio,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
VOICE='en-IN-NeerjaNeural'
RATE='-3%'
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def probe(p):
 return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)]))
async def synthesize(episodes):
    sem=asyncio.Semaphore(3)
    async def one(ep,c):
        dest=ROOT/'episodes'/f'{ep["episode"]:02d}'/'voice'
        dest.mkdir(parents=True,exist_ok=True)
        audio=dest/(c['id']+'.mp3'); boundary=dest/(c['id']+'.words.json'); stamp=dest/(c['id']+'.sha256')
        digest=hashlib.sha256((VOICE+RATE+c['text']).encode()).hexdigest()
        if audio.exists() and boundary.exists() and stamp.exists() and stamp.read_text()==digest:return
        async with sem:
            for attempt in range(3):
                try:
                    events=[]; tmp=audio.with_suffix('.partial')
                    with tmp.open('wb') as f:
                        async for chunk in edge_tts.Communicate(c['text'],VOICE,rate=RATE,boundary='WordBoundary').stream():
                            if chunk['type']=='audio':f.write(chunk['data'])
                            elif chunk['type']=='WordBoundary':events.append({k:chunk[k] for k in ('offset','duration','text')})
                    if not events or not tmp.stat().st_size:raise RuntimeError('Narration or alignment missing')
                    tmp.replace(audio);write(boundary,events);stamp.write_text(digest)
                    print(f'Voice E{ep["episode"]:02d} {c["id"]}',flush=True)
                    return
                except Exception as error:
                    if attempt==2:raise RuntimeError(f'Narration failed E{ep["episode"]} {c["id"]}: {type(error).__name__}')
                    await asyncio.sleep(2*(attempt+1))
    await asyncio.gather(*(one(ep,c) for ep in episodes for c in ep['chapters']))

def srt_time(t):
    ms=round(t*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'

def finish(ep):
    dest=ROOT/'episodes'/f'{ep["episode"]:02d}'; voice=dest/'voice'
    durations=[probe(voice/(c['id']+'.mp3')) for c in ep['chapters']]
    count=len(durations); factor=max(1.0,sum(durations)/(300-count*.65))
    padding=(300-count*.65-sum(durations)/factor)/count
    if not 1.0<=factor<=1.08:raise RuntimeError(f'Unnatural narration speed for E{ep["episode"]}: {factor}')
    print(f'E{ep["episode"]:02d}: {sum(len(c["text"].split()) for c in ep["chapters"])} words, raw {sum(durations):.1f}s, tempo {factor:.3f}',flush=True)
    start=0;subs=[];clips={}
    for i,(c,raw) in enumerate(zip(ep['chapters'],durations)):
        duration=round((raw/factor+.65+padding)*30)/30
        if i==count-1:duration=300-start
        speech=raw/factor
        speed=factor
        wav=voice/(c['id']+'.wav')
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(voice/(c['id']+'.mp3')),'-af',f'atempo={speed:.9f},apad,atrim=duration={duration-.65:.9f}','-ar','48000','-ac','1',str(wav)],check=True)
        c.update(start=round(start,6),duration=round(duration,6),speechDuration=round(speech,6),speed=speed)
        events=json.loads((voice/(c['id']+'.words.json')).read_text())
        for j in range(0,len(events),9):
            group=events[j:j+9]
            a=start+.25+group[0]['offset']/1e7/speed
            b=start+.25+(group[-1]['offset']+group[-1]['duration'])/1e7/speed
            b=min(b,start+duration-.2)
            if a<b:subs.append(dict(start=a,end=b,text=' '.join(e['text'] for e in group)))
        clips[c['id']]=dict(file=wav.name,duration=probe(wav),source='measured-edge-tts')
        start+=duration
    if abs(start-300)>.001:raise RuntimeError('Timeline mismatch')
    write(voice/'manifest.json',dict(leadIn=.25,clips=clips))
    write(dest/'narration.json',dict(voice=VOICE,rate=RATE,pitch='+0Hz',leadIn=.25,scenes={c['id']:c['text'] for c in ep['chapters']}))
    write(dest/'captions.json',subs)
    (dest/'subtitles.srt').write_text('\n\n'.join(f'{i+1}\n{srt_time(s["start"])} --> {srt_time(s["end"])}\n{s["text"]}' for i,s in enumerate(subs))+'\n')
    ep['duration']=300;ep['status']='prepared';write(dest/'lesson.json',ep)
    return ep
