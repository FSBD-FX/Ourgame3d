"""Freeze eight actual integer-registered layers for an opt-in UE observation."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil
root=Path('F:/Ourgame');base=root/'source-assets/production/fairytale-armor-v001/independent-limb-components-v001'
out=root/'source-assets/production/fairytale-shoulder-lookdev-v001';manifest=out/'manifests/import-shoulder-lookdev-v001.json'
assert not out.exists()
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
references={
 'contract':root/'docs/production/first-batch-v2/fairytale-armor-component-contract-v003.md',
 'near_registration':base/'near149-registration-proposed-v001/registration-receipt-v001.json',
 'near_frames':base/'run-shoulder-near-idle-v001/frames/frames-manifest.json',
 'far_registration':base/'far150-registration-proposed-v001/registration-receipt-v001.json',
 'far_frames':base/'run-shoulder-far-idle-v001/frames/frames-manifest.json',
}
for i in range(4):references[f'body131_{i}']=root/f'source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-{i}.png'
for p in references.values():assert p.is_file(),p
assets=[];namespace='/Game/Production/ArtTrials/EV048/v001/HeroShoulderIdle'
for side,folder in [('Near','near149-registration-proposed-v001/armor-near'),('Far','far150-registration-proposed-v001/armor-far')]:
 for i in range(4):
  p=base/f'{folder}/frame-{i}.png';v=desc(p);im=Image.open(p);assert im.mode=='RGBA' and im.size==(512,512)
  name=f'T_Fairytale_Shoulder{side}Idle_{i:03d}_v001'
  assets.append({'side':side,'frame':i,'name':name,'source':p.as_posix(),'source_bytes':v['bytes'],'source_sha256':v['sha256'],
   'source_bbox':list(im.getbbox()),'package_path':namespace+'/'+name,'object_path':namespace+'/'+name+'.'+name})
assert len({a['source_sha256'] for a in assets})==8
packages=[]
for p in sorted((root/'UnrealGame/Content/Production').rglob('*.uasset')):
 v=desc(p);v['path']=p.relative_to(root).as_posix();packages.append(v)
assert len(packages)==873
manifest.parent.mkdir(parents=True)
(manifest.parent/'old-production873-before-import.json').write_text(json.dumps({'files':packages},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d={'schema':'frozen-fairytale-shoulder-lookdev-eight-v1','frozen':True,'asset_count':8,'namespace':namespace,
 'canvas_px':[512,512],'durations_ms':[167]*4,'native_facing':1,'display_pivot_px':[256,464],'preview_canvas_size':72*512/416,
 'per_frame_resize':False,'runtime_verified':False,'full_motion_accepted':False,'semantic_masks_exist':False,
 'formal_complete_units':0,'scope':'Actual149near4/150far4 separate A-registered armor layers for72px observation only; no formalarmor or occlusion/weapon acceptance',
 'references':{k:desc(p) for k,p in references.items()},'assets':assets}
manifest.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');mh=desc(manifest)['sha256']
checks=root/'tools/scripts/ue_fairytale_shoulder_lookdev_checks.py';text=checks.read_text(encoding='utf-8');assert text.count('PENDING_ACTUAL_SOURCE_FREEZE')==1
checks.write_text(text.replace('PENDING_ACTUAL_SOURCE_FREEZE',mh),encoding='utf-8')
copy=out/'import-tool-version-used';copy.mkdir()
for name in ['ue_fairytale_shoulder_lookdev_checks.py','ue-import-fairytale-shoulder-lookdev-v001.py','import-fairytale-shoulder-lookdev-v001.ps1','verify-fairytale-shoulder-lookdev.py','verify-fairytale-shoulder-lookdev.ps1',Path(__file__).name]:
 p=root/'tools/scripts'/name;shutil.copy2(p,copy/name)
print(json.dumps({'manifest':manifest.as_posix(),'sha256':mh,'actual_source_count':8,'old_protected_packages':873,'formal_complete_units':0},ensure_ascii=False))
