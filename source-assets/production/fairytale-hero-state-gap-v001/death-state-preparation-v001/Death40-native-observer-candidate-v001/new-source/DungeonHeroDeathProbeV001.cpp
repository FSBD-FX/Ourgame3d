#include "DungeonHeroDeathProbeV001.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonHUD.h"
#include "DungeonStoneGuardDriver.h"
#include "DungeonStoneBatDriver.h"
#include "DungeonFairytaleSwordDeathDrawState.h"
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
namespace Death=DungeonFairytaleSwordDeathV001;
TArray<JV> XY(FVector2D V){return {MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y)};}
TArray<JV> Strings(const TArray<FString>& A){TArray<JV> R;for(const auto& S:A)R.Add(MakeShared<FJsonValueString>(S));return R;}
void Id(JO O,const TCHAR* N,uint64 V){O->SetStringField(N,FString::Printf(TEXT("%llu"),V));}

const TCHAR* PhaseName(int32 P)
{switch(P){case 0:return TEXT("await_enter");case 1:return TEXT("register_display_LGT_request_E");case 2:return TEXT("await_actual_LGT_commit");case 3:return TEXT("Knight_diagnostic_only");case 4:return TEXT("await_formal_Bat");case 5:return TEXT("Bat_diagnostic_only");case 6:return TEXT("await_formal_Guard");case 7:return TEXT("normal_WASD_approach");case 8:return TEXT("continuous_real_Guard_attacks");case 9:return TEXT("original_player_terminal_Death");case 10:return TEXT("complete");default:return TEXT("invalid");}}
JO Action(const DungeonStoneGuard::FAction& A)
{
 auto O=MakeShared<FJsonObject>();Id(O,TEXT("attack_id"),A.AttackId);O->SetNumberField(TEXT("kind"),int32(A.Kind));O->SetNumberField(TEXT("facing"),A.Facing);O->SetBoolField(TEXT("in_progress"),A.InProgress);O->SetBoolField(TEXT("locked"),A.Locked);O->SetBoolField(TEXT("interrupted"),A.Interrupted);
 for(const auto& Pair:TArray<TPair<FString,double>>{{TEXT("start"),A.Start},{TEXT("lock_at"),A.LockAt},{TEXT("active_at"),A.ActiveAt},{TEXT("active_end"),A.ActiveEnd},{TEXT("recovery_end"),A.RecoveryEnd},{TEXT("cooldown_end"),A.CooldownEnd},{TEXT("damage"),A.Damage},{TEXT("stagger"),A.Stagger}})O->SetNumberField(Pair.Key,Pair.Value);
 O->SetArrayField(TEXT("origin"),XY({A.Origin.X,A.Origin.Y}));O->SetArrayField(TEXT("locked_center"),XY({A.LockedCenter.X,A.LockedCenter.Y}));return O;
}

