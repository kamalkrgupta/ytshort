"""Offline acceptance simulation against deployed publisher; no network calls."""
import sys,os,json,unittest
from pathlib import Path
from datetime import timedelta
from unittest.mock import Mock,patch
source=Path(__file__).parent/'source'
sys.path[:0]=[str(source),str(source/'tests')]
from test_system import Base
from publisher import Publisher
from database import SEED_ID,SEED_URL
from scheduled_reel import wait_for_daily_slot
from video_source import select,scan
class FutureDays(Base):
 def test_seven_daily_cycles_with_retries_and_late_events(self):
  self.config.publish_backend='github-actions';self.config.caption_mode='fallback'
  self.config.activation.write_text(json.dumps({'approved':True,'account_id':self.config.account_id}))
  meta=self.fake_meta()
  meta.create_url.return_value='private-container';meta.wait_finished.return_value='FINISHED'
  meta.publish.side_effect=lambda _:f'media-{self.config.now().date()}'
  meta.media.side_effect=lambda ident:({'id':SEED_ID,'permalink':SEED_URL,'timestamp':'2026-10-29T12:00:00+0000'} if ident==SEED_ID else {'id':ident,'permalink':f'https://www.instagram.com/reel/{ident}/','timestamp':self.config.now().isoformat()})
  publisher=Publisher(self.config,self.db,meta=meta,source_url='https://example.invalid/video.mp4')
  with patch.dict(os.environ,{'GITHUB_ACTIONS':'true'}),patch('publisher.validate_video',return_value={}):
   for day in range(7):
    self.config.now.return_value=(self.now+timedelta(days=day)).replace(hour=13,minute=31)
    if day:(self.source/f'{day+2:03} - Topic {day}.mp4').write_bytes(f'unique-{day}'.encode())
    video=select(scan(self.source),self.db)
    def advance(seconds):self.config.now.return_value+=timedelta(seconds=seconds)
    self.assertTrue(wait_for_daily_slot(self.config,self.db,{'sha256':video.sha256},lambda:{'meta':{'valid':True,'expiration_verified':True}},sleep=advance))
    self.assertEqual(meta.publish.call_count,day)
    self.assertEqual(publisher.stage_next()['status'],'READY')
    self.assertEqual(meta.publish.call_count,day)
    self.config.now.return_value=self.config.now().replace(hour=19,minute=0)
    publisher.execute()
    self.assertTrue(self.db.used_day(self.config.now().date().isoformat()))
    self.assertEqual(self.db.jobs()[-1]['status'],'PUBLISHED')
    self.assertEqual(publisher.execute()['status'],'ALREADY_PUBLISHED_TODAY')
    self.config.now.return_value=self.config.now().replace(hour=23)
    self.assertEqual(publisher.execute()['status'],'OUTSIDE_PUBLISH_WINDOW')
    self.assertEqual(meta.publish.call_count,day+1)
  self.assertEqual(len(self.db.published_hashes()),7)
if __name__=='__main__':unittest.main()
