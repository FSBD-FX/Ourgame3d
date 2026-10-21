#include "DungeonRunExploration.h"
#include "DungeonRoomLayout.h"
#include <limits>

namespace
{
bool Fail(FString& Why,const TCHAR* Message){Why=Message;return false;}
DungeonExploration::FBounds Bounds()
{return {DungeonRoomLayout::MinX,DungeonRoomLayout::MaxX,DungeonRoomLayout::MinY,DungeonRoomLayout::MaxY};}
bool Validate(const FDungeonRunExplorationSnapshot& S,FString& Why)
{
    if(S.Schema!=1||!S.RunGuid.IsValid()||!S.CurrentRoomInstanceId||S.CurrentRoomInstanceId!=uint64(S.Rooms.Num()))
        return Fail(Why,TEXT("Unknown exploration schema or incomplete Run room lineage"));
    int32 PreviousNumber=0;uint64 PreviousId=0;const auto Expected=Bounds();
    for(const auto& R:S.Rooms)
    {
        const auto& B=R.State.Bounds;
        if(PreviousNumber==MAX_int32||R.RoomInstanceId!=PreviousId+1||R.RoomNumber!=PreviousNumber+1
            ||R.State.RoomId!=R.RoomNumber||B.MinX!=Expected.MinX||B.MaxX!=Expected.MaxX||B.MinY!=Expected.MinY||B.MaxY!=Expected.MaxY)
            return Fail(Why,TEXT("Exploration room identity, display label, or known layout differs"));
        DungeonExploration::FExploration Check(Expected,R.RoomNumber);
        if(!Check.Restore(R.State))return Fail(Why,TEXT("Invalid original exploration grid or value"));
        PreviousId=R.RoomInstanceId;PreviousNumber=R.RoomNumber;
    }
    Why.Reset();return true;
}
FDungeonRunExplorationRoom NewRoom(uint64 Id,int32 Number)
{
    DungeonExploration::FExploration Empty(Bounds(),Number);
    return {Id,Number,Empty.Capture()};
}
}
FDungeonRunExploration::FDungeonRunExploration(const FDungeonRunExploration& Other):State(Other.State)
{if(Other.Current)Current=MakeUnique<DungeonExploration::FExploration>(*Other.Current);}
bool FDungeonRunExploration::Begin(FGuid RunGuid,uint64 RoomInstanceId,int32 RoomNumber,FString& Why)
{
    if(State.RunGuid.IsValid()||Current||!State.Rooms.IsEmpty()||RoomInstanceId!=1||RoomNumber!=1)
        return Fail(Why,TEXT("Only a fresh Run may initialize exploration room1"));
    FDungeonRunExplorationSnapshot Candidate;Candidate.RunGuid=RunGuid;Candidate.CurrentRoomInstanceId=RoomInstanceId;
    Candidate.Rooms.Add(NewRoom(RoomInstanceId,RoomNumber));if(!Validate(Candidate,Why))return false;
    auto Memory=MakeUnique<DungeonExploration::FExploration>(Bounds(),RoomNumber);
    State=MoveTemp(Candidate);Current=MoveTemp(Memory);return true;
}
bool FDungeonRunExploration::EnterRoom(uint64 RoomInstanceId,int32 RoomNumber,FString& Why)
{
    if(!Current||State.Rooms.IsEmpty()||State.CurrentRoomInstanceId==std::numeric_limits<uint64>::max()
        ||State.Rooms.Last().RoomNumber==MAX_int32||RoomInstanceId!=State.CurrentRoomInstanceId+1||RoomNumber!=State.Rooms.Last().RoomNumber+1)
        return Fail(Why,TEXT("Exploration transfer must follow the current real room"));
    auto Candidate=Capture();Candidate.Rooms.Add(NewRoom(RoomInstanceId,RoomNumber));Candidate.CurrentRoomInstanceId=RoomInstanceId;
    if(!Validate(Candidate,Why))return false;
    auto Memory=MakeUnique<DungeonExploration::FExploration>(Bounds(),RoomNumber);
    State=MoveTemp(Candidate);Current=MoveTemp(Memory);return true;
}
bool FDungeonRunExploration::Reveal(FGuid RunGuid,uint64 RoomInstanceId,int32 RoomNumber,FVector2D Observer,FString& Why)
{
    if(!Matches(RunGuid,RoomInstanceId)||State.Rooms.IsEmpty()||State.Rooms.Last().RoomNumber!=RoomNumber
        ||!FMath::IsFinite(Observer.X)||!FMath::IsFinite(Observer.Y)||Observer.X<DungeonRoomLayout::MinX||Observer.X>DungeonRoomLayout::MaxX
        ||Observer.Y<DungeonRoomLayout::MinY||Observer.Y>DungeonRoomLayout::MaxY)
        return Fail(Why,TEXT("Exploration observation has no matching Run/room/ground position"));
    Current->Reveal({Observer.X,Observer.Y});Why.Reset();return true;
}
FDungeonRunExplorationSnapshot FDungeonRunExploration::Capture() const
{
    auto Out=State;if(Current&&!Out.Rooms.IsEmpty())Out.Rooms.Last().State=Current->Capture();return Out;
}
bool FDungeonRunExploration::Restore(const FDungeonRunExplorationSnapshot& Saved,FString& Why)
{
    auto Candidate=Saved;
    if(!Validate(Candidate,Why))return false;
    const auto& Last=Candidate.Rooms.Last();
    auto Memory=MakeUnique<DungeonExploration::FExploration>(Last.State.Bounds,Last.RoomNumber);
    if(!Memory->Restore(Last.State))return Fail(Why,TEXT("Current exploration grid rejected"));
    State=MoveTemp(Candidate);Current=MoveTemp(Memory);Why.Reset();return true;
}
double FDungeonRunExploration::MemoryAt(FVector2D P) const{return Current?Current->MemoryAt({P.X,P.Y}):0.;}
int32 FDungeonRunExploration::ExploredVertexCount() const{return Current?int32(Current->ExploredVertexCount()):0;}
