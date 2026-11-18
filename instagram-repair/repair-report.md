# Instagram schedule repair — November 4, 2026

Account: @tech_at_60. Existing authorization: one eligible Reel daily at 19:00 Asia/Kolkata, with ongoing permission to publish. The November 4 request additionally authorizes recovery of the missing video.

## Diagnosis

The cloud workflow was active and all 30 numbered source videos were hosted in the existing public Release. Authentication, account identity, token expiry and Meta publishing quota passed read-only checks. Instagram and the encrypted cloud ledger both showed the last publications on November 2, with no Reel for November 3. No unfinished daily job existed before recovery.

The three latest scheduled runs started at 01:38, 01:54 and 03:05 IST on November 4, after the November 3 19:00–22:00 window. Their tests passed and their publisher correctly returned MISSED_PUBLISH_WINDOW rather than posting a backlog. This establishes late execution; it does not establish the underlying GitHub scheduling cause.

## Deployed repair

Commit: bd3b97e44455c95426256b6ee2eb8a17d22dcf3b

- Set an explicit Asia/Kolkata timezone on the cloud schedule.
- Retain 18:45 private preparation and off-hour retries at 19:03–21:48; retain the application publication window and daily/hash limits.
- Extend the existing 15-minute Mac asset-sync helper with a backup cloud dispatch. It runs only within the evening window, when no Reel is recorded today, an eligible source exists, and no workflow is active or recently started.
- The backup helper never sends Meta mutations or enables local publishing. Cloud cron remains independent of the Mac.
- Export the new module and tests with their deployment dependencies. Scan the export for configured secrets before deploying.
- All 79 tests pass locally. The deployed Ubuntu/Python 3.12 suite and read-only cloud check are tracked below.

## Recovery and verification

Exact source: lesson 004, HTML Paragraphs.
Original SHA-256: 988cc56e6a2dedae882c497621ffe4a44c9e432495acf92737671d23954b7545

Recovery run: https://github.com/kamalkrgupta/techat60-instagram-publisher/actions/runs/41781316456
Final deployed read-only validation (success): https://github.com/kamalkrgupta/techat60-instagram-publisher/actions/runs/41782575841

Recovery is not a confirmed publication until Meta returns a media ID/permalink and the cloud ledger records it. A recovered publication consumes the actual calendar day's allowance; the regular evening run then skips that day.

## Maintenance

```sh
cd /Users/impulsiveweb/Techat60-Instagram
.venv/bin/python github_deploy.py status
.venv/bin/python github_deploy.py sync
.venv/bin/python publisher.py --status
.venv/bin/python publisher.py --queue
.tools/gh run list --repo kamalkrgupta/techat60-instagram-publisher --limit 10
.tools/gh workflow run instagram-daily.yml --repo kamalkrgupta/techat60-instagram-publisher --ref main -f mode=check
```

GitHub can delay or drop scheduled workflow events. This repair adds resilience and monitoring, not an exact-minute guarantee. Official reference: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule

Workflow: https://github.com/kamalkrgupta/techat60-instagram-publisher/actions/workflows/instagram-daily.yml
YouTube schedules, upload records and original source videos were not changed.

## Confirmed recovery

HTML Paragraphs was published at 11:27:18 IST on November 4, 2026.
Media ID: 18154955380544884.
Live Reel: https://www.instagram.com/reel/DfTwaUHCY5H/
Successful recovery run: https://github.com/kamalkrgupta/techat60-instagram-publisher/actions/runs/41782230862

The original binary upload returned ProcessingFailedError and remained IN_PROGRESS. Its worker was canceled and confirmed stopped. Before retiring its private attempt, the operator verified no publish attempt or media ID existed, no exact-caption Reel existed, and Instagram had no publication that day. The abandoned attempt was checkpointed before a second private container was created. Meta's hosted-source route then published successfully and was verified against the encrypted ledger.

Routine cloud publication now uses the same hosted-source route to avoid the observed direct-upload failure. Source URLs must belong to the configured repository, match the manifest's selected original hash, and pass pending-job checks. An unfinished direct upload or uncertain publication blocks switching. Both upload paths retain the original hash identity and daily guards. The original source files remain unchanged.

There is exactly one confirmed Reel on November 4. The next regular slot is November 5 at 19:00 IST; tonight's regular invocation should skip. There are 26 remaining numbered course videos in the cloud queue, plus one already-published special Reel outside that numbered course.

Final Ubuntu/Python 3.12 validation passed all 79 tests plus read-only Meta authentication, durable ledger restore and source availability on the final commit.
