#include "DungeonGuardRoomFlowProbe.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonHUD.h"
#include "DungeonStoneBatDriver.h"
#include "DungeonStoneGuardDriver.h"
#include "DungeonRunInstaller.h"
#include "DungeonRunSnapshotCodec.h"
#include "DungeonSaveGenerationStore.h"
#include "DungeonFairytaleSwordBodyV001.inl"
#include "DungeonProofScreenshots.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Kismet/GameplayStatics.h"
#include "UnrealClient.h"
#include "Misc/App.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformProcess.h"
#include "HAL/PlatformTime.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
namespace
{
using JO=TSharedPtr<FJsonObject>;
void Id(JO O,const TCHAR* K,uint64 V){O->SetStringField(K,LexToString(V));}
TArray<TSharedPtr<FJsonValue>> XY(FVector2D P){return {MakeShared<FJsonValueNumber>(P.X),MakeShared<FJsonValueNumber>(P.Y)};}
const TCHAR* Name(int32 P)
{
 static const TCHAR* N[]={TEXT("normal_room_start"),TEXT("display_light_source"),TEXT("normal_light_commit"),TEXT("normal_move_to_knight"),
 TEXT("normal_J_combat"),TEXT("normal_Shift_retreat"),TEXT("diagnostic_remaining_knight_HP"),TEXT("knight_settled_ground_coin"),TEXT("normal_pickup_knight_coin"),
 TEXT("bat_future_warning_birth"),TEXT("native_bat_then_diagnostic_HP"),TEXT("normal_pickup_bat_coin"),TEXT("guard_future_warning_birth"),
 TEXT("native_guard_then_diagnostic_HP"),TEXT("guard_formal_settled_root_v2"),TEXT("normal_pickup_guard_coin"),TEXT("grouped_install_pause"),
 TEXT("fresh_Enter_continue"),TEXT("complete")};
 return P>=0&&P<UE_ARRAY_COUNT(N)?N[P]:TEXT("invalid");
}
}
struct FDungeonGuardRoomFlowState
{
 FString Directory;bool Manual=false,ManualDone=false,Stopped=false,Prewarm=false,Capturing=false,FinishOnFrame=false,Complete=false;
 TWeakObjectPtr<ADungeonGameMode> Game;TWeakObjectPtr<APlayerController> Controller;TWeakObjectPtr<ADungeonHUD> HUD;
 TMap<FKey,bool> Keys;FKey PulseKey;double ReleaseAt=0.,NeutralUntil=0.,Warm=0.,Start=0.,Stop=0.,PhaseWall=0.,PauseWall=0.;int32 Phase=0;
 FGuid Run;uint64 Owner=0,Restart=0,Light=0,KnightId=0,InitialDodge=0,LastDraw=0;
 double JInitialHP=0.,JActualHPLoss=0.;int32 JHitReceipts=0,WarningFrames[3]={},BornFrames[3]={};bool DodgeObserved=false,WarningSaved[3]={};
 TSet<uint64> JAttacks;TArray<uint8> SavedBytes;FDungeonRunSnapshot Saved;FDungeonPreparedRun Prepared;
 JO Report=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Inputs,Steps,Observations,Offsets,DiagnosticHits,CodecFiles;
 void Key(FKey K,bool Down)
 {
  if(Keys.FindRef(K)==Down)return;if(auto C=Controller.Get())
  {C->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));Keys.Add(K,Down);
   auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("key"),K.ToString());O->SetBoolField(TEXT("down"),Down);
   O->SetNumberField(TEXT("wall_offset_s"),Capturing?FPlatformTime::Seconds()-Start:0.);O->SetNumberField(TEXT("sim"),Game.IsValid()?Game->GetSimulationTime():0.);Inputs.Add(MakeShared<FJsonValueObject>(O));}
 }
 void MoveStop(){for(FKey K:{EKeys::A,EKeys::D,EKeys::W,EKeys::S})Key(K,false);}
 bool CanPulse()const{return !PulseKey.IsValid()&&FPlatformTime::Seconds()>=NeutralUntil;}
 bool Pulse(FKey K){if(!CanPulse())return false;Key(K,true);PulseKey=K;ReleaseAt=FPlatformTime::Seconds()+.08;return true;}
 void Next(int32 P)
 {Phase=P;PhaseWall=FPlatformTime::Seconds();auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("phase"),Name(P));O->SetNumberField(TEXT("wall_offset_s"),PhaseWall-Start);O->SetNumberField(TEXT("sim"),Game->GetSimulationTime());Steps.Add(MakeShared<FJsonValueObject>(O));}
 void Finish(const FString& Why=FString())
 {
  if(Stopped||Manual)return;Stopped=true;Stop=FPlatformTime::Seconds();GIsDumpingMovie=0;
  TArray<FKey> Held;Keys.GetKeys(Held);for(FKey K:Held)Key(K,false);const bool Flushed=FlushFastLosslessProofScreenshots();
  Report->SetStringField(TEXT("schema"),TEXT("guard-room-native-flow-diagnostic-v001"));Report->SetBoolField(TEXT("passed"),Why.IsEmpty()&&Complete&&Flushed&&!Observations.IsEmpty());Report->SetStringField(TEXT("failure"),Why);
  Report->SetBoolField(TEXT("flow_complete"),Complete);Report->SetBoolField(TEXT("normal_J_full_clear"),false);Report->SetBoolField(TEXT("diagnostic_public_damage_used"),!DiagnosticHits.IsEmpty());
  Report->SetStringField(TEXT("scope"),TEXT("Normal Bridge URL/Enter, explicit display-only LGT source and normal E/.50 commit, real movement/J HP loss/native receipt and Shift; public ApplyCombatHit explicitly advances remaining enemies for room/warning/coin/RootV2 grouped-continuation diagnosis. No QA enemy spawn, teleport, manual Tick or time step. Same-process grouped restore, not disk/two-process persistence. Silent viewport, placeholder enemy art, all visual/art/audio acceptance pending."));
  Id(Report,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());Report->SetStringField(TEXT("run"),Run.ToString(EGuidFormats::Digits));Id(Report,TEXT("owner"),Owner);Id(Report,TEXT("light_instance"),Light);Id(Report,TEXT("restart_serial"),Restart);
  Report->SetNumberField(TEXT("normal_J_accepted_attack_count"),JAttacks.Num());Report->SetNumberField(TEXT("normal_J_native_hit_receipts"),JHitReceipts);Report->SetNumberField(TEXT("normal_J_actual_knight_HP_loss"),JActualHPLoss);Report->SetBoolField(TEXT("native_Shift_dodge_observed"),DodgeObserved);
  Report->SetBoolField(TEXT("game_tick_called_manually"),false);Report->SetBoolField(TEXT("silent_video"),true);Report->SetBoolField(TEXT("audio_recorded"),false);Report->SetBoolField(TEXT("visual_reviewed"),false);Report->SetNumberField(TEXT("formal_complete_units"),0);
  Report->SetBoolField(TEXT("native_async_capture_requested"),true);Report->SetBoolField(TEXT("native_async_capture_writes_flushed"),Flushed);Report->SetBoolField(TEXT("capture_stop_before_flush"),true);Report->SetNumberField(TEXT("flush_completed_monotonic_s"),FPlatformTime::Seconds());
  Report->SetArrayField(TEXT("normal_input_requests"),Inputs);Report->SetArrayField(TEXT("steps"),Steps);Report->SetArrayField(TEXT("observations"),Observations);Report->SetArrayField(TEXT("diagnostic_public_hits"),DiagnosticHits);Report->SetArrayField(TEXT("codec_files"),CodecFiles);
  auto T=MakeShared<FJsonObject>();T->SetNumberField(TEXT("capture_start_monotonic_s"),Start);T->SetNumberField(TEXT("capture_stop_monotonic_s"),Stop);T->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());T->SetArrayField(TEXT("frame_wall_offsets_s"),Offsets);Report->SetObjectField(TEXT("capture_timing"),T);Report->SetNumberField(TEXT("duration_s"),Capturing?Stop-Start:0.);
  if(Prepared.IsReady())Prepared=FDungeonPreparedRun();FString Text;auto W=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Report.ToSharedRef(),W);
  const FString Path=Directory/TEXT("runtime-report.json");const bool Written=!Directory.IsEmpty()&&!IFileManager::Get().FileExists(*Path)&&FFileHelper::SaveStringToFile(Text,*Path,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
  if(!Why.IsEmpty())UE_LOG(LogTemp,Error,TEXT("Guard room diagnostic: %s"),*Why);
  FPlatformMisc::RequestExitWithStatus(false,Why.IsEmpty()&&Complete&&Written&&Flushed&&!Observations.IsEmpty()?0:3);
 }
 bool Need(bool V,const FString& Why){if(!V)Finish(Why);return V;}
 ADungeonFighter* Enemy(uint64 Id)const{if(auto G=Game.Get())for(auto E:G->Enemies)if(IsValid(E)&&E->GetRuntimeEntityId()==Id)return E.Get();return nullptr;}
 bool MoveTo(FVector2D Target)
 {
  const auto P=Game->PlayerFighter->GetGroundPosition();const bool Y=FMath::Abs(Target.Y-P.Y)>8.;const bool X=!Y&&FMath::Abs(Target.X-P.X)>8.;
  Key(EKeys::W,Y&&Target.Y>P.Y);Key(EKeys::S,Y&&Target.Y<P.Y);Key(EKeys::D,X&&Target.X>P.X);Key(EKeys::A,X&&Target.X<P.X);return !X&&!Y;
 }
 bool Pickup(int32 Slot)
 {
  FDungeonFirstBatchGuardRoomView P;if(!Game->QueryFirstBatchGuardRoom(P)||!P.Slots.IsValidIndex(Slot))return false;const auto R=Game->CaptureRunRewardsSnapshot();const uint64 Id=P.Slots[Slot].CoinObjectId;
  const auto* O=R.Objects.FindByPredicate([Id](const auto& V){return V.ObjectId==Id;});if(!O)return false;
  if(O->Consumed){MoveStop();return true;}MoveTo(O->Position);return false;
 }
 bool SaveCodec(const TCHAR* Name,TArray<uint8>* Keep=nullptr,FDungeonRunSnapshot* KeepState=nullptr)
 {
  FDungeonRunSnapshot S;TArray<uint8> B;FString Why;
  if(!Need(Game->CaptureRunSnapshot(S,Why)&&S.Schema==2&&S.Rewards.Schema==2&&DungeonRunSnapshotCodec::Encode(S,B,Why),TEXT("Actual RootV2 completed-boundary capture/encode: ")+Why))return false;
  const FString Path=Directory/Name;if(!Need(!IFileManager::Get().FileExists(*Path)&&FFileHelper::SaveArrayToFile(B,*Path),TEXT("Refuse missing/overwritten Codec evidence")))return false;
  TArray<uint8> Read;if(!Need(FFileHelper::LoadFileToArray(Read,*Path)&&Read==B,TEXT("Codec evidence readback differs")))return false;
  auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("file"),Name);O->SetNumberField(TEXT("bytes"),B.Num());O->SetStringField(TEXT("sha256"),DungeonSaveGenerationStore::FGenerationStore::Sha256(B));
  O->SetNumberField(TEXT("root_schema"),S.Schema);O->SetNumberField(TEXT("reward_schema"),S.Rewards.Schema);TArray<TSharedPtr<FJsonValue>> Guards;
  for(const auto& F:S.Fighters)if(F.Guard.IsSet()){auto X=MakeShared<FJsonObject>();Id(X,TEXT("entity"),F.EntityId);X->SetNumberField(TEXT("inner_owner_schema"),F.Guard.GetValue().Schema);X->SetBoolField(TEXT("reported"),F.DeathReported);X->SetBoolField(TEXT("claimed"),F.Guard.GetValue().Kernel.RewardClaimed);Guards.Add(MakeShared<FJsonValueObject>(X));}O->SetArrayField(TEXT("guard_owners"),Guards);CodecFiles.Add(MakeShared<FJsonValueObject>(O));
  if(Keep)*Keep=B;if(KeepState)*KeepState=S;return true;
 }
 bool DiagnosticKill(ADungeonFighter* E)
 {
  if(!Need(E&&Game->PlayerFighter&&!Game->bGameOver,TEXT("Diagnostic target/source absent")))return false;if(E->bDead)return true;
  if(!E->CanReceiveDirectHit())return false;auto O=MakeShared<FJsonObject>();Id(O,TEXT("target_id"),E->GetRuntimeEntityId());O->SetStringField(TEXT("content_id"),E->EnemyContentId);
  O->SetStringField(TEXT("api"),TEXT("ADungeonFighter::ApplyCombatHit"));O->SetNumberField(TEXT("sim"),Game->GetSimulationTime());O->SetNumberField(TEXT("requested_damage"),100000.);O->SetNumberField(TEXT("before_HP"),E->Health);
  E->ApplyCombatHit(100000.f,Game->PlayerFighter,85.f);O->SetNumberField(TEXT("after_HP"),E->Health);O->SetBoolField(TEXT("dead"),E->bDead);DiagnosticHits.Add(MakeShared<FJsonValueObject>(O));
  return Need(E->bDead,TEXT("Public diagnostic hit was not accepted; never force HP/death"));
 }
 JO Facts()
 {
  auto O=MakeShared<FJsonObject>();auto G=Game.Get();auto H=HUD.Get();auto P=G?G->PlayerFighter.Get():nullptr;if(!G||!H||!P)return O;
  O->SetStringField(TEXT("phase"),Name(Phase));O->SetNumberField(TEXT("sim"),G->GetSimulationTime());O->SetArrayField(TEXT("player_ground"),XY(P->GetGroundPosition()));O->SetNumberField(TEXT("player_HP"),P->Health);O->SetNumberField(TEXT("wallet"),P->Coins);Id(O,TEXT("gate"),uint64(G->GetRunInstallGate()));O->SetBoolField(TEXT("room_cleared"),G->bRoomCleared);
  O->SetNumberField(TEXT("native_dodge_phase"),uint64(P->GetDodgeState().Phase));O->SetBoolField(TEXT("native_melee_active"),P->GetMeleeCombatState().Action.Active);Id(O,TEXT("native_melee_attack"),P->GetMeleeCombatState().Action.AttackId);
  const auto& D=H->GetFairytaleSwordDraw();Id(O,TEXT("draw_id"),D.DrawId);O->SetStringField(TEXT("hero_clip"),D.Clip);O->SetNumberField(TEXT("hero_canvas_size"),D.CanvasSize);O->SetNumberField(TEXT("rendered_player_size"),H->GetRenderedPlayerSpriteSize());O->SetBoolField(TEXT("hero_bound_skin"),D.EquipmentBindingValid);O->SetBoolField(TEXT("LGT_drawn"),D.ArmorDrawn);O->SetBoolField(TEXT("interface_visible"),H->GetInterfaceVisible());O->SetNumberField(TEXT("text_calls"),H->GetRenderedTextDrawCalls());
  O->SetBoolField(TEXT("special_hero_presenter_active"),D.Active);O->SetBoolField(TEXT("hero_action_pose_supported"),D.ActionPoseSupported);O->SetStringField(TEXT("actual_rendered_player_texture"),H->GetRenderedPlayerTexturePath());
  TArray<TSharedPtr<FJsonValue>> ActualStack;for(const auto& Path:H->GetRenderedPlayerDrawStack())ActualStack.Add(MakeShared<FJsonValueString>(Path));O->SetArrayField(TEXT("actual_rendered_player_stack"),ActualStack);
  TArray<TSharedPtr<FJsonValue>> Warning,Slots,Enemies;for(const auto& S:H->GetRenderedGuardRoomWarningSlots())Warning.Add(MakeShared<FJsonValueString>(S));O->SetArrayField(TEXT("rendered_warning_slots"),Warning);
  FDungeonFirstBatchGuardRoomView Plan;if(G->QueryFirstBatchGuardRoom(Plan))for(int32 I=0;I<Plan.Slots.Num();++I)
  {
   const auto& S=Plan.Slots[I];auto X=MakeShared<FJsonObject>();X->SetStringField(TEXT("slot"),S.SlotId);X->SetStringField(TEXT("content"),S.ContentId);Id(X,TEXT("stage"),uint64(S.Stage));Id(X,TEXT("entity"),S.EntityId);Id(X,TEXT("coin"),S.CoinObjectId);X->SetNumberField(TEXT("share"),S.Coins);X->SetArrayField(TEXT("spawn"),XY(S.SpawnPosition));X->SetNumberField(TEXT("warning_at"),S.WarningAt);X->SetNumberField(TEXT("materialized_at"),S.MaterializedAt);X->SetNumberField(TEXT("dead_at"),S.DeadAt);X->SetNumberField(TEXT("visibility"),H->GetCurrentVisibilityAt(S.SpawnPosition));Slots.Add(MakeShared<FJsonValueObject>(X));
   if(I<3&&S.Stage==EDungeonGuardRoomSlotStage::Warning&&H->GetRenderedGuardRoomWarningSlots().Contains(S.SlotId))++WarningFrames[I];
   if(auto E=Enemy(S.EntityId))
   {auto A=MakeShared<FJsonObject>();Id(A,TEXT("entity"),S.EntityId);A->SetStringField(TEXT("content"),E->EnemyContentId);A->SetNumberField(TEXT("HP"),E->Health);A->SetArrayField(TEXT("ground"),XY(E->GetGroundPosition()));A->SetBoolField(TEXT("dead"),E->bDead);A->SetBoolField(TEXT("reported"),E->bDeathReported);A->SetNumberField(TEXT("drawn_size"),H->GetRenderedActorSpriteSize(E));
    if(auto V=E->GetStoneKnightDriver()){A->SetStringField(TEXT("native_driver"),TEXT("StoneKnight"));A->SetNumberField(TEXT("native_time"),V->State().Time);A->SetBoolField(TEXT("claimed"),V->State().RewardClaimed);}
    if(auto V=E->GetStoneBatDriver()){A->SetStringField(TEXT("native_driver"),TEXT("StoneBat"));A->SetNumberField(TEXT("native_time"),V->State().Time);A->SetNumberField(TEXT("initial_time"),V->State().InitialTime);A->SetBoolField(TEXT("claimed"),V->State().RewardClaimed);}
    if(auto V=E->GetStoneGuardDriver()){A->SetStringField(TEXT("native_driver"),TEXT("StoneGuard"));A->SetNumberField(TEXT("native_time"),V->State().Time);A->SetNumberField(TEXT("initial_time"),V->State().InitialTime);A->SetBoolField(TEXT("claimed"),V->State().RewardClaimed);}
    const bool Drawn=E->GetStoneGuardDriver()?H->GetRenderedNativeGuardEntityIds().Contains(S.EntityId):H->GetRenderedActorSpriteSize(E)>0.;A->SetBoolField(TEXT("actual_draw_recorded"),Drawn);
    Enemies.Add(MakeShared<FJsonValueObject>(A));if(I<3&&!E->bDead&&Drawn)++BornFrames[I];}
  }
  O->SetArrayField(TEXT("slots"),Slots);O->SetArrayField(TEXT("enemies"),Enemies);const auto R=G->CaptureRunRewardsSnapshot();O->SetNumberField(TEXT("death_count"),R.Deaths.Num());O->SetNumberField(TEXT("coin_objects"),R.Objects.Num());O->SetNumberField(TEXT("collections"),R.Collections.Num());
  TArray<TSharedPtr<FJsonValue>> Coins;for(const auto& V:R.Objects){auto X=MakeShared<FJsonObject>();Id(X,TEXT("id"),V.ObjectId);X->SetNumberField(TEXT("amount"),V.ResolvedAmount);X->SetBoolField(TEXT("consumed"),V.Consumed);X->SetArrayField(TEXT("ground"),XY(V.Position));Coins.Add(MakeShared<FJsonValueObject>(X));}O->SetArrayField(TEXT("coins"),Coins);return O;
 }
 void Observe()
 {
  if(Stopped||Manual)return;if(Prewarm&&!Capturing){if(!Need(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))>8,TEXT("Actual prewarm missing")))return;Start=PhaseWall=FPlatformTime::Seconds();Capturing=true;GIsDumpingMovie=-1;return;}if(!Capturing)return;
  const double Offset=FPlatformTime::Seconds()-Start;auto O=Facts();O->SetNumberField(TEXT("wall_offset_s"),Offset);Observations.Add(MakeShared<FJsonValueObject>(O));Offsets.Add(MakeShared<FJsonValueNumber>(Offset));
  if(auto H=HUD.Get())if(!Need(!H->GetInterfaceVisible()&&H->GetRenderedTextDrawCalls()==0,TEXT("Hidden-HUD proof rendered UI text")))return;
  if(FinishOnFrame)Finish();
 }
 bool Birth(int32 I)
 {
  FDungeonFirstBatchGuardRoomView P;if(!Game->QueryFirstBatchGuardRoom(P)||P.Slots.Num()!=3)return false;const auto& S=P.Slots[I];
  if(S.Stage==EDungeonGuardRoomSlotStage::Warning&&!WarningSaved[I])
  {if(!SaveCodec(I==1?TEXT("bat-warning-root-v2-codec.json"):TEXT("guard-warning-root-v2-codec.json")))return false;WarningSaved[I]=true;}
  if(S.Stage!=EDungeonGuardRoomSlotStage::Materialized)return false;auto E=Enemy(S.EntityId);
  return Need(WarningFrames[I]>=2&&S.WarningAt>=P.Slots[I-1].DeadAt+2.&&S.MaterializedAt>=S.WarningAt+1.2&&E&&!E->bDead
   &&(I==1?bool(E->GetStoneBatDriver()):bool(E->GetStoneGuardDriver())),TEXT("Birth lacks true predecessor/full visible warning/native actor"));
 }
 void Tick(ADungeonGuardRoomFlowProbe& Actor)
 {
  if(Stopped)return;const double Now=FPlatformTime::Seconds();auto G=Actor.GetWorld()->GetAuthGameMode<ADungeonGameMode>();auto C=UGameplayStatics::GetPlayerController(&Actor,0);auto H=C?Cast<ADungeonHUD>(C->GetHUD()):nullptr;
  if(!Game.IsValid()&&G&&C&&C->PlayerInput&&H){Game=G;Controller=C;HUD=H;Actor.AddTickPrerequisiteActor(G);Actor.AddTickPrerequisiteActor(H);return;}
  if(!Game.IsValid())return;auto P=G->PlayerFighter.Get();if(Manual)
  {if(P&&G->GetEquipmentView().Bound){FDungeonFirstBatchGuardRoomView Room;if(!G->QueryFirstBatchGuardRoom(Room))return;if(!ManualDone||Room.RunGuid!=Run){DungeonEquipmentInventory::FItem Item;Item.ContentId="ARM-LGT-001";const auto R=G->RegisterEquipmentSource(TEXT("display.guardroom.manual.light.v001"),Item,P->GetGroundPosition()+FVector2D(24.,0.),true);ManualDone=R.Ok();if(ManualDone)Run=Room.RunGuid;}}return;}
  if(PulseKey.IsValid()&&Now>=ReleaseAt){Key(PulseKey,false);PulseKey=FKey();NeutralUntil=Now+.04;}
  if(!Capturing){if(!Prewarm&&Now-Warm>=2.){Prewarm=true;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}else if(Now-Warm>18.)Finish(TEXT("Prewarm timeout"));return;}
  if(!Need(Now-Start<75.&&Now-PhaseWall<15.,FString(TEXT("Actual room/input phase timeout: "))+Name(Phase)))return;if(FinishOnFrame)return;
  if(!Need(G==Game.Get()&&C==Controller.Get()&&H==HUD.Get()&&P&&C->GetPawn()==P&&!P->bDead&&!G->bGameOver,TEXT("Actual native world/player failed")))return;
  FDungeonFirstBatchGuardRoomView Room;if(!Need(G->QueryFirstBatchGuardRoom(Room)&&Room.Slots.Num()==3&&G->GetEquipmentView().Config==EDungeonEquipmentRunConfig::FirstBatch,TEXT("Normal URL did not start finite Bridge")))return;
  for(int32 I=1;I<3;++I)if(Room.Slots[I].Stage==EDungeonGuardRoomSlotStage::Warning&&!WarningSaved[I])
  {if(!SaveCodec(I==1?TEXT("bat-warning-root-v2-codec.json"):TEXT("guard-warning-root-v2-codec.json")))return;WarningSaved[I]=true;}
  if(!Run.IsValid()){Run=Room.RunGuid;Owner=G->GetEquipmentView().OwnerId;Restart=G->GetRunRestartSerial();KnightId=Room.Slots[0].EntityId;}
  if(!Need(Room.RunGuid==Run&&G->GetRunRestartSerial()==Restart,TEXT("Native Run restarted instead of continued")))return;
  auto K=Enemy(KnightId);const auto& A=P->GetMeleeCombatState().Action;
  if(Phase==4||Phase==5){if(A.Active)JAttacks.Add(A.AttackId);JHitReceipts=0;for(const auto& X:P->GetMeleeCombatState().HitReceipts)if(X.TargetId==KnightId)++JHitReceipts;JActualHPLoss=K?JInitialHP-K->Health:0.;DodgeObserved|=P->GetDodgeState().Phase==DungeonDodge::EPhase::Dodging;}
  switch(Phase)
  {
  case 0:if(!Need(G->bWaitingForStart&&G->GetSimulationTime()==0.&&P->Coins==20,TEXT("Normal Bridge must wait at true new Run0/20")))return;if(Pulse(EKeys::Enter))Next(1);break;
  case 1:if(!G->bWaitingForStart&&CanPulse())
   {DungeonEquipmentInventory::FItem Item;Item.ContentId="ARM-LGT-001";const auto R=G->RegisterEquipmentSource(TEXT("display.guardroom.proof.light.v001"),Item,P->GetGroundPosition()+FVector2D(24.,0.),true);if(!Need(R.Ok()&&!R.Replayed,TEXT("Explicit display LGT source failed")))return;Light=R.InstanceId;Pulse(EKeys::E);Next(2);}break;
  case 2:if(!G->GetEquipmentView().Action.Active&&G->GetEquipmentView().Slots[2].InstanceId==Light&&CanPulse()){if(!SaveCodec(TEXT("entered-root-v2-codec.json")))return;Next(3);}break;
  case 3:if(!Need(K&&!K->bDead,TEXT("Initial normal Knight absent")))return;
   if(MoveTo(K->GetGroundPosition()+FVector2D(P->GetGroundPosition().X<K->GetGroundPosition().X?-90.:90.,0.)))
   {JInitialHP=K->Health;InitialDodge=P->GetDodgeState().NextActionId;Next(4);}break;
  case 4:if(Now-PhaseWall<2.2){if(P->CanStartAttack())Pulse(EKeys::J);}else{MoveStop();Next(5);}break;
  case 5:
   if(P->GetDodgeState().NextActionId==InitialDodge&&!A.Active&&P->CanStartAttack()&&CanPulse()){Key(P->Facing>0?EKeys::A:EKeys::D,true);Pulse(EKeys::LeftShift);}
   if(DodgeObserved&&P->GetDodgeState().Phase==DungeonDodge::EPhase::Idle&&P->GetDodgeState().NextActionId>InitialDodge){MoveStop();if(!Need(JAttacks.Num()>0&&JHitReceipts>0&&JActualHPLoss>0.,TEXT("Real J must have accepted native receipt and positive HP loss before diagnostic hit")))return;Next(6);}break;
  case 6:if(CanPulse()&&DiagnosticKill(K))Next(7);break;
  case 7:if(K&&K->bDead&&K->bDeathReported){if(!Need(!G->bRoomCleared&&G->CaptureRunRewardsSnapshot().Objects.Num()==1,TEXT("Future slots cleared early or Knight ground reward missing")))return;Next(8);}break;
  case 8:if(Pickup(0))Next(9);break;
  case 9:if(Birth(1))Next(10);break;
  case 10:if(Now-PhaseWall>=.9&&BornFrames[1]>=2&&DiagnosticKill(Enemy(Room.Slots[1].EntityId)))Next(11);break;
  case 11:if(Room.Slots[1].Stage==EDungeonGuardRoomSlotStage::Dead&&Pickup(1))Next(12);break;
  case 12:if(Birth(2))Next(13);break;
  case 13:if(Now-PhaseWall>=.9&&BornFrames[2]>=2&&DiagnosticKill(Enemy(Room.Slots[2].EntityId)))Next(14);break;
  case 14:if(Room.Slots[2].Stage==EDungeonGuardRoomSlotStage::Dead&&G->bRoomCleared){if(!SaveCodec(TEXT("guard-settled-root-v2-codec.json")))return;Next(15);}break;
  case 15:if(Pickup(2)&&CanPulse())
   {MoveStop();if(!Need(P->Coins==40&&G->CaptureRunRewardsSnapshot().Collections.Num()==3,TEXT("Physical pickup wallet/history differs")))return;
    if(!SaveCodec(TEXT("after-pickup-root-v2-codec.json"),&SavedBytes,&Saved))return;FDungeonValidatedRun V;FString Why;
    if(!Need(DungeonRunSnapshotCodec::Decode(SavedBytes,V,Why)&&FDungeonRunInstaller::Prepare(*G,V,Prepared,Why)&&FDungeonRunInstaller::Install(*G,Prepared,Why),TEXT("True native RootV2 grouped restore failed: ")+Why))return;PauseWall=Now;Next(16);}break;
  case 16:
   if(!Need(G->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue&&G->GetSimulationTime()==Saved.SimulationTime&&P->Coins==40,TEXT("Grouped restore did not stay paused at saved wallet/time")))return;
   if(Now-PauseWall>=.6&&CanPulse())
   {TArray<uint8> Installed;if(!SaveCodec(TEXT("installed-root-v2-codec.json"),&Installed)||!Need(Installed==SavedBytes,TEXT("Installed whole Codec differs from saved RootV2")))return;Pulse(EKeys::Enter);Next(17);}break;
  case 17:if(G->GetRunInstallGate()==EDungeonRunInstallGate::Open&&G->GetSimulationTime()>Saved.SimulationTime+.3)
   {const auto R=G->CaptureRunRewardsSnapshot();if(!Need(P->Coins==40&&R.Deaths.Num()==3&&R.Objects.Num()==3&&R.Collections.Num()==3&&G->bRoomCleared,TEXT("Resume duplicated death/coin or lost full clear")))return;Complete=true;Next(18);FinishOnFrame=true;}break;
  default:Finish(TEXT("Unknown native diagnostic phase"));break;
  }
 }
};
void FDungeonGuardRoomFlowDeleter::operator()(FDungeonGuardRoomFlowState* P)const{delete P;}
ADungeonGuardRoomFlowProbe::ADungeonGuardRoomFlowProbe(){PrimaryActorTick.bCanEverTick=true;}
ADungeonGuardRoomFlowProbe::~ADungeonGuardRoomFlowProbe()=default;
void ADungeonGuardRoomFlowProbe::BeginPlay()
{
 Super::BeginPlay();Proof.Reset(new FDungeonGuardRoomFlowState());Proof->Warm=FPlatformTime::Seconds();Proof->Manual=FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardRoomManualLightSource"));
 if(Proof->Manual)return;GIsDumpingMovie=0;FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),Proof->Directory);
 if(Proof->Directory.IsEmpty()||FPaths::IsRelative(Proof->Directory)){Proof->Directory.Reset();Proof->Finish(TEXT("Absolute unused evidence directory required"));return;}
 Proof->Directory=FPaths::ConvertRelativePathToFull(Proof->Directory);FPaths::NormalizeDirectoryName(Proof->Directory);TArray<FString> Prior;IFileManager::Get().FindFiles(Prior,*(Proof->Directory/TEXT("MovieFrame*.png")),true,false);
 if(Prior.Num()||IFileManager::Get().FileExists(*(Proof->Directory/TEXT("runtime-report.json")))||IFileManager::Get().FileExists(*(Proof->Directory/TEXT("prewarm-viewport.png")))){Proof->Stopped=true;FPlatformMisc::RequestExitWithStatus(false,3);return;}
 IFileManager::Get().MakeDirectory(*Proof->Directory,true);
 for(const TCHAR* Flag:{TEXT("DungeonGuardRoomFlowProof"),TEXT("DungeonContentProof"),TEXT("DungeonFastLosslessCapture"),TEXT("DungeonAsyncLosslessCapture"),TEXT("DungeonFairytaleSwordWalkPreview"),TEXT("DungeonFairytaleSwordEquipmentBoundPreview")})if(!Proof->Need(FParse::Param(FCommandLine::Get(),Flag),FString(TEXT("Missing explicit flag: "))+Flag))return;
 if(!Proof->Need(!FApp::UseFixedTimeStep(),TEXT("Ordinary native pacing required")))return;GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Proof->Directory;
 FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonGuardRoomFlowProbe::ScreenshotProcessed);
}
void ADungeonGuardRoomFlowProbe::ScreenshotProcessed(){if(Proof)Proof->Observe();}
void ADungeonGuardRoomFlowProbe::Tick(float D){Super::Tick(D);if(Proof)Proof->Tick(*this);}
void ADungeonGuardRoomFlowProbe::EndPlay(const EEndPlayReason::Type R)
{FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);if(Proof&&!Proof->Stopped&&!Proof->Manual)Proof->Finish(TEXT("Native world ended before diagnostic finished"));Super::EndPlay(R);}
