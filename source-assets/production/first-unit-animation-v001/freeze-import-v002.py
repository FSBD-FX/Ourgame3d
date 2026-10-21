"""Freeze actual122 unique candidate PNGs. No model or image modification."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT.parents[2]/'过程图稿与视频'/'2026-10-14_首单元动作生产_v001'
spec = importlib.util.spec_from_file_location('pixel_audit', ROOT/'finalize-batch.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
sys.path.insert(0,r'C:\Users\22499\.codex\skills\generate2dsprite\scripts')
from generate2dsprite import estimate_anchor

# Actual source directories are immutable; failed shield request14 is excluded.
CONFIG = [
 ('hero','idle','hero-idle-matte-v002',3,None),
 ('hero','walk','hero-walk-matte-v002',4,None),
 ('hero','primary_1','hero-primary-1-body-matte-v002',5,[.17,.12,.31]),
 ('hero','primary_2','hero-primary-2-body-matte-v002',6,[.15,.12,.27]),
 ('hero','primary_3','hero-primary-3-body-matte-v002',7,[.22,.12,.32]),
 ('stone','wake','stone-wake',8,None),
 ('stone','idle','stone-idle',10,None),
 ('stone','dormant','stone-dormant',11,None),
 ('stone','walk','stone-walk',12,None),
 ('stone','charge','stone-charge',13,[.9,.8,1.6]),
 ('stone','shield_bash','stone-shield-bash-corrected-v002',15,[.7,.12,.9]),
 ('stone','recovery','stone-recovery',16,None),
 ('stone','hurt','stone-hurt',17,None),
 ('stone','death','stone-death',18,None),
 ('hero','jump_family','hero-jump-family-processor-review',19,None),
 ('hero','dodge','hero-dodge',20,None),
 ('hero','hurt','hero-hurt',21,None),
 ('hero','death','hero-death',22,None),
 ('hero','secondary','hero-secondary-body',23,[.2,.1,.38]),
 ('hero','air_primary_1','hero-air-primary-1-body-processor-review',24,[.17,.12,.31]),
]

# Manually reviewed belt-buckle centres, a visible proxy rather than a skeleton bone.
AIR_BUCKLES = {
 'jump_family':[(269,301),(270,293),(268,299),(269,300),(272,277),(277,280),(275,297),(274,282)],
 'air_primary_1':[(242,280),(251,281),(263,279),(290,279),(240,280),(237,280)],
}
IDLE_BUCKLE = [269,325]
IDLE_ROOT = [256,472]

def write(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def phase_plan(durations, source):
    plan = audit.phase_plan(durations)
    if plan:
        plan['source']=source
    return plan

def frame_root(action,index,path,meta):
    if action not in AIR_BUCKLES:
        return list(meta['output_origin']), {'method':'processor_feet_contact_estimate','runtime_verified':False}
    with Image.open(path) as image:
        image=image.convert('RGBA')
        if action=='jump_family' and index in [0,1,6,7]:
            root=estimate_anchor(image,image.getbbox(),'feet')
            return list(root), {'method':'actual_processed_alpha_feet_contact_estimate','runtime_verified':False}
        buckle=AIR_BUCKLES[action][index]
        assert image.getpixel(buckle)[3]>128
    delta=[IDLE_ROOT[0]-IDLE_BUCKLE[0],IDLE_ROOT[1]-IDLE_BUCKLE[1]]
    root=[buckle[0]+delta[0],buckle[1]+delta[1]]
    return root, {'method':'manual_belt_buckle_proxy_plus_idle_buckle_to_ground_offset',
        'belt_buckle_px':list(buckle),'idle_belt_buckle_px':IDLE_BUCKLE,
        'fixed_offset_px':delta,'status':'manual_proxy_candidate_runtime_review_required',
        'rule':'Render frame origin at this virtual ground root; actorZ alone controls global height. Do not add another baked sprite trajectory.',
        'runtime_verified':False}

def main():
    path=ROOT/'import-subset-v002.json'
    assert not path.exists(), 'Frozen manifest cannot be overwritten'
    ledger=audit.read(ROOT/'generation-ledger.json')
    assert ledger['requested_count']==24 and ledger['remaining_total_authorization']==0
    requests={r['request_number']:r for r in ledger['requests']}
    actions=[];families=[];roots=[];all_frames=[]
    for actor,action,folder,request_number,timings in CONFIG:
        directory=ROOT/'processed'/folder
        meta=audit.read(directory/'pipeline-meta.json')
        frames=[]
        for index,label in enumerate(meta['frame_labels']):
            source=directory/(label+'.png')
            frame=audit.pixel_record(source)
            root,root_info=frame_root(action,index,source,meta)
            frame.update(index=index,source_frame_index=index,ground_root_px=root,root_px=root,
                         root_measurement=root_info)
            with Image.open(source) as image:
                frame['corner_rgba']=[list(image.getpixel(point)) for point in [(0,0),(511,0),(0,511),(511,511)]]
            frames.append(frame);all_frames.append(frame)
            if action in AIR_BUCKLES:
                roots.append({'action_family':action,'frame_index':index,'path':str(source),
                              'sha256':frame['sha256'],'root_px':root,'measurement':root_info})
        assert all(not meta[key] for key in ['empty_frames','source_edge_touch_frames','output_edge_touch_frames','paste_clamped_frames'])
        summary=meta['qc_summary']
        standard_pass=summary['body_scale_cv']<=.08 and summary['anchor_y_std']<=.05 and summary.get('profile_body_scale_drift',0)<=.08
        status=requests[request_number]['status']
        if action=='death':
            assert not standard_pass
        elif action not in AIR_BUCKLES:
            assert standard_pass
        source='docs/production/first-batch-v2/combo-spec.md'
        if actor=='stone':source='docs/production/first-batch-v2/example-manifest.json (template timings only)'
        if action=='secondary':source='docs/production/first-batch-v2/example-manifest.json (template timings only)'
        plan=phase_plan(timings,source)
        duration=plan['duration_s'] if plan else round(meta['duration']/1000*len(frames),6)
        entry={'actor':actor,'action':action,'status':status,'folder':str(directory),
            'source_request_number':request_number,'frame_count':len(frames),'frames':frames,
            'sheet_path':str(directory/'sheet-transparent.png'),'sheet_sha256':audit.sha(directory/'sheet-transparent.png'),
            'layout':{'rows':meta['rows'],'columns':meta['cols'],'cell_px':[512,512]},
            'processor_qc':summary,'standard_grounded_metrics_passed':standard_pass,
            'pose_aware_review_required':action in ['death','jump_family','air_primary_1'],
            'containment_alpha_qc_passed':True,'phase_binding_plan':plan,
            'preview_duration_s':duration,'authoritative_duration_s':plan['duration_s'] if plan else None,
            'phases_absolute':plan['phases_absolute'] if plan else [{'name':'visual_preview_only','start_s':0,'end_s':duration}],
            'loop':action in ['idle','walk','dormant'],'runtime_verified':False,
            'layer_scope':'whole_body_baked_clothing' if actor=='hero' else 'whole_body_baked_shield_and_sword',
            'semantics':'candidates only; images neither authorize movement nor define damage/i-frames'}
        if action=='dodge':
            entry['authoritative_duration_s']=.4
            entry['phases_absolute']=[{'name':'dodge_movement','start_s':0,'end_s':.4}]
            entry['separate_iframe_interval']={'start_s':.06,'end_exclusive_s':.2,'source':'docs/design/player-combat-v1/player-combat-rules.json'}
            entry['frame_intervals_absolute']=[{'frame_index':i,'start_s':round(i*.4/6,6),'end_s':round((i+1)*.4/6,6)} for i in range(6)]
        if action=='jump_family':
            families.append(entry)
            for name,indices,selector in [('jump',[0,1,2,3],'takeoff/rise/apex presentation; actorZ from runtime'),
                                          ('fall',[4,5],'descending vertical state; no extra global sprite movement'),
                                          ('land',[6,7],'actual ground contact event then recovery')]:
                mapped=dict(entry);mapped.update(action=name,frames=[frames[i] for i in indices],frame_count=len(indices),
                    source_family='jump_family',source_frame_indices=indices,runtime_state_selector=selector,
                    authoritative_duration_s=None,phase_binding_plan=None,
                    preview_duration_s=round(meta['duration']/1000*len(indices),6),
                    phases_absolute=[{'name':'visual_preview_only','start_s':0,'end_s':round(meta['duration']/1000*len(indices),6)}])
                actions.append(mapped)
        else:
            actions.append(entry)
    hashes={f['sha256'] for f in all_frames}
    assert len(all_frames)==122 and len(hashes)==122 and len(actions)==22
    provenance=[]
    for request in ledger['requests']:
        source=Path(request['source_path'])
        assert audit.sha(source)==request['sha256']
        for key in ['tool_original_path','archive_original_path','presentation_path']:
            assert audit.sha(Path(request[key]))==request['sha256']
        provenance.append({'request_number':request['request_number'],'status':request['status'],
            'raw_path':str(source),'raw_sha256':request['sha256'],'tool_original_path':request['tool_original_path'],
            'prompt_path':request['prompt_path'],'prompt_sha256':audit.sha(Path(request['prompt_path'])),
            'reference_paths':request['reference_paths'],'provider':'host-native image_gen.imagegen',
            'model':'host_default_model_not_exposed','license_class':'host_generated_no_CC0_claim'})
    weapon=audit.read(ROOT/'processed'/'military-sword-component'/'component-landmarks.json')
    payload={'schema':'frozen-runtime-import-subset-v2','version':'v002','frozen':True,
        'status':'122_unique_visual_candidate_frames_not_formal_layered_content_acceptance',
        'frozen_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'generation_calls_used':24,'generation_calls_remaining':0,'generation_stopped':True,
        'external_api_calls':0,'host_cost_usd':None,'raw_generation_outputs':24,
        'raw_action_sheets_accepted_or_pose_candidates':20,'rejected_raw_action_sheets':1,
        'rejected_request_numbers':[14],'actual_unique_animation_png_count':122,
        'logical_state_mapping_count':22,'logical_actor_counts':{'hero':13,'stone':9},
        'actions':actions,'continuous_source_families':families,'components':[weapon],
        'provenance':provenance,'air_root_measurements':roots,
        'assembly_markers_path':str(ROOT/'assembly-markers-v001.json'),
        'assembly_markers_sha256':audit.sha(ROOT/'assembly-markers-v001.json'),
        'mirror_policy':{'canonical_direction':'right','runtime_mirror_once':True,'pre_mirrored_left_frames':False,
            'root_transform':'left root x=512-right root x; mirror every local socket once, do not mirror component twice'},
        'formal_content_atlas_validation_passed':False,'runtime_verified':False,
        'limitations':['122unique frames include death/air posture candidates, not122 fully accepted runtime frames.',
            'Death standard standing area/root statistics failed and are preserved; rigid-part/contact/transition runtime review required.',
            'Jump/fall/land map8unique continuous frames into4/2/2; no duplicate counting or fabricated extra frames.',
            'Air virtual roots use manually reviewed belt-buckle proxy and idle offset; not a measured skeletal bone.',
            'No independent armor/body-near/body-far layers; stone shield remains baked.',
            'Sword angles and hand occlusion are assembly candidates; idle/walk open hands may not grasp naturally.',
            'Minor matte fringe counted per PNG; no zero-fringe claim.',
            'Noncombat phases markedvisual_preview_only are not gameplay windows; GIF timing is not authoritative.',
            'No UE/Blender launch or import in this subtask.']}
    write(path,payload)
    write(ROOT/'air-root-measurements-v001.json',{'status':'manual_proxy_candidates_runtime_pending',
        'reference_idle_buckle_px':IDLE_BUCKLE,'reference_idle_root_px':IDLE_ROOT,'frames':roots})
    index=audit.read(ARCHIVE/'index.json')
    derived={e['source']:e for e in index.get('derived_outputs',[])}
    folders=[ROOT/'processed'/row[2] for row in CONFIG]
    folders += [ROOT/'processed'/'military-sword-component',ROOT/'processed'/'stone-shield-bash']
    files=[p for folder in folders for p in folder.rglob('*') if p.is_file()]
    files += [path,ROOT/'air-root-measurements-v001.json',ROOT/'generation-ledger.json',ROOT/'stone-scale-profile.json']
    files += list((ROOT/'prompts').glob('*.txt'))
    for source in files:
        relative=source.relative_to(ROOT)
        if source.name=='generation-ledger.json':relative=Path('snapshots')/'generation-ledger-after24.json'
        original,presentation=ARCHIVE/'原件'/relative,ARCHIVE/'展示副本'/relative
        audit.copy_no_overwrite(source,original);audit.copy_no_overwrite(source,presentation)
        derived[str(source)]={'source':str(source),'original':str(original),'presentation':str(presentation),
            'sha256':audit.sha(source),'status':'rejected_source_edge' if 'stone-shield-bash' in source.parts else 'visual_candidate_runtime_pending'}
    index.update(status='24_call_cap_reached_candidates_frozen',generation_calls_used=24,
        generation_calls_remaining_total=0,actual_unique_animation_frames=122,logical_state_mappings=22,
        derived_outputs=list(derived.values()),outputs=ledger['requests'])
    write(ARCHIVE/'index.json',index)
    print(json.dumps({'manifest':str(path),'sha256':audit.sha(path),'unique_frames':122,'logical_states':22,
        'raw_action_sheets':20,'calls_used':24,'calls_remaining':0},ensure_ascii=False))

if __name__=='__main__':
    main()
