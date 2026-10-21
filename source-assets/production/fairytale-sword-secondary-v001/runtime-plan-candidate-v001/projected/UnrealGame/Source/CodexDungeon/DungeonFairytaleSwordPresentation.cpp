#include "DungeonHUD.h"
#include "DungeonFairytaleSwordWalkTextures.inl"
#include "DungeonFairytaleSwordEquipmentBinding.h"
#include "DungeonFighter.h"
#include "DungeonGameMode.h"
#include "DungeonFairytaleSwordBodyV001.inl"
#include "DungeonFairytaleSwordBodyV002.inl"
#include "DungeonFairytaleSwordPrimary2V001.inl"
#include "DungeonFairytaleSwordPrimary2V002.inl"
#include "DungeonFairytaleSwordPrimary2V003.inl"
#include "Engine/Canvas.h"
#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "CanvasItem.h"
#include "Misc/PackageName.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "TextureResource.h"
#include "DungeonFairytaleSwordPrimary2ArmorV001.inl"
#include "DungeonFairytaleSwordPrimary3V001.inl"
#include "DungeonFairytaleSwordPrimary3V002.inl"
#include "UnrealClient.h"

UTexture2D* ADungeonHUD::GetFairytaleSwordArmorReadyTexture(const FString& Component,int32 Frame)
{
    if(Frame<0 || Frame>=4)return nullptr;
    const bool LeatherReady=bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherReadyPreview"))
        &&(Component==TEXT("Chest")||Component==TEXT("ShoulderFar")||Component==TEXT("ShoulderNear"));
    const FString Name=LeatherReady
        ?FString::Printf(TEXT("T_Fairytale_LeatherReady%s_%03d_v001"),*Component,Frame)
        :FString::Printf(TEXT("T_Fairytale_SwordReady%s_%03d_v001"),*Component,Frame);
    if(const auto Found=Frames.Find(Name))return Found->Get();
    const FString Package=FString(LeatherReady?TEXT("/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady/")
        :TEXT("/Game/Production/ArtTrials/EV048/v006/HeroSwordArmorReady/"))+Name;
    UTexture2D* Texture=FPackageName::DoesPackageExist(Package)
        ?LoadObject<UTexture2D>(nullptr,*(Package+TEXT(".")+Name)):nullptr;
    Frames.Add(Name,Texture);
    return Texture;
}

UTexture2D* ADungeonHUD::GetFairytaleSwordArmorPrimary1Texture(const FString& Component,int32 Frame)
{
    if(Frame<0 || Frame>=6)return nullptr;
    // Request258 two-frame trial; actual draw still requires committed LightArmor.
    const bool Bridge258=Frame<2 && bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary1Preview"))
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytalePrimary1Bridge258Preview"));
    const bool LeatherPrimary1=bUseFairytaleSwordEquipmentBoundPreview
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary1Preview"))
        &&(Component==TEXT("Chest")||Component==TEXT("ShoulderFar")||Component==TEXT("ShoulderNear"));
    const FString Name=Bridge258
        ?FString::Printf(TEXT("T_Fairytale_Bridge258_%s_%03d_v001"),*Component,Frame)
        :LeatherPrimary1
        ?FString::Printf(TEXT("T_Fairytale_LeatherPrimary1%s_%03d_v001"),*Component,Frame)
        :FString::Printf(TEXT("T_Fairytale_SwordPrimary1%s_%03d_v001"),*Component,Frame);
    if(const auto Found=Frames.Find(Name))return Found->Get();
    const FString Package=FString(Bridge258?TEXT("/Game/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/")
        :LeatherPrimary1?TEXT("/Game/Production/ArtTrials/EV048/v013/HeroLeatherPrimary1/")
        :TEXT("/Game/Production/ArtTrials/EV048/v007/HeroSwordArmorPrimary1/"))+Name;
    UTexture2D* Texture=FPackageName::DoesPackageExist(Package)
        ?LoadObject<UTexture2D>(nullptr,*(Package+TEXT(".")+Name)):nullptr;
    Frames.Add(Name,Texture);
    return Texture;
}

