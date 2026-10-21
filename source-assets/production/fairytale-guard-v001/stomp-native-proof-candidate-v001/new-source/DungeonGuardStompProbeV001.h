#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonGuardStompProbeV001.generated.h"
struct FDungeonGuardStompProofState;
struct FDungeonGuardStompProofDeleter {void operator()(FDungeonGuardStompProofState*)const;};
UCLASS()
class CODEXDUNGEON_API ADungeonGuardStompProbeV001:public AActor
{
 GENERATED_BODY()
public:
 ADungeonGuardStompProbeV001();virtual ~ADungeonGuardStompProbeV001()override;
 virtual void BeginPlay()override;virtual void Tick(float DeltaSeconds)override;virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 void ScreenshotProcessed();TUniquePtr<FDungeonGuardStompProofState,FDungeonGuardStompProofDeleter> Proof;
};
