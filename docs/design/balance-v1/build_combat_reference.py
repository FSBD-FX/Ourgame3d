"""D-14 offline design arithmetic only. No engine/gameplay code, randomness or source edits."""
from __future__ import annotations
import argparse,hashlib,json,math
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
SOURCES=['equipment-v1/weapons.json','equipment-v1/armor.json','equipment-v2/stat-definitions.json','equipment-v2/enchant-rules.json','player-combat-v1/player-combat-rules.json','items-v1/common-rules.json','items-v1/states.json','enemies-v1/enemies.json','enemies-v1/common-rules.json','enemies-v1/target-profiles.json','enemies-v1/enemy-projectile-profiles.json','bosses-v1/bosses.json','bosses-v1/common-rules.json','bosses-v1/arena-contracts.json','dungeon-v1/room-sequences.json','dungeon-v1/common-rules.json']
src={p:json.loads((ROOT/'docs/design'/p).read_text(encoding='utf-8')) for p in SOURCES}
def ref(path,pointer=''):
    return {'path':'docs/design/'+path,'pointer':pointer,'access':'read_only'}
def q(v):return F(str(v))
def n(v):return round(float(v),9)
def ratio(v):return {'numerator':v.numerator,'denominator':v.denominator,'decimal':n(v)}
def reduction(a):return min(F(3,5),q(a)/(100+q(a)))
W=src['equipment-v1/weapons.json'];A=src['equipment-v1/armor.json'];E=src['enemies-v1/enemies.json'];B=src['bosses-v1/bosses.json']['bosses'];ARENA=src['bosses-v1/arena-contracts.json']['arenas']
# Explicit first-target primary subevents from immutable v1 prose, never parsed as a pellet multiplier twice.
SEG={
'KNF-001':[(.08,12)],'KNF-002':[(.10,10),(.22,10)],'KNF-003':[(.11,14)],
'DAO-001':[(.27,34)],'DAO-002':[(.19,26)],'DAO-003':[(.38,42)],
'SWD-001':[(.17,26)],'SWD-002':[(.12,23)],'SWD-003':[(.20,18),(.34,12)],
'GSW-001':[(.45,46)],'GSW-002':[(.34,40)],'GSW-003':[(.31,24),(.51,24)],
'SPR-001':[(.11,21)],'SPR-002':[(.17,28)],'SPR-003':[(.14,25)],
'HAL-001':[(.23,20),(.43,16)],'HAL-002':[(.26,32)],'HAL-003':[(.18,28)],
'XBW-001':[(.16,34)],'XBW-002':[(.09,18)],'XBW-003':[(.38,52)],
'PST-001':[(.09,23)],'PST-002':[(.12,14),(.18,14)],'PST-003':[(.27,36)],
'SGN-001':[(.17,42)],'SGN-002':[(.30,36)],'SGN-003':[(.12,40)],
'RFL-001':[(.28,43)],'RFL-002':[(.18,13),(.26,13),(.34,13)],'RFL-003':[(.14,24)],
'STF-001':[(.22,24)],'STF-002':[(.18,11),(.28,11)],'STF-003':[(.12,20)]}
NOTES={
'KNF-003':'Only this primary applies 0.75*target armor before the same armor reduction formula; no persistent debuff or ward change.',
'DAO-003':'42 outer x120..170 or 28 inner x0..<120, after exact half-ellipse; alternative zones never sum.',
'SPR-002':'28 first target;16.8 second once. Do not multiply stored16.8 by0.6 again; no third target.',
'HAL-001':'20 thrust rectangle55..215,Y20 nearest target then16 sweep half-ellipse55..175,Y60; envelope215/Y60 does not permit both everywhere.',
'XBW-003':'52 first target;31.2 second once. No third target and wall stops; stored52 is not83.2 single-target.',
'SGN-001':'6 rays*7 already totals42 near full-hit; aggregate by target once, range falloff and precise ray/hurtbox reduce actual total.',
'SGN-002':'4 rays*9 already totals36 near full-hit; aggregate by target once; no physical pellet actors.',
'SGN-003':'8 rays*5 already totals40 near full-hit; aggregate by target once; no physical pellet actors.',
'STF-001':'24 magic direct; no implicit burn.', 'STF-002':'11+11 magic direct;10 focus total,5 each actual emission; no implicit slow; D02/D03 actual muzzle lines supersede legacy same-Y text.',
'STF-003':'20 magic direct instantaneous ray;0 projectile speed is not a stationary projectile; no implicit shock.'}
family_text={
'KNF':('小刀','低承诺/短窄接近，双刺与局部穿甲分支','短触及不能用DPS抵消接近风险'),
'DAO':('大刀','宽前半椭圆清面，刃端与刀根互斥','外包络角点不能当必中；003内区只有28'),
'SWD':('单手剑','标准斜斩/窄线刺/两次返斩','002最近一体，003两子段不增加第二次元素机会'),
'GSW':('重剑','较长承诺与高削韧，长距空区/双砸','削韧不等硬直，保护期会拒绝后续累积'),
'SPR':('长枪','低前摇窄刺/更远两体穿刺/撩刺','贴身空区与对线代价，不许自动吸附'),
'HAL':('戟','分形状刺扫/钩斩/近身月刃','001两形状交集才有36，不能用215×60通判'),
'XBW':('弩','短匣重发/三仓轻发/双目标重穿','一次动作速率远高于含上弦持续速率'),
'PST':('手枪','六仓慢移射/一次双响/窄稳腕单发','双响28已含2弹，总耗2不能缺1免费放'),
'SGN':('霰弹枪','近距固定射线束与强弱不同衰减','每枪先按目标聚合，实际丸数依体型/距离/阻挡'),
'RFL':('步枪','长距拉栓/一按三连/五仓轻枪','拉栓后摇不能切枪跳；三连39已含3弹'),
'STF':('法杖','慢火球/两冰片/瞬时电线的魔法直伤','专注共角色，不给普攻隐含状态；射弹时间另计')}
res={'schema_version':'1.0','design_date':'2026-10-14','timezone':'Asia/Shanghai','module':'D-14','source_event':'EV-032','status':'design_only','runtime_implemented':False,'authority':'assistant_proposal_not_individually_user_approved','calculation_scope':'offline_design_reference_arithmetic_only_not_gameplay_implementation','calculator_ref':'build_combat_reference.py','source_freeze':[],'assumptions':{'model':'zero_talent_grade0_no_enchant_no_relic_no_item_no_conditional_armor_effect; base_action_speed and reload unless explicitly stress-marked','primary_reference':'one legal stationary first target; all declared primary subevents or near shotgun rays hit; fresh press at every legal start; no interruptions','excluded':['real_hit_rate','approach_reposition_or_escape_time','enemy_AI_and_attack_downtime','walls_allied_body_blocks_and_camera','player_damage_or_hurt_or_death','crit_unless_expectation_only','affixes_and_Boss_control_timing','weapon_skills_and_DoT','chapter_scale_unless_root_authority_example'],'ttk_limit':'dummy lethal-hit arithmetic is not measured Boss TTK, expected playtime, fairness certification or zero-talent clear proof'},'player':{'baseline':src['player-combat-v1/player-combat-rules.json']['baseline'],'caps':src['items-v1/common-rules.json']['stat_merge']['caps'],'source_refs':[ref('player-combat-v1/player-combat-rules.json','/baseline'),ref('items-v1/common-rules.json','/stat_merge/caps')]},'formulas':{'primary_nominal_rate':'D_first_target_complete_primary / (windup+active+recovery), before defense and resource-rest downtime','magazine':'N=floor(magazine/ammo_per_trigger); group_damage=N*D; group_time=N*cycle+reload; sustained_rate=group_damage/group_time; incomplete residue is not a free partial trigger','defense':'reduction=min(0.60,a/(100+a)); received=legal_base*(1-reduction)*(1+vulnerability/100), float internal, no per-pellet ceiling','piercing':'KNF003 only effective_armor=0.75*target_armor for its primary; second-target0.6 only once for SPR002/XBW003','crit':'one draw per AttackID shared all subhits/targets; expected multiplier1+p*(m-1); baseline1.025, caps1.2, expectation not an independent roll per pellet','action_speed':'time=base_time/(1+clamp(action_speed_pct,-20,20)/100); primary/subwindow lower bound0.02s remains; timeline freezes at accepted start','reload_speed':'reload=base_reload/(1+clamp(reload_speed_pct,-25,25)/100), does not shorten primary recovery','focus':'actual emissions spend; whole trigger must be affordable at start/40% lock; regen after last actual spend delay, no switch refill','geometry':'center hard bounds then exact per-segment shape/height/LOS; projectiles swept versus independent hurtbox; shotgun capsule ray versus hurtbox, one aggregate per target per gun','source_refs':[ref('equipment-v2/stat-definitions.json'),ref('equipment-v2/enchant-rules.json','/effect_resolution'),ref('items-v1/common-rules.json','/weapon_timing_extension'),ref('enemies-v1/common-rules.json','/projectile')]},'families':[],'weapons':[],'armor':[],'enemy_baselines':[],'elite_baselines':[],'enemy_attack_definitions':[],'boss_baselines':[],'boss_attack_definitions':[],'boss_escape_probes':[],'shotgun_geometry_examples':[],'focus_examples':[],'findings':[],'future_acceptance':[]}
for p in SOURCES+['equipment-v1/00-共同规则.md']:
    raw=(ROOT/'docs/design'/p).read_bytes();res['source_freeze'].append({'path':'docs/design/'+p,'sha256':hashlib.sha256(raw).hexdigest(),'access':'read_only'})
