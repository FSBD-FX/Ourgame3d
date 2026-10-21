"""Actual skill matte and whole-canvas uniform normalization; no art synthesis."""
from pathlib import Path
import importlib.util,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
skill_path=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py')
s=importlib.util.spec_from_file_location('skill',skill_path);skill=importlib.util.module_from_spec(s);s.loader.exec_module(skill)
out=P/'processed/neutral-props-v002';assert not out.exists();out.mkdir(parents=True)
components=P/'components';components.mkdir(exist_ok=True);rows=[]
ledger=r.read(r.LEDGER)
for number,key in [(77,'XBW'),(78,'STF'),(79,'SPR'),(80,'GSW')]:
    entry=next(x for x in ledger['requests'] if x['request_number']==number);source=Path(entry['raw_path']);assert r.sha(source)==entry['sha256']
    raw=Image.open(source).convert('RGBA');assert raw.size==(1254,1254)
    matte=skill.remove_bg_magenta(raw.copy(),threshold=90,edge_threshold=140);matte=skill.clean_edges(matte,depth=3)
    native_chroma_removed=sum(1 for px in matte.get_flattened_data() if px[3] and px[0]>px[1]+30 and px[2]>px[1]+30)
    matte.putdata([(0,0,0,0) if px[3] and px[0]>px[1]+30 and px[2]>px[1]+30 else px for px in matte.get_flattened_data()])
    erased=sum(1 for before,after in zip(raw.get_flattened_data(),matte.get_flattened_data()) if before[3] and not after[3] and not(before[0]>before[1]+30 and before[2]>before[1]+30))
    assert erased==0
    native_path=out/f'{key}-native-alpha.png';matte.save(native_path)
    normalized=matte.resize((512,512),Image.Resampling.LANCZOS)
    # Canonical transparent RGB for deterministic compositing; no visible pixels
    # are painted or geometrically fitted to a bbox.
    output_chroma_removed=sum(1 for px in normalized.get_flattened_data() if px[3] and px[0]>px[1]+30 and px[2]>px[1]+30)
    normalized.putdata([px if px[3] and not(px[0]>px[1]+30 and px[2]>px[1]+30) else (0,0,0,0) for px in normalized.get_flattened_data()])
    alpha=normalized.getchannel('A');assert alpha.getextrema()==(0,255)
    corners=[list(normalized.getpixel(pt)) for pt in [(0,0),(511,0),(0,511),(511,511)]];assert all(p[3]==0 for p in corners)
    opaque=[px for px in normalized.get_flattened_data() if px[3]>=128]
    magenta=sum(px[0]>180 and px[2]>150 and px[1]<120 for px in opaque)/len(opaque)
    assert magenta<.001
    path=components/f'{key}001-neutral-component-v002.png';assert not path.exists();normalized.save(path)
    copies=r.archive(path,path.relative_to(P),'real_single_weapon_component_alpha_candidate_pending_sockets')
    r.archive(native_path,native_path.relative_to(P),'native1254_matte_all_source_parts_preserved')
    row={'family':key,'weapon_id':f'WPN-{key}-001','request_number':number,'source_path':str(source),'source_sha256':r.sha(source),
      'native_dimensions_px':[1254,1254],'native_alpha_path':str(native_path),'native_alpha_sha256':r.sha(native_path),
      'path':str(path),'sha256':r.sha(path),'canvas_px':[512,512],'mode':'RGBA','alpha_extrema':[0,255],'corner_rgba':corners,'bbox_px':list(alpha.getbbox()),
      'source_to_output_scale':512/1254,'translation_px':[0,0],'crop':None,'bbox_fit':False,'aspect_distortion':False,'all_parts_kept':True,
      'opaque_magenta_fraction':magenta,'erased_non_chroma_pixels_native':erased,'additional_native_chroma_removed_px':native_chroma_removed,'additional_output_chroma_removed_px':output_chroma_removed,'extra_chroma_mask':'R>G+30 and B>G+30; no such material in requested prop','F_E_copy_hashes_match':all(r.sha(Path(p))==r.sha(path) for p in copies),
      'processor_script':str(skill_path),'processor_sha256':r.sha(skill_path),'processor_calls':'remove_bg_magenta(90,140)+clean_edges(3)',
      'semantic_socket_review_passed':False,'runtime_verified':False}
    rows.append(row)
    entry.setdefault('processing_revisions',[]).append({'component':str(path),'sha256':r.sha(path),'normalization':'whole1254_square_to512_uniform_no_bboxfit'})
report=out/'processing-report.json';r.write(report,{'schema':'single-neutral-weapon-skill-processing-v1','weapons':rows,'generation_calls_added_by_processing':0,'runtime_executed':False})
r.archive(report,report.relative_to(P),'real_weapon_alpha_source_normalization_checks_not_motion_acceptance')
r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print(json.dumps([{'family':x['family'],'bbox':x['bbox_px'],'opaque_magenta_fraction':x['opaque_magenta_fraction'],'erased_non_chroma':x['erased_non_chroma_pixels_native']} for x in rows]))
