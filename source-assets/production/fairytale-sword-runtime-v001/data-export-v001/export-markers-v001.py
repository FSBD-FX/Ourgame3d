"""Export pinned trial measurements as pure C++ data; independently parse emitted numbers."""
from pathlib import Path
import datetime, hashlib, json, math, re

HERE=Path(__file__).resolve().parent
ART=Path('F:/Ourgame/source-assets/production/fairytale-sword-v001')
CPP=Path('F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordBodyV001.inl')
SPECS=[
 ('Ready','sword_ready_idle',4,ART/'ready-measurement-v001/ready-marker-proposal-v001.json','f0e8a250eaea3b2315ea9c9cf86eab0514ba4f6a0b53a14cc322aedcda8c4f7d'),
 ('Primary1','sword_primary_1',6,ART/'primary1-measurement-v002/primary1-marker-proposal-v002.json','8fddb258171d04c7f72b50b2b5e8a10925bdb010bd061c03c2f66ecf2a05d340')]

def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(p,text):
 assert not p.exists(),f'Never overwrite frozen export: {p}'
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def number(v):
 assert isinstance(v,(int,float)) and math.isfinite(v)
 return repr(float(v))
def vector(v):
 assert len(v)==2
 return f'FVector2D({number(v[0])}, {number(v[1])})'

assert not CPP.exists()
datasets=[]
for label,clip,count,source,pinned in SPECS:
 assert desc(source)['sha256']==pinned,(source,'JSON changed')
 data=json.loads(source.read_text(encoding='utf-8'))
 assert data['state']==clip and len(data['frames'])==count
 for i,frame in enumerate(data['frames']):
  assert frame['frame']==i
  assert desc(Path(frame['source']['path']))==frame['source'],'Actual image changed'
  assert frame['source_root_px']==[256,464]
  assert len(frame['visible_fist_replay_polygon_candidate_px'])>=3
 copy=HERE/'inputs'/source.name;assert not copy.exists();copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(source.read_bytes())
 datasets.append((label,clip,count,source,pinned,data,copy))

lines=['#pragma once', '#include "CoreMinimal.h"', '',
 '// Generated only from retained native155 Ready and native157 Primary1 measurements.',
 '// TRIAL DATA: thumb anatomy, hidden grip axis, blade sign and fist semantic masks are NOT accepted.',
 '// Axis is copied exactly; no normalization, rotation, blade-end sign choice or V007 marker reuse.',
 '// Root is the fixed display pivot, not a claim of exact per-frame sole-center registration.',
 'namespace DungeonFairytaleSwordBodyV001', '{',
 'struct FMarker', '{', '    FVector2D Root;', '    FVector2D Grip;', '    FVector2D Axis;',
 '    TArray<FVector2D> FistPolygon;', '};', '',
 'inline constexpr double CanvasSize = 72. * 512. / 416.;', '',
 'inline int32 Count(const FString& Clip)', '{']
for label,clip,count,source,pinned,data,copy in datasets:
 lines.append(f'    if (Clip == TEXT("{clip}")) return {count};')
lines+=['    return 0;', '}', '', 'inline const FMarker* Find(const FString& Clip, int32 Index)', '{',
        '    if (Index < 0) return nullptr;']
for label,clip,count,source,pinned,data,copy in datasets:
 lines += [f'    if (Clip == TEXT("{clip}"))', '    {',
           f'        // JSONSha256: {pinned}',f'        // JSONSource: {source.as_posix()}',
           f'        static const FMarker {label}Markers[] =', '        {']
 for i,f in enumerate(data['frames']):
  lines.append(f'            // Frame {i} SourceSha256: {f["source"]["sha256"]}')
  vals=[vector(f['source_root_px']),vector(f['grip_candidate_px']),vector(f['handle_axis_candidate_xy'])]
  poly=', '.join(vector(v) for v in f['visible_fist_replay_polygon_candidate_px'])
  lines.append('            FMarker{' + ', '.join(vals) + ', TArray<FVector2D>{' + poly + '}},')
 lines += ['        };', f'        return Index < UE_ARRAY_COUNT({label}Markers) ? &{label}Markers[Index] : nullptr;', '    }']
