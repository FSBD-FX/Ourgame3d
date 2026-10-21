from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');T=R/'tools/scripts';B=R/'source-assets/production/fairytale-sword-primary2-runtime-v002/axis1-correction-v001'
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
f=B/'ready-for-root-import-freeze-v002.json';m=json.loads(f.read_text(encoding='utf-8'))
assert desc(f)['sha256']=='804a585273ebe25fef1cad364782aedf62d7ae57b404199365ee9d94d9c64a37'
for row in m['files']:assert desc(Path(row['path']))==row
manifest=B/'manifests/import-sword-primary2-v002.json';assert desc(manifest)['sha256']=='c5d56440af211145b548ad778edf024321edbe141731daf0b071b8591b15c529'
review=B/'root-bounded-import-review-v001.json';assert not review.exists()
review.write_text(json.dumps({'source_freeze':desc(f),'source_native':171,'root_viewed_six_original512_after_E209':True,
    'independent_measurement':'primary2-measurement-v003; all grippoints uncertain visible palm candidates, not validated real handle axes',
    'decision':'Allow one new-namespace six-texture bounded sword fit import; same fixed72px/displayRoot, no armor yet.',
    'new_axis1':[.85,.526],'old_vertical_low_axis_history_preserved':True,'actual_registry_still_requires_importer_check':True,
    'motion_accepted':False,'complete_equipment':False,'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=T/'ue_sword_primary2_v001_checks.py';q=T/'ue_sword_primary2_v002_checks.py';assert not q.exists()
s=p.read_text(encoding='utf-8').replace('native169','native171')
s=s.replace("'source-assets/production/fairytale-sword-primary2-runtime-v001'","'source-assets/production/fairytale-sword-primary2-runtime-v002/axis1-correction-v001'")
s=s.replace('import-sword-primary2-v001.json','import-sword-primary2-v002.json').replace('ready-for-root-import-freeze-v001.json','ready-for-root-import-freeze-v002.json')
s=s.replace('7297932b9cbd299ea52efb6c304bdfb799547a8851dda4044b79d65a3fd3a749','c5d56440af211145b548ad778edf024321edbe141731daf0b071b8591b15c529')
s=s.replace('2c0156cc3f72b80f08832f2cb2a1690c19c868012098a20ab67ae79786e250be','804a585273ebe25fef1cad364782aedf62d7ae57b404199365ee9d94d9c64a37')
s=s.replace('EV048/v008/','EV048/v009/').replace("p = BASE / 'manifests/old-production983-before-import.json'","p = BASE.parent / 'manifests/old-production989-before-import.json'")
s=s.replace('== 983','== 989').replace('frozen-fairytale-sword-primary2-six-v1','frozen-fairytale-sword-primary2-six-v2')
s=s.replace('T_Fairytale_SwordPrimary2_{row["frame"]:03d}_v001','T_Fairytale_SwordPrimary2_{row["frame"]:03d}_v002')
q.write_text(s,encoding='utf-8')
p=T/'ue-import-sword-primary2-v001.py';q=T/'ue-import-sword-primary2-v002.py';assert not q.exists()
s=p.read_text(encoding='utf-8').replace('ue_sword_primary2_v001_checks.py','ue_sword_primary2_v002_checks.py')
s=s.replace('sword-primary2-v001-import-','sword-primary2-v002-import-').replace('Native169','Native171').replace('"old_packages_unchanged":983','"old_packages_unchanged":989')
s=s.replace('fairytale-sword-primary2-six-native-import-v1','fairytale-sword-primary2-six-native-import-v2')
q.write_text(s,encoding='utf-8')
p=T/'import-sword-primary2-v001.ps1';q=T/'import-sword-primary2-v002.ps1';assert not q.exists()
s=p.read_text(encoding='utf-8').replace('sword-primary2-v001','sword-primary2-v002').replace('983','989')
q.write_text(s,encoding='utf-8')
A=R/'过程图稿与视频/2026-10-16_军剑短肘闭握独立剑试装导入候选_v002';assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
files=[Path(row['path']) for row in m['files']]+[f,review,Path(__file__),T/'ue_sword_primary2_v002_checks.py',T/'ue-import-sword-primary2-v002.py',T/'import-sword-primary2-v002.ps1'];entries=[]
for i,p in enumerate(files):
    q=A/'原件'/f'{i:03d}-{p.name}';shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();entries.append({'source':desc(p),'copy':desc(q)})
for p in (B.parent/'curated').glob('*.png'):shutil.copy2(p,A/'展示副本'/p.name)
(A/'index.json').write_text(json.dumps({'files':entries,'source_version':'native171/final axis1 correction/runtime-v002',
    'status':'Six exact source copies and reviewed candidate ready for bounded newnamespace import; not imported or accepted',
    'formal_complete_units':0,'runtime_verified':False,'armor_present':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('171原六帧和已测可见掌面候选，独立刃轴为设计，轴1浅向前下以免预测拖地。旧直立轴候选冻结历史保留；Root只授权新namespace试装，未导入、未验收握柄/盔/腿/足锁/甲或完整动作。\n',encoding='utf-8')
print(json.dumps({'archive':A.as_posix(),'original_files':len(files),'bounded_import_review':desc(review)},ensure_ascii=False))
