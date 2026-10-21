// Opt-in QA: one genuine scene initialization, then only normal controller keys.
// The sole actor mutation disables autonomous attack starts at time zero;
// the real stone-knight kernel still pursues the player.
void ADungeonContentProbe::TickSceneProof()
{
    if(bGameplayFinished)return;
    auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this));
    auto Player=Game?Game->GetPlayerFighter():nullptr;
    auto Controller=UGameplayStatics::GetPlayerController(this,0);
    auto HUD=Controller?Cast<ADungeonHUD>(Controller->GetHUD()):nullptr;
    auto& S=SceneProof;
    const auto Fail=[this](const FString& Why)
    {
        UnitFailure=Why;UnitReleaseInputs();bGameplayFinished=true;
        const FString Name=TEXT("scene_completed_within_55s");
        if(!Results.ContainsByPredicate([&Name](const TSharedPtr<FJsonValue>& R)
            {return R->AsObject()->GetStringField(TEXT("name"))==Name;}))Check(Name,false);
        FinishAudioCapture();
    };
    if(!Game||!Player||!HUD){Fail(TEXT("scene_missing_game_player_or_hud"));return;}
    if(bFirstUnit||bEquipmentProof||bArmorLayerProof||bRangedProof)
    {Fail(TEXT("scene_conflicting_proof_flags"));return;}
    const double Now=Game->GetSimulationTime();
    if(bUnitEdgeDown&&Now>UnitEdgeAt)
    {Key(UnitEdgeKey,false);bUnitEdgeDown=false;UnitReleasedAt=Now;}
    const auto Require=[this,&Fail](const TCHAR* Name,bool Passed)
    {Check(Name,Passed);if(!Passed)Fail(Name);return Passed;};
    const auto Go=[this,&S,Now](int32 Phase)
    {UnitMove(0,0);S.Phase=Phase;S.PhaseAt=Now;S.ArrivalAt=-1;S.InputAt=-1;S.InputIssued=false;};
    const auto Pulse=[this,&S,Now](FKey Code)
    {
        if(S.InputIssued)return true;
        if(Now-S.PhaseAt<.20||!UnitPulse(Code,Now))return false;
        S.InputIssued=true;S.InputAt=Now;return true;
    };
    const auto Approach=[this,&S,Player,Now](FVector2D Target)
    {
        const auto D=Target-Player->GetGroundPosition();
        if(FMath::Abs(D.X)>10.||FMath::Abs(D.Y)>8.)
        {UnitMove(FMath::Abs(D.X)>10.?float(FMath::Sign(D.X)):0.f,
            FMath::Abs(D.Y)>8.?float(FMath::Sign(D.Y)):0.f);S.ArrivalAt=-1;return false;}
        UnitMove(0,0);if(S.ArrivalAt<0)S.ArrivalAt=Now;return Now-S.ArrivalAt>=.20;
    };
    const auto Object=[](const FDungeonSceneRoomView& Room,EDungeonSceneObjectKind Kind)->const FDungeonSceneObjectView*
    {for(const auto& O:Room.Objects)if(O.Kind==Kind)return &O;return nullptr;};
    const auto Observe=[this,&S,Game,Player,HUD](const TCHAR* Label)
    {
        const auto& V=Game->GetEquipmentView();const auto& Room=Game->GetSceneRoomView();
        const auto& I=Game->GetSceneInteractionView();const auto& WA=Player->GetWeaponActionsState();
        auto R=MakeShared<FJsonObject>();const auto P=Player->GetGroundPosition(),C=HUD->GetCameraGroundCenter();
        R->SetStringField(TEXT("record_type"),TEXT("scene_normal_input_post_batch_observation"));
        R->SetStringField(TEXT("label"),Label);R->SetNumberField(TEXT("fixture_phase"),S.Phase);
        R->SetNumberField(TEXT("sim_time_s"),Game->GetSimulationTime());R->SetNumberField(TEXT("wall_offset_s"),Elapsed);
        R->SetStringField(TEXT("run_guid"),V.RunGuid.ToString());R->SetNumberField(TEXT("room_instance_id"),double(V.RoomInstanceId));
        R->SetNumberField(TEXT("game_room"),Game->RoomNumber);R->SetNumberField(TEXT("player_x"),P.X);R->SetNumberField(TEXT("player_y"),P.Y);
        R->SetNumberField(TEXT("player_hp"),Player->Health);R->SetNumberField(TEXT("focus"),WA.Budget.Focus);
        R->SetNumberField(TEXT("coins"),Player->Coins);R->SetNumberField(TEXT("pickup_count"),Game->Pickups.Num());
        R->SetBoolField(TEXT("waiting_for_start"),Game->bWaitingForStart);R->SetBoolField(TEXT("room_cleared"),Game->bRoomCleared);
        R->SetNumberField(TEXT("active_instance_id"),double(V.Slots[V.ActiveSlot].InstanceId));R->SetNumberField(TEXT("active_slot"),V.ActiveSlot);
        R->SetNumberField(TEXT("selected_source_id"),double(V.SelectedSourceId));R->SetBoolField(TEXT("needs_slot_selection"),V.NeedsSlotSelection);
        R->SetBoolField(TEXT("equipment_action_active"),V.Action.Active);R->SetNumberField(TEXT("next_instance_id"),double(V.NextInstanceId));
        R->SetBoolField(TEXT("interaction_pending"),I.Pending);R->SetBoolField(TEXT("needs_confirmation"),I.NeedsConfirmation);
        R->SetNumberField(TEXT("interaction_kind"),int32(I.Kind));R->SetNumberField(TEXT("interaction_object_id"),double(I.ObjectId));
        R->SetNumberField(TEXT("interaction_room_id"),double(I.RoomInstanceId));R->SetNumberField(TEXT("interaction_at"),I.AtTime);
        R->SetNumberField(TEXT("interaction_failure"),int32(I.LastFailure));
        R->SetBoolField(TEXT("survey_whole_prop_rendered"),HUD->GetRenderedSceneSurveyVisible());
        TArray<TSharedPtr<FJsonValue>> ScenePropPaths;
        for(const auto& Path:HUD->GetRenderedScenePropPaths())ScenePropPaths.Add(MakeShared<FJsonValueString>(Path));
        R->SetArrayField(TEXT("actual_scene_prop_draw_paths"),ScenePropPaths);
        R->SetNumberField(TEXT("hud_room"),HUD->GetExplorationRoomNumber());R->SetNumberField(TEXT("hud_reset_serial"),double(HUD->GetExplorationResetSerial()));
        R->SetNumberField(TEXT("hud_explored_vertices"),HUD->GetExploredVertexCount());
        R->SetNumberField(TEXT("survey_current_visibility"),HUD->GetCurrentVisibilityAt(S.Survey));
        R->SetNumberField(TEXT("survey_memory"),HUD->GetExplorationMemoryAt(S.Survey));
        R->SetNumberField(TEXT("camera_ground_x"),C.X);R->SetNumberField(TEXT("camera_ground_y"),C.Y);
        R->SetStringField(TEXT("rendered_player_texture_path"),HUD->GetRenderedPlayerTexturePath());
        R->SetBoolField(TEXT("interface_visible"),HUD->GetInterfaceVisible());
        R->SetNumberField(TEXT("rendered_text_draw_calls"),HUD->GetRenderedTextDrawCalls());
        R->SetNumberField(TEXT("rendered_player_sprite_size"),HUD->GetRenderedActorSpriteSize(Player));
        R->SetBoolField(TEXT("input_a"),Keys.FindRef(EKeys::A));R->SetBoolField(TEXT("input_d"),Keys.FindRef(EKeys::D));
        R->SetBoolField(TEXT("input_w"),Keys.FindRef(EKeys::W));R->SetBoolField(TEXT("input_s"),Keys.FindRef(EKeys::S));
        R->SetBoolField(TEXT("input_e"),Keys.FindRef(EKeys::E));R->SetBoolField(TEXT("input_enter"),Keys.FindRef(EKeys::Enter));
        R->SetBoolField(TEXT("input_escape"),Keys.FindRef(EKeys::Escape));R->SetBoolField(TEXT("input_j"),Keys.FindRef(EKeys::J));
        R->SetBoolField(TEXT("attack_starts_disabled_only_at_sim_zero"),true);
        R->SetBoolField(TEXT("pursuit_remains_active"),true);
        if(auto K=S.Knight.Get())
        {
            R->SetNumberField(TEXT("rendered_knight_sprite_size"),HUD->GetRenderedActorSpriteSize(K));
            const auto KP=K->GetGroundPosition(),D=KP-P;
            R->SetNumberField(TEXT("initial_knight_entity_id"),double(K->GetRuntimeEntityId()));R->SetNumberField(TEXT("initial_knight_hp"),K->Health);
            R->SetNumberField(TEXT("initial_knight_x"),KP.X);R->SetNumberField(TEXT("initial_knight_y"),KP.Y);
            R->SetBoolField(TEXT("initial_knight_bAIEnabled"),K->bAIEnabled);
            R->SetBoolField(TEXT("knight_frame_can_start_attack"),!Game->bGameOver&&!Game->bWaitingForStart&&K->bAIEnabled);
            if(const auto Driver=K->GetStoneKnightDriver())R->SetNumberField(TEXT("initial_knight_kernel_phase"),int32(Driver->State().Phase));
            R->SetNumberField(TEXT("target_distance"),D.Size());R->SetNumberField(TEXT("target_dx"),D.X);R->SetNumberField(TEXT("target_dy"),D.Y);
            R->SetNumberField(TEXT("target_forward_distance"),D.X*Player->Facing);R->SetNumberField(TEXT("player_facing"),Player->Facing);
            R->SetBoolField(TEXT("player_can_start_attack"),Player->CanStartAttack());
            R->SetBoolField(TEXT("initial_knight_dead"),K->bDead);R->SetBoolField(TEXT("initial_knight_death_reported"),K->bDeathReported);
        }
        TArray<TSharedPtr<FJsonValue>> Objects,Sources,Slots;
        for(const auto& O:Room.Objects)
        {auto F=MakeShared<FJsonObject>();F->SetNumberField(TEXT("object_id"),double(O.ObjectId));F->SetNumberField(TEXT("room_instance_id"),double(O.RoomInstanceId));
            F->SetNumberField(TEXT("kind"),int32(O.Kind));F->SetNumberField(TEXT("x"),O.Position.X);F->SetNumberField(TEXT("y"),O.Position.Y);
            F->SetBoolField(TEXT("surveyed"),O.Surveyed);F->SetNumberField(TEXT("survey_count"),O.SurveyCount);Objects.Add(MakeShared<FJsonValueObject>(F));}
        for(const auto& Source:Game->GetEquipmentSources())
        {auto F=MakeShared<FJsonObject>();F->SetNumberField(TEXT("source_id"),double(Source.SourceId));F->SetNumberField(TEXT("room_instance_id"),double(Source.RoomInstanceId));
            F->SetNumberField(TEXT("instance_id"),double(Source.InstanceId));F->SetBoolField(TEXT("consumed"),Source.Consumed);
            F->SetStringField(TEXT("content_id"),UTF8_TO_TCHAR(Source.Item.ContentId.c_str()));F->SetNumberField(TEXT("x"),Source.Position.X);F->SetNumberField(TEXT("y"),Source.Position.Y);
            Sources.Add(MakeShared<FJsonValueObject>(F));}
        for(const auto& Slot:V.Slots)
        {auto F=MakeShared<FJsonObject>();F->SetNumberField(TEXT("instance_id"),double(Slot.InstanceId));F->SetStringField(TEXT("content_id"),Slot.ContentId);
            F->SetNumberField(TEXT("ammo"),Slot.Ammo);F->SetNumberField(TEXT("cooldown_deadline"),Slot.CooldownDeadline);Slots.Add(MakeShared<FJsonValueObject>(F));}
        R->SetArrayField(TEXT("scene_objects"),Objects);R->SetArrayField(TEXT("equipment_sources"),Sources);R->SetArrayField(TEXT("weapon_slots"),Slots);
        Trace.Add(MakeShared<FJsonValueObject>(R));
    };
    if(Elapsed>=FSceneProofState::DeadlineSeconds||Now-S.PhaseAt>12.)
    {Observe(TEXT("deadline_failure"));Fail(TEXT("scene_phase_or_total_deadline"));return;}
    if(S.Phase!=0)Observe(TEXT("post_batch"));
    const auto P=Player->GetGroundPosition();
    const auto& V=Game->GetEquipmentView();const auto& Room=Game->GetSceneRoomView();
    const auto& I=Game->GetSceneInteractionView();
    switch(S.Phase)
    {
    case 0:
    {
        UnitReleaseInputs();
        if(!Game->BeginSceneExplorationPreview()){Fail(TEXT("scene_real_initialization_rejected"));return;}
        const auto& Init=Game->GetEquipmentView();const auto& Scene=Game->GetSceneRoomView();
        auto K=Game->Enemies.Num()==1?Game->Enemies[0].Get():nullptr;
        const auto Survey=Object(Scene,EDungeonSceneObjectKind::Survey),Exit=Object(Scene,EDungeonSceneObjectKind::Exit);
        const bool Valid=Game->GetSimulationTime()==0.&&Game->bWaitingForStart&&Init.Bound&&Scene.Active&&Scene.RunGuid==Init.RunGuid
            &&Scene.RoomInstanceId==Init.RoomInstanceId&&Scene.Objects.Num()==2&&Survey&&Exit&&K&&K->GetStoneKnightDriver()
            &&K->Health==110.f&&!K->bDead&&K->GetRuntimeEntityId()!=0&&Player->Health==100.f&&Player->ArmorId.IsEmpty()
            &&Init.Slots[0].ContentId==TEXT("WPN-SWD-001")&&Init.Slots[0].InstanceId!=0&&Init.Slots[1].InstanceId==0
            &&Game->GetEquipmentSources().IsEmpty()&&Player->GetGroundPosition().Equals(Scene.Layout.Entry,.0001);
        if(!Require(TEXT("scene_real_run_starter_unique_knight_and_two_objects"),Valid))return;
        // Initialization-only attack-start gate. Pursuit remains active;
        // the normal Scene preview keeps autonomous attack starts enabled.
        K->bAIEnabled=false;S.Knight=K;S.KnightId=K->GetRuntimeEntityId();S.LastKnightHP=K->Health;
        S.RunGuid=Init.RunGuid;S.RoomId=Init.RoomInstanceId;S.StarterId=Init.Slots[0].InstanceId;S.InitialGameRoom=Game->RoomNumber;
        S.Entry=Scene.Layout.Entry;S.Survey=Scene.Layout.Survey;S.Exit=Scene.Layout.Exit;S.Barrier=Scene.Layout.Barrier;
        S.SurveyId=Survey->ObjectId;S.ExitId=Exit->ObjectId;
        Observe(TEXT("before_menu"));Go(1);S.PhaseAt=Game->GetSimulationTime();break;
    }
    case 1:
        // The real menu holds the simulation clock at zero. Its Enter edge must
        // be armed by capture wall time, never by waiting for a frozen Now.
        if(!S.InputIssued&&Elapsed>.20&&UnitPulse(EKeys::Enter,Now))
        {S.InputIssued=true;S.InputAt=Now;}
        if(S.InputIssued&&!Game->bWaitingForStart&&Now-S.InputAt>.25&&HUD->GetExplorationRoomNumber()==Game->RoomNumber)
        {
            if(!Require(TEXT("scene_fresh_enter_opens_real_start_gate"),Now>0.&&V.RunGuid==S.RunGuid&&V.RoomInstanceId==S.RoomId))return;
            S.ResetSerial=HUD->GetExplorationResetSerial();S.InitialExplored=HUD->GetExploredVertexCount();Go(2);
        }
        break;
    case 2:if(Approach({S.Barrier.Min.X+100.,S.Entry.Y}))Go(3);break;
    case 3:
        if(Now-S.PhaseAt<.8){UnitMove(0,1);break;}
        UnitMove(0,0);
        if(!Require(TEXT("scene_normal_w_blocked_by_actual_world_wall"),P.X>S.Barrier.Min.X+18.&&P.X<S.Barrier.Max.X-18.
            &&FMath::Abs(P.Y-(S.Barrier.Min.Y-16.))<.05&&V.RoomInstanceId==S.RoomId))return;
        Observe(TEXT("real_wall_contact"));Go(4);break;
    case 4:if(Approach({S.Entry.X,S.Barrier.Min.Y-16.}))Go(5);break;
    case 5:if(Approach({S.Entry.X,S.Barrier.Max.Y+60.}))Go(6);break;
    case 6:if(Approach({S.Survey.X,S.Barrier.Max.Y+60.}))Go(7);break;
    case 7:
        if(Approach(S.Survey+FVector2D(-60.,0.))&&HUD->GetExplorationMemoryAt(S.Survey)==1.&&HUD->GetCurrentVisibilityAt(S.Survey)==1.)
        {
            const auto O=Object(Room,EDungeonSceneObjectKind::Survey);
            if(!Require(TEXT("scene_normal_west_bypass_reveals_survey"),O&&!O->Surveyed&&O->SurveyCount==0
                &&V.RoomInstanceId==S.RoomId&&HUD->GetExplorationResetSerial()==S.ResetSerial&&HUD->GetExploredVertexCount()>S.InitialExplored))return;
            S.RevealedExplored=HUD->GetExploredVertexCount();S.SurveyCoins=Player->Coins;S.SurveyPickups=Game->Pickups.Num();
            S.SurveySources=Game->GetEquipmentSources().Num();S.SurveyNextInstance=V.NextInstanceId;
            Observe(TEXT("before_survey"));Go(8);
        }
        break;
    case 8:
        Pulse(EKeys::E);
        if(S.InputIssued&&Now-S.InputAt>.20)
        {
            const auto O=Object(Room,EDungeonSceneObjectKind::Survey);
            if(!Require(TEXT("scene_fresh_e_survey_once_without_reward"),O&&O->Surveyed&&O->SurveyCount==1&&!I.Pending
                &&Player->Coins==S.SurveyCoins&&Game->Pickups.Num()==S.SurveyPickups&&Game->GetEquipmentSources().Num()==S.SurveySources
                &&V.NextInstanceId==S.SurveyNextInstance&&V.RoomInstanceId==S.RoomId))return;
            Observe(TEXT("after_survey"));Go(9);
        }
        break;
    case 9:
        Pulse(EKeys::E);
        if(S.InputIssued&&Now-S.InputAt>.20)
        {
            const auto O=Object(Room,EDungeonSceneObjectKind::Survey);
            if(!Require(TEXT("scene_repeat_e_never_repeats_survey_or_income"),O&&O->Surveyed&&O->SurveyCount==1&&!I.Pending
                &&I.LastFailure==EDungeonSceneFailure::AlreadySurveyed&&Player->Coins==S.SurveyCoins&&Game->Pickups.Num()==S.SurveyPickups
                &&Game->GetEquipmentSources().Num()==S.SurveySources&&V.NextInstanceId==S.SurveyNextInstance))return;
            Go(10);
        }
        break;
    case 10:if(Approach({S.Entry.X,S.Survey.Y}))Go(11);break;
    case 11:
        if(Approach(S.Entry))
        {
            if(!Require(TEXT("scene_retreat_keeps_memory_outside_visibility"),HUD->GetCurrentVisibilityAt(S.Survey)==0.
                &&HUD->GetExplorationMemoryAt(S.Survey)==1.&&HUD->GetExploredVertexCount()>=S.RevealedExplored
                &&HUD->GetExplorationResetSerial()==S.ResetSerial&&V.RoomInstanceId==S.RoomId))return;
            Observe(TEXT("retreat_memory"));Go(12);
        }
        break;
    case 12:
        if(auto K=S.Knight.Get())
        {
            // A moving enemy cannot settle at a repeatedly recomputed K.X-70
            // for .20s. Read the authored first SWD window, then stop normal
            // movement as soon as its real facing/XY/height gates are legal.
            const auto& First=DungeonContentCombat::GetWeaponDefinition(DungeonContentCombat::EWeapon::SWD001)->Primary[0];
            const double ReachPct=FMath::Clamp(V.Stats.Final[DungeonEquipmentStats::EStat::ReachPct],-15.,15.);
            const double Range=First.Range*(1.+ReachPct/100.);const auto D=K->GetGroundPosition()-P;
            const double X=D.X*Player->Facing;
            const bool AxisLegal=ADungeonFighter::CanHitTarget(D,Player->Facing,float(Range),float(First.Depth),
                float(Player->GetCombatHeight()),float(K->GetCombatHeight()))&&X>=First.MinRange;
            const bool ShapeLegal=First.Shape!=DungeonContentCombat::EShape::ForwardEllipse
                ||FMath::Square(X/Range)+FMath::Square(D.Y/First.Depth)<=1.;
            if(AxisLegal&&ShapeLegal)
            {UnitMove(0,0);Observe(TEXT("actual_sword_range_ready"));Go(13);}
            else if(FMath::Abs(D.Y)>First.Depth*.5)UnitMove(0,float(FMath::Sign(D.Y)));
            else UnitMove(float(FMath::Sign(D.X)),0);
        }
        else Fail(TEXT("scene_initial_knight_missing_before_combat"));
        break;
    case 13:
    {
        auto K=S.Knight.Get();if(!K){Fail(TEXT("scene_initial_knight_missing_in_combat"));return;}
        if(Player->GetMeleeCombatState().Action.Active)S.SwordActionObserved=true;
        if(K->bDead&&Player->CanStartAttack())
        {
            if(!Require(TEXT("scene_normal_sword_damage_clears_unique_knight"),S.SwordActionObserved&&K->bDeathReported
                &&K->Health==0.f&&Game->bRoomCleared&&K->GetRuntimeEntityId()==S.KnightId&&V.Slots[V.ActiveSlot].InstanceId==S.StarterId
                &&Player->Health==100.f))return;
            Observe(TEXT("real_sword_clear"));Go(14);
        }
        else if(Player->CanStartAttack())UnitPulse(EKeys::J,Now);
        break;
    }
    case 14:if(Approach({665.,S.Exit.Y}))Go(15);break;
    case 15:
        Pulse(EKeys::E);
        if(S.InputIssued&&Now-S.InputAt>.20)
        {
            if(!Require(TEXT("scene_old_665_e_cannot_open_or_change_room"),V.RunGuid==S.RunGuid&&V.RoomInstanceId==S.RoomId
                &&Game->RoomNumber==S.InitialGameRoom&&!I.Pending&&!V.Action.Active&&!V.NeedsSlotSelection))return;
            Observe(TEXT("old_exit_rejected"));Go(16);
        }
        break;
    case 16:if(Approach(S.Exit))Go(17);break;
    case 17:
        Pulse(EKeys::E);
        if(S.InputIssued&&Now-S.InputAt>.20)
        {
            if(!Require(TEXT("scene_actual_1180_e_opens_current_room_confirmation"),I.Pending&&I.NeedsConfirmation
                &&I.Kind==EDungeonSceneInteractionKind::Exit&&I.ObjectId==S.ExitId&&I.RoomInstanceId==S.RoomId
                &&V.RoomInstanceId==S.RoomId&&V.RunGuid==S.RunGuid))return;
            Observe(TEXT("exit_confirmation"));Go(18);
        }
        break;
    case 18:
        Pulse(EKeys::Escape);
        if(S.InputIssued&&Now-S.InputAt>.20)
        {
            if(!Require(TEXT("scene_normal_escape_cancels_without_travel"),!I.Pending&&V.RoomInstanceId==S.RoomId
                &&V.RunGuid==S.RunGuid&&Game->RoomNumber==S.InitialGameRoom))return;
            Observe(TEXT("exit_cancelled"));Go(19);
        }
        break;
    case 19:
        Pulse(EKeys::E);
        if(S.InputIssued&&Now-S.InputAt>.20&&I.Pending&&I.NeedsConfirmation)
        {
            S.ExitHP=Player->Health;S.ExitCoins=Player->Coins;S.ExitFocus=Player->GetWeaponActionsState().Budget.Focus;
            S.ExitAmmo=V.Slots[V.ActiveSlot].Ammo;S.ExitCooldown=V.Slots[V.ActiveSlot].CooldownDeadline;
            S.ExitNextInstance=V.NextInstanceId;S.ExitCritDraw=V.NextCritDraw;Observe(TEXT("before_fresh_exit_confirm"));Go(20);
        }
        break;
    case 20:
        Pulse(EKeys::Enter);
        if(S.InputIssued&&V.RoomInstanceId!=S.RoomId)Go(21);
        break;
    case 21:
        UnitMove(0,0);
        if(Now-S.PhaseAt<.3||HUD->GetExplorationRoomNumber()!=Game->RoomNumber)break;
        {
            const auto Old=Game->FindSceneRoomView(S.RoomId);const auto OldSurvey=Old?Object(*Old,EDungeonSceneObjectKind::Survey):nullptr;
            const auto NewSurvey=Object(Room,EDungeonSceneObjectKind::Survey);
            const float HalfView=580.f/.65f;
            const double CameraTarget=FMath::Clamp(float(S.Entry.X),float(DungeonRoomLayout::MinX)+HalfView,float(DungeonRoomLayout::MaxX)-HalfView);
            const bool Valid=V.RunGuid==S.RunGuid&&V.RoomInstanceId==S.RoomId+1&&Room.RunGuid==S.RunGuid
                &&Room.RoomInstanceId==V.RoomInstanceId&&Game->RoomNumber==S.InitialGameRoom+1
                &&Player->GetGroundPosition().Equals(S.Entry,12.)&&!I.Pending&&V.Slots[V.ActiveSlot].InstanceId==S.StarterId
                &&Player->Health==S.ExitHP&&Player->Coins==S.ExitCoins&&Player->GetWeaponActionsState().Budget.Focus==S.ExitFocus
                &&V.Slots[V.ActiveSlot].Ammo==S.ExitAmmo&&V.Slots[V.ActiveSlot].CooldownDeadline==S.ExitCooldown
                &&V.NextInstanceId==S.ExitNextInstance&&V.NextCritDraw==S.ExitCritDraw
                &&OldSurvey&&OldSurvey->Surveyed&&OldSurvey->SurveyCount==1&&NewSurvey&&!NewSurvey->Surveyed&&NewSurvey->SurveyCount==0
                &&HUD->GetExplorationResetSerial()==S.ResetSerial+1&&HUD->GetExplorationMemoryAt(S.Survey)==0.
                &&HUD->GetCurrentVisibilityAt(S.Survey)==0.&&FMath::Abs(HUD->GetCameraGroundCenter().X-CameraTarget)<.01;
            Observe(TEXT("new_room_hud_reset"));
            if(!Require(TEXT("scene_fresh_enter_keeps_run_instances_and_resets_new_room_hud"),Valid))return;
            if(!Require(TEXT("scene_completed_within_55s"),Elapsed<FSceneProofState::DeadlineSeconds))return;
            UnitReleaseInputs();S.Phase=22;bGameplayFinished=true;FinishAudioCapture();
        }
        break;
    default:Fail(TEXT("scene_invalid_proof_phase"));break;
    }
}
