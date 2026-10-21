from pathlib import Path
import json,hashlib,shutil
R=Path('F:/Ourgame');M=R/'source-assets/production/backups/v125-p1-157G/compiled-source-manifest.json'
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
for kind,name in [('ready','2026-10-17_软皮轻甲左右待机试装_v002-v125'),('default','2026-10-17_军剑真实换装绑定_v007-v125')]:
 A=R/'过程图稿与视频'/name;v=json.loads((A/'原件/runtime-report.json').read_text(encoding='utf-8-sig'));assert v['passed'] and not v['mismatches'];movies=sorted((A/'原件').glob('MovieFrame*.png'));assert len(movies)==len(v['observations'])
 indices=[i for i,x in enumerate(v['observations']) if x['supported'] and x['committed_armor_id']==v['light_instance_id'] and x['clip']==('sword_ready_idle' if kind=='ready' else 'sword_primary_1') and x['frame']==0];assert indices
 p=movies[indices[0]];q=A/'展示副本/native-whole-preview.png';assert not q.exists();shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
 meta=A/'source-version-status-index.json';assert not meta.exists();meta.write_text(json.dumps(dict(snapshot=pin(M),runtime_report=pin(A/'原件/runtime-report.json'),CRC_FIFO=pin(A/'原件/native-pixel-verification.json'),native_original_PNGs=len(movies)+1,presentation_exact_copy=pin(q),copied_native_original=pin(p),kind=kind,status='Actual current native semantic proof passed; original viewpoint retained; complete art/audio/gameplay unit unaccepted',audio_recorded=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');readme=A/'README.md';assert not readme.exists();readme.write_text('v125当前同Source/DLL实录。Ready为新版皮甲左右四帧待机；default为已有旧灰甲完整三提交／三连击流程，两种外观范围明确区分。原PNG不改，展示为原文件逐字节副本；CRC/FIFO/flush通过，全部装备／敌人动作与音效仍未完成。\n',encoding='utf-8')
print('Two exact whole-frame presentation copies and source/version/status indexes prepared; no PNG pixels changed')
