#include "DungeonHeroAirProbeV001.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonHUD.h"
#include "DungeonContentProbe.h"
#include "DungeonNativeMainSubmixCaptureV001.h"
#include "DungeonFairytaleSwordEquipmentBinding.h"
#include "DungeonProofScreenshots.h"
#include "Engine/Engine.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Kismet/GameplayStatics.h"
#include "UnrealClient.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformProcess.h"
#include "HAL/PlatformTime.h"
#include "Misc/App.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#if PLATFORM_WINDOWS
#include "Windows/AllowWindowsPlatformTypes.h"
#include <Windows.h>
#include "Windows/HideWindowsPlatformTypes.h"
#endif

namespace
{
using JO=TSharedPtr<FJsonObject>;using JV=TSharedPtr<FJsonValue>;
bool WriteNewUTF8(const FString& Path,const FString& Text)
{
#if PLATFORM_WINDOWS
 const FTCHARToUTF8 UTF8(*Text,Text.Len());
 HANDLE File=::CreateFileW(*Path,GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
 if(File==INVALID_HANDLE_VALUE)return false;
 DWORD Written=0;const DWORD Length=DWORD(UTF8.Length());
 const bool Ok=::WriteFile(File,UTF8.Get(),Length,&Written,nullptr)!=0&&Written==Length&&::FlushFileBuffers(File)!=0;
 ::CloseHandle(File);return Ok; // Failed partial bytes remain owned evidence; never overwrite/retry.
#else
 return false; // This isolated native proof contract is Windows-only.
#endif
}
TArray<JV> XY(FVector2D V){return {MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y)};}
TArray<JV> Strings(const TArray<FString>& V){TArray<JV> A;for(const auto& S:V)A.Add(MakeShared<FJsonValueString>(S));return A;}
void Id(JO O,const TCHAR* Key,uint64 V){O->SetStringField(Key,FString::Printf(TEXT("%llu"),V));}
int32 PhysicalPose(float H,float V,float Age)
{if(H>0.f||V>0.f)return V>315.f?0:V>90.f?1:V>=-90.f?2:3;return H==0.f&&V==0.f&&Age>=0.f&&Age<.12f?(Age<.06f?4:5):-1;}
bool SwordDrawn(const FDungeonFairytaleSwordDraw& D){return !D.WeaponPath.IsEmpty()&&D.DrawStack.Contains(D.WeaponPath);}
JO OldDraw(const FDungeonFairytaleSwordDraw& D)
{
 auto O=MakeShared<FJsonObject>();Id(O,TEXT("draw_id"),D.DrawId);O->SetNumberField(TEXT("sim"),D.SimulationTime);O->SetStringField(TEXT("clip"),D.Clip);O->SetNumberField(TEXT("frame"),D.Frame);O->SetNumberField(TEXT("facing"),D.Facing);
 O->SetBoolField(TEXT("active"),D.Active);O->SetBoolField(TEXT("supported"),D.Supported);O->SetBoolField(TEXT("action_pose_supported"),D.ActionPoseSupported);O->SetBoolField(TEXT("gear_placeholder"),D.GearPlaceholder);O->SetBoolField(TEXT("texture_ready"),D.TextureReady);
 O->SetBoolField(TEXT("armor_drawn"),D.ArmorDrawn);O->SetBoolField(TEXT("sword_drawn"),SwordDrawn(D));O->SetStringField(TEXT("body_texture"),D.TexturePath);O->SetStringField(TEXT("sword_texture"),D.WeaponPath);O->SetArrayField(TEXT("actual_stack"),Strings(D.DrawStack));
 O->SetArrayField(TEXT("root_source"),XY(D.Root));O->SetArrayField(TEXT("grip_source"),XY(D.Grip));O->SetArrayField(TEXT("grip_screen"),XY(D.GripScreen));O->SetNumberField(TEXT("canvas_size"),D.CanvasSize);
 if(auto* T=FindObject<UTexture2D>(nullptr,*D.TexturePath)){O->SetStringField(TEXT("body_class"),T->GetClass()->GetName());O->SetNumberField(TEXT("body_width"),T->GetSizeX());O->SetNumberField(TEXT("body_height"),T->GetSizeY());O->SetBoolField(TEXT("body_resource_ready"),T->GetResource()!=nullptr);O->SetBoolField(TEXT("body_pending_initialization"),T->HasPendingRenderResourceInitialization());}
 return O;
}
JO NewDraw(const FDungeonFairytaleSwordAirDrawV001& D)
{
 auto O=MakeShared<FJsonObject>();Id(O,TEXT("draw_id"),D.DrawId);Id(O,TEXT("player_entity"),D.PlayerEntityId);O->SetNumberField(TEXT("sim"),D.SimulationTime);O->SetBoolField(TEXT("opt_in"),D.OptIn);O->SetBoolField(TEXT("drawn"),D.Drawn);O->SetBoolField(TEXT("atomic_preflight_ready"),D.AtomicPreflightReady);O->SetStringField(TEXT("missing_reason"),D.MissingReason);
 O->SetNumberField(TEXT("slot_count"),D.Slots.Num());O->SetNumberField(TEXT("resident_count"),D.ResidentTextures.Num());O->SetArrayField(TEXT("actual_stack"),Strings(D.ActualRenderedStack));TArray<JV> Slots;
 for(const auto& S:D.Slots){auto X=MakeShared<FJsonObject>();X->SetNumberField(TEXT("slot"),S.SlotIndex);X->SetNumberField(TEXT("component"),int32(S.Component));X->SetStringField(TEXT("texture"),S.TexturePath);X->SetBoolField(TEXT("drawn"),S.Drawn);X->SetBoolField(TEXT("texture_ready"),S.TextureReady);X->SetArrayField(TEXT("top"),XY(S.Top));X->SetArrayField(TEXT("size"),XY(S.Size));X->SetArrayField(TEXT("uv"),XY(S.UV));X->SetArrayField(TEXT("uv_size"),XY(S.UVSize));X->SetNumberField(TEXT("rotation"),S.RotationDegrees);X->SetArrayField(TEXT("rotation_pivot"),XY(S.RotationPivot));Slots.Add(MakeShared<FJsonValueObject>(X));}
 O->SetArrayField(TEXT("slots"),Slots);return O;
}
}

