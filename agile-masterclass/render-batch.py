import argparse,concurrent.futures,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
def render(n):
    with (root/f'render-{n:02d}.log').open('w') as log:
        result=subprocess.run([sys.executable,str(root/'render.py'),'--start',str(n),'--end',str(n),'--isolated'],stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:raise RuntimeError(f'Episode {n} render failed; inspect render-{n:02d}.log')
    print(f'RENDERED E{n:02d}',flush=True)
ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=2);ap.add_argument('--end',type=int,default=12);args=ap.parse_args()
failures=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    futures={pool.submit(render,n):n for n in range(args.start,args.end+1)}
    for future in concurrent.futures.as_completed(futures):
        try:future.result()
        except Exception as error:failures.append(str(error));print(str(error),flush=True)
if failures:raise RuntimeError('; '.join(failures))
