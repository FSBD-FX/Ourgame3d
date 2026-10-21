from pathlib import Path
from PIL import Image
import hashlib,json,shutil,sys
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-sword-primary3-v001/armor-input-v001';SG=Path('C:/Users/22499/.codex/skills/sprite-gen');assert Path(sys.executable).resolve()==(SG/'.venv/Scripts/python.exe').resolve()
sys.path.insert(0,str(SG));import sprite_gen.frames.extract as native
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
O=B/'feature-diagnostics-v001';assert not O.exists();O.mkdir();records=[]
for component in ['Chest','NearShoulder','FarShoulder']:
    run=B/f'run-{component.lower()}-primary3-v001';state=f'armor_{component.lower()}_sword_primary3';raw=run/f'raw/{state}.png'
    meta=json.loads((run/'frames/frames-manifest.json').read_text(encoding='utf-8'))['rows'][0]['shared_row_fit']
    keyed=native.remove_chroma_background(Image.open(raw),(0,255,0),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005)
    pieces=native.extract_component_images(keyed,6);assert pieces is not None and len(pieces)==6
    for i,piece in enumerate(pieces):
        assert hashlib.sha256(piece.tobytes()).hexdigest()==meta['raw_component_RGBA_sha256'][i]
        crop=piece.crop(piece.getbbox());assert list(crop.size)==meta['frame_records'][i]['source_component_size']
        p=O/f'{component}-component-{i}-pre-fit.png';crop.save(p);assert Image.open(p).tobytes()==crop.tobytes()
        records.append({'component':component,'frame':i,'raw':desc(raw),'pre_fit_component':desc(p),'raw_component_RGBA_sha256':meta['raw_component_RGBA_sha256'][i],'source_bbox':list(piece.getbbox()),'shared_fit':meta['frame_records'][i],'purpose':'Exact native keyed component diagnostic before existing shared fit, not enlarged/repainted asset; view physical feature then confirm original512 A.'})
index=O/'source-map-v001.json';index.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
A=R/'过程图稿与视频/2026-10-16_军剑终结斩三甲特征诊断_v001';assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
files=[Path(x['pre_fit_component']['path']) for x in records]+[index,Path(__file__).resolve()]+list(dict.fromkeys(Path(x['raw']['path']) for x in records))
for i,p in enumerate(files):
    q=A/'原件'/f'{i:03d}-{p.name}';shutil.copy2(p,q);assert q.read_bytes()==p.read_bytes();rows.append({'source':desc(p),'copy':desc(q)})
for x in records:
    p=Path(x['pre_fit_component']['path']);q=A/'展示副本'/p.name;shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
(A/'source-version-status-index.json').write_text(json.dumps({'files':rows,'status':'Unscaled native pre-fit component diagnostics; no new generation or source art/fit change. Physical feature A not accepted yet.','formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('原生标准组件未缩放特征诊断，18个原RGBA哈希与既有sharedrow记录一致；未修改/重复提取生产run。用于检查真实铆钉/孔位置，非新资源或注册验收。\n',encoding='utf-8')
print(json.dumps({'archive':A.as_posix(),'diagnostic_components':len(records),'production_run_changed':False},ensure_ascii=False))
