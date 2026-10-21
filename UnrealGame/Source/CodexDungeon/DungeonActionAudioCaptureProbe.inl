// Included only by DungeonContentProbe.cpp. No gameplay/presentation mutation,
// audio dispatch, clock advance, file IO or JSON work occurs in native sampling.
struct FActionAudioCaptureSnapshot
{
    struct FPoll
    {
        uint64 Index=0;
        double WallOffset=0.,SimulationTime=-1.;
        bool GameAvailable=false,HUDAvailable=false;
        FGuid RunGuid;
        uint64 RoomInstanceId=0,FirstReceiptSequence=0,LastReceiptSequence=0;
        int32 HUDGeneration=0,ReceiptCount=0;
    };
    struct FObservation
    {
        FDungeonActionAudioPlayRequest Request;
        uint64 PollIndex=0;
        double FirstObservedWallOffset=0.,PreviousPollWallOffset=0.,ObservedSimulationTime=-1.;
        bool Preexisting=false,PreviousPollAvailable=false;
        int32 HUDGeneration=0;
    };
    FString Profile;
    bool Started=false,Frozen=false,StartGameAvailable=false,StartHUDAvailable=false;
    bool StopGameAvailable=false,StopHUDAvailable=false,StopPlayerAvailable=false,StopInventoryAvailable=false;
    bool StartEquipmentBound=false,StopEquipmentBound=false,StopRequestExpected=false;
    bool PollLogTruncated=false,ObservationLogTruncated=false;
    double StartWall=0.,StopBoundaryWall=0.,FreezeBeginWall=0.,FreezeEndWall=0.;
    double StartSimulationTime=-1.,StopSimulationTime=-1.;
    FGuid StartRunGuid,StopRunGuid;
    uint64 StartRoomInstanceId=0,StopRoomInstanceId=0,StopOwnerId=0;
    FDungeonActionAudioState Facts;
    TArray<FDungeonActionAudioPlayRequest> Requests;
    TMap<FString,int32> Counts;
    double WeaponTime=-1.;
    uint64 EquippedInstanceId=0,NextWeaponActionId=0,NextWeaponEventId=0;
    DungeonWeaponActions::FAction CurrentWeaponAction;
    std::vector<DungeonWeaponActions::FWeaponRuntimeReceipt> WeaponRuntimeHistory;
    DungeonEquipmentInventory::FState Inventory;
    bool FourArmorEnabled=false;
    FGuid ProofRunGuid;
    uint64 ProofRoomId=0,ProofXBWInstanceId=0;
    int32 GlobalRetryShots=0,ProofShotCount=0;
    FDungeonEquipmentActionView WeaponPickup;
    TArray<FXBWArmorSocketProofState::FArmor> Armors;
    TArray<FPoll> Polls;
    TArray<FObservation> Observations;
    TArray<FString> Failures;
    TSet<FString> SeenRequestKeys,SeenRebuiltKeys;
    TWeakObjectPtr<ADungeonHUD> PreviousHUD;
    uint64 PollCount=0;
    int32 HUDGeneration=0,MissingGamePolls=0,MissingHUDPolls=0;
    int32 DuplicateKeysWithinPoll=0,KeysSeenAfterHUDRebuild=0;
    double PreviousPollWallOffset=0.;
    bool PreviousPollAvailable=false;
};

namespace DungeonActionAudioCaptureJson
{
FString U64(uint64 V){return FString::Printf(TEXT("%llu"),static_cast<unsigned long long>(V));}
FString I64(int64 V){return FString::Printf(TEXT("%lld"),static_cast<long long>(V));}
const TCHAR* const Cues[]={TEXT("XBW_RELOAD_DRAW_01"),TEXT("XBW_RELOAD_INSERT_01"),
    TEXT("XBW_RELOAD_COMPLETE_01"),TEXT("EQUIP_ARMOR_CLOTH_01"),TEXT("EQUIP_ARMOR_METAL_01")};
FString RequestKey(const FDungeonActionAudioPlayRequest& R)
{return R.Source.RunGuid.ToString(EGuidFormats::DigitsWithHyphens)+TEXT(":")+U64(R.Source.Sequence);}
TSharedPtr<FJsonObject> Record(const FDungeonActionAudioRecord& R)
{
    auto J=MakeShared<FJsonObject>();
    J->SetStringField(TEXT("sequence"),U64(R.Sequence));J->SetStringField(TEXT("cue"),R.Cue);
    J->SetNumberField(TEXT("at_time"),R.AtTime);
    J->SetStringField(TEXT("run_guid"),R.RunGuid.ToString(EGuidFormats::DigitsWithHyphens));
    J->SetStringField(TEXT("room_instance_id"),U64(R.RoomInstanceId));J->SetStringField(TEXT("owner_id"),U64(R.OwnerId));
    J->SetStringField(TEXT("action_id"),U64(R.ActionId));J->SetStringField(TEXT("instance_id"),U64(R.InstanceId));
    J->SetStringField(TEXT("operation_id"),U64(R.OperationId));J->SetStringField(TEXT("revision"),U64(R.Revision));
    return J;
}
TSharedPtr<FJsonObject> Request(const FDungeonActionAudioPlayRequest& R)
{
    auto J=MakeShared<FJsonObject>();J->SetObjectField(TEXT("source"),Record(R.Source));
    J->SetStringField(TEXT("sound_path"),R.SoundPath);J->SetNumberField(TEXT("requested_at"),R.RequestedAt);
    J->SetNumberField(TEXT("volume"),R.Volume);J->SetNumberField(TEXT("pitch"),R.Pitch);return J;
}
TSharedPtr<FJsonObject> Pickup(const FDungeonEquipmentActionView& A)
{
    auto J=MakeShared<FJsonObject>();J->SetNumberField(TEXT("kind"),int32(A.Kind));J->SetBoolField(TEXT("active"),A.Active);
    J->SetStringField(TEXT("action_id"),U64(A.ActionId));J->SetStringField(TEXT("operation_id"),U64(A.OperationId));
    J->SetStringField(TEXT("source_id"),U64(A.SourceId));J->SetStringField(TEXT("instance_id"),U64(A.InstanceId));
    J->SetNumberField(TEXT("slot"),A.Slot);J->SetNumberField(TEXT("start"),A.Start);J->SetNumberField(TEXT("deadline"),A.Deadline);return J;
}
}

