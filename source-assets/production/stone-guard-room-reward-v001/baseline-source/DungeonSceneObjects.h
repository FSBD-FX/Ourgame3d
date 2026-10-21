#pragma once

#include "CoreMinimal.h"
#include "DungeonRoomLayout.h"

// In-memory development scene facts. No equipment, health, economic reward or
// persistence authority is stored here. Object identity is (Run,Room,Object).
enum class EDungeonSceneObjectKind : uint8 { Survey, Exit };
enum class EDungeonSceneInteractionKind : uint8 { None, Survey, Exit };
enum class EDungeonSceneFailure : uint8
{
    None, NoTarget, Busy, NotInRange, NoLineOfSight, AlreadySurveyed,
    RoomNotCleared, InvalidRoom, InvalidRequest
};

struct FDungeonSceneObjectView
{
    uint64 ObjectId = 0;
    uint64 RoomInstanceId = 0;
    EDungeonSceneObjectKind Kind = EDungeonSceneObjectKind::Survey;
    FVector2D Position = FVector2D::ZeroVector;
    bool Surveyed = false;
    uint32 SurveyCount = 0;
};

struct FDungeonSceneRoomView
{
    bool Active = false;
    FGuid RunGuid;
    uint64 RoomInstanceId = 0;
    DungeonRoomLayout::FDescription Layout;
    TArray<FDungeonSceneObjectView> Objects;
};

struct FDungeonSceneInteractionView
{
    bool Pending = false;
    bool NeedsConfirmation = false;
    EDungeonSceneInteractionKind Kind = EDungeonSceneInteractionKind::None;
    uint64 RoomInstanceId = 0;
    uint64 ObjectId = 0;
    double AtTime = 0.;
    EDungeonSceneFailure LastFailure = EDungeonSceneFailure::None;
};

struct FDungeonSceneObjectsSnapshot
{
    uint32 Schema = 1;
    FDungeonSceneRoomView CurrentRoom;
    TMap<uint64,FDungeonSceneRoomView> Rooms;
    FDungeonSceneInteractionView Interaction;
};

class FDungeonSceneObjects
{
public:
    void Reset();
    bool BeginRoom(FGuid RunGuid, uint64 RoomInstanceId);
    bool MarkSurvey(uint64 RoomInstanceId, uint64 ObjectId);
    const FDungeonSceneRoomView& Current() const { return CurrentRoom; }
    const FDungeonSceneRoomView* FindRoom(uint64 RoomInstanceId) const;
    FDungeonSceneObjectsSnapshot Capture() const;
    bool Restore(const FDungeonSceneObjectsSnapshot& Snapshot, FString& Diagnostic);
    FDungeonSceneInteractionView Interaction;

private:
    FDungeonSceneRoomView CurrentRoom;
    TMap<uint64,FDungeonSceneRoomView> Rooms;
};
