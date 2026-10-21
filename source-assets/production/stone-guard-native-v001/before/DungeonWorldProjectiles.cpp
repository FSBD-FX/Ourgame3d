#include "DungeonWorldProjectiles.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "DungeonStoneKnightDriver.h"
#include "DungeonRoomLayout.h"
#include "Engine/World.h"
#include "CollisionQueryParams.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include <cmath>
#include <limits>

namespace
{
bool Clip(double A,double Z,double Low,double High,double& Entry,double& Exit)
{
    if (A==Z) return A>=Low&&A<=High;
    double P=(Low-A)/(Z-A),Q=(High-A)/(Z-A);
    if (P>Q) Swap(P,Q);
    Entry=FMath::Max(Entry,P);Exit=FMath::Min(Exit,Q);
    return Entry<=Exit&&Entry<=1.0&&Exit>=0.0;
}
FVector2D BodyPosition(const FDungeonKnightBody& B,double From,double To,double At)
{
    for (int32 I=B.MotionSegments.Num()-1;I>=0;--I)
    {
        const auto& M=B.MotionSegments[I];
        if (At>=M.FromTime&&(At<M.ToTime||(!M.bEndExclusive&&At==M.ToTime)))
            return FMath::Lerp(M.From,M.To,M.ToTime>M.FromTime?(At-M.FromTime)/(M.ToTime-M.FromTime):1.0);
    }
    return FMath::Lerp(B.Start,B.End,To>From?FMath::Clamp((At-From)/(To-From),0.0,1.0):1.0);
}
double BodyHeight(const FDungeonKnightBody& B,double From,double To,double At)
{
    for (int32 I=B.MotionSegments.Num()-1;I>=0;--I)
    {
        const auto& M=B.MotionSegments[I];
        if (At>=M.FromTime&&(At<M.ToTime||(!M.bEndExclusive&&At==M.ToTime)))
            return FMath::Lerp(M.FromHeight,M.ToHeight,M.ToTime>M.FromTime?(At-M.FromTime)/(M.ToTime-M.FromTime):1.0);
    }
    return FMath::Lerp(B.StartHeight,B.EndHeight,To>From?FMath::Clamp((At-From)/(To-From),0.0,1.0):1.0);
}
bool SameEmission(const FDungeonWorldWeaponKey& A,const FDungeonWorldWeaponKey& B)
{
    return A.OwnerId==B.OwnerId&&A.ActionId==B.ActionId&&A.EventId==B.EventId
        &&A.SubhitId==B.SubhitId&&A.RoomInstanceId==B.RoomInstanceId;
}

FDungeonWorldProjectileContact LaunchContact(const FDungeonWorldProjectile& P,double From,double To,
    const TArray<FDungeonKnightBody>& Bodies,const TArray<FDungeonWorldWeaponHitReceipt>& Receipts,
    ADungeonFighter* Owner,UWorld* World,TFunctionRef<bool(const FDungeonKnightBody&,double)> DamageAdmission)
{
    FDungeonWorldProjectileContact Best;
    if(!P.LaunchClearancePending||!P.UsesActorRangeAnchor||!World||!Owner)return Best;
    const FVector2D Start(P.RangeAnchor.X,P.RangeAnchor.Y),End(P.Source.Origin.X,P.Source.Origin.Y),Delta=End-Start;
    double BestFraction=2.;int32 Priority=MAX_int32;uint64 BestTarget=MAX_uint64;
    const auto Consider=[&](double Fraction,EDungeonWorldProjectileStop Stop,int32 Rank,const FDungeonKnightBody* Body=nullptr,bool Legal=false)
    {
        const uint64 Id=Body?Body->EntityId:0;
        if(Fraction<0.||Fraction>1.)return;
        if(!Best.Found||Fraction<BestFraction||(Fraction==BestFraction&&(Rank>Priority||(Rank==Priority&&Id<BestTarget))))
        {
            Best.Found=true;Best.AtTime=P.Source.AtTime;Best.Position=Start+Delta*Fraction;
            Best.Stop=Stop;Best.LegalDamage=Legal;Best.LaunchSegment=true;
            Best.Target=Body?Body->Fighter:TWeakObjectPtr<ADungeonFighter>();
            BestFraction=Fraction;Priority=Rank;BestTarget=Id;
        }
    };
    const auto Bounds=DungeonRoomLayout::CenterBounds();
    if(!Bounds.IsInsideOrOn(Start))Consider(0.,EDungeonWorldProjectileStop::HardBounds,3);
    if(Delta.X>0.&&End.X>=Bounds.Max.X)Consider((Bounds.Max.X-Start.X)/Delta.X,EDungeonWorldProjectileStop::HardBounds,3);
    if(Delta.X<0.&&End.X<=Bounds.Min.X)Consider((Bounds.Min.X-Start.X)/Delta.X,EDungeonWorldProjectileStop::HardBounds,3);
    FCollisionObjectQueryParams Objects;Objects.AddObjectTypesToQuery(ECC_WorldStatic);Objects.AddObjectTypesToQuery(ECC_WorldDynamic);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(WeaponLaunchClearance),false);Params.AddIgnoredActor(Owner);
    TArray<FHitResult> Walls;
    World->LineTraceMultiByObjectType(Walls,FVector(Start.X,Start.Y,0.),FVector(End.X,End.Y,0.),Objects,Params);
    for(const auto& Hit:Walls)if(Hit.bBlockingHit&&FMath::Abs(Hit.ImpactNormal.Z)<.5)
        Consider(double(Hit.Time),EDungeonWorldProjectileStop::Wall,4);
    for(const auto& Body:Bodies)
    {
        if(!Body.bAlive||!Body.EntityId||!Body.Fighter.IsValid()||Body.Fighter.Get()==Owner
            ||(!Body.bBlocksBody&&!Body.Fighter->GetStoneBatDriver()))continue;
        bool Consumed=false;for(const auto& Receipt:Receipts)if(SameEmission(Receipt.Key,P.Key)&&Receipt.TargetId==Body.EntityId){Consumed=true;break;}
        if(Consumed)continue;
        FVector2D Hurt(18.,16.);
        if(Body.Fighter->GetStoneBatDriver()){const auto D=DungeonStoneBat::FBatKernel::Definition();Hurt={D.HurtHalfX,D.HurtHalfY};}
        if(Body.Fighter->GetStoneKnightDriver()){const auto D=DungeonStoneKnight::FKnightKernel::Definition();Hurt={D.HurtHalfX,D.HurtHalfY};}
        const auto Center=BodyPosition(Body,From,To,P.Source.AtTime);
        const double Height=BodyHeight(Body,From,To,P.Source.AtTime);
        if(Body.Fighter->GetStoneBatDriver()&&FMath::Abs(Height-P.Source.Origin.Height)>65.)continue;
        const auto RelativeStart=Center-Start,RelativeEnd=Center-End;double Entry=0.,Exit=1.;
        if(!Clip(RelativeStart.X,RelativeEnd.X,-Hurt.X,Hurt.X,Entry,Exit)
            ||!Clip(RelativeStart.Y,RelativeEnd.Y,-Hurt.Y,Hurt.Y,Entry,Exit))continue;
        const double Forward=(Center.X-P.RangeAnchor.X)*P.Source.Action.Facing;
        const bool Legal=Body.Fighter->bEnemy!=Owner->bEnemy&&Forward>=P.Source.MinRange&&Forward<=P.Source.Range
            &&FMath::Abs(Center.Y-P.RangeAnchor.Y)<=P.Source.Depth&&FMath::Abs(Height-P.Source.Origin.Height)<=65.
            &&DamageAdmission(Body,P.Source.AtTime);
        Consider(Entry,EDungeonWorldProjectileStop::BlockedBody,2,&Body,Legal);
    }
    return Best;
}
}

