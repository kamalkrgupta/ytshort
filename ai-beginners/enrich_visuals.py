from pathlib import Path
import json,re
B=Path(__file__).resolve().parent
source=(B/'source-manuscript.txt').read_text()
for n,topic,body in re.findall(r'EPISODE (\d+) \| ([^\n]+)\n(.*?)(?=\nEPISODE \d+ \||\Z)',source,re.S):
 n=int(n);outcome=re.search(r'Learning outcome: ([^\n]+)',body)[1]
 for kind in ['script.json','lesson.json']:
  p=B/'episodes'/f'{n:02d}'/kind
  if not p.exists():continue
  ep=json.loads(p.read_text());v=ep['visual']
  cards=[['One practical AI skill',topic,'Try a beginner exercise'],[outcome,'Inputs shape the response','Human review remains essential'],[v['example'],'Define input and desired output','Compare the response with your goal'],[v['question'].rstrip('?'),'Make one improvement','Compare your two attempts'],[outcome,v['result'],'Practice again with a new example']]
  if n==1:
   cards=[['AI finds patterns','It predicts or generates outputs','You check whether it is useful'],['Training examples → learned patterns','New input → a prediction','A prediction can be wrong'],['You type: “See you…”','Possible suggestions: “soon” / “tomorrow”','You choose what fits your meaning'],['Write your own sentence ending','Compare it with an AI suggestion','Check meaning, tone and accuracy'],['AI is useful for patterns','AI is not a human brain','Verify important answers']]
  if n==2:
   cards=[['Recommendations choose likely matches','Maps estimate routes and travel time','Spam filters classify suspicious mail'],['Input: viewing or location signals','Output: a recommendation or estimate','Your needs may differ from the pattern'],['Example: a suggested tutorial','Check the topic and source','Choose whether it fits your goal'],['Find three AI features on your phone','Name the input and likely output','Check one result for usefulness'],['Notice AI in everyday tools','Recommendations are predictions','Keep control of the final decision']]
  for i,c in enumerate(ep['chapters']):
   c['cards']=cards[i];c['summary']=outcome if i==1 else v['example'] if i==2 else v['question'].rstrip('?') if i==3 else v['result'] if i==4 else 'Learn one practical idea, see an example, and try it yourself.'
  p.write_text(json.dumps(ep,indent=2,ensure_ascii=False)+'\n')
