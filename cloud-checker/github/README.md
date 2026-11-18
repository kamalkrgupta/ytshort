# Free daily YouTube readiness checker

Deployment state: prepared locally; not activated on GitHub.

Use a dedicated **public repository** and standard `ubuntu-latest` GitHub-hosted runners. Standard runner compute is free in public repositories. This workflow does not create paid cloud services, use larger runners, upload artifacts or save caches. Private repositories use an allowance shared with other workflows and can incur costs, so they are not the zero-cost configuration proposed here.

Schedule: `30 2 * * *` UTC, corresponding to **8:00 AM Asia/Kolkata**, every day. GitHub can delay or drop scheduled runs during load, so the exact start time is not guaranteed. GitHub can also disable schedules in public repositories after prolonged inactivity. Scheduled workflows must exist on the default branch.

Only generic checker code and the workflow belong in this public repository. Do not commit authorization, account-specific schedules, scripts, video files, tokens or client secrets.

## One-time setup

1. Create a dedicated public repository such as `techat60-readiness` in your GitHub account and make it accessible to the connected GitHub app. Do not enable paid runners or other paid services.
2. Publish the contents of this directory on its default branch.
3. In repository Settings → Secrets and variables → Actions, create these encrypted repository secrets locally, without sharing their values in chat:
   - `YOUTUBE_OAUTH_JSON`: the authorized-user JSON from the existing `.youtube-auth/token.json` on your Mac.
   - `YOUTUBE_SCHEDULE_JSON`: the non-secret schedule data from `cloud-checker/schedule.json`, kept in a secret to avoid publishing future episode details.
4. Open Actions → Daily YouTube readiness → Run workflow. Confirm success and inspect the report before considering deployment complete.
5. Verify the schedule is enabled. Future title or release-schedule changes must update the schedule secret. New video IDs are discovered by matching exact titles against the authenticated channel's uploads.

The connected GitHub tools available in this session can edit accessible repositories, but do not provide repository creation or repository-secret management. Those one-time setup actions require the repository owner.

## What runs without the Mac

The checker verifies live YouTube uploads and processing and can repair incorrect future release times or publish already-processed overdue videos. It does not render new videos or reupload missing local files. Full video production/replacement without the Mac requires a separate cloud production setup; it is not included or claimed here.

Official guidance:
- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://docs.github.com/en/actions/how-tos/troubleshoot-workflows
