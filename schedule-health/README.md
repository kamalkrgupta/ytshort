# Daily publishing readiness

Installed job: `com.techat60.schedule-healthcheck`.

Runs daily at **08:00 Asia/Kolkata**. It also runs at login and retries hourly while the current day's audit has unresolved issues. A healthy day's additional hourly runs exit without network calls.

Coverage: Shorts at 11 AM and 4 PM, AI episode pairs at 2 PM, and remaining Agile episode pairs at 6 PM. The audit compares the next three days of planned releases against live YouTube status, including processing completion and exact publish times. Already completed courses naturally stop contributing future slots.

Automatic repairs include correcting private-video release times, publishing overdue ready videos, recovering a missing upload receipt only with an exact channel/title/upload-time match, replacing demonstrably failed or zero-duration stuck uploads from verified local media, restarting existing production workers for missing uploads, and synchronizing ordered playlists. A replacement is attempted at most once per video per day. It preserves the old video privately and archives its receipt rather than deleting the video.

Active producers are inspected read-only; the audit does not modify their files. It retries after they finish. Ambiguous upload matches, revoked Google sign-in, quota restrictions, unavailable source media, or unresolved processing issues are recorded for follow-up; these cannot always be fixed without intervention.

Reports: [latest.md](latest.md), [latest.json](latest.json), timestamped JSON history and activity.log. No email or external messages are sent.

This job runs on this Mac, which must be awake, signed in and online at 8 AM for an on-time local check. Already-uploaded scheduled videos release through YouTube independently. A sleep-delayed calendar event is handled when macOS runs the job after wake.

Validation: nine decision tests cover ready/processing/late/early-public videos, safe status updates, and the canonical Shorts/AI/Agile slot calculations. The job was installed, its 8 AM trigger inspected and a live audit run at setup.
