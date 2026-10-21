#pragma once
#include "Engine/Texture2D.h"
#include "DungeonFairytaleSwordBodyV001.inl"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/PackageName.h"

// Native175 exact body owners + integer registered176/177/178 armor. Trial only.
// Actual175 palms are candidates; directed blade axes are Root DESIGN, not measured.
// KernelStage2 110/110/60/60/160/160ms; source72px/root256,464/Sword.50.
// Grasp, clearance, semantic AA ownership and full motion remain unaccepted.
namespace DungeonFairytaleSwordPrimary3V001
{
inline bool ArmorEnabled()
{
    return FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary3ArmorPreview"));
}
inline bool Enabled()
{ return ArmorEnabled() || FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary3Preview")); }
using FMarker = DungeonFairytaleSwordBodyV001::FMarker;
inline int32 Count(const FString& Clip) { return Clip==TEXT("sword_primary_3")?6:0; }
inline const FMarker* Find(const FString& Clip,int32 Index)
{
    if(Clip!=TEXT("sword_primary_3") || Index<0 || Index>=6)return nullptr;
    static const FMarker Markers[]={
        FMarker{FVector2D(256.,464.),FVector2D(211.,315.),FVector2D(0.94,-0.341),TArray<FVector2D>{FVector2D(190.,296.), FVector2D(204.,294.), FVector2D(219.,297.), FVector2D(229.,306.), FVector2D(238.,316.), FVector2D(234.,326.), FVector2D(224.,334.), FVector2D(210.,341.), FVector2D(198.,339.), FVector2D(189.,333.), FVector2D(181.,324.), FVector2D(181.,312.), FVector2D(184.,302.)}},
        FMarker{FVector2D(256.,464.),FVector2D(194.,191.),FVector2D(-0.7071,-0.7071),TArray<FVector2D>{FVector2D(174.,175.), FVector2D(185.,168.), FVector2D(198.,166.), FVector2D(211.,171.), FVector2D(220.,180.), FVector2D(224.,190.), FVector2D(219.,201.), FVector2D(209.,209.), FVector2D(197.,214.), FVector2D(184.,213.), FVector2D(173.,206.), FVector2D(169.,194.), FVector2D(171.,183.)}},
        FMarker{FVector2D(256.,464.),FVector2D(359.,305.),FVector2D(0.866,0.5),TArray<FVector2D>{FVector2D(341.,286.), FVector2D(352.,281.), FVector2D(367.,284.), FVector2D(380.,289.), FVector2D(388.,299.), FVector2D(387.,308.), FVector2D(380.,318.), FVector2D(367.,325.), FVector2D(354.,325.), FVector2D(341.,320.), FVector2D(332.,313.), FVector2D(329.,304.), FVector2D(333.,294.)}},
        FMarker{FVector2D(256.,464.),FVector2D(331.,360.),FVector2D(0.85,0.526),TArray<FVector2D>{FVector2D(313.,340.), FVector2D(324.,338.), FVector2D(338.,341.), FVector2D(350.,349.), FVector2D(358.,360.), FVector2D(358.,368.), FVector2D(350.,379.), FVector2D(335.,386.), FVector2D(322.,384.), FVector2D(312.,376.), FVector2D(305.,366.), FVector2D(303.,355.), FVector2D(306.,346.)}},
        FMarker{FVector2D(256.,464.),FVector2D(306.,364.),FVector2D(0.98,-0.2),TArray<FVector2D>{FVector2D(287.,343.), FVector2D(300.,341.), FVector2D(315.,346.), FVector2D(328.,353.), FVector2D(338.,365.), FVector2D(339.,374.), FVector2D(331.,383.), FVector2D(318.,390.), FVector2D(305.,386.), FVector2D(293.,379.), FVector2D(281.,369.), FVector2D(278.,358.), FVector2D(282.,349.)}},
        FMarker{FVector2D(256.,464.),FVector2D(207.,316.),FVector2D(0.94,-0.341),TArray<FVector2D>{FVector2D(188.,295.), FVector2D(201.,293.), FVector2D(214.,296.), FVector2D(226.,304.), FVector2D(234.,315.), FVector2D(232.,326.), FVector2D(222.,334.), FVector2D(209.,339.), FVector2D(195.,337.), FVector2D(184.,330.), FVector2D(179.,320.), FVector2D(178.,310.), FVector2D(183.,301.)}},
    };
    return &Markers[Index];
}
inline UTexture2D* GetTexture(const FString& Component,int32 Frame,
    TMap<FString,TObjectPtr<UTexture2D>>& Cache)
{
    if(Frame<0 || Frame>=6)return nullptr;
    bool Known=false;
    for(const TCHAR* Name:{TEXT("Body"),TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),
        TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT("NearHand")})
        Known|=Component==Name;
    if(!Known)return nullptr;
    const FString Name=FString::Printf(TEXT("T_Fairytale_SwordPrimary3%s_%03d_v001"),*Component,Frame);
    if(const auto Found=Cache.Find(Name))return Found->Get();
    const FString Package=TEXT("/Game/Production/ArtTrials/EV048/v011/HeroSwordPrimary3/")+Name;
    UTexture2D* Texture=FPackageName::DoesPackageExist(Package)
        ?LoadObject<UTexture2D>(nullptr,*(Package+TEXT(".")+Name)):nullptr;
    Cache.Add(Name,Texture);
    return Texture;
}
} // namespace DungeonFairytaleSwordPrimary3V001
