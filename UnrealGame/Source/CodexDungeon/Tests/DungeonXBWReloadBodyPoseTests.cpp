#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonXBWBodyPose.h"
#include <limits>

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonXBWReloadBodyPose,
    "CodexDungeon.FirstRoom.XBWReloadBodyAcceptedClock",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonXBWReloadBodyPose::RunTest(const FString&)
{
    using namespace DungeonWeaponActions;
    using DungeonXBWBodyPose::FReloadPose;
    FWeaponActionsKernel K(DungeonContentCombat::EWeapon::XBW001,7,0,100);
    FContext C;
    if(!TestTrue(TEXT("actual empty crossbow starts reload"),K.PressReload(0.,C)))return false;
    const double Times[]={0.,.199,.2,.599,.6,.849,.85,1.099};
    const int Frames[]={0,0,1,1,2,2,3,3};
    for(int I=0;I<8;++I)
    {
        K.StepTo(Times[I],C); FReloadPose P;
        const bool Valid=DungeonXBWBodyPose::Reload(K.State(),P);
        TestTrue(FString::Printf(TEXT("actual accepted reload sample %d"),I),Valid);
        if(Valid)TestEqual(FString::Printf(TEXT("half-open source hold %d"),I),P.Frame,Frames[I]);
        TestTrue(TEXT("visible inserted bolt never refills instance before commit"),K.State().Instances[0].Ammo==0);
    }
    FReloadPose P;
    auto NearEnd=K.State();NearEnd.Time=NearEnd.Action.End;
    TestFalse(TEXT("completion endpoint is no longer a reload image"),DungeonXBWBodyPose::Reload(NearEnd,P));
    K.StepTo(1.1,C);
    TestTrue(TEXT("real completion alone fills magazine"),K.State().Instances[0].Ammo==1);
    TestFalse(TEXT("inactive stored reload cannot keep old pose"),DungeonXBWBodyPose::Reload(K.State(),P));
    FWeaponActionsKernel Fast(DungeonContentCombat::EWeapon::XBW001,8,0,100);
    C.ReloadSpeedPct=20.;
    if(!TestTrue(TEXT("actual kernel accepts legal faster reload"),Fast.PressReload(0.,C)))return false;
    Fast.StepTo(Fast.State().Action.End*(.61/1.1),C);
    TestTrue(TEXT("actual modified duration normalizes into insertion pose"),DungeonXBWBodyPose::Reload(Fast.State(),P));
    TestEqual(TEXT("modified reload remains frame2"),P.Frame,2);
    TestTrue(TEXT("pose uses support hand, not invented early stock grip"),
        P.BodySupportX==321. && P.BodySupportY==325. && P.ComponentSupportX==344. && P.ComponentSupportY==286.
        && P.Scale==.48 && P.Angle==-19.52939909323423);
    Fast.PressReload(Fast.State().Time,C);
    TestFalse(TEXT("normal reload cancellation immediately rejects stale keypose"),DungeonXBWBodyPose::Reload(Fast.State(),P));
    auto Invalid=NearEnd;Invalid.Time=.2;Invalid.Action.Type=EAction::Primary;
    TestFalse(TEXT("primary cannot masquerade as reload"),DungeonXBWBodyPose::Reload(Invalid,P));
    Invalid.Action.Type=EAction::Reload;Invalid.Action.Weapon=DungeonContentCombat::EWeapon::STF001;
    TestFalse(TEXT("staff cannot reuse crossbow mechanics"),DungeonXBWBodyPose::Reload(Invalid,P));
    Invalid.Action.Weapon=DungeonContentCombat::EWeapon::XBW001;Invalid.Time=-.01;
    TestFalse(TEXT("before actual start rejected"),DungeonXBWBodyPose::Reload(Invalid,P));
    Invalid.Time=std::numeric_limits<double>::quiet_NaN();
    TestFalse(TEXT("nonfinite sample rejected"),DungeonXBWBodyPose::Reload(Invalid,P));
    Invalid.Time=.2;Invalid.Action.End=Invalid.Action.Start;
    TestFalse(TEXT("degenerate interval rejected"),DungeonXBWBodyPose::Reload(Invalid,P));
    return true;
}
#endif
