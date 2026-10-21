#include "DungeonHUD.h"
#include "DungeonFairytaleSwordWalkTextures.inl"
#include "DungeonFairytaleSwordHurtTextures.inl"
#include "DungeonFairytaleSwordDeathTextures.inl"
#include "DungeonFairytaleSwordDodgeTextures.inl"
#include "DungeonFairytaleSwordEquipmentBinding.h"
#include "DungeonPresentationScale.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "DungeonProbe.h"
#include "DungeonContentProbe.h"
#include "DungeonFairytaleLookdevProbe.h"
#include "DungeonFairytaleSwordProbe.h"
#include "DungeonFairytaleEquipmentBoundProbe.h"
#include "DungeonFairytaleWalkProbe.h"
#include "DungeonGuardRoomFlowProbe.h"
#include "DungeonGuardArtPartialProbe.h"
#include "DungeonGuardArtKnown44Probe.h"
#include "DungeonGuardArtCombatProbeV003.h"
#include "DungeonHeroHurtProbeV001.h"
#include "DungeonHeroDeathProbeV001.h"
#include "DungeonGuardStompProbeV001.h"
#include "DungeonHeroDodgeProbeV001.h"
#include "DungeonGuardMoveProbeV001.h"
#include "DungeonHeroAirProbeV001.h"
#include "DungeonHeroAirProductionProbeV001.h"
#include "DungeonGuardArtDeathProbeV005.h"
#include "DungeonRunContinueProbe.h"
#include "DungeonGuardRunContinueProbe.h"
#include "DungeonRoomLayout.h"
#include "DungeonXBWBodyPose.h"
#include "DungeonRunSnapshot.h"
#include "Engine/Canvas.h"
#include "Engine/Font.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "GlobalRenderResources.h"
#include "CanvasItem.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/PackageName.h"
#include "RenderingThread.h"
#include "Sound/SoundBase.h"
#include "DungeonCandidateAssemblyV007.inl"
#include "DungeonProofScreenshots.h"
#include "DungeonEquipmentLabels.inl"
#include "DungeonCandidateAssemblyTuningV002.h"
#include "TextureResource.h"
#include "DungeonFairytaleSwordPrimary2ArmorV001.inl"
#include "DungeonFairytaleSwordPrimary3V001.inl"
#include "HAL/PlatformTime.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"
#if WITH_EDITOR
#include "TextureCompiler.h"
#endif

namespace DungeonCandidateAssembly = DungeonCandidateAssemblyV007;

namespace DungeonPalette
{
    const FLinearColor Ink(.025f,.035f,.055f,1.f);
    const FLinearColor Wall(.10f,.15f,.19f,1.f);
    const FLinearColor Mortar(.065f,.10f,.13f,1.f);
    const FLinearColor Gold(.94f,.66f,.28f,1.f);
    const FLinearColor Cream(.91f,.88f,.77f,1.f);
    const FLinearColor Muted(.48f,.59f,.61f,1.f);
}

void ADungeonHUD::BeginPlay()
{
    Super::BeginPlay();
    bCombatRangeDebug=FParse::Param(FCommandLine::Get(),TEXT("DungeonCombatRangeDebug"));
    bCombatRangeProof=FParse::Param(FCommandLine::Get(),TEXT("DungeonCombatRangeProof"));
    bUseFairytaleSwordEquipmentBoundPreview=FParse::Param(FCommandLine::Get(),DungeonFairytaleSwordEquipmentBinding::CommandLineFlag);
    bUseFairytaleSwordHurtPreview=bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),DungeonFairytaleSwordHurtV001::CommandLineFlag);
    bUseFairytaleSwordDeathPreview=bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),DungeonFairytaleSwordDeathV001::CommandLineFlag);
    bUseFairytaleSwordDodgePreview=bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),DungeonFairytaleSwordDodgeV001::CommandLineFlag);
    bUseFairytaleSwordAirPreview=bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),DungeonFairytaleSwordAirV001::CommandLineFlag);
    bUseFairytaleSwordSecondaryPreview=bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordSecondaryPreview"));
    bUseFairytaleSwordWalkPreview=bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordWalkPreview"));
    bUseFairytaleLookdevPreview=!bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLookdevPreview"));
    if(bUseFairytaleLookdevPreview){BeginFairytaleLookdev();return;}
    bShowInterface = FParse::Param(FCommandLine::Get(),TEXT("DungeonShowInterface"));
    ChineseFont = LoadObject<UFont>(nullptr,TEXT("/Game/ThirdParty/Fonts/NotoSansCJKsc/F_NotoSansCJKsc_Regular.F_NotoSansCJKsc_Regular"));
    if(ChineseFont) { ChineseFont->LegacyFontSize=24; ChineseFont->LegacyFontName=TEXT("Regular"); }
    bUseCandidateSprites = FParse::Param(FCommandLine::Get(),TEXT("DungeonCandidateSprites"));
    // Bound mode enables current source/preload selection; only the resolver may authorize armor drawing.
    bUseFairytaleSwordPrimary2Preview=bUseFairytaleSwordEquipmentBoundPreview
        ||FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2Preview"))
        ||FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2BodyPreview"))
        ||DungeonFairytaleSwordPrimary2ArmorV001::Enabled()
        ||DungeonFairytaleSwordPrimary3V001::Enabled();
    bUseFairytaleSwordArmorPrimary1Preview=bUseFairytaleSwordPrimary2Preview||FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordArmorPrimary1Preview"));
    bUseFairytaleSwordArmorReadyPreview=bUseFairytaleSwordArmorPrimary1Preview||FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordArmorReadyPreview"));
    bUseFairytaleSwordBodyV002Preview=bUseFairytaleSwordArmorReadyPreview||FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordBodyV002Preview"));
    bUseFairytaleSwordBodyPreview=bUseFairytaleSwordBodyV002Preview||FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordBodyPreview"));
    if(bUseFairytaleSwordBodyPreview)
    {
        for(const FString Clip:{TEXT("sword_ready_idle"),TEXT("sword_primary_1")})
            for(int32 I=0;I<(Clip==TEXT("sword_ready_idle")?4:6);++I)GetFairytaleSwordTexture(Clip,I);
        if(bUseFairytaleSwordPrimary2Preview)
            for(int32 I=0;I<6;++I)GetFairytaleSwordTexture(TEXT("sword_primary_2"),I);
        GetCandidateSword();
    }
    if(bUseFairytaleSwordArmorReadyPreview)
    {
        // Load every selected armor phase before the existing startup render flush.
        // A valid UTexture/GetResource alone did not make first-use pixels ready.
        TArray<UTexture*> ReadyArmorTextures;
        for(const FString Component:{TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),
            TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("NearHand")})
            for(int32 I=0;I<4;++I)
                if(auto Texture=GetFairytaleSwordArmorReadyTexture(Component,I))ReadyArmorTextures.Add(Texture);
        if(bUseFairytaleSwordArmorPrimary1Preview)
            for(const FString Component:{TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),
                TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT("NearHand")})
                for(int32 I=0;I<6;++I)
                    if(auto Texture=GetFairytaleSwordArmorPrimary1Texture(Component,I))ReadyArmorTextures.Add(Texture);
        if(bUseFairytaleSwordEquipmentBoundPreview || DungeonFairytaleSwordPrimary2ArmorV001::Enabled() || DungeonFairytaleSwordPrimary3V001::Enabled())
            for(const FString Component:{TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),
                TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT("NearHand")})
                for(int32 I=0;I<6;++I)
                    if(auto Texture=DungeonFairytaleSwordPrimary2ArmorV001::GetTexture(Component,I,Frames,
                        bUseFairytaleSwordEquipmentBoundPreview&&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary2Preview"))))ReadyArmorTextures.Add(Texture);
        if(bUseFairytaleSwordEquipmentBoundPreview || DungeonFairytaleSwordPrimary3V001::Enabled())
            for(const FString Component:{TEXT("Body"),TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),
                TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT("NearHand")})
                for(int32 I=0;I<6;++I)
                    if(auto Texture=DungeonFairytaleSwordPrimary3V001::GetTexture(Component,I,Frames,
                        bUseFairytaleSwordEquipmentBoundPreview&&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary3Preview"))))ReadyArmorTextures.Add(Texture);
        // The complete selected draw also needs the independent sword and the
        // source body used by the explicitly unsupported-state placeholder.
        for(const FString Clip:{TEXT("sword_ready_idle"),TEXT("sword_primary_1")})
            for(int32 I=0;I<(Clip==TEXT("sword_ready_idle")?4:6);++I)
                if(auto Texture=GetFairytaleSwordTexture(Clip,I))ReadyArmorTextures.Add(Texture);
        if(auto Texture=GetCandidateSword())ReadyArmorTextures.Add(Texture);
        if(bUseFairytaleSwordPrimary2Preview)
            for(int32 I=0;I<6;++I)
                if(auto Texture=GetFairytaleSwordTexture(TEXT("sword_primary_2"),I))ReadyArmorTextures.Add(Texture);
        if(bUseFairytaleSwordWalkPreview)
            for(const FString Component:{TEXT("Body"),TEXT("BodyRest"),TEXT("NearArmWithoutHand"),TEXT("HelmetForeground"),
                TEXT("NearHand"),TEXT("ShoulderFar"),TEXT("Chest"),TEXT("ShoulderNear")})
                for(int32 I=0;I<6;++I)
                    if(auto Texture=DungeonFairytaleSwordWalkV001::GetTexture(Component,I,Frames))ReadyArmorTextures.Add(Texture);
        if(bUseFairytaleSwordHurtPreview)
        {
            // Complete32 sources include transparent FarHand1/2/3. Compile them
            // and the existing independent sword before the existing render flush.
            const auto& HurtProfile=DungeonFairytaleSwordHurtV001::Profile();
            for(const auto& Phase:HurtProfile.Frames)
                for(const auto& Layer:Phase.Layers)
                    if(auto Texture=DungeonFairytaleSwordHurtV001::PreloadTexture(Layer.TexturePath,Frames))ReadyArmorTextures.Add(Texture);
            if(auto Texture=DungeonFairytaleSwordHurtV001::PreloadTexture(HurtProfile.SwordTexturePath,Frames))ReadyArmorTextures.Add(Texture);
        }
        if(bUseFairytaleSwordDeathPreview)
        {
            // Own source40 plus the existing sword41. All compile/initialize
            // during configured startup, before the existing render flush.
            const auto& DeathProfile=DungeonFairytaleSwordDeathV001::Profile();
            for(const auto& Phase:DeathProfile.Frames)
                for(const auto& Layer:Phase.Layers)
                    if(auto Texture=DungeonFairytaleSwordDeathV001::PreloadTexture(Layer.TexturePath,Frames))ReadyArmorTextures.Add(Texture);
            if(auto Texture=DungeonFairytaleSwordDeathV001::PreloadTexture(DeathProfile.SwordTexturePath,Frames))ReadyArmorTextures.Add(Texture);
        }
        if(bUseFairytaleSwordDodgePreview)
        {
            // All32 nonempty owners and existing sword33 finish at startup.
            const auto& DodgeProfile=DungeonFairytaleSwordDodgeV001::Profile();
            for(const auto& Phase:DodgeProfile.Frames)
                for(const auto& Layer:Phase.Layers)
                    if(auto Texture=DungeonFairytaleSwordDodgeV001::PreloadTexture(Layer.TexturePath,Frames))ReadyArmorTextures.Add(Texture);
            if(auto Texture=DungeonFairytaleSwordDodgeV001::PreloadTexture(DodgeProfile.SwordTexturePath,Frames))ReadyArmorTextures.Add(Texture);
        }
        PreloadFairytaleSwordSecondary(ReadyArmorTextures);
#if WITH_EDITOR
        FTextureCompilingManager::Get().FinishCompilation(ReadyArmorTextures);
#endif
    }
    bUseWeaponBodyPreview = bUseCandidateSprites && FParse::Param(FCommandLine::Get(),TEXT("DungeonWeaponBodyPreview"));
    bUseXBWPrimaryBodyPreview = bUseWeaponBodyPreview && FParse::Param(FCommandLine::Get(),TEXT("DungeonXBWPrimaryBodyPreview"));
    bUseXBWReloadBodyPreview = bUseWeaponBodyPreview && FParse::Param(FCommandLine::Get(),TEXT("DungeonXBWReloadBodyPreview"));
    bUseXBWPrimaryBodyPreview |= bUseXBWReloadBodyPreview;
    bUseArmorSleevesPreview = bUseCandidateSprites && FParse::Param(FCommandLine::Get(),TEXT("DungeonArmorSleevesPreview"));
    bUseArmorLayerPreview = bUseCandidateSprites && (FParse::Param(FCommandLine::Get(),TEXT("DungeonArmorLayerPreview")) || bUseArmorSleevesPreview);
    if(bUseXBWReloadBodyPreview&&bUseArmorLayerPreview)
        for(const FString Armor:{TEXT("ARM-LGT-001"),TEXT("ARM-MED-001"),TEXT("ARM-HVY-001"),TEXT("ARM-ROB-001")})
            for(const FString Clip:{TEXT("primary"),TEXT("reload"),TEXT("ready_idle")})
                for(int32 I=0;I<(Clip==TEXT("reload")?4:6);++I)
                    for(const FString Track:{TEXT("armor_far"),TEXT("armor_near")})GetXBWArmorTexture(Clip,Armor,Track,I);
    const auto LoadRoomTexture=[](const FString& Name)->UTexture2D*
    {
        const FString Package=TEXT("/Game/Production/RoomArt/v001/")+Name;
        return FPackageName::DoesPackageExist(Package) ? LoadObject<UTexture2D>(nullptr,*(Package+TEXT(".")+Name)) : nullptr;
    };
    RoomFarBackground=LoadRoomTexture(TEXT("T_RoomFar_v001"));
    RoomMidBackground=LoadRoomTexture(TEXT("T_RoomMid_v001"));
    RoomFloorTexture=LoadRoomTexture(TEXT("T_RoomFloor_v001"));
    GetScenePropTexture(true);GetScenePropTexture(false);
    if(bUseXBWReloadBodyPreview)
        for(int32 I=0;I<4;++I)
            for(const FString Track:{TEXT("body_far"),TEXT("body_support"),TEXT("body_near"),TEXT("weapon")})GetXBWReloadTexture(Track,I);
    // First use must not draw a valid Texture2D whose render resource is still pending.
    // These are the 64 existing QA textures, not the formal content atlas.
    for (const bool Enemy : {false, true})
        for (const FString Clip : {TEXT("idle"), TEXT("walk"), TEXT("attack"), TEXT("hurt"), TEXT("death")})
        {
            const int32 Count = Clip == TEXT("attack") ? 6 : Clip == TEXT("hurt") ? 2 : 8;
            for (int32 Frame=0; Frame<Count; ++Frame) GetFrame(Enemy, Clip, Frame);
        }
    if (bUseCandidateSprites)
    {
        for (const FString Clip : {TEXT("idle"),TEXT("walk"),TEXT("primary_1"),TEXT("primary_2"),TEXT("primary_3"),
            TEXT("jump"),TEXT("fall"),TEXT("land"),TEXT("hurt"),TEXT("death"),TEXT("dodge"),TEXT("secondary"),TEXT("air_primary_1"),TEXT("equip_weapon"),TEXT("equip_armor")})
            for (int32 Frame=0;Frame<DungeonCandidateAssembly::Count(Clip);++Frame) GetCandidateFrame(TEXT("hero"),Clip,Frame);
        for (const FString Clip : {TEXT("dormant"),TEXT("wake"),TEXT("idle"),TEXT("walk"),TEXT("charge"),TEXT("shield_bash"),TEXT("recovery"),TEXT("hurt"),TEXT("death")})
            for (int32 Frame=0;Frame<6;++Frame) GetCandidateFrame(TEXT("stone"),Clip,Frame);
        GetCandidateSword();
        if(bUseWeaponBodyPreview)
        {
            GetXBWReadyTexture(TEXT("weapon"));
            for(int32 I=0;I<6;++I)
                for(const FString Track:{TEXT("body_far"),TEXT("body_support"),TEXT("body_near")})
                {GetXBWReadyTexture(Track,I);if(bUseXBWPrimaryBodyPreview)GetXBWReadyTexture(Track,I,true);}
        }
        if(bUseArmorLayerPreview)
            for(const FString LayerClip:{TEXT("idle"),TEXT("walk"),TEXT("primary_1"),TEXT("primary_2"),TEXT("primary_3")})
                for(int32 I=0;I<6;++I)
                {
                    GetArmorLayerFrame(LayerClip,TEXT(""),TEXT("body_far"),I);
                    GetArmorLayerFrame(LayerClip,TEXT(""),TEXT("body_near"),I);
                    for(const FString Armor:{TEXT("ARM-LGT-001"),TEXT("ARM-MED-001"),TEXT("ARM-HVY-001"),TEXT("ARM-ROB-001")})
                    {
                        GetArmorLayerFrame(LayerClip,Armor,TEXT("front"),I);
                        if(LayerClip==TEXT("idle")) GetArmorLayerFrame(LayerClip,Armor,TEXT("back"),I);
                        if(bUseArmorSleevesPreview && Armor==TEXT("ARM-ROB-001") && (LayerClip==TEXT("primary_2") || LayerClip==TEXT("primary_3")))
                            GetArmorLayerFrame(LayerClip,Armor,TEXT("near"),I);
                    }
                }
        const FString ReadabilityPackage=TEXT("/Game/Production/FirstBatch/v002/Presentation/M_PlayerOcclusionReadability_v002");
        bUseReadabilityMaterial=FPackageName::DoesPackageExist(ReadabilityPackage);
        PlayerOutlineMaterial=bUseReadabilityMaterial
            ?LoadObject<UMaterialInterface>(nullptr,*(ReadabilityPackage+TEXT(".M_PlayerOcclusionReadability_v002")))
            :LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Production/FirstBatch/v001/Presentation/M_PlayerOcclusionOutline_v001.M_PlayerOcclusionOutline_v001"));
        bUseReadabilityMaterial=bUseReadabilityMaterial && PlayerOutlineMaterial!=nullptr;
        if(PlayerOutlineMaterial)
            for(int32 I=0;I<32;++I) OutlineInstances.Add(UMaterialInstanceDynamic::Create(PlayerOutlineMaterial,this));
    }
    for (const FString Family : {TEXT("SWD"),TEXT("GSW"),TEXT("SPR")})
        for (int32 Stage=1;Stage<=3;++Stage)
        {
            const FString AudioCue=FString::Printf(TEXT("%s_%s_%02d"),*Family,Family==TEXT("SPR")?TEXT("THRUST"):TEXT("WHOOSH"),Stage);
            const FString Name=TEXT("SW_AUD_")+AudioCue+TEXT("_v001");
            const FString Path=FString::Printf(TEXT("/Game/Production/FirstBatch/v001/Audio/%s.%s"),*Name,*Name);
            if(auto Sound=LoadObject<USoundBase>(nullptr,*Path))
            {PreloadedSounds.Add(Sound);ActionAudioSounds.Add(AudioCue,Sound);}
        }
    if (auto Sound=LoadObject<USoundBase>(nullptr,TEXT("/Game/ThirdParty/Kenney/ImpactSounds/ImpactLight/SW_ImpactLight.SW_ImpactLight")))
    { PreloadedSounds.Add(Sound); StoneSounds.Add(TEXT("impact"),Sound); }
    for (const FString Cue : {TEXT("AWAKE"),TEXT("ARMOR_SCRAPE"),TEXT("CHARGE_BRAKE"),TEXT("FRACTURE")})
    {
        const FString Name=FString::Printf(TEXT("SW_AUD_STONE_%s_01_v001"),*Cue);
        const FString Path=FString::Printf(TEXT("/Game/Production/FirstBatch/v001/Audio/%s.%s"),*Name,*Name);
        if(auto Sound=LoadObject<USoundBase>(nullptr,*Path)) StoneSounds.Add(Cue,Sound);
    }
    for(const FString Cue:{TEXT("XBW_RELEASE_01"),TEXT("FIRE_LAUNCH_01"),TEXT("FIRE_BURN_SHORT_01")})
    {
        const FString Name=TEXT("SW_AUD_")+Cue+TEXT("_v001");
        const FString Path=TEXT("/Game/Production/FirstBatch/v001/Audio/")+Name+TEXT(".")+Name;
        if(auto Sound=LoadObject<USoundBase>(nullptr,*Path)) WorldWeaponSounds.Add(Cue,Sound);
    }
    for(const FString Cue:{TEXT("XBW_RELOAD_DRAW_01"),TEXT("XBW_RELOAD_INSERT_01"),TEXT("XBW_RELOAD_COMPLETE_01"),
        TEXT("EQUIP_ARMOR_CLOTH_01"),TEXT("EQUIP_ARMOR_METAL_01")})
    {
        const FString Name=TEXT("SW_AUD_")+Cue+TEXT("_v002");
        const FString Path=TEXT("/Game/Production/FirstBatch/v024/AudioDedicated/")+Name+TEXT(".")+Name;
        if(auto Sound=LoadObject<USoundBase>(nullptr,*Path)) ActionAudioSounds.Add(Cue,Sound);
    }
    LoadGuardFeedbackSounds();
    LoadFairytaleGuardTrial();
    LoadFairytaleGuardFullTrial();
    LoadFairytaleGuardMoveRigTrial();
    LoadFairytaleSwordAirTrial();
    FlushRenderingCommands();
    if(FParse::Param(FCommandLine::Get(),TEXT("DungeonRunSaveProof"))
        ||FParse::Param(FCommandLine::Get(),TEXT("DungeonRunRestoreProof")))
        GetWorld()->SpawnActor<ADungeonRunContinueProbe>();
    if (FParse::Param(FCommandLine::Get(),TEXT("DungeonProof")))
        GetWorld()->SpawnActor<ADungeonProbe>();
    if(FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardRoomManualLightSource")))GetWorld()->SpawnActor<ADungeonGuardRoomFlowProbe>();
    if (FParse::Param(FCommandLine::Get(),TEXT("DungeonContentProof")))
    {
        InstallFastLosslessProofScreenshots();
        if(FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroAirDiskRestoreProofV001")))return;
        if(FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroLandingPriorityProofV001")))return;
        const bool AirProduction=FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroAirProductionProofV001"));
        const bool AirBaseline=FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroAirProofV001"));
        if(AirProduction&&AirBaseline)
        {UE_LOG(LogTemp,Error,TEXT("Production Air and unchanged baseline observers are mutually exclusive"));FPlatformMisc::RequestExitWithStatus(false,3);return;}
        if(AirProduction)GetWorld()->SpawnActor<ADungeonHeroAirProductionProbeV001>();
        else if(AirBaseline)GetWorld()->SpawnActor<ADungeonHeroAirProbeV001>();
        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardMoveProofV001")))GetWorld()->SpawnActor<ADungeonGuardMoveProbeV001>();
        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroDodgeProofV001")))GetWorld()->SpawnActor<ADungeonHeroDodgeProbeV001>();
        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardStompProofV001")))GetWorld()->SpawnActor<ADungeonGuardStompProbeV001>();
        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroDeathProofV001")))GetWorld()->SpawnActor<ADungeonHeroDeathProbeV001>();
        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroHurtProofV001")))GetWorld()->SpawnActor<ADungeonHeroHurtProbeV001>();
        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardArtDeathProofV005")))GetWorld()->SpawnActor<ADungeonGuardArtDeathProbeV005>();
        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardArtCombatProofV003")))GetWorld()->SpawnActor<ADungeonGuardArtCombatProbeV003>();
        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardArtKnown44Proof")))GetWorld()->SpawnActor<ADungeonGuardArtKnown44Probe>();
        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardArtPartialProof")))GetWorld()->SpawnActor<ADungeonGuardArtPartialProbe>();
        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardRoomFlowProof")))GetWorld()->SpawnActor<ADungeonGuardRoomFlowProbe>();
        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleWalkProof")))GetWorld()->SpawnActor<ADungeonFairytaleWalkProbe>();
        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardRunSaveProof"))||FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardRunRestoreProof")))GetWorld()->SpawnActor<ADungeonGuardRunContinueProbe>();
        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleEquipmentBoundProof")))GetWorld()->SpawnActor<ADungeonFairytaleEquipmentBoundProbe>();
        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordBodyProof")))GetWorld()->SpawnActor<ADungeonFairytaleSwordProbe>();
        else GetWorld()->SpawnActor<ADungeonContentProbe>();
    }
}

void ADungeonHUD::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if(bUseFairytaleLookdevPreview)return;
    if(auto Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr)
        if(!Game->IsRunInstallGated()){UpdateActionAudioFeedback(Game);UpdateGuardFeedback(Game);}
}

