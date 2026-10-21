#include "DungeonGuardMoveProbeV001.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonHUD.h"
#include "DungeonStoneGuardDriver.h"
#include "DungeonStoneGuardFeedback.h"
#include "DungeonFairytaleSwordEquipmentBinding.h"
#include "DungeonStoneBatDriver.h"
#include "DungeonFairytaleGuardMoveDrawStateV001.h"
#include "DungeonRoomLayout.h"
#include "DungeonProofScreenshots.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/Texture2D.h"
#include "TextureResource.h"
#include <cmath>
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
using JO=TSharedPtr<FJsonObject>;using JV=TSharedPtr<FJsonValue>;
namespace M=DungeonFairytaleGuardMoveRigV001;
namespace Full=DungeonFairytaleGuardFullV003;
TArray<JV> XY(FVector2D P){return{MakeShared<FJsonValueNumber>(P.X),MakeShared<FJsonValueNumber>(P.Y)};}
void Id(JO O,const TCHAR* Key,uint64 Value){O->SetStringField(Key,FString::Printf(TEXT("%llu"),Value));}
JO Action(const DungeonStoneGuard::FAction& A)
{
 auto O=MakeShared<FJsonObject>();Id(O,TEXT("attack_id"),A.AttackId);O->SetNumberField(TEXT("kind"),int32(A.Kind));O->SetNumberField(TEXT("facing"),A.Facing);O->SetBoolField(TEXT("in_progress"),A.InProgress);O->SetBoolField(TEXT("interrupted"),A.Interrupted);O->SetBoolField(TEXT("locked"),A.Locked);
 O->SetNumberField(TEXT("start"),A.Start);O->SetNumberField(TEXT("lock_at"),A.LockAt);O->SetNumberField(TEXT("active_at"),A.ActiveAt);O->SetNumberField(TEXT("active_end"),A.ActiveEnd);O->SetNumberField(TEXT("recovery_end"),A.RecoveryEnd);O->SetNumberField(TEXT("cooldown_end"),A.CooldownEnd);O->SetNumberField(TEXT("completed_at"),A.CompletedAt);O->SetNumberField(TEXT("damage"),A.Damage);O->SetNumberField(TEXT("stagger"),A.Stagger);O->SetArrayField(TEXT("origin"),XY({A.Origin.X,A.Origin.Y}));O->SetArrayField(TEXT("locked_center"),XY({A.LockedCenter.X,A.LockedCenter.Y}));return O;
}
JO Sample(const FDungeonGuardMoveSample& S)
{
 auto O=MakeShared<FJsonObject>();O->SetBoolField(TEXT("valid"),S.Valid);O->SetBoolField(TEXT("block_known"),S.BlockKnown);Id(O,TEXT("entity"),S.EntityId);Id(O,TEXT("path_owner"),S.AcceptedPathOwnerId);Id(O,TEXT("room"),S.RoomInstanceId);Id(O,TEXT("epoch"),S.PresentationEpoch);Id(O,TEXT("movement_event"),S.MovementEventId);O->SetStringField(TEXT("run"),S.RunGuid.ToString(EGuidFormats::Digits));O->SetStringField(TEXT("content"),S.EnemyContentId);O->SetNumberField(TEXT("sample_time"),S.SampleTime);O->SetNumberField(TEXT("movement_at"),S.MovementAtTime);O->SetNumberField(TEXT("accepted_distance"),S.AcceptedDistance);O->SetNumberField(TEXT("current_accepted"),S.CurrentAcceptedDistance);O->SetNumberField(TEXT("facing"),S.Facing);O->SetArrayField(TEXT("ground"),XY(S.GroundPosition));O->SetArrayField(TEXT("from"),XY(S.MovementFrom));O->SetArrayField(TEXT("to"),XY(S.MovementTo));O->SetArrayField(TEXT("direction"),XY(S.MovementDirection));O->SetBoolField(TEXT("native_selection_valid"),S.NativeSelection.Valid);O->SetNumberField(TEXT("native_selection_phase"),int32(S.NativeSelection.Phase));O->SetStringField(TEXT("native_selection_clip"),UTF8_TO_TCHAR(Full::ClipName(S.NativeSelection.Clip)));Id(O,TEXT("native_selection_event"),S.NativeSelection.SourceEventId);O->SetNumberField(TEXT("native_selection_time"),S.NativeSelection.SampleTime);O->SetNumberField(TEXT("native_selection_distance"),S.NativeSelection.AcceptedDistance);return O;
}
JO Quad(const M::FSubmittedQuad& Q)
{
 auto O=MakeShared<FJsonObject>();O->SetArrayField(TEXT("top"),XY({Q.X,Q.Y}));O->SetArrayField(TEXT("size"),XY({Q.Width,Q.Height}));O->SetArrayField(TEXT("uv"),XY({Q.U,Q.V}));O->SetArrayField(TEXT("uv_size"),XY({Q.UL,Q.VL}));O->SetNumberField(TEXT("rotation"),Q.RotationDegrees);O->SetNumberField(TEXT("draw_scale"),Q.DrawScale);O->SetBoolField(TEXT("scale_position"),Q.ScalePosition);O->SetArrayField(TEXT("pivot"),XY(Q.RotationPivotUV));TArray<JV> Color;for(double C:{double(Q.Tint.R),double(Q.Tint.G),double(Q.Tint.B),double(Q.Tint.A)})Color.Add(MakeShared<FJsonValueNumber>(C));O->SetArrayField(TEXT("tint"),Color);return O;
}
JO RigDraw(const FDungeonFairytaleGuardMoveRigDrawV001& D)
{
 auto O=MakeShared<FJsonObject>();Id(O,TEXT("draw_id"),D.DrawId);Id(O,TEXT("entity"),D.EntityId);O->SetBoolField(TEXT("opt_in"),D.OptIn);O->SetBoolField(TEXT("trial_allowed"),D.TrialAllowed);O->SetBoolField(TEXT("final_accepted"),D.FinalAccepted);O->SetBoolField(TEXT("registration_ready"),D.RegistrationReady);O->SetBoolField(TEXT("texture_ready"),D.TextureReady);O->SetBoolField(TEXT("drawn"),D.Drawn);O->SetBoolField(TEXT("procedural_fallback"),D.ProceduralFallback);O->SetBoolField(TEXT("body_includes_axe"),D.WholebodyIncludesAxe);O->SetStringField(TEXT("type"),D.PresentationType);O->SetStringField(TEXT("missing"),D.MissingReason);
 const auto& P=D.Plan;const auto& R=P.Rig;O->SetBoolField(TEXT("plan_valid"),P.Valid);O->SetBoolField(TEXT("plan_body_includes_axe"),P.WholebodyIncludesAxe);O->SetObjectField(TEXT("sample"),Sample(P.Sample));O->SetNumberField(TEXT("required_resources"),P.RequiredResources);O->SetNumberField(TEXT("independent_axe_layers"),P.IndependentAxeLayers);O->SetStringField(TEXT("trial_record"),P.TrialApprovalRecord);O->SetBoolField(TEXT("rig_valid"),R.Valid);O->SetNumberField(TEXT("facing"),R.Facing);O->SetNumberField(TEXT("half"),R.Half);O->SetNumberField(TEXT("reflection_count"),R.ReflectionCount);O->SetNumberField(TEXT("accepted_distance"),R.AcceptedDistance);O->SetNumberField(TEXT("cycle_position"),R.CyclePosition);O->SetNumberField(TEXT("u"),R.U);O->SetNumberField(TEXT("body_rise"),R.BodyRise);O->SetStringField(TEXT("profile_id"),R.ProfileId);O->SetStringField(TEXT("profile_sha256"),R.ProfileSHA256);O->SetStringField(TEXT("source_snapshot_sha256"),R.SourceSnapshotSHA256);
 TArray<JV> Planned;for(const auto& X:R.Parts){auto J=MakeShared<FJsonObject>();J->SetNumberField(TEXT("component"),int32(X.Component));J->SetStringField(TEXT("texture"),X.TexturePath);J->SetStringField(TEXT("source_SHA"),X.SourceSHA256);J->SetStringField(TEXT("source_RGBA_SHA"),X.SourceRGBASHA256);J->SetNumberField(TEXT("source_native_batch_id"),X.NativeBatchId);J->SetNumberField(TEXT("component_scale"),X.ComponentToRestScale);J->SetNumberField(TEXT("source_rotation_radians"),X.SourceRotationRadians);J->SetArrayField(TEXT("source_pivot"),XY(X.SourcePivot));J->SetArrayField(TEXT("art_anchor_from_ground"),XY(X.ArtAnchorFromGround));J->SetArrayField(TEXT("screen_anchor"),XY(X.ScreenAnchor));J->SetObjectField(TEXT("quad"),Quad(X.Quad));Planned.Add(MakeShared<FJsonValueObject>(J));}O->SetArrayField(TEXT("planned_parts"),Planned);
 TArray<JV> Parts;for(const auto& X:D.Parts){auto J=MakeShared<FJsonObject>();J->SetNumberField(TEXT("component"),int32(X.Component));J->SetStringField(TEXT("texture"),X.TexturePath);J->SetStringField(TEXT("source_SHA"),X.SourceSHA256);J->SetStringField(TEXT("source_RGBA_SHA"),X.SourceRGBASHA256);J->SetNumberField(TEXT("source_native_batch_id"),X.NativeBatchId);J->SetBoolField(TEXT("submitted"),X.Submitted);J->SetObjectField(TEXT("quad"),Quad(X.Quad));Parts.Add(MakeShared<FJsonValueObject>(J));}O->SetArrayField(TEXT("submitted_parts"),Parts);
 TArray<JV> Resources;for(const auto& X:P.Residents){auto J=MakeShared<FJsonObject>();J->SetNumberField(TEXT("component"),int32(X.Component));J->SetStringField(TEXT("texture"),X.TexturePath);J->SetStringField(TEXT("class"),X.ClassName);J->SetStringField(TEXT("source_SHA"),X.SourceSHA256);J->SetStringField(TEXT("source_RGBA_SHA"),X.SourceRGBASHA256);J->SetNumberField(TEXT("width"),X.Width);J->SetNumberField(TEXT("height"),X.Height);J->SetBoolField(TEXT("resource_ready"),X.ResourceReady);J->SetBoolField(TEXT("pending_initialization"),X.PendingInitialization);Resources.Add(MakeShared<FJsonValueObject>(J));}O->SetArrayField(TEXT("resident_textures"),Resources);return O;
}
JO FullDraw(const FDungeonFairytaleGuardFullDrawV003& D)
{
 auto O=MakeShared<FJsonObject>();Id(O,TEXT("draw_id"),D.DrawId);Id(O,TEXT("entity"),D.EntityId);Id(O,TEXT("attack"),D.Selection.AttackId);Id(O,TEXT("event"),D.Selection.SourceEventId);O->SetStringField(TEXT("clip"),UTF8_TO_TCHAR(Full::ClipName(D.Selection.Clip)));O->SetNumberField(TEXT("frame"),D.Selection.Frame);O->SetNumberField(TEXT("facing"),D.Selection.Facing);O->SetNumberField(TEXT("sample_time"),D.Selection.SampleTime);O->SetNumberField(TEXT("interval_start"),D.Selection.IntervalStart);O->SetNumberField(TEXT("interval_end"),D.Selection.IntervalEnd);O->SetBoolField(TEXT("drawn"),D.Drawn);O->SetBoolField(TEXT("quad_submitted"),D.QuadSubmitted);O->SetBoolField(TEXT("fallback"),D.ProceduralFallback);O->SetBoolField(TEXT("ready"),D.TextureReady&&D.RegistrationReady);O->SetStringField(TEXT("texture"),D.TexturePath);O->SetStringField(TEXT("source_SHA"),D.SourceSHA256);O->SetStringField(TEXT("source_RGBA_SHA"),D.SourceRGBASHA256);O->SetNumberField(TEXT("native_source_id"),D.NativeSourceId);O->SetStringField(TEXT("profile_id"),D.ProfileId);O->SetArrayField(TEXT("ground_screen"),XY(D.GroundScreen));O->SetArrayField(TEXT("top"),XY(D.QuadTop));O->SetArrayField(TEXT("size"),XY(D.QuadSize));O->SetArrayField(TEXT("uv"),XY(D.QuadUV));O->SetArrayField(TEXT("uv_size"),XY(D.QuadUVSize));O->SetArrayField(TEXT("pivot"),XY(D.QuadRotationPivot));O->SetNumberField(TEXT("rotation"),D.QuadRotationDegrees);O->SetNumberField(TEXT("draw_scale"),D.QuadDrawScale);O->SetBoolField(TEXT("scale_position"),D.QuadScalePosition);return O;
}
const TCHAR* PhaseName(int32 P){switch(P){case 0:return TEXT("await_enter");case 1:return TEXT("register_LGT_real_E");case 2:return TEXT("await_commit");case 3:return TEXT("Knight_diagnostic");case 4:return TEXT("await_Bat");case 5:return TEXT("Bat_diagnostic");case 6:return TEXT("await_planned_Guard");case 7:return TEXT("normal_side_route");case 8:return TEXT("normal_outward_lead_native_Move128");case 9:return TEXT("release_hero_native_combat_then_Ready");case 10:return TEXT("complete");default:return TEXT("invalid");}}
}
struct FDungeonGuardMoveProofState
{
 FString Directory;bool Stopped=false,Prewarm=false,Capturing=false,Complete=false,FinishOnFrame=false,RoutePlanned=false,RouteReached=false,MovePinned=false,CycleComplete=false,BattlePinned=false,MoveCombatJoin=false,RecoveryReadyJoin=false;
 TWeakObjectPtr<ADungeonGameMode> Game;TWeakObjectPtr<APlayerController> Controller;TWeakObjectPtr<ADungeonHUD> HUD;
 TMap<FKey,bool> Keys;FKey PulseKey;double ReleaseAt=0.,NeutralUntil=0.,Warm=0.,Start=0.,Stop=0.,PhaseWall=0.,RouteLane=0.,BeforeHP=0.;int32 Phase=0,RequestedSide=0,ApproachSide=0,RouteStage=0;
 FGuid Run;uint64 Owner=0,Restart=0,Light=0,Sword=0,GuardId=0,PlayerId=0,RoomId=0,Epoch=0,LastMoveEvent=0,LastMoveDraw=0,LastReadyDraw=0,SwordVersion=0,LightVersion=0,BattleId=0;
 double FirstDistance=-1.,LastDistance=-1.,FirstMoveTime=-1.,LastMoveTime=-1.;uint32 DistanceWindowMask=0;int32 MoveDraws=0,ReadySeen=0;
 FVector2D RouteStart=FVector2D::ZeroVector,RouteGuard=FVector2D::ZeroVector;DungeonStoneGuard::FAction Battle;
 JO Previous=MakeShared<FJsonObject>();TArray<JV> Inputs,Steps,Observations,Offsets,DiagnosticHits,RouteWitnesses,StartupTextures,Joins;
 bool Need(bool B,const FString& Why){if(!B)Finish(Why);return B;}
 ADungeonFighter* Enemy(uint64 Id)const{if(auto G=Game.Get())for(auto E:G->Enemies)if(IsValid(E)&&E->GetRuntimeEntityId()==Id)return E.Get();return nullptr;}
 void Key(FKey K,bool Down){if(Keys.FindRef(K)==Down)return;if(auto C=Controller.Get()){C->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));Keys.Add(K,Down);auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("key"),K.ToString());O->SetBoolField(TEXT("down"),Down);O->SetNumberField(TEXT("sim"),Game.IsValid()?Game->GetSimulationTime():0.);O->SetNumberField(TEXT("wall_offset_s"),Capturing?FPlatformTime::Seconds()-Start:0.);Inputs.Add(MakeShared<FJsonValueObject>(O));}}
 void MoveStop(){for(FKey K:{EKeys::A,EKeys::D,EKeys::W,EKeys::S})Key(K,false);}
 bool CanPulse()const{return !PulseKey.IsValid()&&FPlatformTime::Seconds()>=NeutralUntil;}
 bool Pulse(FKey K){if(!CanPulse())return false;Key(K,true);PulseKey=K;ReleaseAt=FPlatformTime::Seconds()+.08;return true;}
 void Next(int32 P){Phase=P;PhaseWall=FPlatformTime::Seconds();auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("phase"),P);O->SetStringField(TEXT("name"),PhaseName(P));O->SetNumberField(TEXT("sim"),Game->GetSimulationTime());O->SetNumberField(TEXT("wall_offset_s"),PhaseWall-Start);Steps.Add(MakeShared<FJsonValueObject>(O));}
 bool LegalPoint(FVector2D V)const{const auto B=DungeonRoomLayout::ExplorationPreview().Barrier;const auto H=Game->PlayerFighter->GetCombatBodyHalfExtent()+FVector2D(8.,8.);return DungeonRoomLayout::CenterBounds().IsInsideOrOn(V-H)&&DungeonRoomLayout::CenterBounds().IsInsideOrOn(V+H)&&!(V.X>=B.Min.X-H.X&&V.X<=B.Max.X+H.X&&V.Y>=B.Min.Y-H.Y&&V.Y<=B.Max.Y+H.Y);}
 bool SegmentLegal(FVector2D A,FVector2D B)const{const auto H=Game->PlayerFighter->GetCombatBodyHalfExtent()+FVector2D(8.,8.);const auto R=DungeonRoomLayout::ExplorationPreview().Barrier;const FBox2D Seg(FVector2D(FMath::Min(A.X,B.X),FMath::Min(A.Y,B.Y)),FVector2D(FMath::Max(A.X,B.X),FMath::Max(A.Y,B.Y)));if(!LegalPoint(A)||!LegalPoint(B)||FBox2D(R.Min-H,R.Max+H).Intersect(Seg))return false;if(auto E=Enemy(GuardId)){const auto P=E->GetGroundPosition(),S=H+E->GetCombatBodyHalfExtent();if(FBox2D(P-S,P+S).Intersect(Seg))return false;}return true;}
 bool MoveTo(FVector2D T){const auto P=Game->PlayerFighter->GetGroundPosition();if(!Need(LegalPoint(T),TEXT("Normal input target outside legal floor")))return false;if((T-P).GetAbsMax()<=6.){MoveStop();return true;}const bool Y=FMath::Abs(T.Y-P.Y)>6.,X=!Y&&FMath::Abs(T.X-P.X)>6.;Key(EKeys::W,Y&&T.Y>P.Y);Key(EKeys::S,Y&&T.Y<P.Y);Key(EKeys::D,X&&T.X>P.X);Key(EKeys::A,X&&T.X<P.X);return false;}
 bool FollowRoute(ADungeonFighter* E)
 {
  if(RouteReached)return true;const auto P=Game->PlayerFighter->GetGroundPosition(),V=E->GetGroundPosition();
  if(!RoutePlanned){ApproachSide=RequestedSide?RequestedSide:(P.X<V.X?-1:1);for(double S:{1.,-1.}){const double Y=V.Y+S*140.;const FVector2D A(P.X,Y),B(V.X+ApproachSide*140.,Y),C(V.X+ApproachSide*140.,V.Y);if(!SegmentLegal(P,A)||!SegmentLegal(A,B)||!SegmentLegal(B,C))continue;RouteLane=Y;RouteStart=P;RouteGuard=V;RoutePlanned=true;auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("event"),TEXT("planned"));O->SetNumberField(TEXT("sim"),Game->GetSimulationTime());O->SetArrayField(TEXT("player"),XY(P));O->SetArrayField(TEXT("guard"),XY(V));O->SetArrayField(TEXT("outside"),XY(A));O->SetArrayField(TEXT("side_lane"),XY(B));O->SetArrayField(TEXT("approach"),XY(C));RouteWitnesses.Add(MakeShared<FJsonValueObject>(O));break;}if(!Need(RoutePlanned,TEXT("No legal body-aware normal WASD route; never teleport")))return false;}
  const FVector2D T=RouteStage==0?FVector2D(P.X,RouteLane):RouteStage==1?FVector2D(V.X+ApproachSide*140.,RouteLane):FVector2D(V.X+ApproachSide*140.,V.Y);if(!MoveTo(T))return false;
  auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("event"),TEXT("reached"));O->SetNumberField(TEXT("stage"),RouteStage);O->SetNumberField(TEXT("sim"),Game->GetSimulationTime());O->SetArrayField(TEXT("player"),XY(P));O->SetArrayField(TEXT("guard"),XY(V));RouteWitnesses.Add(MakeShared<FJsonValueObject>(O));if(++RouteStage<3)return false;
  const auto D=P-V;RouteReached=Need(D.X*ApproachSide>=120.&&D.X*ApproachSide<=160.&&FMath::Abs(D.Y)<=6.,TEXT("Normal route has not reached real requested side"));return RouteReached;
 }
 bool DiagnosticKill(ADungeonFighter* E)
 {
  if(!Need(E&&!E->GetStoneGuardDriver()&&(E->EnemyContentId==TEXT("ENM-STN-001")||E->EnemyContentId==TEXT("ENM-STN-002"))&&DiagnosticHits.Num()<2,TEXT("Only predecessor Knight/Bat diagnostic is allowed")))return false;if(E->bDead)return true;if(!E->CanReceiveDirectHit())return false;
  auto O=MakeShared<FJsonObject>();Id(O,TEXT("target"),E->GetRuntimeEntityId());O->SetStringField(TEXT("content"),E->EnemyContentId);O->SetStringField(TEXT("api"),TEXT("ADungeonFighter::ApplyCombatHit"));O->SetNumberField(TEXT("sim"),Game->GetSimulationTime());O->SetNumberField(TEXT("before_HP"),E->Health);
  E->ApplyCombatHit(100000.f,Game->PlayerFighter,85.f);O->SetNumberField(TEXT("after_HP"),E->Health);O->SetBoolField(TEXT("dead"),E->bDead);DiagnosticHits.Add(MakeShared<FJsonValueObject>(O));return Need(E->bDead,TEXT("Predecessor diagnostic failed; do not assign HP/death"));
 }

 JO Facts()
 {
  auto O=MakeShared<FJsonObject>();auto G=Game.Get();auto H=HUD.Get();auto P=G?G->PlayerFighter.Get():nullptr;if(!G||!H||!P)return O;
  O->SetNumberField(TEXT("phase"),Phase);O->SetNumberField(TEXT("sim"),G->GetSimulationTime());O->SetArrayField(TEXT("player_ground"),XY(P->GetGroundPosition()));O->SetArrayField(TEXT("camera_ground"),XY(H->GetCameraGroundCenter()));O->SetNumberField(TEXT("player_HP"),P->Health);O->SetNumberField(TEXT("player_facing"),P->Facing);O->SetStringField(TEXT("player_animation"),P->AnimationName);O->SetNumberField(TEXT("player_animation_time"),P->AnimationTime);O->SetBoolField(TEXT("interface_visible"),H->GetInterfaceVisible());O->SetNumberField(TEXT("text_calls"),H->GetRenderedTextDrawCalls());O->SetBoolField(TEXT("range_debug"),H->IsCombatRangeDebugEnabled());O->SetNumberField(TEXT("range_lines"),H->GetCombatRangeDebugLineCount());
  for(const auto& K:TArray<TPair<FString,FKey>>{{TEXT("held_A"),EKeys::A},{TEXT("held_D"),EKeys::D},{TEXT("held_W"),EKeys::W},{TEXT("held_S"),EKeys::S}})O->SetBoolField(K.Key,Controller->IsInputKeyDown(K.Value));
  DungeonFairytaleSwordEquipmentBinding::FBinding Binding;FString Why;if(!Need(DungeonFairytaleSwordEquipmentBinding::Resolve(*G,*P,Binding,Why),TEXT("Actual committed hero gear disappeared")))return O;Id(O,TEXT("weapon_instance"),Binding.WeaponInstanceId);Id(O,TEXT("armor_instance"),Binding.ArmorInstanceId);Id(O,TEXT("weapon_version"),Binding.WeaponVersion);Id(O,TEXT("armor_version"),Binding.ArmorVersion);
  if(LightVersion&&!Need(Binding.WeaponInstanceId==Sword&&Binding.ArmorInstanceId==Light&&Binding.WeaponVersion==SwordVersion&&Binding.ArmorVersion==LightVersion,TEXT("Actual hero equipment IDs/versions changed during Move trial")))return O;
  auto E=Enemy(GuardId);if(!E||!E->GetStoneGuardDriver())return O;const auto& S=E->GetStoneGuardDriver()->State();
  if(!Need(!G->IsRunInstallGated()&&G->GetRunPresentationEpoch()==Epoch&&S.EntityId==GuardId&&S.Time==G->GetSimulationTime()&&!E->bDead&&S.HP==185.&&S.ReceivedHits.empty(),TEXT("Actual completed Guard identity/time/living185/no incoming hit premise lost")))return O;
  O->SetNumberField(TEXT("guard_time"),S.Time);O->SetNumberField(TEXT("guard_phase"),int32(S.Phase));O->SetNumberField(TEXT("guard_facing"),S.Facing);O->SetNumberField(TEXT("guard_HP"),S.HP);O->SetNumberField(TEXT("guard_incoming_count"),S.ReceivedHits.size());O->SetArrayField(TEXT("guard_ground"),XY(E->GetGroundPosition()));O->SetObjectField(TEXT("guard_action"),Action(S.Action));
  FDungeonGuardMoveSample Q;const bool Query=E->QueryCompletedGuardMove(Q);O->SetBoolField(TEXT("move_query_ok"),Query);O->SetObjectField(TEXT("move_query"),Sample(Q));
  const FDungeonFairytaleGuardMoveRigDrawV001* D=nullptr;for(const auto& Candidate:H->GetFairytaleGuardMoveRigDraws())if(Candidate.EntityId==GuardId){if(!Need(!D,TEXT("Repeated Guard Move Draw DTO for one actor")))return O;D=&Candidate;}
  const FDungeonFairytaleGuardFullDrawV003* B=nullptr;for(const auto& Candidate:H->GetFairytaleGuardFullDraws())if(Candidate.EntityId==GuardId){if(!Need(!B,TEXT("Repeated Full Draw DTO for one Guard")))return O;B=&Candidate;}
  O->SetObjectField(TEXT("rig_draw"),D?RigDraw(*D):MakeShared<FJsonObject>());O->SetObjectField(TEXT("full_draw"),B?FullDraw(*B):MakeShared<FJsonObject>());O->SetStringField(TEXT("visual_kind"),D&&D->Drawn?TEXT("Move7"):B&&B->Drawn?UTF8_TO_TCHAR(Full::ClipName(B->Selection.Clip)):TEXT("unqualified"));
  if(Query)
  {
   if(!Need(D&&D->Drawn&&D->OptIn&&D->TrialAllowed&&!D->FinalAccepted&&D->RegistrationReady&&D->TextureReady&&!D->ProceduralFallback&&D->WholebodyIncludesAxe&&D->Plan.WholebodyIncludesAxe&&D->Plan.Valid&&D->Plan.RequiredResources==7&&D->Plan.IndependentAxeLayers==0&&D->Plan.Rig.Valid&&D->Parts.Num()==7&&D->Plan.Rig.Parts.Num()==7&&D->Plan.Residents.Num()==7&&(!B||!B->Drawn),TEXT("Actual Move7 atomic seven submissions/no duplicated wholebody or axe failed")))return O;
   const auto& Actual=D->Plan.Sample;
   if(!Need(Q.Valid&&!Q.BlockKnown&&Q.EntityId==GuardId&&Q.AcceptedPathOwnerId==GuardId&&Q.RunGuid==Run&&Q.RoomInstanceId==RoomId&&Q.PresentationEpoch==Epoch&&Q.SampleTime==S.Time&&Q.MovementAtTime==S.Time&&Q.CurrentAcceptedDistance>0.&&Actual.Valid==Q.Valid&&Actual.BlockKnown==Q.BlockKnown&&Actual.EntityId==Q.EntityId&&Actual.AcceptedPathOwnerId==Q.AcceptedPathOwnerId&&Actual.RunGuid==Q.RunGuid&&Actual.RoomInstanceId==Q.RoomInstanceId&&Actual.PresentationEpoch==Q.PresentationEpoch&&Actual.EnemyContentId==Q.EnemyContentId&&Actual.MovementFrom==Q.MovementFrom&&Actual.MovementTo==Q.MovementTo&&Actual.MovementDirection==Q.MovementDirection&&Actual.MovementAtTime==Q.MovementAtTime&&Actual.MovementEventId==Q.MovementEventId&&Actual.SampleTime==Q.SampleTime&&Actual.AcceptedDistance==Q.AcceptedDistance&&Actual.CurrentAcceptedDistance==Q.CurrentAcceptedDistance&&Actual.GroundPosition==Q.GroundPosition&&Actual.Facing==Q.Facing&&D->Plan.Rig.AcceptedDistance==Q.AcceptedDistance&&D->Plan.Rig.Facing==Q.Facing,TEXT("SAME current owner/run/room/epoch/native distance sample differs from actual renderer plan")))return O;
   for(const auto& T:D->Plan.Residents)if(!Need(T.ClassName==TEXT("Texture2D")&&T.Width==512&&T.Height==512&&T.ResourceReady&&!T.PendingInitialization,TEXT("Actual complete seven cache resources failed")))return O;
   for(const auto& T:D->Parts)if(!Need(T.Submitted,TEXT("Move7 Plan was not really submitted")))return O;
   const auto Delta=P->GetGroundPosition()-E->GetGroundPosition();const bool Straight=Q.Facing==ApproachSide&&Q.MovementDirection.X==ApproachSide&&Q.MovementDirection.Y==0.&&Delta.X*ApproachSide>=80.;
   if(Phase==8&&Straight&&Q.MovementEventId>LastMoveEvent&&D->DrawId>LastMoveDraw)
   {
    if(!MovePinned){MovePinned=true;FirstDistance=Q.AcceptedDistance;FirstMoveTime=Q.SampleTime;}
    LastMoveEvent=Q.MovementEventId;LastMoveDraw=D->DrawId;LastDistance=Q.AcceptedDistance;LastMoveTime=Q.SampleTime;++MoveDraws;
    if(!Need(std::isfinite(D->Plan.Rig.CyclePosition)&&D->Plan.Rig.CyclePosition>=0.&&D->Plan.Rig.CyclePosition<128.,TEXT("Actual distance cycle outside finite half-open128 domain")))return O;const int32 Window=int32(D->Plan.Rig.CyclePosition/(128./6.));DistanceWindowMask|=1u<<Window;
    if(LastDistance-FirstDistance>=128.&&DistanceWindowMask==63)CycleComplete=true;
   }
   else if(Phase==8&&MovePinned&&!CycleComplete&&!Need(Straight,TEXT("One canonical straight-X cycle changed direction/side; preserve failure, never reset gait")))return O;
  }
  if(Phase==9&&CycleComplete)
  {
   if(!BattlePinned&&S.Action.InProgress&&S.Phase==DungeonStoneGuard::EPhase::Windup&&S.Action.Start>=LastMoveTime){BattlePinned=true;BattleId=S.Action.AttackId;Battle=S.Action;}
   if(BattlePinned&&B&&B->Drawn&&B->TextureReady&&B->RegistrationReady&&!B->ProceduralFallback&&B->Selection.Clip==Full::EClip::Ready&&B->Selection.Phase==DungeonStoneGuard::EPhase::Idle&&B->Selection.AttackId==BattleId&&S.Action.CompletedAt==Battle.RecoveryEnd&&S.Time>=Battle.RecoveryEnd&&S.Time<Battle.RecoveryEnd+.3&&B->DrawId>LastReadyDraw){LastReadyDraw=B->DrawId;++ReadySeen;}
  }
  if(Previous->HasField(TEXT("visual_kind")))
  {
   const FString Before=Previous->GetStringField(TEXT("visual_kind")),Now=O->GetStringField(TEXT("visual_kind"));
   if(Phase==9&&Before==TEXT("Move7")&&(Now==TEXT("AxeWindup")||Now==TEXT("StompWindup"))&&B&&B->Selection.Frame==0&&BattlePinned&&B->Selection.AttackId==BattleId)
   {MoveCombatJoin=true;auto J=MakeShared<FJsonObject>();J->SetStringField(TEXT("kind"),TEXT("Move7_to_native_Windup"));J->SetNumberField(TEXT("from_observation"),Observations.Num()-1);J->SetNumberField(TEXT("to_observation"),Observations.Num());Joins.Add(MakeShared<FJsonValueObject>(J));}
   if(Phase==9&&(Before==TEXT("AxeRecovery")||Before==TEXT("StompRecovery"))&&Now==TEXT("Ready")&&B&&BattlePinned&&B->Selection.AttackId==BattleId&&S.Action.CompletedAt==Battle.RecoveryEnd&&S.Time>=Battle.RecoveryEnd&&S.Time<Battle.RecoveryEnd+.3&&Previous->GetObjectField(TEXT("full_draw"))->GetStringField(TEXT("attack"))==FString::Printf(TEXT("%llu"),BattleId)&&Previous->GetObjectField(TEXT("full_draw"))->GetNumberField(TEXT("frame"))==3&&Previous->GetObjectField(TEXT("full_draw"))->GetNumberField(TEXT("interval_end"))==Battle.RecoveryEnd)
   {RecoveryReadyJoin=true;auto J=MakeShared<FJsonObject>();J->SetStringField(TEXT("kind"),TEXT("native_Recovery_to_Ready_stop"));J->SetNumberField(TEXT("from_observation"),Observations.Num()-1);J->SetNumberField(TEXT("to_observation"),Observations.Num());Joins.Add(MakeShared<FJsonValueObject>(J));}
  }
  Previous=O;return O;
 }
 void Observe()
 {
  if(Stopped)return;if(Prewarm&&!Capturing){if(!Need(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))>8,TEXT("Synchronous prewarm missing")))return;Start=PhaseWall=FPlatformTime::Seconds();Capturing=true;GIsDumpingMovie=-1;return;}if(!Capturing)return;
  const double T=FPlatformTime::Seconds()-Start;auto O=Facts();if(Stopped)return;O->SetNumberField(TEXT("wall_offset_s"),T);Observations.Add(MakeShared<FJsonValueObject>(O));Offsets.Add(MakeShared<FJsonValueNumber>(T));
  if(!Need(!HUD->GetInterfaceVisible()&&HUD->GetRenderedTextDrawCalls()==0&&!HUD->IsCombatRangeDebugEnabled()&&HUD->GetCombatRangeDebugLineCount()==0,TEXT("UI/default range hidden contract lost")))return;
  if(Phase==9&&BattlePinned){const auto& S=Enemy(GuardId)->GetStoneGuardDriver()->State();if(S.Time>=Battle.RecoveryEnd+.3&&!Need(ReadySeen>=3&&MoveCombatJoin&&RecoveryReadyJoin,TEXT("Original one Ready window ended before real Move/combat/Ready joins; never replay to fill")))return;}
  if(FinishOnFrame)Finish();
 }
 void Finish(const FString& Why=FString())
 {
  if(Stopped)return;Stopped=true;Stop=FPlatformTime::Seconds();GIsDumpingMovie=0;TArray<FKey> Held;Keys.GetKeys(Held);for(FKey K:Held)Key(K,false);const bool Flushed=FlushFastLosslessProofScreenshots();const bool Passed=Why.IsEmpty()&&Complete&&Flushed&&!Observations.IsEmpty();auto R=MakeShared<FJsonObject>();
  R->SetStringField(TEXT("schema"),TEXT("guard-Move7-native-observer-v001"));R->SetStringField(TEXT("scenario"),TEXT("NormalWASDLeadActualGuardMove128CombatReady"));R->SetBoolField(TEXT("passed"),Passed);R->SetBoolField(TEXT("flow_complete"),Complete);R->SetStringField(TEXT("failure"),Why);Id(R,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());R->SetStringField(TEXT("run"),Run.ToString(EGuidFormats::Digits));Id(R,TEXT("owner"),Owner);Id(R,TEXT("restart_serial"),Restart);Id(R,TEXT("guard_entity"),GuardId);Id(R,TEXT("player_entity"),PlayerId);Id(R,TEXT("room"),RoomId);Id(R,TEXT("epoch"),Epoch);Id(R,TEXT("sword_instance"),Sword);Id(R,TEXT("light_instance"),Light);Id(R,TEXT("sword_version"),SwordVersion);Id(R,TEXT("light_version"),LightVersion);Id(R,TEXT("battle_attack"),BattleId);R->SetNumberField(TEXT("requested_approach_side"),RequestedSide);R->SetNumberField(TEXT("actual_approach_side"),ApproachSide);R->SetNumberField(TEXT("first_distance"),FirstDistance);R->SetNumberField(TEXT("last_distance"),LastDistance);R->SetNumberField(TEXT("first_move_time"),FirstMoveTime);R->SetNumberField(TEXT("last_move_time"),LastMoveTime);R->SetNumberField(TEXT("distance_window_mask"),DistanceWindowMask);R->SetNumberField(TEXT("move_draws"),MoveDraws);R->SetNumberField(TEXT("ready_seen"),ReadySeen);R->SetBoolField(TEXT("MoveCombatJoin"),MoveCombatJoin);R->SetBoolField(TEXT("RecoveryReadyJoin"),RecoveryReadyJoin);R->SetObjectField(TEXT("battle_original_envelope"),Action(Battle));
  R->SetNumberField(TEXT("pre_guard_HP"),BeforeHP);R->SetArrayField(TEXT("normal_inputs"),Inputs);R->SetArrayField(TEXT("steps"),Steps);R->SetArrayField(TEXT("observations"),Observations);R->SetArrayField(TEXT("diagnostic_predecessor_hits"),DiagnosticHits);R->SetArrayField(TEXT("route_witnesses"),RouteWitnesses);R->SetArrayField(TEXT("startup_resident_textures"),StartupTextures);R->SetArrayField(TEXT("actual_adjacent_joins"),Joins);
  R->SetBoolField(TEXT("player_or_Guard_public_damage_used"),false);R->SetBoolField(TEXT("HP_poise_clock_actor_writes"),false);R->SetBoolField(TEXT("AI_toggle_used"),false);R->SetBoolField(TEXT("historical_Sweep_requeried"),false);R->SetBoolField(TEXT("wallclock_gait_used"),false);R->SetBoolField(TEXT("raster_Move6_frames_claimed"),false);R->SetBoolField(TEXT("Guard_Hurt_Stun_native_covered"),false);R->SetBoolField(TEXT("silent_video"),true);R->SetBoolField(TEXT("audio_recorded"),false);R->SetBoolField(TEXT("visual_reviewed"),false);R->SetNumberField(TEXT("formal_complete_units"),0);R->SetBoolField(TEXT("native_async_capture_writes_flushed"),Flushed);
  auto Timing=MakeShared<FJsonObject>();Timing->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());Timing->SetNumberField(TEXT("capture_start_monotonic_s"),Start);Timing->SetNumberField(TEXT("capture_stop_monotonic_s"),Stop);Timing->SetArrayField(TEXT("frame_wall_offsets_s"),Offsets);R->SetObjectField(TEXT("capture_timing"),Timing);
  if(auto E=Enemy(GuardId))if(auto Driver=E->GetStoneGuardDriver()){const auto& S=Driver->State();R->SetNumberField(TEXT("guard_initial_time"),S.InitialTime);R->SetArrayField(TEXT("guard_initial_position"),XY({S.InitialPosition.X,S.InitialPosition.Y}));R->SetNumberField(TEXT("guard_final_HP"),S.HP);R->SetNumberField(TEXT("guard_incoming_count"),S.ReceivedHits.size());TArray<JV> Events,Feedback;for(const auto& V:S.Issued){auto X=MakeShared<FJsonObject>();Id(X,TEXT("event"),V.EventId);Id(X,TEXT("entity"),V.EntityId);Id(X,TEXT("target"),V.TargetId);X->SetNumberField(TEXT("kind"),int32(V.Kind));X->SetNumberField(TEXT("at"),V.AtTime);X->SetNumberField(TEXT("end"),V.EndTime);X->SetNumberField(TEXT("amount"),V.Amount);X->SetArrayField(TEXT("from"),XY({V.From.X,V.From.Y}));X->SetArrayField(TEXT("to"),XY({V.To.X,V.To.Y}));X->SetObjectField(TEXT("action"),Action(V.Action));Events.Add(MakeShared<FJsonValueObject>(X));}for(const auto& V:E->GetGuardFeedback().Entries()){auto X=MakeShared<FJsonObject>();Id(X,TEXT("event"),V.EventId);Id(X,TEXT("entity"),V.EntityId);Id(X,TEXT("attack"),V.AttackId);Id(X,TEXT("target"),V.TargetId);Id(X,TEXT("foot_ordinal"),V.FootOrdinal);X->SetNumberField(TEXT("source_kind"),int32(V.SourceKind));X->SetStringField(TEXT("cue"),UTF8_TO_TCHAR(DungeonGuardFeedback::CueName(V.Cue)));X->SetNumberField(TEXT("at"),V.AtTime);X->SetNumberField(TEXT("actual_HP_loss"),V.ActualHPLoss);X->SetArrayField(TEXT("position"),XY({V.Position.X,V.Position.Y}));Feedback.Add(MakeShared<FJsonValueObject>(X));}R->SetArrayField(TEXT("guard_original_events"),Events);R->SetArrayField(TEXT("guard_feedback"),Feedback);TArray<JV> Hits;for(const auto& V:S.HitReceipts){auto X=MakeShared<FJsonObject>();Id(X,TEXT("attack"),V.AttackId);Id(X,TEXT("target"),V.TargetId);X->SetNumberField(TEXT("at"),V.AtTime);Hits.Add(MakeShared<FJsonValueObject>(X));}R->SetArrayField(TEXT("guard_original_hit_receipts"),Hits);}
  FDungeonFirstBatchGuardRoomView FinalRoom;if(Game.IsValid()&&Game->QueryFirstBatchGuardRoom(FinalRoom)){TArray<JV> Slots;for(const auto& V:FinalRoom.Slots){auto X=MakeShared<FJsonObject>();X->SetStringField(TEXT("slot"),V.SlotId);X->SetStringField(TEXT("content"),V.ContentId);Id(X,TEXT("entity"),V.EntityId);X->SetNumberField(TEXT("stage"),int32(V.Stage));X->SetNumberField(TEXT("warning_at"),V.WarningAt);X->SetNumberField(TEXT("materialized_at"),V.MaterializedAt);X->SetNumberField(TEXT("dead_at"),V.DeadAt);X->SetArrayField(TEXT("spawn"),XY(V.SpawnPosition));Slots.Add(MakeShared<FJsonValueObject>(X));}R->SetArrayField(TEXT("actual_formal_room_slots"),Slots);}
  FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(R.ToSharedRef(),Writer);const FString Path=Directory/TEXT("runtime-report.json");const bool Written=!Directory.IsEmpty()&&!IFileManager::Get().FileExists(*Path)&&FFileHelper::SaveStringToFile(Text,*Path,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);if(!Why.IsEmpty())UE_LOG(LogTemp,Error,TEXT("Guard Move7 proof: %s"),*Why);FPlatformMisc::RequestExitWithStatus(false,Passed&&Written?0:3);
 }
 void Tick(ADungeonGuardMoveProbeV001& Actor)
 {
  if(Stopped)return;const double Now=FPlatformTime::Seconds();auto G=Actor.GetWorld()->GetAuthGameMode<ADungeonGameMode>();auto C=UGameplayStatics::GetPlayerController(&Actor,0);auto H=C?Cast<ADungeonHUD>(C->GetHUD()):nullptr;
  if(!Game.IsValid()&&G&&C&&C->PlayerInput&&H){Game=G;Controller=C;HUD=H;Actor.AddTickPrerequisiteActor(G);Actor.AddTickPrerequisiteActor(H);return;}if(!Game.IsValid())return;
  if(PulseKey.IsValid()&&Now>=ReleaseAt){Key(PulseKey,false);PulseKey=FKey();NeutralUntil=Now+.04;}
  if(!Capturing){if(!Prewarm&&Now-Warm>=2.){Prewarm=true;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}else if(Now-Warm>18.)Finish(TEXT("Prewarm timeout"));return;}if(FinishOnFrame)return;
  auto P=G->PlayerFighter.Get();if(!Need(Now-Start<48.&&Now-PhaseWall<16.&&G==Game.Get()&&C==Controller.Get()&&H==HUD.Get()&&P&&C->GetPawn()==P&&!P->bDead&&!G->bGameOver,TEXT("Native input/room/player timeout or death")))return;
  FDungeonFirstBatchGuardRoomView Room;if(!Need(G->QueryFirstBatchGuardRoom(Room)&&Room.Slots.Num()==3&&G->GetEquipmentView().Config==EDungeonEquipmentRunConfig::FirstBatch,TEXT("Finite formal Guard room required")))return;
  if(!Run.IsValid()){RoomId=Room.RoomInstanceId;Epoch=G->GetRunPresentationEpoch();Run=Room.RunGuid;Owner=G->GetEquipmentView().OwnerId;Restart=G->GetRunRestartSerial();PlayerId=P->GetRuntimeEntityId();Sword=G->GetEquipmentView().Slots[G->GetEquipmentView().ActiveSlot].InstanceId;}
  if(!Need(Room.RunGuid==Run&&Room.RoomInstanceId==RoomId&&G->GetRunPresentationEpoch()==Epoch&&G->GetRunRestartSerial()==Restart,TEXT("Run restarted or player identity changed")))return;
  switch(Phase){case 0:if(!Need(G->bWaitingForStart&&G->GetSimulationTime()==0.&&P->Coins==20,TEXT("Await real Enter at0/20")))return;if(Pulse(EKeys::Enter))Next(1);break;
  case 1:if(!G->bWaitingForStart&&CanPulse()){DungeonEquipmentInventory::FItem I;I.ContentId="ARM-LGT-001";const auto X=G->RegisterEquipmentSource(TEXT("display.guard.move7.light.v001"),I,P->GetGroundPosition()+FVector2D(24.,0.),true);if(!Need(X.Ok()&&!X.Replayed,TEXT("Display LGT source registration failed")))return;Light=X.InstanceId;if(Pulse(EKeys::E))Next(2);}break;
  case 2:if(!G->GetEquipmentView().Action.Active&&G->GetEquipmentView().Slots[2].InstanceId==Light&&CanPulse()){const auto& V=G->GetEquipmentView();if(!Need(V.Slots[V.ActiveSlot].ContentId==TEXT("WPN-SWD-001")&&V.Slots[2].ContentId==TEXT("ARM-LGT-001")&&V.Stats.Poise==30.&&V.Stats.Armor==14.&&V.Stats.PhysicalVulnerabilityMultiplier==1.,TEXT("Actual committed SWD/baseLGT stats differ; never write them")))return;Next(3);}break;
  case 3:if(CanPulse()&&DiagnosticKill(Enemy(Room.Slots[0].EntityId)))Next(4);break;
  case 4:if(Room.Slots[1].Stage==EDungeonGuardRoomSlotStage::Materialized){if(!Need(Room.Slots[1].WarningAt>=Room.Slots[0].DeadAt+2.&&Room.Slots[1].MaterializedAt>=Room.Slots[1].WarningAt+1.2,TEXT("Original Bat warning shortened")))return;Next(5);}break;
  case 5:if(Now-PhaseWall>=.9&&DiagnosticKill(Enemy(Room.Slots[1].EntityId)))Next(6);break;
  case 6:if(Room.Slots[2].Stage==EDungeonGuardRoomSlotStage::Materialized){GuardId=Room.Slots[2].EntityId;if(!Need(Room.Slots[2].WarningAt>=Room.Slots[1].DeadAt+2.&&Room.Slots[2].MaterializedAt>=Room.Slots[2].WarningAt+1.2&&Enemy(GuardId)&&Enemy(GuardId)->GetStoneGuardDriver(),TEXT("Original Guard birth/warning missing")))return;BeforeHP=P->Health;DungeonFairytaleSwordEquipmentBinding::FBinding B;FString Why;if(!Need(DungeonFairytaleSwordEquipmentBinding::Resolve(*G,*P,B,Why),TEXT("Committed gear missing before route")))return;SwordVersion=B.WeaponVersion;LightVersion=B.ArmorVersion;Next(7);}break;

  case 7:{auto E=Enemy(GuardId);if(!Need(E&&E->GetStoneGuardDriver(),TEXT("Planned Guard missing before normal route")))return;if(FollowRoute(E))Next(8);break;}
  case 8:{auto E=Enemy(GuardId);if(!Need(E&&E->GetStoneGuardDriver(),TEXT("Planned Guard missing while native chase is observed")))return;
   if(CycleComplete){MoveStop();Next(9);break;}
   const auto& S=E->GetStoneGuardDriver()->State();const FVector2D Lead(S.InitialPosition.X+ApproachSide*500.,S.InitialPosition.Y);MoveTo(Lead);break;}
  case 9:MoveStop();if(BattlePinned&&ReadySeen>=3&&MoveCombatJoin&&RecoveryReadyJoin){Complete=true;Next(10);FinishOnFrame=true;}break;
  default:Finish(TEXT("Unexpected observer state"));break;}
 }
};
void FDungeonGuardMoveProofDeleter::operator()(FDungeonGuardMoveProofState* P)const{delete P;}
ADungeonGuardMoveProbeV001::ADungeonGuardMoveProbeV001(){PrimaryActorTick.bCanEverTick=true;}
ADungeonGuardMoveProbeV001::~ADungeonGuardMoveProbeV001()=default;
void ADungeonGuardMoveProbeV001::BeginPlay()
{
 Super::BeginPlay();Proof.Reset(new FDungeonGuardMoveProofState());Proof->Warm=FPlatformTime::Seconds();GIsDumpingMovie=0;FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),Proof->Directory);FParse::Value(FCommandLine::Get(),TEXT("DungeonGuardMoveApproachSide="),Proof->RequestedSide);
 if(Proof->Directory.IsEmpty()||FPaths::IsRelative(Proof->Directory)){Proof->Directory.Reset();Proof->Finish(TEXT("Absolute unused evidence directory required"));return;}Proof->Directory=FPaths::ConvertRelativePathToFull(Proof->Directory);FPaths::NormalizeDirectoryName(Proof->Directory);
 TArray<FString> Prior;IFileManager::Get().FindFiles(Prior,*(Proof->Directory/TEXT("*")),true,false);Prior.Remove(TEXT("native-lossless-capture.json"));if(Prior.Num()){Proof->Stopped=true;FPlatformMisc::RequestExitWithStatus(false,3);return;}IFileManager::Get().MakeDirectory(*Proof->Directory,true);
 for(const TCHAR* F:{TEXT("DungeonGuardMoveProofV001"),TEXT("DungeonFairytaleGuardMoveRigPreview"),TEXT("DungeonFairytaleGuardFullPreview"),TEXT("DungeonFairytaleGuardStompPreview"),TEXT("DungeonFairytaleSwordEquipmentBoundPreview"),TEXT("DungeonFairytaleSwordWalkPreview"),TEXT("DungeonContentProof"),TEXT("DungeonFastLosslessCapture"),TEXT("DungeonAsyncLosslessCapture")})if(!Proof->Need(FParse::Param(FCommandLine::Get(),F),FString(TEXT("Missing opt-in flag: "))+F))return;
 for(const TCHAR* F:{TEXT("DungeonHeroHurtProofV001"),TEXT("DungeonHeroDeathProofV001"),TEXT("DungeonHeroDodgeProofV001"),TEXT("DungeonGuardStompProofV001"),TEXT("DungeonGuardArtCombatProofV003"),TEXT("DungeonGuardArtKnown44Proof"),TEXT("DungeonGuardArtDeathProofV005"),TEXT("DungeonCombatRangeDebug")})if(!Proof->Need(!FParse::Param(FCommandLine::Get(),F),TEXT("Independent modes/default range must not share this native trial")))return;
 if(!Proof->Need(!FApp::UseFixedTimeStep()&&(Proof->RequestedSide==-1||Proof->RequestedSide==1),TEXT("Native pacing and real requested side required")))return;
 const auto& P=M::Profile();if(!Proof->Need(P.SourceClosureVerified&&P.TrialAllowed&&!P.FinalAccepted&&P.ProfileSHA256==TEXT("03156e971171f597ca504e9c0176d5a2fdf3c31c09b3eddae2995e2245193b51")&&P.SourceSnapshotSHA256==TEXT("a16a6a151ca0f6895c80ce108221bb3bed8f9c267c8016d142c18ed74f84cd94")&&P.Sources.Num()==7&&!P.TrialApprovalRecord.IsEmpty(),TEXT("Exact seven-source profile and separate Root runtime trial approval required")))return;
 TSet<FString> Unique;for(const auto& X:P.Sources){auto T=FindObject<UTexture2D>(nullptr,*X.TexturePath);if(!Proof->Need(!Unique.Contains(X.TexturePath)&&T&&T->GetClass()==UTexture2D::StaticClass()&&T->GetResource()&&!T->HasPendingRenderResourceInitialization()&&T->GetPathName()==X.TexturePath&&T->GetSizeX()==512&&T->GetSizeY()==512,TEXT("All seven approved Texture2D resources must be resident before Enter; no first-use LoadObject repair")))return;Unique.Add(X.TexturePath);auto J=MakeShared<FJsonObject>();J->SetNumberField(TEXT("component"),int32(X.Component));J->SetStringField(TEXT("texture"),T->GetPathName());J->SetStringField(TEXT("class"),T->GetClass()->GetName());J->SetStringField(TEXT("source_SHA"),X.SourceSHA256);J->SetStringField(TEXT("source_RGBA_SHA"),X.SourceRGBASHA256);J->SetNumberField(TEXT("source_native_batch_id"),X.NativeBatchId);J->SetNumberField(TEXT("width"),T->GetSizeX());J->SetNumberField(TEXT("height"),T->GetSizeY());J->SetBoolField(TEXT("resource_ready"),true);J->SetBoolField(TEXT("pending_initialization"),false);Proof->StartupTextures.Add(MakeShared<FJsonValueObject>(J));}
 GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Proof->Directory;FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonGuardMoveProbeV001::ScreenshotProcessed);
}
void ADungeonGuardMoveProbeV001::ScreenshotProcessed(){if(Proof)Proof->Observe();}
void ADungeonGuardMoveProbeV001::Tick(float D){Super::Tick(D);if(Proof)Proof->Tick(*this);}
void ADungeonGuardMoveProbeV001::EndPlay(const EEndPlayReason::Type R){FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);if(Proof&&!Proof->Stopped)Proof->Finish(TEXT("Native world ended before actual Move128/combat/Ready proof"));Super::EndPlay(R);}
