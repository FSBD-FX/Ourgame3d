from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path('F:/Ourgame');S=R/'Playables/钟盔轻甲-v142-CM52f906';C=R/'source-assets/production/fairytale-hero-air-v001/stable-fast-launch-candidate-v002';O=R/'过程图稿与视频/2026-10-19_钟盔固定试玩快捷入口与核验_v003'
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
proof=R/'source-assets/production/fairytale-hero-air-v001/root-stable-fast-admission-v002/actual-timed-validation-v002.json';d=json.loads(proof.read_text(encoding='utf-8-sig'));assert d['passed'] is True and d['actual_full_gate_result']['runtime_files']==1778
O.mkdir(exist_ok=False);(O/'原件').mkdir();(O/'展示副本').mkdir();rows=[]
sources=[R/'钟盔轻甲快捷试玩.cmd',R/'tools/scripts/launch-hero-stable-preview-v002.ps1',S/'_proof/tools/launch-stable-preview-v002.ps1',S/'_proof/runtime-snapshot-manifest-v002.json',S/'_proof/Root-stable-approval-v002.json',C/'HeroAir6-stable-fast-launch-candidate-freeze-v002.json',C/'protocol-v002.json',proof,proof.parent/'actual-fast-launch-admission-v002.json']
for i,p in enumerate(sources):
 dst=O/'原件'/(f'{i:02d}-'+p.name);shutil.copy2(p,dst)
 for repeat in range(2):assert (pin(p)['bytes'],pin(p)['sha256'])==(pin(dst)['bytes'],pin(dst)['sha256'])
 rows.append(dict(source=pin(p),copy=pin(dst)))
summary=dict(schema='Root-stable-fast-preview-delivery-v002',utc=datetime.now(timezone.utc).isoformat(),status='LIMITED_WIP',actual_full_gate_elapsed_s=d['elapsed_seconds'],actual_staged_native_frames=174,stable_version='v142-CM52f906',development_version='v143-CM5ddd83f5-Source298-203GREEN',entry=pin(R/'钟盔轻甲快捷试玩.cmd'),sources=rows,old_versions_preserved=True,runtime_art_and_gameplay_unchanged=True,full_realtime_playback_reviewed=False,audio_listened=False,known_pose_join_refinement_open=True,formal_complete_units=0,FinalAccepted=False)
write(O/'展示副本/交付状态-v002.json',summary)
with (O/'README.md').open('x',encoding='utf-8') as f:f.write('钟盔轻甲快捷试玩入口v002：实际1778运行文件与引擎/原生证明完整检查5.7827204秒通过。固定v142保留物理副本；当前开发v143Source298另行推进。仅优化路径读取与显式父manifest链，旧文件/原生174帧/旧入口全部保留。Enter开局、E穿甲、Space跳跃、WASD/J/Shift正常操作。Root仅有限姿态审阅，完整原速观看/试听与动作精修未完成，非正式内容完成。\n')
write(O/'来源-版本-状态索引.json',dict(status='LIMITED_WIP',files=[pin(p) for p in sorted(O.rglob('*')) if p.is_file()],FinalAccepted=False))
print(json.dumps(dict(output=O.as_posix(),files=len(list(O.rglob('*')))),ensure_ascii=False))
