"""Install only the final-pair retry task, retaining its reviewable plist here."""
import os,plistlib,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
label='com.techat60.agile-final-episodes'
body=dict(Label=label,ProgramArguments=[str(root.parent/'.youtube-venv/bin/python'),str(root/'retry_final_pair.py')],WorkingDirectory=str(root.parent),StartCalendarInterval=dict(Hour=22,Minute=15),StartInterval=3600,RunAtLoad=True,ProcessType='Background',StandardOutPath=str(root/'retry.log'),StandardErrorPath=str(root/'retry.log'),EnvironmentVariables=dict(PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin',TZ='Asia/Kolkata'))
source=root/f'{label}.plist';source.write_bytes(plistlib.dumps(body))
subprocess.run(['/usr/bin/plutil','-lint',str(source)],check=True)
target=Path.home()/'Library/LaunchAgents'/source.name
if '--prepare-only' not in __import__('sys').argv:
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists() and target.read_bytes()!=source.read_bytes():raise RuntimeError('An existing task has different contents; not overwritten')
    target.write_bytes(source.read_bytes())
    domain=f'gui/{os.getuid()}'
    current=subprocess.run(['/bin/launchctl','print',domain+'/'+label],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    if current.returncode:subprocess.run(['/bin/launchctl','bootstrap',domain,str(target)],check=True)
    subprocess.run(['/bin/launchctl','print',domain+'/'+label],check=True)
