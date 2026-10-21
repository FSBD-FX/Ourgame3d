from pathlib import Path
import difflib,hashlib,json

ROOT=Path('F:/Ourgame');BASE=Path(__file__).resolve().parent;SRC=ROOT/'UnrealGame/Source/CodexDungeon'
STAGE=ROOT/'source-assets/production/fairytale-hero-air-v001/runtime-candidate-v001/stage0'
assert hashlib.sha256((STAGE/'HeroAir-Stage0-candidate-freeze-v001.json').read_bytes()).hexdigest()=='37513295d00ee57f1726260c0da10a296e378962cb1d4cbe21bb6e3010d42c2a'
INDEX=json.loads((STAGE/'stage0-admission-index-v001.json').read_text())['files']

QUERY=r'''bool ADungeonFighter::QueryHeroNonAttackAir(FDungeonHeroAirSample& Out) const
{
    // Observe completed actual owners only. Published Preparing/AwaitContinue
    // remains readable: neither this query nor a pose can open Continue.
    const auto* Game=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr;
    if(!IsInGameThread()||!IsValid(this)||IsActorBeingDestroyed()||!HasAuthority()||!Game||!Game->HasAuthority()
        ||Game->GetWorld()!=GetWorld()||Game->PlayerFighter!=this||bEnemy||StoneKnight||StoneBat||StoneGuard||bDead
        ||Game->bWaitingForStart||Game->bGameOver||Game->bRunTickActive||Game->bSimulationBatch||Game->bSimulatingMotion
        ||!Game->PendingDamage.IsEmpty()||bResolvingContentWindow||bSuppressOrdinaryMovement
        ||bGroundMotionFrameOpen||bUnconsumedGroundMotion||PendingWalkDistance!=0.
        ||!RootComponent||RootComponent->GetAttachParent())return false;
    const auto Transform=GetActorTransform();
    if(Transform.ContainsNaN()||Transform.GetTranslation().Z!=0.||Transform.GetRotation()!=FQuat::Identity
        ||Transform.GetScale3D()!=FVector::OneVector)return false;
    const auto& V=Game->GetEquipmentView();const auto& W=Game->GetWeaponWorldState();
    const uint64 Id=Game->FindWorldEntityId(this);const double Now=Game->GetSimulationTime();const auto Position=GetGroundPosition();
    if(!V.Bound||!V.RunGuid.IsValid()||!V.OwnerId||!V.RoomInstanceId||!Id||Id!=V.OwnerId||Id!=GetRuntimeEntityId()
        ||Game->FindWorldFighter(Id)!=this||W.RunGuid!=V.RunGuid||W.RoomInstanceId!=V.RoomInstanceId
        ||W.Time!=Now||!FMath::IsFinite(Now)||Now<0.||!FMath::IsFinite(Position.X)||!FMath::IsFinite(Position.Y))return false;
    int32 Bindings=0;
    for(const auto& B:W.ActorBindings)if(B.EntityId==Id)
    {
        // Stable player identity retains its birth room across real transfers.
        if(!B.RoomInstanceId||B.RoomInstanceId>V.RoomInstanceId||B.ContentId!=TEXT("player"))return false;
        ++Bindings;
    }
    if(Bindings!=1||!FMath::IsFinite(Health)||Health<=0.f||!FMath::IsFinite(MaxHealth)||MaxHealth<=0.f||Health>MaxHealth
        ||!FMath::IsFinite(JumpHeight)||JumpHeight<0.f||!FMath::IsFinite(JumpVelocity)
        ||!FMath::IsFinite(LandingVisualAge)||LandingVisualAge<0.f||LandingVisualAge>.12f
        ||(Facing!=-1.f&&Facing!=1.f)||!FMath::IsFinite(HurtTime)||HurtTime>0.f||HurtTime<0.f
        ||!FMath::IsFinite(AttackTime)||AttackTime>0.f||AttackTime<0.f||!FMath::IsFinite(ArmorChangeRemaining)
        ||ArmorChangeRemaining!=0.f||V.Action.Active||GetEquipmentActionDeadline()>0.)return false;
    const auto& M=Combat.State();const auto& A=WeaponSkills.State();const auto& D=Dodge.State();
    if(M.Time!=Now||A.Time!=Now||D.Time!=Now||D.OwnerId!=Id||M.Dead||A.Budget.Dead
        ||M.Action.Active||A.Action.Active||D.Phase!=DungeonDodge::EPhase::Idle
        ||M.Grounded!=A.Budget.Grounded||M.WeaponInstanceId!=A.EquippedId
        ||!NativeOwnerPositionProjection(Position,D.Position.X,D.Position.Y))return false;
    // A positive native descending height must not become a premature landing:
    // bound WA deliberately retains its airborne budget until the actual endpoint.
    // Existing validated saves also allow their KINDA_SMALL_NUMBER projection.
    if(A.Budget.Grounded&&(JumpHeight>KINDA_SMALL_NUMBER||JumpVelocity>0.f))return false;
    if(JumpHeight==0.f&&JumpVelocity==0.f&&!A.Budget.Grounded)return false;
    const bool Air=JumpHeight>0.f||JumpVelocity>0.f;
    const bool Landing=JumpHeight==0.f&&JumpVelocity==0.f&&LandingVisualAge<.12f;
    if(!Air&&!Landing)return false;
    FDungeonHeroAirSample Candidate;Candidate.Valid=true;Candidate.RunGuid=V.RunGuid;Candidate.OwnerId=Id;
    Candidate.RoomInstanceId=V.RoomInstanceId;Candidate.PresentationEpoch=Game->GetRunPresentationEpoch(); // Initial epoch0 is legal.
    Candidate.NativeTime=Now;Candidate.GroundPosition=Position;Candidate.Facing=Facing;
    Candidate.JumpHeight=JumpHeight;Candidate.VerticalVelocity=JumpVelocity;Candidate.LandingVisualAge=LandingVisualAge;
    Out=MoveTemp(Candidate);return true;
}'''

