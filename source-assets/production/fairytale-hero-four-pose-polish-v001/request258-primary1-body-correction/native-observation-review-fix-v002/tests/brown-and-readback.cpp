#include "ue-small-shim.h"
#include "../fragments/helper.inc"
#include "brown-under-test.inc"
#include <iostream>
int Checks=0,Failures=0;
void Check(bool Yes,const char* Name){++Checks;if(!Yes){++Failures;std::cout<<"FAIL "<<Name<<'\n';}}
FString Sword(TEXT("/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002"));
FDungeonFairytaleSwordDraw NewDraw(int Frame,int Facing=1)
{
 FDungeonFairytaleSwordDraw D;D.Frame=Frame;D.Facing=Facing;D.Clip=TEXT("sword_primary_1");D.WeaponPath=Sword;D.Root={256,464};D.Grip=Frame?FVector2D(159,213):FVector2D(211,343);D.WeaponScale=.5;D.WeaponAngle=FMath::RadiansToDegrees(FMath::Atan2(Frame?-.98:-.341,Frame?-.2:.94))*(Facing<0?-1.:1.);
 const wchar_t* Parts[]={L"BodyRest",L"ShoulderFar",L"Chest",L"NearArmWithoutHand",L"ShoulderNear",L"HelmetForeground",L"NearHand"};
 for(int I=0;I<7;++I){if(I==6)D.DrawStack.push_back(Sword);const FString Name=FString::Printf(L"T_Fairytale_Bridge258_%s_%03d_v001",Parts[I],Frame);D.DrawStack.push_back(FString(L"/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/")+Name+L"."+Name);}return D;
}
FDungeonFairytaleSwordDraw OldDraw(int Frame,bool Primary)
{
 auto D=NewDraw(Frame);D.Clip=Primary?L"sword_primary_1":L"sword_ready_idle";D.DrawStack=TArray<FString>(Primary?8:7,FString(L"old_other_slot"));D.DrawStack[Primary?6:5]=Sword;
 const wchar_t* Parts[]={L"ShoulderFar",L"Chest",L"ShoulderNear"};const int Slots[]={1,2,4};for(int I=0;I<3;++I){const FString Name=FString::Printf(Primary?L"T_Fairytale_LeatherPrimary1%s_%03d_v001":L"T_Fairytale_LeatherReady%s_%03d_v001",Parts[I],Frame);D.DrawStack[Slots[I]]=FString(Primary?L"/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/":L"/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/")+Name+L"."+Name;}return D;
}
bool Readback(int Base,const FString& Action,int& Count,std::vector<std::wstring>& Paths,bool Reject=false)
{
 int32 ExpectedReadbacks=Base;const auto Capture=[&](const FString& Path,const FString&,const FString&,int32,int32){if(Reject)return false;Paths.push_back(Path.S);return true;};(void)Capture;(void)Action;
#include "readback-under-test.inc"
 Count=ExpectedReadbacks;return true;
}
int main()
{
 HostFlag=true;HostAction=L"J";
 for(int F=0;F<2;++F)for(int Side:{-1,1})Check(Brown(NewDraw(F,Side),true),"new J0/J1 exact draw both facings");
 for(int Slot=0;Slot<8;++Slot){auto D=NewDraw(0);D.DrawStack[Slot]=L"wrong_resource";Check(!Brown(D,true),"every actual stack slot must match");}
 {auto D=NewDraw(0);D.Root.X+=1;Check(!Brown(D,true),"wrong root rejected");D=NewDraw(0);D.Grip.Y+=1;Check(!Brown(D,true),"wrong grip rejected");D=NewDraw(1);D.WeaponPath=L"wrong_sword";Check(!Brown(D,true),"wrong sword rejected");D=NewDraw(0);D.WeaponScale=.6;Check(!Brown(D,true),"wrong sword scale rejected");D=NewDraw(0);D.WeaponAngle+=1;Check(!Brown(D,true),"wrong directed sword angle rejected");}
 HostFlag=false;Check(Brown(OldDraw(0,true),true),"no flag old J0 preserved");Check(!Brown(NewDraw(0),true),"new stack cannot pass without optin");HostFlag=true;HostAction=L"Shift";Check(!Brown(NewDraw(0),true),"new branch requires J action");HostAction=L"J";
 for(int F=2;F<6;++F)Check(Brown(OldDraw(F,true),true),"J2to5 original branch preserved");for(int F=0;F<4;++F)Check(Brown(OldDraw(F,false),false),"Ready original branch preserved");
 int Count=0;std::vector<std::wstring> Paths;Check(Readback(115,L"J",Count,Paths)&&Count==129&&Paths.size()==14,"new J keeps old115 plus14 actual captures");std::sort(Paths.begin(),Paths.end());Check(std::unique(Paths.begin(),Paths.end())==Paths.end(),"fourteen readback paths unique");Paths.clear();Check(!Readback(115,L"J",Count,Paths,true),"new readback failure remains failure");
 HostFlag=false;Paths.clear();Check(Readback(115,L"J",Count,Paths)&&Count==115&&Paths.empty(),"old J count remains115 without flag");Check(Readback(105,L"Shift",Count,Paths)&&Count==105&&Paths.empty(),"old Shift count remains105");HostFlag=true;HostAction=L"Shift";Check(Readback(105,L"Shift",Count,Paths)&&Count==105&&Paths.empty(),"flag Shift does not enable J-only resources");
 std::cout<<"CHECKS="<<Checks<<" FAILURES="<<Failures<<" HOST_SHIM_ONLY=true UE_RUN=false\n";return Failures?1:0;
}
