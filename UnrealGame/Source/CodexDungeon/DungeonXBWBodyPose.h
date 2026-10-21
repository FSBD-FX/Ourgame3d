#pragma once
#include "DungeonWeaponActions.h"
#include <cmath>

// Presentation samples the accepted Actor clock; it never emits combat events.
namespace DungeonXBWBodyPose
{
struct FPose
{
    int Frame = -1;
    double GripX = 0., GripY = 0., Angle = 0., Scale = .48;
};
struct FReloadPose
{
    int Frame = -1;
    double Angle = 0., Scale = .48;
    double BodySupportX = 0., BodySupportY = 0.;
    double ComponentSupportX = 0., ComponentSupportY = 0.;
};
inline bool Reload(const DungeonWeaponActions::FState& S, FReloadPose& Out)
{
    Out = {};
    const auto& A=S.Action;
    if(!A.Active || A.Type!=DungeonWeaponActions::EAction::Reload
        || A.Weapon!=DungeonContentCombat::EWeapon::XBW001 || A.StartedAirborne
        || !std::isfinite(S.Time) || !std::isfinite(A.Start) || !std::isfinite(A.End)
        || !(A.Start<A.End) || S.Time<A.Start || S.Time>=A.End) return false;
    const double T=(S.Time-A.Start)/(A.End-A.Start);
    const int I=T<.2/1.1?0:T<.6/1.1?1:T<.85/1.1?2:3;
    constexpr double Angles[]={-9.048593278634216,-5.633198636185468,-19.52939909323423,1.967075854989118};
    constexpr double SupportY[]={321.,323.,325.,325.};
    // Early near hands manipulate the string/bolt, not an invented stock grip.
    Out={I,Angles[I],.48,321.,SupportY[I],344.,I<2?320.:286.};return true;
}
inline bool Primary(const DungeonWeaponActions::FState& S, FPose& Out)
{
    Out = {};
    const auto& A=S.Action;
    if(!A.Active || A.Type!=DungeonWeaponActions::EAction::Primary
        || A.Weapon!=DungeonContentCombat::EWeapon::XBW001 || A.StartedAirborne
        || !std::isfinite(S.Time) || !std::isfinite(A.Start) || !std::isfinite(A.ActiveAt)
        || !std::isfinite(A.ActiveEnd) || !std::isfinite(A.End)
        || !(A.Start<A.ActiveAt && A.ActiveAt<A.ActiveEnd && A.ActiveEnd<A.End)
        || S.Time<A.Start || S.Time>=A.End) return false;
    const int Base=S.Time<A.ActiveAt?0:S.Time<A.ActiveEnd?2:4;
    const double Start=Base==0?A.Start:Base==2?A.ActiveAt:A.ActiveEnd;
    const double End=Base==0?A.ActiveAt:Base==2?A.ActiveEnd:A.End;
    const int I=Base+(S.Time<(Start+End)*.5?0:1);
    // Frozen import-XBW-primary-v001: all body and rigid prop tracks share I.
    constexpr double GripX[]={224.,250.,255.,250.,240.,224.};
    constexpr double GripY[]={316.,260.,267.,267.,300.,316.};
    constexpr double Angle[]={-5.065580597958718,-6.776388900189802,-9.601046219591353,
        -11.266152277695031,-6.765269983288224,-5.065580597958718};
    Out={I,GripX[I],GripY[I],Angle[I],.48};return true;
}
}
