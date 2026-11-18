"""Upload each reviewed, verified artifact once; preserve uncertain receipts."""
import json,subprocess,sys,time
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1];credential=next(ROOT.glob('client_secret*.json'))
for n in range(48,52):
 d=ROOT/'series/videos'/str(n);deadline=time.monotonic()+600
 while not (d/'video.mp4').exists() or not (d/'verification.json').exists():
  if 'Traceback (most recent call last)' in (BASE/'render.log').read_text():raise RuntimeError('Render failed; no upload of unfinished media')
  if time.monotonic()>deadline:raise RuntimeError('Render wait deadline reached')
  time.sleep(5)
 assert json.loads((d/'reviewed.json').read_text()).get('approved')
 with (BASE/f'upload-{n}.log').open('w') as log:
  subprocess.run([sys.executable,str(ROOT/'tools/youtube_upload.py'),'--credentials',str(credential),'--metadata',str(d/'youtube-metadata.json'),'--noninteractive'],stdout=log,stderr=subprocess.STDOUT,check=True)
 r=json.loads((d/'youtube-upload-receipt.json').read_text());assert r['state']=='scheduled';print('SCHEDULED',n,r['url'],r['verifiedPublishAt'],flush=True)