void ADungeonHUD::AttachRestoredRunPresentation(const FDungeonRunAudioContinuation& Saved,uint64 Epoch)
{
    if(!Epoch||Epoch==RestoredRunPresentationEpoch)return;
    RestoredRunPresentationEpoch=Epoch;
    StoneEffects.Reset();StoneEventCursors.Reset();StoneAudioPlayRequests.Reset();
    WorldWeaponEffects.Reset();WorldWeaponAudioRequests.Reset();WorldWeaponRun=Saved.RunGuid;
    WorldWeaponCursor=Saved.WorldHistoryThrough;
    ActionAudioRun=Saved.RunGuid;ActionAudioCursor=Saved.NextActionSequence-1;bActionAudioAttached=true;
    ActionAudioPlayRequests.Reset();ActionAudioPlayReceipts.Reset();MeleeTrails.Reset();ActorQuads.Reset();FairytaleGuardMoveRigDraws.Reset();
    FairytaleSwordAirDraw=FDungeonFairytaleSwordAirDrawV001();
    ResetFairytaleSwordSecondaryDraw();
    if(auto* Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr)
    {
        ResetGuardFeedback(Game);
        for(const auto& Seed:Saved.StoneSeeds)for(const auto F:Game->Enemies)
            if(IsValid(F)&&F->GetRuntimeEntityId()==Seed.EntityId)StoneEventCursors.Add(F,Seed.NextEventId-1);
        ExplorationOwner.Reset();BoundExplorationRun.Invalidate();BoundExplorationRoom=0;
        UpdateRoomView(Game); // Read installed authoritative bank; never Reveal or empty-grid fallback.
    }
}

void ADungeonHUD::UpdateActionAudioFeedback(ADungeonGameMode* Game)
{
    const auto& State=Game->GetActionAudioState();
    if(!State.RunGuid.IsValid()) { bActionAudioAttached=false;return; }
    if(!bActionAudioAttached || ActionAudioRun!=State.RunGuid)
    {
        ActionAudioRun=State.RunGuid;ActionAudioCursor=State.NextSequence>0?State.NextSequence-1:0;
        bActionAudioAttached=true;ActionAudioPlayRequests.Reset();ActionAudioPlayReceipts.Reset();
        return; // An attached/rebuilt HUD never replays existing journal history.
    }
    const double Now=Game->GetSimulationTime();
    for(const auto& Record:State.Records)
    {
        if(Record.Sequence<=ActionAudioCursor) continue;
        ActionAudioCursor=Record.Sequence;
        const double Age=Now-Record.AtTime;
        if(Record.RunGuid!=State.RunGuid || Record.RoomInstanceId!=Game->GetEquipmentView().RoomInstanceId
            || Age<0. || Age>.25) continue;
        const auto Sound=ActionAudioSounds.Find(Record.Cue);
        if(!Sound || !Sound->Get()) continue;
        // Candidate mix gains; actual listening remains separate from event correctness.
        const bool Melee=Record.Cue.StartsWith(TEXT("SWD_WHOOSH_"))||Record.Cue.StartsWith(TEXT("GSW_WHOOSH_"))
            ||Record.Cue.StartsWith(TEXT("SPR_THRUST_"));
        const float Volume=Melee?.25f:Record.Cue==TEXT("XBW_RELOAD_INSERT_01")?.55f:.32f;
        UGameplayStatics::PlaySound2D(this,Sound->Get(),Volume,1.f);
        ++ActionAudioPlayRequests.FindOrAdd(Record.Cue);
        FDungeonActionAudioPlayRequest Request;Request.Source=Record;
        Request.SoundPath=Sound->Get()->GetPathName();Request.RequestedAt=Now;Request.Volume=Volume;
        ActionAudioPlayReceipts.Add(MoveTemp(Request));
    }
    if(ActionAudioPlayReceipts.Num()>256)
        ActionAudioPlayReceipts.RemoveAt(0,ActionAudioPlayReceipts.Num()-256,EAllowShrinking::No);
}

FVector2D ADungeonHUD::Screen(float X,float Y) const { return Origin+FVector2D(X,Y)*UIScale; }
FVector2D ADungeonHUD::Ground(FVector2D P) const { return FVector2D(640.f+(P.X-CameraX)*.65f,490.f-P.Y*.38f); }
void ADungeonHUD::Box(float X,float Y,float W,float H,FLinearColor C)
{ const auto P=Screen(X,Y); DrawRect(C,P.X,P.Y,W*UIScale,H*UIScale); }
void ADungeonHUD::Line(float X,float Y,float X2,float Y2,FLinearColor C,float W)
{ const auto A=Screen(X,Y), B=Screen(X2,Y2); DrawLine(A.X,A.Y,B.X,B.Y,C,W*UIScale); }
void ADungeonHUD::DrawCombatRangeDebugLine(float X,float Y,float X2,float Y2,FLinearColor C,float W)
{
    if(!bCombatRangeDebug||!Canvas)return;
    Line(X,Y,X2,Y2,C,W);
    ++CombatRangeDebugLineCount;
}
void ADungeonHUD::Text(const FString& V,float X,float Y,float S,FLinearColor C)
{
    if(!bShowInterface) return;
    const auto P=Screen(X,Y);++RenderedTextDrawCalls;
    DrawText(V,C,P.X,P.Y,ChineseFont,S*UIScale);
}
void ADungeonHUD::Triangle(FVector2D A,FVector2D B,FVector2D C,FLinearColor Color)
{
    FCanvasUVTri Tri;
    Tri.V0_Pos=Screen(A.X,A.Y); Tri.V1_Pos=Screen(B.X,B.Y); Tri.V2_Pos=Screen(C.X,C.Y);
    Tri.V0_UV=Tri.V1_UV=Tri.V2_UV=FVector2D::ZeroVector;
    Tri.V0_Color=Tri.V1_Color=Tri.V2_Color=Color;
    FCanvasTriangleItem Item(Tri,GWhiteTexture); Item.BlendMode=SE_BLEND_Translucent;
    Canvas->DrawItem(Item);
}
void ADungeonHUD::Oval(float X,float Y,float W,float H,FLinearColor Color)
{
    const FVector2D C(X+W*.5f,Y+H*.5f);
    for(int I=0;I<32;++I)
    {
        float A=I*2.f*PI/32.f, B=(I+1)*2.f*PI/32.f;
        Triangle(C,C+FVector2D(FMath::Cos(A)*W*.5f,FMath::Sin(A)*H*.5f),C+FVector2D(FMath::Cos(B)*W*.5f,FMath::Sin(B)*H*.5f),Color);
    }
}

const DungeonExploration::FExploration* ADungeonHUD::CurrentExploration() const
{
    const auto Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    return Game&&Game->GetEquipmentView().Bound?Game->GetCurrentRunExplorationView():Exploration.Get();
}
void ADungeonHUD::UpdateRoomView(ADungeonGameMode* Game)
{
    auto Player=Game->GetPlayerFighter();if(!Player) return;
    const FVector2D Position=Player->GetGroundPosition();
    const float HalfView=580.f/.65f;
    const float Target=FMath::Clamp(float(Position.X),float(DungeonRoomLayout::MinX)+HalfView,float(DungeonRoomLayout::MaxX)-HalfView);
    const auto& V=Game->GetEquipmentView();
    if(V.Bound)
    {
        if(!Game->GetCurrentRunExplorationView())return; // Never replace missing Run memory with an empty HUD grid.
        if(ExplorationOwner.Get()!=Player||BoundExplorationRun!=V.RunGuid||BoundExplorationRoom!=V.RoomInstanceId
            ||ExplorationRunRestartSerial!=Game->GetRunRestartSerial())
        {
            ExplorationOwner=Player;BoundExplorationRun=V.RunGuid;BoundExplorationRoom=V.RoomInstanceId;
            ExplorationRunRestartSerial=Game->GetRunRestartSerial();++ExplorationResetSerial;CameraX=Target;
        }
        else CameraX=FMath::FInterpTo(CameraX,Target,FMath::Min(GetWorld()->GetDeltaSeconds(),.1f),5.f);
        return; // Bound Reveal is committed by GameMode; rendering only reads it.
    }
    if(!Exploration || ExplorationOwner.Get()!=Player || Exploration->RoomId()!=Game->RoomNumber
        || ExplorationRunRestartSerial!=Game->GetRunRestartSerial()||BoundExplorationRun.IsValid())
    {
        Exploration=MakeUnique<DungeonExploration::FExploration>(DungeonExploration::FBounds{
            DungeonRoomLayout::MinX,DungeonRoomLayout::MaxX,DungeonRoomLayout::MinY,DungeonRoomLayout::MaxY},Game->RoomNumber);
        ExplorationOwner=Player;ExplorationRunRestartSerial=Game->GetRunRestartSerial();
        ++ExplorationResetSerial;CameraX=Target;
        BoundExplorationRun.Invalidate();BoundExplorationRoom=0;
    }
    else CameraX=FMath::FInterpTo(CameraX,Target,FMath::Min(GetWorld()->GetDeltaSeconds(),.1f),5.f);
    Exploration->Reveal({Position.X,Position.Y});
}

double ADungeonHUD::GetCurrentVisibilityAt(FVector2D Position) const
{
    const auto Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    auto Player=Game&&Game->GetEquipmentView().Bound?Game->GetPlayerFighter():ExplorationOwner.Get();if(!Player)return 1.;
    const auto Observer=Player->GetGroundPosition();
    return DungeonExploration::FExploration::VisibilityAt({Position.X,Position.Y},{Observer.X,Observer.Y});
}

void ADungeonHUD::DrawExplorationFog(float Time)
{
    if(!CurrentExploration()) return;
    TArray<FCanvasUVTri> Triangles;
    const int32 MinCellX=FMath::FloorToInt((CameraX-640.f/.65f)/64.f);
    const int32 MaxCellX=FMath::CeilToInt((CameraX+640.f/.65f)/64.f);
    const int32 MinCellY=FMath::FloorToInt((490.f-(bShowInterface?650.f:720.f))/(.38f*64.f));
    const int32 MaxCellY=FMath::CeilToInt((490.f-(bShowInterface?112.f:0.f))/(.38f*64.f));
    const auto ColorAt=[this,Time](FVector2D Point)
    {
        // Wall haze uses the memory of its ground boundary, not a fictitious
        // walkable cell behind the back wall.
        const FVector2D Query(Point.X,FMath::Min(Point.Y,DungeonRoomLayout::MaxY));
        const double Visible=GetCurrentVisibilityAt(Query);
        const double Memory=GetExplorationMemoryAt(Query);
        const double Known=FMath::Max(Memory,Visible);
        const double Drift=FMath::Sin(Point.X*.008+Time*.28)*FMath::Sin(Point.Y*.012-Time*.18)*.025*(1.-Visible);
        float Alpha=float(FMath::Clamp((1.-Known)*.94+Known*(1.-Visible)*.32+Drift,0.,.97));
        if(Point.Y>=DungeonRoomLayout::MaxY) Alpha*=.35f;
        return FLinearColor(.007f,.012f,.020f,Alpha);
    };
    const auto Add=[this,&Triangles,&ColorAt](FVector2D A,FVector2D B,FVector2D C)
    {
        FCanvasUVTri Tri;const auto PA=Ground(A),PB=Ground(B),PC=Ground(C);
        Tri.V0_Pos=Screen(PA.X,PA.Y);Tri.V1_Pos=Screen(PB.X,PB.Y);Tri.V2_Pos=Screen(PC.X,PC.Y);
        Tri.V0_UV=Tri.V1_UV=Tri.V2_UV=FVector2D::ZeroVector;
        Tri.V0_Color=ColorAt(A);Tri.V1_Color=ColorAt(B);Tri.V2_Color=ColorAt(C);Triangles.Add(Tri);
    };
    for(int32 X=MinCellX;X<MaxCellX;++X)
        for(int32 Y=MinCellY;Y<MaxCellY;++Y)
        {
            const FVector2D A(X*64.,Y*64.),B((X+1)*64.,Y*64.),C((X+1)*64.,(Y+1)*64.),D(X*64.,(Y+1)*64.);
            Add(A,B,C);Add(A,C,D);
        }
    if(Triangles.Num()) { FCanvasTriangleItem Item(Triangles,GWhiteTexture);Item.BlendMode=SE_BLEND_Translucent;Canvas->DrawItem(Item); }
}

void ADungeonHUD::DrawRoomParallax(UTexture2D* Texture,float ScrollFactor)
{
    if(!Texture) return;
    constexpr float Zoom=1.2f;
    const auto Top=Screen((1280.f-1280.f*Zoom)*.5f-CameraX*.65f*ScrollFactor,323.f-323.f*Zoom);
    DrawTexture(Texture,Top.X,Top.Y,1280.f*Zoom*UIScale,720.f*Zoom*UIScale,0,0,1,1,FLinearColor::White);
}

