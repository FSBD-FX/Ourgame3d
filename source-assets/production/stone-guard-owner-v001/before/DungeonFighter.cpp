#include "DungeonFighter.h"
#include "DungeonCombatRules.h"
#include "DungeonGameMode.h"
#include "DungeonRoomLayout.h"
#include "Components/SceneComponent.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"

namespace
{
bool RunInstallBlocksFighter(const ADungeonFighter& Fighter)
{
    const auto W=Fighter.GetWorld();const auto G=W?W->GetAuthGameMode<ADungeonGameMode>():nullptr;
    return G&&G->IsRunInstallGated();
}
}

namespace
{
namespace OwnerCombat=DungeonContentCombat;
namespace OwnerWA=DungeonWeaponActions;
namespace OwnerDodge=DungeonDodge;
using FOwnerSnapshot=FDungeonFighterOwnerSnapshot;
using FOwnerContext=FDungeonFighterRestoreContext;
struct FValidatedFighterOwner
{
    OwnerCombat::FCombatKernel Combat;
    OwnerWA::FWeaponActionsKernel Weapons;
    OwnerDodge::FDodgeKernel Dodge{1};
};
bool SameOwnerOrigin(const OwnerWA::FOrigin& A,const OwnerWA::FOrigin& B)
{return A.X==B.X&&A.Y==B.Y&&A.Height==B.Height;}
bool SameOwnerPose(const DungeonWeaponPoseSocket::FResolved& A,const DungeonWeaponPoseSocket::FResolved& B)
{
    if(A.Supported!=B.Supported||A.CustomOverride!=B.CustomOverride||A.GroundPoseFallback!=B.GroundPoseFallback
        ||A.Clip!=B.Clip||A.Frame!=B.Frame||A.WeaponStateIndex!=B.WeaponStateIndex||A.InstanceId!=B.InstanceId||A.ActionId!=B.ActionId)return false;
    const double X[]={A.SampleTime,A.Facing,A.RootX,A.RootY,A.BodySize,A.GripX,A.GripY,A.SupportX,A.SupportY,A.ComponentSupportX,
        A.ComponentSupportY,A.ComponentEmitX,A.ComponentEmitY,A.ComponentGripX,A.ComponentGripY,A.EmitX,A.EmitY,A.Angle,A.Scale};
    const double Y[]={B.SampleTime,B.Facing,B.RootX,B.RootY,B.BodySize,B.GripX,B.GripY,B.SupportX,B.SupportY,B.ComponentSupportX,
        B.ComponentSupportY,B.ComponentEmitX,B.ComponentEmitY,B.ComponentGripX,B.ComponentGripY,B.EmitX,B.EmitY,B.Angle,B.Scale};
    for(int32 I=0;I<UE_ARRAY_COUNT(X);++I)if(!FMath::IsFinite(X[I])||X[I]!=Y[I])return false;
    return SameOwnerOrigin(A.ActorOrigin,B.ActorOrigin)&&SameOwnerOrigin(A.CombatOrigin,B.CombatOrigin)
        &&SameOwnerOrigin(A.PresentationOrigin,B.PresentationOrigin);
}
bool SameOwnerWeaponAction(const OwnerWA::FAction& A,const OwnerWA::FAction& B)
{
    if(A.Type!=B.Type||A.Phase!=B.Phase||A.Weapon!=B.Weapon||A.InstanceId!=B.InstanceId||A.ActionId!=B.ActionId
        ||A.Active!=B.Active||A.Locked!=B.Locked||A.StartedAirborne!=B.StartedAirborne||A.ForwardStepIssued!=B.ForwardStepIssued
        ||A.NextSubhit!=B.NextSubhit||A.Critical!=B.Critical||A.Terminal!=B.Terminal)return false;
    const double X[]={A.Facing,A.Start,A.LockAt,A.ActiveAt,A.ActiveEnd,A.End,A.SpeedPct,A.DamagePct,A.StaggerPct,A.ReachPct,
        A.CritMultiplier,A.AmmoCost,A.FocusCost,A.CooldownDuration,A.ReloadSpeedPct,A.FocusCostPct,A.SkillCooldownPct};
    const double Y[]={B.Facing,B.Start,B.LockAt,B.ActiveAt,B.ActiveEnd,B.End,B.SpeedPct,B.DamagePct,B.StaggerPct,B.ReachPct,
        B.CritMultiplier,B.AmmoCost,B.FocusCost,B.CooldownDuration,B.ReloadSpeedPct,B.FocusCostPct,B.SkillCooldownPct};
    for(int32 I=0;I<UE_ARRAY_COUNT(X);++I)if(X[I]!=Y[I])return false;return true;
}
bool SameOwnerWeaponEvent(const OwnerWA::FEvent& A,const OwnerWA::FEvent& B)
{
    if(A.EventId!=B.EventId||A.ActionId!=B.ActionId||A.InstanceId!=B.InstanceId||A.SubhitId!=B.SubhitId||A.Kind!=B.Kind
        ||A.MaxTargets!=B.MaxTargets||A.Shape!=B.Shape||A.OriginPolicy!=B.OriginPolicy||!SameOwnerOrigin(A.Origin,B.Origin)
        ||!SameOwnerWeaponAction(A.Action,B.Action))return false;
    const double X[]={A.AtTime,A.WindowEnd,A.Damage,A.Stagger,A.MinRange,A.Range,A.Depth,A.ProjectileSpeed,A.SecondTargetRatio,
        A.BurnDps,A.BurnDuration,A.ForwardStep,A.AmmoConsumed,A.FocusConsumed};
    const double Y[]={B.AtTime,B.WindowEnd,B.Damage,B.Stagger,B.MinRange,B.Range,B.Depth,B.ProjectileSpeed,B.SecondTargetRatio,
        B.BurnDps,B.BurnDuration,B.ForwardStep,B.AmmoConsumed,B.FocusConsumed};
    for(int32 I=0;I<UE_ARRAY_COUNT(X);++I)if(X[I]!=Y[I])return false;return true;
}
bool ValidOwnerPose(const DungeonWeaponPoseSocket::FResolved& P)
{
    if(!SameOwnerPose(P,P)||!P.Supported||static_cast<uint32>(P.Clip)>static_cast<uint32>(DungeonWeaponPoseSocket::EClip::Reload)
        ||P.Clip==DungeonWeaponPoseSocket::EClip::None||P.Frame<0||P.Frame>=6||P.WeaponStateIndex< -1||P.WeaponStateIndex>3
        ||P.BodySize!=DungeonPresentationScale::CandidateBodySize||P.RootX!=256.||P.RootY!=472.||P.Scale<=0.
        ||(P.Facing!=1.&&P.Facing!=-1.))return false;
    for(const auto& O:{P.ActorOrigin,P.CombatOrigin,P.PresentationOrigin})
        if(!FMath::IsFinite(O.X)||!FMath::IsFinite(O.Y)||!FMath::IsFinite(O.Height)||O.Height<0.)return false;
    return true;
}
// UE5.5 SceneComponent.cpp InternalSetWorldLocationAndRotation retains the
// existing native location when FVector::Equals (its default tolerance) says
// no update is needed. Preserve both actual body and precise kernel positions;
// this predicate grants no movement and never rounds either saved value.
bool NativeOwnerPositionProjection(FVector2D Body,double KernelX,double KernelY)
{return FVector(KernelX,KernelY,0.).Equals(FVector(Body.X,Body.Y,0.));}
// Restore exact numerical component facts without the ordinary tiny-update
// suppression. The native cache retains the saved normalized quaternion.
void InstallOwnerRelativeTransform(USceneComponent* Component,const FTransform& Saved)
{
    const FRotator Rotation=Component->GetRelativeRotationCache().NormalizedQuatToRotator(Saved.GetRotation());
    Component->SetRelativeLocation_Direct(Saved.GetTranslation());
    Component->SetRelativeRotation_Direct(Rotation);
    Component->SetRelativeScale3D_Direct(Saved.GetScale3D());
    // Non-None forces ComponentToWorld even below UE_SMALL_NUMBER. These native
    // USceneComponents have no physics; no gameplay movement is performed.
    Component->UpdateComponentToWorld(EUpdateTransformFlags::SkipPhysicsUpdate,ETeleportType::TeleportPhysics);
}
bool ValidOwnerHeightAnchor(const FTransform& Saved)
{
    if(Saved.ContainsNaN()||!Saved.GetRotation().IsNormalized())return false;
    const auto Position=Saved.GetTranslation();const auto Scale=Saved.GetScale3D();
    // Native hierarchy only translates vertically and mirrors X. Do not equate
    // the retained values with current JumpHeight/Facing (including terminal).
    return Position.X==0.&&Position.Y==0.&&Position.Z>=0.
        &&Saved.GetRotation().Equals(FQuat::Identity,0.)
        &&(Scale.X==1.||Scale.X==-1.)&&Scale.Y==1.&&Scale.Z==1.;
}
bool ValidateFighterOwner(const FOwnerSnapshot& S,const FOwnerContext& C,FValidatedFighterOwner& Candidate,FString& Diagnostic)
{
    const auto Reject=[&Diagnostic](const TCHAR* Why){Diagnostic=Why;return false;};
    if(S.Schema!=2||!S.RunGuid.IsValid()||!S.RoomInstanceId||!S.EntityId
        ||S.RunGuid!=C.RunGuid||S.RoomInstanceId!=C.RoomInstanceId||S.EntityId!=C.EntityId
        ||!FMath::IsFinite(C.SimulationTime)||C.SimulationTime<0.||!C.Equipment||!C.WeaponWorld)
        return Reject(TEXT("Unknown fighter schema or missing/mismatched saved aggregate context"));
    const auto& E=*C.Equipment;const auto& V=E.View;const auto& W=*C.WeaponWorld;
    if(!V.Bound||V.RunGuid!=C.RunGuid||V.RoomInstanceId!=C.RoomInstanceId||W.RunGuid!=C.RunGuid||W.RoomInstanceId!=C.RoomInstanceId
        ||!FMath::IsFinite(W.Time)||W.Time<0.||W.Time>C.SimulationTime||!W.NextEntityId||!W.NextEventSequence)
        return Reject(TEXT("Saved equipment/world scope or time conflicts with fighter context"));
    // Validate the complete saved equipment owner, never the live target's GM.
    FDungeonEquipmentRuntime EquipmentCandidate;FString EquipmentWhy;
    if(!EquipmentCandidate.Restore(E,EquipmentWhy))
    {Diagnostic=TEXT("Saved equipment owner rejected: ")+EquipmentWhy;return false;}
    const FDungeonWorldActorBinding* Binding=nullptr;bool HasPlayerBinding=false;
    for(int32 I=0;I<W.ActorBindings.Num();++I)
    {
        const auto& B=W.ActorBindings[I];
        if(!B.EntityId||!B.RoomInstanceId||B.RoomInstanceId>C.RoomInstanceId||B.ContentId.IsEmpty())return Reject(TEXT("Malformed saved historical actor binding"));
        for(int32 J=0;J<I;++J)if(W.ActorBindings[J].EntityId==B.EntityId)return Reject(TEXT("Ambiguous saved stable actor identity"));
        // The one stable player binding retains its birth room across real
        // transfers. The loop above still rejects zero/future room identities.
        if(B.EntityId==V.OwnerId&&B.ContentId==TEXT("player"))HasPlayerBinding=true;
        if(B.EntityId!=V.OwnerId&&B.EntityId>=W.NextEntityId)return Reject(TEXT("Saved actor identity exceeds the world allocator"));
        if(B.EntityId==S.EntityId)Binding=&B;
    }
    const auto KnownEntity=[&W](uint64 Id){for(const auto& B:W.ActorBindings)if(B.EntityId==Id)return true;return false;};
    const bool Player=S.Kind==EDungeonFighterOwnerKind::BoundPlayer,Knight=S.Kind==EDungeonFighterOwnerKind::StoneKnight,Bat=S.Kind==EDungeonFighterOwnerKind::StoneBat;
    if(!HasPlayerBinding||!Binding||(!Player&&Binding->RoomInstanceId!=S.RoomInstanceId))
        return Reject(TEXT("Fighter is absent from the approved player birth/current enemy binding table"));
    if((!Player&&!Knight&&!Bat)||S.Player.IsSet()!=Player||S.Knight.IsSet()!=Knight||S.Bat.IsSet()!=Bat
        ||S.Enemy==Player||((S.EntityId==V.OwnerId)!=Player)
        ||Binding->ContentId!=(Player?TEXT("player"):Knight?TEXT("ENM-STN-001"):TEXT("ENM-STN-002"))
        ||(!Player&&S.EnemyContentId!=Binding->ContentId))return Reject(TEXT("Fighter kind, kernel variant, content, team or stable owner conflicts"));
    const float Nonnegative[]={S.Health,S.MaxHealth,S.JumpHeight,S.InvulnerableTime,S.HurtTime,S.AttackCooldown,S.PoiseAccumulation,
        S.PoiseDecayDelay,S.PoiseProtection,S.FocusMirror,S.AttackElapsed,S.ArmorChangeRemaining,S.FocusConsumeAge,
        S.AttackTime,S.HitFlash,S.AnimationTime,S.LandingVisualAge};
    for(float N:Nonnegative)if(!FMath::IsFinite(N)||N<0.f)return Reject(TEXT("Fighter has a nonfinite/negative body, timer or display value"));
    if(!FMath::IsFinite(S.GroundPosition.X)||!FMath::IsFinite(S.GroundPosition.Y)
        ||S.GroundPosition.X<DungeonRoomLayout::MinX||S.GroundPosition.X>DungeonRoomLayout::MaxX
        ||S.GroundPosition.Y<DungeonRoomLayout::MinY||S.GroundPosition.Y>DungeonRoomLayout::MaxY
        ||!FMath::IsFinite(S.JumpVelocity)||!FMath::IsFinite(S.Facing)||(S.Facing!=1.f&&S.Facing!=-1.f)
        ||S.MaxHealth<=0.f||S.Health>S.MaxHealth||S.Dead!=(S.Health==0.f)||S.DeathReported&&!S.Dead||S.Coins<0
        ||S.FocusMirror>100.f||S.ComboStage<0||S.ComboStage>3||S.LandingVisualAge>.12f
        ||!FMath::IsFinite(S.BatObservedHeight)||S.BatObservedHeight<0.||S.BatObservedHeight>90.
        ||S.CustomMuzzleRelative.ContainsNaN()||!S.CustomMuzzleRelative.GetRotation().IsNormalized()
        ||(!S.CustomMuzzle&&!S.CustomMuzzleRelative.Equals(FTransform::Identity,0.)))
        return Reject(TEXT("Fighter body, HP/death mirror, transform or display domain is invalid"));
    if(!ValidOwnerHeightAnchor(S.HeightAnchorRelative))
        return Reject(TEXT("Native height-anchor transform is nonfinite or outside its component structure domain"));
    if(!S.SkillWindows.empty()||!S.SkillHitReceipts.empty()||S.ArmorChangeRemaining!=0.f||!S.PendingArmorId.IsEmpty())
        return Reject(TEXT("Schema2 cannot silently discard a live legacy window or armor operation"));
    const auto& Protection=S.HurtProtectionSource;
    if(Protection.OwnerId)
    {
        bool Found=false;
        for(const auto& R:W.HitReceipts)if(R.TargetId==S.EntityId&&R.Key.OwnerId==Protection.OwnerId&&R.Key.ActionId==Protection.ActionId
            &&R.Key.EventId==Protection.EventId&&R.Key.SubhitId==Protection.SubhitId&&R.Key.RoomInstanceId==Protection.RoomInstanceId)Found=true;
        bool Committed=false;
        for(const auto& R:W.Events)if(R.Kind==EDungeonWorldWeaponEventKind::DirectHitCommitted&&R.ActualHPLoss>0.
            &&R.TargetId==S.EntityId&&R.Key.OwnerId==Protection.OwnerId&&R.Key.ActionId==Protection.ActionId
            &&R.Key.EventId==Protection.EventId&&R.Key.SubhitId==Protection.SubhitId&&R.Key.RoomInstanceId==Protection.RoomInstanceId)Committed=true;
        if(!Found||!Committed)return Reject(TEXT("Hurt protection has no saved committed world hit"));
    }
    else if(Protection.ActionId||Protection.EventId||Protection.SubhitId||Protection.RoomInstanceId)return Reject(TEXT("Partial hurt protection key"));
    if(Player)
    {
        const auto& P=S.Player.GetValue();const auto& A=P.WeaponActions;const auto& M=P.Combat;const auto& D=P.Dodge;const auto& I=E.InventoryState;
        Candidate.Combat=OwnerCombat::FCombatKernel(M.Weapon,M.WeaponInstanceId);
        Candidate.Dodge=OwnerDodge::FDodgeKernel(D.OwnerId,D.InitialTime,D.InitialPosition);
        if(!Candidate.Combat.Restore(M)||!Candidate.Weapons.Restore(A)||!Candidate.Dodge.Restore(D))
            return Reject(TEXT("Saved complete player kernel rejected its state/history"));
        if(M.Time>C.SimulationTime||A.Time>C.SimulationTime||D.Time>C.SimulationTime||D.OwnerId!=S.EntityId
            ||M.Dead!=S.Dead||A.Budget.Dead!=S.Dead||(D.Phase==OwnerDodge::EPhase::Dead)!=S.Dead
            ||C.GameOver&&!S.Dead||S.DeathReported&&!C.GameOver||S.FocusMirror!=float(A.Budget.Focus)
            ||S.MaxHealth!=float(V.Stats.MaxHP)||S.WeaponId!=V.Slots[V.ActiveSlot].ContentId||S.ArmorId!=V.Slots[2].ContentId
            ||A.EquippedId!=I.Weapons[I.ActiveSlot]||M.WeaponInstanceId!=A.EquippedId
            ||!Candidate.Weapons.Instance(A.EquippedId)||M.Weapon!=Candidate.Weapons.Instance(A.EquippedId)->Weapon
            ||!NativeOwnerPositionProjection(S.GroundPosition,D.Position.X,D.Position.Y)||S.LastSkillEventId>=A.NextEventId)
        {
            Diagnostic=FString::Printf(TEXT("Player saved projection mismatch: times=(%.17g,%.17g,%.17g)/master=%.17g owner=%llu/%llu dead=(%d,%d,%d)/%d gameover=%d reported=%d focus=%.17g/%.17g maxhp=%.17g/%.17g weapon=%s/%s armor=%s/%s equipped=%llu/%llu combatInstance=%llu dodgeXY=(%.17g,%.17g) bodyXY=(%.17g,%.17g) eventCursor=%llu/%llu"),
                M.Time,A.Time,D.Time,C.SimulationTime,static_cast<unsigned long long>(D.OwnerId),static_cast<unsigned long long>(S.EntityId),
                M.Dead,A.Budget.Dead,D.Phase==OwnerDodge::EPhase::Dead,S.Dead,C.GameOver,S.DeathReported,
                double(S.FocusMirror),double(float(A.Budget.Focus)),double(S.MaxHealth),double(float(V.Stats.MaxHP)),*S.WeaponId,*V.Slots[V.ActiveSlot].ContentId,
                *S.ArmorId,*V.Slots[2].ContentId,static_cast<unsigned long long>(A.EquippedId),static_cast<unsigned long long>(I.Weapons[I.ActiveSlot]),
                static_cast<unsigned long long>(M.WeaponInstanceId),D.Position.X,D.Position.Y,S.GroundPosition.X,S.GroundPosition.Y,
                static_cast<unsigned long long>(S.LastSkillEventId),static_cast<unsigned long long>(A.NextEventId));return false;
        }
        if(!S.Dead&&(A.Budget.Grounded!=(S.JumpHeight<=KINDA_SMALL_NUMBER&&S.JumpVelocity<=0.f)
            ||M.Grounded!=A.Budget.Grounded||(!A.Budget.Grounded&&S.AirPrimarySpent!=A.Budget.AirPrimarySpent)))
            return Reject(TEXT("Live player physical/accepted airborne budget conflict"));
        const bool Dodging=D.Phase==OwnerDodge::EPhase::Dodging;
        if((M.Action.Active&&A.Action.Active)||(Dodging&&(M.Action.Active||A.Action.Active))
            ||V.Action.Active&&(M.Action.Active||A.Action.Active||Dodging||S.Dead||S.JumpHeight>0.f||S.JumpVelocity>0.f||S.HurtTime>0.f))
            return Reject(TEXT("Mutually exclusive player actions conflict"));
        const auto FindItem=[&I](uint64 Id)->const DungeonEquipmentInventory::FItem*
        {for(const auto& Item:I.Items)if(Item.InstanceId==Id)return &Item;return nullptr;};
        for(uint64 Id:I.Weapons)if(Id&&!Candidate.Weapons.Instance(Id))return Reject(TEXT("Owned weapon is absent from saved WA imports"));
        for(const auto& Instance:A.Instances)
        {
            const auto Item=FindItem(Instance.InstanceId);const auto Def=OwnerCombat::GetWeaponDefinition(Instance.Weapon);
            if(!Item||!Def||Item->ContentId!=Def->ContentId||Item->Ammo!=Instance.Ammo||Item->SkillCooldownDeadline!=Instance.CooldownDeadline)
                return Reject(TEXT("Imported/retired weapon instance disagrees with saved inventory history"));
        }
        if(A.NextImportReceiptId!=V.NextImportReceiptId)return Reject(TEXT("Weapon import cursor disagrees with saved equipment owner"));
        for(const auto& R:A.Registrations)
        {
            if(R.Kind==OwnerWA::ERegistrationKind::Initial)
            {if(R.Initial.InstanceId!=I.StarterId||R.Initial.Ammo!=I.InitialStarter.Ammo||R.Initial.CooldownDeadline!=I.InitialStarter.SkillCooldownDeadline)
                return Reject(TEXT("WA initial registration disagrees with genuine starter"));}
            else if(R.Kind==OwnerWA::ERegistrationKind::ResolvedImport)
            {
                bool Acquired=false;
                for(const auto& O:I.Operations)if(O.Result.Ok()&&O.Result.AcquiredId==R.Initial.InstanceId&&O.Request.Action==DungeonEquipmentInventory::EAction::Pickup)
                    for(const auto& Source:I.Sources)if(Source.SourceId==O.Request.SourceId&&Source.SpawnItem.InstanceId==R.Initial.InstanceId
                        &&Source.SpawnItem.Ammo==R.Initial.Ammo&&Source.SpawnItem.SkillCooldownDeadline==R.Initial.CooldownDeadline)Acquired=true;
                if(!Acquired)return Reject(TEXT("Resolved WA import has no genuine saved inventory acquisition"));
            }
            else return Reject(TEXT("Legacy WA registration is unsupported in a bound owner"));
        }
        uint64 ExternalFocus=1;
        for(const auto& R:A.FocusHistory)if(R.Kind!=OwnerWA::EFocusChange::Emission&&R.ReceiptId!=ExternalFocus++)
            return Reject(TEXT("External focus history does not match its owner receipt domain"));
        if(ExternalFocus!=V.NextFocusReceiptId)return Reject(TEXT("External focus allocator conflicts with complete WA history"));
        // Both histories persist. Refill/spend/cooldown synchronization cannot be
        // inferred merely from the final magazine count.
        for(const auto& R:I.RuntimeUpdates)
        {
            int Matches=0;
            for(const auto& H:A.WeaponRuntimeHistory)if(H.Action.InstanceId==R.InstanceId&&H.AtTime==R.AtTime
                &&H.BeforeAmmo==R.BeforeAmmo&&H.AfterAmmo==R.Ammo&&H.BeforeCooldown==R.BeforeCooldown&&H.AfterCooldown==R.SkillCooldownDeadline)++Matches;
            if(Matches!=1)return Reject(TEXT("Inventory runtime receipt lacks one exact WA resource mutation"));
        }
        for(const auto& H:A.WeaponRuntimeHistory)if(H.BeforeAmmo!=H.AfterAmmo||H.BeforeCooldown!=H.AfterCooldown)
        {
            int Matches=0;for(const auto& R:I.RuntimeUpdates)if(H.Action.InstanceId==R.InstanceId&&H.AtTime==R.AtTime
                &&H.BeforeAmmo==R.BeforeAmmo&&H.AfterAmmo==R.Ammo&&H.BeforeCooldown==R.BeforeCooldown&&H.AfterCooldown==R.SkillCooldownDeadline)++Matches;
            if(Matches!=1)return Reject(TEXT("WA resource mutation lacks one exact committed inventory receipt"));
        }
        for(const auto& R:E.CritReceipts)
            if(R.ActionId>=(R.WeaponAction?A.NextActionId:M.NextAttackId)||R.EventId>=(R.WeaponAction?A.NextEventId:M.NextEventId)
                ||R.AtTime>(R.WeaponAction?A.Time:M.Time))return Reject(TEXT("Resolved crit receipt exceeds its saved action/event/time domain"));
        const auto CritMatches=[&E](bool WeaponAction,uint64 Id,double At,bool Critical,uint64 ExactEvent)
        {int Matches=0;for(const auto& R:E.CritReceipts)if(R.WeaponAction==WeaponAction&&R.ActionId==Id&&R.AtTime==At
            &&R.Critical==Critical&&(!ExactEvent||R.EventId==ExactEvent))++Matches;return Matches==1;};
        if(M.Action.AttackId&&M.Action.Locked&&!CritMatches(false,M.Action.AttackId,M.Action.LockTime,M.Action.Critical,0))
            return Reject(TEXT("Current melee lock lacks its resolved crit receipt"));
        for(const auto& H:M.IssuedWindows)if(!CritMatches(false,H.AttackId,H.FrozenAction.LockTime,H.FrozenAction.Critical,H.EventId-1))
            return Reject(TEXT("Historical melee window lacks its exact accepted lock draw"));
        if(A.Action.ActionId&&A.Action.Locked&&!CritMatches(true,A.Action.ActionId,A.Action.LockAt,A.Action.Critical,0))
            return Reject(TEXT("Current weapon lock lacks its resolved crit receipt"));
        for(const auto& H:A.Issued)if(!CritMatches(true,H.ActionId,H.Action.LockAt,H.Action.Critical,0))
            return Reject(TEXT("Historical weapon emission lacks its resolved lock draw"));
        for(const auto& H:M.HitReceipts)if(!KnownEntity(H.TargetId))return Reject(TEXT("Melee hit references an unknown saved historical entity"));
        for(std::size_t N=0;N<S.EmissionPoseSockets.size();++N)
        {
            const auto& FrozenPose=S.EmissionPoseSockets[N];const OwnerWA::FEvent* Event=nullptr;
            for(const auto& H:A.Issued)if(H.EventId==FrozenPose.EventId&&H.ActionId==FrozenPose.ActionId&&H.SubhitId==FrozenPose.SubhitId)Event=&H;
            if(!Event||Event->Kind!=OwnerWA::EEvent::ProjectileEmitted||Event->Action.Weapon!=OwnerCombat::EWeapon::XBW001
                ||!ValidOwnerPose(FrozenPose.Pose)||FrozenPose.Pose.SampleTime!=Event->AtTime||FrozenPose.Pose.ActionId!=FrozenPose.ActionId||FrozenPose.Pose.InstanceId!=Event->InstanceId
                ||FrozenPose.Pose.Facing!=Event->Action.Facing||!SameOwnerOrigin(FrozenPose.Pose.CombatOrigin,Event->Origin))
                return Reject(TEXT("Frozen emission pose lacks its exact accepted event/origin/geometry"));
            for(std::size_t J=0;J<N;++J)if(S.EmissionPoseSockets[J].EventId==FrozenPose.EventId
                ||S.EmissionPoseSockets[J].ActionId==FrozenPose.ActionId&&S.EmissionPoseSockets[J].SubhitId==FrozenPose.SubhitId)
                return Reject(TEXT("Duplicate frozen emission identity"));
            int Matches=0;
            for(const auto& Projectile:W.Projectiles)if(Projectile.Key.OwnerId==S.EntityId&&Projectile.Key.EventId==FrozenPose.EventId
                &&Projectile.Key.ActionId==FrozenPose.ActionId&&Projectile.Key.SubhitId==FrozenPose.SubhitId&&Projectile.HasPoseSocket
                &&Projectile.Key.RoomInstanceId&&Projectile.Key.RoomInstanceId<=S.RoomInstanceId
                &&SameOwnerWeaponEvent(Projectile.Source,*Event)&&SameOwnerPose(Projectile.PoseSocket,FrozenPose.Pose))++Matches;
            if(Matches!=1)return Reject(TEXT("Frozen emission has no exact immutable saved world projectile pose"));
        }
        for(const auto& H:A.Issued)if(H.Kind==OwnerWA::EEvent::ProjectileEmitted&&H.Action.Weapon==OwnerCombat::EWeapon::XBW001)
        {
            int Matches=0;for(const auto& FrozenPose:S.EmissionPoseSockets)if(FrozenPose.EventId==H.EventId&&FrozenPose.ActionId==H.ActionId&&FrozenPose.SubhitId==H.SubhitId)++Matches;
            if(Matches!=1)return Reject(TEXT("Accepted crossbow emission lost its frozen owner socket"));
        }
        // Clear only unaccepted physical input after validating its saved value.
        Candidate.Combat.ClearPendingInput();Candidate.Weapons.ClearPendingInput();
    }
    else
    {
        if(S.LastSkillEventId||!S.EmissionPoseSockets.empty())return Reject(TEXT("Stone owner contains unsupported player event obligations"));
        if(Knight)
        {
            const auto& K=S.Knight.GetValue();DungeonStoneKnight::FKnightKernel Pure(S.EntityId);
            const auto Def=DungeonStoneKnight::FKnightKernel::Definition();
            const bool KernelValid=Pure.Restore(K);
            if(!KernelValid||K.Time>C.SimulationTime||K.EntityId!=S.EntityId||S.Health!=float(K.HP)||S.MaxHealth!=float(Def.HP)
                ||S.Dead!=(K.Phase==DungeonStoneKnight::EPhase::Dead)||K.RewardClaimed!=S.DeathReported
                ||!NativeOwnerPositionProjection(S.GroundPosition,K.Position.X,K.Position.Y)||S.JumpHeight!=0.f||S.JumpVelocity!=0.f)
            {
                Diagnostic=FString::Printf(TEXT("Knight saved projection mismatch: kernelValid=%d time=%.17g/master=%.17g entity=%llu/%llu hp=%.17g/%.17g maxhp=%.17g/%.17g dead=%d/phase=%d reward=%d/reported=%d kernelXY=(%.17g,%.17g) bodyXY=(%.17g,%.17g) jump=%.17g velocity=%.17g"),
                    KernelValid,K.Time,C.SimulationTime,static_cast<unsigned long long>(K.EntityId),static_cast<unsigned long long>(S.EntityId),
                    double(S.Health),double(float(K.HP)),double(S.MaxHealth),Def.HP,S.Dead,int32(K.Phase),K.RewardClaimed,S.DeathReported,
                    K.Position.X,K.Position.Y,S.GroundPosition.X,S.GroundPosition.Y,double(S.JumpHeight),double(S.JumpVelocity));return false;
            }
            for(const auto& H:K.HitReceipts)if(!KnownEntity(H.TargetId))return Reject(TEXT("Knight hit references an unknown saved historical entity"));
        }
        else
        {
            const auto& B=S.Bat.GetValue();DungeonStoneBat::FBatKernel Pure(S.EntityId,B.InitialTime,B.InitialPosition);
            const auto Def=DungeonStoneBat::FBatKernel::Definition();
            const bool KernelValid=Pure.Restore(B);
            if(!KernelValid||B.Time>C.SimulationTime||B.EntityId!=S.EntityId||S.Health!=float(B.HP)||S.MaxHealth!=float(Def.HP)
                ||S.Dead!=(B.Phase==DungeonStoneBat::EPhase::Dead)||B.RewardClaimed!=S.DeathReported
                ||!NativeOwnerPositionProjection(S.GroundPosition,B.Position.X,B.Position.Y)||S.BatObservedHeight!=B.Position.Z||S.JumpVelocity!=0.f
                ||(!C.GameOver||!S.Dead?S.JumpHeight!=float(B.Position.Z):S.JumpHeight>float(B.Position.Z)))
            {
                Diagnostic=FString::Printf(TEXT("Bat saved projection mismatch: kernelValid=%d initialTime=%.17g time=%.17g/master=%.17g entity=%llu/%llu hp=%.17g/%.17g maxhp=%.17g/%.17g dead=%d/phase=%d reward=%d/reported=%d kernelXY=(%.17g,%.17g) bodyXY=(%.17g,%.17g) jump=%.17g/kernelZ=%.17g observedZ=%.17g velocity=%.17g gameover=%d"),
                    KernelValid,B.InitialTime,B.Time,C.SimulationTime,static_cast<unsigned long long>(B.EntityId),static_cast<unsigned long long>(S.EntityId),
                    double(S.Health),double(float(B.HP)),double(S.MaxHealth),Def.HP,S.Dead,int32(B.Phase),B.RewardClaimed,S.DeathReported,
                    B.Position.X,B.Position.Y,S.GroundPosition.X,S.GroundPosition.Y,double(S.JumpHeight),B.Position.Z,S.BatObservedHeight,double(S.JumpVelocity),C.GameOver);return false;
            }
            for(const auto& H:B.HitReceipts)if(!KnownEntity(H.TargetId))return Reject(TEXT("Bat hit references an unknown saved historical entity"));
            for(const auto& H:B.Issued)if(H.TargetId&&!KnownEntity(H.TargetId))return Reject(TEXT("Bat event references an unknown saved historical entity"));
        }
    }
    Diagnostic.Reset();return true;
}
}

