"""Attach an immutable compiled snapshot and exact used tools before retention."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

p=argparse.ArgumentParser()
p.add_argument('--archive',required=True)
p.add_argument('--snapshot',required=True)
p.add_argument('--capture-script',default='tools/scripts/verify-content-combat.ps1',
               choices=('tools/scripts/verify-content-combat.ps1','tools/scripts/verify-fairytale-lookdev.ps1'))
p.add_argument('--pixel-verifier',default='tools/scripts/verify-native-capture-pixels.py',
               choices=('tools/scripts/verify-native-capture-pixels.py','tools/scripts/verify-fairytale-lookdev.py'))
a=p.parse_args()
root=Path('F:/Ourgame')
archive=(root/'过程图稿与视频'/a.archive).resolve()
snapshot=(root/'source-assets/production/backups'/a.snapshot).resolve()
assert archive.parent==root/'过程图稿与视频' and snapshot.parent==root/'source-assets/production/backups'
index=json.loads((archive/'index.json').read_text(encoding='utf-8-sig'))
manifest=json.loads((snapshot/'compiled-source-manifest.json').read_text(encoding='utf-8-sig'))
files={r['path']:r for r in manifest['files']}
assert index['module_sha256'].lower()==files['UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll']['sha256']
for name,sha in index['source_sha256_at_capture'].items():
    assert sha.lower()==files['UnrealGame/Source/CodexDungeon/'+name]['sha256'],name
assert index['capture_script_sha256'].lower()==files[a.capture_script]['sha256']
if 'verifier_sha256' in index:
    assert index['verifier_sha256'].lower()==files[a.pixel_verifier]['sha256']
copied=[]
for relative,name in [
    ('compiled-source-manifest.json','compiled-source-manifest-'+a.snapshot.rsplit('-',1)[-1]+'.json'),
    (a.capture_script,'capture-script-used.ps1'),
    (a.pixel_verifier,'native-pixel-verifier-used.py'),
]:
    source=snapshot/relative
    target=archive/'原件'/name
    assert source.is_file() and not target.exists(),target
    shutil.copy2(source,target)
    assert source.read_bytes()==target.read_bytes()
    copied.append(dict(file=name,bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
index['compiled_snapshot_provenance']=dict(snapshot=str(snapshot),files=copied,source_DLL_and_capture_script_exact_match=True)
(archive/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(index['compiled_snapshot_provenance'],ensure_ascii=False))
