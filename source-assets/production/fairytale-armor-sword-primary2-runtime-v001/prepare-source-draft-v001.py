"""Unapplied three-file Primary2 armor opt-in patch. Never writes UnrealGame/Source."""
from pathlib import Path
import difflib, hashlib, json
ROOT=Path('F:/Ourgame')
OUT=Path(__file__).resolve().parent/'source-draft-v001'
SOURCE=ROOT/'UnrealGame/Source/CodexDungeon'
NAME='DungeonFairytaleSwordPrimary2ArmorV001.inl'
def fact(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(path,content):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:f.write(content if isinstance(content,bytes) else content.encode('utf-8'))
def replace(source,before,after):
    assert source.count(before)==1, before
    return source.replace(before,after,1)
assert not OUT.exists(),'Never overwrite a Source draft'
assert not (SOURCE/NAME).exists(),'New inline already exists in actual Source'
originals={n:(SOURCE/n).read_bytes() for n in ['DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp']}
pins=[fact(SOURCE/n) for n in originals]
inline='''#pragma once
#include "Engine/Texture2D.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/PackageName.h"

// UNAPPLIED trial: native171 exact body owners + integer-registered172/173/174.
// Seven same512 quads plus independent Sword; source72px/root256,464 unchanged.
// Marker/grip/axes MUST remain current DungeonFairytaleSwordPrimary2V003.
// Actual grasp/axis/AA semantic ownership/clearance/motion are not accepted.
namespace DungeonFairytaleSwordPrimary2ArmorV001
{
inline bool Enabled()
{
    return FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2ArmorPreview"));
}
inline UTexture2D* GetTexture(const FString& Component,int32 Frame,
    TMap<FString,TObjectPtr<UTexture2D>>& Cache)
{
    if(Frame<0 || Frame>=6)return nullptr;
    bool Known=false;
    for(const TCHAR* Name:{TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),
        TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT("NearHand")})
        Known|=Component==Name;
    if(!Known)return nullptr;
    const FString Name=FString::Printf(TEXT("T_Fairytale_SwordPrimary2%s_%03d_v001"),*Component,Frame);
    if(const auto Found=Cache.Find(Name))return Found->Get();
    const FString Package=TEXT("/Game/Production/ArtTrials/EV048/v010/HeroSwordPrimary2Armor/")+Name;
    UTexture2D* Texture=FPackageName::DoesPackageExist(Package)
        ?LoadObject<UTexture2D>(nullptr,*(Package+TEXT(".")+Name)):nullptr;
    Cache.Add(Name,Texture);
    return Texture;
}
} // namespace DungeonFairytaleSwordPrimary2ArmorV001
'''
modified={n:b.decode('utf-8').replace('\r\n','\n') for n,b in originals.items()}
for n in modified:
    modified[n]=replace(modified[n],'#include "TextureResource.h"','#include "TextureResource.h"\n#include "'+NAME+'"')
h=modified['DungeonHUD.cpp']
h=replace(h,'||FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2BodyPreview"));','||FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2BodyPreview"))\n        ||DungeonFairytaleSwordPrimary2ArmorV001::Enabled();')
before='''        // The complete selected draw also needs the independent sword and the
'''
warm='''        if(DungeonFairytaleSwordPrimary2ArmorV001::Enabled())
            for(const FString Component:{TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),
                TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT("NearHand")})
                for(int32 I=0;I<6;++I)
                    if(auto Texture=DungeonFairytaleSwordPrimary2ArmorV001::GetTexture(Component,I,Frames))ReadyArmorTextures.Add(Texture);
'''
h=replace(h,before,warm+before);modified['DungeonHUD.cpp']=h
p=modified['DungeonFairytaleSwordPresentation.cpp']
p=replace(p,'const bool SecondBodyTrial=Second && FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2BodyPreview"));','const bool SecondBodyTrial=Second && (FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2BodyPreview"))\n        ||DungeonFairytaleSwordPrimary2ArmorV001::Enabled());')
p=replace(p,'const bool Primary2BodyTrial=Primary2 && FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2BodyPreview"));','const bool Primary2BodyTrial=Primary2 && (FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2BodyPreview"))\n        ||DungeonFairytaleSwordPrimary2ArmorV001::Enabled());')
p=replace(p,'const bool PrimaryArmorPhase=bUseFairytaleSwordArmorPrimary1Preview && Primary1;\n    const bool ArmorPhase=(Record.ArmorPreview && StableIdle) || PrimaryArmorPhase;','const bool PrimaryArmorPhase=bUseFairytaleSwordArmorPrimary1Preview && Primary1;\n    const bool Primary2ArmorPhase=Primary2 && DungeonFairytaleSwordPrimary2ArmorV001::Enabled();\n    const bool ArmorPhase=(Record.ArmorPreview && StableIdle) || PrimaryArmorPhase || Primary2ArmorPhase;')
p=replace(p,'// Ready and Primary1 each use only their own actual source phase partition.','// Ready, Primary1 and opt-in Primary2 each use their own source phase partition.')
p=replace(p,'const int32 LayerCount=PrimaryArmorPhase?7:6;','const int32 LayerCount=(PrimaryArmorPhase||Primary2ArmorPhase)?7:6;')
p=replace(p,'ReadyLayers[I]=PrimaryArmorPhase\n                ?GetFairytaleSwordArmorPrimary1Texture(PrimaryComponents[I],Record.Frame)','ReadyLayers[I]=Primary2ArmorPhase\n                ?DungeonFairytaleSwordPrimary2ArmorV001::GetTexture(PrimaryComponents[I],Record.Frame,Frames)\n                :PrimaryArmorPhase?GetFairytaleSwordArmorPrimary1Texture(PrimaryComponents[I],Record.Frame)')
modified['DungeonFairytaleSwordPresentation.cpp']=p
for n in modified:
    if b'\r\n' in originals[n]:modified[n]=modified[n].replace('\n','\r\n')
patch=[]
for n,b in originals.items():
    write(OUT/'before'/n,b);write(OUT/'candidate-source'/n,modified[n])
    patch.extend(difflib.unified_diff(b.decode('utf-8').splitlines(True),modified[n].splitlines(True),fromfile='a/UnrealGame/Source/CodexDungeon/'+n,tofile='b/UnrealGame/Source/CodexDungeon/'+n))
write(OUT/'candidate-source'/NAME,inline)
patch.extend(difflib.unified_diff([],inline.splitlines(True),fromfile='/dev/null',tofile='b/UnrealGame/Source/CodexDungeon/'+NAME))
write(OUT/'primary2-armor-unapplied-v001.patch',''.join(patch))
assert all((SOURCE/n).read_bytes()==b for n,b in originals.items())
assert not (SOURCE/NAME).exists()
files=[fact(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
write(OUT/'draft-freeze-v001.json',json.dumps({'schema':'primary2-armor-three-source-unapplied-draft-v1','source_before':pins,'files':files,'Source_files_written':False,'compiled':False,'UE_called':False,'textures_imported_by_author':False,'feature_or_motion_accepted':False,'formal_complete_units':0},indent=2)+'\n')
print(json.dumps({'draft_freeze':fact(OUT/'draft-freeze-v001.json'),'actualSourceUnchanged':True}))
