# Cloud deployment, scheduling and maintenance

Read for first deployment, migration from a local scheduler, or cloud recovery.

## Hosting and free usage

Check current GitHub documentation before making cost/visibility claims:

- Billing: https://docs.github.com/en/billing/concepts/product-billing/github-actions
- Scheduled events: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
- Secrets: https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions
- Release assets: https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases

Standard hosted runners in public repositories can be a free option under current GitHub rules. Public releases are public downloads; get a deliberate visibility choice. Private repositories use plan-specific allowances. Check video size, Release asset and API limits. Avoid paid AI calls, larger runners, LFS or storage products with unapproved charges. Do not claim a universal zero-cost guarantee.

Upload source videos while the source computer is awake. Use immutable asset names derived from numeric index plus SHA-256, and a manifest such as:

```json
{"videos": [{"filename": "002 - Topic.mp4", "order": 2, "sha256": "<full-sha256>", "bytes": 12345, "topic": "Topic", "download_url": "<approved-asset-url>"}]}
```

Verify bytes and hash after download, restrict redirect hosts to the approved storage provider and never forward GitHub or Meta bearer tokens to an arbitrary URL. Manifest titles/filenames themselves may be sensitive. A local periodic helper can discover new files and upload assets; it must never publish to Meta. Cloud runs use only already synchronized assets when the computer is off.

## Durable encrypted ledger

Ephemeral Actions files, cache and expiring artifacts are not authoritative publication history. One workable design is a separate `instagram-state` branch containing only an encrypted SQLite snapshot:

- Generate a random 32-byte AES-256-GCM key locally, save mode 600 and store a copy in GitHub Actions secrets.
- Use a fresh random 12-byte nonce for each snapshot and authenticated associated data binding repository, schema and purpose.
- Keep a private backup of the key. Loss of the only key blocks safe recovery; never auto-initialize an empty replacement.
- On each run, pin the latest state commit, download, decrypt, validate SQLite and expected account, and restore a runtime DB.
- Write snapshots using the GitHub Contents API's expected blob SHA (compare-and-swap). A conflict means stop and reload/reconcile; do not force overwrite.
- Persist critical transitions before the next Meta write. Save confirmed results even if later reporting fails. An uncertain GitHub checkpoint result also requires re-reading remote state before proceeding.
- Bootstrap once explicitly: empty for a new account, or a verified migration of that recipient's own history. A missing branch after initialization is an error, never a fresh start.

A different durable store is acceptable if it meets the same crash-recovery and consistency guarantees and fits authorized cost constraints. Git history retains old encrypted snapshots; encryption is not a substitute for secret hygiene and retention planning.

## Workflow

Use reviewed supported versions of checkout/setup-python (verify current tags or pin immutable SHAs), a supported Python version, ffmpeg if needed, a bounded job timeout and minimal permissions. State-branch writes require contents:write. Do not run the publishing job against untrusted pull request code, and do not print all environment variables.

Required behavior:

1. Checkout trusted default-branch source, install pinned/bounded dependencies.
2. Run the exact exported automated tests.
3. Restore encrypted state and check account identity.
4. Check enable flag; default disabled.
5. Download only the selected or unresolved asset, verify hash and inspect compatibility.
6. Apply timezone, approval, daily-slot, grace-window and uncertainty guards before publishing.
7. Encrypt and checkpoint every critical commit, then report sanitized status.

Use a single concurrency group for all check/publish runs, `cancel-in-progress: false`, and repository state compare-and-swap. Scheduled and manual publication must share the same guards. A manual read-only `check` mode must never create containers or upload.

For 19:00 Asia/Kolkata, UTC target is 13:30. A tested deployment can trigger at 13:15 UTC for early preparation and at 13:30/13:45 for retries (`15,30,45 13 * * *`). All runs still apply the local-time gate and one-per-day ledger. Choose an explicit grace window; late runs outside it do not create backlog bursts. Change this example for the recipient's cadence and timezone, including DST if applicable.

Optional early preparation may upload/process a PRIVATE container shortly before the slot, then wait to call media_publish at the target. It must have its own bounded early window and never bypass public-publish guards. Ensure timeout covers setup, processing, waiting and publication. If not implementing this, an early trigger must simply exit before the publish time, with an on-time trigger retained.

Actions can delay/drop queued runs and disable inactive public-repository schedules under GitHub's current rules. Explain this, expose last-run/next-slot monitoring and check inactivity policy. Do not claim an exact-time SLA or that a cron line proves execution.

## Safe deployment sequence

1. Authenticate GitHub locally using approved tooling. Verify intended owner/repository. Never overwrite an unrelated repository.
2. Create/adapt the repo only within user authorization and chosen visibility. Export sources through an allowlist, scan against known secret values and inspect the resulting tree.
3. Add encrypted repository secrets via stdin/structured secret tooling; no command-line token values. Set cloud enable false.
4. Upload authorized videos, manifest and initialized encrypted ledger. No original moves/deletions.
5. Dispatch read-only check on the current default-branch commit. Require Linux tests, asset download/hash verification, token/identity and state restore to pass.
6. If migrating, acquire local publisher lock, stop on unresolved local jobs, snapshot the latest confirmed state, disable only the local Instagram publishing agent, then enable cloud. Record authorization and backend ownership privately.
7. Verify active workflow plus enabled secret through a final read-only run and ensure local publisher refuses Meta writes. Avoid reading/printing the secret value.
8. Install optional local asset/history sync independently. Label it as synchronization, not publishing. Mirror cloud history for local status; never overwrite cloud authority from a stale local mirror.

Do not auto-reactivate local publishing after an uncertain handoff. Inspect remote enable state/history and explicitly establish a single owner before recovery.

## Maintenance deliverables

Generate commands using the recipient's actual repository and project paths for:

- listing runs and viewing failed logs;
- dispatching read-only checks;
- checking local queue/status and cloud mirror freshness;
- uploading new source files and verifying manifest changes;
- pausing cloud publication and confirming the pause;
- updating Meta token repository secret after local validation;
- checking token/data-access expiry;
- recovering an uncertain job without reposting;
- stopping/uninstalling only this automation's local sync/scheduler.

No new public Reel is needed to validate a read-only deployment check. If a user authorizes a live test, record its media ID/hash immediately so daily processing cannot republish it. Provide a concise deployment report that distinguishes implemented, mocked, read-only tested and live-tested behavior.
