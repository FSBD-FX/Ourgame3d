from pathlib import Path
import hashlib,json,shutil

R=Path('F:/Ourgame')
S=R/'过程图稿与视频/2026-10-16_钟盔军剑三段真实连击试装_v001'
A=R/'过程图稿与视频/2026-10-16_军剑三段连续出招播放复核_v001'
E=R/'docs/production/first-batch-v2/evidence/sword-primary3-native-review-v001'
assert not A.exists()
(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
def desc(p):
    b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
copies=[]
def copy(p,q):
    original=desc(p);shutil.copy2(p,q);assert desc(q)['sha256']==original['sha256']
    copies.append(dict(source=original,copy=desc(q),resampled=False,retimed=False))
video=S/'展示副本/fairytale-sword-primary3-fit-silent.mp4'
assert desc(video)['sha256']=='0164ca94b6f6bbf8bcaf4d39b6d3c346ae8bc18665641cce48032383716fa32d'
copy(video,A/'展示副本/primary3-v116-native-silent.mp4')
for name in ['index.json','source-version-status-index.json']:
    copy(S/name,A/'原件'/('capture-'+name))
for name in ['compiled-source-binding-audit-v001.json','sword-primary3-fit-runtime-verification-v001.json','video-presentation-receipt-v001.json','selected-frame-source-map-v001.json']:
    copy(S/'原件'/name,A/'原件'/name)
assert desc(E/'review-freeze-v001.json')['sha256']=='6927ff0ff362717b5d46e0fa2bd0588c4b6abff9306863c35a821b16b1b091c4'
for name in ['independent-native-review-v001.md','independent-native-review-v001.json','review-freeze-v001.json']:
    copy(E/name,A/'原件'/name)
for index,label in [(34,'windup'),(35,'raised-hand'),(37,'low-finish')]:
    p=next((S/'展示副本').glob(f'crop-selected-{index:02d}-*.png'))
    copy(p,A/f'展示副本/{label}.png')
mapping=json.loads((S/'原件/selected-frame-source-map-v001.json').read_text(encoding='utf-8'))
root_crops=[x for x in mapping['frames'] if (x['clip']=='sword_primary_3') or (x['facing']==1 and x['clip'] in ['sword_primary_1','sword_primary_2'] and x['frame'] in [0,3,5])]
root_boundaries=[x for x in mapping['transition_frames'] if x['observation_index'] in [65,66,67,68,161,162,163,164]]
root_wholes=[x for x in mapping['frames'] if x['clip']=='sword_primary_3' and x['frame'] in [1,3]]
assert len(root_crops)==18 and len(root_boundaries)==8 and len(root_wholes)==4
review=dict(status='NEEDS_WORK; bounded art trial',root_actually_viewed_crops=[x['unscaled_crop'] for x in root_crops+root_boundaries],root_actually_viewed_wholes=[x['presentation_whole'] for x in root_wholes],independent_viewed_crops=20,independent_viewed_wholes=2,findings=['Bell helmet and amber eye window remain readable in selected phases.','No naked-body switch seen in selected P2 to P3 boundary frames.','Phase1 fist, hilt and helmet edge remain crowded; full grasp/overlap clearance unproved.','Phase3 sword is present but thin; tip close to boot/ground baseline; stable clearance unproved.','Small pose jump at row transition; continuous motion and foot lock not accepted.','Grey armor and grey cloth still need stronger large silhouette separation.'],not_accepted=['complete motion','complete equipment binding render','hit/VFX/SFX','all states','all content units'],formal_complete_units=0)
(A/'原件/root-bounded-art-review-v001.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>钟盔军剑 · 三段穿甲实景试样</title>
<style>body{margin:24px;background:#141b21;color:#edf0df;font:16px system-ui}video{display:block;width:1280px;max-width:100%;background:#000}button{margin:16px 8px 16px 0;padding:10px 20px}p{max-width:1050px;line-height:1.65}.crops{display:flex;gap:24px;flex-wrap:wrap}figure{margin:12px 0}figure img{display:block;width:240px;height:150px}figcaption{margin-top:8px;font-size:14px;color:#c0c5bc}</style>
<h1>钟盔军剑：三段穿甲实景试样</h1>
<p>保留怪诞钟盔、琥珀色眼窗和小比例冒险者，胸甲与前后肩甲随攻击分层遮挡。UE5实录，左右各连续三段攻击；画面1280×720，人物身体最高72px，游戏UI隐藏。</p>
<video id="v" controls preload="auto" src="展示副本/primary3-v116-native-silent.mp4"></video>
<button onclick="v.currentTime=0;v.play()">从头播放</button><button onclick="v.pause()">暂停</button>
<p>这版仍是静音试装。蓄力时拳柄与盔缘较挤，低位收刀的剑尖余量、握柄和动作衔接仍需打磨；防具与灰衣的大轮廓区分继续加强。完整状态、换装画面、命中特效和音效尚未验收。</p>
<div class="crops"><figure><img src="展示副本/windup.png"><figcaption>第三段起手 · 原生裁图</figcaption></figure><figure><img src="展示副本/raised-hand.png"><figcaption>抬手蓄力 · 拳盔间隙待修</figcaption></figure><figure><img src="展示副本/low-finish.png"><figcaption>低位终结 · 剑尖余量待修</figcaption></figure></div></html>'''
(A/'review-player.html').write_text(html,encoding='utf-8')
(A/'index.json').write_text(json.dumps(dict(status='v116 actual native three-stage armor trial, Root30 and independent22 stills reviewed NEEDS_WORK; browser playback pending',source_snapshot='source-assets/production/backups/2026-10-16_Primary3Armor48-fit-full141GREEN-v116',copies=copies,observations=198,native_original_pngs=199,capture_duration_s=6.601578898727894,real_action_ids=[1,2,3,4,5,6],full_UE_tests=141,audio_recorded=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('v116左右三段穿甲实录逐字节复制；保留原始运行和独立审图记录。未放大裁图，未更改动作时钟；CFR展示副本的量化与尾帧重复见原始收据。拳盔间隙、低位剑尖、轮廓和完整视听仍需打磨，不代表完整装备接受。\n',encoding='utf-8')
print(json.dumps(dict(archive=A.as_posix(),copied_files=len(copies),root_reviewed_crops=26,root_reviewed_wholes=4,formal_complete_units=0),ensure_ascii=False))
