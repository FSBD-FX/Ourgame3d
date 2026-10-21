"""Real native RGB->alpha and whole-canvas references, never runtime acceptance."""
from pathlib import Path
import importlib.util,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
sp=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py');s=importlib.util.spec_from_file_location('processor',sp);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
ledger=r.read(r.LEDGER)
for number in [90]:
    e=next(x for x in ledger['requests'] if x['request_number']==number);src=Path(e['raw_path']);assert r.sha(src)==e['sha256']
    assert all(r.sha(Path(x))==e['sha256'] for x in [e['tool_original_path'],*e['archive_paths']])
    raw=Image.open(src).convert('RGBA');assert raw.size==(1254,1254)
    im=m.clean_edges(m.remove_bg_magenta(raw,threshold=90,edge_threshold=140),depth=3)
    im.putdata([p if p[3] and not(p[0]>p[1]+30 and p[2]>p[1]+30) else(0,0,0,0) for p in im.get_flattened_data()])
    erased=sum(b[3] and not a[3] and not(b[0]>b[1]+30 and b[2]>b[1]+30) for b,a in zip(raw.get_flattened_data(),im.get_flattened_data()));assert erased==0
    out=P/f'processed/call{number}-single-keypose-v001';assert not out.exists();out.mkdir()
    native=out/'keypose-native-alpha.png';im.save(native);r.archive(native,native.relative_to(P),'single_native_integrated_keypose_alpha_not_generic_body')
    can=im.resize((512,512),Image.Resampling.LANCZOS);can.putdata([p if p[3] and not(p[0]>p[1]+30 and p[2]>p[1]+30) else(0,0,0,0) for p in can.get_flattened_data()]);q=out/'keypose-canonical512.png';can.save(q);r.archive(q,q.relative_to(P),'single_keypose_uniform_wholecanvas512_reference_not_runtime_animation')
    corners=[can.getpixel(pt)[3] for pt in [(0,0),(511,0),(0,511),(511,511)]];assert corners==[0,0,0,0] and can.getchannel('A').getextrema()==(0,255)
    report={'schema':'single_keypose_reference_processing_v1','request_number':number,'source':str(src),'source_sha256':r.sha(src),'source_canvas':[1254,1254],
      'native_alpha_path':str(native),'native_alpha_sha256':r.sha(native),'canonical_path':str(q),'canonical_sha256':r.sha(q),'canonical_canvas':[512,512],
      'geometry':'whole_canvas_uniform512/1254_only_no_bboxfit_no_translation_no_crop','native_bbox':list(im.getchannel('A').getbbox()),'canonical_bbox':list(can.getchannel('A').getbbox()),
      'corner_alpha':corners,'alpha_extrema':[0,255],'erased_non_chroma_pixels':erased,'processor':str(sp),'processor_sha256':r.sha(sp),
      'source_includes_weapon':True,'semantic_body_weapon_decomposition_complete':False,'usable_runtime_animation_frames':0,'runtime_verified':False,'original_C_F_E_hashes_verified':True}
    j=out/'processing-report.json';r.write(j,report);r.archive(j,j.relative_to(P),'actual_png_reference_processing_evidence_not_mechanical_acceptance')
    e.setdefault('processing_revisions',[]).append({'report':str(j),'sha256':r.sha(j),'geometry':'whole_canvas1254to512_uniform_only','runtime_asset':False})
    print(json.dumps({'number':number,'reference':str(q),'erased_non_chroma':erased,'runtime_frames':0}))
r.write(r.LEDGER,ledger)
for f in r.ARCHIVES:r.write(f/'generation-ledger-snapshot.json',ledger)
src=Path(next(x for x in ledger['requests'] if x['request_number']==90)['raw_path']);q=P/'reviews/XBW-mechanical-contact-90-native-crop-v001.png';assert not q.exists()
Image.open(src).crop((520,590,1010,870)).resize((980,560),Image.Resampling.NEAREST).save(q);r.archive(q,q.relative_to(P),'actual_source_contact_crop2x_nearest_not_runtime_art')
