#pragma once
#include "DungeonFairytaleSwordBodyV001.inl"

// STATIC DATA CANDIDATE ONLY: retained native171 body; not installed in UnrealGame/Source.
// V001 supplies FMarker TYPE only. No old human/body/grip/axis DATA is reused.
// Actual171 visible palm candidate +/-3px; uncertain glove polygon +/-4px, NOT complete AA ownership.
// Actual thumb/handle/blade axis remain null. Axis below is Root explicit DESIGN only, not bone.
// Body then independent Sword then current-body same-original-UV near-fist replay: bounded fit trial.
// Root256,464 / maximum body72 / SwordScale.50 / independent sourceGrip99,256 fixed.
// KernelStage1 durations75/75/60/60/135/135ms; standard100x6 preview does NOT pass timing.
// P1->P2 boundaries, grip, helmet clearance, foot-lock and full motion remain unaccepted.
// MarkerJSON SHA256: 0b14858bff16be273655c17c2d21b769c4ab90e62687b727f4f2314ad9cffcd0
// Measurement SHA256: 9a776415005eb1a71228360d7b14f468bc6d34db76afa554555d87bdafd2e8e4
namespace DungeonFairytaleSwordPrimary2V003
{
using FMarker = DungeonFairytaleSwordBodyV001::FMarker;
inline constexpr double CanvasSize = 72. * 512. / 416.;
inline constexpr double SwordScale = 0.50;
inline FVector2D IndependentSwordGrip() { return FVector2D(99., 256.); }
inline int32 Count(const FString& Clip) { return Clip == TEXT("sword_primary_2") ? 6 : 0; }
inline const FMarker* Find(const FString& Clip, int32 Index)
{
    if (Clip != TEXT("sword_primary_2") || Index < 0 || Index >= 6) return nullptr;
    static const FMarker Markers[] =
    {
        // Frame0 SourceSHA256: 1dd5a9f21d56ed52d8e3142c2f9c42a28037b824e606147c06920142e9a7999e; Grip +/-3px; polygon +/-4px.
        FMarker{FVector2D(256.0, 464.0), FVector2D(207.0, 313.0), FVector2D(0.94, -0.341), TArray<FVector2D>{FVector2D(194.0, 289.0), FVector2D(207.0, 292.0), FVector2D(220.0, 298.0), FVector2D(230.0, 305.0), FVector2D(235.0, 313.0), FVector2D(231.0, 320.0), FVector2D(229.0, 325.0), FVector2D(223.0, 330.0), FVector2D(215.0, 331.0), FVector2D(208.0, 329.0), FVector2D(202.0, 335.0), FVector2D(194.0, 334.0), FVector2D(184.0, 328.0), FVector2D(179.0, 320.0), FVector2D(178.0, 310.0), FVector2D(180.0, 301.0), FVector2D(186.0, 295.0)}},
        // Frame1 SourceSHA256: b7d98a14749e1e8b24f191a9119cb379ef70abb64717fd353303c7a2b05e14e0; Grip +/-3px; polygon +/-4px.
        FMarker{FVector2D(256.0, 464.0), FVector2D(167.0, 333.0), FVector2D(0.35, 0.937), TArray<FVector2D>{FVector2D(157.0, 311.0), FVector2D(168.0, 311.0), FVector2D(177.0, 315.0), FVector2D(184.0, 321.0), FVector2D(190.0, 327.0), FVector2D(193.0, 336.0), FVector2D(189.0, 345.0), FVector2D(182.0, 352.0), FVector2D(170.0, 356.0), FVector2D(159.0, 353.0), FVector2D(151.0, 348.0), FVector2D(146.0, 340.0), FVector2D(145.0, 330.0), FVector2D(148.0, 320.0)}},
        // Frame2 SourceSHA256: 99a080b206c346e7bac24719085197e2b8faffc48765683a0c566a9659d851d4; Grip +/-3px; polygon +/-4px.
        FMarker{FVector2D(256.0, 464.0), FVector2D(281.0, 318.0), FVector2D(0.8, 0.6), TArray<FVector2D>{FVector2D(270.0, 293.0), FVector2D(282.0, 294.0), FVector2D(293.0, 300.0), FVector2D(302.0, 307.0), FVector2D(307.0, 315.0), FVector2D(304.0, 323.0), FVector2D(297.0, 329.0), FVector2D(292.0, 333.0), FVector2D(286.0, 337.0), FVector2D(276.0, 340.0), FVector2D(267.0, 337.0), FVector2D(259.0, 333.0), FVector2D(253.0, 324.0), FVector2D(251.0, 316.0), FVector2D(255.0, 305.0), FVector2D(262.0, 297.0)}},
        // Frame3 SourceSHA256: f0c10731650aac7f8b06b30c63da4548a95e8a7aa48ad38c0621b1c9ab202c85; Grip +/-3px; polygon +/-4px.
        FMarker{FVector2D(256.0, 464.0), FVector2D(311.0, 253.0), FVector2D(0.9, -0.436), TArray<FVector2D>{FVector2D(301.0, 226.0), FVector2D(312.0, 227.0), FVector2D(322.0, 230.0), FVector2D(329.0, 238.0), FVector2D(334.0, 246.0), FVector2D(335.0, 254.0), FVector2D(331.0, 263.0), FVector2D(325.0, 270.0), FVector2D(315.0, 276.0), FVector2D(305.0, 278.0), FVector2D(294.0, 274.0), FVector2D(288.0, 267.0), FVector2D(286.0, 257.0), FVector2D(290.0, 244.0), FVector2D(292.0, 233.0)}},
        // Frame4 SourceSHA256: cacb7d9eb5cff2a38c54acf50f96915fa859f8fac5278939f1184bc97e650a84; Grip +/-3px; polygon +/-4px.
        FMarker{FVector2D(256.0, 464.0), FVector2D(280.0, 275.0), FVector2D(0.95, -0.312), TArray<FVector2D>{FVector2D(275.0, 248.0), FVector2D(286.0, 248.0), FVector2D(295.0, 254.0), FVector2D(301.0, 262.0), FVector2D(304.0, 273.0), FVector2D(301.0, 283.0), FVector2D(295.0, 289.0), FVector2D(290.0, 294.0), FVector2D(282.0, 298.0), FVector2D(271.0, 298.0), FVector2D(260.0, 292.0), FVector2D(256.0, 282.0), FVector2D(260.0, 267.0), FVector2D(264.0, 258.0), FVector2D(269.0, 252.0)}},
        // Frame5 SourceSHA256: b8546838bd72dde4ce72c4c4055d18f916a94e6c3b3b54f5feeb1d5c2cc59dab; Grip +/-3px; polygon +/-4px.
        FMarker{FVector2D(256.0, 464.0), FVector2D(207.0, 313.0), FVector2D(0.94, -0.341), TArray<FVector2D>{FVector2D(194.0, 289.0), FVector2D(207.0, 291.0), FVector2D(219.0, 297.0), FVector2D(230.0, 305.0), FVector2D(235.0, 313.0), FVector2D(231.0, 320.0), FVector2D(229.0, 325.0), FVector2D(223.0, 331.0), FVector2D(215.0, 333.0), FVector2D(207.0, 331.0), FVector2D(201.0, 335.0), FVector2D(193.0, 334.0), FVector2D(184.0, 328.0), FVector2D(179.0, 320.0), FVector2D(178.0, 309.0), FVector2D(181.0, 300.0), FVector2D(187.0, 294.0)}},
    };
    return &Markers[Index];
}
} // namespace DungeonFairytaleSwordPrimary2V003
