from pathlib import Path
import difflib,hashlib,json
R=Path('F:/Ourgame');O=R/'source-assets/production/stone-guard-room-warning-root-v001'
O.mkdir(parents=True,exist_ok=True)
replacements={
 'DungeonHUD.h':[
 ('    int32 GetRenderedTextDrawCalls() const { return RenderedTextDrawCalls; }',
  '    int32 GetRenderedTextDrawCalls() const { return RenderedTextDrawCalls; }\n    const TArray<FString>& GetRenderedGuardRoomWarningSlots() const { return RenderedGuardRoomWarningSlots; }'),
 ('    int32 RenderedTextDrawCalls = 0;', '    int32 RenderedTextDrawCalls = 0;\n    TArray<FString> RenderedGuardRoomWarningSlots;')],
 'DungeonHUD.cpp':[
 ('    RenderedTextDrawCalls=0;RenderedActorSpriteSizes.Reset();',
  '    RenderedTextDrawCalls=0;RenderedActorSpriteSizes.Reset();RenderedGuardRoomWarningSlots.Reset();'),
 ('    DrawWorldWeaponGround(Game);', '''    DrawWorldWeaponGround(Game);
    // World-space arrival warning reads the committed finite room plan only.
    // It never creates enemies, advances deadlines, changes fog or draws UI.
    FDungeonFirstBatchGuardRoomView Arrival;
    if(Game->QueryFirstBatchGuardRoom(Arrival))
    {
        const double Now=Game->GetSimulationTime();
        for(const auto& Slot:Arrival.Slots)
        {
            const double Age=Now-Slot.WarningAt;
            if(Slot.Stage!=EDungeonGuardRoomSlotStage::Warning || Slot.WarningAt<0. || Age<0. || Age>=1.2) continue;
            const float Visibility=float(GetCurrentVisibilityAt(Slot.SpawnPosition));
            const FVector2D P=Ground(Slot.SpawnPosition);
            if(Visibility<=.05f || P.X<20.f || P.X>1260.f || P.Y<24.f || P.Y>696.f) continue;
            const float T=float(Age/1.2),RX=26.f+7.f*T,RY=10.f+3.f*T;
            const float Pulse=.75f+.25f*FMath::Sin(float(Age)*20.f);
            const FLinearColor Amber(1.f,.61f,.16f,Visibility*(.45f+.35f*T)*Pulse);
            Oval(P.X-RX-2.f,P.Y-RY-1.f,2.f*RX+4.f,2.f*RY+2.f,FLinearColor(.08f,.07f,.05f,.35f*Visibility));
            for(int32 I=0;I<24;++I)
            {
                if(I%6==5) continue;
                const float A=2.f*PI*float(I)/24.f,B=2.f*PI*float(I+1)/24.f;
                Line(P.X+RX*FMath::Cos(A),P.Y+RY*FMath::Sin(A),P.X+RX*FMath::Cos(B),P.Y+RY*FMath::Sin(B),Amber,1.7f);
            }
            Line(P.X-9.f,P.Y+2.f,P.X-2.f,P.Y-4.f,Amber,1.5f);
            Line(P.X-2.f,P.Y-4.f,P.X+3.f,P.Y+2.f,Amber,1.5f);
            Line(P.X+3.f,P.Y+2.f,P.X+11.f,P.Y-1.f,Amber,1.5f);
            RenderedGuardRoomWarningSlots.Add(Slot.SlotId);
        }
    }''')]
}
patch=[];pins=[]
for name,pairs in replacements.items():
 src=R/'UnrealGame/Source/CodexDungeon'/name;before=src.read_text(encoding='utf-8-sig');after=before
 for old,new in pairs:
  assert after.count(old)==1,(name,old);after=after.replace(old,new)
 target=O/name;assert not target.exists();target.write_text(after,encoding='utf-8')
 rel=src.relative_to(R).as_posix();patch.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
 pins.append(dict(source=src.as_posix(),before_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),candidate=target.as_posix(),candidate_sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
dest=O/'world-warning.patch';assert not dest.exists();dest.write_text(''.join(patch),encoding='utf-8')
(O/'scope.json').write_text(json.dumps(dict(status='candidate_not_applied',files=pins,warning_seconds=1.2,only_readonly_room_warning_and_visible_world_geometry=True,no_gameplay_or_UI_change=True,runtime_verified=False),indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(candidate=str(O),files=2,actualSource_modified=False)))
