// ArcDesignSHA256: fd12ceaf1ac5a970e63ff5109fdf5a5f6a2b5eb9687e05d6da1dbcd9d6177df2
#pragma once
#include "DungeonFairytaleSwordBodyV001.inl"

// Root rising-axis diagnostic trial v002; original native169 body/palm/polygon data retained.
// V001 supplies FMarker TYPE only. No old human/source marker DATA is reused.
// Grip is visible-palm MANUAL candidate (+/-3 or4px), not an actual grasp-cylinder center.
// FistPolygon is an uncertain visible-glove outline (+/-4px), NOT exact ownership/thumb mask.
// Axis is Root arc-design-v002.json diagnostic only, never a measured blade/bone/accepted grasp.
// Pivot256,464 / body72 / SwordScale.50 / sword sourceGrip99,256 remain fixed.
// Actual kernelStage1 timing75/75/60/60/135/135ms; standard100x6 preview FAILED timing.
// MarkerJSON SHA256: e55dcb6e96936c22d1af1c6447617185db5a2c47d4e8632601ddb856a6934ea8
// Measurement SHA256: 08fedc585b5a839775b71f2ae394393b342c168f3d1b070da6400acc9fb75972
namespace DungeonFairytaleSwordPrimary2V002
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
        // Frame0 SourceSHA256: feb60b9e2ddb7768717249245e2b53876129b50b1a96e17538ed2ddbdb0a21b5; Grip +/-3px; polygon +/-4px.
        FMarker{FVector2D(256.0, 464.0), FVector2D(224.0, 318.0), FVector2D(0.94, -0.341), TArray<FVector2D>{FVector2D(205.0, 300.0), FVector2D(222.0, 297.0), FVector2D(238.0, 301.0), FVector2D(249.0, 310.0), FVector2D(252.0, 322.0), FVector2D(247.0, 334.0), FVector2D(240.0, 337.0), FVector2D(229.0, 341.0), FVector2D(218.0, 341.0), FVector2D(207.0, 337.0), FVector2D(200.0, 329.0), FVector2D(197.0, 319.0), FVector2D(198.0, 309.0)}},
        // Frame1 SourceSHA256: 7df5c42fb65d0cdba05412f124990b06430d9ab05d0a72e1bc0f88de7ed87c2c; Grip +/-3px; polygon +/-4px.
        FMarker{FVector2D(256.0, 464.0), FVector2D(252.0, 274.0), FVector2D(0.35, 0.937), TArray<FVector2D>{FVector2D(239.0, 255.0), FVector2D(249.0, 250.0), FVector2D(263.0, 252.0), FVector2D(273.0, 259.0), FVector2D(275.0, 273.0), FVector2D(272.0, 287.0), FVector2D(265.0, 294.0), FVector2D(249.0, 298.0), FVector2D(237.0, 296.0), FVector2D(229.0, 288.0), FVector2D(230.0, 269.0)}},
        // Frame2 SourceSHA256: b603d5490e942666478bff4cfd68244c929026fe1fed884328fdab679fe9e381; Grip +/-4px; polygon +/-4px.
        FMarker{FVector2D(256.0, 464.0), FVector2D(358.0, 277.0), FVector2D(0.8, 0.6), TArray<FVector2D>{FVector2D(341.0, 260.0), FVector2D(349.0, 256.0), FVector2D(360.0, 258.0), FVector2D(371.0, 263.0), FVector2D(379.0, 271.0), FVector2D(380.0, 283.0), FVector2D(375.0, 294.0), FVector2D(366.0, 299.0), FVector2D(354.0, 298.0), FVector2D(345.0, 293.0), FVector2D(338.0, 282.0), FVector2D(338.0, 268.0)}},
        // Frame3 SourceSHA256: 41fa6afc2ac0803507036025bcfa40093cab99cbde862b9c57b4c0bf18daa1c4; Grip +/-4px; polygon +/-4px.
        FMarker{FVector2D(256.0, 464.0), FVector2D(345.0, 277.0), FVector2D(0.65, -0.76), TArray<FVector2D>{FVector2D(329.0, 255.0), FVector2D(347.0, 255.0), FVector2D(361.0, 259.0), FVector2D(370.0, 267.0), FVector2D(374.0, 278.0), FVector2D(370.0, 290.0), FVector2D(360.0, 297.0), FVector2D(346.0, 298.0), FVector2D(332.0, 294.0), FVector2D(322.0, 287.0), FVector2D(318.0, 275.0), FVector2D(319.0, 264.0)}},
        // Frame4 SourceSHA256: f67684cfa3511ee1eec05a3c2c445de838378d2cec1b71fd2d13407a2aaab747; Grip +/-3px; polygon +/-4px.
        FMarker{FVector2D(256.0, 464.0), FVector2D(250.0, 301.0), FVector2D(0.99, 0.1), TArray<FVector2D>{FVector2D(235.0, 280.0), FVector2D(247.0, 280.0), FVector2D(260.0, 285.0), FVector2D(271.0, 293.0), FVector2D(279.0, 303.0), FVector2D(277.0, 314.0), FVector2D(270.0, 322.0), FVector2D(259.0, 327.0), FVector2D(249.0, 325.0), FVector2D(241.0, 320.0), FVector2D(232.0, 312.0), FVector2D(225.0, 300.0), FVector2D(226.0, 289.0)}},
        // Frame5 SourceSHA256: 1ed340cae841ff5554dc9c35baee26bdfb35648fddc86cece6344a57c16fee57; Grip +/-3px; polygon +/-4px.
        FMarker{FVector2D(256.0, 464.0), FVector2D(224.0, 318.0), FVector2D(0.94, -0.341), TArray<FVector2D>{FVector2D(205.0, 300.0), FVector2D(223.0, 297.0), FVector2D(239.0, 301.0), FVector2D(250.0, 310.0), FVector2D(253.0, 322.0), FVector2D(248.0, 334.0), FVector2D(241.0, 338.0), FVector2D(230.0, 342.0), FVector2D(218.0, 342.0), FVector2D(207.0, 337.0), FVector2D(200.0, 329.0), FVector2D(197.0, 319.0), FVector2D(198.0, 309.0)}},
    };
    return &Markers[Index];
}
} // namespace DungeonFairytaleSwordPrimary2V002
