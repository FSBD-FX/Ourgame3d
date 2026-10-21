"""Read-only art258 normal J left/right native verification.

Only J0/J1 expected paths and numeric marker values vary. Old causal function
bodies, typed Air, raw source/GPU equality, PNG FIFO/CRC, optical reconstruction
and complete MainMix audit execute unchanged. No UE launch or media writes.
"""
from pathlib import Path
import argparse
from datetime import datetime
import ast
import hashlib
import importlib.util
import json
import math
import sys

sys.dont_write_bytecode = True
ROOT = Path('F:/Ourgame')
HERE = Path(__file__).resolve().parent
PRESENTATION = 'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPresentation.cpp'
OBSERVER = 'UnrealGame/Source/CodexDungeon/DungeonHeroLandingPriorityProbeV001.cpp'
DLL = 'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'
PREDECESSOR_SHA = '71e91acd625b9813be555f5b38012e9c7ae39727bb2bd35dc495e584865532ac'
BINDING_SHA = 'eaa11e20169bb6b53687671800100aa1eea1e703a29ec48ecb36ab55cbb0c6b9'
CONTRACT_SHA = 'f85284dc25d0a5f0be5bf09aa7b9f7dbdf2a62bccbb61e4ca0c5ce0ef1238f6e'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    def unique(items):
        result = {}
        for key, value in items:
            need(key not in result, 'Duplicate JSON key: '+key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def resolved(path):
    path = Path(path)
    return (path if path.is_absolute() else ROOT/path).resolve()


def pin(path):
    path = resolved(path); h = hashlib.sha256()
    with path.open('rb') as file:
        for block in iter(lambda: file.read(1024*1024), b''):
            h.update(block)
    return dict(path=path.as_posix(), bytes=path.stat().st_size, sha256=h.hexdigest())


def check_pin(row):
    path = resolved(row['path'])
    need(type(row['bytes']) is int and row['bytes'] >= 0 and path.is_file(), 'Pinned member missing: '+str(path))
    value = pin(path)
    need((value['bytes'], value['sha256']) == (row['bytes'], row['sha256']), 'Pinned member changed: '+str(path))
    return path


def same_pin(a, b):
    return resolved(a['path']) == resolved(b['path']) and (a['bytes'], a['sha256']) == (b['bytes'], b['sha256'])


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def freeze_members(row):
    path = check_pin(row); freeze = read(path)
    need(freeze.get('FinalAccepted', False) is False, 'Freeze cannot imply final content acceptance')
    rows = freeze.get('members', freeze.get('files'))
    need(type(rows) is list and rows, 'Freeze member list required')
    def normalize(entry):
        need(type(entry) is dict and ('relative_path' in entry) != ('path' in entry),
             'Frozen entry requires exactly one path representation')
        if 'relative_path' not in entry:
            return entry  # Preserve strict original absolute/ROOT-relative path pins, including external C inputs.
        relative = entry['relative_path']
        need(type(relative) is str and relative and '\\' not in relative and ':' not in relative
             and not Path(relative).is_absolute() and not relative.startswith('/')
             and all(part not in ('', '.', '..') for part in relative.split('/'))
             and all(ord(char) >= 32 for char in relative), 'Confined canonical local relative_path required')
        value = (path.parent/relative).resolve()
        need(path.parent in value.parents, 'Local freeze path escapes candidate')
        return dict(path=value.as_posix(), bytes=entry['bytes'], sha256=entry['sha256'])
    members = [normalize(entry) for entry in rows]
    need(len({resolved(x['path']) for x in members}) == len(members), 'Duplicate freeze member')
    dependencies = freeze.get('dependency_pins', freeze.get('dependencies', []))
    need(type(dependencies) is list, 'Freeze dependency list required')
    dependencies = [normalize(entry) for entry in dependencies]
    for entry in members+dependencies:
        check_pin(entry)
    return freeze, members


def dependencies():
    table = read(HERE/'dependencies-v001.json')
    loaded = {row['label']: check_pin(row) for row in table['members']}
    need(len(loaded) == len(table['members']), 'Duplicate dependency labels')
    landing = load_module(loaded['landing_checker'], 'bridge258_frozen_landing')
    legacy, frozen, contract = landing.dependencies()
    return loaded, landing, legacy, frozen, contract


LOADED, L, LEGACY, F, C = dependencies()
# Preserve every original causal helper, constant and numeric tolerance.
finite, f32, near, point = L.finite, L.f32, L.near, L.point
SWORD, IDENTITY = L.SWORD, L.IDENTITY
DRAW = read(LOADED['draw_contract'])


def expected_legacy(clip, frame):
    if clip == 'sword_primary_1' and type(frame) is int and frame in (0, 1):
        return list(DRAW['frames'][frame]['draw_stack'])
    return L.expected_legacy(clip, frame)


def legacy_identity(o,clip):
    d=o['old_draw'];need(d['clip']==clip and d['sim']==o['sim'] and d['facing']==o['facing'],'Fresh legacy clip/time/facing differs')
    need(all(d[k] is True for k in ('active','supported','action_pose_supported','texture_ready','armor_drawn','sword_drawn')) and d['gear_placeholder'] is False,'Incomplete actual legacy submission')
    need(d['actual_stack']==o['rendered_player_stack']==expected_legacy(clip,d['frame']),'Actual brown armor/body/sword stack differs')

def verify_causal(r):
    need(r['schema']=='hero-landing-priority-native-observer-v001' and r['requested_action'] in ('J','Shift') and type(r['requested_facing']) is int and r['requested_facing'] in (-1,1),'Wrong landing scenario')
    obs=r['observations'];inputs=r['normal_inputs'];ri,li,qi,ai=(r[k] for k in ('ready_callback_index','landing_callback_index','priority_input_index','first_action_callback_index'))
    need(all(type(x) is int for x in (ri,li,qi,ai)) and 0<=ri<li<ai<len(obs) and 0<=qi<len(inputs),'Completed callback/input indices missing')
    ready,land,q,first=obs[ri],obs[li],inputs[qi],obs[ai]
    top_identity=tuple(k for k in IDENTITY if k not in ('player_entity','facing'))
    need(all(r[k]==ready[k] for k in top_identity) and ready['owner']==ready['player_entity'] and ('player_entity' not in r or r['player_entity']==ready['player_entity']),'Report top identity differs from its actual completed Ready/player')
    verified_identity={k:ready[k] for k in IDENTITY}
    ei,esi,eci=(r[k] for k in ('equipment_input_index','equipment_started_callback_index','equipment_commit_callback_index'))
    need(all(type(x) is int for x in (ei,esi,eci)) and 0<=ei<len(inputs) and 0<=esi<eci<=ri,'Real E start/commit callback indices required before Ready')
    eqinput=inputs[ei];eqstart=obs[esi]['equipment_action'];eqcommit=obs[eci]['equipment_action']
    equip_fields=('kind','action_id','operation_id','source_id','instance_id','slot','start','deadline')
    need([x for x in inputs if x['key']=='E' and x['down'] is True]==[eqinput] and eqinput['context_sampled_before_InputKey'] is True and eqinput['before_equipment_action']['active'] is False and eqinput['selected_source_id']==r['light_source_id'] and eqinput['wall_offset_s']<obs[esi]['wall_offset_s'],'Exactly one actual selected-source E queue from inactive equipment required')
    first_equipment_active=next((i for i,o in enumerate(obs) if o['wall_offset_s']>eqinput['wall_offset_s'] and o['equipment_action']['active']),None)
    need(first_equipment_active==esi and int(eqstart['action_id'])>int(eqinput['before_equipment_action']['action_id']),'First newly started real E callback cannot be skipped or borrowed')
    need(eqstart['active'] is True and eqcommit['active'] is False and eqstart['kind']==2 and eqstart['slot']==2 and eqstart['source_id']==r['light_source_id'] and eqstart['instance_id']==ready['armor_instance'] and int(eqstart['action_id'])>0 and int(eqstart['operation_id'])>0,'Actual PickupArmor action/source/instance/slot required')
    need(all(eqstart[k]==eqcommit[k]==ready['equipment_action'][k] for k in equip_fields) and eqstart['start']==r['equipment_start'] and eqstart['deadline']==r['equipment_deadline']==eqstart['start']+.50,'Same real E action Start/Deadline/operation must survive commit and Ready')
    need(eqinput['sim']<=eqstart['start']<=obs[esi]['sim']<eqstart['deadline']<=obs[eci]['sim']<=ready['sim'] and obs[esi]['next_operation_id']==eqstart['operation_id'] and int(obs[eci]['next_operation_id'])==int(eqstart['operation_id'])+1,'Actual E .50 deadline/commit operation boundary differs')
    need(all(o['equipment_action']['active'] is True and all(o['equipment_action'][k]==eqstart[k] for k in equip_fields) and o['sim']<eqstart['deadline'] for o in obs[esi:eci]),'E active callback was skipped/cancelled/replaced before commit')
    need(obs[eci]['armor_instance']==ready['armor_instance'] and obs[eci]['armor_version']==ready['armor_version'],'Committed E slot is not Ready Light binding')
    equip_identity=tuple(k for k in IDENTITY if k not in ('armor_instance','armor_version'))
    need(all(all(o[k]==ready[k] for k in equip_identity) for o in obs[esi:ri+1]) and all(eqinput[k]==ready[k] for k in equip_identity),'E action callbacks/input borrowed another owner/run/room/epoch/weapon/facing')
    need(all(finite(o['sim']) and finite(o['wall_offset_s']) and o['completed_callback'] is True for o in obs),'Actual finite completed callbacks required')
    need(all(a['sim']<=b['sim'] and a['wall_offset_s']<b['wall_offset_s'] for a,b in zip(obs,obs[1:])),'Callback clocks are not monotonic')
    for o in obs[ri:]:
        need(all(o[k]==ready[k] for k in IDENTITY) and o['facing']==r['requested_facing'],'Owner/run/room/epoch/gear/facing changed')
        need(o['hp']==r['initial_hp'] and o['dead'] is False,'Player HP/death changed')
    need(all(o['hp']==r['initial_hp'] and o['dead'] is False for o in obs),'Player HP changed before committed Ready')
    need(all(q[k]==land[k] for k in IDENTITY) and q['context_sampled_before_InputKey'] is True,'Queued input context changed/was sampled after input')
    legacy_identity(ready,'sword_ready_idle')
    need(ready['jump_height']==ready['vertical_velocity']==0 and ready['landing_visual_age']==f32(.12) and ready['new_air_draw']['drawn'] is False,'Completed initial brown Ready required')
    spaces=[x for x in inputs if x['key']=='SpaceBar' and x['down'] is True]
    need(len(spaces)==1 and ready['wall_offset_s']<spaces[0]['wall_offset_s']<land['wall_offset_s'],'Space must follow its own completed Ready callback exactly once')
    need(all(spaces[0][k]==ready[k] for k in IDENTITY),'Space borrowed another Ready owner/gear token')
    sp=spaces[0]
    need(sp['before_H']==sp['after_H']==sp['before_V']==sp['after_V']==0 and sp['before_landing_age']==sp['after_landing_age']==f32(.12) and sp['before_melee_grounded'] is True and sp['before_wa_grounded'] is True,'Normal Space must queue unchanged from real grounded Ready')
    first_land4=next((i for i,o in enumerate(obs) if o['wall_offset_s']>sp['wall_offset_s'] and o['physical_visual_key']==4 and o['jump_height']==o['vertical_velocity']==0 and 0<=o['landing_visual_age']<f32(.06) and o['melee_grounded'] is True and o['wa_grounded'] is True),None)
    need(first_land4==li,'Landing token skipped the first actual grounded Land4 callback after this Space')
    air=obs[ri+1:li];frames={o['physical_visual_key'] for o in air if o['jump_height']>0 or o['vertical_velocity']>0}
    need(frames=={0,1,2,3} and r['air_mask']==15,'All four actual airborne poses required before Land4')
    first_air=next(o for o in air if o['jump_height']>0 or o['vertical_velocity']>0)
    need(first_air['jump_height']>0 and 315<first_air['vertical_velocity']<=630 and spaces[0]['sim']<=first_air['sim'],'Queued Space lacks actual first rise')
    need(land['physical_visual_key']==4 and land['jump_height']==land['vertical_velocity']==0 and 0<=land['landing_visual_age']<f32(.06) and land['melee_grounded'] is True and land['wa_grounded'] is True,'First completed Land4 grounded callback required')
    need(land['new_air_query_ok'] is True and land['new_air_draw']['drawn'] is True and land['new_air_draw']['slot_count']==9 and land['old_draw']['sim']==land['sim'],'Land4 needs its own actual Air9 submission')
    key='J' if r['requested_action']=='J' else 'LeftShift'
    priority=[x for x in inputs if x['down'] is True and x['key'] in ('J','LeftShift','RightShift')]
    need(priority==[q] and q['key']==key and q['down'] is True and land['wall_offset_s']<q['wall_offset_s']<first['wall_offset_s'] and land['sim']<=q['sim']<=first['sim'],'Priority must be one later Tick queued J/Shift after this Land4')
    need(q['before_H']==q['after_H']==q['before_V']==q['after_V']==0 and q['before_landing_age']==q['after_landing_age'] and 0<=q['before_landing_age']<f32(.12),'InputKey is enqueue only; unchanged H/V/age required inside landing')
    need(q['before_action_id']==q['after_action_id'] and q['before_melee_grounded'] is True and q['before_wa_grounded'] is True,'Immediate action mutation or ungrounded enqueue')
    active_indices=[i for i,o in enumerate(obs) if o['wall_offset_s']>q['wall_offset_s'] and o['action']['active'] is True]
    need(not any(o['action']['active'] for o in obs if o['wall_offset_s']<=q['wall_offset_s']),'Action already active before queued priority')
    need(active_indices and ai==active_indices[0],'First actual action callback cannot be skipped or borrowed')
    action=first['action'];start,end=r['action_start'],r['action_end'];age=land['landing_visual_age']+start-land['sim']
    need(finite(start) and finite(end) and q['sim']<=start<=first['sim'] and end>start and 0<=age<.12 and near(age,r['action_start_landing_age']) and action['start']==start and action['end']==end,'Actual action Start outside original half-open landing window')
    need(int(action['id'])>int(q['before_action_id']) and action['started_airborne'] is False and action['stage']==0,'New grounded action identity required')
    mask=0
    for i in active_indices:
        o=obs[i];a=o['action'];d=o['old_draw'];ad=o['new_air_draw']
        need(a['id']==action['id'] and a['start']==start and a['end']==end and o['jump_height']==o['vertical_velocity']==0 and o['melee_grounded'] is True and o['wa_grounded'] is True,'Action owner/clock/grounded budget changed')
        need(start<=o['sim']<end,'Active action callback outside real action interval')
        need(o['new_air_query_ok'] is False and o['air_query_out_unchanged'] is True and ad['drawn'] is False and ad['slot_count']==0 and ad['actual_stack']==[],'Action did not atomically reject Air with unchanged Out/zero parts')
        need(d['action_id']==a['id'] and d['sim']==o['sim'] and int(d['draw_id'])>int(obs[i-1]['old_draw']['draw_id']),'Stale action draw/action identity')
        if r['requested_action']=='J':
            legacy_identity(o,'sword_primary_1');need(a['started_airborne'] is False and a['stage']==0,'AirPrimary/combo mislabelled Primary1');mask|=1<<d['frame']
        else:
            dd=o['dodge_draw'];need(d['clip']=='sword_dodge' and dd['drawn'] is True and dd['atomic_preflight_ready'] is True and dd['slot_count']==9 and dd['resident_count']==33 and dd['actual_stack']==o['rendered_player_stack']==d['actual_stack'] and dd['sim']==o['sim'] and 0<=dd['frame']<4,'Actual Dodge9/full33 draw differs')
            need(a['invulnerable'] is (start+.06<=o['sim']<min(start+.20,end)),'Actual Dodge iframe differs from original .06/.20')
            need(dd['frame']==min(3,int((o['sim']-start)/.1)),'Dodge draw frame differs from its real original action age')
            need(int(a['start_event_id'])>0 and a['block'] in (0,1,2) and 0<=a['travelled']<=185 and near(math.hypot(*a['direction']),1),'Actual Dodge start/collision/travel receipt invalid')
            need((a['block']==0 and a['blocked_at']==-1 and a['block_event_id']=='0') or (a['block']>0 and start<=a['blocked_at']<=o['sim'] and int(a['block_event_id'])>0),'Actual Dodge blocked event/time differs')
            expected_ground=[a['origin'][k]+a['direction'][k]*a['travelled'] for k in range(2)]
            need(point(o['ground'],expected_ground,1e-3),'Real owner ground differs from actual Dodge position receipt')
            mask|=1<<dd['frame']
    need(mask==(63 if r['requested_action']=='J' else 15) and r['primary_mask']==(63 if r['requested_action']=='J' else 0) and r['dodge_mask']==(15 if r['requested_action']=='Shift' else 0),'Incomplete actual action pose coverage')
    if r['requested_action']=='Shift':need(near(end-start,.4),'Original Dodge .40 duration changed')
    joins=[o for o in obs[active_indices[-1]+1:] if o['old_draw']['clip']=='sword_ready_idle']
    need(len(joins)==r['ready_join_frames'] and len(joins)>=2,'Two completed Ready joins required')
    for o in joins:
        legacy_identity(o,'sword_ready_idle');need(o['sim']>=end and o['action']['active'] is False and o['new_air_draw']['drawn'] is False,'Ready before real completion or Air still drawn')
    if r['requested_action']=='Shift':need(all(o['action']['finish']==1 and o['action']['finished_at']==end and int(o['action']['finish_event_id'])>0 for o in joins),'Dodge must retain actual Completed event/clock')
    return dict(passed=True,scope='causal_callback_and_queued_input_only',verified_identity=verified_identity,first_grounded_Land4_callback_index=first_land4,first_action_callback_index=ai,action_start_landing_age=age,actual_action_mask=mask,FinalAccepted=False)


def verify_exact_inheritance():
    def functions(path):
        raw = path.read_bytes(); lines = raw.splitlines(keepends=True)
        return {n.name: b''.join(lines[n.lineno-1:n.end_lineno]) for n in ast.parse(raw.decode('utf-8-sig')).body
                if isinstance(n, ast.FunctionDef)}
    old, current = functions(LOADED['landing_checker']), functions(Path(__file__))
    for name in ('legacy_identity', 'verify_causal'):
        need(current[name] == old[name], 'Original causal function bytes changed: '+name)
    original = read(LOADED['original_primary_marker'])
    proposed = read(HERE/'primary1-markers-bridge258-v001.json')
    import copy
    expected = copy.deepcopy(original)
    for frame in DRAW['frames']:
        for key, value in (('source_root_px', frame['root']), ('grip_candidate_px', frame['grip']),
                           ('handle_axis_candidate_xy', frame['axis'])):
            expected['frames'][frame['frame']][key] = value
    need(proposed == expected, 'Only exact J0/J1 Root/Grip/Axis marker override is allowed')
    need(pin(LOADED['draw_contract'])['sha256'] == CONTRACT_SHA
         and pin(LOADED['binding_freeze'])['sha256'] == BINDING_SHA, 'Frozen exact art258 contract differs')
    return dict(original_causal_function_bodies_byte_equal=True, original_math_helpers_unchanged=True,
                only_J0_J1_numeric_marker_override=True, original_J2to5_and_Ready_unchanged=True)


def bridge_sources(sources, manifest):
    need(type(manifest['assets']) is list and len(manifest['assets']) == 14,
         'Exactly fourteen bridge source entries required')
    rows = manifest['assets']; keys = {(x['frame'], x['component']) for x in rows}
    components = ('BodyRest', 'ShoulderFar', 'Chest', 'NearArmWithoutHand', 'ShoulderNear', 'HelmetForeground', 'NearHand')
    need(keys == {(f, c) for f in (0, 1) for c in components} and len(keys) == len(rows),
         'Exact J0/J1 seven independent body/armor entries required')
    result = dict(sources)
    for row in rows:
        check_pin(row['source'])
        need(row['object_path'] not in result and row['object_path'] in DRAW['frames'][row['frame']]['draw_stack']
             and row['saved_path'].replace('\\', '/').endswith('/'+row['name']+'.uasset'),
             'Duplicate/wrong bridge texture source binding')
        result[row['object_path']] = dict(row, source=row['source']['path'], source_bytes=row['source']['bytes'],
                                          source_sha256=row['source']['sha256'])
    need(len(sources) == 115 and len(result) == 129, 'Original115 plus new14 source families required')
    return result


def member_map(rows):
    result = {row['path']: row for row in rows}
    need(len(result) == len(rows), 'Duplicate compiled/member path')
    return result


def verify_overlay(before, cm, ad, source_members, added):
    need(ad['schema'] == 'Root-primary1-bridge258-source-admission-v001'
         and ad['RootApproved'] is True and ad['is_template'] is False and ad['actual_applied'] is True
         and ad['FinalAccepted'] is False, 'Actual Root bridge source admission required')
    need(ad['actual_source_files'] == 303 and ad['actual_production_files'] == 1439
         and ad['new_source_files'] == 0 and ad['verification_passes'] == 2
         and ad['unrelated_source_tests_content_byte_mismatches'] == 0, 'Wrong bounded source/content admission')
    old, now = member_map(before['files']), member_map(cm['files'])
    changed = {PRESENTATION, OBSERVER}
    before_rows, after_rows = member_map(ad['before_files']), member_map(ad['after_files'])
    need(set(before_rows) == set(after_rows) == changed
         and all(before_rows[p] == old[p] and after_rows[p] == now[p] and now[p] != old[p] for p in changed),
         'Exactly reviewed presentation and observation CPP changes required')
    need(len(source_members) == 2, 'Two independently frozen source candidates required')
    for path, members in zip((PRESENTATION, OBSERVER), source_members):
        after = after_rows[path]
        need(any(Path(row['path']).name in (Path(path).name, 'after-'+Path(path).name) and (row['bytes'], row['sha256']) == (after['bytes'], after['sha256'])
                 for row in members), 'Actual compiled source differs from frozen reviewed projection: '+path)
    source = {p for p in now if p.startswith('UnrealGame/Source/')}
    old_source = {p for p in old if p.startswith('UnrealGame/Source/')}
    need(len(source) == 303 and source == old_source, 'Source exact303 membership changed')
    need(all(now[p] == old[p] for p in source-changed), 'Unrelated actual source/test member changed')
    production = {p for p in now if p.startswith('UnrealGame/Content/Production/')}
    old_production = {p for p in old if p.startswith('UnrealGame/Content/Production/')}
    added_map = member_map(added)
    need(len(old_production) == 1425 and len(added_map) == 14 and not old_production.intersection(added_map)
         and len(production) == 1439 and production == old_production|set(added_map), 'Original1425 plus exact14 production membership differs')
    need(all(now[p] == old[p] for p in old_production)
         and all(now[p] == row for p, row in added_map.items()), 'Old1425 or newly imported14 byte pins differ')
    tests = lambda rows: {x['path']:(x['bytes'], x['sha256']) for x in rows if '/Source/' in x['path'] and '/Tests/' in x['path']}
    need(tests(cm['files']) == tests(before['files']), 'Frozen203 test sources changed')
    return dict(actual_source_files=303, actual_production_files=1439, production_textures=1433, SoundWaves=6,
                allowed_changed_source=sorted(changed), old1425_unchanged=True, new_Texture2D_count=14,
                old203_test_sources_unchanged=True, unrelated_source_tests_content_byte_mismatches=0)


def verify_content(ad, cm, manifest):
    content = read(check_pin(ad['content_admission_pin']))
    need(content['schema'] == 'Root-primary1-bridge258-content-admission-v001'
         and content['old1425_unchanged'] is True and content['actual_production_files'] == 1439
         and content['new_Texture2D_count'] == 14 and content['verification_passes'] == 2
         and content['twoSHA_mismatches'] == 0 and content['FinalAccepted'] is False,
         'Actual fourteen-texture Root content admission required')
    imported = read(check_pin(content['actual_import'])); process = read(check_pin(content['actual_process']))
    need(process['schema'] == 'Root-primary1-bridge258-import-exit-v001' and process['exit_code'] == 0
         and process['os_exit_confirmed'] is True, 'Actual clean native art import process exit required')
    need(imported['schema'] == 'request258-14-native-import-v001' and imported['success'] is True
         and imported['actual_count'] == imported['saved_count'] == len(imported['assets']) == 14
         and imported['old1425_unchanged'] is True and imported['final_production_count'] == 1439
         and imported['verification_passes'] == 2 and imported['FinalAccepted'] is False
         and same_pin(imported['manifest'], pin(LOADED['import_manifest'])), 'Actual imported asset membership or exact source manifest differs')
    binding_dir = LOADED['binding_freeze'].parent
    need(same_pin(imported['importer'], pin(binding_dir/'import/ue-import-primary1-bridge258-v001.py'))
         and same_pin(imported['host_proof'], pin(binding_dir/'reports/host-preflight-v002.json')),
         'Actual native import must use frozen exact importer and host source-decode proof')
    claim = read(check_pin(imported['claim']))
    need(claim['schema'] == 'request258-native-import-claim-v001' and claim['replace_existing'] is False
         and claim['automatic_retry_allowed'] is False and same_pin(claim['manifest'], pin(LOADED['import_manifest'])),
         'Actual exclusive no-overwrite import claim differs')
    expected = {row['object_path']:row for row in manifest['assets']}
    rows = {row['actual_object_path']:row for row in imported['assets']}
    need(set(expected) == set(rows) and len(rows) == 14, 'Exact fourteen imported Texture2D paths required')
    added = member_map(content['added']); compiled = member_map(cm['files'])
    need(len(added) == 14, 'Exactly fourteen Root admitted content paths required')
    for path, row in rows.items():
        source = expected[path]
        need(row['actual_class'] == 'Texture2D' and row['actual_dimensions'] == [512, 512]
             and (row['frame'], row['component'], row['source']) == (source['frame'], source['component'], source['source'])
             and len(row['actual_import_filenames']) == 1 and resolved(row['actual_import_filenames'][0]) == resolved(source['source']['path']),
             'Imported native Texture2D source/dimensions differ')
        actual = check_pin(row['saved']); rel = actual.relative_to(ROOT).as_posix()
        need(actual == resolved(source['saved_path']) and rel in added and rel in compiled
             and same_pin(row['saved'], added[rel]) and added[rel] == compiled[rel], 'Actual saved Texture2D differs from Root/compiled content pin')
        settings = row['actual_settings']
        need(settings['never_stream'] is True and settings['srgb'] is True and all(token in settings[key] for key, token in
             (('compression_settings','TC_EDITOR_ICON'), ('mip_gen_settings','TMGS_NO_MIPMAPS'), ('lod_group','TEXTUREGROUP_UI'), ('filter','TF_BILINEAR'))),
             'Actual saved texture settings differ')
    return content['added']


def preflight_context(compiled_manifest, source_admission):
    # Revalidate every immutable dependency on every independent invocation.
    loaded, landing, legacy, frozen, contract = dependencies()
    inheritance = verify_exact_inheritance()
    cm_path, ad_path = resolved(compiled_manifest), resolved(source_admission)
    cm, ad = read(cm_path), read(ad_path)
    need(cm['source_files'] == 303 and cm['production_files'] == 1439
         and cm['registered_tests'] == cm['passed'] == 203 and cm['failed'] == cm['notRun'] == 0,
         'Actual current Source303/Production1439/full203 required')
    need(same_pin(cm['source_admission_pin'], pin(ad_path)), 'Current CM source admission pin differs')
    need(ad['predecessor_compiled_manifest']['sha256'] == PREDECESSOR_SHA
         and same_pin(ad['predecessor_compiled_manifest'], pin(loaded['predecessor_compiled_manifest'])), 'Exact actual CM71e91acd predecessor required')
    need(len(ad['source_candidate_freezes']) == len(ad['fresh_source_reviews']) == 2, 'Two reviewed source candidates required')
    need(same_pin(ad['source_candidate_freezes'][0], pin(loaded['binding_freeze']))
         and same_pin(ad['fresh_source_reviews'][0], pin(loaded['binding_review'])), 'Frozen approved renderer binding differs')
    source_members = []
    for freeze_pin, review_pin in zip(ad['source_candidate_freezes'], ad['fresh_source_reviews']):
        freeze, members = freeze_members(freeze_pin); source_members.append(members)
        review = check_pin(review_pin)
        need('Approved' in review.read_text(encoding='utf-8-sig'), 'Fresh independent source approval missing')
    manifest = read(loaded['import_manifest'])
    added = verify_content(ad, cm, manifest)
    overlay = verify_overlay(read(loaded['predecessor_compiled_manifest']), cm, ad, source_members, added)
    contract.strict203(read(check_pin(cm['full_suite'])))
    build = read(check_pin(cm['build'])); log = check_pin(cm['build_log'])
    need(build['ExitCode'] == 0 and build['Target'] == 'CodexDungeonEditor' and resolved(build['Log']) == log,
         'Actual current clean Editor build receipt/log required')
    for row in cm['files']:
        check_pin(row)
    paths = {row['path'] for row in cm['files']}; need(DLL in paths, 'Current compiled DLL missing')
    for prefix, count in (('UnrealGame/Source/',303), ('UnrealGame/Content/Production/',1439)):
        actual = {p.relative_to(ROOT).as_posix() for p in (ROOT/prefix).rglob('*') if p.is_file()}
        need(actual == {p for p in paths if p.startswith(prefix)} and len(actual) == count,
             'Actual on-disk exact directory membership differs: '+prefix)
    sources, am, ap = landing.sources_for('J', legacy, contract)
    sources = bridge_sources(sources, manifest)
    return loaded, landing, legacy, frozen, contract, cm, ad, overlay, inheritance, manifest, sources, am, ap


def verify_preflight(compiled_manifest, source_admission):
    *_, cm, ad, overlay, inheritance, manifest, sources, am, ap = preflight_context(compiled_manifest, source_admission)
    return dict(schema='request258-primary1-bridge-current-independent-preflight-v001', passed=True,
                compiled_manifest_pin=pin(compiled_manifest), source_admission_pin=pin(source_admission),
                source_overlay=overlay, inheritance=inheritance, actual_required_resource_count=129,
                registered_tests=203, UE_started=False, new_native_verified=False, FinalAccepted=False)


def verify_fixed_normal_inputs(r):
    side = r['requested_facing']; need(type(side) is int and side in (-1,1) and r['requested_action'] == 'J', 'Exact J left/right required')
    facing = 'A' if side == -1 else 'D'
    expected = [('Enter',True),('Enter',False),('D',True),('D',False),(facing,True),(facing,False),
                ('E',True),('E',False),('SpaceBar',True),('SpaceBar',False),('J',True),('J',False)]
    rows = r['normal_inputs']
    need(type(rows) is list and len(rows) == 12 and all(type(x) is dict and type(x.get('key')) is str
         and type(x.get('down')) is bool for x in rows) and [(x['key'],x['down']) for x in rows] == expected,
         'Exact fixed J left/right twelve normal-input edges required')
    return dict(passed=True, exact_ordered_input_edges=12, normal_facing_pulse=facing)


def expected_arguments(archive, side):
    # Exact original run-hero-landing-priority-v002 argv, one new opt-in flag.
    return ['F:/Ourgame/UnrealGame/CodexDungeon.uproject', '/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom',
        '-game','-d3d11','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4',
        '-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview',
        '-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview',
        '-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview',
        '-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview',
        '-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytaleLeatherPrimary2Preview',
        '-DungeonFairytaleLeatherPrimary3Preview','-DungeonFairytaleSwordEquipmentBoundPreview',
        '-DungeonFairytaleSwordWalkPreview','-DungeonFairytaleSwordHurtPreview','-DungeonFairytaleSwordDeathPreview',
        '-DungeonFairytaleSwordDodgePreview','-DungeonFairytaleSwordAirPreview','-DungeonFairytaleGuardFullPreview',
        '-DungeonFairytaleGuardStompPreview','-DungeonFairytaleGuardMoveRigPreview','-DungeonFairytalePrimary1Bridge258Preview',
        '-DungeonContentProof','-DungeonHeroLandingPriorityProofV001','-DungeonHeroLandingPriorityAction=J',
        '-DungeonHeroLandingPriorityFacing='+str(side),'-DungeonHeroLandingPriorityClearKnightDiagnostic',
        '-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture','-DungeonContentProofDir='+str(archive/'原件'),
        '-abslog='+str(archive/'native-engine.log')]


def verify_session(r, prereg, index, launch, claim, archive, cm_path, ad_path, checker_freeze):
    edges = verify_fixed_normal_inputs(r); side = r['requested_facing']
    need(prereg['schema'] == 'Root-primary1-bridge258-native-prereg-v001' and prereg['RootApproved'] is True
         and prereg['is_template'] is False and prereg['pre_registered_before_capture'] is True
         and prereg['FinalAccepted'] is False and prereg['requested_action'] == 'J'
         and type(prereg['requested_facing']) is int and prereg['requested_facing'] == side
         and prereg['diagnostic_clear_knight'] is True, 'Actual fixed J left/right prereg required')
    need(resolved(prereg['run_directory']) == archive and ROOT.resolve() in archive.parents, 'Exact prereg archive required')
    need(same_pin(prereg['compiled_manifest_pin'], pin(cm_path)) and same_pin(prereg['source_admission_pin'], pin(ad_path))
         and same_pin(prereg['checker_freeze_pin'], pin(checker_freeze)) and same_pin(prereg['checker_pin'], pin(__file__)),
         'Prereg actual CM/admission/checker differs')
    check_pin(prereg['launcher_pin'])
    need(index['exit_code'] == 0 and str(index['process_id']) == str(launch['process_id']) == r['process_id']
         and claim['schema'] == 'hero-landing-priority-process-claim-v001' and claim['process_id'] == r['process_id'],
         'Actual native PID/normal exit/exclusive process claim differs')
    for key in ('compiled_manifest_pin','source_admission_pin','checker_freeze_pin'):
        need(same_pin(index[key], prereg[key]), 'Session lineage differs: '+key)
    need(same_pin(index['root_prereg_pin'], pin(archive/'preregistration-v001.json'))
         and datetime.fromisoformat(prereg['created_utc'].replace('Z','+00:00'))
         < datetime.fromisoformat(launch['started_utc'].replace('Z','+00:00')), 'Actual prereg must precede native launch')
    need(launch['schema'] == 'Root-primary1-bridge258-native-launch-v001' and launch['requested_action'] == 'J'
         and type(launch['requested_facing']) is int and launch['requested_facing'] == side
         and launch['human_input'] is False and launch['diagnostic_clear_knight'] is True
         and launch['fixed_time_step_requested'] is False, 'Normal queued-input launch scope differs')
    args = launch['arguments']; need(type(args) is list and all(type(x) is str for x in args), 'Exact argv token array required')
    need([x.replace('\\','/') for x in args] == [x.replace('\\','/') for x in expected_arguments(archive, side)],
         'Exact frozen normal-input argv differs; no extra/missing flags or pacing changes')
    need(r['passed'] is True and r['flow_complete'] is True and r['failure'] == '' and r['final_accepted'] is False
         and r['visual_reviewed'] is False and r['audio_listened'] is False and r['real_save_restore'] == 'OPEN_not_run'
         and r['player_Guard_HP_position_AI_time_writes'] is False, 'Bounded actual native claims differ')
    need(all(o['interface_visible'] is False and o['text_calls'] == 0 and o['range_debug'] is False and o['range_lines'] == 0
         and all(o[k] == o['sim'] for k in ('melee_time','wa_time','dodge_time','weapon_world_time'))
         and o['native_actor_root_z'] == 0 for o in r['observations']), 'Actual UI/range/native clocks/root changed')
    duration = r['capture_timing']['capture_stop_monotonic_s']-r['capture_timing']['capture_start_monotonic_s']
    need(all(finite(x['wall_offset_s']) and 0 <= x['wall_offset_s'] < duration for x in r['normal_inputs']),
         'Actual normal input must occur inside original recording')
    return dict(explicit_Knight_diagnostic=True, player_Guard_HP_position_AI_time_writes=False,
                UI_hidden=True, independent_case='J_'+('left' if side == -1 else 'right'), input_edges=edges)


def expected_report_source_pins(manifest):
    return [dict(frame=x['frame'], component=x['component'], object_path=x['object_path'], source_png=x['source']['path'],
                 source_png_bytes=str(x['source']['bytes']), source_png_sha256=x['source']['sha256']) for x in manifest['assets']]


def verify_bridge_observation(r, manifest):
    need(r['request258_primary1_bridge_optin'] is True and r['request258_primary1_bridge_source_contract_sha256'] == CONTRACT_SHA
         and r['request258_primary1_bridge_source_pins'] == expected_report_source_pins(manifest),
         'Actual opt-in/contract/fourteen exact source metadata pins differ')
    markers = read(HERE/'primary1-markers-bridge258-v001.json'); counts = {0:0, 1:0}
    for observation in r['observations']:
        draw = observation['old_draw']
        if draw['clip'] == 'sword_primary_1' and draw['frame'] in (0,1) and observation['action']['active'] is True:
            frame = draw['frame']; contract = DRAW['frames'][frame]
            need(draw['actual_stack'] == observation['rendered_player_stack'] == contract['draw_stack']
                 and draw['body_texture'] == contract['legacy_full_body_TexturePath'] and draw['sword_texture'] == SWORD,
                 'Actual new eight-stack or legacy readiness reference differs')
            # Every relevant completed J0/J1 callback, beyond the selected optical witnesses.
            L.legacy_quads(observation, markers); counts[frame] += 1
    need(all(counts.values()), 'Actual completed J0 and J1 submissions required')
    return dict(passed=True, exact_source_metadata_pin_count=14, completed_callback_counts=counts,
                marker_is_provisional=True, old_full_body_path_is_readiness_reference_only=True,
                actual_new_eight_layer_stack_verified=True, final_art_accepted=False)


def verify_native(archive, compiled_manifest, source_admission):
    loaded, landing, legacy, frozen, contract, cm, ad, overlay, inheritance, manifest, sources, am, ap = preflight_context(compiled_manifest, source_admission)
    archive = resolved(archive); original = archive/'原件'; p = read(archive/'preregistration-v001.json')
    checker_freeze = check_pin(p['checker_freeze_pin']); freeze, members = freeze_members(p['checker_freeze_pin'])
    for path in (Path(__file__), HERE/'dependencies-v001.json', HERE/'primary1-markers-bridge258-v001.json'):
        need(any(same_pin(x, pin(path)) for x in members), 'Selected freeze omits actual checker/config/markers')
    r = read(original/'runtime-report.json')
    session = verify_session(r, p, read(archive/'index.json'), read(archive/'launch-receipt-v001.json'),
                             read(original/'observer-process-claim-v001.json'), archive, compiled_manifest, source_admission, checker_freeze)
    flow = verify_causal(r); bridge = verify_bridge_observation(r, manifest)
    typed = landing.verify_typed_callbacks(r, am, ap, landing.read(legacy['import-Dodge32-v001.json']), landing.read(legacy['Dodge-runtime-profile-data-v001.json']))
    gpu = landing.verify_resources(original, r, sources, am, ap)
    movie = frozen.verify_png_fifo(original, r)
    audio = contract.module(contract.AUDIO_CHECKER,'bridge258_frozen_full_audio',contract.AUDIO_CHECKER_SHA).audit(original/'runtime-report.json',require_frame_timing=True)
    adapted_markers = dict(legacy)
    adapted_markers['primary1-marker-proposal-v003.json'] = HERE/'primary1-markers-bridge258-v001.json'
    pixels = landing.optical(original, r, movie, sources, adapted_markers, frozen, am, ap)
    return dict(schema='request258-primary1-bridge-current-independent-native-v001', passed=True,
                requested_action='J', requested_facing=r['requested_facing'], process_id=int(r['process_id']),
                compiled_manifest_pin=pin(compiled_manifest), source_admission_pin=pin(source_admission),
                checker_freeze_pin=pin(checker_freeze), root_prereg_pin=pin(archive/'preregistration-v001.json'),
                native_report_pin=pin(original/'runtime-report.json'), session=session, source_overlay=overlay,
                inheritance=inheritance, flow=flow, request258_primary1_bridge=bridge, all_typed_callbacks=typed,
                actual_resources=gpu, native_PNG_FIFO_CRC_verified=True, audio=audio, source_pixels=pixels,
                hero_locomotion_request_metadata_present=('hero_locomotion_audio' in r), cue_signal_correlation_proven=False,
                structure_and_native_capture_verified=True, all_cue_audio_complete=False, visual_reviewed=False,
                audio_listened=False, formal_complete_units=0, FinalAccepted=False)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--preflight',action='store_true'); ap.add_argument('--archive')
    ap.add_argument('--compiled-manifest',required=True); ap.add_argument('--source-admission',required=True); ap.add_argument('--out',required=True)
    a = ap.parse_args()
    try:
        need(a.preflight is not bool(a.archive), 'Select --preflight or --archive')
        need(not Path(a.out).exists(), 'Never overwrite previous verification output')
        value = verify_preflight(a.compiled_manifest,a.source_admission) if a.preflight else verify_native(a.archive,a.compiled_manifest,a.source_admission)
        code = 0
    except (ValueError,KeyError,TypeError,OSError,StopIteration,AssertionError) as error:
        value = dict(passed=False,error=str(error),FinalAccepted=False); code = 3
    if not Path(a.out).exists():
        with Path(a.out).open('x',encoding='utf-8') as file:
            json.dump(value,file,ensure_ascii=False,indent=2); file.write('\n')
    print(json.dumps(value,ensure_ascii=False)); return code


if __name__ == '__main__':
    raise SystemExit(main())
