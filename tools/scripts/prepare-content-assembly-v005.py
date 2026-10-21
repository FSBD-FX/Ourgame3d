"""Merge frozen EV042 round-helmet idle and three primary clips, metadata only."""
from pathlib import Path
import hashlib
import json
from PIL import Image

root = Path(__file__).resolve().parents[2]
manifest_path = root / 'source-assets/production/first-unit-animation-v003/import-subset-v003.json'
assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == '96e97a29e7c41fda3856b8e9de47b15ec60d67709291df1a5277080fe7f22ef2'
manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
assert manifest['frozen'] and manifest['actual_unique_animation_png_count'] == 24
marker_path = Path(manifest['assembly_markers_path'])
assert hashlib.sha256(marker_path.read_bytes()).hexdigest() == manifest['assembly_markers_sha256']
new = json.loads(marker_path.read_text(encoding='utf-8-sig'))
base = json.loads((root / 'source-assets/production/first-unit-animation-v001/assembly-markers-v002.json').read_text(encoding='utf-8-sig'))
changed = 0
for action in new['actions']:
    assert action['action'] in {'idle', 'primary_1', 'primary_2', 'primary_3'}
    target = next(a for a in base['actions'] if a['id'] == action['action'])
    assert len(action['frames']) == len(target['frames']) == 6
    frames = []
    for f in action['frames']:
        path, patch_path = Path(f['frame_path']), Path(f['near_grip_patch_path'])
        assert hashlib.sha256(path.read_bytes()).hexdigest() == f['frame_sha256']
        assert hashlib.sha256(patch_path.read_bytes()).hexdigest() == f['near_grip_patch_sha256']
        im, patch = Image.open(path), Image.open(patch_path)
        assert im.mode == patch.mode == 'RGBA' and im.size == patch.size == (512, 512)
        assert im.getpixel(tuple(map(round, f['grip_px'])))[3] == 255
        l, t, r, b = f['near_grip_occlusion_roi_px']
        assert im.crop((l, t, r, b)).tobytes() == patch.crop((l, t, r, b)).tobytes()
        frames.append(dict(index=f['frame_index'], path=str(path), sha256=f['frame_sha256'],
                           grip_px=f['grip_px'], ground_root_px=f['ground_root_px'],
                           weapon_angle_deg_clockwise_screen=f['weapon_angle_image_clockwise_deg'],
                           near_hand_occlusion={'polygon_px': [[l,t],[r,t],[r,b],[l,b]], 'semantics': f['patch_semantics']}))
        changed += 1
    target['frames'] = frames
assert changed == 24
entries = []
for action in base['actions']:
    for f in action['frames']:
        path = Path(f['path'])
        assert hashlib.sha256(path.read_bytes()).hexdigest() == f['sha256']
        im = Image.open(path)
        assert im.mode == 'RGBA' and im.size == (512, 512)
        assert im.getpixel(tuple(map(round, f['grip_px'])))[3] >= 128
        poly = ','.join('FVector2D(%s,%s)' % tuple(p) for p in f['near_hand_occlusion']['polygon_px'])
        entries.append('    {TEXT("%s"),%d,FVector2D(%s,%s),FVector2D(%s,%s),%sf,{%s}}, // %s' % (
            action['id'], f['index'], *f['grip_px'], *f['ground_root_px'], float(f['weapon_angle_deg_clockwise_screen']), poly, f['sha256']))
assert len(entries) == 68
lines = ['#pragma once', '// EV042:24 round-helmet idle/primary frames;44 old identity states still pending.',
         'namespace DungeonCandidateAssemblyV005 {',
         'struct FMarker { const TCHAR* Clip; int32 Index; FVector2D Grip; FVector2D Root; float Angle; TArray<FVector2D> HandPolygon; };',
         'inline const FMarker* Find(const FString& Clip,int32 Index) {', '    static const FMarker Markers[] = {',
         *entries, '    };', '    for(const auto& M:Markers) if(Clip==M.Clip && Index==M.Index) return &M;',
         '    return nullptr;', '}',
         'inline int32 Count(const FString& Clip) {int32 N=0;while(Find(Clip,N)) ++N;return N;}',
         'inline constexpr float WeaponScale=.4f;', 'inline const FVector2D WeaponGrip(99,256);', '}', '']
output = root / 'UnrealGame/Source/CodexDungeon/DungeonCandidateAssemblyV005.inl'
text = '\n'.join(lines)
if output.exists():
    assert output.read_text(encoding='utf-8') == text, 'Never overwrite differing frozen metadata'
else:
    output.write_text(text, encoding='utf-8')
print(json.dumps({'markers':68, 'roundhelmet_frames':24, 'old_identity_frames':44, 'PNG_changes':0, 'file':str(output)}))