void ADungeonHUD::DrawRoom(float T,bool Clear)
{
    using namespace DungeonPalette;
    RenderedScenePropPaths.Reset();bRenderedSceneSurveyVisible=false;
    const auto SceneGame=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    const auto Scene=SceneGame&&SceneGame->GetSceneRoomView().Active?&SceneGame->GetSceneRoomView():nullptr;
    const auto BackLeft=Ground({DungeonRoomLayout::MinX,DungeonRoomLayout::MaxY});
    const auto BackRight=Ground({DungeonRoomLayout::MaxX,DungeonRoomLayout::MaxY});
    const auto FrontLeft=Ground({DungeonRoomLayout::MinX,DungeonRoomLayout::MinY});
    const float Width=float(BackRight.X-BackLeft.X),FloorHeight=float(FrontLeft.Y-BackLeft.Y);
    Box(0,0,1280,720,Ink);
    DrawRoomParallax(RoomFarBackground,.10f);
    DrawRoomParallax(RoomMidBackground,.30f);
    if(!RoomFarBackground && !RoomMidBackground)
    {
    Box(BackLeft.X,118,Width,BackLeft.Y-118,Wall);
    for(int32 Row=0;Row<4;++Row)
        for(int32 Col=0;Col<30;++Col)
        {
            const float X=BackLeft.X+Col*65.f-(Row%2)*32.f,Y=122.f+Row*27.f;
            Box(X+1,Y+1,62,24,FLinearColor(.12f+((Col+Row)%3)*.008f,.17f,.195f,1));
        }
    // Anchored wall bays and pillars scroll with the room rather than framing
    // one small screen-sized arena. These are background structures.
    for(double X=-1125;X<=1125;X+=450)
    {
        const auto P=Ground({X,DungeonRoomLayout::MaxY});
        Box(P.X-58,P.Y-75,116,75,Mortar);Oval(P.X-58,P.Y-112,116,78,Mortar);
        Box(P.X-45,P.Y-70,90,70,Ink);Oval(P.X-45,P.Y-99,90,63,Ink);
        for(int32 I=0;I<4;++I) Box(P.X-32+I*21,P.Y-79,5,79,FLinearColor(.13f,.18f,.20f,1));
        Box(P.X-70,P.Y-105,20,105,FLinearColor(.17f,.22f,.23f,1));
        Box(P.X+50,P.Y-105,20,105,FLinearColor(.17f,.22f,.23f,1));
        Line(P.X-58,P.Y-30,P.X+58,P.Y-30,Wall,4);
    }
    }
    Box(BackLeft.X,BackLeft.Y,Width,FloorHeight,FLinearColor(.18f,.225f,.215f,1));
    Line(BackLeft.X,BackLeft.Y,BackRight.X,BackRight.Y,FLinearColor(.32f,.35f,.31f,1),3);
    if(RoomFloorTexture)
        for(int32 Row=0;Row<FMath::CeilToInt((DungeonRoomLayout::MaxY-DungeonRoomLayout::MinY)/256.);++Row)
            for(int32 Col=0;Col<FMath::CeilToInt((DungeonRoomLayout::MaxX-DungeonRoomLayout::MinX)/256.);++Col)
            {
                const double X=DungeonRoomLayout::MinX+Col*256.,Y=DungeonRoomLayout::MinY+Row*256.;
                if(X>=DungeonRoomLayout::MaxX || Y>=DungeonRoomLayout::MaxY) continue;
                const auto A=Ground({X,FMath::Min(Y+256.,DungeonRoomLayout::MaxY)});
                const auto B=Ground({FMath::Min(X+256.,DungeonRoomLayout::MaxX),Y});
                if(B.X<0 || A.X>1280) continue;
                const auto Top=Screen(A.X,A.Y);
                const float U=float((FMath::Min(X+256.,DungeonRoomLayout::MaxX)-X)/256.);
                const float V=float((FMath::Min(Y+256.,DungeonRoomLayout::MaxY)-Y)/256.);
                DrawTexture(RoomFloorTexture,Top.X,Top.Y,(B.X-A.X)*UIScale,(B.Y-A.Y)*UIScale,0,1.f-V,U,V,FLinearColor::White);
            }
    else
    for(int32 Row=0;Row<=11;++Row)
    {
        const double Y=DungeonRoomLayout::MinY+Row*80.;
        if(Y>DungeonRoomLayout::MaxY) break;
        const auto L=Ground({DungeonRoomLayout::MinX,Y}),R=Ground({DungeonRoomLayout::MaxX,Y});
        Line(L.X,L.Y,R.X,R.Y,FLinearColor(.13f,.175f,.17f,1),1);
        for(int32 Col=0;Col<29;++Col)
        {
            const double X=DungeonRoomLayout::MinX+Col*96.+(Row%2)*48.;
            const auto A=Ground({X,Y}),B=Ground({X,FMath::Min(Y+80.,DungeonRoomLayout::MaxY)});
            Line(A.X,A.Y,B.X,B.Y,FLinearColor(.145f,.19f,.18f,1),1);
            if((Col+Row*3)%7==0)
            {
                const auto Crack=Ground({X+28,Y+30});
                Line(Crack.X,Crack.Y,Crack.X+17,Crack.Y-2,FLinearColor(.105f,.15f,.14f,1),1);
                Line(Crack.X+9,Crack.Y-1,Crack.X+12,Crack.Y-8,FLinearColor(.105f,.15f,.14f,1),1);
            }
        }
    }
    // Flat floor inscriptions add landmarks without pretending that decorative
    // rubble is a collision object or a usable reward.
    for(const FVector2D World : {FVector2D(-1080,-230),FVector2D(-430,230),FVector2D(250,-260),FVector2D(1060,215)})
    {
        const auto P=Ground(World);const FLinearColor Rune(.28f,.43f,.40f,.35f);
        Oval(P.X-28,P.Y-12,56,24,FLinearColor(.12f,.19f,.18f,1));
        for(int32 I=0;I<8;++I)
        {
            const float A=I*PI*.25f,B=A+.28f;
            Line(P.X+FMath::Cos(A)*24,P.Y+FMath::Sin(A)*9,P.X+FMath::Cos(B)*24,P.Y+FMath::Sin(B)*9,Rune,1.4f);
        }
        Line(P.X-10,P.Y,P.X+10,P.Y,Rune,1.4f);Line(P.X,P.Y-5,P.X,P.Y+5,Rune,1.4f);
    }
    if(!RoomFarBackground && !RoomMidBackground)
    for(double X=-1200;X<=1200;X+=400)
    {
        const auto P=Ground({X,DungeonRoomLayout::MaxY});const float Y=P.Y-42;
        Oval(P.X-45,Y-70,90,130,FLinearColor(.94f,.45f,.12f,.05f));
        Box(P.X-4,Y,8,27,FLinearColor(.25f,.18f,.11f,1));Box(P.X-10,Y,20,5,Gold);
        const float Flame=FMath::Sin(T*6+X)*2;
        Triangle({P.X-8,Y},{P.X+8,Y},{P.X+Flame,Y-28},FLinearColor(1,.48f,.15f,1));
        Triangle({P.X-4,Y},{P.X+4,Y},{P.X-Flame*.4f,Y-18},FLinearColor(1,.87f,.39f,1));
    }
    if(!RoomFarBackground && !RoomMidBackground)
    for(double X : {DungeonRoomLayout::MinX,DungeonRoomLayout::MaxX})
    {
        const auto P=Ground({X,0});
        Box(P.X-13,128,26,FrontLeft.Y-128,FLinearColor(.12f,.17f,.19f,1));
        for(int32 I=0;I<10;++I) Line(P.X-13,145+I*50,P.X+13,145+I*50,Mortar,2);
    }
    if(Scene)
    {
        // This low masonry reads the very box that gameplay instantiates.
        // Fog is drawn later, so unexplored masonry and signs remain covered.
        const auto L=Ground(Scene->Layout.Barrier.Min);
        const auto R=Ground(Scene->Layout.Barrier.Max);
        const float W=R.X-L.X,H=L.Y-R.Y;
        auto WallTexture=GetScenePropTexture(true);
        if(WallTexture&&WallTexture->GetResource())
        {
            // The native wall's hidden rear contact is unverified. Keep the
            // actual shared footprint visible as a stone foundation; only its
            // facade/top overlay uses the frozen uniform source transform.
            Box(L.X,R.Y,W,H,FLinearColor(.16f,.22f,.20f,1));
            if(RoomFloorTexture&&RoomFloorTexture->GetResource())
            {
                const auto Foundation=Screen(L.X,R.Y);
                DrawTexture(RoomFloorTexture,Foundation.X,Foundation.Y,W*UIScale,H*UIScale,
                    0,0,1,1,FLinearColor(.70f,.77f,.65f,1));
            }
            Line(L.X,R.Y,R.X,R.Y,FLinearColor(.31f,.39f,.31f,1),2);
            constexpr double Scale=0.5439330543933054;
            const auto Anchor=Ground({Scene->Layout.Barrier.GetCenter().X,Scene->Layout.Barrier.Min.Y});
            const auto Top=Screen(Anchor.X-256.*Scale,Anchor.Y-408.*Scale);
            DrawTexture(WallTexture,Top.X,Top.Y,512.*Scale*UIScale,512.*Scale*UIScale,0,0,1,1,FLinearColor::White);
            RenderedScenePropPaths.Add(WallTexture->GetPathName());
        }
        else
        {
        Box(L.X-5,L.Y-5,W+10,13,FLinearColor(.015f,.025f,.025f,.38f));
        Box(L.X,R.Y-24,W,H+24,FLinearColor(.14f,.19f,.19f,1));
        Box(L.X,R.Y-24,W,H,FLinearColor(.27f,.32f,.29f,1));
        Line(L.X,R.Y-24,R.X,R.Y-24,FLinearColor(.43f,.47f,.39f,1),2);
        for(int32 I=1;I<8;++I)
        {
            const float X=L.X+W*I/8.f;
            Line(X,R.Y-24,X,L.Y,Wall,2);
            if(I%3==0) Line(X+8,R.Y-8,X+18,R.Y-14,Mortar,1.4f);
        }
        Line(L.X,L.Y-12,R.X,L.Y-12,Mortar,2);
        }
        for(const auto& Object:Scene->Objects) if(Object.Kind==EDungeonSceneObjectKind::Survey)
        {
            const double Visible=GetCurrentVisibilityAt(Object.Position);
            const double Remembered=GetExplorationMemoryAt(Object.Position);
            // Tall signs extend above the floor fog mesh. Admit the whole prop
            // and its label explicitly; revealing never commits investigation.
            if(Visible<=0. && Remembered<=0.) continue;
            bRenderedSceneSurveyVisible=true;
            const float ReadAlpha=float(FMath::Clamp(FMath::Max(Visible,.4*Remembered),0.,1.));
            const auto Fade=[ReadAlpha](FLinearColor C){C.A*=ReadAlpha;return C;};
            const auto P=Ground(Object.Position);
            auto SteleTexture=GetScenePropTexture(false);
            if(SteleTexture&&SteleTexture->GetResource())
            {
                constexpr double Scale=.18;
                const auto Top=Screen(P.X-256.*Scale,P.Y-431.*Scale);
                DrawTexture(SteleTexture,Top.X,Top.Y,512.*Scale*UIScale,512.*Scale*UIScale,
                    0,0,1,1,FLinearColor(1,1,1,ReadAlpha));
                RenderedScenePropPaths.Add(SteleTexture->GetPathName());
            }
            else
            {
            Oval(P.X-23,P.Y-5,46,12,Fade(FLinearColor(0,0,0,.26f)));
            Box(P.X-3,P.Y-38,6,37,Fade(FLinearColor(.24f,.20f,.14f,1)));
            Box(P.X-21,P.Y-58,42,30,Fade(FLinearColor(.16f,.20f,.20f,1)));
            Line(P.X-19,P.Y-55,P.X+19,P.Y-55,Fade(FLinearColor(.49f,.52f,.40f,1)),2);
            for(int32 I=0;I<3;++I) Line(P.X-11,P.Y-48+I*6,P.X+11-I*4,P.Y-48+I*6,Fade(Muted),1.5f);
            }
            const auto Player=SceneGame->GetPlayerFighter();
            const auto Delta=Player?Player->GetGroundPosition()-Object.Position:FVector2D(1000,1000);
            const bool Close=FMath::Abs(Delta.X)<=80.&&FMath::Abs(Delta.Y)<=40.;
            const auto Label=Object.Surveyed?TEXT("已调查"):Close?TEXT("E · 调查碎碑"):TEXT("旧城碎碑");
            auto LabelColor=Object.Surveyed?Muted:Gold;LabelColor.A=ReadAlpha;
            Text(Label,P.X-34,P.Y-(Close?140.f:81.f),.43f,LabelColor);
        }
    }
    const auto Exit=Ground(Scene?Scene->Layout.Exit:FVector2D(665.,0.));
    Oval(Exit.X-30,Exit.Y-21,60,42,Clear?FLinearColor(.2f,.75f,.54f,.2f):FLinearColor(.08f,.13f,.13f,.35f));
    for(int32 I=0;I<3;++I)
    {
        Line(Exit.X-15+I*12,Exit.Y-8,Exit.X-8+I*12,Exit.Y,Clear?FLinearColor(.5f,1,.77f,1):Muted,2);
        Line(Exit.X-8+I*12,Exit.Y,Exit.X-15+I*12,Exit.Y+8,Clear?FLinearColor(.5f,1,.77f,1):Muted,2);
    }
    Text(Clear?TEXT("出口 · E"):TEXT("封印"),Exit.X-22,Exit.Y-43,.48f,Clear?FLinearColor(.5f,1,.77f,1):Muted);
    if(bShowInterface) {Box(0,650,1280,70,Ink);Line(65,652,1215,652,FLinearColor(.36f,.33f,.23f,1),2);}
}

UTexture2D* ADungeonHUD::GetFrame(bool Enemy,const FString& Clip,int32 Frame)
{
    const FString CharacterKey=Enemy?TEXT("orc"):TEXT("human");
    const FString Name=FString::Printf(TEXT("T_%s_%s_%03d"),*CharacterKey,*Clip,Frame);
    if(const auto Found=Frames.Find(Name)) return Found->Get();
    const FString Path=FString::Printf(TEXT("/Game/Prototype/FirstRoom/Sprites/%s/%s.%s"),Enemy?TEXT("Orc"):TEXT("Human"),*Name,*Name);
    UTexture2D* Result=LoadObject<UTexture2D>(nullptr,*Path);
    Frames.Add(Name,Result);
    return Result;
}

UTexture2D* ADungeonHUD::GetCandidateFrame(const FString& Actor,const FString& Clip,int32 Frame)
{
    // Frozen walk v007 completes the candidate identity; other hero clips keep
    // their v006 imports, stone clips their v002 imports.
    const FString Version = Actor == TEXT("hero")
        ? Clip == TEXT("walk") ? TEXT("v007") : TEXT("v006") : TEXT("v002");
    const FString Name = FString::Printf(TEXT("T_%s_%s_%03d_%s"),*Actor,*Clip,Frame,*Version);
    if (const auto Found=Frames.Find(Name)) return Found->Get();
    const FString Path = FString::Printf(TEXT("/Game/Production/FirstBatch/%s/CandidateSprites/%s/%s.%s"),
        *Version,Actor == TEXT("hero") ? TEXT("Hero") : TEXT("Stone"),*Name,*Name);
    auto Result=LoadObject<UTexture2D>(nullptr,*Path); Frames.Add(Name,Result); return Result;
}

UTexture2D* ADungeonHUD::GetCandidateSword()
{
    const FString Name=TEXT("T_military_sword_v002");
    if (const auto Found=Frames.Find(Name)) return Found->Get();
    auto Texture=LoadObject<UTexture2D>(nullptr,TEXT("/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002"));
    Frames.Add(Name,Texture); return Texture;
}

UTexture2D* ADungeonHUD::GetArmorLayerFrame(const FString& Clip,const FString& Armor,const FString& Layer,int32 Index)
{
    if(Clip!=TEXT("idle") && Clip!=TEXT("walk") && Clip!=TEXT("primary_1")
        && Clip!=TEXT("primary_2") && Clip!=TEXT("primary_3")) return nullptr;
    // Frozen native 512px layers: idle manifest f0cd3c72..., P1 6369db09... .
    // P1 has no visible back garment; null is an authored visibility decision.
    if(Clip!=TEXT("idle") && Layer==TEXT("back")) return nullptr;
    FString Identity=Armor;Identity.ReplaceInline(TEXT("-"),TEXT("_"));
    const bool Idle=Clip==TEXT("idle");
    const bool Walk=Clip==TEXT("walk");
    const bool P1=Clip==TEXT("primary_1"),P2=Clip==TEXT("primary_2");
    const bool Sleeves=bUseArmorSleevesPreview && (Clip==TEXT("primary_2") || Clip==TEXT("primary_3"));
    if(Layer==TEXT("near") && (!Sleeves || Armor!=TEXT("ARM-ROB-001"))) return nullptr;
    const TCHAR* Prefix=Idle?TEXT("ArmorIdle"):Walk?TEXT("ArmorWalk"):P1?TEXT("ArmorP1"):P2?(Sleeves?TEXT("ArmorP2Sleeves"):TEXT("ArmorP2")):(Sleeves?TEXT("ArmorP3Sleeves"):TEXT("ArmorP3"));
    const TCHAR* Version=P1||Sleeves?TEXT("v002"):TEXT("v001");
    const FString Name=FString::Printf(TEXT("T_%s_%s%s%s_%03d_%s"),Prefix,
        *Identity,Identity.IsEmpty()?TEXT(""):TEXT("_"),*Layer,Index,Version);
    if(const auto Found=Frames.Find(Name)) return Found->Get();
    const TCHAR* Directory=Idle?TEXT("/Game/Production/FirstBatch/v008/ArmorIdle/")
        :Walk?TEXT("/Game/Production/FirstBatch/v010/ArmorWalk/")
        :P1?TEXT("/Game/Production/FirstBatch/v009/ArmorPrimary1/")
        :P2?(Sleeves?TEXT("/Game/Production/FirstBatch/v013/ArmorPrimary2Sleeves/"):TEXT("/Game/Production/FirstBatch/v011/ArmorPrimary2/"))
        :(Sleeves?TEXT("/Game/Production/FirstBatch/v014/ArmorPrimary3Sleeves/"):TEXT("/Game/Production/FirstBatch/v012/ArmorPrimary3/"));
    const FString Package=FString(Directory)+Name;
    UTexture2D* Result=FPackageName::DoesPackageExist(Package)?LoadObject<UTexture2D>(nullptr,*(Package+TEXT(".")+Name)):nullptr;
    Frames.Add(Name,Result);return Result;
}

int32 ADungeonHUD::GetQueuedPlayerMeleeTrailCount() const
{
    int32 Count=0;
    for(const auto& Trail:MeleeTrails) if(auto TrailFighter=Trail.Owner.Get()) if(!TrailFighter->bEnemy) ++Count;
    return Count;
}

UTexture2D* ADungeonHUD::GetScenePropTexture(bool Wall)
{
    const FString Name=Wall?TEXT("T_scene_moss_low_wall_v001"):TEXT("T_scene_old_city_stele_v001");
    if(const auto Found=Frames.Find(Name))return Found->Get();
    const FString Package=TEXT("/Game/Production/SceneExploration/v001/")+Name;
    auto Result=FPackageName::DoesPackageExist(Package)?LoadObject<UTexture2D>(nullptr,*(Package+TEXT(".")+Name)):nullptr;
    Frames.Add(Name,Result);return Result;
}

