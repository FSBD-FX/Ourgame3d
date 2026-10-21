from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003';O=B/'concept179-v001'
assert not O.exists();(O/'references').mkdir(parents=True);(O/'prompts').mkdir();(O/'raw').mkdir()
source=R/'source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-0.png'
b=source.read_bytes();assert hashlib.sha256(b).hexdigest()=='d3f766506a9cc623c38787836a9c23c0126d185d1bdf7e8946181efd554338c5'
ref=O/'references/current158-ready0.png';shutil.copy2(source,ref);assert ref.read_bytes()==b
prompt='''Use case: precise-object-edit. One assembled outfit reference, not a final sprite or animation sheet.
Edit only the clothing in the supplied current sword-ready hero reference. Preserve its exact recognizable grotesque cartoon identity and pose: squat closed tan bell helmet with crooked small top knob, dark eye window and two amber eyes, short limbs, brown gloves/boots, compact bent near arm and closed empty near fist held low, relaxed far hand, three-quarter facing RIGHT. Do not move limbs to expose the outfit; no visible human skin, new face, redesign or oversized body.

The confirmed LIGHT armor is a waist-length soft LEATHER travel jerkin, not a metal breastplate. Create a clear compact tawny-brown leather chest mass over the charcoal cloth, with deep reddish-brown side/under planes and one broad restrained ochre upper plane. Two or three big hand-painted values, thick uneven dark ink edges, few large construction seams. A small simple fastening and attached short side cloth pouch are enough. Keep a distinct dark collar gap below the helmet and a dark belt/waist flex gap; do not merge the tan helmet and jerkin into one blob.

Add two SHORT SOFT leather shoulder caps: the nearer image-LEFT shoulder slightly more projecting, far image-RIGHT cap compressed by the real perspective. Clear small steps in the outer silhouette and broad light-vs-dark planes should identify the armor when this entire character is72pixels high. Keep collar, elbows, wrists, gloves, knees and separated boot shapes visible. Leave most flexible charcoal sleeves and pants visible. The leather is a lighter muted tan-brown than the rust-brown gloves and boots; broad value separation from dark clothing matters more than fine stitching. Preserve free joints and a light agile silhouette. This is not heavy plate or chainmail.

Match the reference's crooked, playful dark-fairytale hand-inked drawing and economical matte painted shapes. Do not add photorealistic texture, engravings, shine, PBR, rim glow or a pixel grid. No oversized square shoulders, metal shell, shoulder spikes, cape, skirt, horns, shield, weapon, extra character, extra limbs, labels, panels, UI, floor or shadow. One full figure centered, head and soles visible, generous clear margin on a truly transparent alpha background. No checkerboard or opaque backdrop. Keep original body/helmet height and overall anatomy; only the attached outfit may add modest local width. This raw assembled reference will later guide separate per-pose leather components; it must never be substituted as the authoritative unchanged common body.'''
p=O/'prompts/179-soft-leather-readability.txt';p.write_text(prompt+'\n',encoding='utf-8')
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
spec=dict(request_number=179,kind='one_assembled_light_leather_reference',source_event='EV-048',reference_images=[dict(role='sole current accepted Ready0 identity/pose edit target; not old metal armor',file=desc(ref),original_source=desc(source))],prompt=desc(p),transparent_background=True,raw_destination=(O/'raw/179-soft-leather-reference.png').as_posix(),scope='Study reference only; commonbody unchanged, no runtime import or complete armor accepted',design_basis=['docs/design/equipment-v1/03-防具.md:41','docs/design/presentation-v1/01-武器与防具动作规范.md:108'],body_max_future_px=72,weapon_scale_unchanged=.5,formal_complete_units=0)
(O/'input-spec-v001.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
A=R/'过程图稿与视频/2026-10-16_软皮轻甲可读性179输入_v001';assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
files=[ref,p,O/'input-spec-v001.json'];rows=[]
for q in files:
 t=A/'原件'/q.name;shutil.copy2(q,t);assert t.read_bytes()==q.read_bytes();rows.append(dict(source=desc(q),retained=desc(t)))
shutil.copy2(ref,A/'展示副本/current158-ready0.png')
(A/'source-version-status-index.json').write_text(json.dumps(dict(files=rows,status='Input only, not yet generated. New light leather honors confirmed item material, old commonbody preserved.',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('179输入：真实当前158Ready0作为唯一身份/姿态参考；轻甲应为褐色软皮，旧灰金属仅研究试样。生成结果未存在，当前UE Source与全部资源保持v121。之后先留原件再审图，单张研究不算完成装备或动作。\n',encoding='utf-8')
print(json.dumps(dict(reference=desc(ref),input_spec=(O/'input-spec-v001.json').as_posix(),archive=A.as_posix()),ensure_ascii=False))