FVector2D DungeonWorldProjectiles::PositionAt(const FDungeonWorldProjectile& P,double At)
{
    if(P.LaunchObstructed)return P.Position;
    return {P.Source.Origin.X+P.Source.Action.Facing*P.Source.ProjectileSpeed*(At-P.Source.AtTime),P.Source.Origin.Y};
}

FDungeonWorldProjectileContact DungeonWorldProjectiles::QueryContact(const FDungeonWorldProjectile& P,
    double From,double To,const TArray<FDungeonKnightBody>& Bodies,
    const TArray<FDungeonWorldWeaponHitReceipt>& Receipts,ADungeonFighter* Owner,UWorld* World,
    TFunctionRef<bool(const FDungeonKnightBody&,double)> DamageAdmission)
{
    FDungeonWorldProjectileContact Best;
    if (!P.Active||!Owner||!World||To<From||P.Source.ProjectileSpeed<=0.0) return Best;
    const double Begin=FMath::Max(From,P.Source.AtTime);
    if (Begin>To) return Best;
    int32 Priority=-1;uint64 BestTarget=MAX_uint64;
    const auto Consider=[&](double At,EDungeonWorldProjectileStop Stop,int32 Rank,
        const FDungeonKnightBody* Body=nullptr,bool Legal=false)
    {
        const uint64 Id=Body?Body->EntityId:0;
        if (At<Begin||At>To) return;
        if (!Best.Found||At<Best.AtTime||(At==Best.AtTime&&(Rank>Priority||(Rank==Priority&&Id<BestTarget))))
        {
            Best.Found=true;Best.AtTime=At;Best.Position=PositionAt(P,At);Best.Stop=Stop;
            Best.Target=Body?Body->Fighter:TWeakObjectPtr<ADungeonFighter>();Best.LegalDamage=Legal;
            Priority=Rank;BestTarget=Id;
        }
    };
    const double RangeEnd=P.Source.AtTime+FMath::Max(0.,P.Source.Range-P.LaunchForwardDistance)/P.Source.ProjectileSpeed;
    if (RangeEnd<=To) Consider(FMath::Max(Begin,RangeEnd),EDungeonWorldProjectileStop::Range,1);
    const auto A=PositionAt(P,Begin),Z=PositionAt(P,To),D=Z-A;
    const auto Bounds=DungeonRoomLayout::CenterBounds();
    if (!Bounds.IsInsideOrOn(A)) Consider(Begin,EDungeonWorldProjectileStop::HardBounds,3);
    if (D.X>0&&Z.X>=Bounds.Max.X) Consider(Begin+(To-Begin)*(Bounds.Max.X-A.X)/D.X,EDungeonWorldProjectileStop::HardBounds,3);
    if (D.X<0&&Z.X<=Bounds.Min.X) Consider(Begin+(To-Begin)*(Bounds.Min.X-A.X)/D.X,EDungeonWorldProjectileStop::HardBounds,3);
    FCollisionObjectQueryParams Objects;
    Objects.AddObjectTypesToQuery(ECC_WorldStatic);Objects.AddObjectTypesToQuery(ECC_WorldDynamic);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(WeaponProjectileWorld),false);Params.AddIgnoredActor(Owner);
    TArray<FHitResult> Walls;
    // A wall is a ground-plane obstruction in this 2.5D world. Jump height is
    // independently checked against bodies; it never turns into downward aim.
    World->LineTraceMultiByObjectType(Walls,FVector(A.X,A.Y,0),FVector(Z.X,Z.Y,0),Objects,Params);
    for (const auto& H:Walls) if (H.bBlockingHit&&FMath::Abs(H.ImpactNormal.Z)<.5)
        Consider(Begin+(To-Begin)*double(H.Time),EDungeonWorldProjectileStop::Wall,4);
    for (const auto& B:Bodies)
    {
        if (!B.bAlive||!B.EntityId||!B.Fighter.IsValid()||(!B.bBlocksBody&&!B.Fighter->GetStoneBatDriver())||B.Fighter.Get()==Owner) continue;
        bool Consumed=false;for (const auto& H:Receipts) if (SameEmission(H.Key,P.Key)&&H.TargetId==B.EntityId) {Consumed=true;break;}
        if (Consumed) continue;
        FVector2D Hurt(18,16);
        if(B.Fighter->GetStoneBatDriver()){const auto Def=DungeonStoneBat::FBatKernel::Definition();Hurt={Def.HurtHalfX,Def.HurtHalfY};}
        if (B.Fighter->GetStoneKnightDriver())
        {
            const auto Def=DungeonStoneKnight::FKnightKernel::Definition();Hurt={Def.HurtHalfX,Def.HurtHalfY};
        }
        TArray<TPair<double,double>> Slices;
        if (B.MotionSegments.IsEmpty()) Slices.Add({Begin,To});
        else for (const auto& M:B.MotionSegments)
        {
            const double L=FMath::Max(Begin,M.FromTime);double R=FMath::Min(To,M.ToTime);
            if (M.bEndExclusive&&R==M.ToTime) R=std::nextafter(R,L);
            if (L<=R&&!(M.bEndExclusive&&L==M.ToTime)) Slices.Add({L,R});
        }
        for (const auto& Slice:Slices)
        {
            const double L=Slice.Key,R=Slice.Value;
            const auto Relative0=BodyPosition(B,From,To,L)-PositionAt(P,L);
            const auto Relative1=BodyPosition(B,From,To,R)-PositionAt(P,R);
            double Entry=0,Exit=1;
            // No authored projectile radius exists for these two player weapons.
            if (!Clip(Relative0.X,Relative1.X,-Hurt.X,Hurt.X,Entry,Exit)
                ||!Clip(Relative0.Y,Relative1.Y,-Hurt.Y,Hurt.Y,Entry,Exit)) continue;
            // Bat hurt contact is independent of its ground body. A projectile
            // below the actual hurt-height gate passes beneath high flight.
            if(B.Fighter->GetStoneBatDriver()&&!Clip(BodyHeight(B,From,To,L)-P.Source.Origin.Height,
                BodyHeight(B,From,To,R)-P.Source.Origin.Height,-65.,65.,Entry,Exit))continue;
            double At=FMath::Lerp(L,R,Entry);
            const auto Inside=[&](double Time)
            {
                const auto Relative=BodyPosition(B,From,To,Time)-PositionAt(P,Time);
                return FMath::Abs(Relative.X)<=Hurt.X&&FMath::Abs(Relative.Y)<=Hurt.Y
                    &&(!B.Fighter->GetStoneBatDriver()||FMath::Abs(BodyHeight(B,From,To,Time)-P.Source.Origin.Height)<=65.);
            };
            if (!Inside(At))
            {
                // The analytic entry can round to a time whose reconstructed
                // projectile is still outside. Find the first representable
                // actual overlap, using exactly the position formula we commit.
                // Never repeat that outside time or add a geometry epsilon.
                const double Last=FMath::Lerp(L,R,Exit);
                double Clear=At+(Last-At)*.5;
                if (!Inside(Clear)) {Clear=Last;if (!Inside(Clear)) continue;}
                double Outside=At;
                for (int32 N=0;N<std::numeric_limits<double>::digits+2;++N)
                {
                    const double Mid=Outside+(Clear-Outside)*.5;
                    if (Mid==Outside||Mid==Clear) break;
                    if (Inside(Mid)) Clear=Mid;else Outside=Mid;
                }
                At=Clear;
            }
            const auto Center=BodyPosition(B,From,To,At);
            const auto& Anchor=P.UsesActorRangeAnchor?P.RangeAnchor:P.Source.Origin;
            const double Forward=(Center.X-Anchor.X)*P.Source.Action.Facing;
            const bool Legal=B.Fighter->bEnemy!=Owner->bEnemy&&Forward>=P.Source.MinRange&&Forward<=P.Source.Range
                &&FMath::Abs(Center.Y-Anchor.Y)<=P.Source.Depth
                &&FMath::Abs(BodyHeight(B,From,To,At)-P.Source.Origin.Height)<=65.0&&DamageAdmission(B,At);
            Consider(At,EDungeonWorldProjectileStop::BlockedBody,2,&B,Legal);
        }
    }
    return Best;
}

