#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "../DungeonFairytaleSwordWalkProfile.h"
#include "../DungeonRunInstaller.h"
#include "../DungeonRunSnapshotCodec.h"
#include "RunCodecFixture_v001.h"

namespace
{
struct FWalkCommandLineScope
{
 const FString Original=FCommandLine::Get();
 ~FWalkCommandLineScope(){FCommandLine::Set(*Original);}
 bool RemoveWalkOptIn()
 {
  FString Without=Original;
  Without.ReplaceInline(TEXT("-DungeonFairytaleSwordWalkPreview"),TEXT(""),ESearchCase::IgnoreCase);
  FCommandLine::Set(*Without);
  return !FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordWalkPreview"));
 }
};
FDungeonFighterRestoreContext WalkOwnerContext(const FDungeonRunSnapshot& S)
{
 FDungeonFighterRestoreContext C;C.RunGuid=S.RunGuid;C.RoomInstanceId=S.RoomInstanceId;C.EntityId=S.OwnerId;
 C.SimulationTime=S.SimulationTime;C.GameOver=S.GameOver;C.Equipment=&S.Equipment;C.WeaponWorld=&S.WeaponWorld.State;return C;
}
// Independent expected modulo, from completed actual XY distance and immutable
// compiled values. It does not call the production phase Advance/Frame helpers.
double ExpectedWalkPhase(double Before,double Distance,const DungeonGroundWalk::FPolicy& P)
{return std::fmod(Before/P.CycleSeconds+Distance/P.CycleDistance,1.)*P.CycleSeconds;}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFairytaleWalkConfiguredLabelContinuity,
 "CodexDungeon.Content.FairytaleGroundWalk.Configured.LabelSaveAndOptOutContinuity",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFairytaleWalkConfiguredLabelContinuity::RunTest(const FString&)
{
 // Pending art data is an explicit prerequisite failure, never a skipped PASS
 // or a synthetic/runtime profile override. Root must freeze the table first.
 if(!TestTrue(TEXT("REQUIRES configured retained actual Walk profile; pending table cannot certify new label"),DungeonFairytaleSwordWalkV001::Valid()))return false;
 if(!TestTrue(TEXT("REQUIRES real initial DungeonFairytaleSwordWalkPreview command-line opt-in"),
  FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordWalkPreview"))))return false;
 FWalkCommandLineScope CommandLine;const auto& P=DungeonFairytaleSwordWalkV001::Profile().Gait;
 const double FloatTolerance=2.e-6*FMath::Max(1.,P.CycleSeconds);
 FCodecWorld Source(*this);if(!Source.Create()||!Source.Key(EKeys::D,true))return false;Source.Frame(.02f);
 if(!Source.Key(EKeys::D,false))return false;
 FDungeonRunSnapshot Initial;FString Why;
 if(!TestTrue(TEXT("Actual opted-in normal movement captures its new distance label"),Source.Game->CaptureRunSnapshot(Initial,Why)
  &&Initial.Fighters[0].AnimationName==DungeonFairytaleSwordWalkV001::AnimationLabel&&Initial.Fighters[0].Moving))return false;

 // An existing legacy owner clock is restored exactly. Its arbitrary finite
 // historical wall time must not seed the first newly opted-in distance phase.
 auto Legacy=Initial.Fighters[0];Legacy.AnimationName=TEXT("walk");Legacy.AnimationTime=12345.25f;
 const auto InitialContext=WalkOwnerContext(Initial);
 if(!TestTrue(TEXT("Legacy walk retains exact historical wall clock through real owner Restore"),
  Source.Player->RestoreOwnerSnapshot(Legacy,InitialContext,Why)&&Source.Player->AnimationName==TEXT("walk")
  &&Source.Player->AnimationTime==Legacy.AnimationTime))return false;
 FDungeonRunSnapshot LegacyRun;TArray<uint8> LegacyBytes;FDungeonValidatedRun LegacyDecoded;
 if(!TestTrue(TEXT("Existing codec roundtrip does not reinterpret legacy walk time"),Source.Game->CaptureRunSnapshot(LegacyRun,Why)
  &&DungeonRunSnapshotCodec::Encode(LegacyRun,LegacyBytes,Why)&&DungeonRunSnapshotCodec::Decode(LegacyBytes,LegacyDecoded,Why)
  &&LegacyDecoded.IsValid()&&LegacyDecoded.Get()->Fighters[0].AnimationName==TEXT("walk")
  &&LegacyDecoded.Get()->Fighters[0].AnimationTime==12345.25f))return false;
 const auto FromLegacy=Source.Player->GetGroundPosition();if(!Source.Key(EKeys::D,true))return false;Source.Frame(.02f);
 const double LegacyDistance=(Source.Player->GetGroundPosition()-FromLegacy).Size();
 TestTrue(TEXT("First actual opted-in distance starts new phase from zero, not saved legacy wall clock"),LegacyDistance>0.
  &&Source.Player->AnimationName==DungeonFairytaleSwordWalkV001::AnimationLabel
  &&FMath::IsNearlyEqual(double(Source.Player->AnimationTime),ExpectedWalkPhase(0.,LegacyDistance,P),FloatTolerance));
 if(!Source.Key(EKeys::D,false))return false;
 FDungeonRunSnapshot Saved;TArray<uint8> Bytes;FDungeonValidatedRun Decoded;
 if(!TestTrue(TEXT("New saved label and float phase survive actual full Run codec exactly"),Source.Game->CaptureRunSnapshot(Saved,Why)
  &&DungeonRunSnapshotCodec::Encode(Saved,Bytes,Why)&&DungeonRunSnapshotCodec::Decode(Bytes,Decoded,Why)&&Decoded.IsValid()
  &&Decoded.Get()->Fighters[0].AnimationName==DungeonFairytaleSwordWalkV001::AnimationLabel
  &&Decoded.Get()->Fighters[0].AnimationTime==Saved.Fighters[0].AnimationTime))return false;

 // The new target HUD starts with the presentation opt-in absent. No profile
 // mutation occurs. A restored versioned label still owns distance semantics.
 if(!TestTrue(TEXT("Actually remove initial Walk opt-in before constructing target world/HUD"),CommandLine.RemoveWalkOptIn()))return false;
 FCodecWorld Target(*this);if(!Target.Create())return false;FDungeonPreparedRun Prepared;
 if(!TestTrue(TEXT("Actual grouped prepare/install accepts the configured saved new label without presentation opt-in"),
  FDungeonRunInstaller::Prepare(*Target.Game,Decoded,Prepared,Why)&&FDungeonRunInstaller::Install(*Target.Game,Prepared,Why)))return false;
 Target.Player=Target.Game->PlayerFighter;const float SavedPhase=Saved.Fighters[0].AnimationTime;
 Target.Frame(.05f);FDungeonCompletedGroundMotion Placement;
 TestTrue(TEXT("Install pause preserves exact saved phase and endpoint, without a placement witness"),
  Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue
  &&Target.Player->AnimationName==DungeonFairytaleSwordWalkV001::AnimationLabel&&Target.Player->AnimationTime==SavedPhase
  &&Target.Player->GetGroundPosition()==Saved.Fighters[0].GroundPosition&&!Target.Player->QueryCompletedGroundMotion(Placement));
 Target.Frame(.005f);
 if(!Target.Key(EKeys::Enter,true))return false;Target.Frame(.005f);
 if(!TestTrue(TEXT("Fresh neutral real Enter opens gate without advancing the saved phase"),
  Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open&&Target.Player->AnimationTime==SavedPhase))return false;
 if(!Target.Key(EKeys::Enter,false)||!Target.Key(EKeys::D,true))return false;
 const auto ResumedFrom=Target.Player->GetGroundPosition();Target.Frame(.02f);
 const double ResumedDistance=(Target.Player->GetGroundPosition()-ResumedFrom).Size();
 TestTrue(TEXT("Restored new label continues actual distance phase even with Walk opt-in absent"),ResumedDistance>0.
  &&!FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordWalkPreview"))
  &&Target.Player->AnimationName==DungeonFairytaleSwordWalkV001::AnimationLabel
  &&FMath::IsNearlyEqual(double(Target.Player->AnimationTime),ExpectedWalkPhase(double(SavedPhase),ResumedDistance,P),FloatTolerance));
 if(!Target.Key(EKeys::D,false))return false;

 FDungeonRunSnapshot Before;if(!Target.Game->CaptureRunSnapshot(Before,Why))return false;
 const auto BeforeBytes=CodecSignature(Before);const auto C=WalkOwnerContext(Before);
 for(const FString InvalidLabel:{TEXT("walk_distance_v002"),TEXT("WALK_DISTANCE_V001")})
 {
  auto Bad=Before.Fighters[0];Bad.AnimationName=InvalidLabel;
  TestFalse(TEXT("Unknown version or wrong-case reserved distance label rejects direct Restore"),Target.Player->RestoreOwnerSnapshot(Bad,C,Why));
  FDungeonRunSnapshot After;
  TestTrue(TEXT("Rejected reserved label leaves full actual Run byte-signature unchanged"),
   Target.Game->CaptureRunSnapshot(After,Why)&&CodecSignature(After)==BeforeBytes);
 }
 return true;
}
#endif
