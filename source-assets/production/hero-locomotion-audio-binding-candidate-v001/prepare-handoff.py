"""Candidate-only exact seams/manifest. Never applies to actual Source/Content."""
from pathlib import Path
import difflib, hashlib, json
ROOT=Path('F:/Ourgame'); HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'UnrealGame/Source/CodexDungeon'
PIN=ROOT/'source-assets/production/backups/v144-HeroAirDiskRestore300-203GREEN-v001/compiled-source-manifest.json'
PIN_SHA='fb225bef1e9b2e3584a16d3eff192bd39587867b68c0fcdb525a4d876324e59a'
ASSETS=ROOT/'source-assets/production/hero-locomotion-audio-candidate-v001'
FREEZE=ASSETS/'HeroLocomotionAudio-Candidate-freeze-v001.json'
FREEZE_SHA='cf63ec47a15855f17703f72540471d8cba2a7a952a26bfc7bc03acd0b2f216ac'
sha=lambda b:hashlib.sha256(b).hexdigest()
def write(rel,obj):
 p=HERE/rel
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
assert sha(PIN.read_bytes())==PIN_SHA
assert sha(FREEZE.read_bytes())==FREEZE_SHA
ops={}
def replace(file,before,after):ops.setdefault(file,[]).append({'before':before,'after':after})
replace('DungeonGameMode.h','#include "DungeonActionAudioFeedback.h"','#include "DungeonActionAudioFeedback.h"\n#include "DungeonHeroLocomotionAudioNativeV001.h"')
replace('DungeonGameMode.h','\nclass ADungeonFighter;\n','\nclass ADungeonFighter;\nclass USoundBase;\nclass USoundConcurrency;\n')
replace('DungeonGameMode.h','    bool IsFairytaleLookdevPreview() const { return bFairytaleLookdevPreview; }','    const TArray<FDungeonHeroLocomotionAudioPlayRequestV001>& GetHeroLocomotionAudioPlayRequestsV001() const { return HeroLocomotionPlayRequests; }\n    bool IsFairytaleLookdevPreview() const { return bFairytaleLookdevPreview; }')
members='''    // New transient named-event prototype adapter; never part of Schema1.
    DungeonHeroLocomotionAudioV001::FState HeroLocomotionState;
    DungeonHeroLocomotionAudioV001::FScope HeroLocomotionAttachedScope;
    TWeakObjectPtr<ADungeonFighter> HeroLocomotionOwner;
    FGuid HeroLocomotionRun;
    bool bHeroLocomotionSoundsLoaded=false;
    UPROPERTY() TArray<TObjectPtr<USoundBase>> HeroLocomotionSounds;
    UPROPERTY() TObjectPtr<USoundConcurrency> HeroLocomotionConcurrency;
    TArray<FDungeonHeroLocomotionAudioPlayRequestV001> HeroLocomotionPlayRequests;
    void LoadHeroLocomotionAudioV001();
    DungeonHeroLocomotionAudioV001::FScope HeroLocomotionScopeV001() const;
    bool HeroLocomotionAudioActiveV001() const;
    bool RefreshHeroLocomotionAudioV001();
    void ObserveHeroGroundDistanceV001(ADungeonFighter* Fighter,double From,double To,double Distance,
        bool Grounded,bool OrdinaryEligible,bool HadIntent);
    void ObserveHeroTakeoffV001(ADungeonFighter* Fighter,double AtTime);
    void ObserveHeroAirMotionV001(ADungeonFighter* Fighter,double From,double To,double FromHeight,double ToHeight,double FallingSpeed);
    void ObserveHeroDodgeV001(ADungeonFighter* Fighter,const std::vector<DungeonDodge::FEvent>& Events);
    void DispatchHeroLocomotionAudioV001();
'''
replace('DungeonGameMode.h','    FDungeonActionAudioState ActionAudioState;',members+'    FDungeonActionAudioState ActionAudioState;')
replace('DungeonGameMode.cpp','    Super::StartPlay();','    Super::StartPlay();\n    LoadHeroLocomotionAudioV001();')
replace('DungeonGameMode.cpp','    SeedActionAudioWeapon(PlayerFighter);\n    return true;','    SeedActionAudioWeapon(PlayerFighter);\n    RefreshHeroLocomotionAudioV001(); // Silent initialized owner/tail.\n    return true;')
replace('DungeonGameMode.cpp','    SuppressRestoreContinueEnter=true;++RunPresentationEpoch;','    SuppressRestoreContinueEnter=true;++RunPresentationEpoch;\n    RefreshHeroLocomotionAudioV001(); // Silent installed H/V and actual Dodge tail; no queued audio restore.')
replace('DungeonGameMode.cpp','    PlayerFighter->ResetFighter(FVector2D(-460.f, 0.f));','    PlayerFighter->ResetFighter(FVector2D(-460.f, 0.f));\n    RefreshHeroLocomotionAudioV001(); // Silent genuine legacy new run.')
replace('DungeonGameMode.cpp','    Super::Tick(DeltaSeconds);\n    if(IsRunInstallGated())','    Super::Tick(DeltaSeconds);\n    RefreshHeroLocomotionAudioV001(); // Scope/room attachment precedes any real input.\n    if(!HeroLocomotionAudioActiveV001())DispatchHeroLocomotionAudioV001(); // Drain while gated/waiting/terminal.\n    if(IsRunInstallGated())')
replace('DungeonGameMode.cpp','            Fighter->bSuppressOrdinaryMovement=true;Fighter->SimulateMotion(Step,false);Fighter->bSuppressOrdinaryMovement=false;','            const double AudioFallingSpeed=FMath::Max(0.,1800.*double(Step)-double(Fighter->JumpVelocity));\n            Fighter->bSuppressOrdinaryMovement=true;Fighter->SimulateMotion(Step,false);Fighter->bSuppressOrdinaryMovement=false;')
replace('DungeonGameMode.cpp','                const auto Actual=Fighter->GetGroundPosition();\n                Fighter->bMoving=Actual!=P.Start;','                // Authoritative resolved H crossing; legacy audio is suppressed in this batch.\n                if(!Fighter->bDead)ObserveHeroAirMotionV001(Fighter,FromTime,ToTime,P.StartHeight,P.EndHeight,AudioFallingSpeed);\n                const auto Actual=Fighter->GetGroundPosition();\n                Fighter->bMoving=Actual!=P.Start;')
replace('DungeonGameMode.cpp','    PlayerFighter->EndGroundMotionFrame(SimulationTime);','    PlayerFighter->EndGroundMotionFrame(SimulationTime);\n    DispatchHeroLocomotionAudioV001(); // Completed real tick; same-endpoint terminal state suppresses stale cues.')
replace('DungeonFighter.cpp','    const auto R=Dodge.TryStart(Dodge.State().Time,C);','    Game->RefreshHeroLocomotionAudioV001(); // Seed old tail before the real accepted event exists.\n    const auto R=Dodge.TryStart(Dodge.State().Time,C);')
replace('DungeonFighter.cpp','    ClearPendingAttackInput();\n    SyncDodgeAction();\n    return true;','    ClearPendingAttackInput();\n    SyncDodgeAction();\n    Game->ObserveHeroDodgeV001(this,R.Events); // Accepted real Started only, never restored Records.\n    return true;')
replace('DungeonFighter.cpp','    bUnconsumedGroundMotion=true;\n    if(Grounded&&OrdinaryEligible&&HadIntent)PendingWalkDistance+=Distance;','    if(auto* AudioGame=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr)\n        AudioGame->ObserveHeroGroundDistanceV001(this,FromTime,ToTime,Distance,Grounded,OrdinaryEligible,HadIntent);\n    bUnconsumedGroundMotion=true;\n    if(Grounded&&OrdinaryEligible&&HadIntent)PendingWalkDistance+=Distance;')
replace('DungeonFighter.cpp','        JumpVelocity = 630.f;','        if(auto* AudioGame=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr)\n            AudioGame->RefreshHeroLocomotionAudioV001(); // Seed grounded facts before the actual successful takeoff.\n        JumpVelocity = 630.f;')
replace('DungeonFighter.cpp','        Combat.NotifyTakeoff();\n        WeaponSkills.NotifyTakeoff();','        Combat.NotifyTakeoff();\n        WeaponSkills.NotifyTakeoff();\n        if(auto* AudioGame=GetWorld()?GetWorld()->GetAuthGameMode<ADungeonGameMode>():nullptr)\n            AudioGame->ObserveHeroTakeoffV001(this,AudioGame->GetSimulationTime());')
files=[];patch=[]
for name,items in ops.items():
 original=(SOURCE/name).read_bytes();nl='\r\n' if b'\r\n' in original else '\n';text=original.decode('utf-8');changed=text
 for op in items:
  before=op['before'].replace('\n',nl);after=op['after'].replace('\n',nl)
  assert changed.count(before)==1,(name,op['before'],changed.count(before))
  changed=changed.replace(before,after,1)
 files.append({'actual_source':str(SOURCE/name),'source_bytes':len(original),'source_sha256':sha(original),'line_ending':'CRLF' if nl=='\r\n' else 'LF','operations':items,'result_bytes':len(changed.encode('utf-8')),'result_sha256':sha(changed.encode('utf-8'))})
 patch.extend(difflib.unified_diff(text.replace('\r\n','\n').splitlines(True),changed.replace('\r\n','\n').splitlines(True),fromfile='a/UnrealGame/Source/CodexDungeon/'+name,tofile='b/UnrealGame/Source/CodexDungeon/'+name))
