#include "DungeonSceneObjects.h"

void FDungeonSceneObjects::Reset()
{
    CurrentRoom = {}; Rooms.Reset(); Interaction = {};
}

bool FDungeonSceneObjects::BeginRoom(FGuid RunGuid, uint64 RoomInstanceId)
{
    if (!RunGuid.IsValid() || !RoomInstanceId) return false;
    if (CurrentRoom.Active && CurrentRoom.RunGuid == RunGuid && CurrentRoom.RoomInstanceId == RoomInstanceId) return true;
    if (CurrentRoom.Active && CurrentRoom.RunGuid != RunGuid) return false;
    if (CurrentRoom.Active) Rooms.Add(CurrentRoom.RoomInstanceId,CurrentRoom);
    if (const auto* Existing = Rooms.Find(RoomInstanceId)) CurrentRoom = *Existing;
    else
    {
        CurrentRoom = {}; CurrentRoom.Active = true; CurrentRoom.RunGuid = RunGuid;
        CurrentRoom.RoomInstanceId = RoomInstanceId; CurrentRoom.Layout = DungeonRoomLayout::ExplorationPreview();
        CurrentRoom.Objects.Add({1,RoomInstanceId,EDungeonSceneObjectKind::Survey,CurrentRoom.Layout.Survey,false,0});
        CurrentRoom.Objects.Add({2,RoomInstanceId,EDungeonSceneObjectKind::Exit,CurrentRoom.Layout.Exit,false,0});
        Rooms.Add(RoomInstanceId,CurrentRoom);
    }
    Interaction = {}; return true;
}

bool FDungeonSceneObjects::MarkSurvey(uint64 RoomInstanceId, uint64 ObjectId)
{
    if (!CurrentRoom.Active || CurrentRoom.RoomInstanceId != RoomInstanceId) return false;
    for (auto& Object : CurrentRoom.Objects)
        if (Object.ObjectId == ObjectId && Object.Kind == EDungeonSceneObjectKind::Survey && !Object.Surveyed)
        {
            Object.Surveyed = true; ++Object.SurveyCount;
            Rooms.Add(RoomInstanceId,CurrentRoom); return true;
        }
    return false;
}

const FDungeonSceneRoomView* FDungeonSceneObjects::FindRoom(uint64 RoomInstanceId) const
{
    return CurrentRoom.Active && CurrentRoom.RoomInstanceId == RoomInstanceId ? &CurrentRoom : Rooms.Find(RoomInstanceId);
}

namespace
{
bool FiniteScenePosition(const FVector2D& Position)
{
    return FMath::IsFinite(Position.X)&&FMath::IsFinite(Position.Y);
}
bool KnownSceneLayout(const DungeonRoomLayout::FDescription& Saved)
{
    if(!FiniteScenePosition(Saved.Entry)||!FiniteScenePosition(Saved.Exit)
        ||!FiniteScenePosition(Saved.ExitHalfExtent)||!FiniteScenePosition(Saved.Barrier.Min)
        ||!FiniteScenePosition(Saved.Barrier.Max)||!FiniteScenePosition(Saved.Survey))return false;
    const auto Known=DungeonRoomLayout::ExplorationPreview();
    return Saved.Id==Known.Id&&Saved.Version==Known.Version&&Saved.Entry==Known.Entry&&Saved.Exit==Known.Exit
        &&Saved.ExitHalfExtent==Known.ExitHalfExtent&&Saved.Barrier.bIsValid==Known.Barrier.bIsValid
        &&Saved.Barrier.Min==Known.Barrier.Min&&Saved.Barrier.Max==Known.Barrier.Max&&Saved.Survey==Known.Survey;
}
bool ValidSceneRoom(const FDungeonSceneRoomView& Room,const FGuid& Run)
{
    if(!Room.Active||Room.RunGuid!=Run||!Room.RoomInstanceId||!KnownSceneLayout(Room.Layout)||Room.Objects.Num()!=2)return false;
    for(int32 N=0;N<2;++N)
    {
        const auto& Object=Room.Objects[N];
        if(Object.ObjectId!=uint64(N+1)||Object.RoomInstanceId!=Room.RoomInstanceId
            ||!FiniteScenePosition(Object.Position))return false;
        if(N==0)
        {
            if(Object.Kind!=EDungeonSceneObjectKind::Survey||Object.Position!=Room.Layout.Survey
                ||Object.SurveyCount>1||Object.Surveyed!=(Object.SurveyCount==1))return false;
        }
        else if(Object.Kind!=EDungeonSceneObjectKind::Exit||Object.Position!=Room.Layout.Exit||Object.Surveyed||Object.SurveyCount)return false;
    }
    return true;
}
bool SameSceneRoom(const FDungeonSceneRoomView& A,const FDungeonSceneRoomView& B)
{
    if(A.Active!=B.Active||A.RunGuid!=B.RunGuid||A.RoomInstanceId!=B.RoomInstanceId||A.Objects.Num()!=B.Objects.Num())return false;
    // Both layouts already passed the same immutable versioned definition.
    for(int32 N=0;N<A.Objects.Num();++N)
    {
        const auto& X=A.Objects[N];const auto& Y=B.Objects[N];
        if(X.ObjectId!=Y.ObjectId||X.RoomInstanceId!=Y.RoomInstanceId||X.Kind!=Y.Kind||X.Position!=Y.Position
            ||X.Surveyed!=Y.Surveyed||X.SurveyCount!=Y.SurveyCount)return false;
    }
    return true;
}
}

