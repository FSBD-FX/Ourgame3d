"""Two original pre-contact technical mannequins; never draw on existing art."""
from pathlib import Path
from datetime import datetime
from xml.sax.saxutils import escape
import hashlib
import json
import math
import shutil
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
HERO=Path('F:/Ourgame/source-assets/production/fairytale-hero-v001')
CANONICAL=HERO/'sprite-run-idle-v002/curated/frame-0.png'
NUMERIC=HERO/'numeric-walk-request-v002.json'
ROW=HERO/'sprite-run-walk-v004/sprite-request.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def text(p,s):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:f.write(s)
def data(p,d):text(p,json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def copy(source,destination):
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():raise RuntimeError('Never overwrite: '+str(destination))
    shutil.copyfile(source,destination)
    assert sha(source)==sha(destination)

def guide(folder,phase):
    # Independent design coordinates: not measured art joints or output roots.
    near,far,gray,ink='#CF3F41','#356EC5','#D6D6DB','#22222B'
    rear_leg=[[238,329],[214,385],[186,435]]
    front_leg=[[257,329],[301,381],[333,436]]
    front_near_leg=[[238,329],[300,381],[333,436]]
    rear_far_leg=[[258,329],[218,385],[186,435]]
    front_arm=[[222,251],[264,282],[310,291]]
    back_near_arm=[[222,251],[200,282],[174,304]]
    back_far_arm=[[276,251],[239,282],[192,296]]
    front_far_arm=[[276,251],[309,279],[329,293]]
    if phase==2:
        nl,fl,na,fa=rear_leg,front_leg,front_arm,back_far_arm
    else:
        nl,fl,na,fa=front_near_leg,rear_far_leg,back_near_arm,front_far_arm
    polygons=[]
    def segment(a,b,width,color,note):
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
        nx,ny=-dy/length*width/2,dx/length*width/2
        points=[(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)]
        polygons.append(('poly',points,color,note))
    def circle(p,r,color,note):polygons.append(('ellipse',(p[0]-r,p[1]-r,p[0]+r,p[1]+r),color,note))
    def chain(joints,widths,color,note):
        for n in range(2):segment(joints[n],joints[n+1],widths[n],color,note)
        circle(joints[1],min(widths)/2,color,note+' joint')
    rear_boot=[(166,425),(190,428),(195,445),(215,454),(224,460),(222,464),(212,464),(170,445),(162,439)]
    front_boot=[(323,424),(343,421),(347,435),(365,432),(380,437),(378,445),(330,455),(322,450)]
    # Far limbs are behind. Near limbs are drawn after the gray torso/pelvis.
    chain(fa,[18,15],far,'far arm behind torso');circle(fa[-1],12,far,'far relaxed empty glove')
    chain(fl,[33,25],far,'far leg from deep hip')
    polygons.append(('poly',front_boot if phase==2 else rear_boot,far,'far boot'))
    polygons.append(('ellipse',(186,48,326,224),gray,'schematic head only; not helmet'))
    polygons.append(('poly',[(217,226),(280,226),(294,310),(279,344),(255,352),(214,341),(204,310)],gray,'schematic torso and pelvis hide deep far root'))
    chain(nl,[41,29],near,'near foreground leg; fixed depth side')
    polygons.append(('poly',rear_boot if phase==2 else front_boot,near,'near boot'))
    chain(na,[24,20],near,'near foreground arm');circle(na[-1],15,near,'near relaxed empty glove')
    png=folder/'references/technical/precontact-depth-guide-v001.png'
    svg=folder/'references/technical/precontact-depth-guide-v001.svg'
    png.parent.mkdir(parents=True,exist_ok=True)
    if png.exists() or svg.exists():raise RuntimeError('Never overwrite guide')
    im=Image.new('RGB',(512,512),'white');draw=ImageDraw.Draw(im)
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">','<rect width="512" height="512" fill="white"/>']
    for kind,pts,color,note in polygons:
        if kind=='ellipse':
            draw.ellipse(pts,fill=color,outline=ink,width=3)
            x0,y0,x1,y1=pts
            parts.append(f'<ellipse cx="{(x0+x1)/2}" cy="{(y0+y1)/2}" rx="{(x1-x0)/2}" ry="{(y1-y0)/2}" fill="{color}" stroke="{ink}" stroke-width="3"><title>{escape(note)}</title></ellipse>')
        else:
            draw.polygon(pts,fill=color);draw.line(pts+[pts[0]],fill=ink,width=3,joint='curve')
            points=' '.join(f'{x:.3f},{y:.3f}' for x,y in pts)
            parts.append(f'<polygon points="{points}" fill="{color}" stroke="{ink}" stroke-width="3" stroke-linejoin="round"><title>{escape(note)}</title></polygon>')
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
    labels=[(12,12,f'PHASE {phase} PRE-CONTACT - TECHNICAL GEOMETRY ONLY',ink),(12,29,'RED near / foreground; BLUE far / rear depth',ink),
            (20,416,'rear heel UP',near if phase==2 else far),(20,434,'rear TOE down',near if phase==2 else far),
            (347,470,'leading heel',far if phase==2 else near),(347,486,'still airborne',far if phase==2 else near)]
    for x,y,s,color in labels:
        draw.text((x,y),s,font=font,fill=color)
        parts.append(f'<text x="{x}" y="{y+11}" font-family="Arial,sans-serif" font-size="12" fill="{color}">{escape(s)}</text>')
    draw.line([(149,467),(399,467)],fill='#888890',width=1)
    parts.append('<path d="M149 467 H399" stroke="#888890" stroke-width="1"/>');parts.append('</svg>')
    im.save(png);text(svg,'\n'.join(parts)+'\n')
    return {'png':str(png),'sha256':sha(png),'svg':str(svg),'svg_sha256':sha(svg),'near_leg_design_px':nl,'far_leg_design_px':fl,'near_arm_design_px':na,'far_arm_design_px':fa,'rear_toe_contact_y_design':464,'leading_heel_y_design':455,'leading_heel_gap_design':9,'leading_toe_y_design':445,'all_numbers':'original technical design, not measured art or locked roots','existing_art_pixels_used':False}

def main():
    if (ROOT/'prep-receipt.json').exists():raise RuntimeError('Version frozen; create another version')
    assert sha(CANONICAL)=='f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718'
    assert sha(NUMERIC)=='7267a6e1fbf8422bc3433ff2fb916100bad19ebab765be1d1c0caed745c09fc3'
    assert sha(ROW)=='2ea85b9f89347950b9e63ad3f4b45a2d593718d6dff1eaaaef36a59da97acc33'
    timestamp=datetime.now().astimezone().isoformat(timespec='seconds')
    identity=ROOT/'references/identity/canonical131-idle-frame-0.png';copy(CANONICAL,identity)
    copy(NUMERIC,ROOT/'references/contracts/original-numeric-walk-request-v002.json')
    copy(ROW,ROOT/'references/contracts/original-139-sprite-request.json')
    cases=[(2,143,'near_push_far_reach',HERO/'passing-far-leg-edit-inputs-v001/raw/passing-far-leg-edit.png','7bcec84667e8d4be54696af9da8c33c9ecf81a4c5ccc47aadae2e76bd56113d0',142,'near','far','FORWARD/RIGHT across the torso','BACK/LEFT',1,3),
           (5,144,'far_push_near_reach',HERO/'walk-passing-pose-inputs-v001/far_support_near_pass/raw/passing-pose.png','333090236b72f262aaea9ff58310ab0f3fb975a3864bd317d57855c3c4058d66',141,'far','near','BACK/LEFT','FORWARD/RIGHT',4,0)]
    for index,label,name,motion_source,expected,motion_request,support,swing,near_arm,far_arm,previous,next_index in cases:
        assert sha(motion_source)==expected
        folder=ROOT/name;motion=folder/'references/motion/previous-passing.png';copy(motion_source,motion)
        g=guide(folder,index)
        refs=[{'order':1,'path':str(identity),'sha256':sha(identity),'source':str(CANONICAL),'role':'sole identity/style canonical131'},
              {'order':2,'path':str(motion),'sha256':sha(motion),'source':str(motion_source),'source_request':motion_request,'role':f'MOTION ONLY preceding passing phase{previous}; not requested pose, not identity, not full-motion proof'},
              {'order':3,'path':g['png'],'sha256':g['sha256'],'role':f'original thick-volume fixed-depth phase{index} guide only; no final colors/marks'}]
        prompt=f'''Generate exactly ONE full-body PRE-CONTACT / LATE-STANCE walking pose. Not a strip, not contact, not passing and not a complete cycle. All references have separate authority.

Image1 is the ONLY identity/style: canonical131 single curated idle. Preserve its rigid closed tan bell helmet, exact dome/rim/top knob/rivet, black visor and exactly two amber eyes, compact proportions, charcoal empty-handed common body, belt and brown gloves/boots. Same RIGHT-facing three-quarter camera; no new armor, weapon, cape, skin redesign or texture style. Do not return to idle stance.
Image2 is MOTION ONLY: the PREVIOUS passing phase{previous}, request{motion_request}. It helps track which leg is camera-near/far and the same compact grounded step. It is not identity and is NOT the output pose: move the previously swinging {swing.upper()} leg out into a forward heel reach, and let the {support.upper()} support leg progress behind the pelvis onto its toe. Do not copy its neutral arms or bent passing-leg pose. Do not copy generation drift in helmet/upper body. Image3 is an ORIGINAL THICK-FILLED TECHNICAL GUIDE ONLY: RED=NEAR foreground anatomical side; BLUE=FAR rear-depth side. It shows physical overlap, not just names. Translate both to the original charcoal clothing and brown gloves/boots; no colored limbs, gray mannequin head, floor line, labels, bones, or technical marks in the output.

EXACT ORIGINAL SIX-PHASE INDEX {index}: {name.upper()}
The {support.upper()} leg is the ONLY weight-bearing leg, now BEHIND the pelvis toward screen-LEFT. Its rear heel is RAISED, while the toe/forefoot still touches the floor, ready to push off. Knee stays softly bent and continuous; no knee buckling or heel-to-butt kick. The pelvis remains supported over this stance chain, not airborne.
The opposite {swing.upper()} leg reaches FORWARD toward screen-RIGHT. Its knee opens from passing into a comfortable longer reach, with a small natural bend, well BELOW the belt. The leading boot's HEEL is still a SMALL visible distance ABOVE the floor, just before landing; its toe is slightly raised above the heel. This heel must NOT touch yet. Do not plant a second sole or duplicate the next contact pose. No high knee, long fighting lunge, floating run or backwards kick. Exactly one rear toe contact and one hovering leading heel, separated readable boots.
Fixed depth: the near thigh is always the foreground anatomical side and overlaps the deeper far thigh root at their crossing; trace both fixed hips through knees to their own boots. For this pose the {support.upper()} thigh goes REARWARD to the grounded toe and the {swing.upper()} thigh goes FORWARD to the hovering heel. Do not swap near/far labels according to screen-left/right or mirror the entire character. Use the guide's actual arm and leg volume layering, with a coherent crotch/hip connection, two legs only and stable lengths.

COUNTER-SWING
The LARGE camera-NEAR arm is {near_arm}; the FAR arm is {far_arm}. They oppose their same-side legs: a forward reaching leg has its same-side arm back, and the opposite arm forward. Hands remain relaxed empty gloves, elbows softly bent and separately traceable. This is a walk counter-swing, not a punch, guard or reaching interaction. Do not leave both arms neutral or repeat the opposite half-stride's near arm.

ADJACENCY AND OUTPUT
This is between original phase{previous} passing and phase{next_index} heel contact. Preserve the same right-facing helmet/body volume; a slight controlled body rise/weight transfer is allowed without squash or scale drift. This still image does not establish actual motion direction, velocity, contact timing or a loop. Keep head-to-toe figure centered inside a nominal512x512 cell with48px safe margin per side; no cropping or unrelated body translation. Exactly two arms/hands and two complete legs/boots; no fused joints or detached parts.
Flat PURE GREEN #00FF00 background, no green material on the character. No cast/contact shadow, floor patch, scenery, dust, blur, trails, glow, effects, text, UI, numbers, arrows, colored guide marks, border or checkerboard. One full-body static pre-contact pose only, with the {support.upper()} REAR TOE down and the {swing.upper()} FORWARD HEEL still airborne. Keep the original hand-drawn dark-fairytale cartoon style, broad painted color blocks and bold uneven ink, not pixel art, PBR or realistic 3D.
'''
        pf=folder/'prompts/precontact.txt';text(pf,prompt)
        contract={'schema':'fairytale-single-precontact-role-contract-v1','prepared_at_system_local':timestamp,'original_phase_index':index,'original_phase_name':name,'intended_root_request_label':label,'status':'prepared_not_generated_not_accepted','output_poses':1,'loop':False,'native_facing':1,'previous_phase_index':previous,'next_phase_index':next_index,'support_leg':support,'support_contact':'rear toe/forefoot only, heel raised','swing_leg':swing,'swing_contact':'leading heel still slightly airborne, toe raised; no second planted foot','arms':{'near':near_arm,'far':far_arm},'depth_contract':'fixed anatomical near side foreground; far root deeper and occluded; not screen-label reassignment','attachments':refs,'technical_guide':g,'actual_measurements':{'raw_sha256':None,'root_px':None,'boot_contact_span':None,'heel_gap_px':None,'body_height_px':None,'helmet_bbox':None},'acceptance_pending':['root F/E retain and actual guide view','native single-pose generation by root only','raw F/E retention then static identity/arm/leg/contact review','deterministic extraction then curated review'],'does_not_prove':['six-frame sequence','contact velocity','stance travel','loop seam','left mirror','runtime integration'],'formal_complete_units':0}
        data(folder/'role-contract.json',contract)
        request={'schema':'fairytale-single-precontact-generation-input-v1','prepared_at_system_local':timestamp,'status':'prepared_only','intended_root_request_label':label,'provider_call_performed':False,'prompt_file':str(pf),'prompt_sha256':sha(pf),'attachments_in_order':refs,'imagegen_parameters_for_root_only':{'referenced_image_paths':[r['path'] for r in refs],'transparent_background':False,'num_last_images_to_include':'omit','prompt':'read exact prompt_file'},'future_raw_path':str(folder/'raw/precontact.png'),'future_raw_sha256':None,'generation_authority':'root only; preparer cannot generate/import/run UE','automatic_extract_or_import':False}
        data(folder/'generation-request.json',request)
        sprite={'version':1,'kind':'sprite-gen-request','engine':'component-row','character':{'id':'fairytale-hero-'+name+'-single-pose-v001','description':'Canonical131 sole identity; one experimental pre-contact static motion role','base_image':str(identity)},'cell':{'shape':'square','size':512,'safe_margin':48},'chroma_key':{'name':'green','hex':'#00FF00','rgb':[0,255,0]},'states':{name:{'frames':1,'fps':1,'loop':False,'action':f'Single original phase{index} {name}; {support} rear toe supports, {swing} leading heel hovers; not a cycle.'}},'style':'Canonical131 hand-drawn dark-fairytale cartoon exactly; not pixel art','fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':True,'segmentation':'components','shared_row_scale':True},'chroma':{'mode':'rgb','unmix_reach':4,'spill_max_fraction':0.005},'project_phase_contract':{'original_numeric_source':str(NUMERIC),'sha256':sha(NUMERIC),'original_phase_index':index,'original_phase_name':name,'future_six_phase_duration_ms_design_only':83,'single_pose_fps_is_not_gameplay_speed':True,'actual_roots_and_stride_unlocked':True}}
        data(folder/'sprite-request.json',sprite)
    text(ROOT/'handoff.md',f'''# 六相中2/5 pre-contact独立输入

系统时间：{timestamp}。正式合同见 references/contracts 的逐字节副本；phase2=near_push_far_reach，phase5=far_push_near_reach。未把139失败图片附入或重新标相位。

原六相可解释为 contact→passing→late-stance/precontact 两半周期。它省略独立down/up采样，属于压缩的六样本设计，尚不保证平滑；但有相反支撑、摆腿、对侧摆臂和连续接地的明确语义，没有必要仅因“标准八关键姿势”就替换合同。若真实motion显示压低/起高节奏无法表达，另立八相contact/down/passing/up×2，重审全周期，不把旧六张改标签凑数。

143/phase2在142/phase1之后、137/phase3之前：near后趾支撑、far前跟悬空；near大臂前、far臂后。144/phase5在141/phase4之后、138/phase0之前：far后趾支撑、near前跟悬空；near大臂后、far臂前。precontact须与双足可接触的contact区别，不能把137/138再画一遍。左右不整体翻转。

每张只附canonical131唯一身份、各自相邻passing原件作MOTION ONLY、原创厚块technical guide。Guide由新空白画布绘制，far先画/near后画，髋和肢体链与摆臂分别交换；没有读取旧图像素用于绘制。技术色/灰头/标线不进入成品，全部坐标仅设计，不是已测足根。PNG和SVG来自同一原创几何数据。

Root先F/E保全输入再实际看guide，随后读各自prompts/precontact.txt原文进行native单姿势生成。原稿另保全后看、提取再审；不要自动生成整行/拼接/改时长/UE导入。单张sprite-request为frames1/fps1/loopfalse，未来83ms只是原六相设计，并非单张已测速度。完整walk仍experimental，formal complete units0。
''')
    records=[{'path':str(f),'relative_path':f.relative_to(ROOT).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(ROOT.rglob('*')) if f.is_file()]
    data(ROOT/'prep-receipt.json',{'schema':'fairytale-precontact-input-preparation-receipt-v1','created_at_system_local':timestamp,'interpreter':sys.executable,'file_bindings':records,'guide_view_status':'not_viewed_pending_root_F_E_retention','native_generation_calls':0,'ue_ubt_calls':0,'source_or_old_media_edits':False,'formal_complete_units':0})
    print(json.dumps({'folder':str(ROOT),'files':len(records)+1,'bytes':sum(x['bytes'] for x in records)+(ROOT/'prep-receipt.json').stat().st_size,'receipt_sha256':sha(ROOT/'prep-receipt.json'),'phase_inputs':[{'phase':i,'name':n,'prompt_sha256':sha(ROOT/n/'prompts/precontact.txt'),'request_sha256':sha(ROOT/n/'generation-request.json'),'guide_sha256':sha(ROOT/n/'references/technical/precontact-depth-guide-v001.png')} for i,n in [(2,'near_push_far_reach'),(5,'far_push_near_reach')]],'new_guides_viewed':False,'generation_calls':0},ensure_ascii=False))

if __name__=='__main__':main()
