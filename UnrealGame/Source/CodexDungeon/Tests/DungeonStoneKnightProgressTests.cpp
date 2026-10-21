#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonStoneKnight.h"
#include <array>
#include <cstring>
#include <type_traits>

namespace
{
using namespace DungeonStoneKnight;

uint64 KnightProgressBits(double Value)
{
    uint64 Out=0;
    std::memcpy(&Out,&Value,sizeof(Out));
    return Out;
}

struct FBoundedKnightProgressSweep
{
    std::array<FSweepRequest,17> Requests{};
    uint32 Calls=0;
    bool SafetyAbort=false;

    FSweepResult Query(const FSweepRequest& Request)
    {
        ++Calls;
        if(Calls<=Requests.size())Requests[Calls-1]=Request;
        // Test safety only: a production retry/event cap would not fix progress.
        // Sixteen legal clear queries precede a finite invalid fraction, so the
        // original StepTo rejects atomically instead of allocating until OOM.
        if(Calls>16){SafetyAbort=true;return {2.,EStop::None,0};}
        return {};
    }
};

FWorldInput KnightProgressWorld()
{
    FWorldInput World;
    World.HasTarget=true;
    World.Target={220.00000000000009,0.};
    World.CanStartAttack=false;
    return World;
}

// Independent field-value proof for invalid-query atomicity and continuation.
// Each scalar is copied separately; no whole-struct padding or pointer bytes.
struct FKnightProgressStateProof
{
    std::vector<uint8> Bytes;
    template<class T>void One(T Value)
    {
        static_assert(std::is_arithmetic_v<T>||std::is_enum_v<T>);
        const auto* Data=reinterpret_cast<const uint8*>(&Value);
        Bytes.insert(Bytes.end(),Data,Data+sizeof(Value));
    }
    template<class... T>void Values(T... V){(One(V),...);}
    void Point(FPoint P){Values(P.X,P.Y);}
    void Action(const FAction& A)
    {
        Values(A.AttackId,A.Kind,A.InProgress,A.Locked,A.ActiveIssued,A.Start,A.LockAt,A.ActiveAt,
            A.PlannedActiveEnd,A.ActiveEnd,A.RecoveryEnd,A.Damage,A.Stagger);
        Point(A.Origin);Point(A.Target);Point(A.Direction);Values(A.Stop);
    }
    explicit FKnightProgressStateProof(const FState& S)
    {
        Values(S.Version,S.EntityId,S.NextAttackId,S.NextEventId,S.Time,S.HP,S.PoiseAccum,S.LastPoiseAt,
            S.ProtectionUntil,S.StunUntil,S.CombatStartedAt,S.WakeStartedAt,S.WakeEnd,S.ChargeReadyAt,
            S.ShieldReadyAt,S.WakeQueued,S.Awakened,S.RewardClaimed,S.Phase);
        Point(S.Position);Action(S.Action);Values(uint64(S.ActiveReceipts.size()));
        for(const auto& R:S.ActiveReceipts){Action(R.FrozenAction);Values(R.End,R.EventId);}
        Values(uint64(S.HitReceipts.size()));
        for(const auto& R:S.HitReceipts)Values(R.AttackId,R.TargetId);
    }
};
bool SameKnightProgressState(const FState& A,const FState& B)
{return FKnightProgressStateProof(A).Bytes==FKnightProgressStateProof(B).Bytes;}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonKnightIdleRoundedEndpointProgressTest,
    "CodexDungeon.Content.StoneKnightProgress.IdleRoundedEndpointAdvances",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonKnightIdleRoundedEndpointProgressTest::RunTest(const FString&)
{
    // A genuine stop must still be queried and respected. A blanket idle/no-op
    // shortcut could hide the loop while bypassing this real kernel contract.
    {
        FKnightKernel Blocked(72,8.,{300.,0.});
        auto World=KnightProgressWorld();uint32 Calls=0;
        World.Sweep=[&](const FSweepRequest&){++Calls;return FSweepResult{0.,EStop::Wall,0};};
        const auto Wake=Blocked.StepTo(8.85,World);
        if(!TestTrue(TEXT("Public construction and full proximity warning reach idle before the blocked control"),
            Wake.Accepted&&Blocked.State().Awakened&&Blocked.State().Phase==EPhase::Idle&&Calls==0))return false;
        const auto Result=Blocked.StepTo(9.1,World);
        TestTrue(TEXT("A genuine wall blocks position while the legal idle interval still reaches its exact time"),
            Result.Accepted&&Calls==1&&Blocked.State().Position.X==300.
            &&Blocked.State().Position.Y==0.&&Blocked.State().Time==9.1);
    }

    {
        FKnightKernel Mirror(73,8.,{-300.,0.});auto MirrorWorld=KnightProgressWorld();
        MirrorWorld.Target.X=-220.00000000000009;FBoundedKnightProgressSweep MirrorSweep;
        MirrorWorld.Sweep=[&](const FSweepRequest& Q){return MirrorSweep.Query(Q);};
        if(!TestTrue(TEXT("Mirrored legal input completes its public proximity warning"),
            Mirror.StepTo(8.85,MirrorWorld).Accepted&&Mirror.State().Awakened&&MirrorSweep.Calls==0))return false;
        const auto Result=Mirror.StepTo(9.1,MirrorWorld);
        TestTrue(TEXT("Opposite X direction also completes exact absolute time without the safety abort"),
            Result.Accepted&&!MirrorSweep.SafetyAbort&&Mirror.State().Time==9.1
            &&Mirror.State().Position.X>-300.&&Mirror.State().Position.X<=MirrorWorld.Target.X);
    }
    {
        FKnightKernel BothAxes(74,8.,{300.,20.});auto AxisWorld=KnightProgressWorld();
        AxisWorld.Target={220.,0.};FBoundedKnightProgressSweep AxisSweep;
        AxisWorld.Sweep=[&](const FSweepRequest& Q){return AxisSweep.Query(Q);};
        if(!TestTrue(TEXT("Sequential-axis control completes the real warning"),
            BothAxes.StepTo(8.85,AxisWorld).Accepted&&BothAxes.State().Awakened))return false;
        const auto Result=BothAxes.StepTo(9.85,AxisWorld);
        TestTrue(TEXT("A full Y alignment preserves remaining interval budget for the original X chase"),
            Result.Accepted&&!AxisSweep.SafetyAbort&&AxisSweep.Calls==2&&BothAxes.State().Time==9.85
            &&BothAxes.State().Position.X==262.&&BothAxes.State().Position.Y==0.);
    }
    {
        FKnightKernel TinyY(75,8.,{300.,0.});auto YWorld=KnightProgressWorld();
        YWorld.Target={300.,1.e-14};FBoundedKnightProgressSweep YSweep;
        YWorld.Sweep=[&](const FSweepRequest& Q){return YSweep.Query(Q);};
        if(!TestTrue(TEXT("Tiny-Y control completes the real warning"),
            TinyY.StepTo(8.85,YWorld).Accepted&&TinyY.State().Awakened))return false;
        const auto Result=TinyY.StepTo(8.850001,YWorld);
        TestTrue(TEXT("Real Y progress remains legal when only its movement time rounds to the preceding time"),
            Result.Accepted&&!YSweep.SafetyAbort&&YSweep.Calls==1&&TinyY.State().Time==8.850001
            &&TinyY.State().Position.X==300.&&TinyY.State().Position.Y==1.e-14);
    }
    for(bool Invalid:{false,true})
    {
        FKnightKernel TinyBudget(76,0.,{300.,0.});auto BudgetWorld=KnightProgressWorld();
        BudgetWorld.Target={220.,0.};uint32 BudgetCalls=0;
        BudgetWorld.Sweep=[&](const FSweepRequest&)
        {++BudgetCalls;return Invalid?FSweepResult{2.,EStop::None,0}:FSweepResult{};};
        if(!TestTrue(TEXT("One-ULP time-budget control completes the public warning"),
            TinyBudget.StepTo(.85,BudgetWorld).Accepted&&TinyBudget.State().Awakened&&BudgetCalls==0))return false;
        const auto BeforeBudget=TinyBudget.Capture();const double Now=std::nextafter(.85,1.);
        const auto Result=TinyBudget.StepTo(Now,BudgetWorld);
        TestEqual(TEXT("An unrepresentable displacement still validates its original Sweep exactly once"),BudgetCalls,uint32(1));
        if(Invalid)
            TestTrue(TEXT("Invalid tiny-budget Sweep rejects atomically across every kernel field and receipt"),
                !Result.Accepted&&Result.Events.empty()&&SameKnightProgressState(BeforeBudget,TinyBudget.Capture()));
        else
            TestTrue(TEXT("Valid tiny-budget Sweep consumes the exact next representable time without invented displacement"),
                Result.Accepted&&TinyBudget.State().Time==Now&&TinyBudget.State().Position.X==300.
                &&TinyBudget.State().Position.Y==0.);
    }

    FKnightKernel Kernel(71,8.,{300.,0.});
    auto World=KnightProgressWorld();FBoundedKnightProgressSweep Sweep;
    World.Sweep=[&](const FSweepRequest& Request){return Sweep.Query(Request);};
    const auto Wake=Kernel.StepTo(8.85,World);
    if(!TestTrue(TEXT("Exact counterexample reaches real idle via public wake without Restore or state edits"),
        Wake.Accepted&&Kernel.State().Awakened&&Kernel.State().Phase==EPhase::Idle
        &&Kernel.State().Time==8.85&&Kernel.State().Position.X==300.&&Sweep.Calls==0))return false;
    const auto Before=Kernel.Capture();
    const auto Result=Kernel.StepTo(9.1,World);
    AddInfo(FString::Printf(TEXT("Bounded original-input progress accepted=%d calls=%u safety-abort=%d target=%.17g target-bits=%016llx time=%.17g x=%.17g"),
        int32(Result.Accepted),Sweep.Calls,int32(Sweep.SafetyAbort),World.Target.X,
        static_cast<unsigned long long>(KnightProgressBits(World.Target.X)),Kernel.State().Time,Kernel.State().Position.X));
    if(Sweep.Calls>=2)
    {
        const auto& Q=Sweep.Requests[1];
        AddInfo(FString::Printf(TEXT("Second real request from-time=%.17g to-time=%.17g from-x=%.17g to-x=%.17g bits=%016llx/%016llx/%016llx/%016llx"),
            Q.FromTime,Q.ToTime,Q.From.X,Q.To.X,
            static_cast<unsigned long long>(KnightProgressBits(Q.FromTime)),
            static_cast<unsigned long long>(KnightProgressBits(Q.ToTime)),
            static_cast<unsigned long long>(KnightProgressBits(Q.From.X)),
            static_cast<unsigned long long>(KnightProgressBits(Q.To.X))));
    }
    TestFalse(TEXT("Legal idle chase finishes before the test-only invalid-sweep safety abort"),Sweep.SafetyAbort);
    TestTrue(TEXT("Half-ULP stop distance cannot reject a valid finite clear-world StepTo"),Result.Accepted);
    TestEqual(TEXT("Rounded endpoint chase consumes the requested absolute interval exactly"),Kernel.State().Time,9.1);
    if(!Result.Accepted)
    {
        TestTrue(TEXT("Safety refusal leaves original live clock, position and event cursor intact"),
            Kernel.State().Time==Before.Time&&Kernel.State().Position.X==Before.Position.X
            &&Kernel.State().Position.Y==Before.Position.Y&&Kernel.State().NextEventId==Before.NextEventId
            &&Kernel.State().NextAttackId==Before.NextAttackId&&Kernel.State().HP==Before.HP
            &&Kernel.State().Phase==Before.Phase&&Result.Events.empty());
        return true;
    }
    TestTrue(TEXT("Clear chase makes physical progress without crossing its fixed target"),
        Kernel.State().Position.X<300.&&Kernel.State().Position.X>=World.Target.X
        &&Kernel.State().Position.Y==0.);
    const auto Events=Kernel.State().NextEventId;const auto Calls=Sweep.Calls;
    const auto Replay=Kernel.StepTo(9.1,World);
    TestTrue(TEXT("Same-time observation neither replays movement nor consumes another sweep or event ID"),
        Replay.Accepted&&Replay.Events.empty()&&Kernel.State().NextEventId==Events&&Sweep.Calls==Calls);
    FKnightKernel Restored(71);
    if(TestTrue(TEXT("Completed rounded-endpoint state remains a valid exact kernel snapshot"),
        Restored.Restore(Kernel.Capture())&&SameKnightProgressState(Kernel.Capture(),Restored.Capture())))
    {
        const auto Continued=Kernel.StepTo(9.2,World);const auto RestoredContinued=Restored.StepTo(9.2,World);
        TestTrue(TEXT("Restored endpoint state continues identically without replay or reset"),
            Continued.Accepted&&RestoredContinued.Accepted&&!Sweep.SafetyAbort
            &&Kernel.State().Time==9.2&&SameKnightProgressState(Kernel.Capture(),Restored.Capture()));
    }
    return true;
}
#endif