uint64 ADungeonGameMode::FindWorldEntityId(const ADungeonFighter* Fighter) const
{
    for (const auto& Pair:WorldEntityIds) if (Pair.Key.Get()==Fighter) return Pair.Value;
    return 0; // Observation never admits or allocates an actor.
}

ADungeonFighter* ADungeonGameMode::FindWorldFighter(uint64 EntityId) const
{
    for (const auto& Pair:WorldEntityIds) if (Pair.Value==EntityId) return Pair.Key.Get();
    return nullptr;
}

void ADungeonGameMode::AdmitWorldFighters()
{
    if (!EquipmentRuntime->View.Bound) return;
    const auto Admit=[this](ADungeonFighter* Fighter)
    {
        if (!IsValid(Fighter)||FindWorldEntityId(Fighter)) return;
        if (!WeaponWorld.NextEntityId||WeaponWorld.NextEntityId>=(uint64(1)<<63)) return;
        const uint64 Id=WeaponWorld.NextEntityId++;
        WorldEntityIds.Add(Fighter,Id);
        WeaponWorld.ActorBindings.Add({Id,WeaponWorld.RoomInstanceId,
            Fighter->EnemyContentId.IsEmpty()?TEXT("QA-PROTOTYPE-ENEMY"):Fighter->EnemyContentId});
    };
    for (ADungeonFighter* Enemy:Enemies) Admit(Enemy);
}

