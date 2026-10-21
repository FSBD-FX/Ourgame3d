"""Prepare only new exact-insert projections; never writes actual Source or runs UE."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];SRC=ROOT/'UnrealGame/Source/CodexDungeon'
FILES=['DungeonWorldProjectiles.h','DungeonGameMode.h','DungeonWorldProjectiles.cpp']
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(rel,obj):
 p=HERE/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8',newline='') as f:f.write(obj if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 return p
def bytewrite(rel,data):
 p=HERE/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(data)
 return p
DTO='''// Transient actual post-placement facts, including a fully blocked zero commit.
// Not audio eligibility, a movement request, saved state, or a new event domain.
struct FDungeonWeaponForwardStepPlacementV001
{
    bool Present=false, GroundedAtCommit=false;
    FGuid RunGuid;
    uint64 RoomInstanceId=0,OwnerId=0,ActionId=0,InstanceId=0,EventId=0;
    uint32 SubhitId=0;
    uint64 PresentationEpoch=0,RunRestartSerial=0,EquipmentRevisionAtCommit=0;
    DungeonWeaponActions::EEvent Kind=DungeonWeaponActions::EEvent::Started;
    DungeonContentCombat::EWeapon Weapon=DungeonContentCombat::EWeapon::SWD001;
    double ActionStart=0.,AtTime=0.,ObservedSimulationTime=0.,RequestedSignedDistance=0.;
    FVector2D Before=FVector2D::ZeroVector,After=FVector2D::ZeroVector,CommittedDelta=FVector2D::ZeroVector;
};

'''
GETTER='''bool ADungeonGameMode::QueryWeaponForwardStepPlacementV001(FDungeonWeaponForwardStepPlacementV001& Out) const
{
    Out={};
    const auto* Fighter=PlayerFighter.Get();
    if(IsRunInstallGated()||!IsValid(Fighter)||Fighter->bDead||!Fighter->IsEquipmentBound())return false;
    const auto& W=LatestWeaponForwardStepPlacementV001;const auto& V=GetEquipmentView();
    const auto& S=Fighter->GetWeaponActionsState();const auto& A=S.Action;
    if(!W.Present||!W.GroundedAtCommit||!V.Bound||!V.RunGuid.IsValid()
        ||W.RunGuid!=V.RunGuid||W.RoomInstanceId!=V.RoomInstanceId||!W.RoomInstanceId
        ||W.OwnerId!=V.OwnerId||!W.OwnerId||Fighter->GetRuntimeEntityId()!=W.OwnerId
        ||WeaponWorld.RunGuid!=W.RunGuid||WeaponWorld.RoomInstanceId!=W.RoomInstanceId
        ||W.PresentationEpoch!=RunPresentationEpoch||W.RunRestartSerial!=RunRestartSerial
        ||W.Kind!=DungeonWeaponActions::EEvent::ForwardStep||W.Weapon!=DungeonContentCombat::EWeapon::SWD001
        ||!W.EventId||!W.ActionId||!W.InstanceId||W.EventId>=S.NextEventId||W.EventId>Fighter->LastSkillEventId
        ||S.Budget.Dead||A.Type!=DungeonWeaponActions::EAction::Skill||A.Weapon!=W.Weapon
        ||!A.Active||!A.Locked||A.StartedAirborne||!A.ForwardStepIssued||A.Terminal==DungeonWeaponActions::EEvent::Interrupted
        ||A.ActionId!=W.ActionId||A.InstanceId!=W.InstanceId||A.Start!=W.ActionStart||A.ActiveAt!=W.AtTime
        ||!std::isfinite(SimulationTime)||S.Time!=SimulationTime||SimulationTime<W.AtTime||SimulationTime>=A.End
        ||!std::isfinite(W.ObservedSimulationTime)||W.ObservedSimulationTime<W.AtTime||W.ObservedSimulationTime>SimulationTime)
        return false;
    Out=W;return true;
}

'''
PUBLISH='''            // Observe only the actual placement above; a blocked commit remains Present.
            // This is independent of AudioScope/Eligible and never dispatches a cue.
            const auto& PlacementAction=AudioSkill.Action;
            if(!IsRunInstallGated()&&Fighter==PlayerFighter&&Fighter->IsEquipmentBound()&&!Fighter->bDead
                &&AudioView.Bound&&AudioView.RunGuid.IsValid()&&AudioView.RoomInstanceId&&AudioView.Revision
                &&Fighter->GetRuntimeEntityId()==AudioView.OwnerId&&AudioView.OwnerId
                &&WeaponWorld.RunGuid==AudioView.RunGuid&&WeaponWorld.RoomInstanceId==AudioView.RoomInstanceId
                &&AudioSkill.Time==SimulationTime&&E.AtTime>=SkillBatchFrom&&E.AtTime<=SkillBatchTo
                &&Fighter->JumpHeight==0.f&&Fighter->JumpVelocity==0.f&&AudioSkill.Budget.Grounded
                &&!AudioSkill.Budget.Dead&&Fighter->GetMeleeCombatState().Grounded
                &&E.EventId&&E.EventId==Fighter->LastSkillEventId&&E.EventId<AudioSkill.NextEventId
                &&E.ActionId&&E.InstanceId&&E.ActionId==E.Action.ActionId&&E.InstanceId==E.Action.InstanceId
                &&E.Action.Type==EAction::Skill&&E.Action.Weapon==DungeonContentCombat::EWeapon::SWD001
                &&E.Action.Active&&E.Action.Locked&&!E.Action.StartedAirborne&&E.Action.ForwardStepIssued
                &&PlacementAction.Type==EAction::Skill&&PlacementAction.Weapon==E.Action.Weapon
                &&PlacementAction.Active&&PlacementAction.Locked&&!PlacementAction.StartedAirborne
                &&PlacementAction.ForwardStepIssued&&PlacementAction.Terminal!=EEvent::Interrupted
                &&PlacementAction.ActionId==E.ActionId&&PlacementAction.InstanceId==E.InstanceId
                &&PlacementAction.Start==E.Action.Start&&PlacementAction.ActiveAt==E.AtTime&&E.Action.ActiveAt==E.AtTime
                &&std::isfinite(SimulationTime)&&std::isfinite(E.AtTime)&&E.AtTime>=0.&&E.AtTime<=SimulationTime
                &&std::isfinite(E.ForwardStep)&&E.ForwardStep!=0.
                &&std::isfinite(AudioBefore.X)&&std::isfinite(AudioBefore.Y)
                &&std::isfinite(AudioAfter.X)&&std::isfinite(AudioAfter.Y))
            {
                FDungeonWeaponForwardStepPlacementV001 Placement;
                Placement.Present=true;Placement.GroundedAtCommit=Fighter->JumpHeight==0.f&&Fighter->JumpVelocity==0.f
                    &&AudioSkill.Budget.Grounded&&Fighter->GetMeleeCombatState().Grounded;
                Placement.RunGuid=AudioView.RunGuid;Placement.RoomInstanceId=AudioView.RoomInstanceId;
                Placement.OwnerId=Fighter->GetRuntimeEntityId();Placement.ActionId=E.ActionId;Placement.InstanceId=E.InstanceId;
                Placement.EventId=E.EventId;Placement.SubhitId=E.SubhitId;Placement.Kind=E.Kind;Placement.Weapon=E.Action.Weapon;
                Placement.PresentationEpoch=RunPresentationEpoch;Placement.RunRestartSerial=RunRestartSerial;
                Placement.EquipmentRevisionAtCommit=AudioView.Revision;Placement.ActionStart=E.Action.Start;
                Placement.AtTime=E.AtTime;Placement.ObservedSimulationTime=SimulationTime;
                Placement.RequestedSignedDistance=E.ForwardStep;Placement.Before=AudioBefore;Placement.After=AudioAfter;
                Placement.CommittedDelta=AudioAfter-AudioBefore;
                LatestWeaponForwardStepPlacementV001=Placement;
            }
'''
getterdecl='''    // Read during the same still-active action; copy the real commit key before End.
    bool QueryWeaponForwardStepPlacementV001(FDungeonWeaponForwardStepPlacementV001& Out) const;
'''
member='''    // Latest real placement observation only; not serialized and never an audio source.
    FDungeonWeaponForwardStepPlacementV001 LatestWeaponForwardStepPlacementV001;
'''
ops=[
 {'id':'placement-dto','file':FILES[0],'anchor':'enum class EDungeonWorldProjectileStop : uint8\n','where':'before','insert':DTO},
 {'id':'const-copy-getter-declaration','file':FILES[1],'anchor':'    const FDungeonActionAudioState& GetActionAudioState() const { return ActionAudioState; }\n','where':'after','insert':getterdecl},
 {'id':'latest-transient-member','file':FILES[1],'anchor':'    FDungeonActionAudioState ActionAudioState;\n','where':'after','insert':member},
 {'id':'const-copy-getter-definition','file':FILES[2],'anchor':'void ADungeonGameMode::ConsumeBoundWeaponEvents(ADungeonFighter* Fighter,const std::vector<DungeonWeaponActions::FEvent>& Events)\n','where':'before','insert':GETTER},
 {'id':'post-real-placement-observation','file':FILES[2],'anchor':'            if(DungeonHeroForwardStepAudioV001::Eligible(E,AudioSkill.Action,Fighter->GetRuntimeEntityId(),\n','where':'before','insert':PUBLISH}]
baselines={};projected={};evidence={};checks=[]
for name in FILES:
 p=SRC/name;original=p.read_bytes();baselines[name]=pin(p);bytewrite('baseline/'+name,original);text=original.decode('utf-8-sig');newline='\r\n' if b'\r\n' in original else '\n';normalized=text.replace('\r\n','\n');cur=normalized;fileops=[]
 for op in ops:
  if op['file']!=name:continue
  assert cur.count(op['anchor'])==1,(name,op['id']);needle=op['insert']+op['anchor'] if op['where']=='before' else op['anchor']+op['insert'];cur=cur.replace(op['anchor'],needle,1);fileops.append(op)
 projectedbytes=cur.replace('\n',newline).encode('utf8');projectedp=bytewrite('projected/'+name,projectedbytes);projected[name]=pin(projectedp)
 inverse=cur
 for op in reversed(fileops):
  needle=op['insert']+op['anchor'] if op['where']=='before' else op['anchor']+op['insert'];assert inverse.count(needle)==1;inverse=inverse.replace(needle,op['anchor'],1)
 assert inverse==normalized
 inversebytes=inverse.replace('\n',newline).encode('utf8');assert inversebytes==original,'Strict inverse byte closure failed; no BOM/current baseline mismatch allowed'
 evidence[name]={'baseline':baselines[name],'projected':projected[name],'newline_preserved':newline=='\r\n','ops':len(fileops),'inverse_all_original_bytes_exact':True}
for op in ops:write('exact-inserts/'+op['id']+'.txt',op['insert'])
assert baselines['DungeonWorldProjectiles.cpp']['sha256']=='1c94c6fd233bd4dd2bd239623b098a49ffa4e72d6c606f01e5e2d4aa58158310'
# Existing complete motion/dedupe/audio blocks remain as exact byte substrings;
# inverse proof also covers all unrelated code across all three actual baselines.
orig=(HERE/'baseline/DungeonWorldProjectiles.cpp').read_bytes();proj=(HERE/'projected/DungeonWorldProjectiles.cpp').read_bytes()
for label,start,end in [('dedupe',b'        if (E.EventId<=Fighter->LastSkillEventId)',b'        if (E.Kind==EEvent::ForwardStep)'),('placement',b'            const auto AudioBefore=',b'            const auto& AudioSkill='),('audio-scope',b'            const auto& AudioSkill=',b'            if(DungeonHeroForwardStepAudioV001::Eligible'),('audio-append',b'            if(DungeonHeroForwardStepAudioV001::Eligible',b'        else if (E.Kind==EEvent::ProjectileEmitted')]:
 i=orig.index(start);j=orig.index(end,i);oldblock=orig[i:j]
 if label=='audio-scope':
  # Insert follows the complete original scope; its precise bytes remain prefix-exact.
  j=orig.index(b'            if(DungeonHeroForwardStepAudioV001::Eligible',i);oldblock=orig[i:j]
 assert oldblock in proj,(label,'changed original block');checks.append({'block':label,'original_bytes':len(oldblock),'original_sha256':hashlib.sha256(oldblock).hexdigest(),'original_bytes_present_unchanged':True})
# Candidate boundary checks are source contracts, not simulated placement or UE tests.
assert 'DistanceSquared' not in PUBLISH and 'CommittedDelta' not in PUBLISH[:PUBLISH.index('FDungeonWeaponForwardStepPlacementV001 Placement;')]
assert 'Placement.Present=true' in PUBLISH and 'Placement.CommittedDelta=AudioAfter-AudioBefore;' in PUBLISH
assert 'AppendActionAudio' not in PUBLISH and 'SetActorLocation' not in PUBLISH and 'SweepWeaponStep' not in PUBLISH
assert GETTER.index('Out={};')<GETTER.index('if(IsRunInstallGated()')
assert 'SimulationTime>=A.End' in GETTER and 'W.PresentationEpoch!=RunPresentationEpoch' in GETTER and 'W.RunRestartSerial!=RunRestartSerial' in GETTER
assert 'W.RunGuid!=V.RunGuid' in GETTER and 'W.RoomInstanceId!=V.RoomInstanceId' in GETTER and 'Fighter->bDead' in GETTER
assert 'W.EventId>=S.NextEventId' in GETTER and 'W.EventId>Fighter->LastSkillEventId' in GETTER
assert 'EquipmentRevisionAtCommit!=' not in GETTER and 'Version' not in GETTER
sourcecount=len([p for p in (ROOT/'UnrealGame/Source').rglob('*') if p.is_file()]);assert sourcecount==303
mapping={
 'Present':'Set true only on actual existing de-duplicated ForwardStep post-SetActorLocation/post-Sync branch, including measured zero delta.',
 'RunGuid/RoomInstanceId/EquipmentRevisionAtCommit':'Already existing actual AudioView=GetEquipmentView(), checked against WeaponWorld Run/Room. Revision observed only, never frozen-version query equality.',
 'OwnerId':'Fighter->GetRuntimeEntityId(), same actual PlayerFighter and current equipment OwnerId.',
 'ActionId/InstanceId/EventId/SubhitId/Kind/Weapon/ActionStart/AtTime/RequestedSignedDistance':'Unchanged true E fields / E.Action fields after original LastSkillEventId de-duplication; IDs not created or borrowed from J.',
 'Before':'Existing AudioBefore=Fighter->GetGroundPosition() immediately before existing SweepWeaponStep and placement.',
 'After':'Existing AudioAfter=Fighter->GetGroundPosition() after existing SetActorLocation and SyncWeaponMuzzleTransform.',
 'CommittedDelta':'Exact actual After-Before, NOT SweepWeaponStep return/request/planned End or observer inference.',
 'GroundedAtCommit':'Actual Fighter JumpHeight/JumpVelocity plus actual WeaponActions budget and Melee grounded states read at commit.',
 'PresentationEpoch':'Existing GameMode RunPresentationEpoch; real CommitPreparedRunGroup increments at existing .cpp354 after publish. Candidate never increments/resets it.',
 'RunRestartSerial':'Existing GameMode RunRestartSerial; BeginEquipmentRun .cpp513 increments, legacy RestartRun .cpp2122 increments. Candidate never increments/resets it.',
 'ObservedSimulationTime':'Existing actual SimulationTime at the commit, not a new clock or observation sequence.'}
seamsp=write('exact-seams-v001.json',{'schema':'forward-step-placement-witness-exact-inserts-v001','baseline_files':baselines,'projected_files':projected,'ops':ops,'strict_inverse_all_original_bytes_exact':True,'existing_audio_scope_and_append_original_bytes_unchanged':True,'existing_motion_dedupe_windows_original_bytes_unchanged':True,'actual_source_files_before':303,'proposed_source_files_after':303,'actual_source_modified':False})
write('verification/source-contract-checks-v001.json',{'schema':'forward-step-placement-source-contract-verification-v001','utc':datetime.now(timezone.utc).isoformat(),'file_inverse_checks':evidence,'preserved_blocks':checks,'zero_commit_not_rejected_by_delta_filter':True,'actual_after_minus_before_only':True,'no_audio_motion_id_clock_writes':True,'read_failure_clears_out':True,'restore_newscope_death_end_event_cursor_guards_present':True,'current_Revision_version_not_compared_to_commit':True,'actualSource303_unchanged':True,'host_Cpp_compile_run':False,'UE_compile_run':False,'native_zero_partial_full_verified':False,'note':'Latest Root instruction: no new test files. These are bounded static source/seam checks only, no mock placement or native pass claim.'})
write('field-sources-and-lifecycle-v001.json',{'field_sources':mapping,'lifecycle':{'new_run':'RunGuid + existing RunRestartSerial differ; query rejects old stored value without changing business reset paths.','new_room':'actual EquipmentView and WeaponWorld RoomInstanceId differ; query rejects old stored room.','restore':'existing RunPresentationEpoch increment invalidates all pre-restore values, even if persisted Run/Room/Action/Event IDs match; install-gated queries also return false.','death':'bDead / budget.Dead read directly; getter clears Out and rejects. No death rules changed.','new_action_or_weapon':'current actual Skill ActionId/InstanceId/ActionStart must match witness, plus actual current action must remain active/locked/ForwardStepIssued.','action_End_or_interrupt':'getter rejects !Active, Interrupted or SimulationTime>=A.End. Observer must read each callback during the real active action and preserve its own local copy. End-time lookup cannot manufacture an instant placement proof.','dedupe':'Producer is inside the unchanged E.EventId>LastSkillEventId branch after LastSkillEventId=E.EventId; no new IDs or sequences. Getter also checks EventId against real consumed LastSkillEventId and real kernel NextEventId.','observer_stale_key':'A successful getter returns latest same-active-action actual fact, not a per-callback new event guarantee. Observer MUST compare Run/Room/Owner/PresentationEpoch/RunRestartSerial/Action/Instance/Event/Subhit/AtTime to its genuine expected event and de-duplicate locally; do not infer zero from lack of audio DTO or getter failure.','no_snapshot_restore':'Private latest value is transient; no D13 Owner/World/Run schema or restoration assignments added.','audio_independent':'Witness neither requires HeroLocomotionAudioActiveV001 nor calls audio eligibility or Append. Actual audio branch preserved byte-for-byte and remains silent on zero.'},'actual_root_facts':{'WorldProjectiles_baseline_sha256':baselines['DungeonWorldProjectiles.cpp']['sha256'],'current_CM_parent_supplied':'ae00569b','no_claim_CM_was_independently_recomputed':True},'not_yet_native_verified':True})
write('HANDOFF-v001.md','''# Actual ForwardStep placement witness candidate

Candidate only. 3 existing projected files, 5 strict insert ops; Source303→303, no new Source/test files. Actual Source/Content/tools/E/status/ledger untouched. Use exact-seams-v001.json against pinned baselines, compose with later Root runtime changes; do not overwrite current files wholesale. Every original byte is recovered exactly by removing only the 5 inserts. Original motion/de-duplication/audio scope/eligibility/Append and window logic remain byte-identical.

API: `bool ADungeonGameMode::QueryWeaponForwardStepPlacementV001(FDungeonWeaponForwardStepPlacementV001& Out) const`. On false Out is reset. The latest member is private/transient; DTO in existing DungeonWorldProjectiles.h. No serialization, new event ID/sequence, timer, motion, sound or damage call.

Producer sits in the existing de-duplicated bound ForwardStep branch after real SetActorLocation/SyncWeaponMuzzleTransform and existing AudioBefore/AudioAfter reads. It uses the real E EventId/SubhitId/ActionId/InstanceId/AtTime/requested signed distance and current actual Run/Room/Owner. `CommittedDelta=AudioAfter-AudioBefore` even if zero; Present=true does not depend on nonzero movement or audio. GroundedAtCommit, ActionStart, current existing SimulationTime, RunPresentationEpoch, RunRestartSerial and observed equipment revision are captured as provenance. Revision is not a frozen-version validation gate.

Observer must read the real getter every callback WHILE THE SAME ACTION IS STILL ACTIVE and save its own local snapshot. Getter rejects ended/interrupted/new actions, dead owners, changed scopes, restored presentation epochs, restart serials and inconsistent real event cursors. It intentionally cannot return a value at/after End. Compare full genuine event key (including Run/Room/Owner/epoch/Action/Instance/Event/Subhit/AtTime) against the expected real emission and de-duplicate locally. A successful lookup is the latest fact for this active action, not proof a new placement occurred in this callback. Getter failure or absent audio is NOT evidence of zero.

Existing private Fighter BatchSkillStepAt/Delta is a batch accumulator without event key; QueryCompletedGroundMotion only covers ordinary movement. Neither is reused as fake zero evidence. No existing same-event skill placement getter was found.

Restore invalidation uses existing CommitPreparedRunGroup RunPresentationEpoch increment(.cpp354); new run uses existing RunGuid and RunRestartSerial increments(.cpp513 / legacy2122); room exit changes existing room ID. No new reset hooks or lifecycle state machines. Raw field sources and exact boundaries are in field-sources-and-lifecycle-v001.json.

Bounded source-contract checks verify strict inverse, zero has no delta-positive filter, no producer audio/motion/ID/clock side effects, lifecycle guards, and exact preserved original blocks. Per latest Root instruction no new test files. No host C++/UE compile or native full/partial/zero claim. Root independent review, exact-seam composition, actual build and native checks remain required. Actor observer v001 blocked-zero remains HARD_NOT_READY until a NEW observer consumes actual getter; its separate first-run route gate must use explicit exploratory mode, not invented verified=true.

FinalAccepted=false, runtime_ready=false, actual_source_modified=false.
''')
deps=[*baselines.values(),pin(SRC/'DungeonFighter.h'),pin(SRC/'DungeonFighter.cpp'),pin(SRC/'DungeonGameMode.cpp'),pin(SRC/'DungeonActionAudioFeedback.h'),pin(SRC/'DungeonCompletedGroundMotion.h'),pin(SRC/'DungeonWeaponActions.h')]
members=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='candidate-freeze-v001.json']
for _ in range(2):
 for r in members+deps:assert pin(r['path'])==r
freezep=write('candidate-freeze-v001.json',{'schema':'actual-forward-step-placement-witness-unadmitted-candidate-freeze-v001','members':members,'dependency_pins':deps,'verification_passes':2,'twoSHA_mismatches':0,'existing_projected_files':3,'insert_ops':5,'new_Source_files':0,'new_test_files':0,'actual_Source_count':303,'proposed_Source_count':303,'strict_inverse_original_bytes_exact':True,'audio_motion_window_dedupe_original_bytes_preserved':True,'actual_source_modified':False,'host_Cpp_compiled':False,'UE_compiled':False,'native_verified':False,'runtime_ready':False,'RootApproved':False,'FinalAccepted':False})
print(json.dumps({'freeze':pin(freezep),'members':len(members),'deps':len(deps),'baselines':baselines,'projected':projected,'strict_inverse':True,'new_tests':0,'actual_Source_count':sourcecount},ensure_ascii=False))
