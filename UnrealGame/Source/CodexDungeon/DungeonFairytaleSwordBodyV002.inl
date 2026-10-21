#pragma once
#include "DungeonFairytaleSwordBodyV001.inl"

// Native158 Ready + native159 Primary1 trial candidates only; no old marker DATA reused.
// V001 supplies the FMarker TYPE only. These arrays use the new retained JSON values.
// Axis is an explicit directed trial design choice: actual handle/blade direction is null.
// Thumb anatomy and exact fist semantic masks remain unaccepted; original uncertainty remains.
// Root is a fixed display pivot, not a measured physical foot joint. No per-frame registration.
// Standard SG Primary1 GIF/atlas timing failed (6x100ms); actual combat phase uses unchanged
// request85/85/60/60/155/155ms through GetPrimaryPoseFrame, never this preview clock.
namespace DungeonFairytaleSwordBodyV002
{
using FMarker = DungeonFairytaleSwordBodyV001::FMarker;

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
        // JSONSha256: 3aff15e506328c9b37aca2e040b56ad6aeca0f6b6d195865ef362fe74adf1e82
        // JSONSource: F:/Ourgame/source-assets/production/fairytale-sword-v001/ready-measurement-v002/ready-marker-proposal-v002.json
        static const FMarker ReadyMarkers[] =
        {
            // Frame 0 SourceSha256: d3f766506a9cc623c38787836a9c23c0126d185d1bdf7e8946181efd554338c5
            // SourcePath: F:/Ourgame/source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-0.png
            FMarker{FVector2D(256.0, 464.0), FVector2D(212.0, 313.0), FVector2D(0.94, -0.341), TArray<FVector2D>{FVector2D(192.0, 290.0), FVector2D(207.0, 290.0), FVector2D(218.0, 295.0), FVector2D(226.0, 302.0), FVector2D(233.0, 311.0), FVector2D(235.0, 317.0), FVector2D(231.0, 324.0), FVector2D(224.0, 330.0), FVector2D(216.0, 330.0), FVector2D(208.0, 333.0), FVector2D(198.0, 334.0), FVector2D(190.0, 329.0), FVector2D(183.0, 321.0), FVector2D(180.0, 309.0), FVector2D(184.0, 298.0)}},
            // Frame 1 SourceSha256: edc706a89da26ab56613f8925c44c9984ddd1abc3ed655f5e92cd9d69a30d5b1
            // SourcePath: F:/Ourgame/source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-1.png
            FMarker{FVector2D(256.0, 464.0), FVector2D(212.0, 312.0), FVector2D(0.94, -0.341), TArray<FVector2D>{FVector2D(193.0, 289.0), FVector2D(209.0, 289.0), FVector2D(220.0, 294.0), FVector2D(227.0, 302.0), FVector2D(234.0, 310.0), FVector2D(234.0, 318.0), FVector2D(230.0, 325.0), FVector2D(223.0, 330.0), FVector2D(215.0, 330.0), FVector2D(207.0, 332.0), FVector2D(197.0, 333.0), FVector2D(189.0, 328.0), FVector2D(183.0, 321.0), FVector2D(181.0, 308.0), FVector2D(185.0, 297.0)}},
            // Frame 2 SourceSha256: 048d606c8ea449a2c9b23890e98c5332f3e84bd986a8b765c909495097dd113e
            // SourcePath: F:/Ourgame/source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-2.png
            FMarker{FVector2D(256.0, 464.0), FVector2D(207.0, 316.0), FVector2D(0.94, -0.341), TArray<FVector2D>{FVector2D(187.0, 292.0), FVector2D(203.0, 293.0), FVector2D(213.0, 297.0), FVector2D(221.0, 304.0), FVector2D(229.0, 313.0), FVector2D(229.0, 319.0), FVector2D(225.0, 328.0), FVector2D(218.0, 332.0), FVector2D(211.0, 335.0), FVector2D(202.0, 335.0), FVector2D(192.0, 336.0), FVector2D(184.0, 331.0), FVector2D(178.0, 324.0), FVector2D(176.0, 311.0), FVector2D(180.0, 301.0)}},
            // Frame 3 SourceSha256: cbff38cc538db16d8f58c89dc1a94f5cd35f6756976d8fe8baa02ec5dcadd960
            // SourcePath: F:/Ourgame/source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-3.png
            FMarker{FVector2D(256.0, 464.0), FVector2D(214.0, 312.0), FVector2D(0.94, -0.341), TArray<FVector2D>{FVector2D(194.0, 288.0), FVector2D(211.0, 289.0), FVector2D(221.0, 294.0), FVector2D(229.0, 301.0), FVector2D(236.0, 310.0), FVector2D(236.0, 317.0), FVector2D(232.0, 324.0), FVector2D(225.0, 329.0), FVector2D(218.0, 329.0), FVector2D(210.0, 332.0), FVector2D(200.0, 334.0), FVector2D(191.0, 329.0), FVector2D(185.0, 322.0), FVector2D(183.0, 309.0), FVector2D(187.0, 298.0)}},
        };
        return Index < UE_ARRAY_COUNT(ReadyMarkers) ? &ReadyMarkers[Index] : nullptr;
    }
    if (Clip == TEXT("sword_primary_1"))
    {
        // JSONSha256: 730f1be4bc17ab4bb2fb520b22c810dc8f392f9e6d1886e3e303ad06cc05b4aa
        // JSONSource: F:/Ourgame/source-assets/production/fairytale-sword-v001/primary1-measurement-v003/primary1-marker-proposal-v003.json
        static const FMarker Primary1Markers[] =
        {
            // Frame 0 SourceSha256: 31fba4718be787b98fd92c551a6515a429c29385cb0e67365fc0b8533fd8b5c3
            // SourcePath: F:/Ourgame/source-assets/production/fairytale-sword-v001/run-primary1-v003/curated/frame-0.png
            FMarker{FVector2D(256.0, 464.0), FVector2D(212.0, 312.0), FVector2D(0.94, -0.341), TArray<FVector2D>{FVector2D(194.0, 288.0), FVector2D(210.0, 290.0), FVector2D(221.0, 295.0), FVector2D(228.0, 302.0), FVector2D(236.0, 308.0), FVector2D(240.0, 316.0), FVector2D(237.0, 324.0), FVector2D(230.0, 330.0), FVector2D(220.0, 332.0), FVector2D(212.0, 335.0), FVector2D(201.0, 335.0), FVector2D(191.0, 330.0), FVector2D(185.0, 323.0), FVector2D(181.0, 313.0), FVector2D(184.0, 300.0)}},
            // Frame 1 SourceSha256: 9c1db7c10a2805a51c82d9a33ccab83627a084d5e5f536dd81df425642b0a7c2
            // SourcePath: F:/Ourgame/source-assets/production/fairytale-sword-v001/run-primary1-v003/curated/frame-1.png
            FMarker{FVector2D(256.0, 464.0), FVector2D(165.0, 189.0), FVector2D(-0.2, -0.98), TArray<FVector2D>{FVector2D(154.0, 167.0), FVector2D(165.0, 166.0), FVector2D(176.0, 169.0), FVector2D(182.0, 174.0), FVector2D(186.0, 181.0), FVector2D(187.0, 190.0), FVector2D(183.0, 199.0), FVector2D(179.0, 207.0), FVector2D(169.0, 211.0), FVector2D(158.0, 211.0), FVector2D(150.0, 208.0), FVector2D(145.0, 203.0), FVector2D(143.0, 195.0), FVector2D(143.0, 184.0), FVector2D(147.0, 175.0)}},
            // Frame 2 SourceSha256: d8a5cfcc350530a4973ab955ec7d5f36819213e17ba5de99d5498a59a6322425
            // SourcePath: F:/Ourgame/source-assets/production/fairytale-sword-v001/run-primary1-v003/curated/frame-2.png
            FMarker{FVector2D(256.0, 464.0), FVector2D(340.0, 286.0), FVector2D(0.95, 0.31), TArray<FVector2D>{FVector2D(331.0, 264.0), FVector2D(344.0, 265.0), FVector2D(354.0, 269.0), FVector2D(362.0, 276.0), FVector2D(365.0, 285.0), FVector2D(363.0, 295.0), FVector2D(357.0, 302.0), FVector2D(350.0, 306.0), FVector2D(342.0, 307.0), FVector2D(334.0, 309.0), FVector2D(325.0, 307.0), FVector2D(318.0, 303.0), FVector2D(314.0, 296.0), FVector2D(314.0, 284.0), FVector2D(318.0, 272.0)}},
            // Frame 3 SourceSha256: 1de81c7193ca228ca058afa63f26e3aac8fe369f3ed6b3ba8eea27e77157b227
            // SourcePath: F:/Ourgame/source-assets/production/fairytale-sword-v001/run-primary1-v003/curated/frame-3.png
            FMarker{FVector2D(256.0, 464.0), FVector2D(280.0, 352.0), FVector2D(0.95, 0.31), TArray<FVector2D>{FVector2D(261.0, 329.0), FVector2D(275.0, 329.0), FVector2D(288.0, 334.0), FVector2D(296.0, 341.0), FVector2D(301.0, 350.0), FVector2D(305.0, 359.0), FVector2D(302.0, 367.0), FVector2D(296.0, 372.0), FVector2D(288.0, 374.0), FVector2D(281.0, 375.0), FVector2D(272.0, 374.0), FVector2D(264.0, 372.0), FVector2D(257.0, 366.0), FVector2D(252.0, 358.0), FVector2D(251.0, 347.0), FVector2D(254.0, 337.0)}},
            // Frame 4 SourceSha256: 1e4256ba0e064c87e3aa075836f3005a68da5c4a044a77600ea63bc519d5d89b
            // SourcePath: F:/Ourgame/source-assets/production/fairytale-sword-v001/run-primary1-v003/curated/frame-4.png
            FMarker{FVector2D(256.0, 464.0), FVector2D(211.0, 312.0), FVector2D(0.94, -0.341), TArray<FVector2D>{FVector2D(193.0, 289.0), FVector2D(208.0, 290.0), FVector2D(220.0, 295.0), FVector2D(228.0, 302.0), FVector2D(236.0, 309.0), FVector2D(240.0, 317.0), FVector2D(236.0, 325.0), FVector2D(229.0, 331.0), FVector2D(219.0, 333.0), FVector2D(211.0, 335.0), FVector2D(200.0, 335.0), FVector2D(190.0, 330.0), FVector2D(184.0, 323.0), FVector2D(180.0, 312.0), FVector2D(184.0, 300.0)}},
            // Frame 5 SourceSha256: 050ca4103fc3ef6a1f3724b16bd0ebf42dc55353b799d5d92a6e4c2707e11bd0
            // SourcePath: F:/Ourgame/source-assets/production/fairytale-sword-v001/run-primary1-v003/curated/frame-5.png
            FMarker{FVector2D(256.0, 464.0), FVector2D(211.0, 312.0), FVector2D(0.94, -0.341), TArray<FVector2D>{FVector2D(193.0, 289.0), FVector2D(209.0, 290.0), FVector2D(221.0, 295.0), FVector2D(229.0, 302.0), FVector2D(237.0, 309.0), FVector2D(240.0, 317.0), FVector2D(237.0, 325.0), FVector2D(230.0, 331.0), FVector2D(220.0, 333.0), FVector2D(212.0, 335.0), FVector2D(200.0, 335.0), FVector2D(191.0, 330.0), FVector2D(185.0, 323.0), FVector2D(181.0, 312.0), FVector2D(184.0, 300.0)}},
        };
        return Index < UE_ARRAY_COUNT(Primary1Markers) ? &Primary1Markers[Index] : nullptr;
    }
    return nullptr;
}
} // namespace DungeonFairytaleSwordBodyV002
