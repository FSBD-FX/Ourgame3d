#include "DungeonGuardStompProbeV001.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonHUD.h"
#include "DungeonStoneGuardDriver.h"
#include "DungeonStoneBatDriver.h"
#include "DungeonFairytaleGuardStompProfileV004.h"
#include "DungeonRoomLayout.h"
#include "DungeonProofScreenshots.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/Texture2D.h"
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
namespace Full=DungeonFairytaleGuardFullV003;
TArray<JV> XY(FVector2D V){return {MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y)};}
TArray<JV> Strings(const TArray<FString>& A){TArray<JV> R;for(const auto& S:A)R.Add(MakeShared<FJsonValueString>(S));return R;}
void Id(JO O,const TCHAR* N,uint64 V){O->SetStringField(N,FString::Printf(TEXT("%llu"),V));}

const TCHAR* PhaseName(int32 P){static const TCHAR* N[]={TEXT("await_enter"),TEXT("normal_E_LGT"),TEXT("await_commit"),TEXT("Knight_diagnostic"),TEXT("await_Bat"),TEXT("Bat_diagnostic"),TEXT("await_Guard"),TEXT("normal_body_route"),TEXT("first_natural_Stomp_cycle"),TEXT("complete")};return P>=0&&P<UE_ARRAY_COUNT(N)?N[P]:TEXT("invalid");}
const Full::FRow* TrialRow(Full::EClip Clip){for(const auto& Row:DungeonFairytaleGuardStompV004::ProfileStompV004())if(Row.Clip==Clip)return &Row;return nullptr;}
FString Json(JO O){FString T;auto W=TJsonWriterFactory<>::Create(&T);FJsonSerializer::Serialize(O.ToSharedRef(),W);return T;}
JO Action(const DungeonStoneGuard::FAction& A)
{
 auto O=MakeShared<FJsonObject>();Id(O,TEXT("attack_id"),A.AttackId);O->SetNumberField(TEXT("kind"),int32(A.Kind));
 O->SetBoolField(TEXT("in_progress"),A.InProgress);O->SetBoolField(TEXT("locked"),A.Locked);O->SetBoolField(TEXT("window_issued"),A.WindowIssued);O->SetBoolField(TEXT("interrupted"),A.Interrupted);
 O->SetNumberField(TEXT("start"),A.Start);O->SetNumberField(TEXT("lock_at"),A.LockAt);O->SetNumberField(TEXT("active_at"),A.ActiveAt);O->SetNumberField(TEXT("active_end"),A.ActiveEnd);O->SetNumberField(TEXT("recovery_end"),A.RecoveryEnd);O->SetNumberField(TEXT("cooldown_end"),A.CooldownEnd);
 O->SetNumberField(TEXT("interrupted_at"),A.InterruptedAt);O->SetNumberField(TEXT("completed_at"),A.CompletedAt);O->SetNumberField(TEXT("damage"),A.Damage);O->SetNumberField(TEXT("stagger"),A.Stagger);O->SetNumberField(TEXT("facing"),A.Facing);
 O->SetNumberField(TEXT("origin_z"),A.Origin.Z);O->SetNumberField(TEXT("locked_center_z"),A.LockedCenter.Z);O->SetNumberField(TEXT("target_z"),A.Target.Z);O->SetArrayField(TEXT("origin"),XY({A.Origin.X,A.Origin.Y}));O->SetArrayField(TEXT("locked_center"),XY({A.LockedCenter.X,A.LockedCenter.Y}));O->SetArrayField(TEXT("target"),XY({A.Target.X,A.Target.Y}));return O;
}
JO Draw(const FDungeonFairytaleGuardFullDrawV003& D)
{
 auto O=MakeShared<FJsonObject>();const auto& S=D.Selection;
 Id(O,TEXT("DrawId"),D.DrawId);Id(O,TEXT("EntityId"),D.EntityId);
 auto Q=MakeShared<FJsonObject>();Q->SetBoolField(TEXT("Valid"),S.Valid);Q->SetBoolField(TEXT("MaterialHit"),S.MaterialHit);Q->SetBoolField(TEXT("TerminalPresentation"),S.TerminalPresentation);Q->SetBoolField(TEXT("DeathAfterglow"),S.DeathAfterglow);Q->SetNumberField(TEXT("DeathAge"),S.DeathAge);
 Q->SetStringField(TEXT("Clip"),UTF8_TO_TCHAR(DungeonFairytaleGuardFullV003::ClipName(S.Clip)));Q->SetNumberField(TEXT("Frame"),S.Frame);Q->SetNumberField(TEXT("Facing"),S.Facing);
 Id(Q,TEXT("EntityId"),S.EntityId);Id(Q,TEXT("AttackId"),S.AttackId);Id(Q,TEXT("SourceEventId"),S.SourceEventId);Id(Q,TEXT("MaterialEventId"),S.MaterialEventId);Q->SetNumberField(TEXT("Phase"),int32(S.Phase));
 Q->SetNumberField(TEXT("SampleTime"),S.SampleTime);Q->SetNumberField(TEXT("IntervalStart"),S.IntervalStart);Q->SetNumberField(TEXT("IntervalEnd"),S.IntervalEnd);Q->SetNumberField(TEXT("AcceptedDistance"),S.AcceptedDistance);Q->SetNumberField(TEXT("DistancePhase"),S.DistancePhase);O->SetObjectField(TEXT("Selection"),Q);
 O->SetBoolField(TEXT("OptIn"),D.OptIn);O->SetBoolField(TEXT("TrialAllowed"),D.TrialAllowed);O->SetBoolField(TEXT("FinalAccepted"),D.FinalAccepted);O->SetBoolField(TEXT("RegistrationReady"),D.RegistrationReady);O->SetBoolField(TEXT("TextureReady"),D.TextureReady);O->SetBoolField(TEXT("Drawn"),D.Drawn);O->SetBoolField(TEXT("ProceduralFallback"),D.ProceduralFallback);O->SetBoolField(TEXT("WholebodyIncludesAxe"),D.WholebodyIncludesAxe);O->SetBoolField(TEXT("RequestedRowTrialAllowed"),D.RequestedRowTrialAllowed);
 O->SetNumberField(TEXT("NativeSourceId"),D.NativeSourceId);O->SetNumberField(TEXT("AssetFrame"),D.AssetFrame);O->SetStringField(TEXT("RequestedClip"),D.RequestedClip);O->SetStringField(TEXT("AssetClip"),D.AssetClip);O->SetStringField(TEXT("TexturePath"),D.TexturePath);O->SetStringField(TEXT("SourceSHA256"),D.SourceSHA256);O->SetStringField(TEXT("SourceRGBASHA256"),D.SourceRGBASHA256);O->SetStringField(TEXT("SourceIndexSHA256"),D.SourceIndexSHA256);O->SetStringField(TEXT("RequestedTrialApprovalRecord"),D.RequestedTrialApprovalRecord);O->SetNumberField(TEXT("PivotAuthority"),int32(D.PivotAuthority));O->SetStringField(TEXT("TrialApprovalRecord"),D.TrialApprovalRecord);O->SetStringField(TEXT("RegistrationEvidenceSHA256"),D.RegistrationEvidenceSHA256);O->SetStringField(TEXT("MissingReason"),D.MissingReason);
 O->SetNumberField(TEXT("StandingExtent"),D.StandingExtent);O->SetNumberField(TEXT("TargetBodyHeight"),D.TargetBodyHeight);O->SetNumberField(TEXT("RowScale"),D.RowScale);O->SetNumberField(TEXT("CanvasSize"),D.CanvasSize);O->SetArrayField(TEXT("SourceFloorPivot"),XY(D.SourceFloorPivot));O->SetArrayField(TEXT("GroundScreen"),XY(D.GroundScreen));O->SetArrayField(TEXT("TopScreen"),XY(D.TopScreen));O->SetArrayField(TEXT("DrawStack"),Strings(D.DrawStack));O->SetStringField(TEXT("ProfileId"),D.ProfileId);O->SetBoolField(TEXT("QuadSubmitted"),D.QuadSubmitted);O->SetArrayField(TEXT("QuadTop"),XY(D.QuadTop));O->SetArrayField(TEXT("QuadSize"),XY(D.QuadSize));O->SetArrayField(TEXT("QuadUV"),XY(D.QuadUV));O->SetArrayField(TEXT("QuadUVSize"),XY(D.QuadUVSize));O->SetArrayField(TEXT("QuadRotationPivot"),XY(D.QuadRotationPivot));O->SetNumberField(TEXT("QuadRotationDegrees"),D.QuadRotationDegrees);O->SetNumberField(TEXT("QuadDrawScale"),D.QuadDrawScale);O->SetBoolField(TEXT("QuadScalePosition"),D.QuadScalePosition);O->SetNumberField(TEXT("UIScale"),D.UIScale);TArray<JV> Color;for(double V:{double(D.QuadTint.R),double(D.QuadTint.G),double(D.QuadTint.B),double(D.QuadTint.A)})Color.Add(MakeShared<FJsonValueNumber>(V));O->SetArrayField(TEXT("QuadTint"),Color);TArray<JV> Residents;for(const auto& T:D.RowResidents){auto X=MakeShared<FJsonObject>();X->SetStringField(TEXT("TexturePath"),T.TexturePath);X->SetStringField(TEXT("ClassName"),T.ClassName);X->SetNumberField(TEXT("Width"),T.Width);X->SetNumberField(TEXT("Height"),T.Height);X->SetBoolField(TEXT("ResourceReady"),T.ResourceReady);X->SetBoolField(TEXT("PendingInitialization"),T.PendingInitialization);Residents.Add(MakeShared<FJsonValueObject>(X));}O->SetArrayField(TEXT("RowResidents"),Residents);return O;
}}
struct FDungeonGuardStompProofState
{
 FString Directory;bool Stopped=false,Prewarm=false,Capturing=false,Complete=false,RoutePlanned=false,RouteReached=false,CyclePinned=false;
 TWeakObjectPtr<ADungeonGameMode> Game;TWeakObjectPtr<APlayerController> Controller;TWeakObjectPtr<ADungeonHUD> HUD;
 TMap<FKey,bool> Keys;FKey PulseKey;double ReleaseAt=0.,NeutralUntil=0.,Warm=0.,Start=0.,Stop=0.,PhaseWall=0.,RouteLane=0.,BeforeHP=-1.,ConfirmedLoss=0.;int32 Phase=0,RequestedSide=0,ApproachSide=0,RouteStage=0;
 FGuid Run;uint64 Owner=0,Restart=0,Light=0,Sword=0,GuardId=0,PlayerId=0,LastConfirmedEvent=0,LastGuardDraw=0,CycleAttackId=0;
 FVector2D RouteStart=FVector2D::ZeroVector,RouteGuard=FVector2D::ZeroVector;DungeonStoneGuard::FAction CycleAction;
 uint32 WindupMask=0,ActiveMask=0,RecoveryMask=0;bool BeforeReady=false,WUActiveJoin=false,ActiveRecoveryJoin=false,AfterReady=false;int32 StompConfirmedHits=0;
 JO Report=MakeShared<FJsonObject>(),PreviousDraw;TArray<JV> Inputs,Steps,Observations,Offsets,DiagnosticHits,RouteWitnesses,StartupTextures,HitWitnesses,Joins;
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