JO Draw(const FDungeonFairytaleSwordDeathDraw& D)
{
 auto O=MakeShared<FJsonObject>();const auto& P=D.Plan;
 Id(O,TEXT("draw_id"),D.DrawId);Id(O,TEXT("player_entity"),D.PlayerEntityId);O->SetNumberField(TEXT("sim"),D.SimulationTime);O->SetBoolField(TEXT("opt_in"),D.OptIn);O->SetBoolField(TEXT("drawn"),D.Drawn);O->SetBoolField(TEXT("atomic_preflight_ready"),D.AtomicPreflightReady);O->SetStringField(TEXT("missing_reason"),D.MissingReason);
 O->SetBoolField(TEXT("supported"),P.Supported);O->SetStringField(TEXT("profile"),P.ProfileId);O->SetNumberField(TEXT("frame"),P.Frame);O->SetNumberField(TEXT("facing"),P.Facing);O->SetNumberField(TEXT("nonempty_count"),P.NonemptyDrawCount);O->SetBoolField(TEXT("visual_sword_released"),P.VisualSwordReleased);O->SetBoolField(TEXT("last_frame_held"),P.LastFrameHeld);
 O->SetBoolField(TEXT("death_active"),P.Death.Active);O->SetBoolField(TEXT("dead"),P.Death.Dead);O->SetBoolField(TEXT("death_reported"),P.Death.DeathReported);O->SetNumberField(TEXT("death_health"),P.Death.Health);O->SetNumberField(TEXT("death_elapsed"),P.Death.Elapsed);O->SetStringField(TEXT("death_animation"),P.Death.AnimationName);
 O->SetArrayField(TEXT("context_ground"),XY(D.Context.GroundScreen));O->SetNumberField(TEXT("ui_scale"),D.Context.UIScale);O->SetNumberField(TEXT("jump_height"),D.Context.JumpHeight);
 O->SetArrayField(TEXT("root_source"),XY(P.RootSource));O->SetArrayField(TEXT("sword_anchor_source"),XY(P.SwordAnchorSource));O->SetArrayField(TEXT("axis_artist"),XY(P.AxisArtist));O->SetArrayField(TEXT("body_top"),XY(P.BodyTop));O->SetArrayField(TEXT("sword_anchor_screen"),XY(P.SwordAnchorScreen));O->SetArrayField(TEXT("sword_top"),XY(P.SwordTop));O->SetArrayField(TEXT("sword_pivot_uv"),XY(P.SwordPivotUV));
 O->SetNumberField(TEXT("canvas_size"),P.CanvasSize);O->SetNumberField(TEXT("source_to_screen_scale"),P.SourceToScreenScale);O->SetNumberField(TEXT("weapon_scale"),P.WeaponScale);O->SetNumberField(TEXT("weapon_width"),P.WeaponWidth);O->SetNumberField(TEXT("weapon_angle"),P.WeaponAngle);O->SetNumberField(TEXT("texture_u"),P.TextureU);O->SetNumberField(TEXT("texture_du"),P.TextureDU);
 const auto& B=P.Binding;O->SetStringField(TEXT("run"),B.RunGuid.ToString(EGuidFormats::Digits));Id(O,TEXT("owner"),B.OwnerId);Id(O,TEXT("weapon_instance"),B.WeaponInstanceId);Id(O,TEXT("weapon_version"),B.WeaponVersion);Id(O,TEXT("armor_instance"),B.ArmorInstanceId);Id(O,TEXT("armor_version"),B.ArmorVersion);O->SetStringField(TEXT("weapon_content"),B.WeaponContentId);O->SetStringField(TEXT("armor_content"),B.ArmorContentId);
 O->SetArrayField(TEXT("actual_stack"),Strings(D.ActualRenderedStack));TArray<JV> Color,PlanColor;for(double V:{double(D.Tint.R),double(D.Tint.G),double(D.Tint.B),double(D.Tint.A)})Color.Add(MakeShared<FJsonValueNumber>(V));for(double V:{double(P.Tint.R),double(P.Tint.G),double(P.Tint.B),double(P.Tint.A)})PlanColor.Add(MakeShared<FJsonValueNumber>(V));O->SetArrayField(TEXT("tint"),Color);O->SetArrayField(TEXT("plan_tint"),PlanColor);
 TArray<JV> Resident;for(const auto& R:D.ResidentTextures){auto X=MakeShared<FJsonObject>();X->SetStringField(TEXT("texture"),R.TexturePath);X->SetStringField(TEXT("class"),R.ClassName);X->SetNumberField(TEXT("width"),R.Width);X->SetNumberField(TEXT("height"),R.Height);X->SetBoolField(TEXT("resource_ready"),R.ResourceReady);Resident.Add(MakeShared<FJsonValueObject>(X));}O->SetArrayField(TEXT("resident_textures"),Resident);
 TArray<JV> Slots;for(const auto& S:D.Slots){auto X=MakeShared<FJsonObject>();X->SetNumberField(TEXT("slot"),S.SlotIndex);X->SetNumberField(TEXT("component"),int32(S.Component));X->SetStringField(TEXT("texture"),S.TexturePath);X->SetBoolField(TEXT("known_empty"),S.KnownOptionalEmpty);X->SetBoolField(TEXT("texture_ready"),S.TextureReady);X->SetBoolField(TEXT("drawn"),S.Drawn);X->SetArrayField(TEXT("top"),XY(S.Top));X->SetArrayField(TEXT("size"),XY(S.Size));X->SetArrayField(TEXT("uv"),XY(S.UV));X->SetArrayField(TEXT("uv_size"),XY(S.UVSize));X->SetNumberField(TEXT("rotation"),S.RotationDegrees);X->SetArrayField(TEXT("rotation_pivot"),XY(S.RotationPivot));X->SetNumberField(TEXT("draw_scale"),S.DrawScale);X->SetBoolField(TEXT("scale_position"),S.ScalePosition);Slots.Add(MakeShared<FJsonValueObject>(X));}O->SetArrayField(TEXT("slots"),Slots);return O;
}
FString Json(JO O){FString T;auto W=TJsonWriterFactory<>::Create(&T);FJsonSerializer::Serialize(O.ToSharedRef(),W);return T;}
}
struct FDungeonHeroDeathProofState
{
 FString Directory;bool Stopped=false,Prewarm=false,Capturing=false,Complete=false,FinishOnFrame=false,DeathPinned=false,RoutePlanned=false,RouteReached=false,PreviousDead=false,PreviousGameOver=false;
 TWeakObjectPtr<ADungeonGameMode> Game;TWeakObjectPtr<APlayerController> Controller;TWeakObjectPtr<ADungeonHUD> HUD;
 TMap<FKey,bool> Keys;FKey PulseKey;double ReleaseAt=0.,NeutralUntil=0.,Warm=0.,Start=0.,Stop=0.,PhaseWall=0.;int32 Phase=0,RequestedSide=0,ApproachSide=0,RouteStage=0,HoldSeen=0,ObservedDeadTransitions=0,ObservedGameOverTransitions=0;
 FGuid Run;uint64 Owner=0,Restart=0,Light=0,Sword=0,GuardId=0,PlayerId=0,LethalEvent=0,LethalAttack=0,LastDeathDraw=0,LastConfirmedEvent=0;
 double LethalAt=-1.,BeforeHP=-1.,ConfirmedLoss=0.,FrozenSim=-1.,FrozenGuardTime=-1.,FrozenCombatTime=-1.,FrozenWeaponTime=-1.,FrozenDodgeTime=-1.,MaximumDeathAge=0.,MinimumHoldAge=-1.,RouteLane=0.;FVector2D RouteStart=FVector2D::ZeroVector,RouteGuard=FVector2D::ZeroVector;
 uint32 DeathMask=0;JO Report=MakeShared<FJsonObject>(),EquipmentBefore,WorldBefore;TArray<JV> Inputs,Steps,Observations,Offsets,DiagnosticHits,RouteWitnesses,StartupTextures,HitWitnesses;
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

