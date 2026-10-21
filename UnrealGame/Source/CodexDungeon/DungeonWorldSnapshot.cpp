#include "DungeonWorldSnapshot.h"

namespace
{
namespace WA=DungeonWeaponActions;
using FWorldKey=FDungeonWorldWeaponKey;
bool Finite(FVector2D P){return FMath::IsFinite(P.X)&&FMath::IsFinite(P.Y);}
bool Origin(const WA::FOrigin& O){return FMath::IsFinite(O.X)&&FMath::IsFinite(O.Y)&&FMath::IsFinite(O.Height)&&O.Height>=0.;}
bool SameOrigin(const WA::FOrigin& A,const WA::FOrigin& B){return Origin(A)&&Origin(B)&&A.X==B.X&&A.Y==B.Y&&A.Height==B.Height;}
bool SameKey(const FWorldKey& A,const FWorldKey& B){return A.OwnerId==B.OwnerId&&A.ActionId==B.ActionId&&A.EventId==B.EventId
    &&A.SubhitId==B.SubhitId&&A.RoomInstanceId==B.RoomInstanceId;}
bool SameAction(const WA::FAction& A,const WA::FAction& B)
{
    if(A.Type!=B.Type||A.Phase!=B.Phase||A.Weapon!=B.Weapon||A.InstanceId!=B.InstanceId||A.ActionId!=B.ActionId
        ||A.Active!=B.Active||A.Locked!=B.Locked||A.StartedAirborne!=B.StartedAirborne||A.ForwardStepIssued!=B.ForwardStepIssued
        ||A.NextSubhit!=B.NextSubhit||A.Critical!=B.Critical||A.Terminal!=B.Terminal)return false;
    const double X[]={A.Facing,A.Start,A.LockAt,A.ActiveAt,A.ActiveEnd,A.End,A.SpeedPct,A.DamagePct,A.StaggerPct,A.ReachPct,
        A.CritMultiplier,A.AmmoCost,A.FocusCost,A.CooldownDuration,A.ReloadSpeedPct,A.FocusCostPct,A.SkillCooldownPct};
    const double Y[]={B.Facing,B.Start,B.LockAt,B.ActiveAt,B.ActiveEnd,B.End,B.SpeedPct,B.DamagePct,B.StaggerPct,B.ReachPct,
        B.CritMultiplier,B.AmmoCost,B.FocusCost,B.CooldownDuration,B.ReloadSpeedPct,B.FocusCostPct,B.SkillCooldownPct};
    for(int32 I=0;I<UE_ARRAY_COUNT(X);++I)if(!FMath::IsFinite(X[I])||!FMath::IsFinite(Y[I])||X[I]!=Y[I])return false;
    return true;
}
bool SameSource(const WA::FEvent& A,const WA::FEvent& B)
{
    if(A.EventId!=B.EventId||A.ActionId!=B.ActionId||A.InstanceId!=B.InstanceId||A.SubhitId!=B.SubhitId||A.Kind!=B.Kind
        ||A.MaxTargets!=B.MaxTargets||A.Shape!=B.Shape||A.OriginPolicy!=B.OriginPolicy||!SameOrigin(A.Origin,B.Origin)||!SameAction(A.Action,B.Action))return false;
    const double X[]={A.AtTime,A.WindowEnd,A.Damage,A.Stagger,A.MinRange,A.Range,A.Depth,A.ProjectileSpeed,A.SecondTargetRatio,
        A.BurnDps,A.BurnDuration,A.ForwardStep,A.AmmoConsumed,A.FocusConsumed};
    const double Y[]={B.AtTime,B.WindowEnd,B.Damage,B.Stagger,B.MinRange,B.Range,B.Depth,B.ProjectileSpeed,B.SecondTargetRatio,
        B.BurnDps,B.BurnDuration,B.ForwardStep,B.AmmoConsumed,B.FocusConsumed};
    for(int32 I=0;I<UE_ARRAY_COUNT(X);++I)if(!FMath::IsFinite(X[I])||!FMath::IsFinite(Y[I])||X[I]!=Y[I])return false;
    return true;
}
bool FinitePose(const DungeonWeaponPoseSocket::FResolved& P)
{
    if(uint32(P.Clip)>uint32(DungeonWeaponPoseSocket::EClip::Reload)||!Origin(P.ActorOrigin)||!Origin(P.CombatOrigin)||!Origin(P.PresentationOrigin))return false;
    for(double V:{P.SampleTime,P.Facing,P.RootX,P.RootY,P.BodySize,P.GripX,P.GripY,P.SupportX,P.SupportY,P.ComponentSupportX,P.ComponentSupportY,
        P.ComponentEmitX,P.ComponentEmitY,P.ComponentGripX,P.ComponentGripY,P.EmitX,P.EmitY,P.Angle,P.Scale})if(!FMath::IsFinite(V))return false;
    return P.SampleTime>=0.&&(P.Facing==1.||P.Facing==-1.)&&P.BodySize>0.&&P.Scale>0.;
}
bool SamePose(const DungeonWeaponPoseSocket::FResolved& A,const DungeonWeaponPoseSocket::FResolved& B)
{
    if(!FinitePose(A)||!FinitePose(B)||A.Supported!=B.Supported||A.CustomOverride!=B.CustomOverride||A.GroundPoseFallback!=B.GroundPoseFallback
        ||A.Clip!=B.Clip||A.Frame!=B.Frame||A.WeaponStateIndex!=B.WeaponStateIndex||A.InstanceId!=B.InstanceId||A.ActionId!=B.ActionId
        ||!SameOrigin(A.ActorOrigin,B.ActorOrigin)||!SameOrigin(A.CombatOrigin,B.CombatOrigin)||!SameOrigin(A.PresentationOrigin,B.PresentationOrigin))return false;
    const double X[]={A.SampleTime,A.Facing,A.RootX,A.RootY,A.BodySize,A.GripX,A.GripY,A.SupportX,A.SupportY,A.ComponentSupportX,
        A.ComponentSupportY,A.ComponentEmitX,A.ComponentEmitY,A.ComponentGripX,A.ComponentGripY,A.EmitX,A.EmitY,A.Angle,A.Scale};
    const double Y[]={B.SampleTime,B.Facing,B.RootX,B.RootY,B.BodySize,B.GripX,B.GripY,B.SupportX,B.SupportY,B.ComponentSupportX,
        B.ComponentSupportY,B.ComponentEmitX,B.ComponentEmitY,B.ComponentGripX,B.ComponentGripY,B.EmitX,B.EmitY,B.Angle,B.Scale};
    for(int32 I=0;I<UE_ARRAY_COUNT(X);++I)if(X[I]!=Y[I])return false;
    return true;
}
}

