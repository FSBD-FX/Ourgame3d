"""Independent landing-priority verification; never launches UE or approves art.

Synthetic causal checks are separate from full native file/source/PNG/audio proof.
Every optional JSON result uses exclusive creation. Original evidence is read only.
"""
from pathlib import Path
import argparse
from datetime import datetime
import hashlib
import importlib.util
import json
import math
import struct
import sys
import zlib

sys.dont_write_bytecode = True
ROOT = Path('F:/Ourgame')
HERE = Path(__file__).resolve().parent
SWORD = '/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002'
IDENTITY = ('run', 'owner', 'current_room', 'epoch', 'player_entity', 'weapon_instance', 'weapon_version', 'armor_instance', 'armor_version', 'facing')
COMPONENTS = ('BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','FarHandForeground','NearHand','IndependentSword')
ORDER9 = ('BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','IndependentSword','FarHandForeground','NearHand')

def need(ok, message):
    if not ok: raise ValueError(message)

def finite(v): return type(v) in (int,float) and math.isfinite(v)
def f32(v): return struct.unpack('<f',struct.pack('<f',v))[0]
def near(a,b,tol=1e-9): return finite(a) and finite(b) and abs(a-b)<=tol
def point(a,b,tol=1e-9): return len(a)==len(b) and all(near(x,y,tol) for x,y in zip(a,b))
def pin(path):
    p=Path(path);return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def resolve_pin(row):
    p=Path(row['path']);p=p if p.is_absolute() else ROOT/p
    need(p.is_file() and p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],'Exact pinned file changed: '+str(p));return p
def read(path):
    def unique(items):
        d={}
        for k,v in items: need(k not in d,'Duplicate JSON key');d[k]=v
        return d
    return json.loads(Path(path).read_text(encoding='utf-8-sig'),object_pairs_hook=unique,parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))

def printf_repair_bytes(before):
    """The actual failed source stays frozen; permit exactly Root's three repairs."""
    repairs=(
        ('FString::Printf(Primary?TEXT("T_Fairytale_LeatherPrimary1%s_%03d_v001"):TEXT("T_Fairytale_LeatherReady%s_%03d_v001"),Parts[I],D.Frame)',
         'Primary?FString::Printf(TEXT("T_Fairytale_LeatherPrimary1%s_%03d_v001"),Parts[I],D.Frame):FString::Printf(TEXT("T_Fairytale_LeatherReady%s_%03d_v001"),Parts[I],D.Frame)'),
        ('FString::Printf(Armor?TEXT("T_Fairytale_LeatherReady%s_%03d_v001"):TEXT("T_Fairytale_SwordReady%s_%03d_v001"),Component,Frame)',
         'Armor?FString::Printf(TEXT("T_Fairytale_LeatherReady%s_%03d_v001"),Component,Frame):FString::Printf(TEXT("T_Fairytale_SwordReady%s_%03d_v001"),Component,Frame)'),
        ('FString::Printf(Armor?TEXT("T_Fairytale_LeatherPrimary1%s_%03d_v001"):TEXT("T_Fairytale_SwordPrimary1%s_%03d_v001"),Component,Frame)',
         'Armor?FString::Printf(TEXT("T_Fairytale_LeatherPrimary1%s_%03d_v001"),Component,Frame):FString::Printf(TEXT("T_Fairytale_SwordPrimary1%s_%03d_v001"),Component,Frame)'))
    for old,new in repairs:
        old,new=old.encode(),new.encode();need(before.count(old)==1,'Exact unique failed Printf source required');before=before.replace(old,new)
    return before