UTexture2D* ADungeonHUD::GetXBWReadyTexture(const FString& Track,int32 Index,bool Primary)
{
    const bool Weapon=Track==TEXT("weapon");
    const FString Name=Weapon?TEXT("T_WPN_XBW_001_neutral_v001")
        :Primary?FString::Printf(TEXT("T_XBWPrimary_%s_%03d_v001"),*Track,Index)
        :FString::Printf(TEXT("T_XBWReadyIdle_%s_%03d_v001"),*Track,Index);
    if(const auto Found=Frames.Find(Name)) return Found->Get();
    const FString Package=FString(Weapon?TEXT("/Game/Production/FirstBatch/v015/WeaponComponents/")
        :Primary?TEXT("/Game/Production/FirstBatch/v017/XBWPrimary/"):TEXT("/Game/Production/FirstBatch/v016/XBWReadyIdle/"))+Name;
    auto Result=FPackageName::DoesPackageExist(Package)?LoadObject<UTexture2D>(nullptr,*(Package+TEXT(".")+Name)):nullptr;
    Frames.Add(Name,Result);return Result;
}

UTexture2D* ADungeonHUD::GetXBWReloadTexture(const FString& Track,int32 Index)
{
    const FString Name=FString::Printf(TEXT("T_XBWReload_%s_%03d_v001"),*Track,Index);
    if(const auto Found=Frames.Find(Name))return Found->Get();
    const FString Package=TEXT("/Game/Production/FirstBatch/v018/XBWReload/")+Name;
    auto Result=FPackageName::DoesPackageExist(Package)?LoadObject<UTexture2D>(nullptr,*(Package+TEXT(".")+Name)):nullptr;
    Frames.Add(Name,Result);return Result;
}

UTexture2D* ADungeonHUD::GetXBWArmorTexture(const FString& Clip,const FString& Armor,const FString& Track,int32 Index)
{
    FString Token=Armor;Token.ReplaceInline(TEXT("-"),TEXT("_"));
    const FString Family=Clip==TEXT("primary")?TEXT("Primary"):Clip==TEXT("reload")?TEXT("Reload"):TEXT("Ready");
    const FString Name=FString::Printf(TEXT("T_XBWArmor%s_%s_%s_%03d_v001"),*Family,*Token,*Track,Index);
    if(const auto Found=Frames.Find(Name))return Found->Get();
    const FString Prefix=Clip==TEXT("primary")?TEXT("/Game/Production/FirstBatch/v019/XBWArmorPrimary/")
        :Clip==TEXT("reload")?TEXT("/Game/Production/FirstBatch/v020/XBWArmorReload/"):TEXT("/Game/Production/FirstBatch/v021/XBWArmorReady/");
    const FString Package=Prefix+Name;
    auto Result=FPackageName::DoesPackageExist(Package)?LoadObject<UTexture2D>(nullptr,*(Package+TEXT(".")+Name)):nullptr;
    Frames.Add(Name,Result);return Result;
}

bool ADungeonHUD::DrawXBWReadyWeapon(ADungeonFighter* F,float Size,FLinearColor Tint,bool Primary)
{
    if(bUseXBWReloadBodyPreview)
    {
        // Actor owns both the selected image state and its rigid matrix. HUD
        // never updates the component or guesses an emitter from screen pixels.
        const auto Pose=F->GetWeaponPoseSocket();
        if(!Pose.Supported)return false;
        auto Texture=Pose.WeaponStateIndex<0?GetXBWReadyTexture(TEXT("weapon")):GetXBWReloadTexture(TEXT("weapon"),Pose.WeaponStateIndex);
        if(!Texture||!Texture->GetResource())return false;
        const auto GroundPoint=Ground(F->GetGroundPosition());
        const auto Project=[this,F,Size,GroundPoint](FVector2D Pixel)
        {return Screen(GroundPoint.X+F->Facing*(Pixel.X-256.)*Size/512.,GroundPoint.Y-F->JumpHeight*.70+(Pixel.Y-472.)*Size/512.);};
        const bool Reload=Pose.Clip==DungeonWeaponPoseSocket::EClip::Reload;
        const FVector2D ComponentAnchor=Reload?FVector2D(Pose.ComponentSupportX,Pose.ComponentSupportY):FVector2D(Pose.ComponentGripX,Pose.ComponentGripY);
        const FVector2D BodyAnchor=Reload?FVector2D(Pose.SupportX,Pose.SupportY):FVector2D(Pose.GripX,Pose.GripY);
        const FVector2D Hand=Project(BodyAnchor);
        const float Width=float(Size*Pose.Scale)*UIScale;
        const FVector2D Pivot(F->Facing<0?1.-ComponentAnchor.X/512.:ComponentAnchor.X/512.,ComponentAnchor.Y/512.);
        const FVector2D Top=Hand-Pivot*Width;
        const float Angle=float(Pose.Angle)*(F->Facing<0?-1.f:1.f);
        DrawTexture(Texture,Top.X,Top.Y,Width,Width,F->Facing<0?1.f:0.f,0.f,F->Facing<0?-1.f:1.f,1.f,
            Tint,BLEND_Translucent,1.f,false,Angle,Pivot);
        FActorQuad Quad;Quad.Owner=F;Quad.Texture=Texture;Quad.Top=Top;Quad.Size=Width;Quad.Rotation=Angle;
        Quad.Pivot=Pivot;Quad.Tint=Tint;Quad.Weapon=true;ActorQuads.Add(Quad);
        RenderedWeaponBodyEmitScreen=Project({Pose.EmitX,Pose.EmitY});
        RenderedPlayerDrawStack.Add(Texture->GetPathName());return true;
    }
    auto Weapon=GetXBWReadyTexture(TEXT("weapon"));
    if(!Weapon || !Weapon->GetResource()) return false;
    const auto GroundPoint=Ground(F->GetGroundPosition());
    const auto Project=[this,F,Size,GroundPoint](FVector2D Pixel)
    {return Screen(GroundPoint.X+F->Facing*(Pixel.X-256.f)*Size/512.f,
        GroundPoint.Y-F->JumpHeight*.70f+(Pixel.Y-472.f)*Size/512.f);};
    DungeonXBWBodyPose::FPose Pose;
    if(Primary && !DungeonXBWBodyPose::Primary(F->GetWeaponActionsState(),Pose)) return false;
    const double GripX=Primary?Pose.GripX:224.,GripY=Primary?Pose.GripY:316.;
    const double SourceAngle=Primary?Pose.Angle:-5.;
    const auto Hand=Project({GripX,GripY});
    const float Width=Size*.48f*UIScale;
    const FVector2D Pivot(F->Facing<0?1.f-128.f/512.f:128.f/512.f,253.f/512.f);
    const FVector2D Top=Hand-Pivot*Width;
    const float Angle=float(SourceAngle)*(F->Facing<0?-1.f:1.f);
    DrawTexture(Weapon,Top.X,Top.Y,Width,Width,F->Facing<0?1.f:0.f,0.f,F->Facing<0?-1.f:1.f,1.f,
        Tint,BLEND_Translucent,1.f,false,Angle,Pivot);
    FActorQuad Quad;Quad.Owner=F;Quad.Texture=Weapon;Quad.Top=Top;Quad.Size=Width;Quad.Rotation=Angle;
    Quad.Pivot=Pivot;Quad.Tint=Tint;Quad.Weapon=true;ActorQuads.Add(Quad);
    // This is a presentation observation, never an Actor/projectile authority write.
    const double Radians=FMath::DegreesToRadians(SourceAngle),DX=489.-128.,DY=224.-253.;
    const FVector2D Emit(GripX+.48*(DX*FMath::Cos(Radians)-DY*FMath::Sin(Radians)),
        GripY+.48*(DX*FMath::Sin(Radians)+DY*FMath::Cos(Radians)));
    RenderedWeaponBodyEmitScreen=Project(Emit);
    RenderedPlayerDrawStack.Add(Weapon->GetPathName());return true;
}

bool ADungeonHUD::DrawCandidateSword(ADungeonFighter* F,UTexture2D* Body,const FString& Clip,int32 Index,float Size,FLinearColor Tint,bool ReplayHandPolygon)
{
    if(F->WeaponId!=TEXT("sword") && F->WeaponId!=TEXT("WPN-SWD-001")) return false;
    const auto Marker=DungeonCandidateAssembly::Find(Clip,Index);
    auto Sword=GetCandidateSword();
    if (!Marker || !Marker->WeaponVisible || !Sword || !Sword->GetResource() || !Body || !Body->GetResource()) return false;
    const auto GroundPoint=Ground(F->GetGroundPosition());
    const auto Project=[this,F,Size,GroundPoint,Marker](FVector2D Pixel)
    {
        return Screen(GroundPoint.X+F->Facing*(Pixel.X-Marker->Root.X)*Size/512.f,
            GroundPoint.Y-F->JumpHeight*.70f+(Pixel.Y-Marker->Root.Y)*Size/512.f);
    };
    const auto Hand=Project(Marker->Grip);
    const float Width=Size*DungeonCandidateAssemblyTuning::WeaponScale*UIScale;
    const float Angle=DungeonCandidateAssemblyTuning::Angle(Clip,Index,Marker->Angle);
    const float PivotX=F->Facing<0 ? 1.f-DungeonCandidateAssembly::WeaponGrip.X/512.f
        : DungeonCandidateAssembly::WeaponGrip.X/512.f;
    // The negative U width is the single mirror. Its baseline blade points left,
    // so -rightAngle produces a final left blade angle of 180-rightAngle.
    DrawTexture(Sword,Hand.X-PivotX*Width,Hand.Y-Width*.5f,Width,Width,
        F->Facing<0?1.f:0.f,0.f,F->Facing<0?-1.f:1.f,1.f,Tint,BLEND_Translucent,1.f,false,
        Angle*(F->Facing<0?-1.f:1.f),FVector2D(PivotX,.5f));
    FActorQuad WeaponQuad;WeaponQuad.Owner=F;WeaponQuad.Texture=Sword;
    WeaponQuad.Top=FVector2D(Hand.X-PivotX*Width,Hand.Y-Width*.5f);WeaponQuad.Size=Width;
    WeaponQuad.Rotation=Angle*(F->Facing<0?-1.f:1.f);WeaponQuad.Pivot=FVector2D(PivotX,.5f);
    WeaponQuad.Tint=Tint;WeaponQuad.Weapon=true;ActorQuads.Add(WeaponQuad);
    // Select actual original hand pixels; this approximate authored polygon is a
    // candidate occlusion region, not a fabricated interchangeable armor layer.
    const auto& Polygon=Marker->HandPolygon;
    for (int32 I=1;ReplayHandPolygon && I+1<Polygon.Num();++I)
    {
        FCanvasUVTri Tri;
        Tri.V0_Pos=Project(Polygon[0]); Tri.V1_Pos=Project(Polygon[I]); Tri.V2_Pos=Project(Polygon[I+1]);
        Tri.V0_UV=Polygon[0]/512.f; Tri.V1_UV=Polygon[I]/512.f; Tri.V2_UV=Polygon[I+1]/512.f;
        Tri.V0_Color=Tri.V1_Color=Tri.V2_Color=Tint;
        FCanvasTriangleItem Item(Tri,Body->GetResource()); Item.BlendMode=SE_BLEND_Translucent; Canvas->DrawItem(Item);
    }
    return true;
}

void ADungeonHUD::UpdateStoneFeedback(ADungeonGameMode* Game)
{
    if(!Game||Game->IsRunInstallGated())return;
    using DungeonStoneKnight::EEventKind;
    const double Now=GetWorld()->GetTimeSeconds();
    StoneEffects.RemoveAll([Now](const FStoneEffect& Fx){return !Fx.Owner.IsValid() || Now-Fx.Started>.9;});
    for(auto It=StoneEventCursors.CreateIterator();It;++It) if(!It.Key().IsValid()) It.RemoveCurrent();
    for(auto FighterPtr:Game->Enemies)
    {
        ADungeonFighter* Fighter=FighterPtr.Get();
        if(!IsValid(Fighter) || !Fighter->GetStoneKnightDriver()) continue;
        auto& Cursor=StoneEventCursors.FindOrAdd(TWeakObjectPtr<ADungeonFighter>(Fighter));
        const auto& Journal=Fighter->GetStoneFeedback();
        for(const auto& Record:Journal.Entries())
        {
            const auto& E=Record.Event;
            if(E.EventId<=Cursor) continue;
            const double Age=FMath::Max(0.0,Game->GetSimulationTime()-E.AtTime);
            if(Age<=.9)
            {
                FStoneEffect Fx;Fx.Owner=Fighter;Fx.Record=Record;Fx.Started=Now-Age;
                StoneEffects.Add(MoveTemp(Fx));
            }
            FString Cue;float Volume=.2f,Pitch=1.f;
            switch(E.Kind)
            {
            case EEventKind::WakeStarted: Cue=TEXT("AWAKE");Volume=.23f;Pitch=.95f;break;
            case EEventKind::ChargeStarted: Cue=TEXT("ARMOR_SCRAPE");Volume=.18f;break;
            case EEventKind::ChargeStopped: Cue=TEXT("CHARGE_BRAKE");Volume=.20f;break;
            case EEventKind::ActiveWindow: Cue=TEXT("ARMOR_SCRAPE");Volume=.18f;Pitch=.82f;break;
            case EEventKind::Damaged: Cue=TEXT("impact");Volume=.18f;Pitch=.75f;break;
            case EEventKind::PoiseBroken: Cue=TEXT("FRACTURE");Volume=.12f;Pitch=1.18f;break;
            case EEventKind::Died: Cue=TEXT("FRACTURE");Volume=.25f;Pitch=.9f;break;
            default: break;
            }
            // A new HUD/late frame must not play a backlog of old combat sounds.
            if(Age<=.25 && !Cue.IsEmpty())
                if(auto Sound=StoneSounds.Find(Cue))
                { UGameplayStatics::PlaySound2D(this,Sound->Get(),Volume,Pitch); ++StoneAudioPlayRequests.FindOrAdd(Cue); }
        }
        Cursor=Journal.LastEventId();
    }
    // One HUD has a bounded transient output, independent of saved simulation.
    if(StoneEffects.Num()>128) StoneEffects.RemoveAt(0,StoneEffects.Num()-128,EAllowShrinking::No);
}

void ADungeonHUD::DrawStoneTelegraph(ADungeonFighter* F)
{
    if(!F || !F->GetStoneKnightDriver() || F->bDead) return;
    using namespace DungeonStoneKnight;
    const auto& S=F->GetStoneKnightDriver()->State();
    const auto P=Ground(F->GetGroundPosition());
    if(S.Phase==EPhase::Waking)
    {
        const float Progress=float(FMath::Clamp((S.Time-S.WakeStartedAt)/.85,0.0,1.0));
        for(int32 Ring=0;Ring<2;++Ring)
        {
            const float R=33.f+Progress*30.f+Ring*8.f;
            const FLinearColor C(.97f,.61f,.21f,(1.f-Progress)*.55f);
            for(int32 I=0;I<28;++I)
            {
                const float A=I*2.f*PI/28.f,B=(I+1)*2.f*PI/28.f;
                Line(P.X+FMath::Cos(A)*R,P.Y+FMath::Sin(A)*R*.32f,
                    P.X+FMath::Cos(B)*R,P.Y+FMath::Sin(B)*R*.32f,C,2.f);
            }
        }
        return;
    }
    const auto& A=S.Action;
    if(S.Phase==EPhase::Windup)
    {
        const float Progress=float(FMath::Clamp((S.Time-A.Start)/(A.ActiveAt-A.Start),0.0,1.0));
        const FLinearColor C=A.Locked?FLinearColor(1.f,.35f,.12f,.25f+Progress*.25f):FLinearColor(1.f,.65f,.2f,.18f);
        if(A.Kind==EAttack::Charge && A.Locked)
        {
            const FVector2D Start(A.Origin.X,A.Origin.Y),Direction(A.Direction.X,A.Direction.Y);
            const FVector2D Side(-Direction.Y,Direction.X),End=Start+Direction*496.f;
            const auto L0=Ground(Start+Side*24.f),R0=Ground(Start-Side*24.f);
            const auto L1=Ground(End+Side*24.f),R1=Ground(End-Side*24.f);
            Triangle(L0,R0,R1,C);Triangle(L0,R1,L1,C);
            Line(L0.X,L0.Y,L1.X,L1.Y,FLinearColor(1,.62f,.21f,.65f),1.5f);
            Line(R0.X,R0.Y,R1.X,R1.Y,FLinearColor(1,.62f,.21f,.65f),1.5f);
            for(int32 I=1;I<=5;++I)
            {
                const FVector2D Center=Start+Direction*(float(I)*75.f);
                const auto Tip=Ground(Center+Direction*17.f),Left=Ground(Center-Direction*10.f+Side*13.f),Right=Ground(Center-Direction*10.f-Side*13.f);
                Line(Left.X,Left.Y,Tip.X,Tip.Y,FLinearColor(1,.72f,.3f,.7f),2.f);
                Line(Right.X,Right.Y,Tip.X,Tip.Y,FLinearColor(1,.72f,.3f,.7f),2.f);
            }
        }
        else if(A.Kind==EAttack::Shield)
        {
            const float Side=A.Direction.X<0?-1.f:1.f;
            for(int32 I=0;I<18;++I)
            {
                const float Alpha=-PI*.5f+I*PI/18.f,Beta=Alpha+PI/18.f;
                const auto L=Ground(F->GetGroundPosition()+FVector2D(Side*FMath::Cos(Alpha)*90.f,FMath::Sin(Alpha)*32.f));
                const auto R=Ground(F->GetGroundPosition()+FVector2D(Side*FMath::Cos(Beta)*90.f,FMath::Sin(Beta)*32.f));
                Triangle(P,L,R,C);Line(L.X,L.Y,R.X,R.Y,FLinearColor(1,.68f,.22f,.7f),2.f);
            }
        }
        else Oval(P.X-35,P.Y-11,70,22,C);
    }
    if(S.Phase==EPhase::Active && A.Kind==EAttack::Charge)
    {
        const FVector2D Direction(A.Direction.X,A.Direction.Y),Side(-Direction.Y,Direction.X);
        for(int32 I=0;I<8;++I)
        {
            const float Age=FMath::Frac(float(S.Time)*3.f+I*.127f);
            const auto Dust=Ground(F->GetGroundPosition()-Direction*(12.f+Age*115.f)+Side*(FMath::Sin(I*2.4f)*14.f));
            const float Radius=5.f+Age*12.f;
            Oval(Dust.X-Radius,Dust.Y-Radius*.35f-Age*6.f,Radius*2,Radius*.7f,FLinearColor(.73f,.67f,.48f,(1-Age)*.3f));
        }
    }
}

