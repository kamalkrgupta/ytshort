# TECH AT 60: reach and engagement experiment

Audit date: November 3, 2026 (IST). Channel: https://www.youtube.com/@Techat60

## Observed baseline

The live channel reports 16 subscribers, 1,224 lifetime views and 57 public videos. The October 27 audit reported 14 subscribers and 637 views. Neither the increase nor this experiment establishes that the earlier SEO edits caused growth.

Deduplicated API results contain 56 public video records: 29 web lessons (1,021 views, median 30), 14 AI lessons (75 views, median 4), 12 Agile lessons (99 views, median 6.5), and one AI awareness Short (5 views). The channel total and enumerated public records differ; do not silently treat either count as the other. Video views sum to 1,200 and may differ from channel totals due to coverage and update timing. Older videos have had longer to accumulate views. These totals are directional observations, not evidence that changing topics alone increases reach.

Only three comments appear across these public records. Likes and comments are visible; impressions, CTR, engaged views, stayed-to-watch, retention, traffic sources and subscriber attribution are unavailable under the current OAuth scopes. Total Shorts views must not be treated as engaged views.

## Bounded live experiment

Six web lessons receive clearer titles, a specific opening description, one answerable topic question and a link to the next public lesson: HTML headings, HTML forms, CSS box model, CSS backgrounds, CSS classes vs IDs, and CSS display. Existing useful exercises and source links remain. The AI awareness Short receives unrelated-tag cleanup. The web course moves to the first homepage playlist section.

Keep HTML introduction, HTML links and HTML buttons unchanged as descriptive reference videos. These are not randomized controls and have different ages and topics. Do not infer title lift from total lifetime views. The original metadata is in experiment-backup.json; local originals are in local-backups. Check applied.json for the verified execution state.

## Next production brief

The sampled narration opens with “[topic]. Let’s make it simple,” followed by generic instructions such as “Read the example from top to bottom.” Replace these in future productions with the actual problem, output and demonstration. Existing rendered media has not been changed by this metadata experiment.

For the next three newly produced web Shorts, use these concepts without interrupting the current release schedule:

1. Box model: open on two boxes with identical content and different padding. Say “Why is this box bigger? Padding adds space inside the border.” Demonstrate the exact CSS, then ask “Which adds space outside: padding or margin?”
2. Class vs ID: open on three cards receiving one class rule. Say “Style three cards with one CSS rule. Use a class.” Show the selector and result, then ask viewers which selector they would use for repeated cards.
3. Display: begin with labels stacking, then flowing inline. Say “These labels stack because they are blocks. Watch what inline-block changes.” Show the edit and result; invite viewers to try width on an inline versus inline-block label.

Show the result immediately; keep code readable on a phone; narrate each visible change. Remove generic filler and repeated requests to like/share/subscribe. End with one question or exercise tied to the demonstrated result. Match the title and opening frame to what the video actually delivers. Re-render and inspect timing, voice synchronization and output before any future upload; shorter scripts alone can leave empty time in the fixed-duration renderer.

For future long tutorials, state the finished task first, demonstrate it early, then explain it. Keep episode numbers in the description when they obscure the title's useful promise. Prepare a distinct, readable thumbnail for each long video once custom-thumbnail upload eligibility is verified in Studio.

## Measurement: November 10 and November 17, 2026

These are recommended manual review dates, not installed reminders or automated jobs.

Use equal seven-day windows before and after the edits, and compare Shorts separately from five- and ten-minute tutorials. Export per-video Studio data, including impressions and CTR for eligible surfaces, traffic sources, engaged views, stayed-to-watch, average view duration, average percentage viewed, retention and subscribers gained. Record comments and substantive exercise answers. Check sample size before interpreting percentages; one response on a few views is unstable.

For long videos, weak CTR relative to similar channel videos with enough impressions suggests a title/thumbnail experiment. Early retention drops suggest the opening fails to deliver the promise. For Shorts, low stayed-to-watch suggests testing the first frame and opening; strong starts with later drops suggest improving pacing and payoff. Compare against the channel's own similar-length videos rather than a universal benchmark.

If a test receives too little exposure, mark it inconclusive. Keep clear, accurate packaging and test a new creative treatment in a future video. Avoid daily metadata churn. Continue a format only when repeated comparable uploads improve viewing and meaningful engagement. Do not increase upload volume based solely on low reach.

## Official guidance

YouTube describes Shorts discovery in terms of viewer personalization, performance and satisfaction signals: https://support.google.com/youtube/answer/11914225?co=YOUTUBE._YTVideoType%3Dshorts&hl=en

YouTube's Shorts analytics guidance covers feed exposure, viewed versus swiped away, traffic sources and retention: https://support.google.com/youtube/answer/12942217?co=YOUTUBE._YTVideoType%3Dshorts&hl=en

No title, tag or schedule change guarantees views or recommendations.
