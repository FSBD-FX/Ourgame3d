from pathlib import Path
import hashlib,json,os,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003/leather-combo-source-v001';F=B/'source-freeze-v001.json';O=R/'docs/production/first-batch-v2/evidence/leather-combo-v001/root-source-admission-v002';assert not O.exists()
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def sha256_check(a):
 p=Path(a['saved_uasset']);s=Path(a['source']);return p.stat().st_size==a['saved_bytes'] and desc(p)['sha256']==a['saved_sha256'] and s.stat().st_size==a['source_bytes'] and desc(s)['sha256']==a['source_sha256']
v=json.loads(F.read_text(encoding='utf-8-sig'));assert desc(F)['sha256']=='de124ef6dc023d6e001ccbf92c1f185f83406e39d1d6a16c93ccf592ab2be85c'
for x in v['files']+v['inputs']:
 p=Path(x['path']);d=desc(p);assert(d['bytes'],d['sha256'])==(x['bytes'],x['sha256'])
receipts=[]
for clip in (2,3):
 ps=list((R/'UnrealGame/Saved/Bootstrap').glob(f'leather-primary{clip}-combo-v001-import-*.json'));assert len(ps)==1;r=json.loads(ps[0].read_text(encoding='utf-8-sig'));assert r['success'] and r['actual_count']==r['saved_count']==18
 for a in r['assets']:assert a['actual_object_type']=='Texture2D' and sha256_check(a)
 receipts.append(desc(ps[0]))
assert len(list((R/'UnrealGame/Content/Production').rglob('*.uasset')))==1151
before={p:desc(p) for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()};(O/'before').mkdir(parents=True)
for x in v['inputs']:
 p=Path(x['path']);q=O/'before'/p.name;shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();c=B/p.name;shutil.copy2(c,p);assert p.read_bytes()==c.read_bytes();os.utime(p,None)
assert {p for p,d in before.items() if desc(p)!=d}=={Path(x['path']) for x in v['inputs']}
(O/'admission.json').write_text(json.dumps(dict(freeze=desc(F),before=[x for x in before.values() if Path(x['path']) in {Path(a['path']) for a in v['inputs']}],after=[desc(Path(x['path'])) for x in v['inputs']],new_import_receipts=receipts,other_source_unchanged=True,compiled=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'docs/production/first-batch-v2/progress.json';d=json.loads(p.read_text(encoding='utf-8-sig'));d.update(ue_current_working_source_compiled=False,ue_current_working_source_verified=False,current_source_uncompiled_changes='Optional leather combo5 Source files admitted after actual36 Texture2D import; GuardOwner Stage0 awaiting production. Compile/full161/native pending.',current_production_packages=1151);d['leather_combo_v001']=dict(admission=(O/'admission.json').as_posix(),runtime_verified=False,formal_complete_units=0);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Admitted5 optional combo Source;1151 actual packages; compilation required.')
