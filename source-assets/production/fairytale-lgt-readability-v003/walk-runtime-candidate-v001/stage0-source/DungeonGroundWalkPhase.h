#pragma once
#include <array>
#include <cmath>

namespace DungeonGroundWalk
{
// Explicit frozen art input, never an invented physical stride. A test may pass
// a clearly labelled synthetic policy without configuring runtime art.
struct FPolicy
{
    double CycleDistance=0.,CycleSeconds=0.;
    std::array<double,6> Durations{};
};
inline bool Valid(const FPolicy&) {return false;}
inline bool Advance(double,double,const FPolicy&,double&) {return false;}
inline bool Frame(double,const FPolicy&,int&) {return false;}
}
