#include "../existing-source/DungeonFairytaleSwordAirV001.cpp"
#include <iostream>
#include <sstream>
#include <iomanip>
#include <limits>
DungeonFairytaleSwordEquipmentBinding::FBinding HostBinding;
bool DungeonFairytaleSwordEquipmentBinding::Resolve(const ADungeonGameMode&,const ADungeonFighter&,FBinding& Out,FString& Diagnostic){Out=HostBinding;Diagnostic.Reset();return true;}

#include <iostream>
#include <limits>

namespace A=DungeonFairytaleSwordAirV001;
int RunSelectCases()
{
 int Cases=0,Failed=0;
 FDungeonHeroAirSample Base;Base.Valid=true;Base.RunGuid.A=1;Base.OwnerId=1;Base.RoomInstanceId=1;Base.PresentationEpoch=0;Base.NativeTime=17.;Base.Facing=1.f;Base.GroundPosition={12.,-14.};
 struct Case{float H,V,Age;int Expected;};const float Inf=std::numeric_limits<float>::infinity();
 const Case Values[]={
  {0.f,630.f,.01f,0},{0.f,630.f,.12f,0},{.0000001f,630.f,0.f,0},
  {80.f,std::nextafter(315.f,Inf),.12f,0},{80.f,315.f,.12f,1},{80.f,std::nextafter(315.f,-Inf),.12f,1},
  {108.f,std::nextafter(90.f,Inf),.12f,1},{108.f,90.f,.12f,2},{110.25f,0.f,.12f,2},
  {108.f,-90.f,.12f,2},{108.f,std::nextafter(-90.f,Inf),.12f,2},{108.f,std::nextafter(-90.f,-Inf),.12f,3},
  {.00000001f,-630.f,.12f,3},{1.f,-450.f,.01f,3},
  {0.f,0.f,0.f,4},{0.f,0.f,std::nextafter(.06f,0.f),4},{0.f,0.f,.06f,5},{0.f,0.f,std::nextafter(.06f,Inf),5},
  {0.f,0.f,std::nextafter(.12f,0.f),5},{0.f,0.f,.12f,-1},{0.f,0.f,std::nextafter(.12f,Inf),-1},
  {0.f,-1.f,.01f,-1},{-1.f,630.f,.01f,-1},{0.f,0.f,-.01f,-1},{Inf,450.f,.12f,-1},{110.f,Inf,.12f,-1},
  {110.f,std::numeric_limits<float>::quiet_NaN(),.12f,-1}};
 const auto Check=[&](const FDungeonHeroAirSample& Q,int Expected)
 {
  ++Cases;A::FSelection Out;Out.Valid=true;Out.Frame=91;Out.Pose=A::EPose::Fall;FString Why;const bool Ok=A::Select(Q,Out,Why);
  const bool Pass=Expected>=0?Ok&&Out.Valid&&Out.Frame==Expected&&int(Out.Pose)==Expected+1&&Why.Value.empty():!Ok&&Out.Valid&&Out.Frame==91&&Out.Pose==A::EPose::Fall&&!Why.Value.empty();
  if(!Pass){++Failed;std::cerr<<"case "<<Cases<<" failed expected "<<Expected<<"\n";}
 };
 for(const auto& V:Values){auto Q=Base;Q.JumpHeight=V.H;Q.VerticalVelocity=V.V;Q.LandingVisualAge=V.Age;Check(Q,V.Expected);}
 Base.JumpHeight=54.f;Base.VerticalVelocity=450.f;
 for(int Domain=0;Domain<10;++Domain)
 {
  auto Q=Base;switch(Domain){case 0:Q.Valid=false;break;case 1:Q.RunGuid={};break;case 2:Q.OwnerId=0;break;case 3:Q.RoomInstanceId=0;break;
   case 4:Q.NativeTime=-1.;break;case 5:Q.NativeTime=std::numeric_limits<double>::infinity();break;case 6:Q.GroundPosition.X=std::numeric_limits<double>::quiet_NaN();break;
   case 7:Q.Facing=0.f;break;case 8:Q.Facing=2.f;break;case 9:Q.LandingVisualAge=std::numeric_limits<float>::quiet_NaN();break;}
  Check(Q,-1);
 }
 for(float Face:{-1.f,1.f}){auto Q=Base;Q.Facing=Face;Check(Q,0);}
 std::cout<<"{\"actual_select_cpp_cases\":"<<Cases<<",\"failed\":"<<Failed<<",\"scope\":\"standalone actual Select CPP with harness types; no UE/native-owner/resource/art claim\"}\n";
 return Failed?1:0;
}

