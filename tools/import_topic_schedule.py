from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
import json,csv
root=Path(__file__).resolve().parent.parent
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with ZipFile('/Users/impulsiveweb/Downloads/Web_Development_50_Video_Topics.xlsx') as z:
 strings=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',ns)] if 'xl/sharedStrings.xml' in z.namelist() else []
 rows=[]
 for row in E.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//m:row',ns):
  vals=[]
  for c in row.findall('m:c',ns):
   v=c.find('m:v',ns); inline=c.find('m:is',ns)
   val=v.text if v is not None else ''.join(inline.itertext()) if inline is not None else ''
   vals.append(strings[int(val)] if c.get('t')=='s' else val)
  if vals and vals[0].isdigit(): rows.append(vals)
existing_path=root/'series/queue.json'
if existing_path.exists() and any(r.get('videoId') for r in json.loads(existing_path.read_text())):
 raise SystemExit('Existing YouTube schedules found. Refusing to overwrite the live queue; reconcile it explicitly.')
queue=[]
for i,(number,phase,topic,description) in enumerate(rows):
 day=datetime(2026,10,20,tzinfo=ZoneInfo('Asia/Kolkata'))+timedelta(days=i//2)
 local=day.replace(hour=(11 if i%2==0 else 16))
 queue.append(dict(videoNumber=int(number),phase=phase,topic=topic,description=description,publishLocal=local.isoformat(),publishAt=local.astimezone(timezone.utc).isoformat().replace('+00:00','Z'),status='planned'))
(root/'series/queue.json').write_text(json.dumps(queue,indent=2,ensure_ascii=False)+'\n')
with (root/'series/posting-calendar.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['videoNumber','topic','publishLocal','publishAt','status']);w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in queue)
p=root/'youtube-publishing.json';c=json.loads(p.read_text());c.update(dailySchedule=dict(times=['11:00','16:00'],timezone='Asia/Kolkata',videosPerDay=2,startDate='2026-10-20'),scheduleStatus='planned',queueFile='series/queue.json');p.write_text(json.dumps(c,indent=2)+'\n')
assert len(queue)==50 and len({r['publishAt'] for r in queue})==50
print('50 unique slots:',queue[0]['publishLocal'],'through',queue[-1]['publishLocal'])
