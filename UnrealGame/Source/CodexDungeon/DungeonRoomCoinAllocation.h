#pragma once
#include <cstdint>
#include <string>
#include <vector>

// Pure preallocation only. These values do not prove formal room/source binding,
// manifest completeness, entity admission, death eligibility or wallet credit.
namespace DungeonRoomCoinAllocation
{
enum class EStatus
{
    Ok, NotImplemented, InvalidRoom, InvalidSource, InvalidBudget,
    InvalidSlot, DuplicateSlot, InvalidWeight, EmptyPositiveBudget,
    Overflow, ResourceFailure
};
struct FSlotWeight
{
    std::string SlotId;
    std::int64_t Weight=0;
};
struct FRequest
{
    std::uint64_t RoomInstanceId=0;
    std::string SourceId;
    std::int64_t Budget=0;
    // Caller supplies the complete finite eligible room manifest once.
    std::vector<FSlotWeight> Slots;
};
struct FSlotAllocation
{
    std::string SlotId;
    std::int64_t Weight=0, Coins=0;
};
struct FAllocation
{
    std::uint32_t Version=1;
    std::uint64_t RoomInstanceId=0;
    std::string SourceId;
    std::int64_t Budget=0;
    std::uint64_t TotalWeight=0;
    // Canonical ascending ASCII SlotId order; zero shares retained as facts.
    std::vector<FSlotAllocation> Slots;
};
// Syntactic identity domain: 1..128 ASCII [A-Za-z0-9_.:-], first alphanumeric.
// No trimming, case folding, source lookup or inferred/implicit budget.
// Budget >= 0, every weight > 0, RoomInstanceId != 0, exact SlotIds unique.
// Empty slots are accepted only for budget 0 (empty allocation, no payout).
// Checked uint64 sum/product: an unrepresentable intermediate is rejected.
// Validation/arithmetic rejection preserves Out; success replaces Out.
// ResourceFailure is returned for allocation/length exceptions only when
// _CPPUNWIND is enabled. In UE no-exception builds, resource exhaustion follows
// the platform/STL fatal-OOM policy; it cannot be reported as ResourceFailure.
// No no-exception resource-failure atomicity or recovery is promised.
EStatus TryAllocate(const FRequest& Request,FAllocation& Out);
}
