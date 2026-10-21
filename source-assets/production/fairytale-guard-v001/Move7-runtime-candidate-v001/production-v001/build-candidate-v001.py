"""Construct typed data and narrow source patches inside this candidate only.

The rig solver and HUD presentation are separately authored source files. This
one-shot preparation script does not compile UE and refuses existing outputs.
"""
from pathlib import Path
import hashlib, json, difflib

C = Path(__file__).resolve().parent
PROFILE = Path('F:/Ourgame/source-assets/production/fairytale-guard-v001/move-leg-rig-generation-v001/Move7-profile-preparation-v001/GuardMove7-runtime-profile-candidate-v001.json')
PROFILE_SHA = '03156e971171f597ca504e9c0176d5a2fdf3c31c09b3eddae2995e2245193b51'
APPROVAL_REL = 'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/root-runtime-trial-approval-v001/Root-limited-runtime-trial-approval-v001.json'
APPROVAL = Path('F:/Ourgame')/APPROVAL_REL
APPROVAL_SHA = 'd78bcbca8cd47caa781ee9a1bdcc1c25c5f9a3036be5d72dc2a2dcceb57feb9e'
def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return p.read_bytes().decode('utf-8-sig').replace('\r\n','\n')
def write(p, s):
    assert not p.exists(), str(p)
    p.write_bytes(s.replace('\r\n','\n').encode('utf-8'))
def patch_file(name, substitutions):
    before = read(C/'before'/name)
    after = before
    for old, new in substitutions:
        assert after.count(old)==1, (name, old[:100], after.count(old))
        after = after.replace(old,new)
    target=C/'changed-source'/name
    assert not target.exists()
    line_end='\r\n' if b'\r\n' in (C/'before'/name).read_bytes() else '\n'
    target.write_bytes(after.replace('\n',line_end).encode('utf-8'))
    diff=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),
      fromfile='a/UnrealGame/Source/CodexDungeon/'+name,tofile='b/UnrealGame/Source/CodexDungeon/'+name))
    write(C/'patches'/(name+'.patch'),diff)

assert sha(PROFILE.read_bytes())==PROFILE_SHA
assert sha(APPROVAL.read_bytes())==APPROVAL_SHA
approval=json.loads(read(APPROVAL))
assert approval['RootApproved'] and approval['RuntimeTrialAllowed'] and approval['TrialAllowed'] and not approval['FinalAccepted']
p=json.loads(read(PROFILE))
names=['BodyRest','NearThigh','NearShin','NearFoot','FarThigh','FarShin','FarFoot']
parts={r['part']:names[i] for i,r in enumerate(p['source7'])}
data=['// Exact frozen artist surface registrations. These are not anatomical bones.\n',
 'namespace DungeonFairytaleGuardMoveRigV001\n{\nnamespace\n{\nFProfile MakeMoveProfile()\n{\n FProfile P;\n',
 f' P.ProfileId=TEXT("{p["profile_id"]}");\n P.ProfileSHA256=TEXT("{PROFILE_SHA}");\n',
 f' P.SourceSnapshotSHA256=TEXT("{p["source_snapshot_sha256"]}");\n',
 f' P.RegistrationEvidenceSHA256=TEXT("{APPROVAL_SHA}");\n',
 f' P.TrialApprovalRecord=TEXT("{APPROVAL_REL}");\n',
 ' P.SourceClosureVerified=true;P.TrialAllowed=true;P.FinalAccepted=false;\n']
for i,r in enumerate(p['source7']):
 data.extend([' {FSourcePart S;\n',f'  S.Component=EComponent::{names[i]};\n',
 f'  S.TexturePath=TEXT("{r["texture_object_path"]}");\n',
 f'  S.SourceSHA256=TEXT("{r["source"]["sha256"]}");\n',
 f'  S.SourceRGBASHA256=TEXT("{r["RGBA_sha256"]}");\n',
 f'  S.NativeBatchId={r["source_native_batch_id"]};S.ComponentToRestScale={r["component_to_rest_scale"]};\n'])
 for name,m in r['artist_surface_markers'].items():
  x,y=m['xy'];rgba=','.join(map(str,m['actual_RGBA']))
  data.append(f'  S.Markers.Add({{TEXT("{name}"),FVector2D({x}.,{y}.),FColor({rgba})}});\n')
 data.append('  P.Sources.Add(MoveTemp(S));}\n')
