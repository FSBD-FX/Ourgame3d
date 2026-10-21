#include "preload-shim.h"
#include "../fragments/helper.inc"
#include "actual-primary1-resolver.inc"
#include <iostream>
int Checks=0,Failures=0;
void Check(bool Yes,const char* Name){++Checks;if(!Yes){++Failures;std::cout<<"FAIL "<<Name<<'\n';}}
bool CollectActualOldRequired(std::set<std::wstring>& Out)
{
 int32 ExpectedReadbacks=0;const auto Capture=[&](const FString& Path,const FString&,const FString&,int32,int32){Out.insert(Path.S);return true;};
#include "actual-old-primary1-readback-loop.inc"
 return ExpectedReadbacks==42;
}
std::size_t Missing(const std::set<std::wstring>& Required){std::size_t N=0;for(const auto& P:Required){const auto I=HostAssets.find(P);if(I==HostAssets.end()||!I->second->Loaded)++N;}return N;}
void RegisterAssets(const std::set<std::wstring>& Required){HostAssets.clear();HostLoadCalls=HostFlushCalls=0;for(const auto& P:Required)HostAssets.emplace(P,std::make_unique<UTexture2D>(FString(P)));for(const auto& P:Bridge258SourcePins)HostAssets.emplace(P.ObjectPath,std::make_unique<UTexture2D>(FString(P.ObjectPath)));}
void RunCaptureSupplement(const FString& Action,const std::set<std::wstring>& Required,bool ExpectNew)
{
 const int Before=HostLoadCalls;(void)Action;
#include "legacy-preload-under-test.inc"
 if(ExpectNew){Check(HostLoadCalls-Before==14,"exact fourteen old resources explicitly loaded");Check(HostStrongRefs==14,"old fourteen retained strongly through current capture");Check(HostFlushCalls==1,"render flush precedes strict lookup");Check(Missing(Required)==0,"actual required old42 all resident after supplement");}
 else{Check(HostLoadCalls==Before&&HostFlushCalls==0&&HostStrongRefs==0,"off or Shift performs no supplemental load flush or refs");}
}
int main()
{
 std::set<std::wstring> Required;Check(CollectActualOldRequired(Required)&&Required.size()==42,"required set comes from actual old Primary1 capture loop");
 HostFlag=true;HostAction=L"J";RegisterAssets(Required);{ADungeonHUD HUD;HUD.RunActualPrimary1Preload();Check(HostLoadCalls==42,"actual HUD loop asks resolver for forty-two textures");Check(Missing(Required)==14,"new resolver replaces exactly old J0/J1 fourteen");RunCaptureSupplement(L"J",Required,true);Check(HostStrongRefs==0,"strong refs released only after capture scope exits");}
 HostFlag=false;HostAction=L"J";RegisterAssets(Required);{ADungeonHUD HUD;HUD.RunActualPrimary1Preload();Check(Missing(Required)==0,"flag off actual HUD still preloads every old layer");RunCaptureSupplement(L"J",Required,false);}
 HostFlag=true;HostAction=L"Shift";RegisterAssets(Required);{ADungeonHUD HUD;HUD.RunActualPrimary1Preload();RunCaptureSupplement(L"Shift",Required,false);}
 std::cout<<"CHECKS="<<Checks<<" FAILURES="<<Failures<<" ACTUAL_HUD_RESOLVER_AND_REQUIRED_SET_HOST_SHIM=true UE_RUN=false\n";return Failures?1:0;
}
