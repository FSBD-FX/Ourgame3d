"""List real native originals; no crops, composites or rescaling are created."""
from pathlib import Path
import hashlib,json
root=Path('F:/Ourgame');a=root/'过程图稿与视频/2026-10-16_暗黑童话双肩甲明暗双向真实观察_v001'
report=json.loads((a/'原件/runtime-report.json').read_text(encoding='utf-8-sig'));files=sorted((a/'原件').glob('MovieFrame*.png'))
assert len(files)==len(report['observations'])==756
groups={}
for i,r in enumerate(report['observations']):
 only='near' if r['input_N'] else 'far' if r['input_F'] else 'both'
 key=(r['hero_dark_position'],r['chest_visible_choice'],r['hero']['facing'],only,r['hero']['frame'])
 groups.setdefault(key,[]).append((i,r))
assert len(groups)==48
selected=[]
for key,rows in sorted(groups.items()):
 i,r=rows[len(rows)//2];p=files[i];data=p.read_bytes()
 selected.append({'dark':key[0],'shoulders_visible':key[1],'facing':key[2],'only':key[3],'frame':key[4],
 'observation_index':i,'wall_offset_s':r['wall_offset_s'],'path':p.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
out=root/'docs/production/first-batch-v2/evidence/fairytale-shoulder-runtime-v001';out.mkdir(parents=True,exist_ok=True)
p=out/'selected-original48-v001.json';assert not p.exists()
p.write_text(json.dumps({'retained_before_view':'E106771files2801563708B/twoSHA0','selection_only_not_review':True,'frames':selected,'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'manifest':p.as_posix(),'count':48,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},ensure_ascii=False))
