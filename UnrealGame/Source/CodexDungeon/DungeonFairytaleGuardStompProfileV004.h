#pragma once
#include "DungeonFairytaleGuardFullProfileV003.h"
namespace DungeonFairytaleGuardStompV004
{
inline const TArray<DungeonFairytaleGuardFullV003::FRow>& ProfileStompV004();
inline DungeonFairytaleGuardFullV003::FBodyPlan PlanStompV004(const DungeonFairytaleGuardFullV003::FSelection& Selection)
{return DungeonFairytaleGuardFullV003::PlanFullInProfile(Selection,ProfileStompV004());}
}
#include "DungeonFairytaleGuardStompDataV004.inl"
