#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonGuardArtDeathProbeV005.generated.h"
struct FDungeonGuardArtDeathV005State;
struct FDungeonGuardArtDeathV005Deleter {void operator()(FDungeonGuardArtDeathV005State*)const;};
// Opt-in known44 full-presentation Death normal-J controller-input observer. The normal room owns all births.
UCLASS()
class CODEXDUNGEON_API ADungeonGuardArtDeathProbeV005:public AActor
{
 GENERATED_BODY()
public:
 ADungeonGuardArtDeathProbeV005();
 virtual ~ADungeonGuardArtDeathProbeV005()override;
 virtual void BeginPlay()override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 void ScreenshotProcessed();
 TUniquePtr<FDungeonGuardArtDeathV005State,FDungeonGuardArtDeathV005Deleter> Proof;
};
