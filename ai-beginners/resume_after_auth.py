"""Resume the authorized publishing worker after the current Google sign-in."""
import subprocess,time
from pathlib import Path
from worker import production_environment
B=Path(__file__).resolve().parent;W=B.parent
token=W/'.youtube-auth/token.json';previous=token.stat().st_mtime_ns
for _ in range(120):
 if token.stat().st_mtime_ns!=previous:
  print('Authorization renewed; resuming AI uploads.',flush=True)
  raise SystemExit(subprocess.run([str(W/'.youtube-venv/bin/python'),'-u',str(B/'worker.py')],cwd=W,env=production_environment()).returncode)
 time.sleep(5)
print('Sign-in not completed; installed hourly worker will retry after authorization.',flush=True)