UTexture2D* ADungeonHUD::GetFairytaleSwordTexture(const FString& Clip,int32 Index)
{
    using namespace DungeonFairytaleSwordBodyV001;
    if(bUseFairytaleSwordWalkPreview&&Clip==TEXT("sword_walk"))
        return DungeonFairytaleSwordWalkV001::GetTexture(TEXT("Body"),Index,Frames);
    if((bUseFairytaleSwordEquipmentBoundPreview || DungeonFairytaleSwordPrimary3V001::Enabled()) && Clip==TEXT("sword_primary_3"))
    {
        if(Index<0 || Index>=DungeonFairytaleSwordPrimary3V001::Count(Clip))return nullptr;
        return DungeonFairytaleSwordPrimary3V001::GetTexture(TEXT("Body"),Index,Frames);
    }
    const bool Second=bUseFairytaleSwordPrimary2Preview && Clip==TEXT("sword_primary_2");
    const bool SecondBodyTrial=Second && (FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2BodyPreview"))
        ||DungeonFairytaleSwordPrimary2ArmorV001::Enabled() || DungeonFairytaleSwordPrimary3V001::Enabled()
        ||bUseFairytaleSwordEquipmentBoundPreview);
    const int32 FrameCount=Second?(SecondBodyTrial?DungeonFairytaleSwordPrimary2V003::Count(Clip):DungeonFairytaleSwordPrimary2V001::Count(Clip))
        :bUseFairytaleSwordBodyV002Preview?DungeonFairytaleSwordBodyV002::Count(Clip):Count(Clip);
    if(Index<0 || Index>=FrameCount)return nullptr;
    const int32 Version=Second?(SecondBodyTrial?2:1):bUseFairytaleSwordBodyV002Preview?2:1;
    FString Name;
    if(Clip==TEXT("sword_ready_idle"))
        Name=FString::Printf(TEXT("T_Fairytale_SwordReady_%03d_v%03d"),Index,Version);
    else if(Clip==TEXT("sword_primary_1"))
        Name=FString::Printf(TEXT("T_Fairytale_SwordPrimary1_%03d_v%03d"),Index,Version);
    else if(Second)
        Name=FString::Printf(TEXT("T_Fairytale_SwordPrimary2_%03d_v%03d"),Index,Version);
    else return nullptr;
    if(const auto Found=Frames.Find(Name))return Found->Get();
    const FString Package=FString(Second?(SecondBodyTrial?TEXT("/Game/Production/ArtTrials/EV048/v009/HeroSwordPrimary2/")
        :TEXT("/Game/Production/ArtTrials/EV048/v008/HeroSwordPrimary2/")):bUseFairytaleSwordBodyV002Preview
        ?TEXT("/Game/Production/ArtTrials/EV048/v005/HeroSwordBody/")
        :TEXT("/Game/Production/ArtTrials/EV048/v004/HeroSwordBody/"))+Name;
    UTexture2D* Texture=FPackageName::DoesPackageExist(Package)
        ?LoadObject<UTexture2D>(nullptr,*(Package+TEXT(".")+Name)):nullptr;
    Frames.Add(Name,Texture);
    return Texture;
}