for family,(name,diff,risk) in family_text.items():
    ids=[w['id'] for w in W if w['family']==family]
    res['families'].append({'id':family,'name':name,'weapon_ids':ids,'difference':diff,'boundary':risk,'source_refs':[ref('equipment-v1/weapons.json','/'+str(i)) for i,w in enumerate(W) if w['family']==family]})
for i,w in enumerate(W):
    seg=SEG[w['id'][4:]];cycle=q(w['cycle_s']);total=q(w['damage_total']);assert sum(q(d) for _,d in seg)==total
    assert cycle==q(w['windup_s'])+q(w['active_s'])+q(w['recovery_s'])
    assert all(q(w['windup_s'])<=q(t)<=q(w['windup_s'])+q(w['active_s']) for t,d in seg)
    assert q(w['active_s'])/F(6,5)>=F(1,50)
    record={k:w[k] for k in ['id','name','family','damage_total','damage_expression','windup_s','active_s','recovery_s','cycle_s','range_cm','min_range_cm','depth_halfwidth_cm','move_multiplier','stagger_total','magazine','reload_s','ammo_per_trigger','focus_cost','projectile_speed_cm_s','primary_pattern']}
    record.update({'primary_sub_events':[{'at_action_s':t,'first_target_nominal_damage':d,'semantics':'shot_aggregate_not_single_pellet' if w['family']=='SGN' else 'one_declared_sub_event'} for t,d in seg],'nominal_primary_rate_before_defense':ratio(total/cycle),'timing_at_action_speed_minus20':ratio(cycle/F(4,5)),'timing_at_action_speed_plus20':ratio(cycle/F(6,5)),'source_refs':[ref('equipment-v1/weapons.json','/'+str(i)),ref('player-combat-v1/player-combat-rules.json','/attack'),ref('items-v1/common-rules.json','/weapon_timing_extension')]})
    if w['magazine']:
        cnt=w['magazine']//w['ammo_per_trigger'];dt=cnt*cycle+q(w['reload_s']);record['magazine_reference']={'full_triggers':cnt,'leftover_ammo':w['magazine']%w['ammo_per_trigger'],'complete_trigger_damage':n(cnt*total),'group_time_s':ratio(dt),'sustained_no_defense_rate':ratio(cnt*total/dt)}
    else:record['magazine_reference']=None
    record['special_boundary']=NOTES.get(w['id'][4:],'No implicit extra subhit/target/element beyond source primary_pattern; all nominal comparisons require exact shape and legal height.')
    record['secondary_reference']={k:w['secondary'][k] for k in ['name','damage_total','windup_s','active_s','recovery_s','cycle_s','cooldown_s','ammo_cost','focus_cost','action'] if k in w['secondary']}
    res['weapons'].append(record)
