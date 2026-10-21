"""Four mechanical states as source-art/geometry reference only, not final art."""
from pathlib import Path
import importlib.util,math,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
source=P/'references/XBW-ready-assembled-cell0-v001.png';base=Image.open(source).convert('RGBA')
a=math.radians(-5);co=math.cos(a);si=math.sin(a)
def point(p):
    x=p[0]-128;y=p[1]-253;return[224+.48*(co*x-si*y),316+.48*(si*x+co*y)]
tips=[point([384,148]),point([385,324])];rest=point([384,236]);latch=point([245,236]);outlet=point([489,224])
states=[('grasp relaxed string',rest,rest,False),('drawn string at rear latch',latch,latch,False),('lay one bolt in rail',[312,286],latch,True),('return trigger',[224,316],latch,True)]
sheet=Image.new('RGB',(1024,1024),(255,0,255));d=ImageDraw.Draw(sheet);rows=[]
for i,(name,hand,apex,bolt) in enumerate(states):
    im=base.copy();di=ImageDraw.Draw(im);di.line([tuple(tips[0]),tuple(apex),tuple(tips[1])],fill='cyan',width=3)
    if bolt:di.line((latch[0]+3,latch[1]-5,outlet[0]-8,outlet[1]-4),fill='yellow',width=3)
    for p,c in [(hand,'red'),([325,321],'lime')]:di.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),outline=c,width=2)
    di.text((15,25),f'{i} {name}',fill='white');di.text((15,40),f'near({hand[0]:.1f},{hand[1]:.1f}) support(325,321)',fill='white')
    sheet.paste(im,((i%2)*512,(i//2)*512),im)
    rows.append({'keypose':i,'name':name,'near_hand_contact_body_px':hand,'support_hand_contact_body_px':[325,321],
      'string_limb_tip_body_px':tips,'string_apex_body_px':apex,'one_bolt_seated':bolt,'actual_output_required':'native image art plus physical contact review; geometry alone not final art'})
q=P/'references/XBW-direct-string-four-keypose-geometry-v001.png';assert not q.exists();sheet.save(q);r.archive(q,q.relative_to(P),'four_mechanical_keypose_source_shape_and_contact_guide_not_runtime_art')
j=q.with_suffix('.json');r.write(j,{'schema':'direct-string-reload-layout-reference-v1','source':str(source),'source_sha256':r.sha(source),'guide':str(q),'guide_sha256':r.sha(q),
 'states':rows,'background_original_deep_string_remains_in_reference_only':True,'planned_cyan_path_is_geometry_not_raw_art':True,
 'sidepiece_cocking_role_retracted':True,'mechanical_route':'direct string draw rear latch single bolt return grip','source_body_geometry_changed':False,
 'no_runtime_asset_created':True});r.archive(j,j.relative_to(P),'mechanical_guide_provenance_and_inference_boundaries');print(q)
