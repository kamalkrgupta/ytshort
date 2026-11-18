# Implementation contract

Read when building or reviewing the local app and cloud runner. Adapt modules and names to the repository; preserve these behavioral guarantees.

## Verify current protocol

Primary starting points (follow current links and version-specific instructions):

- Meta Instagram platform: https://developers.facebook.com/docs/instagram-platform/
- Facebook Login content publishing: https://developers.facebook.com/docs/instagram-platform/instagram-api-with-facebook-login/content-publishing/
- Official Meta Reel examples: https://github.com/fbsamples/reels_publishing_apis
- Facebook long-lived tokens: https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived/
- Token debugging: https://developers.facebook.com/docs/facebook-login/guides/access-tokens/debugging-and-error-handling/

For Facebook Login, the intended flow is:

1. POST `/{ig-user-id}/media` with `media_type=REELS`, `upload_type=resumable` and caption.
2. Capture the creation ID and upload URI. Validate the documented upload hostname before sending credentials.
3. Send binary bytes with the documented authorization, offset and file-size headers. The Facebook Login example uses `Authorization: OAuth <token>`, `offset: 0`, and `file_size: <byte-count>`; verify the current protocol, HTTP method and whether/how offsets can resume before implementing. Do not assume the Graph JSON POST method applies to the binary upload.
4. Poll container `status_code` with bounded timeouts until `FINISHED`; handle terminal error/expiry explicitly.
5. Persist publish intent before POST `/{ig-user-id}/media_publish` with `creation_id`.
6. Retrieve and confirm the resulting media ID, permalink and publication timestamp before recording success.

Do not log authenticated upload URIs or raw request exceptions containing query tokens. Never blindly retry a create/upload/publish request that may have succeeded. Read-only GET retries may use bounded backoff and Retry-After. Respect Meta's account publishing limits and errors.

## Configuration

Use environment overrides plus a protected local .env. Validate required values before mutating APIs. Keep secret fields out of repr/debug output. Example keys (values must belong to the recipient):

```dotenv
INSTAGRAM_ACCOUNT_ID=
FACEBOOK_PAGE_ID=
META_APP_ID=
META_ACCESS_TOKEN=
META_APP_SECRET=
GRAPH_API_VERSION=
VIDEO_FOLDER=/absolute/path/to/source-videos
TIMEZONE=Asia/Kolkata
PUBLISH_TIME=19:00
MISSED_RUN_GRACE_MINUTES=180
CAPTION_MODE=fallback
BRAND_NAME=
INSTAGRAM_HANDLE=
PUBLISH_BACKEND=local
```

Blank secret values mean setup is incomplete. Do not replace them with another account's defaults. App secret is needed only for flows that require it; avoid granting runtime runners unnecessary secrets. OpenAI is optional and must remain unused in free mode. Validate IANA timezone and configurable publish time. UTC cron conversion must handle DST for zones that observe it; use an application timezone gate even with cron.

Validate token identity, required permissions, accessible Page-to-Instagram connection, expiry and data-access expiry where available. Use documented debug_token authentication. Explain missing app review/live mode or role restrictions when they affect the recipient's deployment. Support a documented short-to-long-lived Facebook user-token exchange when applicable. Persist the verified replacement privately only after validation. Give expiry warnings at useful intervals and a local renewal command; do not imply indefinite refresh.

## Suggested modules

- `config.py`: validated account, timezone, secrets, backend and storage configuration.
- `video_source.py`: deterministic numeric ordering, SHA-256, media inspection and derived temporary upload file.
- `caption_generator.py`: free topic-specific templates; optional authorized AI mode with output limits.
- `meta_client.py`: safe Graph requests, documented resumable upload, polling, confirmation and reconciliation.
- `database.py`: transactional durable ledger and schema migrations.
- `publisher.py`: lock, time/day guard, recovery state machine and CLI.
- `cloud_runner.py`: restore durable state, download/verify selected asset, run checks or scheduled publishing, persist commits.
- `github_store.py`: GitHub API wrapper, encrypted snapshot load/save with compare-and-swap.
- deployment/sync helper: source allowlist, video hosting, secrets, state bootstrap, checks and controlled handoff.

Prefer a single coherent publisher across local and cloud backends to prevent divergent recovery behavior.

## SQLite and recovery

Keep at least:

- Queue: original filename, numeric order, original SHA-256, bytes, topic, caption, asset reference, eligibility.
- Jobs: local slot date, original hash, status, creation ID, upload progress/URI (sensitive), media ID, caption, attempt times and sanitized errors.
- Publications: unique media ID, unique original content hash when known, permalink, confirmed publication time and account ID.
- Settings/events: schema version, configured account, seed decisions, activation and audit events.

Enforce one reserved daily slot per account and one active job per content hash. A known terminal failure may release/retry a slot only through an explicit recovery transaction after reconciliation. Keep old attempt evidence. An unresolved job blocks choosing another video, including across midnight, until remote publication status is established.

Possible states: CREATING, CREATE_UNKNOWN, CREATED, UPLOADING, UPLOAD_UNKNOWN, PROCESSING, READY, PUBLISHING, PUBLISH_UNKNOWN, VERIFY_PENDING, PUBLISHED, FAILED, EXPIRED. Names can differ; uncertainty must remain represented.

Commit each transition before the next externally mutating operation. When cloud-backed, the encrypted remote checkpoint must succeed before continuing, not just at process exit. A checkpoint failure stops further Meta writes. Persist content hash and caption before creation, creation ID before upload, and PUBLISHING before media_publish. On ambiguous publish results, inspect container published status and recent account media with exact retained identifiers/caption evidence; do not guess from similar titles. If reconciliation cannot uniquely establish the result, stop and expose an actionable hold.

SQLite backup API must capture committed WAL transactions before encryption. Never copy just the main file while WAL is live. Enable integrity checks, restrictive permissions and schema/account identity validation. Seed existing Reel records only with confirmed IDs/permalinks and an explicit content match. Keep unmatched seeds visible for reconciliation.

## CLI behavior

- `--dry-run`: inspect local queue/selection/caption only; no upload, publish or paid API call.
- `--check`: read-only config, source, API, token, identity and seed validation; no creation container.
- `--status`, `--queue`, `--history`: readable state; cloud mirror must be labeled with last sync time.
- `--scheduled`: active-backend check, timezone/day/grace guards, reconcile, at most one daily publication.
- `--publish-next`: define its guards clearly; never silently bypass cadence or approval.

Use cross-process locks locally and Actions concurrency remotely. Reject local Meta publishing once cloud owns the schedule.

## Meaningful tests

Mock Meta and GitHub mutation boundaries. Cover original bytes preserved; numeric order; duplicate content with a new name; confirmed seed excluded; uncertain match held; one success per timezone day; crash before/after publish; lost publish response; uncertain job across dates; remote checkpoint failure blocks further Meta writes; no empty-ledger fallback; stale remote SHA rejected; tampered/wrong-key encrypted state; wrong account rejected; fallback makes no API calls; dry-run and check never upload/publish; safe export excludes secrets.

Run tests from the exported project on the actual Linux/Python Actions target as well as locally. Mock tests do not establish real direct-upload compatibility. A live publish is a separate authorized operation; state honestly if only mocks and read-only checks were run.
