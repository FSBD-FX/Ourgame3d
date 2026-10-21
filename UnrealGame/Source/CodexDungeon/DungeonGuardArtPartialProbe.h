#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonGuardArtPartialProbe.generated.h"
struct FDungeonGuardArtPartialState;
struct FDungeonGuardArtPartialDeleter {void operator()(FDungeonGuardArtPartialState*)const;};
// Opt-in partial art controller-input observer. The normal room owns all births.
UCLASS()
class CODEXDUNGEON_API ADungeonGuardArtPartialProbe:public AActor
{
 GENERATED_BODY()
public:
 ADungeonGuardArtPartialProbe();
 virtual ~ADungeonGuardArtPartialProbe()override;
 virtual void BeginPlay()override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 void ScreenshotProcessed();
 TUniquePtr<FDungeonGuardArtPartialState,FDungeonGuardArtPartialDeleter> Proof;
};
