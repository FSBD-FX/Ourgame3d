#include "DungeonStoneGuard.h"
#include <cassert>
#include <iostream>
namespace G=DungeonStoneGuard;
int main(){G::FGuardKernel K(901);assert(K.BeginCombat());G::FWorldInput W;W.CanStartAttack=false;
const auto R=K.StepTo(.4,W,{{1,.125,185.,85.}});assert(R.Accepted);int Count=0;double Died=-1;
for(const auto& E:R.Events)if(E.Kind==G::EEventKind::Died){++Count;Died=E.AtTime;}
assert(Count==1&&Died==.125&&K.State().Time==.4&&K.State().ReceivedHits.size()==1&&K.State().ReceivedHits[0].AtTime==.125);
assert(K.ClaimDeathReward().Accepted);G::FGuardKernel Independent(901);assert(Independent.Restore(K.Capture()));
std::cout<<"Actual native Guard kernel accepted lethal receipt0.125; Died=0.125; final State.Time=0.4; full Restore valid. Not UE/OnFighterDied proof.\n";}
