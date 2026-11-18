# Building scenes

## Contents
- Anatomy of a scene
- Sizing and safe areas
- Which library for what
- Rules that keep animations recordable
- Recipes
- Adding another library

## Anatomy of a scene

```jsx
// src/scenes/Hook.jsx
import React, { useRef } from 'react';
import gsap from 'gsap';
import { useGSAP } from '@gsap/react';
import { SplitText } from '../kit/SplitText.jsx';

export default function Hook({ duration }) {      // duration in seconds, from scenes/index.js
  const root = useRef(null);
  useGSAP(() => {
    gsap.timeline()
      .from('.split-word', { yPercent: 120, opacity: 0, stagger: 0.08, duration: 0.7, ease: 'power3.out' }, 0.2)
      .from('.sub', { opacity: 0, y: 30, duration: 0.6 }, 1.6);
  }, { scope: root });

  return (
    <div className="scene" ref={root}>
      <div className="safe">
        <SplitText className="display" text="You forget half of this by tomorrow" />
        <p className="body sub">Unless you do one thing.</p>
      </div>
    </div>
  );
}
```

```js
// src/scenes/index.js
export const scenes = [
  { id: 'hook', duration: 5, transition: 'cut', component: Hook },
  { id: 'problem', duration: 7, transition: 'slideUp', component: Problem },
  // ... total 60
];
```

The player mounts a scene at its start time and unmounts it at its end. Time
zero inside a scene is the moment it appears. `transition` is how the scene
enters (`cut`, `fade`, `slideLeft`, `slideUp`, `zoom`, `wipe`, defined in
`src/engine/transitions.js`; add more there). The outgoing scene exits
underneath while the new one enters, so transitions don't add time. Each scene
frame has an opaque background (`--bg`); set a different background on the
scene's root element when a scene needs its own.

## Sizing and safe areas

The stage is a fixed pixel canvas (1920x1080, 1080x1920 or 1080x1080) scaled
down only in preview. CSS variables on the stage:

- `--u`: 1% of the short side (10.8px in every preset). Write font sizes and
  spacing as `calc(var(--u) * n)` so they hold up if the ratio changes.
- `--w`, `--h`: canvas size in px.
- `--safe-top|right|bottom|left`: margins that keep text clear of platform UI.
  The `.safe` class applies them; 9:16 reserves a large bottom margin.

Helper classes in `theme.css`: `.scene` (fills the frame), `.safe` (padded flex
column, centred), `.display` (11u), `.title` (7u), `.body` (3.6u). Readable
minimum for anything that matters is about 3u; phones are small.

Type size guide: hook headlines 9u to 14u, scene titles 6u to 8u, supporting
lines 3.5u to 4.5u, hero numbers 18u to 30u.

## Which library for what

| Job | Reach for | Why |
|-----|-----------|-----|
| Elements entering, leaving, staggered lists, layout changes | Framer Motion (`motion.div`, variants, `AnimatePresence`, `layout`) | Declarative, lives next to the JSX |
| A scene with many timed steps, word-by-word text, SVG line drawing, morphing colours | GSAP timeline via `useGSAP` | One timeline with positions in seconds mirrors the storyboard's beat list |
| Counting numbers, springy physical motion, trails | react-spring (`useSpring`, `useTrail`, `kit/Counter`) | Interpolates values straight into text |
| Endless ambient motion: drifting gradients, pulsing glows, rotating shapes | CSS `@keyframes` | Free, no JS |

Mix them across the video and inside a scene when it helps, but give each
element one owner: two libraries animating the same property of the same
element fight each other.

## Rules that keep animations recordable

The recorder replaces the page's clock (`performance.now`, `Date`,
`requestAnimationFrame`, timers) and scrubs CSS animations itself. Anything
driven by those is captured frame-exact. A few things are not:

- Start everything on mount. Hover, click, scroll, `whileInView`,
  `ScrollTrigger` and viewport observers never fire in a recording.
- Don't call `element.animate()` (Web Animations API) or Motion's `animate()`
  "mini" import directly; it is disabled during capture. `motion.*` components
  and `useAnimate` from `framer-motion` fall back to their JS driver and work.
- No `<video>` or `<audio>` elements and no GIFs; they keep their own time. Sound
  never comes from the page: the voiceover is mixed in by the recorder from
  `voice/`, and music is added at render time with `--audio`.
- Bundle every asset. Import images and SVGs from `src/`, fonts from
  `@fontsource`. Nothing should load from the network while recording.
- Keep randomness stable: compute random positions once (`useMemo` with a seeded
  generator or a fixed array), not on every render.
- Finish inside the scene. An animation whose delay plus duration exceeds the
  scene's `duration` gets cut off; use the `duration` prop to time anything that
  should happen near the end.
- Canvas and WebGL work if they draw from `requestAnimationFrame`.

## Recipes

Staggered entrance (Framer Motion):

```jsx
import { motion } from 'framer-motion';
import { stagger, rise } from '../kit/motion.js';

<motion.ul variants={stagger(0.15, 0.4)} initial="hidden" animate="show">
  {items.map((t) => <motion.li key={t} variants={rise}>{t}</motion.li>)}
</motion.ul>
```

Reveal items across a long scene (Framer Motion delays):

```jsx
<motion.div initial={{ opacity: 0, x: -60 }} animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.5 + i * 2, duration: 0.6 }} />
```

Swap content mid-scene (state on a timer plus `AnimatePresence`):

```jsx
const [step, setStep] = useState(0);
useEffect(() => { const id = setTimeout(() => setStep(1), 3000); return () => clearTimeout(id); }, []);
<AnimatePresence mode="wait">
  <motion.p key={step} initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -30 }}>
    {lines[step]}
  </motion.p>
</AnimatePresence>
```

Timeline choreography and SVG line drawing (GSAP):

```jsx
useGSAP(() => {
  gsap.timeline({ defaults: { ease: 'power3.out' } })
    .from('.card', { y: 80, opacity: 0, stagger: 0.2, duration: 0.7 }, 0.3)
    .fromTo('.line', { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 1.5 }, 1.5)  // path needs pathLength="1" strokeDasharray="1"
    .to('.card', { scale: 0.9, opacity: 0.4, duration: 0.5 }, duration - 1.2);              // beat near the end
}, { scope: root });
```

Counting number (react-spring):

```jsx
import { Counter } from '../kit/Counter.jsx';
<Counter className="display" to={73} suffix="%" delay={800} duration={1800} />
```

Ambient loop (CSS):

```jsx
<style>{`@keyframes drift { to { transform: translate(8%, 6%) rotate(20deg); } }
.blob { animation: drift 9s ease-in-out infinite alternate; }`}</style>
```

Bar or ring that fills (any library): animate `scaleX`/`scaleY` with
`transformOrigin`, or an SVG circle's `strokeDashoffset` with `pathLength="1"`.

Icons: `lucide-react` is installed (`import { Moon } from 'lucide-react'`,
size with the `size` prop in px, e.g. `size={160}`). For anything it lacks,
draw inline SVG.

## Adding another library

Lottie (`lottie-react`), anime.js, Three.js and similar are fine when they
advance from `requestAnimationFrame` or timers. Install with npm, use it in a
scene, and confirm with `node tools/record.mjs --at <t1>,<t2>` that two
different times produce two different frames.
