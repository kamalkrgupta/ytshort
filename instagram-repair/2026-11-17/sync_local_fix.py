from pathlib import Path
import json,os,shutil,tempfile
base=Path(__file__).resolve().parent;source=base/'source';local=Path('/Users/impulsiveweb/Techat60-Instagram')
files=['cloud_runner.py','cloud_watchdog.py','scheduled_reel.py','tests/test_scheduled_reel.py','tests/test_watchdog.py','.github/workflows/instagram-daily.yml']
for name in files+['README.md']:
 target=local/('README-CLOUD.md' if name=='README.md' else name);backup=base/'before-local'/target.relative_to(local);backup.parent.mkdir(parents=True,exist_ok=True)
 if target.exists() and not backup.exists():shutil.copy2(target,backup)
 target.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=target.parent,prefix='.'+target.name)
 try:
  os.fchmod(fd,0o600 if target.exists() and target.stat().st_mode&0o077==0 else 0o644)
  with os.fdopen(fd,'wb') as f:f.write((source/name).read_bytes());f.flush();os.fsync(f.fileno())
  os.replace(tmp,target)
 finally:Path(tmp).unlink(missing_ok=True)
p=local/'.github-deployment.json';state=json.loads(p.read_text());state.update(source_commit=(base/'deployed-commit.txt').read_text().strip(),read_only_test_run='https://github.com/kamalkrgupta/techat60-instagram-publisher/actions/runs/44067873273')
fd,tmp=tempfile.mkstemp(dir=p.parent,prefix='.deployment-')
try:
 os.fchmod(fd,0o600)
 with os.fdopen(fd,'w') as f:json.dump(state,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
finally:Path(tmp).unlink(missing_ok=True)
print('Local deployment sources and backup dispatcher synchronized; originals retained in workspace.')
