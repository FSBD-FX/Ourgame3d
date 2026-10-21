"""Read real pixels, aliases, source retention and immutable prior manifests."""
from pathlib import Path
import ast,importlib.util,json,math
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
ledger=r.read(r.LEDGER);assert ledger['requested_count']==101 and len(ledger['requests'])==101 and ledger['current_window']['number']==5 and ledger['current_window']['requested_count']==5 and ledger['remaining_batch_requests']==19
assert not any(x['status']=='requested' for x in ledger['requests'])
source_retention=[]
for entry in ledger['requests']:
 if entry['request_number']<91:continue
 paths=[entry['tool_original_path'],entry['raw_path']]+entry['archive_paths'];assert len(paths)==6
 for p in paths:assert r.sha(Path(p))==entry['sha256']
 source_retention.append({'request':entry['request_number'],'sha256':entry['sha256'],'verified_paths':paths})
manifest_path=P/'manifests/import-stone-bat-subset-v002.json';manifest=r.read(manifest_path);assert r.sha(manifest_path)=='de293cd758a6112e7f3d26e15821ebbb308d203c980b07a7107780254e09cf45'
actions=manifest['actions'];files={};logical=0
def resolve(frame,trail=()):
 if 'reference_action' not in frame:return frame
 key=(frame['reference_action'],frame['reference_play_index']);assert key not in trail
 assert frame['alias_no_new_PNG'] is True
 return resolve(actions[key[0]]['frames'][key[1]],trail+(key,))
for key,action in actions.items():
 assert action['frame_count']==len(action['frames'])
 for frame in action['frames']:
  logical+=1;f=resolve(frame);p=Path(f['path']);assert r.sha(p)==f['sha256'];im=Image.open(p);assert im.mode=='RGBA' and im.size==(512,512) and im.getchannel('A').getextrema()==(0,255)
  assert all(im.getpixel(pt)[3]==0 for pt in[(0,0),(511,0),(0,511),(511,511)]) and all(math.isfinite(x) and 0<=x<=512 for x in f['body_root_px'])
  copies=r.archive(p,p.relative_to(P),'postreview_reverified_frozen_candidate_png_no_image_edits');assert len(copies)==4 and all(r.sha(Path(x))==f['sha256'] for x in copies)
  files[str(p)]=f['sha256']
assert logical==35 and len(files)==27 and len(set(files.values()))==27
prior=[]
for p,digest in[(P/'manifests/import-stone-bat-subset-v001.json','38dc4d88880b49239e5ae0416e4e98216009362777763b27932994c8dd6dc89b'),
 (P.parent/'first-batch-weapon-actions-v001/manifests/import-XBW-primary-v001.json','79fd2508eabfdab26f4dcb1cc21682d08b2518d37bbc0111fc38655869eeb11f'),
 (P.parent/'first-batch-weapon-actions-v001/manifests/import-XBW-reload-four-keyposes-v001.json','9a0f99a5b32a5b898b9fa98d4b40812daf5e532a73954f13df91a7c166297ee8')]:
  assert r.sha(p)==digest;prior.append({'path':str(p),'sha256':digest,'unchanged':True})
scripts=[]
for p in sorted(P.glob('*.py')):
 ast.parse(p.read_text('utf-8'));scripts.append({'path':str(p),'sha256':r.sha(p),'ast_pass':True})
review={'schema':'visual_current_handoff_verification_v1','created_utc':r.now(),'requested_count':101,'current_window':ledger['current_window'],'remaining':19,'pending':0,
 'manifest':str(manifest_path),'manifest_sha256':r.sha(manifest_path),'actual_unique_PNGs':27,'unique_content_hashes':27,'logical_frames_with_aliases':35,'F_E_PNG_copies_verified':108,
 'native_raw_requests91through101_verified':source_retention,'native_raw_retention_path_count':66,'source_PNG_hashes':files,'prior_frozen_manifests':prior,'script_AST_checks':scripts,
 'manual_source_review':'all_new_raw_images_viewed_after_F_Eretention; right_origin_assembly5pages_and_correct_percell_left_v0035pages_viewed',
 'candidate_quality_approved_for_formal_or_runtime':False,'UE_or_UBT_executed':False,'full15_target_completed':False,'errors':[]}
q=P/'reviews/current-handoff-verification-v001.json';assert not q.exists();r.write(q,review);r.archive(q,q.relative_to(P),'actual_postreview_source_pixels_alias_hash_and_immutable_baseline_verification')
print(json.dumps({'report':str(q),'sha256':r.sha(q),'PNG27_F_E108':True,'alias35_valid':True,'raw66paths_valid':True,'scripts_AST':len(scripts),'prior_frozen_unchanged':len(prior),'ledger':101,'window5_used':5,'remaining':19,'errors':[]}))
