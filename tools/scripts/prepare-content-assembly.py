"""Merge a hash-frozen hero subset into measured legacy markers, metadata only."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
from PIL import Image

parser=argparse.ArgumentParser()
parser.add_argument('--manifest',required=True)
parser.add_argument('--sha256',required=True)
parser.add_argument('--version',required=True)
parser.add_argument('--base-manifest')
parser.add_argument('--base-sha256')
args=parser.parse_args()
root=Path(__file__).resolve().parents[2]
assert re.fullmatch(r'v[0-9]{3}',args.version)
assert bool(args.base_manifest)==bool(args.base_sha256)
frozen_sources=[]
for name,sha in ([(args.base_manifest,args.base_sha256)] if args.base_manifest else [])+[(args.manifest,args.sha256)]:
    manifest_path=(root/name).resolve()
    assert manifest_path.is_relative_to(root/'source-assets/production')
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest()==sha.lower()
    manifest=json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    assert manifest['frozen']
    marker_path=Path(manifest['assembly_markers_path'])
    assert hashlib.sha256(marker_path.read_bytes()).hexdigest()==manifest['assembly_markers_sha256']
    new=json.loads(marker_path.read_text(encoding='utf-8-sig'))
    assert len({f['frame_path'] for a in new['actions'] for f in a['frames']})==manifest['actual_unique_animation_png_count']
    frozen_sources.extend(new['actions'])
base=json.loads((root/'source-assets/production/first-unit-animation-v001/assembly-markers-v002.json').read_text(encoding='utf-8-sig'))
changed=0
unique_new=set()
for action in frozen_sources:
    assert action['actor']=='hero' and re.fullmatch(r'[a-z0-9_]+',action['action'])
    target=next((a for a in base['actions'] if a['id']==action['action']),None)
    if target is None:
        target={'id':action['action'],'frames':[]};base['actions'].append(target)
    frames=[]
    for index,f in enumerate(action['frames']):
        assert f['frame_index']==index
        path=Path(f['frame_path']);assert hashlib.sha256(path.read_bytes()).hexdigest()==f['frame_sha256']
        im=Image.open(path);assert im.mode=='RGBA' and im.size==(512,512)
        visible=f.get('weapon_visible',True)
        grip=f.get('grip_px')
        if visible:
            assert grip is not None and im.getpixel(tuple(map(round,grip)))[3]==255
            patch_path=Path(f['near_grip_patch_path'])
            assert hashlib.sha256(patch_path.read_bytes()).hexdigest()==f['near_grip_patch_sha256']
            patch=Image.open(patch_path);assert patch.mode=='RGBA' and patch.size==(512,512)
            l,t,r,b=f['near_grip_occlusion_roi_px']
            assert 0<=l<r<=512 and 0<=t<b<=512
            assert im.crop((l,t,r,b)).tobytes()==patch.crop((l,t,r,b)).tobytes()
            polygon=[[l,t],[r,t],[r,b],[l,b]]
        else:
            assert grip is None and f.get('near_grip_patch_path') is None
            grip=[0,0];polygon=[]
        frames.append(dict(index=index,path=str(path),sha256=f['frame_sha256'],grip_px=grip,
            ground_root_px=f['ground_root_px'],weapon_visible=visible,
            weapon_angle_deg_clockwise_screen=f.get('weapon_angle_image_clockwise_deg') or 0,
            near_hand_occlusion={'polygon_px':polygon}))
        changed+=1;unique_new.add(str(path))
    target['frames']=frames
entries=[]
for action in base['actions']:
    for f in action['frames']:
        path=Path(f['path']);assert hashlib.sha256(path.read_bytes()).hexdigest()==f['sha256']
        im=Image.open(path);assert im.mode=='RGBA' and im.size==(512,512)
        visible=f.get('weapon_visible',True)
        if visible:assert im.getpixel(tuple(map(round,f['grip_px'])))[3]>=128
        assert all(math.isfinite(v) for v in f['ground_root_px'])
        polygon=','.join('FVector2D(%s,%s)'%tuple(p) for p in f['near_hand_occlusion']['polygon_px'])
        entries.append('    {TEXT("%s"),%d,FVector2D(%s,%s),FVector2D(%s,%s),%sf,{%s},%s}, // %s'%(
            action['id'],f['index'],*f['grip_px'],*f['ground_root_px'],float(f['weapon_angle_deg_clockwise_screen']),
            polygon,'true' if visible else 'false',f['sha256']))
namespace='DungeonCandidateAssembly'+args.version.upper()
lines=['#pragma once','// Frozen source manifest SHA256 '+args.sha256.lower(),
       '// Candidate measured metadata only; old states remain where not replaced.',
       'namespace '+namespace+' {',
       'struct FMarker { const TCHAR* Clip; int32 Index; FVector2D Grip; FVector2D Root; float Angle; TArray<FVector2D> HandPolygon; bool WeaponVisible; };',
       'inline const FMarker* Find(const FString& Clip,int32 Index) {','    static const FMarker Markers[] = {',
       *entries,'    };','    for(const auto& M:Markers) if(Clip==M.Clip && Index==M.Index) return &M;',
       '    return nullptr;','}',
       'inline int32 Count(const FString& Clip) {int32 N=0;while(Find(Clip,N)) ++N;return N;}',
       'inline constexpr float WeaponScale=.4f;','inline const FVector2D WeaponGrip(99,256);','}','']
if args.base_manifest:lines.insert(2,'// Frozen base manifest SHA256 '+args.base_sha256.lower())
output=root/'UnrealGame/Source/CodexDungeon'/('DungeonCandidateAssembly'+args.version.upper()+'.inl')
text='\n'.join(lines)
if output.exists():assert output.read_text(encoding='utf-8')==text,'Never overwrite differing frozen markers'
else:output.write_text(text,encoding='utf-8')
print(json.dumps(dict(markers=len(entries),new_logical_markers=changed,new_unique_body_PNGs=len(unique_new),
                     old_identity_markers=len(entries)-changed,PNG_changes=0,file=str(output))))
