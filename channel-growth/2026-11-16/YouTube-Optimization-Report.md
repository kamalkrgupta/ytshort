# TECH AT 60 — YouTube optimization, November 16, 2026

This campaign improves lesson discovery and gives viewers a clearer next step. It is a bounded metadata and navigation experiment, not evidence of increased reach or subscribers. All 30 video edits, three playlists and their homepage sections were read back and verified. Release settings were verified unchanged across all 108 enumerated videos. See youtube-application-state.json for the execution record.

## Baseline and access

Live channel statistics at the start: 20 subscribers, 1,800 lifetime views and 101 public videos reported by the channel. The uploads enumeration returned 108 unique video records: 100 public and eight private/scheduled. This coverage discrepancy is retained rather than equating the two totals. No hidden or missing record was changed.

The connection supports YouTube Data API reads and edits. Its granted scopes do not include YouTube Analytics. Impressions, CTR, traffic sources, Shorts engaged views, stayed-to-watch, retention and subscribers attributed to each upload remain unavailable here. Raw public views cannot establish why a video is underperforming.

Historical comparison: the November 5 channel baseline was 18 subscribers and 1,331 views. The increases to the current totals cannot be attributed to past optimization work: additional uploads, time and audience exposure are confounding factors.

## Targeted improvements

Six coding lessons receive concise titles and specific opening descriptions:

- JavaScript Functions: Parameters, Return and Your First Function
- JavaScript If Else: Choose a Message Based on a Score
- JavaScript For Loops: Print 1 to 5 with One Loop
- JavaScript Arrays: Index 0, Push and Length Explained
- Responsive Web Design: Make a Layout Fit Phone and Desktop
- CSS Media Queries: Change Your Layout at a Breakpoint

Each description includes one answerable exercise question, a clear beginner audience promise and instructions to find the relevant channel playlist. Original exercises, reference links and course context remain. These videos were selected for a focused test of generic packaging, not because unavailable CTR data showed a particular problem. HTML introduction and links, the two leading coding examples in the snapshot, remain unchanged; prior November 3 and November 5 experiments remain intact.

Twenty-four AI lesson descriptions gain a verified, consecutive public next-lesson link and the complete course link. This closes navigation gaps beginning with episode 18 through episode 41. Episode 42 does not link to private episode 43. Existing chapters and useful learning details remain. Titles on the AI course were not changed.

Three ordered public learning paths were created and verified as channel homepage sections:

- HTML for Beginners | Build Your First Web Page — 20 lessons.
- CSS for Beginners | Style a Responsive Website — 16 lessons.
- JavaScript for Beginners | Variables to DOM Manipulation — 10 lessons.

The full web-development course, AI course, Agile course and Start Here playlist remain available. New playlists reuse existing videos; they do not create duplicate uploads. Existing homepage section order is retained, with topic sections appended.

## Verification and backups

The execution script checks the channel identity before writing, saves original metadata and a measurement baseline, rejects unexpected concurrent editorial changes and reads updates back from YouTube. It verifies playlist membership/order, homepage presence and every enumerated video's release status, including future releases. Local matching metadata files are synchronized with backups; publication receipts and video binaries are not edited. YouTube may automatically populate an omitted defaultAudioLanguage field after a snippet update; verification permits that server-added field while preserving any pre-existing language setting.

Backups and audit trail: youtube-live-before.json, youtube-change-plan.json, youtube-measurement-baseline.csv, youtube-application-state.json and optimization-local-backups/. The resumable implementation is optimize_youtube.py. Final success requires complete=true in the application-state file; a submission alone is not treated as verification.

## Next production and measurement

The source review still finds generic narration such as “Let's make it simple” and “Read the example from top to bottom.” Metadata cannot change the existing videos' opening or pacing. Next-Video-Briefs.md provides concrete demonstration-led openings for the five planned web projects: profile card, responsive navigation, counter, to-do list and publishing a website. These briefs are prepared, not rendered or uploaded.

Shorts description URLs are non-clickable. For an actual clickable next-video path on a Short, use YouTube Studio's Related video control with a relevant public lesson. That Studio control was not configured through this API workflow. Channel playlist sections provide an additional discoverable path.

Review after seven and fourteen days, on November 23 and November 30, using equal windows for comparable formats. These are manual review dates, not scheduled reminders. In Studio, export Shorts engaged views, stayed-to-watch, average watch duration, percentage viewed and subscribers gained. For long lessons, add impressions, CTR, watch time, opening retention and traffic sources. Record subscriber attribution rather than assuming overall channel growth came from an edited video.

Use the CSV baseline to track public count changes, but do not interpret lifetime view differences as causal lift. Compare the six coding tests with similar-length, similar-age lessons; the comparison is observational. If exposure is too low, mark the test inconclusive. Avoid repeating title changes daily or increasing upload frequency to compensate for weak results.

## Official guidance checked

Accurate, concise titles and measuring audience response: https://support.google.com/youtube/answer/12340300

Packaging, early hooks and retention: https://support.google.com/youtube/answer/16559650

Metadata changes work through changed viewer interactions, not the act of editing itself: https://support.google.com/youtube/answer/16559651

Clickable links and the Shorts description limitation: https://support.google.com/youtube/answer/13748639

## Live topic playlists

- [HTML for Beginners | Build Your First Web Page](https://www.youtube.com/playlist?list=PLPHe_O2eqMt4)
- [CSS for Beginners | Style a Responsive Website](https://www.youtube.com/playlist?list=PLWpjKZkR9a1k)
- [JavaScript for Beginners | Variables to DOM Manipulation](https://www.youtube.com/playlist?list=PLMSxG_d42tRs)
