"""Select actual native walk garment pixels; fixed poses, no generated pixel painting.

This is a visible-surface candidate, not complete hidden clothing reconstruction.
The source walk's belt-proxy roots are copied verbatim, never inferred from alpha.
"""
from pathlib import Path
import importlib.util
import math
from PIL import Image, ImageDraw, ImageChops, ImageFilter

P = Path(__file__).resolve().parent
O = P.parent / 'first-unit-animation-v003'
spec = importlib.util.spec_from_file_location('record', P / 'production-record.py')
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
spec = importlib.util.spec_from_file_location('selection', P / 'extract-idle-components-v001.py')
sel = importlib.util.module_from_spec(spec); spec.loader.exec_module(sel)

BELTS = [(273,338),(340,350),(297,338),(266,342),(234,357),(270,338)]
CROWNS = [112,130,111,117,135,113]
HEAD_X = [246,318,272,237,210,246]
NEAR = [
 [(147,303),(160,300),(176,308),(188,320),(202,331),(214,339),(218,352),(211,366),(198,376),(181,378),(168,369),(162,356),(152,343),(145,327)],
 [(231,306),(246,302),(264,308),(279,323),(297,331),(309,340),(312,353),(305,366),(291,375),(275,376),(261,368),(251,355),(240,343),(231,327)],
 [(169,303),(182,300),(198,308),(210,321),(224,332),(235,340),(237,353),(231,367),(217,376),(201,377),(187,370),(180,357),(171,344),(166,326)],
 [(134,308),(148,305),(161,311),(173,324),(186,332),(195,342),(196,354),(187,368),(173,374),(159,370),(149,361),(142,348),(136,335),(130,321)],
 [(108,327),(124,326),(136,334),(135,347),(125,361),(122,377),(110,389),(93,389),(80,382),(75,369),(79,353),(91,339)],
 [(137,299),(150,296),(166,304),(178,316),(192,327),(204,335),(208,348),(201,362),(188,372),(171,374),(158,365),(152,352),(142,339),(135,323)],
]
OTHER = [
 [(303,323),(316,324),(330,335),(344,347),(350,360),(347,374),(335,383),(320,383),(307,375),(301,361),(296,343)],
 [(368,318),(382,320),(395,332),(410,342),(417,355),(413,367),(401,375),(387,374),(376,366),(370,351),(365,334)],
 [(335,324),(350,325),(365,337),(375,350),(378,362),(370,376),(356,382),(341,375),(334,361),(330,344)],
 [(298,319),(314,321),(328,331),(344,340),(355,353),(354,366),(342,376),(326,375),(312,366),(303,350),(296,333)],
 [(268,315),(282,318),(294,326),(310,331),(320,342),(320,357),(309,368),(293,368),(281,359),(273,345),(265,330)],
 [(307,315),(321,317),(337,329),(351,341),(362,354),(361,368),(348,378),(331,376),(316,366),(309,350),(302,331)],
]
SHORT_HEMS = [
 [(192,347),(249,350),(270,351),(297,348),(311,382),(274,393),(261,372),(250,392),(181,382)],
 [(264,361),(323,363),(341,362),(368,356),(382,387),(351,401),(333,379),(322,401),(249,381)],
 [(218,348),(275,349),(297,349),(326,347),(336,382),(302,393),(286,372),(277,391),(211,380)],
 [(185,352),(244,352),(266,353),(295,350),(308,384),(271,397),(257,375),(245,393),(176,380)],
 [(162,367),(217,366),(236,366),(263,360),(277,387),(241,408),(224,389),(208,406),(151,389)],
 [(190,349),(250,349),(271,349),(300,347),(314,382),(277,394),(263,374),(250,393),(184,380)],
]
MED_HEMS = [
 [(190,347),(249,350),(270,351),(297,348),(313,387),(305,405),(278,413),(264,390),(251,411),(180,400)],
 [(264,361),(323,363),(341,362),(368,356),(383,391),(372,411),(349,417),(333,395),(319,411),(249,392)],
 [(218,348),(275,349),(297,349),(326,347),(338,390),(323,409),(302,413),(287,390),(276,410),(208,399)],
 [(185,352),(244,352),(266,353),(295,350),(310,390),(296,411),(271,416),(257,390),(245,411),(174,398)],
 [(162,367),(217,366),(236,366),(263,360),(279,391),(258,411),(241,423),(224,404),(207,422),(152,401)],
 [(190,349),(250,349),(271,349),(300,347),(315,389),(302,410),(277,414),(262,391),(250,412),(182,399)],
]
ROB_PANELS = [
 [[(183,348),(257,349),(242,447),(176,440),(154,431)],[(274,349),(298,348),(323,429),(283,445)]],
 [[(266,360),(333,362),(310,442),(251,421),(230,405)],[(347,360),(366,355),(391,422),(358,441)]],
 [[(212,348),(282,349),(277,439),(218,435),(201,426)],[(300,348),(325,347),(340,402),(325,427)]],
 [[(178,352),(251,352),(235,439),(177,431),(162,413)],[(268,351),(293,349),(319,436),(280,444)]],
 [[(157,366),(221,367),(202,449),(155,425),(141,401)],[(235,366),(259,360),(289,395),(264,422)]],
 [[(184,348),(256,349),(247,447),(184,438),(165,427)],[(272,348),(298,347),(324,429),(282,445)]],
]
HVY_SHINS = [
 [[(177,397),(225,404),(219,440),(167,449)],[(255,403),(300,400),(308,443),(269,453),(256,439)]],
 [[(244,398),(279,412),(268,447),(221,429)],[(328,400),(369,395),(382,435),(339,445)]],
 [[(218,397),(269,401),(270,447),(216,451)],[(286,392),(326,388),(322,419),(282,426)]],
 [[(183,394),(222,407),(206,443),(167,432)],[(253,406),(298,405),(307,449),(265,456),(252,439)]],
 [[(140,392),(177,400),(181,426),(146,434)],[(222,405),(258,397),(281,437),(255,462),(226,438)]],
 [[(173,398),(225,403),(218,444),(163,449)],[(255,404),(300,400),(309,445),(269,455),(255,441)]],
]


