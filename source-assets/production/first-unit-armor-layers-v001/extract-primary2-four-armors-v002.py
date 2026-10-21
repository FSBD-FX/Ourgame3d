"""Actual P2 armor selections, separate preserved anatomy and distal grip masking."""
from pathlib import Path
import importlib.util, math
from PIL import Image, ImageDraw, ImageChops, ImageFilter
P=Path(__file__).resolve().parent;O=P.parent/'first-unit-animation-v003'
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
s=importlib.util.spec_from_file_location('walk_util',P/'extract-walk-four-armors-v002.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
HEADS=[
 [(156,185),(165,161),(184,144),(210,136),(238,142),(267,157),(284,184),(292,215),(285,244),(273,271),(225,263),(183,250),(165,234),(156,208)],
 [(168,190),(176,168),(197,150),(226,143),(255,149),(283,166),(296,195),(299,227),(285,252),(274,278),(225,267),(186,252),(169,231)],
 [(154,166),(163,145),(183,127),(210,120),(239,126),(266,143),(282,170),(286,198),(276,223),(266,245),(221,239),(180,224),(161,205),(154,180)],
 [(173,170),(183,146),(203,129),(228,123),(256,130),(280,148),(290,178),(288,213),(276,237),(267,253),(224,247),(188,231),(174,209)],
 [(166,172),(176,146),(198,129),(225,122),(253,130),(278,147),(291,177),(290,211),(278,238),(267,254),(222,247),(185,231),(168,209)],
 [(158,169),(168,146),(190,128),(220,122),(250,129),(277,146),(289,176),(290,210),(278,238),(267,254),(219,247),(181,231),(161,210)]]
WEAPON_ARMS=[
 [(161,309),(177,307),(193,315),(207,327),(215,343),(240,350),(252,365),(255,379),(245,390),(226,394),(210,386),(201,373),(185,359),(174,344),(164,332)],
 [(124,282),(143,281),(155,293),(155,309),(157,325),(152,341),(153,350),(143,359),(124,357),(115,347),(117,330),(118,312),(120,295)],
 [(217,245),(231,238),(249,237),(267,238),(289,230),(300,219),(314,216),(328,226),(333,240),(328,253),(316,260),(300,260),(290,269),(269,275),(249,283),(227,286),(216,275)],
 [(134,171),(143,150),(157,131),(170,107),(184,96),(199,99),(210,110),(212,124),(201,137),(188,145),(179,171),(178,195),(171,218),(153,229),(140,221),(133,203)],
 [(118,207),(126,186),(141,171),(150,157),(161,150),(175,154),(185,166),(185,179),(173,188),(166,205),(163,223),(159,239),(145,253),(128,247),(118,236),(114,220)],
 [(116,256),(125,240),(138,230),(147,214),(159,208),(171,210),(183,219),(189,232),(186,244),(174,253),(163,268),(161,284),(150,296),(132,299),(118,291),(112,277)]]
WEAPON_HANDS=[
 [(180,328),(199,325),(213,337),(221,348),(239,350),(252,362),(255,377),(247,389),(230,394),(213,385),(205,373),(190,363),(180,350)],
 [(121,300),(142,299),(155,311),(156,330),(155,346),(143,359),(123,357),(114,347),(117,331)],
 [(255,240),(270,239),(289,231),(300,219),(314,216),(328,225),(333,240),(328,253),(316,260),(300,262),(285,271),(264,276),(258,263)],
 [(141,150),(155,133),(170,107),(184,96),(199,99),(210,110),(212,124),(200,137),(188,146),(179,170),(163,178),(147,171)],
 [(121,207),(131,188),(145,170),(153,157),(164,150),(177,155),(187,166),(185,179),(173,188),(166,205),(161,218),(143,221),(129,214)],
 [(119,259),(129,241),(143,227),(151,214),(164,207),(176,213),(185,222),(190,235),(184,247),(173,253),(164,266),(160,278),(143,280),(129,273)]]
OTHER_ARMS=[
 [(277,304),(291,303),(304,313),(317,322),(332,330),(343,345),(340,358),(328,368),(313,367),(301,357),(292,345),(281,333)],
 [(263,307),(280,296),(291,290),(309,282),(322,282),(333,290),(338,303),(332,318),(319,323),(309,335),(294,345),(280,343),(266,334),(259,323)],
 [(267,293),(280,289),(294,290),(305,303),(313,315),(309,329),(299,338),(283,340),(269,331),(260,318)],
 [(270,304),(286,307),(300,308),(313,319),(320,332),(318,344),(307,353),(292,352),(280,343),(272,333),(265,319)],
 [(268,285),(282,279),(295,271),(307,276),(316,286),(318,301),(311,312),(297,321),(282,318),(272,309),(266,296)],
 [(270,300),(280,292),(292,284),(307,285),(319,297),(323,312),(317,325),(301,335),(284,335),(272,325),(264,311)]]
OTHER_HANDS=[
 [(288,315),(304,311),(316,320),(331,329),(343,343),(340,357),(329,368),(314,366),(302,355),(294,343)],
 [(286,295),(302,286),(315,281),(329,285),(337,297),(337,310),(329,321),(315,324),(305,334),(293,337),(285,323)],
 [(269,303),(280,293),(295,291),(307,303),(314,316),(310,330),(299,338),(283,340),(270,331),(264,317)],
 [(274,314),(287,309),(302,310),(314,319),(321,333),(318,346),(307,354),(292,352),(280,343),(271,329)],
 [(274,290),(284,280),(297,271),(309,277),(318,290),(319,303),(312,314),(298,322),(283,319),(274,308)],
 [(275,306),(283,294),(295,284),(309,286),(320,299),(324,313),(317,326),(302,336),(285,335),(274,324)]]
BELTS=[(245,342),(231,347),(235,331),(244,326),(244,326),(243,326)]
CLOTH=[
 [(148,275),(166,255),(197,251),(226,263),(270,263),(291,280),(308,307),(303,330),(281,344),(291,367),(271,390),(237,387),(222,398),(150,388),(146,371),(157,347),(155,324),(148,307)],
 [(121,287),(142,268),(173,255),(202,256),(228,265),(264,266),(283,280),(290,304),(280,330),(265,349),(287,375),(250,398),(230,393),(217,404),(142,391),(140,372),(151,350),(151,324)],
 [(152,260),(160,241),(186,232),(215,240),(249,241),(272,250),(279,281),(282,303),(274,330),(287,365),(276,382),(237,387),(224,375),(210,390),(146,379),(142,364),(152,342),(151,313)],
 [(141,217),(158,211),(176,228),(187,245),(222,249),(259,252),(275,269),(285,295),(288,316),(278,336),(294,363),(277,385),(245,380),(232,366),(219,385),(145,372),(148,354),(163,331),(164,300),(150,273)],
 [(121,231),(139,225),(153,230),(174,238),(188,248),(219,251),(257,253),(275,269),(282,295),(287,315),(280,337),(294,365),(277,385),(244,381),(233,367),(219,384),(145,372),(150,354),(166,331),(164,301),(145,278)],
 [(136,264),(152,247),(171,242),(188,250),(217,254),(254,255),(272,270),(281,292),(287,315),(282,338),(295,366),(277,385),(245,380),(234,366),(219,384),(145,372),(150,354),(165,332),(162,306),(144,286)]]
SHORT_HEMS=[
 [(151,350),(224,352),(242,353),(272,352),(295,376),(250,397),(235,380),(219,396),(144,382)],
 [(146,354),(216,356),(233,357),(266,353),(290,375),(247,399),(232,383),(215,399),(141,387)],
 [(150,339),(220,341),(237,341),(268,339),(286,368),(250,389),(234,369),(220,388),(142,376)],
 [(154,334),(221,336),(244,337),(270,337),(295,366),(253,384),(235,366),(220,385),(147,372)],
 [(153,334),(221,336),(244,337),(270,337),(295,367),(253,385),(235,366),(220,385),(146,372)],
 [(154,334),(220,336),(243,337),(270,337),(295,366),(253,385),(235,367),(219,385),(147,372)]]
MED_HEMS=[]
for points in SHORT_HEMS:
    MED_HEMS.append([(x,y+(14 if index>=5 else 0)) for index,(x,y) in enumerate(points)])
ROB_HEMS=[]
for i,(bx,by) in enumerate(BELTS):
    ROB_HEMS.append([
        [(150,by+8),(bx-13,by+10),(bx-25,445),(151,432)],
        [(bx+2,by+9),(bx+38,by+10),(311,426),(bx+17,444)],
        [(151,by+17),(164,by+24),(130,415),(122,416)]])
HVY_LEGS=[
 [[(149,382),(172,386),(186,399),(182,413),(169,432),(154,447),(126,447),(119,438),(132,415),(137,396)],[(267,380),(289,380),(304,390),(308,405),(302,421),(306,445),(270,452),(258,435),(255,412)]],
 [[(138,388),(164,387),(183,401),(178,419),(163,435),(148,447),(119,446),(114,435),(126,412)],[(265,380),(290,380),(304,393),(308,410),(301,426),(306,447),(269,452),(258,435),(254,411)]],
 [[(148,380),(172,384),(185,397),(179,415),(167,433),(151,446),(123,445),(119,434),(132,409)],[(270,379),(292,382),(304,394),(307,411),(301,427),(307,448),(270,453),(258,436),(254,412)]],
 [[(148,386),(173,390),(185,404),(177,420),(162,436),(151,450),(122,448),(120,434),(132,411)],[(267,383),(289,382),(303,394),(306,411),(301,428),(307,448),(270,452),(258,434),(253,411)]],
 [[(147,388),(171,390),(184,403),(177,420),(163,437),(151,449),(121,448),(118,435),(131,412)],[(269,382),(291,382),(305,395),(309,411),(302,429),(308,449),(270,453),(258,435),(254,411)]],
 [[(149,387),(173,391),(185,405),(178,421),(164,437),(152,449),(124,448),(120,434),(132,412)],[(267,383),(289,382),(304,394),(307,411),(302,429),(308,449),(271,453),(258,435),(254,412)]]]


# Actual source-specific split mail panels exclude the trouser gap below the slit.
MED_PANELS=[
 [[(150,350),(220,352),(218,378),(217,397),(214,406),(146,397),(143,391)],[(239,352),(271,352),(296,377),(292,389),(251,405),(238,386)]],
 [[(146,354),(219,356),(217,382),(216,404),(147,397),(143,387)],[(235,355),(270,352),(291,376),(289,388),(252,406),(237,390)]],
 [[(150,339),(221,341),(220,385),(216,400),(145,391)],[(239,341),(268,339),(287,369),(275,385),(253,398),(237,378)]],
 [[(154,334),(221,336),(220,379),(216,395),(147,386)],[(244,337),(270,337),(295,366),(290,378),(253,396),(235,377)]],
 [[(153,334),(221,336),(220,380),(216,396),(146,386)],[(244,337),(270,337),(295,367),(290,379),(253,396),(235,378)]],
 [[(154,334),(220,336),(219,380),(215,396),(147,386)],[(243,337),(270,337),(295,366),(290,379),(253,396),(235,378)]]]

def masks_for(i):
    bx,by=BELTS[i]
    return {name:w.poly(points) for name,points in {
        'head':HEADS[i],'weapon_forearm':WEAPON_ARMS[i],'other_forearm':OTHER_ARMS[i],
        'weapon_hand':WEAPON_HANDS[i],'other_hand':OTHER_HANDS[i],'cloth':CLOTH[i],
        'belt':[(bx-91,by-16),(bx+32,by-17),(bx+35,by+9),(bx+16,by+21),(bx-91,by+14)],
        'pouch':[(bx-91,by-9),(bx-39,by-8),(bx-35,by+8),(bx-48,by+32),(bx-93,by+24)]}.items()}

def main():
    out=P/'components/primary2-four-armors-v002';assert not out.exists();out.mkdir()
    marks=next(a for a in r.read(O/'assembly-markers-import-v005.json')['actions'] if a['action']=='primary_2')['frames']
    sheets={name:Image.new('RGBA',(1536,1024),(0,0,0,0)) for name in ['base','body_near']}
    for key in ['LGT','MED','HVY','ROB']:
        sheets[key+'_isolated']=Image.new('RGBA',(1536,1024),(0,0,0,0));sheets[key+'_sword']=sheets[key+'_isolated'].copy()
    sword=Image.open(O.parent/'first-unit-animation-v002/components/military-sword-clean-v001.png').convert('RGBA')
    bodies=[];armors={f'ARM-{k}-001':[] for k in ['LGT','MED','HVY','ROB']}
    for i,m in enumerate(marks):
        original=Image.open(m['frame_path']).convert('RGBA');native=Image.open(P/f'processed/call62-fixed-canvas-v002/frame-{i}.png').convert('RGBA')
        masks=masks_for(i);base=native.copy()
        for name in ['head','weapon_forearm','other_forearm','weapon_hand','other_hand','belt','pouch']:base.paste(original,(0,0),masks[name])
        lower=Image.new('L',(512,512),0);ImageDraw.Draw(lower).rectangle((0,410,511,511),fill=255);base.paste(original,(0,0),lower)
        base=w.sel.extract(base,Image.new('L',(512,512),255));near=w.sel.extract(base,masks['weapon_hand']);far=w.sel.extract(base,ImageChops.invert(masks['weapon_hand']))
        reconstructed=far.copy();reconstructed.alpha_composite(near);assert reconstructed.tobytes()==base.tobytes()
        for name in ['head','weapon_forearm','other_forearm','weapon_hand','other_hand']:assert w.sel.extract(base,masks[name]).tobytes()==w.sel.extract(original,masks[name]).tobytes()
        assert base.getpixel(tuple(m['grip_px']))==original.getpixel(tuple(m['grip_px']))
        parts={name:w.save(im,out/f'{name}-{i}.png','actual_P2_shared_body_distal_grip_candidate') for name,im in [('base_common',base),('body_far',far),('body_near',near)]}
        bodies.append({'index':i,'parts':parts,'root_px':m['ground_root_px'],'grip_px':m['grip_px'],'weapon_angle_image_clockwise_deg':m['weapon_angle_image_clockwise_deg'],
            'source_original_path':m['frame_path'],'source_original_sha256':m['frame_sha256'],
            'source_common_path':str(P/f'processed/call62-fixed-canvas-v002/frame-{i}.png'),'source_common_sha256':r.sha(P/f'processed/call62-fixed-canvas-v002/frame-{i}.png'),
            'exact_body_far_near_reconstruction':True,'original_traced_anatomy_preserved':True,'near_scope':'visible_distal_wrist_wrap_and_empty_gripping_fist_not_entire_forearm'})
        for name,im in [('base',base),('body_near',near)]:sheets[name].alpha_composite(im,((i%3)*512,(i//3)*512))
        for name,mask in masks.items():
            path=P/f'masks/primary2-{name}-{i}-v002.png';mask.save(path);r.archive(path,path.relative_to(P),'manual_P2_original_anatomy_and_clothing_trace')
        for key,request in [('LGT',63),('MED',64),('HVY',65),('ROB',66)]:
            source_path=P/f'processed/call{request}-fixed-canvas-v002/frame-{i}.png';source=Image.open(source_path).convert('RGBA')
            limit=Image.new('L',(512,512),0);ImageDraw.Draw(limit).rectangle((0,0,511,BELTS[i][1]+12),fill=255)
            q=ImageChops.darker(masks['cloth'],limit)
            q=ImageChops.lighter(q,w.union(ROB_HEMS[i] if key=='ROB' else MED_PANELS[i] if key=='MED' else [SHORT_HEMS[i]]))
            if key=='HVY':q=ImageChops.lighter(q,w.union(HVY_LEGS[i]))
            if key=='ROB':
                for name in ['weapon_forearm','other_forearm']:q=ImageChops.lighter(q,masks[name])
            exclusions=['head','weapon_hand','other_hand','belt','pouch']+([] if key=='ROB' else ['weapon_forearm','other_forearm'])
            for name in exclusions:
                exclusion=masks[name].filter(ImageFilter.MaxFilter(7)) if name in ['weapon_forearm','other_forearm','weapon_hand','other_hand'] else masks[name]
                q=ImageChops.subtract(q,exclusion)
            guard=ImageChops.lighter(masks['weapon_forearm'],masks['other_forearm']).filter(ImageFilter.MaxFilter(13))
            sp=source.load();px=q.load();gp=guard.load()
            for yy in range(512):
                for xx in range(512):
                    rr,gg,bb,aa=sp[xx,yy]
                    skin=gp[xx,yy] and rr>200 and gg>145 and bb>80 and rr>gg*1.15 and gg>bb*1.22
                    blue=(gg>=rr+8 and bb>=gg+5) or (key=='ROB' and gp[xx,yy] and gg>=rr*1.03 and bb>=gg*.91)
                    if px[xx,yy] and (skin or blue):px[xx,yy]=0
            pruned=w.prune_tiny(q,source);armor=w.sel.extract(source,q)
            assert all(a==b for a,b in zip(armor.get_flattened_data(),source.get_flattened_data()) if a[3])
            for name in ['head','weapon_hand','other_hand','belt','pouch']:assert ImageChops.multiply(armor.getchannel('A'),masks[name]).getbbox() is None
            part=w.save(armor,out/f'ARM-{key}-001-armor-front-{i}.png','actual_P2_native_visible_garment_candidate_pending_review')
            mp=P/f'masks/primary2-ARM-{key}-001-front-{i}-v002.png';q.save(mp);r.archive(mp,mp.relative_to(P),'manual_P2_garment_source_selection_mask')
            preview=far.copy();preview.alpha_composite(armor);angle=math.radians(m['weapon_angle_image_clockwise_deg']);co=math.cos(angle);si=math.sin(angle);gx,gy=m['grip_px'];scale=.4
            preview.alpha_composite(sword.transform((512,512),Image.Transform.AFFINE,(co/scale,si/scale,99-(co*gx+si*gy)/scale,-si/scale,co/scale,256-(-si*gx+co*gy)/scale),resample=Image.Resampling.BICUBIC));preview.alpha_composite(near)
            sheets[key+'_isolated'].alpha_composite(armor,((i%3)*512,(i//3)*512));sheets[key+'_sword'].alpha_composite(preview,((i%3)*512,(i//3)*512))
            armors[f'ARM-{key}-001'].append({'index':i,'armor_front':part,'armor_back':None,'armor_back_visibility':'actual_visible_surfaces_front_overlay_only_no_hidden_back_invented',
                'source_path':str(source_path),'source_sha256':r.sha(source_path),'mask_path':str(mp),'mask_sha256':r.sha(mp),
                'root_px':m['ground_root_px'],'grip_px':m['grip_px'],'visible_RGBA_equals_source':True,'pruned_detached_fragment_sizes':pruned})
    for name,im in sheets.items():
        path=P/f'reviews/primary2-{name}-selection-v002.png';im.save(path);r.archive(path,path.relative_to(P),'actual_P2_layer_and_sword_review_pending')
    path=P/'manifests/primary2-four-armors-candidate-v002.json'
    r.write(path,{'schema':'manual-action-visible-layer-candidate-v1','clip':'primary_2','canvas':[512,512],'common_body':bodies,'armors':armors,
        'phase_seconds':[.15,.12,.27],'phase_frames':[2,2,2],'source_requests':[62,63,64,65,66],
        'draw_order':['body_far','armor_front','independent_weapon','body_near'],'no_body_geometry_transform':True,'source_pixels_only_no_paint':True,
        'near_scope':'actual_visible_distal_wrap_and_gripping_fist; preserved_full_forearms_are_in_far_except_this_selection',
        'robe_scope':'actual_native_gray_sleeve_surface_may_cover_preserved_bare_forearm_in_far; source_wrap_material_excluded',
        'semantic_visual_review_passed':False,'runtime_verified':False,'complete_armor':False,
        'limitations':['Native robe changes cuff position in raised poses; source-specific wrap material removed within traced arm zones. Actual sleeve/old wrist seam remains a candidate limitation, not complete clothing acceptance.',
            'Selected visible surfaces are front-only; hidden full garment and old four-layer validator pass are not asserted.',
            'No clip transition,20-combination,mirror or running layered appearance acceptance.']})
    r.archive(path,path.relative_to(P),'P2_actual_source_selection_candidate_pending_semantic_review')
    print({'real_body_PNGs':18,'real_armor_PNGs':24,'runtime_new_PNGs_if_frozen':36,'semantic_review_pending':True})

if __name__=='__main__':main()