FDungeonWorldWeaponKey ADungeonGameMode::WorldWeaponKey(ADungeonFighter* Fighter,const DungeonWeaponActions::FEvent& E) const
{
    return {Fighter->GetRuntimeEntityId(),E.ActionId,E.EventId,E.SubhitId,WeaponWorld.RoomInstanceId};
}

void ADungeonGameMode::AppendWeaponWorldEvent(FDungeonWorldWeaponEvent Event)
{
    Event.Sequence=WeaponWorld.NextEventSequence++;WeaponWorld.Events.Add(Event);
}

bool ADungeonGameMode::WorldDamageAdmission(const FDungeonKnightBody& B,double At,const FDungeonWorldWeaponKey& Key) const
{
    if (!B.bAlive||!B.Fighter.IsValid()) return false;
    const auto F=B.Fighter.Get();const auto& Protection=F->HurtProtectionSource;
    const bool OwnAction=Key.OwnerId&&Protection.OwnerId==Key.OwnerId&&Protection.ActionId==Key.ActionId;
    if (OwnAction)
    {
        // Same accepted action's later subhits bypass only its own hurt protection.
        // Independently accepted dodge remains a fresh check for every subhit.
        return !F->IsDodgeInvulnerableAt(At);
    }
    if (!B.bUseTimedDamageAdmission) return B.bCanTakeDamage;
    for (const auto& I:B.DirectInvulnerabilityIntervals) if (At>=I.Start&&At<I.EndExclusive) return false;
    return true;
}

