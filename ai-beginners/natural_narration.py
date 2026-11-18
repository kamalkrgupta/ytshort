"""Apply conversational copy and rebuild unpublished episodes with native pacing."""
import asyncio,fcntl,json,os,shutil
from pathlib import Path
from worker import production_environment,run
from voice import synthesize,finish
from render import setup,render
B=Path(__file__).resolve().parent
REPLACEMENTS={
 'You do not need':'You don’t need','you do not need':'you don’t need','It can':'It can',
 'It is your turn.':'Your turn.','What is useful?':'What’s useful?','What is missing?':'What’s missing?',
 'what is correct':'what’s correct','what is my goal':'what’s my goal','what information':'what information',
 'Here is our real-world situation:':'Here’s the example we’ll use:',
 'First, let us understand the key idea in plain English. In this lesson, the key idea is this:':'Let’s start with the main idea.',
 'Now let us put that idea into action.':'Let’s try it with an example.',
 'Here is your challenge:':'Here’s your challenge:',
 'If you enjoyed this tutorial, please like this video, share it with someone who wants to learn AI, and subscribe to Techat60 for more easy-to-follow AI tutorials.':'If this helped, share it with someone learning AI. And subscribe to Tech at sixty for the next lesson.',
 'Thanks for watching, and I will see you in the next lesson.':'Thanks for watching. See you in the next lesson.',
 'Today we are exploring ':'Today, we’re looking at ',
 'By the end of this lesson, you will understand':'By the end, you’ll understand',
 'We will use that situation':'We’ll use that situation',
 'We are building practical AI skills':'We’re building practical AI skills',
 'does not automatically':'doesn’t automatically','we are not judging':'we’re not judging','We are checking':'We’re checking',
 'you are writing':'you’re writing','if you want':'if you’d like','All you need is curiosity and a willingness to experiment.':'Bring your curiosity. We’ll work through it together.',
 'Techat60':'Tech at sixty',
}

def revise():
 for p in sorted((B/'episodes').glob('*/script.json')):
  ep=json.loads(p.read_text())
  for c in ep['chapters']:
   text=c['text']
   for a,b in REPLACEMENTS.items():text=text.replace(a,b)
   text=text.replace('?.','?').replace('!.','!')
   # Paragraph boundaries cue complete thoughts, rather than a single dense block.
   text=text.replace(' Think of AI','\n\nThink of AI').replace(' Ask yourself','\n\nAsk yourself').replace(' Start by','\n\nStart by').replace(' Pause the video','\n\nPause the video')
   c['text']=text
  p.write_text(json.dumps(ep,indent=2,ensure_ascii=False)+'\n')

if __name__=='__main__':
 os.environ.update(production_environment())
 with (B/'.worker.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  revise()
  for n in (1,2):
   d=B/'episodes'/f'{n:02d}'
   if (d/'youtube-upload-receipt.json').exists():raise RuntimeError('Inspect upload receipt before revising media')
   backup=d/'previous-narration';backup.mkdir(exist_ok=True)
   for name in ['voice','narration.json','lesson.json','captions.json','subtitles.srt','video.mp4','verification.json','reviewed.json','contact.png','stills','frames']:
    p=d/name
    if p.exists():shutil.move(str(p),str(backup/name))
   ep=json.loads((d/'script.json').read_text());asyncio.run(synthesize([ep]));finish(ep)
   meta=d/'youtube-metadata.json';m=json.loads(meta.read_text());m['description']=m['description'].split('\n\nCHAPTERS\n')[0]+'\n\nCHAPTERS\n'+'\n'.join(f'{int(c["start"])//60:02d}:{int(c["start"])%60:02d} {c["title"]}' for c in ep['chapters']);meta.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
   project=setup(n);run(['node','tools/capture-longform.mjs','--stills'],cwd=project);render(n)
  print('Both episodes rebuilt with conversational narration and native speech timing.',flush=True)