 JO Equipment()const
 {
  auto O=MakeShared<FJsonObject>();const auto* S=Game->GetEquipmentInventoryState();if(!S)return O;
  Id(O,TEXT("run_alias"),S->RunId);Id(O,TEXT("owner"),S->OwnerId);Id(O,TEXT("revision"),S->Revision);Id(O,TEXT("starter"),S->StarterId);Id(O,TEXT("armor"),S->Armor);Id(O,TEXT("weapon0"),S->Weapons[0]);Id(O,TEXT("weapon1"),S->Weapons[1]);O->SetNumberField(TEXT("active_slot"),S->ActiveSlot);O->SetNumberField(TEXT("runtime_updates"),S->RuntimeUpdates.size());
  TArray<JV> Items,Sources,Ops,WorldSources;for(const auto& I:S->Items){auto X=MakeShared<FJsonObject>();Id(X,TEXT("instance"),I.InstanceId);Id(X,TEXT("version"),I.Version);X->SetStringField(TEXT("content"),UTF8_TO_TCHAR(I.ContentId.c_str()));X->SetNumberField(TEXT("ammo"),I.Ammo);X->SetNumberField(TEXT("cooldown"),I.SkillCooldownDeadline);X->SetNumberField(TEXT("grade"),I.Grade);X->SetNumberField(TEXT("tier"),I.Tier);Items.Add(MakeShared<FJsonValueObject>(X));}
  for(const auto& S0:S->Sources){auto X=MakeShared<FJsonObject>();Id(X,TEXT("source"),S0.SourceId);Id(X,TEXT("version"),S0.Version);Id(X,TEXT("instance"),S0.InstanceId);Id(X,TEXT("created_revision"),S0.CreatedRevision);X->SetBoolField(TEXT("available"),S0.Available);X->SetStringField(TEXT("content"),UTF8_TO_TCHAR(S0.SpawnItem.ContentId.c_str()));Sources.Add(MakeShared<FJsonValueObject>(X));}
  for(const auto& V:S->Operations){auto X=MakeShared<FJsonObject>();Id(X,TEXT("operation"),V.OperationId);X->SetNumberField(TEXT("action"),int32(V.Request.Action));Id(X,TEXT("instance"),V.Request.InstanceId);Id(X,TEXT("dropped"),V.Result.DroppedId);Id(X,TEXT("dropped_source"),V.Result.DroppedSourceId);Ops.Add(MakeShared<FJsonValueObject>(X));}
  for(const auto& V:Game->GetEquipmentSources()){auto X=MakeShared<FJsonObject>();Id(X,TEXT("source"),V.SourceId);Id(X,TEXT("instance"),V.InstanceId);Id(X,TEXT("version"),V.Version);Id(X,TEXT("room"),V.RoomInstanceId);X->SetStringField(TEXT("logical_key"),V.LogicalKey);X->SetStringField(TEXT("content"),UTF8_TO_TCHAR(V.Item.ContentId.c_str()));X->SetArrayField(TEXT("position"),XY(V.Position));X->SetBoolField(TEXT("settled"),V.Settled);X->SetBoolField(TEXT("consumed"),V.Consumed);WorldSources.Add(MakeShared<FJsonValueObject>(X));}
  O->SetArrayField(TEXT("items"),Items);O->SetArrayField(TEXT("sources"),Sources);O->SetArrayField(TEXT("operations"),Ops);O->SetArrayField(TEXT("world_equipment_sources"),WorldSources);return O;
 }
 JO WorldPickupIdentity()const
 {
  auto O=MakeShared<FJsonObject>();TArray<JV> A;for(const auto& V:Game->Pickups){auto X=MakeShared<FJsonObject>();Id(X,TEXT("object"),V.ObjectId);Id(X,TEXT("source"),V.SourceId);Id(X,TEXT("room"),V.RoomInstanceId);X->SetStringField(TEXT("kind"),V.Kind.ToString());X->SetArrayField(TEXT("position"),XY(V.Position));A.Add(MakeShared<FJsonValueObject>(X));}O->SetArrayField(TEXT("pickups"),A);return O;
 }
 bool PinHits(ADungeonFighter* P,ADungeonFighter* E)
 {
  if(!E||!E->GetStoneGuardDriver())return true;const auto& S=E->GetStoneGuardDriver()->State();
  for(const auto& R:E->GetGuardFeedback().Entries())if(R.SourceKind==DungeonStoneGuard::EEventKind::Hit&&R.TargetId==PlayerId&&R.ActualHPLoss>0.&&R.EventId>LastConfirmedEvent)
  {
   const DungeonStoneGuard::FEvent* Event=nullptr;for(const auto& V:S.Issued)if(V.EventId==R.EventId)Event=&V;bool Receipt=false;for(const auto& V:S.HitReceipts)if(V.AttackId==R.AttackId&&V.TargetId==PlayerId&&V.AtTime==R.AtTime)Receipt=true;
   const bool Kind=Event&&(Event->Action.Kind==DungeonStoneGuard::EAttack::AxeSweep||Event->Action.Kind==DungeonStoneGuard::EAttack::Stomp);
   if(!Need(!DeathPinned&&Phase==8&&RouteReached&&BeforeHP>0.&&Event&&Receipt&&Kind&&Event->Kind==DungeonStoneGuard::EEventKind::Hit&&Event->EntityId==GuardId&&Event->TargetId==PlayerId&&Event->AtTime==R.AtTime&&Event->Action.AttackId==R.AttackId&&R.AtTime>=Event->Action.ActiveAt&&R.AtTime<Event->Action.ActiveEnd,TEXT("Actual Guard hit/receipt/window identity invalid or after terminal death")))return false;
   const double ChainBefore=BeforeHP-ConfirmedLoss;ConfirmedLoss+=R.ActualHPLoss;const double ChainAfter=BeforeHP-ConfirmedLoss;
   if(!Need(ChainBefore>0.&&R.ActualHPLoss<=ChainBefore+1.e-4&&ChainAfter>=-1.e-4,TEXT("Actual Guard committed HP chain overdraws hero health")))return false;
   auto X=MakeShared<FJsonObject>();Id(X,TEXT("event"),R.EventId);Id(X,TEXT("attack"),R.AttackId);X->SetNumberField(TEXT("at"),R.AtTime);X->SetNumberField(TEXT("actual_HP_loss"),R.ActualHPLoss);X->SetNumberField(TEXT("chain_before"),ChainBefore);X->SetNumberField(TEXT("chain_after"),FMath::Max(0.,ChainAfter));X->SetObjectField(TEXT("action"),Action(Event->Action));HitWitnesses.Add(MakeShared<FJsonValueObject>(X));LastConfirmedEvent=R.EventId;
   if(ChainAfter<=1.e-4)
   {
    FDungeonDeathPresentationSample Q;const bool OK=P->QueryDeathPresentation(Q);
    if(!Need(P->bDead&&P->Health==0.f&&Game->bGameOver&&OK&&Q.Active&&Q.Dead&&Q.DeathReported&&Q.Health==0.f&&Q.AnimationName==TEXT("death"),TEXT("Natural Guard lethal hit failed actual HP0/GameOver/Death query")))return false;
    DeathPinned=true;LethalEvent=R.EventId;LethalAttack=R.AttackId;LethalAt=R.AtTime;FrozenSim=Game->GetSimulationTime();FrozenGuardTime=S.Time;FrozenCombatTime=P->GetMeleeCombatState().Time;FrozenWeaponTime=P->GetWeaponSkillTime();FrozenDodgeTime=P->GetDodgeState().Time;MoveStop();Next(9);
   }
  }
  return Need(BeforeHP<0.||FMath::Abs(P->Health-FMath::Max(0.,BeforeHP-ConfirmedLoss))<1.e-4,TEXT("Actual player HP differs from complete Guard confirmed-loss chain"));
 }
 JO Facts()
 {
  auto O=MakeShared<FJsonObject>();auto G=Game.Get();auto H=HUD.Get();auto P=G?G->PlayerFighter.Get():nullptr;if(!G||!H||!P)return O;auto E=Enemy(GuardId);if(!PinHits(P,E))return O;
  FDungeonDeathPresentationSample Q;const bool Query=P->QueryDeathPresentation(Q);const auto& V=G->GetEquipmentView();if(!Need(V.ActiveSlot>=0&&V.ActiveSlot<2,TEXT("Actual active weapon slot invalid")))return O;
  if(P->bDead&&!PreviousDead)++ObservedDeadTransitions;if(G->bGameOver&&!PreviousGameOver)++ObservedGameOverTransitions;if(!Need(!PreviousDead||P->bDead,TEXT("Dead hero revived during terminal source proof")))return O;PreviousDead=P->bDead;PreviousGameOver=G->bGameOver;
  O->SetNumberField(TEXT("phase"),Phase);O->SetNumberField(TEXT("sim"),G->GetSimulationTime());O->SetArrayField(TEXT("ground"),XY(P->GetGroundPosition()));O->SetNumberField(TEXT("HP"),P->Health);O->SetBoolField(TEXT("dead"),P->bDead);O->SetBoolField(TEXT("game_over"),G->bGameOver);O->SetNumberField(TEXT("facing"),P->Facing);O->SetStringField(TEXT("animation"),P->AnimationName);O->SetNumberField(TEXT("animation_time"),P->AnimationTime);O->SetBoolField(TEXT("death_query_ok"),Query);O->SetBoolField(TEXT("death_active"),Q.Active);O->SetBoolField(TEXT("death_reported"),Q.DeathReported);O->SetNumberField(TEXT("death_elapsed"),Q.Elapsed);O->SetNumberField(TEXT("death_query_health"),Q.Health);O->SetNumberField(TEXT("player_combat_time"),P->GetMeleeCombatState().Time);O->SetNumberField(TEXT("player_weapon_time"),P->GetWeaponSkillTime());O->SetNumberField(TEXT("player_dodge_time"),P->GetDodgeState().Time);
  O->SetNumberField(TEXT("poise_threshold"),P->GetPoiseThreshold());O->SetNumberField(TEXT("armor"),V.Stats.Armor);O->SetNumberField(TEXT("physical_vulnerability"),V.Stats.PhysicalVulnerabilityMultiplier);O->SetNumberField(TEXT("wallet"),P->Coins);
  O->SetBoolField(TEXT("held_A"),Controller->IsInputKeyDown(EKeys::A));O->SetBoolField(TEXT("held_D"),Controller->IsInputKeyDown(EKeys::D));O->SetBoolField(TEXT("held_W"),Controller->IsInputKeyDown(EKeys::W));O->SetBoolField(TEXT("held_S"),Controller->IsInputKeyDown(EKeys::S));O->SetBoolField(TEXT("interface_visible"),H->GetInterfaceVisible());O->SetNumberField(TEXT("text_calls"),H->GetRenderedTextDrawCalls());O->SetBoolField(TEXT("combat_range_debug"),H->IsCombatRangeDebugEnabled());O->SetNumberField(TEXT("combat_range_lines"),H->GetCombatRangeDebugLineCount());O->SetArrayField(TEXT("rendered_stack"),Strings(H->GetRenderedPlayerDrawStack()));O->SetArrayField(TEXT("camera_ground"),XY(H->GetCameraGroundCenter()));
  Id(O,TEXT("weapon_instance"),V.Slots[V.ActiveSlot].InstanceId);Id(O,TEXT("armor_instance"),V.Slots[2].InstanceId);Id(O,TEXT("player_entity"),P->GetRuntimeEntityId());auto CurrentEquipment=Equipment();O->SetObjectField(TEXT("equipment"),CurrentEquipment);O->SetObjectField(TEXT("world_pickup_identity"),WorldPickupIdentity());
  const auto& D=H->GetFairytaleSwordDeathDraw();O->SetObjectField(TEXT("death_draw"),Draw(D));
  if(EquipmentBefore&&!Need(Json(CurrentEquipment)==Json(EquipmentBefore),TEXT("Committed inventory/world equipment source changed after normal E commit")))return O;
  if(DeathPinned)
  {
   if(!Need(Phase==9&&P->bDead&&P->Health==0.f&&G->bGameOver&&Query&&Q.Active&&Q.Dead&&Q.DeathReported&&Q.Elapsed==P->AnimationTime&&Q.AnimationName==TEXT("death")&&G->GetSimulationTime()==FrozenSim&&P->GetMeleeCombatState().Time==FrozenCombatTime&&P->GetWeaponSkillTime()==FrozenWeaponTime&&P->GetDodgeState().Time==FrozenDodgeTime&&E&&E->GetStoneGuardDriver()&&E->GetStoneGuardDriver()->State().Time==FrozenGuardTime&&WorldBefore&&Json(WorldPickupIdentity())==Json(WorldBefore),TEXT("Actual terminal query/clock freeze/unchanged world pickup identity failed")))return O;
   if(!Need(D.DrawId>LastDeathDraw&&D.PlayerEntityId==PlayerId&&D.SimulationTime==G->GetSimulationTime()&&D.Drawn&&D.OptIn&&D.AtomicPreflightReady&&D.Plan.Supported&&D.Plan.Frame>=0&&D.Plan.Frame<5&&D.Plan.Facing==-ApproachSide&&D.Plan.Death.Active&&D.Plan.Death.Dead&&D.Plan.Death.DeathReported&&D.Plan.Death.Elapsed==Q.Elapsed&&D.Plan.Death.Health==0.f&&D.Plan.Binding.WeaponInstanceId==Sword&&D.Plan.Binding.ArmorInstanceId==Light&&D.Slots.Num()==9&&D.ActualRenderedStack==H->GetRenderedPlayerDrawStack()&&D.ActualRenderedStack.Num()==9&&D.ResidentTextures.Num()==41&&D.Tint==FLinearColor::White&&D.Plan.Tint==FLinearColor::White,TEXT("Actual Death draw/real clock/equipment/41 residents/9 slots/white tint failed")))return O;
   LastDeathDraw=D.DrawId;DeathMask|=1u<<D.Plan.Frame;MaximumDeathAge=FMath::Max(MaximumDeathAge,double(Q.Elapsed));if(D.Plan.Frame==4&&D.Plan.LastFrameHeld){++HoldSeen;if(MinimumHoldAge<0.)MinimumHoldAge=Q.Elapsed;}
  }
  else if(!Need(!Query&&!Q.Active&&!D.Drawn&&!P->bDead&&!G->bGameOver,TEXT("Death presentation became active before actual lethal ownership")))return O;
  if(E&&E->GetStoneGuardDriver()){const auto& S=E->GetStoneGuardDriver()->State();O->SetNumberField(TEXT("guard_HP"),S.HP);O->SetNumberField(TEXT("guard_time"),S.Time);O->SetNumberField(TEXT("guard_received_count"),S.ReceivedHits.size());O->SetNumberField(TEXT("guard_hit_count"),S.HitReceipts.size());O->SetObjectField(TEXT("guard_action"),Action(S.Action));O->SetArrayField(TEXT("guard_ground"),XY(E->GetGroundPosition()));}
  return O;
 }
 void Observe()
 {
  if(Stopped)return;if(Prewarm&&!Capturing){if(!Need(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))>8,TEXT("Synchronous prewarm missing")))return;Start=PhaseWall=FPlatformTime::Seconds();Capturing=true;GIsDumpingMovie=-1;return;}if(!Capturing)return;
  const double T=FPlatformTime::Seconds()-Start;auto O=Facts();if(Stopped)return;O->SetNumberField(TEXT("wall_offset_s"),T);Observations.Add(MakeShared<FJsonValueObject>(O));Offsets.Add(MakeShared<FJsonValueNumber>(T));
  if(!Need(!HUD->GetInterfaceVisible()&&HUD->GetRenderedTextDrawCalls()==0&&!HUD->IsCombatRangeDebugEnabled()&&HUD->GetCombatRangeDebugLineCount()==0,TEXT("Hidden interface or default-off combat range drew overlays")))return;
  if(DeathPinned&&DeathMask==31&&MaximumDeathAge>=1.2&&HoldSeen>=2&&MinimumHoldAge>=.8&&MaximumDeathAge-MinimumHoldAge>=.35){Complete=true;Next(10);FinishOnFrame=true;Finish();}
 }
 void Finish(const FString& Why=FString())
 {
  if(Stopped)return;Stopped=true;Stop=FPlatformTime::Seconds();GIsDumpingMovie=0;TArray<FKey> Held;Keys.GetKeys(Held);for(FKey K:Held)Key(K,false);const bool Flushed=FlushFastLosslessProofScreenshots();const bool Passed=Why.IsEmpty()&&Complete&&Flushed&&!Observations.IsEmpty();
  Report->SetStringField(TEXT("schema"),TEXT("hero-SWD-LGT-Death5-native-observer-v001"));Report->SetStringField(TEXT("scenario"),TEXT("NaturalGuardAttacksToHeroDeath5"));Report->SetBoolField(TEXT("passed"),Passed);Report->SetBoolField(TEXT("flow_complete"),Complete);Report->SetStringField(TEXT("failure"),Why);Id(Report,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());Report->SetStringField(TEXT("run"),Run.ToString(EGuidFormats::Digits));Id(Report,TEXT("owner"),Owner);Id(Report,TEXT("restart_serial"),Restart);Id(Report,TEXT("guard_entity"),GuardId);Id(Report,TEXT("player_entity"),PlayerId);Id(Report,TEXT("sword_instance"),Sword);Id(Report,TEXT("light_instance"),Light);Id(Report,TEXT("lethal_event"),LethalEvent);Id(Report,TEXT("lethal_attack"),LethalAttack);Report->SetNumberField(TEXT("lethal_at"),LethalAt);Report->SetNumberField(TEXT("pre_guard_HP"),BeforeHP);Report->SetNumberField(TEXT("confirmed_HP_loss"),ConfirmedLoss);Report->SetNumberField(TEXT("frozen_sim"),FrozenSim);Report->SetNumberField(TEXT("frozen_guard_time"),FrozenGuardTime);Report->SetNumberField(TEXT("frozen_combat_time"),FrozenCombatTime);Report->SetNumberField(TEXT("frozen_weapon_time"),FrozenWeaponTime);Report->SetNumberField(TEXT("frozen_dodge_time"),FrozenDodgeTime);Report->SetNumberField(TEXT("DeathMask"),DeathMask);Report->SetNumberField(TEXT("HoldSeen"),HoldSeen);Report->SetNumberField(TEXT("MinimumHoldAge"),MinimumHoldAge);Report->SetNumberField(TEXT("MaximumDeathAge"),MaximumDeathAge);Report->SetNumberField(TEXT("observed_dead_transitions"),ObservedDeadTransitions);Report->SetNumberField(TEXT("observed_game_over_transitions"),ObservedGameOverTransitions);Report->SetNumberField(TEXT("requested_approach_side"),RequestedSide);Report->SetNumberField(TEXT("actual_approach_side"),ApproachSide);
  if(EquipmentBefore)Report->SetObjectField(TEXT("equipment_before_death"),EquipmentBefore);if(WorldBefore)Report->SetObjectField(TEXT("world_pickups_before_death"),WorldBefore);
  Report->SetArrayField(TEXT("startup_resident_textures"),StartupTextures);Report->SetArrayField(TEXT("normal_inputs"),Inputs);Report->SetArrayField(TEXT("steps"),Steps);Report->SetArrayField(TEXT("observations"),Observations);Report->SetArrayField(TEXT("diagnostic_predecessor_hits"),DiagnosticHits);Report->SetArrayField(TEXT("route_witnesses"),RouteWitnesses);Report->SetArrayField(TEXT("guard_hit_witnesses"),HitWitnesses);Report->SetBoolField(TEXT("player_or_Guard_public_damage_used"),false);Report->SetBoolField(TEXT("HP_poise_clock_actor_writes"),false);Report->SetBoolField(TEXT("silent_video"),true);Report->SetBoolField(TEXT("audio_recorded"),false);Report->SetBoolField(TEXT("visual_reviewed"),false);Report->SetBoolField(TEXT("native_async_capture_writes_flushed"),Flushed);Report->SetNumberField(TEXT("formal_complete_units"),0);
  auto T=MakeShared<FJsonObject>();T->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());T->SetNumberField(TEXT("capture_start_monotonic_s"),Start);T->SetNumberField(TEXT("capture_stop_monotonic_s"),Stop);T->SetArrayField(TEXT("frame_wall_offsets_s"),Offsets);Report->SetObjectField(TEXT("capture_timing"),T);
  if(auto E=Enemy(GuardId))if(auto Driver=E->GetStoneGuardDriver()){const auto& S=Driver->State();TArray<JV> Events,Receipts,Confirmed;for(const auto& V:S.Issued){auto X=MakeShared<FJsonObject>();Id(X,TEXT("event"),V.EventId);Id(X,TEXT("entity"),V.EntityId);Id(X,TEXT("target"),V.TargetId);X->SetNumberField(TEXT("kind"),int32(V.Kind));X->SetNumberField(TEXT("at"),V.AtTime);X->SetNumberField(TEXT("end"),V.EndTime);X->SetObjectField(TEXT("action"),Action(V.Action));Events.Add(MakeShared<FJsonValueObject>(X));}for(const auto& V:S.HitReceipts){auto X=MakeShared<FJsonObject>();Id(X,TEXT("attack"),V.AttackId);Id(X,TEXT("target"),V.TargetId);X->SetNumberField(TEXT("at"),V.AtTime);Receipts.Add(MakeShared<FJsonValueObject>(X));}for(const auto& V:E->GetGuardFeedback().Entries())if(V.ActualHPLoss>0.){auto X=MakeShared<FJsonObject>();Id(X,TEXT("event"),V.EventId);Id(X,TEXT("attack"),V.AttackId);Id(X,TEXT("target"),V.TargetId);X->SetNumberField(TEXT("at"),V.AtTime);X->SetNumberField(TEXT("actual_HP_loss"),V.ActualHPLoss);X->SetNumberField(TEXT("source_kind"),int32(V.SourceKind));Confirmed.Add(MakeShared<FJsonValueObject>(X));}Report->SetArrayField(TEXT("guard_original_events"),Events);Report->SetArrayField(TEXT("guard_original_hit_receipts"),Receipts);Report->SetArrayField(TEXT("guard_actual_confirmed_losses"),Confirmed);Report->SetNumberField(TEXT("guard_final_HP"),S.HP);Report->SetNumberField(TEXT("guard_incoming_count"),S.ReceivedHits.size());}
  const FString Text=Json(Report),Path=Directory/TEXT("runtime-report.json");const bool Written=!Directory.IsEmpty()&&!IFileManager::Get().FileExists(*Path)&&FFileHelper::SaveStringToFile(Text,*Path,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);if(!Why.IsEmpty())UE_LOG(LogTemp,Error,TEXT("Hero Death5 proof: %s"),*Why);FPlatformMisc::RequestExitWithStatus(false,Passed&&Written?0:3);
 }
 void Tick(ADungeonHeroDeathProbeV001& Actor)
 {
  if(Stopped)return;const double Now=FPlatformTime::Seconds();auto G=Actor.GetWorld()->GetAuthGameMode<ADungeonGameMode>();auto C=UGameplayStatics::GetPlayerController(&Actor,0);auto H=C?Cast<ADungeonHUD>(C->GetHUD()):nullptr;
  if(!Game.IsValid()&&G&&C&&C->PlayerInput&&H){Game=G;Controller=C;HUD=H;Actor.AddTickPrerequisiteActor(G);Actor.AddTickPrerequisiteActor(H);return;}if(!Game.IsValid())return;
  if(PulseKey.IsValid()&&Now>=ReleaseAt){Key(PulseKey,false);PulseKey=FKey();NeutralUntil=Now+.04;}
  if(!Capturing){if(!Prewarm&&Now-Warm>=2.){Prewarm=true;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}else if(Now-Warm>18.)Finish(TEXT("Prewarm timeout"));return;}if(FinishOnFrame)return;
  auto P=G->PlayerFighter.Get();if(!Need(Now-Start<70.&&Now-PhaseWall<38.&&G==Game.Get()&&C==Controller.Get()&&H==HUD.Get()&&P&&C->GetPawn()==P,TEXT("Native input/room/player timeout or identity mismatch")))return;if(!PinHits(P,Enemy(GuardId)))return;
  if(!Need(DeathPinned?(P->bDead&&G->bGameOver):(!P->bDead&&!G->bGameOver),TEXT("HP0/GameOver lacks exactly one real pinned Guard lethal transition")))return;
  FDungeonFirstBatchGuardRoomView Room;if(!Need(G->QueryFirstBatchGuardRoom(Room)&&Room.Slots.Num()==3&&G->GetEquipmentView().Config==EDungeonEquipmentRunConfig::FirstBatch,TEXT("Finite formal Guard room required")))return;
  if(!Run.IsValid()){Run=Room.RunGuid;Owner=G->GetEquipmentView().OwnerId;Restart=G->GetRunRestartSerial();PlayerId=P->GetRuntimeEntityId();Sword=G->GetEquipmentView().Slots[G->GetEquipmentView().ActiveSlot].InstanceId;}
  if(!Need(Room.RunGuid==Run&&G->GetRunRestartSerial()==Restart,TEXT("Run restarted or player identity changed")))return;
  switch(Phase){case 0:if(!Need(G->bWaitingForStart&&G->GetSimulationTime()==0.&&P->Coins==20,TEXT("Await real Enter at0/20")))return;if(Pulse(EKeys::Enter))Next(1);break;
  case 1:if(!G->bWaitingForStart&&CanPulse()){DungeonEquipmentInventory::FItem I;I.ContentId="ARM-LGT-001";const auto X=G->RegisterEquipmentSource(TEXT("display.hero.death.light.v001"),I,P->GetGroundPosition()+FVector2D(24.,0.),true);if(!Need(X.Ok()&&!X.Replayed,TEXT("Display LGT source registration failed")))return;Light=X.InstanceId;if(Pulse(EKeys::E))Next(2);}break;
  case 2:if(!G->GetEquipmentView().Action.Active&&G->GetEquipmentView().Slots[2].InstanceId==Light&&CanPulse()){const auto& V=G->GetEquipmentView();if(!Need(V.Slots[V.ActiveSlot].ContentId==TEXT("WPN-SWD-001")&&V.Slots[2].ContentId==TEXT("ARM-LGT-001")&&V.Stats.Poise==30.&&V.Stats.Armor==14.&&V.Stats.PhysicalVulnerabilityMultiplier==1.,TEXT("Actual normal E committed SWD/LGT stats differ; never write")))return;EquipmentBefore=Equipment();Next(3);}break;
  case 3:if(CanPulse()&&DiagnosticKill(Enemy(Room.Slots[0].EntityId)))Next(4);break;
  case 4:if(Room.Slots[1].Stage==EDungeonGuardRoomSlotStage::Materialized){if(!Need(Room.Slots[1].WarningAt>=Room.Slots[0].DeadAt+2.&&Room.Slots[1].MaterializedAt>=Room.Slots[1].WarningAt+1.2,TEXT("Original Bat warning shortened")))return;Next(5);}break;
  case 5:if(Now-PhaseWall>=.9&&DiagnosticKill(Enemy(Room.Slots[1].EntityId)))Next(6);break;
  case 6:if(Room.Slots[2].Stage==EDungeonGuardRoomSlotStage::Materialized){GuardId=Room.Slots[2].EntityId;if(!Need(Room.Slots[2].WarningAt>=Room.Slots[1].DeadAt+2.&&Room.Slots[2].MaterializedAt>=Room.Slots[2].WarningAt+1.2&&Enemy(GuardId)&&Enemy(GuardId)->GetStoneGuardDriver(),TEXT("Original Guard birth/warning missing")))return;BeforeHP=P->Health;Next(7);}break;
  case 7:{auto E=Enemy(GuardId);if(!Need(E&&E->GetStoneGuardDriver(),TEXT("Formal Guard missing before normal route")))return;if(FollowRoute(E)){WorldBefore=WorldPickupIdentity();Next(8);}break;}
  case 8:{auto E=Enemy(GuardId);if(!Need(E&&E->GetStoneGuardDriver(),TEXT("Formal Guard disappeared")))return;MoveStop();if(P->Facing!=float(-ApproachSide))Key(ApproachSide>0?EKeys::A:EKeys::D,true);break;}
  case 9:MoveStop();break;
  default:Finish(TEXT("Unexpected Death observer state"));break;}
 }
};
void FDungeonHeroDeathProofDeleter::operator()(FDungeonHeroDeathProofState* P)const{delete P;}
ADungeonHeroDeathProbeV001::ADungeonHeroDeathProbeV001(){PrimaryActorTick.bCanEverTick=true;}
ADungeonHeroDeathProbeV001::~ADungeonHeroDeathProbeV001()=default;
void ADungeonHeroDeathProbeV001::BeginPlay()
{
 Super::BeginPlay();Proof.Reset(new FDungeonHeroDeathProofState());Proof->Warm=FPlatformTime::Seconds();GIsDumpingMovie=0;FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),Proof->Directory);FParse::Value(FCommandLine::Get(),TEXT("DungeonHeroDeathApproachSide="),Proof->RequestedSide);
 if(Proof->Directory.IsEmpty()||FPaths::IsRelative(Proof->Directory)){Proof->Directory.Reset();Proof->Finish(TEXT("Absolute unused evidence directory required"));return;}Proof->Directory=FPaths::ConvertRelativePathToFull(Proof->Directory);FPaths::NormalizeDirectoryName(Proof->Directory);
 TArray<FString> Prior;IFileManager::Get().FindFiles(Prior,*(Proof->Directory/TEXT("*")),true,false);Prior.Remove(TEXT("native-lossless-capture.json"));if(Prior.Num()){Proof->Stopped=true;FPlatformMisc::RequestExitWithStatus(false,3);return;}IFileManager::Get().MakeDirectory(*Proof->Directory,true);
 for(const TCHAR* F:{TEXT("DungeonHeroDeathProofV001"),TEXT("DungeonFairytaleSwordDeathPreview"),TEXT("DungeonFairytaleSwordEquipmentBoundPreview"),TEXT("DungeonFairytaleSwordWalkPreview"),TEXT("DungeonFairytaleGuardFullPreview"),TEXT("DungeonContentProof"),TEXT("DungeonFastLosslessCapture"),TEXT("DungeonAsyncLosslessCapture")})if(!Proof->Need(FParse::Param(FCommandLine::Get(),F),FString(TEXT("Missing opt-in flag: "))+F))return;
 for(const TCHAR* F:{TEXT("DungeonHeroHurtProofV001"),TEXT("DungeonGuardArtCombatProofV003"),TEXT("DungeonGuardArtKnown44Proof"),TEXT("DungeonGuardArtDeathProofV005"),TEXT("DungeonFairytaleWalkProof"),TEXT("DungeonCombatRangeDebug"),TEXT("DungeonGuardRoomFlowProof"),TEXT("DungeonGuardRunSaveProof"),TEXT("DungeonGuardRunRestoreProof"),TEXT("DungeonFairytaleEquipmentBoundProof"),TEXT("DungeonFairytaleSwordBodyProof"),TEXT("DungeonRunContinueProof")})if(!Proof->Need(!FParse::Param(FCommandLine::Get(),F),TEXT("Independent observer modes/default range flags cannot share this controller")))return;
 if(!Proof->Need(!FApp::UseFixedTimeStep()&&(Proof->RequestedSide==-1||Proof->RequestedSide==1),TEXT("Native pacing and explicitside[-1,+1] required")))return;
 const auto& Profile=Death::Profile();if(!Proof->Need(Profile.SourceClosureVerified&&Profile.SourceClosureSHA256==TEXT("5f6506b609440d8cfda40b493b7ce9b23131b0f83aa09add333f8d8e74ef788c"),TEXT("Exact reviewed Death40 source closure missing")))return;
 TSet<FString> Unique;for(const auto& Frame:Profile.Frames)for(const auto& Source:Frame.Layers){auto T=FindObject<UTexture2D>(nullptr,*Source.TexturePath);if(!Proof->Need(!Source.KnownOptionalEmpty&&!Unique.Contains(Source.TexturePath)&&T&&T->GetResource()&&!T->HasPendingRenderResourceInitialization()&&T->GetPathName()==Source.TexturePath&&T->GetSizeX()==512&&T->GetSizeY()==512,TEXT("All40 source textures must already be resident before Enter; no first-use repair")))return;Unique.Add(Source.TexturePath);auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("frame"),Frame.Frame);O->SetNumberField(TEXT("component"),int32(Source.Component));O->SetStringField(TEXT("texture"),T->GetPathName());O->SetStringField(TEXT("class"),T->GetClass()->GetName());O->SetNumberField(TEXT("width"),T->GetSizeX());O->SetNumberField(TEXT("height"),T->GetSizeY());O->SetBoolField(TEXT("resident"),true);O->SetBoolField(TEXT("known_empty"),Source.KnownOptionalEmpty);O->SetNumberField(TEXT("source_alpha_nonzero"),Source.SourceAlphaNonzero);O->SetStringField(TEXT("source_SHA"),Source.SourceSHA256);O->SetStringField(TEXT("source_RGBA_SHA"),Source.SourceRGBASHA256);Proof->StartupTextures.Add(MakeShared<FJsonValueObject>(O));}
 auto Sword=FindObject<UTexture2D>(nullptr,*Profile.SwordTexturePath);if(!Proof->Need(Unique.Num()==40&&Sword&&Sword->GetResource()&&!Sword->HasPendingRenderResourceInitialization()&&Sword->GetSizeX()==512&&Sword->GetSizeY()==512,TEXT("Exact40 + reused independentSword41 preload required")))return;auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("texture"),Sword->GetPathName());O->SetStringField(TEXT("class"),Sword->GetClass()->GetName());O->SetNumberField(TEXT("width"),Sword->GetSizeX());O->SetNumberField(TEXT("height"),Sword->GetSizeY());O->SetBoolField(TEXT("resident"),true);O->SetBoolField(TEXT("sword"),true);Proof->StartupTextures.Add(MakeShared<FJsonValueObject>(O));
 GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Proof->Directory;FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonHeroDeathProbeV001::ScreenshotProcessed);
}
void ADungeonHeroDeathProbeV001::ScreenshotProcessed(){if(Proof)Proof->Observe();}
void ADungeonHeroDeathProbeV001::Tick(float D){Super::Tick(D);if(Proof)Proof->Tick(*this);}
void ADungeonHeroDeathProbeV001::EndPlay(const EEndPlayReason::Type R){FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);if(Proof&&!Proof->Stopped)Proof->Finish(TEXT("Native world ended before real Death5/terminalhold proof complete"));Super::EndPlay(R);}
