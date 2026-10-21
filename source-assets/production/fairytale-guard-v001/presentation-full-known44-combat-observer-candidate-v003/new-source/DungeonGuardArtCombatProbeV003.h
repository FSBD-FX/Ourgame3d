#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonGuardArtCombatProbeV003.generated.h"
struct FDungeonGuardArtCombatV003State;
struct FDungeonGuardArtCombatV003Deleter {void operator()(FDungeonGuardArtCombatV003State*)const;};
// Opt-in known44 full-presentation StunIR normal-J controller-input observer. The normal room owns all births.
UCLASS()
class CODEXDUNGEON_API ADungeonGuardArtCombatProbeV003:public AActor
{
 GENERATED_BODY()
public:
 ADungeonGuardArtCombatProbeV003();
 virtual ~ADungeonGuardArtCombatProbeV003()override;
 virtual void BeginPlay()override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 void ScreenshotProcessed();
 TUniquePtr<FDungeonGuardArtCombatV003State,FDungeonGuardArtCombatV003Deleter> Proof;
};
