#include <array>
#include <cstdint>
#include <vector>
namespace DungeonHeroLocomotionObservationV001
{
struct FRequestScopeKey { std::array<std::uint64_t,8> Fields{}; };
class FRequestCursor
{
 struct FThrough {FRequestScopeKey Scope;std::uint64_t Sequence=0;};
 std::vector<FThrough> Through;
public:
 bool Observe(const FRequestScopeKey& Scope,std::uint64_t Sequence,std::uint64_t& Gap)
 {
  Gap=0;if(!Sequence)return false;
  for(auto& T:Through)if(T.Scope.Fields==Scope.Fields)
  {
   if(Sequence<=T.Sequence)return false;
   Gap=Sequence-T.Sequence-1;T.Sequence=Sequence;return true;
  }
  Through.push_back({Scope,Sequence});Gap=Sequence-1;return true;
 }
};
}
