#pragma once
#include "DungeonWeaponActions.h"
#include <array>
#include <cstring>
namespace DungeonFairytaleSwordSecondaryV001
{
// Eight action frames and eight possible draw slots are independent counts.
inline constexpr int FrameCount=8,LayerCount=7,SlotCount=8,ClosureCount=57;
inline constexpr double CanvasSize=72.*512./416.,WeaponScale=.50;
enum class EArmor {None,Light,Unsupported};
enum class EDecision {PassThrough,Closed,Sampled};
enum class EReason {None,PriorityOrGround,Clock,ActionIdentity,Deadlines,Phase};
enum class EComponent {BodyRest,ShoulderFar,Chest,NearArmWithoutHand,ShoulderNear,HelmetForeground,IndependentSword,NearHand};
struct FContext
{
 bool OptIn=false,EquipmentBound=false,OwnerAuthorized=false,Grounded=false;
 bool Dead=false,Hurt=false,Dodging=false,Equipping=false,MeleeActive=false;
 std::uint64_t BoundWeaponInstanceId=0;
 double WeaponTime=0,StateTime=0,SimulationTime=0,Height=0,VerticalVelocity=0;
 EArmor Armor=EArmor::Unsupported;
};
struct FSample
{
 EDecision Decision=EDecision::PassThrough;EReason Reason=EReason::None;
 int Frame=-1,Facing=0;double SampleTime=0.;
 DungeonWeaponActions::FAction Action;
 std::array<double,9> Boundaries{};
};
// Root must replace Profile()'s unadmitted default with the measured, pinned
// 8-frame data. These fields are metadata, not a way to load external files.
struct FSourcePin {const char* SourceRelativePath=nullptr;const char* Sha256=nullptr;std::uint64_t Bytes=0;};
struct FLayer {const char* TexturePath=nullptr;FSourcePin Source;};
struct FPoint {double X=0,Y=0;};
struct FFrame {FPoint Root,Grip,Axis;std::array<FLayer,7> Layers;};
struct FProfile {bool RuntimeReady=false;const char* ProfileId=nullptr;const char* SourceContractSha256=nullptr;std::array<FFrame,8> Frames;FLayer Sword;};
struct FGeometryContext {FPoint GroundScreen;double UIScale=1.;};
struct FGeometry {FPoint BodyTop,GripScreen,SwordTop,SwordPivot;double BodyWidth=0.,SwordWidth=0.,Angle=0.,U=0.,DU=1.;};
inline bool Finite(double N){return std::isfinite(N);}
inline bool Geometry(const FFrame& F,int Facing,const FGeometryContext& C,FGeometry& Out)
{
 if((Facing!=1&&Facing!=-1)||!Finite(C.GroundScreen.X)||!Finite(C.GroundScreen.Y)
  ||!Finite(C.UIScale)||C.UIScale<=0.||F.Root.X!=256.||F.Root.Y!=464.
  ||!Finite(F.Grip.X)||!Finite(F.Grip.Y)||!Finite(F.Axis.X)||!Finite(F.Axis.Y)
  ||F.Axis.X*F.Axis.X+F.Axis.Y*F.Axis.Y<1.e-12)return false;
 FGeometry G;G.BodyWidth=CanvasSize*C.UIScale;G.SwordWidth=G.BodyWidth*WeaponScale;
 const double Scale=G.BodyWidth/512.;const double DisplayRootX=Facing<0?512.-F.Root.X:F.Root.X;
 G.BodyTop={C.GroundScreen.X-DisplayRootX*Scale,C.GroundScreen.Y-F.Root.Y*Scale};
 G.GripScreen={C.GroundScreen.X+Facing*(F.Grip.X-F.Root.X)*Scale,C.GroundScreen.Y+(F.Grip.Y-F.Root.Y)*Scale};
 G.Angle=std::atan2(F.Axis.Y,F.Axis.X)*180./std::acos(-1.)*(Facing<0?-1.:1.);
 G.U=Facing<0?1.:0.;G.DU=Facing<0?-1.:1.;
 G.SwordPivot={Facing<0?1.-99./512.:99./512.,256./512.};
 G.SwordTop={G.GripScreen.X-G.SwordPivot.X*G.SwordWidth,G.GripScreen.Y-G.SwordPivot.Y*G.SwordWidth};
 for(double N:{G.BodyTop.X,G.BodyTop.Y,G.GripScreen.X,G.GripScreen.Y,G.SwordTop.X,G.SwordTop.Y,G.BodyWidth,G.SwordWidth,G.Angle})
  if(!Finite(N))return false;
 Out=G;return true;
}
inline FSample Sample(const DungeonWeaponActions::FAction& A,const FContext& C)
{
 using namespace DungeonWeaponActions;
 FSample R;
 // Off/unsupported/non-skill leaves the old presenter byte-for-byte reachable.
 if(false||!C.EquipmentBound||!C.OwnerAuthorized||C.Armor==EArmor::Unsupported
  ||!A.Active||A.Type!=EAction::Skill)return R;
 R.Decision=EDecision::Closed;R.Action=A;R.SampleTime=C.WeaponTime;
 if(C.Dead||C.Hurt||C.Dodging||C.Equipping||C.MeleeActive||!C.Grounded
  ||!Finite(C.Height)||!Finite(C.VerticalVelocity)||C.Height!=0.||C.VerticalVelocity!=0.)
 {R.Reason=EReason::PriorityOrGround;return R;}
 if(!Finite(C.WeaponTime)||!Finite(C.StateTime)||!Finite(C.SimulationTime)
  ||C.WeaponTime!=C.StateTime||C.WeaponTime!=C.SimulationTime)
 {R.Reason=EReason::Clock;return R;}
 if(A.Weapon!=EWeapon::SWD001||!A.ActionId||!A.InstanceId||A.InstanceId!=C.BoundWeaponInstanceId
  ||A.StartedAirborne||!Finite(A.Facing)||(A.Facing!=1.&&A.Facing!=-1.)
  ||!Finite(A.SpeedPct)||A.SpeedPct < -20.||A.SpeedPct>20.)
 {R.Reason=EReason::ActionIdentity;return R;}
 for(double N:{A.Start,A.LockAt,A.ActiveAt,A.ActiveEnd,A.End})if(!Finite(N))
 {R.Reason=EReason::Deadlines;return R;}
 if(A.Start<0.||!(A.Start<A.LockAt&&A.LockAt<A.ActiveAt&&A.ActiveAt<A.ActiveEnd&&A.ActiveEnd<A.End)
  ||C.WeaponTime<A.Start||!(C.WeaponTime<A.End)
  ||std::abs((A.LockAt-A.Start)-.4*(A.ActiveAt-A.Start))>1.e-9)
 {R.Reason=EReason::Deadlines;return R;}
 const auto Phase=C.WeaponTime<A.ActiveAt?EPhase::Windup:C.WeaponTime<A.ActiveEnd?EPhase::Active:EPhase::Recovery;
 if(A.Phase!=Phase||A.Locked!=(C.WeaponTime>=A.LockAt))
 {R.Reason=EReason::Phase;return R;}
 // LockAt is authoritative. The remaining 60% windup is two equal 30%s;
 // active is 50/50 and recovery is 12/38,13/38,13/38. No FPS or new clock.
 const double Recovery=A.End-A.ActiveEnd;
 R.Boundaries={A.Start,A.LockAt,A.LockAt+(A.ActiveAt-A.LockAt)*.5,A.ActiveAt,
  A.ActiveAt+(A.ActiveEnd-A.ActiveAt)*.5,A.ActiveEnd,
  A.ActiveEnd+Recovery*(12./38.),A.ActiveEnd+Recovery*(25./38.),A.End};
 for(int I=0;I<FrameCount;++I)if(C.WeaponTime<R.Boundaries[I+1])
 {R.Frame=I;R.Facing=A.Facing<0.?-1:1;R.Decision=EDecision::Sampled;return R;}
 R.Reason=EReason::Deadlines;return R;
}
inline bool SelectedSlot(EArmor Armor,int Slot)
{
 return Slot>=0&&Slot<SlotCount&&(Armor==EArmor::Light
  ||(Armor==EArmor::None&&Slot!=1&&Slot!=2&&Slot!=4));
}
inline int SelectedSlotCount(EArmor Armor){return Armor==EArmor::Light?8:Armor==EArmor::None?5:0;}
inline bool AllResident(const std::array<bool,ClosureCount>& Resident)
{
 for(bool Ready:Resident)if(!Ready)return false;
 return true;
}
inline bool HasText(const char* S){return S&&*S;}
inline bool ValidSha(const char* S)
{
 if(!S||std::strlen(S)!=64)return false;
 for(const char* P=S;*P;++P)if(!(*P>='0'&&*P<='9')&&!(*P>='a'&&*P<='f'))return false;
 return true;
}
inline bool ValidSource(const FSourcePin& P)
{
 return P.Bytes&&ValidSha(P.Sha256)&&HasText(P.SourceRelativePath)
  &&std::strncmp(P.SourceRelativePath,"source-assets/",14)==0
  &&!std::strstr(P.SourceRelativePath,"..")&&!std::strchr(P.SourceRelativePath,'\\')&&!std::strchr(P.SourceRelativePath,':');
}
inline bool ValidTexturePath(const char* S)
{
 if(!HasText(S)||std::strncmp(S,"/Game/Production/",17)!=0||std::strstr(S,"..")||std::strchr(S,'\\')||std::strchr(S,':'))return false;
 const char* Slash=std::strrchr(S,'/');const char* Dot=std::strrchr(S,'.');
 return Slash&&Dot&&Dot>Slash+1&&*(Dot+1)&&std::strlen(Dot+1)==std::size_t(Dot-Slash-1)
  &&std::strncmp(Slash+1,Dot+1,std::size_t(Dot-Slash-1))==0;
}
inline bool ProfileValid(const FProfile& P)
{
 if(!P.RuntimeReady||!HasText(P.ProfileId)||!ValidSha(P.SourceContractSha256)
  ||!ValidTexturePath(P.Sword.TexturePath)||!ValidSource(P.Sword.Source))return false;
 for(const auto& F:P.Frames)
 {
  if(F.Root.X!=256.||F.Root.Y!=464.||!Finite(F.Grip.X)||!Finite(F.Grip.Y)
   ||F.Grip.X<0.||F.Grip.X>512.||F.Grip.Y<0.||F.Grip.Y>512.
   ||!Finite(F.Axis.X)||!Finite(F.Axis.Y)||F.Axis.X*F.Axis.X+F.Axis.Y*F.Axis.Y<1.e-12)return false;
  for(const auto& L:F.Layers)if(!ValidTexturePath(L.TexturePath)||!ValidSource(L.Source))return false;
 }
 return true;
}
// This source candidate has NO final data. Do not change the gate alone.
// Root replaces the entire measured profile only after its separate asset review.
const FProfile& Profile();
}
