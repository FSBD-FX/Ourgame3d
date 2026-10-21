"""Read-only K causal/native proof checker. Model tests are never native evidence."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, math, subprocess, sys, zlib
from copy import deepcopy
SOUND='/Game/Production/HeroLocomotion/v001/Audio/SW_AUD_HERO_STEP_LIGHT_01_v001.SW_AUD_HERO_STEP_LIGHT_01_v001'
CUE='HERO_STEP_LIGHT_01'
class NotReady(ValueError): pass
def need(ok,why):
    if not ok: raise ValueError(why)
def finite(x): return type(x) in (int,float) and math.isfinite(x)
def u64(x, nonzero=True):
    need(isinstance(x,str) and x.isascii() and x.isdecimal() and str(int(x))==x and 0<=int(x)<2**64 and (not nonzero or int(x)>0), 'canonical U64 identity required'); return int(x)
def pair(x):
    need(isinstance(x,list) and len(x)==2 and all(finite(v) for v in x),'finite XY required');return x
def near(a,b,t=1e-6):return finite(a) and finite(b) and abs(a-b)<=t
def action(a):
    u64(a['action_id']);u64(a['instance_id']);need(a['type']==2 and a['weapon']==0 and a['started_airborne'] is False and a['facing'] in [-1,1],'real grounded SWD Skill identity required')
    for k in ('start','lock_at','active_at','active_end','end'):need(finite(a[k]),'finite original deadline required')
    # Current authored timings with zero speed affix; prereg must reject changed speed profiles.
    need(near(a['lock_at']-a['start'],.08) and near(a['active_at']-a['start'],.20) and near(a['active_end']-a['start'],.30) and near(a['end']-a['start'],.68),'original .08/.20/.30/.68 action deadlines changed')
    need(a['speed_pct']==0 and a['cooldown_duration']==(4 if a['locked'] else 0),'baseline speed and actual unlocked0/locked4 cooldown facts required');return a
PARENT=('sequence','cue','at_time','run','room','owner','action_id','instance_id','operation_id','revision','forward_step')
def source_key(f):return (f['run'],f['room'],f['owner'],f['action_id'],f['instance_id'],f['forward_step']['event_id'],f['forward_step']['subhit_id'])
def audit_causal(r):
    need(r['schema']=='swd-forward-step-native-observer-v001' and r['passed'] is True and r['failure']=='' and r['flow_complete'] is True,'actual successful observer report required')
    need(r['player_enemy_HP_position_AI_clock_writes'] is False and r['enemy_diagnostic_used'] is False,'diagnostic gameplay forcing prohibited in this scope')
    need(r['formal_accepted'] is False and r['audio_listened'] is False and r['device_onset_measured'] is False,'request/native retention cannot claim listening or device onset')
    a=action(r['accepted_action']);locked=action(r['locked_action_source']);need(locked['locked'] is True and locked['cooldown_duration']==4 and all(locked[k]==a[k] for k in ('action_id','instance_id','start','lock_at','active_at','active_end','end')),'actual locked cooldown source snapshot required');need(u64(r['weapon_version_end'])==u64(r['weapon_version'])+1,'actual one SkillLock weapon version increment required');face=r['requested_facing'];need(a['facing']==face and a['instance_id']==r['weapon_instance'],'actual K instance/facing mismatch')
    kind,side=r['case'].rsplit('_',1);need(kind in ('full','partial','blocked_zero') and side in ('right','left') and face==(1 if side=='right' else -1),'case/facing mismatch')
    aa=r['action_audio'];need(aa['schema']=='swd-forward-step-action-audio-observation-v001' and aa['scope_changes']==0 and aa['fact_sequence_gaps']==0,'scope changed or source log gap')
    need(aa['request_only'] is True and aa['source_epoch_available'] is False and aa['device_onset_measured'] is False,'honest parent-scope/request boundary required')
    facts=aa['facts'];reqs=aa['requests'];seqs=[u64(f['sequence']) for f in facts];need(len(seqs)==len(set(seqs)) and seqs==list(range(1,len(seqs)+1)),'complete unique ActionAudio source prefix required')
    for f in facts:
        for k in ('room','owner','action_id','instance_id','operation_id','revision'):u64(f[k],False)
        need(f['run']==r['run'] and f['room']==r['room'],'source parent run/room stale')
        w=f['forward_step'];need(type(w['present']) is bool,'actual optional DTO marker required')
        if not w['present']:need(all(w[k] is None for k in ('event_id','subhit_id','requested_signed_distance','before','after','committed_delta')),'absent DTO fields must be null, never fabricated zero')
        if w['present']:need(f['cue']==CUE and f['owner']==r['owner'] and f['action_id']==a['action_id'] and f['instance_id']==a['instance_id'],'true forward step parent K/player scope mismatch')
    step=[f for f in facts if f['cue']==CUE]
    stepq=[q for q in reqs if q['source']['cue']==CUE]
    requestseq=[q['source']['sequence'] for q in reqs];need(len(requestseq)==len(set(requestseq)),'duplicate actual HUD request source')
    for q in reqs:
        f=next((f for f in facts if f['sequence']==q['source']['sequence']),None);need(f is not None and all(q['source'][k]==f[k] for k in PARENT),'HUD request Source is not exact actual append copy')
        need(finite(q['requested_at']) and 0<=q['requested_at']-f['at_time']<=.25+1e-9,'HUD stale/future request age')
        need(q['first_seen_callback']>=f['first_seen_callback'] and q['first_seen_wall_min_s']<=q['first_seen_wall_max_s'],'actual callback request observation bounds invalid')
    if kind=='blocked_zero':
        need(not step and not stepq,'zero commit must emit no forward-step fact/request')
        raise NotReady('No independent actual ForwardStep zero-placement commit reader admitted; absence of DTO is insufficient')
    need(len(step)==len(stepq)==1,'exactly one actual step append and HUD request required')
    f,q=step[0],stepq[0];w=f['forward_step'];need(w['present'] is True,'positive committed step requires true DTO Present')
    u64(w['event_id']);need(w['subhit_id']=='0','actual ForwardStep subhit 0 required');need(near(w['requested_signed_distance'],face*30.),'actual signed requested 30cm changed')
    b,e,d=map(pair,(w['before'],w['after'],w['committed_delta']));need(all(near(b[i]+d[i],e[i],1e-7) for i in range(2)),'committed Delta is not actual After minus Before')
    distance=math.hypot(*d);need(distance>1e-4 and abs(d[1])<1e-6 and d[0]*face>0,'real positive signed horizontal commit required')
    need(abs(distance-30.)<.05 if kind=='full' else 1e-4<distance<29.95,'full/partial actual commit classification mismatch')
    need(near(f['at_time'],a['active_at']) and f['observed_sim']>=f['at_time'],'step source must retain exact actual ActiveAt deadline, no delayed append')
    need(q['sound_path']==SOUND and near(q['volume'],.25,1e-7) and near(q['pitch'],1.),'existing step SoundWave/gain .25/pitch1 mapping changed')
    need(len({source_key(x) for x in step})==1,'causal source key duplicate')
    rows=r['observations'];need(rows and [o['callback_index'] for o in rows]==list(range(len(rows))),'actual callback sequence gap')
    offsets=r['capture_timing']['frame_wall_offsets_s'];need(len(offsets)==len(rows) and all(near(o['wall_offset_s'],offsets[i]) for i,o in enumerate(rows)),'native callback wall origin mismatch')
    need(all(finite(x) and x>=0 for x in offsets) and all(x<=y for x,y in zip(offsets,offsets[1:])),'wall callback times invalid')
    for event in step:
        i=event['first_seen_callback'];need(type(i) is int and 0<=i<len(rows),'source callback outside actual capture');o=rows[i];need(near(event['observed_sim'],o['sim']) and event['first_seen_wall_min_s']<=event['first_seen_wall_max_s']<=o['wall_offset_s']+.01 and event['first_seen_wall_max_s']>=o['wall_offset_s']-.01,'source callback/sim/wall window mismatch')
    for request in stepq:
        i=request['first_seen_callback'];need(type(i) is int and 0<=i<len(rows) and request['requested_at']<=rows[i]['sim'],'request callback/time outside actual capture')
    active=[o for o in rows if o['action']['active'] and o['action']['action_id']==a['action_id']];need(active,'no real live K action samples')
    seen=set()
    for o in active:
        x=action(o['action']);need(all(x[k]==a[k] for k in ('action_id','instance_id','start','lock_at','active_at','active_end','end')),'live K identity/deadlines replaced')
        need(o['height']==o['vertical_velocity']==0 and o['melee_grounded'] is o['weapon_grounded'] is True,'actual K sample not grounded')
        t=o['secondary'];s=t['sample'];sx=action(s['action']);need(all(sx[k]==x[k] for k in ('action_id','instance_id','start','lock_at','active_at','active_end','end')) and near(sx['sample_time'],o['sim']),'K trace not actual same-draw action/time')
        need(all(t[k] is True for k in ('opt_in','owns_branch','profile_ready','atomic_preflight_ready','drawn')) and t['missing_reason']=='','incomplete atomic K branch')
        need(t['player_entity_id']==r['owner'] and t['binding']['run']==r['run'] and t['binding']['owner']==r['owner'] and t['binding']['weapon_instance']==r['weapon_instance'] and t['binding']['armor_instance']==r['armor_instance'],'actual trace binding mismatch')
        updates=o['runtime_inventory'];need(updates['available'] is True,'actual runtime inventory unavailable');changes=[v for v in updates['runtime_updates'] if v['instance_id']==a['instance_id']];need(len(changes)==(1 if o['sim']>=a['lock_at'] else 0),'actual cooldown receipt presence differs from lock boundary')
        if changes:
            v=changes[0];need(v['before_version']==r['weapon_version'] and v['after_version']==r['weapon_version_end'] and v['ok'] is True and v['replayed'] is False and v['before_ammo']==v['ammo'] and a['lock_at']<=v['at_time']<=o['sim'] and near(v['cooldown_deadline'],a['lock_at']+4.),'legal inventory version increment/cooldown receipt mismatch');need(t['binding']['weapon_version']==v['after_version'],'draw binding weapon version not actual committed cooldown version')
        else:need(t['binding']['weapon_version']==r['weapon_version'],'pre-lock weapon version changed')
        bounds=[a['start'],a['lock_at'],a['start']+.14,a['active_at'],a['start']+.25,a['active_end'],a['start']+.42,a['start']+.55,a['end']]
        need(len(s['boundaries'])==9 and all(near(v,b) for v,b in zip(s['boundaries'],bounds)),'trace altered actual K frame boundaries')
        frame=s['frame'];need(type(frame) is int and 0<=frame<8 and bounds[frame]<=o['sim']<bounds[frame+1],'trace frame/sample time mismatch');seen.add(frame)
        need(t['expected_draw_count']==8 and len(t['slots'])==len(t['actual_stack'])==8 and [p['slot'] for p in t['slots']]==list(range(8)),'actual eight-slot order incomplete')
        need(all(p['selected'] is p['texture_ready'] is p['drawn'] is True for p in t['slots']) and [p['texture'] for p in t['slots']]==t['actual_stack'],'actual selected/drawn stack differs')
        need({p['texture'] for p in t['slots']}<={p['texture'] for p in t['residents']},'selected K texture not in actual resident closure')
        need(len(t['residents'])==57 and len({p['texture'] for p in t['residents']})==57 and all(p['ready'] is True and p['pending_initialization'] is False and p['class']=='Texture2D' and p['width']==p['height']==512 for p in t['residents']),'actual full 57-resource residency missing')
        need(o['common_draw']['clip']=='sword_secondary' and o['common_draw']['actual_stack']==t['actual_stack'] and o['common_draw']['draw_id']==t['draw_id'],'common draw and typed trace not same draw')
    need(seen==set(range(8)) and r['secondary_frame_mask']==255,'all actual K0..7 frames required')
    ready=lambda o:o['common_draw']['clip']=='sword_ready_idle' and o['common_draw']['supported'] is True and o['secondary']['drawn'] is False
    need(len([o for o in rows if o['sim']<a['start'] and ready(o)])>=3 and r['ready_before_frames']>=3,'actual Ready entry absent')
    need(len([o for o in rows if o['sim']>=a['end'] and not o['action']['active'] and ready(o)])>=2 and r['ready_after_frames']>=2,'unchanged original End to Ready join absent')
    keys=[p['key'] for p in r['normal_inputs'] if p['down']];need(keys.count('K')==1 and keys.count('E')==1 and keys.count('Enter')==1 and set(keys)<=set(['K','E','Enter','W','A','S','D']),'normal input route introduced jump/J/forced action')
    return dict(passed=True,causal_source_key=list(source_key(f)),committed_cm=distance,K8_and_original_End_join=True,true_HUD_PlaySound2D_request=True,each_cue_PCM_identified=False,device_onset_measured=False,listened=False,formal_accepted=False)
def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def audit_resources(r,prereg,original):
    from PIL import Image
    pins=prereg['resource_pins'];rows=r['startup_resource_readbacks'];need(len(pins)==len(rows)==81,'K57 plus Ready24 original source/GPU closure required')
    need({p['texture'] for p in pins}=={x['texture'] for x in rows} and len({x['texture'] for x in rows})==81,'missing/duplicate source/GPU resources')
    need(r['startup_readback_complete'] is True and r['startup_readback_stop_monotonic_s']<r['capture_timing']['capture_start_monotonic_s'],'source/GPU readback must complete before audio')
    for p in pins:
        x=next(x for x in rows if x['texture']==p['texture']);png=Path(p['source_png']);data=png.read_bytes();need(len(data)==p['bytes'] and hashlib.sha256(data).hexdigest()==p['sha256'],'immutable actual source PNG pin mismatch')
        rgba=Image.open(png).convert('RGBA');need(rgba.size==(512,512),'source PNG512 required');raw=rgba.tobytes();need(hashlib.sha256(raw).hexdigest()==p['rgba_sha256'],'source RGBA hash mismatch')
        bgra=rgba.tobytes('raw','BGRA');gpu=(original/x['GPU_file']).read_bytes();editor=(original/x['editor_source_file']).read_bytes();need(gpu==editor==bgra and len(gpu)==512*512*4,'actual GPU/editor pixels differ from full source PNG')
        need(zlib.crc32(gpu)&0xffffffff==x['GPU_BGRA8_CRC32'] and zlib.crc32(editor)&0xffffffff==x['editor_source_BGRA8_CRC32'],'actual GPU/editor CRC changed')
        need(x['resource_ready'] is True and x['pending_initialization'] is False and x['class']=='Texture2D' and x['width']==x['height']==512,'actual resource not ready')
    return dict(actual_full_source_GPU_resources=81,unchanged_source_pixels=True)
def audit_native(archive,prereg,prereg_path):
    
    if prereg.get('ready') is not True: raise NotReady('; '.join(prereg.get('pending',[])) or 'prereg not ready')
    original=Path(archive)/'原件';rp=original/'runtime-report.json';r=json.loads(rp.read_text(encoding='utf-8-sig'));result=audit_causal(r)
    need(prereg['ready'] is True,'prereg not ready')
    launch=json.loads((Path(archive)/'launch-argv.json').read_text(encoding='utf-8-sig'));started=json.loads((Path(archive)/'process-started.json').read_text(encoding='utf-8-sig'));psha=hashlib.sha256(Path(prereg_path).read_bytes()).hexdigest();need(launch['prereg_sha256']==started['prereg_sha256']==psha and started['process_id']==r['process_id'] and started['native_run_attempted'] is True,'actual launched native process/prereg pin mismatch')
    driver=load_module(Path(__file__).with_name('drive-swd-forward-step-native-v001.py'),'swd_frozen_driver_v001');expected=driver.launch_args(prereg,Path(prereg['editor_executable']['path']),Path(prereg['uproject']['path']),original,r['case'],prereg_path);need([x.replace('\\','/') for x in launch['argv']]==[x.replace('\\','/') for x in expected],'exact original normal-input launch argv mismatch')
    eq=[o for o in r['observations'] if o['equipment_action']['active'] and o['equipment_action']['kind']==2 and o['equipment_action']['source_id']==r['light_source'] and o['equipment_action']['instance_id']==r['armor_instance'] and o['equipment_action']['slot']==2];need(eq,'actual E PickupArmor interval for QA source absent');first=eq[0]['equipment_action'];need(first['start']<first['deadline']<r['accepted_action']['start'] and all(o['equipment_action']['start']==first['start'] and o['equipment_action']['deadline']==first['deadline'] and o['equipment_action']['action_id']==first['action_id'] for o in eq),'actual equipment action identity/deadline changed');need(any(o['sim']>=first['deadline'] and o['equipment_action']['armor_instance']==r['armor_instance'] and not o['equipment_action']['active'] for o in r['observations']),'real armor commit after unchanged equipment deadline absent')
    result['resources']=audit_resources(r,prereg,original)
    deps=prereg['checker_dependencies']
    for k,p in deps.items():
        b=Path(p['path']).read_bytes();need(len(b)==p['bytes'] and hashlib.sha256(b).hexdigest()==p['sha256'],'checker dependency pin changed: '+k)
    mix=load_module(deps['main_mix']['path'],'swd_native_main_mix_v001');result['main_mix']=mix.audit(rp,require_frame_timing=True)
    completed=subprocess.run([sys.executable,'-B','-X','utf8',deps['native_png']['path'],'--archive',str(archive)],capture_output=True,text=True,encoding='utf-8');need(completed.returncode==0,'actual full native PNG CRC/FIFO check failed: '+completed.stderr);result['PNG']=json.loads(completed.stdout)
    # External pinned checker must verify actual K layered composition against captured pixels,
    # not just reproduce plan math. Interface is deliberately explicit and currently unavailable.
    art=load_module(deps['K_pixel_composition']['path'],'swd_native_K_pixels_v001');result['K_pixels']=art.audit(archive=Path(archive),prereg=prereg)
    need(result['K_pixels'].get('actual_native_pixel_composition_verified') is True,'actual K8 PNG composition not verified')
    return result
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--archive',type=Path,required=True);ap.add_argument('--prereg',type=Path,required=True);ns=ap.parse_args()
    try:out=audit_native(ns.archive,json.loads(ns.prereg.read_text(encoding='utf-8-sig')),ns.prereg);code=0
    except NotReady as e:out=dict(status='NotReady',passed=False,reason=str(e));code=2
    except (ValueError,KeyError,OSError,AssertionError,TypeError) as e:out=dict(status='NeedsFixes',passed=False,reason=str(e));code=3
    print(json.dumps(out,ensure_ascii=False,indent=2));sys.exit(code)
