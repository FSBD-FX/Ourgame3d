"""Audit the actual full report and both canonical/frozen provenance endpoints."""
from pathlib import Path
import hashlib,json
root=Path('F:/Ourgame');snapshot=root/'source-assets/production/backups/2026-10-16_RunExploration-and-typedAggregate-full122GREEN-v089'
manifest=json.loads((snapshot/'compiled-source-manifest.json').read_text(encoding='utf-8'))
report=root/'UnrealGame/Saved/Automation/FirstRoom-20261016-065641/index.json'
r=json.loads(report.read_text(encoding='utf-8-sig'));prior=json.loads((root/'UnrealGame/Saved/Automation/FirstRoom-20261016-052952/index.json').read_text(encoding='utf-8-sig'))
assert r['succeeded']==122 and r['failed']==r['notRun']==r['inProcess']==0 and len(r['tests'])==122
assert all(t['state']=='Success' and t.get('warnings',0)==0 for t in r['tests'])
old={t['fullTestPath'] for t in prior['tests']};current={t['fullTestPath'] for t in r['tests']}
assert len(old)==116 and old<=current and len(current-old)==6
oldmanifest=json.loads((root/'source-assets/production/backups/2026-10-16_rewards-owner116GREEN-chest4import-v079/compiled-source-manifest.json').read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
differences=[];checks=0
for row in manifest['files']:
 for base in (root,snapshot):
  p=base/row['path'];checks+=1
  if not p.is_file() or p.stat().st_size!=row['bytes'] or sha(p)!=row['sha256']:differences.append(p.as_posix())
oldtests=[x for x in oldmanifest['files'] if x['path'].startswith('UnrealGame/Source/CodexDungeon/Tests/')]
oldtestchanges=[x['path'] for x in oldtests if sha(root/x['path'])!=x['sha256'] or (root/x['path']).stat().st_size!=x['bytes']]
assert not differences and not oldtestchanges,(differences,oldtestchanges)
out=root/'docs/production/first-batch-v2/evidence/run-capture-v001/actual-full122-audit-v001.json';assert not out.exists()
d={'actual_report':report.relative_to(root).as_posix(),'succeeded':122,'failed':0,'warnings':0,'notRun':0,'inProcess':0,
 'original116_names_preserved':True,'new_names':sorted(current-old),'original_test_source_files_unchanged':len(oldtests),
 'old_test_source_differences':oldtestchanges,'snapshot':snapshot.relative_to(root).as_posix(),'snapshot_files':len(manifest['files']),
 'snapshot_bytes':manifest['bytes'],'canonical_F_vs_frozen_F_size_SHA_checks':checks,'differences':differences,
 'not_an_E_source_mirror':True,'DLL_sha256':sha(root/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'),
 'default_runner_expected':122,'default_runner_separate_rerun_performed':False,'formal_complete_units':0}
out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d,ensure_ascii=False))
