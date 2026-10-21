#include "DungeonStoneGuard.h"
#include <iostream>
using namespace DungeonStoneGuard;
int main()
{
 FWorldInput W;W.HasTarget=true;W.Target={900,0,0};
 FGuardKernel K(817);const bool Setup=K.StepTo(3,W,{{1,2,185,0},{2,2.5,1,0}}).Accepted&&K.ClaimDeathReward().Accepted;
 auto Forged=K.Capture();FGuardKernel Real(817);const bool RealAccepted=Real.Restore(Forged);
 Forged.Issued.back().AtTime=2.25;
 FGuardKernel Receiver(817);const bool Accepted=Receiver.Restore(Forged);
 std::cout<<"SETUP="<<Setup<<" REAL_RESTORE="<<RealAccepted<<" FORGED_RESTORE="<<Accepted<<" CLAIM_AT="<<Forged.Issued.back().AtTime<<" LAST_RECEIVED="<<Forged.ReceivedHits.back().AtTime<<'\n';
 return Setup&&RealAccepted&&Accepted?1:0;
}