def verify_source_overlay(predecessor,admission,repair,source_freeze,cm):
    """Pure membership/pin gate, including the bounded actual compile repair."""
    need(admission['schema']=='Root-hero-landing-priority-source-admission-v001' and admission['RootApproved'] is True and admission['is_template'] is False and admission['actual_applied'] is True and admission['FinalAccepted'] is False and admission['actual_source_files']==cm['source_files'] and admission['actual_production_files']==1419,'Actual Root source admission required')
    admitted=admission['after_files'];need(len(admitted)==4 and {Path(x['path']).name for x in admitted}=={'DungeonGameMode.cpp','DungeonHUD.cpp','DungeonHeroLandingPriorityProbeV001.h','DungeonHeroLandingPriorityProbeV001.cpp'},'Exact final four source admission pins required')
    cpp=next(x for x in admitted if x['path'].endswith('DungeonHeroLandingPriorityProbeV001.cpp'))
    need(repair['schema']=='Root-hero-landing-Printf-literal-source-repair-v001' and repair['RootApproved'] is True and repair['is_template'] is False and repair['actual_applied'] is True and repair['FinalAccepted'] is False and repair['exact_three_literal_call_repairs'] is True and repair['protocol_texture_paths_and_action_behavior_changed'] is False and repair['actual_source_files']==cm['source_files'] and repair['actual_production_files']==1419,'Actual bounded Printf repair admission required')
    need(all(repair['before'][k]==cpp[k] for k in ('bytes','sha256')) and Path(repair['before']['path']).resolve()==Path(repair['after']['path']).resolve()==(ROOT/cpp['path']).resolve(),'Repair before/after target differs from admitted failed source')
    need(repair['after']['bytes']==54742 and repair['after']['sha256']=='621b9bef73c46e83f9b5610180a6dfa4f676707fcb5323e2081630bb2ca42569','Unexpected repair beyond the actual three literal calls')
    source_members={Path(x['path']).name:x for x in source_freeze['members'] if '/new-source/' in x['path'].replace('\\','/')}
    for name in ('DungeonHeroLandingPriorityProbeV001.h','DungeonHeroLandingPriorityProbeV001.cpp'):
        row=next(x for x in admitted if Path(x['path']).name==name);need(all(source_members[name][k]==row[k] for k in ('bytes','sha256')),'Admission source differs from frozen candidate')
    current={x['path']:x for x in cm['files']};expected_admitted=[]
    for row in admitted:
        expected=dict(row)
        if row is cpp:expected.update(bytes=repair['after']['bytes'],sha256=repair['after']['sha256'])
        need(expected==current.get(row['path']),'Admitted/repaired source differs from current compiled member');expected_admitted.append(expected)
    allowed={x['path'] for x in expected_admitted};before={x['path']:x for x in predecessor['source_files']}
    for path,row in before.items():
        if path not in allowed:need(current.get(path)==row,'Unrelated predecessor source changed: '+path)
    actual={x for x in current if x.startswith('UnrealGame/Source/')};need(len(actual)==cm['source_files'] and actual==set(before)|allowed,'Unexpected source overlay outside final four')
    tests=lambda rows:{x['path']:(x['bytes'],x['sha256']) for x in rows if '/Source/' in x['path'] and '/Tests/' in x['path']}
    need(tests(cm['files'])==tests(predecessor['source_files']),'Frozen203 test sources changed')
    return dict(source_files=len(actual),original_candidate_cpp_sha256=cpp['sha256'],actual_repaired_cpp_sha256=repair['after']['sha256'],unrelated_source_changes=0)

def expected_legacy(clip,frame):
    primary=clip=='sword_primary_1';need(primary or clip=='sword_ready_idle','Wrong legacy clip')
    need(type(frame) is int and 0<=frame<(6 if primary else 4),'Invalid legacy frame')
    order=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear']+(['HelmetForeground'] if primary else [])+['IndependentSword','NearHand']
    out=[]
    for component in order:
        if component=='IndependentSword':out.append(SWORD);continue
        armor=component in ('ShoulderFar','Chest','ShoulderNear')
        family='Primary1' if primary else 'Ready'
        namespace=('v013/HeroLeatherPrimary1' if primary else 'v012/HeroLeatherReady') if armor else ('v007/HeroSwordArmorPrimary1' if primary else 'v006/HeroSwordArmorReady')
        name=f'T_Fairytale_{"Leather" if armor else "Sword"}{family}{component}_{frame:03d}_v001'
        out.append('/Game/Production/ArtTrials/EV048/'+namespace+'/'+name+'.'+name)
    return out

def legacy_identity(o,clip):
    d=o['old_draw'];need(d['clip']==clip and d['sim']==o['sim'] and d['facing']==o['facing'],'Fresh legacy clip/time/facing differs')
    need(all(d[k] is True for k in ('active','supported','action_pose_supported','texture_ready','armor_drawn','sword_drawn')) and d['gear_placeholder'] is False,'Incomplete actual legacy submission')
    need(d['actual_stack']==o['rendered_player_stack']==expected_legacy(clip,d['frame']),'Actual brown armor/body/sword stack differs')

def verify_causal(r):
    need(r['schema']=='hero-landing-priority-native-observer-v001' and r['requested_action'] in ('J','Shift') and type(r['requested_facing']) is int and r['requested_facing'] in (-1,1),'Wrong landing scenario')
    obs=r['observations'];inputs=r['normal_inputs'];ri,li,qi,ai=(r[k] for k in ('ready_callback_index','landing_callback_index','priority_input_index','first_action_callback_index'))
    need(all(type(x) is int for x in (ri,li,qi,ai)) and 0<=ri<li<ai<len(obs) and 0<=qi<len(inputs),'Completed callback/input indices missing')
    ready,land,q,first=obs[ri],obs[li],inputs[qi],obs[ai]
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
    return dict(passed=True,scope='causal_callback_and_queued_input_only',first_action_callback_index=ai,action_start_landing_age=age,actual_action_mask=mask,FinalAccepted=False)

