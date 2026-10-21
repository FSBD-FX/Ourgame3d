"""Small synthetic corruption/boundary cases. No actual E/source media writes."""
from pathlib import Path
from datetime import datetime,timezone
import importlib.util
import io
import json
import lzma
import os
import sys
import tarfile
import unittest
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('solid_retention_tested',HERE/'retain-native-media-lossless-solid-tar-xz-v001.py')
V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
RUN=HERE/'validation-runs'/('t'+datetime.now(timezone.utc).strftime('%H%M%S%f'))
SOURCE=RUN/'sources'

def fixture(name):
 s=SOURCE/name;s.mkdir(parents=True)
 for rel,data in [('原件/a.bin',b'original\x00'*45),('展示副本/b.txt','展示副本保持原字节'.encode()),('index.json',b'{"synthetic":true}\n')]:
  p=s/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 storage=RUN/('storage-'+name);storage.mkdir();(storage/'README.md').write_bytes(b'SYNTHETIC STORAGE ROOT DO NOT CHANGE\n')
 return s,storage

def archive(path,items):
 with lzma.open(path,'wb',preset=0) as f:
  with tarfile.open(fileobj=f,mode='w|',format=tarfile.PAX_FORMAT) as t:
   for name,data,typ in items:
    info=tarfile.TarInfo(name);info.type=typ
    if typ==tarfile.SYMTYPE:info.linkname='../foreign'
    else:info.size=len(data)
    t.addfile(info,None if typ==tarfile.SYMTYPE else io.BytesIO(data))

