#include "DungeonStoneGuard.h"
#include <iostream>
using namespace DungeonStoneGuard;
int main()
{
 FWorldInput W;W.HasTarget=true;W.Target={150,0,0};W.Sweep=[](const FSweepRequest&){return FSweepResult{};};
 FGuardKernel K(816);const bool Setup=K.StepTo(0,W).Accepted&&K.StepTo(1,W).Accepted&&K.TryStartAttack(EAttack::AxeSweep,W).Accepted
  &&K.StepTo(2,W,{{1,2,1,0},{2,2,1,0}}).Accepted&&K.TryHit({903,{100,0,0}}).Accepted&&K.ApplyResolvedHit(3,1,85,W).Accepted;
 auto Forged=K.Capture();FGuardKernel Real(816);const bool RealAccepted=Real.Restore(Forged);
 Forged.ReceivedHits[0].Stagger=40;Forged.ReceivedHits[1].Stagger=45;Forged.ReceivedHits[2].Stagger=0;
 FGuardKernel Receiver(816);const bool Accepted=Receiver.Restore(Forged);
 std::cout<<"SETUP="<<Setup<<" REAL_RESTORE="<<RealAccepted<<" FORGED_RESTORE="<<Accepted<<'\n';
 return Setup&&RealAccepted&&Accepted?1:0;
}