void ADungeonContentProbe::BeginActionAudioEvidence()
{
    ActionAudioCaptureSnapshot=MakeShared<FActionAudioCaptureSnapshot>();auto& S=*ActionAudioCaptureSnapshot;
    S.Started=true;S.StartWall=CaptureStartWall;
    S.Profile=bArmorLayerProof?TEXT("armor_idle_primary1_layers_normal_inputs")
        :bEquipmentProof?TEXT("equipment_adapter_sources_and_normal_inputs")
        :bFirstUnitExplore?TEXT("first_unit_swd_skill_lgt_stone_explore")
        :bFirstUnitSkill?TEXT("first_unit_swd_skill_lgt_stone")
        :bFirstUnit?TEXT("first_unit_swd_lgt_stone"):TEXT("melee_benchmark");
    if(bArmorComboProof)S.Profile=TEXT("armor_idle_walk_primary123_layers_normal_inputs");
    if(bSceneProof)S.Profile=TEXT("scene_exploration_normal_inputs");
    if(bXBWReloadSocketProof)S.Profile=TEXT("xbw_reload_socket_normal_inputs");
    if(bXBWArmorSocketProof)S.Profile=TEXT("xbw_four_armor_socket_normal_inputs");
    if(bRangedProof)S.Profile=bXBWPrimaryProof?TEXT("xbw_authored_primary_body_normal_inputs")
        :bXBWHeldIdentityProof?TEXT("xbw_held_body_identity_normal_inputs")
        :bXBWReadyProof?TEXT("xbw_ready_body_normal_inputs"):TEXT("ranged_spear_adapter_normal_inputs");
    if(bArmorSleevesProof)S.Profile=TEXT("armor_idle_walk_primary123_sleeves_normal_inputs");
    const auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this));
    const auto Controller=UGameplayStatics::GetPlayerController(this,0);
    const auto HUD=IsValid(Controller)?Cast<ADungeonHUD>(Controller->GetHUD()):nullptr;
    S.StartGameAvailable=IsValid(Game);S.StartHUDAvailable=IsValid(HUD);
    if(S.StartGameAvailable)
    {
        S.StartSimulationTime=Game->GetSimulationTime();const auto& V=Game->GetEquipmentView();
        S.StartEquipmentBound=V.Bound;S.StartRunGuid=V.RunGuid;S.StartRoomInstanceId=V.RoomInstanceId;
    }
    if(!S.StartGameAvailable)S.Failures.AddUnique(TEXT("start_game_missing"));
    if(!S.StartHUDAvailable)S.Failures.AddUnique(TEXT("start_hud_missing"));
    PollActionAudioEvidence(true);
}

