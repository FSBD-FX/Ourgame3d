"""Only exact frozen pixels become pose references; no creative art or body transform."""
from pathlib import Path
import importlib.util,json,shutil
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
B=P.parent/'first-batch-weapon-actions-v001';A=P.parent/'first-unit-armor-layers-v001'
ledger=r.read(r.LEDGER);assert ledger['requested_count']==103 and ledger['current_window']['requested_count']==7 and ledger['remaining_batch_requests']==17
assert not any(x['status']=='requested' for x in ledger['requests'])
checks={'ready-idle':'21c8ff90c59c411bfdbcabcfee0292881d77e4e652cc2fde46cab35e99373813','primary':'79fd2508eabfdab26f4dcb1cc21682d08b2518d37bbc0111fc38655869eeb11f','reload-four-keyposes':'9a0f99a5b32a5b898b9fa98d4b40812daf5e532a73954f13df91a7c166297ee8'}
refs=[]
for action,digest in checks.items():
 q=B/f'manifests/import-XBW-{action}-v001.json';assert r.sha(q)==digest;d=r.read(q)
 cols=3 if len(d['frames'])==6 else 2;rows=2
 sheet=Image.new('RGBA',(cols*512,rows*512),(255,0,255,255));sources=[]
 for i,f in enumerate(d['frames']):
  path=Path(f.get('source_body_path',f.get('body_source')));expected=f.get('source_body_sha256',f.get('body_source_sha256'));assert r.sha(path)==expected
  image=Image.open(path).convert('RGBA');assert image.size==(512,512);sheet.alpha_composite(image,((i%cols)*512,(i//cols)*512));sources.append({'index':i,'path':str(path),'sha256':expected,'root_px':f['ground_root_px']})
 out=P/f'references/frozen-XBW-{action}-pose-plate-v001.png';out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists();sheet.convert('RGB').save(out);r.archive(out,out.relative_to(P),'exact_frozen_XBW_body_pose_reference_no_geometry_transform')
 refs.append({'action':action,'path':str(out),'sha256':r.sha(out),'canvas_px':list(sheet.size),'sources':sources,'manifest_path':str(q),'manifest_sha256':digest,'transforms':'none'})
for key in ['LGT','MED','HVY','ROB']:
 src=A/f'reviews/idle-ARM-{key}-001-isolated-armor-v003.png';im=Image.open(src).convert('RGBA');out=P/f'references/ARM-{key}-001-native-style-v001.png';assert not out.exists();im.crop((0,0,512,512)).save(out);r.archive(out,out.relative_to(P),'existing_native_armor_material_style_only_not_XBW_pose')
 refs.append({'armor_id':f'ARM-{key}-001','path':str(out),'sha256':r.sha(out),'source_path':str(src),'source_sha256':r.sha(src),'transform':'integer_crop_first_existing512cell_no_resample'})
out=P/'references/reference-sources-v001.json';r.write(out,{'schema':'XBW-armor-frozen-inputs-v1','source_contracts_unchanged':checks,'references':refs,'initial_requested_count':103,'max_new_calls_this_task':12,'body_pose_authority':'frozen_native_source_only','runtime_verified':False});r.archive(out,out.relative_to(P),'frozen_XBW_pose_and_existing_armor_style_provenance')
print(json.dumps({'pose_plates':3,'style_cells':4,'initial_requests':103,'max_calls':12}))
