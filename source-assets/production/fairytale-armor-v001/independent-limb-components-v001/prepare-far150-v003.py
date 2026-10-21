"""New original technical diagram, frozen input, and single-writer reservation.

No existing artwork is edited. The old guide and failed two-point gate remain.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import datetime, hashlib, json, shutil

root=Path('F:/Ourgame')
base=Path(__file__).resolve().parent
control=base/'generation-control-v001'
ledger=root/'source-assets/production/first-unit-animation-v003/generation-ledger.json'
prompt=root/'docs/production/first-batch-v2/evidence/fairytale-limb-contract-v003/far-five-reference-prompt-v003.txt'
guide=base/'guides/shoulder-far-primary-mount-v003.png'
archive=root/'过程图稿与视频/2026-10-16_远肩单挂点五参考输入_v003'
assert not guide.exists() and not archive.exists()
assert hashlib.sha256(prompt.read_bytes()).hexdigest()=='04adfbb81c1b8828af05bab69dd07036567ee925edb278c24a09a12b77e31e05'
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
im=Image.new('RGB',(2048,512),'#f4f6f8');d=ImageDraw.Draw(im)
targets=[((296,255),(302,275)),((296,253),(302,273)),((296,256),(302,276)),((296,255),(302,275))]
outline=[(-9,-9),(1,-12),(12,-5),(18,8),(16,18),(6,20),(-5,15),(-9,5)]
for i,(mount,hint) in enumerate(targets):
    ox=i*512
    def tx(p):return (ox+256+p[0]*5,235+p[1]*5)
    d.rectangle((ox+10,10,ox+502,502),outline='#94a3b8',width=2)
    d.text((ox+24,24),f'FAR shoulder / idle {i} / 167ms / v003',fill='#172554',font=font)
    d.text((ox+24,52),f'BODY A {mount}; upper-arm HINT {hint}',fill='#172554',font=font)
    d.line([tx((0,0)),tx((18,45))],fill='#c9ced5',width=22)
    d.polygon([tx(p) for p in outline],fill='#cab2d4',outline='#334155',width=4)
    for p,color in [(tx((0,0)),'#dc2626'),(tx((6,20)),'#16a34a')]:
        d.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),fill=color)
    d.text((ox+24,418),'RED = single primary rivet A',fill='#172554',font=font)
    d.text((ox+24,444),'GREEN = arm / lower-edge hint, NOT attachment',fill='#172554',font=font)
    d.text((ox+24,476),'NO technical colors / dots / text in final art',fill='#172554',font=font)
guide.parent.mkdir(parents=True,exist_ok=True);im.save(guide)
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(p,v):
    assert not p.exists(),p
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
l=json.loads(ledger.read_text(encoding='utf-8-sig'))
assert l['requested_count']==149 and l['current_window']['number']==7,l['current_window']
write(control/'ledger-before-request150.json',l)
refs=[
 (root/'source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png','sole_identity'),
 (root/'source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/qa/idle-contact.png','four_idle_pose_order_only'),
 (root/'source-assets/production/fairytale-armor-v001/independent-idle-components-v001/registration-proposed-v001/composite-preview/frame-0.png','147_actual_chest_palette_only'),
 (base/'run-shoulder-far-idle-v001/references/layout-guides/armor_shoulder_far_idle.png','standard_four_component_layout'),
 (guide,'corrected_original_technical_primary_A_direction_hint_only')]
request={'request_number':150,'asset':'fairytale-far-shoulder-four-idle-primary-mount-v003','status':'requested_pending',
 'source_event':'EV-048','authorization_events':['EV-040','EV-041'],'window_number':7,
 'requested_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prompt_path':prompt.as_posix(),
 'prompt':prompt.read_text(encoding='utf-8'),'prompt_file_sha256':desc(prompt)['sha256'],
 'reference_images':[dict(desc(p),role=role) for p,role in refs],
 'transparent_background':False,'backend':'image_gen.imagegen','external_api_calls':0,'host_fee_usd':None,
 'raw_destination_planned':(base/'run-shoulder-far-idle-v001/raw/armor_shoulder_far_idle.png').as_posix(),
 'scope':'Four genuine independent far caps only. A mount; B direction hint. Old v002 gate failure retained, not retroactively passed.',
 'formal_complete_units':0}
write(control/'generation-request150-v003.json',request)
l['requests'].append(request);l['requested_count']=150;l['batch_requested_count']+=1
l['current_window']['requested_count']+=1
l['remaining_batch_requests']=24-l['current_window']['requested_count']
l['lifetime_requested_count']=l['lifetime_prior_EV038_requests']+150
ledger.write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write(control/'ledger-after-request150-reserved.json',l)
(archive/'原件').mkdir(parents=True);(archive/'展示副本').mkdir()
files=[prompt,guide,Path(__file__),control/'generation-request150-v003.json',control/'ledger-before-request150.json',
       control/'ledger-after-request150-reserved.json',root/'docs/production/first-batch-v2/fairytale-shoulder149-static-review-v001.md']+[p for p,_ in refs]
rows=[]
for n,p in enumerate(dict.fromkeys(files)):
    target=archive/'原件'/f'{n:02d}-{p.name}';shutil.copy2(p,target);assert target.read_bytes()==p.read_bytes()
    rows.append(dict(desc(p),retained_relative=target.relative_to(archive).as_posix()))
shutil.copy2(guide,archive/'展示副本/far-primary-mount-guide-v003.png')
write(archive/'source-version-status-index.json',{'files':rows,'status':'input_only_not_generated_or_accepted',
 'old_guide_and_two_point_failure_retained':True,'formal_complete_units':0})
(archive/'README.md').write_text('Original technical diagram regenerated from authored coordinates with corrected labels. No existing art pixels edited. Input only, pending real native150. Old v002 gate failure retained. F canonical / E display retention, not acceptance.\n',encoding='utf-8')
print(json.dumps({'request':150,'refs':len(refs),'window':l['current_window'],'lifetime':l['lifetime_requested_count'],'archive':archive.as_posix(),'guide':desc(guide)},ensure_ascii=False))
