// Draft only: root must explicitly connect the independent flag/state/dispatch.
// Phase0 is the sole gameplay fixture initialization. Later writes are inputs
// and recorder observations; no direct selection, attack, damage or live reset.
void ADungeonContentProbe::TickXBWArmorSocketProof()
{
    if(bGameplayFinished)return;
    auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this));
    auto Player=Game?Game->GetPlayerFighter():nullptr;
    auto Controller=UGameplayStatics::GetPlayerController(this,0);
    auto HUD=Controller?Cast<ADungeonHUD>(Controller->GetHUD()):nullptr;
    auto& S=XBWArmorSocketProof;
    const auto Fail=[this,&S](const FString& Why)
    {
        UnitFailure=Why;UnitReleaseInputs();bGameplayFinished=true;
        const FString End=TEXT("xbw_armor_completed_within_55s");
        if(!S.Checked.Contains(End)){S.Checked.Add(End);Check(End,false);}
        FinishAudioCapture();
    };
    if(!Game||!Player||!Controller||!HUD){Fail(TEXT("xbw_armor_missing_world_controller_hud"));return;}
    if(bFirstUnit||bFirstUnitSkill||bFirstUnitExplore||bEquipmentProof||bArmorLayerProof||bArmorComboProof
        ||bArmorSleevesProof||bRangedProof||bSceneProof||bXBWReadyProof||bXBWHeldIdentityProof
        ||bXBWPrimaryProof||bXBWReloadSocketProof)
    {Fail(TEXT("xbw_armor_conflicting_proof_flags"));return;}
    const double Now=Game->GetSimulationTime();
    if(bUnitEdgeDown&&Now>UnitEdgeAt)
    {Key(UnitEdgeKey,false);bUnitEdgeDown=false;UnitReleasedAt=Now;}
    using ActionKind=DungeonWeaponActions::EAction;
    using WeaponKind=DungeonContentCombat::EWeapon;
    using EventKind=EDungeonWorldWeaponEventKind;
    using MutationKind=DungeonWeaponActions::EWeaponMutation;
    const auto& V=Game->GetEquipmentView();const auto& WA=Player->GetWeaponActionsState();
    const auto& World=Game->GetWeaponWorldState();
    const auto Near=[](double A,double B,double E=1.e-5){return FMath::Abs(A-B)<=E;};
    const auto OriginSame=[&Near](const DungeonWeaponActions::FOrigin& A,const DungeonWeaponActions::FOrigin& B)
    {return Near(A.X,B.X)&&Near(A.Y,B.Y)&&Near(A.Height,B.Height);};
    const auto Instance=[&WA](uint64 Id)->const DungeonWeaponActions::FInstance*
    {for(const auto& I:WA.Instances)if(I.InstanceId==Id)return &I;return nullptr;};
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
        if(S.Checked.Contains(Name)){Fail(TEXT("xbw_armor_duplicate_check:")+Name);return false;}
        S.Checked.Add(Name);Check(Name,Passed);if(!Passed)Fail(Name);return Passed;
    };
    const auto Go=[this,&S,Now](int32 Phase)
    {UnitMove(0,0);S.Phase=Phase;S.PhaseAt=Now;S.InputAt=-1;S.InputIssued=false;S.ActionObserved=false;};
    const auto Pulse=[this,&S,Now](FKey K)
    {
        if(S.InputIssued)return true;
        if(Now-S.PhaseAt<.15||!UnitPulse(K,Now))return false;
        S.InputIssued=true;S.InputAt=Now;return true;
    };
    const auto SelectByTab=[this,&S,Now,&V](uint64 Intended)
    {
        if(V.SelectedSourceId==Intended)return true;
        if(!bUnitEdgeDown&&Now-S.LastTabAt>=.15&&UnitPulse(EKeys::Tab,Now))
        {S.LastTabAt=Now;++S.TabPulses;}
        return false;
    };
    const auto ArmorCheck=[&S](const TCHAR* Suffix)
    {return FXBWArmorSocketProofState::ArmorCheck(S.Armors[S.ArmorIndex].Token,Suffix);};

    if(S.Phase>0)
    {
        if(V.RunGuid!=S.RunGuid||V.RoomInstanceId!=S.RoomId||!Player->IsEquipmentBound())
        {Fail(TEXT("xbw_armor_run_or_room_identity_changed"));return;}
        if(S.Phase>=4&&(WA.EquippedId!=S.InstanceId||V.ActiveSlot!=1||V.Slots[1].InstanceId!=S.InstanceId||V.Slots[0].InstanceId!=S.StarterId))
        {Fail(TEXT("xbw_armor_weapon_identity_changed"));return;}
        if(S.Phase>=6&&S.Phase<=11&&(Player->ArmorId!=S.Armors[S.ArmorIndex].Id||V.Slots[2].InstanceId!=S.Armors[S.ArmorIndex].InstanceId))
        {Fail(TEXT("xbw_armor_held_armor_identity_changed"));return;}
        if(S.PendingShotInput>=0&&S.CurrentShot<0)
        {
            const DungeonWeaponActions::FAction* Accepted=nullptr;
            if(WA.Action.Active&&WA.Action.Type==ActionKind::Primary&&WA.Action.Weapon==WeaponKind::XBW001
                &&WA.Action.Start>=S.PendingShotInput)Accepted=&WA.Action;
            else for(const auto& E:WA.Issued)if(E.Action.Type==ActionKind::Primary&&E.Action.Weapon==WeaponKind::XBW001
                &&E.Action.Start>=S.PendingShotInput)Accepted=&E.Action;
            if(Accepted)
            {
                auto& Armor=S.Armors[S.ArmorIndex];
                if(Accepted->InstanceId!=S.InstanceId||Accepted->StartedAirborne||Accepted->Facing!=(S.Side==0?1.:-1.)
                    ||Player->ArmorId!=Armor.Id||V.Slots[2].InstanceId!=Armor.InstanceId)
                {Fail(TEXT("xbw_armor_wrong_identity_at_actual_primary_acceptance"));return;}
                FXBWArmorSocketProofState::FShot Shot;Shot.Armor=S.ArmorIndex;Shot.Side=S.Side;Shot.Action=*Accepted;
                Shot.TargetId=S.Targets[S.Side].IsValid()?S.Targets[S.Side]->GetRuntimeEntityId():0;
                S.CurrentShot=S.Shots.Add(Shot);++Armor.ShotsPerSide[S.Side];S.PendingShotInput=-1;
                if(S.Shots.Num()>8+FXBWArmorSocketProofState::MaxGlobalRetries)
                {Fail(TEXT("xbw_armor_actual_shot_budget_exceeded"));return;}
            }
        }
        for(auto& Shot:S.Shots)if(!Shot.EmissionObserved)
            for(const auto& P:World.Projectiles)if(P.Key.ActionId==Shot.Action.ActionId)
            {Shot.Emission=P;Shot.EmissionObserved=true;break;}
        if(S.CurrentShot>=0)
        {
            auto& Shot=S.Shots[S.CurrentShot];
            if(WA.Action.Active&&WA.Action.Type==ActionKind::Reload&&WA.Action.InstanceId==S.InstanceId)
            {
                if(!Shot.ReloadObserved)
                {
                    Shot.Reload=WA.Action;Shot.ReloadObserved=true;
                    if(!Near(Shot.Reload.Start,Shot.Action.End,1.e-12)||!Near(Shot.Reload.End-Shot.Reload.Start,1.10,1.e-12))
                    {Fail(TEXT("xbw_armor_auto_reload_skipped_recovery_or_changed_full_duration"));return;}
                }
                if(Now<Shot.Reload.End)Shot.NoEarlyRefill&=Instance(S.InstanceId)&&Instance(S.InstanceId)->Ammo==0&&V.Slots[1].Ammo==0;
                if(!Shot.NoEarlyRefill){Fail(TEXT("xbw_armor_actual_early_refill"));return;}
            }
        }
    }

    const auto Path=[](const FString& Root,const FString& Prefix,const FString& Track,int32 Frame)
    {const FString N=FString::Printf(TEXT("%s_%s_%03d_v001"),*Prefix,*Track,Frame);return Root+N+TEXT(".")+N;};
    const auto WeaponPath=[&Path](int32 Index)
    {return Index<0?FString(TEXT("/Game/Production/FirstBatch/v015/WeaponComponents/T_WPN_XBW_001_neutral_v001.T_WPN_XBW_001_neutral_v001"))
        :Path(TEXT("/Game/Production/FirstBatch/v018/XBWReload/"),TEXT("T_XBWReload"),TEXT("weapon"),Index);};
    const FString DrawClip=HUD->GetRenderedWeaponBodyClip();
    const int32 DrawFrame=HUD->GetRenderedWeaponBodyFrame(),DrawFacing=HUD->GetRenderedWeaponBodyFacing(),DrawState=HUD->GetRenderedWeaponStateIndex();
    const double DrawTime=HUD->GetRenderedWeaponBodySampleTime();
    const uint64 DrawAction=HUD->GetRenderedWeaponBodyActionId(),DrawInstance=HUD->GetRenderedWeaponBodyInstanceId();
    bool DrawValid=false;
    if(S.ArmorIndex<FXBWArmorSocketProofState::ArmorCount&&S.Armors[S.ArmorIndex].Committed&&S.InstanceId
        &&HUD->GetRenderedWeaponBodyUsed()&&DrawInstance==S.InstanceId&&FMath::IsFinite(DrawTime)&&DrawTime<=Now
        &&DrawTime>=S.Armors[S.ArmorIndex].Pickup.Deadline&&(DrawFacing==1||DrawFacing==-1))
    {
        auto& Armor=S.Armors[S.ArmorIndex];
        FString Root,Prefix,ArmorRoot,ArmorPrefix;int32 Expected=-1,Side=DrawFacing<0?1:0;bool StateValid=false;
        FString Token=Armor.Id;Token.ReplaceInline(TEXT("-"),TEXT("_"));
        if(DrawClip==TEXT("xbw_ready_idle")&&DrawFrame>=0&&DrawFrame<6)
        {
            Root=TEXT("/Game/Production/FirstBatch/v016/XBWReadyIdle/");Prefix=TEXT("T_XBWReadyIdle");
            ArmorRoot=TEXT("/Game/Production/FirstBatch/v021/XBWArmorReady/");ArmorPrefix=TEXT("T_XBWArmorReady_")+Token;
            Expected=DrawFrame;StateValid=DrawState==(AmmoAt(DrawTime)==0?0:Refills(DrawTime)>0?3:-1);
        }
        else if(DrawClip==TEXT("xbw_primary"))for(const auto& Shot:S.Shots)
        {
            const auto& A=Shot.Action;if(Shot.Armor!=S.ArmorIndex||A.ActionId!=DrawAction||DrawTime<A.Start||DrawTime>=A.End)continue;
            Root=TEXT("/Game/Production/FirstBatch/v017/XBWPrimary/");Prefix=TEXT("T_XBWPrimary");
            ArmorRoot=TEXT("/Game/Production/FirstBatch/v019/XBWArmorPrimary/");ArmorPrefix=TEXT("T_XBWArmorPrimary_")+Token;
            Side=Shot.Side;const int32 Base=DrawTime<A.ActiveAt?0:DrawTime<A.ActiveEnd?2:4;
            const double Begin=Base==0?A.Start:Base==2?A.ActiveAt:A.ActiveEnd,End=Base==0?A.ActiveAt:Base==2?A.ActiveEnd:A.End;
            Expected=Base+(DrawTime<(Begin+End)*.5?0:1);
            StateValid=DrawFacing==int32(A.Facing)&&DrawState==(AmmoAt(DrawTime)==0?0:Refills(DrawTime)>0?3:-1);break;
        }
        else if(DrawClip==TEXT("xbw_reload_four_keyposes"))for(const auto& Shot:S.Shots)
        {
            const auto& R=Shot.Reload;if(Shot.Armor!=S.ArmorIndex||!Shot.ReloadObserved||R.ActionId!=DrawAction||DrawTime<R.Start||DrawTime>=R.End)continue;
            Root=TEXT("/Game/Production/FirstBatch/v018/XBWReload/");Prefix=TEXT("T_XBWReload");
            ArmorRoot=TEXT("/Game/Production/FirstBatch/v020/XBWArmorReload/");ArmorPrefix=TEXT("T_XBWArmorReload_")+Token;
            const double U=(DrawTime-R.Start)/(R.End-R.Start);Expected=U<.2/1.1?0:U<.6/1.1?1:U<.85/1.1?2:3;
            Side=Shot.Side;StateValid=DrawState==Expected&&DrawFacing==int32(Shot.Action.Facing)&&AmmoAt(DrawTime)==0;break;
        }
        if(Expected>=0)
        {
            const TArray<FString> Stack={Path(Root,Prefix,TEXT("body_far"),Expected),Path(ArmorRoot,ArmorPrefix,TEXT("armor_far"),Expected),
                WeaponPath(DrawState),Path(Root,Prefix,TEXT("body_support"),Expected),Path(ArmorRoot,ArmorPrefix,TEXT("armor_near"),Expected),
                Path(Root,Prefix,TEXT("body_near"),Expected)};
            DrawValid=Expected==DrawFrame&&StateValid&&HUD->GetRenderedPlayerDrawStack()==Stack
                &&HUD->GetRenderedArmorLayersUsed()&&HUD->GetRenderedPlayerSpriteSize()==160.f&&HUD->GetQueuedPlayerMeleeTrailCount()==0;
            if(DrawClip==TEXT("xbw_ready_idle")){Armor.ReadyValid[Side]&=DrawValid;if(DrawValid)Armor.ReadyMask[Side]|=1<<Expected;}
            else if(DrawClip==TEXT("xbw_primary")){Armor.PrimaryValid[Side]&=DrawValid;if(DrawValid)Armor.PrimaryMask[Side]|=1<<Expected;}
            else{Armor.ReloadValid[Side]&=DrawValid;if(DrawValid)Armor.ReloadMask[Side]|=1<<Expected;}
        }
    }
    const auto LoadedDraw=[&](){return DrawValid&&DrawClip==TEXT("xbw_ready_idle")&&DrawState==3&&DrawInstance==S.InstanceId;};
    const auto ShotValid=[&](const FXBWArmorSocketProofState::FShot& Shot)
    {
        if(!Shot.EmissionObserved||!Shot.ReloadObserved||!Shot.NoEarlyRefill||!Shot.LoadedAfterCommit)return false;
        const auto& P=Shot.Emission;const auto& E=P.Source;const auto& Pose=P.PoseSocket;
        const auto* Emit=FindEvent(EventKind::ProjectileEmitted,Shot.Action.ActionId);
        const auto* Hit=FindEvent(EventKind::DirectHitCommitted,Shot.Action.ActionId,Shot.TargetId);
        const double Forward=(Pose.EmitX-Pose.RootX)*Pose.BodySize/512./.65;
        const double Height=(Pose.RootY-Pose.EmitY)*Pose.BodySize/512./.70;
        const auto Target=S.TargetPositions[Shot.Side];
        const double CenterForward=(Target.X-P.RangeAnchor.X)*Shot.Action.Facing;
        const double Contact=E.AtTime+(Target.X-double(Shot.Action.Facing)*18.-E.Origin.X)*Shot.Action.Facing/E.ProjectileSpeed;
        int32 Spends=0,Commits=0,Receipts=0;bool ReceiptValid=true;
        for(const auto& R:WA.WeaponRuntimeHistory)
        {
            if(R.Kind==MutationKind::Emission&&R.Action.ActionId==Shot.Action.ActionId&&R.Action.InstanceId==S.InstanceId
                &&R.AtTime==E.AtTime&&R.BeforeAmmo==1&&R.AfterAmmo==0)++Spends;
            if(R.Kind==MutationKind::ReloadCompleted&&R.Action.ActionId==Shot.Reload.ActionId&&R.Action.InstanceId==S.InstanceId
                &&R.AtTime==Shot.Reload.End&&R.BeforeAmmo==0&&R.AfterAmmo==1)++Commits;
        }
        for(const auto& H:World.HitReceipts)if(H.Key.ActionId==Shot.Action.ActionId)
        {
            ++Receipts;ReceiptValid&=H.TargetId==Shot.TargetId&&H.HasPoseSocket&&!H.Magic&&!H.LaunchObstructed
                &&Near(H.Damage,E.Damage,.0002)&&Near(H.Stagger,E.Stagger,.0002)&&Near(H.AtTime,Contact,1.e-7)
                &&OriginSame(H.PoseSocket.CombatOrigin,Pose.CombatOrigin)&&OriginSame(H.RangeAnchor,P.RangeAnchor);
        }
        return P.HasPoseSocket&&Pose.Supported&&!Pose.CustomOverride&&!Pose.GroundPoseFallback&&P.UsesActorRangeAnchor
            &&E.Action.Type==ActionKind::Primary&&E.Action.Weapon==WeaponKind::XBW001&&E.ActionId==Shot.Action.ActionId&&E.InstanceId==S.InstanceId
            &&Pose.Clip==DungeonWeaponPoseSocket::EClip::Primary&&Pose.Frame==2&&Pose.SampleTime==E.AtTime
            &&Pose.InstanceId==S.InstanceId&&Pose.ActionId==Shot.Action.ActionId&&Pose.Facing==Shot.Action.Facing
            &&E.AtTime==Shot.Action.ActiveAt&&E.Origin.Height==0&&P.RangeAnchor.Height==0
            &&OriginSame(E.Origin,Pose.CombatOrigin)&&OriginSame(P.RangeAnchor,Pose.ActorOrigin)
            &&Forward>0&&Near((E.Origin.X-P.RangeAnchor.X)*Shot.Action.Facing,Forward)&&Near(P.LaunchForwardDistance,Forward)
            &&Near(E.Origin.Y,P.RangeAnchor.Y)&&Height>65&&Near(Pose.PresentationOrigin.Height,Height)
            &&Near(Pose.PresentationOrigin.X,E.Origin.X)&&Near(Pose.PresentationOrigin.Y,E.Origin.Y)
            &&CenterForward>=E.MinRange&&CenterForward<=E.Range&&FMath::Abs(Target.Y-P.RangeAnchor.Y)<=E.Depth
            &&Emit&&Emit->HasPoseSocket&&Emit->PoseSocket.SampleTime==E.AtTime&&OriginSame(Emit->RangeAnchor,P.RangeAnchor)
            &&Hit&&Hit->HasPoseSocket&&!Hit->Magic&&Hit->ActualHPLoss>0&&Near(Hit->ActualHPLoss,E.Damage,.0002)
            &&Near(Hit->Stagger,E.Stagger,.0002)&&Near(Hit->AtTime,Contact,1.e-7)
            &&OriginSame(Hit->PoseSocket.PresentationOrigin,Pose.PresentationOrigin)&&Hit->PoseSocket.SampleTime==E.AtTime
            &&Count(EventKind::ProjectileEmitted,Shot.Action.ActionId)==1&&Count(EventKind::DirectHitCommitted,Shot.Action.ActionId)==1
            &&Count(EventKind::DirectHitCommitted,Shot.Action.ActionId,Shot.TargetId)==1&&Count(EventKind::ProjectileStopped,Shot.Action.ActionId)==1
            &&Spends==1&&Commits==1&&Receipts==1&&ReceiptValid&&!P.LaunchObstructed;
    };

    if(S.Phase>0)
    {
        auto R=MakeShared<FJsonObject>();const auto Pose=Player->GetWeaponPoseSocket();const auto XY=Player->GetGroundPosition();
        R->SetStringField(TEXT("record_type"),TEXT("xbw_four_armor_normal_input_post_batch_observation"));
        R->SetNumberField(TEXT("fixture_phase"),S.Phase);R->SetNumberField(TEXT("armor_variant"),S.ArmorIndex);R->SetNumberField(TEXT("side"),S.Side);
        R->SetNumberField(TEXT("sim_time_s"),Now);R->SetNumberField(TEXT("wall_offset_s"),Elapsed);
        R->SetStringField(TEXT("run_guid"),V.RunGuid.ToString());R->SetNumberField(TEXT("room_instance_id"),double(V.RoomInstanceId));
        R->SetNumberField(TEXT("player_x"),XY.X);R->SetNumberField(TEXT("player_y"),XY.Y);R->SetNumberField(TEXT("player_facing"),Player->Facing);
        R->SetNumberField(TEXT("player_hp"),Player->Health);R->SetNumberField(TEXT("actual_focus"),WA.Budget.Focus);
        R->SetStringField(TEXT("actual_armor_id"),Player->ArmorId);R->SetNumberField(TEXT("actual_armor_instance_id"),double(V.Slots[2].InstanceId));
        R->SetNumberField(TEXT("weapon_instance_id"),double(WA.EquippedId));R->SetNumberField(TEXT("slot_weapon_instance_id"),double(V.Slots[1].InstanceId));
        R->SetNumberField(TEXT("selected_source_id"),double(V.SelectedSourceId));R->SetBoolField(TEXT("needs_slot_selection"),V.NeedsSlotSelection);
        R->SetNumberField(TEXT("selection_slot"),V.SelectionSlot);R->SetBoolField(TEXT("equipment_action_active"),V.Action.Active);
        R->SetNumberField(TEXT("equipment_action_start"),V.Action.Start);R->SetNumberField(TEXT("equipment_action_deadline"),V.Action.Deadline);
        R->SetNumberField(TEXT("actual_ammo"),Instance(S.InstanceId)?Instance(S.InstanceId)->Ammo:-1.);R->SetNumberField(TEXT("slot_ammo"),V.Slots[1].Ammo);
        R->SetNumberField(TEXT("actual_reserved_ammo"),Instance(S.InstanceId)?Instance(S.InstanceId)->ReservedAmmo:-1.);
        R->SetNumberField(TEXT("actual_reload_commits"),Refills());R->SetNumberField(TEXT("crit_next_draw"),double(V.NextCritDraw));
        R->SetNumberField(TEXT("action_id"),double(WA.Action.ActionId));R->SetNumberField(TEXT("action_type"),int32(WA.Action.Type));
        R->SetBoolField(TEXT("action_active"),WA.Action.Active);R->SetBoolField(TEXT("waiting_for_start"),Game->bWaitingForStart);
        R->SetNumberField(TEXT("action_start"),WA.Action.Start);R->SetNumberField(TEXT("action_active_at"),WA.Action.ActiveAt);
        R->SetNumberField(TEXT("action_active_end"),WA.Action.ActiveEnd);R->SetNumberField(TEXT("action_end"),WA.Action.End);
        R->SetStringField(TEXT("hud_clip"),DrawClip);R->SetNumberField(TEXT("hud_frame"),DrawFrame);R->SetNumberField(TEXT("hud_facing"),DrawFacing);
        R->SetNumberField(TEXT("hud_sample_time"),DrawTime);R->SetNumberField(TEXT("hud_action_id"),double(DrawAction));
        R->SetNumberField(TEXT("hud_instance_id"),double(DrawInstance));R->SetNumberField(TEXT("hud_weapon_state_index"),DrawState);
        R->SetBoolField(TEXT("hud_draw_clock_stack_valid"),DrawValid);R->SetBoolField(TEXT("hud_weapon_state_is_resource_authority"),false);
        R->SetNumberField(TEXT("hud_emit_screen_x"),HUD->GetRenderedWeaponBodyEmitScreen().X);
        R->SetNumberField(TEXT("hud_emit_screen_y"),HUD->GetRenderedWeaponBodyEmitScreen().Y);
        R->SetNumberField(TEXT("actor_socket_time"),Pose.SampleTime);R->SetNumberField(TEXT("actor_socket_combat_x"),Pose.CombatOrigin.X);
        R->SetNumberField(TEXT("actor_socket_combat_y"),Pose.CombatOrigin.Y);R->SetNumberField(TEXT("actor_socket_combat_height"),Pose.CombatOrigin.Height);
        R->SetNumberField(TEXT("actor_socket_presentation_height"),Pose.PresentationOrigin.Height);
        R->SetNumberField(TEXT("actual_shots"),S.Shots.Num());R->SetNumberField(TEXT("global_retry_shots"),S.GlobalRetries);R->SetNumberField(TEXT("tab_pulses"),S.TabPulses);
        TArray<TSharedPtr<FJsonValue>> Stack,Armors,Sources,Targets,Events,History;
        for(const auto& P:HUD->GetRenderedPlayerDrawStack())Stack.Add(MakeShared<FJsonValueString>(P));
        for(const auto& A:S.Armors)
        {
            auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("armor_id"),A.Id);O->SetNumberField(TEXT("source_id"),double(A.SourceId));
            O->SetNumberField(TEXT("instance_id"),double(A.InstanceId));O->SetBoolField(TEXT("committed"),A.Committed);
            O->SetBoolField(TEXT("old_held_during_pickup"),A.PickupOldHeld);O->SetBoolField(TEXT("fresh_enter_confirmed"),A.Confirmed);
            O->SetNumberField(TEXT("pickup_start"),A.Pickup.Start);O->SetNumberField(TEXT("pickup_deadline"),A.Pickup.Deadline);
            for(int32 Side=0;Side<2;++Side)
            {
                const FString Prefix=Side==0?TEXT("right_"):TEXT("left_");
                O->SetNumberField(Prefix+TEXT("ready_mask"),A.ReadyMask[Side]);O->SetNumberField(Prefix+TEXT("primary_mask"),A.PrimaryMask[Side]);
                O->SetNumberField(Prefix+TEXT("reload_mask"),A.ReloadMask[Side]);O->SetNumberField(Prefix+TEXT("actual_shots"),A.ShotsPerSide[Side]);
            }
            Armors.Add(MakeShared<FJsonValueObject>(O));
        }
        for(const auto& SourceView:Game->GetEquipmentSources())
        {
            auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("source_id"),double(SourceView.SourceId));O->SetNumberField(TEXT("instance_id"),double(SourceView.InstanceId));
            O->SetStringField(TEXT("logical_key"),SourceView.LogicalKey);O->SetBoolField(TEXT("consumed"),SourceView.Consumed);
            O->SetNumberField(TEXT("x"),SourceView.Position.X);O->SetNumberField(TEXT("y"),SourceView.Position.Y);Sources.Add(MakeShared<FJsonValueObject>(O));
        }
        for(const auto& Target:S.Targets)if(Target.IsValid())
        {
            auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("entity_id"),double(Target->GetRuntimeEntityId()));
            O->SetNumberField(TEXT("hp"),Target->Health);O->SetNumberField(TEXT("x"),Target->GetGroundPosition().X);O->SetNumberField(TEXT("y"),Target->GetGroundPosition().Y);
            O->SetBoolField(TEXT("dead"),Target->bDead);Targets.Add(MakeShared<FJsonValueObject>(O));
        }
        for(const auto& E:World.Events)if(E.Sequence>S.WorldCursor)
        {
            auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("sequence"),double(E.Sequence));O->SetNumberField(TEXT("kind"),int32(E.Kind));
            O->SetNumberField(TEXT("action_id"),double(E.Key.ActionId));O->SetNumberField(TEXT("instance_id"),double(E.PoseSocket.InstanceId));
            O->SetNumberField(TEXT("target_id"),double(E.TargetId));O->SetNumberField(TEXT("at_time"),E.AtTime);O->SetNumberField(TEXT("hp_loss"),E.ActualHPLoss);
            O->SetBoolField(TEXT("has_pose_socket"),E.HasPoseSocket);O->SetNumberField(TEXT("socket_sample_time"),E.PoseSocket.SampleTime);
            O->SetNumberField(TEXT("combat_x"),E.PoseSocket.CombatOrigin.X);O->SetNumberField(TEXT("combat_height"),E.PoseSocket.CombatOrigin.Height);
            O->SetNumberField(TEXT("presentation_height"),E.PoseSocket.PresentationOrigin.Height);O->SetNumberField(TEXT("range_anchor_x"),E.RangeAnchor.X);
            Events.Add(MakeShared<FJsonValueObject>(O));S.WorldCursor=E.Sequence;
        }
        for(const auto& H:WA.WeaponRuntimeHistory)
        {
            auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("event_id"),double(H.EventId));O->SetNumberField(TEXT("kind"),int32(H.Kind));
            O->SetNumberField(TEXT("action_id"),double(H.Action.ActionId));O->SetNumberField(TEXT("instance_id"),double(H.Action.InstanceId));
            O->SetNumberField(TEXT("at_time"),H.AtTime);O->SetNumberField(TEXT("before_ammo"),H.BeforeAmmo);O->SetNumberField(TEXT("after_ammo"),H.AfterAmmo);
            History.Add(MakeShared<FJsonValueObject>(O));
        }
        R->SetArrayField(TEXT("actual_draw_stack"),Stack);R->SetArrayField(TEXT("armor_variants"),Armors);R->SetArrayField(TEXT("actual_sources"),Sources);
        R->SetArrayField(TEXT("qa_targets"),Targets);R->SetArrayField(TEXT("new_world_journal"),Events);R->SetArrayField(TEXT("actual_weapon_runtime_history"),History);
        for(const auto& K:{EKeys::A,EKeys::D,EKeys::E,EKeys::Tab,EKeys::Enter,EKeys::J})R->SetBoolField(TEXT("input_held_")+K.GetFName().ToString(),Controller->IsInputKeyDown(K));
        Trace.Add(MakeShared<FJsonValueObject>(R));
    }
    if(Elapsed>=FXBWArmorSocketProofState::DeadlineSeconds||Player->bDead||Game->bGameOver)
    {Fail(TEXT("xbw_armor_total_deadline_or_death"));return;}
    if(S.Phase>1&&Now-S.PhaseAt>12.){Fail(FString::Printf(TEXT("xbw_armor_phase_%02d_timeout"),S.Phase));return;}

    switch(S.Phase)
    {
    case 0:
    {
        UnitReleaseInputs();S={};
        if(!Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1)){Fail(TEXT("xbw_armor_real_run_rejected"));return;}
        S.Origin=Player->GetGroundPosition();const auto& Init=Game->GetEquipmentView();
        S.RunGuid=Init.RunGuid;S.RoomId=Init.RoomInstanceId;S.StarterId=Init.Slots[0].InstanceId;S.InitialCritDraw=Init.NextCritDraw;
        DungeonEquipmentInventory::FItem XBW;XBW.ContentId="WPN-XBW-001";XBW.Ammo=1;
        const auto WeaponSource=Game->RegisterEquipmentSource(TEXT("qa.xbw-four-armor.single-xbw"),XBW,S.Origin+FVector2D(32,0));
        S.SourceId=WeaponSource.SourceId;S.InstanceId=WeaponSource.InstanceId;bool Registered=WeaponSource.Ok();
        const TCHAR* Ids[]={TEXT("ARM-LGT-001"),TEXT("ARM-MED-001"),TEXT("ARM-HVY-001"),TEXT("ARM-ROB-001")};
        const TCHAR* Tokens[]={TEXT("lgt"),TEXT("med"),TEXT("hvy"),TEXT("rob")};
        for(int32 I=0;I<FXBWArmorSocketProofState::ArmorCount;++I)
        {
            auto& A=S.Armors[I];A.Id=Ids[I];A.Token=Tokens[I];DungeonEquipmentInventory::FItem Item;Item.ContentId=TCHAR_TO_UTF8(Ids[I]);
            const auto RegisteredArmor=Game->RegisterEquipmentSource(TEXT("qa.xbw-four-armor.")+A.Token,Item,S.Origin+FVector2D(32,0));
            A.SourceId=RegisteredArmor.SourceId;A.InstanceId=RegisteredArmor.InstanceId;Registered&=RegisteredArmor.Ok();
        }
        for(int32 Side=0;Side<2;++Side)
        {
            auto Target=GetWorld()->SpawnActor<ADungeonFighter>();if(!Target){Fail(TEXT("xbw_armor_target_spawn_failed"));return;}
            Target->SetActorTickEnabled(false);Target->bEnemy=true;Target->bAIEnabled=false;Target->MaxHealth=2000.f;
            S.TargetPositions[Side]=S.Origin+FVector2D(Side==0?220.:-220.,0);Target->ResetFighter(S.TargetPositions[Side]);
            Game->Enemies.Add(Target);S.Targets[Side]=Target;
        }
        Game->bWaitingForStart=true; // Sole explicit fixture gate, before any input.
        TSet<uint64> SourceIds,InstanceIds;bool ExactSources=true;
        for(const auto& RegisteredSource:Game->GetEquipmentSources())
        {
            SourceIds.Add(RegisteredSource.SourceId);InstanceIds.Add(RegisteredSource.InstanceId);
            ExactSources&=RegisteredSource.SourceId!=0&&RegisteredSource.InstanceId!=0&&RegisteredSource.RoomInstanceId==S.RoomId
                &&RegisteredSource.Settled&&!RegisteredSource.Consumed&&RegisteredSource.Position==S.Origin+FVector2D(32,0);
        }
        if(!Require(TEXT("xbw_armor_fixture_real_run_five_qa_sources_two_static_targets"),Registered&&Game->GetSimulationTime()==0
            &&Player->IsEquipmentBound()&&Init.ActiveSlot==0&&Init.Slots[0].ContentId==TEXT("WPN-SWD-001")&&S.StarterId
            &&!Init.Slots[1].InstanceId&&!Init.Slots[2].InstanceId&&Player->ArmorId.IsEmpty()
            &&Game->GetEquipmentSources().Num()==5&&SourceIds.Num()==5&&InstanceIds.Num()==5&&ExactSources
            &&Game->Enemies.Num()==2&&S.Targets[0]->Health==2000&&S.Targets[1]->Health==2000))return;
        Go(1);S.PhaseAt=0;break;
    }
    case 1:
        if(!S.InputIssued&&Elapsed>.20&&UnitPulse(EKeys::Enter,Now)){S.InputIssued=true;S.InputAt=Now;}
        if(S.InputIssued&&!Game->bWaitingForStart&&Now>S.InputAt+.2)
        {
            if(!Require(TEXT("xbw_armor_fresh_enter_opens_initialized_start_gate"),Now>0&&S.Targets[0]->GetRuntimeEntityId()!=0&&S.Targets[1]->GetRuntimeEntityId()!=0))return;
            Go(2);
        }
        break;
    case 2:if(SelectByTab(S.SourceId)&&Pulse(EKeys::E))Go(3);break;
    case 3:
        if(V.Action.Active)
        {
            S.ActionObserved=true;S.WeaponPickup=V.Action;
            S.WeaponOldHeld&=WA.EquippedId==S.StarterId&&V.Slots[V.ActiveSlot].InstanceId==S.StarterId;
            S.WeaponDuration&=V.Action.Kind==EDungeonEquipmentActionKind::PickupWeapon&&V.Action.SourceId==S.SourceId
                &&V.Action.InstanceId==S.InstanceId&&V.Action.Slot==1&&Near(V.Action.Deadline-V.Action.Start,.35,1.e-12);
        }
        else if(S.ActionObserved)
        {
            if(!Require(TEXT("xbw_armor_normal_e_035_commits_single_xbw_instance"),S.WeaponOldHeld&&S.WeaponDuration&&Now>=S.WeaponPickup.Deadline
                &&WA.EquippedId==S.InstanceId&&V.ActiveSlot==1&&V.Slots[1].InstanceId==S.InstanceId&&V.Slots[1].Ammo==1
                &&Instance(S.InstanceId)&&Instance(S.InstanceId)->Ammo==1&&Source(S.SourceId)&&Source(S.SourceId)->Consumed))return;
            Go(4);
        }
        break;
    case 4:
    {
        auto& A=S.Armors[S.ArmorIndex];A.OldId=Player->ArmorId;A.OldInstanceId=V.Slots[2].InstanceId;
        if(SelectByTab(A.SourceId)&&Pulse(EKeys::E))Go(5);break;
    }
    case 5:
    {
        auto& A=S.Armors[S.ArmorIndex];
        if(V.NeedsSlotSelection)
        {
            if(S.ArmorIndex==0||V.SelectionSlot!=2||V.SelectedSourceId!=A.SourceId||V.Action.Active
                ||Player->ArmorId!=A.OldId||V.Slots[2].InstanceId!=A.OldInstanceId)
            {Fail(TEXT("xbw_armor_opening_e_invalid_replacement_layer"));return;}
            if(!A.Confirmed&&Now-S.PhaseAt>=.15&&UnitPulse(EKeys::Enter,Now))A.Confirmed=true;
        }
        else if(V.Action.Active)
        {
            A.PickupObserved=true;A.Pickup=V.Action;A.PickupOldHeld&=Player->ArmorId==A.OldId&&V.Slots[2].InstanceId==A.OldInstanceId;
            A.PickupDuration&=V.Action.Kind==EDungeonEquipmentActionKind::PickupArmor&&V.Action.SourceId==A.SourceId
                &&V.Action.InstanceId==A.InstanceId&&V.Action.Slot==2&&Near(V.Action.Deadline-V.Action.Start,.50,1.e-12);
        }
        else if(A.PickupObserved)
        {
            if(!Require(ArmorCheck(TEXT("normal_e_050_commit")),A.PickupOldHeld&&A.PickupDuration&&(S.ArmorIndex==0?!A.Confirmed:A.Confirmed)
                &&Now>=A.Pickup.Deadline&&Player->ArmorId==A.Id&&V.Slots[2].InstanceId==A.InstanceId&&Source(A.SourceId)&&Source(A.SourceId)->Consumed
                &&WA.EquippedId==S.InstanceId&&V.Slots[1].InstanceId==S.InstanceId&&Instance(S.InstanceId)&&Instance(S.InstanceId)->Ammo==1))return;
            A.Committed=true;S.Side=0;Go(6);
        }
        break;
    }
    case 6:
        if(Now-S.PhaseAt<.08||Player->Facing!=(S.Side==0?1:-1)){UnitMove(S.Side==0?1:-1,0);break;}
        Go(7);break;
    case 7:
    {
        auto& A=S.Armors[S.ArmorIndex];
        if(!A.ReadyValid[S.Side]){Require(ArmorCheck(TEXT("ready_both_facings_all6_six_stack")),false);return;}
        if(Now-S.PhaseAt>=1.1&&A.ReadyMask[S.Side]==63&&A.ReadyValid[S.Side])Go(8);
        break;
    }
    case 8:
        if(!WA.Action.Active&&Instance(S.InstanceId)&&Instance(S.InstanceId)->Ammo==1&&Pulse(EKeys::J))
        {S.PendingShotInput=S.InputAt;S.CurrentShot=-1;Go(9);}break;
    case 9:
        if(S.CurrentShot>=0&&S.Shots[S.CurrentShot].ReloadObserved)Go(10);break;
    case 10:
    {
        auto& A=S.Armors[S.ArmorIndex];auto& Shot=S.Shots[S.CurrentShot];
        if(Now<Shot.Reload.End+.2||WA.Action.Active||!LoadedDraw()||DrawTime<Shot.Reload.End)break;
        if(!Instance(S.InstanceId)||Instance(S.InstanceId)->Ammo!=1||V.Slots[1].Ammo!=1)
        {Fail(TEXT("xbw_armor_completed_reload_did_not_hold_actual_one_ammo"));return;}
        Shot.LoadedAfterCommit=true;
        if(!ShotValid(Shot)){Fail(TEXT("xbw_armor_actual_bolt_or_reload_receipt_failed"));return;}
        if(!A.PrimaryValid[S.Side]||!A.ReloadValid[S.Side])
        {Require(ArmorCheck(!A.PrimaryValid[S.Side]?TEXT("primary_both_facings_all6_actor_clock"):TEXT("reload_both_facings_all4_full_clock")),false);return;}
        if(A.PrimaryMask[S.Side]!=63||A.ReloadMask[S.Side]!=15)
        {
            if(S.GlobalRetries<FXBWArmorSocketProofState::MaxGlobalRetries){++S.GlobalRetries;Go(8);break;}
            Require(ArmorCheck(A.PrimaryMask[S.Side]!=63?TEXT("primary_both_facings_all6_actor_clock"):TEXT("reload_both_facings_all4_full_clock")),false);return;
        }
        A.LoadedAfterCommit[S.Side]=true;
        if(S.Side==0){S.Side=1;Go(6);}else Go(11);break;
    }
    case 11:
    {
        auto& A=S.Armors[S.ArmorIndex];bool Bolts=true,Reloads=true;
        for(const auto& Shot:S.Shots)if(Shot.Armor==S.ArmorIndex)
        {Bolts&=ShotValid(Shot);Reloads&=Shot.ReloadObserved&&Shot.NoEarlyRefill&&Shot.LoadedAfterCommit;}
        if(!Require(ArmorCheck(TEXT("ready_both_facings_all6_six_stack")),A.ReadyMask[0]==63&&A.ReadyMask[1]==63&&A.ReadyValid[0]&&A.ReadyValid[1]))return;
        if(!Require(ArmorCheck(TEXT("primary_both_facings_all6_actor_clock")),A.PrimaryMask[0]==63&&A.PrimaryMask[1]==63&&A.PrimaryValid[0]&&A.PrimaryValid[1]))return;
        if(!Require(ArmorCheck(TEXT("bolts_both_facings_frozen_socket_once")),Bolts&&A.ShotsPerSide[0]>=1&&A.ShotsPerSide[1]>=1))return;
        if(!Require(ArmorCheck(TEXT("reload_both_facings_all4_full_clock")),Reloads&&A.ReloadMask[0]==15&&A.ReloadMask[1]==15&&A.ReloadValid[0]&&A.ReloadValid[1]))return;
        if(!Require(ArmorCheck(TEXT("loaded3_only_after_real_commits")),A.LoadedAfterCommit[0]&&A.LoadedAfterCommit[1]&&LoadedDraw()
            &&Instance(S.InstanceId)&&Instance(S.InstanceId)->Ammo==1&&V.Slots[1].Ammo==1))return;
        if(++S.ArmorIndex<FXBWArmorSocketProofState::ArmorCount)Go(4);else Go(12);break;
    }
    case 12:
        if(Now-S.PhaseAt>.4)
        {
            bool Stable=WA.EquippedId==S.InstanceId&&V.Slots[1].InstanceId==S.InstanceId&&V.Slots[0].InstanceId==S.StarterId
                &&World.RunGuid==S.RunGuid&&World.RoomInstanceId==S.RoomId&&World.Projectiles.Num()==S.Shots.Num()
                &&S.Shots.Num()==8+S.GlobalRetries&&S.GlobalRetries<=FXBWArmorSocketProofState::MaxGlobalRetries;
            double Loss[2]={0,0};
            for(const auto& Shot:S.Shots)
            {
                Stable&=ShotValid(Shot);const auto& Old=Shot.Emission;bool Found=false;
                for(const auto& P:World.Projectiles)if(P.Key.EventId==Old.Key.EventId&&P.Key.ActionId==Old.Key.ActionId)
                {
                    Found=true;Stable&=P.HasPoseSocket&&P.UsesActorRangeAnchor&&OriginSame(P.Source.Origin,Old.Source.Origin)
                        &&P.Key.OwnerId==Old.Key.OwnerId&&P.Key.SubhitId==Old.Key.SubhitId&&P.Key.RoomInstanceId==Old.Key.RoomInstanceId
                        &&P.Source.EventId==Old.Source.EventId&&P.Source.ActionId==Old.Source.ActionId&&P.Source.InstanceId==Old.Source.InstanceId
                        &&P.Source.AtTime==Old.Source.AtTime&&P.Source.Damage==Old.Source.Damage&&P.Source.Stagger==Old.Source.Stagger
                        &&P.Source.Range==Old.Source.Range&&P.Source.ProjectileSpeed==Old.Source.ProjectileSpeed
                        &&OriginSame(P.RangeAnchor,Old.RangeAnchor)&&OriginSame(P.PoseSocket.CombatOrigin,Old.PoseSocket.CombatOrigin)
                        &&OriginSame(P.PoseSocket.PresentationOrigin,Old.PoseSocket.PresentationOrigin)&&P.PoseSocket.SampleTime==Old.PoseSocket.SampleTime
                        &&P.PoseSocket.Frame==Old.PoseSocket.Frame&&P.PoseSocket.Facing==Old.PoseSocket.Facing&&P.PoseSocket.InstanceId==S.InstanceId
                        &&P.PoseSocket.WeaponStateIndex==Old.PoseSocket.WeaponStateIndex&&Near(P.PoseSocket.EmitX,Old.PoseSocket.EmitX)&&Near(P.PoseSocket.EmitY,Old.PoseSocket.EmitY);
                }
                Stable&=Found;Loss[Shot.Side]+=Old.Source.Damage;
            }
            for(int32 Side=0;Side<2;++Side)Stable&=S.Targets[Side].IsValid()&&!S.Targets[Side]->bDead
                &&S.Targets[Side]->GetGroundPosition()==S.TargetPositions[Side]&&Near(2000.-S.Targets[Side]->Health,Loss[Side],.002);
            Stable&=Count(EventKind::ProjectileEmitted)==S.Shots.Num()&&Count(EventKind::DirectHitCommitted)==S.Shots.Num()
                &&Count(EventKind::ProjectileStopped)==S.Shots.Num()&&Refills()==S.Shots.Num()&&WA.FocusHistory.empty()
                &&V.NextCritDraw==S.InitialCritDraw+uint64(S.Shots.Num())&&Instance(S.InstanceId)&&Instance(S.InstanceId)->Ammo==1
                &&Player->ArmorId==S.Armors[3].Id&&V.Slots[2].InstanceId==S.Armors[3].InstanceId;
            if(!Require(TEXT("xbw_armor_history_immutable_once_same_weapon_instance"),Stable))return;
            if(!Require(TEXT("xbw_armor_completed_within_55s"),Elapsed<FXBWArmorSocketProofState::DeadlineSeconds))return;
            UnitReleaseInputs();bGameplayFinished=true;FinishAudioCapture();
        }
        break;
    default:Fail(TEXT("xbw_armor_invalid_phase"));break;
    }
}
