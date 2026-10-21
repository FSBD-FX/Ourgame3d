from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent
BASE=ROOT/'baseline-source'
OUT=ROOT/'production-source'
OUT.mkdir(exist_ok=True)

def put(name,s):
    (OUT/name).write_text(s,encoding='utf-8',newline='\n')
def source(name):
    return (BASE/name).read_text(encoding='utf-8-sig')
def replace(s,old,new):
    assert s.count(old)==1,(old[:90],s.count(old))
    return s.replace(old,new)

put('DungeonGroundWalkPhase.h',r'''#pragma once
#include <array>
#include <cmath>

namespace DungeonGroundWalk
{
// One immutable compiled profile supplies physical stride and six intervals.
// Numeric test fixtures do not configure or approve runtime artwork.
struct FPolicy
{
    double CycleDistance=0.,CycleSeconds=0.;
    std::array<double,6> Durations{};
};
inline bool Valid(const FPolicy& P)
{
    if(!std::isfinite(P.CycleDistance)||P.CycleDistance<=0.
        ||!std::isfinite(P.CycleSeconds)||P.CycleSeconds<=0.)return false;
    double Sum=0.;
    for(double D:P.Durations)
    {
        if(!std::isfinite(D)||D<=0.)return false;
        Sum+=D;if(!std::isfinite(Sum))return false;
    }
    return std::abs(Sum-P.CycleSeconds)<=1.e-12*P.CycleSeconds;
}
inline bool Advance(double Clock,double Distance,const FPolicy& P,double& Out)
{
    if(!Valid(P)||!std::isfinite(Clock)||Clock<0.||!std::isfinite(Distance)||Distance<0.)return false;
    if(Distance==0.){Out=Clock;return true;}
    // Reduce before division/addition: huge finite distances and clocks cannot
    // overflow a quotient or an integer frame cursor. Zero is exact above.
    const double Phase=std::fmod(Clock,P.CycleSeconds)/P.CycleSeconds;
    const double Step=std::fmod(Distance,P.CycleDistance)/P.CycleDistance;
    const double Candidate=std::fmod(Phase+Step,1.)*P.CycleSeconds;
    if(!std::isfinite(Candidate)||Candidate<0.)return false;
    Out=Candidate;return true;
}
inline bool Frame(double Clock,const FPolicy& P,int& Out)
{
    if(!Valid(P)||!std::isfinite(Clock)||Clock<0.)return false;
    const double Phase=std::fmod(Clock,P.CycleSeconds);
    double End=0.;
    for(int I=0;I<6;++I){End+=P.Durations[I];if(Phase<End||I==5){Out=I;return true;}}
    return false;
}
}
''')
shutil.copyfile(ROOT/'stage0-source/DungeonCompletedGroundMotion.h',OUT/'DungeonCompletedGroundMotion.h')

