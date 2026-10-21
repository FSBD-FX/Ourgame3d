from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');A=R/'过程图稿与视频/2026-10-16_守卫纯核后换装运行复核_v001'
S=R/'过程图稿与视频/2026-10-16_军剑真实换装绑定_v005-guardKernelGREEN'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
v=read(S/'原件/runtime-report.json');assert v['passed'] and v['flow_complete'] and not v['mismatches']
assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
for p in [S/'展示副本/equipment-bound-flow-green-silent.mp4']+[S/'原件'/n for n in ['runtime-report.json','independent-bound-flow-verification-v001.json','source-and-snapshot-binding-verification-v001.json','video-presentation-receipt-v001.json']]:
 q=A/('展示副本' if p.suffix=='.mp4' else '原件')/p.name;shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(dict(source=desc(p),copy=desc(q)))
(A/'review-player.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>当前构建换装运行复核</title><style>body{margin:24px;background:#151e23;color:#eae7d9;font:16px system-ui;line-height:1.7}h1{font-size:24px}p{max-width:1100px}video{display:block;width:1280px;max-width:100%;background:#000}button{margin-top:14px;padding:10px 20px}</style><h1>守卫纯核加入后的现有换装回归</h1><p>当前构建148项回归通过。此录像检查原有军剑与灰甲的换装、取消、三段攻击及同件重拾。新179软皮甲参考还未替换进游戏；守卫纯核没有在这个房间生成正式敌人。</p><video id="v" controls preload="auto" src="展示副本/equipment-bound-flow-green-silent.mp4"></video><button onclick="v.currentTime=0;v.play()">从头播放</button><p>换装动作仍借用待机姿势，中甲未适配、世界拾取标记占位；这段录像静音，不能作为音色混音或完整敌人验收。</p></html>''',encoding='utf-8')
(A/'index.json').write_text(json.dumps(dict(source_snapshot='v122 current148',copies=rows,observations=len(v['observations']),browser_playback='pending',formal_complete_units=0,actual_guard_driver=False,new_leather_runtime_import=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('真实普通输入141观察142原PNG对应当前v122 Source/DLL；原视频字节保持。新棕色轻甲仅参考，纯Guard逻辑不是实际敌人展示。待Root完整播放。\n',encoding='utf-8')
print(json.dumps(dict(archive=A.as_posix(),copies=len(rows)),ensure_ascii=False))
