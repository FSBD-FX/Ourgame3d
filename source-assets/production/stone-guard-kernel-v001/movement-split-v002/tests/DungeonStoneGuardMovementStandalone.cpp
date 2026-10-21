#include "StoneGuardMovementCases.h"
#include <iostream>
int main()
{
 int Checks=0,Failed=0;
 const bool Pass=StoneGuardMovementCases::Run([&](bool V,const char* Name){++Checks;if(!V)++Failed;std::cout<<(V?"PASS ":"FAIL ")<<Name<<'\n';});
 std::cout<<"SUMMARY groups=1 cases=6 checks="<<Checks<<" failed="<<Failed<<'\n';return Pass?0:1;
}