SELECT=r'''bool Select(const FDungeonHeroAirSample& Q,FSelection& Out,FString& Diagnostic)
{
 if(!Q.Valid||!Q.RunGuid.IsValid()||!Q.OwnerId||!Q.RoomInstanceId||!FMath::IsFinite(Q.NativeTime)||Q.NativeTime<0.
  ||!FMath::IsFinite(Q.GroundPosition.X)||!FMath::IsFinite(Q.GroundPosition.Y)||(Q.Facing!=-1.f&&Q.Facing!=1.f)
  ||!FMath::IsFinite(Q.JumpHeight)||Q.JumpHeight<0.f||!FMath::IsFinite(Q.VerticalVelocity)
  ||!FMath::IsFinite(Q.LandingVisualAge)||Q.LandingVisualAge<0.f||Q.LandingVisualAge>.12f)
 {Diagnostic=TEXT("Nonattack Air requires complete finite actual-owner sample facts");return false;}
 FSelection Candidate;
 if(Q.JumpHeight>0.f||Q.VerticalVelocity>0.f)
 {
  Candidate.Frame=Q.VerticalVelocity>315.f?0:Q.VerticalVelocity>90.f?1:Q.VerticalVelocity>=-90.f?2:3;
 }
 else if(Q.JumpHeight==0.f&&Q.VerticalVelocity==0.f&&Q.LandingVisualAge<.12f)
  Candidate.Frame=Q.LandingVisualAge<.06f?4:5;
 else{Diagnostic=TEXT("Actual owner is outside nonattack Air and original landing window");return false;}
 Candidate.Valid=true;Candidate.Pose=static_cast<EPose>(Candidate.Frame+1);Out=Candidate;Diagnostic.Reset();return true;
}'''

edits={
'DungeonFighter.cpp':('''bool ADungeonFighter::QueryHeroNonAttackAir(FDungeonHeroAirSample&) const
{
    // Stage0 semantic RED seam: leave Out untouched; do not infer from idle/Ready.
    return false;
}''',QUERY),
'DungeonFairytaleSwordAirV001.cpp':('''bool Select(const FDungeonHeroAirSample&,FSelection&,FString& Diagnostic)
{Diagnostic=TEXT("Stage0: real nonattack Air selection is not implemented");return false;}''',SELECT)}
rows=[]
for name,(old,new) in edits.items():
    source=SRC/name;data=source.read_bytes();ref=next(x for x in INDEX if Path(x['actual']).name==name);assert data==(STAGE/ref['candidate']).read_bytes()
    nl=b'\r\n' if b'\r\n' in data else b'\n';a=old.encode().replace(b'\n',nl);b=new.encode().replace(b'\n',nl);assert data.count(a)==1
    result=data.replace(a,b,1);target=BASE/'existing-source'/name;target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();target.write_bytes(result)
    (BASE/(name+'.patch')).write_text(''.join(difflib.unified_diff(data.decode('utf-8-sig').splitlines(True),result.decode('utf-8-sig').splitlines(True),fromfile='a/UnrealGame/Source/CodexDungeon/'+name,tofile='b/UnrealGame/Source/CodexDungeon/'+name)),encoding='utf-8',newline='')
    rows.append({'actual':'UnrealGame/Source/CodexDungeon/'+name,'before_bytes':len(data),'before_sha256':hashlib.sha256(data).hexdigest(),'candidate':target.relative_to(BASE).as_posix(),'after_bytes':len(result),'after_sha256':hashlib.sha256(result).hexdigest()})
(BASE/'before-after-pins-v001.json').write_text(json.dumps({'schema':'HeroAir-production-query-select-preparation-pins-v001','stage0_source_freeze_sha256':'37513295d00ee57f1726260c0da10a296e378962cb1d4cbe21bb6e3010d42c2a','source_profile_pending':True,'atomic_plan_and_presenter_pending':True,'actual_source_written':False,'native_semantic_red_confirmation_pending':True,'files':rows},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'query_select_candidates':len(rows),'actual_source_written':False,'plan_presenter_profile_pending':True}))