put('DungeonFairytaleSwordWalkProfile.h',r'''#pragma once
#include "CoreMinimal.h"
#include <limits>
#include "DungeonGroundWalkPhase.h"
#include "DungeonFairytaleSwordBodyV001.inl"

namespace DungeonFairytaleSwordWalkV001
{
inline constexpr TCHAR AnimationLabel[]=TEXT("walk_distance_v001");
struct FFrame
{
    FString Body,BodyRest,NearArmWithoutHand,HelmetForeground,NearHand;
    FString ShoulderFar,Chest,ShoulderNear;
    DungeonFairytaleSwordBodyV001::FMarker Marker{};
    bool MeasurementsSupplied=false;
};
struct FProfile
{
    DungeonGroundWalk::FPolicy Gait;
    std::array<FFrame,6> Frames;
    // Set only from a retained, verified six-phase assembly and measurements.
    bool SourceClosureVerified=false;
};
const FProfile& Profile();
inline bool Valid()
{
    const auto& P=Profile();
    if(!P.SourceClosureVerified||!DungeonGroundWalk::Valid(P.Gait)
        ||P.Gait.CycleSeconds>double(std::numeric_limits<float>::max()))return false;
    for(const auto& F:P.Frames)
    {
        const auto InCanvas=[](const FVector2D& V){return FMath::IsFinite(V.X)&&FMath::IsFinite(V.Y)
            &&V.X>=0.&&V.X<=512.&&V.Y>=0.&&V.Y<=512.;};
        if(!F.MeasurementsSupplied||!InCanvas(F.Marker.Root)||!InCanvas(F.Marker.Grip)
            ||!FMath::IsFinite(F.Marker.Axis.X)||!FMath::IsFinite(F.Marker.Axis.Y)
            ||F.Marker.Axis==FVector2D::ZeroVector)return false;
        TSet<FString> Unique;
        for(const FString* Path:{&F.Body,&F.BodyRest,&F.NearArmWithoutHand,&F.HelmetForeground,&F.NearHand,
            &F.ShoulderFar,&F.Chest,&F.ShoulderNear})
        {
            if(!Path->StartsWith(TEXT("/Game/Production/"))||!Path->Contains(TEXT("."))||Unique.Contains(*Path))return false;
            Unique.Add(*Path);
        }
    }
    return true;
}
inline const FFrame* Find(int32 Index)
{return Valid()&&Index>=0&&Index<6?&Profile().Frames[Index]:nullptr;}
}
#include "DungeonFairytaleSwordWalkDataV001.inl"
''')
put('DungeonFairytaleSwordWalkDataV001.inl',r'''#pragma once
// REQUIRED ART INPUT IS PENDING. No root, grip, axis, path or physical stride is
// inferred from the old display pivot or an animation preview's frame duration.
// Root replaces this ONE immutable compiled table from a frozen assembly plus
// measured markers/stride. There is no per-process or command-line policy override.
namespace DungeonFairytaleSwordWalkV001
{
inline const FProfile& Profile()
{
    static const FProfile Pending{};
    return Pending;
}
}
''')
put('DungeonFairytaleSwordWalkTextures.inl',r'''#pragma once
#include "DungeonFairytaleSwordWalkProfile.h"
#include "Engine/Texture2D.h"
#include "Misc/PackageName.h"

namespace DungeonFairytaleSwordWalkV001
{
inline UTexture2D* GetTexture(const FString& Component,int32 Index,TMap<FString,TObjectPtr<UTexture2D>>& Cache)
{
    const auto* F=Find(Index);if(!F)return nullptr;
    const FString* Path=Component==TEXT("Body")?&F->Body:Component==TEXT("BodyRest")?&F->BodyRest
        :Component==TEXT("NearArmWithoutHand")?&F->NearArmWithoutHand:Component==TEXT("HelmetForeground")?&F->HelmetForeground
        :Component==TEXT("NearHand")?&F->NearHand:Component==TEXT("ShoulderFar")?&F->ShoulderFar
        :Component==TEXT("Chest")?&F->Chest:Component==TEXT("ShoulderNear")?&F->ShoulderNear:nullptr;
    if(!Path)return nullptr;
    if(const auto Found=Cache.Find(*Path))return Found->Get();
    const FString Package=FPackageName::ObjectPathToPackageName(*Path);
    UTexture2D* Texture=FPackageName::DoesPackageExist(Package)?LoadObject<UTexture2D>(nullptr,**Path):nullptr;
    Cache.Add(*Path,Texture);return Texture;
}
}
''')

h=source('DungeonFighter.h')
h=replace(h,'#include "DungeonFighter.generated.h"','#include "DungeonCompletedGroundMotion.h"\n#include "DungeonFighter.generated.h"')
h=replace(h,'    virtual void Tick(float DeltaSeconds) override;', '''    virtual void Tick(float DeltaSeconds) override;
    // Native completed-commit witness, never a saved owner field or HUD estimate.
    bool QueryCompletedGroundMotion(FDungeonCompletedGroundMotion& Out) const;
    bool IsOrdinaryGroundWalkPose() const;''')
h=replace(h,'    bool bMoving = false;', '''    bool bMoving = false;
    FDungeonCompletedGroundMotion CompletedGroundMotion;
    bool bGroundMotionFrameOpen=false,bUnconsumedGroundMotion=false,bInvalidGroundMotion=false,bGroundMotionDiscontinuous=false;
    double PendingWalkDistance=0.;
    bool CanAccumulateGroundWalk() const;
    void BeginGroundMotionFrame(double FromTime);
    void RecordCompletedGroundMotion(FVector2D From,FVector2D To,double FromTime,double ToTime,
        bool Grounded,bool OrdinaryEligible,bool HadIntent);
    void EndGroundMotionFrame(double ToTime);
    void InvalidateGroundMotion();''')
