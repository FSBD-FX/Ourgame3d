"""Verify all 24 actual outputs before closing window3 and opening authorized4."""
from pathlib import Path
import importlib.util, copy, json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
j=r.read(r.LEDGER);assert j['requested_count']==72 and len(j['requests'])==72
assert j['current_window']['number']==3 and j['current_window']['requested_count']==24
assert j['automatic_follow_on_batches_authorized'] is True
rows=[];frame_count=0;errors=[]
for n in range(49,73):
    entry=next(x for x in j['requests'] if x['request_number']==n)
    raw=Path(entry['raw_path']);prompt=Path(entry['prompt_path']);tool=Path(entry['tool_original_path'])
    assert raw.exists() and tool.exists() and r.sha(raw)==r.sha(tool)==entry['sha256']
    assert prompt.read_text('utf-8')==entry['prompt']
    assert all(Path(x['path']).exists() and r.sha(Path(x['path']))==x['sha256'] for x in entry['references'])
    assert len(entry['archive_paths'])==4 and all(r.sha(Path(q))==entry['sha256'] for q in entry['archive_paths'])
    assert 'pending_review' not in entry['status'] or n!=72
    r.archive(prompt,prompt.relative_to(P),'window003_original_request_prompt_reviewed')
    report_path=P/f'processed/call{n}-fixed-canvas-v002/fixed-canvas-report.json';rep=r.read(report_path)
    assert len(rep['frames'])==6
    for frame in rep['frames']:
        path=Path(frame['path']);assert r.sha(path)==frame['sha256']
        with Image.open(path) as im:
            assert im.mode=='RGBA' and im.size==(512,512) and im.getchannel('A').getextrema()==(0,255)
            assert all(im.getpixel(pt)[3]==0 for pt in [(0,0),(511,0),(0,511),(511,511)])
        assert frame['erased_non_chroma_pixels']==0 and not frame['bbox_fit_applied']
        assert frame['translation']==[0,0] and frame['source_to_output_scale']==1.0
        copies=r.archive(path,path.relative_to(P),'window003_fixed_canvas_real_alpha_source_candidate');assert all(r.sha(Path(q))==frame['sha256'] for q in copies)
        frame_count+=1
    rows.append({'request_number':n,'asset':entry['asset'],'status':entry['status'],'raw_path':str(raw),'sha256':entry['sha256'],
        'C_original_and_4_F_E_raw_copies_verified':True,'prompt_sha256':r.sha(prompt),'reference_hashes_match':True,
        'fixed_canvas_report':str(report_path),'fixed_canvas_report_sha256':r.sha(report_path),'actual_RGBA_frames_verified':6})

review_path=P/'reviews/window003-review-and-source-verification-v001.json';assert not review_path.exists()
review={'schema':'generation-window-output-review-v1','window_number':3,'first_request':49,'last_request':72,'request_count':24,'reviewed_utc':r.now(),
 'request_limit':24,'completed_native_outputs':24,'source_rows':rows,'raw_F_E_copies_verified':96,'C_tool_originals_verified':24,
 'actual_RGBA512_fixed_canvas_frames_verified':frame_count,'frame_F_E_copies_verified':frame_count*4,
 'scale_or_translation_applied':False,'material_erasure_non_chroma_pixels':0,'new_generation_called_by_review':False,
 'review_scope':'All24 native outputs were actually viewed after retention. This closes accounting/QC only; source cloth candidates are not all semantically complete, assembled or runtime accepted.',
 'known_limits':['Native71 P3 robe has actual bare-forearm gaps in several poses; full sleeve coverage absent.',
  'Native66 P2 pose0 narrow cuff skin gap remains; sleeve contracts require explicit armor_near.',
  '49-71 source masks/derived failed versions retained; source alpha QC does not make old partial armor complete.',
  '72 common hurt source is reviewed/matted but not yet restored into frozen common body or four armor surfaces.',
  'walk original support-contact/bob limits remain. Native AA fringe and all runtime transitions require game review.'],
 'art_complete':False,'runtime_verified':False,'external_api_calls':0,'host_fee_usd':None,'errors':errors}
assert frame_count==144 and not errors
r.write(review_path,review);r.archive(review_path,review_path.relative_to(P),'window00324_output_QC_closed_not_content_acceptance')
frozen_path=r.LEDGER.parent/'generation-ledger-window003-frozen.json';assert not frozen_path.exists()
snapshot=copy.deepcopy(j);snapshot['current_window'].update(status='reviewed_closed',review=str(review_path),review_sha256=r.sha(review_path))
r.write(frozen_path,snapshot);r.archive(frozen_path,Path('ledgers')/frozen_path.name,'window003_frozen_24_requests_QC_snapshot')
closed=copy.deepcopy(snapshot['current_window']);closed.update(frozen_ledger=str(frozen_path),frozen_ledger_sha256=r.sha(frozen_path))
j['completed_windows'].append(closed)
j['current_window']={'number':4,'first_request_number':73,'last_request_number':96,'request_limit':24,'requested_count':0,'status':'active_auto_authorized_after_window003_review'}
j['batch_requested_count']=0;j['remaining_batch_requests']=24;j['lifetime_requested_count']=j['lifetime_prior_EV038_requests']+j['requested_count']
r.write(r.LEDGER,j)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',j)
print(json.dumps({'requested_count':72,'window3_frozen':str(frozen_path),'window3_frozen_sha256':r.sha(frozen_path),'review':str(review_path),
 'review_sha256':r.sha(review_path),'RGBA_frames':144,'window4_requested':0,'window4_remaining':24,'errors':0},ensure_ascii=False))
