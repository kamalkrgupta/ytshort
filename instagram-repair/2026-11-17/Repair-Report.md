# Instagram publisher repair — November 17, 2026

Account: @tech_at_60. Existing authorization remains one eligible Reel daily at 19:00 Asia/Kolkata, with the existing grace window ending at 22:00. YouTube videos and schedules were not changed.

## Diagnosis

The screenshot's latest run, [43985339092](https://github.com/kamalkrgupta/techat60-instagram-publisher/actions/runs/43985339092), passed all 87 original tests. Its publisher started at 05:39 IST on November 17 for the November 16 19:00 slot and returned MISSED_PUBLISH_WINDOW. [43761034841](https://github.com/kamalkrgupta/techat60-instagram-publisher/actions/runs/43761034841) showed the same late-window failure for November 15. These failures were not caused by rejected Instagram credentials or a broken test suite.

The existing design relied on evening cron events arriving inside a short publication window. GitHub delivered the inspected events overnight. The old Mac backup also started only at 18:45 and treated any queued workflow as an active publisher indefinitely.

A November 11 event remained listed queued with no jobs. GitHub's cancellation endpoint said it was already completed while read endpoints continued listing it queued. The repair does not depend on clearing that inconsistent record: an old unstarted queue entry no longer blocks backup dispatch indefinitely. Genuinely running jobs and recent queued jobs still block another backup.

## Deployed changes

Commit: [5a352d7e3744803ebe6fd89c7dc4bb7a8fba6eef](https://github.com/kamalkrgupta/techat60-instagram-publisher/commit/5a352d7e3744803ebe6fd89c7dc4bb7a8fba6eef).

- Explicit Asia/Kolkata cron entries start workers at 13:31, 15:31 and 17:31. Evening retries remain at :03 and :33 from 19:00 through 21:00.
- A daily worker starting between 13:30 and 19:00 validates authorization, source and restored history, then waits until private preparation at 18:45. It does not upload or publish during the afternoon wait.
- Publishing jobs have a six-hour timeout, sufficient for the maximum 5.5-hour wait plus setup and processing. Read-only checks keep their shorter timeout.
- The Mac asset-sync backup can dispatch the same guarded cloud worker from 13:30. Queued entries older than 30 minutes do not block it forever; running jobs, recent queued jobs and unknown timestamps remain protected.
- One-per-day, source-hash, exact-account, uncertain-outcome, publish-window and encrypted-checkpoint guards remain intact. No automatic overnight catch-up or backlog burst was added.
- The installed local source/export files were synchronized with the tested deployment. Original local files are backed up in before-local/. Future redeployments will retain the repair.

Cloud publication was temporarily disabled for deployment, and re-enabled only after the exact deployed commit passed its cloud tests and read-only Meta/source/history check. No new hosting provider, billing, paid API or external message was introduced.

## Verification

- Local suite: **95 tests passed**, including afternoon waiting, time boundaries, failed preflight, midnight/window crossing, stale queued workflows and duplicate guards.
- [Deployed read-only validation](https://github.com/kamalkrgupta/techat60-instagram-publisher/actions/runs/44067873273): **success**, 95 Linux/Python 3.12 tests passed; correct Instagram identity and token expiry verified; 47 source assets accessible; encrypted state restored with 11 confirmed publications; zero Meta mutations.
- Workflow is enabled. Cloud publishing is active. Local Meta publishing is disabled.
- At 16:19 IST, the authoritative encrypted cloud ledger contained today's WAITING checkpoint for [worker 44068142527](https://github.com/kamalkrgupta/techat60-instagram-publisher/actions/runs/44068142527), on the tested commit, targeting **November 17 at 19:00 IST**. Its setup/tests passed and its publishing step was running.
- Pending Meta jobs: zero at that check. The next eligible source is **lesson 011, HTML Comments**, SHA-256 e4de41a1e56da252e0270d4feda4ef58b40f28393ab8843bc81db76d7525d424.
- Latest confirmed public Reel remains November 11. Today's publication has **not yet been observed**; the worker's waiting checkpoint is not a publication receipt. Confirm the media ID/permalink and durable ledger result after 19:00.

## Limits and operations

GitHub can still delay or drop scheduled events. Starting early and retaining a Mac-online backup gives substantially more lead time, but does not guarantee an exact publication minute. The already-running worker handles today's slot without needing the Mac to remain on. Historical failed runs stay red as an audit trail.

No missed-day backfill was performed. The next normal daily publication consumes the actual day's allowance.

Maintenance commands (existing installation):

```sh
cd /Users/impulsiveweb/Techat60-Instagram
.tools/gh run view 44068142527 --repo kamalkrgupta/techat60-instagram-publisher
.venv/bin/python github_deploy.py sync
.venv/bin/python publisher.py --status
```

While a waiting publishing worker owns the concurrency group, another cloud check will queue behind it. Use the read-only local status/remote checkpoint for an interim inspection rather than repeatedly dispatching checks.

Official scheduling reference checked: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule

Evidence: deployment.log, local-tests.log, deployed-commit.txt, live-verification.json and the linked workflow runs. The publisher skill used was /Users/impulsiveweb/.codex/skills/instagram-reels-cloud-publisher/SKILL.md.

## Requested retest

Re-ran the exact deployed source suite: 95 tests passed. Added a separate offline acceptance simulation in test_future_days.py: seven successive days using the real Publisher and SQLite ledger with mocked Meta responses. Every day waited from 13:31 to private preparation at 18:45, staged without publishing early, confirmed one publication at 19:00, blocked another same-day publication, and refused the 23:00 event. Seven distinct hashes and media IDs were recorded. This is a simulation, not seven live Instagram uploads; no production files or cloud deployment were changed for this retest.

GitHub worker 44068142527 remained in_progress with dependency installation and automated tests successful and its publishing step running. Tonight's actual media ID/permalink is still unconfirmed before the publication time. Existing retry and uncertainty guards remain active. No future uptime or exact cron delivery guarantee is implied.