with (HERE/'exact-seams.patch').open('x',encoding='utf-8',newline='\n') as f:f.write(''.join(patch))
write('exact-seams.json',{'status':'PROPOSAL_NOT_APPLIED','base_compiled_source_manifest':str(PIN),'base_manifest_sha256':PIN_SHA,'files':files,'new_source_files':[str(p) for p in sorted((HERE/'Source').glob('*'))]})
freeze=json.loads(FREEZE.read_text(encoding='utf-8-sig'));members={r['relative_path']:r for r in freeze['files']}
rows=[];package='/Game/Production/HeroLocomotion/v001/Audio'
for wav in sorted((ASSETS/'wav').glob('*.wav')):
 data=wav.read_bytes();frozen=members['wav/'+wav.name]
 assert len(data)==frozen['bytes'] and sha(data)==frozen['sha256']
 cue=wav.stem.split('__')[0];name='SW_'+cue.replace('-','_')+'_v001'
 rows.append({'cue':cue.removeprefix('AUD-').replace('-','_'),'source_wav':str(wav),'source_bytes':len(data),'source_sha256':sha(data),'asset_name':name,'package_path':package+'/'+name,'object_path':package+'/'+name+'.'+name,'compression':'ADPCM','loading':'FORCE_INLINE','priority':40. if '-STEP-' in cue else 50.,'looping':False,'volume':1.,'pitch':1.})
