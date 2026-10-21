"""Preserve explicit frozen candidates before any diagnostic image is viewed."""
from pathlib import Path
import hashlib,json,shutil

R=Path('F:/Ourgame')
B=R/'source-assets/production/fairytale-armor-sword-ready-v002'
A=R/'过程图稿与视频/2026-10-16_低位持剑胸肩整数配准候选_v001'
assert not A.exists(),A
(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(p,d):
    assert not p.exists(),p
    p.write_text(d if isinstance(d,str) else json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
specs=[('near',B/'nearshoulder-extraction-v002/extracted-freeze-v001.json','219f7cf3fb5e9b50a9085f65d86258bc82f9901c6520260b69d207c4efa20921'),
       ('far',B/'farshoulder-extraction-v002/extracted-freeze-v001.json','aa39abab817544b14c1c29783e01185a48bf794ec38eedefaa5a1d531afd4f06'),
       ('chest',B/'chest-registration-proposed-v001/registered-freeze-v001.json','0684d7d9b9c3a0524f3d53b4b17f529292bd4b3a80e2199c3a36cf2fbc7b3cfc')]
entries=[]
for group,pin,sha in specs:
    assert desc(pin)['sha256']==sha
    freeze=json.loads(pin.read_text(encoding='utf-8-sig'))
    rows=freeze['files']+[desc(pin)]
    for i,row in enumerate(rows):
        source=Path(row['path']);actual=desc(source)
        assert actual['bytes']==row['bytes'] and actual['sha256']==row['sha256'],source
        target=A/'原件'/f'{group}-{i:03d}-{source.name}'
        assert not target.exists();shutil.copy2(source,target)
        assert desc(target)['sha256']==actual['sha256']
        entries.append({'source':actual,'retained':desc(target),'group':group})
for i in range(4):
    source=B/f'chest-registration-proposed-v001/assemblies/frame-{i}-chest-only-proposed.png'
    target=A/'展示副本'/f'chest-only-proposed-{i}.png';shutil.copy2(source,target)
    assert desc(source)['sha256']==desc(target)['sha256']
write(A/'index.json',{'schema':'ready-armor-candidates-pre-view-retention-v1','files':entries,
    'status':'Unreviewed chest integer registration and two shoulders extraction; not UE import or equipment acceptance',
    'far_original_central_feature_contract_met':False,'formal_complete_units':0,
    'source_pixels_untouched':True,'retention_not_acceptance':True})
write(A/'README.md','# 低位持剑胸肩候选\n\n161胸片中央boss整数平移候选，以及162近肩／163远肩标准提取。原始RGBA、共同提取比例和既有curated保持；本批保存后才开始审图。远肩没有按原提示生成中央boss，原合同保持未通过，后续若用真实顶带铆钉必须另列试装设计。尚未导入UE，也未完成实际四甲或动作适配。\n')
print(json.dumps({'archive':A.as_posix(),'frozen_source_files':len(entries),'bytes':sum(e['retained']['bytes'] for e in entries),'sha_mismatches':0},ensure_ascii=False))
