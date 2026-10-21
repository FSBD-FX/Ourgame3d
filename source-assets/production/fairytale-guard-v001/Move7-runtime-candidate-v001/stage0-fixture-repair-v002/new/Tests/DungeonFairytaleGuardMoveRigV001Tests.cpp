#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "StoneGuardOwnerFixture_v002.h"
#include "../DungeonFairytaleGuardMoveRigV001.h"
#include "../DungeonFairytaleGuardMoveDrawStateV001.h"
#include "../DungeonFairytaleGuardFullProfileV003.h"
#include "../DungeonFairytaleGuardProfile.h"
#include <cmath>
#include <limits>
namespace
{
namespace G=DungeonStoneGuard;
namespace M=DungeonFairytaleGuardMoveRigV001;
namespace F=DungeonFairytaleGuardFullV003;
G::FWorldInput MoveInput(int32 Side=1,double Y=0.)
{G::FWorldInput W;W.HasTarget=true;W.Target={Side*210.,Y,0.};W.CanStartAttack=false;W.Sweep=[](const G::FSweepRequest&){return G::FSweepResult{};};return W;}
bool BeginMove(G::FGuardKernel& K,const G::FWorldInput& W,double At=1.01)
{return K.BeginCombat()&&K.StepTo(0.,W).Accepted&&K.StepTo(1.,W).Accepted&&K.StepTo(At,W).Accepted&&F::SelectFull(K.State()).Clip==F::EClip::Move;}
double Path(const G::FState& S)
{double D=0.;for(const auto& E:S.Issued)if(E.Kind==G::EEventKind::Movement)D+=std::hypot(E.To.X-E.From.X,E.To.Y-E.From.Y);return D;}
const G::FEvent* CurrentMove(const G::FState& S)
{const G::FEvent* Last=nullptr;for(const auto& E:S.Issued)if(E.Kind==G::EEventKind::Movement&&E.AtTime==S.Time&&std::hypot(E.To.X-E.From.X,E.To.Y-E.From.Y)>0.)Last=&E;return Last;}
bool RealMove(GuardOwnerTests::FGuardWorld& W,int32 Side=1)
{
 if(!W.Create())return false;
 // Public native spawn and attack-permission control. No actor relocation,
 // forged FState, injected event, owner-map write, or manually advanced clock.
 W.Guard=W.Game->SpawnStoneGuard(W.Player->GetGroundPosition()+FVector2D(Side*210.,0.));
 if(!W.Guard||!W.Guard->GetStoneGuardDriver())return false;
 W.Guard->bAIEnabled=false; // Existing native Move stays active; only attacks are disabled.
 for(int32 N=0;N<400&&!W.Game->bGameOver;++N)
 {W.Frame(.01f);if(F::SelectFull(W.State()).Clip==F::EClip::Move&&CurrentMove(W.State()))return true;}
 W.Diagnostic(TEXT("Move7-native-fixture-no-current-movement"));return false;
}
// Independent expected value copied from the ACTUAL completed World producer.
// This helper isolates the plan test from the query-under-test; it never
// constructs/decorates FState or grants authorization to a synthetic Actor.
FDungeonGuardMoveSample Expected(const GuardOwnerTests::FGuardWorld& W)
{
 FDungeonGuardMoveSample R;const auto& S=W.State();const auto* E=CurrentMove(S);if(!E)return R;
 const auto& V=W.Game->GetEquipmentView();R.Valid=true;R.EntityId=S.EntityId;R.AcceptedPathOwnerId=S.EntityId;
 R.RunGuid=V.RunGuid;R.RoomInstanceId=V.RoomInstanceId;R.PresentationEpoch=W.Game->GetRunPresentationEpoch();
 R.EnemyContentId=W.Guard->EnemyContentId;R.SampleTime=S.Time;R.MovementAtTime=E->AtTime;R.MovementEventId=E->EventId;
 R.GroundPosition=W.Guard->GetGroundPosition();R.MovementFrom={E->From.X,E->From.Y};R.MovementTo={E->To.X,E->To.Y};
 R.CurrentAcceptedDistance=std::hypot(E->To.X-E->From.X,E->To.Y-E->From.Y);R.AcceptedDistance=Path(S);
 R.MovementDirection=(R.MovementTo-R.MovementFrom)/R.CurrentAcceptedDistance;R.Facing=S.Facing;R.NativeSelection=F::SelectFull(S);return R;
}
TArray<uint8> SampleSig(const FDungeonGuardMoveSample& S)
{
 GuardOwnerTests::FGuardSignature B;B.V(S.Valid,S.BlockKnown,S.EntityId,S.AcceptedPathOwnerId,S.RoomInstanceId,S.PresentationEpoch,
 S.MovementEventId,S.RunGuid.A,S.RunGuid.B,S.RunGuid.C,S.RunGuid.D,S.SampleTime,S.MovementAtTime,S.AcceptedDistance,S.CurrentAcceptedDistance,S.Facing);
 B.String(S.EnemyContentId);B.Point(S.GroundPosition);B.Point(S.MovementFrom);B.Point(S.MovementTo);B.Point(S.MovementDirection);
 const auto& N=S.NativeSelection;B.V(N.Valid,N.MaterialHit,N.TerminalPresentation,N.DeathAfterglow,N.Clip,N.Frame,N.Facing,N.EntityId,N.AttackId,N.SourceEventId,
 N.MaterialEventId,N.Phase,N.SampleTime,N.IntervalStart,N.IntervalEnd,N.AcceptedDistance,N.DistancePhase,N.DeathAge);return B.Bytes;
}
TArray<uint8> LegacySig()
{
 GuardOwnerTests::FGuardSignature B;
 for(const auto& R:F::ProfileFull())
 {B.V(R.Clip,R.AliasTarget,R.AliasFrame,R.NativeSourceId,R.PendingNativeCandidateId,R.StandingBasisFrame,R.StandingCrownY,R.StandingSoleY,
 R.CanvasWidth,R.CanvasHeight,R.StandingExtent,R.TargetBodyHeight,R.SourcePoseApproved,R.TrialAllowed,R.FinalAccepted,R.IndependentPoseOnly);
 B.String(R.TrialApprovalRecord);B.String(R.RegistrationEvidenceSHA256);B.String(R.SourceIndexSHA256);B.String(R.GapReason);B.V(R.Frames.Num());
 for(const auto& A:R.Frames){B.String(A.TexturePath);B.String(A.SourceSHA256);B.String(A.SourceRGBASHA256);B.Point(A.FloorPivot);B.V(A.PivotAuthority);}}
 return B.Bytes;
}
TArray<M::FResidentTexture> Residents(const M::FProfile& P)
{TArray<M::FResidentTexture> R;for(const auto& S:P.Sources){M::FResidentTexture T;T.Component=S.Component;T.TexturePath=S.TexturePath;
 T.SourceSHA256=S.SourceSHA256;T.SourceRGBASHA256=S.SourceRGBASHA256;T.ClassName=TEXT("Texture2D");T.Width=T.Height=512;T.ResourceReady=true;R.Add(T);}return R;}
const M::FPartPose* Part(const M::FRigSolution& R,M::EComponent C)
{return R.Parts.FindByPredicate([C](const auto& P){return P.Component==C;});}
FVector2D SubmittedPoint(const M::FPartPose& P,FVector2D Source)
{
 const auto& Q=P.Quad;const FVector2D Size(double(Q.Width),double(Q.Height));
 const FVector2D Pivot(double(Q.X)+Q.RotationPivotUV.X*Size.X,double(Q.Y)+Q.RotationPivotUV.Y*Size.Y);
 const FVector2D Relative(double(Q.X)+(Q.UL<0.?1.-Source.X/512.:Source.X/512.)*Size.X-Pivot.X,
 double(Q.Y)+Source.Y/512.*Size.Y-Pivot.Y);
 const double A=double(Q.RotationDegrees)*3.14159265358979323846/180.;
 return Pivot+FVector2D(Relative.X*std::cos(A)-Relative.Y*std::sin(A),Relative.X*std::sin(A)+Relative.Y*std::cos(A));
}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGuardMoveRigRealOwner,
 "CodexDungeon.Content.FairytaleGuardMoveRigV001.RealCompletedGuardOwnerAndAcceptedPath",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGuardMoveRigRealOwner::RunTest(const FString&)
{
 G::FGuardKernel K(95101);auto Input=MoveInput(1,45.);
 if(!TestTrue(TEXT("PRECONDITION real native Wake then positive current Idle Movement without attacks"),BeginMove(K,Input,1.2)
  &&K.State().Phase==G::EPhase::Idle&&CurrentMove(K.State())&&Path(K.State())==F::SelectFull(K.State()).AcceptedDistance))return false;
 GuardOwnerTests::FGuardWorld World(*this);
 if(!TestTrue(TEXT("PRECONDITION actual bound GameMode naturally issues completed Guard Move with AI attack permission disabled"),RealMove(World)))return false;
 const auto ExpectedMove=Expected(World);const auto NativeBefore=GuardOwnerTests::StateSig(World.State());const double Time=World.Game->GetSimulationTime();
 FDungeonGuardMoveSample Actual;
 if(!TestTrue(TEXT("TARGET Stage0 RED: real current Guard native Movement is exposed by read-only completed owner/run/room/time query"),World.Guard->QueryCompletedGuardMove(Actual)))return false;
 TestTrue(TEXT("Full actual producer sample agrees exactly including real path, direction, event, facing, Guard ID and unknown historical blocker"),SampleSig(Actual)==SampleSig(ExpectedMove)
  &&Actual.EntityId==World.Guard->GetRuntimeEntityId()&&Actual.EntityId!=World.Game->GetEquipmentView().OwnerId&&!Actual.BlockKnown
  &&Actual.SampleTime==Time&&Actual.NativeSelection.Clip==F::EClip::Move&&Actual.CurrentAcceptedDistance>0.);
 TestTrue(TEXT("Current actual binding is ENM-STN-003 in the same room and Run"),World.Game->GetWeaponWorldState().ActorBindings.ContainsByPredicate([&](const auto& B)
 {return B.EntityId==Actual.EntityId&&B.RoomInstanceId==Actual.RoomInstanceId&&B.ContentId==TEXT("ENM-STN-003");})&&Actual.RunGuid==World.Game->GetEquipmentView().RunGuid);
 for(int32 Read=0;Read<8;++Read){FDungeonGuardMoveSample Repeat;TestTrue(TEXT("Repeated current read does not reset/rephase movement"),World.Guard->QueryCompletedGuardMove(Repeat)&&SampleSig(Repeat)==SampleSig(Actual));}
 TestTrue(TEXT("Query leaves full native histories, HP and master time unchanged"),NativeBefore==GuardOwnerTests::StateSig(World.State())&&Time==World.Game->GetSimulationTime());
 auto RejectActor=[&](ADungeonFighter* A){auto Out=Actual;const auto Before=SampleSig(Out);return !A->QueryCompletedGuardMove(Out)&&Before==SampleSig(Out);};
 TestTrue(TEXT("Hero cannot masquerade as Guard and failure preserves every Out field"),RejectActor(World.Player));
 World.Game->bWaitingForStart=true;TestTrue(TEXT("Waiting-for-start rejects even an otherwise completed Move"),RejectActor(World.Guard));World.Game->bWaitingForStart=false;
 World.Game->bGameOver=true;TestTrue(TEXT("Game-over rejects even a still-published Move"),RejectActor(World.Guard));World.Game->bGameOver=false;
 const float Height=World.Guard->JumpHeight;World.Guard->JumpHeight=1.f;TestTrue(TEXT("Air projection rejects atomically"),RejectActor(World.Guard));World.Guard->JumpHeight=Height;
 const float Facing=World.Guard->Facing;World.Guard->Facing=-Facing;TestTrue(TEXT("Actor/native facing mismatch rejects atomically"),RejectActor(World.Guard));World.Guard->Facing=Facing;
 const auto Position=World.Guard->GetActorLocation();World.Guard->SetActorLocation(Position+FVector(1.,0.,0.));
 TestTrue(TEXT("Stale native body/root projection rejects without changing producer histories"),RejectActor(World.Guard)&&NativeBefore==GuardOwnerTests::StateSig(World.State()));World.Guard->SetActorLocation(Position);
 World.Guard->ApplyCombatHit(1.6f,World.Player,0.f);FDungeonGuardMoveSample MaterialMove;
 TestTrue(TEXT("Ordinary actual Damaged material tint does not invent a nonMove Hurt phase or suppress valid native Move"),World.State().Phase==G::EPhase::Idle
  &&F::SelectFull(World.State()).Clip==F::EClip::Move&&F::SelectFull(World.State()).MaterialHit&&World.Guard->QueryCompletedGuardMove(MaterialMove)&&MaterialMove.NativeSelection.MaterialHit);
 if(!K.StepTo(1.4,Input).Accepted)return false;
 TestTrue(TEXT("Native Y alignment followed by X accumulates issued XY hypot path rather than net displacement or elapsed speed"),Path(K.State())==F::SelectFull(K.State()).AcceptedDistance
  &&Path(K.State())>std::hypot(K.State().Position.X-K.State().InitialPosition.X,K.State().Position.Y-K.State().InitialPosition.Y));
 Input.Target={-210.,45.,0.};const double Prior=Path(K.State());if(!K.StepTo(1.41,Input).Accepted)return false;
 TestTrue(TEXT("Real reverse changes current facing and preserves cumulative path without a contact reset"),K.State().Facing==-1&&Path(K.State())>Prior&&F::SelectFull(K.State()).AcceptedDistance==Path(K.State()));
 G::FGuardKernel Partial(95102);auto Wall=MoveInput();Wall.Sweep=[](const G::FSweepRequest&){G::FSweepResult R;R.Fraction=.4;R.Stop=G::EStop::Wall;return R;};
 if(!TestTrue(TEXT("Real sweep partial result creates actual current native Movement"),BeginMove(Partial,Wall,1.05)))return false;
 TestTrue(TEXT("Partial collision uses accepted segment, never nominal speed distance"),Path(Partial.State())>0.&&Path(Partial.State())<160.*.05&&Path(Partial.State())==F::SelectFull(Partial.State()).AcceptedDistance);
 Wall.Sweep=[](const G::FSweepRequest&){G::FSweepResult R;R.Fraction=0.;R.Stop=G::EStop::Body;return R;};if(!Partial.StepTo(1.06,Wall).Accepted)return false;
 TestTrue(TEXT("Zero accepted blocked segment is Ready, not Move; path does not advance"),F::SelectFull(Partial.State()).Clip==F::EClip::Ready&&!CurrentMove(Partial.State()));
 // An actual install supplies stale external actor/run/time and a genuine pause.
 FDungeonRunSnapshot Saved;FDungeonValidatedRun Sealed;FString Why;
 if(!TestTrue(TEXT("Real moving Run captures and validates for a genuine pause gate"),World.Game->CaptureRunSnapshot(Saved,Why)&&FDungeonRunAggregate::Validate(Saved,Sealed,Why)))return false;
 GuardOwnerTests::FGuardWorld Target(*this);if(!TestTrue(TEXT("Actual independent target Run exists"),Target.Create()))return false;
 FDungeonPreparedRun Prepared;if(!TestTrue(TEXT("Real prepared Guard group installs in AwaitExplicitContinue"),FDungeonRunInstaller::Prepare(*Target.Game,Sealed,Prepared,Why)&&FDungeonRunInstaller::Install(*Target.Game,Prepared,Why)
  &&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue))return false;
 for(auto Enemy:Target.Game->Enemies)if(Enemy&&Enemy->GetRuntimeEntityId()==Actual.EntityId)Target.Guard=Enemy;
 if(!TestTrue(TEXT("Installed actual Guard actor is present"),Target.Guard&&Target.Guard->GetStoneGuardDriver()))return false;
 TestTrue(TEXT("Genuine AwaitExplicitContinue rejects Move and leaves Out unchanged"),RejectActor(Target.Guard));
 World.Guard->bAIEnabled=true;
 for(int32 N=0;N<400&&!World.State().Action.InProgress&&!World.Game->bGameOver;++N)World.Frame(.01f);
 TestTrue(TEXT("Real native attack occupies its original phase and excludes Move"),World.State().Action.InProgress&&RejectActor(World.Guard));
 World.Guard->ApplyCombatHit(1.6f,World.Player,85.f);
 TestTrue(TEXT("Actual native poise break excludes Hurt/Stunned Move"),World.State().Phase==G::EPhase::Stunned&&RejectActor(World.Guard));
 World.Guard->ApplyCombatHit(100000.f,World.Player,0.f);
 TestTrue(TEXT("Actual native lethal damage excludes terminal/dead Move"),World.State().Phase==G::EPhase::Dead&&RejectActor(World.Guard));
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGuardMoveRigGeometry,
 "CodexDungeon.Content.FairytaleGuardMoveRigV001.FixedSurfaceRigSingleMirrorAndFiniteBounds",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGuardMoveRigGeometry::RunTest(const FString&)
{
 G::FGuardKernel Native(95103);const auto W=MoveInput();if(!TestTrue(TEXT("PRECONDITION solver distance is from real kernel positive current Movement"),BeginMove(Native,W)))return false;
 const auto& P=M::Profile();int32 Markers=0;for(const auto& S:P.Sources)Markers+=S.Markers.Num();
 if(!TestTrue(TEXT("TARGET Stage0 RED: separately typed Move7 profile owns exactly seven fixed252/250/251 sources and eighteen opaque surface points"),P.Sources.Num()==7&&Markers==18&&P.LayerOrder.Num()==7))return false;
 const TCHAR* ExpectedPNG[]={TEXT("402d6da9d41e88079b82d6fc5978badb8e19f86e1aac3d04d5320800220d4e2c"),TEXT("40d167afa7e61a64da7a7dacba3b2110cd28c384d3459ec1e81480cee049b460"),TEXT("ad4b460374b9ac313f18be190845dab32ad0ece101c88b0b35dab73b050feeff"),TEXT("bd6e8e5488891d62e7c6756eff9721152c3f99790b131f354496ca81010105a0"),TEXT("5e2768723ba949b3f04bb07def025e008afe0161a8d149545a705d73c67e3ff4"),TEXT("1dd04abe980ddc3018c15769105ea5f0513ac6336d61c4045f050f5e8e346dbc"),TEXT("62eedb18f9de49bfdedf60205644da4e2c0d770a7aa943103315bb39de9ca5a9")};
 const TCHAR* ExpectedRGBA[]={TEXT("bac74c59c75cab64c8d36744d2e2ad513a270f208fd159dab01d87ff1ce71fb1"),TEXT("32b1d0fac2fad4e97cd01289b172e43d183300c5de2124255feb5c6bd460f0c3"),TEXT("71c60a24f58fa28ec4746edc923163108f7d3346c6af3e3034ae762398b10351"),TEXT("42cefad645d17f84cd0ef0b1fb1797fe50b9d08a471e3ef5b2dbee5eccb4e370"),TEXT("7f71a1afe85db6ca5b6ef9ce9b1b653bc19b6d0ceb3f79c6f21a08198310674a"),TEXT("b302ef32885c941d760ac10601ca584a91dc4a4f78c72f6b95856392fe687005"),TEXT("16eb8d091f9cb0d0100717c4a4f444f05380954b8f8db33d0e3fb63537f2011f")};
 const TCHAR* ExpectedPaths[]={TEXT("/Game/Production/ArtTrials/EV048/v019/GuardMoveRig/T_GuardMoveRig_BodyRest_v001.T_GuardMoveRig_BodyRest_v001"),TEXT("/Game/Production/ArtTrials/EV048/v019/GuardMoveRig/T_GuardMoveRig_NearThigh_v001.T_GuardMoveRig_NearThigh_v001"),TEXT("/Game/Production/ArtTrials/EV048/v019/GuardMoveRig/T_GuardMoveRig_NearShin_v001.T_GuardMoveRig_NearShin_v001"),TEXT("/Game/Production/ArtTrials/EV048/v019/GuardMoveRig/T_GuardMoveRig_NearFoot_v001.T_GuardMoveRig_NearFoot_v001"),TEXT("/Game/Production/ArtTrials/EV048/v019/GuardMoveRig/T_GuardMoveRig_FarThigh_v001.T_GuardMoveRig_FarThigh_v001"),TEXT("/Game/Production/ArtTrials/EV048/v019/GuardMoveRig/T_GuardMoveRig_FarShin_v001.T_GuardMoveRig_FarShin_v001"),TEXT("/Game/Production/ArtTrials/EV048/v019/GuardMoveRig/T_GuardMoveRig_FarFoot_v001.T_GuardMoveRig_FarFoot_v001")};
 const TCHAR* ExpectedMarkerNames[]={TEXT("root"),TEXT("crown"),TEXT("near_hip_socket"),TEXT("far_hip_socket"),TEXT("hip"),TEXT("knee"),TEXT("knee"),TEXT("ankle"),TEXT("ankle"),TEXT("heel"),TEXT("toe"),TEXT("hip"),TEXT("knee"),TEXT("knee"),TEXT("ankle"),TEXT("ankle"),TEXT("heel"),TEXT("toe")};
 const FVector2D ExpectedPoints[]={FVector2D(250,403),FVector2D(254,137),FVector2D(224,404),FVector2D(277,400),FVector2D(280,126),FVector2D(214,389),FVector2D(268,184),FVector2D(260,400),FVector2D(216,294),FVector2D(108,445),FVector2D(420,445),FVector2D(263,124),FVector2D(228,389),FVector2D(237,193),FVector2D(267,407),FVector2D(220,258),FVector2D(105,430),FVector2D(418,442)};
 const FColor ExpectedColors[]={FColor(255,227,144,255),FColor(248,234,166,255),FColor(144,134,109,255),FColor(227,188,126,255),FColor(253,244,172,255),FColor(158,143,119,255),FColor(218,189,136,255),FColor(227,194,132,255),FColor(254,242,170,255),FColor(1,0,2,255),FColor(1,0,0,255),FColor(230,204,144,255),FColor(177,155,119,255),FColor(162,146,119,255),FColor(176,156,120,255),FColor(217,189,133,255),FColor(13,11,18,255),FColor(8,9,11,255)};
 int32 MarkerIndex=0;for(int32 Index=0;Index<7;++Index)
 {const auto& S=P.Sources[Index];TestTrue(TEXT("Every exact component identity, path and original PNG/RGBA hash remains frozen"),S.Component==M::EComponent(Index)&&S.TexturePath==ExpectedPaths[Index]&&S.SourceSHA256==ExpectedPNG[Index]&&S.SourceRGBASHA256==ExpectedRGBA[Index]);
 for(const auto& A:S.Markers){TestTrue(TEXT("Every artist18 source name, opaque RGBA and exact surface coordinate remains frozen"),A.Name==ExpectedMarkerNames[MarkerIndex]&&A.Point==ExpectedPoints[MarkerIndex]&&A.SurfaceRGBA==ExpectedColors[MarkerIndex]);++MarkerIndex;}}
 TestTrue(TEXT("Frozen profile pins retain fixed scale, own-hip C128 trajectory and no formal art acceptance"),P.ProfileId==TEXT("GuardMoveRig252_250_251_AuthorOwnHipC128_v001")
  &&P.ProfileSHA256==TEXT("03156e971171f597ca504e9c0176d5a2fdf3c31c09b3eddae2995e2245193b51")&&P.SourceSnapshotSHA256==TEXT("a16a6a151ca0f6895c80ce108221bb3bed8f9c267c8016d142c18ed74f84cd94")
  &&P.CanvasSize==512&&P.StandingExtent==449.&&P.TargetBodyHeight==100.8&&P.CycleWorld==128.&&P.HalfCycleWorld==64.
  &&P.FootHalfStance==20.8&&P.SwingLift==2.&&P.BodyBob==4.&&P.NearBranch==-1&&P.FarBranch==1&&!P.FinalAccepted);
 for(const auto& S:P.Sources){TestTrue(TEXT("All seven immutable surfaces have exact512 source pins and no bone claims"),S.SourceSHA256.Len()==64&&S.SourceRGBASHA256.Len()==64&&S.ComponentToRestScale==(S.Component==M::EComponent::BodyRest?1.:.36)
  &&S.NativeBatchId==(S.Component==M::EComponent::BodyRest?252:(int32(S.Component)<=int32(M::EComponent::NearFoot)?250:251)));
  for(const auto& A:S.Markers)TestTrue(TEXT("All artist18 registrations are opaque in the original image"),A.SurfaceRGBA.A==255&&A.Point.X>=0.&&A.Point.X<512.&&A.Point.Y>=0.&&A.Point.Y<512.);}
 for(const double Distance:{0.,32.,64.,96.,128.,Path(Native.State())})
 {
  M::FSolveInput I;I.EntityId=I.AcceptedPathOwnerId=Native.State().EntityId;I.AcceptedDistance=Distance;I.Facing=1;I.Context.GroundScreen={640.125,420.875};I.Context.UIScale=1.25;
  M::FRigSolution Right,Left;FString Why;if(!TestTrue(TEXT("Fixed reachable own-hip trajectory solves exactly seven ordered parts"),M::Solve(I,P,Right,Why)&&Right.Valid&&Right.Parts.Num()==7))return false;
  I.Facing=-1;if(!TestTrue(TEXT("Same path solves one reflected rig without swapping Near/Far"),M::Solve(I,P,Left,Why)&&Left.Valid&&Left.Parts.Num()==7))return false;
  const double Cycle=std::fmod(Distance,128.),Bob=4.*std::pow(std::sin(2.*3.14159265358979323846*Distance/128.),2.);
  TestTrue(TEXT("Native accepted distance alone drives C128/body4sin2; current Facing is independent"),FMath::IsNearlyEqual(Right.CyclePosition,Cycle,1.e-12)&&FMath::IsNearlyEqual(Right.BodyRise,Bob,1.e-12)&&Right.Facing==1&&Left.Facing==-1);
  for(int32 Index=0;Index<7;++Index)
  {
   const auto& R=Right.Parts[Index];const auto& L=Left.Parts[Index];const auto& Q=R.Quad;
   TestTrue(TEXT("Actual float DrawTexture arguments remain positive finite at fixed size; pivot remains native double FVector2D"),R.Component==P.LayerOrder[Index]&&L.Component==R.Component
    &&std::isfinite(Q.X)&&std::isfinite(Q.Y)&&std::isfinite(Q.Width)&&std::isfinite(Q.Height)&&std::isfinite(Q.RotationDegrees)&&Q.Width>0.f&&Q.Height==Q.Width
    &&Q.Width==float(512.*(100.8/449.*R.ComponentToRestScale*I.Context.UIScale))&&Q.U==0.f&&Q.UL==1.f&&L.Quad.U==1.f&&L.Quad.UL==-1.f
    &&L.Quad.RotationDegrees==-Q.RotationDegrees&&L.Quad.RotationPivotUV.X==1.-Q.RotationPivotUV.X&&L.Quad.RotationPivotUV.Y==Q.RotationPivotUV.Y);
   for(const FVector2D Source:{FVector2D(0.,0.),FVector2D(512.,0.),FVector2D(512.,512.),FVector2D(0.,512.)})
   {const auto A=SubmittedPoint(R,Source),B=SubmittedPoint(L,Source);TestTrue(TEXT("One whole-rig X reflection including source corners; no doubled affine plus UV reflection"),FMath::IsNearlyEqual(A.X+B.X,2.*I.Context.GroundScreen.X,.001)&&FMath::IsNearlyEqual(A.Y,B.Y,.001));}
  }
  for(const bool Near:{false,true})
  {
   const auto* Thigh=Part(Right,Near?M::EComponent::NearThigh:M::EComponent::FarThigh);const auto* Shin=Part(Right,Near?M::EComponent::NearShin:M::EComponent::FarShin);const auto* Foot=Part(Right,Near?M::EComponent::NearFoot:M::EComponent::FarFoot);
   if(!TestTrue(TEXT("Every complete leg has three exclusive component owners"),Thigh&&Shin&&Foot))return false;
   const FVector2D Hip=Near?FVector2D(280,126):FVector2D(263,124),KneeT=Near?FVector2D(214,389):FVector2D(228,389),KneeS=Near?FVector2D(268,184):FVector2D(237,193),AnkleS=Near?FVector2D(260,400):FVector2D(267,407),AnkleF=Near?FVector2D(216,294):FVector2D(220,258);
   const auto H=SubmittedPoint(*Thigh,Hip),KT=SubmittedPoint(*Thigh,KneeT),KS=SubmittedPoint(*Shin,KneeS),AS=SubmittedPoint(*Shin,AnkleS),AF=SubmittedPoint(*Foot,AnkleF);
   TestTrue(TEXT("Fixed-length component similarities register cap/knee/ankle surfaces without stretch or hidden perpose normalization"),(KT-KS).Size()<.001&&(AS-AF).Size()<.001
    &&FMath::IsNearlyEqual((KT-H).Size(),(KneeT-Hip).Size()*.36*100.8/449.*I.Context.UIScale,.001)&&FMath::IsNearlyEqual((AS-KS).Size(),(AnkleS-KneeS).Size()*.36*100.8/449.*I.Context.UIScale,.001));
   const auto Heel=SubmittedPoint(*Foot,Near?FVector2D(108,445):FVector2D(105,430)),Toe=SubmittedPoint(*Foot,Near?FVector2D(420,445):FVector2D(418,442));
   const auto V=AS-H,ToKnee=KT-H;const double Branch=V.X*ToKnee.Y-V.Y*ToKnee.X;
   TestTrue(TEXT("Frozen Near-1/Far+1 knee branch remains distinct"),Near?Branch<0.:Branch>0.);
   const bool Stance=(Cycle<64.)==Near;const double U=(Cycle-(Cycle<64.?0.:64.))/64.;
   const double X=Stance?20.8-41.6*U:-20.8+41.6*U,Lift=Stance?0.:2.*std::pow(std::sin(3.14159265358979323846*U),2.);
   const double OwnHipX=I.Context.GroundScreen.X+((Near?224.:277.)-250.)*100.8/449.*I.Context.UIScale;
   // Opaque Heel/Toe author points sit ABOVE the alpha>=128 core sole.
   // The independent retained source oracle fixes these two offsets; they
   // must never be normalized to ground by changing the profile or markers.
   const double MarkerAboveCore=Near?54.36-60.84:63.46059870632066-72.69764651497574;
   const double ExpectedMarkerY=I.Context.GroundScreen.Y-Lift*I.Context.UIScale+MarkerAboveCore*100.8/449.*I.Context.UIScale;
   TestTrue(TEXT("Frozen own-hip stance/swing and original heel/toe angle preserve original opaque-marker-to-core-sole offsets"),FMath::Abs(Toe.Y-Heel.Y)<.001
    &&FMath::IsNearlyEqual((Heel.X+Toe.X)*.5,OwnHipX+X*I.Context.UIScale,.001)&&FMath::IsNearlyEqual(FMath::Max(Heel.Y,Toe.Y),ExpectedMarkerY,.001));
  }
 }
 M::FSolveInput I;I.EntityId=I.AcceptedPathOwnerId=Native.State().EntityId;I.AcceptedDistance=Path(Native.State());I.Facing=1;I.Context.GroundScreen={640.,420.};
 for(int32 Which=0;Which<8;++Which)
 {auto Bad=I;auto BadProfile=P;if(Which==0)Bad.AcceptedDistance=std::numeric_limits<double>::quiet_NaN();if(Which==1)Bad.AcceptedDistance=-1.;if(Which==2)Bad.AcceptedPathOwnerId++;
 if(Which==3)Bad.Facing=0;if(Which==4)Bad.Context.UIScale=1.e-300;if(Which==5)Bad.Context.GroundScreen.X=std::numeric_limits<double>::infinity();if(Which==6)BadProfile.Sources[1].ComponentToRestScale=.361;if(Which==7)BadProfile.Sources[1].Markers[0].Point.X+=1.;
 M::FRigSolution Out;Out.BodyRise=987.;FString Why;TestTrue(TEXT("Invalid domain/underflow/profile marker or scale change rejects atomically"),!M::Solve(Bad,BadProfile,Out,Why)&&!Why.IsEmpty()&&!Out.Valid&&Out.BodyRise==987.);}
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGuardMoveRigAtomic,
 "CodexDungeon.Content.FairytaleGuardMoveRigV001.AtomicSevenResourcesAndLegacyIsolation",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGuardMoveRigAtomic::RunTest(const FString&)
{
 GuardOwnerTests::FGuardWorld World(*this);if(!TestTrue(TEXT("PRECONDITION actual completed Guard Move for atomic plan"),RealMove(World)))return false;
 const auto Sample=Expected(World);const auto& P=M::Profile();const auto Before=GuardOwnerTests::StateSig(World.State()),Old=LegacySig();
 const auto& OldMove=*F::FindRowFull(F::EClip::Move);const auto Legacy=DungeonFairytaleGuard::Plan(DungeonFairytaleGuard::Select(World.State()));
 if(!TestTrue(TEXT("PRECONDITION old full known44/13rows/57logical and rejected Move/native221 remain closed"),F::AvailableUniqueBindingsFull()==44&&F::ProfileFull().Num()==13&&F::LogicalFrameBudget()==57
  &&OldMove.Frames.IsEmpty()&&!OldMove.SourcePoseApproved&&!OldMove.TrialAllowed&&!F::PlanFull(Sample.NativeSelection).Valid&&!Legacy.Valid))return false;
 M::FDrawContext C;C.GroundScreen={640.125,420.875};C.UIScale=1.25;auto Ready=Residents(P);M::FDrawPlan Plan;FString Why;
 if(!TestTrue(TEXT("TARGET Stage0 RED: seven exact resident512 Texture2D resources authorize one complete isolated Move7 plan before any draw"),M::PlanFromSample(Sample,P,Ready,C,Plan,Why)&&Plan.Valid&&Plan.Rig.Parts.Num()==7))return false;
 TestTrue(TEXT("Atomic plan preserves actual sample and excludes a duplicate fixed axe"),SampleSig(Plan.Sample)==SampleSig(Sample)&&Plan.RequiredResources==7&&Plan.WholebodyIncludesAxe&&Plan.IndependentAxeLayers==0);
 for(int32 Missing=0;Missing<7;++Missing)for(int32 Fault=0;Fault<7;++Fault)
 {auto Resources=Ready;if(Fault==0)Resources.RemoveAt(Missing);else if(Fault==1)Resources[Missing].ResourceReady=false;else if(Fault==2)Resources[Missing].PendingInitialization=true;
 else if(Fault==3)Resources[Missing].Width=511;else if(Fault==4)Resources[Missing].ClassName=TEXT("TextureRenderTarget2D");else if(Fault==5)Resources[Missing].SourceSHA256=TEXT("bad");else Resources[Missing].SourceRGBASHA256=TEXT("bad");
 M::FDrawPlan Out;Out.RequiredResources=987;FString Failure;TestTrue(TEXT("Any single source missing/unready/pending/wrongclass/wrongsize/wrongPNG/wrongRGBA rejects all parts before submission and preserves Out"),
 !M::PlanFromSample(Sample,P,Resources,C,Out,Failure)&&!Failure.IsEmpty()&&!Out.Valid&&Out.Rig.Parts.IsEmpty()&&Out.RequiredResources==987);}
 {auto Extra=Ready;Extra.Add(Ready[0]);M::FDrawPlan Out;FString Failure;TestTrue(TEXT("Duplicate or extra resource ownership cannot pass exact7 gate"),!M::PlanFromSample(Sample,P,Extra,C,Out,Failure));}
 for(int32 Fault=0;Fault<8;++Fault)
 {auto Bad=Sample;if(Fault==0)Bad.Valid=false;if(Fault==1)Bad.AcceptedPathOwnerId++;if(Fault==2)Bad.MovementAtTime=std::nextafter(Bad.SampleTime,0.);if(Fault==3)Bad.CurrentAcceptedDistance=0.;if(Fault==4)Bad.NativeSelection.Clip=F::EClip::Ready;
 if(Fault==5)Bad.NativeSelection.SampleTime=std::nextafter(Bad.SampleTime,0.);if(Fault==6)Bad.BlockKnown=true;if(Fault==7)Bad.RunGuid.Invalidate();
 M::FDrawPlan Out;FString Failure;TestTrue(TEXT("Stale/foreign/nonMove/zero-progress or invented blocker sample rejects complete plan"),!M::PlanFromSample(Bad,P,Ready,C,Out,Failure)&&Out.Rig.Parts.IsEmpty());}
 TestTrue(TEXT("Plan/profile queries preserve full original producer and all legacy row fields"),Before==GuardOwnerTests::StateSig(World.State())&&Old==LegacySig()
  &&F::AvailableUniqueBindingsFull()==44&&OldMove.NativeSourceId==0&&OldMove.PendingNativeCandidateId==0&&OldMove.Frames.IsEmpty()&&!F::PlanFull(Sample.NativeSelection).Valid);
 TestTrue(TEXT("Readback starts with zero submitted components until renderer actually executes DrawTexture"),World.HUD->GetFairytaleGuardMoveRigDraws().IsEmpty());
 return true;
}
#endif
