import fcntl,os,sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
print('Waiting for the current production batch to finish.',flush=True)
with (root/'series/.production.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 fcntl.flock(lock,fcntl.LOCK_UN)
print('Starting the remaining 48 topics.',flush=True)
os.chdir(root)
python=str(root/'.youtube-venv/bin/python')
os.execv(python,[python,'-u',str(root/'series/produce.py'),'--start','4','--upload'])