FDungeonSceneObjectsSnapshot FDungeonSceneObjects::Capture() const
{
    return {1,CurrentRoom,Rooms,Interaction};
}
bool FDungeonSceneObjects::Restore(const FDungeonSceneObjectsSnapshot& Snapshot, FString& Diagnostic)
{
    Diagnostic.Reset();
    const auto Reject=[&Diagnostic](const TCHAR* Why){Diagnostic=Why;return false;};
    if(Snapshot.Schema!=1)return Reject(TEXT("Unknown scene snapshot schema"));
    const auto& Room=Snapshot.CurrentRoom;const auto& Pending=Snapshot.Interaction;
    if(uint8(Pending.LastFailure)>uint8(EDungeonSceneFailure::InvalidRequest)
        ||!FMath::IsFinite(Pending.AtTime)||Pending.AtTime<0)
        return Reject(TEXT("Invalid interaction observation"));
    if(!Room.Active)
    {
        if(Room.RunGuid.IsValid()||Room.RoomInstanceId||!Room.Objects.IsEmpty()||!Snapshot.Rooms.IsEmpty()
            ||!KnownSceneLayout(Room.Layout)||Pending.Pending||Pending.NeedsConfirmation
            ||Pending.Kind!=EDungeonSceneInteractionKind::None||Pending.RoomInstanceId||Pending.ObjectId||Pending.AtTime!=0)
            return Reject(TEXT("Inactive scene contains active or unknown facts"));
    }
    else
    {
        if(!Room.RunGuid.IsValid()||!ValidSceneRoom(Room,Room.RunGuid))return Reject(TEXT("Invalid current scene room"));
        for(const auto& Entry:Snapshot.Rooms)
            if(Entry.Key!=Entry.Value.RoomInstanceId||!ValidSceneRoom(Entry.Value,Room.RunGuid))
                return Reject(TEXT("Scene history Run, room, object or layout mismatch"));
        const auto* Current=Snapshot.Rooms.Find(Room.RoomInstanceId);
        if(!Current||!SameSceneRoom(Room,*Current))return Reject(TEXT("Current room and history disagree"));
        if(Pending.Pending)
        {
            if(Pending.RoomInstanceId!=Room.RoomInstanceId||Pending.LastFailure!=EDungeonSceneFailure::None)
                return Reject(TEXT("Pending interaction belongs to another room or failed observation"));
            const FDungeonSceneObjectView* Object=Room.Objects.FindByPredicate(
                [&Pending](const FDungeonSceneObjectView& Value){return Value.ObjectId==Pending.ObjectId;});
            if(!Object)return Reject(TEXT("Pending interaction references a missing object"));
            if(Pending.Kind==EDungeonSceneInteractionKind::Survey)
            {
                if(Object->Kind!=EDungeonSceneObjectKind::Survey||Object->Surveyed||Pending.NeedsConfirmation)
                    return Reject(TEXT("Pending survey is already consumed or has invalid confirmation"));
            }
            else if(Pending.Kind==EDungeonSceneInteractionKind::Exit)
            {
                if(Object->Kind!=EDungeonSceneObjectKind::Exit)return Reject(TEXT("Pending exit kind mismatch"));
                // NeedsConfirmation=false is a valid accepted exit awaiting its semantic commit.
            }
            else return Reject(TEXT("Unknown pending interaction kind"));
        }
        else if(Pending.NeedsConfirmation||Pending.Kind!=EDungeonSceneInteractionKind::None
            ||Pending.RoomInstanceId||Pending.ObjectId||Pending.AtTime!=0)
            return Reject(TEXT("Inactive interaction contains a live intent"));
    }
    FDungeonSceneObjects Candidate;
    Candidate.CurrentRoom=Room;Candidate.Rooms=Snapshot.Rooms;Candidate.Interaction=Pending;
    *this=MoveTemp(Candidate);return true;
}
