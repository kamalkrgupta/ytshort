#!/usr/bin/env python3
"""Verify rendered assets, reuse the existing channel authorization, save evidence."""
import argparse,csv,json,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from render import verify

def write(path,value):
    tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n');tmp.replace(path)

def update(n,**changes):
    queue=json.loads((ROOT/'queue.json').read_text())
    for row in queue:
        if row['episode']==n:row.update(changes)
    write(ROOT/'queue.json',queue)
    fields=['episode','topic','plannedDate','publishAt','status','url','videoId']
    with (ROOT/'posting-calendar.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows({k:row.get(k) for k in fields} for row in queue)
    config=json.loads((ROOT/'youtube-publishing.json').read_text());config['scheduleStatus']='confirmed' if all(r['status'] in ('published','scheduled') for r in queue) else 'in_progress';write(ROOT/'youtube-publishing.json',config)

def publish(n):
    dest=ROOT/'episodes'/f'{n:02d}';verify(dest)
    if not (dest/'reviewed.json').exists():raise RuntimeError('Visual inspection has not been recorded')
    metadata=json.loads((dest/'youtube-metadata.json').read_text())
    if n>2 and datetime.fromisoformat(metadata['publishAt'])<=datetime.now(timezone.utc):raise RuntimeError('Release time has passed; do not publish unexpectedly')
    credentials=list(ROOT.parent.glob('client_secret*.json'))
    if len(credentials)!=1:raise RuntimeError('Expected one configured OAuth client')
    cmd=[sys.executable,ROOT.parent/'tools/youtube_upload.py','--credentials',credentials[0],'--config',ROOT/'youtube-publishing.json','--metadata',dest/'youtube-metadata.json']
    result=subprocess.run(list(map(str,cmd)),cwd=ROOT.parent)
    receiptpath=dest/'youtube-upload-receipt.json'
    if receiptpath.exists():
        receipt=json.loads(receiptpath.read_text());update(n,status=receipt['state'],url=receipt.get('url'),videoId=receipt.get('videoId'),thumbnailSet=receipt.get('thumbnailSet',False))
    if result.returncode:raise RuntimeError('Upload or verification needs attention; retained existing receipt')
    receipt=json.loads(receiptpath.read_text())
    expected='published' if n<3 else 'scheduled'
    if receipt['state']!=expected:raise RuntimeError('YouTube release status not yet confirmed')
    if not receipt.get('thumbnailSet') and receipt.get('thumbnailStatus')!='permission_denied':raise RuntimeError('Custom thumbnail not confirmed')
    print(f'CONFIRMED E{n:02d}: {receipt["state"]} {receipt["url"]}',flush=True)
    subprocess.run([sys.executable,str(ROOT/'playlist.py')],cwd=ROOT.parent,check=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=1);ap.add_argument('--end',type=int,default=12);ap.add_argument('--render',action='store_true');ap.add_argument('--wait-for-renders',action='store_true');args=ap.parse_args()
    for n in range(args.start,args.end+1):
        if args.wait_for_renders:
            deadline=time.monotonic()+5400;announced=False
            while not (ROOT/'episodes'/f'{n:02d}'/'verification.json').exists():
                if not announced:print(f'Waiting for verified render E{n:02d}',flush=True);announced=True
                log=ROOT/f'render-{n:02d}.log'
                resumed=ROOT/f'render-{n:02d}-resumed.log'
                if resumed.exists():log=resumed
                if log.exists() and 'Traceback (most recent call last)' in log.read_text():raise RuntimeError(f'Render E{n:02d} failed; upload not attempted')
                if time.monotonic()>deadline:raise RuntimeError('Render wait limit reached')
                time.sleep(5)
        if args.render:
            update(n,status='rendering')
            subprocess.run([sys.executable,str(ROOT/'render.py'),'--start',str(n),'--end',str(n)],check=True)
            update(n,status='rendered')
        publish(n)

if __name__=='__main__':main()
