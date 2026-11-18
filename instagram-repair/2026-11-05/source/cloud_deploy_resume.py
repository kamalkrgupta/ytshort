"""Finish the approved cloud deployment after GitHub device login succeeds."""
import json,os,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
from config import ROOT,secure_json
from github_deploy import GH,auth,deployment,command,GitHub
STATUS=ROOT/'logs/cloud-deployment.json';LOG=ROOT/'logs/cloud-deployment.log'
def status(phase,**details):secure_json(STATUS,dict(phase=phase,updated_at=datetime.now(timezone.utc).isoformat(),**details))
def logged(args):
 with LOG.open('a') as out:r=subprocess.run(list(map(str,args)),cwd=ROOT,stdout=out,stderr=out)
 if r.returncode:raise RuntimeError('Deployment step failed; see local cloud-deployment.log (no credentials printed).')
def wait_check(repo,started):
 api=GitHub(repo,auth());head=api.request('GET',api.path('/git/ref/heads/main'))['object']['sha']
 for _ in range(180):
  runs=api.request('GET',api.path('/actions/workflows/instagram-daily.yml/runs?event=workflow_dispatch&per_page=15')).get('workflow_runs',[])
  candidates=[r for r in runs if r.get('head_sha')==head and r.get('created_at','')>=started]
  if candidates:
   run=max(candidates,key=lambda r:r['id']);status('validating_cloud',repository=repo,run_url=run['html_url'],run_status=run['status'])
   if run['status']=='completed':
    if run.get('conclusion')!='success':raise RuntimeError('Cloud validation failed. Inspect the workflow run before changing local publishing.')
    return run['html_url']
  time.sleep(10)
 raise RuntimeError('Cloud validation timed out; existing local publisher was not changed.')
def check_run(repo):
 started=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
 for attempt in range(6):
  result=command([GH,'workflow','run','instagram-daily.yml','--repo',repo,'--ref','main','-f','mode=check'],check=False)
  if result.returncode==0:break
  if attempt==5:raise RuntimeError('GitHub has not accepted the read-only workflow run.')
  time.sleep(10)
 return wait_check(repo,started)
def main():
 status('awaiting_github_authorization')
 for _ in range(180):
  if command([GH,'auth','status'],check=False).returncode==0:break
  time.sleep(5)
 else:status('blocked',reason='GitHub device authorization not completed.');return 1
 status('deploying')
 logged([sys.executable,ROOT/'github_deploy.py','prepare']);info=deployment();repo=info['repository'];status('cloud_check_requested',repository=repo)
 first=check_run(repo);status('handoff',repository=repo,verified_check=first)
 # No retry of uncertain activation: local must never race an uncertain cloud enable.
 logged([sys.executable,ROOT/'github_deploy.py','activate'])
 second=check_run(repo);status('active',repository=repo,url='https://github.com/'+repo,verified_check=second,caption_mode='free fallback',daily_time='19:00 Asia/Kolkata',timing='Early preparation and retries; GitHub scheduling can still delay runs.')
 return 0
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as e:status('needs_attention',reason=str(e) if isinstance(e,RuntimeError) else type(e).__name__);raise SystemExit(1)
