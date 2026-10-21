#include "DungeonRoomCoinAllocation.h"
#include <algorithm>
#include <limits>
#include <new>
#include <stdexcept>
#include <utility>

namespace DungeonRoomCoinAllocation
{
namespace
{
bool AlphaNumeric(unsigned char C)
{
    return (C>='A'&&C<='Z')||(C>='a'&&C<='z')||(C>='0'&&C<='9');
}
bool Identity(const std::string& Id)
{
    if(Id.empty()||Id.size()>128||!AlphaNumeric(static_cast<unsigned char>(Id.front())))return false;
    for(const unsigned char C:Id)
        if(!AlphaNumeric(C)&&C!='_'&&C!='.'&&C!=':'&&C!='-')return false;
    return true;
}
struct FShare
{
    std::size_t Index=0;
    std::uint64_t Remainder=0;
};
EStatus Build(const FRequest& Request,FAllocation& Candidate)
{
    if(Request.RoomInstanceId==0)return EStatus::InvalidRoom;
    if(!Identity(Request.SourceId))return EStatus::InvalidSource;
    if(Request.Budget<0)return EStatus::InvalidBudget;
    if(Request.Slots.empty()&&Request.Budget!=0)return EStatus::EmptyPositiveBudget;

    Candidate.RoomInstanceId=Request.RoomInstanceId;
    Candidate.SourceId=Request.SourceId;
    Candidate.Budget=Request.Budget;
    Candidate.Slots.reserve(Request.Slots.size());
    const auto Maximum=std::numeric_limits<std::uint64_t>::max();
    for(const auto& Slot:Request.Slots)
    {
        if(!Identity(Slot.SlotId))return EStatus::InvalidSlot;
        if(Slot.Weight<=0)return EStatus::InvalidWeight;
        const auto Weight=static_cast<std::uint64_t>(Slot.Weight);
        if(Weight>Maximum-Candidate.TotalWeight)return EStatus::Overflow;
        Candidate.TotalWeight+=Weight;
        Candidate.Slots.push_back({Slot.SlotId,Slot.Weight,0});
    }
    std::sort(Candidate.Slots.begin(),Candidate.Slots.end(),[](const auto& A,const auto& B)
        {return A.SlotId<B.SlotId;});
    for(std::size_t I=1;I<Candidate.Slots.size();++I)
        if(Candidate.Slots[I-1].SlotId==Candidate.Slots[I].SlotId)return EStatus::DuplicateSlot;
    // The sole no-denominator case is the explicitly valid empty zero plan.
    if(Candidate.Slots.empty())return EStatus::Ok;

    const auto Budget=static_cast<std::uint64_t>(Request.Budget);
    std::uint64_t FloorSum=0;
    std::vector<FShare> Shares;Shares.reserve(Candidate.Slots.size());
    for(std::size_t I=0;I<Candidate.Slots.size();++I)
    {
        const auto Weight=static_cast<std::uint64_t>(Candidate.Slots[I].Weight);
        if(Budget!=0&&Weight>Maximum/Budget)return EStatus::Overflow;
        const auto Numerator=Budget*Weight;
        const auto Floor=Numerator/Candidate.TotalWeight;
        if(Floor>Budget-FloorSum)return EStatus::Overflow;
        FloorSum+=Floor;
        Candidate.Slots[I].Coins=static_cast<std::int64_t>(Floor);
        Shares.push_back({I,Numerator%Candidate.TotalWeight});
    }
    std::sort(Shares.begin(),Shares.end(),[&Candidate](const FShare& A,const FShare& B)
    {
        if(A.Remainder!=B.Remainder)return A.Remainder>B.Remainder;
        return Candidate.Slots[A.Index].SlotId<Candidate.Slots[B.Index].SlotId;
    });
    const auto Residual=Budget-FloorSum;
    if(Residual>static_cast<std::uint64_t>(Shares.size()))return EStatus::Overflow;
    for(std::uint64_t I=0;I<Residual;++I)
    {
        auto& Coins=Candidate.Slots[Shares[static_cast<std::size_t>(I)].Index].Coins;
        if(Coins==std::numeric_limits<std::int64_t>::max())return EStatus::Overflow;
        ++Coins;
    }
    return EStatus::Ok;
}
}
EStatus TryAllocate(const FRequest& Request,FAllocation& Out)
{
    try
    {
        FAllocation Candidate;
        const auto Status=Build(Request,Candidate);
        if(Status!=EStatus::Ok)return Status;
        Out=std::move(Candidate);
        return EStatus::Ok;
    }
    catch(const std::bad_alloc&){return EStatus::ResourceFailure;}
    catch(const std::length_error&){return EStatus::ResourceFailure;}
}
}