def dependencies():
    table=read(HERE/'dependencies-v001.json');rows=table['members'];loaded={}
    for row in rows:loaded[Path(row['path']).name]=resolve_pin(row)
    airpath=loaded['verify-Air-production-native-v001.py'];sys.path.insert(0,str(airpath.parent))
    spec=importlib.util.spec_from_file_location('landing_frozen_air',airpath);air=importlib.util.module_from_spec(spec);spec.loader.exec_module(air)
    return loaded,air,air.C

def sources_for(action,loaded,C):
    _,am,ap,*_=C.source_only();sources={a['object_path']:a for a in am['assets']};sword=ap['independent_sword'];sources[SWORD]=dict(object_path=SWORD,source=sword['source']['path'],source_bytes=sword['source']['bytes'],source_sha256=sword['source']['sha256'])
    families=[('import-sword-armor-ready-v001.json',False),('import-leather-ready-v001.json',True)]
    if action=='J':families += [('import-sword-armor-primary1-v001.json',False),('import-leather-primary1-v001.json',True)]
    else:families += [('import-Dodge32-v001.json',None)]
    for filename,armor in families:
        for a in read(loaded[filename])['assets']:
            is_armor=a['component'] in ('ShoulderFar','Chest','ShoulderNear')
            if armor is None or is_armor is armor:sources[a['object_path']]=a
    need(len(sources)==(115 if action=='J' else 105),'Exact source texture family count differs')
    for a in sources.values():resolve_pin(dict(path=a['source'],bytes=a['source_bytes'],sha256=a['source_sha256']))
    return sources,am,ap

def verify_resources(original,r,sources,manifest,profile):
    import numpy as np
    from PIL import Image
    rows=r['startup_resource_readbacks'];need(len(rows)==len(sources) and len({x['texture'] for x in rows})==len(rows) and {x['texture'] for x in rows}==set(sources),'Actual complete115/105 readback set differs')
    need(r['startup_actual_GPU_source_textures49']==rows[:49] and r['startup_readback_complete'] is True,'Original Air49 readback subset changed')
    air_metadata={a['object_path']:(a['frame'],COMPONENTS.index(a['component']),a['source_sha256'],a['source_RGBA_sha256']) for a in manifest['assets']}
    air_metadata[SWORD]=(-1,8,profile['independent_sword']['source']['sha256'],'')
    need({x['texture'] for x in rows[:49]}==set(air_metadata),'Exact original Air49 readback membership differs')
    stop=r['startup_readback_stop_monotonic_s'];start=r['capture_timing']['capture_start_monotonic_s'];need(0<stop<start,'RHI/source readback must finish before audio/movie/input')
    files=set()
    for row in rows:
        a=sources[row['texture']];need(row['class']=='Texture2D' and row['width']==row['height']==512 and row['resource_ready'] is True and row['pending_initialization'] is False and row['sRGB'] is True and row['RHI_format'] in (2,37) and row['editor_source_format']=='TSF_BGRA8','Actual resource format/dimensions differ')
        need(0<row['read_start_monotonic_s']<=row['read_stop_monotonic_s']<=stop,'Actual raw readback clock differs')
        need(row['read_flags']=='RCM_UNorm/Mip0/LinearToGamma=false; BGRA8/RGBA8 UNORM(_SRGB) byte copy','Original raw non-gamma-converting read flags changed')
        if row['texture'] in air_metadata:
            need(tuple(row[k] for k in ('frame','component','source_SHA_metadata','source_RGBA_SHA_metadata'))==air_metadata[row['texture']],'Original Air49 actual source/frame/component metadata differs')
        with Image.open(a['source']) as im:need(im.mode=='RGBA' and im.size==(512,512),'Original source RGBA512 required');expected=np.asarray(im).copy()
        for field,crc in (('GPU_file','GPU_BGRA8_CRC32'),('editor_source_file','editor_source_BGRA8_CRC32')):
            name=row[field];need(name not in files and name.startswith('texture-readback/') and ':' not in name and '..' not in Path(name).parts,'Unique confined raw filename required');files.add(name);data=(original/name).read_bytes()
            need(len(data)==1048576 and zlib.crc32(data)&0xffffffff==row[crc],'Actual raw BGRA length/CRC differs');actual=np.frombuffer(data,dtype=np.uint8).reshape(512,512,4)[...,[2,1,0,3]];need(np.array_equal(actual,expected),'GPU/editor source bytes differ from exact PNG')
    need(files=={p.relative_to(original).as_posix() for p in (original/'texture-readback').glob('*.bin')},'Extra/missing raw readback bins')
    return dict(actual_GPU_and_source_RGBA_byte_equal=True,texture_count=len(rows),raw_bin_count=len(files))

