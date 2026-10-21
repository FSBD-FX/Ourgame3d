#pragma once
#include "CoreMinimal.h"

// Generated only from retained native155 Ready and native157 Primary1 measurements.
// TRIAL DATA: thumb anatomy, hidden grip axis, blade sign and fist semantic masks are NOT accepted.
// Axis is copied exactly; no normalization, rotation, blade-end sign choice or V007 marker reuse.
// Root is the fixed display pivot, not a claim of exact per-frame sole-center registration.
namespace DungeonFairytaleSwordBodyV001
{
struct FMarker
{
    FVector2D Root;
    FVector2D Grip;
    FVector2D Axis;
    TArray<FVector2D> FistPolygon;
};

inline constexpr double CanvasSize = 72. * 512. / 416.;

inline int32 Count(const FString& Clip)
{
    if (Clip == TEXT("sword_ready_idle")) return 4;
    if (Clip == TEXT("sword_primary_1")) return 6;
    return 0;
}

inline const FMarker* Find(const FString& Clip, int32 Index)
{
    if (Index < 0) return nullptr;
    if (Clip == TEXT("sword_ready_idle"))
    {
        // JSONSha256: f0e8a250eaea3b2315ea9c9cf86eab0514ba4f6a0b53a14cc322aedcda8c4f7d
        // JSONSource: F:/Ourgame/source-assets/production/fairytale-sword-v001/ready-measurement-v001/ready-marker-proposal-v001.json
        static const FMarker ReadyMarkers[] =
        {
            // Frame 0 SourceSha256: 7b747dd4bdbfa326653661583afc0b79a3baf9927eea65d931b96ecc78d6130f
            FMarker{FVector2D(256.0, 464.0), FVector2D(258.0, 282.0), FVector2D(0.0, -1.0), TArray<FVector2D>{FVector2D(242.0, 256.0), FVector2D(264.0, 256.0), FVector2D(274.0, 262.0), FVector2D(279.0, 270.0), FVector2D(278.0, 281.0), FVector2D(274.0, 286.0), FVector2D(272.0, 297.0), FVector2D(266.0, 303.0), FVector2D(246.0, 305.0), FVector2D(232.0, 301.0), FVector2D(225.0, 295.0), FVector2D(225.0, 278.0), FVector2D(231.0, 267.0)}},
            // Frame 1 SourceSha256: 04c48e214cfd693dab4afacb7f2bb3abca7ab22e717e982a1d394e5174449be1
            FMarker{FVector2D(256.0, 464.0), FVector2D(258.0, 281.0), FVector2D(0.0, -1.0), TArray<FVector2D>{FVector2D(243.0, 256.0), FVector2D(265.0, 257.0), FVector2D(275.0, 263.0), FVector2D(280.0, 271.0), FVector2D(279.0, 282.0), FVector2D(274.0, 287.0), FVector2D(272.0, 297.0), FVector2D(266.0, 302.0), FVector2D(246.0, 304.0), FVector2D(232.0, 300.0), FVector2D(225.0, 294.0), FVector2D(225.0, 277.0), FVector2D(232.0, 266.0)}},
            // Frame 2 SourceSha256: fd00251555fb2254206f5d8e981a564b28b18d42d19af8b52ca294fb048ba972
            FMarker{FVector2D(256.0, 464.0), FVector2D(259.0, 284.0), FVector2D(0.0, -1.0), TArray<FVector2D>{FVector2D(245.0, 259.0), FVector2D(265.0, 259.0), FVector2D(275.0, 264.0), FVector2D(280.0, 272.0), FVector2D(279.0, 284.0), FVector2D(275.0, 288.0), FVector2D(272.0, 299.0), FVector2D(266.0, 304.0), FVector2D(247.0, 306.0), FVector2D(232.0, 302.0), FVector2D(225.0, 296.0), FVector2D(225.0, 279.0), FVector2D(233.0, 268.0)}},
            // Frame 3 SourceSha256: 86e8c702e1455bf6fde682f0cd384d5e0f41ba7e0935af6b5cb0704b4e3970d6
            FMarker{FVector2D(256.0, 464.0), FVector2D(258.0, 282.0), FVector2D(0.0, -1.0), TArray<FVector2D>{FVector2D(243.0, 256.0), FVector2D(264.0, 256.0), FVector2D(274.0, 262.0), FVector2D(279.0, 270.0), FVector2D(279.0, 282.0), FVector2D(274.0, 286.0), FVector2D(272.0, 297.0), FVector2D(266.0, 303.0), FVector2D(246.0, 305.0), FVector2D(232.0, 301.0), FVector2D(225.0, 295.0), FVector2D(225.0, 278.0), FVector2D(231.0, 267.0)}},
        };
        return Index < UE_ARRAY_COUNT(ReadyMarkers) ? &ReadyMarkers[Index] : nullptr;
    }
    if (Clip == TEXT("sword_primary_1"))
    {
        // JSONSha256: 8fddb258171d04c7f72b50b2b5e8a10925bdb010bd061c03c2f66ecf2a05d340
        // JSONSource: F:/Ourgame/source-assets/production/fairytale-sword-v001/primary1-measurement-v002/primary1-marker-proposal-v002.json
        static const FMarker Primary1Markers[] =
        {
            // Frame 0 SourceSha256: cbfdd1c68004597e7d240323cfd39d53c145ac0212bb853ad2dca7ebc2bf7f87
            FMarker{FVector2D(256.0, 464.0), FVector2D(258.0, 281.0), FVector2D(0.0, -1.0), TArray<FVector2D>{FVector2D(243.0, 255.0), FVector2D(264.0, 256.0), FVector2D(275.0, 262.0), FVector2D(280.0, 270.0), FVector2D(278.0, 282.0), FVector2D(274.0, 286.0), FVector2D(272.0, 298.0), FVector2D(266.0, 303.0), FVector2D(246.0, 305.0), FVector2D(232.0, 301.0), FVector2D(225.0, 295.0), FVector2D(225.0, 278.0), FVector2D(231.0, 267.0)}},
            // Frame 1 SourceSha256: 0f7e090b9bd18a37d35b8caf444679b309d1909c4f8f7d97e7eebc68a586445d
            FMarker{FVector2D(256.0, 464.0), FVector2D(202.0, 125.0), FVector2D(0.5, -0.8660254), TArray<FVector2D>{FVector2D(193.0, 102.0), FVector2D(205.0, 101.0), FVector2D(217.0, 106.0), FVector2D(226.0, 113.0), FVector2D(229.0, 120.0), FVector2D(225.0, 129.0), FVector2D(221.0, 135.0), FVector2D(215.0, 143.0), FVector2D(204.0, 148.0), FVector2D(192.0, 147.0), FVector2D(179.0, 141.0), FVector2D(176.0, 132.0), FVector2D(180.0, 120.0), FVector2D(186.0, 109.0)}},
            // Frame 2 SourceSha256: f1b7ae21775342e75d91edfb76b48a640ccebb4aa81110931733548203a21bcc
            FMarker{FVector2D(256.0, 464.0), FVector2D(291.0, 264.0), FVector2D(0.65, -0.7599342), TArray<FVector2D>{FVector2D(282.0, 241.0), FVector2D(300.0, 242.0), FVector2D(310.0, 249.0), FVector2D(317.0, 259.0), FVector2D(315.0, 269.0), FVector2D(310.0, 279.0), FVector2D(303.0, 287.0), FVector2D(294.0, 290.0), FVector2D(280.0, 285.0), FVector2D(269.0, 280.0), FVector2D(262.0, 271.0), FVector2D(264.0, 257.0), FVector2D(271.0, 247.0)}},
            // Frame 3 SourceSha256: ddc467f578cff5c74d95b6342ada0be7d26d91945af2a6cecfaf038a83658a1e
            FMarker{FVector2D(256.0, 464.0), FVector2D(352.0, 330.0), FVector2D(0.94, -0.3411744), TArray<FVector2D>{FVector2D(341.0, 307.0), FVector2D(362.0, 308.0), FVector2D(374.0, 313.0), FVector2D(380.0, 322.0), FVector2D(378.0, 335.0), FVector2D(372.0, 344.0), FVector2D(365.0, 349.0), FVector2D(362.0, 354.0), FVector2D(353.0, 357.0), FVector2D(345.0, 352.0), FVector2D(335.0, 345.0), FVector2D(326.0, 337.0), FVector2D(325.0, 325.0), FVector2D(330.0, 314.0)}},
            // Frame 4 SourceSha256: 7e45683b3b0a8ffbf64ba19970925032ddb13ef0ec8e6ebb93d00fe1d12cd212
            FMarker{FVector2D(256.0, 464.0), FVector2D(258.0, 280.0), FVector2D(0.0, -1.0), TArray<FVector2D>{FVector2D(243.0, 254.0), FVector2D(264.0, 255.0), FVector2D(275.0, 261.0), FVector2D(280.0, 269.0), FVector2D(279.0, 281.0), FVector2D(274.0, 286.0), FVector2D(272.0, 297.0), FVector2D(266.0, 302.0), FVector2D(246.0, 304.0), FVector2D(232.0, 300.0), FVector2D(225.0, 294.0), FVector2D(225.0, 277.0), FVector2D(231.0, 266.0)}},
            // Frame 5 SourceSha256: 58e8bda396e87b0d1faaf1b476acf7ec793d2e64da9ae07e869d23e4c56700d0
            FMarker{FVector2D(256.0, 464.0), FVector2D(258.0, 281.0), FVector2D(0.0, -1.0), TArray<FVector2D>{FVector2D(243.0, 255.0), FVector2D(264.0, 256.0), FVector2D(275.0, 262.0), FVector2D(280.0, 270.0), FVector2D(279.0, 282.0), FVector2D(274.0, 287.0), FVector2D(272.0, 298.0), FVector2D(266.0, 303.0), FVector2D(246.0, 305.0), FVector2D(232.0, 301.0), FVector2D(225.0, 295.0), FVector2D(225.0, 278.0), FVector2D(231.0, 267.0)}},
        };
        return Index < UE_ARRAY_COUNT(Primary1Markers) ? &Primary1Markers[Index] : nullptr;
    }
    return nullptr;
}
} // namespace DungeonFairytaleSwordBodyV001
