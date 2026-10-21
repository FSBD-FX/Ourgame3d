"""Manual same-pose native garment selections, no geometry/skin edits or engine work."""
from pathlib import Path
import importlib.util,math
from PIL import Image,ImageDraw,ImageChops,ImageFilter,ImageOps
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('rec',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
def poly(points):
 m=Image.new('L',(512,512));ImageDraw.Draw(m).polygon(points,fill=255);return m
def union(polys):
 m=Image.new('L',(512,512));dr=ImageDraw.Draw(m)
 for p in polys:dr.polygon(p,fill=255)
 return m
def extract(im,m):
 a=im.copy();a.putalpha(ImageChops.multiply(im.getchannel('A'),m));a.putdata([p if p[3]else(0,0,0,0)for p in a.get_flattened_data()]);return a
def save(im,q,status):
 q.parent.mkdir(parents=True,exist_ok=True);assert not q.exists();im.save(q);r.archive(q,q.relative_to(P),status)
 return {'path':str(q),'sha256':r.sha(q),'canvas_px':list(im.size),'mode':im.mode,'alpha_extrema':list(im.getchannel('A').getextrema()),'bbox_px':list(im.getchannel('A').getbbox()),'corner_alpha':[im.getpixel(p)[3]for p in[(0,0),(511,0),(0,511),(511,511)]]}
def main():
 cp=P/'manifests/import-XBW-common-walk-v001.json';base=r.read(cp);assert r.sha(cp)=='7185df2ad077ec92d020788f84f2f9b890dc7d042ceb7656d0a9576177d471a5'
 rows={f'ARM-{k}-001':[]for k in['LGT','MED','HVY','ROB']};sheets={(k,n):Image.new('RGBA',(1536,1024))for k in['LGT','MED','HVY','ROB']for n in['armor_far','armor_near','native_selected','assembled_right','assembled_left']}
 # Coordinates measured on the first exact native pose; upper-body offsets follow actual original grasp motion.
 head=[(169,116),(258,108),(305,144),(315,191),(305,239),(280,254),(212,244),(178,225),(165,181)]
 upper=[(152,237),(177,230),(215,242),(280,242),(309,254),(329,278),(342,309),(331,325),(292,335),(282,347),(187,347),(161,326),(150,300)]
 neararea=[(145,235),(184,229),(210,244),(225,269),(222,292),(218,318),(201,333),(170,326),(149,306)]
 bare=[(158,275),(180,277),(193,290),(189,312),(170,310),(158,300)]
 belt=[[(185,316),(225,317),(280,315),(291,326),(285,341),(228,340),(219,337),(187,337)],[(187,330),(210,328),(232,332),(230,354),(220,367),(183,365),(179,349)]]
 shins=[
  [[(172,383),(211,382),(214,410),(200,426),(166,425)],[(256,384),(301,382),(306,425),(267,431)]],
  [[(185,369),(221,385),(214,401),(199,412),(161,394),(174,379)],[(255,377),(296,377),(305,418),(268,426)]],
  [[(188,372),(215,376),(234,388),(217,405),(203,413),(183,395)],[(262,382),(302,382),(308,427),(268,433)]],
  [[(195,380),(223,382),(241,397),(224,414),(210,421),(191,404)],[(267,389),(308,386),(314,429),(274,434)]],
  [[(194,359),(230,365),(248,379),(233,392),(211,396),(189,381)],[(287,373),(315,370),(337,403),(321,418),(296,424),(274,392)]],
  [[(161,384),(203,382),(210,423),(165,432)],[(253,385),(294,385),(301,427),(260,433)]]]
 for i,f in enumerate(base['frames']):
  g=f['primary_grip_px'];dx=g[0]-base['frames'][0]['primary_grip_px'][0];dy=g[1]-base['frames'][0]['primary_grip_px'][1]
  def shifted(p):return [(x+dx,y+dy)for x,y in p]
  hand=Image.open(f['body_near']['path']).convert('RGBA');support=Image.open(f['body_support']['path']).convert('RGBA');farbody=Image.open(f['body_far']['path']).convert('RGBA');body=Image.open(f['source_body_path']).convert('RGBA')
  # Protect the actual original distal hand/wrist tracks, plus blue wraps visible in the original body.
  blue=Image.new('L',(512,512));blue.putdata([255 if p[3]and p[2]>p[1]*1.035 and p[1]>p[0]*1.03 and ((g[0]-65<=j%512<=g[0]+25 and g[1]-35<=j//512<=g[1]+30)or(f['support_grip_px'][0]-40<=j%512<=f['support_grip_px'][0]+25 and f['support_grip_px'][1]-35<=j//512<=f['support_grip_px'][1]+30)) else 0 for j,p in enumerate(body.get_flattened_data())])
  anatomy=ImageChops.lighter(hand.getchannel('A'),support.getchannel('A'))
  protection=ImageChops.lighter(poly(shifted(head)),ImageChops.lighter(union([shifted(p)for p in belt]),ImageChops.lighter(anatomy,blue))).point(lambda v:255 if v else 0).filter(ImageFilter.MaxFilter(5))
  narea=poly(shifted(neararea));baremask=poly(shifted(bare)).filter(ImageFilter.MaxFilter(5))
  state=next(s for s in f['weapon_state_mappings']if s['state_index']==3);a,b,c,d,e,ff=state['component_to_body_affine_2x3'];det=a*e-b*d;inv=(e/det,-b/det,(b*ff-e*c)/det,-d/det,a/det,(d*c-a*ff)/det)
  weapon=Image.open(state['path']).convert('RGBA').transform((512,512),Image.Transform.AFFINE,inv,resample=Image.Resampling.BICUBIC)
  for key,num in [('LGT',118),('MED',119),('HVY',120),('ROB',121)]:
   src=P/f'processed/call{num}-fixed-canvas-v001/frame-{i}.png';native=Image.open(src).convert('RGBA')
   if key=='ROB':hems=[[(182,337),(250,337),(234,425),(170,417),(151,409)],[(264,338),(289,336),(325,413),(273,425),(256,368)]]
   elif key=='MED':hems=[[(182,338),(249,339),(238,380),(218,392),(170,383)],[(262,338),(288,337),(310,378),(275,393),(254,372)]]
   elif key=='HVY':hems=[[(183,338),(288,336),(310,371),(283,384),(254,376),(235,385),(176,371)],*shins[i]]
   else:hems=[[(182,338),(249,339),(238,371),(209,379),(176,367)],[(262,338),(288,337),(305,370),(275,378),(254,360)]]
   robe_hems=[
    [[(184,337),(250,337),(236,424),(170,416),(153,408)],[(263,337),(289,336),(324,412),(275,424),(257,367)]],
    [[(188,337),(250,337),(242,368),(220,418),(154,397),(171,373)],[(263,336),(287,335),(318,409),(275,417),(256,365)]],
    [[(188,337),(243,337),(237,368),(222,417),(178,397),(179,371)],[(181,340),(189,346),(168,378),(161,373)],[(255,337),(280,336),(307,409),(272,417),(252,367)]],
    [[(198,340),(258,338),(248,376),(232,418),(188,397),(187,374)],[(190,343),(197,351),(174,379),(168,375)],[(272,338),(295,338),(322,410),(282,418),(266,366)]],
    [[(200,337),(265,339),(257,371),(241,409),(188,391),(205,356)],[(276,336),(294,335),(337,384),(307,393),(269,356)]],
    [[(182,341),(243,341),(227,428),(168,416),(173,385)],[(170,351),(182,345),(153,411),(145,410)],[(256,339),(281,337),(315,418),(269,430),(250,369)]]]
   # Shin coordinates were individually measured in their own cells; upper/hem use the small actual body offset.
   hp=robe_hems[i] if key=='ROB' else ([shifted(p)for p in hems[:1]]+shins[i] if key=='HVY' else [shifted(p)for p in hems])
   selection=ImageChops.subtract(ImageChops.lighter(poly(shifted(upper)),union(hp)),protection);mp=selection.load();sp=native.load();bm=baremask.load()
   for y in range(512):
    for x in range(512):
     rr,gg,bb,aa=sp[x,y]
     if mp[x,y]and aa and((rr>gg+30 and bb>gg+30)or(rr<gg*.97 and bb>gg*.90 and ((g[0]-47<=x<=g[0]-15 and g[1]-18<=y<=g[1]+15)or(f['support_grip_px'][0]-34<=x<=f['support_grip_px'][0]-12 and f['support_grip_px'][1]-16<=y<=f['support_grip_px'][1]+20)))or(key!='ROB'and bm[x,y])):mp[x,y]=0
   selected=extract(native,selection);near=extract(native,ImageChops.darker(selection,narea));far=extract(native,ImageChops.subtract(selection,narea));check=far.copy();check.alpha_composite(near);assert check.tobytes()==selected.tobytes()
   assert not ImageChops.multiply(selected.getchannel('A'),protection).getbbox();assert all(a==b for a,b in zip(selected.get_flattened_data(),native.get_flattened_data())if a[3])
   parts={name:save(im,P/f'components/XBW-walk-four-armors-v004/ARM-{key}-001-{name}-{i}.png','actual_same_pose_native_clothing_surface_candidate_no_anatomy_repaint')for name,im in[('armor_far',far),('armor_near',near)]};masks={}
   for name,im in[('garment',selection),('near',narea),('protected',protection)]:
    q=P/f'masks/XBW-walk-ARM-{key}-001-{name}-{i}-v004.png';q.parent.mkdir(exist_ok=True);im.save(q);r.archive(q,q.relative_to(P),'actual_manual_garment_boundary_mask');masks[name]={'path':str(q),'sha256':r.sha(q)}
   assembled=farbody.copy();assembled.alpha_composite(far);assembled.alpha_composite(weapon);assembled.alpha_composite(support);assembled.alpha_composite(near);assembled.alpha_composite(hand)
   for name,im in[('armor_far',far),('armor_near',near),('native_selected',selected),('assembled_right',assembled),('assembled_left',ImageOps.mirror(assembled))]:sheets[(key,name)].alpha_composite(im,((i%3)*512,(i//3)*512))
   rows[f'ARM-{key}-001'].append({'index':i,**parts,'armor_hidden_back':None,'hidden_back_policy':'visible_back_only_in_actual_far_unseen_null','root_px':[256,472],'primary_grip_px':f['primary_grip_px'],'support_grip_px':f['support_grip_px'],'source_path':str(src),'source_sha256':r.sha(src),'selection_masks':masks,'source_pixels_only':True,'body_geometry_transform':'none_relative_to_frozen_common_walk','armor_geometry_transform':'none_native512_cell_selection','phase':'walk','time_start_s':f['time_start_s'],'time_end_s':f['time_end_s'],'runtime_verified':False,'semantic_full_armor_acceptance':False})
 previews=[]
 for(key,name),im in sheets.items():
  q=P/f'reviews/XBW-walk-ARM-{key}-001-{name}-selection-v004.png';save(im,q,'static_walk_armor_both_direction_review_not_runtime_contact_acceptance');previews.append({'armor_id':f'ARM-{key}-001','kind':name,'path':str(q),'sha256':r.sha(q)})
 q=P/'manifests/XBW-walk-four-armors-selection-candidate-v004.json';r.write(q,{'schema':'XBW-pose-specific-armor-source-candidate-v1','clip':'walk','source_body_contract_path':str(cp),'source_body_contract_sha256':r.sha(cp),'common_body':base['frames'],'frame_count':6,'canvas_px':[512,512],'armors':rows,'previews':previews,'draw_order':['body_far','armor_far','independent_weapon','body_support','armor_near','body_near'],'source_requests':[118,119,120,121],'armor_texture_count_new':48,'common_body_texture_count_reused':18,'runtime_verified':False,'semantic_full_armor_acceptance':False});r.archive(q,q.relative_to(P),'walk_armor_actual_native_pixel_selection_candidate')
 print({'candidate':str(q),'sha256':r.sha(q),'new_armor_PNGs':48})
if __name__=='__main__':main()
