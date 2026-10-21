"""Freeze eight already extracted and registered armor layers; never edit pixels."""
from pathlib import Path
from PIL import Image
import argparse, hashlib, json

p=argparse.ArgumentParser()
p.add_argument('--bracer',required=True);p.add_argument('--shin',required=True)
p.add_argument('--reference',action='append',default=[])
a=p.parse_args()
root=Path('F:/Ourgame').resolve()
out=root/'source-assets/production/fairytale-limb-lookdev-v001'
manifest=out/'manifests/import-limb-lookdev-v001.json'
assert not out.exists(), 'Do not overwrite a source freeze'
def desc(path):
    data=path.read_bytes();return {'path':path.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
references={f'registration_{i}':Path(name).resolve() for i,name in enumerate(a.reference)}
references['armor_contract']=root/'docs/production/first-batch-v2/fairytale-armor-component-contract-v003.md'
for i in range(4): references[f'body131_{i}']=root/f'source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-{i}.png'
for path in references.values(): assert path.is_relative_to(root) and path.is_file(),path
namespace='/Game/Production/ArtTrials/EV048/v002/HeroNearLimbIdle'
assets=[]
for component,folder in [('NearBracer',a.bracer),('NearShin',a.shin)]:
    folder=Path(folder).resolve();assert folder.is_relative_to(root)
    for i in range(4):
        path=folder/f'frame-{i}.png';data=desc(path)
        im=Image.open(path);assert im.mode=='RGBA' and im.size==(512,512) and im.getbbox()
        name=f'T_Fairytale_{component}Idle_{i:03d}_v001'
        assets.append({'component':component,'frame':i,'name':name,'source':path.as_posix(),
                       'source_bytes':data['bytes'],'source_sha256':data['sha256'],'source_bbox':list(im.getbbox()),
                       'package_path':namespace+'/'+name,'object_path':namespace+'/'+name+'.'+name})
assert len({a['source_sha256'] for a in assets})==8
packages=[]
for path in sorted((root/'UnrealGame/Content/Production').rglob('*.uasset')):
    data=desc(path);data['path']=path.relative_to(root).as_posix();packages.append(data)
assert len(packages)==881
manifest.parent.mkdir(parents=True)
(manifest.parent/'old-production881-before-import.json').write_text(json.dumps({'files':packages},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
document={'schema':'frozen-fairytale-near-limb-lookdev-eight-v1','frozen':True,'asset_count':8,'namespace':namespace,
          'canvas_px':[512,512],'durations_ms':[167]*4,'native_facing':1,'display_pivot_px':[256,464],
          'preview_canvas_size':72*512/416,'per_frame_resize':False,'runtime_verified':False,
          'full_motion_accepted':False,'semantic_masks_exist':False,'formal_complete_units':0,
          'scope':'Native near bracer and near shin idle components on canonical131. Art observation only; no actual equipment binding or combat acceptance.',
          'references':{k:desc(v) for k,v in references.items()},'assets':assets}
manifest.write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
checks=root/'tools/scripts/ue_fairytale_limb_lookdev_checks.py';text=checks.read_text(encoding='utf-8')
assert text.count('PENDING_ACTUAL_SOURCE_FREEZE')==1
checks.write_text(text.replace('PENDING_ACTUAL_SOURCE_FREEZE',desc(manifest)['sha256']),encoding='utf-8')
print(json.dumps({'manifest':desc(manifest),'sources':8,'protected_packages':881},ensure_ascii=False))