bool ADungeonFighter::ValidateOwnerSnapshot(const FDungeonFighterOwnerSnapshot& Snapshot,
    const FDungeonFighterRestoreContext& Context,FString& Diagnostic)
{
    FValidatedFighterOwner Candidate;
    return ValidateFighterOwner(Snapshot,Context,Candidate,Diagnostic);
}

bool ADungeonFighter::CaptureOwnerSnapshot(FDungeonFighterOwnerSnapshot& Out,FString& Diagnostic,
    const FDungeonFighterRestoreContext* ExplicitStaging) const
{
    const auto Reject=[&Diagnostic](const TCHAR* Why){Diagnostic=Why;return false;};
    if(!RootComponent||!WeaponMuzzle||!WeaponMuzzleHeightAnchor
        ||WeaponMuzzleHeightAnchor->GetAttachParent()!=RootComponent||WeaponMuzzle->GetAttachParent()!=WeaponMuzzleHeightAnchor
        ||bResolvingContentWindow||bSuppressOrdinaryMovement)
        return Reject(TEXT("Fighter capture requires a complete stable owner outside a resolving batch"));
    const auto Transform=GetActorTransform();
    if(Transform.GetTranslation().Z!=0.||Transform.GetRotation()!=FQuat::Identity||Transform.GetScale3D()!=FVector::OneVector
        ||RootComponent->GetAttachParent())return Reject(TEXT("Schema2 supports the real flat, unattached native actor transform only"));
    FDungeonEquipmentRuntimeSnapshot Equipment;FOwnerContext Local;const FOwnerContext* Context=ExplicitStaging;
    if(!Context)
    {
        const auto Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
        if(!Game||!Game->EquipmentRuntime||!Game->EquipmentRuntime->View.Bound||Game->bSimulationBatch||Game->bSimulatingMotion
            ||!Game->PendingDamage.IsEmpty())return Reject(TEXT("Capture requires the true bound GM outside its full simulation/damage batch"));
        Equipment=Game->EquipmentRuntime->Capture();Local.Equipment=&Equipment;Local.WeaponWorld=&Game->WeaponWorld;
        Local.RunGuid=Equipment.View.RunGuid;Local.RoomInstanceId=Equipment.View.RoomInstanceId;
        Local.EntityId=Game->FindWorldEntityId(this);Local.SimulationTime=Game->SimulationTime;Local.GameOver=Game->bGameOver;Context=&Local;
        if(!Local.EntityId||(Game->PlayerFighter==this)!=(Local.EntityId==Equipment.View.OwnerId))
            return Reject(TEXT("Capture cannot substitute a QA/object ID for the true GM binding"));
    }
    FOwnerSnapshot S;S.RunGuid=Context->RunGuid;S.RoomInstanceId=Context->RoomInstanceId;S.EntityId=Context->EntityId;
    S.Kind=StoneKnight?EDungeonFighterOwnerKind::StoneKnight:StoneBat?EDungeonFighterOwnerKind::StoneBat:
        !bEnemy?EDungeonFighterOwnerKind::BoundPlayer:EDungeonFighterOwnerKind::Unsupported;
    if(StoneKnight&&StoneBat)return Reject(TEXT("Two stone drivers cannot own the same fighter"));
    S.GroundPosition=GetGroundPosition();
    S.Health=Health;
    S.MaxHealth=MaxHealth;
    S.JumpHeight=JumpHeight;
    S.JumpVelocity=JumpVelocity;
    S.Facing=Facing;
    S.Enemy=bEnemy;
    S.AIEnabled=bAIEnabled;
    S.Dead=bDead;
    S.DeathReported=bDeathReported;
    S.Coins=Coins;
    S.EnemyContentId=EnemyContentId;
    S.WeaponId=WeaponId;
    S.ArmorId=ArmorId;
    S.FocusMirror=Focus;
    S.InvulnerableTime=InvulnerableTime;
    S.HurtTime=HurtTime;
    S.AttackCooldown=AttackCooldown;
    S.PoiseAccumulation=PoiseAccumulation;
    S.PoiseDecayDelay=PoiseDecayDelay;
    S.PoiseProtection=PoiseProtection;
    S.AirPrimarySpent=bAirPrimarySpent;
    S.HurtProtectionSource=HurtProtectionSource;
    S.LastSkillEventId=LastSkillEventId;
    S.SkillWindows=SkillWindows;
    S.AttackElapsed=AttackElapsed;
    S.ArmorChangeRemaining=ArmorChangeRemaining;
    S.FocusConsumeAge=FocusConsumeAge;
    S.AttackResolved=bAttackResolved;
    S.HasAxe=bHasAxe;
    S.PendingArmorId=PendingArmorId;
    S.AttackTime=AttackTime;
    S.HitFlash=HitFlash;
    S.AnimationTime=AnimationTime;
    S.LandingVisualAge=LandingVisualAge;
    S.ComboStage=ComboStage;
    S.Moving=bMoving;
    S.AnimationName=AnimationName;
    S.AttackPhase=AttackPhase;
    S.BatObservedHeight=BatObservedHeight;
    S.HeightAnchorRelative=WeaponMuzzleHeightAnchor->GetRelativeTransform();
    S.CustomMuzzle=bWeaponMuzzleCustomOverride||!WeaponMuzzle->GetRelativeTransform().Equals(LastAutomaticMuzzleTransform,0.);
    if(S.CustomMuzzle)S.CustomMuzzleRelative=WeaponMuzzle->GetRelativeTransform();
    for(const auto& P:EmissionPoseSockets)S.EmissionPoseSockets.push_back({P.EventId,P.ActionId,P.SubhitId,P.Pose});
    for(const auto& H:SkillHitReceipts)S.SkillHitReceipts.push_back({H.ActionId,H.SubhitId,H.TargetId});
    if(S.Kind==EDungeonFighterOwnerKind::BoundPlayer)S.Player=FDungeonPlayerKernelSnapshot{Combat.Capture(),WeaponSkills.Capture(),Dodge.Capture()};
    if(StoneKnight)S.Knight=StoneKnight->Capture();if(StoneBat)S.Bat=StoneBat->Capture();
    FValidatedFighterOwner Candidate;if(!ValidateFighterOwner(S,*Context,Candidate,Diagnostic))return false;
    Out=MoveTemp(S);Diagnostic.Reset();return true;
}
bool ADungeonFighter::RestoreOwnerSnapshot(const FDungeonFighterOwnerSnapshot& S,
    const FDungeonFighterRestoreContext& Context,FString& Diagnostic)
{
    if(!RootComponent||!WeaponMuzzle||!WeaponMuzzleHeightAnchor||RootComponent->GetAttachParent()
        ||WeaponMuzzleHeightAnchor->GetAttachParent()!=RootComponent||WeaponMuzzle->GetAttachParent()!=WeaponMuzzleHeightAnchor
        ||bResolvingContentWindow||bSuppressOrdinaryMovement)
    {Diagnostic=TEXT("Restore requires independent native owner components outside a resolving batch");return false;}
    FValidatedFighterOwner Candidate;if(!ValidateFighterOwner(S,Context,Candidate,Diagnostic))return false;
    // Construct weak-owner drivers only after the full pure candidate passes.
    // Neither constructor reads a live GM or issues an action/reward.
    TUniquePtr<FDungeonStoneKnightDriver> NewKnight;TUniquePtr<FDungeonStoneBatDriver> NewBat;
    DungeonStoneFeedback::FJournal NewFeedback;
    if(S.Knight.IsSet())
    {
        NewKnight=MakeUnique<FDungeonStoneKnightDriver>(this,S.EntityId,S.Knight.GetValue().Time);
        if(!NewKnight->Restore(S.Knight.GetValue())||!NewFeedback.Begin(S.EntityId,S.Knight.GetValue().NextEventId))
        {Diagnostic=TEXT("Knight candidate driver/feedback rejected the saved tail");return false;}
    }
    if(S.Bat.IsSet())
    {
        const auto& B=S.Bat.GetValue();NewBat=MakeUnique<FDungeonStoneBatDriver>(this,S.EntityId,B.InitialTime,B.InitialPosition);
        if(!NewBat->Restore(B)){Diagnostic=TEXT("Bat candidate driver rejected immutable saved birth origin/time");return false;}
    }
    std::vector<FEmissionPoseSocket> NewPoses;std::vector<FSkillHitReceipt> NewHits;
    for(const auto& P:S.EmissionPoseSockets)NewPoses.push_back({P.EventId,P.ActionId,P.SubhitId,P.Pose});
    for(const auto& H:S.SkillHitReceipts)NewHits.push_back({H.ActionId,H.SubhitId,H.TargetId});
    FTransform Muzzle=FTransform::Identity;
    if(S.CustomMuzzle)Muzzle=S.CustomMuzzleRelative;
    else if(S.Player.IsSet())
    {
        DungeonWeaponPoseSocket::FResolved Pose;
        DungeonWeaponPoseSocket::Resolve(Candidate.Weapons.State(),Candidate.Weapons.State().Time,double(S.AnimationTime),Pose);
        if(Pose.Supported)Muzzle=FTransform(FQuat::Identity,FVector((Pose.EmitX-Pose.RootX)*Pose.BodySize/512./.65,0.,
            (Pose.RootY-Pose.EmitY)*Pose.BodySize/512./.7),FVector::OneVector);
    }
    // No fallible validation, simulation or external effect follows this point.
    Combat=MoveTemp(Candidate.Combat);WeaponSkills=MoveTemp(Candidate.Weapons);Dodge=MoveTemp(Candidate.Dodge);
    StoneKnight=MoveTemp(NewKnight);StoneBat=MoveTemp(NewBat);StoneFeedback=MoveTemp(NewFeedback);
    Health=S.Health;
    MaxHealth=S.MaxHealth;
    JumpHeight=S.JumpHeight;
    JumpVelocity=S.JumpVelocity;
    Facing=S.Facing;
    bEnemy=S.Enemy;
    bAIEnabled=S.AIEnabled;
    bDead=S.Dead;
    bDeathReported=S.DeathReported;
    Coins=S.Coins;
    EnemyContentId=S.EnemyContentId;
    WeaponId=S.WeaponId;
    ArmorId=S.ArmorId;
    Focus=S.FocusMirror;
    InvulnerableTime=S.InvulnerableTime;
    HurtTime=S.HurtTime;
    AttackCooldown=S.AttackCooldown;
    PoiseAccumulation=S.PoiseAccumulation;
    PoiseDecayDelay=S.PoiseDecayDelay;
    PoiseProtection=S.PoiseProtection;
    bAirPrimarySpent=S.AirPrimarySpent;
    HurtProtectionSource=S.HurtProtectionSource;
    LastSkillEventId=S.LastSkillEventId;
    SkillWindows=S.SkillWindows;
    AttackElapsed=S.AttackElapsed;
    ArmorChangeRemaining=S.ArmorChangeRemaining;
    FocusConsumeAge=S.FocusConsumeAge;
    bAttackResolved=S.AttackResolved;
    bHasAxe=S.HasAxe;
    PendingArmorId=S.PendingArmorId;
    AttackTime=S.AttackTime;
    HitFlash=S.HitFlash;
    AnimationTime=S.AnimationTime;
    LandingVisualAge=S.LandingVisualAge;
    ComboStage=S.ComboStage;
    bMoving=S.Moving;
    AnimationName=S.AnimationName;
    AttackPhase=S.AttackPhase;
    BatObservedHeight=S.BatObservedHeight;
    EmissionPoseSockets=MoveTemp(NewPoses);SkillHitReceipts=MoveTemp(NewHits);
    HitAction={};bResolvingContentWindow=false;BatchSkillStepAt=-1.;BatchSkillStepDelta=FVector2D::ZeroVector;
    bSuppressOrdinaryMovement=false;bEquipmentUiArrowLatch=false;
    LastStoneSyncTime=S.Knight.IsSet()?S.Knight.GetValue().Time:0.;LastBatSyncTime=S.Bat.IsSet()?S.Bat.GetValue().Time:0.;
    // The native, unattached SceneComponent root has no collision/physics.
    // This public exact path assigns saved body XY even when the ordinary
    // movement setter would suppress a tiny correction. Kernel XY is untouched.
    RootComponent->SetRelativeScale3D(FVector::OneVector);
    RootComponent->SetWorldLocationAndRotationNoPhysics(FVector(S.GroundPosition.X,S.GroundPosition.Y,0.),FRotator::ZeroRotator);
    // NoPhysics assigns relative values; this explicit force also installs the
    // actual world value when its delta is below the secondary UE_SMALL_NUMBER.
    RootComponent->UpdateComponentToWorld(EUpdateTransformFlags::SkipPhysicsUpdate,ETeleportType::TeleportPhysics);
    InstallOwnerRelativeTransform(WeaponMuzzleHeightAnchor,S.HeightAnchorRelative);
    bWeaponMuzzleCustomOverride=S.CustomMuzzle;
    InstallOwnerRelativeTransform(WeaponMuzzle,Muzzle);
    LastAutomaticMuzzleTransform=S.CustomMuzzle?FTransform::Identity:Muzzle;
    SetActorTickEnabled(false);Diagnostic.Reset();return true;
}

