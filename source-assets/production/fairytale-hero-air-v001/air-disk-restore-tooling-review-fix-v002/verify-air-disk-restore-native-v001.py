"""Read-only independent v144 real two-process disk restore verifier.

Never launches UE, fabricates receipts, edits stores or invokes old causal gates.
Only --out writes one exclusive new verification JSON; failures are preserved.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math,sys,zlib,uuid
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
import air_disk_contract_v001 as C
HERE=Path(__file__).resolve().parent
ROOT=C.ROOT
need=C.need
ORDER_WALK=('BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','IndependentSword','NearHand')
ARMOR={'ShoulderFar','Chest','ShoulderNear'}

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

def dependencies():
    d=C.read(HERE/'dependencies-v001.json');paths={k:C.resolve_pin(v) for k,v in d['pins'].items()}
    freeze(d['pins']['retained_landing_freeze'])
    landing=module(paths['retained_landing_checker'],'disk_restore_retained_pure_landing')
    loaded,air,oldC=landing.dependencies()
    return d,paths,landing,loaded,air,oldC

def frozen_member(row):
    # Metadata closures retain intentional empty negative fixtures. Actual
    # native evidence always continues through C.resolve_pin (>0 bytes).
    need(isinstance(row,dict) and type(row.get('bytes')) is int and row['bytes']>=0
         and isinstance(row.get('path'),str) and row['path']
         and isinstance(row.get('sha256'),str) and C.re.fullmatch('[0-9a-f]{64}',row['sha256']),'Complete nonnegative frozen member bytes/SHA/path required')
    p=Path(row['path']);p=(p if p.is_absolute() else ROOT/p).resolve();value=C.pin(p)
    need((value['bytes'],value['sha256'])==(row['bytes'],row['sha256']),'Frozen member bytes/SHA differ: '+str(p));return p

def freeze(row):
    f=C.read(C.resolve_pin(row));members=f.get('members',f.get('files'))
    need(isinstance(members,list) and members and len({x['path'] for x in members})==len(members),'Exact nonempty frozen member closure required')
    for m in members:frozen_member(m)
    return f

def relative(row):
    p=Path(row['path']);return p.resolve().relative_to(ROOT.resolve()).as_posix() if p.is_absolute() else p.as_posix()

def row_map(rows):
    result={relative(r):r for r in rows};need(len(result)==len(rows),'Duplicated actual member rows');return result

def signature(row):return row['bytes'],row['sha256']

def actual_lineage(p,protocol,oldC):
    cm=C.read(C.resolve_pin(p['compiled_manifest_pin']));before=C.read(C.resolve_pin(p['predecessor_compiled_manifest_pin']))
    need(cm['registered_tests']==cm['passed']==203 and cm['failed']==cm['notRun']==0 and cm['production_files']==1419,'Actual new strict203/Production1419 CM required')
    oldC.strict203(C.read(C.resolve_pin(cm['full_suite'])))
    build=C.read(C.resolve_pin(cm['build']));need(build['ExitCode']==0 and build['Target']=='CodexDungeonEditor','Actual current Editor build must pass');C.resolve_pin(cm['build_log'])
    allrows=row_map(cm['files']);oldrows=row_map(before['files'])
    for row in cm['files']:C.resolve_pin(row)
    for prefix,count in (('UnrealGame/Source/',cm['source_files']),('UnrealGame/Content/Production/',1419)):
        expected={k for k in allrows if k.startswith(prefix)};actual={x.relative_to(ROOT).as_posix() for x in (ROOT/prefix).rglob('*') if x.is_file()}
        need(len(actual)==len(expected)==count and actual==expected,'Actual exact source/content membership differs: '+prefix)
    oldsrc={k:r for k,r in oldrows.items() if k.startswith('UnrealGame/Source/')};src={k:r for k,r in allrows.items() if k.startswith('UnrealGame/Source/')}
    names={'UnrealGame/Source/CodexDungeon/'+n for n in protocol['source_files']}
    added=set(src)-set(oldsrc);changed={k for k in set(src)&set(oldsrc) if signature(src[k])!=signature(oldsrc[k])}
    allowed=names|{'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp','UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp'}
    need(added==names and not (set(oldsrc)-set(src)) and changed<=allowed and cm['source_files']==before['source_files']+len(names),'Actual v144 source delta/count differs from new2 + narrow admitted seams')
    need({k:signature(v) for k,v in src.items() if '/Tests/' in k}=={k:signature(v) for k,v in oldsrc.items() if '/Tests/' in k},'Original203 test sources changed')
    need({k:signature(v) for k,v in allrows.items() if k.startswith('UnrealGame/Content/Production/')}=={k:signature(v) for k,v in oldrows.items() if k.startswith('UnrealGame/Content/Production/')},'Actual Production1419 bytes changed')
    sf=freeze(p['source_candidate_freeze_pin']);ad=C.read(C.resolve_pin(p['source_admission_pin']))
    need(ad['schema']=='Root-hero-air-disk-restore-source-admission-v001' and ad['RootApproved'] is True and ad['is_template'] is False and ad['actual_applied'] is True and ad['FinalAccepted'] is False,'Root actual v144 source admission required')
    need(ad['actual_source_files']==cm['source_files'] and ad['actual_production_files']==1419 and ad['new_source_files']==len(names) and ad['verification_passes']==2 and ad['unrelated_source_tests_content_byte_mismatches']==0,'Actual admission counts/two byte verification passes differ')
    need(C.same_pin(ad['source_candidate_freeze'],p['source_candidate_freeze_pin']) and C.same_pin(ad['predecessor_compiled_manifest'],p['predecessor_compiled_manifest_pin']),'Actual source admission/freeze/predecessor binding differs')
    C.resolve_pin(ad['source_admit_index']);C.resolve_pin(ad['fresh_source_review'])
    after=row_map(ad['after_files']);need(set(after)==added|changed,'Root admission after rows must exactly cover actual source delta')
    for name in names:
        matches=[r for r in sf['members'] if Path(r['path']).as_posix().endswith('/new-source/'+Path(name).name)]
        need(len(matches)==1 and signature(matches[0])==signature(after[name]),'Admitted new observer differs from exact frozen candidate')
    repairs=[]
    for row in p['source_repair_admission_pins']:
        repair=C.read(C.resolve_pin(row));need(repair['RootApproved'] is True and repair['is_template'] is False and repair['actual_applied'] is True,'Actual optional compile repair admission required')
        name=relative(repair['before']);need(name==relative(repair['after']) and name in after and signature(repair['before'])==signature(after[name]),'Repair before pin is not exact preceding admitted source')
        after[name]=repair['after'];C.resolve_pin(repair['after'])
        for key in ('failed_build','failed_log'):C.resolve_pin(repair[key])
        repairs.append(row)
    need(all(signature(src[k])==signature(v) for k,v in after.items()),'Actual compiled source differs from admitted source/explicit repair chain')
    dll=C.resolve_pin(p['game_dll_pin']);need(dll==ROOT/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll' and relative(p['game_dll_pin']) in allrows and signature(p['game_dll_pin'])==signature(allrows[relative(p['game_dll_pin'])]),'Actual game DLL differs from current CM')
    project=C.resolve_pin(p['uproject_pin']);need(project==ROOT/'UnrealGame/CodexDungeon.uproject','Actual game project required')
    engine=C.resolve_pin(p['engine_executable_pin']);need(engine.name=='UnrealEditor.exe','Actual installed Editor executable required')
    gm_path=C.resolve_pin(p['game_module_descriptor_pin']);em_path=C.resolve_pin(p['engine_module_descriptor_pin'])
    need(gm_path==dll.parent/'UnrealEditor.modules' and em_path==engine.parent/'UnrealEditor.modules','Actual installed game/engine module descriptor paths required')
    gm=C.read(gm_path);em=C.read(em_path)
    need(gm['BuildId']==em['BuildId'] and gm['BuildId'] and gm['Modules']['CodexDungeon']==dll.name,'Actual engine/game module BuildId or DLL mapping differs')
    return cm,dict(source_count=cm['source_files'],source_count_derived_from_predecessor=True,new_source_files=len(names),narrow_modified_paths=sorted(changed),Production1419_bytes_unchanged=True,old203_source_bytes_unchanged=True,compile_repair_pins=repairs,game_build_id=gm['BuildId'])

def preflight(prereg):
    p=C.read(prereg)
    need(p['schema']=='hero-air-disk-restore-root-prereg-v001' and p['RootApproved'] is True and p['is_template'] is False and p['pre_registered_before_capture'] is True and p['FinalAccepted'] is False,'Actual newly approved Root prereg required; templates never pass')
    need(p['registered_tests']==203 and p['production_files']==1419 and type(p['diagnostic_clear_knight']) is bool,'Actual bounded current test/content/diagnostic scope required')
    d,paths,L,loaded,F,oldC=dependencies();protocol=C.read(C.resolve_pin(p['protocol_pin']))
    binding=C.read(HERE/'source-binding-v001.json')
    need(C.same_pin(p['protocol_pin'],binding['protocol_pin']) and C.same_pin(p['source_candidate_freeze_pin'],binding['source_candidate_freeze_pin']),'Prereg must bind the exact final reviewed source protocol/candidate; actual CM/admission/compile repairs remain external')
    need(protocol['runtime_schema']=='hero-air-disk-restore-native-observer-v001' and protocol['facing']==1,'Exact current source protocol required')
    need(set(protocol['common_cli'])<=set(p['visual_flags']) and len(p['visual_flags'])==len(set(p['visual_flags'])),'Minimum original visual/capture flags required; registered supersets allowed')
    need(not set(protocol['forbidden_flags'])&set(p['visual_flags']),'Other proof flags forbidden')
    need(p['source_map']==protocol['source_map'] and p['target_map']==protocol['target_map'],'Actual source FirstBatch and target pristine maps required')
    profiles=Path(p['profiles_directory']);need(profiles.is_absolute() and profiles.as_posix()==profiles.resolve().as_posix() and profiles.name=='BoundRunOnly-v2','Exact normalized absolute BoundRunOnly-v2 store required')
    profile=uuid.UUID(p['profile_id']);need(profile.int>0 and str(profile)==p['profile_id'],'Exact new lower-case hyphenated ProfileGuid required')
    archives=[Path(p[k]).resolve() for k in ('source_archive','target_archive')]
    need(all(Path(p[k]).is_absolute() and ROOT.resolve() in archives[i].parents for i,k in enumerate(('source_archive','target_archive'))) and archives[0]!=archives[1] and not any(a.is_relative_to(b) for a,b in (archives,archives[::-1])),'Two distinct absolute nonnested native archives inside project required')
    need(p['target_audio_policy']=='existing-native-capture-complete-silence-allowed-without-signal-acceptance' and C.same_pin(p['target_audio_policy_addendum_pin'],d['pins']['audio_policy_addendum']) and C.same_pin(p['target_audio_audit_evidence_pin'],d['pins']['audio_gap_source_audit']),'Exact new target native silent capture policy/evidence required')
    C.resolve_pin(p['target_audio_policy_addendum_pin']);C.resolve_pin(p['target_audio_audit_evidence_pin'])
    cf=freeze(p['checker_freeze_pin']);need(any(frozen_member(r)==Path(__file__).resolve() for r in cf['members']),'Current checker absent from selected actual freeze')
    sf=freeze(p['source_candidate_freeze_pin']);need(any(frozen_member(r)==C.resolve_pin(p['protocol_pin']) for r in sf['members']),'Actual protocol absent from candidate source freeze')
    cm,lineage=actual_lineage(p,protocol,oldC)
    # Deliberately no requirement that a Profile is still absent here: post-native
    # verification runs after publication. Root source launch records that fact.
    return p,cm,lineage,protocol,(d,paths,L,loaded,F,oldC)

def art_sources(dep):
    d,paths,L,loaded,F,oldC=dep
    _,am,ap,*_=oldC.source_only();sources={a['object_path']:a for a in am['assets']};sword=ap['independent_sword']['source']
    actual_sword=ap['independent_sword'].get('texture',ap['independent_sword'].get('object_path',L.SWORD));need(actual_sword==L.SWORD,'Retained independent sword identity differs')
    sources[L.SWORD]=dict(object_path=L.SWORD,source=sword['path'],source_bytes=sword['bytes'],source_sha256=sword['sha256'])
    for name,armor in (('import-sword-armor-ready-v001.json',False),('import-leather-ready-v001.json',True)):
        for a in C.read(loaded[name])['assets']:
            if (a['component'] in ARMOR)==armor:sources[a['object_path']]=a
    wm=C.read(paths['walk_manifest']);wp=C.read(paths['walk_profile'])
    for a in wm['assets']:
        if a['component']!='Body':sources[a['object_path']]=a
    need(len(sources)==115 and len([a for a in wm['assets'] if a['component']!='Body'])==42,'Exact Air49+Ready24+Walk42 source family required')
    for a in sources.values():C.resolve_pin(dict(path=a['source'],bytes=a['source_bytes'],sha256=a['source_sha256']))
    return sources,am,ap,wm,wp

def inspect_draws(r,dep,am,ap,wm,wp):
    d,paths,L,loaded,F,oldC=dep;ready=C.read(loaded['ready-marker-proposal-v002.json']);air_paths={a['object_path'] for a in am['assets']}|{L.SWORD}
    walk_markers=dict(frames=[dict(source_root_px=f['root'],grip_candidate_px=f['grip'],handle_axis_candidate_xy=f['axis']) for f in wp['frames']])
    ready_index=r['equipment']['ready_callback_index'] if r['role']=='source' else -1
    counts=dict(Air9=0,BrownReady7=0,Walk8=0,preparation_NoneWalk5=0,preparation_NoneReady3_excluded_from_source_pixel_acceptance=0,pristine_noPawn=0);slots={}
    for i,o in enumerate(r['observations']):
        if not o['has_player']:
            counts['pristine_noPawn']+=1;need(o['new_air_draw']['drawn'] is False and o['rendered_player_stack']==[],'Pristine cannot draw a player');continue
        nd=o['new_air_draw'];frame=o['physical_visual_key'];old=o['old_draw'];stack=o['rendered_player_stack']
        if frame>=0 and (r['role']=='target' or i>=ready_index):
            need(isinstance(nd.get('draw_id'),str) and C.uint(nd['draw_id'])==C.uint(old['draw_id']),'Actual Air draw ID must be positive and match the same completed callback draw ID')
            paths_for={a['component']:a['object_path'] for a in am['assets'] if a['frame']==frame};paths_for['IndependentSword']=L.SWORD
            slots[i]=L.quad_geometry(o,ap['Frames'][frame],paths_for,True,air_paths);counts['Air9']+=1;continue
        need(nd['drawn'] is False and nd['slot_count']==0 and nd['actual_stack']==[],'Unsupported actual state cannot retain stale Air parts')
        if old['clip']=='sword_walk':
            wf=old['frame'];parts={a['component']:a['object_path'] for a in wm['assets'] if a['frame']==wf};parts['IndependentSword']=L.SWORD
            brown=r['role']=='target' or i>=ready_index
            wanted=[parts[k] for k in ORDER_WALK if brown or k not in ARMOR]
            need(stack==old['actual_stack']==wanted and old['texture_ready'] is True and old['sword_drawn'] is True,'Actual Walk source stack differs from existing full/None parts')
            slots[i]=L.legacy_quads(o,walk_markers);counts['Walk8' if brown else 'preparation_NoneWalk5']+=1;continue
        if old['clip']=='sword_ready_idle' and (r['role']=='target' or i>=ready_index):
            L.legacy_identity(o,'sword_ready_idle');slots[i]=L.legacy_quads(o,ready);counts['BrownReady7']+=1;continue
        # Exact acknowledged boundary: before real E commit, None Ready uses the
        # old whole PNG plus replayed fist. It is recorded preparation, not a
        # new115 GPU/source-pixel completion claim or a fabricated BrownReady7.
        need(r['role']=='source' and i<ready_index and old['clip']=='sword_ready_idle','Unregistered actual player clip')
        if len(stack)==3:
            need(stack[0]==stack[2] and stack[1]==L.SWORD,'Actual preparation NoneReady whole/sword/fist stack differs')
            counts['preparation_NoneReady3_excluded_from_source_pixel_acceptance']+=1
        else:
            # Real E commit may display brown Ready before observer consumes its
            # Ready token; still validate its actual frozen seven-layer identity.
            L.legacy_identity(o,'sword_ready_idle');slots[i]=L.legacy_quads(o,ready);counts['BrownReady7']+=1
    return counts,slots

def optical(original,r,movie,sources,dep,slots):
    d,paths,L,loaded,F,oldC=dep;pixel=oldC.module(oldC.DODGE_PIXELS,'disk_restore_frozen_pixels',oldC.DODGE_PIXELS_SHA)
    rgba={}
    for name,a in sources.items():
        with Image.open(a['source']) as im:v=np.asarray(im.convert('RGBA'),dtype=np.float64)/255
        v[...,:3]=pixel.linear(v[...,:3]);rgba[name]=v
    obs=r['observations'];chosen=[]
    def choose(rows,kind,frame):
        need(rows,'Required actual source-pixel pose/callback missing');chosen.append((rows[len(rows)//2],kind,frame))
    if r['role']=='source':
        choose([r['equipment']['ready_callback_index']],'Ready',obs[r['equipment']['ready_callback_index']]['old_draw']['frame'])
        choose([r['checkpoint']['observation_index']],'ApexCheckpoint',2)
        for frame in (0,1):
            rows=[i for i in slots if obs[i]['physical_visual_key']==frame]
            if rows:choose(rows,'Air',frame)
        for frame in range(6):
            rows=[i for i in slots if obs[i]['old_draw']['clip']=='sword_walk' and obs[i]['old_draw']['frame']==frame]
            if rows:choose(rows,'Walk_observed',frame)
    else:
        paused=[q['observation_index'] for q in r['pause_checks']]
        for i,label in ((paused[0],'InstalledApex'),(paused[len(paused)//2],'PausedApex'),(paused[-1],'LastAwaitApex')):choose([i],label,2)
        for frame in (3,4,5):choose([i for i in slots if obs[i]['physical_visual_key']==frame],'ContinuedAir',frame)
        choose([len(obs)-2],'ReadyJoin',obs[-2]['old_draw']['frame']);choose([len(obs)-1],'ReadyJoin',obs[-1]['old_draw']['frame'])
    results=[]
    for i,kind,frame in chosen:
        draw=slots[i];xs=[];ys=[]
        for s in draw:
            for xy in ([0,0],[512,0],[0,512],[512,512]):xy=oldC.project(s,xy);xs.append(xy[0]);ys.append(xy[1])
        x0=max(0,math.floor(min(xs))-1);x1=min(1280,math.ceil(max(xs))+1);y0=max(0,math.floor(min(ys))-1);y1=min(720,math.ceil(max(ys))+1)
        need(x1>x0 and y1>y0,'Actual projected ROI outside viewport');yy,xx=np.mgrid[y0:y1,x0:x1];color=np.zeros((*xx.shape,3));alpha=np.zeros(xx.shape);blade=np.zeros(xx.shape)
        for s in draw:
            v=pixel.sample(rgba[s['texture']],s,xx,yy);a=v[...,3];color=v[...,:3]*a[...,None]+color*(1-a[...,None]);alpha=a+alpha*(1-a);blade=a if s['component']==8 else blade*(1-a)
        expected=np.rint(pixel.srgb(color)*255).astype(np.uint8)
        with Image.open(original/movie[i]['file']) as im:actual=np.asarray(im.convert('RGB'))[y0:y1,x0:x1]
        err=np.mean(np.abs(actual.astype(float)-expected.astype(float)),axis=-1);opaque=(alpha>=.999)&(np.max(expected,axis=-1)>=32);steel=(blade>=.98)&(np.min(expected,axis=-1)>=45)
        values=F.fixed_optical_gate(err,opaque,steel);results.append(dict(observation=i,kind=kind,frame=frame,file=movie[i]['file'],fixed_gate_values=values))
    return dict(source_pixel_witnesses=results,registration_search_used=False,pixels_modified=False,fixed_optical_function_unchanged=True,actual_camera_per_callback_used=True,pre_E_whole_Ready_pixels_excluded=True,legacy_quads='frozen source-marker/render math reconstruction; not invented submitted native slot trace',FinalAccepted=False)

def audio_audit(report_path,role,dep,p):
    d,paths,L,loaded,F,oldC=dep
    audio=oldC.module(oldC.AUDIO_CHECKER,'disk_restore_original_audio',oldC.AUDIO_CHECKER_SHA)
    if role=='source':
        result=audio.audit(report_path,require_frame_timing=True)
        result.update(policy='original_source_non_silent_gate_unchanged; E CLOTH can produce sound, Walk/jump/landing not attributed',policy_addendum_pin=p['target_audio_policy_addendum_pin'],policy_source_audit_pin=p['target_audio_audit_evidence_pin'])
        return result
    # Approved precise existing API: complete target capture may legitimately
    # contain no emitted cues. All original binding/header/PCM/timing gates stay.
    report=C.read(report_path);capture=report['main_submix_capture'];duration=audio.validate_capture_receipt(capture)
    directory=Path(capture['output_directory']);need(directory.is_absolute(),'Absolute actual helper output directory required');directory=directory.resolve()
    need(directory.is_relative_to(Path(report_path).resolve().parent),'Target WAV must belong to this report archive')
    original,canonical=Path(capture['engine_original_wav']),Path(capture['canonical_wav'])
    need(original.is_absolute() and canonical.is_absolute() and original.resolve()==directory/'runtime-mix-engine-export.wav' and canonical.resolve()==directory/'runtime-mix.wav','Exact original target WAV binding required')
    decoded=audio.validate_pcm_bytes(original.read_bytes(),canonical.read_bytes(),require_non_silent=False)
    need(capture['channels']==decoded['channels'] and capture['sample_rate_hz']==decoded['sample_rate_hz'] and capture['pcm_frames']==decoded['frames'] and capture['header_block_align_repaired'] is decoded['header_block_align_repaired'],'Helper native target PCM/header facts differ from full independent decode')
    difference=abs(decoded['duration_s']-duration);need(difference<=.15,'Actual target WAV/wall duration exceeds unchanged150ms gate')
    timing=audio.validate_frame_timing(report,capture,duration)
    return dict(schema='v144-native-target-main-submix-independent-audio-v001',passed=True,scope='Actual full native recording binding/PCM/timing only; signal may be truly silent',
                native_report=C.pin(report_path),engine_original=C.pin(original),canonical=C.pin(canonical),decoded_PCM=decoded,
                capture_wall_duration_s=duration,actual_WAV_wall_duration_difference_s=difference,maximum_duration_difference_s=.15,frame_timing=timing,
                target_requires_non_silent=False,target_signal_present=decoded['non_silent'],actual_complete_zero_PCM=decoded['nonzero_samples']==0,
                signal_or_each_cue_or_audition_acceptance=False,audio_modified=False,offline_audio_constructed=False,
                policy_addendum_pin=p['target_audio_policy_addendum_pin'],policy_source_audit_pin=p['target_audio_audit_evidence_pin'],auditioned=False,final_mix_accepted=False,formal_complete_units=0)

def native_receipts(archive,role,p,prereg,pair):
    archive=Path(archive).resolve();original=archive/'原件';r=C.read(original/'runtime-report.json');index_path=C.resolve_pin(pair['session_index_pin'])
    need(index_path==archive/'index.json' and Path(pair['archive']).resolve()==archive,'Exact registered role archive/index required')
    index=C.read(index_path);launch_path=C.resolve_pin(pair['launch_receipt_pin']);exit_path=C.resolve_pin(pair['exit_receipt_pin'])
    need(launch_path==archive/'launch-receipt-v001.json' and exit_path==archive/'exit-receipt-v001.json','Original actual role launch/OS-exit receipt paths required')
    launch=C.read(launch_path);exited=C.read(exit_path)
    for value,schema in ((index,'hero-air-disk-restore-native-session-index-v001'),(launch,'hero-air-disk-restore-process-launch-v001'),(exited,'hero-air-disk-restore-process-exit-v001')):
        need(value['schema']==schema and value['role']==role and value['is_template'] is False and value['actual_recorded'] is True,'Actual new role receipts required; template/history cannot substitute')
    pid=C.uint(r['process_id']);need(pid==index['process_id']==launch['process_id']==exited['process_id'] and index['exit_code']==exited['exit_code']==0 and index['native_runtime_passed'] is True,'Actual process PID/native passed/OS exit binding differs')
    need(exited['process_still_running'] is False and exited['os_exit_confirmed'] is True and exited['started_utc']==launch['started_utc'] and C.same_pin(exited['launch_receipt_pin'],C.pin(launch_path)),'Actual completed OS lifetime/launch receipt required')
    need(C.utc(p['created_utc'])<C.utc(launch['started_utc']),'Root prereg must truly precede launch')
    for key in ('compiled_manifest_pin','source_candidate_freeze_pin','source_admission_pin','checker_freeze_pin','game_dll_pin'):
        need(C.same_pin(index[key],p[key]),'Role session lineage differs: '+key)
    need(index['source_repair_admission_pins']==p['source_repair_admission_pins'] and C.same_pin(index['root_prereg_pin'],C.pin(prereg)) and C.same_pin(launch['root_prereg_pin'],C.pin(prereg)),'Role prereg/repair chain differs')
    need(C.same_pin(index['runtime_report_pin'],C.pin(original/'runtime-report.json')) and C.same_pin(index['launch_receipt_pin'],C.pin(launch_path)) and C.same_pin(index['exit_receipt_pin'],C.pin(exit_path)),'Actual role original report/receipt pins differ')
    for key in ('game_dll_pin','executable_pin','uproject_pin'):
        expected=p['engine_executable_pin'] if key=='executable_pin' else p[key]
        need(C.same_pin(launch[key],expected),'Actual launch binary/project differs: '+key)
    build='v144-'+p['compiled_manifest_pin']['sha256']+'-'+p['game_dll_pin']['sha256']
    need(r['build_id']==build and r['compiled_manifest_sha256']==p['compiled_manifest_pin']['sha256'] and r['expected_game_dll_sha256']==p['game_dll_pin']['sha256'] and C.same_pin(r['actual_game_module'],p['game_dll_pin']),'Actual loaded DLL/current CM/BuildId binding differs; V2 success alone is insufficient')
    profile=Path(p['profiles_directory'])/p['profile_id']
    need(r['profile_id']==p['profile_id'] and Path(r['profiles_directory']).resolve()==Path(p['profiles_directory']).resolve() and Path(r['profile_directory']).resolve()==profile.resolve(),'Actual exact store/Profile path differs')
    claim=C.read(original/'observer-process-claim-v001.json');need(claim['schema']=='hero-air-disk-restore-process-claim-v001' and C.uint(claim['process_id'])==pid,'Exclusive native process claim differs')
    args=launch['arguments'];need(isinstance(args,list) and all(isinstance(x,str) for x in args),'Actual structured argv array required')
    need(len(args)>=2 and Path(args[0]).resolve()==C.resolve_pin(p['uproject_pin']) and args[1]==p[role+'_map'],'Actual first project/map argv tokens differ')
    protocol=C.read(C.resolve_pin(p['protocol_pin']))
    need(all('-'+flag in args for flag in protocol['common_cli']) and set('-'+x for x in p['visual_flags'])<=set(args),'Minimum actual original visual/capture flags missing')
    need(p[role+'_map'] in args and '-game' in args and '-d3d11' in args and '-windowed' in args and '-ResX=1280' in args and '-ResY=720' in args,'Actual original native mode/map/viewport/D3D11 args missing')
    for flag in protocol['forbidden_flags']+['DungeonProof','DungeonCombatRangeDebug','DungeonCombatRangeProof','DungeonShowInterface','nosound','UseFixedTimeStep']:
        need(not any(x.lower()==('-'+flag).lower() or x.lower().startswith(('-'+flag+'=').lower()) for x in args),'Other proof/audio/UI/fixed pacing flag cannot share native role')
    values={x.split('=',1)[0]:x.split('=',1)[1] for x in args if x.startswith('-') and '=' in x}
    need(len(values)==len([x for x in args if x.startswith('-') and '=' in x]),'Duplicate command parameters could override registered input')
    expected={'-DungeonHeroAirDiskRole':role,'-DungeonContentProofDir':str(original),'-DungeonHeroAirDiskProfilesDir':p['profiles_directory'],'-DungeonHeroAirDiskProfileGuid':p['profile_id'],'-DungeonHeroAirDiskCompiledManifestSHA':p['compiled_manifest_pin']['sha256'],'-DungeonHeroAirDiskGameDLLSHA':p['game_dll_pin']['sha256'],'-DungeonHeroAirDiskBuildId':build}
    for key,value in expected.items():
        need(key in values,'Actual required native parameter missing: '+key)
        if key in ('-DungeonContentProofDir','-DungeonHeroAirDiskProfilesDir'):need(Path(values[key]).resolve()==Path(value).resolve(),'Native original path parameter differs')
        else:need(values[key]==value,'Native registered role/profile/BuildId parameter differs')
    diagnostic='-DungeonHeroAirDiskClearKnightDiagnostic' in args
    need(diagnostic==(role=='source' and p['diagnostic_clear_knight']),'Explicit source-only Knight authorization differs')
    need(not r['diagnostic_knight_hits'] or diagnostic,'Unapproved native diagnostic hit')
    for h in r['diagnostic_knight_hits']:need(h['content']=='ENM-STN-001' and h['api']=='ADungeonFighter::ApplyCombatHit' and h['explicit_cli_authorization'] is True,'Only actual source predecessor Knight public diagnostic allowed')
    if role=='source':need(launch['source_profile_absent_before_launch'] is True,'Actual source launch must record wholly unused Profile before creation')
    return r,launch,exited,values

def verify_disk(source,target,so,to,p,codec):
    s=source['disk'];t=target['disk'];commit=s['commit'];need(s['writer_status']==0 and s['close_writer_called'] is True and commit['status']==0 and commit['generation_id']=='1' and commit['replayed'] is False and commit['publication_may_have_succeeded'] is False,'Actual exclusive fresh gen1 Commit/Close receipt required')
    cp=source['checkpoint'];start=source['capture_timing']['capture_start_monotonic_s'];stop=source['capture_timing']['capture_stop_monotonic_s']
    need(start+source['observations'][cp['observation_index']]['wall_offset_s']<=s['writer_open_monotonic_s']<=s['commit_start_monotonic_s']<=s['commit_stop_monotonic_s']<=s['closed_monotonic_s']<stop,'Same-boundary native disk writer/Commit/Close timing differs')
    for receipt in (s,s['source_load_receipt'],target['prepare_install'],t['target_final_load_receipt']):
        need(receipt['load_status']==0 and receipt['observed_head_generation']==receipt['generation_id']=='1' and receipt['parent_generation']=='0' and receipt['loaded_build_id']==source['build_id'],'Actual highest head/gen1/parent0/readback/BuildId differs')
    need(s['published_before']==[] and t['published_files_unchanged'] is True,'Source must begin unpublished; target must retain published bytes')
    groups=[];profile=(Path(p['profiles_directory'])/p['profile_id']).resolve()
    for disk,field,original in ((s,'published_after',so),(t,'published_before',to),(t,'published_after',to)):
        rows=disk[field];need(len(rows)==2 and {Path(r['original_path']).name for r in rows}=={'slot-A.bundle.json','slot-A.commit.json'},'Exact two original published slotA files required')
        data={}
        for row in rows:
            live=profile/Path(row['original_path']).name;need(Path(row['original_path']).resolve()==live and (C.pin(live)['bytes'],C.pin(live)['sha256'])==(row['bytes'],row['sha256']),'Published live file differs from exact registered profile bytes')
            copy=C.confined_pin(row['evidence_file'],original);need(copy.parent==original/('disk-before' if field=='published_before' else 'disk-after') and copy.name==live.name,'Original disk evidence copy path differs')
            need((C.pin(copy)['bytes'],C.pin(copy)['sha256'])==(row['bytes'],row['sha256']) and copy.read_bytes()==live.read_bytes(),'Published original/evidence copy bytes differ')
            data[live.name]=copy.read_bytes()
        groups.append(data)
    need(groups[0]==groups[1]==groups[2],'Source published/target before/after complete disk bytes changed')
    actual_published={f.name for f in profile.iterdir() if f.is_file() and (f.name.endswith('.bundle.json') or f.name.endswith('.commit.json'))}
    need(actual_published=={'slot-A.bundle.json','slot-A.commit.json'},'Extra/missing published head slots')
    result=C.verify_store_bytes(groups[0]['slot-A.bundle.json'],groups[0]['slot-A.commit.json'],codec,cp,p['profile_id'],source['build_id'])
    need((commit['bundle_sha256'],commit['bundle_crc32'],commit['bundle_byte_length'])==(result['bundle_sha256'],result['bundle_crc32'],result['bundle_bytes']),'Commit original bundle hash/CRC/length receipt differs')
    C.codec_file(s['source_readback_codec'],so,codec);C.codec_file(t['target_final_readback_codec'],to,codec)
    return dict(**result,published_originals_unchanged=True,whole_source_load_and_target_final_load_bytes_equal=True)

def verify_native(source_path,target_path,prereg,session_path):
    prereg_before=C.pin(prereg);session_before=C.pin(session_path)
    p,cm,lineage,protocol,dep=preflight(prereg);session=C.read(session_path)
    need(session['schema']=='hero-air-disk-restore-two-process-session-v001' and session['is_template'] is False and session['actual_recorded'] is True and session['FinalAccepted'] is False and C.same_pin(session['root_prereg_pin'],C.pin(prereg)),'Actual new two-process Root session required')
    for phase in ('before','after'):
        need(C.same_pin(session[phase+'_compiled_manifest_pin'],p['compiled_manifest_pin']) and C.same_pin(session[phase+'_game_dll_pin'],p['game_dll_pin']),'Actual before/after current CM/DLL changed')
    need(Path(source_path).resolve()==Path(p['source_archive']).resolve() and Path(target_path).resolve()==Path(p['target_archive']).resolve() and Path(source_path).resolve()!=Path(target_path).resolve(),'Two exact distinct Root-registered native archives required')
    s,sl,se,sv=native_receipts(source_path,'source',p,prereg,session['source']);t,tl,te,tv=native_receipts(target_path,'target',p,prereg,session['target'])
    order=C.verify_process_order(se,te)
    need(tl['source_process_observed_exited_before_target'] is True and tl['source_process_id']==int(s['process_id']),'Actual target launch source OS exit binding differs')
    so=Path(source_path).resolve()/'原件';to=Path(target_path).resolve()/'原件';codec=C.codec_file(s['checkpoint']['codec'],so)
    need(tv['-DungeonHeroAirDiskExpectedRun']==s['checkpoint']['run'] and tv['-DungeonHeroAirDiskExpectedOwner']==s['checkpoint']['owner'] and tv['-DungeonHeroAirDiskExpectedCodecSHA']==hashlib.sha256(codec).hexdigest() and tv['-DungeonHeroAirDiskSourcePID']==s['process_id'],'Actual target expected identity/completeCodec/exited source PID args differ')
    source_flow=C.verify_source_flow(s,codec);target_flow=C.verify_target_flow(t,s,codec,to);disk=verify_disk(s,t,so,to,p,codec)
    sources,am,ap,wm,wp=art_sources(dep);d,paths,L,loaded,F,oldC=dep;roles={}
    for name,r,original in (('source',s,so),('target',t,to)):
        resources=L.verify_resources(original,r,sources,am,ap);movie=F.verify_png_fifo(original,r)
        need(len(movie)==len(r['observations']),'Every actual completed callback needs one original PNG')
        counts,slots=inspect_draws(r,dep,am,ap,wm,wp);pixels=optical(original,r,movie,sources,dep,slots);audio=audio_audit(original/'runtime-report.json',name,dep,p)
        roles[name]=dict(native_report_pin=C.pin(original/'runtime-report.json'),process_id=int(r['process_id']),callbacks=len(r['observations']),actual_resources=resources,all_related_typed_draws=counts,source_pixels=pixels,native_PNG_FIFO_CRC_verified=True,audio=audio)
    # Actual inputs are immutable throughout verification; don't silently accept
    # a Source/Content/DLL change that happens while large readbacks are checked.
    for row in cm['files']:C.resolve_pin(row)
    for field in ('compiled_manifest_pin','game_dll_pin','source_admission_pin','source_candidate_freeze_pin','checker_freeze_pin'):C.resolve_pin(p[field])
    for row in (prereg_before,session_before):C.resolve_pin(row)
    for name in ('source','target'):
        role=session[name]
        for field in ('session_index_pin','launch_receipt_pin','exit_receipt_pin'):C.resolve_pin(role[field])
        C.resolve_pin(C.read(C.resolve_pin(role['session_index_pin']))['runtime_report_pin'])
    for row in s['disk']['published_after']:
        value=C.pin(row['original_path']);need(signature(value)==signature(row),'Published disk bytes changed during independent verification')
        C.resolve_pin(row['evidence_file'])
    return dict(schema='hero-air-disk-restore-independent-two-native-v001',passed=True,root_prereg_pin=C.pin(prereg),two_process_session_pin=C.pin(session_path),compiled_manifest_pin=p['compiled_manifest_pin'],source_candidate_freeze_pin=p['source_candidate_freeze_pin'],source_admission_pin=p['source_admission_pin'],source_repair_admission_pins=p['source_repair_admission_pins'],checker_freeze_pin=p['checker_freeze_pin'],game_dll_pin=p['game_dll_pin'],current_lineage=lineage,process_order=order,profile_id=p['profile_id'],run=s['run'],owner=s['owner'],current_room=s['current_room'],source_flow=source_flow,target_flow=target_flow,disk=disk,roles=roles,
                restore_scope='BoundRunOnly-v2; not Account/talents/Settings/full Profile',audio_queue_continuity_claimed=False,full_realtime_playback_reviewed=False,visual_reviewed=False,audio_listened=False,RootApproved=False,FinalAccepted=False)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--prereg',required=True);ap.add_argument('--preflight',action='store_true');ap.add_argument('--source');ap.add_argument('--target');ap.add_argument('--session');ap.add_argument('--out');a=ap.parse_args()
    try:
        need((a.preflight and not any((a.source,a.target,a.session))) or (not a.preflight and all((a.source,a.target,a.session))),'Select new preflight or complete two-process native pair')
        if a.preflight:
            p,cm,lineage,protocol,dep=preflight(a.prereg);result=dict(schema='hero-air-disk-restore-independent-preflight-v001',passed=True,root_prereg_pin=C.pin(a.prereg),compiled_manifest_pin=p['compiled_manifest_pin'],lineage=lineage,actual_native_verified=False,UE_started=False,RootApproved=False,FinalAccepted=False)
        else:result=verify_native(a.source,a.target,a.prereg,a.session)
    except Exception as e:result=dict(schema='hero-air-disk-restore-independent-rejection-v001',passed=False,error=str(e),failure_evidence_preserved=True,UE_started=False,RootApproved=False,FinalAccepted=False)
    if a.out:
        with Path(a.out).open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(result,ensure_ascii=False,allow_nan=False));return 0 if result['passed'] else 3

if __name__=='__main__':raise SystemExit(main())