struct FDungeonHeroAirProofStateV001
{
 FString Directory,Failure;int32 Side=0,Phase=0,JumpInputs=0,AirTransitions=0,LandingTransitions=0,BareFrames=0,LandingFrames=0;
 bool Stopped=false,EvidenceClaimed=false,PrewarmRequested=false,PrewarmDone=false,AudioRequested=false,Capturing=false,Stopping=false,FlowComplete=false;
 bool PreviousAir=false,FirstLandingObserved=false,SecondLandingObserved=false,GearPinned=false,KnightCleared=false,AllowKnightDiagnostic=false;
 double WarmStarted=0.,Start=0.,Stop=0.,ReleaseAt=0.,NeutralUntil=0.,PhaseAt=0.,InitialHP=0.,CaptureFinalHP=0.;
 FKey PulseKey;TMap<FKey,bool> Keys;uint32 AirMask=0,LandingMask=0;uint64 LastOldDraw=0;
 TWeakObjectPtr<ADungeonGameMode> Game;TWeakObjectPtr<APlayerController> Controller;TWeakObjectPtr<ADungeonHUD> HUD;
 FGuid Run;uint64 Owner=0,Room=0,Epoch=0,Restart=0,LightSource=0,Light=0,Sword=0,SwordVersion=0,LightVersion=0;
 TArray<JV> Inputs,Steps,Observations,Offsets,DiagnosticHits;

