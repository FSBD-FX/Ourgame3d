#include "DungeonStoneGuard.h"
#include <iostream>
using namespace DungeonStoneGuard;
int main()
{
 FWorldInput W;W.HasTarget=true;W.Target={900,0,0};
 FGuardKernel K(815);const bool Setup=K.ApplyResolvedHit(1,1,40,W).Accepted&&K.ApplyResolvedHit(2,184,0,W).Accepted;
 auto Forged=K.Capture();FGuardKernel Real(815);const bool RealAccepted=Real.Restore(Forged);
 Forged.PoiseAccum=0;Forged.PoiseDecayOrigin=0;Forged.LastPoiseAt=-1;
 FGuardKernel Receiver(815);const bool Accepted=Receiver.Restore(Forged);
 std::cout<<"SETUP="<<Setup<<" REAL_RESTORE="<<RealAccepted<<" FORGED_RESTORE="<<Accepted<<" WAKE_START="<<Forged.WakeStartedAt<<'\n';
 return Setup&&RealAccepted&&Accepted?1:0;
}