for i,a in enumerate(A):
    res['armor'].append({**{k:a[k] for k in ['id','name','type','armor','ward','move_multiplier','poise_bonus','focus_regen_per_s','focus_regen_delay_s','trait']},'base_physical_reduction':ratio(reduction(a['armor'])),'base_magic_reduction':ratio(reduction(a['ward'])),'base_poise_threshold':30+a['poise_bonus'],'base_idle_move_cm_s':n(265*q(a['move_multiplier'])),'source_refs':[ref('equipment-v1/armor.json','/'+str(i))]})
# Enemy damage fields are copied with explicit semantics; only per-projectile ROB elite has total14, parallel ELF/TRE retain one-target max1.
def attack_record(a,path,pointer,multiplier=F(1)):
    fields=['id','name','type','windup_s','active_s','recovery_s','cooldown_s','damage','damage_type','stagger','shape','subhits','subhit_rule','same_attack_subhits','max_hits_per_player_per_attack','projectile_count','per_projectile_damage','total_base_damage_if_both_hit','damage_semantics','counter']
    r={k:a[k] for k in fields if k in a};r['direct_damage_multiplier_applied_once']=n(multiplier)
    if a['id']=='ELT-ROB-001-A1':nominal=q(a['total_base_damage_if_both_hit']);sem='explicit7+7=14 before elite; each real subhit checks dodge/dedup'
    elif a.get('subhits') and a.get('max_hits_per_player_per_attack')==1:nominal=q(a['damage']);sem='multiple regions/subevents but explicit whole-AttackID max1; not sum for one player'
    else:nominal=q(a['damage']);sem='outer field as declared; explicit Boss subhits describe this total, never add outer damage again'
    r['one_target_nominal_direct_ceiling_before_mitigation']=n(nominal*multiplier);r['ceiling_semantics']=sem;r['source_refs']=[ref(path,pointer)];return r
