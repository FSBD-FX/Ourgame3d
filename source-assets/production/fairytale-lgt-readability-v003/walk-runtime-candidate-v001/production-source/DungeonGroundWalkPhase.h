#pragma once
#include <array>
#include <cmath>

namespace DungeonGroundWalk
{
// One immutable compiled profile supplies physical stride and six intervals.
// Numeric test fixtures do not configure or approve runtime artwork.
struct FPolicy
{
    double CycleDistance=0.,CycleSeconds=0.;
    std::array<double,6> Durations{};
};
inline bool Valid(const FPolicy& P)
{
    if(!std::isfinite(P.CycleDistance)||P.CycleDistance<=0.
        ||!std::isfinite(P.CycleSeconds)||P.CycleSeconds<=0.)return false;
    double Sum=0.;
    for(double D:P.Durations)
    {
        if(!std::isfinite(D)||D<=0.)return false;
        Sum+=D;if(!std::isfinite(Sum))return false;
    }
    return std::abs(Sum-P.CycleSeconds)<=1.e-12*P.CycleSeconds;
}
inline bool Advance(double Clock,double Distance,const FPolicy& P,double& Out)
{
    if(!Valid(P)||!std::isfinite(Clock)||Clock<0.||!std::isfinite(Distance)||Distance<0.)return false;
    if(Distance==0.){Out=Clock;return true;}
    // Reduce before division/addition: huge finite distances and clocks cannot
    // overflow a quotient or an integer frame cursor. Zero is exact above.
    const double Phase=std::fmod(Clock,P.CycleSeconds)/P.CycleSeconds;
    const double Step=std::fmod(Distance,P.CycleDistance)/P.CycleDistance;
    const double Candidate=std::fmod(Phase+Step,1.)*P.CycleSeconds;
    if(!std::isfinite(Candidate)||Candidate<0.)return false;
    Out=Candidate;return true;
}
inline bool Frame(double Clock,const FPolicy& P,int& Out)
{
    if(!Valid(P)||!std::isfinite(Clock)||Clock<0.)return false;
    const double Phase=std::fmod(Clock,P.CycleSeconds);
    double End=0.;
    for(int I=0;I<6;++I){End+=P.Durations[I];if(Phase<End||I==5){Out=I;return true;}}
    return false;
}
}
