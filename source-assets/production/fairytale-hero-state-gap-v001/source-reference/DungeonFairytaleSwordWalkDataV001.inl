#pragma once
// Root-authored immutable native visual trial. Source/data pins in walk-profile-root-v001.
// Unique import manifest SHA256 0098a1f16d99c59a55c2e7b43d9709a4d3c71d9fc14a5d148b84326b57f1f680
// Native import receipt SHA256 df3b5bc9d9c6cd6f5bcec79f87e18d92c7fca5eba61d97af5475977998d036bc
// 80 is art-tuned cycle distance, never movement speed or proof of foot locking.
// Root256,464 is a display pivot. Grip/Axis are artist attachment design.
namespace DungeonFairytaleSwordWalkV001
{
inline const FProfile& Profile()
{
    static const FProfile Frozen=[]
    {
        FProfile P;
        P.Gait.CycleDistance=80.; P.Gait.CycleSeconds=.498;
        P.Gait.Durations={.083,.083,.083,.083,.083,.083};
        { auto& F=P.Frames[0];
          F.Body=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_Body_000_v001.T_Fairytale_Walk_Body_000_v001");
          F.BodyRest=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_BodyRest_000_v001.T_Fairytale_Walk_BodyRest_000_v001");
          F.NearArmWithoutHand=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_NearArmWithoutHand_000_v001.T_Fairytale_Walk_NearArmWithoutHand_000_v001");
          F.HelmetForeground=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_HelmetForeground_000_v001.T_Fairytale_Walk_HelmetForeground_000_v001");
          F.NearHand=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_NearHand_000_v001.T_Fairytale_Walk_NearHand_000_v001");
          F.ShoulderFar=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_ShoulderFar_000_v001.T_Fairytale_Walk_ShoulderFar_000_v001");
          F.Chest=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_Chest_000_v001.T_Fairytale_Walk_Chest_000_v001");
          F.ShoulderNear=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_ShoulderNear_000_v001.T_Fairytale_Walk_ShoulderNear_000_v001");
          F.Marker= DungeonFairytaleSwordBodyV001::FMarker{FVector2D(256.,464.),FVector2D(143.,325.),FVector2D(0.8,-0.6),TArray<FVector2D>{}};
          F.MeasurementsSupplied=true; }
        { auto& F=P.Frames[1];
          F.Body=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_Body_001_v001.T_Fairytale_Walk_Body_001_v001");
          F.BodyRest=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_BodyRest_001_v001.T_Fairytale_Walk_BodyRest_001_v001");
          F.NearArmWithoutHand=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_NearArmWithoutHand_001_v001.T_Fairytale_Walk_NearArmWithoutHand_001_v001");
          F.HelmetForeground=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_HelmetForeground_001_v001.T_Fairytale_Walk_HelmetForeground_001_v001");
          F.NearHand=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_NearHand_001_v001.T_Fairytale_Walk_NearHand_001_v001");
          F.ShoulderFar=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_ShoulderFar_001_v001.T_Fairytale_Walk_ShoulderFar_001_v001");
          F.Chest=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_Chest_001_v001.T_Fairytale_Walk_Chest_001_v001");
          F.ShoulderNear=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_ShoulderNear_001_v001.T_Fairytale_Walk_ShoulderNear_001_v001");
          F.Marker= DungeonFairytaleSwordBodyV001::FMarker{FVector2D(256.,464.),FVector2D(176.,344.),FVector2D(0.8,-0.6),TArray<FVector2D>{}};
          F.MeasurementsSupplied=true; }
        { auto& F=P.Frames[2];
          F.Body=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_Body_002_v001.T_Fairytale_Walk_Body_002_v001");
          F.BodyRest=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_BodyRest_002_v001.T_Fairytale_Walk_BodyRest_002_v001");
          F.NearArmWithoutHand=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_NearArmWithoutHand_002_v001.T_Fairytale_Walk_NearArmWithoutHand_002_v001");
          F.HelmetForeground=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_HelmetForeground_002_v001.T_Fairytale_Walk_HelmetForeground_002_v001");
          F.NearHand=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_NearHand_002_v001.T_Fairytale_Walk_NearHand_002_v001");
          F.ShoulderFar=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_ShoulderFar_002_v001.T_Fairytale_Walk_ShoulderFar_002_v001");
          F.Chest=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_Chest_002_v001.T_Fairytale_Walk_Chest_002_v001");
          F.ShoulderNear=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_ShoulderNear_002_v001.T_Fairytale_Walk_ShoulderNear_002_v001");
          F.Marker= DungeonFairytaleSwordBodyV001::FMarker{FVector2D(256.,464.),FVector2D(320.,317.),FVector2D(0.8,-0.6),TArray<FVector2D>{}};
          F.MeasurementsSupplied=true; }
        { auto& F=P.Frames[3];
          F.Body=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_Body_003_v001.T_Fairytale_Walk_Body_003_v001");
          F.BodyRest=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_BodyRest_003_v001.T_Fairytale_Walk_BodyRest_003_v001");
          F.NearArmWithoutHand=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_NearArmWithoutHand_003_v001.T_Fairytale_Walk_NearArmWithoutHand_003_v001");
          F.HelmetForeground=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_HelmetForeground_003_v001.T_Fairytale_Walk_HelmetForeground_003_v001");
          F.NearHand=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_NearHand_003_v001.T_Fairytale_Walk_NearHand_003_v001");
          F.ShoulderFar=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_ShoulderFar_003_v001.T_Fairytale_Walk_ShoulderFar_003_v001");
          F.Chest=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_Chest_003_v001.T_Fairytale_Walk_Chest_003_v001");
          F.ShoulderNear=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_ShoulderNear_003_v001.T_Fairytale_Walk_ShoulderNear_003_v001");
          F.Marker= DungeonFairytaleSwordBodyV001::FMarker{FVector2D(256.,464.),FVector2D(337.,318.),FVector2D(0.8,-0.6),TArray<FVector2D>{}};
          F.MeasurementsSupplied=true; }
        { auto& F=P.Frames[4];
          F.Body=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_Body_004_v001.T_Fairytale_Walk_Body_004_v001");
          F.BodyRest=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_BodyRest_004_v001.T_Fairytale_Walk_BodyRest_004_v001");
          F.NearArmWithoutHand=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_NearArmWithoutHand_004_v001.T_Fairytale_Walk_NearArmWithoutHand_004_v001");
          F.HelmetForeground=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_HelmetForeground_004_v001.T_Fairytale_Walk_HelmetForeground_004_v001");
          F.NearHand=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_NearHand_004_v001.T_Fairytale_Walk_NearHand_004_v001");
          F.ShoulderFar=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_ShoulderFar_004_v001.T_Fairytale_Walk_ShoulderFar_004_v001");
          F.Chest=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_Chest_004_v001.T_Fairytale_Walk_Chest_004_v001");
          F.ShoulderNear=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_ShoulderNear_004_v001.T_Fairytale_Walk_ShoulderNear_004_v001");
          F.Marker= DungeonFairytaleSwordBodyV001::FMarker{FVector2D(256.,464.),FVector2D(184.,351.),FVector2D(0.8,-0.6),TArray<FVector2D>{}};
          F.MeasurementsSupplied=true; }
        { auto& F=P.Frames[5];
          F.Body=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_Body_005_v001.T_Fairytale_Walk_Body_005_v001");
          F.BodyRest=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_BodyRest_005_v001.T_Fairytale_Walk_BodyRest_005_v001");
          F.NearArmWithoutHand=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_NearArmWithoutHand_005_v001.T_Fairytale_Walk_NearArmWithoutHand_005_v001");
          F.HelmetForeground=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_HelmetForeground_005_v001.T_Fairytale_Walk_HelmetForeground_005_v001");
          F.NearHand=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_NearHand_005_v001.T_Fairytale_Walk_NearHand_005_v001");
          F.ShoulderFar=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_ShoulderFar_005_v001.T_Fairytale_Walk_ShoulderFar_005_v001");
          F.Chest=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_Chest_005_v001.T_Fairytale_Walk_Chest_005_v001");
          F.ShoulderNear=TEXT("/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk/T_Fairytale_Walk_ShoulderNear_005_v001.T_Fairytale_Walk_ShoulderNear_005_v001");
          F.Marker= DungeonFairytaleSwordBodyV001::FMarker{FVector2D(256.,464.),FVector2D(151.,327.),FVector2D(0.8,-0.6),TArray<FVector2D>{}};
          F.MeasurementsSupplied=true; }
        P.SourceClosureVerified=true; return P;
    }();
    return Frozen;
}
}
