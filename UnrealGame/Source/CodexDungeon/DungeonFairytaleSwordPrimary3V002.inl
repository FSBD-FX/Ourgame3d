#pragma once
#include "DungeonFairytaleSwordPrimary3V001.inl"

// Axis-only Root Bound-mode trial; keep V001 and all old flags unchanged.
// CPU nominal phase1 residual3core/17AA samples, +/-3source worst47core.
// Fixed original NearHand/Helmet86adjacent core hand pixels remain unchanged.
// Phase3 alpha-support center gap~4.19screenpx at UIScale1 is CPU, not GPU proof.
// All palms/roots/polygons/textures/72px/.50/timing are inherited exactly.
namespace DungeonFairytaleSwordPrimary3V002
{
using FMarker = DungeonFairytaleSwordPrimary3V001::FMarker;
inline int32 Count(const FString& Clip)
{ return DungeonFairytaleSwordPrimary3V001::Count(Clip); }
inline const FMarker* Find(const FString& Clip,int32 Frame)
{
    if(Clip!=TEXT("sword_primary_3") || Frame<0 || Frame>=Count(Clip))return nullptr;
    static const TArray<FMarker> Markers=[]()
    {
        TArray<FMarker> Values;Values.Reserve(6);
        for(int32 SampleIndex=0;SampleIndex<6;++SampleIndex)
        {
            const FMarker* Base=DungeonFairytaleSwordPrimary3V001::Find(TEXT("sword_primary_3"),SampleIndex);
            if(!Base)return TArray<FMarker>();
            Values.Add(*Base);
        }
        Values[1].Axis=FVector2D(-.5,-.8660254037844386);
        Values[3].Axis=FVector2D(.9135454576426009,.4067366430758002);
        return Values;
    }();
    return Markers.IsValidIndex(Frame)?&Markers[Frame]:nullptr;
}
inline UTexture2D* GetTexture(const FString& Component,int32 Frame,
    TMap<FString,TObjectPtr<UTexture2D>>& Cache)
{ return DungeonFairytaleSwordPrimary3V001::GetTexture(Component,Frame,Cache); }
} // namespace DungeonFairytaleSwordPrimary3V002
