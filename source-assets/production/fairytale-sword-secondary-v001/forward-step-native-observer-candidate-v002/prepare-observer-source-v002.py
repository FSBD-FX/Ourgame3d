from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
HERE=Path(__file__).resolve().parent;OLD=HERE.parent/'forward-step-native-observer-candidate-v001';ROOT=HERE.parents[3]
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(rel,obj):
 p=HERE/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8',newline='') as f:f.write(obj if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 return p
def replace(text,old,new):assert text.count(old)==1,old[:130];return text.replace(old,new,1)
assert pin(OLD/'candidate-freeze-v001.json')['sha256']=='cdc65ddfd5922156517ff681aba6378ac4b3047888cd425054d9e38b41603046'
f=json.loads((OLD/'candidate-freeze-v001.json').read_text(encoding='utf8'))
for r in f['members']+f['dependencies']:
 q=Path(r['path']);q=q if q.is_absolute() else OLD/q;actual=pin(q);assert actual['bytes']==r['bytes'] and actual['sha256']==r['sha256'],q
cpp=(OLD/'projected/UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV001.cpp').read_text(encoding='utf-8-sig').replace('\r\n','\n')
hdr=(OLD/'projected/UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV001.h').read_text(encoding='utf-8-sig').replace('\r\n','\n')
for before,after in [('DungeonSwdForwardStepProbeV001','DungeonSwdForwardStepProbeV002'),('DungeonSwdForwardStepProofV001','DungeonSwdForwardStepProofV002'),('DungeonSwdForwardStepProofDeleterV001','DungeonSwdForwardStepProofDeleterV002')]:cpp=cpp.replace(before,after);hdr=hdr.replace(before,after)
# Keep original source readers, exclusive file writers, GPU/editor capture, InputKey,
# MainMix and lossless callback mechanisms. Only add true placement observation/mode.
cpp=replace(cpp,' TArray<JV> Inputs,Observations,Offsets,StartupTextures;',' TArray<JV> Inputs,Observations,Offsets,StartupTextures,PlacementRecords;\n TArray<FString> PlacementKeys;TArray<FDungeonWeaponForwardStepPlacementV001> PlacementValues;bool ExploratoryPilot=false;')
placement='''  JO PlacementPoll(const ADungeonFighter& P,const DungeonWeaponActions::FAction& Skill,double Sim,double Wall){
   auto O=MakeShared<FJsonObject>();const bool Called=Skill.Active&&Skill.Type==DungeonWeaponActions::EAction::Skill;
   O->SetBoolField(TEXT("getter_called_while_action_active"),Called);O->SetBoolField(TEXT("available"),false);O->SetBoolField(TEXT("new_unique_event"),false);
   O->SetNumberField(TEXT("callback_index"),Frames);O->SetNumberField(TEXT("callback_sim"),Sim);O->SetNumberField(TEXT("wall_offset_s"),Wall);
   if(!Called)return O;
   FDungeonWeaponForwardStepPlacementV001 W;if(!G->QueryWeaponForwardStepPlacementV001(W))return O;
   O->SetBoolField(TEXT("available"),true);auto R=MakeShared<FJsonObject>();R->SetBoolField(TEXT("present"),W.Present);R->SetBoolField(TEXT("grounded_at_commit"),W.GroundedAtCommit);
   R->SetStringField(TEXT("run"),W.RunGuid.ToString(EGuidFormats::Digits));
   Id(R,TEXT("room"),W.RoomInstanceId);Id(R,TEXT("owner"),W.OwnerId);Id(R,TEXT("action_id"),W.ActionId);Id(R,TEXT("instance_id"),W.InstanceId);Id(R,TEXT("event_id"),W.EventId);Id(R,TEXT("subhit_id"),W.SubhitId);Id(R,TEXT("epoch"),W.PresentationEpoch);Id(R,TEXT("restart"),W.RunRestartSerial);Id(R,TEXT("revision_at_commit"),W.EquipmentRevisionAtCommit);
   R->SetNumberField(TEXT("kind"),int32(W.Kind));R->SetNumberField(TEXT("weapon"),int32(W.Weapon));R->SetNumberField(TEXT("action_start"),W.ActionStart);R->SetNumberField(TEXT("at_time"),W.AtTime);R->SetNumberField(TEXT("observed_simulation_time"),W.ObservedSimulationTime);R->SetNumberField(TEXT("requested_signed_distance"),W.RequestedSignedDistance);
   R->SetArrayField(TEXT("before"),DungeonSwdForwardStepObservationV001::XY(W.Before));R->SetArrayField(TEXT("after"),DungeonSwdForwardStepObservationV001::XY(W.After));R->SetArrayField(TEXT("committed_delta"),DungeonSwdForwardStepObservationV001::XY(W.CommittedDelta));
   R->SetNumberField(TEXT("first_seen_callback"),Frames);R->SetNumberField(TEXT("readback_sim"),Sim);R->SetNumberField(TEXT("first_seen_wall_offset_s"),Wall);
   const DungeonWeaponActions::FEvent* Issued=nullptr;
   for(const auto& E:P.GetWeaponActionsState().Issued)if(E.Kind==DungeonWeaponActions::EEvent::ActiveWindow&&E.EventId==W.EventId+1&&E.ActionId==W.ActionId&&E.InstanceId==W.InstanceId&&E.SubhitId==W.SubhitId)Issued=&E;
   const bool Same=Issued&&W.Present&&W.GroundedAtCommit&&W.RunGuid==Run&&W.RoomInstanceId==Room&&W.OwnerId==Owner&&W.PresentationEpoch==Epoch&&W.RunRestartSerial==Restart
    &&W.ActionId==Skill.ActionId&&W.InstanceId==Sword&&W.ActionStart==Skill.Start&&W.AtTime==Skill.ActiveAt&&W.Kind==DungeonWeaponActions::EEvent::ForwardStep&&W.Weapon==Skill.Weapon
    &&Issued->AtTime==W.AtTime&&Issued->Action.Start==W.ActionStart&&W.RequestedSignedDistance==DungeonContentCombat::GetWeaponDefinition(Skill.Weapon)->Skill.ForwardStep*Skill.Facing&&W.ObservedSimulationTime>=W.AtTime&&W.ObservedSimulationTime<=Sim;
   R->SetBoolField(TEXT("actual_kernel_window_matches_step_source_key"),Same);Id(R,TEXT("kernel_next_event_id"),P.GetWeaponActionsState().NextEventId);
   if(Issued){auto E=MakeShared<FJsonObject>();Id(E,TEXT("event_id"),Issued->EventId);Id(E,TEXT("action_id"),Issued->ActionId);Id(E,TEXT("instance_id"),Issued->InstanceId);Id(E,TEXT("subhit_id"),Issued->SubhitId);E->SetNumberField(TEXT("at_time"),Issued->AtTime);E->SetNumberField(TEXT("kind"),int32(Issued->Kind));E->SetNumberField(TEXT("action_start"),Issued->Action.Start);R->SetObjectField(TEXT("actual_kernel_window_event"),E);}
   O->SetObjectField(TEXT("source"),R);if(!Need(Same,TEXT("Actual placement getter returned stale or mismatched real event/scope")))return O;
   const FString Key=W.RunGuid.ToString(EGuidFormats::Digits)+FString::Printf(TEXT("/%llu/%llu/%llu/%llu/%llu/%llu/%u/%llu"),(unsigned long long)W.RoomInstanceId,(unsigned long long)W.OwnerId,(unsigned long long)W.PresentationEpoch,(unsigned long long)W.RunRestartSerial,(unsigned long long)W.ActionId,(unsigned long long)W.InstanceId,W.SubhitId,(unsigned long long)W.EventId);
   const int32 Existing=PlacementKeys.IndexOfByKey(Key);
   if(Existing==INDEX_NONE){PlacementKeys.Add(Key);PlacementValues.Add(W);PlacementRecords.Add(MakeShared<FJsonValueObject>(R));O->SetBoolField(TEXT("new_unique_event"),true);}
   else {const auto& Old=PlacementValues[Existing];Need(Old.AtTime==W.AtTime&&Old.ActionStart==W.ActionStart&&Old.ObservedSimulationTime==W.ObservedSimulationTime&&Old.RequestedSignedDistance==W.RequestedSignedDistance&&Old.Before==W.Before&&Old.After==W.After&&Old.CommittedDelta==W.CommittedDelta,TEXT("Same real event key changed placement facts"));}
   return O;
  }
  FString PlacementClassification()const{
   if(PlacementValues.Num()!=1)return TEXT("missing_or_multiple");const double D=PlacementValues[0].CommittedDelta.Size();
   return D==0.?TEXT("blocked_zero"):FMath::Abs(D-30.)<.05?TEXT("full"):D>1.e-4&&D<29.95?TEXT("partial"):TEXT("unexpected");
  }
'''
cpp=replace(cpp,' JO RuntimeInventory()const{',placement+' JO RuntimeInventory()const{')
cpp=replace(cpp,'  auto W=MakeShared<FJsonObject>();W->SetBoolField(TEXT("available"),false);W->SetStringField(TEXT("reason"),TEXT("positive DTO is not an independent zero-placement commit reader"));O->SetObjectField(TEXT("zero_placement_witness"),W);','   O->SetObjectField(TEXT("placement_witness_poll"),PlacementPoll(*P,Skill,Sim,Wall));')
cpp=replace(cpp,'FlowComplete=Need(Mask==255&&ReadyBefore>=3,TEXT("K8 or actual Ready entry/End join missing"));','FlowComplete=Need(Mask==255&&ReadyBefore>=3&&PlacementValues.Num()==1,TEXT("K8, actual Ready join, or active-callback placement witness missing"));')
cpp=replace(cpp,'TEXT("swd-forward-step-native-observer-v001")','TEXT("swd-forward-step-native-observer-v002")')
cpp=replace(cpp,'R->SetBoolField(TEXT("formal_accepted"),false);','R->SetBoolField(TEXT("formal_accepted"),false);R->SetBoolField(TEXT("checker_accepted"),false);R->SetStringField(TEXT("route_mode"),ExploratoryPilot?TEXT("exploratory_pilot"):TEXT("strict"));R->SetBoolField(TEXT("normal_route_native_verified"),Route.IsValid()&&Route->GetBoolField(TEXT("normal_route_native_verified")));R->SetStringField(TEXT("native_route_classification"),PlacementClassification());if(Route.IsValid())R->SetObjectField(TEXT("route_input_configuration"),Route);R->SetArrayField(TEXT("placement_witnesses"),PlacementRecords);R->SetStringField(TEXT("K_pixel_composition_status"),TEXT("PENDING_INDEPENDENT_ACTUAL_NATIVE_PIXEL_CHECKER"));')
old=' S.Route=S.Prereg->GetObjectField(TEXT("cases"))->GetObjectField(S.Case);S.Facing=int32(S.Route->GetNumberField(TEXT("facing")));if(!S.Need((S.Facing==-1||S.Facing==1)&&S.Route->GetBoolField(TEXT("normal_route_native_verified")),TEXT("NotReady: exact normal input route unverified")))return;\n if(S.Case.StartsWith(TEXT("blocked_zero"))){S.Need(false,TEXT("NotReady: independent actual zero-placement commit reader not available"));return;}\n'
new='''  S.ExploratoryPilot=FParse::Param(FCommandLine::Get(),TEXT("DungeonSwdForwardStepPilotV002"));FString RouteMode;
  if(!S.Need(S.Prereg->TryGetStringField(TEXT("route_mode"),RouteMode)&&RouteMode==(S.ExploratoryPilot?TEXT("exploratory_pilot"):TEXT("strict")),TEXT("NotReady: explicit pilot flag and prereg mode must agree")))return;
  if(!S.Need(S.Prereg->GetBoolField(TEXT("placement_witness_source_ready")),TEXT("NotReady: actual placement getter must be admitted and compiled")))return;
  S.Route=S.Prereg->GetObjectField(TEXT("cases"))->GetObjectField(S.Case);S.Facing=int32(S.Route->GetNumberField(TEXT("facing")));
  if(!S.Need((S.Facing==-1||S.Facing==1)&&(S.ExploratoryPilot||S.Route->GetBoolField(TEXT("normal_route_native_verified"))),TEXT("NotReady: strict requires independently verified actual normal route")))return;
'''
cpp=replace(cpp,old,new)
write('projected/UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV002.cpp',cpp.replace('\n','\r\n'));write('projected/UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV002.h',hdr.replace('\n','\r\n'))
seams=json.loads((OLD/'exact-seams-v001.json').read_text(encoding='utf8'))
for op in seams['operations']:op['text']=op['text'].replace('DungeonSwdForwardStepProbeV001','DungeonSwdForwardStepProbeV002').replace('DungeonSwdForwardStepProofV001','DungeonSwdForwardStepProofV002')
seams['schema']='swd-native-observer-exact-seams-v002';seams['new_files']=[x.replace('ProbeV001','ProbeV002') for x in seams['new_files']];seams['existing_source_semantics']='Only V002 opt-in observer dispatch/old ContentProbe suppression. Compose exact inserts; never copy whole old HUD. Pilot is explicit -DungeonSwdForwardStepPilotV002 and cannot claim acceptance.'
baselines={}
for rel in {o['target'] for o in seams['operations']}:
 p=ROOT/rel;raw=p.read_bytes();text=raw.decode('utf8');after=text
 for op in [o for o in seams['operations'] if o['target']==rel]:
  assert after.count(op['anchor'])==1;joined=op['text']+op['anchor'] if op['kind']=='insert_before' else op['anchor']+op['text'];after=after.replace(op['anchor'],joined,1)
 inv=after
 for op in reversed([o for o in seams['operations'] if o['target']==rel]):
  joined=op['text']+op['anchor'] if op['kind']=='insert_before' else op['anchor']+op['text'];assert inv.count(joined)==1;inv=inv.replace(joined,op['anchor'],1)
 assert inv.encode('utf8')==raw;baselines[rel]=pin(p)