void ADungeonGameMode::ConsumeBoundWeaponEvents(ADungeonFighter* Fighter,const std::vector<DungeonWeaponActions::FEvent>& Events)
{
    using namespace DungeonWeaponActions;
    bool NewProjectile=false;
    for (const auto& E:Events)
    {
        if (E.EventId<=Fighter->LastSkillEventId) continue;
        Fighter->LastSkillEventId=E.EventId;
        if (E.Kind==EEvent::ForwardStep)
        {
            const auto Delta=SweepWeaponStep(Fighter,E.ForwardStep,E.AtTime);
            const auto End=Fighter->GetGroundPosition()+Delta;
            Fighter->BatchSkillStepAt=E.AtTime;Fighter->BatchSkillStepDelta+=Delta;
            Fighter->SetActorLocation(FVector(End.X,End.Y,0));Fighter->SyncWeaponMuzzleTransform();
        }
        else if (E.Kind==EEvent::ProjectileEmitted||E.Kind==EEvent::ActiveWindow)
        {
            const auto Key=WorldWeaponKey(Fighter,E);bool Existing=false;
            for (const auto& P:WeaponWorld.Projectiles) Existing|=SameEmission(P.Key,Key);
            for (const auto& W:WeaponWorld.Windows) Existing|=SameEmission(W.Key,Key);
            if (Existing) continue;
            FDungeonWorldWeaponEvent Fact;Fact.Key=Key;Fact.AtTime=E.AtTime;
            Fact.Position={E.Origin.X,E.Origin.Y};Fact.Height=E.Origin.Height;
            Fact.Damage=E.Damage;Fact.Stagger=E.Stagger;Fact.Magic=E.Action.Weapon==DungeonContentCombat::EWeapon::STF001;
            if (E.Kind==EEvent::ProjectileEmitted)
            {
                FDungeonWorldProjectile P;P.Key=Key;P.Source=E;P.Position=Fact.Position;P.Active=true;
                P.RangeAnchor=E.Origin;
                if(const auto* Pose=Fighter->FindWeaponEmissionPoseSocket(E.ActionId,E.SubhitId))
                {
                    P.HasPoseSocket=Fact.HasPoseSocket=true;P.PoseSocket=Fact.PoseSocket=*Pose;
                    P.UsesActorRangeAnchor=!Pose->CustomOverride;
                    if(P.UsesActorRangeAnchor)
                    {
                        P.RangeAnchor=Pose->ActorOrigin;
                        P.LaunchForwardDistance=FMath::Max(0.,(E.Origin.X-P.RangeAnchor.X)*E.Action.Facing);
                        P.LaunchClearancePending=true;
                    }
                }
                Fact.RangeAnchor=P.RangeAnchor;
                WeaponWorld.Projectiles.Add(P);NewProjectile=true;Fact.Kind=EDungeonWorldWeaponEventKind::ProjectileEmitted;
            }
            else
            {
                FDungeonWorldWeaponWindow W;W.Key=Key;W.Source=E;W.Active=true;WeaponWorld.Windows.Add(W);
                Fact.Kind=EDungeonWorldWeaponEventKind::WindowCreated;
                if (E.Action.Weapon!=DungeonContentCombat::EWeapon::STF001)
                {
                    const TCHAR* Family=E.Action.Weapon==DungeonContentCombat::EWeapon::GSW001?TEXT("GSW")
                        :E.Action.Weapon==DungeonContentCombat::EWeapon::SPR001?TEXT("SPR"):TEXT("SWD");
                    const TCHAR* Cue=E.Action.Weapon==DungeonContentCombat::EWeapon::SPR001?TEXT("THRUST"):TEXT("WHOOSH");
                    // This branch already admitted one new authoritative WindowCreated.
                    // Each real spear subhit keeps its own E.AtTime and journal sequence.
                    const FString AudioCue=FString::Printf(TEXT("%s_%s_03"),Family,Cue);
                    AppendActionAudio(*AudioCue,E.AtTime,Fighter->GetRuntimeEntityId(),E.ActionId,
                        E.InstanceId,0,EquipmentRuntime->View.Revision);
                }
            }
            AppendWeaponWorldEvent(Fact);
        }
    }
    ResolveWeaponSkillWindows(Fighter);
    if(NewProjectile)
    {
        // Old interval contacts retain their shared admission. This immediate
        // new-emission query must not admit a body killed by those earlier hits.
        auto FreshEmissionBodies=SkillBatchBodies;
        for(auto& Body:FreshEmissionBodies)
            if(Body.Fighter.IsValid()&&Body.Fighter->bDead)Body.bAlive=false;
        ResolveWorldProjectiles(SkillBatchTo,SkillBatchTo,FreshEmissionBodies);
    }
    else ResolveWorldProjectiles(SkillBatchTo,SkillBatchTo,SkillBatchBodies);
}