put('DungeonFighter.h',h)

s=source('DungeonFighter.cpp')
s=replace(s,'#include "DungeonFighter.h"','#include "DungeonFighter.h"\n#include "DungeonFairytaleSwordWalkProfile.h"\n#include "Misc/CommandLine.h"\n#include "Misc/Parse.h"')
s=replace(s,'    if(!ValidOwnerHeightAnchor(S.HeightAnchorRelative))', '''    if(S.AnimationName.StartsWith(TEXT("walk_distance_"),ESearchCase::IgnoreCase))
    {
        // This saved label has distance-cycle semantics. Never reinterpret a
        // legacy "walk" wall clock or accept a new label without its profile.
        if(!S.AnimationName.Equals(DungeonFairytaleSwordWalkV001::AnimationLabel,ESearchCase::CaseSensitive)
            ||!Player||!DungeonFairytaleSwordWalkV001::Valid()||!S.Moving||S.Dead||S.HurtTime!=0.f
            ||S.JumpHeight!=0.f||S.JumpVelocity!=0.f||S.WeaponId!=TEXT("WPN-SWD-001")
            ||!S.Player.GetValue().Combat.Grounded||S.Player.GetValue().Combat.Action.Active
            ||S.Player.GetValue().WeaponActions.Action.Active||V.Action.Active
            ||S.Player.GetValue().Dodge.Phase!=OwnerDodge::EPhase::Idle
            ||double(S.AnimationTime)>=DungeonFairytaleSwordWalkV001::Profile().Gait.CycleSeconds)
            return Reject(TEXT("Distance Walk label requires its frozen profile and consistent saved ordinary ground pose"));
    }
    if(!ValidOwnerHeightAnchor(S.HeightAnchorRelative))''')
assert s.count('||bResolvingContentWindow||bSuppressOrdinaryMovement)')==2
s=s.replace('||bResolvingContentWindow||bSuppressOrdinaryMovement)',
    '||bResolvingContentWindow||bSuppressOrdinaryMovement||bGroundMotionFrameOpen\n        ||bUnconsumedGroundMotion||bInvalidGroundMotion||PendingWalkDistance!=0.)')
