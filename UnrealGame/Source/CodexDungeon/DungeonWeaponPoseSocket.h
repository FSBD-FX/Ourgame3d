#pragma once

#include "DungeonWeaponActions.h"
#include "DungeonXBWBodyPose.h"
#include "DungeonPresentationScale.h"

// Actor-owned native image geometry. Combat height remains the real jump plane;
// presentation height is a separate physical component/display coordinate.
namespace DungeonWeaponPoseSocket
{
enum class EClip { None, Ready, Primary, Reload };

struct FResolved
{
    bool Supported = false;
    bool CustomOverride = false;
    bool GroundPoseFallback = false;
    EClip Clip = EClip::None;
    int Frame = -1;
    int WeaponStateIndex = -1; // -1 original neutral; 0..3 frozen native states.
    double SampleTime = 0.;
    std::uint64_t InstanceId = 0, ActionId = 0;
    double Facing = 1.;
    double RootX = 256., RootY = 472., BodySize = DungeonPresentationScale::CandidateBodySize;
    double GripX = 0., GripY = 0., SupportX = 0., SupportY = 0.;
    double ComponentSupportX = 0., ComponentSupportY = 0.;
    double ComponentEmitX = 0., ComponentEmitY = 0.;
    double ComponentGripX = 0., ComponentGripY = 0.;
    double EmitX = 0., EmitY = 0., Angle = 0., Scale = .48;
    DungeonWeaponActions::FOrigin ActorOrigin;
    DungeonWeaponActions::FOrigin CombatOrigin;
    DungeonWeaponActions::FOrigin PresentationOrigin;
};

inline bool Resolve(const DungeonWeaponActions::FState& State,double At,double AnimationTime,FResolved& Out)
{
    using namespace DungeonWeaponActions;
    Out={};Out.SampleTime=At;Out.InstanceId=State.EquippedId;
    Out.ActionId=State.Action.Active?State.Action.ActionId:0;
    if(!std::isfinite(At)||At<State.Time||!std::isfinite(AnimationTime)||AnimationTime<0.||State.Budget.Dead)return false;
    const FInstance* Instance=nullptr;
    for(const auto& I:State.Instances)if(I.InstanceId==State.EquippedId){Instance=&I;break;}
    if(!Instance||Instance->Weapon!=DungeonContentCombat::EWeapon::XBW001)return false;
    FState Clock;Clock.Time=At;Clock.Action=State.Action;
    Out.Supported=true;Out.Clip=EClip::Ready;Out.Frame=int(std::fmod(std::floor(AnimationTime/.15),6.));
    Out.GripX=224.;Out.GripY=316.;Out.Angle=-5.;
    DungeonXBWBodyPose::FPose Primary;DungeonXBWBodyPose::FReloadPose Reload;
    const bool IsPrimary=DungeonXBWBodyPose::Primary(Clock,Primary);
    const bool IsReload=DungeonXBWBodyPose::Reload(Clock,Reload);
    if(IsPrimary)
    {
        Out.Clip=EClip::Primary;Out.Frame=Primary.Frame;Out.GripX=Primary.GripX;
        Out.GripY=Primary.GripY;Out.Angle=Primary.Angle;Out.Scale=Primary.Scale;
    }
    else if(IsReload)
    {
        Out.Clip=EClip::Reload;Out.Frame=Reload.Frame;Out.Angle=Reload.Angle;Out.Scale=Reload.Scale;
    }
    else Out.GroundPoseFallback=State.Action.Active&&State.Action.Type!=EAction::Reload;
    // Initial loaded sources use their original neutral component. Only real
    // receipts change that instance's cosmetic component state, across switches.
    bool Reloaded=false;
    for(const auto& H:State.WeaponRuntimeHistory)if(H.Action.InstanceId==Instance->InstanceId
        &&H.Kind==EWeaponMutation::ReloadCompleted){Reloaded=true;break;}
    Out.WeaponStateIndex=IsReload?Reload.Frame:Instance->Ammo<=0.?0:Reloaded?3:-1;
    Out.ComponentGripX=Out.WeaponStateIndex<0?128.:138.;
    Out.ComponentGripY=Out.WeaponStateIndex<0?253.:Out.WeaponStateIndex<2?308.:274.;
    Out.ComponentSupportX=Out.WeaponStateIndex<0?337.:344.;
    Out.ComponentSupportY=Out.WeaponStateIndex<0?282.:Out.WeaponStateIndex<2?320.:286.;
    Out.ComponentEmitX=Out.WeaponStateIndex<0?489.:506.;
    Out.ComponentEmitY=Out.WeaponStateIndex<0?224.:Out.WeaponStateIndex<2?263.:229.;
    if(!IsReload&&Out.WeaponStateIndex>=0)
    {
        // Frozen94f2 lifecycle fit: exact stock anchor; original hand pixels
        // and fixed .48 scale, with the measured support residual preserved.
        constexpr double StateAngles[]={-.4997396452300605,-2.2105479474611447,-5.035205266862698,
            -6.700311324966375,-2.199429030559567,-.4997396452300605};
        Out.Angle=IsPrimary?StateAngles[Out.Frame]:StateAngles[0];
    }
    const double R=Out.Angle*3.14159265358979323846/180.,C=std::cos(R),S=std::sin(R);
    const auto X=[&](double DX,double DY){return Out.Scale*(DX*C-DY*S);};
    const auto Y=[&](double DX,double DY){return Out.Scale*(DX*S+DY*C);};
    if(IsReload)
    {
        Out.ComponentSupportX=Reload.ComponentSupportX;Out.ComponentSupportY=Reload.ComponentSupportY;
        Out.SupportX=Reload.BodySupportX;Out.SupportY=Reload.BodySupportY;
        Out.GripX=Out.SupportX+X(Out.ComponentGripX-Out.ComponentSupportX,Out.ComponentGripY-Out.ComponentSupportY);
        Out.GripY=Out.SupportY+Y(Out.ComponentGripX-Out.ComponentSupportX,Out.ComponentGripY-Out.ComponentSupportY);
    }
    else
    {
        Out.SupportX=Out.GripX+X(Out.ComponentSupportX-Out.ComponentGripX,Out.ComponentSupportY-Out.ComponentGripY);
        Out.SupportY=Out.GripY+Y(Out.ComponentSupportX-Out.ComponentGripX,Out.ComponentSupportY-Out.ComponentGripY);
    }
    Out.EmitX=Out.GripX+X(Out.ComponentEmitX-Out.ComponentGripX,Out.ComponentEmitY-Out.ComponentGripY);
    Out.EmitY=Out.GripY+Y(Out.ComponentEmitX-Out.ComponentGripX,Out.ComponentEmitY-Out.ComponentGripY);
    return true;
}
}
