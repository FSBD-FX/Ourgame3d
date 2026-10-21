"""Publish new explicit current manual checkpoint; retain old wrapper and before entrypoints."""
from pathlib import Path
import json,hashlib,shutil
R=Path('F:/Ourgame'); E=R/'docs/production/first-batch-v2/evidence/combat-range-cleanup-v001/root-manual-v137-v001'
assert not E.exists();(E/'before').mkdir(parents=True)
files=['钟盔轻甲受击试玩.cmd','裂岩守卫挥斧试样.cmd','裂岩守卫三动作试样.cmd','石廊三敌原生试玩.cmd']
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
before=[];after=[]
for name in files:
 p=R/name;before.append(pin(p));shutil.copy2(p,E/'before'/name)
wrapper=R/'tools/scripts/launch-guard-room-native-trial-v008.ps1';assert not wrapper.exists()
wrapper.write_text("""param([string]$EngineRoot='G:\\UE_5.5',[string]$Snapshot='',[string]$RootCheckpoint='source-assets/production/fairytale-guard-v001/root-Hurt1286-checkpoint-v002/manual-input-v001.json',[switch]$LightArtTrial,[switch]$GuardFullArt,[switch]$ValidateOnly)
$ErrorActionPreference='Stop'
# Explicitly forward the default too: PSBoundParameters omits values supplied by param defaults.
$PSBoundParameters['RootCheckpoint']=$RootCheckpoint
$launcher='F:\\Ourgame\\source-assets\\production\\fairytale-guard-v001\\current-Hurt1286-checkpoint-tooling-candidate-v001\\tooling\\launch-guard-room-native-trial-v007.ps1'
& $launcher @PSBoundParameters
if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
""",encoding='utf-8')
for name in files:
 p=R/name;t=p.read_text(encoding='utf-8-sig');assert t.count('launch-guard-room-native-trial-v007.ps1')==1;t=t.replace('launch-guard-room-native-trial-v007.ps1','launch-guard-room-native-trial-v008.ps1');p.write_text(t,encoding='utf-8');after.append(pin(p))
(E/'manual-entry-publication-v001.json').write_text(json.dumps(dict(before=before,after=after,wrapper=pin(wrapper),snapshot='v137-range187G',checkpoint='root-Hurt1286-checkpoint-v002',default_combat_range_debug=False,validation_pending=True,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(wrapper=wrapper.as_posix(),updated_entries=files,previous_wrapper_unchanged=True),ensure_ascii=False))
