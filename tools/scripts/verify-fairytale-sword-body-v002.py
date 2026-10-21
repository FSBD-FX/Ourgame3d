"""Verify the bounded real Enter/A/J presentation recording; no art acceptance."""
from pathlib import Path
import argparse, importlib.util, json, math, subprocess

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--archive');p.add_argument('--preflight-only',action='store_true');a=p.parse_args()
spec=importlib.util.spec_from_file_location('sword_checks',Path(__file__).with_name('ue_fairytale_sword_body_v002_checks.py'))
checks=importlib.util.module_from_spec(spec);spec.loader.exec_module(checks)
manifest=checks.preflight(require_unused=False)
if a.preflight_only:
    print(json.dumps({'actual_imported':10,'old907_unchanged':True,'manifest_sha256':checks.MANIFEST_SHA}));raise SystemExit(0)
archive=Path(a.archive).resolve();original=archive/'原件'
r=json.loads((original/'runtime-report.json').read_text(encoding='utf-8-sig'))
assert r['schema']=='fairytale-sword-normal-input-capture-v1' and r['passed'] and r['native_async_capture_writes_flushed']
assert r['silent_video'] and not r['audio_recorded'] and r['formal_complete_units']==0
rows=r['observations'];assert len(rows)>120
times=r['capture_timing']['frame_wall_offsets_s'];duration=r['capture_timing']['requested_video_wall_duration_s']
assert len(times)==len(rows) and 5.8<=duration<8 and not r['capture_timing']['use_fixed_time_step']
assert all(math.isfinite(x) for x in times) and all(y>x for x,y in zip(times,times[1:]))
masks={(side,clip):0 for side in [-1,1] for clip in ['Ready','Primary1']};actions={-1:set(),1:set()};draws=[];runs=set()
for d in rows:
    assert d['hud'] and d['player'] and d['active'] and d['texture_ready']
    assert not d['interface_visible'] and d['text_calls']==0
    assert abs(d['canvas_size']-72*512/416)<1e-8 and d['root']==[256,464]
    assert d['facing'] in [-1,1] and d['run'];runs.add(d['run']);draws.append(int(d['draw_id']))
    if not d['supported']:
        assert not d['weapon'] and len(d['draw_stack'])==1
        continue
    clip='Primary1' if d['clip']=='sword_primary_1' else 'Ready'
    assert d['clip'] in ['sword_primary_1','sword_ready_idle']
    asset=next(v for v in manifest['assets'] if v['clip']==clip and v['frame']==d['frame'])
    assert d['texture']==asset['object_path'] and d['weapon']
    assert d['draw_stack']==[d['texture'],d['weapon'],d['texture']]
    masks[(d['facing'],clip)]|=1<<d['frame']
    if clip=='Primary1':
        assert d['stage']==0 and int(d['action_id'])>0
        now=d['sim'];start=d['start'];active=d['active_at'];endactive=d['active_end'];end=d['end']
        assert start<=now<end and start<active<endactive<end
        lo,hi,base=(start,active,0) if now<active else (active,endactive,2) if now<endactive else (endactive,end,4)
        expected=base+max(0,min(1,math.floor((now-lo)/(hi-lo)*2)))
        assert d['frame']==expected,'Rendered body does not sample actual kernel phase'
        actions[d['facing']].add(d['action_id'])
assert len(runs)==1 and len(draws)==len(set(draws)) and all(y>x for x,y in zip(draws,draws[1:]))
assert all(mask==(15 if clip=='Ready' else 63) for (side,clip),mask in masks.items()),masks
assert all(len(v)==1 for v in actions.values()) and actions[-1]!=actions[1]
inputs=r['normal_input_requests']
for key,count in [('Enter',1),('A',1),('J',2)]:
    assert sum(x['key']==key and x['down'] for x in inputs)==count
    assert sum(x['key']==key and not x['down'] for x in inputs)==count
receipts=[json.loads(x) for x in (original/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines() if x]
movies=[x for x in receipts if x['file'].startswith('MovieFrame')]
assert len(movies)==len(rows) and len(movies)+1==len(receipts)
assert all(abs(x['capture_callback_monotonic_s']-(r['capture_timing']['capture_start_monotonic_s']+t))<.1 for x,t in zip(movies,times))
result={'passed':True,'observations':len(rows),'duration_s':duration,'actual_masks':{str(k):v for k,v in masks.items()},'actual_actions':{str(k):sorted(v) for k,v in actions.items()},'kernel_phase_sampling_exact':True,'old907_packages_unchanged':True,'source10_actual_imported':True,'scope':'Actual normal-input render path only; hit timing, armor, thumb, fullstates/combos and audio remain unaccepted','formal_complete_units':0}
out=original/'sword-runtime-verification.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
