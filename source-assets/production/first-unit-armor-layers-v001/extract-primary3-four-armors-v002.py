"""Actual P3 armor selections, separate preserved anatomy and distal grip masking."""
from pathlib import Path
import importlib.util, math
from PIL import Image, ImageDraw, ImageChops, ImageFilter
P=Path(__file__).resolve().parent;O=P.parent/'first-unit-animation-v003'
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
s=importlib.util.spec_from_file_location('walk_util',P/'extract-walk-four-armors-v002.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)

HEADS=[
 [(185,179),(193,157),(214,141),(242,134),(271,140),(299,156),(315,184),(320,215),(310,245),(297,275),(252,264),(209,247),(188,225)],
 [(178,184),(186,160),(207,142),(235,136),(263,143),(290,159),(307,186),(313,219),(301,248),(289,277),(241,265),(201,248),(181,225)],
 [(171,202),(180,179),(199,163),(225,154),(254,162),(282,177),(302,204),(307,236),(295,265),(280,295),(234,281),(196,261),(177,239)],
 [(187,206),(198,181),(218,166),(247,159),(279,166),(307,184),(324,209),(329,241),(316,271),(301,303),(257,291),(215,270),(194,248)],
 [(183,181),(192,156),(214,140),(244,132),(272,140),(300,157),(317,184),(324,216),(312,246),(300,276),(251,264),(212,246),(192,226)],
 [(164,185),(174,161),(197,144),(227,137),(256,144),(283,160),(301,188),(306,219),(295,251),(281,282),(234,270),(194,251),(173,230)]]
WEAPON_ARMS=[
 [(128,214),(138,196),(150,189),(166,175),(178,167),(193,167),(204,177),(209,190),(203,203),(192,211),(179,219),(169,234),(155,250),(144,252),(130,240),(125,226)],
 [(125,181),(134,164),(146,148),(157,134),(168,124),(183,123),(197,132),(204,144),(201,155),(189,163),(178,180),(169,201),(168,220),(151,236),(136,234),(128,218),(124,199)],
 [(184,319),(200,314),(216,323),(231,339),(239,350),(251,365),(270,374),(280,388),(280,404),(270,415),(251,419),(234,411),(229,395),(216,384),(205,369),(195,355),(186,340)],
 [(224,340),(241,330),(255,339),(269,356),(280,371),(297,382),(311,383),(323,398),(322,415),(311,426),(290,426),(277,417),(268,401),(251,386),(237,373),(228,357)],
 [(119,264),(130,257),(144,261),(156,272),(164,284),(171,293),(187,304),(194,316),(192,329),(183,340),(167,343),(151,335),(140,321),(130,309),(121,296),(115,279)],
 [(118,297),(131,288),(145,291),(160,304),(166,319),(180,329),(188,342),(188,356),(181,366),(166,371),(150,366),(139,353),(130,339),(121,326),(115,310)]]
WEAPON_HANDS=[
 [(136,213),(146,198),(159,190),(170,176),(180,166),(194,168),(205,180),(209,192),(201,204),(190,211),(178,220),(168,230),(151,230)],
 [(133,169),(145,151),(158,135),(168,124),(183,123),(198,133),(204,145),(200,156),(189,164),(179,180),(165,190),(145,183)],
 [(214,354),(231,348),(245,356),(254,369),(270,375),(280,389),(281,403),(271,415),(253,419),(236,412),(229,397),(216,384),(211,368)],
 [(254,368),(268,358),(281,367),(292,380),(310,383),(323,398),(323,415),(311,426),(292,426),(278,417),(270,402),(256,391),(248,379)],
 [(128,281),(142,277),(158,284),(170,296),(186,304),(194,317),(191,330),(182,341),(166,343),(151,334),(144,322),(131,312),(125,297)],
 [(127,309),(141,305),(155,312),(166,324),(181,329),(190,343),(188,356),(180,368),(165,372),(149,367),(141,354),(131,340),(123,324)]]
OTHER_ARMS=[
 [(282,305),(296,305),(311,315),(329,317),(342,325),(352,337),(351,350),(343,360),(328,365),(312,360),(299,350),(291,337),(279,323)],
 [(278,303),(293,304),(309,314),(324,317),(336,326),(345,339),(344,352),(333,362),(316,362),(304,353),(293,340),(281,326)],
 [(258,317),(273,307),(289,312),(303,320),(312,334),(314,348),(304,359),(288,363),(273,354),(263,341),(256,327)],
 [(139,275),(151,264),(165,266),(177,276),(180,292),(174,308),(162,318),(146,319),(136,310),(132,294)],
 [(281,311),(296,311),(311,320),(332,326),(346,338),(355,350),(354,364),(344,374),(328,374),(313,364),(302,350),(289,335),(277,322)],
 [(277,321),(290,321),(305,331),(321,338),(336,345),(346,356),(346,369),(337,378),(321,379),(307,370),(295,357),(282,342),(272,328)]]
OTHER_HANDS=[
 [(296,314),(309,310),(328,316),(341,325),(352,337),(351,351),(342,361),(328,366),(312,359),(302,349),(294,334)],
 [(290,315),(305,310),(322,315),(336,326),(345,339),(344,352),(333,363),(316,363),(304,352),(295,338)],
 [(266,321),(277,314),(292,315),(304,324),(313,337),(314,350),(303,360),(289,364),(275,356),(264,343)],
 [(136,279),(147,274),(161,282),(168,295),(161,311),(149,317),(139,310),(133,296)],
 [(294,320),(308,314),(327,324),(342,336),(354,349),(354,363),(344,375),(329,375),(314,365),(304,350),(293,336)],
 [(289,332),(303,327),(318,335),(335,344),(346,356),(346,370),(336,379),(321,380),(307,371),(296,357),(286,342)]]
BELTS=[(239,340),(231,341),(202,357),(216,354),(241,335),(237,344)]
CLOTH=[
 [(137,238),(158,223),(180,226),(206,244),(240,263),(279,269),(297,286),(313,312),(303,333),(274,347),(291,371),(251,390),(234,374),(218,395),(148,380),(143,364),(155,341),(158,313),(150,281)],
 [(136,225),(153,214),(175,226),(197,247),(230,265),(274,271),(294,285),(309,311),(300,332),(271,349),(290,374),(249,393),(230,376),(214,395),(141,381),(136,363),(151,339),(155,307),(141,277)],
 [(145,286),(154,268),(175,255),(196,262),(219,282),(247,291),(271,294),(281,309),(280,330),(264,349),(265,369),(281,397),(247,409),(211,397),(200,412),(127,391),(123,376),(137,352),(138,326)],
 [(142,281),(160,260),(185,249),(210,264),(235,283),(261,300),(277,319),(281,342),(265,361),(263,381),(276,403),(240,413),(208,399),(193,411),(124,393),(119,379),(133,355),(133,328),(139,303)],
 [(119,264),(133,242),(158,226),(180,230),(199,245),(228,261),(272,268),(291,284),(309,309),(304,333),(275,347),(292,373),(252,390),(235,375),(219,392),(146,380),(141,362),(154,339),(153,309),(132,286)],
 [(117,302),(125,279),(141,261),(162,249),(182,250),(200,262),(227,277),(270,281),(287,295),(301,316),(295,339),(274,353),(293,381),(250,397),(234,382),(217,398),(141,386),(136,368),(150,345),(145,324)]]
SHORT_HEMS=[
 [(149,348),(218,349),(238,351),(270,348),(291,371),(253,393),(236,374),(220,393),(144,379)],
 [(143,349),(211,350),(230,352),(267,349),(288,373),(251,395),(232,376),(216,394),(139,381)],
 [(129,364),(189,367),(208,370),(246,367),(269,393),(232,411),(211,391),(197,411),(121,391)],
 [(127,362),(190,365),(216,369),(251,368),(275,397),(238,414),(211,394),(193,414),(118,391)],
 [(150,343),(218,344),(240,346),(270,344),(291,370),(254,391),(237,373),(221,392),(144,378)],
 [(143,352),(212,353),(236,355),(268,352),(291,380),(254,398),(236,380),(218,398),(136,387)]]
MED_PANELS=[
 [[(149,348),(219,349),(218,378),(215,405),(143,394)],[(239,351),(270,348),(291,371),(286,386),(254,405),(236,385)]],
 [[(143,349),(212,350),(214,381),(211,407),(138,397)],[(231,352),(267,349),(288,373),(283,389),(252,408),(231,386)]],
 [[(129,364),(192,367),(198,396),(194,424),(119,407)],[(209,370),(246,367),(270,393),(260,410),(232,426),(211,404)]],
 [[(127,362),(193,365),(194,397),(188,425),(117,407)],[(217,369),(251,368),(275,397),(263,413),(240,428),(211,408)]],
 [[(150,343),(219,344),(218,377),(214,403),(143,393)],[(241,346),(270,344),(291,370),(285,385),(255,404),(236,384)]],
 [[(143,352),(213,353),(214,387),(210,411),(135,402)],[(237,355),(268,352),(291,380),(285,393),(255,412),(236,391)]]]
ROB_HEMS=[
 [[(149,348),(228,350),(205,446),(135,429)],[(243,350),(270,348),(316,415),(258,436)],[(147,359),(161,367),(119,414),(111,411)]],
 [[(143,350),(220,352),(203,450),(133,432)],[(234,351),(267,349),(310,418),(253,439)],[(141,360),(155,366),(115,415),(107,413)]],
 [[(127,365),(198,368),(181,452),(112,433)],[(215,371),(246,367),(298,431),(242,451)],[(126,374),(137,381),(101,420),(94,416)]],
 [[(124,364),(192,368),(179,451),(105,433)],[(219,370),(251,368),(303,429),(247,449)],[(123,373),(136,381),(97,424),(90,419)]],
 [[(148,343),(230,345),(214,448),(140,430)],[(244,347),(270,344),(313,418),(262,442)],[(146,355),(160,364),(119,414),(111,411)]],
 [[(141,353),(226,355),(209,451),(134,434)],[(240,356),(268,352),(313,425),(259,447)],[(139,365),(154,373),(114,421),(106,417)]]]
HVY_LEGS=[
 [[(137,390),(176,401),(166,427),(147,449),(117,447),(119,430)],[(253,401),(299,397),(307,446),(270,454),(256,436)]],
 [[(128,390),(168,402),(157,430),(143,449),(108,448),(113,429)],[(251,402),(296,397),(305,446),(267,454),(253,436)]],
 [[(110,392),(151,403),(140,430),(121,450),(91,447),(96,429)],[(243,405),(287,402),(298,447),(261,454),(248,437)]],
 [[(110,393),(150,406),(137,432),(119,451),(87,449),(94,429)],[(247,409),(291,405),(305,449),(267,456),(254,439)]],
 [[(136,392),(175,403),(166,429),(148,450),(116,448),(120,429)],[(254,403),(299,399),(308,446),(271,454),(257,436)]],
 [[(132,399),(170,411),(159,435),(142,452),(109,451),(115,432)],[(249,409),(294,404),(306,449),(267,457),(254,438)]]]


# Native low-followthrough coat/mail ends above the trouser wedges. Select the
# actual two panels separately; the diagonal robe end follows its real border.
SHORT_PANELS={
 2:[[(131,365),(196,369),(208,378),(199,407),(126,384)],[(212,371),(240,371),(252,395),(232,408),(207,406)]],
 3:[[(135,363),(211,364),(218,378),(209,398),(132,376),(126,366)],[(220,371),(244,374),(256,394),(231,400),(214,394)]]}
MED_PANELS[2]=[[(129,364),(194,369),(203,382),(191,414),(119,400)],[(210,373),(239,371),(252,399),(233,414),(209,403)]]
MED_PANELS[3]=[[(135,363),(211,364),(218,379),(207,400),(190,409),(132,392)],[(220,372),(245,375),(262,398),(251,405),(218,399)]]
ROB_HEMS[2][1]=[(215,371),(245,367),(263,390),(281,407),(296,421),(234,445)]
ROB_HEMS[3][1]=[(225,377),(248,375),(270,405),(286,424),(239,441)]

def masks_for(i):
    bx,by=BELTS[i]
    return {name:w.poly(points) for name,points in {
        'head':HEADS[i],'weapon_forearm':WEAPON_ARMS[i],'other_forearm':OTHER_ARMS[i],
        'weapon_hand':WEAPON_HANDS[i],'other_hand':OTHER_HANDS[i],'cloth':CLOTH[i],
        'belt':[(bx-91,by-16),(bx+32,by-17),(bx+35,by+9),(bx+16,by+21),(bx-91,by+14)],
        'pouch':[(bx-91,by-9),(bx-39,by-8),(bx-35,by+8),(bx-48,by+32),(bx-93,by+24)]}.items()}

def main():
    out=P/'components/primary3-four-armors-v002';assert not out.exists();out.mkdir()
    marks=next(a for a in r.read(O/'assembly-markers-import-v005.json')['actions'] if a['action']=='primary_3')['frames']
    sheets={name:Image.new('RGBA',(1536,1024),(0,0,0,0)) for name in ['base','body_near']}
    for key in ['LGT','MED','HVY','ROB']:
        sheets[key+'_isolated']=Image.new('RGBA',(1536,1024),(0,0,0,0));sheets[key+'_sword']=sheets[key+'_isolated'].copy()
    sword=Image.open(O.parent/'first-unit-animation-v002/components/military-sword-clean-v001.png').convert('RGBA')
    bodies=[];armors={f'ARM-{k}-001':[] for k in ['LGT','MED','HVY','ROB']}
    for i,m in enumerate(marks):
        original=Image.open(m['frame_path']).convert('RGBA');native=Image.open(P/f'processed/call67-fixed-canvas-v002/frame-{i}.png').convert('RGBA')
        masks=masks_for(i);base=native.copy()
        for name in ['head','weapon_hand','other_hand','belt','pouch']:base.paste(original,(0,0),masks[name])
        lower=Image.new('L',(512,512),0);ImageDraw.Draw(lower).rectangle((0,410,511,511),fill=255);base.paste(original,(0,0),lower)
        base=w.sel.extract(base,Image.new('L',(512,512),255));near=w.sel.extract(base,masks['weapon_hand']);far=w.sel.extract(base,ImageChops.invert(masks['weapon_hand']))
        reconstructed=far.copy();reconstructed.alpha_composite(near);assert reconstructed.tobytes()==base.tobytes()
        for name in ['head','weapon_hand','other_hand']:assert w.sel.extract(base,masks[name]).tobytes()==w.sel.extract(original,masks[name]).tobytes()
        assert base.getpixel(tuple(m['grip_px']))==original.getpixel(tuple(m['grip_px']))
        parts={name:w.save(im,out/f'{name}-{i}.png','actual_P3_shared_body_distal_grip_candidate') for name,im in [('base_common',base),('body_far',far),('body_near',near)]}
        bodies.append({'index':i,'parts':parts,'root_px':m['ground_root_px'],'grip_px':m['grip_px'],'weapon_angle_image_clockwise_deg':m['weapon_angle_image_clockwise_deg'],
            'source_original_path':m['frame_path'],'source_original_sha256':m['frame_sha256'],
            'source_common_path':str(P/f'processed/call67-fixed-canvas-v002/frame-{i}.png'),'source_common_sha256':r.sha(P/f'processed/call67-fixed-canvas-v002/frame-{i}.png'),
            'exact_body_far_near_reconstruction':True,'original_traced_head_hands_preserved':True,'base_forearms_source':'native67_actual_same_pose_not_synthesized_or_rescaled','near_scope':'visible_distal_wrist_wrap_and_empty_gripping_fist_not_entire_forearm'})
        for name,im in [('base',base),('body_near',near)]:sheets[name].alpha_composite(im,((i%3)*512,(i//3)*512))
        for name,mask in masks.items():
            path=P/f'masks/primary3-{name}-{i}-v002.png';mask.save(path);r.archive(path,path.relative_to(P),'manual_P3_original_anatomy_and_clothing_trace')
        for key,request in [('LGT',68),('MED',69),('HVY',70),('ROB',71)]:
            source_path=P/f'processed/call{request}-fixed-canvas-v002/frame-{i}.png';source=Image.open(source_path).convert('RGBA')
            limit=Image.new('L',(512,512),0);ImageDraw.Draw(limit).rectangle((0,0,511,BELTS[i][1]+12),fill=255)
            q=ImageChops.darker(masks['cloth'],limit)
            hems=ROB_HEMS[i] if key=='ROB' else MED_PANELS[i] if key=='MED' else SHORT_PANELS[i] if key=='LGT' and i in SHORT_PANELS else [SHORT_HEMS[i]]
            q=ImageChops.lighter(q,w.union(hems))
            if key=='HVY':q=ImageChops.lighter(q,w.union(HVY_LEGS[i]))
            # ROB native changed wrist/cuff geometry: do not import its wrap or invented forearm coverage.
            exclusions=['head','weapon_hand','other_hand','belt','pouch','weapon_forearm','other_forearm']
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
            part=w.save(armor,out/f'ARM-{key}-001-armor-front-{i}.png','actual_P3_native_visible_garment_candidate_pending_review')
            mp=P/f'masks/primary3-ARM-{key}-001-front-{i}-v002.png';q.save(mp);r.archive(mp,mp.relative_to(P),'manual_P3_garment_source_selection_mask')
            preview=far.copy();preview.alpha_composite(armor);angle=math.radians(m['weapon_angle_image_clockwise_deg']);co=math.cos(angle);si=math.sin(angle);gx,gy=m['grip_px'];scale=.4
            preview.alpha_composite(sword.transform((512,512),Image.Transform.AFFINE,(co/scale,si/scale,99-(co*gx+si*gy)/scale,-si/scale,co/scale,256-(-si*gx+co*gy)/scale),resample=Image.Resampling.BICUBIC));preview.alpha_composite(near)
            sheets[key+'_isolated'].alpha_composite(armor,((i%3)*512,(i//3)*512));sheets[key+'_sword'].alpha_composite(preview,((i%3)*512,(i//3)*512))
            armors[f'ARM-{key}-001'].append({'index':i,'armor_front':part,'armor_back':None,'armor_back_visibility':'actual_visible_surfaces_front_overlay_only_no_hidden_back_invented',
                'source_path':str(source_path),'source_sha256':r.sha(source_path),'mask_path':str(mp),'mask_sha256':r.sha(mp),
                'root_px':m['ground_root_px'],'grip_px':m['grip_px'],'visible_RGBA_equals_source':True,'pruned_detached_fragment_sizes':pruned})
    for name,im in sheets.items():
        path=P/f'reviews/primary3-{name}-selection-v002.png';im.save(path);r.archive(path,path.relative_to(P),'actual_P3_layer_and_sword_review_pending')
    path=P/'manifests/primary3-four-armors-candidate-v002.json'
    r.write(path,{'schema':'manual-action-visible-layer-candidate-v1','clip':'primary_3','canvas':[512,512],'common_body':bodies,'armors':armors,
        'phase_seconds':[.22,.12,.32],'phase_frames':[2,2,2],'source_requests':[67,68,69,70,71],
        'draw_order':['body_far','armor_front','independent_weapon','body_near'],'no_body_geometry_transform':True,'source_pixels_only_no_paint':True,
        'near_scope':'actual_visible_distal_wrap_and_gripping_fist; native_same_pose_forearms_are_in_far_except_this_original_hand_selection',
        'robe_scope':'only_real_torso_upper_sleeve_and_hem_outside_original_forearms; full_long_sleeve_coverage_unfulfilled',
        'semantic_visual_review_passed':False,'runtime_verified':False,'complete_armor':False,
        'limitations':['ROB source changes raised forearm/cuff/wrap shape; whole traced original forearm excluded from armor. Only torso/upper-sleeve/hem candidate; full robe sleeve coverage remains unfulfilled.',
            'Selected visible surfaces are front-only; hidden full garment and old four-layer validator pass are not asserted.',
            'No clip transition,20-combination,mirror or running layered appearance acceptance.']})
    r.archive(path,path.relative_to(P),'P3_actual_source_selection_candidate_pending_semantic_review')
    print({'real_body_PNGs':18,'real_armor_PNGs':24,'runtime_new_PNGs_if_frozen':36,'semantic_review_pending':True})

if __name__=='__main__':main()
