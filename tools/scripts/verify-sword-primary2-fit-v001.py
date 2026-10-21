"""Verify real paired J/kernel phases and source binding, not motion taste."""
from pathlib import Path
import argparse
import importlib.util
import json
import math

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser();p.add_argument('--archive');p.add_argument('--preflight-only',action='store_true');a=p.parse_args()
def module(name, filename):
    s=importlib.util.spec_from_file_location(name,Path(__file__).with_name(filename));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
body=module('fit_body','ue_fairytale_sword_body_v002_checks.py').preflight(False)
ready=module('fit_ready','ue_sword_armor_ready_v001_checks.py').preflight(False)
primary=module('fit_primary','ue_sword_armor_primary1_v001_checks.py').preflight(False)
second=module('fit_second','ue_sword_primary2_v001_checks.py').preflight(False)
markers=json.loads(Path(second['marker_json']['path']).read_text(encoding='utf-8-sig'))
if a.preflight_only:
    print(json.dumps({'actual_second_imported_saved':6,'old983_unchanged':True,'armor_only_ready_primary1':True}));raise SystemExit(0)
archive=Path(a.archive).resolve();original=archive/'原件'
r=json.loads((original/'runtime-report.json').read_text(encoding='utf-8-sig'))
assert r['schema']=='fairytale-sword-normal-input-capture-v1' and r['passed'] and r['primary2_fit_trial']
assert r['native_async_capture_writes_flushed'] and r['silent_video'] and not r['audio_recorded']
rows=r['observations'];times=r['capture_timing']['frame_wall_offsets_s'];duration=r['capture_timing']['requested_video_wall_duration_s']
assert len(rows)>160 and len(times)==len(rows) and 6.6<=duration<8 and not r['capture_timing']['use_fixed_time_step']
assert all(math.isfinite(t) for t in times) and all(b>a for a,b in zip(times,times[1:]))
assets={(x['clip'],x['frame']):x for x in body['assets']+second['assets']}
armor_ready={(x['component'],x['frame']):x['object_path'] for x in ready['assets']}
armor_first={(x['component'],x['frame']):x['object_path'] for x in primary['assets']}
masks={(side,clip):0 for side in (-1,1) for clip in ('Ready','Primary1','Primary2')}
actions={(side,clip):set() for side in (-1,1) for clip in ('Primary1','Primary2')}
runs=set();draws=[];second_samples=0
for d in rows:
    assert d['hud'] and d['player'] and d['active'] and d['texture_ready']
    assert not d['interface_visible'] and d['text_calls']==0
    assert math.isclose(d['canvas_size'],72*512/416,abs_tol=1e-9) and d['root']==[256,464]
    assert d['facing'] in (-1,1) and d['run'];runs.add(d['run']);draws.append(int(d['draw_id']))
    if not d['supported']:
        assert not d['weapon'] and len(d['draw_stack'])==1 and not d['armor_drawn']
        continue
    clip={'sword_ready_idle':'Ready','sword_primary_1':'Primary1','sword_primary_2':'Primary2'}[d['clip']]
    frame=d['frame'];asset=assets[(clip,frame)]
    assert d['texture']==asset['object_path'] and d['weapon']=='/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002'
    assert d['weapon_scale']==.5 and math.isclose(d['weapon_width'],72*512/416*.5,abs_tol=1e-4)
    assert d['armor_preview']
    if clip=='Ready':
        assert d['armor_ready'] and d['armor_drawn']
        expected=[armor_ready[(c,frame)] for c in ('BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear')]+[d['weapon'],armor_ready[('NearHand',frame)]]
    elif clip=='Primary1':
        assert d['armor_ready'] and d['armor_drawn']
        expected=[armor_first[(c,frame)] for c in ('BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground')]+[d['weapon'],armor_first[('NearHand',frame)]]
    else:
        assert not d['armor_drawn'] and not d['armor_ready']
        expected=[asset['object_path'],d['weapon'],asset['object_path']]
        marker=markers['markers'][frame]
        assert d['grip']==marker['grip_candidate_px'], 'Actual Primary2 palm differs from frozen source measurement'
        axis=marker['axis_design_only']
        angle=math.degrees(math.atan2(axis[1],axis[0]))*(1 if d['facing']>0 else -1)
        assert math.isclose(d['weapon_angle'],angle,abs_tol=1e-9), 'Actual directed Primary2 sword axis differs from frozen design'
        second_samples+=1
    assert d['draw_stack']==expected, 'Wrong actual phase/source/armor stack'
    masks[(d['facing'],clip)]|=1<<frame
    if clip!='Ready':
        assert d['stage']==(0 if clip=='Primary1' else 1) and int(d['action_id'])>0
        now,start,active,last,end=(d[k] for k in ('sim','start','active_at','active_end','end'))
        assert start<=now<end and start<active<last<end
        expected_durations=(.17,.12,.31) if clip=='Primary1' else (.15,.12,.27)
        assert all(math.isclose(x,y,abs_tol=1e-8) for x,y in zip((active-start,last-active,end-last),expected_durations))
        lo,hi,base=(start,active,0) if now<active else (active,last,2) if now<last else (last,end,4)
        assert frame==base+max(0,min(1,math.floor((now-lo)/(hi-lo)*2))), 'Frame sampled outside real kernel phase'
        actions[(d['facing'],clip)].add(int(d['action_id']))
assert all(mask==(15 if clip=='Ready' else 63) for (side,clip),mask in masks.items()), masks
assert len(runs)==1 and len(set(draws))==len(draws) and all(b>a for a,b in zip(draws,draws[1:]))
for side in (-1,1):
    assert len(actions[(side,'Primary1')])==len(actions[(side,'Primary2')])==1
    assert next(iter(actions[(side,'Primary2')]))==next(iter(actions[(side,'Primary1')]))+1
for key,count in (('Enter',1),('A',1),('J',4)):
    assert sum(x['key']==key and x['down'] for x in r['normal_input_requests'])==count
    assert sum(x['key']==key and not x['down'] for x in r['normal_input_requests'])==count
receipts=[json.loads(x) for x in (original/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines() if x]
movies=[x for x in receipts if x['file'].startswith('MovieFrame')]
assert len(movies)==len(rows) and len(receipts)==len(rows)+1
assert all(abs(x['capture_callback_monotonic_s']-r['capture_timing']['capture_start_monotonic_s']-t)<.1 for x,t in zip(movies,times))
result={'passed':True,'observations':len(rows),'duration_s':duration,'primary2_samples':second_samples,
 'masks':{str(k):v for k,v in masks.items()},'actual_actions':{str(k):sorted(v) for k,v in actions.items()},
 'source989_packages_verified':True,'kernel_phase_sampling_exact':True,'normal_fresh_J_pairs':True,
 'primary2_grip_and_directed_axis_bound_to_frozen_marker_JSON':True,
 'body_max_px':72,'UI_hidden':True,'primary2_armor_present':False,'grip_accepted':False,
 'blade_axis_measured':False,'footlock_accepted':False,'fullmotion_accepted':False,'audio_accepted':False,
 'scope':'Source-bound actual groundedStage0→Stage1 pairs/6phases each/bothfacings. Fit candidate only; second armor absent, no hit target or complete unit acceptance.', 'formal_complete_units':0}
out=original/'sword-primary2-fit-runtime-verification.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
