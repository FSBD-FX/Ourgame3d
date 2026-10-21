from pathlib import Path
import importlib.util,hashlib,json
from PIL import Image,ImageChops,ImageFilter
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
s=importlib.util.spec_from_file_location('trace',P/'extract-primary1-other-armors-v007.py');tr=importlib.util.module_from_spec(s);s.loader.exec_module(tr)
prior=P/'manifests/import-armor-primary1-LGT-v001.json';d=r.read(prior);c=r.read(P/'manifests/primary1-other-armors-candidate-v007.json');files=[]
common_digest=hashlib.sha256(json.dumps(d['common_body'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
for key,rows in c['armors'].items():
 out=[]
 for row,b in zip(rows,d['common_body']):
  p=Path(row['armor_front']['path']);assert r.sha(p)==row['armor_front']['sha256'];im=Image.open(p).convert('RGBA');a=im.getchannel('A');assert im.size==(512,512) and a.getextrema()==(0,255)
  corners=[list(im.getpixel(pt)) for pt in [(0,0),(511,0),(0,511),(511,511)]];assert all(v[3]==0 for v in corners)
  src=Image.open(row['source_path']).convert('RGBA');assert all(x==y for x,y in zip(im.get_flattened_data(),src.get_flattened_data()) if x[3])
  # No armor opacity in the traced original head/hands/forearms/waist regions;
  # no opacity in the explicit non-weapon wrist continuation either.
  pose=tr.tr.POSES[row['index']]
  for name in ['head','weapon_hand','other_hand','belt','pouch']:
   m=tr.tr.mask(pose[name]);assert ImageChops.multiply(a,m).getbbox() is None
  assert ImageChops.multiply(a,tr.union([tr.OTHER_WRISTS[row['index']]])).getbbox() is None
  copies=r.archive(p,p.relative_to(P),'frozen_four_armor_P1_visible_surface_candidate');assert all(r.sha(Path(q))==r.sha(p) for q in copies)
  record={'path':str(p),'sha256':r.sha(p),'canvas_px':[512,512],'mode':'RGBA','alpha_extrema':list(a.getextrema()),'corner_rgba':corners,'bbox_px':list(a.getbbox()),'four_archive_hashes_match':True}
  files.append(record);out.append({'index':row['index'],'armor_back':None,'armor_back_visibility':'no_separate_visible_back_classification_no_synthetic_hidden_pixels','armor_front':record,'root_px':b['root_px'],'grip_px':b['grip_px'],'mask_path':row['mask_path'],'mask_sha256':row['mask_sha256'],'every_visible_pixel_equals_native_source':True,'native_source_path':row['source_path'],'native_source_sha256':row['source_sha256'],'pruned_detached_fragment_sizes':row['pruned_detached_fragment_sizes']})
 d['armors'][key]=out
assert len(files)==18
for n in [54,55,56]:
 e=next(e for e in r.read(r.LEDGER)['requests'] if e['request_number']==n);prompt=Path(e['prompt_path']);r.archive(prompt,prompt.relative_to(P),'frozen_native_armor_P1_prompt')
 d['source_provenance'].append({'request_number':n,'raw_path':e['raw_path'],'raw_sha256':e['sha256'],'prompt_path':str(prompt),'prompt_sha256':r.sha(prompt),'references':e['references'],'backend':'image_gen.imagegen','host_fee_usd':None})
script=P/'extract-primary1-other-armors-v007.py';r.archive(script,Path('scripts')/script.name,'frozen_three_armor_P1_surface_selection')
d.update(version=2,status='four_armor_P1_visible_surface_candidates_for_runtime_preview',unfulfilled_armors=[],runtime_texture_count_total=36,runtime_texture_count_new_delta=18,previous_frozen_import=str(prior),previous_frozen_import_sha256=r.sha(prior),unique_common_pose_count=6,armor_pose_samples=24,common_body_canonical_json_sha256=common_digest)
d['selection_manifest_other_armors']=str(P/'manifests/primary1-other-armors-candidate-v007.json');d['selection_manifest_other_armors_sha256']=r.sha(P/'manifests/primary1-other-armors-candidate-v007.json')
d['processing_sources'].append({'path':str(script),'sha256':r.sha(script)})
d['manual_visual_review']={'six_frames_each_of_four_isolated_armors_and_sword_assemblies_viewed':True,'result':'real_visible_garment_surfaces_no_head_hands_or_complete_body_layers; candidate_for_runtime_preview','selection_work':'Manual per-pose garment/hem/shin traces; exclude actual original anatomy and extended wrist shapes; 5px forearm seam clearance on MED/HVY/ROB; prune detached<=24px fragments while keeping all meaningful parts. All visible RGBA remains native source byte-identical.','limitations':['Shared foreground forearm constrains upper-sleeve coverage; undercoat may show at the 5px seam clearance.','Wearable sets include their native cuff/hem/greave-strap material borders; hidden full garments are not reconstructed.','Back is null in this P1 contract, all actually selected visible surfaces are front overlay; not an old four-layer validator pass.','Only idle and P1 currently have frozen armor candidates; P2/P3/walk and full states remain incomplete.','No runtime readability, transition, clipping, mirror,20-combination or full-armor acceptance claim.']}
d['complete_armor']=False;d['runtime_verified']=False
f=P/'manifests/import-armor-primary1-four-v002.json';assert not f.exists();r.write(f,d);r.archive(f,f.relative_to(P),'frozen_four_armor_P1_real_surface_candidate')
q=P/'reviews/import-armor-primary1-four-v002-verification.json';r.write(q,{'manifest':str(f),'manifest_sha256':r.sha(f),'common_body_identical_to_frozen_LGT_v001':common_digest,'new_delta_PNGs':18,'total_runtime_PNGs':36,'real_files':files,'new_F_E_copies_verified':72,'errors':[],'runtime_executed':False});r.archive(q,q.relative_to(P),'actual_four_armor_P1_pixel_and_archive_evidence')
print({'manifest':str(f),'sha256':r.sha(f),'new_delta_PNGs':18,'total_runtime_PNGs':36,'same_common_body_sha256':common_digest,'errors':0})
