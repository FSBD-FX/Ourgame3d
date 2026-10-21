#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonSwdForwardStepProbeV001.generated.h"
class UDungeonNativeMainSubmixCaptureV001;
struct FDungeonSwdForwardStepProofV001;
struct FDungeonSwdForwardStepProofDeleterV001{void operator()(FDungeonSwdForwardStepProofV001*)const;};
UCLASS()
class CODEXDUNGEON_API ADungeonSwdForwardStepProbeV001:public AActor {
 GENERATED_BODY()
public:
 ADungeonSwdForwardStepProbeV001();
 virtual ~ADungeonSwdForwardStepProbeV001()override;
 virtual void BeginPlay()override;
 virtual void Tick(float DeltaSeconds)override;
 virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 friend struct FDungeonSwdForwardStepProofV001;
 void ScreenshotProcessed();
 TUniquePtr<FDungeonSwdForwardStepProofV001,FDungeonSwdForwardStepProofDeleterV001> Proof;
 UPROPERTY(Transient) TObjectPtr<UDungeonNativeMainSubmixCaptureV001> MainMix;
};
