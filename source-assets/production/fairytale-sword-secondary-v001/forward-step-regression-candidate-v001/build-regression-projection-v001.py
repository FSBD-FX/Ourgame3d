from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re

HERE=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame')
REL='UnrealGame/Source/CodexDungeon/Tests/DungeonMeleeAudioJournalIntegrationTests.cpp'
SOURCE=ROOT/REL
EXPECTED={'bytes':16662,'sha256':'1988802f314071e27d5c74c7bd998ffb9661236bfd93c811fa2b7334d63e8e1a'}
FAILURE=ROOT/'UnrealGame/Saved/Automation/FirstRoomNativeRHI-20261019-062104/index.json'
BUILD=ROOT/'UnrealGame/Saved/Bootstrap/build-editor-20261019-061304.log'
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(rel,value):
 p=HERE/rel;p.parent.mkdir(parents=True,exist_ok=True)
 b=value if isinstance(value,bytes) else (value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 with p.open('xb') as f:f.write(b)
 return p
before=SOURCE.read_bytes();assert len(before)==EXPECTED['bytes'] and hashlib.sha256(before).hexdigest()==EXPECTED['sha256']
assert pin(FAILURE)['sha256']=='625037d5cf53cbaa03221c3181d7b9c23e7ad6dfb37cc80a6d358cf274a49bc4'
report=json.loads(FAILURE.read_bytes());assert report['succeeded']==202 and report['failed']==1 and len(report['tests'])==203
failed=[t for t in report['tests'] if t['state']!='Success'];assert len(failed)==1
assert failed[0]['fullTestPath']=='CodexDungeon.Content.MeleeAudioJournal.NormalSkillsRealIndependentSubhitsOnce'
write('before/'+REL,before);write('evidence/failed-index-062104.json',FAILURE.read_bytes());write('evidence/build-editor-061304.log',BUILD.read_bytes())
write('evidence/original-203-test-ids.json',{'schema':'original203-test-identity-before-forward-step-regression-v001','source_report':pin(FAILURE),'ids':sorted(t['fullTestPath'] for t in report['tests']),'failed_entry':failed[0]})

helper=r'''    bool ExpectSkillForwardStep(int32 Family,const MW::FAction& Started,double At,
        double BeforeAt,uint64 BeforeEventId,FVector2D BeforeGround,bool BeforeGrounded)
    {
        const FString Cue=TEXT("HERO_STEP_LIGHT_01");
        int32 StepFacts=0,StepRequests=0,FactWitnesses=0,RequestWitnesses=0;
        const FDungeonActionAudioRecord* Fact=nullptr;const FDungeonActionAudioPlayRequest* Request=nullptr;
        for(const auto& R:Game->GetActionAudioState().Records)
        {if(R.Cue==Cue){++StepFacts;Fact=&R;}if(R.ForwardStep.Present)++FactWitnesses;}
        for(const auto& R:HUD->GetActionAudioPlayReceipts())
        {if(R.Source.Cue==Cue){++StepRequests;Request=&R;}if(R.Source.ForwardStep.Present)++RequestWitnesses;}
        if(Family!=0)
            return Test->TestTrue(TEXT("Non-SWD real skills add no forward-step cue or witness anywhere in either complete journal"),
                StepFacts==0&&StepRequests==0&&FactWitnesses==0&&RequestWitnesses==0);
        if(!Test->TestTrue(TEXT("SWD has exactly one real forward-step fact, request and copied witness in the complete journals"),
            StepFacts==1&&StepRequests==1&&FactWitnesses==1&&RequestWitnesses==1&&Fact&&Request))return false;
        const auto& V=Game->GetEquipmentView();const auto& State=Player->GetWeaponActionsState();const auto& A=State.Action;
        const auto& World=Game->GetWeaponWorldState();const auto& J=Game->GetActionAudioState();
        const auto& S=Fact->ForwardStep;const auto& P=Request->Source;const auto& Copy=P.ForwardStep;
        const MW::FEvent* Window=nullptr;int32 KernelWindows=0;
        for(const auto& E:State.Issued)
            if(E.Kind==MW::EEvent::ActiveWindow&&E.ActionId==Started.ActionId&&E.InstanceId==AcquiredInstance
                &&E.SubhitId==0&&E.AtTime==At){++KernelWindows;Window=&E;}
        const FDungeonWorldWeaponWindow* WorldWindow=nullptr;int32 WorldWindows=0;
        for(const auto& W:World.Windows)
            if(W.Key.OwnerId==Player->GetRuntimeEntityId()&&W.Key.ActionId==Started.ActionId&&W.Key.SubhitId==0
                &&W.Source.InstanceId==AcquiredInstance&&W.Source.AtTime==At){++WorldWindows;WorldWindow=&W;}
        if(!Test->TestTrue(TEXT("SWD foot witness is backed by exactly one actual kernel and world active window"),
            KernelWindows==1&&WorldWindows==1&&Window&&WorldWindow))return false;
        const auto* Definition=MC::GetWeaponDefinition(A.Weapon);
        if(!Test->TestTrue(TEXT("SWD forward step uses the live ground skill instance and exact ActiveAt, never a J or synthetic clock"),
            Definition&&A.Weapon==MC::EWeapon::SWD001&&A.Type==MW::EAction::Skill&&A.Active&&A.Locked
            &&A.Phase==MC::EPhase::Active&&!A.StartedAirborne&&A.ForwardStepIssued&&A.NextSubhit==1
            &&A.ActionId==Started.ActionId&&A.InstanceId==Started.InstanceId&&A.InstanceId==AcquiredInstance
            &&State.EquippedId==AcquiredInstance&&A.Start==Started.Start&&A.ActiveAt==Started.ActiveAt&&A.ActiveAt==At
            &&State.Time==At&&Game->GetSimulationTime()==At&&World.Time==At
            &&BeforeAt==std::nextafter(At,-std::numeric_limits<double>::infinity())&&BeforeGrounded
            &&Player->GetMeleeCombatState().Grounded&&State.Budget.Grounded&&!State.Budget.Dead&&!Player->bDead
            &&Player->JumpHeight==0.f&&Player->GetVerticalVelocity()==0.f&&Game->PlayerFighter==Player&&!Player->bEnemy
            &&Game->HasAuthority()&&Player->HasAuthority()&&Game->GetWorld()==Player->GetWorld()
            &&!UGameplayStatics::IsGamePaused(Game)&&!Game->IsRunInstallGated()&&!Game->bWaitingForStart&&!Game->bGameOver))return false;
        if(!Test->TestTrue(TEXT("SWD foot source EventId is the actual pre-boundary next event, immediately before its real Subhit0 window"),
            BeforeEventId>0&&S.Present&&S.EventId==BeforeEventId&&S.SubhitId==0
            &&Window->EventId==BeforeEventId+1&&State.NextEventId==BeforeEventId+2
            &&WorldWindow->Key.EventId==Window->EventId&&WorldWindow->Source.EventId==Window->EventId
            &&Window->Action.ActionId==A.ActionId&&Window->Action.InstanceId==A.InstanceId
            &&Window->Action.ForwardStepIssued&&WorldWindow->Source.ActionId==A.ActionId
            &&WorldWindow->Source.InstanceId==A.InstanceId&&WorldWindow->Source.SubhitId==0
            &&WorldWindow->Source.Action.ActionId==A.ActionId
            &&WorldWindow->Source.Action.InstanceId==A.InstanceId))return false;
        if(!Test->TestTrue(TEXT("SWD foot fact keeps the committed real Run Room Owner Action Instance and revision parent"),
            V.Bound&&V.RunGuid.IsValid()&&V.ActiveSlot>=0&&V.ActiveSlot<2&&V.Slots[V.ActiveSlot].InstanceId==AcquiredInstance
            &&Fact->Cue==Cue&&Fact->RunGuid==V.RunGuid&&Fact->RunGuid==J.RunGuid&&Fact->RunGuid==World.RunGuid
            &&Fact->RoomInstanceId==V.RoomInstanceId&&Fact->RoomInstanceId==J.RoomInstanceId
            &&Fact->RoomInstanceId==World.RoomInstanceId&&Fact->RoomInstanceId==WorldWindow->Key.RoomInstanceId
            &&Fact->OwnerId==V.OwnerId&&Fact->OwnerId==Player->GetRuntimeEntityId()&&Fact->OwnerId==WorldWindow->Key.OwnerId
            &&Fact->ActionId==A.ActionId&&Fact->InstanceId==AcquiredInstance&&Fact->AtTime==At&&Fact->OperationId==0
            &&Fact->Revision==V.Revision&&Fact->Revision>0&&Fact->Sequence>0&&Fact->Sequence<J.NextSequence))return false;
        const FVector2D ActualAfter=Player->GetGroundPosition();const FVector2D ActualDelta=ActualAfter-BeforeGround;
        if(!Test->TestTrue(TEXT("SWD foot audio witnesses requested signed30 versus the actual finite positive bounded ground commit"),
            std::isfinite(S.RequestedSignedDistance)&&Definition->Skill.ForwardStep==30.
            &&S.RequestedSignedDistance==Definition->Skill.ForwardStep*A.Facing
            &&std::isfinite(S.Before.X)&&std::isfinite(S.Before.Y)&&std::isfinite(S.After.X)&&std::isfinite(S.After.Y)
            &&std::isfinite(S.CommittedDelta.X)&&std::isfinite(S.CommittedDelta.Y)
            &&S.Before==BeforeGround&&S.After==ActualAfter&&S.CommittedDelta==ActualDelta&&S.CommittedDelta==S.After-S.Before
            &&S.CommittedDelta.X*A.Facing>0.&&S.CommittedDelta.Y==0.
            &&FMath::Abs(S.CommittedDelta.X)<=FMath::Abs(S.RequestedSignedDistance)))return false;
        const FString ExpectedPath=TEXT("/Game/Production/HeroLocomotion/v001/Audio/SW_AUD_HERO_STEP_LIGHT_01_v001.SW_AUD_HERO_STEP_LIGHT_01_v001");
        return Test->TestTrue(TEXT("Existing HUD consumer copies every SWD foot source field and requests the real light-step asset once at original gain"),
            P.Sequence==Fact->Sequence&&P.Cue==Fact->Cue&&P.AtTime==Fact->AtTime&&P.RunGuid==Fact->RunGuid
            &&P.RoomInstanceId==Fact->RoomInstanceId&&P.OwnerId==Fact->OwnerId&&P.ActionId==Fact->ActionId
            &&P.InstanceId==Fact->InstanceId&&P.OperationId==Fact->OperationId&&P.Revision==Fact->Revision
            &&Copy.Present==S.Present&&Copy.EventId==S.EventId&&Copy.SubhitId==S.SubhitId
            &&Copy.RequestedSignedDistance==S.RequestedSignedDistance&&Copy.Before==S.Before&&Copy.After==S.After&&Copy.CommittedDelta==S.CommittedDelta
            &&Request->SoundPath==ExpectedPath&&Request->Volume==.25f&&Request->Pitch==1.f&&Request->RequestedAt==At);
    }
'''
pre=r'''            // Read the actual immediately preceding point; do not add ticks, input, placement or a fake event.
            const double ForwardStepBeforeAt=F.Game->GetSimulationTime();
            const uint64 ForwardStepBeforeEventId=F.Player->GetWeaponActionsState().NextEventId;
            const FVector2D ForwardStepBeforeGround=F.Player->GetGroundPosition();
            const bool ForwardStepBeforeGrounded=F.Player->GetWeaponActionsState().Budget.Grounded
                &&F.Player->GetMeleeCombatState().Grounded&&F.Player->JumpHeight==0.f&&F.Player->GetVerticalVelocity()==0.f;
            if(Family==0&&!TestEqual(TEXT("SWD step sound is absent before its real ActiveAt"),
                F.Facts(TEXT("HERO_STEP_LIGHT_01"),A.ActionId,A.ActiveAt),0))return false;
'''
post=r'''            if(!F.ExpectSkillForwardStep(Family,A,At,ForwardStepBeforeAt,ForwardStepBeforeEventId,
                ForwardStepBeforeGround,ForwardStepBeforeGrounded))return false;
'''
ops=[
 {'label':'strict-foot-source-helper','kind':'insert_before','anchor':'    bool NoReplay()\n','addition':helper},
 {'label':'read-real-point-before-existing-At-step','kind':'insert_after','anchor':'            if(!F.AdvanceTo(std::nextafter(At,-std::numeric_limits<double>::infinity())))return false;\n','addition':pre},
 {'label':'strict-foot-check-after-existing-At-step','kind':'insert_after','anchor':'            if(!F.AdvanceTo(At))return false;\n','addition':post},
 {'label':'complete-journal-facts-now-includes-SWD-step-only','kind':'replace','anchor':'        TestEqual(TEXT("Skill facts count exactly matches real independent window count"),F.Game->GetActionAudioState().Records.Num(),int32(D->Skill.SubhitCount));\n','addition':'        TestEqual(TEXT("Skill complete journal facts equal real independent windows plus only the SWD step"),F.Game->GetActionAudioState().Records.Num(),int32(D->Skill.SubhitCount)+(Family==0?1:0));\n'},
 {'label':'complete-journal-requests-now-includes-SWD-step-only','kind':'replace','anchor':'        TestEqual(TEXT("Skill requests count exactly matches real independent window count"),F.HUD->GetActionAudioPlayReceipts().Num(),int32(D->Skill.SubhitCount));\n','addition':'        TestEqual(TEXT("Skill complete journal requests equal real independent windows plus only the SWD step"),F.HUD->GetActionAudioPlayReceipts().Num(),int32(D->Skill.SubhitCount)+(Family==0?1:0));\n'},
]
after=before
for op in ops:
 a=op['anchor'].encode();x=op['addition'].encode();assert after.count(a)==1,(op['label'],'anchor')
 replacement=x+a if op['kind']=='insert_before' else a+x if op['kind']=='insert_after' else x
 after=after.replace(a,replacement,1)
inverse=after
for op in reversed(ops):
 a=op['anchor'].encode();x=op['addition'].encode();replacement=x+a if op['kind']=='insert_before' else a+x if op['kind']=='insert_after' else x
 assert inverse.count(replacement)==1;inverse=inverse.replace(replacement,a,1)
assert inverse==before
old_ids=re.findall(rb'"CodexDungeon\.[^"\r\n]+"',before);new_ids=re.findall(rb'"CodexDungeon\.[^"\r\n]+"',after);assert old_ids==new_ids and len(old_ids)==3
projection=write('projected/'+REL,after)
write('exact-seams-v001.json',{'schema':'forward-step-regression-exact-seams-v001','path':REL,'before':EXPECTED,'after':{k:v for k,v in pin(projection).items() if k!='path'},'operations':ops,'inverse_roundtrip_byte_exact':True,'existing_test_IDs_preserved':[i.decode() for i in old_ids],'actual_Source_modified':False,'UE_or_native_run':False,'FinalAccepted':False})
write('evidence/failure-and-projection-proof-v001.json',{'schema':'forward-step-old-whoosh-only-premise-regression-v001','created_utc':datetime.now(timezone.utc).isoformat(),'original_build_log':pin(BUILD),'original_failed_report':pin(FAILURE),'original_source':pin(SOURCE),'projected_source':pin(projection),'original_result':{'succeeded':202,'failed':1,'succeededWithWarnings':0,'notRun':0,'inProcess':0},'failed_test':failed[0],'cause':'The complete transient action journal now legitimately contains SWD single ActiveWindow whoosh plus one real postcommit ForwardStep light-foot cue; old total==SubhitCount was a whoosh-only premise. Existing exact window, per-whoosh ExpectOne and NoReplay checks remain unchanged.','complete_journal_count_delta':{'SWD':1,'GSW':0,'SPR':0},'inverse_roundtrip_byte_exact':True,'existing_203_test_IDs_not_removed_or_replaced':True,'no_new_input_clock_or_placement':True,'projected_UE_tests_run':False,'projected_native_run':False,'FinalAccepted':False})
assert SOURCE.read_bytes()==before
print(json.dumps({'projected':pin(projection),'exact_seams':pin(HERE/'exact-seams-v001.json'),'roundtrip_exact':True,'existing_test_ids_preserved':3,'original203_ids_retained':203,'actual_source_unchanged':True,'UE_native_run':False}))