class Tests(unittest.TestCase):
 def test01_full_unicode_original_presentation_two_streaming_passes_and_index(self):
  s,d=fixture('positive');r=V.retain(s,d,'2026-10-19_full_v001',SOURCE,preset=0)
  self.assertTrue(r['full_source_member_retention']);self.assertFalse(r['is_actual_E_retention'])
  self.assertEqual(r['file_count'],3);self.assertEqual(r['verification_passes'],2)
  proof=V.verify_index(d/'2026-10-19_full_v001'/V.INDEX_NAME);self.assertTrue(proof['passed'])
 def test02_bad_member_names_rejected_without_extraction(self):
  for i,name in enumerate(('../escape','/absolute','C:/drive','a\\b','a//b','./a','a/../b')):
   p=RUN/('unsafe-'+str(i)+'.tar.xz');archive(p,[(name,b'x',tarfile.REGTYPE)])
   with self.assertRaises(ValueError):V.verify_archive(p,[dict(member='safe',bytes=1,sha256='0'*64)])
 def test03_duplicate_extra_and_missing_tar_members_rejected(self):
  s,d=fixture('member-count');_,rows,_=V.snapshot(s,SOURCE);base=[(x['member'],Path(x['source']).read_bytes(),tarfile.REGTYPE) for x in rows]
  for i,items in enumerate((base+base[:1],base+[('extra',b'x',tarfile.REGTYPE)],base[:-1])):
   p=d/('bad-'+str(i)+'.tar.xz');archive(p,items)
   with self.assertRaises(ValueError):V.verify_archive(p,rows)
 def test04_source_same_size_drift_preserves_failed_packet(self):
  s,d=fixture('source-drift');before=V.pin(d/'README.md');pack=V.pack
  def drifting(*args):pack(*args);p=s/'原件/a.bin';p.write_bytes(b'x'*p.stat().st_size)
  with patch.object(V,'pack',side_effect=drifting):
   with self.assertRaises(ValueError):V.retain(s,d,'2026-10-19_drift_v001',SOURCE,preset=0)
  failed=d/'2026-10-19_drift_v001'
  self.assertTrue((failed/V.PACKET_NAME).exists());self.assertTrue((failed/'retention-failure-v001.json').exists())
  self.assertFalse((failed/V.INDEX_NAME).exists());self.assertEqual(before,V.pin(d/'README.md'))
 def test05_existing_target_is_rejected_without_changing_previous_packet(self):
  s,d=fixture('existing');r=V.retain(s,d,'2026-10-19_exists_v001',SOURCE,preset=0);before=V.pin(r['packet']['path'])
  with self.assertRaises(ValueError):V.retain(s,d,'2026-10-19_exists_v001',SOURCE,preset=0)
  self.assertEqual(before,V.pin(r['packet']['path']))
 def test06_missing_source_after_snapshot_preserves_failure(self):
  s,d=fixture('missing-source');pack=V.pack
  def missing(*args):pack(*args);(s/'index.json').unlink()
  with patch.object(V,'pack',side_effect=missing):
   with self.assertRaises(ValueError):V.retain(s,d,'2026-10-19_missing_v001',SOURCE,preset=0)
  self.assertTrue((d/'2026-10-19_missing_v001'/'retention-failure-v001.json').exists())
 def test07_source_membership_addition_rejected(self):
  s,d=fixture('extra-source');pack=V.pack
  def extra(*args):pack(*args);(s/'.extra-member.bin').write_bytes(b'new')
  with patch.object(V,'pack',side_effect=extra):
   with self.assertRaises(ValueError):V.retain(s,d,'2026-10-19_extra_v001',SOURCE,preset=0)
 def test08_corrupt_xz_is_rejected_and_not_extracted(self):
  s,d=fixture('corrupt');_,rows,_=V.snapshot(s,SOURCE);p=d/'corrupt.tar.xz';V.pack(p,rows,0)
  data=bytearray(p.read_bytes());data[len(data)//2]^=0xff;p.write_bytes(data)
  with self.assertRaises((ValueError,lzma.LZMAError,tarfile.ReadError,EOFError)):V.verify_archive(p,rows)
 def test09_tar_symlink_and_wrong_member_bytes_rejected(self):
  s,d=fixture('bad-type');_,rows,_=V.snapshot(s,SOURCE)
  p=d/'symlink.tar.xz';archive(p,[(rows[0]['member'],b'',tarfile.SYMTYPE)])
  with self.assertRaises(ValueError):V.verify_archive(p,rows)
  p=d/'wrong-bytes.tar.xz';items=[(x['member'],b'x'*x['bytes'],tarfile.REGTYPE) for x in rows];archive(p,items)
  with self.assertRaises(ValueError):V.verify_archive(p,rows)
 def test10_root_readme_drift_refuses_success_index(self):
  s,d=fixture('readme-drift');verify=V.verify_archive
  def changed(*args):r=verify(*args);(d/'README.md').write_bytes(b'changed synthetic root');return r
  with patch.object(V,'verify_archive',side_effect=changed):
   with self.assertRaises(ValueError):V.retain(s,d,'2026-10-19_rootdrift_v001',SOURCE,preset=0)
  self.assertFalse((d/'2026-10-19_rootdrift_v001'/V.INDEX_NAME).exists())
 def test11_bad_batch_missing_selected_and_full_index_omission_rejected(self):
  s,d=fixture('bad-input')
  for name in ('../old','2026-/old','2026-x:ads','2026-x.'):
   with self.assertRaises(ValueError):V.retain(s,d,name,SOURCE,preset=0)
  with self.assertRaises(ValueError):V.retain(s,d,'2026-10-19_select_v001',SOURCE,selected=['missing'],kind='sample_fixture')
  with self.assertRaises(ValueError):V.retain(s,d,'2026-10-19_falsefull_v001',SOURCE,selected=['index.json'],kind='full')
  r=V.retain(s,d,'2026-10-19_good_v001',SOURCE,preset=0);index=d/'2026-10-19_good_v001'/V.INDEX_NAME
  altered=dict(r);altered['files']=r['files'][:-1];V.write_new(index.parent/'poison-index.json',altered)
  with self.assertRaises(ValueError):V.verify_index(index.parent/'poison-index.json')

if __name__=='__main__':
 RUN.mkdir(parents=True,exist_ok=False);before=V.pin(V.__file__)
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 result=dict(schema='native-solid-retention-host-tests-v001',tests=r.testsRun,failures=len(r.failures),errors=len(r.errors),
  passed=r.wasSuccessful() and before==V.pin(V.__file__),tool_before=before,tool_after=V.pin(V.__file__),
  synthetic_fixtures_only=True,actual_E_written=False,existing_real_source_modified=False,UE_started=False,View=False,FinalAccepted=False)
 V.write_new(RUN/'host-tests-result.json',result);print(json.dumps(dict(result=V.pin(RUN/'host-tests-result.json'),passed=result['passed'])))
 raise SystemExit(0 if result['passed'] else 1)