void ADungeonGameMode::ResolveWorldProjectiles(double From,double To,const TArray<FDungeonKnightBody>& Bodies)
{
    if (!EquipmentRuntime->View.Bound) return;
    for (auto& P:WeaponWorld.Projectiles)
    {
        if (!P.Active||P.Key.RoomInstanceId!=WeaponWorld.RoomInstanceId) continue;
        ADungeonFighter* ProjectileOwner=FindWorldFighter(P.Key.OwnerId);if (!ProjectileOwner) continue;
        // A piercing projectile can contact coincident hurtboxes at one time.
        for (int32 Pass=0;Pass<3&&P.Active;++Pass)
        {
            const auto Admission=[this,&P](const FDungeonKnightBody& B,double At){return WorldDamageAdmission(B,At,P.Key);};
            auto Contact=LaunchContact(P,From,To,Bodies,WeaponWorld.HitReceipts,ProjectileOwner,GetWorld(),Admission);
            if(!Contact.Found)
            {
                P.LaunchClearancePending=false;
                Contact=DungeonWorldProjectiles::QueryContact(P,From,To,Bodies,WeaponWorld.HitReceipts,ProjectileOwner,GetWorld(),Admission);
            }
            if (!Contact.Found)
            {
                P.Position=DungeonWorldProjectiles::PositionAt(P,To);
                P.Traveled=FMath::Max(0.0,(To-P.Source.AtTime)*P.Source.ProjectileSpeed);break;
            }
            P.Position=Contact.Position;P.Traveled=Contact.LaunchSegment?0.:FMath::Max(0.0,(Contact.AtTime-P.Source.AtTime)*P.Source.ProjectileSpeed);
            auto Stop=Contact.Stop;
            if (Contact.LegalDamage&&Contact.Target.IsValid())
            {
                int32 Count=0;for (const auto& H:WeaponWorld.HitReceipts) if (SameEmission(H.Key,P.Key)) ++Count;
                const double Ratio=Count?P.Source.SecondTargetRatio:1.0;
                const double Damage=P.Source.Damage*Ratio,Stagger=P.Source.Stagger*Ratio;
                const bool Magic=P.Source.Action.Weapon==DungeonContentCombat::EWeapon::STF001;
                FDungeonWorldWeaponHitReceipt Receipt{P.Key,Contact.Target->GetRuntimeEntityId(),Contact.AtTime,Damage,Stagger,Magic};
                Receipt.HasPoseSocket=P.HasPoseSocket;Receipt.PoseSocket=P.PoseSocket;Receipt.RangeAnchor=P.RangeAnchor;
                Receipt.LaunchObstructed=Contact.LaunchSegment;WeaponWorld.HitReceipts.Add(Receipt);
                FPendingDamage H{ProjectileOwner,Contact.Target.Get(),float(Damage),float(Stagger),Contact.AtTime};
                H.Magic=Magic;H.Source=P.Key;H.ImpactPosition=Contact.Position;H.ImpactHeight=P.Source.Origin.Height;
                PendingDamage.Add(H);
                if (P.Source.MaxTargets&&uint32(Count+1)>=P.Source.MaxTargets) Stop=EDungeonWorldProjectileStop::TargetLimit;
                else continue;
            }
            P.Active=false;P.Stop=Stop;P.LaunchObstructed=Contact.LaunchSegment;P.LaunchClearancePending=false;
            FDungeonWorldWeaponEvent Fact;Fact.Kind=EDungeonWorldWeaponEventKind::ProjectileStopped;Fact.Key=P.Key;
            Fact.AtTime=Contact.AtTime;Fact.Position=P.Position;Fact.Height=P.Source.Origin.Height;
            Fact.HasPoseSocket=P.HasPoseSocket;Fact.PoseSocket=P.PoseSocket;Fact.RangeAnchor=P.RangeAnchor;
            Fact.LaunchObstructed=P.LaunchObstructed;AppendWeaponWorldEvent(Fact);
        }
    }
}

