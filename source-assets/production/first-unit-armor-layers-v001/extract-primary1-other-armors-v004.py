"""Actual material selections over frozen common P1 body; no creative pixel drawing."""
from pathlib import Path
import importlib.util,math
from PIL import Image,ImageDraw,ImageChops,ImageFilter
P=Path(__file__).resolve().parent;O=P.parent/'first-unit-animation-v003'
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
s=importlib.util.spec_from_file_location('trace',P/'extract-primary1-LGT-v005.py');tr=importlib.util.module_from_spec(s);s.loader.exec_module(tr)
COMMON=r.read(P/'manifests/import-armor-primary1-LGT-v001.json')
MED_HEMS=[
[(143,346),(212,349),(228,351),(266,350),(290,378),(284,389),(237,408),(222,389),(207,410),(136,391)],
[(137,346),(208,348),(226,351),(270,348),(291,380),(282,393),(239,411),(222,392),(206,406),(128,391)],
[(138,355),(202,353),(227,357),(262,354),(284,386),(278,407),(235,415),(215,395),(205,409),(131,394)],
[(123,344),(187,344),(215,353),(256,352),(280,388),(243,411),(219,393),(200,414),(112,393)],
[(118,346),(181,346),(211,345),(249,344),(282,380),(244,411),(220,390),(204,409),(111,392)],
[(124,350),(185,346),(219,346),(251,349),(282,382),(243,413),(220,392),(203,414),(119,396)]]
HVY_SHINS=[
 [[(125,399),(162,402),(180,412),(166,444),(112,450),(113,434)],[(248,402),(293,400),(310,445),(267,455),(257,437)]],
 [[(114,399),(152,401),(172,413),(154,445),(100,449),(104,433)],[(245,402),(290,401),(304,447),(262,454),(252,438)]],
 [[(118,404),(155,406),(169,419),(152,447),(101,451),(106,433)],[(248,406),(293,405),(307,448),(265,455),(255,439)]],
 [[(105,397),(143,403),(155,417),(131,447),(86,451),(94,430)],[(245,406),(291,405),(309,448),(265,455),(253,438)]],
 [[(108,398),(147,405),(158,418),(136,448),(91,452),(98,431)],[(243,407),(290,405),(307,450),(263,455),(252,438)]],
 [[(111,402),(151,405),(164,418),(145,449),(94,453),(102,432)],[(245,407),(291,406),(307,449),(264,455),(254,439)]]]
ROB_HEMS=[
[(142,347),(211,349),(226,350),(264,349),(306,413),(246,441),(224,414),(199,443),(108,415)],
[(135,346),(206,345),(224,349),(270,347),(307,416),(247,442),(224,414),(201,442),(101,416)],
[(138,354),(202,351),(227,355),(262,353),(293,430),(243,446),(216,418),(203,452),(108,427)],
[(124,344),(184,344),(215,352),(253,351),(285,429),(233,445),(211,417),(187,446),(84,412)],
[(118,347),(179,345),(212,345),(247,344),(285,430),(234,448),(214,419),(187,445),(91,414)],
[(125,351),(184,345),(219,346),(250,348),(285,431),(237,449),(216,421),(189,449),(98,419)]]
# Revised traced mail-hem side corners exclude visible trouser triangles.
for ii,point in enumerate([(142,389),(136,388),(138,391),(123,390),(122,391),(129,392)]):MED_HEMS[ii][-1]=point
def union(polygons):
    m=Image.new('L',(512,512),0);d=ImageDraw.Draw(m)
    for p in polygons:d.polygon(p,fill=255)
    return m
