#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Math/RotationMatrix.h"
#include "Math/TranslationMatrix.h"
#include "../DungeonStoneGuard.h"
#include "../DungeonFairytaleGuardMoveRigV001.h"
#include <cmath>

namespace
{
namespace G=DungeonStoneGuard;
namespace M=DungeonFairytaleGuardMoveRigV001;
namespace F=DungeonFairytaleGuardFullV003;

double AcceptedPath(const G::FState& State)
{
 double Distance=0.;
 for(const auto& Event:State.Issued)
  if(Event.Kind==G::EEventKind::Movement)
   Distance+=std::hypot(Event.To.X-Event.From.X,Event.To.Y-Event.From.Y);
 return Distance;
}

bool HasCurrentAcceptedMovement(const G::FState& State)
{
 for(const auto& Event:State.Issued)
  if(Event.Kind==G::EEventKind::Movement&&Event.AtTime==State.Time
   &&std::hypot(Event.To.X-Event.From.X,Event.To.Y-Event.From.Y)>0.)return true;
 return false;
}

const M::FPartPose* FindPart(const M::FRigSolution& Rig,M::EComponent Component)
{return Rig.Parts.FindByPredicate([Component](const auto& Part){return Part.Component==Component;});}

bool UsableSubmittedQuad(const M::FSubmittedQuad& Q)
{
 return std::isfinite(Q.X)&&std::isfinite(Q.Y)&&std::isfinite(Q.Width)&&std::isfinite(Q.Height)
  &&std::isfinite(Q.RotationDegrees)&&std::isfinite(Q.RotationPivotUV.X)&&std::isfinite(Q.RotationPivotUV.Y)
  &&Q.Width>0.f&&Q.Height>0.f&&Q.DrawScale==1.f&&!Q.ScalePosition
  &&(Q.U==0.f||Q.U==1.f)&&Q.V==0.f&&(Q.UL==1.f||Q.UL==-1.f)&&Q.VL==1.f;
}

// Independent reconstruction from the actual submitted DrawTexture arguments.
// UE5.5.4 HUD.cpp:976-978 creates a positive-size FCanvasTileItem; its
// CanvasItem.cpp:423-432 rotates about Position+Size*PivotPoint, and :447-470
// rounds the four unrotated vertex coordinates to float. Preserve those CPU
// vertex rounds here. This is an API-boundary oracle, not a GPU pixel receipt.
FVector2D SubmittedSurfacePoint(const M::FSubmittedQuad& Q,FVector2D Source)
{
 const FVector2D Position(double(Q.X),double(Q.Y));
 const FVector2D Size(double(Q.Width),double(Q.Height));
 const float Left=float(Position.X),Top=float(Position.Y);
 const float Right=float(Position.X+Size.X),Bottom=float(Position.Y+Size.Y);
 const double U=(Source.X/512.-double(Q.U))/double(Q.UL);
 const double V=(Source.Y/512.-double(Q.V))/double(Q.VL);
 const FVector4 Vertex(double(Left)+U*(double(Right)-double(Left)),
  double(Top)+V*(double(Bottom)-double(Top)),0.,1.);
 const FVector Anchor(Size.X*Q.RotationPivotUV.X,Size.Y*Q.RotationPivotUV.Y,0.);
 const FVector ScreenPosition(Position.X,Position.Y,0.);
 const FMatrix Transform=FTranslationMatrix(-ScreenPosition)*FTranslationMatrix(-Anchor)
  *FRotationMatrix(FRotator(0.,double(Q.RotationDegrees),0.))
  *FTranslationMatrix(Anchor)*FTranslationMatrix(ScreenPosition);
 const FVector4 Point=Transform.TransformFVector4(Vertex);
 return {Point.X,Point.Y};
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGuardMoveRigBodyHipRoot,
 "CodexDungeon.Content.FairytaleGuardMoveRigV001.BodyHipAttachmentAndActualSourceRoot",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGuardMoveRigBodyHipRoot::RunTest(const FString&)
{
 // Catches a translated body, an incorrect source-ground/root basis, and legs
 // that solve internally while detached from the body. Expectations below use
 // frozen source pixels and equations, never solver anchors or BodyRise fields.
 const auto& Profile=M::Profile();bool ProfileChecked=false;M::FSolveInput LastInput;
 for(const int32 Facing:{1,-1})
 {
  G::FGuardKernel Native(Facing==1?95104:95105,0.,{},Facing);
  G::FWorldInput World;World.HasTarget=true;World.Target={Facing*450.,0.,0.};World.CanStartAttack=false;
  World.Sweep=[](const G::FSweepRequest&){return G::FSweepResult{};};
  if(!TestTrue(TEXT("PRECONDITION native explicit combat and cleared-enemy wake enters its real one-second warning"),
   Native.BeginCombat()&&Native.NotifyOtherAcceptedEnemiesCleared()&&Native.StepTo(0.,World).Accepted
   &&Native.State().Phase==G::EPhase::Waking&&Native.State().WakeEnd==1.))return false;
  if(!ProfileChecked)
  {
   if(!TestTrue(TEXT("TARGET Stage0 RED: fixed seven-source Move7 solver must expose the actual body/root and both hip attachments"),
    Profile.Sources.Num()==7))return false;
   ProfileChecked=true;
  }
  for(const double RequestedDistance:{2.,24.,32.,48.,64.,72.,96.,120.,128.,134.})
  {
   // StepTo is only the native test producer. Solver distance comes exclusively
   // from the positive collision-accepted Movement facts issued by this owner.
   if(!TestTrue(TEXT("PRECONDITION native wake completion followed by actual current positive X movement"),
    Native.StepTo(1.+RequestedDistance/160.,World).Accepted&&Native.State().Phase==G::EPhase::Idle
    &&HasCurrentAcceptedMovement(Native.State())&&Native.State().Facing==Facing))return false;
   const double Distance=AcceptedPath(Native.State());const auto Selection=F::SelectFull(Native.State());
   if(!TestTrue(TEXT("PRECONDITION actual issued cumulative path agrees with native Move selection and reaches the requested sample"),
    Selection.Valid&&Selection.Clip==F::EClip::Move&&Selection.AcceptedDistance==Distance
    &&FMath::IsNearlyEqual(Distance,RequestedDistance,1.e-10)))return false;
   const double Cycle=std::fmod(Distance,128.);
   const double Bob=4.*std::pow(std::sin(2.*3.14159265358979323846*Cycle/128.),2.);
   for(const double UI:{1.,1.25})
   {
    M::FSolveInput Input;Input.EntityId=Input.AcceptedPathOwnerId=Native.State().EntityId;
    Input.AcceptedDistance=Distance;Input.Facing=Native.State().Facing;
    Input.Context.GroundScreen={640.125,420.875};Input.Context.UIScale=UI;LastInput=Input;
    M::FRigSolution Rig;FString Diagnostic;
    if(!TestTrue(TEXT("Real accepted owner path solves all seven components for both actual native facings and viewport scales"),
     M::Solve(Input,Profile,Rig,Diagnostic)&&Rig.Valid&&Rig.Parts.Num()==7))return false;
    const auto* Body=FindPart(Rig,M::EComponent::BodyRest);
    const auto* NearThigh=FindPart(Rig,M::EComponent::NearThigh);
    const auto* FarThigh=FindPart(Rig,M::EComponent::FarThigh);
    if(!TestTrue(TEXT("Body and both thigh source quads exist and expose finite usable DrawTexture arguments"),
     Body&&NearThigh&&FarThigh&&UsableSubmittedQuad(Body->Quad)
     &&UsableSubmittedQuad(NearThigh->Quad)&&UsableSubmittedQuad(FarThigh->Quad)))return false;
    const double SourceScale=100.8/449.;const auto Ground=Input.Context.GroundScreen;
    const auto Root=SubmittedSurfacePoint(Body->Quad,{250.,403.});
    const FVector2D ExpectedRoot(Ground.X,Ground.Y+((403.-580.)*SourceScale-Bob)*UI);
    TestTrue(TEXT("Actual submitted BodyRest root250/403 uses fixed source-ground250/580 and visible body bob"),
     (Root-ExpectedRoot).Size()<.001);
    const auto BodyNearHip=SubmittedSurfacePoint(Body->Quad,{224.,404.});
    const auto BodyFarHip=SubmittedSurfacePoint(Body->Quad,{277.,400.});
    const auto NearCap=SubmittedSurfacePoint(NearThigh->Quad,{280.,126.});
    const auto FarCap=SubmittedSurfacePoint(FarThigh->Quad,{263.,124.});
    TestTrue(TEXT("Actual Near thigh hip280/126 attaches to submitted BodyRest hip224/404"),
     (NearCap-BodyNearHip).Size()<.001);
    TestTrue(TEXT("Actual Far thigh hip263/124 attaches to submitted BodyRest hip277/400 without identity swap on reflection"),
     (FarCap-BodyFarHip).Size()<.001);
    const FVector2D ExpectedNearHip(Ground.X+Facing*(224.-250.)*SourceScale*UI,
     Ground.Y+((404.-580.)*SourceScale-Bob)*UI);
    const FVector2D ExpectedFarHip(Ground.X+Facing*(277.-250.)*SourceScale*UI,
     Ground.Y+((400.-580.)*SourceScale-Bob)*UI);
    TestTrue(TEXT("Both actual body hip points share the one fixed body transform and exactly one screen-X reflection"),
     (BodyNearHip-ExpectedNearHip).Size()<.001&&(BodyFarHip-ExpectedFarHip).Size()<.001);
    // Row131 is the frozen alpha-core crown basis, not an added surface marker.
    // The original opaque authored crown marker remains254/137 and is lower.
    const auto CoreCrownBasis=SubmittedSurfacePoint(Body->Quad,{250.,131.});
    const auto OriginalCrownMarker=SubmittedSurfacePoint(Body->Quad,{254.,137.});
    const FVector2D ExpectedCrownBasis(Ground.X,Ground.Y-(100.8+Bob)*UI);
    const FVector2D ExpectedCrownMarker(Ground.X+Facing*4.*SourceScale*UI,
     Ground.Y+((137.-580.)*SourceScale-Bob)*UI);
    TestTrue(TEXT("Actual submitted core crown basis131 preserves standing100.8 plus bob; opaque marker137 is not normalized into the standing basis"),
     (CoreCrownBasis-ExpectedCrownBasis).Size()<.001&&(OriginalCrownMarker-ExpectedCrownMarker).Size()<.001
     &&FMath::IsNearlyEqual(OriginalCrownMarker.Y-CoreCrownBasis.Y,6.*SourceScale*UI,.001));
   }
  }
 }
 // The frozen host accepts this finite coordinate, but UE5.5.4 CanvasItem.cpp
 // rounds (Position+Size) to float, making all four actual vertices identical.
 // The production backend-domain gate must be stricter than that host limit.
 auto Collapsed=LastInput;Collapsed.Context.GroundScreen={1.e20,1.e20};
 M::FRigSolution Out;Out.BodyRise=987.;Out.CyclePosition=654.;Out.Facing=73;Out.ProfileId=TEXT("sentinel-unmodified");
 FString Failure;
 TestTrue(TEXT("Finite huge screen ground whose actual float Right/Bottom collapse onto Left/Top rejects atomically and preserves caller Out"),
  !M::Solve(Collapsed,Profile,Out,Failure)&&!Failure.IsEmpty()&&!Out.Valid&&Out.Parts.IsEmpty()
  &&Out.BodyRise==987.&&Out.CyclePosition==654.&&Out.Facing==73&&Out.ProfileId==TEXT("sentinel-unmodified"));
 return true;
}
#endif