FDungeonWeaponWorldSnapshot DungeonWorldSnapshot::Capture(const FDungeonWeaponWorldState& State){return {1,State};}

bool DungeonWorldSnapshot::Restore(const FDungeonWeaponWorldSnapshot& Snapshot,
    const FDungeonWeaponWorldRestoreContext& C,FDungeonWeaponWorldState& Out,FString& Diagnostic)
{
    Diagnostic.Reset();const auto Reject=[&](const TCHAR* Why){Diagnostic=Why;return false;};
    const auto& S=Snapshot.State;
    if(Snapshot.Schema!=1||!C.RunGuid.IsValid()||!C.OwnerId||!C.RoomInstanceId||!C.PlayerActions
        ||!FMath::IsFinite(C.SimulationTime)||C.SimulationTime<0.||S.RunGuid!=C.RunGuid||S.RoomInstanceId!=C.RoomInstanceId
        ||!FMath::IsFinite(S.Time)||S.Time!=C.SimulationTime)return Reject(TEXT("Unknown schema or mismatched world scope/clock"));
    WA::FWeaponActionsKernel VerifiedActions;
    if(!FMath::IsFinite(C.PlayerActions->Time)||C.PlayerActions->Time>S.Time||!VerifiedActions.Restore(*C.PlayerActions))
        return Reject(TEXT("Saved player action owner is invalid or ahead of world boundary"));
    TMap<uint64,const FDungeonWorldActorBinding*> Bindings;uint64 Maximum=0;int32 Players=0;
    for(const auto& B:S.ActorBindings)
    {
        if(!B.EntityId||B.EntityId>=(uint64(1)<<63)||!B.RoomInstanceId||B.RoomInstanceId>S.RoomInstanceId||B.ContentId.IsEmpty()||Bindings.Contains(B.EntityId))
            return Reject(TEXT("Invalid or duplicate historical entity binding"));
        if(B.ContentId==TEXT("player")){if(B.EntityId!=C.OwnerId)return Reject(TEXT("Player binding differs from approved owner"));++Players;}
        Bindings.Add(B.EntityId,&B);Maximum=FMath::Max(Maximum,B.EntityId);
    }
    if(Players!=1||!S.NextEntityId||S.NextEntityId<=Maximum||S.NextEntityId>(uint64(1)<<63)
        ||!S.NextEventSequence||S.NextEventSequence!=uint64(S.Events.Num())+1)
        return Reject(TEXT("World entity/event cursor aliases saved history"));
    TMap<uint64,const WA::FEvent*> Issued;
    for(const auto& E:C.PlayerActions->Issued){if(Issued.Contains(E.EventId))return Reject(TEXT("Duplicated issued action event"));Issued.Add(E.EventId,&E);}
    TMap<uint64,FWorldKey> Keys;TMap<uint64,const WA::FEvent*> Sources;
    TMap<uint64,const FDungeonWorldProjectile*> Projectiles;
    TMap<uint64,const FDungeonWorldWeaponWindow*> Windows;
    const auto AddSource=[&](const FWorldKey& K,const WA::FEvent& E)
    {
        const auto* Known=Issued.Find(K.EventId);
        if(K.OwnerId!=C.OwnerId||!K.ActionId||!K.EventId||!K.RoomInstanceId||K.RoomInstanceId>S.RoomInstanceId
            ||K.ActionId!=E.ActionId||K.EventId!=E.EventId||K.SubhitId!=E.SubhitId||!Known||!SameSource(E,**Known)
            ||E.AtTime>S.Time||Sources.Contains(K.EventId))return false;
        Keys.Add(K.EventId,K);Sources.Add(K.EventId,&E);return true;
    };
    const auto KnownKey=[&](const FWorldKey& K){const auto* Original=Keys.Find(K.EventId);return Original&&SameKey(K,*Original);};
    for(const auto& P:S.Projectiles)
    {
        if(P.Source.Kind!=WA::EEvent::ProjectileEmitted||!AddSource(P.Key,P.Source)||!Finite(P.Position)
            ||!FMath::IsFinite(P.Traveled)||P.Traveled<0.||!FMath::IsFinite(P.LaunchForwardDistance)||P.LaunchForwardDistance<0.
            ||uint8(P.Stop)>uint8(EDungeonWorldProjectileStop::BlockedBody)||!FinitePose(P.PoseSocket)||!Origin(P.RangeAnchor)
            ||P.Source.ProjectileSpeed<=0.||(P.Active?(P.Stop!=EDungeonWorldProjectileStop::None||P.Key.RoomInstanceId!=S.RoomInstanceId):P.Stop==EDungeonWorldProjectileStop::None))
            return Reject(TEXT("Invalid projectile emission, geometry or active/stop state"));
        if(P.HasPoseSocket)
        {
            const auto& Pose=P.PoseSocket;
            if(!Pose.Supported||P.Source.Action.Weapon!=DungeonContentCombat::EWeapon::XBW001
                ||(Pose.Clip!=DungeonWeaponPoseSocket::EClip::Ready&&Pose.Clip!=DungeonWeaponPoseSocket::EClip::Primary)
                ||Pose.InstanceId!=P.Source.InstanceId||Pose.ActionId!=P.Source.ActionId||Pose.SampleTime!=P.Source.AtTime
                ||Pose.Facing!=P.Source.Action.Facing||!SameOrigin(Pose.CombatOrigin,P.Source.Origin)
                ||Pose.Frame<0||Pose.Frame>5||Pose.WeaponStateIndex < -1||Pose.WeaponStateIndex>3
                ||P.UsesActorRangeAnchor==Pose.CustomOverride)return Reject(TEXT("Frozen emission pose differs from original emission"));
        }
        else if(P.Source.Action.Weapon==DungeonContentCombat::EWeapon::XBW001||P.UsesActorRangeAnchor||P.LaunchClearancePending||P.LaunchObstructed)
            return Reject(TEXT("Missing frozen actor socket for the current crossbow geometry contract"));
        const auto& Anchor=P.UsesActorRangeAnchor?P.PoseSocket.ActorOrigin:P.Source.Origin;
        if(!SameOrigin(P.RangeAnchor,Anchor)||P.LaunchForwardDistance!=(P.UsesActorRangeAnchor?FMath::Max(0.,(P.Source.Origin.X-Anchor.X)*P.Source.Action.Facing):0.)
            ||(P.LaunchClearancePending&&(!P.Active||!P.UsesActorRangeAnchor||P.Traveled!=0.||S.Time!=P.Source.AtTime))
            ||(P.LaunchObstructed&&(P.Active||!P.UsesActorRangeAnchor||P.Traveled!=0.||P.LaunchClearancePending)))
            return Reject(TEXT("Frozen launch anchor or clearance facts disagree"));
        if(P.Active)
        {
            const auto Expected=DungeonWorldProjectiles::PositionAt(P,S.Time);
            if(P.Position.X!=Expected.X||P.Position.Y!=Expected.Y||P.Traveled!=FMath::Max(0.,(S.Time-P.Source.AtTime)*P.Source.ProjectileSpeed)
                ||S.Time>=P.Source.AtTime+FMath::Max(0.,P.Source.Range-P.LaunchForwardDistance)/P.Source.ProjectileSpeed)
                return Reject(TEXT("Live projectile does not occupy its saved ballistic boundary"));
        }
        Projectiles.Add(P.Key.EventId,&P);
    }
    for(const auto& W:S.Windows)
    {
        if(W.Source.Kind!=WA::EEvent::ActiveWindow||!AddSource(W.Key,W.Source)
            ||(W.Active&&(W.Key.RoomInstanceId!=S.RoomInstanceId||S.Time>=W.Source.WindowEnd)))return Reject(TEXT("Invalid world attack window"));
        Windows.Add(W.Key.EventId,&W);
    }
    if(Sources.Num()!=Issued.Num())return Reject(TEXT("An issued weapon emission disappeared from complete world history"));
    TMap<uint64,TMap<uint64,const FDungeonWorldWeaponHitReceipt*>> Hits;
    for(const auto& H:S.HitReceipts)
    {
        if(!KnownKey(H.Key)||!Bindings.Contains(H.TargetId)||H.TargetId==C.OwnerId||Bindings[H.TargetId]->RoomInstanceId!=H.Key.RoomInstanceId
            ||!FMath::IsFinite(H.AtTime)||H.AtTime>S.Time||!FMath::IsFinite(H.Damage)||H.Damage<0.||!FMath::IsFinite(H.Stagger)||H.Stagger<0.
            ||!FinitePose(H.PoseSocket)||!Origin(H.RangeAnchor))return Reject(TEXT("Invalid consumed hit identity, time or numbers"));
        const auto& E=*Sources[H.Key.EventId];auto& Seen=Hits.FindOrAdd(H.Key.EventId);
        if(Seen.Contains(H.TargetId)||H.AtTime<E.AtTime||H.Magic!=(E.Action.Weapon==DungeonContentCombat::EWeapon::STF001)
            ||(E.MaxTargets&&uint32(Seen.Num())>=E.MaxTargets))return Reject(TEXT("Duplicate/excess hit or invalid original hit domain"));
        const auto* P=Projectiles.Find(H.Key.EventId);const double Ratio=P&&Seen.Num()?E.SecondTargetRatio:1.;
        if(H.Damage!=E.Damage*Ratio||H.Stagger!=E.Stagger*Ratio)return Reject(TEXT("Consumed hit differs from original damage/stagger"));
        if(P)
        {
            if(H.HasPoseSocket!=(*P)->HasPoseSocket||!SamePose(H.PoseSocket,(*P)->PoseSocket)||!SameOrigin(H.RangeAnchor,(*P)->RangeAnchor)
                ||(H.LaunchObstructed&&(!(*P)->UsesActorRangeAnchor||H.AtTime!=E.AtTime)))return Reject(TEXT("Hit lost frozen projectile socket/anchor"));
        }
        else if(H.HasPoseSocket||H.LaunchObstructed||H.AtTime>=E.WindowEnd||!SameOrigin(H.RangeAnchor,{}))return Reject(TEXT("Window hit contains foreign projectile facts"));
        Seen.Add(H.TargetId,&H);
    }
    for(const auto& Pair:Projectiles)
    {
        const auto& P=*Pair.Value;const auto* Used=Hits.Find(Pair.Key);const uint32 Count=Used?uint32(Used->Num()):0;
        if((P.Stop==EDungeonWorldProjectileStop::TargetLimit&&(!P.Source.MaxTargets||Count<P.Source.MaxTargets))
            ||(P.Active&&P.Source.MaxTargets&&Count>=P.Source.MaxTargets))return Reject(TEXT("Projectile target-limit state disagrees with consumed hits"));
    }
    for(const auto& Pair:Windows)
    {const auto* Used=Hits.Find(Pair.Key);if(Pair.Value->Active&&Pair.Value->Source.MaxTargets&&Used&&uint32(Used->Num())>=Pair.Value->Source.MaxTargets)
        return Reject(TEXT("Live window has already consumed its target limit"));}
    TSet<uint64> BurnTargets;
    for(const auto& B:S.Burns)
    {
        if(!KnownKey(B.Key)||!Bindings.Contains(B.TargetId)||BurnTargets.Contains(B.TargetId)||!Hits.Contains(B.Key.EventId)
            ||!Hits[B.Key.EventId].Contains(B.TargetId))return Reject(TEXT("Burn lacks its unique target and original consumed direct hit"));
        const auto& E=*Sources[B.Key.EventId];const auto& Hit=*Hits[B.Key.EventId][B.TargetId];
        for(double V:{B.Dps,B.AppliedAt,B.ExpiresAt,B.NextTickAt})if(!FMath::IsFinite(V))return Reject(TEXT("Nonfinite burn state"));
        if(B.Dps<=0.||B.Dps!=E.BurnDps||E.BurnDuration<=0.||B.AppliedAt!=Hit.AtTime||B.AppliedAt>S.Time
            ||B.ExpiresAt!=B.AppliedAt+E.BurnDuration||B.NextTickAt<=B.AppliedAt||B.NextTickAt>B.ExpiresAt+1.
            ||(B.Active&&(B.ExpiresAt<=S.Time||B.NextTickAt<=S.Time
                ||(Bindings[B.TargetId]->RoomInstanceId!=S.RoomInstanceId&&B.TargetId!=C.OwnerId))))return Reject(TEXT("Burn application/expiry/tick phase is invalid"));
        // Refresh deliberately inherits the old phase; not AppliedAt+integer.
        BurnTargets.Add(B.TargetId);
    }
    struct FBurnPhase
    {
        FWorldKey Key;double Dps=0.,AppliedAt=0.,ExpiresAt=0.,NextTickAt=0.;bool Active=false;
    };
    TMap<uint64,FBurnPhase> BurnHistory;
    TMap<uint64,TSet<uint64>> PositiveDirectHits;
    // Each verified intrinsic burn lasts three seconds. A refresh segment can
    // advance at most four ticks, including the endpoint; never loop on untrusted time.
    const auto AdvanceBurnPhase=[](FBurnPhase& R,double Boundary)
    {
        for(int32 I=0;I<8&&R.NextTickAt<=Boundary&&R.NextTickAt<=R.ExpiresAt;++I)
        {const double Next=R.NextTickAt+1.;if(!FMath::IsFinite(Next)||Next<=R.NextTickAt)return false;R.NextTickAt=Next;}
        return R.NextTickAt>Boundary||R.NextTickAt>R.ExpiresAt;
    };
    TMap<uint64,int32> Created;TMap<uint64,const FDungeonWorldWeaponEvent*> Stopped;
    for(int32 I=0;I<S.Events.Num();++I)
    {
        const auto& E=S.Events[I];
        if(E.Sequence!=uint64(I)+1||uint8(E.Kind)>uint8(EDungeonWorldWeaponEventKind::BurnExpired)||!KnownKey(E.Key)
            ||!FMath::IsFinite(E.AtTime)||E.AtTime>S.Time||!Finite(E.Position)||!FinitePose(E.PoseSocket)||!Origin(E.RangeAnchor)
            ||(E.TargetId&&!Bindings.Contains(E.TargetId)))return Reject(TEXT("Invalid world journal sequence, reference or geometry"));
        for(double V:{E.Height,E.Damage,E.Stagger,E.ActualHPLoss})if(!FMath::IsFinite(V)||V<0.)return Reject(TEXT("Invalid journal numeric payload"));
        const auto& Source=*Sources[E.Key.EventId];if(E.AtTime<Source.AtTime)return Reject(TEXT("Journal fact predates its emission"));
        const auto* P=Projectiles.Find(E.Key.EventId);
        if(E.Kind==EDungeonWorldWeaponEventKind::ProjectileEmitted||E.Kind==EDungeonWorldWeaponEventKind::WindowCreated)
        {
            if(E.TargetId||E.AtTime!=Source.AtTime||E.Position.X!=Source.Origin.X||E.Position.Y!=Source.Origin.Y
                ||E.Height!=Source.Origin.Height||E.Damage!=Source.Damage||E.Stagger!=Source.Stagger
                ||E.Magic!=(Source.Action.Weapon==DungeonContentCombat::EWeapon::STF001)
                ||(E.Kind==EDungeonWorldWeaponEventKind::ProjectileEmitted)!=bool(P)||Created.Contains(E.Key.EventId))
                return Reject(TEXT("World creation journal differs from original emission"));
            if(P&&(E.HasPoseSocket!=(*P)->HasPoseSocket||!SamePose(E.PoseSocket,(*P)->PoseSocket)||!SameOrigin(E.RangeAnchor,(*P)->RangeAnchor)))
                return Reject(TEXT("Creation journal lost frozen socket/anchor"));
            Created.Add(E.Key.EventId,1);
        }
        else if(E.Kind==EDungeonWorldWeaponEventKind::ProjectileStopped)
        {
            if(!P||(*P)->Active||E.TargetId||Stopped.Contains(E.Key.EventId)||E.Position.X!=(*P)->Position.X||E.Position.Y!=(*P)->Position.Y
                ||E.HasPoseSocket!=(*P)->HasPoseSocket||!SamePose(E.PoseSocket,(*P)->PoseSocket)||!SameOrigin(E.RangeAnchor,(*P)->RangeAnchor)
                ||E.LaunchObstructed!=(*P)->LaunchObstructed)return Reject(TEXT("Projectile stop journal disagrees with saved projectile"));
            if((*P)->Stop==EDungeonWorldProjectileStop::Range&&E.AtTime!=Source.AtTime
                +FMath::Max(0.,Source.Range-(*P)->LaunchForwardDistance)/Source.ProjectileSpeed)
                return Reject(TEXT("Range stop predates or exceeds its intrinsic ballistic deadline"));
            if(!E.LaunchObstructed&&(*P)->Stop!=EDungeonWorldProjectileStop::RoomExit)
            {
                const auto At=DungeonWorldProjectiles::PositionAt(**P,E.AtTime);
                if(E.Position.X!=At.X||E.Position.Y!=At.Y||(*P)->Traveled!=FMath::Max(0.,(E.AtTime-Source.AtTime)*Source.ProjectileSpeed))
                    return Reject(TEXT("Stopped projectile does not match its original ballistic time"));
            }
            Stopped.Add(E.Key.EventId,&E);
        }
        else if(E.Kind==EDungeonWorldWeaponEventKind::DirectHitCommitted)
        {
            const auto* Group=Hits.Find(E.Key.EventId);const auto* Hit=Group?Group->Find(E.TargetId):nullptr;
            if(!Hit||E.AtTime!=(*Hit)->AtTime||E.Damage!=double(float((*Hit)->Damage))||E.Stagger!=double(float((*Hit)->Stagger))
                ||E.ActualHPLoss<=0.||E.Magic!=(*Hit)->Magic||E.HasPoseSocket!=(*Hit)->HasPoseSocket
                ||!SamePose(E.PoseSocket,(*Hit)->PoseSocket)||!SameOrigin(E.RangeAnchor,(*Hit)->RangeAnchor)
                ||E.LaunchObstructed!=(*Hit)->LaunchObstructed)return Reject(TEXT("Positive-loss journal differs from its consumed hit"));
            auto& Seen=PositiveDirectHits.FindOrAdd(E.Key.EventId);
            if(Seen.Contains(E.TargetId))return Reject(TEXT("A consumed direct hit has duplicate positive-loss facts"));
            Seen.Add(E.TargetId);
        }
        else
        {
            if(!E.TargetId||Source.BurnDps<=0.||Source.BurnDuration<=0.
                ||(E.Kind!=EDungeonWorldWeaponEventKind::BurnExpired&&!E.Magic))return Reject(TEXT("Burn journal has no original burn source/target"));
            if((E.Kind==EDungeonWorldWeaponEventKind::BurnApplied||E.Kind==EDungeonWorldWeaponEventKind::BurnRefreshed)
                &&(E.Damage!=Source.BurnDps||!Hits.Contains(E.Key.EventId)||!Hits[E.Key.EventId].Contains(E.TargetId)
                    ||Hits[E.Key.EventId][E.TargetId]->AtTime!=E.AtTime))return Reject(TEXT("Burn application journal has no matching direct hit"));
            if(E.Kind==EDungeonWorldWeaponEventKind::BurnTickCommitted&&(E.Damage!=double(float(Source.BurnDps))||E.Stagger!=0.||E.ActualHPLoss<=0.))
                return Reject(TEXT("Burn tick journal has invalid intrinsic damage"));
            if(E.HasPoseSocket||E.LaunchObstructed||!SameOrigin(E.RangeAnchor,{}))return Reject(TEXT("Burn journal carries foreign projectile facts"));
            auto* Prior=BurnHistory.Find(E.TargetId);
            if(E.Kind==EDungeonWorldWeaponEventKind::BurnApplied||E.Kind==EDungeonWorldWeaponEventKind::BurnRefreshed)
            {
                const auto* Positive=PositiveDirectHits.Find(E.Key.EventId);
                if(!Positive||!Positive->Contains(E.TargetId))return Reject(TEXT("Burn application lacks its actual positive-loss direct fact"));
                if(E.Kind==EDungeonWorldWeaponEventKind::BurnApplied)
                {
                    if(Prior&&Prior->Active)return Reject(TEXT("Fresh burn application replaces a still-active status"));
                    FBurnPhase R;R.Key=E.Key;R.Dps=Source.BurnDps;R.AppliedAt=E.AtTime;R.ExpiresAt=E.AtTime+Source.BurnDuration;
                    R.NextTickAt=E.AtTime+1.;R.Active=true;BurnHistory.Add(E.TargetId,R);
                }
                else
                {
                    if(!Prior||!Prior->Active||E.AtTime<Prior->AppliedAt||E.AtTime>Prior->ExpiresAt||Source.BurnDps<Prior->Dps||!AdvanceBurnPhase(*Prior,E.AtTime))
                        return Reject(TEXT("Burn refresh has no compatible preceding active phase"));
                    // Damage facts can precede a refresh with an earlier AtTime.
                    // Advance only the remaining old obligations; never rewind.
                    Prior->Key=E.Key;Prior->Dps=Source.BurnDps;Prior->AppliedAt=E.AtTime;Prior->ExpiresAt=E.AtTime+Source.BurnDuration;
                }
            }
            else if(E.Kind==EDungeonWorldWeaponEventKind::BurnTickCommitted)
            {
                if(!Prior||!Prior->Active||!SameKey(Prior->Key,E.Key)||E.AtTime<=Prior->AppliedAt||E.AtTime>Prior->ExpiresAt)
                    return Reject(TEXT("Burn tick has no current application source"));
                double Tick=Prior->NextTickAt;
                for(int32 N=0;N<8&&Tick<E.AtTime&&Tick<=Prior->ExpiresAt;++N)
                {const double Next=Tick+1.;if(!FMath::IsFinite(Next)||Next<=Tick)return Reject(TEXT("Burn phase cannot advance"));Tick=Next;}
                if(Tick!=E.AtTime)return Reject(TEXT("Burn tick is duplicated or moved off its inherited phase"));
                Prior->NextTickAt=Tick+1.;
            }
            else
            {
                if(!Prior||!Prior->Active||!SameKey(Prior->Key,E.Key)||E.AtTime<Prior->AppliedAt)
                    return Reject(TEXT("Burn expiry has no current application"));
                Prior->Active=false;
            }
        }
    }
    if(BurnHistory.Num()!=S.Burns.Num())return Reject(TEXT("Burn values and application history have different target domains"));
    for(const auto& B:S.Burns)
    {
        auto* R=BurnHistory.Find(B.TargetId);
        if(!R||!SameKey(B.Key,R->Key)||B.Dps!=R->Dps||B.AppliedAt!=R->AppliedAt||B.ExpiresAt!=R->ExpiresAt)
            return Reject(TEXT("Saved burn differs from its latest actual application"));
        if(B.Active)
        {
            if(!R->Active||!AdvanceBurnPhase(*R,S.Time)||B.NextTickAt!=R->NextTickAt)
                return Reject(TEXT("Live burn next tick differs from inherited application/tick phase"));
        }
        else
        {
            if(R->Active&&B.Key.RoomInstanceId==S.RoomInstanceId)return Reject(TEXT("Current-room inactive burn has no expiry fact"));
            // Death may stop before a due zero-loss tick, and room exit appends
            // no expiry. Retain the proven phase lower bound without replaying to Now.
            double Next=R->NextTickAt;
            for(int32 N=0;N<8&&Next<B.NextTickAt&&Next<=R->ExpiresAt;++N)
            {const double Advanced=Next+1.;if(!FMath::IsFinite(Advanced)||Advanced<=Next)return Reject(TEXT("Inactive burn phase cannot advance"));Next=Advanced;}
            if(Next!=B.NextTickAt)return Reject(TEXT("Inactive burn moved backward or off its proven phase"));
        }
    }
    if(Created.Num()!=Sources.Num())return Reject(TEXT("An accepted world emission has no unique creation fact"));
    for(const auto& Pair:Projectiles)if(Pair.Value->Active==Stopped.Contains(Pair.Key))return Reject(TEXT("Projectile live/stop journal state conflicts"));
    // Hit consumption can legitimately produce no positive HP-loss journal.
    // All checks above observed only saved data; install one independent value.
    FDungeonWeaponWorldState Candidate=S;Out=MoveTemp(Candidate);return true;
}
