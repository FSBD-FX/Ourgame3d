#include "DungeonStoneGuard.h"
#include <iostream>
using namespace DungeonStoneGuard;
FWorldInput World(){FWorldInput W;W.HasTarget=true;W.Target={150,0,0};W.Sweep=[](const FSweepRequest&){return FSweepResult{};};return W;}
int main()
{
 FGuardKernel K(811);const auto W=World();
 const bool Setup=K.StepTo(0,W).Accepted&&K.StepTo(1,W).Accepted&&K.TryStartAttack(EAttack::AxeSweep,W).Accepted&&K.StepTo(2,W).Accepted
  &&K.ApplyResolvedHit(1,1,0,W).Accepted&&K.TryHit({901,{100,0,0}}).Accepted&&K.ApplyResolvedHit(2,1,85,W).Accepted;
 const auto Original=K.Capture();FGuardKernel Real(811);const bool RealAccepted=Real.Restore(Original);
 auto Forged=Original;Forged.ReceivedHits[0].Stagger=85;Forged.ReceivedHits[1].Stagger=0;
 FGuardKernel Rejected(811);const bool ForgedAccepted=Rejected.Restore(Forged);
 std::cout<<"SETUP="<<Setup<<" REAL_RESTORE="<<RealAccepted<<" FORGED_RESTORE="<<ForgedAccepted<<'\n';
 for(const auto& E:Forged.Issued)std::cout<<E.EventId<<" kind="<<int(E.Kind)<<" at="<<E.AtTime<<" amount="<<E.Amount<<'\n';
 // A real call with the forged first receipt breaks before the recorded Hit.
 FGuardKernel Witness(811);
 const bool WitnessSetup=Witness.StepTo(0,W).Accepted&&Witness.StepTo(1,W).Accepted&&Witness.TryStartAttack(EAttack::AxeSweep,W).Accepted&&Witness.StepTo(2,W).Accepted
  &&Witness.ApplyResolvedHit(1,1,85,W).Accepted;
 std::cout<<"WITNESS_SETUP="<<WitnessSetup<<" REAL_HIT_AFTER_BREAK="<<Witness.TryHit({901,{100,0,0}}).Accepted<<'\n';
 return Setup&&RealAccepted&&WitnessSetup&&ForgedAccepted?1:0;
}
