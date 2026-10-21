#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonRoomCoinAllocation.h"
#include <algorithm>
#include <limits>
using namespace DungeonRoomCoinAllocation;
namespace RoomCoinAutomation
{
FAllocation Sentinel()
{
    FAllocation A;A.Version=93;A.RoomInstanceId=701;A.SourceId="UNCHANGED";
    A.Budget=83;A.TotalWeight=97;A.Slots={{"sentinel",41,83},{"second",56,0}};return A;
}
bool Same(const FAllocation& A,const FAllocation& B)
{
    if(A.Version!=B.Version||A.RoomInstanceId!=B.RoomInstanceId||A.SourceId!=B.SourceId||
       A.Budget!=B.Budget||A.TotalWeight!=B.TotalWeight||A.Slots.size()!=B.Slots.size())return false;
    for(std::size_t I=0;I<A.Slots.size();++I)
        if(A.Slots[I].SlotId!=B.Slots[I].SlotId||A.Slots[I].Weight!=B.Slots[I].Weight||
           A.Slots[I].Coins!=B.Slots[I].Coins)return false;
    return true;
}
bool Literal(FAutomationTestBase& Test,const FRequest& Request,
             const std::vector<FSlotAllocation>& Slots,std::uint64_t Total)
{
    auto Out=Sentinel();
    if(!Test.TestTrue(TEXT("Explicit full manifest preallocates successfully"),TryAllocate(Request,Out)==EStatus::Ok))return false;
    FAllocation Want;Want.RoomInstanceId=Request.RoomInstanceId;Want.SourceId=Request.SourceId;
    Want.Budget=Request.Budget;Want.TotalWeight=Total;Want.Slots=Slots;
    return Test.TestTrue(TEXT("Exact hand-calculated allocation and canonical identity"),Same(Out,Want));
}
void Reject(FAutomationTestBase& Test,const FRequest& Request,EStatus Status)
{
    auto Out=Sentinel();const auto Before=Out;
    Test.TestTrue(TEXT("Malformed or overflowing request rejected explicitly"),TryAllocate(Request,Out)==Status);
    Test.TestTrue(TEXT("Rejected request preserves every Out field"),Same(Out,Before));
}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonRoomCoinLiteral,
 "CodexDungeon.Content.RoomCoinAllocation.LiteralLargestRemainderAndCanonicalOrder",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonRoomCoinLiteral::RunTest(const FString& Parameters)
{
    (void)Parameters;using namespace RoomCoinAutomation;
    const FRequest Six={73,"RWD-REG-01-N03-GOLD",20,
        {{"RSEQ-001-S06",2},{"RSEQ-001-S03",3},{"RSEQ-001-S05",4},
         {"RSEQ-001-S01",2},{"RSEQ-001-S04",2},{"RSEQ-001-S02",2}}};
    if(!Literal(*this,Six,{{"RSEQ-001-S01",2,3},{"RSEQ-001-S02",2,3},{"RSEQ-001-S03",3,4},
         {"RSEQ-001-S04",2,3},{"RSEQ-001-S05",4,5},{"RSEQ-001-S06",2,2}},15))return false;
    FRequest Request={7,"RWD-Canonical",7,{{"A",2},{"B",3},{"C",4}}};
    do{Literal(*this,Request,{{"A",2,2},{"B",3,2},{"C",4,3}},9);}
    while(std::next_permutation(Request.Slots.begin(),Request.Slots.end(),
        [](const auto& A,const auto& B){return A.SlotId<B.SlotId;}));
    Literal(*this,{74,"RWD-Test",2,{{"S2",1},{"S10",1},{"S1",1}}},
        {{"S1",1,1},{"S10",1,1},{"S2",1,0}},3);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonRoomCoinInteger,
 "CodexDungeon.Content.RoomCoinAllocation.ExactIntegerAndZeroBoundaries",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonRoomCoinInteger::RunTest(const FString& Parameters)
{
    (void)Parameters;using namespace RoomCoinAutomation;
    if(!Literal(*this,{74,"RWD-Test",1,{{"A",9007199254740992LL},{"B",9007199254740993LL}}},
        {{"A",9007199254740992LL,0},{"B",9007199254740993LL,1}},18014398509481985ULL))return false;
    const auto Maximum=std::numeric_limits<std::int64_t>::max();
    Literal(*this,{74,"RWD-Test",Maximum,{{"C",1},{"B",1},{"A",1}}},
        {{"A",1,3074457345618258603LL},{"B",1,3074457345618258602LL},{"C",1,3074457345618258602LL}},3);
    Literal(*this,{7,"RWD-Zero",0,{{"B",3},{"A",4}}},{{"A",4,0},{"B",3,0}},7);
    Literal(*this,{7,"RWD-Zero",0,{}},{},0);
    Literal(*this,{7,"RWD-LargeWeight",1,{{"B",Maximum},{"A",Maximum}}},
        {{"A",Maximum,1},{"B",Maximum,0}},18446744073709551614ULL);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonRoomCoinInvalid,
 "CodexDungeon.Content.RoomCoinAllocation.RejectionIsAtomic",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonRoomCoinInvalid::RunTest(const FString& Parameters)
{
    (void)Parameters;using namespace RoomCoinAutomation;
    if(!Literal(*this,{7,"RWD-Valid",2,{{"A",1}}},{{"A",1,2}},1))return false;
    Reject(*this,{0,"RWD-Test",1,{{"A",1}}},EStatus::InvalidRoom);
    Reject(*this,{7,"",1,{{"A",1}}},EStatus::InvalidSource);
    Reject(*this,{7,std::string("RWD\0BAD",7),1,{{"A",1}}},EStatus::InvalidSource);
    Reject(*this,{7,"RWD-Test",-1,{{"A",1}}},EStatus::InvalidBudget);
    Reject(*this,{7,"RWD-Test",1,{}},EStatus::EmptyPositiveBudget);
    Reject(*this,{7,"RWD-Test",1,{{"A",1},{"A",2}}},EStatus::DuplicateSlot);
    Reject(*this,{7,"RWD-Test",1,{{"A B",1}}},EStatus::InvalidSlot);
    Reject(*this,{7,"RWD-Test",1,{{"A",0}}},EStatus::InvalidWeight);
    Reject(*this,{7,"RWD-Test",1,{{"A",-1}}},EStatus::InvalidWeight);
    const auto Maximum=std::numeric_limits<std::int64_t>::max();
    Reject(*this,{7,"RWD-Overflow",1,{{"A",Maximum},{"B",Maximum},{"C",Maximum}}},EStatus::Overflow);
    Reject(*this,{7,"RWD-Overflow",Maximum,{{"A",1},{"B",3}}},EStatus::Overflow);
    return true;
}
#endif