void ADungeonGameMode::ApplyWorldBurn(const FPendingDamage& H)
{
    if (H.BurnDps<=0||H.BurnDuration<=0||!IsValid(H.Target)||H.Target->bDead) return;
    const uint64 Target=H.Target->GetRuntimeEntityId();
    FDungeonWorldBurn* Slot=nullptr;for (auto& B:WeaponWorld.Burns) if (B.TargetId==Target) {Slot=&B;break;}
    const bool Refresh=Slot&&Slot->Active;
    if (Refresh&&H.BurnDps<Slot->Dps) return;
    if (!Slot) {WeaponWorld.Burns.AddDefaulted();Slot=&WeaponWorld.Burns.Last();}
    const double Next=Refresh?Slot->NextTickAt:H.AtTime+1.0;
    Slot->Key=H.Source;Slot->TargetId=Target;Slot->Dps=H.BurnDps;Slot->AppliedAt=H.AtTime;
    Slot->ExpiresAt=H.AtTime+H.BurnDuration;Slot->NextTickAt=Next;Slot->Active=true;
    FDungeonWorldWeaponEvent Fact;Fact.Kind=Refresh?EDungeonWorldWeaponEventKind::BurnRefreshed:EDungeonWorldWeaponEventKind::BurnApplied;
    Fact.Key=H.Source;Fact.TargetId=Target;Fact.AtTime=H.AtTime;Fact.Damage=H.BurnDps;Fact.Magic=true;
    Fact.Position=H.Target->GetGroundPosition();Fact.Height=H.Target->JumpHeight;AppendWeaponWorldEvent(Fact);
}

