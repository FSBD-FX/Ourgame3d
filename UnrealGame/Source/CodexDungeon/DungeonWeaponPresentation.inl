// Presentation reads authoritative world facts. No damage, timing, projectile
// creation or inventory mutation is permitted here. Native weapon/body art is
// still a separate content requirement; these are procedural feedback candidates.
void ADungeonHUD::UpdateWorldWeaponFeedback(ADungeonGameMode* Game)
{
    if(!Game||Game->IsRunInstallGated())return;
    const auto& World=Game->GetWeaponWorldState();
    if(WorldWeaponRun!=World.RunGuid)
    {WorldWeaponRun=World.RunGuid;WorldWeaponCursor=0;WorldWeaponEffects.Reset();WorldWeaponAudioRequests.Reset();}
    const double Now=Game->GetSimulationTime();
    WorldWeaponEffects.RemoveAll([Now](const FDungeonWorldWeaponEvent& E){return Now-E.AtTime>.45;});
    for(const auto& Event:World.Events)
    {
        if(Event.Sequence<=WorldWeaponCursor) continue;
        WorldWeaponCursor=Event.Sequence;
        const double Age=Now-Event.AtTime;
        if(Age<0 || Age>.25 || Event.Key.RoomInstanceId!=World.RoomInstanceId) continue;
        FString Cue;
        if(Event.Kind==EDungeonWorldWeaponEventKind::ProjectileEmitted)
            Cue=Event.Magic?TEXT("FIRE_LAUNCH_01"):TEXT("XBW_RELEASE_01");
        else if(Event.Kind==EDungeonWorldWeaponEventKind::WindowCreated && Event.Magic)
            Cue=TEXT("FIRE_LAUNCH_01");
        else if(Event.Kind==EDungeonWorldWeaponEventKind::BurnTickCommitted && Event.ActualHPLoss>0)
            Cue=TEXT("FIRE_BURN_SHORT_01");
        if(!Cue.IsEmpty())
            if(const auto Sound=WorldWeaponSounds.Find(Cue))
            {
                UGameplayStatics::PlaySound2D(this,Sound->Get(),Cue==TEXT("FIRE_BURN_SHORT_01")?.12f:.23f);
                ++WorldWeaponAudioRequests.FindOrAdd(Cue);
            }
        if(Event.Kind==EDungeonWorldWeaponEventKind::DirectHitCommitted
            || Event.Kind==EDungeonWorldWeaponEventKind::ProjectileStopped
            || Event.Kind==EDungeonWorldWeaponEventKind::BurnTickCommitted)
            WorldWeaponEffects.Add(Event);
    }
    if(WorldWeaponEffects.Num()>128) WorldWeaponEffects.RemoveAt(0,WorldWeaponEffects.Num()-128,EAllowShrinking::No);
}

void ADungeonHUD::DrawWorldWeaponProjectile(const FDungeonWorldProjectile& P,double Now)
{
        // The caller admits only this room's active entries into the shared depth list.
        if(!P.Active || GetCurrentVisibilityAt(P.Position)<=.05) return;
        const auto Point=Ground(P.Position);
        const double PresentationHeight=P.HasPoseSocket?P.PoseSocket.PresentationOrigin.Height:P.Source.Origin.Height;
        const float Y=float(Point.Y-PresentationHeight*.70);
        const float Facing=float(P.Source.Action.Facing);
        const bool Fire=P.Source.Action.Weapon==DungeonContentCombat::EWeapon::STF001;
        if(Fire)
        {
            const float Pulse=1.f+.12f*FMath::Sin(float(Now-P.Source.AtTime)*34.f);
            Oval(Point.X-10*Pulse,Y-8*Pulse,20*Pulse,16*Pulse,FLinearColor(1,.24f,.035f,.22f));
            Oval(Point.X-5,Y-4,10,8,FLinearColor(1,.58f,.12f,.9f));
            Oval(Point.X-2,Y-2,4,4,FLinearColor(1,.94f,.55f,1));
            for(int32 I=1;I<=3;++I)
                Line(Point.X-Facing*(7+I*6),Y+FMath::Sin(float(Now)*18.f+I)*2,
                    Point.X-Facing*(12+I*6),Y,FLinearColor(1,.35f,.05f,.38f/I),2.f);
        }
        else
        {
            Line(Point.X-Facing*12,Y,Point.X+Facing*5,Y,FLinearColor(.18f,.11f,.055f,1),3.f);
            Line(Point.X-Facing*10,Y,Point.X+Facing*5,Y,FLinearColor(.87f,.78f,.58f,1),1.5f);
            Triangle({Point.X+Facing*7,Y},{Point.X+Facing*2,Y-2},{Point.X+Facing*2,Y+2},DungeonPalette::Cream);
            Line(Point.X-Facing*9,Y-2,Point.X-Facing*6,Y+2,DungeonPalette::Gold,1.3f);
        }
}

