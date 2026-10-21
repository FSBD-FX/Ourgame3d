#include "DungeonHeroDodgeProbeV001.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonHUD.h"
#include "DungeonStoneGuardDriver.h"
#include "DungeonStoneBatDriver.h"
#include "DungeonFairytaleSwordDodgeDrawState.h"
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
namespace Dodge=DungeonFairytaleSwordDodgeV001;
TArray<JV> XY(FVector2D V){return {MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y)};}
TArray<JV> Strings(const TArray<FString>& A){TArray<JV> R;for(const auto& S:A)R.Add(MakeShared<FJsonValueString>(S));return R;}
void Id(JO O,const TCHAR* N,uint64 V){O->SetStringField(N,FString::Printf(TEXT("%llu"),V));}
const TCHAR* PhaseName(int32 P)
{switch(P){case 0:return TEXT("await_enter");case 1:return TEXT("register_display_LGT_request_E");case 2:return TEXT("await_actual_LGT_commit");case 3:return TEXT("Knight_diagnostic_only");case 4:return TEXT("await_formal_Bat");case 5:return TEXT("Bat_diagnostic_only");case 6:return TEXT("await_formal_Guard");case 7:return TEXT("normal_WASD_approach");case 8:return TEXT("normal_outward_staging_and_Shift");case 9:return TEXT("original_player_Dodge4");case 10:return TEXT("actual_Ready_join");case 11:return TEXT("actual_Walk_join");case 12:return TEXT("complete");default:return TEXT("invalid");}}
JO Action(const DungeonStoneGuard::FAction& A)
{
 auto O=MakeShared<FJsonObject>();Id(O,TEXT("attack_id"),A.AttackId);O->SetNumberField(TEXT("kind"),int32(A.Kind));O->SetNumberField(TEXT("facing"),A.Facing);O->SetBoolField(TEXT("in_progress"),A.InProgress);O->SetBoolField(TEXT("locked"),A.Locked);O->SetBoolField(TEXT("interrupted"),A.Interrupted);
 for(const auto& Pair:TArray<TPair<FString,double>>{{TEXT("start"),A.Start},{TEXT("lock_at"),A.LockAt},{TEXT("active_at"),A.ActiveAt},{TEXT("active_end"),A.ActiveEnd},{TEXT("recovery_end"),A.RecoveryEnd},{TEXT("cooldown_end"),A.CooldownEnd},{TEXT("damage"),A.Damage},{TEXT("stagger"),A.Stagger}})O->SetNumberField(Pair.Key,Pair.Value);
 O->SetArrayField(TEXT("origin"),XY({A.Origin.X,A.Origin.Y}));O->SetArrayField(TEXT("locked_center"),XY({A.LockedCenter.X,A.LockedCenter.Y}));return O;
}
JO Draw(const FDungeonFairytaleSwordDodgeDraw& D)
{
 auto O=MakeShared<FJsonObject>();const auto& P=D.Plan;
 Id(O,TEXT("draw_id"),D.DrawId);Id(O,TEXT("player_entity"),D.PlayerEntityId);O->SetNumberField(TEXT("sim"),D.SimulationTime);O->SetBoolField(TEXT("opt_in"),D.OptIn);O->SetBoolField(TEXT("drawn"),D.Drawn);O->SetBoolField(TEXT("atomic_preflight_ready"),D.AtomicPreflightReady);O->SetStringField(TEXT("missing_reason"),D.MissingReason);
 O->SetBoolField(TEXT("supported"),P.Supported);O->SetStringField(TEXT("profile"),P.ProfileId);O->SetNumberField(TEXT("frame"),P.Frame);O->SetNumberField(TEXT("facing"),P.Facing);O->SetNumberField(TEXT("nonempty_count"),P.NonemptyDrawCount);
 Id(O,TEXT("dodge_owner"),P.Dodge.OwnerId);Id(O,TEXT("dodge_action"),P.Dodge.ActionId);Id(O,TEXT("dodge_start_event"),P.Dodge.StartEventId);O->SetNumberField(TEXT("dodge_sample_time"),P.Dodge.SampleTime);O->SetNumberField(TEXT("dodge_start"),P.Dodge.Start);O->SetNumberField(TEXT("dodge_end"),P.Dodge.End);O->SetNumberField(TEXT("dodge_ready_at"),P.Dodge.ReadyAt);O->SetNumberField(TEXT("dodge_travelled"),P.Dodge.Travelled);O->SetNumberField(TEXT("dodge_block"),int32(P.Dodge.Block));O->SetNumberField(TEXT("dodge_finish"),int32(P.Dodge.Finish));O->SetArrayField(TEXT("dodge_direction"),XY(P.Dodge.Direction));O->SetBoolField(TEXT("dodge_invulnerable"),P.Dodge.Invulnerable);O->SetBoolField(TEXT("dodge_active"),P.Dodge.Active);O->SetNumberField(TEXT("dodge_elapsed"),P.Dodge.Elapsed);O->SetNumberField(TEXT("dodge_remaining"),P.Dodge.Remaining);
 O->SetArrayField(TEXT("context_ground"),XY(D.Context.GroundScreen));O->SetNumberField(TEXT("ui_scale"),D.Context.UIScale);O->SetNumberField(TEXT("jump_height"),D.Context.JumpHeight);
 O->SetArrayField(TEXT("root_source"),XY(P.RootSource));O->SetArrayField(TEXT("grip_source"),XY(P.GripSource));O->SetArrayField(TEXT("axis_artist"),XY(P.AxisArtist));O->SetArrayField(TEXT("body_top"),XY(P.BodyTop));O->SetArrayField(TEXT("grip_screen"),XY(P.GripScreen));O->SetArrayField(TEXT("sword_top"),XY(P.SwordTop));O->SetArrayField(TEXT("sword_pivot_uv"),XY(P.SwordPivotUV));
 O->SetNumberField(TEXT("canvas_size"),P.CanvasSize);O->SetNumberField(TEXT("source_to_screen_scale"),P.SourceToScreenScale);O->SetNumberField(TEXT("weapon_scale"),P.WeaponScale);O->SetNumberField(TEXT("weapon_width"),P.WeaponWidth);O->SetNumberField(TEXT("weapon_angle"),P.WeaponAngle);O->SetNumberField(TEXT("texture_u"),P.TextureU);O->SetNumberField(TEXT("texture_du"),P.TextureDU);
 const auto& B=P.Binding;O->SetStringField(TEXT("run"),B.RunGuid.ToString(EGuidFormats::Digits));Id(O,TEXT("owner"),B.OwnerId);Id(O,TEXT("weapon_instance"),B.WeaponInstanceId);Id(O,TEXT("weapon_version"),B.WeaponVersion);Id(O,TEXT("armor_instance"),B.ArmorInstanceId);Id(O,TEXT("armor_version"),B.ArmorVersion);O->SetStringField(TEXT("weapon_content"),B.WeaponContentId);O->SetStringField(TEXT("armor_content"),B.ArmorContentId);
 O->SetArrayField(TEXT("actual_stack"),Strings(D.ActualRenderedStack));TArray<JV> Color;for(double V:{double(D.Tint.R),double(D.Tint.G),double(D.Tint.B),double(D.Tint.A)})Color.Add(MakeShared<FJsonValueNumber>(V));O->SetArrayField(TEXT("tint"),Color);
 TArray<JV> Slots;for(const auto& S:D.Slots){auto X=MakeShared<FJsonObject>();X->SetNumberField(TEXT("slot"),S.SlotIndex);X->SetNumberField(TEXT("component"),int32(S.Component));X->SetStringField(TEXT("texture"),S.TexturePath);X->SetBoolField(TEXT("known_empty"),S.KnownOptionalEmpty);X->SetBoolField(TEXT("texture_ready"),S.TextureReady);X->SetBoolField(TEXT("drawn"),S.Drawn);X->SetArrayField(TEXT("top"),XY(S.Top));X->SetArrayField(TEXT("size"),XY(S.Size));X->SetArrayField(TEXT("uv"),XY(S.UV));X->SetArrayField(TEXT("uv_size"),XY(S.UVSize));X->SetNumberField(TEXT("rotation"),S.RotationDegrees);X->SetArrayField(TEXT("rotation_pivot"),XY(S.RotationPivot));X->SetNumberField(TEXT("draw_scale"),S.DrawScale);X->SetBoolField(TEXT("scale_position"),S.ScalePosition);TArray<JV> Tint;for(double C:{double(S.TraceTint.R),double(S.TraceTint.G),double(S.TraceTint.B),double(S.TraceTint.A)})Tint.Add(MakeShared<FJsonValueNumber>(C));X->SetArrayField(TEXT("trace_tint"),Tint);Slots.Add(MakeShared<FJsonValueObject>(X));}O->SetArrayField(TEXT("slots"),Slots);TArray<JV> Residents;for(const auto& T:D.ResidentTextures){auto X=MakeShared<FJsonObject>();X->SetStringField(TEXT("texture"),T.TexturePath);X->SetStringField(TEXT("class"),T.ClassName);X->SetNumberField(TEXT("width"),T.Width);X->SetNumberField(TEXT("height"),T.Height);X->SetBoolField(TEXT("resource_ready"),T.ResourceReady);X->SetBoolField(TEXT("pending_initialization"),T.PendingInitialization);Residents.Add(MakeShared<FJsonValueObject>(X));}O->SetArrayField(TEXT("resident_textures"),Residents);return O;
}
}
struct FDungeonHeroDodgeProofState
{
 FString Directory;bool Stopped=false,Prewarm=false,Capturing=false,Complete=false,FinishOnFrame=false,DodgePinned=false,ShiftIssued=false,RoutePlanned=false,RouteReached=false;
 TWeakObjectPtr<ADungeonGameMode> Game;TWeakObjectPtr<APlayerController> Controller;TWeakObjectPtr<ADungeonHUD> HUD;
 TMap<FKey,bool> Keys;FKey PulseKey;double ReleaseAt=0.,NeutralUntil=0.,Warm=0.,Start=0.,Stop=0.,PhaseWall=0.;int32 Phase=0,RequestedSide=0,ApproachSide=0,RouteStage=0;
 FGuid Run;uint64 Owner=0,Restart=0,Light=0,Sword=0,GuardId=0,PlayerId=0,DodgeAction=0,DodgeStartEvent=0,LastDodgeDraw=0,LastJoinDraw=0,SwordVersion=0,LightVersion=0;
 double DodgeStart=-1.,DodgeEnd=-1.,DodgeReadyAt=-1.,BeforeHP=0.,ShiftWindow=-1.,RouteLane=0.,LastMotionTo=-1.,AcceptedWalk=0.,WalkWindowStart=-1.;FVector2D RouteStart=FVector2D::ZeroVector,RouteGuard=FVector2D::ZeroVector;
 uint32 DodgeMask=0;int32 ReadySeen=0,WalkSeen=0;JO Report=MakeShared<FJsonObject>();TArray<JV> Inputs,Steps,Observations,Offsets,DiagnosticHits,RouteWitnesses,StartupTextures;
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
 bool PinDodge(ADungeonFighter* P)
 {
  const auto& S=P->GetDodgeState();if(S.Records.empty())return true;
  if(!Need(ShiftIssued&&S.Records.size()==1,TEXT("Only one normal fresh Shift action is permitted")))return false;
  const auto& R=S.Records.back();
  if(!DodgePinned)
  {
   if(!Need(Phase==8&&RouteReached&&S.Phase==DungeonDodge::EPhase::Dodging&&R.StartEventId&&R.ActionId&&R.Block==DungeonDodge::EBlock::None&&R.Direction.X==ApproachSide&&R.Direction.Y==0.&&R.End==R.Start+.4&&R.ReadyAt==R.Start+1.2,TEXT("First normal Shift did not start one outward original400ms action")))return false;
   DodgePinned=true;DodgeAction=R.ActionId;DodgeStartEvent=R.StartEventId;DodgeStart=R.Start;DodgeEnd=R.End;DodgeReadyAt=R.ReadyAt;MoveStop();Next(9);
  }
  return Need(R.ActionId==DodgeAction&&R.StartEventId==DodgeStartEvent&&R.Start==DodgeStart&&R.End==DodgeEnd&&R.ReadyAt==DodgeReadyAt,TEXT("Original Dodge owner/action/deadline changed"));
 }
 JO DodgeRecord(const DungeonDodge::FState& S,ADungeonFighter* P)
 {
  auto O=MakeShared<FJsonObject>();Id(O,TEXT("owner"),S.OwnerId);O->SetNumberField(TEXT("time"),S.Time);O->SetNumberField(TEXT("phase"),int32(S.Phase));O->SetArrayField(TEXT("position"),XY({S.Position.X,S.Position.Y}));O->SetNumberField(TEXT("record_count"),S.Records.size());
  if(S.Records.empty())return O;const auto& R=S.Records.back();Id(O,TEXT("action"),R.ActionId);Id(O,TEXT("start_event"),R.StartEventId);Id(O,TEXT("block_event"),R.BlockEventId);Id(O,TEXT("finish_event"),R.FinishEventId);
  O->SetNumberField(TEXT("start"),R.Start);O->SetNumberField(TEXT("end"),R.End);O->SetNumberField(TEXT("ready_at"),R.ReadyAt);O->SetNumberField(TEXT("travelled"),R.Travelled);O->SetNumberField(TEXT("blocked_at"),R.BlockedAt);O->SetNumberField(TEXT("finished_at"),R.FinishedAt);O->SetNumberField(TEXT("block"),int32(R.Block));O->SetNumberField(TEXT("finish"),int32(R.Finish));O->SetArrayField(TEXT("origin"),XY({R.Origin.X,R.Origin.Y}));O->SetArrayField(TEXT("direction"),XY({R.Direction.X,R.Direction.Y}));
  auto Receipt=MakeShared<FJsonObject>();Id(Receipt,TEXT("id"),R.OriginReceipt.Id);Id(Receipt,TEXT("after_action"),R.OriginReceipt.AfterActionId);Receipt->SetNumberField(TEXT("at"),R.OriginReceipt.AtTime);Receipt->SetArrayField(TEXT("position"),XY({R.OriginReceipt.Position.X,R.OriginReceipt.Position.Y}));O->SetObjectField(TEXT("origin_receipt"),Receipt);
  O->SetBoolField(TEXT("invulnerable_at_sample"),P->IsDodgeInvulnerableAt(S.Time));O->SetBoolField(TEXT("iframe_before_start"),P->IsDodgeInvulnerableAt(std::nextafter(R.Start+.06,R.Start)));O->SetBoolField(TEXT("iframe_at_start"),P->IsDodgeInvulnerableAt(R.Start+.06));O->SetBoolField(TEXT("iframe_before_end"),P->IsDodgeInvulnerableAt(std::nextafter(R.Start+.20,R.Start)));O->SetBoolField(TEXT("iframe_at_end"),P->IsDodgeInvulnerableAt(R.Start+.20));O->SetBoolField(TEXT("iframe_at_action_end"),P->IsDodgeInvulnerableAt(R.End));return O;
 }
 JO Facts()
 {
  auto O=MakeShared<FJsonObject>();auto G=Game.Get();auto H=HUD.Get();auto P=G?G->PlayerFighter.Get():nullptr;if(!G||!H||!P)return O;auto E=Enemy(GuardId);if(!PinDodge(P))return O;
  FDungeonDodgePresentationSample Q;const bool Query=P->QueryDodgePresentation(Q);const auto& V=G->GetEquipmentView();if(!Need(V.ActiveSlot>=0&&V.ActiveSlot<2,TEXT("Actual active weapon slot invalid")))return O;
  O->SetNumberField(TEXT("phase"),Phase);O->SetNumberField(TEXT("sim"),G->GetSimulationTime());O->SetArrayField(TEXT("ground"),XY(P->GetGroundPosition()));O->SetNumberField(TEXT("HP"),P->Health);O->SetNumberField(TEXT("facing"),P->Facing);O->SetStringField(TEXT("animation"),P->AnimationName);O->SetNumberField(TEXT("animation_time"),P->AnimationTime);O->SetBoolField(TEXT("dodge_query_ok"),Query);O->SetBoolField(TEXT("dodge_active"),Q.Active);O->SetNumberField(TEXT("dodge_elapsed"),Q.Elapsed);O->SetNumberField(TEXT("dodge_remaining"),Q.Remaining);O->SetNumberField(TEXT("poise_threshold"),P->GetPoiseThreshold());O->SetNumberField(TEXT("armor"),V.Stats.Armor);O->SetNumberField(TEXT("physical_vulnerability"),V.Stats.PhysicalVulnerabilityMultiplier);
  O->SetBoolField(TEXT("held_A"),Controller->IsInputKeyDown(EKeys::A));O->SetBoolField(TEXT("held_D"),Controller->IsInputKeyDown(EKeys::D));O->SetBoolField(TEXT("held_W"),Controller->IsInputKeyDown(EKeys::W));O->SetBoolField(TEXT("held_S"),Controller->IsInputKeyDown(EKeys::S));O->SetBoolField(TEXT("held_Shift"),Controller->IsInputKeyDown(EKeys::LeftShift));O->SetBoolField(TEXT("interface_visible"),H->GetInterfaceVisible());O->SetNumberField(TEXT("text_calls"),H->GetRenderedTextDrawCalls());O->SetArrayField(TEXT("rendered_stack"),Strings(H->GetRenderedPlayerDrawStack()));
  O->SetArrayField(TEXT("camera_ground"),XY(H->GetCameraGroundCenter()));
  Id(O,TEXT("weapon_instance"),V.Slots[V.ActiveSlot].InstanceId);Id(O,TEXT("armor_instance"),V.Slots[2].InstanceId);Id(O,TEXT("player_entity"),P->GetRuntimeEntityId());
  const auto& D=H->GetFairytaleSwordDodgeDraw();O->SetObjectField(TEXT("dodge_draw"),Draw(D));
  O->SetBoolField(TEXT("combat_range_debug"),H->IsCombatRangeDebugEnabled());O->SetNumberField(TEXT("combat_range_lines"),H->GetCombatRangeDebugLineCount());
  const auto& S=P->GetDodgeState();O->SetObjectField(TEXT("dodge_record"),DodgeRecord(S,P));
  DungeonFairytaleSwordEquipmentBinding::FBinding Binding;FString Why;
  if(!Need(DungeonFairytaleSwordEquipmentBinding::Resolve(*G,*P,Binding,Why),TEXT("Actual committed Dodge binding lost")))return O;
  Id(O,TEXT("weapon_version"),Binding.WeaponVersion);Id(O,TEXT("armor_version"),Binding.ArmorVersion);
  if(LightVersion&&!Need(Binding.WeaponInstanceId==Sword&&Binding.ArmorInstanceId==Light&&Binding.WeaponVersion==SwordVersion&&Binding.ArmorVersion==LightVersion,TEXT("Same actual equipment IDs/versions changed")))return O;
  if(DodgePinned&&P->AnimationName==TEXT("dodge")&&!Need(Query&&Q.Active,TEXT("Actual native Dodge label lost its read-only active query")))return O;
  if(DodgePinned&&Q.Active)
  {
   if(!Need(Phase==9&&D.DrawId>LastDodgeDraw&&D.PlayerEntityId==PlayerId&&D.SimulationTime==G->GetSimulationTime()&&D.Drawn&&D.OptIn&&D.AtomicPreflightReady&&D.Plan.Supported&&D.Plan.Frame>=0&&D.Plan.Frame<4&&D.Plan.Facing==ApproachSide&&D.Plan.Dodge.Active&&D.Plan.Dodge.Elapsed==Q.Elapsed&&D.Plan.Dodge.Remaining==Q.Remaining&&D.Plan.Binding.WeaponInstanceId==Sword&&D.Plan.Binding.ArmorInstanceId==Light&&D.Slots.Num()==9&&D.ActualRenderedStack==H->GetRenderedPlayerDrawStack()&&D.ActualRenderedStack.Num()==9&&D.ResidentTextures.Num()==33,TEXT("Actual Dodge draw/clock/committed gear/9 real quads/33 resources failed")))return O;
   LastDodgeDraw=D.DrawId;DodgeMask|=1u<<D.Plan.Frame;
   const auto& ActualRecord=S.Records.back();const double PhaseAges[]={0.,.1,.2,.3};int32 ExpectedFrame=0;for(int32 Frame=1;Frame<4;++Frame)if(S.Time>=DodgeStart+PhaseAges[Frame])ExpectedFrame=Frame;
   if(!Need(D.Plan.Frame==ExpectedFrame&&S.Time>=DodgeStart&&S.Time<DodgeEnd&&P->AnimationName==TEXT("dodge")&&P->AnimationTime==float(S.Time-DodgeStart)&&S.Position.X==ActualRecord.Origin.X+ActualRecord.Direction.X*ActualRecord.Travelled&&S.Position.Y==ActualRecord.Origin.Y+ActualRecord.Direction.Y*ActualRecord.Travelled&&P->GetGroundPosition()==FVector2D(S.Position.X,S.Position.Y),TEXT("Original absolute phase/float label/actual accepted physics position differs")))return O;
   if(!Need(S.OwnerId==PlayerId&&D.Plan.Dodge.OwnerId==PlayerId&&D.Plan.Dodge.ActionId==DodgeAction&&D.Plan.Dodge.StartEventId==DodgeStartEvent&&D.Plan.Dodge.SampleTime==S.Time&&D.Plan.Dodge.Start==DodgeStart&&D.Plan.Dodge.End==DodgeEnd&&D.Plan.Dodge.ReadyAt==DodgeReadyAt&&D.Plan.Dodge.Travelled==S.Records.back().Travelled&&Q.Elapsed==S.Time-DodgeStart&&Q.Invulnerable==P->IsDodgeInvulnerableAt(S.Time)&&S.Records.back().Block==DungeonDodge::EBlock::None,TEXT("Actual double sample/physics/iframe query differs from original Dodge record")))return O;
   for(const auto& T:D.ResidentTextures)if(!Need(T.ClassName==TEXT("Texture2D")&&T.Width==512&&T.Height==512&&T.ResourceReady&&!T.PendingInitialization,TEXT("Actual complete33 GPU resident set failed")))return O;
   for(const auto& T:D.Slots)if(!Need(T.Drawn&&T.TextureReady&&!T.KnownOptionalEmpty&&T.TraceTint==D.Tint,TEXT("Actual nine submitted quad/Tint failed")))return O;
  }
  const auto& B=H->GetFairytaleSwordDraw();auto J=MakeShared<FJsonObject>();Id(J,TEXT("draw_id"),B.DrawId);J->SetStringField(TEXT("clip"),B.Clip);J->SetBoolField(TEXT("active"),B.Active);J->SetBoolField(TEXT("supported"),B.Supported);J->SetBoolField(TEXT("walk"),B.WalkPose);J->SetBoolField(TEXT("texture_ready"),B.TextureReady);J->SetBoolField(TEXT("armor_drawn"),B.ArmorDrawn);J->SetNumberField(TEXT("facing"),B.Facing);J->SetNumberField(TEXT("frame"),B.Frame);Id(J,TEXT("weapon_instance"),B.InstanceId);J->SetArrayField(TEXT("stack"),Strings(B.DrawStack));O->SetObjectField(TEXT("join_draw"),J);
  FDungeonCompletedGroundMotion M;const bool Motion=P->QueryCompletedGroundMotion(M);auto N=MakeShared<FJsonObject>();N->SetBoolField(TEXT("query_ok"),Motion);N->SetBoolField(TEXT("published"),M.Published);N->SetBoolField(TEXT("grounded"),M.Grounded);N->SetBoolField(TEXT("ordinary"),M.OrdinaryEligible);N->SetBoolField(TEXT("intent"),M.HadMoveIntent);N->SetNumberField(TEXT("from_time"),M.FromTime);N->SetNumberField(TEXT("to_time"),M.ToTime);N->SetNumberField(TEXT("accepted"),M.AcceptedDistance);N->SetArrayField(TEXT("from"),XY(M.From));N->SetArrayField(TEXT("to"),XY(M.To));Id(N,TEXT("owner"),M.OwnerId);N->SetStringField(TEXT("run"),M.RunGuid.ToString(EGuidFormats::Digits));O->SetObjectField(TEXT("motion"),N);
  if(DodgePinned&&!Query&&!Q.Active&&!D.Drawn&&Phase==10&&B.DrawId>LastJoinDraw&&B.Active&&B.Supported&&!B.WalkPose&&B.Clip==TEXT("sword_ready_idle")&&B.TextureReady&&B.ArmorDrawn&&B.InstanceId==Sword&&B.EquipmentBinding.ArmorInstanceId==Light&&B.DrawStack==H->GetRenderedPlayerDrawStack()){LastJoinDraw=B.DrawId;++ReadySeen;}
  const bool Outward=Controller->IsInputKeyDown(ApproachSide>0?EKeys::D:EKeys::A)&&!Controller->IsInputKeyDown(ApproachSide>0?EKeys::A:EKeys::D)&&!Controller->IsInputKeyDown(EKeys::W)&&!Controller->IsInputKeyDown(EKeys::S);
  if(Phase==11&&!Query&&!Q.Active&&!D.Drawn&&B.DrawId>LastJoinDraw&&B.Active&&B.Supported&&B.WalkPose&&B.TextureReady&&B.ArmorDrawn&&B.InstanceId==Sword&&B.Facing==ApproachSide&&B.EquipmentBinding.ArmorInstanceId==Light&&Motion&&M.Published&&M.Grounded&&M.OrdinaryEligible&&M.HadMoveIntent&&M.OwnerId==Owner&&M.RunGuid==Run&&M.FromTime>=WalkWindowStart&&M.ToTime>LastMotionTo&&Outward&&(M.To.X-M.From.X)*ApproachSide>0.&&M.To.Y==M.From.Y&&M.AcceptedDistance>0.){LastJoinDraw=B.DrawId;LastMotionTo=M.ToTime;++WalkSeen;AcceptedWalk+=M.AcceptedDistance;}
  if(E&&E->GetStoneGuardDriver()){const auto& GuardState=E->GetStoneGuardDriver()->State();O->SetNumberField(TEXT("guard_HP"),GuardState.HP);O->SetNumberField(TEXT("guard_received_count"),GuardState.ReceivedHits.size());O->SetNumberField(TEXT("guard_hit_count"),GuardState.HitReceipts.size());O->SetObjectField(TEXT("guard_action"),Action(GuardState.Action));O->SetArrayField(TEXT("guard_ground"),XY(E->GetGroundPosition()));if(!Need(!E->bDead&&GuardState.HP==185.&&GuardState.ReceivedHits.empty(),TEXT("Formal Guard must remain living185 with no incoming proof damage")))return O;}
  return O;
 }
 void Observe()
 {
  if(Stopped)return;if(Prewarm&&!Capturing){if(!Need(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))>8,TEXT("Synchronous prewarm missing")))return;Start=PhaseWall=FPlatformTime::Seconds();Capturing=true;GIsDumpingMovie=-1;return;}if(!Capturing)return;
  const double T=FPlatformTime::Seconds()-Start;auto O=Facts();if(Stopped)return;O->SetNumberField(TEXT("wall_offset_s"),T);Observations.Add(MakeShared<FJsonValueObject>(O));Offsets.Add(MakeShared<FJsonValueNumber>(T));
  if(!Need(!HUD->GetInterfaceVisible()&&HUD->GetRenderedTextDrawCalls()==0,TEXT("Hidden interface drew UI text")))return;
  if(Phase==9){const auto& S=Game->PlayerFighter->GetDodgeState();if(S.Phase!=DungeonDodge::EPhase::Dodging){const auto& R=S.Records.back();if(!Need(DodgeMask==15&&R.Finish==DungeonDodge::EFinish::Completed&&R.Block==DungeonDodge::EBlock::None&&R.Travelled==185.&&R.FinishedAt==R.End,TEXT("One original Dodge ended without4phases/unblocked185/completed; no replay")))return;Next(10);}}
  if(FinishOnFrame)Finish();
 }
 void Finish(const FString& Why=FString())
 {
  if(Stopped)return;Stopped=true;Stop=FPlatformTime::Seconds();GIsDumpingMovie=0;TArray<FKey> Held;Keys.GetKeys(Held);for(FKey K:Held)Key(K,false);const bool Flushed=FlushFastLosslessProofScreenshots();const bool Passed=Why.IsEmpty()&&Complete&&Flushed&&!Observations.IsEmpty();
  Report->SetStringField(TEXT("schema"),TEXT("hero-SWD-LGT-Dodge4-native-observer-v001"));Report->SetStringField(TEXT("scenario"),TEXT("NormalShiftOutwardUnblockedDodge4"));Report->SetBoolField(TEXT("passed"),Passed);Report->SetBoolField(TEXT("flow_complete"),Complete);Report->SetStringField(TEXT("failure"),Why);Id(Report,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());Report->SetStringField(TEXT("run"),Run.ToString(EGuidFormats::Digits));Id(Report,TEXT("owner"),Owner);Id(Report,TEXT("restart_serial"),Restart);Id(Report,TEXT("guard_entity"),GuardId);Id(Report,TEXT("player_entity"),PlayerId);Id(Report,TEXT("sword_instance"),Sword);Id(Report,TEXT("light_instance"),Light);Id(Report,TEXT("dodge_action"),DodgeAction);Id(Report,TEXT("dodge_start_event"),DodgeStartEvent);Id(Report,TEXT("sword_version"),SwordVersion);Id(Report,TEXT("light_version"),LightVersion);Report->SetNumberField(TEXT("dodge_start"),DodgeStart);Report->SetNumberField(TEXT("dodge_end"),DodgeEnd);Report->SetNumberField(TEXT("dodge_ready_at"),DodgeReadyAt);Report->SetNumberField(TEXT("pre_guard_HP"),BeforeHP);Report->SetNumberField(TEXT("DodgeMask"),DodgeMask);Report->SetNumberField(TEXT("ReadySeen"),ReadySeen);Report->SetNumberField(TEXT("WalkSeen"),WalkSeen);Report->SetNumberField(TEXT("accepted_walk"),AcceptedWalk);Report->SetNumberField(TEXT("requested_approach_side"),RequestedSide);Report->SetNumberField(TEXT("actual_approach_side"),ApproachSide);
  Report->SetArrayField(TEXT("startup_resident_textures"),StartupTextures);Report->SetArrayField(TEXT("normal_inputs"),Inputs);Report->SetArrayField(TEXT("steps"),Steps);Report->SetArrayField(TEXT("observations"),Observations);Report->SetArrayField(TEXT("diagnostic_predecessor_hits"),DiagnosticHits);Report->SetArrayField(TEXT("route_witnesses"),RouteWitnesses);Report->SetBoolField(TEXT("player_or_Guard_public_damage_used"),false);Report->SetBoolField(TEXT("HP_poise_clock_actor_writes"),false);Report->SetBoolField(TEXT("silent_video"),true);Report->SetBoolField(TEXT("audio_recorded"),false);Report->SetBoolField(TEXT("visual_reviewed"),false);Report->SetBoolField(TEXT("native_async_capture_writes_flushed"),Flushed);Report->SetNumberField(TEXT("formal_complete_units"),0);
  auto T=MakeShared<FJsonObject>();T->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());T->SetNumberField(TEXT("capture_start_monotonic_s"),Start);T->SetNumberField(TEXT("capture_stop_monotonic_s"),Stop);T->SetArrayField(TEXT("frame_wall_offsets_s"),Offsets);Report->SetObjectField(TEXT("capture_timing"),T);
  if(auto E=Enemy(GuardId))if(auto D=E->GetStoneGuardDriver()){const auto& S=D->State();TArray<JV> Events,Receipts,Confirmed;for(const auto& V:S.Issued){auto X=MakeShared<FJsonObject>();Id(X,TEXT("event"),V.EventId);Id(X,TEXT("entity"),V.EntityId);Id(X,TEXT("target"),V.TargetId);X->SetNumberField(TEXT("kind"),int32(V.Kind));X->SetNumberField(TEXT("at"),V.AtTime);X->SetNumberField(TEXT("end"),V.EndTime);X->SetObjectField(TEXT("action"),Action(V.Action));Events.Add(MakeShared<FJsonValueObject>(X));}for(const auto& V:S.HitReceipts){auto X=MakeShared<FJsonObject>();Id(X,TEXT("attack"),V.AttackId);Id(X,TEXT("target"),V.TargetId);X->SetNumberField(TEXT("at"),V.AtTime);Receipts.Add(MakeShared<FJsonValueObject>(X));}for(const auto& V:E->GetGuardFeedback().Entries())if(V.ActualHPLoss>0.){auto X=MakeShared<FJsonObject>();Id(X,TEXT("event"),V.EventId);Id(X,TEXT("attack"),V.AttackId);Id(X,TEXT("target"),V.TargetId);X->SetNumberField(TEXT("at"),V.AtTime);X->SetNumberField(TEXT("actual_HP_loss"),V.ActualHPLoss);X->SetNumberField(TEXT("source_kind"),int32(V.SourceKind));Confirmed.Add(MakeShared<FJsonValueObject>(X));}Report->SetArrayField(TEXT("guard_original_events"),Events);Report->SetArrayField(TEXT("guard_original_hit_receipts"),Receipts);Report->SetArrayField(TEXT("guard_actual_confirmed_losses"),Confirmed);Report->SetNumberField(TEXT("guard_final_HP"),S.HP);Report->SetNumberField(TEXT("guard_incoming_count"),S.ReceivedHits.size());}
  FString Text;auto W=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Report.ToSharedRef(),W);const FString Path=Directory/TEXT("runtime-report.json");const bool Written=!Directory.IsEmpty()&&!IFileManager::Get().FileExists(*Path)&&FFileHelper::SaveStringToFile(Text,*Path,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);if(!Why.IsEmpty())UE_LOG(LogTemp,Error,TEXT("Hero Dodge4 proof: %s"),*Why);FPlatformMisc::RequestExitWithStatus(false,Passed&&Written?0:3);
 }
 void Tick(ADungeonHeroDodgeProbeV001& Actor)
 {
  if(Stopped)return;const double Now=FPlatformTime::Seconds();auto G=Actor.GetWorld()->GetAuthGameMode<ADungeonGameMode>();auto C=UGameplayStatics::GetPlayerController(&Actor,0);auto H=C?Cast<ADungeonHUD>(C->GetHUD()):nullptr;
  if(!Game.IsValid()&&G&&C&&C->PlayerInput&&H){Game=G;Controller=C;HUD=H;Actor.AddTickPrerequisiteActor(G);Actor.AddTickPrerequisiteActor(H);return;}if(!Game.IsValid())return;
  if(PulseKey.IsValid()&&Now>=ReleaseAt){Key(PulseKey,false);PulseKey=FKey();NeutralUntil=Now+.04;}
  if(!Capturing){if(!Prewarm&&Now-Warm>=2.){Prewarm=true;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}else if(Now-Warm>18.)Finish(TEXT("Prewarm timeout"));return;}if(FinishOnFrame)return;
  auto P=G->PlayerFighter.Get();if(!Need(Now-Start<42.&&Now-PhaseWall<16.&&G==Game.Get()&&C==Controller.Get()&&H==HUD.Get()&&P&&C->GetPawn()==P&&!P->bDead&&!G->bGameOver,TEXT("Native input/room/player timeout or death")))return;
  FDungeonFirstBatchGuardRoomView Room;if(!Need(G->QueryFirstBatchGuardRoom(Room)&&Room.Slots.Num()==3&&G->GetEquipmentView().Config==EDungeonEquipmentRunConfig::FirstBatch,TEXT("Finite formal Guard room required")))return;
  if(!Run.IsValid()){Run=Room.RunGuid;Owner=G->GetEquipmentView().OwnerId;Restart=G->GetRunRestartSerial();PlayerId=P->GetRuntimeEntityId();Sword=G->GetEquipmentView().Slots[G->GetEquipmentView().ActiveSlot].InstanceId;}
  if(!Need(Room.RunGuid==Run&&G->GetRunRestartSerial()==Restart,TEXT("Run restarted or player identity changed")))return;
  switch(Phase){case 0:if(!Need(G->bWaitingForStart&&G->GetSimulationTime()==0.&&P->Coins==20,TEXT("Await real Enter at0/20")))return;if(Pulse(EKeys::Enter))Next(1);break;
  case 1:if(!G->bWaitingForStart&&CanPulse()){DungeonEquipmentInventory::FItem I;I.ContentId="ARM-LGT-001";const auto X=G->RegisterEquipmentSource(TEXT("display.hero.dodge.light.v001"),I,P->GetGroundPosition()+FVector2D(24.,0.),true);if(!Need(X.Ok()&&!X.Replayed,TEXT("Display LGT source registration failed")))return;Light=X.InstanceId;if(Pulse(EKeys::E))Next(2);}break;
  case 2:if(!G->GetEquipmentView().Action.Active&&G->GetEquipmentView().Slots[2].InstanceId==Light&&CanPulse()){const auto& V=G->GetEquipmentView();if(!Need(V.Slots[V.ActiveSlot].ContentId==TEXT("WPN-SWD-001")&&V.Slots[2].ContentId==TEXT("ARM-LGT-001")&&V.Stats.Poise==30.&&V.Stats.Armor==14.&&V.Stats.PhysicalVulnerabilityMultiplier==1.,TEXT("Actual committed SWD/baseLGT stats differ; never write them")))return;Next(3);}break;
  case 3:if(CanPulse()&&DiagnosticKill(Enemy(Room.Slots[0].EntityId)))Next(4);break;
  case 4:if(Room.Slots[1].Stage==EDungeonGuardRoomSlotStage::Materialized){if(!Need(Room.Slots[1].WarningAt>=Room.Slots[0].DeadAt+2.&&Room.Slots[1].MaterializedAt>=Room.Slots[1].WarningAt+1.2,TEXT("Original Bat warning shortened")))return;Next(5);}break;
  case 5:if(Now-PhaseWall>=.9&&DiagnosticKill(Enemy(Room.Slots[1].EntityId)))Next(6);break;
  case 6:if(Room.Slots[2].Stage==EDungeonGuardRoomSlotStage::Materialized){GuardId=Room.Slots[2].EntityId;if(!Need(Room.Slots[2].WarningAt>=Room.Slots[1].DeadAt+2.&&Room.Slots[2].MaterializedAt>=Room.Slots[2].WarningAt+1.2&&Enemy(GuardId)&&Enemy(GuardId)->GetStoneGuardDriver(),TEXT("Original Guard birth/warning missing")))return;BeforeHP=P->Health;DungeonFairytaleSwordEquipmentBinding::FBinding B;FString Why;if(!Need(DungeonFairytaleSwordEquipmentBinding::Resolve(*G,*P,B,Why),TEXT("Committed gear missing before route")))return;SwordVersion=B.WeaponVersion;LightVersion=B.ArmorVersion;Next(7);}break;
  case 7:{auto E=Enemy(GuardId);if(!Need(E&&E->GetStoneGuardDriver(),TEXT("Formal Guard missing before normal route")))return;if(FollowRoute(E))Next(8);break;}
  case 8:{auto E=Enemy(GuardId);if(!Need(E&&E->GetStoneGuardDriver(),TEXT("Formal Guard disappeared")))return;if(ShiftWindow<0.)ShiftWindow=G->GetSimulationTime();
   if(ShiftIssued){MoveStop();if(!Need(G->GetSimulationTime()-ShiftWindow<1.,TEXT("Single natural Shift did not start an admitted action")))return;break;}
   Key(ApproachSide>0?EKeys::D:EKeys::A,true);Key(ApproachSide>0?EKeys::A:EKeys::D,false);Key(EKeys::W,false);Key(EKeys::S,false);
   FDungeonCompletedGroundMotion M;const bool Motion=P->QueryCompletedGroundMotion(M);const auto Pos=P->GetGroundPosition();
   if(P->Facing==float(ApproachSide)&&Motion&&M.OrdinaryEligible&&M.HadMoveIntent&&M.ToTime>ShiftWindow&&M.AcceptedDistance>0.&&(M.To.X-M.From.X)*ApproachSide>0.&&CanPulse())
   {if(!Need(SegmentLegal(Pos,Pos+FVector2D(ApproachSide*185.,0.)),TEXT("Requested outward185 path not legal; never teleport or hide block")))return;ShiftIssued=Pulse(EKeys::LeftShift);}
   break;}
  case 9:MoveStop();break;
  case 10:MoveStop();if(ReadySeen>=2){LastMotionTo=-1.;AcceptedWalk=0.;WalkWindowStart=G->GetSimulationTime();Next(11);}break;
  case 11:Key(ApproachSide>0?EKeys::D:EKeys::A,true);if(WalkSeen>=4&&AcceptedWalk>=24.){MoveStop();Complete=true;Next(12);FinishOnFrame=true;}break;
  default:Finish(TEXT("Unexpected observer state"));break;}
 }
};
void FDungeonHeroDodgeProofDeleter::operator()(FDungeonHeroDodgeProofState* P)const{delete P;}
ADungeonHeroDodgeProbeV001::ADungeonHeroDodgeProbeV001(){PrimaryActorTick.bCanEverTick=true;}
ADungeonHeroDodgeProbeV001::~ADungeonHeroDodgeProbeV001()=default;
void ADungeonHeroDodgeProbeV001::BeginPlay()
{
 Super::BeginPlay();Proof.Reset(new FDungeonHeroDodgeProofState());Proof->Warm=FPlatformTime::Seconds();GIsDumpingMovie=0;FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),Proof->Directory);FParse::Value(FCommandLine::Get(),TEXT("DungeonHeroDodgeApproachSide="),Proof->RequestedSide);
 if(Proof->Directory.IsEmpty()||FPaths::IsRelative(Proof->Directory)){Proof->Directory.Reset();Proof->Finish(TEXT("Absolute unused evidence directory required"));return;}Proof->Directory=FPaths::ConvertRelativePathToFull(Proof->Directory);FPaths::NormalizeDirectoryName(Proof->Directory);
 TArray<FString> Prior;IFileManager::Get().FindFiles(Prior,*(Proof->Directory/TEXT("*")),true,false);Prior.Remove(TEXT("native-lossless-capture.json"));if(Prior.Num()){Proof->Stopped=true;FPlatformMisc::RequestExitWithStatus(false,3);return;}IFileManager::Get().MakeDirectory(*Proof->Directory,true);
 for(const TCHAR* F:{TEXT("DungeonHeroDodgeProofV001"),TEXT("DungeonFairytaleSwordDodgePreview"),TEXT("DungeonFairytaleSwordEquipmentBoundPreview"),TEXT("DungeonFairytaleSwordWalkPreview"),TEXT("DungeonFairytaleGuardFullPreview"),TEXT("DungeonFairytaleGuardStompPreview"),TEXT("DungeonContentProof"),TEXT("DungeonFastLosslessCapture"),TEXT("DungeonAsyncLosslessCapture")})if(!Proof->Need(FParse::Param(FCommandLine::Get(),F),FString(TEXT("Missing opt-in flag: "))+F))return;
 for(const TCHAR* F:{TEXT("DungeonHeroHurtProofV001"),TEXT("DungeonHeroDeathProofV001"),TEXT("DungeonGuardStompProofV001"),TEXT("DungeonGuardArtCombatProofV003"),TEXT("DungeonGuardArtKnown44Proof"),TEXT("DungeonGuardArtDeathProofV005"),TEXT("DungeonFairytaleWalkProof")})if(!Proof->Need(!FParse::Param(FCommandLine::Get(),F),TEXT("Independent observer modes cannot share one controller")))return;
 if(!Proof->Need(!FApp::UseFixedTimeStep()&&(Proof->RequestedSide==-1||Proof->RequestedSide==1),TEXT("Native pacing and side[-1,+1] required")))return;
 const auto& Profile=Dodge::Profile();if(!Proof->Need(Profile.SourceClosureVerified&&Profile.SourceClosureSHA256==TEXT("7b62e4e15616c8ada14826ab926361e9a78666f78639eb0e253fbaca50727097"),TEXT("Exact reviewed Dodge source profile missing")))return;
 TSet<FString> Unique;int32 Empty=0;for(const auto& Frame:Profile.Frames)for(const auto& Source:Frame.Layers){auto T=FindObject<UTexture2D>(nullptr,*Source.TexturePath);if(!Proof->Need(!Unique.Contains(Source.TexturePath)&&T&&T->GetResource()&&!T->HasPendingRenderResourceInitialization()&&T->GetPathName()==Source.TexturePath&&T->GetSizeX()==512&&T->GetSizeY()==512,TEXT("All32 nonempty Dodge textures must already be resident before Enter; no first-use repair")))return;Unique.Add(Source.TexturePath);if(Source.KnownOptionalEmpty)++Empty;auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("frame"),Frame.Frame);O->SetNumberField(TEXT("component"),int32(Source.Component));O->SetStringField(TEXT("texture"),T->GetPathName());O->SetStringField(TEXT("class"),T->GetClass()->GetName());O->SetNumberField(TEXT("width"),T->GetSizeX());O->SetNumberField(TEXT("height"),T->GetSizeY());O->SetBoolField(TEXT("resident"),true);O->SetBoolField(TEXT("known_empty"),Source.KnownOptionalEmpty);O->SetNumberField(TEXT("source_alpha_nonzero"),Source.SourceAlphaNonzero);O->SetStringField(TEXT("source_SHA"),Source.SourceSHA256);O->SetStringField(TEXT("source_RGBA_SHA"),Source.SourceRGBASHA256);Proof->StartupTextures.Add(MakeShared<FJsonValueObject>(O));}
 auto Sword=FindObject<UTexture2D>(nullptr,*Profile.SwordTexturePath);if(!Proof->Need(Unique.Num()==32&&Empty==0&&Sword&&Sword->GetResource()&&!Sword->HasPendingRenderResourceInitialization()&&Sword->GetSizeX()==512&&Sword->GetSizeY()==512,TEXT("Exact32 + reused independent sword preload required")))return;auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("texture"),Sword->GetPathName());O->SetStringField(TEXT("class"),Sword->GetClass()->GetName());O->SetNumberField(TEXT("width"),Sword->GetSizeX());O->SetNumberField(TEXT("height"),Sword->GetSizeY());O->SetBoolField(TEXT("resident"),true);O->SetBoolField(TEXT("sword"),true);Proof->StartupTextures.Add(MakeShared<FJsonValueObject>(O));
 GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Proof->Directory;FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonHeroDodgeProbeV001::ScreenshotProcessed);
}
void ADungeonHeroDodgeProbeV001::ScreenshotProcessed(){if(Proof)Proof->Observe();}
void ADungeonHeroDodgeProbeV001::Tick(float D){Super::Tick(D);if(Proof)Proof->Tick(*this);}
void ADungeonHeroDodgeProbeV001::EndPlay(const EEndPlayReason::Type R){FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);if(Proof&&!Proof->Stopped)Proof->Finish(TEXT("Native world ended before original Dodge proof complete"));Super::EndPlay(R);}