def quad_geometry(o,spec,paths,air,resident_paths):
    d=o['new_air_draw'] if air else o['dodge_draw'];side=o['facing'];scale=72/416
    root,grip,axis=(spec['Root'],spec['Grip'],spec['AxisArtist']) if air else (spec['ground_root_source_xy'],spec['Grip_source_xy'],spec['Axis_artist_raw_xy'])
    need(d['drawn'] is True and d['atomic_preflight_ready'] is True and d['slot_count']==9 and d['frame']==spec['frame'],'Actual complete/current pose submission required')
    need(d['player_entity']==o['owner'],'Actual drawing player differs from owner')
    if air:
        need(d['supported'] is True and d['sample_valid'] is True and d['opt_in'] is True and d['missing_reason']=='' and d['sample_native_time']==o['sim'] and d['sample_run']==d['binding_run']==o['run'] and d['sample_owner']==d['binding_owner']==o['owner'] and d['sample_room']==o['current_room'] and d['sample_epoch']==o['epoch'],'Actual Air sample/binding owner/clock differs')
        need(d['sample_ground']==o['ground'] and d['sample_H']==o['jump_height'] and d['sample_V']==o['vertical_velocity'] and d['sample_landing_age']==o['landing_visual_age'] and d['weapon_content']=='WPN-SWD-001' and d['armor_kind']==1 and d['armor_content']=='ARM-LGT-001' and all(d[k]==o[k] for k in ('weapon_instance','weapon_version','armor_instance','armor_version')),'Raw real LGT Air sample/gear differs')
    residents=d['resident_textures'];need(d['resident_count']==len(residents)==(49 if air else 33) and len({x['texture'] for x in residents})==len(residents) and all(x['class']=='Texture2D' and x['width']==x['height']==512 and x['resource_ready'] is True and x['pending_initialization'] is False for x in residents),'Complete actual Air49/Dodge33 resident preflight required')
    need({x['texture'] for x in residents}==set(resident_paths),'Resident resources differ from exact full Air49/Dodge33 family')
    g=[f32(640+(o['ground'][0]-o['camera_ground'][0])*f32(.65)),f32(490-o['ground'][1]*f32(.38))];lift=[g[0],g[1]-o['jump_height']*.70];top=[lift[0]-(root[0] if side>0 else 512-root[0])*scale,lift[1]-root[1]*scale];at=[lift[0]+side*(grip[0]-root[0])*scale,lift[1]+(grip[1]-root[1])*scale];angle=math.degrees(math.atan2(axis[1],axis[0]))*side;pivot=[99/512 if side>0 else 1-99/512,.5];width=512*scale*.5;swtop=[at[k]-pivot[k]*width for k in range(2)]
    need(d['sim']==o['sim'] and d['facing']==side and point(d['context_ground'],g,0) and d['ui_scale']==1 and point(d['root_source'],root,0) and point(d['grip_source'],grip,0) and point(d['axis_artist'],axis,0),'Actual source points/context identity differ')
    need(point(d['body_top'],top,1e-4) and point(d['sword_top'],swtop,1e-4) and point(d['sword_pivot_uv'],pivot) and near(d['weapon_angle'],angle) and near(d['canvas_size'],512*scale) and near(d['source_to_screen_scale'],scale),'Original height/root/weapon geometry differs')
    expected=[paths[n] for n in ORDER9];need(d['actual_stack']==o['rendered_player_stack']==o['old_draw']['actual_stack']==expected,'Exact actual nine-layer source order differs')
    need(len(d['slots'])==9,'Exact nine submitted slots required')
    for i,(s,name) in enumerate(zip(d['slots'],ORDER9)):
        sword=name=='IndependentSword';need(s['slot']==i and s['component']==COMPONENTS.index(name) and s['texture']==paths[name] and s['drawn'] is True and s['texture_ready'] is True and s['known_empty'] is False,'Actual slot/resource differs')
        need(point(s['top'],[f32(v) for v in (swtop if sword else top)],0) and point(s['size'],[f32(width if sword else 512*scale)]*2,0) and point(s['uv'],[0 if side>0 else 1,0],0) and point(s['uv_size'],[side,1],0) and s['rotation']==(f32(angle) if sword else 0) and point(s['rotation_pivot'],pivot if sword else [0,0]) and s['trace_tint']==[1,1,1,1] and s['draw_scale']==1 and s['scale_position'] is False,'Exact float submission/one mirror/tint differs')
    return d['slots']

