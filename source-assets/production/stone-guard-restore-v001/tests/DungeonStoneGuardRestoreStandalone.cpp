#include "StoneGuardRestoreCases.h"
#include <iostream>
int main()
{
 int Checks=0,Failed=0;const auto Check=[&](bool V,const char* N){++Checks;if(!V)++Failed;std::cout<<(V?"PASS ":"FAIL ")<<N<<'\n';};
 std::cout<<"GROUP RealStagesAndFutureContinuation\n";StoneGuardRestoreCases::StageRoundTrips(Check);
 std::cout<<"GROUP ClosedWindowsSameCursorDeathAndIndependentObligations\n";StoneGuardRestoreCases::HistoriesAndObligations(Check);
 std::cout<<"GROUP CorruptionAtomicityPolicyAndDeepOwnership\n";StoneGuardRestoreCases::CorruptionAndAtomicity(Check);
 std::cout<<"SUMMARY groups=3 checks="<<Checks<<" failed="<<Failed<<'\n';return Failed?1:0;
}
