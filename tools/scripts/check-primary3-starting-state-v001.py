from pathlib import Path
import hashlib,json,datetime
R=Path('F:/Ourgame');S=R/'source-assets/production/backups/2026-10-16_Primary2Armor42-fit-full138GREEN-v115'
m=json.loads((S/'compiled-source-manifest.json').read_text());rows=[]
for r in m['files']:
 if not (r['path'].startswith('UnrealGame/Source/') or r['path']=='UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'):continue
 p=R/r['path'];b=p.read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'];rows.append(r)
g=json.loads((R/'source-assets/production/first-unit-animation-v003/generation-ledger.json').read_text(encoding='utf-8-sig'))
assert g['requested_count']==174 and g['current_window']['requested_count']==6 and g['remaining_batch_requests']==18
actual=R/'UnrealGame/Saved/Automation/FirstRoom-20261016-180344/index.json';a=json.loads(actual.read_text(encoding='utf-8-sig'))
assert a['succeeded']==len(a['tests'])==138 and all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in a['tests'])
E=R/'docs/production/first-batch-v2/evidence/sword-primary3-native-tooling-v001';E.mkdir(parents=True,exist_ok=True);p=E/'starting-state-v001.json';assert not p.exists()
p.write_text(json.dumps(dict(date=datetime.datetime.now().astimezone().isoformat(),source_DLL_rows_checked=len(rows),baseline='v115',current_138_success_rechecked=True,ledger_request=174,next=175,window_remaining=18,previous_goal_turn_classification='progress: actualP2armor42saved/source4compiled/full138/bilateralnativefit/E223224 and Root+independent actualview',goal_status='active',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(p.read_text())
