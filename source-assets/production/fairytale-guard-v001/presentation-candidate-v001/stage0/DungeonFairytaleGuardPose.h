#pragma once
#include "DungeonStoneGuard.h"
namespace DungeonFairytaleGuard
{
enum class EClip { Dormant, Wake, Ready, Move, AxeWindup, AxeFollow, StompWindup, StompFollow, Stunned, Death, InterruptedRecovery, Count, Invalid };
struct FSelection
{
 bool Valid=false,MaterialHit=false,TerminalPresentation=false;
 EClip Clip=EClip::Invalid;
 int Frame=-1,Facing=1;
 std::uint64_t EntityId=0,AttackId=0,SourceEventId=0,MaterialEventId=0;
 DungeonStoneGuard::EPhase Phase=DungeonStoneGuard::EPhase::Dormant;
 double SampleTime=0,IntervalStart=0,IntervalEnd=0,AcceptedDistance=0,DistancePhase=0;
};
inline FSelection Select(const DungeonStoneGuard::FState&,double=-1.) {return {};}
}
