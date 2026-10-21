from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame');T=R/'tools/scripts';B=R/'source-assets/production/fairytale-sword-primary2-runtime-v002/axis1-correction-v001'
receipt=R/'UnrealGame/Saved/Bootstrap/sword-primary2-v002-import-20261016-085358-730896.json'
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
d=json.loads(receipt.read_text(encoding='utf-8-sig'));assert d['success'] and d['actual_count']==d['saved_count']==6 and d['old_packages_unchanged']==989
pointer=B/'manifests/actual-import-receipt-ref.json';assert not pointer.exists();pointer.write_text(json.dumps(desc(receipt),indent=2)+'\n',encoding='utf-8')
p=T/'verify-sword-primary2-fit-v002.py';q=T/'verify-sword-primary2-fit-v003.py';assert not q.exists()
s=p.read_text(encoding='utf-8').replace('ue_sword_primary2_v001_checks.py','ue_sword_primary2_v002_checks.py')
start=s.index("arc_path=ROOT/");end=s.index('if a.preflight_only:',start)
s=s[:start]+"axes=[x['axis_design_only'] for x in markers['markers']]\n"+s[end:]
s=s.replace("arc['axis_design_only'][frame]","axes[frame]").replace("old983_unchanged","old989_unchanged").replace("source989_packages_verified","source995_packages_verified").replace('runtime-verification-v002.json','runtime-verification-v003.json')
q.write_text(s,encoding='utf-8')
p=T/'verify-sword-primary2-fit-v002.ps1';q=T/'verify-sword-primary2-fit-v003.ps1';assert not q.exists()
s=p.read_text(encoding='utf-8').replace('$Version=2','$Version=3').replace('verify-sword-primary2-fit-v002.py','verify-sword-primary2-fit-v003.py').replace('native169 Primary2','native171 Primary2')
assert s.count("'-DungeonFairytaleSwordPrimary2ArcPreview'")==1
s=s.replace("'-DungeonFairytaleSwordPrimary2ArcPreview'","'-DungeonFairytaleSwordPrimary2ArcPreview','-DungeonFairytaleSwordPrimary2BodyPreview'")
q.write_text(s,encoding='utf-8')
p=T/'postprocess-sword-primary2-fit-v002.py';q=T/'postprocess-sword-primary2-fit-v003.py';assert not q.exists()
s=p.read_text(encoding='utf-8').replace('钟盔军剑第二段真实连击试装_v002','钟盔军剑第二段真实连击试装_v003').replace('runtime-verification-v002.json','runtime-verification-v003.json').replace('tool-postprocess-sword-primary2-fit-v002.py','tool-postprocess-sword-primary2-fit-v003.py').replace('Native169','Native171')
q.write_text(s,encoding='utf-8')
p=T/'freeze-sword-primary2-fit-build-v002.py';q=T/'freeze-sword-primary2-fit-build-v003.py';assert not q.exists()
s=p.read_text(encoding='utf-8');anchor='rows = []\n';assert s.count(anchor)==1
extra='''# Native171 new six-body namespace, source measurements, corrected axis history and actual import.
p2_new = root / 'source-assets/production/fairytale-sword-primary2-runtime-v002'
paths.extend(p for p in p2_new.rglob('*') if p.is_file())
paths.extend((root / 'UnrealGame/Saved/Bootstrap').glob('sword-primary2-v002-import-*.json'))
paths.extend(root / 'tools/scripts' / name for name in (
    'ue-import-sword-primary2-v002.py','ue_sword_primary2_v002_checks.py','import-sword-primary2-v002.ps1',
    'verify-sword-primary2-fit-v003.py','verify-sword-primary2-fit-v003.ps1','postprocess-sword-primary2-fit-v003.py'))
paths.extend(root / 'tools/scripts' / name for name in (
    'verify-run-pristine-two-process-v002.py','verify-run-pristine-two-process-v002.ps1'))
'''
s=s.replace(anchor,extra+anchor);q.write_text(s,encoding='utf-8')
print(json.dumps({'actual_import_pointer':desc(pointer),'new_tools':[desc(T/n) for n in ['verify-sword-primary2-fit-v003.py','verify-sword-primary2-fit-v003.ps1','postprocess-sword-primary2-fit-v003.py','freeze-sword-primary2-fit-build-v003.py']]},ensure_ascii=False))
