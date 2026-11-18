# Writing the storyboard

The storyboard is the whole video on paper. Write it as `storyboard.md` before
any code. Someone who reads only this file should be able to picture every
second of the video.

## Shape of a 60-second video

Use 6 to 9 scenes. Fewer and each one overstays; more and nothing lands.

| Part | Time | Job |
|------|------|-----|
| Hook | 0 to 5s | A question, a surprising number or a bold claim. The viewer decides here whether to keep watching, so no title card and no logo intro. |
| Setup | 5 to 12s | Why it matters or what the problem is. |
| Core | 12 to 48s | 3 to 5 scenes, one idea each. Change the visual form from scene to scene: a number, a comparison, a diagram, a list, a timeline. |
| Payoff | 48 to 55s | The takeaway in one sentence. |
| Close | 55 to 60s | Call to action, source line or sign-off. Let the last frame rest for a full second so the video doesn't end mid-motion. |

Scenes run 4 to 10 seconds. Durations are whole or half seconds and total
exactly 60. Add them up in the file; the recorder checks the sum too.

## Writing the narration

Each scene has one narration line, spoken by the voiceover. The narration tells
the story; the screen shows it.

- A minute holds about 130 to 145 spoken words in English once pauses between
  scenes are counted. Budget about 2.3 words per second of scene time, minus one
  second per scene for the lead-in and the breath before the cut. A 6-second
  scene carries about 11 words.
- Write for the ear: short sentences, contractions, one clause at a time. Read
  each line out in your head; if it needs a comma-laden second breath, split it
  or cut it.
- Spell things the way they should be said. Write "dot com" for ".com", spell
  out symbols and unusual abbreviations, and write numbers as you want them
  read ("a hundred milliseconds", "twenty twenty-six").
- Write the narration in the language and script of the chosen voice.
- The word counts are estimates. Step 4 of the skill generates the audio and
  reports the real length of every line, and the durations follow from that.

## Writing for the screen

With a voiceover, on-screen text is the highlight reel of the narration: the key
phrase, the number, the name. It should be readable at a glance while the voice
carries the sentence. For a silent video the text carries everything, so use
the upper end of these budgets.

- Budget about 1 word on screen per second of scene time with voiceover (2 for
  a silent video), and never more than about 14 words on screen at once.
- Don't put the narration on screen verbatim; reading and listening to the same
  sentence at different speeds is tiring.
- One idea per scene. If a scene needs "and", it is two scenes.
- Prefer concrete things to adjectives: "8 of 10 passwords are reused" beats
  "passwords are often insecure".
- Write the exact copy in the storyboard. Placeholder text ("headline about X")
  only postpones the decision into the code.
- Only state facts you are sure of. Check figures and dates if a search tool is
  available; otherwise phrase them at the precision you actually know.

## Keeping it alive

A scene that animates in over one second and then sits still for six reads as a
slide. Plan a beat (something entering, changing, counting or moving) every 2 to
3 seconds, and give each scene one main event that the eye follows. List the
beats with their times in the storyboard; they become delays and timeline
positions in the code. Tie each beat to the words it illustrates: the voice
starts about 0.35s into the scene and moves at roughly 2.5 words per second, so
a phrase that begins at the eighth word lands near 3.5s.

Pick one visual motif from the topic's own world and carry it through the scenes
(a coffee video might build everything from rings and steam; a cybersecurity one
from locks and terminal text). It makes seven separate screens feel like one video.

## Template

```markdown
# <Video title>

Ratio: 9:16 (1080 x 1920) | Length: 60s | fps: 30

## Direction
- Audience: who is watching and where
- Tone: three adjectives
- Voice: Edge TTS voice name and language (e.g. en-IN-NeerjaNeural)
- Palette: background, surface, ink, accent (hex values)
- Type: display face / body face
- Motif: the recurring visual idea

## Scenes

| # | id | Time | Dur | One-line summary |
|---|----|------|-----|------------------|
| 1 | hook | 0:00 to 0:05 | 5s | ... |
| ... |
| | | **Total** | **60s** | |

### 1. hook (5s) | transition: cut
- Purpose: what the viewer should think or feel
- Narration: "The sentence the voice says." (word count)
- Text: "Exact words on screen" (word count)
- Visuals: layout and elements, where they sit in this ratio
- Animation:
  - 0.0s headline words rise in, staggered (GSAP)
  - 1.5s number counts 0 to 73 (react-spring)
  - 3.5s underline draws (GSAP, SVG)
- Background: ambient motion, if any (CSS keyframes)

### 2. ...
```

## Layout by ratio

- 16:9: room for side-by-side layouts (text left, visual right). Large type can
  run wide; keep lines under about 30 characters at display size.
- 9:16: stack vertically. Headline in the upper third, visual in the middle, and
  keep the bottom fifth free of text because platform captions and buttons cover
  it. Display lines break after 2 or 3 words.
- 1:1: one centred idea per scene. Least room of the three, so cut copy first.
