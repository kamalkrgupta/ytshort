#!/usr/bin/env python3
"""Authorize a Desktop OAuth client, verify the channel, upload one final MP4."""
import argparse, hashlib, json, os, sys, time, tempfile
from datetime import datetime, timezone
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.readonly']
ROOT = Path(__file__).resolve().parent.parent

def save(path, value, private=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.'+path.name+'-', suffix='.tmp', dir=path.parent)
    temp = Path(name)
    try:
        os.fchmod(fd, 0o600 if private else 0o644)
        with os.fdopen(fd, 'w') as f:
            json.dump(value, f, indent=2)
            f.flush(); os.fsync(f.fileno())
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--credentials', required=True)
    ap.add_argument('--metadata')
    ap.add_argument('--config', default=str(ROOT / 'youtube-publishing.json'))
    ap.add_argument('--authorize-only', action='store_true')
    ap.add_argument('--noninteractive', action='store_true')
    ap.add_argument('--publish-now', action='store_true', help='Explicitly publish a missed slot immediately')
    args = ap.parse_args()
    config_path = Path(args.config).resolve()
    config = json.loads(config_path.read_text())
    if not config.get('enabled') or config.get('privacyStatus') not in ('public','private','unlisted') or type(config.get('madeForKids')) is not bool:
        raise RuntimeError('Publishing preferences are incomplete.')
    token = ROOT / '.youtube-auth/token.json'
    creds = Credentials.from_authorized_user_file(str(token)) if token.exists() else None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if args.noninteractive: raise RuntimeError('Google authorization required; background upload stopped.')
        flow = InstalledAppFlow.from_client_secrets_file(args.credentials, SCOPES, autogenerate_code_verifier=True)
        print('Opening Google sign-in. Choose the account/channel for @Techat60.', flush=True)
        creds = flow.run_local_server(host='127.0.0.1', port=0, timeout_seconds=300, access_type='offline', prompt='consent', authorization_prompt_message='Complete Google authorization in the browser: {url}', success_message='Authorization complete. You can close this tab.')
    save(token, json.loads(creds.to_json()), True)
    youtube = build('youtube','v3',credentials=creds,cache_discovery=False)
    handle = config['channelUrl'].rstrip('/').split('/')[-1]
    expected = youtube.channels().list(part='id,snippet',forHandle=handle).execute().get('items',[])
    mine = youtube.channels().list(part='id,snippet',mine=True).execute().get('items',[])
    if len(expected) != 1 or expected[0]['id'] not in {c['id'] for c in mine}:
        raise RuntimeError('Authenticated channel does not match the configured handle. No upload attempted. Reauthorize with the correct YouTube channel.')
    channel_id = expected[0]['id']
    if config.get('channelId') and config['channelId'] != channel_id:
        raise RuntimeError('Saved channel ID mismatch; no upload attempted.')
    config.update(channelId=channel_id, connection='youtube-data-api-oauth')
    save(config_path,config)
    print('Verified channel:', expected[0]['snippet']['title'], channel_id, flush=True)
    if args.authorize_only: return
    if not args.metadata: raise RuntimeError('--metadata is required for upload.')
    metadata_path = Path(args.metadata).resolve()
    metadata = json.loads(metadata_path.read_text())
    metadata['tags'] = list(dict.fromkeys(metadata.get('tags', []) + config.get('additionalTags', [])))
    if config.get('playlistId'):
        playlist_url='https://www.youtube.com/playlist?list='+config['playlistId']
        if playlist_url not in metadata['description']:
            metadata['description']+='\n\nWatch the course in order: '+playlist_url
    if len(metadata['description'])>5000:raise RuntimeError('Video description exceeds YouTube limit.')
    publish_at = None if args.publish_now else metadata.get('publishAt')
    if config.get('publishMode') == 'scheduled' and not publish_at and not args.publish_now:
        raise RuntimeError('Scheduled mode requires a publishAt timestamp in the video metadata.')
    if publish_at:
        when = datetime.fromisoformat(publish_at.replace('Z', '+00:00'))
        if when.tzinfo is None or when <= datetime.now(timezone.utc):
            raise RuntimeError('publishAt must be a future timezone-aware timestamp; no upload attempted.')
    video = (metadata_path.parent / metadata['video']).resolve()
    digest = hashlib.file_digest(video.open('rb'),'sha256').hexdigest()
    receipt_path = metadata_path.parent / 'youtube-upload-receipt.json'
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    if receipt:
        if receipt.get('sha256') != digest or receipt.get('channelId') != channel_id:
            raise RuntimeError('An upload receipt exists for another file/channel; resolve revision publishing first.')
        if not receipt.get('videoId'):
            raise RuntimeError('A previous upload has an uncertain result. Reconcile it before retrying; no duplicate upload attempted.')
        video_id = receipt['videoId']
        print('Existing upload:',receipt['url'],flush=True)
    else:
        title = metadata['title']
        if not title or len(title)>100: raise RuntimeError('Invalid video title.')
        body = {'snippet':{'title':title,'description':metadata['description'],'tags':metadata.get('tags',[]),'categoryId':'27','defaultLanguage':config.get('defaultLanguage','en')},'status':{'privacyStatus':config['privacyStatus'],'selfDeclaredMadeForKids':config['madeForKids']}}
        if publish_at:
            body['status'].update(privacyStatus='private',publishAt=publish_at)
        receipt={'state':'uploading','channelId':channel_id,'sha256':digest,'title':title,'requestedVisibility':config['privacyStatus'],'startedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
        receipt['publishAt'] = publish_at
        save(receipt_path,receipt)
        request=youtube.videos().insert(part='snippet,status',body=body,media_body=MediaFileUpload(str(video),mimetype='video/mp4',chunksize=1024*1024,resumable=True))
        response=None
        while response is None:
            try:
                progress,response=request.next_chunk(num_retries=3)
            except Exception as upload_error:
                detail=json.loads(upload_error.content).get('error',{}) if hasattr(upload_error,'content') else {}
                reasons=[item.get('reason') for item in detail.get('errors',[])]
                if reasons==['uploadLimitExceeded'] and not request.resumable_uri:
                    receipt.update(state='rejected',errorReason='uploadLimitExceeded',rejectedBeforeUpload=True)
                    save(receipt_path,receipt)
                raise
            if request.resumable_uri:
                save(ROOT/'.youtube-auth/upload-session.json',{'uri':request.resumable_uri,'sha256':digest,'channelId':channel_id},True)
            if progress: print(f'Upload {progress.progress():.0%}',flush=True)
        video_id=response['id']
        receipt.update(videoId=video_id,url='https://www.youtube.com/watch?v='+video_id,state='uploaded',actualVisibility=response['status']['privacyStatus'])
        save(receipt_path,receipt)
        print('Uploaded:',receipt['url'],flush=True)
    if metadata.get('thumbnail') and config.get('customThumbnailsSupported') is False:
        receipt.update(thumbnailSet=False,thumbnailStatus='permission_denied',thumbnailError='Channel custom-thumbnail upload permission was denied; using a YouTube-generated thumbnail.')
        save(receipt_path,receipt)
    if metadata.get('thumbnail') and not receipt.get('thumbnailSet') and config.get('customThumbnailsSupported') is not False:
        thumbnail = (metadata_path.parent / metadata['thumbnail']).resolve()
        try:
            thumbnail_result = youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumbnail),mimetype='image/jpeg',resumable=False)).execute()
            if not thumbnail_result.get('items'):
                raise RuntimeError('YouTube did not confirm the custom thumbnail.')
            receipt['thumbnailSet'] = True
            save(receipt_path,receipt)
        except Exception as thumbnail_error:
            details = json.loads(thumbnail_error.content).get('error',{}) if hasattr(thumbnail_error,'content') else {}
            reasons = [item.get('reason') for item in details.get('errors',[])]
            if getattr(getattr(thumbnail_error,'resp',None),'status',None)==403 and reasons==['forbidden']:
                receipt.update(thumbnailSet=False,thumbnailStatus='permission_denied',thumbnailError=details.get('message','Custom thumbnail permission denied'))
                config['customThumbnailsSupported']=False
                save(config_path,config)
                save(receipt_path,receipt)
                print('Custom thumbnail unavailable:',receipt['thumbnailError'],flush=True)
            else:
                raise
    for attempt in range(60):
        items=youtube.videos().list(part='snippet,status,processingDetails',id=video_id).execute().get('items',[])
        if not items: raise RuntimeError('Video ID returned but status is not yet readable; keep the receipt and check later.')
        item=items[0]
        if item['snippet']['channelId'] != channel_id: raise RuntimeError('Uploaded channel mismatch.')
        status=item['status']; processing=item.get('processingDetails',{}).get('processingStatus')
        receipt.update(actualVisibility=status['privacyStatus'],uploadStatus=status.get('uploadStatus'),processingStatus=processing,madeForKids=status.get('selfDeclaredMadeForKids'),verifiedPublishAt=status.get('publishAt'))
        if config.get('deferScheduledProcessing') and publish_at and status.get('publishAt') and processing not in ('failed','terminated') and status.get('uploadStatus') not in ('failed','rejected','deleted'):
            actual = datetime.fromisoformat(status['publishAt'].replace('Z','+00:00'))
            expected = datetime.fromisoformat(publish_at.replace('Z','+00:00'))
            if actual != expected or status['privacyStatus'] != 'private':
                raise RuntimeError('Returned schedule differs from requested schedule; inspect receipt.')
            receipt['state']='scheduled'
            save(receipt_path,receipt)
            print(json.dumps(receipt,indent=2),flush=True)
            return
        if processing=='succeeded' or status.get('uploadStatus')=='processed':
            if publish_at and status.get('publishAt'):
                actual = datetime.fromisoformat(status['publishAt'].replace('Z','+00:00'))
                expected = datetime.fromisoformat(publish_at.replace('Z','+00:00'))
                if actual != expected or status['privacyStatus'] != 'private':
                    raise RuntimeError('Returned schedule differs from requested schedule; inspect receipt.')
                receipt['state']='scheduled'
            elif publish_at:
                raise RuntimeError('YouTube did not confirm the requested schedule; inspect receipt.')
            else:
                receipt['state']='published' if status['privacyStatus']=='public' else 'uploaded' 
            save(receipt_path,receipt)
            if config_path==ROOT/'youtube-publishing.json' and receipt['state']=='published':
                try:
                    from archive_published_shorts import sync as archive_shorts
                    archive_shorts(youtube)
                except Exception as archive_error:
                    print('Published upload confirmed; local archive needs attention:',type(archive_error).__name__,flush=True)
            print(json.dumps(receipt,indent=2),flush=True)
            return
        if processing in ('failed','terminated') or status.get('uploadStatus') in ('failed','rejected','deleted'):
            receipt['state']='failed'; save(receipt_path,receipt)
            raise RuntimeError('YouTube processing failed; inspect the saved receipt.')
        receipt['state']='processing'; save(receipt_path,receipt)
        print('YouTube processing; visibility:',status['privacyStatus'],flush=True)
        time.sleep(5)
    print('Uploaded; processing still pending. Receipt saved:',receipt_path,flush=True)

if __name__=='__main__':
    try: main()
    except Exception as e:
        # Avoid printing token-bearing HTTP request objects or resumable URLs.
        if hasattr(e,'resp'):
            print('YouTube API request failed (HTTP '+str(e.resp.status)+'). Check API enablement, permission, and quota. Existing upload state was retained.',file=sys.stderr)
            try:
                detail=json.loads(e.content).get('error',{})
                print('API reason: '+', '.join(str(x.get('reason')) for x in detail.get('errors',[])),file=sys.stderr)
                print('API message: '+detail.get('message',''),file=sys.stderr)
            except Exception: pass
        else: print(str(e),file=sys.stderr)
        sys.exit(1)
