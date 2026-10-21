from pathlib import Path
import hashlib,json,difflib
R=Path('F:/Ourgame');S=R/'UnrealGame/Source/CodexDungeon'
O=R/'source-assets/production/fairytale-lgt-readability-v003/ready-native-source-v001';assert not O.exists();O.mkdir()
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def replace(s,a,b):
 assert s.count(a)==1,(a[:100],s.count(a));return s.replace(a,b)
inputs=[];outputs=[];patches=[]
for name in ['DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleEquipmentBoundProbe.h','DungeonFairytaleEquipmentBoundProbe.cpp']:
 p=S/name;inputs.append(desc(p));old=p.read_text(encoding='utf-8');new=old
 if name=='DungeonFairytaleSwordPresentation.cpp':
  new=replace(new,'    const FString Name=FString::Printf(TEXT("T_Fairytale_SwordReady%s_%03d_v001"),*Component,Frame);','''    const bool LeatherReady=bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherReadyPreview"))
        &&(Component==TEXT("Chest")||Component==TEXT("ShoulderFar")||Component==TEXT("ShoulderNear"));
    const FString Name=FString::Printf(LeatherReady?TEXT("T_Fairytale_LeatherReady%s_%03d_v001")
        :TEXT("T_Fairytale_SwordReady%s_%03d_v001"),*Component,Frame);''')
  new=replace(new,'    const FString Package=TEXT("/Game/Production/ArtTrials/EV048/v006/HeroSwordArmorReady/")+Name;','''    const FString Package=FString(LeatherReady?TEXT("/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/")
        :TEXT("/Game/Production/ArtTrials/EV048/v006/HeroSwordArmorReady/"))+Name;''')
 elif name.endswith('.h'):
  new=replace(new,'    bool Prewarm=false,Started=false,Stopped=false,FlowComplete=false;','''    bool Prewarm=false,Started=false,Stopped=false,FlowComplete=false;
    bool LeatherReadyOnly=false,LeatherTurnRequested=false;
    int32 LeatherReadyMasks[2]={};''')
 else:
  new=replace(new,'    Super::BeginPlay();GIsDumpingMovie=0;WarmStart=FPlatformTime::Seconds();','''    Super::BeginPlay();GIsDumpingMovie=0;WarmStart=FPlatformTime::Seconds();
    LeatherReadyOnly=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherReadyOnlyProof"));
    if(LeatherReadyOnly&&!FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherReadyPreview")))
    {Finish(TEXT("leather_ready_only_requires_explicit_leather_art_flag"));return;}''')
  new=replace(new,'    Observations.Add(MakeShared<FJsonValueObject>(R));','''    if(LeatherReadyOnly&&Step==5&&Light&&D.Supported&&D.Clip==TEXT("sword_ready_idle")
        &&!V.Action.Active&&P->AnimationName==TEXT("idle")&&D.Frame>=0&&D.Frame<4)
    {
        LeatherReadyMasks[D.Facing<0?0:1]|=1<<D.Frame;
        int32 NewArmorPaths=0;
        for(const auto& Path:D.DrawStack)if(Path.Contains(TEXT("/EV048/v012/HeroLeatherReady/")))++NewArmorPaths;
        if(NewArmorPaths!=3)Mismatch(TEXT("leather_ready_requires_three_actual_new_armor_layers"),Observation);
    }
    Observations.Add(MakeShared<FJsonValueObject>(R));''')
  new=replace(new,'    case 5:\n        if(ReadySeen[5]>=3&&CanPulse()){Pulse(EKeys::J);Next(6);}break;','''    case 5:
        if(LeatherReadyOnly)
        {
            if(LeatherReadyMasks[0]==15&&LeatherReadyMasks[1]==15)
            {FlowComplete=true;Next(13);Finish();}
            else if(!LeatherTurnRequested&&LeatherReadyMasks[P->Facing<0?0:1]==15&&CanPulse())
            {Pulse(P->Facing<0?EKeys::D:EKeys::A);LeatherTurnRequested=true;}
        }
        else if(ReadySeen[5]>=3&&CanPulse()){Pulse(EKeys::J);Next(6);}break;''')
  new=replace(new,'for(const FKey Code:{EKeys::Enter,EKeys::E,EKeys::A,EKeys::J})','for(const FKey Code:{EKeys::Enter,EKeys::E,EKeys::A,EKeys::D,EKeys::J})')
  new=replace(new,'    Report->SetArrayField(TEXT("observations"),Observations);','''    Report->SetBoolField(TEXT("leather_ready_only_trial"),LeatherReadyOnly);
    TArray<TSharedPtr<FJsonValue>> LeatherMasks;
    for(int32 Mask:LeatherReadyMasks)LeatherMasks.Add(MakeShared<FJsonValueNumber>(Mask));
    Report->SetArrayField(TEXT("leather_ready_phase_masks_left_right"),LeatherMasks);
    if(LeatherReadyOnly)Report->SetStringField(TEXT("scope"),TEXT("Opt-in leather Ready4 fit trial only: genuine normal Enter/E/A cancel and E light-armor commit from QA registered source, then normal direction input and all4idle phases both facings; same actual committed light instance. New3armor layers only. No attack, full equip/walk/hurt/death, loot/shop/reward/save or audio acceptance. Default complete bound proof remains separate."));
    Report->SetArrayField(TEXT("observations"),Observations);''')
 q=O/name;q.write_text(new,encoding='utf-8',newline='\n');outputs.append(desc(q))
 rel='UnrealGame/Source/CodexDungeon/'+name
 patches.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
patch=O/'ready-trial-v001.patch';patch.write_text(''.join(patches),encoding='utf-8',newline='\n')
freeze=dict(schema='leather-ready-opt-in-source-candidate-v001',inputs=inputs,files=outputs+[desc(patch)],actual_source_written=False,native_build_run=False,native_trial_run=False,default_flow_unchanged=True,new_armor_namespace='/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady',ready_only_complete_animation_acceptance=False,formal_complete_units=0)
(O/'source-freeze-v001.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(candidate=O.as_posix(),files=len(outputs),actual_source_written=False)))
