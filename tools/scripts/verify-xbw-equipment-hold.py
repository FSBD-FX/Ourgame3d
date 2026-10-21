"""Read-only visual-stack regression for actual normal-input armor transactions."""
from pathlib import Path
import argparse
import hashlib
import json
import math

p=argparse.ArgumentParser()
p.add_argument('--archive',required=True)
p.add_argument('--output',required=True)
a=p.parse_args()
root=Path('F:/Ourgame')
archive=(root/'过程图稿与视频'/a.archive).resolve()
assert archive.parent==root/'过程图稿与视频'
output=(root/a.output).resolve()
output.relative_to(root/'docs/production/first-batch-v2/evidence')
assert not output.exists(),output
report=json.loads((archive/'原件/runtime-report.json').read_text(encoding='utf-8-sig'))
assert report['profile']=='xbw_four_armor_socket_normal_inputs' and report['passed'] is True
armors=['','ARM-LGT-001','ARM-MED-001','ARM-HVY-001']
old_instances=[0,3,4,5]
groups={i:[] for i in range(4)}
errors=[]

def path(folder,prefix,track,frame):
    name=f'{prefix}_{track}_{frame:03d}_v001'
    return f'/Game/Production/FirstBatch/{folder}/{name}.{name}'

for index,t in enumerate(report['trace']):
    if not(t['equipment_action_active'] and t['fixture_phase']==5):
        continue
    variant=t['armor_variant']
    assert variant in groups
    groups[variant].append(t)
    frame=t['hud_frame']
    state=-1 if t['actual_reload_commits']==0 else 3
    valid=(t['weapon_instance_id']==2 and t['slot_weapon_instance_id']==2
           and abs(t['equipment_action_deadline']-t['equipment_action_start']-.5)<1e-8
           and t['selected_source_id']==variant+2
           and t['actual_armor_id']==armors[variant]
           and t['actual_armor_instance_id']==old_instances[variant]
           and t['actual_ammo']==1 and t['action_active'] is False
           and t['hud_instance_id']==2 and t['hud_action_id']==0
           and t['hud_clip'] in ('xbw_ready_idle','xbw_ready_idle_pose_during_equip_armor')
           and 0<=frame<6 and t['hud_facing']==t['player_facing']
           and t['hud_weapon_state_index']==state
           and math.isfinite(t['hud_sample_time']) and 0<t['hud_sample_time']<=t['sim_time_s'])
    expected=[]
    if frame>=0:
        expected=[path('v016/XBWReadyIdle','T_XBWReadyIdle','body_far',frame)]
        token=armors[variant].replace('-','_')
        if token:
            expected.append(path('v021/XBWArmorReady','T_XBWArmorReady_'+token,'armor_far',frame))
        expected.append('/Game/Production/FirstBatch/v015/WeaponComponents/T_WPN_XBW_001_neutral_v001.T_WPN_XBW_001_neutral_v001'
                        if state<0 else path('v018/XBWReload','T_XBWReload','weapon',state))
        expected.append(path('v016/XBWReadyIdle','T_XBWReadyIdle','body_support',frame))
        if token:
            expected.append(path('v021/XBWArmorReady','T_XBWArmorReady_'+token,'armor_near',frame))
        expected.append(path('v016/XBWReadyIdle','T_XBWReadyIdle','body_near',frame))
    valid=valid and t['actual_draw_stack']==expected
    if not valid:
        errors.append(dict(trace_index=index,variant=variant,sim_time_s=t['sim_time_s'],
                           hud_clip=t['hud_clip'],hud_frame=frame,actual_old_armor=t['actual_armor_id']))

coverage=[]
for variant,rows in groups.items():
    span=rows[-1]['sim_time_s']-rows[0]['sim_time_s'] if rows else 0
    covered=len(rows)>=3 and span>=.35
    coverage.append(dict(variant=variant,observed_rows=len(rows),observed_span_s=span,covered=covered))
passed=not errors and all(c['covered'] for c in coverage)
result=dict(passed=passed,archive=str(archive),normal_profile_checks=29,
            verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            runtime_report_sha256=hashlib.sha256((archive/'原件/runtime-report.json').read_bytes()).hexdigest(),
            additional_readonly_regression='held XBW2 and old armor exact four/six draw stack throughout every observed actual .50 armor transaction',
            checked_actual_rows=sum(len(rows) for rows in groups.values()),coverage=coverage,
            invalid_row_count=len(errors),first_invalid_rows=errors[:8],
            scope='Actual trace draw-call identity and stack only; native PNG visual inspection, audio, walk and full content completion remain separate.')
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
raise SystemExit(0 if passed else 1)
