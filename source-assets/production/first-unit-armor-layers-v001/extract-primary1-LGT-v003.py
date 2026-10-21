"""Actual primary1 clothing selection, frozen anatomy and original weapon grips."""
from pathlib import Path
import importlib.util,math
from PIL import Image,ImageDraw,ImageChops,ImageFilter
P=Path(__file__).resolve().parent;O=P.parent/'first-unit-animation-v003'
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
s=importlib.util.spec_from_file_location('selection',P/'extract-idle-components-v001.py');sel=importlib.util.module_from_spec(s);s.loader.exec_module(sel)
# All coordinates manually traced on original actual frozen body frames.
POSES=[
 {'cloth':[(129,223),(149,219),(166,237),(174,249),(209,257),(243,262),(274,259),(300,269),(315,288),(322,313),(307,328),(280,335),(278,352),(294,380),(277,395),(229,397),(215,381),(205,395),(140,384),(136,368),(146,345),(145,322),(161,308),(155,290),(143,284),(130,266)],
  'head':[(163,188),(171,160),(193,139),(217,132),(250,138),(280,154),(292,185),(294,221),(283,248),(268,267),(219,258),(177,246),(165,227)],
  'weapon_hand':[(106,176),(130,171),(148,176),(157,187),(155,205),(145,215),(142,239),(145,254),(138,272),(121,268),(109,258),(104,242),(101,228)],
  'other_hand':[(244,309),(253,302),(274,300),(292,305),(311,306),(321,315),(326,327),(320,340),(306,346),(284,345),(269,339),(251,339),(242,327)],
  'belt':[(148,326),(168,320),(221,329),(257,329),(272,332),(272,349),(221,354),(174,348),(145,343)],'pouch':[(153,324),(187,329),(189,343),(176,365),(144,361),(145,342)]},
 {'cloth':[(125,200),(147,192),(169,207),(184,223),(198,244),(231,257),(263,260),(296,268),(315,286),(324,316),(306,333),(280,338),(276,351),(295,381),(278,397),(229,396),(211,384),(203,396),(129,382),(126,365),(138,343),(138,320),(155,305),(153,275),(135,257),(125,240)],
  'head':[(175,182),(183,157),(207,138),(230,132),(259,139),(290,156),(305,184),(306,219),(293,249),(281,268),(230,259),(187,245),(177,220)],
  'weapon_hand':[(143,120),(163,114),(179,118),(192,134),(191,151),(179,163),(170,186),(161,216),(144,235),(129,228),(117,215),(112,196),(114,184),(129,155)],
  'other_hand':[(245,310),(256,302),(276,301),(294,306),(312,307),(324,318),(327,330),(319,341),(307,347),(285,345),(269,339),(252,339),(243,328)],
  'belt':[(133,318),(166,315),(219,329),(257,328),(270,333),(269,350),(219,354),(166,343),(133,337)],'pouch':[(146,316),(181,321),(184,338),(170,362),(137,353),(136,334)]},
 {'cloth':[(132,253),(146,238),(166,236),(185,247),(198,260),(226,268),(256,267),(276,285),(282,311),(269,327),(270,349),(282,375),(293,393),(252,409),(226,397),(214,407),(136,391),(129,374),(138,349),(145,327),(143,304),(133,291)],
  'head':[(139,181),(149,158),(170,140),(197,132),(225,137),(252,151),(269,181),(273,214),(260,245),(246,266),(200,257),(158,246),(142,222)],
  'weapon_hand':[(173,266),(191,265),(215,269),(236,273),(263,275),(283,276),(297,286),(301,299),(294,311),(279,315),(260,308),(234,311),(216,310),(193,304),(175,291)],
  'other_hand':[(262,320),(279,320),(299,326),(310,343),(304,356),(290,365),(274,357),(263,347),(254,334)],
  'belt':[(137,337),(169,333),(199,342),(235,343),(264,339),(274,350),(261,365),(211,366),(164,354),(136,352)],'pouch':[(145,333),(182,339),(185,355),(172,376),(136,369),(134,352)]},
 {'cloth':[(151,266),(176,255),(196,267),(220,277),(253,279),(279,285),(292,300),(291,330),(274,348),(276,368),(294,397),(265,406),(229,401),(217,390),(198,401),(119,389),(116,375),(128,352),(128,327),(143,310),(146,287)],
  'head':[(176,184),(184,163),(205,146),(233,138),(263,145),(293,162),(307,190),(310,224),(295,257),(281,283),(234,269),(194,251),(176,226)],
  'weapon_hand':[(197,314),(215,317),(233,327),(251,339),(275,350),(298,363),(310,377),(308,389),(296,400),(282,399),(266,390),(248,372),(233,363),(211,348),(199,334)],
  'other_hand':[(268,284),(285,283),(297,291),(306,308),(298,321),(284,326),(269,317),(261,303)],
  'belt':[(126,324),(158,327),(199,340),(230,346),(260,345),(265,360),(241,365),(193,356),(150,348),(124,341)],'pouch':[(132,325),(162,334),(163,353),(149,374),(118,365),(120,345)]},
 {'cloth':[(132,272),(151,264),(177,272),(204,280),(238,282),(263,289),(278,305),(277,332),(258,350),(268,374),(294,401),(266,412),(229,407),(215,395),(200,408),(109,391),(105,377),(120,350),(121,326),(129,304)],
  'head':[(163,185),(172,163),(194,146),(220,139),(251,145),(280,161),(293,190),(294,226),(280,258),(267,282),(219,270),(181,252),(163,227)],
  'weapon_hand':[(131,317),(147,315),(167,321),(183,331),(198,345),(218,355),(225,370),(218,382),(203,390),(186,384),(169,367),(150,353),(134,340)],
  'other_hand':[(246,282),(263,280),(279,287),(289,300),(282,316),(268,322),(254,313),(244,301)],
  'belt':[(113,332),(147,331),(182,342),(217,344),(245,340),(253,356),(234,364),(183,358),(145,350),(110,346)],'pouch':[(119,330),(150,337),(153,354),(139,376),(105,364),(108,345)]},
 {'cloth':[(134,272),(153,261),(181,268),(210,276),(246,278),(274,285),(289,299),(294,325),(280,346),(278,374),(295,400),(265,413),(229,409),(213,396),(197,409),(110,393),(106,375),(119,349),(122,326),(128,302)],
  'head':[(159,180),(169,158),(191,140),(216,133),(248,140),(277,156),(289,183),(291,220),(277,253),(265,276),(217,265),(179,247),(161,223)],
  'weapon_hand':[(136,314),(152,312),(171,320),(183,333),(204,345),(225,350),(227,365),(217,378),(201,381),(184,375),(171,363),(150,349),(136,335)],
  'other_hand':[(259,281),(275,280),(291,290),(307,303),(308,318),(295,332),(279,328),(267,313),(256,300)],
  'belt':[(115,333),(148,331),(185,339),(222,343),(259,335),(267,351),(244,362),(184,357),(145,349),(112,346)],'pouch':[(120,331),(151,336),(155,354),(141,376),(107,366),(110,345)]}
]

