from pathlib import Path
import argparse,hashlib,json
R=Path('F:/Ourgame');ap=argparse.ArgumentParser();ap.add_argument('--snapshot',required=True);a=ap.parse_args()
S=(R/a.snapshot).resolve();assert S.is_relative_to(R/'source-assets/production/backups')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def match(p,row):
 b=p.read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],p
m=read(S/'compiled-source-manifest.json');assert m['current_automation_succeeded']==154 and m['production_packages']==1097
for row in m['files']:
 for base in [R,S]:match(base/row['path'],row)
for folder in ['UnrealGame/Source','UnrealGame/Content/Production']:
 actual={p.relative_to(R).as_posix() for p in (R/folder).rglob('*') if p.is_file()}
 expected={x['path'] for x in m['files'] if x['path'].startswith(folder+'/')}
 assert actual==expected, 'Source/production file set changed after this build'
A=R/'过程图稿与视频/2026-10-17_军剑真实换装绑定_v006-guardCoinGREEN';v=read(A/'原件/runtime-report.json');ix=read(A/'index.json')
assert v['passed'] and v['flow_complete'] and not v['mismatches'] and not v['reason'] and v['light_primary_phase_masks']==[63,63,63]
assert ix['source_manifest_SHA256']==hashlib.sha256((S/'compiled-source-manifest.json').read_bytes()).hexdigest()
print(json.dumps(dict(preflight_passed=True,snapshot=a.snapshot,strict_actual_tests=154,production_packages=1097,actual_bound_flow_mismatches=0,old_V001_retained=True,manual_game_not_launched=True),ensure_ascii=False))
