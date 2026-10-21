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
 bool Observe(const FRequestScopeKey&,std::uint64_t,std::uint64_t& Gap){Gap=0;return false;}
};
}
