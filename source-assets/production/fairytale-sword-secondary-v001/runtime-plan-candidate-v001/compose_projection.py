from pathlib import Path
import hashlib,json

HERE=Path(__file__).resolve().parent
ROOT=Path('F:/Ourgame')
PROJECT=HERE/'projected'
BASES={
 'UnrealGame/Source/CodexDungeon/DungeonHUD.h':(16409,'94d4f3f8bfe8e3857d005583b1931f14e4255f5ce5af513a7022c2d689ef8db5'),
 'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp':(123680,'a68a9df57826a3761f2bfbf8511858b139c193589f285c0cc7bbb29ad950e16f'),
 'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPresentation.cpp':(25397,'be8afcfce07e2c02a01481a86a819d6ea516002ccce925a74873871f2a748794'),
}
SEAMS=[]
def add(path,label,anchor,addition,after=True):
 SEAMS.append(dict(path=path,label=label,kind='insert_after' if after else 'insert_before',anchor=anchor.replace('\n','\r\n'),addition=addition.replace('\n','\r\n')))
H='UnrealGame/Source/CodexDungeon/DungeonHUD.h'
C='UnrealGame/Source/CodexDungeon/DungeonHUD.cpp'
R='UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPresentation.cpp'
add(H,'secondary-trace-include','#include "DungeonFairytaleSwordAirDrawStateV001.h"\n','#include "DungeonFairytaleSwordSecondaryDrawStateV001.h"\n')
add(H,'texture-forward-declaration','class UTexture2D;\n','class UTexture;\n')
add(H,'same-callback-trace-getter','    const FDungeonFairytaleSwordAirDrawV001& GetFairytaleSwordAirDraw() const { return FairytaleSwordAirDraw; }\n','    const FDungeonFairytaleSwordSecondaryDrawV001& GetFairytaleSwordSecondaryDraw() const { return FairytaleSwordSecondaryDraw; }\n')
add(H,'bounded-secondary-members','    FDungeonFairytaleSwordAirDrawV001 FairytaleSwordAirDraw;\n',
 '    bool bUseFairytaleSwordSecondaryPreview=false;\n'
 '    FDungeonFairytaleSwordSecondaryDrawV001 FairytaleSwordSecondaryDraw;\n'
 '    void ResetFairytaleSwordSecondaryDraw();\n'
 '    void PreloadFairytaleSwordSecondary(TArray<UTexture*>& Textures);\n'
 '    bool DrawFairytaleSwordSecondaryBody(ADungeonFighter* Fighter);\n')
add(C,'new-explicit-optin','    bUseFairytaleSwordAirPreview=bUseFairytaleSwordEquipmentBoundPreview\n        &&FParse::Param(FCommandLine::Get(),DungeonFairytaleSwordAirV001::CommandLineFlag);\n',
 '    bUseFairytaleSwordSecondaryPreview=bUseFairytaleSwordEquipmentBoundPreview\n'
 '        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordSecondaryPreview"));\n')
add(C,'startup-before-existing-FinishCompilation',
 '            if(auto Texture=DungeonFairytaleSwordDodgeV001::PreloadTexture(DodgeProfile.SwordTexturePath,Frames))ReadyArmorTextures.Add(Texture);\n        }\n',
 '        PreloadFairytaleSwordSecondary(ReadyArmorTextures);\n')
add(C,'restore-trace-clearing','    FairytaleSwordAirDraw=FDungeonFairytaleSwordAirDrawV001();\n',
 '    ResetFairytaleSwordSecondaryDraw();\n')
# The Air reset occurs twice in this file. The restore anchor must be unique;
# make it include the actual preceding restore reset line, not a global replace.
SEAMS[-1]['anchor']=('    ActionAudioPlayRequests.Reset();ActionAudioPlayReceipts.Reset();MeleeTrails.Reset();ActorQuads.Reset();FairytaleGuardMoveRigDraws.Reset();\n'
 '    FairytaleSwordAirDraw=FDungeonFairytaleSwordAirDrawV001();\n').replace('\n','\r\n')
add(C,'callback-clearing-before-no-Canvas','void ADungeonHUD::DrawHUD()\n{\n','    ResetFairytaleSwordSecondaryDraw();\n')
add(R,'clearing-before-Death-Hurt','    if(!F || F->bEnemy)return false;\n','    ResetFairytaleSwordSecondaryDraw();\n')
add(R,'dispatch-after-Air-before-J','    if(bUseFairytaleSwordAirPreview && DrawFairytaleSwordAirBody(F))return true;\n',
 '    if(bUseFairytaleSwordSecondaryPreview && DrawFairytaleSwordSecondaryBody(F))return true;\n')

def pin(path):
 b=path.read_bytes();return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())

reports=[]
for path,(size,sha) in BASES.items():
 original=(ROOT/path).read_bytes()
 assert len(original)==size and hashlib.sha256(original).hexdigest()==sha,('base_changed',path)
 result=original
 operations=[s for s in SEAMS if s['path']==path]
 for s in operations:
  a=s['anchor'].encode();x=s['addition'].encode()
  assert result.count(a)==1,(s['label'],'nonunique_anchor',result.count(a))
  result=result.replace(a,a+x if s['kind']=='insert_after' else x+a,1)
 # Inverse exact insert removal proves every old byte remains untouched.
 inverse=result
 for s in reversed(operations):
  a=s['anchor'].encode();x=s['addition'].encode();composite=a+x if s['kind']=='insert_after' else x+a
  assert inverse.count(composite)==1,(s['label'],'nonunique_inverse')
  inverse=inverse.replace(composite,a,1)
 assert inverse==original,('roundtrip_failed',path)
 target=PROJECT/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(result)
 reports.append(dict(path=path,before=dict(bytes=size,sha256=sha),after=pin(target),insertions=len(operations),roundtrip_to_base=True))
for path in BASES:assert pin(ROOT/path)==dict(bytes=BASES[path][0],sha256=BASES[path][1]),('actual_mutated',path)
(HERE/'exact-seams-v001.json').write_text(json.dumps(dict(schema='secondary8-unadmitted-exact-insert-seams-v001',FinalAccepted=False,runtime_not_ready=True,base_compiled_manifest_sha256='e08bf832e82c6af093650b7ebde3fa4fc25b59aa47bfe465bb239f7308292564',operations=SEAMS,projected_files=reports),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'verification'/'source-roundtrip-v001.json').write_text(json.dumps(dict(schema='secondary8-candidate-source-roundtrip-v001',actual_source_unchanged=True,projected_old_files=reports,source_additions=3,projected_total_source_files_if_admitted=306,ue_build_run=False,native_run=False,FinalAccepted=False,runtime_not_ready=True),indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(passed=True,exact_insertions=len(SEAMS),old_files_roundtrip=3,new_source_files=3,actual_mutations=0,runtime_not_ready=True)))
