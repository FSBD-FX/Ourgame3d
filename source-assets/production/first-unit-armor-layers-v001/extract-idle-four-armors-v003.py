"""Four real visible-surface armor selections; masks select native pixels only."""
from pathlib import Path
import importlib.util,json,math
from PIL import Image,ImageDraw,ImageChops
P=Path(__file__).resolve().parent;O=P.parent/'first-unit-animation-v003'
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
s=importlib.util.spec_from_file_location('selections',P/'extract-idle-components-v001.py');old=importlib.util.module_from_spec(s);s.loader.exec_module(old)
SHIFTS=old.SHIFTS
PRESERVE=dict(old.POLYGONS)
PRESERVE['near_forearm_hand']=[(143,306),(153,304),(165,307),(177,313),(188,319),(198,324),(205,337),(202,352),(192,365),(173,366),(163,359),(153,343),(144,329),(140,315)]
PRESERVE['far_wrist_hand_preserve']=[(309,334),(321,343),(331,353),(339,364),(337,376),(324,383),(312,379),(303,368),(300,352)]
# Polygons are hand-traced on the actual full-body sources at original512px size.
GARMENTS={
 'ARM-LGT-001':{'request':48,'parts':{
  'armor_back':[[(173,366),(184,357),(195,362),(198,390),(187,394),(173,387)]],
  'armor_far_shoulder':[[(281,257),(292,256),(303,264),(309,276),(300,290),(290,287),(284,275)]],
  'armor_torso':[[(207,254),(228,260),(271,258),(286,266),(293,283),(290,318),(287,336),(206,336),(195,321),(198,296),(208,280)]],
  'armor_front':[old.POLYGONS['armor_near_shoulder'],old.POLYGONS['armor_front_hem']]}},
 'ARM-MED-001':{'request':49,'parts':{
  'armor_back':[[(170,375),(190,357),(204,378),(201,410),(179,410),(170,399)]],
  'armor_far_shoulder':[[(278,250),(293,250),(306,258),(311,278),(302,290),(307,304),(301,311),(288,308),(282,290)]],
  'armor_torso':[[(191,248),(220,248),(249,252),(279,249),(291,268),(291,327),(282,339),(204,339),(193,320),(194,287)]],
  'armor_front':[[(146,263),(163,247),(179,244),(198,252),(210,271),(201,292),(198,306),(178,311),(147,299),(142,287)],[(196,345),(282,344),(301,389),(302,408),(262,415),(250,399),(241,413),(173,405),(173,388),(186,365)]]}},
 'ARM-HVY-001':{'request':50,'parts':{
  'armor_back':[[(169,370),(192,354),(209,367),(213,395),(198,404),(176,399),(169,389)]],
  'armor_far_shoulder':[[(277,241),(303,242),(321,256),(321,276),(313,282),(316,294),(298,306),(280,284)]],
  'armor_torso':[[(184,242),(215,242),(243,251),(276,246),(302,262),(310,300),(294,328),(281,340),(205,337),(202,318),(201,292)]],
  'armor_front':[[(135,248),(165,232),(190,231),(213,247),(216,266),(209,283),(201,293),(177,295),(133,287),(131,272)],[(194,346),(281,344),(301,375),(304,398),(279,406),(267,394),(222,397),(213,407),(173,399),(171,386)],[(178,403),(223,408),(217,441),(207,453),(168,457),(169,432)],[(250,403),(297,403),(304,448),(286,455),(257,450)]]}},
 'ARM-ROB-001':{'request':51,'parts':{
  'armor_back':[[(178,353),(193,352),(190,381),(172,443),(159,449),(149,433)]],
  'armor_far_shoulder':[[(276,252),(295,259),(303,279),(321,322),(321,334),(300,345),(289,324),(280,292)]],
  'armor_torso':[[(182,247),(211,247),(243,256),(276,252),(294,271),(298,317),(287,339),(202,339),(187,318),(181,291)]],
  'armor_front':[[(151,268),(168,251),(185,251),(205,265),(205,289),(193,306),(175,312),(138,302),(136,294)],[(195,347),(250,348),(243,451),(224,453),(170,445),(172,415),(186,368)],[(253,345),(285,346),(300,381),(315,437),(278,450),(264,432),(251,376)]]}}
}
def mask(poly,shift):
    m=Image.new('L',(512,512),0);d=ImageDraw.Draw(m)
    for p in poly:d.polygon([(x+shift[0],y+shift[1]) for x,y in p],fill=255)
    return m
