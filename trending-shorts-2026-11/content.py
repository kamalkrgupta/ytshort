"""Twenty original beginner explainers, checked against primary sources on 2026-11-16."""
TOPICS=[]
def add(slug,title,category,source,headline,meaning,example,comparison,caution,question,flow,left,right,lines):
 TOPICS.append(dict(slug=slug,title=title,category=category,source=source,headline=headline,meaning=meaning,example=example,comparison=comparison,caution=caution,question=question,flow=flow,left=left,right=right,lines=lines))
add('passkeys','Passkeys Explained: Sign In Without Typing a Password','SECURITY','https://blog.google/innovation-and-ai/technology/safety-security/how-to-set-up-passkey/',
'Your face is not\nyour password.','Unlock a passkey with your device.','The website receives proof, not your fingerprint.','Password: a shared secret. Passkey: cryptographic proof.','Keep account recovery options up to date.','Would you try a passkey?',['Website challenge','Device unlock','Signed response'],['PASSWORD','Type a shared secret'],['PASSKEY','Unlock and prove'],[
'You unlock your phone with your face. A passkey can let you sign in the same way.',
'Instead of typing a password, your device uses a cryptographic key to prove the sign-in is yours.',
'The website sends a challenge. You approve with your fingerprint, face scan, or device pin.',
'The site receives a signed response, not your fingerprint. Passkeys are designed to resist phishing.',
'Recovery still matters. Check how your account restores access if your device is lost.',
'Would you try a passkey? Subscribe to Tech at sixty for clear tech explainers.'])
add('agents','AI Agents vs Chatbots: What Actually Changes?','AI','https://www.anthropic.com/research/trustworthy-agents',
'An answer.\nOr an action?','Agents use tools in a feedback loop.','Draft a plan, use a tool, inspect the result.','The key difference is tool use and a decision loop.','Give tools only the permissions the task needs.','Which task would you delegate?',['Plan','Use a tool','Check result'],['CHATBOT','Responds in a conversation'],['AGENT','Acts, observes, adjusts'],[
'A chatbot can explain how to organize files. An agent may actually organize them using tools.',
'An agent can plan a step, take an action, inspect the result, and decide what comes next.',
'Imagine a helper that reads receipt details, sorts them, and checks whether anything is missing.',
'The difference is not a magic personality. It is the combination of a model, tools, and a control loop.',
'Permissions matter because a mistaken answer and a mistaken action have different consequences.',
'Which task would you delegate? Subscribe to Tech at sixty for practical tech explained.'])
add('wifi7','Wi-Fi 7 Explained: Why Multiple Links Matter','CONNECTIVITY','https://www.intel.com/content/www/us/en/products/details/wireless/wi-fi-7-series.html',
'One connection.\nMore than one lane.','Multi-Link Operation can use multiple wireless links.','A compatible device can avoid a congested link.','Wi-Fi capacity is different from internet-plan speed.','Both the router and device need compatible support.','Is your bottleneck Wi-Fi or internet?',['Your device','Multiple links','Your router'],['WI-FI LINK','Device to router'],['INTERNET PLAN','Router to the internet'],[
'Your wireless connection can feel busy even when your internet plan looks fast. Wi-Fi seven adds another idea.',
'Multi-Link Operation allows compatible devices to use multiple wireless links instead of relying on just one.',
'Think of traffic moving through more than one lane, with the exact behavior depending on the hardware.',
'This can improve reliability and responsiveness. It does not automatically make your internet subscription faster.',
'Your router, device, surroundings, and local rules all affect which features you can actually use.',
'Is your bottleneck Wi-Fi or internet? Subscribe to Tech at sixty for clear tech explainers.'])
add('local-ai','Local AI vs Cloud AI: Where Does Your Prompt Go?','AI','https://developers.googleblog.com/en/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/',
'Where does\nyour prompt go?','Local inference runs on your own device.','A downloaded model can process a note locally.','Cloud processing uses a remote server. Local uses your hardware.','Local apps can still have network-connected features.','Which task would you keep local?',['Your prompt','On-device model','Local result'],['LOCAL MODEL','Uses your device resources'],['CLOUD MODEL','Uses remote compute'],[
'When you ask an A I a question, the answer does not always come from a distant server.',
'Local A I runs a downloaded model on your own phone or computer. Cloud A I processes requests remotely.',
'A local app might summarize a sample note without sending that note to a model server.',
'The tradeoff is hardware. Your memory and processor limit which models run comfortably.',
'Do not assume every feature stays offline. Check the app, downloads, and network settings.',
'Which task would you keep local? Subscribe to Tech at sixty for clear tech explainers.'])
add('usb-c','USB-C Explained: Same Plug, Different Capabilities','GADGETS','https://www.usb.org/sites/default/files/usb_type-c_language_product_and_packaging_guidelines_20230320.pdf',
'Same plug.\nDifferent capabilities.','USB-C describes the connector shape.','Two matching connectors can support different data rates.','Data, charging and display support are separate capabilities.','Check the port, cable and connected device.','Have two identical cables behaved differently?',['Computer port','USB-C cable','Connected device'],['CONNECTOR','The physical shape'],['CAPABILITIES','Data, power, display'],[
'These two cables have the same plug. That does not mean they do the same job.',
'U S B C describes a connector. Data speed, charging power, and display support are separate capabilities.',
'A cable with that connector might support basic data, while another supports much faster transfers.',
'The connection is limited by the combination of the port, cable, and device, not the plug shape alone.',
'Check the performance labels and specifications before expecting a cable to handle a display or fast transfer.',
'Have identical plugs behaved differently? Subscribe to Tech at sixty for clear tech explainers.'])
add('prompt-injection','Prompt Injection: When a Webpage Tries to Boss an AI Around','SECURITY','https://www.anthropic.com/research/prompt-injection-defenses',
'When a webpage\ntries to give orders.','Untrusted content can contain instructions aimed at an AI.','A page summary should not become permission to take actions.','Reading a page is different from obeying it.','Prompt injection remains an unsolved security challenge.','Should a page be allowed to give orders?',['Your task','Untrusted page','Check authority'],['YOUR REQUEST','Summarize this page'],['PAGE CONTENT','May contain hostile instructions'],[
'You ask an A I to summarize a webpage. The page contains instructions trying to redirect the assistant.',
'That is prompt injection: untrusted content attempts to influence how an A I follows your task.',
'The trick becomes more serious when an assistant can also use tools or access private information.',
'Text on a webpage is information to inspect. It should not automatically become an instruction to obey.',
'Defenses help, but the problem is not fully solved. Limit access and check important actions.',
'Should a page give orders? Subscribe to Tech at sixty for practical tech explained.'])
add('digital-twins','Digital Twins Explained: Test a Change Before Making It','FUTURE TECH','https://www.nvidia.com/en-eu/glossary/digital-twin/',
'Test the change\nbefore the real world.','A digital twin represents a real system.','Try a factory-layout change in a connected simulation.','A useful twin connects its model to relevant real-world data.','Simulation results depend on model and data quality.','What would you test in a digital twin?',['Real system','Data connection','Digital model'],['REAL SYSTEM','Machines and measurements'],['DIGITAL TWIN','Model and simulation'],[
'What if you could test a factory change before moving a single machine? That is one use of digital twins.',
'A digital twin is a digital representation of a real object or system, connected to relevant data.',
'A team might simulate a different layout and inspect how people, machines, or materials move.',
'The point is not just a beautiful three dimensional picture. The connection to the real system makes it useful.',
'A simulation is only as dependable as its assumptions, model, and data. Check those before acting.',
'What would you test first? Subscribe to Tech at sixty for clear tech explainers.'])
add('npu','CPU vs GPU vs NPU: What Does an AI Chip Do?','GADGETS','https://www.qualcomm.com/artificial-intelligence/what-is-ai-faq',
'What is the\nAI chip actually doing?','An NPU specializes in neural-network workloads.','Run supported AI operations efficiently on the device.','CPU, GPU and NPU handle different workloads.','App support and the full system matter, too.','Which chip does your app actually use?',['App task','Supported workload','Right processor'],['CPU / GPU','General tasks / parallel work'],['NPU','Specialized neural computation'],[
'An A I chip is not a tiny person inside your laptop. It is hardware designed for particular calculations.',
'A C P U handles general computing. A G P U processes many operations in parallel.',
'An N P U specializes in neural network workloads, helping supported A I tasks run efficiently on a device.',
'These processors work together. An app may use one or several depending on the operation.',
'A bigger marketing number alone does not tell you the whole experience. Software support and memory matter too.',
'Which chip does your app use? Subscribe to Tech at sixty for clear tech explainers.'])
add('matter','Matter Explained: A Common Language for Smart Homes','SMART HOME','https://csa-iot.org/all-solutions/matter/matter-faq/',
'Why cannot your\nsmart devices agree?','Matter is a shared smart-home application protocol.','Connect compatible products across supported ecosystems.','Thread or Wi-Fi carries data; Matter defines communication.','Check device type, controller and supported features.','Which smart-home device should work together?',['Compatible device','Matter controller','Home ecosystem'],['MATTER','A shared application protocol'],['THREAD / WI-FI','Ways to carry the data'],[
'A smart bulb and a smart speaker can come from different brands. How do they understand each other?',
'Matter gives compatible smart home products a common application protocol, helping supported ecosystems work together.',
'Think of it as shared rules for messages such as turn the light on or report a temperature.',
'Wi-Fi, Thread, and Ethernet carry the data. Matter describes how compatible devices communicate over that connection.',
'Compatibility still needs checking. The device type, controller, setup, and supported features can differ.',
'Which devices should work together? Subscribe to Tech at sixty for clear tech explainers.'])
add('post-quantum','Post-Quantum Encryption: Why Prepare Before Quantum Computers?','SECURITY','https://blog.cloudflare.com/post-quantum-geo-key-manager/',
'Why prepare for\na computer not here yet?','Some public-key systems face a future quantum threat.','Recorded encrypted data may stay sensitive for years.','Post-quantum cryptography runs on ordinary computers.','It is about migration, not an instant universal break.','How long must your data stay private?',['Protect data now','Keep it for years','Future threat'],['QUANTUM COMPUTER','A future capability threat'],['POST-QUANTUM CRYPTO','New protective algorithms'],[
'Why change encryption before a powerful enough quantum computer exists? Because some information must stay private for years.',
'An attacker could record encrypted traffic now and hope to decrypt it later with future capabilities.',
'Post quantum cryptography uses algorithms designed to resist known quantum attacks. It runs on ordinary computers.',
'This does not mean every kind of encryption is already broken, or that a quantum laptop is required.',
'Organizations are updating protocols and systems gradually. Long lived sensitive data is an important reason to prepare.',
'How long must data stay private? Subscribe to Tech at sixty for clear tech explainers.'])
add('smart-glasses','AI Glasses vs AR Glasses: Do They All Have a Screen?','GADGETS','https://about.fb.com/news/2026/09/introducing-ray-ban-meta-audio-glasses-new-styles-plus-muse/',
'AI glasses\ndo not all have screens.','Audio, cameras and displays are different features.','A voice assistant can respond without a visual overlay.','An AI assistant is different from an AR display.','Check the exact model and recording indicators.','Would you prefer audio or a display?',['Microphone / camera','AI processing','Audio / display'],['AI FEATURES','Questions and assistance'],['AR DISPLAY','Visual overlays when supported'],[
'When you hear A I glasses, do you imagine a screen floating in front of your eyes? Not every pair has one.',
'Glasses can combine microphones, speakers, cameras, and an assistant. The exact features depend on the model.',
'An audio focused pair may answer through speakers without showing a visual interface in the lens.',
'An augmented reality display is a separate capability. The labels A I and A R are not interchangeable.',
'Before choosing, check the specific hardware, phone connection, available features, and recording indicators.',
'Would you prefer audio or a display? Subscribe to Tech at sixty for clear tech explainers.'])
add('webgpu','WebGPU Explained: How AI Can Run Inside a Browser','WEB TECH','https://developer.chrome.com/blog/io24-webassembly-webgpu-1',
'AI inside\na browser tab?','WebGPU exposes GPU computation to web applications.','A supported model can process data on your device.','A webpage can use local hardware, not only a cloud server.','Support, model downloads and app design still matter.','Which browser task would you run locally?',['Browser app','WebGPU','Your GPU'],['CLOUD REQUEST','Remote model server'],['WEB INFERENCE','Processing on your device'],[
'An A I tool in a browser does not always need to send every calculation to a remote server.',
'Web G P U lets supported web applications use graphics hardware for computation, as well as graphics.',
'That can help a suitable model process data directly on your device, inside a browser tab.',
'Local processing can reduce network dependence, but it still uses your device memory, power, and compute.',
'Not every browser, model, or feature supports the same setup. A model download may be needed first.',
'Which task would you run locally? Subscribe to Tech at sixty for clear tech explainers.'])
add('world-models','AI World Models: Predicting What Happens Next','AI','https://deepmind.google/blog/genie-4-a-new-generation-of-world-simulation/',
'An AI that models\nwhat happens next.','World models generate or predict changing environments.','An action changes the next state of a simulated world.','Interactive simulation differs from a fixed video clip.','A generated world is not guaranteed real-world physics.','What would you try in a simulated world?',['Current scene','Your action','Next scene'],['VIDEO CLIP','A fixed sequence'],['WORLD MODEL','Responds to actions'],[
'A video plays the same sequence. A world model can generate a changing environment that responds to actions.',
'Give it a scene and an action, and it tries to model what happens next.',
'Imagine steering through a generated space rather than simply watching a prerecorded clip. This diagram is only an illustration.',
'Researchers explore these models for interactive experiences and environments where agents can practise.',
'A convincing world can still contain mistakes. Visual realism does not guarantee correct physics or reliable real world behavior.',
'What would you try in a simulated world? Subscribe to Tech at sixty for tech explained.'])
add('small-models','Small Language Models: Why Smaller Can Be Useful','AI','https://developers.googleblog.com/own-your-ai-fine-tune-gemma-3-270m-for-on-device/',
'Does every task\nneed a giant model?','Small models can focus on narrow tasks.','Classify a message or transform a short piece of text.','Model size is one tradeoff, not a quality score.','Test the model on the actual task.','What small task would you automate?',['Narrow task','Small model','Check result'],['LARGE MODEL','Broader capacity; more resources'],['SMALL MODEL','Lighter; task dependent'],[
'Does sorting short messages need the same model as a complex research task? Not necessarily.',
'Small language models use fewer parameters and can be easier to run on limited hardware.',
'A focused model might classify a message, transform a short sentence, or handle a narrow assistant feature.',
'Smaller does not automatically mean better, faster, or accurate enough. The task and implementation decide the tradeoff.',
'Compare real outputs, memory use, and response time on your own examples before choosing.',
'What small task would you automate? Subscribe to Tech at sixty for clear tech explainers.'])
add('watermarks','AI Watermarks Explained: What They Can and Cannot Prove','DIGITAL LIFE','https://deepmind.google/models/synthid/',
'Can an invisible mark\nidentify AI media?','A watermark can signal how content was generated.','A detector checks for a supported watermark pattern.','Finding a mark is different from proving a claim true.','No detected mark does not prove human creation.','What would you verify before sharing?',['Supported generation','Embedded watermark','Detector check'],['MARK FOUND','Evidence of a supported signal'],['NO MARK FOUND','Not proof of human origin'],[
'An image can contain a watermark you cannot see. A detector may still be able to find it.',
'Tools such as Synth I D embed signals in supported A I generated content to help identify its origin.',
'The signal is part of the content, rather than just a visible logo placed in a corner.',
'A detected watermark can support an origin claim. It does not prove that the scene or message is true.',
'And no detected mark does not prove a human made the file. Check sources and context too.',
'What would you verify before sharing? Subscribe to Tech at sixty for clear tech explainers.'])
add('satellite','Satellite Messaging: How a Phone Connects Beyond Cell Towers','CONNECTIVITY','https://www.t-mobile.com/dialed-in/wireless/how-satellite-phone-service-works',
'No nearby tower.\nCan a message still travel?','Supported phones can connect through satellites.','A message travels via space and a ground network.','Satellite connectivity differs from normal mobile broadband.','Availability depends on phone, provider, region and sky view.','Would messaging be enough off the grid?',['Compatible phone','Satellite','Ground network'],['CELLULAR','Nearby terrestrial towers'],['SATELLITE','Space-based radio link'],[
'Your phone has no nearby cell tower. Some supported services can send messages through a satellite instead.',
'The signal travels between a compatible phone, a satellite, and the network on the ground.',
'This can extend connectivity beyond regular tower coverage, depending on the service and where you are.',
'It is not automatically a replacement for normal mobile broadband. Speed, supported apps, and delays can differ.',
'Check your phone, provider, region, and clear view of the sky before relying on a feature.',
'Would messaging be enough off the grid? Subscribe to Tech at sixty for clear tech explainers.'])
add('vibe-coding','Vibe Coding: The Part You Still Need to Check','CODING','https://github.blog/news-insights/product-news/github-copilot-agent-mode-activated/',
'The code runs.\nIs the job finished?','AI can turn a description into a draft implementation.','Ask for a small feature, then test normal and edge cases.','A generated draft is different from verified software.','Understand changes before running them on real data.','What test would you run first?',['Describe feature','Review code','Run tests'],['GENERATED DRAFT','Looks plausible'],['VERIFIED CHANGE','Tested against requirements'],[
'You describe an app, and an A I writes code. The first version appears quickly. Is the work finished?',
'People often call this vibe coding. The useful idea is describing a goal and iterating with a coding assistant.',
'Try a tiny example: a counter that adds one. Then test what reset does and what happens at the boundaries.',
'Generated code is a draft, not proof that the feature is correct or safe for real data.',
'Read changes, run tests, and check dependencies. Keep the project small enough to understand.',
'What test would you run first? Subscribe to Tech at sixty for practical tech explained.'])
add('semantic-search','Semantic Search: Finding Meaning Instead of Exact Words','AI','https://developers.googleblog.com/en/embeddinggemma-2-the-developer-guide/',
'Search for meaning,\nnot just matching words.','Embeddings represent content as numerical vectors.','A query about a rainy trip may find a relevant note.','Similar meaning can match different wording.','Similarity does not guarantee truth or relevance.','When would meaning-based search help?',['Your question','Embedding comparison','Related content'],['KEYWORD SEARCH','Matches words and phrases'],['SEMANTIC SEARCH','Compares learned meaning'],[
'You search for a rainy trip, but the note says wet weekend. Exact word matching might miss the connection.',
'Semantic search uses embeddings: numerical representations that capture useful relationships between pieces of content.',
'A query and a document can be compared in that numerical space, even when their wording differs.',
'This helps retrieve related material. Some systems can compare images, audio, or video as well as text.',
'Similarity is not a guarantee of truth. Inspect the results and test how the search behaves.',
'When would meaning based search help? Subscribe to Tech at sixty for clear tech explainers.'])
add('auracast','Auracast Explained: One Audio Broadcast, Many Listeners','GADGETS','https://www.bluetooth.com/auracast/faq/',
'One screen.\nMany sets of earbuds.','Auracast broadcasts audio to compatible receivers.','Listeners can join a nearby supported broadcast.','Broadcast audio differs from one-to-one pairing.','Both transmitter and receiver need support.','Where would shared audio be useful?',['Audio source','One broadcast','Many receivers'],['PAIRED AUDIO','A device-to-device relationship'],['BROADCAST AUDIO','Many listeners join a stream'],[
'Imagine several people listening to the same television through their own earbuds. Auracast is designed for shared audio.',
'A compatible transmitter broadcasts an audio stream that nearby compatible receivers can join.',
'Instead of creating a separate one to one link for every listener, one broadcast serves many receivers.',
'A phone or another assistant can help you discover the broadcast and choose which stream to hear.',
'An ordinary Bluetooth label alone is not enough. Check Auracast support on both ends of the connection.',
'Where would shared audio be useful? Subscribe to Tech at sixty for clear tech explainers.'])
add('mcp','MCP Explained: How AI Apps Connect to Tools','AI','https://modelcontextprotocol.io/docs/getting-started/intro',
'How does an AI\nconnect to your tools?','MCP standardizes connections to tools and data.','An AI app can ask a connected service for information.','A connection protocol is different from permission.','Review the server, data access and action permissions.','Which tool would you connect first?',['AI application','MCP connection','Tool or data'],['WITHOUT A STANDARD','Separate custom integrations'],['WITH MCP','A shared connection protocol'],[
'An A I model and your calendar are different systems. How does an app connect the two?',
'The Model Context Protocol, or M C P, standardizes how A I applications connect to tools and data sources.',
'A connected service can expose useful information or actions in a structured way the application understands.',
'Think of a common connection language. It does not magically give a model access to everything.',
'Permissions, server trust, and what data gets shared still need careful setup.',
'Which tool would you connect first? Subscribe to Tech at sixty for clear tech explainers.'])
