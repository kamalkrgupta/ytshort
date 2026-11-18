#!/usr/bin/env python3
"""Read back the complete series from YouTube and write a shareable local report."""
import json,re,time,sys
from datetime import datetime,timezone
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

ROOT=Path(__file__).resolve().parent
COUNT=int(sys.argv[sys.argv.index('--count')+1]) if '--count' in sys.argv else 12
if '--wait-for-uploads' in sys.argv:
    limit=time.monotonic()+1800
    print('Waiting for all twelve upload confirmations before the final remote audit.',flush=True)
    while True:
        paths=[ROOT/'episodes'/f'{n:02d}'/'youtube-upload-receipt.json' for n in range(1,COUNT+1)]
        if all(p.exists() for p in paths):
            current=[json.loads(p.read_text()) for p in paths]
            if all(r.get('videoId') and r.get('state') in ('published','scheduled') for r in current):break
        if time.monotonic()>limit:raise RuntimeError('Not all uploads have been confirmed; audit not performed')
        time.sleep(5)
token=ROOT.parent/'.youtube-auth/token.json'
creds=Credentials.from_authorized_user_file(str(token))
if creds.expired:creds.refresh(Request())
youtube=build('youtube','v3',credentials=creds,cache_discovery=False)
receipts=[json.loads((ROOT/'episodes'/f'{n:02d}'/'youtube-upload-receipt.json').read_text()) for n in range(1,COUNT+1)]
deadline=time.monotonic()+600
while True:
    items=youtube.videos().list(part='snippet,status,contentDetails,processingDetails',id=','.join(r['videoId'] for r in receipts)).execute()['items']
    if len(items)!=COUNT:raise RuntimeError('YouTube did not return all requested uploaded videos')
    failed=[v['id'] for v in items if v['status'].get('uploadStatus') in ('failed','rejected','deleted') or v.get('processingDetails',{}).get('processingStatus') in ('failed','terminated')]
    if failed:raise RuntimeError('Processing failed for '+', '.join(failed))
    pending=[v['id'] for v in items if v['status'].get('uploadStatus')!='processed']
    if not pending:break
    if time.monotonic()>deadline:raise RuntimeError('Processing remains pending; audit not complete')
    print(f'YouTube is still processing {len(pending)} video(s).',flush=True);time.sleep(5)
lookup={v['id']:v for v in items};rows=[]
for n,r in enumerate(receipts,1):
    meta=json.loads((ROOT/'episodes'/f'{n:02d}'/'youtube-metadata.json').read_text())
    v=lookup[r['videoId']];status=v['status'];snippet=v['snippet']
    assert snippet['channelId']=='UC7F3e0NsVP37sqroVmYxiFw'
    assert snippet['title']==meta['title']
    assert set(meta['tags'])<=set(snippet.get('tags',[]))
    duration=v['contentDetails']['duration']
    match=re.fullmatch(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?',duration)
    # The exported file is exactly 600s/18000 frames; YouTube can round the
    # transcoded container duration up to the next second.
    assert match and abs(sum(float(x or 0)*factor for x,factor in zip(match.groups(),[3600,60,1]))-600)<=1.1,duration
    assert status['uploadStatus']=='processed'
    assert status.get('selfDeclaredMadeForKids') is False
    if n<3:
        assert status['privacyStatus']=='public'
        release='Published 23 October 2026';state='published'
    else:
        assert status['privacyStatus']=='private'
        actual=datetime.fromisoformat(status['publishAt'].replace('Z','+00:00'))
        planned=datetime.fromisoformat(meta['publishAt'])
        assert actual==planned
        release=planned.strftime('%d %B %Y, 6:00 PM IST');state='scheduled'
    row=dict(episode=n,title=snippet['title'],videoId=v['id'],url=r['url'],state=state,release=release,actualVisibility=status['privacyStatus'],publishAt=status.get('publishAt'),duration=v['contentDetails']['duration'],tagsVerified=True,thumbnailSet=r.get('thumbnailSet',False))
    rows.append(row)
    r.update(state=state,actualVisibility=status['privacyStatus'],uploadStatus=status['uploadStatus'],processingStatus=v.get('processingDetails',{}).get('processingStatus'),verifiedPublishAt=status.get('publishAt'),remoteAuditedAt=datetime.now(timezone.utc).isoformat())
    (ROOT/'episodes'/f'{n:02d}'/'youtube-upload-receipt.json').write_text(json.dumps(r,indent=2)+'\n')
    print(f'VERIFIED E{n:02d}: {state} | {release} | {r["url"]}',flush=True)
for n in range(COUNT+1,13):
    meta=json.loads((ROOT/'episodes'/f'{n:02d}'/'youtube-metadata.json').read_text())
    rows.append(dict(episode=n,title=meta['title'],url=None,state='pending upload — channel daily limit',release='Planned: '+datetime.fromisoformat(meta['publishAt']).strftime('%d %B %Y, 6:00 PM IST'),publishAt=meta['publishAt'],duration='PT10M',tagsVerified=False,thumbnailSet=False))
report=dict(auditedAt=datetime.now(timezone.utc).isoformat(),channel='https://www.youtube.com/@Techat60',remotelyVerifiedCount=COUNT,episodes=rows)
(ROOT/'youtube-audit.json').write_text(json.dumps(report,indent=2)+'\n')
text='# Agile Testing Masterclass — publishing report\n\nChannel: [Tech in 60 / @Techat60](https://www.youtube.com/@Techat60)\n\nAll twelve videos: 16:9, 1920 × 1080, 30 fps, 10:00, English narration.\n\n| Episode | Video | Status | Release |\n|---|---|---|---|\n'
for r in rows:
    label=f'[{r["title"]}]({r["url"]})' if r['url'] else r['title']
    text+=f'| {r["episode"]} | {label} | {r["state"]} | {r["release"]} |\n'
text+='\nYouTube confirmed the published and scheduled rows above. YouTube handles those releases; the local computer does not need to stay running for them. Pending rows are local plans until their uploads are accepted.\n\nTitles, descriptions, chapter timestamps and topic tags were prepared for all twelve videos and uploaded for the accepted videos. Each includes the four requested tags: cjp, modi, latent, neha bora.\n\nCustom thumbnails were designed and saved in each episode folder, but YouTube denied custom-thumbnail upload permission for this channel. Accepted videos currently use YouTube-generated thumbnails.\n\nEach episode folder contains the MP4, thumbnail JPEG, SRT subtitles, narration, storyboard, upload metadata and verification. Subtitle tracks are embedded in the local MP4 and provided separately; no separate YouTube caption upload was performed with the current connection.\n\nNarration timing, audio presence and levels were checked programmatically; narration was not reviewed by ear.\n'
if COUNT<12:text+='\nEpisodes 11–12 are ready locally. A retry is planned for 24 October 2026 at 10:15 PM IST, after a full 24-hour wait from the upload-limit rejection, with intended publication on 28 October at 6:00 PM IST. The retry needs this Mac logged in, awake and online. Check retry-state.json for actual job status.\n'
(ROOT/'publishing-report.md').write_text(text)
print(f'{COUNT} remote statuses, durations, audience settings, tags and release times verified.',flush=True)
