// Explicit QA sources/targets, real controller edges, read-only post-batch receipts.
// The fixture configures actors only at creation; it never repairs live gameplay.
void ADungeonContentProbe::TickRangedProof()
{
    if(bGameplayFinished) return;
    auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this));
    auto Player=Game?Game->GetPlayerFighter():nullptr;
    auto Controller=UGameplayStatics::GetPlayerController(this,0);
    auto HUD=Controller?Cast<ADungeonHUD>(Controller->GetHUD()):nullptr;
    auto& S=RangedProof;
    const auto Fail=[this](const FString& Reason)
    {
        UnitFailure=Reason;UnitReleaseInputs();bGameplayFinished=true;
        Check(TEXT("ranged_completed_within_45s"),false);FinishAudioCapture();
    };
    if(!Game||!Player||!HUD) {Fail(TEXT("ranged_missing_mode_player_or_hud"));return;}
    if(bFirstUnit||bEquipmentProof||bArmorLayerProof) {Fail(TEXT("ranged_conflicting_proof_flags"));return;}
    const double Now=Game->GetSimulationTime();
    if(bUnitEdgeDown&&Now>UnitEdgeAt)
    {Key(UnitEdgeKey,false);bUnitEdgeDown=false;UnitReleasedAt=Now;}
    const auto& V=Game->GetEquipmentView();
    const auto& WA=Player->GetWeaponActionsState();
    const auto& World=Game->GetWeaponWorldState();
    using EventKind=EDungeonWorldWeaponEventKind;
    using ActionKind=DungeonWeaponActions::EAction;
    using WeaponKind=DungeonContentCombat::EWeapon;
    const auto Near=[](double A,double B,double Tolerance=1.e-5){return FMath::Abs(A-B)<=Tolerance;};
    const auto ActiveId=[&V](){return V.Slots[V.ActiveSlot].InstanceId;};
    const auto Instance=[&WA](uint64 Id)->const DungeonWeaponActions::FInstance*
    {for(const auto& I:WA.Instances)if(I.InstanceId==Id)return &I;return nullptr;};
    const auto Source=[Game](uint64 Id)->const FDungeonEquipmentSourceView*
    {for(const auto& I:Game->GetEquipmentSources())if(I.SourceId==Id)return &I;return nullptr;};
    const auto Issued=[&WA](uint64 Id,uint32 Sub=0)->const DungeonWeaponActions::FEvent*
    {for(const auto& E:WA.Issued)if(E.ActionId==Id&&E.SubhitId==Sub)return &E;return nullptr;};
    const auto Count=[&World](EventKind Kind,uint64 Action=0,uint64 Target=0,int32 Sub=-1)
    {int32 N=0;for(const auto& E:World.Events)if(E.Kind==Kind&&(!Action||E.Key.ActionId==Action)
        &&(!Target||E.TargetId==Target)&&(Sub<0||E.Key.SubhitId==uint32(Sub)))++N;return N;};
    const auto Event=[&World](EventKind Kind,uint64 Action,uint64 Target,int32 Sub=-1)->const FDungeonWorldWeaponEvent*
    {for(const auto& E:World.Events)if(E.Kind==Kind&&E.Key.ActionId==Action&&E.TargetId==Target
        &&(Sub<0||E.Key.SubhitId==uint32(Sub)))return &E;return nullptr;};
    const auto FocusReceipt=[&WA](uint64 EventId,double Cost)
    {int32 N=0;for(const auto& R:WA.FocusHistory)if(R.Kind==DungeonWeaponActions::EFocusChange::Emission&&R.ReceiptId==EventId
        &&R.Requested==Cost&&R.Applied==Cost&&R.After==R.Before-Cost)++N;return N==1;};
    const auto Refills=[&WA,&S]()
    {int32 N=0;for(const auto& R:WA.WeaponRuntimeHistory)if(R.Kind==DungeonWeaponActions::EWeaponMutation::ReloadCompleted
        &&R.Action.InstanceId==S.InstanceIds[0])++N;return N;};
    const auto Require=[this,&Fail](const TCHAR* Name,bool Passed)
    {Check(Name,Passed);if(!Passed)Fail(Name);return Passed;};
    const auto Go=[this,&S,Now](int32 Phase)
    {UnitMove(0,0);S.Phase=Phase;S.PhaseAt=Now;S.ArrivalAt=-1;S.InputAt=-1;
        S.InputIssued=false;S.ActionObserved=false;S.OldHeld=true;S.DurationValid=true;};
    const auto Approach=[this,&S,Player,Now](FVector2D Target)
    {
        const auto D=Target-Player->GetGroundPosition();
        if(FMath::Abs(D.X)>20.||FMath::Abs(D.Y)>12.)
        {UnitMove(FMath::Abs(D.X)>20.?float(FMath::Sign(D.X)):0.f,FMath::Abs(D.Y)>12.?float(FMath::Sign(D.Y)):0.f);S.ArrivalAt=-1;return false;}
        UnitMove(0,0);if(S.ArrivalAt<0)S.ArrivalAt=Now;return Now-S.ArrivalAt>=.2;
    };
    const auto PulseAction=[this,&S,&WA,&V,Now](int32 Index,FKey Code)
    {
        if(!S.InputIssued&&Now-S.PhaseAt>.25&&UnitPulse(Code,Now))
        {S.InputIssued=true;S.InputAt=Now;S.FocusAtInput[Index]=WA.Budget.Focus;S.CritAtInput[Index]=V.NextCritDraw;}
        const auto& A=WA.Action;
        const auto Expected=Index<2?WeaponKind::XBW001:Index<4?WeaponKind::STF001:WeaponKind::SPR001;
        const auto Type=Index==0||Index==2?ActionKind::Primary:ActionKind::Skill;
        if(S.InputIssued&&!S.ActionObserved&&A.Active&&A.Start>=S.InputAt&&A.Weapon==Expected&&A.Type==Type)
        {S.Actions[Index]=A;S.ActionObserved=true;}
        return S.ActionObserved;
    };

    // Every row is a post-batch observation; world events are recorded once by sequence.
    auto Row=MakeShared<FJsonObject>();
    Row->SetStringField(TEXT("record_type"),TEXT("ranged_normal_input_post_batch_observation"));
    Row->SetNumberField(TEXT("fixture_phase"),S.Phase);Row->SetNumberField(TEXT("sim_time_s"),Now);
    Row->SetNumberField(TEXT("wall_offset_s"),Elapsed);Row->SetStringField(TEXT("run_guid"),V.RunGuid.ToString());
    Row->SetNumberField(TEXT("room_instance_id"),double(World.RoomInstanceId));
    Row->SetNumberField(TEXT("player_x"),Player->GetGroundPosition().X);Row->SetNumberField(TEXT("player_y"),Player->GetGroundPosition().Y);
    Row->SetNumberField(TEXT("player_hp"),Player->Health);Row->SetNumberField(TEXT("focus"),WA.Budget.Focus);
    Row->SetNumberField(TEXT("reserved_focus"),WA.Budget.ReservedFocus);Row->SetNumberField(TEXT("last_actual_spend"),WA.Budget.LastActualSpend);
    Row->SetNumberField(TEXT("weapon_clock"),WA.Time);Row->SetBoolField(TEXT("grounded"),WA.Budget.Grounded);
    Row->SetNumberField(TEXT("active_instance_id"),double(WA.EquippedId));Row->SetNumberField(TEXT("active_slot"),V.ActiveSlot);
    Row->SetNumberField(TEXT("action_id"),double(WA.Action.ActionId));Row->SetNumberField(TEXT("action_type"),int32(WA.Action.Type));
    Row->SetBoolField(TEXT("action_active"),WA.Action.Active);Row->SetBoolField(TEXT("action_locked"),WA.Action.Locked);
    Row->SetNumberField(TEXT("action_start"),WA.Action.Start);Row->SetNumberField(TEXT("action_end"),WA.Action.End);
    Row->SetNumberField(TEXT("crit_next_draw"),double(V.NextCritDraw));Row->SetNumberField(TEXT("selected_source"),double(V.SelectedSourceId));
    Row->SetBoolField(TEXT("needs_slot_selection"),V.NeedsSlotSelection);Row->SetNumberField(TEXT("selection_slot"),V.SelectionSlot);
    Row->SetBoolField(TEXT("equipment_action_active"),V.Action.Active);Row->SetNumberField(TEXT("equipment_action_start"),V.Action.Start);
    Row->SetNumberField(TEXT("equipment_action_deadline"),V.Action.Deadline);
    Row->SetStringField(TEXT("rendered_player_texture_path"),HUD->GetRenderedPlayerTexturePath());
    Row->SetNumberField(TEXT("sprite_canvas_size"),HUD->GetRenderedPlayerSpriteSize());
    if(bXBWReadyProof)
    {
        Row->SetBoolField(TEXT("actual_weapon_body_draw_used"),HUD->GetRenderedWeaponBodyUsed());
        Row->SetNumberField(TEXT("ready_body_frame"),HUD->GetRenderedWeaponBodyFrame());
        Row->SetNumberField(TEXT("ready_body_facing"),HUD->GetRenderedWeaponBodyFacing());
        const auto Emit=HUD->GetRenderedWeaponBodyEmitScreen();
        Row->SetNumberField(TEXT("presentation_emit_screen_x"),Emit.X);Row->SetNumberField(TEXT("presentation_emit_screen_y"),Emit.Y);
        TArray<TSharedPtr<FJsonValue>> Stack;
        for(const auto& Path:HUD->GetRenderedPlayerDrawStack()) Stack.Add(MakeShared<FJsonValueString>(Path));
        Row->SetArrayField(TEXT("actual_player_draw_stack"),Stack);
        Row->SetBoolField(TEXT("presentation_emit_is_world_authority"),false);
        Row->SetStringField(TEXT("held_body_render_clip"),HUD->GetRenderedWeaponBodyClip());
        Row->SetNumberField(TEXT("rendered_body_action_id"),double(HUD->GetRenderedWeaponBodyActionId()));
        Row->SetNumberField(TEXT("rendered_body_sample_time"),HUD->GetRenderedWeaponBodySampleTime());
        Row->SetStringField(TEXT("player_animation_name"),Player->AnimationName);
        Row->SetNumberField(TEXT("queued_player_melee_trails"),HUD->GetQueuedPlayerMeleeTrailCount());
        if(bXBWHeldIdentityProof && WA.Action.Active && WA.Action.Weapon==WeaponKind::XBW001
            && (WA.Action.Type==ActionKind::Primary || WA.Action.Type==ActionKind::Reload))
        {
            const int32 Pose=HUD->GetRenderedWeaponBodyFrame();
            const bool Held=HUD->GetRenderedWeaponBodyUsed()&&HUD->GetRenderedPlayerDrawStack().Num()==4
                &&Pose>=0&&Pose<6&&HUD->GetQueuedPlayerMeleeTrailCount()==0;
            S.HeldActionIdentityValid&=Held;
            if(Held && HUD->GetRenderedWeaponBodyClip()==(bXBWPrimaryProof?TEXT("xbw_primary"):TEXT("xbw_ready_idle_pose_during_attack"))) S.HeldFiringSeen=true;
            if(Held && WA.Action.Type==ActionKind::Reload && HUD->GetRenderedWeaponBodyClip()==TEXT("xbw_ready_idle_pose_during_reload"))
                S.HeldReloadFrameMask|=1<<Pose;
        }
    }
    if(bXBWPrimaryProof && HUD->GetRenderedWeaponBodyClip()==TEXT("xbw_primary")
        && HUD->GetRenderedWeaponBodyActionId()==WA.Action.ActionId)
    {
        auto DrawState=WA;DrawState.Time=HUD->GetRenderedWeaponBodySampleTime();
        DungeonXBWBodyPose::FPose ExpectedPose;
        const int32 Pose=HUD->GetRenderedWeaponBodyFrame();
        const auto Path=[Pose](const FString& Track){const FString Name=FString::Printf(TEXT("T_XBWPrimary_%s_%03d_v001"),*Track,Pose);
            return TEXT("/Game/Production/FirstBatch/v017/XBWPrimary/")+Name+TEXT(".")+Name;};
        const TArray<FString> ExpectedStack={Path(TEXT("body_far")),
            TEXT("/Game/Production/FirstBatch/v015/WeaponComponents/T_WPN_XBW_001_neutral_v001.T_WPN_XBW_001_neutral_v001"),
            Path(TEXT("body_support")),Path(TEXT("body_near"))};
        S.PrimaryClockStackValid&=DungeonXBWBodyPose::Primary(DrawState,ExpectedPose)&&ExpectedPose.Frame==Pose
            &&HUD->GetRenderedPlayerDrawStack()==ExpectedStack&&HUD->GetQueuedPlayerMeleeTrailCount()==0;
        if(Pose>=0&&Pose<6){S.PrimaryFrameMask|=1<<Pose;S.PrimaryPhaseMask|=Pose<2?1:Pose<4?2:4;}
    }
    Row->SetNumberField(TEXT("xbw_release_audio_requests"),HUD->GetWorldWeaponAudioRequests(TEXT("XBW_RELEASE_01")));
    Row->SetNumberField(TEXT("fire_launch_audio_requests"),HUD->GetWorldWeaponAudioRequests(TEXT("FIRE_LAUNCH_01")));
    Row->SetNumberField(TEXT("fire_burn_audio_requests"),HUD->GetWorldWeaponAudioRequests(TEXT("FIRE_BURN_SHORT_01")));
    TArray<TSharedPtr<FJsonValue>> Slots,Sources,Targets,Events,Projectiles,Burns,IssuedFacts,FocusFacts,WeaponFacts;
    for(const auto& Slot:V.Slots)
    {
        auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("content_id"),Slot.ContentId);
        O->SetNumberField(TEXT("instance_id"),double(Slot.InstanceId));O->SetNumberField(TEXT("ammo"),Slot.Ammo);
        O->SetNumberField(TEXT("cooldown_deadline"),Slot.CooldownDeadline);Slots.Add(MakeShared<FJsonValueObject>(O));
    }
    for(const auto& F:Game->GetEquipmentSources())
    {
        auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("qa_logical_key"),F.LogicalKey);
        O->SetStringField(TEXT("content_id"),UTF8_TO_TCHAR(F.Item.ContentId.c_str()));O->SetNumberField(TEXT("source_id"),double(F.SourceId));
        O->SetNumberField(TEXT("instance_id"),double(F.InstanceId));O->SetNumberField(TEXT("version"),double(F.Version));
        O->SetNumberField(TEXT("x"),F.Position.X);O->SetNumberField(TEXT("y"),F.Position.Y);O->SetBoolField(TEXT("consumed"),F.Consumed);
        O->SetNumberField(TEXT("ammo"),F.Item.Ammo);O->SetNumberField(TEXT("cooldown_deadline"),F.Item.SkillCooldownDeadline);
        Sources.Add(MakeShared<FJsonValueObject>(O));
    }
    for(int32 Lane=0;Lane<2;++Lane)for(int32 I=0;I<3;++I)
        if(auto T=(Lane?S.SpearTargets[I]:S.RangedTargets[I]).Get())
        {
            auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("lane"),Lane);O->SetNumberField(TEXT("order"),I);
            O->SetNumberField(TEXT("entity_id"),double(T->GetRuntimeEntityId()));O->SetNumberField(TEXT("hp"),T->Health);
            O->SetNumberField(TEXT("authored_max_hp"),T->MaxHealth);O->SetBoolField(TEXT("dead"),T->bDead);
            O->SetNumberField(TEXT("x"),T->GetGroundPosition().X);O->SetNumberField(TEXT("y"),T->GetGroundPosition().Y);
            Targets.Add(MakeShared<FJsonValueObject>(O));
        }
    for(const auto& E:World.Events)if(E.Sequence>S.WorldCursor)
    {
        auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("sequence"),double(E.Sequence));O->SetNumberField(TEXT("kind"),int32(E.Kind));
        O->SetNumberField(TEXT("owner_id"),double(E.Key.OwnerId));O->SetNumberField(TEXT("action_id"),double(E.Key.ActionId));
        O->SetNumberField(TEXT("event_id"),double(E.Key.EventId));O->SetNumberField(TEXT("subhit_id"),E.Key.SubhitId);
        O->SetNumberField(TEXT("target_id"),double(E.TargetId));O->SetNumberField(TEXT("at_time"),E.AtTime);
        O->SetNumberField(TEXT("damage"),E.Damage);O->SetNumberField(TEXT("stagger"),E.Stagger);
        O->SetNumberField(TEXT("actual_hp_loss"),E.ActualHPLoss);O->SetBoolField(TEXT("magic"),E.Magic);
        O->SetNumberField(TEXT("x"),E.Position.X);O->SetNumberField(TEXT("y"),E.Position.Y);O->SetNumberField(TEXT("height"),E.Height);
        Events.Add(MakeShared<FJsonValueObject>(O));S.WorldCursor=FMath::Max(S.WorldCursor,E.Sequence);
    }
    for(const auto& P:World.Projectiles)
    {
        auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("action_id"),double(P.Key.ActionId));O->SetNumberField(TEXT("event_id"),double(P.Key.EventId));
        O->SetBoolField(TEXT("active"),P.Active);O->SetNumberField(TEXT("stop"),int32(P.Stop));O->SetNumberField(TEXT("x"),P.Position.X);
        O->SetNumberField(TEXT("y"),P.Position.Y);O->SetNumberField(TEXT("traveled"),P.Traveled);
        O->SetNumberField(TEXT("emitted_at"),P.Source.AtTime);O->SetNumberField(TEXT("projectile_speed"),P.Source.ProjectileSpeed);
        Projectiles.Add(MakeShared<FJsonValueObject>(O));
    }
    for(const auto& B:World.Burns)
    {
        auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("target_id"),double(B.TargetId));O->SetNumberField(TEXT("action_id"),double(B.Key.ActionId));
        O->SetNumberField(TEXT("applied_at"),B.AppliedAt);O->SetNumberField(TEXT("next_tick_at"),B.NextTickAt);O->SetNumberField(TEXT("expires_at"),B.ExpiresAt);
        O->SetNumberField(TEXT("dps"),B.Dps);O->SetBoolField(TEXT("active"),B.Active);Burns.Add(MakeShared<FJsonValueObject>(O));
    }
    for(const auto& F:WA.FocusHistory)
    {
        auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("mutation_id"),double(F.MutationId));O->SetNumberField(TEXT("receipt_id"),double(F.ReceiptId));
        O->SetNumberField(TEXT("at_time"),F.AtTime);O->SetNumberField(TEXT("applied"),F.Applied);O->SetNumberField(TEXT("before"),F.Before);O->SetNumberField(TEXT("after"),F.After);
        FocusFacts.Add(MakeShared<FJsonValueObject>(O));
    }
    for(const auto& E:WA.Issued)
    {
        auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("event_id"),double(E.EventId));O->SetNumberField(TEXT("action_id"),double(E.ActionId));
        O->SetNumberField(TEXT("instance_id"),double(E.InstanceId));O->SetNumberField(TEXT("subhit_id"),E.SubhitId);O->SetNumberField(TEXT("at_time"),E.AtTime);
        O->SetNumberField(TEXT("window_end"),E.WindowEnd);O->SetNumberField(TEXT("damage"),E.Damage);O->SetNumberField(TEXT("stagger"),E.Stagger);
        O->SetNumberField(TEXT("focus_consumed"),E.FocusConsumed);O->SetNumberField(TEXT("ammo_consumed"),E.AmmoConsumed);
        O->SetBoolField(TEXT("critical"),E.Action.Critical);O->SetNumberField(TEXT("crit_multiplier"),E.Action.CritMultiplier);
        O->SetNumberField(TEXT("min_range"),E.MinRange);O->SetNumberField(TEXT("range"),E.Range);O->SetNumberField(TEXT("depth"),E.Depth);
        O->SetNumberField(TEXT("max_targets"),E.MaxTargets);O->SetNumberField(TEXT("second_target_ratio"),E.SecondTargetRatio);
        O->SetNumberField(TEXT("burn_dps"),E.BurnDps);O->SetNumberField(TEXT("burn_duration"),E.BurnDuration);
        IssuedFacts.Add(MakeShared<FJsonValueObject>(O));
    }
    for(const auto& F:WA.WeaponRuntimeHistory)
    {
        auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("event_id"),double(F.EventId));O->SetNumberField(TEXT("kind"),int32(F.Kind));
        O->SetNumberField(TEXT("instance_id"),double(F.Action.InstanceId));O->SetNumberField(TEXT("action_id"),double(F.Action.ActionId));
        O->SetNumberField(TEXT("at_time"),F.AtTime);O->SetNumberField(TEXT("ammo_before"),F.BeforeAmmo);O->SetNumberField(TEXT("ammo_after"),F.AfterAmmo);
        O->SetNumberField(TEXT("cooldown_after"),F.AfterCooldown);WeaponFacts.Add(MakeShared<FJsonValueObject>(O));
    }
    Row->SetArrayField(TEXT("slots"),Slots);Row->SetArrayField(TEXT("sources"),Sources);Row->SetArrayField(TEXT("targets"),Targets);Row->SetArrayField(TEXT("new_world_journal"),Events);
    Row->SetArrayField(TEXT("projectiles"),Projectiles);Row->SetArrayField(TEXT("burns"),Burns);
    Row->SetArrayField(TEXT("issued_action_events"),IssuedFacts);Row->SetArrayField(TEXT("focus_receipts"),FocusFacts);Row->SetArrayField(TEXT("weapon_runtime_receipts"),WeaponFacts);
    Trace.Add(MakeShared<FJsonValueObject>(Row));
    if(Elapsed>=FRangedProofState::DeadlineSeconds||Player->bDead||Game->bGameOver) {Fail(TEXT("ranged_deadline_or_player_death"));return;}
    if(S.Phase>0&&Now-S.PhaseAt>6.) {Fail(FString::Printf(TEXT("ranged_phase_%02d_timeout"),S.Phase));return;}
    switch(S.Phase)
    {
    case 0:
    {
        if(!Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1)) {Fail(TEXT("ranged_run_setup_failed"));return;}
        S={};S.Origin=Player->GetGroundPosition();
        DungeonEquipmentInventory::FItem Xbow;Xbow.ContentId="WPN-XBW-001";Xbow.Ammo=1;
        DungeonEquipmentInventory::FItem Staff;Staff.ContentId="WPN-STF-001";
        DungeonEquipmentInventory::FItem Spear;Spear.ContentId="WPN-SPR-001";
        const auto X=Game->RegisterEquipmentSource(TEXT("qa.ranged-proof.crossbow"),Xbow,S.Origin+FVector2D(32,0));
        S.SourceIds[0]=X.SourceId;S.InstanceIds[0]=X.InstanceId;
        bool ExtraSourcesValid=true;
        if(!bXBWReadyProof)
        {
            const auto F=Game->RegisterEquipmentSource(TEXT("qa.ranged-proof.staff"),Staff,S.Origin+FVector2D(60,0));
            const auto P=Game->RegisterEquipmentSource(TEXT("qa.ranged-proof.spear"),Spear,S.Origin+FVector2D(95,160));
            S.SourceIds[1]=F.SourceId;S.SourceIds[2]=P.SourceId;
            S.InstanceIds[1]=F.InstanceId;S.InstanceIds[2]=P.InstanceId;ExtraSourcesValid=F.Ok()&&P.Ok();
        }
        const auto& SetupView=Game->GetEquipmentView();S.StarterId=SetupView.Slots[0].InstanceId;
        if(!Require(bXBWReadyProof?TEXT("xbw_ready_real_run_starter_and_single_qa_source"):TEXT("ranged_real_run_starter_and_qa_sources"),X.Ok()&&ExtraSourcesValid&&Player->IsEquipmentBound()
            &&SetupView.ActiveSlot==0&&SetupView.Slots[0].ContentId==TEXT("WPN-SWD-001")&&SetupView.Slots[0].Grade==0
            &&S.StarterId&&!SetupView.Slots[1].InstanceId&&!SetupView.Slots[2].InstanceId))return;
        for(int32 I=bXBWReadyProof?0:2;I>=0;--I)
        {
            auto R=GetWorld()->SpawnActor<ADungeonFighter>();
            auto T=bXBWReadyProof?nullptr:GetWorld()->SpawnActor<ADungeonFighter>();
            if(!R||(!bXBWReadyProof&&!T)) {Fail(TEXT("ranged_target_spawn_failed"));return;}
            R->SetActorTickEnabled(false);R->bEnemy=true;R->bAIEnabled=false;R->MaxHealth=400.f;
            R->ResetFighter(S.Origin+FVector2D(180+90*I,0));Game->Enemies.Add(R);S.RangedTargets[I]=R;
            if(T)
            {
                T->SetActorTickEnabled(false);T->bEnemy=true;T->bAIEnabled=false;T->MaxHealth=12.f;
                T->ResetFighter(S.Origin+FVector2D(185+60*I,160));Game->Enemies.Add(T);S.SpearTargets[I]=T;
            }
        }
        Fixture=0;Game->bWaitingForStart=false;
        Game->LastMessage=TEXT("远程运行测试：正常拾取、弩装填与贯穿、火球地火、长枪三次最近目标；画面声音候选待审阅");
        if(bXBWReadyProof) Game->LastMessage=TEXT("猎弩：拾取后左右转向，观察双手持握；随后试射");
        Go(1);break;
    }
    case 1:
        if(Now-S.PhaseAt>.2)
        {
            bool Valid=Game->Enemies.Num()==(bXBWReadyProof?1:6)&&!Player->IsActorTickEnabled();
            for(int32 I=0;I<(bXBWReadyProof?1:3);++I)
            {
                auto R=S.RangedTargets[I].Get();auto T=S.SpearTargets[I].Get();
                Valid&=R&&R->GetRuntimeEntityId()&&!R->bAIEnabled&&R->Health==400.f&&R->GetArmorRating()==0&&R->GetArmorRating(true)==0
                    &&R->GetGroundPosition()==S.Origin+FVector2D(180+90*I,0);
                if(!bXBWReadyProof) Valid&=T&&T->GetRuntimeEntityId()&&!T->bAIEnabled&&T->Health==12.f
                    &&T->GetGroundPosition()==S.Origin+FVector2D(185+60*I,160);
            }
            if(!Require(bXBWReadyProof?TEXT("xbw_ready_single_authored_ground_target"):TEXT("ranged_fixture_authored_targets_and_ground_positions"),Valid))return;
            Go(2);
        }
        break;
    case 2:
        if(V.SelectedSourceId==S.SourceIds[0]&&UnitPulse(EKeys::E,Now))Go(3);
        break;
    case 3:
        if(V.Action.Active)
        {S.ActionObserved=true;S.OldHeld&=ActiveId()==S.StarterId;S.DurationValid&=Near(V.Action.Deadline-V.Action.Start,.35,1.e-12);}
        else if(S.ActionObserved)
        {
            if(!Require(TEXT("xbw_normal_e_035_commit_real_instance"),S.OldHeld&&S.DurationValid&&ActiveId()==S.InstanceIds[0]
                &&V.ActiveSlot==1&&Source(S.SourceIds[0])&&Source(S.SourceIds[0])->Consumed&&Instance(S.InstanceIds[0])&&Instance(S.InstanceIds[0])->Ammo==1))return;
            Go(bXBWReadyProof?40:4);
        }
        break;
    case 4:
        if(PulseAction(0,EKeys::J))
        {
            const auto& A=S.Actions[0];const auto E=Issued(A.ActionId);auto T=S.RangedTargets[0].Get();
            if(E&&T&&Count(EventKind::DirectHitCommitted,A.ActionId,T->GetRuntimeEntityId())==1)
            {
                const auto H=Event(EventKind::DirectHitCommitted,A.ActionId,T->GetRuntimeEntityId());
                if(!Require(TEXT("xbw_normal_j_single_world_bolt_and_real_hit"),E->ProjectileSpeed==950&&E->AmmoConsumed==1
                    &&E->FocusConsumed==0&&Count(EventKind::ProjectileEmitted,A.ActionId)==1&&H&&!H->Magic
                    &&Near(H->ActualHPLoss,E->Damage,.0002)&&Near(400-T->Health,E->Damage,.0002)&&Instance(S.InstanceIds[0])->Ammo==0
                    &&V.NextCritDraw==S.CritAtInput[0]+1&&Near(A.End-A.Start,.68)))return;
                Go(5);
            }
        }
        break;
    case 5:
    case 7:
    {
        const int32 I=S.Phase==5?0:1;const auto* X=Instance(S.InstanceIds[0]);const auto& A=WA.Action;
        if(A.Active&&A.Type==ActionKind::Reload)
        {S.ReloadStarts[I]=A.Start;S.ReloadEnds[I]=A.End;S.ReloadValid[I]&=A.Start==S.Actions[I].End&&Near(A.End-A.Start,1.10,1.e-12)&&X&&X->Ammo==0;}
        if(S.ReloadEnds[I]>0&&Now>=S.ReloadEnds[I]&&!A.Active)
        {
            const bool Good=S.ReloadValid[I]&&X&&X->Ammo==1&&Refills()==I+1&&Count(EventKind::ProjectileEmitted)==I+1;
            if(I==0)
            {
                if(!Require(TEXT("xbw_last_shot_full_recovery_then_110_reload"),Good))return;
                if(bXBWReadyProof)
                {
                    if(bXBWHeldIdentityProof && !Require(TEXT("xbw_ground_firing_and_all6_reload_keep_held_body_without_blade_trail"),
                        S.HeldFiringSeen&&S.HeldActionIdentityValid&&S.HeldReloadFrameMask==63))return;
                    if(bXBWPrimaryProof && !Require(TEXT("xbw_authored_primary_all_three_phases_match_drawn_actor_clock_and_stack"),
                        S.PrimaryPhaseMask==7&&S.PrimaryClockStackValid))return;
                    if(!Require(TEXT("xbw_ready_real_release_audio_request"),HUD->GetWorldWeaponAudioRequests(TEXT("XBW_RELEASE_01"))==1))return;
                    Check(TEXT("ranged_completed_within_45s"),Elapsed<FRangedProofState::DeadlineSeconds);
                    S.Phase=44;UnitReleaseInputs();bGameplayFinished=true;FinishAudioCapture();return;
                }
                Go(6);
            }
            else
            {if(!Require(TEXT("xbw_second_full_reload_no_repeat_or_refund"),Good&&X->CooldownDeadline==S.CrossbowCooldown&&WA.FocusHistory.empty()))return;Go(8);}
        }
        break;
    }
    case 40:
    case 42:
    {
        const int32 Side=S.Phase==40?0:1;
        const int32 Direction=Side==0?1:-1,Pose=HUD->GetRenderedWeaponBodyFrame();
        if(HUD->GetRenderedWeaponBodyUsed() && Player->AnimationName==TEXT("idle")
            &&Player->Facing==Direction&&HUD->GetRenderedWeaponBodyFacing()==Direction&&Pose>=0&&Pose<6)
        {
            const FString Prefix=TEXT("/Game/Production/FirstBatch/v016/XBWReadyIdle/");
            const auto Path=[&Prefix,Pose](const FString& Track)
            {const FString Name=FString::Printf(TEXT("T_XBWReadyIdle_%s_%03d_v001"),*Track,Pose);return Prefix+Name+TEXT(".")+Name;};
            const TArray<FString> Expected={Path(TEXT("body_far")),
                TEXT("/Game/Production/FirstBatch/v015/WeaponComponents/T_WPN_XBW_001_neutral_v001.T_WPN_XBW_001_neutral_v001"),
                Path(TEXT("body_support")),Path(TEXT("body_near"))};
            S.ReadyFrameMask[Side]|=1<<Pose;
            S.ReadyStackValid[Side]&=HUD->GetRenderedPlayerDrawStack()==Expected&&HUD->GetRenderedPlayerSpriteSize()==120.f;
        }
        // Actual native capture can hitch on first resource/readback. Keep normal
        // idle until every pose was really drawn; the unchanged six-second phase
        // deadline still rejects absent resources/poses. Never synthesize a mask.
        if(Now-S.PhaseAt>=1.1 && S.ReadyFrameMask[Side]==63)
        {
            if(!Require(Side==0?TEXT("xbw_ready_right_all6_actual_four_layer_stack"):TEXT("xbw_ready_left_all6_actual_four_layer_stack"),
                S.ReadyFrameMask[Side]==63&&S.ReadyStackValid[Side]))return;
            Go(Side==0?41:43);
        }
        break;
    }
    case 41:
    case 43:
    {
        const int32 Direction=S.Phase==41?-1:1;
        if(!S.InputIssued&&UnitPulse(Direction<0?EKeys::A:EKeys::D,Now)) S.InputIssued=true;
        if(S.InputIssued&&!bUnitEdgeDown&&Player->Facing==Direction) Go(S.Phase==41?42:4);
        break;
    }
    case 6:
        if(PulseAction(1,EKeys::K))
        {
            const auto& A=S.Actions[1];const auto E=Issued(A.ActionId);auto T1=S.RangedTargets[0].Get();auto T2=S.RangedTargets[1].Get();auto T3=S.RangedTargets[2].Get();
            if(E&&T1&&T2&&T3&&Count(EventKind::DirectHitCommitted,A.ActionId)==2)
            {
                const auto H1=Event(EventKind::DirectHitCommitted,A.ActionId,T1->GetRuntimeEntityId());
                const auto H2=Event(EventKind::DirectHitCommitted,A.ActionId,T2->GetRuntimeEntityId());
                if(!Require(TEXT("xbw_normal_k_nearest_two_second_sixty_percent"),E->ProjectileSpeed==1100&&E->MaxTargets==2&&E->SecondTargetRatio==.6
                    &&Count(EventKind::ProjectileEmitted,A.ActionId)==1&&H1&&H2&&!H1->Magic&&!H2->Magic&&H1->AtTime<H2->AtTime
                    &&Near(H1->ActualHPLoss,E->Damage,.0002)&&Near(H2->ActualHPLoss,E->Damage*.6,.0002)
                    &&H1->Stagger==24&&Near(H2->Stagger,14.4)&&T3->Health==400.f))return;
                const auto X=Instance(S.InstanceIds[0]);S.CrossbowCooldown=X?X->CooldownDeadline:0;
                if(!Require(TEXT("xbw_skill_single_crit_and_instance_cooldown"),X&&X->Ammo==0&&X->ReservedAmmo==0
                    &&V.NextCritDraw==S.CritAtInput[1]+1&&Near(X->CooldownDeadline,A.LockAt+6.,1.e-12)&&WA.FocusHistory.empty()))return;
                Go(7);
            }
        }
        break;
    case 8:
        if(Now-S.PhaseAt>.25&&UnitPulse(EKeys::Q,Now))Go(9);
        break;
    case 9:
        if(V.Action.Active) {S.ActionObserved=true;S.OldHeld&=ActiveId()==S.InstanceIds[0];S.DurationValid&=Near(V.Action.Deadline-V.Action.Start,.35,1.e-12);}
        else if(S.ActionObserved)
        {
            const auto X=Instance(S.InstanceIds[0]);
            if(!Require(TEXT("ranged_normal_q_preserves_crossbow_instance"),S.OldHeld&&S.DurationValid&&ActiveId()==S.StarterId&&V.ActiveSlot==0
                &&V.Slots[1].InstanceId==S.InstanceIds[0]&&X&&X->Ammo==1&&X->CooldownDeadline==S.CrossbowCooldown))return;
            Go(10);
        }
        break;
    case 10:
        if(Approach(S.Origin+FVector2D(60,0))&&V.SelectedSourceId==S.SourceIds[1]&&UnitPulse(EKeys::E,Now))
        {S.SelectionRevision=V.Revision;S.SelectionObserved=false;Go(11);}
        break;
    case 11:
        if(V.NeedsSlotSelection&&V.SelectionSlot==0&&!V.Action.Active&&V.Revision==S.SelectionRevision)
        {S.SelectionObserved=true;if(Now-S.PhaseAt>.3&&UnitPulse(EKeys::Enter,Now))Go(12);}
        break;
    case 12:
        if(V.Action.Active) {S.ActionObserved=true;S.OldHeld&=ActiveId()==S.StarterId&&V.Slots[1].InstanceId==S.InstanceIds[0];S.DurationValid&=Near(V.Action.Deadline-V.Action.Start,.35,1.e-12);}
        else if(S.ActionObserved)
        {
            bool Dropped=false;for(const auto& D:Game->GetEquipmentSources())Dropped|=!D.Consumed&&D.InstanceId==S.StarterId;
            if(!Require(TEXT("stf_full_slots_fresh_e_enter_slot0_commit"),S.SelectionObserved&&S.OldHeld&&S.DurationValid&&Dropped
                &&ActiveId()==S.InstanceIds[1]&&V.ActiveSlot==0&&V.Slots[1].InstanceId==S.InstanceIds[0]&&Source(S.SourceIds[1])&&Source(S.SourceIds[1])->Consumed))return;
            Go(13);
        }
        break;
    case 13:
        if(PulseAction(2,EKeys::J))
        {
            const auto& A=S.Actions[2];const auto E=Issued(A.ActionId);auto T=S.RangedTargets[0].Get();
            if(E&&T&&Count(EventKind::DirectHitCommitted,A.ActionId,T->GetRuntimeEntityId())==1&&Now>=A.End)
            {
                const auto H=Event(EventKind::DirectHitCommitted,A.ActionId,T->GetRuntimeEntityId());
                if(!Require(TEXT("stf_normal_j_magic_fireball_focus10_no_burn"),E->ProjectileSpeed==600&&E->FocusConsumed==10&&E->AmmoConsumed==0
                    &&E->BurnDps==0&&E->BurnDuration==0&&FocusReceipt(E->EventId,10)&&H&&H->Magic&&Near(H->ActualHPLoss,E->Damage,.0002)
                    &&Count(EventKind::ProjectileEmitted,A.ActionId)==1&&Count(EventKind::BurnApplied)==0&&V.NextCritDraw==S.CritAtInput[2]+1))return;
                Go(14);
            }
        }
        break;
    case 14:
        if(Approach(S.Origin+FVector2D(100,0)))
        {
            auto T1=S.RangedTargets[0].Get();auto T2=S.RangedTargets[1].Get();auto T3=S.RangedTargets[2].Get();const auto P=Player->GetGroundPosition();
            if(!Require(TEXT("stf_normal_d_enters_actual_fireline_range"),T1&&T2&&T3&&P.X>S.Origin.X+60&&Player->Facing>0
                &&T1->GetGroundPosition().X-P.X>0&&T2->GetGroundPosition().X-P.X<=240&&T3->GetGroundPosition().X-P.X>240
                &&FMath::Abs(T1->GetGroundPosition().Y-P.Y)<=35))return;
            Go(15);
        }
        break;
    case 15:
        if(PulseAction(3,EKeys::K))
        {
            const auto& A=S.Actions[3];const auto E=Issued(A.ActionId);
            if(E&&Count(EventKind::DirectHitCommitted,A.ActionId)==2)
            {
                const auto F=Instance(S.InstanceIds[1]);S.StaffCooldown=F?F->CooldownDeadline:0;
                bool HitsValid=true;
                for(int32 I=0;I<2;++I)
                {
                    auto T=S.RangedTargets[I].Get();
                    const auto H=T?Event(EventKind::DirectHitCommitted,A.ActionId,T->GetRuntimeEntityId()):nullptr;
                    HitsValid&=H&&H->Magic&&Near(H->ActualHPLoss,E->Damage,.0002)&&H->Stagger==E->Stagger
                        &&Count(EventKind::DirectHitCommitted,A.ActionId,T->GetRuntimeEntityId())==1
                        &&Count(EventKind::BurnApplied,A.ActionId,T->GetRuntimeEntityId())==1;
                }
                auto Third=S.RangedTargets[2].Get();
                HitsValid&=Third&&Third->Health==400.f&&Count(EventKind::DirectHitCommitted,A.ActionId,Third->GetRuntimeEntityId())==0;
                if(!Require(TEXT("stf_normal_k_real_ground_window_focus24"),E->Shape==DungeonContentCombat::EShape::GroundRectangle&&E->Origin.Height==0
                    &&E->Range==240&&E->Depth==35&&E->FocusConsumed==24&&E->BurnDps==2&&E->BurnDuration==3&&FocusReceipt(E->EventId,24)
                    &&Count(EventKind::WindowCreated,A.ActionId)==1&&Count(EventKind::BurnApplied,A.ActionId)==2
                    &&HitsValid&&V.NextCritDraw==S.CritAtInput[3]+1&&F&&Near(F->CooldownDeadline,A.LockAt+7.,1.e-12)))return;
                Go(16);
            }
        }
        break;
    case 16:
        if(Now>=S.Actions[3].ActiveAt+3.25)
        {
            bool Good=Count(EventKind::BurnTickCommitted,S.Actions[3].ActionId)==6;
            for(int32 I=0;I<2;++I)
            {
                auto T=S.RangedTargets[I].Get();if(!T){Good=false;continue;}
                const uint64 Id=T->GetRuntimeEntityId();const FDungeonWorldBurn* B=nullptr;
                for(const auto& Burn:World.Burns)if(Burn.TargetId==Id)B=&Burn;
                int32 N=0;double Loss=0;for(const auto& E:World.Events)if(E.Kind==EventKind::BurnTickCommitted&&E.Key.ActionId==S.Actions[3].ActionId&&E.TargetId==Id)
                {++N;Loss+=E.ActualHPLoss;Good&=E.Damage==2&&E.ActualHPLoss==2&&E.Stagger==0&&E.Magic&&B&&Near(E.AtTime,B->AppliedAt+N,1.e-12);}
                Good&=B&&!B->Active&&B->Dps==2&&Near(B->ExpiresAt-B->AppliedAt,3.,1.e-12)&&N==3&&Loss==6;
            }
            if(!Require(TEXT("stf_actual_burn_three_ticks_fixed2_per_target"),Good&&S.RangedTargets[2].IsValid()&&S.RangedTargets[2]->Health==400.f))return;
            Go(17);
        }
        break;
    case 17:
        if(Approach(S.Origin+FVector2D(95,160))&&V.SelectedSourceId==S.SourceIds[2]&&UnitPulse(EKeys::E,Now))
        {S.SelectionRevision=V.Revision;S.SelectionObserved=false;Go(18);}
        break;
    case 18:
        if(V.NeedsSlotSelection&&V.SelectionSlot==0&&!V.Action.Active&&V.Revision==S.SelectionRevision)
        {S.SelectionObserved=true;if(Now-S.PhaseAt>.3&&UnitPulse(EKeys::Right,Now))Go(19);}
        break;
    case 19:
        if(V.NeedsSlotSelection&&V.SelectionSlot==1&&!bUnitEdgeDown&&UnitPulse(EKeys::Enter,Now))Go(20);
        break;
    case 20:
        if(V.Action.Active) {S.ActionObserved=true;S.OldHeld&=ActiveId()==S.InstanceIds[1]&&V.Slots[1].InstanceId==S.InstanceIds[0];S.DurationValid&=Near(V.Action.Deadline-V.Action.Start,.35,1.e-12);}
        else if(S.ActionObserved)
        {
            bool Dropped=false;for(const auto& D:Game->GetEquipmentSources())Dropped|=!D.Consumed&&D.InstanceId==S.InstanceIds[0]&&D.Item.Ammo==1&&D.Item.SkillCooldownDeadline==S.CrossbowCooldown;
            if(!Require(TEXT("spr_full_slots_e_right_enter_backup_commit"),S.SelectionObserved&&S.OldHeld&&S.DurationValid&&Dropped
                &&ActiveId()==S.InstanceIds[1]&&V.Slots[1].InstanceId==S.InstanceIds[2]&&Source(S.SourceIds[2])&&Source(S.SourceIds[2])->Consumed))return;
            Go(21);
        }
        break;
    case 21:
        if(Now-S.PhaseAt>.25&&UnitPulse(EKeys::Q,Now))Go(22);
        break;
    case 22:
        if(V.Action.Active) {S.ActionObserved=true;S.OldHeld&=ActiveId()==S.InstanceIds[1];S.DurationValid&=Near(V.Action.Deadline-V.Action.Start,.35,1.e-12);}
        else if(S.ActionObserved)
        {
            if(!Require(TEXT("spr_normal_q_activates_acquired_instance"),S.OldHeld&&S.DurationValid&&V.ActiveSlot==1&&ActiveId()==S.InstanceIds[2]
                &&V.Slots[0].InstanceId==S.InstanceIds[1]&&Instance(S.InstanceIds[1])&&Instance(S.InstanceIds[1])->CooldownDeadline==S.StaffCooldown))return;
            Go(23);
        }
        break;
    case 23:
        if(PulseAction(4,EKeys::K)&&Now>=S.Actions[4].End)
        {
            const auto& A=S.Actions[4];bool Good=Count(EventKind::WindowCreated,A.ActionId)==3&&Count(EventKind::DirectHitCommitted,A.ActionId)==3;
            const double Times[3]={.18,.28,.38};
            for(int32 I=0;I<3;++I)
            {
                auto T=S.SpearTargets[I].Get();const auto E=Issued(A.ActionId,uint32(I));
                const auto H=T?Event(EventKind::DirectHitCommitted,A.ActionId,T->GetRuntimeEntityId(),I):nullptr;
                Good&=T&&T->bDead&&T->Health==0&&E&&H&&E->MaxTargets==1&&H->ActualHPLoss==12&&H->Stagger==6&&!H->Magic
                    &&Near(H->Damage,E->Damage)&&H->AtTime>=A.Start+Times[I]&&H->AtTime<A.Start+Times[I]+.04
                    &&Count(EventKind::DirectHitCommitted,A.ActionId,T->GetRuntimeEntityId(),I)==1;
            }
            if(!Require(TEXT("spr_normal_k_three_independent_nearest_targets"),Good&&V.NextCritDraw==S.CritAtInput[4]+1&&!WA.Action.Active))return;
            Go(24);
        }
        break;
    case 24:
        if(Now-S.PhaseAt>.25&&UnitPulse(EKeys::Q,Now))
        {S.FinalSwitchAt=Now;S.FocusBeforeFinalSwitch=WA.Budget.Focus;S.LastSpendBeforeFinalSwitch=WA.Budget.LastActualSpend;
            S.FocusCursorBeforeFinalSwitch=WA.NextFocusMutationId;S.FocusHistoryBeforeFinalSwitch=int32(WA.FocusHistory.size());Go(25);}
        break;
    case 25:
        if(V.Action.Active) {S.ActionObserved=true;S.OldHeld&=ActiveId()==S.InstanceIds[2];S.DurationValid&=Near(V.Action.Deadline-V.Action.Start,.35,1.e-12);}
        else if(S.ActionObserved)
        {
            const auto F=Instance(S.InstanceIds[1]);
            if(!Require(TEXT("ranged_normal_q_back_to_same_staff_without_reset"),S.OldHeld&&S.DurationValid&&V.ActiveSlot==0&&ActiveId()==S.InstanceIds[1]
                &&V.Slots[1].InstanceId==S.InstanceIds[2]&&F&&F->CooldownDeadline==S.StaffCooldown&&WA.Budget.LastActualSpend==S.LastSpendBeforeFinalSwitch
                &&WA.NextFocusMutationId==S.FocusCursorBeforeFinalSwitch&&int32(WA.FocusHistory.size())==S.FocusHistoryBeforeFinalSwitch
                &&WA.Budget.Focus>=S.FocusBeforeFinalSwitch&&Near(Player->Focus,WA.Budget.Focus,.0001)))return;
            Go(26);
        }
        break;
    case 26:
        if(Now-S.PhaseAt>=1.)
        {
            if(!Require(TEXT("ranged_hud_real_release_launch_burn_audio_requests"),HUD->GetWorldWeaponAudioRequests(TEXT("XBW_RELEASE_01"))>=2
                &&HUD->GetWorldWeaponAudioRequests(TEXT("FIRE_LAUNCH_01"))>=2&&HUD->GetWorldWeaponAudioRequests(TEXT("FIRE_BURN_SHORT_01"))>=6
                &&Count(EventKind::ProjectileEmitted)==3&&Count(EventKind::WindowCreated)==4&&Count(EventKind::DirectHitCommitted)==9
                &&Count(EventKind::BurnTickCommitted)==6&&WA.FocusHistory.size()==2&&Refills()==2))return;
            Check(TEXT("ranged_completed_within_45s"),Elapsed<FRangedProofState::DeadlineSeconds);
            UnitReleaseInputs();bGameplayFinished=true;FinishAudioCapture();
        }
        break;
    default:Fail(TEXT("ranged_invalid_phase"));break;
    }
}
