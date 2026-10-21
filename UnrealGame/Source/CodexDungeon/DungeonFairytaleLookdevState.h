#pragma once

#include "CoreMinimal.h"

// EV047 opt-in source observation only. Never a complete equipment/combat identity.
namespace DungeonFairytaleLookdev
{
    constexpr int32 FrameCount = 4;
    constexpr double FrameSeconds = .167;
    constexpr int32 HeroWalkFrameCount = 6;
    constexpr double HeroWalkFrameSeconds = .083;
    constexpr double HeroCanvas = 72. * 512. / 416.;
    constexpr double HeroTargetHeight = 72.;
    constexpr double StoneTargetHeight = 93.6;
    // Fixed scale: mean source body height 386.5px; no per-frame rescaling of the idle motion.
    constexpr bool StoneMeasurementsConfirmed = true;
    constexpr double StoneCanvas = 93.6 * 512. / 386.5;
    inline FVector2D Root(bool Stone, int32 Frame)
    {
        static const FVector2D StoneRoots[4] = {{260.,464.},{257.,464.},{264.,464.},{265.,464.}};
        return Stone ? StoneRoots[FMath::Clamp(Frame,0,3)] : FVector2D(256.,464.);
    }
    inline FString Path(bool Stone, int32 Frame)
    {
        const FString Name=Stone?FString::Printf(TEXT("T_Fairytale_StoneIdle_%03d_v001"),Frame)
            :FString::Printf(TEXT("T_Fairytale_HeroIdle_%03d_v001"),Frame);
        return FString(TEXT("/Game/Production/ArtTrials/EV047/v001/"))+(Stone?TEXT("StoneIdle/"):TEXT("HeroCommonIdle/"))+Name+TEXT(".")+Name;
    }
    inline int64 Sample(double Elapsed)
    { return FMath::IsFinite(Elapsed)&&Elapsed>=0. ? int64(FMath::FloorToDouble(Elapsed/FrameSeconds)) : -1; }
    inline int64 HeroWalkSample(double Elapsed)
    { return FMath::IsFinite(Elapsed)&&Elapsed>=0. ? int64(FMath::FloorToDouble(Elapsed/HeroWalkFrameSeconds)) : -1; }
    inline FString HeroWalkPath(int32 Frame)
    {
        const FString Name=FString::Printf(TEXT("T_Fairytale_HeroWalk_%03d_v002"),Frame);
        return FString(TEXT("/Game/Production/ArtTrials/EV047/v002/HeroCommonWalk/"))+Name+TEXT(".")+Name;
    }
    inline FString HeroChestPath(int32 Frame)
    {
        const FString Name=FString::Printf(TEXT("T_Fairytale_ChestIdle_%03d_v001"),Frame);
        return FString(TEXT("/Game/Production/ArtTrials/EV048/v001/HeroChestIdle/"))+Name+TEXT(".")+Name;
    }
    inline FString HeroShoulderPath(bool Near,int32 Frame)
    {
        const FString Name=FString::Printf(TEXT("T_Fairytale_Shoulder%sIdle_%03d_v001"),Near?TEXT("Near"):TEXT("Far"),Frame);
        return FString(TEXT("/Game/Production/ArtTrials/EV048/v001/HeroShoulderIdle/"))+Name+TEXT(".")+Name;
    }
    inline FString HeroNearLimbPath(bool Bracer,int32 Frame)
    {
        const FString Name=FString::Printf(TEXT("T_Fairytale_Near%sIdle_%03d_v002"),Bracer?TEXT("Bracer"):TEXT("Shin"),Frame);
        return FString(TEXT("/Game/Production/ArtTrials/EV048/v003/HeroNearLimbIdle/"))+Name+TEXT(".")+Name;
    }
}

struct FFairytaleLookdevActorDraw
{
    FString TexturePath, Clip, ChestTexturePath, NearShoulderTexturePath, FarShoulderTexturePath;
    FString NearBracerTexturePath,NearShinTexturePath;
    int32 NearBracerFrame=-1,NearShinFrame=-1;
    int32 Frame=-1, NativeFacing=0, Facing=0;
    int64 Sample=-1;
    double CanvasSize=0.;
    FVector2D Root=FVector2D::ZeroVector, Ground=FVector2D::ZeroVector;
    FVector2D GroundScreen=FVector2D::ZeroVector, TopScreen=FVector2D::ZeroVector;
    bool TextureReady=false, Flipped=false;
    bool ChestTextureReady=false, ChestDrawn=false;
    bool NearShoulderReady=false,FarShoulderReady=false,NearShoulderDrawn=false,FarShoulderDrawn=false;
    bool NearBracerReady=false,NearShinReady=false,NearBracerDrawn=false,NearShinDrawn=false;
};

struct FFairytaleLookdevDraw
{
    bool Active=false, ConfigurationConfirmed=false, HeroWalkActive=false;
    bool HeroChestActive=false, HeroShoulderActive=false, HeroDarkPosition=false, ChestVisibleChoice=false;
    bool NearShoulderOnly=false,FarShoulderOnly=false;
    bool HeroNearLimbActive=false,LimbVisibleChoice=false,NearBracerOnly=false,NearShinOnly=false;
    uint64 Serial=0;
    double Wall=0., AnimationElapsed=0., UIScale=0.;
    FVector2D Viewport=FVector2D::ZeroVector;
    FFairytaleLookdevActorDraw Hero, Stone;
};
