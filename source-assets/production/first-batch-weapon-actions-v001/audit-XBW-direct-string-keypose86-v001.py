"""Single native keypose matte/measurement, not an import-ready animation."""
from pathlib import Path
import importlib.util,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
sp=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py');s=importlib.util.spec_from_file_location('processor',sp);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
ledger=r.read(r.LEDGER);e=next(x for x in ledger['requests'] if x['request_number']==86);src=Path(e['raw_path']);assert r.sha(src)==e['sha256']
assert all(r.sha(Path(x))==e['sha256'] for x in [e['tool_original_path'],*e['archive_paths']])
raw=Image.open(src).convert('RGBA');assert raw.size==(1254,1254)
im=m.clean_edges(m.remove_bg_magenta(raw,threshold=90,edge_threshold=140),depth=3)
im.putdata([p if p[3] and not(p[0]>p[1]+30 and p[2]>p[1]+30) else(0,0,0,0) for p in im.get_flattened_data()])
bad=sum(b[3] and not a[3] and not(b[0]>b[1]+30 and b[2]>b[1]+30) for b,a in zip(raw.get_flattened_data(),im.get_flattened_data()));assert bad==0
out=P/'processed/call86-single-keypose-v001';assert not out.exists();out.mkdir()
native=out/'keypose-native-alpha.png';im.save(native);r.archive(native,native.relative_to(P),'single_native_visible_mechanical_keypose_not_generic_body')
can=im.resize((512,512),Image.Resampling.LANCZOS);can.putdata([p if p[3] and not(p[0]>p[1]+30 and p[2]>p[1]+30) else(0,0,0,0) for p in can.get_flattened_data()]);q=out/'keypose-canonical512.png';can.save(q);r.archive(q,q.relative_to(P),'single_keypose_whole_canvas_uniform1254to512_no_bboxfit')
points={'near_string_contact':[838,690],'support_grip':[792,792],'upper_string_bow_tip':[854,619],'lower_string_bow_tip':[850,830],
 'visible_string_above_hand':[845,645],'visible_string_below_hand':[838,740]}
values={key:{'native_px':p,'canonical_px':[x*512/1254 for x in p],'native_RGBA':list(im.getpixel(tuple(p)))} for key,p in points.items()}
review=im.copy();d=ImageDraw.Draw(review)
for key,row in values.items():
    x,y=row['native_px'];d.ellipse((x-7,y-7,x+7,y+7),outline='cyan',width=2);d.text((x+9,y),key,fill='white')
rq=P/'reviews/XBW-direct-string-start-contact86-v001.png';review.save(rq);r.archive(rq,rq.relative_to(P),'actual_native_single_keypose_string_contact_measurement_diagnostic')
report={'schema':'native-mechanical-keypose-review-v1','keypose':'grasp_relaxed_front_string','source_request':86,'source_path':str(src),'source_sha256':r.sha(src),
 'native_canvas_px':[1254,1254],'canonical_canvas_px':[512,512],'canonical_method':'uniform whole canvas scale512/1254; no_bboxfit/crop/translation',
 'native_alpha_path':str(native),'native_alpha_sha256':r.sha(native),'canonical_path':str(q),'canonical_sha256':r.sha(q),'measurements':values,
 'native_alpha_bbox':list(im.getchannel('A').getbbox()),'canonical_alpha_bbox':list(can.getchannel('A').getbbox()),'erased_non_chroma_pixels':bad,
 'internal_visual_review':'front near_hand visibly reaches/contacts near-vertical relaxed string; far_hand supports front grip; enclosed identity retained',
 'manual_contact_inference':'visible2D hand/string overlap and cable continuity; not a skeleton/3D force or gameplay proof',
 'integrated_source_includes_weapon':True,'independent_layer_extraction_complete':False,'body_occluded_regions_generic_reuse_unfulfilled':True,
 'required_remaining_keyposes':['drawn_string_rear_latch','place_single_bolt_in_rail','return_trigger_ready'],
 'expanded_animation_authorized_after_keypose_review_but_not_created':True,'full_reload_accepted':False,'runtime_verified':False,
 'F_E_C_original_hash_verified':True,'backend':'image_gen.imagegen','host_fee_usd':None,'external_api_calls':0}
j=P/'reviews/XBW-direct-string-start-contact86-v001.json';assert not j.exists();r.write(j,report);r.archive(j,j.relative_to(P),'single_keypose_review_honest_scope_not_animation_acceptance')
e.update(status='direct_string_start_single_keypose_internal_candidate_other_stages_unfulfilled',dispatch_pending=False,dispatched_scope='single_keypose_only',
 review_notes='One native visible-weapon keypose establishes front relaxed-string hand contact; no six-frame grid was called for the superseded86plan. Other3keyposes, decomposition and full reload/runtime pending.',reviewed_utc=r.now())
e.setdefault('processing_revisions',[]).append({'report':str(j),'sha256':r.sha(j),'geometry':'whole_canvas1254to512_uniform_only','runtime_asset':False})
r.write(r.LEDGER,ledger)
for f in r.ARCHIVES:r.write(f/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'review':str(j),'sha256':r.sha(j),'keypose_only':True,'requested_count':ledger['requested_count'],'remaining':ledger['remaining_batch_requests'],'non_chroma_erased':bad}))
