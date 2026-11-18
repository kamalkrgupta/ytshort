import json
from pathlib import Path
W=Path(__file__).resolve().parent.parent;B=W/'channel-seo'
a=json.loads((B/'before.json').read_text())
keywords=['TECH AT 60','Techat60','AI for beginners','artificial intelligence tutorials','prompt engineering','AI tools','AI agents','RAG explained','web development for beginners','learn HTML','CSS tutorial','JavaScript tutorial','coding shorts','Agile testing','software testing tutorial','manual testing','QA tutorial','Scrum','Kanban','test automation']
description='''Learn AI, web development and software testing with TECH AT 60. Beginner-friendly English tutorials, practical examples and short lessons to help you build useful technology skills.

Explore our learning paths:
• AI for Beginners: AI basics, prompts, productivity, creative tools, automation, agents and RAG.
• Web Development: HTML, CSS and JavaScript, explained one concept at a time.
• Agile Testing Masterclass: QA fundamentals, Scrum, Kanban, test design, documentation and automation.

Watch the playlists in lesson order, try the exercises and use sample data while you practice. Alongside 60-second coding Shorts, you’ll find longer tutorials with guided examples.

Subscribe to TECH AT 60 for clear, practical technology lessons. Ask a question or share what you built in the comments.'''
assert len(description)<=1000
kw=' '.join('"'+k+'"' if ' ' in k else k for k in keywords);assert len(kw)<=500
plan=dict(channelDescription=description,channelKeywords=kw,removeTags=['cjp','bjp','congree','neha bora','elon mask','trump','usa','modi','latent','delhi'],sourceGuidance=['https://support.google.com/youtube/answer/146402','https://support.google.com/youtube/answer/12948449','https://support.google.com/youtube/answer/16090438'])
(B/'changes.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n');print('Prepared channel description:',len(description),'characters; keywords:',len(kw),'characters.')
