// Optional actual ForwardStep commit witness on the existing transient journal.
// Source key = this EventId/SubhitId plus the parent record's Run/Room/Owner/Action/Instance.
struct FDungeonActionAudioForwardStepV001
{
    bool Present = false;
    uint64 EventId = 0;
    uint32 SubhitId = 0;
    double RequestedSignedDistance = 0.0;
    FVector2D Before{0.,0.}, After{0.,0.}, CommittedDelta{0.,0.};
};

namespace DungeonHeroForwardStepAudioV001
{
// Reads the real post-placement result. No movement, cadence, IDs or clocks are created.
inline bool Eligible(const DungeonWeaponActions::FEvent& E,const DungeonWeaponActions::FAction& Current,
    uint64 Owner,uint64 ExpectedOwner,bool ActiveGroundedScope,double Now,FVector2D Before,FVector2D After)
{
    using namespace DungeonWeaponActions;
    if(!ActiveGroundedScope||!Owner||Owner!=ExpectedOwner||E.Kind!=EEvent::ForwardStep||!E.EventId
        ||!E.ActionId||!E.InstanceId||E.Action.Type!=EAction::Skill||E.Action.Weapon!=EWeapon::SWD001
        ||!E.Action.Active||!E.Action.Locked||E.Action.StartedAirborne||!E.Action.ForwardStepIssued
        ||E.ActionId!=E.Action.ActionId||E.InstanceId!=E.Action.InstanceId
        ||Current.Type!=EAction::Skill||Current.Weapon!=EWeapon::SWD001||!Current.Active||!Current.Locked
        ||Current.StartedAirborne||!Current.ForwardStepIssued||!Current.NextSubhit||Current.Terminal==EEvent::Interrupted
        ||Current.ActionId!=E.ActionId||Current.InstanceId!=E.InstanceId
        ||Current.Start!=E.Action.Start||Current.ActiveAt!=E.AtTime||E.Action.ActiveAt!=E.AtTime
        ||!std::isfinite(E.AtTime)||E.AtTime<0.||!std::isfinite(Now)||Now<E.AtTime||Now-E.AtTime>.25
        ||!std::isfinite(E.ForwardStep)||E.ForwardStep==0.
        ||!std::isfinite(Before.X)||!std::isfinite(Before.Y)||!std::isfinite(After.X)||!std::isfinite(After.Y))return false;
    const double DX=After.X-Before.X,DY=After.Y-Before.Y,DistanceSquared=DX*DX+DY*DY;
    return std::isfinite(DistanceSquared)&&DistanceSquared>1.e-8;
}
}

