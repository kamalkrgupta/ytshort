# Publish completed videos to YouTube

Read after video verification. This is an agent workflow: adding this document does not install an uploader, connect an account, or create a background watcher.

## One-time setup

Keep non-secret preferences in `youtube-publishing.json` in the video workspace (a starter is supplied in assets). Ask only for missing settings:

- Exact channel URL or @handle; resolve and save the channel ID using the authenticated provider. Check the connected destination matches it, including Brand Account selection.
- A supported publishing connection: prefer an already connected integration with confirmed YouTube video-upload capability. An integration description alone does not establish upload support. If needed, discover integrations and inspect their actual tools after connection. Alternatively use an authorized local YouTube Data API OAuth uploader.
- Default visibility: public, unlisted, or private. Set it explicitly. For scheduled publication, collect date, time, timezone, and confirm the provider supports scheduling.
- Audience declaration: made for kids or not made for kids. Obtain the owner's setting; do not infer it from an educational topic.
- Whether completed videos should upload automatically. When the user has requested automatic uploads, record that authorization and reuse it within the configured channel and visibility. Do not require another per-video confirmation.
- Optional defaults: language, category, playlist, branded description ending, and channel-specific call to action. These should not block setup.

For direct API setup, enable YouTube Data API v3 in a Google Cloud project, configure OAuth consent, create a Desktop OAuth client, and have the user complete Google sign-in and consent locally. Use the scopes needed for upload and authenticated channel verification; an API key or channel URL alone cannot authorize uploads. Ask for a local credentials-file path, never a password, verification code, refresh token, or secrets pasted into chat. Store OAuth credentials outside the skill, generated artifacts, and version control. Never put them in the distributable archive. Follow current official upload and OAuth documentation rather than assuming an SDK or endpoint is available:

- https://developers.google.com/youtube/data/guides/uploading_a_video
- https://developers.google.com/youtube/data/reference/rest/v3/videos/insert
- https://developers.google.com/youtube/v3/guides/authentication

Verify effective visibility after upload; service restrictions may differ from the requested setting. Do not promise public publishing until confirmed.

## Per-video process

1. Confirm recorder success, resolution, duration, frame count, and expected audio. Upload only the verified final export, including the closing call to action when requested.
2. Generate `out/youtube-metadata.json` and a readable `out/youtube-upload-details.txt` from the actual video. Use a clear, accurate title aimed at the topic and audience, a description whose first lines explain the lesson, one relevant subscriber invitation, and a concise list of relevant tags. Use up to three relevant hashtags in the description. Do not promise views or subscribers or add unrelated trending keywords. YouTube says tags play a minimal discovery role: https://support.google.com/youtube/answer/146402
3. Load the workspace publishing preferences and check the authenticated channel, explicit visibility, audience declaration, and upload permission. If required settings or connection are missing, deliver the MP4 and metadata and list the missing setup. Do not silently substitute another channel or visibility.
4. Compute the final MP4 SHA-256. Check `out/youtube-upload-receipt.json` for the same channel and hash. If a video ID already exists, return that result rather than uploading a duplicate. Revisions must not automatically replace, delete, or publicly upload a second copy; establish the user's revision publishing preference first.
5. Persist an `uploading` receipt with hash, channel ID, timestamp, and a resumable upload/session or provider job identifier when available. Upload the local MP4 using the confirmed provider capability or authorized API uploader, supplying title, description, tags, visibility, audience, and optional approved defaults. With the API, use resumable upload; resume the same session after a transient failure. Do not blindly repeat a create/upload operation after an uncertain result. Reconcile the existing job/session/video first; if that is impossible, report the uncertain state and stop further upload attempts.
6. Poll processing or the publishing job with bounded retries. Stop on authentication failure, channel mismatch, quota or policy rejection, or after a reasonable retry limit. Preserve session state for resuming. Do not retry indefinitely or create duplicates to bypass errors.
7. Verify the returned video ID, destination, processing status, and effective visibility. Save the completed receipt with video URL, requested and actual visibility, hash, title, and provider result. Distinguish uploaded, processing, scheduled, and published. Report the MP4 and confirmed URL/status to the user. If the connection lacks permission to read back status, disclose that verification limit instead of claiming public release.

Keep receipt files local; exclude resumable session URLs and other credential-bearing state from shareable deliverables. A persistent scheduled/background automation is a separate setup task, not implied by this agent workflow.
