import re,json,csv
from pathlib import Path
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
B=Path(__file__).resolve().parent
TITLES='''What Is AI? A Simple Explanation with Everyday Examples
AI in Everyday Life: 3 Features You Already Use
AI vs Machine Learning vs Deep Learning: The Simple Difference
How Generative AI Works: From Prompt to New Content
5 AI Myths Beginners Should Stop Believing
ChatGPT for Beginners: Ask, Refine and Get Better Answers
Write Better AI Prompts: Goal, Context, Audience and Format
Prompt Engineering for Beginners: Show AI an Example
Role Prompting Explained: Give AI the Context It Needs
Better AI Answers Start with Better Follow-Up Prompts
AI Research for Beginners: Find Sources and Verify Claims
AI Hallucinations: How to Spot and Check Confident Errors
Reusable AI Prompt Templates: Stop Starting from Scratch
Write Better Emails with AI: Clear Drafts in Simple Steps
AI for Students: Build a Tutor, Not an Answer Machine
AI for Job Seekers: Improve Your Resume and Interview Practice
AI at Work: Turn Meeting Notes into Clear Action Items
AI for Spreadsheets: Understand Formulas and Check Results
AI Presentations: Turn One Idea into a Clear Slide Outline
AI Time Management: Prioritize Tasks That Actually Matter
Learn a Language with AI: Vocabulary and Conversation Practice
AI Social Media Captions: Write a Hook That Fits Your Audience
AI for YouTube Creators: Plan Titles, Scripts and Descriptions
AI Image Generation for Beginners: Your First Image Prompt
Better AI Image Prompts: Framing, Color and Aspect Ratio
AI Video Generation for Beginners: Plan Scenes and Camera Motion
AI Voiceovers Explained: Prepare a Script for Text to Speech
AI Music and Sound Effects: Choose Audio That Fits Your Video
AI Graphic Design: Turn a Rough Draft into a Clear Layout
AI Translation and Subtitles: Check Meaning Before You Publish
AI Search vs Traditional Search: Answers, Sources and Verification
AI Privacy: What to Check Before Sharing Personal Data
AI Copyright Basics: Originality, Licensing and Attribution
AI Scams and Deepfakes: Warning Signs You Can Check
Responsible AI: Spot Bias and Missing Perspectives
No-Code AI Automation: Connect a Trigger, Action and Human Check
Build an AI Workflow: Inputs, Outputs and Review Steps
AI Customer Support: Better FAQ Answers and Human Handoffs
AI for Small Business: Find Repetitive Tasks Worth Automating
AI Data Analysis for Beginners: Ask Better Questions of Your Data
What Is an AI API? Requests and Responses Explained Simply
AI and Python for Beginners: Variables, Strings and Functions
Build a Simple FAQ Chatbot: Questions, Answers and Limits
What Are AI Agents? Planning, Tools and Human Oversight
RAG Explained for Beginners: Give AI Relevant Documents
AI Coding Help: Explain, Generate and Debug Small Programs
Your First AI Project: Pick a Useful Goal and Keep It Small
Build an AI Study Assistant: Prompts, Examples and Fact Checks
AI Content Workflow: Take an Educational Video from Idea to Upload
Learn AI in 30 Days: A Practical Beginner Practice Plan'''.splitlines()
source=(B/'source-manuscript.txt').read_text();queue=[]
for n,title,body in re.findall(r'EPISODE (\d+) \| ([^\n]+)\n(.*?)(?=\nEPISODE \d+ \||\Z)',source,re.S):
 n=int(n); outcome=re.search(r'Learning outcome: ([^\n]+)',body)[1]
 example=re.search(r'Our example is ([^.]+)',body)[1]
 exercise=re.search(r'Try this exercise: ([^.]+)',body)[1]
 caution=re.search(r'remember this important limitation: ([^.]+)',body)[1]
 chapters=[]
 for i,(heading,text,direction) in enumerate(re.findall(r'\d\d:\d\d–\d\d:\d\d \| ([^\n]+)\nNARRATION — ([^\n]+)\nVISUAL / EDIT — ([^\n]+)',body)):
  # Repair recurring manuscript grammar without changing the teaching objective.
  text=text.replace('the focus is to ','the key idea is this: ').replace('learned how to ','learned that ')
  chapters.append(dict(id=f'chapter-{i+1:02d}',title=heading,text=text,direction=direction))
 assert len(chapters)==5,(n,len(chapters))
 when=datetime(2026,10,27,14,tzinfo=ZoneInfo('Asia/Kolkata'))+timedelta(days=(n-1)//2)
 ep=dict(episode=n,topic=title,chapters=chapters,visual=dict(example=example[0].upper()+example[1:],question=exercise[0].upper()+exercise[1:]+'?',steps=['Define your goal','Provide useful input','Review the output'],checks=['Check accuracy','Refine the response','Compare the result'],result=caution[0].upper()+caution[1:]),publishAt=when.isoformat(),plannedDate=when.date().isoformat(),status='planned')
 dest=B/'episodes'/f'{n:02d}';dest.mkdir(parents=True,exist_ok=True)
 (dest/'script.json').write_text(json.dumps(ep,indent=2,ensure_ascii=False))
 title=TITLES[n-1]+f' | Ep {n:02d}'
 tags=list(dict.fromkeys([ep['topic'].lower(),'AI for beginners','artificial intelligence tutorial','learn AI','AI tutorial English','Techat60']+(['AI agents','agentic AI'] if n==44 else ['RAG','retrieval augmented generation'] if n==45 else ['prompt engineering','AI prompts'] if n in (7,8,9,10,13) else [])))
 description=f'{TITLES[n-1]}. Learn with a simple example and a beginner exercise.\n\nAI for Beginners — Episode {n:02d} of 50\n\nWhat you will learn: {outcome}\nExample: {example}.\nTry it: {exercise}.\nRemember: {caution}.\n\nFollow the series in episode order and practice with sample data. Share your question or exercise result in the comments.\nSubscribe to @Techat60 for practical AI tutorials.\n\n#AIForBeginners #ArtificialIntelligence #LearnAI'
 meta=dict(title=title,description=description,tags=tags,video='video.mp4',publishAt=when.isoformat())
 assert len(title)<=100 and len(description)<5000 and sum(len(t)+3 for t in tags)<500
 (dest/'youtube-metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False))
 (dest/'youtube-upload-details.txt').write_text(title+'\n\n'+description+'\n\nTags: '+', '.join(tags))
 queue.append(dict(episode=n,topic=ep['topic'],title=title,publishAt=when.isoformat(),plannedDate=when.date().isoformat(),status='planned'))
(B/'queue.json').write_text(json.dumps(queue,indent=2))
with (B/'posting-calendar.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(queue[0]));w.writeheader();w.writerows(queue)
with (B/'youtube-metadata.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['episode','publishAt','title','description','tags']);w.writeheader()
 for row in queue:
  m=json.loads((B/'episodes'/f'{row["episode"]:02d}'/'youtube-metadata.json').read_text());w.writerow(dict(episode=row['episode'],publishAt=row['publishAt'],title=m['title'],description=m['description'],tags=', '.join(m['tags'])))
print('Prepared',len(queue),'episodes;',queue[0]['publishAt'],'through',queue[-1]['publishAt'])
