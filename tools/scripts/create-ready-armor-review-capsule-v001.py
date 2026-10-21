from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2'
A=R/'过程图稿与视频/2026-10-16_钟盔胸肩试装复核与失败更正_v001'
assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
files=[D/'runtime-review-fairytale-sword-armor-ready-v002.md',D/'progress.json',R/'README.md',R/'AGENTS.md',R/'项目需求台账.md',
 R/'.superpowers/sdd/2026-10-15-bound-run-capture-restore/progress.md',R/'tools/scripts/checkpoint-sword-armor-ready-v002.py',Path(__file__),
 R/'钟盔军剑低位动作试装.cmd',R/'钟盔军剑胸肩试装.cmd']
for folder in ['docs/production/first-batch-v2/evidence/sword-body-v002','docs/production/first-batch-v2/evidence/sword-armor-ready-v001']:
 files.extend(p for p in (R/folder).glob('*') if p.is_file())
for version in ['2026-10-16_LowGuard158159-actual126GREEN-v099','2026-10-16_SwordReadyArmor24-actual126GREEN-v100','2026-10-16_SwordReadyArmor24-preloadFix-actual126GREEN-v101']:
 root=R/'source-assets/production/backups'/version
 files.append(root/'compiled-source-manifest.json')
 if version.endswith(('v100','v101')):
  files.extend(root/'UnrealGame/Source/CodexDungeon'/name for name in ['DungeonHUD.h','DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp','DungeonFairytaleSwordDrawState.h','DungeonFairytaleSwordProbe.cpp'])
files.extend(R/'UnrealGame/Source/CodexDungeon'/name for name in ['DungeonFairytaleSwordBodyV001.inl','DungeonFairytaleSwordBodyV002.inl'])
for folder in ['source-assets/production/fairytale-sword-v001/ready-measurement-v002','source-assets/production/fairytale-sword-v001/primary1-measurement-v003','source-assets/production/fairytale-sword-runtime-v001/data-export-v003']:
 files.extend(p for p in (R/folder).rglob('*') if p.is_file())
for folder in ['source-assets/production/fairytale-sword-runtime-v002/manifests','source-assets/production/fairytale-sword-armor-ready-runtime-v001/manifests']:
 files.extend(p for p in (R/folder).glob('*') if p.is_file())
files.append(R/'source-assets/production/first-unit-animation-v003/generation-ledger.json')
files.extend(R/'source-assets/production/fairytale-armor-sword-ready-v002/macro-registration-proposed-v001'/name for name in ['visual-review-v001.md','visual-review-v001.json','delivery-freeze-v001.json'])
for name in ['launch-fairytale-sword-body-v002.ps1','launch-fairytale-sword-armor-ready-v001.ps1','verify-ready-body-pixel-presence-v001.py','verify-sword-armor-ready-v001.py','verify-sword-armor-ready-v001.ps1','verify-sword-armor-ready-v002.ps1','postprocess-sword-armor-ready-v001.py','postprocess-sword-armor-ready-v002.py','ue_sword_armor_ready_v001_checks.py','ue-import-sword-armor-ready-v001.py','import-sword-armor-ready-v001.ps1']:
 files.append(R/'tools/scripts'/name)
files.extend((R/'UnrealGame/Saved/Bootstrap').glob('sword-armor-ready-v001-import-*.json'))
files.extend((R/'UnrealGame/Saved/Bootstrap').glob('fairytale-sword-body-v002-import-*.json'))
for version in ['v001','v002']:
 root=R/f'过程图稿与视频/2026-10-16_钟盔军剑低位胸肩真实按键试装_{version}'
 files.extend(root/'原件'/name for name in ['visible-ready-head-gate-v001.json','sword-armor-runtime-verification.json','selected-frame-source-map-v001.json','video-presentation-receipt-v001.json'])
 if version=='v001':files.append(root/'ERRATA-and-visual-failure-v001.md')
files.extend(R/'UnrealGame/Saved/Bootstrap'/name for name in ['build-editor-20261016-111349.log'])
files.append(R/'UnrealGame/Saved/Automation/FirstRoom-20261016-111515/index.json')
entries=[]
for i,p in enumerate(dict.fromkeys(files)):
 assert p.is_file(),p
 t=A/'原件'/f'{i:03d}-{p.name}';assert not t.exists();shutil.copy2(p,t)
 assert desc(p)['sha256']==desc(t)['sha256']
 entries.append({'source':desc(p),'retained_relative':t.relative_to(A).as_posix()})
for name in ['ready-right.png','ready-left.png']:
 source=R/'过程图稿与视频/2026-10-16_低位军剑胸肩试装播放复核_v001/展示副本'/name
 target=A/'展示副本'/name;shutil.copy2(source,target);assert desc(source)['sha256']==desc(target)['sha256']
(A/'README.md').write_text('钟盔胸肩持剑待机候选的实际检查点。保留v100/E164首次消失失败与说明更正、v101/E165修复实录/独立审图/源码审查、明确仅待机甲及下一步。引用的原帧与视频已分别在E164/E165/E166保全。本批局部图是现有原生像素裁切的字节副本，没有放大。完整目标active0/15。\n',encoding='utf-8')
(A/'index.json').write_text(json.dumps({'schema':'ready-armor-review-capsule-v1','files':entries,'size_SHA_mismatches':0,'status':'Postfix startup visibility checked; art candidate only, attack armor/fullstates/equipment/codec/audio unfinished','formal_complete_units':0,'goal_status':'active'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'archive':A.as_posix(),'source_files':len(entries),'bytes':sum(x['source']['bytes'] for x in entries),'mismatches':0},ensure_ascii=False))
