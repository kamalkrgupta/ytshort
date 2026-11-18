# Mac-independent 8 AM checker — prepared, not deployed

Render cron: `30 2 * * *` UTC = **08:00 Asia/Kolkata**, daily. This package needs a connected Render account, a private source repository or image registry, and the existing YouTube OAuth authorization installed as the encrypted `YOUTUBE_OAUTH_JSON` environment secret. Credentials are not included in this folder.

The checker discovers uploaded videos from YouTube on every run and verifies the next three days of releases. It can correct release timestamps and publish processed overdue videos without a Mac. An unresolved issue fails the run so the cloud provider records it as a failure. It does not send external messages.

Missing, stuck or failed uploads are reported. This package alone cannot render or reupload local-only media. To provide full automatic recovery while the Mac is off, move the renderer, source files and video assets to cloud compute/storage as well. Render cron storage is ephemeral; persistent video production needs an additional object store or a disk-backed background worker.

Render currently documents a $1/month minimum per cron service, with usage-based charges. Storage and full video production add costs. No cloud resources or billing have been activated.

Deployment steps after connection: create a private source repository from this folder; set the OAuth secret without putting it in git; deploy the cron; manually trigger one run and inspect results; verify the 02:30 UTC schedule. Keep the local checker as fallback until the cloud run is verified.