for i,e in enumerate(E['enemies']):
    res['enemy_baselines'].append({'id':e['id'],'name':e['name'],'family':e['family'],'stats':e['stats'],'body':e['body'],'attack_ids':[a['id'] for a in e['attacks']],'physical_effective_HP_no_special_rules':ratio(q(e['stats']['hp'])/(1-reduction(e['stats']['armor']))),'magic_effective_HP_no_special_rules':ratio(q(e['stats']['hp'])/(1-reduction(e['stats']['ward']))),'source_refs':[ref('enemies-v1/enemies.json','/enemies/'+str(i))]})
    for j,a in enumerate(e['attacks']):res['enemy_attack_definitions'].append(attack_record(a,'enemies-v1/enemies.json',f'/enemies/{i}/attacks/{j}'))
for i,e in enumerate(E['elite_variants']):
    pi=next(i for i,x in enumerate(E['enemies']) if x['id']==e['parent_id']);parent=E['enemies'][pi];stats=dict(parent['stats']);stats['hp']=n(q(stats['hp'])*q(e['stat_multipliers']['hp']));stats['poise']+=e['poise_bonus']
    attacks=list(parent['attacks']);extra=e.get('extra_attack',e.get('attack_override'));kind='extra_attack' if 'extra_attack' in e else 'attack_override'
    if kind=='attack_override':attacks=[a for a in attacks if a['id']!=extra.get('replaces_attack_id')]
    attacks.append(extra);m=q(e['stat_multipliers']['damage'])
    res['elite_baselines'].append({'id':e['id'],'name':e['name'],'parent_id':e['parent_id'],'base_parent_stats':parent['stats'],'inherited_effective_stats':stats,'direct_damage_multiplier':n(m),'effective_attack_ids':[a['id'] for a in attacks],'effective_attack_direct_ceiling_map':{a['id']:attack_record(a,'enemies-v1/enemies.json','/elite_variants/'+str(i),m)['one_target_nominal_direct_ceiling_before_mitigation'] for a in attacks},'no_Boss_control_profile':True,'behavior_change':e['behavior_change'],'source_refs':[ref('enemies-v1/enemies.json','/elite_variants/'+str(i)),ref('enemies-v1/enemies.json','/enemies/'+str(pi)),ref('enemies-v1/enemies.json','/adapter_contract')]})
    res['enemy_attack_definitions'].append(attack_record(extra,'enemies-v1/enemies.json',f'/elite_variants/{i}/{kind}',m))
