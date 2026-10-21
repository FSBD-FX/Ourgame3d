"""New V002 trial data from native158/159 JSON; no existing Source or sourceart edits."""
from pathlib import Path
import argparse, datetime, hashlib, json, math, re

HERE=Path(__file__).resolve().parent
ART=Path('F:/Ourgame/source-assets/production/fairytale-sword-v001')
CPP=Path('F:/Ourgame/UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordBodyV002.inl')
V1=CPP.with_name('DungeonFairytaleSwordBodyV001.inl')
parser=argparse.ArgumentParser()
parser.add_argument('--audit-existing',action='store_true',help='Do not rewrite emitted Source or copied input; finish the corrected parser audit only.')
audit_existing=parser.parse_args().audit_existing
SPECS=[
 ('Ready','sword_ready_idle',4,158,ART/'ready-measurement-v002/ready-marker-proposal-v002.json','3aff15e506328c9b37aca2e040b56ad6aeca0f6b6d195865ef362fe74adf1e82'),
 ('Primary1','sword_primary_1',6,159,ART/'primary1-measurement-v003/primary1-marker-proposal-v003.json','730f1be4bc17ab4bb2fb520b22c810dc8f392f9e6d1886e3e303ad06cc05b4aa'),
]

def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(p,s):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(s if isinstance(s,str) else json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def number(v):
 assert isinstance(v,(int,float)) and math.isfinite(v)
 return repr(float(v))
def vec(p):
 assert len(p)==2
 return 'FVector2D('+number(p[0])+', '+number(p[1])+')'

assert CPP.exists() if audit_existing else not CPP.exists()
before_v1=desc(V1)
assert before_v1['sha256']=='022d0cff100f3323f6b40c64d929ad6077ae351a5a47a1c5a7a1cd2fc6ad35dd'
data=[]
for label,clip,count,native,p,pin in SPECS:
 assert desc(p)['sha256']==pin
 d=json.loads(p.read_text(encoding='utf-8'))
 assert d['state']==clip and d['native_request']==native and len(d['frames'])==count
 for i,f in enumerate(d['frames']):
  assert f['frame']==i and desc(Path(f['source']['path']))==f['source']
  assert f['actual_handle_axis_xy'] is None and f['actual_blade_end_direction_xy'] is None
  assert f['axis_is_measured'] is False and not f['thumb_anatomy_accepted']
  assert f['source_root_px']==[256,464] and len(f['visible_fist_replay_polygon_candidate_px'])>=3
 q=HERE/'inputs'/p.name
 if audit_existing:
  assert q.read_bytes()==p.read_bytes()
 else:
  q.parent.mkdir(parents=True,exist_ok=True);assert not q.exists();q.write_bytes(p.read_bytes())
 data.append((label,clip,count,native,p,pin,d,q))

lines=['#pragma once','#include "DungeonFairytaleSwordBodyV001.inl"','',
 '// Native158 Ready + native159 Primary1 trial candidates only; no old marker DATA reused.',
 '// V001 supplies the FMarker TYPE only. These arrays use the new retained JSON values.',
 '// Axis is an explicit directed trial design choice: actual handle/blade direction is null.',
 '// Thumb anatomy and exact fist semantic masks remain unaccepted; original uncertainty remains.',
 '// Root is a fixed display pivot, not a measured physical foot joint. No per-frame registration.',
 '// Standard SG Primary1 GIF/atlas timing failed (6x100ms); actual combat phase uses unchanged',
 '// request85/85/60/60/155/155ms through GetPrimaryPoseFrame, never this preview clock.',
 'namespace DungeonFairytaleSwordBodyV002','{',
 'using FMarker = DungeonFairytaleSwordBodyV001::FMarker;','',
 'inline constexpr double CanvasSize = 72. * 512. / 416.;','',
 'inline int32 Count(const FString& Clip)','{']
for label,clip,count,native,p,pin,d,q in data:
 lines.append(f'    if (Clip == TEXT("{clip}")) return {count};')
lines+=['    return 0;','}','','inline const FMarker* Find(const FString& Clip, int32 Index)','{','    if (Index < 0) return nullptr;']
for label,clip,count,native,p,pin,d,q in data:
 lines += [f'    if (Clip == TEXT("{clip}"))','    {',f'        // JSONSha256: {pin}',
           f'        // JSONSource: {p.as_posix()}',f'        static const FMarker {label}Markers[] =','        {']
 for i,f in enumerate(d['frames']):
  lines += [f'            // Frame {i} SourceSha256: {f["source"]["sha256"]}',
            f'            // SourcePath: {f["source"]["path"]}']
  vals=[vec(f['source_root_px']),vec(f['grip_candidate_px']),vec(f['handle_axis_candidate_xy'])]
  poly=', '.join(vec(x) for x in f['visible_fist_replay_polygon_candidate_px'])
  lines.append('            FMarker{'+', '.join(vals)+', TArray<FVector2D>{'+poly+'}},')
 lines += ['        };',f'        return Index < UE_ARRAY_COUNT({label}Markers) ? &{label}Markers[Index] : nullptr;','    }']
lines += ['    return nullptr;','}','} // namespace DungeonFairytaleSwordBodyV002','']
if audit_existing:
 assert CPP.read_text(encoding='utf-8')=='\n'.join(lines)
else:
 write(CPP,'\n'.join(lines))

# Reverse-read the emitted file with a parser independent of the text formatter.
text=CPP.read_text(encoding='utf-8');checks=[];scalars=0;poly_count=0
for label,clip,count,native,p,pin,d,q in data:
 section=re.search(r'static const FMarker '+label+r'Markers\[\] =\s*\{(.*?)\n        \};',text,re.S).group(1)
 emitted=[s for s in section.splitlines() if s.strip().startswith('FMarker{')]
 assert len(emitted)==count
 actual=[]
 for i,line in enumerate(emitted):
  pairs=[[float(x),float(y)] for x,y in re.findall(r'FVector2D\(([-+0-9.eE]+), ([-+0-9.eE]+)\)',line)]
  f=d['frames'][i]
  expected=[f['source_root_px'],f['grip_candidate_px'],f['handle_axis_candidate_xy']]+f['visible_fist_replay_polygon_candidate_px']
  assert pairs==expected,(label,i,pairs,expected)
  assert f'// Frame {i} SourceSha256: {f["source"]["sha256"]}' in section
  assert f'// SourcePath: {f["source"]["path"]}' in section
  scalars+=len(pairs)*2;poly_count+=len(pairs)-3
  actual.append({'frame':i,'root':pairs[0],'grip':pairs[1],'axis':pairs[2],
                'fist_polygon':pairs[3:],'numeric_exact':True,'source_image':f['source']})
 assert f'if (Clip == TEXT("{clip}")) return {count};' in text
 # JSON metadata precedes the array and is intentionally outside the array-only regex.
 assert f'// JSONSha256: {pin}' in text and f'// JSONSource: {p.as_posix()}' in text
 assert f'return Index < UE_ARRAY_COUNT({label}Markers) ? &{label}Markers[Index] : nullptr;' in text
 checks.append({'clip':clip,'count':count,'native_request':native,'input':desc(p),'frozen_input':desc(q),'readback':actual})
assert desc(V1)==before_v1
assert text.count('using FMarker = DungeonFairytaleSwordBodyV001::FMarker;')==1
assert 'DungeonFairytaleSwordBodyV001::Find' not in text and 'DungeonFairytaleSwordBodyV001::Count' not in text
assert 'if (Index < 0) return nullptr;' in text and text.count('inline const FMarker* Find(')==1
assert text.count('inline int32 Count(')==1 and 'inline constexpr double CanvasSize = 72. * 512. / 416.;' in text
report={'schema':'fairytale-sword-v002-pure-data-reverse-read-audit-v1',
 'created_local':datetime.datetime.now().astimezone().isoformat(),'output':desc(CPP),
 'old_v001_before_and_after':before_v1,'old_source_unchanged':True,'type_alias_only':True,
 'clips':checks,'total_frames':10,'total_numeric_scalars_compared':scalars,
 'total_fist_polygon_points':poly_count,'numeric_mismatches':0,'axes_normalized':False,
 'source_and_json_hashes_exact':True,'Count_unknown':0,'Find_negative_or_out_of_range_or_unknown':'nullptr',
 'interface_checks':'Static emitted-text checks, not UE compilation or an independent human code review.',
 'images_or_frozen_measurements_modified':False,'presenter_or_HUD_modified':False,
 'actual_handle_axis_and_blade_end_remain_null':True,'exported_axis_is_trial_design_choice':True,
 'compiled_or_UE_executed':False,'formal_complete_units':0}
if audit_existing:
 report['first_writer_attempt']={'exit_code':1,'reason':'Audit incorrectly searched preceding JSON metadata within the array-only regex. Actual emitted header and copied inputs remain byte-identical.',
                                'parser_scope_corrected':True,'source_rewritten_on_retry':False}
rp=HERE/'numeric-readback-audit-v002.json';write(rp,report)
files=sorted([p for p in HERE.rglob('*') if p.is_file()]+[CPP])
fp=HERE/'export-freeze-v002.json'
write(fp,{'schema':'fairytale-sword-v002-data-export-freeze-v1','file_count':len(files),
 'total_bytes':sum(p.stat().st_size for p in files),'files':[desc(p) for p in files],
 'scope':'Only new V002 include and export evidence; source author is not an independent reviewer. No include/compile/import or running integration performed.'})
print(json.dumps({'cpp':desc(CPP),'audit':desc(rp),'freeze':desc(fp),
                  'numeric_scalars':scalars,'polygon_points':poly_count},ensure_ascii=False))
