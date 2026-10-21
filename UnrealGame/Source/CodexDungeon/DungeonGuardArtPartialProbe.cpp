#include "DungeonGuardArtPartialProbe.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonHUD.h"
#include "DungeonStoneBatDriver.h"
#include "DungeonStoneGuardDriver.h"
#include "DungeonFairytaleGuardProfile.h"
#include "DungeonRoomLayout.h"
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
TArray<TSharedPtr<FJsonValue>> Strings(const TArray<FString>& A)
{TArray<TSharedPtr<FJsonValue>> R;for(const auto& S:A)R.Add(MakeShared<FJsonValueString>(S));return R;}
const TCHAR* PhaseName(int32 P)
{static const TCHAR* N[]={TEXT("normal_Enter"),TEXT("display_LGT_normal_E"),TEXT("normal_LGT_commit"),TEXT("diagnostic_Knight"),TEXT("plan_Bat_birth"),TEXT("diagnostic_Bat"),TEXT("plan_Guard_birth"),TEXT("Guard_Dormant_observe"),TEXT("normal_guard_approach_and_cycles"),TEXT("complete")};return P>=0&&P<UE_ARRAY_COUNT(N)?N[P]:TEXT("invalid");}
JO SerializeDraw(const FDungeonFairytaleGuardDraw& D)
{
 auto O=MakeShared<FJsonObject>();const auto& S=D.Selection;
 Id(O,TEXT("DrawId"),D.DrawId);Id(O,TEXT("EntityId"),D.EntityId);
 auto Q=MakeShared<FJsonObject>();Q->SetBoolField(TEXT("Valid"),S.Valid);Q->SetBoolField(TEXT("MaterialHit"),S.MaterialHit);Q->SetBoolField(TEXT("TerminalPresentation"),S.TerminalPresentation);
 Q->SetStringField(TEXT("Clip"),UTF8_TO_TCHAR(DungeonFairytaleGuard::ClipName(S.Clip)));Q->SetNumberField(TEXT("Frame"),S.Frame);Q->SetNumberField(TEXT("Facing"),S.Facing);
 Id(Q,TEXT("EntityId"),S.EntityId);Id(Q,TEXT("AttackId"),S.AttackId);Id(Q,TEXT("SourceEventId"),S.SourceEventId);Id(Q,TEXT("MaterialEventId"),S.MaterialEventId);Q->SetNumberField(TEXT("Phase"),int32(S.Phase));
 Q->SetNumberField(TEXT("SampleTime"),S.SampleTime);Q->SetNumberField(TEXT("IntervalStart"),S.IntervalStart);Q->SetNumberField(TEXT("IntervalEnd"),S.IntervalEnd);Q->SetNumberField(TEXT("AcceptedDistance"),S.AcceptedDistance);Q->SetNumberField(TEXT("DistancePhase"),S.DistancePhase);O->SetObjectField(TEXT("Selection"),Q);
 O->SetBoolField(TEXT("OptIn"),D.OptIn);O->SetBoolField(TEXT("TrialAllowed"),D.TrialAllowed);O->SetBoolField(TEXT("FinalAccepted"),D.FinalAccepted);O->SetBoolField(TEXT("RegistrationReady"),D.RegistrationReady);O->SetBoolField(TEXT("TextureReady"),D.TextureReady);O->SetBoolField(TEXT("Drawn"),D.Drawn);O->SetBoolField(TEXT("ProceduralFallback"),D.ProceduralFallback);O->SetBoolField(TEXT("WholebodyIncludesAxe"),D.WholebodyIncludesAxe);
 O->SetNumberField(TEXT("NativeSourceId"),D.NativeSourceId);O->SetNumberField(TEXT("AssetFrame"),D.AssetFrame);O->SetStringField(TEXT("AssetClip"),D.AssetClip);O->SetStringField(TEXT("TexturePath"),D.TexturePath);O->SetStringField(TEXT("SourceSHA256"),D.SourceSHA256);O->SetStringField(TEXT("TrialApprovalRecord"),D.TrialApprovalRecord);O->SetStringField(TEXT("RegistrationEvidenceSHA256"),D.RegistrationEvidenceSHA256);O->SetStringField(TEXT("MissingReason"),D.MissingReason);
 O->SetNumberField(TEXT("StandingExtent"),D.StandingExtent);O->SetNumberField(TEXT("TargetBodyHeight"),D.TargetBodyHeight);O->SetNumberField(TEXT("RowScale"),D.RowScale);O->SetNumberField(TEXT("CanvasSize"),D.CanvasSize);O->SetArrayField(TEXT("SourceFloorPivot"),XY(D.SourceFloorPivot));O->SetArrayField(TEXT("GroundScreen"),XY(D.GroundScreen));O->SetArrayField(TEXT("TopScreen"),XY(D.TopScreen));O->SetArrayField(TEXT("DrawStack"),Strings(D.DrawStack));return O;
}
}
struct FDungeonGuardArtPartialState
{
 FString Directory;bool Stopped=false,Prewarm=false,Capturing=false,FinishOnFrame=false,Complete=false;
 TWeakObjectPtr<ADungeonGameMode> Game;TWeakObjectPtr<APlayerController> Controller;TWeakObjectPtr<ADungeonHUD> HUD;
 TMap<FKey,bool> Keys;FKey PulseKey;double ReleaseAt=0.,NeutralUntil=0.,Warm=0.,Start=0.,Stop=0.,PhaseWall=0.;int32 Phase=0,RequestedSide=0,ApproachSide=0;
 FGuid Run;uint64 Owner=0,Restart=0,Light=0,GuardId=0,LastGuardDraw=0;
 uint32 WakeMask=0,ReadyMask=0,WindupMask=0;int32 DormantSeen=0,GuardDrawCount=0;bool GapSeen=false,GuardWasAlreadyWaking=false;
 bool RoutePlanned=false,RouteReached=false;int32 RouteStage=0;double RouteLaneY=0.,RouteStartedWall=0.,FirstReachedSim=-1.;
 FVector2D RouteStartPlayer=FVector2D::ZeroVector,RouteStartGuard=FVector2D::ZeroVector,FirstReachedPlayer=FVector2D::ZeroVector,FirstReachedGuard=FVector2D::ZeroVector;
 JO Report=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Inputs,Steps,Observations,Offsets,DiagnosticHits,RouteWitnesses;
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
 {Phase=P;PhaseWall=FPlatformTime::Seconds();auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("phase"),PhaseName(P));O->SetNumberField(TEXT("wall_offset_s"),PhaseWall-Start);O->SetNumberField(TEXT("sim"),Game->GetSimulationTime());Steps.Add(MakeShared<FJsonValueObject>(O));}
 ADungeonFighter* Enemy(uint64 Id)const{if(auto G=Game.Get())for(auto E:G->Enemies)if(IsValid(E)&&E->GetRuntimeEntityId()==Id)return E.Get();return nullptr;}
 bool AtStrictApproach()const
 {
  auto G=Game.Get();auto E=Enemy(GuardId);if(!G||!G->PlayerFighter||!E||!ApproachSide)return false;
  const auto D=G->PlayerFighter->GetGroundPosition()-E->GetGroundPosition();const double SignedX=D.X*ApproachSide;
  return SignedX>=120.&&SignedX<=180.&&D.Size()<=180.&&FMath::Abs(D.Y)<=12.;
 }
 bool SpatialCredit(const DungeonFairytaleGuard::FSelection& Selection)const
 {
  using C=DungeonFairytaleGuard::EClip;
  if(Selection.Clip==C::Wake||Selection.Clip==C::Dormant)return true;
  if(!RouteReached||Phase!=8||Selection.Facing!=ApproachSide)return false;
  if(Selection.Clip==C::Ready)return AtStrictApproach();
  if(Selection.Clip!=C::AxeWindup)return false;
  if(AtStrictApproach())return true;
  if(Selection.Frame<3)return false;
  const auto E=Enemy(GuardId);if(!E||!E->GetStoneGuardDriver()||!Game.IsValid()||!Game->PlayerFighter)return false;
  const auto& S=E->GetStoneGuardDriver()->State();const auto D=Game->PlayerFighter->GetGroundPosition()-E->GetGroundPosition();
  return S.Phase==DungeonStoneGuard::EPhase::Windup&&S.Action.Kind==DungeonStoneGuard::EAttack::AxeSweep
   &&S.Action.Locked&&Selection.AttackId==S.Action.AttackId&&Selection.SampleTime>=S.Action.LockAt
   &&D.X*ApproachSide>=120.&&D.X*ApproachSide<=180.; // Real post-lock Y evade, never wrong-side credit.
 }
 JO SpatialFacts()const
 {
  auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("requested_side"),RequestedSide);O->SetNumberField(TEXT("selected_side"),ApproachSide);
  O->SetBoolField(TEXT("route_planned"),RoutePlanned);O->SetBoolField(TEXT("route_reached"),RouteReached);O->SetNumberField(TEXT("route_stage"),RouteStage);
  O->SetNumberField(TEXT("lane_y"),RouteLaneY);O->SetNumberField(TEXT("first_reached_sim"),FirstReachedSim);
  O->SetArrayField(TEXT("route_start_player"),XY(RouteStartPlayer));O->SetArrayField(TEXT("route_start_guard"),XY(RouteStartGuard));
  O->SetArrayField(TEXT("first_reached_player"),XY(FirstReachedPlayer));O->SetArrayField(TEXT("first_reached_guard"),XY(FirstReachedGuard));
  if(auto G=Game.Get())if(G->PlayerFighter)if(auto E=Enemy(GuardId))
  {
   const auto P=G->PlayerFighter->GetGroundPosition(),V=E->GetGroundPosition(),D=P-V;
   O->SetArrayField(TEXT("player"),XY(P));O->SetArrayField(TEXT("guard"),XY(V));O->SetNumberField(TEXT("dx"),D.X);O->SetNumberField(TEXT("dy"),D.Y);
   O->SetNumberField(TEXT("signed_dx"),D.X*ApproachSide);O->SetNumberField(TEXT("distance"),D.Size());O->SetBoolField(TEXT("strict_point"),AtStrictApproach());O->SetNumberField(TEXT("player_HP"),G->PlayerFighter->Health);
  }
  return O;
 }
 bool PrepareRoute(ADungeonFighter* E)
 {
  const auto P=Game->PlayerFighter->GetGroundPosition(),V=E->GetGroundPosition();
  for(double Sign:{1.,-1.})
  {
   const double Lane=V.Y+Sign*140.;const FVector2D A(P.X,Lane),B(V.X+ApproachSide*150.,Lane),C(V.X+ApproachSide*150.,V.Y);
   if(!SegmentLegal(P,A)||!SegmentLegal(A,B)||!SegmentLegal(B,C))continue;
   RouteLaneY=Lane;RoutePlanned=true;RouteStage=0;RouteStartedWall=FPlatformTime::Seconds();RouteStartPlayer=P;RouteStartGuard=V;
   auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("event"),TEXT("normal_route_planned"));O->SetNumberField(TEXT("sim"),Game->GetSimulationTime());
   O->SetArrayField(TEXT("player"),XY(P));O->SetArrayField(TEXT("guard"),XY(V));O->SetArrayField(TEXT("outside_lane"),XY(A));O->SetArrayField(TEXT("side_lane"),XY(B));O->SetArrayField(TEXT("approach_point"),XY(C));RouteWitnesses.Add(MakeShared<FJsonValueObject>(O));return true;
  }
  return Need(false,TEXT("No legal body-aware outside140 route to requested side; never teleport"));
 }
 bool FollowRoute(ADungeonFighter* E)
 {
  if(RouteReached)return true;if(!RoutePlanned&&!PrepareRoute(E))return false;
  if(!Need(FPlatformTime::Seconds()-RouteStartedWall<8.,TEXT("Normal body-aware approach route timed out before actual side point")))return false;
  const auto P=Game->PlayerFighter->GetGroundPosition(),V=E->GetGroundPosition();
  FVector2D Target=RouteStage==0?FVector2D(P.X,RouteLaneY):RouteStage==1?FVector2D(V.X+ApproachSide*150.,RouteLaneY):FVector2D(V.X+ApproachSide*150.,V.Y);
  if(!MoveTo(Target))return false;
  auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("event"),TEXT("normal_route_waypoint_reached"));O->SetNumberField(TEXT("stage"),RouteStage);O->SetNumberField(TEXT("sim"),Game->GetSimulationTime());O->SetArrayField(TEXT("actual_player"),XY(P));O->SetArrayField(TEXT("actual_guard"),XY(V));RouteWitnesses.Add(MakeShared<FJsonValueObject>(O));
  if(++RouteStage<3)return false;
  if(!Need(AtStrictApproach(),TEXT("WASD route ended without actual signed120..180 / radius180 / dy12 approach point")))return false;
  RouteReached=true;FirstReachedSim=Game->GetSimulationTime();FirstReachedPlayer=P;FirstReachedGuard=V;MoveStop();return true;
 }

 bool Need(bool V,const FString& Why){if(!V)Finish(Why);return V;}
 void Finish(const FString& Why=FString())
 {
  if(Stopped)return;Stopped=true;Stop=FPlatformTime::Seconds();GIsDumpingMovie=0;
  TArray<FKey> Held;Keys.GetKeys(Held);for(FKey K:Held)Key(K,false);const bool Flushed=FlushFastLosslessProofScreenshots();
  const bool Passed=Why.IsEmpty()&&Complete&&Flushed&&!Observations.IsEmpty();
  Report->SetStringField(TEXT("schema"),TEXT("guard-art-partial-native-observer-v009"));Report->SetBoolField(TEXT("passed"),Passed);Report->SetBoolField(TEXT("flow_complete"),Complete);Report->SetStringField(TEXT("failure"),Why);
  Report->SetStringField(TEXT("scope"),TEXT("Formal FirstBatchGuardRoom URL and normal Enter/E/direction input. Knight/Bat are explicitly diagnostic public ApplyCombatHit clears, not normal full combat. Guard is born only by formal slot2 plan; no Guard spawn, damage API, teleport, manual Tick/StepTo/SetState or clock override. Actual opt-in partial wholebody209/210/212; missing rows remain explicit procedural gaps. Observed native flow is not final visual/art acceptance. Silent viewport, no captured audio."));
  Id(Report,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());Report->SetStringField(TEXT("run"),Run.ToString(EGuidFormats::Digits));Id(Report,TEXT("owner"),Owner);Id(Report,TEXT("guard_entity"),GuardId);Id(Report,TEXT("light_instance"),Light);Id(Report,TEXT("restart_serial"),Restart);
  Report->SetNumberField(TEXT("requested_approach_side"),RequestedSide);Report->SetNumberField(TEXT("actual_approach_side"),ApproachSide);Report->SetObjectField(TEXT("spatial_approach"),SpatialFacts());Report->SetArrayField(TEXT("route_witnesses"),RouteWitnesses);
  Report->SetStringField(TEXT("coverage_spatial_rule"),TEXT("Ready and AxeWindup0..2 require actual signedDx120..180/radius180/absDy12 after reached route; AxeWindup3..5 may evade in Y only after native lock while signedDx120..180; Wake/Dormant retain actual native facing."));
  Report->SetBoolField(TEXT("normal_J_full_clear"),false);Report->SetBoolField(TEXT("diagnostic_public_damage_used"),!DiagnosticHits.IsEmpty());Report->SetBoolField(TEXT("guard_public_damage_used"),false);Report->SetBoolField(TEXT("guard_spawned_by_probe"),false);
  Report->SetBoolField(TEXT("game_tick_called_manually"),false);Report->SetBoolField(TEXT("silent_video"),true);Report->SetBoolField(TEXT("audio_recorded"),false);Report->SetBoolField(TEXT("visual_reviewed"),false);Report->SetNumberField(TEXT("formal_complete_units"),0);
  Report->SetNumberField(TEXT("WakeMask"),WakeMask);Report->SetNumberField(TEXT("ReadyMask"),ReadyMask);Report->SetNumberField(TEXT("WindupMask"),WindupMask);Report->SetNumberField(TEXT("DormantSeen"),DormantSeen);Report->SetBoolField(TEXT("DormantUnobserved"),DormantSeen==0);Report->SetBoolField(TEXT("guard_already_waking_at_birth_observation"),GuardWasAlreadyWaking);Report->SetBoolField(TEXT("procedural_gap_seen"),GapSeen);
  Report->SetStringField(TEXT("action_contract_gap"),TEXT("New Axe Active4(.2)+Recovery4(1.4)=8 is outside frozen v001 partial presenter. No claim that old54/55 images or complete Guard are accepted."));
  Report->SetBoolField(TEXT("native_async_capture_requested"),true);Report->SetBoolField(TEXT("native_async_capture_writes_flushed"),Flushed);Report->SetBoolField(TEXT("capture_stop_before_flush"),true);Report->SetNumberField(TEXT("flush_completed_monotonic_s"),FPlatformTime::Seconds());
  Report->SetArrayField(TEXT("normal_input_requests"),Inputs);Report->SetArrayField(TEXT("steps"),Steps);Report->SetArrayField(TEXT("observations"),Observations);Report->SetArrayField(TEXT("diagnostic_public_hits"),DiagnosticHits);
  auto T=MakeShared<FJsonObject>();T->SetNumberField(TEXT("capture_start_monotonic_s"),Start);T->SetNumberField(TEXT("capture_stop_monotonic_s"),Stop);T->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());T->SetArrayField(TEXT("frame_wall_offsets_s"),Offsets);Report->SetObjectField(TEXT("capture_timing"),T);Report->SetNumberField(TEXT("duration_s"),Capturing?Stop-Start:0.);
  if(auto E=Enemy(GuardId))if(auto D=E->GetStoneGuardDriver())
  {
   const auto& S=D->State();TArray<TSharedPtr<FJsonValue>> Issued;
   for(const auto& V:S.Issued){auto X=MakeShared<FJsonObject>();Id(X,TEXT("EventId"),V.EventId);Id(X,TEXT("EntityId"),V.EntityId);X->SetNumberField(TEXT("Kind"),int32(V.Kind));X->SetNumberField(TEXT("AtTime"),V.AtTime);X->SetNumberField(TEXT("EndTime"),V.EndTime);X->SetNumberField(TEXT("Amount"),V.Amount);X->SetArrayField(TEXT("From"),XY({V.From.X,V.From.Y}));X->SetArrayField(TEXT("To"),XY({V.To.X,V.To.Y}));Id(X,TEXT("AttackId"),V.Action.AttackId);Issued.Add(MakeShared<FJsonValueObject>(X));}
   Report->SetArrayField(TEXT("guard_original_issued_events"),Issued);Report->SetNumberField(TEXT("guard_final_HP"),S.HP);Report->SetNumberField(TEXT("guard_incoming_receipt_count"),S.ReceivedHits.size());
  }
  FString Text;auto W=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Report.ToSharedRef(),W);
  const FString Path=Directory/TEXT("runtime-report.json");const bool Written=!Directory.IsEmpty()&&!IFileManager::Get().FileExists(*Path)&&FFileHelper::SaveStringToFile(Text,*Path,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
  if(!Why.IsEmpty())UE_LOG(LogTemp,Error,TEXT("Guard partial art: %s"),*Why);
  FPlatformMisc::RequestExitWithStatus(false,Passed&&Written?0:3);
 }
 bool LegalPoint(FVector2D V)const
 {
  const auto B=DungeonRoomLayout::ExplorationPreview().Barrier;
  const auto Half=Game->PlayerFighter->GetCombatBodyHalfExtent()+FVector2D(8.,8.);
  return DungeonRoomLayout::CenterBounds().IsInsideOrOn(V-Half)&&DungeonRoomLayout::CenterBounds().IsInsideOrOn(V+Half)
   &&!(V.X>=B.Min.X-Half.X&&V.X<=B.Max.X+Half.X&&V.Y>=B.Min.Y-Half.Y&&V.Y<=B.Max.Y+Half.Y);
 }
 bool SegmentLegal(FVector2D A,FVector2D B)const
 {
  const auto Barrier=DungeonRoomLayout::ExplorationPreview().Barrier;
  const auto Half=Game->PlayerFighter->GetCombatBodyHalfExtent()+FVector2D(8.,8.);
  const FBox2D Expanded(Barrier.Min-Half,Barrier.Max+Half);
  const FBox2D SegmentBox(FVector2D(FMath::Min(A.X,B.X),FMath::Min(A.Y,B.Y)),FVector2D(FMath::Max(A.X,B.X),FMath::Max(A.Y,B.Y)));
  if(!LegalPoint(A)||!LegalPoint(B)||Expanded.Intersect(SegmentBox))return false;
  // Planning uses the same real live body footprints plus8 clearance. Native
  // collision remains authoritative; this only prevents choosing a blocked Y-first leg.
  if(auto E=Enemy(GuardId))if(!E->bDead)
  {
   const auto V=E->GetGroundPosition();const auto Body=Game->PlayerFighter->GetCombatBodyHalfExtent()+E->GetCombatBodyHalfExtent()+FVector2D(8.,8.);
   if(FBox2D(V-Body,V+Body).Intersect(SegmentBox))return false;
  }
  return true;
 }
 bool MoveTo(FVector2D Target)
 {
  const auto P=Game->PlayerFighter->GetGroundPosition();if(!Need(LegalPoint(Target),TEXT("Requested normal-input waypoint is not legal floor")))return false;
  if((Target-P).GetAbsMax()<=6.){MoveStop();return true;}
  FVector2D Next=Target;
  // Crossing to an explicitly requested opposite facing goes around the real Guard body.
  // This only chooses normal input waypoints; physical resolution still owns all movement.
  if(auto E=Enemy(GuardId))
  {
   const auto V=E->GetGroundPosition();
   if((P.X-V.X)*(Target.X-V.X)<0.&&FMath::Abs(Target.Y-V.Y)<75.)
   {
    double Lane=V.Y-110.;if(!LegalPoint({P.X,Lane})||!LegalPoint({Target.X,Lane}))Lane=V.Y+110.;
    if(!Need(LegalPoint({P.X,Lane})&&LegalPoint({Target.X,Lane}),TEXT("No legal ordinary route around actual Guard body")))return false;
    Target=FMath::Abs(P.Y-V.Y)<100.?FVector2D(P.X,Lane):FVector2D(Target.X,P.Y);
   }
  }
  const FVector2D YFirst(P.X,Target.Y),XFirst(Target.X,P.Y);
  if(SegmentLegal(P,YFirst)&&SegmentLegal(YFirst,Target))Next=FMath::Abs(Target.Y-P.Y)>6.?YFirst:Target;
  else if(SegmentLegal(P,XFirst)&&SegmentLegal(XFirst,Target))Next=FMath::Abs(Target.X-P.X)>6.?XFirst:Target;
  else
  {
   const auto B=DungeonRoomLayout::ExplorationPreview().Barrier;const double Low=B.Min.Y-70.,High=B.Max.Y+70.;
   const double Lane=FMath::Abs(P.Y-Low)+FMath::Abs(Target.Y-Low)<=FMath::Abs(P.Y-High)+FMath::Abs(Target.Y-High)?Low:High;
   if(SegmentLegal(P,{P.X,Lane}))Next={P.X,Lane};
   else {const double X=P.X<(B.Min.X+B.Max.X)*.5?B.Min.X-70.:B.Max.X+70.;Next={X,P.Y};}
  }
  const bool Y=FMath::Abs(Next.Y-P.Y)>6.,X=!Y&&FMath::Abs(Next.X-P.X)>6.;
  Key(EKeys::W,Y&&Next.Y>P.Y);Key(EKeys::S,Y&&Next.Y<P.Y);Key(EKeys::D,X&&Next.X>P.X);Key(EKeys::A,X&&Next.X<P.X);return false;
 }
 bool DiagnosticKill(ADungeonFighter* E)
 {
  if(!Need(E&&!E->GetStoneGuardDriver()&&Game->PlayerFighter&&!Game->bGameOver,TEXT("Diagnostic target/source absent")))return false;if(E->bDead)return true;
  if(!E->CanReceiveDirectHit())return false;auto O=MakeShared<FJsonObject>();Id(O,TEXT("target_id"),E->GetRuntimeEntityId());O->SetStringField(TEXT("content_id"),E->EnemyContentId);
  O->SetStringField(TEXT("api"),TEXT("ADungeonFighter::ApplyCombatHit"));O->SetNumberField(TEXT("sim"),Game->GetSimulationTime());O->SetNumberField(TEXT("requested_damage"),100000.);O->SetNumberField(TEXT("before_HP"),E->Health);
  E->ApplyCombatHit(100000.f,Game->PlayerFighter,85.f);O->SetNumberField(TEXT("after_HP"),E->Health);O->SetBoolField(TEXT("dead"),E->bDead);DiagnosticHits.Add(MakeShared<FJsonValueObject>(O));
  return Need(E->bDead,TEXT("Public Knight/Bat diagnostic hit was not accepted; never force HP/death"));
 }
 JO Facts()
 {
  auto O=MakeShared<FJsonObject>();auto G=Game.Get();auto H=HUD.Get();auto P=G?G->PlayerFighter.Get():nullptr;if(!G||!H||!P)return O;
  O->SetStringField(TEXT("phase"),PhaseName(Phase));O->SetNumberField(TEXT("sim"),G->GetSimulationTime());O->SetArrayField(TEXT("player_ground"),XY(P->GetGroundPosition()));O->SetNumberField(TEXT("player_HP"),P->Health);O->SetNumberField(TEXT("wallet"),P->Coins);O->SetArrayField(TEXT("camera_ground"),XY(H->GetCameraGroundCenter()));O->SetBoolField(TEXT("room_cleared"),G->bRoomCleared);
  const auto& Hero=H->GetFairytaleSwordDraw();O->SetBoolField(TEXT("hero_bound_skin"),Hero.EquipmentBindingValid);O->SetBoolField(TEXT("LGT_drawn"),Hero.ArmorDrawn);O->SetNumberField(TEXT("hero_canvas_size"),Hero.CanvasSize);O->SetArrayField(TEXT("actual_rendered_player_stack"),Strings(H->GetRenderedPlayerDrawStack()));O->SetBoolField(TEXT("interface_visible"),H->GetInterfaceVisible());O->SetNumberField(TEXT("text_calls"),H->GetRenderedTextDrawCalls());
  FDungeonFirstBatchGuardRoomView Plan;TArray<TSharedPtr<FJsonValue>> Slots;
  if(G->QueryFirstBatchGuardRoom(Plan))for(const auto& V:Plan.Slots)
  {auto X=MakeShared<FJsonObject>();X->SetStringField(TEXT("slot"),V.SlotId);X->SetStringField(TEXT("content"),V.ContentId);Id(X,TEXT("stage"),uint64(V.Stage));Id(X,TEXT("entity"),V.EntityId);X->SetNumberField(TEXT("warning_at"),V.WarningAt);X->SetNumberField(TEXT("materialized_at"),V.MaterializedAt);X->SetNumberField(TEXT("dead_at"),V.DeadAt);X->SetArrayField(TEXT("spawn"),XY(V.SpawnPosition));X->SetNumberField(TEXT("visibility"),H->GetCurrentVisibilityAt(V.SpawnPosition));Slots.Add(MakeShared<FJsonValueObject>(X));}
  O->SetArrayField(TEXT("slots"),Slots);O->SetArrayField(TEXT("rendered_warning_slots"),Strings(H->GetRenderedGuardRoomWarningSlots()));O->SetObjectField(TEXT("approach_spatial"),SpatialFacts());
  if(auto E=Enemy(GuardId))if(auto Driver=E->GetStoneGuardDriver())
  {
   const auto& S=Driver->State();const auto& A=S.Action;auto N=MakeShared<FJsonObject>();Id(N,TEXT("entity"),S.EntityId);N->SetNumberField(TEXT("time"),S.Time);N->SetNumberField(TEXT("initial_time"),S.InitialTime);N->SetNumberField(TEXT("phase"),int32(S.Phase));N->SetNumberField(TEXT("HP"),S.HP);N->SetNumberField(TEXT("incoming_receipts"),S.ReceivedHits.size());N->SetNumberField(TEXT("wake_start"),S.WakeStartedAt);N->SetNumberField(TEXT("wake_end"),S.WakeEnd);N->SetArrayField(TEXT("ground"),XY(E->GetGroundPosition()));N->SetBoolField(TEXT("dead"),E->bDead);Id(N,TEXT("attack_id"),A.AttackId);N->SetNumberField(TEXT("attack_kind"),int32(A.Kind));N->SetNumberField(TEXT("facing"),S.Facing);N->SetBoolField(TEXT("in_progress"),A.InProgress);N->SetBoolField(TEXT("locked"),A.Locked);N->SetBoolField(TEXT("interrupted"),A.Interrupted);
   N->SetNumberField(TEXT("start"),A.Start);N->SetNumberField(TEXT("lock_at"),A.LockAt);N->SetNumberField(TEXT("active_at"),A.ActiveAt);N->SetNumberField(TEXT("active_end"),A.ActiveEnd);N->SetNumberField(TEXT("recovery_end"),A.RecoveryEnd);N->SetNumberField(TEXT("cooldown_end"),A.CooldownEnd);N->SetNumberField(TEXT("occupied_until"),S.OccupiedUntil);N->SetNumberField(TEXT("stun_until"),S.StunUntil);N->SetNumberField(TEXT("window_count"),S.Windows.size());O->SetObjectField(TEXT("guard_native"),N);
  }
  TArray<TSharedPtr<FJsonValue>> Draws;
  for(const auto& D:H->GetFairytaleGuardDraws())
  {
   auto Draw=SerializeDraw(D);Draw->SetBoolField(TEXT("SpatialCoverageEligible"),SpatialCredit(D.Selection));Draws.Add(MakeShared<FJsonValueObject>(Draw));if(D.EntityId!=GuardId||D.DrawId<=LastGuardDraw)continue;
   LastGuardDraw=D.DrawId;++GuardDrawCount;const auto& S=D.Selection;
   if(!Need(S.Valid&&S.EntityId==GuardId&&D.OptIn,TEXT("Actual Guard draw lacks native valid identity / partial opt-in")))break;
   const bool Known=S.Clip==DungeonFairytaleGuard::EClip::Dormant||S.Clip==DungeonFairytaleGuard::EClip::Wake||S.Clip==DungeonFairytaleGuard::EClip::Ready||S.Clip==DungeonFairytaleGuard::EClip::AxeWindup;
   if(Known&&!Need(D.Drawn&&D.TextureReady&&D.RegistrationReady&&D.TrialAllowed&&!D.FinalAccepted&&!D.ProceduralFallback&&D.MissingReason.IsEmpty(),FString(TEXT("Approved partial row did not draw: "))+D.MissingReason))break;
   if(D.Drawn&&!Need(D.WholebodyIncludesAxe&&D.DrawStack.Num()==1&&D.DrawStack[0]==D.TexturePath,TEXT("Actual wholebody draw stack is not exactly one fixed-axe layer")))break;
   if(!Known)
   {if(!Need(!D.Drawn&&D.ProceduralFallback&&!D.MissingReason.IsEmpty()&&D.DrawStack.IsEmpty(),TEXT("Missing row concealed by a sprite instead of explicit procedural gap")))break;GapSeen=true;}
   if(D.Drawn&&S.Frame>=0&&S.Frame<6)
   {
    if(S.Clip==DungeonFairytaleGuard::EClip::Dormant)++DormantSeen;
    if(S.Clip==DungeonFairytaleGuard::EClip::Wake)WakeMask|=1u<<S.Frame;
    if(S.Clip==DungeonFairytaleGuard::EClip::Ready&&SpatialCredit(S))ReadyMask|=1u<<S.Frame;
    if(S.Clip==DungeonFairytaleGuard::EClip::AxeWindup&&SpatialCredit(S))WindupMask|=1u<<S.Frame;
   }
  }
  O->SetArrayField(TEXT("guard_draws"),Draws);return O;
 }
 void Observe()
 {
  if(Stopped)return;
  if(Prewarm&&!Capturing)
  {if(!Need(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))>8,TEXT("Actual synchronous prewarm missing")))return;Start=PhaseWall=FPlatformTime::Seconds();Capturing=true;GIsDumpingMovie=-1;return;}
  if(!Capturing)return;const double Offset=FPlatformTime::Seconds()-Start;auto O=Facts();if(Stopped)return;
  O->SetNumberField(TEXT("wall_offset_s"),Offset);Observations.Add(MakeShared<FJsonValueObject>(O));Offsets.Add(MakeShared<FJsonValueNumber>(Offset));
  // Account for the completed real draw above before deciding coverage. Wake is
  // once-only: an already ended native window cannot produce its missing frame.
  if(auto E=Enemy(GuardId))if(auto Driver=E->GetStoneGuardDriver())
  {
   const auto& S=Driver->State();
   if(S.WakeStartedAt>=0.&&S.WakeEnd>S.WakeStartedAt&&S.Time>=S.WakeEnd&&WakeMask!=63)
   {Finish(FString::Printf(TEXT("Native once-only Wake ended with incomplete coverage: WakeMask=%u required63 at %.17g originalEnd=%.17g; no replay or timeout retry"),WakeMask,S.Time,S.WakeEnd));return;}
  }
  if(auto H=HUD.Get())if(!Need(!H->GetInterfaceVisible()&&H->GetRenderedTextDrawCalls()==0,TEXT("Hidden interface proof rendered UI text")))return;
  if(FinishOnFrame)Finish();
 }
 bool Born(int32 I,const FDungeonFirstBatchGuardRoomView& Room)
 {
  const auto& S=Room.Slots[I];if(S.Stage!=EDungeonGuardRoomSlotStage::Materialized)return false;const auto E=Enemy(S.EntityId);
  return Need(S.WarningAt>=Room.Slots[I-1].DeadAt+2.&&S.MaterializedAt>=S.WarningAt+1.2&&E&&!E->bDead
   &&(I==1?bool(E->GetStoneBatDriver()):bool(E->GetStoneGuardDriver())),TEXT("Formal future slot birth lacks predecessor / full native warning / native actor"));
 }
 bool ChooseSide(ADungeonFighter* E)
 {
  const auto V=E->GetGroundPosition();const double Near=Game->PlayerFighter->GetGroundPosition().X<V.X?-1.:1.;
  for(int32 Try=0;Try<2;++Try)
  {
   const int32 Side=RequestedSide?RequestedSide:(Try==0?int32(Near):-int32(Near));
   if(LegalPoint(V+FVector2D(Side*150.,0.))){ApproachSide=Side;return true;}
   if(RequestedSide)break;
  }
  return Need(false,TEXT("No legal requested normal-input axe approach side; never teleport"));
 }
 void Tick(ADungeonGuardArtPartialProbe& Actor)
 {
  if(Stopped)return;const double Now=FPlatformTime::Seconds();auto G=Actor.GetWorld()->GetAuthGameMode<ADungeonGameMode>();auto C=UGameplayStatics::GetPlayerController(&Actor,0);auto H=C?Cast<ADungeonHUD>(C->GetHUD()):nullptr;
  if(!Game.IsValid()&&G&&C&&C->PlayerInput&&H){Game=G;Controller=C;HUD=H;Actor.AddTickPrerequisiteActor(G);Actor.AddTickPrerequisiteActor(H);return;}
  if(!Game.IsValid())return;auto P=G->PlayerFighter.Get();
  if(PulseKey.IsValid()&&Now>=ReleaseAt){Key(PulseKey,false);PulseKey=FKey();NeutralUntil=Now+.04;}
  if(!Capturing){if(!Prewarm&&Now-Warm>=2.){Prewarm=true;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}else if(Now-Warm>18.)Finish(TEXT("Prewarm timeout"));return;}
  if(!Need(Now-Start<90.&&Now-PhaseWall<(Phase==8?45.:20.),FString(TEXT("Actual input/room/coverage timeout: "))+PhaseName(Phase)))return;if(FinishOnFrame)return;
  if(!Need(G==Game.Get()&&C==Controller.Get()&&H==HUD.Get()&&P&&C->GetPawn()==P&&!P->bDead&&!G->bGameOver,TEXT("Actual world/player failed")))return;
  FDungeonFirstBatchGuardRoomView Room;
  if(!Need(G->QueryFirstBatchGuardRoom(Room)&&Room.Slots.Num()==3&&G->GetEquipmentView().Config==EDungeonEquipmentRunConfig::FirstBatch,TEXT("Formal URL did not start finite three-slot room")))return;
  if(!Run.IsValid()){Run=Room.RunGuid;Owner=G->GetEquipmentView().OwnerId;Restart=G->GetRunRestartSerial();}
  if(!Need(Room.RunGuid==Run&&G->GetRunRestartSerial()==Restart,TEXT("Actual Run restarted during trial")))return;
  switch(Phase)
  {
  case 0:
   if(!Need(G->bWaitingForStart&&G->GetSimulationTime()==0.&&P->Coins==20,TEXT("Normal formal URL must await first real Enter at0/20")))return;
   if(Pulse(EKeys::Enter))Next(1);break;
  case 1:
   if(!G->bWaitingForStart&&CanPulse())
   {DungeonEquipmentInventory::FItem Item;Item.ContentId="ARM-LGT-001";const auto X=G->RegisterEquipmentSource(TEXT("display.guardart.partial.light.v002"),Item,P->GetGroundPosition()+FVector2D(24.,0.),true);if(!Need(X.Ok()&&!X.Replayed,TEXT("Explicit display LGT source failed")))return;Light=X.InstanceId;if(Pulse(EKeys::E))Next(2);}break;
  case 2:if(!G->GetEquipmentView().Action.Active&&G->GetEquipmentView().Slots[2].InstanceId==Light&&CanPulse())Next(3);break;
  case 3:if(CanPulse()&&DiagnosticKill(Enemy(Room.Slots[0].EntityId)))Next(4);break;
  case 4:if(Born(1,Room))Next(5);break;
  case 5:if(Now-PhaseWall>=.9&&DiagnosticKill(Enemy(Room.Slots[1].EntityId)))Next(6);break;
  case 6:
   if(Born(2,Room))
   {GuardId=Room.Slots[2].EntityId;auto E=Enemy(GuardId);if(!Need(E&&E->GetStoneGuardDriver(),TEXT("Formal Guard entity missing")))return;GuardWasAlreadyWaking=E->GetStoneGuardDriver()->State().Phase!=DungeonStoneGuard::EPhase::Dormant;MoveStop();Next(7);}break;
  case 7:
   if(Now-PhaseWall>=.45)
   {auto E=Enemy(GuardId);if(!Need(E&&E->GetStoneGuardDriver()&&GuardDrawCount>0,TEXT("No actual Guard draw at birth"))||!ChooseSide(E))return;Next(8);}break;
  case 8:
  {
   auto E=Enemy(GuardId);if(!Need(E&&E->GetStoneGuardDriver(),TEXT("Formal Guard disappeared")))return;
   const auto& S=E->GetStoneGuardDriver()->State();const auto& A=S.Action;
   if(!Need(S.HP==185.&&S.ReceivedHits.empty()&&!E->bDead,TEXT("Guard art observer must never damage or replace Guard")))return;
   if(!FollowRoute(E))return;
   if(!Need(P->Health==100.,TEXT("Actual player damage during safe side trial; preserve HP and failure, never heal or add invulnerability")))return;
   if(WakeMask==63&&ReadyMask==15&&WindupMask==63&&GapSeen)
   {MoveStop();Complete=true;Next(9);FinishOnFrame=true;return;}
   const FVector2D V=E->GetGroundPosition();const FVector2D AttackPoint=V+FVector2D(ApproachSide*150.,0.);
   if((S.Phase==DungeonStoneGuard::EPhase::Windup&&S.Time>=A.LockAt+.01)||S.Phase==DungeonStoneGuard::EPhase::Active)
   {
    // Only normal player direction input after actual native aim lock; no Guard/time writes.
    FVector2D Safe=AttackPoint+FVector2D(0.,-100.);
    if(!SegmentLegal(AttackPoint,Safe))Safe=AttackPoint+FVector2D(0.,100.);
    if(!Need(SegmentLegal(AttackPoint,Safe),TEXT("No legal normal-input evade lane from actual axe point")))return;MoveTo(Safe);
   }
   else if(S.Phase==DungeonStoneGuard::EPhase::Recovery&&S.Time<A.ActiveEnd+.08)MoveStop();
   else MoveTo(AttackPoint);
   break;
  }
  default:Finish(TEXT("Unknown partial observer phase"));break;
  }
 }
};
void FDungeonGuardArtPartialDeleter::operator()(FDungeonGuardArtPartialState* P)const{delete P;}
ADungeonGuardArtPartialProbe::ADungeonGuardArtPartialProbe(){PrimaryActorTick.bCanEverTick=true;}
ADungeonGuardArtPartialProbe::~ADungeonGuardArtPartialProbe()=default;
void ADungeonGuardArtPartialProbe::BeginPlay()
{
 Super::BeginPlay();Proof.Reset(new FDungeonGuardArtPartialState());Proof->Warm=FPlatformTime::Seconds();GIsDumpingMovie=0;
 FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),Proof->Directory);FParse::Value(FCommandLine::Get(),TEXT("DungeonGuardArtApproachSide="),Proof->RequestedSide);
 if(Proof->Directory.IsEmpty()||FPaths::IsRelative(Proof->Directory)){Proof->Directory.Reset();Proof->Finish(TEXT("Absolute unused evidence directory required"));return;}
 Proof->Directory=FPaths::ConvertRelativePathToFull(Proof->Directory);FPaths::NormalizeDirectoryName(Proof->Directory);
 TArray<FString> Prior;IFileManager::Get().FindFiles(Prior,*(Proof->Directory/TEXT("*")),true,false);
 Prior.Remove(TEXT("native-lossless-capture.json")); // Installed capture metadata precedes this actor BeginPlay.
 if(Prior.Num()){Proof->Stopped=true;FPlatformMisc::RequestExitWithStatus(false,3);return;}IFileManager::Get().MakeDirectory(*Proof->Directory,true);
 for(const TCHAR* Flag:{TEXT("DungeonGuardArtPartialProof"),TEXT("DungeonFairytaleGuardPartialPreview"),TEXT("DungeonContentProof"),TEXT("DungeonFastLosslessCapture"),TEXT("DungeonAsyncLosslessCapture"),TEXT("DungeonFairytaleSwordWalkPreview"),TEXT("DungeonFairytaleSwordEquipmentBoundPreview")})if(!Proof->Need(FParse::Param(FCommandLine::Get(),Flag),FString(TEXT("Missing explicit flag: "))+Flag))return;
 if(!Proof->Need(!FApp::UseFixedTimeStep()&&Proof->RequestedSide>=-1&&Proof->RequestedSide<=1,TEXT("Ordinary native pacing and side[-1,0,1] required")))return;
 for(auto C:{DungeonFairytaleGuard::EClip::Ready,DungeonFairytaleGuard::EClip::Wake,DungeonFairytaleGuard::EClip::AxeWindup})
 {const auto R=DungeonFairytaleGuard::FindRow(C);if(!Proof->Need(R&&DungeonFairytaleGuard::TrialGate(*R).IsEmpty()&&!R->FinalAccepted,TEXT("Root approved partial209/210/212 trial profile is required")))return;}
 GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Proof->Directory;
 FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonGuardArtPartialProbe::ScreenshotProcessed);
}
void ADungeonGuardArtPartialProbe::ScreenshotProcessed(){if(Proof)Proof->Observe();}
void ADungeonGuardArtPartialProbe::Tick(float D){Super::Tick(D);if(Proof)Proof->Tick(*this);}
void ADungeonGuardArtPartialProbe::EndPlay(const EEndPlayReason::Type R)
{FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);if(Proof&&!Proof->Stopped)Proof->Finish(TEXT("Actual world ended before partial trial complete"));Super::EndPlay(R);}