# Actual isolated-layer review v001 found exposed elbow skin, trousers in the
# fifth hem and boot wedges below diagonal robe panels. Re-trace those surfaces;
# source RGBA remains untouched. The folded far shin in pose2 has no visible plate.
NEAR[4]=[(103,307),(118,306),(134,313),(143,329),(136,346),(125,361),
         (122,377),(110,389),(93,389),(80,382),(75,369),(79,353),(90,333),(97,317)]
SHORT_HEMS[4]=[(153,368),(216,368),(235,375),(254,375),(269,388),(260,391),
               (237,379),(212,391),(170,402),(152,388)]
MED_HEMS[4]=[(152,367),(226,367),(224,383),(212,395),(211,413),(171,415),(152,405)]
ROB_PANELS[1]=[[(267,361),(334,362),(328,390),(301,443),(275,414),(250,398)],
               [(262,365),(249,389),(222,410),(229,407),(248,395),(263,375)],
               [(347,360),(366,355),(391,422),(358,441)]]
ROB_PANELS[3]=[[(189,353),(252,352),(231,436),(174,407),(189,386)],
               [(186,362),(177,388),(158,405),(163,411),(178,395)],
               [(268,351),(293,349),(319,436),(280,444)]]
HVY_SHINS[2]=[HVY_SHINS[2][0]]
HVY_SHINS[4][0]=[(140,399),(164,401),(178,417),(169,428),(145,431)]
HVY_HEM4=[[(151,365),(169,370),(167,386),(154,393),(139,380)],
          [(173,376),(204,375),(201,403),(170,402)],
          [(208,374),(238,370),(246,394),(215,398)],
          [(245,366),(258,362),(269,385),(252,391)]]