# Revised traces after actual isolated-layer review. No source pixels painted.
POSES[0]['weapon_hand']=[(106,176),(130,171),(148,176),(157,187),(155,205),(145,215),(142,239),(137,254),(134,269),(121,266),(109,257),(104,242),(101,228)]
POSES[1]['weapon_hand']=[(143,120),(163,114),(179,118),(192,134),(191,151),(179,163),(170,186),(160,214),(141,230),(129,225),(117,212),(112,196),(114,184),(129,155)]
POSES[2]['weapon_hand']=[(179,272),(194,267),(213,270),(224,273),(246,272),(266,276),(286,276),(299,287),(302,300),(295,311),(280,315),(268,309),(249,312),(227,313),(211,307),(192,303),(178,294)]
POSES[3]['weapon_hand']=[(202,299),(220,299),(235,311),(248,320),(263,336),(274,349),(299,353),(308,366),(310,381),(301,390),(282,391),(269,381),(263,365),(245,360),(231,349),(215,338),(200,324),(195,309)]
POSES[4]['weapon_hand']=[(133,296),(148,294),(163,300),(177,312),(184,326),(193,339),(211,345),(222,358),(221,372),(211,385),(194,387),(180,378),(174,365),(156,361),(145,348),(136,333),(129,315)]
POSES[5]['weapon_hand']=[(135,308),(151,306),(165,313),(178,324),(188,339),(209,341),(222,352),(224,366),(215,379),(197,381),(181,373),(174,362),(156,359),(143,349),(134,333)]
POSES[3]['cloth']=[(147,247),(173,239),(198,249),(220,277),(253,279),(279,285),(292,300),(291,330),(274,348),(276,368),(294,397),(265,406),(229,401),(217,390),(198,401),(119,389),(116,375),(128,352),(128,327),(143,310),(146,287)]
POSES[4]['cloth']=[(119,273),(132,252),(158,238),(181,245),(204,280),(238,282),(263,289),(278,305),(277,332),(258,350),(268,374),(294,401),(266,412),(229,407),(215,395),(200,408),(109,391),(105,377),(120,350),(121,326),(129,304)]
POSES[5]['cloth']=[(125,277),(138,255),(163,246),(184,253),(210,276),(246,278),(274,285),(289,299),(294,325),(280,346),(278,374),(295,400),(265,413),(229,409),(213,396),(197,409),(110,393),(106,375),(119,349),(122,326),(128,302)]
ARMOR_TOP_LIMIT=[350,350,360,350,350,355]
ARMOR_HEMS=[
[(144,346),(209,347),(222,350),(263,347),(280,365),(283,381),(231,393),(217,375),(205,393),(139,380)],
[(136,346),(206,344),(224,348),(268,348),(286,377),(282,387),(230,394),(213,378),(203,393),(129,380)],
[(137,353),(204,350),(229,356),(263,353),(277,384),(268,399),(226,405),(214,384),(204,401),(134,389)],
[(126,344),(189,344),(219,353),(258,351),(271,369),(223,384),(209,362),(198,388),(122,374)],
[(119,348),(185,346),(215,345),(252,344),(280,366),(239,384),(217,366),(206,392),(129,377),(117,367)],
[(126,352),(188,346),(222,346),(252,349),(279,370),(236,389),(219,369),(205,397),(127,382),(122,367)]]