void ADungeonContentProbe::PollActionAudioEvidence(bool Initial)
{
    if(!ActionAudioCaptureSnapshot.IsValid()||ActionAudioCaptureSnapshot->Frozen)return;
    auto& S=*ActionAudioCaptureSnapshot;
    FActionAudioCaptureSnapshot::FPoll P;P.Index=++S.PollCount;
    P.WallOffset=FPlatformTime::Seconds()-S.StartWall;
    const auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this));
    const auto Controller=UGameplayStatics::GetPlayerController(this,0);
    const auto HUD=IsValid(Controller)?Cast<ADungeonHUD>(Controller->GetHUD()):nullptr;
    P.GameAvailable=IsValid(Game);P.HUDAvailable=IsValid(HUD);
    if(P.GameAvailable)
    {
        P.SimulationTime=Game->GetSimulationTime();const auto& V=Game->GetEquipmentView();
        P.RunGuid=V.RunGuid;P.RoomInstanceId=V.RoomInstanceId;
    }
    else {++S.MissingGamePolls;S.Failures.AddUnique(TEXT("poll_game_missing"));}
    if(!P.HUDAvailable){++S.MissingHUDPolls;S.Failures.AddUnique(TEXT("poll_hud_missing"));}
    if(P.HUDAvailable)
    {
        const bool HUDChanged=S.PreviousHUD.Get()!=HUD;
        if(HUDChanged){++S.HUDGeneration;S.PreviousHUD=HUD;}
        P.HUDGeneration=S.HUDGeneration;const auto& Receipts=HUD->GetActionAudioPlayReceipts();P.ReceiptCount=Receipts.Num();
        if(!Receipts.IsEmpty()){P.FirstReceiptSequence=Receipts[0].Source.Sequence;P.LastReceiptSequence=Receipts.Last().Source.Sequence;}
        TSet<FString> KeysInPoll;
        for(const auto& R:Receipts)
        {
            const FString ReceiptKey=DungeonActionAudioCaptureJson::RequestKey(R);
            if(KeysInPoll.Contains(ReceiptKey))++S.DuplicateKeysWithinPoll;else KeysInPoll.Add(ReceiptKey);
            if(S.SeenRequestKeys.Contains(ReceiptKey))
            {
                if(HUDChanged)for(const auto& O:S.Observations)if(DungeonActionAudioCaptureJson::RequestKey(O.Request)==ReceiptKey&&O.HUDGeneration!=P.HUDGeneration)
                {
                    const FString GenerationKey=ReceiptKey+TEXT(":hud:")+FString::FromInt(P.HUDGeneration);
                    if(!S.SeenRebuiltKeys.Contains(GenerationKey)){S.SeenRebuiltKeys.Add(GenerationKey);++S.KeysSeenAfterHUDRebuild;}
                    break;
                }
                continue;
            }
            S.SeenRequestKeys.Add(ReceiptKey);
            if(S.Observations.Num()>=4096){S.ObservationLogTruncated=true;continue;}
            FActionAudioCaptureSnapshot::FObservation O;O.Request=R;O.PollIndex=P.Index;
            O.FirstObservedWallOffset=P.WallOffset;O.PreviousPollWallOffset=S.PreviousPollWallOffset;
            O.ObservedSimulationTime=P.SimulationTime;O.Preexisting=Initial;
            O.PreviousPollAvailable=S.PreviousPollAvailable&&P.GameAvailable&&P.HUDAvailable&&!HUDChanged;
            O.HUDGeneration=P.HUDGeneration;S.Observations.Add(MoveTemp(O));
        }
    }
    if(S.Polls.Num()<8192)S.Polls.Add(P);else S.PollLogTruncated=true;
    S.PreviousPollWallOffset=P.WallOffset;S.PreviousPollAvailable=P.GameAvailable&&P.HUDAvailable;
}

void ADungeonContentProbe::FreezeActionAudioEvidence()
{
    if(!ActionAudioCaptureSnapshot.IsValid()||ActionAudioCaptureSnapshot->Frozen)return;
    auto& S=*ActionAudioCaptureSnapshot;S.FreezeBeginWall=FPlatformTime::Seconds();
    S.StopBoundaryWall=CaptureStopWall;S.StopRequestExpected=bAudioStartRequested&&IsValid(RecordingSubmix);
    PollActionAudioEvidence();
    const auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this));
    const auto Controller=UGameplayStatics::GetPlayerController(this,0);
    const auto HUD=IsValid(Controller)?Cast<ADungeonHUD>(Controller->GetHUD()):nullptr;
    const auto Player=IsValid(Game)?Game->GetPlayerFighter():nullptr;
    S.StopGameAvailable=IsValid(Game);S.StopHUDAvailable=IsValid(HUD);S.StopPlayerAvailable=IsValid(Player);
    if(S.StopGameAvailable)
    {
        S.StopSimulationTime=Game->GetSimulationTime();const auto& V=Game->GetEquipmentView();
        S.StopEquipmentBound=V.Bound;S.StopRunGuid=V.RunGuid;S.StopRoomInstanceId=V.RoomInstanceId;S.StopOwnerId=V.OwnerId;
        S.Facts=Game->GetActionAudioState();
        if(const auto Inventory=Game->GetEquipmentInventoryState()){S.Inventory=*Inventory;S.StopInventoryAvailable=true;}
    }
    if(S.StopHUDAvailable)
    {
        S.Requests=HUD->GetActionAudioPlayReceipts();
        for(const TCHAR* Cue:DungeonActionAudioCaptureJson::Cues)S.Counts.Add(Cue,HUD->GetActionAudioPlayRequests(Cue));
    }
    if(S.StopPlayerAvailable)
    {
        const auto& W=Player->GetWeaponActionsState();S.WeaponTime=W.Time;S.EquippedInstanceId=W.EquippedId;
        S.NextWeaponActionId=W.NextActionId;S.NextWeaponEventId=W.NextEventId;S.CurrentWeaponAction=W.Action;
        S.WeaponRuntimeHistory=W.WeaponRuntimeHistory;
    }
    S.FourArmorEnabled=bXBWArmorSocketProof;
    if(S.FourArmorEnabled)
    {
        S.ProofRunGuid=XBWArmorSocketProof.RunGuid;S.ProofRoomId=XBWArmorSocketProof.RoomId;
        S.ProofXBWInstanceId=XBWArmorSocketProof.InstanceId;S.GlobalRetryShots=XBWArmorSocketProof.GlobalRetries;
        S.ProofShotCount=XBWArmorSocketProof.Shots.Num();S.WeaponPickup=XBWArmorSocketProof.WeaponPickup;
        for(const auto& A:XBWArmorSocketProof.Armors)S.Armors.Add(A);
    }
    if(!S.StopGameAvailable)S.Failures.AddUnique(TEXT("stop_game_missing"));
    if(!S.StopHUDAvailable)S.Failures.AddUnique(TEXT("stop_hud_missing"));
    if(!S.StopPlayerAvailable)S.Failures.AddUnique(TEXT("stop_player_missing"));
    if(!S.StopInventoryAvailable)S.Failures.AddUnique(TEXT("stop_inventory_missing"));
    if(!S.StopEquipmentBound)S.Failures.AddUnique(TEXT("stop_equipment_unbound"));
    if(!S.StopRunGuid.IsValid())S.Failures.AddUnique(TEXT("stop_run_guid_invalid"));
    if(S.StopGameAvailable&&S.Facts.RunGuid!=S.StopRunGuid)S.Failures.AddUnique(TEXT("stop_fact_run_mismatch"));
    if(S.StopGameAvailable&&S.Facts.RoomInstanceId!=S.StopRoomInstanceId)S.Failures.AddUnique(TEXT("stop_fact_room_mismatch"));
    if(S.PollLogTruncated)S.Failures.AddUnique(TEXT("poll_log_truncated"));
    if(S.ObservationLogTruncated)S.Failures.AddUnique(TEXT("observation_log_truncated"));
    S.FreezeEndWall=FPlatformTime::Seconds();S.Frozen=true;
}