void ADungeonHUD::DrawStoneEffects(ADungeonFighter* F)
{
    using DungeonStoneKnight::EEventKind;
    const double Now=GetWorld()->GetTimeSeconds();
    for(const auto& Fx:StoneEffects)
    {
        if(Fx.Owner.Get()!=F) continue;
        const auto Kind=Fx.Record.Event.Kind;
        const bool Death=Kind==EEventKind::Died,Brake=Kind==EEventKind::ChargeStopped;
        const bool Hurt=Kind==EEventKind::Damaged,Break=Kind==EEventKind::PoiseBroken;
        if(!Death && !Brake && !Hurt && !Break) continue;
        const float Life=Death?.75f:Brake?.34f:Break?.4f:.24f;
        const float Age=float(Now-Fx.Started);if(Age<0 || Age>Life) continue;
        const float Fade=1.f-Age/Life;
        const auto OriginPoint=Ground({Fx.Record.Position.X,Fx.Record.Position.Y});
        const auto Center=OriginPoint+FVector2D(Brake?0.f:F->Facing*25.f,Brake?-3.f:-90.f);
        const int32 Count=Death?16:Brake?12:7;
        for(int32 I=0;I<Count;++I)
        {
            const float Angle=I*2.39996f+float(Fx.Record.Event.EventId%17)*.3f;
            const float Speed=(Death?85.f:Brake?65.f:95.f)+float(I%4)*17.f;
            const FVector2D Velocity(FMath::Cos(Angle)*Speed,FMath::Sin(Angle)*(Brake?25.f:Speed)-35.f);
            const auto Pos=Center+Velocity*Age+FVector2D(0,Age*Age*(Death?155.f:70.f));
            const float Size=(Death?5.f:Brake?6.f:2.5f)*Fade+1.f;
            const FLinearColor C=Hurt?FLinearColor(1.f,.83f,.4f,Fade):FLinearColor(.75f,.72f,.6f,Fade*.75f);
            if(Brake) Oval(Pos.X-Size,Pos.Y-Size*.4f,Size*2,Size*.8f,C);
            else Triangle(Pos+FVector2D(-Size,-Size*.3f),Pos+FVector2D(Size,0),Pos+FVector2D(0,Size),C);
        }
    }
}

void ADungeonHUD::DrawMeleeTrail(ADungeonFighter* F,const FString& Clip,int32 Index,float Size,bool CandidateWeapon)
{
    const auto GroundPoint=Ground(F->GetGroundPosition());
    FVector2D Center=GroundPoint+FVector2D(F->Facing*14.f,-70.f-F->JumpHeight*.7f);
    float Angle=-.25f,Radius=76.f;
    if(CandidateWeapon)
        if(const auto Marker=DungeonCandidateAssembly::Find(Clip,Index))
        {
            Center=GroundPoint+FVector2D(F->Facing*(Marker->Grip.X-Marker->Root.X)*Size/512.f,
                (Marker->Grip.Y-Marker->Root.Y)*Size/512.f-F->JumpHeight*.7f);
            Angle=FMath::DegreesToRadians(DungeonCandidateAssemblyTuning::Angle(Clip,Index,Marker->Angle));
            Radius=(482.f-99.f)*DungeonCandidateAssemblyTuning::WeaponScale*Size/512.f;
        }
    if(F->WeaponId==TEXT("WPN-SPR-001"))
    {
        for(int32 I=0;I<3;++I)
            Line(Center.X+F->Facing*(35.f+I*10.f),Center.Y+(I-1)*3.f,
                Center.X+F->Facing*(110.f-I*8.f),Center.Y+(I-1)*2.f,FLinearColor(.83f,.94f,1.f,.75f-I*.18f),I==1?3.f:1.f);
        return;
    }
    const bool Heavy=F->WeaponId==TEXT("WPN-GSW-001") || F->WeaponId==TEXT("axe");
    if(Heavy) Radius=100.f;
    const float Span=Heavy?1.5f:.9f,Thickness=Heavy?12.f:4.f;
    for(int32 I=0;I<12;++I)
    {
        const float T=float(I)/12.f,U=float(I+1)/12.f;
        const float A=Angle-Span*(1-T),B=Angle-Span*(1-U);
        const FVector2D VA(F->Facing*FMath::Cos(A),FMath::Sin(A)),VB(F->Facing*FMath::Cos(B),FMath::Sin(B));
        const float Width=Thickness*FMath::Sin((T+.05f)*PI);
        const auto O0=Center+VA*Radius,O1=Center+VB*Radius;
        const auto I0=Center+VA*(Radius-Width),I1=Center+VB*(Radius-Width);
        const FLinearColor C=Heavy?FLinearColor(1.f,.69f,.3f,.65f*T):FLinearColor(.83f,.94f,1.f,.65f*T);
        Triangle(I0,O0,O1,C);Triangle(I0,O1,I1,C);
    }
}

