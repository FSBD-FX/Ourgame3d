#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonXBWBodyPose.h"
#include <limits>

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonXBWPrimaryClockTest,
    "CodexDungeon.FirstRoom.XBWPrimaryBodyAcceptedClock",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FDungeonXBWPrimaryClockTest::RunTest(const FString&)
{
    using namespace DungeonWeaponActions;
    FState S;
    S.Action.Active=true; S.Action.Type=EAction::Primary;
    S.Action.Weapon=DungeonContentCombat::EWeapon::XBW001;
    S.Action.Start=10.; S.Action.ActiveAt=10.16; S.Action.ActiveEnd=10.20; S.Action.End=10.68;
    const double Times[]={10.,10.079,10.08,10.159,10.16,10.179,10.18,10.199,10.20,10.439,10.44,10.679};
    const int Frames[]={0,0,1,1,2,2,3,3,4,4,5,5};
    for(int I=0;I<12;++I)
    {
        S.Time=Times[I]; DungeonXBWBodyPose::FPose P;
        TestTrue(FString::Printf(TEXT("accepted primary sample %d"),I),DungeonXBWBodyPose::Primary(S,P));
        TestEqual(FString::Printf(TEXT("half-open phase frame %d"),I),P.Frame,Frames[I]);
    }
    // Produce a legal +20% action through the actual kernel, not invented times.
    FWeaponActionsKernel Fast(DungeonContentCombat::EWeapon::XBW001,7,1,100);
    FContext Context;Context.ActionSpeedPct=20.;
    if(!TestTrue(TEXT("actual kernel accepts legal accelerated primary"),Fast.TryStart(EAction::Primary,0.,Context)))return false;
    const double Midpoint=(Fast.State().Action.ActiveAt+Fast.State().Action.ActiveEnd)*.5;
    Fast.StepTo(Midpoint,Context); S=Fast.State(); DungeonXBWBodyPose::FPose P;
    TestTrue(TEXT("modified Actor clock accepted"),DungeonXBWBodyPose::Primary(S,P));
    TestEqual(TEXT("modified active second pose"),P.Frame,3);
    TestTrue(TEXT("frozen grip and angle sampled together"),P.GripX==250. && P.GripY==267. && P.Angle==-11.266152277695031 && P.Scale==.48);
    S.Time=S.Action.End;
    TestFalse(TEXT("completion endpoint belongs to next state"),DungeonXBWBodyPose::Primary(S,P));
    S.Time=Midpoint; S.Action.Type=EAction::Reload;
    TestFalse(TEXT("reload cannot be mislabeled primary"),DungeonXBWBodyPose::Primary(S,P));
    S.Action.Type=EAction::Primary; S.Action.StartedAirborne=true;
    TestFalse(TEXT("ground-only source cannot admit airborne action"),DungeonXBWBodyPose::Primary(S,P));
    S.Action.StartedAirborne=false; S.Time=std::numeric_limits<double>::quiet_NaN();
    TestFalse(TEXT("nonfinite clock rejected"),DungeonXBWBodyPose::Primary(S,P));
    S.Time=Midpoint; S.Action.Weapon=DungeonContentCombat::EWeapon::STF001;
    TestFalse(TEXT("another weapon cannot reuse this body contract"),DungeonXBWBodyPose::Primary(S,P));
    S.Action.Weapon=DungeonContentCombat::EWeapon::XBW001; S.Action.Active=false;
    TestFalse(TEXT("completed stored action cannot keep drawing a primary"),DungeonXBWBodyPose::Primary(S,P));
    return true;
}
#endif
