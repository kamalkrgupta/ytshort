#!/usr/bin/env python3
"""Prepare an isolated, resumable long-form series; never changes the Shorts queue."""
import asyncio, csv, hashlib, json, math, re, subprocess, sys
from pathlib import Path
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import edge_tts

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
VOICE = 'en-IN-NeerjaNeural'
RATE = '-12%'

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(path)

def probe(path):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)]))

def spoken(text):
    for old,new in [('CI/CD','continuous integration and delivery'),('ATDD','A T D D'),('TDD','T D D'),('BDD','B D D'),('APIs','A P I services'),('API','A P I'),('SQL','S Q L'),('PDF','P D F'),('WIP','work in progress'),('SaaS','software as a service'),('UI','user interface'),('XP','X P'),('Q1','quadrant one'),('Q2','quadrant two'),('Q3','quadrant three'),('Q4','quadrant four')]:
        text = text.replace(old,new)
    return text.replace('Red–Green–Refactor','Red, Green, Refactor')

def parse():
    source = (ROOT/'source-manuscript.txt').read_text()
    extra = json.loads((ROOT/'lesson-expansions.json').read_text())
    dives = json.loads((ROOT/'deep-dives.json').read_text())
    visuals = json.loads((ROOT/'visuals.json').read_text())
    episodes = []
    for num,title,body in re.findall(r'Episode (\d+) \| ([^\n]+)\n(.*?)(?=\nEpisode \d+ \||\nProduction Standards|\Z)',source,re.S):
        original = re.findall(r'(\d\d:\d\d)[^\n]+\|\s+([^\n]+)\n([^\n]+)\nVISUAL / ON-SCREEN DIRECTION\s+([^\n]+)',body)
        chapters=[]; supplements=list(extra[num])
        for i,(_,heading,narration,direction) in enumerate(original[:-1]):
            if num == '1':
                add = supplements.pop(0) if i in (1,3,5,6) else ''
            else:
                add = supplements.pop(0) if supplements else ''
            chapters.append(dict(title=heading,text=spoken(narration+' '+add),direction=direction))
        for i,text in enumerate(supplements):
            chapters.append(dict(title='Worked example' if i%2==0 else 'Guided practice',text=spoken(text),direction=visuals[num]['example']))
        for i,text in enumerate(dives[num]):
            chapters.append(dict(title='A closer look' if i==0 else 'Verify the outcome',text=spoken(text),direction=visuals[num]['example']))
        _,heading,narration,direction=original[-1]
        ending = (' Subscribe to Tech at sixty for the next episode in this Agile Testing Masterclass. Practice the example with synthetic data, and share the most important risk you identified in the comments.' if num!='12' else ' Thank you for completing the Agile Testing Masterclass with Tech at sixty. Keep your examples and evidence, apply the approach to a small feature, and share your most useful takeaway in the comments. Subscribe for more practical software testing tutorials.')
        chapters.append(dict(title=heading,text=spoken(narration+ending),direction=direction))
        for i,c in enumerate(chapters): c['id']=f'chapter-{i+1:02d}'
        n=int(num)
        when=None if n<3 else datetime(2026,10,23,18,tzinfo=ZoneInfo('Asia/Kolkata'))+timedelta(days=(n-1)//2)
        release=when.isoformat() if when else None
        episodes.append(dict(episode=n,topic=title,visual=visuals[num],chapters=chapters,publishAt=release,plannedDate='2026-10-23' if when is None else when.date().isoformat(),status='planned',voice=VOICE,rate=RATE))
    return episodes

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
    count=len(durations); factor=sum(durations)/(600-count*.65)
    if not .65<factor<1.35:raise RuntimeError(f'Unnatural narration speed for E{ep["episode"]}: {factor}')
    print(f'E{ep["episode"]:02d}: {sum(len(c["text"].split()) for c in ep["chapters"])} words, raw {sum(durations):.1f}s, tempo {factor:.3f}',flush=True)
    start=0;subs=[];clips={}
    for i,(c,raw) in enumerate(zip(ep['chapters'],durations)):
        duration=round((raw/factor+.65)*30)/30
        if i==count-1:duration=600-start
        speech=duration-.65
        speed=raw/speech
        wav=voice/(c['id']+'.wav')
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(voice/(c['id']+'.mp3')),'-af',f'atempo={speed:.9f},apad,atrim=duration={speech:.9f}','-ar','48000','-ac','1',str(wav)],check=True)
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
    if abs(start-600)>.001:raise RuntimeError('Timeline mismatch')
    write(voice/'manifest.json',dict(leadIn=.25,clips=clips))
    write(dest/'narration.json',dict(voice=VOICE,rate=RATE,pitch='+0Hz',leadIn=.25,scenes={c['id']:c['text'] for c in ep['chapters']}))
    write(dest/'captions.json',subs)
    (dest/'subtitles.srt').write_text('\n\n'.join(f'{i+1}\n{srt_time(s["start"])} --> {srt_time(s["end"])}\n{s["text"]}' for i,s in enumerate(subs))+'\n')
    ep['duration']=600;ep['status']='prepared';write(dest/'lesson.json',ep)
    chapters='\n'.join(f'{int(c["start"])//60:02d}:{int(c["start"])%60:02d} {c["title"]}' for c in ep['chapters'])
    description=f'Learn {ep["topic"].lower()} with practical software testing examples, diagrams and a guided exercise.\nAgile Testing Masterclass — Episode {ep["episode"]} of 12 | English | 10-minute tutorial.\n\nIn this lesson:\n'+'\n'.join('• '+c['title'] for c in ep['chapters'][:8])+f'\n\nCHAPTERS\n{chapters}\n\nPractice: {ep["visual"]["question"]}\nExamples use fictional applications and synthetic data.\n\nSubscribe to @Techat60 for practical QA and software testing tutorials. Watch the series in episode order.\n\nReferences and further reading:\nhttps://agilemanifesto.org/\nhttps://scrumguides.org/scrum-guide.html\nhttps://kanbanguides.org/the-kanban-guide/2025.5/\nhttps://playwright.dev/docs/best-practices\n\n#AgileTesting #SoftwareTesting #QATutorial'
    tags=['agile testing',ep['topic'].lower(),'software testing tutorial','agile testing for beginners','QA tutorial','manual testing','software quality assurance','Techat60','agile testing masterclass']
    metadata=dict(title=ep['visual']['title'],description=description,tags=tags,video='video.mp4',thumbnail='thumbnail.jpg',publishAt=ep['publishAt'])
    assert len(metadata['title'])<=100 and len(description)<5000 and sum(len(x)+1 for x in tags)<450
    write(dest/'youtube-metadata.json',metadata)
    (dest/'youtube-upload-details.txt').write_text(metadata['title']+'\n\n'+description+'\n\nTags: '+', '.join(tags)+'\n')
    board=f'# Episode {ep["episode"]}: {ep["topic"]}\n\n16:9 | 1920 × 1080 | 30 fps | 600 seconds\nVoice: {VOICE}, English (India). Measured narration fitted uniformly to the timeline.\nDirection: navy, mint and lavender; Inter; risk-to-evidence diagrams; fictional examples.\n\n'
    for c in ep['chapters']:
        board+=f'## {c["id"]} — {c["title"]} ({c["start"]:.2f}s, {c["duration"]:.2f}s)\nNarration: {c["text"]}\nVisual direction: {c["direction"]}\nOn-screen example: {ep["visual"]["example"]}; steps: '+ ' | '.join(ep['visual']['steps'])+'; checks: '+' | '.join(ep['visual']['checks'])+f'\nMotion: three progressive views; Framer Motion entrances; GSAP path reveals. Panels change at thirds of the measured chapter duration. Final view: {ep["visual"]["result"]}.\n\n'
    (dest/'storyboard.md').write_text(board)
    return ep

def main():
    episodes=parse();write(ROOT/'queue.json',episodes)
    if '--text-only' in sys.argv:return
    asyncio.run(synthesize(episodes))
    for ep in episodes:finish(ep)
    write(ROOT/'queue.json',episodes)
    with (ROOT/'posting-calendar.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=['episode','topic','plannedDate','publishAt','status']);writer.writeheader()
        writer.writerows({k:ep.get(k) for k in writer.fieldnames} for ep in episodes)
    base=json.loads((WORKSPACE/'youtube-publishing.json').read_text())
    base.update(publishMode='per-video',descriptionSuffix='Subscribe to @Techat60 for practical software testing tutorials.',queueFile='agile-masterclass/queue.json',dailySchedule=dict(times=['18:00'],timezone='Asia/Kolkata',videosPerDay=2,startDate='2026-10-24'),scheduleStatus='prepared')
    write(ROOT/'youtube-publishing.json',base)
    print('Prepared all twelve episodes, metadata, storyboards and aligned subtitles.',flush=True)

if __name__=='__main__': main()