std::string Signature(const A::FDrawPlan& P)
{
 std::ostringstream S;S<<std::setprecision(17)<<P.Supported<<P.Frame<<P.Facing<<P.NonemptyDrawCount<<int(P.Pose)<<P.ProfileId.Value;
 S<<P.CanvasSize<<P.SourceToScreenScale<<P.WeaponScale<<P.WeaponWidth<<P.WeaponAngle<<P.TextureU<<P.TextureDU;
 const auto& Q=P.Sample;S<<Q.Valid<<Q.RunGuid.A<<Q.RunGuid.B<<Q.RunGuid.C<<Q.RunGuid.D<<Q.OwnerId<<Q.RoomInstanceId<<Q.PresentationEpoch<<Q.NativeTime<<Q.GroundPosition.X<<Q.GroundPosition.Y<<Q.Facing<<Q.JumpHeight<<Q.VerticalVelocity<<Q.LandingVisualAge;
 const auto& B=P.Binding;S<<B.RunGuid.A<<B.RunGuid.B<<B.RunGuid.C<<B.RunGuid.D<<B.RunAlias<<B.OwnerId<<B.Revision<<B.ActiveSlot<<B.WeaponInstanceId<<B.WeaponVersion<<B.ArmorInstanceId<<B.ArmorVersion<<B.WeaponContentId.Value<<B.ArmorContentId.Value<<int(B.Armor);
 for(const auto V:{P.RootSource,P.GripSource,P.AxisArtist,P.BodyTop,P.GripScreen,P.SwordTop,P.SwordPivotUV})S<<V.X<<V.Y;
 S<<P.Tint.R<<P.Tint.G<<P.Tint.B<<P.Tint.A;
 for(const auto& Slot:P.Slots)S<<int(Slot.Component)<<Slot.Enabled<<Slot.KnownOptionalEmpty<<Slot.TexturePath.Value;
 return S.str();
}
int main()
{
 if(RunSelectCases())return 1;
 int Cases=0,Failed=0;
 const auto Check=[&](bool Pass,const char* Label){++Cases;if(!Pass){++Failed;std::cerr<<Cases<<" "<<Label<<" failed\n";}};
 DungeonFairytaleSwordEquipmentBinding::FBinding Binding;Binding.RunGuid.A=1;Binding.RunAlias=1;Binding.OwnerId=17;Binding.Revision=2;Binding.ActiveSlot=0;Binding.WeaponInstanceId=19;Binding.WeaponVersion=3;Binding.WeaponContentId="WPN-SWD-001";
 FDungeonHeroAirSample Sample;Sample.Valid=true;Sample.RunGuid=Binding.RunGuid;Sample.OwnerId=17;Sample.RoomInstanceId=7;Sample.NativeTime=12.;Sample.Facing=1.f;Sample.JumpHeight=54.f;Sample.VerticalVelocity=450.f;
 A::FDrawContext Context;Context.GroundScreen={640.125,490.25};Context.JumpHeight=Sample.JumpHeight;
 A::FDrawPlan Out;Out.Supported=true;Out.Frame=91;Out.Facing=17;Out.ProfileId="sentinel";Out.Sample.NativeTime=927.;Out.GripScreen={73.,74.};Out.Slots[0].TexturePath="sentinel.texture";const auto Before=Signature(Out);FString Why;
 Check(A::Profile().SourceClosureVerified,"real retained-source preparation is present");
 Check(A::Profile().Frames[2].Root.Y==530.,"actual virtual Apex projection origin remains outside canvas");
 struct Physical{float H,V,Age;};const Physical Poses[]={{0.f,630.f,.01f},{90.f,200.f,.12f},{110.25f,0.f,.12f},{12.f,-500.f,.12f},{0.f,0.f,0.f},{0.f,0.f,.06f}};
 for(bool Light:{false,true})for(float Face:{-1.f,1.f})for(double UI:{.75,1.,1.5})for(int Pose=0;Pose<6;++Pose)
 {
  auto B=Binding;B.Armor=Light?DungeonFairytaleSwordEquipmentBinding::EArmor::LightArmor:DungeonFairytaleSwordEquipmentBinding::EArmor::NoArmor;
  if(Light){B.ArmorInstanceId=21;B.ArmorVersion=2;B.ArmorContentId="ARM-LGT-001";}
  auto Q=Sample;Q.Facing=Face;Q.JumpHeight=Poses[Pose].H;Q.VerticalVelocity=Poses[Pose].V;Q.LandingVisualAge=Poses[Pose].Age;
  auto C=Context;C.UIScale=UI;C.JumpHeight=Q.JumpHeight;C.Tint=FLinearColor(1.7f,.6f,.4f,1.f);
  A::FDrawPlan Plan;const bool Ok=A::BuildDrawPlanFromCommitted(B,Q,A::Profile(),C,Plan,Why);
  const auto& Frame=A::Profile().Frames[Pose];const double Scale=72./416.*UI,Width=72.*512./416.*.5*UI;
  const FVector2D Lift(0.,double(Q.JumpHeight)*.70*UI);
  const FVector2D Top(C.GroundScreen.X-(Face<0?512.-Frame.Root.X:Frame.Root.X)*Scale,C.GroundScreen.Y-Lift.Y-Frame.Root.Y*Scale);
  const FVector2D Grip(C.GroundScreen.X+Face*(Frame.Grip.X-Frame.Root.X)*Scale,C.GroundScreen.Y-Lift.Y+(Frame.Grip.Y-Frame.Root.Y)*Scale);
  const auto ComponentGrip=A::Profile().ComponentGrip;const FVector2D Pivot(Face<0?1.-ComponentGrip.X/512.:ComponentGrip.X/512.,ComponentGrip.Y/512.);
  bool Pass=Ok&&Why.IsEmpty()&&Plan.Supported&&Plan.Frame==Pose&&int(Plan.Pose)==Pose+1&&Plan.Facing==int(Face)&&Plan.NonemptyDrawCount==(Light?9:6)
   &&Plan.RootSource==Frame.Root&&Plan.GripSource==Frame.Grip&&Plan.AxisArtist==Frame.AxisArtist&&Plan.BodyTop.Equals(Top,1.e-10)&&Plan.GripScreen.Equals(Grip,1.e-10)
   &&std::abs(Plan.CanvasSize-72.*512./416.)<1.e-12&&std::abs(Plan.SourceToScreenScale-Scale)<1.e-12&&Plan.WeaponWidth==Width
   &&Plan.SwordPivotUV==Pivot&&Plan.SwordTop.Equals(Grip-Pivot*Width,1.e-10)&&Plan.Tint==C.Tint&&Plan.TextureU==(Face<0?1.:0.)&&Plan.TextureDU==double(Face);
  int Enabled=0;for(int Slot=0;Slot<9;++Slot){const auto& V=Plan.Slots[Slot];const bool Armor=V.Component==A::EComponent::ShoulderFar||V.Component==A::EComponent::Chest||V.Component==A::EComponent::ShoulderNear;
   Pass=Pass&&V.Component==Frame.SlotOrder[Slot]&&V.Enabled==(Light||!Armor)&&!V.KnownOptionalEmpty&&!V.TexturePath.IsEmpty();Enabled+=V.Enabled?1:0;}
  Pass=Pass&&Enabled==(Light?9:6);
  // Native DrawTexture pivot is invariant under rotation. Mirrored source +
  // negative left angle maps intrinsic sword +X into reflected artist axis.
  const double R=Plan.WeaponAngle*3.14159265358979323846/180.;const FVector2D Axis(Face*std::cos(R),Face*std::sin(R));
  const double Len=std::hypot(Frame.AxisArtist.X,Frame.AxisArtist.Y);
  Pass=Pass&&Axis.Equals({Face*Frame.AxisArtist.X/Len,Frame.AxisArtist.Y/Len},1.e-12);
  Check(Pass,"6poses x None/LGT x both facings x 3UI shared actual source profile geometry");
 }
 const auto RejectPlan=[&](auto B,auto Q,auto Source,auto C,const char* Label){Out=A::FDrawPlan{};Out.Supported=true;Out.Frame=91;Out.ProfileId="sentinel";Out.Sample.NativeTime=927.;Out.GripScreen={73.,74.};Out.Slots[0].TexturePath="sentinel.texture";const auto Sig=Signature(Out);Check(!A::BuildDrawPlanFromCommitted(B,Q,Source,C,Out,Why)&&Signature(Out)==Sig&&!Why.IsEmpty(),Label);};
 for(int Field=0;Field<21;++Field)
 {
  auto B=Binding;auto Q=Sample;auto P=A::Profile();auto C=Context;
  switch(Field){case 0:B.OwnerId=0;break;case 1:B.WeaponContentId="WPN-XBW-001";break;case 2:B.Revision=std::numeric_limits<uint64>::max();break;
   case 3:Q.OwnerId=18;break;case 4:Q.RunGuid.A=2;break;case 5:Q.Valid=false;break;case 6:P.SourceClosureVerified=false;break;case 7:P.SourceClosureSHA256="bad";break;
   case 8:P.Frames[0].Layers[0].TexturePath.Reset();break;case 9:P.Frames[2].Layers[6].KnownOptionalEmpty=true;break;
   case 10:P.Frames[3].AxisArtist={};break;case 11:P.Frames[0].Root.X+=1.;break;case 12:std::swap(P.Frames[0].SlotOrder[0],P.Frames[0].SlotOrder[1]);break;
   case 13:P.Frames[0].Layers[1].SourceRGBASHA256="bad";break;case 14:C.GroundScreen={1.e20,1.e20};break;case 15:C.UIScale=0.;break;
   case 16:C.UIScale=std::numeric_limits<double>::infinity();break;case 17:C.JumpHeight+=1.;break;case 18:C.Tint.R=std::numeric_limits<float>::quiet_NaN();break;
   case 19:C.GroundScreen.Y=std::numeric_limits<double>::quiet_NaN();break;case 20:Q.LandingVisualAge=-.01f;break;}
  RejectPlan(B,Q,P,C,"invalid binding/sample/source/context atomically preserves all Out fields");
 }
 TArray<A::FResidentTexture> Residents;
 for(const auto& Frame:A::Profile().Frames)for(const auto& Layer:Frame.Layers)Residents.Add({Layer.TexturePath,"Texture2D",512,512,true,false});
 Residents.Add({A::Profile().SwordTexturePath,"Texture2D",512,512,true,false});
 Check(A::ValidateResidentSet(A::Profile(),Residents,Why)&&Residents.Num()==49&&Why.IsEmpty(),"complete49 explicit value facts admit preflight seam");
 for(int I=0;I<49;++I){auto Bad=Residents;Bad[size_t(I)].ResourceReady=false;Check(!A::ValidateResidentSet(A::Profile(),Bad,Why),"every one-of49 missing resource closes");}
 for(int Field=0;Field<7;++Field){auto Bad=Residents;switch(Field){case 0:Bad[1].TexturePath=Bad[0].TexturePath;break;case 1:Bad[0].ClassName="TextureCube";break;
  case 2:Bad[0].Width=256;break;case 3:Bad[0].Height=256;break;case 4:Bad[0].PendingInitialization=true;break;case 5:Bad.pop_back();break;case 6:Bad[0].TexturePath="other";break;}
  Check(!A::ValidateResidentSet(A::Profile(),Bad,Why),"invalid count/path/class/dimension/pending closes complete49");}
 HostBinding=Binding;ADungeonGameMode Game;Game.Time=Sample.NativeTime;ADungeonFighter Fighter;Fighter.Sample=Sample;Fighter.JumpHeight=Sample.JumpHeight;
 Check(A::BuildDrawPlan(Game,Fighter,Context,Out,Why),"actual-entry API-shape harness calls real query/committed plan");
 auto OutBefore=Signature(Out);Game.Epoch=1;Check(!A::BuildDrawPlan(Game,Fighter,Context,Out,Why)&&Signature(Out)==OutBefore,"stale epoch atomically rejects");Game.Epoch=0;
 Game.Time+=.01;Check(!A::BuildDrawPlan(Game,Fighter,Context,Out,Why)&&Signature(Out)==OutBefore,"stale native time atomically rejects");Game.Time=Sample.NativeTime;
 Fighter.HitFlash=1.f;Check(!A::BuildDrawPlan(Game,Fighter,Context,Out,Why)&&Signature(Out)==OutBefore,"wrong actual tint rejects");Context.Tint={1.7f,.6f,.4f,1.f};
 Check(A::BuildDrawPlan(Game,Fighter,Context,Out,Why)&&Out.Tint==Context.Tint,"ordinary real hit tint remains accepted");OutBefore=Signature(Out);
 FParse::Enabled=false;Check(!A::BuildDrawPlan(Game,Fighter,Context,Out,Why)&&Signature(Out)==OutBefore,"missing explicit opt-in closes");FParse::Enabled=true;
 std::cout<<"{\"actual_full_cpp_value_cases\":"<<Cases<<",\"failed\":"<<Failed<<",\"real_source_table\":true,\"scope\":\"actual CPP + actual API headers + retained author table; actor/resource facts are stand-ins, no UE/native/GPU claim\"}\n";
 return Failed?1:0;
}
