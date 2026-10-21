#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "../DungeonFairytaleSwordDodgePlan.h"
#include "../DungeonRunInstaller.h"
#include "../DungeonRunSnapshotCodec.h"
#include "RunCodecFixture_v001.h"
#include <cmath>

namespace
{
namespace D=DungeonFairytaleSwordDodgeV001;
namespace B=DungeonFairytaleSwordEquipmentBinding;
struct FDodgeOptInScope
{
 const FString Original=FCommandLine::Get();
 FDodgeOptInScope(){FString Next=Original;for(const TCHAR* Flag:{B::CommandLineFlag,D::CommandLineFlag})if(!FParse::Param(*Next,Flag))Next+=FString(TEXT(" -"))+Flag;FCommandLine::Set(*Next);}
 ~FDodgeOptInScope(){FCommandLine::Set(*Original);}
};
bool Equip(FCodecWorld& W,const TCHAR* Id,const TCHAR* Key)
{
 IV::FItem Item;Item.ContentId=TCHAR_TO_UTF8(Id);
 const auto R=W.Game->RegisterEquipmentSource(Key,Item,W.Player->GetGroundPosition()+FVector2D(24,0),true);
 if(!W.Test.TestTrue(TEXT("PRECONDITION real legal armor pickup source and transaction"),R.Ok()&&W.Game->SelectEquipmentSource(R.SourceId)&&W.Game->TryInteractEquipment()))return false;
 const auto A=W.Game->GetEquipmentView().Action;
 return W.Test.TestTrue(TEXT("PRECONDITION actual existing armor .5s deadline commits without modifying gear mirrors"),A.Active&&A.InstanceId==R.InstanceId&&W.AdvanceTo(A.Deadline)&&W.Player->ArmorId==Id&&!W.Game->GetEquipmentView().Action.Active);
}
bool StartShift(FCodecWorld& W)
{
 const auto Count=W.Player->GetDodgeState().Records.size();
 if(!W.Test.TestTrue(TEXT("PRECONDITION genuine fresh Shift normal input"),W.Pulse(EKeys::LeftShift)))return false;
 const auto& S=W.Player->GetDodgeState();
 return W.Test.TestTrue(TEXT("PRECONDITION actual current grounded .40 action/owner/clock accepted before missing presentation"),S.Phase==DK::EPhase::Dodging&&S.Records.size()==Count+1&&S.OwnerId==W.Player->GetRuntimeEntityId()
  &&S.Time==W.Game->GetSimulationTime()&&S.Records.back().Finish==DK::EFinish::None&&S.Records.back().End==S.Records.back().Start+.4
  &&S.Records.back().ReadyAt==S.Records.back().Start+1.2&&W.Player->AnimationName==TEXT("dodge")&&W.Player->JumpHeight==0.f);
}
D::FDrawContext Context(const FCodecWorld& W)
{
 D::FDrawContext C;const auto P=W.Player->GetGroundPosition(),Camera=W.HUD->GetCameraGroundCenter();C.GroundScreen={640.+(P.X-Camera.X)*.65,490.-P.Y*.38};C.JumpHeight=W.Player->JumpHeight;return C;
}
TArray<uint8> SampleSignature(const FDungeonDodgePresentationSample& Q)
{
 FSignature S;S.V(Q.Active,Q.Invulnerable,Q.OwnerId,Q.ActionId,Q.StartEventId,Q.SampleTime,Q.Start,Q.End,Q.ReadyAt,Q.Elapsed,Q.Remaining,Q.Travelled,Q.Block,Q.Finish);S.Point(Q.Direction);return S.Bytes;
}
FDungeonDodgePresentationSample SentinelSample(){FDungeonDodgePresentationSample Q;Q.Active=true;Q.OwnerId=991;Q.ActionId=992;Q.Elapsed=9.;Q.Remaining=8.;Q.Direction={7,6};return Q;}
TArray<uint8> PlanSignature(const D::FDrawPlan& P)
{
 FSignature S;S.V(P.Supported,P.Frame,P.Facing,P.NonemptyDrawCount,P.CanvasSize,P.SourceToScreenScale,P.WeaponScale,P.WeaponWidth,P.WeaponAngle,P.TextureU,P.TextureDU);S.String(P.ProfileId);S.Bytes.Append(SampleSignature(P.Dodge));
 const auto& B=P.Binding;S.V(B.RunGuid.A,B.RunGuid.B,B.RunGuid.C,B.RunGuid.D,B.RunAlias,B.OwnerId,B.Revision,B.ActiveSlot,B.WeaponInstanceId,B.WeaponVersion,B.ArmorInstanceId,B.ArmorVersion,B.Armor);S.String(B.WeaponContentId);S.String(B.ArmorContentId);
 for(auto V:{P.RootSource,P.GripSource,P.AxisArtist,P.BodyTop,P.GripScreen,P.SwordTop,P.SwordPivotUV})S.Point(V);
 for(const auto& V:P.Slots){S.V(V.Component,V.KnownOptionalEmpty);S.String(V.TexturePath);}return S.Bytes;
}
D::FDrawPlan SentinelPlan(){D::FDrawPlan P;P.Supported=true;P.Frame=91;P.Facing=17;P.ProfileId=TEXT("sentinel.Dodge.plan");P.Dodge=SentinelSample();P.Binding.OwnerId=995;P.CanvasSize=76.;P.GripScreen={73,74};P.Slots[0].TexturePath=TEXT("sentinel.texture");return P;}
bool Prepared32(FAutomationTestBase& T)
{
 const auto& P=D::Profile();TSet<FString> Paths;const double Starts[]={0.,.1,.2,.3};
 bool Ok=P.SourceClosureVerified&&P.ProfileId==TEXT("EV048-v018-HeroLeatherDodge-v001")&&P.SourceClosureSHA256==TEXT("7b62e4e15616c8ada14826ab926361e9a78666f78639eb0e253fbaca50727097")
  &&P.CanvasSource==512&&P.StandingExtent==416.&&P.StandingDisplay==72.&&P.WeaponScale==.5&&P.ComponentGrip==FVector2D(99,256)
  &&P.SwordSourceSHA256==TEXT("2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a");
 for(int32 I=0;I<4;++I)
 {
  const auto& F=P.Frames[I];Ok&=F.Frame==I&&F.KeyAge==Starts[I]&&F.ExpectedNonemptyDrawCount==9;
  for(const auto& L:F.Layers){Ok&=!L.KnownOptionalEmpty&&L.SourceAlphaNonzero>0&&L.SourceSHA256.Len()==64&&L.SourceRGBASHA256.Len()==64&&!Paths.Contains(L.TexturePath)
   &&L.TexturePath.StartsWith(TEXT("/Game/Production/ArtTrials/EV048/v018/HeroLeatherDodge/"));Paths.Add(L.TexturePath);}
 }
 return T.TestTrue(TEXT("PRECONDITION immutable32 retained source metadata:5 owners+3 armor, all farhands nonempty, no WholeBody/GPU claim"),Ok&&Paths.Num()==32);
}
bool CheckSample(FAutomationTestBase& T,const FCodecWorld& W,const FDungeonDodgePresentationSample& Q)
{
 const auto& S=W.Player->GetDodgeState();const auto& R=S.Records.back();
 return T.TestTrue(TEXT("Read-only sample is the exact native double action record/clock, actual block and protection"),Q.Active&&Q.OwnerId==S.OwnerId&&Q.ActionId==R.ActionId&&Q.StartEventId==R.StartEventId
  &&Q.SampleTime==S.Time&&Q.Start==R.Start&&Q.End==R.End&&Q.ReadyAt==R.ReadyAt&&Q.Elapsed==S.Time-R.Start&&Q.Remaining==R.End-S.Time
  &&Q.Travelled==R.Travelled&&Q.Direction==FVector2D(R.Direction.X,R.Direction.Y)&&Q.Block==R.Block&&Q.Finish==R.Finish&&Q.Invulnerable==W.Player->IsDodgeInvulnerableAt(S.Time));
}
bool CheckPlan(FAutomationTestBase& T,const FCodecWorld& W,const D::FDrawPlan& P,int32 Frame)
{
 const auto& F=D::Profile().Frames[Frame];const auto C=Context(W);const int32 Face=W.Player->Facing<0?-1:1;const double Scale=72./416.*C.UIScale;
 const FVector2D Grip=C.GroundScreen+FVector2D(Face*(F.Grip.X-F.Root.X)*Scale,(F.Grip.Y-F.Root.Y)*Scale),Top=C.GroundScreen-FVector2D((Face<0?512.-F.Root.X:F.Root.X)*Scale,F.Root.Y*Scale);
 const auto& V=W.Game->GetEquipmentView();const auto& Weapon=V.Slots[V.ActiveSlot];const auto& Armor=V.Slots[2];
 bool Ok=P.Supported&&P.ProfileId==D::Profile().ProfileId&&P.Frame==Frame&&P.Facing==Face&&P.NonemptyDrawCount==9
  &&P.Binding.OwnerId==V.OwnerId&&P.Binding.Revision==V.Revision&&P.Binding.WeaponInstanceId==Weapon.InstanceId&&P.Binding.WeaponVersion==Weapon.Version
  &&P.Binding.ArmorInstanceId==Armor.InstanceId&&P.Binding.ArmorVersion==Armor.Version&&P.Binding.Armor==B::EArmor::LightArmor
  &&P.RootSource==F.Root&&P.GripSource==F.Grip&&P.AxisArtist==F.AxisArtist&&P.BodyTop.Equals(Top,1.e-7)&&P.GripScreen.Equals(Grip,1.e-7)
  &&FMath::IsNearlyEqual(P.CanvasSize,72.*512./416.,1.e-10)&&FMath::IsNearlyEqual(P.SourceToScreenScale,Scale,1.e-12)&&P.WeaponScale==.5
  &&FMath::IsNearlyEqual(P.WeaponWidth,72.*512./416.*.5*C.UIScale,1.e-10);
 const D::EComponent Order[]={D::EComponent::BodyRest,D::EComponent::ShoulderFar,D::EComponent::Chest,D::EComponent::NearArmWithoutHand,D::EComponent::ShoulderNear,D::EComponent::HelmetForeground,D::EComponent::IndependentSword,D::EComponent::FarHandForeground,D::EComponent::NearHand};
 for(int32 I=0;I<9;++I)
 {
  const auto& Slot=P.Slots[I];Ok&=Slot.Component==Order[I]&&!Slot.KnownOptionalEmpty;
  if(I==6){Ok&=Slot.TexturePath==D::Profile().SwordTexturePath;continue;}
  const auto Layer=std::find_if(F.Layers.begin(),F.Layers.end(),[&](const auto& L){return L.Component==Order[I];});Ok&=Layer!=F.Layers.end()&&Slot.TexturePath==Layer->TexturePath;
 }
 const double Angle=FMath::RadiansToDegrees(FMath::Atan2(F.AxisArtist.Y,F.AxisArtist.X))*(Face<0?-1.:1.);const FVector2D Pivot(Face<0?1.-99./512.:99./512.,.5);
 const double A=FMath::DegreesToRadians(P.WeaponAngle);const FVector2D Local((Face<0?-1.:1.)*100./512.*P.WeaponWidth,0.);
 const FVector2D ActualTip=P.SwordTop+Pivot*P.WeaponWidth+FVector2D(FMath::Cos(A)*Local.X-FMath::Sin(A)*Local.Y,FMath::Sin(A)*Local.X+FMath::Cos(A)*Local.Y);
 const FVector2D ExpectedTip=Grip+FVector2D(Face*F.AxisArtist.X,F.AxisArtist.Y)*(100./512.*P.WeaponWidth);
 Ok&=FMath::IsNearlyEqual(P.WeaponAngle,Angle,1.e-10)&&P.SwordPivotUV==Pivot&&P.SwordTop.Equals(Grip-Pivot*P.WeaponWidth,1.e-7)&&ActualTip.Equals(ExpectedTip,1.e-7)&&P.TextureU==(Face<0?1.:0.)&&P.TextureDU==(Face<0?-1.:1.);
 return CheckSample(T,W,P.Dodge)&&T.TestTrue(TEXT("Same complete nine-slot source plan/current gear versions/constant72/oneXmirror/.50 sword parent grip and axis"),Ok);
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFairytaleDodgeNativeClock,"CodexDungeon.Content.FairytaleSwordDodgeV001.RealShiftDoubleClockFourPhasesAndInterrupts",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFairytaleDodgeNativeClock::RunTest(const FString&)
{
 FDodgeOptInScope Flags;FCodecWorld W(*this);if(!W.Create()||!Equip(W,TEXT("ARM-LGT-001"),TEXT("dodge.clock.light"))||!Prepared32(*this)||!StartShift(W))return false;
 const auto R=W.Player->GetDodgeState().Records.back();FDungeonDodgePresentationSample Q;
 if(!TestTrue(TEXT("TARGET Stage0 RED: real Shift exposes exact readonly owner Dodge sample"),W.Player->QueryDodgePresentation(Q)))return false;
 CheckSample(*this,W,Q);
 // Exact same-action absolute boundaries and their real previous representations, not an invented animation clock.
 for(int32 Frame=0;Frame<4;++Frame)
 {
  if(Frame>0)
  {
   const double At=R.Start+(Frame==1?.1:Frame==2?.2:.3);const double Before=std::nextafter(At,R.Start);
   if(!TestTrue(TEXT("Real bound GameMode reaches previous representable phase boundary"),W.AdvanceTo(Before)))return false;
   D::FDrawPlan P;FString Why;if(!TestTrue(TEXT("Previous actual clock sample remains in earlier source phase"),D::BuildDrawPlan(*W.Game,*W.Player,Context(W),P,Why)))return false;CheckPlan(*this,W,P,Frame-1);
   if(!TestTrue(TEXT("Real bound GameMode reaches original Start+100/200/300ms exactly"),W.AdvanceTo(At)))return false;
  }
  FDungeonRunSnapshot Before,After;if(!W.Capture(TEXT("Actual active Dodge captures before readonly planning"),Before))return false;
  D::FDrawPlan P;FString Why;if(!TestTrue(TEXT("Actual active phase uses shared production plan"),W.Player->QueryDodgePresentation(Q)&&D::BuildDrawPlan(*W.Game,*W.Player,Context(W),P,Why)))return false;
  CheckPlan(*this,W,P,Frame);if(!W.Capture(TEXT("Actual active Dodge captures after readonly planning"),After))return false;TestTrue(TEXT("Query/plan never mutates complete native Run"),CodecSignature(Before)==CodecSignature(After));
 }
 TestTrue(TEXT("Original iframe half-open endpoints are independent of art frames"),!W.Player->IsDodgeInvulnerableAt(std::nextafter(R.Start+.06,R.Start))&&W.Player->IsDodgeInvulnerableAt(R.Start+.06)
  &&W.Player->IsDodgeInvulnerableAt(std::nextafter(R.Start+.20,R.Start))&&!W.Player->IsDodgeInvulnerableAt(R.Start+.20));
 if(!TestTrue(TEXT("Actual last representable sample stays active before original End"),W.AdvanceTo(std::nextafter(R.End,R.Start))&&W.Player->QueryDodgePresentation(Q)))return false;
 if(!TestTrue(TEXT("Actual End boundary completes original kernel action exactly"),W.AdvanceTo(R.End)&&W.Player->GetDodgeState().Phase==DK::EPhase::Idle&&W.Player->GetDodgeState().Records.back().Finish==DK::EFinish::Completed))return false;
 Q=SentinelSample();const auto Bytes=SampleSignature(Q);D::FDrawPlan P=SentinelPlan();const auto PBytes=PlanSignature(P);FString Why;
 TestTrue(TEXT("No source hold beyond actual End and no cooldown refund"),!W.Player->QueryDodgePresentation(Q)&&SampleSignature(Q)==Bytes&&!D::BuildDrawPlan(*W.Game,*W.Player,Context(W),P,Why)&&PlanSignature(P)==PBytes&&W.Player->GetDodgeState().ReadyAt==R.ReadyAt);
 W.Player->StartJump();W.Frame(.02f);TestTrue(TEXT("Actual airborne higher priority cannot become Dodge art"),W.Player->JumpHeight>0.f&&!W.Player->QueryDodgePresentation(Q)&&SampleSignature(Q)==Bytes);
 for(bool Lethal:{false,true})
 {
  FCodecWorld X(*this);if(!X.Create()||!Equip(X,TEXT("ARM-LGT-001"),Lethal?TEXT("dodge.dead.light"):TEXT("dodge.hurt.light"))||!StartShift(X))return false;
  const auto Action=X.Player->GetDodgeState().Records.back();if(!X.AdvanceTo(Action.Start+(Lethal?.025:.25)))return false;
  X.Player->ApplyCombatHit(Lethal?100000.f:5.f,nullptr,X.Player->GetPoiseThreshold());X.Frame(.005f);
  const auto& S=X.Player->GetDodgeState();Q=SentinelSample();
  TestTrue(TEXT("Real non-protected poise break/death closes original action, cannot be masked by Dodge"),S.Records.back().Finish==(Lethal?DK::EFinish::Death:DK::EFinish::PoiseBreak)
   &&X.Player->AnimationName==(Lethal?TEXT("death"):TEXT("hurt"))&&!X.Player->QueryDodgePresentation(Q)&&SampleSignature(Q)==Bytes);
 }
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFairytaleDodgeBindings,"CodexDungeon.Content.FairytaleSwordDodgeV001.RealBindingSource32NineSlotsMirrorAndAtomicRejection",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFairytaleDodgeBindings::RunTest(const FString&)
{
 FDodgeOptInScope Flags;if(!Prepared32(*this))return false;
 for(int32 Facing:{-1,1})
 {
  FCodecWorld W(*this);if(!W.Create()||!Equip(W,TEXT("ARM-LGT-001"),Facing<0?TEXT("dodge.left.light"):TEXT("dodge.right.light")))return false;
  const FKey Establish=Facing<0?EKeys::A:EKeys::D,Backwards=Facing<0?EKeys::D:EKeys::A;if(!W.Pulse(Establish)||!W.Key(Backwards,true)||!StartShift(W)||!W.Key(Backwards,false))return false;
  if(!TestTrue(TEXT("PRECONDITION genuine normal input rolls backwards while preserving actual facing"),W.Player->Facing==float(Facing)&&W.Player->GetDodgeState().Records.back().Direction.X==-double(Facing)))return false;
  auto P=SentinelPlan();FString Why;
  if(!TestTrue(TEXT("TARGET Stage0 RED: actual committed SWD/LGT Dodge admits complete nine-slot source32 plan"),D::BuildDrawPlan(*W.Game,*W.Player,Context(W),P,Why)))return false;
  const auto R=W.Player->GetDodgeState().Records.back();
  for(int32 Frame=0;Frame<4;++Frame)
  {
   if(Frame&&!W.AdvanceTo(R.Start+(Frame==1?.125:Frame==2?.225:.325)))return false;
   if(!D::BuildDrawPlan(*W.Game,*W.Player,Context(W),P,Why))return false;CheckPlan(*this,W,P,Frame);
  }
  FDungeonDodgePresentationSample Q;if(!W.Player->QueryDodgePresentation(Q))return false;B::FBinding Binding;if(!B::Resolve(*W.Game,*W.Player,Binding,Why))return false;
  const auto Reject=[&](const TCHAR* Label,auto Alter)
  {
   auto Source=D::Profile();Alter(Source);auto Out=SentinelPlan();const auto Bytes=PlanSignature(Out);TestTrue(Label,!D::BuildDrawPlanFromCommitted(Binding,Q,W.Player->Facing,Source,Context(W),Out,Why)&&PlanSignature(Out)==Bytes&&!Why.IsEmpty());
  };
  Reject(TEXT("Any missing source rejects complete32 atomically"),[](auto& S){S.Frames[0].Layers[0].TexturePath.Reset();});
  Reject(TEXT("Dodge FarHand cannot borrow Hurt optional-empty policy"),[](auto& S){S.Frames[1].Layers[6].KnownOptionalEmpty=true;S.Frames[1].Layers[6].SourceAlphaNonzero=0;});
  Reject(TEXT("Source closure/axis ownership cannot be replaced"),[](auto& S){S.Frames[3].AxisArtist=FVector2D::ZeroVector;});
  auto Bad=Binding;Bad.OwnerId++;auto Out=SentinelPlan();const auto Bytes=PlanSignature(Out);
  TestTrue(TEXT("A real action sample cannot authorize another committed owner"),!D::BuildDrawPlanFromCommitted(Bad,Q,W.Player->Facing,D::Profile(),Context(W),Out,Why)&&PlanSignature(Out)==Bytes);
  auto Stale=W.Game->GetEquipmentView();++Stale.Slots[Stale.ActiveSlot].Version;B::FBinding Rejected=Binding;
  TestTrue(TEXT("Stale equipped version cannot resolve for a new Dodge plan"),!B::ValidateCommitted(Stale,*W.Game->GetEquipmentInventoryState(),W.Player->GetMeleeCombatState(),W.Player->WeaponId,W.Player->ArmorId,Rejected,Why)&&Rejected.WeaponVersion==Binding.WeaponVersion);
  auto Air=Context(W);Air.JumpHeight=1.;Out=SentinelPlan();TestTrue(TEXT("Air context cannot bypass grounded Dodge priority"),!D::BuildDrawPlanFromCommitted(Binding,Q,W.Player->Facing,D::Profile(),Air,Out,Why)&&PlanSignature(Out)==Bytes);
 }
 FCodecWorld Other(*this);if(!Other.Create()||!Equip(Other,TEXT("ARM-MED-001"),TEXT("dodge.unsupported.medium"))||!StartShift(Other))return false;
 auto P=SentinelPlan();const auto Bytes=PlanSignature(P);FString Why;FDungeonRunSnapshot Before,After;if(!Other.Capture(TEXT("Actual unsupported gear captures"),Before))return false;
 TestTrue(TEXT("Actually committed MED cannot partially draw the SWD/LGT-only Dodge profile"),!D::BuildDrawPlan(*Other.Game,*Other.Player,Context(Other),P,Why)&&PlanSignature(P)==Bytes&&!Why.IsEmpty());
 if(Other.Capture(TEXT("Unsupported presentation remains capturable"),After))TestTrue(TEXT("Unsupported gear rejection is read-only"),CodecSignature(Before)==CodecSignature(After));return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFairytaleDodgeContinuation,"CodexDungeon.Content.FairytaleSwordDodgeV001.RealCodecPausedActiveActionKeepsClockAndGear",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFairytaleDodgeContinuation::RunTest(const FString&)
{
 FDodgeOptInScope Flags;FCodecWorld Source(*this);if(!Source.Create()||!Equip(Source,TEXT("ARM-LGT-001"),TEXT("dodge.codec.light"))||!Prepared32(*this)||!StartShift(Source))return false;
 const auto R=Source.Player->GetDodgeState().Records.back();if(!Source.AdvanceTo(R.Start+.13))return false;
 FDungeonRunSnapshot Saved;if(!Source.Capture(TEXT("PRECONDITION existing capture supports genuine active Dodge"),Saved))return false;
 const auto& D0=Saved.Fighters[0].Player.GetValue().Dodge;
 if(!TestTrue(TEXT("PRECONDITION saved original owner action is genuinely active in phase1"),D0.Phase==DK::EPhase::Dodging&&D0.Time>=R.Start+.1&&D0.Time<R.Start+.2&&D0.Records.back().Finish==DK::EFinish::None))return false;
 TArray<uint8> Encoded;FDungeonValidatedRun Decoded;FString Why;
 if(!TestTrue(TEXT("PRECONDITION existing codec preserves original double Dodge history without a neutral reset"),DungeonRunSnapshotCodec::Encode(Saved,Encoded,Why)&&DungeonRunSnapshotCodec::Decode(Encoded,Decoded,Why)&&Decoded.IsValid()
  &&Decoded.Get()->Fighters[0].Player.GetValue().Dodge.Time==D0.Time&&Decoded.Get()->Fighters[0].Player.GetValue().Dodge.Records.back().Start==R.Start))return false;
 FCodecWorld Target(*this);if(!Target.Create())return false;FDungeonPreparedRun Prepared;auto* Old=Target.Player;
 if(!TestTrue(TEXT("PRECONDITION real grouped installer accepts existing supported active Dodge"),FDungeonRunInstaller::Prepare(*Target.Game,Decoded,Prepared,Why)&&Prepared.IsReady()&&FDungeonRunInstaller::Install(*Target.Game,Prepared,Why)))return false;
 Target.Player=Target.Game->PlayerFighter;Target.Frame(.25f);FDungeonRunSnapshot Paused;if(!Target.Capture(TEXT("PRECONDITION installed paused active Dodge captures"),Paused))return false;
 if(!TestTrue(TEXT("PRECONDITION a new actual published Pawn retains original action/equipment and closed Continue, old Actor not reused"),Target.Player!=Old&&Target.Controller->GetPawn()==Target.Player
  &&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue&&CodecSignature(Paused)==CodecSignature(Saved)))return false;
 D::FDrawPlan P;
 if(!TestTrue(TEXT("TARGET Stage0 RED: paused installed Dodge draws saved phase/current gear without advancing or borrowing old actor"),D::BuildDrawPlan(*Target.Game,*Target.Player,Context(Target),P,Why)))return false;
 CheckPlan(*this,Target,P,1);FDungeonRunSnapshot Still;if(!Target.Capture(TEXT("Paused plan remains a readonly published boundary"),Still))return false;TestTrue(TEXT("Dodge presentation cannot continue, rewind or change saved native owners"),CodecSignature(Still)==CodecSignature(Saved));
 Target.Frame(.005f);if(!Target.Key(EKeys::Enter,true))return false;Target.Frame(.005f);
 if(!TestTrue(TEXT("Existing fresh Enter opens Continue without consuming saved Dodge time"),Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open&&Target.Player->GetDodgeState().Time==D0.Time))return false;
 if(!Target.Key(EKeys::Enter,false))return false;Target.Frame(.02f);
 if(!TestTrue(TEXT("Continued original action progresses from saved phase1 rather than Dodge0"),Target.Player->GetDodgeState().Time>D0.Time&&Target.Player->GetDodgeState().Records.back().ActionId==R.ActionId&&D::BuildDrawPlan(*Target.Game,*Target.Player,Context(Target),P,Why)))return false;
 CheckPlan(*this,Target,P,1);
 const auto Current=Target.Player->GetDodgeState();FCodecWorld Wrong(*this);if(!Wrong.Create())return false;auto Out=SentinelPlan();const auto Bytes=PlanSignature(Out);
 TestTrue(TEXT("Another World cannot authorize this installed player's old plan/binding"),!D::BuildDrawPlan(*Wrong.Game,*Target.Player,Context(Target),Out,Why)&&PlanSignature(Out)==Bytes&&Target.Player->GetDodgeState().Time==Current.Time);return true;
}
#endif