namespace DungeonActionAudioCaptureJson
{
TSharedPtr<FJsonObject> Action(const DungeonWeaponActions::FAction& A)
{
    auto J=MakeShared<FJsonObject>();
    J->SetNumberField(TEXT("type"),int32(A.Type));
    J->SetStringField(TEXT("type_name"),A.Type==DungeonWeaponActions::EAction::Reload?TEXT("Reload")
        :A.Type==DungeonWeaponActions::EAction::Primary?TEXT("Primary"):A.Type==DungeonWeaponActions::EAction::Skill?TEXT("Skill"):TEXT("None"));
    J->SetNumberField(TEXT("phase"),int32(A.Phase));J->SetNumberField(TEXT("weapon"),int32(A.Weapon));
    J->SetStringField(TEXT("instance_id"),U64(A.InstanceId));J->SetStringField(TEXT("action_id"),U64(A.ActionId));
    J->SetBoolField(TEXT("active"),A.Active);J->SetBoolField(TEXT("locked"),A.Locked);
    J->SetBoolField(TEXT("started_airborne"),A.StartedAirborne);J->SetBoolField(TEXT("forward_step_issued"),A.ForwardStepIssued);
    J->SetNumberField(TEXT("next_subhit"),A.NextSubhit);
    J->SetNumberField(TEXT("facing"),A.Facing);
    J->SetNumberField(TEXT("start"),A.Start);
    J->SetNumberField(TEXT("lock_at"),A.LockAt);
    J->SetNumberField(TEXT("active_at"),A.ActiveAt);
    J->SetNumberField(TEXT("active_end"),A.ActiveEnd);
    J->SetNumberField(TEXT("end"),A.End);
    J->SetNumberField(TEXT("speed_pct"),A.SpeedPct);
    J->SetNumberField(TEXT("damage_pct"),A.DamagePct);
    J->SetNumberField(TEXT("stagger_pct"),A.StaggerPct);
    J->SetNumberField(TEXT("reach_pct"),A.ReachPct);
    J->SetNumberField(TEXT("crit_multiplier"),A.CritMultiplier);
    J->SetNumberField(TEXT("ammo_cost"),A.AmmoCost);
    J->SetNumberField(TEXT("focus_cost"),A.FocusCost);
    J->SetNumberField(TEXT("cooldown_duration"),A.CooldownDuration);
    J->SetNumberField(TEXT("reload_speed_pct"),A.ReloadSpeedPct);
    J->SetNumberField(TEXT("focus_cost_pct"),A.FocusCostPct);
    J->SetNumberField(TEXT("skill_cooldown_pct"),A.SkillCooldownPct);
    J->SetBoolField(TEXT("critical"),A.Critical);J->SetNumberField(TEXT("terminal"),int32(A.Terminal));
    J->SetStringField(TEXT("terminal_name"),A.Terminal==DungeonWeaponActions::EEvent::ReloadCompleted?TEXT("ReloadCompleted")
        :A.Terminal==DungeonWeaponActions::EEvent::ReloadCancelled?TEXT("ReloadCancelled")
        :A.Terminal==DungeonWeaponActions::EEvent::Completed?TEXT("Completed")
        :A.Terminal==DungeonWeaponActions::EEvent::Interrupted?TEXT("Interrupted"):TEXT("Other"));
    return J;
}
TSharedPtr<FJsonObject> Runtime(const DungeonWeaponActions::FWeaponRuntimeReceipt& R)
{
    auto J=MakeShared<FJsonObject>();J->SetStringField(TEXT("event_id"),U64(R.EventId));
    J->SetNumberField(TEXT("kind"),int32(R.Kind));
    J->SetStringField(TEXT("kind_name"),R.Kind==DungeonWeaponActions::EWeaponMutation::ReloadCompleted?TEXT("ReloadCompleted")
        :R.Kind==DungeonWeaponActions::EWeaponMutation::Emission?TEXT("Emission"):TEXT("SkillLock"));
    J->SetNumberField(TEXT("at_time"),R.AtTime);J->SetNumberField(TEXT("before_ammo"),R.BeforeAmmo);J->SetNumberField(TEXT("after_ammo"),R.AfterAmmo);
    J->SetNumberField(TEXT("before_cooldown"),R.BeforeCooldown);J->SetNumberField(TEXT("after_cooldown"),R.AfterCooldown);
    J->SetNumberField(TEXT("subhit_id"),R.SubhitId);J->SetObjectField(TEXT("action"),Action(R.Action));return J;
}
TSharedPtr<FJsonObject> InventoryResult(const DungeonEquipmentInventory::FResult& R)
{
    auto J=MakeShared<FJsonObject>();J->SetNumberField(TEXT("error"),int32(R.Error));J->SetBoolField(TEXT("ok"),R.Ok());
    J->SetBoolField(TEXT("replayed"),R.Replayed);J->SetStringField(TEXT("revision"),U64(R.Revision));
    J->SetStringField(TEXT("acquired_id"),U64(R.AcquiredId));J->SetStringField(TEXT("dropped_id"),U64(R.DroppedId));
    J->SetStringField(TEXT("dropped_source_id"),U64(R.DroppedSourceId));J->SetNumberField(TEXT("active_slot"),R.ActiveSlot);return J;
}
TSharedPtr<FJsonObject> Operation(const DungeonEquipmentInventory::FOperation& O)
{
    auto J=MakeShared<FJsonObject>();J->SetStringField(TEXT("operation_id"),U64(O.OperationId));J->SetStringField(TEXT("drop_source_id"),U64(O.DropSourceId));
    const auto& P=O.Request;auto R=MakeShared<FJsonObject>();R->SetNumberField(TEXT("action"),int32(P.Action));
    R->SetStringField(TEXT("action_name"),P.Action==DungeonEquipmentInventory::EAction::Pickup?TEXT("Pickup")
        :P.Action==DungeonEquipmentInventory::EAction::Switch?TEXT("Switch"):TEXT("Drop"));
    R->SetNumberField(TEXT("slot"),P.Slot);R->SetStringField(TEXT("base_revision"),U64(P.BaseRevision));
    R->SetStringField(TEXT("source_id"),U64(P.SourceId));R->SetStringField(TEXT("source_version"),U64(P.SourceVersion));
    R->SetStringField(TEXT("instance_id"),U64(P.InstanceId));R->SetStringField(TEXT("instance_version"),U64(P.InstanceVersion));
    R->SetStringField(TEXT("replaced_id"),U64(P.ReplacedId));J->SetObjectField(TEXT("request"),R);
    J->SetObjectField(TEXT("result"),InventoryResult(O.Result));return J;
}
TSharedPtr<FJsonObject> Item(const DungeonEquipmentInventory::FItem& I)
{
    auto J=MakeShared<FJsonObject>();J->SetStringField(TEXT("instance_id"),U64(I.InstanceId));J->SetStringField(TEXT("version"),U64(I.Version));
    J->SetStringField(TEXT("content_id"),UTF8_TO_TCHAR(I.ContentId.c_str()));J->SetNumberField(TEXT("grade"),I.Grade);
    J->SetNumberField(TEXT("package"),int32(I.Package));J->SetNumberField(TEXT("tier"),I.Tier);
    J->SetNumberField(TEXT("ammo"),I.Ammo);J->SetNumberField(TEXT("skill_cooldown_deadline"),I.SkillCooldownDeadline);
    TArray<TSharedPtr<FJsonValue>> Affixes;
    for(const auto& A:I.Affixes)
    {
        auto V=MakeShared<FJsonObject>();V->SetStringField(TEXT("id"),UTF8_TO_TCHAR(A.Id.c_str()));V->SetNumberField(TEXT("magnitude"),A.Magnitude);
        V->SetStringField(TEXT("original_q_numerator"),I64(A.OriginalQ.Numerator));V->SetStringField(TEXT("original_q_denominator"),I64(A.OriginalQ.Denominator));
        Affixes.Add(MakeShared<FJsonValueObject>(V));
    }
    J->SetArrayField(TEXT("affixes"),Affixes);return J;
}
TSharedPtr<FJsonObject> Source(const DungeonEquipmentInventory::FSource& S)
{
    auto J=MakeShared<FJsonObject>();J->SetStringField(TEXT("source_id"),U64(S.SourceId));J->SetStringField(TEXT("version"),U64(S.Version));
    J->SetStringField(TEXT("instance_id"),U64(S.InstanceId));J->SetBoolField(TEXT("available"),S.Available);
    J->SetStringField(TEXT("created_revision"),U64(S.CreatedRevision));J->SetObjectField(TEXT("spawn_item"),Item(S.SpawnItem));return J;
}
TSharedPtr<FJsonObject> InventoryRuntime(const DungeonEquipmentInventory::FRuntimeReceipt& R)
{
    auto J=MakeShared<FJsonObject>();J->SetStringField(TEXT("receipt_id"),U64(R.ReceiptId));J->SetStringField(TEXT("base_revision"),U64(R.BaseRevision));
    J->SetStringField(TEXT("instance_id"),U64(R.InstanceId));J->SetStringField(TEXT("before_version"),U64(R.BeforeVersion));
    J->SetStringField(TEXT("after_version"),U64(R.AfterVersion));J->SetNumberField(TEXT("at_time"),R.AtTime);
    J->SetNumberField(TEXT("before_ammo"),R.BeforeAmmo);J->SetNumberField(TEXT("ammo"),R.Ammo);
    J->SetNumberField(TEXT("before_cooldown"),R.BeforeCooldown);J->SetNumberField(TEXT("skill_cooldown_deadline"),R.SkillCooldownDeadline);
    J->SetObjectField(TEXT("result"),InventoryResult(R.Result));return J;
}
}

