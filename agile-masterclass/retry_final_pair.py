#!/usr/bin/env python3
"""Bounded retry for episodes 11–12 after YouTube's 24-hour upload limit."""
import fcntl,json,os,subprocess,sys
from datetime import datetime,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

ROOT=Path(__file__).resolve().parent
ZONE=ZoneInfo('Asia/Kolkata')
NOT_BEFORE=datetime(2026,10,24,22,15,tzinfo=ZONE)
DEADLINE=datetime(2026,10,28,17,30,tzinfo=ZONE)
LABEL='com.techat60.agile-final-episodes'
PLIST=Path.home()/'Library/LaunchAgents'/f'{LABEL}.plist'
STATE=ROOT/'retry-state.json'

def write(value):
    tmp=STATE.with_suffix('.json.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(STATE)

def receipts():
    values=[]
    for n in (11,12):
        p=ROOT/'episodes'/f'{n:02d}'/'youtube-upload-receipt.json'
        values.append(json.loads(p.read_text()) if p.exists() else {})
    return values

def main():
    now=datetime.now(ZONE)
    state=json.loads(STATE.read_text()) if STATE.exists() else dict(status='scheduled',attempts=0,notBefore=NOT_BEFORE.isoformat(),deadline=DEADLINE.isoformat(),episodes=[11,12],intendedPublishAt='2026-10-28T18:00:00+05:30')
    if '--check' in sys.argv:
        print(json.dumps(dict(now=now.isoformat(),**state),indent=2));return
    if state.get('status') in ('completed','needs_attention','expired'):return
    if now<NOT_BEFORE:write(state);print('Retry is scheduled; no network or upload attempted before '+NOT_BEFORE.isoformat(),flush=True);return
    if now>=DEADLINE:
        state.update(status='expired',error='Release deadline reached; no late or immediate publication attempted');write(state);return
    if state.get('nextAttemptAt') and now<datetime.fromisoformat(state['nextAttemptAt']):return
    if state.get('attempts',0)>=4:
        state.update(status='needs_attention',error='Four bounded attempts used');write(state);return
    try:
        # Never launch an interactive sign-in from a background job.
        creds=Credentials.from_authorized_user_file(str(ROOT.parent/'.youtube-auth/token.json'))
        if creds.expired:creds.refresh(Request())
        if not creds.valid:raise RuntimeError('Existing authorization is not valid')
        for n,r in zip((11,12),receipts()):
            if not r or r.get('videoId'):continue
            if r.get('state')!='rejected' or r.get('errorReason')!='uploadLimitExceeded' or not r.get('rejectedBeforeUpload'):
                raise RuntimeError('Uncertain prior upload requires reconciliation')
            # A documented server rejection created no video or resumable session.
            # Preserve its evidence before a new attempt after the waiting period.
            p=ROOT/'episodes'/f'{n:02d}'/'youtube-upload-receipt.json'
            p.replace(p.with_name(f'youtube-rejected-{now.strftime("%Y%m%d-%H%M%S")}.json'))
        state.update(status='running',attempts=state.get('attempts',0)+1,lastAttemptAt=now.isoformat());write(state)
        result=subprocess.run([sys.executable,str(ROOT/'publish.py'),'--start','11','--end','12'],cwd=ROOT.parent)
        if result.returncode:
            undone=[r for r in receipts() if not (r.get('videoId') and r.get('state')=='scheduled')]
            if undone and all(r.get('state')=='rejected' and r.get('errorReason')=='uploadLimitExceeded' and r.get('rejectedBeforeUpload') for r in undone):
                state.update(status='waiting_for_upload_limit_reset',nextAttemptAt=(now+timedelta(hours=24)).isoformat());write(state);return
            raise RuntimeError('Upload needs attention; preserved receipts prevent duplication')
        subprocess.run([sys.executable,str(ROOT/'audit.py')],cwd=ROOT.parent,check=True)
        state.update(status='completed',completedAt=datetime.now(ZONE).isoformat());write(state)
        print('Final pair uploaded, remotely scheduled and fully audited; removing retry job.',flush=True)
        PLIST.unlink(missing_ok=True)
        subprocess.run(['/bin/launchctl','bootout',f'gui/{os.getuid()}/{LABEL}'],check=False)
    except Exception as error:
        # Do not print request objects, credentials or resumable-session URLs.
        state.update(status='needs_attention',error=type(error).__name__+': retry stopped; inspect publishing receipts and retry.log');write(state)
        print(state['error'],flush=True)

if __name__=='__main__':
    with (ROOT/'.retry.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);main()