def poly(points):
    image = Image.new('L', (512,512), 0)
    ImageDraw.Draw(image).polygon(points, fill=255)
    return image

def union(polygons):
    image = Image.new('L', (512,512), 0)
    for points in polygons:
        image = ImageChops.lighter(image, poly(points))
    return image

def relative(points, origin):
    return [(x+origin[0],y+origin[1]) for x,y in points]

def masks_for(i):
    head = relative([(-73,65),(-64,35),(-40,11),(-12,0),(21,5),(51,24),
                     (69,58),(73,93),(61,122),(44,145),(3,141),(-38,129),
                     (-67,114),(-74,88)], (HEAD_X[i],CROWNS[i]))
    belt = relative([(-82,-15),(29,-18),(35,7),(17,20),(-80,14)],BELTS[i])
    pouch = relative([(-75,-11),(-35,-9),(-33,4),(-42,27),(-77,26),(-83,8)],BELTS[i])
    cloth = relative([(-133,-41),(-127,-66),(-115,-88),(-97,-103),(-76,-108),
                      (-55,-99),(-32,-91),(0,-84),(31,-83),(48,-63),(58,-33),
                      (62,-5),(49,12),(-74,13),(-99,-3),(-117,-17)],BELTS[i])
    return {name:poly(points) for name,points in {
        'head':head,'weapon_hand':NEAR[i],'other_hand':OTHER[i],
        'belt':belt,'pouch':pouch,'cloth':cloth}.items()}

def prune_tiny(selection, source):
    points={(x,y) for y in range(512) for x in range(512)
            if selection.getpixel((x,y)) and source.getpixel((x,y))[3]}
    pruned=[]
    while points:
        seed=points.pop(); stack=[seed]; group=[seed]
        while stack:
            x,y=stack.pop()
            for next_point in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if next_point in points:
                    points.remove(next_point); stack.append(next_point); group.append(next_point)
        if len(group)<=24:
            pruned.append(len(group))
            for point in group: selection.putpixel(point,0)
    return pruned

def save(image, path, status):
    image.save(path); r.archive(path,path.relative_to(P),status)
    alpha=image.getchannel('A')
    return {'path':str(path),'sha256':r.sha(path),'canvas':[512,512],
            'mode':'RGBA','bbox':list(alpha.getbbox()) if alpha.getbbox() else None}