void ADungeonHUD::DrawFighter(ADungeonFighter* F)
{
    if(bUseFairytaleSwordBodyPreview&&!F->bEnemy&&DrawFairytaleSwordBody(F))return;
    if(F->GetStoneGuardDriver())
    {
        RenderedNativeGuardEntityIds.Add(F->GetRuntimeEntityId()); // Same actual DrawFighter invocation; no art/gameplay mutation.
        if(bUseFairytaleGuardMoveRigPreview&&DrawFairytaleGuardMoveRigBody(F))return;
        if(bUseFairytaleGuardFullPreview)
        {if(DrawFairytaleGuardFullBody(F))return;}
        else if(DrawFairytaleGuardBody(F))return;
        DrawGuardFeedback(F);
        // Dedicated procedural body placeholder; finite Guard feedback is a separate event consumer.
        const auto& S=F->GetStoneGuardDriver()->State();const auto& A=S.Action;
        const FVector2D P=Ground(F->GetGroundPosition());const float Side=F->Facing;
        Oval(P.X-24.f,P.Y-5.f,48.f,10.f,FLinearColor(0,0,0,.25f));
        const FLinearColor Edge(.10f,.12f,.12f,1.f);
        const FLinearColor Rock=F->HitFlash>0.f?FLinearColor(.63f,.53f,.35f,1.f):FLinearColor(.35f,.38f,.38f,1.f);
        if(F->bDead)
        {
            DrawRect(Edge,P.X-27.f,P.Y-13.f,54.f,13.f);DrawRect(Rock,P.X-24.f,P.Y-11.f,48.f,9.f);
            return;
        }
        if(S.Phase==DungeonStoneGuard::EPhase::Windup||S.Phase==DungeonStoneGuard::EPhase::Active)
        {
            const auto C=A.LockedCenter;const FLinearColor Hint=S.Phase==DungeonStoneGuard::EPhase::Windup
                ?FLinearColor(.95f,.50f,.12f,.55f):FLinearColor(1.f,.72f,.20f,.8f);
            if(A.Kind==DungeonStoneGuard::EAttack::AxeSweep)
            {
                const FVector2D V[]={Ground({C.X,C.Y-65.}),Ground({C.X+180.*A.Facing,C.Y-65.}),
                    Ground({C.X+180.*A.Facing,C.Y+65.}),Ground({C.X,C.Y+65.})};
                for(int32 I=0;I<4;++I)DrawCombatRangeDebugLine(V[I].X,V[I].Y,V[(I+1)%4].X,V[(I+1)%4].Y,Hint,1.5f);
            }
            else for(int32 I=0;I<32;++I)
            {
                const double T=2.*PI*double(I)/32.,U=2.*PI*double(I+1)/32.;
                const auto V=Ground({C.X+160.*FMath::Cos(T),C.Y+90.*FMath::Sin(T)});
                const auto W=Ground({C.X+160.*FMath::Cos(U),C.Y+90.*FMath::Sin(U)});
                DrawCombatRangeDebugLine(V.X,V.Y,W.X,W.Y,Hint,1.5f);
            }
        }
        // Blocky large stone silhouette, clearly separate from existing human/Knight sprites.
        DrawRect(Edge,P.X-25.f,P.Y-65.f,50.f,59.f);DrawRect(Rock,P.X-22.f,P.Y-62.f,44.f,54.f);
        DrawRect(Edge,P.X-18.f,P.Y-82.f,36.f,23.f);DrawRect(Rock,P.X-15.f,P.Y-79.f,30.f,17.f);
        DrawRect(Edge,P.X-23.f,P.Y-11.f,18.f,11.f);DrawRect(Edge,P.X+5.f,P.Y-11.f,18.f,11.f);
        const FLinearColor Eye=S.Phase==DungeonStoneGuard::EPhase::Dormant?Edge:FLinearColor(.95f,.60f,.18f,1.f);
        DrawRect(Eye,P.X-10.f,P.Y-73.f,6.f,3.f);DrawRect(Eye,P.X+4.f,P.Y-73.f,6.f,3.f);
        Line(P.X-8.f,P.Y-56.f,P.X+3.f,P.Y-42.f,Edge,2.f);Line(P.X+3.f,P.Y-42.f,P.X-6.f,P.Y-27.f,Edge,2.f);
        // Two-handed stone axe reads the real phase clock; this is not an authored action clip.
        float Lift=0.f;
        if(S.Phase==DungeonStoneGuard::EPhase::Windup&&A.Kind==DungeonStoneGuard::EAttack::AxeSweep)
            Lift=float(FMath::Clamp((S.Time-A.Start)/(A.ActiveAt-A.Start),0.,1.));
        else if(S.Phase==DungeonStoneGuard::EPhase::Active)Lift=.45f;
        const FVector2D Grip(P.X+Side*14.f,P.Y-43.f),Tip(P.X+Side*(44.f-18.f*Lift),P.Y-14.f-78.f*Lift);
        Line(Grip.X-Side*9.f,Grip.Y+12.f,Tip.X,Tip.Y,Edge,7.f);
        Line(Grip.X-Side*9.f,Grip.Y+12.f,Tip.X,Tip.Y,FLinearColor(.31f,.23f,.14f,1.f),3.f);
        DrawRect(Edge,Tip.X-13.f,Tip.Y-9.f,26.f,19.f);DrawRect(Rock,Tip.X-10.f,Tip.Y-6.f,20.f,13.f);
        DrawRect(Edge,Grip.X-3.f,Grip.Y-3.f,6.f,6.f);DrawRect(Edge,Grip.X-Side*8.f-3.f,Grip.Y+5.f,6.f,6.f);
        return; // Never borrow generic enemy sprites, sword trails or Knight-only sounds.
    }

    using namespace DungeonPalette;
    FVector2D P=Ground(F->GetGroundPosition());
    constexpr float BodyScale=float(DungeonPresentationScale::RelativeScale);
    Oval(P.X-20*BodyScale,P.Y-5*BodyScale,40*BodyScale,10*BodyScale,FLinearColor(0,0,0,.28f));
    const FString Clip=F->AnimationName;
    const int Count=Clip==TEXT("attack")?6:Clip==TEXT("hurt")?2:8;
    const bool Loop=Clip==TEXT("idle")||Clip==TEXT("walk");
    const float FPS=Clip==TEXT("idle")?8.f:Clip==TEXT("walk")?12.f:Clip==TEXT("attack")?15.f:Clip==TEXT("death")?12.f:10.f;
    int Index=FMath::FloorToInt(F->AnimationTime*FPS);
    if (Clip == TEXT("attack") && F->IsContentMelee())
        Index = FMath::Min(Count-1, FMath::FloorToInt(F->GetActionProgress()*Count));
    Index=Loop?Index%Count:FMath::Min(Index,Count-1);
    UTexture2D* Frame=nullptr;
    bool Candidate=false;
    FString CandidateClip;
    int32 CandidateIndex=0;
    FVector2D CandidateRoot(256.f,472.f);
    if (bUseCandidateSprites && !F->bEnemy)
    {
        bRenderedArmorLayersUsed=false;RenderedArmorLayerPaths.Reset();RenderedPlayerDrawStack.Reset();
        bRenderedWeaponBodyUsed=false;RenderedWeaponBodyFrame=-1;RenderedWeaponBodyFacing=0;
        RenderedWeaponBodyClip.Reset();RenderedWeaponBodyActionId=0;RenderedWeaponBodySampleTime=0.;
        RenderedWeaponBodyInstanceId=0;RenderedWeaponStateIndex=-1;
        const bool SwordPose=F->WeaponId==TEXT("sword") || F->WeaponId==TEXT("WPN-SWD-001");
        CandidateClip=Clip==TEXT("attack") ? F->IsCurrentPrimaryAirborne()?TEXT("air_primary_1"):FString::Printf(TEXT("primary_%d"),F->ComboStage) : Clip;
        CandidateIndex=Clip==TEXT("attack")?F->GetPrimaryPoseFrame():FMath::FloorToInt(F->AnimationTime*(Clip==TEXT("walk")?10.f:6.f))%6;
        if(bUseArmorLayerPreview && Clip==TEXT("idle")) CandidateIndex=FMath::FloorToInt(F->AnimationTime/.15f)%6;
        const auto& Skill=F->GetWeaponSkillAction();
        if(Clip==TEXT("secondary") && Skill.Active)
        {
            const double Now=F->GetWeaponSkillTime();
            const double Start=Now<Skill.ActiveAt?Skill.Start:Now<Skill.ActiveEnd?Skill.ActiveAt:Skill.ActiveEnd;
            const double End=Now<Skill.ActiveAt?Skill.ActiveAt:Now<Skill.ActiveEnd?Skill.ActiveEnd:Skill.End;
            const int32 Base=Now<Skill.ActiveAt?0:Now<Skill.ActiveEnd?2:4;
            CandidateIndex=Base+FMath::Clamp(FMath::FloorToInt((Now-Start)/(End-Start)*2.0),0,1);
        }
        // Preserve the armored identity when switching to unfinished weapon
        // families. Their attack body is an explicit idle placeholder, with
        // the existing family weapon drawing; never play SWD poses as GSW/SPR.
        if(!SwordPose && (Clip==TEXT("attack") || Clip==TEXT("secondary") || Clip==TEXT("reload")))
        { CandidateClip=TEXT("idle");CandidateIndex=FMath::FloorToInt(F->AnimationTime*6.f)%6; }
        // Legacy QA armor keeps its original duration. Bound equipment samples
        // the accepted transaction's actual clock, including weapon Q.
        if(Clip==TEXT("equip"))
        { CandidateClip=TEXT("equip_armor");CandidateIndex=FMath::Clamp(FMath::FloorToInt(F->AnimationTime/.5f*6.f),0,5); }
        if(F->IsEquipmentBound() && (Clip==TEXT("equip_weapon") || Clip==TEXT("equip_armor")))
            if(auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this)))
            {
                const auto& Action=Game->GetEquipmentView().Action;
                if(Action.Active && Action.Deadline>Action.Start)
                    CandidateIndex=FMath::Clamp(FMath::FloorToInt((Game->GetSimulationTime()-Action.Start)/(Action.Deadline-Action.Start)*6.0),0,5);
            }
        if(Clip==TEXT("dodge")) CandidateIndex=FMath::Clamp(FMath::FloorToInt(F->AnimationTime/.40f*6.f),0,5);
        if (Clip!=TEXT("attack") && Clip!=TEXT("hurt") && Clip!=TEXT("secondary") && Clip!=TEXT("dodge") && Clip!=TEXT("equip") && Clip!=TEXT("equip_weapon") && Clip!=TEXT("equip_armor") && !F->bDead)
        {
            if (F->JumpHeight>0.f)
            {
                const float V=F->GetVerticalVelocity(); CandidateClip=V>=0.f?TEXT("jump"):TEXT("fall");
                CandidateIndex=V>=0.f?FMath::Clamp(FMath::FloorToInt((630.f-V)/630.f*4.f),0,3)
                    :FMath::Clamp(FMath::FloorToInt(-V/630.f*2.f),0,1);
            }
            else if (F->GetLandingVisualAge()<.12f)
            { CandidateClip=TEXT("land"); CandidateIndex=FMath::Clamp(FMath::FloorToInt(F->GetLandingVisualAge()/.12f*2.f),0,1); }
        }
        if (Clip==TEXT("hurt")) CandidateIndex=FMath::Clamp(FMath::FloorToInt(F->AnimationTime/.4f*6.f),0,5);
        if (F->bDead) { CandidateClip=TEXT("death"); CandidateIndex=FMath::Clamp(FMath::FloorToInt(F->AnimationTime/.8f*6.f),0,5); }
        if (!CandidateClip.IsEmpty())
            if (auto Texture=GetCandidateFrame(TEXT("hero"),CandidateClip,CandidateIndex))
            {
                Frame=Texture; Candidate=true;
                if (auto Marker=DungeonCandidateAssembly::Find(CandidateClip,CandidateIndex)) CandidateRoot=Marker->Root;
            }
    }
    if (bUseCandidateSprites && F->bEnemy && F->GetStoneKnightDriver())
    {
        const auto& S=F->GetStoneKnightDriver()->State();
        CandidateClip=Clip;
        CandidateIndex=FMath::FloorToInt(F->AnimationTime*(Clip==TEXT("walk")?10.f:6.f))%6;
        if (S.Phase==DungeonStoneKnight::EPhase::Dormant) CandidateIndex=0;
        else if (S.Phase==DungeonStoneKnight::EPhase::Waking)
            CandidateIndex=FMath::Clamp(FMath::FloorToInt((S.Time-S.WakeStartedAt)/.85*6.0),0,5);
        else if (S.Phase==DungeonStoneKnight::EPhase::Windup)
            CandidateIndex=FMath::Clamp(FMath::FloorToInt((S.Time-S.Action.Start)/(S.Action.ActiveAt-S.Action.Start)*2.0),0,1);
        else if (S.Phase==DungeonStoneKnight::EPhase::Active)
            CandidateIndex=2+(S.Action.Kind==DungeonStoneKnight::EAttack::Charge
                ? FMath::FloorToInt((S.Time-S.Action.ActiveAt)*12.0)%2
                : FMath::Clamp(FMath::FloorToInt((S.Time-S.Action.ActiveAt)/(S.Action.ActiveEnd-S.Action.ActiveAt)*2.0),0,1));
        else if (S.Phase==DungeonStoneKnight::EPhase::Recovery)
            CandidateIndex=FMath::Clamp(FMath::FloorToInt((S.Time-S.Action.ActiveEnd)/(S.Action.RecoveryEnd-S.Action.ActiveEnd)*6.0),0,5);
        else if (S.Phase==DungeonStoneKnight::EPhase::Stunned)
            CandidateIndex=FMath::Clamp(FMath::FloorToInt((S.Time-(S.StunUntil-.4))/.4*6.0),0,5);
        else if (F->bDead) CandidateIndex=FMath::Clamp(FMath::FloorToInt(F->AnimationTime/.6f*6.f),0,5);
        if (auto Texture=GetCandidateFrame(TEXT("stone"),CandidateClip,CandidateIndex)) { Frame=Texture; Candidate=true; }
    }
    if (!Frame) Frame=GetFrame(F->bEnemy,Clip,Index);
    UTexture2D *BodyFar=nullptr,*BodyNear=nullptr,*ArmorFront=nullptr,*ArmorBack=nullptr,*ArmorNear=nullptr;
    bool Layered=false;
    bool WeaponLayered=false,WeaponPrimary=false;
    UTexture2D *WeaponBodyFar=nullptr,*WeaponBodySupport=nullptr,*WeaponBodyNear=nullptr;
    bool WeaponArmorLayered=false;
    UTexture2D *WeaponArmorFar=nullptr,*WeaponArmorNear=nullptr;
    const bool KnownWeaponArmor=F->ArmorId==TEXT("ARM-LGT-001")||F->ArmorId==TEXT("ARM-MED-001")
        ||F->ArmorId==TEXT("ARM-HVY-001")||F->ArmorId==TEXT("ARM-ROB-001");
    const bool NativeXBWHeld=bUseXBWReloadBodyPreview&&!F->bEnemy&&F->WeaponId==TEXT("WPN-XBW-001");
    bool XBWEquipmentHold=false;
    if(NativeXBWHeld&&F->IsEquipmentBound()&&(Clip==TEXT("equip_weapon")||Clip==TEXT("equip_armor")))
    {
        const auto HeldSocket=F->GetWeaponPoseSocket();
        XBWEquipmentHold=HeldSocket.Supported&&HeldSocket.Clip==DungeonWeaponPoseSocket::EClip::Ready;
    }
    if(bUseWeaponBodyPreview && !F->bEnemy && !F->bDead
        && (F->ArmorId.IsEmpty() || (bUseXBWReloadBodyPreview&&bUseArmorLayerPreview&&KnownWeaponArmor))
        && F->WeaponId==TEXT("WPN-XBW-001") && (Clip==TEXT("idle") || Clip==TEXT("attack")
            || Clip==TEXT("secondary") || Clip==TEXT("reload") || XBWEquipmentHold) && (F->JumpHeight==0.f||bUseXBWReloadBodyPreview))
    {
        DungeonXBWBodyPose::FPose PrimaryPose;
        const auto Socket=F->GetWeaponPoseSocket();
        const bool Reload=bUseXBWReloadBodyPreview&&Socket.Supported&&Socket.Clip==DungeonWeaponPoseSocket::EClip::Reload;
        WeaponPrimary=bUseXBWReloadBodyPreview
            ?Socket.Supported&&Socket.Clip==DungeonWeaponPoseSocket::EClip::Primary&&!Socket.GroundPoseFallback
            :bUseXBWPrimaryBodyPreview&&Clip==TEXT("attack")&&DungeonXBWBodyPose::Primary(F->GetWeaponActionsState(),PrimaryPose);
        const int32 ReadyIndex=bUseXBWReloadBodyPreview&&Socket.Supported?Socket.Frame
            :WeaponPrimary?PrimaryPose.Frame:FMath::FloorToInt(F->AnimationTime/.15f)%6;
        WeaponBodyFar=Reload?GetXBWReloadTexture(TEXT("body_far"),ReadyIndex):GetXBWReadyTexture(TEXT("body_far"),ReadyIndex,WeaponPrimary);
        WeaponBodySupport=Reload?GetXBWReloadTexture(TEXT("body_support"),ReadyIndex):GetXBWReadyTexture(TEXT("body_support"),ReadyIndex,WeaponPrimary);
        WeaponBodyNear=Reload?GetXBWReloadTexture(TEXT("body_near"),ReadyIndex):GetXBWReadyTexture(TEXT("body_near"),ReadyIndex,WeaponPrimary);
        auto WeaponTexture=bUseXBWReloadBodyPreview&&Socket.Supported&&Socket.WeaponStateIndex>=0
            ?GetXBWReloadTexture(TEXT("weapon"),Socket.WeaponStateIndex):GetXBWReadyTexture(TEXT("weapon"));
        const auto Ready=[](UTexture2D* T){return T && T->GetResource();};
        WeaponLayered=Ready(WeaponBodyFar)&&Ready(WeaponBodySupport)&&Ready(WeaponBodyNear)&&Ready(WeaponTexture);
        const FString ArmorClip=Reload?TEXT("reload"):WeaponPrimary?TEXT("primary"):TEXT("ready_idle");
        if(WeaponLayered&&KnownWeaponArmor)
        {
            WeaponArmorFar=GetXBWArmorTexture(ArmorClip,F->ArmorId,TEXT("armor_far"),ReadyIndex);
            WeaponArmorNear=GetXBWArmorTexture(ArmorClip,F->ArmorId,TEXT("armor_near"),ReadyIndex);
            WeaponArmorLayered=Ready(WeaponArmorFar)&&Ready(WeaponArmorNear);
            WeaponLayered&=WeaponArmorLayered; // Missing cloth never borrows a Sword pose.
        }
        if(WeaponLayered)
        {
            Frame=WeaponBodyFar;Candidate=true;
            CandidateClip=Reload?TEXT("xbw_reload_four_keyposes"):WeaponPrimary?TEXT("xbw_primary")
                :Clip==TEXT("idle")?TEXT("xbw_ready_idle"):TEXT("xbw_ready_idle_pose_during_")+Clip;
            CandidateIndex=ReadyIndex;RenderedWeaponBodyClip=CandidateClip;
            if(bUseXBWReloadBodyPreview&&Socket.Supported)
            {
                RenderedWeaponBodyActionId=Socket.ActionId;RenderedWeaponBodySampleTime=Socket.SampleTime;
                RenderedWeaponBodyInstanceId=Socket.InstanceId;RenderedWeaponStateIndex=Socket.WeaponStateIndex;
            }
            else if(WeaponPrimary){RenderedWeaponBodyActionId=F->GetWeaponActionsState().Action.ActionId;
                RenderedWeaponBodySampleTime=F->GetWeaponActionsState().Time;}
            CandidateRoot=FVector2D(256.f,472.f);bRenderedWeaponBodyUsed=true;
            RenderedWeaponBodyFrame=ReadyIndex;RenderedWeaponBodyFacing=F->Facing;
            bRenderedArmorLayersUsed=WeaponArmorLayered;
        }
    }
    if(bUseArmorLayerPreview && Candidate && !F->bEnemy && !F->bDead
        && (CandidateClip==TEXT("idle") || CandidateClip==TEXT("walk") || (CandidateClip.StartsWith(TEXT("primary_"))
            && (F->WeaponId==TEXT("sword") || F->WeaponId==TEXT("WPN-SWD-001")))))
    {
        const bool KnownArmor=F->ArmorId==TEXT("ARM-LGT-001") || F->ArmorId==TEXT("ARM-MED-001")
            || F->ArmorId==TEXT("ARM-HVY-001") || F->ArmorId==TEXT("ARM-ROB-001");
        if(KnownArmor || F->ArmorId.IsEmpty())
        {
            BodyFar=GetArmorLayerFrame(CandidateClip,TEXT(""),TEXT("body_far"),CandidateIndex);
            BodyNear=GetArmorLayerFrame(CandidateClip,TEXT(""),TEXT("body_near"),CandidateIndex);
            if(KnownArmor)
            {
                ArmorFront=GetArmorLayerFrame(CandidateClip,F->ArmorId,TEXT("front"),CandidateIndex);
                if(CandidateClip==TEXT("idle")) ArmorBack=GetArmorLayerFrame(CandidateClip,F->ArmorId,TEXT("back"),CandidateIndex);
                if(bUseArmorSleevesPreview && F->ArmorId==TEXT("ARM-ROB-001") && (CandidateClip==TEXT("primary_2") || CandidateClip==TEXT("primary_3")))
                    ArmorNear=GetArmorLayerFrame(CandidateClip,F->ArmorId,TEXT("near"),CandidateIndex);
            }
            const auto Ready=[](UTexture2D* T){return T && T->GetResource();};
            Layered=Ready(BodyFar) && Ready(BodyNear) && (!KnownArmor
                || (Ready(ArmorFront) && (CandidateClip!=TEXT("idle") || Ready(ArmorBack))));
            const bool NeedsNear=bUseArmorSleevesPreview && F->ArmorId==TEXT("ARM-ROB-001")
                && (CandidateClip==TEXT("primary_2") || CandidateClip==TEXT("primary_3"));
            Layered &= !NeedsNear || Ready(ArmorNear);
            if(Layered) { Frame=BodyFar;bRenderedArmorLayersUsed=true; }
        }
    }
    const float Size=float(Candidate?DungeonPresentationScale::CandidateBodySize:F->bEnemy
        ?DungeonPresentationScale::FallbackEnemyBodySize:DungeonPresentationScale::FallbackPlayerBodySize);
    RenderedActorSpriteSizes.Add(F,Size);
    const float Elevation=F->JumpHeight*.70f;
    const auto Top=Screen(P.X-Size*(Candidate?(F->Facing<0?512.f-CandidateRoot.X:CandidateRoot.X)/512.f:.5f),
        P.Y-Elevation-Size*(Candidate?CandidateRoot.Y/512.f:220.f/256.f));
    auto Tint=F->HitFlash>0?FLinearColor(1.7f,.6f,.4f,1):FLinearColor::White;
    if(F->bEnemy) Tint.A=float(GetCurrentVisibilityAt(F->GetGroundPosition()));
    if(!F->bEnemy) { RenderedPlayerTexturePath=Frame?Frame->GetPathName():FString();RenderedPlayerSpriteSize=Size; }
    const auto DrawLayer=[this,F,Top,Size,Tint,Layered,WeaponLayered,WeaponArmorLayered](UTexture2D* Texture)
    {
        if(!Texture) return;
        DrawTexture(Texture,Top.X,Top.Y,Size*UIScale,Size*UIScale,F->Facing<0?1.f:0.f,0,F->Facing<0?-1.f:1.f,1,Tint);
        FActorQuad Quad;Quad.Owner=F;Quad.Texture=Texture;Quad.Top=Top;Quad.Size=Size*UIScale;Quad.Tint=Tint;ActorQuads.Add(Quad);
        if(Layered || WeaponArmorLayered) RenderedArmorLayerPaths.Add(Texture->GetPathName());
        if((Layered || WeaponLayered) && !F->bEnemy) RenderedPlayerDrawStack.Add(Texture->GetPathName());
    };
    if(Layered)
    {
        DrawLayer(ArmorBack);DrawLayer(BodyFar);DrawLayer(ArmorFront);
    }
    else if(Frame)
    {
        DrawLayer(Frame);
    }
    else
    {
        // Readable fallback while source art is loading, preserving the same feet.
        Oval(P.X-18*BodyScale,P.Y-Elevation-95*BodyScale,36*BodyScale,37*BodyScale,F->bEnemy?FLinearColor(.3f,.7f,.3f,1):Gold);
        Box(P.X-23*BodyScale,P.Y-Elevation-62*BodyScale,46*BodyScale,50*BodyScale,F->bEnemy?FLinearColor(.30f,.47f,.24f,1):FLinearColor(.37f,.55f,.65f,1));
        Box(P.X-19*BodyScale,P.Y-Elevation-12*BodyScale,14*BodyScale,16*BodyScale,Muted);
        Box(P.X+4*BodyScale,P.Y-Elevation-12*BodyScale,14*BodyScale,16*BodyScale,Muted);
    }
    // The frozen wake frame4 has an empty eye slit. Keep the actual source and
    // its recorded defect; this measured presentation glow only prevents one
    // dark blink during the real .85s wake warning. Both facings mirror once.
    if(Candidate && F->GetStoneKnightDriver() && CandidateClip==TEXT("wake") && CandidateIndex==3)
    {
        const FVector2D Eye(P.X+F->Facing*(295.f-256.f)*Size/512.f,P.Y-Elevation+(231.f-472.f)*Size/512.f);
        Oval(Eye.X-4,Eye.Y-4,8,8,FLinearColor(1,.52f,.08f,.25f));
        Oval(Eye.X-2,Eye.Y-2,4,4,FLinearColor(1,.72f,.16f,1));
    }
    const auto HeroMarker=Candidate && !F->bEnemy ? DungeonCandidateAssembly::Find(CandidateClip,CandidateIndex) : nullptr;
    const bool AuthoredNoWeapon=HeroMarker && !HeroMarker->WeaponVisible;
    if(WeaponArmorLayered)DrawLayer(WeaponArmorFar);
    const bool ReadyWeapon=WeaponLayered && DrawXBWReadyWeapon(F,Size,Tint,WeaponPrimary);
    const bool CandidateWeapon=ReadyWeapon || (Candidate && !F->bEnemy && !F->bDead && DrawCandidateSword(F,Frame,CandidateClip,CandidateIndex,Size,Tint,!Layered));
    if(CandidateWeapon && !ReadyWeapon) RenderedPlayerDrawStack.Add(GetCandidateSword()->GetPathName());
    if(WeaponLayered) {DrawLayer(WeaponBodySupport);if(WeaponArmorLayered)DrawLayer(WeaponArmorNear);DrawLayer(WeaponBodyNear);bRenderedWeaponBodyUsed=ReadyWeapon;}
    if(Layered) {DrawLayer(ArmorNear);DrawLayer(BodyNear);}
    const bool BakedStoneEquipment=Candidate && F->bEnemy && F->GetStoneKnightDriver();
    if(!F->bDead && !AuthoredNoWeapon && !CandidateWeapon && !BakedStoneEquipment && !NativeXBWHeld)
    {
        const float Side=F->Facing;
        const FVector2D Hand(P.X+Side*13*BodyScale,P.Y-Elevation-54*BodyScale);
        const float Swing=F->AttackTime>0?FMath::Sin((F->IsContentMelee()?F->GetActionProgress()*PI:F->AnimationTime*9.f))*.9f:0.f;
        const FVector2D Tip=Hand+FVector2D(Side*(25+Swing*35),-43+Swing*30)*BodyScale;
        Line(Hand.X,Hand.Y,Tip.X,Tip.Y,Ink,8*BodyScale);
        Line(Hand.X,Hand.Y,Tip.X,Tip.Y,F->bEnemy?FLinearColor(.48f,.31f,.17f,1):Cream,4*BodyScale);
        if(F->WeaponId==TEXT("axe")&&!F->bEnemy)
            Triangle(Tip+FVector2D(-Side*9,-9)*BodyScale,Tip+FVector2D(Side*20,-6)*BodyScale,Tip+FVector2D(Side*12,19)*BodyScale,Gold);
        else if(!F->bEnemy)
            Line(Hand.X-Side*8*BodyScale,Hand.Y-10*BodyScale,Hand.X+Side*16*BodyScale,Hand.Y-4*BodyScale,Gold,4*BodyScale);
    }
    const auto& Skill=F->GetWeaponSkillAction();
    const bool SkillWindow=Skill.Active && Skill.Phase==DungeonWeaponActions::EPhase::Active;
    const bool RangedFamily=F->WeaponId==TEXT("WPN-XBW-001") || F->WeaponId==TEXT("WPN-STF-001");
    if(F->AttackTime>0&&!F->bDead && !RangedFamily && !F->GetStoneKnightDriver() && (!F->IsContentMelee() || F->IsAttackActive() || SkillWindow))
    {
        FMeleeTrail Trail;Trail.Owner=F;Trail.Clip=CandidateClip;Trail.Frame=CandidateIndex;
        Trail.Size=Size;Trail.CandidateWeapon=CandidateWeapon;MeleeTrails.Add(MoveTemp(Trail));
    }
    DrawStoneEffects(F);
    if(bShowInterface&&F->bEnemy&&!F->bDead)
    {
        Box(P.X-17,P.Y-Elevation-Size*.65f,34,3,Ink);
        Box(P.X-17,P.Y-Elevation-Size*.65f,34*FMath::Clamp(F->Health/F->MaxHealth,0.f,1.f),3,FLinearColor(.82f,.29f,.22f,1));
    }
    if(bShowInterface&&!F->bEnemy&&!F->bDead) Triangle({P.X-5,P.Y+17},{P.X+5,P.Y+17},{P.X,P.Y+11},Gold);
    bool EquipmentProgress=false;
    if(bShowInterface && !F->bEnemy && !F->bDead && F->IsEquipmentBound())
        if(auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this)))
        {
            const auto& Action=Game->GetEquipmentView().Action;
            if(Action.Active && Action.Deadline>Action.Start)
            {
                EquipmentProgress=true;
                const float Progress=float(FMath::Clamp((Game->GetSimulationTime()-Action.Start)/(Action.Deadline-Action.Start),0.,1.));
                Box(P.X-24,P.Y+23,48,4,Ink);Box(P.X-24,P.Y+23,48*Progress,4,Gold);
                Text(Action.Kind==EDungeonEquipmentActionKind::PickupArmor?TEXT("穿戴"):Action.Kind==EDungeonEquipmentActionKind::SwitchWeapon?TEXT("切换"):TEXT("拾取"),P.X-14,P.Y+29,.38f,Cream);
            }
        }
    if(bShowInterface && !EquipmentProgress && !F->bEnemy && F->GetArmorChangeRemaining()>0.f)
    {
        Box(P.X-24,P.Y+23,48,4,Ink);
        Box(P.X-24,P.Y+23,48*(1.f-F->GetArmorChangeRemaining()/.5f),4,Gold);
        Text(TEXT("换甲"),P.X-14,P.Y+29,.38f,Cream);
    }
}

void ADungeonHUD::DrawEquipmentSources(ADungeonGameMode* Game)
{
    using namespace DungeonPalette;
    const auto& View=Game->GetEquipmentView();if(!View.Bound) return;
    for(const auto& Source:Game->GetEquipmentSources())
    {
        if(Source.Consumed || !Source.Settled || Source.RoomInstanceId!=View.RoomInstanceId
            || GetCurrentVisibilityAt(Source.Position)<=.05) continue;
        const auto P=Ground(Source.Position);if(P.X<-100 || P.X>1380) continue;
        const bool Selected=View.SelectedSourceId==Source.SourceId;
        const auto* Definition=DungeonEquipmentStats::FindTemplate(Source.Item.ContentId);
        const bool Armor=Definition && Definition->Kind==DungeonEquipmentStats::EKind::Armor;
        const FLinearColor Color=bShowInterface&&Selected?Gold:Muted;
        Oval(P.X-14,P.Y-3,28,7,FLinearColor(0,0,0,.35f));
        // These small ground tokens are explicit development placeholders;
        // their identity and selection come from the authoritative source.
        if(Armor)
        {
            Line(P.X-9,P.Y-23,P.X+9,P.Y-23,Color,2);
            Line(P.X-9,P.Y-23,P.X-7,P.Y-7,Color,2);
            Line(P.X+9,P.Y-23,P.X+7,P.Y-7,Color,2);
            Line(P.X-7,P.Y-7,P.X+7,P.Y-7,Color,2);
        }
        else
        {Line(P.X-7,P.Y-5,P.X+8,P.Y-26,Color,3);Line(P.X-9,P.Y-13,P.X+3,P.Y-6,Color,2);}
        if(bShowInterface&&Selected) Oval(P.X-19,P.Y-3,38,4,FLinearColor(.94f,.66f,.28f,.7f));
        const bool BeingPickedUp=View.Action.Active&&View.Action.SourceId==Source.SourceId;
        // The actor already has one progress label. Repeating the source name
        // and hint beneath its feet makes the two text rows overlap that bar.
        if(!BeingPickedUp)
        {
            Text(DungeonEquipmentLabels::Name(UTF8_TO_TCHAR(Source.Item.ContentId.c_str())),P.X-45,P.Y+8,.38f,Color);
            if(Selected) Text(TEXT("E 拾取 · Tab 选物"),P.X-48,P.Y+25,.34f,Cream);
        }
    }
}

