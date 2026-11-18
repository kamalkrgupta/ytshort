# Build a JavaScript To-Do List: Add and Remove Tasks

9:16; 1080 × 1920; 30 fps; 60 seconds. Voice: en-US-GuyNeural, -15%.
Creative direction: midnight, mint and orange; large readable code; result first; working counter/list handlers; simple before/after transitions. No stock imagery.

## hook — 7.5s
Narration: Type a task, click Add, and put it in a list. Here is the basic idea.
Visuals/text: Type → Add → Remove
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## idea — 8.0s
Narration: Use an input, an Add button, and an unordered list. Connect the button to a click handler.
Visuals/text: An input becomes a new list item.
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## code — 8.5s
Narration: Read the input and trim extra spaces. If it is empty, stop before creating anything.
Visuals/text: const text = input.value.trim();
if (!text) return;
const item =
  document.createElement("li");
item.textContent = text;
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## result — 6.5s
Narration: Create a list item, set its text content, then append it to the list.
Visuals/text: const remove =
  document.createElement("button");
remove.textContent = "Remove";
remove.onclick = () => item.remove();
item.append(remove);
list.append(item);
input.value = "";
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## tip — 8.0s
Narration: Clear the input so the next task is easy to enter. Add a remove button to each item.
Visuals/text: Clear the input after adding the task.
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## caution — 8.5s
Narration: When Remove is clicked, remove that item. Text content displays user input as plain text.
Visuals/text: Reject empty input; use textContent.
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## try — 8.0s
Narration: Try adding one task and removing it. This version does not save tasks after a refresh.
Visuals/text: Add a task and a remove button.
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

## close — 5.0s
Narration: Subscribe to Tech at sixty for more beginner projects.
Visuals/text: Subscribe for practical beginner coding projects.
Motion: Framer Motion reveals text/cards after 0.1s; GSAP draws the rule and runs the demo; actions begin 0.7s after the demo mounts. Transition: fade.

