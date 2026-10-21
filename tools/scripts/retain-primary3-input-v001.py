from pathlib import Path
import hashlib,json,shutil

root=Path('F:/Ourgame');base=root/'source-assets/production/fairytale-sword-primary3-v001'
freeze=base/'preparation-freeze-v001.json'
f=json.loads(freeze.read_text(encoding='utf-8'))
out=root/'过程图稿与视频/2026-10-16_军剑第三段终结斩输入_v001'
assert not out.exists()
rows=[]
for item in f['files']:
    p=Path(item['path']);data=p.read_bytes()
    assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'],p
for item in f['files']+[{'path':freeze.as_posix()}]:
    p=Path(item['path']);target=out/'原件'/p.relative_to(base)
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    assert p.read_bytes()==target.read_bytes()
    rows.append({'source':p.as_posix(),'retained':target.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
draft=json.loads((base/'handoffs/primary3-native-input-draft-v001.json').read_text(encoding='utf-8'))
for i,ref in enumerate(draft['rows'][0]['reference_images_in_order']):
    p=Path(ref['file']['path']);target=out/'展示副本'/f'{i:02d}-{p.name}'
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    assert p.read_bytes()==target.read_bytes()
(out/'source-version-status-index.json').write_text(json.dumps({'files':rows,'status':'Input draft only; not generated; root visual review pending; no measured palms or sockets','formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'README.md').write_text('第三段终结斩输入草稿；原件与未修改展示副本。仅六相660ms设计输入，尚未生成或验收。\n',encoding='utf-8')
print(json.dumps({'archive':out.as_posix(),'originals':len(rows),'generation_called':False},ensure_ascii=False))
