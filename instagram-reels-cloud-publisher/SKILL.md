---
name: instagram-reels-cloud-publisher
description: Build, test, deploy, or maintain a direct-upload Instagram Reels publisher using Meta Graph API and GitHub Actions, with a durable queue and duplicate prevention, so publishing works while the source computer is off.
---

# Instagram Reels cloud publisher

Implement the automation in the user's environment and repository; do not stop at sample code. This skill is a reusable engineering workflow, not a prebuilt publisher or a grant of permission to post. It contains no account credentials, source videos, or personal publication history.

## Establish the deployment

Inspect existing code, schedulers, source folders and publication records before changing anything. Ask only for missing choices that affect deployment: Instagram professional account, Meta app/login method, source folder, timezone, daily time, posting frequency, GitHub repository/visibility and caption budget. Default to one Reel daily and free deterministic captions when the user wants no cost; do not assume a particular account, path or timezone.

Keep source videos and unrelated automations unchanged. In particular, a YouTube-published folder can be an input without giving permission to modify YouTube schedules or publishing records. Store Instagram state separately.

Verify current official documentation before choosing Graph API version, permissions, upload headers, token exchange, Actions versions and free-tier assumptions. Read [references/implementation.md](references/implementation.md) for the implementation contract and primary documentation starting points. Use the matching Facebook Login or Instagram Login documentation consistently; do not mix their hosts, IDs, permissions or token types.

Use connected tools where sufficient; use a local authenticated GitHub CLI when repository, workflow or secret operations are unavailable through them. Have the user enter credentials locally into a mode-600 file or a hidden terminal prompt. Never ask for credentials in chat or print them.

## Build and validate locally

Use a supported Python version in an isolated environment. Implement configuration, Meta client, caption generation, source scanning, SQLite ledger, CLI, cloud runner and deployment/sync helpers. Keep account identity checks configurable, but fail on a mismatch against this user's explicitly configured account.

Select numbered MP4s in ascending numeric order. Fingerprint original bytes with SHA-256; deduplicate by content, not just filename. Seed any existing Instagram publications with confirmed IDs/permalinks. A similar title is insufficient to bind an old Reel to a file: compare evidence and ask if uncertain. New folders start with an empty, explicitly initialized ledger, never with another person's history.

Implement the documented resumable direct upload, bounded processing polling, publish and confirmation sequence. No Cloudinary, browser automation or unofficial Instagram API is needed. Preserve original files; create temporary compatible derivatives only if required.

Use captions inferred from filenames and available lightweight metadata. Include a truthful hook, beginner-friendly topic explanation, natural keywords, a varied call to action, and 3–5 relevant hashtags. Parameterize brand/handle and language. The free mode must make no paid API calls even if a key exists. An optional API mode must respect the user's budget and fall back deterministically.

Test selection, seed matching, daily limits, timezone boundaries, recovery, uncertainty handling, state encryption, stale writes and secret exclusion. Run a dry-run that performs no uploads or public publishing, followed by read-only authentication and API checks. Report what has and has not been exercised against Meta.

## Deploy to GitHub Actions

Read [references/cloud-deployment.md](references/cloud-deployment.md) for repository layout, persistent state, scheduling and handoff. The GitHub runner must have both video bytes and the durable publication ledger without accessing the sleeping computer. A cron file alone is not a working cloud deployment.

Repository visibility is a user choice. Public repositories and Release assets expose videos and filenames to everyone. Existing publication on YouTube does not automatically authorize copying videos into a public GitHub repository. Obtain the user's visibility choice before uploading. Private storage must be checked against current free allowances; do not promise unlimited free capacity or enable billing.

Build a strict source export allowlist. Exclude .env files, tokens, app secrets, encryption keys, logs, plaintext SQLite, local approval files and private account records. A local deployment module imported by tests must also be exported with all its import dependencies, or its test must be deliberately scoped to local execution. Run the exact exported test suite on Linux before activation.

Use repository secrets for Meta credentials, the state encryption key and the cloud enable flag. Keep cloud publishing disabled until the current commit passes Actions tests and a read-only Meta/source/state check. Inspect failures and correct them before switching backends.

Before public posting or activation, verify explicit authorization for this account and cadence. Reuse existing ongoing authorization; do not ask per Reel when that is already authorized. Permission from the person who shared this skill does not transfer to its recipient.

For migration, lock the local publisher, reconcile unfinished work, copy the latest ledger, disable only the old Instagram publisher, then enable cloud publishing. Leave unrelated schedules untouched. If enabling has an uncertain result, leave local publishing disabled and inspect cloud state before any rollback.

Run a final read-only cloud check after activation. Confirm workflow enabled, correct UTC schedule, durable history restored, source accessible, intended account authenticated and only one publishing backend active.

## Operations and reporting

Supply CLI commands for check, dry-run, status, queue, history and scheduled execution, plus instructions for pause, resume, credential renewal and recovery. Validate tokens and warn before expiry; Facebook user tokens cannot be renewed forever without reauthorization. Updating a local token must also update the cloud secret through a protected channel.

Explain that Actions can queue, delay or disable scheduled workflows; it cannot guarantee an exact minute. Newly added local videos become cloud-eligible only after upload while the source computer is online. Within an agreed grace window retry safely; after it expires skip that day's slot without bursting through a backlog.

Report separately: files implemented, tests passed, read-only authentication, live uploads actually tested, workflow installed, publishing activated, next local-time slot, first eligible video and any remaining steps. Link the workflow run and provide exact maintenance commands. Never claim setup is complete solely because a workflow YAML exists.