TSharedPtr<FJsonObject> ADungeonContentProbe::SerializeActionAudioEvidence() const
{
    using namespace DungeonActionAudioCaptureJson;
    auto J=MakeShared<FJsonObject>();J->SetNumberField(TEXT("schema"),1);
    J->SetStringField(TEXT("uint64_encoding"),TEXT("decimal_string"));
    J->SetStringField(TEXT("scope"),TEXT("Probe-only native copies at the stop boundary; no live gameplay reads during Save or export wait. PlaySound2D receipts prove requests, not audio-device onset, complete WAV inclusion, listening or final content acceptance."));
    TArray<TSharedPtr<FJsonValue>> Limitations;
    for(const TCHAR* L:{TEXT("request_first_observed_wall_offset_s is polling visibility, not audio onset"),
        TEXT("simulation time does not map to WAV offset across menus or fresh Runs"),
        TEXT("previous poll bounds require previous_poll_available; the first poll has no absence bound"),
        TEXT("HUD generation, retained receipt tails and truncation flags must be reviewed"),
        TEXT("stop boundary stamp precedes native copy; final poll may be later but still precedes StopRecordingOutput"),
        TEXT("snapshot does not measure audio-thread start/stop acknowledgement or render latency")})Limitations.Add(MakeShared<FJsonValueString>(L));
    J->SetArrayField(TEXT("limitations"),Limitations);
    if(!ActionAudioCaptureSnapshot.IsValid())
    {
        J->SetBoolField(TEXT("valid"),false);J->SetBoolField(TEXT("frozen"),false);
        TArray<TSharedPtr<FJsonValue>> E;E.Add(MakeShared<FJsonValueString>(TEXT("capture_evidence_not_started")));
        J->SetArrayField(TEXT("failures"),E);return J;
    }
    // Everything below reads this native snapshot only. In particular, no
    // Game/HUD getter, current platform clock or audio control API is called.
    const auto& S=*ActionAudioCaptureSnapshot;
    J->SetStringField(TEXT("profile"),S.Profile);J->SetBoolField(TEXT("started"),S.Started);J->SetBoolField(TEXT("frozen"),S.Frozen);
    J->SetBoolField(TEXT("snapshot_taken_before_stop_request"),S.Frozen&&S.StopRequestExpected);
    J->SetBoolField(TEXT("valid"),S.Started&&S.Frozen&&S.StopRequestExpected&&S.Failures.IsEmpty());
    TArray<TSharedPtr<FJsonValue>> Errors;for(const auto& E:S.Failures)Errors.Add(MakeShared<FJsonValueString>(E));
    if(!S.Frozen)Errors.Add(MakeShared<FJsonValueString>(TEXT("stop_snapshot_not_taken")));
    if(!S.StopRequestExpected)Errors.Add(MakeShared<FJsonValueString>(TEXT("recording_stop_api_not_expected")));
    J->SetArrayField(TEXT("failures"),Errors);
    auto B=MakeShared<FJsonObject>();
    B->SetNumberField(TEXT("capture_start_monotonic_s"),S.StartWall);B->SetNumberField(TEXT("capture_stop_boundary_monotonic_s"),S.StopBoundaryWall);
    B->SetNumberField(TEXT("freeze_begin_monotonic_s"),S.FreezeBeginWall);B->SetNumberField(TEXT("freeze_end_monotonic_s"),S.FreezeEndWall);
    B->SetNumberField(TEXT("capture_start_sim_s"),S.StartSimulationTime);B->SetNumberField(TEXT("capture_stop_sim_s"),S.StopSimulationTime);
    B->SetBoolField(TEXT("start_game_available"),S.StartGameAvailable);B->SetBoolField(TEXT("start_hud_available"),S.StartHUDAvailable);
    B->SetBoolField(TEXT("stop_game_available"),S.StopGameAvailable);B->SetBoolField(TEXT("stop_hud_available"),S.StopHUDAvailable);
    B->SetBoolField(TEXT("stop_player_available"),S.StopPlayerAvailable);B->SetBoolField(TEXT("stop_inventory_available"),S.StopInventoryAvailable);
    B->SetBoolField(TEXT("start_equipment_bound"),S.StartEquipmentBound);B->SetBoolField(TEXT("stop_equipment_bound"),S.StopEquipmentBound);
    B->SetStringField(TEXT("start_run_guid"),S.StartRunGuid.ToString(EGuidFormats::DigitsWithHyphens));
    B->SetStringField(TEXT("stop_run_guid"),S.StopRunGuid.ToString(EGuidFormats::DigitsWithHyphens));
    B->SetStringField(TEXT("start_room_instance_id"),U64(S.StartRoomInstanceId));B->SetStringField(TEXT("stop_room_instance_id"),U64(S.StopRoomInstanceId));
    B->SetStringField(TEXT("stop_owner_id"),U64(S.StopOwnerId));J->SetObjectField(TEXT("boundaries"),B);
    auto F=MakeShared<FJsonObject>();F->SetStringField(TEXT("run_guid"),S.Facts.RunGuid.ToString(EGuidFormats::DigitsWithHyphens));
    F->SetStringField(TEXT("room_instance_id"),U64(S.Facts.RoomInstanceId));F->SetStringField(TEXT("next_sequence"),U64(S.Facts.NextSequence));
    F->SetNumberField(TEXT("retained_count"),S.Facts.Records.Num());
    F->SetStringField(TEXT("first_retained_sequence"),U64(S.Facts.Records.IsEmpty()?0:S.Facts.Records[0].Sequence));
    F->SetStringField(TEXT("last_retained_sequence"),U64(S.Facts.Records.IsEmpty()?0:S.Facts.Records.Last().Sequence));
    TArray<TSharedPtr<FJsonValue>> FactValues;for(const auto& R:S.Facts.Records)FactValues.Add(MakeShared<FJsonValueObject>(Record(R)));
    F->SetArrayField(TEXT("records"),FactValues);J->SetObjectField(TEXT("facts"),F);
    auto H=MakeShared<FJsonObject>();H->SetBoolField(TEXT("available"),S.StopHUDAvailable);H->SetNumberField(TEXT("generation"),S.HUDGeneration);
    H->SetNumberField(TEXT("retained_request_count"),S.Requests.Num());
    H->SetStringField(TEXT("first_retained_sequence"),U64(S.Requests.IsEmpty()?0:S.Requests[0].Source.Sequence));
    H->SetStringField(TEXT("last_retained_sequence"),U64(S.Requests.IsEmpty()?0:S.Requests.Last().Source.Sequence));
    auto Counts=MakeShared<FJsonObject>();for(const TCHAR* Cue:Cues)Counts->SetNumberField(Cue,S.Counts.FindRef(Cue));H->SetObjectField(TEXT("counts"),Counts);
    TArray<TSharedPtr<FJsonValue>> RequestValues;for(const auto& R:S.Requests)RequestValues.Add(MakeShared<FJsonValueObject>(Request(R)));
    H->SetArrayField(TEXT("receipts"),RequestValues);J->SetObjectField(TEXT("hud"),H);
    auto P=MakeShared<FJsonObject>();P->SetStringField(TEXT("poll_count"),U64(S.PollCount));
    P->SetNumberField(TEXT("retained_poll_count"),S.Polls.Num());P->SetNumberField(TEXT("retained_observation_count"),S.Observations.Num());
    P->SetBoolField(TEXT("poll_log_truncated"),S.PollLogTruncated);P->SetBoolField(TEXT("observation_log_truncated"),S.ObservationLogTruncated);
    P->SetNumberField(TEXT("missing_game_polls"),S.MissingGamePolls);P->SetNumberField(TEXT("missing_hud_polls"),S.MissingHUDPolls);
    P->SetNumberField(TEXT("hud_generation_count"),S.HUDGeneration);P->SetNumberField(TEXT("duplicate_keys_within_poll"),S.DuplicateKeysWithinPoll);
    P->SetNumberField(TEXT("keys_seen_after_hud_rebuild"),S.KeysSeenAfterHUDRebuild);
    P->SetNumberField(TEXT("poll_log_capacity"),8192);P->SetNumberField(TEXT("observation_log_capacity"),4096);
    P->SetStringField(TEXT("tick_order_scope"),TEXT("Probe normal recording tick and final stop-entry poll only. HUD and GameMode are never ticked by this observer; relative same-frame scheduling and menu pauses remain visible in poll intervals."));
    TArray<TSharedPtr<FJsonValue>> PollValues;
    for(const auto& R:S.Polls)
    {
        auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("index"),U64(R.Index));O->SetNumberField(TEXT("wall_offset_s"),R.WallOffset);
        O->SetNumberField(TEXT("simulation_time_s"),R.SimulationTime);O->SetBoolField(TEXT("game_available"),R.GameAvailable);O->SetBoolField(TEXT("hud_available"),R.HUDAvailable);
        O->SetStringField(TEXT("run_guid"),R.RunGuid.ToString(EGuidFormats::DigitsWithHyphens));O->SetStringField(TEXT("room_instance_id"),U64(R.RoomInstanceId));
        O->SetNumberField(TEXT("hud_generation"),R.HUDGeneration);O->SetNumberField(TEXT("receipt_count"),R.ReceiptCount);
        O->SetStringField(TEXT("first_receipt_sequence"),U64(R.FirstReceiptSequence));O->SetStringField(TEXT("last_receipt_sequence"),U64(R.LastReceiptSequence));
        PollValues.Add(MakeShared<FJsonValueObject>(O));
    }
    P->SetArrayField(TEXT("polls"),PollValues);
    TArray<TSharedPtr<FJsonValue>> ObservationValues;
    for(const auto& R:S.Observations)
    {
        auto O=MakeShared<FJsonObject>();O->SetObjectField(TEXT("request"),Request(R.Request));O->SetStringField(TEXT("poll_index"),U64(R.PollIndex));
        O->SetNumberField(TEXT("request_first_observed_wall_offset_s"),R.FirstObservedWallOffset);
        O->SetNumberField(TEXT("previous_poll_wall_offset_s"),R.PreviousPollWallOffset);O->SetNumberField(TEXT("observed_simulation_time_s"),R.ObservedSimulationTime);
        O->SetBoolField(TEXT("preexisting_at_capture_start"),R.Preexisting);O->SetBoolField(TEXT("previous_poll_available"),R.PreviousPollAvailable);
        O->SetBoolField(TEXT("poll_interval_valid"),R.PreviousPollAvailable&&!R.Preexisting);O->SetNumberField(TEXT("hud_generation"),R.HUDGeneration);
        ObservationValues.Add(MakeShared<FJsonValueObject>(O));
    }
    P->SetArrayField(TEXT("observations"),ObservationValues);J->SetObjectField(TEXT("polling"),P);
    auto W=MakeShared<FJsonObject>();W->SetNumberField(TEXT("weapon_time"),S.WeaponTime);
    W->SetStringField(TEXT("equipped_instance_id"),U64(S.EquippedInstanceId));W->SetStringField(TEXT("next_action_id"),U64(S.NextWeaponActionId));
    W->SetStringField(TEXT("next_event_id"),U64(S.NextWeaponEventId));W->SetObjectField(TEXT("current_action"),Action(S.CurrentWeaponAction));
    TArray<TSharedPtr<FJsonValue>> RuntimeValues;for(const auto& R:S.WeaponRuntimeHistory)RuntimeValues.Add(MakeShared<FJsonValueObject>(Runtime(R)));
    W->SetArrayField(TEXT("weapon_runtime_history"),RuntimeValues);J->SetObjectField(TEXT("resources"),W);
    auto I=MakeShared<FJsonObject>();I->SetBoolField(TEXT("available"),S.StopInventoryAvailable);
    I->SetStringField(TEXT("run_id"),U64(S.Inventory.RunId));I->SetStringField(TEXT("owner_id"),U64(S.Inventory.OwnerId));
    I->SetStringField(TEXT("revision"),U64(S.Inventory.Revision));I->SetStringField(TEXT("starter_id"),U64(S.Inventory.StarterId));
    I->SetNumberField(TEXT("active_slot"),S.Inventory.ActiveSlot);I->SetStringField(TEXT("armor_instance_id"),U64(S.Inventory.Armor));
    TArray<TSharedPtr<FJsonValue>> Weapons;for(const auto Id:S.Inventory.Weapons)Weapons.Add(MakeShared<FJsonValueString>(U64(Id)));I->SetArrayField(TEXT("weapons"),Weapons);
    TArray<TSharedPtr<FJsonValue>> Operations;for(const auto& O:S.Inventory.Operations)Operations.Add(MakeShared<FJsonValueObject>(Operation(O)));I->SetArrayField(TEXT("operations"),Operations);
    TArray<TSharedPtr<FJsonValue>> Items;for(const auto& R:S.Inventory.Items)Items.Add(MakeShared<FJsonValueObject>(Item(R)));I->SetArrayField(TEXT("items"),Items);
    TArray<TSharedPtr<FJsonValue>> Sources;for(const auto& R:S.Inventory.Sources)Sources.Add(MakeShared<FJsonValueObject>(Source(R)));I->SetArrayField(TEXT("sources"),Sources);
    I->SetStringField(TEXT("next_runtime_receipt_id"),U64(S.Inventory.NextRuntimeReceiptId));
    TArray<TSharedPtr<FJsonValue>> RuntimeUpdates;for(const auto& R:S.Inventory.RuntimeUpdates)RuntimeUpdates.Add(MakeShared<FJsonValueObject>(InventoryRuntime(R)));I->SetArrayField(TEXT("runtime_updates"),RuntimeUpdates);
    J->SetObjectField(TEXT("inventory"),I);
    auto A=MakeShared<FJsonObject>();A->SetBoolField(TEXT("enabled"),S.FourArmorEnabled);
    A->SetStringField(TEXT("proof_run_guid"),S.ProofRunGuid.ToString(EGuidFormats::DigitsWithHyphens));
    A->SetStringField(TEXT("room_instance_id"),U64(S.ProofRoomId));A->SetStringField(TEXT("xbw_instance_id"),U64(S.ProofXBWInstanceId));
    A->SetNumberField(TEXT("global_retry_shots"),S.GlobalRetryShots);A->SetNumberField(TEXT("shot_count"),S.ProofShotCount);
    A->SetObjectField(TEXT("weapon_pickup"),Pickup(S.WeaponPickup));TArray<TSharedPtr<FJsonValue>> Armors;
    for(const auto& R:S.Armors)
    {
        auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("id"),R.Id);O->SetStringField(TEXT("token"),R.Token);O->SetStringField(TEXT("old_id"),R.OldId);
        O->SetStringField(TEXT("source_id"),U64(R.SourceId));O->SetStringField(TEXT("instance_id"),U64(R.InstanceId));O->SetStringField(TEXT("old_instance_id"),U64(R.OldInstanceId));
        O->SetBoolField(TEXT("pickup_observed"),R.PickupObserved);O->SetBoolField(TEXT("committed"),R.Committed);
        O->SetBoolField(TEXT("pickup_old_held"),R.PickupOldHeld);O->SetBoolField(TEXT("pickup_duration"),R.PickupDuration);
        O->SetBoolField(TEXT("confirmed"),R.Confirmed);O->SetObjectField(TEXT("pickup"),Pickup(R.Pickup));Armors.Add(MakeShared<FJsonValueObject>(O));
    }
    A->SetArrayField(TEXT("armors"),Armors);J->SetObjectField(TEXT("four_armor_pickups"),A);return J;
}
