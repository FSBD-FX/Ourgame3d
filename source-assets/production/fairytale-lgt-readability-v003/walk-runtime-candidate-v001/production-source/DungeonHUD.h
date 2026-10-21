#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "DungeonStoneFeedback.h"
#include "DungeonExploration.h"
#include "DungeonWorldProjectiles.h"
#include "DungeonActionAudioFeedback.h"
#include "DungeonFairytaleLookdevState.h"
#include "DungeonFairytaleSwordDrawState.h"
#include "DungeonHUD.generated.h"

class UTexture2D;
class UFont;
class USoundBase;
class UMaterialInterface;
class UMaterialInstanceDynamic;
class ADungeonFighter;
class ADungeonGameMode;
struct FDungeonRunAudioContinuation;

struct FDungeonActionAudioPlayRequest
{
    FDungeonActionAudioRecord Source;
    FString SoundPath;
    double RequestedAt = 0.;
    float Volume = 0.f, Pitch = 1.f;
};

/** A fixed 2D presentation of the ground plane; jump elevation is independent. */
UCLASS()
class CODEXDUNGEON_API ADungeonHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void DrawHUD() override;
    void AttachRestoredRunPresentation(const FDungeonRunAudioContinuation& Saved,uint64 Epoch);
    int32 GetStoneAudioPlayRequests(const FString& Cue) const { return StoneAudioPlayRequests.FindRef(Cue); }
    int32 GetExplorationRoomNumber() const { const auto E=CurrentExploration();return E?E->RoomId():0; }
    uint64 GetExplorationResetSerial() const { return ExplorationResetSerial; }
    int32 GetExploredVertexCount() const {const auto E=CurrentExploration();return E?int32(E->ExploredVertexCount()):0;}
    double GetExplorationMemoryAt(FVector2D Position) const {const auto E=CurrentExploration();return E?E->MemoryAt({Position.X,Position.Y}):0.;}
    double GetCurrentVisibilityAt(FVector2D Position) const;
    FVector2D GetCameraGroundCenter() const { return FVector2D(CameraX,0.0); }
    const FString& GetRenderedPlayerTexturePath() const { return RenderedPlayerTexturePath; }
    float GetRenderedPlayerSpriteSize() const { return RenderedPlayerSpriteSize; }
    bool GetInterfaceVisible() const { return bShowInterface; }
    int32 GetRenderedTextDrawCalls() const { return RenderedTextDrawCalls; }
    float GetRenderedActorSpriteSize(ADungeonFighter* Fighter) const { return RenderedActorSpriteSizes.FindRef(Fighter); }
    bool GetRenderedArmorLayersUsed() const { return bRenderedArmorLayersUsed; }
    const TArray<FString>& GetRenderedArmorLayerPaths() const { return RenderedArmorLayerPaths; }
    const TArray<FString>& GetRenderedPlayerDrawStack() const { return RenderedPlayerDrawStack; }
    bool GetRenderedWeaponBodyUsed() const { return bRenderedWeaponBodyUsed; }
    int32 GetRenderedWeaponBodyFrame() const { return RenderedWeaponBodyFrame; }
    int32 GetRenderedWeaponBodyFacing() const { return RenderedWeaponBodyFacing; }
    FVector2D GetRenderedWeaponBodyEmitScreen() const { return RenderedWeaponBodyEmitScreen; }
    const FString& GetRenderedWeaponBodyClip() const { return RenderedWeaponBodyClip; }
    int32 GetQueuedPlayerMeleeTrailCount() const;
    uint64 GetRenderedWeaponBodyActionId() const { return RenderedWeaponBodyActionId; }
    double GetRenderedWeaponBodySampleTime() const { return RenderedWeaponBodySampleTime; }
    uint64 GetRenderedWeaponBodyInstanceId() const { return RenderedWeaponBodyInstanceId; }
    int32 GetRenderedWeaponStateIndex() const { return RenderedWeaponStateIndex; }
    const TArray<FString>& GetRenderedScenePropPaths() const { return RenderedScenePropPaths; }
    bool GetRenderedSceneSurveyVisible() const { return bRenderedSceneSurveyVisible; }
    int32 GetWorldWeaponAudioRequests(const FString& Cue) const { return WorldWeaponAudioRequests.FindRef(Cue); }
    int32 GetActionAudioPlayRequests(const FString& Cue) const { return ActionAudioPlayRequests.FindRef(Cue); }
    const TArray<FDungeonActionAudioPlayRequest>& GetActionAudioPlayReceipts() const { return ActionAudioPlayReceipts; }
    const FFairytaleLookdevDraw& GetFairytaleLookdevDraw() const { return FairytaleLookdevDraw; }
    const FDungeonFairytaleSwordDraw& GetFairytaleSwordDraw() const { return FairytaleSwordDraw; }
