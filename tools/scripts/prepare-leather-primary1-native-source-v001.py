from pathlib import Path
import json,hashlib,difflib
R=Path('F:/Ourgame');S=R/'UnrealGame/Source/CodexDungeon';O=R/'source-assets/production/fairytale-lgt-readability-v003/primary1-native-source-v001';assert not O.exists();O.mkdir()
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def sub(s,a,b):assert s.count(a)==1,(a[:80],s.count(a));return s.replace(a,b)
inputs=[];files=[];patch=[]
for n in ['DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleEquipmentBoundProbe.h','DungeonFairytaleEquipmentBoundProbe.cpp']:
 p=S/n;inputs.append(desc(p));old=p.read_text(encoding='utf-8');new=old
 if n=='DungeonFairytaleSwordPresentation.cpp':
  new=sub(new,'    const FString Name=FString::Printf(TEXT("T_Fairytale_SwordPrimary1%s_%03d_v001"),*Component,Frame);','''    const bool LeatherPrimary1=bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary1Preview"))
        &&(Component==TEXT("Chest")||Component==TEXT("ShoulderFar")||Component==TEXT("ShoulderNear"));
    const FString Name=LeatherPrimary1
        ?FString::Printf(TEXT("T_Fairytale_LeatherPrimary1%s_%03d_v001"),*Component,Frame)
        :FString::Printf(TEXT("T_Fairytale_SwordPrimary1%s_%03d_v001"),*Component,Frame);''')
  new=sub(new,'    const FString Package=TEXT("/Game/Production/ArtTrials/EV048/v007/HeroSwordArmorPrimary1/")+Name;','''    const FString Package=FString(LeatherPrimary1?TEXT("/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/")
        :TEXT("/Game/Production/ArtTrials/EV048/v007/HeroSwordArmorPrimary1/"))+Name;''')
 elif n.endswith('.h'):
  new=sub(new,'    int32 LeatherReadyMasks[2]={};','''    int32 LeatherReadyMasks[2]={};
    bool LeatherPrimary1Only=false,LeatherPrimaryTurnRequested=false;
    int32 LeatherPrimary1Masks[2]={};
    uint64 LeatherPrimary1AttackIds[2]={};''')
 else:
  new=sub(new,'    LeatherReadyOnly=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherReadyOnlyProof"));','''    LeatherReadyOnly=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherReadyOnlyProof"));
    LeatherPrimary1Only=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary1OnlyProof"));
    if(LeatherPrimary1Only&&(LeatherReadyOnly
        ||!FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherReadyPreview"))
        ||!FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary1Preview"))))
    {Finish(TEXT("primary1_trial_requires_both_art_flags_and_excludes_ready_only"));return;}''')
  new=sub(new,'    Observations.Add(MakeShared<FJsonValueObject>(R));','''    if(LeatherPrimary1Only&&Step==6&&Light&&D.Supported&&D.Clip==TEXT("sword_primary_1")
        &&D.Stage==0&&D.Frame>=0&&D.Frame<6)
    {
        const int32 Side=D.Facing<0?0:1;
        LeatherPrimary1Masks[Side]|=1<<D.Frame;
        if(!LeatherPrimary1AttackIds[Side])LeatherPrimary1AttackIds[Side]=D.ActionId;
        else if(LeatherPrimary1AttackIds[Side]!=D.ActionId)Mismatch(TEXT("primary1_facing_reuses_multiple_attacks"),Observation);
        int32 NewArmorPaths=0;
        for(const auto& Path:D.DrawStack)if(Path.Contains(TEXT("/EV048/v013/HeroLeatherPrimary1/")))++NewArmorPaths;
        if(NewArmorPaths!=3)Mismatch(TEXT("primary1_requires_three_actual_new_armor_layers"),Observation);
    }
    Observations.Add(MakeShared<FJsonValueObject>(R));''')
  anchor='''        const auto& Action=P->GetMeleeCombatState().Action;
        if(Action.Active)'''
  new=sub(new,anchor,'''        const auto& Action=P->GetMeleeCombatState().Action;
        if(LeatherPrimary1Only)
        {
            if(Action.Active)
            {
                if(Action.WeaponInstanceId!=SwordId||Action.Stage!=0)
                {Finish(TEXT("primary1_trial_must_remain_fresh_stage0"));return;}
            }
            else if(LeatherPrimary1Masks[0]==63&&LeatherPrimary1Masks[1]==63&&ReadySeen[6]>=3)
            {
                if(!LeatherPrimary1AttackIds[0]||!LeatherPrimary1AttackIds[1]
                    ||LeatherPrimary1AttackIds[0]==LeatherPrimary1AttackIds[1])
                {Finish(TEXT("primary1_trial_requires_two_distinct_actual_attack_ids"));return;}
                FlowComplete=true;Next(13);Finish();
            }
            // Existing kernel expires its .45s chain; never reset or forge it.
            else if(G->GetSimulationTime()>=Action.End+.46&&ReadySeen[6]>=3&&CanPulse())
            {
                if(!LeatherPrimaryTurnRequested)
                {Pulse(P->Facing<0?EKeys::D:EKeys::A);LeatherPrimaryTurnRequested=true;}
                else Pulse(EKeys::J);
            }
            break;
        }
        if(Action.Active)''')
  new=sub(new,'    Report->SetBoolField(TEXT("leather_ready_only_trial"),LeatherReadyOnly);','''    Report->SetBoolField(TEXT("leather_ready_only_trial"),LeatherReadyOnly);
    Report->SetBoolField(TEXT("leather_primary1_only_trial"),LeatherPrimary1Only);
    TArray<TSharedPtr<FJsonValue>> Primary1Masks,Primary1Ids;
    for(int32 Mask:LeatherPrimary1Masks)Primary1Masks.Add(MakeShared<FJsonValueNumber>(Mask));
    for(uint64 Id:LeatherPrimary1AttackIds)Primary1Ids.Add(MakeShared<FJsonValueString>(FString::Printf(TEXT("%llu"),(unsigned long long)Id)));
    Report->SetArrayField(TEXT("leather_primary1_masks_left_right"),Primary1Masks);
    Report->SetArrayField(TEXT("leather_primary1_attack_ids_left_right"),Primary1Ids);''')
  new=sub(new,'    Report->SetArrayField(TEXT("observations"),Observations);','''    if(LeatherPrimary1Only)Report->SetStringField(TEXT("scope"),TEXT("Opt-in new leather Primary1 trial only: same real light commit and weapon instance, two fresh normal J attacks with existing .45s combo expiry and normal direction input; six phases each facing, then actual Ready. No forced pose/frame/clock/gear, no Primary2/3 acceptance, no full locomotion/equip/hurt/death/audio/Save or full unit acceptance."));
    Report->SetArrayField(TEXT("observations"),Observations);''')
 q=O/n;q.write_text(new,encoding='utf-8',newline='\n');files.append(desc(q));rel='UnrealGame/Source/CodexDungeon/'+n
 patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
p=O/'primary1-trial-v001.patch';p.write_text(''.join(patch),encoding='utf-8',newline='\n');files.append(desc(p))
(O/'source-freeze-v001.json').write_text(json.dumps(dict(schema='leather-primary1-source-candidate-v001',inputs=inputs,files=files,actual_source_written=False,compiled=False,native_trial_run=False,art_assets_not_yet_generated=True,default_flow_unchanged=True,actual_chain_expiry_preserved=True,full_unit_complete=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(candidate=O.as_posix(),actual_source_written=False,art_inputs_required=True)))
