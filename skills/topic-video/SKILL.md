---
name: topic-video
description: Creates a finished 60-second animated explainer video (MP4) with voiceover about any topic, by writing a scene-by-scene storyboard with narration, generating the voice with Edge TTS, building each scene as an animated React screen (Framer Motion, GSAP, react-spring), recording it frame by frame in headless Chrome and encoding it to MP4 with the narration mixed in, followed by uploading to a configured YouTube channel when enabled by the user. Use this skill whenever the user asks for a video, short, reel, explainer, narrated clip, animated clip, motion graphic, promo or "1 minute video" on a topic, wants a topic "turned into a video", wants a voiceover added to such a video, or asks for an MP4 for YouTube, Shorts, Reels, TikTok, LinkedIn or WhatsApp, even if they don't mention React, animation or narration. Not for editing existing footage or for videos that need filmed or AI-generated footage.
metadata:
  compatibility: Needs a shell with Node.js 18+, npm, a Chrome/Chromium binary and ffmpeg (Claude Code, Cowork, or a chat sandbox with code execution). Voiceover also needs Python with the edge-tts package and internet access; without them the video can still be rendered silent.
---

# Topic video

Turn a topic into a one-minute animated MP4 with a spoken voiceover. The video
is a small React app in which every scene is a full-screen animated component.
Edge TTS speaks one narration line per scene; a recorder plays the app in
headless Chrome on a virtual clock, screenshots every frame, and ffmpeg encodes
the frames and mixes each voice clip in at the start of its scene.

The pipeline is fixed, the creative work is not. Scaffolding, the player, the
recorder and the encoder are bundled and tested, so spend effort where it shows:
the storyboard, the narration, and the look and motion of each scene.

## Workflow

1. Ask for the aspect ratio
2. Write the storyboard (scene details and narration)
3. Scaffold the React project
4. Generate the voiceover and lock the scene durations
5. Build each scene
6. Check stills, fix, repeat
7. Record and encode the MP4
8. Verify the video
9. Upload to the configured YouTube channel and deliver

### 1. Ask for the aspect ratio

The ratio decides every layout, so settle it before designing anything. If the
user has not already stated it, ask exactly one question and stop until they
answer. Use a tappable-options tool if one is available (for example
`ask_user_input`), otherwise ask in plain text:

> Which screen ratio should the video use?
> - **16:9** landscape (YouTube, presentations, web)
> - **9:16** vertical (Shorts, Reels, TikTok, WhatsApp status)
> - **1:1** square (Instagram and LinkedIn feed)

Don't guess a ratio from the platform unless the user named one that allows only
one answer, and don't pile on other questions. Reasonable defaults cover
everything else (audience, tone, palette, voice); state the ones you chose when
you deliver, so the user can redirect.

Voiceover is on by default, in the language the user wrote the request in
unless they name another. Leave it out only if the user asks for a silent video.

| Ratio | Canvas | fps |
|-------|--------|-----|
| 16:9 | 1920 x 1080 | 30 |
| 9:16 | 1080 x 1920 | 30 |
| 1:1 | 1080 x 1080 | 30 |

### 2. Write the storyboard

Read `references/storyboard.md`, then write `storyboard.md` (it goes in the
project root once the project exists). It holds a short creative direction
(audience, tone, palette, fonts, a visual motif tied to the topic) and one block
per scene: id, duration, purpose, the narration line that is spoken, exact
on-screen text, visuals, animation beats with timings and library, and the
transition in.

Do this before writing any React. A scene that is vague on paper turns into a
static slide with a fade on it, and timing mistakes are cheap to fix in a table
and expensive to fix in code. Durations must add up to exactly 60 seconds; at
this stage they are estimates, and step 4 replaces them with measured ones.

If facts, figures or dates matter to the topic and a search tool is available,
verify them now. A wrong number rendered into a video is costly to correct.

Show the user the storyboard as a compact table in your reply, then keep going
in the same turn. Only pause for approval if they asked to review it first.

