from pathlib import Path
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
ap=argparse.ArgumentParser();ap.add_argument('--name',required=True);ap.add_argument('--build-log',required=True);ap.add_argument('--automation-report',required=True);a=ap.parse_args()
assert all(c.isalnum() or c in '_-' for c in a.name)
O=R/'source-assets/production/backups'/a.name;assert not O.exists()
base=R/'source-assets/production/backups/2026-10-17_StoneGuardNative-Coin-full154GREEN-beforeLeather-v123/compiled-source-manifest.json';old=read(base)
build=R/a.build_log;last=R/'UnrealGame/Saved/Bootstrap/last-build.json';v=read(last);assert v['ExitCode']==0 and Path(v['Log']).resolve()==build.resolve()
report=R/a.automation_report;v=read(report);assert v['succeeded']==len(v['tests'])==154 and len({t['fullTestPath'] for t in v['tests']})==154
assert all(v.get(k,0)==0 for k in ['failed','succeededWithWarnings','notRun','inProcess']) and all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in v['tests'])
import sys
sys.path.insert(0,str(R/'tools/scripts'));import ue_leather_ready_v001_checks as checks
checks.preflight(False)
ptr=R/'source-assets/production/fairytale-lgt-readability-v003/ready-import-v001/actual-import-receipt-ref.json';ref=read(ptr);receipt=Path(ref['path']);imp=read(receipt)
assert hashlib.sha256(receipt.read_bytes()).hexdigest()==ref['sha256'] and imp['success'] and imp['saved_count']==12
oldprod={r['path']:r for r in old['files'] if r['path'].startswith('UnrealGame/Content/Production/')};assert len(oldprod)==1085
newprod={desc(Path(r['saved_uasset']))['path']:desc(Path(r['saved_uasset'])) for r in imp['assets']};assert len(newprod)==12 and not(set(oldprod)&set(newprod))
actualprod={desc(p)['path']:desc(p) for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()}
assert actualprod=={**oldprod,**newprod} and len(actualprod)==1097
allowed={'UnrealGame/Source/CodexDungeon/'+n for n in ['DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleEquipmentBoundProbe.cpp','DungeonFairytaleEquipmentBoundProbe.h']}
source_changes={r['path'] for r in old['files'] if r['path'].startswith(('UnrealGame/Source/','UnrealGame/Config/')) and desc(R/r['path'])!=r};assert source_changes==allowed
paths=[p for directory in ['UnrealGame/Source','UnrealGame/Config','UnrealGame/Content/Production'] for p in (R/directory).rglob('*') if p.is_file()]
paths += [build,last,report,R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',Path(__file__).resolve(),R/'tools/scripts/test-first-room.ps1',receipt,ptr,checks.MANIFEST,R/'tools/scripts/ue_leather_ready_v001_checks.py',R/'tools/scripts/ue-import-leather-ready-v001.py',R/'source-assets/production/fairytale-lgt-readability-v003/ready-native-source-v002/source-freeze-v002.json',R/'source-assets/production/fairytale-lgt-readability-v003/ready-integer-assembly-v001/assembly-freeze-v001.json']
rows=[]
for p in sorted(set(paths)):
 d=desc(p);q=O/d['path'];q.parent.mkdir(parents=True,exist_ok=True);assert not q.exists();shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(d)
for d in rows:
 assert desc(R/d['path'])==d
 p=O/d['path'];assert p.stat().st_size==d['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==d['sha256']
v=dict(schema='equipment-bound-plus-leather-ready-current-build-freeze-v001',snapshot=O.as_posix(),status='current154GREEN_before_native_flows',files=rows,copied_files=len(rows),bytes=sum(d['bytes'] for d in rows),production_packages=1097,old_production_packages=1085,old_production_unchanged=True,new_production_packages=12,new_production_import_receipt=desc(receipt),base_snapshot=base.parent.as_posix(),current_automation_report=a.automation_report,current_automation_succeeded=154,build_log=a.build_log,source_and_copy_checks=2*len(rows),mismatches=0,formal_complete_units=0)
(O/'compiled-source-manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:x for k,x in v.items() if k!='files'},ensure_ascii=False))