def pick(im,m):return old.extract(im,m)
def save(path,im,status):
    assert not path.exists(),path
    im.save(path);r.archive(path,path.relative_to(P),status)
    a=im.getchannel('A');return {'path':str(path),'sha256':r.sha(path),'canvas':[512,512],'mode':'RGBA','alpha_extrema':list(a.getextrema()),'corner_alpha':[a.getpixel(p) for p in [(0,0),(511,0),(0,511),(511,511)]],'bbox':list(a.getbbox()) if a.getbbox() else None,'nonempty':bool(a.getbbox())}
def main():
    out=P/'components/idle-four-armors-v003';assert not out.exists() or not any(out.iterdir());out.mkdir(exist_ok=True)
    marks=r.read(O/'assembly-markers-import-v005.json');idle=next(a for a in marks['actions'] if a['action']=='idle')['frames']
    sword=Image.open(O.parent/'first-unit-animation-v003/components/military-sword-clean-v001.png').convert('RGBA')
    sheets={key:Image.new('RGBA',(1536,1024),(0,0,0,0)) for key in ['base','ARM-LGT-001','ARM-MED-001','ARM-HVY-001','ARM-ROB-001']}
    isolated={key:Image.new('RGBA',(1536,1024),(0,0,0,0)) for key in GARMENTS}
    bodies=[];armors={key:[] for key in GARMENTS}
    for i,shift in enumerate(SHIFTS):
        original=Image.open(idle[i]['frame_path']).convert('RGBA');common=Image.open(P/f'processed/call45-fixed-canvas-v002/frame-{i}.png').convert('RGBA')
        pm={name:mask([poly],shift) for name,poly in PRESERVE.items()}
        cloth=pm['clothing_replace'].copy()
        for name in ['head_preserve','near_forearm_hand','far_wrist_hand_preserve','belt_preserve','pouch_preserve']:cloth=ImageChops.subtract(cloth,pm[name])
        base=original.copy();base.paste(common,(0,0),cloth);base=pick(base,Image.new('L',(512,512),255))
        near=pick(base,pm['near_forearm_hand']);far=pick(base,ImageChops.invert(pm['near_forearm_hand']));rebuilt=far.copy();rebuilt.alpha_composite(near);assert rebuilt.tobytes()==base.tobytes()
        for name in ['head_preserve','near_forearm_hand','far_wrist_hand_preserve']:assert pick(base,pm[name]).tobytes()==pick(original,pm[name]).tobytes()
        parts={name:save(out/f'body-{name}-{i}.png',im,'frozen_head_hands_common_base_actual_native_clothing_selection') for name,im in [('common',base),('far',far),('near',near)]}
        bodies.append({'frame_index':i,'parts':parts,'root_px':idle[i]['ground_root_px'],'grip_px':idle[i]['grip_px'],'weapon_angle_image_clockwise_deg':idle[i]['weapon_angle_image_clockwise_deg'],'weapon_scale':idle[i]['weapon_scale'],'head_hands_preserved':True,'near_far_exact_reconstruction':True,'source_frozen_path':idle[i]['frame_path'],'source_frozen_sha256':idle[i]['frame_sha256']})
        sheets['base'].alpha_composite(base,((i%3)*512,(i//3)*512))
        for key,config in GARMENTS.items():
            source=Path(P/f"processed/call{config['request']}-fixed-canvas-v002/frame-{i}.png");src=Image.open(source).convert('RGBA')
            masks={name:mask(polys,shift) for name,polys in config['parts'].items()}
            for name in masks:
                for excluded in ['head_preserve','near_forearm_hand','far_wrist_hand_preserve','belt_preserve','pouch_preserve']:masks[name]=ImageChops.subtract(masks[name],pm[excluded])
            used=Image.new('L',(512,512),0)
            for name in ['armor_front','armor_torso','armor_far_shoulder','armor_back']:
                masks[name]=ImageChops.subtract(masks[name],used);used=ImageChops.lighter(used,masks[name])
            selected={name:pick(src,m) for name,m in masks.items()};records={}
            for name,im in selected.items():
                # Source RGB/A is selected verbatim; no painting or synthetic repair.
                records[name]=save(out/f'{key}-{name}-{i}.png',im,'actual_visible_armor_pixels_manual_binary_selection_candidate')
                mp=P/f'masks/{key}-idle-{name}-{i}-v003.png';assert not mp.exists();masks[name].save(mp);r.archive(mp,mp.relative_to(P),'manual_armor_surface_selection_mask')
                records[name]['mask_path']=str(mp);records[name]['mask_sha256']=r.sha(mp)
            overlay=Image.new('RGBA',(512,512),(0,0,0,0))
            for name in ['armor_back','armor_far_shoulder','armor_torso','armor_front']:overlay.alpha_composite(selected[name])
            isolated[key].alpha_composite(overlay,((i%3)*512,(i//3)*512))
            worn=Image.new('RGBA',(512,512),(0,0,0,0))
            worn.alpha_composite(selected['armor_back']);worn.alpha_composite(far)
            for name in ['armor_far_shoulder','armor_torso','armor_front']:worn.alpha_composite(selected[name])
            a=math.radians(idle[i]['weapon_angle_image_clockwise_deg']);c=math.cos(a);s=math.sin(a);gx,gy=idle[i]['grip_px'];sc=.4;sx,sy=99,256
            coeff=(c/sc,s/sc,sx-(c*gx+s*gy)/sc,-s/sc,c/sc,sy-(-s*gx+c*gy)/sc)
            worn.alpha_composite(sword.transform((512,512),Image.Transform.AFFINE,coeff,resample=Image.Resampling.BICUBIC));worn.alpha_composite(near)
            sheets[key].alpha_composite(worn,((i%3)*512,(i//3)*512))
            armors[key].append({'frame_index':i,'parts':records,'source_path':str(source),'source_sha256':r.sha(source),'source_frame_transforms':'none','manual_mask_translation_px':list(shift),'root_px':idle[i]['ground_root_px'],'grip_px':idle[i]['grip_px']})
    for key,im in sheets.items():save(P/f'reviews/idle-{key}-assembly-v003.png',im,'actual_component_assembly_candidate_pending_visual_review')
    for key,im in isolated.items():save(P/f'reviews/idle-{key}-isolated-armor-v003.png',im,'actual_selected_armor_surfaces_without_body')
    report={'schema':'armor-visible-layer-candidate-v1','version':3,'frozen':False,'identity':'EV042_round_enclosed_helmet_knight','action':'idle','frame_count':6,'canvas':[512,512],'common_body':bodies,'armors':armors,'draw_order':['armor_back','body_far','armor_far_shoulder','armor_torso','armor_front','independent_weapon','body_near'],'weapon':{'path':str(O.parent/'first-unit-animation-v003/components/military-sword-clean-v001.png'),'sha256':r.sha(O.parent/'first-unit-animation-v003/components/military-sword-clean-v001.png'),'grip_px':[99,256],'tip_px':[482,256],'scale':.4},'mirror_policy':'assemble_right_facing_once_then_one_runtime_mirror','polygons':GARMENTS,'preserve_polygons':PRESERVE,'manual_shifts':SHIFTS,'no_body_scale_or_translation':True,'true_hidden_complete_surfaces':False,'armor_back_scope':'only_source_visible_back_hem_fragment_can_be_fully_occluded_in_stack_no_synthetic_hidden_pixels','armor_front_scope':'near_shoulder_and_front_hem_plus_HVY_shin_guards','body_near_scope':'real_visible_near_forearm_wrap_and_hand_only','legal_empty_part':'if all pixels truly occluded/removed, explicit nonempty=false; no fabricated transparent layer acceptance against old4layergate','semantic_visual_review_passed':False,'runtime_verified':False,'four_armor_full_state_complete':False,'host_fee_usd':None,'external_api_calls':0}
    f=P/'manifests/idle-four-armors-candidate-v003.json';r.write(f,report);r.archive(f,f.relative_to(P),'source_and_mask_evidence_candidate_pending_visual_review')
    print({'body_frames':6,'armor_pose_sets':4,'armor_frames':24,'actual_component_pngs':len(list(out.glob('*.png'))),'runtime_verified':False})
if __name__=='__main__':main()
