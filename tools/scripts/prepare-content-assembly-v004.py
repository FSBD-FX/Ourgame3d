"""Merge6 EV042 helmet idle and18 corrected primary markers with44 unchanged.

Only metadata/C++ is produced; no PNG editing, scaling or bitmap fabrication.
"""
from pathlib import Path
import hashlib,json
from PIL import Image
root=Path(__file__).resolve().parents[2]
base_path=root/'source-assets/production/first-unit-animation-v001/assembly-markers-v002.json'
primary_path=root/'source-assets/production/first-unit-animation-v002/assembly-markers-import-v002.json'
idle_manifest_path=root/'source-assets/production/first-unit-animation-v003/import-subset-v001.json'
assert hashlib.sha256(idle_manifest_path.read_bytes()).hexdigest()=='95f362ea3b19af1e4c14fb4c2c3b8a4703ccb205b0ffbee45f6d50ca16ccf536'
idle_manifest=json.loads(idle_manifest_path.read_text(encoding='utf-8-sig'))
idle_path=root/'source-assets/production/first-unit-animation-v003/assembly-markers-import-v001.json'
base=json.loads(base_path.read_text(encoding='utf-8-sig'))
changed=0
for new_path,expected_hash in [(primary_path,'78bdd628feebcf991b92c0032e69dc51050306680a31b033f0e64ec831a7e81f'),(idle_path,idle_manifest['assembly_markers_sha256'])]:
    assert hashlib.sha256(new_path.read_bytes()).hexdigest()==expected_hash
    new=json.loads(new_path.read_text(encoding='utf-8-sig'))
    for action in new['actions']:
        target=next(a for a in base['actions'] if a['id']==action['action'])
        assert len(action['frames'])==len(target['frames'])==6
        frames=[]
        for f in action['frames']:
            path=Path(f['frame_path']);patch_path=Path(f['near_grip_patch_path'])
            assert hashlib.sha256(path.read_bytes()).hexdigest()==f['frame_sha256']
            assert hashlib.sha256(patch_path.read_bytes()).hexdigest()==f['near_grip_patch_sha256']
            im=Image.open(path);patch=Image.open(patch_path);assert im.mode==patch.mode=='RGBA' and im.size==patch.size==(512,512)
            x,y=f['grip_px'];assert im.getpixel((round(x),round(y)))[3]==255
            l,t,r,b=f['near_grip_occlusion_roi_px']
            assert im.crop((l,t,r,b)).tobytes()==patch.crop((l,t,r,b)).tobytes()
            frames.append(dict(index=f['frame_index'],path=str(path),sha256=f['frame_sha256'],grip_px=f['grip_px'],
                ground_root_px=f['ground_root_px'],weapon_angle_deg_clockwise_screen=f['weapon_angle_image_clockwise_deg'],
                near_hand_occlusion={'polygon_px':[[l,t],[r,t],[r,b],[l,b]],'semantics':f['patch_semantics']}))
            changed+=1
        target['frames']=frames
assert changed==24
entries=[]
for action in base['actions']:
    for f in action['frames']:
        path=Path(f['path']);assert hashlib.sha256(path.read_bytes()).hexdigest()==f['sha256']
        im=Image.open(path);assert im.mode=='RGBA' and im.size==(512,512)
        assert im.getpixel(tuple(map(round,f['grip_px'])))[3]>=128
        poly=','.join('FVector2D(%s,%s)'%tuple(p) for p in f['near_hand_occlusion']['polygon_px'])
        entries.append('    {TEXT("%s"),%d,FVector2D(%s,%s),FVector2D(%s,%s),%sf,{%s}}, // %s'%(
            action['id'],f['index'],*f['grip_px'],*f['ground_root_px'],float(f['weapon_angle_deg_clockwise_screen']),poly,f['sha256']))
assert len(entries)==68
lines=['#pragma once','// EV042 measured merge;6 helmet idle,18 corrected primary,44 old frames. Other identity states pending.',
       'namespace DungeonCandidateAssemblyV004 {',
       'struct FMarker { const TCHAR* Clip; int32 Index; FVector2D Grip; FVector2D Root; float Angle; TArray<FVector2D> HandPolygon; };',
       'inline const FMarker* Find(const FString& Clip,int32 Index) {','    static const FMarker Markers[] = {',*entries,'    };',
       '    for(const auto& M:Markers) if(Clip==M.Clip && Index==M.Index) return &M;','    return nullptr;','}',
       'inline int32 Count(const FString& Clip) {int32 N=0;while(Find(Clip,N)) ++N;return N;}',
       'inline constexpr float WeaponScale=.4f;','inline const FVector2D WeaponGrip(99,256);','}','']
output=root/'UnrealGame/Source/CodexDungeon/DungeonCandidateAssemblyV004.inl'
text='\n'.join(lines)
if output.exists():assert output.read_text(encoding='utf-8')==text,'Never overwrite differing frozen metadata'
else:output.write_text(text,encoding='utf-8')
print(json.dumps({'markers':68,'new_helmet_idle_frames':6,'corrected_old_identity_primary_frames':18,'unchanged_old_identity_frames':44,'PNG_changes':0,'file':str(output)}))
