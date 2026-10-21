#include "DungeonStoneGuard.h"
#include <cmath>
#include <iostream>
using namespace DungeonStoneGuard;
namespace
{
int Checks=0, Failures=0;
void Check(bool V,const char* N){++Checks;if(!V)++Failures;std::cout<<(V?"PASS ":"FAIL ")<<N<<'\n';}
FWorldInput World(){FWorldInput W;W.HasTarget=true;W.Target={150,0,0};W.Sweep=[](const FSweepRequest&){return FSweepResult{};};return W;}
bool Ready(FGuardKernel& K)
{
 auto W=World();auto R=K.StepTo(0,W);Check(R.Accepted,"regression actual proximity accepted");R=K.StepTo(1,W);Check(R.Accepted&&K.State().Awakened,"regression actual warning completed");R=K.TryStartAttack(EAttack::AxeSweep,W);Check(R.Accepted,"regression actual axe started");return R.Accepted;
}
int Count(const FResult& R,EEventKind Kind){int N=0;for(const auto& E:R.Events)N+=E.Kind==Kind;return N;}
}
int main()
{
 std::cout<<"GROUP DeathWithLaterReceipts\n";
 FGuardKernel D(80);if(Ready(D))
 {
  const auto R=D.StepTo(3,World(),{{1,2,185,0},{2,2.5,10,85}});
  Check(R.Accepted&&D.State().HP==0,"preaccepted later receipt batch completes after lethal hit");
  Check(Count(R,EEventKind::Died)==1&&Count(R,EEventKind::Damaged)==1,"only one death across separate later receipt times");
  Check(D.State().ReceivedHits.size()==2&&D.State().ReceivedHits.back().ActualHPLoss==0&&D.State().LastDamageReceiptId==2,"later receipt acknowledged once with zero actual damage");
  Check(Count(R,EEventKind::PoiseBroken)==0&&Count(R,EEventKind::ActiveWindow)==0,"death suppresses later break and active issue");
 }
 std::cout<<"GROUP RecoveryDeadlineInsideStun\n";
 FGuardKernel K(81);if(Ready(K))
 {
  const double End=K.State().Action.RecoveryEnd;
  const auto R=K.StepTo(4,World(),{{1,3.5,1,85}});
  Check(R.Accepted&&K.State().Phase==EPhase::Idle,"late recovery break eventually returns to idle");
  Check(Count(R,EEventKind::AttackCompleted)==1,"stun straddling recovery end does not drop completion");
  bool Exact=false;for(const auto& E:R.Events)if(E.Kind==EEventKind::AttackCompleted)Exact=E.AtTime==End;
  Check(Exact&&K.State().Action.CompletedAt==End,"completion keeps original authoritative deadline during stun");
  Check(K.State().StunUntil>End&&K.State().IdleReadyAt==End+.3,"stun and minimum idle remain separate obligations");
 }
 std::cout<<"GROUP WarningDeadlineInsideStun\n";
 FGuardKernel W(82);W.StepTo(0,World());const auto R=W.StepTo(1.4,World(),{{1,.9,1,85}});
 Check(R.Accepted&&W.State().Awakened&&W.State().HP==184&&W.State().Phase==EPhase::Idle,"late warning break keeps both clocks and damage");
 Check(Count(R,EEventKind::WakeCompleted)==1&&Count(R,EEventKind::PoiseBroken)==1,"overlapping warning and break issue each event once");
 std::cout<<"SUMMARY groups=3 checks="<<Checks<<" failed="<<Failures<<'\n';return Failures?1:0;
}
