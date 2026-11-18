import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import archive_published_shorts as a
class ArchiveTests(unittest.TestCase):
 def test_scheduled_and_unprocessed_videos_are_excluded(self):
  self.assertFalse(a.eligible({'status':{'privacyStatus':'private','uploadStatus':'processed'}}))
  self.assertFalse(a.eligible({'status':{'privacyStatus':'public','uploadStatus':'uploaded'},'processingDetails':{'processingStatus':'processing'}}))
 def test_copy_is_independent_idempotent_and_retains_publication_record(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp).resolve();dest=root/'source';dest.mkdir();archive=root/'Published Shorts';archive.mkdir();source=dest/'video.mp4';source.write_bytes(b'published-video-content')
   digest=hashlib.sha256(source.read_bytes()).hexdigest();rp=dest/'youtube-upload-receipt.json';receipt={'sha256':digest,'videoId':'vid'};rp.write_text(json.dumps(receipt));(dest/'youtube-metadata.json').write_text(json.dumps({'video':'video.mp4','publishAt':'2026-10-29T05:30:00Z'}))
   item={'id':'vid','snippet':{'channelId':a.CHANNEL,'title':'A title / with punctuation','publishedAt':'2026-10-29T05:30:00Z'},'status':{'privacyStatus':'public','uploadStatus':'processed'},'processingDetails':{'processingStatus':'succeeded'}};rows=[]
   with patch.object(a,'ROOT',root),patch.object(a,'ARCHIVE',archive):
    self.assertTrue(a.archive_one(20,rp,receipt,item,rows));self.assertFalse(a.archive_one(20,rp,receipt,item,rows));a.write_register(rows)
    self.assertEqual(len(rows),1);self.assertIn('+05:30',rows[0]['publishedIST']);self.assertTrue((archive/'published.csv').exists())
    target=archive/rows[0]['file'];self.assertNotEqual(source.stat().st_ino,target.stat().st_ino);source.write_bytes(b'new revision');self.assertEqual(target.read_bytes(),b'published-video-content')
if __name__=='__main__':unittest.main()
