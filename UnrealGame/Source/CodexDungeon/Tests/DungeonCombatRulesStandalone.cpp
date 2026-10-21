#if defined(DUNGEON_COMBAT_RULES_STANDALONE)
#include "../DungeonCombatRules.h"
#include <cstdio>

int main()
{
    int Failures = 0;
    const auto Check = [&Failures](bool Condition, const char* Name)
    {
        std::printf("%s %s\n", Condition ? "PASS" : "FAIL", Name);
        Failures += Condition ? 0 : 1;
    };
    using namespace DungeonCombatRules;
    Check(CanHit(90, 0, 1, 120, 45, 0, 0), "forward same-depth sword hits");
    Check(CanHit(-90, 0, -1, 120, 45, 0, 0), "left-facing sword hits left");
    Check(!CanHit(-1, 0, 1, 120, 45, 0, 0), "attack cannot hit behind");
    Check(!CanHit(121, 0, 1, 120, 45, 0, 0), "attack cannot hit beyond range");
    Check(!CanHit(90, 46, 1, 120, 45, 0, 0), "visible overlap at different depth misses");
    Check(CanHit(120, -45, 1, 120, 45, 0, 0), "range and depth boundary remain hittable");
    Check(!CanHit(90, 0, 1, 120, 45, 0, 100), "high jump dodges ground attack");
    Check(CanHit(90, 0, 1, 120, 45, 100, 100), "equal airborne heights can hit");
    Check(RestoreHealth(97, 100, 30) == 100, "potion caps at maximum health");
    Check(RestoreHealth(40, 100, 30) == 70, "potion restores actual missing health");
    Check(RestoreHealth(40, 100, -10) == 40, "negative healing does not deal damage");
    std::printf("%d failures\n", Failures);
    return Failures ? 1 : 0;
}
#endif
