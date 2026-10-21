"""Read real PNG CRC/pixels, hashes, original tracks and archives; source proof only."""
from pathlib import Path
import ast,hashlib,importlib.util,json,struct,zlib
from PIL import Image,ImageChops
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
EXPECTED={'primary':'0acc811b8633f8d3b165ea588ad38c8f95372f4bd13ab37ec7ece7174ecc0a82','reload':'963d74e304894088492b205fb9b113b0e5b6d9acf52785724c6d400271722002','ready_idle':'093d6b15a44dadc485b28584784c888b2df7f1a88261891632ef836e128925a1'}
def png_crc(p):
 data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';offset=8;chunks=0
 while offset+12<=len(data):
  n=struct.unpack_from('>I',data,offset)[0];kind=data[offset+4:offset+8];payload=data[offset+8:offset+8+n];assert zlib.crc32(kind+payload)&0xffffffff==struct.unpack_from('>I',data,offset+8+n)[0];offset+=n+12;chunks+=1
  if kind==b'IEND':assert offset==len(data);return chunks
 raise AssertionError('No PNG IEND')
def main():
 manifest_checks=[];armor_paths=set();armor_hashes=set();body_paths=set();body_hashes=set();mask_checks=set();crc_chunks=0
 for clip,digest in EXPECTED.items():
  q=P/f'manifests/import-XBW-{clip}-four-armors-v001.json';assert r.sha(q)==digest;m=r.read(q);assert m['frozen'] and not m['runtime_verified']
  body=r.read(Path(m['source_body_contract_path']));assert r.sha(Path(m['source_body_contract_path']))==m['source_body_contract_sha256']
  assert m['common_body']==body['frames'];n=0
  for f in m['common_body']:
   assert f['ground_root_px']==[256,472]
   parts=[]
   for layer in ['body_far','body_support','body_near']:
    p=Path(f[layer]['path']);assert r.sha(p)==f[layer]['sha256'];body_paths.add(str(p));body_hashes.add(r.sha(p));parts.append(Image.open(p).convert('RGBA'))
   rebuilt=parts[0].copy();rebuilt.alpha_composite(parts[1]);rebuilt.alpha_composite(parts[2]);p=Path(f.get('source_body_path',f.get('body_source')));assert rebuilt.tobytes()==Image.open(p).convert('RGBA').tobytes()
  for armor,frames in m['armors'].items():
   for row in frames:
    source=Image.open(row['source_path']).convert('RGBA');assert r.sha(Path(row['source_path']))==row['source_sha256'];protected=Image.open(row['selection_masks']['protected']['path']).convert('L')
    for mask in row['selection_masks'].values():assert r.sha(Path(mask['path']))==mask['sha256'];mask_checks.add(mask['path'])
    for layer in ['armor_far','armor_near']:
     p=Path(row[layer]['path']);assert r.sha(p)==row[layer]['sha256'];crc_chunks+=png_crc(p);im=Image.open(p);im.load();assert im.mode=='RGBA' and im.size==(512,512) and im.getchannel('A').getextrema()==(0,255)
     assert list(im.getchannel('A').getbbox())==row[layer]['bbox_px'] and all(im.getpixel(t)[3]==0 for t in[(0,0),(511,0),(0,511),(511,511)])
     assert not ImageChops.multiply(im.getchannel('A'),protected).getbbox()
     assert all(a==b for a,b in zip(im.get_flattened_data(),source.get_flattened_data()) if a[3])
     for body_layer in ['body_near','body_support']:
      hand=Image.open(m['common_body'][row['index']][body_layer]['path']).convert('RGBA');assert not ImageChops.multiply(im.getchannel('A'),hand.getchannel('A')).getbbox()
     armor_paths.add(str(p));armor_hashes.add(r.sha(p));n+=1
  assert n==m['armor_texture_count_new'];manifest_checks.append({'clip':clip,'manifest_path':str(q),'sha256':digest,'actual_armor_files':n,'common_body_referenced_files':len(m['common_body'])*3,'runtime_verified':False})
 ledger=r.read(r.LEDGER);assert ledger['requested_count']==115 and ledger['current_window']['requested_count']==19 and ledger['remaining_batch_requests']==5
 assert not any(e['status']=='requested' for e in ledger['requests']);raw_paths=0
 for e in ledger['requests']:
  if 104<=e['request_number']<=115:
   for p in [e['tool_original_path'],e['raw_path']]+e['archive_paths']:assert r.sha(Path(p))==e['sha256'];raw_paths+=1
 archive_paths=0;archive_bytes=0
 for folder in r.ARCHIVES:
  for item in r.read(folder/'index.json')['files']:
   assert r.sha(Path(item['source']))==item['sha256']
   for category in ['原件','展示副本']:
    p=folder/category/item['relative'];assert p.stat().st_size==item['bytes'] and r.sha(p)==item['sha256'];archive_paths+=1;archive_bytes+=p.stat().st_size
 frozen={
  P.parent/'first-batch-weapon-actions-v001/manifests/import-XBW-ready-idle-v001.json':'21c8ff90c59c411bfdbcabcfee0292881d77e4e652cc2fde46cab35e99373813',
  P.parent/'first-batch-weapon-actions-v001/manifests/import-XBW-primary-v001.json':'79fd2508eabfdab26f4dcb1cc21682d08b2518d37bbc0111fc38655869eeb11f',
  P.parent/'first-batch-weapon-actions-v001/manifests/import-XBW-reload-four-keyposes-v001.json':'9a0f99a5b32a5b898b9fa98d4b40812daf5e532a73954f13df91a7c166297ee8',
  P.parent/'first-batch-weapon-actions-v001/manifests/weapon-state-lifecycle-v001.json':'94f2d3b6163f620babe8d5d550cacbeb7204ca69f8b3942ebdc27f512e72fffe',
  P.parent/'first-batch-stone-bat-v001/manifests/import-stone-bat-subset-v002.json':'de293cd758a6112e7f3d26e15821ebbb308d203c980b07a7107780254e09cf45',
  P.parent/'scene-exploration-props-v001/manifests/import-scene-exploration-props-v001.json':'a6eb21c81c1c2a29ac703454ee03318604e4cf5c96bde8070540e3f8c2a5c969'}
 for p,digest in frozen.items():assert r.sha(p)==digest
 scripts=[]
 for p in P.glob('*.py'):ast.parse(p.read_text('utf-8'));scripts.append({'path':str(p),'sha256':r.sha(p)})
 assert len(armor_paths)==len(armor_hashes)==128 and raw_paths==72
 out=P/'reviews/XBW-armor-source-checkpoint-v001.json';assert not out.exists();r.write(out,{'schema':'XBW-armor-real-source-verification-v1','utc':r.now(),'manifests':manifest_checks,'actual_new_armor_paths':len(armor_paths),'actual_unique_armor_sha256':len(armor_hashes),'reused_body_paths':len(body_paths),'unique_reused_body_track_hashes':len(body_hashes),'native_PNG_CRC_chunks_verified':crc_chunks,'mask_paths_verified':len(mask_checks),'all_armor_overlap_with_frozen_distal_hand_pixels_zero':True,'all_body_tracks_reconstruct_exact_original_pixels':True,'new_raw_tool_F_E_paths_verified':raw_paths,'F_E_existing_archived_paths_verified':archive_paths,'F_E_existing_archived_bytes_verified':archive_bytes,'task_generation_calls':12,'task_call_limit':12,'ledger_requested_completed':115,'window5_used':19,'window5_remaining':5,'pending':0,'prior_contracts_unchanged':[{'path':str(p),'sha256':d} for p,d in frozen.items()],'AST_scripts':scripts,'engine_run':False,'runtime_verified':False,'full_armor_accepted':False,'errors':[]});r.archive(out,out.relative_to(P),'actual_final_XBW_armor_source_hash_pixel_hand_overlap_and_archive_audit_not_runtime')
 report=P/'XBW-armor-production-report-v001.md';r.archive(report,report.relative_to(P),'12call_XBW_four_armor_source_candidates_honest_partial_cloth_and_runtime_report')
 r.archive(Path(__file__),Path('scripts')/Path(__file__).name,'actual_source_verification_script')
 print(json.dumps({'audit_path':str(out),'audit_sha256':r.sha(out),'report_sha256':r.sha(report),'armor_paths':len(armor_paths),'unique_armor_hashes':len(armor_hashes),'reused_body_paths':len(body_paths),'unique_body_track_hashes':len(body_hashes),'archive_paths_verified':archive_paths,'archive_bytes_verified':archive_bytes,'requests':115,'task_calls':12,'runtime_verified':False}))
if __name__=='__main__':main()
