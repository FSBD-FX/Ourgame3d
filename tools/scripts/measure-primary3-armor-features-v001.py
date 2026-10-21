from pathlib import Path
from PIL import Image
import hashlib,json
B=Path('F:/Ourgame/source-assets/production/fairytale-sword-primary3-v001/armor-input-v001');O=B/'component-measurement-v001';assert not O.exists();O.mkdir()
def desc(p):
    d=p.read_bytes();return {'path':p.as_posix(),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
# Visually selected actual large native component feature centres, not a body joint,
# bbox centre or specular highlight. Mapping follows the already-performed fit.
centres={'Chest':[[120,112],[144,140],[156,134],[159,150],[163,146],[149,128]],'NearShoulder':[[88,125],[104,150],[81,110],[85,115],[92,111],[83,116]],'FarShoulder':[[71,35],[30,39],[45,36],[52,35],[63,32],[94,32]]}
earlier={'Chest':[[256,263],[262,261],[260,262],[263,264],[265,266],[258,263]],'NearShoulder':[[249,264],[251,260],[249,264],[250,262],[250,263],[249,263]],'FarShoulder':[[246,253],[248,249],[247,249],[249,251],[247,252],[248,252]]}
maps=json.loads((B/'feature-diagnostics-v001/source-map-v001.json').read_text(encoding='utf-8'));rows=[];rejected=[]
for r in maps:
    c=r['component'];i=r['frame'];p=B/f'run-{c.lower()}-primary3-v001/curated/frame-{i}.png';im=Image.open(p);raw=Path(r['pre_fit_component']['path']);pre=Image.open(raw);u,v=centres[c][i];f=r['shared_fit'];w,h=f['source_component_size'];fw,fh=f['resampled_size'];ox,oy=f['placement_xy']
    x=round(ox+(u+.5)*fw/w-.5);y=round(oy+(v+.5)*fh/h-.5)
    assert im.getpixel((x,y))[3]>=128,(c,i,x,y)
    a,b=earlier[c][i];rejected.append({'component':c,'frame':i,'earlier_small_crop_estimate':[a,b],'rgba':list(im.getpixel((a,b))),'status':'Rejected/unpublished preliminary selection; too small to locate physical feature reliably. No registration or Source consumed it.'})
    rows.append({'component':c,'frame':i,'source':desc(p),'physical_feature_A_candidate':[x,y],'uncertainty_source512_px':2,'feature':{'Chest':'actual central raised boss outer-contour centre, not highlight','NearShoulder':'actual central washer dark-hole centre','FarShoulder':'actual small top-strap end rivet, not central face boss'}[c],'manual_pre_fit_component_centre':[u,v],'manual_pre_fit_uncertainty_px':3,'pre_fit_source':desc(raw),'pre_fit_pixel_rgba':list(pre.getpixel((u,v))),'fit_provenance':f,'method':'Root actually viewed all18 original512 full-component crops after E236 and all18 unscaled native pre-fit components after E237. Manual physical feature centre mapped through original fixed shared fit and sampled on actual512. No perframe rescale or repaint; uncertainty retained.','source_rgba':list(im.getpixel((x,y))),'source_cross_rgba':[{'xy':[xx,yy],'rgba':list(im.getpixel((xx,yy)))} for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]],'body_target':None,'accepted_registration':False})
p=O/'physical-feature-measurement-v001.json';p.write_text(json.dumps({'rows':rows,'rejected_preliminary_small_crop_estimates':rejected,'all18_derived_and18_native_component_views_actually_seen':True,'source_body_points_from_independent175_measurement_required':True,'registered_or_imported':False,'motion_accepted':False,'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
freeze=O/'measurement-freeze-v001.json';freeze.write_text(json.dumps({'files':[desc(p),desc(Path(__file__).resolve())],'source_body_targets_measured':False,'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'measurement':desc(p),'freeze':desc(freeze),'actual_A_candidates':[{'c':r['component'],'f':r['frame'],'A':r['physical_feature_A_candidate'],'rgba':r['source_rgba']} for r in rows]},ensure_ascii=False))
