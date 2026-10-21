#pragma once
#include "CoreMinimal.h"
#include "DungeonExploration.h"

// Durable exploration belongs to the bound Run. HUD/camera are consumers.
struct FDungeonRunExplorationRoom
{
    uint64 RoomInstanceId=0;
    int32 RoomNumber=0;
    DungeonExploration::FState State;
};
struct FDungeonRunExplorationSnapshot
{
    uint32 Schema=1;
    FGuid RunGuid;
    uint64 CurrentRoomInstanceId=0;
    TArray<FDungeonRunExplorationRoom> Rooms;
};
class CODEXDUNGEON_API FDungeonRunExploration
{
public:
    FDungeonRunExploration()=default;
    FDungeonRunExploration(const FDungeonRunExploration&);
    bool Begin(FGuid RunGuid,uint64 RoomInstanceId,int32 RoomNumber,FString& Why);
    bool EnterRoom(uint64 RoomInstanceId,int32 RoomNumber,FString& Why);
    bool Reveal(FGuid RunGuid,uint64 RoomInstanceId,int32 RoomNumber,FVector2D Observer,FString& Why);
    FDungeonRunExplorationSnapshot Capture() const;
    bool Restore(const FDungeonRunExplorationSnapshot&,FString& Why);
    double MemoryAt(FVector2D Point) const;
    int32 ExploredVertexCount() const;
    bool Matches(FGuid RunGuid,uint64 RoomInstanceId) const
    {return Current&&State.RunGuid==RunGuid&&State.CurrentRoomInstanceId==RoomInstanceId;}
    const DungeonExploration::FExploration* CurrentView() const {return Current.Get();}
private:
    FDungeonRunExplorationSnapshot State;
    TUniquePtr<DungeonExploration::FExploration> Current;
};
