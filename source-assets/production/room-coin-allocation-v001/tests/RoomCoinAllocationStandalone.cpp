#include "DungeonRoomCoinAllocation.h"
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <limits>
#include <string>
#include <vector>
using namespace DungeonRoomCoinAllocation;
namespace
{
int Checks=0,Failures=0;
void Check(bool Value,const char* Name)
{
    ++Checks;
    if(!Value){++Failures;std::cout<<"FAIL "<<Name<<'\n';}
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
FAllocation Sentinel()
{
    FAllocation A;A.Version=93;A.RoomInstanceId=701;A.SourceId="UNCHANGED";
    A.Budget=83;A.TotalWeight=97;A.Slots={{"sentinel",41,83},{"second",56,0}};return A;
}
FRequest Six(std::int64_t Budget)
{
    return {73,"RWD-REG-01-N03-GOLD",Budget,
        {{"RSEQ-001-S06",2},{"RSEQ-001-S03",3},{"RSEQ-001-S05",4},
         {"RSEQ-001-S01",2},{"RSEQ-001-S04",2},{"RSEQ-001-S02",2}}};
}
void Expect(const FRequest& Request,const std::vector<FSlotAllocation>& Literal,
            std::uint64_t Total,const char* Name)
{
    FAllocation Out=Sentinel();const auto Before=Request;
    const auto Status=TryAllocate(Request,Out);
    Check(Status==EStatus::Ok,Name);
    if(Status!=EStatus::Ok)return;
    FAllocation Want;Want.RoomInstanceId=Request.RoomInstanceId;Want.SourceId=Request.SourceId;
    Want.Budget=Request.Budget;Want.TotalWeight=Total;Want.Slots=Literal;
    Check(Same(Out,Want),"exact hand-derived canonical allocation including identity");
    Check(Request.RoomInstanceId==Before.RoomInstanceId&&Request.SourceId==Before.SourceId&&
          Request.Budget==Before.Budget&&Request.Slots.size()==Before.Slots.size(),"input unchanged");
    for(std::size_t I=0;I<Request.Slots.size();++I)
        Check(Request.Slots[I].SlotId==Before.Slots[I].SlotId&&Request.Slots[I].Weight==Before.Slots[I].Weight,
              "input slot order and weights unchanged");
    std::int64_t Sum=0;for(const auto& S:Out.Slots)Sum+=S.Coins;
    Check(Sum==Request.Budget,"every coin retained including zero shares");
}
void Reject(const FRequest& R,EStatus Want,const char* Name)
{
    FAllocation Out=Sentinel();const auto Before=Out;
    Check(TryAllocate(R,Out)==Want,Name);
    Check(Same(Out,Before),"all Out fields unchanged on rejected input");
}
void ArithmeticExamples()
{
    // D08 paper example: floors [2,2,4,2,5,2], residual 3, tied 10/15
    // remainders award S01,S02,S04; S06 is later lexically and stays 2.
    Expect(Six(20),{{"RSEQ-001-S01",2,3},{"RSEQ-001-S02",2,3},{"RSEQ-001-S03",3,4},
        {"RSEQ-001-S04",2,3},{"RSEQ-001-S05",4,5},{"RSEQ-001-S06",2,2}},15,"documented20 example succeeds");
    // The same weights are arithmetic-only fixtures, not formal N02/N05 manifests.
    Expect(Six(8),{{"RSEQ-001-S01",2,1},{"RSEQ-001-S02",2,1},{"RSEQ-001-S03",3,2},
        {"RSEQ-001-S04",2,1},{"RSEQ-001-S05",4,2},{"RSEQ-001-S06",2,1}},15,"explicit8 budget no fixed5 payout");
    Expect(Six(24),{{"RSEQ-001-S01",2,3},{"RSEQ-001-S02",2,3},{"RSEQ-001-S03",3,5},
        {"RSEQ-001-S04",2,3},{"RSEQ-001-S05",4,7},{"RSEQ-001-S06",2,3}},15,"explicit24 budget not inferred from room");
    Expect({74,"RWD-Test",10,{{"C",3},{"A",1},{"B",2}}},
        {{"A",1,2},{"B",2,3},{"C",3,5}},6,"fraction rank beats input and share order");
    Expect({74,"RWD-Test",2,{{"S2",1},{"S10",1},{"S1",1}}},
        {{"S1",1,1},{"S10",1,1},{"S2",1,0}},3,"ASCII tie ordering rather than natural-number sorting");
    Expect({74,"RWD-Test",2,{{"small1",1},{"large",10},{"small2",1}}},
        {{"large",10,2},{"small1",1,0},{"small2",1,0}},12,"largest fractional remainder may belong to largest share");
    // These adjacent weights collapse to the same IEEE double; integer order must not.
    Expect({74,"RWD-Test",1,{{"A",9007199254740992LL},{"B",9007199254740993LL}}},
        {{"A",9007199254740992LL,0},{"B",9007199254740993LL,1}},18014398509481985ULL,
        "integer remainders distinguish weights above double precision");
    const auto Max=std::numeric_limits<std::int64_t>::max();
    Expect({74,"RWD-Test",Max,{{"C",1},{"B",1},{"A",1}}},
        {{"A",1,3074457345618258603LL},{"B",1,3074457345618258602LL},{"C",1,3074457345618258602LL}},3,
        "maximum signed budget exact division and residual");
    Expect({std::numeric_limits<std::uint64_t>::max(),"RWD-Test",Max,{{"A",2}}},
        {{"A",2,Max}},2,"positive max room identity and product at uint64 boundary accepted");
}
void CanonicalAndZero()
{
    FRequest R={7,"RWD-Canonical",7,{{"C",4},{"A",2},{"B",3}}};
    const std::vector<FSlotAllocation> Want={{"A",2,2},{"B",3,2},{"C",4,3}};
    Expect(R,Want,9,"canonical fixture succeeds");
    std::sort(R.Slots.begin(),R.Slots.end(),[](const auto& A,const auto& B){return A.SlotId<B.SlotId;});
    int Permutations=0;do{Expect(R,Want,9,"all input permutations produce same allocations");++Permutations;}
    while(std::next_permutation(R.Slots.begin(),R.Slots.end(),[](const auto& A,const auto& B){return A.SlotId<B.SlotId;}));
    Check(Permutations==6,"all six permutations covered");
    Expect({7,"RWD-Zero",0,{{"B",3},{"A",4}}},{{"A",4,0},{"B",3,0}},7,"zero budget preserves eligible slots with zero shares");
    Expect({7,"RWD-Zero",0,{}},{},0,"empty zero allocation succeeds without fabricated coin");
    Expect({7,"RWD-Case",1,{{"a",1},{"A",1}}},{{"A",1,1},{"a",1,0}},2,"identities case sensitive without normalization");
    auto Altered=Six(20);Altered.RoomInstanceId=888;Altered.SourceId="EXPLICIT-Source";
    Expect(Altered,{{"RSEQ-001-S01",2,3},{"RSEQ-001-S02",2,3},{"RSEQ-001-S03",3,4},
        {"RSEQ-001-S04",2,3},{"RSEQ-001-S05",4,5},{"RSEQ-001-S06",2,2}},15,
        "source and room do not trigger hidden budget lookup");
}
void InvalidAndOverflow()
{
    auto R=Six(20);R.RoomInstanceId=0;Reject(R,EStatus::InvalidRoom,"room0 rejected");
    R=Six(20);R.SourceId="";Reject(R,EStatus::InvalidSource,"empty source rejected");
    R.SourceId=" bad";Reject(R,EStatus::InvalidSource,"untrimmed source rejected");
    R.SourceId=std::string("RWD\0BAD",7);Reject(R,EStatus::InvalidSource,"embedded NUL source rejected");
    R.SourceId="RWD/Other";Reject(R,EStatus::InvalidSource,"non-token source rejected");
    R.SourceId=std::string(129,'A');Reject(R,EStatus::InvalidSource,"overlong source rejected");
    R.SourceId="_RWD";Reject(R,EStatus::InvalidSource,"nonalphanumeric initial source rejected");
    R.SourceId=std::string(1,static_cast<char>(0xff));Reject(R,EStatus::InvalidSource,"nonASCII source rejected");
    R=Six(-1);Reject(R,EStatus::InvalidBudget,"negative budget rejected");
    R=Six(20);R.Slots.clear();Reject(R,EStatus::EmptyPositiveBudget,"positive budget with no recipients rejected");
    R=Six(20);R.Slots[1].SlotId=R.Slots[0].SlotId;Reject(R,EStatus::DuplicateSlot,"duplicate exact identity rejected");
    R=Six(20);R.Slots[0].SlotId="";Reject(R,EStatus::InvalidSlot,"empty slot rejected");
    R.Slots[0].SlotId="A B";Reject(R,EStatus::InvalidSlot,"slot whitespace rejected");
    R.Slots[0].SlotId="S/1";Reject(R,EStatus::InvalidSlot,"slot separators cannot escape identity");
    R.Slots[0].SlotId=std::string("S\0BAD",5);Reject(R,EStatus::InvalidSlot,"embedded NUL slot rejected");
    R.Slots[0].SlotId=std::string(129,'B');Reject(R,EStatus::InvalidSlot,"overlong slot rejected");
    R=Six(20);R.Slots[0].Weight=0;Reject(R,EStatus::InvalidWeight,"zero denominator contribution rejected");
    R.Slots[0].Weight=-1;Reject(R,EStatus::InvalidWeight,"negative weight rejected");
    R=Six(0);R.Slots[0].Weight=0;Reject(R,EStatus::InvalidWeight,"zero budget does not bypass manifest validation");
    const auto Max=std::numeric_limits<std::int64_t>::max();
    R={7,"RWD-Overflow",1,{{"A",Max},{"B",Max},{"C",Max}}};
    Reject(R,EStatus::Overflow,"sum overflow rejected rather than wrap");
    R.Budget=0;Reject(R,EStatus::Overflow,"zero budget still rejects overflowing total");
    R={7,"RWD-Overflow",Max,{{"A",3}}};Reject(R,EStatus::Overflow,"intermediate multiply overflow rejected");
    R={7,"RWD-Overflow",Max,{{"A",1},{"B",3}}};Reject(R,EStatus::Overflow,"late product failure leaves no partial output");
    // Two maximum weights sum safely to 2^64-2, and budget1 needs no overflowing product.
    Expect({7,"RWD-LargeWeight",1,{{"B",Max},{"A",Max}}},{{"A",Max,1},{"B",Max,0}},18446744073709551614ULL,
        "large valid denominator and exact tied remainders accepted");
}
}
int main()
{
    ArithmeticExamples();CanonicalAndZero();InvalidAndOverflow();
    std::cout<<"GROUPS=3 CHECKS="<<Checks<<" FAILURES="<<Failures<<'\n';
    return Failures==0?0:1;
}
