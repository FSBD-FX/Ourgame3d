#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonGuardRoomFlowProbe.generated.h"
struct FDungeonGuardRoomFlowState;
struct FDungeonGuardRoomFlowDeleter {void operator()(FDungeonGuardRoomFlowState*)const;};
// Opt-in diagnostic controller-input observer. The normal room owns all births.
UCLASS()
class CODEXDUNGEON_API ADungeonGuardRoomFlowProbe:public AActor
{
 GENERATED_BODY()
public:
 ADungeonGuardRoomFlowProbe();
 virtual ~ADungeonGuardRoomFlowProbe()override;
 virtual void BeginPlay()override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 void ScreenshotProcessed();
 TUniquePtr<FDungeonGuardRoomFlowState,FDungeonGuardRoomFlowDeleter> Proof;
};