### 3. Scaffold the project

```bash
node <skill-dir>/scripts/create-project.mjs <project-dir> --ratio <16:9|9:16|1:1> --title "<video title>"
```

This copies `assets/template`, writes `video.config.json`, runs `npm install`
and reports whether Chrome and ffmpeg were found. If one is missing:

- Chrome: `npx puppeteer browsers install chrome` inside the project, or set `CHROME_PATH`
- ffmpeg: install it with the system package manager, or `npm i -D ffmpeg-static` inside the project

Project layout:

```
video.config.json      title, ratio, fps, duration (60)
storyboard.md          the plan from step 2
narration.json         voice settings and one spoken line per scene id
voice/                 generated clips and manifest.json (made by `npm run voice`)
src/theme.css          palette and font tokens, shared helper classes
src/scenes/index.js    scene order, durations, transitions   <- the timeline
src/scenes/*.jsx       one component per scene               <- most of the work
src/kit/               SplitText, Counter, Framer Motion presets
src/engine/            player, transitions, ratio presets (rarely needs edits)
tools/voiceover.mjs    Edge TTS clips, measuring, fit table
tools/record.mjs       recorder, encoder and audio mix
```

The template ships three `Example*.jsx` scenes, one per animation library. Read
them as recipes, then replace them and delete the files.

### 4. Generate the voiceover

Do this before building scenes: how long each line takes to say decides how
long each scene must be, and animation beats are timed against the voice.

Put the narration from the storyboard into `narration.json`, keyed by the scene
ids you will use in `src/scenes/index.js`:

```json
{
  "voice": "en-IN-NeerjaNeural",
  "rate": "+0%",
  "pitch": "+0Hz",
  "leadIn": 0.35,
  "scenes": {
    "hook": "You type a name. Your computer has no idea where it is.",
    "numbers": "Computers find each other by number, called an IP address."
  }
}
```

`leadIn` is the pause between a scene appearing and its voice starting. A scene
with no entry stays silent.

Pick a voice that matches the language and audience:

| Language | Voices |
|----------|--------|
| English (US) | `en-US-AriaNeural` (f), `en-US-GuyNeural` (m) |
| English (UK) | `en-GB-SoniaNeural` (f), `en-GB-RyanNeural` (m) |
| English (India) | `en-IN-NeerjaNeural` (f), `en-IN-PrabhatNeural` (m) |
| Hindi | `hi-IN-SwaraNeural` (f), `hi-IN-MadhurNeural` (m) |

For anything else, list what the service offers: `node tools/voiceover.mjs --voices <locale or name>`
(for example `--voices ta-IN`). The voice only pronounces its own language well,
so the narration text must be written in that language and script.

Then generate:

```bash
pip install edge-tts        # once; pipx or uvx also work
npm run voice
```

This writes `voice/<scene-id>.wav` (silence trimmed) and prints a table: each
clip's length, the minimum duration its scene needs, and the total. Now settle
the timeline:

- Set each scene's `duration` in the storyboard (and later `src/scenes/index.js`)
  to at least its "needs" value, then hand out the remaining seconds where the
  visuals need room, keeping the total at 60.
- If the total needed exceeds 60, shorten the wordiest lines first. A small
  `rate` increase (`"+5%"` to `"+10%"`) is fine; beyond that it sounds rushed.
- Re-run `npm run voice` after any edit. Only changed lines are regenerated.
  Once the scenes exist, the same command checks every clip against its scene
  and exits non-zero on a misfit.

If Edge TTS cannot be reached (no internet, the service refuses, `edge-tts`
cannot be installed), say so plainly and offer the two ways forward: render
silent now (`--no-voice`), or let the user drop their own recordings into
`voice/` named `<scene-id>.wav` or `.mp3` and run `node tools/voiceover.mjs --measure`.
Don't quietly ship a silent video when a voiceover was expected.

### 5. Build each scene

Read `references/animation.md` before writing scenes. It covers which library
suits which job, sizing and safe areas for each ratio, and the handful of rules
that keep animations recordable.

