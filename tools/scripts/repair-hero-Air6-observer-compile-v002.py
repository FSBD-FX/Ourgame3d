"""Preserve failed observer compile and repair only its local shadowed name."""
from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');O=R/'docs/production/first-batch-v2/evidence/HeroAir6-v142-v001/observer-compile-repair-v002'
assert not O.exists();O.mkdir(parents=True)
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
p=R/'UnrealGame/Source/CodexDungeon/DungeonHeroAirProbeV001.cpp';old=p.read_text(encoding='utf-8')
for src in [p,R/'UnrealGame/Saved/Bootstrap/last-build.json',R/'UnrealGame/Saved/Bootstrap/build-editor-20261019-000522.log']:shutil.copy2(src,O/src.name)
before=pin(p)
a='const auto Phase=Actor.MainMixCapture->Status().Phase;\n   if(Phase==EDungeonNativeMixCapturePhaseV001::Recording||Phase==EDungeonNativeMixCapturePhaseV001::ExportPending)'
b='const auto MixPhase=Actor.MainMixCapture->Status().Phase;\n   if(MixPhase==EDungeonNativeMixCapturePhaseV001::Recording||MixPhase==EDungeonNativeMixCapturePhaseV001::ExportPending)'
assert old.count(a)==1
new=old.replace(a,b);candidate=O/'DungeonHeroAirProbeV001.repaired.cpp';candidate.write_text(new,encoding='utf-8',newline='\n');shutil.copy2(candidate,p)
receipt=dict(schema='Root-Air6-observer-compile-local-shadow-repair-v002',before=before,after=pin(p),root_cause='Compiler C4458: BeginStop local Phase hides FDungeonHeroAirProofStateV001::Phase under existing warnings-as-errors policy.',only_change='Rename one local variable and its two references to MixPhase.',test_bytes_and_thresholds_changed=False,old_candidate_freeze_overwritten=False,compiled=False,formal_complete_units=0)
(O/'repair-receipt-v002.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,ensure_ascii=False))
