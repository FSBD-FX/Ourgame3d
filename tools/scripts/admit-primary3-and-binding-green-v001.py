from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');S=R/'UnrealGame/Source/CodexDungeon';B=R/'source-assets/production/fairytale-sword-primary3-runtime-v001';D=B/'source-draft-v001';I=R/'source-assets/production/fairytale-sword-equipment-binding-v001/implementation-v001'
def desc(p):
    d=p.read_bytes();return {'path':p.as_posix(),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
sf=D/'source-freeze-v001.json';assert desc(sf)['sha256']=='7333206244801590a19b0004dfd935523656e76e96a803392f303fa0d71656a0'
for pin in json.loads(sf.read_text(encoding='utf-8'))['files']:assert desc(R/pin['path'])==dict(pin,path=(R/pin['path']).as_posix())
gf=I/'implementation-freeze-v001.json';assert desc(gf)['sha256']=='1051c074d3c856b5078d5bbf337a30db9a278b750ad5b4e6f7bcdaa21461c06d'
for pin in json.loads(gf.read_text(encoding='utf-8'))['files']:
    a=desc(I/pin['path']);assert a['bytes']==pin['bytes'] and a['sha256']==pin['sha256']
for n in ['DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleSwordProbe.cpp']:assert (S/n).read_bytes()==(D/'source-before'/n).read_bytes()
assert desc(S/'DungeonFairytaleSwordEquipmentBinding.cpp')['sha256']=='c3811e611520638083f60e3391cc220549e01b8ab038eb6a38fbcccd712ba651'
assert desc(S/'Tests/DungeonFairytaleSwordEquipmentBindingTests.cpp')['sha256']=='174593b8f156cf0e78c7b031c375d5a7234875cf2a6b92ba020cb78f61fa8877'
inl=B/'data/DungeonFairytaleSwordPrimary3V001.inl';assert desc(inl)['sha256']=='6749343b607b21ae5d7d1b8d1bf959b67324d13b85c7f6b37f70097088116054' and not (S/inl.name).exists()
red=R/'UnrealGame/Saved/Automation/FirstRoom-20261016-191319/index.json';rr=json.loads(red.read_text(encoding='utf-8-sig'));assert rr['failed']==3 and rr['succeeded']==0
errors=[e['event']['message'] for t in rr['tests'] for e in t['entries'] if e['event']['type']=='Error'];assert len(errors)==11 and all('actual binding is implemented' in e or 'Pure seam must first accept' in e for e in errors)
O=B/'root-source-green-admission-v001';assert not O.exists();O.mkdir();rows=[]
jobs=[(D/'candidate-source'/n,S/n) for n in ['DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleSwordProbe.cpp']]+[(I/'candidate-source/DungeonFairytaleSwordEquipmentBinding.cpp',S/'DungeonFairytaleSwordEquipmentBinding.cpp'),(inl,S/inl.name)]
for p,q in jobs:
    if q.exists():shutil.copy2(q,O/('before-'+q.name))
    rows.append({'candidate':desc(p),'destination':q.as_posix(),'before':desc(q) if q.exists() else None})
for p,q in jobs:shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
for row in rows:row['actual_source']=desc(Path(row['destination']))
receipt=R/'UnrealGame/Saved/Bootstrap/sword-armor-primary3-v001-import-20261016-112045-451279.json';ri=json.loads(receipt.read_text(encoding='utf-8-sig'));assert ri['success'] and ri['actual_count']==ri['saved_count']==48 and ri['old_packages_unchanged']==1037
ref=B/'manifests/actual-import-receipt-ref.json';assert not ref.exists();ref.write_text(json.dumps(desc(receipt),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'source-admission.json').write_text(json.dumps({'files':rows,'P3_source_freeze':desc(sf),'resolver_implementation_freeze':desc(gf),'actual_cleanRED':desc(red),'cleanRED_errors_all_honest_stub_positive':11,'import_actual':desc(receipt),'scope':'Root reviewed minimal P3 flags, true kernelStage2, unchanged lower transform/failclosed and oldinput branches; resolver exact committed identity checks after cleanRED. No accepted visual motion or equipment rendering follows until actual build/tests/native draw.','compiled':False,'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'source_files':len(rows),'actual_saved_textures':48,'production_total':1037+48,'cleanRED':11},ensure_ascii=False))