void ADungeonHUD::DrawEquipmentPanel(ADungeonGameMode* Game)
{
    using namespace DungeonPalette;
    const auto& View=Game->GetEquipmentView();if(!View.Bound) return;
    const FDungeonEquipmentSourceView* Source=nullptr;
    for(const auto& Candidate:Game->GetEquipmentSources())
        if(Candidate.SourceId==View.SelectedSourceId && !Candidate.Consumed
            && Candidate.RoomInstanceId==View.RoomInstanceId) {Source=&Candidate;break;}
    if(!Source)
    {
        if(!View.FailureText.IsEmpty()) Text(View.FailureText,900,154,.45f,FLinearColor(.94f,.48f,.37f,1));
        return;
    }
    FDungeonEquipmentSlotView Incoming;
    Incoming.InstanceId=Source->InstanceId;Incoming.ContentId=UTF8_TO_TCHAR(Source->Item.ContentId.c_str());
    Incoming.Grade=Source->Item.Grade;Incoming.Tier=Source->Item.Tier;Incoming.Package=Source->Item.Package;
    for(const auto& Affix:Source->Item.Affixes)
    {
        FDungeonEquipmentAffixView A;A.Id=UTF8_TO_TCHAR(Affix.Id.c_str());A.Magnitude=Affix.Magnitude;Incoming.Affixes.Add(A);
    }
    const auto* Definition=DungeonEquipmentStats::FindTemplate(Source->Item.ContentId);
    const bool Armor=Definition && Definition->Kind==DungeonEquipmentStats::EKind::Armor;
    const int32 CompareSlot=Armor?2:View.NeedsSlotSelection&&View.SelectionSlot>=0&&View.SelectionSlot<2?View.SelectionSlot:View.ActiveSlot;
    const auto& Current=View.Slots[CompareSlot];
    const float Height=(View.NeedsSlotSelection?260.f:210.f)+18.f*(Incoming.Affixes.Num()+Current.Affixes.Num());
    const float X=900,Y=180,W=320;
    Box(X,Y,W,Height,FLinearColor(.025f,.045f,.06f,.96f));
    Line(X,Y,X+W,Y,Gold,2);
    float Row=Y+12;
    const auto DrawItem=[this,X,&Row](const FString& Title,const FDungeonEquipmentSlotView& Item)
    {
        using namespace DungeonPalette;
        Text(Title,X+14,Row,.40f,Muted);Row+=19;
        Text(Item.InstanceId?FString::Printf(TEXT("%s +%d"),*DungeonEquipmentLabels::Name(Item.ContentId),Item.Grade):TEXT("空槽"),X+14,Row,.62f,Cream);Row+=27;
        if(Item.Affixes.IsEmpty()) {Text(TEXT("无附魔"),X+14,Row,.40f,Muted);Row+=18;}
        else
        {
            Text(FString::Printf(TEXT("附魔 %d 阶"),Item.Tier),X+14,Row,.40f,Muted);Row+=18;
            for(const auto& A:Item.Affixes)
            {
                const auto Label=DungeonEquipmentLabels::Affix(A.Id);
                Text(FString::Printf(TEXT("%s  %+d%s"),Label.Name,A.Magnitude*Label.Direction,Label.Unit),X+14,Row,.43f,
                    Label.Beneficial?FLinearColor(.51f,.87f,.69f,1):FLinearColor(.94f,.48f,.37f,1));Row+=18;
            }
        }
    };
    DrawItem(TEXT("地面装备"),Incoming);
    Row+=8;Line(X+14,Row,X+W-14,Row,FLinearColor(.21f,.29f,.30f,1));Row+=9;
    DrawItem(Armor?TEXT("身上防具"):CompareSlot==View.ActiveSlot?TEXT("当前武器"):TEXT("备用武器"),Current);
    Row+=7;
    if(View.NeedsSlotSelection)
    {
        Text(Armor?TEXT("Enter 替换防具 · Esc 取消"):TEXT("← → 选槽 · Enter 替换 · Esc 取消"),X+14,Row,.42f,Gold);
        if(!Armor)
        {
            Row+=20;
            for(int32 Slot=0;Slot<2;++Slot)
                Text(FString::Printf(TEXT("%s %s %s +%d"),Slot==View.SelectionSlot?TEXT("▶"):TEXT("·"),Slot==View.ActiveSlot?TEXT("当前"):TEXT("备用"),*DungeonEquipmentLabels::Name(View.Slots[Slot].ContentId),View.Slots[Slot].Grade),X+14,Row+Slot*19,.42f,Slot==View.SelectionSlot?Gold:Muted);
        }
    }
    else Text(View.Action.Active?View.Action.Kind==EDungeonEquipmentActionKind::SwitchWeapon?TEXT("切换中"):TEXT("移动或受伤会中断拾取"):TEXT("E 拾取 · Tab 选择其他物品"),X+14,Row,.42f,Gold);
    if(!View.FailureText.IsEmpty()&&View.LastFailure!=EDungeonEquipmentFailure::SelectionRequired)
        Text(View.FailureText,X+14,Y+Height-22,.38f,FLinearColor(.94f,.48f,.37f,1));
}

void ADungeonHUD::DrawInterface(ADungeonGameMode* Game)
{
    if(!bShowInterface) return;
    using namespace DungeonPalette;
    auto Player=Game->GetPlayerFighter(); if(!Player) return;
    Box(0,0,1280,108,Ink);
    Text(TEXT("烬堡 · 原型"),62,29,1.15f,Cream);
    Text(TEXT("地牢试炼 / 单人"),65,72,.55f,Muted);
    if (bUseCandidateSprites) Text(TEXT("开发试玩"),290,87,.45f,Gold);
    Box(290,35,265,14,FLinearColor(.18f,.12f,.12f,1));
    Box(290,35,265*FMath::Clamp(Player->Health/Player->MaxHealth,0.f,1.f),14,FLinearColor(.78f,.25f,.22f,1));
    Text(FString::Printf(TEXT("生命  %.0f / %.0f"),Player->Health,Player->MaxHealth),290,58,.65f,Cream);
    Text(FString::Printf(TEXT("金币  %02d"),Player->Coins),597,35,.8f,Gold);
    const auto& Equipment=Game->GetEquipmentView();
    const FString WeaponName = Equipment.Bound
        ?FString::Printf(TEXT("%s +%d"),*DungeonEquipmentLabels::Name(Equipment.Slots[Equipment.ActiveSlot].ContentId),Equipment.Slots[Equipment.ActiveSlot].Grade)
        : Player->WeaponId==TEXT("axe")?TEXT("原型战斧")
        : Player->WeaponId==TEXT("WPN-GSW-001")?TEXT("裂碑重剑")
        : Player->WeaponId==TEXT("WPN-SPR-001")?TEXT("疾雨短枪"):TEXT("尺衡军剑");
    Text(WeaponName,788,35,Equipment.Bound?.65f:.8f,Cream);
    if(Equipment.Bound)
    {
        const auto& Backup=Equipment.Slots[1-Equipment.ActiveSlot];
        Text(Backup.InstanceId?FString::Printf(TEXT("备用 %s +%d"),*DungeonEquipmentLabels::Name(Backup.ContentId),Backup.Grade):TEXT("备用 空"),790,57,.42f,Muted);
    }
    if (Player->ComboStage > 0)
        Text(FString::Printf(TEXT("连段 %d / 3"),Player->ComboStage),790,69,.55f,Gold);
    else if(Player->GetWeaponSkillAction().Active) Text(DungeonEquipmentLabels::Skill(Player->WeaponId),790,69,.55f,Gold);
    const double SkillCooldown=Player->GetWeaponSkillCooldownRemaining();
    if(SkillCooldown>0) Text(FString::Printf(TEXT("武器技 %.1f秒"),SkillCooldown),790,87,.44f,Muted);
    int Alive=0; for(auto Enemy:Game->Enemies) if(Enemy&&!Enemy->bDead) ++Alive;
    Text(FString::Printf(TEXT("房间 %02d   /   敌人 %d"),Game->RoomNumber,Alive),1020,36,.7f,Muted);
    const FString Armor=Player->ArmorId==TEXT("ARM-LGT-001")?TEXT("轻甲"):Player->ArmorId==TEXT("ARM-MED-001")?TEXT("中甲")
        :Player->ArmorId==TEXT("ARM-HVY-001")?TEXT("重甲"):Player->ArmorId==TEXT("ARM-ROB-001")?TEXT("法袍"):TEXT("未装备甲");
    Text(Equipment.Bound&&Equipment.Slots[2].InstanceId?DungeonEquipmentLabels::Name(Equipment.Slots[2].ContentId):Armor,1020,68,.5f,Cream);
    Text(FString::Printf(TEXT("专注 %.0f  韧性 %.0f"),Player->Focus,Player->GetPoiseThreshold()),1020,87,.44f,Muted);
    Line(62,107,1218,107,FLinearColor(.40f,.34f,.22f,1),1);
    Text(TEXT("WASD / 方向键  移动"),68,674,.56f,Cream);
    Text(TEXT("空格  跳跃"),300,674,.56f,Cream);
    Text(TEXT("J / 左键  主攻"),465,674,.56f,Cream);
    Text(TEXT("K / 右键  武器技"),680,674,.56f,Cream);
    Text(TEXT("E  拾取 / 出口"),905,674,.53f,Cream);
    Text(TEXT("Q 切换  R 重开"),1095,674,.44f,Gold);
    if(!Game->LastMessage.IsEmpty()) Text(Game->LastMessage,244,126,.60f,Gold);
    DrawEquipmentPanel(Game);
    if(Game->bWaitingForStart)
    {
        Box(310,232,660,199,FLinearColor(.025f,.05f,.075f,.94f));
        Line(336,247,944,247,Gold,2);
        Text(TEXT("烬堡 · 地牢试炼"),449,266,1.3f,Cream);
        Text(TEXT("按 Enter 进入地牢"),481,334,.95f,Gold);
        Text(TEXT("先单人探索 · 二维角色与纵深战斗原型"),424,387,.63f,Muted);
    }
    if(Game->bRoomCleared&&!Game->bGameOver&&!Game->GetSceneInteractionView().NeedsConfirmation)
    {
        Box(360,198,560,73,FLinearColor(.025f,.07f,.08f,.9f));
        Text(TEXT("房间已清空"),533,207,1.0f,FLinearColor(.48f,.94f,.73f,1));
        Text(Game->GetSceneRoomView().Active?TEXT("探索后前往东侧出口，按 E 查看离开提示"):TEXT("拾取战利品，走到右侧出口按 E 继续"),409,241,.65f,Cream);
    }
    if(Game->GetSceneInteractionView().NeedsConfirmation&&!Game->bGameOver)
    {
        Box(303,220,674,220,FLinearColor(.025f,.05f,.065f,.97f));
        Line(327,238,953,238,Gold,2);
        Text(TEXT("前往下一个房间？"),451,258,1.04f,Cream);
        Text(TEXT("离开后无法返回，遗留物品不会带走。"),371,311,.70f,Muted);
        Text(TEXT("Enter · 离开       Esc · 继续探索"),411,373,.78f,Gold);
    }
    if(Game->bGameOver)
    {
        Box(0,160,1280,460,FLinearColor(.02f,.025f,.04f,.75f));
        Text(TEXT("本次冒险结束"),481,306,1.4f,Cream);
        Text(TEXT("按 R 再次出发"),530,369,.9f,Gold);
    }
}

void ADungeonHUD::DrawPlayerOcclusionOutline(ADungeonFighter* Player)
{
    if(!bUseCandidateSprites || !Player || Player->bDead || OutlineInstances.IsEmpty()) return;
    int32 Instance=0;
    const auto Project=[](const FActorQuad& Q,FVector2D UV)
    {
        const float A=FMath::DegreesToRadians(Q.Rotation),C=FMath::Cos(A),S=FMath::Sin(A);
        const FVector2D V=(UV-Q.Pivot)*Q.Size;
        return Q.Top+Q.Pivot*Q.Size+FVector2D(C*V.X-S*V.Y,S*V.X+C*V.Y);
    };
    // Original body / weapon / hand ordering remains. This pass only restores
    // a faint player image where a real, later-drawn enemy alpha occludes it.
    for(int32 PlayerQuadIndex=0;PlayerQuadIndex<ActorQuads.Num();++PlayerQuadIndex)
    {
        const auto& P=ActorQuads[PlayerQuadIndex];
        if(P.Owner.Get()!=Player || !P.Texture || P.Size<=0 || (P.Weapon&&!bUseReadabilityMaterial)) continue;
        FVector2D Min=Project(P,{0,0}),Max=Min;
        for(const FVector2D UV:{FVector2D(0,1),FVector2D(1,0),FVector2D(1,1)})
        {const auto V=Project(P,UV);Min.X=FMath::Min(Min.X,V.X);Min.Y=FMath::Min(Min.Y,V.Y);Max.X=FMath::Max(Max.X,V.X);Max.Y=FMath::Max(Max.Y,V.Y);}
        for(int32 EI=PlayerQuadIndex+1;EI<ActorQuads.Num() && Instance<OutlineInstances.Num();++EI)
        {
            const auto& E=ActorQuads[EI];auto Enemy=E.Owner.Get();
            if(!Enemy || !Enemy->bEnemy || E.Size<=0 || !E.Texture || E.Tint.A<=0) continue;
            if(Max.X<=E.Top.X || E.Top.X+E.Size<=Min.X || Max.Y<=E.Top.Y || E.Top.Y+E.Size<=Min.Y) continue;
            auto Material=OutlineInstances[Instance++].Get();
            Material->SetTextureParameterValue(TEXT("ActorSprite"),P.Texture);
            Material->SetTextureParameterValue(TEXT("OccluderSprite"),E.Texture);
            Material->SetScalarParameterValue(TEXT("ActorSpriteMirror"),Player->Facing<0?1.f:0.f);
            Material->SetScalarParameterValue(TEXT("OccluderSpriteMirror"),Enemy->Facing<0?1.f:0.f);
            Material->SetScalarParameterValue(TEXT("OutlineWidth"),(bUseReadabilityMaterial?(P.Weapon?1.f:1.4f):2.f)/P.Size);
            Material->SetScalarParameterValue(TEXT("OutlineOpacity"),bUseReadabilityMaterial?.8f:.9f);
            Material->SetScalarParameterValue(TEXT("OccludedFillOpacity"),P.Weapon?.5f:.28f);
            Material->SetScalarParameterValue(TEXT("OccluderOpacity"),E.Tint.A);
            Material->SetScalarParameterValue(TEXT("ActorOpacity"),P.Tint.A);
            Material->SetVectorParameterValue(TEXT("ActorTint"),P.Tint);
            Material->SetVectorParameterValue(TEXT("OutlineColor"),FLinearColor(.55f,.91f,1.f,1.f));
            const auto Zero=Project(P,{0,0});
            const auto X=(Project(P,{1,0})-Zero)/E.Size,Y=(Project(P,{0,1})-Zero)/E.Size;
            Material->SetVectorParameterValue(TEXT("OccluderUVAxisX"),FLinearColor(X.X,X.Y,0,0));
            Material->SetVectorParameterValue(TEXT("OccluderUVAxisY"),FLinearColor(Y.X,Y.Y,0,0));
            Material->SetScalarParameterValue(TEXT("OccluderUVScale"),P.Size/E.Size);
            Material->SetVectorParameterValue(TEXT("OccluderUVOffset"),FLinearColor((Zero.X-E.Top.X)/E.Size,(Zero.Y-E.Top.Y)/E.Size,0,0));
            DrawMaterial(Material,P.Top.X,P.Top.Y,P.Size,P.Size,0,0,1,1,1.f,false,P.Rotation,P.Pivot);
        }
    }
}

#include "DungeonWeaponPresentation.inl"

