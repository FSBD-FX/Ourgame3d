#pragma once
#include "DungeonFairytaleGuardPose.h"
#include <algorithm>
#include <cmath>
namespace DungeonFairytaleGuardFullV003
{
enum class EPivotAuthority {Unconfigured,VisibleShoeSupport,ArtistStandingRootPropagation,ArtistNearSupportDeltaPropagation};
enum class EClip {Dormant,Wake,Ready,Move,AxeWindup,AxeActive,AxeRecovery,StompWindup,StompActive,StompRecovery,Stunned,Death,InterruptedRecovery,Count,Invalid};
struct FSelection
{
 bool Valid=false,MaterialHit=false,TerminalPresentation=false,DeathAfterglow=false;
 EClip Clip=EClip::Invalid;int Frame=-1,Facing=1;
 std::uint64_t EntityId=0,AttackId=0,SourceEventId=0,MaterialEventId=0;
 DungeonStoneGuard::EPhase Phase=DungeonStoneGuard::EPhase::Dormant;
 double SampleTime=0.,IntervalStart=0.,IntervalEnd=0.,AcceptedDistance=0.,DistancePhase=0.,DeathAge=-1.;
};
inline const char* ClipName(EClip C)
{switch(C){case EClip::Dormant:return "Dormant";case EClip::Wake:return "Wake";case EClip::Ready:return "Ready";case EClip::Move:return "Move";
case EClip::AxeWindup:return "AxeWindup";case EClip::AxeActive:return "AxeActive";case EClip::AxeRecovery:return "AxeRecovery";
case EClip::StompWindup:return "StompWindup";case EClip::StompActive:return "StompActive";case EClip::StompRecovery:return "StompRecovery";
case EClip::Stunned:return "Stunned";case EClip::Death:return "Death";case EClip::InterruptedRecovery:return "InterruptedRecovery";default:return "Invalid";}}
inline int RequiredFrames(EClip C)
{switch(C){case EClip::Dormant:return 1;case EClip::Ready:case EClip::AxeActive:case EClip::AxeRecovery:case EClip::StompRecovery:case EClip::Stunned:case EClip::InterruptedRecovery:return 4;
case EClip::StompActive:return 2;case EClip::Wake:case EClip::Move:case EClip::AxeWindup:case EClip::StompWindup:case EClip::Death:return 6;default:return 0;}}
inline int LogicalFrameBudget(){int N=0;for(int I=0;I<int(EClip::Count);++I)N+=RequiredFrames(EClip(I));return N;}
inline FSelection SelectFull(const DungeonStoneGuard::FState&,double=-1.){return {};}
}