s=replace(s,'    bMoving=S.Moving;','    bMoving=S.Moving;\n    InvalidateGroundMotion(); // Install assigns saved phase, never counts its XY placement.')
helpers=r'''bool ADungeonFighter::CanAccumulateGroundWalk() const
{
    return !bEnemy&&!bDead&&!StoneKnight&&!StoneBat&&!StoneGuard&&HurtTime<=0.f
        &&JumpHeight==0.f&&JumpVelocity==0.f&&Combat.State().Grounded
        &&!Combat.State().Action.Active&&!WeaponSkills.State().Action.Active
        &&Dodge.State().Phase==DungeonDodge::EPhase::Idle&&ArmorChangeRemaining<=0.f
        &&GetEquipmentActionDeadline()<=0.;
}
bool ADungeonFighter::IsOrdinaryGroundWalkPose() const
{return CanAccumulateGroundWalk()&&bMoving&&AnimationName==DungeonFairytaleSwordWalkV001::AnimationLabel
    &&FMath::IsFinite(AnimationTime)&&AnimationTime>=0.f;}
void ADungeonFighter::InvalidateGroundMotion()
{
    CompletedGroundMotion={};bGroundMotionFrameOpen=false;bUnconsumedGroundMotion=false;
    bInvalidGroundMotion=false;bGroundMotionDiscontinuous=false;PendingWalkDistance=0.;
}
void ADungeonFighter::BeginGroundMotionFrame(double FromTime)
{
    CompletedGroundMotion={};bGroundMotionFrameOpen=true;bGroundMotionDiscontinuous=false;
    const auto* Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    if(!Game||!FMath::IsFinite(FromTime)||FromTime<0.){bInvalidGroundMotion=true;return;}
    const auto& V=Game->GetEquipmentView();
    CompletedGroundMotion.RunGuid=V.RunGuid;CompletedGroundMotion.OwnerId=GetRuntimeEntityId();
    CompletedGroundMotion.RoomInstanceId=V.RoomInstanceId;
    CompletedGroundMotion.FromTime=CompletedGroundMotion.ToTime=FromTime;
    CompletedGroundMotion.From=CompletedGroundMotion.To=GetGroundPosition();
    CompletedGroundMotion.Grounded=JumpHeight==0.f&&JumpVelocity==0.f;
    CompletedGroundMotion.OrdinaryEligible=CanAccumulateGroundWalk();
    // A direct public MoveOnGround call may have pending distance already. Do
    // not erase it here; only the next real Actions commit may consume it.
}
void ADungeonFighter::RecordCompletedGroundMotion(FVector2D From,FVector2D To,double FromTime,double ToTime,
    bool Grounded,bool OrdinaryEligible,bool HadIntent)
{
    if(bEnemy)return;
    const double Distance=(To-From).Size();
    if(!FMath::IsFinite(From.X)||!FMath::IsFinite(From.Y)||!FMath::IsFinite(To.X)||!FMath::IsFinite(To.Y)
        ||!FMath::IsFinite(FromTime)||!FMath::IsFinite(ToTime)||FromTime<0.||ToTime<FromTime
        ||!FMath::IsFinite(Distance)){bInvalidGroundMotion=true;CompletedGroundMotion.Published=false;return;}
    bUnconsumedGroundMotion=true;
    if(Grounded&&OrdinaryEligible&&HadIntent)PendingWalkDistance+=Distance;
    if(!FMath::IsFinite(PendingWalkDistance)){bInvalidGroundMotion=true;return;}
    if(!bGroundMotionFrameOpen){CompletedGroundMotion.Published=false;return;}
    auto& M=CompletedGroundMotion;
    // A skill/room placement between ordinary commits invalidates this frame's
    // witness. It is not a new distance and must not poison later stable saves.
    if(M.To!=From||M.ToTime!=FromTime)bGroundMotionDiscontinuous=true;
    M.To=To;M.ToTime=ToTime;M.AcceptedDistance+=Distance;
    M.WalkDistance+=(Grounded&&OrdinaryEligible&&HadIntent)?Distance:0.;
    M.Grounded=M.Grounded&&Grounded;M.OrdinaryEligible=M.OrdinaryEligible&&OrdinaryEligible;
    M.HadMoveIntent=M.HadMoveIntent||HadIntent;
}
void ADungeonFighter::EndGroundMotionFrame(double ToTime)
{
    bGroundMotionFrameOpen=false;
    const auto* Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    if(!Game)return;
    const auto& V=Game->GetEquipmentView();auto& M=CompletedGroundMotion;
    const bool SameScope=V.Bound&&V.RunGuid==M.RunGuid&&V.OwnerId==M.OwnerId
        &&V.RoomInstanceId==M.RoomInstanceId&&GetRuntimeEntityId()==M.OwnerId;
    // Room installation/restart/scene placement is not ordinary movement.
    if(!SameScope||M.To!=GetGroundPosition()){InvalidateGroundMotion();return;}
    M.Published=!bInvalidGroundMotion&&!bGroundMotionDiscontinuous&&!bUnconsumedGroundMotion&&PendingWalkDistance==0.
        &&FMath::IsFinite(ToTime)&&M.ToTime==ToTime&&M.FromTime<ToTime;
}
bool ADungeonFighter::QueryCompletedGroundMotion(FDungeonCompletedGroundMotion& Out) const
{
    const auto* Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    if(!Game||bGroundMotionFrameOpen||bUnconsumedGroundMotion||bInvalidGroundMotion
        ||PendingWalkDistance!=0.||!CompletedGroundMotion.Published)return false;
    const auto& M=CompletedGroundMotion;const auto& V=Game->GetEquipmentView();
    if(!V.Bound||V.RunGuid!=M.RunGuid||V.OwnerId!=M.OwnerId||V.RoomInstanceId!=M.RoomInstanceId
        ||GetRuntimeEntityId()!=M.OwnerId||Game->GetSimulationTime()!=M.ToTime||GetGroundPosition()!=M.To)return false;
    Out=M;return true;
}

'''
s=replace(s,'void ADungeonFighter::MoveOnGround(FVector2D Direction, float DeltaSeconds)',helpers+'void ADungeonFighter::MoveOnGround(FVector2D Direction, float DeltaSeconds)')
s=replace(s,'    bMoving = true;','    const bool OrdinaryEligible=CanAccumulateGroundWalk();\n    const bool Grounded=JumpHeight==0.f&&JumpVelocity==0.f;')
s=replace(s,'    SetActorLocation(FVector(Position.X, Position.Y, 0.f));\n    SyncWeaponMuzzleTransform();\n    CommitIdleDodgePosition();', '''    SetActorLocation(FVector(Position.X, Position.Y, 0.f));
    const auto Actual=GetGroundPosition();bMoving=Actual!=From;
    const auto* Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    const double FromTime=Game?Game->GetSimulationTime():FMath::Max(Combat.State().Time,WeaponSkills.State().Time);
    RecordCompletedGroundMotion(From,Actual,FromTime,FromTime+double(DeltaSeconds),Grounded,OrdinaryEligible,true);
    SyncWeaponMuzzleTransform();
    CommitIdleDodgePosition();''')