void ADungeonGameMode::QueueWorldBurnTicks(double At)
{
    for (auto& B:WeaponWorld.Burns) if (B.Active)
    {
        auto Target=FindWorldFighter(B.TargetId);if (!IsValid(Target)||Target->bDead) continue;
        while (B.NextTickAt<=At&&B.NextTickAt<=B.ExpiresAt)
        {
            FPendingDamage H{FindWorldFighter(B.Key.OwnerId),Target,float(B.Dps),0.f,B.NextTickAt};
            H.Magic=true;H.DamageOverTime=true;H.Source=B.Key;H.ImpactPosition=Target->GetGroundPosition();H.ImpactHeight=Target->JumpHeight;
            PendingDamage.Add(H);B.NextTickAt+=1.0;
        }
    }
}

void ADungeonGameMode::ExpireWorldBurns(double At)
{
    for (auto& B:WeaponWorld.Burns) if (B.Active)
    {
        auto Target=FindWorldFighter(B.TargetId);
        if (IsValid(Target)&&!Target->bDead&&(At<B.ExpiresAt||B.NextTickAt<=B.ExpiresAt)) continue;
        B.Active=false;FDungeonWorldWeaponEvent Fact;Fact.Kind=EDungeonWorldWeaponEventKind::BurnExpired;
        Fact.Key=B.Key;Fact.TargetId=B.TargetId;Fact.AtTime=At;AppendWeaponWorldEvent(Fact);
    }
}

void ADungeonGameMode::CancelWorldWeaponWindows(uint64 OwnerId)
{
    if (!EquipmentRuntime->View.Bound) return;
    for (auto& W:WeaponWorld.Windows) if (W.Key.OwnerId==OwnerId) W.Active=false;
}

void ADungeonGameMode::ClearWorldRoomAttacks()
{
    for (auto& P:WeaponWorld.Projectiles) if (P.Active)
    {
        P.Active=false;P.Stop=EDungeonWorldProjectileStop::RoomExit;
        FDungeonWorldWeaponEvent Fact;Fact.Kind=EDungeonWorldWeaponEventKind::ProjectileStopped;Fact.Key=P.Key;
        Fact.AtTime=SimulationTime;Fact.Position=P.Position;Fact.Height=P.Source.Origin.Height;
        Fact.HasPoseSocket=P.HasPoseSocket;Fact.PoseSocket=P.PoseSocket;Fact.RangeAnchor=P.RangeAnchor;
        AppendWeaponWorldEvent(Fact);
    }
    for (auto& W:WeaponWorld.Windows) W.Active=false;
    for (auto& B:WeaponWorld.Burns) if (B.TargetId!=EquipmentRuntime->View.OwnerId) B.Active=false;
}