ADungeonFighter::ADungeonFighter()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.bStartWithTickEnabled = false;
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("GroundAnchor"));
    WeaponMuzzleHeightAnchor = CreateDefaultSubobject<USceneComponent>(TEXT("WeaponMuzzleHeightAnchor"));
    WeaponMuzzleHeightAnchor->SetupAttachment(RootComponent);
    WeaponMuzzle = CreateDefaultSubobject<USceneComponent>(TEXT("WeaponMuzzle"));
    WeaponMuzzle->SetupAttachment(WeaponMuzzleHeightAnchor);
    // Zero authored socket offset until the ranged art supplies its actual hold point.
    SetActorEnableCollision(false);
    AutoPossessAI = EAutoPossessAI::Disabled;
    bUseControllerRotationYaw = false;
}

FVector2D ADungeonFighter::GetGroundPosition() const
{
    const FVector Location = GetActorLocation();
    return FVector2D(Location.X, Location.Y);
}

bool ADungeonFighter::IsEquipmentBound() const
{
    const auto Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    return Game && Game->PlayerFighter==this && Game->GetEquipmentView().Bound;
}

double ADungeonFighter::GetEquipmentActionDeadline() const
{
    const auto Game=GetWorld()->GetAuthGameMode<ADungeonGameMode>();
    return IsEquipmentBound() && Game->GetEquipmentView().Action.Active ? Game->GetEquipmentView().Action.Deadline : 0.0;
}

bool ADungeonFighter::IsContentMelee() const
{
    return !bEnemy && (WeaponId == TEXT("sword") || WeaponId == TEXT("WPN-SWD-001")
        || WeaponId == TEXT("WPN-GSW-001") || WeaponId == TEXT("WPN-SPR-001"));
}

DungeonContentCombat::EWeapon ADungeonFighter::ContentWeapon() const
{
    using namespace DungeonContentCombat;
    if (WeaponId == TEXT("WPN-GSW-001")) return EWeapon::GSW001;
    if (WeaponId == TEXT("WPN-SPR-001")) return EWeapon::SPR001;
    if (WeaponId == TEXT("WPN-XBW-001")) return EWeapon::XBW001;
    if (WeaponId == TEXT("WPN-STF-001")) return EWeapon::STF001;
    return EWeapon::SWD001;
}

