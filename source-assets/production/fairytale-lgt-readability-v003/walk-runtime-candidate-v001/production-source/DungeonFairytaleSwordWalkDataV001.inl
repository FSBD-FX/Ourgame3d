#pragma once
// REQUIRED ART INPUT IS PENDING. No root, grip, axis, path or physical stride is
// inferred from the old display pivot or an animation preview's frame duration.
// Root replaces this ONE immutable compiled table from a frozen assembly plus
// measured markers/stride. There is no per-process or command-line policy override.
namespace DungeonFairytaleSwordWalkV001
{
inline const FProfile& Profile()
{
    static const FProfile Pending{};
    return Pending;
}
}
