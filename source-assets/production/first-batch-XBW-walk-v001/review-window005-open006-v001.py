"""Audit the actual closed request window before continuing existing auto-authorization."""
from pathlib import Path
import importlib.util,collections
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('rec',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
d=r.read(r.LEDGER);assert d['requested_count']==120 and d['current_window']['number']==5 and d['current_window']['requested_count']==24
for n in [118,119,120]:
 e=next(x for x in d['requests'] if x['request_number']==n);e.update(status='native_XBW_walk_garment_source_reviewed_pending_semantic_selection',reviewed_utc=r.now(),review_notes='All6poses viewed afterF/E retention: new native costume matches frozen two-hand walk source; head/hands are reference only and will be discarded. Layer masks/assembly still pending; not runtime accepted.')
entries=[e for e in d['requests'] if 97<=e['request_number']<=120];assert len(entries)==24
paths=0;rows=[]
for e in entries:
 assert e['status']!='requested' and 'raw_path'in e,(e['request_number'],e['status'])
 for q in [e['tool_original_path'],e['raw_path']]+e['archive_paths']:
  p=Path(q);assert r.sha(p)==e['sha256'];Image.open(p).verify();paths+=1
 for ref in e.get('references',[]):assert r.sha(Path(ref['path']))==ref['sha256']
 rows.append({'request_number':e['request_number'],'status':e['status'],'raw_path':e['raw_path'],'raw_sha256':e['sha256'],'native_dimensions':e['image_size'],'archive_paths_verified':len(e['archive_paths']),'source_directory':e['source_directory']})
q=P/'reviews/window005-request-source-audit-v001.json';assert not q.exists();r.write(q,{'schema':'closed-generation-window-source-audit-v1','window_number':5,'request_range':[97,120],'requested_count':24,'pending_count':0,'actual_raw_images':24,'actual_original_raw_archive_paths_verified':paths,'all_reference_hashes_match':True,'status_counts':dict(collections.Counter(e['status']for e in entries)),'requests':rows,'review_scope':'Source request completion/hash/retention and per-request honest status only. Some garment source selection is pending; closing a24call accounting window does not accept runtime/full equipment.','external_API_calls':0,'host_fee_usd':None,'auto_authorization':['EV039','EV040','EV041'],'new_walk_task_call_limit':8,'new_walk_task_used':5,'source_only':True});r.archive(q,q.relative_to(P),'window005_closed_source_retention_QC_not_runtime_acceptance')
old=dict(d['current_window']);old.update(status='closed_source_QC_reviewed_before_auto_window006',review_path=str(q),review_sha256=r.sha(q),closed_utc=r.now())
d.setdefault('completed_windows',[]).append(old)
d['current_window']={'number':6,'first_request_number':121,'last_request_number':144,'request_limit':24,'requested_count':0,'status':'active_auto_authorized_after_window005_review'}
d['accounting_window_id']='window006';d['batch_requested_count']=0;d['remaining_batch_requests']=24;r.write(r.LEDGER,d)
snapshot=P/'reviews/generation-ledger-after-window005-before-request121-v001.json';r.write(snapshot,d);r.archive(snapshot,snapshot.relative_to(P),'immutable_post_window005_QC_pre_window006_snapshot')
for a in r.ARCHIVES:r.write(a/'generation-ledger-snapshot.json',d)
print({'window5_closed':True,'verified_source_paths':paths,'pending':0,'window6_opened':True,'walk_task_used':5,'walk_task_remaining':3,'audit_sha256':r.sha(q)})
