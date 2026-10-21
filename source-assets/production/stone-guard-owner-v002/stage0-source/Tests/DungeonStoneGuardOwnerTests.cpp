#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "StoneGuardOwnerFixture_v002.h"
#include <limits>
namespace
{
using namespace GuardOwnerTests;
namespace Codec=DungeonRunSnapshotCodec;
bool V1Positive(FGuardWorld& F,FDungeonRunSnapshot& Saved,FDungeonValidatedRun& Sealed)
{
 if(!CodecSeal(F,Saved,Sealed,TEXT("Genuine no-Guard V1 aggregate positive control")))return false;
 TArray<uint8> Bytes;FString Why;const auto Expected=FCodecOracle::Bytes(Saved);
 if(!F.Test.TestTrue(TEXT("Existing V1 codec bytes stay exactly the immutable independent oracle before Guard support is exercised"),
   Saved.Schema==1&&Saved.Scope==EDungeonRunScope::BoundDevelopmentV1&&Codec::Encode(Saved,Bytes,Why)&&Bytes==Expected))return false;
 FDungeonValidatedRun Again;return F.Test.TestTrue(TEXT("Existing independent V1 bytes decode unchanged"),Codec::Decode(Expected,Again,Why)&&Again.IsValid()&&CodecSignature(*Again.Get())==CodecSignature(Saved));
}
bool DeepReadback(FAutomationTestBase& T,const FDungeonFighterOwnerSnapshot& Saved,ADungeonFighter& Actor,const FDungeonFighterRestoreContext& C)
{
 FString Why;FDungeonFighterOwnerSnapshot Back;
 return T.TestTrue(TEXT("Native readback preserves every native owner field plus all33Guard fields,five histories,Policy and observer bit"),
  Actor.CaptureOwnerSnapshot(Back,Why,&C)&&OwnerSig(Back)==OwnerSig(Saved));
}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonStoneGuardOwnerNative,
 "CodexDungeon.Content.StoneGuardOwner.NativePolicyHistoriesAndAtomicRestore",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonStoneGuardOwnerNative::RunTest(const FString& Parameters)
{
 (void)Parameters;using namespace GuardOwnerTests;FGuardWorld F(*this);if(!TestTrue(TEXT("Real complete native no-Guard Scene fixture"),F.Create()))return false;
 FDungeonRunSnapshot Legacy;FDungeonValidatedRun LegacySealed;if(!V1Positive(F,Legacy,LegacySealed)||!F.Rich())return false;
 const auto RealState=F.State();G::FGuardKernel Pure(RealState.EntityId,RealState.InitialTime,RealState.InitialPosition,RealState.Facing,F.Guard->GetStoneGuardDriver()->CapturePolicy());
 if(!TestTrue(TEXT("Already implemented pure Restore independently validates the actual native driver history before Owner stub"),Pure.Restore(RealState)&&StateSig(Pure.Capture())==StateSig(RealState)))return false;
 FDungeonFighterOwnerSnapshot Saved;if(!F.CaptureGuard(Saved))return false;
 TestTrue(TEXT("Only exact003 uses appended Guard kind/schema3; old variants are absent"),Saved.Schema==3&&Saved.Kind==EDungeonFighterOwnerKind::StoneGuard&&Saved.Guard.IsSet()
  &&!Saved.Player.IsSet()&&!Saved.Knight.IsSet()&&!Saved.Bat.IsSet()&&Saved.EnemyContentId==TEXT("ENM-STN-003"));
 if(!Saved.Guard.IsSet())return false;
 TestTrue(TEXT("Default Policy is captured explicitly; producer and native observer are independent facts"),Saved.Guard->Schema==1&&Saved.Guard->Policy.ExtremelyCloseRadius==70
  &&StateSig(Saved.Guard->Kernel)==StateSig(RealState)&&!Saved.Guard->DeathObserved&&!Saved.DeathReported&&!Saved.Guard->Kernel.RewardClaimed);
 auto E=F.Game->CaptureEquipmentSnapshot();const auto C=F.Context(E);FString Why;
 auto Receiver=F.World->SpawnActor<ADungeonFighter>();if(!TestNotNull(TEXT("Real independent native receiver Actor"),Receiver))return false;Receiver->SetActorTickEnabled(false);
 if(!TestTrue(TEXT("Whole Owner restores without BeginCombat,Step,Sync,heal or new logicalIDs"),Receiver->RestoreOwnerSnapshot(Saved,C,Why)))return false;
 DeepReadback(*this,Saved,*Receiver,C);
 // Policy is outside FState. A real independently validated custom-policy
 // receiver provides the policy/value source; no history element is invented.
 G::FGuardKernel CustomPure(RealState.EntityId,RealState.InitialTime,RealState.InitialPosition,RealState.Facing,{123});
 if(!TestTrue(TEXT("Real custom123Policy receiver independently accepts the same immutable birth/history"),CustomPure.Restore(RealState)))return false;
 auto Custom=Saved;Custom.Guard->Policy=CustomPure.CapturePolicy();Custom.Guard->Kernel=CustomPure.Capture();
 const auto ActorBefore=F.Guard->GetActorTransform();FDungeonStoneGuardDriver CustomDriver(F.Guard,RealState.EntityId,RealState.InitialTime,RealState.InitialPosition,CustomPure.CapturePolicy());
 if(TestTrue(TEXT("Driver Restore accepts explicit nondefault savedPolicy without world queries or actor mutation"),CustomDriver.Restore(Custom.Guard->Kernel)))
 {
  TestTrue(TEXT("Driver preserves all33values and123policy while native Actor is untouched"),StateSig(CustomDriver.Capture())==StateSig(RealState)
   &&CustomDriver.CapturePolicy().ExtremelyCloseRadius==123&&F.Guard->GetActorTransform().Equals(ActorBefore,0.));
  const auto Before=StateSig(CustomDriver.Capture());auto WrongBirth=RealState;WrongBirth.InitialTime+=1;
  TestTrue(TEXT("Wrongbirth Driver Restore is atomic"),!CustomDriver.Restore(WrongBirth)&&StateSig(CustomDriver.Capture())==Before&&CustomDriver.CapturePolicy().ExtremelyCloseRadius==123);
 }
 if(TestTrue(TEXT("Whole native Owner reconstructs saved123Policy rather than default70"),Receiver->RestoreOwnerSnapshot(Custom,C,Why)))
 {DeepReadback(*this,Custom,*Receiver,C);TestTrue(TEXT("Actual reconstructed Driver retained nondefault configuration"),Receiver->GetStoneGuardDriver()&&Receiver->GetStoneGuardDriver()->CapturePolicy().ExtremelyCloseRadius==123);}
 FDungeonFighterOwnerSnapshot Before;if(!Receiver->CaptureOwnerSnapshot(Before,Why,&C))return false;const auto BeforeSig=OwnerSig(Before);const auto* Pointer=Receiver->GetStoneGuardDriver();
 TArray<FDungeonFighterOwnerSnapshot> Bad;
 auto B=Custom;B.Schema=2;Bad.Add(B);B=Custom;B.EnemyContentId=TEXT("ENM-STN-002");Bad.Add(B);
 B=Custom;B.Guard->Policy.ExtremelyCloseRadius=161;Bad.Add(B);B=Custom;B.Guard->Policy.ExtremelyCloseRadius=std::numeric_limits<double>::quiet_NaN();Bad.Add(B);
 B=Custom;++B.Guard->Kernel.InitialTime;Bad.Add(B);B=Custom;++B.Guard->Kernel.EntityId;Bad.Add(B);
 B=Custom;B.Knight=F.Game->Enemies[0]->GetStoneKnightDriver()->Capture();Bad.Add(B);
 B=Custom;B.Guard->Kernel.HitReceipts[0].TargetId=std::numeric_limits<uint64>::max();Bad.Add(B);
 B=Custom;B.Guard->Kernel.Closures[0].AtTime=B.Guard->Kernel.Windows[0].End+1;Bad.Add(B);
 B=Custom;B.Guard->Kernel.ReceivedHits[0].ActualHPLoss+=1;Bad.Add(B);
 B=Custom;++B.Guard->Kernel.Issued[0].EventId;Bad.Add(B);B=Custom;B.DeathReported=true;Bad.Add(B);
 for(const auto& Invalid:Bad)
 {
  TestFalse(TEXT("Malformed/cross-owner Guard Owner rejects atomically"),Receiver->RestoreOwnerSnapshot(Invalid,C,Why));FDungeonFighterOwnerSnapshot After;
  TestTrue(TEXT("Rejected Restore preserves Driver identity and every native/history value"),Receiver->GetStoneGuardDriver()==Pointer&&Receiver->CaptureOwnerSnapshot(After,Why,&C)&&OwnerSig(After)==BeforeSig);
 }
 const auto SavedSig=OwnerSig(Custom);Receiver->Destroy();F.Guard->bAIEnabled=false;F.Frame(.02f);
 TestTrue(TEXT("Captured histories own deep storage after real source advances"),OwnerSig(Custom)==SavedSig&&StateSig(F.State())!=StateSig(Custom.Guard->Kernel));
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonStoneGuardOwnerCodec,
 "CodexDungeon.Content.StoneGuardOwner.RootV2ExactCodecAndLegacyV1Bytes",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonStoneGuardOwnerCodec::RunTest(const FString& Parameters)
{
 (void)Parameters;using namespace GuardOwnerTests;FGuardWorld F(*this);if(!TestTrue(TEXT("Real native Scene source for strictCodec"),F.Create()))return false;
 FDungeonRunSnapshot Legacy;FDungeonValidatedRun V1;if(!V1Positive(F,Legacy,V1)||!F.Rich())return false;
 FDungeonRunSnapshot Saved;FDungeonValidatedRun Positive;if(!SealGuard(F,Saved,Positive))return false;
 const auto Exact=RunSig(Saved);const auto Document=FGuardWire::DocumentV2(Saved);const auto Expected=FCodecOracle::Bytes(Document);TArray<uint8> Encoded{0x77,0};FString Why;
 if(!TestTrue(TEXT("Explicit Schema2 BoundV2 Run encodes using bound-run-v2"),Codec::Encode(Saved,Encoded,Why)))return false;
 TestTrue(TEXT("Every V2 named nested field equals independent decimal/hex/null/ordered-array oracle"),Encoded==Expected&&RunSig(Saved)==Exact);
 FDungeonValidatedRun Decoded;if(!TestTrue(TEXT("Decode independent V2 oracle bytes seals the whole guarded aggregate"),Codec::Decode(Expected,Decoded,Why)&&Decoded.IsValid()))return false;
 TestTrue(TEXT("Full root plus all33Guard fields/five histories/policy/observer survive typed decode bit-exact"),RunSig(*Decoded.Get())==Exact);
 TArray<uint8> Again;TestTrue(TEXT("Repeated typed V2 encoding is canonical"),Codec::Encode(*Decoded.Get(),Again,Why)&&Again==Expected);
 int32 Index=INDEX_NONE;for(int32 I=0;I<Saved.Fighters.Num();++I)if(Saved.Fighters[I].Guard.IsSet())Index=I;
 if(!TestTrue(TEXT("Exactly real current Guard index is found"),Index!=INDEX_NONE))return false;
 const auto Reject=[&](const JO& Wrong,const TCHAR* Label)
 {auto Out=Decoded;const auto* Ptr=Out.Get();const auto Bytes=RunSig(*Ptr);TestFalse(Label,Codec::Decode(FCodecOracle::Bytes(Wrong),Out,Why));TestTrue(TEXT("Codec failure leaves sealed pointer and complete typed values unchanged"),Out.Get()==Ptr&&RunSig(*Out.Get())==Bytes);};
 // Every actual state field is mandatory. Missing a container cannot become an empty default.
 const auto StateObject=Document->GetObjectField(TEXT("snapshot"))->GetArrayField(TEXT("Fighters"))[Index]->AsObject()->GetObjectField(TEXT("Guard"))->GetObjectField(TEXT("Kernel"));
 TArray<FString> Keys;StateObject->Values.GetKeys(Keys);TestEqual(TEXT("Independent wire oracle explicitly names all33state fields"),Keys.Num(),33);
 for(const auto& K:Keys){auto Wrong=FGuardWire::DocumentV2(Saved);Wrong->GetObjectField(TEXT("snapshot"))->GetArrayField(TEXT("Fighters"))[Index]->AsObject()->GetObjectField(TEXT("Guard"))->GetObjectField(TEXT("Kernel"))->RemoveField(K);Reject(Wrong,TEXT("Every Guard state field is required"));}
 auto Wrong=FGuardWire::DocumentV2(Saved);Wrong->SetStringField(TEXT("codec"),TEXT("bound-run-v1"));Reject(Wrong,TEXT("V1 never silently accepts Guard/V2 fields"));
 Wrong=FGuardWire::DocumentV2(Saved);Wrong->GetObjectField(TEXT("snapshot"))->SetField(TEXT("Schema"),FCodecOracle::Value(uint32(1)));Reject(Wrong,TEXT("V2 discriminator cannot relabel an old root schema"));
 Wrong=FGuardWire::DocumentV2(Saved);Wrong->GetObjectField(TEXT("snapshot"))->GetArrayField(TEXT("Fighters"))[0]->AsObject()->RemoveField(TEXT("Guard"));Reject(Wrong,TEXT("V2 requires explicitnull Guard even on player"));
 Wrong=FGuardWire::DocumentV2(Saved);auto WGuard=Wrong->GetObjectField(TEXT("snapshot"))->GetArrayField(TEXT("Fighters"))[Index]->AsObject()->GetObjectField(TEXT("Guard"));WGuard->RemoveField(TEXT("Policy"));Reject(Wrong,TEXT("Missing savedPolicy is never healed to70"));
 Wrong=FGuardWire::DocumentV2(Saved);Wrong->GetObjectField(TEXT("snapshot"))->GetArrayField(TEXT("Fighters"))[Index]->AsObject()->GetObjectField(TEXT("Guard"))->SetBoolField(TEXT("unexpected"),true);Reject(Wrong,TEXT("Unknown Guard field rejects"));
 auto Invalid=Saved;Invalid.Schema=1;Encoded={0x17,0x29};const auto Initial=Encoded;TestTrue(TEXT("Invalid V1/V2 Encode is byteatomic"),!Codec::Encode(Invalid,Encoded,Why)&&Encoded==Initial);
 TArray<uint8> LegacyAgain;TestTrue(TEXT("V1 byte contract remains unchanged after V2 usage"),Codec::Encode(Legacy,LegacyAgain,Why)&&LegacyAgain==FCodecOracle::Bytes(Legacy));
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonStoneGuardOwnerInstall,
 "CodexDungeon.Content.StoneGuardOwner.StagedInstallContinuationAndDeathObserver",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonStoneGuardOwnerInstall::RunTest(const FString& Parameters)
{
 (void)Parameters;using namespace GuardOwnerTests;FGuardWorld Source(*this),Target(*this);
 if(!TestTrue(TEXT("Two independent real bound worlds with original valid Runs"),Source.Create()&&Target.Create()))return false;
 FDungeonRunSnapshot SourceV1,Before;FDungeonValidatedRun SourceV1Sealed,BeforeSealed;
 if(!V1Positive(Source,SourceV1,SourceV1Sealed)||!V1Positive(Target,Before,BeforeSealed)||!Source.Rich())return false;
 FDungeonRunSnapshot Saved;FDungeonValidatedRun Sealed;if(!SealGuard(Source,Saved,Sealed))return false;
 const uint64 Id=Source.Guard->GetRuntimeEntityId();const auto* SavedGuard=FindGuard(Saved,Id);if(!TestTrue(TEXT("Real currentGuard source has five deep histories before staging"),SavedGuard&&SavedGuard->Guard.IsSet()))return false;
 const auto Exact=RunSig(Saved);const auto GuardExact=StateSig(SavedGuard->Guard->Kernel);FString Why;const uint64 Serial=Target.Game->GetRunRestartSerial();auto* OldPlayer=Target.Player;
 {
  FDungeonPreparedRun Released;if(!TestTrue(TEXT("Real full saved Guard prepares hidden independent actors before publication"),FDungeonRunInstaller::Prepare(*Target.Game,Sealed,Released,Why)&&Released.IsReady()))return false;
  TestTrue(TEXT("Prepared copy retains every field/history independent from source"),Released.GetSavedSnapshot()&&RunSig(*Released.GetSavedSnapshot())==Exact&&Target.Game->PlayerFighter==OldPlayer);
  for(const auto& A:Released.GetStagedActors())TestTrue(TEXT("Every actual staged object stays hidden/tickoff/collisionoff"),A.IsValid()&&A->IsHidden()&&!A->IsActorTickEnabled()&&!A->GetActorEnableCollision());
 }
 FDungeonRunSnapshot AfterRelease;TestTrue(TEXT("RAII release restores oldRun gate/identity/values without logical restart"),Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open&&Target.Game->PlayerFighter==OldPlayer
  &&Target.Game->CaptureRunSnapshot(AfterRelease,Why)&&RunSig(AfterRelease)==RunSig(Before)&&Target.Game->GetRunRestartSerial()==Serial);
 FDungeonPreparedRun Prepared;if(!TestTrue(TEXT("Real Guard group prepares and installs through existing full boundary"),FDungeonRunInstaller::Prepare(*Target.Game,Sealed,Prepared,Why)&&FDungeonRunInstaller::Install(*Target.Game,Prepared,Why)))return false;
 Target.Player=Target.Game->PlayerFighter;Target.Guard=nullptr;for(auto Enemy:Target.Game->Enemies)if(Enemy&&Enemy->GetRuntimeEntityId()==Id)Target.Guard=Enemy;
 if(!TestTrue(TEXT("New real003 Actor owns dedicated Driver with exact immutable birth"),Target.Guard&&Target.Guard->GetStoneGuardDriver()&&StateSig(Target.State())==GuardExact))return false;
 FDungeonRunSnapshot Installed;if(!Target.Game->CaptureRunSnapshot(Installed,Why))return TestTrue(TEXT("Installed guarded Run must recapture"),false);
 TestTrue(TEXT("Actual paused full readback equals all saved native/history fields"),RunSig(Installed)==Exact&&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue&&Target.Game->GetRunRestartSerial()==Serial);
 Target.Frame(.4f);FDungeonRunSnapshot Paused;TestTrue(TEXT("Technical pause freezes Guard producer/native transforms/IDs/Policy as well as rootclock"),Target.Game->CaptureRunSnapshot(Paused,Why)&&RunSig(Paused)==Exact);
 Target.Frame(.005f);if(!Target.Key(EKeys::Enter,true))return false;Target.Frame(.005f);if(!Target.Key(EKeys::Enter,false))return false;
 if(!TestTrue(TEXT("Real neutral then freshEnter resumes without BeginRun/reset/RNG"),Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open&&Target.Game->GetRunRestartSerial()==Serial))return false;
 // Source and restored run receive the exact same genuine future public ticks.
 // The Enter admission tick intentionally does not simulate the saved run.
 TestTrue(TEXT("ExplicitContinue did not consume old action deadline on admission"),Target.Game->GetSimulationTime()==Saved.SimulationTime);
 const double End=SavedGuard->Guard->Kernel.Action.ActiveEnd+.05;
 if(!TestTrue(TEXT("Original and installed Guard reach original activeEnd using real central-clock ticks"),Source.AdvanceTo(End)&&Target.AdvanceTo(End)))return false;
 TestTrue(TEXT("Future Guard histories/cursors/once-hit obligations remain identical"),StateSig(Source.State())==StateSig(Target.State())&&Source.Player->Health==Target.Player->Health);
 Source.Guard->ApplyCombatHit(1.6f,Source.Player,0.f);Target.Guard->ApplyCombatHit(1.6f,Target.Player,0.f);
 TestTrue(TEXT("Next native mitigation receipt advances from saved cursor exactly once"),StateSig(Source.State())==StateSig(Target.State())&&Target.State().LastDamageReceiptId>SavedGuard->Guard->Kernel.LastDamageReceiptId);
 // Genuine death observation and local eligibility are distinct from the
 // unsupported formal reward consumer; neither a5coin nor roomClear is invented.
 Target.Guard->ApplyCombatHit(100000.f,Target.Player,85.f);
 if(!TestTrue(TEXT("Actual native death is observed once with formal003 settlement still false"),Target.Guard->bDead&&Target.Guard->IsStoneGuardDeathObserved()&&!Target.Guard->bDeathReported&&!Target.State().RewardClaimed))return false;
 FDungeonFighterOwnerSnapshot DeadUnclaimed;if(!Target.CaptureGuard(DeadUnclaimed))return false;
 TestTrue(TEXT("DeathObserved true and localRewardClaimed false are separately retained"),DeadUnclaimed.Guard->DeathObserved&&!DeadUnclaimed.Guard->Kernel.RewardClaimed&&!DeadUnclaimed.DeathReported);
 if(!TestTrue(TEXT("Actual local eligibility consumed exactlyonce without formalreward"),Target.Guard->ClaimStoneGuardDeathEligibility()&&!Target.Guard->ClaimStoneGuardDeathEligibility()))return false;
 Target.Game->LastMessage=TEXT("saved003-independent-death-observer");FDungeonRunSnapshot DeadSaved;FDungeonValidatedRun DeadSealed;
 if(!SealGuard(Target,DeadSaved,DeadSealed))return false;
 const auto* DeadGuard=FindGuard(DeadSaved,Id);TestTrue(TEXT("Current003 reward validation includes exact localtrue/formalfalse fact rather than omitting003"),DeadGuard&&DeadGuard->Guard->DeathObserved&&DeadGuard->Guard->Kernel.RewardClaimed&&!DeadGuard->DeathReported
  &&!DeadSaved.Rewards.Deaths.ContainsByPredicate([Id](const auto& D){return D.Death.EntityId==Id;}));
 FGuardWorld DeadTarget(*this);if(!TestTrue(TEXT("Independent valid target for actual deadGuard installation"),DeadTarget.Create()))return false;FDungeonPreparedRun DeadPrepared;
 if(!TestTrue(TEXT("Dead localclaimed Guard fully stages/installs without observer or reward replay"),FDungeonRunInstaller::Prepare(*DeadTarget.Game,DeadSealed,DeadPrepared,Why)&&FDungeonRunInstaller::Install(*DeadTarget.Game,DeadPrepared,Why)))return false;
 DeadTarget.Player=DeadTarget.Game->PlayerFighter;for(auto Enemy:DeadTarget.Game->Enemies)if(Enemy&&Enemy->GetRuntimeEntityId()==Id)DeadTarget.Guard=Enemy;
 if(!TestTrue(TEXT("Native installed observer retained independently from formalDeathReported"),DeadTarget.Guard&&DeadTarget.Guard->IsStoneGuardDeathObserved()&&!DeadTarget.Guard->bDeathReported&&DeadTarget.State().RewardClaimed))return false;
 FDungeonRunSnapshot DeadBack;TestTrue(TEXT("Terminal presentation and every producer history match saved full root before resuming"),DeadTarget.Game->CaptureRunSnapshot(DeadBack,Why)&&RunSig(DeadBack)==RunSig(DeadSaved));
 DeadTarget.Frame(.005f);if(!DeadTarget.Key(EKeys::Enter,true))return false;DeadTarget.Frame(.005f);if(!DeadTarget.Key(EKeys::Enter,false))return false;const int32 Pickups=DeadTarget.Game->Pickups.Num();const int32 Coins=DeadTarget.Player->Coins;
 DeadTarget.Game->OnFighterDied(DeadTarget.Guard);DeadTarget.Game->OnFighterDied(DeadTarget.Guard);
 TestTrue(TEXT("Restored observer prevents repeatLastMessage/eligibility/coin/roomclear consumers"),DeadTarget.Game->LastMessage==DeadSaved.LastMessage&&!DeadTarget.Guard->ClaimStoneGuardDeathEligibility()
  &&DeadTarget.Game->Pickups.Num()==Pickups&&DeadTarget.Player->Coins==Coins&&DeadTarget.Game->bRoomCleared==DeadSaved.RoomCleared);
 return true;
}
#endif