DungeonContentCombat::FAttackContext ADungeonFighter::CombatContext() const
{
    DungeonContentCombat::FAttackContext Context;
    Context.Facing = Facing;
    Context.Grounded = JumpHeight <= KINDA_SMALL_NUMBER && JumpVelocity <= 0.f;
    Context.CanStart = !bDead && HurtTime <= 0.f && ArmorChangeRemaining <= 0.f && !WeaponSkills.State().Action.Active
        && Dodge.State().Phase != DungeonDodge::EPhase::Dodging;
    if (IsEquipmentBound())
    {
        const auto Game=GetWorld()->GetAuthGameMode<ADungeonGameMode>();const auto& R=*Game->EquipmentRuntime;
        const auto& S=R.View.Stats;using DungeonEquipmentStats::EStat;
        Context.CanStart=Context.CanStart&&!R.View.Action.Active;
        Context.ActionSpeedPct=S.Final[EStat::ActionSpeedPct];Context.DamagePct=S.Final[EStat::DamagePct];
        Context.StaggerPct=S.Final[EStat::StaggerPct];Context.ReachPct=S.Final[EStat::ReachPct];
        Context.CritMultiplier=S.CritMultiplier;Context.Critical=R.PeekCritical();
    }
    return Context;
}

void ADungeonFighter::SyncContentAction()
{
    using namespace DungeonContentCombat;
    const auto& State = Combat.State();
    const auto& Action = State.Action;
    AttackTime = Action.Active ? float(FMath::Max(0.0, Action.End - State.Time)) : 0.f;
    ComboStage = Action.Active ? int32(Action.Stage + 1) : 0;
    AttackPhase = Action.Phase == EPhase::Windup ? TEXT("windup")
        : Action.Phase == EPhase::Active ? TEXT("active")
        : Action.Phase == EPhase::Recovery ? TEXT("recovery") : TEXT("idle");
    if (Action.Active)
    {
        Facing = float(Action.Facing);
        AnimationName = TEXT("attack");
        AnimationTime = float(FMath::Max(0.0, State.Time - Action.Start));
    }
}

void ADungeonFighter::AdvanceContentActionTo(double Now)
{
    using namespace DungeonContentCombat;
    const auto Events = Combat.StepTo(Now, CombatContext());
    for (const auto& Event : Events)
    {
        if (Event.Kind==EEventKind::Locked && IsEquipmentBound())
            GetWorld()->GetAuthGameMode<ADungeonGameMode>()->EquipmentRuntime->ObserveCritLock(false,Event.AttackId,Event.EventId,Event.AtTime,Event.Action.Critical);
        if (Event.Kind == EEventKind::ActiveWindow)
        {
            const TCHAR* Family = Event.Action.Weapon == EWeapon::GSW001 ? TEXT("GSW")
                : Event.Action.Weapon == EWeapon::SPR001 ? TEXT("SPR") : TEXT("SWD");
            const TCHAR* Cue = Event.Action.Weapon == EWeapon::SPR001 ? TEXT("THRUST") : TEXT("WHOOSH");
            const FString AudioCue=FString::Printf(TEXT("%s_%s_%02d"),Family,Cue,Event.Stage+1);
            if(IsEquipmentBound())
            {
                if(auto Game=GetWorld()->GetAuthGameMode<ADungeonGameMode>())
                    Game->AppendActionAudio(*AudioCue,Event.AtTime,GetRuntimeEntityId(),Event.AttackId,
                        Event.Action.WeaponInstanceId,0,Game->GetEquipmentView().Revision);
            }
            else
            {
                // Historical unbound prototypes retain their original direct path.
                const FString Name=TEXT("SW_AUD_")+AudioCue+TEXT("_v001");
                const FString SoundPath=FString::Printf(TEXT("/Game/Production/FirstBatch/v001/Audio/%s.%s"),*Name,*Name);
                if(auto Sound=LoadObject<USoundBase>(nullptr,*SoundPath))UGameplayStatics::PlaySound2D(this,Sound,.25f);
            }
            HitAction = Event.Action;
            bResolvingContentWindow = true;
            if (auto Game = GetWorld()->GetAuthGameMode<ADungeonGameMode>()) Game->ResolveAttack(this);
            bResolvingContentWindow = false;
        }
    }
    SyncContentAction();
    if (IsAttackActive())
        if (auto Game = GetWorld()->GetAuthGameMode<ADungeonGameMode>()) Game->ResolveAttack(this);
}

bool ADungeonFighter::IsAttackActive() const
{
    return bResolvingContentWindow || (IsContentMelee() && Combat.State().Action.Active
        && Combat.State().Action.Phase == DungeonContentCombat::EPhase::Active);
}

float ADungeonFighter::GetAttackMinRange() const
{
    return IsContentMelee() ? float((bResolvingContentWindow ? HitAction : Combat.State().Action).MinRange) : 0.f;
}

bool ADungeonFighter::CanContentHit(ADungeonFighter* Target) const
{
    if (!Target || !IsAttackActive()) return false;
    const auto& Action = bResolvingContentWindow ? HitAction : Combat.State().Action;
    const auto Delta = Target->GetGroundPosition() - GetGroundPosition();
    const double X = Delta.X * Action.Facing;
    if (X < Action.MinRange || X > Action.Range || FMath::Abs(Delta.Y) > Action.Depth
        || FMath::Abs(Target->GetCombatHeight() - GetCombatHeight()) > 65.) return false;
    if (Action.Shape == DungeonContentCombat::EShape::ForwardEllipse)
        return FMath::Square(X / Action.Range) + FMath::Square(Delta.Y / Action.Depth) <= 1.0;
    return true;
}

bool ADungeonFighter::MarkContentHit(ADungeonFighter* Target)
{
    if(RunInstallBlocksFighter(*this))return false;
    const auto& Action = bResolvingContentWindow ? HitAction : Combat.State().Action;
    if (Action.Weapon == DungeonContentCombat::EWeapon::SPR001)
        for (const auto& Hit : Combat.State().HitReceipts)
            if (Hit.AttackId == Action.AttackId && Hit.SubhitId == 0) return false;
    // Runtime identity only until the persistent SpawnID adapter is connected.
    return Target && Combat.TryMarkHit(Action.AttackId, 0, IsEquipmentBound()?Target->GetRuntimeEntityId():Target->GetUniqueID());
}

float ADungeonFighter::GetActionProgress() const
{
    const auto& Action = Combat.State().Action;
    return IsContentMelee() && Action.Active
        ? float(FMath::Clamp((Combat.State().Time - Action.Start) / (Action.End - Action.Start), 0.0, 1.0)) : 0.f;
}

int32 ADungeonFighter::GetPrimaryPoseFrame() const
{
    const auto& Action = Combat.State().Action;
    if (!IsContentMelee() || !Action.Active) return 0;
    const double Now = Combat.State().Time;
    const double Start = Now < Action.ActiveStart ? Action.Start : Now < Action.ActiveEnd ? Action.ActiveStart : Action.ActiveEnd;
    const double End = Now < Action.ActiveStart ? Action.ActiveStart : Now < Action.ActiveEnd ? Action.ActiveEnd : Action.End;
    const int32 Base = Now < Action.ActiveStart ? 0 : Now < Action.ActiveEnd ? 2 : 4;
    return Base + FMath::Clamp(FMath::FloorToInt((Now-Start)/(End-Start)*2.0),0,1);
}

void ADungeonFighter::ClearPendingAttackInput() {
    if(RunInstallBlocksFighter(*this))return; Combat.ClearPendingInput(); WeaponSkills.ClearPendingInput(); }
void ADungeonFighter::CommitIdleDodgePosition()
{
    if (bEnemy || Dodge.State().Phase != DungeonDodge::EPhase::Idle) return;
    const auto P=GetGroundPosition(); const auto& S=Dodge.State();
    if (S.Position.X==P.X && S.Position.Y==P.Y) return;
    ensureMsgf(Dodge.CommitResolvedIdlePosition(S.Time,{P.X,P.Y},S.NextPositionReceiptId),
        TEXT("Resolved actor movement must enter the persistent dodge position receipt domain."));
}

bool ADungeonFighter::TryBeginDodge(FVector2D MoveIntent, bool FreshPress)
{
    if(RunInstallBlocksFighter(*this))return false;
    auto Game=GetWorld()->GetAuthGameMode<ADungeonGameMode>();
    if (!Game || Game->bGameOver || Game->bWaitingForStart || bEnemy || bDead || HurtTime>0.f
        || Combat.State().Action.Active || AttackCooldown>0.f
        || (AttackTime>0.f&&!(WeaponSkills.State().Action.Active&&WeaponSkills.State().Action.Type==DungeonWeaponActions::EAction::Reload))
        || (WeaponSkills.State().Action.Active && WeaponSkills.State().Action.Type!=DungeonWeaponActions::EAction::Reload)
        || Game->GetSimulationTime()!=Dodge.State().Time) return false;
    if (IsEquipmentBound() && Game->GetEquipmentView().Action.Active
        && Game->GetEquipmentView().Action.Kind==EDungeonEquipmentActionKind::SwitchWeapon) return false;
    DungeonDodge::FContext C;
    C.FreshPress=FreshPress; C.Grounded=JumpHeight<=KINDA_SMALL_NUMBER && JumpVelocity<=0.f;
    C.CanStart=true; C.Facing=Facing<0.f?-1:1; C.MoveIntent={MoveIntent.X,MoveIntent.Y};
    // A failed request has no cancellation, receipt or resource side effects.
    const auto R=Dodge.TryStart(Dodge.State().Time,C);
    if (!R.Accepted) return false;
    if (IsEquipmentBound()) Game->CancelEquipmentAction();
    ArmorChangeRemaining=0.f; PendingArmorId.Reset();
    Combat.Interrupt(DungeonContentCombat::EInterruptReason::ExclusiveAction);
    WeaponSkills.Interrupt(DungeonWeaponActions::EInterrupt::ExclusiveAction);
    if(IsEquipmentBound())Game->ObservePendingActionAudio(this);
    ClearPendingAttackInput();
    SyncDodgeAction();
    return true;
}

bool ADungeonFighter::IsDodgeInvulnerableAt(double HitTime) const { return !bEnemy && Dodge.IsDirectInvulnerableAt(HitTime); }

void ADungeonFighter::SyncDodgeAction()
{
    const auto& S=Dodge.State();
    if (S.Phase!=DungeonDodge::EPhase::Dodging || S.Records.empty()) return;
    SetActorLocation(FVector(S.Position.X,S.Position.Y,0.0));
    const auto& R=S.Records.back();
    AttackTime=0.f; ComboStage=0; AttackPhase=TEXT("dodge");
    AnimationName=TEXT("dodge"); AnimationTime=float(S.Time-R.Start);
    bMoving=R.Block==DungeonDodge::EBlock::None;
}

DungeonWeaponActions::FContext ADungeonFighter::WeaponSkillContext() const
{
    DungeonWeaponActions::FContext C;
    C.Facing = Facing;
    C.Grounded = JumpHeight <= KINDA_SMALL_NUMBER && JumpVelocity <= 0.f;
    C.CanStart = !bDead && HurtTime <= 0.f && ArmorChangeRemaining <= 0.f && !Combat.State().Action.Active
        && Dodge.State().Phase != DungeonDodge::EPhase::Dodging;
    C.FocusRegen = 0.0; // Historical unbound QA only; bound Run reads its sole WA budget below.
    if (IsEquipmentBound())
    {
        static_cast<DungeonContentCombat::FAttackContext&>(C)=CombatContext();
        const auto& S=GetWorld()->GetAuthGameMode<ADungeonGameMode>()->GetEquipmentView().Stats;
        using DungeonEquipmentStats::EStat;
        C.CanStart=C.CanStart&&!Combat.State().Action.Active;
        C.FocusCostPct=S.Final[EStat::FocusCostPct];C.SkillCooldownPct=S.Final[EStat::SkillCooldownPct];
        C.ReloadSpeedPct=S.Final[EStat::ReloadSpeedPct];C.FocusRegen=S.FocusRegen;C.FocusDelay=S.FocusDelay;
        // CombatContext excludes the other action domain. Its own WA.Active
        // must not prevent WA from finishing, buffering, or starting auto reload.
        C.CanStart=!bDead&&HurtTime<=0.f&&ArmorChangeRemaining<=0.f&&!Combat.State().Action.Active
            &&Dodge.State().Phase!=DungeonDodge::EPhase::Dodging&&!GetWorld()->GetAuthGameMode<ADungeonGameMode>()->GetEquipmentView().Action.Active;
        // A physical landing is committed to WA after endpoint damage. Tiny
        // positive heights and the landed actor cannot predate that transition.
        C.Grounded=WeaponSkills.State().Budget.Grounded;
    }
    C.Muzzle=GetWeaponMuzzleOrigin();
    return C;
}

bool ADungeonFighter::TryBeginWeaponSkill(bool FreshPress)
{
    if(RunInstallBlocksFighter(*this))return false;
    ADungeonGameMode* Game = GetWorld()->GetAuthGameMode<ADungeonGameMode>();
    const bool Supported=WeaponId==TEXT("sword") || WeaponId==TEXT("WPN-SWD-001") || IsEquipmentBound();
    if (!FreshPress || bEnemy || !Supported
        || !Game || Game->bGameOver || Game->bWaitingForStart || !CanStartAttack()
        || JumpHeight > KINDA_SMALL_NUMBER || JumpVelocity > 0.f
        || Game->GetSimulationTime() != WeaponSkills.State().Time) return false;
    if (!WeaponSkills.TryStart(DungeonWeaponActions::EAction::Skill, WeaponSkills.State().Time, WeaponSkillContext(), true)) return false;
    // This cannot cancel an active primary: the common gate above must succeed first.
    Combat.Interrupt(DungeonContentCombat::EInterruptReason::ExclusiveAction);
    SkillWindows.clear(); SkillHitReceipts.clear();
    SyncWeaponSkillAction();
    return true;
}

bool ADungeonFighter::TryBeginReload(bool FreshPress)
{
    if(RunInstallBlocksFighter(*this))return false;
    auto Game=GetWorld()->GetAuthGameMode<ADungeonGameMode>();
    if (!FreshPress||!IsEquipmentBound()||bEnemy||bDead||!Game||Game->bGameOver||Game->bWaitingForStart
        ||Game->GetSimulationTime()!=WeaponSkills.State().Time||HurtTime>0.f
        ||Combat.State().Action.Active||Dodge.State().Phase==DungeonDodge::EPhase::Dodging
        ||Game->GetEquipmentView().Action.Active||JumpHeight>KINDA_SMALL_NUMBER||JumpVelocity>0.f) return false;
    if (!WeaponSkills.PressReload(WeaponSkills.State().Time,WeaponSkillContext(),true)) return false;
    Game->ObservePendingActionAudio(this);
    Combat.Interrupt(DungeonContentCombat::EInterruptReason::ExclusiveAction);
    SyncWeaponSkillAction();return true;
}

void ADungeonFighter::SyncWeaponMuzzleTransform(double SampleTime)
{
    if(!WeaponMuzzle->GetRelativeTransform().Equals(LastAutomaticMuzzleTransform,0.))bWeaponMuzzleCustomOverride=true;
    WeaponMuzzleHeightAnchor->SetRelativeLocation(FVector(0,0,JumpHeight));
    WeaponMuzzleHeightAnchor->SetRelativeScale3D(FVector(Facing<0.f?-1.0:1.0,1,1));
    if(bWeaponMuzzleCustomOverride)return;
    const auto Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    const double At=SampleTime>=0.?SampleTime:Game?Game->GetSimulationTime():WeaponSkills.State().Time;
    const auto Pose=ResolveWeaponPoseSocketAt(At);
    const FVector Offset=Pose.Supported?FVector((Pose.EmitX-Pose.RootX)*Pose.BodySize/512./.65,0.,
        (Pose.RootY-Pose.EmitY)*Pose.BodySize/512./.7):FVector::ZeroVector;
    WeaponMuzzle->SetRelativeTransform(FTransform(FQuat::Identity,Offset,FVector::OneVector));
    LastAutomaticMuzzleTransform=WeaponMuzzle->GetRelativeTransform();
}

DungeonWeaponActions::FOrigin ADungeonFighter::GetWeaponMuzzleOrigin() const
{
    const FVector P=WeaponMuzzle->GetComponentLocation();
    const bool Custom=bWeaponMuzzleCustomOverride||!WeaponMuzzle->GetRelativeTransform().Equals(LastAutomaticMuzzleTransform,0.);
    return {P.X,P.Y,Custom?FMath::Max(0.0,P.Z):double(JumpHeight)};
}

