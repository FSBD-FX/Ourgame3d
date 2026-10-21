"""Prepare an unapplied optional leather two-facing combo source candidate."""
from pathlib import Path
import ast, datetime, difflib, hashlib, json, shutil
ROOT=Path('F:/Ourgame')
OUT=Path(__file__).resolve().parent
SOURCE=ROOT/'UnrealGame/Source/CodexDungeon'
FAMILY=ROOT/'source-assets/production/fairytale-lgt-readability-v003'
WATCH={}
def desc(p,watch=True):
 b=p.read_bytes();r={'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
 if watch and not p.is_relative_to(OUT):WATCH[p]=r
 return r
def write(name,data):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as s:s.write(data if isinstance(data,str) else json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 return p
def sub(s,a,b):
 if s.count(a)!=1:raise RuntimeError('Expected one source match: '+a[:100])
 return s.replace(a,b)

def renderer(s):
 s=sub(s,'?DungeonFairytaleSwordPrimary3V001::GetTexture(PrimaryComponents[I],Record.Frame,Frames)',
 '''?DungeonFairytaleSwordPrimary3V001::GetTexture(PrimaryComponents[I],Record.Frame,Frames,
                    BoundLightArmor&&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary3Preview")))''')
 s=sub(s,'?DungeonFairytaleSwordPrimary2ArmorV001::GetTexture(PrimaryComponents[I],Record.Frame,Frames)',
 '''?DungeonFairytaleSwordPrimary2ArmorV001::GetTexture(PrimaryComponents[I],Record.Frame,Frames,
                    BoundLightArmor&&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary2Preview")))''')
 return s

def texture_resolver(s,stage,old_namespace,new_version):
 s=sub(s,'TMap<FString,TObjectPtr<UTexture2D>>& Cache)', 'TMap<FString,TObjectPtr<UTexture2D>>& Cache,bool UseLeather=false)')
 old=f'    const FString Name=FString::Printf(TEXT("T_Fairytale_SwordPrimary{stage}%s_%03d_v001"),*Component,Frame);'
 new=f'''    // Only the renderer's successful committed Bound LGT authorizes this opt-in.
    // Original four body layers (and whole Body) keep their existing package/name.
    const bool LeatherComponent=UseLeather&&(Component==TEXT("Chest")
        ||Component==TEXT("ShoulderNear")||Component==TEXT("ShoulderFar"));
    const FString Name=LeatherComponent
        ?FString::Printf(TEXT("T_Fairytale_LeatherPrimary{stage}%s_%03d_v001"),*Component,Frame)
        :FString::Printf(TEXT("T_Fairytale_SwordPrimary{stage}%s_%03d_v001"),*Component,Frame);'''
 s=sub(s,old,new)
 s=sub(s,f'    const FString Package=TEXT("{old_namespace}/")+Name;',
 f'''    const FString Package=FString(LeatherComponent
        ?TEXT("/Game/Production/ArtTrials/EV048/v{new_version:03d}/HeroLeatherPrimary{stage}/")
        :TEXT("{old_namespace}/"))+Name;''')
 return s

def probe_header(s):
 return sub(s,'    FKey PulseKey;TMap<FKey,bool> Keys;', '''    bool LeatherComboOnly=false,LeatherComboTurnRequested=false,LeatherComboSecondRequested=false;
    int32 LeatherComboFirstSide=-1,LeatherComboMasks[2][3]={},LeatherComboReadySeen[2]={};
    uint64 LeatherComboAttackIds[2][3]={};
    FKey PulseKey;TMap<FKey,bool> Keys;''')

def probe_cpp(s):
 s=sub(s,'    if(LeatherPrimary1Only&&(LeatherReadyOnly', '''    LeatherComboOnly=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherComboOnlyProof"));
    if(LeatherComboOnly&&(LeatherReadyOnly||LeatherPrimary1Only||FApp::UseFixedTimeStep()
        ||!FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherReadyPreview"))
        ||!FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary1Preview"))
        ||!FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary2Preview"))
        ||!FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary3Preview"))))
    {Finish(TEXT("leather_combo_requires_four_explicit_art_flags_nonfixed_clock_and_excludes_other_only_modes"));return;}
    if(LeatherPrimary1Only&&(LeatherReadyOnly''')
 s=sub(s,'    Observations.Add(MakeShared<FJsonValueObject>(R));', '''    if(LeatherComboOnly&&Light&&D.Supported)
    {
        if(!D.EquipmentBoundMode||!D.EquipmentBindingValid
            ||D.EquipmentBinding.Armor!=DungeonFairytaleSwordEquipmentBinding::EArmor::LightArmor
            ||D.EquipmentBinding.ArmorInstanceId!=LightId)
            Mismatch(TEXT("leather_combo_not_actual_committed_LGT_binding"),Observation);
        const bool Idle=D.Clip==TEXT("sword_ready_idle");
        const int32 Stage=Idle?-1:D.Stage;
        const int32 Side=D.Facing<0?0:1;
        const bool ValidFrame=Idle?(D.Frame>=0&&D.Frame<4):(Stage>=0&&Stage<3&&D.Frame>=0&&D.Frame<6);
        if(!ValidFrame)Mismatch(TEXT("leather_combo_invalid_clip_frame_or_stage"),Observation);
        else
        {
            const FString OldNamespace=Idle?TEXT("/Game/Production/ArtTrials/EV048/v006/HeroSwordArmorReady/")
                :Stage==0?TEXT("/Game/Production/ArtTrials/EV048/v007/HeroSwordArmorPrimary1/")
                :Stage==1?TEXT("/Game/Production/ArtTrials/EV048/v010/HeroSwordPrimary2Armor/")
                :TEXT("/Game/Production/ArtTrials/EV048/v011/HeroSwordPrimary3/");
            const FString NewNamespace=Idle?TEXT("/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/")
                :Stage==0?TEXT("/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/")
                :Stage==1?TEXT("/Game/Production/ArtTrials/EV048/v014/HeroLeatherPrimary2/")
                :TEXT("/Game/Production/ArtTrials/EV048/v015/HeroLeatherPrimary3/");
            const FString OldPrefix=Idle?TEXT("T_Fairytale_SwordReady")
                :FString::Printf(TEXT("T_Fairytale_SwordPrimary%d"),Stage+1);
            const FString NewPrefix=Idle?TEXT("T_Fairytale_LeatherReady")
                :FString::Printf(TEXT("T_Fairytale_LeatherPrimary%d"),Stage+1);
            TArray<FString> Expected;
            for(const TCHAR* Component:{TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),
                TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT("NearHand")})
            {
                if(Idle&&FCString::Strcmp(Component,TEXT("HelmetForeground"))==0)continue;
                if(FCString::Strcmp(Component,TEXT("NearHand"))==0)Expected.Add(D.WeaponPath);
                const bool Armor=FCString::Strcmp(Component,TEXT("Chest"))==0
                    ||FCString::Strcmp(Component,TEXT("ShoulderFar"))==0||FCString::Strcmp(Component,TEXT("ShoulderNear"))==0;
                const FString Name=FString::Printf(TEXT("%s%s_%03d_v001"),*(Armor?NewPrefix:OldPrefix),Component,D.Frame);
                Expected.Add((Armor?NewNamespace:OldNamespace)+Name+TEXT(".")+Name);
            }
            if(D.DrawStack!=Expected)Mismatch(TEXT("leather_combo_exact_three_new_armor_old_body_stack_mismatch"),Observation);
            if(Step==6&&!Idle)
            {
                const auto& A=ActualMelee.Action;
                const FString ExpectedClip=FString::Printf(TEXT("sword_primary_%d"),Stage+1);
                const bool Actual=A.Active&&A.AttackId&&D.ActionId==A.AttackId
                    &&D.InstanceId==SwordId&&A.WeaponInstanceId==SwordId
                    &&int32(A.Stage)==Stage&&D.Clip==ExpectedClip&&!A.StartedAirborne
                    &&(D.Facing==-1||D.Facing==1)&&A.Facing==D.Facing
                    &&D.Frame==P->GetPrimaryPoseFrame();
                if(!Actual)Mismatch(TEXT("leather_combo_draw_not_corroborated_by_actual_attack_owner"),Observation);
                else
                {
                    if(LeatherComboFirstSide<0)
                    {
                        if(Stage!=0)Mismatch(TEXT("leather_combo_first_observed_stage_not_zero"),Observation);
                        else LeatherComboFirstSide=Side;
                    }
                    const int32 ExpectedSide=LeatherComboTurnRequested?1-LeatherComboFirstSide:LeatherComboFirstSide;
                    if(Side!=ExpectedSide)Mismatch(TEXT("leather_combo_action_changed_facing_inside_sequence"),Observation);
                    uint64& Id=LeatherComboAttackIds[Side][Stage];
                    if(!Id)
                    {
                        Id=A.AttackId;
                        // Discard pre-input Ready at the FIRST OBSERVED actual new attack,
                        // including second-sequence requests not yet processed by native input.
                        LeatherComboReadySeen[Side]=0;
                        if(Stage>0&&(!LeatherComboAttackIds[Side][Stage-1]
                            ||Id<=LeatherComboAttackIds[Side][Stage-1]))
                            Mismatch(TEXT("leather_combo_stage_order_or_actual_attack_id_not_fresh"),Observation);
                    }
                    else if(Id!=A.AttackId)Mismatch(TEXT("leather_combo_multiple_actual_attacks_for_same_side_stage"),Observation);
                    if(Side==ExpectedSide&&Id==A.AttackId
                        &&(Stage==0||LeatherComboAttackIds[Side][Stage-1]!=0))
                        LeatherComboMasks[Side][Stage]|=1<<D.Frame;
                }
            }
            if(Step==6&&Idle&&!ActualMelee.Action.Active&&!ActualMelee.PendingPrimary
                &&!V.Action.Active&&!V.NeedsSlotSelection&&P->AnimationName==TEXT("idle")&&(D.Facing==-1||D.Facing==1)
                &&LeatherComboFirstSide>=0
                &&Side==(LeatherComboTurnRequested?1-LeatherComboFirstSide:LeatherComboFirstSide))
            {
                bool Complete=LeatherComboAttackIds[Side][2]!=0;
                for(int32 Index=0;Index<3;++Index)Complete&=LeatherComboMasks[Side][Index]==63;
                if(Complete)++LeatherComboReadySeen[Side];
            }
            R->SetNumberField(TEXT("leather_combo_side"),Side);
            R->SetNumberField(TEXT("leather_combo_fresh_ready_seen_this_side"),LeatherComboReadySeen[Side]);
        }
    }
    Observations.Add(MakeShared<FJsonValueObject>(R));''')
 s=sub(s,'    if(Wall-CaptureStart>30.||Wall-StepStart>5.)',
       '    if(Wall-CaptureStart>30.||Wall-StepStart>(LeatherComboOnly&&Step==6?12.:5.))')
 s=sub(s,'        if(LeatherPrimary1Only)\n        {\n            if(Action.Active)', '''        if(LeatherComboOnly)
        {
            const auto& Melee=P->GetMeleeCombatState();
            if(Action.Active)
            {
                if(Action.WeaponInstanceId!=SwordId||Action.Stage>=3)
                {Finish(TEXT("leather_combo_actual_attack_owner_or_stage_wrong"));return;}
                if(Action.Stage<2&&Action.AttackId!=QueuedAttack
                    &&G->GetSimulationTime()>=Action.ActiveEnd
                    &&G->GetSimulationTime()>=Action.End-.10&&CanPulse())
                {if(Pulse(EKeys::J))QueuedAttack=Action.AttackId;}
            }
            else if(LeatherComboFirstSide>=0)
            {
                const int32 First=LeatherComboFirstSide,Second=1-First;
                const auto Complete=[&](int32 Side)
                {
                    bool Ok=LeatherComboReadySeen[Side]>=3;
                    for(int32 Stage=0;Stage<3;++Stage)Ok&=LeatherComboMasks[Side][Stage]==63&&LeatherComboAttackIds[Side][Stage]!=0;
                    return Ok;
                };
                if(LeatherComboSecondRequested&&Complete(First)&&Complete(Second))
                {
                    TSet<uint64> ActualIds;
                    for(int32 Side=0;Side<2;++Side)for(int32 Stage=0;Stage<3;++Stage)ActualIds.Add(LeatherComboAttackIds[Side][Stage]);
                    if(ActualIds.Num()!=6||V.NextOperationId!=InitialOperation+1
                        ||Inventory->Operations.size()!=InitialOperationCount+1||Inventory->Armor!=LightId)
                    {Finish(TEXT("leather_combo_requires_six_unique_actual_ids_and_same_single_light_commit"));return;}
                    FlowComplete=true;Next(13);Finish();
                }
                else if(Complete(First)&&!Melee.ComboReady&&!Melee.PendingPrimary
                    &&G->GetSimulationTime()>=Action.End+.46&&CanPulse())
                {
                    if(!LeatherComboTurnRequested)
                    {
                        if(Pulse(Second==0?EKeys::A:EKeys::D))LeatherComboTurnRequested=true;
                    }
                    else if(!LeatherComboSecondRequested&&(P->Facing<0?0:1)==Second)
                    {
                        if(Pulse(EKeys::J)){LeatherComboSecondRequested=true;LeatherComboReadySeen[Second]=0;}
                    }
                }
            }
            break;
        }
        if(LeatherPrimary1Only)
        {
            if(Action.Active)''')
 s=sub(s,'    Report->SetBoolField(TEXT("leather_ready_only_trial"),LeatherReadyOnly);', '''    Report->SetBoolField(TEXT("leather_combo_only_trial"),LeatherComboOnly);
    TArray<TSharedPtr<FJsonValue>> ComboMasks,ComboIds,ComboReady;
    for(int32 Side=0;Side<2;++Side)
    {
        TArray<TSharedPtr<FJsonValue>> MasksForSide,IdsForSide;
        for(int32 Stage=0;Stage<3;++Stage)
        {
            MasksForSide.Add(MakeShared<FJsonValueNumber>(LeatherComboMasks[Side][Stage]));
            IdsForSide.Add(MakeShared<FJsonValueString>(FString::Printf(TEXT("%llu"),(unsigned long long)LeatherComboAttackIds[Side][Stage])));
        }
        ComboMasks.Add(MakeShared<FJsonValueArray>(MasksForSide));ComboIds.Add(MakeShared<FJsonValueArray>(IdsForSide));
        ComboReady.Add(MakeShared<FJsonValueNumber>(LeatherComboReadySeen[Side]));
    }
    Report->SetArrayField(TEXT("leather_combo_masks_left_right_by_stage"),ComboMasks);
    Report->SetArrayField(TEXT("leather_combo_attack_ids_left_right_by_stage"),ComboIds);
    Report->SetArrayField(TEXT("leather_combo_fresh_ready_seen_left_right"),ComboReady);
    Report->SetNumberField(TEXT("leather_combo_first_side"),LeatherComboFirstSide);
    Report->SetBoolField(TEXT("leather_combo_normal_turn_requested"),LeatherComboTurnRequested);
    Report->SetBoolField(TEXT("leather_combo_second_sequence_normal_J_requested"),LeatherComboSecondRequested);
    Report->SetBoolField(TEXT("leather_ready_only_trial"),LeatherReadyOnly);''')
 s=sub(s,'    Report->SetArrayField(TEXT("observations"),Observations);', '''    if(LeatherComboOnly)Report->SetStringField(TEXT("scope"),TEXT("Opt-in soft-leather combo-only trial: normal Enter/E/A cancel/E single actual LGT commit, normal J three-stage chain, actual post-chain Ready, native chain expiry, normal opposite direction, second fresh normal J three-stage chain and final actual Ready. Six actual distinct attack IDs, each facing/stage mask63; original body layers plus matching new3 armor per clip. No forced pose/frame/clock/gear or invented phase counters. QA registered source is not lawful loot/shop/reward. No full unit, all actions, armor compatibility, complete equip animation, grasp/clearance, audio or Save acceptance. Default proof remains separate."));
    Report->SetArrayField(TEXT("observations"),Observations);''')
 return s


def main():
 if OUT!=FAMILY/'leather-combo-source-v001' or (OUT/'source-freeze-v001.json').exists():raise RuntimeError('Unexpected/existing candidate')
 modifiers={'DungeonFairytaleSwordPresentation.cpp':renderer,
   'DungeonFairytaleSwordPrimary2ArmorV001.inl':lambda s:texture_resolver(s,2,'/Game/Production/ArtTrials/EV048/v010/HeroSwordPrimary2Armor',14),
   'DungeonFairytaleSwordPrimary3V001.inl':lambda s:texture_resolver(s,3,'/Game/Production/ArtTrials/EV048/v011/HeroSwordPrimary3',15),
   'DungeonFairytaleEquipmentBoundProbe.h':probe_header,'DungeonFairytaleEquipmentBoundProbe.cpp':probe_cpp}
 inputs=[];candidate_files=[];patch=[]
 for name,modify in modifiers.items():
  original=SOURCE/name;inputs.append(desc(original));old=original.read_text('utf-8-sig');new=modify(old)
  if old==new:raise RuntimeError('No source change')
  before=OUT/'current-source-originals'/name;before.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,before)
  if before.read_bytes()!=original.read_bytes():raise RuntimeError('Original byte copy changed')
  candidate=write(name,new);candidate_files.append(desc(candidate))
  rel='UnrealGame/Source/CodexDungeon/'+name
  patch.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
 body_evidence=[]
 for stage in [2,3]:
  mapping_path=FAMILY/f'primary{stage}-leather-input-v001/actual-runtime-source-version-mapping-v001.json'
  mapping=json.loads(mapping_path.read_text('utf-8-sig'));desc(mapping_path)
  for body in mapping['body_frames']:
   for entry in [body['actual_canonical_body']]+[b['current_imported_source'] for b in body['existing_runtime_four_layers_to_keep']]:
    if desc(Path(entry['path']))!=entry:raise RuntimeError('Current body source pin differs from verified mapping')
  body_evidence.append({'stage':stage,'mapping':desc(mapping_path),'actual_body_native_request':mapping['body_native_request'],'canonical_run':mapping['body_run_version'],
      'body_texture_namespace':mapping['armor_and_four_body_layer_namespace'],'whole_body_namespace':mapping['full_body_namespace'],
      'body_layers_remain_the_existing_imported_24_PNGs':True,'old_body_pixels_or_marker_modified':False})
 contract=write('combo-contract-v001.json',{'schema':'leather-two-facing-three-stage-combo-source-contract-v001','created_local':datetime.datetime.now().astimezone().isoformat(),
   'base_current_source':'Root v125 actual source; exact hashes in inputs, no inferred checkpoint state','inputs':inputs,
   'body_source_versions':body_evidence,'new_optional_art_flags':['DungeonFairytaleLeatherPrimary2Preview','DungeonFairytaleLeatherPrimary3Preview'],
   'new_proof_flag':'DungeonFairytaleLeatherComboOnlyProof','required_art_flags':['DungeonFairytaleLeatherReadyPreview','DungeonFairytaleLeatherPrimary1Preview','DungeonFairytaleLeatherPrimary2Preview','DungeonFairytaleLeatherPrimary3Preview'],
   'required_actual_Bound_renderer_flag':'DungeonFairytaleSwordEquipmentBoundPreview','renderer_new_armor_gate':'Already successfully resolved committed BoundLightArmor AND explicit per-stage leather flag; only Chest/ShoulderNear/ShoulderFar. All other components use old namespaces.',
   'new_namespaces':{'Primary2':'/Game/Production/ArtTrials/EV048/v014/HeroLeatherPrimary2','Primary3':'/Game/Production/ArtTrials/EV048/v015/HeroLeatherPrimary3'},
   'name_patterns':{'Primary2':'T_Fairytale_LeatherPrimary2{Chest|ShoulderNear|ShoulderFar}_{frame:03d}_v001','Primary3':'T_Fairytale_LeatherPrimary3{Chest|ShoulderNear|ShoulderFar}_{frame:03d}_v001'},
   'phase_durations_ms':{'Primary1':[85,85,60,60,155,155],'Primary2':[75,75,60,60,135,135],'Primary3':[110,110,60,60,160,160]},
   'normal_inputs':'Existing Enter/E/A movement cancel/E one LGT commit; J plus 2 native recovery-window buffered J requests, actual Ready>=3 and expired .45s chain, normal opposite A/D, then same J3 and final actual Ready>=3.',
   'observation_masks':'Independent [left,right][stage0,1,2], each63; OR bits only from real screenshot observed Frame corroborated by active native melee action/Stage/Clip/WeaponInstanceId/AttackId.',
   'attack_ids':'Six nonzero globally distinct actual native AttackIds, one per facing/stage and increasing by stage; recorded only on actual screenshot observation, not when J is requested.',
   'fresh_Ready_rule':'Clear side Ready on first observation of every new actual attack; count only inactive native melee + no pending primary/action/selection + idle and all three actual side masks63. Second J request also clears its side counter; request is not action proof.',
   'finish_rule':'Both sides all3mask63, freshReady>=3 per side, six actual unique IDs, same Sword/Light/run/owner, exactly one actual equipment operation. FinalReady cannot come from between J request and actual processing.',
   'default_mode_preserved':True,'other_only_modes_mutually_exclusive':True,'case6_wall_timeout_s_if_combo':12,'other_case_wall_timeout_s':5,'whole_capture_wall_timeout_s':30,
   'fixed_clock_or_gameplay_timing_changed':False,'forced_pose_frame_gear_or_counter_fakes':False,'Source_or_tools_applied':False,'compiled':False,'native_run':False,
   'new_art_assets_and_fit_review_required_before_admission':True,'source_patch_is_not_build_or_runtime_proof':True,'first_observed_attack_facing_and_grounded_corroborated':True,'full_unit_or_all_actions_accepted':False})
 patch_path=write('leather-combo-trial-v001.patch',''.join(patch))
 write('HANDOFF.md','''# Soft leather combo source candidate

Unapplied optional renderer/probe patch against the exact current v125 source hashes. P2/P3 flags replace only three armor components after actual Bound LGT resolution; whole body and four imported body layers retain existing v009/v010 and v011 sources. Current default flags and existing ReadyOnly/Primary1Only/default flow remain unchanged.

New ComboOnly uses the existing normal source/pickup/cancel/commit flow, normal J recovery-window requests, six actual screenshot-corroborated AttackIds and independent left/right × three-stage six-bit masks. It waits for native chain expiry before normal turn and the second chain. Fresh Ready is reset at every first observed new actual attack and counted only after that side has all three complete actual masks. Scope is combo only, no full unit/action/audio/Save acceptance.

Root must wait for all new P2/P3 art extraction, actual A/B, curated/export provenance, integer fit review/import and source review before applying/building. No ActualSource, tools, UE, imports, status, media or ledger were written here; no native run or compilation is claimed. Candidate source/patch/contract are frozen; original byte copies are retained.
''')
 mismatch=[str(p) for p,before in WATCH.items() if desc(p,False)!=before]
 if mismatch:raise RuntimeError('Current read-only source changed: '+str(mismatch))
 files=[desc(p,False) for p in sorted(OUT.rglob('*')) if p.is_file()]
 freeze=write('source-freeze-v001.json',{'schema':'leather-combo-unapplied-source-candidate-freeze-v001','inputs':inputs,'files':files,'contract':desc(contract),'patch':desc(patch_path),
    'current_body_source_rechecks':len(WATCH),'source_mismatches':[],'actual_source_written':False,'tools_written':False,'compiled':False,'native_run':False,'imported':False,'new_art_fit_unaccepted':True,'default_flags_unchanged':True,'full_unit_complete':False})
 print(json.dumps({'candidate':OUT.as_posix(),'source_freeze':desc(freeze),'contract':desc(contract),'patch':desc(patch_path),'candidate_source_count':len(candidate_files),'read_only_rechecks':len(WATCH),'source_mismatches':[],'compiled':False,'native_run':False},indent=2))

if __name__=='__main__':main()
