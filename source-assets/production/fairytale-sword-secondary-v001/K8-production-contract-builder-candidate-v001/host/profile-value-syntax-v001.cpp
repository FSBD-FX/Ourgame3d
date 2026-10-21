#include "DungeonFairytaleSwordSecondaryPlanV001.h"
#include <iostream>
namespace DungeonFairytaleSwordSecondaryV001 {
#include "../output/source-contract-package-v001/profile-whole-value-v001.inl"
}
int main(){using namespace DungeonFairytaleSwordSecondaryV001;const auto& P=Profile();
 if(P.RuntimeReady||ProfileValid(P)||!ValidSha(P.SourceContractSha256))return 1;
 int N=0;for(const auto& F:P.Frames){if(F.Root.X!=256.||F.Root.Y!=464.)return 2;for(const auto& L:F.Layers){if(!ValidTexturePath(L.TexturePath)||!ValidSource(L.Source))return 3;++N;}}
 if(!ValidTexturePath(P.Sword.TexturePath)||!ValidSource(P.Sword.Source)||N!=56)return 4;
 std::cout<<"actual_runtime_FProfile_type_complete_layer_records="<<N<<" reused_sword=1 RuntimeReady=false UE_imported=false\n";return 0;}
