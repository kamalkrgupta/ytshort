import os,plistlib,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
label='com.techat60.schedule-healthcheck'
body=dict(Label=label,ProgramArguments=[str(ROOT/'.youtube-venv/bin/python'),'-u',str(ROOT/'tools/schedule_healthcheck.py'),'--repair'],WorkingDirectory=str(ROOT),StartCalendarInterval=dict(Hour=8,Minute=0),StartInterval=3600,RunAtLoad=True,ProcessType='Background',StandardOutPath=str(ROOT/'schedule-health/activity.log'),StandardErrorPath=str(ROOT/'schedule-health/activity.log'),EnvironmentVariables=dict(PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin',TZ='Asia/Kolkata'))
source=ROOT/'tools'/(label+'.plist');source.write_bytes(plistlib.dumps(body));subprocess.run(['plutil','-lint',str(source)],check=True)
if '--install' in sys.argv:
 target=Path.home()/'Library/LaunchAgents'/source.name
 if target.exists() and target.read_bytes()!=source.read_bytes():raise RuntimeError('Different health-check job exists; inspect first')
 target.write_bytes(source.read_bytes());domain=f'gui/{os.getuid()}'
 if subprocess.run(['launchctl','print',domain+'/'+label],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:subprocess.run(['launchctl','bootstrap',domain,str(target)],check=True)
 subprocess.run(['launchctl','print',domain+'/'+label],check=True)
