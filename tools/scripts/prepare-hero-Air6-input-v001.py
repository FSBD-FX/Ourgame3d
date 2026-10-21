"""Prepare standard component-row inputs only; no image generation or engine writes."""
from pathlib import Path
import hashlib,json,shutil,sys
R=Path('F:/Ourgame');S=Path('C:/Users/22499/.codex/skills/sprite-gen')
B=R/'source-assets/production/fairytale-hero-state-gap-v001/air-state-preparation-v001/standard-input-v001'
O=R/'过程图稿与视频/2026-10-18_钟盔非攻击跳跃六相输入_v001'
assert Path(sys.executable).resolve()==(S/'.venv/Scripts/python.exe').resolve()
assert not B.exists() and not O.exists();B.mkdir(parents=True);(O/'原件').mkdir(parents=True);(O/'展示副本').mkdir()
sys.path.insert(0,str(S));from sprite_gen.gen.prepare import draw_guide,row_prompt,normalize_states
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
anchor=R/'source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-0.png'
assert pin(anchor)['sha256']=='d3f766506a9cc623c38787836a9c23c0126d185d1bdf7e8946181efd554338c5'
request=json.loads((R/'source-assets/production/fairytale-hero-state-gap-v001/standard-input-candidate-v001/sprite-request.json').read_text(encoding='utf-8'))
action='''The exact attached accepted native-RIGHT three-quarter bell/clock-helmet hero, body only in charcoal cloth shirt/trousers and original brown gloves/boots. This is ONE continuous nonattack jump-to-land action, six genuinely articulated poses, not6 different identities. Same rigid squat helmet volume, original crooked top knob, two contained amber eyes, same head/torso/limb anatomical scale and heavy hand-inked contours as the identity anchor. Preserve416-source-pixel standing-equivalent anatomical scale on512 cells: naturally tucked poses are shorter, NEVER zoom or independently fit them. Keep the torso/pelvis spatial reference consistent across the strip; actual world vertical translation comes from the game, do not draw a row of higher/lower world positions. Do not force a boot baseline for airborne poses. No armor/chest/shoulder plates, no sword/handle/shield/staff/rod, no ground/shadow/dust/FX. Future armor and sword are separate modules. Both near and far hands must be real connected wrist/thumb/fingers and arms; no detached gloves, painted socket dots or copied frozen hands. Near hand maintains a natural compact later one-hand grip, but author grip/axis is unknown until actual pixels exist. Body owner is only the accepted frame0; no old canonical/alternate art. Exact left-to-right progression: 0 EARLY RISE: legs push away and begin a genuine knee tuck, connected arms draw in, torso subtly extends; not standing Ready. 1 LATE RISE: both knees tuck more, boots and hips visibly articulate, near/far elbows and wrists naturally adjust. 2 APEX: compact readable floating suspension, knees tucked with distinct boot angles, rigid helmet settles without stretching. 3 DESCENT: legs reopen downward to prepare contact, ankles and shoulders brace, distinct from rise/apex; torso anatomical scale unchanged. 4 LANDING IMPACT: authentic knee/hip compression under weight, boots receive support and connected arms counterbalance; no impact effect and no whole-sprite rotation. 5 LANDING SETTLE: knees/torso reopen toward the actual accepted Ready anatomy, hands remain naturally connected; no exact paste of the idle. In game frames0..3 sample actual H/V, frames4..5 use the already existing .12s landing age. The standard10fps preview is only an author preview, not the gameplay clock.'''
request['character']['id']='fairytale-clock-hero-nonattack-Air6-v001'
request['states']={'jump_nonattack':dict(frames=6,fps=10,loop=False,action=action)}
assert normalize_states(request['states'])==request['states']
q=B/'sprite-request.json';q.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
guide=B/'references/layout-guides/jump_nonattack.png';guide.parent.mkdir(parents=True);draw_guide(guide,'jump_nonattack',6,request['cell'],motion_phase_guides=False)
prompt=B/'prompts/jump_nonattack.txt';prompt.parent.mkdir();prompt.write_text(row_prompt(request,'jump_nonattack',request['states']['jump_nonattack']),encoding='utf-8')
runtime=dict(schema='Hero-Air6-actual-physics-presentation-proposal-v001',air='H>0 OR V>0',frames=['RiseEarly V>315','RiseLate 90<V<=315','Apex abs(V)<=90','Fall V<-90','LandingImpact H=V=0 age in[0,.06)','LandingSettle H=V=0 age in[.06,.12)'],physics_unchanged=dict(initialV=630,gravity=1800,landingAgeCap='.12f',projection=.70,standing_scale='72/416'),source_points=None,source_accepted=False,runtime_imported=False,preview_fps_is_not_runtime_clock=True,whole_rig_or_per_pose_fit_forbidden=True)
(B/'runtime-sampling-proposal-v001.json').write_text(json.dumps(runtime,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[anchor,q,guide,prompt,B/'runtime-sampling-proposal-v001.json',Path(__file__)];rows=[]
for i,p in enumerate(files):
 t=O/'原件'/f'{i:03d}-{p.name}';shutil.copy2(p,t);assert pin(t)['sha256']==pin(p)['sha256'];rows.append(dict(source=pin(p),copy=pin(t)))
for i,p in enumerate([anchor,guide]):shutil.copy2(p,O/'展示副本'/f'{i:02d}-{p.name}')
(O/'index.json').write_text(json.dumps(dict(schema='Root-Hero-Air6-input-preparation-v001',files=rows,sole_identity=pin(anchor),guide_only=True,generation_performed=False,viewed=False,E_before_view_required=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'README.md').write_text('当前钟盔唯一身份与标准六格动作输入。仅准备，未生成、导入或接受；416→72共同解剖尺度，空中不按脚底强制对齐，真实高度/速度/落地时间由原游戏决定。保全E后才能View或作为图像参考。\n',encoding='utf-8')
print(json.dumps(dict(input=B.as_posix(),archive=O.as_posix(),prompt=pin(prompt),identity=pin(anchor),guide=pin(guide)),ensure_ascii=False))
