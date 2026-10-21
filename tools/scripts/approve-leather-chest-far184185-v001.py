from pathlib import Path
import json,hashlib
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003/row-correction-v002'
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):
 assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=B/'lgt-ready-correction-input-draft-v002.json';assert desc(p)['sha256']=='cbe04bb8249fa4eaa18745169250a89b232a24fbfc0195a1fb3e7f1c537427a5'
v=json.loads(p.read_text(encoding='utf-8-sig'));rows=[]
for c,n in [('Chest',184),('FarShoulder',185)]:
 row=next(r for r in v['rows'] if r['component']==c)
 assert row['generation_ready'] is False and row['standard_prepare_exit_code']==0 and row['reference_count']==1
 assert row['frame_count']==4 and row['durations_ms']==[167]*4 and row['future_component_A']==[None]*4
 assert desc(Path(row['prompt']['path']))==row['prompt']
 for ref in row['reference_images_in_order']:assert desc(Path(ref['file']['path']))==ref['file']
 row['generation_ready']=True;row['native_request_number']=n;rows.append(row)
review=B/'root-chest-far-edit-review184185-v001.json'
write(review,dict(source_draft=desc(p),actual_old_raw_viewed_after_E_retention=['180/E255','182/E257'],approval='Two single-target native edits:Chest remove both caps/undercloth but keep leather chest/waist/pouch;Far keep only each image-RIGHT small cap, no torso/collar/pouch. Same actual perspectives. No local semantic crop, futureA unknown, no runtime acceptance.',formal_complete_units=0))
v['rows']=rows;v['root_input_review']=desc(review);write(B/'lgt-chest-far-edit-approved184185-v003.json',v)
print(json.dumps(dict(approved_rows=2,planned_numbers=[184,185],futureA=None),ensure_ascii=False))
