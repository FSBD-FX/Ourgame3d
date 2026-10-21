#include "DungeonStoneGuard.h"
#include <iostream>
using namespace DungeonStoneGuard;
void Drive(FGuardKernel& K,const FWorldInput& W){for(int N=0;N<400&&!K.State().Action.InProgress;++N){const double T=K.State().Time+double(.01f);if(!K.StepTo(T,W).Accepted)break;const auto A=K.ChooseAttack(W);if(A!=EAttack::None)K.TryStartAttack(A,W);}}
int main(){FWorldInput W;W.HasTarget=true;W.Target={-1180,0,0};W.Sweep=[](const FSweepRequest&){return FSweepResult{};};
 FGuardKernel Wrong(42,.01,{-150,0,0});FGuardKernel Relative(43,.01,{-1330,0,0});Wrong.BeginCombat();Relative.BeginCombat();Drive(Wrong,W);Drive(Relative,W);
 const bool A=Wrong.State().Phase==EPhase::Dormant&&Wrong.State().WakeStartedAt<0&&!Wrong.State().Action.InProgress;
 const bool B=Relative.State().Action.InProgress&&Relative.State().Action.Kind==EAttack::AxeSweep&&Relative.State().Awakened;
 std::cout<<"old_x="<<Wrong.State().Position.X<<" target_x="<<W.Target.X<<" old_time="<<Wrong.State().Time<<" old_phase="<<int(Wrong.State().Phase)<<" old_wake="<<Wrong.State().WakeStartedAt<<" wrong_relation_reproduced="<<A<<'\n';
 std::cout<<"relative_x="<<Relative.State().Position.X<<" relative_time="<<Relative.State().Time<<" relative_phase="<<int(Relative.State().Phase)<<" relative_wake="<<Relative.State().WakeStartedAt<<" axe_within_unchanged_budget="<<B<<" native_UE_not_executed=1\n";
 return A&&B?0:1;}