DungeonWeaponPoseSocket::FResolved ADungeonFighter::ResolveWeaponPoseSocketAt(double SampleTime) const
{
    DungeonWeaponPoseSocket::FResolved Out;
    DungeonWeaponPoseSocket::Resolve(WeaponSkills.State(),SampleTime,double(AnimationTime),Out);
    Out.Facing=Facing<0.f?-1.:1.;
    const auto Ground=GetGroundPosition();Out.ActorOrigin={Ground.X,Ground.Y,double(JumpHeight)};
    Out.CustomOverride=bWeaponMuzzleCustomOverride||!WeaponMuzzle->GetRelativeTransform().Equals(LastAutomaticMuzzleTransform,0.);
    Out.CombatOrigin=GetWeaponMuzzleOrigin();Out.PresentationOrigin=Out.CombatOrigin;
    if(Out.Supported&&!Out.CustomOverride)
    {
        // The synchronized physical component is the sole world-space mouth authority.
        // SyncWeaponMuzzleTransform still derives that component from authored geometry.
        Out.PresentationOrigin.Height=WeaponMuzzle->GetComponentLocation().Z;
    }
    return Out;
}

DungeonWeaponPoseSocket::FResolved ADungeonFighter::GetWeaponPoseSocket() const
{
    const auto Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    return ResolveWeaponPoseSocketAt(Game?Game->GetSimulationTime():WeaponSkills.State().Time);
}

const DungeonWeaponPoseSocket::FResolved* ADungeonFighter::FindWeaponEmissionPoseSocket(uint64 ActionId,uint32 SubhitId) const
{
    for(const auto& Snapshot:EmissionPoseSockets)if(Snapshot.ActionId==ActionId&&Snapshot.SubhitId==SubhitId)return &Snapshot.Pose;
    return nullptr;
}

void ADungeonFighter::UseAuthoredWeaponPoseSocket()
{
    if(RunInstallBlocksFighter(*this))return;
    bWeaponMuzzleCustomOverride=false;WeaponMuzzle->SetRelativeTransform(LastAutomaticMuzzleTransform);
    SyncWeaponMuzzleTransform();
}

double ADungeonFighter::GetWeaponSkillCooldownRemaining() const
{
    const auto* Instance = WeaponSkills.Instance(WeaponSkills.State().EquippedId);
    return Instance ? FMath::Max(0.0, Instance->CooldownDeadline-WeaponSkills.State().Time) : 0.0;
}

void ADungeonFighter::SyncWeaponSkillAction()
{
    const auto& S = WeaponSkills.State(); const auto& A = S.Action;
    if (!A.Active)
    {
        if (A.ActionId&&!Combat.State().Action.Active&&Dodge.State().Phase!=DungeonDodge::EPhase::Dodging)
        {AttackTime=0.f;ComboStage=0;AttackPhase=TEXT("idle");}
        SyncWeaponMuzzleTransform(S.Time);
        return;
    }
    AttackTime = float(FMath::Max(0.0,A.End-S.Time));
    ComboStage = 0;
    // Reload carries no aim lock. Its default Action.Facing must not replace
    // the actor's real facing after a left shot or ordinary reload movement.
    if(A.Type!=DungeonWeaponActions::EAction::Reload)Facing=float(A.Facing);
    AttackPhase = A.Phase == DungeonContentCombat::EPhase::Windup ? TEXT("windup")
        : A.Phase == DungeonContentCombat::EPhase::Active ? TEXT("active") : TEXT("recovery");
    AnimationName=A.Type==DungeonWeaponActions::EAction::Reload?TEXT("reload")
        :A.Type==DungeonWeaponActions::EAction::Primary?TEXT("attack"):TEXT("secondary");
    if (A.Type==DungeonWeaponActions::EAction::Reload) AttackPhase=TEXT("reload");
    AnimationTime = float(FMath::Max(0.0,S.Time-A.Start));
    SyncWeaponMuzzleTransform(S.Time);
}

void ADungeonFighter::AdvanceWeaponSkillTo(double Now, std::vector<DungeonWeaponActions::FEvent>* DeferredEvents,
    bool* RuntimeSynchronized)
{
    bool Synchronized=false;
    SyncWeaponMuzzleTransform(Now);
    const auto PreparedPose=ResolveWeaponPoseSocketAt(Now);
    const auto Context=WeaponSkillContext();
    std::vector<DungeonWeaponActions::FEvent> Events;
    if (IsEquipmentBound()&&!WeaponSkills.State().Budget.Grounded&&JumpHeight==0.f&&JumpVelocity==0.f)
    {
        auto Landing=WeaponSkills.LandAt(Now,Context);
        ensureMsgf(Landing.Accepted,TEXT("Actual landing must preserve ordered weapon deadlines at its endpoint."));
        Events=std::move(Landing.Events);
    }
    else Events=WeaponSkills.StepTo(Now,Context);
    for(const auto& E:Events)if(E.Kind==DungeonWeaponActions::EEvent::ProjectileEmitted&&PreparedPose.Supported)
    {
        const bool Exact=E.AtTime==PreparedPose.SampleTime&&E.ActionId==PreparedPose.ActionId
            &&E.InstanceId==PreparedPose.InstanceId&&E.Origin.X==PreparedPose.CombatOrigin.X
            &&E.Origin.Y==PreparedPose.CombatOrigin.Y&&E.Origin.Height==PreparedPose.CombatOrigin.Height;
        ensureMsgf(Exact,TEXT("Emission socket must be prepared from the actual same-point pre-spend actor pose. EventAt=%.17g PreparedAt=%.17g EventAction=%llu PreparedAction=%llu EventInstance=%llu PreparedInstance=%llu EventOrigin=(%.17g,%.17g,%.17g) PreparedCombat=(%.17g,%.17g,%.17g) ActualMuzzle=(%.17g,%.17g,%.17g)"),
            E.AtTime,PreparedPose.SampleTime,static_cast<unsigned long long>(E.ActionId),static_cast<unsigned long long>(PreparedPose.ActionId),
            static_cast<unsigned long long>(E.InstanceId),static_cast<unsigned long long>(PreparedPose.InstanceId),
            E.Origin.X,E.Origin.Y,E.Origin.Height,PreparedPose.CombatOrigin.X,PreparedPose.CombatOrigin.Y,PreparedPose.CombatOrigin.Height,
            GetWeaponMuzzleOrigin().X,GetWeaponMuzzleOrigin().Y,GetWeaponMuzzleOrigin().Height);
        if(Exact)EmissionPoseSockets.push_back({E.EventId,E.ActionId,E.SubhitId,PreparedPose});
    }
    if (IsEquipmentBound())
    {
        auto Game=GetWorld()->GetAuthGameMode<ADungeonGameMode>();
        for (const auto& E:Events) if (E.Kind==DungeonWeaponActions::EEvent::Locked)
            Game->EquipmentRuntime->ObserveCritLock(true,E.ActionId,E.EventId,E.AtTime,E.Action.Critical);
        Synchronized=Game->SyncEquipmentRuntime();
        ensureMsgf(Synchronized,TEXT("Only public receipts may synchronize actual weapon runtime facts."));
        Focus=float(WeaponSkills.State().Budget.Focus);
    }
    if(RuntimeSynchronized)*RuntimeSynchronized=Synchronized;
    if(!DeferredEvents&&IsEquipmentBound())
        GetWorld()->GetAuthGameMode<ADungeonGameMode>()->ObserveActionAudio(this,Events,Synchronized);
    if (DeferredEvents) *DeferredEvents=Events;
    else if (ADungeonGameMode* Game = GetWorld()->GetAuthGameMode<ADungeonGameMode>()) Game->ConsumeWeaponSkillEvents(this,Events);
    SyncWeaponSkillAction();
    SyncWeaponMuzzleTransform(Now);
}
bool ADungeonFighter::InitializeStoneKnight(uint64 EntityId, double StartTime)
{
    if(RunInstallBlocksFighter(*this))return false;
    // This is initial spawn configuration, never a continue/reset/healing operation.
    if (StoneKnight || StoneBat || StoneGuard || !EntityId || !FMath::IsFinite(StartTime) || StartTime < 0.0 || bDead) return false;
    const auto Definition = DungeonStoneKnight::FKnightKernel::Definition();
    EnemyContentId = UTF8_TO_TCHAR(Definition.ContentId);
    bEnemy = true; bAIEnabled = true;
    MaxHealth = float(Definition.HP);
    StoneKnight = MakeUnique<FDungeonStoneKnightDriver>(this, EntityId, StartTime);
    StoneKnight->BeginCombat();
    ensureMsgf(StoneFeedback.Begin(EntityId, StoneKnight->State().NextEventId),
        TEXT("Stone feedback journal initializes once at the actual kernel event cursor."));
    LastStoneSyncTime = StartTime;
    AttackTime = AttackElapsed = AttackCooldown = InvulnerableTime = HurtTime = 0.f;
    JumpHeight = JumpVelocity = 0.f;
    ArmorChangeRemaining = 0.f; PendingArmorId.Reset();
    SetActorTickEnabled(false);
    SyncStoneKnightState();
    return true;
}

bool ADungeonFighter::InitializeStoneBat(uint64 EntityId,double StartTime)
{
    if(RunInstallBlocksFighter(*this))return false;
    const auto Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    if(StoneKnight||StoneBat||StoneGuard||IsEquipmentBound()||bDead||!EntityId||!FMath::IsFinite(StartTime)||StartTime<0.)return false;
    if(Game&&Game->GetEquipmentView().Bound&&(GetRuntimeEntityId()!=EntityId||StartTime!=Game->GetSimulationTime()))return false;
    // Initial admission preserves the current Run and central clock.
    const auto D=DungeonStoneBat::FBatKernel::Definition();
    EnemyContentId=UTF8_TO_TCHAR(D.ContentId);bEnemy=true;bAIEnabled=true;
    MaxHealth=Health=float(D.HP);JumpHeight=90.f;JumpVelocity=0.f;
    StoneBat=MakeUnique<FDungeonStoneBatDriver>(this,EntityId,StartTime);StoneBat->BeginCombat();
    AttackTime=AttackElapsed=AttackCooldown=InvulnerableTime=HurtTime=0.f;
    AnimationName=AttackPhase=TEXT("dormant");AnimationTime=0.f;SetActorTickEnabled(false);
    return true;
}

void ADungeonFighter::SyncStoneBatState()
{
    if(!StoneBat)return;const auto& S=StoneBat->State();const auto& A=S.Action;
    const FVector2D P(S.Position.X,S.Position.Y);bMoving=GetGroundPosition()!=P;SetActorLocation({P.X,P.Y,0});
    Health=float(S.HP);bDead=S.Phase==DungeonStoneBat::EPhase::Dead;BatObservedHeight=S.Position.Z;JumpHeight=float(S.Position.Z);JumpVelocity=0.f;
    AttackTime=A.InProgress?float(FMath::Max(0.,A.NominalEnd-S.Time)):0.f;HurtTime=S.Phase==DungeonStoneBat::EPhase::Stunned?float(FMath::Max(0.,S.StunUntil-S.Time)):0.f;
    PoiseAccumulation=float(S.PoiseAccum);PoiseProtection=float(FMath::Max(0.,S.ProtectionUntil-S.Time));ComboStage=0;
    if(A.Locked&&A.LockedTarget.X!=A.Origin.X)Facing=A.LockedTarget.X>A.Origin.X?1.f:-1.f;
    const TCHAR* Name=TEXT("idle");using PState=DungeonStoneBat::EPhase;
    switch(S.Phase){case PState::Dormant:Name=TEXT("dormant");break;case PState::Waking:Name=TEXT("wake");break;
    case PState::Windup:Name=TEXT("windup");break;case PState::Active:Name=A.Kind==DungeonStoneBat::EAttack::Peck?TEXT("peck"):TEXT("wing");break;
    case PState::SeekingLow:Name=TEXT("descent");break;case PState::LowRecovery:Name=TEXT("recovery");break;case PState::Rising:Name=TEXT("rise");break;
    case PState::Stunned:Name=TEXT("hurt");break;case PState::Dead:Name=TEXT("death");break;default:break;}
    SetAnimation(Name,float(FMath::Max(0.,S.Time-LastBatSyncTime)));AttackPhase=Name;
    if(S.Phase==PState::Waking)AnimationTime=float(S.Time-S.WakeStartedAt);else if(A.InProgress)AnimationTime=float(S.Time-A.Start);
    LastBatSyncTime=S.Time;
}

uint64 ADungeonFighter::GetRuntimeEntityId() const
{
    if (IsEquipmentBound()) return GetWorld()->GetAuthGameMode<ADungeonGameMode>()->GetEquipmentView().OwnerId;
    const auto Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    if (Game&&Game->GetEquipmentView().Bound) return Game->FindWorldEntityId(this);
    return StoneKnight ? StoneKnight->State().EntityId : StoneBat?StoneBat->State().EntityId:StoneGuard?StoneGuard->State().EntityId:(uint64(1) << 63) | uint64(GetUniqueID());
}

void ADungeonFighter::SyncStoneKnightState()
{
    if (!StoneKnight) return;
    using namespace DungeonStoneKnight;
    const auto& S = StoneKnight->State();
    const auto& A = S.Action;
    const FVector2D Position(S.Position.X, S.Position.Y);
    bMoving = !GetGroundPosition().Equals(Position, 1.e-6);
    Health = float(S.HP); bDead = S.Phase == EPhase::Dead;
    SetActorLocation(FVector(Position.X, Position.Y, 0.0));
    JumpHeight = JumpVelocity = 0.f;
    AttackTime = A.InProgress ? float(FMath::Max(0.0, A.RecoveryEnd-S.Time)) : 0.f;
    ComboStage = 0;
    if (A.InProgress && A.Locked && FMath::Abs(A.Direction.X) > 1.e-6)
        Facing = A.Direction.X > 0.0 ? 1.f : -1.f;
    else if (ADungeonGameMode* Game = GetWorld()->GetAuthGameMode<ADungeonGameMode>())
        if (IsValid(Game->PlayerFighter) && FMath::Abs(Game->PlayerFighter->GetGroundPosition().X-Position.X) > 1.e-6)
            Facing = Game->PlayerFighter->GetGroundPosition().X > Position.X ? 1.f : -1.f;
    const TCHAR* Name = TEXT("idle");
    switch (S.Phase)
    {
    case EPhase::Dormant: Name = TEXT("dormant"); break;
    case EPhase::Waking: Name = TEXT("wake"); break;
    case EPhase::Idle: Name = bMoving ? TEXT("walk") : TEXT("idle"); break;
    case EPhase::Windup: case EPhase::Active:
        Name = A.Kind == EAttack::Charge ? TEXT("charge") : TEXT("shield_bash"); break;
    case EPhase::Recovery: Name = TEXT("recovery"); break;
    case EPhase::Stunned: Name = TEXT("hurt"); break;
    case EPhase::Dead: Name = TEXT("death"); break;
    }
    SetAnimation(Name, float(FMath::Max(0.0, S.Time-LastStoneSyncTime)));
    if (S.Phase == EPhase::Waking) AnimationTime = float(S.Time-S.WakeStartedAt);
    else if (A.InProgress) AnimationTime = float(S.Time-A.Start);
    else if (S.Phase == EPhase::Stunned) AnimationTime = float(FMath::Max(0.0, S.Time-(S.StunUntil-.4)));
    AttackPhase = S.Phase == EPhase::Windup ? TEXT("windup") : S.Phase == EPhase::Active ? TEXT("active")
        : S.Phase == EPhase::Recovery ? TEXT("recovery") : Name;
    LastStoneSyncTime = S.Time;
}

DungeonContentCombat::EArmor ADungeonFighter::ContentArmor() const
{
    using namespace DungeonContentCombat;
    if (ArmorId == TEXT("ARM-LGT-001")) return EArmor::LGT001;
    if (ArmorId == TEXT("ARM-MED-001")) return EArmor::MED001;
    if (ArmorId == TEXT("ARM-HVY-001")) return EArmor::HVY001;
    if (ArmorId == TEXT("ARM-ROB-001")) return EArmor::ROB001;
    return EArmor::None;
}

bool ADungeonFighter::BeginArmorChange(const FString& TemplateId)
{
    if(RunInstallBlocksFighter(*this))return false;
    const bool Known = TemplateId.IsEmpty() || TemplateId == TEXT("ARM-LGT-001")
        || TemplateId == TEXT("ARM-MED-001") || TemplateId == TEXT("ARM-HVY-001") || TemplateId == TEXT("ARM-ROB-001");
    if (IsEquipmentBound() || bEnemy || !Known || TemplateId == ArmorId || !CanStartAttack() || JumpHeight > 0.f || JumpVelocity > 0.f)
        return false;
    if (!Combat.Interrupt(DungeonContentCombat::EInterruptReason::ExclusiveAction)) return false;
    PendingArmorId = TemplateId;
    ArmorChangeRemaining = .5f;
    AnimationName = TEXT("equip"); AnimationTime = 0.f;
    return true;
}

