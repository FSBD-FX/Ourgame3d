"""D-14 static integration audit. Does not run or implement the game."""
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
errors = []
checks = Counter()
reference_runs = []


def check(ok, group, label):
    checks[group] += 1
    if not ok:
        errors.append(f"{group}: {label}")


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def resolve_path(name):
    if name.startswith('../') or (HERE/name).is_file():
        return (HERE/name).resolve()
    return (ROOT/name).resolve()


def resolve_ref(name, pointer=''):
    name, _, fragment = name.partition('#')
    path = resolve_path(name)
    if not path.is_file():
        raise ValueError(f'missing {name}')
    pointer = pointer or fragment
    if not pointer:
        return read(path) if path.suffix == '.json' else path.read_text(encoding='utf-8-sig')
    value = read(path)
    if not pointer.startswith('/'):
        raise ValueError(f'invalid pointer {pointer}')
    for part in pointer[1:].split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def ids(rows, key='id'):
    return {r[key] for r in rows}


def capability(actor, bases, elites):
    elite = actor['id'] in elites
    base = bases[actor['parent_id']] if elite else actor
    attacks = list(base['attacks'])
    if elite:
        extra = actor.get('extra_attack', actor.get('attack_override'))
        if extra:
            if extra.get('original_attack_retained') is False:
                attacks = [a for a in attacks if a['id'] != extra['replaces_attack_id']]
            attacks.append(extra)
    types = {a['type'] for a in attacks}
    flags = {'large': base['size'] == 'large', 'charger': 'charge' in types, 'flying': base['locomotion'] == 'flying', 'support': 'support' in types, 'projectile_users': 'projectile' in types, 'elites': elite}
    role = max(1 if base['size'] == 'small' else 2, 4 if flags['large'] else 0, 3 if flags['charger'] else 0, 2 if flags['support'] or flags['projectile_users'] else 0)
    return {'cost': role + int(flags['flying']) + 2*int(elite), **flags, 'scanned_attack_ids': [a['id'] for a in attacks]}


