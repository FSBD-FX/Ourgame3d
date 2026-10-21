from pathlib import Path
import json
H=Path('F:/Ourgame/source-assets/production/fairytale-sword-secondary-v001/forward-step-native-observer-candidate-v002');O=H.parent/'forward-step-native-observer-candidate-v001'
s=(O/'check-swd-forward-step-native-v001.py').read_text(encoding='utf-8-sig')
def rep(a,b):
 global s
 assert s.count(a)==1,a[:100];s=s.replace(a,b,1)
helper='''
def placement_key(w):return tuple(w[k] for k in ('run','room','owner','epoch','restart','action_id','instance_id','event_id','subhit_id','at_time'))
def audit_placement(r,require_case_match=True):
    need(r['schema']=='swd-forward-step-native-observer-v002','actual V002 getter observer report required')
    rows=r['observations'];items=r['placement_witnesses'];need(len(items)==1,'one actual unique placement event snapshot required; absence is not zero')
    w=items[0];need(w['present'] is True and w['grounded_at_commit'] is True and w['actual_kernel_window_matches_step_source_key'] is True,'actual grounded getter+issued-event source required')
    for k in ('room','owner','epoch','restart','action_id','instance_id','event_id','subhit_id','revision_at_commit','kernel_next_event_id'):u64(w[k],k not in ('epoch','restart','subhit_id'))
    a=r['accepted_action'];need(w['run']==r['run'] and w['room']==r['room'] and w['owner']==r['owner'] and w['epoch']==r['epoch'] and w['restart']==r['restart'],'actual getter run/room/owner/epoch scope stale')
    need(w['action_id']==a['action_id'] and w['instance_id']==a['instance_id']==r['weapon_instance'] and w['kind']==2 and w['weapon']==0 and w['subhit_id']=='0' and w['action_start']==a['start'] and w['at_time']==a['active_at'],'actual getter action/instance/event kind/deadline mismatch')
    need(u64(w['event_id'])<u64(w['kernel_next_event_id']) and near(w['requested_signed_distance'],r['requested_facing']*30.),'actual issued cursor/request mismatch')
    issued=w['actual_kernel_window_event'];need(all(issued[k]==w[k] for k in ('action_id','instance_id','subhit_id','at_time','action_start')) and u64(issued['event_id'])==u64(w['event_id'])+1 and issued['kind']==3,'getter step key not linked to the actual immediate next kernel ActiveWindow')
    b,e,d=map(pair,(w['before'],w['after'],w['committed_delta']));need(all(near(b[i]+d[i],e[i],1e-7) for i in range(2)) and abs(d[1])<1e-6,'actual commit is not real horizontal After-Before')
    distance=math.hypot(*d);kind='blocked_zero' if distance==0 else 'full' if abs(distance-30.)<.05 else 'partial' if 1e-4<distance<29.95 else 'unexpected'
    need(kind!='unexpected' and (distance==0 or d[0]*r['requested_facing']>0),'actual commit has unsupported size/direction')
    need(r['native_route_classification']==kind,'native classification does not match actual getter delta')
    if require_case_match:need(r['case'].rsplit('_',1)[0]==kind,'actual measured route classification differs from requested case')
    i=w['first_seen_callback'];need(type(i) is int and 0<=i<len(rows),'actual placement callback outside recording');first=rows[i];poll=first['placement_witness_poll'];need(poll['getter_called_while_action_active'] is poll['available'] is poll['new_unique_event'] is True and poll['source']==w and first['action']['active'] is True,'placement not retained from actual first active callback')
    need(near(first['sim'],w['readback_sim']) and w['at_time']<=w['observed_simulation_time']<=w['readback_sim']<a['end'] and near(first['wall_offset_s'],w['first_seen_wall_offset_s']),'actual placement source time/callback is stale or after End')
    new=0;immutable=['present','grounded_at_commit','run','room','owner','epoch','restart','action_id','instance_id','event_id','subhit_id','kind','weapon','action_start','at_time','observed_simulation_time','requested_signed_distance','before','after','committed_delta']
    for row in rows:
        p=row['placement_witness_poll'];need(p['callback_index']==row['callback_index'] and near(p['callback_sim'],row['sim']),'placement poll not actual same callback')
        if not row['action']['active']:need(p['getter_called_while_action_active'] is False and p['available'] is False,'getter cannot be sampled after action End')
        if p['available']:
            need(p['getter_called_while_action_active'] is True and row['action']['active'] is True and all(p['source'][k]==w[k] for k in immutable),'duplicate key changed actual immutable commit or wrong action callback')
            need(placement_key(p['source'])==placement_key(w),'actual event-key mismatch');new+=int(p['new_unique_event'])
    need(new==1,'actual placement event was not deduplicated exactly once')
    return dict(passed=True,actual_source_placement_verified=True,causal_source_key=list(placement_key(w)),committed_cm=distance,classification=kind,witness=w,formal_accepted=False,checker_accepted=False)
'''
rep('def audit_causal(r):',helper+'\ndef audit_causal(r):')
rep("r['schema']=='swd-forward-step-native-observer-v001'", "r['schema']=='swd-forward-step-native-observer-v002'")
rep("need(r['formal_accepted'] is False and r['audio_listened'] is False and r['device_onset_measured'] is False,'request/native retention cannot claim listening or device onset')","need(r['formal_accepted'] is False and r['checker_accepted'] is False and r['audio_listened'] is False and r['device_onset_measured'] is False,'native collection cannot grant checker/formal/listening/device acceptance')")
start=s.index("    if kind=='blocked_zero':\n");end=s.index("    rows=r['observations'];",start)
s=s[:start]+'''    placement=audit_placement(r,require_case_match=r['route_mode']=='strict');pw=placement['witness'];distance=placement['committed_cm'];actual_kind=placement['classification']
    if actual_kind=='blocked_zero':
        need(not step and not stepq,'measured zero commit must emit no step fact/request')
    else:
        need(len(step)==len(stepq)==1,'exactly one actual positive step append and HUD request required')
        f,q=step[0],stepq[0];w=f['forward_step'];need(w['present'] is True,'positive committed step requires true audio DTO')
        need(all(w[k]==pw[k] for k in ('event_id','subhit_id','requested_signed_distance','before','after','committed_delta')) and all(f[k]==pw[k] for k in ('run','room','owner','action_id','instance_id','at_time')),'actual audio DTO does not copy the same real placement event')
        need(near(f['at_time'],a['active_at']) and f['observed_sim']>=f['at_time'],'actual step deadline changed')
        need(q['sound_path']==SOUND and near(q['volume'],.25,1e-7) and near(q['pitch'],1.),'actual SoundWave gain/pitch changed')
        need(len({source_key(x) for x in step})==1,'actual audio source key duplicate')
''' +s[end:]
rep("return dict(passed=True,causal_source_key=list(source_key(f)),committed_cm=distance,K8_and_original_End_join=True,true_HUD_PlaySound2D_request=True,each_cue_PCM_identified=False,device_onset_measured=False,listened=False,formal_accepted=False)","return dict(passed=True,causal_source_key=placement['causal_source_key'],committed_cm=distance,classification=actual_kind,K8_and_original_End_join=True,true_HUD_PlaySound2D_request=(actual_kind!='blocked_zero'),measured_zero_no_step_request=(actual_kind=='blocked_zero'),each_cue_PCM_identified=False,device_onset_measured=False,listened=False,formal_accepted=False)")
start=s.index('def audit_native(archive,prereg,prereg_path):');s=s[:start]+'''def audit_native(archive,prereg,prereg_path):
    original=Path(archive)/'原件';rp=original/'runtime-report.json';r=json.loads(rp.read_text(encoding='utf-8-sig'))
    driver=load_module(Path(__file__).with_name('drive-swd-forward-step-native-v002.py'),'swd_native_driver_v002')
    driver.preflight(prereg_path,r['case'],prereg['route_mode'])
    need(r['route_mode']==prereg['route_mode'] and r['formal_accepted'] is False and r['checker_accepted'] is False,'actual report mode/acceptance boundary changed')
    launch=json.loads((Path(archive)/'launch-argv.json').read_text(encoding='utf-8-sig'));started=json.loads((Path(archive)/'process-started.json').read_text(encoding='utf-8-sig'));psha=hashlib.sha256(Path(prereg_path).read_bytes()).hexdigest()
    need(launch['prereg_sha256']==started['prereg_sha256']==psha and started['process_id']==r['process_id'] and started['native_run_attempted'] is True,'actual process/prereg pin mismatch')
    expected=driver.launch_args(prereg,Path(prereg['editor_executable']['path']),Path(prereg['uproject']['path']),original,r['case'],prereg_path);need([x.replace('\\\\','/') for x in launch['argv']]==[x.replace('\\\\','/') for x in expected],'exact launch argv mismatch')
    need(driver.route_digest(r['route_input_configuration'])==driver.route_digest(prereg['cases'][r['case']]),'actual route config differs from pinned prereg')
    deps=prereg['checker_dependencies']
    for name in ('main_mix','native_png'):driver.pin(deps[name])
    def equipment():
        eq=[o for o in r['observations'] if o['equipment_action']['active'] and o['equipment_action']['kind']==2 and o['equipment_action']['source_id']==r['light_source'] and o['equipment_action']['instance_id']==r['armor_instance'] and o['equipment_action']['slot']==2];need(eq,'actual E PickupArmor interval absent');first=eq[0]['equipment_action'];need(first['start']<first['deadline']<r['accepted_action']['start'] and all(o['equipment_action']['start']==first['start'] and o['equipment_action']['deadline']==first['deadline'] and o['equipment_action']['action_id']==first['action_id'] for o in eq),'actual armor action identity/deadline changed');need(any(o['sim']>=first['deadline'] and o['equipment_action']['armor_instance']==r['armor_instance'] and not o['equipment_action']['active'] for o in r['observations']),'actual armor commit absent');return dict(passed=True)
    def mix():return load_module(deps['main_mix']['path'],'swd_main_mix_v002').audit(rp,require_frame_timing=True)
    def png():
        q=subprocess.run([sys.executable,'-B','-X','utf8',deps['native_png']['path'],'--archive',str(archive)],capture_output=True,text=True,encoding='utf8');need(q.returncode==0,'native PNG CRC/FIFO failed: '+q.stderr);return json.loads(q.stdout)
    work={'placement':lambda:audit_placement(r,require_case_match=prereg['route_mode']=='strict'),'causal':lambda:audit_causal(r),'equipment':equipment,'resources':lambda:audit_resources(r,prereg,original),'main_mix':mix,'PNG':png}
    if prereg['route_mode']=='exploratory_pilot':
        results={};errors={}
        for name,fn in work.items():
            try:results[name]=fn()
            except (ValueError,KeyError,OSError,AssertionError,TypeError) as e:errors[name]=str(e)
        return dict(status='ExploratoryPilotRecorded',passed=False,pilot_collection_retained=True,pilot_checks_passed=not errors,route_mode='exploratory_pilot',formal_accepted=False,checker_accepted=False,actual_native_route_verified=False,observed_classification=results.get('placement',{}).get('classification'),checks=results,errors=errors,K_pixels=dict(status='PendingIndependentNativePixelChecker',actual_native_pixel_composition_verified=False),listened=False,device_onset_measured=False)
    result={name:fn() for name,fn in work.items()}
    if not deps.get('K_pixel_composition'):raise NotReady('Independent actual K native pixel composition checker pending')
    driver.pin(deps['K_pixel_composition']);art=load_module(deps['K_pixel_composition']['path'],'swd_K_pixels_v002');result['K_pixels']=art.audit(archive=Path(archive),prereg=prereg);need(result['K_pixels'].get('actual_native_pixel_composition_verified') is True,'actual K native composition not verified')
    result.update(passed=True,checker_accepted=True,formal_accepted=False,route_mode='strict',listened=False,device_onset_measured=False);return result
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--archive',type=Path,required=True);ap.add_argument('--prereg',type=Path,required=True);ns=ap.parse_args()
    try:out=audit_native(ns.archive,json.loads(ns.prereg.read_text(encoding='utf-8-sig')),ns.prereg);code=0
    except NotReady as e:out=dict(status='NotReady',passed=False,reason=str(e),formal_accepted=False,checker_accepted=False);code=2
    except (ValueError,KeyError,OSError,AssertionError,TypeError) as e:out=dict(status='NeedsFixes',passed=False,reason=str(e),formal_accepted=False,checker_accepted=False);code=3
    print(json.dumps(out,ensure_ascii=False,indent=2));sys.exit(code)
'''
(H/'check-swd-forward-step-native-v002.py').write_text(s,encoding='utf8')
print('prepared actual-getter checker; no native evidence generated')