s=replace(s,'    Health = MaxHealth;','    InvalidateGroundMotion();\n    Health = MaxHealth;')
s=replace(s,'''    Super::Tick(DeltaSeconds);
    SimulateMotion(DeltaSeconds, true);
    SimulateActions(DeltaSeconds);''','''    Super::Tick(DeltaSeconds);
    const double FromTime=FMath::Max(Combat.State().Time,WeaponSkills.State().Time);
    BeginGroundMotionFrame(FromTime);
    SimulateMotion(DeltaSeconds, true);
    SimulateActions(DeltaSeconds);
    EndGroundMotionFrame(FMath::Max(Combat.State().Time,WeaponSkills.State().Time));''')
s=replace(s,'    if (bDead) return;\n    if (IsContentMelee() || IsEquipmentBound()) AdvanceContentActionTo(Now);',
    '    if (bDead){PendingWalkDistance=0.;bUnconsumedGroundMotion=false;return;}\n    if (IsContentMelee() || IsEquipmentBound()) AdvanceContentActionTo(Now);')
s=replace(s,'''    else if (!(IsContentMelee() && AttackTime > 0.f))
        SetAnimation(AttackTime > 0.f ? TEXT("attack") : HurtTime > 0.f ? TEXT("hurt")
            : ArmorChangeRemaining > 0.f ? TEXT("equip") : bMoving ? TEXT("walk") : TEXT("idle"), DeltaSeconds);''', '''    else if (!(IsContentMelee() && AttackTime > 0.f))
    {
        const FString Next=AttackTime > 0.f ? TEXT("attack") : HurtTime > 0.f ? TEXT("hurt")
            : ArmorChangeRemaining > 0.f ? TEXT("equip") : bMoving ? TEXT("walk") : TEXT("idle");
        const bool DistanceRequested=IsEquipmentBound()
            &&(FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordWalkPreview"))
                ||AnimationName==DungeonFairytaleSwordWalkV001::AnimationLabel);
        if(Next==TEXT("walk")&&CanAccumulateGroundWalk()&&ContentWeapon()==DungeonContentCombat::EWeapon::SWD001&&DistanceRequested
            &&DungeonFairytaleSwordWalkV001::Valid())
        {
            double Phase=0.;const double Before=AnimationName==DungeonFairytaleSwordWalkV001::AnimationLabel?double(AnimationTime):0.;
            if(DungeonGroundWalk::Advance(Before,PendingWalkDistance,DungeonFairytaleSwordWalkV001::Profile().Gait,Phase))
            {
                AnimationName=DungeonFairytaleSwordWalkV001::AnimationLabel;AnimationTime=float(Phase);
                if(double(AnimationTime)>=DungeonFairytaleSwordWalkV001::Profile().Gait.CycleSeconds)AnimationTime=0.f;
            }
            else bInvalidGroundMotion=true;
        }
        else SetAnimation(Next,DeltaSeconds);
    }''')
s=replace(s,'''            AnimationTime=float(FMath::Max(0.0,Now-A.Start));
        }
    }
}

bool ADungeonFighter::InitializeStoneGuard''','''            AnimationTime=float(FMath::Max(0.0,Now-A.Start));
        }
    }
    // Even when an action starts at this boundary, no movement accumulator may
    // escape into a successful Capture. The saved AnimationTime is final here.
    PendingWalkDistance=0.;bUnconsumedGroundMotion=false;
}

bool ADungeonFighter::InitializeStoneGuard''')
put('DungeonFighter.cpp',s)

