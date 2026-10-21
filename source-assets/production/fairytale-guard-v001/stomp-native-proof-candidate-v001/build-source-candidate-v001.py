"""Prepare new candidate Source only. Never writes actual Source or invokes UE/UBT."""
from pathlib import Path
import difflib,json,hashlib
R=Path('F:/Ourgame');C=Path(__file__).resolve().parent;S=R/'UnrealGame/Source/CodexDungeon'
(C/'new-source').mkdir(exist_ok=True);(C/'patches').mkdir(exist_ok=True);(C/'before').mkdir(exist_ok=True)
base=(R/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001/Death40-native-observer-candidate-v001/new-source/DungeonHeroDeathProbeV001.cpp').read_text(encoding='utf-8-sig')
known=(S/'DungeonGuardArtKnown44Probe.cpp').read_text(encoding='utf-8-sig');combat=(S/'DungeonGuardArtCombatProbeV003.cpp').read_text(encoding='utf-8-sig')
def span(t,a,b):return t[t.index(a):t.index(b,t.index(a))]
prefix=span(base,'#include','const TCHAR* PhaseName').replace('DungeonHeroDeathProbeV001.h','DungeonGuardStompProbeV001.h').replace('DungeonFairytaleSwordDeathDrawState.h','DungeonFairytaleGuardStompProfileV004.h').replace('namespace Death=DungeonFairytaleSwordDeathV001;','namespace Full=DungeonFairytaleGuardFullV003;')
action=span(combat,'JO SerializeAction(', 'JO SerializeMeleeAction(').replace('SerializeAction','Action')
draw=span(known,'JO SerializeDraw(', '\n}\nstruct FDungeonGuardArtKnown44State').replace('SerializeDraw','Draw')
draw=draw.replace('return O;','''O->SetStringField(TEXT("ProfileId"),D.ProfileId);O->SetBoolField(TEXT("QuadSubmitted"),D.QuadSubmitted);O->SetArrayField(TEXT("QuadTop"),XY(D.QuadTop));O->SetArrayField(TEXT("QuadSize"),XY(D.QuadSize));O->SetArrayField(TEXT("QuadUV"),XY(D.QuadUV));O->SetArrayField(TEXT("QuadUVSize"),XY(D.QuadUVSize));O->SetArrayField(TEXT("QuadRotationPivot"),XY(D.QuadRotationPivot));O->SetNumberField(TEXT("QuadRotationDegrees"),D.QuadRotationDegrees);O->SetNumberField(TEXT("QuadDrawScale"),D.QuadDrawScale);O->SetBoolField(TEXT("QuadScalePosition"),D.QuadScalePosition);O->SetNumberField(TEXT("UIScale"),D.UIScale);TArray<JV> Color;for(double V:{double(D.QuadTint.R),double(D.QuadTint.G),double(D.QuadTint.B),double(D.QuadTint.A)})Color.Add(MakeShared<FJsonValueNumber>(V));O->SetArrayField(TEXT("QuadTint"),Color);TArray<JV> Residents;for(const auto& T:D.RowResidents){auto X=MakeShared<FJsonObject>();X->SetStringField(TEXT("TexturePath"),T.TexturePath);X->SetStringField(TEXT("ClassName"),T.ClassName);X->SetNumberField(TEXT("Width"),T.Width);X->SetNumberField(TEXT("Height"),T.Height);X->SetBoolField(TEXT("ResourceReady"),T.ResourceReady);X->SetBoolField(TEXT("PendingInitialization"),T.PendingInitialization);Residents.Add(MakeShared<FJsonValueObject>(X));}O->SetArrayField(TEXT("RowResidents"),Residents);return O;''')
methods=span(base,' ADungeonFighter* Enemy(',' JO Equipment()const')
header='''#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonGuardStompProbeV001.generated.h"
struct FDungeonGuardStompProofState;
struct FDungeonGuardStompProofDeleter {void operator()(FDungeonGuardStompProofState*)const;};
UCLASS()
class CODEXDUNGEON_API ADungeonGuardStompProbeV001:public AActor
{
 GENERATED_BODY()
public:
 ADungeonGuardStompProbeV001();virtual ~ADungeonGuardStompProbeV001()override;
 virtual void BeginPlay()override;virtual void Tick(float DeltaSeconds)override;virtual void EndPlay(const EEndPlayReason::Type Reason)override;
private:
 void ScreenshotProcessed();TUniquePtr<FDungeonGuardStompProofState,FDungeonGuardStompProofDeleter> Proof;
};
'''
phase='''const TCHAR* PhaseName(int32 P){static const TCHAR* N[]={TEXT("await_enter"),TEXT("normal_E_LGT"),TEXT("await_commit"),TEXT("Knight_diagnostic"),TEXT("await_Bat"),TEXT("Bat_diagnostic"),TEXT("await_Guard"),TEXT("normal_body_route"),TEXT("first_natural_Stomp_cycle"),TEXT("complete")};return P>=0&&P<UE_ARRAY_COUNT(N)?N[P]:TEXT("invalid");}
const Full::FRow* TrialRow(Full::EClip Clip){for(const auto& Row:DungeonFairytaleGuardStompV004::ProfileStompV004())if(Row.Clip==Clip)return &Row;return nullptr;}
FString Json(JO O){FString T;auto W=TJsonWriterFactory<>::Create(&T);FJsonSerializer::Serialize(O.ToSharedRef(),W);return T;}
'''
state='''}
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
'''
logic='''
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
'''
tick=span(base,' void Tick(ADungeonHeroDeathProbeV001& Actor)','\n};\nvoid FDungeonHeroDeathProofDeleter')
tick=tick.replace('ADungeonHeroDeathProbeV001','ADungeonGuardStompProbeV001').replace('if(!PinHits(P,Enemy(GuardId)))return;','if(!PinHits(P,Enemy(GuardId)))return;').replace('Now-Start<70.&&Now-PhaseWall<38.','Now-Start<42.&&Now-PhaseWall<24.')
tick=tick.replace('EquipmentBefore=Equipment();Next(3);','Next(3);').replace('WorldBefore=WorldPickupIdentity();Next(8);','Next(8);').replace('  case 9:MoveStop();break;','')
tick=tick.replace('if(FinishOnFrame)return;','').replace('DeathPinned?(P->bDead&&G->bGameOver):(!P->bDead&&!G->bGameOver)','!P->bDead&&!G->bGameOver&&P->Health>0.f').replace('HP0/GameOver lacks exactly one real pinned Guard lethal transition','Alive actual hero through original Stomp cycle required')
tick=tick.replace('display.hero.death.light.v001','display.guard.stomp.light.v001').replace('Unexpected Death observer state','Unexpected Stomp observer state')
finish='''
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
'''
tail=span(base,'void FDungeonHeroDeathProofDeleter', ' const auto& Profile=Death::Profile();')
tail=tail.replace('FDungeonHeroDeathProofDeleter','FDungeonGuardStompProofDeleter').replace('FDungeonHeroDeathProofState','FDungeonGuardStompProofState').replace('ADungeonHeroDeathProbeV001','ADungeonGuardStompProbeV001').replace('DungeonHeroDeath','DungeonGuardStomp').replace('DungeonFairytaleSwordDeathPreview','DungeonFairytaleGuardStompPreview').replace('TEXT("DungeonGuardStompProofV001"),TEXT("DungeonFairytaleGuardStompPreview")','TEXT("DungeonGuardStompProofV001"),TEXT("DungeonFairytaleGuardStompPreview")')
tail=tail.replace('TEXT("DungeonHeroHurtProofV001")','TEXT("DungeonHeroDeathProofV001"),TEXT("DungeonHeroHurtProofV001")')
startup=''' int32 Unique=0;TSet<FString> Paths;for(const auto& Row:DungeonFairytaleGuardStompV004::ProfileStompV004())
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
'''
cpp=prefix+phase+action+draw+state+methods+logic+finish+tick+'\n};\n'+tail+startup
(C/'new-source/DungeonGuardStompProbeV001.h').write_text(header,encoding='utf-8');(C/'new-source/DungeonGuardStompProbeV001.cpp').write_text(cpp,encoding='utf-8')
def patch(name,old,new):
 (C/'before'/name).write_bytes((S/name).read_bytes());(C/'patches'/('minimal-'+name+'.patch')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/UnrealGame/Source/CodexDungeon/'+name,tofile='b/UnrealGame/Source/CodexDungeon/'+name,n=2)),encoding='utf-8')
name='DungeonFairytaleGuardFullDrawStateV003.h';old=(S/name).read_text(encoding='utf-8-sig');new=old.replace('/** Full-v003','struct FDungeonFairytaleGuardRowResidentV001\n{FString TexturePath,ClassName;int32 Width=0,Height=0;bool ResourceReady=false,PendingInitialization=false;};\n/** Full-v003').replace(' TArray<FString> DrawStack;',' TArray<FString> DrawStack;\n bool QuadSubmitted=false,QuadScalePosition=false;\n FVector2D QuadTop=FVector2D::ZeroVector,QuadSize=FVector2D::ZeroVector,QuadUV=FVector2D::ZeroVector,QuadUVSize=FVector2D::ZeroVector,QuadRotationPivot=FVector2D::ZeroVector;\n double QuadRotationDegrees=0.,QuadDrawScale=1.,UIScale=1.;FLinearColor QuadTint=FLinearColor::White;\n TArray<FDungeonFairytaleGuardRowResidentV001> RowResidents;');patch(name,old,new)
name='DungeonFairytaleGuardFullPresentationV003.cpp';old=(S/name).read_text(encoding='utf-8-sig');new=old.replace('  UTexture2D* T=Frames.FindRef(Candidate.TexturePath);','  UTexture2D* T=Frames.FindRef(Candidate.TexturePath);\n  FDungeonFairytaleGuardRowResidentV001 RR;RR.TexturePath=T?T->GetPathName():Candidate.TexturePath;RR.ClassName=T?T->GetClass()->GetName():FString();RR.Width=T?T->GetSizeX():0;RR.Height=T?T->GetSizeY():0;RR.ResourceReady=T&&T->GetResource();RR.PendingInitialization=T&&T->HasPendingRenderResourceInitialization();R.RowResidents.Add(MoveTemp(RR));')
oldcall=' DrawTexture(Texture,float(R.TopScreen.X),float(R.TopScreen.Y),Width,Width,\n  R.Selection.Facing<0?1.f:0.f,0.f,R.Selection.Facing<0?-1.f:1.f,1.f,Tint);'
newcall=''' R.UIScale=double(UIScale);R.QuadTop={float(R.TopScreen.X),float(R.TopScreen.Y)};R.QuadSize={Width,Width};R.QuadUV={R.Selection.Facing<0?1.f:0.f,0.f};R.QuadUVSize={R.Selection.Facing<0?-1.f:1.f,1.f};R.QuadTint=Tint;R.QuadRotationDegrees=0.;R.QuadRotationPivot=FVector2D::ZeroVector;R.QuadDrawScale=1.;R.QuadScalePosition=false;
 DrawTexture(Texture,float(R.QuadTop.X),float(R.QuadTop.Y),float(R.QuadSize.X),float(R.QuadSize.Y),float(R.QuadUV.X),float(R.QuadUV.Y),float(R.QuadUVSize.X),float(R.QuadUVSize.Y),R.QuadTint,BLEND_Translucent,float(R.QuadDrawScale),R.QuadScalePosition,float(R.QuadRotationDegrees),R.QuadRotationPivot);R.QuadSubmitted=true;'''
assert oldcall in new;new=new.replace(oldcall,newcall);patch(name,old,new)
name='DungeonHUD.cpp';old=(S/name).read_text(encoding='utf-8-sig');new=old.replace('#include "DungeonHeroDeathProbeV001.h"','#include "DungeonHeroDeathProbeV001.h"\n#include "DungeonGuardStompProbeV001.h"').replace('        if(FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroDeathProofV001")))','        if(FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardStompProofV001")))GetWorld()->SpawnActor<ADungeonGuardStompProbeV001>();\n        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroDeathProofV001")))');patch(name,old,new)
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
(C/'exact-before-pins-v001.json').write_text(json.dumps(dict(files=[pin(S/name)for name in ['DungeonFairytaleGuardFullDrawStateV003.h','DungeonFairytaleGuardFullPresentationV003.cpp','DungeonHUD.cpp']],UE_HUD_DrawTexture_default_signature=pin(Path('G:/UE_5.5/Engine/Source/Runtime/Engine/Classes/GameFramework/HUD.h')),source_ids='Injected Root current approved rows, never hardcoded224/225'),indent=2)+'\n',encoding='utf-8')
print('New candidate Probe2 + 3 narrowpatches + exactbeforepins prepared; no actual Source/UE writes')
