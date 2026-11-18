import asyncio,json,os
from pathlib import Path
from voice import synthesize,finish
from render import render,setup
from worker import production_environment,run
B=Path(__file__).resolve().parent
os.environ.update(production_environment())
n=2;d=B/'episodes'/f'{n:02d}'
if not (d/'lesson.json').exists():
 ep=json.loads((d/'script.json').read_text());asyncio.run(synthesize([ep]));finish(ep)
if not (d/'contact.png').exists():
 project=setup(n);run(['node','tools/capture-longform.mjs','--stills'],cwd=project)
render(n)