def legacy_quads(o,markers):
    d=o['old_draw'];s=markers['frames'][d['frame']];root=s['source_root_px'];grip=s['grip_candidate_px'];axis=s['handle_axis_candidate_xy'];side=o['facing'];scale=72/416;canvas=512*scale
    need(point(d['root_source'],root,0) and point(d['grip_source'],grip,0) and near(d['canvas_size'],canvas),'Legacy frozen source marker differs')
    g=[640+(o['ground'][0]-o['camera_ground'][0])*f32(.65),490-o['ground'][1]*f32(.38)]
    top=[f32(g[0]-(root[0] if side>0 else 512-root[0])*scale),f32(g[1]-o['jump_height']*.70-root[1]*scale)];at=[f32(g[0]+side*(grip[0]-root[0])*scale),f32(g[1]-o['jump_height']*.70+(grip[1]-root[1])*scale)]
    need(point(d['grip_screen'],at,0),'Legacy actual grip projection differs');width=f32(canvas*.5);pivot=[99/512 if side>0 else 1-99/512,.5];swtop=[f32(at[k]-pivot[k]*width) for k in range(2)];angle=f32(math.degrees(math.atan2(axis[1],axis[0]))*side)
    return [dict(texture=p,component=8 if p==SWORD else -1,drawn=True,top=swtop if p==SWORD else top,size=[width if p==SWORD else f32(canvas)]*2,uv=[0 if side>0 else 1,0],uv_size=[side,1],rotation=angle if p==SWORD else 0,rotation_pivot=pivot if p==SWORD else [0,0]) for p in d['actual_stack']]