void ADungeonHUD::DrawHUD()
{
    ResetFairytaleSwordSecondaryDraw();
    FairytaleGuardMoveRigDraws.Reset(); // Every callback, including no-Canvas and early lookdev paths.
    FairytaleSwordAirDraw=FDungeonFairytaleSwordAirDrawV001();
    FairytaleSwordAirDraw.OptIn=bUseFairytaleSwordAirPreview;
    Super::DrawHUD(); if(!Canvas) return;
    CombatRangeDebugLineCount=0;
    ++CombatRangeProofFrame;
    if(bUseFairytaleLookdevPreview)
    {DrawFairytaleLookdev(Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this)));return;}
    RenderedTextDrawCalls=0;RenderedActorSpriteSizes.Reset();RenderedGuardRoomWarningSlots.Reset();RenderedNativeGuardEntityIds.Reset();FairytaleGuardDraws.Reset();FairytaleGuardFullDraws.Reset();
    UIScale=FMath::Min(Canvas->SizeX/1280.f,Canvas->SizeY/720.f);
    Origin=FVector2D((Canvas->SizeX-1280*UIScale)*.5f,(Canvas->SizeY-720*UIScale)*.5f);
    auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this));
    if(Game) UpdateRoomView(Game);
    if(Game) UpdateStoneFeedback(Game);
    if(Game) UpdateWorldWeaponFeedback(Game);
    DrawRoom(GetWorld()->GetTimeSeconds(),Game&&Game->bRoomCleared);
    if(!Game) { Text(TEXT("房间加载中"),555,400,1,DungeonPalette::Cream); return; }
    // Ground pickups are drawn behind fighter silhouettes and never move with jump height.
    for(const auto& Item:Game->Pickups)
    {
        if(Item.bConsumed) continue;
        const auto P=Ground(Item.Position);
        Oval(P.X-17,P.Y-4,34,9,FLinearColor(0,0,0,.30f));
        float Bob=FMath::Sin(GetWorld()->GetTimeSeconds()*3+Item.Position.X)*3;
        if(Item.Kind==TEXT("coin"))
        { Oval(P.X-10,P.Y-23+Bob,20,22,DungeonPalette::Gold); Line(P.X,P.Y-20+Bob,P.X,P.Y-5+Bob,FLinearColor(.48f,.29f,.1f,1),3); }
        else if(Item.Kind==TEXT("potion"))
        { Box(P.X-8,P.Y-22+Bob,16,20,FLinearColor(.75f,.20f,.26f,1)); Box(P.X-4,P.Y-29+Bob,8,8,DungeonPalette::Cream); }
        else
        { Line(P.X-13,P.Y-2+Bob,P.X+12,P.Y-31+Bob,DungeonPalette::Cream,5); Box(P.X+2,P.Y-34+Bob,23,15,DungeonPalette::Gold); }
        FString Label=Item.Kind==TEXT("coin")?TEXT("金币"):Item.Kind==TEXT("potion")?TEXT("药水"):TEXT("战斧");
        Text(Label,P.X-16,P.Y+11,.48f,DungeonPalette::Cream);
    }
    DrawEquipmentSources(Game);
    TArray<ADungeonFighter*> Sorted;
    if(Game->GetPlayerFighter()) Sorted.Add(Game->GetPlayerFighter());
    for(auto Enemy:Game->Enemies) if(Enemy) Sorted.Add(Enemy);
    Sorted.Sort([](const ADungeonFighter& A,const ADungeonFighter& B)
    {
        if (A.GetActorLocation().Y != B.GetActorLocation().Y) return A.GetActorLocation().Y > B.GetActorLocation().Y;
        return A.GetUniqueID() < B.GetUniqueID();
    });
    ActorQuads.Reset();
    MeleeTrails.Reset();
    DrawExplorationFog(GetWorld()->GetTimeSeconds());
    DrawWorldWeaponGround(Game);
    // World-space arrival warning reads the committed finite room plan only.
    // It never creates enemies, advances deadlines, changes fog or draws UI.
    FDungeonFirstBatchGuardRoomView Arrival;
    if(Game->QueryFirstBatchGuardRoom(Arrival))
    {
        const double Now=Game->GetSimulationTime();
        for(const auto& Slot:Arrival.Slots)
        {
            const double Age=Now-Slot.WarningAt;
            if(Slot.Stage!=EDungeonGuardRoomSlotStage::Warning || Slot.WarningAt<0. || Age<0. || Age>=1.2) continue;
            const float Visibility=float(GetCurrentVisibilityAt(Slot.SpawnPosition));
            const FVector2D P=Ground(Slot.SpawnPosition);
            if(Visibility<=.05f || P.X<20.f || P.X>1260.f || P.Y<24.f || P.Y>696.f) continue;
            const float T=float(Age/1.2),RX=26.f+7.f*T,RY=10.f+3.f*T;
            const float Pulse=.75f+.25f*FMath::Sin(float(Age)*20.f);
            const FLinearColor Amber(1.f,.61f,.16f,Visibility*(.45f+.35f*T)*Pulse);
            Oval(P.X-RX-2.f,P.Y-RY-1.f,2.f*RX+4.f,2.f*RY+2.f,FLinearColor(.08f,.07f,.05f,.35f*Visibility));
            for(int32 I=0;I<24;++I)
            {
                if(I%6==5) continue;
                const float A=2.f*PI*float(I)/24.f,B=2.f*PI*float(I+1)/24.f;
                Line(P.X+RX*FMath::Cos(A),P.Y+RY*FMath::Sin(A),P.X+RX*FMath::Cos(B),P.Y+RY*FMath::Sin(B),Amber,1.7f);
            }
            Line(P.X-9.f,P.Y+2.f,P.X-2.f,P.Y-4.f,Amber,1.5f);
            Line(P.X-2.f,P.Y-4.f,P.X+3.f,P.Y+2.f,Amber,1.5f);
            Line(P.X+3.f,P.Y+2.f,P.X+11.f,P.Y-1.f,Amber,1.5f);
            RenderedGuardRoomWarningSlots.Add(Slot.SlotId);
        }
    }
    for(auto F:Sorted) if(!F->bEnemy || GetCurrentVisibilityAt(F->GetGroundPosition())>.05) DrawStoneTelegraph(F);
    struct FDepthEntry { double GroundY;ADungeonFighter* Fighter=nullptr;const FDungeonWorldProjectile* Projectile=nullptr; };
    TArray<FDepthEntry> Entries;
    for(auto F:Sorted) Entries.Add({F->GetGroundPosition().Y,F,nullptr});
    for(const auto& P:Game->GetWeaponWorldState().Projectiles)
        if(P.Active && P.Key.RoomInstanceId==Game->GetWeaponWorldState().RoomInstanceId) Entries.Add({P.Position.Y,nullptr,&P});
    Entries.Sort([](const FDepthEntry& A,const FDepthEntry& B)
    {
        if(A.GroundY!=B.GroundY) return A.GroundY>B.GroundY;
        if(A.Fighter && B.Fighter) return A.Fighter->GetUniqueID()<B.Fighter->GetUniqueID();
        if(A.Fighter || B.Fighter) return A.Fighter!=nullptr;
        const auto& X=A.Projectile->Key;const auto& Y=B.Projectile->Key;
        if(X.OwnerId!=Y.OwnerId) return X.OwnerId<Y.OwnerId;
        if(X.ActionId!=Y.ActionId) return X.ActionId<Y.ActionId;
        return X.EventId<Y.EventId;
    });
    for(const auto& Entry:Entries)
        if(auto Fighter=Entry.Fighter)
        {if(!Fighter->bEnemy || GetCurrentVisibilityAt(Fighter->GetGroundPosition())>.05) DrawFighter(Fighter);}
        else DrawWorldWeaponProjectile(*Entry.Projectile,Game->GetSimulationTime());
    DrawPlayerOcclusionOutline(Game->GetPlayerFighter());
    // Short-lived swing effects remain visible at contact; body and equipment
    // still keep their real ground-depth order. This pass never creates hits.
    for(const auto& Trail:MeleeTrails)
        if(auto Fighter=Trail.Owner.Get()) DrawMeleeTrail(Fighter,Trail.Clip,Trail.Frame,Trail.Size,Trail.CandidateWeapon);
    DrawWorldWeaponFeedback(Game);
    if(bShowInterface) DrawInterface(Game);
    if(bCombatRangeProof)
        UE_LOG(LogTemp,Display,TEXT("CombatRangeProof frame=%llu sim=%.17g enabled=%d lines=%d"),
            CombatRangeProofFrame,Game->GetSimulationTime(),int32(bCombatRangeDebug),CombatRangeDebugLineCount);
}

void ADungeonHUD::BeginFairytaleLookdev()
{
    bShowInterface=false;
    bUseFairytaleWalkLookdevPreview=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleWalkLookdev"));
    bUseFairytaleChestLookdevPreview=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleChestLookdev"));
    bUseFairytaleShoulderLookdevPreview=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleShoulderLookdev"));
    bUseFairytaleLimbLookdevPreview=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLimbLookdev"));
    const auto LoadRoom=[](const FString& Name)->UTexture2D*
    {
        const FString Package=TEXT("/Game/Production/RoomArt/v001/")+Name;
        return FPackageName::DoesPackageExist(Package)?LoadObject<UTexture2D>(nullptr,*(Package+TEXT(".")+Name)):nullptr;
    };
    RoomFarBackground=LoadRoom(TEXT("T_RoomFar_v001"));
    RoomMidBackground=LoadRoom(TEXT("T_RoomMid_v001"));
    RoomFloorTexture=LoadRoom(TEXT("T_RoomFloor_v001"));
    GetScenePropTexture(true);GetScenePropTexture(false);
    for(const bool Stone:{false,true})
    {
        const bool Walk=!Stone&&bUseFairytaleWalkLookdevPreview;
        const int32 Count=Walk?DungeonFairytaleLookdev::HeroWalkFrameCount:4;
        for(int32 Frame=0;Frame<Count;++Frame)
        {
            const FString Path=Walk?DungeonFairytaleLookdev::HeroWalkPath(Frame):DungeonFairytaleLookdev::Path(Stone,Frame);
            const FString Package=Path.Left(Path.Find(TEXT(".")));
            if(FPackageName::DoesPackageExist(Package))
                if(auto Texture=LoadObject<UTexture2D>(nullptr,*Path))Frames.Add(Path,Texture);
        }
    }
    if(bUseFairytaleChestLookdevPreview)
        for(int32 Frame=0;Frame<4;++Frame)
        {
            const FString Path=DungeonFairytaleLookdev::HeroChestPath(Frame);
            if(auto Texture=LoadObject<UTexture2D>(nullptr,*Path))Frames.Add(Path,Texture);
        }
    if(bUseFairytaleShoulderLookdevPreview)
        for(const bool Near:{false,true})for(int32 Frame=0;Frame<4;++Frame)
        {
            const FString Path=DungeonFairytaleLookdev::HeroShoulderPath(Near,Frame);
            if(auto Texture=LoadObject<UTexture2D>(nullptr,*Path))Frames.Add(Path,Texture);
        }
    if(bUseFairytaleLimbLookdevPreview)
        for(const bool Bracer:{false,true})for(int32 Frame=0;Frame<4;++Frame)
        {
            const FString Path=DungeonFairytaleLookdev::HeroNearLimbPath(Bracer,Frame);
            if(auto Texture=LoadObject<UTexture2D>(nullptr,*Path))Frames.Add(Path,Texture);
        }
    FlushRenderingCommands();
    if(FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLookdevProof")))
    {
        // DungeonContentProof is only the unchanged native screenshot install contract here.
        // The early return in BeginPlay prevents the old ContentProbe/old proof fixture.
        InstallFastLosslessProofScreenshots();
        GetWorld()->SpawnActor<ADungeonFairytaleLookdevProbe>();
    }
}

void ADungeonHUD::DrawFairytaleLookdev(ADungeonGameMode* Game)
{
    RenderedTextDrawCalls=0;RenderedActorSpriteSizes.Reset();
    RenderedPlayerDrawStack.Reset();RenderedArmorLayerPaths.Reset();ActorQuads.Reset();MeleeTrails.Reset();
    bRenderedArmorLayersUsed=false;bRenderedWeaponBodyUsed=false;
    RenderedPlayerTexturePath.Reset();RenderedPlayerSpriteSize=0.f;
    UIScale=FMath::Min(Canvas->SizeX/1280.f,Canvas->SizeY/720.f);
    Origin=FVector2D((Canvas->SizeX-1280*UIScale)*.5f,(Canvas->SizeY-720*UIScale)*.5f);
    const uint64 Serial=FairytaleLookdevDraw.Serial+1;
    FairytaleLookdevDraw=FFairytaleLookdevDraw();FairytaleLookdevDraw.Serial=Serial;
    FairytaleLookdevDraw.Wall=FPlatformTime::Seconds();
    FairytaleLookdevDraw.UIScale=UIScale;FairytaleLookdevDraw.Viewport={double(Canvas->SizeX),double(Canvas->SizeY)};
    if(Game)UpdateRoomView(Game);
    DrawRoom(GetWorld()->GetTimeSeconds(),false);
    DrawExplorationFog(GetWorld()->GetTimeSeconds());
    if(!Game||!Game->IsFairytaleLookdevPreview()||!Game->GetPlayerFighter())return;
    FairytaleLookdevDraw.Active=true;
    FairytaleLookdevDraw.HeroWalkActive=bUseFairytaleWalkLookdevPreview;
    FairytaleLookdevDraw.HeroChestActive=bUseFairytaleChestLookdevPreview;
    FairytaleLookdevDraw.HeroShoulderActive=bUseFairytaleShoulderLookdevPreview;
    FairytaleLookdevDraw.HeroNearLimbActive=bUseFairytaleLimbLookdevPreview;
    if(bUseFairytaleChestLookdevPreview)
        if(auto Controller=UGameplayStatics::GetPlayerController(this,0))
        {
            // W/C select presentation-only position and chest visibility. They
            // never move/equip the frozen Fighter or alter its fog memory.
            FairytaleLookdevDraw.HeroDarkPosition=Controller->IsInputKeyDown(EKeys::W);
            FairytaleLookdevDraw.ChestVisibleChoice=Controller->IsInputKeyDown(EKeys::C);
            if(bUseFairytaleShoulderLookdevPreview)
            {
                FairytaleLookdevDraw.NearShoulderOnly=Controller->IsInputKeyDown(EKeys::N);
                FairytaleLookdevDraw.FarShoulderOnly=Controller->IsInputKeyDown(EKeys::F);
            }
        }
    if(bUseFairytaleLimbLookdevPreview)
    {
        // Existing body/chest/two shoulders are the constant comparison baseline.
        FairytaleLookdevDraw.ChestVisibleChoice=true;
        FairytaleLookdevDraw.NearShoulderOnly=false;FairytaleLookdevDraw.FarShoulderOnly=false;
        if(auto Controller=UGameplayStatics::GetPlayerController(this,0))
        {
            FairytaleLookdevDraw.LimbVisibleChoice=Controller->IsInputKeyDown(EKeys::L);
            FairytaleLookdevDraw.NearBracerOnly=FairytaleLookdevDraw.LimbVisibleChoice&&Controller->IsInputKeyDown(EKeys::B);
            FairytaleLookdevDraw.NearShinOnly=FairytaleLookdevDraw.LimbVisibleChoice&&Controller->IsInputKeyDown(EKeys::G);
        }
    }
    FairytaleLookdevDraw.ConfigurationConfirmed=DungeonFairytaleLookdev::StoneMeasurementsConfirmed
        &&!(bUseFairytaleWalkLookdevPreview&&bUseFairytaleChestLookdevPreview)
        &&(!bUseFairytaleShoulderLookdevPreview||bUseFairytaleChestLookdevPreview)
        &&(!bUseFairytaleLimbLookdevPreview||(bUseFairytaleChestLookdevPreview&&bUseFairytaleShoulderLookdevPreview))
        &&!(FairytaleLookdevDraw.NearBracerOnly&&FairytaleLookdevDraw.NearShinOnly);
    const double Elapsed=FairytaleLookdevDraw.Wall-Game->GetFairytaleLookdevEpoch();
    FairytaleLookdevDraw.AnimationElapsed=Elapsed;
    if(DungeonFairytaleLookdev::Sample(Elapsed)<0)return;
    const auto DrawActor=[&](bool Stone,FFairytaleLookdevActorDraw& Record)
    {
        const bool Walk=!Stone&&bUseFairytaleWalkLookdevPreview;
        Record.Clip=Walk?TEXT("walk"):TEXT("idle");
        Record.Sample=Walk?DungeonFairytaleLookdev::HeroWalkSample(Elapsed):DungeonFairytaleLookdev::Sample(Elapsed);
        Record.Frame=int32(Record.Sample%(Walk?DungeonFairytaleLookdev::HeroWalkFrameCount:4));
        Record.NativeFacing=Stone?-1:1;
        Record.Facing=Stone?-Game->GetFairytaleLookdevFacing():Game->GetFairytaleLookdevFacing();
        Record.Flipped=Record.Facing!=Record.NativeFacing;
        Record.Root=DungeonFairytaleLookdev::Root(Stone,Record.Frame);
        Record.CanvasSize=Stone?DungeonFairytaleLookdev::StoneCanvas:DungeonFairytaleLookdev::HeroCanvas;
        // Observation anchors, inverse-projected onto the existing ground plane.
        // They never change a Fighter's physical ground position or Facing.
        const FVector2D Anchor=Stone?FVector2D(819.2,540.):
            FairytaleLookdevDraw.HeroDarkPosition?FVector2D(190.,590.):FVector2D(435.2,540.);
        Record.Ground={CameraX+(Anchor.X-640.)/.65,(490.-Anchor.Y)/.38};
        const auto Projected=Ground(Record.Ground);Record.GroundScreen=Screen(Projected.X,Projected.Y);
        const double RootX=Record.Flipped?512.-Record.Root.X:Record.Root.X;
        Record.TopScreen=Screen(Projected.X-Record.CanvasSize*RootX/512.,Projected.Y-Record.CanvasSize*Record.Root.Y/512.);
        const FString ExpectedPath=Walk?DungeonFairytaleLookdev::HeroWalkPath(Record.Frame):DungeonFairytaleLookdev::Path(Stone,Record.Frame);
        UTexture2D* Texture=Frames.FindRef(ExpectedPath);
        Record.TextureReady=Texture&&Texture->GetResource()&&Texture->GetSizeX()==512&&Texture->GetSizeY()==512
            &&(!Stone||DungeonFairytaleLookdev::StoneMeasurementsConfirmed)&&Record.CanvasSize>0.;
        if(!Record.TextureReady)return; // No legacy sprite/fighter/weapon fallback.
        Record.TexturePath=Texture->GetPathName();
        Oval(Projected.X-Record.CanvasSize*.18,Projected.Y-2.,Record.CanvasSize*.36,5.,FLinearColor(0,0,0,.3f));
        DrawTexture(Texture,Record.TopScreen.X,Record.TopScreen.Y,Record.CanvasSize*UIScale,Record.CanvasSize*UIScale,
            Record.Flipped?1.f:0.f,0.f,Record.Flipped?-1.f:1.f,1.f,FLinearColor::White);
        const auto DrawShoulder=[&](bool Near)
        {
            if(Stone||!bUseFairytaleShoulderLookdevPreview)return;
            auto Shoulder=Frames.FindRef(DungeonFairytaleLookdev::HeroShoulderPath(Near,Record.Frame));
            bool& Ready=Near?Record.NearShoulderReady:Record.FarShoulderReady;
            bool& Drawn=Near?Record.NearShoulderDrawn:Record.FarShoulderDrawn;
            FString& Path=Near?Record.NearShoulderTexturePath:Record.FarShoulderTexturePath;
            Ready=Shoulder&&Shoulder->GetResource()&&Shoulder->GetSizeX()==512&&Shoulder->GetSizeY()==512;
            if(!Ready)return;
            Path=Shoulder->GetPathName();
            if(!FairytaleLookdevDraw.ChestVisibleChoice)return;
            if((FairytaleLookdevDraw.NearShoulderOnly&&!Near)||(FairytaleLookdevDraw.FarShoulderOnly&&Near))return;
            DrawTexture(Shoulder,Record.TopScreen.X,Record.TopScreen.Y,Record.CanvasSize*UIScale,Record.CanvasSize*UIScale,
                Record.Flipped?1.f:0.f,0.f,Record.Flipped?-1.f:1.f,1.f,FLinearColor::White);
            Drawn=true;
        };
        DrawShoulder(false); // Actual separate far plate over its sleeve, below the chest strap.
        if(!Stone&&bUseFairytaleChestLookdevPreview)
        {
            UTexture2D* Chest=Frames.FindRef(DungeonFairytaleLookdev::HeroChestPath(Record.Frame));
            Record.ChestTextureReady=Chest&&Chest->GetResource()&&Chest->GetSizeX()==512&&Chest->GetSizeY()==512;
            if(Record.ChestTextureReady)
            {
                Record.ChestTexturePath=Chest->GetPathName();
                if(FairytaleLookdevDraw.ChestVisibleChoice||bUseFairytaleShoulderLookdevPreview)
                {
                    DrawTexture(Chest,Record.TopScreen.X,Record.TopScreen.Y,Record.CanvasSize*UIScale,Record.CanvasSize*UIScale,
                        Record.Flipped?1.f:0.f,0.f,Record.Flipped?-1.f:1.f,1.f,FLinearColor::White);
                    Record.ChestDrawn=true;
                }
            }
        }
        DrawShoulder(true);
        const auto DrawNearLimb=[&](bool Bracer)
        {
            if(Stone||!bUseFairytaleLimbLookdevPreview)return;
            auto LimbTexture=Frames.FindRef(DungeonFairytaleLookdev::HeroNearLimbPath(Bracer,Record.Frame));
            bool& Ready=Bracer?Record.NearBracerReady:Record.NearShinReady;
            bool& Drawn=Bracer?Record.NearBracerDrawn:Record.NearShinDrawn;
            FString& Path=Bracer?Record.NearBracerTexturePath:Record.NearShinTexturePath;
            int32& Frame=Bracer?Record.NearBracerFrame:Record.NearShinFrame;
            Ready=LimbTexture&&LimbTexture->GetResource()&&LimbTexture->GetSizeX()==512&&LimbTexture->GetSizeY()==512;
            if(!Ready)return;Path=LimbTexture->GetPathName();Frame=Record.Frame;
            if(!FairytaleLookdevDraw.LimbVisibleChoice||FairytaleLookdevDraw.NearBracerOnly&&FairytaleLookdevDraw.NearShinOnly)return;
            if((FairytaleLookdevDraw.NearBracerOnly&&!Bracer)||(FairytaleLookdevDraw.NearShinOnly&&Bracer))return;
            DrawTexture(LimbTexture,Record.TopScreen.X,Record.TopScreen.Y,Record.CanvasSize*UIScale,Record.CanvasSize*UIScale,
                Record.Flipped?1.f:0.f,0.f,Record.Flipped?-1.f:1.f,1.f,FLinearColor::White);
            Drawn=true;
        };
        DrawNearLimb(false);DrawNearLimb(true);
    };
    DrawActor(false,FairytaleLookdevDraw.Hero);DrawActor(true,FairytaleLookdevDraw.Stone);
}