bool ADungeonFighter::SpendFocus(float Amount)
{
    if(RunInstallBlocksFighter(*this))return false;
    if (IsEquipmentBound())
    {
        auto Game=GetWorld()->GetAuthGameMode<ADungeonGameMode>();auto& V=Game->EquipmentRuntime->View;
        if (!WeaponSkills.TrySpendExternalFocus(WeaponSkills.State().Time,Amount,V.NextFocusReceiptId)) return false;
        ++V.NextFocusReceiptId;Focus=float(WeaponSkills.State().Budget.Focus);return true;
    }
    if (bDead || !FMath::IsFinite(Amount) || Amount <= 0.f || Amount > Focus) return false;
    Focus -= Amount; FocusConsumeAge = 0.f;
    return true;
}

float ADungeonFighter::RestoreFocus(float Amount)
{
    if(RunInstallBlocksFighter(*this))return 0.f;
    if (!IsEquipmentBound()) return 0.f;
    auto& V=GetWorld()->GetAuthGameMode<ADungeonGameMode>()->EquipmentRuntime->View;
    const double Applied=WeaponSkills.RestoreExternalFocus(WeaponSkills.State().Time,Amount,V.NextFocusReceiptId);
    if (Applied>0) {++V.NextFocusReceiptId;Focus=float(WeaponSkills.State().Budget.Focus);}
    return float(Applied);
}

float ADungeonFighter::GetArmorRating(bool Magic) const
{
    if(StoneGuard){const auto D=DungeonStoneGuard::FGuardKernel::Definition();return float(Magic?D.Ward:D.Armor);}
    if(StoneBat){const auto D=DungeonStoneBat::FBatKernel::Definition();return float(Magic?D.Ward:D.Armor);}
    if (IsEquipmentBound()) {const auto& S=GetWorld()->GetAuthGameMode<ADungeonGameMode>()->GetEquipmentView().Stats;return float(Magic?S.Ward:S.Armor);}
    if (StoneKnight)
    {
        const auto Definition = DungeonStoneKnight::FKnightKernel::Definition();
        return float(Magic ? Definition.Ward : Definition.Armor);
    }
    const auto* Definition = DungeonContentCombat::GetArmorDefinition(ContentArmor());
    return bEnemy ? 0.f : float(Magic ? Definition->Ward : Definition->Armor);
}
float ADungeonFighter::GetMoveSpeed() const
{
    if(StoneGuard)return float(DungeonStoneGuard::FGuardKernel::Definition().MoveSpeed);
    if(StoneBat)return float(DungeonStoneBat::FBatKernel::Definition().MoveSpeed);
    if (IsEquipmentBound()) return float(GetWorld()->GetAuthGameMode<ADungeonGameMode>()->GetEquipmentView().Stats.MoveSpeed);
    if (StoneKnight) return float(DungeonStoneKnight::FKnightKernel::Definition().MoveSpeed);
    return bEnemy ? 112.f : 265.f * float(DungeonContentCombat::GetArmorDefinition(ContentArmor())->MoveMultiplier);
}
float ADungeonFighter::GetPoiseThreshold() const
{
    if(StoneGuard)return float(DungeonStoneGuard::FGuardKernel::Definition().Poise);
    if(StoneBat)return float(DungeonStoneBat::FBatKernel::Definition().Poise);
    if (IsEquipmentBound()) return float(GetWorld()->GetAuthGameMode<ADungeonGameMode>()->GetEquipmentView().Stats.Poise);
    if (StoneKnight) return float(DungeonStoneKnight::FKnightKernel::Definition().Poise);
    return 30.f + float(DungeonContentCombat::GetArmorDefinition(ContentArmor())->PoiseBonus);
}

void ADungeonFighter::MoveOnGround(FVector2D Direction, float DeltaSeconds)
{
    if(RunInstallBlocksFighter(*this))return;
    if (StoneKnight || StoneBat || StoneGuard || bDead || HurtTime > 0.f || DeltaSeconds <= 0.f || bSuppressOrdinaryMovement || Dodge.State().Phase==DungeonDodge::EPhase::Dodging)
    {
        return;
    }
    if (Direction.SizeSquared() > 1.f) Direction.Normalize();
    if (Direction.IsNearlyZero())
    {
        return;
    }
    if (IsEquipmentBound()) GetWorld()->GetAuthGameMode<ADungeonGameMode>()->CancelEquipmentAction();
    if (ArmorChangeRemaining > 0.f)
    {
        ArmorChangeRemaining = 0.f;
        PendingArmorId.Reset();
    }
    bMoving = true;
    const auto& Skill = WeaponSkills.State().Action;
    if (IsEquipmentBound()&&Skill.Active&&Skill.Type==DungeonWeaponActions::EAction::Primary&&FMath::Abs(Direction.X)>KINDA_SMALL_NUMBER)
    {WeaponSkills.TryReverseCancel(WeaponSkills.State().Time,FMath::Sign(Direction.X));SyncWeaponSkillAction();}
    if (!Skill.Active && IsContentMelee() && AttackTime > 0.f && FMath::Abs(Direction.X) > KINDA_SMALL_NUMBER)
    {
        Combat.TryReverseCancel(Combat.State().Time, FMath::Sign(Direction.X));
        SyncContentAction();
    }
    if ((AttackTime <= 0.f || (Skill.Active && !Skill.Locked)) && FMath::Abs(Direction.X) > KINDA_SMALL_NUMBER)
    {
        Facing = Direction.X > 0.f ? 1.f : -1.f;
    }
    const float WeaponMove = Skill.Active ? float(Skill.Type==DungeonWeaponActions::EAction::Skill
        ?DungeonContentCombat::GetWeaponDefinition(Skill.Weapon)->Skill.Timeline.MoveMultiplier
        :DungeonContentCombat::GetWeaponDefinition(Skill.Weapon)->Primary[0].MoveMultiplier)
        : IsContentMelee() ? float(Combat.State().Action.MoveMultiplier) : 0.2f;
    const float ActionMultiplier = FMath::Min(AttackTime > 0.f ? WeaponMove : 1.f, HurtTime > 0.f ? 0.3f : 1.f)
        * (JumpHeight > 0.f ? 0.8f : 1.f);
    const float Speed = GetMoveSpeed();
    const auto From=GetGroundPosition();
    FVector2D Position = From + Direction * Speed * ActionMultiplier * DeltaSeconds;
    Position.X = FMath::Clamp(Position.X, DungeonRoomLayout::MinX, DungeonRoomLayout::MaxX);
    Position.Y = FMath::Clamp(Position.Y, DungeonRoomLayout::MinY, DungeonRoomLayout::MaxY);
    if (auto Game=GetWorld()->GetAuthGameMode<ADungeonGameMode>())
    {
        const auto Query=Game->QueryResolvedMovement(this,From,Position,Game->SimulationTime,Game->SimulationTime+double(DeltaSeconds),
            Game->bSimulatingMotion?Game->MotionBatchBodies:Game->CaptureKnightBodies());
        const double Fraction=FMath::Min(Query.HitWall?Query.WallFraction:1.0,Query.HitBody?Query.BodyFraction:1.0);
        Position=FMath::Lerp(From,Position,Fraction);
    }
    SetActorLocation(FVector(Position.X, Position.Y, 0.f));
    SyncWeaponMuzzleTransform();
    CommitIdleDodgePosition();
}

void ADungeonFighter::StartJump()
{
    if(RunInstallBlocksFighter(*this))return;
    if (!StoneKnight && !StoneBat && !StoneGuard && GetEquipmentActionDeadline()<=0 && Dodge.State().Phase!=DungeonDodge::EPhase::Dodging && !WeaponSkills.State().Action.Active && !bDead && JumpHeight <= 0.f && JumpVelocity <= 0.f && HurtTime <= 0.f && AttackTime <= 0.f && ArmorChangeRemaining <= 0.f)
    {
        JumpVelocity = 630.f;
        bAirPrimarySpent = false;
        Combat.NotifyTakeoff();
        WeaponSkills.NotifyTakeoff();
    }
}

bool ADungeonFighter::CanStartAttack() const
{
    if(RunInstallBlocksFighter(*this))return false;
    return !StoneKnight && !StoneBat && !StoneGuard && GetEquipmentActionDeadline()<=0 && Dodge.State().Phase!=DungeonDodge::EPhase::Dodging && !WeaponSkills.State().Action.Active && !bDead && AttackTime <= 0.f && AttackCooldown <= 0.f && HurtTime <= 0.f && ArmorChangeRemaining <= 0.f
        && !(JumpHeight > 0.f && bAirPrimarySpent);
}

float ADungeonFighter::GetAttackRange() const
{
    if(StoneGuard)return StoneGuard->State().Action.InProgress?float(StoneGuard->State().Action.Kind==DungeonStoneGuard::EAttack::AxeSweep?180.:160.):0.f;
    return IsContentMelee() ? float((bResolvingContentWindow ? HitAction : Combat.State().Action).Range)
        : bEnemy ? 112.f : (WeaponId == TEXT("axe") ? 150.f : 135.f);
}

float ADungeonFighter::GetAttackDamage() const
{
    if(StoneGuard)return StoneGuard->State().Action.InProgress?float(StoneGuard->State().Action.Damage):0.f;
    return IsContentMelee() ? float((bResolvingContentWindow ? HitAction : Combat.State().Action).Damage)
        : bEnemy ? 13.f : (WeaponId == TEXT("axe") ? 42.f : 26.f);
}

float ADungeonFighter::GetAttackStagger() const
{
    if(StoneGuard)return StoneGuard->State().Action.InProgress?float(StoneGuard->State().Action.Stagger):0.f;
    return IsContentMelee() ? float((bResolvingContentWindow ? HitAction : Combat.State().Action).Stagger) : 13.f;
}

float ADungeonFighter::GetAttackDepth() const
{
    if(StoneGuard)return StoneGuard->State().Action.InProgress?float(StoneGuard->State().Action.Kind==DungeonStoneGuard::EAttack::AxeSweep?65.:90.):0.f;
    return IsContentMelee() ? float((bResolvingContentWindow ? HitAction : Combat.State().Action).Depth)
        : bEnemy ? 44.f : (WeaponId == TEXT("axe") ? 66.f : 52.f);
}

bool ADungeonFighter::CanHitTarget(FVector2D Delta, float InFacing, float Range,
    float DepthTolerance, float AttackerHeight, float TargetHeight)
{
    return DungeonCombatRules::CanHit(Delta.X, Delta.Y, InFacing, Range,
        DepthTolerance, AttackerHeight, TargetHeight);
}

void ADungeonFighter::BeginAttack()
{
    if(RunInstallBlocksFighter(*this))return;
    if (IsEquipmentBound())
    {
        auto Game=GetWorld()->GetAuthGameMode<ADungeonGameMode>();Game->UpdateEquipmentMirrors();
        if (Game->GetEquipmentView().Action.Active) return;
        if (!IsContentMelee())
        {
            if (Game->bGameOver||Game->bWaitingForStart||bDead||HurtTime>0.f||Dodge.State().Phase==DungeonDodge::EPhase::Dodging
                ||Combat.State().Action.Active||WeaponSkills.State().Time!=Game->GetSimulationTime()) return;
            if (!WeaponSkills.TryStart(DungeonWeaponActions::EAction::Primary,WeaponSkills.State().Time,WeaponSkillContext(),true)) return;
            Combat.Interrupt(DungeonContentCombat::EInterruptReason::ExclusiveAction);
            if (JumpHeight>0.f||JumpVelocity>0.f) bAirPrimarySpent=true;
            SyncWeaponSkillAction();return;
        }
        auto NextCombat=Combat;auto NextActions=WeaponSkills;
        const uint64 Id=Game->GetEquipmentView().Slots[Game->GetEquipmentView().ActiveSlot].InstanceId;
        if ((NextCombat.State().Weapon!=ContentWeapon() || NextCombat.State().WeaponInstanceId!=Id)
            && !NextCombat.ChangeWeapon(ContentWeapon(),Id)) return;
        const uint64 Before=NextCombat.State().Action.AttackId;
        if (!NextActions.CanAdmitExternalMeleePrimary() || !NextCombat.PressPrimary(NextCombat.State().Time,CombatContext())) return;
        if (NextCombat.State().Action.AttackId!=Before && !NextActions.RecordAcceptedExternalMeleePrimary()) return;
        Combat=MoveTemp(NextCombat);WeaponSkills=MoveTemp(NextActions);
        if (JumpHeight>0 || JumpVelocity>0) bAirPrimarySpent=true;
        SyncContentAction();return;
    }
    if (StoneKnight || StoneBat || StoneGuard || Dodge.State().Phase==DungeonDodge::EPhase::Dodging || WeaponSkills.State().Action.Active || ArmorChangeRemaining > 0.f) return;
    if (IsContentMelee())
    {
        if (Combat.State().Weapon != ContentWeapon())
            Combat.ChangeWeapon(ContentWeapon(), uint64(ContentWeapon()) + 1);
        if (Combat.PressPrimary(Combat.State().Time, CombatContext()))
        {
            if (JumpHeight > 0.f || JumpVelocity > 0.f) bAirPrimarySpent = true;
            SyncContentAction();
        }
        return;
    }
    if (!CanStartAttack())
    {
        return;
    }
    AttackTime = bEnemy ? 0.72f : (WeaponId == TEXT("axe") ? 0.64f : 0.43f);
    AttackElapsed = 0.f;
    AttackCooldown = bEnemy ? 1.2f : (WeaponId == TEXT("axe") ? 0.72f : 0.48f);
    bAttackResolved = false;
    AnimationName = TEXT("attack");
    AnimationTime = 0.f;
}

void ADungeonFighter::ApplyCombatHit(float Damage, ADungeonFighter* Attacker, float Stagger, bool Magic)
{
    if(RunInstallBlocksFighter(*this))return;
    ApplyCombatHitInternal(Damage, Attacker, Stagger, false, Magic);
}

void ADungeonFighter::InterruptWeaponActionForHit(DungeonWeaponActions::EInterrupt Reason)
{
    auto Game=GetWorld()->GetAuthGameMode<ADungeonGameMode>();
    if (IsEquipmentBound()&&Game&&Game->bSimulationBatch)
        ensureMsgf(WeaponSkills.InterruptAt(Game->SimulationTime,Reason,WeaponSkillContext()),
            TEXT("Endpoint interruption must not skip an earlier weapon deadline or mutate emission history."));
    else WeaponSkills.Interrupt(Reason);
    if(IsEquipmentBound()&&Game)Game->ObservePendingActionAudio(this);
}

bool ADungeonFighter::CanReceiveDirectHit() const { return !bDead && InvulnerableTime <= 0.f && !IsDodgeInvulnerableAt(Dodge.State().Time); }