- Set the palette and fonts in `src/theme.css` first, so every scene shares one
  look. Install fonts from npm (`npm i @fontsource-variable/<family>`) and import
  them in `src/main.jsx`; the recorder runs offline-safe and must not depend on a CDN.
- Create one file per storyboard scene in `src/scenes/` and register them in
  order in `src/scenes/index.js` with `id`, `duration` and `transition`.
- A scene's animations start when it mounts and are spaced with delays or
  timeline positions, so each scene is self-contained and can be previewed alone.
- Use more than one library across the video, each for what it does best:
  Framer Motion for entrances, exits and layout; GSAP timelines for multi-step
  choreography, text and SVG; react-spring for counting numbers and physical
  motion; CSS keyframes for ambient loops.
- Use the real copy from the storyboard. Keep text inside `.safe`; backgrounds
  can bleed to the edges.
- Time the beats to the voice. Speech starts `leadIn` seconds into the scene, so
  the thing being named should appear as it is said, not seconds before or after.
  On-screen text supports the narration with key words and numbers; it does not
  transcribe it.
- For non-Latin scripts (Hindi and others) install a font that covers the script,
  for example `@fontsource-variable/noto-sans-devanagari`, or the text renders as boxes.

If the `frontend-design` skill is available, its guidance on palette, type and
restraint applies to these scenes too.

### 6. Check stills, fix, repeat

```bash
npm run stills
```

This builds the app and writes one PNG per scene (taken 85% of the way through,
when the layout is fully built) to `out/stills/`, plus `out/stills/contact.png`
with all of them in one image. Look at the contact sheet, then open individual
stills when something needs a closer look. You cannot watch the video, so stills
are your eyes. Check for:

