// Prepared data only; not included in actual Source. JSON is the profile SSoT.
namespace FairytaleHurtPreparedV001 {
inline constexpr int FrameCount = 4;
inline constexpr double DurationSeconds = .4;
inline constexpr double FrameSeconds = .1;
inline constexpr double SourceCanvasSize = 512.;
inline constexpr double StandingSourceHeight = 416.;
inline constexpr double StandingDisplayHeight = 72.;
inline constexpr double BodyCanvasDisplay = 72. * 512. / 416.;
inline constexpr double SwordScale = .50;
inline constexpr double GroundRoot[4][2] = {
    {259.91826829878289, 463},
    {283.33893152136142, 464},
    {247.06828334586936, 464},
    {252.4471254026009, 464},
};
inline constexpr double Grip[4][2] = {
    {236, 303},
    {194, 289},
    {205, 289},
    {218, 303},
};
inline constexpr double ArtistAxisRaw[4][2] = {
    {0.69999999999999996, 0.71414284285428498},
    {0.80000000000000004, 0.59999999999999998},
    {0.95999999999999996, 0.28000000000000003},
    {0.93999999999999995, -0.34100000000000003},
};
inline constexpr double ArtistAxisUnit[4][2] = {
    {0.69999999999999996, 0.71414284285428498},
    {0.80000000000000004, 0.59999999999999998},
    {0.95999999999999996, 0.28000000000000003},
    {0.9400559349922476, -0.34102029131101746},
};
inline constexpr bool FarHandOptionalEmpty[4] = {false,true,true,true};
inline constexpr int ExpectedNonemptyDrawCountWithSword[4] = {9,8,8,8};
} // No engine hook, clock, assetload orstatepriority is authored here.