 void Next(int32 P){Phase=P;PhaseAt=FPlatformTime::Seconds();auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("phase"),P);O->SetNumberField(TEXT("wall_offset_s"),PhaseAt-Start);O->SetNumberField(TEXT("sim"),Game.IsValid()?Game->GetSimulationTime():0.);Steps.Add(MakeShared<FJsonValueObject>(O));}
 bool Need(bool Yes,const FString& Why){if(!Yes&&Failure.IsEmpty())Failure=Why;return Yes;}
 void Key(FKey K,bool Down)
 {
  if(!Controller.IsValid()||Keys.FindRef(K)==Down)return;Controller->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));Keys.Add(K,Down);
  auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("key"),K.GetFName().ToString());O->SetBoolField(TEXT("down"),Down);O->SetNumberField(TEXT("wall_offset_s"),FPlatformTime::Seconds()-Start);O->SetNumberField(TEXT("sim"),Game.IsValid()?Game->GetSimulationTime():0.);Inputs.Add(MakeShared<FJsonValueObject>(O));
 }
 bool CanPulse()const{return !PulseKey.IsValid()&&FPlatformTime::Seconds()>=NeutralUntil;}
 bool Pulse(FKey K){if(!CanPulse())return false;Key(K,true);PulseKey=K;ReleaseAt=FPlatformTime::Seconds()+.04;return true;}
 void ReleaseKeys(){TArray<FKey> Held;Keys.GetKeys(Held);for(FKey K:Held)Key(K,false);PulseKey=FKey();}
 void BeginStop(ADungeonHeroAirProbeV001& Actor)
 {
  if(Stopping||Stopped)return;Stopping=true;Capturing=false;GIsDumpingMovie=0;ReleaseKeys();
  if(Actor.MainMixCapture)
  {
   const auto MixPhase=Actor.MainMixCapture->Status().Phase;
   if(MixPhase==EDungeonNativeMixCapturePhaseV001::Recording||MixPhase==EDungeonNativeMixCapturePhaseV001::ExportPending)
   {if(!Actor.MainMixCapture->Stop())Need(false,TEXT("Native main mix could not stop after final actual callback"));}
   else if(!Actor.MainMixCapture->IsTerminal())Actor.MainMixCapture->Abort(Failure.IsEmpty()?TEXT("Capture stopped before Recording"):Failure);
   Stop=Actor.MainMixCapture->Status().StopMonotonic;
  }
  if(Stop<=0.)Stop=FPlatformTime::Seconds();
 }
 bool ClearKnightIfRequested(ADungeonFighter* Player,const FDungeonFirstBatchGuardRoomView& View)
 {
  if(!AllowKnightDiagnostic||KnightCleared)return true;
  ADungeonFighter* Knight=nullptr;for(auto E:Game->Enemies)if(E&&E->GetRuntimeEntityId()==View.Slots[0].EntityId)Knight=E;
  if(!Need(Knight&&Knight->GetStoneKnightDriver()&&!Knight->GetStoneGuardDriver()&&Knight->EnemyContentId==TEXT("ENM-STN-001"),TEXT("Explicit diagnostic requires the actual first Knight only")))return false;
  if(Knight->bDead){KnightCleared=true;return true;}if(!Knight->CanReceiveDirectHit())return false;
  auto O=MakeShared<FJsonObject>();Id(O,TEXT("entity"),Knight->GetRuntimeEntityId());O->SetStringField(TEXT("content"),Knight->EnemyContentId);O->SetStringField(TEXT("api"),TEXT("ADungeonFighter::ApplyCombatHit"));O->SetBoolField(TEXT("explicit_cli_authorization"),true);O->SetNumberField(TEXT("sim"),Game->GetSimulationTime());O->SetNumberField(TEXT("before_hp"),Knight->Health);
  Knight->ApplyCombatHit(100000.f,Player,85.f);O->SetNumberField(TEXT("after_hp"),Knight->Health);O->SetBoolField(TEXT("dead"),Knight->bDead);DiagnosticHits.Add(MakeShared<FJsonValueObject>(O));KnightCleared=Knight->bDead;return Need(KnightCleared,TEXT("Public predecessor diagnostic did not complete; no HP assignment fallback"));
 }
 bool PinGear(ADungeonFighter* P)
 {
  DungeonFairytaleSwordEquipmentBinding::FBinding B;FString Why;if(!DungeonFairytaleSwordEquipmentBinding::Resolve(*Game.Get(),*P,B,Why))return Need(false,TEXT("Actual committed SWD/LGT binding: ")+Why);
  if(!Need(B.Armor==DungeonFairytaleSwordEquipmentBinding::EArmor::LightArmor&&B.ArmorInstanceId==Light&&B.WeaponContentId==TEXT("WPN-SWD-001"),TEXT("Real E did not commit the requested SWD/LGT pair")))return false;
  if(!GearPinned){Sword=B.WeaponInstanceId;SwordVersion=B.WeaponVersion;LightVersion=B.ArmorVersion;GearPinned=true;}
  return Need(B.WeaponInstanceId==Sword&&B.WeaponVersion==SwordVersion&&B.ArmorInstanceId==Light&&B.ArmorVersion==LightVersion,TEXT("Pinned committed equipment identity/version changed"));
 }
 void Observe(ADungeonHeroAirProbeV001& Actor)
 {
  if(Stopped||Stopping)return;if(PrewarmRequested&&!PrewarmDone){PrewarmDone=Need(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))>8,TEXT("Actual prewarm image missing"));return;}if(!Capturing)return;
  auto G=Game.Get();auto H=HUD.Get();auto P=G?G->PlayerFighter.Get():nullptr;if(!Need(G&&H&&P,TEXT("Actual callback lost native owner"))){BeginStop(Actor);return;}
  const auto& V=G->GetEquipmentView();const auto& B=H->GetFairytaleSwordDraw();const auto& A=H->GetFairytaleSwordAirDraw();const bool Air=P->JumpHeight>0.f||P->GetVerticalVelocity()>0.f;
  const int32 Pose=PhysicalPose(P->JumpHeight,P->GetVerticalVelocity(),P->GetLandingVisualAge());auto O=MakeShared<FJsonObject>();const double Offset=FPlatformTime::Seconds()-Start;
  O->SetNumberField(TEXT("wall_offset_s"),Offset);O->SetNumberField(TEXT("phase"),Phase);O->SetNumberField(TEXT("sim"),G->GetSimulationTime());O->SetStringField(TEXT("run"),V.RunGuid.ToString(EGuidFormats::Digits));Id(O,TEXT("owner"),V.OwnerId);Id(O,TEXT("current_room"),V.RoomInstanceId);Id(O,TEXT("epoch"),G->GetRunPresentationEpoch());Id(O,TEXT("player_entity"),P->GetRuntimeEntityId());
  O->SetArrayField(TEXT("ground"),XY(P->GetGroundPosition()));O->SetArrayField(TEXT("camera_ground"),XY(H->GetCameraGroundCenter()));O->SetNumberField(TEXT("facing"),P->Facing);O->SetNumberField(TEXT("jump_height"),P->JumpHeight);O->SetNumberField(TEXT("vertical_velocity"),P->GetVerticalVelocity());O->SetNumberField(TEXT("landing_visual_age"),P->GetLandingVisualAge());O->SetNumberField(TEXT("physical_visual_key"),Pose);
  O->SetNumberField(TEXT("hp"),P->Health);O->SetBoolField(TEXT("dead"),P->bDead);O->SetStringField(TEXT("animation"),P->AnimationName);O->SetNumberField(TEXT("animation_time"),P->AnimationTime);O->SetBoolField(TEXT("melee_grounded"),P->GetMeleeCombatState().Grounded);O->SetBoolField(TEXT("wa_grounded"),P->GetWeaponActionsState().Budget.Grounded);O->SetBoolField(TEXT("melee_active"),P->GetMeleeCombatState().Action.Active);O->SetBoolField(TEXT("wa_active"),P->GetWeaponSkillAction().Active);
  O->SetNumberField(TEXT("melee_time"),P->GetMeleeCombatState().Time);O->SetNumberField(TEXT("wa_time"),P->GetWeaponActionsState().Time);O->SetNumberField(TEXT("dodge_time"),P->GetDodgeState().Time);O->SetNumberField(TEXT("weapon_world_time"),G->GetWeaponWorldState().Time);O->SetNumberField(TEXT("native_actor_root_z"),P->GetActorLocation().Z);Id(O,TEXT("melee_attack_id"),P->GetMeleeCombatState().Action.AttackId);Id(O,TEXT("wa_action_id"),P->GetWeaponSkillAction().ActionId);
  FDungeonHeroAirSample Q;O->SetBoolField(TEXT("new_air_query_ok"),P->QueryHeroNonAttackAir(Q));O->SetObjectField(TEXT("old_draw"),OldDraw(B));O->SetObjectField(TEXT("new_air_draw"),NewDraw(A));O->SetArrayField(TEXT("rendered_player_stack"),Strings(H->GetRenderedPlayerDrawStack()));O->SetStringField(TEXT("rendered_player_texture"),H->GetRenderedPlayerTexturePath());
  O->SetBoolField(TEXT("interface_visible"),H->GetInterfaceVisible());O->SetNumberField(TEXT("text_calls"),H->GetRenderedTextDrawCalls());O->SetBoolField(TEXT("range_debug"),H->IsCombatRangeDebugEnabled());O->SetNumberField(TEXT("range_lines"),H->GetCombatRangeDebugLineCount());
  Id(O,TEXT("weapon_instance"),V.Slots[V.ActiveSlot].InstanceId);Id(O,TEXT("weapon_version"),V.Slots[V.ActiveSlot].Version);Id(O,TEXT("armor_instance"),V.Slots[2].InstanceId);Id(O,TEXT("armor_version"),V.Slots[2].Version);
  const bool Bare=Air&&B.Active&&!B.Supported&&B.TextureReady&&B.Clip==TEXT("sword_ready_idle")&&B.Frame==0&&!B.ArmorDrawn&&!SwordDrawn(B)&&B.DrawStack.Num()==1&&B.DrawStack[0]==B.TexturePath&&H->GetRenderedPlayerDrawStack()==B.DrawStack;
  O->SetBoolField(TEXT("baseline_bare_ready0_gap"),Bare);Observations.Add(MakeShared<FJsonValueObject>(O));Offsets.Add(MakeShared<FJsonValueNumber>(Offset));
  if(!Need(V.RunGuid==Run&&V.OwnerId==Owner&&V.RoomInstanceId==Room&&G->GetRunPresentationEpoch()==Epoch&&G->GetRunRestartSerial()==Restart&&P->GetRuntimeEntityId()==Owner,TEXT("Native owner/run/room/epoch changed during isolated baseline"))
   ||!Need(!H->GetInterfaceVisible()&&H->GetRenderedTextDrawCalls()==0&&!H->IsCombatRangeDebugEnabled()&&H->GetCombatRangeDebugLineCount()==0,TEXT("Traditional HUD/range must remain hidden"))
   ||!Need(P->Health==InitialHP&&!P->bDead&&!G->bGameOver,TEXT("Baseline player took damage or died; no state repair allowed"))){BeginStop(Actor);return;}
  if(GearPinned&&!PinGear(P)){BeginStop(Actor);return;}
  if(GearPinned&&Air)
  {
   if(!Need(B.SimulationTime==G->GetSimulationTime()&&B.DrawId>LastOldDraw&&Bare&&A.Slots.IsEmpty()&&!A.Drawn,TEXT("Current baseline did not expose fresh bareReady0/no gear and zero unimplemented Air slots"))){BeginStop(Actor);return;}
   LastOldDraw=B.DrawId;++BareFrames;if(Pose>=0&&Pose<4)AirMask|=1u<<Pose;
  }
  if(Air&&!PreviousAir)++AirTransitions;
  if(!Air&&PreviousAir){++LandingTransitions;if(AirTransitions==1)FirstLandingObserved=true;if(AirTransitions==2)SecondLandingObserved=true;}
  PreviousAir=Air;if(SecondLandingObserved&&!Air&&Pose>=4){++LandingFrames;LandingMask|=1u<<Pose;}
  if(Phase==8&&SecondLandingObserved&&!Air&&P->GetLandingVisualAge()==.12f)
  {
   FlowComplete=Need(JumpInputs==2&&AirTransitions==2&&LandingTransitions==2&&AirMask==15&&LandingMask==48&&BareFrames>=8&&LandingFrames>=2,TEXT("Two real jumps did not expose full physical four-air/two-landing coverage and current gap"));CaptureFinalHP=P->Health;Next(9);BeginStop(Actor);
  }
 }
 void Finalize(ADungeonHeroAirProbeV001& Actor)
 {
  if(Stopped)return;Stopped=true;GIsDumpingMovie=0;ReleaseKeys();const bool Flushed=FlushFastLosslessProofScreenshots();auto R=MakeShared<FJsonObject>();
  const bool AudioComplete=Actor.MainMixCapture&&Actor.MainMixCapture->Status().Phase==EDungeonNativeMixCapturePhaseV001::Complete;
  const bool Passed=Failure.IsEmpty()&&FlowComplete&&Flushed&&AudioComplete&&!Observations.IsEmpty();
  R->SetStringField(TEXT("schema"),TEXT("hero-nonattack-air-baseline-native-observer-v001"));R->SetStringField(TEXT("pass_scope"),TEXT("current_renderer_missing_air_pose_and_gear_only"));R->SetBoolField(TEXT("passed"),Passed);R->SetBoolField(TEXT("baseline_gap_observed"),FlowComplete);R->SetBoolField(TEXT("new_air_passed"),false);R->SetBoolField(TEXT("final_accepted"),false);R->SetBoolField(TEXT("visual_reviewed"),false);R->SetBoolField(TEXT("audio_listened"),false);R->SetStringField(TEXT("failure"),Failure);
  Id(R,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());R->SetNumberField(TEXT("requested_facing"),Side);R->SetStringField(TEXT("run"),Run.ToString(EGuidFormats::Digits));Id(R,TEXT("owner"),Owner);Id(R,TEXT("current_room"),Room);Id(R,TEXT("epoch"),Epoch);Id(R,TEXT("restart_serial"),Restart);Id(R,TEXT("weapon_instance"),Sword);Id(R,TEXT("weapon_version"),SwordVersion);Id(R,TEXT("armor_instance"),Light);Id(R,TEXT("armor_version"),LightVersion);
  R->SetNumberField(TEXT("normal_space_inputs"),JumpInputs);R->SetNumberField(TEXT("air_transitions"),AirTransitions);R->SetNumberField(TEXT("landing_transitions"),LandingTransitions);R->SetNumberField(TEXT("physical_air_mask"),AirMask);R->SetNumberField(TEXT("second_landing_mask"),LandingMask);R->SetNumberField(TEXT("bare_ready0_frames"),BareFrames);R->SetNumberField(TEXT("landing_frames"),LandingFrames);R->SetNumberField(TEXT("initial_hp"),InitialHP);R->SetNumberField(TEXT("capture_final_hp"),CaptureFinalHP);
  R->SetArrayField(TEXT("normal_inputs"),Inputs);R->SetArrayField(TEXT("steps"),Steps);R->SetArrayField(TEXT("observations"),Observations);R->SetArrayField(TEXT("diagnostic_knight_hits"),DiagnosticHits);
  auto Timing=MakeShared<FJsonObject>();Timing->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());Timing->SetNumberField(TEXT("capture_start_monotonic_s"),Start);Timing->SetNumberField(TEXT("capture_stop_monotonic_s"),Stop);Timing->SetArrayField(TEXT("frame_wall_offsets_s"),Offsets);R->SetObjectField(TEXT("capture_timing"),Timing);
  if(Actor.MainMixCapture)R->SetObjectField(TEXT("main_submix_capture"),Actor.MainMixCapture->SerializeReport());
  FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);const bool Serialized=FJsonSerializer::Serialize(R,Writer);const FString Path=Directory/TEXT("runtime-report.json");
  const bool Written=Serialized&&EvidenceClaimed&&!Directory.IsEmpty()&&WriteNewUTF8(Path,Text);
  if(!Failure.IsEmpty())UE_LOG(LogTemp,Error,TEXT("Hero Air baseline: %s"),*Failure);FPlatformMisc::RequestExitWithStatus(false,Passed&&Written?0:3);
 }
 void Tick(ADungeonHeroAirProbeV001& Actor)
 {
  if(Stopped)return;const double Now=FPlatformTime::Seconds();if(Actor.MainMixCapture)Actor.MainMixCapture->Poll();
  if(Stopping){if(!Actor.MainMixCapture||Actor.MainMixCapture->IsTerminal())Finalize(Actor);return;}
  if(!Failure.IsEmpty()){BeginStop(Actor);return;}
  auto G=Actor.GetWorld()->GetAuthGameMode<ADungeonGameMode>();auto C=UGameplayStatics::GetPlayerController(&Actor,0);auto H=C?Cast<ADungeonHUD>(C->GetHUD()):nullptr;
  if(!Game.IsValid()&&Now-WarmStarted>12.){Need(false,TEXT("Native owner startup timeout"));BeginStop(Actor);return;}
  if(!Game.IsValid()&&G&&C&&C->PlayerInput&&H)
  {
   auto* P=G->PlayerFighter.Get();const auto& V=G->GetEquipmentView();if(!P||!V.Bound||!V.RunGuid.IsValid())return;
   Game=G;Controller=C;HUD=H;Run=V.RunGuid;Owner=V.OwnerId;Room=V.RoomInstanceId;Epoch=G->GetRunPresentationEpoch();Restart=G->GetRunRestartSerial();InitialHP=P->Health;
   Actor.AddTickPrerequisiteActor(G);Actor.AddTickPrerequisiteActor(H);return;
  }
  if(!Game.IsValid())return;
  if(PulseKey.IsValid()&&Now>=ReleaseAt){Key(PulseKey,false);PulseKey=FKey();NeutralUntil=Now+.04;}
  if(!Capturing)
  {
   if(!PrewarmRequested&&Now-WarmStarted>=2.){PrewarmRequested=true;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}
   if(PrewarmDone&&!AudioRequested){AudioRequested=true;Actor.MainMixCapture=NewObject<UDungeonNativeMainSubmixCaptureV001>(&Actor);if(!Actor.MainMixCapture->Begin(Actor.GetWorld(),Directory/TEXT("audio-v001")))Need(false,TEXT("Native main mix Begin request rejected"));}
   if(AudioRequested&&Actor.MainMixCapture&&Actor.MainMixCapture->Status().Phase==EDungeonNativeMixCapturePhaseV001::Recording)
   {
    const auto& Status=Actor.MainMixCapture->Status();if(!Need(Status.StartRequested&&Status.StartMonotonic>0.,TEXT("Recording state has no actual monotonic origin")))return;
    Start=Status.StartMonotonic;Capturing=true;GIsDumpingMovie=-1;Next(0);
   }
   if(Now-WarmStarted>20.)Need(false,TEXT("Prewarm/native mix arming timeout"));return;
  }
  auto P=G->PlayerFighter.Get();if(!Need(G==Game.Get()&&C==Controller.Get()&&H==HUD.Get()&&P&&C->GetPawn()==P&&C->IsLocalController()&&Now-Start<12.&&Now-PhaseAt<5.,TEXT("Normal-input baseline owner/phase timeout")))return;
  FDungeonFirstBatchGuardRoomView View;if(!Need(G->QueryFirstBatchGuardRoom(View)&&View.Slots.Num()==3&&G->GetEquipmentView().Config==EDungeonEquipmentRunConfig::FirstBatch,TEXT("Actual finite FirstBatchGuardRoom required")))return;
  if(!Run.IsValid()){const auto& V=G->GetEquipmentView();Run=V.RunGuid;Owner=V.OwnerId;Room=V.RoomInstanceId;Epoch=G->GetRunPresentationEpoch();Restart=G->GetRunRestartSerial();InitialHP=P->Health;}
  switch(Phase)
  {
   case 0:if(!Need(G->bWaitingForStart&&G->GetSimulationTime()==0.,TEXT("Baseline must start with real Enter, not Space releasing waiting")))return;if(Pulse(EKeys::Enter))Next(1);break;
   case 1:if(!G->bWaitingForStart&&CanPulse()&&ClearKnightIfRequested(P,View)){DungeonEquipmentInventory::FItem I;I.ContentId="ARM-LGT-001";const auto R=G->RegisterEquipmentSource(TEXT("display.hero.air.baseline.light.v001"),I,P->GetGroundPosition()+FVector2D(24,0),true);if(!Need(R.Ok()&&!R.Replayed,TEXT("Actual display LGT registration failed")))return;LightSource=R.SourceId;Light=R.InstanceId;Next(2);}break;
   case 2:if(CanPulse()&&G->GetEquipmentView().SelectedSourceId==LightSource&&Pulse(EKeys::E))Next(3);break;
   case 3:if(!G->GetEquipmentView().Action.Active&&G->GetEquipmentView().Slots[2].InstanceId==Light&&CanPulse()&&PinGear(P))Next(4);break;
   case 4:if(CanPulse()&&Pulse(Side<0?EKeys::A:EKeys::D))Next(5);break;
   case 5:if(CanPulse()&&P->Facing==float(Side)){const auto& D=H->GetFairytaleSwordDraw();if(!Need(D.Active&&D.Supported&&D.ArmorDrawn&&SwordDrawn(D),TEXT("Real committed LGT and sword were not visible before Space")))return;if(Pulse(EKeys::SpaceBar)){++JumpInputs;Next(6);}}break;
   case 6:if(FirstLandingObserved&&CanPulse()){if(!Need(P->JumpHeight==0.f&&P->GetVerticalVelocity()==0.f&&P->GetLandingVisualAge()<.10f,TEXT("Normal re-jump missed original landing window")))return;if(Pulse(EKeys::SpaceBar)){++JumpInputs;Next(7);}}break;
   case 7:if(AirTransitions==2)Next(8);break;
   case 8:break; // Finalize only after a real screenshot callback sees the second landing cap.
   default:Need(false,TEXT("Unexpected baseline observer state"));break;
  }
 }
};

