from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame');T=R/'tools/scripts';B=R/'source-assets/production/fairytale-armor-sword-primary2-runtime-v001'
receipt=R/'UnrealGame/Saved/Bootstrap/sword-armor-primary2-v001-import-20261016-095757-471989.json'
def d(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def new(p,v):
 assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v=json.loads(receipt.read_text(encoding='utf-8-sig'));assert v['success'] and v['actual_count']==v['saved_count']==42 and v['old_packages_unchanged']==995
new(B/'manifests/actual-import-receipt-ref.json',d(receipt))
s=(T/'verify-sword-primary2-fit-v003.py').read_text(encoding='utf-8')
anchor="markers=json.loads(Path(second['marker_json']['path']).read_text(encoding='utf-8-sig'))"
assert s.count(anchor)==1
s=s.replace(anchor,"second_armor=module('fit_second_armor','ue_sword_armor_primary2_v001_checks.py').preflight(False)\n"+anchor)
s=s.replace("'actual_second_imported_saved':6,'old989_unchanged':True,'armor_only_ready_primary1':True","'actual_second_body_imported_saved':6,'actual_second_armor_imported_saved':42,'old995_unchanged':True,'armor_present_ready_primary1_primary2':True")
anchor="armor_first={(x['component'],x['frame']):x['object_path'] for x in primary['assets']}"
assert s.count(anchor)==1;s=s.replace(anchor,anchor+"\narmor_second={(x['component'],x['frame']):x['object_path'] for x in second_armor['assets']}")
old="        assert not d['armor_drawn'] and not d['armor_ready']\n        expected=[asset['object_path'],d['weapon'],asset['object_path']]"
assert s.count(old)==1
s=s.replace(old,"        assert d['armor_drawn'] and d['armor_ready']\n        expected=[armor_second[(c,frame)] for c in ('BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground')]+[d['weapon'],armor_second[('NearHand',frame)]]")
s=s.replace('source995_packages_verified','source1037_packages_verified').replace("'primary2_armor_present':False","'primary2_armor_present':True")
s=s.replace('Fit candidate only; second armor absent, no hit target or complete unit acceptance.','Fit candidate only; real second armor8draw stack, no hit target or complete unit acceptance.')
s=s.replace('runtime-verification-v003.json','runtime-verification-v004.json')
compile(s,'verify-sword-primary2-fit-v004.py','exec');new(T/'verify-sword-primary2-fit-v004.py',s)
s=(T/'verify-sword-primary2-fit-v003.ps1').read_text(encoding='utf-8')
s=s.replace('$Version=3','$Version=4').replace('verify-sword-primary2-fit-v003.py','verify-sword-primary2-fit-v004.py')
old="'-DungeonFairytaleSwordPrimary2BodyPreview'";assert s.count(old)==1;s=s.replace(old,old+",'-DungeonFairytaleSwordPrimary2ArmorPreview'")
s=s.replace('158Ready/Primary1 armor plus native171 Primary2 body fit. Second armor absent.','Ready/Primary1 matching armor plus native171 Primary2 body with42 body/armor textures from172/173/174. Real independent sword/armor fit.')
new(T/'verify-sword-primary2-fit-v004.ps1',s)
s=(T/'postprocess-sword-primary2-fit-v003.py').read_text(encoding='utf-8').replace('钟盔军剑第二段真实连击试装_v003','钟盔军剑第二段真实连击试装_v004').replace('runtime-verification-v003.json','runtime-verification-v004.json').replace('tool-postprocess-sword-primary2-fit-v003.py','tool-postprocess-sword-primary2-fit-v004.py')
s=s.replace('Primary2 armor is absent','Primary2 uses matching42 body/armor-layer textures').replace('actual Ready7/Primary8 stacks','actual Ready7/Primary1and2-8 stacks')
compile(s,'postprocess-sword-primary2-fit-v004.py','exec');new(T/'postprocess-sword-primary2-fit-v004.py',s)
s=(T/'freeze-sword-primary2-fit-build-v003.py').read_text(encoding='utf-8');anchor='rows = []\n';assert s.count(anchor)==1
extra="""p2_armor = root / 'source-assets/production/fairytale-armor-sword-primary2-runtime-v001'
paths.extend(p for p in p2_armor.rglob('*') if p.is_file())
paths.extend((root / 'UnrealGame/Saved/Bootstrap').glob('sword-armor-primary2-v001-import-*.json'))
paths.extend(root / 'tools/scripts' / name for name in (
    'verify-sword-primary2-fit-v004.py','verify-sword-primary2-fit-v004.ps1','postprocess-sword-primary2-fit-v004.py',
    'ue_sword_armor_primary2_v001_checks.py','ue-import-sword-armor-primary2-v001.py','import-sword-armor-primary2-v001.ps1'))
"""
s=s.replace(anchor,extra+anchor);compile(s,'freeze-sword-primary2-fit-build-v004.py','exec');new(T/'freeze-sword-primary2-fit-build-v004.py',s)
print(json.dumps(dict(actual_import_pointer=d(B/'manifests/actual-import-receipt-ref.json'),tools=[d(T/n) for n in ['verify-sword-primary2-fit-v004.py','verify-sword-primary2-fit-v004.ps1','postprocess-sword-primary2-fit-v004.py','freeze-sword-primary2-fit-build-v004.py']]),ensure_ascii=False))