s=source('DungeonGameMode.cpp')
s=replace(s,'    PlayerFighter->UpdatePlayerInput(0.f,true);','    PlayerFighter->BeginGroundMotionFrame(SimulationTime);\n    PlayerFighter->UpdatePlayerInput(0.f,true);')
s=replace(s,'        const auto CommitMotion=[Step,&Predicted](ADungeonFighter* Fighter)','        const auto CommitMotion=[Step,FromTime,ToTime,&Predicted](ADungeonFighter* Fighter)')
s=replace(s,'''            // Timers, existing resources and ballistic velocity advance exactly once.
            // XY is the already resolved query result, not a second movement attempt.''','''            const bool OrdinaryEligible=Fighter->CanAccumulateGroundWalk();
            const bool HadIntent=!Fighter->bEnemy&&!Fighter->ReadMoveIntent().IsNearlyZero();
            // Timers, existing resources and ballistic velocity advance exactly once.
            // XY is the already resolved query result, not a second movement attempt.''')
s=replace(s,'                Fighter->bMoving=!P.Start.Equals(P.End,1.e-9);', '''                const auto Actual=Fighter->GetGroundPosition();
                Fighter->bMoving=Actual!=P.Start;
                Fighter->RecordCompletedGroundMotion(P.Start,Actual,FromTime,ToTime,
                    P.StartHeight==0.&&P.EndHeight==0.&&Fighter->JumpVelocity==0.f,OrdinaryEligible,HadIntent);''')
s=replace(s,'''    bSceneEquipmentTargetLost=false;
    ObserveRunExploration(); // One observation per completed Tick, independent of Canvas.''','''    PlayerFighter->EndGroundMotionFrame(SimulationTime);
    bSceneEquipmentTargetLost=false;
    ObserveRunExploration(); // One observation per completed Tick, independent of Canvas.''')
put('DungeonGameMode.cpp',s)

h=source('DungeonHUD.h')
h=replace(h,'    bool bUseFairytaleSwordEquipmentBoundPreview', '    bool bUseFairytaleSwordWalkPreview=false;\n    bool bUseFairytaleSwordEquipmentBoundPreview')
put('DungeonHUD.h',h)
s=source('DungeonHUD.cpp')
s=replace(s,'#include "DungeonHUD.h"','#include "DungeonHUD.h"\n#include "DungeonFairytaleSwordWalkTextures.inl"')
s=replace(s,'    bUseFairytaleLookdevPreview=!bUseFairytaleSwordEquipmentBoundPreview', '''    bUseFairytaleSwordWalkPreview=bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordWalkPreview"));
    bUseFairytaleLookdevPreview=!bUseFairytaleSwordEquipmentBoundPreview''')
s=replace(s,'''#if WITH_EDITOR
        FTextureCompilingManager::Get().FinishCompilation(ReadyArmorTextures);''','''        if(bUseFairytaleSwordWalkPreview)
            for(const FString Component:{TEXT("Body"),TEXT("BodyRest"),TEXT("NearArmWithoutHand"),TEXT("HelmetForeground"),
                TEXT("NearHand"),TEXT("ShoulderFar"),TEXT("Chest"),TEXT("ShoulderNear")})
                for(int32 I=0;I<6;++I)
                    if(auto Texture=DungeonFairytaleSwordWalkV001::GetTexture(Component,I,Frames))ReadyArmorTextures.Add(Texture);
#if WITH_EDITOR
        FTextureCompilingManager::Get().FinishCompilation(ReadyArmorTextures);''')
put('DungeonHUD.cpp',s)

s=source('DungeonFairytaleSwordPresentation.cpp')
s=replace(s,'#include "DungeonHUD.h"','#include "DungeonHUD.h"\n#include "DungeonFairytaleSwordWalkTextures.inl"')
s=replace(s,'    using namespace DungeonFairytaleSwordBodyV001;\n    if((bUseFairytaleSwordEquipmentBoundPreview', '''    using namespace DungeonFairytaleSwordBodyV001;
    if(bUseFairytaleSwordWalkPreview&&Clip==TEXT("sword_walk"))
        return DungeonFairytaleSwordWalkV001::GetTexture(TEXT("Body"),Index,Frames);
    if((bUseFairytaleSwordEquipmentBoundPreview''')
