from pathlib import Path
import json,hashlib
R=Path('F:/Ourgame');T=R/'tools/scripts';D=R/'source-assets/production/checkpoint-v125-root-input-v001'
def pin(p):
 p=p.resolve();b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,s):assert not p.exists();p.write_text(s,encoding='utf-8')
s=(T/'verify-equipment-bound-current-build-v005.py').read_text(encoding='utf-8');a='x,m["art_mode"]=="primary1")';b='x,m["art_mode"]=="primary1" and x["kind"]!="default")';assert a in s;s=s.replace(a,b)
a='    if m["art_mode"]=="primary1":flags += ["-DungeonFairytaleLeatherReadyPreview","-DungeonFairytaleLeatherPrimary1Preview"]\n';assert a in s;s=s.replace(a,'    # Default full-flow proof retains established complete art; new Ready/P1 are separate trials.\n')
vf=T/'verify-equipment-bound-current-build-v006.py';write(vf,s)
s=(T/'launch-fairytale-equipment-bound-v005.ps1').read_text(encoding='utf-8').replace('verify-equipment-bound-current-build-v005.py','verify-equipment-bound-current-build-v006.py');s=s.replace(",' -DungeonFairytaleLeatherReadyPreview'",'') if False else s
s=s.replace(",'-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview'",'');lf=T/'launch-fairytale-equipment-bound-v006.ps1';write(lf,s)
proofs=[]
for kind,name in [('default','2026-10-17_军剑真实换装绑定_v007-v125'),('ready','2026-10-17_软皮轻甲左右待机试装_v002-v125'),('primary1','2026-10-17_软皮轻甲左右第一刀试装_v001')]:
 A=R/'过程图稿与视频'/name;proofs.append(dict(kind=kind,index=pin(A/'index.json'),runtime=pin(A/'原件/runtime-report.json'),pixel=pin(A/'原件/native-pixel-verification.json')))
p=D/'manual-proof-contract-v125-v001.json';write(p,json.dumps(dict(schema='equipment-bound-manual-proof-contract-v125',snapshot_manifest=pin(R/'source-assets/production/backups/v125-p1-157G/compiled-source-manifest.json'),proofs=proofs),ensure_ascii=False,indent=2)+'\n')
f=D/'manual-tool-freeze-v006.json';write(f,json.dumps(dict(files=[pin(vf),pin(lf),pin(T/'checkpoint_v125_common_v001.py'),pin(p)],scope='Same strict157/source1115/current3proof gate. Default is complete existing gray-armor flow, so validate its own structural/transaction/three-combo semantics with art=false; Ready and Primary1 separately require exact new v012/v013 paths. No partial-new-art flags in default launcher. Source/DLL/game behavior unchanged.',full_unit_complete=False),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(contract=pin(p),manual_tool_freeze=pin(f)),ensure_ascii=False))
