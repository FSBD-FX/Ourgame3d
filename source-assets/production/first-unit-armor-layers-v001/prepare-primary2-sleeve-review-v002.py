"""Review the revised real-cloth track on all four armors; no media generation."""
from pathlib import Path
import importlib.util, math, json
from PIL import Image, ImageChops
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
old=r.read(P/'manifests/import-armor-primary2-four-v001.json')
c=r.read(P/'manifests/primary2-ROB-real-sleeves-candidate-v007.json')
sword=Image.open(old['weapon']['path']).convert('RGBA');audit=[]
ns={'__file__':str(P/'select-primary2-ROB-sleeves-v007.py')}
exec(compile((P/'select-primary2-ROB-sleeves-v007.py').read_text('utf-8').split('prior=P/')[0],str(P/'select-primary2-ROB-sleeves-v007.py'),'exec'),ns)
for armor_id,rows in old['armors'].items():
    sheets={d:Image.new('RGBA',(1536,1024),(0,0,0,0)) for d in ['right','left']}
    for i,(b,row,new) in enumerate(zip(old['common_body'],rows,c['frames'])):
        far=Image.open(new['parts']['body_far']['path']).convert('RGBA');hand=Image.open(new['parts']['body_near']['path']).convert('RGBA')
        whole=Image.open(b['body_far']['path']).convert('RGBA');whole.alpha_composite(Image.open(b['body_near']['path']).convert('RGBA'))
        rebuilt=far.copy();rebuilt.alpha_composite(hand);assert rebuilt.tobytes()==whole.tobytes()
        front=Image.open(new['parts']['armor_front']['path'] if armor_id=='ARM-ROB-001' else row['armor_front']['path']).convert('RGBA')
        near=Image.open(new['parts']['armor_near']['path']).convert('RGBA') if armor_id=='ARM-ROB-001' else None
        if near is not None:
            combined=front.copy();combined.alpha_composite(near)
            previous=Image.open(row['armor_front']['path']).convert('RGBA')
            added=ImageChops.subtract(combined.getchannel('A'),previous.getchannel('A'))
            # The estimated helmet polygon contains 1..48 pre-existing native
            # collar pixels in five poses. New sleeves must not enter it; the
            # existing partial front remains as frozen, not silently redefined.
            assert ImageChops.multiply(added,ns['tr'].w.poly(ns['HELMETS'][i])).getbbox() is None
            assert ImageChops.multiply(combined.getchannel('A'),ns['tr'].w.poly(ns['FISTS'][i])).getbbox() is None
        assembled=far.copy();assembled.alpha_composite(front)
        a=math.radians(b['weapon_angle_image_clockwise_deg']);co=math.cos(a);si=math.sin(a);gx,gy=b['grip_px'];scale=.4
        assembled.alpha_composite(sword.transform((512,512),Image.Transform.AFFINE,(co/scale,si/scale,99-(co*gx+si*gy)/scale,-si/scale,co/scale,256-(-si*gx+co*gy)/scale),resample=Image.Resampling.BICUBIC))
        if near is not None:assembled.alpha_composite(near)
        assembled.alpha_composite(hand)
        # Mirror the assembled image once about declared root X=256. This is a
        # review only; source frames/markers remain right-facing and untouched.
        mirrored=assembled.transform((512,512),Image.Transform.AFFINE,(-1,0,512,0,1,0),resample=Image.Resampling.NEAREST)
        for name,image in [('right',assembled),('left',mirrored)]:sheets[name].alpha_composite(image,((i%3)*512,(i//3)*512))
        audit.append({'armor_id':armor_id,'frame':i,'common_body_exact_RGBA_reconstruction':True,'root_px':b['root_px'],'grip_px':b['grip_px'],
            'common_near_scope':'actual_original_distal_fist_and_short_wrist_not_whole_forearm','actual_robe_near_present':near is not None})
    for direction,image in sheets.items():
        path=P/f'reviews/primary2-four-armors-sleeves-v007-{armor_id}-{direction}.png'
        if path.exists():assert Image.open(path).convert('RGBA').tobytes()==image.tobytes()
        else:image.save(path)
        r.archive(path,path.relative_to(P),'four_armor_actual_sleeve_partition_sword_preview_pending_manual_review')
path=P/'reviews/primary2-four-armors-sleeves-v007-provisional-audit.json';assert not path.exists()
r.write(path,{'schema':'four-armor-sleeve-partition-audit-v1','frames':audit,'preview_count':8,'generation_calls_added':0,'runtime_executed':False,
    'candidate':str(P/'manifests/primary2-ROB-real-sleeves-candidate-v007.json'),'candidate_sha256':r.sha(P/'manifests/primary2-ROB-real-sleeves-candidate-v007.json'),
    'semantic_manual_review_passed':False,'limitations':['Deterministic previews are not runtime/mirror-motion acceptance. Actual narrow pose0 skin gap remains from native source.']})
r.archive(path,path.relative_to(P),'four_armor_sleeve_partition_numeric_audit_not_motion_acceptance');print({'numeric_pose_samples':len(audit),'previews':8})
