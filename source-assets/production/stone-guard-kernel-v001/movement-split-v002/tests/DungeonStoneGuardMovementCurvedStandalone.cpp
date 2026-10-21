#include "DungeonStoneGuard.h"
#include <cmath>
#include <iostream>
using namespace DungeonStoneGuard;
int main()
{
 int Checks=0,Failed=0;auto Check=[&](bool V,const char* N){++Checks;if(!V)++Failed;std::cout<<(V?"PASS ":"FAIL ")<<N<<'\n';};
 for(int Sign:{-1,1})
 {
  auto World=[&](){FWorldInput W;W.HasTarget=true;W.Target={80.,Sign*100.,0};W.Sweep=[](const FSweepRequest&){return FSweepResult{};};return W;};
  auto W=World();FGuardKernel A(Sign<0?451:452),B(Sign<0?453:454);
  const bool Ready=A.StepTo(0,W).Accepted&&A.StepTo(1,W).Accepted&&B.StepTo(0,W).Accepted&&B.StepTo(1,W).Accepted;
  Check(Ready,"curved ellipse actual wake prerequisite");if(!Ready)continue;
  const auto RA=A.StepTo(2,W),RB=B.StepTo(2,W,{{1,1.2,0,0}});
  // 100-45*sqrt(3), independently rounded from an 80-digit decimal calculation.
  const double Expected=Sign*22.057713659400521790264914632235744;
  Check(RA.Accepted&&RB.Accepted&&std::abs(A.State().Position.Y-Expected)<1e-12&&std::abs(B.State().Position.Y-Expected)<1e-12,"analytic curved first entry survives receipt partition");
  Check(A.ChooseAttack(W)==EAttack::Stomp&&B.ChooseAttack(W)==EAttack::Stomp,"representable curved boundary is actually inside stomp shape");
 }
 std::cout<<"SUMMARY groups=1 cases=2 checks="<<Checks<<" failed="<<Failed<<'\n';return Failed?1:0;
}
