#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "StoneGuardOwnerFixture_v002.h"
#include "../DungeonStoneGuardFeedback.h"
namespace
{
using namespace GuardOwnerTests;
namespace GF=DungeonGuardFeedback;
int32 CueCount(const GF::FJournal& J,GF::ECue Cue)
{int32 N=0;for(const auto& R:J.Entries())if(R.Cue==Cue)++N;return N;}
int32 FxCount(const ADungeonHUD* HUD,GF::EFx Fx)
{int32 N=0;for(const auto& R:HUD->GetGuardEffectSpawnRequests())if(R.Source.Effect==Fx)++N;return N;}
bool StartGuard(FGuardWorld& W,G::EAttack Kind=G::EAttack::AxeSweep)
{
 W.Guard=W.Game->SpawnStoneGuard(W.Player->GetGroundPosition()-FVector2D(Kind==G::EAttack::Stomp?55.:150.,0.));
 if(!W.Test.TestTrue(TEXT("Actual public ENM-STN-003 spawn has its dedicated native owner"),W.Guard&&W.Guard->GetStoneGuardDriver()))return false;
 for(int32 I=0;I<400&&!W.State().Action.InProgress&&!W.Game->bGameOver;++I)W.Frame(.01f);
 return W.Test.TestTrue(TEXT("Real completed GameMode ticks select requested action after native wake"),W.State().Action.InProgress&&W.State().Action.Kind==Kind);
}
bool OnceAndReadOnly(FGuardWorld& W)
{
 const auto Before=StateSig(W.State());const int32 A=W.HUD->GetGuardAudioPlayReceipts().Num(),F=W.HUD->GetGuardEffectSpawnRequests().Num();
 for(int32 I=0;I<7;++I)W.HUD->Tick(0.f);
 return W.Test.TestTrue(TEXT("Repeated real HUD consumption cannot replay or mutate Guard authority"),Before==StateSig(W.State())&&A==W.HUD->GetGuardAudioPlayReceipts().Num()&&F==W.HUD->GetGuardEffectSpawnRequests().Num());
}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonGuardFeedbackFlow,
 "CodexDungeon.Content.StoneGuardFeedback.RealWakeAxeStompAndCommittedMaterial",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonGuardFeedbackFlow::RunTest(const FString& Parameters)
{
 (void)Parameters;FGuardWorld W(*this);if(!W.Create()||!StartGuard(W))return false;
 // Stage0 intentionally fails one semantic witness; all following expectations remain frozen.
 if(!TestTrue(TEXT("Guard accepted WakeStarted is actually journaled and consumed by native HUD (Stage0 RED)"),CueCount(W.Guard->GetGuardFeedback(),GF::ECue::Wake)==1&&W.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_WAKE_01"))==1&&FxCount(W.HUD,GF::EFx::WakeCracks)==1))return false;
 TestEqual(TEXT("Actual axe windup voice is requested once before accepted window"),W.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_AXE_WINDUP_01")),1);
 const auto A=W.State().Action;if(!W.AdvanceTo(A.ActiveAt+.001))return false;
 TestTrue(TEXT("Accepted native Axe window, real hit receipt and actual target HP loss exist"),W.State().Windows.size()==1&&W.State().HitReceipts.size()==1&&W.Player->Health==76.f);
 TestEqual(TEXT("Axe release consumes original ActiveWindow exactly once"),W.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_AXE_RELEASE_01")),1);
 TestEqual(TEXT("Ground dust cut is a finite accepted-window presentation request"),FxCount(W.HUD,GF::EFx::AxeDustCut),1);
 TestEqual(TEXT("Outgoing material voice only follows native actual HP loss"),W.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_HIT_FLESH_LEATHER_01")),1);
 bool Matched=false;for(const auto& R:W.HUD->GetGuardAudioPlayReceipts())if(R.Source.Cue==GF::ECue::HitFleshLeather)
  for(const auto& E:W.State().Issued)if(E.Kind==G::EEventKind::Hit&&E.EventId==R.Source.EventId&&E.TargetId==R.Source.TargetId&&E.AtTime==R.Source.AtTime&&R.Source.ActualHPLoss==24.)Matched=true;
 TestTrue(TEXT("Material request keeps exact Guard Hit EventId/target/time and actual24HP commit"),Matched);
 W.Guard->ApplyCombatHit(1.6f,W.Player,0.f);W.HUD->Tick(0.f);
 TestTrue(TEXT("Incoming stone chips use actual mitigated1HP received receipt"),W.State().HP==184.&&W.State().ReceivedHits.back().ActualHPLoss==1.&&W.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_HIT_STONE_01"))==1&&FxCount(W.HUD,GF::EFx::StoneChips)==1);
 for(const auto& R:W.HUD->GetGuardAudioPlayReceipts())TestTrue(TEXT("Real play receipt has concrete loaded asset, source entity/event and fresh simulation time"),!R.SoundPath.IsEmpty()&&R.Source.EntityId==W.Guard->GetRuntimeEntityId()&&R.Source.EventId>0&&R.RequestedAt>=R.Source.AtTime&&R.RequestedAt-R.Source.AtTime<=.25&&R.Volume>0.f);
 if(!OnceAndReadOnly(W))return false;
 FGuardWorld S(*this);if(!S.Create()||!StartGuard(S,G::EAttack::Stomp)||!S.AdvanceTo(S.State().Action.ActiveAt+.001))return false;
 TestTrue(TEXT("Real extremely-close Stomp issues one window and one impact voice/effect"),S.State().Windows.size()==1&&S.State().Windows[0].Kind==G::EAttack::Stomp&&S.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_STOMP_WINDUP_01"))==1&&S.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_STOMP_IMPACT_01"))==1&&FxCount(S.HUD,GF::EFx::StompBurst)==1);
 return OnceAndReadOnly(S);
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonGuardFeedbackInterrupt,
 "CodexDungeon.Content.StoneGuardFeedback.InterruptIssuedWindowDeathAndOnceConsumption",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonGuardFeedbackInterrupt::RunTest(const FString& Parameters)
{
 (void)Parameters;FGuardWorld W(*this);if(!W.Create()||!StartGuard(W))return false;const auto A=W.State().Action;
 if(!W.AdvanceTo(A.ActiveAt-.1))return false;W.Guard->ApplyCombatHit(1.6f,W.Player,85.f);W.HUD->Tick(0.f);
 if(!TestTrue(TEXT("Actual public poise85 interruption consumes one stun and cancellation request (Stage0 RED)"),W.State().Phase==G::EPhase::Stunned&&W.State().HP==184.&&W.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_STUN_01"))==1&&FxCount(W.HUD,GF::EFx::StunChips)==1&&FxCount(W.HUD,GF::EFx::CancelAttack)==1))return false;
 if(!W.AdvanceTo(A.ActiveEnd+.01))return false;
 TestTrue(TEXT("Cancelled pre-window attack never fabricates/replays a release or hit"),W.State().Windows.empty()&&W.State().HitReceipts.empty()&&W.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_AXE_RELEASE_01"))==0);
 if(!OnceAndReadOnly(W))return false;
 FGuardWorld Issued(*this);if(!Issued.Create()||!StartGuard(Issued)||!Issued.AdvanceTo(Issued.State().Action.ActiveAt+.001))return false;
 const auto Original=Issued.State().Action;Issued.Guard->ApplyCombatHit(1.6f,Issued.Player,85.f);Issued.HUD->Tick(0.f);
 if(!Issued.AdvanceTo(Original.ActiveEnd+.01))return false;
 TestTrue(TEXT("Already-issued swing is preserved once; later closure cannot retract or replay it"),Issued.State().Windows.size()==1&&Issued.State().Closures.size()==1&&Issued.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_AXE_RELEASE_01"))==1);
 Issued.Guard->ApplyCombatHit(100000.f,Issued.Player,0.f);Issued.HUD->Tick(0.f);
 TestTrue(TEXT("Actual lethal receipt emits exactly one fracture voice and finite death chunks"),Issued.Guard->bDead&&Issued.State().HP==0.&&Issued.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_DEATH_01"))==1&&FxCount(Issued.HUD,GF::EFx::DeathChunks)==1);
 const auto Dead=StateSig(Issued.State());Issued.Guard->ApplyCombatHit(100000.f,Issued.Player,85.f);Issued.Game->OnFighterDied(Issued.Guard);Issued.Game->OnFighterDied(Issued.Guard);Issued.HUD->Tick(0.f);
 TestTrue(TEXT("Repeated dead contact/death observation cannot create additional Guard events or fracture"),Dead==StateSig(Issued.State())&&Issued.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_DEATH_01"))==1&&FxCount(Issued.HUD,GF::EFx::DeathChunks)==1);
 return OnceAndReadOnly(Issued);
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonGuardFeedbackRestore,
 "CodexDungeon.Content.StoneGuardFeedback.RestoreSeedsFutureOnlyAndLateHud",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonGuardFeedbackRestore::RunTest(const FString& Parameters)
{
 (void)Parameters;FGuardWorld W(*this);if(!W.Create()||!W.Rich())return false;
 FDungeonRunSnapshot Saved;FDungeonValidatedRun Valid;if(!SealGuard(W,Saved,Valid))return false;
 FGuardWorld T(*this);if(!T.Create())return false;FDungeonPreparedRun P;FString Why;
 if(!TestTrue(TEXT("Existing real installer prepares/installs complete accepted Guard root"),FDungeonRunInstaller::Prepare(*T.Game,Valid,P,Why)&&FDungeonRunInstaller::Install(*T.Game,P,Why))){AddInfo(Why);return false;}
 T.Player=T.Game->PlayerFighter;for(auto E:T.Game->Enemies)if(E&&E->GetRuntimeEntityId()==W.Guard->GetRuntimeEntityId())T.Guard=E;
 if(!TestTrue(TEXT("Installed dedicated003 exists with original all-history signature"),T.Guard&&StateSig(T.State())==StateSig(W.State())))return false;
 const auto SavedCursor=T.State().NextEventId;FDungeonRunSnapshot Paused;
 T.Frame(.2f);TestTrue(TEXT("Install pause preserves entire saved aggregate and does not replay any Guard presentation"),T.Game->CaptureRunSnapshot(Paused,Why)&&RunSig(Paused)==RunSig(Saved)&&T.HUD->GetGuardAudioPlayReceipts().IsEmpty()&&T.HUD->GetGuardEffectSpawnRequests().IsEmpty());
 T.Frame(.005f);if(!T.Pulse(EKeys::Enter)||!T.AdvanceTo(T.State().Action.ActiveEnd+.01))return false;
 T.Guard->ApplyCombatHit(1.6f,T.Player,0.f);T.HUD->Tick(0.f);
 if(!TestTrue(TEXT("Restored journal seeds saved cursor then consumes only next actual1HP event (Stage0 RED)"),T.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_HIT_STONE_01"))==1&&CueCount(T.Guard->GetGuardFeedback(),GF::ECue::HitStone)==1))return false;
 TestTrue(TEXT("Restored old wake/swing/hit/stun cannot replay"),T.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_WAKE_01"))==0&&T.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_AXE_RELEASE_01"))==0&&T.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_STUN_01"))==0&&T.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_HIT_FLESH_LEATHER_01"))==0);
 const auto& R=T.HUD->GetGuardAudioPlayReceipts().Last();TestTrue(TEXT("Future actual request retains event at or beyond saved NextEventId and exact incoming loss"),R.Source.EventId>=SavedCursor&&R.Source.ActualHPLoss==1.&&R.Source.AtTime==T.Game->GetSimulationTime());
 if(!OnceAndReadOnly(T))return false;
 T.Controller->ClientSetHUD_Implementation(ADungeonHUD::StaticClass());T.HUD=Cast<ADungeonHUD>(T.Controller->GetHUD());if(!T.HUD)return false;
 if(!T.HUD->HasActorBegunPlay())T.HUD->DispatchBeginPlay();T.HUD->Tick(0.f);
 TestTrue(TEXT("Genuinely rebuilt late HUD attaches at live journal tail without historical requests"),T.HUD->GetGuardAudioPlayReceipts().IsEmpty()&&T.HUD->GetGuardEffectSpawnRequests().IsEmpty());
 T.Guard->ApplyCombatHit(1.6f,T.Player,0.f);T.HUD->Tick(0.f);TestEqual(TEXT("Late HUD consumes next fresh actual stone receipt once"),T.HUD->GetGuardAudioPlayRequests(TEXT("GUARD_HIT_STONE_01")),1);
 // Native kernel locomotion, not a fabricated movement event or actor teleport.
 G::FGuardKernel K(9001);K.BeginCombat();K.NotifyOtherAcceptedEnemiesCleared();G::FWorldInput World;World.HasTarget=true;World.Target={450,0,0};World.CanStartAttack=false;World.Sweep=[](const G::FSweepRequest&){return G::FSweepResult{};};
 GF::FJournal Before;TestTrue(TEXT("New live native movement journal begins"),Before.Begin(K.State()));
 for(int I=0;I<160&&K.State().Position.X<90.;++I){const auto B=K.StepTo(double(I+1)*.01,World);if(!B.Accepted)return false;Before.Observe(B.Events,K.State().Position);}
 GF::FJournal Restored;if(!TestTrue(TEXT("Saved native motion history can seed fresh presentation without records"),Restored.Begin(K.State())&&Restored.Entries().empty()&&Restored.LastEventId()==K.State().NextEventId-1))return false;
 const auto Seed=K.State();for(int I=0;I<30;++I){const auto B=K.StepTo(Seed.Time+double(I+1)*.01,World);if(!B.Accepted)return false;Before.Observe(B.Events,K.State().Position);Restored.Observe(B.Events,K.State().Position);}
 const GF::FRecord* AStep=nullptr,*BStep=nullptr;for(const auto& Q:Before.Entries())if(Q.Cue==GF::ECue::Step&&Q.EventId>=Seed.NextEventId)AStep=&Q;for(const auto& Q:Restored.Entries())if(Q.Cue==GF::ECue::Step)BStep=&Q;
 TestTrue(TEXT("Restored stride remainder yields identical next real foot ordinal/time/position without old step replay"),AStep&&BStep&&AStep->FootOrdinal==BStep->FootOrdinal&&AStep->AtTime==BStep->AtTime&&AStep->Position.X==BStep->Position.X);
 return OnceAndReadOnly(T);
}
#endif