def main():
    out=P/'components/primary1-other-armors-v004';assert not out.exists();out.mkdir()
    result={};sword=Image.open(COMMON['weapon']['path']).convert('RGBA')
    for key,request in [('ARM-MED-001',54),('ARM-HVY-001',55),('ARM-ROB-001',56)]:
        rows=[];isolated=Image.new('RGBA',(1536,1024),(0,0,0,0));assembled=isolated.copy()
        for i,(pose,b) in enumerate(zip(tr.POSES,COMMON['common_body'])):
            srcpath=P/f'processed/call{request}-fixed-canvas-v002/frame-{i}.png';src=Image.open(srcpath).convert('RGBA')
            masks={k:tr.mask(v) for k,v in pose.items()};upper=masks['cloth'].copy()
            limit=Image.new('L',(512,512),0);ImageDraw.Draw(limit).rectangle((0,0,511,tr.ARMOR_TOP_LIMIT[i]),fill=255);upper=ImageChops.darker(upper,limit)
            hem=MED_HEMS[i] if key=='ARM-MED-001' else ROB_HEMS[i] if key=='ARM-ROB-001' else tr.ARMOR_HEMS[i]
            # Broader shoulder envelope selects only actual source alpha; native
            # detached backgrounds stay empty, source anatomy is excluded below.
            shoulders=masks['cloth'].filter(ImageFilter.MaxFilter(13));shoulderlimit=Image.new('L',(512,512),0);ImageDraw.Draw(shoulderlimit).rectangle((0,0,511,330),fill=255)
            q=ImageChops.lighter(upper,ImageChops.darker(shoulders,shoulderlimit));q=ImageChops.lighter(q,union([hem]))
            if key=='ARM-HVY-001':q=ImageChops.lighter(q,union(HVY_SHINS[i]))
            for name in ['head','weapon_hand','other_hand','belt','pouch']:q=ImageChops.subtract(q,masks[name])
            guard=ImageChops.lighter(masks['weapon_hand'],masks['other_hand']).filter(ImageFilter.MaxFilter(21))
            px=q.load();sp=src.load();gp=guard.load()
            for y in range(512):
                for x in range(512):
                    rr,gg,bb,aa=sp[x,y]
                    warm_skin=gp[x,y] and rr>220 and gg>160 and bb>100 and rr>gg*1.17 and gg>bb*1.25
                    blue_wrist=gg>=rr+8 and bb>=gg+5 # actual blue wraps; teal, warm steel and grayrobe do not match
                    sampled_trousers=False # warm metal/robe shadows overlap trousers; rely on traced garment contours
                    if px[x,y] and (warm_skin or blue_wrist or sampled_trousers):px[x,y]=0
            armor=tr.sel.extract(src,q);assert all(a==z for a,z in zip(armor.get_flattened_data(),src.get_flattened_data()) if a[3])
            path=out/f'{key}-armor-front-{i}.png';armor.save(path);r.archive(path,path.relative_to(P),'real_visible_P1_armor_selection_pending_visual_review')
            mp=P/f'masks/primary1-{key}-front-{i}-v004.png';q.save(mp);r.archive(mp,mp.relative_to(P),'manual_material_assisted_P1_armor_surface_mask')
            isolated.alpha_composite(armor,((i%3)*512,(i//3)*512))
            far=Image.open(b['body_far']['path']).convert('RGBA');near=Image.open(b['body_near']['path']).convert('RGBA');preview=far.copy();preview.alpha_composite(armor)
            a=math.radians(b['weapon_angle_image_clockwise_deg']);c=math.cos(a);s=math.sin(a);gx,gy=b['grip_px'];sc=.4
            preview.alpha_composite(sword.transform((512,512),Image.Transform.AFFINE,(c/sc,s/sc,99-(c*gx+s*gy)/sc,-s/sc,c/sc,256-(-s*gx+c*gy)/sc),resample=Image.Resampling.BICUBIC));preview.alpha_composite(near)
            assembled.alpha_composite(preview,((i%3)*512,(i//3)*512))
            rows.append({'index':i,'armor_front':{'path':str(path),'sha256':r.sha(path),'canvas':[512,512],'mode':'RGBA','bbox':list(armor.getchannel('A').getbbox())},'mask_path':str(mp),'mask_sha256':r.sha(mp),'source_path':str(srcpath),'source_sha256':r.sha(srcpath),'root_px':b['root_px'],'grip_px':b['grip_px'],'armor_back':None,'armor_back_visibility':'not_separately_classified_no_synthetic_hidden_pixels','visible_RGBA_equals_source':True})
        for suffix,im in [('isolated',isolated),('sword',assembled)]:
            f=P/f'reviews/primary1-{key}-{suffix}-v004.png';im.save(f);r.archive(f,f.relative_to(P),'actual_P1_component_review_pending')
        result[key]=rows
    f=P/'manifests/primary1-other-armors-candidate-v004.json';r.write(f,{'schema':'manual-action-visible-layer-candidate-v1','common_body_import':str(P/'manifests/import-armor-primary1-LGT-v001.json'),'common_body_import_sha256':r.sha(P/'manifests/import-armor-primary1-LGT-v001.json'),'clip':'primary_1','armors':result,'manual_hem_polygons':{'MED':MED_HEMS,'HVY':tr.ARMOR_HEMS,'ROB':ROB_HEMS},'HVY_shin_polygons':HVY_SHINS,'native_pixel_selection_only':True,'semantic_visual_review_passed':False,'runtime_verified':False,'complete_armor':False,'limitations':['Forearm anatomy follows common frozen body; upper-sleeve coverage is constrained by that shared foreground forearm.','Back cloth not separately classified yet; all selected visible garment is in the front overlay.','Manual source-specific material assistance and polygons require actual isolated-layer review, not a universal semantic segmentation claim.']});r.archive(f,f.relative_to(P),'P1_other_armor_source_and_mask_evidence_pending_review')
    print({'armor_clips':3,'frames_each':6,'real_PNGs':18,'visual_review_pending':True})
if __name__=='__main__':main()