slow=max(q(w['cycle_s']) for w in W)/F(4,5)
for i,b in enumerate(B):
    arena=next(x for x in ARENA if x['boss_id']==b['id']);contact=q(b['body']['half_x_cm'])+18;minrec=min(q(a['recovery_s']) for a in b['attacks']);sw=next(w for w in W if w['id']=='WPN-SWD-001');hit=q(sw['damage_total'])*(1-reduction(b['stats']['armor']));triggers=math.ceil(q(b['stats']['hp'])/hit)
    intervals=[{'weapon_id':w['id'],'legal_y0_front_center_x_interval_cm':[n(max(contact,q(w['min_range_cm']))),n(q(w['range_cm'])*(F(1) if w['family']=='SGN' else F(17,20)))],'interval_nonempty':max(contact,q(w['min_range_cm']))<=q(w['range_cm'])*(F(1) if w['family']=='SGN' else F(17,20)),'one_full_primary_fits_if_already_legal_in_range':q(w['cycle_s'])/F(4,5)<=minrec} for w in W]
    br={'id':b['id'],'name':b['name'],'suggested_chapter':b.get('suggested_chapter'),'stats':b['stats'],'body':b['body'],'attack_ids':[a['id'] for a in b['attacks']],'attack_count':len(b['attacks']),'min_recovery_s':n(minrec),'shortest_negative_reach_cm':74.8,'legal_front_contact_distance_cm':n(contact),'shortest_knife_front_margin_cm':n(F(374,5)-contact),'slowest_primary_cycle_minus20_s':n(slow),'prepositioned_full_action_slack_s':n(minrec-slow),'max_additional_approach_distance_at_stress_speed_if_other_costs_zero_cm':n((minrec-slow)*F(2067,16)),'weapon_feasibility_intervals':intervals,'physical_effective_HP_no_special_rules':ratio(q(b['stats']['hp'])/(1-reduction(b['stats']['armor']))),'magic_effective_HP_no_special_rules':ratio(q(b['stats']['hp'])/(1-reduction(b['stats']['ward']))),'stationary_dummy_SWD001_no_crit_reference':{'damage_per_legal_hit':ratio(hit),'minimum_complete_primaries':triggers,'lethal_event_time_from_first_start_s':ratio(q(sw['windup_s'])+(triggers-1)*q(sw['cycle_s'])),'full_action_slot_time_s':ratio(triggers*q(sw['cycle_s'])),'not_actual_Boss_TTK':True},'limitations':['already_legal_position_only','no_blocking_or_residual_projectile_union','no_damage_taken_or_poise_break','not_all_recovery_time_is_safe_approach_time','no_weapon_skill_fit_claim','melee_y0_interval_does_not_prove_general_pathfinding_or_camera'],'source_refs':[ref('bosses-v1/bosses.json','/bosses/'+str(i)),ref('bosses-v1/arena-contracts.json','/arenas/'+str(i)),ref('bosses-v1/common-rules.json','/attack'),ref('equipment-v1/weapons.json','/9')]}
    res['boss_baselines'].append(br)
    for j,a in enumerate(b['attacks']):res['boss_attack_definitions'].append(attack_record(a,'bosses-v1/bosses.json',f'/bosses/{i}/attacks/{j}'))
    for j,a in enumerate(arena['attacks']):
        p=a['open_ground_centerline_walk_probe'];distance=(q(p['first_hit_minus_lock_s'])-q(p['reaction_s']))*q(p['stress_speed_cm_s']);margin=distance-q(p['needed_y_cm'])-q(p['extra_margin_cm']);res['boss_escape_probes'].append({'boss_id':b['id'],'attack_id':a['attack_id'],'source_probe':p,'recomputed_walk_cm':ratio(distance),'strict_margin_after_1cm_cm':ratio(margin),'strict_open_ground_probe_positive':margin>0,'engine_navigation_camera_or_attack_union_verified':False,'source_refs':[ref('bosses-v1/arena-contracts.json',f'/arenas/{i}/attacks/{j}/open_ground_centerline_walk_probe')]})
# Deterministic 2D capsule/axis-aligned rectangle query for isolated legal grounded target.
def point_segment_d2(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy;t=0 if den==0 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den));return (p[0]-a[0]-t*dx)**2+(p[1]-a[1]-t*dy)**2

def segment_rect_d2(a,b,x0,x1,y0,y1):
    # Liang-Barsky exact line/box intersection, then endpoint-to-segment minima on all box edges.
    low,high=0.,1.;dx,dy=b[0]-a[0],b[1]-a[1]
    for p,z in [(-dx,a[0]-x0),(dx,x1-a[0]),(-dy,a[1]-y0),(dy,y1-a[1])]:
        if p==0:
            if z<0:low,high=1.,0.;break
        else:
            t=z/p
            if p<0:low=max(low,t)
            else:high=min(high,t)
    if low<=high:return 0.
    corners=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)];vals=[]
    for j,c in enumerate(corners):
        d=corners[(j+1)%4];vals += [point_segment_d2(a,c,d),point_segment_d2(b,c,d),point_segment_d2(c,a,b),point_segment_d2(d,a,b)]
    return min(vals)
