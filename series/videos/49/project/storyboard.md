# Build a JavaScript Counter: Click to Add One

9:16; 1080 × 1920; 30 fps; 60 seconds. Voice: en-US-GuyNeural, -15%.
Creative direction: midnight, mint and orange; large readable code; result first; working counter/list handlers; simple before/after transitions. No stock imagery.

## hook — 7.0s
Narration: One click, one number higher. Build this counter with JavaScript.
Visuals/text: Click +1 and watch the number
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## idea — 8.0s
Narration: The page needs a button and an output element. Start the displayed number at zero.
Visuals/text: State is the value; textContent shows it.
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## code — 7.5s
Narration: Select both elements after the page exists, and store zero in a variable called count.
Visuals/text: const button =
  document.querySelector("button");
const output =
  document.querySelector("output");
let count = 0;
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## result — 9.0s
Narration: Add a click listener. Each click increases count, then text content updates the number on screen.
Visuals/text: button.addEventListener("click", () => {
  count++;
  output.textContent = count;
});
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## tip — 9.0s
Narration: Watch the value change from zero to one, then two. The variable and display stay in sync.
Visuals/text: Update the screen after changing count.
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## caution — 8.0s
Narration: Changing the variable alone will not update the page. You must update the output too.
Visuals/text: Select elements after the HTML exists.
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## try — 6.5s
Narration: Your challenge: add a reset button that sets both the value and display back to zero.
Visuals/text: Add a reset button that returns to zero.
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## close — 5.0s
Narration: Subscribe to Tech at sixty for the next coding project.
Visuals/text: Subscribe for practical beginner coding projects.
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

