"""Verify preserved raw outputs, freeze reviewed window, open authorized next window."""
from pathlib import Path
import importlib.util,json
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
ledger=r.read(r.LEDGER)
assert ledger['requested_count']==48 and ledger['current_window']['number']==2
assert ledger['current_window']['requested_count']==24
rows=[]
for e in ledger['requests']:
    if not 25<=e['request_number']<=48:continue
    source=Path(e['raw_path']);assert source.is_file() and r.sha(source)==e['sha256']
    copies=e['archive_paths'];assert len(copies)==4
    assert all(Path(q).is_file() and r.sha(Path(q))==e['sha256'] for q in copies)
    rows.append({'request_number':e['request_number'],'asset':e['asset'],'raw_path':str(source),'sha256':e['sha256'],'all_four_archive_hashes_match':True,'status_at_review':e['status']})
assert len(rows)==24
for number,status,notes in [
 (45,'common_base_idle6_true_head_hands_preserved_component_prototype','Native clothing-only replacement with frozen head/wrist/hand pixels preserved. Binary near/far split reconstructs base exactly. No per-frame scale or translation. Edge/semantic polish remains.'),
 (48,'same_pose_LGT_idle_real_component_selection_candidate','48 is a full same-pose source, NOT an armor layer. Its manually selected visible torso/shoulder/hem surfaces form separate prototype parts. Sleeve contamination and tiny back-fragment scope are explicit, no runtime pass.')]:
    e=next(x for x in ledger['requests'] if x['request_number']==number);e.update(status=status,review_notes=notes,reviewed_utc=r.now())
review={'schema':'generation-window-review-v1','window':2,'first':25,'last':48,'requested':24,'completed_raw':24,'failed_requests_still_count':True,'all_raw_four_archive_hashes_match':True,'sources':rows,
 'armor_route_result':'45 common underarmor source, 46 and47 detached armor fit FAILED;48 same-pose full source selected into actual armor pixels. Initial plan47/48 P1 changed after observed fit failures. P1/P2/P3 layered production not started.',
 'processing_discovery':'Old matte180/260 erased nonchroma helmet/hand pixels; failed derived v001 retained. Matte90/140 v002 preserves all nonchroma source pixels,24 cells checked. Fine chromatic edge fringe still requires scrutiny.',
 'component_scope':'Idle six frames only. Exact base near/far reconstruction and frozen head/hands equality measured. Selected armor has no head/hands/legs, but minor sleeve-edge contamination remains. Back is a tiny visible hem fragment, not complete hidden back.',
 'runtime_evidence_as_parent_report':'Base68+Walk6 =74 unique body /80 logical markers. Parent Explore26/26 and actual right/left review found alternating legs and unified identity. Two stride frames lack clear flat support, bob insufficient; footlock/no-slide not certified. This worker did not execute UE.',
 'formal_complete':False,'runtime_verified_by_this_worker':False,'external_api_calls':0,'host_fee_usd':None,'reviewed_utc':r.now()}
review_path=P/'reviews/window002-review-and-source-verification-v001.json';r.write(review_path,review);r.archive(review_path,Path('reviews')/review_path.name,'window002_source_hashes_and_honest_QC_closure')
frozen=r.LEDGER.parent/'generation-ledger-window002-frozen.json'
assert not frozen.exists()
ledger['current_window']['status']='reviewed_closed'
r.write(frozen,ledger);r.archive(frozen,Path('accounting')/frozen.name,'immutable_window002_48_cumulative_requests')
ledger['completed_windows'].append({'number':2,'first_request_number':25,'last_request_number':48,'request_limit':24,'requested_count':24,'status':'reviewed_closed','frozen_ledger':str(frozen),'frozen_ledger_sha256':r.sha(frozen),'review':str(review_path),'review_sha256':r.sha(review_path)})
ledger['current_window']={'number':3,'first_request_number':49,'last_request_number':72,'request_limit':24,'requested_count':0,'status':'active_auto_authorized_after_window002_review'}
ledger.update(batch_requested_count=0,remaining_batch_requests=24,phase='window003_true_armor_components_same_pose_surface_selection')
r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print({'cumulative_requests':48,'lifetime_including_EV038':72,'closed_window':2,'window3_remaining':24,'verified_four_archive_copies':len(rows)*4,'frozen_sha256':r.sha(frozen)})
