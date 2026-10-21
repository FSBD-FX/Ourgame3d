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