def mask(points):
    m=Image.new('L',(512,512),0);ImageDraw.Draw(m).polygon(points,fill=255);return m
def main():
    out=P/'components/primary1-LGT-selection-v003';assert not out.exists();out.mkdir()
    marks=next(a for a in r.read(O/'assembly-markers-import-v005.json')['actions'] if a['action']=='primary_1')['frames']
    sheets={name:Image.new('RGBA',(1536,1024),(0,0,0,0)) for name in ['base','body_near','LGT_isolated','LGT_sword']};rows=[]
    sword=Image.open(O.parent/'first-unit-animation-v002/components/military-sword-clean-v001.png').convert('RGBA')
    for i,(pose,m) in enumerate(zip(POSES,marks)):
        orig=Image.open(m['frame_path']).convert('RGBA');common=Image.open(P/f'processed/call52-fixed-canvas-v002/frame-{i}.png').convert('RGBA');armored=Image.open(P/f'processed/call53-fixed-canvas-v002/frame-{i}.png').convert('RGBA')
        masks={k:mask(v) for k,v in pose.items()};cloth=masks['cloth'].copy()
        for k in ['head','weapon_hand','other_hand','belt','pouch']:cloth=ImageChops.subtract(cloth,masks[k])
        base=common.copy()
        # The native common body has no residual old shoulder armor; preserve
        # frozen anatomy/waist and every original lower-leg/boot pixel explicitly.
        for k in ['head','weapon_hand','other_hand','belt','pouch']:base.paste(orig,(0,0),masks[k])
        lower=Image.new('L',(512,512),0);ImageDraw.Draw(lower).rectangle((0,410,511,511),fill=255);base.paste(orig,(0,0),lower)
        base=sel.extract(base,Image.new('L',(512,512),255))
        near=sel.extract(base,masks['weapon_hand']);far=sel.extract(base,ImageChops.invert(masks['weapon_hand']));b=far.copy();b.alpha_composite(near);assert b.tobytes()==base.tobytes()
        for k in ['head','weapon_hand','other_hand']:assert sel.extract(base,masks[k]).tobytes()==sel.extract(orig,masks[k]).tobytes()
        assert base.getpixel(tuple(m['grip_px']))==orig.getpixel(tuple(m['grip_px']))
        top=Image.new('L',(512,512),0);ImageDraw.Draw(top).rectangle((0,0,511,ARMOR_TOP_LIMIT[i]),fill=255)
        armor_mask=ImageChops.lighter(ImageChops.darker(cloth,top),mask(ARMOR_HEMS[i]))
        for k in ['head','weapon_hand','other_hand','belt','pouch']:
            exclusion=masks[k].filter(ImageFilter.MaxFilter(21)) if k in ['weapon_hand','other_hand'] else masks[k]
            armor_mask=ImageChops.subtract(armor_mask,exclusion)
        armor=sel.extract(armored,armor_mask)
        parts={}
        for name,im in [('base_common',base),('body_far',far),('body_near',near),('armor_front',armor)]:
            f=out/f'{name}-{i}.png';im.save(f);r.archive(f,f.relative_to(P),'manual_actual_P1_visible_component_selection_pending_semantic_review');a=im.getchannel('A');parts[name]={'path':str(f),'sha256':r.sha(f),'canvas':[512,512],'mode':'RGBA','bbox':list(a.getbbox()) if a.getbbox() else None}
        for k,q in dict(clothing_replace=cloth,**masks).items():
            f=P/f'masks/primary1-{k}-{i}-v003.png';q.save(f);r.archive(f,f.relative_to(P),'manual_per_pose_visible_surface_mask')
        preview=far.copy();preview.alpha_composite(armor)
        a=math.radians(m['weapon_angle_image_clockwise_deg']);c=math.cos(a);s=math.sin(a);gx,gy=m['grip_px'];sc=.4
        preview.alpha_composite(sword.transform((512,512),Image.Transform.AFFINE,(c/sc,s/sc,99-(c*gx+s*gy)/sc,-s/sc,c/sc,256-(-s*gx+c*gy)/sc),resample=Image.Resampling.BICUBIC));preview.alpha_composite(near)
        for name,im in [('base',base),('body_near',near),('LGT_isolated',armor),('LGT_sword',preview)]:sheets[name].alpha_composite(im,((i%3)*512,(i//3)*512))
        rows.append({'index':i,'parts':parts,'root_px':m['ground_root_px'],'grip_px':m['grip_px'],'weapon_angle_image_clockwise_deg':m['weapon_angle_image_clockwise_deg'],'source_original_path':m['frame_path'],'source_original_sha256':m['frame_sha256'],'head_and_both_forearms_hands_preserved':True,'exact_body_far_near_reconstruction':True,'armor_back':None,'armor_back_visibility':'not_separately_visible_no_synthetic_hidden_back','mask_coordinates':pose})
    for name,im in sheets.items():
        f=P/f'reviews/primary1-{name}-selection-v003.png';im.save(f);r.archive(f,f.relative_to(P),'six_actual_component_frames_visual_review_pending')
    f=P/'manifests/primary1-LGT-selection-candidate-v003.json';r.write(f,{'schema':'manual-action-visible-layer-candidate-v1','clip':'primary_1','frames':rows,'phase_seconds':[.17,.12,.31],'phase_frames':[2,2,2],'canvas':[512,512],'draw_order':['body_far','armor_front','independent_weapon','body_near'],'no_body_geometry_transform':True,'source_requests':[52,53],'source_pixels_only_no_paint':True,'base_construction':'native52_shared_body_with_frozen_head_forearms_hands_waist_and_lowerlegs_restored','armor_selection_hand_clearance_px':10,'semantic_visual_review_passed':False,'runtime_verified':False,'complete_armor':False});r.archive(f,f.relative_to(P),'manual_pose_source_selection_candidate_not_runtime')
    print({'frames':6,'original_head_hands_preserved':True,'near_far_exact':True,'manual_semantic_review_pending':True})
if __name__=='__main__':main()