s=replace(s,'    Record.Supported=Primary1 || Primary2 || Primary3 || StableIdle;', '''    int WalkFrame=-1;
    const bool StableWalk=bUseFairytaleSwordWalkPreview&&Sword&&F->IsOrdinaryGroundWalkPose()
        &&DungeonFairytaleSwordWalkV001::Valid()
        &&DungeonGroundWalk::Frame(double(F->AnimationTime),DungeonFairytaleSwordWalkV001::Profile().Gait,WalkFrame);
    Record.WalkPose=StableWalk;
    if(StableWalk){Record.WalkPhase=F->AnimationTime;Record.WalkCycleDistance=DungeonFairytaleSwordWalkV001::Profile().Gait.CycleDistance;}
    Record.Supported=Primary1 || Primary2 || Primary3 || StableIdle || StableWalk;''')
s=replace(s,'Record.Clip=Primary3?TEXT("sword_primary_3")','Record.Clip=StableWalk?TEXT("sword_walk"):Primary3?TEXT("sword_primary_3")')
s=replace(s,'    Record.Frame=(Primary1||Primary2||Primary3)?F->GetPrimaryPoseFrame():StableIdle',
    '    Record.Frame=StableWalk?WalkFrame:(Primary1||Primary2||Primary3)?F->GetPrimaryPoseFrame():StableIdle')
s=replace(s,'    const FMarker* Marker=Primary3?',
    '    const auto* WalkSource=StableWalk?DungeonFairytaleSwordWalkV001::Find(Record.Frame):nullptr;\n    const FMarker* Marker=WalkSource?&WalkSource->Marker:Primary3?')
s=replace(s,'''    const bool ArmorPhase=(!Record.EquipmentBoundMode || DrawGear)
        &&((Record.ArmorPreview''','''    const bool WalkArmorPhase=StableWalk&&BoundLightArmor;
    const bool ArmorPhase=(!Record.EquipmentBoundMode || DrawGear)
        &&(WalkArmorPhase || (Record.ArmorPreview''')
s=replace(s,'    const int32 LayerCount=(PrimaryArmorPhase||Primary2ArmorPhase||Primary3ArmorPhase)?7:6;',
    '    const int32 LayerCount=(StableWalk||PrimaryArmorPhase||Primary2ArmorPhase||Primary3ArmorPhase)?7:6;')
s=replace(s,'    if(ArmorPhase)\n    {\n        Record.ArmorReady=true;', '''    if(StableWalk || ArmorPhase)
    {
        Record.ArmorReady=true;''')
s=replace(s,'''            ReadyLayers[I]=Primary3ArmorPhase''','''            if(StableWalk&&!WalkArmorPhase&&(I==1||I==2||I==4))continue;
            ReadyLayers[I]=StableWalk?DungeonFairytaleSwordWalkV001::GetTexture(PrimaryComponents[I],Record.Frame,Frames):Primary3ArmorPhase''')
s=replace(s,'    if(ArmorPhase)\n    {\n        for(int32 I=0;I<LayerCount-1;++I)DrawBodyLayer(ReadyLayers[I]);', '''    if(StableWalk)
    {
        for(int32 I=0;I<LayerCount-1;++I)
            if(WalkArmorPhase||(I!=1&&I!=2&&I!=4))DrawBodyLayer(ReadyLayers[I]);
        if(WalkArmorPhase)
        {
            Record.ArmorDrawn=true;bRenderedArmorLayersUsed=true;
            for(int32 I : {1,2,4})RenderedArmorLayerPaths.Add(ReadyLayers[I]->GetPathName());
        }
    }
    else if(ArmorPhase)
    {
        for(int32 I=0;I<LayerCount-1;++I)DrawBodyLayer(ReadyLayers[I]);''')
s=replace(s,'    if(ArmorPhase)DrawBodyLayer(ReadyLayers[LayerCount-1]);',
    '    if(StableWalk||ArmorPhase)DrawBodyLayer(ReadyLayers[LayerCount-1]);')
put('DungeonFairytaleSwordPresentation.cpp',s)

h=source('DungeonFairytaleSwordDrawState.h')
h=replace(h,'    bool ActionPoseSupported=false, GearPlaceholder=false;', '''    bool ActionPoseSupported=false, GearPlaceholder=false;
    bool WalkPose=false;
    double WalkPhase=0.,WalkCycleDistance=0.; // Same-draw read-only compiled profile facts.''')
put('DungeonFairytaleSwordDrawState.h',h)
print('candidate files',len(list(OUT.iterdir())))
