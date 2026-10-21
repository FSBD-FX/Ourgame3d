#include "DungeonStoneGuard.h"
#include <iostream>
using namespace DungeonStoneGuard;
int main(){int Checks=0,Failures=0;auto C=[&](bool V,const char* N){++Checks;if(!V){++Failures;std::cout<<"FAIL "<<N<<'\n';}};
 FWorldInput W;W.HasTarget=true;W.Target={0,0,0};W.Sweep=[](const FSweepRequest&){return FSweepResult{};};
 FGuardKernel K(42,.01,{-150,0,0});C(K.BeginCombat(),"real combat origin");C(K.StepTo(.01,W).Accepted,"wake started");C(K.StepTo(K.State().WakeEnd,W).Accepted,"wake completed");
 C(K.TryStartAttack(EAttack::AxeSweep,W).Accepted,"axe start");C(K.StepTo(K.State().Action.ActiveAt,W).Accepted,"active immutable window");C(K.TryHit({7,{0,0,0}}).Accepted,"real once-hit receipt");
 C(K.ApplyResolvedHit(1,1,85,W).Accepted,"resolved receipt and break");const auto S=K.Capture();
 C(S.Windows.size()==1&&S.Closures.size()==1&&S.HitReceipts.size()==1&&S.ReceivedHits.size()==1&&!S.Issued.empty(),"five real histories nonempty");
 FGuardKernel R(S.EntityId,S.InitialTime,S.InitialPosition,S.Facing,{123});C(R.Restore(S),"same birth custompolicy validated restore");C(R.CapturePolicy().ExtremelyCloseRadius==123,"explicit receiverpolicy retained");
 C(R.State().NextEventId==S.NextEventId&&R.State().LastDamageReceiptId==S.LastDamageReceiptId&&R.State().HP==184,"no emitted event healedHP or cursor loss");
 auto Bad=S;++Bad.InitialTime;C(!R.Restore(Bad)&&R.State().InitialTime==S.InitialTime,"wrong immutablebirth rejection");
 std::cout<<"checks="<<Checks<<" failures="<<Failures<<" native_owner_not_executed=1\n";return Failures?1:0;}