private:
    UPROPERTY() TObjectPtr<UFont> ChineseFont;
    UPROPERTY() TMap<FString,TObjectPtr<UTexture2D>> Frames;
    UPROPERTY() TArray<TObjectPtr<USoundBase>> PreloadedSounds;
    UPROPERTY() TObjectPtr<UTexture2D> RoomFarBackground;
    UPROPERTY() TObjectPtr<UTexture2D> RoomMidBackground;
    UPROPERTY() TObjectPtr<UTexture2D> RoomFloorTexture;
    UPROPERTY() TMap<FString,TObjectPtr<USoundBase>> StoneSounds;
    struct FStoneEffect { TWeakObjectPtr<ADungeonFighter> Owner; DungeonStoneFeedback::FRecord Record; double Started=0; };
    TMap<TWeakObjectPtr<ADungeonFighter>,uint64> StoneEventCursors;
    TMap<FString,int32> StoneAudioPlayRequests;
    UPROPERTY() TObjectPtr<UMaterialInterface> PlayerOutlineMaterial;
    UPROPERTY() TArray<TObjectPtr<UMaterialInstanceDynamic>> OutlineInstances;
    struct FActorQuad {
        TWeakObjectPtr<ADungeonFighter> Owner; UTexture2D* Texture=nullptr;
        FVector2D Top; float Size=0,Rotation=0; FVector2D Pivot=FVector2D::ZeroVector;
        FLinearColor Tint=FLinearColor::White; bool Weapon=false;
    };
    TArray<FActorQuad> ActorQuads;
    struct FMeleeTrail { TWeakObjectPtr<ADungeonFighter> Owner; FString Clip; int32 Frame=0; float Size=0; bool CandidateWeapon=false; };
    TArray<FMeleeTrail> MeleeTrails;
    TArray<FStoneEffect> StoneEffects;
    UPROPERTY() TMap<FString,TObjectPtr<USoundBase>> WorldWeaponSounds;
    FGuid WorldWeaponRun;
    uint64 WorldWeaponCursor=0;
    TArray<FDungeonWorldWeaponEvent> WorldWeaponEffects;
    TMap<FString,int32> WorldWeaponAudioRequests;
    UPROPERTY() TMap<FString,TObjectPtr<USoundBase>> ActionAudioSounds;
    FGuid ActionAudioRun;
    uint64 ActionAudioCursor = 0;
    uint64 RestoredRunPresentationEpoch=0;
    bool bUseFairytaleSwordWalkPreview=false;
    bool bUseFairytaleSwordEquipmentBoundPreview=false;
    bool bUseFairytaleSwordBodyPreview=false;
    bool bUseFairytaleSwordBodyV002Preview=false;
    bool bUseFairytaleSwordPrimary2Preview=false; // Bounded native169 independent-sword fit; no stage2 armor yet.
    bool bUseFairytaleSwordArmorReadyPreview=false;
    UTexture2D* GetFairytaleSwordArmorReadyTexture(const FString& Component,int32 Frame);
    bool bUseFairytaleSwordArmorPrimary1Preview=false;
    UTexture2D* GetFairytaleSwordArmorPrimary1Texture(const FString& Component,int32 Frame);
    FDungeonFairytaleSwordDraw FairytaleSwordDraw;
    UTexture2D* GetFairytaleSwordTexture(const FString& Clip,int32 Index);
    bool DrawFairytaleSwordBody(ADungeonFighter* Fighter);
    bool bActionAudioAttached = false;
    TMap<FString,int32> ActionAudioPlayRequests;
    TArray<FDungeonActionAudioPlayRequest> ActionAudioPlayReceipts;
    TUniquePtr<DungeonExploration::FExploration> Exploration;
    const DungeonExploration::FExploration* CurrentExploration() const;
    FGuid BoundExplorationRun;
    uint64 BoundExplorationRoom=0;
    TWeakObjectPtr<ADungeonFighter> ExplorationOwner;
    uint64 ExplorationResetSerial = 0;
    uint64 ExplorationRunRestartSerial = 0;
    float CameraX = 0.f;
    FString RenderedPlayerTexturePath;
    float RenderedPlayerSpriteSize = 0.f;
    TMap<ADungeonFighter*,float> RenderedActorSpriteSizes;
    int32 RenderedTextDrawCalls = 0;
    bool bShowInterface = false;
    bool bRenderedArmorLayersUsed = false;
    TArray<FString> RenderedArmorLayerPaths;
    TArray<FString> RenderedPlayerDrawStack;
    bool bRenderedWeaponBodyUsed = false;
    int32 RenderedWeaponBodyFrame = -1, RenderedWeaponBodyFacing = 0;
    FVector2D RenderedWeaponBodyEmitScreen = FVector2D::ZeroVector;
    FString RenderedWeaponBodyClip;
    TArray<FString> RenderedScenePropPaths;
    bool bRenderedSceneSurveyVisible = false;
    uint64 RenderedWeaponBodyActionId = 0;
    uint64 RenderedWeaponBodyInstanceId = 0;
    int32 RenderedWeaponStateIndex = -1;
    double RenderedWeaponBodySampleTime = 0.;
    float UIScale = 1.f;
    FVector2D Origin = FVector2D::ZeroVector;
    bool bUseCandidateSprites = false;
    bool bUseArmorLayerPreview = false;
    bool bUseArmorSleevesPreview = false;
    bool bUseWeaponBodyPreview = false;
    bool bUseXBWPrimaryBodyPreview = false;
    bool bUseXBWReloadBodyPreview = false;
    bool bUseReadabilityMaterial = false;
    bool bUseFairytaleLookdevPreview = false;
    bool bUseFairytaleWalkLookdevPreview = false;
    bool bUseFairytaleChestLookdevPreview = false;
    bool bUseFairytaleShoulderLookdevPreview = false;
    bool bUseFairytaleLimbLookdevPreview = false;
    FFairytaleLookdevDraw FairytaleLookdevDraw;
    void BeginFairytaleLookdev();
    void DrawFairytaleLookdev(ADungeonGameMode* Game);
    FVector2D Screen(float X, float Y) const;
    FVector2D Ground(FVector2D Position) const;
    void Box(float X,float Y,float W,float H,FLinearColor Color);
    void Line(float X,float Y,float X2,float Y2,FLinearColor Color,float Width=1.f);
    void Text(const FString& Value,float X,float Y,float Size,FLinearColor Color);
    void Triangle(FVector2D A,FVector2D B,FVector2D C,FLinearColor Color);
    void Oval(float X,float Y,float W,float H,FLinearColor Color);
    void DrawRoom(float Time,bool bCleared);
    void DrawRoomParallax(UTexture2D* Texture,float ScrollFactor);
    void UpdateRoomView(ADungeonGameMode* Game);
    void DrawExplorationFog(float Time);
    void DrawFighter(ADungeonFighter* Fighter);
    void DrawInterface(ADungeonGameMode* Game);
    void DrawEquipmentSources(ADungeonGameMode* Game);
    void DrawEquipmentPanel(ADungeonGameMode* Game);
    UTexture2D* GetFrame(bool bEnemy,const FString& Clip,int32 Frame);
    UTexture2D* GetCandidateFrame(const FString& Actor,const FString& Clip,int32 Frame);
    UTexture2D* GetCandidateSword();
    UTexture2D* GetXBWReadyTexture(const FString& Track,int32 Frame=0,bool Primary=false);
    UTexture2D* GetXBWReloadTexture(const FString& Track,int32 Frame);
    UTexture2D* GetXBWArmorTexture(const FString& Clip,const FString& Armor,const FString& Track,int32 Frame);
    UTexture2D* GetScenePropTexture(bool Wall);
    bool DrawXBWReadyWeapon(ADungeonFighter* Fighter,float Size,FLinearColor Tint,bool Primary=false);
    UTexture2D* GetArmorLayerFrame(const FString& Clip,const FString& Armor,const FString& Layer,int32 Frame);
    bool DrawCandidateSword(ADungeonFighter* Fighter,UTexture2D* Body,const FString& Clip,int32 Frame,float Size,FLinearColor Tint,bool ReplayHandPolygon=true);
    void UpdateStoneFeedback(ADungeonGameMode* Game);
    void DrawStoneTelegraph(ADungeonFighter* Fighter);
    void DrawStoneEffects(ADungeonFighter* Fighter);
    void DrawMeleeTrail(ADungeonFighter* Fighter,const FString& Clip,int32 Frame,float Size,bool CandidateWeapon);
    void DrawPlayerOcclusionOutline(ADungeonFighter* Player);
    void UpdateWorldWeaponFeedback(ADungeonGameMode* Game);
    void UpdateActionAudioFeedback(ADungeonGameMode* Game);
    void DrawWorldWeaponFeedback(ADungeonGameMode* Game);
    void DrawWorldWeaponGround(ADungeonGameMode* Game);
    void DrawWorldWeaponProjectile(const FDungeonWorldProjectile& Projectile,double SimulationTime);
};
