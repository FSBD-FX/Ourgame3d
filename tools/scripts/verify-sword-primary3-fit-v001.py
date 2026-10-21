"""Actual three-stage source/phase/stack proof; not art, hit or audio acceptance."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import math
import os

ROOT = Path('F:/Ourgame')
TOOLS = ROOT / 'tools/scripts'
P3 = ROOT / 'source-assets/production/fairytale-sword-primary3-runtime-v001'
PINS = {
    'ue_fairytale_sword_body_v002_checks.py': 'e65e06f51261cd37020d4a930679a6ef198b083ce68d30d04aae78adbdebfce6',
    'ue_sword_armor_ready_v001_checks.py': 'ece1ae52251c76760d01d3ebac2cf5ed93d351bf4fca7f40af61840af38de14c',
    'ue_sword_armor_primary1_v001_checks.py': 'bfe52eaaeaa06aa1a3d68dcd953e35866723b2d15e672c2c77e8982d6ead9c4e',
    'ue_sword_primary2_v002_checks.py': 'da3b2ee63387e23049f3d9f06be7549670116f2a65f2cc242b8e0d7e123672a0',
    'ue_sword_armor_primary2_v001_checks.py': 'ef0d821593d45641ebacecb1747dd8e294c8923f6883f54903195c9bae48b5dd',
    'ue_sword_armor_primary3_v001_checks.py': '0e89e3b9c0a684986c2e99cdb1f244febdd793ec5fb55c029f73c213f7c1259c',
    'verify-native-sword-capture-pixels.py': '7d0868d07266738d7819f82ffc92ab09f398c3dc2d45d9f2b345bd40737529f5',
}
P3_MARKER_SHA = '5ebe10d89f9ab5847acf613bc96f656e45631e525e7c2918d08d1c531b89f60a'
P3_INLINE_SHA = '6749343b607b21ae5d7d1b8d1bf959b67324d13b85c7f6b37f70097088116054'
OLD_INLINE_PINS = {
    'DungeonFairytaleSwordBodyV001.inl':'022d0cff100f3323f6b40c64d929ad6077ae351a5a47a1c5a7a1cd2fc6ad35dd',
    'DungeonFairytaleSwordBodyV002.inl':'eaea2ee52c87bcc7da355d9a398e0f2e737e937b641a98b052f5611f3135d594',
    'DungeonFairytaleSwordPrimary2V003.inl':'b2f769bcd7c92d8531a8faa9a10b9a6345e077b44f3f019f0c7de8639c34dc44',
    'DungeonFairytaleSwordPrimary2ArmorV001.inl':'a58ad7a34a836566d956e481bee146b4961ba222192da9b87fe1e623bddc3982',
}
COMPONENTS = ('BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand')
CLIPS = ('Ready','Primary1','Primary2','Primary3')
PRIMARY = CLIPS[1:]

def io_path(path):
    path=Path(path)
    return Path('\\\\?\\'+str(path.resolve())) if os.name=='nt' else path

def load(path):
    return json.loads(io_path(path).read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(io_path(path).read_bytes()).hexdigest()

def desc(path):
    path = Path(path)
    return {'path':path.as_posix(),'bytes':io_path(path).stat().st_size,'sha256':sha(path)}

def strict141(report):
    assert report['succeeded']==141
    assert all(report[k]==0 for k in ('succeededWithWarnings','failed','notRun','inProcess'))
    tests=report['tests']
    assert len(tests)==len({t['fullTestPath'] for t in tests})==141
    assert all(t['state']=='Success' and t['warnings']==t['errors']==0 for t in tests)

def snapshot_check(snapshot):
    snapshot=Path(snapshot).resolve()
    assert snapshot.is_relative_to((ROOT/'source-assets/production/backups').resolve())
    manifest=load(snapshot/'compiled-source-manifest.json')
    strict141(load(ROOT/manifest['automation_report']))
    assert manifest['actual_automation_succeeded']==141 and manifest['actual_automation_failed']==manifest['actual_automation_not_run']==0
    for row in manifest['files']:
        for base in (ROOT,snapshot):
            path=base/row['path']
            assert io_path(path).stat().st_size==row['bytes'] and sha(path)==row['sha256'], path
    production={p.relative_to(ROOT).as_posix() for p in (ROOT/'UnrealGame/Content/Production').rglob('*') if p.is_file()}
    frozen={x['path'] for x in manifest['files'] if x['path'].startswith('UnrealGame/Content/Production/')}
    assert production==frozen and len(production)==1085
    return manifest

def module(name, filename):
    path=TOOLS/filename
    assert sha(path)==PINS[filename], 'Pinned source preflight changed: '+filename
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result

def preflight(snapshot=None):
    for name,expected in PINS.items():
        assert sha(TOOLS/name)==expected, name
    for name,expected in OLD_INLINE_PINS.items():
        assert sha(ROOT/'UnrealGame/Source/CodexDungeon'/name)==expected, 'Old selected inline changed: '+name
    body=module('p3_body','ue_fairytale_sword_body_v002_checks.py').preflight(False)
    ready=module('p3_ready','ue_sword_armor_ready_v001_checks.py').preflight(False)
    first=module('p3_first','ue_sword_armor_primary1_v001_checks.py').preflight(False)
    second=module('p3_second','ue_sword_primary2_v002_checks.py').preflight(False)
    second_armor=module('p3_second_armor','ue_sword_armor_primary2_v001_checks.py').preflight(False)
    third=module('p3_third','ue_sword_armor_primary3_v001_checks.py').preflight(False)
    marker_path=P3/'data/primary3-marker-candidate-v001.json'
    assert sha(marker_path)==P3_MARKER_SHA and sha(P3/'data/DungeonFairytaleSwordPrimary3V001.inl')==P3_INLINE_SHA
    assert sha(ROOT/'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPrimary3V001.inl')==P3_INLINE_SHA
    markers3=load(marker_path)
    assert markers3['source_native']==175 and [m['frame'] for m in markers3['markers']]==list(range(6))
    assert all(m['actual_handle_center'] is None and m['actual_blade_axis'] is None for m in markers3['markers'])
    markers2=load(second['marker_json']['path'])
    if snapshot:
        snapshot_check(snapshot)
    return body,ready,first,second,second_armor,third,markers2,markers3

def verify_capture(archive, snapshot):
    body,ready,first,second,second_armor,third,markers2,markers3=preflight(snapshot)
    archive=Path(archive).resolve();original=archive/'原件'
    r=load(original/'runtime-report.json')
    assert r['schema']=='fairytale-sword-normal-input-capture-v1' and r['passed']
    assert r['primary2_fit_trial'] and r['primary3_fit_trial'] and r['primary3_armor_trial']
    assert r['native_async_capture_writes_flushed'] and r['silent_video'] and not r['audio_recorded']
    assert r['formal_complete_units']==0
    rows=r['observations'];times=r['capture_timing']['frame_wall_offsets_s']
    duration=r['capture_timing']['requested_video_wall_duration_s']
    assert len(rows)>160 and len(times)==len(rows) and 6.6<=duration<8 and not r['capture_timing']['use_fixed_time_step']
    assert all(math.isfinite(t) for t in times) and all(b>a for a,b in zip(times,times[1:]))
    assets={(x['clip'],x['frame']):x for x in body['assets']+second['assets']}
    assets.update({('Primary3',x['frame']):x for x in third['assets'] if x['component']=='Body'})
    maps={name:{(x['component'],x['frame']):x['object_path'] for x in doc['assets']}
        for name,doc in [('Ready',ready),('Primary1',first),('Primary2',second_armor),('Primary3',third)]}
    masks={(s,c):0 for s in (-1,1) for c in CLIPS}
    actions={(s,c):set() for s in (-1,1) for c in PRIMARY}
    runs=set();draws=[];samples={'Primary2':0,'Primary3':0};instances=set()
    for i,d in enumerate(rows):
        assert d['wall_offset_s']==times[i]
        assert d['hud'] and d['player'] and d['active'] and d['texture_ready']
        assert not d['interface_visible'] and d['text_calls']==0
        assert math.isclose(d['canvas_size'],72*512/416,abs_tol=1e-9) and d['root']==[256,464]
        assert d['facing'] in (-1,1) and d['run'];runs.add(d['run']);draws.append(int(d['draw_id']))
        if not d['supported']:
            assert not d['weapon'] and len(d['draw_stack'])==1 and not d['armor_drawn']
            continue
        clip={'sword_ready_idle':'Ready','sword_primary_1':'Primary1','sword_primary_2':'Primary2','sword_primary_3':'Primary3'}[d['clip']]
        frame=d['frame'];assert type(frame) is int or int(frame)==frame
        assert 0<=frame<(4 if clip=='Ready' else 6)
        asset=assets[(clip,frame)]
        assert d['texture']==asset['object_path']
        assert d['weapon']=='/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002'
        assert d['weapon_scale']==.5 and math.isclose(d['weapon_width'],72*512/416*.5,abs_tol=1e-4)
        assert d['armor_preview'] and d['armor_ready'] and d['armor_drawn']
        components=COMPONENTS if clip!='Ready' else tuple(c for c in COMPONENTS if c!='HelmetForeground')
        expected=[maps[clip][(c,frame)] for c in components[:-1]]+[d['weapon'],maps[clip][('NearHand',frame)]]
        assert d['draw_stack']==expected, 'Wrong actual phase/source/armor stack'
        if clip in ('Primary2','Primary3'):
            marker=(markers2 if clip=='Primary2' else markers3)['markers'][frame]
            assert d['grip']==marker['grip_candidate_px'], 'Actual palm differs from pinned candidate'
            axis=marker['axis_design_only'] if clip=='Primary2' else marker['directed_blade_axis_DESIGN']
            angle=math.degrees(math.atan2(axis[1],axis[0]))*(1 if d['facing']>0 else -1)
            assert math.isclose(d['weapon_angle'],angle,abs_tol=1e-9), 'Actual directed blade differs from pinned DESIGN'
            samples[clip]+=1
        masks[(d['facing'],clip)]|=1<<int(frame)
        if clip!='Ready':
            assert d['stage']==PRIMARY.index(clip) and int(d['action_id'])>0 and int(d['instance_id'])>0
            now,start,active,last,end=(d[k] for k in ('sim','start','active_at','active_end','end'))
            assert all(math.isfinite(x) for x in (now,start,active,last,end))
            assert start<=now<end and start<active<last<end
            durations={'Primary1':(.17,.12,.31),'Primary2':(.15,.12,.27),'Primary3':(.22,.12,.32)}[clip]
            assert all(math.isclose(x,y,abs_tol=1e-8) for x,y in zip((active-start,last-active,end-last),durations))
            if clip=='Primary3':
                assert math.isclose(end-start,.660,abs_tol=1e-8)
                assert all(math.isclose(x,y,abs_tol=1e-8) for x,y in zip(((active-start)/2,)*2+((last-active)/2,)*2+((end-last)/2,)*2,(.110,.110,.060,.060,.160,.160)))
            lo,hi,base=(start,active,0) if now<active else (active,last,2) if now<last else (last,end,4)
            assert frame==base+max(0,min(1,math.floor((now-lo)/(hi-lo)*2))), 'Frame outside actual kernel phase'
            actions[(d['facing'],clip)].add(int(d['action_id']));instances.add(int(d['instance_id']))
    assert all(mask==(15 if clip=='Ready' else 63) for (side,clip),mask in masks.items()), masks
    assert len(runs)==len(instances)==1 and len(set(draws))==len(draws) and all(b>a for a,b in zip(draws,draws[1:]))
    assert all(len(ids)==1 for ids in actions.values()), 'Unexpected duplicate action in a stage/facing'
    assert [[next(iter(actions[(s,c)])) for c in PRIMARY] for s in (1,-1)]==[[1,2,3],[4,5,6]]
    transitions=[]
    for side in (1,-1):
        sequences={c:[(i,d) for i,d in enumerate(rows) if d['facing']==side and d['supported'] and d['clip']=='sword_primary_'+str(PRIMARY.index(c)+1)] for c in PRIMARY}
        for previous,following in zip(PRIMARY,PRIMARY[1:]):
            left=sequences[previous];right=sequences[following]
            assert any(d['melee_pending_primary'] for _,d in left), 'Actual previous stage never accepted pending J'
            assert left[0][1]['end']==right[0][1]['start'], 'Original End != exact next Start'
            assert right[0][0]==left[-1][0]+1, 'Ready/unsupported/missing observation bridge between actions'
            transitions.append({'facing':side,'from':previous,'to':following,'from_observation':left[-1][0],
                'to_observation':right[0][0],'previous_end':left[0][1]['end'],'next_start':right[0][1]['start'],
                'exact_end_equals_start':True,'adjacent_observations':True,'actual_pending_seen':True})
    for key,count in (('Enter',1),('A',1),('J',6)):
        assert sum(x['key']==key and x['down'] for x in r['normal_input_requests'])==count
        assert sum(x['key']==key and not x['down'] for x in r['normal_input_requests'])==count
    requests=[x for x in r['normal_input_requests'] if x['key']=='J' and x['down']]
    for request,earliest in zip(requests,(1.10,1.60,2.16,4.30,4.80,5.36)):
        assert earliest<=request['wall_offset_s']<earliest+.08
    receipts=[json.loads(x) for x in (original/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines() if x]
    movies=[x for x in receipts if x['file'].startswith('MovieFrame')]
    assert len(movies)==len(rows) and len(receipts)==len(rows)+1
    assert [x['file'] for x in movies]==[f'MovieFrame{i:05d}.png' for i in range(len(rows))]
    assert all(abs(x['capture_callback_monotonic_s']-r['capture_timing']['capture_start_monotonic_s']-t)<.1 for x,t in zip(movies,times))
    native=load(original/'native-pixel-verification.json')
    assert native['passed'] and native['every_source_viewport_pixel_crc_matches'] and native['native_async_writer_verified']
    assert native['verified_original_PNG_count']==len(rows)+1
    return {'passed':True,'observations':len(rows),'duration_s':duration,'phase_samples':samples,
        'masks':{str(k):v for k,v in masks.items()},'actual_actions':{str(k):sorted(v) for k,v in actions.items()},
        'transitions':transitions,'source1085_packages_verified':True,'full141_snapshot_verified':True,
        'kernel_phase_sampling_exact':True,'primary3_durations_ms':[110,110,60,60,160,160],
        'normal_fresh_J_six':True,'actual_buffer_pending_and_exact_end_start_no_ready_bridge':True,
        'primary2_and_primary3_grip_and_directed_axis_bound_to_frozen_marker_JSON':True,
        'primary3_marker':desc(P3/'data/primary3-marker-candidate-v001.json'),
        'primary3_inline':desc(P3/'data/DungeonFairytaleSwordPrimary3V001.inl'),
        'body_max_px':72,'UI_hidden':True,'primary2_armor_present':True,'primary3_armor_present':True,
        'grip_accepted':False,'blade_axis_measured':False,'footlock_accepted':False,'fullmotion_accepted':False,'audio_accepted':False,
        'scope':'Source-bound groundedStage0→1→2 triples, both facings, each six phases. Real P2/P3 eight-draw stacks; no hit target or complete content acceptance.',
        'formal_complete_units':0}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--archive');parser.add_argument('--snapshot',required=True)
    parser.add_argument('--preflight-only',action='store_true');args=parser.parse_args()
    snapshot=(ROOT/args.snapshot).resolve()
    if args.preflight_only:
        preflight(snapshot)
        print(json.dumps({'preflight_passed':True,'actual_third_imported_saved':48,'old1037_unchanged':True,
            'production_packages':1085,'strict_automation_registered_and_success':141,'capture_executed':False,
            'observations':None,'capture_duration_s':None}));return
    assert args.archive, 'Archive required after actual capture'
    result=verify_capture(args.archive,snapshot)
    out=Path(args.archive).resolve()/'原件/sword-primary3-fit-runtime-verification-v001.json'
    with out.open('x',encoding='utf-8') as handle:handle.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':
    main()
