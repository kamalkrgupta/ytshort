import os,plistlib,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
label='com.techat60.daily-publishing'
body=dict(Label=label,ProgramArguments=[str(ROOT/'.youtube-venv/bin/python'),'-u',str(ROOT/'tools/daily_schedule.py')],WorkingDirectory=str(ROOT),StartInterval=3600,StartCalendarInterval=[dict(Hour=22,Minute=15),dict(Hour=8,Minute=0),dict(Hour=14,Minute=0),dict(Hour=17,Minute=0)],RunAtLoad=True,ProcessType='Background',StandardOutPath=str(ROOT/'series/daily-publishing.log'),StandardErrorPath=str(ROOT/'series/daily-publishing.log'),EnvironmentVariables=dict(PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin',TZ='Asia/Kolkata'))
source=ROOT/'tools'/f'{label}.plist';source.write_bytes(plistlib.dumps(body))
subprocess.run(['plutil','-lint',str(source)],check=True)
if '--install' in sys.argv:
 target=Path.home()/'Library/LaunchAgents'/source.name
 if target.exists() and target.read_bytes()!=source.read_bytes():raise RuntimeError('Existing different job; inspect first')
 target.write_bytes(source.read_bytes())
 domain=f'gui/{os.getuid()}'
 if subprocess.run(['launchctl','print',domain+'/'+label],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:subprocess.run(['launchctl','bootstrap',domain,str(target)],check=True)
 subprocess.run(['launchctl','print',domain+'/'+label],check=True)
