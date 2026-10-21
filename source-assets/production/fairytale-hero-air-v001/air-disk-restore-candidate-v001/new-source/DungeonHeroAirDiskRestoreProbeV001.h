#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonHeroAirDiskRestoreProbeV001.generated.h"

class UDungeonNativeMainSubmixCaptureV001;
class UTexture2D;
struct FDungeonHeroAirDiskRestoreProofStateV001;
struct FDungeonHeroAirDiskRestoreProofDeleterV001{void operator()(FDungeonHeroAirDiskRestoreProofStateV001*)const;};
// Normal-input observer: no forced gameplay values. Actual Installer restores snapshot state in target.
UCLASS()
class CODEXDUNGEON_API ADungeonHeroAirDiskRestoreProbeV001:public AActor
{
 GENERATED_BODY()
public:
 ADungeonHeroAirDiskRestoreProbeV001();
 virtual ~ADungeonHeroAirDiskRestoreProbeV001()override;
 virtual void BeginPlay()override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 friend struct FDungeonHeroAirDiskRestoreProofStateV001;
 void ScreenshotProcessed();
 TUniquePtr<FDungeonHeroAirDiskRestoreProofStateV001,FDungeonHeroAirDiskRestoreProofDeleterV001> Proof;
 UPROPERTY(Transient) TObjectPtr<UDungeonNativeMainSubmixCaptureV001> MainMixCapture;
 UPROPERTY(Transient) TMap<FString,TObjectPtr<UTexture2D>> ProofTextures;
};
