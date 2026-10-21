#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonGuardArtKnown44Probe.generated.h"
struct FDungeonGuardArtKnown44State;
struct FDungeonGuardArtKnown44Deleter {void operator()(FDungeonGuardArtKnown44State*)const;};
// Opt-in known44 full-presentation AxeCycle controller-input observer. The normal room owns all births.
UCLASS()
class CODEXDUNGEON_API ADungeonGuardArtKnown44Probe:public AActor
{
 GENERATED_BODY()
public:
 ADungeonGuardArtKnown44Probe();
 virtual ~ADungeonGuardArtKnown44Probe()override;
 virtual void BeginPlay()override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 void ScreenshotProcessed();
 TUniquePtr<FDungeonGuardArtKnown44State,FDungeonGuardArtKnown44Deleter> Proof;
};
