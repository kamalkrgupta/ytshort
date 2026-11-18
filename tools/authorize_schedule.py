from pathlib import Path
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
sys.path.insert(0,str(Path(__file__).resolve().parent))
from youtube_upload import save,ROOT
scopes=['https://www.googleapis.com/auth/youtube.upload','https://www.googleapis.com/auth/youtube.readonly','https://www.googleapis.com/auth/youtube.force-ssl']
flow=InstalledAppFlow.from_client_secrets_file(str(next(ROOT.glob('client_secret*.json'))),scopes,autogenerate_code_verifier=True)
creds=flow.run_local_server(host='127.0.0.1',port=0,timeout_seconds=300,access_type='offline',prompt='consent',success_message='YouTube schedule authorization complete. You may close this tab.')
youtube=build('youtube','v3',credentials=creds,cache_discovery=False)
assert 'UC7F3e0NsVP37sqroVmYxiFw' in {v['id'] for v in youtube.channels().list(part='id',mine=True).execute()['items']},'Wrong channel; existing authorization preserved'
save(ROOT/'.youtube-auth/token.json',__import__('json').loads(creds.to_json()),True)
print('Channel schedule authorization saved.')
