from pathlib import Path
import hashlib,json,shutil,subprocess,os,datetime
R=Path('F:/Ourgame');F=R/'source-assets/production/fairytale-lgt-readability-v003';B=F/'ready-native-source-v002';S=R/'UnrealGame/Source/CodexDungeon';D=R/'docs/production/first-batch-v2';O=D/'evidence/leather-ready-v001/root-source-admission-v002'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
v=read(B/'source-freeze-v002.json')
for row in v['inputs']+v['files']:assert desc(Path(row['path']))==row
receipt=R/'UnrealGame/Saved/Bootstrap/leather-ready-v001-import-20261016-164451-394112.json';imp=read(receipt)
assert imp['success'] and imp['actual_count']==imp['saved_count']==len(imp['assets'])==12 and imp['old_packages_unchanged']==1085
ptr=F/'ready-import-v001/actual-import-receipt-ref.json';assert not ptr.exists();ptr.write_text(json.dumps(dict(path=receipt.as_posix(),bytes=receipt.stat().st_size,sha256=desc(receipt)['sha256']),indent=2)+'\n',encoding='utf-8')
import sys
sys.path.insert(0,str(R/'tools/scripts'))
import ue_leather_ready_v001_checks as checks
checks.preflight(False)
snap=R/'source-assets/production/backups/2026-10-17_StoneGuardNative-Coin-full154GREEN-beforeLeather-v123'
for row in read(snap/'compiled-source-manifest.json')['files']:
 if row['path'].startswith(('UnrealGame/Source/','UnrealGame/Config/')):
  p=R/row['path'];d=desc(p);assert d['bytes']==row['bytes'] and d['sha256']==row['sha256']
patch=B/'ready-trial-v002.patch';subprocess.run(['git','apply','--check',str(patch)],cwd=R,check=True)
assert not O.exists();O.mkdir(parents=True)
before={p:desc(p) for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()}
names=['DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleEquipmentBoundProbe.h','DungeonFairytaleEquipmentBoundProbe.cpp']
for name in names:
 p=S/name;q=O/'before'/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
subprocess.run(['git','apply',str(patch)],cwd=R,check=True)
changed={p for p,d in before.items() if desc(p)!=d};assert changed=={S/n for n in names}
for name in names:
 p=S/name;assert p.read_bytes().replace(b'\r\n',b'\n')==(B/name).read_bytes().replace(b'\r\n',b'\n');os.utime(p,None)
(O/'admission.json').write_text(json.dumps(dict(source_freeze=desc(B/'source-freeze-v002.json'),import_receipt=desc(receipt),before_source=list(before.values()),after_changed=[desc(S/n) for n in names],all_tests_unchanged=True,other_Source_unchanged=True,default_art_selection_unchanged=True,source_mtime_refreshed=True,compiled=False,native_trial_verified=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v=read(D/'progress.json');v['ue_current_working_source_compiled']=False;v['ue_current_working_source_verified']=False;v['current_source_uncompiled_changes']='Opt-in Ready leather3layers/actual-input Ready4bothface probe admitted after v123full154GREEN; compiling pending; imported12new packages old1085unchanged.';v['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(D/'progress.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(changed_files=names,imported12_verified=True,all_tests_unchanged=True,actual_build_not_yet=True)))
