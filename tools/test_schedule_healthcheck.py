import unittest
from datetime import datetime,timedelta
from schedule_healthcheck import action,corrected_status,expected_at,ZONE
class ReadinessTests(unittest.TestCase):
 def setUp(self):
  self.now=datetime(2026,10,28,8,tzinfo=ZONE);self.at=self.now.replace(hour=11)
  self.item={'id':'video','status':{'privacyStatus':'private','publishAt':self.at.isoformat(),'uploadStatus':'processed','license':'youtube','selfDeclaredMadeForKids':False},'processingDetails':{'processingStatus':'succeeded'}}
 def test_scheduled_and_processed_is_ready(self):self.assertEqual(action(self.item,self.at,self.now),'ready')
 def test_wrong_time_gets_fixed(self):
  self.item['status']['publishAt']=(self.at+timedelta(hours=1)).isoformat();self.assertEqual(action(self.item,self.at,self.now),'correct_schedule')
 def test_processing_is_not_mistaken_for_ready(self):
  self.item['processingDetails']['processingStatus']='processing';self.item['status']['uploadStatus']='uploaded';self.assertEqual(action(self.item,self.at,self.now),'processing')
 def test_overdue_private_video_publishes(self):self.assertEqual(action(self.item,self.at,self.now.replace(hour=12)),'publish_overdue')
 def test_public_video_is_not_hidden_for_future_slot(self):
  self.item['status']['privacyStatus']='public';self.assertEqual(action(self.item,self.at,self.now),'already_public')
 def test_status_update_preserves_audience_and_license(self):
  out=corrected_status(self.item,self.at,self.now);self.assertFalse(out['status']['selfDeclaredMadeForKids']);self.assertEqual(out['status']['license'],'youtube');self.assertEqual(out['status']['publishAt'],self.at.isoformat())
 def test_past_release_does_not_send_past_publish_at(self):self.assertNotIn('publishAt',corrected_status(self.item,self.at,self.now.replace(hour=12))['status'])
 def test_short_slots(self):
  cfg={'dailySchedule':{'startDate':'2026-10-20','times':['11:00','16:00'],'videosPerDay':2}}
  self.assertEqual(expected_at('Shorts',{'videoNumber':18},cfg),self.at);self.assertEqual(expected_at('Shorts',{'videoNumber':19},cfg),self.at.replace(hour=16))
 def test_daily_pairs_for_ai_and_agile(self):
  for kind,start,hour,n in [('AI','2026-10-27',14,3),('Agile','2026-10-24',18,11)]:
   cfg={'dailySchedule':{'startDate':start,'times':[f'{hour}:00'],'videosPerDay':2}}
   a=expected_at(kind,{'episode':n},cfg);b=expected_at(kind,{'episode':n+1},cfg);self.assertEqual(a,b);self.assertEqual(a,self.now.replace(hour=hour))
if __name__=='__main__':unittest.main()