SGN={'WPN-SGN-001':(230,[-59,-35.4,-11.8,11.8,35.4,59],6,7,100,F(65,100)),'WPN-SGN-002':(350,[-25,-8.333,8.333,25],5,9,140,F(1,2)),'WPN-SGN-003':(200,[-84,-60,-36,-12,12,36,60,84],6,5,70,F(4,5))}
for wid,(reach,offsets,radius,pellet,near,falloff) in SGN.items():
    w=next(x for x in W if x['id']==wid);wi=W.index(w)
    for d,y,hx,hy,label in [(50,0,18,16,'standard_near'),(near,0,18,16,'standard_full_damage_boundary'),(reach,0,18,16,'standard_max_range'),(reach+1,0,18,16,'center_beyond_range'),(reach,w['depth_halfwidth_cm']+1,18,16,'center_beyond_depth'),(reach,0,56,36,'wide_Boss_size_reference')]:
        hard=0<=d<=reach and abs(y)<=w['depth_halfwidth_cm'];hits=[j for j,off in enumerate(offsets) if hard and segment_rect_d2((0.,0.),(float(reach),float(off)),d-hx,d+hx,y-hy,y+hy)<=radius*radius];factor=F(1) if d<=near else max(F(0),F(1)-falloff*(q(d)-near)/(reach-near));damage=q(len(hits)*pellet)*factor if hard else F(0)
        res['shotgun_geometry_examples'].append({'id':wid+'-'+label,'weapon_id':wid,'scenario':label,'target_center_xy_cm':[d,y],'hurtbox_half_xy_cm':[hx,hy],'ray_query_radius_cm':radius,'max_range_ray_offsets_y_cm':offsets,'center_hard_bounds_pass':hard,'intersecting_ray_indices':hits,'pellet_count':len(hits),'distance_factor':ratio(factor),'aggregate_direct_before_defense':ratio(damage),'one_hurt_and_shared_AttackID_budget':True,'assumptions':'grounded_same_actual_height_no_wall_no_intervening_body_muzzle_origin0; isolated geometry reference_not_engine_proof','source_refs':[ref('equipment-v1/weapons.json','/'+str(wi)),ref('enemies-v1/target-profiles.json','/player_reference')]})
for wid in ['WPN-STF-001','WPN-STF-002','WPN-STF-003']:
    w=next(x for x in W if x['id']==wid);wi=W.index(w);cost=q(w['focus_cost']);cnt=int(F(100)/cost);remaining=F(100)-cnt*cost;segments=SEG[wid[4:]];last=(cnt-1)*q(w['cycle_s'])+q(segments[-1][0]);fulltime=max(cnt*q(w['cycle_s']),last+1+(100-remaining)/12);gap=q(w['cycle_s'])+q(segments[0][0])-q(segments[-1][0]);rob2regen=max(F(0),gap-F(45,100))*12
    res['focus_examples'].append({'weapon_id':wid,'base_no_regen_continuous_trigger_count':cnt,'focus_after_burst':n(remaining),'last_actual_spend_s':ratio(last),'burst_complete_action_s':ratio(cnt*q(w['cycle_s'])),'full_refill_and_next_full_burst_start_s':ratio(fulltime),'specific_burst_then_full_refill_nominal_rate':ratio(cnt*q(w['damage_total'])/fulltime),'not_optimal_sustained_strategy':True,'source_default_actual_spend_gap_s':ratio(gap),'baseline_delay1_blocks_regen_during_unbroken_train':gap<=1,'ROB002_per_trigger_partial_regen_during_accepted_unbroken_train':ratio(rob2regen),'ROB002_net_focus_drain_per_trigger_after_first':ratio(cost-rob2regen),'ROB002_still_depletes':cost>rob2regen,'limitations':'ROB002 amortized actual-spend calculation excludes start/lock rejection boundary and does not promise how many full triggers are accepted; other armor and conditional20/s require separate current conditions','source_refs':[ref('equipment-v1/weapons.json','/'+str(wi)),ref('equipment-v1/armor.json','/10'),ref('player-combat-v1/player-combat-rules.json','/baseline'),ref('items-v1/common-rules.json','/weapon_timing_extension')]})
