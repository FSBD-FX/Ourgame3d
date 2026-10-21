// Opt-in integration fixture. Sources are explicitly registered QA objects;
// every transfer below is requested through ordinary controller key edges.
// This does not certify DEV loot tables, full armor art or disk persistence.
void ADungeonContentProbe::TickEquipmentProof()
{
    if(bGameplayFinished) return;
    auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this));
    auto Player=Game?Game->GetPlayerFighter():nullptr;
    const auto Fail=[this](const FString& Reason)
    {
        UnitFailure=Reason;UnitReleaseInputs();bGameplayFinished=true;
        Check(TEXT("equipment_completed_within_40s"),false);FinishAudioCapture();
    };
    if(!Game || !Player) {Fail(TEXT("missing_player_or_mode"));return;}
    const double Now=Game->GetSimulationTime();
    if(bUnitEdgeDown && Now>UnitEdgeAt)
    {Key(UnitEdgeKey,false);bUnitEdgeDown=false;UnitReleasedAt=Now;}
    const auto& V=Game->GetEquipmentView();
    const auto ActiveId=[&V](){return V.Slots[V.ActiveSlot].InstanceId;};
    const auto FindSource=[Game](uint64 Id)->const FDungeonEquipmentSourceView*
    {for(const auto& S:Game->GetEquipmentSources())if(S.SourceId==Id)return &S;return nullptr;};
    const auto Go=[this,Now](int32 Phase)
    {
        UnitMove(0,0);UnitPhase=Phase;UnitPhaseAt=Now;
        bEquipmentOldHeld=true;bEquipmentDuration=true;bEquipmentStarted=false;
    };
    const auto Approach=[this,Player,Now](FVector2D Target)
    {
        const auto P=Player->GetGroundPosition();
        const float DX=float(Target.X-P.X),DY=float(Target.Y-P.Y);
        // Stop comfortably inside the real 80x40 pickup rectangle. A 5cm
        // arrival target can oscillate under genuine 50ms frames at full speed.
        constexpr float Arrival=24.f;
        if(FMath::Abs(DX)>Arrival || FMath::Abs(DY)>Arrival)
        {UnitMove(FMath::Abs(DX)>Arrival?FMath::Sign(DX):0.f,FMath::Abs(DY)>Arrival?FMath::Sign(DY):0.f);bEquipmentStarted=false;return false;}
        UnitMove(0,0);
        if(!bEquipmentStarted) {bEquipmentStarted=true;UnitPhaseAt=Now;}
        return Now-UnitPhaseAt>=.2;
    };
    auto Row=MakeShared<FJsonObject>();
    Row->SetStringField(TEXT("record_type"),TEXT("equipment_post_batch_state_observation"));
    Row->SetNumberField(TEXT("fixture_phase"),UnitPhase);Row->SetNumberField(TEXT("sim_time_s"),Now);
    Row->SetNumberField(TEXT("wall_offset_s"),Elapsed);Row->SetStringField(TEXT("run_guid"),V.RunGuid.ToString());
    Row->SetNumberField(TEXT("player_x"),Player->GetGroundPosition().X);Row->SetNumberField(TEXT("player_y"),Player->GetGroundPosition().Y);
    Row->SetNumberField(TEXT("hp"),Player->Health);Row->SetNumberField(TEXT("max_hp"),Player->MaxHealth);
    Row->SetNumberField(TEXT("focus"),Player->Focus);Row->SetNumberField(TEXT("revision"),double(V.Revision));
    Row->SetNumberField(TEXT("active_slot"),V.ActiveSlot);Row->SetNumberField(TEXT("selected_source"),double(V.SelectedSourceId));
    Row->SetBoolField(TEXT("needs_slot_selection"),V.NeedsSlotSelection);Row->SetNumberField(TEXT("selection_slot"),V.SelectionSlot);
    Row->SetBoolField(TEXT("equipment_action_active"),V.Action.Active);Row->SetNumberField(TEXT("equipment_action_kind"),int32(V.Action.Kind));
    Row->SetNumberField(TEXT("equipment_action_start"),V.Action.Start);Row->SetNumberField(TEXT("equipment_action_deadline"),V.Action.Deadline);
    Row->SetNumberField(TEXT("equipment_action_slot"),V.Action.Slot);Row->SetNumberField(TEXT("crit_next_draw"),double(V.NextCritDraw));
    Row->SetStringField(TEXT("animation"),Player->AnimationName);
    TArray<TSharedPtr<FJsonValue>> Slots;
    for(const auto& Slot:V.Slots)
    {
        auto S=MakeShared<FJsonObject>();S->SetStringField(TEXT("content_id"),Slot.ContentId);
        S->SetNumberField(TEXT("instance_id"),double(Slot.InstanceId));S->SetNumberField(TEXT("grade"),Slot.Grade);
        S->SetNumberField(TEXT("cooldown_deadline"),Slot.CooldownDeadline);Slots.Add(MakeShared<FJsonValueObject>(S));
    }
    Row->SetArrayField(TEXT("slots"),Slots);
    TArray<TSharedPtr<FJsonValue>> Sources;
    for(const auto& Source:Game->GetEquipmentSources())
    {
        auto S=MakeShared<FJsonObject>();S->SetNumberField(TEXT("source_id"),double(Source.SourceId));
        S->SetNumberField(TEXT("instance_id"),double(Source.InstanceId));S->SetBoolField(TEXT("consumed"),Source.Consumed);
        S->SetNumberField(TEXT("x"),Source.Position.X);S->SetNumberField(TEXT("y"),Source.Position.Y);
        Sources.Add(MakeShared<FJsonValueObject>(S));
    }
    Row->SetArrayField(TEXT("sources"),Sources);
    const auto Controller=UGameplayStatics::GetPlayerController(this,0);
    if(auto HUD=Controller?Cast<ADungeonHUD>(Controller->GetHUD()):nullptr)
    {
        Row->SetStringField(TEXT("rendered_player_texture_path"),HUD->GetRenderedPlayerTexturePath());
        Row->SetNumberField(TEXT("sprite_canvas_size"),HUD->GetRenderedPlayerSpriteSize());
        Row->SetNumberField(TEXT("camera_x"),HUD->GetCameraGroundCenter().X);
    }
    Trace.Add(MakeShared<FJsonValueObject>(Row));
    if(Elapsed>=40. || Player->bDead || Game->bGameOver)
    {Fail(TEXT("deadline_or_player_death"));return;}
    if(UnitPhase>0 && Now-UnitPhaseAt>8.)
    {Fail(FString::Printf(TEXT("equipment_phase_%02d_timeout"),UnitPhase));return;}
    switch(UnitPhase)
    {
    case 0:
    {
        if(!Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1))
        {Fail(TEXT("equipment_run_not_bound"));return;}
        DungeonEquipmentInventory::FItem Heavy;Heavy.ContentId="WPN-GSW-001";
        DungeonEquipmentInventory::FItem Armor;Armor.ContentId="ARM-LGT-001";Armor.Tier=5;
        Armor.Package=DungeonEquipmentStats::EPackage::Mixed;
        Armor.Affixes={{"AFF-N-014",25,{9,10}},{"AFF-P-017",25,{9,10}},{"AFF-P-018",25,{9,10}}};
        DungeonEquipmentInventory::FItem Sword;Sword.ContentId="WPN-SWD-001";Sword.Grade=1;
        const auto H=Game->RegisterEquipmentSource(TEXT("equipment-proof-heavy"),Heavy,{-480,0});
        const auto A=Game->RegisterEquipmentSource(TEXT("equipment-proof-armor"),Armor,{-360,0});
        const auto S=Game->RegisterEquipmentSource(TEXT("equipment-proof-second-sword"),Sword,{-240,0});
        const auto& SetupView=Game->GetEquipmentView();
        EquipmentCritBefore=SetupView.NextCritDraw;
        EquipmentStarter=SetupView.Slots[SetupView.ActiveSlot].InstanceId;
        EquipmentHeavy=H.InstanceId;EquipmentArmor=A.InstanceId;EquipmentSecondSword=S.InstanceId;
        EquipmentHeavySource=H.SourceId;EquipmentArmorSource=A.SourceId;EquipmentSecondSwordSource=S.SourceId;
        const bool Valid=H.Ok()&&A.Ok()&&S.Ok()&&EquipmentStarter&&SetupView.Bound&&Player->IsEquipmentBound()
            &&SetupView.Slots[SetupView.ActiveSlot].ContentId==TEXT("WPN-SWD-001")&&SetupView.Slots[SetupView.ActiveSlot].Grade==0&&!SetupView.Slots[2].InstanceId;
        Check(TEXT("equipment_real_run_starter_and_registered_sources"),Valid);
        if(!Valid) {Fail(TEXT("source_or_starter_setup_failed"));return;}
        Fixture=0;Game->bWaitingForStart=false;
        Game->LastMessage=TEXT("装备接入测试：正常 E 拾取、Q 切换；地面图标与甲层仍为候选");
        Go(1);break;
    }
    case 1:
        if(!bEquipmentStarted && Now-UnitPhaseAt>.2 && UnitPulse(EKeys::K,Now)) bEquipmentStarted=true;
        if(Player->GetWeaponSkillAction().Active) UnitSkillId=Player->GetWeaponSkillAction().ActionId;
        if(bEquipmentStarted && UnitSkillId && !Player->GetWeaponSkillAction().Active)
        {
            EquipmentSwordCooldown=V.Slots[V.ActiveSlot].CooldownDeadline;
            Check(TEXT("normal_k_lock_single_crit_and_real_cooldown"),V.NextCritDraw==EquipmentCritBefore+1&&EquipmentSwordCooldown>Now);
            Go(2);
        }
        break;
    case 2:
        if(Approach({-480,0}) && V.SelectedSourceId==EquipmentHeavySource && UnitPulse(EKeys::E,Now)) Go(3);
        break;
    case 3:
        if(V.Action.Active)
        {
            bEquipmentStarted=true;bEquipmentOldHeld&=ActiveId()==EquipmentStarter;
            bEquipmentDuration&=FMath::Abs(V.Action.Deadline-V.Action.Start-.35)<1.e-12;
        }
        else if(bEquipmentStarted)
        {
            Check(TEXT("normal_e_weapon_035_kept_old_until_commit"),bEquipmentOldHeld&&bEquipmentDuration&&ActiveId()==EquipmentHeavy
                &&FindSource(EquipmentHeavySource)&&FindSource(EquipmentHeavySource)->Consumed);
            Go(4);
        }
        break;
    case 4:
        if(Now-UnitPhaseAt>.5 && UnitPulse(EKeys::Q,Now)) Go(5);
        break;
    case 5:
        if(V.Action.Active)
        {
            bEquipmentStarted=true;bEquipmentOldHeld&=ActiveId()==EquipmentHeavy;
            bEquipmentDuration&=FMath::Abs(V.Action.Deadline-V.Action.Start-.35)<1.e-12;
        }
        else if(bEquipmentStarted)
        {
            Check(TEXT("normal_q_035_kept_instances_and_cooldown"),bEquipmentOldHeld&&bEquipmentDuration&&ActiveId()==EquipmentStarter
                &&V.Slots[1-V.ActiveSlot].InstanceId==EquipmentHeavy&&V.Slots[V.ActiveSlot].CooldownDeadline==EquipmentSwordCooldown);
            Go(6);
        }
        break;
    case 6:
        if(Approach({-360,0})&&V.SelectedSourceId==EquipmentArmorSource&&UnitPulse(EKeys::E,Now)) Go(7);
        break;
    case 7:
        if(V.Action.Active)
        {
            bEquipmentStarted=true;bEquipmentOldHeld&=V.Slots[2].InstanceId==0&&Player->MaxHealth==100.f;
            bEquipmentDuration&=FMath::Abs(V.Action.Deadline-V.Action.Start-.5)<1.e-12;
        }
        else if(bEquipmentStarted)
        {
            Check(TEXT("normal_e_armor_050_single_stats_and_hp_cap"),bEquipmentOldHeld&&bEquipmentDuration&&V.Slots[2].InstanceId==EquipmentArmor
                &&Player->MaxHealth==125.f&&Player->Health==100.f&&V.Stats.Armor==14.&&V.Stats.FocusRegen==15.);
            Go(8);
        }
        break;
    case 8:
        if(Approach({-240,0})&&V.SelectedSourceId==EquipmentSecondSwordSource&&UnitPulse(EKeys::E,Now))
        {EquipmentRevisionBeforeSelection=V.Revision;Go(9);}
        break;
    case 9:
        if(V.NeedsSlotSelection&&Now-UnitPhaseAt>.6)
        {
            Check(TEXT("full_slots_e_requires_explicit_fresh_selection"),!V.Action.Active&&V.Revision==EquipmentRevisionBeforeSelection
                &&ActiveId()==EquipmentStarter&&V.Slots[1-V.ActiveSlot].InstanceId==EquipmentHeavy);
            if(UnitPulse(EKeys::Right,Now)) Go(10);
        }
        break;
    case 10:
        if(!bUnitEdgeDown&&V.SelectionSlot==1-V.ActiveSlot&&UnitPulse(EKeys::Enter,Now)) Go(11);
        break;
    case 11:
        if(V.Action.Active) {bEquipmentStarted=true;bEquipmentOldHeld&=ActiveId()==EquipmentStarter&&V.Slots[1-V.ActiveSlot].InstanceId==EquipmentHeavy;}
        else if(bEquipmentStarted)
        {
            for(const auto& Source:Game->GetEquipmentSources())
                if(!Source.Consumed&&Source.InstanceId==EquipmentHeavy) EquipmentDropSource=Source.SourceId;
            Check(TEXT("normal_enter_backup_replacement_dropped_old_instance"),bEquipmentOldHeld&&ActiveId()==EquipmentStarter
                &&V.Slots[1-V.ActiveSlot].InstanceId==EquipmentSecondSword&&EquipmentDropSource!=0);
            Go(12);
        }
        break;
    case 12:
    {
        const auto S=FindSource(EquipmentDropSource);if(!S){Fail(TEXT("old_weapon_missing_on_ground"));return;}
        if(Approach(S->Position)&&V.SelectedSourceId==EquipmentDropSource&&UnitPulse(EKeys::E,Now)) Go(13);
        break;
    }
    case 13:
        if(V.NeedsSlotSelection&&Now-UnitPhaseAt>.4&&UnitPulse(EKeys::Right,Now)) Go(14);
        break;
    case 14:
        if(!bUnitEdgeDown&&V.SelectionSlot==1-V.ActiveSlot&&UnitPulse(EKeys::Enter,Now)) Go(15);
        break;
    case 15:
        if(V.Action.Active) bEquipmentStarted=true;
        else if(bEquipmentStarted)
        {
            Check(TEXT("normal_e_repickup_preserved_old_instance"),ActiveId()==EquipmentStarter
                &&V.Slots[1-V.ActiveSlot].InstanceId==EquipmentHeavy&&V.Slots[1-V.ActiveSlot].CooldownDeadline==0.
                &&FindSource(EquipmentDropSource)&&FindSource(EquipmentDropSource)->Consumed
                &&V.Slots[V.ActiveSlot].CooldownDeadline==EquipmentSwordCooldown);
            Go(16);
        }
        break;
    case 16:
        if(Now-UnitPhaseAt>1.)
        {Check(TEXT("equipment_completed_within_40s"),Elapsed<40.);UnitReleaseInputs();bGameplayFinished=true;FinishAudioCapture();}
        break;
    default: Fail(TEXT("invalid_equipment_phase"));break;
    }
}
