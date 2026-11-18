"""Upload only reviewed, verified final artifacts; keep receipts on any failure."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
B=Path(__file__).resolve().parent;W=B.parent
q=json.loads((B/'queue.json').read_text());credential=next(W.glob('client_secret*.json'))
for t in q:
 n=t['number'];d=B/'videos'/f'{n:02d}';deadline=time.monotonic()+900
 while not (d/'video.mp4').exists() or not (d/'verification.json').exists():
  log=d/'render.log'
  if log.exists() and any(s in log.read_text() for s in ('ERROR:','Traceback (most recent call last)')):raise RuntimeError(f'Render failure for {n}; unfinished video not uploaded')
  if time.monotonic()>deadline:raise RuntimeError(f'Render deadline for {n}; no upload attempted')
  time.sleep(5)
 verification=json.loads((d/'verification.json').read_text());assert hashlib.sha256((d/'video.mp4').read_bytes()).hexdigest()==verification['sha256']
 assert json.loads((d/'reviewed.json').read_text())['approved']
 with (d/'upload.log').open('w') as log:
  subprocess.run([sys.executable,str(W/'tools/youtube_upload.py'),'--credentials',str(credential),'--metadata',str(d/'youtube-metadata.json'),'--config',str(B/'youtube-publishing.json'),'--noninteractive'],cwd=W,stdout=log,stderr=subprocess.STDOUT,check=True)
 r=json.loads((d/'youtube-upload-receipt.json').read_text());assert r['state']=='scheduled';print('SCHEDULED',n,t['slug'],r['url'],r['verifiedPublishAt'],flush=True)
