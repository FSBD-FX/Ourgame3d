from pathlib import Path
import hashlib,json,shutil
from urllib.parse import quote
from PIL import Image
R=Path('F:/Ourgame');A=R/'过程图稿与视频/2026-10-18_棕皮军剑双向行走与三连斩实录_v001'
B=R/'source-assets/production/fairytale-lgt-readability-v003/walk-native-proof-candidate-v001'
O=R/'过程图稿与视频/2026-10-18_Walk实录原比例相位与播放审阅_v002';assert not O.exists()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def fact(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
report=A/'原件/runtime-report.json';verification=A/'原件/independent-walk-proof-verification-v001.json';v=read(verification);assert v['passed'] and v['pixel_verification']['verified_original_PNG_count']==197
assert (A/'index.json').exists() and read(A/'index.json')['status']=='failed_preserved'
continuation=dict(schema='Root-same-originals-reverification-v002',first_run_index_preserved=fact(A/'index.json'),first_failure_preserved=fact(A/'independent-verification-output.txt'),diagnosis='Verifier incorrectly expected normal ScenePreview restart serial0; actual StartPlay->RestartRun->BeginEquipmentRun increments once; Enter only releases waiting. Exact single oracle0->1 repair; all scope/motion/actions/CRC assertions unchanged.',repair_freeze=fact(B/'tooling-freeze-v002.json'),actual_runtime_report=fact(report),same_original_independent_pass=fact(verification),original_game_Source_DLL_PNGs_not_changed=True,game_rerun_for_this_repair=False,complete_units=0)
assert read(A/'Root-verification-continuation-v002.json')==continuation  # retained by failed preparation-v001; never overwrite
assert (A/'README.md').is_file()  # retained original preparation text, unchanged
original=O/'原件';show=O/'展示副本';original.mkdir(parents=True);show.mkdir()
source_map=A/'展示副本/walk-crops-v002/crop-source-map-v001.json';maps=read(source_map)['maps'];assert len(maps)==48
contacts=[]
for kind,stage in [('Walk',-1),('Primary',0),('Primary',1),('Primary',2)]:
 for side in [-1,1]:
  rows=sorted([m for m in maps if m['kind'].lower()==kind.lower() and m['stage']==stage and m['facing']==side],key=lambda x:x['frame'])
  assert [m['frame'] for m in rows]==list(range(6)),(kind,side,stage,[(m['kind'],m['stage']) for m in maps[:5]])
  contact=Image.new('RGB',(1440,160));pins=[]
  for i,m in enumerate(rows):
   p=Path(m['unscaled_crop']['path']);assert p.resolve()==Path(m['unscaled_crop']['path']).resolve() and (p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest())==(m['unscaled_crop']['bytes'],m['unscaled_crop']['sha256'])
   im=Image.open(p);assert im.size==(240,160)
   contact.paste(im,(i*240,0));q=original/'source-crops'/p.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();pins.append(m)
  name=f"{'left' if side<0 else 'right'}-{kind.lower()}-stage{stage+1}-six-UNSCALED-v001.png"
  q=original/name;contact.save(q);shutil.copy2(q,show/name);contacts.append(dict(contact=fact(q),phase_order=list(range(6)),source_rows=pins,rescaled=False))
movie=A/'展示副本/walk-native-core-proof-v001-silent.mp4';assert movie.is_file()
videos=[('左右行走与三连斩',movie),('守卫保存进程',R/'过程图稿与视频/2026-10-18_裂岩守卫V2双进程保存实证_v001/展示副本/guard-v2-source-silent-v001.mp4'),('守卫复开恢复进程',R/'过程图稿与视频/2026-10-18_裂岩守卫V2双进程复开恢复实证_v001/展示副本/guard-v2-restore-silent-v001.mp4')]
links=[dict(title=t,url='/'+quote(p.relative_to(R).as_posix()),file=fact(p)) for t,p in videos]
payload=json.dumps(links,ensure_ascii=False).replace('<','\\u003c')
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>UE行走与存续实录审阅</title><style>body{background:#171a19;color:#eee;font:16px system-ui;margin:20px}button{padding:10px;margin:5px;background:#303932;color:#fff;border:1px solid #6a776d}video{width:100%;max-width:1280px}pre{white-space:pre-wrap}</style><p>UE原生录像，静音。行走使用80世界单位循环步距调参；足锁、受击死亡及完整内容尚未验收。</p><div id="buttons"></div><p id="title"></p><video id="player" controls playsinline preload="metadata"></video><pre id="status"></pre><script>const entries='''+payload+''';const v=document.getElementById('player');function select(i){v.pause();v.src=entries[i].url;document.getElementById('title').textContent=entries[i].title;v.load()}for(let i=0;i<entries.length;i++){const b=document.createElement('button');b.textContent=entries[i].title;b.onclick=()=>select(i);document.getElementById('buttons').appendChild(b)}function update(){document.getElementById('status').textContent=JSON.stringify({source:v.currentSrc,currentTime:v.currentTime,duration:v.duration,ended:v.ended,paused:v.paused,readyState:v.readyState,error:v.error?{code:v.error.code,message:v.error.message}:null},null,2)}v.addEventListener('timeupdate',update);v.addEventListener('loadedmetadata',update);v.addEventListener('ended',update);select(0);</script></html>'''
(original/'review-player.html').write_text(html,encoding='utf-8');shutil.copy2(original/'review-player.html',show/'review-player.html')
(O/'source-version-status-index.json').write_text(json.dumps(dict(schema='Root-native-phase-contact-and-player-v001',source_native_report=fact(report),independent_verification=fact(verification),contacts=contacts,videos=links,root_new_checker_receipt=continuation,actual_source_pixels_changed=False,actually_viewed=False,complete_units=0),ensure_ascii=False,indent=2),encoding='utf-8')
(O/'README.md').write_text('原比例审阅联系图：每格240×160直接来自真实1280×720原帧裁图，未缩放；六相顺序0..5。不是游戏素材或重画。原件、展示副本及来源映射保留；须E留存后实际审看。\n',encoding='utf-8')
print(json.dumps(dict(out=str(O),contacts=len(contacts),phase_pairs=48,video=fact(movie),E_before_view=True),ensure_ascii=False))
