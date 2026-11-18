import os,plistlib,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent;W=B.parent
label='com.techat60.ai-beginners'
LOGS=Path.home()/'Library/Logs/Techat60';LOGS.mkdir(parents=True,exist_ok=True)
body=dict(Label=label,ProgramArguments=[str(W/'.youtube-venv/bin/python'),'-u',str(B/'worker.py')],WorkingDirectory=str(W),StartInterval=3600,StartCalendarInterval=[dict(Hour=8,Minute=0),dict(Hour=14,Minute=0)],RunAtLoad=True,ProcessType='Background',StandardOutPath=str(LOGS/'ai-beginners.log'),StandardErrorPath=str(LOGS/'ai-beginners.log'),EnvironmentVariables=dict(PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin',TZ='Asia/Kolkata'))
source=B/(label+'.plist');source.write_bytes(plistlib.dumps(body))
subprocess.run(['plutil','-lint',str(source)],check=True)
if '--install' in sys.argv:
 target=Path.home()/'Library/LaunchAgents'/source.name
 if target.exists() and target.read_bytes()!=source.read_bytes():raise RuntimeError('Different existing job requires inspection')
 target.write_bytes(source.read_bytes());domain=f'gui/{os.getuid()}'
 if subprocess.run(['launchctl','print',domain+'/'+label],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:subprocess.run(['launchctl','bootstrap',domain,str(target)],check=True)
 subprocess.run(['launchctl','print',domain+'/'+label],check=True)