seams['baseline_files']=baselines;seams['strict_inverse_original_bytes_exact']=True;write('exact-seams-v002.json',seams)
for name in ['reused-gpu-capture-lambda-v001.inl','reused-exclusive-writers-v001.inl']:
 data=(OLD/'source'/name).read_text(encoding='utf-8-sig');write('source/'+name,data)
# Template is intentionally not runnable until real review/compile/resource pins exist.
p=json.loads((OLD/'readiness-v001.json').read_text(encoding='utf8'));p['schema']='swd-forward-step-native-readiness-v002';p['route_mode']='exploratory_pilot';p['ready']=False;p['placement_witness_source_ready']=False;p['pending']=['actual admitted K8 Profile and all57 Texture2D paths plus oldReady24 readback pins','fresh independent V002 observer plus placement getter source review/admission and Editor build','complete current compiled manifest/203 or actual registered tests and current game DLL pins','first full_right exploratory pilot route is intentionally not verified; no cyclic route gate','actual independent K pixel-composition checker remains pending; pilot can retain raw evidence with acceptance false'];p['zero_placement_reader']='QueryWeaponForwardStepPlacementV001, candidate4e1b918f..., requires actual source admission/build';p['K_trace_adapter']='same typed K8 interface; requires Root final profile/source admission';p['checker_dependencies']={'main_mix':None,'native_png':None,'K_pixel_composition':None}
for case in p['cases'].values():case['route_native_verification']=None
write('prereg-exploratory-full-right-template-v002.json',p)
write('source-build-preparation-v002.json',{'utc':datetime.now(timezone.utc).isoformat(),'old_freeze':pin(OLD/'candidate-freeze-v001.json'),'placement_witness_freeze':pin(HERE.parent/'forward-step-placement-witness-candidate-v001/candidate-freeze-v001.json'),'actual_baselines':baselines,'new_source_files':2,'old_HUD_not_copied':True,'original_full_gpu_editor_readback_writer_input_MainMix_mechanisms_retained':True,'native_executed':False,'UE_compiled':False})
print(json.dumps({'new_cpp':pin(HERE/'projected/UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV002.cpp'),'new_header':pin(HERE/'projected/UnrealGame/Source/CodexDungeon/DungeonSwdForwardStepProbeV002.h'),'seams':len(seams['operations']),'native_executed':False}))
