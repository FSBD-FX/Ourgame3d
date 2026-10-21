"""In-memory oracle boundary checks only; not synthetic gameplay or native proof."""
from pathlib import Path
import ast,copy,json,runpy
C=Path(__file__).resolve().parent.parent
m=runpy.run_path(str(C/'tooling/verify-Death-v005.py'))
reward=m['reward_proof'];spatial=m['spatial'];cases=[]
death=dict(AtTime=10.)
source=dict(SourceId='1',ObjectId='1',EntityId='3',Room='1',Kind=0,AtTime=10.)
coin=dict(ObjectId='1',SourceId='1',Room='1',CollectionOperationId='1',Kind=0,Amount=9,Position=[82.,88.],Consumed=True,Retired=False)
df=dict(EntityId='3',Room='1',ContentId='ENM-STN-003',AtTime=10.,Position=[100.,100.],FirstDeath=False,RoomCleared=True,SourceIds=['1'])
collection=dict(OperationId='1',ObjectId='1',SourceId='1',OwnerId='1',Room='1',AtTime=11.1,BeforeCoins=20,AfterCoins=29)
rw=dict(Schema=2,Bound=True,Run='test-only',OwnerId='1',Room='1',InitialCoins=20,Deaths=[df],Sources=[source],Objects=[coin],Collections=[collection])
r=dict(rewards_final=rw,run='test-only',owner='1',guard_entity='3',coin_object_id='1',coin_operation_id='1',coin_collected_at=11.1,coin_before=20,coin_after=29,wallet=29,actual_approach_side=-1,death_event_id='20',death_at=10.)
n=dict(dead=True,HP=0,phase=7,can_receive_direct_hit=False,in_progress=False,death_observed=True,death_settled=True,reward_claimed=True,ground=[100.,100.])
slot=dict(stage='3',entity='3',coin='1',coin_share=9,dead_at=10.)
o=dict(rewards=rw,guard_native=n,player_HP=78,player_ground=[22.,88.],sim=11.1,wallet=29,room_cleared=True,slots=[{}, {},slot],phase='normal_guard_J_Death_and_coin',approach_spatial=dict(route_reached=True))
reward(r,death,[o]);cases.append('valid_original_Died_coin9_wallet_chain_with_real_player_damage')
def reject(name,mutator):
 rr,dd,oo=copy.deepcopy((r,death,[o]));mutator(rr,dd,oo)
 try:reward(rr,dd,oo)
 except (ValueError,AssertionError,KeyError):cases.append(name);return
 raise AssertionError('Invalid media-only contract accepted: '+name)
reject('later_legal_Death_time_cannot_reuse_earlier_settlement',lambda rr,dd,oo:dd.update(AtTime=10.01))
reject('duplicated_original_source_rejected',lambda rr,dd,oo:rr['rewards_final']['Sources'].append(copy.deepcopy(rr['rewards_final']['Sources'][0])))
reject('duplicated_collection_rejected',lambda rr,dd,oo:rr['rewards_final']['Collections'].append(copy.deepcopy(rr['rewards_final']['Collections'][0])))
reject('wrong_coin_amount_rejected',lambda rr,dd,oo:rr['rewards_final']['Objects'][0].update(Amount=5))
reject('wrong_wallet_after_rejected',lambda rr,dd,oo:rr.update(wallet=30))
reject('remote_first_consumed_callback_rejected',lambda rr,dd,oo:oo[0].update(player_ground=[0.,0.]))
reject('gameplay_hit_enabled_after_dead_rejected',lambda rr,dd,oo:oo[0]['guard_native'].update(can_receive_direct_hit=True))
so=copy.deepcopy(o);so['player_ground']=[-25.,100.];s=dict(Selection=dict(Clip='Death',SourceEventId='20',SampleTime=10.05))
assert spatial(so,s,r);cases.append('actual_Died_original_window_spatial_credit')
s['Selection']['SampleTime']=11.;assert not spatial(so,s,r);cases.append('held_last_frame_after_original1s_cannot_repair_coverage')
s['Selection'].update(SampleTime=10.05,SourceEventId='21');assert not spatial(so,s,r);cases.append('other_death_event_cannot_donate_phase')
for p in (C/'tooling').glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
print(json.dumps(dict(schema='Death-contract-only-static-check-v005',passed=True,cases=cases,Python_AST_parsed=True,synthetic_in_memory_contract_only=True,native_proof_generated=False,UE_started=False,UBT_started=False,View_used=False,compiled=False,formal_complete_units=0)))
