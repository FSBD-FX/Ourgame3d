"""Existing reviewed sources in exact512cells; no body pixels fabricated."""
from pathlib import Path
import importlib.util,shutil
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
paths=[P/'processed/call86-single-keypose-v001/keypose-canonical512.png',P/'processed/call87-single-keypose-v001/keypose-canonical512.png',
 P/'decomposition-trials/loading-shared-panel-v002/loading-composite-reference.png',P/'processed/call89-single-keypose-v001/keypose-canonical512.png']
sheet=Image.new('RGB',(1024,1024),(255,0,255));rows=[]
for i,path in enumerate(paths):
 im=Image.open(path).convert('RGBA');assert im.size==(512,512);sheet.paste(im,((i%2)*512,(i//2)*512),im);rows.append({'index':i,'path':str(path),'sha256':r.sha(path),'placement':[i%2*512,i//2*512],'geometry_transform':'none'})
q=P/'references/XBW-four-mechanical-keypose-guide-v002.png';assert not q.exists();sheet.save(q);r.archive(q,q.relative_to(P),'actual_native4pose_structure_guide_no_creative_code_art')
original=P/'processed/call81-fixed-canvas-v001/frame-0.png';body=P/'references/XBW-ready-body-cell0-v001.png';assert not body.exists();shutil.copy2(original,body);r.archive(body,body.relative_to(P),'immutable_original81_body_identity_and_original_plain_wrists_reference')
j=q.with_suffix('.json');r.write(j,{'guide':str(q),'sha256':r.sha(q),'canvas':[1024,1024],'grid':[2,2],'rows':rows,
 'original_body':str(body),'original_body_sha256':r.sha(body),'original_body_source':str(original),'creative_art_added':False,
 'derived_loading_state_declared_not_raw90':True,'requested_native_edit':'remove weapon and natively inpaint hidden body; preserve the4actual poses and original81identity'})
r.archive(j,j.relative_to(P),'body_only_native_edit_reference_provenance');print(q);print(body)