void ADungeonFighter::ApplyCombatHitInternal(float Damage, ADungeonFighter* Attacker, float Stagger, bool PreviouslyAccepted,
    bool Magic, bool DamageOverTime, bool PreserveHurtProtection)
{
    if (bDead || (!DamageOverTime&&!PreviouslyAccepted && !CanReceiveDirectHit()) || !FMath::IsFinite(Damage) || Damage <= 0.f)
    {
        return;
    }
    const float Rating = FMath::Max(0.f, GetArmorRating(Magic));
    float ActualDamage = Damage * (1.f - FMath::Min(.6f, Rating / (100.f + Rating)));
    if (IsEquipmentBound())
    {
        auto Game=GetWorld()->GetAuthGameMode<ADungeonGameMode>();const auto& S=Game->GetEquipmentView().Stats;
        ActualDamage*=float(Magic?S.MagicVulnerabilityMultiplier:S.PhysicalVulnerabilityMultiplier);
        if (ActualDamage>0) Game->CancelEquipmentAction();
    }
    if(StoneGuard)
    {
        auto Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;if(!Game)return;
        const float Incoming=DamageOverTime?0.f:Stagger>=0.f?Stagger:Attacker?Attacker->GetAttackStagger():13.f;
        if(!FMath::IsFinite(Incoming)||Incoming<0.f)return;
        const auto Frame=Game->MakeKnightFrame(this,StoneGuard->State().Time,Game->SimulationTime,
            Game->bSimulationBatch?Game->SkillBatchBodies:Game->CaptureKnightBodies());
        const auto Batch=StoneGuard->ApplyResolvedHit(FMath::Min(double(ActualDamage),StoneGuard->State().HP),Incoming,Frame);
        if(!Batch.Accepted)return;
        HitFlash=.22f;Game->AcceptGuardBatch(this,Batch);SyncStoneGuardState();if(bDead)Game->OnFighterDied(this);
        return; // No second mitigation, generic iframe/push, or second HP owner.
    }
    if (StoneKnight)
    {
        ADungeonGameMode* Game = GetWorld()->GetAuthGameMode<ADungeonGameMode>();
        if (!Game) return; // No fabricated world observations outside the authoritative simulation.
        const float IncomingStagger = Stagger >= 0.f ? Stagger : Attacker ? Attacker->GetAttackStagger() : 13.f;
        if (!FMath::IsFinite(IncomingStagger) || IncomingStagger < 0.f) return;
        const auto Batch = StoneKnight->ApplyResolvedHit(FMath::Min(double(ActualDamage), StoneKnight->State().HP),
            double(IncomingStagger), Game->MakeKnightDamageFrame(this));
        if (!Batch.Accepted) return;
        HitFlash = .22f;
        Game->AcceptKnightBatch(this, Batch);
        SyncStoneKnightState();
        if (bDead) Game->OnFighterDied(this);
        return; // Kernel owns poise, wake, action interruption and death; no prototype iframe or push.
    }
    if(StoneBat)
    {
        auto Game=GetWorld()->GetAuthGameMode<ADungeonGameMode>();if(!Game)return;
        const float Incoming=DamageOverTime?0.f:Stagger>=0.f?Stagger:Attacker?Attacker->GetAttackStagger():13.f;
        if(!FMath::IsFinite(Incoming)||Incoming<0.f)return;
        const auto Frame=Game->MakeKnightFrame(this,StoneBat->State().Time,Game->SimulationTime,Game->bSimulationBatch?Game->SkillBatchBodies:Game->CaptureKnightBodies());
        const auto Batch=StoneBat->ApplyResolvedHit(FMath::Min(double(ActualDamage),StoneBat->State().HP),Incoming,Frame);if(!Batch.Accepted)return;
        HitFlash=.22f;Game->AcceptBatBatch(this,Batch);SyncStoneBatState();if(bDead)Game->OnFighterDied(this);return;
    }
    Health = FMath::Max(0.f, Health - ActualDamage);
    ArmorChangeRemaining = 0.f; PendingArmorId.Reset();
    if (DamageOverTime)
    {
        // Status ticks bypass direct protection and never create hurt/poise/push.
        if (Health<=0.f)
        {
            bDead=true;AttackTime=0.f;Combat.Interrupt(DungeonContentCombat::EInterruptReason::Death);
            InterruptWeaponActionForHit(DungeonWeaponActions::EInterrupt::Death);
            if (!bEnemy) Dodge.Interrupt(Dodge.State().Time,DungeonDodge::EFinish::Death);
            AnimationName=TEXT("death");AnimationTime=0;
            if (auto Game=GetWorld()->GetAuthGameMode<ADungeonGameMode>()) Game->OnFighterDied(this);
        }
        return;
    }
    if (USoundBase* Impact = LoadObject<USoundBase>(nullptr,TEXT("/Game/ThirdParty/Kenney/ImpactSounds/ImpactLight/SW_ImpactLight.SW_ImpactLight")))
        UGameplayStatics::PlaySound2D(this,Impact,0.45f,bEnemy?1.15f:0.9f);
    HitFlash = 0.22f;
    if (!PreserveHurtProtection)
    {InvulnerableTime = bEnemy ? 0.18f : 0.65f;HurtProtectionSource={};}
    bool Broken = bEnemy; // Historical generic enemies remain prototype adapters.
    if (!bEnemy && PoiseProtection <= 0.f)
    {
        PoiseAccumulation += Stagger >= 0.f ? Stagger : Attacker ? Attacker->GetAttackStagger() : 13.f;
        PoiseDecayDelay = 1.f;
        if (PoiseAccumulation >= GetPoiseThreshold())
        {
            Broken = true; PoiseAccumulation = 0.f; PoiseProtection = 1.f;
        }
    }
    if (Broken || Health <= 0.f)
    {
        HurtTime = bEnemy ? .2f : .4f;
        AttackTime = 0.f;
        Combat.Interrupt(Health <= 0.f ? DungeonContentCombat::EInterruptReason::Death
            : DungeonContentCombat::EInterruptReason::PoiseBreak);
        InterruptWeaponActionForHit(Health <= 0.f ? DungeonWeaponActions::EInterrupt::Death
            : DungeonWeaponActions::EInterrupt::PoiseBreak);
        if (!bEnemy) Dodge.Interrupt(Dodge.State().Time,Health<=0.f?DungeonDodge::EFinish::Death:DungeonDodge::EFinish::PoiseBreak);
        SkillWindows.clear();
        if (auto Game=GetWorld()->GetAuthGameMode<ADungeonGameMode>()) Game->CancelWorldWeaponWindows(GetRuntimeEntityId());
        AnimationTime = 0.f;
        AnimationName = Health > 0.f ? TEXT("hurt") : TEXT("death");
    }
    if (Attacker && bEnemy && !(PreviouslyAccepted&&Attacker->IsEquipmentBound()))
    {
        FVector Position = GetActorLocation();
        Position.X = FMath::Clamp(Position.X + Attacker->Facing * 24.f, DungeonRoomLayout::MinX, DungeonRoomLayout::MaxX);
        SetActorLocation(Position);
    }
    if (Health <= 0.f)
    {
        bDead = true;
        if (ADungeonGameMode* GameMode = GetWorld()->GetAuthGameMode<ADungeonGameMode>())
        {
            GameMode->OnFighterDied(this);
        }
    }
}

void ADungeonFighter::ResetFighter(FVector2D GroundPosition)
{
    if(RunInstallBlocksFighter(*this))return;
    if (StoneKnight || StoneBat || StoneGuard || IsEquipmentBound()) return; // Transfers/continue must never reset a bound Run.
    Health = MaxHealth;
    JumpHeight = 0.f;
    JumpVelocity = 0.f;
    LandingVisualAge = .12f;
    Facing = bEnemy ? -1.f : 1.f;
    AttackTime = 0.f;
    AttackElapsed = 0.f;
    AttackCooldown = 0.f;
    InvulnerableTime = 0.f;
    HurtTime = 0.f;
    HitFlash = 0.f;
    bDead = false;
    bDeathReported = false;
    bAttackResolved = false;
    bMoving = false;
    Combat = DungeonContentCombat::FCombatKernel(ContentWeapon(), uint64(ContentWeapon()) + 1);
    WeaponSkills = DungeonWeaponActions::FWeaponActionsKernel();
    Dodge = DungeonDodge::FDodgeKernel(GetRuntimeEntityId(),0.0,{GroundPosition.X,GroundPosition.Y});
    SkillWindows.clear(); SkillHitReceipts.clear(); EmissionPoseSockets.clear(); LastSkillEventId = 0;
    BatchSkillStepAt = -1.0; BatchSkillStepDelta = FVector2D::ZeroVector;
    ComboStage = 0;
    AttackPhase = TEXT("idle");
    bAirPrimarySpent = false;
    bResolvingContentWindow = false;
    PoiseAccumulation = PoiseDecayDelay = PoiseProtection = 0.f;
    ArmorChangeRemaining = 0.f; PendingArmorId.Reset();
    Focus = 100.f; FocusConsumeAge = 1.f;
    HurtProtectionSource={};
    AnimationName = TEXT("idle");
    AnimationTime = 0.f;
    SetActorLocation(FVector(GroundPosition.X, GroundPosition.Y, 0.f));
    SyncWeaponMuzzleTransform();
}

void ADungeonFighter::SwitchWeapon()
{
    if(RunInstallBlocksFighter(*this))return;
    if (IsEquipmentBound()) {GetWorld()->GetAuthGameMode<ADungeonGameMode>()->TrySwitchEquipment();return;}
    if (Dodge.State().Phase!=DungeonDodge::EPhase::Dodging && !WeaponSkills.State().Action.Active && !bDead && bHasAxe && AttackTime <= 0.f && JumpHeight <= 0.f && HurtTime <= 0.f && ArmorChangeRemaining <= 0.f)
    {
        if (!Combat.Interrupt(DungeonContentCombat::EInterruptReason::SwitchWeapon)) return;
        WeaponId = WeaponId == TEXT("sword") ? TEXT("axe") : TEXT("sword");
        if (ADungeonGameMode* GameMode = GetWorld()->GetAuthGameMode<ADungeonGameMode>())
        {
            GameMode->LastMessage = WeaponId == TEXT("axe") ? TEXT("已切换重斧：范围更大，攻击更慢") : TEXT("已切换长剑：攻击更快");
        }
    }
}

FVector2D ADungeonFighter::ReadMoveIntent() const
{
    auto C=Cast<APlayerController>(GetController());
    if (!C || !C->IsLocalController()) return FVector2D::ZeroVector;
    const auto MoveHeld=[C,this](FKey Letter,FKey Arrow){return C->IsInputKeyDown(Letter)||(!bEquipmentUiArrowLatch&&C->IsInputKeyDown(Arrow));};
    return {(MoveHeld(EKeys::D,EKeys::Right)?1.0:0.0)-(MoveHeld(EKeys::A,EKeys::Left)?1.0:0.0),
        (MoveHeld(EKeys::W,EKeys::Up)?1.0:0.0)-(MoveHeld(EKeys::S,EKeys::Down)?1.0:0.0)};
}

FVector2D ADungeonFighter::PredictGroundPosition(double DeltaSeconds) const
{
    const auto Origin=GetGroundPosition();
    if (StoneKnight || StoneBat || StoneGuard || bDead || HurtTime>0.f || DeltaSeconds<=0.0 || Dodge.State().Phase==DungeonDodge::EPhase::Dodging) return Origin;
    FVector2D Direction=ReadMoveIntent();
    if (bEnemy)
    {
        auto Game=GetWorld()->GetAuthGameMode<ADungeonGameMode>();
        if (!bAIEnabled || !Game || !Game->PlayerFighter || Game->PlayerFighter->bDead || AttackTime>0.f) return Origin;
        const auto D=Game->PlayerFighter->GetGroundPosition()-Origin;
        if (FMath::Abs(D.X)<=102.f && FMath::Abs(D.Y)<=33.f) return Origin;
        Direction={FMath::Abs(D.X)>88.f?FMath::Sign(D.X):0.0,FMath::Abs(D.Y)>20.f?FMath::Sign(D.Y):0.0};
    }
    if (Direction.SizeSquared()>1.0) Direction.Normalize();
    const auto& Skill=WeaponSkills.State().Action;
    const double ActionMove=Skill.Active?(Skill.Type==DungeonWeaponActions::EAction::Skill
        ?DungeonContentCombat::GetWeaponDefinition(Skill.Weapon)->Skill.Timeline.MoveMultiplier
        :DungeonContentCombat::GetWeaponDefinition(Skill.Weapon)->Primary[0].MoveMultiplier)
        :IsContentMelee()?Combat.State().Action.MoveMultiplier:.2;
    const double Multiplier=(AttackTime>0.f?ActionMove:1.0)*(JumpHeight>0.f?.8:1.0);
    auto P=Origin+Direction*double(GetMoveSpeed())*Multiplier*DeltaSeconds;
    P.X=FMath::Clamp(P.X,DungeonRoomLayout::MinX,DungeonRoomLayout::MaxX);
    P.Y=FMath::Clamp(P.Y,DungeonRoomLayout::MinY,DungeonRoomLayout::MaxY);
    return P;
}

void ADungeonFighter::UpdatePlayerInput(float DeltaSeconds, bool ConsumeInputEdges)
{
    if(RunInstallBlocksFighter(*this))return;
    APlayerController* PlayerController = Cast<APlayerController>(GetController());
    ADungeonGameMode* GameMode = GetWorld()->GetAuthGameMode<ADungeonGameMode>();
    if (!PlayerController || !PlayerController->IsLocalController() || !GameMode || GameMode->bGameOver || GameMode->bWaitingForStart)
    {
        return;
    }
    if (!PlayerController->IsInputKeyDown(EKeys::Left)&&!PlayerController->IsInputKeyDown(EKeys::Right)
        &&!PlayerController->IsInputKeyDown(EKeys::Up)&&!PlayerController->IsInputKeyDown(EKeys::Down)) bEquipmentUiArrowLatch=false;
    if(IsEquipmentBound()&&GameMode->GetSceneInteractionView().Pending&&GameMode->GetSceneInteractionView().NeedsConfirmation)
    {
        if(ConsumeInputEdges&&PlayerController->WasInputKeyJustPressed(EKeys::Escape)){GameMode->CancelSceneInteraction();return;}
        if(!ReadMoveIntent().IsNearlyZero())GameMode->CancelSceneInteraction();
    }
    const auto AcceptSceneWorldRequest=[GameMode]()
    {if(GameMode->GetSceneInteractionView().Pending)GameMode->CancelSceneInteraction();};
    if (IsEquipmentBound() && GameMode->GetEquipmentView().NeedsSlotSelection)
    {
        auto& V=GameMode->EquipmentRuntime->View;
        const bool UiDodge=ConsumeInputEdges && (PlayerController->WasInputKeyJustPressed(EKeys::LeftShift)||PlayerController->WasInputKeyJustPressed(EKeys::RightShift));
        if (UiDodge) {TryBeginDodge(ReadMoveIntent(),true);return;}
        if (ConsumeInputEdges && PlayerController->WasInputKeyJustPressed(EKeys::Escape)) {GameMode->CancelEquipmentSelection();return;}
        const bool Arrows=PlayerController->IsInputKeyDown(EKeys::Left)||PlayerController->IsInputKeyDown(EKeys::Right)
            ||PlayerController->IsInputKeyDown(EKeys::Up)||PlayerController->IsInputKeyDown(EKeys::Down);
        bEquipmentUiArrowLatch=bEquipmentUiArrowLatch||Arrows;
        if (ConsumeInputEdges && V.SelectionSlot!=2)
        {
            if (PlayerController->WasInputKeyJustPressed(EKeys::Left)||PlayerController->WasInputKeyJustPressed(EKeys::Up)) V.SelectionSlot=0;
            if (PlayerController->WasInputKeyJustPressed(EKeys::Right)||PlayerController->WasInputKeyJustPressed(EKeys::Down)) V.SelectionSlot=1;
        }
        if (ConsumeInputEdges && !GameMode->SuppressRestoreContinueEnter && PlayerController->WasInputKeyJustPressed(EKeys::Enter)) {GameMode->ConfirmEquipmentSlot(V.SelectionSlot,true);return;}
        if (ReadMoveIntent().IsNearlyZero()) return;
        GameMode->CancelEquipmentSelection();
    }
    const auto Intent=ReadMoveIntent();
    const bool DodgePress=ConsumeInputEdges && (PlayerController->WasInputKeyJustPressed(EKeys::LeftShift)
        ||PlayerController->WasInputKeyJustPressed(EKeys::RightShift));
    if (DodgePress && TryBeginDodge(Intent,true)) {AcceptSceneWorldRequest();return;}
    if (IsEquipmentBound()&&WeaponSkills.State().Action.Active&&WeaponSkills.State().Action.Type==DungeonWeaponActions::EAction::Reload)
    {
        MoveOnGround(Intent,DeltaSeconds);
        if (ConsumeInputEdges)
        {
            if (PlayerController->WasInputKeyJustPressed(EKeys::Q)) {GameMode->TrySwitchEquipment();return;}
            if (PlayerController->WasInputKeyJustPressed(EKeys::T)) {TryBeginReload();return;}
        }
        return;
    }
    if (DeltaSeconds==0.f && !Intent.IsNearlyZero() && !bDead && HurtTime<=0.f
        && Dodge.State().Phase!=DungeonDodge::EPhase::Dodging)
    {
        if (IsEquipmentBound()) GameMode->CancelEquipmentAction();
        if (ArmorChangeRemaining>0.f) {ArmorChangeRemaining=0.f;PendingArmorId.Reset();}
        if (!WeaponSkills.State().Action.Active && IsContentMelee() && FMath::Abs(Intent.X)>KINDA_SMALL_NUMBER)
        {Combat.TryReverseCancel(Combat.State().Time,FMath::Sign(Intent.X));SyncContentAction();}
        if (IsEquipmentBound()&&WeaponSkills.State().Action.Active&&WeaponSkills.State().Action.Type==DungeonWeaponActions::EAction::Primary
            &&FMath::Abs(Intent.X)>KINDA_SMALL_NUMBER)
        {WeaponSkills.TryReverseCancel(WeaponSkills.State().Time,FMath::Sign(Intent.X));SyncWeaponSkillAction();}
    }
    if (DeltaSeconds==0.f && HurtTime<=0.f && Dodge.State().Phase!=DungeonDodge::EPhase::Dodging
        && (AttackTime<=0.f || (WeaponSkills.State().Action.Active&&!WeaponSkills.State().Action.Locked))
        && FMath::Abs(Intent.X)>KINDA_SMALL_NUMBER)
        Facing=Intent.X>0.f?1.f:-1.f;
    MoveOnGround(Intent, DeltaSeconds);
    if (!ConsumeInputEdges) return;
    if (PlayerController->WasInputKeyJustPressed(EKeys::SpaceBar))
    {
        StartJump();
        if (JumpVelocity > 0.f) {AcceptSceneWorldRequest();return;}
    }
    const bool SkillPress = PlayerController->WasInputKeyJustPressed(EKeys::K)
        || PlayerController->WasInputKeyJustPressed(EKeys::RightMouseButton);
    if (SkillPress && TryBeginWeaponSkill(true)) {AcceptSceneWorldRequest();return;}
    if (PlayerController->WasInputKeyJustPressed(EKeys::J) || PlayerController->WasInputKeyJustPressed(EKeys::LeftMouseButton))
    {
        const auto BeforeCombat=Combat.State().NextAttackId;
        const auto BeforeWeaponAction=WeaponSkills.State().NextActionId;
        GameMode->TryAttack(this);
        if (IsEquipmentBound() && (Combat.State().NextAttackId!=BeforeCombat || Combat.State().PendingPrimary
            ||WeaponSkills.State().NextActionId!=BeforeWeaponAction)) {AcceptSceneWorldRequest();return;}
    }
    if (IsEquipmentBound())
    {
        if (PlayerController->WasInputKeyJustPressed(EKeys::Q))
        {
            if(GameMode->TrySwitchEquipment()){AcceptSceneWorldRequest();return;}
            if(!GameMode->GetSceneInteractionView().Pending)return;
        }
        if (PlayerController->WasInputKeyJustPressed(EKeys::T))
        {
            if(TryBeginReload()){AcceptSceneWorldRequest();return;}
            if(!GameMode->GetSceneInteractionView().Pending)return;
        }
        if(GameMode->GetSceneInteractionView().Pending&&GameMode->GetSceneInteractionView().NeedsConfirmation)
        {
            // Live-layer confirmation follows every legal world request. An
            // invalid request leaves this layer intact for its own fresh key.
            if(PlayerController->WasInputKeyJustPressed(EKeys::Tab))return;
            if(!GameMode->SuppressRestoreContinueEnter&&PlayerController->WasInputKeyJustPressed(EKeys::Enter)){GameMode->ConfirmSceneInteraction(true);return;}
            if(PlayerController->WasInputKeyJustPressed(EKeys::E))return;
        }
        if (PlayerController->WasInputKeyJustPressed(EKeys::Tab)) {GameMode->CycleEquipmentTarget();return;}
        if (PlayerController->WasInputKeyJustPressed(EKeys::E)) {GameMode->TryInteract();return;}
        return;
    }
    if (PlayerController->WasInputKeyJustPressed(EKeys::E))
    {
        GameMode->TryInteract();
    }
    if (PlayerController->WasInputKeyJustPressed(EKeys::Q))
    {
        SwitchWeapon();
    }
}

