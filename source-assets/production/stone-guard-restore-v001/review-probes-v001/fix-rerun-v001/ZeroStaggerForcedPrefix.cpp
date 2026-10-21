#include "DungeonStoneGuard.h"
#include <iostream>
using namespace DungeonStoneGuard;
int main()
{
 FWorldInput W;W.HasTarget=true;W.Target={150,0,0};W.Sweep=[](const FSweepRequest&){return FSweepResult{};};
 FGuardKernel K(814);const bool Setup=K.StepTo(0,W).Accepted&&K.StepTo(1,W).Accepted&&K.TryStartAttack(EAttack::AxeSweep,W).Accepted
  &&K.StepTo(2,W).Accepted&&K.ApplyResolvedHit(1,1,0,W).Accepted&&K.TryHit({902,{100,0,0}}).Accepted&&K.ApplyResolvedHit(2,184,0,W).Accepted;
 FGuardKernel Receiver(814);const bool Accepted=Receiver.Restore(K.Capture());
 std::cout<<"SETUP="<<Setup<<" LEGAL_RESTORE="<<Accepted<<" ORIGIN="<<K.State().PoiseDecayOrigin<<" LAST="<<K.State().LastPoiseAt<<'\n';
 return Setup&&!Accepted?1:0;
}