data.append(' P.LayerOrder={'+','.join('EComponent::'+parts[x] for x in p['layer_order'])+'};\n return P;\n}\n}\n}\n')
write(C/'new-source'/'DungeonFairytaleGuardMoveRigDataV001.inl',''.join(data))

query='''bool ADungeonFighter::QueryCompletedGuardMove(FDungeonGuardMoveSample& Out) const
{
    // This is a completed native-owner read. No AI step, sweep, clock, cache,
    // event insertion, feedback consumption, persistence or movement occurs.
    namespace G=DungeonStoneGuard;namespace F=DungeonFairytaleGuardFullV003;
    const auto* Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    if(!IsInGameThread()||!Game||!StoneGuard||StoneKnight||StoneBat||!bEnemy||bDead
        ||Game->PlayerFighter==this||Game->bWaitingForStart||Game->bGameOver||Game->IsRunInstallGated()
        ||Game->bRunTickActive||Game->bSimulationBatch||Game->bSimulatingMotion||!Game->PendingDamage.IsEmpty()
        ||bResolvingContentWindow||bSuppressOrdinaryMovement||!RootComponent||RootComponent->GetAttachParent()
        ||EnemyContentId!=TEXT("ENM-STN-003")||!bHasAxe||WeaponId!=TEXT("enemy_stone_guard_twohand_axe")||!ArmorId.IsEmpty()
        ||JumpHeight!=0.f||JumpVelocity!=0.f)return false;
    const auto Transform=GetActorTransform();
    if(Transform.ContainsNaN()||Transform.GetTranslation().Z!=0.||Transform.GetRotation()!=FQuat::Identity
        ||Transform.GetScale3D()!=FVector::OneVector)return false;
    const auto& V=Game->GetEquipmentView();const auto& W=Game->GetWeaponWorldState();
    const uint64 Id=Game->FindWorldEntityId(this);const double Now=Game->GetSimulationTime();
    if(!V.Bound||!V.RunGuid.IsValid()||!V.RoomInstanceId||!Id||Id==V.OwnerId||Id!=GetRuntimeEntityId()
        ||Game->FindWorldFighter(Id)!=this||!Game->Enemies.Contains(this)
        ||W.RunGuid!=V.RunGuid||W.RoomInstanceId!=V.RoomInstanceId||W.Time!=Now||!FMath::IsFinite(Now)||Now<0.)return false;
    int32 Bindings=0;
    for(const auto& B:W.ActorBindings)if(B.EntityId==Id)
    {if(B.RoomInstanceId!=V.RoomInstanceId||B.ContentId!=EnemyContentId)return false;++Bindings;}
    if(Bindings!=1)return false;
    const auto& S=StoneGuard->State();const auto Position=GetGroundPosition();
    if(S.EntityId!=Id||!FMath::IsFinite(S.InitialTime)||S.InitialTime<0.||S.Time!=Now||S.Time<S.InitialTime
        ||LastGuardSyncTime!=S.Time||S.Phase!=G::EPhase::Idle||S.Action.InProgress
        ||!FMath::IsFinite(S.HP)||S.HP<=0.||!FMath::IsFinite(Health)||Health!=float(S.HP)
        ||MaxHealth!=float(G::FGuardKernel::Definition().HP)||S.Position.Z!=0.
        ||!FMath::IsFinite(S.Position.X)||!FMath::IsFinite(S.Position.Y)
        ||!FMath::IsFinite(Position.X)||!FMath::IsFinite(Position.Y)
        ||!NativeOwnerPositionProjection(Position,S.Position.X,S.Position.Y)
        ||(S.Facing!=1&&S.Facing!=-1)||Facing!=float(S.Facing))return false;
    const G::FEvent* Current=nullptr;double Total=0.,CurrentDistance=0.;
    for(const auto& E:S.Issued)
    {
        if(!E.EventId||E.EventId>=S.NextEventId||E.EntityId!=Id||!FMath::IsFinite(E.AtTime)
            ||E.AtTime<S.InitialTime||E.AtTime>S.Time)return false;
        if(E.Kind!=G::EEventKind::Movement)continue;
        for(double N:{E.From.X,E.From.Y,E.From.Z,E.To.X,E.To.Y,E.To.Z})if(!FMath::IsFinite(N))return false;
        if(E.From.Z!=0.||E.To.Z!=0.)return false;
        const double Length=std::hypot(E.To.X-E.From.X,E.To.Y-E.From.Y);
        if(!FMath::IsFinite(Length)||Length<0.)return false;
        Total+=Length;if(!FMath::IsFinite(Total))return false;
        if(E.AtTime==S.Time&&Length>0.){Current=&E;CurrentDistance=Length;}
    }
    if(!Current||Current->To.X!=S.Position.X||Current->To.Y!=S.Position.Y)return false;
    const auto Selection=F::SelectFull(S);
    if(!Selection.Valid||Selection.Clip!=F::EClip::Move||Selection.Phase!=G::EPhase::Idle
        ||Selection.EntityId!=Id||Selection.Facing!=S.Facing||Selection.SampleTime!=Now
        ||Selection.SourceEventId!=Current->EventId||Selection.AcceptedDistance!=Total)return false;
    FDungeonGuardMoveSample Candidate;
    Candidate.Valid=true;Candidate.BlockKnown=false; // Original Movement has no historical sweep stop/fraction.
    Candidate.EntityId=Candidate.AcceptedPathOwnerId=Id;Candidate.RunGuid=V.RunGuid;
    Candidate.RoomInstanceId=V.RoomInstanceId;Candidate.PresentationEpoch=Game->GetRunPresentationEpoch();
    Candidate.EnemyContentId=EnemyContentId;Candidate.SampleTime=S.Time;Candidate.MovementAtTime=Current->AtTime;
    Candidate.MovementEventId=Current->EventId;Candidate.AcceptedDistance=Total;Candidate.CurrentAcceptedDistance=CurrentDistance;
    Candidate.GroundPosition=Position;Candidate.MovementFrom={Current->From.X,Current->From.Y};Candidate.MovementTo={Current->To.X,Current->To.Y};
    Candidate.MovementDirection=(Candidate.MovementTo-Candidate.MovementFrom)/CurrentDistance;
    Candidate.Facing=S.Facing;Candidate.NativeSelection=Selection;
    Out=MoveTemp(Candidate);return true;
}'''
patch_file('DungeonFighter.cpp', [('''bool ADungeonFighter::QueryCompletedGuardMove(FDungeonGuardMoveSample& Out) const
{
    (void)Out; // Stage0 semantic RED: no fabricated witness or caller mutation.
    return false;
}''',query)])
patch_file('DungeonHUD.h', [('    bool bUseFairytaleGuardMoveRigPreview=false;',
'''    bool bUseFairytaleGuardMoveRigPreview=false;
    void LoadFairytaleGuardMoveRigTrial();
    bool DrawFairytaleGuardMoveRigBody(ADungeonFighter* Fighter);''')])
