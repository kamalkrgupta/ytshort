# Responsive Navbar with CSS Flexbox: Make Links Wrap

9:16; 1080 × 1920; 30 fps; 60 seconds. Voice: en-US-GuyNeural, -15%.
Creative direction: midnight, mint and orange; large readable code; result first; working counter/list handlers; simple before/after transitions. No stock imagery.

## hook — 6.0s
Narration: These navigation links need to work on a phone as well as a desktop.
Visuals/text: Wide screen → narrow screen
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## idea — 8.0s
Narration: Put real links inside a navigation element. Each link needs a destination.
Visuals/text: Keep every link visible and usable.
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## code — 7.5s
Narration: Set display to flex to arrange the links. Gap adds space between them.
Visuals/text: <nav>
  <a href="/">Home</a>
  <a href="about.html">About</a>
  <a href="contact.html">Contact</a>
</nav>
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## result — 9.0s
Narration: Now add flex wrap. When the container gets narrower, links move onto another line.
Visuals/text: nav {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## tip — 6.5s
Narration: The links stay visible instead of being squeezed into unreadable text.
Visuals/text: flex-wrap lets links flow onto another line.
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## caution — 9.5s
Narration: This is a wrapping menu. A separate collapsible menu would need an accessible toggle and keyboard support.
Visuals/text: This example wraps; it is not a hamburger menu.
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## try — 8.0s
Narration: Try three links, then shrink the available width. Can you still use every link?
Visuals/text: Try three links at a narrow width.
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## close — 5.5s
Narration: Subscribe to Tech at sixty for practical web projects.
Visuals/text: Subscribe for practical beginner coding projects.
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