res['findings']=[{'id':'CB-F01','kind':'model_boundary','finding':'Unreloaded action nominal rate is not ranged sustained throughput; magazine rate includes every full primary and one full reload.','source_refs':[ref('equipment-v1/weapons.json','/18'),ref('equipment-v1/weapons.json','/20')]},{'id':'CB-F02','kind':'material_runtime_risk','finding':'Mechanical Boss negative-reach shortest knife y0 front interval has only0.8cm paper margin; numeric positivity is not a navigation/collision tolerance acceptance.','minimum_change_if_runtime_fails':'first verify common collision/center/hurtbox/coordinate contract; if geometry is correct but unavoidable failure remains, root may propose a small Boss body or shortest reach revision and re-run all gates; do not silently expand hitboxes.','source_refs':[ref('bosses-v1/arena-contracts.json','/arenas/3'),ref('equipment-v2/stat-definitions.json','/3')]},{'id':'CB-F03','kind':'model_boundary','finding':'All33 base primaries at-20% action speed can fit the7 minimum Boss recoveries only if already legal in-range, sufficient whole-trigger resources and no interruptions. No complete approach/attack/escape proof.','source_refs':[ref('bosses-v1/common-rules.json','/attack'),ref('equipment-v1/weapons.json','/9')]},{'id':'CB-F04','kind':'semantic_trap','finding':'ELT-ELF two arrows and ELT-TRE two areas are whole-AttackID max1 per player:12*1.15=13.8; ELT-ROB explicit7+7=14 then*1.15=16.1. Boss40/44 totals already include declared subhits.','source_refs':[ref('enemies-v1/enemies.json','/elite_variants/1/attack_override'),ref('enemies-v1/enemies.json','/elite_variants/2/extra_attack'),ref('enemies-v1/enemies.json','/elite_variants/3/attack_override'),ref('bosses-v1/bosses.json','/bosses/2/attacks/2')]},{'id':'CB-F05','kind':'model_boundary','finding':'Zero-talent clear remains an unverified playtest target; positive damage, recovery fit and free route arithmetic are necessary but insufficient.','source_refs':[ref('dungeon-v1/common-rules.json','/generation'),ref('bosses-v1/common-rules.json','/arena_proposal')]},{'id':'CB-F06','kind':'no_proven_contradiction_found','finding':'This scoped arithmetic found no cycle sum mismatch, empty frontal reach interval for tested7Boss×33weapon stress case, negative escape probe margin or Boss recovery below1.8s. No engine reachability, collision or fairness claim.','source_refs':[ref('bosses-v1/arena-contracts.json','/arenas'),ref('equipment-v1/weapons.json')]}]
for i,(title,expect) in enumerate([('11家族三把逐件运行','验证各源主攻子窗口、空区/内外沿/最近目标，不能用通用矩形代替'),('霰弹聚合与距离','逐丸与hurtbox相交/硬界/衰减，按同枪同目标只做一次受击并保共享预算'),('子段与暴击','同AttackID只一次crit，合法未来子段可命中且每段检查闪避，元素只有一次机会'),('装填完整周期','从满匣持续发射到再装填完成；长按不自动连射、切换不能跳后摇或免费补弹'),('法杖专注边界','前摇接受/40%锁点整轮资源重验；实际发射逐发花费，读最后实际花费延迟'),('普通精英继承','HP1.35和直接伤1.15仅一次；替换招不同时保被替换原招，状态不放大'),('Boss7×11反击','每Boss每家族至少零天赋+0装备实机可利用窗口；含接近/攻击/脱离而非仅周期'),('最短刀与长枪空区','所有Boss四边/角、前后/body接触与最短-15%刀；长武器不能让死区误伤'),('石蝠低位','每次攻击/失手/打断后实际合法Z20至少1.8s，不从空中早计时'),('同点全量伤害与死亡','多段/旧弹/DoT/死亡先于治疗及成功，不以治疗预算复活'),('整房攻击联合','D07各有限组重叠、残弹与当前招并集、角色帽和可走地面，非单招逃逸认证'),('章趋势与零成长','按root章系数冻结同manifest后测零/部分/完整成长及供应；Boss不二乘')],1):
    res['future_acceptance'].append({'id':f'CB-CASE-{i:02}','title':title,'expected':expect,'status':'future_not_run'})