def main():
    out=P/'components/walk-four-armors-v002'; assert not out.exists(); out.mkdir()
    marks=next(a for a in r.read(O/'assembly-markers-import-v007.json')['actions'] if a['action']=='walk')['frames']
    sheets={name:Image.new('RGBA',(1536,1024),(0,0,0,0)) for name in ['base','body_near']}
    for key in ['LGT','MED','HVY','ROB']:
        sheets[key+'_isolated']=Image.new('RGBA',(1536,1024),(0,0,0,0));sheets[key+'_sword']=sheets[key+'_isolated'].copy()
    swordpath=O.parent/'first-unit-animation-v002/components/military-sword-clean-v001.png'
    sword=Image.open(swordpath).convert('RGBA'); common_rows=[];armor_rows={f'ARM-{k}-001':[] for k in ['LGT','MED','HVY','ROB']}
    for i,m in enumerate(marks):
        original=Image.open(m['frame_path']).convert('RGBA'); native=Image.open(P/f'processed/call57-fixed-canvas-v002/frame-{i}.png').convert('RGBA')
        masks=masks_for(i);base=native.copy()
        for name in ['head','weapon_hand','other_hand','belt','pouch']:base.paste(original,(0,0),masks[name])
        lower=Image.new('L',(512,512),0);ImageDraw.Draw(lower).rectangle((0,BELTS[i][1]+52,511,511),fill=255)
        base.paste(original,(0,0),lower);base=sel.extract(base,Image.new('L',(512,512),255))
        near=sel.extract(base,masks['weapon_hand']);far=sel.extract(base,ImageChops.invert(masks['weapon_hand']))
        composed=far.copy();composed.alpha_composite(near);assert composed.tobytes()==base.tobytes()
        for name in ['head','weapon_hand','other_hand']:assert sel.extract(base,masks[name]).tobytes()==sel.extract(original,masks[name]).tobytes()
        assert base.getpixel(tuple(m['grip_px']))==original.getpixel(tuple(m['grip_px']))
        parts={name:save(image,out/f'{name}-{i}.png','actual_walk_shared_body_fixed_geometry_candidate')
               for name,image in [('base_common',base),('body_far',far),('body_near',near)]}
        common_rows.append({'index':i,'parts':parts,'root_px':m['ground_root_px'],'root_kind':m['root_kind'],
                            'grip_px':m['grip_px'],'weapon_angle_image_clockwise_deg':m['weapon_angle_image_clockwise_deg'],
                            'source_original_path':m['frame_path'],'source_original_sha256':m['frame_sha256'],
                            'source_common_path':str(P/f'processed/call57-fixed-canvas-v002/frame-{i}.png'),
                            'source_common_sha256':r.sha(P/f'processed/call57-fixed-canvas-v002/frame-{i}.png'),
                            'exact_body_far_near_reconstruction':True,'traced_head_hands_preserved_exactly':True,
                            'original_lower_region_restored_from_y':BELTS[i][1]+52})
        for name,image in [('base',base),('body_near',near)]:sheets[name].alpha_composite(image,((i%3)*512,(i//3)*512))
        for name,mask in masks.items():
            path=P/f'masks/walk-{name}-{i}-v002.png';mask.save(path);r.archive(path,path.relative_to(P),'manual_actual_walk_visible_anatomy_and_clothes_trace')
        for key,request in [('LGT',58),('MED',59),('HVY',60),('ROB',61)]:
            source_path=P/f'processed/call{request}-fixed-canvas-v002/frame-{i}.png';source=Image.open(source_path).convert('RGBA')
            q=masks['cloth'].copy()
            limit=Image.new('L',(512,512),0);ImageDraw.Draw(limit).rectangle((0,0,511,BELTS[i][1]+12),fill=255)
            q=ImageChops.darker(q,limit)
            hems=ROB_PANELS[i] if key=='ROB' else [MED_HEMS[i] if key=='MED' else SHORT_HEMS[i]]
            if i==4 and key=='MED':hems += [[(239,366),(260,360),(278,388),(268,399),(247,394)]]
            if i==4 and key=='HVY':hems=HVY_HEM4
            q=ImageChops.lighter(q,union(hems))
            if key=='HVY':q=ImageChops.lighter(q,union(HVY_SHINS[i]))
            for name in ['head','weapon_hand','other_hand','belt','pouch']:
                exclusion=masks[name].filter(ImageFilter.MaxFilter(11)) if name in ['weapon_hand','other_hand'] else masks[name]
                q=ImageChops.subtract(q,exclusion)
            # Only known actual blue wraps and warm skin in traced limb neighborhoods;
            # no global gray/olive trouser filter that would erase metal or robe.
            guard=ImageChops.lighter(masks['weapon_hand'],masks['other_hand']).filter(ImageFilter.MaxFilter(21))
            pixels=q.load();sp=source.load();gp=guard.load()
            for yy in range(512):
                for xx in range(512):
                    rr,gg,bb,aa=sp[xx,yy]
                    warm_skin=gp[xx,yy] and rr>220 and gg>160 and bb>100 and rr>gg*1.17 and gg>bb*1.25
                    blue_wrap=gg>=rr+8 and bb>=gg+5
                    if pixels[xx,yy] and (warm_skin or blue_wrap):pixels[xx,yy]=0
            pruned=prune_tiny(q,source);armor=sel.extract(source,q)
            assert all(a==b for a,b in zip(armor.get_flattened_data(),source.get_flattened_data()) if a[3])
            alpha=armor.getchannel('A')
            for name in ['head','weapon_hand','other_hand','belt','pouch']:assert ImageChops.multiply(alpha,masks[name]).getbbox() is None
            part=save(armor,out/f'ARM-{key}-001-armor-front-{i}.png','actual_native_walk_garment_visible_surface_pending_visual_review')
            mp=P/f'masks/walk-ARM-{key}-001-front-{i}-v002.png';q.save(mp);r.archive(mp,mp.relative_to(P),'manual_per_frame_actual_walk_garment_selection')
            preview=far.copy();preview.alpha_composite(armor)
            angle=math.radians(m['weapon_angle_image_clockwise_deg']);c=math.cos(angle);s=math.sin(angle);gx,gy=m['grip_px'];scale=.4
            preview.alpha_composite(sword.transform((512,512),Image.Transform.AFFINE,(c/scale,s/scale,99-(c*gx+s*gy)/scale,-s/scale,c/scale,256-(-s*gx+c*gy)/scale),resample=Image.Resampling.BICUBIC));preview.alpha_composite(near)
            sheets[key+'_isolated'].alpha_composite(armor,((i%3)*512,(i//3)*512));sheets[key+'_sword'].alpha_composite(preview,((i%3)*512,(i//3)*512))
            armor_rows[f'ARM-{key}-001'].append({'index':i,'armor_front':part,'armor_back':None,
                'armor_back_visibility':'actual_visible_selected_surfaces_front_only_no_synthetic_hidden_back',
                'mask_path':str(mp),'mask_sha256':r.sha(mp),'source_path':str(source_path),'source_sha256':r.sha(source_path),
                'root_px':m['ground_root_px'],'grip_px':m['grip_px'],'visible_RGBA_equals_source':True,
                'pruned_detached_fragment_sizes':pruned,'tiny_fragment_threshold_px':24})
    for name,image in sheets.items():
        path=P/f'reviews/walk-{name}-selection-v002.png';image.save(path);r.archive(path,path.relative_to(P),'six_actual_walk_component_frames_pending_semantic_review')
    manifest=P/'manifests/walk-four-armors-candidate-v002.json'
    r.write(manifest,{'schema':'manual-action-visible-layer-candidate-v1','clip':'walk','canvas':[512,512],
        'common_body':common_rows,'armors':armor_rows,'duration_seconds':.6,'frame_duration_seconds':.1,'loop':True,
        'source_requests':[57,58,59,60,61],'no_body_geometry_transform':True,'source_pixels_only_no_paint':True,
        'draw_order':['body_far','armor_front','independent_weapon','body_near'],'armor_back_all_null':True,
        'root_scope':'copy_original_v007_manual_belt_proxy_not_single_support_foot_contact',
        'mask_scope':'manual_actual_visible_surfaces_excluding_head_forearms_hands_belt_pouch; no hidden anatomy',
        'semantic_visual_review_passed':False,'runtime_verified':False,'complete_armor':False,
        'limitations':['Source cycle has two extension poses without clear flat support and insufficient bob; no footlock or no-sliding acceptance.',
                       'Five-pixel foreground-forearm clearance can expose common leather undercoat at cuffs.',
                       'Common body is native57 with explicitly traced frozen head/hands/waist and lower-region original pixels restored.',
                       'All visible selected armor is front overlay; complete hidden garment or four-layer validator pass is not asserted.']})
    r.archive(manifest,manifest.relative_to(P),'actual_walk_source_selection_candidate_pending_review')
    print({'real_body_PNGs':18,'real_armor_PNGs':24,'runtime_new_PNGs_if_frozen':36,'semantic_visual_review_pending':True})

if __name__=='__main__':main()