bool ADungeonHUD::DrawFairytaleSwordBody(ADungeonFighter* F)
{
    if(!F || F->bEnemy)return false;
    ResetFairytaleSwordSecondaryDraw();
    // Clear Dodge observation before higher-priority Death/Hurt can return.
    const uint64 PreviousDodgeDrawId=FairytaleSwordDodgeDraw.DrawId;
    FairytaleSwordDodgeDraw=FDungeonFairytaleSwordDodgeDraw();
    FairytaleSwordDodgeDraw.DrawId=PreviousDodgeDrawId;
    FairytaleSwordDodgeDraw.OptIn=bUseFairytaleSwordDodgePreview;
    const uint64 PreviousDeathDrawId=FairytaleSwordDeathDraw.DrawId;
    FairytaleSwordDeathDraw=FDungeonFairytaleSwordDeathDraw();
    FairytaleSwordDeathDraw.DrawId=PreviousDeathDrawId;
    FairytaleSwordDeathDraw.OptIn=bUseFairytaleSwordDeathPreview;
    // Unsupported gear continues this same clock-helmet presenter; a supported
    // Death draw owns its complete/closed branch ahead of living Hurt and Ready.
    if(bUseFairytaleSwordDeathPreview && F->bDead && DrawFairytaleSwordDeathBody(F))return true;
    const uint64 PreviousHurtDrawId=FairytaleSwordHurtDraw.DrawId;
    FairytaleSwordHurtDraw=FDungeonFairytaleSwordHurtDraw();
    FairytaleSwordHurtDraw.DrawId=PreviousHurtDrawId;
    FairytaleSwordHurtDraw.OptIn=bUseFairytaleSwordHurtPreview;
    if(bUseFairytaleSwordHurtPreview && !F->bDead && F->AnimationName==TEXT("hurt"))
        return DrawFairytaleSwordHurtBody(F);
    // Death > Hurt > actual air > Dodge. Backward roll keeps actual Facing.
    if(bUseFairytaleSwordDodgePreview && !F->bDead && F->JumpHeight==0.f && F->GetVerticalVelocity()==0.f
        && F->AnimationName==TEXT("dodge") && F->GetDodgeState().Phase==DungeonDodge::EPhase::Dodging
        && DrawFairytaleSwordDodgeBody(F))return true;
    if(bUseFairytaleSwordAirPreview && DrawFairytaleSwordAirBody(F))return true;
    if(bUseFairytaleSwordSecondaryPreview && DrawFairytaleSwordSecondaryBody(F))return true;
    using namespace DungeonFairytaleSwordBodyV001;
    const uint64 PreviousDrawId=FairytaleSwordDraw.DrawId;
    FairytaleSwordDraw=FDungeonFairytaleSwordDraw();
    auto& Record=FairytaleSwordDraw;
    Record.Active=true;
    Record.DrawId=PreviousDrawId;
    Record.CanvasSize=CanvasSize;
    Record.Facing=F->Facing<0?-1:1;
    Record.NativeScreenshotPath=FScreenshotRequest::IsScreenshotRequested()?FScreenshotRequest::GetFilename():FString();

    const auto& Melee=F->GetMeleeCombatState();
    const auto& Action=Melee.Action;
    const auto* Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    Record.SimulationTime=Game?Game->GetSimulationTime():Melee.Time;
    Record.InstanceId=Action.Active?Action.WeaponInstanceId:Melee.WeaponInstanceId;
    if(Action.Active)
    {
        Record.ActionId=Action.AttackId;
        Record.Stage=int32(Action.Stage);
        Record.ActionStart=Action.Start;
        Record.ActiveAt=Action.ActiveStart;
        Record.ActiveEnd=Action.ActiveEnd;
        Record.ActionEnd=Action.End;
    }

    Record.EquipmentBoundMode=bUseFairytaleSwordEquipmentBoundPreview;
    if(Record.EquipmentBoundMode)
    {
        if(Game)Record.EquipmentBindingValid=DungeonFairytaleSwordEquipmentBinding::Resolve(
            *Game,*F,Record.EquipmentBinding,Record.EquipmentBindingDiagnostic);
        else Record.EquipmentBindingDiagnostic=TEXT("No actual authoritative GameMode for equipment-bound draw");
    }
    // One resolver call controls both weapon and all armor phases. Old art flags
    // cannot override missing/unsupported committed gear in explicit Bound mode.
    const bool BoundLightArmor=Record.EquipmentBoundMode && Record.EquipmentBindingValid
        &&Record.EquipmentBinding.Armor==DungeonFairytaleSwordEquipmentBinding::EArmor::LightArmor;
    const bool Sword=Record.EquipmentBoundMode?Record.EquipmentBindingValid
        :((F->WeaponId==TEXT("sword") || F->WeaponId==TEXT("WPN-SWD-001"))
            &&Melee.Weapon==DungeonContentCombat::EWeapon::SWD001);
    const bool Primary1=Sword && !F->bDead && Action.Active
        && Action.Weapon==DungeonContentCombat::EWeapon::SWD001
        && Action.Stage==0 && !Action.StartedAirborne;
    const bool Primary2=bUseFairytaleSwordPrimary2Preview && Sword && !F->bDead && Action.Active
        && Action.Weapon==DungeonContentCombat::EWeapon::SWD001
        && Action.Stage==1 && !Action.StartedAirborne;
    const bool Primary3=(Record.EquipmentBoundMode || DungeonFairytaleSwordPrimary3V001::Enabled()) && Sword && !F->bDead && Action.Active && Melee.Grounded
        && Action.Weapon==DungeonContentCombat::EWeapon::SWD001
        && Action.Stage==2 && !Action.StartedAirborne;
    const bool StableIdle=Sword && !F->bDead && !Action.Active && Melee.Grounded
        && F->AnimationName==TEXT("idle") && F->JumpHeight==0.f
        && !F->GetWeaponSkillAction().Active
        && F->GetDodgeState().Phase!=DungeonDodge::EPhase::Dodging
        && F->GetArmorChangeRemaining()<=0.f
        && FMath::IsFinite(F->AnimationTime) && F->AnimationTime>=0.f;
    int WalkFrame=-1;
    const bool StableWalk=bUseFairytaleSwordWalkPreview&&Sword&&F->IsOrdinaryGroundWalkPose()
        &&DungeonFairytaleSwordWalkV001::Valid()
        &&DungeonGroundWalk::Frame(double(F->AnimationTime),DungeonFairytaleSwordWalkV001::Profile().Gait,WalkFrame);
    Record.WalkPose=StableWalk;
    if(StableWalk){Record.WalkPhase=F->AnimationTime;Record.WalkCycleDistance=DungeonFairytaleSwordWalkV001::Profile().Gait.CycleDistance;}
    Record.Supported=Primary1 || Primary2 || Primary3 || StableIdle || StableWalk;
    Record.ActionPoseSupported=Record.Supported;
    const auto* PendingPickup=Game?&Game->GetEquipmentView().Action:nullptr;
    const bool ActualPickup=PendingPickup && PendingPickup->Active && PendingPickup->ActionId
        &&PendingPickup->OperationId && PendingPickup->SourceId && PendingPickup->InstanceId
        &&((PendingPickup->Kind==EDungeonEquipmentActionKind::PickupArmor && PendingPickup->Slot==2)
            ||(PendingPickup->Kind==EDungeonEquipmentActionKind::PickupWeapon && PendingPickup->Slot>=0 && PendingPickup->Slot<2))
        &&FMath::IsFinite(PendingPickup->Start) && FMath::IsFinite(PendingPickup->Deadline)
        &&PendingPickup->Start>=0. && PendingPickup->Start<=Record.SimulationTime && Record.SimulationTime<PendingPickup->Deadline;
    // Reuse only this draw's successful committed binding. The pending target
    // never selects a skin; unknown armor and all unrelated unsupported poses stay closed.
    Record.GearPlaceholder=Record.EquipmentBoundMode && Record.EquipmentBindingValid && !Record.ActionPoseSupported
        &&ActualPickup && !F->bDead && Melee.Grounded && F->JumpHeight==0.f && F->GetVerticalVelocity()==0.f
        &&!Action.Active && !F->GetWeaponSkillAction().Active && F->GetDodgeState().Phase==DungeonDodge::EPhase::Idle
        &&((PendingPickup->Kind==EDungeonEquipmentActionKind::PickupArmor && F->AnimationName==TEXT("equip_armor"))
            ||(PendingPickup->Kind==EDungeonEquipmentActionKind::PickupWeapon && F->AnimationName==TEXT("equip_weapon")));
    const bool DrawGear=Record.Supported || Record.GearPlaceholder;
    Record.Clip=StableWalk?TEXT("sword_walk"):Primary3?TEXT("sword_primary_3"):Primary2?TEXT("sword_primary_2"):Primary1?TEXT("sword_primary_1"):TEXT("sword_ready_idle");
    // The accepted kernel owns attack timing/speed. No independent attack clock.
    Record.Frame=StableWalk?WalkFrame:(Primary1||Primary2||Primary3)?F->GetPrimaryPoseFrame():StableIdle
        ?FMath::FloorToInt(double(F->AnimationTime)/.167)%4:0;
    if(Record.GearPlaceholder){Record.Clip=TEXT("sword_ready_idle");Record.Frame=0;}
    const bool RisingAxisTrial=Primary2 && FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2ArcPreview"));
    const bool Primary2BodyTrial=Primary2 && (FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleSwordPrimary2BodyPreview"))
        ||DungeonFairytaleSwordPrimary2ArmorV001::Enabled() || DungeonFairytaleSwordPrimary3V001::Enabled()
        ||bUseFairytaleSwordEquipmentBoundPreview);
    const auto* WalkSource=StableWalk?DungeonFairytaleSwordWalkV001::Find(Record.Frame):nullptr;
    const FMarker* Marker=WalkSource?&WalkSource->Marker:Primary3?(Record.EquipmentBoundMode?DungeonFairytaleSwordPrimary3V002::Find(Record.Clip,Record.Frame)
        :DungeonFairytaleSwordPrimary3V001::Find(Record.Clip,Record.Frame))
        :Primary2BodyTrial?DungeonFairytaleSwordPrimary2V003::Find(Record.Clip,Record.Frame)
        :RisingAxisTrial?DungeonFairytaleSwordPrimary2V002::Find(Record.Clip,Record.Frame)
        :Primary2?DungeonFairytaleSwordPrimary2V001::Find(Record.Clip,Record.Frame):bUseFairytaleSwordBodyV002Preview
        ?DungeonFairytaleSwordBodyV002::Find(Record.Clip,Record.Frame):Find(Record.Clip,Record.Frame);
    // Provisional Request258 source-pixel markers. No new action clock or timing.
    // The old full Body below remains legacy metadata/readiness only in this
    // seven-layer LightArmor branch; DrawStack records every actual new layer.
    FMarker Bridge258Marker{};
    if(Marker && Primary1 && BoundLightArmor && Record.Frame>=0 && Record.Frame<2
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary1Preview"))
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytalePrimary1Bridge258Preview")))
    {
        Bridge258Marker=*Marker;
        Bridge258Marker.Root=FVector2D(256.,464.);
        Bridge258Marker.Grip=Record.Frame==0?FVector2D(211.,343.):FVector2D(159.,213.);
        Bridge258Marker.Axis=Record.Frame==0?FVector2D(.94,-.341):FVector2D(-.2,-.98);
        Bridge258Marker.FistPolygon.Reset(); // NearHand texture owns visible fist.
        Marker=&Bridge258Marker;
    }
    UTexture2D* Body=GetFairytaleSwordTexture(Record.Clip,Record.Frame);
    Record.TexturePath=Body?Body->GetPathName():FString();
    Record.TextureReady=Body && Body->GetResource()
        && !Body->HasPendingRenderResourceInitialization() && Marker;
    Record.ArmorPreview=Record.EquipmentBoundMode?BoundLightArmor:bUseFairytaleSwordArmorReadyPreview;
    const bool PrimaryArmorPhase=Primary1 && (Record.EquipmentBoundMode?BoundLightArmor:bUseFairytaleSwordArmorPrimary1Preview);
    const bool Primary2ArmorPhase=Primary2 && (Record.EquipmentBoundMode?BoundLightArmor
        :(DungeonFairytaleSwordPrimary2ArmorV001::Enabled() || DungeonFairytaleSwordPrimary3V001::Enabled()));
    const bool Primary3ArmorPhase=Primary3 && (Record.EquipmentBoundMode?BoundLightArmor:DungeonFairytaleSwordPrimary3V001::ArmorEnabled());
    const bool WalkArmorPhase=StableWalk&&BoundLightArmor;
    const bool ArmorPhase=(!Record.EquipmentBoundMode || DrawGear)
        &&(WalkArmorPhase || (Record.ArmorPreview && (StableIdle || Record.GearPlaceholder)) || PrimaryArmorPhase || Primary2ArmorPhase || Primary3ArmorPhase);
    // Source body partition is exclusive, and every part keeps its original UVs.
    // Ready and each supported primary stage use their own source phase partition.
    static const TCHAR* Components[]={TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),
        TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("NearHand")};
    static const TCHAR* PrimaryComponents[]={TEXT("BodyRest"),TEXT("ShoulderFar"),TEXT("Chest"),
        TEXT("NearArmWithoutHand"),TEXT("ShoulderNear"),TEXT("HelmetForeground"),TEXT("NearHand")};
    const int32 LayerCount=(StableWalk||PrimaryArmorPhase||Primary2ArmorPhase||Primary3ArmorPhase)?7:6;
    UTexture2D* ReadyLayers[7]={};
    if(StableWalk || ArmorPhase)
    {
        Record.ArmorReady=true;
        for(int32 I=0;I<LayerCount;++I)
        {
            if(StableWalk&&!WalkArmorPhase&&(I==1||I==2||I==4))continue;
            ReadyLayers[I]=StableWalk?DungeonFairytaleSwordWalkV001::GetTexture(PrimaryComponents[I],Record.Frame,Frames):Primary3ArmorPhase
                ?DungeonFairytaleSwordPrimary3V001::GetTexture(PrimaryComponents[I],Record.Frame,Frames,
                    BoundLightArmor&&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary3Preview")))
                :Primary2ArmorPhase
                ?DungeonFairytaleSwordPrimary2ArmorV001::GetTexture(PrimaryComponents[I],Record.Frame,Frames,
                    BoundLightArmor&&FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLeatherPrimary2Preview")))
                :PrimaryArmorPhase?GetFairytaleSwordArmorPrimary1Texture(PrimaryComponents[I],Record.Frame)
                :GetFairytaleSwordArmorReadyTexture(Components[I],Record.Frame);
            Record.ArmorReady=Record.ArmorReady && ReadyLayers[I] && ReadyLayers[I]->GetResource()
                && !ReadyLayers[I]->HasPendingRenderResourceInitialization();
        }
        // Fail visibly/structurally if a candidate is missing; never substitute
        // the old body, old armor or a different Ready phase.
        Record.TextureReady=Record.TextureReady && Record.ArmorReady;
    }
    // Validate the whole supported draw before emitting any body/armor quad.
    // A non-null resource can still be waiting for render initialization.
    UTexture2D* SwordTexture=DrawGear?GetCandidateSword():nullptr;
    if(DrawGear)
        Record.TextureReady=Record.TextureReady && SwordTexture && SwordTexture->GetResource()
            && !SwordTexture->HasPendingRenderResourceInitialization();

    // This branch owns player presentation even with missing textures or unsupported
    // states. Never fall through to the old human body, old armor or old sockets.
    bRenderedArmorLayersUsed=false;
    RenderedArmorLayerPaths.Reset();
    RenderedPlayerDrawStack.Reset();
    bRenderedWeaponBodyUsed=false;
    RenderedWeaponBodyFrame=-1;
    RenderedWeaponBodyFacing=0;
    RenderedWeaponBodyClip.Reset();
    RenderedWeaponBodyActionId=0;
    RenderedWeaponBodySampleTime=0.;
    RenderedWeaponBodyInstanceId=0;
    RenderedWeaponStateIndex=-1;
    RenderedWeaponBodyEmitScreen=FVector2D::ZeroVector; // SWD has no projectile emitter.
    RenderedPlayerTexturePath=Record.TexturePath;
    RenderedPlayerSpriteSize=float(CanvasSize);
    RenderedActorSpriteSizes.Add(F,float(CanvasSize));
    if(!Record.TextureReady || !Canvas)return true;

    Record.Root=Marker->Root;
    Record.Grip=Marker->Grip;
    const FVector2D GroundPoint=Ground(F->GetGroundPosition());
    const auto Project=[this,F,GroundPoint,Marker,&Record](const FVector2D& Pixel)
    {
        return Screen(float(GroundPoint.X+Record.Facing*(Pixel.X-Marker->Root.X)*CanvasSize/512.),
            float(GroundPoint.Y-double(F->JumpHeight)*.70+(Pixel.Y-Marker->Root.Y)*CanvasSize/512.));
    };
    Record.GripScreen=Project(Marker->Grip);
    const double DisplayRootX=Record.Facing<0?512.-Marker->Root.X:Marker->Root.X;
    const FVector2D Top=Screen(float(GroundPoint.X-CanvasSize*DisplayRootX/512.),
        float(GroundPoint.Y-double(F->JumpHeight)*.70-CanvasSize*Marker->Root.Y/512.));
    const float Width=float(CanvasSize)*UIScale;
    const FLinearColor Tint=F->HitFlash>0?FLinearColor(1.7f,.6f,.4f,1.f):FLinearColor::White;
    const float U=Record.Facing<0?1.f:0.f, DU=Record.Facing<0?-1.f:1.f;
    ++Record.DrawId;
    const auto DrawBodyLayer=[&](UTexture2D* Texture)
    {
        DrawTexture(Texture,Top.X,Top.Y,Width,Width,U,0.f,DU,1.f,Tint);
        Record.DrawStack.Add(Texture->GetPathName());
        RenderedPlayerDrawStack.Add(Texture->GetPathName());
        FActorQuad Quad;
        Quad.Owner=F;Quad.Texture=Texture;Quad.Top=Top;Quad.Size=Width;Quad.Tint=Tint;
        ActorQuads.Add(Quad);
    };
    if(StableWalk)
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
        for(int32 I=0;I<LayerCount-1;++I)DrawBodyLayer(ReadyLayers[I]);
        Record.ArmorDrawn=true;bRenderedArmorLayersUsed=true;
        for(int32 I : {1,2,4})RenderedArmorLayerPaths.Add(ReadyLayers[I]->GetPathName());
    }
    else DrawBodyLayer(Body);

    // Other unsupported poses stay a bare Ready0. Only a legitimate pending
    // pickup may retain committed gear while action-pose support remains false.
    if(!DrawGear)return true;
    // One uniform scale for the independent weapon across every supported phase.
    // Keep the actor/body/armor scale and combat range unchanged at this art trial.
    constexpr double WeaponScale=.50;
    const FVector2D ComponentGrip(99.,256.); // Existing independent WEAPON only.
    const double NativeAngle=FMath::RadiansToDegrees(FMath::Atan2(Marker->Axis.Y,Marker->Axis.X));
    Record.WeaponAngle=NativeAngle*(Record.Facing<0?-1.:1.);
    const float SwordWidth=float(CanvasSize*WeaponScale)*UIScale;
    Record.WeaponScale=WeaponScale;
    Record.WeaponWidth=SwordWidth;
    const FVector2D Pivot(Record.Facing<0?1.-ComponentGrip.X/512.:ComponentGrip.X/512.,ComponentGrip.Y/512.);
    const FVector2D SwordTop=Record.GripScreen-Pivot*SwordWidth;
    // Negative U is the single texture mirror. Reversing rotation is the same
    // reflected transform, not an additional image flip. Trial blade end follows
    // the original candidate Axis positive direction by root's explicit design.
    DrawTexture(SwordTexture,SwordTop.X,SwordTop.Y,SwordWidth,SwordWidth,U,0.f,DU,1.f,
        Tint,BLEND_Translucent,1.f,false,float(Record.WeaponAngle),Pivot);
    Record.WeaponPath=SwordTexture->GetPathName();
    Record.DrawStack.Add(Record.WeaponPath);
    RenderedPlayerDrawStack.Add(Record.WeaponPath);
    FActorQuad SwordQuad;
    SwordQuad.Owner=F;SwordQuad.Texture=SwordTexture;SwordQuad.Top=SwordTop;SwordQuad.Size=SwordWidth;
    SwordQuad.Rotation=float(Record.WeaponAngle);SwordQuad.Pivot=Pivot;SwordQuad.Tint=Tint;SwordQuad.Weapon=true;
    ActorQuads.Add(SwordQuad);

    // Replay only this new source's visible fist pixels. Original UVs plus the
    // reflected screen projection mirror the hand once; no old polygon/mask.
    if(StableWalk||ArmorPhase)DrawBodyLayer(ReadyLayers[LayerCount-1]);
    else
    {
        const auto& Polygon=Marker->FistPolygon;
        for(int32 I=1;I+1<Polygon.Num();++I)
        {
            FCanvasUVTri Tri;
            Tri.V0_Pos=Project(Polygon[0]);Tri.V1_Pos=Project(Polygon[I]);Tri.V2_Pos=Project(Polygon[I+1]);
            Tri.V0_UV=Polygon[0]/512.;Tri.V1_UV=Polygon[I]/512.;Tri.V2_UV=Polygon[I+1]/512.;
            Tri.V0_Color=Tri.V1_Color=Tri.V2_Color=Tint;
            FCanvasTriangleItem Item(Tri,Body->GetResource());
            Item.BlendMode=SE_BLEND_Translucent;
            Canvas->DrawItem(Item);
        }
        Record.DrawStack.Add(Record.TexturePath);
        RenderedPlayerDrawStack.Add(Record.TexturePath);
    }
    bRenderedWeaponBodyUsed=true;
    RenderedWeaponBodyClip=Record.Clip;
    RenderedWeaponBodyFrame=Record.Frame;
    RenderedWeaponBodyFacing=Record.Facing;
    RenderedWeaponBodyActionId=Record.ActionId;
    RenderedWeaponBodySampleTime=Record.SimulationTime;
    RenderedWeaponBodyInstanceId=Record.InstanceId;
    RenderedWeaponStateIndex=Record.Frame;
    return true;
}