lines+=['    return nullptr;', '}', '} // namespace DungeonFairytaleSwordBodyV001', '']
write(CPP,'\n'.join(lines))

# Read the actual emitted C++ text with a separate parser; compare every numeric scalar.
text=CPP.read_text(encoding='utf-8');checks=[];scalar_count=0;polygon_points=0
for label,clip,count,source,pinned,data,copy in datasets:
 section=re.search(r'static const FMarker '+label+r'Markers\[\] =\s*\{(.*?)\n        \};',text,re.S).group(1)
 emitted=[s for s in section.splitlines() if s.strip().startswith('FMarker{')]
 assert len(emitted)==count
 parsed=[]
 for i,line in enumerate(emitted):
  pairs=[[float(x),float(y)] for x,y in re.findall(r'FVector2D\(([-+0-9.eE]+), ([-+0-9.eE]+)\)',line)]
  f=data['frames'][i]
  expected=[f['source_root_px'],f['grip_candidate_px'],f['handle_axis_candidate_xy']]+f['visible_fist_replay_polygon_candidate_px']
  assert pairs==expected,(label,i,pairs,expected)
  scalar_count+=len(pairs)*2;polygon_points+=len(pairs)-3
  parsed.append({'frame':i,'root':pairs[0],'grip':pairs[1],'axis':pairs[2],'fist_polygon':pairs[3:],'all_numeric_fields_exact':True,'source_image':f['source']})
 assert f'if (Clip == TEXT("{clip}")) return {count};' in text
 assert f'return Index < UE_ARRAY_COUNT({label}Markers) ? &{label}Markers[Index] : nullptr;' in text
 checks.append({'clip':clip,'count':count,'input':desc(source),'frozen_input_copy':desc(copy),'cpp_readback_frames':parsed})
assert 'if (Index < 0) return nullptr;' in text
assert text.count('inline const FMarker* Find(')==1
assert text.count('inline int32 Count(')==1
assert 'inline constexpr double CanvasSize = 72. * 512. / 416.;' in text
report={'schema':'fairytale-sword-pure-data-export-numeric-audit-v1','created_local':datetime.datetime.now().astimezone().isoformat(),
 'output':desc(CPP),'json_and_source_image_sha_matches':True,'clips':checks,
 'total_frames':10,'total_numeric_scalars_compared':scalar_count,'total_fist_polygon_points':polygon_points,
 'numeric_mismatches':0,'exact_preserved_fields':['source_root_px','grip_candidate_px','handle_axis_candidate_xy','visible_fist_replay_polygon_candidate_px'],
 'invalid_index_policy':'Index<0 or Index>=count -> nullptr','unknown_clip_policy':'Find -> nullptr; Count ->0',
 'static_interface_text_checks_passed':True,'compiled_or_ue_executed':False,
 'images_or_frozen_source_measurements_modified':False,'old_markers_reused':False,'blade_sign_or_angle_designed':False,
 'formal_complete_units':0,'scope':'New unused pure-data include only. Original candidate uncertainty, thumb failure and trial boundary remain unchanged.'}
rp=HERE/'numeric-readback-audit-v001.json';write(rp,json.dumps(report,ensure_ascii=False,indent=2)+'\n')
files=sorted([p for p in HERE.rglob('*') if p.is_file()]+[CPP])
fp=HERE/'export-freeze-v001.json';write(fp,json.dumps({'schema':'fairytale-sword-pure-data-export-freeze-v1','file_count':len(files),'total_bytes':sum(x.stat().st_size for x in files),'files':[desc(x) for x in files],'scope':'New inl + export evidence only; no existing Source changed. Not compiled/used yet.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'cpp':desc(CPP),'numeric_audit':desc(rp),'freeze':desc(fp),'numeric_scalars':scalar_count,'polygon_points':polygon_points},ensure_ascii=False))
