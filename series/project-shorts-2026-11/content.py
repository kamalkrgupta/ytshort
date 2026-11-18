"""Original scripts and visible examples for the five remaining project lessons."""
DATA={
47:dict(title='Build a Profile Card with HTML and CSS',shortTitle='Your first\nprofile card',hook='Plain text → profile card',idea='HTML adds structure. CSS adds style.',rule='Use a class to style the card.',tip='Padding adds space inside the card.',caution='Keep text readable against the background.',exercise='Add your name, bio and a useful link.',closing='What will your card say?',code='<article class="card">\n  <h2>Alex</h2>\n  <p>Learning to code</p>\n  <a href="about.html">About me</a>\n</article>',code2='.card {\n  padding: 24px;\n  border: 2px solid teal;\n  border-radius: 20px;\n}',lines=[
'Build this profile card with a name, a short bio, and one useful link.',
'Use an article for the card, a heading for the name, and a paragraph for the introduction.',
'Give the article a class called card. The same class connects it to your style rule.',
'Add padding for breathing room. A border and rounded corners turn the content into a card.',
'Keep the text readable against your background. Simple colors work well.',
'If you add a portrait, write alternative text that describes its purpose.',
'Now replace Alex with your name, change the bio, and add your own link.',
'Subscribe to Tech at sixty for more small coding projects.'
]),
48:dict(title='Responsive Navbar with CSS Flexbox: Make Links Wrap',shortTitle='A menu that\nfits your screen',hook='Wide screen → narrow screen',idea='Keep every link visible and usable.',rule='Flexbox arranges the navigation links.',tip='flex-wrap lets links flow onto another line.',caution='This example wraps; it is not a hamburger menu.',exercise='Try three links at a narrow width.',closing='Can you still use every link?',code='<nav>\n  <a href="/">Home</a>\n  <a href="about.html">About</a>\n  <a href="contact.html">Contact</a>\n</nav>',code2='nav {\n  display: flex;\n  flex-wrap: wrap;\n  gap: 16px;\n}',lines=[
'These navigation links need to work on a phone as well as a desktop.',
'Put real links inside a navigation element. Each link needs a destination.',
'Set display to flex to arrange the links. Gap adds space between them.',
'Now add flex wrap. When the container gets narrower, links move onto another line.',
'The links stay visible instead of being squeezed into unreadable text.',
'This is a wrapping menu. A separate collapsible menu would need an accessible toggle and keyboard support.',
'Try three links, then shrink the available width. Can you still use every link?',
'Subscribe to Tech at sixty for practical web projects.'
]),
49:dict(title='Build a JavaScript Counter: Click to Add One',shortTitle='One click.\nOne number higher.',hook='Click +1 and watch the number',idea='State is the value; textContent shows it.',rule='Listen for a click, then update the value.',tip='Update the screen after changing count.',caution='Select elements after the HTML exists.',exercise='Add a reset button that returns to zero.',closing='Can you add a reset button?',code='const button =\n  document.querySelector("button");\nconst output =\n  document.querySelector("output");\nlet count = 0;',code2='button.addEventListener("click", () => {\n  count++;\n  output.textContent = count;\n});',lines=[
'One click, one number higher. Build this counter with JavaScript.',
'The page needs a button and an output element. Start the displayed number at zero.',
'Select both elements after the page exists, and store zero in a variable called count.',
'Add a click listener. Each click increases count, then text content updates the number on screen.',
'Watch the value change from zero to one, then two. The variable and display stay in sync.',
'Changing the variable alone will not update the page. You must update the output too.',
'Your challenge: add a reset button that sets both the value and display back to zero.',
'Subscribe to Tech at sixty for the next coding project.'
]),
50:dict(title='Build a JavaScript To-Do List: Add and Remove Tasks',shortTitle='Type a task.\nAdd it to your list.',hook='Type → Add → Remove',idea='An input becomes a new list item.',rule='Create the item, set text, append it.',tip='Clear the input after adding the task.',caution='Reject empty input; use textContent.',exercise='Add a task and a remove button.',closing='What is your first task?',code='const text = input.value.trim();\nif (!text) return;\nconst item =\n  document.createElement("li");\nitem.textContent = text;',code2='const remove =\n  document.createElement("button");\nremove.textContent = "Remove";\nremove.onclick = () => item.remove();\nitem.append(remove);\nlist.append(item);\ninput.value = "";',lines=[
'Type a task, click Add, and put it in a list. Here is the basic idea.',
'Use an input, an Add button, and an unordered list. Connect the button to a click handler.',
'Read the input and trim extra spaces. If it is empty, stop before creating anything.',
'Create a list item, set its text content, then append it to the list.',
'Clear the input so the next task is easy to enter. Add a remove button to each item.',
'When Remove is clicked, remove that item. Text content displays user input as plain text.',
'Try adding one task and removing it. This version does not save tasks after a refresh.',
'Subscribe to Tech at sixty for more beginner projects.'
]),
51:dict(title='Publish a Website for Free with GitHub Pages',shortTitle='From local files\nto a public URL',hook='index.html → GitHub Pages',idea='GitHub Pages serves static website files.',rule='Choose a branch and folder as the source.',tip='Keep index.html at the source root.',caution='Public files must not contain secrets.',exercise='Open your published URL on a phone.',closing='Check your site on a phone.',code='my-website/\n  index.html\n  styles.css\n  script.js',code2='Settings → Pages\nSource: Deploy from a branch\nBranch: main\nFolder: / (root)\nSave',lines=[
'Your website works on your computer. Give it a public address with GitHub Pages.',
'For the free public repository option, upload your static files, including index dot H T M L.',
'Open the repository settings, then Pages. Choose deploy from a branch.',
'Select your source branch and folder, then save. Keep the entry file at that source root.',
'Wait for the deployment to finish. Pages shows the address you can visit and share.',
'Keep passwords and private files out. Pages serves static files, not a custom application server.',
'Open the published address on your phone. Check the layout, links, and images.',
'Subscribe to Tech at sixty and keep building.'
])
}
