"""Re-render unpublished episodes after correcting the channel branding."""
import fcntl,json,os,shutil
from pathlib import Path
from worker import production_environment,run
from render import setup,render
B=Path(__file__).resolve().parent
os.environ.update(production_environment())
with (B/'.worker.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 for relative in ['src/scenes/Lesson.jsx','tools/thumbnail.mjs']:
  p=B/'renderer'/relative;p.write_text(p.read_text().replace('TECH IN','TECH AT'))
 for n in (1,2):
  d=B/'episodes'/f'{n:02d}'
  if (d/'youtube-upload-receipt.json').exists():raise RuntimeError('Inspect upload receipt before replacing rendered media')
  old=d/'previous-branding';old.mkdir(exist_ok=True)
  for name in ['video.mp4','verification.json','reviewed.json','contact.png','stills','frames']:
   p=d/name
   if p.exists():
    target=old/name
    if target.exists():raise RuntimeError('Previous branding backup already exists: '+str(target))
    shutil.move(str(p),str(target))
  project=setup(n)
  run(['node','tools/capture-longform.mjs','--stills'],cwd=project)
  render(n)
 print('Corrected and verified both videos: TECH AT 60',flush=True)