void ADungeonFighter::UpdateEnemy(float DeltaSeconds)
{
    ADungeonGameMode* GameMode = GetWorld()->GetAuthGameMode<ADungeonGameMode>();
    ADungeonFighter* Player = GameMode ? GameMode->GetPlayerFighter() : nullptr;
    if (!bAIEnabled || !Player || Player->bDead || GameMode->bGameOver || GameMode->bWaitingForStart || AttackTime > 0.f || HurtTime > 0.f)
    {
        return;
    }
    const FVector2D Delta = Player->GetGroundPosition() - GetGroundPosition();
    if (FMath::Abs(Delta.X) > 3.f)
    {
        Facing = Delta.X > 0.f ? 1.f : -1.f;
    }
    if (FMath::Abs(Delta.X) <= 102.f && FMath::Abs(Delta.Y) <= 33.f)
    {
        GameMode->TryAttack(this);
        return;
    }
    FVector2D Direction(FMath::Abs(Delta.X) > 88.f ? FMath::Sign(Delta.X) : 0.f,
        FMath::Abs(Delta.Y) > 20.f ? FMath::Sign(Delta.Y) : 0.f);
    MoveOnGround(Direction, DeltaSeconds);
}

void ADungeonFighter::SetAnimation(const FString& Name, float DeltaSeconds)
{
    if (AnimationName == Name)
    {
        AnimationTime += DeltaSeconds;
    }
    else
    {
        AnimationName = Name;
        AnimationTime = 0.f;
    }
}

void ADungeonFighter::Tick(float DeltaSeconds)
{
    if(RunInstallBlocksFighter(*this))return;
    Super::Tick(DeltaSeconds);
    SimulateMotion(DeltaSeconds, true);
    SimulateActions(DeltaSeconds);
}

void ADungeonFighter::AdvanceTerminalPresentation(float DeltaSeconds)
{
    if(RunInstallBlocksFighter(*this))return;
    if (!bDead || !FMath::IsFinite(DeltaSeconds) || DeltaSeconds <= 0.f) return;
    // Terminal display only: no kernel/driver clock, movement, input, damage or resource tick.
    AnimationTime += DeltaSeconds;
    JumpHeight = FMath::Max(0.f, JumpHeight-360.f*DeltaSeconds);
}

void ADungeonFighter::SimulateMotion(float DeltaSeconds, bool ConsumeInputEdges)
{
    if(RunInstallBlocksFighter(*this))return;
    if (StoneKnight || StoneBat || StoneGuard)
    {
        HitFlash = FMath::Max(0.f, HitFlash-DeltaSeconds);
        return; // Driver advances only once in GameMode's absolute-time action batch.
    }
    HitFlash = FMath::Max(0.f, HitFlash - DeltaSeconds);
    InvulnerableTime = FMath::Max(0.f, InvulnerableTime - DeltaSeconds);
    HurtTime = FMath::Max(0.f, HurtTime - DeltaSeconds);
    AttackCooldown = FMath::Max(0.f, AttackCooldown - DeltaSeconds);
    PoiseProtection = FMath::Max(0.f, PoiseProtection - DeltaSeconds);
    const float DecayTime = FMath::Max(0.f, DeltaSeconds - PoiseDecayDelay);
    PoiseDecayDelay = FMath::Max(0.f, PoiseDecayDelay - DeltaSeconds);
    PoiseAccumulation = FMath::Max(0.f, PoiseAccumulation - 20.f * DecayTime);
    if (bDead)
    {
        JumpHeight = FMath::Max(0.f, JumpHeight - 360.f * DeltaSeconds);
        SetAnimation(TEXT("death"), DeltaSeconds);
        return;
    }
    LandingVisualAge = FMath::Min(.12f, LandingVisualAge+DeltaSeconds);
    if (!IsEquipmentBound())
    {
        const auto* Armor = DungeonContentCombat::GetArmorDefinition(ContentArmor());
        const float RegenTime = FMath::Max(0.f, DeltaSeconds - FMath::Max(0.f, float(Armor->FocusDelay) - FocusConsumeAge));
        Focus = FMath::Min(100.f, Focus + float(Armor->FocusRegen) * RegenTime);
        FocusConsumeAge = FMath::Min(float(Armor->FocusDelay), FocusConsumeAge + DeltaSeconds);
    }
    if (ArmorChangeRemaining > 0.f)
    {
        ArmorChangeRemaining = FMath::Max(0.f, ArmorChangeRemaining - DeltaSeconds);
        if (ArmorChangeRemaining <= 0.f) { ArmorId = PendingArmorId; PendingArmorId.Reset(); }
    }
    bMoving = false;
    if (bEnemy)
    {
        UpdateEnemy(DeltaSeconds);
    }
    else
    {
        UpdatePlayerInput(DeltaSeconds, ConsumeInputEdges);
    }
    if (JumpHeight > 0.f || JumpVelocity > 0.f)
    {
        JumpHeight = FMath::Max(0.f, JumpHeight + JumpVelocity * DeltaSeconds - 900.f * DeltaSeconds * DeltaSeconds);
        JumpVelocity -= 1800.f * DeltaSeconds;
        if (JumpHeight <= 0.f)
        {
            JumpVelocity = 0.f;
            LandingVisualAge = 0.f;
            bAirPrimarySpent = false;
            Combat.NotifyLand();
            if (!IsEquipmentBound()) WeaponSkills.NotifyLand();
        }
    }
    SyncWeaponMuzzleTransform();
}

void ADungeonFighter::SimulateActions(float DeltaSeconds)
{
    if(RunInstallBlocksFighter(*this))return;
    SimulateActionsTo(FMath::Max(Combat.State().Time,WeaponSkills.State().Time)+double(DeltaSeconds),DeltaSeconds);
}

void ADungeonFighter::SimulateActionsTo(double Now, float DeltaSeconds, std::vector<DungeonWeaponActions::FEvent>* DeferredEvents)
{
    if(RunInstallBlocksFighter(*this))return;
    if (StoneKnight || StoneBat || StoneGuard) return;
    if (bDead) return;
    if (IsContentMelee() || IsEquipmentBound()) AdvanceContentActionTo(Now);
    // Bound GameMode first commits old world contacts and endpoint damage.
    // Only then may WA emit and consume its reserved trigger at this same time.
    if (!bEnemy&&!(IsEquipmentBound()&&DeferredEvents)) AdvanceWeaponSkillTo(Now,DeferredEvents);
    if (AttackTime > 0.f && !IsContentMelee() && !IsEquipmentBound())
    {
        AttackElapsed += DeltaSeconds;
        const float Windup = bEnemy ? 0.46f : (WeaponId == TEXT("axe") ? 0.31f : 0.17f);
        if (!bAttackResolved && AttackElapsed >= Windup)
        {
            bAttackResolved = true;
            if (ADungeonGameMode* GameMode = GetWorld()->GetAuthGameMode<ADungeonGameMode>())
            {
                GameMode->ResolveAttack(this);
            }
        }
        AttackTime = FMath::Max(0.f, AttackTime - DeltaSeconds);
    }
    if (Dodge.State().Phase==DungeonDodge::EPhase::Dodging) SyncDodgeAction();
    else if (WeaponSkills.State().Action.Active) SyncWeaponSkillAction();
    else if (!(IsContentMelee() && AttackTime > 0.f))
        SetAnimation(AttackTime > 0.f ? TEXT("attack") : HurtTime > 0.f ? TEXT("hurt")
            : ArmorChangeRemaining > 0.f ? TEXT("equip") : bMoving ? TEXT("walk") : TEXT("idle"), DeltaSeconds);
    if (IsEquipmentBound())
    {
        const auto& A=GetWorld()->GetAuthGameMode<ADungeonGameMode>()->GetEquipmentView().Action;
        if (A.Active)
        {
            AnimationName=A.Kind==EDungeonEquipmentActionKind::PickupArmor?TEXT("equip_armor"):TEXT("equip_weapon");
            AnimationTime=float(FMath::Max(0.0,Now-A.Start));
        }
    }
}

bool ADungeonFighter::InitializeStoneGuard(uint64 EntityId,double StartTime)
{
    if(RunInstallBlocksFighter(*this))return false;
    auto Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    if(!Game||!Game->GetEquipmentView().Bound||StoneKnight||StoneBat||StoneGuard||IsEquipmentBound()||bDead||!bEnemy
        ||EnemyContentId!=TEXT("ENM-STN-003")||!EntityId||!FMath::IsFinite(StartTime)||StartTime<0.
        ||GetRuntimeEntityId()!=EntityId||StartTime!=Game->GetSimulationTime()||JumpHeight!=0.f||JumpVelocity!=0.f)return false;
    auto Candidate=MakeUnique<FDungeonStoneGuardDriver>(this,EntityId,StartTime);
    if(!Candidate->BeginCombat())return false;
    const auto D=DungeonStoneGuard::FGuardKernel::Definition();
    StoneGuard=MoveTemp(Candidate);MaxHealth=Health=float(D.HP);bEnemy=true;bAIEnabled=true;
    WeaponId=TEXT("enemy_stone_guard_twohand_axe");bHasAxe=true;
    AttackTime=AttackElapsed=AttackCooldown=InvulnerableTime=HurtTime=0.f;
    ArmorChangeRemaining=0.f;PendingArmorId.Reset();JumpHeight=JumpVelocity=0.f;
    LastGuardSyncTime=StartTime;bGuardDeathObserved=false;SetActorTickEnabled(false);SyncStoneGuardState();return true;
}
bool ADungeonFighter::ClaimStoneGuardDeathEligibility()
{
    if(RunInstallBlocksFighter(*this)||!StoneGuard||!bDead||StoneGuard->State().HP!=0.)return false;
    return StoneGuard->ClaimDeathReward();
}
FVector2D ADungeonFighter::GetCombatBodyHalfExtent() const
{
    if(StoneGuard){const auto D=DungeonStoneGuard::FGuardKernel::Definition();return {D.BodyHalfX,D.BodyHalfY};}
    if(StoneBat){const auto D=DungeonStoneBat::FBatKernel::Definition();return {D.BodyHalfX,D.BodyHalfY};}
    if(StoneKnight){const auto D=DungeonStoneKnight::FKnightKernel::Definition();return {D.BodyHalfX,D.BodyHalfY};}
    return {18.,16.};
}
FVector2D ADungeonFighter::GetProjectileHurtHalfExtent() const
{
    if(StoneGuard){const auto D=DungeonStoneGuard::FGuardKernel::Definition();return {D.HurtHalfX,D.HurtHalfY};}
    if(StoneBat){const auto D=DungeonStoneBat::FBatKernel::Definition();return {D.HurtHalfX,D.HurtHalfY};}
    if(StoneKnight){const auto D=DungeonStoneKnight::FKnightKernel::Definition();return {D.HurtHalfX,D.HurtHalfY};}
    return {18.,16.};
}
void ADungeonFighter::SyncStoneGuardState()
{
    if(!StoneGuard)return;const auto& S=StoneGuard->State();const auto& A=S.Action;
    const FVector2D P(S.Position.X,S.Position.Y);bMoving=GetGroundPosition()!=P;SetActorLocation({P.X,P.Y,0});
    Health=float(S.HP);bDead=S.Phase==DungeonStoneGuard::EPhase::Dead;Facing=float(S.Facing);
    JumpHeight=float(S.Position.Z);JumpVelocity=0.f;InvulnerableTime=0.f;
    using Phase=DungeonStoneGuard::EPhase;
    const bool Owned=S.Phase==Phase::Windup||S.Phase==Phase::Active||S.Phase==Phase::Recovery;
    AttackTime=Owned?float(FMath::Max(0.,S.OccupiedUntil-S.Time)):0.f;
    HurtTime=S.Phase==Phase::Stunned?float(FMath::Max(0.,S.StunUntil-S.Time)):0.f;
    PoiseAccumulation=float(S.PoiseAccum);PoiseProtection=float(FMath::Max(0.,S.ProtectionUntil-S.Time));ComboStage=0;
    const TCHAR* Pose=TEXT("idle");const TCHAR* PhaseName=TEXT("idle");
    switch(S.Phase)
    {
    case Phase::Dormant:Pose=PhaseName=TEXT("dormant");break;
    case Phase::Waking:Pose=PhaseName=TEXT("wake");break;
    case Phase::Idle:Pose=bMoving?TEXT("walk"):TEXT("idle");break;
    case Phase::Windup:Pose=A.Kind==DungeonStoneGuard::EAttack::AxeSweep?TEXT("axe_windup"):TEXT("stomp_windup");PhaseName=TEXT("windup");break;
    case Phase::Active:Pose=A.Kind==DungeonStoneGuard::EAttack::AxeSweep?TEXT("axe_active"):TEXT("stomp_active");PhaseName=TEXT("active");break;
    case Phase::Recovery:Pose=PhaseName=TEXT("recovery");break;
    case Phase::Stunned:Pose=PhaseName=TEXT("hurt");break;
    case Phase::Dead:Pose=PhaseName=TEXT("death");break;
    }
    SetAnimation(FString(TEXT("stone_guard_placeholder_"))+Pose,float(FMath::Max(0.,S.Time-LastGuardSyncTime)));
    AttackPhase=PhaseName;
    if(S.Phase==Phase::Waking)AnimationTime=float(S.Time-S.WakeStartedAt);
    else if(Owned)AnimationTime=float(S.Time-A.Start);
    else if(S.Phase==Phase::Stunned)AnimationTime=float(FMath::Max(0.,S.Time-(S.StunUntil-.4)));
    LastGuardSyncTime=S.Time;
}
