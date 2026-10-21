"""Freeze equipment source values and an independent golden eligibility fixture.

Only writes the two marked blocks in this task's header/test. Never runs the design
catalogue builder (which writes source JSON), UE, generation APIs or global config.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / 'docs/design'
CODE = ROOT / 'UnrealGame/Source/CodexDungeon'
STATS = ['damage_pct', 'action_speed_pct', 'stagger_pct', 'reach_pct',
         'crit_chance_pct', 'crit_damage_bonus_pct', 'skill_cooldown_pct',
         'reload_speed_pct', 'focus_cost_pct', 'lifesteal_pct', 'armor_flat',
         'ward_flat', 'poise_flat', 'max_health_pct', 'move_speed_pct',
         'focus_regen_pct', 'healing_received_pct', 'physical_vulnerability_pct',
         'magic_vulnerability_pct', 'burn_dps', 'slow_pct', 'shock_flat']
ENUMS = ['DamagePct', 'ActionSpeedPct', 'StaggerPct', 'ReachPct', 'CritChancePct',
         'CritDamageBonusPct', 'SkillCooldownPct', 'ReloadSpeedPct', 'FocusCostPct',
         'LifestealPct', 'ArmorFlat', 'WardFlat', 'PoiseFlat', 'MaxHealthPct',
         'MoveSpeedPct', 'FocusRegenPct', 'HealingReceivedPct',
         'PhysicalVulnerabilityPct', 'MagicVulnerabilityPct', 'BurnDps', 'SlowPct', 'ShockFlat']
FAMILIES = ['KNF', 'DAO', 'SWD', 'GSW', 'SPR', 'HAL', 'XBW', 'PST', 'SGN', 'RFL', 'STF']
SOURCES = ['equipment-v2/00-属性附魔共同规则.md', 'equipment-v2/01-属性体系与计算.md',
           'equipment-v2/04-逐件附魔适配与示例.md', 'equipment-v2/stat-definitions.json',
           'equipment-v2/affixes.json', 'equipment-v2/equipment-profiles.json',
           'equipment-v2/enchant-rules.json', 'equipment-v1/weapons.json',
           'equipment-v1/armor.json', 'items-v1/common-rules.json',
           'economy-v1/equipment-growth.json', 'progression-v1/talents.json']


def read(name):
    return json.loads((DESIGN / name).read_text(encoding='utf-8-sig'))


def num(value):
    return format(float(value), '.15g')


def replace_block(path, marker, content, check):
    old = path.read_text(encoding='utf-8')
    begin, end = f'// BEGIN {marker}', f'// END {marker}'
    assert old.count(begin) == old.count(end) == 1, path
    prefix, rest = old.split(begin)
    _, suffix = rest.split(end)
    new = prefix + begin + '\n' + content + '\n' + end + suffix
    if new != old:
        if check:
            raise SystemExit(f'STALE_FROZEN_BLOCK: {path}')
        path.write_text(new, encoding='utf-8', newline='\n')


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--check', action='store_true')
    opt = args.parse_args()
    profile_document = read('equipment-v2/equipment-profiles.json')
    profiles = profile_document['items']
    stats = read('equipment-v2/stat-definitions.json')
    affixes = read('equipment-v2/affixes.json')
    talents = read('progression-v1/talents.json')['nodes']
    growth = read('economy-v1/equipment-growth.json')
    assert len(profiles) == 45 and len(affixes) == 36 and len(talents) == 9
    originals = {}
    for name in ['weapons', 'armor']:
        path = DESIGN/f'equipment-v1/{name}.json'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == profile_document['source_catalogue_sha256'][f'{name}.json']
        originals.update({i['id']: i for i in read(f'equipment-v1/{name}.json')})
    assert all(p['base_definition'] == originals[p['id']] for p in profiles)
    # These three conditional replacement bases exist in source prose, not JSON scalar fields.
    # Fail instead of quietly retaining a mapped number if that source wording changes.
    for template_id, token in [('ARM-LGT-002', '1.12'), ('ARM-LGT-003', '1.14'), ('ARM-ROB-003', '20/s')]:
        assert token in originals[template_id]['trait'], template_id
    assert [x['id'] for x in stats] == STATS
    assert [x['id'] for x in talents] == ['TAL-'+n for n in ['VIT', 'GRD', 'MED', 'ATK', 'BRK', 'CRT', 'MOV', 'FOC', 'RLD']]
    rows = ['// Generated only from the frozen design sources; do not edit this block by hand.',
            'inline constexpr std::array<FSource,12> Sources={{']
    for source in SOURCES:
        digest = hashlib.sha256((DESIGN/source).read_bytes()).hexdigest()
        rows.append(f' {{"docs/design/{source}","{digest}"}},')
    rows += ['}};', 'inline constexpr std::array<FTemplate,45> Templates={{']
    for p in profiles:
        b = p['base_definition']; s = b.get('secondary', {})
        values = [b.get('armor', 0), b.get('ward', 0), b.get('poise_bonus', 0),
                  b.get('move_multiplier', 1) if p['kind'] == 'armor' else 1,
                  b.get('focus_regen_per_s', 12), b.get('focus_regen_delay_s', 1),
                  {'ARM-LGT-002': 1.12, 'ARM-LGT-003': 1.14}.get(p['id'], 0),
                  20 if p['id'] == 'ARM-ROB-003' else 0,
                  b.get('damage_total', 0), b.get('stagger_total', 0), b.get('min_range_cm', 0),
                  b.get('range_cm', 0), b.get('focus_cost', 0), s.get('min_range_cm', 0),
                  s.get('range_cm', 0), s.get('focus_cost', 0), b.get('reload_s', 0)]
        rows.append(' {"%s","%s",EKind::%s,%s},' % (p['id'], b.get('family', b.get('type')),
                    p['kind'].title(), ','.join(map(num, values))))
    rows += ['}};', 'inline constexpr std::array<FAffixDefinition,36> Affixes={{']
    for a in affixes:
        mask = sum(1 << FAMILIES.index(f) for f in a['eligible_weapon_families'])
        bands = ','.join('{%s,%s}' % (t['min'], t['max']) for t in a['tiers'])
        rows.append(' {"%s","%s",EStat::%s,%s,%s,%s,%s,%su,{{%s}}},' % (
            a['id'], a['group'], ENUMS[STATS.index(a['stat'])], a['direction'],
            str(a['polarity'] == 'beneficial').lower(), str('weapon' in a['eligible_kinds']).lower(),
            str('armor' in a['eligible_kinds']).lower(), mask, bands))
    rows += ['}};', 'inline constexpr std::array<FStatDefinition,22> StatDefinitions={{']
    for s in stats:
        rows.append(f' {{"{s["id"]}",{num(s["min_value"])},{num(s["max_value"])} }},')
    rows += ['}};', 'inline constexpr std::array<FTalentDefinition,9> Talents={{']
    talent_ids = [t['id'] for t in talents]
    for t in talents:
        prereqs = t['prerequisites']; assert len(prereqs) <= 1
        index = talent_ids.index(prereqs[0]['talent_id']) if prereqs else -1
        rank = prereqs[0]['minimum_owned_rank'] if prereqs else 0
        contributions = ','.join(num(t['per_rank_contributions'].get(s, 0)) for s in STATS)
        rows.append(' {"%s",%s,FValues{{%s}},%s,%s},' % (t['id'], t['max_rank'], contributions, index, rank))
    rows += ['}};']
    rows.append('inline constexpr std::array<double,4> WeaponGradePct={%s};' % ','.join(num(g['weapon_damage_pct_contribution']) for g in growth['grades']))
    rows.append('inline constexpr std::array<double,4> ArmorGradeRatio={%s};' % ','.join(num(g['armor_intrinsic_protection_ratio_bonus']) for g in growth['grades']))
    for member, key in [('WorkshopCaps', 'workshop_grade_cap'), ('NaturalDropCaps', 'natural_drop_grade_cap')]:
        rows.append('inline constexpr std::array<int,5> %s={%s};' % (member, ','.join(str(c[key]) for c in growth['chapter_profiles'])))
    replace_block(CODE/'DungeonEquipmentStats.h', 'FROZEN EQUIPMENT DATA', '\n'.join(rows), opt.check)
    # Golden fixture uses source-authored eligibility intervals, not the production legality algorithm.
    fixture = ['struct FExpectedRangeRow { std::string_view TemplateId,AffixId; std::array<FRange,5> Ranges; };',
               'static const std::array<std::string_view,45> ExpectedTemplateIds={'+','.join('"'+p['id']+'"' for p in profiles)+'};']
    all_eligibility = [(p['id'], a) for p in profiles for a in p['affix_eligibility']]
    fixture.append(f'static const std::array<FExpectedRangeRow,{len(all_eligibility)}> ExpectedRanges={{{{')
    for item_id, a in all_eligibility:
        ranges = {r['tier']: r for r in a['legal_tier_ranges']}
        bands = ','.join('{%s,%s}' % (ranges[t]['min'], ranges[t]['max']) if t in ranges else '{0,-1}' for t in range(1, 6))
        fixture.append(' {"%s","%s",{{%s}}},' % (item_id, a['affix_id'], bands))
    fixture += ['}};']
    replace_block(CODE/'Tests/DungeonEquipmentStatsStandalone.cpp', 'GOLDEN SOURCE ELIGIBILITY', '\n'.join(fixture), opt.check)
    print(f'FROZEN_SOURCE_CHECK_OK templates=45 affixes=36 stats=22 talents=9 eligibility_cells=8100 sources={len(SOURCES)} check_only={opt.check}')


if __name__ == '__main__':
    main()
