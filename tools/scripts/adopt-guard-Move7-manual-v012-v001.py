"""Adopt the actual prepared v012 into normal user-facing entries, preserving old versions."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-guard-v001/Move7-manual-checkpoint-candidate-v001'
O=R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/root-native-checkpoint-v001/manual-adoption-v012-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
cp=R/'source-assets/production/fairytale-guard-v001/root-Move7-checkpoint-v001/manual-input-v001.json'
prep=cp.parent/'preparation-receipt-v001.json';assert read(prep)['success']
assert not O.exists();O.mkdir(parents=True)
wrapper=R/'tools/scripts/launch-guard-room-native-trial-v012.ps1';assert not wrapper.exists();shutil.copy2(C/'Root-wrapper-candidate-v012.ps1',wrapper)
result=subprocess.run(['pwsh','-NoProfile','-File',str(wrapper),'-LightArtTrial','-GuardFullArt','-ValidateOnly'],capture_output=True,text=True,encoding='utf-8')
log=O/'actual-v012-ValidateOnly-v001.log';log.write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,result.stderr
facts=json.loads(result.stdout);assert facts['strict_registry']==200 and facts['source_files']==283 and facts['production_files']==1371
assert not facts['UE_started'] and not facts['automatic_inputs'] and not facts['diagnostic_damage']
names=['裂岩守卫挥斧试样.cmd','石廊三敌原生试玩.cmd','裂岩守卫三动作试样.cmd','钟盔轻甲倒地试玩.cmd','钟盔轻甲受击试玩.cmd','裂岩守卫跺击试玩.cmd','钟盔轻甲闪避试玩.cmd']
changed=[]
for name in names:
 p=R/name;before=pin(p);target=O/'before'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 s=p.read_text(encoding='utf-8-sig');assert s.count('launch-guard-room-native-trial-v011.ps1')==1
 p.write_text(s.replace('launch-guard-room-native-trial-v011.ps1','launch-guard-room-native-trial-v012.ps1'),encoding='utf-8',newline='\n');changed.append(dict(before=before,after=pin(p)))
entry=R/'裂岩守卫行走试玩.cmd';assert not entry.exists()
entry.write_text('@echo off\ncd /d "F:\\Ourgame"\npwsh -NoProfile -ExecutionPolicy Bypass -File "F:\\Ourgame\\tools\\scripts\\launch-guard-room-native-trial-v012.ps1" -LightArtTrial -GuardFullArt\npause\n',encoding='utf-8',newline='\n')
d=dict(schema='Root-Move7-v012-manual-adoption-v141-v001',utc=datetime.now(timezone.utc).isoformat(),success=True,checkpoint=pin(cp),preparation=pin(prep),wrapper=pin(wrapper),validation=pin(log),facts=facts,changed_entries=changed,new_entry=pin(entry),old_v011_preserved=True,automatic_inputs=False,diagnostic_damage=False,UE_started=False,FinalAccepted=False)
q=O/'adoption-receipt-v001.json'
with q.open('x',encoding='utf-8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(adoption=pin(q),entries=8,source_files=283,production_files=1371,strict_registry=200,UE_started=False),ensure_ascii=False))
