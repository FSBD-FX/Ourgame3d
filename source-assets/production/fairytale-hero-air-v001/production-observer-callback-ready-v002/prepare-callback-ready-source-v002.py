"""Create a NEW observer-only completed-Ready callback handoff candidate."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import difflib

ROOT=Path('F:/Ourgame')
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'production-observer-candidate-v001'
SOURCE_FREEZE=OLD/'HeroAir-production-observer-source-freeze-v001.json'
SOURCE_SHA='e7b9f44fe53fa2c827d962b359494badf2efbf1ffb8d2e2face8dd2449fa6140'


def pin(p):
    p=Path(p).resolve();b=p.read_bytes()
    return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())


def write_new(p,b):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(b)


def jwrite(p,x):write_new(p,(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8'))


def replace_once(s,a,b):
    if s.count(a)!=1:raise ValueError('Expected unique source seam absent: '+a[:80])
    return s.replace(a,b,1)


def main():
    if pin(SOURCE_FREEZE)['sha256']!=SOURCE_SHA:raise ValueError('Original source freeze changed')
    old=json.loads(SOURCE_FREEZE.read_text(encoding='utf-8-sig'))
    before=[]
    for row in old['source_files']:
        if pin(row['path'])!=row:raise ValueError('Original frozen source changed')
        name=Path(row['path']).name;actual=ROOT/'UnrealGame/Source/CodexDungeon'/name
        current=pin(actual)
        if (current['bytes'],current['sha256'])!=(row['bytes'],row['sha256']):raise ValueError('Actual observer Source296 differs from frozen original')
        before.append(current)
        write_new(HERE/'before-source'/name,Path(row['path']).read_bytes())
        if name!='DungeonHeroAirProductionProbeV001.cpp':
            write_new(HERE/'new-source'/name,Path(row['path']).read_bytes())
    source=(HERE/'before-source/DungeonHeroAirProductionProbeV001.cpp').read_bytes().decode('utf-8')
    newline='\r\n' if '\r\n' in source else '\n'
    if newline=='\r\n':source=source.replace('\r\n','\n')
    original=source
    source=replace_once(source,' TArray<JV> Inputs,Steps,Observations,Offsets,DiagnosticHits,StartupTextures;',
''' // This token is created only by an actual completed screenshot callback.
 bool LightReadyCallbackObserved=false,LightReadyCallbackConsumed=false;
 int32 LightReadyObservationIndex=INDEX_NONE;
 uint64 LightReadyDrawId=0;
 double LightReadyCallbackSim=-1.,LightReadyCallbackWall=-1.;
 JO LightReadyCallback;
 TArray<JV> Inputs,Steps,Observations,Offsets,DiagnosticHits,StartupTextures;''')
    source=replace_once(source,'  auto P=Game.IsValid()?Game->PlayerFighter.Get():nullptr;auto O=MakeShared<FJsonObject>();',
'''  auto P=Game.IsValid()?Game->PlayerFighter.Get():nullptr;auto O=MakeShared<FJsonObject>();
  if(Game.IsValid())
  {
   const auto& InputView=Game->GetEquipmentView();
   O->SetBoolField(TEXT("context_sampled_before_InputKey"),true);
   O->SetStringField(TEXT("run"),InputView.RunGuid.ToString(EGuidFormats::Digits));Id(O,TEXT("owner"),InputView.OwnerId);
   Id(O,TEXT("current_room"),InputView.RoomInstanceId);Id(O,TEXT("epoch"),Game->GetRunPresentationEpoch());
   Id(O,TEXT("player_entity"),P?P->GetRuntimeEntityId():0);
   if(InputView.ActiveSlot>=0&&InputView.ActiveSlot<3)
   {Id(O,TEXT("weapon_instance"),InputView.Slots[InputView.ActiveSlot].InstanceId);Id(O,TEXT("weapon_version"),InputView.Slots[InputView.ActiveSlot].Version);}
   Id(O,TEXT("armor_instance"),InputView.Slots[2].InstanceId);Id(O,TEXT("armor_version"),InputView.Slots[2].Version);
   O->SetNumberField(TEXT("observed_air_transition_ordinal_before"),AirTransitions);
   O->SetNumberField(TEXT("space_enqueue_observer_ordinal"),Down&&K==EKeys::SpaceBar?JumpInputs+1:0);
   O->SetBoolField(TEXT("space_enqueue_ordinal_is_gameplay_jump_id"),false);
  }''')
    source=replace_once(source,'  if(GearPinned&&!PinGear(P)){BeginStop(Actor);return;}\n  if(Pose>=0)',
'''  if(GearPinned&&!PinGear(P)){BeginStop(Actor);return;}
  // HUD.Tick prerequisites do not wait for DrawHUD. Wait for its real completed
  // callback instead of reading the prior equipment-change placeholder in Tick.
  if(Phase==5&&!LightReadyCallbackObserved&&GearPinned&&!V.Action.Active&&V.Slots[2].InstanceId==Light)
  {
   const auto& ReadyBinding=B.EquipmentBinding;
   const bool CompletedReady=B.Active&&B.Supported&&B.ArmorDrawn&&SwordDrawn(B)&&P->Facing==float(Side)
    &&B.ActionPoseSupported&&B.TextureReady&&!B.GearPlaceholder&&B.Clip==TEXT("sword_ready_idle")
    &&B.SimulationTime==G->GetSimulationTime()&&B.DrawId>LastNewDraw&&B.Facing==Side&&!A.Drawn
    &&P->JumpHeight==0.f&&P->GetVerticalVelocity()==0.f&&P->GetLandingVisualAge()==.12f
    &&B.DrawStack.Num()>0&&B.DrawStack==H->GetRenderedPlayerDrawStack()
    &&B.EquipmentBoundMode&&B.EquipmentBindingValid&&ReadyBinding.RunGuid==Run&&ReadyBinding.OwnerId==Owner
    &&ReadyBinding.WeaponInstanceId==Sword&&ReadyBinding.WeaponVersion==SwordVersion
    &&ReadyBinding.Armor==DungeonFairytaleSwordEquipmentBinding::EArmor::LightArmor
    &&ReadyBinding.ArmorInstanceId==Light&&ReadyBinding.ArmorVersion==LightVersion
    &&ReadyBinding.WeaponContentId==TEXT("WPN-SWD-001")&&ReadyBinding.ArmorContentId==TEXT("ARM-LGT-001");
   if(CompletedReady)
   {
    LightReadyCallbackObserved=true;LightReadyObservationIndex=Observations.Num()-1;
    LightReadyDrawId=B.DrawId;LightReadyCallbackSim=G->GetSimulationTime();LightReadyCallbackWall=Offset;
    LightReadyCallback=MakeShared<FJsonObject>();auto& ReadyReceipt=LightReadyCallback;
    ReadyReceipt->SetBoolField(TEXT("completed_native_screenshot_callback"),true);
    ReadyReceipt->SetNumberField(TEXT("observation_index"),LightReadyObservationIndex);
    Id(ReadyReceipt,TEXT("draw_id"),B.DrawId);ReadyReceipt->SetNumberField(TEXT("draw_sim"),B.SimulationTime);
    ReadyReceipt->SetNumberField(TEXT("callback_sim"),LightReadyCallbackSim);ReadyReceipt->SetNumberField(TEXT("wall_offset_s"),Offset);
    ReadyReceipt->SetStringField(TEXT("run"),ReadyBinding.RunGuid.ToString(EGuidFormats::Digits));Id(ReadyReceipt,TEXT("owner"),ReadyBinding.OwnerId);
    Id(ReadyReceipt,TEXT("room"),V.RoomInstanceId);Id(ReadyReceipt,TEXT("epoch"),G->GetRunPresentationEpoch());
    Id(ReadyReceipt,TEXT("weapon_instance"),ReadyBinding.WeaponInstanceId);Id(ReadyReceipt,TEXT("weapon_version"),ReadyBinding.WeaponVersion);
    Id(ReadyReceipt,TEXT("armor_instance"),ReadyBinding.ArmorInstanceId);Id(ReadyReceipt,TEXT("armor_version"),ReadyBinding.ArmorVersion);
    ReadyReceipt->SetNumberField(TEXT("facing"),B.Facing);ReadyReceipt->SetObjectField(TEXT("old_draw"),OldDraw(B));
    ReadyReceipt->SetArrayField(TEXT("actual_stack"),Strings(H->GetRenderedPlayerDrawStack()));
   }
  }
  if(Pose>=0)''')
    source=replace_once(source,'FlowComplete=Need(JumpInputs==3&&AirTransitions==3&&LandingTransitions==3&&NoArmorMask==63&&LightFirstMask==63&&LightSecondMask==63&&RejumpIssuedInsideLanding&&NoArmorFrames>=6&&LightFrames>=12,',
        'FlowComplete=Need(LightReadyCallbackObserved&&LightReadyCallbackConsumed&&JumpInputs==3&&AirTransitions==3&&LandingTransitions==3&&NoArmorMask==63&&LightFirstMask==63&&LightSecondMask==63&&RejumpIssuedInsideLanding&&NoArmorFrames>=6&&LightFrames>=12,')
    source=replace_once(source,'  R->SetArrayField(TEXT("normal_inputs"),Inputs);',
'''  R->SetBoolField(TEXT("LGT_completed_Ready_callback_observed"),LightReadyCallbackObserved);
  R->SetBoolField(TEXT("LGT_completed_Ready_callback_consumed_once"),LightReadyCallbackConsumed);
  if(LightReadyCallback.IsValid())R->SetObjectField(TEXT("LGT_completed_Ready_callback"),LightReadyCallback);
  R->SetArrayField(TEXT("normal_inputs"),Inputs);''')
    source=replace_once(source,
'''   case 5:if(!G->GetEquipmentView().Action.Active&&G->GetEquipmentView().Slots[2].InstanceId==Light&&CanPulse()&&PinGear(P))
    {const auto& D=H->GetFairytaleSwordDraw();if(!Need(D.Active&&D.Supported&&D.ArmorDrawn&&SwordDrawn(D)&&P->Facing==float(Side),TEXT("Real committed LGT/sword/facing not visible before normal Space")))return;if(Pulse(EKeys::SpaceBar)){++JumpInputs;Next(6);}}break;''',
'''   case 5:if(!G->GetEquipmentView().Action.Active&&G->GetEquipmentView().Slots[2].InstanceId==Light&&CanPulse()&&PinGear(P)&&LightReadyCallbackObserved)
    {
     const auto& CurrentView=G->GetEquipmentView();const auto& D=H->GetFairytaleSwordDraw();
     if(!Need(!LightReadyCallbackConsumed&&LightReadyCallback.IsValid()&&LightReadyObservationIndex>=0&&LightReadyDrawId>LastNewDraw
       &&LightReadyCallbackSim>=0.&&LightReadyCallbackSim<=G->GetSimulationTime()&&Now-Start>LightReadyCallbackWall
       &&CurrentView.RunGuid==Run&&CurrentView.OwnerId==Owner&&CurrentView.RoomInstanceId==Room
       &&G->GetRunPresentationEpoch()==Epoch&&G->GetRunRestartSerial()==Restart&&P->GetRuntimeEntityId()==Owner,
       TEXT("Completed LGT Ready callback handoff lost its actual owner/clock or was reused")))return;
     if(!Need(D.Active&&D.Supported&&D.ArmorDrawn&&SwordDrawn(D)&&P->Facing==float(Side),TEXT("Real committed LGT/sword/facing not visible before normal Space")))return;
     if(Pulse(EKeys::SpaceBar)){LightReadyCallbackConsumed=true;++JumpInputs;Next(6);}
    }break;''')
    result=source.replace('\n',newline) if newline=='\r\n' else source
    write_new(HERE/'new-source/DungeonHeroAirProductionProbeV001.cpp',result.encode('utf-8'))
    write_new(HERE/'callback-ready-only-v002.diff',''.join(difflib.unified_diff(original.splitlines(True),source.splitlines(True),fromfile='frozen-e7b9/DungeonHeroAirProductionProbeV001.cpp',tofile='NEW-callback-ready-v002/DungeonHeroAirProductionProbeV001.cpp')).encode('utf-8'))
    jwrite(HERE/'before-actual-Source296-three-pins-v002.json',before)
    failed=ROOT/'过程图稿与视频/2026-10-19_钟盔装备跳跃三连实录_left_v001/原件/runtime-report.json'
    r=json.loads(failed.read_text(encoding='utf-8-sig'))
    spaces=[x for x in r['normal_inputs'] if x['down'] and x['key']=='SpaceBar']
    jwrite(HERE/'callback-ready-source-lineage-v002.json',dict(schema='HeroAir-production-observer-callback-ready-source-lineage-v002',
        utc=datetime.now(timezone.utc).isoformat(),old_source_freeze=pin(SOURCE_FREEZE),old_source_files=old['source_files'],
        actual_before_files=before,failed_native_report=pin(failed),failed_native_passed=r['passed'],failed_reason=r['failure'],
        first_Space_immediate_actual_fields=spaces[0],
        change_scope='Observe actual completed Ready callback creates one identity-bound token; case5 waits and consumes once before ordinary Space. Key only appends actual pre-InputKey identity/gear/observer-ordinal metadata. Prior Need and immediate H/V remain; no sleep, input or gameplay/physics changes.',
        callback_Ready_stack='Existing Ready actual nonempty stack; not Air9. Exact current HUD stack equality required.',
        immutable_other_files=['DungeonHeroAirProductionProbeV001.h','DungeonHUD.cpp'],
        current_after_candidate_files=[pin(HERE/'new-source'/Path(x['path']).name) for x in old['source_files']],
        geometry_optics_masks_landing_window_audio_PNG_GPU_unchanged=True,
        queued_input_checker_legacy_issue='Actual first InputKey afterV0; old66f1 assumed synchronous630. NEW independently owned causal checker required, never spoof these actual fields.',
        current_actual_CM296_SHA256='57da85947be6d028dbc413f3c4fc6221ff5b0f4c66eed4cedea07773995da647',
        current_actual_CM296=pin(ROOT/'source-assets/production/backups/v142-HeroAir6-Observer296-203GREEN-v001/compiled-source-manifest.json'),
        source_actual_changed=False,UE_started=False,native_passed=False,FinalAccepted=False))
    print(json.dumps(dict(new_source=[pin(p) for p in sorted((HERE/'new-source').glob('*'))],actual_writes=0,UE_started=False,FinalAccepted=False)))


if __name__=='__main__':main()