assert len(rows)==6 and len({r['object_path'] for r in rows})==6
write('import/import-manifest.json',{'schema':'HeroLocomotionAudioImportProposal-v001','status':'NOT_IMPORTED_NOT_AUDITIONED','asset_freeze':str(FREEZE),'asset_freeze_sha256':FREEZE_SHA,'package':package,'destination':str(ROOT/'UnrealGame/Content/Production/HeroLocomotion/v001/Audio'),'soundwave_count':len(rows),'rows':rows})
scount=sum(p.is_file() for p in SOURCE.parent.rglob('*'));modulecount=sum(p.is_file() for p in SOURCE.rglob('*'));pcount=sum(p.is_file() for p in (ROOT/'UnrealGame/Content/Production').rglob('*'));newcount=sum(p.is_file() for p in (HERE/'Source').glob('*'))
write('reports/preparation.json',{'base_source_count_observed':scount,'base_codexdungeon_module_file_count_observed':modulecount,'base_production_file_count_observed':pcount,'proposed_new_source_files':newcount,'proposed_existing_source_files_modified':len(files),'proposed_soundwaves':len(rows),'projected_source_count_if_only_this_integrated':scount+newcount,'projected_production_files_if_exact_import':pcount+len(rows),'actual_files_modified':False,'ue_started':False,'api_called':False})
print(json.dumps({'actual_source_files':scount,'actual_production_files':pcount,'new_source_files':newcount,'overlay_files':len(files),'soundwaves':len(rows),'actual_mutations':False}))