def verify_typed_callbacks(r,AM,AP,DM,DP):
    """Initial extraction of the v001 midpoint-only gate for the RED checks."""
    counts={'Air':0,'Dodge':0}
    for air,manifest,profile,kind in ((True,AM,AP,'Air'),(False,DM,DP,'Dodge')):
        key='new_air_draw' if air else 'dodge_draw'
        rows=[o for o in r['observations'] if o[key]['drawn']]
        for frame in {o[key]['frame'] for o in rows}:
            choices=[o for o in rows if o[key]['frame']==frame];o=choices[len(choices)//2]
            paths={a['component']:a['object_path'] for a in manifest['assets'] if a['frame']==frame};paths['IndependentSword']=SWORD
            quad_geometry(o,(profile['Frames'] if air else profile['frames'])[frame],paths,air,{a['object_path'] for a in manifest['assets']}|{SWORD});counts[kind]+=1
    return dict(passed=True,counts=counts)

def optical(original,r,movie,sources,loaded,frozen,AM,AP):
    import numpy as np
    from PIL import Image
    pixel=frozen.C.module(frozen.C.DODGE_PIXELS,'landing_frozen_pixels',frozen.C.DODGE_PIXELS_SHA)
    rgba={}
    for name,a in sources.items():
        with Image.open(a['source']) as im:v=np.asarray(im.convert('RGBA'),dtype=np.float64)/255
        v[...,:3]=pixel.linear(v[...,:3]);rgba[name]=v
    ready=read(loaded['ready-marker-proposal-v002.json']);primary=read(loaded['primary1-marker-proposal-v003.json']);dodge=read(loaded['Dodge-runtime-profile-data-v001.json']);dm=read(loaded['import-Dodge32-v001.json']);obs=r['observations'];chosen=[]
    for frame in range(5):
        rows=[i for i,o in enumerate(obs) if o['old_draw']['clip']=='sword_nonattack_air' and o['physical_visual_key']==frame];need(rows,'Required actual Air/Land4 source-pixel witness missing');i=rows[len(rows)//2];o=obs[i];paths={a['component']:a['object_path'] for a in AM['assets'] if a['frame']==frame};paths['IndependentSword']=SWORD;slots=quad_geometry(o,AP['Frames'][frame],paths,True,{a['object_path'] for a in AM['assets']}|{SWORD});chosen.append((i,'Air',frame,slots))
    for frame in range(6 if r['requested_action']=='J' else 4):
        rows=[i for i,o in enumerate(obs) if o['action']['active'] and o['old_draw']['frame']==frame and i>=r['first_action_callback_index']];need(rows,'Required action optical witness missing');i=rows[len(rows)//2];o=obs[i]
        if r['requested_action']=='J':slots=legacy_quads(o,primary)
        else:paths={a['component']:a['object_path'] for a in dm['assets'] if a['frame']==frame};paths['IndependentSword']=SWORD;slots=quad_geometry(o,dodge['frames'][frame],paths,False,{a['object_path'] for a in dm['assets']}|{SWORD})
        chosen.append((i,r['requested_action'],frame,slots))
    for i in [r['ready_callback_index'],len(obs)-1]:chosen.append((i,'Ready',obs[i]['old_draw']['frame'],legacy_quads(obs[i],ready)))
    results=[]
    for i,kind,frame,slots in chosen:
        xs=[];ys=[]
        for s in slots:
            for xy in ([0,0],[512,0],[0,512],[512,512]):p=frozen.C.project(s,xy);xs.append(p[0]);ys.append(p[1])
        x0=max(0,math.floor(min(xs))-1);x1=min(1280,math.ceil(max(xs))+1);y0=max(0,math.floor(min(ys))-1);y1=min(720,math.ceil(max(ys))+1);need(x1>x0 and y1>y0,'Projected ROI outside viewport');yy,xx=np.mgrid[y0:y1,x0:x1];color=np.zeros((*xx.shape,3));alpha=np.zeros(xx.shape);blade=np.zeros(xx.shape)
        for s in slots:
            v=pixel.sample(rgba[s['texture']],s,xx,yy);a=v[...,3];color=v[...,:3]*a[...,None]+color*(1-a[...,None]);alpha=a+alpha*(1-a);blade=a if s['component']==8 else blade*(1-a)
        expected=np.rint(pixel.srgb(color)*255).astype(np.uint8)
        with Image.open(original/movie[i]['file']) as im:actual=np.asarray(im.convert('RGB'))[y0:y1,x0:x1]
        err=np.mean(np.abs(actual.astype(float)-expected.astype(float)),axis=-1);opaque=(alpha>=.999)&(np.max(expected,axis=-1)>=32);steel=(blade>=.98)&(np.min(expected,axis=-1)>=45);values=frozen.fixed_optical_gate(err,opaque,steel);results.append(dict(observation=i,kind=kind,frame=frame,file=movie[i]['file'],fixed_gate_values=values))
    return dict(source_pixel_witnesses=results,registration_search_used=False,pixels_modified=False,legacy_quads='independently reconstructed from frozen renderer/source points, not an invented native slot trace',FinalAccepted=False)

def preflight_context(prereg):
    loaded,F,C=dependencies();p=read(prereg);need(p['schema']=='hero-landing-priority-root-prereg-v001' and p['RootApproved'] is True and p['is_template'] is False and p['pre_registered_before_capture'] is True and p['FinalAccepted'] is False,'Actual fresh Root prereg required')
    need(p['requested_action'] in ('J','Shift') and p['requested_facing'] in (-1,1) and type(p['diagnostic_clear_knight']) is bool,'Exact independent case required')
    lineage=read(HERE/'Root-actual-input-pins-v001.json')
    for key in ('compiled_manifest_pin','source_admission_pin','source_repair_admission_pin','source_candidate_freeze_pin'):
        need(p[key]==lineage[key],'Prereg differs from the actual bounded v143 lineage: '+key)
    cm=read(resolve_pin(p['compiled_manifest_pin']));need(cm['registered_tests']==cm['passed']==203 and cm['failed']==cm['notRun']==0 and cm['production_files']==1419,'Actual unchanged strict203/Production1419 required');C.strict203(read(resolve_pin(cm['full_suite'])))
    build=read(resolve_pin(cm['build']));need(build['ExitCode']==0 and build['Target']=='CodexDungeonEditor','Actual Editor build must pass');resolve_pin(cm['build_log'])
    predecessor=read(HERE.parent/'before-source-pins-v001.json');need(predecessor['compiled_manifest_pin']['sha256']=='52f906018a042d006db3470ec2fa7b4603a6b54e2489ab33d2bdff0bf309cd62','Wrong actual predecessor')
    current_tests={x['path']:(x['bytes'],x['sha256']) for x in cm['files'] if '/Source/' in x['path'] and '/Tests/' in x['path']}
    before_tests={x['path']:(x['bytes'],x['sha256']) for x in predecessor['source_files'] if '/Tests/' in x['path']};need(current_tests==before_tests,'Frozen203 test sources changed')
    for row in cm['files']:resolve_pin(row)
    actual_paths={x['path'] for x in cm['files']};need(len(actual_paths)==len(cm['files']),'Compiled membership duplicated')
    for prefix,count in (('UnrealGame/Source/',cm['source_files']),('UnrealGame/Content/Production/',1419)):
        expected={x for x in actual_paths if x.startswith(prefix)};actual={x.relative_to(ROOT).as_posix() for x in (ROOT/prefix).rglob('*') if x.is_file()};need(len(expected)==len(actual)==count and actual==expected,'Actual compiled directory exact membership differs: '+prefix)
    admission=read(resolve_pin(p['source_admission_pin']))
    need(admission['predecessor_compiled_manifest']['sha256']==predecessor['compiled_manifest_pin']['sha256'] and admission['source_candidate_freeze']['bytes']==p['source_candidate_freeze_pin']['bytes'] and admission['source_candidate_freeze']['sha256']==p['source_candidate_freeze_pin']['sha256'] and resolve_pin(admission['source_candidate_freeze'])==resolve_pin(p['source_candidate_freeze_pin']),'Actual admission/predecessor/source freeze lineage differs')
    resolve_pin(admission['source_admit_index']);resolve_pin(admission['fresh_scoped_source_review'])
    for key in ('source_candidate_freeze_pin','checker_freeze_pin'):
        freeze=read(resolve_pin(p[key]));need(freeze['FinalAccepted'] is False,'Candidate is not content acceptance')
        for row in freeze['members']:resolve_pin(row)
    source_freeze=read(resolve_pin(p['source_candidate_freeze_pin']));repair=read(resolve_pin(p['source_repair_admission_pin']));overlay=verify_source_overlay(predecessor,admission,repair,source_freeze,cm)
    for key in ('failed_build','failed_log'):resolve_pin(repair[key])
    candidate_cpp=next(x for x in source_freeze['members'] if x['path'].replace('\\','/').endswith('/new-source/DungeonHeroLandingPriorityProbeV001.cpp'))
    need(printf_repair_bytes(resolve_pin(candidate_cpp).read_bytes())==resolve_pin(repair['after']).read_bytes(),'Actual compiled repair contains a change beyond the three literal calls')
    cf=read(resolve_pin(p['checker_freeze_pin']));need(any(resolve_pin(x)==Path(__file__).resolve() for x in cf['members']),'Checker absent from selected freeze')
    for key in ('dependencies-v001.json','Root-actual-input-pins-v001.json'):
        need(any(resolve_pin(x)==(HERE/key).resolve() for x in cf['members']),'Checker configuration absent from selected freeze: '+key)
    return loaded,F,C,p,cm,overlay

def verify_preflight(prereg):
    loaded,F,C,p,cm,overlay=preflight_context(prereg)
    return dict(schema='hero-landing-priority-independent-preflight-v001',passed=True,compiled_manifest_pin=p['compiled_manifest_pin'],source_admission_pin=p['source_admission_pin'],source_repair_admission_pin=p['source_repair_admission_pin'],source_candidate_freeze_pin=p['source_candidate_freeze_pin'],checker_freeze_pin=p['checker_freeze_pin'],registered_tests=203,production_files=1419,source_overlay=overlay,UE_started=False,new_native_verified=False,RootApproved=False,FinalAccepted=False)

def verify_native(archive,prereg):
    loaded,F,C,p,cm,overlay=preflight_context(prereg)
    archive=Path(archive).resolve();need(archive==Path(p['run_directory']).resolve() and ROOT.resolve() in archive.parents,'Exact Root unused archive required');original=archive/'原件';r=read(original/'runtime-report.json');index=read(archive/'index.json');launch=read(archive/'launch-receipt-v001.json')
    need(r['passed'] is True and r['flow_complete'] is True and r['failure']=='' and r['final_accepted'] is False and r['visual_reviewed'] is False and r['audio_listened'] is False and r['real_save_restore']=='OPEN_not_run' and r['player_Guard_HP_position_AI_time_writes'] is False,'Bounded actual native result required')
    need(r['requested_action']==p['requested_action'] and r['requested_facing']==p['requested_facing'] and index['exit_code']==0 and str(index['process_id'])==str(launch['process_id'])==r['process_id'] and index['root_prereg_pin']==pin(prereg) and index['compiled_manifest_pin']==p['compiled_manifest_pin'],'Actual session PID/exit/prereg/compiled pin differs')
    need(all(index[k]==p[k] for k in ('source_admission_pin','source_repair_admission_pin','source_candidate_freeze_pin','checker_freeze_pin')),'Session source/admission/repair/checker freeze lineage differs')
    need(datetime.fromisoformat(p['created_utc'].replace('Z','+00:00'))<datetime.fromisoformat(launch['started_utc'].replace('Z','+00:00')),'Root prereg must actually precede this process launch')
    claim=read(original/'observer-process-claim-v001.json');need(claim['schema']=='hero-landing-priority-process-claim-v001' and claim['process_id']==r['process_id'],'Exclusive native process claim differs')
    required=['DungeonHeroLandingPriorityProofV001','DungeonContentProof','DungeonFastLosslessCapture','DungeonAsyncLosslessCapture','DungeonCandidateSprites','DungeonFairytaleSwordEquipmentBoundPreview','DungeonFairytaleLeatherReadyPreview','DungeonFairytaleLeatherPrimary1Preview','DungeonFairytaleLeatherPrimary2Preview','DungeonFairytaleLeatherPrimary3Preview','DungeonFairytaleSwordWalkPreview','DungeonFairytaleSwordHurtPreview','DungeonFairytaleSwordDeathPreview','DungeonFairytaleSwordDodgePreview','DungeonFairytaleSwordAirPreview','DungeonFairytaleGuardFullPreview','DungeonFairytaleGuardStompPreview','DungeonFairytaleGuardMoveRigPreview'];args=launch['arguments'];need(all('-'+x in args for x in required) and '-DungeonHeroLandingPriorityAction='+p['requested_action'] in args and '-DungeonHeroLandingPriorityFacing='+str(p['requested_facing']) in args,'Actual launch brown-art/scenario flags missing')
    need(isinstance(args,list) and all(isinstance(x,str) for x in args),'Actual argv token array required')
    forbidden=('DungeonProof','DungeonHeroAirProductionProofV001','DungeonHeroAirProofV001','DungeonHeroDodgeProofV001','DungeonHeroHurtProofV001','DungeonHeroDeathProofV001','DungeonGuardMoveProofV001','DungeonGuardStompProofV001','DungeonGuardArtCombatProofV003','DungeonGuardArtDeathProofV005','DungeonGuardArtKnown44Proof','DungeonGuardArtPartialProof','DungeonGuardRoomFlowProof','DungeonGuardRoomManualLightSource','DungeonFairytaleWalkProof','DungeonFairytaleEquipmentBoundProof','DungeonFairytaleSwordBodyProof','DungeonRunSaveProof','DungeonRunRestoreProof','DungeonGuardRunSaveProof','DungeonGuardRunRestoreProof','DungeonFairytaleLookdevProof','DungeonFairytaleLookdevPreview','DungeonCombatRangeDebug','DungeonCombatRangeProof','DungeonShowInterface')
    need(not any('-'+x in args for x in forbidden),'Other proof/HUD/range flags cannot share this actual case')
    need(('-DungeonHeroLandingPriorityClearKnightDiagnostic' in args)==p['diagnostic_clear_knight'],'Diagnostic authorization differs');need(not r['diagnostic_knight_hits'] or p['diagnostic_clear_knight'],'Unapproved diagnostic hit')
    need(all(o['interface_visible'] is False and o['text_calls']==0 and o['range_debug'] is False and o['range_lines']==0 and all(o[k]==o['sim'] for k in ('melee_time','wa_time','dodge_time','weapon_world_time')) and o['native_actor_root_z']==0 for o in r['observations']),'Actual HUD/range/native clock/root changed')
    duration=r['capture_timing']['capture_stop_monotonic_s']-r['capture_timing']['capture_start_monotonic_s'];need(all(finite(x['wall_offset_s']) and 0<=x['wall_offset_s']<duration for x in r['normal_inputs']),'Actual normal inputs must occur only while recording')
    flow=verify_causal(r);sources,am,ap=sources_for(r['requested_action'],loaded,C);gpu=verify_resources(original,r,sources,am,ap);movie=F.verify_png_fifo(original,r);audio=C.module(C.AUDIO_CHECKER,'landing_frozen_audio',C.AUDIO_CHECKER_SHA).audit(original/'runtime-report.json',require_frame_timing=True);pixels=optical(original,r,movie,sources,loaded,F,am,ap)
    return dict(schema='hero-landing-priority-independent-native-v001',passed=True,requested_action=r['requested_action'],requested_facing=r['requested_facing'],process_id=int(r['process_id']),run=r['run'],root_prereg_pin=pin(prereg),compiled_manifest_pin=p['compiled_manifest_pin'],source_admission_pin=p['source_admission_pin'],source_repair_admission_pin=p['source_repair_admission_pin'],source_candidate_freeze_pin=p['source_candidate_freeze_pin'],checker_freeze_pin=p['checker_freeze_pin'],native_report_pin=pin(original/'runtime-report.json'),flow=flow,actual_resources=gpu,native_PNG_FIFO_CRC_verified=True,audio=audio,source_pixels=pixels,visual_reviewed=False,audio_listened=False,FinalAccepted=False)

def verify_four(cases):
    need(len(cases)==4 and len({str(Path(a).resolve()) for a,p in cases})==4 and len({str(Path(p).resolve()) for a,p in cases})==4,'Four distinct archive/prereg pairs required')
    results=[verify_native(a,p) for a,p in cases]
    need({(r['requested_action'],r['requested_facing']) for r in results}=={('J',-1),('J',1),('Shift',-1),('Shift',1)} and len({r['process_id'] for r in results})==len({r['run'] for r in results})==4,'Four fresh PIDs/Runs and all requested J/Shift sides required')
    for key in ('compiled_manifest_pin','source_admission_pin','source_repair_admission_pin','source_candidate_freeze_pin','checker_freeze_pin'):need(all(r[key]==results[0][key] for r in results),'Four cases bind different actual predecessor/admission/repair/source/checker')
    return dict(schema='hero-landing-priority-independent-four-v001',passed=True,cases=results,four_fresh_processes=True,visual_reviewed=False,audio_listened=False,FinalAccepted=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--archive');ap.add_argument('--prereg');ap.add_argument('--preflight',action='store_true');ap.add_argument('--case',nargs=2,action='append',dest='cases');ap.add_argument('--out');a=ap.parse_args()
    try:
        need((a.preflight and a.prereg and not a.archive and not a.cases) or (not a.preflight and ((bool(a.archive) and bool(a.prereg) and not a.cases) or (a.cases and not a.archive and not a.prereg))),'Select --preflight --prereg, one native case, or exactly four --case ARCHIVE PREREG pairs')
        result=verify_preflight(a.prereg) if a.preflight else verify_four(a.cases) if a.cases else verify_native(a.archive,a.prereg)
        if a.out:
            with Path(a.out).open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
        print(json.dumps(result,ensure_ascii=False));return 0
    except (ValueError,KeyError,TypeError,OSError,StopIteration) as e:print(json.dumps(dict(passed=False,error=str(e),FinalAccepted=False),ensure_ascii=False));return 3

if __name__=='__main__':raise SystemExit(main())
