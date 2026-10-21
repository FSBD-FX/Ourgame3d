// Opt-in visual integration proof: QA-authored sources, real E transactions,
// A/D facing changes and J attacks. Never writes armor, pixels or HUD state.
void ADungeonContentProbe::TickArmorLayerProof()
{
    if(bGameplayFinished) return;
    auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this));
    auto Player=Game?Game->GetPlayerFighter():nullptr;
    auto Controller=UGameplayStatics::GetPlayerController(this,0);
    auto HUD=Controller?Cast<ADungeonHUD>(Controller->GetHUD()):nullptr;
    const auto Fail=[this](const FString& Reason)
    {
        UnitFailure=Reason;UnitReleaseInputs();bGameplayFinished=true;
        Check(bArmorComboProof?TEXT("armor_combo_completed_within_55s"):TEXT("armor_layer_completed_within_40s"),false);FinishAudioCapture();
    };
    if(!Game || !Player || !HUD) {Fail(TEXT("missing_mode_player_or_hud"));return;}
    const double Now=Game->GetSimulationTime();
    if(bUnitEdgeDown && Now>UnitEdgeAt)
    {Key(UnitEdgeKey,false);bUnitEdgeDown=false;UnitReleasedAt=Now;}
    static const TCHAR* Ids[]={TEXT(""),TEXT("ARM-LGT-001"),TEXT("ARM-MED-001"),TEXT("ARM-HVY-001"),TEXT("ARM-ROB-001")};
    static const TCHAR* Names[]={TEXT("none"),TEXT("LGT"),TEXT("MED"),TEXT("HVY"),TEXT("ROB")};
    const FString ExpectedArmor=Ids[FMath::Clamp(ArmorVariant,0,4)];
    const auto& V=Game->GetEquipmentView();
    const auto Go=[this,Now](int32 Phase){UnitMove(0,0);UnitPhase=Phase;UnitPhaseAt=Now;};
    const auto LayersMatch=[this,HUD,&ExpectedArmor](bool Primary,bool Walk=false,int32 Stage=1)
    {
        if(!HUD->GetRenderedArmorLayersUsed()) return false;
        const auto& Paths=HUD->GetRenderedArmorLayerPaths();
        const bool NearRequired=bArmorSleevesProof && Primary && Stage>=2 && ExpectedArmor==TEXT("ARM-ROB-001");
        const int32 Expected=ExpectedArmor.IsEmpty()?2:NearRequired?4:Primary||Walk?3:4;
        if(Paths.Num()!=Expected) return false;
        FString Identity=ExpectedArmor;Identity.ReplaceInline(TEXT("-"),TEXT("_"));
        bool Far=false,Near=false,Front=Identity.IsEmpty(),Back=Identity.IsEmpty()||Primary||Walk,ClothNear=!NearRequired;
        for(const FString& Path:Paths)
        {
            const FString Folder=Primary?Stage==1?TEXT("/v009/ArmorPrimary1/"):Stage==2?(bArmorSleevesProof?TEXT("/v013/ArmorPrimary2Sleeves/"):TEXT("/v011/ArmorPrimary2/")):(bArmorSleevesProof?TEXT("/v014/ArmorPrimary3Sleeves/"):TEXT("/v012/ArmorPrimary3/")):Walk?TEXT("/v010/ArmorWalk/"):TEXT("/v008/ArmorIdle/");
            if(!Path.Contains(Folder)) return false;
            if(Path.Contains(TEXT("body_far"))) Far=true;
            else if(Path.Contains(TEXT("body_near"))) Near=true;
            else if(!Identity.IsEmpty() && Path.Contains(Identity+TEXT("_front_"))) Front=true;
            else if(NearRequired && Path.Contains(Identity+TEXT("_near_"))) ClothNear=true;
            else if(!Identity.IsEmpty() && !Primary && Path.Contains(Identity+TEXT("_back_"))) Back=true;
            else return false;
        }
        return Far&&Near&&Front&&Back&&ClothNear;
    };
    if((UnitPhase==1 || UnitPhase==4) && LayersMatch(false,true))
        for(const FString& Path:HUD->GetRenderedArmorLayerPaths())
            if(Path.Contains(TEXT("body_far")))
                for(int32 I=0;I<6;++I)
                    if(Path.Contains(FString::Printf(TEXT("_%03d_"),I))) ArmorWalkMask[UnitPhase==1?0:1]|=1<<I;
    if(UnitPhase==3 || UnitPhase==6)
    {
        const int32 Side=UnitPhase==3?0:1;
        const auto& Action=Player->GetMeleeCombatState().Action;
        if(Action.Active && !Action.StartedAirborne && Player->ComboStage==1) bArmorPrimaryAccepted=true;
        if(bArmorComboProof && Action.Active && Action.AttackId!=ArmorComboLastId[Side])
        {
            const int32 Stage=int32(Action.Stage);
            const int32 ExpectedStage=ArmorComboStageMask[Side]==0?0:ArmorComboStageMask[Side]==1?1:ArmorComboStageMask[Side]==3?2:-1;
            if(ExpectedStage==0) ArmorComboWeaponInstance[Side]=Action.WeaponInstanceId;
            bArmorComboContinuous[Side]&=Stage==ExpectedStage && !Action.StartedAirborne
                && Action.WeaponInstanceId==V.Slots[V.ActiveSlot].InstanceId
                && Action.WeaponInstanceId!=0 && Action.WeaponInstanceId==ArmorComboWeaponInstance[Side]
                && Player->ArmorId==ExpectedArmor
                && Action.Facing==(Side==0?1.:-1.);
            if(Stage>0) bArmorComboContinuous[Side]&=Action.Start==ArmorComboLastEnd[Side];
            if(Stage>=0 && Stage<3) ArmorComboStageMask[Side]|=1<<Stage;
            ArmorComboLastId[Side]=Action.AttackId;ArmorComboLastEnd[Side]=Action.End;
        }
        if(bArmorComboProof)
        {
            for(int32 Stage=1;Stage<=3;++Stage)
                if(LayersMatch(true,false,Stage))
                {
                    for(const FString& Path:HUD->GetRenderedArmorLayerPaths())
                        if(Path.Contains(TEXT("body_far")))
                            for(int32 I=0;I<6;++I)
                                if(Path.Contains(FString::Printf(TEXT("_%03d_"),I)))
                                {
                                    ArmorComboFrameMask[Side][Stage-1]|=1<<I;
                                    if(bArmorSleevesProof && ExpectedArmor==TEXT("ARM-ROB-001") && Stage>=2)
                                    {
                                        const auto& Stack=HUD->GetRenderedPlayerDrawStack();
                                        const FString PoseTag=FString::Printf(TEXT("_%03d_"),I);
                                        const bool Ordered=Stack.Num()==5 && Stack[0].Contains(TEXT("body_far"))
                                            && Stack[1].Contains(TEXT("ARM_ROB_001_front_")) && Stack[2].Contains(TEXT("T_military_sword_v002"))
                                            && Stack[3].Contains(TEXT("ARM_ROB_001_near_")) && Stack[4].Contains(TEXT("body_near"))
                                            && Stack[0].Contains(PoseTag) && Stack[1].Contains(PoseTag)
                                            && Stack[3].Contains(PoseTag) && Stack[4].Contains(PoseTag);
                                        bArmorSleeveOrderValid[Side][Stage-2]&=Ordered;
                                        if(Ordered) ArmorSleeveOrderFrameMask[Side][Stage-2]|=1<<I;
                                    }
                                }
                }
            if(Action.Active && Player->ComboStage>=1 && Player->ComboStage<=2
                && Player->AttackPhase==TEXT("recovery") && Player->AttackTime>0 && Player->AttackTime<=.10f
                && UnitQueuedStage==Player->ComboStage && UnitPulse(EKeys::J,Now)) ++UnitQueuedStage;
        }
        if(LayersMatch(true))
            for(const FString& Path:HUD->GetRenderedArmorLayerPaths())
                if(Path.Contains(TEXT("body_far")))
                    for(int32 I=0;I<6;++I)
                        if(Path.Contains(FString::Printf(TEXT("_%03d_"),I))) ArmorPrimaryMask[Side]|=1<<I;
    }
    auto Row=MakeShared<FJsonObject>();
    Row->SetStringField(TEXT("record_type"),TEXT("armor_layer_post_batch_observation"));
    Row->SetNumberField(TEXT("sim_time_s"),Now);Row->SetNumberField(TEXT("wall_offset_s"),Elapsed);
    Row->SetNumberField(TEXT("fixture_phase"),UnitPhase);Row->SetNumberField(TEXT("variant"),ArmorVariant);
    Row->SetStringField(TEXT("armor_id"),Player->ArmorId);Row->SetNumberField(TEXT("armor_instance_id"),double(V.Slots[2].InstanceId));
    Row->SetStringField(TEXT("animation"),Player->AnimationName);Row->SetNumberField(TEXT("facing"),Player->Facing);
    Row->SetNumberField(TEXT("player_x"),Player->GetGroundPosition().X);Row->SetNumberField(TEXT("player_y"),Player->GetGroundPosition().Y);
    Row->SetBoolField(TEXT("actual_layer_draw_used"),HUD->GetRenderedArmorLayersUsed());
    Row->SetStringField(TEXT("rendered_player_texture_path"),HUD->GetRenderedPlayerTexturePath());
    Row->SetNumberField(TEXT("sprite_canvas_size"),HUD->GetRenderedPlayerSpriteSize());
    const auto& ObservedAction=Player->GetMeleeCombatState().Action;
    Row->SetNumberField(TEXT("melee_attack_id"),double(ObservedAction.AttackId));
    Row->SetNumberField(TEXT("melee_stage"),ObservedAction.Stage);
    Row->SetNumberField(TEXT("melee_start"),ObservedAction.Start);
    Row->SetNumberField(TEXT("melee_end"),ObservedAction.End);
    Row->SetNumberField(TEXT("melee_weapon_instance_id"),double(ObservedAction.WeaponInstanceId));
    Row->SetBoolField(TEXT("melee_active"),ObservedAction.Active);
    TArray<TSharedPtr<FJsonValue>> LayerPaths;
    for(const FString& Path:HUD->GetRenderedArmorLayerPaths()) LayerPaths.Add(MakeShared<FJsonValueString>(Path));
    Row->SetArrayField(TEXT("actual_drawn_layer_paths"),LayerPaths);
    TArray<TSharedPtr<FJsonValue>> DrawStack;
    for(const FString& Path:HUD->GetRenderedPlayerDrawStack()) DrawStack.Add(MakeShared<FJsonValueString>(Path));
    Row->SetArrayField(TEXT("actual_drawn_player_stack"),DrawStack);
    Row->SetBoolField(TEXT("armor_sleeves_profile"),bArmorSleevesProof);
    Row->SetNumberField(TEXT("primary_right_mask"),ArmorPrimaryMask[0]);Row->SetNumberField(TEXT("primary_left_mask"),ArmorPrimaryMask[1]);
    Row->SetNumberField(TEXT("walk_right_mask"),ArmorWalkMask[0]);Row->SetNumberField(TEXT("walk_left_mask"),ArmorWalkMask[1]);
    Row->SetBoolField(TEXT("armor_combo_profile"),bArmorComboProof);
    for(int32 Side=0;Side<2;++Side)
    {
        Row->SetNumberField(FString::Printf(TEXT("combo_%s_stage_mask"),Side==0?TEXT("right"):TEXT("left")),ArmorComboStageMask[Side]);
        Row->SetBoolField(FString::Printf(TEXT("combo_%s_continuous"),Side==0?TEXT("right"):TEXT("left")),bArmorComboContinuous[Side]);
        Row->SetNumberField(FString::Printf(TEXT("combo_%s_frozen_weapon_instance_id"),Side==0?TEXT("right"):TEXT("left")),double(ArmorComboWeaponInstance[Side]));
        for(int32 Stage=0;Stage<2;++Stage)
        {
            Row->SetNumberField(FString::Printf(TEXT("sleeve_%s_p%d_order_frame_mask"),Side==0?TEXT("right"):TEXT("left"),Stage+2),ArmorSleeveOrderFrameMask[Side][Stage]);
            Row->SetBoolField(FString::Printf(TEXT("sleeve_%s_p%d_order_valid"),Side==0?TEXT("right"):TEXT("left"),Stage+2),bArmorSleeveOrderValid[Side][Stage]);
        }
        for(int32 Stage=0;Stage<3;++Stage)
            Row->SetNumberField(FString::Printf(TEXT("combo_%s_p%d_frame_mask"),Side==0?TEXT("right"):TEXT("left"),Stage+1),ArmorComboFrameMask[Side][Stage]);
    }
    Row->SetBoolField(TEXT("equipment_action_active"),V.Action.Active);
    Row->SetBoolField(TEXT("needs_slot_selection"),V.NeedsSlotSelection);
    Row->SetNumberField(TEXT("selection_slot"),V.SelectionSlot);
    Row->SetNumberField(TEXT("equipment_action_start"),V.Action.Start);Row->SetNumberField(TEXT("equipment_action_deadline"),V.Action.Deadline);
    Trace.Add(MakeShared<FJsonValueObject>(Row));
    const double Deadline=bArmorComboProof?55.:40.;
    if(Elapsed>=Deadline || Player->bDead) {Fail(TEXT("deadline_or_player_death"));return;}
    if(UnitPhase>0 && Now-UnitPhaseAt>6.) {Fail(TEXT("armor_phase_timeout"));return;}
    switch(UnitPhase)
    {
    case 0:
        if(!Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1)) {Fail(TEXT("run_setup_failed"));return;}
        Check(TEXT("armor_layer_real_starter_no_armor"),Player->IsEquipmentBound()&&Player->ArmorId.IsEmpty()
            &&Game->GetEquipmentView().Slots[Game->GetEquipmentView().ActiveSlot].ContentId==TEXT("WPN-SWD-001"));
        Fixture=0;Game->bWaitingForStart=false;
        Game->LastMessage=bArmorComboProof?TEXT("换装预览：未着甲→轻甲→中甲→重甲→法袍；双向行走与三段连招"):TEXT("换装预览：未着甲→轻甲→中甲→重甲→法袍；行走、待机与首段斩击");
        Go(1);break;
    case 1: // Turn right with ordinary movement, including after a pickup.
        UnitMove(1,0);
        if(Now-UnitPhaseAt>=.75) Go(2);
        break;
    case 2:
        if(Now-UnitPhaseAt>=.35 && Player->Facing>0 && Player->ArmorId==ExpectedArmor && LayersMatch(false))
        {bArmorIdleRight=true;bArmorPrimaryAccepted=false;if(UnitPulse(EKeys::J,Now)) {UnitQueuedStage=1;Go(3);}}
        break;
    case 3:
        if(Now-UnitPhaseAt>=(bArmorComboProof?2.5:.95) && !Player->GetMeleeCombatState().Action.Active)
        {
            if(!bArmorPrimaryAccepted || ArmorPrimaryMask[0]!=63) {Fail(TEXT("right_primary_missing_acceptance_or_six_frames"));return;}
            if(bArmorComboProof && (ArmorComboStageMask[0]!=7 || !bArmorComboContinuous[0]
                || ArmorComboFrameMask[0][0]!=63 || ArmorComboFrameMask[0][1]!=63 || ArmorComboFrameMask[0][2]!=63))
            {Fail(TEXT("right_combo_missing_real_chain_or_six_frames"));return;}
            bArmorPrimaryAccepted=false;Go(4);
        }
        break;
    case 4:
        UnitMove(-1,0);if(Now-UnitPhaseAt>=.75) Go(5);
        break;
    case 5:
        if(Now-UnitPhaseAt>=.35 && Player->Facing<0 && Player->ArmorId==ExpectedArmor && LayersMatch(false))
        {
            if(UnitPulse(EKeys::J,Now))
            {
                Check(FString::Printf(TEXT("armor_%s_idle_both_facings"),Names[ArmorVariant]),bArmorIdleRight&&HUD->GetRenderedPlayerSpriteSize()==160.f);
                Check(FString::Printf(TEXT("armor_%s_walk_both_facings_all6"),Names[ArmorVariant]),ArmorWalkMask[0]==63&&ArmorWalkMask[1]==63);
                UnitQueuedStage=1;
                Go(6);
            }
        }
        break;
    case 6:
        if(Now-UnitPhaseAt>=(bArmorComboProof?2.5:.95) && !Player->GetMeleeCombatState().Action.Active)
        {
            Check(FString::Printf(TEXT("armor_%s_primary1_both_facings_all6"),Names[ArmorVariant]),bArmorPrimaryAccepted&&ArmorPrimaryMask[0]==63&&ArmorPrimaryMask[1]==63);
            if(!bArmorPrimaryAccepted || ArmorPrimaryMask[1]!=63) {Fail(TEXT("left_primary_missing_acceptance_or_six_frames"));return;}
            if(bArmorComboProof)
            {
                for(int32 Stage=1;Stage<3;++Stage)
                    Check(FString::Printf(TEXT("armor_%s_primary%d_both_facings_all6"),Names[ArmorVariant],Stage+1),ArmorComboFrameMask[0][Stage]==63&&ArmorComboFrameMask[1][Stage]==63);
                const bool Continuous=ArmorComboStageMask[0]==7&&ArmorComboStageMask[1]==7&&bArmorComboContinuous[0]&&bArmorComboContinuous[1];
                Check(FString::Printf(TEXT("armor_%s_three_stage_chain_continuous_both_facings"),Names[ArmorVariant]),Continuous);
                if(!Continuous || ArmorComboFrameMask[1][1]!=63 || ArmorComboFrameMask[1][2]!=63)
                {Fail(TEXT("left_combo_missing_real_chain_or_six_frames"));return;}
                if(bArmorSleevesProof && ArmorVariant==4)
                    for(int32 Stage=0;Stage<2;++Stage)
                        Check(FString::Printf(TEXT("armor_ROB_primary%d_near_after_weapon_before_hand_both_facings"),Stage+2),
                            bArmorSleeveOrderValid[0][Stage]&&bArmorSleeveOrderValid[1][Stage]
                            &&ArmorSleeveOrderFrameMask[0][Stage]==63&&ArmorSleeveOrderFrameMask[1][Stage]==63);
            }
            if(ArmorVariant==4) {Go(10);break;}
            ArmorOldId=Player->ArmorId;ArmorOldInstance=V.Slots[2].InstanceId;
            ArmorPickupPosition=Player->GetGroundPosition()+FVector2D(180,0);
            DungeonEquipmentInventory::FItem Item;Item.ContentId=TCHAR_TO_UTF8(Ids[ArmorVariant+1]);
            const auto Source=Game->RegisterEquipmentSource(FString::Printf(TEXT("armor-layer-proof-%d"),ArmorVariant+1),Item,ArmorPickupPosition);
            if(!Source.Ok()) {Fail(TEXT("armor_source_registration_failed"));return;}
            ArmorSourceId=Source.SourceId;ArmorSourceInstance=Source.InstanceId;
            bArmorPickupAccepted=false;bArmorOldHeld=true;bArmorDuration=true;Go(7);
        }
        break;
    case 7:
        if(FMath::Abs(Player->GetGroundPosition().X-ArmorPickupPosition.X)>24.) UnitMove(1,0);
        else
        {
            UnitMove(0,0);
            if(V.SelectedSourceId==ArmorSourceId && UnitPulse(EKeys::E,Now)) Go(8);
        }
        break;
    case 8:
        // An occupied armor slot requires a separate fresh Enter after E.
        // The opening E must never silently confirm replacement.
        if(V.NeedsSlotSelection && V.SelectionSlot==2 && !bUnitEdgeDown && Now-UnitPhaseAt>.2)
        {UnitPulse(EKeys::Enter,Now);}
        else if(V.Action.Active)
        {
            bArmorPickupAccepted=true;bArmorOldHeld&=Player->ArmorId==ArmorOldId&&V.Slots[2].InstanceId==ArmorOldInstance;
            bArmorDuration&=V.Action.Kind==EDungeonEquipmentActionKind::PickupArmor&&FMath::Abs(V.Action.Deadline-V.Action.Start-.5)<1.e-12;
        }
        else if(bArmorPickupAccepted)
        {
            Check(FString::Printf(TEXT("armor_%s_normal_e_050_commit"),Names[ArmorVariant+1]),bArmorOldHeld&&bArmorDuration
                &&Player->ArmorId==Ids[ArmorVariant+1]&&V.Slots[2].InstanceId==ArmorSourceInstance);
            if(Player->ArmorId!=Ids[ArmorVariant+1]) {Fail(TEXT("wrong_armor_commit"));return;}
            ++ArmorVariant;ArmorPrimaryMask[0]=ArmorPrimaryMask[1]=0;ArmorWalkMask[0]=ArmorWalkMask[1]=0;bArmorIdleRight=false;bArmorPrimaryAccepted=false;
            for(int32 Side=0;Side<2;++Side)
            {ArmorComboStageMask[Side]=0;ArmorComboLastId[Side]=0;ArmorComboWeaponInstance[Side]=0;ArmorComboLastEnd[Side]=0;bArmorComboContinuous[Side]=true;for(int32 Stage=0;Stage<3;++Stage) ArmorComboFrameMask[Side][Stage]=0;}
            Go(1);
        }
        break;
    case 10:
        if(Now-UnitPhaseAt>=.6)
        {Check(bArmorComboProof?TEXT("armor_combo_completed_within_55s"):TEXT("armor_layer_completed_within_40s"),Elapsed<Deadline);UnitReleaseInputs();bGameplayFinished=true;FinishAudioCapture();}
        break;
    default: Fail(TEXT("invalid_armor_layer_phase"));break;
    }
}
