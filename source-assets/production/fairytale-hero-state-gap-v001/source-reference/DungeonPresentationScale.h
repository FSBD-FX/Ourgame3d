#pragma once

// EV-043: reduce actor presentation by 25%; ground coordinates and combat rules stay unchanged.
namespace DungeonPresentationScale
{
    constexpr double RelativeScale = .75;
    constexpr double CandidateBodySize = 120.;
    constexpr double FallbackPlayerBodySize = 150. * RelativeScale;
    constexpr double FallbackEnemyBodySize = 142. * RelativeScale;
}