patch_file('DungeonHUD.cpp', [
 ('    LoadFairytaleGuardFullTrial();\n    FlushRenderingCommands();',
  '    LoadFairytaleGuardFullTrial();\n    LoadFairytaleGuardMoveRigTrial();\n    FlushRenderingCommands();'),
 ('        if(bUseFairytaleGuardFullPreview)\n        {if(DrawFairytaleGuardFullBody(F))return;}',
  '        if(bUseFairytaleGuardMoveRigPreview&&DrawFairytaleGuardMoveRigBody(F))return;\n        if(bUseFairytaleGuardFullPreview)\n        {if(DrawFairytaleGuardFullBody(F))return;}'),
 ('void ADungeonHUD::DrawHUD()\n{\n    Super::DrawHUD(); if(!Canvas) return;',
  'void ADungeonHUD::DrawHUD()\n{\n    FairytaleGuardMoveRigDraws.Reset(); // Every callback, including no-Canvas and early lookdev paths.\n    Super::DrawHUD(); if(!Canvas) return;'),
 ('    ActionAudioPlayRequests.Reset();ActionAudioPlayReceipts.Reset();MeleeTrails.Reset();ActorQuads.Reset();',
  '    ActionAudioPlayRequests.Reset();ActionAudioPlayReceipts.Reset();MeleeTrails.Reset();ActorQuads.Reset();FairytaleGuardMoveRigDraws.Reset();')])
patch_file('DungeonFairytaleGuardFullPresentationV003.cpp', [
 (' bUseFairytaleGuardStompPreview=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleGuardStompPreview"));',
  ' bUseFairytaleGuardStompPreview=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleGuardStompPreview"))||FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleGuardMoveRigPreview"));')])
print(json.dumps({'candidate':C.as_posix(),'status':'candidate-only; native compile/draw pending','actual_source_written':False}))
