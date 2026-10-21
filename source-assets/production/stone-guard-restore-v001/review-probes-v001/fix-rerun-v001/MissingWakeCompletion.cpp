#include "DungeonStoneGuard.h"
#include <algorithm>
#include <iostream>
using namespace DungeonStoneGuard;
int main()
{
 FWorldInput W;W.HasTarget=true;W.Target={150,0,0};W.Sweep=[](const FSweepRequest&){return FSweepResult{};};
 FGuardKernel K(812);const bool Setup=K.StepTo(0,W).Accepted&&K.StepTo(2,W,{{1,2,185,0}}).Accepted;
 auto Forged=K.Capture();FGuardKernel Real(812);const bool RealAccepted=Real.Restore(Forged);
 Forged.Issued.erase(std::remove_if(Forged.Issued.begin(),Forged.Issued.end(),[](const FEvent& E){return E.Kind==EEventKind::WakeCompleted;}),Forged.Issued.end());
 for(std::size_t I=0;I<Forged.Issued.size();++I)Forged.Issued[I].EventId=I+1;
 Forged.NextEventId=Forged.Issued.size()+1;Forged.Awakened=false;
 FGuardKernel Receiver(812);const bool ForgedAccepted=Receiver.Restore(Forged);
 std::cout<<"SETUP="<<Setup<<" REAL_RESTORE="<<RealAccepted<<" FORGED_RESTORE="<<ForgedAccepted<<" DEATH_AT="<<Forged.Time<<" WAKE_END="<<Forged.WakeEnd<<'\n';
 return Setup&&RealAccepted&&ForgedAccepted?1:0;
}