# New D14 chapter authority is referenced, never duplicated as an independent rule.
integration_path=OUT/'integration-rules.json'
integration=json.loads(integration_path.read_text(encoding='utf-8'))
rows=integration['chapter_scaling']['rows']
res['chapter_scaling_authority']={'source_refs':[ref('balance-v1/integration-rules.json','/chapter_scaling/rows'),ref('balance-v1/integration-rules.json','/chapter_scaling/formula')],'module_dependency_digest':hashlib.sha256(integration_path.read_bytes()).hexdigest(),'rules':integration['chapter_scaling'],'old_baseline_numbers_above_remain_unscaled':True}
parent=next(e for e in E['enemies'] if e['id']=='ENM-BST-002');elite=next(e for e in E['elite_variants'] if e['id']=='ELT-BST-001');attack=parent['attacks'][0]
res['chapter_scaling_examples']=[]
for row in rows:
    hm=q(row['ordinary_and_elite_hp_multiplier']);dm=q(row['ordinary_and_elite_direct_damage_multiplier'])
    res['chapter_scaling_examples'].append({'region_id':row['region_id'],'chapter':row['chapter'],'example_only_not_spawn_placement_claim':True,'ordinary_id':parent['id'],'elite_id':elite['id'],'parent_attack_id':attack['id'],'base_HP':parent['stats']['hp'],'original_elite_HP_multiplier':elite['stat_multipliers']['hp'],'chapter_HP_multiplier':n(hm),'ordinary_spawn_HP':n(q(parent['stats']['hp'])*hm),'elite_spawn_HP':n(q(parent['stats']['hp'])*q(elite['stat_multipliers']['hp'])*hm),'base_direct_damage':attack['damage'],'original_elite_direct_multiplier':elite['stat_multipliers']['damage'],'chapter_direct_multiplier':n(dm),'ordinary_direct_before_defense':n(q(attack['damage'])*dm),'elite_direct_before_defense':n(q(attack['damage'])*q(elite['stat_multipliers']['damage'])*dm),'Boss_uses_authored_stats_no_extra_chapter_multiplier':True,'source_refs':[ref('balance-v1/integration-rules.json','/chapter_scaling/rows/'+str(row['chapter']-1)),ref('enemies-v1/enemies.json','/enemies/23'),ref('enemies-v1/enemies.json','/elite_variants/7')]})
res['findings'].append({'id':'CB-F07','kind':'new_D14_chapter_scope','finding':'Source proposed base ranges are not final chapter caps:190HP ordinary becomes266 atREG5, its1.35elite359.1. Defense/poise/timing do not scale; Boss650..1800 authored stats are not multiplied again. Additional durability and supply risk require measured zero-growth playtests.','source_refs':[ref('balance-v1/integration-rules.json','/chapter_scaling'),ref('enemies-v1/enemies.json','/enemies/23'),ref('enemies-v1/enemies.json','/elite_variants/7')]})

# Internal reproducibility gates, not engine tests.
assert len(W)==33 and len(res['families'])==11 and len(res['enemy_baselines'])==28 and len(res['elite_baselines'])==9 and len(B)==7
assert len(res['enemy_attack_definitions'])==65 and len(res['boss_attack_definitions'])==27 and len(res['boss_escape_probes'])==27
assert all(x['strict_open_ground_probe_positive'] for x in res['boss_escape_probes'])
assert all(x['interval_nonempty'] and x['one_full_primary_fits_if_already_legal_in_range'] for b in res['boss_baselines'] for x in b['weapon_feasibility_intervals'])
assert min(b['min_recovery_s'] for b in res['boss_baselines'])>=1.8
res['static_arithmetic_result']={'passed':True,'runtime_passed':False,'source_file_count':len(res['source_freeze']),'weapon_cycle_and_segment_sums_checked':33,'enemy_definition_count':65,'Boss_definition_count':27,'Boss_weapon_y0_interval_checks':231,'positive_open_ground_escape_probes':27}
OUT.mkdir(parents=True,exist_ok=True)
parser=argparse.ArgumentParser()
parser.add_argument('--check',action='store_true')
args=parser.parse_args()
encoded=json.dumps(res,ensure_ascii=False,indent=2)+'\n'
if args.check:
    assert (OUT/'combat-baselines.json').read_text(encoding='utf-8')==encoded, 'combat reference differs from source arithmetic'
else:
    (OUT/'combat-baselines.json').write_text(encoded,encoding='utf-8')
print(json.dumps(res['static_arithmetic_result'],ensure_ascii=False))
