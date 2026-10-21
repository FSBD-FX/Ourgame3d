// Opt-in recorder implementation, not the independent socket acceptance suite.
// Only phase0 initializes QA sources/targets/start gate. Later actions use keys.
void ADungeonContentProbe::TickXBWReloadSocketProof()
{
    if(bGameplayFinished)return;
    auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this));
    auto Player=Game?Game->GetPlayerFighter():nullptr;
    auto Controller=UGameplayStatics::GetPlayerController(this,0);
    auto HUD=Controller?Cast<ADungeonHUD>(Controller->GetHUD()):nullptr;
    auto& S=XBWReloadSocketProof;
    const auto Fail=[this,&S](const FString& Why)
    {
        UnitFailure=Why;UnitReleaseInputs();bGameplayFinished=true;
        const FString End=TEXT("xbw_socket_completed_within_55s");
        if(!S.Checked.Contains(End)){S.Checked.Add(End);Check(End,false);}
        FinishAudioCapture();
    };
    if(!Game||!Player||!Controller||!HUD){Fail(TEXT("xbw_socket_missing_game_player_controller_or_hud"));return;}
    if(bFirstUnit||bEquipmentProof||bArmorLayerProof||bRangedProof||bSceneProof)
    {Fail(TEXT("xbw_socket_conflicting_proof_flags"));return;}
    const double Now=Game->GetSimulationTime();
    if(bUnitEdgeDown&&Now>UnitEdgeAt)
    {Key(UnitEdgeKey,false);bUnitEdgeDown=false;UnitReleasedAt=Now;}
    using ActionKind=DungeonWeaponActions::EAction;
    using WeaponKind=DungeonContentCombat::EWeapon;
    using EventKind=EDungeonWorldWeaponEventKind;
    using MutationKind=DungeonWeaponActions::EWeaponMutation;
    const auto& V=Game->GetEquipmentView();
    const auto& WA=Player->GetWeaponActionsState();
    const auto& World=Game->GetWeaponWorldState();
    const auto Near=[](double A,double B,double E=1.e-5){return FMath::Abs(A-B)<=E;};
    const auto OriginSame=[&Near](const DungeonWeaponActions::FOrigin& A,const DungeonWeaponActions::FOrigin& B)
    {return Near(A.X,B.X)&&Near(A.Y,B.Y)&&Near(A.Height,B.Height);};
    const auto Instance=[&WA](uint64 Id)->const DungeonWeaponActions::FInstance*
    {for(const auto& I:WA.Instances)if(I.InstanceId==Id)return &I;return nullptr;};
    const auto ActiveId=[&V](){return V.Slots[V.ActiveSlot].InstanceId;};
    const auto Source=[Game](uint64 Id)->const FDungeonEquipmentSourceView*
    {for(const auto& I:Game->GetEquipmentSources())if(I.SourceId==Id)return &I;return nullptr;};
    const auto Refills=[&WA,&S](double At=MAX_dbl)
    {int32 N=0;for(const auto& R:WA.WeaponRuntimeHistory)if(R.Kind==MutationKind::ReloadCompleted
        &&R.Action.InstanceId==S.InstanceId&&R.AtTime<=At)++N;return N;};
    const auto AmmoAt=[&WA,&S](double At)
    {double Ammo=1.;for(const auto& R:WA.WeaponRuntimeHistory)if(R.Action.InstanceId==S.InstanceId&&R.AtTime<=At)Ammo=R.AfterAmmo;return Ammo;};
    const auto Count=[&World](EventKind Kind,uint64 Action=0,uint64 Target=0)
    {int32 N=0;for(const auto& E:World.Events)if(E.Kind==Kind&&(!Action||E.Key.ActionId==Action)&&(!Target||E.TargetId==Target))++N;return N;};
    const auto FindEvent=[&World](EventKind Kind,uint64 Action,uint64 Target=0)->const FDungeonWorldWeaponEvent*
    {for(const auto& E:World.Events)if(E.Kind==Kind&&E.Key.ActionId==Action&&(!Target||E.TargetId==Target))return &E;return nullptr;};
    const auto Require=[this,&S,&Fail](const FString& Name,bool Passed)
    {
        if(S.Checked.Contains(Name)){Fail(TEXT("xbw_socket_duplicate_check_attempt:")+Name);return false;}
        S.Checked.Add(Name);Check(Name,Passed);if(!Passed)Fail(Name);return Passed;
    };
    const auto Go=[this,&S,Now](int32 Phase)
    {UnitMove(0,0);S.Phase=Phase;S.PhaseAt=Now;S.InputAt=-1;S.ArrivalAt=-1;S.InputIssued=false;S.ActionObserved=false;};
    const auto Pulse=[this,&S,Now](FKey K)
    {
        if(S.InputIssued)return true;
        if(Now-S.PhaseAt<.15||!UnitPulse(K,Now))return false;
        S.InputIssued=true;S.InputAt=Now;return true;
    };
    const auto AddReload=[&S](const DungeonWeaponActions::FAction& A)
    {
        if(!A.Active||A.Weapon!=WeaponKind::XBW001||A.Type!=ActionKind::Reload)return;
        for(const auto& R:S.Reloads)if(R.ActionId==A.ActionId)return;
        S.Reloads.Add(A);
    };
    if(S.Phase>0)
    {
        // Observe a genuinely accepted action or its actual issued snapshot;
        // missing rendered frames are never reconstructed into a frame mask.
        if(S.PendingShotInput>=0&&S.CurrentShot<0)
        {
            const DungeonWeaponActions::FAction* Accepted=nullptr;
            if(WA.Action.Active&&WA.Action.Type==ActionKind::Primary&&WA.Action.Weapon==WeaponKind::XBW001
                &&WA.Action.Start>=S.PendingShotInput)Accepted=&WA.Action;
            else for(const auto& E:WA.Issued)if(E.Action.Type==ActionKind::Primary&&E.Action.Weapon==WeaponKind::XBW001
                &&E.Action.Start>=S.PendingShotInput)Accepted=&E.Action;
            if(Accepted)
            {
                FXBWReloadSocketProofState::FShot Shot;Shot.Side=S.Phase==15?-1:S.Side;Shot.Action=*Accepted;
                const int32 TargetSide=Accepted->Facing<0?1:0;
                Shot.TargetId=S.Targets[TargetSide].IsValid()?S.Targets[TargetSide]->GetRuntimeEntityId():0;
                S.CurrentShot=S.Shots.Add(Shot);if(Shot.Side>=0)++S.ShotsPerSide[Shot.Side];S.PendingShotInput=-1;
            }
        }
        for(auto& Shot:S.Shots)if(!Shot.EmissionObserved)
            for(const auto& P:World.Projectiles)if(P.Key.ActionId==Shot.Action.ActionId)
            {Shot.Emission=P;Shot.EmissionObserved=true;break;}
        AddReload(WA.Action);
    }

    const auto Path=[](const FString& Root,const FString& Prefix,const FString& Track,int32 Frame)
    {const FString N=FString::Printf(TEXT("%s_%s_%03d_v001"),*Prefix,*Track,Frame);return Root+N+TEXT(".")+N;};
    const auto WeaponPath=[&Path](int32 Index)
    {return Index<0?FString(TEXT("/Game/Production/FirstBatch/v015/WeaponComponents/T_WPN_XBW_001_neutral_v001.T_WPN_XBW_001_neutral_v001"))
        :Path(TEXT("/Game/Production/FirstBatch/v018/XBWReload/"),TEXT("T_XBWReload"),TEXT("weapon"),Index);};
    const auto DrawClip=HUD->GetRenderedWeaponBodyClip();
    const int32 DrawFrame=HUD->GetRenderedWeaponBodyFrame(),DrawFacing=HUD->GetRenderedWeaponBodyFacing(),DrawState=HUD->GetRenderedWeaponStateIndex();
    const double DrawTime=HUD->GetRenderedWeaponBodySampleTime();
    const uint64 DrawAction=HUD->GetRenderedWeaponBodyActionId(),DrawInstance=HUD->GetRenderedWeaponBodyInstanceId();
    bool DrawValid=false;
    if(S.InstanceId&&HUD->GetRenderedWeaponBodyUsed()&&DrawInstance==S.InstanceId&&FMath::IsFinite(DrawTime)&&DrawTime<=Now
        &&(DrawFacing==1||DrawFacing==-1))
    {
        FString Root,Prefix;int32 Expected=-1,Side=DrawFacing<0?1:0;bool ExpectedState=false;
        if(DrawClip==TEXT("xbw_ready_idle")&&DrawFrame>=0&&DrawFrame<6)
        {
            Root=TEXT("/Game/Production/FirstBatch/v016/XBWReadyIdle/");Prefix=TEXT("T_XBWReadyIdle");Expected=DrawFrame;
            const int32 StateAtDraw=AmmoAt(DrawTime)==0?0:Refills(DrawTime)>0?3:-1;
            ExpectedState=DrawState==StateAtDraw;
        }
        else if(DrawClip==TEXT("xbw_primary"))for(const auto& Shot:S.Shots)
        {
            const auto& A=Shot.Action;if(A.ActionId!=DrawAction||DrawTime<A.Start||DrawTime>=A.End)continue;
            Root=TEXT("/Game/Production/FirstBatch/v017/XBWPrimary/");Prefix=TEXT("T_XBWPrimary");Side=Shot.Side;
            const int32 Base=DrawTime<A.ActiveAt?0:DrawTime<A.ActiveEnd?2:4;
            const double Begin=Base==0?A.Start:Base==2?A.ActiveAt:A.ActiveEnd,End=Base==0?A.ActiveAt:Base==2?A.ActiveEnd:A.End;
            Expected=Base+(DrawTime<(Begin+End)*.5?0:1);
            ExpectedState=DrawState==(AmmoAt(DrawTime)==0?0:Refills(DrawTime)>0?3:-1)&&DrawFacing==int32(A.Facing);break;
        }
        else if(DrawClip==TEXT("xbw_reload_four_keyposes"))for(const auto& R:S.Reloads)
        {
            if(R.ActionId!=DrawAction||DrawTime<R.Start||DrawTime>=R.End)continue;
            Root=TEXT("/Game/Production/FirstBatch/v018/XBWReload/");Prefix=TEXT("T_XBWReload");
            const double U=(DrawTime-R.Start)/(R.End-R.Start);
            Expected=U<.2/1.1?0:U<.6/1.1?1:U<.85/1.1?2:3;ExpectedState=DrawState==Expected;Side=-1;
            double Latest=-1,LockedFacing=0;for(const auto& Shot:S.Shots)if(Shot.Action.End<=R.Start&&Shot.Action.Start>Latest)
            {Latest=Shot.Action.Start;Side=Shot.Side;LockedFacing=Shot.Action.Facing;}
            ExpectedState&=Latest>=0&&DrawFacing==int32(LockedFacing);break;
        }
        if(Expected>=0)
        {
            const TArray<FString> ExpectedStack={Path(Root,Prefix,TEXT("body_far"),Expected),WeaponPath(DrawState),
                Path(Root,Prefix,TEXT("body_support"),Expected),Path(Root,Prefix,TEXT("body_near"),Expected)};
            DrawValid=Expected==DrawFrame&&ExpectedState&&HUD->GetRenderedPlayerDrawStack()==ExpectedStack
                &&HUD->GetQueuedPlayerMeleeTrailCount()==0;
            if(Side>=0&&Side<2)
            {
                if(DrawClip==TEXT("xbw_ready_idle")){S.ReadyValid[Side]&=DrawValid;if(DrawValid)S.ReadyMask[Side]|=1<<Expected;}
                else if(DrawClip==TEXT("xbw_primary")){S.PrimaryValid[Side]&=DrawValid;if(DrawValid)S.PrimaryMask[Side]|=1<<Expected;}
                else{S.ReloadValid[Side]&=DrawValid;if(DrawValid)S.ReloadMask[Side]|=1<<Expected;}
            }
        }
    }
    const auto LoadedDraw=[&](){return DrawValid&&DrawClip==TEXT("xbw_ready_idle")&&DrawState==3&&DrawInstance==S.InstanceId;};
    const auto ShotValid=[&](const FXBWReloadSocketProofState::FShot& Shot)
    {
        if(!Shot.EmissionObserved)return false;
        const auto& P=Shot.Emission;const auto& E=P.Source;const auto& Pose=P.PoseSocket;
        const auto* Hit=FindEvent(EventKind::DirectHitCommitted,Shot.Action.ActionId,Shot.TargetId);
        const auto* Emit=FindEvent(EventKind::ProjectileEmitted,Shot.Action.ActionId);
        const double Forward=(Pose.EmitX-Pose.RootX)*Pose.BodySize/512./.65;
        const double HandHeight=(Pose.RootY-Pose.EmitY)*Pose.BodySize/512./.70;
        return P.HasPoseSocket&&Pose.Supported&&!Pose.CustomOverride&&!Pose.GroundPoseFallback
            &&P.UsesActorRangeAnchor&&Pose.Frame==2&&Pose.Clip==DungeonWeaponPoseSocket::EClip::Primary
            &&Pose.SampleTime==E.AtTime&&E.AtTime==Shot.Action.ActiveAt&&Pose.ActionId==Shot.Action.ActionId
            &&Pose.InstanceId==S.InstanceId&&Pose.Facing==Shot.Action.Facing&&E.Origin.Height==0&&P.RangeAnchor.Height==0
            &&OriginSame(Pose.CombatOrigin,E.Origin)&&OriginSame(Pose.ActorOrigin,P.RangeAnchor)&&Near(E.Origin.Y,P.RangeAnchor.Y)
            &&Forward>0&&Near((E.Origin.X-P.RangeAnchor.X)*Shot.Action.Facing,Forward)
            &&Near(P.LaunchForwardDistance,Forward)&&HandHeight>65
            &&Near(Pose.PresentationOrigin.Height,Pose.CombatOrigin.Height+HandHeight)
            &&Near(Pose.PresentationOrigin.X,E.Origin.X)&&Near(Pose.PresentationOrigin.Y,E.Origin.Y)
            &&Emit&&Emit->HasPoseSocket&&Emit->PoseSocket.SampleTime==E.AtTime&&OriginSame(Emit->RangeAnchor,P.RangeAnchor)
            &&Count(EventKind::ProjectileEmitted,Shot.Action.ActionId)==1&&Hit&&Hit->HasPoseSocket&&!Hit->Magic
            &&Hit->ActualHPLoss>0&&Near(Hit->ActualHPLoss,E.Damage,.0002)&&Hit->PoseSocket.SampleTime==E.AtTime
            &&OriginSame(Hit->PoseSocket.PresentationOrigin,Pose.PresentationOrigin)
            &&Count(EventKind::DirectHitCommitted,Shot.Action.ActionId)==1&&Count(EventKind::DirectHitCommitted,Shot.Action.ActionId,Shot.TargetId)==1;
    };

    // Readonly trace records both clocks; a prior GPU draw is not relabeled as
    // the current post-batch Actor state. World snapshots are actual emissions.
    if(S.Phase>0)
    {
        auto R=MakeShared<FJsonObject>();const auto ActorPose=Player->GetWeaponPoseSocket();const auto XY=Player->GetGroundPosition();
        R->SetStringField(TEXT("record_type"),TEXT("xbw_reload_socket_normal_input_post_batch_observation"));
        R->SetNumberField(TEXT("fixture_phase"),S.Phase);R->SetNumberField(TEXT("side"),S.Side);
        R->SetNumberField(TEXT("sim_time_s"),Now);R->SetNumberField(TEXT("wall_offset_s"),Elapsed);
        R->SetStringField(TEXT("run_guid"),V.RunGuid.ToString());R->SetNumberField(TEXT("room_instance_id"),double(V.RoomInstanceId));
        R->SetNumberField(TEXT("player_x"),XY.X);R->SetNumberField(TEXT("player_y"),XY.Y);R->SetNumberField(TEXT("player_facing"),Player->Facing);
        R->SetBoolField(TEXT("waiting_for_start"),Game->bWaitingForStart);R->SetNumberField(TEXT("weapon_clock"),WA.Time);
        R->SetNumberField(TEXT("active_instance_id"),double(WA.EquippedId));R->SetNumberField(TEXT("active_slot"),V.ActiveSlot);
        R->SetNumberField(TEXT("source_id"),double(S.SourceId));R->SetBoolField(TEXT("source_consumed"),Source(S.SourceId)&&Source(S.SourceId)->Consumed);
        R->SetNumberField(TEXT("actual_ammo"),Instance(S.InstanceId)?Instance(S.InstanceId)->Ammo:-1.);
        R->SetNumberField(TEXT("slot_ammo"),V.Slots[1].Ammo);R->SetNumberField(TEXT("actual_reserved_ammo"),Instance(S.InstanceId)?Instance(S.InstanceId)->ReservedAmmo:-1.);
        R->SetNumberField(TEXT("actual_reload_commits"),Refills());R->SetNumberField(TEXT("crit_next_draw"),double(V.NextCritDraw));
        R->SetNumberField(TEXT("action_id"),double(WA.Action.ActionId));R->SetNumberField(TEXT("action_type"),int32(WA.Action.Type));
        R->SetBoolField(TEXT("action_active"),WA.Action.Active);R->SetNumberField(TEXT("action_start"),WA.Action.Start);
        R->SetNumberField(TEXT("action_active_at"),WA.Action.ActiveAt);R->SetNumberField(TEXT("action_active_end"),WA.Action.ActiveEnd);
        R->SetNumberField(TEXT("action_end"),WA.Action.End);R->SetNumberField(TEXT("last_reload_cancel_time"),WA.LastReloadCancelTime);
        R->SetStringField(TEXT("hud_clip"),DrawClip);R->SetNumberField(TEXT("hud_frame"),DrawFrame);
        R->SetNumberField(TEXT("hud_facing"),DrawFacing);R->SetNumberField(TEXT("hud_weapon_state_index"),DrawState);
        R->SetBoolField(TEXT("hud_weapon_state_is_resource_authority"),false);R->SetBoolField(TEXT("hud_draw_clock_stack_valid"),DrawValid);
        R->SetNumberField(TEXT("hud_action_id"),double(DrawAction));R->SetNumberField(TEXT("hud_instance_id"),double(DrawInstance));
        R->SetNumberField(TEXT("hud_sample_time"),DrawTime);R->SetNumberField(TEXT("hud_trails"),HUD->GetQueuedPlayerMeleeTrailCount());
        const auto ScreenEmit=HUD->GetRenderedWeaponBodyEmitScreen();R->SetNumberField(TEXT("hud_emit_screen_x"),ScreenEmit.X);R->SetNumberField(TEXT("hud_emit_screen_y"),ScreenEmit.Y);
        R->SetNumberField(TEXT("actor_socket_sample_time"),ActorPose.SampleTime);R->SetNumberField(TEXT("actor_socket_frame"),ActorPose.Frame);
        R->SetNumberField(TEXT("actor_current_weapon_state_index"),ActorPose.WeaponStateIndex);
        R->SetNumberField(TEXT("actor_combat_x"),ActorPose.CombatOrigin.X);R->SetNumberField(TEXT("actor_combat_y"),ActorPose.CombatOrigin.Y);
        R->SetNumberField(TEXT("actor_combat_height"),ActorPose.CombatOrigin.Height);R->SetNumberField(TEXT("actor_presentation_height"),ActorPose.PresentationOrigin.Height);
        R->SetNumberField(TEXT("right_ready_mask"),S.ReadyMask[0]);R->SetNumberField(TEXT("left_ready_mask"),S.ReadyMask[1]);
        R->SetNumberField(TEXT("right_primary_mask"),S.PrimaryMask[0]);R->SetNumberField(TEXT("left_primary_mask"),S.PrimaryMask[1]);
        R->SetNumberField(TEXT("right_reload_mask"),S.ReloadMask[0]);R->SetNumberField(TEXT("left_reload_mask"),S.ReloadMask[1]);
        R->SetNumberField(TEXT("right_attempts"),S.ShotsPerSide[0]);R->SetNumberField(TEXT("left_attempts"),S.ShotsPerSide[1]);
        R->SetBoolField(TEXT("fixture_targets_are_static_plain_qa_actors"),true);
        R->SetBoolField(TEXT("initial_start_gate_is_qa_initialization_not_begin_run_contract"),true);
        TArray<TSharedPtr<FJsonValue>> Stack,Targets,Events,History;
        for(const auto& P:HUD->GetRenderedPlayerDrawStack())Stack.Add(MakeShared<FJsonValueString>(P));
        for(int32 I=0;I<2;++I)if(auto T=S.Targets[I].Get())
        {auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("side"),I);O->SetNumberField(TEXT("entity_id"),double(T->GetRuntimeEntityId()));
            O->SetNumberField(TEXT("x"),T->GetGroundPosition().X);O->SetNumberField(TEXT("y"),T->GetGroundPosition().Y);O->SetNumberField(TEXT("hp"),T->Health);Targets.Add(MakeShared<FJsonValueObject>(O));}
        for(const auto& E:World.Events)if(E.Sequence>S.WorldCursor)
        {
            auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("sequence"),double(E.Sequence));O->SetNumberField(TEXT("kind"),int32(E.Kind));
            O->SetNumberField(TEXT("owner_id"),double(E.Key.OwnerId));O->SetNumberField(TEXT("room_id"),double(E.Key.RoomInstanceId));
            O->SetNumberField(TEXT("action_id"),double(E.Key.ActionId));O->SetNumberField(TEXT("event_id"),double(E.Key.EventId));
            O->SetNumberField(TEXT("subhit_id"),E.Key.SubhitId);O->SetNumberField(TEXT("target_id"),double(E.TargetId));O->SetNumberField(TEXT("at_time"),E.AtTime);
            O->SetNumberField(TEXT("x"),E.Position.X);O->SetNumberField(TEXT("y"),E.Position.Y);O->SetNumberField(TEXT("combat_height"),E.Height);
            O->SetNumberField(TEXT("actual_hp_loss"),E.ActualHPLoss);O->SetBoolField(TEXT("has_pose_socket"),E.HasPoseSocket);
            O->SetNumberField(TEXT("socket_sample_time"),E.PoseSocket.SampleTime);O->SetNumberField(TEXT("socket_frame"),E.PoseSocket.Frame);
            O->SetNumberField(TEXT("socket_facing"),E.PoseSocket.Facing);O->SetNumberField(TEXT("socket_instance_id"),double(E.PoseSocket.InstanceId));
            O->SetNumberField(TEXT("emission_weapon_state_index"),E.PoseSocket.WeaponStateIndex);
            O->SetNumberField(TEXT("native_emit_x"),E.PoseSocket.EmitX);O->SetNumberField(TEXT("native_emit_y"),E.PoseSocket.EmitY);
            O->SetNumberField(TEXT("component_emit_x"),E.PoseSocket.ComponentEmitX);O->SetNumberField(TEXT("component_emit_y"),E.PoseSocket.ComponentEmitY);
            O->SetNumberField(TEXT("source_x"),E.PoseSocket.CombatOrigin.X);O->SetNumberField(TEXT("source_y"),E.PoseSocket.CombatOrigin.Y);
            O->SetNumberField(TEXT("presentation_height"),E.PoseSocket.PresentationOrigin.Height);
            O->SetNumberField(TEXT("range_anchor_x"),E.RangeAnchor.X);O->SetNumberField(TEXT("range_anchor_y"),E.RangeAnchor.Y);
            O->SetBoolField(TEXT("launch_obstructed"),E.LaunchObstructed);Events.Add(MakeShared<FJsonValueObject>(O));S.WorldCursor=E.Sequence;
        }
        for(const auto& E:WA.WeaponRuntimeHistory)
        {auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("event_id"),double(E.EventId));O->SetNumberField(TEXT("kind"),int32(E.Kind));
            O->SetNumberField(TEXT("instance_id"),double(E.Action.InstanceId));O->SetNumberField(TEXT("action_id"),double(E.Action.ActionId));
            O->SetNumberField(TEXT("at_time"),E.AtTime);O->SetNumberField(TEXT("before_ammo"),E.BeforeAmmo);O->SetNumberField(TEXT("after_ammo"),E.AfterAmmo);History.Add(MakeShared<FJsonValueObject>(O));}
        R->SetArrayField(TEXT("actual_draw_stack"),Stack);R->SetArrayField(TEXT("qa_targets"),Targets);R->SetArrayField(TEXT("new_world_journal"),Events);
        R->SetArrayField(TEXT("actual_weapon_runtime_history"),History);
        for(const auto& K:{EKeys::A,EKeys::D,EKeys::W,EKeys::S,EKeys::E,EKeys::Enter,EKeys::J,EKeys::T,EKeys::Q})
            R->SetBoolField(TEXT("input_held_")+K.GetFName().ToString(),Controller->IsInputKeyDown(K));
        Trace.Add(MakeShared<FJsonValueObject>(R));
    }
    if(Elapsed>=FXBWReloadSocketProofState::DeadlineSeconds||Player->bDead||Game->bGameOver)
    {Fail(TEXT("xbw_socket_total_deadline_or_death"));return;}
    if(S.Phase>1&&Now-S.PhaseAt>12.){Fail(FString::Printf(TEXT("xbw_socket_phase_%02d_timeout"),S.Phase));return;}
    switch(S.Phase)
    {
    case 0:
    {
        UnitReleaseInputs();S={};
        if(!Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1)){Fail(TEXT("xbw_socket_real_run_rejected"));return;}
        S.Origin=Player->GetGroundPosition();const auto& Init=Game->GetEquipmentView();
        S.RunGuid=Init.RunGuid;S.RoomId=Init.RoomInstanceId;S.StarterId=Init.Slots[0].InstanceId;S.InitialCritDraw=Init.NextCritDraw;
        DungeonEquipmentInventory::FItem I;I.ContentId="WPN-XBW-001";I.Ammo=1;
        const auto Registered=Game->RegisterEquipmentSource(TEXT("qa.xbw-reload-socket.single-source"),I,S.Origin+FVector2D(32,0));
        S.SourceId=Registered.SourceId;S.InstanceId=Registered.InstanceId;
        for(int32 Side=0;Side<2;++Side)
        {
            auto T=GetWorld()->SpawnActor<ADungeonFighter>();if(!T){Fail(TEXT("xbw_socket_target_spawn_failed"));return;}
            T->SetActorTickEnabled(false);T->bEnemy=true;T->bAIEnabled=false;T->MaxHealth=400.f;
            S.TargetPositions[Side]=S.Origin+FVector2D(Side==0?220.:-220.,0);
            T->ResetFighter(S.TargetPositions[Side]);Game->Enemies.Add(T);S.Targets[Side]=T;
        }
        // Explicit QA initialization only. BeginEquipmentRun itself opens the
        // start gate; this recorder deliberately restores a menu before Enter.
        Game->bWaitingForStart=true;
        if(!Require(TEXT("xbw_socket_fixture_real_run_single_source_two_static_targets"),Registered.Ok()&&Game->GetSimulationTime()==0
            &&Player->IsEquipmentBound()&&Init.ActiveSlot==0&&S.StarterId&&Init.Slots[0].ContentId==TEXT("WPN-SWD-001")
            &&!Init.Slots[1].InstanceId&&!Init.Slots[2].InstanceId&&Game->GetEquipmentSources().Num()==1&&Game->Enemies.Num()==2
            &&Player->ArmorId.IsEmpty()&&S.Targets[0]->Health==400&&S.Targets[1]->Health==400))return;
        Go(1);S.PhaseAt=0;break;
    }
    case 1:
        if(!S.InputIssued&&Elapsed>.20&&UnitPulse(EKeys::Enter,Now)){S.InputIssued=true;S.InputAt=Now;}
        if(S.InputIssued&&!Game->bWaitingForStart&&Now>S.InputAt+.2)
        {
            if(!Require(TEXT("xbw_socket_fresh_enter_opens_qa_initialized_start_gate"),Now>0&&V.RunGuid==S.RunGuid
                &&S.Targets[0]->GetRuntimeEntityId()!=0&&S.Targets[1]->GetRuntimeEntityId()!=0))return;
            Go(2);
        }
        break;
    case 2:if(V.SelectedSourceId==S.SourceId&&Pulse(EKeys::E))Go(3);break;
    case 3:
        if(V.Action.Active){S.ActionObserved=true;S.PickupOldHeld&=ActiveId()==S.StarterId;S.PickupDuration&=Near(V.Action.Deadline-V.Action.Start,.35,1.e-12);}
        else if(S.ActionObserved)
        {
            if(!Require(TEXT("xbw_socket_normal_e_035_commits_acquired_instance"),S.PickupOldHeld&&S.PickupDuration&&ActiveId()==S.InstanceId
                &&WA.EquippedId==S.InstanceId&&Source(S.SourceId)&&Source(S.SourceId)->Consumed&&Instance(S.InstanceId)
                &&Instance(S.InstanceId)->Ammo==1&&V.Slots[1].Ammo==1))return;
            S.Side=0;Go(4);
        }
        break;
    case 4:
        if(Now-S.PhaseAt<.08||Player->Facing!=(S.Side==0?1:-1)){UnitMove(S.Side==0?1:-1,0);break;}
        UnitMove(0,0);Go(5);break;
    case 5:
        if(Now-S.PhaseAt>=1.1&&S.ReadyMask[S.Side]==63)
        {
            if(!Require(S.Side==0?TEXT("xbw_socket_right_ready_all6_native_stack"):TEXT("xbw_socket_left_ready_all6_native_stack"),S.ReadyValid[S.Side]
                &&Instance(S.InstanceId)&&Instance(S.InstanceId)->Ammo==1&&WA.EquippedId==S.InstanceId))return;
            Go(6);
        }
        break;
    case 6:
        if(!WA.Action.Active&&Instance(S.InstanceId)&&Instance(S.InstanceId)->Ammo==1&&Pulse(EKeys::J))
        {S.PendingShotInput=S.InputAt;S.CurrentShot=-1;Go(7);}
        break;
    case 7:
        if(S.CurrentShot>=0&&WA.Action.Active&&WA.Action.Type==ActionKind::Reload)
        {
            const auto& A=S.Shots[S.CurrentShot].Action;S.CurrentReload=WA.Action;
            if(!Near(S.CurrentReload.Start,A.End)||!Near(S.CurrentReload.End-S.CurrentReload.Start,1.1,1.e-12))
            {Fail(TEXT("xbw_socket_auto_reload_skipped_full_recovery_or_changed_duration"));return;}
            Go(8);
        }
        break;
    case 8:
        if(Now<S.CurrentReload.End&&(!Instance(S.InstanceId)||Instance(S.InstanceId)->Ammo!=0))
        {Fail(TEXT("xbw_socket_early_refill_during_actual_reload"));return;}
        if(Now>=S.CurrentReload.End&&!WA.Action.Active&&Instance(S.InstanceId)&&Instance(S.InstanceId)->Ammo==1)Go(9);
        break;
    case 9:
        if(!LoadedDraw()||DrawTime<S.CurrentReload.End||Now-S.PhaseAt<.20)break;
        if(!ShotValid(S.Shots[S.CurrentShot])){Fail(TEXT("xbw_socket_actual_bolt_hit_or_frozen_socket_failed"));return;}
        if(S.PrimaryMask[S.Side]!=63||S.ReloadMask[S.Side]!=15)
        {
            if(S.ShotsPerSide[S.Side]<3){Go(6);break;}
            if(!Require(S.Side==0?TEXT("xbw_socket_right_primary_all6_actor_clock"):TEXT("xbw_socket_left_primary_all6_actor_clock"),S.PrimaryMask[S.Side]==63&&S.PrimaryValid[S.Side]))return;
            Require(S.Side==0?TEXT("xbw_socket_right_reload_all4_actor_clock"):TEXT("xbw_socket_left_reload_all4_actor_clock"),false);return;
        }
        {
            bool ShotsGood=true;for(const auto& Shot:S.Shots)if(Shot.Side==S.Side)ShotsGood&=ShotValid(Shot);
            if(!Require(S.Side==0?TEXT("xbw_socket_right_primary_all6_actor_clock"):TEXT("xbw_socket_left_primary_all6_actor_clock"),S.PrimaryValid[S.Side]&&S.PrimaryMask[S.Side]==63))return;
            if(!Require(S.Side==0?TEXT("xbw_socket_right_world_bolt_hit_frozen_hand_origin"):TEXT("xbw_socket_left_world_bolt_hit_frozen_hand_origin"),ShotsGood&&S.ShotsPerSide[S.Side]>=1&&S.ShotsPerSide[S.Side]<=3))return;
            if(!Require(S.Side==0?TEXT("xbw_socket_right_reload_all4_actor_clock"):TEXT("xbw_socket_left_reload_all4_actor_clock"),S.ReloadValid[S.Side]&&S.ReloadMask[S.Side]==15))return;
            if(!Require(S.Side==0?TEXT("xbw_socket_right_loaded3_after_real_reload_commit"):TEXT("xbw_socket_left_loaded3_after_real_reload_commit"),LoadedDraw()
                &&Instance(S.InstanceId)->Ammo==1&&V.Slots[1].Ammo==1&&Refills()>=S.ShotsPerSide[S.Side]))return;
            if(S.Side==0){S.Side=1;Go(4);}else Go(10);
        }
        break;
    case 10:if(Pulse(EKeys::Q)){S.SwitchOldHeld=true;S.SwitchDuration=true;Go(11);}break;
    case 11:
        if(V.Action.Active){S.ActionObserved=true;S.SwitchOldHeld&=ActiveId()==S.InstanceId;S.SwitchDuration&=Near(V.Action.Deadline-V.Action.Start,.35,1.e-12);}
        else if(S.ActionObserved&&ActiveId()==S.StarterId)Go(12);
        break;
    case 12:if(Pulse(EKeys::Q))Go(13);break;
    case 13:
        if(V.Action.Active){S.ActionObserved=true;S.SwitchOldHeld&=ActiveId()==S.StarterId;S.SwitchDuration&=Near(V.Action.Deadline-V.Action.Start,.35,1.e-12);}
        else if(S.ActionObserved&&LoadedDraw())
        {
            if(!Require(TEXT("xbw_socket_normal_q_roundtrip_same_loaded_instance"),S.SwitchOldHeld&&S.SwitchDuration&&WA.EquippedId==S.InstanceId
                &&V.Slots[0].InstanceId==S.StarterId&&V.Slots[1].InstanceId==S.InstanceId&&Instance(S.InstanceId)->Ammo==1
                &&Instance(S.InstanceId)->CooldownDeadline==0&&V.RunGuid==S.RunGuid&&V.RoomInstanceId==S.RoomId))return;
            Go(14);
        }
        break;
    case 14:
        if(Pulse(EKeys::J)){S.PendingShotInput=S.InputAt;S.CurrentShot=-1;S.CancelShotChecked=false;Go(15);}break;
    case 15:
        if(S.CurrentShot>=0)
        {
            const auto& Shot=S.Shots[S.CurrentShot];
            if(!S.CancelShotChecked&&Shot.EmissionObserved&&DrawValid&&DrawClip==TEXT("xbw_primary")&&DrawState==0&&DrawTime>=Shot.Action.ActiveAt)
            {
                if(!Require(TEXT("xbw_socket_real_shot_changes_loaded_to_empty0"),Instance(S.InstanceId)->Ammo==0&&V.Slots[1].Ammo==0
                    &&Count(EventKind::ProjectileEmitted,Shot.Action.ActionId)==1))return;
                S.CancelShotChecked=true;
            }
            if(WA.Action.Active&&WA.Action.Type==ActionKind::Reload)
            {
                S.CancelledReload=WA.Action;
                if(S.CancelShotChecked&&DrawValid&&DrawClip==TEXT("xbw_reload_four_keyposes")&&DrawAction==WA.Action.ActionId&&DrawFrame==2
                    &&DrawTime>=WA.Action.Start+.6/1.1*(WA.Action.End-WA.Action.Start)&&Now<WA.Action.End-.1&&!bUnitEdgeDown)
                {
                    const FString Insert=TEXT("xbw_socket_insert_frame2_is_visual_without_early_refill");
                    if(!S.Checked.Contains(Insert)&&!Require(Insert,DrawState==2&&Instance(S.InstanceId)->Ammo==0
                        &&V.Slots[1].Ammo==0&&ShotValid(Shot)))return;
                    if(UnitPulse(EKeys::T,Now)){S.RefillsBeforeCancel=Refills();Go(16);}
                }
            }
        }
        break;
    case 16:
        if(!WA.Action.Active&&WA.Action.Terminal==DungeonWeaponActions::EEvent::ReloadCancelled&&S.CancelledAt<0)S.CancelledAt=WA.LastReloadCancelTime;
        if(S.CancelledAt>=0&&Now>S.CancelledReload.End+.15&&DrawValid&&DrawClip==TEXT("xbw_ready_idle")&&DrawTime>=S.CancelledAt)
        {
            if(!Require(TEXT("xbw_socket_fresh_t_cancel_stays_empty_past_old_deadline"),S.CancelledAt>=S.CancelledReload.Start
                &&S.CancelledAt<S.CancelledReload.End&&DrawState==0&&Instance(S.InstanceId)->Ammo==0&&V.Slots[1].Ammo==0
                &&Refills()==S.RefillsBeforeCancel&&!WA.Action.Active))return;
            Go(17);
        }
        break;
    case 17:if(Pulse(EKeys::T)){S.RestartHeldEmpty=true;Go(18);}break;
    case 18:
        if(WA.Action.Active&&WA.Action.Type==ActionKind::Reload)
        {
            if(!S.ActionObserved){S.RestartedReload=WA.Action;S.ActionObserved=true;}
            S.RestartHeldEmpty&=Instance(S.InstanceId)->Ammo==0&&V.Slots[1].Ammo==0;
        }
        else if(S.ActionObserved&&Now>=S.RestartedReload.End&&LoadedDraw()&&DrawTime>=S.RestartedReload.End)
        {
            if(!Require(TEXT("xbw_socket_fresh_t_restart_full_duration_then_one_bolt"),S.RestartHeldEmpty
                &&S.RestartedReload.Start>S.CancelledReload.End&&Near(S.RestartedReload.End-S.RestartedReload.Start,1.1,1.e-12)
                &&S.RestartedReload.ActionId!=S.CancelledReload.ActionId&&Instance(S.InstanceId)->Ammo==1&&V.Slots[1].Ammo==1
                &&Refills()==S.RefillsBeforeCancel+1))return;
            Go(19);
        }
        break;
    case 19:
        if(Now-S.PhaseAt>.40)
        {
            bool Stable=World.RunGuid==S.RunGuid&&World.RoomInstanceId==S.RoomId&&World.Projectiles.Num()==S.Shots.Num();
            double Loss[2]={0,0};
            for(const auto& Shot:S.Shots)
            {
                Stable&=ShotValid(Shot);const auto& Old=Shot.Emission;bool Found=false;
                for(const auto& P:World.Projectiles)if(P.Key.EventId==Old.Key.EventId&&P.Key.ActionId==Old.Key.ActionId)
                {Found=true;Stable&=P.HasPoseSocket&&OriginSame(P.Source.Origin,Old.Source.Origin)&&OriginSame(P.RangeAnchor,Old.RangeAnchor)
                    &&OriginSame(P.PoseSocket.CombatOrigin,Old.PoseSocket.CombatOrigin)&&OriginSame(P.PoseSocket.PresentationOrigin,Old.PoseSocket.PresentationOrigin)
                    &&P.PoseSocket.SampleTime==Old.PoseSocket.SampleTime&&P.PoseSocket.Frame==Old.PoseSocket.Frame
                    &&P.PoseSocket.InstanceId==Old.PoseSocket.InstanceId&&P.PoseSocket.Facing==Old.PoseSocket.Facing
                    &&P.PoseSocket.WeaponStateIndex==Old.PoseSocket.WeaponStateIndex
                    &&Near(P.PoseSocket.EmitX,Old.PoseSocket.EmitX)&&Near(P.PoseSocket.EmitY,Old.PoseSocket.EmitY);}
                Stable&=Found;Loss[Shot.Action.Facing<0?1:0]+=Old.Source.Damage;
            }
            for(int32 I=0;I<2;++I)Stable&=S.Targets[I].IsValid()&&S.Targets[I]->GetGroundPosition()==S.TargetPositions[I]
                &&Near(400.-S.Targets[I]->Health,Loss[I],.002);
            Stable&=Count(EventKind::ProjectileEmitted)==S.Shots.Num()&&Count(EventKind::DirectHitCommitted)==S.Shots.Num()
                &&Count(EventKind::ProjectileStopped)==S.Shots.Num()&&WA.FocusHistory.empty()&&Refills()==S.Shots.Num()
                &&V.NextCritDraw==S.InitialCritDraw+uint64(S.Shots.Num())&&Instance(S.InstanceId)->Ammo==1;
            if(!Require(TEXT("xbw_socket_history_immutable_and_once_only"),Stable))return;
            if(!Require(TEXT("xbw_socket_completed_within_55s"),Elapsed<FXBWReloadSocketProofState::DeadlineSeconds))return;
            UnitReleaseInputs();bGameplayFinished=true;FinishAudioCapture();
        }
        break;
    default:Fail(TEXT("xbw_socket_invalid_phase"));break;
    }
}