void ADungeonHUD::DrawWorldWeaponGround(ADungeonGameMode* Game)
{
    const auto& World=Game->GetWeaponWorldState();
    const double Now=Game->GetSimulationTime();
    for(const auto& W:World.Windows)
    {
        if(!W.Active || W.Key.RoomInstanceId!=World.RoomInstanceId
            || W.Source.Action.Weapon!=DungeonContentCombat::EWeapon::STF001
            || Now<W.Source.AtTime || Now>=W.Source.WindowEnd) continue;
        const int32 Count=FMath::Clamp(FMath::CeilToInt(W.Source.Range/16.),1,28);
        for(int32 I=0;I<=Count;++I)
        {
            const FVector2D XY(W.Source.Origin.X+W.Source.Action.Facing*W.Source.Range*I/Count,W.Source.Origin.Y);
            const float Visibility=float(GetCurrentVisibilityAt(XY));if(Visibility<=.05f) continue;
            const auto Point=Ground(XY);const float Age=float(Now-W.Source.AtTime);
            const float Height=10.f+4.f*FMath::Sin(Age*35+I*1.7f);
            Oval(Point.X-7,Point.Y-W.Source.Depth*.38f,14,W.Source.Depth*.76f,FLinearColor(1,.25f,.03f,.12f*Visibility));
            Triangle({Point.X-4,Point.Y},{Point.X+4,Point.Y},{Point.X+FMath::Sin(Age*21+I)*2,Point.Y-Height},FLinearColor(1,.43f,.08f,.8f*Visibility));
            Triangle({Point.X-2,Point.Y},{Point.X+2,Point.Y},{Point.X,Point.Y-Height*.65f},FLinearColor(1,.88f,.36f,.9f*Visibility));
        }
    }
}

void ADungeonHUD::DrawWorldWeaponFeedback(ADungeonGameMode* Game)
{
    const auto& World=Game->GetWeaponWorldState();
    const double Now=Game->GetSimulationTime();
    const auto FindActor=[Game](uint64 Id)->ADungeonFighter*
    {
        if(auto Player=Game->GetPlayerFighter()) if(Player->GetRuntimeEntityId()==Id) return Player;
        for(auto Enemy:Game->Enemies) if(Enemy && Enemy->GetRuntimeEntityId()==Id) return Enemy;
        return nullptr;
    };
    for(const auto& B:World.Burns)
    {
        if(!B.Active) continue;
        auto Target=FindActor(B.TargetId);if(!Target || Target->bDead) continue;
        const auto XY=Target->GetGroundPosition();const float Visibility=float(GetCurrentVisibilityAt(XY));
        if(Visibility<=.05f) continue;
        const auto Point=Ground(XY);const float Y=Point.Y-Target->JumpHeight*.70f;
        for(int32 I=0;I<4;++I)
        {
            const float Phase=FMath::Frac(float(Now-B.AppliedAt)*1.9f+I*.25f);
            const float X=Point.X+(I-1.5f)*6.f;
            Oval(X-2,Y-8-Phase*22.f,4,5,FLinearColor(1,.48f,.09f,(1-Phase)*.7f*Visibility));
        }
    }
    for(const auto& Event:WorldWeaponEffects)
    {
        if(Event.Key.RoomInstanceId!=World.RoomInstanceId || GetCurrentVisibilityAt(Event.Position)<=.05) continue;
        const float Age=float(Now-Event.AtTime);if(Age<0 || Age>.24f) continue;
        const auto Point=Ground(Event.Position);
        const double PresentationHeight=Event.HasPoseSocket?Event.PoseSocket.PresentationOrigin.Height:Event.Height;
        const float Y=float(Point.Y-PresentationHeight*.70);
        const FLinearColor C=Event.Magic?FLinearColor(1,.55f,.13f,1-Age/.24f):FLinearColor(1,.9f,.6f,1-Age/.24f);
        for(int32 I=0;I<5;++I)
        {
            const float A=I*2*PI/5.f+float(Event.Sequence%7),R=2+Age*45;
            Line(Point.X+FMath::Cos(A)*R,Y+FMath::Sin(A)*R,
                Point.X+FMath::Cos(A)*(R+4),Y+FMath::Sin(A)*(R+4),C,1.5f);
        }
    }
}
