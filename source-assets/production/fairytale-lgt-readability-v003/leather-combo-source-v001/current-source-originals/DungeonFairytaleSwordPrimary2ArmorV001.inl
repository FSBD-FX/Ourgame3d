#pragma once
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
