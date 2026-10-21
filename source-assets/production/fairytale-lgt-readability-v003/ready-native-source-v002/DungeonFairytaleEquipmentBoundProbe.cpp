#include "DungeonFairytaleEquipmentBoundProbe.h"
#include "DungeonHUD.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonFairytaleSwordEquipmentBinding.h"
#include "DungeonFairytaleSwordBodyV001.inl"
#include "DungeonProofScreenshots.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Kismet/GameplayStatics.h"
#include "UnrealClient.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "Misc/App.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformTime.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
namespace
{
using FObject=TSharedPtr<FJsonObject>;
void BoundNumber(FObject Object,const TCHAR* Name,uint64 Value)
{Object->SetStringField(Name,FString::Printf(TEXT("%llu"),(unsigned long long)Value));}
TArray<TSharedPtr<FJsonValue>> BoundXY(FVector2D Point)
{return {MakeShared<FJsonValueNumber>(Point.X),MakeShared<FJsonValueNumber>(Point.Y)};}
const DungeonEquipmentInventory::FItem* BoundItem(const ADungeonGameMode& G,uint64 Id)
{const auto* Inventory=G.GetEquipmentInventoryState();if(Inventory)for(const auto& Item:Inventory->Items)if(Item.InstanceId==Id)return &Item;return nullptr;}
const FDungeonEquipmentSourceView* BoundSource(const ADungeonGameMode& G,uint64 Id)
{for(const auto& Source:G.GetEquipmentSources())if(Source.SourceId==Id)return &Source;return nullptr;}
uint64 BoundGroundSource(const ADungeonGameMode& G,uint64 Id)
{for(const auto& Source:G.GetEquipmentSources())if(!Source.Consumed&&Source.InstanceId==Id)return Source.SourceId;return 0;}
}
ADungeonFairytaleEquipmentBoundProbe::ADungeonFairytaleEquipmentBoundProbe(){PrimaryActorTick.bCanEverTick=true;}
ADungeonGameMode* ADungeonFairytaleEquipmentBoundProbe::Game()const
{return GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;}
APlayerController* ADungeonFairytaleEquipmentBoundProbe::Controller()const
{return UGameplayStatics::GetPlayerController(this,0);}
ADungeonHUD* ADungeonFairytaleEquipmentBoundProbe::HUD()const
{auto C=Controller();return C?Cast<ADungeonHUD>(C->GetHUD()):nullptr;}
const TCHAR* ADungeonFairytaleEquipmentBoundProbe::StepName()const
{
    static const TCHAR* Names[]={TEXT("start"),TEXT("baseline_no_armor"),TEXT("light_pending_cancel"),TEXT("light_canceled"),
        TEXT("light_pickup_commit"),TEXT("light_ready"),TEXT("light_three_stage"),TEXT("medium_selection"),TEXT("medium_commit"),
        TEXT("medium_unsupported_ready"),TEXT("original_light_retake_selection"),TEXT("original_light_retake_commit"),TEXT("original_light_retaken_ready"),TEXT("complete")};
    return Step>=0&&Step<14?Names[Step]:TEXT("invalid");
}
void ADungeonFairytaleEquipmentBoundProbe::Next(int32 Value)
{
    auto Entry=MakeShared<FJsonObject>();Entry->SetStringField(TEXT("phase"),StepName());Entry->SetNumberField(TEXT("step"),Step);
    Entry->SetNumberField(TEXT("wall_offset_s"),FPlatformTime::Seconds()-CaptureStart);
    if(auto G=Game()){Entry->SetNumberField(TEXT("sim"),G->GetSimulationTime());BoundNumber(Entry,TEXT("revision"),G->GetEquipmentView().Revision);}
    PhaseChecks.Add(MakeShared<FJsonValueObject>(Entry));Step=Value;StepStart=FPlatformTime::Seconds();
}
void ADungeonFairytaleEquipmentBoundProbe::BeginPlay()
{
    Super::BeginPlay();GIsDumpingMovie=0;WarmStart=FPlatformTime::Seconds();
    LeatherReadyOnly=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherReadyOnlyProof"));
    if(LeatherReadyOnly&&!FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherReadyPreview")))
    {Finish(TEXT("leather_ready_only_requires_explicit_leather_art_flag"));return;}
    if(!FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),Directory)||Directory.IsEmpty())
    {Finish(TEXT("missing_directory"));return;}
    Directory=FPaths::ConvertRelativePathToFull(Directory);
    TArray<FString> Prior;IFileManager::Get().FindFiles(Prior,*(Directory/TEXT("MovieFrame*.png")),true,false);
    if(Prior.Num()||IFileManager::Get().FileExists(*(Directory/TEXT("runtime-report.json")))||IFileManager::Get().FileExists(*(Directory/TEXT("prewarm-viewport.png"))))
    {Stopped=true;FPlatformMisc::RequestExit(false);return;}
    IFileManager::Get().MakeDirectory(*Directory,true);GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Directory;
    if(!FParse::Param(FCommandLine::Get(),DungeonFairytaleSwordEquipmentBinding::CommandLineFlag))
    {Finish(TEXT("Bound_renderer_flag_required_even_for_expected_RED"));return;}
    if(auto C=Controller())C->AddTickPrerequisiteActor(this);
    FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonFairytaleEquipmentBoundProbe::ScreenshotProcessed);
}
void ADungeonFairytaleEquipmentBoundProbe::Key(FKey Code,bool Down)
{
    if(Keys.FindRef(Code)==Down)return;
    if(auto C=Controller())
    {
        C->InputKey(FInputKeyParams(Code,Down?IE_Pressed:IE_Released,Down?1.:0.));Keys.Add(Code,Down);
        auto Input=MakeShared<FJsonObject>();Input->SetStringField(TEXT("key"),Code.ToString());Input->SetBoolField(TEXT("down"),Down);
        Input->SetNumberField(TEXT("wall_offset_s"),Started?FPlatformTime::Seconds()-CaptureStart:0.);
        if(auto G=Game())Input->SetNumberField(TEXT("sim"),G->GetSimulationTime());Inputs.Add(MakeShared<FJsonValueObject>(Input));
    }
}
bool ADungeonFairytaleEquipmentBoundProbe::CanPulse()const
{return !PulseKey.IsValid()&&FPlatformTime::Seconds()>=NeutralUntil;}
bool ADungeonFairytaleEquipmentBoundProbe::Pulse(FKey Code)
{if(!CanPulse())return false;Key(Code,true);PulseKey=Code;PulseReleaseAt=FPlatformTime::Seconds()+.08;return true;}
void ADungeonFairytaleEquipmentBoundProbe::Mismatch(const FString& Reason,int32 Observation)
{
    const FString Unique=FString::Printf(TEXT("%d:"),Step)+Reason;if(MismatchKeys.Contains(Unique))return;MismatchKeys.Add(Unique);
    auto Entry=MakeShared<FJsonObject>();Entry->SetStringField(TEXT("phase"),StepName());Entry->SetStringField(TEXT("reason"),Reason);
    Entry->SetNumberField(TEXT("first_observation"),Observation);Mismatches.Add(MakeShared<FJsonValueObject>(Entry));
}
void ADungeonFairytaleEquipmentBoundProbe::ScreenshotProcessed()
{
    if(Stopped)return;
    if(Prewarm&&!Started)
    {
        if(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))<=8){Finish(TEXT("prewarm_file_missing"));return;}
        CaptureStart=StepStart=FPlatformTime::Seconds();Started=true;GIsDumpingMovie=-1;return;
    }
    if(!Started)return;
    auto G=Game();auto H=HUD();auto P=G?G->GetPlayerFighter():nullptr;
    if(!G||!H||!P){Finish(TEXT("actual_native_owner_or_HUD_missing"));return;}
    const auto* Inventory=G->GetEquipmentInventoryState();if(!Inventory){Finish(TEXT("actual_committed_inventory_missing"));return;}
    const auto& V=G->GetEquipmentView();if(V.ActiveSlot<0||V.ActiveSlot>1){Finish(TEXT("actual_slot_out_of_range"));return;}
    const auto& D=H->GetFairytaleSwordDraw();const int32 Observation=Observations.Num();
    auto R=MakeShared<FJsonObject>();const double At=FPlatformTime::Seconds()-CaptureStart;Offsets.Add(MakeShared<FJsonValueNumber>(At));
    R->SetNumberField(TEXT("wall_offset_s"),At);R->SetStringField(TEXT("flow_phase"),StepName());R->SetNumberField(TEXT("flow_step"),Step);
    R->SetBoolField(TEXT("active"),D.Active);R->SetBoolField(TEXT("supported"),D.Supported);R->SetBoolField(TEXT("texture_ready"),D.TextureReady);
    R->SetBoolField(TEXT("armor_preview"),D.ArmorPreview);R->SetBoolField(TEXT("armor_ready"),D.ArmorReady);R->SetBoolField(TEXT("armor_drawn"),D.ArmorDrawn);
    BoundNumber(R,TEXT("draw_id"),D.DrawId);BoundNumber(R,TEXT("action_id"),D.ActionId);BoundNumber(R,TEXT("instance_id"),D.InstanceId);
    R->SetNumberField(TEXT("sim"),D.SimulationTime);R->SetNumberField(TEXT("actual_sim"),G->GetSimulationTime());
    R->SetNumberField(TEXT("start"),D.ActionStart);R->SetNumberField(TEXT("active_at"),D.ActiveAt);R->SetNumberField(TEXT("active_end"),D.ActiveEnd);R->SetNumberField(TEXT("end"),D.ActionEnd);
    R->SetNumberField(TEXT("body_max_contract"),72.);
    R->SetNumberField(TEXT("canvas_size"),D.CanvasSize);R->SetNumberField(TEXT("weapon_angle"),D.WeaponAngle);R->SetNumberField(TEXT("weapon_scale"),D.WeaponScale);R->SetNumberField(TEXT("weapon_width"),D.WeaponWidth);
    R->SetNumberField(TEXT("facing"),D.Facing);R->SetNumberField(TEXT("frame"),D.Frame);R->SetNumberField(TEXT("stage"),D.Stage);
    R->SetStringField(TEXT("clip"),D.Clip);R->SetStringField(TEXT("texture"),D.TexturePath);R->SetStringField(TEXT("weapon"),D.WeaponPath);
    R->SetStringField(TEXT("screenshot_request"),D.NativeScreenshotPath);R->SetArrayField(TEXT("root"),BoundXY(D.Root));R->SetArrayField(TEXT("grip"),BoundXY(D.Grip));R->SetArrayField(TEXT("grip_screen"),BoundXY(D.GripScreen));
    R->SetBoolField(TEXT("interface_visible"),H->GetInterfaceVisible());R->SetNumberField(TEXT("text_calls"),H->GetRenderedTextDrawCalls());
    R->SetStringField(TEXT("run"),V.RunGuid.ToString(EGuidFormats::Digits).ToLower());BoundNumber(R,TEXT("run_alias"),V.RunAlias);BoundNumber(R,TEXT("owner_id"),V.OwnerId);BoundNumber(R,TEXT("revision"),V.Revision);
    R->SetNumberField(TEXT("active_slot"),V.ActiveSlot);BoundNumber(R,TEXT("committed_weapon_id"),V.Slots[V.ActiveSlot].InstanceId);BoundNumber(R,TEXT("committed_weapon_version"),V.Slots[V.ActiveSlot].Version);
    BoundNumber(R,TEXT("committed_armor_id"),V.Slots[2].InstanceId);BoundNumber(R,TEXT("committed_armor_version"),V.Slots[2].Version);
    R->SetStringField(TEXT("weapon_mirror"),P->WeaponId);R->SetStringField(TEXT("armor_mirror"),P->ArmorId);
    R->SetBoolField(TEXT("pending_equipment_action"),V.Action.Active);BoundNumber(R,TEXT("pending_instance_id"),V.Action.InstanceId);
    R->SetNumberField(TEXT("equipment_deadline"),V.Action.Deadline);R->SetBoolField(TEXT("needs_slot_selection"),V.NeedsSlotSelection);R->SetNumberField(TEXT("selection_slot"),V.SelectionSlot);
    BoundNumber(R,TEXT("selected_source_id"),V.SelectedSourceId);
    BoundNumber(R,TEXT("next_operation_id"),V.NextOperationId);BoundNumber(R,TEXT("operation_count"),static_cast<uint64>(Inventory->Operations.size()));
    BoundNumber(R,TEXT("next_crit"),V.NextCritDraw);R->SetArrayField(TEXT("ground"),BoundXY(P->GetGroundPosition()));R->SetStringField(TEXT("animation"),P->AnimationName);
    R->SetBoolField(TEXT("melee_pending_primary"),P->GetMeleeCombatState().PendingPrimary);
    TArray<TSharedPtr<FJsonValue>> Stack;bool HasArmor=false;
    for(const auto& Path:D.DrawStack){Stack.Add(MakeShared<FJsonValueString>(Path));HasArmor|=Path.Contains(TEXT("Shoulder"))||Path.Contains(TEXT("Chest"));}
    R->SetArrayField(TEXT("draw_stack"),Stack);R->SetBoolField(TEXT("draw_stack_has_armor"),HasArmor);
    const bool NoArmor=Inventory->Armor==0,Light=LightId&&Inventory->Armor==LightId,Medium=MediumId&&Inventory->Armor==MediumId;
    R->SetStringField(TEXT("expected_armor_mode"),NoArmor?TEXT("no_armor"):Light?TEXT("light_armor"):Medium?TEXT("unsupported_medium"):TEXT("unexpected"));
    // This expectation is derived from committed native owners, not future
    // DrawState flags or the production resolver. Pending target does not equip.
    const bool ActualPickup=V.Action.Active&&(V.Action.Kind==EDungeonEquipmentActionKind::PickupArmor
        ||V.Action.Kind==EDungeonEquipmentActionKind::PickupWeapon);
    const auto& ActualMelee=P->GetMeleeCombatState();
    const bool RetainPending=ActualPickup&&(NoArmor||Light)&&!P->bDead&&ActualMelee.Grounded
        &&P->JumpHeight==0.f&&P->GetVerticalVelocity()==0.f&&!ActualMelee.Action.Active
        &&!P->GetWeaponSkillAction().Active&&P->GetDodgeState().Phase==DungeonDodge::EPhase::Idle
        &&((V.Action.Kind==EDungeonEquipmentActionKind::PickupArmor&&P->AnimationName==TEXT("equip_armor"))
            ||(V.Action.Kind==EDungeonEquipmentActionKind::PickupWeapon&&P->AnimationName==TEXT("equip_weapon")));
    R->SetBoolField(TEXT("committed_gear_placeholder_expected"),RetainPending);
    R->SetNumberField(TEXT("pending_equipment_kind"),int32(V.Action.Kind));
    if(!D.Active||!D.TextureReady)Mismatch(TEXT("draw_inactive_or_resource_not_ready"),Observation);
    if(!FMath::IsNearlyEqual(D.CanvasSize,DungeonFairytaleSwordBodyV001::CanvasSize,1.e-9)||H->GetInterfaceVisible()||H->GetRenderedTextDrawCalls()!=0)Mismatch(TEXT("source_canvas_or_UIoff_contract_changed"),Observation);
    if(!FMath::IsNearlyEqual(D.SimulationTime,G->GetSimulationTime(),1.e-9))Mismatch(TEXT("draw_and_committed_owner_clock_differ"),Observation);
    if(Inventory->RunId!=V.RunAlias||Inventory->OwnerId!=V.OwnerId||Inventory->Revision!=V.Revision||Inventory->ActiveSlot!=V.ActiveSlot||Inventory->Armor!=V.Slots[2].InstanceId)
        Mismatch(TEXT("actual_view_inventory_ownership_inconsistent"),Observation);
    const auto* ActualWeapon=BoundItem(*G,V.Slots[V.ActiveSlot].InstanceId);const auto* ActualArmor=BoundItem(*G,Inventory->Armor);
    if(!ActualWeapon||ActualWeapon->Version!=V.Slots[V.ActiveSlot].Version||P->WeaponId!=V.Slots[V.ActiveSlot].ContentId
        ||(Inventory->Armor&&(!ActualArmor||ActualArmor->Version!=V.Slots[2].Version||P->ArmorId!=V.Slots[2].ContentId))
        ||(!Inventory->Armor&&(V.Slots[2].Version!=0||!V.Slots[2].ContentId.IsEmpty()||!P->ArmorId.IsEmpty())))
        Mismatch(TEXT("actual_item_version_or_mirror_inconsistent"),Observation);
    if(NoArmor&&(D.ArmorDrawn||HasArmor))Mismatch(TEXT("actual_no_armor_is_dressed_by_art_flags"),Observation);
    if(Light&&D.Supported&&(!D.ArmorDrawn||!HasArmor||!D.ArmorReady||D.WeaponPath.IsEmpty()||D.DrawStack.Num()!=(D.Clip==TEXT("sword_ready_idle")?7:8)))
        Mismatch(TEXT("actual_light_missing_current_matching_stack"),Observation);
    if((NoArmor||Light)&&D.Supported&&(D.WeaponPath.IsEmpty()||D.InstanceId!=SwordId))Mismatch(TEXT("supported_actual_sword_missing_or_wrong_instance"),Observation);
    if(Medium&&(D.Supported||D.ArmorDrawn||HasArmor||!D.WeaponPath.IsEmpty()))Mismatch(TEXT("unsupported_medium_is_falsely_drawn_as_sword_or_light"),Observation);
    if(!NoArmor&&!Light&&!Medium)Mismatch(TEXT("unexpected_actual_armor_instance"),Observation);
    if(RetainPending)
    {
        if(D.Supported)Mismatch(TEXT("pending_pickup_falsely_claims_supported_action_pose"),Observation);
        if(D.Clip!=TEXT("sword_ready_idle")||D.Frame!=0||D.WeaponPath.IsEmpty()||D.InstanceId!=SwordId)
            Mismatch(TEXT("pending_pickup_loses_committed_sword_Ready0_placeholder"),Observation);
        if(Light&&(!D.ArmorDrawn||!HasArmor||!D.ArmorReady||D.DrawStack.Num()!=7))
            Mismatch(TEXT("pending_pickup_loses_committed_light_Ready0_placeholder"),Observation);
        if(NoArmor&&(D.ArmorDrawn||HasArmor||D.DrawStack.Num()!=3))
            Mismatch(TEXT("pending_no_armor_placeholder_substitutes_armor_or_wrong_stack"),Observation);
    }
    if((NoArmor||Light)&&!D.Supported&&!RetainPending&&(D.ArmorDrawn||HasArmor||!D.WeaponPath.IsEmpty()))
        Mismatch(TEXT("unsupported_pose_leaks_weapon_or_armor"),Observation);
    if(!V.Action.Active&&!V.NeedsSlotSelection&&P->AnimationName==TEXT("idle")&&D.Clip==TEXT("sword_ready_idle")&&Step>=0&&Step<14)++ReadySeen[Step];
    if(Step==6&&Light&&D.Supported&&D.Stage>=0&&D.Stage<3&&D.Frame>=0&&D.Frame<6)
    {++StageFrames[D.Stage];StageMasks[D.Stage]|=1<<D.Frame;}
    if(LeatherReadyOnly&&Step==5&&Light&&D.Supported&&D.Clip==TEXT("sword_ready_idle")
        &&!V.Action.Active&&P->AnimationName==TEXT("idle")&&D.Frame>=0&&D.Frame<4)
    {
        LeatherReadyMasks[D.Facing<0?0:1]|=1<<D.Frame;
        int32 NewArmorPaths=0;
        for(const auto& Path:D.DrawStack)if(Path.Contains(TEXT("/EV048/v012/HeroLeatherReady/")))++NewArmorPaths;
        if(NewArmorPaths!=3)Mismatch(TEXT("leather_ready_requires_three_actual_new_armor_layers"),Observation);
    }
    Observations.Add(MakeShared<FJsonValueObject>(R));
}
void ADungeonFairytaleEquipmentBoundProbe::Tick(float Dt)
{
    Super::Tick(Dt);if(Stopped)return;const double Wall=FPlatformTime::Seconds();
    if(PulseKey.IsValid()&&Wall>=PulseReleaseAt){Key(PulseKey,false);PulseKey=FKey();NeutralUntil=Wall+.034;}
    if(!Started)
    {
        if(!Prewarm&&Wall-WarmStart>=2.){Prewarm=true;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}
        else if(Wall-WarmStart>17.)Finish(TEXT("prewarm_timeout"));return;
    }
    if(Wall-CaptureStart>30.||Wall-StepStart>5.){Finish(TEXT("scene_or_input_timeout:")+FString(StepName()));return;}
    auto G=Game();auto P=G?G->GetPlayerFighter():nullptr;auto C=Controller();
    if(!G||!P||!C||!C->IsLocalController()||C->GetPawn()!=P){Finish(TEXT("actual_local_player_or_possession_missing"));return;}
    const auto* Inventory=G->GetEquipmentInventoryState();const auto& V=G->GetEquipmentView();
    if(!Inventory||!V.Bound||V.ActiveSlot<0||V.ActiveSlot>1||P->bDead||G->bGameOver){Finish(TEXT("actual_scene_run_not_usable"));return;}
    if(!InitialRun.IsValid())
    {
        InitialRun=V.RunGuid;InitialOwner=V.OwnerId;InitialRunAlias=V.RunAlias;InitialRestartSerial=G->GetRunRestartSerial();SwordId=V.Slots[V.ActiveSlot].InstanceId;
        InitialOperation=V.NextOperationId;InitialOperationCount=static_cast<uint64>(Inventory->Operations.size());
        if(!InitialRun.IsValid()||!InitialOwner||!SwordId||Inventory->Armor||P->WeaponId!=TEXT("WPN-SWD-001"))
        {Finish(TEXT("native_start_must_be_actual_unarmored_SWD"));return;}
    }
    if(V.RunGuid!=InitialRun||V.RunAlias!=InitialRunAlias||V.OwnerId!=InitialOwner||G->GetRunRestartSerial()!=InitialRestartSerial||V.Slots[V.ActiveSlot].InstanceId!=SwordId)
    {Finish(TEXT("run_or_active_sword_identity_changed"));return;}
    const auto SelectIs=[&](uint64 SourceId){return SourceId&&V.SelectedSourceId==SourceId;};
    const auto Register=[&](const TCHAR* KeyName,const char* Content,uint64& SourceId,uint64& InstanceId)
    {
        DungeonEquipmentInventory::FItem Prototype;Prototype.ContentId=Content;
        const auto Receipt=G->RegisterEquipmentSource(KeyName,Prototype,P->GetGroundPosition()+FVector2D(24.,0.),true);
        if(!Receipt.Ok()||Receipt.Replayed){Finish(TEXT("QA_source_actual_registration_failed"));return false;}
        SourceId=Receipt.SourceId;InstanceId=Receipt.InstanceId;return true;
    };
    switch(Step)
    {
    case 0:
        if(G->bWaitingForStart){if(CanPulse())Pulse(EKeys::Enter);}else Next(1);break;
    case 1:
        if(ReadySeen[1]>=3&&CanPulse())
        {
            if(!Register(TEXT("qa.bound.native.light.v1"),"ARM-LGT-001",LightSource,LightId))return;
            if(!SelectIs(LightSource)){Finish(TEXT("actual_nearest_light_target_not_selected"));return;}
            Pulse(EKeys::E);Next(2);
        }break;
    case 2:
        if(V.Action.Active&&V.Action.Kind==EDungeonEquipmentActionKind::PickupArmor&&V.Action.InstanceId==LightId)
        {
            CancelDeadline=V.Action.Deadline;
            if(Inventory->Armor||CancelDeadline!=V.Action.Start+.5){Finish(TEXT("pending_light_early_commit_or_wrong_deadline"));return;}
            if(G->GetSimulationTime()>=V.Action.Start+.10&&CanPulse())
            {
                if(G->GetSimulationTime()>=CancelDeadline-.08){Finish(TEXT("native_cancel_window_was_missed"));return;}
                Pulse(EKeys::A);Next(3);
            }
        }break;
    case 3:
        if(!V.Action.Active&&G->GetSimulationTime()>CancelDeadline+.02&&CanPulse())
        {
            const auto* Source=BoundSource(*G,LightSource);
            if(Inventory->Armor||!Source||Source->Consumed||V.NextOperationId!=InitialOperation){Finish(TEXT("real_cancel_spent_or_late_committed_light"));return;}
            if(!SelectIs(LightSource)){Finish(TEXT("canceled_original_light_not_actual_target"));return;}
            Pulse(EKeys::E);Next(4);
        }break;
    case 4:
        if(!V.Action.Active&&Inventory->Armor==LightId)
        {
            const auto* LightItem=BoundItem(*G,LightId);
            if(!LightItem||V.NextOperationId!=InitialOperation+1||P->ArmorId!=TEXT("ARM-LGT-001")){Finish(TEXT("normal_light_commit_identity_missing"));return;}
            InitialLightVersion=LightItem->Version;Next(5);
        }break;
    case 5:
        if(LeatherReadyOnly)
        {
            if(LeatherReadyMasks[0]==15&&LeatherReadyMasks[1]==15)
            {FlowComplete=true;Next(13);Finish();}
            else if(!LeatherTurnRequested&&LeatherReadyMasks[P->Facing<0?0:1]==15&&CanPulse())
            {Pulse(P->Facing<0?EKeys::D:EKeys::A);LeatherTurnRequested=true;}
        }
        else if(ReadySeen[5]>=3&&CanPulse()){Pulse(EKeys::J);Next(6);}break;
    case 6:
    {
        const auto& Action=P->GetMeleeCombatState().Action;
        if(Action.Active)
        {
            if(Action.WeaponInstanceId!=SwordId||Action.Stage>=3){Finish(TEXT("normal_J_action_owner_or_stage_wrong"));return;}
            if(Action.Stage<2&&Action.AttackId!=QueuedAttack&&G->GetSimulationTime()>=Action.End-.10&&CanPulse())
            {Pulse(EKeys::J);QueuedAttack=Action.AttackId;}
        }
        else if(StageFrames[0]&&StageFrames[1]&&StageFrames[2]&&ReadySeen[6]>=3&&CanPulse())
        {
            for(int32 StageIndex=0;StageIndex<3;++StageIndex)if(StageMasks[StageIndex]!=63)Mismatch(TEXT("light_combo_did_not_observe_all_six_phases"),Observations.Num());
            if(!Register(TEXT("qa.bound.native.medium.v1"),"ARM-MED-001",MediumSource,MediumId))return;
            if(!SelectIs(MediumSource)){Finish(TEXT("actual_nearest_medium_target_not_selected"));return;}
            Pulse(EKeys::E);Next(7);
        }break;
    }
    case 7:
        if(V.NeedsSlotSelection&&CanPulse())
        {
            if(V.SelectionSlot!=2||V.Action.Active||Inventory->Armor!=LightId){Finish(TEXT("actual_medium_selection_contract_wrong"));return;}
            Pulse(EKeys::Enter);Next(8);
        }break;
    case 8:
        if(!V.Action.Active&&Inventory->Armor==MediumId)
        {
            DroppedLightSource=BoundGroundSource(*G,LightId);
            if(!DroppedLightSource||V.NextOperationId!=InitialOperation+2||P->ArmorId!=TEXT("ARM-MED-001")){Finish(TEXT("actual_medium_commit_or_old_light_drop_missing"));return;}
            Next(9);
        }break;
    case 9:
        if(ReadySeen[9]>=3&&CanPulse())
        {
            if(!SelectIs(DroppedLightSource)){Finish(TEXT("original_dropped_light_not_actual_nearest_target"));return;}
            Pulse(EKeys::E);Next(10);
        }break;
    case 10:
        if(V.NeedsSlotSelection&&CanPulse())
        {
            if(V.SelectionSlot!=2||V.Action.Active||Inventory->Armor!=MediumId){Finish(TEXT("actual_retake_selection_contract_wrong"));return;}
            Pulse(EKeys::Enter);Next(11);
        }break;
    case 11:
        if(!V.Action.Active&&Inventory->Armor==LightId)
        {
            const auto* Item=BoundItem(*G,LightId);const auto* Source=BoundSource(*G,DroppedLightSource);
            if(!Item||Item->Version<=InitialLightVersion||!Source||!Source->Consumed||V.NextOperationId!=InitialOperation+3
                ||Inventory->Operations.size()!=InitialOperationCount+3||P->ArmorId!=TEXT("ARM-LGT-001"))
            {Finish(TEXT("actual_original_light_retake_identity_or_receipts_wrong"));return;}
            Next(12);
        }break;
    case 12:
        if(ReadySeen[12]>=3){FlowComplete=true;Next(13);Finish();}break;
    default:Finish(TEXT("unknown_flow_step"));break;
    }
}
void ADungeonFairytaleEquipmentBoundProbe::Finish(const FString& Reason)
{
    if(Stopped)return;Stopped=true;CaptureStop=FPlatformTime::Seconds();GIsDumpingMovie=0;
    for(const FKey Code:{EKeys::Enter,EKeys::E,EKeys::A,EKeys::D,EKeys::J})Key(Code,false);
    const bool Flushed=FlushFastLosslessProofScreenshots();
    auto Report=MakeShared<FJsonObject>();Report->SetStringField(TEXT("schema"),TEXT("fairytale-equipment-bound-native-flow-v1"));
    Report->SetBoolField(TEXT("passed"),Reason.IsEmpty()&&FlowComplete&&Mismatches.IsEmpty()&&Flushed&&!Observations.IsEmpty());
    Report->SetStringField(TEXT("reason"),Reason);Report->SetStringField(TEXT("failure"),Reason);
    Report->SetBoolField(TEXT("flow_complete"),FlowComplete);Report->SetBoolField(TEXT("silent_video"),true);Report->SetBoolField(TEXT("audio_recorded"),false);
    Report->SetBoolField(TEXT("native_async_capture_writes_flushed"),Flushed);Report->SetNumberField(TEXT("formal_complete_units"),0);
    Report->SetStringField(TEXT("scope"),TEXT("Process-only QA registered-source real Enter/E/A/J/Enter flow: committed no armor, movement-canceled light, genuine light commit, one-facing current three-stage sword, explicit Slot2 medium replacement and original-light drop/retake. Expectations use actual inventory/receipts and existing draw fields, compatible with pre-consumer DrawState. RED mismatches are preserved without stopping flow. Not lawful loot/shop, audio, complete equip animation/grasp/fullmotion, full unit or full Profile acceptance"));
    Report->SetBoolField(TEXT("leather_ready_only_trial"),LeatherReadyOnly);
    TArray<TSharedPtr<FJsonValue>> LeatherMasks;
    for(int32 Mask:LeatherReadyMasks)LeatherMasks.Add(MakeShared<FJsonValueNumber>(Mask));
    Report->SetArrayField(TEXT("leather_ready_phase_masks_left_right"),LeatherMasks);
    if(LeatherReadyOnly)Report->SetStringField(TEXT("scope"),TEXT("Opt-in leather Ready4 fit trial only: genuine normal Enter/E/A cancel and E light-armor commit from QA registered source, then normal direction input and all4idle phases both facings; same actual committed light instance. New3armor layers only. No attack, full equip/walk/hurt/death, loot/shop/reward/save or audio acceptance. Default complete bound proof remains separate."));
    Report->SetArrayField(TEXT("observations"),Observations);Report->SetArrayField(TEXT("normal_input_requests"),Inputs);Report->SetArrayField(TEXT("inputevents"),Inputs);
    Report->SetArrayField(TEXT("phasechecks"),PhaseChecks);Report->SetArrayField(TEXT("mismatches"),Mismatches);
    Report->SetNumberField(TEXT("duration_s"),Started?CaptureStop-CaptureStart:0.);
    BoundNumber(Report,TEXT("light_source_id"),LightSource);BoundNumber(Report,TEXT("medium_source_id"),MediumSource);
    BoundNumber(Report,TEXT("light_instance_id"),LightId);BoundNumber(Report,TEXT("medium_instance_id"),MediumId);BoundNumber(Report,TEXT("original_light_drop_source"),DroppedLightSource);
    TArray<TSharedPtr<FJsonValue>> Masks;for(int32 Value:StageMasks)Masks.Add(MakeShared<FJsonValueNumber>(Value));Report->SetArrayField(TEXT("light_primary_phase_masks"),Masks);
    auto Timing=MakeShared<FJsonObject>();Timing->SetNumberField(TEXT("capture_start_monotonic_s"),CaptureStart);Timing->SetNumberField(TEXT("capture_stop_monotonic_s"),CaptureStop);
    Timing->SetNumberField(TEXT("requested_video_wall_duration_s"),Started?CaptureStop-CaptureStart:0.);Timing->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());
    Timing->SetArrayField(TEXT("frame_wall_offsets_s"),Offsets);Report->SetObjectField(TEXT("capture_timing"),Timing);
    FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Report,Writer);
    if(!Directory.IsEmpty())FFileHelper::SaveStringToFile(Text,*(Directory/TEXT("runtime-report.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    FPlatformMisc::RequestExit(false);
}
void ADungeonFairytaleEquipmentBoundProbe::EndPlay(const EEndPlayReason::Type Reason)
{FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);GIsDumpingMovie=0;Super::EndPlay(Reason);}