def run_reference(script):
    result = subprocess.run([sys.executable, '-X', 'utf8', str(HERE/script), '--check'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    return {'script': script, 'mode': 'check_no_rewrite', 'exit_code': result.returncode, 'output': result.stdout.strip(), 'error': result.stderr.strip()}


def main():
    names = ['integration-rules','encounter-deck','combat-baselines','economy-progression-audit','system-acceptance','integrated-cases','design-index']
    docs = {name: read(HERE/(name+'.json')) for name in names}
    refs = set()
    for name, data in docs.items():
        check(data.get('module') == 'D-14' and data.get('source_event') == 'EV-032' and data.get('design_date') == '2026-10-14', 'metadata', name)
        check(data.get('runtime_implemented') is False and data.get('status') == 'design_only', 'metadata', name+' scope')
        for key, value in data.items():
            if isinstance(value, list) and value and all(isinstance(row, dict) and 'id' in row for row in value):
                check(len(ids(value)) == len(value), 'identity', name+'/'+key)
        for value in walk(data):
            if isinstance(value, dict) and isinstance(value.get('path'), str):
                for key in ['pointer','json_pointer']:
                    if key in value:
                        refs.add((value['path'], value[key] or ''))
                for pointer in value.get('pointers', []):
                    refs.add((value['path'],pointer))
                if 'sha256' in value:
                    path = resolve_path(value['path'])
                    check(path.is_file() and sha(path) == value['sha256'], 'source_hash', value['path'])
            elif isinstance(value, str) and re.fullmatch(r'(?:\.\./|docs/)?[^\s#]+\.json(?:#/[\w/~.\-]+)?', value):
                refs.add((value,''))
    for name, pointer in sorted(refs):
        try:
            resolve_ref(name,pointer)
            check(True,'source_reference',name+'#'+pointer)
        except (ValueError,KeyError,IndexError) as exc:
            check(False,'source_reference',str(exc))

    rules = docs['integration-rules']
    deck = docs['encounter-deck']
    combat = docs['combat-baselines']
    economy = docs['economy-progression-audit']
    acceptance = docs['system-acceptance']
    cases = docs['integrated-cases']
    index = docs['design-index']
    source_enemies = resolve_ref('../enemies-v1/enemies.json')
    bases = {a['id']:a for a in source_enemies['enemies']}
    elites = {a['id']:a for a in source_enemies['elite_variants']}
    source_weapons = resolve_ref('../equipment-v1/weapons.json')
    source_armor = resolve_ref('../equipment-v1/armor.json')
    source_bosses = resolve_ref('../bosses-v1/bosses.json')['bosses']
    routes = resolve_ref('../dungeon-v1/regions-and-routes.json')['regions']
    regions = {r['id']:r for r in routes}
    cap_rule = resolve_ref('../dungeon-v1/common-rules.json')['budget']
    old_profiles = resolve_ref('../dungeon-v1/room-sequences.json')['capability_profiles']
    check(ids(combat['weapons']) == ids(source_weapons) and len(combat['weapons']) == 33, 'catalogue', 'weapons')
    check(ids(combat['armor']) == ids(source_armor) and len(combat['armor']) == 12, 'catalogue', 'armor')
    check(ids(combat['enemy_baselines']) == set(bases) and ids(combat['elite_baselines']) == set(elites), 'catalogue', '28+9')
    check(ids(combat['boss_baselines']) == ids(source_bosses) and len(combat['boss_baselines']) == 7, 'catalogue', 'Bosses')
    check(len(combat['enemy_attack_definitions']) == 65 and len(combat['boss_attack_definitions']) == 27, 'catalogue', 'attack counts')
    check(len(combat['families']) == 11 and set(deck['capability_profiles']) == set(bases)|set(elites), 'catalogue', 'families and all actor capability identities')
    for actor in source_enemies['enemies']+source_enemies['elite_variants']:
        expected = capability(actor,bases,elites)
        actual = deck['capability_profiles'][actor['id']]
        check(all(actual[k] == v for k,v in expected.items()), 'capabilities', actor['id'])
        if actor['id'] in old_profiles:
            check(all(actual[k] == old_profiles[actor['id']][k] for k in ['cost','large','charger','flying','support','projectile_users','elites']), 'capabilities', actor['id']+' historical agreement')
    scaling = {x['region_id']:x for x in rules['chapter_scaling']['rows']}
    check(set(scaling) == set(regions) and rules['difficulty_policy']['no_hidden_player_strength_scaling'], 'chapter', 'five fixed chapters')
    for i,reg in enumerate(routes,1):
        row = scaling[reg['id']]
        check(math.isclose(row['ordinary_and_elite_hp_multiplier'],1+.1*(i-1)) and math.isclose(row['ordinary_and_elite_direct_damage_multiplier'],1+.04*(i-1)) and row['Boss_multiplier'] == 1, 'chapter',reg['id'])
    all_slots = []
    all_groups = []
    expected_nodes = {f'REG-{i:02d}-N{j:02d}' for i in range(1,6) for j in [2,3,5]}
    check(ids(deck['recipes'],'node_id') == expected_nodes and len(deck['recipes']) == 15, 'encounter', '15 ordinary mainline nodes')
    for recipe in deck['recipes']:
        reg = regions[recipe['region_id']]
        node = resolve_ref(recipe['source_route_ref'])
        check(node['id'] == recipe['node_id'] and node['room_role_id'] == recipe['role_id'], 'encounter',recipe['id']+' route')
        check(recipe['overlap_allowed'] is False and recipe['geometry_verified'] is False and recipe['runtime_playtested'] is False, 'encounter',recipe['id']+' acceptance scope')
        earlier = []
        slots = []
        for gi,group in enumerate(recipe['groups']):
            all_groups.append(group['group_id'])
            check(group['dependencies_terminal'] == earlier and group['whole_group_admission'], 'encounter',group['group_id']+' terminal chain')
            if gi:
                t = group['trigger']
                check(t['threshold_fraction'] == (.4 if gi==1 else .7) and t['latch_once'] and t['latch_before_dependencies'] and t['unlatch_on_return'] is False and t['breather_from_latest_required_dependency_terminal_s']==2, 'encounter',group['group_id']+' depth')
            roster = [s['enemy_id'] for s in group['slots']]
            allowed = set(reg['enemy_candidates'])|set(reg['elite_candidates'])
            check(set(roster)<=allowed, 'encounter',group['group_id']+' region pool')
            profiles = [deck['capability_profiles'][eid] for eid in roster]
            usage = {'actors':len(profiles),'threat':sum(p['cost'] for p in profiles)}
            usage.update({k:sum(int(p[k]) for p in profiles) for k in cap_rule['roster_caps']})
            check(usage == group['computed_reserved_cap_usage'], 'encounter',group['group_id']+' totals')
            check(usage['actors']<=cap_rule['actor_cap'] and usage['threat']<=cap_rule['threat_cap'] and all(usage[k]<=cap for k,cap in cap_rule['roster_caps'].items()), 'encounter',group['group_id']+' caps')
            for slot in group['slots']:
                eid = slot['enemy_id']
                base = bases[elites[eid]['parent_id']] if eid in elites else bases[eid]
                hp = base['stats']['hp']*(elites[eid]['stat_multipliers']['hp'] if eid in elites else 1)*scaling[reg['id']]['ordinary_and_elite_hp_multiplier']
                check(math.isclose(hp,slot['scaled_spawn_max_hp_reference'],abs_tol=1e-6), 'chapter',slot['slot_id'])
                slots.append(slot)
            earlier.append(group['group_id'])
        check(len(slots)==recipe['finite_slot_count'], 'encounter',recipe['id']+' finite count')
        if recipe['role_id']=='ROOM-ROLE-TEACH':
            check(len(slots)==1 and len(recipe['groups'])==1, 'encounter',recipe['id']+' minimal teach')
        all_slots.extend(s['slot_id'] for s in slots)
    check(len(all_slots)==len(set(all_slots))==55 and len(all_groups)==len(set(all_groups))==30, 'encounter','55 unique slots /30 groups')
    sums=[]
    for summary in deck['region_summaries']:
        recipes = [r for r in deck['recipes'] if r['region_id']==summary['region_id']]
        hp = sum(s['scaled_spawn_max_hp_reference'] for r in recipes for g in r['groups'] for s in g['slots'])
        sums.append(hp)
        check(math.isclose(hp,summary['sum_scaled_spawn_HP_reference'],abs_tol=1e-6), 'chapter',summary['region_id']+' workload sum')
    check(all(b>a for a,b in zip(sums,sums[1:])), 'chapter','increasing workload, not difficulty certification')
    mainline = [n['id'] for reg in routes for n in reg['nodes'] if n['route_class']=='mainline']
    check([c['node_id'] for c in cases['mainline_checkpoints']]==mainline and len(mainline)==35, 'flow','35 mainline checkpoints')
    recipe_lookup={r['node_id']:r['id'] for r in deck['recipes']}
    for checkpoint in cases['mainline_checkpoints']:
        check(checkpoint['encounter_id']==recipe_lookup.get(checkpoint['node_id']), 'flow',checkpoint['node_id']+' encounter binding')
    check(len(cases['conditional_end_to_end_flows'])==6 and len(cases['future_acceptance'])==22 and all(c['runtime_tested'] is False for c in cases['future_acceptance']), 'flow','conditional cases not executed')
    baseline = economy['baseline']
    check(baseline['start_once_gold']+baseline['ordinary_ground_gold']+baseline['first_four_Boss_ground_gold']==baseline['gross_gold_if_all_picked']==700, 'economy','700 includes start20')
    check(baseline['ordinary_ground_shards_if_picked']+baseline['Boss_direct_shards']==baseline['repeat_shards']==60 and baseline['five_main_Boss_first_extra_if_unclaimed']==10, 'economy','60+first10 conditional')
    for plan in economy['ordered_full_run_plans']:
        balance=0
        init=0
        for event in plan['events']:
            check(event['gold_before']==balance,'economy',plan['id']+' before '+str(event['ordinal']))
            balance += event['gold_delta']
            check(balance==event['gold_after'] and balance>=0,'economy',plan['id']+' after '+str(event['ordinal']))
            if event['kind']=='initialize_once':
                init+=1
        check(init==1 and plan['mainline_nodes_covered']==mainline,'economy',plan['id']+' start and route')
        check(plan['gross_gold_including_start']-plan['spent_gold']==plan['pre_end_gold'] and plan['post_end_gold']==0,'economy',plan['id']+' total and terminal')
    check([row['module'] for row in acceptance['module_coverage']]==[f'D-{i:02d}' for i in range(1,15)],'coverage','14 module coverage')
    for row in acceptance['module_coverage']:
        check((ROOT/row['entry']).is_file() and row['design_document_available'] and row['formal_module_runtime_complete'] is False,'coverage',row['module'])
    slice_data=acceptance['first_production_slice']
    actual_first={s['enemy_id'] for r in deck['recipes'] if r['region_id']=='REG-01' for g in r['groups'] for s in g['slots']}
    check(ids(slice_data['enemies'])==actual_first and len(actual_first)==5,'coverage','slice enemy scope matches entire first region deck')
    check(slice_data['chapter_boundary']['destination']=='REG-02-N01' and slice_data['work_started_this_turn'] is False,'coverage','slice real transition, not completed')
    for group in ['historical_design_sha256','observed_existing_code_and_manifest_sha256']:
        for rel,digest in index[group].items():
            path=ROOT/rel
            check(path.is_file() and sha(path)==digest,'preservation',rel)
    expected_code={rel for rel in index['observed_existing_code_and_manifest_sha256'] if rel.startswith('UnrealGame/Source/')}
    actual_code={p.relative_to(ROOT).as_posix() for p in (ROOT/'UnrealGame/Source').rglob('*') if p.is_file() and p.suffix in {'.cpp','.h','.cs'}}
    check(expected_code==actual_code,'preservation','engine Source inventory')
    for rel in [index['overview']]+index['reading_order']:
        check((HERE/rel).is_file(),'navigation',rel)
    for path in [ROOT/'难度数值与整体设计验收.md']+list(HERE.glob('*.md')):
        for link in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8-sig')):
            if not re.match(r'(?:https?:|#)',link):
                target=link.split('#')[0].strip('<>')
                if target and not target.endswith('validation-report.json'):
                    check((path.parent/target).is_file(),'navigation',path.name+' -> '+link)
    ledger=(ROOT/'项目需求台账.md').read_text(encoding='utf-8-sig')
    check(re.findall(r'^\| EV-(\d{3}) \|',ledger,re.M)==[f'{i:03d}' for i in range(1,33)],'bookkeeping','EV001..032')
    check(re.findall(r'^\| REQ-(\d{3}) \|',ledger,re.M)==[f'{i:03d}' for i in range(1,18)],'bookkeeping','no new invented REQ')
    row=next(l for l in ledger.splitlines() if l.startswith('| EV-032 |'))
    check('“ok”' in row and '不新增独立REQ' in row and '2026-10-14' in row,'bookkeeping','exact user event')
    check('先追加 `EV-033`' in ledger and '下一事件EV-033' in ledger,'bookkeeping','next event')
    for name in ['README.md','AGENTS.md','整体设计清单与推进顺序.md']:
        body=(ROOT/name).read_text(encoding='utf-8-sig')
        check('EV-032' in body and '难度数值与整体设计验收.md' in body and '首批' in body,'bookkeeping',name)
    check('v1.14' in (ROOT/'整体设计清单与推进顺序.md').read_text(encoding='utf-8-sig'),'bookkeeping','roadmap version')
    with ThreadPoolExecutor(max_workers=2) as pool:
        runs=list(pool.map(run_reference,['build_combat_reference.py','build_economy_reference.py']))
    for run in runs:
        reference_runs.append(run)
        check(run['exit_code']==0,'reference_recompute',run['script']+' '+run['error'])
    return docs


if __name__=='__main__':
    docs={}
    try:
        docs=main()
    except Exception as exc:
        errors.append(f'validator_exception: {type(exc).__name__}: {exc}')
    index=docs.get('design-index',read(HERE/'design-index.json'))
    paths=[p for p in HERE.iterdir() if p.suffix in {'.json','.md','.py'} and p.name!='validation-report.json']+[ROOT/'难度数值与整体设计验收.md']
    report={'module':'D-14','design_date':'2026-10-14','source_event':'EV-032','status':'static_reference_integration_checks_passed' if not errors else 'needs_correction','checks':sum(checks.values()),'check_groups':dict(checks),'errors':errors,'runtime_implemented':False,'runtime_tested_this_turn':False,'zero_talent_clear_verified':False,'full_game_balance_accepted':False,'formal_art_style_accepted':False,'all14_initial_drafts_available':not errors,'reference_runs':reference_runs,'future_cross_system_runtime_cases':22,'future_runtime_cases_executed':0,'historical_design_sha256':index['historical_design_sha256'],'observed_existing_code_and_manifest_sha256':index['observed_existing_code_and_manifest_sha256'],'current_design_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)},'limits':['Static IDs/source hashes/pointers/caps/finite dependencies/chapter arithmetic and conditional ledgers only.','Reference calculators use idealized explicit assumptions; they are not game AI, full-run simulations, measured damage taken, difficulty or completion time.','Actual collision/navigation/visibility/action ordering/healing opportunities/exact saves/frame times and playability require staged runtime tests.','14 initial draft documents being available does not imply individual user approval or production/release acceptance.']}
    (HERE/'validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['status','checks','check_groups','errors']},ensure_ascii=False))
    sys.exit(1 if errors else 0)
