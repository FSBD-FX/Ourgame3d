#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "../DungeonFairytaleSwordAirV001.h"
#include "../DungeonRunInstaller.h"
#include "../DungeonRunSnapshotCodec.h"
#include "Engine/Texture2D.h"
#include "TextureResource.h"
#include "RunCodecFixture_v001.h"
#include <cmath>

namespace
{
namespace Air=DungeonFairytaleSwordAirV001;
namespace Bind=DungeonFairytaleSwordEquipmentBinding;
struct FAirOptIns
{
 const FString Original=FCommandLine::Get();
 FAirOptIns(){FString Next=Original;for(const TCHAR* Flag:{Bind::CommandLineFlag,Air::CommandLineFlag})if(!FParse::Param(*Next,Flag))Next+=FString(TEXT(" -"))+Flag;FCommandLine::Set(*Next);}
 ~FAirOptIns(){FCommandLine::Set(*Original);}
};
bool EquipLight(FCodecWorld& W,const TCHAR* Key)
{
 IV::FItem Item;Item.ContentId="ARM-LGT-001";
 const auto R=W.Game->RegisterEquipmentSource(Key,Item,W.Player->GetGroundPosition()+FVector2D(24,0),true);
 if(!W.Test.TestTrue(TEXT("PRECONDITION real legal LGT display source"),R.Ok()))return false;
 W.Frame(.005f);
 if(!W.Test.TestTrue(TEXT("PRECONDITION real displayed armor source receives normal fresh E"),W.Game->GetEquipmentView().SelectedSourceId==R.SourceId&&W.Pulse(EKeys::E)))return false;
 const auto A=W.Game->GetEquipmentView().Action;
 return W.Test.TestTrue(TEXT("PRECONDITION actual .50 armor transaction commits through its existing deadline"),A.Active&&A.Kind==EDungeonEquipmentActionKind::PickupArmor&&A.InstanceId==R.InstanceId&&A.Deadline==A.Start+.5
  &&W.AdvanceTo(A.Deadline)&&W.Player->ArmorId==TEXT("ARM-LGT-001")&&!W.Game->GetEquipmentView().Action.Active);
}
bool RealSpace(FCodecWorld& W)
{
 if(!W.Test.TestTrue(TEXT("PRECONDITION stable real owner is grounded before normal Space"),W.Player->JumpHeight==0.f&&W.Player->GetVerticalVelocity()==0.f
  &&W.Player->GetMeleeCombatState().Grounded&&W.Player->GetWeaponActionsState().Budget.Grounded&&W.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open))return false;
 if(!W.Test.TestTrue(TEXT("PRECONDITION genuine fresh Space input is admitted"),W.Pulse(EKeys::SpaceBar)))return false;
 return W.Test.TestTrue(TEXT("PRECONDITION actual native ballistic owner is rising before any target assertion"),W.Player->JumpHeight>0.f&&W.Player->GetVerticalVelocity()>315.f
  &&!W.Player->GetMeleeCombatState().Grounded&&!W.Player->GetWeaponActionsState().Budget.Grounded&&!W.Player->GetMeleeCombatState().Action.Active&&!W.Player->GetWeaponActionsState().Action.Active);
}
Air::FDrawContext Context(const FCodecWorld& W)
{
 Air::FDrawContext C;const auto G=W.Player->GetGroundPosition(),Camera=W.HUD->GetCameraGroundCenter();
 C.GroundScreen={double(float(640.+(G.X-Camera.X)*.65f)),double(float(490.-G.Y*.38f))};C.JumpHeight=double(W.Player->JumpHeight);
 C.Tint=W.Player->HitFlash>0.f?FLinearColor(1.7f,.6f,.4f,1.f):FLinearColor::White;return C;
}
TArray<uint8> SampleBytes(const FDungeonHeroAirSample& Q)
{FSignature S;S.V(Q.Valid,Q.RunGuid.A,Q.RunGuid.B,Q.RunGuid.C,Q.RunGuid.D,Q.OwnerId,Q.RoomInstanceId,Q.PresentationEpoch,Q.NativeTime,Q.Facing,Q.JumpHeight,Q.VerticalVelocity,Q.LandingVisualAge);S.Point(Q.GroundPosition);return S.Bytes;}
FDungeonHeroAirSample SentinelSample(){FDungeonHeroAirSample Q;Q.Valid=true;Q.OwnerId=901;Q.NativeTime=902.;Q.JumpHeight=903.f;Q.GroundPosition={904,905};return Q;}
TArray<uint8> PlanBytes(const Air::FDrawPlan& P)
{
 FSignature S;S.V(P.Supported,P.Frame,P.Facing,P.NonemptyDrawCount,P.Pose,P.CanvasSize,P.SourceToScreenScale,P.WeaponScale,P.WeaponWidth,P.WeaponAngle,P.TextureU,P.TextureDU);
 S.String(P.ProfileId);S.Bytes.Append(SampleBytes(P.Sample));const auto& B=P.Binding;
 S.V(B.RunGuid.A,B.RunGuid.B,B.RunGuid.C,B.RunGuid.D,B.RunAlias,B.OwnerId,B.Revision,B.ActiveSlot,B.WeaponInstanceId,B.WeaponVersion,B.ArmorInstanceId,B.ArmorVersion,B.Armor);S.String(B.WeaponContentId);S.String(B.ArmorContentId);
 for(auto V:{P.RootSource,P.GripSource,P.AxisArtist,P.BodyTop,P.GripScreen,P.SwordTop,P.SwordPivotUV})S.Point(V);
 S.V(P.Tint.R,P.Tint.G,P.Tint.B,P.Tint.A);for(const auto& V:P.Slots){S.V(V.Component,V.KnownOptionalEmpty,V.Enabled);S.String(V.TexturePath);}return S.Bytes;
}
Air::FDrawPlan SentinelPlan(){Air::FDrawPlan P;P.Supported=true;P.Frame=91;P.Facing=17;P.ProfileId=TEXT("sentinel.air.plan");P.Sample=SentinelSample();P.GripScreen={73,74};P.Slots[0].TexturePath=TEXT("sentinel.texture");return P;}
int32 IndependentFrame(float H,float V,float Age)
{
 if(H>0.f||V>0.f)return V>315.f?0:V>90.f?1:V>=-90.f?2:3;
 return H==0.f&&V==0.f&&Age>=0.f&&Age<.12f?(Age<.06f?4:5):-1;
}
bool CheckSample(FAutomationTestBase& T,const FCodecWorld& W,const FDungeonHeroAirSample& Q)
{
 const auto& V=W.Game->GetEquipmentView();
 return T.TestTrue(TEXT("Sample is exact current completed native owner/run/current-room/epoch/time/H/V/age, not AnimationTime"),Q.Valid&&Q.RunGuid==V.RunGuid&&Q.OwnerId==V.OwnerId&&Q.OwnerId==W.Player->GetRuntimeEntityId()
  &&Q.RoomInstanceId==V.RoomInstanceId&&Q.PresentationEpoch==W.Game->GetRunPresentationEpoch()&&Q.NativeTime==W.Game->GetSimulationTime()
  &&Q.GroundPosition==W.Player->GetGroundPosition()&&Q.Facing==W.Player->Facing&&Q.JumpHeight==W.Player->JumpHeight&&Q.VerticalVelocity==W.Player->GetVerticalVelocity()&&Q.LandingVisualAge==W.Player->GetLandingVisualAge());
}
bool CheckSelect(FAutomationTestBase& T,const FDungeonHeroAirSample& Q)
{
 Air::FSelection S;FString Why;const int32 Expected=IndependentFrame(Q.JumpHeight,Q.VerticalVelocity,Q.LandingVisualAge);
 return T.TestTrue(TEXT("Pure visual selector consumes actual H/V/age with original half-open landing window"),Expected>=0&&Air::Select(Q,S,Why)&&S.Valid&&S.Frame==Expected&&int32(S.Pose)==Expected+1);
}
bool ReachLanding(FCodecWorld& W)
{
 for(int32 N=0;N<160&&(W.Player->JumpHeight>0.f||W.Player->GetVerticalVelocity()>0.f);++N)W.Frame(.005f);
 return W.Test.TestTrue(TEXT("PRECONDITION real central motion reached living first grounded landing window"),!W.Player->bDead&&W.Player->JumpHeight==0.f&&W.Player->GetVerticalVelocity()==0.f
  &&W.Player->GetMeleeCombatState().Grounded&&W.Player->GetWeaponActionsState().Budget.Grounded&&W.Player->GetLandingVisualAge()>=0.f&&W.Player->GetLandingVisualAge()<.01f);
}
bool IsArmor(Air::EComponent C)
{return C==Air::EComponent::ShoulderFar||C==Air::EComponent::Chest||C==Air::EComponent::ShoulderNear;}
bool ProfileAndResidents(FAutomationTestBase& T,TArray<Air::FResidentTexture>& Residents)
{
 const auto& P=Air::Profile();TSet<FString> Paths;bool Ok=P.SourceClosureVerified&&!P.ProfileId.IsEmpty()&&P.SourceClosureSHA256.Len()==64
  &&P.CanvasSource==512&&P.StandingExtent==416.&&P.StandingDisplay==72.&&P.HeightProjection==.70&&P.WeaponScale==.5&&P.SwordSourceSHA256.Len()==64&&!P.SwordTexturePath.IsEmpty();
 for(int32 I=0;I<6;++I)
 {
  const auto& F=P.Frames[I];TSet<uint8> Owners,Order;Ok&=F.Frame==I&&int32(F.Pose)==I+1&&F.ExpectedNonemptyDrawCount==9;
  for(const auto& L:F.Layers){Ok&=!L.KnownOptionalEmpty&&L.SourceAlphaNonzero>0&&L.SourceSHA256.Len()==64&&L.SourceRGBASHA256.Len()==64&&!Paths.Contains(L.TexturePath)&&!L.TexturePath.IsEmpty();Paths.Add(L.TexturePath);Owners.Add(uint8(L.Component));}
  for(auto C:F.SlotOrder)Order.Add(uint8(C));Ok&=Owners.Num()==8&&Order.Num()==9;
 }
 Ok&=Paths.Num()==48&&!Paths.Contains(P.SwordTexturePath);Paths.Add(P.SwordTexturePath);
 for(const auto& Path:Paths)
 {
  auto* Texture=FindObject<UTexture2D>(nullptr,*Path);Air::FResidentTexture R;R.TexturePath=Path;
  if(Texture){R.ClassName=Texture->GetClass()->GetName();R.Width=Texture->GetSizeX();R.Height=Texture->GetSizeY();R.ResourceReady=Texture->GetResource()!=nullptr;R.PendingInitialization=Texture->HasPendingRenderResourceInitialization();}
  Residents.Add(R);Ok&=Texture&&Texture->GetPathName()==Path&&R.ClassName==TEXT("Texture2D")&&R.Width==512&&R.Height==512&&R.ResourceReady&&!R.PendingInitialization;
 }
 FString Why;return T.TestTrue(TEXT("Actual preload contains complete48 unique retained phase layers and independent sword49 before any slot"),Ok&&Residents.Num()==49&&Air::ValidateResidentSet(P,Residents,Why));
}
bool CheckPlan(FAutomationTestBase& T,const FCodecWorld& W,const Air::FDrawPlan& P)
{
 const int32 Frame=IndependentFrame(W.Player->JumpHeight,W.Player->GetVerticalVelocity(),W.Player->GetLandingVisualAge());if(Frame<0)return T.TestTrue(TEXT("Expected real Air/Landing phase exists"),false);
 const auto& F=Air::Profile().Frames[Frame];const auto C=Context(W);const int32 Face=W.Player->Facing<0?-1:1;const bool Light=!W.Player->ArmorId.IsEmpty();const double S=72./416.*C.UIScale;
 const FVector2D Lift(0.,double(W.Player->JumpHeight)*.70*C.UIScale),Grip=C.GroundScreen-Lift+FVector2D(Face*(F.Grip.X-F.Root.X)*S,(F.Grip.Y-F.Root.Y)*S);
 const FVector2D Top=C.GroundScreen-Lift-FVector2D((Face<0?512.-F.Root.X:F.Root.X)*S,F.Root.Y*S);
 bool Ok=P.Supported&&P.Frame==Frame&&int32(P.Pose)==Frame+1&&P.Facing==Face&&P.NonemptyDrawCount==(Light?9:6)&&P.ProfileId==Air::Profile().ProfileId
  &&P.Binding.OwnerId==W.Game->GetEquipmentView().OwnerId&&P.Binding.WeaponInstanceId==W.Game->GetEquipmentView().Slots[W.Game->GetEquipmentView().ActiveSlot].InstanceId
  &&P.Binding.ArmorInstanceId==W.Game->GetEquipmentView().Slots[2].InstanceId&&P.RootSource==F.Root&&P.GripSource==F.Grip&&P.AxisArtist==F.AxisArtist
  &&P.BodyTop.Equals(Top,1.e-6)&&P.GripScreen.Equals(Grip,1.e-6)&&FMath::IsNearlyEqual(P.CanvasSize,72.*512./416.,1.e-10)
  &&FMath::IsNearlyEqual(P.SourceToScreenScale,S,1.e-12)&&P.WeaponScale==.5&&P.Tint==C.Tint&&P.TextureU==(Face<0?1.:0.)&&P.TextureDU==(Face<0?-1.:1.);
 int32 Enabled=0;TSet<uint8> Seen;for(int32 I=0;I<9;++I)
 {
  const auto& Slot=P.Slots[I];Ok&=Slot.Component==F.SlotOrder[I]&&!Slot.KnownOptionalEmpty&&!Seen.Contains(uint8(Slot.Component));Seen.Add(uint8(Slot.Component));
  const bool ExpectEnabled=Light||!IsArmor(Slot.Component);Ok&=Slot.Enabled==ExpectEnabled;Enabled+=Slot.Enabled?1:0;
  if(Slot.Component==Air::EComponent::IndependentSword)Ok&=Slot.TexturePath==Air::Profile().SwordTexturePath;
  else{const auto L=std::find_if(F.Layers.begin(),F.Layers.end(),[&](const auto& X){return X.Component==Slot.Component;});Ok&=L!=F.Layers.end()&&L->TexturePath==Slot.TexturePath;}
 }
 const double Angle=FMath::RadiansToDegrees(FMath::Atan2(F.AxisArtist.Y,F.AxisArtist.X))*(Face<0?-1.:1.);const auto CG=Air::Profile().ComponentGrip;
 const FVector2D Pivot(Face<0?1.-CG.X/512.:CG.X/512.,CG.Y/512.);const double Width=72.*512./416.*.5*C.UIScale;
 Ok&=Enabled==(Light?9:6)&&Seen.Num()==9&&FMath::IsNearlyEqual(P.WeaponWidth,Width,1.e-10)&&FMath::IsNearlyEqual(P.WeaponAngle,Angle,1.e-10)&&P.SwordPivotUV==Pivot&&P.SwordTop.Equals(Grip-Pivot*Width,1.e-6);
 return CheckSample(T,W,P.Sample)&&T.TestTrue(TEXT("Same actual plan retains all author owners, None6/LGT9, 416-to72, real .70 lift, one mirror, sword grip/axis and actual Tint"),Ok);
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FHeroAirRealSpace,"CodexDungeon.Content.FairytaleSwordAirV001.RealSpaceOwnerStateVelocityClassification",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FHeroAirRealSpace::RunTest(const FString&)
{
 FAirOptIns Flags;FCodecWorld W(*this);if(!W.Create()||!RealSpace(W))return false;
 FDungeonRunSnapshot Before,After;if(!W.Capture(TEXT("PRECONDITION actual airborne run remains capturable"),Before))return false;FDungeonHeroAirSample Q;
 if(!TestTrue(TEXT("TARGET Stage0 RED: real Space exposes exact readonly current hero nonattack Air sample"),W.Player->QueryHeroNonAttackAir(Q)))return false;
 CheckSample(*this,W,Q);CheckSelect(*this,Q);if(!W.Capture(TEXT("Query and selector leave complete native run unchanged"),After))return false;TestTrue(TEXT("Air reads never mutate native run"),CodecSignature(Before)==CodecSignature(After));
 const double Start=W.Game->GetSimulationTime();for(double Age:{.10,.22,.34,.44,.60})
 {if(!W.AdvanceTo(Start+Age))return false;if(!TestTrue(TEXT("Every completed real ballistic phase exposes current sample"),W.Player->QueryHeroNonAttackAir(Q)))return false;CheckSample(*this,W,Q);CheckSelect(*this,Q);}
 // Explicit value-seam boundary tests derive from a genuine owner sample. These
 // are unit domains, not substituted native jump witnesses or GPU receipts.
 for(const auto& C:TArray<TPair<float,int32>>{{630.f,0},{std::nextafter(315.f,INFINITY),0},{315.f,1},{std::nextafter(90.f,INFINITY),1},{90.f,2},{0.f,2},{-90.f,2},{std::nextafter(-90.f,-INFINITY),3}})
 {auto Value=Q;Value.JumpHeight=110.f;Value.VerticalVelocity=C.Key;Air::FSelection S;FString Why;TestTrue(TEXT("Frozen pure velocity boundary chooses the declared six-pose key"),Air::Select(Value,S,Why)&&S.Frame==C.Value);}
 auto Takeoff=Q;Takeoff.JumpHeight=0.f;Takeoff.VerticalVelocity=630.f;Takeoff.LandingVisualAge=.01f;Air::FSelection S;FString Why;
 TestTrue(TEXT("H0/V630 with previous landing age selects RiseEarly before Landing"),Air::Select(Takeoff,S,Why)&&S.Frame==0);
 auto Invalid=Q;Invalid.JumpHeight=-1.f;S.Valid=true;S.Frame=91;TestTrue(TEXT("Invalid physical domain rejects selector without modifying Out"),!Air::Select(Invalid,S,Why)&&S.Valid&&S.Frame==91);
 for(int32 Facing:{-1,1}){FCodecWorld X(*this);if(!X.Create()||!X.Pulse(Facing<0?EKeys::A:EKeys::D)||!RealSpace(X))return false;TestTrue(TEXT("Both normal input facings survive the actual query"),X.Player->QueryHeroNonAttackAir(Q)&&Q.Facing==float(Facing));}
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FHeroAirAtomic,"CodexDungeon.Content.FairytaleSwordAirV001.RealBinding49ResidentsSixPosesNone6Light9MirrorTintAtomic",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FHeroAirAtomic::RunTest(const FString&)
{
 FAirOptIns Flags;FCodecWorld W(*this);if(!W.Create()||!EquipLight(W,TEXT("air.atomic.light"))||!RealSpace(W))return false;Air::FDrawPlan P;FString Why;
 if(!TestTrue(TEXT("TARGET Stage0 RED: actual committed SWD/LGT real Air admits complete atomic source49 plan"),Air::BuildDrawPlan(*W.Game,*W.Player,Context(W),P,Why)))return false;
 TArray<Air::FResidentTexture> Residents;if(!ProfileAndResidents(*this,Residents))return false;CheckPlan(*this,W,P);
 auto BadResident=Residents;BadResident[0].ResourceReady=false;TestTrue(TEXT("One missing resource closes complete49 preflight"),!Air::ValidateResidentSet(Air::Profile(),BadResident,Why));
 BadResident=Residents;BadResident[1].TexturePath=BadResident[0].TexturePath;TestTrue(TEXT("Duplicate path cannot masquerade as complete49"),!Air::ValidateResidentSet(Air::Profile(),BadResident,Why));
 for(bool Light:{false,true})for(int32 Facing:{-1,1})
 {
  FCodecWorld X(*this);if(!X.Create()||(Light&&!EquipLight(X,Light?TEXT("air.light.case"):TEXT("air.none.case")))||!X.Pulse(Facing<0?EKeys::A:EKeys::D)||!RealSpace(X))return false;
  const double Start=X.Game->GetSimulationTime();TSet<int32> Frames;
  for(int32 N=0;N<170;++N)
  {
   FDungeonHeroAirSample Q;if(X.Player->QueryHeroNonAttackAir(Q)){if(!Air::BuildDrawPlan(*X.Game,*X.Player,Context(X),P,Why))return TestTrue(TEXT("Actual live selected phase has a full plan"),false);CheckPlan(*this,X,P);Frames.Add(P.Frame);}
   X.Frame(.005f);
  }
  TestTrue(TEXT("One genuine jump observes all six air/landing poses without new animation clock"),Frames.Num()==6&&X.Game->GetSimulationTime()>Start+.80);
 }
 FDungeonHeroAirSample Q;if(!W.Player->QueryHeroNonAttackAir(Q))return false;Bind::FBinding B;if(!Bind::Resolve(*W.Game,*W.Player,B,Why))return false;
 const auto Reject=[&](const TCHAR* Label,auto Alter){auto Source=Air::Profile();Alter(Source);auto Out=SentinelPlan();const auto Bytes=PlanBytes(Out);TestTrue(Label,!Air::BuildDrawPlanFromCommitted(B,Q,Source,Context(W),Out,Why)&&PlanBytes(Out)==Bytes&&!Why.IsEmpty());};
 Reject(TEXT("Missing phase source rejects atomically"),[](auto& Source){Source.Frames[0].Layers[0].TexturePath.Reset();});
 Reject(TEXT("A nonempty hand cannot borrow optional-empty policy"),[](auto& Source){Source.Frames[2].Layers[6].KnownOptionalEmpty=true;Source.Frames[2].Layers[6].SourceAlphaNonzero=0;});
 Reject(TEXT("Wrong source axis/closure cannot authorize source ownership"),[](auto& Source){Source.Frames[3].AxisArtist=FVector2D::ZeroVector;});
 auto Out=SentinelPlan();const auto Bytes=PlanBytes(Out);auto C=Context(W);C.GroundScreen={1.e20,1.e20};
 TestTrue(TEXT("Finite but float-collapsed submitted quad is rejected atomically"),!Air::BuildDrawPlanFromCommitted(B,Q,Air::Profile(),C,Out,Why)&&PlanBytes(Out)==Bytes);
 W.Player->ApplyCombatHit(1.f,nullptr,0.f);W.Frame(.005f);
 TestTrue(TEXT("Ordinary nonpoise hit remains nonattack Air with same full-stack actual feedback Tint"),W.Player->HitFlash>0.f&&W.Player->AnimationName!=TEXT("hurt")&&Air::BuildDrawPlan(*W.Game,*W.Player,Context(W),P,Why)&&P.Tint==Context(W).Tint);CheckPlan(*this,W,P);
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FHeroAirLanding,"CodexDungeon.Content.FairytaleSwordAirV001.RealLandingRejumpActionsHurtDeathRestoreEpochPriority",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FHeroAirLanding::RunTest(const FString&)
{
 FAirOptIns Flags;FCodecWorld W(*this);if(!W.Create()||!EquipLight(W,TEXT("air.landing.light"))||!RealSpace(W)||!ReachLanding(W))return false;FDungeonHeroAirSample Q;Air::FSelection S;FString Why;
 if(!TestTrue(TEXT("TARGET Stage0 RED: real native landing window exposes LandingImpact without inventing a new timer"),W.Player->QueryHeroNonAttackAir(Q)&&Air::Select(Q,S,Why)&&S.Frame==4))return false;
 CheckSample(*this,W,Q);W.Frame(.065f);TestTrue(TEXT("Original landing age enters second half and selects LandingSettle"),W.Player->GetLandingVisualAge()>=.06f&&W.Player->GetLandingVisualAge()<.12f&&W.Player->QueryHeroNonAttackAir(Q)&&Air::Select(Q,S,Why)&&S.Frame==5);
 W.Frame(.06f);Q=SentinelSample();const auto Bytes=SampleBytes(Q);TestTrue(TEXT("At original .12 cap nonattack Landing ends with Out unchanged"),W.Player->GetLandingVisualAge()==.12f&&!W.Player->QueryHeroNonAttackAir(Q)&&SampleBytes(Q)==Bytes);
 for(FKey Input:{EKeys::SpaceBar,EKeys::J,EKeys::LeftShift,EKeys::K})
 {
  FCodecWorld X(*this);if(!X.Create()||!RealSpace(X)||!ReachLanding(X)||!X.Pulse(Input))return false;Q=SentinelSample();
  if(Input==EKeys::SpaceBar)TestTrue(TEXT("Fresh normal re-jump during .12 landing window immediately owns Air"),X.Player->JumpHeight>0.f&&X.Player->GetVerticalVelocity()>0.f&&X.Player->QueryHeroNonAttackAir(Q)&&Air::Select(Q,S,Why)&&S.Frame==0);
  else TestTrue(TEXT("Normal grounded J/Shift/K during landing immediately retain original action priority"),(Input==EKeys::J?X.Player->GetMeleeCombatState().Action.Active:Input==EKeys::LeftShift?X.Player->GetDodgeState().Phase==DK::EPhase::Dodging:X.Player->GetWeaponSkillAction().Active)&&!X.Player->QueryHeroNonAttackAir(Q)&&SampleBytes(Q)==Bytes);
 }
 for(bool Lethal:{false,true})
 {
  FCodecWorld X(*this);if(!X.Create()||!RealSpace(X))return false;X.Player->ApplyCombatHit(Lethal?100000.f:5.f,nullptr,X.Player->GetPoiseThreshold());X.Frame(.005f);Q=SentinelSample();
  TestTrue(TEXT("Real airborne poise break/death keeps Hurt/Death ahead of nonattack Air"),X.Player->AnimationName==(Lethal?TEXT("death"):TEXT("hurt"))&&!X.Player->QueryHeroNonAttackAir(Q)&&SampleBytes(Q)==Bytes);
 }
 FCodecWorld Attack(*this);if(!Attack.Create()||!RealSpace(Attack)||!Attack.Pulse(EKeys::J))return false;Q=SentinelSample();
 TestTrue(TEXT("Accepted real AirPrimary cannot be renamed nonattack Air"),Attack.Player->GetMeleeCombatState().Action.Active&&Attack.Player->GetMeleeCombatState().Action.StartedAirborne&&!Attack.Player->QueryHeroNonAttackAir(Q)&&SampleBytes(Q)==Bytes);
 FCodecWorld Gear(*this);if(!Gear.Create()||!RealSpace(Gear)||!ReachLanding(Gear))return false;IV::FItem Item;Item.ContentId="ARM-LGT-001";
 const auto Pickup=Gear.Game->RegisterEquipmentSource(TEXT("air.landing.gear"),Item,Gear.Player->GetGroundPosition()+FVector2D(24,0),true);Gear.Frame(.005f);
 if(!TestTrue(TEXT("Real armor source receives normal E during landing"),Pickup.Ok()&&Gear.Game->GetEquipmentView().SelectedSourceId==Pickup.SourceId&&Gear.Pulse(EKeys::E)))return false;Q=SentinelSample();
 TestTrue(TEXT("Actual pickup transaction owns its .50 interval before any nonattack Landing pose"),Gear.Game->GetEquipmentView().Action.Active&&!Gear.Player->QueryHeroNonAttackAir(Q)&&SampleBytes(Q)==Bytes);
 FCodecWorld Source(*this);if(!Source.Create()||!EquipLight(Source,TEXT("air.restore.light"))||!RealSpace(Source))return false;Source.Frame(.13f);FDungeonRunSnapshot Saved;if(!Source.Capture(TEXT("Real airborne H/V/age can be captured by existing schema"),Saved))return false;
 TArray<uint8> Encoded;FDungeonValidatedRun Decoded;
 if(!TestTrue(TEXT("Existing codec preserves real airborne owner without added Air fields"),DungeonRunSnapshotCodec::Encode(Saved,Encoded,Why)&&DungeonRunSnapshotCodec::Decode(Encoded,Decoded,Why)&&Decoded.IsValid()))return false;
 FCodecWorld Target(*this);if(!Target.Create())return false;const uint64 BeforeEpoch=Target.Game->GetRunPresentationEpoch();auto* Old=Target.Player;FDungeonPreparedRun Prepared;
 if(!TestTrue(TEXT("Existing grouped installer publishes actual saved Air under a fresh epoch"),FDungeonRunInstaller::Prepare(*Target.Game,Decoded,Prepared,Why)&&FDungeonRunInstaller::Install(*Target.Game,Prepared,Why)))return false;
 Target.Player=Target.Game->PlayerFighter;Target.Frame(.25f);FDungeonRunSnapshot Paused;if(!Target.Capture(TEXT("Paused restored Air remains capturable"),Paused))return false;
 TestTrue(TEXT("Paused current owner sample uses new actor/epoch and saved H/V/age/time without auto Continue"),Target.Player!=Old&&Target.Game->GetRunPresentationEpoch()!=BeforeEpoch&&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue
  &&CodecSignature(Paused)==CodecSignature(Saved)&&Target.Player->QueryHeroNonAttackAir(Q)&&Q.PresentationEpoch==Target.Game->GetRunPresentationEpoch()&&Q.NativeTime==Saved.SimulationTime);CheckSample(*this,Target,Q);
 if(!Target.Pulse(EKeys::Enter))return false;Target.Frame(.02f);TestTrue(TEXT("Normal fresh Enter resumes saved airborne trajectory rather than replaying Takeoff"),Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open&&Target.Game->GetSimulationTime()>Saved.SimulationTime&&Target.Player->GetVerticalVelocity()<Saved.Fighters[0].JumpVelocity);
 FCodecWorld Wrong(*this);if(!Wrong.Create())return false;auto Out=SentinelPlan();const auto PBytes=PlanBytes(Out);
 TestTrue(TEXT("Another GameMode/World cannot authorize this current hero or cached epoch"),!Air::BuildDrawPlan(*Wrong.Game,*Target.Player,Context(Target),Out,Why)&&PlanBytes(Out)==PBytes);
 return true;
}
#endif