- text clipped, overflowing or outside the safe area
- elements overlapping, or type too small to read on a phone
- a scene that is nearly empty (an animation failed, or a delay runs past the scene's end)
- weak contrast, and scenes that look inconsistent with each other
- page errors or voiceover warnings printed at the end of the command

Useful variations:

```bash
node tools/record.mjs --at 0.4,7.9,31     # stills at exact seconds (after a build)
node tools/record.mjs --from 12 --to 18 --out out/clip.mp4   # render one slice
```

Check at least one scene mid-animation with `--at`, to confirm things are
actually moving and not just appearing. Fix what you find and re-run until the
stills look right. Skipping this step is the usual reason a video ships with a
headline cut off.

For a live preview on a machine with a browser: `npm run dev`, then open the URL.
`?scene=3` starts at the third scene and `?t=25` starts at 25 seconds.

### 7. Record and encode

```bash
npm run render
```

This builds the app, opens it in headless Chrome, steps a virtual clock one
frame at a time (1800 frames), screenshots each frame and pipes them to ffmpeg.
If `voice/manifest.json` exists, each clip is placed at its scene's start plus
`leadIn`, the voice track is loudness-normalised, and it is muxed in as AAC.
Output: `out/<title-slug>.mp4`, H.264, yuv420p, 30 fps, faststart, which plays
on phones, browsers and editors alike.

Why frame stepping and not a real-time screen recording: real-time capture drops
or repeats frames whenever the machine is busy, and headless Chrome is always
busy while it is being recorded. With a virtual clock each frame takes as long
as it needs and the result is perfectly smooth and repeatable.

The render takes roughly 2 to 6 minutes depending on the machine and the ratio.
If the shell enforces a command timeout, or ends background jobs when a command
returns, start it fully detached and poll the log until it prints `Done`:

```bash
mkdir -p out && setsid nohup npm run render > out/render.log 2>&1 < /dev/null &
tail -n 3 out/render.log        # repeat until the "Done in ..." and "ffprobe:" lines appear
```

(`setsid` is Linux-only; on macOS plain `nohup ... &` is enough.)

The recorder refuses to render when scene durations don't add up to 60 seconds,
when a voice clip is longer than its scene, or when a narration line was edited
after its clip was generated. It prints what to fix.

Options: `--audio <file>` adds music (looped, faded out at the end, and kept
quietly under the voice when there is one; adjust with `--music-volume 0.2`),
`--no-voice` renders silent, `--out <file>` changes the output path, `--crf <n>`
sets quality (default 18, lower is better and larger), `--png` uses lossless
frames (slower).

### 8. Verify and deliver

The recorder ends with an `ffprobe` line. Confirm it shows the right resolution
for the ratio, 30 fps, 1800 frames, 60.00s and `audio: aac` (or `audio: none`
for a deliberately silent video). Then hand over the MP4:

- In a chat sandbox, copy it to the user-visible outputs folder and present it
  with the file-presenting tool.
- In Claude Code or Cowork, give the path to `out/<slug>.mp4`.

Keep the delivery message short: the file, the ratio and resolution, the voice
used, and a one-line note on the creative choices made by default. You cannot
listen to the result, so say that the narration timing was checked by clip
length and not by ear, and invite the user to flag any line that sounds off.
Offer changes scene by scene, since editing a scene and re-rendering is cheap.

### 9. Upload to YouTube

For a topic list and posting cadence, also read [references/batch-posting.md](references/batch-posting.md).

After the final MP4 passes step 8, follow [references/youtube-publishing.md](references/youtube-publishing.md). Prepare title, description, and relevant tags, then upload automatically when the user has enabled this workflow and the channel, visibility, audience setting, and publishing connection are configured. Respect an explicit local-only or no-upload request. Reuse existing authorization; do not ask for confirmation on every video. If setup is incomplete, finish the MP4 and upload metadata, explain what is missing, and report upload as pending. Never report an upload or public release without a confirmed video ID and actual status.

## Revisions

Scenes are independent, so a change request usually touches one file. Edit the
scene, check it with `node tools/record.mjs --at <seconds>` after `npm run build`,
then `npm run render` again. To change what is said, edit the line in
`narration.json`, run `npm run voice`, fix any scene it reports as too short,
and render. To change the voice, edit `voice` and run `npm run voice` (every
clip is regenerated, so re-check the fit table). To change the ratio, edit `ratio` in
`video.config.json`, re-run stills and adjust the layouts that break; sizes
written in `--u` units mostly survive the switch, compositions often need rework.

## Troubleshooting

| Symptom | Cause and fix |
|---------|---------------|
| "The app never became ready" | A runtime error in a scene. The page errors are printed; fix and rebuild. |
| A scene is blank in stills | Animation still waiting on a delay longer than the scene, or it relies on hover, scroll or `whileInView`, which never fire. Start it on mount. |
| An element never animates in the MP4 but does in `npm run dev` | It uses `element.animate()` or a `<video>`, which the virtual clock can't step. Use Framer Motion, GSAP, react-spring or CSS keyframes. |
| Fonts differ between preview and render | A font loaded from a CDN. Install it from `@fontsource` and import it. |
| Render is very slow | Large `filter: blur()` or `backdrop-filter` areas animated every frame. Reduce their size or bake them into a gradient. |
| Duration error at render | Fix the `duration` values in `src/scenes/index.js` to total 60. |
| "edge-tts not found" | `pip install edge-tts` (add `--break-system-packages` or use `pipx`/`uvx` on managed Pythons), or set `EDGE_TTS` to the command. |
| "Edge TTS failed for scene ..." | No internet, a mistyped voice name, or the service is briefly refusing. Check with `--voices`, retry after a minute; see step 4 for the fallbacks. |
| Voice cut off or overlapping the next scene | The scene is shorter than its clip. `npm run voice` shows by how much; lengthen the scene or shorten the line. |
| A word is mispronounced | Respell it phonetically in `narration.json` only ("DNS" as "D N S", "nginx" as "engine x"); the on-screen text keeps the correct spelling. |
| Long silence at the end of a scene | The fit table flags it. Move seconds to a tighter scene or add a sentence. |