 bool AtSide(ADungeonFighter* E)const{const auto D=Game->PlayerFighter->GetGroundPosition()-E->GetGroundPosition();return RouteReached&&D.X*ApproachSide>=120.&&D.X*ApproachSide<=160.&&FMath::Abs(D.Y)<=6.;}
 bool PinHits(ADungeonFighter* P,ADungeonFighter* E)
 {
  if(!E||!E->GetStoneGuardDriver())return true;const auto& S=E->GetStoneGuardDriver()->State();
  for(const auto& R:E->GetGuardFeedback().Entries())if(R.SourceKind==DungeonStoneGuard::EEventKind::Hit&&R.TargetId==PlayerId&&R.ActualHPLoss>0.&&R.EventId>LastConfirmedEvent)
  {
   const DungeonStoneGuard::FEvent* Event=nullptr;for(const auto& V:S.Issued)if(V.EventId==R.EventId)Event=&V;bool Receipt=false;for(const auto& V:S.HitReceipts)if(V.AttackId==R.AttackId&&V.TargetId==PlayerId&&V.AtTime==R.AtTime)Receipt=true;
   if(!Need(Phase==8&&RouteReached&&BeforeHP>0.&&Event&&Receipt&&Event->Kind==DungeonStoneGuard::EEventKind::Hit&&Event->AtTime==R.AtTime&&Event->TargetId==PlayerId&&Event->Action.AttackId==R.AttackId&&R.AtTime>=Event->Action.ActiveAt&&R.AtTime<Event->Action.ActiveEnd,TEXT("Original Guard actual hit/window/receipt identity invalid")))return false;
   const double ChainBefore=BeforeHP-ConfirmedLoss;ConfirmedLoss+=R.ActualHPLoss;const double ChainAfter=BeforeHP-ConfirmedLoss;
   if(!Need(ChainBefore>0.&&ChainAfter>0.&&P->Health>0.f&&!P->bDead&&!Game->bGameOver,TEXT("Natural hit killed hero before complete first Stomp cycle; preserve failure, never heal")))return false;
   auto X=MakeShared<FJsonObject>();Id(X,TEXT("event"),R.EventId);Id(X,TEXT("attack"),R.AttackId);X->SetNumberField(TEXT("at"),R.AtTime);X->SetNumberField(TEXT("actual_HP_loss"),R.ActualHPLoss);X->SetNumberField(TEXT("chain_before"),ChainBefore);X->SetNumberField(TEXT("chain_after"),ChainAfter);X->SetObjectField(TEXT("action"),Action(Event->Action));HitWitnesses.Add(MakeShared<FJsonValueObject>(X));LastConfirmedEvent=R.EventId;if(Event->Action.Kind==DungeonStoneGuard::EAttack::Stomp)++StompConfirmedHits;
  }
  return Need(BeforeHP<0.||FMath::Abs(P->Health-(BeforeHP-ConfirmedLoss))<1.e-4,TEXT("Hero actualHP differs from all original Guard ConfirmHit losses"));
 }
 bool PinCycle(ADungeonFighter* E)
 {
  const auto& S=E->GetStoneGuardDriver()->State();if(CyclePinned)return true;
  const DungeonStoneGuard::FEvent* First=nullptr;for(const auto& V:S.Issued)if(V.Kind==DungeonStoneGuard::EEventKind::AttackStarted&&V.Action.Kind==DungeonStoneGuard::EAttack::Stomp){First=&V;break;}
  if(!First)return true;
  if(!Need(Phase==8&&AtSide(E)&&First->Action.AttackId==2&&S.Action.AttackId==First->Action.AttackId&&S.Phase==DungeonStoneGuard::EPhase::Windup&&S.Time>=First->Action.Start&&S.Time<First->Action.Start+.15,TEXT("First natural Aid2 Stomp Windup0 already missed; never select/replay later attack")))return false;
  CyclePinned=true;CycleAttackId=First->Action.AttackId;CycleAction=First->Action;return true;
 }
 void Join(const TCHAR* Name,JO Current)
 {
  auto X=MakeShared<FJsonObject>();X->SetStringField(TEXT("name"),Name);X->SetNumberField(TEXT("before_observation"),Observations.Num()-1);X->SetNumberField(TEXT("after_observation"),Observations.Num());X->SetObjectField(TEXT("before_draw"),PreviousDraw);X->SetObjectField(TEXT("after_draw"),Current);Joins.Add(MakeShared<FJsonValueObject>(X));
 }
 JO Facts()
 {
  auto O=MakeShared<FJsonObject>();auto G=Game.Get();auto H=HUD.Get();auto P=G?G->PlayerFighter.Get():nullptr;if(!G||!H||!P)return O;auto E=Enemy(GuardId);if(!PinHits(P,E)||!Need(!P->bDead&&!G->bGameOver&&P->Health>0.f,TEXT("Actual live player required through Recovery/Ready")))return O;
  O->SetNumberField(TEXT("phase"),Phase);O->SetNumberField(TEXT("sim"),G->GetSimulationTime());O->SetArrayField(TEXT("player_ground"),XY(P->GetGroundPosition()));O->SetArrayField(TEXT("camera_ground"),XY(H->GetCameraGroundCenter()));O->SetNumberField(TEXT("player_HP"),P->Health);O->SetBoolField(TEXT("dead"),P->bDead);O->SetBoolField(TEXT("game_over"),G->bGameOver);O->SetBoolField(TEXT("interface_visible"),H->GetInterfaceVisible());O->SetNumberField(TEXT("text_calls"),H->GetRenderedTextDrawCalls());O->SetBoolField(TEXT("combat_range_debug"),H->IsCombatRangeDebugEnabled());O->SetNumberField(TEXT("combat_range_lines"),H->GetCombatRangeDebugLineCount());
  const auto& V=G->GetEquipmentView();Id(O,TEXT("weapon_instance"),V.Slots[V.ActiveSlot].InstanceId);Id(O,TEXT("armor_instance"),V.Slots[2].InstanceId);O->SetNumberField(TEXT("armor"),V.Stats.Armor);O->SetNumberField(TEXT("poise"),V.Stats.Poise);O->SetArrayField(TEXT("player_rendered_stack"),Strings(H->GetRenderedPlayerDrawStack()));
  if(!E||!E->GetStoneGuardDriver())return O;const auto& S=E->GetStoneGuardDriver()->State();if(!Need(S.HP==185.&&S.ReceivedHits.empty()&&!E->bDead,TEXT("Probe may never damage or change Guard"))||!PinCycle(E))return O;
  O->SetNumberField(TEXT("guard_time"),S.Time);O->SetNumberField(TEXT("guard_phase"),int32(S.Phase));O->SetNumberField(TEXT("guard_HP"),S.HP);O->SetNumberField(TEXT("guard_incoming_count"),S.ReceivedHits.size());O->SetNumberField(TEXT("occupied_until"),S.OccupiedUntil);O->SetNumberField(TEXT("idle_ready_at"),S.IdleReadyAt);O->SetNumberField(TEXT("wake_end"),S.WakeEnd);O->SetArrayField(TEXT("guard_ground"),XY(E->GetGroundPosition()));O->SetObjectField(TEXT("guard_action"),Action(S.Action));O->SetBoolField(TEXT("actual_side_eligible"),AtSide(E));
  TArray<JV> Draws;JO Current;
  for(const auto& D:H->GetFairytaleGuardFullDraws())
  {
   auto X=Draw(D);Draws.Add(MakeShared<FJsonValueObject>(X));if(D.EntityId!=GuardId)continue;
   if(!Need(D.DrawId>LastGuardDraw&&D.Selection.Valid&&D.ProfileId==TEXT("GuardStomp50V004"),TEXT("Missing new actual full-overlay draw identity/profile")))return O;LastGuardDraw=D.DrawId;
   const auto* Row=TrialRow(D.Selection.Clip);const bool Known=Row&&Row->SourcePoseApproved&&Row->NativeSourceId>0;
   if(Known&&!Need(D.Drawn&&D.QuadSubmitted&&D.TextureReady&&D.RegistrationReady&&D.TrialAllowed&&!D.FinalAccepted&&!D.ProceduralFallback&&D.DrawStack.Num()==1&&D.DrawStack[0]==D.TexturePath&&D.WholebodyIncludesAxe&&D.MissingReason.IsEmpty(),TEXT("Approved wholebody overlay did not submit exact one quad")))return O;
   if(Known){if(!Need(Row->IsAlias()||D.RowResidents.Num()==Row->Frames.Num(),TEXT("Complete actual selected-row resource facts absent")))return O;for(const auto& T:D.RowResidents)if(!Need(T.ClassName==TEXT("Texture2D")&&T.Width==512&&T.Height==512&&T.ResourceReady&&!T.PendingInitialization,TEXT("Actual selected row texture resource not ready")))return O;}
   const auto& Q=D.Selection;Current=X;
   if(CyclePinned&&Q.AttackId==CycleAttackId&&AtSide(E)&&D.Drawn)
   {
    if(Q.Clip==Full::EClip::StompWindup){if(!Need(Q.SampleTime>=CycleAction.Start&&Q.SampleTime<CycleAction.ActiveAt,TEXT("WU source outside original half-open window")))return O;WindupMask|=1u<<Q.Frame;if(Q.Frame==0&&PreviousDraw&&PreviousDraw->GetObjectField(TEXT("Selection"))->GetStringField(TEXT("Clip"))==TEXT("Ready")){BeforeReady=true;Join(TEXT("Ready-to-StompWU0"),X);}}
    if(Q.Clip==Full::EClip::StompActive){if(!Need(Q.SampleTime>=CycleAction.ActiveAt&&Q.SampleTime<CycleAction.ActiveEnd,TEXT("Active source outside original half-open window")))return O;ActiveMask|=1u<<Q.Frame;if(Q.Frame==0&&PreviousDraw&&PreviousDraw->GetObjectField(TEXT("Selection"))->GetStringField(TEXT("Clip"))==TEXT("StompWindup")&&PreviousDraw->GetObjectField(TEXT("Selection"))->GetNumberField(TEXT("Frame"))==5){WUActiveJoin=true;Join(TEXT("StompWU5-to-Active0"),X);}}
    if(Q.Clip==Full::EClip::StompRecovery){if(!Need(Q.SampleTime>=CycleAction.ActiveEnd&&Q.SampleTime<CycleAction.RecoveryEnd,TEXT("Recovery source outside original half-open window")))return O;RecoveryMask|=1u<<Q.Frame;if(Q.Frame==0&&PreviousDraw&&PreviousDraw->GetObjectField(TEXT("Selection"))->GetStringField(TEXT("Clip"))==TEXT("StompActive")&&PreviousDraw->GetObjectField(TEXT("Selection"))->GetNumberField(TEXT("Frame"))==1){ActiveRecoveryJoin=true;Join(TEXT("StompActive1-to-Recovery0"),X);}}
   }
   if(CyclePinned&&AtSide(E)&&Q.Clip==Full::EClip::Ready&&Q.SampleTime>=CycleAction.RecoveryEnd&&PreviousDraw&&PreviousDraw->GetObjectField(TEXT("Selection"))->GetStringField(TEXT("Clip"))==TEXT("StompRecovery")&&PreviousDraw->GetObjectField(TEXT("Selection"))->GetNumberField(TEXT("Frame"))==3){AfterReady=true;Join(TEXT("StompRecovery3-to-actual-Ready"),X);}
  }
  O->SetArrayField(TEXT("guard_draws"),Draws);PreviousDraw=Current;return O;
 }
 void Observe()
 {
  if(Stopped)return;if(Prewarm&&!Capturing){if(!Need(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))>8,TEXT("Synchronous prewarm missing")))return;Start=PhaseWall=FPlatformTime::Seconds();Capturing=true;GIsDumpingMovie=-1;return;}if(!Capturing)return;
  const double T=FPlatformTime::Seconds()-Start;auto O=Facts();if(Stopped)return;O->SetNumberField(TEXT("wall_offset_s"),T);Observations.Add(MakeShared<FJsonValueObject>(O));Offsets.Add(MakeShared<FJsonValueNumber>(T));
  if(!Need(!HUD->GetInterfaceVisible()&&HUD->GetRenderedTextDrawCalls()==0&&!HUD->IsCombatRangeDebugEnabled()&&HUD->GetCombatRangeDebugLineCount()==0,TEXT("Hidden interface/default-off combat range required")))return;
  if(CyclePinned)if(auto E=Enemy(GuardId))
  {const double N=E->GetStoneGuardDriver()->State().Time;if(N>=CycleAction.ActiveAt&&(!BeforeReady||WindupMask!=63)){Finish(TEXT("Original WU900ms ended without6/sourceReady join"));return;}if(N>=CycleAction.ActiveEnd&&(!WUActiveJoin||ActiveMask!=3)){Finish(TEXT("Original Active150ms ended without2x75ms/sameAid/join"));return;}if(N>=CycleAction.RecoveryEnd&&(!ActiveRecoveryJoin||RecoveryMask!=15)){Finish(TEXT("Original Recovery1500ms ended without4x375ms/sameAid/join"));return;}}
  if(CyclePinned&&WindupMask==63&&ActiveMask==3&&RecoveryMask==15&&BeforeReady&&WUActiveJoin&&ActiveRecoveryJoin&&AfterReady&&StompConfirmedHits==1){Complete=true;Next(9);Finish();}
 }

 void Finish(const FString& Why=FString())
 {
  if(Stopped)return;Stopped=true;Stop=FPlatformTime::Seconds();GIsDumpingMovie=0;TArray<FKey> Held;Keys.GetKeys(Held);for(FKey K:Held)Key(K,false);const bool Flushed=FlushFastLosslessProofScreenshots();const bool Passed=Why.IsEmpty()&&Complete&&Flushed&&!Observations.IsEmpty();
  Report->SetStringField(TEXT("schema"),TEXT("guard-Stomp50-native-observer-v001"));Report->SetStringField(TEXT("scenario"),TEXT("FirstNaturalStompAid2Cycle"));Report->SetBoolField(TEXT("passed"),Passed);Report->SetBoolField(TEXT("flow_complete"),Complete);Report->SetStringField(TEXT("failure"),Why);Id(Report,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());Report->SetStringField(TEXT("run"),Run.ToString(EGuidFormats::Digits));Id(Report,TEXT("owner"),Owner);Id(Report,TEXT("guard_entity"),GuardId);Id(Report,TEXT("player_entity"),PlayerId);Id(Report,TEXT("sword_instance"),Sword);Id(Report,TEXT("light_instance"),Light);Id(Report,TEXT("cycle_attack_id"),CycleAttackId);Report->SetObjectField(TEXT("cycle_action_at_pin"),Action(CycleAction));Report->SetNumberField(TEXT("requested_approach_side"),RequestedSide);Report->SetNumberField(TEXT("actual_approach_side"),ApproachSide);Report->SetNumberField(TEXT("pre_guard_HP"),BeforeHP);Report->SetNumberField(TEXT("confirmed_HP_loss"),ConfirmedLoss);Report->SetNumberField(TEXT("StompConfirmedHits"),StompConfirmedHits);Report->SetNumberField(TEXT("StompWindupMask"),WindupMask);Report->SetNumberField(TEXT("StompActiveMask"),ActiveMask);Report->SetNumberField(TEXT("StompRecoveryMask"),RecoveryMask);
  Report->SetArrayField(TEXT("joins"),Joins);Report->SetArrayField(TEXT("startup_resident_textures"),StartupTextures);Report->SetArrayField(TEXT("normal_inputs"),Inputs);Report->SetArrayField(TEXT("steps"),Steps);Report->SetArrayField(TEXT("observations"),Observations);Report->SetArrayField(TEXT("diagnostic_predecessor_hits"),DiagnosticHits);Report->SetArrayField(TEXT("route_witnesses"),RouteWitnesses);Report->SetArrayField(TEXT("guard_hit_witnesses"),HitWitnesses);Report->SetBoolField(TEXT("player_or_Guard_public_damage_used"),false);Report->SetBoolField(TEXT("HP_poise_clock_actor_writes"),false);Report->SetBoolField(TEXT("silent_video"),true);Report->SetBoolField(TEXT("audio_recorded"),false);Report->SetBoolField(TEXT("visual_reviewed"),false);Report->SetNumberField(TEXT("formal_complete_units"),0);Report->SetBoolField(TEXT("native_async_capture_writes_flushed"),Flushed);
  auto T=MakeShared<FJsonObject>();T->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());T->SetNumberField(TEXT("capture_start_monotonic_s"),Start);T->SetNumberField(TEXT("capture_stop_monotonic_s"),Stop);T->SetArrayField(TEXT("frame_wall_offsets_s"),Offsets);Report->SetObjectField(TEXT("capture_timing"),T);
  if(auto E=Enemy(GuardId))if(auto D=E->GetStoneGuardDriver())
  {
   const auto& S=D->State();TArray<JV> Events,Windows,Closures,Receipts,Confirmed;
   for(const auto& V:S.Issued){auto X=MakeShared<FJsonObject>();Id(X,TEXT("event"),V.EventId);Id(X,TEXT("entity"),V.EntityId);Id(X,TEXT("target"),V.TargetId);X->SetNumberField(TEXT("kind"),int32(V.Kind));X->SetNumberField(TEXT("at"),V.AtTime);X->SetNumberField(TEXT("end"),V.EndTime);X->SetNumberField(TEXT("amount"),V.Amount);X->SetObjectField(TEXT("action"),Action(V.Action));Events.Add(MakeShared<FJsonValueObject>(X));}
   for(const auto& V:S.Windows){auto X=MakeShared<FJsonObject>();Id(X,TEXT("attack"),V.AttackId);Id(X,TEXT("event"),V.EventId);X->SetNumberField(TEXT("kind"),int32(V.Kind));X->SetNumberField(TEXT("start"),V.Start);X->SetNumberField(TEXT("end"),V.End);X->SetNumberField(TEXT("damage"),V.Damage);X->SetNumberField(TEXT("stagger"),V.Stagger);X->SetNumberField(TEXT("facing"),V.Facing);X->SetArrayField(TEXT("center"),XY({V.Center.X,V.Center.Y}));X->SetNumberField(TEXT("center_z"),V.Center.Z);Windows.Add(MakeShared<FJsonValueObject>(X));}
   for(const auto& V:S.Closures){auto X=MakeShared<FJsonObject>();Id(X,TEXT("attack"),V.AttackId);X->SetNumberField(TEXT("at"),V.AtTime);Closures.Add(MakeShared<FJsonValueObject>(X));}
   for(const auto& V:S.HitReceipts){auto X=MakeShared<FJsonObject>();Id(X,TEXT("attack"),V.AttackId);Id(X,TEXT("target"),V.TargetId);X->SetNumberField(TEXT("at"),V.AtTime);Receipts.Add(MakeShared<FJsonValueObject>(X));}
   for(const auto& V:E->GetGuardFeedback().Entries())if(V.ActualHPLoss>0.){auto X=MakeShared<FJsonObject>();Id(X,TEXT("event"),V.EventId);Id(X,TEXT("attack"),V.AttackId);Id(X,TEXT("target"),V.TargetId);X->SetNumberField(TEXT("at"),V.AtTime);X->SetNumberField(TEXT("actual_HP_loss"),V.ActualHPLoss);Confirmed.Add(MakeShared<FJsonValueObject>(X));}
   Report->SetArrayField(TEXT("guard_original_events"),Events);Report->SetArrayField(TEXT("guard_original_windows"),Windows);Report->SetArrayField(TEXT("guard_original_closures"),Closures);Report->SetArrayField(TEXT("guard_original_hit_receipts"),Receipts);Report->SetArrayField(TEXT("guard_actual_confirmed_losses"),Confirmed);Report->SetNumberField(TEXT("guard_final_HP"),S.HP);Report->SetNumberField(TEXT("guard_incoming_count"),S.ReceivedHits.size());
  }
  const FString Path=Directory/TEXT("runtime-report.json");const bool Written=!Directory.IsEmpty()&&!IFileManager::Get().FileExists(*Path)&&FFileHelper::SaveStringToFile(Json(Report),*Path,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);if(!Why.IsEmpty())UE_LOG(LogTemp,Error,TEXT("Guard Stomp50: %s"),*Why);FPlatformMisc::RequestExitWithStatus(false,Passed&&Written?0:3);
 }
 void Tick(ADungeonGuardStompProbeV001& Actor)
 {
  if(Stopped)return;const double Now=FPlatformTime::Seconds();auto G=Actor.GetWorld()->GetAuthGameMode<ADungeonGameMode>();auto C=UGameplayStatics::GetPlayerController(&Actor,0);auto H=C?Cast<ADungeonHUD>(C->GetHUD()):nullptr;
  if(!Game.IsValid()&&G&&C&&C->PlayerInput&&H){Game=G;Controller=C;HUD=H;Actor.AddTickPrerequisiteActor(G);Actor.AddTickPrerequisiteActor(H);return;}if(!Game.IsValid())return;
  if(PulseKey.IsValid()&&Now>=ReleaseAt){Key(PulseKey,false);PulseKey=FKey();NeutralUntil=Now+.04;}
  if(!Capturing){if(!Prewarm&&Now-Warm>=2.){Prewarm=true;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}else if(Now-Warm>18.)Finish(TEXT("Prewarm timeout"));return;}
  auto P=G->PlayerFighter.Get();if(!Need(Now-Start<42.&&Now-PhaseWall<24.&&G==Game.Get()&&C==Controller.Get()&&H==HUD.Get()&&P&&C->GetPawn()==P,TEXT("Native input/room/player timeout or identity mismatch")))return;if(!PinHits(P,Enemy(GuardId)))return;
  if(!Need(!P->bDead&&!G->bGameOver&&P->Health>0.f,TEXT("Alive actual hero through original Stomp cycle required")))return;
  FDungeonFirstBatchGuardRoomView Room;if(!Need(G->QueryFirstBatchGuardRoom(Room)&&Room.Slots.Num()==3&&G->GetEquipmentView().Config==EDungeonEquipmentRunConfig::FirstBatch,TEXT("Finite formal Guard room required")))return;
  if(!Run.IsValid()){Run=Room.RunGuid;Owner=G->GetEquipmentView().OwnerId;Restart=G->GetRunRestartSerial();PlayerId=P->GetRuntimeEntityId();Sword=G->GetEquipmentView().Slots[G->GetEquipmentView().ActiveSlot].InstanceId;}
  if(!Need(Room.RunGuid==Run&&G->GetRunRestartSerial()==Restart,TEXT("Run restarted or player identity changed")))return;
  switch(Phase){case 0:if(!Need(G->bWaitingForStart&&G->GetSimulationTime()==0.&&P->Coins==20,TEXT("Await real Enter at0/20")))return;if(Pulse(EKeys::Enter))Next(1);break;
  case 1:if(!G->bWaitingForStart&&CanPulse()){DungeonEquipmentInventory::FItem I;I.ContentId="ARM-LGT-001";const auto X=G->RegisterEquipmentSource(TEXT("display.guard.stomp.light.v001"),I,P->GetGroundPosition()+FVector2D(24.,0.),true);if(!Need(X.Ok()&&!X.Replayed,TEXT("Display LGT source registration failed")))return;Light=X.InstanceId;if(Pulse(EKeys::E))Next(2);}break;
  case 2:if(!G->GetEquipmentView().Action.Active&&G->GetEquipmentView().Slots[2].InstanceId==Light&&CanPulse()){const auto& V=G->GetEquipmentView();if(!Need(V.Slots[V.ActiveSlot].ContentId==TEXT("WPN-SWD-001")&&V.Slots[2].ContentId==TEXT("ARM-LGT-001")&&V.Stats.Poise==30.&&V.Stats.Armor==14.&&V.Stats.PhysicalVulnerabilityMultiplier==1.,TEXT("Actual normal E committed SWD/LGT stats differ; never write")))return;Next(3);}break;
  case 3:if(CanPulse()&&DiagnosticKill(Enemy(Room.Slots[0].EntityId)))Next(4);break;
  case 4:if(Room.Slots[1].Stage==EDungeonGuardRoomSlotStage::Materialized){if(!Need(Room.Slots[1].WarningAt>=Room.Slots[0].DeadAt+2.&&Room.Slots[1].MaterializedAt>=Room.Slots[1].WarningAt+1.2,TEXT("Original Bat warning shortened")))return;Next(5);}break;
  case 5:if(Now-PhaseWall>=.9&&DiagnosticKill(Enemy(Room.Slots[1].EntityId)))Next(6);break;
  case 6:if(Room.Slots[2].Stage==EDungeonGuardRoomSlotStage::Materialized){GuardId=Room.Slots[2].EntityId;if(!Need(Room.Slots[2].WarningAt>=Room.Slots[1].DeadAt+2.&&Room.Slots[2].MaterializedAt>=Room.Slots[2].WarningAt+1.2&&Enemy(GuardId)&&Enemy(GuardId)->GetStoneGuardDriver(),TEXT("Original Guard birth/warning missing")))return;BeforeHP=P->Health;Next(7);}break;
  case 7:{auto E=Enemy(GuardId);if(!Need(E&&E->GetStoneGuardDriver(),TEXT("Formal Guard missing before normal route")))return;if(FollowRoute(E)){Next(8);}break;}
  case 8:{auto E=Enemy(GuardId);if(!Need(E&&E->GetStoneGuardDriver(),TEXT("Formal Guard disappeared")))return;MoveStop();if(P->Facing!=float(-ApproachSide))Key(ApproachSide>0?EKeys::A:EKeys::D,true);break;}

  default:Finish(TEXT("Unexpected Stomp observer state"));break;}
 }
};
void FDungeonGuardStompProofDeleter::operator()(FDungeonGuardStompProofState* P)const{delete P;}
ADungeonGuardStompProbeV001::ADungeonGuardStompProbeV001(){PrimaryActorTick.bCanEverTick=true;}
ADungeonGuardStompProbeV001::~ADungeonGuardStompProbeV001()=default;
void ADungeonGuardStompProbeV001::BeginPlay()
{
 Super::BeginPlay();Proof.Reset(new FDungeonGuardStompProofState());Proof->Warm=FPlatformTime::Seconds();GIsDumpingMovie=0;FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),Proof->Directory);FParse::Value(FCommandLine::Get(),TEXT("DungeonGuardStompApproachSide="),Proof->RequestedSide);
 if(Proof->Directory.IsEmpty()||FPaths::IsRelative(Proof->Directory)){Proof->Directory.Reset();Proof->Finish(TEXT("Absolute unused evidence directory required"));return;}Proof->Directory=FPaths::ConvertRelativePathToFull(Proof->Directory);FPaths::NormalizeDirectoryName(Proof->Directory);
 TArray<FString> Prior;IFileManager::Get().FindFiles(Prior,*(Proof->Directory/TEXT("*")),true,false);Prior.Remove(TEXT("native-lossless-capture.json"));if(Prior.Num()){Proof->Stopped=true;FPlatformMisc::RequestExitWithStatus(false,3);return;}IFileManager::Get().MakeDirectory(*Proof->Directory,true);
 for(const TCHAR* F:{TEXT("DungeonGuardStompProofV001"),TEXT("DungeonFairytaleGuardStompPreview"),TEXT("DungeonFairytaleSwordEquipmentBoundPreview"),TEXT("DungeonFairytaleSwordWalkPreview"),TEXT("DungeonFairytaleGuardFullPreview"),TEXT("DungeonContentProof"),TEXT("DungeonFastLosslessCapture"),TEXT("DungeonAsyncLosslessCapture")})if(!Proof->Need(FParse::Param(FCommandLine::Get(),F),FString(TEXT("Missing opt-in flag: "))+F))return;
 for(const TCHAR* F:{TEXT("DungeonHeroDeathProofV001"),TEXT("DungeonHeroHurtProofV001"),TEXT("DungeonGuardArtCombatProofV003"),TEXT("DungeonGuardArtKnown44Proof"),TEXT("DungeonGuardArtDeathProofV005"),TEXT("DungeonFairytaleWalkProof"),TEXT("DungeonCombatRangeDebug"),TEXT("DungeonGuardRoomFlowProof"),TEXT("DungeonGuardRunSaveProof"),TEXT("DungeonGuardRunRestoreProof"),TEXT("DungeonFairytaleEquipmentBoundProof"),TEXT("DungeonFairytaleSwordBodyProof"),TEXT("DungeonRunContinueProof")})if(!Proof->Need(!FParse::Param(FCommandLine::Get(),F),TEXT("Independent observer modes/default range flags cannot share this controller")))return;
 if(!Proof->Need(!FApp::UseFixedTimeStep()&&(Proof->RequestedSide==-1||Proof->RequestedSide==1),TEXT("Native pacing and explicitside[-1,+1] required")))return;
 int32 Unique=0;TSet<FString> Paths;for(const auto& Row:DungeonFairytaleGuardStompV004::ProfileStompV004())
 {
  if(!Row.SourcePoseApproved||Row.NativeSourceId<=0)continue;if(!Proof->Need(Full::TrialGateFull(Row).IsEmpty()&&!Row.FinalAccepted,TEXT("Every approved overlay row needs actual Root limited trial")))return;if(Row.IsAlias())continue;int32 Frame=0;
  for(const auto& F:Row.Frames){auto T=FindObject<UTexture2D>(nullptr,*F.TexturePath);if(!Proof->Need(!Paths.Contains(F.TexturePath)&&T&&T->GetClass()==UTexture2D::StaticClass()&&T->GetResource()&&!T->HasPendingRenderResourceInitialization()&&T->GetPathName()==F.TexturePath&&T->GetSizeX()==512&&T->GetSizeY()==512,TEXT("Complete50 must already be GPU ready before Enter, no first-use LoadObject")))return;Paths.Add(F.TexturePath);auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("clip"),UTF8_TO_TCHAR(Full::ClipName(Row.Clip)));O->SetNumberField(TEXT("frame"),Frame++);O->SetNumberField(TEXT("native_source_id"),Row.NativeSourceId);O->SetStringField(TEXT("texture"),T->GetPathName());O->SetStringField(TEXT("class"),T->GetClass()->GetName());O->SetNumberField(TEXT("width"),T->GetSizeX());O->SetNumberField(TEXT("height"),T->GetSizeY());O->SetBoolField(TEXT("resident"),true);O->SetStringField(TEXT("source_SHA"),F.SourceSHA256);O->SetStringField(TEXT("source_RGBA_SHA"),F.SourceRGBASHA256);Proof->StartupTextures.Add(MakeShared<FJsonValueObject>(O));++Unique;}
 }
 if(!Proof->Need(Unique==50&&Full::LogicalFrameBudget()==57,TEXT("Exact50 overlay and unchanged57 selector contract required")))return;
 GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Proof->Directory;FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonGuardStompProbeV001::ScreenshotProcessed);
}
void ADungeonGuardStompProbeV001::ScreenshotProcessed(){if(Proof)Proof->Observe();}
void ADungeonGuardStompProbeV001::Tick(float D){Super::Tick(D);if(Proof)Proof->Tick(*this);}
void ADungeonGuardStompProbeV001::EndPlay(const EEndPlayReason::Type R){FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);if(Proof&&!Proof->Stopped)Proof->Finish(TEXT("World ended before sameAid2 Stomp full cycle and actualReady return"));Super::EndPlay(R);}