void FDungeonHeroAirProofDeleterV001::operator()(FDungeonHeroAirProofStateV001* P)const{delete P;}
ADungeonHeroAirProbeV001::ADungeonHeroAirProbeV001(){PrimaryActorTick.bCanEverTick=true;}
ADungeonHeroAirProbeV001::~ADungeonHeroAirProbeV001()=default;
void ADungeonHeroAirProbeV001::BeginPlay()
{
 Super::BeginPlay();Proof.Reset(new FDungeonHeroAirProofStateV001());Proof->WarmStarted=FPlatformTime::Seconds();GIsDumpingMovie=0;
 FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),Proof->Directory);FParse::Value(FCommandLine::Get(),TEXT("DungeonHeroAirFacing="),Proof->Side);Proof->AllowKnightDiagnostic=FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroAirClearKnightDiagnostic"));
 if(!Proof->Need(!Proof->Directory.IsEmpty()&&!FPaths::IsRelative(Proof->Directory)&&(Proof->Side==-1||Proof->Side==1),TEXT("Absolute unused evidence directory and explicit facing[-1,+1] required")))return;
 Proof->Directory=FPaths::ConvertRelativePathToFull(Proof->Directory);FPaths::NormalizeDirectoryName(Proof->Directory);IFileManager::Get().MakeDirectory(*Proof->Directory,true);
 TArray<FString> Prior;IFileManager::Get().FindFiles(Prior,*(Proof->Directory/TEXT("*")),true,false);Prior.Remove(TEXT("native-lossless-capture.json"));TArray<FString> Subdirs;IFileManager::Get().FindFiles(Subdirs,*(Proof->Directory/TEXT("*")),false,true);
 if(!Proof->Need(Prior.IsEmpty()&&Subdirs.IsEmpty(),TEXT("Baseline output directory already contains prior evidence")))return;
 const FString Claim=FString::Printf(TEXT("{\"schema\":\"hero-air-baseline-process-claim-v001\",\"pid\":%u}\n"),FPlatformProcess::GetCurrentProcessId());
 if(!Proof->Need(WriteNewUTF8(Proof->Directory/TEXT("observer-process-claim-v001.json"),Claim),TEXT("Evidence claim already exists or cannot be created")))return;
 Proof->EvidenceClaimed=true;
 for(const TCHAR* Flag:{TEXT("DungeonHeroAirProofV001"),TEXT("DungeonHeroAirBaselineV001"),TEXT("DungeonFairytaleSwordEquipmentBoundPreview"),TEXT("DungeonContentProof"),TEXT("DungeonFastLosslessCapture"),TEXT("DungeonAsyncLosslessCapture")})if(!Proof->Need(FParse::Param(FCommandLine::Get(),Flag),FString(TEXT("Missing explicit baseline opt-in: "))+Flag))return;
 for(const TCHAR* Flag:{TEXT("DungeonProof"),TEXT("DungeonGuardMoveProofV001"),TEXT("DungeonHeroDodgeProofV001"),TEXT("DungeonHeroHurtProofV001"),TEXT("DungeonHeroDeathProofV001"),TEXT("DungeonGuardStompProofV001"),TEXT("DungeonGuardArtCombatProofV003"),TEXT("DungeonGuardArtDeathProofV005"),TEXT("DungeonGuardArtKnown44Proof"),TEXT("DungeonGuardArtPartialProof"),TEXT("DungeonGuardRoomFlowProof"),TEXT("DungeonFairytaleWalkProof"),TEXT("DungeonFairytaleEquipmentBoundProof"),TEXT("DungeonFairytaleSwordBodyProof"),TEXT("DungeonRunSaveProof"),TEXT("DungeonRunRestoreProof"),TEXT("DungeonGuardRunSaveProof"),TEXT("DungeonGuardRunRestoreProof"),TEXT("DungeonFairytaleLookdevProof"),TEXT("DungeonFairytaleLookdevPreview"),TEXT("DungeonCombatRangeDebug"),TEXT("DungeonCombatRangeProof"),TEXT("DungeonShowInterface")})if(!Proof->Need(!FParse::Param(FCommandLine::Get(),Flag),TEXT("Independent proof/visible HUD/range cannot share this observer")))return;
 for(TActorIterator<ADungeonContentProbe> It(GetWorld());It;++It)if(IsValid(*It)){Proof->Need(false,TEXT("Old ContentProbe is already running"));return;}
 if(!Proof->Need(!FApp::UseFixedTimeStep(),TEXT("Native variable pacing required")))return;
 GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Proof->Directory;FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonHeroAirProbeV001::ScreenshotProcessed);
}
void ADungeonHeroAirProbeV001::ScreenshotProcessed(){if(Proof)Proof->Observe(*this);}
void ADungeonHeroAirProbeV001::Tick(float D){Super::Tick(D);if(Proof)Proof->Tick(*this);}
void ADungeonHeroAirProbeV001::EndPlay(const EEndPlayReason::Type R)
{
 FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);
 if(Proof&&!Proof->Stopped)
 {
  Proof->Need(false,TEXT("Air baseline world ended before capture/export completed"));GIsDumpingMovie=0;
  if(MainMixCapture&&!MainMixCapture->IsTerminal())MainMixCapture->Abort(TEXT("Air baseline world ended before export completed"));
  Proof->BeginStop(*this);Proof->Finalize(*this);
 }
 Super::EndPlay(R);
}
